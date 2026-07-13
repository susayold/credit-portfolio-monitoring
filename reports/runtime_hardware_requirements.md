# Runtime and Hardware Requirements

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Tested environment

| Item | Value |
| --- | --- |
| Operating system | Windows-10-10.0.19045-SP0 |
| Python | 3.14.2 |
| CPU count | 6 |
| Memory GB | 23.94 |
| Pipeline scripts | 1 |
| Pipeline duration seconds | 6.904 |

## Reviewer guidance

- Use `python scripts/run_two_phase_reproducibility.py` for the complete author-then-reviewer evidence route.
- Use `python scripts/run_reviewer_rebuild_with_evidence.py` only with a pre-existing frozen author reference.
- Use `P2_RUN_MODE=quick python scripts/run_full_pipeline.py` for read-only manifest and executable-suite validation.
- The full package includes large observed/synthetic files; use the AI review light ZIP only for content review, not full rebuild.
- Power BI Desktop is still required separately for PBIX/DAX runtime gates.
