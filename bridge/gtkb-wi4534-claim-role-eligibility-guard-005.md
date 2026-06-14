NEW

bridge_kind: implementation_report
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 26c2349e-1cd0-4024-acef-f934b35fea4e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4534

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

# Implementation Report (BLOCKED — owner scope decision required) — WI-4534 Slice A

## Status Summary

The GO'd guard (`bridge/gtkb-wi4534-claim-role-eligibility-guard-004.md`) was
implemented **faithfully to the REVISED-003 design**, and the new test module
passes its full required matrix. **However, this report does NOT request
`VERIFIED`.** Faithful implementation of the approved F3 contract regresses 5
pre-existing tests in `platform_tests/scripts/test_go_impl_claim_timebox.py`,
which the GO requires remain green. The only fix is editing that timebox test
file, which is **outside the two GO'd `target_paths`**. This is a blocking
contradiction in the approved artifacts that requires an owner scope decision.

A non-interactive dispatched worker cannot AskUserQuestion; per the dispatch
worker contract I am recording the blocker here and stopping rather than
expanding scope unilaterally or weakening the F3 contract.

## Specification Links

Carried forward from the approved proposal
`bridge/gtkb-wi4534-claim-role-eligibility-guard-003.md`:

- **GOV-SESSION-ROLE-AUTHORITY-001** — durable-role authority; a
  `go_implementation` claim is an implementation-authority action and the guard
  resolves eligibility from the canonical registry, not a transient token.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the work-intent claim registry serves
  bridge coordination; the guard adds no `bridge/INDEX.md` write surface.
- **DCL-SESSION-ROLE-RESOLUTION-001** — deterministic role resolution via the
  stdlib-only `scripts/harness_projection_reader.py`.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this report cites
  every governing specification it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each new test has a real
  `acquire()` oracle (see Spec-to-Test Mapping).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — durable phased
  artifacts; blocker surfaced as a tracked artifact rather than chat.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — blocked-pending-owner
  lifecycle state handled explicitly.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision
  (DELIB-20263200), PAUTH, WI-4534, specs, and tests are linked and traceable.

## What Was Implemented (faithful to GO/-003)

In `scripts/bridge_work_intent_registry.py` (additive, scoped to the
`go_implementation` mint point in `acquire()`):

1. `DISPATCH_SESSION_ID_RE` — anchored regex parsing the cross-harness-trigger
   dispatch id `<compact-ISO8601>-<role>-<harness_id>-<6hex>`; captures the
   harness-id segment only (role token never authorizes).
2. `_dispatch_harness_id(session_id) -> str | None` — returns the parsed harness
   id, or `None` for non-dispatch (interactive / raw-UUID) ids.
3. `_resolve_go_implementation_eligibility(session_id, *, project_root) -> (bool, str)`
   and the thin `_go_implementation_eligible(...)` wrapper:
   - **Dispatch id (F2/F2d):** durable registry role-set via the stdlib-only
     `harness_projection_reader` (`load_harness_projection` + `role_set_for_id`);
     eligible iff it intersects `{prime-builder, acting-prime-builder}`. Unknown
     harness id → empty set → reject (no token fallback). Registry wins over the
     token.
   - **Non-dispatch id (F3):** read `.claude/session/active-session-role.json`;
     eligible iff `role == "prime-builder"`; absent / unreadable /
     `loyal-opposition` → reject (no fail-open).
4. `acquire()` raises `WorkIntentRegistryError` (CLI exit 3) when the computed
   claim is `go_implementation` and the session is not eligible. Draft (non-GO)
   claims are unaffected.

New test module `platform_tests/scripts/test_work_intent_role_eligibility.py`
(8 tests) covering the GO's full required matrix.

## Verification Results (run per the GO's Required Implementation Conditions)

| Command | Result |
|---|---|
| `python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q` | **8 passed** |
| `python -m pytest platform_tests/scripts/test_go_impl_claim_timebox.py -q` | **5 failed, 3 passed** (regression — see Blocker) |
| `python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py` | All checks passed |
| `python -m ruff format --check <both files>` | 2 files already formatted |

## Spec-to-Test Mapping (new module)

| Linked spec / criterion | Test | Result |
|---|---|---|
| GOV-SESSION-ROLE-AUTHORITY-001 — LO dispatch harness rejected | `test_go_impl_rejected_for_lo_dispatch_harness` | PASS |
| GOV-SESSION-ROLE-AUTHORITY-001 — prime dispatch harness allowed | `test_go_impl_allowed_for_prime_dispatch_harness` | PASS |
| F2 — unknown harness id rejected (no token fallback) | `test_go_impl_rejected_for_unknown_harness_id` | PASS |
| F2/d — registry authoritative over token | `test_go_impl_resolves_from_registry_not_token` | PASS |
| F3/a — LO UUID session without Prime marker rejected | `test_go_impl_rejected_for_uuid_session_without_prime_marker` | PASS |
| F3/b — owner-declared interactive Prime accepted | `test_go_impl_allowed_for_uuid_session_with_prime_marker` | PASS |
| Guard scoped to go_implementation only | `test_draft_claim_unaffected_for_lo_harness_on_non_go_thread` | PASS |
| acting-prime-builder registry compat | `test_go_impl_allowed_for_registry_acting_prime_builder` | PASS |

## Blocker — Approved Design vs. "timebox green" are contradictory

**Finding.** The 5 failing timebox tests acquire a `go_implementation` claim on a
GO-latest thread with **bare, non-dispatch session ids** (`"session-a"`,
`"session-b"`) and **no session-role marker**. The approved F3 contract
(REVISED-003: "non-dispatch ids require positive Prime evidence — the marker;
absent → reject; no fail-open") therefore rejects them.

- Failing: `test_go_claim_records_deadline_and_non_go_keeps_draft_ttl`,
  `test_extend_adds_fixed_increment_and_refuses_past_total_hold_cap`,
  `test_lapsed_go_claim_releases_for_takeover_after_grace`,
  `test_report_latest_status_stops_lapsed_go_claim_detection`,
  `test_doctor_warns_on_lapsed_go_implementation_claim`.

**Why no in-scope design resolves it.** The `(non-dispatch id, no marker)` input
is the *same class* that the GO-required F3/a test demands be **rejected**. The
timebox tests demand the **opposite** outcome (acquire) for that identical class.
No single guard behavior satisfies both:
- "non-dispatch + no marker → allow" keeps timebox green but **fails F3/a** and
  re-opens the exact fail-open the `-002` NO-GO rejected.
- "non-dispatch + no marker → reject" satisfies F3/a (approved design) but
  **regresses timebox**.

Resolving via the current process's durable harness role also fails: the timebox
tests run with `project_root=tmp_path`, which has no `harness-identities.json`,
so current-harness resolution cannot return a Prime role there.

**The only working fix** is to update the 5 timebox tests' session ids from
`"session-a"`/`"session-b"` to dispatch-prime form (e.g.,
`"2026-06-13T...-prime-builder-B-<6hex>"`). The autouse conftest fixture
`platform_tests/scripts/conftest.py::mock_harness_registry_for_tests` already
points `GTKB_HARNESS_REGISTRY_PATH` at the real registry for that module, so a
dispatch-prime id resolves to `prime-builder` and the claim succeeds —
**preserving every timebox assertion and the timebox behavior** (deadline,
extension, lapse, doctor warning). This is test-maintenance accompanying a
deliberate behavior change, not a behavior regression.

But `platform_tests/scripts/test_go_impl_claim_timebox.py` is **not in the two
GO'd `target_paths`**, and the GO explicitly states "keep implementation scoped
to the two declared target paths." Editing a third file (and whether modifying
an existing test exceeds the PAUTH's `test_addition` class) is an owner scope
decision, not a Prime Builder discretion call.

## Owner Decisions / Input

This report depends on an owner decision and cannot be `VERIFIED` until it is
resolved. **Required owner decision (AskUserQuestion in the next interactive
session):**

- **Option A (recommended):** Expand the WI-4534 Slice A scope/`target_paths`
  (and confirm the PAUTH permits modifying the existing timebox test) to include
  `platform_tests/scripts/test_go_impl_claim_timebox.py`, then update its 5
  failing tests' session ids to dispatch-prime form. Smallest change; preserves
  all timebox behavior and the approved F3 contract.
- **Option B:** Revise the F3 design (e.g., a documented, owner-accepted
  fail-open for non-dispatch non-UUID ids) — re-opens part of the `-002` NO-GO
  concern; not recommended.

Prior durable owner evidence for the slice itself: **DELIB-20263200** (owner AUQ
authorizing WI-4534 Slice A + the bounded PAUTH). That authorization scoped to
two paths and `source + test_addition`; it does not by itself authorize editing
the existing timebox test. No further owner decision was anticipated by the
proposal, which is precisely the gap surfaced here.

## State Left Behind (no commit, no MemBase mutation)

- `scripts/bridge_work_intent_registry.py` — guard implemented (ruff-clean).
- `platform_tests/scripts/test_work_intent_role_eligibility.py` — 8 tests, all pass.
- Not committed; WI-4534 not resolved in MemBase. Work-intent claim held by this
  dispatched session (deadline 2026-06-13T22:49:33Z).
- No file outside the two `target_paths` was modified.

## Recommended Commit Type

`fix:` — once unblocked (defect repair in the work-intent claim registry +
regression tests; the accompanying timebox session-id update is test maintenance
for the same behavior change).
