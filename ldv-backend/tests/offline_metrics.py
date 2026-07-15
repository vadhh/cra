"""Pure metrics helpers for the offline validation harness — no ML imports,
so these stay fast and testable in isolation."""


def compute_clause_metrics(presence_map: dict, present_expected: list, missing_expected: list) -> dict:
    tp = fp = tn = fn = 0
    details = []
    for cid in present_expected:
        if presence_map.get(cid, False):
            tp += 1
            details.append({"clause_id": cid, "status": "TP"})
        else:
            fn += 1
            details.append({"clause_id": cid, "status": "FN"})
    for cid in missing_expected:
        if presence_map.get(cid, False):
            fp += 1
            details.append({"clause_id": cid, "status": "FP"})
        else:
            tn += 1
            details.append({"clause_id": cid, "status": "TN"})
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "details": details}


def percentile(values: list, pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round(pct / 100 * (len(s) - 1)))))
    return s[k]
