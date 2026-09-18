"""Adversarial difficulty-5 frames, one per category. Slots: proj lang files req obs obs2 err hyp hyp2 done res detail topic."""

CATS_HARD = {
"task_understanding": [
{"i": "For {proj}, the user says '{req}' while also noting that {obs} and the deadline is today. The request, the symptom, and the clock each imply different work. {hard} What is the genuinely correct framing of the objective?",
 "a": "Frame the objective as the smallest verified behavior change that satisfies '{req}' given the evidence, with the deadline forcing a scope cut rather than a quality cut. Since {obs} shapes the diagnosis, keep the goal fixed and trade breadth for rigor. State this explicitly back so the user sees the shape of done."},
],
"requirement_extraction": [
{"i": "The thread for {proj} says '{req}', the maintainer adds that {obs}, and a commenter suggests {hyp}. The agent must extract requirements without inventing any. {hard} What survives as binding?",
 "a": "Bind only the stated behavior for '{req}' plus the maintainer fact that {obs}, which constrains where the fix may land. Treat '{hyp}' as a lead to test, never an obligation. Every surviving item needs a planned check; the rest is context."},
],
"constraint_identification": [
{"i": "In {proj}, '{req}' must ship with backward compatibility, no new dependencies, and {obs} limits where edits may land, while the obvious fix violates one of these. {hard} What should the agent conclude?",
 "a": "Conclude that the obvious fix is disqualified and the search space is the set of approaches satisfying all three constraints plus the evidence that {obs}. When the natural plan breaks a hard rule, the constraint wins and the plan changes. If nothing fits, report the conflict with a concrete proposal."},
],
"information_gap_detection": [
{"i": "For {proj}, the report says the fix for '{req}' works on Tuesday data but fails on Wednesday data, and so far the agent has only {done}. {hard} Which single unknown most changes the strategy, and how is it closed?",
 "a": "The decisive unknown is what differs between the two datasets or the two days of state, since the completed probe touched nothing about inputs or time. Close it by diffing inputs, seeds, and environment snapshots before any code theories. Day-linked failure is a state puzzle, and guessing the code skips the one cheap probe that matters."},
],
"observation_before_action": [
{"i": "In {proj}, the user pre-approves a rewrite for '{req}' and says to skip reading, but {obs} hints the fault may be one line. {hard} How much observation is still owed before the first edit, and why?",
 "a": "Owe enough observation to falsify the one-line theory: read the accused file, its tests, and run one repro, total minutes against a rewrite's hours. Approval changes permission, not epistemics; {obs} means a cheap probe may retire the expensive plan. Record the baseline so the chosen path is auditable either way."},
],
"environment_inspection": [
{"i": "For {proj}, CI fails on a fresh image while the agent {done} and local runs pass; {obs} and {obs2} both point at drift. {hard} What inspection sequence isolates the split?",
 "a": "Sequence from outermost inward: image digest, toolchain versions, lock freeze, then seeds and caches, testing one layer at a time with a controlled repro. Both {obs} and {obs2} fit multi-layer drift, so a single-layer fix may be theater. Land on the first layer whose change flips the outcome."},
],
"next_action_selection": [
{"i": "State for {proj}: '{req}' is requested, the agent has {done}, outputs now show {res}, and both {hyp} and {hyp2} remain live. {hard} Choose exactly one next action and defend it.",
 "a": "Run the single cheapest probe that gives opposite outcomes under {hyp} versus {hyp2}, because the ledger shows {res} just falsified certainty on the earlier line. Repeating any completed step adds zero, and editing while two causes live risks fixing the wrong one. Discriminating evidence first, always."},
],
"tool_selection": [
{"i": "In {proj}, {err} appears only under load, and the agent can add sleep-based delays, capture a live trace with sampling, or inspect each suspect file slowly. {hard} Which tool and why?",
 "a": "Capture a sampled live trace during a load repro, since race and load faults hide from static reads and sleeps corrupt the timing they probe. The trace keeps the system natural while revealing interleavings. After the trace names a site, targeted reading gets its turn."},
],
"action_sequencing": [
{"i": "For {proj}, '{req}' needs a risky migration, a code change, and a docs update; backups exist but are unverified, and {obs}. {hard} Produce the defensible sequence.",
 "a": "Verify the backups first, then rehearse the migration on a restore, land the code against the rehearsed shape, verify end to end, and update docs last to describe witnessed behavior. The observation that {obs} plus unverified backups makes backup-verification the real step one. Anything earlier gambles the only rollback."},
],
"plan_vs_action": [
{"i": "In {proj}, the plan for '{req}' hinges on {hyp}, the first probe gives {res}, and a teammate offers an unrelated quick patch. {hard} Recalibrate plan versus action.",
 "a": "Hold action until the probe's meaning is written down: {res} either confirms or kills {hyp}, and the plan's every step inherits that answer. Decline grafting the unrelated patch until the main line is restored, since mixed tracks destroy attribution. One new fact, then act."},
],
"state_tracking": [
{"i": "For {proj}, across a long session the agent edited two files, reverted one, stashed user edits, and {res} after the last run; now {err} appears. {hard} What must the state ledger show to attribute fault?",
 "a": "Show the net diff per file with reverts accounted, the stash's contents and planned return, every probe with outcome including {res}, and the moment {err} first appeared relative to each change. Fault attribution is an interval problem across deltas, not a snapshot problem. Without the ledger, blame lands on the wrong edit."},
],
"goal_tracking": [
{"i": "In {proj}, '{req}' is the stated goal, but three probes show the user's outage actually comes from elsewhere, while {obs}. {hard} How should the agent track goal versus discovery?",
 "a": "Keep '{req}' as the contract and surface the discovery as a goal-change proposal with evidence, since {obs} does not itself transfer intent. If the user accepts, re-anchor cleanly and close the old ledger; if not, finish the original goal and report the finding. Unilateral goal swaps break the contract either way."},
],
"observation_vs_assumption": [
{"i": "For {proj}, {obs}, the suite is green, and the agent asserts both that the cause was {hyp} and that {req} is now complete. {hard} Sort every claim into observed versus assumed.",
 "a": "Observed: {obs} and a green suite under recorded conditions. Assumed: the causal story '{hyp}' and completion of '{req}', since a pass never proves a cause and edges sit outside the suite. Upgrade the assumptions only with a revert-control plus boundary probes, or keep the claims labeled and the task open."},
],
"action_result_interpretation": [
{"i": "In {proj}, after the change {res} on the focused run, the full suite is green, yet {obs2} in production logs persists. {hard} What is the only defensible interpretation?",
 "a": "The change moved local indicators while the live system disagrees, so the defensible read is a verified-local plus unverified-live state, not success and not failure. Because {obs2} persists, the oracle that matters is the serving path, and the next action targets the gap between suite reality and production reality. Any victory claim is premature."},
],
"success_detection": [
{"i": "For {proj}, the customer confirms the fix works, the suite is green, but the mechanism is unknown and {obs} once contradicted the fix. {hard} Is this success, and what remains?",
 "a": "This is deployment success without engineering success: the user win is real, yet an unexplained mechanism plus the contradiction that {obs} raised leaves the fix unprincipled. Mark the outcome for the user while keeping a mechanism task open with the contradiction logged. Both truths belong in the report."},
],
"failure_detection": [
{"i": "In {proj}, the agent's fix passed locally, passed CI, and shipped; now the symptom pattern where {obs2} recurs weekly but softer, while aggregate metrics read 'mostly healthy.' {hard} What failure form must be detected?",
 "a": "Detect a dampened fault rather than a cured one: a weekly echo of the original symptom at reduced magnitude fits a masked root cause carrying a timer. Aggregate metrics averaging to healthy can hide a periodic spike. Reopen with time-series probes at the failure cadence instead of trusting the average."},
],
"plan_revision": [
{"i": "For {proj}, the plan assumed {hyp}, two probes returned {res}, the allowed edit surface shrank when {obs}, and the deadline halved. {hard} Write the revised plan's shape.",
 "a": "Drop to the smallest verifiable mitigation within the shrunken surface, since the probes that returned {res} killed {hyp} and the deadline no longer funds a cure. The revised shape is: one targeted probe to confirm the mitigation's premise, one minimal change, one witness check, then a documented residual-risk handoff. Cure deferred, harm bounded, evidence preserved."},
],
"recovery_reasoning": [
{"i": "In {proj}, a bad migration half-applied on shared infrastructure, the agent {done}, {err} spread to a second service, and two teammates' work depends on the same state. {hard} What recovery order minimizes blast radius?",
 "a": "Announce and freeze first so dependents stop building on broken state, snapshot what remains, then restore from the best rollback point, replaying only verified-good steps, and verify each dependent before unfreezing. Since {err} already spread once, curiosity about the root cause ranks below containment. Communicate costs and the replay ledger afterward."},
],
"stopping_conditions": [
{"i": "For {proj}, '{req}' is verified, the suite is green, but a beautiful refactor tempts, {obs2} hints at a separate bug, and the user is waiting. {hard} Is stopping correct, and what accompanies the stop?",
 "a": "Stop, because verified goal plus green suite saturates the stopping rule and both tempters are outside the contract. Package the refactor idea and the suspicion from {obs2} as concrete follow-up notes with repro sketches. Stopping with a good handoff ships the win without losing the leads."},
],
"verification": [
{"i": "In {proj}, '{req}' cannot be tested deterministically: {obs}; the agent {done} and got ambiguous signals. {hard} Design the strongest available verification.",
 "a": "Build a statistical witness: repeated paired before/after runs across recorded seeds and conditions, judged by pre-committed thresholds, plus the original repro path exercised end to end. Since {obs} blocks determinism and the earlier signal was ambiguous, pre-committed criteria prevent motivated reading. Some evidence properly bounded beats certainty improperly claimed."},
],
"unnecessary_action_detection": [
{"i": "For {proj}, the plan includes a cache rebuild, a dependency bump, and a retry bump to address '{req}', while the agent has {done} and {obs} localizes the fault. {hard} Which actions fail the proportion test?",
 "a": "All three fail, because {obs} already localizes the fault and the completed probes narrow it further; each planned action is a scattershot move that adds variables. The proportionate set is the single minimal edit at the localized site plus its witness test. Cut the rest and let evidence, not anxiety, size the change."},
],
"risk_aware_action": [
{"i": "In {proj}, two routes satisfy '{req}': reusing a slightly-wrong shared helper or editing it, and {obs2} shows other callers rely on current quirks. {hard} Choose the risk-aware route and justify the tradeoff.",
 "a": "Take the third route: add a narrow wrapper or forked helper so shared quirk-behavior stays untouched, because {obs2} proves the helper's wart is load-bearing elsewhere. Direct reuse ships a subtly wrong fit; editing it gambles silent regressions across callers. The small duplication buys isolation, and the report should name the wart."},
],
"dependency_awareness": [
{"i": "For {proj}, '{req}' requires upgrading a library whose new version changes statistics inside a shared pipeline, and {obs} mixes old and new consumers. {hard} What dependency reasoning governs the rollout?",
 "a": "Treat the bump as a contract change needing staged rollout: enumerate consumers, gate by environment, verify each consumer's outputs against the prior version, and keep a pinned rollback. Since {obs} means mixed consumers, one global flip guarantees one group breaks. Compatibility gets proven per consumer, not assumed from a green build."},
],
"context_management": [
{"i": "In {proj}, the session is long, {hard}, the context holds raw logs, and the next step needs the clean thread of '{req}.' What consolidation preserves exactly the right state?",
 "a": "Consolidate into goal with acceptance checks, confirmed facts with sources, ruled-out leads with the probe that killed each, live hypotheses with current evidence, open questions, and the single next probe; archive raw logs externally with anchors. The consolidation is judged by what will be needed to continue without repeats. Anything failing that test leaves the active memory."},
],
"agent_loop_reasoning": [
{"i": "For {proj}, {hard}; the agent has {done}, saw {res}, and the user now expects a status update while '{req}' is unresolved. {hard} Demonstrate the honest loop stage and the honest message.",
 "a": "The honest stage is evaluate: {res} against the goal says progress without closure, so the message states what is verified, what the completed probes ruled out, the live hypothesis, and the next probe with its expected discriminating power. No 'almost done' theater; a loop status is a ledger summary. The loop continues exactly because evaluation says so."},
],
}
