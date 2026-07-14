import time
import json
from app.protection.legal_protection import LegalProtectionEngine
from app.protection.glossary_engine import GlossaryEngine, GlossaryTerm
from app.services.quality_analyzer import TranslationQualityAnalyzer


def run_benchmark():
    print("==================================================")
    print("        MICRO-BENCHMARK: SPRINT 5 ENGINES        ")
    print("==================================================")

    # Sample Legal Text
    sample_legal_text = (
        "Pasal 4: Ketentuan Umum.\n\n"
        "1. PT Sydeco Global (selanjutnya disebut \"Pihak Pertama\") dan Kementerian Keuangan "
        "(selanjutnya disebut \"Pihak Kedua\") sepakat untuk melakukan transaksi sebesar USD 1,500,000 "
        "pada tanggal 12-07-2026. Transaksi ini diatur oleh UU No. 13/2003 tentang Ketenagakerjaan.\n\n"
        "2. Pihak Pertama wajib menyerahkan kode sumber (source code) dan lisensi perangkat lunak "
        "kepada Pihak Kedua. Pihak Kedua berhak untuk membatalkan perjanjian jika terjadi wanprestasi "
        "oleh Pihak Pertama. Email kontak resmi adalah legal@sydeco.com dan nomor telepon +62-21-5555123."
    )

    sample_translation_text = (
        "Article 4: General Provisions.\n\n"
        "1. PT Sydeco Global (hereinafter referred to as \"First Party\") and Ministry of Finance "
        "(hereinafter referred to as \"Second Party\") agree to perform a transaction of USD 1,500,000 "
        "on 12-07-2026. This transaction is governed by Law No. 13/2003 concerning Labor.\n\n"
        "2. First Party shall deliver the source code and software license "
        "to Second Party. Second Party has the right to terminate the agreement if breach of contract "
        "occurs by First Party. Official contact email is legal@sydeco.com and phone number +62-21-5555123."
    )

    iterations = 500

    # 1. Benchmark Legal Protection Engine
    protection_engine = LegalProtectionEngine()
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        protected_text, p_map = protection_engine.protect(sample_legal_text)
        restored = protection_engine.restore(protected_text, p_map)
    duration_protect = (time.perf_counter() - start_time) / iterations * 1000
    
    # 2. Benchmark Glossary Engine
    glossary_engine = GlossaryEngine()
    # Add a decent number of terms to simulate database size
    for i in range(100):
        glossary_engine._glossaries.setdefault(("id", "en"), []).append(
            GlossaryTerm(f"term_{i}", f"translation_{i}", "Legal", "1.0", 1.0)
        )
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        injected, r_map, _ = glossary_engine.inject_glossary(sample_legal_text, "id", "en", sector="Legal")
        restored = glossary_engine.restore_glossary(injected, r_map)
    duration_glossary = (time.perf_counter() - start_time) / iterations * 1000

    # 3. Benchmark Quality Analyzer
    quality_analyzer = TranslationQualityAnalyzer()
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        qa_result = quality_analyzer.analyze(
            source_text=sample_legal_text,
            translated_text=sample_translation_text,
            source_lang="id",
            target_lang="en",
            avg_confidence=0.98,
            glossary_map={"__GLOS_TERM_0__": "First Party", "__GLOS_TERM_1__": "Second Party"}
        )
    duration_qa = (time.perf_counter() - start_time) / iterations * 1000

    # Output Results
    results = {
        "iterations": iterations,
        "legal_protection_engine_ms": round(duration_protect, 4),
        "glossary_engine_ms": round(duration_glossary, 4),
        "quality_analyzer_ms": round(duration_qa, 4)
    }

    print(json.dumps(results, indent=2))
    print("==================================================")
    
    # Save report
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_sprint5.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Also write a markdown report
    with open("reports/benchmark_sprint5.md", "w") as f:
        f.write("# Sprint 5 Engine Benchmark Report\n\n")
        f.write(f"- **Iterations**: {iterations}\n")
        f.write(f"- **Legal Protection Engine (Protect + Restore)**: {duration_protect:.4f} ms per doc\n")
        f.write(f"- **Glossary Engine (Inject + Restore)**: {duration_glossary:.4f} ms per doc\n")
        f.write(f"- **Quality Analyzer (Analyze)**: {duration_qa:.4f} ms per doc\n")


if __name__ == "__main__":
    run_benchmark()
