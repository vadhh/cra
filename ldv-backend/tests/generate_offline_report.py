"""generate_offline_report.py — renders the offline multilingual acceptance
report as a PDF from tests/offline_validation_results.json.

Usage: python3 tests/generate_offline_report.py
"""
import json
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

HERE = Path(__file__).parent
RESULTS_PATH = HERE / "offline_validation_results.json"
REPORT_PATH = HERE / "offline_validation_report.pdf"

_NAVY = colors.HexColor("#1a2744")
_GREY = colors.HexColor("#6c757d")

_TABLE_HEADER_STYLE = [
    ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]


def generate_report(results: dict, out_path: Path) -> None:
    W = A4[0] - 4 * cm
    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    base = getSampleStyleSheet()

    def _style(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    h1 = _style("h1", fontSize=18, textColor=_NAVY, fontName="Helvetica-Bold", spaceAfter=6)
    h2 = _style("h2", fontSize=13, textColor=_NAVY, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    body = _style("body", fontSize=9, leading=13, spaceAfter=4)
    small = _style("sm", fontSize=8, leading=12, textColor=_GREY, spaceAfter=3)

    story = []
    story.append(Paragraph("LDV Offline Multilingual Acceptance Report", h1))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}", small))

    cfg = results.get("config", {})
    story.append(Paragraph(
        f"Config: LDV_REMOTE_TRANSLATION={cfg.get('LDV_REMOTE_TRANSLATION')} | "
        f"Run window: {cfg.get('started_at')} → {cfg.get('finished_at')}", small,
    ))
    story.append(HRFlowable(width=W, thickness=1, color=_NAVY))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        "Scope: this run tests English, Indonesian, French, and Dutch contract and "
        "non-contract documents, one scanned/no-text PDF, and two malformed files, "
        "with all outbound network sockets blocked (see Verification Evidence).", body,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # ── Test Results ─────────────────────────────────────────────────────
    story.append(Paragraph("Test Results", h2))
    overall = results.get("overall", {})
    rows = [
        ["Test category", "Total", "Passed", "Failed", "Blocked", "Evidence"],
        [
            "Offline multilingual suite",
            str(overall.get("total", 0)), str(overall.get("passed", 0)),
            str(overall.get("failed", 0)), str(overall.get("blocked", 0)),
            "ldv-backend/tests/offline_validation_results.json",
        ],
    ]
    story.append(Table(
        rows, colWidths=[W * 0.27, W * 0.1, W * 0.1, W * 0.1, W * 0.1, W * 0.33],
        style=TableStyle(_TABLE_HEADER_STYLE),
    ))
    story.append(Spacer(1, 0.4 * cm))

    # ── Per-language breakdown ───────────────────────────────────────────
    story.append(Paragraph("Per-Language Metrics", h2))
    lang_rows = [["Language", "Total", "Passed", "Doc-type acc.", "Clause recall", "Mean ms", "Median ms", "P95 ms"]]
    for lang, m in sorted(results.get("by_language", {}).items()):
        lang_rows.append([
            lang.upper(), str(m["total"]), str(m["passed"]),
            f"{m['doc_type_accuracy_pct']}%",
            f"{m['clause_recall_pct']}%" if m["clause_recall_pct"] is not None else "n/a",
            str(m["latency_mean_ms"]), str(m["latency_median_ms"]), str(m["latency_p95_ms"]),
        ])
    story.append(Table(lang_rows, colWidths=[W * 0.13] * 8, style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.4 * cm))

    # ── Per-fixture detail ───────────────────────────────────────────────
    story.append(Paragraph("Per-Fixture Detail", h2))
    fix_rows = [["Fixture", "Status", "Detail"]]
    for f in results.get("fixtures", []):
        detail = f.get("error") or f.get("document_type_detected") or ""
        fix_rows.append([f["path"], f["status"], str(detail)[:60]])
    story.append(Table(fix_rows, colWidths=[W * 0.4, W * 0.15, W * 0.45], style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.4 * cm))

    # ── Model Provenance ─────────────────────────────────────────────────
    story.append(Paragraph("Model Provenance", h2))
    prov_rows = [["Model", "Revision"]]
    for m in results.get("model_provenance", []):
        prov_rows.append([m["name"], m["revision"]])
    story.append(Table(prov_rows, colWidths=[W * 0.6, W * 0.4], style=TableStyle(_TABLE_HEADER_STYLE)))
    story.append(Spacer(1, 0.3 * cm))

    # ── Translation Failures ─────────────────────────────────────────────
    story.append(Paragraph("Translation Failures", h2))
    failures = results.get("translation_failures") or []
    if failures:
        for msg in failures:
            story.append(Paragraph(msg, body))
    else:
        story.append(Paragraph("None recorded during this run.", body))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"Peak RAM (RSS): {results.get('peak_rss_mb', 'n/a')} MB", body))
    story.append(Spacer(1, 0.3 * cm))

    # ── Verification Evidence ────────────────────────────────────────────
    story.append(Paragraph("Verification Evidence", h2))
    self_check_line = (
        "PASS — a real outbound connect attempt was raised and blocked"
        if results.get("self_check_passed") else "FAIL"
    )
    story.append(Paragraph(f"Network egress self-check: {self_check_line} before any fixture was processed.", body))
    story.append(Paragraph("Raw results: ldv-backend/tests/offline_validation_results.json", body))
    story.append(Paragraph(
        "Harness source: ldv-backend/tests/run_offline_validation.py, "
        "ldv-backend/tests/offline_net_trap.py", body,
    ))
    story.append(Spacer(1, 0.3 * cm))

    # ── Decisions Required from Management ───────────────────────────────
    story.append(Paragraph("Decisions Required from Management", h2))
    decisions = [
        "Accept socket-level egress blocking as sufficient offline proof for this dev-sandbox "
        "environment, or require kernel-level network-namespace isolation for the next report.",
        "No OCR is implemented; scanned documents are rejected with a clear error rather than "
        "silently mis-analyzed. Confirm this fail-closed behavior is acceptable for the pilot, "
        "or request OCR as a new priority.",
        "Confirm the current fixture set (EN/ID/FR/NL contracts + non-contracts, one scanned "
        "PDF, two malformed files) is sufficient acceptance coverage, or specify additional "
        "cases to add.",
    ]
    for i, d in enumerate(decisions, 1):
        story.append(Paragraph(f"{i}. {d}", body))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Status: Implemented, Tested — pending management Accepted/Blocked decision above.", body))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width=W, thickness=0.5, color=_GREY))
    story.append(Paragraph(
        "Generated automatically by tests/generate_offline_report.py from "
        "tests/offline_validation_results.json.", small,
    ))

    doc.build(story)


def main():
    if not RESULTS_PATH.exists():
        raise SystemExit(f"{RESULTS_PATH} not found — run run_offline_validation.py first")
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    generate_report(results, REPORT_PATH)
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
