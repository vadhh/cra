"""Legal Benchmark Runner for PT Sydeco Contract Risk Analyzer (CR-05/07/08).

Evaluates the L1-L3 analysis pipeline accuracy, precision, and recall
across the standard benchmark fixtures set.
"""
import os
import sys
import json
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, BACKEND_DIR)

from app import _run_analysis, _extract_pdf, _extract_docx, _extract_txt
from detector.detector_jurisdiction import detect_jurisdiction
from langdetect import detect

FIXTURES_DIR = Path(HERE) / "fixtures"

BENCHMARK_SUITE = [
    {
        "path": "pdf/01_employment_id.pdf",
        "expected": {
            "language": "id",
            "jurisdiction": "Indonesia",
            "document_type": "employment contract",
            "is_contract": True,
            "present_clauses": ["governing_law", "termination", "working_hours", "compensation"],
            "missing_clauses": ["jurisdiction_venue", "notice_period", "dispute_resolution"]
        }
    },
    {
        "path": "pdf/02_lease_be.pdf",
        "expected": {
            "language": "fr",
            "jurisdiction": "Belgium",
            "document_type": "lease agreement",
            "is_contract": True,
            "present_clauses": ["governing_law", "termination", "rent_amount", "security_deposit"],
            "missing_clauses": ["jurisdiction_venue", "lease_term", "maintenance_responsibility", "dispute_resolution"]
        }
    },
    {
        "path": "pdf/03_nda_en.pdf",
        "expected": {
            "language": "en",
            "jurisdiction": "England",
            "document_type": "non-disclosure agreement",
            "is_contract": True,
            "present_clauses": ["governing_law", "termination", "confidentiality"],
            "missing_clauses": ["jurisdiction_venue", "return_of_materials", "dispute_resolution"]
        }
    },
    {
        "path": "pdf/04_incomplete_en.pdf",
        "expected": {
            "language": "en",
            "jurisdiction": "Unknown",
            "document_type": "software license",
            "is_contract": True,
            "missing_clauses": ["governing_law", "jurisdiction_venue", "termination", "dispute_resolution", "limitation_liability"]
        }
    },
    {
        "path": "pdf/05_brochure_en.pdf",
        "expected": {
            "language": "en",
            "is_contract": False
        }
    }
]

def extract_text(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    data = file_path.read_bytes()
    if ext == ".pdf":
        return _extract_pdf(data)
    elif ext == ".docx":
        return _extract_docx(data)
    elif ext in (".txt", ".html"):
        return _extract_txt(data)
    else:
        raise ValueError(f"Unsupported benchmark file extension: {ext}")

def run_benchmark():
    print("=" * 60)
    print("   PT SYDECO CONTRACT RISK ANALYZER - LEGAL BENCHMARK RUNNER")
    print("=" * 60)
    
    results = []
    
    # Metrics counters
    lang_correct = 0
    juris_correct = 0
    type_correct = 0
    is_contract_correct = 0
    
    clause_tp = 0  # True Positive (Expected present, detected present)
    clause_fp = 0  # False Positive (Expected missing, detected present)
    clause_tn = 0  # True Negative (Expected missing, detected missing)
    clause_fn = 0  # False Negative (Expected present, detected missing)

    for case in BENCHMARK_SUITE:
        file_path = FIXTURES_DIR / case["path"]
        if not file_path.exists():
            print(f"WARNING: Benchmark fixture missing: {case['path']}")
            continue
            
        text = extract_text(file_path)
        
        # Run detection
        try:
            lang = detect(text)
        except Exception:
            lang = "unknown"
            
        jurisdiction = detect_jurisdiction(text)
        analysis = _run_analysis(text, jurisdiction, lang)
        
        expected = case["expected"]
        
        # 1. Language Match
        lang_match = (lang.lower() == expected["language"].lower())
        if lang_match:
            lang_correct += 1
            
        # 2. Jurisdiction Match
        # Handle "England" mapping to "England & Wales" or similar
        juris_detected = analysis.get("jurisdiction", "Unknown")
        juris_match = False
        if expected.get("jurisdiction", "Unknown") == "Unknown":
            juris_match = (juris_detected in ("Unknown", "generic"))
        else:
            juris_match = expected.get("jurisdiction", "Unknown").lower() in juris_detected.lower()
            
        if juris_match:
            juris_correct += 1
            
        # 3. Document Type Match
        l2 = analysis.get("layer2") or {}
        doc_type_detected = (l2.get("document_type") or {}).get("label")
        is_contract_detected = (doc_type_detected is not None and analysis.get("layer3", {}).get("skipped") is not True)
        
        is_contract_match = (is_contract_detected == expected["is_contract"])
        if is_contract_match:
            is_contract_correct += 1
            
        type_match = False
        if expected["is_contract"]:
            type_match = (doc_type_detected is not None and expected["document_type"].lower() in doc_type_detected.lower())
            if type_match:
                type_correct += 1
        else:
            type_match = (doc_type_detected is None)
            if type_match:
                type_correct += 1
                
        # 4. Clause Presence Metrics
        clause_details = []
        if expected["is_contract"]:
            presence_list = analysis.get("layer1", {}).get("clause_presence", [])
            presence_map = {c["clause_id"]: c["present"] for c in presence_list}
            
            # Check expected present
            for cid in expected.get("present_clauses", []):
                detected = presence_map.get(cid, False)
                if detected:
                    clause_tp += 1
                    clause_details.append({"clause_id": cid, "status": "TP"})
                else:
                    clause_fn += 1
                    clause_details.append({"clause_id": cid, "status": "FN"})
                    
            # Check expected missing
            for cid in expected.get("missing_clauses", []):
                detected = presence_map.get(cid, False)
                if detected:
                    clause_fp += 1
                    clause_details.append({"clause_id": cid, "status": "FP"})
                else:
                    clause_tn += 1
                    clause_details.append({"clause_id": cid, "status": "TN"})
                    
        results.append({
            "fixture": case["path"],
            "metrics": {
                "language_match": lang_match,
                "language_detected": lang,
                "jurisdiction_match": juris_match,
                "jurisdiction_detected": juris_detected,
                "document_type_match": type_match,
                "document_type_detected": doc_type_detected,
                "is_contract_match": is_contract_match,
                "clause_details": clause_details
            }
        })
        
        print(f"Analyzed: {case['path']}")
        print(f"  - Lang: {lang} (Expected: {expected['language']}) -> {'PASS' if lang_match else 'FAIL'}")
        print(f"  - Juris: {juris_detected} (Expected: {expected.get('jurisdiction', 'Unknown')}) -> {'PASS' if juris_match else 'FAIL'}")
        print(f"  - Type: {doc_type_detected} (Expected: {expected.get('document_type', 'Non-Contract')}) -> {'PASS' if type_match else 'FAIL'}")
        print("-" * 60)

    # Calculate overall metrics
    total_cases = len(BENCHMARK_SUITE)
    lang_accuracy = (lang_correct / total_cases) * 100
    juris_accuracy = (juris_correct / total_cases) * 100
    contract_class_accuracy = (is_contract_correct / total_cases) * 100
    
    # Clause matching precision & recall
    clause_precision = (clause_tp / (clause_tp + clause_fp)) * 100 if (clause_tp + clause_fp) > 0 else 0
    clause_recall = (clause_tp / (clause_tp + clause_fn)) * 100 if (clause_tp + clause_fn) > 0 else 0
    clause_accuracy = ((clause_tp + clause_tn) / (clause_tp + clause_tn + clause_fp + clause_fn)) * 100 if (clause_tp + clause_tn + clause_fp + clause_fn) > 0 else 0

    print("=" * 60)
    print("   BENCHMARK SUMMARY METRICS")
    print("=" * 60)
    print(f"Language Detection Accuracy        : {lang_accuracy:.1f}%")
    print(f"Jurisdiction Detection Accuracy    : {juris_accuracy:.1f}%")
    print(f"Contract vs Non-Contract Accuracy  : {contract_class_accuracy:.1f}%")
    print(f"Clause Presence Detection Accuracy : {clause_accuracy:.1f}%")
    print(f"Clause Detection Precision         : {clause_precision:.1f}%")
    print(f"Clause Detection Recall            : {clause_recall:.1f}%")
    print("=" * 60)

    # Save Markdown report
    report_md_path = Path(HERE) / "benchmark_report.md"
    report_json_path = Path(HERE) / "benchmark_report.json"
    
    md_content = f"""# PT Sydeco Contract Risk Analyzer - Legal Benchmark Report

## 1. Overview Summary Metrics
*   **Language Detection Accuracy**: {lang_accuracy:.1f}%
*   **Jurisdiction Classification Accuracy**: {juris_accuracy:.1f}%
*   **Contract Classification Accuracy**: {contract_class_accuracy:.1f}%
*   **Clause Presence Detection Accuracy**: {clause_accuracy:.1f}%
*   **Clause Detection Precision**: {clause_precision:.1f}% (Avoidance of false positives)
*   **Clause Detection Recall**: {clause_recall:.1f}% (Avoidance of false negatives)

## 2. Clause Matching Details
*   **True Positives (TP)**: {clause_tp} (Expected present, detected present)
*   **True Negatives (TN)**: {clause_tn} (Expected missing, detected missing)
*   **False Positives (FP)**: {clause_fp} (Expected missing, detected present)
*   **False Negatives (FN)**: {clause_fn} (Expected present, detected missing)

## 3. Fixture Analysis Log
"""
    for res in results:
        m = res["metrics"]
        md_content += f"""
### `{res['fixture']}`
*   **Language**: Detected `{m['language_detected']}`, Match: `{'🟢 PASS' if m['language_match'] else '🔴 FAIL'}`
*   **Jurisdiction**: Detected `{m['jurisdiction_detected']}`, Match: `{'🟢 PASS' if m['jurisdiction_match'] else '🔴 FAIL'}`
*   **Document Type**: Detected `{m['document_type_detected']}`, Match: `{'🟢 PASS' if m['document_type_match'] else '🔴 FAIL'}`
"""
        if m["clause_details"]:
            md_content += "*   **Clause Verification Details**:\n"
            for detail in m["clause_details"]:
                status_emoji = {
                    "TP": "🟢 True Positive",
                    "TN": "🟢 True Negative",
                    "FP": "🔴 False Positive (Highlight drift)",
                    "FN": "🔴 False Negative (Missed detection)"
                }.get(detail["status"], detail["status"])
                md_content += f"    - `{detail['clause_id']}`: {status_emoji}\n"

    report_md_path.write_text(md_content, encoding="utf-8")
    report_json_path.write_text(json.dumps({
        "summary": {
            "language_accuracy": lang_accuracy,
            "jurisdiction_accuracy": juris_accuracy,
            "contract_classification_accuracy": contract_class_accuracy,
            "clause_accuracy": clause_accuracy,
            "clause_precision": clause_precision,
            "clause_recall": clause_recall,
            "clause_tp": clause_tp,
            "clause_tn": clause_tn,
            "clause_fp": clause_fp,
            "clause_fn": clause_fn
        },
        "details": results
    }, indent=2), encoding="utf-8")
    
    print(f"Reports saved to:")
    print(f"  - {report_md_path}")
    print(f"  - {report_json_path}")

if __name__ == "__main__":
    run_benchmark()
