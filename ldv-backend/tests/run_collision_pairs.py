"""Collision-pair classification test (2026-07-17 review punch-list item 3).

Tests the 13 classifier collision pairs documented in
docs/classifier_collision_pairs.md with positive/negative/borderline examples,
per the review's mandate: "Test the 13 collision pairs with positive and
negative examples."

Test text for each pair is built directly from that doc's own "A-only
signal"/"B-only signal"/borderline descriptions (authored 2026-07-17) --
not invented here. Scope boundary, stated explicitly in that doc: resolving
any collision found is "a legal/domain call, not a code fix" for Ilham/joint
review. This script tests and reports; it does not attempt to fix
classification behavior for these pairs.

Most profiles in these pairs are registry classifier.status == "draft" (11 of
13 pairs have exactly one draft side; 1 pair -- #10 -- is draft on both
sides). Draft-status misclassification is lower-severity than a mistake among
the validated 11: worker._needs_confirmation()'s draft_profile gate already
forces human confirmation whenever ANY resolved profile isn't validated,
regardless of whether this script's assertions pass. So a FAIL here is a
classifier-accuracy finding for Ilham/Afridho to triage, not a silent-wrong-
result risk in the running pilot.

Run: python3 tests/run_collision_pairs.py
"""
import os
import sys
import json
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, BACKEND_DIR)

from detector.detector_distilbert import classify_document_type
import detector.profile_registry as profile_registry

# Each pair: (profile_a, profile_b, text_a, text_b, text_borderline, borderline_note)
# text_a should classify as profile_a; text_b should classify as profile_b.
# text_borderline has no "correct" answer by design (see collision-pairs doc)
# -- reported for visibility only, no assertion.
PAIRS = [
    (
        "distribution_agreement", "service_agreement",
        "DISTRIBUTION AGREEMENT. The distributor shall resell the supplier's products within the assigned territory of Southeast Asia on an exclusive basis. Distributor purchases products at wholesale price for resale to end customers.",
        "SERVICE AGREEMENT. The provider agrees to perform maintenance agreement services for the client's office equipment on a monthly basis. Services shall be delivered as described in Schedule A.",
        "SERVICE AGREEMENT. The provider agrees to deliver ongoing consulting services to the client, and will additionally resell a small quantity of spare parts from time to time as needed.",
        "service agreement with an ancillary product-resale clause",
    ),
    (
        "purchase_agreement", "supply_agreement",
        "SALE AGREEMENT. Seller agrees to sell and buyer agrees to purchase the goods described in Schedule A for a one-time payment of $50,000, with delivery to occur within 30 days of this agreement.",
        "SUPPLIER AGREEMENT. Supplier shall provide ongoing recurring deliveries of raw materials to buyer pursuant to a standing order, with the term of supply set at 24 months and deliveries occurring monthly.",
        "PURCHASE AGREEMENT. Buyer purchases the goods described in Schedule A, to be delivered in three scheduled installments over the next six months.",
        "purchase agreement with installment deliveries (ongoing/one-off boundary)",
    ),
    (
        "agency_agreement", "service_agreement",
        "AGENCY AGREEMENT. The agent is hereby granted authority to negotiate and conclude transactions on behalf of the principal within the assigned market. The agent shall act in the principal's name.",
        "SERVICE AGREEMENT. The provider agrees to perform maintenance agreement services for the client on a monthly basis, without any authority to bind or represent the client in transactions with third parties.",
        "SERVICE AGREEMENT. The service provider will represent the client's interests when interacting with vendors, though no contracts shall be signed on the client's behalf.",
        "service contract with loose 'represent' language",
    ),
    (
        "maintenance_contract", "service_agreement",
        "MAINTENANCE CONTRACT. Contractor shall perform equipment maintenance, repair, and upkeep of the client's HVAC systems, with scheduled service intervals every three months.",
        "SERVICE AGREEMENT. The provider agrees to deliver general business advisory services to the client, with no equipment, repair, or upkeep obligations of any kind.",
        "IT SUPPORT AGREEMENT. Provider agrees to maintain the client's software systems, offering ongoing troubleshooting and updates as needed.",
        "IT support contract using 'maintain' loosely (not equipment/repair)",
    ),
    (
        "it_services_contract", "service_agreement",
        "IT SERVICES AGREEMENT. Provider shall deliver managed services including 24/7 helpdesk support, infrastructure monitoring, and system uptime guarantees as outlined in the SLA.",
        "SERVICE AGREEMENT. The provider agrees to perform maintenance agreement cleaning services for the client's office premises on a weekly basis.",
        "SERVICE AGREEMENT. The consultant will provide general business advisory services, and may occasionally reference the client's internal software systems during engagements.",
        "generic advisory service mentioning software incidentally",
    ),
    (
        "licensing_agreement", "software_license",
        "LICENSING AGREEMENT. Licensor grants licensee the right to use the registered trademark and associated patent rights in connection with licensee's branded merchandise, in exchange for royalty payments.",
        "SOFTWARE LICENSE AGREEMENT (EULA). Licensor grants licensee a non-exclusive license to use the software as a SaaS application, subject to the end user license agreement terms herein.",
        "TECHNOLOGY LICENSING AGREEMENT. Licensor grants licensee rights to use both the patented hardware design and the accompanying proprietary software source code.",
        "combined patent + software licensing deal",
    ),
    (
        "joint_venture_agreement", "partnership_agreement",
        "JOINT VENTURE AGREEMENT. The parties hereby form a new jointly owned entity, JV Holdings Ltd, to pursue the stated business purpose, with each party contributing capital in exchange for equity in the new entity.",
        "PARTNERSHIP AGREEMENT. The partners agree to conduct business together as a general partnership, sharing profits and losses as set forth herein, without forming any new corporate entity.",
        "PARTNERSHIP AGREEMENT. The partners agree to operate the partnership business, and may in the future consider forming a jointly owned subsidiary for a specific project.",
        "partnership agreement referencing a possible future subsidiary",
    ),
    (
        "outsourcing_agreement", "service_agreement",
        "OUTSOURCING AGREEMENT. Client shall transfer its existing payroll processing function to provider, including the transition of affected employees and assets, effective the handover date.",
        "SERVICE AGREEMENT. The provider agrees to perform maintenance agreement bookkeeping services for the client on a monthly basis, with no transfer of existing client staff or internal functions.",
        "SERVICE AGREEMENT. The provider will take over responsibility for a broad scope of the client's customer support operations, including several client staff members transitioning to the provider's payroll.",
        "large-scope service contract with partial staff transition",
    ),
    (
        "employment_contract", "employment_termination_agreement",
        "EMPLOYMENT CONTRACT. Employee shall commence employment on the start date below and perform the ongoing duties described in Schedule A in exchange for the compensation set forth herein.",
        "SEPARATION AGREEMENT. This agreement sets forth the terms of employee's termination, including final pay, release of claims, and the effective end date of employment (PHK).",
        "EMPLOYMENT CONTRACT. Employee's ongoing duties are set forth in Schedule A; this contract also includes a standard termination-for-cause clause permitting dismissal for serious misconduct.",
        "ongoing employment contract with a routine termination-for-cause clause",
    ),
    (
        "agency_agreement", "sales_representative_agreement",
        "AGENCY AGREEMENT. The agent is granted authority to conclude and bind transactions on behalf of the principal, negotiating and executing contracts directly with customers in the principal's name.",
        "SALES REPRESENTATIVE AGREEMENT. The sales representative shall promote and sell the principal's products on a commission-only basis, with no authority to negotiate or bind the principal to any contract.",
        "SALES REPRESENTATIVE AGREEMENT. The representative shall sell products on commission, and is additionally granted limited authority to negotiate discount terms directly with customers.",
        "commission sales rep with limited negotiation authority",
    ),
    (
        "consulting_agreement", "freelance_contract",
        "CONSULTING AGREEMENT. Consultant shall provide expert strategic advice and recommendations to the client's management team regarding market entry strategy, in an advisory capacity.",
        "INDEPENDENT CONTRACTOR AGREEMENT. Contractor shall complete the specific deliverables set forth in Schedule A, including a functioning website and three milestone deliverables, on a freelance basis.",
        "INDEPENDENT CONTRACTOR AGREEMENT. Contractor shall provide consulting services, delivering a final strategy report as the sole milestone deliverable under this freelance engagement.",
        "freelance deliverable framed as a consulting engagement",
    ),
    (
        "cooperation_agreement", "partnership_agreement",
        "COOPERATION AGREEMENT. The parties agree to collaborate on the joint research project described herein, without forming any new entity and without any profit-sharing arrangement between them.",
        "PARTNERSHIP AGREEMENT. The partners hereby form a general partnership, contributing capital as set forth in Schedule A and sharing all profits and losses of the partnership business.",
        "COOPERATION AGREEMENT. The parties agree to collaborate on the joint project, and further agree to share a limited percentage of any profits arising directly from the collaboration.",
        "cooperation agreement with a limited profit-sharing clause",
    ),
    (
        "banking_facility_agreement", "loan_agreement",
        "CREDIT FACILITY AGREEMENT. Bank grants borrower a revolving credit facility of up to $1,000,000, subject to OJK regulations, with drawdowns available at borrower's discretion during the facility period.",
        "LOAN AGREEMENT. Lender agrees to loan borrower the principal amount of $50,000, to be disbursed in a single payment and repaid according to the schedule in Schedule A. Lender is a private individual, not a bank.",
        "LOAN AGREEMENT. Bank agrees to loan borrower the principal amount of $50,000 as a single disbursement, to be repaid according to the schedule in Schedule A.",
        "bank-issued single-disbursement term loan (bank vs. facility-structure boundary)",
    ),
]


def _classify(text):
    result = classify_document_type(text)
    label = result.get("label")
    resolved = profile_registry.detect_profile(label) if label else None
    return (resolved.get("id") if resolved else None), label


def run():
    print("=" * 70)
    print("  CLASSIFIER COLLISION-PAIR TEST (2026-07-20/21)")
    print("=" * 70)

    pass_a = pass_b = 0
    rows = []

    for i, (profile_a, profile_b, text_a, text_b, text_border, border_note) in enumerate(PAIRS, start=1):
        id_a, label_a = _classify(text_a)
        id_b, label_b = _classify(text_b)
        id_border, label_border = _classify(text_border)

        ok_a = id_a == profile_a
        ok_b = id_b == profile_b
        pass_a += int(ok_a)
        pass_b += int(ok_b)

        collided_a = id_a == profile_b
        collided_b = id_b == profile_a

        rows.append({
            "pair": i, "profile_a": profile_a, "profile_b": profile_b,
            "a_result": {"pass": ok_a, "resolved_id": id_a, "label": label_a, "collided_with_b": collided_a},
            "b_result": {"pass": ok_b, "resolved_id": id_b, "label": label_b, "collided_with_a": collided_b},
            "borderline": {"note": border_note, "resolved_id": id_border, "label": label_border},
        })

        print(f"[{i}] {profile_a} vs {profile_b}")
        print(f"  A-signal -> {'PASS' if ok_a else 'FAIL'} (resolved={id_a}, label={label_a!r})" + (" [collided with B]" if collided_a else ""))
        print(f"  B-signal -> {'PASS' if ok_b else 'FAIL'} (resolved={id_b}, label={label_b!r})" + (" [collided with A]" if collided_b else ""))
        print(f"  borderline ({border_note}) -> resolved={id_border}, label={label_border!r} (informational, no assertion)")
        print("-" * 70)

    total = len(PAIRS)
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"Pairs tested                 : {total}/13")
    print(f"A-signal correctly resolved  : {pass_a}/{total}")
    print(f"B-signal correctly resolved  : {pass_b}/{total}")
    print("Borderline cases: reported only, no pass/fail (ambiguous by design per classifier_collision_pairs.md)")
    print()
    print("Note: most B/A-side profiles here are registry status=draft. A FAIL is a")
    print("classifier-accuracy finding for Ilham/Afridho triage -- not a silent-wrong-")
    print("result risk in the running pilot, since worker._needs_confirmation()'s")
    print("draft_profile gate already forces human confirmation on any non-validated")
    print("resolved profile regardless of this script's outcome.")

    report = {"total_pairs": total, "a_pass": pass_a, "b_pass": pass_b, "rows": rows}
    out_path = Path(HERE) / "collision_pairs_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {out_path}")


if __name__ == "__main__":
    run()
