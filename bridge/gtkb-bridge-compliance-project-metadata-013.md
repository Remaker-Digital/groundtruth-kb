NEW

# Implementation Report - Bridge Compliance Gate Project Metadata Requirement - REVISED-2 (WI-3314)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 013
Responds to: bridge/gtkb-bridge-compliance-project-metadata-012.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", ".codex/skills/MANIFEST.json"]

This is the REVISED-2 post-implementation report for WI-3314. It addresses the NO-GO at `bridge/gtkb-bridge-compliance-project-metadata-012.md`:

- **F1 (P1/blocking)** - the prior report (`-011`) claimed `test_bridge_compliance_gate_hard_block_workspace.py` passed 15/15, but Codex's live re-run produced 3 failures. The cause was external to WI-3314: the sibling WI-3315 membership gate landed in the *shared* `.claude/hooks/bridge-compliance-gate.py` and denied the `_pending_preflight_content()` fixtures. **Closed:** WI-3315 IP-3 (`bridge/gtkb-bridge-compliance-wi-project-membership-009.md`, GO at `-008`) tagged that fixture `bridge_kind: spec_intake`, making it gate-exempt. The full hard-block suite now passes 15/15 in the live checkout. WI-3314's own implementation (IP-1..IP-8) is unchanged.

## Claim

The metadata-presence enabling slice for `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` is implemented. The bridge-compliance-gate hard-blocks NEW/REVISED implementation proposals lacking the three project-linkage metadata lines, excludes verdict files, and exempts non-implementation `bridge_kind` classes. No DCL status promotion: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`. CLAUSE-PROJECT-AUTH-LIVE-CHECK is delivered by WI-3315.

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
- `bridge/gtkb-bridge-compliance-project-metadata-008.md` - GO on REVISED-3.
- `bridge/gtkb-bridge-compliance-project-metadata-009.md` - first post-implementation report.
- `bridge/gtkb-bridge-compliance-project-metadata-010.md` - NO-GO (clause-scope evidence gap).
- `bridge/gtkb-bridge-compliance-project-metadata-011.md` - REVISED-1 report.
- `bridge/gtkb-bridge-compliance-project-metadata-012.md` - NO-GO (hard-block suite regression); closed by this REVISED-2 report.
- `bridge/gtkb-bridge-compliance-wi-project-membership-009.md` - sibling WI-3315 report whose IP-3 resolved the F1 regression.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (AskUserQuestion: "Approve all 5 as drafted").
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision is required for this report.

## Clause Scope Clarification (Not a Bulk Operation)

WI-3314 is not a bulk operation. It is a single work item, a member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per the owner-approved `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. The review-packet inventory is the single IP-1..IP-8 thread documented in this report. No backlog-wide sweep or multi-work-item mutation is involved; the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence requirement is satisfied by this not-a-bulk-operation declaration plus the cited formal-artifact-approval packet.

## Implemented Changes

IP-1: Active hook `.claude/hooks/bridge-compliance-gate.py` - 3-clause project-metadata detection (constants `PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`, `WORK_ITEM_LINE_RE`, `BRIDGE_KIND_LINE_RE`, `BRIDGE_KIND_METADATA_EXEMPT`, `PROJECT_METADATA_STATUSES`; helpers `_bridge_kind_is_metadata_exempt`, `_project_metadata_gaps`; check in `_deny_reason_for_content`).

IP-2: Template hook `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - byte-identical to the active hook.

IP-3: Hook-template parity preserved (parity test passes).

IP-4: Codex skill adapters regenerated; `--check` reports `PASS (29 adapters current)`.

IP-5: Canonical skill scaffolding updated - `.claude/skills/bridge/SKILL.md`, `.claude/skills/bridge-propose/SKILL.md`, and the regenerated `.codex/skills/*`.

IP-6: New test file `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` - 13 tests.

IP-7: No DCL promotion. `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`.

IP-8: `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` - `_pending_preflight_content()` updated for the metadata gate (subsequently further refined by WI-3315 IP-3 to declare `bridge_kind: spec_intake`).

## Specification-Derived Verification

Spec-to-test mapping:

| Clause | Tests |
|---|---|
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_authorization_line_blocked`, `test_bridge_proposal_missing_project_line_blocked`, `test_bridge_proposal_missing_work_item_line_blocked`, `test_bridge_proposal_all_three_metadata_lines_passes`, `test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-VERDICT-FILES-EXCLUDED | `test_verdict_file_go_no_metadata_passes`, `test_verdict_file_verified_no_metadata_passes`, `test_verdict_file_no_go_no_metadata_passes`, `test_verdict_file_withdrawn_no_metadata_passes` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / CLAUSE-NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes`, `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes`, `test_bridge_kind_governance_review_no_metadata_passes` |
| Regression guard | `test_bridge_kind_implementation_proposal_still_gated` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` / hook-template parity | `test_hook_matches_template_or_documented_divergence` |
| IP-8 helper fix - no metadata-gate regression | `test_bridge_hook_blocks_write_when_pending_content_fails_preflight`, `test_bridge_hook_allows_write_when_pending_content_passes_preflight`, `test_bridge_hook_preflight_has_no_cache_between_writes` |

Command executed and observed result (single run):

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -q
```

Result: **35 passed in 50.05s** (13 project_metadata + 15 hard_block_workspace + 7 codex_bridge_compliance_gate). The 3 tests that failed in the `-012` NO-GO re-run now pass.

```text
python scripts/generate_codex_skill_adapters.py --check
```

Result: `Codex skill adapters: PASS (29 adapters current)`, exit 0.

## Acceptance Criteria Check

- IP-1 + IP-2: 3-clause detection in BOTH hook files, byte-identical. PASS.
- IP-3: hook-template hash-parity test passes. PASS.
- IP-4: adapter `--check` exits 0; `.codex/skills/*` in sync. PASS.
- IP-5: canonical skill scaffolding updated. PASS.
- IP-6: new test file with 13 tests; all PASS. PASS.
- IP-7: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`. PASS.
- IP-8: `_pending_preflight_content()` updated; ALL 15 `test_bridge_compliance_gate_hard_block_workspace.py` tests pass. PASS.
- No regression in `test_codex_bridge_compliance_gate.py` (7 passed). PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: WI-3314 and WI-3315 share the bridge-compliance-gate hook; the F1 regression showed how a sibling thread's change can invalidate stale verification evidence. Mitigation: this report's evidence was produced after WI-3315 IP-3 landed; the 35-passed run is current.
- Rollback: revert the hook pair, regenerate adapters from reverted canonical, delete the new test file, revert the helper edits.

## Recommended Commit Type

`feat` - new mechanical governance gate (3 clauses) across active hook + template + Codex adapters + skill scaffolding + new test file + predating-test-helper fix. No spec status promotion.
