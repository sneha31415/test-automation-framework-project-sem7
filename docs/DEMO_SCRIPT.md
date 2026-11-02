# Demo Script (about 8 minutes, 6 speakers)

Replace "Member 1-6" with your names. Everyone should be able to answer questions about **their own part**.
Do a full dry run the day before, on the laptop you will present from.

**Before you start:** internet on, Chrome closed, terminal open in the project folder with `venv\Scripts\activate`
done, `reports\` folder cleared (delete old report, screenshots and logs so the demo output is fresh), JMeter
results already generated as a backup.

| # | Who | Time | What to show and say |
|---|---|---|---|
| 1 | Member 1 | 1 min | Problem and scope: 16 requirements, 36 tests. Open `docs/Test_Design_and_Traceability.xlsx` - show the **EP-BVA** sheet (username 29/30/31, postal code 4/5/6) and the **Traceability** sheet (16/16 covered). |
| 2 | Member 2 | 1.5 min | Framework structure in VS Code: `pages/`, `tests/`, `testdata/`, `conftest.py`, `pytest.ini`. Explain POM (locators in pages, assertions in tests), explicit waits in `base_page.py` (no `time.sleep`), markers. |
| 3 | Member 3 | 1 min | **Run smoke live:** `pytest -m smoke`. While Chrome runs, point out FR-01 login and FR-06/07 cart. Show the 5 passes. |
| 4 | Member 4 | 1.5 min | Data-driven tests: open `testdata/login_negative.csv` and `postal_codes.json`, run `pytest tests/test_login.py -k "boundary"` (or the regression suite). Explain the 4/5/6-digit postal code boundary and the **xfail / DEF-01** finding, which is a requirement-vs-behaviour mismatch the team found. |
| 5 | Member 5 | 1.5 min | **Evidence:** open `reports/report.html` (FR ID column, results, environment). Show a screenshot from `reports/screenshots/` and a log from `reports/logs/` (test name, step, status). Optionally break a test on purpose (`set SAUCE_PASS=wrong` then `pytest tests/test_login.py::test_login_success`) to show screenshot-on-failure, then `set SAUCE_PASS=`. |
| 6 | Member 6 | 1.5 min | JMeter: show the `.jmx` (20 users, 60 s ramp-up, 180 s), the HTML dashboard (`performance/html_report/index.html`) and `Findings.md` with Pass/Fail for NFR-01 to 03. Mention the single-page-app limitation. |

**Closing (Member 1, 30 s):** how to reproduce - README steps (`setup.bat`, `run_smoke.bat`, `run_all.bat`,
`performance\run_jmeter.bat`).

## Likely questions - prepare answers

- *Why Page Object Model?* A locator change is fixed in one place; tests read like the requirement.
- *Why no `time.sleep`?* Fixed sleeps are slow and flaky; explicit waits proceed the moment the condition is true.
- *What is the difference between smoke and regression here?* Smoke = 5 core happy paths, run first and fast. Regression = negative, boundary and secondary flows.
- *Why are 4 tests xfail?* The application accepts postal codes the requirement says are invalid. We record this as a defect instead of hiding it.
- *EP vs BVA?* EP groups inputs expected to behave the same (letters, blank, digits); BVA tests the edges (4/5/6 digits, 29/30/31 characters).
- *Why can't JMeter test the login?* SauceDemo logs in client-side with JavaScript, so there is no login request to send.
- *How would you add a new test?* Add a method to the page object, then a test function with `@pytest.mark.smoke` or `regression` and `@pytest.mark.fr("FR-xx")`.

## Backup plan

If the internet or the site is slow: show a pre-generated `report.html`, a screenshot folder and the JMeter
dashboard from an earlier successful run, and explain the live run you would have shown.
