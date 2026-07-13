# Early-Warning and Management Action Report

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Alert state

Current EWS contains **6 Red**, **1 Amber** and **7 open actions**. Dynamic indicators use latest/prior eligible periods; P4/P5 frozen overlays are labelled `STATIC_REVIEW`.

| kri_id | metric | current_period | prior_period | current_value | prior_value | change | status | alert_state | affected_accounts | affected_exposure | estimated_impact | impact_unit | owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| KRI-001 | Observed bad rate | 2017-12 | 2017-11 | 0.2135 | 0.2088 | 0.0047 | RED | PERSISTENT | 10045.0000 | 149741725.0000 | 3581733.6241 | cost_units | Portfolio Risk |
| KRI-002 | 30+ DPD rate | 2020-10 | 2020-09 | 0.1233 | 0.1190 | 0.0044 | RED | PERSISTENT | 130.0000 | 953713.0139 |  | not_monetised | Collections |
| KRI-003 | PD PSI | 2017-12 | 2017-11 | 0.1270 | 0.1005 | 0.0265 | AMBER | PERSISTENT | 10045.0000 | 149741725.0000 |  | not_directly_monetised | Model Risk |
| KRI-004 | Absolute calibration gap | 2017-12 | 2017-11 | 0.0289 | 0.0214 | 0.0075 | GREEN | STABLE_GREEN | 10045.0000 | 149741725.0000 | 1628179.3934 | cost_units | Model Owner |
| KRI-005 | Policy exception rate | 2018-12 | 2018-11 | 0.0506 | 0.0529 | -0.0023 | RED | PERSISTENT | 63.0000 | 979125.0000 | 10.5000 | estimated_review_hours | Credit Policy |
| KRI-006 | Stage 2 proxy share | 2018-12 | NOT_AVAILABLE | 0.4830 |  |  | RED | STATIC_REVIEW | 90111.0000 | 530587218.6270 | 86813192.1033 | cost_units | Credit Risk |
| KRI-007 | Downside ECL uplift | 2018-12 downside scenario | NOT_AVAILABLE | 0.5385 |  |  | RED | STATIC_REVIEW | 186566.0000 | 1178651014.6596 | 58464058.0146 | cost_units | Finance Risk |
| KRI-008 | Critical control precision | P5 frozen v1.0.1 | NOT_AVAILABLE | 0.0132 |  |  | RED | STATIC_REVIEW | 152.0000 |  | 150.0000 | non_fraud_alerts | Fraud Strategy |

## Action quality

Each breach includes a root-cause hypothesis, affected segment, specific investigation, quantified remediation, decision required, acceptance criteria, closure evidence, dependency, owner and approver.
