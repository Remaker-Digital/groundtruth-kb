REVISED

bridge_kind: implementation_proposal
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 003
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

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

# Implementation Proposal (REVISED) — WI-4534 Slice A: Role-Eligibility Guard on `go_implementation` Claim Acquisition

## Revision Scope (addresses NO-GO `-002`)

This REVISED proposal addresses the three findings in the Loyal Opposition
NO-GO at `bridge/gtkb-wi4534-claim-role-eligibility-guard-002.md`:

- **F1 (duplicate threads): RESOLVED.** The competing duplicate
  `gtkb-wi-4534-claim-role-eligibility-guard-slice-a` was **WITHDRAWN** (at its
  `-003`; see `bridge/INDEX.md`). This thread is the single surviving WI-4534
  Slice A chain and supersedes that duplicate.
- **F2 (unknown harness id → token authorization): FIXED.** Eligibility now
  derives **only** from the durable harness registry, never the session-id role
  token. A parsed harness id absent from the registry is **rejected** (no token
  fallback). A `prime-builder` token whose registry role is `loyal-opposition`
  is likewise rejected (registry is authoritative).
- **F3 (unparseable UUID fail-open): FIXED.** Un-resolvable (interactive/raw-UUID)
  session ids now require **positive** Prime evidence — the owner-declared
  interactive-Prime marker `.claude/session/active-session-role.json` recording a
  `prime-builder` session-stated role. Absent/unreadable/`loyal-opposition`
  marker → rejected. A Codex/LO automation session (UUID id, no Prime marker) is
  therefore rejected on GO; the fail-open path is removed.

## Summary

WI-4534 is a bridge-dispatch defect: a non-Prime (Loyal-Opposition-role) harness
can acquire a `go_implementation` work-intent claim on a GO-latest bridge thread,
blocking the Prime Builder implementer. Observed repeatedly this session blocking
the owner-authorized TAFE cutover (WI-4508): sessions
`2026-06-13T19-13-44Z-loyal-opposition-D-54f7e1` and
`2026-06-13T20-07-29Z-loyal-opposition-D-20c71a` each held `go_implementation`
claims on `gtkb-tafe-dual-write-index-parity` while harness `D` is
`loyal-opposition` per the canonical registry.

**Root cause (confirmed in code):**
`scripts/bridge_work_intent_registry.py` `_claim_values()` sets
`claim_kind = CLAIM_KIND_GO_IMPLEMENTATION` solely when
`_latest_status(slug) == "GO"` (lines ~247-263); `acquire()` performs no role
check. So any session acquiring a claim on a GO-latest thread is granted a
`go_implementation` claim regardless of whether its harness is durably eligible
to implement.

**Slice A (this proposal):** a registry-authoritative role-eligibility guard at
the `go_implementation` mint point — the defensive floor that rejects the
ineligible claim at acquisition regardless of how the session was dispatched.

**Part 2 (deferred per PAUTH; NOT in this proposal):** route GO-event dispatch to
prime-builder harnesses only (in the cross-harness trigger / dispatcher). The
PAUTH `forbidden_operations` explicitly defers GO-event dispatch routing changes
to a separate slice; this proposal changes no dispatch routing, cutover, or
canonical bridge-state write path.

## Specification Links

- **GOV-SESSION-ROLE-AUTHORITY-001** — durable-role authority: implementation
  authority is keyed to the durable harness role. A `go_implementation` claim is
  an implementation-authority action; this guard enforces it is held only by a
  durably `prime-builder` (or compat `acting-prime-builder`) harness, resolved
  from the canonical registry rather than a transient session-id token.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the work-intent claim registry serves
  bridge coordination; the guard preserves canonical bridge state and adds no
  `bridge/INDEX.md` write surface. It only constrains who may hold an
  implementation claim.
- **DCL-SESSION-ROLE-RESOLUTION-001** — deterministic role resolution; the guard
  resolves the acquiring harness's durable role via the canonical stdlib-only
  registry reader (`scripts/harness_projection_reader.py`) rather than ad-hoc
  authority parsing.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing specification it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test below
  has a real oracle.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`; no application/adopter surface is touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — the fix is delivered as
  durable, tracked, phased artifacts (Slice A guard + tests; Part 2 deferred).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — deferred (Part 2),
  superseded (the withdrawn duplicate), and captured-defect (WI-4534) lifecycle
  states are handled explicitly.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision
  (DELIB-20263200), PAUTH, work item (WI-4534), specs, and tests are linked and
  traceable.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 (durable-role
authority) and WI-4534 govern this work; no new or revised requirement is needed
for Slice A. The Part 2 dispatch-routing correction is deferred to its own slice
per the PAUTH and is out of scope here.

## Prior Deliberations

- **DELIB-20263200** — owner AUQ (2026-06-13) authorizing this WI-4534 Slice A
  fix and the bounded PAUTH.
- **DELIB-20263195** — the TAFE cutover authorization (the work this defect was
  blocking).
- Superseded sibling: `bridge/gtkb-wi-4534-claim-role-eligibility-guard-slice-a`
  (WITHDRAWN at `-003`) — a duplicate Slice A proposal whose token-only role
  source this thread improves upon with registry-authoritative resolution.
- Related dispatch-reliability items: WI-4527 (go-implementation claim TTL),
  WI-4479 (headless dispatch crash), WI-4396 (lease contention in dispatch logs).
- Deliberation searches for the role-eligibility-guard topic returned no prior
  deliberation proposing a role-eligibility guard on work-intent claim
  acquisition; this is the first treatment of the claim-kind/role mismatch.

## Design (Slice A, REVISED)

All changes are in `scripts/bridge_work_intent_registry.py` plus a new test
module. Two new helpers (lazy-importing the stdlib-only
`scripts/harness_projection_reader.py` — no DB, hook-safe):

1. `_dispatch_harness_id(session_id) -> str | None` — parse the dispatcher
   session-id format `<compact-ISO8601>-<role>-<harness_id>-<hash>` (produced by
   `cross_harness_bridge_trigger._new_dispatch_id`) with an anchored regex
   `^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-(?:prime-builder|loyal-opposition|acting-prime-builder)-([A-Za-z0-9]+)-[0-9a-fA-F]{6}$`.
   Return the captured `harness_id`, or `None` for non-dispatch (interactive /
   raw-UUID) ids. The role token is matched only to locate the harness-id
   segment; it is **never** used for authorization.

2. `_go_implementation_eligible(session_id, *, project_root) -> bool`:
   - **Dispatch id:** load the durable projection via
     `harness_projection_reader.load_harness_projection(project_root)` and resolve
     `role_set_for_id(doc, harness_id)`. Eligible iff the durable role set
     intersects `{prime-builder, acting-prime-builder}`.
     - **F2:** an empty role set (harness id absent from the registry) → return
       `False` (reject; no token fallback).
     - **F2/d:** authorization derives only from the registry, so a token/registry
       mismatch resolves from the registry (token ignored).
   - **Non-dispatch id (un-resolvable):** **F3** — require positive Prime
     evidence. Read the owner-declared marker
     `.claude/session/active-session-role.json`; eligible iff it records a
     `prime-builder` session-stated role. Absent / unreadable / `loyal-opposition`
     → return `False` (reject). No fail-open.

3. In `acquire()`, when the computed `claim_kind == CLAIM_KIND_GO_IMPLEMENTATION`
   and `not _go_implementation_eligible(session_id, project_root=project_root)`:
   raise `WorkIntentRegistryError` with a clear message naming the session and
   resolved role (the claim CLI surfaces a non-zero exit). The guard is scoped to
   `go_implementation` only — draft claims (non-GO threads), same-session
   re-acquisition, durably-prime acquisitions, and registry-`acting-prime-builder`
   acquisitions are unaffected.

**Known limitation (documented, not a Slice-A blocker):** the interactive-Prime
marker is session-global and invalidated at SessionStart; it is the best
available positive signal for un-resolvable interactive ids and matches the
NO-GO F3 contract. Strengthening interactive-session role binding (e.g.,
harness-identity-bound evidence) is a candidate for the Part 2 / a follow-on
slice.

**Why the registry chokepoint, not the dispatcher:** the cross-harness trigger
already acquires prime work-intent only for prime-builder dispatches
(`cross_harness_bridge_trigger.py:3110` guard), so the observed Loyal-Opposition
claim arrives through the CLI path (`bridge_claim_cli.py:123 → acquire()`).
`acquire()` is the single chokepoint every claim path traverses. Dispatcher
GO-routing is Part 2 (deferred per the PAUTH).

## Verification Plan (Specification-Derived)

New tests in `platform_tests/scripts/test_work_intent_role_eligibility.py`, each
using an isolated `project_root` fixture (a test `harness-state/harness-registry.json`
with harnesses `B=prime-builder`, `D=loyal-opposition`, `X=acting-prime-builder`;
a test `bridge/INDEX.md` with one GO-latest and one NEW-latest thread;
`groundtruth.db` auto-created by `_ensure_schema`; and, where relevant, a test
`.claude/session/active-session-role.json` marker). Pattern mirrors
`platform_tests/scripts/test_go_impl_claim_timebox.py`. Every test's oracle is the
`acquire()` outcome (raise vs. acquired) plus the `claim_status()` record.

| Spec / acceptance criterion | Test | Oracle / Method |
|---|---|---|
| GOV-SESSION-ROLE-AUTHORITY-001 — LO dispatch harness rejected | `test_go_impl_rejected_for_lo_dispatch_harness` | `…-loyal-opposition-D-<hash>`, registry D=loyal-opposition, GO-latest → `acquire()` raises `WorkIntentRegistryError`; no row inserted |
| GOV-SESSION-ROLE-AUTHORITY-001 — prime dispatch harness allowed | `test_go_impl_allowed_for_prime_dispatch_harness` | `…-prime-builder-B-<hash>`, registry B=prime-builder, GO-latest → acquired; `claim_kind=go_implementation` |
| F2 — unknown harness id rejected (no token fallback) | `test_go_impl_rejected_for_unknown_harness_id` | `…-prime-builder-Z-<hash>`, Z absent from registry, GO-latest → raises (token says prime-builder but unknown ≠ Prime) |
| F2/d — registry authoritative over token | `test_go_impl_resolves_from_registry_not_token` | `…-prime-builder-D-<hash>`, registry D=loyal-opposition, GO-latest → raises (registry wins) |
| F3/a — LO UUID session without marker rejected | `test_go_impl_rejected_for_uuid_session_without_prime_marker` | raw-UUID session id, no marker (or marker=loyal-opposition), GO-latest → raises (no fail-open) |
| F3/b — owner-declared interactive Prime accepted | `test_go_impl_allowed_for_uuid_session_with_prime_marker` | raw-UUID session id, `.claude/session/active-session-role.json` role=prime-builder, GO-latest → acquired |
| Guard scoped to go_implementation only | `test_draft_claim_unaffected_for_lo_harness_on_non_go_thread` | `…-loyal-opposition-D-<hash>` on NEW-latest thread → acquired as `draft` |
| acting-prime-builder registry compat | `test_go_impl_allowed_for_registry_acting_prime_builder` | registry X=acting-prime-builder, `…-<role>-X-<hash>`, GO-latest → acquired (compat durable role is Prime-eligible) |

Pre-file code-quality gates (before the implementation report): `python -m ruff
check` + `python -m ruff format --check` on both changed files; `python -m pytest
platform_tests/scripts/test_work_intent_role_eligibility.py -q`. The existing
`platform_tests/scripts/test_go_impl_claim_timebox.py` must remain green
(no timebox regression).

## Risk / Rollback

- **Risk: low-moderate.** The claim registry is concurrency-hot, but the change
  is additive and scoped: it only *rejects* new `go_implementation` acquisitions
  by durably-non-prime harnesses (and by un-resolvable ids lacking a Prime
  marker). Drafts, prime acquisitions, registry-acting-prime acquisitions,
  same-session re-acquire, and existing claims are unaffected; no schema change.
- **Failure mode considered:** a legitimate interactive Prime session that did
  not declare `::init gtkb pb` (no marker) and uses a raw-UUID id would be
  rejected for a `go_implementation` claim. This is the intended NO-GO F3
  contract (positive Prime evidence required); the remedy is to declare the Prime
  session role. Documented above as a known limitation.
- **Rollback:** revert the two helpers + the `acquire()` check in
  `bridge_work_intent_registry.py` and delete the new test module; no migration,
  no state change, no canonical artifact touched.

## Owner Decisions / Input

- **DELIB-20263200** (owner AUQ, 2026-06-13): authorized the bounded WI-4534
  Slice A PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
  (active; allows `source` + `test_addition`; forbids GO-event dispatch routing
  changes [Part 2 deferred] and cutover / canonical bridge-state writes).
- **Session owner AUQ (2026-06-13):** owner selected "Fix WI-4534 (dispatch
  defect)" and then "Carry surviving WI-4534 thread to GO", directing this
  session to revise the surviving thread to GO, and authorized pre-drafting this
  revision to file on the next free claim window to break the observed claim-churn.
- No further owner decision is required for Slice A.

## Recommended Commit Type

`fix:` — repairs a defect (registry-authoritative role-eligibility guard on the
work-intent claim registry) with no new user-facing capability surface; adds a
regression test module.
