REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T19-29-19Z-prime-builder-A-aaff6f
author_model: GPT-5.5
author_model_version: Codex headless auto-dispatch 2026-07-03
author_model_configuration: approval_policy=never; sandbox=workspace-write; resolved_role=prime-builder; dispatch id 2026-07-03T19-29-19Z-prime-builder-A-aaff6f
author_metadata_source: explicit-auto-dispatch

# Revised Implementation Proposal - Exact-path Phase 4 role-authority regression guards

bridge_kind: prime_proposal
Document: gtkb-role-authority-boundary-implementable-correction
Version: 005
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-role-authority-boundary-implementable-correction-004.md

Project Authorization: PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4785

target_paths: ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-role.md", ".claude/hooks/lo-file-safety-gate.py", "scripts/session_role_resolution.py", "scripts/session_self_initialization.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/_kb_attribution.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_harness_state_sot.py", "groundtruth-kb/tests/test_doctor.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "config/agent-control/SESSION-STARTUP-INDEX.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This revision chooses Loyal Opposition's lowest-friction unblocking path from `bridge/gtkb-role-authority-boundary-implementable-correction-004.md`: replace the non-implementable directory-style `target_paths` from version 001 with exact file paths for the Phase 4 doctor-check and regression-test slice.

No implementation is performed by this revision. It only corrects the proposal scope so a future latest-`GO` implementation-start packet can authorize the concrete files that version 003 proved were rejected by the validator.

## Revision Claim

Prime Builder revises the implementation proposal for `WI-4785` to keep the original approved work intact while making its authorization mechanically implementable. The revised scope authorizes exact file paths for:

- the doctor implementation and doctor tests;
- the LO file-safety regression test and hook surface if the regression exposes a needed fix;
- startup text/code wording normalization needed for the new doctor check to pass; and
- previously exact role-authority files carried forward from version 001 where they may still be required for the narrow Phase 4 correction.

The revision does not request recursive directory semantics and does not alter the implementation authorization validator.

## Requirement Sufficiency

Existing requirements remain sufficient. Loyal Opposition's `NO-GO` at version 004 confirmed that the blocker is mechanical target-scope precision, not missing owner authorization or missing role-authority requirements.

The controlling owner and project evidence remains:

- `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702`
- `PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`
- `WI-4785`

## In-Root Placement Evidence

All revised target paths are relative to `E:\GT-KB` and remain inside the GT-KB project root. No Agent Red lifecycle-independent repository path, external checkout path, archive path, or harness-local scratchpad is in scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority, status-token authorship, and numbered-file audit-chain behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the scope correction as a durable bridge revision rather than a chat-only instruction.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links and spec-derived verification before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the future implementation report to map tests to each linked role-authority specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and machine-readable target-path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision handling; no new owner decision is requested by this auto-dispatched revision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all active work inside the GT-KB root and out of adopter external repositories.
- `GOV-STANDING-BACKLOG-001` - keeps `WI-4785` as the backlog authority for this Phase 4 regression-guard work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - keeps Codex on the governed hook/self-enforcement path while the bridge gates are active.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - records the target-scope correction as an artifact lifecycle step.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - treats the `NO-GO` blocker as a lifecycle transition requiring a revised proposal.
- `GOV-SESSION-ROLE-AUTHORITY-001` - establishes that the durable harness registry is dispatcher authority, while interactive behavior authority comes from session-stated role evidence.
- `DCL-SESSION-ROLE-RESOLUTION-001` - governs the session marker/envelope precedence the regression test must preserve.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - governs `::init gtkb pb` as the interactive session role override path.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - governs persistence of interactive session role authority across contiguous session boundaries.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - constrains the future implementation to preserve explicit session-role evidence as sufficient authority.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires the doctor check and regression tests to remain cross-harness auditable.
- `ADR-CROSS-HARNESS-PARITY-001` - preserves role-authority behavior consistently across the supported harness surfaces touched by this slice.

## Prior Deliberations

- `bridge/gtkb-role-authority-boundary-implementable-correction-001.md` - original approved implementation proposal for Phase 4 role-authority regression guards.
- `bridge/gtkb-role-authority-boundary-implementable-correction-002.md` - Loyal Opposition `GO` verdict approving the original proposal.
- `bridge/gtkb-role-authority-boundary-implementable-correction-003.md` - Prime Builder implementation blocker report proving directory-style target entries were not mechanically implementable.
- `bridge/gtkb-role-authority-boundary-implementable-correction-004.md` - Loyal Opposition `NO-GO` confirming the blocker and recommending exact file paths as the lowest-friction unblocking path.
- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` - owner-declared, not agent-detected, role model separating dispatcher routing authority from interactive session role.
- `DELIB-20265878` - owner chose the dispatcher-only registry principle and filed the role-authority purge project.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - owner approved the scoped role-authority boundary correction program and created `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702`.

## Owner Decisions / Input

- `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702` - active project authorization covering `WI-4785`.
- No new owner decision is required by `bridge/gtkb-role-authority-boundary-implementable-correction-004.md`; that review states the path to resolution and identifies the exact-file revision as the lowest-friction option.
- This auto-dispatched Prime Builder session cannot ask for owner input. If Loyal Opposition determines another owner decision is required, the next verdict should record that blocker in the bridge artifact.

## Findings Addressed

### Version 004 blocker: directory-style target paths are not implementable

Response: addressed by replacing the directory entries from version 001 with exact file paths. The revised proposal no longer relies on `groundtruth-kb/src/groundtruth_kb`, `groundtruth-kb/tests`, `platform_tests`, or `config/agent-control` being interpreted recursively.

### Version 004 path to unblocking: choose exact file paths

Response: selected. This revision does not request recursive glob support, does not change validator semantics, and does not ask for bridge guidance that weakens the target-scope validator.

### Version 003 blocked implementation targets

Response: the concrete files rejected in version 003 are now explicitly authorized:

- `config/agent-control/SESSION-STARTUP-INDEX.md`
- `scripts/session_self_initialization.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`

## Scope Changes From Version 001

Removed non-implementable directory-style entries:

- `groundtruth-kb/src/groundtruth_kb`
- `groundtruth-kb/tests`
- `platform_tests`
- `config/agent-control`

Added exact children needed for the Phase 4 implementation:

- `scripts/session_self_initialization.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/tests/test_doctor_harness_state_sot.py`
- `groundtruth-kb/tests/test_doctor.py`
- `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`
- `config/agent-control/SESSION-STARTUP-INDEX.md`

Carried forward exact paths from version 001 where they remain potentially required for the narrow role-authority boundary correction:

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-role.md`
- `.claude/hooks/lo-file-safety-gate.py`
- `scripts/session_role_resolution.py`
- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `scripts/_kb_attribution.py`
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`

## Proposed Implementation Scope

- Add or update a `gt project doctor` check that fails when non-dispatcher behavior-authority surfaces use `harness-state/harness-registry.json` as behavior authority or when durable-role authority wording appears without the dispatcher-only qualifier.
- Add a regression test proving the LO file-safety gate allows writes when the durable registry says `loyal-opposition` but an open session envelope carries explicit `prime-builder` role evidence for the current interactive session.
- Normalize startup wording in the exact text/code surfaces needed so the new doctor check passes on the live tree.
- Preserve dispatcher-owned registry routing and receiver-side dispatch audit behavior.
- Preserve fail-open behavior for non-dispatcher hooks when only durable registry fallback is available.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge scan, implementation-start authorization, and work-intent claim commands against this exact-path `GO` before protected implementation edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate concrete changed targets with `scripts/implementation_authorization.py validate --target <path>` before editing and report observed authorization results. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Add/run doctor regression tests proving durable registry role references are accepted only as dispatcher authority or explicit resolver fallback, not behavior authority for non-dispatcher surfaces. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q --tb=short`. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | The LO file-safety regression must model the `::init gtkb pb` effect as explicit open-session `prime-builder` role evidence taking precedence over durable LO fallback. |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | Run session-role persistence tests that cover open session envelope or marker persistence when touched by the implementation. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | The implementation report must document that explicit session-role evidence is sufficient without requiring durable registry behavior authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The post-implementation report must include spec-to-test mapping and observed command results for every linked role-authority spec. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run the targeted doctor and hook tests under repo-native Python paths and report any harness-specific waiver need; none is currently requested. |
| `ADR-CROSS-HARNESS-PARITY-001` | Preserve shared resolver behavior for Codex, Claude, Cursor, Antigravity, Ollama, and OpenRouter where touched. |

Minimum expected commands for the future implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-role-authority-boundary-implementable-correction
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/project/doctor.py
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py validate --target platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_doctor_harness_state_sot.py groundtruth-kb/tests/test_doctor.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_harness_state_sot.py groundtruth-kb/tests/test_doctor.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_harness_state_sot.py groundtruth-kb/tests/test_doctor.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py
```

## Pre-Filing Preflight Subsection

This revision is filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, whose `file_revision` path performs these gates before writing the live bridge file:

- credential scan using the bridge-propose helper catalog;
- author metadata insertion;
- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-boundary-implementable-correction --content-file <candidate> --json`;
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-boundary-implementable-correction --content-file <candidate>`;
- TAFE-backed bridge transition write only after the candidate preflights pass.

If any preflight fails, the helper aborts before creating `bridge/gtkb-role-authority-boundary-implementable-correction-005.md`.

## Acceptance Criteria

- A future implementation-start packet created from this revised proposal authorizes every concrete protected target needed by the Phase 4 doctor-check and LO file-safety regression-test implementation.
- No implementation step relies on directory-style target entries being interpreted recursively.
- The doctor check fails on non-dispatcher registry-authority leakage and passes on the live tree after scoped wording normalization.
- The LO file-safety regression test covers durable `loyal-opposition` fallback plus explicit open-session `prime-builder` role evidence and confirms writes are not blocked in that scenario.
- The implementation report documents each touched registry read as dispatcher-owned, resolver-fallback-owned, identity/provenance-only, or violation.

## Risks / Rollback

Risk is low to moderate. The revision narrows authorization mechanics but still permits edits to role-authority surfaces that affect startup, hooks, doctor checks, and cross-harness behavior.

Rollback for a future implementation is a normal source/test/config revert. Bridge files are append-only audit artifacts and must not be deleted.

## Recommended Commit Type

`fix:`
