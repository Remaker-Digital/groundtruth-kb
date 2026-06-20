REVISED
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ee46e-e98a-7bd0-858c-0257095f56c8
author_model: gpt-5-codex
author_model_version: 2026-06-20
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# WI-4592 Cross-Harness Protocol Parity Tests - Corrected Implementation Report

bridge_kind: implementation_report
Document: agent-disposition-wi4592-cross-harness-protocol-parity-slice1
Version: 005 (REVISED; corrected post-implementation report)
Responds to: bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-004.md
Approved proposal: bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-001.md
GO verdict: bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-002.md

Project Authorization: PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA
Project: PROJECT-AGENT-DISPOSITION-AND-PROTOCOL-ENFORCEMENT
Work Item: WI-4592

target_paths: ["platform_tests/scripts/test_cross_harness_protocol_parity.py"]

## Revision Claim

This revision addresses `FINDING-P1-001` from `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-004.md`.

Prime Builder revised `platform_tests/scripts/test_cross_harness_protocol_parity.py` so the parity test no longer hardcodes a fixed durable role assignment for each harness ID. The test now treats `harness-state/harness-identities.json` as the identity expectation surface, reads current roles and statuses from `harness-state/harness-registry.json`, distinguishes active from suspended harness rows, and asserts stable protocol invariants rather than stale role ownership.

The corrected test still verifies that:

- the expected harness identities exist;
- registry rows use valid role and status vocabulary;
- active rows include current role data;
- suspended rows are not treated as active event sources;
- at least one active Prime Builder role and one active Loyal Opposition role are available;
- every expected harness can receive dispatch through its registered headless surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-PROTOCOL-001`
- `.claude/rules/file-bridge-protocol.md`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `REQ-HARNESS-REGISTRY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `WI-4592`

## Prior Deliberations

- `DELIB-20265293` - prior Loyal Opposition GO verdict for this cross-harness parity slice.
- `DELIB-20263499` - Loyal Opposition GO on the Agent Disposition Protocol Enforcement umbrella.
- `DELIB-20263455` - owner-approved Agent Disposition and Protocol Enforcement planning and ranked child work items.
- `DELIB-0862` - bridge-first governance and warning against ambiguous queue/workflow state.
- `DELIB-20260872` - project authorization grants bridge-cycle eligibility, not blanket implementation authority.
- `DELIB-2258` - implementation-start and work-intent gating are durable safety controls.
- `DELIB-20261178` - live versioned bridge and dispatcher state are authority, not stale summaries.
- `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-004.md` - Loyal Opposition NO-GO finding addressed by this revision.

## Owner Decisions / Input

No new owner decision was required for this corrective revision. The work stayed inside the existing owner-approved project authorization and Loyal Opposition GO scope:

- `DELIB-20263455`
- `PAUTH-PROJECT-AGENT-DISPOSITION-PROTOCOL-ENFORCEMENT-UMBRELLA`
- `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-002.md`

## Findings Addressed

### FINDING-P1-001: The parity test encodes stale durable-role expectations and fails in the current registry state

Response:

- Removed the hardcoded `EXPECTED_ROLE_BY_ID` table.
- Added `VALID_ROLES` and `VALID_STATUSES` vocabulary checks.
- Kept fixed harness identity expectations in `harness-state/harness-identities.json`.
- Read current roles and statuses from `harness-state/harness-registry.json`.
- Separated active rows from suspended rows.
- Asserted stable invariants that should remain true across owner-directed role changes: active rows have role data; suspended rows are not event sources; the active registry still includes Prime Builder and Loyal Opposition capacity; every expected harness can receive dispatch through its registered headless surface.

## Scope Changes

This revision changes only `platform_tests/scripts/test_cross_harness_protocol_parity.py`, the approved test-only target path. It does not mutate harness registry state, dispatcher configuration, hook registrations, source modules, prompts, rules, MemBase records, bridge state outside this revision file, cloud services, deployments, or credentials.

The active implementation-start packet was recreated for this session before editing:

- work-intent claim: `agent-disposition-wi4592-cross-harness-protocol-parity-slice1`, session `019ee46e-e98a-7bd0-858c-0257095f56c8`, acquired `2026-06-20T10:11:05Z`.
- implementation authorization packet: `sha256:856d4fc44bd91f53c3ba16d81fdfe49369f37cb1f36b71ef2105fe7503a15c06`, created `2026-06-20T10:11:42Z`, latest status `NO-GO`, GO file `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-002.md`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `REQ-HARNESS-REGISTRY-001` | Focused pytest now reads the durable identity file for expected IDs and the live registry for current role/status data. The corrected test passed against current registry state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001`, `.claude/rules/file-bridge-protocol.md` | Focused pytest still verifies dispatcher status rules and bridge actionability boundaries. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Focused pytest still verifies protected mutation surfaces expose bridge GO, implementation authorization, and work-intent requirements. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Focused pytest still verifies owner-action visibility contract surfaces. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This revised report carries project metadata, linked specs, target paths, spec-to-test mapping, command evidence, and observed results. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The implementation stayed inside the approved test-only target path and avoided forbidden operations. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All edited and reported paths are under `E:\GT-KB`; `Test-Path -LiteralPath bridge\INDEX.md` returned `False`. |
| `GOV-STANDING-BACKLOG-001`, `WI-4592` | The revision addresses the active WI-4592 NO-GO without widening the work item scope. |

## Commands Run

```text
python scripts\bridge_claim_cli.py claim agent-disposition-wi4592-cross-harness-protocol-parity-slice1 --session-id 019ee46e-e98a-7bd0-858c-0257095f56c8 --ttl-seconds 7200
python scripts\implementation_authorization.py begin --bridge-id agent-disposition-wi4592-cross-harness-protocol-parity-slice1 --session-id 019ee46e-e98a-7bd0-858c-0257095f56c8 --expires-minutes 120
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cross_harness_protocol_parity.py -q --tb=short --basetemp .gtkb-state\pytest-wi4592-pb-rerun
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests/scripts/test_cross_harness_protocol_parity.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests/scripts/test_cross_harness_protocol_parity.py
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id agent-disposition-wi4592-cross-harness-protocol-parity-slice1
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4592-cross-harness-protocol-parity-slice1
Test-Path -LiteralPath bridge\INDEX.md
```

## Observed Results

- Work-intent claim acquired for session `019ee46e-e98a-7bd0-858c-0257095f56c8`.
- Implementation authorization packet created with hash `sha256:856d4fc44bd91f53c3ba16d81fdfe49369f37cb1f36b71ef2105fe7503a15c06`.
- Pytest: 6 passed, 1 warning (`PytestConfigWarning: Unknown config option: asyncio_mode`).
- Ruff check: `All checks passed!`
- Ruff format check: `1 file already formatted`.
- Applicability preflight against the then-operative implementation report chain passed: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, packet hash `sha256:9545d2008eb710a7b83f007bef327506e0725068c7e1d7106f381993319a4d0f`.
- ADR/DCL clause preflight against the then-latest NO-GO verdict passed with `Blocking gaps (gate-failing): 0`.
- Retired bridge index check: `False`.

## Files Changed

- `platform_tests/scripts/test_cross_harness_protocol_parity.py` - corrected registry-role assertions to derive current roles/statuses from the live durable registry.

## Recommended Commit Type

Recommended commit type: `test:`

Justification: this revision corrects a test-only implementation.

## Acceptance Criteria Status

- [x] The read-only cross-harness protocol parity test module still runs independently.
- [x] Tests inspect Codex, Claude Code, Antigravity, Ollama, and OpenRouter-related surfaces represented in the repo.
- [x] Startup role resolution checks no longer encode stale durable role assignments.
- [x] Bridge actionability, protected-write preflight, owner-action visibility, capability registry, and hook fallback checks still pass.
- [x] The implementation remains read-only and does not require external services.

## Risk And Rollback

Residual risk is limited to the chosen registry invariants becoming too broad or too narrow as dispatcher policy evolves. The revised assertions are intentionally tied to durable identities and live registry vocabulary rather than a fixed owner role assignment. Rollback is path-local removal or reversion of `platform_tests/scripts/test_cross_harness_protocol_parity.py`; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the stale-role hardcoding finding in `bridge/agent-disposition-wi4592-cross-harness-protocol-parity-slice1-004.md` is addressed.
2. Confirm the corrected test remains read-only and within the approved target path.
3. Return `VERIFIED` if satisfied, or `NO-GO` with any remaining findings.
