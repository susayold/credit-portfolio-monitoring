# Policy Monitoring Report

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Recommendation

**PILOT_WITH_CAPACITY_REDESIGN**. The 20% candidate reduces straight-through auto-approved risk and EL, but breaches the -15pp approval constraint and +50% manual-review capacity constraint. The reduction is not a realised portfolio-loss claim because routed manual-review outcomes are not modelled. The zero decline rate under the 25/20/15 policies is expected because the frozen population has no PD above the 35% decline threshold; the 30% sensitivity produces a measurable decline population.

| policy_version | approval_rate | manual_review_rate | decline_rate | approved_bad_rate_matured | bad_capture_non_approved | auto_approved_expected_loss | manual_review_expected_loss | declined_expected_loss | total_routed_expected_loss | auto_approved_el_reduction_vs_baseline | manual_review_disposition_assumption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_current_25 | 0.7979 | 0.2021 | 0.0000 | 0.1764 | 0.3020 | 1021716693.2603 | 450802717.9255 | 0.0000 | 450802717.9255 | 0.0000 | NOT_MODELED |
| scenario_1_recommended_20 | 0.4947 | 0.5053 | 0.0000 | 0.1464 | 0.6407 | 511289238.2581 | 961230172.9277 | 0.0000 | 961230172.9277 | 0.4996 | NOT_MODELED |
| scenario_2_conservative_15 | 0.2944 | 0.7056 | 0.0000 | 0.1213 | 0.8230 | 252253323.3672 | 1220266087.8186 | 0.0000 | 1220266087.8186 | 0.7531 | NOT_MODELED |
| scenario_3_overlay_20 | 0.4916 | 0.5084 | 0.0000 | 0.1461 | 0.6439 | 507801460.9534 | 964717950.2325 | 0.0000 | 964717950.2325 | 0.5030 | NOT_MODELED |
| scenario_4_decline_threshold_30 | 0.4947 | 0.4042 | 0.1011 | 0.1464 | 0.6407 | 511289238.2581 | 727850023.4573 | 233380149.4704 | 961230172.9277 | 0.4996 | NOT_MODELED |
