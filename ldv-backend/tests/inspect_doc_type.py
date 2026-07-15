import sys
sys.path.insert(0, "/app")
from detector.detector_distilbert import classify_document_type
from langdetect import detect
from translator import translate_text

with open("/app/tests/fixtures/txt/01_employment_id.txt", "r", encoding="utf-8") as f:
    text = f.read()

lang = detect(text)
translated = translate_text(text, "en", src_lang=lang)
res = classify_document_type(translated)
print("Classification Result:")
import pprint
pprint.pprint(res)
