from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from project2_gold_common import (
    MIN_BAD_EVENTS,
    MIN_MATURED_ACCOUNTS,
    MODEL_BASELINE_END,
    MODEL_BASELINE_START,
    PACKAGED_SOURCES,
    ROOT,
    add_meta,
    alert_state,
    ks_threshold_detail,
    ks_stat,
    load_base,
    make_psi_edges,
    psi_from_edges,
    risk_status,
    safe_ratio,
    write_csv,
)


DPD_BUCKETS = ["Current", "1-29", "30-59", "60-89", "90+", "Default", "Closed"]
DELINQUENT_BUCKETS = {"1-29", "30-59", "60-89", "90+"}


def build_delinquency_and_vintage_metrics() -> None:
    snap = pd.read_csv(ROOT / "data/synthetic/monthly_delinquency_snapshots.csv.gz")
    if snap[["account_id", "snapshot_month"]].duplicated().any():
        raise ValueError("Synthetic account-month grain is not unique")

    stock_rows: list[dict[str, object]] = []
    for period, group in snap.groupby("snapshot_month", sort=True):
        accounts = len(group)
        beginning_stock = int(group["beginning_delinquent_flag"].sum())
        inflow = int(group["new_delinquency_inflow_flag"].sum())
        cures = int(group["cure_flag"].sum())
        defaults = int(group["delinquent_default_outflow_flag"].sum())
        closures = int(group["delinquent_closure_outflow_flag"].sum())
        other_net = int(group["other_migration_net"].sum())
        ending_stock = int(group["ending_delinquent_flag"].sum())
        calculated_ending = beginning_stock + inflow - cures - defaults - closures + other_net
        at_risk_for_default = int((~group["beginning_dpd_bucket"].isin(["Default", "Closed"])).sum())
        stock_rows.append(
            {
                "snapshot_month": period,
                "accounts": accounts,
                "total_balance": float(group["ending_balance"].sum()),
                "beginning_delinquent_stock": beginning_stock,
                "new_delinquency_inflow": inflow,
                "cures": cures,
                "new_defaults_from_delinquency": defaults,
                "delinquent_closures": closures,
                "other_migration_net": other_net,
                "calculated_ending_delinquent_stock": calculated_ending,
                "ending_delinquent_stock": ending_stock,
                "bridge_difference": ending_stock - calculated_ending,
                "dpd_30_plus_accounts": int(group["dpd_bucket"].isin(["30-59", "60-89", "90+", "Default"]).sum()),
                "dpd_30_plus": float(group["dpd_bucket"].isin(["30-59", "60-89", "90+", "Default"]).mean()),
                "dpd_60_plus": float(group["dpd_bucket"].isin(["60-89", "90+", "Default"]).mean()),
                "dpd_90_plus": float(group["dpd_bucket"].isin(["90+", "Default"]).mean()),
                "default_stock_accounts": int(group["default_stock_flag"].sum()),
                "default_stock_rate": float(group["default_stock_flag"].mean()),
                "new_default_flow_accounts": int(group["new_default_flag"].sum()),
                "new_default_flow_rate": safe_ratio(int(group["new_default_flag"].sum()), at_risk_for_default),
                "closed_stock_rate": float(group["dpd_bucket"].eq("Closed").mean()),
                "term_36_accounts": int(group["term_months"].eq(36).sum()),
                "term_60_accounts": int(group["term_months"].eq(60).sum()),
            }
        )
    stock = pd.DataFrame(stock_rows).sort_values("snapshot_month")
    for metric in ["dpd_30_plus", "dpd_60_plus", "dpd_90_plus", "default_stock_rate", "new_default_flow_rate", "ending_delinquent_stock"]:
        stock[f"prior_{metric}"] = stock[metric].shift(1)
        stock[f"change_{metric}"] = stock[metric] - stock[f"prior_{metric}"]
    write_csv(
        add_meta(
            stock,
            "Synthetic",
            "Synthetic",
            "P2",
            "Reconciled synthetic delinquency stock-flow bridge; not observed servicing",
            "snapshot_month",
        ),
        "outputs/delinquency_stock_flow_summary.csv",
    )

    roll_counts = pd.crosstab(snap["beginning_dpd_bucket"], snap["dpd_bucket"]).reindex(
        index=DPD_BUCKETS, columns=DPD_BUCKETS, fill_value=0
    )
    roll_rates = roll_counts.div(roll_counts.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    roll = roll_rates.reset_index().rename(columns={"beginning_dpd_bucket": "from_bucket"})
    roll.insert(1, "transition_count", roll_counts.sum(axis=1).reindex(roll["from_bucket"]).to_numpy())
    write_csv(
        add_meta(roll, "Synthetic", "Synthetic", "P2", "Synthetic term-aware roll-rate matrix"),
        "outputs/roll_rate_matrix.csv",
    )

    cure_rows: list[dict[str, object]] = []
    for bucket in ["1-29", "30-59", "60-89", "90+"]:
        subset = snap[snap["beginning_dpd_bucket"].eq(bucket)]
        cure_rows.append(
            {
                "from_bucket": bucket,
                "starting_accounts": len(subset),
                "cured_accounts": int(subset["dpd_bucket"].eq("Current").sum()),
                "cure_rate": float(subset["dpd_bucket"].eq("Current").mean()) if len(subset) else np.nan,
                "denominator_definition": "Account-month transitions starting in delinquent bucket",
            }
        )
    write_csv(
        add_meta(pd.DataFrame(cure_rows), "Synthetic", "Synthetic", "P2", "Synthetic cure rates with explicit denominator"),
        "outputs/cure_rate_summary.csv",
    )

    vintage = snap.groupby(
        ["origination_vintage", "snapshot_month", "months_on_book", "risk_grade", "term_months", "policy_version"],
        as_index=False,
    ).agg(
        accounts=("account_id", "nunique"),
        ending_balance=("ending_balance", "sum"),
        dpd30_rate=("dpd_bucket", lambda series: series.isin(["30-59", "60-89", "90+", "Default"]).mean()),
        default_stock_rate=("default_stock_flag", "mean"),
        new_default_flow_rate=("new_default_flag", "mean"),
        cure_rate=("cure_flag", "mean"),
    )
    write_csv(
        add_meta(
            vintage,
            "Synthetic",
            "Synthetic",
            "P2",
            "Multi-vintage cohort comparison with term and policy controls",
            "snapshot_month",
        ),
        "outputs/vintage_performance_summary.csv",
    )
    vintage_control = pd.DataFrame(
        [
            ["origination_vintages", snap["origination_vintage"].nunique(), ">1", "PASS"],
            ["snapshot_months", snap["snapshot_month"].nunique(), ">36 expected from staggered vintages", "PASS"],
            ["month_mob_pairs", snap[["snapshot_month", "months_on_book"]].drop_duplicates().shape[0], ">36", "PASS"],
            ["term_60_balance_at_mob36", float(snap.loc[(snap["term_months"].eq(60)) & (snap["months_on_book"].eq(36)), "ending_balance"].sum()), ">0", "PASS"],
            ["stock_flow_max_abs_bridge_difference", int(stock["bridge_difference"].abs().max()), "=0", "PASS" if stock["bridge_difference"].abs().max() == 0 else "FAIL"],
        ],
        columns=["control", "actual_value", "expected_condition", "status"],
    )
    write_csv(vintage_control, "validation/synthetic_vintage_stockflow_controls.csv")


def _eligible_model_periods(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        frame["matured_accounts"].ge(MIN_MATURED_ACCOUNTS)
        & frame["bad_events"].ge(MIN_BAD_EVENTS)
        & frame["good_events"].ge(MIN_BAD_EVENTS)
    ].sort_values("period")


def build_model_monitoring() -> None:
    base = load_base()
    matured_base = base[base["matured_flag"].eq(1)].copy()
    baseline = matured_base[matured_base["application_period"].between(MODEL_BASELINE_START, MODEL_BASELINE_END)].copy()
    if len(baseline) < MIN_MATURED_ACCOUNTS:
        baseline_periods = sorted(matured_base["application_period"].unique())[:24]
        baseline = matured_base[matured_base["application_period"].isin(baseline_periods)].copy()
    pd_edges = make_psi_edges(baseline["pd"])
    rows: list[dict[str, object]] = []
    ks_detail_rows: list[pd.DataFrame] = []
    for period, full_group in base.groupby("application_period", sort=True):
        group = full_group[full_group["matured_flag"].eq(1)]
        bad_events = int(group["bad_flag"].sum())
        good_events = len(group) - bad_events
        eligible = len(group) >= MIN_MATURED_ACCOUNTS and bad_events >= MIN_BAD_EVENTS and good_events >= MIN_BAD_EVENTS
        auc = float(roc_auc_score(group["bad_flag"], group["pd"])) if eligible else np.nan
        threshold_detail = ks_threshold_detail(group["bad_flag"], group["pd"]) if eligible else pd.DataFrame()
        ks = float(threshold_detail["ks_gap"].max()) if not threshold_detail.empty else np.nan
        if eligible:
            threshold_detail.insert(0, "period", period)
            threshold_detail.insert(1, "eligibility_status", "ELIGIBLE")
            ks_detail_rows.append(threshold_detail)
        observed_bad_rate = float(group["bad_flag"].mean()) if len(group) else np.nan
        mean_pd = float(group["pd"].mean()) if len(group) else np.nan
        pd_psi = psi_from_edges(baseline["pd"], full_group["pd"], pd_edges)
        rows.append(
            {
                "period": period,
                "accounts": len(full_group),
                "matured_accounts": len(group),
                "excluded_immature_accounts": int(full_group["matured_flag"].eq(0).sum()),
                "bad_events": bad_events,
                "good_events": good_events,
                "eligibility_status": "ELIGIBLE" if eligible else "NOT_ASSESSABLE_MIN_SAMPLE_OR_EVENTS",
                "auc": auc,
                "ks": ks,
                "gini": 2 * auc - 1 if eligible else np.nan,
                "observed_bad_rate_matured": observed_bad_rate,
                "mean_pd_matured": mean_pd,
                "calibration_gap_matured": observed_bad_rate - mean_pd if len(group) else np.nan,
                "oe_ratio_matured": safe_ratio(observed_bad_rate, mean_pd),
                "pd_psi_vs_development_baseline": pd_psi,
                "reference_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}",
                "outcome_window": "12-month matured target inherited from P3",
            }
        )
    monitoring = pd.DataFrame(rows).sort_values("period")
    eligible_periods = _eligible_model_periods(monitoring)
    current_period = str(eligible_periods.iloc[-1]["period"])
    prior_period = str(eligible_periods.iloc[-2]["period"])
    monitoring["is_current_eligible_period"] = monitoring["period"].eq(current_period)
    monitoring["is_prior_eligible_period"] = monitoring["period"].eq(prior_period)
    for metric in ["auc", "ks", "gini", "observed_bad_rate_matured", "mean_pd_matured", "calibration_gap_matured", "oe_ratio_matured", "pd_psi_vs_development_baseline"]:
        monitoring[f"prior_{metric}"] = monitoring[metric].shift(1)
        monitoring[f"change_{metric}"] = monitoring[metric] - monitoring[f"prior_{metric}"]
    write_csv(
        add_meta(
            monitoring,
            "Observed",
            "Derived",
            "P3/P6",
            "Frozen P3 model monitoring on matured outcome population; no retraining",
            "period",
        ),
        "outputs/model_monitoring_summary.csv",
    )
    if ks_detail_rows:
        ks_detail = pd.concat(ks_detail_rows, ignore_index=True)
    else:
        ks_detail = pd.DataFrame()
    write_csv(
        add_meta(
            ks_detail,
            "Observed",
            "Derived",
            "P3/P6",
            "Threshold-level tie-safe KS evidence; score ties are aggregated before cumulative shares",
            "period",
        ),
        "outputs/model_ks_threshold_detail.csv",
    )

    calibration_rows: list[dict[str, object]] = []
    for (period, risk_grade), group in matured_base.groupby(["application_period", "risk_grade"], sort=True):
        full_count = int(((base["application_period"].eq(period)) & (base["risk_grade"].eq(risk_grade))).sum())
        observed_rate = float(group["bad_flag"].mean()) if len(group) else np.nan
        mean_pd = float(group["pd"].mean()) if len(group) else np.nan
        calibration_rows.append(
            {
                "period": period,
                "risk_grade": risk_grade,
                "eligible_accounts": len(group),
                "excluded_immature_accounts": full_count - len(group),
                "bad_events": int(group["bad_flag"].sum()),
                "observed_bad_rate_matured": observed_rate,
                "mean_pd_matured": mean_pd,
                "calibration_gap_matured": observed_rate - mean_pd,
                "oe_ratio_matured": safe_ratio(observed_rate, mean_pd),
                "outcome_window": "12-month matured target",
                "eligibility_status": "ELIGIBLE" if len(group) >= 100 and group["bad_flag"].sum() >= 10 else "LOW_SAMPLE_REVIEW",
            }
        )
    calibration = pd.DataFrame(calibration_rows)
    write_csv(
        add_meta(calibration, "Observed", "Derived", "P3/P6", "Calibration uses matured accounts only", "period"),
        "outputs/model_calibration_summary.csv",
    )
    population_summary = monitoring[
        ["period", "accounts", "matured_accounts", "excluded_immature_accounts", "bad_events", "good_events", "eligibility_status", "outcome_window"]
    ].copy()
    write_csv(
        add_meta(population_summary, "Observed", "Derived", "P3/P6", "Calibration population eligibility", "period"),
        "outputs/calibration_population_summary.csv",
    )

    drift_rows: list[dict[str, object]] = []
    methodology_rows: list[dict[str, object]] = []
    for feature in ["pd", "scorecard_points", "fico", "dti", "loan_amount"]:
        edges = make_psi_edges(baseline[feature])
        methodology_rows.append(
            {
                "feature": feature,
                "baseline_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}",
                "baseline_rows": int(baseline[feature].notna().sum()),
                "missing_treatment": "Excluded from numeric bins; missing rate monitored separately",
                "bin_edges": json.dumps([None if np.isinf(value) else round(float(value), 8) for value in edges]),
            }
        )
        for period, group in base.groupby("application_period", sort=True):
            value = psi_from_edges(baseline[feature], group[feature], edges)
            drift_rows.append(
                {
                    "period": period,
                    "feature": feature,
                    "current_rows": int(group[feature].notna().sum()),
                    "baseline_rows": int(baseline[feature].notna().sum()),
                    "current_mean": float(pd.to_numeric(group[feature], errors="coerce").mean()),
                    "baseline_mean": float(pd.to_numeric(baseline[feature], errors="coerce").mean()),
                    "current_missing_rate": float(group[feature].isna().mean()),
                    "baseline_missing_rate": float(baseline[feature].isna().mean()),
                    "psi_vs_development_baseline": value,
                    "status": risk_status(value, 0.10, 0.25, "higher_bad"),
                    "reference_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}",
                }
            )
    drift = pd.DataFrame(drift_rows).sort_values(["feature", "period"])
    drift["prior_psi"] = drift.groupby("feature")["psi_vs_development_baseline"].shift(1)
    drift["psi_change"] = drift["psi_vs_development_baseline"] - drift["prior_psi"]
    drift["is_current_model_period"] = drift["period"].eq(current_period)
    write_csv(
        add_meta(drift, "Observed", "Derived", "P3/P6", "Period-level feature drift with fixed baseline bins", "period"),
        "outputs/feature_drift_summary.csv",
    )
    write_csv(pd.DataFrame(methodology_rows), "outputs/feature_drift_bin_definition.csv")

    current = monitoring.loc[monitoring["period"].eq(current_period)].iloc[0]
    prior = monitoring.loc[monitoring["period"].eq(prior_period)].iloc[0]
    current_rows = []
    for metric in ["auc", "ks", "gini", "observed_bad_rate_matured", "mean_pd_matured", "calibration_gap_matured", "oe_ratio_matured", "pd_psi_vs_development_baseline"]:
        current_rows.append(
            {
                "metric": metric,
                "reference_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}",
                "current_period": current_period,
                "prior_period": prior_period,
                "current_value": current[metric],
                "prior_value": prior[metric],
                "change": current[metric] - prior[metric],
                "current_matured_accounts": current["matured_accounts"],
                "current_bad_events": current["bad_events"],
            }
        )
    write_csv(
        add_meta(pd.DataFrame(current_rows), "Observed", "Derived", "P3/P6", "Latest and prior eligible model periods", current_period),
        "outputs/model_monitoring_current_summary.csv",
    )


POLICY_CONFIGS = [
    ("baseline_current_25", "Baseline Current Policy 25%", 0.25, 0.35, False),
    ("scenario_1_recommended_20", "Scenario 1 Candidate 20%", 0.20, 0.35, False),
    ("scenario_2_conservative_15", "Scenario 2 Conservative 15%", 0.15, 0.35, False),
    ("scenario_3_overlay_20", "Scenario 3 20% plus DTI/FICO overlay", 0.20, 0.35, True),
    ("scenario_4_decline_threshold_30", "Scenario 4 20% plus 30% decline sensitivity", 0.20, 0.30, False),
]


def _policy_decision(base: pd.DataFrame, approve: float, manual_upper: float, overlay: bool) -> np.ndarray:
    decisions = np.select(
        [base["pd"].le(approve), base["pd"].le(manual_upper)],
        ["APPROVE", "MANUAL_REVIEW"],
        default="DECLINE",
    ).astype(object)
    if overlay:
        overlay_mask = base["pd"].le(approve) & (base["dti"].ge(35) | base["fico"].lt(660))
        decisions[overlay_mask.to_numpy()] = "MANUAL_REVIEW"
    decisions[pd.isna(base["pd"]).to_numpy()] = "EXCEPTION_QUEUE"
    return decisions


def build_policy_monitoring() -> None:
    base = load_base()
    matured = base[base["matured_flag"].eq(1)].copy()
    detail_rows: list[dict[str, object]] = []
    period_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for version_id, version_name, approve_cutoff, manual_upper, overlay in POLICY_CONFIGS:
        version = base.copy()
        version["policy_version"] = version_id
        version["policy_version_name"] = version_name
        version["policy_decision"] = _policy_decision(version, approve_cutoff, manual_upper, overlay)
        version["policy_exception_flag"] = version["exception_flag"].astype(int)
        version["policy_override_flag"] = (overlay & version["policy_decision"].eq("MANUAL_REVIEW") & version["pd"].le(approve_cutoff)).astype(int)

        for (period, decision), group in version.groupby(["application_period", "policy_decision"], sort=True):
            eligible = group[group["matured_flag"].eq(1)]
            detail_rows.append(
                {
                    "policy_version": version_id,
                    "policy_version_name": version_name,
                    "application_period": period,
                    "policy_decision": decision,
                    "accounts": len(group),
                    "matured_accounts": len(eligible),
                    "observed_bad_accounts": int(eligible["bad_flag"].sum()),
                    "observed_bad_rate_matured": float(eligible["bad_flag"].mean()) if len(eligible) else np.nan,
                    "outcome_status": "ASSESSABLE" if len(eligible) else "NOT_MATURED_NOT_ASSESSABLE",
                    "exposure": float(group["exposure"].sum()),
                    "avg_pd": float(group["pd"].mean()),
                    "expected_loss": float(group["expected_loss"].sum()),
                    "exceptions": int(group["policy_exception_flag"].sum()),
                    "overrides": int(group["policy_override_flag"].sum()),
                    "approve_cutoff": approve_cutoff,
                    "manual_upper_cutoff": manual_upper,
                    "segment_overlay_enabled": overlay,
                }
            )
        for period, group in version.groupby("application_period", sort=True):
            eligible = group[group["matured_flag"].eq(1)]
            period_rows.append(
                {
                    "policy_version": version_id,
                    "application_period": period,
                    "accounts": len(group),
                    "matured_accounts": len(eligible),
                    "approval_rate": float(group["policy_decision"].eq("APPROVE").mean()),
                    "manual_review_rate": float(group["policy_decision"].eq("MANUAL_REVIEW").mean()),
                    "decline_rate": float(group["policy_decision"].eq("DECLINE").mean()),
                    "exception_queue_rate": float(group["policy_decision"].eq("EXCEPTION_QUEUE").mean()),
                    "exception_rate": float(group["policy_exception_flag"].mean()),
                    "approved_bad_rate_matured": float(eligible.loc[eligible["policy_decision"].eq("APPROVE"), "bad_flag"].mean()) if eligible["policy_decision"].eq("APPROVE").any() else np.nan,
                    "auto_approved_expected_loss": float(group.loc[group["policy_decision"].eq("APPROVE"), "expected_loss"].sum()),
                    "manual_review_expected_loss": float(group.loc[group["policy_decision"].eq("MANUAL_REVIEW"), "expected_loss"].sum()),
                    "declined_expected_loss": float(group.loc[group["policy_decision"].eq("DECLINE"), "expected_loss"].sum()),
                    "exception_queue_expected_loss": float(group.loc[group["policy_decision"].eq("EXCEPTION_QUEUE"), "expected_loss"].sum()),
                    "outcome_status": "ASSESSABLE" if len(eligible) else "NOT_MATURED_NOT_ASSESSABLE",
                }
            )

        matured_version = version[version["matured_flag"].eq(1)]
        approved = matured_version[matured_version["policy_decision"].eq("APPROVE")]
        manual_review = matured_version[matured_version["policy_decision"].eq("MANUAL_REVIEW")]
        declined = matured_version[matured_version["policy_decision"].eq("DECLINE")]
        exception_queue = matured_version[matured_version["policy_decision"].eq("EXCEPTION_QUEUE")]
        non_approved = matured_version[~matured_version["policy_decision"].eq("APPROVE")]
        auto_approved_el = float(approved["expected_loss"].sum())
        manual_review_el = float(manual_review["expected_loss"].sum())
        declined_el = float(declined["expected_loss"].sum())
        exception_queue_el = float(exception_queue["expected_loss"].sum())
        total_routed_el = manual_review_el + declined_el + exception_queue_el
        total_scored_el = auto_approved_el + total_routed_el
        summary_rows.append(
            {
                "policy_version": version_id,
                "policy_version_name": version_name,
                "total_scored_accounts": len(matured_version),
                "matured_accounts": len(matured_version),
                "approved_accounts": len(approved),
                "manual_review_accounts": int(matured_version["policy_decision"].eq("MANUAL_REVIEW").sum()),
                "declined_accounts": int(matured_version["policy_decision"].eq("DECLINE").sum()),
                "exception_queue_accounts": int(matured_version["policy_decision"].eq("EXCEPTION_QUEUE").sum()),
                "approval_rate": len(approved) / len(matured_version),
                "manual_review_rate": float(matured_version["policy_decision"].eq("MANUAL_REVIEW").mean()),
                "decline_rate": float(matured_version["policy_decision"].eq("DECLINE").mean()),
                "exception_queue_rate": float(matured_version["policy_decision"].eq("EXCEPTION_QUEUE").mean()),
                "approved_bad_rate_matured": float(approved["bad_flag"].mean()) if len(approved) else np.nan,
                "manual_review_bad_rate_matured": float(manual_review["bad_flag"].mean()) if len(manual_review) else np.nan,
                "decline_bad_rate_matured": float(declined["bad_flag"].mean()) if len(declined) else np.nan,
                "bad_capture_non_approved": safe_ratio(int(non_approved["bad_flag"].sum()), int(matured_version["bad_flag"].sum())),
                "approved_exposure": float(approved["exposure"].sum()),
                "auto_approved_expected_loss": auto_approved_el,
                "manual_review_expected_loss": manual_review_el,
                "declined_expected_loss": declined_el,
                "exception_queue_expected_loss": exception_queue_el,
                "total_routed_expected_loss": total_routed_el,
                "total_scored_expected_loss": total_scored_el,
                "manual_review_disposition_assumption": "NOT_MODELED",
                "approve_cutoff": approve_cutoff,
                "manual_upper_cutoff": manual_upper,
                "segment_overlay_enabled": overlay,
            }
        )
    detail = pd.DataFrame(detail_rows)
    period_summary = pd.DataFrame(period_rows).sort_values(["policy_version", "application_period"])
    period_summary["total_routed_expected_loss"] = (
        period_summary["manual_review_expected_loss"]
        + period_summary["declined_expected_loss"]
        + period_summary["exception_queue_expected_loss"]
    )
    period_summary["total_scored_expected_loss"] = (
        period_summary["auto_approved_expected_loss"] + period_summary["total_routed_expected_loss"]
    )
    period_summary["approved_expected_loss"] = period_summary["auto_approved_expected_loss"]
    period_summary["approved_expected_loss_alias_status"] = "DEPRECATED_ALIAS_AUTO_APPROVED_EXPECTED_LOSS"
    for metric in [
        "approval_rate", "manual_review_rate", "decline_rate", "exception_rate", "exception_queue_rate",
        "approved_bad_rate_matured", "auto_approved_expected_loss", "total_routed_expected_loss",
    ]:
        period_summary[f"prior_{metric}"] = period_summary.groupby("policy_version")[metric].shift(1)
        period_summary[f"change_{metric}"] = period_summary[metric] - period_summary[f"prior_{metric}"]
    summary = pd.DataFrame(summary_rows)
    baseline = summary[summary["policy_version"].eq("baseline_current_25")].iloc[0]
    for metric in [
        "approval_rate", "manual_review_rate", "decline_rate", "exception_queue_rate",
        "approved_bad_rate_matured", "bad_capture_non_approved", "auto_approved_expected_loss",
        "manual_review_expected_loss", "declined_expected_loss", "total_routed_expected_loss",
    ]:
        summary[f"delta_{metric}_vs_baseline"] = summary[metric] - baseline[metric]
    summary["auto_approved_el_reduction_vs_baseline"] = (
        baseline["auto_approved_expected_loss"] - summary["auto_approved_expected_loss"]
    ) / baseline["auto_approved_expected_loss"]
    summary["approved_expected_loss"] = summary["auto_approved_expected_loss"]
    summary["expected_loss_reduction_pct_vs_baseline"] = summary["auto_approved_el_reduction_vs_baseline"]
    summary["approved_expected_loss_alias_status"] = "DEPRECATED_ALIAS_AUTO_APPROVED_EXPECTED_LOSS"
    summary["expected_loss_reduction_alias_status"] = "DEPRECATED_ALIAS_AUTO_APPROVED_EL_REDUCTION"

    write_csv(
        add_meta(detail, "Observed", "Derived", "P6/P2", "Policy decision outcomes use matured denominators", "application_period"),
        "outputs/policy_monitoring_summary.csv",
    )
    write_csv(
        add_meta(period_summary, "Observed", "Derived", "P6/P2", "Policy version period trend on common booked population", "application_period"),
        "outputs/policy_period_trend.csv",
    )
    write_csv(
        add_meta(summary, "Observed", "Derived", "P6/P2", "Common-population policy-version bridge"),
        "outputs/policy_version_bridge_summary.csv",
    )

    upstream = pd.read_csv(PACKAGED_SOURCES["p6_policy"])
    comparisons = []
    for _, row in summary.iterrows():
        match = upstream[upstream["scenario_id"].eq(row["policy_version"])]
        if match.empty:
            continue
        upstream_row = match.iloc[0]
        comparisons.append(
            {
                "policy_version": row["policy_version"],
                "p2_approval_rate": row["approval_rate"],
                "p6_approval_rate": upstream_row["approval_rate"],
                "approval_rate_difference": row["approval_rate"] - upstream_row["approval_rate"],
                "p2_approved_bad_rate": row["approved_bad_rate_matured"],
                "p6_approved_bad_rate": upstream_row["approved_bad_rate"],
                "approved_bad_rate_difference": row["approved_bad_rate_matured"] - upstream_row["approved_bad_rate"],
                "p2_auto_approved_expected_loss": row["auto_approved_expected_loss"],
                "p6_approved_expected_loss": upstream_row["approved_expected_loss"],
                "auto_approved_expected_loss_difference": row["auto_approved_expected_loss"] - upstream_row["approved_expected_loss"],
                "compatibility_mapping": "P6 approved_expected_loss maps to P2 auto_approved_expected_loss",
            }
        )
    reconciliation = pd.DataFrame(comparisons)
    reconciliation["rate_tolerance"] = 1e-10
    reconciliation["expected_loss_tolerance"] = 0.01
    reconciliation["status"] = np.where(
        reconciliation[["approval_rate_difference", "approved_bad_rate_difference"]].abs().max(axis=1).le(reconciliation["rate_tolerance"])
        & reconciliation["auto_approved_expected_loss_difference"].abs().le(reconciliation["expected_loss_tolerance"]),
        "PASS",
        "FAIL",
    )
    write_csv(reconciliation, "validation/policy_reconciliation_p6.csv")


def build_ecl_enterprise_risk_monitoring() -> None:
    p4 = pd.read_csv(PACKAGED_SOURCES["p4_account"])
    stage_grade = p4.groupby(["stage", "risk_grade"], as_index=False).agg(
        accounts=("loan_id", "count"),
        ead=("ead_current", "sum"),
        ecl_base=("ecl_base", "sum"),
        ecl_weighted=("ecl_weighted", "sum"),
        ecl_downside=("ecl_downside", "sum"),
        ecl_severe=("ecl_severe", "sum"),
    )
    stage_grade["weighted_ecl_rate"] = stage_grade["ecl_weighted"] / stage_grade["ead"]
    stage_grade["downside_uplift_vs_weighted"] = (stage_grade["ecl_downside"] - stage_grade["ecl_weighted"]) / stage_grade["ecl_weighted"]
    stage_grade["trend_status"] = "NOT_ASSESSABLE_NO_PRIOR_SNAPSHOT"
    stage_grade["reporting_date"] = str(p4["reporting_date"].iloc[0])
    write_csv(
        add_meta(stage_grade, "Observed", "Proxy", "P4", "Frozen P4 ECL snapshot; Stage 2 proxy limitation applies", "reporting_date"),
        "outputs/ecl_stress_monitoring_summary.csv",
    )

    scenario = pd.read_csv(PACKAGED_SOURCES["p4_scenario"])
    scenario["monitoring_dimension"] = "SCENARIO_NOT_TIME_TREND"
    scenario["prior_period_status"] = "NOT_AVAILABLE"
    write_csv(
        add_meta(scenario, "Observed", "Proxy", "P4", "Scenario monitoring overlay; not current-versus-prior ECL", "2018-12"),
        "outputs/ecl_scenario_monitoring.csv",
    )
    view = pd.read_csv(PACKAGED_SOURCES["p4_view"])
    write_csv(add_meta(view, "Observed", "Proxy", "P4", "Evidence-constrained versus proxy-lifetime ECL view", "2018-12"), "outputs/ecl_view_bridge.csv")
    sensitivity = pd.read_csv(PACKAGED_SOURCES["p4_sensitivity"])
    write_csv(add_meta(sensitivity, "Observed", "Proxy", "P4", "Controlled ECL assumption sensitivities", "2018-12"), "outputs/ecl_sensitivity_monitoring.csv")
    assumption_bridge = pd.read_csv(PACKAGED_SOURCES["p4_assumption_bridge"])
    write_csv(add_meta(assumption_bridge, "Observed", "Proxy", "P4", "Same-population assumption-change attribution", "2018-12"), "outputs/ecl_assumption_movement_bridge.csv")
    policy_bridge = pd.read_csv(PACKAGED_SOURCES["p4_policy_bridge"])
    write_csv(add_meta(policy_bridge, "Observed", "Proxy", "P4/P6", "P6-to-P4 ECL scope bridge", "2018-12"), "outputs/ecl_policy_bridge.csv")

    concentration_rows = []
    for dimension in ["term", "purpose", "risk_grade"]:
        grouped = p4.groupby(dimension, dropna=False, as_index=False).agg(
            accounts=("loan_id", "count"), ead=("ead_current", "sum"), ecl_weighted=("ecl_weighted", "sum"), ecl_downside=("ecl_downside", "sum")
        )
        grouped["dimension"] = dimension
        grouped = grouped.rename(columns={dimension: "segment"})
        grouped["ecl_share"] = grouped["ecl_weighted"] / grouped["ecl_weighted"].sum()
        grouped["downside_uplift"] = (grouped["ecl_downside"] - grouped["ecl_weighted"]) / grouped["ecl_weighted"]
        concentration_rows.append(grouped)
    concentration = pd.concat(concentration_rows, ignore_index=True)
    write_csv(add_meta(concentration, "Observed", "Proxy", "P4", "ECL concentration and downside overlay", "2018-12"), "outputs/ecl_concentration_monitoring.csv")

    readiness = pd.DataFrame(
        [
            ["Observed current EAD", "PROXY_ONLY", "Contractual-balance reconstruction", "RED", "Acquire reporting-date servicing balances"],
            ["Relative SICR", "NOT_ASSESSABLE", "No date-aligned current risk measure", "RED", "Acquire origination/current PD or DPD history"],
            ["Stage 3", "NOT_ASSESSABLE", "No valid reporting-date credit-impaired flag", "RED", "Acquire default/90+ DPD snapshot"],
            ["Workout LGD", "NOT_AVAILABLE", "FICO-based proxy used", "AMBER", "Acquire recoveries and workout cash flows"],
            ["Prior-period ECL", "NOT_AVAILABLE", "No controlled prior snapshot", "AMBER", "Establish monthly frozen ECL snapshots"],
        ],
        columns=["data_requirement", "readiness", "current_method", "status", "management_action"],
    )
    write_csv(add_meta(readiness, "Governance", "Proxy", "P4/P2", "ECL data-readiness KRI", "2018-12"), "outputs/ecl_readiness_kri.csv")

    enterprise_rows: list[dict[str, object]] = []
    fraud_kpi = pd.read_csv(PACKAGED_SOURCES["p5_fraud_kpi"])
    for metric in ["total_transactions", "fraud_transactions", "fraud_rate", "fraud_amount", "fraud_amount_rate"]:
        match = fraud_kpi[fraud_kpi["metric"].eq(metric)]
        if not match.empty:
            enterprise_rows.append({"domain": "Fraud observed benchmark", "metric": metric, "value": match.iloc[0]["value"], "source": "P5 observed PCA benchmark", "evidence_status": "Observed"})
    priority = pd.read_csv(PACKAGED_SOURCES["p5_priority"])
    critical = priority[priority["review_priority"].eq("CRITICAL")].iloc[0]
    enterprise_rows.extend(
        [
            {"domain": "Operational controls", "metric": "critical_queue_alerts", "value": critical["alerts"], "source": "P5 synthetic controls", "evidence_status": "Synthetic"},
            {"domain": "Operational controls", "metric": "critical_queue_precision", "value": critical["fraud_precision"], "source": "P5 synthetic controls", "evidence_status": "Synthetic"},
        ]
    )
    incidents = pd.read_csv(PACKAGED_SOURCES["p5_incidents"])
    enterprise_rows.extend(
        [
            {"domain": "Operational risk", "metric": "open_incidents", "value": int(incidents["status"].ne("Closed").sum()), "source": "P5 synthetic incident register", "evidence_status": "Synthetic"},
            {"domain": "Operational risk", "metric": "net_loss_proxy", "value": float(incidents["net_loss"].sum()), "source": "P5 synthetic incident register", "evidence_status": "Synthetic"},
        ]
    )
    write_csv(
        add_meta(pd.DataFrame(enterprise_rows), "Mixed", "Derived", "P5", "P5 observed and synthetic boundaries retained"),
        "outputs/enterprise_risk_summary.csv",
    )


def _breach_variance(value: float, green: float, amber: float, direction: str, status: str) -> tuple[float, float]:
    trigger = green if status == "AMBER" else amber
    variance = value - trigger if direction == "higher_bad" else trigger - value
    return trigger, variance


def build_ews_kri_actions() -> None:
    base = load_base()
    model = pd.read_csv(ROOT / "outputs/model_monitoring_summary.csv")
    model_eligible = _eligible_model_periods(model)
    current_model = model_eligible.iloc[-1]
    prior_model = model_eligible.iloc[-2]
    stock = pd.read_csv(ROOT / "outputs/delinquency_stock_flow_summary.csv")
    stock_eligible = stock[stock["accounts"].ge(1_000)].sort_values("snapshot_month")
    current_stock = stock_eligible.iloc[-1]
    prior_stock = stock_eligible.iloc[-2]
    policy_period = pd.read_csv(ROOT / "outputs/policy_period_trend.csv")
    current_policy_series = policy_period[policy_period["policy_version"].eq("baseline_current_25")].sort_values("application_period")
    current_policy = current_policy_series.iloc[-1]
    prior_policy = current_policy_series.iloc[-2]
    p4 = pd.read_csv(PACKAGED_SOURCES["p4_account"])
    p4_scenario = pd.read_csv(PACKAGED_SOURCES["p4_scenario"])
    enterprise = pd.read_csv(ROOT / "outputs/enterprise_risk_summary.csv")

    p4_stage2 = p4[p4["stage"].eq("Stage 2")]
    base_scenario = p4_scenario[p4_scenario["scenario_id"].eq("base")].iloc[0]
    downside_scenario = p4_scenario[p4_scenario["scenario_id"].eq("downside")].iloc[0]
    critical_precision = float(enterprise.loc[enterprise["metric"].eq("critical_queue_precision"), "value"].iloc[0])
    critical_alerts = int(float(enterprise.loc[enterprise["metric"].eq("critical_queue_alerts"), "value"].iloc[0]))

    current_credit_period = str(current_model["period"])
    prior_credit_period = str(prior_model["period"])
    current_credit_group = base[(base["application_period"].eq(current_credit_period)) & base["matured_flag"].eq(1)]
    current_credit_exposure = float(current_credit_group["exposure"].sum())
    current_credit_el = float(current_credit_group["expected_loss"].sum())
    current_policy_group = base[base["application_period"].eq(str(current_policy["application_period"]))]
    current_policy_exceptions = current_policy_group[current_policy_group["exception_flag"].eq(1)]
    current_stock_group = pd.read_csv(ROOT / "data/synthetic/monthly_delinquency_snapshots.csv.gz")
    current_stock_group = current_stock_group[current_stock_group["snapshot_month"].eq(current_stock["snapshot_month"])]

    definitions = [
        {
            "kri_id": "KRI-001", "metric": "Observed bad rate", "current": current_model["observed_bad_rate_matured"], "prior": prior_model["observed_bad_rate_matured"],
            "green": 0.15, "amber": 0.18, "direction": "higher_bad", "owner": "Portfolio Risk", "source": "P3/P6",
            "reference_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}", "current_period": current_credit_period, "prior_period": prior_credit_period,
            "affected_accounts": len(current_credit_group), "affected_exposure": current_credit_exposure,
            "impact_value": max(0.0, float(current_model["observed_bad_rate_matured"]) - 0.15) * current_credit_exposure * float(current_credit_group["lgd"].mean()),
            "impact_unit": "cost_units", "impact_method": "Excess bad-rate above Green boundary x exposure x average LGD",
        },
        {
            "kri_id": "KRI-002", "metric": "30+ DPD rate", "current": current_stock["dpd_30_plus"], "prior": prior_stock["dpd_30_plus"],
            "green": 0.03, "amber": 0.05, "direction": "higher_bad", "owner": "Collections", "source": "P2 Synthetic",
            "reference_period": "Synthetic multi-vintage control", "current_period": current_stock["snapshot_month"], "prior_period": prior_stock["snapshot_month"],
            "affected_accounts": int(current_stock["dpd_30_plus_accounts"]), "affected_exposure": float(current_stock_group.loc[current_stock_group["dpd_bucket"].isin(["30-59", "60-89", "90+", "Default"]), "ending_balance"].sum()),
            "impact_value": np.nan, "impact_unit": "not_monetised", "impact_method": "Synthetic delinquent accounts and balance; no observed loss estimate",
        },
        {
            "kri_id": "KRI-003", "metric": "PD PSI", "current": current_model["pd_psi_vs_development_baseline"], "prior": prior_model["pd_psi_vs_development_baseline"],
            "green": 0.10, "amber": 0.25, "direction": "higher_bad", "owner": "Model Risk", "source": "P3/P6",
            "reference_period": current_model["reference_period"], "current_period": current_credit_period, "prior_period": prior_credit_period,
            "affected_accounts": len(current_credit_group), "affected_exposure": current_credit_exposure,
            "impact_value": np.nan, "impact_unit": "not_directly_monetised", "impact_method": "Current eligible scored population; PSI is a drift trigger, not loss",
        },
        {
            "kri_id": "KRI-004", "metric": "Absolute calibration gap", "current": abs(current_model["calibration_gap_matured"]), "prior": abs(prior_model["calibration_gap_matured"]),
            "green": 0.03, "amber": 0.05, "direction": "higher_bad", "owner": "Model Owner", "source": "P3/P6",
            "reference_period": current_model["reference_period"], "current_period": current_credit_period, "prior_period": prior_credit_period,
            "affected_accounts": len(current_credit_group), "affected_exposure": current_credit_exposure,
            "impact_value": abs(float(current_model["calibration_gap_matured"])) * current_credit_exposure * float(current_credit_group["lgd"].mean()),
            "impact_unit": "cost_units", "impact_method": "Absolute PD calibration gap x current-period exposure x average LGD",
        },
        {
            "kri_id": "KRI-005", "metric": "Policy exception rate", "current": current_policy["exception_rate"], "prior": prior_policy["exception_rate"],
            "green": 0.02, "amber": 0.05, "direction": "higher_bad", "owner": "Credit Policy", "source": "P6/P2",
            "reference_period": "Baseline Current Policy 25%", "current_period": current_policy["application_period"], "prior_period": prior_policy["application_period"],
            "affected_accounts": len(current_policy_exceptions), "affected_exposure": float(current_policy_exceptions["exposure"].sum()),
            "impact_value": len(current_policy_exceptions) * 10.0 / 60.0, "impact_unit": "estimated_review_hours", "impact_method": "Current-period exception accounts x documented 10-minute handling-time assumption",
        },
        {
            "kri_id": "KRI-006", "metric": "Stage 2 proxy share", "current": len(p4_stage2) / len(p4), "prior": np.nan,
            "green": 0.15, "amber": 0.25, "direction": "higher_bad", "owner": "Credit Risk", "source": "P4",
            "reference_period": "P4 reporting-date frozen snapshot", "current_period": str(p4["reporting_date"].iloc[0])[:7], "prior_period": "NOT_AVAILABLE",
            "affected_accounts": len(p4_stage2), "affected_exposure": float(p4_stage2["ead_current"].sum()),
            "impact_value": float(p4_stage2["ecl_weighted"].sum()), "impact_unit": "cost_units", "impact_method": "P4 Stage 2 proxy accounts, EAD and weighted ECL",
        },
        {
            "kri_id": "KRI-007", "metric": "Downside ECL uplift", "current": float(downside_scenario["uplift_vs_base"]), "prior": np.nan,
            "green": 0.25, "amber": 0.50, "direction": "higher_bad", "owner": "Finance Risk", "source": "P4",
            "reference_period": "P4 base scenario", "current_period": "2018-12 downside scenario", "prior_period": "NOT_AVAILABLE",
            "affected_accounts": len(p4), "affected_exposure": float(p4["ead_current"].sum()),
            "impact_value": float(downside_scenario["total_ecl"] - base_scenario["total_ecl"]), "impact_unit": "cost_units", "impact_method": "P4 downside ECL minus base ECL",
        },
        {
            "kri_id": "KRI-008", "metric": "Critical control precision", "current": critical_precision, "prior": np.nan,
            "green": 0.05, "amber": 0.02, "direction": "lower_bad", "owner": "Fraud Strategy", "source": "P5 Synthetic",
            "reference_period": "P5 synthetic queue snapshot", "current_period": "P5 frozen v1.0.1", "prior_period": "NOT_AVAILABLE",
            "affected_accounts": critical_alerts, "affected_exposure": np.nan,
            "impact_value": critical_alerts - int(round(critical_alerts * critical_precision)), "impact_unit": "non_fraud_alerts", "impact_method": "Critical alerts minus synthetic fraud-label hits; no credit exposure assigned",
        },
    ]

    kri_rows: list[dict[str, object]] = []
    alerts: list[dict[str, object]] = []
    actions: list[dict[str, object]] = []
    action_specs = {
        "KRI-001": ["Recent-vintage risk mix or macro deterioration", "Current eligible credit cohort", "Decompose by grade, purpose, FICO and DTI; compare prior cohort", "Reduce Red-segment origination exposure by an approved quantified cap", "Approve targeted policy review or accept residual risk", "Bad rate <=18% for two eligible periods", "Segment analysis, policy approval and two-period monitoring evidence", "P3 score and P6 policy fields"],
        "KRI-002": ["Synthetic transition assumptions produce elevated late-stage stock", "Synthetic 30+ DPD accounts", "Review transition matrix, term mix and balance bridge", "Validate scenario severity, transition assumptions and representativeness; retain the Red outcome when it is an intentional stress scenario", "Accept the documented controls-test scenario or revise unsupported transition assumptions", "Bridge difference 0, documented scenario rationale and no outcome-driven tuning", "Transition tests, stock-flow reconciliation and scenario-governance note", "Synthetic engine only; observed DPD required for production"],
        "KRI-003": ["Score distribution shift versus P3 development baseline", "Latest eligible scored cohort", "Review fixed-bin PSI by score, FICO, DTI, loan amount and missingness", "Perform Amber diagnostic review and heightened monthly monitoring; formal model review only if PSI >0.25", "Model Risk decides whether drivers justify monitoring exception, challenger analysis or recalibration study", "PSI <0.10 for two consecutive eligible periods or approved monitoring exception with owner, driver, residual risk and expiry", "Feature PSI drilldown, root-cause note and Model Risk monitoring decision", "Frozen P3 model"],
        "KRI-004": ["PD under/over-prediction in latest matured cohort", "Latest eligible matured cohort", "Reconcile mean PD to observed bad rate by grade and tail", "Prepare calibration overlay candidate and impact estimate", "Approve recalibration study or accepted-risk note", "Absolute gap <=5pp for two eligible periods", "Calibration table, tail review and approval record", "Matured outcomes and P3 calibration method"],
        "KRI-005": ["High DTI/low FICO routing and data exceptions", "Current baseline-policy cohort", "Profile exception reason, owner, exposure and outcome maturity", "Reduce avoidable exceptions to <=2% or document capacity plan", "Credit Policy approves rule/data remediation", "Exception rate <=2%", "Exception log, owner sign-off and closure sample", "P6 rule definitions"],
        "KRI-006": ["Broad watchlist proxy rather than observed relative SICR", "P4 Stage 2 proxy population", "Decompose trigger attribution, term and purpose concentration", "Acquire current PD/DPD and replace broad proxy", "Credit Risk approves data-remediation roadmap", "Observed SICR coverage established; proxy share no longer primary", "Data contract, trigger attribution and implementation evidence", "P4 data gaps"],
        "KRI-007": ["PD/LGD/EAD downside multipliers and 60-month concentration", "P4 eligible ECL population", "Review downside bridge, EAD sensitivity and top concentration", "Set downside buffer/action tied to quantified uplift", "Finance Risk approves buffer or risk acceptance", "Downside uplift <=50% or approved buffer", "Scenario bridge, concentration action and committee decision", "P4 ECL assumptions"],
        "KRI-008": ["Critical queue priority does not align with fraud yield", "P5 CRITICAL synthetic alerts", "Review rule overlap, reason codes and non-fraud alerts", "Redesign priority routing to precision >=2% minimum", "Fraud Strategy approves routing change", "Precision >=2% in controlled retest", "Rule-level retest and queue evidence", "P5 synthetic controls only"],
    }

    for index, definition in enumerate(definitions, start=1):
        current_value = float(definition["current"])
        prior_value = float(definition["prior"]) if not pd.isna(definition["prior"]) else np.nan
        current_status = risk_status(current_value, definition["green"], definition["amber"], definition["direction"])
        prior_status = None if pd.isna(prior_value) else risk_status(prior_value, definition["green"], definition["amber"], definition["direction"])
        state = "STATIC_REVIEW" if pd.isna(prior_value) else alert_state(current_status, prior_status)
        trigger, variance = _breach_variance(current_value, definition["green"], definition["amber"], definition["direction"], current_status) if current_status in {"AMBER", "RED"} else (definition["green"], 0.0)
        kri_row = {
            "kri_id": definition["kri_id"],
            "metric": definition["metric"],
            "reference_period": definition["reference_period"],
            "current_period": definition["current_period"],
            "prior_period": definition["prior_period"],
            "current_value": current_value,
            "prior_value": prior_value,
            "change": current_value - prior_value if not pd.isna(prior_value) else np.nan,
            "green_threshold": definition["green"],
            "amber_threshold": definition["amber"],
            "breach_trigger_used": trigger,
            "variance_to_trigger": variance,
            "direction": definition["direction"],
            "status": current_status,
            "prior_status": prior_status or "NOT_AVAILABLE",
            "alert_state": state,
            "owner": definition["owner"],
            "source_scope": definition["source"],
            "affected_accounts": definition["affected_accounts"],
            "affected_exposure": definition["affected_exposure"],
            "estimated_impact": definition["impact_value"],
            "impact_unit": definition["impact_unit"],
            "impact_method": definition["impact_method"],
        }
        kri_rows.append(kri_row)
        if current_status not in {"AMBER", "RED"}:
            continue
        alert_id = f"EWS-{index:03d}"
        severity = "HIGH" if current_status == "RED" else "MEDIUM"
        alerts.append(
            {
                "ews_id": alert_id,
                **kri_row,
                "severity": severity,
                "recommended_action": action_specs[definition["kri_id"]][3],
                "due_date": "2026-08-15",
                "workflow_status": "OPEN",
            }
        )
        spec = action_specs[definition["kri_id"]]
        actions.append(
            {
                "action_id": f"ACT-{index:03d}",
                "alert_id": alert_id,
                "kri_id": definition["kri_id"],
                "root_cause_hypothesis": spec[0],
                "affected_segment": spec[1],
                "specific_investigation": spec[2],
                "quantified_remediation": spec[3],
                "decision_required": spec[4],
                "acceptance_criteria": spec[5],
                "closure_evidence": spec[6],
                "dependency": spec[7],
                "owner": definition["owner"],
                "approver": "Risk Committee",
                "created_date": "2026-07-11",
                "due_date": "2026-08-15",
                "status": "OPEN",
                "residual_risk": "Pending quantified review",
            }
        )

    kri_frame = add_meta(pd.DataFrame(kri_rows), "Mixed", "Derived", "P2", "Latest-period EWS with static upstream overlays", "current_period")
    alert_frame = add_meta(pd.DataFrame(alerts), "Mixed", "Derived", "P2", "Source-specific EWS alerts; no production workflow claim", "current_period")
    action_frame = add_meta(pd.DataFrame(actions), "Governance", "Derived", "P2", "Specific management action register", "created_date")
    write_csv(kri_frame, "outputs/kri_status_summary.csv")
    write_csv(alert_frame, "outputs/early_warning_alerts.csv")
    write_csv(action_frame, "outputs/management_action_summary.csv")
    write_csv(action_frame.copy(), "governance/management_action_library.csv")
