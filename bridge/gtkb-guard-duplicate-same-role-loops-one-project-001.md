NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Guard duplicate same-role loops on one project

bridge_kind: prime_proposal
Document: gtkb-guard-duplicate-same-role-loops-one-project
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4378

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

Implementation proposal for a bounded code or platform change.

## Claim

There is no role+project concurrency guard against two concurrent same-role `/loop` automations selecting and working the same project. The existing coordination surfaces guard adjacent-but-different granularities: the work-intent registry (`scripts/bridge_work_intent_registry.py`) gates per *bridge thread* (`work_intent_claims.UNIQUE(thread_slug)`), and the per-role dispatch concurrency module (`scripts/bridge_dispatch_concurrency.py`) gates the *count* of in-flight workers per role. Neither prevents two same-role loops from independently picking the same project and each drafting/triaging its work items: per-thread claims only collide once both loops happen to target the identical thread slug, and the per-role count cap is satisfied as long as each loop holds a distinct slot. The result is correctness-safe (the per-thread claim still serializes the actual Write) but token-wasteful: redundant same-role loops repeatedly re-derive the same project context before colliding. This work item adds a cheap, deterministic role+project advisory guard so a redundant same-role loop can detect an active same-role claim on the same project and stand down (or switch work) before spending investigation tokens.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-AUTOMATION-VALUE-VS-COST-001` already establishes the governing principle that an expensive action (waking/continuing a harness into a full project investigation) must be gated behind a cheap deterministic check evaluated as value-vs-cost; this work operationalizes that principle at the role+project granularity. The guard is a deterministic read over the existing `work_intent_claims` store and introduces no new public behavior contract, no new owner-facing decision class, and no new/revised specification. No new or revised requirement is introduced.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the work-intent registry is bridge-coordination infrastructure; the guard must preserve the file-bridge authority model and must not let the new role+project check alter, bypass, or weaken per-thread claim correctness or the GO/VERIFIED protocol. This proposal and its implementation report will be filed as the next numbered bridge files under `bridge/` (e.g. `bridge/gtkb-guard-duplicate-same-role-loops-one-project-001.md`, `-002.md`, ...) with correct status tokens; the change is coordination-mechanism-only and the versioned bridge file chain remains canonical and append-only (no prior version is deleted or rewritten).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the guard reads durable claim artifacts (the `work_intent_claims` rows) rather than transient session state, keeping the coordination decision artifact-backed and auditable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each regression test from a cited spec clause and runs it against the implementation (mandatory spec-derived testing gate).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory project-linkage gate).
- `SPEC-AUQ-POLICY-ENGINE-001` - boundary citation: the role+project stand-down is fully deterministic and MUST NOT require owner AskUserQuestion; this change deliberately stays outside the AUQ policy surface (no owner-decision class is created), and the proposal confirms it does not invoke the AUQ engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform coordination module (`scripts/...`) and its platform test; no adopter/application surface is touched and no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4378 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES, surfaced via the canonical `work_items` authority.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the guard is exposed through the shared registry/CLI surface that BOTH the Claude and Codex `/loop` automations consume; the change keeps a single harness-neutral read path so neither harness gains a divergent guard behavior, preserving cross-harness parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the coordination decision is derived from the durable claim artifact graph (claims carry role + project), preserving traceability rather than relying on inferred in-memory state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the guard respects claim lifecycle state (expired / lapsed claims are ignored exactly as the existing readers do), so a stale same-role claim never strands a fresh loop.

## Prior Deliberations

- `DELIB-20264299` - gtkb-loop-multi-instance-coordinator-design-slice-1 (GO on REVISED-1) - directly on-topic prior design deliberation for coordinating multiple `/loop` instances; this WI is the concrete role+project stand-down primitive complementary to that coordinator design.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch that includes WI-4378.
- `DELIB-20263200` - authorization for the WI-4534 dispatch/claim role-eligibility fix (Slice A) - establishes the registry-authoritative role-resolution pattern (`_resolve_go_implementation_eligibility`) that this guard reuses for resolving the acting role of a claim.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the active non-fast-lane project authorization covering this PROJECT-GTKB-RELIABILITY-FIXES batch; WI-4378 is an active member (origin=improvement, component=bridge-dispatch) and is in-scope for bounded implementation under this authorization.
- `DELIB-20265457` - owner AUQ on 2026-06-21 directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items in this batch; this is the owner-decision evidence that authorizes the proposal/implementation of WI-4378.

## Proposed Scope

Minimal, additive change to the existing work-intent registry; no new module, no new substrate, no dispatcher rewrite.

1. In `scripts/bridge_work_intent_registry.py`, persist two additive, nullable columns on `work_intent_claims` — `acting_role` (the resolved Prime/LO role of the claiming session) and `project_id` (the project the claim's thread belongs to) — using the established `additive_columns` ALTER-on-missing pattern in `_ensure_schema` (so existing rows and databases upgrade transparently; the columns default to NULL and pre-existing readers are unaffected).
2. Populate the two columns inside `_claim_values` / `acquire`:
   - `acting_role`: resolved via the existing registry-authoritative resolver path used by `_resolve_go_implementation_eligibility` (dispatch-id harness → durable role-set; interactive → owner-declared marker). When the role cannot be resolved, store NULL (the guard then treats the claim as non-participating, fail-open for correctness — it never blocks).
   - `project_id`: resolved from the thread slug's project membership via the existing project-membership read path (reused read-only; no new MemBase write surface). When membership cannot be resolved, store NULL.
3. Add one read-only public function `same_role_project_holder(role, project_id, session_id, *, project_root=None) -> dict | None` that returns the active (non-expired, non-lapsed) `work_intent_claims` record held by a *different* session whose `acting_role == role` and `project_id == project_id`, or `None` when no such conflicting claim exists. It must reuse `_is_expired` / `_is_lapsed_go_implementation` so stale claims never count, and must return `None` (no conflict) when `role` or `project_id` is falsy/NULL (fail-open).
4. Expose the guard as a non-mutating advisory check on the existing `bridge_claim_cli.py` surface is OUT OF SCOPE for this slice (kept to the two declared target paths); the function is the deterministic primitive a `/loop` automation calls before drafting. CLI wiring, if desired, is a follow-on.

The guard is advisory and stand-down-only: it never deletes, overrides, or blocks another session's claim, and it never changes the allow/deny verdict of the per-thread `acquire` path. Correctness continues to rest on the existing `UNIQUE(thread_slug)` claim; this change only lets a redundant same-role loop notice the overlap earlier and cheaply.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` (cheap deterministic gate before expensive same-role spawn) — via `GOV-FILE-BRIDGE-AUTHORITY-001` coordination surface | `test_same_role_project_holder_detects_conflicting_same_role_claim` | When session A holds an active claim with `acting_role='prime-builder'`, `project_id='PROJECT-X'`, `same_role_project_holder('prime-builder', 'PROJECT-X', session_b)` returns A's record (a different same-role session is detected). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (guard must not weaken per-thread claim correctness) | `test_same_role_project_guard_does_not_alter_acquire_verdict` | `acquire` of a *different* thread slug still succeeds for session B even while A holds a same-role same-project claim on another thread (the guard is advisory; it does not block acquisition). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (expired/lapsed claims must not count) | `test_same_role_project_holder_ignores_expired_claim` | An expired (TTL-elapsed) same-role same-project claim is NOT returned by `same_role_project_holder` (stale claims never strand a fresh loop). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (different role does not collide) | `test_same_role_project_holder_ignores_different_role` | A claim with `acting_role='loyal-opposition'` on `PROJECT-X` is NOT returned when querying for `'prime-builder'` on `PROJECT-X` (role-scoped, not project-only). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (artifact-backed, fail-open on missing data) | `test_same_role_project_holder_returns_none_on_null_project_or_role` | `same_role_project_holder(role, None, ...)` and `same_role_project_holder(None, project_id, ...)` both return `None` (unresolvable role/project never produces a false stand-down). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (additive schema upgrade is transparent) | `test_work_intent_schema_upgrades_with_acting_role_and_project_columns` | Opening a registry whose `work_intent_claims` predates the new columns transparently adds `acting_role` and `project_id`, and `acquire` populates/reads them without error. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short`
- `python -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`
- `python -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py`

## Acceptance Criteria

1. `work_intent_claims` gains additive nullable `acting_role` and `project_id` columns via the existing ALTER-on-missing schema pattern; pre-existing rows/databases upgrade transparently and existing readers (`current_holder`, `claim_status`, `current_claimed_bridge_id`, `acquire`, `extend`, `release`) keep their current behavior.
2. `same_role_project_holder` returns a conflicting different-session same-role same-project claim, and returns `None` for: same session, different role, different project, expired/lapsed claims, and NULL/falsy role or project.
3. The guard is advisory only: it never blocks, deletes, or overrides any per-thread claim, and the allow/deny verdict of `acquire` is unchanged.
4. The six derived regression tests pass; `ruff check` and `ruff format --check` are clean on both changed files.

## Risks / Rollback

- Risk: over-eager stand-down strands a legitimate solo loop (false positive). Mitigation: the guard fails open — NULL/unresolvable role or project, expired/lapsed claims, and same-session claims all return `None`; the guard only fires on a confirmed active *different-session, same-role, same-project* claim.
- Risk: schema migration affects existing rows. Mitigation: columns are additive and nullable via the proven `additive_columns` ALTER-on-missing path already used for the GO-implementation columns; no backfill, no data rewrite, no UNIQUE change.
- Risk: role/project resolution cost on the hot path. Mitigation: resolution reuses existing readers and is only computed at claim-acquire time (already an I/O boundary); the guard read itself is a single indexed SELECT.
- Rollback: revert the additive columns, the populate lines, and the `same_role_project_holder` function plus its tests; the change is purely additive and fully reversible with no migration to undo (NULL columns left on existing rows are harmless if a partial revert occurs).

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## Recommended Commit Type

`fix`
