REVISED

bridge_kind: implementation_proposal
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 007
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

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py", "platform_tests/scripts/test_go_impl_claim_timebox.py"]

# Implementation Proposal (REVISED -007) — WI-4534 Slice A: Role-Eligibility Guard + Timebox-Regression Scope Expansion

## Revision Scope (addresses verification NO-GO -006)

This REVISED proposal addresses the Loyal Opposition verification NO-GO at
`bridge/gtkb-wi4534-claim-role-eligibility-guard-006.md`. The GO'd guard
implementation (the `-003`/`-004` design, implemented in
`scripts/bridge_work_intent_registry.py` and
`platform_tests/scripts/test_work_intent_role_eligibility.py`) is correct and its
8 role-eligibility tests pass. However, by correctly making `go_implementation`
claims Prime-only, the guard breaks the pre-existing regression suite
`platform_tests/scripts/test_go_impl_claim_timebox.py` (6 failures), whose tests
asserted the prior buggy "any session may hold a `go_implementation` claim"
behavior — including the CLI-path test
`test_cli_claim_extend_status_reports_go_implementation_fields` exercising
`CODEX_THREAD_ID=codex-session`. The GO'd `-004` `target_paths` did not include
that timebox test, so repairing it requires an owner-approved scope expansion.

Owner decision **DELIB-20263205** (AUQ Option A) authorizes expanding scope to
edit `platform_tests/scripts/test_go_impl_claim_timebox.py` and update its 6
failing timebox/CLI expectations to Prime-eligible session ids, preserving the
strict F3 positive-Prime-evidence contract. Option B (relaxing F3) was rejected
as reopening the `-002` fail-open concern.

**Changes vs the GO'd `-003`:** (1) `target_paths` adds
`platform_tests/scripts/test_go_impl_claim_timebox.py`; (2) the Verification Plan
adds the timebox/CLI regression repair; (3) Owner Decisions cites
DELIB-20263205; (4) the PAUTH is supplemented to cover existing-test
modification of the timebox test. The guard **design itself is unchanged** from
the GO'd `-003`.

## Summary

WI-4534: a non-Prime (Loyal-Opposition-role) harness could acquire a
`go_implementation` work-intent claim on a GO-latest bridge thread, blocking the
Prime Builder implementer. Root cause: `bridge_work_intent_registry._claim_values()`
sets `claim_kind = CLAIM_KIND_GO_IMPLEMENTATION` solely from latest `GO` status;
`acquire()` performed no role check. Slice A adds a registry-authoritative
role-eligibility guard at the `go_implementation` mint point. Part 2 (GO-event
dispatch routing) remains deferred per the PAUTH; this proposal changes no
dispatch routing, cutover, or canonical bridge-state write path.

## Specification Links

- **GOV-SESSION-ROLE-AUTHORITY-001** — durable-role authority; a
  `go_implementation` claim is an implementation-authority action held only by a
  durably `prime-builder` (or compat `acting-prime-builder`) harness, resolved
  from the canonical registry, not a session-id token.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the work-intent claim registry serves
  bridge coordination; the guard adds no `bridge/INDEX.md` write surface.
- **DCL-SESSION-ROLE-RESOLUTION-001** — deterministic role resolution via the
  canonical stdlib-only registry reader `scripts/harness_projection_reader.py`.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing specification it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test has a
  real oracle, and the previously-regressed timebox suite is repaired green.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — phased, tracked
  artifacts (Slice A guard + tests + scope-expansion revision; Part 2 deferred).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — deferred (Part 2),
  superseded-duplicate, and captured-defect lifecycle states handled explicitly.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decisions
  (DELIB-20263200, DELIB-20263205), PAUTH, WI-4534, specs, tests linked.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 and WI-4534
govern the guard; DELIB-20263205 authorizes the bounded scope expansion to repair
the timebox regression. No new or revised requirement is needed.

## Prior Deliberations

- **DELIB-20263200** — owner AUQ authorizing WI-4534 Slice A + the bounded PAUTH.
- **DELIB-20263205** — owner AUQ (Option A) authorizing this revision's scope
  expansion to edit `test_go_impl_claim_timebox.py` and update its 6 failing
  timebox/CLI tests to Prime-eligible session ids; preserve strict F3; reject
  Option B.
- **DELIB-20263195** — TAFE cutover authorization (the work this defect blocked).
- `bridge/gtkb-wi4534-claim-role-eligibility-guard-006.md` — the verification
  NO-GO this revision addresses.
- Superseded duplicate `gtkb-wi-4534-claim-role-eligibility-guard-slice-a`
  (WITHDRAWN) — token-only design improved upon here with registry-authoritative
  resolution.

## Design (Slice A) — unchanged from the GO'd -003

In `scripts/bridge_work_intent_registry.py` (already implemented on disk and
verified by the 8 passing role-eligibility tests):

1. `_dispatch_harness_id(session_id) -> str | None` — parse the dispatcher
   session-id format `<compact-ISO8601>-<role>-<harness_id>-<hash>` with an
   anchored regex; return the captured `harness_id`, else `None` for non-dispatch
   (interactive/raw-UUID) ids. The role token only locates the harness-id
   segment; it is never used for authorization.
2. `_go_implementation_eligible(session_id, *, project_root) -> bool`:
   - **Dispatch id:** resolve the parsed harness id's durable role set via
     `harness_projection_reader.load_harness_projection` +
     `role_set_for_id`. Eligible iff that durable set intersects
     `{prime-builder, acting-prime-builder}`. An unknown harness id (empty set)
     returns `False` (F2: no token fallback); token/registry mismatch resolves
     from the registry.
   - **Non-dispatch id:** require positive Prime evidence — the owner-declared
     marker `.claude/session/active-session-role.json` recording a
     `prime-builder` session-stated role; absent/unreadable/`loyal-opposition`
     returns `False` (F3: no fail-open).
3. In `acquire()`, when `claim_kind == CLAIM_KIND_GO_IMPLEMENTATION` and not
   eligible, raise `WorkIntentRegistryError`. Guard scoped to `go_implementation`
   only; drafts, same-session re-acquire, prime, and registry-acting-prime
   acquisitions unaffected.

## Verification Plan (Specification-Derived)

**Role-eligibility tests (`platform_tests/scripts/test_work_intent_role_eligibility.py`,
on disk, already green — 8 passed):** LO dispatch rejected; prime dispatch
allowed; unknown harness id rejected (F2); registry-over-token (F2/d); UUID
without marker rejected (F3/a); UUID with prime marker allowed (F3/b); LO on
non-GO still draft; registry acting-prime allowed. Each asserts `acquire()`
raise-vs-return + `claim_status`.

**Timebox-regression repair (this revision's scope expansion):**

| Spec / criterion | Repair | Oracle |
|---|---|---|
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — no regression of the timebox suite | Update the 6 failing tests in `platform_tests/scripts/test_go_impl_claim_timebox.py` (the direct-registry assertions at lines ~62/83/105/122/139/181 and the CLI test `test_cli_claim_extend_status_reports_go_implementation_fields` using `CODEX_THREAD_ID`) to use Prime-eligible session ids — a dispatch-format `…-prime-builder-B-<hash>` id (resolving to prime-builder in the test registry) or a Prime marker — so `go_implementation` acquisition succeeds under the Prime-only contract while the tests still assert the timebox deadline/extension/grace behavior they were written to cover. | `python -m pytest platform_tests/scripts/test_go_impl_claim_timebox.py -q` green (8 passed) |

Verification commands (run before the re-filed implementation report):
`python -m ruff check` + `python -m ruff format --check` on all three
`target_paths` files; `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py platform_tests/scripts/test_go_impl_claim_timebox.py -q` (both suites green).

## Risk / Rollback

- **Risk: low.** The guard is additive and already verified; the timebox repair
  is mechanical test maintenance — updating session ids in existing assertions to
  reflect the corrected Prime-only contract, preserving the timebox
  deadline/extension/grace coverage. No production behavior beyond the guard
  changes.
- **Rollback:** revert the guard + helpers in
  `bridge_work_intent_registry.py`, the new test module, and the timebox-test
  session-id updates; no migration, no state change.

## Owner Decisions / Input

- **DELIB-20263200** (owner AUQ): WI-4534 Slice A authorization + the bounded
  PAUTH (`source` + `test_addition`; forbids dispatch-routing / cutover).
- **DELIB-20263205** (owner AUQ, Option A): authorized expanding scope to edit
  `platform_tests/scripts/test_go_impl_claim_timebox.py` and update its 6 failing
  timebox/CLI tests to Prime-eligible session ids; preserve the strict F3
  contract; Option B (relax F3) rejected.
- The PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
  is supplemented to cover existing-test modification of the timebox test per
  DELIB-20263205.

## Recommended Commit Type

`fix:` — repairs a defect (registry-authoritative role-eligibility guard) and the
spec-derived regression it surfaced in the timebox suite; no new user-facing
capability surface.
