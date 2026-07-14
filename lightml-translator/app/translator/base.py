from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """
    Abstract Base Class outlining the interface for all translation backends.
    All translation engines (Helsinki-NLP Marian, etc.) must implement this interface.
    """
    
    @abstractmethod
    def load_model(self, source_lang: str, target_lang: str) -> None:
        """
        Loads the required model and tokenizer into memory.
        
        Parameters:
            source_lang: Language code to translate from.
            target_lang: Language code to translate to.
        """
        pass

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates the given text from source language to target language.
        
        Parameters:
            text: Text to be translated.
            source_lang: Language code of the input text.
            target_lang: Language code of the output text.
            
        Returns:
            Translated text.
        """
        pass

    @abstractmethod
    def is_model_loaded(self, source_lang: str, target_lang: str) -> bool:
        """
        Checks if the model for the given language pair is currently loaded in memory.
        
        Parameters:
            source_lang: Source language code.
            target_lang: Target language code.
            
        Returns:
            True if loaded, False otherwise.
        """
        pass
