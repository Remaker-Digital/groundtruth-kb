REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-22T15-10Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation Prime Builder auto-builder

# Revised Proposal - bridge-compliance-gate project-linkage metadata format guidance

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-gate-regex-bold-variant
Version: 003
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-bridge-compliance-gate-regex-bold-variant-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3496

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py"]

## First-Line Role Eligibility Check

Resolved session role: Prime Builder, by explicit owner instruction for this fresh automation session. Latest bridge status reviewed: NO-GO in `bridge/gtkb-bridge-compliance-gate-regex-bold-variant-002.md`. Status authored here: REVISED. Prime Builder is authorized to author REVISED proposal entries responding to Loyal Opposition NO-GO verdicts.

## Revision Claim

This revision addresses `FINDING-P1-001` by retargeting the proposal to the actual WI-3496 acceptance surface: the project-linkage metadata lines parsed by `PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`, and `WORK_ITEM_LINE_RE` in `.claude/hooks/bridge-compliance-gate.py`.

The proposed fix takes the lower-risk acceptance arm from WI-3496: keep the current plain-line metadata contract unchanged, but make the hard-deny message explicit and copy-paste-ready when markdown-bold metadata is silently rejected. The gate will continue to require plain metadata lines, and its message will show examples such as:

- `Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- `Project: PROJECT-GTKB-RELIABILITY-FIXES`
- `Work Item: WI-3496`

The message will also state that markdown-bold forms such as `**Project Authorization:** ...`, `**Project:** ...`, and `**Work Item:** ...` are not recognized as project-linkage metadata lines by this gate. No regex acceptance, control flow, bridge status transition, or formal metadata requirement changes.

## Findings Addressed

### FINDING-P1-001: Proposed implementation targets the wrong gate surface

Response: corrected. The prior proposal targeted section-heading diagnostics. This revision targets the project-linkage metadata diagnostics around `_project_metadata_gaps` and the missing project-linkage hard-deny path in `_deny_reason_for_content`, matching WI-3496 and the NO-GO verdict.

## Specification Links

- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-3496 is specifically about the bridge proposal project-linkage metadata lines and the gate behavior when markdown-bold project metadata is rejected.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge-compliance gate enforces bridge authority and proposal validity at write time; clearer metadata denials improve the enforcement surface without weakening it.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing specifications for the gate and the revision preserves the proposal linkage contract.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps the message-change assertions directly to the cited project-linkage and bridge-authority requirements.
- `GOV-STANDING-BACKLOG-001` - WI-3496 is a standing-backlog defect item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the live hook and tracked template must remain aligned so Codex parity behavior does not drift.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform hook and platform-test surfaces and does not touch `applications/`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix improves author guidance for producing durable, correctly linked bridge artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal keeps the gate behavior traceable to the durable project-linkage artifact contract.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - clearer bridge-gate denials reduce preventable churn in the proposal lifecycle.
- `SPEC-AUQ-POLICY-ENGINE-001` - no new owner question is required because the standing reliability authorization already covers this small defect-fix proposal and the change does not alter owner-decision semantics.

## Prior Deliberations

- `DELIB-2215` - prior bridge-compliance-gate regex fix thread; establishes that scoped compliance-gate parser/message defects are handled through bridge proposals.
- `DELIB-20263744` - verified outcome for the prior bridge-compliance-gate WI-AUTO regex fix; supports live hook and template lockstep handling.
- `DELIB-20263745` - Loyal Opposition review of the prior bridge-compliance-gate regex fix; documents reviewer expectations for gate regex/message changes.
- `bridge/gtkb-bridge-compliance-gate-regex-bold-variant-002.md` - current Loyal Opposition NO-GO requiring the revision to cover project-linkage metadata regexes or their failure guidance.
- Deliberation search was attempted for WI-3496 and project-linkage metadata. No additional located decision changes the scope of this revision.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` already requires the `Project Authorization:`, `Project:`, and `Work Item:` metadata lines, and WI-3496 already defines the allowed fix shape: either accept the markdown-bold variant or emit the expected format explicitly. This proposal implements the explicit-format message arm and introduces no new public API, lifecycle state, database schema, harness role rule, or specification obligation.

## Proposed Scope

1. In `.claude/hooks/bridge-compliance-gate.py`, augment the missing project-linkage metadata hard-deny text in `_deny_reason_for_content`. Keep `PROJECT_AUTHORIZATION_LINE_RE`, `PROJECT_LINE_RE`, `WORK_ITEM_LINE_RE`, `_project_metadata_gaps`, and all acceptance control flow unchanged. The new message text should include copy-paste-ready plain-line examples for `Project Authorization:`, `Project:`, and `Work Item:`, and should state that markdown-bold metadata forms are not recognized by the gate.
2. Apply the identical message-text change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` so the live hook and tracked activation template stay in lockstep.
3. Extend `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py` to verify the project-linkage metadata behavior for both hook copies. The tests should cover markdown-bold metadata denial with the new examples and confirm plain metadata lines still pass.

Out of scope: accepting markdown-bold metadata as valid, broadening the metadata regexes, changing section-heading diagnostics, changing bridge writer semantics, changing owner-decision policy, or editing any bridge dispatcher/runtime machinery.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Add `test_project_metadata_bold_variant_denied_with_copy_paste_examples` to `platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`. | A proposal using `**Project Authorization:**`, `**Project:**`, and `**Work Item:**` is denied as missing project-linkage metadata, and the deny reason contains the three plain-line examples. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Keep or extend the existing plain-metadata passing coverage in `test_bridge_compliance_gate_project_metadata.py`. | Canonical plain project-linkage metadata lines remain accepted, proving the message change does not break valid proposal metadata. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Parametrize or explicitly run the metadata tests against both `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. | The enforcement-facing hook and tracked template produce the same augmented guidance and retain the same accept/reject behavior. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest plus ruff checks on the changed hook and test files. | Verification output demonstrates the revision's claims with executed, spec-derived checks. |

Execution commands after implementation:

- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q --tb=short`
- `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`
- `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py`
- `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_project_metadata.py -q --tb=short` after any formatting adjustment

## Acceptance Criteria

1. A markdown-bold project-linkage metadata attempt is still rejected as invalid metadata.
2. The rejection reason includes copy-paste-ready plain-line examples for `Project Authorization:`, `Project:`, and `Work Item:`.
3. The rejection reason explicitly states that markdown-bold metadata forms are not recognized by the gate.
4. Plain project-linkage metadata lines still pass.
5. The live hook and tracked template remain aligned for this message text.
6. Focused pytest and ruff verification commands pass for the changed files.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - standing project authorization for reliability defect fixes under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20265457` - owner AUQ authorizing the `PROJECT-GTKB-RELIABILITY-FIXES` proposal batch that includes WI-3496.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - reliability fast-lane direction for small, single-concern defect fixes that proceed through the bridge protocol without a new per-item owner question.

No new owner input is required for this revision because it stays within the existing WI-3496 acceptance alternatives and selects the lower-risk explicit-message arm.

## Risk And Rollback

Risk: message-string changes can make tests brittle if assertions require exact full text. Mitigation: add focused substring assertions for the examples and bold-format warning, while preserving existing reason prefixes.

Risk: hook/template drift. Mitigation: edit both files in lockstep and test both surfaces.

Risk: scope creep into accepting markdown-bold metadata. Mitigation: this proposal explicitly keeps regex acceptance unchanged.

Rollback: revert the message-text additions in both hook copies and remove the added project-metadata message tests. No schema, data, or migration rollback is needed.

## Recommended Commit Type

`fix`
