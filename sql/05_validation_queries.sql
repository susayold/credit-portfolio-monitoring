SELECT 'observed_account_key_unique' AS check_name,
       CASE WHEN COUNT(*) = COUNT(DISTINCT account_id) THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS actual_value
FROM fact_portfolio_snapshot;

SELECT 'synthetic_account_month_key_unique' AS check_name,
       CASE WHEN COUNT(*) = COUNT(DISTINCT account_id || '|' || snapshot_month) THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS actual_value
FROM fact_synthetic_servicing;

SELECT 'pd_range' AS check_name,
       CASE WHEN SUM(CASE WHEN pd < 0 OR pd > 1 OR pd IS NULL THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       SUM(CASE WHEN pd < 0 OR pd > 1 OR pd IS NULL THEN 1 ELSE 0 END) AS actual_value
FROM fact_portfolio_snapshot;

SELECT 'immature_bad_rate_is_null' AS check_name,
       CASE WHEN SUM(CASE WHEN matured_accounts = 0 AND observed_bad_rate_matured IS NOT NULL THEN 1 ELSE 0 END) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       SUM(CASE WHEN matured_accounts = 0 AND observed_bad_rate_matured IS NOT NULL THEN 1 ELSE 0 END) AS actual_value
FROM mart_portfolio_period;
