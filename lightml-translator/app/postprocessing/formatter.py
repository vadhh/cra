import re


class TextFormatter:
    """
    Handles postprocessing of translated text to restore clean formatting,
    fix punctuation spacings introduced by translation models, and clean up layouts.
    """
    
    def __init__(self):
        # Spacing adjustments around common punctuation marks
        self._punctuation_spaces = [
            (re.compile(r"[^\S\r\n\f]+([.,;:!?])"), r"\1"),  # Remove spaces before punctuation (preserve newlines/pagebreaks)
            (re.compile(r"([(])\s+"), r"\1"),      # Remove spaces after opening brackets
            (re.compile(r"\s+([)])"), r"\1"),      # Remove spaces before closing brackets
        ]

    def format(self, text: str) -> str:
        """
        Applies formatting routines to translated text.
        
        Parameters:
            text: Translated raw text.
            
        Returns:
            Properly formatted and readable text.
        """
        if not text:
            return ""
            
        formatted = text
        
        # 1. Clean spacing around punctuation
        for pattern, replacement in self._punctuation_spaces:
            formatted = pattern.sub(replacement, formatted)
            
        # 2. Re-collapse any multi-spaces that might have been introduced (preserve newlines/pagebreaks)
        formatted = re.sub(r"[^\S\r\n\f]{2,}", " ", formatted)
        
        # 3. Capitalize first letter of sentences without destroying structural whitespace
        # Require whitespace after sentence-ending punctuation to avoid matching inside emails/domains
        formatted = re.sub(r"(?:^|(?<=[.!?]\s))\s*([a-z])", lambda m: m.group(0).upper(), formatted)
        
        return formatted.strip()
