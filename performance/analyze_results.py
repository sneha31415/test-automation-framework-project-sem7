"""Turns JMeter's raw results.jtl into the lab's remaining deliverables.

Reads  : performance/results/results.jtl         (written by JMeter)
Writes : performance/results/aggregate.csv       (same columns as JMeter's Aggregate Report)
         performance/Findings.md                 (NFR-01..03 mapped to Pass / Fail)

Usage  : python performance/analyze_results.py [path/to/results.jtl]

Uses only the Python standard library. Percentiles use the nearest-rank method.
"""
import csv
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PERF_DIR = Path(__file__).resolve().parent
JTL_DEFAULT = PERF_DIR / "results" / "results.jtl"
AGGREGATE_CSV = PERF_DIR / "results" / "aggregate.csv"
FINDINGS_MD = PERF_DIR / "Findings.md"

# ---- thresholds from the case study (section 6.2) ----
LOGIN_LABEL = "Login Page"
PRODUCTS_LABEL = "Products Page"
NFR01_P95_MS = 3000
NFR02_P95_MS = 4000
NFR03_ERROR_PCT = 2.0


def percentile(sorted_values, pct):
    """Nearest-rank percentile of an already sorted list."""
    if not sorted_values:
        return 0
    rank = max(1, math.ceil(pct / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def load_samples(jtl_path):
    with open(jtl_path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(rows, window_seconds):
    """Return aggregate statistics for a list of JTL rows."""
    elapsed = sorted(int(r["elapsed"]) for r in rows)
    errors = sum(1 for r in rows if r["success"].strip().lower() != "true")
    total_bytes = sum(int(r.get("bytes") or 0) for r in rows)
    sent_bytes = sum(int(r.get("sentBytes") or 0) for r in rows)
    n = len(rows)
    window = max(window_seconds, 0.001)
    return {
        "samples": n,
        "average": round(sum(elapsed) / n),
        "median": percentile(elapsed, 50),
        "p90": percentile(elapsed, 90),
        "p95": percentile(elapsed, 95),
        "p99": percentile(elapsed, 99),
        "min": elapsed[0],
        "max": elapsed[-1],
        "error_pct": round(errors / n * 100, 2),
        "errors": errors,
        "throughput": round(n / window, 2),
        "received_kbps": round(total_bytes / 1024 / window, 2),
        "sent_kbps": round(sent_bytes / 1024 / window, 2),
    }


def write_aggregate_csv(stats_by_label, total):
    AGGREGATE_CSV.parent.mkdir(parents=True, exist_ok=True)
    header = ["Label", "# Samples", "Average", "Median", "90% Line", "95% Line", "99% Line",
              "Min", "Max", "Error %", "Throughput", "Received KB/sec", "Sent KB/sec"]
    with open(AGGREGATE_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for label, s in list(stats_by_label.items()) + [("TOTAL", total)]:
            writer.writerow([label, s["samples"], s["average"], s["median"], s["p90"], s["p95"],
                             s["p99"], s["min"], s["max"], f"{s['error_pct']:.2f}%",
                             s["throughput"], s["received_kbps"], s["sent_kbps"]])


def verdict(passed):
    return "PASS" if passed else "FAIL"


def write_findings(stats_by_label, total, rows, window_seconds):
    login = stats_by_label.get(LOGIN_LABEL)
    products = stats_by_label.get(PRODUCTS_LABEL)

    def nfr_row(nfr_id, label, stats, limit_ms):
        if stats is None:
            return f"| {nfr_id} | {label} P95 < {limit_ms / 1000:.1f} s | n/a | **FAIL** | No samples labelled '{label}' in results.jtl |"
        ok = stats["p95"] < limit_ms
        return (f"| {nfr_id} | {label} P95 < {limit_ms / 1000:.1f} s | {stats['p95'] / 1000:.3f} s "
                f"| **{verdict(ok)}** | {stats['samples']} samples, avg {stats['average']} ms, max {stats['max']} ms |")

    nfr3_ok = total["error_pct"] < NFR03_ERROR_PCT
    nfr3 = (f"| NFR-03 | Overall error rate < {NFR03_ERROR_PCT:.0f}% | {total['error_pct']:.2f}% "
            f"| **{verdict(nfr3_ok)}** | {total['errors']} failed of {total['samples']} samples |")

    peak_users = max((int(r["allThreads"]) for r in rows if r.get("allThreads", "").isdigit()), default=None)
    config_lines = [
        f"| Concurrent users (required 20) | {peak_users if peak_users is not None else 'not recorded'} peak active threads |",
        f"| Test window (required about 180 s) | {window_seconds:.0f} s measured |",
    ]

    result_lines = []
    for label, s in list(stats_by_label.items()) + [("TOTAL", total)]:
        result_lines.append(
            f"| {label} | {s['samples']} | {s['average']} | {s['median']} | {s['p90']} | {s['p95']} "
            f"| {s['p99']} | {s['min']} | {s['max']} | {s['error_pct']:.2f}% | {s['throughput']}/s |")

    text = f"""# Performance Test Findings - SauceDemo

*Generated automatically by `performance/analyze_results.py` on {datetime.now():%Y-%m-%d %H:%M} from `results/results.jtl`.*

## 1. Test configuration

| Parameter | Value |
|---|---|
| Tool | Apache JMeter (non-GUI mode) |
| Plan file | `performance/jmx/saucedemo_weekend_lab.jmx` |
| Target | https://www.saucedemo.com/ - Login page `GET /` and Products page `GET /inventory.html` |
| Load profile | 20 concurrent users, 60 s ramp-up, 3 min duration, 0-500 ms random think time |
{chr(10).join(config_lines)}

## 2. NFR results (Pass / Fail)

| NFR ID | Requirement | Measured | Result | Notes |
|---|---|---|---|---|
{nfr_row("NFR-01", LOGIN_LABEL, login, NFR01_P95_MS)}
{nfr_row("NFR-02", PRODUCTS_LABEL, products, NFR02_P95_MS)}
{nfr3}

## 3. Detailed results (response times in ms)

| Label | Samples | Average | Median | P90 | P95 | P99 | Min | Max | Error % | Throughput |
|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(result_lines)}

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
"""
    FINDINGS_MD.write_text(text, encoding="utf-8")


def main():
    jtl_path = Path(sys.argv[1]) if len(sys.argv) > 1 else JTL_DEFAULT
    if not jtl_path.exists():
        sys.exit(f"[ERROR] {jtl_path} not found. Run performance\\run_jmeter.bat first.")

    rows = load_samples(jtl_path)
    if not rows:
        sys.exit("[ERROR] results.jtl contains no samples.")

    # measured test window: first sample start -> last sample end (seconds)
    starts = [int(r["timeStamp"]) for r in rows]
    ends = [int(r["timeStamp"]) + int(r["elapsed"]) for r in rows]
    window_seconds = (max(ends) - min(starts)) / 1000

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["label"]].append(row)

    stats_by_label = {label: summarize(label_rows, window_seconds) for label, label_rows in grouped.items()}
    total = summarize(rows, window_seconds)

    write_aggregate_csv(stats_by_label, total)
    write_findings(stats_by_label, total, rows, window_seconds)
    print(f"Wrote {AGGREGATE_CSV.relative_to(PERF_DIR.parent)}")
    print(f"Wrote {FINDINGS_MD.relative_to(PERF_DIR.parent)}")
    for label in (LOGIN_LABEL, PRODUCTS_LABEL):
        if label in stats_by_label:
            print(f"  {label}: P95 = {stats_by_label[label]['p95']} ms")
    print(f"  Overall error rate: {total['error_pct']:.2f}%")


if __name__ == "__main__":
    main()
