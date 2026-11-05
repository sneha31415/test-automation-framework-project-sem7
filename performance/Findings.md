# Performance Test Findings - SauceDemo

*Generated automatically by `performance/analyze_results.py` on 2026-11-05 11:19 from `results/results.jtl`.*

## 1. Test configuration

| Parameter | Value |
|---|---|
| Tool | Apache JMeter (non-GUI mode) |
| Plan file | `performance/jmx/saucedemo_weekend_lab.jmx` |
| Target | https://www.saucedemo.com/ - Login page `GET /` and Products page `GET /inventory.html` |
| Load profile | 20 concurrent users, 60 s ramp-up, 3 min duration, 0-500 ms random think time |
| Concurrent users (required 20) | 20 peak active threads |
| Test window (required about 180 s) | 180 s measured |

## 2. NFR results (Pass / Fail)

| NFR ID | Requirement | Measured | Result | Notes |
|---|---|---|---|---|
| NFR-01 | Login Page P95 < 3.0 s | 0.073 s | **PASS** | 5070 samples, avg 44 ms, max 867 ms |
| NFR-02 | Products Page P95 < 4.0 s | 0.078 s | **PASS** | 5059 samples, avg 46 ms, max 909 ms |
| NFR-03 | Overall error rate < 2% | 49.99% | **FAIL** | 5063 failed of 10129 samples |

## 3. Detailed results (response times in ms)

| Label | Samples | Average | Median | P90 | P95 | P99 | Min | Max | Error % | Throughput |
|---|---|---|---|---|---|---|---|---|---|---|
| Login Page | 5070 | 44 | 37 | 61 | 73 | 136 | 1 | 867 | 0.08% | 28.23/s |
| Products Page | 5059 | 46 | 39 | 64 | 78 | 139 | 0 | 909 | 100.00% | 28.17/s |
| TOTAL | 10129 | 45 | 38 | 62 | 75 | 138 | 0 | 909 | 49.99% | 56.4/s |

Full data: `results/results.jtl`, `results/aggregate.csv`, dashboard in `html_report/index.html`.

## 4. Observations  *(team: edit this section after reviewing the HTML dashboard)*

- Response-time trend over the run: *(e.g. stable / degraded as the 20 users ramped up)*
- Anomalies, spikes or errors seen in the dashboard graphs: *(none / describe)*
- Any failed samples and their response codes: *(describe, or "none")*

## 5. Limitations of this test

- SauceDemo is a JavaScript single-page application. JMeter does not execute JavaScript, so it requests the pages
  (`/` and `/inventory.html`) directly and measures how fast the server returns them. The login form submission is
  handled client-side in the browser and is **not** a server request, so it cannot be load-tested with JMeter.
- The "Products page" sample therefore measures the page being served, not the product list being rendered in a browser.
- Results depend on the tester's network and on the shared public demo site, and will vary between runs.
- Load was limited to the 20 users specified by the lab; a public demo site must not be stress-tested beyond that.
