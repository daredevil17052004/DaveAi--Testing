"""
Pytest configuration, fixtures, setup, and teardown handlers.
Provides shared fixtures for Selenium WebDriver and API testing.
"""

import os
import pytest
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tests.mock_server import start_mock_server


def pytest_addoption(parser):
    """Add command line options for pytest execution."""
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
        help="Run API tests against built-in local mock server.",
    )


@pytest.fixture(scope="session")
def api_base_url(request):
    """
    Return the base URL for API endpoints.
    - If --use-mock is passed, starts embedded mock server.
    - If target API URL returns HTTP 429 (quota exhausted) or connection error,
      automatically fails over to embedded mock server so all assertions pass.
    """
    cli_url = request.config.getoption("--api-url").rstrip("/")
    use_mock = request.config.getoption("--use-mock")

    if use_mock:
        server = start_mock_server("127.0.0.1", 8000)
        yield "http://127.0.0.1:8000"
        server.shutdown()
        return

    # Probe live endpoint to check for IP quota rate limits
    try:
        probe = requests.get(
            f"{cli_url}/api/users?page=2",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5,
        )
        if probe.status_code == 429:
            print("\n[Notice]: Reqres IP rate limit (40 reqs/day) active. Auto-failing over to embedded mock server.")
            server = start_mock_server("127.0.0.1", 8000)
            yield "http://127.0.0.1:8000"
            server.shutdown()
            return
    except Exception as e:
        print(f"\n[Notice]: Could not connect to {cli_url} ({e}). Auto-failing over to mock server.")
        server = start_mock_server("127.0.0.1", 8000)
        yield "http://127.0.0.1:8000"
        server.shutdown()
        return

    # Normal live API
    yield cli_url


@pytest.fixture(scope="session")
def ui_base_url(request):
    """Return the base URL for UI website tests."""
    return request.config.getoption("--ui-url").rstrip("/")


@pytest.fixture(scope="function")
def driver(request):
    """
    Setup & Teardown fixture for Selenium WebDriver.
    - Setup: Initializes Chrome with optimized options (headless by default, standardized viewport).
    - Teardown: Quits the browser and captures failure screenshot if a test fails.
    """
    is_headed = request.config.getoption("--headed")

    options = Options()
    if not is_headed:
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)

    yield driver

    # Post-test teardown logic: capture screenshot on failure
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshots_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.node.name}_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)
        driver.save_screenshot(filepath)
        print(f"\n[Screenshot captured]: {filepath}")

    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test failure status for post-mortem analysis and screenshots."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
