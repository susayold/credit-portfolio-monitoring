# Project 2 Run Modes

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

- `quick`: validate packaged outputs and run lightweight executable controls.
- `author_reference`: rebuild from packaged frozen inputs inside an isolated workspace and capture the immutable author baseline bundle. This mode is only permitted when `P2_ALLOW_AUTHOR_REFERENCE_CAPTURE=1`.
- `reviewer`: rebuild all Project 2 outputs from the packaged observed base and frozen P3/P4/P5/P6 references. Reviewer mode must read a pre-existing author reference and cannot create or refresh it.
- `author`: refresh packaged inputs from the external portfolio project roots, then rebuild.
- `auto`: use author mode when every external source exists; otherwise reviewer mode.

The controlled route is `python scripts/run_two_phase_reproducibility.py`: isolated author-reference build, frozen-reference copy, reviewer rebuild, then clean-extract validation.
