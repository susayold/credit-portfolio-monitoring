DROP TABLE IF EXISTS dim_period;
CREATE TABLE dim_period AS
SELECT DISTINCT application_period AS period_key, 'OBSERVED_COHORT' AS period_type
FROM fact_portfolio_snapshot
UNION
SELECT DISTINCT snapshot_month AS period_key, 'SYNTHETIC_SNAPSHOT' AS period_type
FROM fact_synthetic_servicing;

DROP TABLE IF EXISTS dim_risk_grade;
CREATE TABLE dim_risk_grade AS
SELECT
    ROW_NUMBER() OVER (ORDER BY SUBSTR(risk_grade, 1, 1)) AS risk_grade_key,
    risk_grade,
    SUBSTR(risk_grade, 1, 1) AS grade_code,
    CASE SUBSTR(risk_grade, 1, 1)
        WHEN 'A' THEN 1
        WHEN 'B' THEN 2
        WHEN 'C' THEN 3
        WHEN 'D' THEN 4
        WHEN 'E' THEN 5
        ELSE 99
    END AS grade_order
FROM (SELECT DISTINCT risk_grade FROM fact_portfolio_snapshot WHERE risk_grade IS NOT NULL);

DROP TABLE IF EXISTS dim_policy_decision;
CREATE TABLE dim_policy_decision AS
SELECT ROW_NUMBER() OVER (ORDER BY policy_decision) AS decision_key, policy_decision
FROM (SELECT DISTINCT policy_decision FROM fact_portfolio_snapshot WHERE policy_decision IS NOT NULL);

DROP TABLE IF EXISTS dim_dpd_bucket;
CREATE TABLE dim_dpd_bucket AS
SELECT ROW_NUMBER() OVER (ORDER BY dpd_bucket) AS dpd_bucket_key, dpd_bucket
FROM (SELECT DISTINCT dpd_bucket FROM fact_synthetic_servicing WHERE dpd_bucket IS NOT NULL);
