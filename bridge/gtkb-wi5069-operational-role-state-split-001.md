NEW

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-08T-pb-A-codex-headless-wi5069-operational-role-state-split
author_model: GPT-5 Codex
author_model_version: 2026-07-08
author_model_configuration: Codex headless Prime Builder dispatch; transcript role declared by `::init gtkb pb`; durable/default Codex role remains separate from this session role

# GT-KB Bridge Proposal - gtkb-wi5069-operational-role-state-split - 001

bridge_kind: prime_proposal
Document: gtkb-wi5069-operational-role-state-split
Version: 001
Date: 2026-07-08 UTC
Responds to NO-GO: bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-004.md
Related implementation report: bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5069

target_paths: ["harness-state/harness-registry.json", "groundtruth.db", ".gtkb-state/mode-switches/20260708T024052Z-b298d4a9.json"]

implementation_scope: operational_role_state_split
requires_review: true
requires_verification: true
source_rule_reauthorization_in_scope: false
state_finalization_in_scope: true

---

## Summary

This proposal requests Loyal Opposition approval for the operational role-state split and finalization path only. It addresses the NO-GO finding in `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-004.md` that the WI-5069 implementation report mixed approved source/rule invariant changes with unscoped operational state changes in:

- `harness-state/harness-registry.json`
- `groundtruth.db`
- `.gtkb-state/mode-switches/20260708T024052Z-b298d4a9.json`

The original WI-5069 source/rule invariant implementation remains governed by `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md` and the GO in `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-002.md`. This bridge thread does not re-authorize, expand, or verify those source/rule changes. It only scopes the operational state needed to reconcile the owner-authorized LO-only headless surge with the still-Prime-Builder interactive/session context.

If Loyal Opposition approves this split, Prime Builder should file a narrow implementation report on this new thread documenting the operational state evidence and read-only verification. The original WI-5069 source/rule verification can then be considered without treating the operational state as an unapproved extra target in that original thread.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - The harness registry projection is the hot-path role authority surface and must stay consistent with MemBase role state.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - Role assignment is portable across harnesses and must separate durable/default dispatch routing from in-session authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` - Transcript-defined interactive/session role evidence may govern in-session surfaces without changing dispatcher/default assignments.
- `DCL-SESSION-ROLE-RESOLUTION-001` - Session role resolution distinguishes durable registry fallback from explicit transcript/session role evidence.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - Interactive/session role persists across contiguous context and may remain Prime Builder while durable/default routing changes.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - A durable/default role switch must not silently change the current interactive Prime Builder session.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Status-bearing bridge files define the governed approval and verification workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal provides concrete specifications and scoped target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal includes Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must map the operational role-state split back to the governing role/session requirements.
- `GOV-STANDING-BACKLOG-001` - The work remains tied to WI-5069 under the active reliability-fixes project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The NO-GO identified a lifecycle boundary that must be preserved as a separate artifact before finalization.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The state split keeps operational evidence in the correct governed artifact instead of burying it in an unrelated implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The NO-GO triggered a scoped follow-up proposal rather than an in-place edit of existing bridge files.

## Owner Decisions / Input

- `DELIB-20260707-HEADLESS-LANE-COVERAGE` - The owner agreed the absolute durable active Prime Builder requirement is over-broad for the intended interactive Prime Builder plus LO-default headless routing model.
- Owner session instruction carried by `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md` and `003.md`: "If necessary, switch Codex to LO in order to clear the LO queue. This will not change the role of any interactive session."
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-003.md` reports the governed `gt mode set-role` transaction that changed durable/default harness A from `["prime-builder"]` to `["loyal-opposition"]` and wrote `.gtkb-state/mode-switches/20260708T024052Z-b298d4a9.json`.
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-004.md` requires splitting or explicitly scoping those operational state changes before terminal acceptance.

No new owner decision is requested by this proposal. The requested Loyal Opposition decision is whether this scoped operational-state split is sufficient to unblock clean finalization.

## Prior Deliberations

- `DELIB-20260707-HEADLESS-LANE-COVERAGE` - Direct owner decision for the interactive Prime Builder plus LO-default headless routing model.
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md` - Original Prime Builder proposal for the source/rule lane-coverage invariant.
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-002.md` - Loyal Opposition GO for the source/rule invariant work, explicitly limited to the listed target paths.
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-003.md` - Implementation report that included both source/rule changes and operational state evidence.
- `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-004.md` - Loyal Opposition NO-GO requiring this operational state to be split or explicitly brought into scope.
- `DELIB-20265152` - Prior verification that spawned headless harness prompts defer to durable role records; relevant because this split preserves durable/default routing for headless work while treating the current PB authority as session-scoped.
- `DELIB-20264030` - Prior GO on whole-candidate mode-switch validation; relevant because any future corrective role-state transaction must continue to use the governed role writer and whole-candidate validation path.

## Requirement Sufficiency

Existing requirements are sufficient. The NO-GO did not require a new product requirement or architecture decision; it required a lifecycle correction so operational state can be reviewed under its own target set. The governing role/session specifications already define the separation between durable/default routing and interactive/session role authority.

## Proposed Operational State Scope

The state in scope is the already-reported owner-authorized role-state transition and its generated surfaces:

- `groundtruth.db` contains the durable/default harness role state written by the governed mode-switch transaction.
- `harness-state/harness-registry.json` is the generated hot-path projection of that MemBase role state.
- `.gtkb-state/mode-switches/20260708T024052Z-b298d4a9.json` is the audit record for harness A moving from `["prime-builder"]` to `["loyal-opposition"]` with the reason `WI-5069 owner-authorized LO-only headless surge; interactive PB marker anchors Prime Builder coverage`.

This proposal does not request manual editing of any of those files. If verification finds inconsistency among the DB, projection, and audit record, the correction path must be a separately reported governed mode-switch/projection operation limited to these target paths.

## Acceptance Criteria

- The split thread scopes the operational role-state files separately from the original WI-5069 source/rule invariant target set.
- The original source/rule invariant files and tests are not re-authorized, reimplemented, or terminally verified by this proposal.
- The operational state is attributable to the owner decision and session instruction carried in the WI-5069 thread.
- The audit record, durable/default role projection, and canonical role reader agree that harness A durable/default role is `loyal-opposition` after the `2026-07-08T02:40:52Z` transaction.
- The absence of an active durable/default Prime Builder in the post-transaction projection is explicitly treated as the intended operational state for this split, while current-session Prime Builder authority remains transcript/session-scoped.
- Verification is reproducible in headless Codex with read-only commands and without requiring reviewer writes to temp locations outside `E:/GT-KB`.
- Any future corrective mutation, if required, is limited to the target paths and uses the governed role writer/projection path rather than manual registry or database edits.

## Specification-Derived Verification Plan

| Spec / governing surface | Verification command or check | Expected result |
| --- | --- | --- |
| `REQ-HARNESS-REGISTRY-001`, `GOV-HARNESS-ROLE-PORTABILITY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli harness roles` | Canonical projection reads successfully; harness A is active and has role `["loyal-opposition"]`; no active durable/default Prime Builder is present in this operational topology. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Review this proposal's `author_model_configuration` plus the carried owner instruction in `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md` and `003.md`. | The split distinguishes this headless PB bridge-authoring session from the durable/default LO routing state and does not claim the durable registry alone provides PB authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5069-operational-role-state-split` and `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5069-operational-role-state-split` | Proposal packet is linkable to WI-5069, target paths are concrete, and no mandatory clause gap blocks Loyal Opposition review. |
| Operational audit evidence | `Get-Content -LiteralPath '.gtkb-state/mode-switches/20260708T024052Z-b298d4a9.json'` | Audit record shows harness A changed from `["prime-builder"]` to `["loyal-opposition"]`, with `deferred: false` and the WI-5069 owner-authorized LO-only surge reason. |
| Split boundary | Read `target_paths` in this proposal and compare them with `target_paths` in `bridge/gtkb-wi5069-headless-lane-coverage-role-invariant-001.md`. | This proposal targets only operational role-state files; the original proposal remains the only approval surface for source/rule invariant files. |

## Out-of-Scope Boundaries

- No source or test changes under `groundtruth-kb/src/`, `groundtruth-kb/tests/`, `platform_tests/`, or `tests/` are authorized by this split.
- No rule/config changes under `.claude/rules/`, `.claude/hooks/`, `.codex/gtkb-hooks/`, `config/`, or `.github/workflows/` are authorized by this split.
- No dispatcher ranking, worker selection, launcher readiness, budget, or codex no-window readiness behavior is authorized by this split.
- No edit to existing bridge files is authorized by this split. If the original WI-5069 report needs replacement or clarification, that must be a new status-bearing file in the appropriate bridge thread.
- Prime Builder must not write GO, NO-GO, or VERIFIED for this split.
- This proposal does not make the source/rule invariant implementation VERIFIED. It only asks Loyal Opposition to approve the operational state as a separately scoped finalization path.

## Risk / Rollback

The main risk is normalizing an operational state that appears surprising in isolation: there is no active durable/default Prime Builder in the current role projection. This proposal treats that state as intentional only because the owner explicitly authorized an LO-only headless surge while preserving the active Prime Builder session through transcript/session role evidence.

Rollback, if required, must use the governed mode-switch transaction path rather than manual edits. A rollback would restore harness A durable/default role to `prime-builder`, regenerate `harness-state/harness-registry.json` from `groundtruth.db`, and write a new audit record under `.gtkb-state/mode-switches/`. That rollback is not requested by this proposal.

## Loyal Opposition Asks

1. Confirm whether this operational role-state split is sufficient to satisfy the `004` NO-GO scope finding.
2. Confirm whether the target paths are appropriately limited to `harness-state/harness-registry.json`, `groundtruth.db`, and the named mode-switch audit record.
3. If GO is granted, review the follow-up implementation report for read-only evidence that the DB, projection, and audit record match the owner-authorized LO-only headless surge.

## Recommended Commit Type

chore: isolate WI-5069 operational role-state finalization from source invariant work
