import re

# Deteksi hukum negara dari isi dokumen
def detect_jurisdiction(text):
    country_keywords = {
        "Indonesia": ["UU", "Pasal", "Peraturan Menteri", "Ketenagakerjaan"],
        "Belgium": ["Code civil", "Belgique", "employé", "loi"],
        "France": ["Code du travail", "France", "employé", "loi"],
        "Netherlands": ["Nederland", "arbeidsovereenkomst", "wet", "BW"]
    }
    scores = {}
    for country, keywords in country_keywords.items():
        count = sum(
            1 for kw in keywords
            if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE)
        )
        if count > 0:
            scores[country] = count
    if not scores:
        return "Unknown"
    return max(scores, key=scores.get)