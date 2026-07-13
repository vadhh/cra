import csv
import json
import logging
import os
import re
import uuid
import threading
from typing import Dict, Tuple, List, Optional, Any

logger = logging.getLogger(__name__)


class GlossaryTerm:
    """Represents a single glossary terminology entry with metadata for context matching."""
    def __init__(
        self,
        source_term: str,
        target_term: str,
        sector: str = "Legal",
        version: str = "1.0.0",
        confidence: float = 1.0,
        context_words: List[str] = None
    ):
        self.source_term = source_term.strip()
        self.target_term = target_term.strip()
        self.sector = sector.strip()
        self.version = version.strip()
        self.confidence = float(confidence)
        self.context_words = [w.strip().lower() for w in context_words] if context_words else []

    def __repr__(self):
        return f"<GlossaryTerm {self.source_term} -> {self.target_term} ({self.sector})>"


class GlossaryEngine:
    """
    Legal Glossary Engine.
    Manages sector-specific terminology lookup tables for Indonesian, English, French, and Dutch.
    Guarantees term protection during translation using placeholder injections to avoid model drift.
    Thread-safe and context-aware.
    """

    def __init__(self):
        # Nested glossary map: (source_lang, target_lang) -> List[GlossaryTerm]
        self._glossaries: Dict[Tuple[str, str], List[GlossaryTerm]] = {}
        self._lock = threading.RLock()
        
        # Load default embedded glossary terms
        self._load_default_glossary()

    def _load_default_glossary(self):
        """Pre-populates default sector terminology across supported languages (id, en, fr, nl)."""
        default_terms = {
            ("id", "en"): [
                # Legal sector
                GlossaryTerm("perjanjian", "agreement", "Legal", "1.0.0-default", 1.0, ["kontrak", "hukum", "perdata"]),
                GlossaryTerm("pihak pertama", "First Party", "Legal", "1.0.0-default", 1.0, ["kontrak", "perjanjian"]),
                GlossaryTerm("pihak kedua", "Second Party", "Legal", "1.0.0-default", 1.0, ["kontrak", "perjanjian"]),
                GlossaryTerm("wanprestasi", "breach of contract", "Legal", "1.0.0-default", 1.0, ["lalai", "gugat", "rugi"]),
                GlossaryTerm("keadaan memaksa", "force majeure", "Legal", "1.0.0-default", 1.0, ["bencana", "darurat"]),
                GlossaryTerm("domisili hukum", "legal domicile", "Legal", "1.0.0-default", 1.0, ["kantor", "alamat"]),
                # Employment sector
                GlossaryTerm("perjanjian kerja", "employment contract", "Employment", "1.0.0-default", 1.0, ["karyawan", "pegawai", "gaji"]),
                GlossaryTerm("pemberi kerja", "employer", "Employment", "1.0.0-default", 1.0, ["perusahaan", "bos"]),
                GlossaryTerm("pekerja", "employee", "Employment", "1.0.0-default", 1.0, ["buruh", "staf"]),
                GlossaryTerm("pesangon", "severance pay", "Employment", "1.0.0-default", 1.0, ["phk", "pemutusan"]),
                GlossaryTerm("upah lembur", "overtime pay", "Employment", "1.0.0-default", 1.0, ["jam", "ekstra"]),
                # Software sector
                GlossaryTerm("lisensi perangkat lunak", "software license", "Software", "1.0.0-default", 1.0, ["aplikasi", "program"]),
                GlossaryTerm("kode sumber", "source code", "Software", "1.0.0-default", 1.0, ["git", "github", "pemrograman"]),
                GlossaryTerm("hak kekayaan intelektual", "intellectual property rights", "Software", "1.0.0-default", 1.0, ["paten", "merek", "cipta"]),
                # Finance sector
                GlossaryTerm("suku bunga", "interest rate", "Finance", "1.0.0-default", 1.0, ["bank", "pinjaman"]),
                GlossaryTerm("jaminan", "collateral", "Finance", "1.0.0-default", 1.0, ["gadai", "sertifikat"]),
                GlossaryTerm("jatuh tempo", "maturity date", "Finance", "1.0.0-default", 1.0, ["bayar", "tagihan"]),
            ],
            ("fr", "en"): [
                GlossaryTerm("contrat", "contract", "Legal", "1.0.0-default", 1.0, ["loi", "droit"]),
                GlossaryTerm("force majeure", "force majeure", "Legal", "1.0.0-default", 1.0, ["accident", "tempête"]),
                GlossaryTerm("domicile légal", "legal domicile", "Legal", "1.0.0-default", 1.0, ["adresse", "tribunal"]),
                GlossaryTerm("mise en demeure", "formal notice", "Legal", "1.0.0-default", 1.0, ["retard", "obligation"]),
                GlossaryTerm("contrat de travail", "employment contract", "Employment", "1.0.0-default", 1.0, ["salaire", "employé"]),
                GlossaryTerm("employeur", "employer", "Employment", "1.0.0-default", 1.0, ["entreprise", "patron"]),
                GlossaryTerm("salarié", "employee", "Employment", "1.0.0-default", 1.0, ["travailleur", "bureau"]),
                GlossaryTerm("indemnité de licenciement", "severance pay", "Employment", "1.0.0-default", 1.0, ["rupture", "licencié"]),
            ],
            ("nl", "en"): [
                GlossaryTerm("overeenkomst", "agreement", "Legal", "1.0.0-default", 1.0, ["wet", "contract"]),
                GlossaryTerm("overmacht", "force majeure", "Legal", "1.0.0-default", 1.0, ["nood", "crisis"]),
                GlossaryTerm("ingebrekestelling", "notice of default", "Legal", "1.0.0-default", 1.0, ["verzuim", "sommatie"]),
                GlossaryTerm("arbeidsovereenkomst", "employment contract", "Employment", "1.0.0-default", 1.0, ["salaris", "werknemer"]),
                GlossaryTerm("werkgever", "employer", "Employment", "1.0.0-default", 1.0, ["bedrijf", "baas"]),
                GlossaryTerm("werknemer", "employee", "Employment", "1.0.0-default", 1.0, ["arbeider", "personeel"]),
            ]
        }
        
        with self._lock:
            for lang_pair, terms in default_terms.items():
                self._glossaries[lang_pair] = terms

    def load_json(self, filepath: str, source_lang: str, target_lang: str, sector: str, version: str) -> bool:
        """Loads glossary terms from a JSON file."""
        if not os.path.isfile(filepath):
            logger.error(f"Glossary JSON file not found: {filepath}")
            return False
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            new_terms = []
            if isinstance(data, list):
                for obj in data:
                    src_term = obj.get("source_term", "")
                    tgt_term = obj.get("target_term", "")
                    if src_term and tgt_term:
                        new_terms.append(GlossaryTerm(
                            source_term=src_term,
                            target_term=tgt_term,
                            sector=obj.get("sector", sector),
                            version=obj.get("version", version),
                            confidence=obj.get("confidence", 1.0),
                            context_words=obj.get("context_words", [])
                        ))
            elif isinstance(data, dict):
                # Backwards compatible key-value loader
                for src_term, tgt_term in data.items():
                    new_terms.append(GlossaryTerm(
                        source_term=src_term,
                        target_term=tgt_term,
                        sector=sector,
                        version=version,
                        confidence=1.0
                    ))

            lang_key = (source_lang.lower(), target_lang.lower())
            with self._lock:
                if lang_key not in self._glossaries:
                    self._glossaries[lang_key] = []
                self._glossaries[lang_key].extend(new_terms)

            logger.info(f"Loaded JSON glossary {filepath} ({len(new_terms)} terms, Version: {version}, Sector: {sector})")
            return True
        except Exception as e:
            logger.error(f"Failed to load JSON glossary: {e}")
            return False

    def load_csv(self, filepath: str, source_lang: str, target_lang: str, sector: str, version: str) -> bool:
        """Loads glossary terms from a CSV file."""
        if not os.path.isfile(filepath):
            logger.error(f"Glossary CSV file not found: {filepath}")
            return False
            
        try:
            new_terms = []
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    return False
                
                # Check if it has a header like 'source_term' or 'source'
                has_header = any(h.strip().lower() in ["source_term", "source", "target_term", "target"] for h in header)
                if not has_header:
                    # Treat the first row as data
                    f.seek(0)
                    reader = csv.reader(f)

                for row in reader:
                    if len(row) >= 2:
                        src_term = row[0].strip()
                        tgt_term = row[1].strip()
                        if not src_term or not tgt_term:
                            continue
                        
                        sec = row[2].strip() if len(row) > 2 and row[2].strip() else sector
                        conf = float(row[3].strip()) if len(row) > 3 and row[3].strip() else 1.0
                        ctx_words = [w.strip() for w in row[4].split(",")] if len(row) > 4 and row[4].strip() else []
                        
                        new_terms.append(GlossaryTerm(
                            source_term=src_term,
                            target_term=tgt_term,
                            sector=sec,
                            version=version,
                            confidence=conf,
                            context_words=ctx_words
                        ))
                        
            lang_key = (source_lang.lower(), target_lang.lower())
            with self._lock:
                if lang_key not in self._glossaries:
                    self._glossaries[lang_key] = []
                self._glossaries[lang_key].extend(new_terms)

            logger.info(f"Loaded CSV glossary {filepath} ({len(new_terms)} terms, Version: {version}, Sector: {sector})")
            return True
        except Exception as e:
            logger.error(f"Failed to load CSV glossary: {e}")
            return False

    def get_terms(self, source_lang: str, target_lang: str, sector: Optional[str] = None) -> Dict[str, str]:
        """
        Retrieves active glossary terms, sorted by key length descending to prevent conflicts.
        If duplicates exist, chooses the one with higher confidence/matching sector.
        """
        lang_key = (source_lang.lower(), target_lang.lower())
        with self._lock:
            if lang_key not in self._glossaries:
                return {}
            terms_list = self._glossaries[lang_key]

        compiled_terms: Dict[str, GlossaryTerm] = {}
        for t in terms_list:
            if sector and t.sector != sector:
                continue
            
            # Resolve duplication conflicts by picking the highest confidence term
            if t.source_term in compiled_terms:
                existing = compiled_terms[t.source_term]
                if t.confidence > existing.confidence:
                    compiled_terms[t.source_term] = t
            else:
                compiled_terms[t.source_term] = t

        # Sort keys by length descending to resolve overlapping conflict matches
        sorted_items = sorted(compiled_terms.items(), key=lambda x: len(x[0]), reverse=True)
        return {src: term.target_term for src, term in sorted_items}

    def detect_conflicts(self, source_lang: str, target_lang: str, sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Scans glossary for conflicts such as:
        1. Duplicate terms: same source term mapping to different translations.
        2. Overlapping terms: one term is a substring of another which might lead to matching conflicts.
        """
        lang_key = (source_lang.lower(), target_lang.lower())
        with self._lock:
            if lang_key not in self._glossaries:
                return []
            all_terms = self._glossaries[lang_key]

        filtered = [t for t in all_terms if not sector or t.sector == sector]
        conflicts = []

        # 1. Detect duplicates with different translations
        by_src: Dict[str, List[GlossaryTerm]] = {}
        for t in filtered:
            by_src.setdefault(t.source_term.lower(), []).append(t)

        for src, terms in by_src.items():
            targets = {t.target_term.lower() for t in terms}
            if len(targets) > 1:
                conflicts.append({
                    "type": "duplicate_translation",
                    "source_term": terms[0].source_term,
                    "conflicting_targets": [t.target_term for t in terms],
                    "severity": "HIGH",
                    "description": f"Term '{terms[0].source_term}' maps to different translations: {', '.join(repr(t.target_term) for t in terms)}"
                })

        # 2. Detect overlapping terms
        sorted_by_len = sorted(list(by_src.keys()), key=len, reverse=True)
        for i, longer in enumerate(sorted_by_len):
            for shorter in sorted_by_len[i + 1:]:
                if shorter in longer:
                    conflicts.append({
                        "type": "overlapping_term",
                        "longer_term": by_src[longer][0].source_term,
                        "shorter_term": by_src[shorter][0].source_term,
                        "severity": "MEDIUM",
                        "description": f"Overlapping terms: '{by_src[longer][0].source_term}' contains '{by_src[shorter][0].source_term}'"
                    })

        return conflicts

    def inject_glossary(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str, 
        sector: Optional[str] = None
    ) -> Tuple[str, Dict[str, str], List[Dict[str, Any]]]:
        """
        Replaces matched glossary terms in text with non-translatable placeholders using context scoring.
        
        Returns:
            Tuple of (injected_text, restoration_map, match_details).
        """
        if not text:
            return "", {}, []

        lang_key = (source_lang.lower(), target_lang.lower())
        with self._lock:
            if lang_key not in self._glossaries:
                return text, {}, []
            terms = self._glossaries[lang_key]

        # Filter terms by sector if requested, or group them by source term
        term_groups: Dict[str, List[GlossaryTerm]] = {}
        for t in terms:
            term_groups.setdefault(t.source_term.lower(), []).append(t)

        # We first locate all occurrences of every term in the text
        candidate_matches: List[Dict[str, Any]] = []
        for src_lower, group in term_groups.items():
            pattern = re.compile(rf"\b{re.escape(group[0].source_term)}\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                start, end = match.span()
                matched_str = match.group(0)
                
                # Context-aware confidence scoring: evaluate each candidate in the group
                best_candidate: Optional[GlossaryTerm] = None
                best_score = -1.0
                
                # Context window size: 50 chars before and after
                window_start = max(0, start - 50)
                window_end = min(len(text), end + 50)
                context_window = text[window_start:window_end].lower()

                for cand in group:
                    score = cand.confidence
                    # Boost score if sector matches
                    if sector and cand.sector.lower() == sector.lower():
                        score += 0.2
                    # Boost score based on context words
                    for word in cand.context_words:
                        if word in context_window:
                            score += 0.1
                    
                    score = min(1.0, max(0.0, score))
                    if score > best_score:
                        best_score = score
                        best_candidate = cand

                if best_candidate:
                    candidate_matches.append({
                        "start": start,
                        "end": end,
                        "source_term": best_candidate.source_term,
                        "target_term": best_candidate.target_term,
                        "matched_str": matched_str,
                        "confidence": best_score,
                        "sector": best_candidate.sector
                    })

        # Resolve conflicts: if spans overlap, keep the longest match or higher confidence match
        # Sort matches by span length descending, then by confidence descending
        candidate_matches.sort(key=lambda m: (m["end"] - m["start"], m["confidence"]), reverse=True)
        
        accepted_matches: List[Dict[str, Any]] = []
        for match in candidate_matches:
            # Check overlap
            overlap = False
            for accepted in accepted_matches:
                if not (match["end"] <= accepted["start"] or match["start"] >= accepted["end"]):
                    overlap = True
                    break
            if not overlap:
                accepted_matches.append(match)

        # Sort accepted matches by starting index descending to replace without shifting indices
        accepted_matches.sort(key=lambda m: m["start"], reverse=True)

        restoration_map = {}
        injected_text = text
        
        match_details = []
        for i, match in enumerate(accepted_matches):
            placeholder = f"__GLOS_ZxxTERM{i}__"
            restoration_map[placeholder] = match["target_term"]
            
            start, end = match["start"], match["end"]
            injected_text = injected_text[:start] + placeholder + injected_text[end:]
            
            match_details.append({
                "source": match["source_term"],
                "target": match["target_term"],
                "matched": match["matched_str"],
                "confidence": round(match["confidence"], 4),
                "sector": match["sector"]
            })

        return injected_text, restoration_map, match_details

    def restore_glossary(self, text: str, restoration_map: Dict[str, str]) -> str:
        """Restores placeholders back to the target legal terms."""
        if not text or not restoration_map:
            return text
            
        restored = text
        for placeholder, target_term in sorted(restoration_map.items(), key=lambda x: len(x[0]), reverse=True):
            parts = [p for p in placeholder.split("_") if p]
            match_idx = re.search(r"\d+", placeholder)
            index = match_idx.group(0) if match_idx else parts[-1]
            regex_pattern = r"(?:__\s*|_\s*|\b)GLOS[\s_]+TERM(?:[\s_]+[a-zA-Z]+){0,3}[\s_]*" + re.escape(index) + r"(?:\s*__|\s*_|\b)"
            restored = re.sub(regex_pattern, lambda m, val=target_term: val, restored, flags=re.IGNORECASE)
            
        return restored
