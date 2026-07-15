"""Regression test: _keyword_doc_type must count total keyword occurrences,
not just how many distinct patterns matched at least once.

Root cause (NL NDA fixture): Marian MT mistranslated the Dutch title
"Geheimhoudingsovereenkomst" into nonsense ("HELLO-HOLDING AGREEMENT"), and
none of the other Dutch/French/Indonesian NDA synonyms survive translation
either. Only the English pattern `confidential(?:ity)?` still matches — but
it matches 3 times in the body text. Counting distinct patterns caps the
score at 1 (below _KEYWORD_MIN_HITS=2) even though the repeated term is
strong evidence; "non-disclosure agreement" only has 6 candidate patterns
total, vs. 17 for "lease agreement", so sparser categories were structurally
penalized regardless of how much real evidence survived translation.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detector_distilbert import _keyword_doc_type, _KEYWORD_MIN_HITS


def test_repeated_single_keyword_clears_min_hits():
    text = (
        "Article 2 - Purpose. This contract regulates the confidentiality.\n"
        "Article 3 - Confidential Information. All data shared is confidential.\n"
    )
    label, hits = _keyword_doc_type(text)
    assert label == "non-disclosure agreement"
    assert hits >= _KEYWORD_MIN_HITS, f"expected >= {_KEYWORD_MIN_HITS} hits from 3 occurrences, got {hits}"


if __name__ == "__main__":
    test_repeated_single_keyword_clears_min_hits()
    print("PASS")
