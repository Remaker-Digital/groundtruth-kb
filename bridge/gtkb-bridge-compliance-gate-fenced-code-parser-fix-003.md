NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-fenced-code-parser-tests
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Implementation Report - Bridge Compliance Gate Fenced-Code Parser Fix

bridge_kind: implementation_report
Document: gtkb-bridge-compliance-gate-fenced-code-parser-fix
Version: 003
Status: NEW
Author: Prime Builder (Codex / harness A)
Date: 2026-05-19 UTC
Responds to: `bridge/gtkb-bridge-compliance-gate-fenced-code-parser-fix-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3336
target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py"]

## Summary

Implemented and verified the fenced-code section-parser fix approved in `-002`.

When this Prime Builder pass began, `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` already contained the shared `_collect_section_lines(...)` helper and already routed `_has_clean_applicability_preflight`, `_has_concrete_spec_links`, and `_has_concrete_owner_decisions_section` through it. The two hook copies were byte-identical. This pass completed the bridge item by adding the missing regression suite and by verifying that the existing source behavior satisfies the GO acceptance criteria.

## Changes Made

- Added `platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py`.
- Confirmed the live hook and scaffold template both contain `_collect_section_lines(...)`.
- Confirmed `_has_clean_applicability_preflight`, `_has_concrete_spec_links`, and `_has_concrete_owner_decisions_section` use the shared fence-aware helper.
- Confirmed `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge verdict files remain writeable when they contain fenced preflight output.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Claude-side gate now accepts the fenced verdict format Codex already writes.
- `SPEC-AUQ-POLICY-ENGINE-001` - parser behavior remains deterministic.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - the fix is a pure markdown-line state machine with no LLM classifier.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec-link section parsing remains enforced.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps requirements to executed tests.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3336 is a small reliability defect fix.
- `GOV-STANDING-BACKLOG-001` - WI-3336 is tracked under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched files are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - proposal, tests, and report preserve durable traceability.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the artifact chain is maintained.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - GO triggered this implementation report.

## Prior Deliberations

- `DELIB-1637`, `DELIB-1638`, `DELIB-1639`, and `DELIB-1640` - prior bridge-compliance-gate parity review chain.
- `DELIB-1920` - consolidated `gtkb-codex-bridge-compliance-gate-parity` thread record.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - owner decision refreshing the harness hook-parity stance.

No prior deliberation found in the GO review rejected this fenced-code parser fix.

## Spec-Derived Test Mapping

| Specification | Behavior verified | Test |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fenced `bridge_applicability_preflight.py` output inside a GO verdict passes | `test_go_verdict_with_fenced_preflight_output_passes` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The Codex-style fenced preflight verdict format is accepted by the Claude gate | `test_go_verdict_with_fenced_preflight_output_passes` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | A verdict genuinely missing `packet_hash` still fails | `test_go_verdict_missing_packet_hash_still_fails` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | A verdict genuinely missing `missing_required_specs: []` still fails | `test_go_verdict_missing_required_specs_line_still_fails` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Spec-link scanning reaches real citations after an in-fence heading | `test_spec_links_with_fenced_heading_still_detected` |
| `SPEC-AUQ-POLICY-ENGINE-001` | Owner-decisions scanning reaches real prose after an in-fence heading | `test_owner_decisions_with_fenced_heading_still_detected` |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | Section collection is a deterministic fence/heading state machine | `test_collect_section_lines_fence_state_machine` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Both hook copies carry the behavior | all tests parametrized over live and template hook copies |

## Verification Commands

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py -v --tb=short
```

Observed result: `12 passed`.

```text
python -m pytest platform_tests/hooks -q --tb=short -k "bridge_compliance_gate"
```

Observed result: `101 passed, 210 deselected`.

```text
python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py
```

Observed result: `3 files already formatted`.

```text
Get-FileHash .claude\hooks\bridge-compliance-gate.py, groundtruth-kb\templates\hooks\bridge-compliance-gate.py
```

Observed SHA-256 for both files:

```text
1C58E3AA99526393993303795A290F7BBEA46FE819FF68D1286DC4C27DE653DF
```

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-compliance-gate-fenced-code-parser-fix
```

Observed result: PASS; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-compliance-gate-fenced-code-parser-fix
```

Observed result: PASS; `Blocking gaps (gate-failing): 0`.

## Scope Notes

The broader worktree contains unrelated dirty files from other bridge continuations. This report claims only the fenced-code parser regression test plus verification of the already-present hook/template implementation. No advisory template check, project metadata check, WI membership check, pending-proposal checkpoint, or tilde-fence support was changed.

## Recommended Commit Type

`test:` for this pass, because the source behavior was already present and this implementation pass adds the missing regression coverage. If squashed with the earlier hook/template source change, `fix:` remains appropriate for the combined change set.

## Risk And Rollback

Risk is low. The added tests exercise private hook helpers without changing runtime behavior. Rollback is deletion of `platform_tests/hooks/test_bridge_compliance_gate_fenced_code.py`; no data, schema, or config rollback is required.

## Owner Action Required

None.
