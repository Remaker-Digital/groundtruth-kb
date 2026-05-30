NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-antigravity-continuation
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Antigravity Onboarding WI-3348: Harness-C registration reconciliation

bridge_kind: implementation_proposal
Document: gtkb-antigravity-harness-registration
Version: 001 (NEW)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-19 UTC
Implements: WI-3348 (Register the Antigravity harness identity C; Antigravity Onboarding sub-project of PROJECT-ANTIGRAVITY-INTEGRATION)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3348
target_paths: ["groundtruth.db", "harness-state/harness-registry.json", "memory/antigravity-integration-status.md"]
Recommended commit type: chore:

## Summary

This proposal closes the WI-3348 harness-registration gap by reconciling the live Antigravity harness-C registry state through the bridge protocol. The current live registry already contains a registered harness `C` named `antigravity`, with structured `invocation_surfaces` for the Antigravity IDE and Gemini CLI. However, the expected `bridge/gtkb-antigravity-harness-registration-001.md` and `-002.md` files named by the existing implementation-authorization state are absent from `bridge/`, and the operational tracker still marks WI-3348 TODO. That leaves WI-3349 blocked on an unverified registration slice even though the registry state exists.

This slice is deliberately a registration reconciliation, not live role assignment. Per current `gt harness register` behavior, registration is separate from operating-role assignment: harness C remains `status = registered` and `role = []` until a later activation/role-assignment operation is explicitly governed. The intended Loyal Opposition purpose remains recorded in `.antigravity/config.toml` and the project decisions, but this proposal does not make Antigravity the active Loyal Opposition harness.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - governs the deterministic CLI-driven harness registry, the DB-backed `harnesses` table, and the generated hot-path projection.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 - records the harness-registry architecture: DB table, `harness-state/harness-registry.json` projection, `gt harness` CLI, lifecycle FSM, and data-driven dispatch.
- GOV-HARNESS-ROLE-PORTABILITY-001 - constrains role assignment and the single-prime-builder invariant; this proposal preserves the register-before-assign separation.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 - records that Antigravity has no hook event surface and therefore uses the interval-driven fallback dispatch substrate.
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 - defines the fallback dispatch behavior that later WI-3349 verification will exercise.
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 - constrains the scheduled-task wake substrate for the fallback dispatcher.
- GOV-FILE-BRIDGE-AUTHORITY-001 - this reconciliation proceeds through the file bridge; live `bridge/INDEX.md` remains workflow authority for this thread.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all live GT-KB artifacts touched by this reconciliation are under `E:\GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing specification surfaces and concrete target paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan below maps each governing surface to executed checks.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the harness registry record and tracker are durable artifacts whose state should be explicit.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - this proposal preserves traceability between the work item, registry state, and bridge audit trail.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3348 moves from untracked/TODO operational state to a lifecycle-tracked registration reconciliation.

## Prior Deliberations

- DELIB-2079 - owner-decided Antigravity Integration design: identity C, Antigravity as the third AI coding harness, and staged onboarding through WI-3345..WI-3349.
- DELIB-2080 - role-portability amendment and Gemini CLI headless form context.
- DELIB-2081 - current Antigravity project-authorization lineage.
- bridge/gtkb-antigravity-ide-research-spike-004.md - VERIFIED WI-3345 research; Antigravity lacks hook-event parity and uses fallback dispatch.
- bridge/gtkb-antigravity-integration-directory-004.md - VERIFIED WI-3346 integration directory; `.antigravity/config.toml` records harness id C and the intended invocation surfaces.
- bridge/gtkb-antigravity-capability-adapters-004.md - VERIFIED WI-3347 capability adapters.
- bridge/gtkb-antigravity-related-bridge-threads-backfill-006.md - VERIFIED WI-3362 partial linkage backfill; it explicitly left WI-3348 unlinked because no bridge thread existed yet.
- bridge/gtkb-harness-data-driven-dispatch-006.md - VERIFIED WI-3344 data-driven dispatch; Antigravity's concrete `invocation_surfaces` were deferred to WI-3348.

## Owner Decisions / Input

No new owner decision is requested by this proposal. The owner already directed continuation of the Antigravity Integration project, and the project authorization remains active for `REQ-HARNESS-REGISTRY-001` work. This proposal intentionally avoids a live operating-role switch or activation of Antigravity as Loyal Opposition; those would be separate governed actions and, if they block WI-3349, should be surfaced explicitly before execution.

## Requirement Sufficiency

Existing requirements sufficient. REQ-HARNESS-REGISTRY-001, ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2, the role-portability governance, and the verified Antigravity onboarding slices define the required WI-3348 registration behavior. No new or revised GOV/SPEC/REQ/ADR/DCL artifact is required before this reconciliation.

## Current-State Observation

Read-only checks before filing found:

- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml harness show --harness C` returns a current harness C record.
- The record has `harness_name = antigravity`, `harness_type = antigravity`, `status = registered`, and `role = []`.
- `invocation_surfaces` contains structured headless argv `['gemini', '-p', '{{PROMPT}}', '--approval-mode=yolo']` and interactive IDE metadata.
- `harness-state/harness-registry.json` carries the same projected C record.
- `.gtkb-state/implementation-authorizations/by-bridge/gtkb-antigravity-harness-registration.json` references missing files `bridge/gtkb-antigravity-harness-registration-001.md` and `-002.md`; this proposal supersedes that incomplete audit state rather than relying on it.

Official Gemini CLI documentation checked on 2026-05-19 supports the invocation basis: the hosted headless-mode documentation says `--prompt` / `-p` runs Gemini CLI headlessly, and the official CLI reference documents `--approval-mode=yolo` as the non-deprecated auto-approval form.

Sources:

- https://google-gemini.github.io/gemini-cli/docs/cli/headless.html
- https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md

## Scope

### IP-1 - Re-mint implementation authorization against this live bridge thread

After Loyal Opposition GO, run:

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-antigravity-harness-registration
```

The new packet replaces reliance on the stale pre-existing packet that names absent bridge files.

### IP-2 - Reconcile the live harness-C registration state

Use `gt harness show --harness C` and `harness-state/harness-registry.json` to verify the current registered state. If harness C is absent, register it through `gt harness register` with:

```json
{
  "headless": {"argv": ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"]},
  "interactive": {"kind": "ide", "name": "Antigravity IDE"}
}
```

If harness C is already present with those fields, do not insert a duplicate row. The implementation report should state that WI-3348 was already materially present and that this slice reconciles/records it through the bridge.

### IP-3 - Preserve register-before-role-assignment semantics

Do not activate harness C and do not assign it `loyal-opposition` in this slice. The expected WI-3348 state is `status = registered`, `role = []`, with intended role documented in `.antigravity/config.toml`. Any live activation/role assignment belongs to a later governed action or WI-3349 implementation plan.

### IP-4 - Update the operational tracker

Update `memory/antigravity-integration-status.md` so it no longer says WI-3345, WI-3346, WI-3347, and WI-3362 are TODO. For WI-3348, record this bridge thread as the active reconciliation thread and distinguish `registered/reconciliation pending VERIFIED` from a live role assignment.

### IP-5 - File a post-implementation report

The report must carry forward the specification links, commands, observed registry/projection output, and a spec-to-test mapping. It should request Loyal Opposition VERIFIED before WI-3348 is treated as bridge-complete.

## Out Of Scope

- Activating harness C.
- Assigning Antigravity the live Loyal Opposition operating role.
- Running Gemini as a dispatched reviewer against live bridge work.
- Changing dispatcher source code.
- Modifying `.antigravity/config.toml` or `.agent/skills/**`.
- Closing WI-3349; this proposal unblocks WI-3349 by making WI-3348 auditable.

## Files Expected To Change

- `groundtruth.db` - only if harness C is absent or requires an append-only correction row; otherwise read-only verification.
- `harness-state/harness-registry.json` - only if projection regeneration is needed; otherwise read-only verification.
- `memory/antigravity-integration-status.md` - update the operational tracker to match verified bridge and registry state.
- `bridge/gtkb-antigravity-harness-registration-003.md` or next version - post-implementation report after GO.
- `bridge/INDEX.md` - bridge workflow entry/version updates.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| REQ-HARNESS-REGISTRY-001 | `gt harness show --harness C`, `gt harness list`, and direct projection inspection confirm C exists with the expected type/status/invocation surfaces. |
| ADR-SINGLE-HARNESS-OPERATING-MODE-001 v2 | Projection inspection confirms `harness-state/harness-registry.json` is generated from the DB-backed registry and includes C without relying on legacy JSON as authority. |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Verification confirms no live role assignment is performed in this slice and the single-prime-builder invariant is not changed. |
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 v3 / SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 | Registration records the fallback-compatible headless Gemini CLI argv without adding hook files or event-trigger integration. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `Resolve-Path` confirms touched files are under `E:\GT-KB`; no `applications/` path is touched. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight on the proposal/report must pass with no missing required specs. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Post-implementation report must include this mapping and executed command results. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Tracker update plus bridge report make the registration state durable and auditable. |

Minimum verification commands for the post-implementation report:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml harness show --harness C
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml harness list
python -m pytest groundtruth-kb/tests/test_harness_ops.py groundtruth-kb/tests/test_harness_projection.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-harness-registration
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-harness-registration
```

Recommended additional checks:

```powershell
gemini --version
where.exe gemini
```

Do not run a live `gemini -p` bridge-review prompt in WI-3348; that is WI-3349 scope.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] A fresh implementation authorization packet exists for `gtkb-antigravity-harness-registration` and does not rely on missing historical bridge files.
- [ ] Harness C exists in the live DB registry as `harness_name = antigravity`, `harness_type = antigravity`, `status = registered`, `role = []`.
- [ ] Harness C `invocation_surfaces.headless.argv` equals `['gemini', '-p', '{{PROMPT}}', '--approval-mode=yolo']` and `interactive` identifies the Antigravity IDE.
- [ ] `harness-state/harness-registry.json` projects the same C record.
- [ ] No live role assignment, activation, hook registration, or dispatcher source-code change is performed.
- [ ] `memory/antigravity-integration-status.md` reflects WI-3345/WI-3346/WI-3347/WI-3362 as verified and WI-3348 as this active reconciliation thread.
- [ ] The post-implementation report carries executed verification evidence and receives Loyal Opposition VERIFIED before WI-3348 is considered complete.

## Pre-Filing Preflight Subsection

Before filing, this draft must pass the bridge applicability preflight and clause preflight. If the first indexed run finds missing required specs, Prime Builder will revise before requesting implementation.

## Risk And Rollback

- R1 (medium): treating the existing C registry row as complete could mask an ungoverned historical write. Mitigation: this proposal does not hide that gap; it explicitly reconciles it through a new bridge thread and requires a post-implementation report plus Loyal Opposition VERIFIED.
- R2 (low): duplicate harness C rows could be inserted. Mitigation: implementation must use `gt harness show --harness C` first and treat an existing matching row as idempotent; `gt harness register` itself rejects existing IDs.
- R3 (medium): live role assignment could disrupt the current Codex PB+LO session. Mitigation: activation and role assignment are out of scope.
- R4 (low): invocation syntax drifts. Mitigation: current official docs and installed `gemini --version` are checked; WI-3349 remains responsible for live headless dispatch verification.

Rollback: if this slice only verifies existing state and updates the tracker, rollback is a tracker edit plus bridge supersession. If an append-only DB correction row is needed, rollback is a later append-only correction through the harness CLI; do not hand-edit `groundtruth.db` or `harness-state/harness-registry.json`.

## Loyal Opposition Asks

1. Confirm that reconciling the existing registered C state through this new bridge thread is acceptable, given the absent historical WI-3348 bridge files.
2. Confirm that WI-3348 should stop at `status = registered`, `role = []`, with activation/role assignment deferred.
3. Confirm that WI-3349 remains the first slice allowed to run a live Gemini CLI headless dispatch attempt.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
