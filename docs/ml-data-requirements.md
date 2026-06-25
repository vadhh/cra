# ML Training Data Requirements

Two training jobs are ready to run once labeled data is provided.
GPU is available (RTX 4050, 5 GB VRAM) — hardware is no longer a blocker.

---

## Job 1 — DistilBERT Fine-tuning (P2 #5)

**What it improves:** Layer 2 clause classification accuracy. Currently zero-shot; fine-tuning on real legal text raises precision significantly.

**Script:** `python3 scripts/generate_nli_training_data.py && python3 scripts/finetune_distilbert.py`

### What you need to provide

A CSV file at `ldv-backend/data/clause_training_data.csv` (already exists — append to it).

**Format:**
```
text,label
"The party waives all rights to dispute.",abusive_clause
"Payment within 30 days of invoice.",normal
```

**Labels (4 classes):**

| Label | Meaning | Examples |
|-------|---------|---------|
| `abusive_clause` | One-sided, waives rights, unilateral modification, liability exclusion, leonine profit sharing | "Client irrevocably waives all legal rights." |
| `payment_risk` | Excessive penalty rates (>10%/day or >20%/month), compounding interest | "Late payment incurs 25% per day." |
| `missing_mandatory` | Placeholder, TBD, incomplete section, blank clause | "[Governing law to be inserted]" |
| `normal` | Balanced, standard contractual language | "Either party may terminate with 30 days notice." |

**Minimum per class:** 200 full-sentence examples (800 total).
**Current count:** ~160 synthetic sentences already in the file — need real contract text to supplement.

**Quality tips:**
- Use actual clause text from real contracts, not paraphrases
- Each example should be 1–4 sentences (one clause)
- Include Indonesian, French, and Dutch examples alongside English
- `abusive_clause` and `payment_risk` are the most important to get right — add more if unsure

**How to run after adding data:**
```bash
cd ldv-backend
python3 scripts/generate_nli_training_data.py   # converts CSV → NLI triples
python3 scripts/finetune_distilbert.py           # ~15 min on RTX 4050
# Model saved to ~/.cache/ldv/models/distilbert-nli-finetuned/
```

**Remaining wiring (code, ~30 min):** `detector_distilbert.py` needs to check `LDV_DISTILBERT_MODEL` env var and load the fine-tuned model instead of `typeform/distilbert-base-uncased-mnli`.

---

## Job 2 — Risk Scorer MLP (P2 #9)

**What it improves:** Layer 3 risk scoring. Currently a deterministic formula with fixed weights; an MLP can learn non-linear relationships between clause patterns and true risk.

**Script:** `python3 scripts/train_risk_scorer.py --csv <your-file>`

### What you need to provide

A CSV file with expert-assigned risk scores per analyzed contract.

**Format:**
```
missing_required,high_flags,medium_flags,unique_l2,has_governing_law,has_venue,l2_available,risk_score
2,1,0,1,0,0,1,72
0,0,0,0,1,1,1,12
3,2,1,2,0,0,0,95
```

**Column definitions:**

| Column | Type | Meaning |
|--------|------|---------|
| `missing_required` | int | Number of mandatory clauses absent for this contract type |
| `high_flags` | int | Number of HIGH severity red flags found |
| `medium_flags` | int | Number of MEDIUM severity red flags found |
| `unique_l2` | int | Number of DistilBERT findings not already in L1 |
| `has_governing_law` | 0/1 | Governing law clause present |
| `has_venue` | 0/1 | Jurisdiction/venue clause present |
| `l2_available` | 0/1 | DistilBERT ran (1) or skipped (0) |
| `risk_score` | int 0–100 | **Expert judgment: how risky is this contract overall?** |

**Risk score guidance:**

| Score | Meaning |
|-------|---------|
| 0–30 | LOW — standard contract, minor gaps at most |
| 31–60 | MEDIUM — notable gaps or imbalanced terms |
| 61–80 | HIGH — significant abusive clauses or multiple mandatory gaps |
| 81–100 | CRITICAL — severely one-sided, illegal elements, or nearly incomplete |

**Minimum:** 50 scored contracts. 100+ significantly improves generalization.

**Fastest way to collect feature vectors:** run `/analyze` on your contracts and copy `layer3.features` from the JSON response into the CSV, then add your `risk_score` judgment column.

**How to run:**
```bash
cd ldv-backend
python3 scripts/train_risk_scorer.py --csv /path/to/your-scores.csv
# Saved to data/risk_scorer.pkl
# Activate: LDV_USE_MLP_SCORER=1
```

**Note:** without expert scores, the bootstrap MLP (no `--csv`) just learns to mimic the deterministic scorer and offers no real improvement. Keep using the deterministic scorer until you have 50+ labeled contracts.

---

## Priority order

1. **Do Job 1 first** — clause labeling is the highest-impact improvement and needs the most data
2. **Job 2 can wait** — the deterministic L3 scorer is well-calibrated; MLP only helps at the edges
