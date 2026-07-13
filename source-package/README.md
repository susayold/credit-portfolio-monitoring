# Project 2 - Credit Portfolio Monitoring and Early Warning

## Portfolio review path

- Start: `OPEN_THIS_FIRST.html`
- Decision summary: `EXECUTIVE_SUMMARY.md`
- Interactive command center: `dashboard/index.html`
- Validation: `VALIDATION_SUMMARY.md`
- Limitations: `LIMITATIONS.md`
- Artifact map: `ARTIFACT_INDEX.md`

> Public delivery: **Web-First Release v1.0**. Analytical foundation: reviewer-mode reproducibility checked **v2.1.4**. Power BI implementation is intentionally excluded from this release.

## Business purpose

This project demonstrates how a Portfolio Risk Analyst converts frozen credit-risk evidence into a governed monitoring process that answers four management questions: what changed, why it matters, what decision is required, and what evidence closes the action.

Open `OPEN_THIS_FIRST.html`, then use `dashboard/index.html` as the authoritative interactive dashboard.

## Portfolio evidence

- 1,347,681 historical accepted/booked accounts; 1,291,521 matured outcome records.
- Latest observed matured bad rate 21.35%, up 47 bps versus 2017-11.
- Latest AUC 0.597, fixed-bin PD PSI 0.127 and calibration gap 2.89%.
- Grades D/E contain 673,840 accounts and represent 50.00% of the portfolio.
- The 20% policy candidate reduces routed auto-approved expected loss by 49.96%, while approval drops 30.32pp and manual review rises 150.0% versus baseline.
- Management recommendation: `PILOT_WITH_CAPACITY_REDESIGN`, not wholesale rollout.

## What the release proves

- Maturity-safe portfolio quality, concentration and period movement.
- Frozen model monitoring using AUC, tie-safe KS, calibration and population drift.
- Policy scenario trade-offs across approval, manual review, bad capture and expected-loss routing.
- Proxy ECL sensitivity with explicit Stage 2 and time-series limitations.
- KRI thresholds, accountable owners, actions, acceptance criteria and closure evidence.
- Rebuildable Python and SQL logic, a formula-driven Excel control model and an interactive browser dashboard.

## Validation

- Analytical controls: 131/131 PASS.
- UAT: 56/56 PASS.
- SIT: 25/25 PASS.
- Negative tests: 25/25 PASS.
- Excel KPI reconciliation: 13/13 PASS.
- Web dashboard checks: 25/25 PASS.
- Frozen author baseline and reviewer rebuild are compared by hashes, row counts and controlled run evidence.

See `validation/web_first_release_validation_report.md` and `validation/web_first_release_manifest_verification.json`.

## Claim boundary

Observed credit outcomes cover historical matured accepted/booked accounts, not the full applicant population. Monthly servicing, DPD, roll-rate, cure and vintage outputs are synthetic controls-testing evidence. ECL staging is proxy-based. Policy results are historical booked-account routing simulations, not realised loss reduction. This is not a live servicing platform, regulatory submission, production model validation, audited provisioning process or organisational sign-off.

## Primary artifacts

- `dashboard/index.html` - authoritative browser dashboard.
- `excel/Project2_CreditPortfolioMonitoring_Gold_v2_1_4.xlsx` - formula-driven control model.
- `reports/risk_committee_monitoring_memo.md` - management decision memo.
- `validation/web_first_release_validation_report.md` - current release validation.
- `PACKAGE_INDEX.md` - authoritative package map.

