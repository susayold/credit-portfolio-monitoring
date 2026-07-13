# Monthly Snapshot Methodology

> Educational portfolio monitoring framework. Observed credit metrics are based on historical accepted/booked portfolio evidence and frozen upstream project outputs. Delinquency/roll-rate/monthly servicing metrics are synthetic controls-testing demonstrations. No live servicing, regulatory reporting, production model monitoring, Power BI refresh, independent validation or organisational sign-off is claimed.

Observed monthly monitoring is cohort-based. Synthetic monthly snapshots are generated account x month with beginning balance, payment due, payment received, ending balance, DPD, DPD bucket, default/cure/closed flags and collection queue. The synthetic generator uses PD/grade as risk inputs but does not copy the observed bad flag into monthly DPD status.
