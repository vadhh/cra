"""
pdf_report.py — PDF report generator for Sydeco LightML Contract Risk Analyzer.

Usage:
    from pdf_report import generate_pdf
    pdf_bytes = generate_pdf(analysis_result_dict)
"""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

# ── Palette ───────────────────────────────────────────────────────────────────

_NAVY      = colors.HexColor("#1a2744")
_GREEN     = colors.HexColor("#198754")
_ORANGE    = colors.HexColor("#fd7e14")
_RED       = colors.HexColor("#dc3545")
_CRIMSON   = colors.HexColor("#8b0000")
_GREY      = colors.HexColor("#6c757d")
_LIGHT     = colors.HexColor("#f8f9fa")
_GREEN_BG  = colors.HexColor("#d4edda")
_GREEN_FG  = colors.HexColor("#155724")

# ── Suggested rewrites per L1 red-flag id ────────────────────────────────────

_REWRITES: dict[str, str] = {
    "leonine_profit": (
        "Suggested rewrite: 'Profits shall be distributed proportionally to each "
        "party's contribution as set out in Schedule A. No party may be excluded "
        "from losses while retaining the right to profits.'"
    ),
    "leonine_no_loss": (
        "Suggested rewrite: 'Each party shall bear losses in proportion to their "
        "respective investment or contribution share as defined herein.'"
    ),
    "excessive_penalty": (
        "Suggested rewrite: 'Late payment interest shall not exceed 0.5% per month "
        "(6% per annum) calculated on the overdue outstanding amount.'"
    ),
    "rights_waiver": (
        "Suggested rewrite: 'Each party retains all statutory rights and remedies "
        "afforded under applicable law. No general waiver of rights is granted by "
        "this agreement.'"
    ),
    "unilateral_modification": (
        "Suggested rewrite: 'This agreement may only be amended by a written "
        "instrument signed by authorised representatives of all parties, with a "
        "minimum notice period of 30 days.'"
    ),
    "total_liability_exclusion": (
        "Suggested rewrite: 'The total aggregate liability of either party shall not "
        "exceed the total fees paid under this agreement in the 12 months preceding "
        "the event giving rise to liability.'"
    ),
    "auto_renewal_no_notice": (
        "Suggested rewrite: 'This agreement renews automatically for successive "
        "12-month terms unless either party provides written notice of non-renewal "
        "at least 60 days before the current term expires.'"
    ),
    "illegal_object": (
        "Action required: This clause may be void or unenforceable under applicable "
        "law. Seek qualified legal advice before signing."
    ),
}

# ── Risk colour map ───────────────────────────────────────────────────────────

def _risk_color(label: str) -> colors.Color:
    return {"LOW": _GREEN, "MEDIUM": _ORANGE, "HIGH": _RED, "CRITICAL": _CRIMSON}.get(
        label, _GREY
    )


# ── PDF builder ───────────────────────────────────────────────────────────────

def generate_pdf(result: dict) -> bytes:
    """Return raw PDF bytes for the given /analyze response dict."""
    buf = io.BytesIO()
    W = A4[0] - 4 * cm

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    base = getSampleStyleSheet()

    def _style(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    h1      = _style("h1",   fontSize=20, textColor=_NAVY, fontName="Helvetica-Bold", spaceAfter=4)
    h2      = _style("h2",   fontSize=13, textColor=_NAVY, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body    = _style("body", fontSize=9,  leading=14, spaceAfter=4)
    small   = _style("sm",   fontSize=8,  leading=12, textColor=_GREY, spaceAfter=3)
    rewrite = _style("rw",   fontSize=8.5, leading=13, textColor=_GREEN_FG,
                     backColor=_GREEN_BG, leftIndent=8, rightIndent=8,
                     spaceBefore=3, spaceAfter=6, borderPad=4)
    footer  = _style("ft",   fontSize=7,  textColor=_GREY, alignment=TA_CENTER)

    story = []

    # ── Header bar ───────────────────────────────────────────────────────────
    header_style_co   = _style("co",  fontSize=11, textColor=colors.white, fontName="Helvetica-Bold")
    header_style_prod = _style("prd", fontSize=11, textColor=colors.white, fontName="Helvetica")
    story.append(Table(
        [[Paragraph("SYDECO", header_style_co),
          Paragraph("LightML Contract Risk Analyzer", header_style_prod)]],
        colWidths=[W * 0.25, W * 0.75],
        style=TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), _NAVY),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]),
    ))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(
        f"Report generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", small
    ))
    story.append(HRFlowable(width=W, thickness=1, color=_NAVY))
    story.append(Spacer(1, 0.3 * cm))

    # ── Risk score banner ─────────────────────────────────────────────────────
    layer3 = result.get("layer3", {})
    score  = layer3.get("score", "N/A")
    label  = layer3.get("label", "UNKNOWN")
    rc     = _risk_color(label)

    story.append(Table(
        [[
            Paragraph("RISK SCORE",
                       _style("rsl", fontSize=9, textColor=_GREY, fontName="Helvetica-Bold")),
            Paragraph(f"{score} / 100",
                       _style("rsv", fontSize=26, textColor=rc, fontName="Helvetica-Bold")),
            Paragraph(label,
                       _style("rst", fontSize=14, textColor=colors.white,
                              fontName="Helvetica-Bold", alignment=TA_CENTER)),
        ]],
        colWidths=[W * 0.25, W * 0.40, W * 0.35],
        style=TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND",    (2, 0), (2, 0),   rc),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Executive Summary ─────────────────────────────────────────────────────
    story.append(Paragraph("Executive Summary", h2))

    layer1     = result.get("layer1", {})
    layer2     = result.get("layer2", {}) or {}
    lang       = result.get("language", "unknown")
    juris      = result.get("jurisdiction", "not detected")
    
    doctype_dict = layer2.get("document_type")
    if isinstance(doctype_dict, dict):
        doctype = doctype_dict.get("label", "not detected")
        confidence_val = doctype_dict.get("confidence")
    else:
        doctype = doctype_dict or "not detected"
        confidence_val = None

    gov_law    = layer1.get("governing_law") or "not detected"
    venue      = layer1.get("venue") or "not detected"
    red_flags  = layer1.get("red_flags", [])
    clauses    = layer1.get("clause_presence", [])
    missing    = [c for c in clauses if c.get("required") and not c.get("present")]
    l2_flagged = layer2.get("flagged_clauses", [])

    profile_used = "N/A"
    profile_version = "N/A"
    validation_status = "N/A"
    
    if doctype and doctype != "not detected":
        try:
            from detector.detector_profiles import ProfileManager
            manager = ProfileManager()
            profile = manager.resolve_profile_by_name(doctype)
            if profile:
                profile_used = profile["metadata"]["display_name"]
                profile_version = profile["version"]
                validation_status = profile["validation_status"]
        except Exception as exc:
            logger.warning("PDF generator failed to resolve profile: %s", exc)

    if confidence_val is not None:
        confidence_str = f"{confidence_val * 100:.1f}%" if confidence_val <= 1.0 else f"{confidence_val:.1f}%"
    else:
        confidence_str = "N/A"

    analysis_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_rows = [
        ["Language",         lang.upper() if lang not in ("unknown", "") else "Not detected"],
        ["Contract Type",    doctype.title() if doctype not in ("not detected", "", None) else "Not detected"],
        ["Detection Confidence", confidence_str],
        ["Jurisdiction",     juris or "Not detected"],
        ["Governing law",    gov_law],
        ["Dangerous clauses", str(len(red_flags) + len(l2_flagged))],
        ["Missing clauses",   str(len(missing))],
        ["Profile Used",     profile_used],
        ["Profile Version",  profile_version],
        ["Validation Status", validation_status],
        ["Analysis Date",    analysis_date]
    ]

    story.append(Table(
        summary_rows,
        colWidths=[W * 0.38, W * 0.62],
        style=TableStyle([
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("BACKGROUND",    (0, 0), (0, -1),  _LIGHT),
            ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Dangerous Clauses ─────────────────────────────────────────────────────
    story.append(Paragraph("Dangerous Clauses", h2))

    if not red_flags and not l2_flagged:
        story.append(Paragraph("No dangerous clauses detected.", body))
    else:
        for flag in red_flags:
            sev       = flag.get("severity", "")
            sev_hex   = "#dc3545" if sev == "HIGH" else "#fd7e14"
            flag_id   = flag.get("id", "")
            desc      = flag.get("description", flag.get("type", ""))
            evidence  = flag.get("evidence", "")
            story.append(Paragraph(
                f'<font color="{sev_hex}"><b>[{sev}]</b></font> {desc}',
                _style("df", fontSize=9, leading=13, textColor=_RED),
            ))
            if evidence:
                story.append(Paragraph(f'Evidence: "…{evidence}…"', small))
            rw = _REWRITES.get(flag_id)
            if rw:
                story.append(Paragraph(rw, rewrite))

        for fl in l2_flagged:
            lbl = fl.get("label", "").replace("_", " ").title()
            sc  = fl.get("score", "?")
            story.append(Paragraph(f"[AI] {lbl} (confidence: {sc})",
                                    _style("af", fontSize=9, leading=13, textColor=_ORANGE)))

    story.append(Spacer(1, 0.3 * cm))

    # ── Missing Clauses ───────────────────────────────────────────────────────
    story.append(Paragraph("Missing Important Clauses", h2))

    if not clauses:
        story.append(Paragraph("Clause analysis not available.", body))
    else:
        rows = [
            ["✓ Present" if c.get("present") else "✗ Missing",
             c.get("title", c.get("clause_id", ""))]
            for c in clauses
        ]
        ts = [
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]
        for i, row in enumerate(rows):
            col = _GREEN if row[0].startswith("✓") else _RED
            ts.append(("TEXTCOLOR", (0, i), (0, i), col))
        story.append(Table(rows, colWidths=[W * 0.22, W * 0.78], style=TableStyle(ts)))

    story.append(Spacer(1, 0.3 * cm))

    # ── Recommendations ───────────────────────────────────────────────────────
    story.append(Paragraph("Recommendations", h2))

    recs = []
    if missing:
        titles = ", ".join(c.get("title", c.get("clause_id", "")) for c in missing)
        recs.append(f"Add the following missing clauses: {titles}.")
    high_flags = [f for f in red_flags if f.get("severity") == "HIGH"]
    if high_flags:
        recs.append(
            f"Address {len(high_flags)} HIGH-severity clause(s) before signing — "
            "these create significant legal exposure."
        )
    if gov_law == "not detected":
        recs.append(
            "Add a governing law clause specifying which country's law governs the contract."
        )
    if venue == "not detected":
        recs.append(
            "Add a jurisdiction/venue clause specifying where disputes will be resolved."
        )
    if label in ("HIGH", "CRITICAL"):
        recs.append(
            "This contract presents substantial risk. Have a qualified lawyer review "
            "it before signing."
        )
    if not recs:
        recs.append(
            "Contract appears well-structured. Standard legal review recommended before signing."
        )

    for i, rec in enumerate(recs, 1):
        story.append(Paragraph(f"{i}. {rec}", body))

    story.append(Spacer(1, 0.5 * cm))

    # ── Professional Legal Review ─────────────────────────────────────────────
    review_status = result.get("review_status", "unreviewed")
    if review_status and review_status != "unreviewed":
        story.append(Paragraph("Professional Legal Review", h2))
        reviewer = result.get("reviewer_email", "Anonymous Reviewer")
        comment = result.get("review_comment") or "No comments provided."
        reviewed_at = result.get("reviewed_at")
        
        date_str = ""
        if reviewed_at:
            try:
                # Handle possible SQLite timestamp formats
                ts_clean = reviewed_at.split(".")[0].replace("T", " ")
                dt = datetime.strptime(ts_clean, "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d %B %Y, %H:%M")
            except Exception:
                date_str = reviewed_at
        
        review_rows = [
            ["Status", review_status.upper()],
            ["Reviewer", reviewer],
        ]
        if date_str:
            review_rows.append(["Date", date_str])
        review_rows.append(["Comments", comment])
        
        story.append(Table(
            review_rows,
            colWidths=[W * 0.25, W * 0.75],
            style=TableStyle([
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("BACKGROUND",    (0, 0), (0, -1),  _LIGHT),
                ("FONTNAME",      (0, 0), (0, -1),  "Helvetica-Bold"),
                ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]),
        ))
        story.append(Spacer(1, 0.5 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, thickness=0.5, color=_GREY))
    story.append(Paragraph(
        "This report is generated automatically by Sydeco LightML Contract Risk Analyzer. "
        "It does not constitute legal advice. Always consult a qualified lawyer before signing any contract.",
        footer,
    ))

    doc.build(story)
    return buf.getvalue()
