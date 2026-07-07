"""Regression test: local translation must preserve one-clause-per-line
structure, since detector_distilbert._split_paragraphs splits on \\n+ and
semantic_clause_presence scores each paragraph independently. Blind
character-count chunking merges multiple clauses into one blob and destroys
that structure, causing every clause hypothesis to be scored against the same
multi-topic paragraph (see FR lease fixture: jurisdiction_venue,
maintenance_responsibility, and lease_term all spuriously matched the same
merged paragraph at 0.70-0.80 confidence).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import translator


class _FakeTokenizerOutput(dict):
    def to(self, device):
        return self


class _FakeTokenizer:
    def __call__(self, text, **kwargs):
        return _FakeTokenizerOutput({"text": text})

    def decode(self, ids, skip_special_tokens=True):
        return ids


class _FakeModel:
    class _Param:
        device = "cpu"

    def parameters(self):
        return iter([self._Param()])

    def generate(self, **inputs):
        # Real MarianMT generation normalizes whitespace — embedded newlines
        # inside a translated chunk do not survive tokenize/generate/decode.
        return [inputs["text"].replace("\n", " ").upper()]


def test_local_translate_preserves_line_boundaries():
    model_path = translator._OPUS_MT["fr"]
    translator._local_model_cache[model_path] = (_FakeModel(), _FakeTokenizer())

    text = "Article 1 - Bail\nArticle 2 - Loyer\nArticle 3 - Duree"
    result = translator._local_translate(text, "fr")

    assert result.count("\n") == text.count("\n"), (
        f"expected {text.count(chr(10))} newlines preserved, got {result.count(chr(10))}: {result!r}"
    )
    assert result == "ARTICLE 1 - BAIL\nARTICLE 2 - LOYER\nARTICLE 3 - DUREE"


def test_local_translate_does_not_drop_long_line_tail():
    """A single line with no newlines (e.g. a PDF paragraph the extractor
    didn't break up) that exceeds Marian's 512-token limit must not have its
    tail silently truncated away — every word must survive via sub-chunking."""
    model_path = translator._OPUS_MT["fr"]
    translator._local_model_cache[model_path] = (_FakeModel(), _FakeTokenizer())

    words = [f"mot{i}" for i in range(700)]
    text = " ".join(words)
    result = translator._local_translate(text, "fr")

    assert "MOT0" in result and "MOT699" in result, (
        f"expected first and last word to survive translation, got tail: {result[-60:]!r}"
    )
    assert len(result.split()) == len(words), (
        f"expected {len(words)} words preserved, got {len(result.split())}"
    )


if __name__ == "__main__":
    test_local_translate_preserves_line_boundaries()
    test_local_translate_does_not_drop_long_line_tail()
    print("PASS")
