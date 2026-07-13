# Risk Committee Monitoring Memo

> Educational portfolio-monitoring and executive-dashboard framework. Observed credit outcomes are limited to historical matured accepted/booked accounts. Monthly delinquency, roll-rate, cure and vintage servicing are separately labelled synthetic controls-testing evidence. P4 ECL staging remains proxy-based, P5 operations indicators retain their observed/synthetic boundaries, and P6 policy impact remains a historical booked-account simulation. No live servicing platform, regulatory report, production model monitoring, independent validation or organisational sign-off is claimed.

## Executive conclusion

Portfolio risk is **deteriorating on the latest eligible observed cohort**, while evidence quality remains mixed across domains. The matured observed bad rate rose from **20.88%** in 2017-11 to **21.35%** in 2017-12 (+47 bps), and remains above the 18% Red boundary. Ranking power weakened to AUC **0.597**; PSI increased to **0.127** (Amber). Calibration gap is **2.89%**, still inside the 3% Green boundary but worsening by +75 bps.

## What changed and why

1. **Observed credit quality:** bad rate increased +47 bps. Diagnose grade, purpose, FICO and DTI mix before changing policy.
2. **Model stability:** AUC changed -0.013; PSI rose +0.026. PSI is Amber, so the correct action is diagnostic review and heightened monitoring, not automatic recalibration.
3. **Collections control scenario:** formal synthetic KRI-002 uses 2020-10 because it is the latest month with enough snapshot accounts. 30+ DPD reached 12.33%, up +44 bps. This is a controls test, not observed servicing deterioration. Raw 2020-11 has lower sample and is informational only.
4. **ECL overlay:** Stage 2 proxy share is 48.30%; downside ECL uplift is 53.85%. Both are Red, but P4 remains a proxy snapshot without prior-period movement.

## Policy decision

The 20% candidate improves the auto-approval risk profile: approved bad rate falls from **17.64%** to **14.64%**, and auto-approved routed EL is **49.96% lower versus baseline**. This is a policy-routing simulation result, not a realised portfolio-loss reduction, because manual-review disposition is not modelled. It fails capacity/customer constraints: approval falls **-3,032 bps**, and manual-review volume rises **150.0%** versus baseline. Recommendation: **PILOT_WITH_CAPACITY_REDESIGN**, not full rollout.

## Decisions required

1. Approve a constrained pilot or redesign the review/decline boundary; do not deploy the 20% cutoff wholesale.
2. Assign Model Risk to diagnose PSI drivers and determine whether recalibration/challenger work is warranted.
3. Keep synthetic delinquency outputs outside observed portfolio claims until real servicing history is acquired.
4. Require P4 data remediation for observed SICR and prior-period ECL before using stage trends in production governance.
5. Close each Red/Amber alert only with the acceptance criteria and evidence recorded in the action register.
