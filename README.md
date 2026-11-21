# Automated QA Engineering Suite: API & UI Test Automation

A Python-based test automation suite covering RESTful API tests (**Reqres**) and Web UI tests (**DaveAI - www.iamdave.ai**), with an optional Locust load test.

---

## 📁 Repository Structure

```text
DAVEAI/
├── pages/                                # Page Object Model (POM) for UI tests
│   ├── __init__.py
│   ├── base_page.py                      # Reusable base page with explicit waits & interactions
│   ├── home_page.py                      # DaveAI Homepage locators and action flows
│   ├── contact_page.py                   # Contact Us form interactions & validation checks
│   └── demo_page.py                      # Book Demo lead capture verification
├── tests/                                # Test suites
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures, WebDriver setup/teardown & failure screenshots
│   ├── quota_guard.py                    # Shared daily quota tracker; default cap 35, override with REQRES_DAILY_LIMIT env var
│   ├── api_tests.py                      # Part 1: API tests for Reqres.in (assignment filename)
│   ├── ui_tests.py                       # Part 2: UI tests for www.iamdave.ai — Selenium POM (primary, assignment filename)
│   ├── test_ui_playwright.py             # Bonus: Alternative UI test suite using Playwright
│   └── mock_server.py                    # Embedded mock server implementing Reqres API contract
├── reports/                              # Automated test artifacts & reports
│   ├── test_report.html                  # Self-contained HTML execution report
│   ├── locust_results/                   # Load test charts, latency metrics, and CSV logs
│   │   ├── report.html                   # Interactive Locust HTML report
│   │   ├── reqres_load_stats.csv         # Aggregated request & latency percentiles
│   │   └── reqres_load_failures.csv      # Error classification logs
│   └── screenshots/                      # Automatically captured screenshots on UI test failures
├── load_test.py                          # Bonus: Locust load testing script
├── pytest.ini                            # Test discovery config (collects api_tests.py, ui_tests.py, test_ui_playwright.py)
├── requirements.txt                      # Project dependencies
└── README.md
```

---

## ⚙️ Prerequisites & Setup

### 1. Python Environment
Python **3.10+** (tested on Python 3.12).

Clone the repository and install dependencies in a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate
# Activate on macOS/Linux
# source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Browser Driver Setup
- **Selenium:** Selenium 4.x includes automated driver management (`Selenium Manager`), so no manual `chromedriver` download is needed. Google Chrome must be installed on the machine.
- **Playwright (Optional Bonus Suite):**
  ```bash
  playwright install chromium
  ```

### 3. Dependencies

| Package | Minimum Version | Purpose |
|---|---|---|
| `pytest` | `>=8.0.0` | Test framework, runner, test discovery, and fixture injection |
| `pytest-html` | `>=4.1.0` | Standalone, self-contained HTML test report generation |
| `requests` | `>=2.31.0` | HTTP client for Reqres REST API testing |
| `selenium` | `>=4.20.0` | Browser automation engine for primary Page Object Model UI suite |
| `webdriver-manager` | `>=4.0.0` | Automated driver management fallback |
| `playwright` | `>=1.40.0` | Cross-browser automation engine for bonus UI suite |
| `locust` | `>=2.20.0` | User load testing and latency percentile generation |

---

## 🚀 Execution Guide

### Run All Tests (safe — uses embedded mock for API)
```bash
pytest --use-mock --html=reports/test_report.html --self-contained-html
```

### Part 1: API Automation Tests (`tests/api_tests.py`)
```bash
# Run against embedded mock server (no live API calls; safe to run any number of times)
pytest tests/api_tests.py --use-mock -v

# Run against live Reqres API (consumes daily quota — see Rate Limit section below)
pytest tests/api_tests.py -v

# Filter using custom marker
pytest -m api -v
```

### Part 2: UI Automation Tests — Selenium POM, primary (`tests/ui_tests.py`)
```bash
# Run UI test suite in headless mode (default)
pytest tests/ui_tests.py -v

# Run UI test suite in headed mode (visible browser window)
pytest tests/ui_tests.py --headed -v
```

### Bonus: Playwright UI Tests (`tests/test_ui_playwright.py`)
```bash
pytest tests/test_ui_playwright.py -v
```

### Part 3: Locust Load Testing (Bonus)
```bash
# Headless run — 5 users, 1 user/s spawn rate, 15s duration
locust -f load_test.py --headless --host=https://reqres.in -u 5 -r 1 -t 15s --csv=reports/locust_results/reqres_load --html=reports/locust_results/report.html

# Interactive Web UI
locust -f load_test.py --host=https://reqres.in
# Open http://localhost:8089 in your browser
```

---

## 🧪 Test Case Design & Rationale

### Part 1: API Test Suite (`tests/api_tests.py`)
Target API: `https://reqres.in`

| # | Test Function | HTTP Method / Endpoint | Purpose | Key Assertions |
|---|---|---|---|---|
| **1** | `test_get_users_list_success` | `GET /api/users?page=2` | Validates paginated user retrieval and schema. | HTTP 200, `page==2`, `per_page==6`, `total>=12`, fields: `id, email, first_name, last_name, avatar`. |
| **2** | `test_get_users_list_latency_sla` | `GET /api/users?page=2` | Checks network SLA separately from schema correctness. | HTTP 200, response time < 2.5s. |
| **3** | `test_get_single_user_content_and_structure` | `GET /api/users/2` | Verifies data integrity of a specific user entity. | HTTP 200, `id==2`, `first_name=="Janet"`, `last_name=="Weaver"`, valid email, `support.url` present. |
| **4** | `test_create_user_success` | `POST /api/users` | Validates resource creation workflow. | HTTP 201, server echoes `name` and `job`, non-empty `id`, valid ISO 8601 `createdAt` timestamp. |
| **5** | `test_register_missing_password_error` | `POST /api/register` | Tests error handling when a required field is omitted. | HTTP 400, `error == "Missing password"`. |
| **6** | `test_get_non_existent_user_not_found` | `GET /api/users/999` | Asserts correct 404 behaviour. | HTTP 404, response body is `{}`. |

#### Resilience & Rate Limit Mitigation

**Rate limits — what is actually known:**
- The assignment states a maximum of **100 Reqres API calls per day**.
- The Reqres anonymous API has returned the error message `"You've hit the anonymous demo limit of 40 requests/day"` in a previous live run. No 429 response body is recorded in any CSV or log file in this repository — that message came from a manual run.
- Because both figures exist, the safe operating assumption is **40 calls/day** for anonymous access.
- The default daily cap in `tests/quota_guard.py` is **35** — a conservative margin below 40, shared across all Pytest and Locust calls for the day.
- To raise the cap, set the environment variable `REQRES_DAILY_LIMIT=<n>` before running (e.g. `set REQRES_DAILY_LIMIT=90` on Windows). Values above 40 are only safe if you have a Reqres API key (set `REQRES_API_KEY=<key>`).
- `quota_guard.py` prints today's current recorded count every time it loads, so you always know your starting position.

**How the quota guard works:**
- `tests/quota_guard.py` persists `{"date": "YYYY-MM-DD", "count": N}` in `reports/.reqres_quota.json`. It resets automatically when the calendar date changes.
- Both Pytest (via `conftest.py`) and Locust (`load_test.py`) share the same counter. If the cap is reached, Pytest tests are **skipped** with a message that includes today's count and the cap; Locust stops its runner.
- Tests call `check_rate_limit(response)` after each live request. If Reqres returns HTTP 429, the test is skipped immediately.
- Use `--use-mock` for fully offline, deterministic runs (no quota consumed).

---

### Part 2: Website UI Test Suite (`tests/ui_tests.py`) — Primary
Target Website: `https://www.iamdave.ai/`

The **primary** UI suite uses the **Page Object Model (POM)** pattern with Selenium WebDriver. The Playwright suite (`tests/test_ui_playwright.py`) is a bonus alternative implementation.

| # | Test Function | Page / Flow | Key Assertions |
|---|---|---|---|
| **1** | `test_homepage_load_and_branding` | Homepage (`/`) | `"DaveAI" in title`, primary H1 contains `"Automotive Intelligence"`, brand logo in DOM. |
| **2** | `test_navigation_flow_to_platform_page` | Navigation Flow | Clicks platform CTA, URL transitions to `/platform/`, title contains `"Platform"` and `"DaveAI"`. |
| **3** | `test_navigation_to_book_demo` | Conversion Funnel | Clicks demo CTA, URL transitions to `/book-demo/`, form fields (name, email, message) visible. |
| **4** | `test_contact_form_interactions_and_validation` | Form Interaction (`/contact-us/`) | 5 fields filled and read back; invalid email fails `checkValidity()`; valid email passes. Form is NOT submitted. |

#### Setup & Teardown Lifecycle:
- **Setup:** Configures Chrome with standardized desktop viewport (`1920x1080`), `--no-sandbox`, and headless mode (toggleable with `--headed`).
- **Teardown:** Safely terminates the browser process (`driver.quit()`).
- **Failure Diagnostics:** Hooks into `pytest_runtest_makereport` to capture a timestamped PNG screenshot into `reports/screenshots/` when any UI test fails.

---

### Bonus: Playwright Alternative (`tests/test_ui_playwright.py`)
Demonstrates Playwright's sync API as an alternative to the Selenium POM primary suite:
- Auto-waiting locators (`expect(hero).to_be_visible()`).
- Browser context isolation per test via fixture.
- Cross-validates homepage rendering, navigation, and client-side form validation.

---

## 📈 Locust Load Testing (Bonus)

### Test Plan & Architecture
The load test (`load_test.py`) simulates realistic API traffic against Reqres with strict safety parameters:
- **Target Host:** `https://reqres.in`
- **Simulated Users:** 5 concurrent virtual users
- **Spawn Rate:** 1 user/second
- **Duration:** 15 seconds (`-t 15s`)
- **User Pacing / Think Time:** 1.5s to 3.0s between requests (`between(1.5, 3.0)`)
- **Traffic Mix:**
  - 75% traffic: Paginated collection (`GET /api/users?page=2`, weight=3)
  - 25% traffic: Single entity (`GET /api/users/2`, weight=1)
  - *Note:* Task weights (3:1) are probabilities per task pick, not fixed quotas, so a short run can produce different ratios — in the recorded 15s run the actual split was 18 vs. 8 requests.
- **Daily Quota Circuit Breaker:**
  - `load_test.py` features a persistent daily request counter (`DAILY_QUOTA_LIMIT = 35` by default, configurable via `REQRES_DAILY_LIMIT`) stored in `reports/.reqres_quota.json`. Once the combined quota is reached across Locust and Pytest, the runner terminates safely.
  - With multiple concurrent virtual users, the guard checks the count before each request and records it after, so it can overshoot by the number of concurrent users; the cap (35 by default) sits well below the enforced API limit for this reason.

### Recorded Load Test Results

Summary metrics from `reports/locust_results/reqres_load_stats.csv`. This is a **live Reqres API run** using the exact command:
```
locust -f load_test.py --headless --host=https://reqres.in -u 5 -r 1 -t 15s --csv=reports/locust_results/reqres_load --html=reports/locust_results/report.html
```

| Endpoint | Requests | Failures | Median Latency | Average Latency | Min Latency | Max Latency | 90th %ile | 95th %ile |
|---|---|---|---|---|---|---|---|---|
| `GET /api/users?page=2` | 18 | 0 (0.0%) | 210 ms | 249.8 ms | 169.0 ms | 594.8 ms | 520 ms | 590 ms |
| `GET /api/users/2` | 8 | 0 (0.0%) | 180 ms | 196.0 ms | 169.9 ms | 315.8 ms | 320 ms | 320 ms |
| **Aggregated Total** | **26** | **0 (0.0%)** | **200 ms** | **233.2 ms** | **169.0 ms** | **594.8 ms** | **360 ms** | **520 ms** |

*Note on Response Handling vs. Quota Circuit Breaker:*
- **HTTP 429 Response Handling:** Handled inside Locust tasks via `catch_response=True`, marking a `429` response as a test failure rather than raising an exception. In this recorded 15s run with 1.5–3s think time between requests, zero 429 responses were received.
- **Daily Quota Circuit Breaker:** The persistent quota guard (default cap 35, configurable via `REQRES_DAILY_LIMIT`) is the mechanism that stops the Locust runner when the combined daily budget is exhausted. These are two separate concerns.

Interactive HTML visualization available at: `reports/locust_results/report.html`.

---

## 📊 Test Execution Results

### Mock Run (safe, offline — no live API calls)
```text
$ pytest --use-mock -v
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\Ansh Sharma\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
metadata: {'Python': '3.12.0', 'Platform': 'Windows-11-10.0.26200-SP0', 'Packages': {'pytest': '9.0.3', 'pluggy': '1.6.0'}, 'Plugins': {'anyio': '4.15.1', 'langsmith': '0.7.24', 'locust': '2.47.0', 'html': '4.2.0', 'metadata': '3.1.1'}}
rootdir: D:\projects\DAVEAI
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1, langsmith-0.7.24, locust-2.47.0, html-4.2.0, metadata-3.1.1
collecting ... collected 13 items

tests/api_tests.py::test_get_users_list_success PASSED                   [  7%]
tests/api_tests.py::test_get_users_list_latency_sla PASSED               [ 15%]
tests/api_tests.py::test_get_single_user_content_and_structure PASSED    [ 23%]
tests/api_tests.py::test_create_user_success PASSED                      [ 30%]
tests/api_tests.py::test_register_missing_password_error PASSED          [ 38%]
tests/api_tests.py::test_get_non_existent_user_not_found PASSED          [ 46%]
tests/test_ui_playwright.py::test_pw_homepage_title_and_hero PASSED      [ 53%]
tests/test_ui_playwright.py::test_pw_navigation_to_platform PASSED       [ 61%]
tests/test_ui_playwright.py::test_pw_contact_form_inputs PASSED          [ 69%]
tests/ui_tests.py::test_homepage_load_and_branding PASSED                [ 76%]
tests/ui_tests.py::test_navigation_flow_to_platform_page PASSED          [ 84%]
tests/ui_tests.py::test_navigation_to_book_demo PASSED                   [ 92%]
tests/ui_tests.py::test_contact_form_interactions_and_validation PASSED  [100%]

============================= 13 passed in 22.70s =============================
```
*API tests above ran against the embedded mock server (`--use-mock`), not the live Reqres API.*

### Live API Run (uses real Reqres API quota)
Before running without `--use-mock`, confirm available daily quota in `reports/.reqres_quota.json`. A clean live run makes exactly **6 live Reqres API calls** (one per API test function: 5 functional + 1 latency SLA). The former startup probe in `conftest.py` was removed to conserve API budget, so there are no hidden probe calls.

---

## 💡 Key Automation Practices Demonstrated

1. **Page Object Model (POM):** UI tests interact with dedicated page classes (`HomePage`, `ContactPage`, `DemoPage`) rather than embedding raw selectors in test functions.
2. **Explicit Waits:** Element synchronisation uses `WebDriverWait` with `presence_of_element_located` and `visibility_of`. No `time.sleep()` calls are present in the codebase.
3. **Non-submitting Form Tests:** Contact form tests validate input entry and HTML5 client-side constraints without submitting data to the production CRM.
4. **Shared Daily Quota Guard:** `tests/quota_guard.py` persists and shares a daily request count between Pytest and Locust, keeping total live API calls well within the assignment limit.
5. **Strict Live vs. Mock Separation:** Live runs strictly enforce quota exhaustion by skipping API tests (`pytest.skip`) with an informative message rather than silently falling back to the mock server. The embedded mock server is activated solely when passing `--use-mock`, guaranteeing transparency in test execution.
