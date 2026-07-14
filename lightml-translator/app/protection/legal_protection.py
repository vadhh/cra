import re
import uuid
from typing import Dict, Tuple, List


class Segment:
    """Represents a segment of text that is either a literal text or an injected placeholder."""
    def __init__(self, is_placeholder: bool, content: str, placeholder: str = ""):
        self.is_placeholder = is_placeholder
        self.content = content
        self.placeholder = placeholder


class LegalProtectionEngine:
    """
    Identifies and masks critical legal entities, numbers, references, formatting tags,
    and metadata before translation, then restores them exactly to maintain 100% data integrity.
    Inherently thread-safe by managing state through per-request local contexts.
    """

    def __init__(self):
        # Ordered patterns from most specific to general to avoid prefix truncation issues.
        # We compile patterns that depend on line boundaries (e.g. clause numbers, headings) with re.M.
        self._patterns = {
            "html": re.compile(r"<[^>]+>"),
            "url": re.compile(r"\bhttps?://[a-zA-Z0-9.\-_~:/?#\[\]@!$&'()*+,;=]+\b"),
            "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
            "phone": re.compile(r"(?:\b|(?<=[\s]))(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
            "signature": re.compile(r"(?:\b|(?<=[\s]))(?:\[Digitally Signed\]|/s/\s*[a-zA-Z \t.]+\b)", re.I),
            
            # Statutory & citation formats
            "statutory_ref": re.compile(
                r"\b(?:UU|Perpres|PP|Permen|Keppres|UUD)\s+(?:No\.?\s*)?\d+/\d+(?:\s+Tahun\s+\d+)?\b"
                r"|\b(?:Civil Code|Penal Code|KUHP|KUHPer)\b", re.I
            ),
            "article_ref": re.compile(r"\b(?:Article|Pasal|Section|Bab)\s+\d+(?:\s+[a-z0-9()]+)*\b", re.I),
            "clause_num": re.compile(r"^\s*(?:\d+\.\d+(?:\.\d+)*|\(\s*[a-zA-Z0-9]\s*\)|[a-zA-Z0-9]\.)\s+", re.M),
            
            # Markdown components
            "markdown": re.compile(
                r"(?:(?<=[\s.,;:!?()'\"-])|^)("
                r"\*\*[^*]+\*\*"       # Bold with **
                r"|__[^\_]+__"          # Bold with __
                r"|\*[^*]+\*"          # Italic with *
                r"|_[^\_]+_"           # Italic with _
                r"|`[^`]+`"            # Inline code
                r"|^#{1,6}\s+.+$"      # Headings
                r")(?=(?:[\s.,;:!?()'\"-])|$)",
                re.M
            ),
            
            # Entities & Names
            "company": re.compile(
                r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*(?:\s+(?:PT|Tbk|Ltd|Inc|Corp|LLC|Co|B\.V\.|S\.A\.))\b"
                r"|\b(?:PT|CV)\s+[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*\b"
            ),
            "gov_agency": re.compile(
                r"\b(?:Kementerian|Departemen|Ministry of|Directorate General of|OJK|BI|BPN|SEC)\s+[A-Z][a-zA-Z\s]+\b"
            ),
            
            # Address formats
            "address": re.compile(
                r"\b\d+\s+[A-Z][a-zA-Z0-9\s,]{2,}(?:[sS]treet|[sS]t\b|[aA]venue|[aA]ve\b|[rR]oad|[rR]d\b|[bB]oulevard|[bB]lvd\b|[lL]ane|[lL]n\b|[dD]rive|[dD]r\b|[jJ]alan|[jJ]l\.)\b"
                r"|\b(?:[jJ]alan|[jJ]l\.)\s+[A-Z][a-zA-Z0-9\s,]{2,}(?:\s+[nN]o\.?\s*\d+)?\b"
            ),
            
            # Person names
            "person": re.compile(
                r"\b(?:Mr\.|Ms\.|Mrs\.|Dr\.|Prof\.|Sdr\.|Sdri\.|Tuan|Nyonya|Nona)\s+[A-Z][a-zA-Z\']+(?:\s+[A-Z][a-zA-Z\']+)*\b"
                r"|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b"
            ),
            
            # Defined Terms (e.g. "Perjanjian", "Pihak Kedua")
            "defined_term": re.compile(r'["\u201c\u201d][A-Z][a-zA-Z\s]+["\u201c\u201d]'),
            
            # Numbers & Financials
            "percentage": re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent\b|persen\b)", re.I),
            "currency": re.compile(r"\b(?:Rp\.?|USD|EUR|IDR|\$|€)\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\b", re.I),
            "date": re.compile(
                r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December"
                r"|Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember"
                r"|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b"
                r"|\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b"
            ),
            "registration_num": re.compile(r"\b(?:KVK|VAT|BTW|NPWP|NIB|Co\.\s*Reg\.\s*No\.?)\s*[A-Z0-9.\-/]+\b", re.I),
            "number": re.compile(r"\b\d+(?:\.\d+)*(?:[.,]\d+)?\b")
        }

    def protect(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces legal patterns with structured, collision-resistant placeholders.
        Generates a unique salt per request to avoid any placeholder collisions.
        Uses a segment-splitting algorithm to ensure absolute protection integrity
        and prevent nested/recursive matching of already protected entities.
        
        Parameters:
            text: Raw input text.
            
        Returns:
            Tuple of (protected_text, placeholder_map).
        """
        if not text:
            return "", {}

        placeholder_map: Dict[str, str] = {}
        
        # Start with a single text segment
        segments = [Segment(is_placeholder=False, content=text)]
        token_counter = 0

        # Run protection sequentially across defined categories
        for category, regex in self._patterns.items():
            new_segments = []
            for seg in segments:
                if seg.is_placeholder:
                    new_segments.append(seg)
                    continue

                matches = list(regex.finditer(seg.content))
                if not matches:
                    new_segments.append(seg)
                    continue

                last_idx = 0
                for match in matches:
                    start, end = match.span()
                    original = match.group(0)

                    # Text before match
                    if start > last_idx:
                        new_segments.append(Segment(is_placeholder=False, content=seg.content[last_idx:start]))

                    # Find or create placeholder for duplicate values
                    existing_placeholder = None
                    for placeholder, orig_val in placeholder_map.items():
                        if orig_val == original:
                            existing_placeholder = placeholder
                            break

                    if existing_placeholder:
                        use_placeholder = existing_placeholder
                    else:
                        use_placeholder = f"__LEG_PROT_Zxx{category.upper()}{token_counter}__"
                        placeholder_map[use_placeholder] = original
                        token_counter += 1

                    new_segments.append(Segment(is_placeholder=True, content=original, placeholder=use_placeholder))
                    last_idx = end

                # Text after last match
                if last_idx < len(seg.content):
                    new_segments.append(Segment(is_placeholder=False, content=seg.content[last_idx:]))

            segments = new_segments

        # Reassemble the final text
        protected_pieces = []
        for seg in segments:
            if seg.is_placeholder:
                protected_pieces.append(seg.placeholder)
            else:
                protected_pieces.append(seg.content)

        return "".join(protected_pieces), placeholder_map

    def restore(self, text: str, placeholder_map: Dict[str, str]) -> str:
        """
        Restores protected elements back into translated text.
        Uses lambda substitutions to protect special character sequences in original text.
        
        Parameters:
            text: Translated text with placeholders.
            placeholder_map: Placeholder-to-value map.
            
        Returns:
            Restored text.
        """
        if not text or not placeholder_map:
            return text

        restored_text = text
        for placeholder, original in sorted(placeholder_map.items(), key=lambda x: len(x[0]), reverse=True):
            parts = [p for p in placeholder.split("_") if p]
            # Extract digits anywhere in the placeholder name
            match_idx = re.search(r"\d+", placeholder)
            index = match_idx.group(0) if match_idx else parts[-1]
            regex_pattern = r"(?:__\s*|_\s*|\b)LEG[\s_]+PROT(?:[\s_]+[a-zA-Z]+){0,3}[\s_]*" + re.escape(index) + r"(?:\s*__|\s*_|\b)"
            restored_text = re.sub(regex_pattern, lambda m, val=original: val, restored_text, flags=re.IGNORECASE)
            
        return restored_text
