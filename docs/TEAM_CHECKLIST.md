# Team Checklist - what still has to be done by you

The framework, tests, test design workbook and JMeter plan are complete, but they were built without access to
saucedemo.com, so **nothing has been run against the real site yet**. These steps are yours.

## A. Before the demo (must do)

- [ ] **1. Install the tools** on the demo laptop: Python 3.11+, Chrome, Java, JMeter 5.6+ (add JMeter `bin` to PATH).
- [ ] **2. Run `setup.bat`**, then `run_smoke.bat` and `run_all.bat`.
  Expected: smoke 5 passed; full suite about 32 passed + 4 xfailed.
- [ ] **3. Look at any failures.** If a test fails on the real site, open its screenshot in `reports/screenshots/`
  and the log in `reports/logs/`. The most likely cause is a changed error-message text or locator - fix it in
  `testdata/*.csv` (expected text) or the page object (locator). Tell me what failed if you want help fixing it.
- [ ] **4. Confirm DEF-01.** Check `reports/screenshots/XFAIL_*` - does the site really accept 4-digit / letter postal
  codes? Update the **Defects & Observations** sheet in the workbook (Status, Evidence). If the site rejects them,
  the tests show as XPASS; then remove the `xfail` mark in `tests/test_checkout.py` and change DEF-01 to "not
  reproduced".
- [ ] **5. Run the JMeter test:** `performance\run_jmeter.bat` (3 minutes). This creates `results.jtl`,
  `aggregate.csv`, `html_report/` and **overwrites `Findings.md` with your real results**.
  Do not submit the placeholder `Findings.md`.
- [ ] **6. Write the Observations** section of `performance/Findings.md` (section 4) after reading the dashboard graphs.
  If a threshold fails, say so honestly and explain why - a documented FAIL is better than a hidden one.
- [ ] **7. Fill in the workbook:** set each test's Status (Pass / Known Defect / Fail), Actual Result, Executed By, Date on
  the **Test Cases** sheet. The **Execution Summary** sheet calculates itself.
- [ ] **8. Test on a second laptop** following only the README (reproducibility is graded).
- [ ] **9. Put the project on GitHub** (or whatever sir asks for) and submit the repo / zip.
- [ ] **10. Rehearse the demo** using `docs/DEMO_SCRIPT.md` and add your names.



## B. Suggested split of the remaining work (6 people)

| Member | Task |
|---|---|
| 1 | Install + run the suite on the real site; triage any failures (items 1-3) |
| 2 | Confirm DEF-01 and finish the Defects sheet (item 4) |
| 3 | Run JMeter, write Findings observations (items 5-6) |
| 4 | Update workbook statuses after the final run (item 7) |
| 5 | Second-laptop reproducibility test + GitHub upload (items 8-9) |
| 6 | Demo script, slides/notes if required, rehearsal (item 10) |

## C. Rules to keep following if you edit the code

- No `time.sleep` - use the wait helpers in `pages/base_page.py`.
- Locators and actions go in `pages/`, assertions go in `tests/`.
- Every test needs a marker (`smoke` or `regression`) and `@pytest.mark.fr("FR-xx")`.
- Do not run the load test with more than 20 users against the public site.
