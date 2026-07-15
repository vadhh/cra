import sys
sys.path.insert(0, "/app")
from detector.detector_distilbert import _load_model, _classify_doc_type
from langdetect import detect
from translator import translate_text

with open("/app/tests/fixtures/txt/01_employment_id.txt", "r", encoding="utf-8") as f:
    text = f.read()

lang = detect(text)
translated = translate_text(text, "en", src_lang=lang)
premise = translated[:800].strip()
print(f"Premise snippet: {premise[:300]}")

model, tokenizer = _load_model()
candidates = _classify_doc_type(model, tokenizer, premise)
print("NLI candidates:")
for c in candidates:
    print(f"  {c['label']}: {c['confidence']}")
