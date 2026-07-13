DROP TABLE IF EXISTS fact_portfolio_snapshot;
CREATE TABLE fact_portfolio_snapshot AS
SELECT * FROM stg_p2_observed_accounts;

DROP TABLE IF EXISTS fact_synthetic_servicing;
CREATE TABLE fact_synthetic_servicing AS
SELECT * FROM stg_p2_synthetic_snapshots;

CREATE UNIQUE INDEX ux_fact_portfolio_account ON fact_portfolio_snapshot(account_id);
CREATE UNIQUE INDEX ux_fact_servicing_account_month ON fact_synthetic_servicing(account_id, snapshot_month);
