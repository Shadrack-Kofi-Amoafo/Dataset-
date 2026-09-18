# Dataset-

Synthetic instruction-tuning datasets.

## Contents

- [`data/phase1/`](data/phase1/) — Phase 1: General Intelligence Foundation
  - `level_1_2_critical_causal_reasoning.jsonl` — 500 samples on critical and causal
    reasoning (confounding, interventions, counterfactuals, evidence quality, causal
    chains, bias, temporal reasoning, regression to the mean, uncertainty).
  - `level_1_2_critical_causal_reasoning_batch2.jsonl` — 200 further samples complementing
    the first batch, with no reused scenario, phrasing, or question template, weighted to
    difficulties 2-4.
  - Combined: **700 samples**. See [`data/phase1/README.md`](data/phase1/README.md) for the
    schema, distributions, and adversarial coverage.

## Validation

```
python3 data/phase1/validate_level_1_2.py
```

Checks each file's line count, JSON validity, the exact field set, allowed category values,
difficulty range, reasoning length in sentences, duplicate and near-duplicate scenarios, and
cross-file near-duplicates between the two batches. Prints the category and difficulty
distributions plus adversarial coverage counts.
