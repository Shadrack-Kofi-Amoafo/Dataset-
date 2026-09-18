"""Pools for Phase 8.2 task-decomposition web-specialization dataset.

Imports project/environment filler from the 8.1 web pools for consistency.
ASCII only, no double quotes inside text.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("wpools", Path(__file__).parent.parent / "web" / "wpools.py")
_wpools = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wpools)

PROJECTS = _wpools.WPROJECTS
ERRORS = _wpools.WERRORS

DGOALS = [
    "Add user profile editing with name, bio, and avatar, with server-side validation and a preview before save",
    "Implement email-and-password login with secure sessions, rate-limited attempts, and a logout that clears state",
    "Add product search with keyword, category filter, and cursor pagination on the catalog page",
    "Fix the checkout total that rounds incorrectly when a discount code is applied",
    "Add a dark mode toggle persisted per user with no flash of wrong theme on load",
    "Add avatar upload with size limits, format checks, and a progress indicator",
    "Build an admin orders dashboard with status filter, date range, and CSV export",
    "Add OAuth sign-in alongside the existing password login without breaking current sessions",
    "Rate-limit the public API per client with clear 429 responses and retry guidance",
    "Add end-to-end coverage for the checkout happy path plus the three known failure paths",
    "Set up a staging deployment pipeline with build, test, migrate, and rollback stages",
    "Upgrade the frontend bundler one major version with no runtime regressions",
    "Refactor the 900-line settings component into a routed sub-page structure",
    "Add keyboard navigation and focus management to the main navigation menu",
    "Add notifications for order status changes via in-app inbox plus email",
    "Implement a shopping cart with add, remove, quantity edit, and server-side price recompute",
    "Add comment threads under posts with moderation flags and pagination",
    "Fix the flaky payment-webhook handler that double-counts retried events",
    "Add full-text search results highlighting with debounced queries",
    "Implement role-based access control for admin, editor, and viewer on the CMS routes",
    "Add client-side and server-side validation to the signup form with matching rules",
    "Fix the timezone bug that shifts scheduled posts by one hour twice a year",
    "Add an audit log for admin actions with actor, action, and timestamp",
    "Implement password reset via expiring signed tokens and a rate-limited request route",
    "Add a public status page fed by health checks with a five-minute cache",
    "Optimize the dashboard that renders 2000 rows without pagination or virtualization",
    "Migrate session storage from memory to the database with zero session loss on deploy",
    "Add i18n support for English and French with language negotiation and localized dates",
    "Fix the CORS failures blocking the staging frontend from the API",
    "Add image galleries to listings with lazy loading and a lightbox",
    "Implement two-step order confirmation with a review step and edit-back links",
    "Add webhook delivery for order events with retries and a dead-letter log",
    "Fix the memory leak in the real-time dashboard that grows through the day",
    "Add search-as-type autocomplete capped at eight suggestions with keyboard support",
    "Implement inventory decrement on checkout with oversell protection",
    "Add a printable invoice view generated from the order API with its own stylesheet",
    "Fix the login redirect loop for users with expired-but-present cookies",
    "Add data export for user-owned records in JSON with async job and download link",
    "Implement bookmark saving across devices with conflict-safe last-write-wins sync",
    "Add an onboarding checklist for new accounts with dismiss persistence",
    "Fix the mobile layout where the checkout button is unreachable below 360px",
    "Add structured logging with request ids across the API and surface it in errors",
    "Implement comment editing with a ten-minute window and an edited-marker",
    "Add subscription plan selection with prorated preview computed server-side",
    "Fix the double-submit on the payment button during slow networks",
    "Add a maintenance mode flag that returns friendly 503s and bypasses for staff",
    "Implement tag management for articles with create-rename-merge and counts",
    "Add a recent-activity feed on profiles from the existing events table",
    "Fix the stale list after deletion on the admin page that needs manual refresh",
    "Add API request validation schemas shared between client and server",
    "Implement saved search alerts with daily digest emails",
    "Add graceful degradation when the recommendations service is down",
    "Fix the session fixation on login by rotating the session id",
    "Add a bulk pricing import via CSV with dry-run validation and error report",
    "Implement draft autosave for the editor with conflict prompts on multi-tab edit",
    "Add a read-only public profile route with cached responses and purge on update",
    "Fix the N+1 queries loading the activity feed at fifty requests per page",
    "Add accessibility labels and error announcements across the checkout forms",
    "Implement per-environment API base urls with runtime injection and no rebuilds",
    "Add store credit adjustments behind an approval queue with two-step confirmation",
    "Fix the build pipeline that silently skips type checking on cached builds",
]

DPLAN_ITEMS = [
    "inspect the existing {area} implementation",
    "define the validation rules and error messages on the server first",
    "add the API route with tests before any UI work",
    "write the failing probe that demonstrates the bug",
    "design the response contract and freeze it in docs",
    "backfill data after the new column exists and is verified",
    "wire the form to the endpoint with loading and error states",
    "rotate the secret before changing consuming code",
    "seed the feature flag off by default",
    "add the regression test that fails before the fix",
]

DOBS = [
    "the repo already contains a working user API and profile page",
    "no tests currently touch the checkout area",
    "the schema lacks the column this feature needs",
    "the API contract is documented under docs/api with examples",
    "CI currently runs lint only, no tests",
    "the auth middleware exists and is used by sibling routes",
    "the target component is one 900-line file with mixed concerns",
    "a shared email client already exists in lib/mailer",
    "the frontend and API are separate apps in one repo",
    "the database is SQLite locally and PostgreSQL in production",
    "the upload handler writes to disk while production expects object storage",
    "the grid system was recently replaced with design tokens",
    "the e2e suite runs only on release branches weekly",
    "the request reaches the handler only after three middleware layers",
    "translations live in per-locale JSON files under messages/",
    "the events table already records everything the feed needs",
    "the cart state is currently localStorage-only with no server copy",
    "the search index refreshes nightly, not in real time",
    "two sibling components own copies of the same server data",
    "the flag framework was adopted last month but unused here",
    "deploys currently run migrations manually from a wiki page",
    "the validation rules exist client-side only",
    "the list page renders fine but fires one query per row",
    "the router plugin was upgraded and some hooks were renamed",
    "a recent commit added audit columns that this task can reuse",
    "sessions currently live in process memory",
    "the API returns timestamps in UTC while the UI assumes local",
    "the modal library is deprecated and scheduled for removal",
    "the pagination helpers already exist in a shared package",
    "upload limits are set at the proxy, not the app",
    "the form library supports async server errors natively",
    "the events pipeline can retry but has no dead-letter log",
    "the editor already autosaves drafts to local storage",
    "print styles exist globally but not for this view",
    "the seed script creates an admin user suitable for e2e",
    "the checkout totals are computed both client and server side",
]

DNEW_FACTS = [
    "inspection reveals the endpoint was fine and the query was the fault",
    "the failing behavior turns out to come from configuration, not code",
    "the requested capability already exists behind an unused flag",
    "the column the plan assumed must be created already exists",
    "the upstream API changed its contract last week",
    "the bug reproduces only with production data shapes",
    "the teammate already merged half of this work on another branch",
    "the library being upgraded has a documented migration guide",
    "load testing shows the real bottleneck is elsewhere",
    "the deploy tool reads migrations from a different folder than the plan assumed",
]

DHARD = [
    "the time budget covers only half the ideal work",
    "a teammate owns one of the affected packages",
    "the release freeze starts tomorrow",
    "the change spans three services with separate deploys",
    "part of the pipeline is generated code",
    "the request includes a security-sensitive surface",
    "production data cannot be used for testing",
    "an older client version must keep working",
]

DTOPICS = [
    "whether existing rows must be backfilled",
    "which roles may access the new panel",
    "whether old tokens remain valid",
    "the maximum file size to accept",
    "whether the legacy route must redirect",
    "which browsers must keep working",
    "the retention period for the new log",
    "whether offline support is expected",
]

AREAS = [
    "checkout", "profile", "catalog", "admin", "auth", "search",
    "upload", "notification", "dashboard", "settings", "billing", "editor",
]
