# Model Card - Credit Risk Scorecard & Portfolio Analytics

## Intended Use

Credit risk education, portfolio analytics, scorecard mechanics, cutoff simulation and recruiter-facing demonstration.

## Not Intended Use

Production underwriting, automated credit approval, regulatory capital reporting or audited IFRS 9 provisioning.

## Data

Core population: accepted/booked consumer lending accounts.

Target: bad account flag on matured accounts.

Observation date: application month.

Performance window assumption: 12 months.

## Population Bridge

| Dataset layer | Rows | Role | Scope limitation |
|---|---:|---|---|
| Portfolio base | 1,347,681 | Target, baseline PD, EL, cutoff, monitoring and stress/pricing framework | Thin/core feature set |
| Enriched accepted sample | 331,865 | Expanded WOE scorecard and logistic challenger benchmark | Smaller accepted-loan sample with richer fields |
| Rejected applicant data | 27,648,741 | Reject inference sensitivity | No observed repayment outcome |

The AUC 0.626 baseline and the AUC 0.765 / 0.793 enriched models are **not directly comparable as the same model on the same population**. They answer different questions: portfolio foundation performance versus enriched-model benchmark performance.

## Method

This version uses WOE/IV-based formula scoring as the primary explanation layer. Variables are mapped to smoothed WOE bins, combined using IV-based weights, converted into formula PD by score decile, and translated into scorecard points using good-odds convention.

An enriched modeling module then adds 17 candidate application-time risk features from the enriched accepted-loan sample, selects 15 into an expanded WOE formula scorecard, builds a final clean WOE-logistic scorecard after sign/stability cleanup, and benchmarks those layers against a raw logistic regression challenger.

Enriched WOE/IV is fitted only on the 183,002-row training window. Validation 2016 and test 2017 are reserved for out-of-time performance checks.

The expanded WOE formula scorecard is a transparent IV-weighted heuristic scoring layer, not a coefficient-estimated logistic scorecard. The final clean WOE-logistic scorecard fits logistic regression on WOE-transformed variables, excludes variables with severe sign/stability issues, and converts coefficients into scorecard points.

## Key Metrics

| Metric | Test 2017 |
|---|---:|
| AUC | 0.626 |
| Gini | 0.253 |
| KS | 0.180 |
| Brier Score | 0.173 |
| Calibration Gap | 3.50% |

## Metric Interpretation

- AUC 0.626 indicates **moderate ranking power**. It is useful for transparent segmentation, but it is not strong enough for production-grade automated underwriting by itself.
- KS 0.180 confirms **moderate separation**, useful for policy discussion but requiring challenger modeling before production.
- Calibration by score decile is mechanically close because formula PD is assigned from observed default rate by risk decile.
- The more realistic calibration assessment is the 2017 out-of-time sample. The test calibration gap is **3.50%**, meaning observed default is higher than average predicted PD when positive.
- This formula-first risk workflow is suitable for portfolio demonstration, risk analytics explanation and policy simulation, not for automated production approval.

## Enriched Scorecard And Challenger Benchmark

| Model | Test AUC | Test Gini | Test KS | Calibration Gap |
|---|---:|---:|---:|---:|
| Expanded WOE formula scorecard | 0.765 | 0.530 | 0.400 | 1.69% |
| Final clean WOE-logistic scorecard | 0.781 | 0.562 | 0.418 | 1.81% |
| Logistic regression challenger | 0.793 | 0.586 | 0.440 | 1.44% |

The logistic regression challenger improves ranking, but the formula scorecard remains the public explanation layer because it is more transparent for policy, governance and adverse-action style discussion.

## Term Sensitivity

`term_band_exp` is available at origination and is not an outcome variable, so it is retained as an application-time product-tenor feature. However, its IV is very high, so it is treated as a policy-sensitive variable.

| Model | Test AUC | Test KS | Interpretation |
|---|---:|---:|---|
| Expanded WOE with term | 0.765 | 0.400 | Current scorecard benchmark |
| Expanded WOE without term | 0.734 | 0.350 | Performance declines but remains usable |
| Logistic with term | 0.793 | 0.440 | Current challenger benchmark |
| Logistic without term | 0.766 | 0.404 | Performance declines but does not collapse |

Conclusion: product tenor contributes meaningful signal, but enriched performance is not solely driven by term.

## Enriched Calibration And Drift Evidence

- Split drift table: `reports/37_enriched_split_drift_summary.csv`
- Logistic calibration by decile: `reports/37_logistic_calibration_by_decile.csv`
- Formula vs logistic calibration comparison: `reports/38_formula_vs_logistic_calibration_comparison.csv`
- Three-model calibration comparison: `reports/38_formula_vs_woe_logistic_vs_raw_logistic_calibration.csv`
- WOE-logistic calibration by decile: `reports/39_woe_logistic_calibration_by_decile.csv`
- Tail calibration review: `reports/38_tail_calibration_review.csv`
- Tail recalibration plan: `reports/39_tail_recalibration_plan.csv`
- Recalibrated PD by decile candidate: `reports/39_recalibrated_pd_by_decile.csv`
- Recalibration before/after metrics: `reports/40_recalibration_before_after_metrics.csv`
- Top-feature CSI: `reports/37_enriched_feature_csi_top5.csv`
- Score distribution shift: `reports/37_enriched_score_distribution_shift.csv`
- Binning quality check: `reports/37_enriched_binning_quality_check.csv`
- Feature selection rationale: `reports/37_feature_selection_rationale.csv`

High-risk tail note: validation decile 10 has a 10.00 pp logistic calibration gap and test decile 10 has a 6.92 pp gap. Current PDs are pre-recalibration and should not be used for production pricing, ECL or automated cutoff decisions without approved recalibration. The candidate validation-factor recalibration reduces the test decile 10 gap from +6.92 pp to -3.03 pp, but it is diagnostic evidence only; no final recalibrated PD is selected.

## Scorecard Governance Evidence

- Final clean WOE-logistic coefficients: `reports/40_final_clean_woe_logistic_scorecard_coefficients.csv`
- Final clean scorecard points: `reports/40_final_clean_woe_logistic_scorecard_points.csv`
- Final clean coefficient sign review: `reports/40_final_clean_woe_logistic_coefficient_sign_review.csv`
- Final clean exclusion log: `reports/40_final_clean_scorecard_exclusion_log.csv`
- Post-coarse model stack performance: `reports/40_post_coarse_model_stack_performance.csv`
- Mort-account sensitivity: `reports/40_mort_acc_sensitivity.csv`
- Final model recommendation: `reports/40_final_model_recommendation.csv`
- Coarse-binning adjustment log: `reports/38_binning_coarse_adjustment_log.csv`
- Post-coarse WOE stability: `reports/39_woe_stability_after_coarse_binning.csv`
- Final scorecard feature governance list: `reports/39_final_scorecard_feature_governance_list.csv`
- Feature selection governance: `reports/38_feature_selection_governance.csv`
- WOE monotonicity/stability: `reports/38_woe_monotonicity_review.csv`, `reports/38_woe_stability_train_test.csv`
- Challenger decision matrix: `reports/38_challenger_decision_matrix.csv`
- Reason codes and fairness/proxy review: `reports/38_reason_code_mapping.csv`, `reports/38_fairness_proxy_review.csv`

## Limitations

- Reject outcomes are unobserved.
- Reject inference is sensitivity analysis, not a labeled reject-inference implementation.
- Cutoff approval rate is measured on matured accepted/booked accounts, not all applicants.
- True monthly DPD roll-rate is unavailable in the consumer-loan core.
- Consumer-loan recovery cashflows are unavailable.
- LGD and EAD are proxy assumptions.
- RAROC requires funding, operating and capital cost assumptions.
- `sub_grade` and `int_rate` are excluded from challenger features because they can encode lender pricing/risk decisions.
- Low-IV variables retained in the benchmark would require stricter selection, stability and adverse-action review for production.
- `revol_util_band_exp`, `mort_acc_band_exp` and `bankruptcy_band_exp` are excluded from the final clean WOE-logistic scorecard; benchmark evidence is retained separately for governance review.
- This project should not be used for automated underwriting, pricing, credit limit assignment or IFRS 9 reporting without independent validation, recalibration, production data lineage, adverse-action review and governance approval.
