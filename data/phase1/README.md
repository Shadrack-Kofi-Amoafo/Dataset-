# Level 1.2 — Critical & Causal Reasoning

Phase 1 (General Intelligence Foundation), Level 1.2 of the training set.

| file | samples |
|---|---|
| `level_1_2_critical_causal_reasoning.jsonl` | 500 (batch 1) |
| `level_1_2_critical_causal_reasoning_batch2.jsonl` | 200 (batch 2) |
| **total** | **700** |

One JSON object per line, UTF-8, ASCII-only field values, no blank lines, single trailing newline.

Validator (checks both files, their combined 700 samples, and cross-file near-duplicates):

```bash
python3 data/phase1/validate_level_1_2.py
```

Current result: both files PASS, 700 objects, 0 cross-file near-duplicates.

## Purpose

Teach a small model to reason about causes, effects, evidence, uncertainty, competing
explanations, interventions, and counterfactuals, rather than to pattern-match on the phrase
"correlation does not imply causation".

## Schema

Every line has exactly these fields, in this order:

| field         | type   | meaning                                                          |
|---------------|--------|------------------------------------------------------------------|
| `instruction` | string | A self-contained scenario, question, or claim to evaluate         |
| `reasoning`   | string | 3-6 sentences of pedagogical rationale: evidence, causal structure, alternatives, missing information |
| `answer`      | string | The final answer, including "cannot determine" where the evidence does not justify a conclusion |
| `category`    | string | One of the 16 labels below                                        |
| `difficulty`  | int    | 1-4, where 4 needs several reasoning steps and careful uncertainty handling |

## Category distribution

| category | batch 1 | batch 2 | total |
|---|---|---|---|
| intervention | 56 | 26 | 82 |
| counterfactual | 51 | 26 | 77 |
| confounding | 56 | 20 | 76 |
| correlation_vs_causation | 56 | 8 | 64 |
| competing_explanations | 42 | 22 | 64 |
| causal_chain | 42 | 14 | 56 |
| reverse_causality | 33 | 12 | 45 |
| evidence_quality | 33 | 9 | 42 |
| experimental_design | 23 | 18 | 41 |
| selection_bias | 23 | 10 | 33 |
| measurement_bias | 19 | 9 | 28 |
| temporal_reasoning | 19 | 6 | 25 |
| alternative_hypothesis | 19 | 5 | 24 |
| regression_to_mean | 9 | 8 | 17 |
| uncertainty | 10 | 5 | 15 |
| causal_attribution | 9 | 2 | 11 |
| **total** | **500** | **200** | **700** |

## Difficulty distribution

| level | batch 1 | batch 2 | total |
|---|---|---|---|
| 1 | 50 | 6 | 56 |
| 2 | 125 | 54 | 179 |
| 3 | 200 | 95 | 295 |
| 4 | 125 | 45 | 170 |

Batch 2 is deliberately weighted to difficulties 2-4 (97% of it), since it complements the
broader spread in batch 1. Every category contains a spread rather than a single level.

## Adversarial coverage

Counts below are keyword-detected lower bounds from the validator, not audited classifications.

| measure | batch 1 | batch 2 | total |
|---|---|---|---|
| answers naming a misleading or tempting reading and why it fails | 209 | 91 | 300 |
| answers stating the cause cannot be determined from the evidence given | 12 | 9 | 21 |
| answers that withhold or qualify a causal conclusion | 286 | 112 | 398 |

Batch 2 was specified against these minimums, all met: at least 50 samples whose answer names a
tempting-but-wrong reading (91), at least 30 asking what additional evidence or experiment would
resolve it (103), at least 25 counterfactual (26), at least 25 intervention (26), at least 20
competing explanations (22), and at least 20 conditional or explicitly uncertain answers (112).

## Batch 2 scope

Batch 2 was written to complement batch 1 rather than repeat it: no scenario, phrasing, or
question template is reused. The validator enforces this by testing every instruction and answer
in batch 2 against all 500 in batch 1 at a Jaccard threshold of 0.34. Domains added or
broadened relative to batch 1 include cybersecurity incident attribution, clinical safety
reporting, agricultural trials, logistics scheduling, energy retrofit schemes, and public
health surveillance.

## Scenario domains

Business, software, cybersecurity, medicine, education, manufacturing, agriculture,
environment, transport, sport, public services, social situations, statistics, workplace
and everyday decision-making. Scenarios are self-contained and do not depend on specialist
factual knowledge.
