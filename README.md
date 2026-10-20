# Operations Analytics & Data Quality
**Portfolio prepared for Teja Manjusree Koduru · SQL · Python · KPI reporting**

An end-to-end, reproducible demonstration of checking delivery records before calculating operational KPIs. This connects quality-assurance thinking with analytics: define rules, quarantine ambiguous records, preserve an audit trail, and explain the business denominator.

**Transparency:** this project was created with AI assistance as a portfolio learning project. All records are fictional, generated with seed 42. It is not work performed for Flink, RMSI or any other employer, and is not the original master's thesis. Review and understand the implementation before presenting it in an interview.

## Open the results
- [Dashboard](outputs/dashboard.html) — download/open locally; GitHub displays HTML source rather than rendering the dashboard.
- [Generated findings](outputs/findings.md)
- [SQL scorecard](outputs/operations_kpis.csv)
- [Row-level audit](outputs/quality_issues.csv)

## Reproduce in two commands
Python 3.10+; no third-party dependencies, downloads or credentials.
```sh
python run.py
python -m unittest discover -s tests -v
```
Run from the repository root. Each run replaces the deterministic sample data and outputs. The pipeline also resolves its own file paths if launched elsewhere.

## What this demonstrates
| Work sample | Evidence |
|---|---|
| SQL aggregation, CTEs, conditional logic, window ranking | `sql/operations_kpis.sql` |
| Date and hub reporting grain | `sql/daily_trends.sql` |
| Python quality rules and exception handling | `src/quality.py` |
| Traceable rejects, reproducible data preparation | `outputs/quality_issues.csv`, `run.py` |
| Automated edge-case checks | `tests/test_quality.py` |
| Communicating KPIs and limitations | `outputs/dashboard.html`, `outputs/findings.md` |

## Method
1. Generate 1,200 fictional orders across three hubs and append one intentional duplicate.
2. Inject a small set of missing, invalid and inconsistent values.
3. Validate IDs, hub/status domains, nonnegative finite revenue and timestamp consistency.
4. Quarantine every failing row. Keep every failed rule and original CSV line number.
5. Load accepted orders into in-memory SQLite, enforcing unique order IDs.
6. Export hub KPIs, daily trends, clean data and a standalone HTML scorecard.

## Metric contract
| Metric | Definition |
|---|---|
| Accepted order | Input row that passes all implemented rules |
| On-time delivery % | Delivered orders with delivered_at ≤ promised_at / delivered orders × 100 |
| Cancellation % | Cancelled accepted orders / all accepted orders × 100 |
| Delivered sales EUR | Sum of order value for delivered accepted orders; not profit |
| Average delivery minutes | Mean placed-to-delivered duration, delivered accepted orders only |
| Rejected row % | Distinct rejected source rows / input rows × 100 |

Zero denominators return SQL NULL. A delivery exactly at the promise counts as on time. All occurrences of a duplicated ID are quarantined instead of choosing a record arbitrarily.

## Limits and next decisions
Synthetic data intentionally makes Berlin slower. The difference is a demonstration, not evidence about real logistics. Rejections can bias the resulting KPIs, so investigate rejected rows before using this approach for decisions. The sample assumes naive timestamps in one timezone, a fixed CSV schema and EUR currency. It does not model refunds, taxes, source freshness, real-time ingestion or schema drift. Revenue thresholds and operational SLA definitions require a business owner in production.

For a real use case, first confirm the source contract and timezone policy, assess missingness by hub/day, then investigate staffing, demand and routing with comparable order groups.

## Optional Power BI extension
Import `outputs/clean_orders.csv`, `outputs/daily_trends.csv` and `outputs/operations_kpis.csv`. Use the provided [build guide and DAX](docs/POWER_BI.md). **No Power BI `.pbix` file is included or claimed.** The HTML report is already runnable.

## Interview walkthrough
Explain why a cancelled order is excluded from the on-time denominator, why both duplicate rows are rejected, how quarantine can introduce bias, and why a simulated hub gap does not prove a cause. Then change a quality rule and rerun the tests and pipeline.
