"""Difficulty-5 adversarial frames, one per decomp category."""

DCATS_HARD = {
"goal_decomposition": [
{"i": "For {proj}, '{goal}'; twist one: {hard}; twist two: {obs}.. Produce the decomposition that survives both, at the right granularity.",
 "a": "Survive both by shape: contract-first subgoals sized to reverse cleanly under the twist that {hard}, with an investigation subtask immediately since {obs} re-scopes reuse, each subgoal independently verifiable and none justified by proximity. Constraints resize plans; they do not replace them. The right granularity is whatever makes every step individually witnessable and individually revertible."},
],
"requirement_breakdown": [
{"i": "For {proj}, '{goal}' must satisfy product, security, and ops reviewers whose written clauses conflict on {topic}, while {obs2}. Break the requirements honestly.",
 "a": "Break them by adjudicating the conflict first: surface the mutually contradictory clauses about {topic} with each reviewer's rationale, get one owner decision, then decompose the surviving clauses into requirement groups with witnesses, respecting the constraint that {obs2} imposes. Requirement conflicts resolved silently reappear as reviewer fights in the final hour. Honest breakdown makes the politics visible early, in writing."},
],
"subtask_identification": [
{"i": "Plan for '{goal}' in {proj}: inspect, server work, UI, migrate all data today, docs, nice cleanup. {hard}. Which subtasks survive adversarial review?",
 "a": "Adversarial review kills three: migrate-all-data-today fails the risk-and-dependency test without a rehearsed batched plan, nice cleanup fails the would-anyone-notice and scope tests, and docs-first ordering fails sequencing. Inspect plus server plus UI survives if contract-first, and data work returns as its own phased plan. Subtask lists confront risk, dependency, scope, and order, or they get confronted by incidents."},
],
"dependency_identification": [
{"i": "For {proj}, '{goal}' plan treats authorization work as dependent on finishing every UI page, and caching as independent, while {obs}. Untangle real from fake dependencies.",
 "a": "Untangle at true consumption: authorization depends on the route and role contracts, not finished pages, so it gates enforcement work and can parallelize page work; caching depends on the invalidation signals the mutations emit, so it is not independent. Given {obs}, the plan misprices both. Real dependencies follow artifacts consumed, fake ones follow whatever was listed adjacent."},
],
"prerequisite_detection": [
{"i": "For {proj}, '{goal}' begins tomorrow, secrets rotation history is unknown, {obs2}, and {hard}. Which prerequisites gate the start and which merely deserve early slots?",
 "a": "Gating prerequisites are the ones whose failure invalidates everything after: provenance of secrets and recovery paths, the environment baseline green, and the access needed for {topic}, while comfort items like extra docs or tooling polish are early-slot niceties, given {hard} shrinks slack. Prerequisite status is priced by invalidation, not importance-feel. Gate lists stay short and provably necessary."},
],
"task_ordering": [
{"i": "For {proj}, '{goal}': five subtasks (spike, contract, implement, verify, deprecate) plus stakeholder pressure to demo early, and {obs2}. Order it defensibly.",
 "a": "Order: spike first for truth at least risk, contract second to freeze seams, implement third, verify at each handoff and the full flow last, deprecate strictly after verified non-use of the old path, with a demo possible after contract plus stubs without resequencing anything. Given {obs2} raises verification stakes, demo pressure moves no risk-bearing order. Defensible ordering cites dependency and risk, not theater."},
],
"frontend_task_decomposition": [
{"i": "For {proj}, '{goal}' appears purely visual, but {obs} and the design implies state the page never models, with {hard}. Decompose the frontend honestly.",
 "a": "Decompose honestly past the visual framing: model the implied states explicitly, including loading, error, empty, and permission variants, build per-state slices with visual witnesses, and only then the styling polish, since {obs} proves data-driven branches exist and {hard} forbids sloppy sequencing. Pure-visual framing is how stateful pages ship with invisible-state bugs. Style follows state-modeling, never precedes it."},
],
"backend_task_decomposition": [
{"i": "For {proj}, '{goal}' needs idempotent webhook handling, ordered processing per account, and at-least-once delivery guarantees, while {obs2}. Decompose the backend with semantics before code.",
 "a": "Semantics-first decomposition: define per-entity ordering keys and dedupe identity, implement idempotent processors with replay witnesses, build the queue topology that segregates ordering domains, then the handler code, then failure-drill verification under duplicates and reorderings, since {obs2} marks volume risk. Delivery guarantees are properties of the queue-and-processor design, not of careful coding. Semantics own subtasks before code does."},
],
"api_task_decomposition": [
{"i": "For {proj}, '{goal}' changes response shapes three client generations consume, a fourth party scrapes the undocumented internals, and {hard}. Decompose the API evolution without picking villains.",
 "a": "Decompose with additive-versioned discipline: version the contract explicitly, emit old and new through a translation seam, measure actual usage per generation with telemetry, communicate deprecation windows, and shield the undocumented-surface problem by versioning the internals it scrapes rather than breaking aggressively. Given {hard}, coordination cost dominates. Evolution respects every consumer's reality, including the badly-behaved ones."},
],
"database_task_decomposition": [
{"i": "For {proj}, '{goal}' requires re-shaping data that reports and exports read live against, {obs} on volume, while {hard}. Decompose the database work without an outage or a forked truth.",
 "a": "Decompose as dual-surface transition: build the new shape beside the old with views or translation keeping readers working, backfill with parity witnesses, contract the old surface only after every reader migrates with evidence, and schedule everything around the contention reality that {obs} plus {hard} imply. Live-read data transitions are timeline projects, not migration files. Dual surfaces with parity are the no-fork, no-outage path."},
],
"authentication_task_decomposition": [
{"i": "For {proj}, '{goal}' must add SSO while existing password sessions and remembered devices span three months of tokens, and {obs}. Decompose the auth migration like users matter.",
 "a": "Decompose with coexistence as the design: map sessions to identities first, introduce SSO as an additional verified issuer while honoring existing sessions, add linking flows with recovery witnesses, migrate gradually with per-user coherence, and set hard sunsetting only with notice windows, since {obs} shows live session mass. Auth migrations are user-trust operations wearing engineering clothes. Coexistence-first; revocation last, always announced."},
],
"fullstack_task_decomposition": [
{"i": "For {proj}, '{goal}' crosses cache layers at CDN, server, and client, three teams own a layer each, and {obs2}. Decompose the fullstack plan across ownership.",
 "a": "Decompose with one freshness contract: define cache keys, TTLs, and invalidation events per layer in one document each team signs, implement per-layer behind interface checks, verify cross-layer behavior with refresh-path probes, and assign seam ownership across teams explicitly, since {obs2} shows drift at boundaries. Cross-owner fullstack work fails at the seams by default. One contract, three implementations, one witness chain."},
],
"ui_feature_decomposition": [
{"i": "For {proj}, '{goal}' is an interactive dashboard whose widgets each refresh differently, real-time is wanted but budgets exist, and {hard}. Decompose the UI feature with refresh policy first.",
 "a": "Decompose with the refresh policy as architecture: classify widgets by freshness need into push, poll, and manual classes with budgets per class, design connection-sharing and backoff behavior, build widgets per slice with staleness indicators, and verify load against the budget, since {hard} prices every open socket. Real-time dashboards are subscription-economics problems. Freshness policy precedes widget construction."},
],
"bug_fix_decomposition": [
{"i": "For {proj}, '{goal}' recurs despite four prior fixes, each touching a different layer, and {obs} enters and leaves. Decompose the fifth attempt diagnostically.",
 "a": "Decompose diagnostically, not habitually: autopsy all four fixes with their witnesses, instrument across the layers to bracket the recurrence window, bisect conditions instead of files, and only then fix with a mechanism-level witness, since {obs} marks transient state. Four layer-touches with recurrence convicts the diagnostic method, not the modules. The fifth decomposition is an investigation that ends in either cause or instrument."},
],
"refactoring_decomposition": [
{"i": "For {proj}, '{goal}' modernizes state management across a codebase without full coverage, production cannot pause, and {obs2}. Decompose the refactor as incremental coexistence.",
 "a": "Decompose coexistence-first: define the target plus an adapter seam where old and new intermediate, migrate vertical slices each with behavior witnesses, gradual coverage expansion targeted at churn areas, and retire-by-usage policies instead of forced uniform conversion, since {obs2} limits test safety. Big refactor under partial coverage is a risk-migration project. Coexistence with slice-verification is the decomposition that survives reality."},
],
"testing_decomposition": [
{"i": "For {proj}, '{goal}' inherits a suite that is 60 percent flaky, blocks CI nightly, and three teams distrust it, while {hard}. Decompose test-suite rehabilitation.",
 "a": "Decompose rehabilitation as engineering: measure flakes statistically, triage classes by cause, quarantine with owners and expiry never silently, rebuild trust by stabilizing the signal suite first and expanding on measured reliability, and give CI an always-green core, since {hard} turns protest into bypass rites. Distrusted suites fail socially before technically. Rehab decomposes trust restoration before coverage growth."},
],
"deployment_decomposition": [
{"i": "For {proj}, '{goal}' launches a renamed product with DNS, CDN, app deploy, and email-delivery changes, with {obs2}. Decompose the launch choreography with rollback per stage.",
 "a": "Decompose choreography-first: pre-stage assets and certificates, pre-lower TTLs, rehearse on the staging clone, then sequence DNS-last where reversal is slowest, app-first where reversible, CDN between with cache choreography, email behind flags, with per-stage health gates and rollback owners, since {obs2} marks multi-system drift risk. Launch choreography prices reversal speed per stage. Slowest-to-reverse goes last, with the sharpest witness."},
],
"configuration_decomposition": [
{"i": "For {proj}, '{goal}' needs config changes in cloud console, env files, and the secrets store with six services involved, and {hard}, while {obs}. Decompose the coordinated config release.",
 "a": "Decompose with a source-of-truth cascade: declare precedence among the three stores, change-propagate in dependency order with per-service verification hooks, roll through services tolerant-first-then-strict, and audit each change as a versioned artifact with owners, since {obs} plus {hard} punishes coordination drift. Coordinated config is a mini-release with its own choreography. Cascades with declared precedence prevent the six-way drift."},
],
"repository_change_decomposition": [
{"i": "For {proj}, '{goal}' splits the repo the week before a release while two feature branches are long-lived, and {obs2}. Decompose the repo change without stranding anyone.",
 "a": "Decompose with migration-compassion: reconcile long-lived branches first via a primer merge pre-split, freeze windows communicated with owners, split with automated import-rewrites and a compatibility period where both shapes resolve, and retire the old paths post-release with evidence, since {obs2} shows heavy in-flight work. Repo surgery mid-flight needs preservation engineering for in-flight work. Sequence the compassion before the surgery."},
],
"risk_based_decomposition": [
{"i": "For {proj}, '{goal}' touches payments-adjacent code, untested audit paths, and a deadline, while {obs} skips it. Decompose the risk allocation ruthlessly.",
 "a": "Allocate ruthlessly: the payments-adjacent and audit surfaces receive threat-model slices, abuse witnesses, and review gates regardless of deadline pressure, mundane surfaces receive normal coverage, and the deadline adjust scope, not verification depth, since {obs} confirms surfaces beyond initial sight. Risk-based decomposition moves scope, never safety review, under time pressure. Ruthless risk-pricing protects the surfaces incidents punish."},
],
"parallel_vs_sequential_tasks": [
{"i": "For {proj}, '{goal}' server work waits on the data model while its tests are pure mocks; the UI mocks the contract; a teammate shares files, and {hard}. Maximize true parallelism without fake independence.",
 "a": "Maximize truthfully: UI proceeds fully parallel against the frozen contract, server logic builds against an in-memory model while awaiting the data model behind a repository seam, tests interleave per layer, and teammate-shared files get explicit ownership windows, since {hard} punishes collisions. Fake parallelism collapses at seams; real parallelism is designed through seams. Independence must be engineered, verified, and then exploited."},
],
"blocked_task_reasoning": [
{"i": "For {proj}, '{goal}' is blocked three layers deep: needs API shape, which needs product decision, which needs legal signoff, and {obs2}. Decompose recovery from deep blockage.",
 "a": "Recover layer by layer with decoupling: negotiate a decision-shaped temporary contract product can amend safely, build behind seams optimized for the plausible answers, prepare legal-ready variants rather than one guess, and re-verify continuously, since {obs2} shows time already lost. Deep blockages decompose into decoupling and range-covering preparation. Total blockage is usually three smaller solvable-isolation problems."},
],
"scope_control": [
{"i": "For {proj}, '{goal}' plan doubled through feedback loops, an adjacent team wants adjacent savings, and {obs2} keeps expanding. Perform the ruthless rescope.",
 "a": "Rescope by contract: the goal's clauses re-verify against the original acceptance, every additions routes into linked tasks with their own decompositions, adjacent-team asks earn a boundary meeting not absorbed scope, and the plan's protected core locks with the cut list published, since {obs2} marks adjacent expansion risk. Scope control is boundary diplomacy with written edges. Plans shrink to the smallest whole that honestly satisfies the ask."},
],
"verification_decomposition": [
{"i": "For {proj}, '{goal}' must be verified across three environments, four browsers, two auth roles, and a screen reader, with a three-day window, and {hard}. Decompose the witness matrix without fake coverage.",
 "a": "Decompose as risk-weighted matrix: full witness depth on the primary lane, targeted probes on axis-intersections that changed behavior logically implicates, documented per-cell rationale, with escapes for any surprise, and a written residual-risk statement distributed with the launch, since {hard} forbids performing completeness. Infinite matrices are unaffordable; honest matrices are sampled, justified, and residual-declared. Coverage honesty beats coverage theater every launch."},
],
"adaptive_replanning": [
{"i": "For {proj}, '{goal}': halfway, a vendor deprecates a dependency, legal changes one requirement, and a teammate's parallel merge just landed, with {obs2}. Replan the moving target.",
 "a": "Replan in three tracks: track the deprecation with a spike and fallback now, track the legal delta as a scope transaction with its own witnesses, and reconcile the merged seam by resynchronizing around the new baseline, while banking all verified work since {obs2} shows churn is not done. Moving-target replans decompose by track with per-track owners. The plan's agility is measured in conditions survived per replan."},
],
}
