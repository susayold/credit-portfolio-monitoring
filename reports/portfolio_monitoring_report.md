# Portfolio Monitoring Report

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Current condition

Latest eligible observed period: **2017-12**. Matured bad rate: **21.35%**, change versus 2017-11: **+47 bps**. Total booked accounts: **1,347,681**; matured coverage: **95.83%**.

## Current/prior/change

| metric | current_period | current | prior | change | status | evidence_note |
| --- | --- | --- | --- | --- | --- | --- |
| Observed bad rate matured | 2017-12 | 0.2135 | 0.2088 | 0.0047 | RED | Matured outcomes only |
| AUC | 2017-12 | 0.5968 | 0.6100 | -0.0132 | MONITOR | Moderate ranking; not strong |
| PD PSI | 2017-12 | 0.1270 | 0.1005 | 0.0265 | AMBER | Fixed development bins |
| Calibration gap | 2017-12 | 0.0289 | 0.0214 | 0.0075 | GREEN | Observed minus predicted |
| Synthetic 30+ DPD | 2020-10 | 0.1233 | 0.1190 | 0.0044 | RED | Synthetic controls only; latest eligible KRI period |

## Interpretation

Immature cohorts are excluded from bad-rate and calibration denominators. Their outcome is `NOT_ASSESSABLE`, not zero. Composition and exposure remain monitorable for those cohorts.
