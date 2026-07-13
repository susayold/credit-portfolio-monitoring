PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS stg_p2_observed_accounts;
DROP TABLE IF EXISTS stg_p2_synthetic_snapshots;

CREATE TABLE stg_p2_observed_accounts AS
SELECT
    CAST(account_id AS TEXT) AS account_id,
    CAST(application_period AS TEXT) AS application_period,
    CAST(matured_flag AS INTEGER) AS matured_flag,
    CAST(outcome_eligible_flag AS INTEGER) AS outcome_eligible_flag,
    CAST(bad_flag AS INTEGER) AS bad_flag,
    CAST(pd AS REAL) AS pd,
    CAST(scorecard_points AS REAL) AS scorecard_points,
    CAST(risk_grade AS TEXT) AS risk_grade,
    CAST(exposure AS REAL) AS exposure,
    CAST(expected_loss AS REAL) AS expected_loss,
    CAST(stage_proxy AS TEXT) AS stage_proxy,
    CAST(policy_version AS TEXT) AS policy_version,
    CAST(policy_decision AS TEXT) AS policy_decision,
    CAST(exception_flag AS INTEGER) AS exception_flag,
    CAST(fico AS REAL) AS fico,
    CAST(dti AS REAL) AS dti,
    CAST(purpose AS TEXT) AS purpose
FROM raw_observed;

CREATE UNIQUE INDEX ux_stg_observed_account ON stg_p2_observed_accounts(account_id);
CREATE INDEX ix_stg_observed_period ON stg_p2_observed_accounts(application_period);
CREATE INDEX ix_stg_observed_grade ON stg_p2_observed_accounts(risk_grade);

CREATE TABLE stg_p2_synthetic_snapshots AS
SELECT
    CAST(account_id AS TEXT) AS account_id,
    CAST(origination_vintage AS TEXT) AS origination_vintage,
    CAST(snapshot_month AS TEXT) AS snapshot_month,
    CAST(months_on_book AS INTEGER) AS months_on_book,
    CAST(term_months AS INTEGER) AS term_months,
    CAST(beginning_balance AS REAL) AS beginning_balance,
    CAST(ending_balance AS REAL) AS ending_balance,
    CAST(beginning_dpd_bucket AS TEXT) AS beginning_dpd_bucket,
    CAST(dpd_bucket AS TEXT) AS dpd_bucket,
    CAST(new_delinquency_inflow_flag AS INTEGER) AS new_delinquency_inflow_flag,
    CAST(cure_flag AS INTEGER) AS cure_flag,
    CAST(new_default_flag AS INTEGER) AS new_default_flag,
    CAST(default_stock_flag AS INTEGER) AS default_stock_flag,
    CAST(closure_flow_flag AS INTEGER) AS closure_flow_flag,
    CAST(risk_grade AS TEXT) AS risk_grade,
    CAST(policy_version AS TEXT) AS policy_version
FROM raw_synthetic;

CREATE UNIQUE INDEX ux_stg_synthetic_account_month
ON stg_p2_synthetic_snapshots(account_id, snapshot_month);
CREATE INDEX ix_stg_synthetic_month ON stg_p2_synthetic_snapshots(snapshot_month);
