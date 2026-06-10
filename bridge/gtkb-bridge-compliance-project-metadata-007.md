REVISED

# Implementation Proposal - Bridge Compliance Gate Project Metadata Requirement - REVISED-3 (WI-3314)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-project-metadata
Version: 007
Responds to: bridge/gtkb-bridge-compliance-project-metadata-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3314

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", ".claude/skills/bridge/SKILL.md", ".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", ".codex/skills/MANIFEST.json"]

This REVISED-3 is a **Prime-initiated scope correction** filed after the GO at `-006`. Implementing the GO'd REVISED-2 surfaced a target_paths gap that REVISED-2 did not anticipate. The proposal was GO'd at `-006`; implementation is substantively complete; this REVISED-3 corrects ONLY the `target_paths` scope.

## Why REVISED-3 (scope gap discovered during implementation)

REVISED-2's acceptance criteria required "No regression in existing `test_bridge_compliance_gate_hard_block_workspace.py`". During implementation that regression turned out to be **unavoidable without modifying that test file**:

- The new metadata gate (IP-1) correctly hard-blocks NEW/REVISED bridge proposals lacking the 3 project-linkage metadata lines.
- `test_bridge_compliance_gate_hard_block_workspace.py`'s helper `_pending_preflight_content()` (line 285) builds NEW bridge proposal fixtures that **predate the metadata gate** and lack those lines.
- 3 preflight-behavior tests (`test_bridge_hook_blocks_write_when_pending_content_fails_preflight`, `test_bridge_hook_allows_write_when_pending_content_passes_preflight`, `test_bridge_hook_preflight_has_no_cache_between_writes`) consume that helper. After IP-1, the metadata gate fires on those fixtures BEFORE the preflight logic they intend to test — so they fail with a `CLAUSE-PROJECT-METADATA-PRESENT` denial.
- Fixing the helper (adding the 3 metadata lines so the fixtures stay compliant and reach the preflight path) requires editing `test_bridge_compliance_gate_hard_block_workspace.py` — a file REVISED-2 did NOT authorize.

REVISED-3 adds that single file to `target_paths` and adds IP-8 to update the helper. Everything else carries forward from REVISED-2 unchanged.

## Claim

Identical to REVISED-2: metadata-presence enabling slice for 3 of 4 clauses of `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; no DCL status promotion. The only delta is `target_paths` + IP-8 (update the predating test helper).

## In-Root Placement Evidence

All 9 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - source spec; this slice lands 3 of 4 clauses.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema referenced by metadata lines.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex skill-adapter parity contract (governs IP-4).
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
- `bridge/gtkb-bridge-compliance-project-metadata-006.md` - GO on REVISED-2; this REVISED-3 corrects the target_paths gap that GO did not catch.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; REVISED-3 expands `target_paths` by one test file to make the GO'd acceptance criteria achievable.

## Requirement Sufficiency

Existing requirements sufficient. The source DCL fully specifies all 4 clauses; this slice scopes to 3 by explicit deferral of LIVE-CHECK to WI-3315.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3314); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1..IP-8 single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-project-metadata-007.md`; `REVISED:` line prepended. All prior lines (-006 GO, -005 REVISED-2, -004 NO-GO, -003 REVISED-1, -002 NO-GO, -001 NEW) preserved. Append-only audit trail intact.

## Proposed Scope

IP-1 through IP-7 are **unchanged from REVISED-2** (`bridge/gtkb-bridge-compliance-project-metadata-005.md`): IP-1 active-hook 3-clause detection; IP-2 byte-identical template change; IP-3 hook-template parity preservation; IP-4 Codex adapter regeneration; IP-5 canonical skill scaffolding; IP-6 new test file; IP-7 no DCL promotion.

### IP-8 (NEW in REVISED-3): Update the predating test helper

In `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`, update the `_pending_preflight_content()` helper (line 285) to include the 3 project-linkage metadata lines in the NEW bridge proposal fixture it produces:

```text
Project Authorization: PAUTH-TEST-PENDING-PREFLIGHT
Project: PROJECT-TEST-PENDING-PREFLIGHT
Work Item: WI-0000
```

These lines make the fixture compliant with the new metadata gate so the 3 preflight-behavior tests reach the preflight logic they intend to exercise. No assertion logic in those 3 tests changes; only the fixture content is made gate-compliant. The hook-parity test (`test_hook_matches_template_or_documented_divergence`) and all other tests in the file are untouched.

## Specification-Derived Verification Plan

New test file `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` (13 tests — the proposal's 12 + 1 regression guard `test_bridge_kind_implementation_proposal_still_gated`):

| Clause | Test |
|---|---|
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_authorization_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_project_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_missing_work_item_line_blocked` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_all_three_metadata_lines_passes` |
| PROJECT-METADATA-PRESENT | `test_bridge_proposal_metadata_accepts_wi_gtkb_worklist_id_formats` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_go_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_verified_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_no_go_no_metadata_passes` |
| VERDICT-FILES-EXCLUDED | `test_verdict_file_withdrawn_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_spec_intake_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_loyal_opposition_advisory_no_metadata_passes` |
| NON-IMPLEMENTATION-EXEMPT | `test_bridge_kind_governance_review_no_metadata_passes` |
| Regression guard | `test_bridge_kind_implementation_proposal_still_gated` |

Verification commands:
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -v` (13 new tests)
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py -v` (15 tests — parity + preflight; must ALL pass after IP-8 helper fix)
- `python -m pytest platform_tests/scripts/test_codex_bridge_compliance_gate.py -v` (Codex-side regression — 7 tests)
- `python scripts/generate_codex_skill_adapters.py --check` (adapter sync — exit 0)

## Acceptance Criteria

- IP-1 + IP-2: 3-clause detection in BOTH hook files, byte-identical.
- IP-3: hook-template hash-parity test passes.
- IP-4: adapter `--check` exits 0; `.codex/skills/*` in sync.
- IP-5: canonical skill scaffolding updated.
- IP-6: new test file lands with 13 tests; all PASS.
- IP-7: `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remains `specified`.
- IP-8: `_pending_preflight_content()` helper updated; ALL 15 tests in `test_bridge_compliance_gate_hard_block_workspace.py` pass.
- No regression in `test_codex_bridge_compliance_gate.py`.
- Both preflights PASS.

## Risks / Rollback

- Risk: REVISED-3 expands an already-GO'd thread's scope. Mitigation: the expansion is exactly one test file + one helper edit; the scope correction is required to make the GO'd acceptance criteria achievable.
- Risk: `--update-registry` would also touch `config/agent-control/harness-capability-registry.toml`, still outside scope. Mitigation: adapter regeneration runs WITHOUT `--update-registry`; plain `--check` confirms adapter sync (PASS, 29 adapters current). The registry-pointer update is a separate concern (not adapter content); flagged for a follow-on if Codex deems it required.
- Rollback: revert hook changes (parallel single-function-scope); regenerate adapters from reverted canonical; delete new test file; revert the helper edit.

## Recommended Commit Type

`feat` - new mechanical governance gate (3 clauses) across active hook + template + Codex adapters + 1 predating-test-helper fix. No spec status promotion.
