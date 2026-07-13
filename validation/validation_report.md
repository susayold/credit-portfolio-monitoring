# Project 2 Gold Candidate v2.1.4 Validation Report

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Automated status

**PASS - 131 automated analytical and control checks passed.**

- Executable UAT: **56/56**.
- Executable SIT: **25/25**.
- Injected negative tests: **25/25**.
- Excel formulas: **140**, with **13/13** KPI reconciliations.
- Formula count is the OOXML/openpyxl `<f>` node count; third-party inspectors may expose a supported subset and are not expected to match it one-for-one.
- Excel cached-value evidence: see `testing/excel_cached_value_reconciliation.csv`.
- DAX expected-value readiness: **66/66** typed expected values populated.
- DAX semantic lint: **12/12 PASS**; actual DAX runtime remains an external gate.
- Author/reviewer sequencing: see `validation/reference_temporal_validation.json`; reviewer rebuild evidence is in `validation/reviewer_rebuild_evidence.json`; final release scope is verified in `validation/release_manifest_verification.json`.

## Validation composition

| validation_component | total_items | pass_or_ready_items | status | evidence |
| --- | --- | --- | --- | --- |
| Artifact | 116.0000 | 116.0000 | PASS | validation/validation_checks.csv |
| Executable testing | 3.0000 | 3.0000 | PASS | validation/validation_checks.csv |
| Substantive reconciliation | 12.0000 | 12.0000 | PASS | validation/validation_checks.csv |
| Detailed UAT assertions | 56.0000 | 56.0000 | PASS | testing/uat_test_cases.csv |
| Detailed SIT assertions | 25.0000 | 25.0000 | PASS | testing/sit_test_cases.csv |
| Detailed negative controls | 25.0000 | 25.0000 | PASS | testing/negative_test_cases.csv |
| DAX semantic lint | 12.0000 | 12.0000 | PASS | testing/dax_semantic_lint_results.csv |
| DAX typed expected values | 66.0000 | 66.0000 | EXTERNAL_GATE_RUNTIME_PENDING | testing/dax_measure_test_cases.csv |
| Excel formula definition evidence | 13.0000 | 13.0000 | PASS | testing/excel_formula_runtime_tests.csv |
| Excel cached-value reconciliation | 13.0000 | 13.0000 | PASS | testing/excel_cached_value_reconciliation.csv |
| Reviewer expected-vs-actual controls | 25.0000 | 25.0000 | PASS | validation/reviewer_expected_actual_comparison.csv |
| Deterministic rebuild hash comparison | 9.0000 | 9.0000 | PASS | validation/deterministic_rebuild_comparison.csv |
| Frozen author-reference controls | 12.0000 | 12.0000 | PASS | validation/reference_control_test_results.csv |
| PBIX runtime execution | 66.0000 | 0.0000 | OPEN_EXTERNAL_GATE | powerbi/pbix_release_gate.md |
| Independent review | 1.0000 | 0.0000 | NOT_PERFORMED | validation/independent_review_checklist.csv |

## Failed automated checks

No automated failures.

## External gates

| gate_id | requirement | status | reason | closure_evidence | release_impact |
| --- | --- | --- | --- | --- | --- |
| GATE-001 | Real PBIX binary | OPEN_EXTERNAL_GATE | Desktop detected; governed PBIX has not been authored and runtime-validated | Create PBIX and pass refresh/relationship tests | Blocks unconditional Gold dashboard sign-off |
| GATE-002 | Actual DAX runtime values | OPEN_EXTERNAL_GATE | No controlled PBIX semantic-model/DAX execution evidence | Populate actual/difference/tolerance in DAX tests | Blocks Power BI measure execution claim |
| GATE-003 | Power BI screenshots | OPEN_EXTERNAL_GATE | No real PBIX | Export desktop/mobile screenshots from PBIX | Browser screenshots do not close this gate |
| GATE-004 | Independent validation | NOT_PERFORMED | Portfolio project scope | Independent reviewer signs evidence | No independent sign-off claim |
| GATE-005 | Organisational release approval | NOT_PERFORMED | Educational portfolio | Risk/BI owners approve release | No production claim |

## Release conclusion

The analytical/reviewer package is recruiter-ready. Public wording must remain conditional for Power BI completion until a real PBIX closes GATE-001 to GATE-003. Independent validation and organisational approval are not claimed.
