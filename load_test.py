"""
Locust Load Testing Suite for Reqres API (https://reqres.in)

Test Plan Summary:
- Target Host: https://reqres.in
- Endpoints Tested:
    * GET /api/users?page=2 (Paginated collection, weight=3)
    * GET /api/users/2      (Single resource, weight=1)
- Simulated Concurrency: 5 to 10 users
- Spawn Rate: 1 user/second
- Request Throttling / Pacing: 1.5s - 3.0s think time between user requests
- Safety Quota: Hard ceiling of 80 API calls (strictly within the daily 100-request limit)
- Automatic Circuit Breaker: Automatically terminates the test run once quota is hit.

Execution:
    Headless Execution (automated report generation):
        locust -f load_test.py --headless --host=https://reqres.in -u 5 -r 1 -t 30s --csv=reports/locust_results/reqres_load --html=reports/locust_results/report.html

    Interactive Web UI:
        locust -f load_test.py --host=https://reqres.in
        Open http://localhost:8089 in your browser.
"""

import logging
from locust import HttpUser, task, between, events

# Configure custom logger for load test monitoring
logger = logging.getLogger("locust_load_test")
logger.setLevel(logging.INFO)

# Hard limit for total requests across all simulated users (Quota safety guard)
MAX_REQUEST_LIMIT = 80
_request_counter = 0


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logger.info("=" * 60)
    logger.info("🚀 Starting Locust Load Test for Reqres.in")
    logger.info(f"🛡️  Safety Quota Guard Active: Hard cap at {MAX_REQUEST_LIMIT} requests")
    logger.info("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    global _request_counter
    _request_counter += 1
    if exception:
        logger.warning(f"⚠️ [{_request_counter}/{MAX_REQUEST_LIMIT}] Request Failed: {name} | Error: {exception}")
    else:
        logger.info(f"✅ [{_request_counter}/{MAX_REQUEST_LIMIT}] {request_type} {name} | {response_time:.1f}ms")


class ReqresUser(HttpUser):
    """
    Simulates a client application browsing Reqres API endpoints.
    Includes simulated think time (1.5 to 3.0s) to avoid aggressive rate-limiting.
    """
    wait_time = between(1.5, 3.0)

    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    def on_start(self):
        """Initialize session headers upon virtual user spawn."""
        self.client.headers.update(self.default_headers)

    def _enforce_quota(self) -> bool:
        """
        Circuit breaker to prevent exceeding the assignment's 100-request ceiling.
        Stops the Locust runner when the limit is reached.
        """
        global _request_counter
        if _request_counter >= MAX_REQUEST_LIMIT:
            logger.info(f"🛑 Reached {MAX_REQUEST_LIMIT} calls quota. Halting load test runner safely.")
            if self.environment.runner:
                self.environment.runner.quit()
            return True
        return False

    @task(3)
    def test_get_users_page(self):
        """Query paginated user list endpoint (3x weight)."""
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
        """Query single user profile endpoint (1x weight)."""
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
