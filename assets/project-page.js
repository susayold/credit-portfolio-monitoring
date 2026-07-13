(function () {
  "use strict";

  const root = document.getElementById("project-root");
  const projectId = document.body.dataset.projectId;
  const project = window.PORTFOLIO_PROJECTS && window.PORTFOLIO_PROJECTS[projectId];

  if (!root || !project) {
    if (root) {
      root.innerHTML = '<main class="container" style="padding:80px 0"><h1>Project page unavailable</h1><p>Return to <a href="index.html">the portfolio overview</a>.</p></main>';
    }
    return;
  }

  const escapeHtml = function (value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };

  const header = `
    <a class="skip-link" href="#main-content">Skip to project content</a>
    <div class="scroll-progress" data-scroll-progress aria-hidden="true"></div>
    <header class="site-header">
      <a class="brand" href="index.html" aria-label="Financial Risk Analytics Portfolio home">
        <span class="brand-mark" data-i18n-ignore>FR</span>
        <span class="brand-copy"><strong>Financial Risk Analytics</strong><small>Completed risk analytics project</small></span>
      </a>
      <button class="menu-button" type="button" data-menu-button aria-expanded="false" aria-label="Open navigation">
        <span></span><span></span><span></span>
      </button>
      <nav class="site-nav" data-site-nav aria-label="Primary navigation">
        <a href="#problem">Problem</a>
        <a href="#data">Data</a>
        <a href="#process">Process</a>
        <a href="#results">Results</a>
        <a href="#validation">Validation</a>
        <a href="#artifacts">Artifacts</a>
        <a href="#artifacts">Project files</a>
      </nav>
    </header>`;

  const metrics = project.metrics.map(function (metric) {
    return `<article><strong>${escapeHtml(metric.value)}</strong><span>${escapeHtml(metric.label)}</span></article>`;
  }).join("");

  const dataLayers = project.dataLayers.map(function (layer) {
    return `
      <article class="data-layer reveal">
        <span class="layer-meta">${escapeHtml(layer.meta)}</span>
        <h3>${escapeHtml(layer.title)}</h3>
        <p>${escapeHtml(layer.text)}</p>
      </article>`;
  }).join("");

  const formulas = project.formulas.map(function (formula) {
    return `
      <article class="formula-card reveal">
        <h3>${escapeHtml(formula.name)}</h3>
        <code>${escapeHtml(formula.expression)}</code>
        <p>${escapeHtml(formula.meaning)}</p>
        <span class="formula-use"><strong class="inline-label">Decision use:</strong> ${escapeHtml(formula.use)}</span>
      </article>`;
  }).join("");

  const process = project.process.map(function (step, index) {
    return `
      <article class="process-step reveal">
        <span class="step-number">${String(index + 1).padStart(2, "0")}</span>
        <div class="process-copy">
          <h3>${escapeHtml(step.title)}</h3>
          <p>${escapeHtml(step.text)}</p>
          <small><strong class="inline-label">Evidence:</strong> ${escapeHtml(step.evidence)}</small>
        </div>
      </article>`;
  }).join("");

  const tables = project.resultTables.map(function (table) {
    const headers = table.headers.map(function (headerCell) {
      return `<th scope="col">${escapeHtml(headerCell)}</th>`;
    }).join("");
    const rows = table.rows.map(function (row) {
      return `<tr>${row.map(function (cell) { return `<td>${escapeHtml(cell)}</td>`; }).join("")}</tr>`;
    }).join("");
    return `
      <div class="result-block reveal" style="margin-top:28px">
        <h3>${escapeHtml(table.title)}</h3>
        <p class="muted">${escapeHtml(table.note)}</p>
        <div class="result-table-wrap">
          <table class="result-table">
            <thead><tr>${headers}</tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>`;
  }).join("");

  const alerts = project.alerts.map(function (alert) {
    return `<li class="${escapeHtml(alert.tone)}">${escapeHtml(alert.text)}</li>`;
  }).join("");

  const charts = project.charts.map(function (chart) {
    return `
      <figure class="chart-card reveal">
        <button class="chart-button" type="button" data-expand-image="${escapeHtml(chart.src)}" data-image-alt="${escapeHtml(chart.alt)}" aria-label="Open chart: ${escapeHtml(chart.alt)}">
          <img src="${escapeHtml(chart.src)}" alt="${escapeHtml(chart.alt)}" loading="lazy">
        </button>
        <figcaption>${escapeHtml(chart.caption)}</figcaption>
      </figure>`;
  }).join("");

  const validationCards = project.validation.cards.map(function (card) {
    return `<article class="validation-card reveal"><h3>${escapeHtml(card.title)}</h3><p>${escapeHtml(card.text)}</p></article>`;
  }).join("");

  const limitations = project.limitations.map(function (item) {
    return `<li>${escapeHtml(item)}</li>`;
  }).join("");

  const employerValues = project.employerValues.map(function (item) {
    return `<article class="employer-card reveal"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.text)}</p></article>`;
  }).join("");

  const artifacts = project.artifacts.length ? project.artifacts.map(function (artifact) {
    return `
      <li>
        <a href="${escapeHtml(artifact.href)}">
          <span><strong>${escapeHtml(artifact.label)}</strong><small>${escapeHtml(artifact.detail)}</small></span>
          <span class="artifact-type" data-i18n-ignore>${escapeHtml(artifact.type)}</span>
        </a>
      </li>`;
  }).join("") : '<li><span class="muted">No validated public artifacts are claimed for this deferred or unfinished project.</span></li>';

  const heroAction = project.heroAction ? `
    <div class="hero-actions" style="margin-top:22px">
      <a class="button primary" href="${escapeHtml(project.heroAction.href)}">${escapeHtml(project.heroAction.label)}</a>
      <span class="muted">${escapeHtml(project.heroAction.detail)}</span>
    </div>` : "";

  const formulaSection = project.formulas.length ? `
    <section class="project-section" id="formulas">
      <p class="eyebrow">Analytical core</p>
      <h2>Formulas that drive the decision</h2>
      <p class="lead">Each formula is shown with its business meaning and the decision it supports. Tool choice is secondary to correct risk logic.</p>
      <div class="formula-grid">${formulas}</div>
    </section>` : "";

  const chartSection = project.charts.length ? `
    <section class="project-section" id="visuals">
      <p class="eyebrow">Visual evidence</p>
      <h2>What the analytical outputs show</h2>
      <p class="lead">Charts are generated from the analytical outputs. Select a chart to inspect the underlying result at full size.</p>
      <div class="chart-grid">${charts}</div>
    </section>` : "";

  const tocLinks = [
    ["problem", "Decision problem"],
    ["data", "Data"],
    ...(project.formulas.length ? [["formulas", "Formulas"]] : []),
    ["process", "Process"],
    ...(project.resultTables.length ? [["results", "Results"]] : []),
    ...(project.charts.length ? [["visuals", "Visuals"]] : []),
    ["validation", "Validation"],
    ["artifacts", "Artifacts"]
  ].map(function (item) { return `<a href="#${item[0]}">${item[1]}</a>`; }).join("");

  root.style.setProperty("--project-accent", project.accent);
  root.innerHTML = `
    ${header}
    <main id="main-content">
      <section class="project-hero" style="--project-accent:${escapeHtml(project.accent)}">
        <div class="container project-hero-grid">
          <div>
            <div class="project-kicker">
              <p class="eyebrow">${escapeHtml(project.category)}</p>
              <span class="status ${escapeHtml(project.statusClass)}">${escapeHtml(project.status)}</span>
            </div>
            <h1>${escapeHtml(project.title)}</h1>
            <p class="project-thesis">${escapeHtml(project.thesis)}</p>
            <div class="tag-list">${project.tags.map(function (tag) { return `<span class="tag">${escapeHtml(tag)}</span>`; }).join("")}</div>
            ${heroAction}
          </div>
        </div>
      </section>

      <section class="metric-rail" aria-label="Project headline evidence">${metrics}</section>

      <div class="project-shell">
        <aside class="project-toc" aria-label="Project contents">
          <strong>On this page</strong>
          <nav>${tocLinks}</nav>
        </aside>

        <div class="project-main">
          <section class="project-section" id="problem">
            <p class="eyebrow">Business problem</p>
            <h2>Decision supported by the analysis</h2>
            <blockquote class="decision-question">${escapeHtml(project.business.question)}</blockquote>
            <div class="three-up">
              <article class="info-block reveal"><h3>Why it matters</h3><p>${escapeHtml(project.business.context)}</p></article>
              <article class="info-block reveal"><h3>Analytical deliverables</h3><p>${escapeHtml(project.business.output)}</p></article>
              <article class="info-block reveal"><h3>Analytical approach</h3><p>${escapeHtml(project.employerValues[0].text)}</p></article>
            </div>
          </section>

          <section class="project-section" id="data">
            <p class="eyebrow">Population & evidence</p>
            <h2>Data architecture and claim boundary</h2>
            <p class="lead">The project distinguishes observed evidence, proxy assumptions, synthetic controls and reference data before any result is interpreted.</p>
            <div class="data-layer-grid">${dataLayers}</div>
          </section>

          ${formulaSection}

          <section class="project-section" id="process">
            <p class="eyebrow">End-to-end flow</p>
            <h2>How the project moves from source to decision</h2>
            <div class="process-list">${process}</div>
          </section>

          ${project.resultTables.length ? `
            <section class="project-section" id="results">
              <p class="eyebrow">Analytical results</p>
              <h2>Results, interpretation and management action</h2>
              ${tables}
              <h3 style="margin-top:34px">Material risk signals</h3>
              <ul class="alert-list">${alerts}</ul>
              <div class="decision-panel reveal">
                <div><h3>Risk assessment</h3><p>${escapeHtml(project.decision.finding)}</p></div>
                <div class="recommendation"><h3>Management recommendation</h3><p>${escapeHtml(project.decision.recommendation)}</p></div>
              </div>
            </section>` : `
            <section class="project-section" id="results">
              <p class="eyebrow">Current state</p>
              <h2>No result is claimed before implementation</h2>
              <ul class="alert-list">${alerts}</ul>
              <div class="decision-panel reveal">
                <div><h3>Risk assessment</h3><p>${escapeHtml(project.decision.finding)}</p></div>
                <div class="recommendation"><h3>Recommendation</h3><p>${escapeHtml(project.decision.recommendation)}</p></div>
              </div>
            </section>`}

          ${chartSection}

          <section class="project-section" id="validation">
            <p class="eyebrow">Control evidence</p>
            <h2>Validation and limitations</h2>
            <p class="lead">${escapeHtml(project.validation.headline)}</p>
            <div class="validation-grid">${validationCards}</div>
            <h3 style="margin-top:32px">Scope boundaries</h3>
            <ul>${limitations}</ul>
          </section>

          <section class="project-section" id="artifacts">
            <p class="eyebrow">Supporting analysis</p>
            <h2>Methods, controls and source outputs</h2>
            <p class="lead">Key conclusions are linked to the methodology, control reports and supporting summary data.</p>
            <ul class="artifact-list">${artifacts}</ul>
          </section>

          <section class="project-section" id="value">
            <p class="eyebrow">Analytical capabilities</p>
            <h2>Risk analysis and governance capabilities</h2>
            <div class="employer-grid">${employerValues}</div>
          </section>
        </div>
      </div>
      <section class="project-next" style="--project-accent:${escapeHtml(project.accent)}">
        <div class="container project-next-inner">
          <div><p class="eyebrow" style="color:rgba(255,255,255,.72)">Analytical documentation</p><h2>Review the complete methodology and results</h2><p>This repository contains the completed analysis, validation controls and supporting source outputs.</p></div>
          <a class="button" href="#artifacts">Review supporting analysis</a>
        </div>
      </section>
    </main>

    <footer class="site-footer">
      <div class="container footer-inner">
        <div class="footer-summary"><strong>Financial Risk Analytics Portfolio</strong><p>Independent analytical projects built on a governed data pool, with explicit evidence, assumptions and production-use boundaries.</p></div>
        <address class="footer-contact" id="contact">
          <span class="footer-contact-label">Contact</span>
          <strong data-i18n-ignore>Nguyễn Phạm Khôi Nguyên</strong>
          <a data-i18n-ignore href="tel:+84865385817">0865385817</a>
          <a data-i18n-ignore href="mailto:nguyen28052005@gmail.com">nguyen28052005@gmail.com</a>
        </address>
        <nav class="footer-links" aria-label="Footer navigation"><a href="#problem">Problem</a><a href="#results">Results</a><a href="#artifacts">Evidence</a><a href="README.md">README</a></nav>
      </div>
    </footer>

    <dialog class="image-dialog" data-image-dialog aria-label="Expanded project chart">
      <button class="dialog-close" type="button" data-dialog-close aria-label="Close image">X</button>
      <img src="" alt="">
    </dialog>`;
})();
