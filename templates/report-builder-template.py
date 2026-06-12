"""
report-builder-template.py -- minimal reference builder for an HTML results report.
====================================================================================

Copy this file to ``code/python/build_<topic>_report_v1.py`` and adapt it. It is
intentionally small and heavily commented: it shows the *canonical skeleton* every
report builder in this project should follow. All look-and-feel lives in
``code/python/report_lib.py`` -- this file only (a) reads results, (b) decides which
cells/tables to render, and (c) writes + verifies the HTML.

What it does
------------
1. Reads a results CSV (schema documented below).
2. Builds ONE heat-grid (focal t-stat per DV x horizon), each cell clickable.
3. Builds the full AEA tables (focal terms + a Controls block), one per
   DV x horizon, each with an ``id`` matching its heat cell's link.
4. Writes the HTML and runs ``report_lib.verify_anchor_links`` (fails loudly on
   any broken/orphan anchor) -- the clickable-heatmap guarantee.

Run it (writes a demo report next to this file the first time, using the bundled
sample CSV if no real CSV is found)::

    python templates/report-builder-template.py

------------------------------------------------------------------------------
RESULTS CSV SCHEMA  (one row per regression; extra columns are ignored)
------------------------------------------------------------------------------
    test       short test name, e.g. "ReturnPricing"      (str)
    dv         dependent-variable key, e.g. "ret"          (str)
    horizon    horizon key, e.g. "F0","F1","cum6","1Q"     (str)
    sample     sample label, e.g. "Full","Subsample"       (str)
    fe         fixed-effects label, e.g. "Ind+YM"          (str)
    cluster    cluster label, e.g. "Firm"                  (str)
    sentiment  shock variant, e.g. "anti","pro","net"      (str)
    N          observation count                           (int)
    r2         adjusted R^2                                 (float)
    focal_b    focal interaction coef (Treat x dShock)     (float)
    focal_t    focal interaction 1-way t-stat              (float)
    focal_t2   focal interaction 2-way t-stat (optional)   (float; blank ok)
    treat_b    Treat main-effect coef (optional)           (float; blank ok)
    treat_t    Treat main-effect t-stat (optional)         (float; blank ok)
    ctrl_*_b / ctrl_*_t   any number of control columns,   (float; blank ok)
                          e.g. ctrl_size_b, ctrl_size_t,
                          ctrl_btm_b, ctrl_btm_t, ...
------------------------------------------------------------------------------
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

# --- Locate report_lib regardless of where this template is copied to. --------
# When copied to code/python/, report_lib sits beside it. When run in place from
# templates/, report_lib is one dir up under code/python/.
ROOT = Path(__file__).resolve().parent.parent  # project root (templates/ -> root)
for cand in (Path(__file__).resolve().parent, ROOT / "code" / "python"):
    if (cand / "report_lib.py").exists():
        sys.path.insert(0, str(cand))
        break
import report_lib as R  # noqa: E402

# --- Paths (edit these for a real builder). -----------------------------------
RESULTS_CSV = ROOT / "output" / "results" / "report_results.csv"
OUT_HTML = ROOT / "output" / "ResultsReport_v1.html"

# --- Display config: order + pretty labels (edit for your project). -----------
DVS = [("ret", "Size/industry-adj. return"),
       ("vol", "Return volatility")]
HORIZONS = [("F0", "Month 0"), ("F1", "Month +1"), ("cum6", "Cum [0,+6]")]
SAMPLE = "Full"          # the one manuscript-spec sample shown in main tables
SENTIMENT = "anti"       # focal shock channel for the headline heatmap

# Pretty labels for control columns, keyed by the slug in ctrl_<slug>_b/_t.
CTRL_LABELS = {"size": "Size", "btm": "BTM", "roa": "ROA",
               "ag": "Asset growth", "mom": "Past 12-mo return",
               "vol": "Return volatility"}


# ------------------------------------------------------------------------------
# CSV loading + lookup helpers
# ------------------------------------------------------------------------------
def load_rows(path: Path) -> list[dict]:
    """Read the results CSV into a list of dict rows (strings preserved)."""
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return [{k.strip(): (v.strip() if v else "") for k, v in r.items()}
                for r in csv.DictReader(fh)]


def find(rows: list[dict], **filt) -> dict | None:
    """First row matching all key==value filters (string compare)."""
    for r in rows:
        if all(str(r.get(k, "")) == str(v) for k, v in filt.items()):
            return r
    return None


def control_rows_from(rec: dict) -> list[dict]:
    """Build aea_table control rows from any ctrl_<slug>_b / ctrl_<slug>_t pairs."""
    slugs = sorted({k[len("ctrl_"):-2] for k in rec
                    if k.startswith("ctrl_") and k.endswith("_b")})
    out = []
    for slug in slugs:
        b, t = rec.get(f"ctrl_{slug}_b"), rec.get(f"ctrl_{slug}_t")
        if b in (None, "") and t in (None, ""):
            continue
        out.append({"label": CTRL_LABELS.get(slug, slug), "control": True,
                    "cells": [{"b": b, "t": t}]})
    return out


# ------------------------------------------------------------------------------
# Section builders
# ------------------------------------------------------------------------------
def build_heatmap(rows: list[dict]) -> str:
    """One heat table per DV; columns = horizons; each cell links to its table.

    The anchor id is built from (dv, horizon, SAMPLE) -- the SAME keys used by
    the full table below -- so report_lib.verify_anchor_links sees them paired.
    """
    heat_tables = []
    for dv_key, dv_lab in DVS:
        head = "<tr><th>DV \\ Horizon</th>" + "".join(
            f"<th>{hl}</th>" for _, hl in HORIZONS) + "</tr>\n"
        body = f'<tr><td class="var">{dv_lab}</td>'
        for hz_key, _ in HORIZONS:
            rec = find(rows, dv=dv_key, horizon=hz_key, sample=SAMPLE,
                       sentiment=SENTIMENT)
            t = rec.get("focal_t") if rec else None
            anchor = R.anchor_id(dv_key, hz_key, SAMPLE)  # matches table id
            body += R.hcell(t, anchor=anchor)
        body += "</tr>"
        heat_tables.append(
            f'<table class="heat"><caption>Focal: Treat &times; &Delta;Shock '
            f'&mdash; {dv_lab}</caption>\n{head}{body}</table>')
    return R.heat_grid(heat_tables)


def build_full_tables(rows: list[dict]) -> str:
    """Full clickable AEA tables (focal + Controls), one per DV x horizon."""
    blocks = ['<div class="aea-grid">']
    for dv_key, dv_lab in DVS:
        for hz_key, hz_lab in HORIZONS:
            rec = find(rows, dv=dv_key, horizon=hz_key, sample=SAMPLE,
                       sentiment=SENTIMENT)
            if not rec:
                continue
            dual = bool(rec.get("focal_t2"))  # show [t2] if a 2-way t is present
            focal_rows = []
            if rec.get("treat_b") not in (None, ""):
                focal_rows.append({"label": "Treat", "hi": True,
                                   "cells": [{"b": rec.get("treat_b"),
                                              "t": rec.get("treat_t")}]})
            focal_rows.append({
                "label": "Treat &times; &Delta;Shock", "hi": True,
                "cells": [{"b": rec.get("focal_b"), "t": rec.get("focal_t"),
                           "t2": rec.get("focal_t2")}]})
            tbl = R.aea_table(
                caption=f"{dv_lab} &mdash; {hz_lab} ({SAMPLE})",
                anchor=R.anchor_id(dv_key, hz_key, SAMPLE),
                columns=[f"(1) {SAMPLE}"],
                dual_cluster=dual,
                rows=focal_rows + control_rows_from(rec),
                n=rec.get("N"), r2=rec.get("r2"),
                notes=(f"DV: {dv_lab}. Firm-month panel. FE: {rec.get('fe','Ind+YM')}. "
                       f"Cluster: {rec.get('cluster','Firm')}. &Delta;Shock is a "
                       "standardized one-period change (not a level)."
                       + (" 2-way (firm+time) t in [brackets]." if dual else "")
                       + " * p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01; "
                       "t-statistics in parentheses. Shaded = focal terms."),
            )
            blocks.append(tbl)
    blocks.append("</div>")
    return "\n".join(blocks)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main() -> None:
    rows = load_rows(RESULTS_CSV)
    if not rows:
        # No real CSV present -> fall back to a tiny bundled sample so the
        # template runs end-to-end out of the box. Delete this branch in a
        # real builder (you always have a results CSV).
        rows = _sample_rows()
        print(f"[note] {RESULTS_CSV} not found; using bundled sample rows.")

    today = date.today().strftime("%B %d, %Y")
    n_focal = sum(1 for r in rows if r.get("sample") == SAMPLE
                  and r.get("sentiment") == SENTIMENT)

    html = (
        R.html_head("Results Report v1")
        + "<h1>Results Report</h1>\n"
        + f'<p class="sub">{today} &nbsp;|&nbsp; {len(rows)} regressions '
          f'&nbsp;|&nbsp; commit [SHA] &nbsp;|&nbsp; branch [name]</p>\n'
        # 1) Executive-summary finding box (fill with the headline).
        + R.finding_box("<strong>Headline:</strong> the focal "
                        "Treat &times; &Delta;Shock interaction is the object of "
                        "interest; scan the heatmap, click any cell for the full table.")
        # 2) TOC.
        + R.toc([("vars", "1. Variable definitions"),
                 ("heat", "2. Heatmap"),
                 ("model", "3. Model"),
                 ("tables", "4. Full tables"),
                 ("guide", "5. Reading guide"),
                 ("caveats", "6. Caveats")])
        # 3) Variable definitions.
        + '<h2 id="vars">1. Variable definitions</h2>\n'
        + '<p>Treat = focal firm characteristic (e.g. above-median exposure). '
          '&Delta;Shock = standardized one-period change in the conditioning '
          'series. Controls: Size, BTM, ROA, asset growth, past 12-mo return, '
          'return volatility.</p>\n'
        # 4) Heatmaps.
        + '<h2 id="heat">2. Heatmap</h2>\n'
        + build_heatmap(rows)
        # 5) Model spec.
        + '<h2 id="model">3. Model</h2>\n'
        + R.model_box(
            "Y<sub>i,t&rarr;t+h</sub> = &beta;<sub>1</sub> Treat<sub>i</sub> "
            "+ &beta;<sub>2</sub> Treat &times; &Delta;Shock<sub>t</sub> "
            "+ &gamma;'Controls + &alpha;<sub>ind</sub> + &delta;<sub>t</sub> "
            "+ &epsilon;<sub>i,t</sub><br>"
            "Industry + year-month FE; cluster(firm); levels (changes are robustness).")
        # 6) Full AEA tables (clickable from the heatmap).
        + '<h2 id="tables">4. Full tables</h2>\n'
        + build_full_tables(rows)
        # 7) Reading guide.
        + '<h2 id="guide">5. Reading guide</h2>\n'
        + R.finding_box(
            "Green = positive, red = negative; darker = more significant "
            "(|t| &ge; 1.645 / 1.96 / 2.576). A signal is robust if the 1-way "
            "(t) and 2-way [t] both clear conventional thresholds. With many "
            "cells, treat marginal single-cell hits as multiple-testing noise.")
        # 8) Caveats + provenance footer.
        + '<h2 id="caveats">6. Caveats</h2>\n'
        + '<ul><li>Inference: firm-clustered (Petersen 2009 RFS); 2-way '
          'firm+time as robustness (Cameron-Gelbach-Miller 2011).</li>'
          '<li>Standardized &Delta;Shock; coefficients are per-SD.</li></ul>\n'
        + R.provenance_footer({
            "built": today, "commit": "[SHA]", "branch": "[name]",
            "results": str(RESULTS_CSV.relative_to(ROOT)),
            "script": Path(__file__).name})
        + R.html_tail()
    )

    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(html, encoding="utf-8")

    # MANDATORY: clickable-heatmap guarantee -- fails loudly on any broken/orphan.
    counts = R.verify_anchor_links(OUT_HTML)
    print(f"Wrote {OUT_HTML}")
    print(f"Anchors: {counts['links']} links / {counts['ids']} ids "
          f"(broken={len(counts['broken'])}, orphans={len(counts['orphans'])})")
    print(f"Focal regressions shown: {n_focal}")


def _sample_rows() -> list[dict]:
    """Tiny bundled sample so the template runs without a real CSV."""
    base = dict(test="ReturnPricing", sample=SAMPLE, fe="Ind+YM",
                cluster="Firm", sentiment=SENTIMENT, N="189036", r2="0.016",
                treat_b="0.0150", treat_t="2.99",
                ctrl_size_b="-0.0015", ctrl_size_t="-4.31",
                ctrl_btm_b="0.0078", ctrl_btm_t="5.51",
                ctrl_roa_b="0.0151", ctrl_roa_t="4.58")
    cells = {("ret", "F0"): ("-0.0031", "-2.83", "-2.41"),
             ("ret", "F1"): ("-0.0012", "-1.40", "-1.05"),
             ("ret", "cum6"): ("-0.0044", "-3.10", "-2.62"),
             ("vol", "F0"): ("0.0021", "1.80", "1.33"),
             ("vol", "F1"): ("0.0008", "0.60", "0.41"),
             ("vol", "cum6"): ("0.0030", "2.20", "1.71")}
    rows = []
    for (dv, hz), (b, t, t2) in cells.items():
        r = dict(base, dv=dv, horizon=hz, focal_b=b, focal_t=t, focal_t2=t2)
        rows.append(r)
    return rows


if __name__ == "__main__":
    main()
