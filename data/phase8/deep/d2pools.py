"""Pools for the Phase 8.2 DEEP task-decomposition web dataset.

Imports filler lists from the 8.2 decomp pools to stay consistent,
and adds architecture-constraint and boundary pools used by deep frames.
ASCII only, no double quotes inside text.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("dpools", Path(__file__).parent.parent / "decomp" / "dpools.py")
_dp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dp)

PROJECTS = _dp.PROJECTS
ERRORS = _dp.ERRORS
DGOALS = _dp.DGOALS
DOBS = _dp.DOBS
DNEW_FACTS = _dp.DNEW_FACTS
DHARD = _dp.DHARD
DTOPICS = _dp.DTOPICS
DPLAN_ITEMS = _dp.DPLAN_ITEMS
AREAS = _dp.AREAS

CONSTRAINTS = [
    "the platform forbids secrets in client bundles",
    "SEO requires the landing pages to be server-rendered",
    "the database is shared with a legacy system that reads the same tables",
    "the monorepo enforces strict package boundaries through lint rules",
    "the API is consumed by a mobile app that cannot be force-updated",
    "the design system is frozen until the rebrand ships",
    "the CDN caches HTML for sixty seconds unless told otherwise",
    "the hosting plan limits the server to one process",
    "the WAF blocks request bodies over one megabyte",
    "the team freezes dependency changes during release weeks",
    "accessibility conformance to WCAG AA is a contractual obligation",
    "the oldest supported browser lacks several modern APIs",
    "row-level security in Postgres is the isolation mechanism in place",
    "the CI budget caps the full suite at twelve minutes",
    "the company policy requires audit trails for admin mutations",
    "the search service bills per query",
    "the single shared staging database serves three applications",
    "the build pipeline bakes feature flags at compile time",
    "the queue offers at-least-once delivery with no ordering across keys",
    "third-party cookies are blocked for the browser share that matters",
]

BOUNDARIES = [
    "the browser sandbox and the first-party server",
    "the first-party server and the upstream provider",
    "the shared package boundary in the monorepo",
    "the edge runtime and the origin server",
    "the admin surface and the public surface",
    "the synchronous request path and the async workers",
    "the transactional database and the read replicas",
    "the flagged rollout path and the legacy path",
    "the public API contract and the private admin API",
    "the static shell and the hydrated application",
]

RISKS = [
    "destructive data change on a table reports also read",
    "an auth-cookie attribute change during live sessions",
    "a dependency bump that changes serialized output subtly",
    "a concurrency window between read and write under checkout load",
    "a shared component consumed by eleven routes",
    "a cached negative response poisoning the client path",
    "a per-tenant configuration override with cross-tenant blast radius",
    "an irreversible export deletion users rely on for audits",
    "a clock-skew-sensitive token validation across regions",
    "an async retry that can double-write downstream events",
]

QUESTIONS = [
    "Which subtask is fake-parallel and which is truly parallel?",
    "Which dependency in this plan is fabricated?",
    "Which information gap must close before any implementation task starts?",
    "Which verification witness belongs to which requirement?",
    "Which ordering mistake does the tempting plan commit?",
    "Which subtasks would a boundary-respecting plan draw?",
    "Which plan items die under an adversarial review?",
    "Whose permission does the plan silently assume?",
    "Which statement in the plan is a scope violation?",
    "Which compensation would the plan need if the assumption fails?",
]
