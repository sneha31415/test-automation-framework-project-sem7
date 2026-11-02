# Performance Test Findings - SauceDemo

> **STATUS: NOT YET EXECUTED.**
> This file is a placeholder. After you run `performance\run_jmeter.bat`, the script
> `analyze_results.py` **overwrites this file** with the real P95 values, error rate and
> Pass/Fail verdicts for NFR-01 to NFR-03. Do not submit this placeholder.

## Planned test configuration

| Parameter | Value |
|---|---|
| Tool | Apache JMeter (non-GUI mode) |
| Plan file | `performance/jmx/saucedemo_weekend_lab.jmx` |
| Target | https://www.saucedemo.com/ - Login page `GET /` and Products page `GET /inventory.html` |
| Load profile | 20 concurrent users, 60 s ramp-up, 3 min duration, 0-500 ms random think time |

## NFR thresholds to be verified

| NFR ID | Requirement | Measured | Result |
|---|---|---|---|
| NFR-01 | Login page response time P95 < 3.0 s | *pending run* | *pending* |
| NFR-02 | Products page response time P95 < 4.0 s | *pending run* | *pending* |
| NFR-03 | Overall error rate < 2% | *pending run* | *pending* |
