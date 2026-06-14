NEW

bridge_kind: implementation_proposal
Document: gtkb-wi-4534-claim-role-eligibility-guard-slice-a
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 9c338cc5-135b-4eda-b66d-6900c89bf047
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4534
target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_go_impl_claim_role_gating.py"]

# Implementation Proposal — WI-4534 Claim Role-Eligibility Guard (Slice A): refuse `go_implementation` claims from Loyal-Opposition-role sessions

## Summary

WI-4534: a session whose dispatch-generated session id carries the
`loyal-opposition` role (e.g. `2026-06-13T20-07-29Z-loyal-opposition-D-20c71a`)
can acquire a `go_implementation` work-intent claim on a GO-latest bridge
thread. `scripts/bridge_work_intent_registry.py` assigns the claim kind solely
from the thread's latest `bridge/INDEX.md` status: `_claim_values()` (lines
239-263) sets `claim_kind = CLAIM_KIND_GO_IMPLEMENTATION` whenever
`latest_status == "GO"`, and `acquire()` (lines 279-321) performs **no check on
the claiming session's role**. The resulting claim carries a 30-minute
implementation deadline plus a 10-minute grace (extendable to a 2-hour cap) and
is held under the table's `UNIQUE(thread_slug)` constraint, so it blocks the
real Prime Builder implementer from claiming and implementing the GO'd thread
until the Loyal-Opposition claim lapses.

This was observed live this session on `gtkb-tafe-dual-write-index-parity`
(claim rowid 1864, held by session `2026-06-13T20-07-29Z-loyal-opposition-D-20c71a`,
acquired 20:07:37Z, grace through 20:47:37Z), which repeatedly blocked a Prime
Builder session from implementing the Codex-GO'd Slice A across multiple
autonomous cycles.

**Scope (Slice A, per the bounded PAUTH).** This slice is a claim-layer
**role-eligibility guard** at the registry chokepoint. The complementary
GO-event dispatch-routing correction is explicitly **deferred to a separate
slice (Part 2)** per the PAUTH `forbidden_operations`. This slice does **not**
change dispatcher routing, cutover, or any canonical bridge-state write path; it
only reads `bridge/INDEX.md` latest-status (read-only) and gates one claim
grant.

## Specification Links

- **GOV-SESSION-ROLE-AUTHORITY-001** — the durable Prime Builder vs Loyal
  Opposition authority split. Implementing a GO'd bridge thread is Prime Builder
  work; a Loyal-Opposition-role session must not assume Prime Builder
  implementation authority. This guard enforces that authority boundary at the
  work-intent claim layer (a `go_implementation` claim is an implementation
  intent).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` is the canonical bridge
  workflow authority and work-intent claims coordinate bridge implementation
  work against it. The guard preserves the integrity of `go_implementation`
  claim ownership (only an eligible Prime implementer may hold one). Slice A
  reads INDEX latest-status read-only and writes nothing to `bridge/INDEX.md`.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing specification it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan
  below derives tests from each linked specification and acceptance criterion.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`; no application/adopter surface is touched.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 governs the
Prime Builder / Loyal Opposition authority boundary, and WI-4534 defines the
defect and the role-eligibility-guard remedy authorized by
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
(allowed mutation classes: `source`, `test_addition`). No new or revised
requirement is needed for Slice A. The GO-event dispatch-routing correction
(Part 2) is deferred to a separate slice per the PAUTH and is out of scope here.

## Prior Deliberations

- **DELIB-20263200** — owner AUQ authorizing the bounded WI-4534 Slice A PAUTH
  (claim role-eligibility guard; allowed `source` + `test_addition`; forbids
  GO-event dispatch routing changes [Part 2 deferred] and cutover / canonical
  bridge-state write paths).
- Deliberation searches for `go_implementation work-intent claim loyal
  opposition role gate dispatch blocks prime implementer` and `WI-4534 claim
  role harness dispatch go implementation` returned **no** prior deliberations;
  this is novel implementation work building on the authority split in
  GOV-SESSION-ROLE-AUTHORITY-001.

## Design (Slice A)

All changes are in `scripts/bridge_work_intent_registry.py`.

1. **New helper `_session_role(session_id: str) -> str | None`.** Parse the
   canonical dispatch session-id format
   (`<compact-ISO8601>-<role>-<harness_id>-<uuid6>`, produced by
   `cross_harness_bridge_trigger.py::_new_dispatch_id`) and return the embedded
   role token. Anchored regex:
   `^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-(prime-builder|loyal-opposition)-`.
   Returns `"prime-builder"`, `"loyal-opposition"`, or `None` when the id does
   not match the dispatch format (interactive / non-dispatch UUID session ids
   such as `CLAUDE_CODE_SESSION_ID`, which carry no role token).

2. **Role-eligibility gate in `acquire()`.** Before granting the claim, when the
   thread's latest status is `GO` AND `_session_role(session_id) ==
   "loyal-opposition"`, refuse the claim — return `False` without recording any
   row. A Loyal-Opposition-role session is not eligible to hold a
   `go_implementation` claim. All other cases are unchanged:
   - prime-builder-role dispatch sessions: acquire `go_implementation` as today;
   - interactive / unparseable session ids (`_session_role` → `None`): ungated,
     acquire as today (a Prime interactive session must not be blocked);
   - loyal-opposition sessions on a non-GO-latest thread: still acquire the
     normal `draft` claim (LO legitimately drafts NEW/REVISED verdicts) — the
     guard is GO-scoped only.

3. **Contract preservation.** The gate returns `False` (the existing
   "not acquired" signal) rather than raising, so existing callers
   (`scripts/bridge_claim_cli.py:123`; the cross-harness trigger's prime-only
   batch `cross_harness_bridge_trigger.py:772`) need no change and the CLI
   surfaces its existing exit-2 path.

**Why the registry chokepoint, not the dispatcher.** The cross-harness trigger
already acquires prime work-intent only for prime-builder dispatches
(`cross_harness_bridge_trigger.py:3110` guard), so the observed Loyal-Opposition
claim arrives through the CLI path (`bridge_claim_cli.py:123 → acquire()`).
`acquire()` is the single chokepoint every claim path traverses, so gating there
gives defense regardless of caller with minimal blast radius. The dispatcher
GO-routing correction is Part 2 (deferred per the PAUTH).

**Blast radius.** The only non-test callers of `acquire()` are
`bridge_claim_cli.py:123` (CLI `claim` — correctly affected: an LO dispatch
session is refused on a GO-latest thread) and
`cross_harness_bridge_trigger.py:772` (`_acquire_prime_work_intent_batch` —
prime-builder session ids only, unaffected). Existing tests
(`test_go_impl_claim_timebox.py`, `test_cross_harness_bridge_trigger_work_intent.py`,
`test_implementation_authorization.py`, `test_implementation_start_gate.py`,
`test_bridge_propose_helper_work_intent.py`) use synthetic session ids that do
not match the loyal-opposition dispatch format, so `_session_role` returns
`None` and they are unaffected.

## Verification Plan (Specification-Derived)

New test module `platform_tests/scripts/test_go_impl_claim_role_gating.py`
(mirrors the temp-project + `bridge/INDEX.md` fixture pattern in
`test_go_impl_claim_timebox.py`). Every test's oracle is the `acquire()` return
value plus the `claim_status()` record.

| Spec / acceptance criterion | Test | Method / oracle |
|---|---|---|
| GOV-SESSION-ROLE-AUTHORITY-001 — LO not eligible for a `go_implementation` claim | `test_loyal_opposition_dispatch_session_refused_on_go` | `acquire()` with a `…-loyal-opposition-D-…` id on a GO-latest fixture returns `False`; `claim_status` shows no recorded row (oracle: return value + DB-row absence) |
| WI-4534 — Prime unblocked after LO refusal | `test_prime_can_claim_after_lo_refused` | LO refused, then a `…-prime-builder-B-…` id acquires → `True`, `claim_kind == go_implementation` (oracle: return + `claim_status`) |
| Role boundary preserved for Prime | `test_prime_builder_dispatch_session_granted_on_go` | `…-prime-builder-B-…` id on GO fixture → `True`, `go_implementation` (oracle: return + `claim_status`) |
| Interactive sessions ungated | `test_interactive_uuid_session_granted_on_go` | UUID id (no role token) on GO fixture → `True` (not refused) (oracle: return value) |
| Guard is GO-scoped only | `test_loyal_opposition_granted_draft_on_non_go` | `…-loyal-opposition-D-…` id on a REVISED-latest fixture → `True`, `claim_kind == draft` (oracle: return + `claim_status`) |
| GOV-FILE-BRIDGE-AUTHORITY-001 — INDEX read-only | covered by all fixtures | guard reads INDEX latest-status only; no `bridge/INDEX.md` write occurs |

Pre-file code-quality gates (run before the implementation report):
`python -m ruff check` and `python -m ruff format --check` on the changed files,
and `python -m pytest platform_tests/scripts/test_go_impl_claim_role_gating.py -q`.

## Risk / Rollback

- **Risk: low.** Additive guard at one chokepoint; the refusal path fires only
  for loyal-opposition dispatch session ids on GO-latest threads. No behavior
  change for Prime Builder or interactive sessions, and no change for LO on
  non-GO threads.
- **Edge case:** an LO session mid-verdict-drafting claims while latest is
  NEW/REVISED — unaffected (the guard is GO-scoped; LO legitimately holds a
  `draft` claim there). The refusal fires only on GO-latest, where an LO session
  has no legitimate work-intent.
- **Concurrency:** none introduced; `acquire()` already runs under
  `BEGIN IMMEDIATE`.
- **Rollback:** revert `_session_role` and the `acquire()` check, and delete the
  new test module. No migration, no state change, no canonical artifact touched.

## Owner Decisions / Input

- **DELIB-20263200** (owner AUQ): authorized the bounded WI-4534 Slice A PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
  (allowed_mutation_classes `source` + `test_addition`; forbidden_operations:
  GO-event dispatch routing changes [Part 2 deferred] and cutover / canonical
  bridge-state writes).
- **Session owner AUQ (2026-06-13):** owner selected "Fix WI-4534 (dispatch
  defect)", directing this session to implement the claim role-eligibility
  guard.
- No further owner decision is required for Slice A.

## Recommended Commit Type

`fix:` — repairs a defect (a Loyal-Opposition-role session wrongly holding a
Prime-blocking `go_implementation` claim) with no new capability surface.
