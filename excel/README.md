# Excel Formula Control Model

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

Primary workbook: `Project2_CreditPortfolioMonitoring_Gold_v2_1_4.xlsx`.

The workbook contains **140 OOXML/openpyxl formula nodes**, central assumptions, formula-driven KPI reconciliation, formula-driven EWS status/variance, release controls and executive charts. An external inspector may expose fewer formula records (for example 82) because it reports a supported subset rather than every OOXML `<f>` node; the two counts are not expected to reconcile one-for-one. Runtime control relies on the full formula-node scan plus the governed cached-value reconciliation, not the external inspector count.

Excel COM calculation status: **PASS**. Requested calculation mode is **Automatic**; the resolved mode is **Automatic**, read after the workbook is open. The pre-workbook raw COM value is retained separately in `validation/windows_excel_environment.json` because it can be a non-mode sentinel.

Runtime and cached-value evidence is stored in `testing/excel_formula_runtime_tests.csv` and `testing/excel_cached_value_reconciliation.csv`.

The workbook is a control model and reviewer pack; it is not a substitute for the account-level Python engine or the pending PBIX.
