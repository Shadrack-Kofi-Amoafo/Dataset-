# Level 1.2 — Critical & Causal Reasoning

Phase 1 (General Intelligence Foundation), Level 1.2 of the training set.

- File: `level_1_2_critical_causal_reasoning.jsonl`
- Samples: 200 (one JSON object per line, UTF-8, no blank lines)
- Validator: `python3 data/phase1/validate_level_1_2.py`

## Purpose

Teach a small model to reason about causal structure rather than to pattern-match on the
phrase "correlation does not imply causation". Every sample requires reasoning about
evidence, causes and effects, alternative explanations, interventions, confounders,
counterfactuals, causal chains, or uncertainty.

## Schema

Every line has exactly these fields, in this order:

| field         | type   | meaning                                                        |
|---------------|--------|----------------------------------------------------------------|
| `instruction` | string | A self-contained scenario, question, or claim to evaluate      |
| `reasoning`   | string | Why the answer holds: evidence, causal structure, or the error |
| `answer`      | string | The final answer, including "insufficient information" where apt |
| `category`    | string | One of the 16 labels below                                     |
| `difficulty`  | int    | 1-4, where 4 needs several reasoning steps and careful uncertainty handling |

## Distribution

| group | categories | n | share |
|-------|------------|---|-------|
| confounding / alternative explanations | `confounding` 22, `alternative_hypothesis` 10, `competing_explanations` 10 | 42 | 21% |
| intervention & experimental reasoning | `intervention` 14, `experimental_design` 14 | 28 | 14% |
| counterfactual reasoning | `counterfactual` | 28 | 14% |
| correlation vs causation | `correlation_vs_causation` | 20 | 10% |
| evidence quality / study design | `evidence_quality` | 18 | 9% |
| causal chains & mechanisms | `causal_chain` 12, `causal_attribution` 8 | 20 | 10% |
| reverse causality | `reverse_causality` | 10 | 5% |
| selection & measurement bias | `selection_bias` 6, `measurement_bias` 5 | 11 | 5.5% |
| temporal reasoning | `temporal_reasoning` | 10 | 5% |
| regression to the mean / uncertainty | `regression_to_mean` 6, `uncertainty` 7 | 13 | 6.5% |

Difficulty: 1 → 4 samples, 2 → 42, 3 → 103, 4 → 51 (98% at difficulty 2-4).
