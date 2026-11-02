# SauceDemo Test Automation Framework

Selenium 4 + PyTest automation framework (Page Object Model) with a JMeter performance test, built for the
**Software Testing Lab - Automation Framework Case Study**.

- **Application under test:** https://www.saucedemo.com/ (`standard_user` / `secret_sauce`)
- **Functional automation:** 36 automated tests covering **all 16 requirements (FR-01 to FR-16)**
- **Performance:** JMeter plan - 20 users, 60 s ramp-up, 3 min, thresholds NFR-01 to NFR-03

---

## 1. Prerequisites

| Tool | Version | Check with |
|---|---|---|
| Windows 10/11 | - | - |
| Python | 3.11 or newer | `python --version` |
| Google Chrome | latest | open `chrome://version` |
| Java (for JMeter) | 8 or newer | `java -version` |
| Apache JMeter | 5.6 or newer, `bin` folder on `PATH` | `jmeter --version` |
| Internet access | to saucedemo.com and PyPI | - |

All tools are free. No paid software is used.

## 2. Setup (one time)

Open a terminal in the project folder and run:

```bat
setup.bat
```

or manually:

```bat
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`webdriver-manager` downloads the matching ChromeDriver automatically on the first run.

## 3. Running the tests

Activate the environment first (`venv\Scripts\activate`), then run from the project root:

| Goal | Command | Shortcut |
|---|---|---|
| **Smoke suite** (5 core flows) | `pytest -m smoke` | `run_smoke.bat` |
| **Regression suite** (31 negative / boundary / secondary tests) | `pytest -m regression` | `run_regression.bat` |
| **Full suite** (all 36 tests) | `pytest` | `run_all.bat` |
| Run without opening a browser window | `pytest --headless` | - |
| One requirement or test | `pytest -k "FR-14"` or `pytest tests/test_login.py` | - |
| Different application URL | `pytest --base-url https://www.saucedemo.com/` | - |

### What a successful run looks like

Against the live site the expected result is **32 passed + 4 xfailed**. The 4 *xfailed* tests are the postal-code
cases the site is expected to accept even though FR-14 says they must be rejected (see section 7, DEF-01). If the
site actually rejects them they appear as *xpassed*, which is also fine (`strict=False`).

## 4. Where to find the output

| Output | Location |
|---|---|
| **HTML report** (self-contained, includes an FR ID column and embedded failure screenshots) | `reports/report.html` |
| **Screenshots** on failure (`FAIL_...png`) and on expected failures (`XFAIL_...png`, evidence for DEF-01) | `reports/screenshots/` |
| **Execution log** - one file per run with timestamp, test name, STEP lines and STATUS | `reports/logs/execution_<timestamp>.log` |

Sample log lines:

```
2026-11-02 12:20:47 | INFO | test_login_success | STEP   | Enter 'standard_user' in Username
2026-11-02 12:20:58 | INFO | test_login_success | STATUS | FAILED - Products page title was not displayed after login
```

## 5. Framework design

```
saucedemo-automation-framework/
├── config/settings.py        URLs, credentials, timeouts, folder paths (no hard-coding elsewhere)
├── pages/                    Page Object Model - locators + actions only, no assertions
│   ├── base_page.py          explicit-wait helpers, cart badge, logout (shared header)
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py      Your Information / Overview / Complete
├── tests/                    test logic and assertions only
│   ├── test_login.py         FR-01 to FR-05
│   ├── test_products_cart.py FR-06 to FR-09
│   ├── test_session.py       FR-10
│   └── test_checkout.py      FR-11 to FR-16
├── testdata/                 CSV / JSON data for data-driven tests
├── utils/                    driver factory, logger, data reader
├── conftest.py               fixtures + hooks (driver, screenshot on failure, logging, report columns)
├── pytest.ini                markers (smoke, regression, fr, known_defect) + HTML report options
├── performance/              JMeter plan, run script, analyzer, results, Findings.md
├── docs/                     test design workbook, demo script, team checklist
└── reports/                  generated output (report, screenshots, logs)
```

### How each mandatory engineering requirement is met

| Requirement | Implementation |
|---|---|
| Page Object Model | `pages/` - one class per screen; tests contain no locators |
| Explicit waits, no sleeps | `BasePage` wraps `WebDriverWait` + `expected_conditions`; implicit wait fixed at 0; `time.sleep` is not used anywhere |
| Data-driven (min. 2 tests) | **4 data-driven tests:** `login_negative.csv` (8 rows), `username_boundary.json` (5), `checkout_negative.csv` (3), `postal_codes.json` (7) |
| Markers | `smoke`, `regression` (plus `fr("FR-xx")` for traceability, `known_defect`) |
| Screenshot on failure | `conftest.py` hook saves to `reports/screenshots/` and embeds it in the HTML report |
| Logging | `utils/logger.py` -> `reports/logs/` (test name, step, status) |
| HTML report | `pytest-html`, configured in `pytest.ini` -> `reports/report.html` |
| Reproducible setup | `requirements.txt` with pinned versions, `setup.bat`, this README |

## 6. Test design and traceability

`docs/Test_Design_and_Traceability.xlsx` contains the 36 test cases, the Equivalence Partitioning / Boundary Value
tables, the requirement-to-test traceability matrix (FR-01 to FR-16, 100% covered), the defect log and a results
summary that updates from the Status column.

Requirement-to-test mapping (also visible as the **FR ID** column in the HTML report):

| Requirement | Test(s) | Suite |
|---|---|---|
| FR-01 | `test_login_success` | smoke |
| FR-02, FR-03, FR-04 | `test_login_failure` (8 data rows) | regression |
| FR-05 | `test_username_length_boundary` (29, 30, 31, 32, 255 characters) | regression |
| FR-06 | `test_products_visible_with_name_price_and_button` | smoke |
| FR-07 | `test_add_to_cart_updates_badge_and_button` / `test_add_multiple_items_increments_badge` | smoke / regression |
| FR-08 | `test_remove_item_clears_badge_and_restores_button` / `test_remove_one_of_two_items_decrements_badge` | regression |
| FR-09 | `test_cart_lists_selected_items_with_matching_name_and_price` | regression |
| FR-10 | `test_logout_returns_to_login_page`, `test_protected_pages_redirect_to_login_after_logout` | regression |
| FR-11 | `test_checkout_button_opens_your_information_page` | smoke |
| FR-12, FR-13 | `test_mandatory_name_fields` (3 data rows) | regression |
| FR-14 | `test_postal_code_validation` (4, 5, 6 digits, letters, mixed, blank, symbols) | regression |
| FR-15 | `test_valid_information_leads_to_overview` | regression |
| FR-16 | `test_finish_order_shows_success_message` | smoke |

## 7. Known defect and limitations

- **DEF-01 (FR-14 postal code):** the requirement says the postal code must be numeric and that 4 digits is invalid.
  SauceDemo is believed to accept any non-blank value. Those 4 tests are marked `xfail` with the reason, so the suite
  stays green while the report and screenshots document the mismatch. Run the suite once, check what actually
  happens, and update the defect log in the workbook. To treat them as hard failures, delete the `xfail` mark in
  `_postal_code_params()` in `tests/test_checkout.py`.
- **FR-05 (username > 30 characters):** every length fails because the user does not exist, so the UI cannot reveal a
  separate 30-character limit (see OBS-01 in the workbook).
- **JMeter** cannot execute SauceDemo's JavaScript, so it measures page delivery (`GET /` and `GET /inventory.html`),
  not the client-side login (see section 8).

## 8. Performance testing (JMeter)

Plan: `performance/jmx/saucedemo_weekend_lab.jmx` - 20 threads, 60 s ramp-up, 180 s duration, 0-500 ms random
think time, HTTP 200 assertion on each request, samplers labelled **Login Page** (`GET /`) and **Products Page**
(`GET /inventory.html`).

Run it (about 3 minutes):

```bat
performance\run_jmeter.bat
```

The script runs JMeter in non-GUI mode, then `analyze_results.py` creates the remaining deliverables:

| Deliverable | Location | Created by |
|---|---|---|
| Test plan | `performance/jmx/saucedemo_weekend_lab.jmx` | provided |
| Raw results | `performance/results/results.jtl` | JMeter |
| Aggregate CSV | `performance/results/aggregate.csv` | `analyze_results.py` |
| HTML dashboard | `performance/html_report/` (open `index.html`) | JMeter |
| NFR Pass/Fail summary | `performance/Findings.md` | `analyze_results.py` |

Equivalent manual command: `jmeter -n -t performance\jmx\saucedemo_weekend_lab.jmx -l performance\results\results.jtl -e -o performance\html_report`
(the `html_report` folder must not exist or must be empty).

To smoke-test the plan quickly before the full run: `jmeter -n -t jmx\saucedemo_weekend_lab.jmx -l results\test.jtl -Jthreads=2 -Jrampup=2 -Jduration=10`.

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `pytest` not recognised | Activate the environment: `venv\Scripts\activate` |
| ChromeDriver cannot be downloaded (college / corporate network) | Download a driver matching your Chrome version manually and set `set CHROMEDRIVER_PATH=C:\path\to\chromedriver.exe`, or `set USE_WEBDRIVER_MANAGER=0` to use Selenium Manager |
| Chrome opens but tests time out | Check the site loads in a normal browser; re-run - the public site can be slow |
| `jmeter` not recognised | Add `<JMeter folder>\bin` to the Windows `PATH` and open a new terminal |
| JMeter error "html_report folder not empty" | Delete `performance\html_report` (the run script does this automatically) |
| JMeter shows 100% errors | Open `results\jmeter.log`; confirm saucedemo.com is reachable from your network |
| Tests need a visible browser for the demo | Run without `--headless` (the default) |
