window.PORTFOLIO_PROJECTS = {
  "2": {
    number: "02",
    status: "Completed | Evidence and controls verified",
    statusClass: "complete",
    accent: "#2559a7",
    category: "Portfolio Risk & Monitoring",
    title: "Credit Portfolio Monitoring & Early Warning",
    thesis: "A governed monitoring system that translates credit, policy, ECL and enterprise-risk evidence into current, prior-period and change KRIs, early-warning alerts, accountable actions and an interactive credit risk dashboard.",
    tags: ["Interactive web dashboard", "Portfolio risk", "Multi-vintage", "PSI", "KRI", "Formula Excel", "SQL marts", "Release governance"],
    heroAction: { href: "dashboards/project-2/index.html", label: "Open credit risk dashboard", detail: "Seven interactive views with policy and KRI filters" },
    metrics: [
      { value: "1.348M", label: "Accounts monitored" },
      { value: "19.42B", label: "Exposure proxy" },
      { value: "21.35%", label: "Latest matured bad rate" },
      { value: "6 Red", label: "Current KRI view" },
      { value: "131/131", label: "Automated checks passed" }
    ],
    business: {
      question: "Is portfolio risk deteriorating, what is driving the change, which appetite thresholds are breached and who must act?",
      context: "Risk committees need a single monitoring language across portfolio quality, model behavior, policy outcomes, ECL stress, concentration and enterprise-risk signals.",
      output: "A governed monitoring pack with current, prior-period and change metrics, source-specific EWS impacts, owner/action closure logic, executable SQL, formula-driven Excel and a seven-view interactive browser dashboard."
    },
    dataLayers: [
      { meta: "Observed", title: "Historical booked-account base", text: "1,347,681 accounts with frozen PD, score, grade, exposure, bad flag and policy proxies from the Credit Risk Decision Engine and Risk System Rule Implementation projects." },
      { meta: "Synthetic controls", title: "Term-aware monthly servicing", text: "50,000 sampled accounts create 1.8M account-month rows across 48 vintages, 36/60-month terms and MOB 1-36 for DPD, roll-rate, cure and stock-flow testing only." },
      { meta: "Frozen upstream", title: "ECL and enterprise context", text: "The IFRS 9-Style ECL & Stress Testing project supplies Stage 2 and ECL stress indicators; the Fraud Detection, Controls & Operational Risk project supplies fraud and operational-risk indicators. Their methodologies remain unchanged." },
      { meta: "Governance", title: "Contracts and ownership", text: "Input contracts, KPI dictionary, KRI register, appetite rules, actions, exceptions and audit evidence define how monitoring is used." }
    ],
    formulas: [
      { name: "Observed bad rate", expression: "Bad Rate = Matured bad accounts / Matured accounts", meaning: "Restricts performance to accounts with sufficient outcome history.", use: "Portfolio quality and risk-appetite monitoring." },
      { name: "Expected loss proxy", expression: "Expected Loss = SUM(PD x LGD x EAD)", meaning: "Aggregates account-level credit risk into monetary exposure.", use: "Connects portfolio quality to financial materiality." },
      { name: "Population Stability Index", expression: "PSI = SUM((Actual% - Expected%) x ln(Actual% / Expected%))", meaning: "Measures movement in score or feature distributions.", use: "Triggers model review when drift breaches thresholds." },
      { name: "Roll rate", expression: "Roll i->j = Accounts moving i to j / Accounts in bucket i at t", meaning: "Quantifies migration between delinquency states.", use: "Synthetic controls-testing implementation only in this project." },
      { name: "KRI status", expression: "Status = GREEN / AMBER / RED by metric direction and appetite threshold", meaning: "Turns measures into governed escalation signals.", use: "Routes actions to named owners." }
    ],
    process: [
      { title: "Lock scope and claim boundaries", text: "Define observed versus synthetic use, monitoring period, metric ownership and downstream dependencies before dashboard design.", evidence: "Scope, evidence and ownership rules documented" },
      { title: "Build observed monitoring base", text: "Load frozen account evidence from the Credit Risk Decision Engine and Risk System Rule Implementation projects, then reconcile account, exposure, PD and outcome fields.", evidence: "1,347,681 accounts" },
      { title: "Generate servicing control layer", text: "Create deterministic, term-aware monthly DPD states across multiple origination vintages; separate default stock from new-default flow and reconcile every stock-flow bridge.", evidence: "1.8M account-month rows; zero bridge gap" },
      { title: "Calculate monitoring marts", text: "Produce matured-only portfolio/model metrics, period-level feature drift, policy-version bridges, ECL overlays and concentration views.", evidence: "Latest eligible 2017-12 vs 2017-11" },
      { title: "Convert breaches into action", text: "Evaluate eight KRIs with source-specific affected population, impact, owner, decision, acceptance criteria and closure evidence.", evidence: "6 Red, 1 Amber, 7 actions" },
      { title: "Package decision surfaces", text: "Build executable SQL marts, a 140-formula Excel control model and a responsive credit risk dashboard.", evidence: "13/13 Excel/Python reconciliation" },
      { title: "Validate end to end", text: "Freeze an isolated reference baseline, run executable UAT/SIT and negative tests, reconcile code and outputs independently, and validate the final package after clean extraction.", evidence: "131/131 controls; 253 manifested release files; clean extract PASS" }
    ],
    resultTables: [
      {
        title: "Portfolio health snapshot",
        note: "Exposure and expected-loss values are analytical cost-unit proxies, not regulatory reporting values.",
        headers: ["Metric", "Current", "Interpretation"],
        rows: [
          ["Accounts monitored", "1,347,681", "Large accepted/booked portfolio base"],
          ["Matured population", "1,291,521", "Eligible for observed bad-rate analysis"],
          ["Latest average PD", "18.47%", "2017-12 matured cohort"],
          ["Latest observed bad rate", "21.35%", "2017-12 matured outcome; +47 bps"],
          ["Expected loss proxy", "1.53B", "PD x LGD x EAD aggregation"],
          ["Current 25% approval rate", "80.00%", "Historical booked-account policy view"]
        ]
      },
      {
        title: "KRI status board",
        note: "DPD and some cross-project indicators are Mixed/Synthetic by design; status does not convert them into observed servicing history.",
        headers: ["KRI", "Current", "Threshold", "Status"],
        rows: [
          ["Observed bad rate", "21.35%", "Red > 18%", "RED - persistent"],
          ["30+ DPD rate", "12.33%", "Red > 5%", "RED - synthetic control"],
          ["PD PSI", "0.127", "Amber 0.10-0.25", "AMBER - persistent"],
          ["Calibration gap", "2.89 pp", "Green <= 3 pp", "GREEN"],
          ["Policy exception rate", "5.06%", "Red > 5%", "RED"],
          ["Stage 2 proxy share", "48.30%", "Red > 25%", "RED - static proxy review"],
          ["Downside ECL uplift", "53.85%", "Red > 50%", "RED - static scenario"],
          ["Critical control precision", "1.32%", "Red < 2%", "RED"]
        ]
      }
    ],
    alerts: [
      { tone: "red", text: "Latest observed bad rate increased 47 bps to 21.35%; ranking weakened and PSI rose to 0.127, requiring portfolio and model-risk diagnosis." },
      { tone: "red", text: "Stage 2 proxy share is materially elevated; interpretation must retain the broad proxy limitation documented in the IFRS 9-Style ECL & Stress Testing project." },
      { tone: "amber", text: "The 20% policy candidate reduces straight-through auto-approved EL by 49.96% but fails approval and manual-review capacity constraints; this is routing impact, not realised loss reduction." },
      { tone: "info", text: "Synthetic DPD, roll-rate and cure outputs demonstrate controls and dashboard behavior, not actual servicing performance." }
    ],
    decision: {
      finding: "Observed risk deteriorated in the latest eligible cohort. The 20% cutoff candidate improves approved bad rate and expected loss but approval falls 30.32 percentage points and manual-review workload rises about 150% versus baseline.",
      recommendation: "Do not roll out the 20% cutoff wholesale. Run a constrained pilot or redesign review/decline capacity, diagnose PSI drivers, and keep synthetic delinquency outside observed servicing claims."
    },
    charts: [],
    validation: {
      headline: "The analytical implementation, interactive dashboard and clean-package controls passed validation; evidence scope and limitations remain explicit.",
      cards: [
        { title: "Validation", text: "All 131 automated checks passed, including 12 substantive reconciliations." },
        { title: "Manifest", text: "253 release-manifested files passed size, SHA-256, unlisted-file and clean-extract controls." },
        { title: "Testing", text: "56 UAT, 25 SIT, 25 injected negative tests, 13 Excel reconciliations and 25 web checks passed." },
        { title: "Reproducibility", text: "The reference baseline was frozen before independent reruns; 12/12 integrity and path controls plus 9/9 deterministic output reconciliations passed; clean-extract validation passed." }
      ]
    },
    limitations: [
      "Observed layer is historical accepted/booked-account monitoring, not a live servicing platform.",
      "Monthly DPD, roll-rate and cure metrics are synthetic controls-testing evidence and do not represent observed servicing outcomes.",
      "The Credit Risk Decision Engine model, IFRS 9-Style ECL & Stress Testing outputs and Fraud Detection, Controls & Operational Risk indicators are frozen upstream evidence; this monitoring project does not retrain or independently validate them.",
      "No regulatory report, independent validation or organisational sign-off is claimed.",
      "Power BI is documented as a separate future workstream; the completed public interface is the interactive web dashboard."
    ],
    employerValues: [
      { title: "Portfolio diagnosis", text: "Bad rate, exposure, vintage, concentration, model, policy and ECL signals are integrated into one portfolio view." },
      { title: "Early warning governance", text: "Risk thresholds are converted into alerts, named owners, actions and committee decisions." },
      { title: "Technical control", text: "Executable SQL, formula-driven Excel and browser reporting reconcile across delivery surfaces with explicit evidence boundaries." }
    ],
    artifacts: [
      { label: "Open credit risk dashboard", type: "WEB", href: "dashboards/project-2/index.html", detail: "Seven-view interactive credit risk monitoring" },
      { label: "Credit Portfolio Monitoring README", type: "MD", href: "evidence/project-2/README.md", detail: "Scope, evidence and claim boundary" },
      { label: "Risk committee memo", type: "MD", href: "evidence/project-2/risk_committee_monitoring_memo.md", detail: "Breaches and management actions" },
      { label: "Validation report", type: "MD", href: "evidence/project-2/validation_report.md", detail: "Analytical, UAT/SIT, Excel, web and clean-extract controls" },
      { label: "Portfolio KPI summary", type: "CSV", href: "evidence/project-2/portfolio_kpi_summary.csv", detail: "Account, exposure, PD and EL evidence" },
      { label: "KRI status summary", type: "CSV", href: "evidence/project-2/kri_status_summary.csv", detail: "Threshold-level status board" }
    ],
    next: { href: "#artifacts", label: "Evidence pack", title: "Supporting evidence" }
  }
};
