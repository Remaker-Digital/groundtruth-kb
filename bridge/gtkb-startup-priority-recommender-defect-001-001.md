NEW

# Implementation Proposal — GTKB-STARTUP-PRIORITY-RECOMMENDER-DEFECT-001 (Slice 0 Scoping)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-08
**Bridge thread:** `gtkb-startup-priority-recommender-defect-001`
**Type:** Scoping proposal for a stale-priority-recommender defect in the
session-startup payload generator. Slice 0 = scope confirmation +
verification plan; Slice 1 = mechanical fix; both proposed here for
single-GO/VERIFIED traversal because the fix is small.
**Status:** NEW
**Scope tag:** Defect — `bridge/INDEX.md` and `memory/work_list.md` cross-artifact consistency.

## Claim

`scripts/session_self_initialization.py` recommends top priority actions
that are already VERIFIED. Concretely, the 2026-05-08T04:34:00Z startup
disclosure for harness B (this session) listed three top priorities —
`GTKB-ENV-INVENTORY-001`, `GTKB-SYSTEMS-TERMINOLOGY-MAP-001`,
`GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` — but two of those are
VERIFIED at `bridge/gtkb-systems-terminology-map-001-004.md` (2026-05-06)
and `bridge/gtkb-resource-reference-disambiguation-001-004.md`
(2026-05-06) respectively, and the third's outstanding closure
landed in commit `206a1edb` earlier this session. Owner inspection
required AUQ rounds to surface this; the recommender produced false
priority signal.

## Specification Links

Cross-cutting (per `config/governance/spec-applicability.toml` triggers):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — blocking; this proposal is filed
  through `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — blocking;
  this section satisfies the mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — blocking; the test
  plan below derives from the linked specs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; backlog and work
  item are referenced as governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; traceability is
  the failure surface this proposal addresses.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the defect manifests
  at the `verified` lifecycle transition (work_list.md doesn't auto-update
  when bridge thread reaches VERIFIED).

Domain-specific:

- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — startup disclosure is
  release-gate-visible recommendation surface; stale priorities mislead
  release-readiness perception.
- `GOV-SESSION-SELF-INITIALIZATION-001` (per `acting-prime-builder.md`)
  — fresh-session startup disclosure must propose the three top priority
  actions; this proposal asks that those proposals be accurate.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — dashboard surfaces must
  distinguish implemented from intended state per
  `.claude/rules/operating-model.md` §3 alignment test 3.
- `.claude/rules/operating-model.md` §4 alignment test 3 — "Does it
  distinguish implemented behavior from desired behavior?" — the
  recommender currently fails this test.

Implementation files under verification:

- `scripts/session_self_initialization.py:980` — `_active_backlog_metrics`
  parses `memory/work_list.md` only.
- `scripts/session_self_initialization.py:990` — `top_priority_actions`
  is `visible_items[:3]` with no INDEX cross-check.
- `bridge/INDEX.md` — canonical workflow state, the authoritative VERIFIED
  signal that the recommender currently ignores.
- `memory/work_list.md` — narrative work items; entries lag VERIFIED
  state because no automated update exists.

## Owner Decisions / Input

Owner authorization captured this session via AUQ at 2026-05-08:

| Question | Answer |
|---|---|
| All three Top Priority Actions are VERIFIED — what shall I do? | "File a defect bridge for the startup payload" |

This authorizes filing this NEW proposal. Implementation (the mechanical
fix proposed below) requires Codex GO before code changes. No additional
owner approval is required to file this NEW.

## Defect Mechanics

`_active_backlog_metrics(project_root)` (line 980-994) of
`scripts/session_self_initialization.py`:

1. Reads `memory/work_list.md` text and parses it via
   `_parse_active_work_items`.
2. Classifies each entry by dashboard scope.
3. Returns `top_priority_actions = visible_items[:3]` — the first 3
   visible items in work_list order, regardless of bridge state.

The recommender does NOT:

- Read `bridge/INDEX.md` to check whether each candidate work item has
  a VERIFIED bridge thread (the dashboard scan separately produces
  bridge metrics at `_bridge_metrics`, line 997, but that data is not
  joined into the priority recommendation).
- Read `groundtruth.db` `work_items` table for completion state.
- Honor any "verified-with-residuals" annotation in work_list.md (none
  currently exists; entries are narrative-only).

Result: when an item's bridge thread reaches VERIFIED but the work_list
narrative lags, the recommender keeps surfacing the item as a top
priority. Two such stale items appeared in this session's startup; both
had been VERIFIED for two days.

## Proposed Fix (Slice 1)

Add a VERIFIED-state filter to `_active_backlog_metrics`:

1. After parsing visible items from work_list.md, build a set of
   document names from `bridge/INDEX.md` whose latest entry is VERIFIED
   and whose `Document:` name maps to the work-item ID. The mapping
   convention is: lowercased + hyphenated work-item ID becomes
   `Document:` name (e.g., `GTKB-ENV-INVENTORY-001` →
   `gtkb-env-inventory-001`). The `_bridge_metrics` parser already
   reads INDEX; expose its output as a side-channel.
2. Filter visible items: drop those whose ID maps to a VERIFIED bridge
   thread, UNLESS the work_list entry contains a `**Status:** VERIFIED
   (residual: ...)` line (the explicit-residuals override).
3. The remaining `visible_items[:3]` is the corrected
   `top_priority_actions`.

Edge case: a work item may not have a 1:1 bridge thread (e.g., a
governance item with multiple slices). For Slice 1, the mapping is
best-effort; items without a discoverable bridge thread are treated as
"not VERIFIED" (current behavior). A follow-on slice may add explicit
work-item-to-bridge-thread links in MemBase if best-effort proves
insufficient.

Out of scope for Slice 1:

- Auto-updating work_list.md when bridge VERIFIED lands (separate
  bridge thread `gtkb-gov-backlog-source-of-truth` covers this
  upstream).
- Removing VERIFIED items from work_list.md entirely (owner-owned
  curation; the recommender filter is non-destructive).
- `groundtruth.db` work_items table cross-check (deferred until
  backlog source-of-truth migration completes).
- Changes to the dashboard surface beyond what the recommender
  produces.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-recommender-1 | Filter VERIFIED items | `tests/scripts/test_session_self_initialization.py::test_top_priority_excludes_verified_bridge_thread` — fixture work_list with 3 items, fixture INDEX where item 1 is VERIFIED; recommender returns items 2 and 3 only |
| T-recommender-2 | Mapping convention | `test_work_item_id_maps_to_bridge_document_name` — verify `GTKB-ENV-INVENTORY-001` resolves to `gtkb-env-inventory-001` Document entry |
| T-recommender-3 | Best-effort fallback | `test_unmapped_work_item_treated_as_active` — work item with no matching bridge Document still appears in priorities |
| T-recommender-4 | Residuals override | `test_verified_with_residuals_annotation_remains_active` — work_list entry tagged `**Status:** VERIFIED (residual: ...)` is still recommended |
| T-recommender-5 | INDEX parse robustness | Reuse `_bridge_metrics` regex `^(NEW\|REVISED\|GO\|NO-GO\|VERIFIED):\s+(bridge/[^\s]+)` so INDEX-format drift is detected at one parser |
| T-recommender-6 | Live regression | `python scripts/session_self_initialization.py --json --no-write` against the live tree must NOT include `GTKB-SYSTEMS-TERMINOLOGY-MAP-001` or `GTKB-RESOURCE-REFERENCE-DISAMBIGUATION-001` in `top_priority_actions` after the fix lands |

| Cross-cutting linked spec | Verification evidence |
|---|---|
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This Specification Links section |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-recommender-1..6 derive from defect mechanics |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal is filed via `bridge/INDEX.md` |
| `.claude/rules/operating-model.md` §4 test 3 | T-recommender-1 directly tests "distinguishes implemented from desired" by gating on VERIFIED |

## Acceptance Criteria

For VERIFIED:

1. `scripts/session_self_initialization.py` no longer recommends items
   whose mapped bridge thread is VERIFIED (T-recommender-1, T-recommender-6).
2. Best-effort mapping does not break startup for unmapped items
   (T-recommender-3).
3. `**Status:** VERIFIED (residual: ...)` annotation in work_list.md
   keeps the entry recommended (T-recommender-4).
4. New tests added in `tests/scripts/test_session_self_initialization.py`
   pass; existing startup tests remain green.
5. `python scripts/session_self_initialization.py --json --no-write`
   live regression confirms the two stale items do not appear in
   `top_priority_actions`.
6. `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
   continues to PASS.

## Risk / Rollback

Risk surface:

- **Mapping ambiguity:** work-item IDs and bridge `Document:` names
  share a convention but it's not enforced. Items that don't map will
  still appear (acceptable; same as current behavior). Items that map
  to the wrong bridge thread could be silently filtered out — this is
  the primary risk. Mitigation: T-recommender-2 + a dry-run report
  printed to startup diagnostics ("recommender filtered N VERIFIED
  items: <ids>").
- **Owner overrides:** if owner wants a VERIFIED item kept on the
  priority list (e.g., active follow-on residuals), the
  `**Status:** VERIFIED (residual: ...)` annotation provides the
  override. T-recommender-4 verifies it.

Rollback: revert the `scripts/session_self_initialization.py` change
+ remove the new test file. The recommender returns to current
unfiltered behavior. No data migration; no schema change; no INDEX
mutation.

## Files Expected To Change (Slice 1)

- `scripts/session_self_initialization.py` — add VERIFIED-state filter
  (~30-50 LOC, contained inside `_active_backlog_metrics`).
- `tests/scripts/test_session_self_initialization.py` — add 6 new tests
  (T-recommender-1..6) per the test plan above.

No changes to `bridge/INDEX.md`, `groundtruth.db`, `memory/work_list.md`,
hooks, or rules in this slice.

## Prior Deliberations

`db.search_deliberations("startup recommender priority work_list cross-check", limit=5)`
returned:

- DELIB-1083 — Startup Token And Premature Wrap-Up Feedback (related
  but distinct: token-cost discussion, not stale-priority).
- DELIB-1277 / DELIB-0727 — `post-phase-a-prioritization` bridge thread
  (general prioritization workflow; not specific to the recommender).
- DELIB-0016, DELIB-0186 — broader process integrity (not directly
  addressing this defect).

No prior deliberation found that rejects a recommender VERIFIED-state
filter. No conflicting design decisions.

## Pre-Filing Preflight

- bridge_document_name: `gtkb-startup-priority-recommender-defect-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-priority-recommender-defect-001-001.md`
- operative_file: `bridge/gtkb-startup-priority-recommender-defect-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

All triggered cross-cutting specs (4 advisory + 2 blocking) are cited
in `## Specification Links` above. Self-check ran 2026-05-08 against
the filed `-001`. Codex should recompute `packet_hash` at review time
against the operative file as filed; recording a specific hash here
would be self-referential because adding the hash to this file changes
the hash.

## Recommended Commit Type

For this proposal filing: `docs(bridge):` — bridge-protocol artifact only,
no code or test changes in this commit.

For the eventual Slice 1 implementation commit: `fix(startup):` —
defect repair with no new capability surface, matching the pattern
of the drift-control fix earlier this session.

## Requested Loyal Opposition Action

Review this proposal for GO. Specific questions for Codex:

1. Is the best-effort work-item-ID-to-bridge-Document mapping
   acceptable for Slice 1, or should an explicit MemBase link table be
   filed first?
2. Is the `**Status:** VERIFIED (residual: ...)` annotation convention
   sufficient owner-override, or should we propose an explicit
   `**recommend_until:** <date>` field in work_list.md instead?
3. Does the diagnostic dry-run output ("recommender filtered N
   VERIFIED items: <ids>") need to land in startup-disclosure user-visible
   text, or is logging to startup diagnostics sufficient?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
