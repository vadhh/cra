from app.services.translation_service import TranslationService
import logging

service = TranslationService()
text = open('datasets/employment_nl.txt').read()

cleaned_text = service._cleaner.clean(text)
protected, p_map = service._legal_protector.protect(cleaned_text)
print("1. Protected:", repr(protected))
print("P_Map:", p_map)

# Run direct translate
translated_batch = service._translate_batch_with_retry([protected], "nl", "en", [])
translated_text = translated_batch[0]
print("\n2. Translated before restore:")
print(repr(translated_text))

# Restore
restored = service._legal_protector.restore(translated_text, p_map)
print("\n3. Restored:")
print(repr(restored))
