# SauceDemo Automation Framework

Selenium 4 + PyTest Page Object Model (POM) test automation framework with JMeter performance testing for **SauceDemo** (`https://www.saucedemo.com/`).

* **Credentials:** `standard_user` / `secret_sauce`
* **Test Coverage:** All 16 functional requirements (FR-01 to FR-16) across 36 test cases
* **Performance Testing:** JMeter load test (20 users, 60s ramp-up, 180s duration) for NFR-01 to NFR-03

---

## Quick Start: Step-by-Step Execution

### 1. One-Time Setup

**macOS / Linux:**
```bash
./setup.sh
```
*(Or manually: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`)*

**Windows:**
```cmd
setup.bat
```

---

### 2. Run Functional Tests

Always activate your virtual environment first (`source venv/bin/activate` on Mac/Linux or `venv\Scripts\activate` on Windows).

| Test Suite | macOS / Linux | Windows | Purpose |
|---|---|---|---|
| **Smoke Suite** | `./run_smoke.sh` | `run_smoke.bat` | Core happy path (5 tests) |
| **Regression Suite** | `./run_regression.sh` | `run_regression.bat` | Negative & boundary cases (31 tests) |
| **Full Suite** | `./run_all.sh` | `run_all.bat` | All 36 tests |
| **Headless Mode** | `pytest --headless` | `pytest --headless` | Run without opening browser |

> **Expected Test Result:** **32 Passed, 4 Xfailed**  
> The 4 `xfail` cases are expected boundary postal code tests under **DEF-01** (FR-14 specifies numeric-only postal codes, but the live site accepts alphanumeric/4-digit codes). The framework logs and captures screenshots for them as defect evidence without breaking the build.

---

### 3. Run JMeter Performance Test

Ensure Java 8+ and Apache JMeter 5.6+ are installed and available on `PATH`.

**macOS / Linux:**
```bash
cd performance
./run_jmeter.sh
cd ..
```

**Windows:**
```cmd
performance\run_jmeter.bat
```

This runs the 3-minute load test, generates the HTML dashboard, and automatically updates `performance/Findings.md`.

---

## Deliverables & Output Locations

| Deliverable | Location | Description |
|---|---|---|
| **Test Execution Report** | `reports/report.html` | Self-contained HTML report with test statuses and embedded failure screenshots |
| **Failure Screenshots** | `reports/screenshots/` | Captured automatically on test failure and xfail |
| **Execution Logs** | `reports/logs/` | Step-by-step logs with timestamps and test names |
| **JMeter Raw Results** | `performance/results/results.jtl` | Sample data from load test |
| **JMeter Aggregate CSV** | `performance/results/aggregate.csv` | Summary stats (samples, avg, P95, error rate, throughput) |
| **JMeter HTML Dashboard** | `performance/html_report/index.html` | Interactive performance graphs and charts |
| **Performance Findings** | `performance/Findings.md` | Maps NFR-01, NFR-02, and NFR-03 to Pass/Fail |
| **Traceability Matrix** | `docs/Test_Design_and_Traceability.xlsx` | EP/BVA test design, traceability matrix, and defect log |

---

## Framework Architecture

```
saucedemo-automation-framework/
├── config/settings.py        # Central configuration (URLs, timeouts, paths)
├── pages/                    # Page Object Model (locators and actions, no assertions)
│   ├── base_page.py          # Explicit wait wrappers (zero time.sleep)
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/                    # PyTest test cases (assertions only)
│   ├── test_login.py         # FR-01 to FR-05
│   ├── test_products_cart.py # FR-06 to FR-09
│   ├── test_session.py       # FR-10
│   └── test_checkout.py      # FR-11 to FR-16
├── testdata/                 # Data-driven CSV/JSON files
├── utils/                    # Driver factory, custom logger, data reader
├── performance/              # JMeter test plan (.jmx), scripts, and results
└── reports/                  # Generated HTML reports, logs, and screenshots
```

---

## Performance Thresholds (NFRs)

* **NFR-01 (Login Page P95 < 3.0s):** PASS (Measured ~0.073s)
* **NFR-02 (Products Page P95 < 4.0s):** PASS (Measured ~0.078s)
* **NFR-03 (Overall Error Rate < 2%):** Documented in `performance/Findings.md`.
