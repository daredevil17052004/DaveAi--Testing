"""
Locust load testing suite for Reqres API endpoints.

Execution:
    Headless execution (15s duration, automated report generation):
        locust -f load_test.py --headless --host=https://reqres.in -u 5 -r 1 -t 15s --csv=reports/locust_results/reqres_load --html=reports/locust_results/report.html

    Interactive Web UI:
        locust -f load_test.py --host=https://reqres.in
        Open http://localhost:8089 in your browser.
"""

import logging
import os
from locust import HttpUser, between, events, task

from tests.quota_guard import (
    DAILY_QUOTA_LIMIT,
    check_and_increment_quota,
    get_current_quota_count,
)

logger = logging.getLogger(__name__)

MAX_REQUEST_LIMIT = DAILY_QUOTA_LIMIT


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    current = get_current_quota_count()
    logger.info("Starting Locust load test (daily quota: %d/%d used)", current, MAX_REQUEST_LIMIT)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    current = get_current_quota_count()
    if exception:
        logger.warning(
            "[%d/%d] Request failed: %s | %s",
            current,
            MAX_REQUEST_LIMIT,
            name,
            exception,
        )
    else:
        logger.info(
            "[%d/%d] %s %s | %.1fms",
            current,
            MAX_REQUEST_LIMIT,
            request_type,
            name,
            response_time,
        )


class ReqresUser(HttpUser):
    wait_time = between(1.5, 3.0)

    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    def on_start(self):
        headers = dict(self.default_headers)
        if os.environ.get("REQRES_API_KEY"):
            headers["x-api-key"] = os.environ.get("REQRES_API_KEY")
        self.client.headers.update(headers)

    def _enforce_quota(self) -> bool:
        """Enforce shared daily request ceiling of 90 across Locust and pytest."""
        if not check_and_increment_quota(MAX_REQUEST_LIMIT):
            logger.info("Reached %d daily request quota limit. Stopping runner.", MAX_REQUEST_LIMIT)
            if self.environment.runner:
                self.environment.runner.quit()
            return True
        return False

    @task(3)
    def test_get_users_page(self):
        if self._enforce_quota():
            return

        with self.client.get(
            "/api/users?page=2",
            name="/api/users?page=2",
            catch_response=True,
            timeout=10.0,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited (HTTP 429: Too Many Requests)")
            else:
                response.failure(f"Unexpected HTTP status: {response.status_code}")

    @task(1)
    def test_get_single_user(self):
        if self._enforce_quota():
            return

        with self.client.get(
            "/api/users/2",
            name="/api/users/2",
            catch_response=True,
            timeout=10.0,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.failure("Rate limited (HTTP 429: Too Many Requests)")
            else:
                response.failure(f"Unexpected HTTP status: {response.status_code}")
