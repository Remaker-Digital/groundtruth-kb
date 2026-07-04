NEW
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: 2026-07-04T14-36-16Z-prime-builder-A-4e5997
author_model: GPT-5 Codex
author_model_version: Codex runtime 2026-07-04
author_model_configuration: Codex auto-dispatch Prime Builder

# Implementation Report - WI-4967 controlled artifact direct mutation guard

bridge_kind: implementation_report
Document: gtkb-wi4967-controlled-artifact-direct-mutation-guard
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard-002.md
Approved proposal: bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard-001.md
Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4967-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4967
Recommended commit type: feat:

## Implementation Claim

WI-4967 first implementation slice is complete. The implementation adds a shared controlled-artifact path classifier and routes the existing implementation-start gate, protected mutation guard, commit authorization check, and SDK Bash bridge guard through the same controlled-artifact semantics.

Direct tool or shell writes to root MemBase `groundtruth.db`, status-bearing bridge files, retired `bridge_INDEX`, and authority runtime-state subtrees now fail closed with stable reason codes. Governed bridge/helper workflows, non-status bridge notes, and diagnostic/report draft state remain supported.

## Scope Boundary

The implementation is limited to the approved target paths:

- `scripts/controlled_artifact_paths.py`
- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `scripts/check_protected_commit_authorization.py`
- `scripts/sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_controlled_artifact_paths.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`

This slice does not claim Codex hidden `.codex` helper write parity or DACL repair. WI-5002 remains retired as the failed initial hidden-helper workflow, and WI-5008 carried the dispatch-suppression remediation separately.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `WI-4967`

## Owner Decisions / Input

No new owner decision is required. The active GO verdict and project authorization cover this bounded source/test implementation slice.

## Prior Deliberations

- `DELIB-202665197` - owner-decision evidence for Phase 3 child work authorization.
- `bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard-001.md` - Prime Builder proposal.
- `bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard-002.md` - Loyal Opposition GO verdict.
- `bridge/harness-equivalence-phase-3-umbrella-004.md` - VERIFIED umbrella evidence for Phase 3 child WIs.
- `bridge/gtkb-wi4972-phase3-prioritization-release-gating` - VERIFIED Phase 3 release-gating baseline referenced by backlog reconciliation.

## Implementation-Start Authorization

The implementation packet is `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi4967-controlled-artifact-direct-mutation-guard.json`.

- Packet hash: `sha256:d96a31dbb67efcd7399bfb7f4d127cf88ee291e7bbd9295fbd6b0645bc1977cd`
- Created: `2026-07-04T14:37:50Z`
- Expires: `2026-07-04T16:37:50Z`
- Work-intent claim row: `29924`
- Work-intent session: `2026-07-04T14-36-16Z-prime-builder-A-4e5997`
- Claim kind: `go_implementation`
- Latest bridge status at claim check: `GO`

## Files Changed

- `scripts/controlled_artifact_paths.py` - new shared classifier for controlled bridge, MemBase, authority-state, protected-source, and dispatcher-config surfaces.
- `scripts/implementation_start_gate.py` - delegates protected path classification to the shared classifier and blocks direct controlled-artifact writes before normal packet-scope checks.
- `scripts/protected_mutation_guard.py` - delegates protection classification and blocks direct controlled-artifact mutations with stable reason codes.
- `scripts/check_protected_commit_authorization.py` - recognizes direct MemBase, authority-state, retired bridge index, and protected helper surfaces while preserving governed non-VERIFIED bridge helper filing compatibility.
- `scripts/sdk_bridge_bash_guard.py` - imports the shared bridge mutation command pattern so SDK Bash guarding uses the same bridge status-file and retired-index classification.
- `platform_tests/scripts/test_controlled_artifact_paths.py` - new direct classifier coverage.
- `platform_tests/scripts/test_implementation_start_gate.py` - adds controlled-artifact direct-write denial, preserves non-status bridge note writes, and clears ambient dispatch work-intent env in synthetic tests.
- `platform_tests/scripts/test_protected_mutation_guard.py` - adds direct controlled-artifact denial coverage and updates per-session PB marker setup.
- `platform_tests/scripts/test_check_protected_commit_authorization.py` - adds commit-authorization coverage for direct MemBase, bridge index, and authority runtime-state paths while preserving helper compatibility.
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py` - extends SDK Bash bridge guard coverage to `bridge_INDEX`.

## Architecture Alignment Ledger

| Related item | Disposition for this slice |
| --- | --- |
| `WI-4516` OpenRouter/Ollama Bash bridge bypass | Resolved precedent preserved. The shared SDK Bash bridge guard still blocks shell-mediated bridge artifact mutations and now uses the centralized bridge-status pattern. |
| `WI-4975` claimed-path leading-dot parser defect | Resolved prerequisite acknowledged. The classifier preserves leading-dot prefixes and tests cover dot-prefixed controlled paths rather than stripping them. |
| `WI-5002` Codex hidden helper write boundary | Retired failed initial workflow acknowledged. This implementation does not claim hidden `.codex` write parity or DACL repair; it only guards direct controlled-artifact bypass paths in the approved source/test surfaces. |
| `WI-5008` circuit-breaker dispatch suppression | Resolved carry-forward acknowledged. Terminal WI-5002 dispatch suppression remains separate; this slice does not reopen the retired WI-5002 workflow. |
| `WI-4972` Phase 3 prioritization and release gating | Resolved classification baseline acknowledged. WI-4967 proceeds as the bounded direct-manipulation prevention slice after prerequisite dispositions were resolved or explicitly scoped out. |

## Specification-Derived Verification

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests prove direct `bridge/<slug>-NNN.md` and `bridge_INDEX` mutation attempts are blocked by the gate/guard and SDK Bash coverage. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The change preserves governed helper/report paths and keeps diagnostic draft state outside the direct-authority-state deny list. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's concrete spec links and target-path boundary. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, and ruff format verification were run across every touched source/test file. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation remained inside the approved project authorization, work item, and exact target path list. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Stable structured reason codes were added for direct bridge-status, bridge-index, MemBase, runtime-authority-state, and mixed controlled-artifact denials. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed paths are GT-KB platform source/test or governed bridge report artifacts; no Agent Red or adopter files changed. |
| `GOV-STANDING-BACKLOG-001` | The alignment ledger uses current backlog dispositions for WI-4516, WI-4975, WI-5002, WI-5008, and WI-4972 instead of duplicating or reopening them. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Native Codex/file-tool paths are guarded through the implementation-start gate/protected mutation guard while SDK Bash paths share classifier semantics. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Controlled artifact authority is represented as source and test logic, not as an untracked convention. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Versioned bridge status artifacts remain governed lifecycle artifacts; direct mutations are blocked outside helper routes. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Direct writes to `groundtruth.db` and authority runtime-state paths fail closed even when a raw tool command attempts to bypass project authorization. |
| `ADR-CROSS-HARNESS-PARITY-001` | Shared classification is reused by Codex guard surfaces and SDK Bash guard tests rather than diverging by harness. |

## Tests And Results

| Command | Result |
| --- | --- |
| `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/controlled_artifact_paths.py scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_protected_commit_authorization.py scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_sdk_bridge_bash_guard.py` | PASS - `All checks passed!` |
| `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/controlled_artifact_paths.py scripts/implementation_start_gate.py scripts/protected_mutation_guard.py scripts/check_protected_commit_authorization.py scripts/sdk_bridge_bash_guard.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_sdk_bridge_bash_guard.py` | PASS - `10 files already formatted` |
| `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_sdk_bridge_bash_guard.py -q --tb=short --basetemp .gtkb-state/pytest-wi4967-controlled-artifact` | PASS - `246 passed, 2 warnings in 41.61s` |

Pytest warnings observed:

- `PytestConfigWarning: Unknown config option: asyncio_mode`
- `PytestCacheWarning: could not create cache path E:\GT-KB\.pytest_cache\v\cache\nodeids: [WinError 183] Cannot create a file when that file already exists`

## Acceptance Criteria Status

- PASS: Direct tool and shell writes to `groundtruth.db`, `bridge/<slug>-NNN.md`, `bridge_INDEX`, and authority-state subtrees are denied with stable reason codes.
- PASS: Governed helper/report draft flows and non-status bridge notes remain supported.
- PASS: WI-4516 SDK Bash bridge hardening remains covered and now imports the same bridge artifact command-pattern semantics.
- PASS: The Architecture Alignment Ledger cites WI-4516, WI-4975, WI-5002, WI-5008, and WI-4972 dispositions.

## Risk And Rollback

Risk is moderate because these guards sit on protected mutation paths. The implementation intentionally blocks raw direct mutation of controlled authority surfaces before normal GO/packet checks, so the expected operational path is governed helpers and source-controlled guard code.

Rollback is a revert of the ten source/test files changed in this implementation. Bridge proposal, GO verdict, and this implementation report are append-only audit artifacts and must not be deleted during rollback.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
