"""Pytest configuration, fixtures, and execution hooks."""

from datetime import datetime
import logging
import os

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tests.mock_server import start_mock_server
from tests.quota_guard import DAILY_QUOTA_LIMIT, check_and_increment_quota, enforce_api_quota

logger = logging.getLogger(__name__)


def check_rate_limit(response):
    """Skip the running test if Reqres returns HTTP 429 Too Many Requests."""
    if response.status_code == 429:
        pytest.skip("Reqres returned HTTP 429: Too Many Requests. Test skipped.")


def pytest_addoption(parser):
    """Register custom command line options."""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser tests in headed mode (default: headless).",
    )
    parser.addoption(
        "--api-url",
        action="store",
        default="https://reqres.in",
        help="Base URL for API tests.",
    )
    parser.addoption(
        "--ui-url",
        action="store",
        default="https://www.iamdave.ai",
        help="Base URL for UI tests.",
    )
    parser.addoption(
        "--use-mock",
        action="store_true",
        default=False,
        help="Run API tests against the built-in local mock server instead of live Reqres.",
    )


@pytest.fixture(scope="session")
def api_base_url(request):
    """
    Provide the base URL for API tests.

    - If --use-mock is passed: starts the embedded mock server and returns its URL.
      No live Reqres calls are made; quota is not consumed.
    - Otherwise: returns the live Reqres URL (default: https://reqres.in).
      If the quota is already exhausted, all API tests will be skipped via the
      guard_api_quota autouse fixture — there is NO silent fallback to mock.
    """
    if request.config.getoption("--use-mock"):
        server = start_mock_server("127.0.0.1", 8000)
        yield "http://127.0.0.1:8000"
        server.shutdown()
        return

    # Live mode: return the CLI URL as-is.
    # The guard_api_quota fixture (below) handles skipping when the cap is reached.
    # The check_rate_limit helper (called in each test) handles skipping on HTTP 429.
    yield request.config.getoption("--api-url").rstrip("/")


@pytest.fixture(autouse=True)
def guard_api_quota(request, api_base_url):
    """
    Before each @pytest.mark.api test, enforce the daily quota.

    - Mock runs (127.0.0.1 / localhost): free, no quota consumed.
    - Live runs: increments the shared counter and skips the test if the cap is reached.
      The skip message includes today's count and the cap so the reason is visible in output.
    """
    if "api" in request.keywords:
        enforce_api_quota(api_base_url, DAILY_QUOTA_LIMIT)


@pytest.fixture(scope="session")
def ui_base_url(request):
    """Provide the base URL for UI website tests."""
    return request.config.getoption("--ui-url").rstrip("/")


@pytest.fixture(scope="function")
def driver(request):
    """Initialize Chrome WebDriver and capture a screenshot on test failure."""
    is_headed = request.config.getoption("--headed")

    options = Options()
    if not is_headed:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)

    yield driver

    # Capture screenshot if the test failed.
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(screenshots_dir, f"{request.node.name}_{timestamp}.png")
        driver.save_screenshot(filepath)
        logger.info("Screenshot saved: %s", filepath)

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store the test call outcome on the item so the driver fixture can read it."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
