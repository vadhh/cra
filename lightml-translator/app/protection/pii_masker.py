import re
from typing import Dict, Tuple


class PIIMasker:
    """
    Identifies and masks PII (Personally Identifiable Information) before
    translation to ensure compliance and data privacy, then restores it after translation.
    """
    
    def __init__(self):
        # Basic patterns for PII detection
        self._patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        }

    def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Masks PII elements with placeholder tokens.
        
        Parameters:
            text: Input text containing PII.
            
        Returns:
            A tuple of (masked_text, map_of_tokens_to_original_pii).
        """
        if not text:
            return "", {}
            
        pii_map: Dict[str, str] = {}
        masked_text = text
        token_counter = 0
        
        for category, regex in self._patterns.items():
            matches = list(regex.finditer(masked_text))
            for match in reversed(matches):
                original = match.group(0)
                token = f"__PII_{category.upper()}_{token_counter}__"
                
                # Check for duplicates
                existing_token = None
                for t, orig in pii_map.items():
                    if orig == original:
                        existing_token = t
                        break
                        
                if existing_token:
                    use_token = existing_token
                else:
                    use_token = token
                    pii_map[token] = original
                    token_counter += 1
                
                start, end = match.span()
                masked_text = masked_text[:start] + use_token + masked_text[end:]
                
        return masked_text, pii_map

    def unmask(self, text: str, pii_map: Dict[str, str]) -> str:
        """
        Restores masked PII back into the text.
        
        Parameters:
            text: Translated text with PII tokens.
            pii_map: Map of tokens to original PII values.
            
        Returns:
            Unmasked text.
        """
        if not text or not pii_map:
            return text
            
        unmasked_text = text
        for token, original in pii_map.items():
            regex_pattern = r"\s*".join(re.escape(token))
            unmasked_text = re.sub(regex_pattern, original, unmasked_text)
            
        return unmasked_text
