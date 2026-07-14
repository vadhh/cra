import time
import json
import numpy as np
import resource
import os
from app.services.translation_service import TranslationService

# Define sample documents

SHORT_DOC = (
    "HUUROVEREENKOMST KANTOORRUIMTE\n\n"
    "Artikel 1: Partijen\n"
    "PT Sydeco Global, gevestigd te Yogyakarta (Verhuurder), en "
    "Ministry of Finance (Huurder), "
    "komen overeen dat de huurprijs USD 2,500 per maand bedraagt, ingaande op 12-07-2026."
)

MEDIUM_DOC = "\n\n".join([
    "ALGEMENE DIENSTVERLENINGSOVEREENKOMST",
    "Artikel 2: Onderwerp van de Overeenkomst\n"
    "1. De Dienstverlener zal softwareontwikkelingsdiensten leveren aan de Cliënt onder de voorwaarden van deze \"Overeenkomst\".\n"
    "2. De diensten omvatten het opleveren van de broncode (source code) van de applicatie op 15-08-2026.",
    "Artikel 3: Tarieven en Betaling\n"
    "1. De totale contractwaarde bedraagt EUR 45.000, exclusief btw. Betaling geschiedt in termijnen:\n"
    "   * Eerste termijn van 50% bij ondertekening;\n"
    "   * Tweede termijn van 50% bij acceptatie.",
    "De contactpersonen voor deze overeenkomst zijn:\n"
    "   * Voor Verhuurder: Mr. John Doe (john.doe@sydeco.com)\n"
    "   * Voor Huurder: Ms. Sarah Smith (sarah.smith@finance.gov)\n"
    "Telefoonnummer voor noodgevallen: +31-20-555-0199."
])

LARGE_DOC = "\n\n".join([
    "AANDEELHOUDERSOVEREENKOMST",
    "Deze Aandeelhoudersovereenkomst (\"Overeenkomst\") is aangegaan op 12-07-2026 door en tussen:\n"
    "1. Mr. Robert Smith, wonende te Londen (Aandeelhouder A); en\n"
    "2. PT Sydeco Global, gevestigd te Jakarta (Aandeelhouder B).",
    "Artikel 1: Definities en Interpretatie\n"
    "In deze Overeenkomst hebben de volgende termen de onderstaande betekenis:\n"
    "   * \"Aandelen\": de gewone aandelen in het kapitaal van de Vennootschap;\n"
    "   * \"Raad van Bestuur\": de raad van bestuur van de Vennootschap;\n"
    "   * \"Algemene Vergadering\": de algemene vergadering van aandeelhouders.",
    "Artikel 2: Doel en Activiteiten van de Vennootschap\n"
    "Het doel van de Vennootschap is het ontwikkelen, exploiteren en verkopen van beveiligingssoftware en gerelateerde IT-diensten.",
    "Artikel 3: Financiering en Aandelenkapitaal\n"
    "1. Het geplaatste kapitaal bedraagt USD 1.000.000, verdeeld over 1.000.000 aandelen met een nominale waarde van USD 1,00 elk.\n"
    "2. Aandeelhouder A houdt 60% van de aandelen en Aandeelhouder B houdt 40% van de aandelen.",
    "Artikel 4: Bestuur en Besluitvorming\n"
    "1. De Raad van Bestuur bestaat uit drie (3) leden. Aandeelhouder A heeft het recht om twee bestuurders te benoemen, en Aandeelhouder B heeft het recht om één bestuurder te benoemen.\n"
    "2. Belangrijke besluiten vereisen een voorafgaande goedkeuring van de Algemene Vergadering met een meerderheid van ten minste 75% van de stemmen.",
    "Artikel 5: Overdracht van Aandelen en Aanbiedingsplicht\n"
    "1. Indien een aandeelhouder zijn aandelen wenst over te dragen, dient hij deze eerst schriftelijk aan te bieden aan de andere aandeelhouders.\n"
    "2. De prijs van de aandelen wordt in onderling overleg vastgesteld of, bij gebreke daarvan, door een accountant.",
    "Artikel 6: Geheimhouding en Concurrentiebeding\n"
    "1. Partijen verplichten zich tot strikte geheimhouding van alle vertrouwelijke informatie die zij in het kader van deze Overeenkomst verkrijgen.\n"
    "2. Het is aandeelhouders niet toegestaan om gedurende de looptijd van deze Overeenkomst en gedurende een periode van twee (2) jaar daarna concurrerende activiteiten te ontplooien.",
    "Artikel 7: Duur en Beëindiging\n"
    "Deze Overeenkomst treedt in werking op de datum van ondertekening en blijft van kracht totdat de Vennootschap wordt ontbonden of wanneer alle aandelen in handen zijn van één partij.",
    "Artikel 8: Toepasselijk Recht en Geschillenbeslechting\n"
    "Op deze Overeenkomst is uitsluitend Nederlands recht van toepassing. Alle geschillen zullen worden voorgelegd aan de bevoegde rechter te Amsterdam."
])

def get_memory_usage_mb():
    try:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except Exception:
        return 0.0

def run_benchmark_for_doc(service, doc_text, doc_name, iterations):
    print(f"\nRunning benchmark for {doc_name} ({iterations} iterations)...", flush=True)
    latencies = []
    cpu_times = []
    throughputs = []
    
    # Warmup run
    print("  Warmup run...", flush=True)
    service.translate_document(doc_text, "nl", "en", preserve_formatting=True)
    
    mem_before = get_memory_usage_mb()
    word_count = len(doc_text.split())
    
    for i in range(iterations):
        # Clear translation cache
        service._translation_cache.cache.clear()
        
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        
        service.translate_document(doc_text, "nl", "en", preserve_formatting=True)
        
        dur_cpu = (time.process_time() - start_cpu) * 1000
        dur_wall = (time.perf_counter() - start_time) * 1000
        
        latencies.append(dur_wall)
        cpu_times.append(dur_cpu)
        
        # Throughput in words per second
        words_per_sec = word_count / (dur_wall / 1000.0) if dur_wall > 0 else 0
        throughputs.append(words_per_sec)
        
        print(f"    Iteration {i+1}/{iterations}: Wall={dur_wall:.2f} ms, CPU={dur_cpu:.2f} ms, Throughput={words_per_sec:.2f} words/sec", flush=True)
        
    mem_after = get_memory_usage_mb()
    mem_diff = max(0.0, mem_after - mem_before)
    
    # Calculate statistics
    avg_lat = np.mean(latencies)
    min_lat = np.min(latencies)
    max_lat = np.max(latencies)
    p50_lat = np.percentile(latencies, 50)
    p95_lat = np.percentile(latencies, 95)
    
    avg_cpu = np.mean(cpu_times)
    avg_throughput = np.mean(throughputs)
    
    # Peak resident set size (maxrss) tracks the maximum memory used in process lifetime
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    
    results = {
        "document_name": doc_name,
        "word_count": word_count,
        "iterations": iterations,
        "latency_ms": {
            "average": round(avg_lat, 2),
            "minimum": round(min_lat, 2),
            "maximum": round(max_lat, 2),
            "p50": round(p50_lat, 2),
            "p95": round(p95_lat, 2)
        },
        "cpu_time_ms": {
            "average": round(avg_cpu, 2),
            "values": [round(c, 2) for c in cpu_times]
        },
        "throughput_words_per_sec": {
            "average": round(avg_throughput, 2),
            "values": [round(t, 2) for t in throughputs]
        },
        "memory_usage_mb": {
            "rss_before": round(mem_before, 2),
            "rss_after": round(mem_after, 2),
            "rss_increase": round(mem_diff, 2),
            "peak_rss": round(peak_rss, 2)
        }
    }
    
    print(f"  Results for {doc_name}:", flush=True)
    print(f"    Avg Wall Latency: {avg_lat:.2f} ms", flush=True)
    print(f"    Avg CPU Time:     {avg_cpu:.2f} ms", flush=True)
    print(f"    Avg Throughput:   {avg_throughput:.2f} words/sec", flush=True)
    print(f"    Peak RSS Memory:  {peak_rss:.2f} MB", flush=True)
    
    return results

def main():
    service = TranslationService()
    
    short_res = run_benchmark_for_doc(service, SHORT_DOC, "Short Document", 1)
    medium_res = run_benchmark_for_doc(service, MEDIUM_DOC, "Medium Document", 1)
    large_res = run_benchmark_for_doc(service, LARGE_DOC, "Large Document", 1)
    
    summary = {
        "short_document": short_res,
        "medium_document": medium_res,
        "large_document": large_res
    }
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_results.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    print("\nBenchmark completed successfully. Results saved to reports/benchmark_results.json", flush=True)

if __name__ == "__main__":
    main()
