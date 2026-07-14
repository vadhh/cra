import re
from typing import Dict, Tuple, List


class TagProtector:
    """
    Protects special formatting, links, placeholders, or legal citations
    from being translated or mangled by translation models.
    """
    
    def __init__(self):
        # Patterns to protect during translation
        self._patterns = {
            "html_tag": re.compile(r"<[^>]+>"),
            "md_link": re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
            "curly_placeholder": re.compile(r"\{\{[^}]+\}\}"),
            "square_placeholder": re.compile(r"\[\[[^\]]+\]\]"),
            "citation": re.compile(r"\b(?:UU|Perpres|PP|Permen|Keppres|UUD)\s+(?:No\.?\s*)?\d+/\d+(?:\s+Tahun\s+\d+)?\b", re.I),
        }

    def protect(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces matched patterns with non-translatable tokens.
        
        Parameters:
            text: Text to protect.
            
        Returns:
            A tuple of (protected_text, map_of_tokens_to_original_strings).
        """
        if not text:
            return "", {}
            
        protection_map: Dict[str, str] = {}
        protected_text = text
        token_counter = 0
        
        # We protect each pattern one by one
        for category, regex in self._patterns.items():
            matches = list(regex.finditer(protected_text))
            # Process in reverse order to keep string indices valid
            for match in reversed(matches):
                original = match.group(0)
                token = f"__PROT_{category.upper()}_{token_counter}__"
                
                # Check if this exact string was already replaced to avoid duplicates
                existing_token = None
                for t, orig in protection_map.items():
                    if orig == original:
                        existing_token = t
                        break
                        
                if existing_token:
                    use_token = existing_token
                else:
                    use_token = token
                    protection_map[token] = original
                    token_counter += 1
                
                start, end = match.span()
                protected_text = protected_text[:start] + use_token + protected_text[end:]
                
        return protected_text, protection_map

    def restore(self, text: str, protection_map: Dict[str, str]) -> str:
        """
        Restores original protected elements back into the translated text.
        
        Parameters:
            text: Translated text containing protection tokens.
            protection_map: Map of tokens to original strings.
            
        Returns:
            Text with original elements restored.
        """
        if not text or not protection_map:
            return text
            
        restored_text = text
        # Restore in order
        for token, original in protection_map.items():
            # Support fuzzy matching for cases where models added spaces inside tokens,
            # e.g., "__ PROT_HTML_TAG_0 __" or similar quirks.
            regex_pattern = r"\s*".join(re.escape(token))
            restored_text = re.sub(regex_pattern, original, restored_text)
            
        return restored_text
