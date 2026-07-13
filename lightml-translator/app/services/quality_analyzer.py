import re
from typing import Dict, List, Tuple, Any


class TranslationQualityAnalyzer:
    """
    Quality Assurance and Risk Scorer for Legal Translations.
    Compares source document structures with translation targets to audit numbers,
    percentages, dates, currencies, negations, duplicates, legal meaning, and glossary alignment.
    """

    def __init__(self):
        # Numeric and structural patterns
        self._number_regex = re.compile(r"\b\d+(?:[.,]\d+)*\b")
        self._percent_regex = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|persen)\b", re.I)
        
        # Currency prefixes and codes
        self._currency_regex = re.compile(r"\b(?:Rp\.?|USD|EUR|IDR|\$|€)\b", re.I)
        
        # Date regex for common formats
        self._date_regex = re.compile(
            r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December"
            r"|Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember"
            r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b"
            r"|\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b",
            re.I
        )

        # Negation lists for source and target languages
        self._negations = {
            "id": ["tidak", "bukan", "jangan", "tanpa", "tiada", "dilarang"],
            "en": ["not", "no", "never", "without", "prohibited", "neither", "nor", "cannot"],
            "fr": ["ne", "pas", "non", "jamais", "sans", "interdit", "ni"],
            "nl": ["niet", "geen", "nooit", "zonder", "verboden", "noch"]
        }
        
        # Critical legal modalities to detect shifting obligations (mandatory vs discretionary)
        self._legal_modalities = {
            "id": {
                "wajib": "mandatory", "harus": "mandatory", 
                "dapat": "discretionary", "boleh": "discretionary",
                "hak": "discretionary", "wenang": "discretionary"
            },
            "en": {
                "shall": "mandatory", "must": "mandatory", "obligated": "mandatory", "required": "mandatory",
                "may": "discretionary", "should": "discretionary", "optional": "discretionary", "can": "discretionary"
            },
            "fr": {
                "doit": "mandatory", "doivent": "mandatory", "obligatoire": "mandatory",
                "peut": "discretionary", "peuvent": "discretionary", "optionnel": "discretionary"
            },
            "nl": {
                "moet": "mandatory", "moeten": "mandatory", "verplicht": "mandatory",
                "kan": "discretionary", "kunnen": "discretionary", "optioneel": "discretionary"
            }
        }

    def _normalize_date(self, date_str: str) -> List[int]:
        months_map = {
            "jan": 1, "januari": 1, "january": 1,
            "feb": 2, "februari": 2, "february": 2,
            "mar": 3, "maret": 3, "march": 3,
            "apr": 4, "april": 4,
            "mei": 5, "may": 5,
            "jun": 6, "juni": 6, "june": 6,
            "jul": 7, "juli": 7, "july": 7,
            "aug": 8, "agustus": 8, "august": 8,
            "sep": 9, "september": 9,
            "oct": 10, "oktober": 10, "october": 10,
            "nov": 11, "november": 11,
            "dec": 12, "desember": 12, "december": 12
        }
        tokens = re.findall(r"\b\w+\b", date_str.lower())
        values = []
        for tok in tokens:
            if tok.isdigit():
                values.append(int(tok))
            elif tok in months_map:
                values.append(months_map[tok])
        return sorted(values)

    def analyze(
        self, 
        source_text: str, 
        translated_text: str, 
        source_lang: str, 
        target_lang: str,
        avg_confidence: float = 1.0,
        glossary_map: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Audits translation quality by comparing source and translated texts.
        
        Returns:
            Dict containing:
                - quality_score: float (0.0 to 100.0)
                - warnings: List[str]
                - risk_level: str ("LOW", "MEDIUM", "HIGH", "CRITICAL")
                - confidence: float
                - report: Dict[str, Any]
        """
        score = 100.0
        warnings = []

        # Pre-clean strings
        src = source_text.strip()
        trans = translated_text.strip()

        # 1. Audit missing content / sentences
        src_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', src) if s.strip()]
        trans_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', trans) if s.strip()]
        
        missing_count = len(src_sentences) - len(trans_sentences)
        if missing_count > 0:
            score -= (missing_count * 10.0)
            warnings.append(f"Missing text detected: Translation has {missing_count} fewer sentence(s) than the source.")

        # 2. Audit changed dates
        src_dates = self._date_regex.findall(src)
        trans_dates = self._date_regex.findall(trans)
        
        src_norm_dates = [self._normalize_date(d) for d in src_dates]
        trans_norm_dates = [self._normalize_date(d) for d in trans_dates]
        
        missing_dates = []
        for d, norm_d in zip(src_dates, src_norm_dates):
            if norm_d not in trans_norm_dates:
                missing_dates.append(d)
                
        if missing_dates:
            score -= len(missing_dates) * 15.0
            warnings.append(f"Date mismatch: The dates {missing_dates} from source were not preserved in the translation.")

        # 3. Audit changed numbers
        src_numbers = self._number_regex.findall(src)
        trans_numbers = self._number_regex.findall(trans)
        
        # Check standard values (ignoring formatting commas/periods), excluding date parts to prevent double-counting
        # We can exclude numbers that are substrings of any matched date
        def get_date_nums(dates_list):
            nums = []
            for d in dates_list:
                nums.extend(re.findall(r"\b\d+\b", d))
            return set(nums)

        src_date_nums = get_date_nums(src_dates)
        trans_date_nums = get_date_nums(trans_dates)

        clean_src_nums = [n.replace(",", "").replace(".", "") for n in src_numbers if n not in src_date_nums]
        clean_trans_nums = [n.replace(",", "").replace(".", "") for n in trans_numbers if n not in trans_date_nums]
        
        missing_numbers = [num for num in clean_src_nums if num not in clean_trans_nums]
        if missing_numbers:
            penalty = len(missing_numbers) * 15.0
            score -= penalty
            warnings.append(f"Number mismatch: Standalone numbers {missing_numbers} from the source are missing or modified in the translation.")

        # 4. Audit changed percentages
        src_percents = [p.lower().replace(" ", "") for p in self._percent_regex.findall(src)]
        trans_percents = [p.lower().replace(" ", "") for p in self._percent_regex.findall(trans)]
        
        src_percent_vals = [re.sub(r"[^\d]", "", p) for p in src_percents]
        trans_percent_vals = [re.sub(r"[^\d]", "", p) for p in trans_percents]
        
        missing_percents = [p for p in src_percent_vals if p not in trans_percent_vals]
        if missing_percents:
            score -= len(missing_percents) * 15.0
            warnings.append(f"Percentage mismatch: Mismatched percentage values detected.")

        # 5. Audit changed currencies
        src_currencies = [c.upper() for c in self._currency_regex.findall(src)]
        trans_currencies = [c.upper() for c in self._currency_regex.findall(trans)]
        sym_map = {"$": "USD", "€": "EUR", "RP": "IDR"}
        src_mapped = {sym_map.get(c, c) for c in src_currencies}
        trans_mapped = {sym_map.get(c, c) for c in trans_currencies}
        
        missing_currencies = src_mapped - trans_mapped
        if missing_currencies:
            score -= len(missing_currencies) * 10.0
            warnings.append(f"Currency mismatch: Source currencies {list(missing_currencies)} were not preserved in the translation.")

        # 6. Audit negations (Polarity check)
        src_neg_words = self._negations.get(source_lang.lower(), [])
        trans_neg_words = self._negations.get(target_lang.lower(), [])
        
        src_neg_count = sum(1 for w in src.lower().split() if w in src_neg_words)
        trans_neg_count = sum(1 for w in trans.lower().split() if w in trans_neg_words)
        
        if (src_neg_count > 0 and trans_neg_count == 0) or (src_neg_count == 0 and trans_neg_count > 0):
            score -= 25.0
            warnings.append("CRITICAL: Negation mismatch. Polarity (negative vs. positive statement) might have changed in translation.")

        # 7. Audit changed legal meaning (Obligation shifts in modality, negation-aware)
        src_mod_map = self._legal_modalities.get(source_lang.lower(), {})
        trans_mod_map = self._legal_modalities.get(target_lang.lower(), {})
        src_negs = self._negations.get(source_lang.lower(), [])
        trans_negs = self._negations.get(target_lang.lower(), [])
        
        src_mandatory = 0
        src_discretionary = 0
        src_words = re.findall(r"\b\w+\b", src.lower())
        for idx, word in enumerate(src_words):
            if word in src_mod_map:
                prev_neg = idx > 0 and src_words[idx - 1] in src_negs
                mod_type = src_mod_map[word]
                if mod_type == "mandatory":
                    src_mandatory += 1
                elif mod_type == "discretionary":
                    if prev_neg:
                        # "tidak boleh" / "not allowed" -> mandatory (prohibited)
                        src_mandatory += 1
                    else:
                        src_discretionary += 1

        trans_mandatory = 0
        trans_discretionary = 0
        trans_words = re.findall(r"\b\w+\b", trans.lower())
        for idx, word in enumerate(trans_words):
            if word in trans_mod_map:
                prev_neg = idx > 0 and trans_words[idx - 1] in trans_negs
                mod_type = trans_mod_map[word]
                if mod_type == "mandatory":
                    trans_mandatory += 1
                elif mod_type == "discretionary":
                    if prev_neg:
                        trans_mandatory += 1
                    else:
                        trans_discretionary += 1

        modality_mismatch_count = 0
        modality_warnings = []
        if src_mandatory > trans_mandatory:
            modality_mismatch_count += (src_mandatory - trans_mandatory)
            modality_warnings.append(f"Legal meaning shift: Source contains {src_mandatory} mandatory obligation(s), but translation only contains {trans_mandatory}.")
        if src_discretionary > trans_discretionary:
            modality_mismatch_count += (src_discretionary - trans_discretionary)
            modality_warnings.append(f"Legal meaning shift: Source contains {src_discretionary} discretionary rights/permissions, but translation only contains {trans_discretionary}.")
            
        if modality_mismatch_count > 0:
            score -= min(30.0, modality_mismatch_count * 10.0)
            warnings.extend(modality_warnings)

        # 8. Audit terminology inconsistency (Glossary alignment)
        glossary_failures = 0
        if glossary_map:
            for placeholder, target_term in glossary_map.items():
                if target_term.lower() not in trans.lower():
                    glossary_failures += 1
            if glossary_failures > 0:
                score -= (glossary_failures * 10.0)
                warnings.append(f"Terminology inconsistency: {glossary_failures} glossary term(s) were not found in the translated text.")

        # 9. Audit repeated translations (Hallucination looping)
        consecutive_repeats = 0
        for i in range(len(trans_sentences) - 1):
            if trans_sentences[i] == trans_sentences[i+1] and len(trans_sentences[i]) > 10:
                consecutive_repeats += 1
        if consecutive_repeats > 0:
            score -= 20.0
            warnings.append("MT Loop detected: Consecutive duplicate sentences detected in the output.")

        # 10. Audit low confidence
        if avg_confidence < 0.65:
            score -= 15.0
            warnings.append(f"Low translation confidence: Model returned a low probability score ({avg_confidence:.2f}).")

        # Bounds check score
        score = max(0.0, min(100.0, score))

        # Classify risk level
        if score >= 85.0:
            risk = "LOW"
        elif score >= 60.0:
            risk = "MEDIUM"
        elif score >= 40.0:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        report = {
            "sentence_count_source": len(src_sentences),
            "sentence_count_target": len(trans_sentences),
            "missing_sentences": max(0, missing_count),
            "number_mismatches": len(missing_numbers),
            "percentage_mismatches": len(missing_percents),
            "date_mismatches": len(missing_dates),
            "currency_mismatches": len(missing_currencies),
            "negation_mismatches": abs(src_neg_count - trans_neg_count) if (src_neg_count == 0 or trans_neg_count == 0) and src_neg_count != trans_neg_count else 0,
            "modality_mismatches": modality_mismatch_count,
            "glossary_mismatches": glossary_failures,
            "repetition_loops": consecutive_repeats,
            "model_confidence": round(avg_confidence, 4)
        }

        return {
            "quality_score": round(score, 2),
            "warnings": warnings,
            "risk_level": risk,
            "confidence": round(avg_confidence, 4),
            "report": report
        }
