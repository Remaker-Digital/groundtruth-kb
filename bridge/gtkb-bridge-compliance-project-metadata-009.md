NEW

# Implementation Report - Bridge Compliance Gate Project Metadata Requirement (WI-3314)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 009
Responds to: bridge/gtkb-bridge-compliance-project-metadata-008.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", ".codex/skills/MANIFEST.json"]

This is the post-implementation report for WI-3314. The proposal was GO'd as REVISED-2 at `-006` and as REVISED-3 (scope correction) at `-008`. IP-1 through IP-8 are implemented; all verification commands pass.

## Claim

The metadata-presence enabling slice for `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` is implemented. The bridge-compliance-gate now hard-blocks NEW/REVISED implementation proposals that lack the three project-linkage metadata lines (`Project Authorization:`, `Project:`, `Work Item:`), excludes verdict files, and exempts non-implementation `bridge_kind` classes. No DCL status promotion: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`. CLAUSE-PROJECT-AUTH-LIVE-CHECK is deferred to WI-3315.

## In-Root Placement Evidence

All 9 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - source spec; this slice lands 3 of 4 clauses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema referenced by metadata lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex skill-adapter parity contract.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3314 tracked.
- `SPEC-AUQ-POLICY-ENGINE-001` - bridge-compliance-gate is part of the policy engine surface.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing WI-3314.
- `bridge/gtkb-bridge-compliance-project-metadata-002.md` - first NO-GO (closed by REVISED-1).
- `bridge/gtkb-bridge-compliance-project-metadata-004.md` - second NO-GO (closed by REVISED-2).
- `bridge/gtkb-bridge-compliance-project-metadata-006.md` - GO on REVISED-2.
- `bridge/gtkb-bridge-compliance-project-metadata-007.md` - REVISED-3 scope correction (added the predating test helper file).
- `bridge/gtkb-bridge-compliance-project-metadata-008.md` - GO on REVISED-3.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (AskUserQuestion: "Approve all 5 as drafted").
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision is required for this implementation report; the work is within the GO'd REVISED-3 `target_paths`.

## Implemented Changes

IP-1: Active hook `.claude/hooks/bridge-compliance-gate.py` - added 3-clause project-metadata detection (constants `PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`, `WORK_ITEM_LINE_RE`, `BRIDGE_KIND_LINE_RE`, `BRIDGE_KIND_METADATA_EXEMPT`, `PROJECT_METADATA_STATUSES`; helpers `_bridge_kind_is_metadata_exempt`, `_project_metadata_gaps`; new check in `_deny_reason_for_content`).

IP-2: Template hook `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - byte-identical to the active hook.

IP-3: Hook-template parity preserved. Active and template sha256 both `959c63a0a73454f7fc6cedfea16c1e48faf3f9f37fc689f4d03576ff47ce1a53`.

IP-4: Codex skill adapters regenerated. `python scripts/generate_codex_skill_adapters.py --check` reports `PASS (29 adapters current)`. Run without `--update-registry`.

IP-5: Canonical skill scaffolding updated - `.claude/skills/bridge/SKILL.md` and `.claude/skills/bridge-propose/SKILL.md` document the project-linkage metadata requirement; `.codex/skills/*` regenerated to match.

IP-6: New test file `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` - 13 tests.

IP-7: No DCL promotion. `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`.

IP-8: `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` - `_pending_preflight_content()` helper now emits the 3 project-linkage metadata lines (`Project Authorization: PAUTH-TEST-PENDING-PREFLIGHT`, `Project: PROJECT-TEST-PENDING-PREFLIGHT`, `Work Item: WI-0000`) so its NEW-proposal fixtures stay metadata-compliant and the 3 preflight-behavior tests reach the preflight path they exercise. No assertion logic changed.

## Specification-Derived Verification

Spec-to-test mapping:

| Clause | Tests |
|---|---|
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_authorization_line_blocked`, `test_bridge_proposal_missing_project_line_blocked`, `test_bridge_proposal_missing_work_item_line_blocked`, `test_bridge_proposal_all_three_metadata_lines_passes`, `test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-VERDICT-FILES-EXCLUDED | `test_verdict_file_go_no_metadata_passes`, `test_verdict_file_verified_no_metadata_passes`, `test_verdict_file_no_go_no_metadata_passes`, `test_verdict_file_withdrawn_no_metadata_passes` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes`, `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes`, `test_bridge_kind_governance_review_no_metadata_passes` |
| Regression guard | `test_bridge_kind_implementation_proposal_still_gated` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` / hook-template parity | `test_hook_matches_template_or_documented_divergence` (in hard-block suite) |
| IP-8 helper fix - no metadata-gate regression | `test_bridge_hook_blocks_write_when_pending_content_fails_preflight`, `test_bridge_hook_allows_write_when_pending_content_passes_preflight`, `test_bridge_hook_preflight_has_no_cache_between_writes` |

Commands executed and observed results:

- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q` - 13 passed.
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -q` - 15 passed.
- `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -q` - 7 passed.
- `python scripts/generate_codex_skill_adapters.py --check` - `Codex skill adapters: PASS (29 adapters current)`, exit 0.

Combined run of the two hook suites reported `28 passed`.

## Acceptance Criteria Check

- IP-1 + IP-2: 3-clause detection in BOTH hook files, byte-identical. PASS (sha256 parity confirmed).
- IP-3: hook-template hash-parity test passes. PASS (`test_hook_matches_template_or_documented_divergence`).
- IP-4: adapter `--check` exits 0; `.codex/skills/*` in sync. PASS.
- IP-5: canonical skill scaffolding updated. PASS.
- IP-6: new test file lands with 13 tests; all PASS. PASS.
- IP-7: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`. PASS.
- IP-8: `_pending_preflight_content()` helper updated; ALL 15 tests in `test_bridge_compliance_gate_hard_block_workspace.py` pass. PASS.
- No regression in `test_codex_bridge_compliance_gate.py`. PASS (7 passed).
- Both preflights PASS (recorded in the REVISED-3 GO at `-008`).

## Risks / Rollback

- Risk: the working tree carries unrelated parallel-session changes; a commit must be scoped to the 9 WI-3314 target paths only. Mitigation: report explicitly enumerates the target paths; commit deferred to owner direction.
- Rollback: revert the hook pair, regenerate adapters from reverted canonical, delete the new test file, revert the helper edit.

## Recommended Commit Type

`feat` - new mechanical governance gate (3 clauses) across active hook + template + Codex adapters + skill scaffolding + new test file + 1 predating-test-helper fix. No spec status promotion.
