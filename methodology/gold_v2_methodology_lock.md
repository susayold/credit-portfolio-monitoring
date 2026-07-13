# Gold v2 Methodology Lock

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Monitoring principles

1. Observed outcome metrics use matured accounts only.
2. A period with zero matured accounts is `NOT_ASSESSABLE`, never a zero bad rate.
3. EWS uses the latest eligible period and prior eligible period, not historical maxima.
4. Model metrics require at least 1,000 matured accounts and 50 bad events.
5. Synthetic servicing uses multiple origination vintages, term-aware amortisation and separate default stock/flow.
6. P6 policy scenarios are monitored as versions on a common matured population.
7. P4 ECL has scenario/assumption monitoring overlays but no fabricated prior-period trend.
8. Every alert has source-specific affected population, impact method and specific management action.
9. Reviewer rebuild uses packaged frozen inputs; author rebuild uses external project roots.
10. Validation distinguishes file presence, substantive reconciliation, executable tests and open external gates.
