from offline_metrics import compute_clause_metrics, percentile


def test_all_present_expected_detected():
    result = compute_clause_metrics({"a": True, "b": True}, ["a", "b"], [])
    assert result["tp"] == 2
    assert result["fp"] == 0
    assert result["tn"] == 0
    assert result["fn"] == 0
    assert result["details"] == [
        {"clause_id": "a", "status": "TP"},
        {"clause_id": "b", "status": "TP"},
    ]


def test_missing_expected_not_detected_is_true_negative():
    result = compute_clause_metrics({}, [], ["c"])
    assert result["tn"] == 1
    assert result["fn"] == 0


def test_false_negative_when_expected_present_not_detected():
    result = compute_clause_metrics({"a": False}, ["a"], [])
    assert result["fn"] == 1
    assert result["tp"] == 0


def test_false_positive_when_expected_missing_but_detected():
    result = compute_clause_metrics({"c": True}, [], ["c"])
    assert result["fp"] == 1
    assert result["tn"] == 0


def test_percentile_p95_of_ten_values():
    values = list(range(1, 11))  # 1..10
    assert percentile(values, 95) == 10


def test_percentile_empty_list_returns_zero():
    assert percentile([], 95) == 0.0
