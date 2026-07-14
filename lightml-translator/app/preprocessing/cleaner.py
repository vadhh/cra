import re


class TextCleaner:
    """
    Handles preprocessing of text before sending to the translation models.
    Ensures optimal input format to avoid MarianMT tokenization errors.
    """
    
    def __init__(self):
        # Match multiple consecutive spaces but keep single/double newlines
        self._multi_space_regex = re.compile(r"[^\S\r\n]{2,}")
        # Match invalid Unicode or control characters (preserving \x0c / \f page break indicator)
        self._control_chars_regex = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f-\x9f]")

    def clean(self, text: str) -> str:
        """
        Applies cleaning routines to input text.
        
        Parameters:
            text: Raw input text.
            
        Returns:
            Cleaned and normalized text.
        """
        if not text:
            return ""
            
        # 1. Normalize line endings to LF
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # 2. Clean out dangerous control characters
        cleaned = self._control_chars_regex.sub("", cleaned)
        
        # 3. Collapse multiple horizontal spaces to a single space
        cleaned = self._multi_space_regex.sub(" ", cleaned)
        
        return cleaned.strip()
