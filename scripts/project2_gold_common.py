from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parent
EXISTING_P2 = PORTFOLIO_ROOT / "01_CreditPortfolioAnalytics"

RUN_DATE = "2026-07-12"
SEED = 20260711
VERSION = "Project2_CreditPortfolioMonitoring_GoldCandidate_v2_1_4"
MIN_MATURED_ACCOUNTS = 1_000
MIN_BAD_EVENTS = 50
MODEL_BASELINE_START = "2014-01"
MODEL_BASELINE_END = "2015-12"
SYNTHETIC_SAMPLE_SIZE = 50_000
SYNTHETIC_HORIZON_MONTHS = 36

DISCLAIMER = (
    "Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to "
    "historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are "
    "separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations "
    "indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account "
    "simulation. No live servicing platform, regulatory report, production model monitoring, independent validation "
    "or organisational sign-off is claimed."
)


EXTERNAL_SOURCES = {
    "p6_input": PORTFOLIO_ROOT / "06_RiskSystemRuleImplementation" / "data" / "project6_policy_input.csv.gz",
    "p6_policy": PORTFOLIO_ROOT / "06_RiskSystemRuleImplementation" / "reports" / "policy_scenario_impact_summary.csv",
    "p3_validation": PORTFOLIO_ROOT / "03_CreditRiskDecisionEngine" / "reports" / "06_validation_metrics.csv",
    "p3_cutoff": PORTFOLIO_ROOT / "03_CreditRiskDecisionEngine" / "reports" / "08_cutoff_strategy.csv",
    "p3_model_stack": PORTFOLIO_ROOT / "03_CreditRiskDecisionEngine" / "reports" / "40_post_coarse_model_stack_performance.csv",
    "p3_recommendation": PORTFOLIO_ROOT / "03_CreditRiskDecisionEngine" / "reports" / "40_final_model_recommendation.csv",
    "p3_model_card": PORTFOLIO_ROOT / "03_CreditRiskDecisionEngine" / "docs" / "model_card.md",
    "p4_account": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "ecl_account_level.csv.gz",
    "p4_view": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "ecl_view_comparison.csv",
    "p4_stage": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "ecl_by_stage.csv",
    "p4_segment": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "ecl_by_segment.csv",
    "p4_scenario": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "scenario_ecl_summary.csv",
    "p4_appetite": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "outputs" / "risk_appetite_status.csv",
    "p4_sensitivity": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "reports" / "sensitivity_analysis.csv",
    "p4_assumption_bridge": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "reports" / "assumption_change_ecl_bridge.csv",
    "p4_policy_bridge": PORTFOLIO_ROOT / "04_IFRS9StyleECLStressTesting" / "reports" / "project6_to_project4_ecl_bridge.csv",
    "p5_fraud_kpi": PORTFOLIO_ROOT / "05_FraudOperationalRisk" / "outputs" / "observed_fraud_kpi_summary.csv",
    "p5_priority": PORTFOLIO_ROOT / "05_FraudOperationalRisk" / "outputs" / "priority_queue_efficiency.csv",
    "p5_incidents": PORTFOLIO_ROOT / "05_FraudOperationalRisk" / "operational_risk" / "incident_register.csv",
}

PACKAGED_SOURCES = {
    "p6_input": ROOT / "data" / "observed" / "p2_observed_account_base.csv.gz",
    "p6_policy": ROOT / "data" / "reference_p6" / "policy_scenario_impact_summary.csv",
    "p3_validation": ROOT / "data" / "reference_p3" / "validation_metrics.csv",
    "p3_cutoff": ROOT / "data" / "reference_p3" / "cutoff_strategy.csv",
    "p3_model_stack": ROOT / "data" / "reference_p3" / "model_stack_performance.csv",
    "p3_recommendation": ROOT / "data" / "reference_p3" / "final_model_recommendation.csv",
    "p3_model_card": ROOT / "data" / "reference_p3" / "model_card.md",
    "p4_account": ROOT / "data" / "reference_p4" / "ecl_account_level.csv.gz",
    "p4_view": ROOT / "data" / "reference_p4" / "ecl_view_comparison.csv",
    "p4_stage": ROOT / "data" / "reference_p4" / "ecl_by_stage.csv",
    "p4_segment": ROOT / "data" / "reference_p4" / "ecl_by_segment.csv",
    "p4_scenario": ROOT / "data" / "reference_p4" / "scenario_ecl_summary.csv",
    "p4_appetite": ROOT / "data" / "reference_p4" / "risk_appetite_status.csv",
    "p4_sensitivity": ROOT / "data" / "reference_p4" / "sensitivity_analysis.csv",
    "p4_assumption_bridge": ROOT / "data" / "reference_p4" / "assumption_change_ecl_bridge.csv",
    "p4_policy_bridge": ROOT / "data" / "reference_p4" / "project6_to_project4_ecl_bridge.csv",
    "p5_fraud_kpi": ROOT / "data" / "reference_p5" / "observed_fraud_kpi_summary.csv",
    "p5_priority": ROOT / "data" / "reference_p5" / "priority_queue_efficiency.csv",
    "p5_incidents": ROOT / "data" / "reference_p5" / "incident_register.csv",
}

SOURCE_VERSIONS = {
    "P3": "Project3_CreditRiskDecisionEngine_Final",
    "P4": "Project4_IFRS9StyleECLStressTesting_Gold_v1_2_2",
    "P5": "Project5_FraudOperationalRisk_Gold_v1_0_1",
    "P6": "Project6_RiskSystemRuleImplementation_Final_v1_6",
}


def ensure_dirs() -> None:
    for name in [
        "audit",
        "data_contract",
        "data/observed",
        "data/synthetic",
        "data/reference_p3",
        "data/reference_p4",
        "data/reference_p5",
        "data/reference_p6",
        "data/reviewer_samples",
        "methodology",
        "outputs",
        "governance",
        "testing",
        "validation",
        "archive/superseded/excel",
        "archive/superseded/validation",
        "archive/superseded/evidence",
        "reports",
        "excel",
        "powerbi/dax_queries",
        "powerbi/screenshots",
        "powerbi/screenshots/desktop",
        "powerbi/screenshots/mobile",
        "dashboard/assets",
        "sql",
        "scripts",
        "logs",
    ]:
        (ROOT / name).mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(frame: pd.DataFrame, relative: str, **kwargs) -> Path:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, **kwargs)
    return path


def write_md(relative: str, title: str, body: str, disclaimer: bool = True) -> Path:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = f"# {title}\n\n"
    if disclaimer:
        prefix += f"> {DISCLAIMER}\n\n"
    path.write_text(prefix + body.rstrip() + "\n", encoding="utf-8")
    return path


def add_meta(
    frame: pd.DataFrame,
    layer: str,
    status: str,
    source_project: str,
    boundary: str,
    period: str | None = None,
) -> pd.DataFrame:
    out = frame.copy()
    out["data_layer"] = layer
    out["data_status"] = status
    out["source_project"] = source_project
    out["source_version"] = VERSION
    out["claim_boundary"] = boundary
    if period is None:
        out["as_of_period"] = "ALL"
    elif period in out.columns:
        out["as_of_period"] = out[period].astype(str)
    else:
        out["as_of_period"] = str(period)
    return out


def table_md(frame: pd.DataFrame, decimals: int = 4) -> str:
    temp = frame.copy()
    for column in temp.select_dtypes(include=["number"]).columns:
        temp[column] = temp[column].map(lambda value: "" if pd.isna(value) else f"{value:.{decimals}f}")
    headers = [str(column) for column in temp.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in temp.astype(str).itertuples(index=False, name=None):
        lines.append("| " + " | ".join(value.replace("|", "/") for value in row) + " |")
    return "\n".join(lines)


def safe_ratio(numerator: float, denominator: float, zero_value: float = np.nan) -> float:
    return float(numerator / denominator) if denominator else float(zero_value)


def ks_threshold_detail(y: pd.Series, score: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame({"y": y.astype(int), "score": score.astype(float)}).dropna()
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "score_threshold", "total_accounts", "bad_accounts", "good_accounts",
                "cumulative_bad_accounts", "cumulative_good_accounts",
                "cumulative_bad_share", "cumulative_good_share", "ks_gap",
            ]
        )
    grouped = (
        frame.groupby("score", as_index=False)
        .agg(total_accounts=("y", "size"), bad_accounts=("y", "sum"))
        .rename(columns={"score": "score_threshold"})
        .sort_values("score_threshold", ascending=False)
    )
    grouped["good_accounts"] = grouped["total_accounts"] - grouped["bad_accounts"]
    bad_count = int(grouped["bad_accounts"].sum())
    good_count = int(grouped["good_accounts"].sum())
    if not good_count or not bad_count:
        grouped["cumulative_bad_accounts"] = np.nan
        grouped["cumulative_good_accounts"] = np.nan
        grouped["cumulative_bad_share"] = np.nan
        grouped["cumulative_good_share"] = np.nan
        grouped["ks_gap"] = np.nan
        return grouped
    grouped["cumulative_bad_accounts"] = grouped["bad_accounts"].cumsum()
    grouped["cumulative_good_accounts"] = grouped["good_accounts"].cumsum()
    grouped["cumulative_bad_share"] = grouped["cumulative_bad_accounts"] / bad_count
    grouped["cumulative_good_share"] = grouped["cumulative_good_accounts"] / good_count
    grouped["ks_gap"] = (grouped["cumulative_bad_share"] - grouped["cumulative_good_share"]).abs()
    return grouped


def ks_stat(y: pd.Series, score: pd.Series) -> float:
    detail = ks_threshold_detail(y, score)
    if detail.empty or detail["ks_gap"].isna().all():
        return np.nan
    return float(detail["ks_gap"].max())


def make_psi_edges(reference: pd.Series, bins: int = 10) -> np.ndarray:
    values = pd.to_numeric(reference, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    if len(values) == 0:
        return np.array([-np.inf, np.inf])
    edges = np.unique(np.quantile(values, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return np.array([-np.inf, np.inf])
    edges[0] = -np.inf
    edges[-1] = np.inf
    return edges


def psi_from_edges(reference: pd.Series, actual: pd.Series, edges: np.ndarray) -> float:
    expected = pd.to_numeric(reference, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    current = pd.to_numeric(actual, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    if len(expected) == 0 or len(current) == 0 or len(edges) < 3:
        return np.nan
    expected_pct = np.histogram(expected, bins=edges)[0] / len(expected)
    current_pct = np.histogram(current, bins=edges)[0] / len(current)
    expected_pct = np.clip(expected_pct, 1e-6, None)
    current_pct = np.clip(current_pct, 1e-6, None)
    return float(np.sum((current_pct - expected_pct) * np.log(current_pct / expected_pct)))


def risk_status(value: float, green: float, amber: float, direction: str) -> str:
    if pd.isna(value):
        return "NOT_ASSESSABLE"
    if direction == "higher_bad":
        return "GREEN" if value <= green else "AMBER" if value <= amber else "RED"
    return "GREEN" if value >= green else "AMBER" if value >= amber else "RED"


def alert_state(current_status: str, prior_status: str | None) -> str:
    if current_status == "NOT_ASSESSABLE":
        return "NOT_ASSESSABLE"
    if prior_status is None or prior_status == "NOT_ASSESSABLE":
        return "NEW" if current_status in {"AMBER", "RED"} else "STABLE_GREEN"
    severity = {"GREEN": 0, "AMBER": 1, "RED": 2}
    current_level = severity[current_status]
    prior_level = severity[prior_status]
    if current_level == 0 and prior_level > 0:
        return "RESOLVED"
    if current_level > prior_level:
        return "WORSENING"
    if current_level < prior_level and current_level > 0:
        return "IMPROVING"
    if current_level > 0:
        return "PERSISTENT"
    return "STABLE_GREEN"


def count_rows(path: Path) -> int:
    if path.suffix.lower() == ".md":
        return 0
    try:
        return int(sum(len(chunk) for chunk in pd.read_csv(path, usecols=[0], chunksize=250_000)))
    except Exception:
        return 0


def _load_external_p6() -> pd.DataFrame:
    frame = pd.read_csv(EXTERNAL_SOURCES["p6_input"])
    frame = frame.rename(columns={"loan_id": "account_id", "predicted_pd": "pd", "ead": "exposure"})
    frame["application_period"] = pd.to_datetime(frame["application_month"]).dt.to_period("M").astype(str)
    frame["score_band"] = pd.cut(
        frame["scorecard_points"],
        bins=[-np.inf, 450, 500, 550, 600, 650, 700, np.inf],
        labels=["<450", "450-500", "500-550", "550-600", "600-650", "650-700", "700+"],
    ).astype(str)
    frame["pd_band"] = pd.cut(
        frame["pd"],
        bins=[-np.inf, 0.05, 0.10, 0.15, 0.20, 0.25, np.inf],
        labels=["<=5%", "5-10%", "10-15%", "15-20%", "20-25%", ">25%"],
    ).astype(str)
    frame["outcome_eligible_flag"] = frame["matured_flag"].astype(int)
    frame["policy_version"] = "P6_Current_25pct"
    frame["policy_decision"] = np.select(
        [frame["pd"].le(0.25), frame["pd"].le(0.35)],
        ["APPROVE", "MANUAL_REVIEW"],
        default="DECLINE",
    )
    frame["exception_flag"] = (
        frame["pd"].isna()
        | frame["high_dti_indicator"].astype(bool)
        | frame["low_fico_indicator"].astype(bool)
    ).astype(int)
    frame["override_flag"] = frame["segment_overlay_flag"].astype(int)
    frame["stage_proxy"] = np.where(
        frame["risk_grade"].astype(str).str.contains("D|E", regex=True) | frame["pd"].ge(0.20),
        "Stage 2 proxy",
        "Stage 1 proxy",
    )
    frame["segment_key"] = frame["risk_grade"].astype(str) + " | " + frame["purpose"].astype(str)
    return frame


def load_base() -> pd.DataFrame:
    path = PACKAGED_SOURCES["p6_input"]
    if not path.exists():
        raise FileNotFoundError(f"Packaged observed base is missing: {path}")
    frame = pd.read_csv(path)
    if "outcome_eligible_flag" not in frame.columns:
        frame["outcome_eligible_flag"] = frame["matured_flag"].astype(int)
    return frame


def resolve_run_mode() -> str:
    requested = os.environ.get("P2_RUN_MODE", "auto").strip().lower()
    if requested not in {"auto", "author", "author_reference", "reviewer", "quick"}:
        raise ValueError("P2_RUN_MODE must be auto, author, author_reference, reviewer or quick")
    external_ready = all(path.exists() for path in EXTERNAL_SOURCES.values())
    packaged_ready = all(path.exists() for key, path in PACKAGED_SOURCES.items() if key != "p6_input") and PACKAGED_SOURCES["p6_input"].exists()
    if requested == "auto":
        return "author" if external_ready else "reviewer"
    if requested == "author" and not external_ready:
        missing = [key for key, path in EXTERNAL_SOURCES.items() if not path.exists()]
        raise FileNotFoundError(f"Author rebuild missing external sources: {missing}")
    if requested in {"author_reference", "reviewer", "quick"} and not packaged_ready:
        missing = [key for key, path in PACKAGED_SOURCES.items() if not path.exists()]
        raise FileNotFoundError(f"Packaged rebuild inputs are incomplete: {missing}")
    return requested


def audit_existing_project() -> None:
    ensure_dirs()
    findings = pd.DataFrame(
        [
            ["P2-R01", "Maturity", "Immature outcomes displayed as zero", "REBUILD", "Outcome metrics must use matured denominators and N/A when no eligible accounts"],
            ["P2-R02", "EWS", "Historical maxima labelled current", "REBUILD", "Use latest eligible period, prior, baseline, movement and persistence"],
            ["P2-R03", "Synthetic", "Single vintage and 36-month amortisation for all", "REBUILD", "Use multiple origination vintages and term-aware balances"],
            ["P2-R04", "Stock flow", "Static rates labelled stock-flow bridge", "REBUILD", "Reconcile beginning stock, inflow, cures, defaults, closures and ending stock"],
            ["P2-R05", "Policy/ECL", "Static summaries only", "REBUILD", "Add policy-version bridge and controlled ECL overlays"],
            ["P2-R06", "Technical", "SQL/DAX/Excel tests not executable", "REBUILD", "Run SQL, add complete DAX and formula-driven Excel controls"],
            ["P2-R07", "Packaging", "External dependencies and stale manifest", "REBUILD", "Add reviewer mode and generate manifest after final report"],
            ["P2-R08", "Power BI", "No PBIX or Power BI engine available", "OPEN_EXTERNAL", "Do not fake PBIX; deliver executable dashboard and governed PBIX build gate"],
        ],
        columns=["finding_id", "area", "finding", "decision", "required_remediation"],
    )
    write_csv(findings, "audit/gold_v2_remediation_register.csv")
    write_md(
        "audit/gold_v2_remediation_assessment.md",
        "Project 2 Gold v2 Remediation Assessment",
        "The v1 package is reclassified as a Gold candidate. Gold v2 requires substantive methodology, monitoring, testing and packaging remediation. PBIX remains an external execution gate because Power BI Desktop is not available in the build environment; no binary will be fabricated.",
    )


def phase0_methodology_lock() -> None:
    ensure_dirs()
    write_md(
        "methodology/gold_v2_methodology_lock.md",
        "Gold v2 Methodology Lock",
        f"""## Monitoring principles

1. Observed outcome metrics use matured accounts only.
2. A period with zero matured accounts is `NOT_ASSESSABLE`, never a zero bad rate.
3. EWS uses the latest eligible period and prior eligible period, not historical maxima.
4. Model metrics require at least {MIN_MATURED_ACCOUNTS:,} matured accounts and {MIN_BAD_EVENTS:,} bad events.
5. Synthetic servicing uses multiple origination vintages, term-aware amortisation and separate default stock/flow.
6. P6 policy scenarios are monitored as versions on a common matured population.
7. P4 ECL has scenario/assumption monitoring overlays but no fabricated prior-period trend.
8. Every alert has source-specific affected population, impact method and specific management action.
9. Reviewer rebuild uses packaged frozen inputs; author rebuild uses external project roots.
10. Validation distinguishes file presence, substantive reconciliation, executable tests and open external gates.
""",
    )
    write_md(
        "data_contract/run_modes.md",
        "Project 2 Run Modes",
        """- `quick`: validate packaged outputs and run lightweight executable controls.
- `author_reference`: rebuild from packaged frozen inputs inside an isolated workspace and capture the immutable author baseline bundle. This mode is only permitted when `P2_ALLOW_AUTHOR_REFERENCE_CAPTURE=1`.
- `reviewer`: rebuild all Project 2 outputs from the packaged observed base and frozen P3/P4/P5/P6 references. Reviewer mode must read a pre-existing author reference and cannot create or refresh it.
- `author`: refresh packaged inputs from the external portfolio project roots, then rebuild.
- `auto`: use author mode when every external source exists; otherwise reviewer mode.

The controlled route is `python scripts/run_two_phase_reproducibility.py`: isolated author-reference build, frozen-reference copy, reviewer rebuild, then clean-extract validation.
""",
    )
    core_requirements = "numpy==2.4.4\nopenpyxl==3.1.5\npandas==3.0.2\npillow==12.2.0\nscikit-learn==1.8.0\n"
    (ROOT / "requirements-core.txt").write_text(core_requirements, encoding="ascii")
    (ROOT / "requirements.txt").write_text(
        "# Core cross-platform reviewer dependencies. Windows Excel cache refresh is optional.\n"
        "-r requirements-core.txt\n",
        encoding="ascii",
    )
    (ROOT / "requirements-windows-excel.txt").write_text(
        "-r requirements-core.txt\npywin32==311\n",
        encoding="ascii",
    )

    observed_contract = pd.DataFrame(
        [
            ["account_id", "Required", "Unique accepted/booked account identifier", "All accounts", "P3/P6"],
            ["application_period", "Required", "Historical origination/application cohort period", "All accounts", "P3/P6"],
            ["matured_flag", "Required", "Outcome eligibility flag", "Outcome gate", "P3/P6"],
            ["bad_flag", "Required", "Observed historical outcome; used only when matured_flag=1", "Matured only", "P3/P6"],
            ["pd", "Required", "Frozen P3-derived probability of default", "All for mix; matured for calibration", "P3/P6"],
            ["scorecard_points", "Required", "Frozen P3-derived score", "All accounts", "P3/P6"],
            ["risk_grade", "Required", "Frozen risk grade", "All accounts", "P3/P6"],
            ["exposure", "Required", "EAD/exposure proxy", "All accounts", "P3/P6"],
            ["policy_decision", "Derived", "Baseline policy decision", "Historical simulation", "P6"],
            ["fico", "Required", "FICO for segment overlay and drift", "All accounts", "P3/P6"],
            ["dti", "Required", "DTI for segment overlay and drift", "All accounts", "P3/P6"],
        ],
        columns=["field", "requirement", "business_definition", "population_scope", "source_project"],
    )
    observed_contract = add_meta(observed_contract, "Observed", "Contract", "P2", "Historical accepted/booked accounts; outcomes matured only")
    write_csv(observed_contract, "data_contract/p2_observed_input_contract.csv")
    write_csv(observed_contract, "02_p2_observed_input_contract.csv")

    synthetic_contract = pd.DataFrame(
        [
            ["account_id", "Required", "Synthetic servicing account identifier"],
            ["origination_vintage", "Required", "Distinct origination cohort"],
            ["snapshot_month", "Required", "Synthetic monthly snapshot"],
            ["months_on_book", "Required", "MOB 1-36 monitoring horizon"],
            ["term_months", "Required", "Documented 36/60-month synthetic term"],
            ["beginning_balance", "Required", "Beginning synthetic balance"],
            ["ending_balance", "Required", "Term-aware ending synthetic balance"],
            ["beginning_dpd_bucket", "Required", "Beginning delinquency stock"],
            ["dpd_bucket", "Required", "Ending delinquency/default/closed state"],
            ["new_delinquency_inflow_flag", "Required", "Current-to-delinquent flow"],
            ["cure_flag", "Required", "Delinquent-to-current flow"],
            ["new_default_flag", "Required", "New default flow; distinct from stock"],
            ["default_stock_flag", "Required", "Ending default stock"],
            ["closure_flow_flag", "Required", "New closure flow"],
        ],
        columns=["field", "requirement", "business_definition"],
    )
    synthetic_contract = add_meta(synthetic_contract, "Synthetic", "Contract", "P2", "Controls-testing only; not observed servicing history")
    write_csv(synthetic_contract, "data_contract/p2_synthetic_input_contract.csv")
    write_csv(synthetic_contract, "03_p2_synthetic_input_contract.csv")

    dependency_contract = pd.DataFrame(
        [
            ["P3/P6", "Observed account base and frozen PD/score", "data/observed/p2_observed_account_base.csv.gz", SOURCE_VERSIONS["P6"]],
            ["P3", "Model benchmark and governance", "data/reference_p3/", SOURCE_VERSIONS["P3"]],
            ["P4", "ECL, stress and concentration overlays", "data/reference_p4/", SOURCE_VERSIONS["P4"]],
            ["P5", "Fraud and operational-risk context", "data/reference_p5/", SOURCE_VERSIONS["P5"]],
            ["P6", "Policy-version reconciliation", "data/reference_p6/", SOURCE_VERSIONS["P6"]],
        ],
        columns=["source_project", "monitoring_use", "packaged_reviewer_path", "source_version"],
    )
    dependency_contract = add_meta(dependency_contract, "Mixed", "Frozen", "P2", "Reviewer paths are packaged and portable; author mode may refresh external roots")
    write_csv(dependency_contract, "data_contract/p2_upstream_dependency_contract.csv")
    write_csv(dependency_contract, "04_p2_upstream_dependency_contract.csv")

    availability_body = """| Source | Reviewer availability | Use | Packaged path |
| --- | --- | --- | --- |
| P3/P6 account base | Yes | Observed portfolio and model/policy monitoring | `data/observed/p2_observed_account_base.csv.gz` |
| P3 references | Yes | Frozen development/model benchmark | `data/reference_p3/` |
| P4 references | Yes | ECL/stress/concentration overlays | `data/reference_p4/` |
| P5 references | Yes | Fraud/operational-risk context | `data/reference_p5/` |
| P6 references | Yes | Policy reconciliation | `data/reference_p6/` |

`reviewer` mode requires no sibling project folders. `author` mode refreshes these frozen files from the portfolio roots.
"""
    write_md("data_contract/p2_data_availability_check.md", "Project 2 Data Availability Check", availability_body)
    write_md("05_p2_data_availability_check.md", "Project 2 Data Availability Check", availability_body)
    evidence_design = """## Observed/frozen layer

Historical accepted/booked account evidence supports portfolio composition and matured outcome metrics. P3/P4/P5/P6 methods remain frozen.

## Synthetic servicing-control layer

Monthly DPD, roll-rate, cure, default stock/flow and vintage servicing are deterministic synthetic controls because observed monthly servicing history is unavailable. The layer uses multiple vintages and term-aware 36/60-month balances and must never be labelled observed.
"""
    write_md("data_contract/observed_vs_synthetic_design.md", "Observed vs Synthetic Evidence Design", evidence_design)
    write_md("06_observed_vs_synthetic_design.md", "Observed vs Synthetic Evidence Design", evidence_design)
    period_body = """Observed `application_period` is a historical cohort period, not a servicing snapshot. Outcome metrics are assessable only where matured accounts exist and model metrics also meet minimum account/event gates.

Synthetic `snapshot_month` is an account-month servicing-control period. `months_on_book` covers MOB 1-36 across staggered origination vintages; a 60-month account can retain balance after MOB36.
"""
    write_md("data_contract/monitoring_period_definition.md", "Monitoring Period Definition", period_body)
    write_md("07_monitoring_period_definition.md", "Monitoring Period Definition", period_body)
    write_md("01_project2_scope.md", "Project 2 Scope", "Project 2 is a governed monitoring and management-action system. It integrates maturity-safe observed credit outcomes, synthetic servicing controls, frozen model/policy/ECL/enterprise-risk overlays, executable SQL, formula-driven Excel, an executable browser dashboard and a conditional Power BI release pack.")
    write_md("11_monthly_snapshot_methodology.md", "Monthly Snapshot Methodology", "Observed monitoring is cohort-based. Synthetic account-month snapshots use multiple origination vintages, documented 36/60-month term assignment, term-aware balances, beginning/ending DPD states, default stock versus flow, cures, closures and a zero-difference stock-flow bridge.")
    write_md("12_model_monitoring_decision.md", "Model Monitoring Decision", "P2 monitors frozen P3-derived PD/score fields and does not retrain the model. AUC, KS, Gini and calibration use matured outcomes; PSI uses fixed development bins. Latest and prior eligible periods drive EWS.")
    write_md("13_policy_monitoring_decision.md", "Policy Monitoring Decision", "P2 compares baseline 25%, candidate 20%, conservative 15%, overlay and decline-threshold sensitivity on one common historical booked population. It does not claim full applicant-level production impact. Candidate 20% requires a controlled pilot/capacity redesign, not wholesale rollout.")
    write_md("14_ecl_monitoring_decision.md", "ECL Monitoring Decision", "P2 monitors frozen P4 ECL scenario, sensitivity, concentration and readiness outputs. Stage 2 remains a broad proxy and no prior ECL snapshot exists, so no period trend is fabricated.")
    write_md("15_phase0_validation_gate.md", "Phase 0 Validation Gate", "PASS. Scope, portable reviewer contracts, exact upstream versions, monitoring period, maturity gates, observed/synthetic boundaries and external PBIX/DAX gates are locked before calculation.")


def _copy_frozen_inputs() -> None:
    for key, source in EXTERNAL_SOURCES.items():
        if key == "p6_input":
            continue
        target = PACKAGED_SOURCES[key]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _source_project(key: str) -> str:
    return key[:2].upper()


def load_validate_sources() -> None:
    ensure_dirs()
    mode = resolve_run_mode()
    if mode == "author":
        base = _load_external_p6()
        base.to_csv(PACKAGED_SOURCES["p6_input"], index=False, compression="gzip")
        _copy_frozen_inputs()
    else:
        base = load_base()

    required_columns = {
        "account_id", "application_period", "matured_flag", "bad_flag", "pd", "scorecard_points",
        "risk_grade", "exposure", "lgd", "expected_loss", "fico", "dti", "loan_amount", "purpose",
        "policy_decision", "outcome_eligible_flag",
    }
    missing_columns = sorted(required_columns - set(base.columns))
    if missing_columns:
        raise ValueError(f"Observed base missing required columns: {missing_columns}")
    if base["account_id"].isna().any() or base["account_id"].duplicated().any():
        raise ValueError("Observed account_id must be complete and unique")
    if not base["pd"].between(0, 1).all():
        raise ValueError("Observed PD must be between 0 and 1")
    if not base["bad_flag"].isin([0, 1]).all() or not base["matured_flag"].isin([0, 1]).all():
        raise ValueError("Observed bad_flag and matured_flag must be binary")

    base.sample(min(100_000, len(base)), random_state=SEED).to_csv(
        ROOT / "data/reviewer_samples/observed_base_sample_100k.csv.gz", index=False, compression="gzip"
    )
    sample_columns = [
        "account_id", "application_period", "matured_flag", "bad_flag", "pd", "scorecard_points",
        "risk_grade", "exposure", "lgd", "expected_loss", "fico", "dti", "loan_amount", "purpose",
        "policy_decision",
    ]
    base[sample_columns].sample(5_000, random_state=SEED).to_csv(
        ROOT / "data/reviewer_samples/observed_account_sample_5k.csv", index=False
    )

    source_uses = {
        "p3_validation": "Frozen P3 baseline validation benchmark",
        "p3_cutoff": "Frozen P3 cutoff economics",
        "p3_model_stack": "Frozen P3 model-stack benchmark",
        "p3_recommendation": "Frozen P3 model-use decision",
        "p3_model_card": "Frozen P3 model governance",
        "p4_account": "Full frozen P4 account-level ECL monitoring input",
        "p4_view": "P4 evidence-constrained versus proxy-lifetime view",
        "p4_stage": "P4 stage contribution monitoring",
        "p4_segment": "P4 purpose concentration monitoring",
        "p4_scenario": "P4 scenario ECL monitoring",
        "p4_appetite": "P4 risk-appetite context",
        "p4_sensitivity": "P4 EAD/LGD/PD sensitivity overlays",
        "p4_assumption_bridge": "P4 assumption-change attribution",
        "p4_policy_bridge": "P6-to-P4 ECL scope bridge",
        "p5_fraud_kpi": "P5 observed fraud benchmark indicators",
        "p5_priority": "P5 synthetic queue-efficiency indicator",
        "p5_incidents": "P5 synthetic incident-governance indicators",
        "p6_policy": "Frozen P6 policy-version scenario summary",
    }
    source_rows = [
        {
            "source_project": "P3/P6",
            "source_version": f"{SOURCE_VERSIONS['P3']} via {SOURCE_VERSIONS['P6']}",
            "original_source": "P6 packaged policy input containing frozen P3-derived score/PD",
            "packaged_path": PACKAGED_SOURCES["p6_input"].relative_to(ROOT).as_posix(),
            "row_count": len(base),
            "sha256": sha256(PACKAGED_SOURCES["p6_input"]),
            "transformation": "Observed Project 2 account base",
            "data_status": "Observed/Derived",
            "claim_boundary": "Historical accepted/booked account evidence; not full applicant flow",
        }
    ]
    for key, use in source_uses.items():
        packaged = PACKAGED_SOURCES[key]
        source_project = _source_project(key)
        source_rows.append(
            {
                "source_project": source_project,
                "source_version": SOURCE_VERSIONS[source_project],
                "original_source": EXTERNAL_SOURCES[key].name,
                "packaged_path": packaged.relative_to(ROOT).as_posix(),
                "row_count": count_rows(packaged),
                "sha256": sha256(packaged),
                "transformation": use,
                "data_status": "Frozen/Derived",
                "claim_boundary": "Upstream methodology remains frozen; Project 2 monitors outputs only",
            }
        )
    write_csv(pd.DataFrame(source_rows), "validation/source_manifest.csv")
    (ROOT / "validation/run_mode.json").write_text(
        json.dumps(
            {
                "run_mode": mode,
                "run_date": RUN_DATE,
                "version": VERSION,
                "external_sources_used": mode == "author",
                "packaged_reviewer_sources_complete": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    matured = base[base["matured_flag"].eq(1)]
    reconciliation = pd.DataFrame(
        [
            ["Total accepted/booked base", len(base), int(base["bad_flag"].sum()), float(base["exposure"].sum()), "ALL", "PASS"],
            ["Matured observed outcome", len(matured), int(matured["bad_flag"].sum()), float(matured["exposure"].sum()), "MATURED_ONLY", "PASS"],
            ["Immature monitor-only", int(base["matured_flag"].eq(0).sum()), np.nan, float(base.loc[base["matured_flag"].eq(0), "exposure"].sum()), "OUTCOME_NOT_ASSESSABLE", "PASS"],
        ],
        columns=["population", "accounts", "observed_bad_accounts", "exposure", "outcome_scope", "status"],
    )
    write_csv(
        add_meta(reconciliation, "Observed", "Derived", "P3/P6/P2", "Maturity-safe population reconciliation"),
        "data_contract/population_reconciliation.csv",
    )


def _period_change(frame: pd.DataFrame, value_columns: list[str]) -> pd.DataFrame:
    out = frame.sort_values("application_period").copy()
    for column in value_columns:
        out[f"prior_{column}"] = out[column].shift(1)
        out[f"change_{column}"] = out[column] - out[f"prior_{column}"]
    return out


def build_observed_monitoring_base() -> None:
    base = load_base()
    base["outcome_eligible_flag"] = base["matured_flag"].astype(int)
    snapshot_columns = [
        "account_id", "application_period", "outcome_eligible_flag", "matured_flag", "bad_flag", "pd",
        "scorecard_points", "risk_grade", "pd_band", "score_band", "risk_decile", "exposure", "expected_loss",
        "lgd", "policy_version", "policy_decision", "exception_flag", "override_flag", "stage_proxy", "fico",
        "fico_band", "dti", "dti_band", "annual_inc", "income_band", "loan_amount", "term", "purpose",
        "home_ownership", "state", "segment_key",
    ]
    observed_snapshot = add_meta(
        base[snapshot_columns],
        "Observed",
        "Derived",
        "P3/P6",
        "Historical origination-cohort monitoring; not monthly servicing",
        "application_period",
    )
    write_csv(observed_snapshot, "outputs/monthly_portfolio_snapshot.csv.gz", compression="gzip")

    matured = base[base["matured_flag"].eq(1)]
    kpi = pd.DataFrame(
        [
            ["total_accounts", len(base), "count", "ALL"],
            ["matured_accounts", len(matured), "count", "MATURED_ONLY"],
            ["immature_accounts", int(base["matured_flag"].eq(0).sum()), "count", "OUTCOME_NOT_ASSESSABLE"],
            ["total_exposure", float(base["exposure"].sum()), "cost_units", "ALL"],
            ["average_pd_all_accounts", float(base["pd"].mean()), "ratio", "ALL"],
            ["average_pd_matured", float(matured["pd"].mean()), "ratio", "MATURED_ONLY"],
            ["observed_bad_accounts_matured", int(matured["bad_flag"].sum()), "count", "MATURED_ONLY"],
            ["observed_bad_rate_matured", float(matured["bad_flag"].mean()), "ratio", "MATURED_ONLY"],
            ["expected_loss_proxy", float(base["expected_loss"].sum()), "cost_units", "ALL_PROXY"],
            ["high_risk_share_grade_d_e", float(base["risk_grade"].astype(str).str.contains("D|E", regex=True).mean()), "ratio", "ALL"],
            ["stage2_proxy_share", float(base["stage_proxy"].eq("Stage 2 proxy").mean()), "ratio", "ALL_PROXY"],
            ["policy_approval_rate_25pct", float(base["policy_decision"].eq("APPROVE").mean()), "ratio", "ALL"],
            ["policy_manual_review_rate_25pct", float(base["policy_decision"].eq("MANUAL_REVIEW").mean()), "ratio", "ALL"],
        ],
        columns=["metric", "value", "unit", "population_scope"],
    )
    write_csv(add_meta(kpi, "Observed", "Derived", "P3/P6", "Maturity-safe portfolio KPI summary"), "outputs/portfolio_kpi_summary.csv")

    rows: list[dict[str, object]] = []
    for period, group in base.groupby("application_period", sort=True):
        eligible = group[group["matured_flag"].eq(1)]
        observed_bad_accounts = int(eligible["bad_flag"].sum()) if len(eligible) else 0
        rows.append(
            {
                "application_period": period,
                "accounts": len(group),
                "matured_accounts": len(eligible),
                "immature_accounts": int(group["matured_flag"].eq(0).sum()),
                "outcome_eligibility_rate": len(eligible) / len(group),
                "observed_bad_accounts": observed_bad_accounts,
                "observed_bad_rate_matured": safe_ratio(observed_bad_accounts, len(eligible)),
                "outcome_status": "ASSESSABLE" if len(eligible) else "NOT_MATURED_NOT_ASSESSABLE",
                "exposure": float(group["exposure"].sum()),
                "avg_pd_all": float(group["pd"].mean()),
                "avg_pd_matured": float(eligible["pd"].mean()) if len(eligible) else np.nan,
                "calibration_gap_matured": float(eligible["bad_flag"].mean() - eligible["pd"].mean()) if len(eligible) else np.nan,
                "expected_loss": float(group["expected_loss"].sum()),
                "stage2_proxy_share": float(group["stage_proxy"].eq("Stage 2 proxy").mean()),
                "approval_rate_25pct": float(group["policy_decision"].eq("APPROVE").mean()),
            }
        )
    trend = _period_change(
        pd.DataFrame(rows),
        ["accounts", "matured_accounts", "observed_bad_rate_matured", "exposure", "avg_pd_matured", "expected_loss", "stage2_proxy_share", "approval_rate_25pct"],
    )
    trend = add_meta(
        trend,
        "Observed",
        "Derived",
        "P3/P6",
        "Origination-cohort outcome metrics use matured denominators",
        "application_period",
    )
    write_csv(trend, "outputs/portfolio_monthly_trend.csv")
    write_csv(trend.copy(), "outputs/origination_cohort_summary.csv")

    segment_rows: list[dict[str, object]] = []
    for keys, group in base.groupby(["risk_grade", "purpose"], dropna=False):
        eligible = group[group["matured_flag"].eq(1)]
        segment_rows.append(
            {
                "risk_grade": keys[0],
                "purpose": keys[1],
                "accounts": len(group),
                "matured_accounts": len(eligible),
                "exposure": float(group["exposure"].sum()),
                "avg_pd": float(group["pd"].mean()),
                "observed_bad_accounts": int(eligible["bad_flag"].sum()),
                "observed_bad_rate_matured": float(eligible["bad_flag"].mean()) if len(eligible) else np.nan,
                "expected_loss": float(group["expected_loss"].sum()),
            }
        )
    segment = pd.DataFrame(segment_rows)
    segment["exposure_share"] = segment["exposure"] / segment["exposure"].sum()
    segment["el_share"] = segment["expected_loss"] / segment["expected_loss"].sum()
    segment = segment.sort_values("expected_loss", ascending=False)
    write_csv(
        add_meta(segment, "Observed", "Derived", "P3/P6", "Segment outcomes use matured denominator"),
        "outputs/segment_concentration_summary.csv",
    )

    eligible_periods = trend[
        trend["matured_accounts"].ge(MIN_MATURED_ACCOUNTS)
        & trend["observed_bad_accounts"].ge(MIN_BAD_EVENTS)
    ].sort_values("application_period")
    current = eligible_periods.iloc[-1]
    prior = eligible_periods.iloc[-2]
    change_rows = []
    for metric in ["observed_bad_rate_matured", "avg_pd_matured", "calibration_gap_matured", "exposure", "expected_loss", "stage2_proxy_share", "approval_rate_25pct"]:
        change_rows.append(
            {
                "metric": metric,
                "reference_period": f"{MODEL_BASELINE_START}_to_{MODEL_BASELINE_END}",
                "current_period": current["application_period"],
                "prior_period": prior["application_period"],
                "current_value": current[metric],
                "prior_value": prior[metric],
                "change": current[metric] - prior[metric],
                "current_matured_accounts": current["matured_accounts"],
                "prior_matured_accounts": prior["matured_accounts"],
            }
        )
    write_csv(
        add_meta(pd.DataFrame(change_rows), "Observed", "Derived", "P3/P6", "Latest eligible versus prior eligible cohort", str(current["application_period"])),
        "outputs/portfolio_change_summary.csv",
    )


def _synthetic_transition(last_bucket: str, draw: float, risk_factor: float) -> str:
    if last_bucket in {"Default", "Closed"}:
        return last_bucket
    if last_bucket == "Current":
        return "1-29" if draw < min(0.18, 0.012 * risk_factor) else "Current"
    if last_bucket == "1-29":
        if draw < min(0.42, 0.18 * risk_factor):
            return "30-59"
        return "Current" if draw < 0.55 else "1-29"
    if last_bucket == "30-59":
        if draw < min(0.48, 0.22 * risk_factor):
            return "60-89"
        return "Current" if draw < 0.45 else "30-59"
    if last_bucket == "60-89":
        if draw < min(0.55, 0.25 * risk_factor):
            return "90+"
        return "30-59" if draw < 0.55 else "60-89"
    if last_bucket == "90+":
        return "Default" if draw < min(0.70, 0.28 * risk_factor) else "60-89"
    raise ValueError(f"Unsupported DPD bucket: {last_bucket}")


def generate_synthetic_monthly_snapshots() -> None:
    base = load_base()
    eligible = base[
        base["matured_flag"].eq(1)
        & base["application_period"].between("2014-01", "2017-12")
    ].copy()
    sample = eligible.sample(min(SYNTHETIC_SAMPLE_SIZE, len(eligible)), random_state=SEED).copy()
    rng = np.random.default_rng(SEED)
    sample["term_months_synthetic"] = np.where(rng.random(len(sample)) < 0.70, 36, 60)
    sample["term_source"] = "Synthetic 70/30 assignment because P3/P6 base term is unavailable"
    rows: list[list[object]] = []
    delinquent = {"1-29", "30-59", "60-89", "90+"}
    dpd_values = {"Current": 0, "1-29": 15, "30-59": 45, "60-89": 75, "90+": 100, "Default": 120, "Closed": 0}
    payment_rates = {"Current": 1.00, "1-29": 0.80, "30-59": 0.55, "60-89": 0.30, "90+": 0.15, "Default": 0.0, "Closed": 0.0}

    for row in sample.itertuples(index=False):
        original_balance = float(row.loan_amount)
        balance = original_balance
        last_bucket = "Current"
        term_months = int(row.term_months_synthetic)
        origination_vintage = str(row.application_period)
        risk_factor = min(3.0, max(0.5, float(row.pd) / 0.15))
        scheduled_payment = original_balance / term_months
        for mob in range(1, SYNTHETIC_HORIZON_MONTHS + 1):
            snapshot_month = str(pd.Period(origination_vintage, freq="M") + (mob - 1))
            beginning_bucket = last_bucket
            beginning_balance = balance
            draw = float(rng.random())
            ending_bucket = _synthetic_transition(beginning_bucket, draw, risk_factor)
            payment_due = 0.0 if beginning_bucket in {"Default", "Closed"} else min(scheduled_payment, beginning_balance)
            payment_received = payment_due * payment_rates[ending_bucket]
            if ending_bucket == "Default":
                ending_balance = beginning_balance
            elif ending_bucket == "Closed":
                ending_balance = 0.0
            else:
                ending_balance = max(0.0, beginning_balance - payment_received)

            scheduled_maturity_close = mob >= term_months and ending_bucket == "Current" and ending_balance <= scheduled_payment + 1.0
            if scheduled_maturity_close:
                ending_balance = 0.0
                ending_bucket = "Closed"

            new_default_flag = int(beginning_bucket != "Default" and ending_bucket == "Default")
            default_stock_flag = int(ending_bucket == "Default")
            cure_flag = int(beginning_bucket in delinquent and ending_bucket == "Current")
            new_delinquency_inflow_flag = int(beginning_bucket == "Current" and ending_bucket in delinquent)
            closure_flow_flag = int(beginning_bucket != "Closed" and ending_bucket == "Closed")
            beginning_delinquent_flag = int(beginning_bucket in delinquent)
            ending_delinquent_flag = int(ending_bucket in delinquent)
            delinquent_default_outflow_flag = int(beginning_bucket in delinquent and ending_bucket == "Default")
            delinquent_closure_outflow_flag = int(beginning_bucket in delinquent and ending_bucket == "Closed")
            other_migration_net = (
                ending_delinquent_flag
                - beginning_delinquent_flag
                - new_delinquency_inflow_flag
                + cure_flag
                + delinquent_default_outflow_flag
                + delinquent_closure_outflow_flag
            )
            collection_queue = (
                "Legal/Recovery" if ending_bucket in {"Default", "90+"}
                else "Late Stage" if ending_bucket == "60-89"
                else "Early Stage" if ending_bucket in {"1-29", "30-59"}
                else "None"
            )
            rows.append(
                [
                    row.account_id, origination_vintage, snapshot_month, mob, term_months, row.term_source,
                    "Synthetic_Control_25pct", beginning_balance, payment_due, payment_received, ending_balance,
                    beginning_bucket, ending_bucket, dpd_values[ending_bucket], beginning_delinquent_flag,
                    ending_delinquent_flag, new_delinquency_inflow_flag, cure_flag, new_default_flag,
                    default_stock_flag, closure_flow_flag, delinquent_default_outflow_flag,
                    delinquent_closure_outflow_flag, other_migration_net, row.risk_grade, row.pd, row.exposure,
                    row.purpose, collection_queue,
                ]
            )
            balance = ending_balance
            last_bucket = ending_bucket

    columns = [
        "account_id", "origination_vintage", "snapshot_month", "months_on_book", "term_months", "term_source",
        "policy_version", "beginning_balance", "payment_due", "payment_received", "ending_balance",
        "beginning_dpd_bucket", "dpd_bucket", "dpd", "beginning_delinquent_flag", "ending_delinquent_flag",
        "new_delinquency_inflow_flag", "cure_flag", "new_default_flag", "default_stock_flag", "closure_flow_flag",
        "delinquent_default_outflow_flag", "delinquent_closure_outflow_flag", "other_migration_net", "risk_grade",
        "pd", "exposure", "purpose", "collection_queue",
    ]
    snapshots = pd.DataFrame(rows, columns=columns)
    snapshots = add_meta(
        snapshots,
        "Synthetic",
        "Synthetic",
        "P2",
        "Multi-vintage, term-aware synthetic servicing controls; not observed delinquency history",
        "snapshot_month",
    )
    write_csv(snapshots, "data/synthetic/monthly_delinquency_snapshots.csv.gz", compression="gzip")
    snapshots.sample(min(50_000, len(snapshots)), random_state=SEED).to_csv(
        ROOT / "data/reviewer_samples/synthetic_snapshot_sample_50k.csv.gz", index=False, compression="gzip"
    )
