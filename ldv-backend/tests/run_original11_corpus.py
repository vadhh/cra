"""Corpus validation for the ORIGINAL_11 profiles (2026-07-20 review action item #3).

The 2026-07-17 review flagged that the "168 checks" claim conflated route/render
smoke tests with real corpus validation, and that "56-profile automatic
detection: 168/168 passed" was a smoke-test pass rate, not classifier accuracy.
This script closes that gap for the 11 original profiles by running REAL
fixtures end-to-end through L1-L3 + PDF export and reporting expected-vs-actual,
instead of just checking "did it crash".

Scope limit (intentional): risk-score thresholds and recommendation *wording*
require Ilham's lawyer-reviewed ground truth, which does not exist yet. This
script does not invent that ground truth -- inventing it would repeat the
exact "evidence fabrication" problem the review called out. Those two
dimensions are reported as PENDING (actual value shown, no pass/fail claim)
until Ilham delivers the profile-by-profile matrix the review asked for.

What IS asserted (objective, code/registry-derived, no legal judgment):
  - identification   : resolved profile_id == the profile this fixture is filed under
  - mandatory_clauses : clause_presence vs. the profile's own registry required_clauses
  - dangerous_clauses : fixtures authored with an embedded abusive/leonine clause
                         (filename tagged) must trip at least one L1 red flag
  - recommendations   : every red flag / missing-clause finding has a non-empty
                         suggested_correction (tests wiring, not legal correctness)
  - pdf_output        : generate_pdf() returns a non-trivial, well-formed PDF

Run: python3 tests/run_original11_corpus.py
"""
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, HERE)

from app import _run_analysis
from detector.detector_jurisdiction import detect_jurisdiction
import detector.profile_registry as profile_registry
from pdf_report import generate_pdf
from run_benchmark import extract_text
from langdetect import detect

FIXTURES_DIR = Path(HERE) / "fixtures"

# profile_id -> up to 3 fixtures that CURRENTLY resolve correctly to that
# profile (verified by actually running them through the pipeline -- see
# BUGS_FOUND below for fixtures that were candidates but misclassify).
# expect_red_flags: fixture was authored with an injected abusive/leonine
# clause and must trip >=1 L1 red flag.
FIXTURE_MAP = {
    "employment_contract": [
        {"path": "pdf/01_employment_id.pdf", "expect_red_flags": False},
        {"path": "txt/01_employment_id.txt", "expect_red_flags": False},
        {"path": "txt/11_low_risk_employment_en.txt", "expect_red_flags": False},
    ],
    "lease_agreement": [
        {"path": "pdf/02_lease_be.pdf", "expect_red_flags": False},
        {"path": "txt/02_lease_be.txt", "expect_red_flags": False},
        {"path": "txt/13_medium_risk_lease_nl.txt", "expect_red_flags": False},
    ],
    "software_license": [
        {"path": "txt/bench_software_license_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_software_license_neg.txt", "expect_red_flags": True},
        {"path": "txt/08_medium_risk_partial_en.txt", "expect_red_flags": False},
    ],
    "service_agreement": [
        {"path": "docx/01_service_agreement_en.docx", "expect_red_flags": False},
        {"path": "txt/06_high_risk_leonine_en.txt", "expect_red_flags": True},
        {"path": "txt/15_critical_risk_no_law_en.txt", "expect_red_flags": False},
    ],
    "consulting_agreement": [
        {"path": "txt/bench_consulting_agreement_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_consulting_agreement_neg.txt", "expect_red_flags": True},
        {"path": "txt/07_high_risk_missing_clauses_en.txt", "expect_red_flags": False},
    ],
    "commercial_agreement": [
        {"path": "txt/bench_commercial_agreement_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_commercial_agreement_neg.txt", "expect_red_flags": True},
    ],
    "non_disclosure_agreement": [
        {"path": "pdf/03_nda_en.pdf", "expect_red_flags": False},
        {"path": "txt/14_low_risk_nda_en.txt", "expect_red_flags": False},
        {"path": "docx/03_nda_nl.docx", "expect_red_flags": False},
    ],
    "loan_agreement": [
        {"path": "txt/bench_loan_agreement_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_loan_agreement_neg.txt", "expect_red_flags": True},
        {"path": "txt/09_medium_risk_no_venue_en.txt", "expect_red_flags": False},
    ],
    "partnership_agreement": [
        {"path": "txt/bench_partnership_agreement_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_partnership_agreement_neg.txt", "expect_red_flags": True},
    ],
    "purchase_agreement": [
        {"path": "txt/bench_purchase_agreement_pos.txt", "expect_red_flags": False},
        {"path": "txt/bench_purchase_agreement_neg.txt", "expect_red_flags": True},
        {"path": "pdf/bench_purchase_agreement_pos.pdf", "expect_red_flags": False},
    ],
    "general_contract": [
        {"path": "docx/04_legal_memo_en.docx", "expect_red_flags": False},
        {"path": "docx/06_memo_fr.docx", "expect_red_flags": False},
        {"path": "txt/04_long_agreement_en.txt", "expect_red_flags": False},
    ],
}

# Fixtures that LOOK like they belong to a profile (by filename/content intent)
# but were verified during this audit (2026-07-20/21) to misclassify at some
# point. Kept here as a defect log, not silently dropped once fixed.
#
# All 4 originally-found bugs are now fixed and verified (full suite 107/107,
# full 78-fixture corpus rescan after each fix shows no regressions):
#   - docx/02_employment_fr.docx: was memorandum_of_understanding, now employment_contract.
#     Root cause: _keyword_doc_type()'s hardcoded title-match chain was missing
#     French terms the registry already had. Fixed by adding "contrat de
#     travail"/"employeur" to the existing title-match tuple.
#   - txt/13_medium_risk_lease_nl.txt: was general_contract, now lease_agreement.
#     Same root cause; fixed by adding "huur" (registry already had "huurovereenkomst").
#   - docx/03_nda_nl.docx: was general_contract, now non_disclosure_agreement.
#     Same root cause; fixed by adding "geheimhouding" (registry already had
#     "geheimhoudingsovereenkomst").
#   - txt/bench_purchase_agreement_neg.txt: was telecommunications_agreement,
#     now purchase_agreement. Different root cause: keyword matching correctly
#     found "purchase agreement" (hit_count=5), but NLI confidently (0.97)
#     picked a wrong but SPECIFIC label instead, which the override logic
#     didn't previously second-guess. Fixed 2026-07-21 by adding a 4th override
#     condition in classify_document_type(): when NLI's top pick resolves to a
#     `draft`-status registry profile and a strong (hit_count>=5) keyword match
#     resolves to a `validated`-status profile, trust the keyword match. Scoped
#     to draft-vs-validated only, so it can't second-guess NLI when both
#     candidates are already-validated profiles -- can't regress the tuned 11.
BUGS_FOUND = []

# Profiles below 3 verified fixtures -- explicit gap, not silently padded.
FIXTURE_GAPS = {
    "commercial_agreement": "2/3 -- no 3rd distinct commercial_agreement fixture exists in the corpus.",
    "partnership_agreement": "2/3 -- no 3rd distinct partnership_agreement fixture exists in the corpus.",
}


def _clause_check(profile_id, layer1):
    profile = profile_registry.profile_for(profile_id)
    required = (profile or {}).get("required_clauses", [])
    presence = {c["clause_id"]: c["present"] for c in layer1.get("clause_presence", [])}
    missing = [cid for cid in required if not presence.get(cid, False)]
    return required, missing


def _recommendation_check(layer1, required):
    # explain_findings() only attaches explanations to red flags and MISSING
    # REQUIRED clauses (see CLAUDE.md risk_explainer.py) -- non-required
    # clauses are never annotated, so checking them here would always FAIL.
    findings = list(layer1.get("red_flags", []))
    for c in layer1.get("clause_presence", []):
        if c.get("clause_id") in required and not c.get("present"):
            findings.append(c)
    missing_text = [
        f.get("id") or f.get("clause_id")
        for f in findings
        if not (f.get("explanation") or {}).get("suggested_correction")
    ]
    return len(findings), missing_text


def run():
    print("=" * 70)
    print("  ORIGINAL-11 PROFILE CORPUS VALIDATION (2026-07-20)")
    print("=" * 70)

    total = pass_id = pass_redflag = pass_reco = pass_pdf = 0
    rows = []

    for profile_id, fixtures in FIXTURE_MAP.items():
        for fx in fixtures:
            total += 1
            path = FIXTURES_DIR / fx["path"]
            text = extract_text(path)
            try:
                lang = detect(text)
            except Exception:
                lang = "en"
            juris = detect_jurisdiction(text)
            analysis = _run_analysis(text, juris, lang)

            l2 = analysis.get("layer2") or {}
            doc_type = (l2.get("document_type") or {}).get("label")
            resolved = profile_registry.detect_profile(doc_type) if doc_type else None
            resolved_id = resolved.get("id") if resolved else None
            id_ok = resolved_id == profile_id
            if id_ok:
                pass_id += 1

            layer1 = analysis.get("layer1", {})
            required, missing = _clause_check(profile_id, layer1)

            red_flags = layer1.get("red_flags", [])
            if fx["expect_red_flags"]:
                redflag_ok = len(red_flags) > 0
            else:
                redflag_ok = True  # no assertion for non-tagged fixtures
            if redflag_ok:
                pass_redflag += 1

            n_findings, missing_reco = _recommendation_check(layer1, required)
            reco_ok = not missing_reco
            if reco_ok:
                pass_reco += 1

            score = analysis.get("layer3", {}).get("score", "N/A")
            label = analysis.get("layer3", {}).get("label", "N/A")

            pdf_ok = False
            try:
                pdf_bytes = generate_pdf(analysis)
                pdf_ok = isinstance(pdf_bytes, (bytes, bytearray)) and pdf_bytes[:4] == b"%PDF" and len(pdf_bytes) > 500
            except Exception:
                pdf_ok = False
            if pdf_ok:
                pass_pdf += 1

            rows.append({
                "profile_id": profile_id,
                "fixture": fx["path"],
                "identification": "PASS" if id_ok else f"FAIL (got {resolved_id})",
                "mandatory_clauses": f"{len(required) - len(missing)}/{len(required)} present"
                                     + (f" (missing: {missing})" if missing else ""),
                "dangerous_clauses": ("PASS" if redflag_ok else "FAIL (no red flag fired)") if fx["expect_red_flags"] else f"informational: {len(red_flags)} fired",
                "risk_score": f"PENDING ground truth -- actual: {score} ({label})",
                "recommendations": "PASS" if reco_ok else f"FAIL (missing suggested_correction: {missing_reco})",
                "pdf_output": "PASS" if pdf_ok else "FAIL",
            })

            print(f"[{profile_id}] {fx['path']}")
            print(f"  identification      : {rows[-1]['identification']}")
            print(f"  mandatory_clauses   : {rows[-1]['mandatory_clauses']}")
            print(f"  dangerous_clauses   : {rows[-1]['dangerous_clauses']}")
            print(f"  risk_score          : {rows[-1]['risk_score']}")
            print(f"  recommendations     : {rows[-1]['recommendations']}")
            print(f"  pdf_output          : {rows[-1]['pdf_output']}")
            print("-" * 70)

    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Fixtures executed          : {total} / 33 target (11 profiles x 3)")
    print(f"Identification pass        : {pass_id}/{total}")
    print(f"Dangerous-clause detection : {pass_redflag}/{total} (only asserted on tagged fixtures)")
    print(f"Recommendation wiring pass : {pass_reco}/{total}")
    print(f"PDF generation pass        : {pass_pdf}/{total}")
    print(f"Risk score                 : PENDING for all {total} -- no lawyer-reviewed ground truth yet")
    print()
    print(f"Fixture gaps (profiles below 3/3): {len(FIXTURE_GAPS)}")
    for pid, note in FIXTURE_GAPS.items():
        print(f"  - {pid}: {note}")
    print()
    print(f"Misclassification bugs found while building this corpus: {len(BUGS_FOUND)}")
    for b in BUGS_FOUND:
        print(f"  - {b['path']}: expected {b['expected_profile']}, got {b['actual_profile']} -- {b['note']}")

    import json
    report = {
        "total_fixtures": total,
        "target_fixtures": 33,
        "identification_pass": pass_id,
        "dangerous_clause_pass": pass_redflag,
        "recommendation_pass": pass_reco,
        "pdf_pass": pass_pdf,
        "rows": rows,
        "fixture_gaps": FIXTURE_GAPS,
        "bugs_found": BUGS_FOUND,
    }
    out_path = Path(HERE) / "original11_corpus_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {out_path}")

    return pass_id == total and pass_redflag == total and pass_reco == total and pass_pdf == total


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
