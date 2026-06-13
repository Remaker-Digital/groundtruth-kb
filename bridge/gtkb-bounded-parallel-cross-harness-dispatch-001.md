NEW

# Bounded Parallel Cross-Harness Auto-Dispatch (supersede binary same-role active-session suppression)

bridge_kind: implementation_proposal
Document: gtkb-bounded-parallel-cross-harness-dispatch
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7a2ca6a2-1229-4ff9-984e-a5b9c6e88177
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive; Prime Builder (session-stated ::init gtkb pb; durable role prime-builder)

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-CA9165

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement SPEC-INTAKE-ca9165. Today the cross-harness event-driven trigger
suppresses auto-spawning a headless worker of a role whenever a session of that
role already has a fresh active-session heartbeat lock. The predicate is
`check_target_active()` (`scripts/cross_harness_bridge_trigger.py:2246`), and the
binary 0-or-1 contract it enforces is the design constraint
`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`. That binary suppression blocks
multiple same-role headless workers from progressing **different** bridge items
in parallel — the exact throughput ceiling visible in the current swarm, where
several Prime sessions serialize behind one another.

This proposal supersedes the binary same-role suppression with a **bounded
per-role concurrency cap**: at the `run_trigger()` dispatch decision, instead of
"suppress if any same-role session is active", count the live dispatched headless
workers **of that role** and allow a new spawn while that count is below a
per-role cap (`GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`, conservative default 2,
env-overridable). Multiple same-role workers may then run concurrently on
distinct items.

The collision-safety preconditions the spec requires are already in place:

- **Per-item ownership lock** — `SPEC-INTAKE-9cb2ee` (claim-gated
  implementation-start) is verified implemented this session: both
  `implementation_authorization.py begin` and the `implementation_start_gate`
  hook refuse protected target-path mutation unless the session holds the active
  GO-implementation work-intent claim. So exactly one claim-holding session owns
  a given GO'd thread's implementation; parallel workers cannot collide on the
  same item's source.
- **Global blast-radius cap** — the existing `MAX_LIVE_DISPATCHED_PROCESSES`
  global cap (WI-4472, `cross_harness_bridge_trigger.py:2360`, default 8) is
  retained unchanged; per-role headroom never exceeds it.
- **Per-item dispatch dedup** — the actionable-signature dispatch-state dedup
  ensures no two workers target the same bridge item; dispatch stays
  event-driven on actionable-signature change (never blind interval polling —
  the S308 token-waste lesson).
- **Fail-closed fallback** — if per-role counting errors, the trigger falls back
  to the conservative suppress-on-active behavior (fail closed, never
  over-spawn).

`check_target_active()` is retained as a helper (the heartbeat-lock reader is
still used for fallback and for the per-role accounting); the change is at its
`run_trigger()` decision site, which moves from binary suppression to the
bounded per-role cap and emits a distinct `per_role_cap_reached` dispatch result
(separate from the legacy `active_session_suppressed`).

## Coupled Formal-Artifact Action (DCL supersession — implement-time, owner-gated)

`DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` encodes the binary single-active-per-role
contract this proposal relaxes. The code change and the DCL supersession MUST
land together to avoid an assertion/behavior contradiction. Because a DCL
supersession is a formal-artifact MemBase mutation, it is **out of this
proposal's `target_paths`** and is handled at implement-time via:

1. a `GOV-ARTIFACT-APPROVAL-001` formal-artifact approval packet (owner-visible
   content + owner approval) for the superseding `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
   version; and
2. a one-line amendment to PAUTH `…-22C078-9CB2EE-CA9165` adding a spec-mutation
   allowed-class (current allowed-mutations: source, test, narrative_artifact),
   citing the existing owner authorization `DELIB-20263189`.

The implementation report will carry both the code/test evidence AND the DCL
supersession packet evidence; `VERIFIED` is contingent on the superseded DCL's
assertions matching the new bounded-concurrency behavior. This proposal seeks
LO `GO` on the design + the code/test scope; it does not itself mutate the DCL.

## Specification Links

- `SPEC-INTAKE-ca9165` — the governing requirement: supersede binary same-role
  active-session suppression with bounded parallel cross-harness auto-dispatch.
  This proposal implements it.
- `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` — the design constraint encoding the
  binary suppression; this proposal supersedes it (coupled formal-artifact
  action above).
- `SPEC-INTAKE-9cb2ee` — claim-gated implementation-start (verified implemented
  this session); the per-item ownership lock that makes bounded parallelism
  collision-safe. Prerequisite — now satisfied.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity: dispatch automation serves
  the bridge and must not degrade it; `bridge/INDEX.md` remains canonical and the
  change is dispatch-mechanism-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specs (this list).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/WI/PAUTH metadata
  is in the header block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  maps each linked spec to a derived test.
- `GOV-STANDING-BACKLOG-001` — `WI-AUTO-SPEC-INTAKE-CA9165` is the governed
  backlog item, admitted to `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` and
  covered by the cited PAUTH.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — this proposal preserves
  the artifact graph: WI-AUTO-SPEC-INTAKE-CA9165 → DELIB-20263189 → PAUTH →
  this proposal → derived tests → VERIFIED, with the coupled DCL supersession
  linked; no behavior added outside the graph.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — originated through
  artifact-oriented governance: owner AUQ → DELIB-20263189 → PAUTH → bridge
  proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — participates in the bridge
  thread lifecycle (NEW → GO → report → VERIFIED) and emits a new
  dispatch-result lifecycle state (`per_role_cap_reached`) distinct from
  `active_session_suppressed`.

## Prior Deliberations

- `INTAKE-2ce995f2` — the ca9165 intake (confirmed → `SPEC-INTAKE-ca9165`); the
  source requirement text this proposal implements verbatim, including the named
  safeguards (global cap, per-item claim dedup, actionable-signature dedup,
  event-driven).
- `DELIB-20263189` — owner AUQ authorization (2026-06-13) for the 3 P1 dispatch
  specs and the "ca9165 first" sequencing; the direct authorization basis for
  this proposal under the cited PAUTH.
- `INTAKE-b4928376` — sibling intake `SPEC-INTAKE-22c078` (harness-agnostic
  review eligibility), the next item in this workstream; related dispatch-role
  concern but distinct (eligibility vs. concurrency). No overlap in scope.
- `INTAKE-a815f782` — per-document lease intake; complementary per-item dedup
  framing. This proposal relies on the existing actionable-signature + work-intent
  claim dedup rather than introducing a new per-document lease.

## Owner Decisions / Input

This proposal depends on owner approval. Authorizing evidence:

- `DELIB-20263189` (AskUserQuestion, 2026-06-13, this session): owner selected
  "Authorize 3 P1 dispatch specs," then "ca9165 first, then 22c078," authorizing
  implementation of `SPEC-INTAKE-ca9165` under PAUTH
  `…-22C078-9CB2EE-CA9165`. Recorded via the governed deliberation path
  (`presented_to_user=true`, `approved_by=owner`, `outcome=owner_decision`).
- `SPEC-INTAKE-ca9165` is owner-confirmed (intake `INTAKE-2ce995f2`,
  `intake_status=confirmed`, `outcome=owner_decision`).

A further owner gate remains at implement-time (NOT required to file this
proposal or for LO review): the `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
supersession requires a `GOV-ARTIFACT-APPROVAL-001` formal-artifact approval
packet with owner-visible content, per the Coupled Formal-Artifact Action
section.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-ca9165` defines the required
behavior (bounded per-role concurrency superseding binary suppression) and names
the safeguards; `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` is the constraint to
supersede; the global cap (WI-4472) and the claim-ownership lock
(`SPEC-INTAKE-9cb2ee`, verified) are existing, in-place safeguards. No new or
revised requirement is needed before implementation. The superseding DCL content
is a derived artifact authored during implementation under an owner-approved
formal-artifact packet, not a new requirement.

## Spec-Derived Verification Plan

New pytests in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`,
plus the code-quality gates and the mandatory bridge preflights. Verification
interpreter: the project's uv-managed dev environment (the bare venv lacks
pytest; `uv run --extra dev` provides pytest 9.0.3).

| Linked spec | Derived test / verification | Expected result |
|---|---|---|
| `SPEC-INTAKE-ca9165` (bounded per-role concurrency replaces binary suppression) | `test_bounded_per_role_allows_parallel_same_role_dispatch`: with a fresh same-role active-session lock present AND per-role live count below the per-role cap, `run_trigger()` dispatches a worker for a DIFFERENT actionable item. | spawn occurs; result is NOT `active_session_suppressed`. |
| `SPEC-INTAKE-ca9165` (per-role cap bounds concurrency) | `test_per_role_cap_suppresses_at_limit`: when per-role live count ≥ `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`, no additional same-role spawn occurs; a distinct `per_role_cap_reached` result is recorded. | no spawn; result `per_role_cap_reached`. |
| `WI-4472` global cap retained | `test_global_cap_still_enforced`: when global live count ≥ `MAX_LIVE_DISPATCHED_PROCESSES`, no spawn regardless of per-role headroom. | no spawn (existing behavior preserved). |
| `SPEC-INTAKE-9cb2ee` per-item dedup safety | `test_same_item_not_double_dispatched`: under bounded parallelism, the actionable-signature dispatch-state dedup prevents two workers targeting the same item. | second same-item dispatch suppressed by signature dedup. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (regression + quality) | full `test_cross_harness_bridge_trigger.py` suite; `ruff check` and `ruff format --check` on changed files. | all green. |

Test execution command (from `groundtruth-kb/`):

```text
uv run --extra dev pytest ../platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --no-header
```

The implementation report will also include the two mandatory bridge preflights
(`bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`) for this
bridge id.

## Risk / Rollback

**Risk surface.** Hot-path change to the cross-harness dispatch concurrency
control: relaxing same-role suppression increases the number of concurrent
same-role headless workers. Mitigations:

- Global cap `MAX_LIVE_DISPATCHED_PROCESSES` (default 8) is unchanged and bounds
  total live dispatched processes.
- New per-role cap (`GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`, conservative default 2)
  bounds same-role concurrency; the cap is env-overridable for tuning.
- Per-item dedup (work-intent claim as authoritative ownership lock per
  `SPEC-INTAKE-9cb2ee`, plus actionable-signature dispatch-state) prevents two
  workers on the same item.
- Dispatch remains event-driven on actionable-signature change (no blind
  interval polling — S308 lesson).
- Fail-closed: on any error computing the per-role live count, the trigger falls
  back to the conservative binary suppression (never over-spawns).

**Rollback.** Single-commit revert of `scripts/cross_harness_bridge_trigger.py`
and the new tests, plus restoring `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` to
its pre-supersession version (the code + DCL are committed together). No schema,
MemBase-table, or on-disk-state migration; no new runtime dependency.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-bounded-parallel-cross-harness-dispatch` document list in
`bridge/INDEX.md`; no prior version is deleted or rewritten (append-only).
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — net-new bounded per-role concurrency dispatch behavior plus a new
`per_role_cap_reached` dispatch result and new tests; supersedes a design
constraint rather than refactoring existing behavior, and is not a bug fix.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
