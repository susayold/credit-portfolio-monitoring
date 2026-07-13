DROP TABLE IF EXISTS mart_portfolio_period;
CREATE TABLE mart_portfolio_period AS
SELECT
    application_period,
    COUNT(*) AS accounts,
    SUM(matured_flag) AS matured_accounts,
    SUM(CASE WHEN matured_flag = 1 THEN bad_flag ELSE 0 END) AS matured_bad_accounts,
    CASE WHEN SUM(matured_flag) = 0 THEN NULL
         ELSE 1.0 * SUM(CASE WHEN matured_flag = 1 THEN bad_flag ELSE 0 END) / SUM(matured_flag)
    END AS observed_bad_rate_matured,
    SUM(exposure) AS exposure,
    AVG(pd) AS average_pd_all,
    CASE WHEN SUM(matured_flag) = 0 THEN NULL
         ELSE SUM(CASE WHEN matured_flag = 1 THEN pd ELSE 0 END) / SUM(matured_flag)
    END AS average_pd_matured,
    SUM(expected_loss) AS expected_loss
FROM fact_portfolio_snapshot
GROUP BY application_period;

DROP TABLE IF EXISTS mart_synthetic_stock_flow;
CREATE TABLE mart_synthetic_stock_flow AS
SELECT
    snapshot_month,
    COUNT(*) AS accounts,
    SUM(CASE WHEN beginning_dpd_bucket IN ('1-29','30-59','60-89','90+') THEN 1 ELSE 0 END) AS beginning_delinquent_stock,
    SUM(new_delinquency_inflow_flag) AS new_delinquency_inflow,
    SUM(cure_flag) AS cures,
    SUM(new_default_flag) AS new_default_flow,
    SUM(default_stock_flag) AS ending_default_stock,
    SUM(closure_flow_flag) AS closures,
    SUM(CASE WHEN dpd_bucket IN ('1-29','30-59','60-89','90+') THEN 1 ELSE 0 END) AS ending_delinquent_stock
FROM fact_synthetic_servicing
GROUP BY snapshot_month;

DROP TABLE IF EXISTS mart_vintage;
CREATE TABLE mart_vintage AS
SELECT
    origination_vintage,
    months_on_book,
    term_months,
    risk_grade,
    COUNT(*) AS accounts,
    SUM(ending_balance) AS ending_balance,
    AVG(default_stock_flag) AS default_stock_rate,
    AVG(CASE WHEN dpd_bucket IN ('30-59','60-89','90+','Default') THEN 1.0 ELSE 0.0 END) AS dpd_30_plus_rate
FROM fact_synthetic_servicing
GROUP BY origination_vintage, months_on_book, term_months, risk_grade;
