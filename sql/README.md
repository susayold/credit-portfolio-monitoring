# Executable SQL Monitoring Layer

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

The five SQL scripts were executed with Python `sqlite3` against packaged reviewer samples. The implementation builds typed staging, two facts, four dimensions/marts and executable validation queries.

| check_name | status | actual_value |
| --- | --- | --- |
| observed_account_key_unique | PASS | 5000.0000 |
| synthetic_account_month_key_unique | PASS | 50000.0000 |
| pd_range | PASS | 0.0000 |
| immature_bad_rate_is_null | PASS | 0.0000 |
| required_sql_marts_created | PASS | 9.0000 |

`risk_grade` is explicitly loaded into staging and fact tables; the v1 missing-column defect is removed.
