# Level 8.1 — Agent Foundations, Web Development Specialization

Phase 8 (Agentic Autonomous Coding), Level 8.1, web-specialization variant.

| file | samples |
|---|---|
| `level_8_1_agent_foundations_web.jsonl` | 1,000 |

One JSON object per line, UTF-8, ASCII-only field values, no blank lines.

Validator:

```bash
python3 data/phase8/web/validate_level_8_1_web.py
```

Current result: PASS — 1,000 objects, 0 duplicate or near-duplicate instructions
(Jaccard 0.62 over glue-stripped word sets), 0 answers repeated more than twice,
0 uses of the anti-template phrase, 76% adversarial/evidence phrasing (lower bound,
versus the 35% requirement).

## Purpose

Same agent loop as the general Level 8.1 set, instantiated for web-development
environments: UNDERSTAND → INSPECT → PLAN → ACT → OBSERVE → EVALUATE → REVISE →
VERIFY → STOP, across frontend, backend, data, tooling, debugging, testing, and
deployment contexts. Samples are state-based: compact project states plus
observations (console, network tab, server logs, git status) and a request, with
the defensible next action or judgment as the answer.

## Schema and difficulty

Identical to the general set: `{instruction, reasoning, answer, category,
difficulty}` in that key order, reasoning 3-7 sentences, difficulty integer 1-5.

Global difficulty targets met exactly: 1: 100, 2: 200, 3: 350, 4: 250, 5: 100.

## Categories (35, 26-30 samples each)

web_task_understanding, requirement_extraction, frontend_inspection,
backend_inspection, repository_structure, dependency_inspection,
package_configuration, browser_inspection, network_inspection, api_reasoning,
html_reasoning, css_reasoning, javascript_reasoning, typescript_reasoning,
react_reasoning, nextjs_reasoning, nodejs_reasoning, database_reasoning,
git_reasoning, tool_selection, next_action_selection, plan_vs_action,
state_tracking, hypothesis_testing, debugging_decision,
test_result_interpretation, build_result_interpretation,
requirement_verification, failure_recovery, stopping_conditions,
frontend_backend_integration, dependency_reasoning, configuration_reasoning,
regression_detection, autonomous_web_workflow.

## Technology balance

Project states span 70 distinct web project types: React, Next.js, Express,
Node.js services, vanilla JS widgets, static/CSS-heavy sites, TypeScript
libraries and monorepos, SQL-backed APIs (PostgreSQL, SQLite), PWAs, and
framework-independent pages. No framework dominates; difficulty-5 items are
anchored in cross-boundary adversarial states (frontend-backend splits,
config-versus-code, environment drift, co-deploying changes).

## Generation provenance

Curated archetype-and-pool synthesis in this directory (`wgen.py`, `wpools.py`,
`wframes_*.py`): 9 question archetypes per category (315 distinct concepts),
varied question formats per the anti-template requirement, instantiated over
the web pools with generator-enforced uniqueness (exact plus Jaccard),
per-(frame, project) non-repetition, answer non-repetition, ASCII and quoting
rules, and exact difficulty quotas computed to sum to the global targets.
Regenerate deterministically with `python3 wgen.py`.
