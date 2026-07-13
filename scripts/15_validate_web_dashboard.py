from __future__ import annotations

import csv
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard" / "index.html"
RESULTS = ROOT / "validation" / "web_dashboard_validation.csv"
REPORT = ROOT / "validation" / "web_dashboard_validation_report.md"


class DashboardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.nav_targets: list[str] = []
        self.view_ids: list[str] = []
        self.select_ids: list[str] = []
        self.labels_for: list[str] = []
        self.active_views = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            self.ids.append(element_id)
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        if tag == "button" and values.get("data-view"):
            self.nav_targets.append(str(values["data-view"]))
        if tag == "section" and "view" in str(values.get("class", "")).split():
            if element_id:
                self.view_ids.append(element_id)
            if "active" in str(values.get("class", "")).split():
                self.active_views += 1
        if tag == "select" and element_id:
            self.select_ids.append(element_id)
        if tag == "label" and values.get("for"):
            self.labels_for.append(str(values["for"]))


def main() -> None:
    html = DASHBOARD.read_text(encoding="utf-8")
    parser = DashboardParser()
    parser.feed(html)
    checks: list[dict[str, str]] = []

    def add(check_id: str, name: str, passed: bool, evidence: str) -> None:
        checks.append(
            {
                "check_id": check_id,
                "check_name": name,
                "status": "PASS" if passed else "FAIL",
                "evidence": evidence,
            }
        )

    required_views = ["executive", "portfolio", "model", "policy", "ecl", "governance", "evidence"]
    add("WEB-001", "Dashboard file exists", DASHBOARD.exists(), DASHBOARD.relative_to(ROOT).as_posix())
    add("WEB-002", "Substantive single-file report", len(html) > 30000, f"{len(html)} characters")
    add("WEB-003", "Seven governed report views", parser.view_ids == required_views, ", ".join(parser.view_ids))
    add("WEB-004", "Navigation matches report views", parser.nav_targets == required_views, ", ".join(parser.nav_targets))
    add("WEB-005", "One default active view", parser.active_views == 1, str(parser.active_views))
    add("WEB-006", "Unique element identifiers", len(parser.ids) == len(set(parser.ids)), f"{len(parser.ids)} ids")
    add("WEB-007", "Five policy scenarios", len(re.findall(r"\{id:'(?:baseline|scenario)_", html)) == 5, "baseline plus four scenarios")
    add("WEB-008", "Eight governed KRIs", len(re.findall(r"\{id:'KRI-\d{3}'", html)) == 8, "KRI-001 to KRI-008")
    add("WEB-009", "Five risk grades", len(re.findall(r"\{g:'[A-E] -", html)) == 5, "A to E")
    add("WEB-010", "Policy slicer contract", "policy-filter" in parser.select_ids, "policy-filter")
    add("WEB-011", "KRI status slicer contract", "status-filter" in parser.select_ids, "status-filter")
    add("WEB-012", "Owner slicer contract", "owner-filter" in parser.select_ids, "owner-filter")
    add("WEB-013", "Slicers have labels", set(["policy-filter", "status-filter", "owner-filter"]).issubset(set(parser.labels_for)), ", ".join(parser.labels_for))
    add("WEB-014", "Responsive desktop/tablet/mobile breakpoints", all(token in html for token in ["@media(max-width:1120px)", "@media(max-width:760px)", "@media(max-width:430px)"]), "1120, 760 and 430 px")
    add("WEB-015", "Observed/synthetic/proxy labels", all(token in html for token in ["Observed outcomes", "Synthetic servicing controls", "Proxy ECL"]), "three evidence roles")
    add("WEB-016", "Public claim boundary", "not a live bank system or organisational approval" in html, "explicit educational/non-production wording")
    add("WEB-017", "No author-local path in public HTML", not re.search(r"[A-Za-z]:\\", html), "no Windows absolute path")
    add("WEB-018", "No file URI embedded", "file://" not in html.lower(), "portable relative links")
    add("WEB-019", "Authoritative dashboard path", DASHBOARD.parent == ROOT / "dashboard", "dashboard/index.html")
    add("WEB-020", "Project landing page points to authoritative report", "dashboard/index.html" in (ROOT / "OPEN_THIS_FIRST.html").read_text(encoding="utf-8"), "OPEN_THIS_FIRST.html")

    missing_links: list[str] = []
    for href in parser.hrefs:
        if href.startswith(("http://", "https://", "#")):
            continue
        target = (DASHBOARD.parent / href.split("?", 1)[0]).resolve()
        if not target.exists():
            missing_links.append(href)
    add("WEB-021", "All local dashboard links resolve", not missing_links, ", ".join(missing_links) or "all resolved")

    script_matches = re.findall(r"<script>(.*?)</script>", html, flags=re.DOTALL | re.IGNORECASE)
    js_ok = False
    js_evidence = "inline script not found"
    if script_matches:
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
            handle.write(script_matches[-1])
            temp_path = Path(handle.name)
        try:
            result = subprocess.run(["node", "--check", str(temp_path)], capture_output=True, text=True, check=False)
            js_ok = result.returncode == 0
            js_evidence = "node --check PASS" if js_ok else (result.stderr.strip() or "node --check failed")
        finally:
            temp_path.unlink(missing_ok=True)
    add("WEB-022", "Inline JavaScript syntax", js_ok, js_evidence)

    required_numbers = ["1,347,681", "1,291,521", "673,840", "21.35%", "0.597", "0.127", "108.57M", "118.65M", "131 / 131"]
    add("WEB-023", "Governed headline values represented", all(value in html for value in required_numbers), ", ".join(required_numbers))
    add("WEB-024", "Interactive reset and filter handlers", all(token in html for token in ["reset-btn", "filter-toggle", "renderPolicy()", "renderKri()"]), "filter/reset render functions")
    add("WEB-025", "Evidence drill contract", "showEvidence" in html and "evidence-detail" in html, "KRI row to source/impact/boundary")

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check_id", "check_name", "status", "evidence"])
        writer.writeheader()
        writer.writerows(checks)

    passed = sum(row["status"] == "PASS" for row in checks)
    report = [
        "# Web Dashboard Validation Report",
        "",
        f"- Status: **{'PASS' if passed == len(checks) else 'FAIL'}**",
        f"- Checks passed: **{passed}/{len(checks)}**",
        "- Scope: static structure, interaction contracts, local links, claim wording and JavaScript syntax.",
        "- Boundary: visual/pixel validation still requires opening the local HTML in a browser.",
        "",
        "| Check | Result | Evidence |",
        "| --- | --- | --- |",
    ]
    report.extend(f"| {row['check_id']} {row['check_name']} | {row['status']} | {row['evidence']} |" for row in checks)
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"{'PASS' if passed == len(checks) else 'FAIL'}: {passed}/{len(checks)} web dashboard checks")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
