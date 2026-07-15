import sys
sys.path.insert(0, "/app")
from detector.detector_distilbert import _load_model, _entailment_score, load_doc_type_specs

model, tokenizer = _load_model()

premise = """WORK PROMISE

Between CV Teknologi Nusantara (Pemberi Kerja) and Dewi Rahayu (Work).

Pasal 1 - Identitas Para Pihak
CV Teknologi Nusantara address on Surabaya. Worker: Dewi Rahayu.

Pasal 2 - Jabatan
Pekerja is appointed as Data Analyst based on bill Ketenagakerjaan No. 13 Year 2003."""

for spec in load_doc_type_specs():
    score = _entailment_score(model, tokenizer, premise, spec["hypothesis"])
    print(f"{spec['label']}: {score:.4f}")
