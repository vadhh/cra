"""Self-check for sydeco_engine.py (decoupled version)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import sydeco_engine

def test_sydeco_engine_flow():
    assert sydeco_engine.is_available() is True
    
    text = "The user accepts late payment penalty of 12% per day. We may modify this contract at any time without notice."
    tags = sydeco_engine.classify_clauses(text)
    assert len(tags) >= 2
    assert any(t["label"] == "payment_risk" for t in tags)
    assert any(t["label"] == "abusive_clause" for t in tags)
    
    score = sydeco_engine.quick_risk_score(text)
    assert score is not None
    assert score["score"] > 0
    assert score["clause_count"] >= 2
    assert score["flagged"] >= 2

if __name__ == "__main__":
    test_sydeco_engine_flow()
    print("test_sydeco_engine OK")
