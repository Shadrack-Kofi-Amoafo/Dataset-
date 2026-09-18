# Level 1.2 — Critical & Causal Reasoning

Phase 1 (General Intelligence Foundation), Level 1.2 of the training set.

- File: `level_1_2_critical_causal_reasoning.jsonl`
- Samples: 500 (one JSON object per line, UTF-8, no blank lines)
- Validator: `python3 data/phase1/validate_level_1_2.py`

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

The requested target mix summed to 535, so targets are shown scaled to 500.

| category | actual | share | scaled target |
|---|---|---|---|
| correlation_vs_causation | 56 | 11.2% | 56 |
| intervention | 56 | 11.2% | 56 |
| confounding | 56 | 11.2% | 56 |
| counterfactual | 51 | 10.2% | 51 |
| competing_explanations | 42 | 8.4% | 42 |
| causal_chain | 42 | 8.4% | 42 |
| evidence_quality | 33 | 6.6% | 33 |
| reverse_causality | 33 | 6.6% | 33 |
| selection_bias | 23 | 4.6% | 23 |
| experimental_design | 23 | 4.6% | 23 |
| alternative_hypothesis | 19 | 3.8% | 19 |
| temporal_reasoning | 19 | 3.8% | 19 |
| measurement_bias | 19 | 3.8% | 19 |
| uncertainty | 10 | 2.0% | 9 |
| causal_attribution | 9 | 1.8% | 9 |
| regression_to_mean | 9 | 1.8% | 9 |

## Difficulty distribution

| level | count | share | target |
|---|---|---|---|
| 1 | 50 | 10% | 10% |
| 2 | 125 | 25% | 25% |
| 3 | 200 | 40% | 40% |
| 4 | 125 | 25% | 25% |

Every category contains a spread of difficulties rather than a single level.

## Adversarial coverage

- 192 answers explicitly name the misleading or tempting reading and why it fails
  (co-occurring interventions, common causes, reversed direction, survivorship, changed
  measurement, regression to the mean, small samples, plausible but unverified mechanisms).
- 11 answers state outright that the cause cannot be determined from the evidence given;
  170 withhold or qualify a causal conclusion rather than forcing one.

## Scenario domains

Business, software, cybersecurity, medicine, education, manufacturing, agriculture,
environment, transport, sport, public services, social situations, statistics, workplace
and everyday decision-making. Scenarios are self-contained and do not depend on
specialist factual knowledge.
