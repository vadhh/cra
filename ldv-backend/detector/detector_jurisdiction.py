import re

# Deteksi hukum negara dari isi dokumen
def detect_jurisdiction(text):
    # First check explicit governing law clauses
    gov_law_patterns = [
        (r"laws?\s+of\s+(?:the\s+)?republic\s+of\s+indonesia|hukum\s+(?:negara\s+)?indonesia", "Indonesia"),
        (r"laws?\s+of\s+belgium|droit\s+belge|belgisch\s+recht", "Belgium"),
        (r"laws?\s+of\s+france|droit\s+fran[çc]ais", "France"),
        (r"laws?\s+of\s+the\s+netherlands|nederlands\s+recht", "Netherlands"),
        (r"laws?\s+of\s+england(?:\s+and\s+wales)?|english\s+law", "England & Wales"),
        (r"laws?\s+of\s+(?:the\s+)?united\s+states|us\s+law|delaware\s+law", "United States"),
    ]
    for pat, country in gov_law_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return country

    country_keywords = {
        "Indonesia": ["UU", "Pasal", "Peraturan Menteri", "Ketenagakerjaan"],
        "Belgium": ["Code civil", "Belgique", "employé", "loi"],
        "France": ["Code du travail", "France", "employé", "loi"],
        "Netherlands": ["Nederland", "arbeidsovereenkomst", "wet", "BW"],
        "England & Wales": ["England", "Wales", "English law", "London"],
        "United States": ["United States", "Delaware", "State of New York"]
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