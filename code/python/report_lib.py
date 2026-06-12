"""
report_lib.py -- Reusable HTML research-report module (manuscript look).
=========================================================================

A small, **stdlib-only** library for assembling publication-style HTML results
reports for empirical-finance / accounting projects. It is the single source of
truth for the report *look*, so every report a project produces is visually and
structurally consistent.

Design goals
------------
1. **Mirror the LaTeX manuscript.** The embedded CSS uses a serif body font
   (Georgia / Times New Roman), *booktabs-style horizontal rules only* (top /
   mid / bottom borders -- NO vertical lines), an AEA-style ``\\textit{Notes:}``
   block under each table, two-line ``coef`` / ``(t)`` cells, true minus signs,
   and significance stars. A reader who knows the paper recognises the tables.
2. **Enforce conventions in code, not prose.** Sign x significance shading,
   the |t| thresholds (1.645 / 1.96 / 2.576), the dual-cluster ``(t)`` / ``[t]``
   cell, the clickable heatmap -> table anchor scheme, and the bidirectional
   anchor verifier all live here so individual builders cannot drift.
3. **No heavy dependencies.** Accepts plain Python lists / dicts. ``pandas`` /
   ``numpy`` are *not* required to import or use this module (a builder may use
   them upstream to read a CSV, but the rendering layer is pure stdlib).

Public surface
--------------
Formatting / classification:
    ``sig_class(t, cell=False)``  -- CSS class from |t| thresholds (+ sign).
    ``stars(t_or_p)``             -- significance stars from a t-stat or p-value.

Cells / grids:
    ``hcell(t, anchor=None)``     -- one heat-map ``<td>`` (optionally a link).
    ``heat_grid(tables_html)``    -- wrap heat tables in a responsive grid.
    ``aea_table(...)``            -- a full regression table (focal + controls).

Page scaffolding / callouts:
    ``html_head(title)`` / ``html_tail()``
    ``anchor_id(*keys)``          -- stable, sanitized anchor id.
    ``finding_box`` / ``model_box`` / ``toc`` / ``provenance_footer``

Verification:
    ``verify_anchor_links(html_path)`` -- assert no broken / orphan anchors.

Anchor contract
---------------
Report anchors carry a stable prefix (``ANCHOR_PREFIX``, default ``"tab_"``) so
``verify_anchor_links`` checks *only* report tables and ignores incidental page
ids. Build every clickable table's id with ``anchor_id(...)`` and pass the same
id to ``hcell(anchor=...)``; the verifier then guarantees every heat cell links
to a real table and every table is reachable from a heat cell.

Run ``python code/python/report_lib.py`` to execute the built-in smoke test,
which assembles a tiny 2-DV demo report and verifies its anchors.
"""

from __future__ import annotations

import html as _html
import re
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence, Union

__all__ = [
    "CSS",
    "ANCHOR_PREFIX",
    "sig_class",
    "stars",
    "hcell",
    "heat_grid",
    "anchor_id",
    "aea_table",
    "finding_box",
    "model_box",
    "toc",
    "provenance_footer",
    "html_head",
    "html_tail",
    "verify_anchor_links",
]

# Stable prefix for every *report table* anchor. verify_anchor_links() only
# inspects ids/hrefs that start with this, so unrelated page anchors are ignored.
ANCHOR_PREFIX = "tab_"

# t-stat significance thresholds (two-sided normal): 10% / 5% / 1%.
_T10, _T5, _T1 = 1.645, 1.960, 2.576

# ---------------------------------------------------------------------------
# Embedded CSS -- mirrors the LaTeX manuscript (serif, booktabs rules, AEA notes)
# ---------------------------------------------------------------------------
CSS = """
/* ===== Manuscript look: serif body, booktabs rules, AEA notes ===== */
body { font-family: Georgia, 'Times New Roman', serif;
       max-width: 1400px; margin: 24px auto; padding: 0 28px;
       background: #fff; color: #1a1a1a; font-size: 13px; line-height: 1.55; }
h1 { font-size: 23px; margin: 0 0 2px 0; font-weight: 600; letter-spacing: .2px; }
h2 { font-size: 16px; border-bottom: 2px solid #222; padding-bottom: 4px;
     margin-top: 34px; font-weight: 600; }
h3 { font-size: 13px; margin: 20px 0 6px 0; font-weight: 600; }
.sub { font-size: 11.5px; color: #666; margin-top: 0; }
p, li { font-size: 13px; }

/* ----- AEA / booktabs regression tables: HORIZONTAL rules only ----- */
table.aea { border-collapse: collapse; font-size: 11.5px; margin: 10px 0 6px 0;
            border: none; }
table.aea th, table.aea td { padding: 3px 9px; text-align: center; border: none; }
table.aea th.varh, table.aea td.var { text-align: left; font-style: italic; }
table.aea td.ctrl { font-style: normal; color: #333; }
/* booktabs equivalents: \\toprule \\midrule \\bottomrule */
table.aea tr.top th  { border-top: 1.6px solid #222; border-bottom: .8px solid #222;
                        font-weight: 600; }     /* toprule + header midrule */
table.aea tr.head th { border-bottom: .8px solid #888; font-weight: 400; }
table.aea tr.ctrlsep td { border-top: .6px solid #ccc; }   /* faint rule before Controls */
table.aea tr.sep td  { border-top: .8px solid #999; }      /* midrule before N */
table.aea tr.bot td  { border-bottom: 1.6px solid #222; }  /* bottomrule */
table.aea caption { text-align: left; font-size: 12px; font-weight: 600;
                    margin-bottom: 4px; }
.coef { white-space: nowrap; }
.st  { color: #b00; }                                  /* significance stars */
.ts  { color: #777; font-size: 10px; }                 /* 1-way (t) */
.ts2 { color: #555; font-size: 10px; font-family: 'Courier New', monospace; } /* 2-way [t] */

/* AEA focal-cell shading: green=positive, red=negative; lighter = less sig.
   Whole cell is tinted (lighter than heat shades so two-line text stays legible). */
.aea-pos3 { background: #6cd095; }   /* +, 1%  */
.aea-pos2 { background: #a8e0bb; }   /* +, 5%  */
.aea-pos1 { background: #d6efe0; }   /* +, 10% */
.aea-pos0 { background: #f0f8f3; }   /* +, ns  */
.aea-neg3 { background: #f29ca5; }   /* -, 1%  */
.aea-neg2 { background: #f8c4c9; }   /* -, 5%  */
.aea-neg1 { background: #fbe0e3; }   /* -, 10% */
.aea-neg0 { background: #fdf3f4; }   /* -, ns  */

/* AEA "Notes:" block under a table (mirrors \\textit{Notes:} in threeparttable) */
.note { font-size: 10.5px; color: #444; margin: 2px 0 16px 0; line-height: 1.45;
        max-width: 720px; }
.note em { font-style: italic; }

/* ----- Heat-map tables (one t-stat per cell, color-coded) ----- */
table.heat { border-collapse: collapse; font-size: 11px; margin: 0; border: none; }
table.heat th, table.heat td { padding: 4px 7px; border: 1px solid #e2e2e2;
                                text-align: center; white-space: nowrap; }
table.heat th { background: #f5f5f5; font-weight: 600; font-size: 10.5px; }
table.heat td.var { text-align: left; font-style: italic; background: #fafafa;
                     font-size: 10.5px; }
table.heat caption { font-size: 11px; font-weight: 600; margin-bottom: 3px;
                     text-align: left; }
.pos3 { background: #1a7431; color: #fff; }   /* t >= 2.576 (1%)  */
.pos2 { background: #28a745; color: #fff; }   /* t >= 1.96  (5%)  */
.pos1 { background: #8fd19e; }                /* t >= 1.645 (10%) */
.neg3 { background: #a71d2a; color: #fff; }
.neg2 { background: #dc3545; color: #fff; }
.neg1 { background: #f5a3a9; }
.ns   { background: #fff; color: #999; font-size: 10px; }  /* show t for transparency */
.fail { background: #f5f5f5; color: #ccc; }                /* missing / non-PSD */

/* ----- Responsive grids: pack 2-3 tables per row ----- */
.heat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(560px, 1fr));
             gap: 12px 16px; margin: 6px 0 18px 0; }
.heat-grid > table.heat { margin: 0; }
.aea-grid  { display: grid; grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
             gap: 10px 14px; margin: 6px 0 16px 0; }
.aea-grid  > table.aea { margin: 0; }

/* ----- Clickable heat-cell -> table anchors ----- */
a.hlink { color: inherit; text-decoration: none; display: block; }
a.hlink:hover { text-decoration: underline; opacity: .88; }
table.aea:target { outline: 2px solid #56a; outline-offset: 3px; background: #f7faff; }

/* ----- Callout boxes & nav ----- */
.model    { background: #f8f9fa; border: 1px solid #ddd; padding: 10px 16px;
            margin: 10px 0; font-size: 12px; }
.finding  { background: #f0f7f0; border-left: 3px solid #2a7; padding: 9px 14px;
            margin: 12px 0; font-size: 12.5px; }
.shape-guide { background: #eef3fb; border-left: 3px solid #4670c0; padding: 9px 14px;
               margin: 12px 0; font-size: 12.5px; }
.correction { background: #fdf3ec; border-left: 3px solid #d9822b; padding: 9px 14px;
              margin: 12px 0; font-size: 12.5px; }
.note-box { background: #fafafa; border-left: 3px solid #bbb; padding: 8px 14px;
            margin: 10px 0; font-size: 12px; color: #444; }
.toc { background: #fafafa; border: 1px solid #ddd; padding: 12px 20px;
       margin: 14px 0; font-size: 12.5px; }
.toc a { display: block; margin: 2px 0; }
a { color: #1a1a1a; }
a:hover { text-decoration: underline; }
details { margin: 6px 0; }
summary { cursor: pointer; font-weight: 600; padding: 3px 0; font-size: 12px; }
.foot { margin-top: 40px; padding-top: 12px; border-top: 1px solid #ccc;
        font-size: 10.5px; color: #777; line-height: 1.5; }
"""


# ---------------------------------------------------------------------------
# Numeric helpers
# ---------------------------------------------------------------------------
def _to_float(v) -> Optional[float]:
    """Coerce a value to float, returning None for blanks / sentinels."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        return None if f != f else f  # drop NaN
    s = str(v).strip()
    if s in ("", ".", "NA", "NaN", "nan", "FAILED", "."):
        return None
    try:
        f = float(s)
        return None if f != f else f
    except ValueError:
        return None


def sig_class(t: Optional[float], *, cell: bool = False) -> str:
    """Return the CSS color class for a t-stat from its sign and |t|.

    Thresholds (two-sided normal): 1.645 (10%), 1.96 (5%), 2.576 (1%).

    Parameters
    ----------
    t :
        The t-statistic. ``None`` / non-numeric -> ``"fail"`` (heat) or
        ``"aea-pos0"`` is *not* used; for cells a missing t yields ``""``.
    cell :
        When ``False`` (default) return a heat-map class
        (``pos3/2/1``, ``neg3/2/1``, ``ns``, ``fail``).
        When ``True`` return the lighter AEA focal-cell shade
        (``aea-pos3/2/1/0``, ``aea-neg3/2/1/0``).

    Examples
    --------
    >>> sig_class(3.1)
    'pos3'
    >>> sig_class(-2.0)
    'neg2'
    >>> sig_class(0.4)
    'ns'
    >>> sig_class(0.4, cell=True)
    'aea-pos0'
    >>> sig_class(-3.0, cell=True)
    'aea-neg3'
    """
    f = _to_float(t)
    if f is None:
        return "" if cell else "fail"
    at = abs(f)
    sign = "pos" if f >= 0 else "neg"
    if at >= _T1:
        lvl = 3
    elif at >= _T5:
        lvl = 2
    elif at >= _T10:
        lvl = 1
    else:
        lvl = 0
    if cell:
        return f"aea-{sign}{lvl}"
    return "ns" if lvl == 0 else f"{sign}{lvl}"


def stars(t_or_p: Optional[float], *, is_pvalue: bool = False) -> str:
    """Significance stars from a t-statistic (default) or a p-value.

    ``*`` p<0.10, ``**`` p<0.05, ``***`` p<0.01. For a t-stat the |t|
    thresholds 1.645 / 1.96 / 2.576 are used.

    >>> stars(2.0)
    '**'
    >>> stars(0.03, is_pvalue=True)
    '**'
    >>> stars(None)
    ''
    """
    f = _to_float(t_or_p)
    if f is None:
        return ""
    if is_pvalue:
        if f < 0.01:
            return "***"
        if f < 0.05:
            return "**"
        if f < 0.10:
            return "*"
        return ""
    at = abs(f)
    if at >= _T1:
        return "***"
    if at >= _T5:
        return "**"
    if at >= _T10:
        return "*"
    return ""


# ---------------------------------------------------------------------------
# Heat-map cells & grid
# ---------------------------------------------------------------------------
def hcell(t: Optional[float], anchor: Optional[str] = None, *, fmt: str = ".2f") -> str:
    """Render one heat-map ``<td>``: color-coded by sign x significance.

    The t-stat is shown even when non-significant (``ns``) for transparency,
    and a missing t renders a gray ``.`` (``fail``).

    Parameters
    ----------
    t :
        The t-statistic for the cell.
    anchor :
        If given, the cell content is wrapped in
        ``<a class="hlink" href="#{anchor}">`` so the reader can click through
        to the matching full table. Pair this with an ``aea_table`` whose
        ``anchor`` is the same id (build both from :func:`anchor_id`).
    fmt :
        Python format spec for the t-stat (default two decimals).

    >>> hcell(3.1, fmt='.2f')
    '<td class="pos3">3.10***</td>'
    >>> hcell(None)
    '<td class="fail">.</td>'
    >>> 'href="#tab_x"' in hcell(2.0, anchor='tab_x')
    True
    """
    f = _to_float(t)
    if f is None:
        return '<td class="fail">.</td>'
    cls = sig_class(f)
    content = f"{format(f, fmt)}{stars(f)}"
    if anchor:
        content = (f'<a class="hlink" href="#{_html.escape(anchor, quote=True)}" '
                   f'title="Jump to full table">{content}</a>')
    return f'<td class="{cls}">{content}</td>'


def heat_grid(tables_html: Sequence[str]) -> str:
    """Wrap a sequence of heat-table HTML strings in a ``.heat-grid`` div.

    The CSS grid packs 2-3 tables per row (``minmax(560px, 1fr)``), wrapping
    responsively. Empty / falsy entries are skipped.

    >>> heat_grid(['<table class="heat"></table>']).startswith('<div class="heat-grid">')
    True
    """
    inner = "\n".join(t for t in tables_html if t)
    return f'<div class="heat-grid">\n{inner}\n</div>\n'


# ---------------------------------------------------------------------------
# Anchors
# ---------------------------------------------------------------------------
def anchor_id(*keys: object) -> str:
    """Build a stable, sanitized anchor id from join keys.

    Joins the keys with ``_`` after the module prefix and replaces any
    character outside ``[A-Za-z0-9_]`` with ``_`` so the id is a valid HTML
    fragment. Use the SAME keys (in the same order) for a heat cell's
    ``anchor=`` and its full table's ``anchor=`` so the two link up.

    >>> anchor_id('Full', 'L1', 'ret', 'F0')
    'tab_Full_L1_ret_F0'
    >>> anchor_id('B/M', 'F+1')
    'tab_B_M_F_1'
    """
    raw = "_".join(str(k) for k in keys)
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", raw).strip("_")
    return f"{ANCHOR_PREFIX}{safe}"


# ---------------------------------------------------------------------------
# Full AEA regression table
# ---------------------------------------------------------------------------
def _fmt_coef(b: Optional[float], t: Optional[float], fmt: str) -> str:
    """Coefficient + significance stars (top line of an AEA cell)."""
    bf = _to_float(b)
    if bf is None:
        return "&nbsp;"
    return f'{format(bf, fmt)}<span class="st">{stars(t)}</span>'


def _fmt_t(t: Optional[float], *, two_way: bool = False) -> str:
    """A parenthesised (1-way) or bracketed (2-way) t-stat line, or blank."""
    tf = _to_float(t)
    if tf is None:
        return ""
    if two_way:
        return f'<span class="ts2">[{tf:.2f}]</span>'
    return f'<span class="ts">({tf:.2f})</span>'


def _aea_cell(b, t, *, hi: bool, dual_cluster: bool, t2=None, fmt: str) -> str:
    """One AEA ``<td>``: coef+stars on top, ``(t)`` (and optional ``[t2]``) below.

    ``hi=True`` shades the whole cell by sign x significance (focal rows).
    A fully empty (b, t) renders an empty cell (used for column gaps).
    """
    bf, tf = _to_float(b), _to_float(t)
    if bf is None and tf is None:
        return "<td></td>"
    cls = f' class="{sig_class(tf, cell=True)}"' if (hi and tf is not None) else ""
    top = _fmt_coef(b, t, fmt)
    t_line = _fmt_t(t)
    if dual_cluster:
        t2_line = _fmt_t(t2, two_way=True)
        sep = "&nbsp;" if (t_line and t2_line) else ""
        below = f"{t_line}{sep}{t2_line}"
    else:
        below = t_line
    return f'<td{cls}><span class="coef">{top}</span><br>{below}</td>'


def aea_table(
    *,
    caption: str,
    rows: Sequence[Mapping[str, object]],
    notes: str = "",
    anchor: Optional[str] = None,
    dual_cluster: bool = False,
    columns: Optional[Sequence[str]] = None,
    n: Optional[Union[int, Sequence[Optional[int]]]] = None,
    r2: Optional[Union[float, Sequence[Optional[float]]]] = None,
    fmt: str = ".4f",
) -> str:
    """Render a full AEA-style regression table (focal terms + Controls block).

    Layout (matches the LaTeX manuscript table): a booktabs *toprule*, an
    optional numbered/labeled column header, the focal/hypothesis rows at the
    top (shaded by sign x significance), a faint rule, a labeled **Controls**
    block, a *midrule*, then ``N`` and ``Adj. R^2`` rows, and a *bottomrule*.
    Each estimate is two lines: coefficient + stars on top, ``(t)`` below
    (and ``[t2]`` if ``dual_cluster``). t-statistics in parentheses -- never SE.

    Parameters
    ----------
    caption :
        Table caption (already HTML; render Greek/operators with entities,
        e.g. ``&Delta;``, ``&times;``, ``&minus;``). State the DV here.
    rows :
        Ordered list of row dicts. Recognised keys:

        ============  =================================================
        ``label``     row label (left col; HTML ok, e.g. ``Treat &times; &Delta;Shock``)
        ``cells``     list of per-column dicts, each with ``b`` and ``t``
                      (and ``t2`` when ``dual_cluster=True``); use ``{}`` for
                      a blank/empty cell (column gap).
        ``hi``        ``True`` for a focal row -> sign x significance shading
                      (default ``False``).
        ``control``   ``True`` to mark the row as part of the Controls block
                      (rendered in the de-emphasised ``ctrl`` style; the first
                      control row gets a faint separator rule).
        ============  =================================================

    notes :
        AEA ``Notes:`` text shown under the table (DV, FE, cluster, controls,
        star legend, shading note). Wrapped in ``<p class="note">``.
    anchor :
        Stable id (from :func:`anchor_id`) emitted as ``id="..."`` on the
        ``<table>`` so heat cells built with the same id link here.
    dual_cluster :
        When ``True`` each cell also shows a bracketed 2-way ``[t2]`` line.
    columns :
        Column headers (HTML). If omitted and any row has cells, columns are
        numbered ``(1) ... (k)``.
    n, r2 :
        ``N`` and adjusted-``R^2`` footer values. A scalar is broadcast to all
        columns; a sequence supplies one value per column (``None`` -> blank).
    fmt :
        Format spec for coefficients (default 4 decimals; t-stats fixed 2dp).

    Returns
    -------
    str
        The full ``<table class="aea">...</table>`` block, plus the
        ``<p class="note">`` if ``notes`` is given.
    """
    # Determine column count from the widest row.
    ncols = 0
    for r in rows:
        cells = r.get("cells") or []
        ncols = max(ncols, len(cells))
    if columns is not None:
        ncols = max(ncols, len(columns))
    if ncols == 0:
        ncols = 1

    id_attr = f' id="{_html.escape(anchor, quote=True)}"' if anchor else ""
    out = [f'<table class="aea"{id_attr}>', f"<caption>{caption}</caption>"]

    # Header row(s): toprule + column labels.
    hdr = '<tr class="top"><th class="varh">&nbsp;</th>'
    if columns is not None:
        for c in columns:
            hdr += f"<th>{c}</th>"
    else:
        for i in range(ncols):
            hdr += f"<th>({i + 1})</th>"
    hdr += "</tr>"
    out.append(hdr)

    # Body rows.
    first_control = True
    for r in rows:
        label = r.get("label", "")
        cells = list(r.get("cells") or [])
        hi = bool(r.get("hi", False))
        is_ctrl = bool(r.get("control", False))
        tr_cls = ""
        var_cls = "var"
        if is_ctrl:
            var_cls = "var ctrl"
            if first_control:
                tr_cls = ' class="ctrlsep"'
                first_control = False
        row_html = f"<tr{tr_cls}><td class=\"{var_cls}\">{label}</td>"
        for j in range(ncols):
            c = cells[j] if j < len(cells) else {}
            row_html += _aea_cell(
                c.get("b"), c.get("t"),
                hi=hi, dual_cluster=dual_cluster, t2=c.get("t2"), fmt=fmt,
            )
        row_html += "</tr>"
        out.append(row_html)

    # Footer: N and adj-R^2.
    def _broadcast(v):
        if isinstance(v, (list, tuple)):
            return [(_to_float(x) if not isinstance(x, str) else x) for x in v]
        return [v] * ncols

    if n is not None:
        nv = _broadcast(n)
        cells = ""
        for j in range(ncols):
            x = _to_float(nv[j]) if j < len(nv) else None
            cells += f"<td>{int(x):,}</td>" if x is not None else "<td></td>"
        out.append(f'<tr class="sep"><td class="var">$N$</td>{cells}</tr>')

    if r2 is not None:
        rv = _broadcast(r2)
        cells = ""
        for j in range(ncols):
            x = _to_float(rv[j]) if j < len(rv) else None
            cells += f"<td>{x:.4f}</td>" if x is not None else "<td></td>"
        out.append(f'<tr class="bot"><td class="var">Adj. $R^2$</td>{cells}</tr>')
    else:
        # Still close the table body with a bottomrule on the last data row.
        if out[-1].startswith("<tr"):
            out[-1] = out[-1].replace("<tr", '<tr class="bot"', 1) \
                if 'class=' not in out[-1].split('>', 1)[0] else out[-1]

    out.append("</table>")
    block = "\n".join(out) + "\n"
    if notes:
        block += f'<p class="note"><em>Notes:</em> {notes}</p>\n'
    return block


# ---------------------------------------------------------------------------
# Callout boxes & page scaffolding
# ---------------------------------------------------------------------------
def finding_box(html: str) -> str:
    """Green executive-summary / key-finding callout."""
    return f'<div class="finding">{html}</div>\n'


def model_box(latex_or_text: str) -> str:
    """Gray box for the estimating equation / specification.

    Pass HTML with entities for math (``&beta;``, ``&times;``, ``&Delta;``,
    subscripts via ``<sub>``); this is not a LaTeX renderer.
    """
    return f'<div class="model">{latex_or_text}</div>\n'


def toc(entries: Sequence[tuple]) -> str:
    """Table-of-contents box from ``(anchor, label)`` pairs.

    >>> toc([('s1', '1. Returns')]).startswith('<div class="toc">')
    True
    """
    links = "\n".join(
        f'<a href="#{_html.escape(a, quote=True)}">{lab}</a>' for a, lab in entries
    )
    return f'<div class="toc"><strong>Contents</strong>\n{links}\n</div>\n'


def provenance_footer(meta: Mapping[str, object]) -> str:
    """Footer listing build provenance (commit, branch, data, scripts, etc.).

    Every ``meta`` item is rendered as ``<b>key:</b> value``. Recommended keys:
    ``commit``, ``branch``, ``built``, ``data``, ``script``, ``N``.
    """
    parts = [f"<b>{_html.escape(str(k))}:</b> {_html.escape(str(v))}"
             for k, v in meta.items()]
    return f'<div class="foot">{" &nbsp;|&nbsp; ".join(parts)}</div>\n'


def html_head(title: str) -> str:
    """Opening HTML through ``<body>``, embedding :data:`CSS`."""
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_html.escape(title)}</title>\n"
        f"<style>{CSS}</style></head><body>\n"
    )


def html_tail() -> str:
    """Closing ``</body></html>``."""
    return "</body></html>\n"


# ---------------------------------------------------------------------------
# Anchor verification (run before delivering any report)
# ---------------------------------------------------------------------------
def verify_anchor_links(html_path: Union[str, Path], *, prefix: str = ANCHOR_PREFIX) -> dict:
    """Assert every report anchor is wired bidirectionally; return counts.

    Parses the written HTML file, collects the set of ``href="#{prefix}..."``
    link targets and the set of ``id="{prefix}..."`` table ids, then asserts:

    * **no broken links** -- ``links - ids`` is empty (every heat cell points
      at a real table), and
    * **no orphan tables** -- ``ids - links`` is empty (every full table is
      reachable from at least one heat cell).

    Only anchors carrying ``prefix`` (default :data:`ANCHOR_PREFIX`) are
    checked, so incidental page ids never trip the verifier.

    Parameters
    ----------
    html_path :
        Path to the written report.
    prefix :
        Anchor prefix to inspect (default ``"tab_"``).

    Returns
    -------
    dict
        ``{"links": <int>, "ids": <int>, "broken": [...], "orphans": [...]}``.

    Raises
    ------
    AssertionError
        If any broken link or orphan id exists (first few are listed).
    """
    text = Path(html_path).read_text(encoding="utf-8")
    pat = re.escape(prefix)
    links = set(re.findall(rf'href="#({pat}[^"]+)"', text))
    ids = set(re.findall(rf'id="({pat}[^"]+)"', text))
    broken = sorted(links - ids)
    orphans = sorted(ids - links)
    assert not broken, f"BROKEN LINKS (no matching table): {broken[:5]}"
    assert not orphans, f"ORPHAN TABLES (not linked from any heat cell): {orphans[:5]}"
    return {"links": len(links), "ids": len(ids), "broken": broken, "orphans": orphans}


# ---------------------------------------------------------------------------
# Smoke test -- a tiny 2-DV demo report + anchor verification
# ---------------------------------------------------------------------------
def _smoke_test() -> None:
    """Build a minimal 2-DV report (1 heat-grid + 2 clickable AEA tables) and verify."""
    # Two demo DVs x two horizons -> 4 clickable cells, each linking to a table.
    dvs = [("ret", "Size/industry-adj. return"), ("vol", "Return volatility")]
    horizons = [("F0", 2.99, -2.83), ("F1", 1.20, -1.40)]

    # --- Heat grid: one heat table per DV, cells link to the full tables. ---
    heat_tables = []
    for dv_key, dv_lab in dvs:
        rows = '<tr><th>DV</th><th>F0</th><th>F1</th></tr>\n'
        rows += f'<tr><td class="var">{dv_lab}</td>'
        for hz_key, _b, tval in horizons:
            rows += hcell(tval, anchor=anchor_id(dv_key, hz_key))
        rows += "</tr>"
        heat_tables.append(
            f'<table class="heat"><caption>Focal: Treat &times; &Delta;Shock '
            f'({dv_lab})</caption>\n{rows}</table>'
        )
    heat_html = heat_grid(heat_tables)

    # --- Full AEA tables (one per DV x horizon), with focal + controls. ---
    aea_tables = []
    for dv_key, dv_lab in dvs:
        for hz_key, b, tval in horizons:
            tbl = aea_table(
                caption=f"{dv_lab} ({hz_key})",
                anchor=anchor_id(dv_key, hz_key),
                columns=["(1) Full"],
                rows=[
                    {"label": "Treat", "hi": True,
                     "cells": [{"b": b, "t": tval}]},
                    {"label": "Treat &times; &Delta;Shock", "hi": True,
                     "cells": [{"b": -0.0031, "t": tval}]},
                    {"label": "Size", "control": True,
                     "cells": [{"b": -0.0015, "t": -4.31}]},
                    {"label": "BTM", "control": True,
                     "cells": [{"b": 0.0078, "t": 5.51}]},
                    {"label": "ROA", "control": True,
                     "cells": [{"b": 0.0151, "t": 4.58}]},
                ],
                n=189_036, r2=0.016,
                notes=("DV: " + dv_lab + ". Firm-month panel. FE: industry "
                       "(SIC3) + year-month. Cluster: firm. &Delta;Shock is a "
                       "standardized one-period change (not a level). "
                       "* p&lt;0.10, ** p&lt;0.05, *** p&lt;0.01; "
                       "t-statistics in parentheses. Shaded = focal terms."),
            )
            aea_tables.append(tbl)

    body = (
        html_head("report_lib smoke test")
        + "<h1>report_lib smoke test</h1>\n"
        + '<p class="sub">Tiny 2-DV demo &mdash; clickable heatmap &rarr; full tables.</p>\n'
        + finding_box("<strong>Demo finding:</strong> the focal "
                      "Treat &times; &Delta;Shock loads negative at F0.")
        + toc([("s1", "1. Heatmap"), ("s2", "2. Full tables")])
        + '<h2 id="s1">1. Heatmap</h2>\n'
        + model_box("Y<sub>i,t</sub> = &beta;<sub>1</sub> Treat<sub>i</sub> "
                    "+ &beta;<sub>2</sub> Treat &times; &Delta;Shock<sub>t</sub> "
                    "+ &gamma;'Controls + &alpha;<sub>ind</sub> + &delta;<sub>t</sub> "
                    "+ &epsilon;<sub>i,t</sub>")
        + heat_html
        + '<h2 id="s2">2. Full tables</h2>\n'
        + '<div class="aea-grid">\n' + "\n".join(aea_tables) + "\n</div>\n"
        + provenance_footer({"commit": "demo", "branch": "smoke",
                             "script": "report_lib.py", "N": "189,036"})
        + html_tail()
    )

    with tempfile.NamedTemporaryFile(
        "w", suffix="_report_lib_smoke.html", delete=False, encoding="utf-8"
    ) as fh:
        fh.write(body)
        path = fh.name

    counts = verify_anchor_links(path)
    print(f"Wrote demo report: {path}")
    print(f"Anchor check: {counts['links']} links, {counts['ids']} ids, "
          f"{len(counts['broken'])} broken, {len(counts['orphans'])} orphans")
    assert counts["links"] == 4 and counts["ids"] == 4, "expected 4 linked tables"
    print("OK")


if __name__ == "__main__":
    _smoke_test()
