NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Remove authoritative labels from memory/* paths in system-interface-map.toml; relocate release directives to a governed artifact

bridge_kind: prime_proposal
Document: gtkb-wi5119-memory-authoritative-label-removal
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5119

target_paths: ["config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_system_interface_map.py", "groundtruth-kb/tests/test_cli_authority.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Finding A1 (Tier-1) of DELIB-202665929: remove authoritative labels from the two memory/* entries in the governed system-interface control map, aligning them with the file's existing non_authoritative precedent. Low-risk enum + read_method edits; the stale Feature Freeze directive (confirmed lifted at v0.7.0-rc1) carries no governed authority once this lands.

Work item description: Finding A1 (Tier-1 severe). system-interface-map.toml:358 tags memory/release-readiness.md authoritative_source; :98 tags memory/MEMORY.md authoritative. Move binding release directives (Feature Freeze at release-readiness.md:37) into a GOV/spec or governed release-gate artifact. Re-verify freeze validity (lifts at v0.7.0-rc1; package already 0.7.0rc1).

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5119` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/agent-control/system-interface-map.toml`, `platform_tests/scripts/test_system_interface_map.py`, `groundtruth-kb/tests/test_cli_authority.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-PLATFORM-SOT-REGISTRY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265740` - Loyal Opposition GO verdict - WI-4701 Codex adapter CRLF whitespace fix
- `DELIB-20261112` - Loyal Opposition Verdict - Platform SoT Consolidation Umbrella REVISED
- `DELIB-20261254` - Loyal Opposition Verdict - Platform SoT Consolidation Umbrella REVISED
- `DELIB-20261049` - Loyal Opposition Advisory: WI-3404 v1.0 Acceptance Criteria Gate
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP` - S365 AUQ D: retire WI-3418 (RC Gate seed fixture) as obsoleted by Layer A hygiene-sweep program

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5119`.

## Proposed Scope

- Change generated_or_authoritative for the memory-md entry (~line 99) from authoritative_operational_notepad to non_authoritative_operational_notepad and reword its read_method to non-authoritative session-state framing.
- Change generated_or_authoritative for the release-readiness entry (~line 359) from authoritative_release_working_record to non_authoritative_release_working_record and reword its read_method.
- Retain the authoritative_source path field on both entries per the in-file parked-draft precedent (line 219); authority is carried by generated_or_authoritative. No schema field added or removed.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-INTAKE-bb25be` | After the change, no memory/* entry in system-interface-map.toml has an authoritative_* classification; test_system_interface_map.py asserts the non_authoritative_* values. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The governed control surface no longer advertises memory as an authoritative source. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- No memory/* entry in system-interface-map.toml carries an authoritative_* generated_or_authoritative value.
- test_system_interface_map.py and test_cli_authority.py pass with the new non_authoritative_* values.
- ruff check and ruff format --check pass on any changed Python.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/agent-control/system-interface-map.toml`
- `platform_tests/scripts/test_system_interface_map.py`
- `groundtruth-kb/tests/test_cli_authority.py`

## Recommended Commit Type

`feat`
