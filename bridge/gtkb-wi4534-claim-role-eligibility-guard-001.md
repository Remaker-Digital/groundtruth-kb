NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4534-claim-role-eligibility-guard
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dfc088ac-2d2c-4b3e-8117-6e5ed57469e8
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4534
target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]

# Implementation Proposal — WI-4534 Slice A: Role-Eligibility Guard on go_implementation Claim Acquisition

## Summary

WI-4534 is a P2 bridge-dispatch defect: a loyal-opposition-role harness can
acquire a `go_implementation` work-intent claim on a GO-latest bridge thread,
blocking the Prime Builder implementer. It was observed twice this session
blocking the owner-authorized TAFE cutover (WI-4508): sessions
`2026-06-13T19-13-44Z-loyal-opposition-D-54f7e1` and
`2026-06-13T20-07-29Z-loyal-opposition-D-20c71a` each held `go_implementation`
claims on `gtkb-tafe-dual-write-index-parity` while harness D (ollama) is
`loyal-opposition` per the canonical registry.

**Root cause (confirmed in code):** `bridge_work_intent_registry._claim_values()`
sets `claim_kind = CLAIM_KIND_GO_IMPLEMENTATION` solely when
`_latest_status(slug) == "GO"` (lines ~247-263). `acquire()` performs no check
of the acquiring harness's role. So *any* session acquiring a claim on a
GO-latest thread is granted a go_implementation claim, regardless of whether its
harness is eligible to implement.

**Slice A (this proposal):** add a role-eligibility guard at the
go_implementation mint point. This is the defensive floor — it rejects the
ineligible claim at acquisition regardless of how the session was dispatched.

**Part 2 (deferred per PAUTH; NOT in this proposal):** route GO-event dispatch
to prime-builder harnesses only (in the cross-harness trigger / dispatcher) so
ineligible harnesses are never dispatched to implement in the first place. This
is the upstream complement; it carries more concurrency-sensitive design and is
explicitly excluded from this slice's PAUTH.

## Specification Links

- **GOV-SESSION-ROLE-AUTHORITY-001** — durable-role authority: headless dispatch
  and implementation authority are keyed to the durable role. A
  `go_implementation` claim is an implementation-authority action; this guard
  enforces that it is held only by a `prime-builder`-role harness.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — the work-intent claim registry serves
  bridge coordination; the guard preserves canonical bridge state and only
  constrains who may hold an implementation claim. No canonical INDEX write
  surface is added.
- **DCL-SESSION-ROLE-RESOLUTION-001** — deterministic role resolution; the guard
  resolves the acquiring harness's durable role via the canonical registry
  reader rather than ad-hoc parsing of role authority.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing spec it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every named test below
  has a real oracle.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`; no application/adopter surface is touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — the fix is delivered as
  durable, tracked, phased artifacts (Slice A guard + tests; Part 2 deferred to
  its own slice).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — deferred (Part 2) and
  captured-defect (WI-4534) lifecycle states are handled explicitly.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision
  (DELIB-20263200), PAUTH, work item (WI-4534), spec, and test artifacts are
  linked and traceable.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SESSION-ROLE-AUTHORITY-001 (durable-role
authority) and WI-4534 govern this work; no new or revised requirement is needed
for Slice A. (Part 2 dispatch-routing may warrant a DCL clarification before its
own slice, but that is out of scope here.)

## Prior Deliberations

- **DELIB-20263200** — owner AUQ (2026-06-13) authorizing this WI-4534 Slice A
  fix and the bounded PAUTH.
- **WI-4534** — the defect candidate captured this session (`gt backlog add`),
  with the recurring-claim evidence.
- **DELIB-20263195** — the TAFE cutover authorization (the work this defect was
  blocking).
- Related dispatch-reliability items: WI-4479 (headless dispatch crash),
  WI-4520 (Antigravity LO hallucination), WI-4396 (lease contention in dispatch
  logs).

_Deliberation search note: no prior deliberation proposes a role-eligibility
guard on work-intent claim acquisition; this is the first treatment of the
claim-kind/role mismatch._

## Design (Slice A)

In `scripts/bridge_work_intent_registry.py`:

1. New helper `_acquiring_harness_role_set(session_id, *, project_root) -> frozenset[str] | None`:
   - Parse the dispatcher-generated session-id format, which encodes role +
     harness id: `<timestamp>-<role>-<harness_id>-<hash>` (e.g.,
     `2026-06-13T20-07-29Z-loyal-opposition-D-20c71a`). A regex anchored at the
     end captures `-(prime-builder|loyal-opposition|acting-prime-builder)-(<harness_id>)-(<hash>)`.
   - Resolve the parsed `harness_id`'s **durable** role set from the canonical
     registry via the stdlib-only reader `scripts/harness_projection_reader.py`
     (the DB-independent counterpart to `groundtruth_kb.harness_projection`,
     hook-safe — no heavy imports). Return the role token set.
   - When the parsed harness id is not found in the registry, fall back to the
     role token parsed from the session id (still distinguishes prime vs LO).
   - Return `None` when the session id does not match the dispatched format
     (e.g., an interactive raw-UUID session) — un-resolvable.
2. In `acquire()`, after computing `values` (or inside `_claim_values`), when
   `values["claim_kind"] == CLAIM_KIND_GO_IMPLEMENTATION`:
   - Resolve `_acquiring_harness_role_set(session_id, project_root=project_root)`.
   - If the role set is non-`None` AND contains neither `prime-builder` nor the
     compat `acting-prime-builder`: raise `WorkIntentRegistryError` with a clear
     message (`"go_implementation claim requires a prime-builder harness; session <id> resolves to role-set <roles>"`).
     The CLI maps this to exit 3 (`ERROR: ...`).
   - If the role set is `None` (un-resolvable interactive id): proceed
     (fail-open). Interactive owner-Prime sessions are the legitimate
     go_implementation actors; the defect class is dispatched non-prime harnesses
     whose ids encode the role.
3. The guard is scoped to `go_implementation` only. Draft claims (non-GO
   threads) are unaffected. Existing valid claims, same-session re-acquisition,
   and prime-builder acquisitions are unaffected.

Considered alternative (noted, not chosen for Slice A): reading
`GTKB_BRIDGE_DISPATCH_KEYWORD` env (pb/lo) as the role signal. Rejected as the
primary mechanism because the session id is the value already passed to
`acquire()` and reliably encodes the dispatched role/harness, whereas env
presence varies by dispatch path; the registry lookup is also more authoritative
than the dispatcher's keyword label.

## Verification Plan (Specification-Derived)

New tests in `platform_tests/scripts/test_work_intent_role_eligibility.py`, each
using an isolated `project_root` fixture (test `harness-registry.json` with
harnesses B=prime-builder, D=loyal-opposition; a test `bridge/INDEX.md` with one
GO-latest thread and one NEW-latest thread; `groundtruth.db` auto-created by
`_ensure_schema`). Pattern mirrors `platform_tests/scripts/test_go_impl_claim_timebox.py`.

| Spec / Acceptance criterion | Test | Oracle / Method |
|---|---|---|
| GOV-SESSION-ROLE-AUTHORITY-001 — LO harness cannot hold go_implementation | `test_go_impl_claim_rejected_for_lo_harness_session` | session id `...-loyal-opposition-D-<hash>` on GO-latest thread -> `acquire()` raises `WorkIntentRegistryError`; no row inserted |
| GOV-SESSION-ROLE-AUTHORITY-001 — prime harness may hold go_implementation | `test_go_impl_claim_allowed_for_prime_harness_session` | session id `...-prime-builder-B-<hash>` on GO-latest -> acquired; `claim_status` shows `claim_kind=go_implementation` |
| Interactive owner-Prime fail-open | `test_go_impl_claim_allowed_for_interactive_uuid_session` | raw-UUID session id on GO-latest -> acquired (un-resolvable role -> allow) |
| Guard scoped to go_implementation only | `test_draft_claim_unaffected_for_lo_harness_on_non_go_thread` | `...-loyal-opposition-D-<hash>` on NEW-latest thread -> acquired as `draft` |
| DCL-SESSION-ROLE-RESOLUTION-001 — registry-authoritative resolution | `test_role_resolved_from_registry_not_token` | registry says harness D=loyal-opposition; session token says D -> rejection cites registry role |
| acting-prime-builder compat | `test_acting_prime_builder_session_allowed` | `...-acting-prime-builder-A-<hash>` on GO-latest -> acquired (compat maps to prime authority) |

Pre-file code-quality gates (before the implementation report): `python -m ruff
check` + `python -m ruff format --check` on both changed files; `python -m pytest
platform_tests/scripts/test_work_intent_role_eligibility.py -q`. The existing
`platform_tests/scripts/test_go_impl_claim_timebox.py` must remain green (no
regression to the timebox behavior).

## Risk / Rollback

- **Risk:** low-moderate. The claim registry is concurrency-hot, but the change
  is additive and scoped: it only *rejects* new `go_implementation` acquisitions
  by resolved-non-prime harnesses and fail-opens for everything else (drafts,
  prime acquisitions, un-resolvable interactive ids, same-session re-acquire).
  No existing claim is invalidated; no schema change.
- **Failure mode considered:** if role resolution mis-identifies a legitimate
  prime acquisition as non-prime, it would wrongly reject. Mitigated by
  fail-open on un-resolvable ids and by the test matrix covering prime/LO/interactive/compat.
- **Rollback:** revert the guard + helper in `bridge_work_intent_registry.py`
  and delete the new test file; no migration, no state change.

## Owner Decisions / Input

- **DELIB-20263200** (owner AUQ, 2026-06-13): owner selected "Fix WI-4534
  claim-role defect", authorizing this Slice A and the bounded PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A`
  (active; allows `source` + `test_addition`; forbids GO-event dispatch routing
  changes and cutover/canonical-bridge-state writes — Part 2 deferred).
- AUQ id `AUQ-2026-06-13-WI4534-FIX`, answer "Fix WI-4534 claim-role defect".
- No further owner decision is required for Slice A.

## Recommended Commit Type

`fix:` — repairs a defect (role-eligibility guard) in the work-intent claim
registry with no new user-facing capability surface; adds a regression test.
