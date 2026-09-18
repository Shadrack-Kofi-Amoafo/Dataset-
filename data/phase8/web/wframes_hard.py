"""Difficulty-5 adversarial frames, one per web category."""

WCATS_HARD = {
"web_task_understanding": [
{"i": "For {proj}, the request '{req}' comes with a mockup, a performance complaint, and {hard}, while {obs}. Frame the true objective.",
 "a": "Frame one verifiable behavior target as the objective, with the complaint becoming a measured budget and the visual target remaining provisional while unwitnessed. Since {hard} complicates the space and {obs} anchors part of the evidence, any goal statement ignoring these layers prices the work wrong. State the layered goal back before acting."},
],
"requirement_extraction": [
{"i": "The thread for {proj} asks for '{req}', ops adds that {obs}, security forbids one natural implementation, and a commenter pushes {hyp}. With the added twist that {hard}, what survives as binding and what does not?",
 "a": "Bind the outcome of '{req}', the ops observation that {obs} as a constraint on where changes land, and the security rule as a hard boundary. The commenter's '{hyp}' is an untested lead only, and {hard} shapes sequencing without adding obligations. Each surviving item must name its witness; the rest stays context."},
],
"frontend_inspection": [
{"i": "In {proj}, '{req}' presents as a styling fault, the console is clean, the network tab shows healthy stylesheets, and {obs}. With the added twist that {hard}, which inspection branch does the evidence actually justify?",
 "a": "Clean console plus healthy stylesheets push the fault into cascade resolution or runtime mutation, not missing files, so the justified inspection is computed-style resolution and any script that writes styles, since {obs} brackets the family. The styling-fault framing is only the user's vocabulary. Inspect what the evidence names, not what the vocabulary suggests."},
],
"backend_inspection": [
{"i": "For {proj}, '{req}' appears as case of {err}, the on-call runbook blames the handler, but staging reproduces it only when {obs2}. With the added twist that {hard}, what does the inspection sequence actually owe?",
 "a": "The runbook's blame is one hypothesis among model, handler, and environment candidates, and the conditional reproduction that {obs2} reveals shifts probability toward stateful or environmental causes. The owed sequence is condition-bracketed reproduction first, then per-layer inspection ordered by the narrowed conditions. Handler-first reading today restarts on-call archaeology tomorrow."},
],
"repository_structure": [
{"i": "For {proj}, two directory trees both look authoritative for '{req}', git history is ambiguous, the README contradicts the build config, and {hard}. Which structural evidence wins?",
 "a": "The build config wins because it is executable proof of what the pipeline assembles, while directories, history, and READMEs are all commentary; where evidence ranks conflict, executable truth outranks declared truth. Since {hard} muddies the social evidence, grep the build inputs for the true tree. Then update the README, because wrong documentation is the bug's accomplice."},
],
"dependency_inspection": [
{"i": "For {proj}, '{req}' worked before npm install, {obs} on the lockfile, and the team wants full reinstall plus cache clear, while {hard}. What inspection does this justify?",
 "a": "The lockfile observation makes install-time changes the named suspect, so justify diff-first inspection: compare installed trees between working and broken states before any reinstall, since nuke-and-reinstall destroys the only evidence. Given {hard}, the smallest differential instrument isolates the guilty version. Reinstalls are verdicts after conviction, never first procedure."},
],
"package_configuration": [
{"i": "In {proj}, '{req}' fails while the scripts, the env loader, and the tool configs each look correct, and {obs}. With the added twist that {hard}, what does package-configuration reasoning conclude?",
 "a": "Individually-correct-seeming configs that fail together imply interplay: precedence conflicts, option-shape mismatches across tools, or a wrapper silently intercepting options, with {obs} naming where to start. Given {hard}, the inspection is of the composed chain, not of each file in isolation. Configuration bugs hide between correct files, in composition."},
],
"browser_inspection": [
{"i": "For {proj}, '{req}' fails for a subset of users, their consoles are silent, no errors reach aggregation, and {obs2}. With the added twist that {hard}, what is the browser-inspection move?",
 "a": "Silent-subset failures need instrumented divergence: compare a working and a failing session across capability checks, fetched asset versions, and cache states, since {obs2} plus no-error means the browser believes it succeeded. Given {hard}, synthetic monitoring in the failing conditions beats more user screenshots. Silent failures are loud in comparisons."},
],
"network_inspection": [
{"i": "In {proj}, '{req}' shows intermittent API failure only through the CDN path, direct-to-origin works, and {hard}, while {err} appears at the edge. Which interpretation earns the next configuration change?",
 "a": "Edge-only failures earning changes come under reproducing the exact failing exchange per edge behavior: transformed headers, cached error responses, or origin-selection rules, with {err} literally placed at that layer. Since {hard} complicates the chain, the next change follows path-isolated evidence, not intuition. Direct-path health plus edge-path pain is middle-box evidence."},
],
"api_reasoning": [
{"i": "For {proj}, '{req}' needs the endpoint to tell three different clients apart: browser, mobile, and scripted partner. With the added twist that {hard}, what API reasoning designs the answer without three bespoke endpoints?",
 "a": "Reason the clients as consumers of one contract with negotiated views: content negotiation, explicit query-driven field selection, or per-client tokens driving response shaping, since endpoint-per-client multiplies contracts and drift. Under {hard}, the design must still hold authorization per client class. One contract with views beats three endpoints diverging."},
],
"html_reasoning": [
{"i": "For {proj}, '{req}' asked interactive card layouts containing full-card links plus inner buttons, shipped as nested interactives, and assistive tech now double-announces. Given the added twist that {hard}, resolve by reasoning, not by more aria patches.",
 "a": "Resolve at the content model: nested interactives are illegal and create duplicate accessible stops, so restructure to one link surface with buttons layered as siblings under positioning, and remove the aria patches which only amplified contradictory semantics. Under {hard}, DOM structure is semantics, not presentation. Verify the a11y tree shows one logical stop."},
],
"css_reasoning": [
{"i": "In {proj}, '{req}' needs the card grid themable by customers, theming must survive shadow-DOM widgets, the build is CSS-modules, and {obs}. With the added twist that {hard}, what styling architecture follows from reasoning alone?",
 "a": "Follow the boundaries with variables as the contract: define theme tokens as custom properties on the highest shared container, pierce shadow boundaries only through deliberate inherited variables, and accept CSS-modules as an implementation detail beneath them, since {obs} confirms boundary friction. Under {hard}, no amount of class engineering crosses boundaries custom properties cross by design. The theme contract is variables; everything else is mechanics."},
],
"javascript_reasoning": [
{"i": "For {proj}, '{req}' shows data corruption after concurrent tab usage, both tabs on the same origin, each with correct local logic, and {obs2}. With the added twist that {hard}, what does JavaScript reasoning say the unit tests missed?",
 "a": "Reason about cross-tab shared state: correct-per-tab logic races over shared storage and broadcasts, and {obs2} is the fingerprint of last-write-wins damage. Unit tests verified one process against sequential events, missing concurrency across processes. The fix moves to leader election or conflict-tolerant sync; only concurrency-shaped tests verify it."},
],
"typescript_reasoning": [
{"i": "In {proj}, '{req}' exposed that the validated boundary types and the upstream API silently drifted, two lockfile copies of the shared types exist, and {hard}. What is the complete reasoning verdict?",
 "a": "The verdict is two faults cooperating: duplicated type packages made nominal conflicts look structural while runtime drift made the compile layer lie, so fix the dedupe to one source plus add boundary validation, verified by a contract probe from production payloads. Under {hard}, quiet compile-time layers mislead exactly where trust concentrates. Type truth plus boundary truth; both, verified."},
],
"react_reasoning": [
{"i": "For {proj}, '{req}' needs server-session-driven UI that stays consistent under token refresh, tab sleep wakeup, and mid-form expiry, while {obs}. With the added twist that {hard}, what is the React-native reasoning structure?",
 "a": "Structure around the server as clock-owner: session state arrives as data with expiry timestamps, a single refresh coordinator owns renewal, and UI reads a derived validity rather than timing its own timers, since {obs} shows timer-led logic fragmenting. Under {hard}, three triggers are one invalidation discipline. Consistency follows from one authority plus derived views."},
],
"nextjs_reasoning": [
{"i": "In {proj}, '{req}' involves personalized pages with SEO needs, and the team debates SSR versus static plus client fetch, while {obs2}. With the added twist that {hard}, which rendering policy does reasoning choose?",
 "a": "Choose by consumer: crawlers receive rendered canonical content while personalization hydrates client-side, or fully dynamic rendering where personalization defines the page, because personalization in cached static output leaks personas and {obs2} marks the leakage risk. Under {hard}, one policy per content class, implemented in segment config, beats framework-heroics. SEO and privacy both rank above novelty."},
],
"nodejs_reasoning": [
{"i": "For {proj}, '{req}' runs CPU-heavy report generation inside the web process and latency for all users triples during reports, while {obs}. With the added twist that {hard}, what Node reasoning governs the architecture?",
 "a": "Govern by event-loop sovereignty: CPU-heavy work must leave the request-handling loop, via worker threads, child processes, or a queue-backed job service, since {obs} demonstrates head-of-line blocking across users. Under {hard}, optimizing the report loop first still leaves every request hostage. Separation of compute classes is the structural fix."},
],
"database_reasoning": [
{"i": "In {proj}, '{req}' requires tenant isolation guarantees in a shared-schema app, an auditor flagged one leak path, and {hard}, while {obs2}. What satisfies the guarantee at the database layer?",
 "a": "Satisfy it with defense in depth: row-level security or schema-per-tenant enforced in the database, tenant-scoped connection policies, plus appended tenant filters verified by cross-tenant probes, since {obs2} shows application-side filtering already leaked once. Under {hard}, one missing filter in one query becomes a breach. Guarantees live where they cannot be forgotten."},
],
"git_reasoning": [
{"i": "For {proj}, '{req}' fix must ship in the release cut today, main contains conflicting refactors, the teammate owning the seam is offline, and {obs}. With the added twist that {hard}, what is the Git-sound path?",
 "a": "The sound path isolates the fix to a cherry-pickable delta against the release line, verified there, with conflict ownership deferred to the teammate's return because semantic seams require their owner. Since {obs} marks collision risk, rewriting over the seam today would strand the merge. Ship the small verified delta, park the reconciliation, log the debt."},
],
"tool_selection": [
{"i": "For {proj}, '{req}' is reproducible only in production's third-party-integrated form, staging mocks hide the fault, and {hard}. Which tool set diagnoses without production damage?",
 "a": "Shadow-mode observability diagnoses: flagged canary cohorts, request-level tracing on the integrated path, and contract recordings of third-party exchanges replayed against candidate fixes, since {hard} blocks naive production experiments. Staging fidelity gaps are paid with recorded-truth replay. Instrument to replay, verify in shadow, then ship narrow."},
],
"next_action_selection": [
{"i": "State for {proj}: '{req}' unverified, three contradictory hypotheses alive, the user waiting for status, and {obs2} just arrived. Given the added twist that {hard}, choose exactly one next action and defend it.",
 "a": "Run the one probe whose outcomes discriminate among all three hypotheses, because {obs2} has identified the discriminating variable; status updates without new evidence only defer truth. The selection principle is discriminating power per unit cost, never anxiety relief. Answer the user with the probe and its branch logic, then act."},
],
"plan_vs_action": [
{"i": "In {proj}, '{req}' is time-critical, the planned fix depends on an upstream team's async answer, and a local workaround is available, while {hard}. Recalibrate plan versus action.",
 "a": "Recalibrate to dual-track: implement the verified-safe local mitigation minimizing blast radius now, and schedule the upstream-dependent proper fix conditioned on the answer, with both written down. Since {hard} warns the deadline is real, blocking on async answers converts partner latency into user outage. Time-critical work pays dual-track prices gladly."},
],
"state_tracking": [
{"i": "For {proj}, long '{req}' session: two files edited, one reverted, a fixture toggled, prod observing enabled, and {obs2} arrived. Given the added twist that {hard}, reconstruct the live state the agent must hold.",
 "a": "The live state: net one-file delta with the revert's intent remembered, fixture non-canonical with ownership and restore-time logged, production instrumentation active with an off-date, and {obs2} evaluated against every prior verdict for contamination. Under {hard}, amnesia anywhere converts the session into archaeology. State is the difference between a task and a story about a task."},
],
"hypothesis_testing": [
{"i": "In {proj}, '{req}' intermittently fails, three team members hold three theories, every theory has one anecdote, and {hard}. Design the adjudicating instrument.",
 "a": "Design against anecdotes: instrument the failing path to log, per occurrence, the exact variables each theory claims, run until a pre-agreed sufficient sample, and score theories against all occurrences instead of single stories. Under {hard}, any theory unfalsifiable by these logs is exiled from the room. Adjudication belongs to logging discipline, not seniority."},
],
"debugging_decision": [
{"i": "For {proj}, '{req}' is failing and the two prime suspects span outsourced services neither team can introspect, while {obs}. With the added twist that {hard}, what debugging decision survives partner opacity?",
 "a": "Survive with boundary-truth inference: exhaustive contract-logging at the edges plus controlled black-box probing across the boundary, because {obs} plus opacity means interiors are invisible and only inputs-outputs testify. Under {hard}, unresolved internals remain unresolved, and the fix targets interface defensive design. Debugging across opaque partners is black-box science."},
],
"test_result_interpretation": [
{"i": "In {proj}, '{req}' fix shipped with a suite that now passes 500 tests where previously 480 passed, the product monitor shows residual symptom, and {obs2}. With the added twist that {hard}, what is the interpretation?",
 "a": "Interpret as coverage-growth alongside blind-spot survival: new tests testify about the paths they exercise while the residual symptom plus {obs2} names a path that remains unwitnessed, and monitoring outranks suite-total arithmetic. Test count is not a regression budget. The next work is a witness for the specific surviving path, from the monitor inward."},
],
"build_result_interpretation": [
{"i": "For {proj}, '{req}' has builds passing everywhere, source maps disabled, runtime minified-only errors in one browser, and {hard}. What does interpretation demand before more code edits?",
 "a": "Demand observable artifacts before edits: reproduce with source-mapped staging builds, because minified-only evidence under {hard} without maps makes every edit a shot at a symbol-table ghost. Build interpretation says the artifact currently cannot testify. Fix the observability, then the fault."},
],
"requirement_verification": [
{"i": "In {proj}, '{req}' carries four acceptance clauses across security, compatibility, behavior, and performance, and each has a different witness environment, while {obs2}. With the added twist that {hard}, what closes verification?",
 "a": "Close with a per-clause witness matrix: each clause mapped to its proper environment, evidence captured per row, and zero clause-closing by adjacency, because {obs2} shows one clause's environment drifted. Under {hard}, a clause verified in the wrong environment is unverified. Done equals matrix all-witnessed, nothing else."},
],
"failure_recovery": [
{"i": "For {proj}, '{req}' fix attempt 3 of 5 just shipped and worsened the first bug while fixing the second, half the traffic saw it, and {hard}. Reconstruct the recovery and the lesson.",
 "a": "Recover to one coherent known-better state, flag the worsening attempt off, and re-establish the baseline against the traffic that saw it, then rebuild with one-delta-per-verification discipline. The lesson: five-deep attempt chains merge causes, and {hard} was the warning the system was already compounding. Recovery restores grounding; discipline prevents the chains."},
],
"stopping_conditions": [
{"i": "In {proj}, '{req}' verified green, one remaining odd log line unexplained but harmless-seeming, and the next task queues, while {obs2}. Given the added twist that {hard}, is stopping correct, and what accompanies it?",
 "a": "Stop with the oddity escalated into a logged observation owning a severity and a revisit trigger, since green with one unexplained benign-seeming signal is the classic shape of deferred incidents when {obs2} fits. Stopping is correct only when anomalies get ownership. Ship the task; hand the anomaly a name and a watch."},
],
"frontend_backend_integration": [
{"i": "For {proj}, '{req}' touches optimistic updates rolling back wrongly for concurrent users, offline queue replays, and server authority on conflicts, while {obs}. With the added twist that {hard}, what integration policy does reasoning choose?",
 "a": "Choose explicit conflict semantics: optimistic layers tagged with operation ids, server verdicts per id, and deterministic conflict policies such as last-writer-wins or merge where defined per resource, because {obs} demonstrates replay confusion. Under {hard}, optimistic layers without policies are disagreement generators. The policy is the contract; clients merely execute it."},
],
"dependency_reasoning": [
{"i": "In {proj}, '{req}' exposes a vulnerability in a deep transitive package whose direct parent is abandoned, and {hard}, plus {obs2}. What does dependency reasoning choose?",
 "a": "Choose among three moves with full pricing: upgrade through resolutions or overrides pinning the transitive safe version, replace the abandoned parent with a maintained alternative, or vendor and fork with provenance, because {obs2} shows no passive path exists. Under {hard}, waiting on upstream resurrection is not a plan. Every choice ends with verified installed versions."},
],
"configuration_reasoning": [
{"i": "For {proj}, '{req}' involves secrets rotation breaking multiple services on different schedules, each managing its own env, and {hard}. What configuration architecture does reasoning recommend?",
 "a": "Recommend centralized versioned secret management: one authoritative store, services reading through declared references, and rotation pushed atomically with coordinated reload semantics, because per-service schedules guarantee exactly the drift seen. Under {hard}, config consistency at fleet scale is architecture, not discipline. Secrets are infrastructure with owners and versions."},
],
"regression_detection": [
{"i": "In {proj}, '{req}' passed everything but quarterly numbers show conversion slowly degrading since the release window, masked by traffic growth, while {obs2}. With the added twist that {hard}, what regression shape is this and what catches it?",
 "a": "Name it a slow masked regression: per-user metrics degrade while aggregates grow, exactly the shape that cohort-normalized dashboards and before-after controlled comparisons catch, with {obs2} marking the mechanism. Under {hard}, green suites certify releases not trajectories. Catches live in long-window product telemetry, which becomes part of the definition of done."},
],
"autonomous_web_workflow": [
{"i": "For {proj}, '{req}' runs end-to-end through ambiguous goal, environment drift, competing hypotheses, and a co-deploying teammate, as {hard} summarizes. Show the workflow spine that survives all four.",
 "a": "The spine: write the goal with witnesses, then reconcile environment, then falsify-first probe ordering, then isolated-delta action with banked verified checkpoints, then explicit synchronization against the teammate's seam, then clause-by-clause verification, then stop with the ledger. Surviving ambiguity is procedural, not heroic. Each hazard in {hard} has one named loop stage that defeats it."},
],
}
