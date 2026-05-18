NEW

# Data-Driven Cross-Harness Dispatch From invocation_surfaces (WI-3344)

bridge_kind: implementation_proposal
Document: gtkb-harness-data-driven-dispatch
Version: 001 (NEW; data-driven harness command construction from the harnesses registry)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC
Implements: REQ-HARNESS-REGISTRY-001 (FR8 invocation-surface dispatch); DELIB-2079 Q9
Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3344
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "scripts/seed_harness_registry.py", "groundtruth.db", "harness-state/harness-registry.json"]
Recommended commit type: feat:

## Claim

The cross-harness event-driven trigger (`scripts/cross_harness_bridge_trigger.py`) dispatches a counterpart AI coding harness when actionable bridge work appears. Harness role resolution is already data-driven from the role/identity records, but the *command construction* — how a harness is invoked as a subprocess — is hard-coded to a two-harness Claude/Codex topology in `_harness_command()` (lines 456-479): a literal `if command_handle == "codex" / elif == "claude"` switch. Any third harness returns `None` ("unknown_recipient") and cannot be dispatched.

This proposal makes command construction data-driven: the trigger reads each harness's `invocation_surfaces` from the DB-backed `harnesses` registry (surfaced through the generated `harness-state/harness-registry.json` projection) and builds the dispatch argv from it, with a fail-safe fallback to the existing switch when `invocation_surfaces` is absent. It also populates `invocation_surfaces` for the two existing harness records so the data-driven path is genuinely exercised rather than shipped as dead code. This is FR8 of REQ-HARNESS-REGISTRY-001 and operationalizes DELIB-2079 Q9 ("the cross-harness trigger dispatches harnesses data-driven from the registry's invocation_surfaces column ... no hard-coded per-harness branch"). It is the prerequisite that makes a third harness (Antigravity / Gemini CLI) dispatchable at all.

## Specification Links

- REQ-HARNESS-REGISTRY-001 — the harness registry requirement; FR8 governs invocation-surface dispatch (the requirement this implements).
- DELIB-2079 — owner-decided Antigravity Integration design; Q9 decided data-driven dispatch from `invocation_surfaces` with no hard-coded per-harness branch.
- DELIB-2080 — role-portability amendment (FR9); cross-harness dispatch must honor portable harness-assigned roles.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — the harness operating-mode architecture the registry and this dispatch change extend.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the cross-harness trigger is bridge dispatch infrastructure; `bridge/INDEX.md` remains canonical workflow state.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — verification is derived from the linked specifications and executed against the implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable artifact preservation (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across artifacts and tests (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — artifact lifecycle state transitions (advisory).

## Prior Deliberations

- DELIB-2079 — the owner-decided Antigravity Integration design. Q9 explicitly decided dispatch must be data-driven from `invocation_surfaces`, rejecting "hard-coded per-harness branch" and "interactive-only (no headless dispatch)". This proposal implements that decision.
- The cross-harness event-driven trigger replaced the retired smart poller (bridge thread `gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations`, VERIFIED). The trigger's actionable-signature scheme and dispatch-state contract are preserved unchanged by this proposal.
- WI-3337 (harnesses table schema, VERIFIED) created the `invocation_surfaces` column; WI-3338 (hot-path projection, VERIFIED) created the `harness-state/harness-registry.json` projection this proposal reads.

## Owner Decisions / Input

The Antigravity Integration project, including data-driven dispatch (DELIB-2079 Q9), was owner-decided via an 11-question AskUserQuestion clarification interview on 2026-05-16, recorded as DELIB-2079. The project is authorized under PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION (status active; scope: REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344). This proposal requires no new owner decision before GO; it implements an already-owner-decided requirement through the governed bridge path.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001 FR8 and DELIB-2079 Q9 fully govern this work. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a scoped code change to `scripts/cross_harness_bridge_trigger.py` plus two append-only `harnesses` registry record inserts and a projection regeneration. It is NOT a bulk standing-backlog operation: it does not resolve, retire, promote, batch-mutate, or produce an inventory of work items, and it requests no formal-artifact-approval packet for a bulk action. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` — which requires a bulk-operation inventory artifact, a review packet, and a deferred-decision marker, or an explicit owner-approval packet for the bulk action — is therefore not applicable to this proposal. The single work item cited (WI-3344) is this proposal's own implementing work item under the mandatory project-linkage metadata, not the target of a bulk mutation.

## Scope

### IP-1: Make _harness_command() data-driven

In `scripts/cross_harness_bridge_trigger.py`:
- Add an `invocation_surfaces: dict[str, str] | None` field to the `DispatchTarget` dataclass (~line 535).
- In `_resolve_dispatch_target()` (~line 637), after the harness ID is resolved, load `harness-state/harness-registry.json` via `harness_projection_reader.load_harness_projection()`, locate the record by `id == harness_id`, and attach its `invocation_surfaces` to the `DispatchTarget`.
- Rewrite `_harness_command()` (lines 456-479): when `target.invocation_surfaces` carries a `headless` entry, build the dispatch argv from it via template substitution of the prompt and project-root; otherwise fall back to the existing `codex`/`claude` switch. Preserve the current fail-closed `None` ("unknown_recipient") behavior when neither path yields a command.

### IP-2: Populate invocation_surfaces for the two existing harness records

`invocation_surfaces` is currently NULL for every seeded harness row. Populate it for the two existing harnesses (Claude, Codex) by inserting new append-only `harnesses` versions through the existing `db.insert_harness()` API, then regenerate the `harness-state/harness-registry.json` projection via `harness_projection.generate_harness_projection()`. The Antigravity harness record's `invocation_surfaces` is set when that harness is registered (WI-3348, separate thread).

### IP-3: Seed-path consistency

Update `scripts/seed_harness_registry.py` so the seed populates `invocation_surfaces` (it currently leaves it NULL), keeping fresh installs consistent with the live registry.

### IP-4: Regression tests

Extend `platform_tests/scripts/test_cross_harness_bridge_trigger.py`:
- Allow the test fixture to construct a three-harness projection.
- Assert `_harness_command()` builds a correct argv from a harness record's `invocation_surfaces`, including a non-Claude/Codex harness.
- Assert a NULL `invocation_surfaces` triggers the fallback switch.
- Assert an unknown harness with neither `invocation_surfaces` nor a known `command_handle` still returns `None`.

## Out Of Scope

- Registering the Antigravity harness record and setting its `invocation_surfaces` (WI-3348, separate thread).
- The `run_trigger()` two-recipient loop and `_compute_actionable()` two-tuple — Antigravity takes a *role* (loyal-opposition), not a third dispatch queue; the two-recipient (prime-builder / loyal-opposition) structure is unchanged.
- Migrating the trigger's role/identity readers to the projection (WI-3342 Slice B, separate thread — that thread touches `cross_harness_bridge_trigger.py`'s `_load_role_assignments` / `_load_harness_identities` raw readers at lines ~595-620; this proposal touches only `_harness_command()`, `_resolve_dispatch_target()`, and the `DispatchTarget` dataclass — disjoint functions in the same file).
- Changing the actionable-signature scheme, dispatch-state contract, or active-session suppression.
- Any file outside E:\GT-KB.

## Files Expected To Change

- `scripts/cross_harness_bridge_trigger.py` — data-driven `_harness_command()`, `DispatchTarget.invocation_surfaces`, projection lookup in `_resolve_dispatch_target()`.
- `scripts/seed_harness_registry.py` — seed `invocation_surfaces`.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — new regression coverage.
- `groundtruth.db` — new append-only `harnesses` versions carrying `invocation_surfaces` for the two existing harnesses.
- `harness-state/harness-registry.json` — regenerated projection.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 FR8 (invocation-surface dispatch) | Test: `_harness_command()` builds argv from `invocation_surfaces`; test that a third (non-Claude/Codex) harness record dispatches correctly. |
| DELIB-2079 Q9 (no hard-coded per-harness branch) | Test: the data-driven path produces a correct command without a per-harness `if/elif`; the fallback is exercised only on NULL `invocation_surfaces`. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | The trigger continues to read `bridge/INDEX.md` as canonical and preserves the dispatch-state contract — covered by the existing suppression/signature test suite still passing. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping plus the executed test commands and observed results. |

Implementation verification will run:
- `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `_harness_command()` builds the dispatch argv from `invocation_surfaces` with a fail-safe fallback.
- [ ] `invocation_surfaces` is populated for the two existing harness records and reflected in the regenerated projection.
- [ ] Regression tests cover data-driven dispatch, the NULL fallback, and the unknown-harness `None` case.
- [ ] The existing cross-harness-trigger test suite still passes (no regression to signatures, suppression, or dispatch-state).
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this draft before the live NEW INDEX entry is inserted:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-data-driven-dispatch --content-file .gtkb-state/bridge-drafts/gtkb-harness-data-driven-dispatch-001.md`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-data-driven-dispatch --content-file .gtkb-state/bridge-drafts/gtkb-harness-data-driven-dispatch-001.md`

Observed results (run against this draft, prior to INDEX insertion):

- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet_hash `sha256:7f779c63cbeee715cff5417e5575db576416f40937a9efc130bd5a0c0e922825`.
- Clause preflight: exit 0; `Blocking gaps (gate-failing): 0` across 5 must_apply clauses.

Both preflights are re-run against the indexed operative file after filing.

## Risk And Rollback

**Risk R1 (medium):** A malformed `invocation_surfaces` template could build a wrong argv and dispatch incorrectly. Mitigation: fail closed to `None` ("unknown_recipient") on any parse or substitution failure; the fallback switch covers the two known harnesses; tests assert both the success and failure paths.

**Risk R2 (low):** The regenerated projection could drift from the DB. Mitigation: the projection is produced by the existing `harness_projection.generate_harness_projection()`; no new projection logic is introduced.

**Risk R3 (low):** New append-only `harnesses` versions are created for the two existing harnesses. Mitigation: append-only versioning preserves history; rollback is a further corrective version, not a history rewrite.

Rollback: revert the `cross_harness_bridge_trigger.py` and `seed_harness_registry.py` changes; the `_harness_command()` switch fallback keeps the trigger working for Claude and Codex throughout the transition.

## Loyal Opposition Asks

1. Confirm the `invocation_surfaces` headless-template substitution shape is acceptable, or recommend an alternative encoding (for example, a structured argv list vs. a templated string).
2. Confirm that splitting the Antigravity harness-record registration and its `invocation_surfaces` value (WI-3348) out of this proposal is the correct scope boundary.
3. Confirm the fail-closed fallback to the existing `codex`/`claude` switch is the right safety posture for the transition window.
