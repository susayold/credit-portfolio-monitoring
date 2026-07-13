# Reviewer Rebuild Runtime Guide

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Environment recorded during latest controlled rebuild

| Item | Value |
| --- | --- |
| Operating system | Windows-10-10.0.19045-SP0 |
| Python | 3.14.2 |
| Processor | Intel64 Family 6 Model 158 Stepping 10, GenuineIntel |
| Machine | AMD64 |
| CPU cores | 6 |
| Memory GB | 23.94 |
| Working directory | <PROJECT_ROOT> |
| Pipeline start | 2026-07-13T13:58:49 |
| Pipeline end | 2026-07-13T13:58:56 |
| Pipeline duration seconds | 6.904 |
| Pipeline scripts | 1 |
| Observed account-base size bytes | 52340233 |
| Synthetic monthly snapshot size bytes | 34620132 |
| Excel availability | See `validation/windows_excel_environment.json` |
| Power BI availability | OPEN_EXTERNAL_GATE; no PBIX runtime executed in v2.1.4 |

## Per-script runtime

| script_name | duration_seconds | status |
| --- | --- | --- |
| 10_validate_final_outputs.py | 6.9040 | PASS |

## Reviewer guidance

- Run `python scripts/run_two_phase_reproducibility.py` to create the isolated author baseline, freeze it before reviewer start, execute the reviewer rebuild and test the final ZIP on clean extract.
- Run `python scripts/run_reviewer_rebuild_with_evidence.py` only when a valid frozen author reference already exists.
- Run `P2_RUN_MODE=quick python scripts/run_full_pipeline.py` for read-only package validation.
- The full package includes large observed/synthetic files; the AI review light ZIP is for content review only and cannot prove full rebuild.
- Power BI Desktop is still required separately for v2.2 PBIX/DAX runtime closure.
