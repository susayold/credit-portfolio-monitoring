# Project 2 Web-First Release v1.0 Validation Report

## Release verdict

**PASS - reviewer-ready web release.** The analytical baseline is unchanged from v2.1.4; this release governs presentation, packaging, portability and claim clarity.

## Control results

| Control layer | Result | Evidence |
| --- | --- | --- |
| Analytical baseline controls | 131/131 PASS | `validation/validation_checks.csv` |
| User acceptance tests | 56/56 PASS | `testing/uat_test_cases.csv` |
| System integration tests | 25/25 PASS | `testing/sit_test_cases.csv` |
| Negative and exception tests | 25/25 PASS | `testing/negative_test_cases.csv` |
| Excel KPI reconciliation | 13/13 PASS | `validation/excel_formula_reconciliation.csv` |
| Browser dashboard checks | 25/25 PASS | `validation/web_dashboard_validation.csv` |
| Reviewer expected-versus-actual controls | PASS | `validation/reviewer_expected_actual_comparison.csv` |
| Clean-extract package verification | PASS when generated | `validation/web_first_release_manifest_verification.json` |

## Governance decisions

- `dashboard/index.html` is the only authoritative public dashboard.
- Baseline manifests are labelled as analytical baseline v2.1.4 evidence.
- `validation/web_first_release_manifest.csv` is the only current public release manifest.
- Superseded visuals and deferred Power BI assets are excluded from the release ZIP.
- The public package must contain no author-specific absolute path.

## Claim boundary

The release supports a historical educational credit portfolio monitoring case study. Observed outcomes are limited to matured accepted/booked accounts. Servicing metrics are synthetic controls-testing evidence; ECL staging is proxy-based; policy impact is a historical routing simulation. No live production, regulatory submission, audited provisioning, independent validation or organisational approval is claimed.

