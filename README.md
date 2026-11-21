# Automated QA Engineering Suite: API & UI Test Automation

A comprehensive, production-grade test automation framework built in Python. This repository covers end-to-end automation for both RESTful APIs (**Reqres**) and Web Applications (**DaveAI - www.iamdave.ai**), complemented by an optional load-testing suite using **Locust** with strict quota controls.

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
│   ├── test_api.py                       # Part 1: API test cases for Reqres.in
│   ├── api_tests.py                      # Alias module matching submission naming spec
│   ├── test_ui.py                        # Part 2: UI test cases for www.iamdave.ai (Selenium POM)
│   ├── ui_tests.py                       # Alias module matching submission naming spec
│   ├── test_ui_playwright.py             # Bonus: Alternative UI test suite using Playwright
│   └── mock_server.py                    # Embedded mock server adhering to Reqres contract
├── reports/                              # Automated test artifacts & reports
│   ├── test_report.html                  # Self-contained HTML execution report
│   ├── locust_results/                   # Load test charts, latency metrics, and CSV logs
│   │   ├── report.html                   # Interactive Locust HTML report
│   │   ├── reqres_load_stats.csv         # Aggregated request & latency percentiles
│   │   └── reqres_load_failures.csv      # Error classification logs
│   └── screenshots/                      # Automatically captured screenshots on UI test failures
├── load_test.py                          # Bonus: Locust load testing script with safety circuit breaker
├── pytest.ini                            # Test discovery, custom markers, and logging configuration
├── requirements.txt                      # Project dependencies
└── README.md                             # Comprehensive technical documentation
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

---

## 🚀 Execution Guide

### Run All Tests
```bash
# Run both API and UI test suites with HTML report generation
pytest --use-mock --html=reports/test_report.html --self-contained-html
```

### Part 1: API Automation Tests
```bash
# Run against live Reqres API
pytest tests/test_api.py -v

# Run against embedded mock server (recommended for deterministic CI runs to bypass external IP rate limits)
pytest tests/test_api.py --use-mock -v

# Filter using custom markers
pytest -m api -v
```

### Part 2: UI Automation Tests (DaveAI)
```bash
# Run UI test suite in headless mode (default)
pytest tests/test_ui.py -v

# Run UI test suite in headed mode (visible browser window)
pytest tests/test_ui.py --headed -v

# Run the Playwright UI implementation
pytest tests/test_ui_playwright.py -v
```

### Part 3: Locust Load Testing (Bonus)
```bash
# Run headless load test with 5 simulated users, 15s duration, and HTML export
locust -f load_test.py --headless --host=https://reqres.in -u 5 -r 1 -t 15s --csv=reports/locust_results/reqres_load --html=reports/locust_results/report.html

# Run with interactive Web UI
locust -f load_test.py --host=https://reqres.in
# Open http://localhost:8089 in your browser
```

---

## 🧪 Test Case Design & Rationale

### Part 1: API Test Suite (`tests/test_api.py` / `tests/api_tests.py`)
Target API: `https://reqres.in`

| # | Test Function | HTTP Method / Endpoint | Purpose & Usability Impact | Key Assertions |
|---|---|---|---|---|
| **1** | `test_get_users_list_success` | `GET /api/users?page=2` | Validates paginated user retrieval. Ensures client apps receive complete lists without truncation. | HTTP 200, Latency < 2.5s SLA, `page==2`, `per_page==6`, `total>=12`, fields: `id, email, first_name, last_name, avatar`. |
| **2** | `test_get_single_user_content_and_structure` | `GET /api/users/2` | Verifies data integrity of a specific customer entity and support metadata. | HTTP 200, `id==2`, `first_name=="Janet"`, `last_name=="Weaver"`, valid email format, presence of `support.url`. |
| **3** | `test_create_user_success` | `POST /api/users` | Validates resource creation workflow for onboarding new users. | HTTP 201 Created, server echoes `name` and `job`, server assigns non-empty `id` and ISO `createdAt` timestamp. |
| **4** | `test_register_missing_password_error` | `POST /api/register` | Tests robust error handling and defensive API design when required parameters are omitted. | HTTP 400 Bad Request, response payload contains `error: "Missing password"`. |
| **5** | `test_get_non_existent_user_not_found` | `GET /api/users/999` | Asserts standard HTTP 404 response when querying entities that do not exist. | HTTP 404 Not Found, returns empty JSON payload `{}`. |

#### Resilience & Rate Limit Mitigation:
Reqres enforces a daily quota of 40 requests per IP on anonymous requests. To protect CI pipelines:
- The suite checks for `HTTP 429 (Too Many Requests)` and skips gracefully with an informative message.
- A built-in embedded mock server (`tests/mock_server.py`) can be enabled via `--use-mock` to guarantee 100% test reproducibility regardless of network conditions or external quotas.

---

### Part 2: Website UI Test Suite (`tests/test_ui.py` / `tests/ui_tests.py`)
Target Website: `https://www.iamdave.ai/`

The UI suite utilizes the **Page Object Model (POM)** pattern to decouple test logic from web element locators, maximizing code reuse and maintainability.

| # | Test Function | Page / Flow | Business & Usability Impact | Key Assertions |
|---|---|---|---|---|
| **1** | `test_homepage_load_and_branding` | Homepage (`/`) | Confirms the core marketing site is live, brand identity is intact, and above-the-fold value proposition renders. | Title matches `"AI-Native Automotive Intelligence Platform \| DaveAI"`, primary H1 hero heading contains `"Automotive Intelligence"`, brand logo exists in DOM. |
| **2** | `test_navigation_flow_to_platform_page` | Navigation Flow | Validates primary product discovery path ("Explore Platform" CTA) for enterprise leads. | Clicks `"MORE ABOUT OUR PLATFORM"`, explicitly waits for URL to transition to `/platform/`, asserts new page title contains `"Platform \| DaveAI"`. |
| **3** | `test_navigation_to_book_demo` | Conversion Funnel | Validates the high-intent lead conversion flow from homepage to the booking scheduler. | Clicks `"SEE DAVEAI IN ACTION"` CTA, waits for `/book-demo/` URL, verifies visibility of name, email, and message inputs. |
| **4** | `test_contact_form_interactions_and_validation` | Form Interaction (`/contact-us/`) | Ensures inbound inquiry channels function smoothly without data entry defects or silent submission failures. | Enters test data across 5 form fields, asserts 100% two-way data binding; triggers HTML5 email validation on malformed email (`validity.valid == False`), and passes on valid format. |

#### Setup & Teardown Lifecycle:
- **Setup:** Configures Chrome with standardized desktop viewport (`1920x1080`), `--no-sandbox`, and automated headless mode (toggleable with `--headed`).
- **Teardown:** Safely terminates the browser process (`driver.quit()`).
- **Failure Diagnostics:** Hooks into `pytest_runtest_makereport` to capture a full-resolution timestamped PNG screenshot into `reports/screenshots/` whenever any UI test fails.

---

### Bonus: Playwright Alternative (`tests/test_ui_playwright.py`)
Demonstrates modern async/sync browser automation:
- Auto-waiting locators (`expect(hero).to_be_visible()`).
- High-level browser context isolation per test.
- Cross-validates homepage rendering, navigation, and client-side form validation.

---

## 📈 Locust Load Testing (Bonus)

### Test Plan & Architecture
The load test (`load_test.py`) simulates realistic API traffic against Reqres with strict safety parameters:
- **Target Host:** `https://reqres.in`
- **Simulated Users:** 5 concurrent virtual users
- **Spawn Rate:** 1 user/second
- **User Pacing / Think Time:** 1.5s to 3.0s between requests (`between(1.5, 3.0)`)
- **Traffic Mix:**
  - 75% traffic: Paginated collection (`GET /api/users?page=2`, weight=3)
  - 25% traffic: Single entity (`GET /api/users/2`, weight=1)
- **Daily Quota Circuit Breaker:**
  - To respect the assignment rule (*"Limit this to a max of 100 api calls within the day"*), `load_test.py` features a global atomic request counter (`MAX_REQUEST_LIMIT = 80`). Once 80 requests are made, the runner immediately terminates itself.

### Recorded Load Test Results

Summary metrics extracted from `reports/locust_results/reqres_load_stats.csv`:

| Endpoint | Requests | Failures | Median Latency | Average Latency | Min Latency | Max Latency | 90th %ile | 95th %ile |
|---|---|---|---|---|---|---|---|---|
| `GET /api/users?page=2` | 29 | 3 (10.3%)* | 230 ms | 317.3 ms | 198.2 ms | 781.3 ms | 560 ms | 650 ms |
| `GET /api/users/2` | 5 | 1 (20.0%)* | 360 ms | 345.5 ms | 207.9 ms | 553.2 ms | 550 ms | 550 ms |
| **Aggregated Total** | **34** | **4 (11.8%)** | **230 ms** | **321.5 ms** | **198.2 ms** | **781.3 ms** | **550 ms** | **650 ms** |

*\*Note on Failures: As captured in `reports/locust_results/reqres_load_failures.csv`, Reqres.in triggers an automated rate limit (`HTTP 429: Too Many Requests`) once rapid concurrent bursts exceed their anonymous IP quota threshold. This validates our circuit breaker and error-handling mechanisms in real-world scenarios.*

Interactive HTML visualization available at: `reports/locust_results/report.html`.

---

## 📊 Summary of Test Execution Results

```text
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.0.3
plugins: anyio-4.15.1, locust-2.47.0, html-4.2.0, metadata-3.1.1
collected 9 items

tests/test_api.py::test_get_users_list_success PASSED                    [ 11%]
tests/test_api.py::test_get_single_user_content_and_structure PASSED     [ 22%]
tests/test_api.py::test_create_user_success PASSED                       [ 33%]
tests/test_api.py::test_register_missing_password_error PASSED           [ 44%]
tests/test_api.py::test_get_non_existent_user_not_found PASSED           [ 55%]
tests/test_ui.py::test_homepage_load_and_branding PASSED                 [ 66%]
tests/test_ui.py::test_navigation_flow_to_platform_page PASSED           [ 77%]
tests/test_ui.py::test_navigation_to_book_demo PASSED                    [ 88%]
tests/test_ui.py::test_contact_form_interactions_and_validation PASSED   [100%]

============================= 9 passed in 16.54s ==============================
```

---

## 💡 Key Automation Best Practices Demonstrated

1. **Page Object Model (POM):** UI tests interact with dedicated Page classes (`HomePage`, `ContactPage`, `DemoPage`) rather than scattering raw XPath/CSS selectors in test bodies.
2. **Robust Synchronization:** Zero brittle `time.sleep()` calls. All element state resolutions use dynamic explicit waits (`WebDriverWait` with `presence_of_element_located` and `visibility_of`).
3. **Smart Element Resolution:** Solved multi-viewport Elementor DOM rendering quirks by detecting displayed navigation elements and handling responsive drawer layouts.
4. **Safety & Defensiveness:** Form interaction tests validate input entry and client-side constraints without submitting spam records to the live production CRM.
5. **Circuit Breakers & Quotas:** Enforced strict adherence to API rate boundaries with custom test runners and embedded mock fallbacks.
