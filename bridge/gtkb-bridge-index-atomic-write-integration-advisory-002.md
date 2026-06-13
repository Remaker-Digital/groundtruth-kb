ADVISORY
author_identity: codex
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-12
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: default
author_metadata_source: Codex Loyal Opposition automation

# Bridge INDEX Atomic Write Integration Handoff Advisory

bridge_kind: loyal_opposition_advisory
Document: gtkb-bridge-index-atomic-write-integration-advisory
Version: 002
Source Work Item: WI-4481
Supersedes Advisory: bridge/gtkb-bridge-index-atomic-write-integration-advisory-001.md
Date: 2026-06-12
Recommended commit type: fix:

## Claim

The WI-4481 bridge-index concurrency defect has been implemented locally under Loyal Opposition's standing bridge-function repair authority. The implementation routes the live bridge filing paths that were identified in `-001` through the shared lock-backed `atomic_index_update()` boundary and adds regression coverage for same-document stale writes and unrelated concurrent document writes.

This is a bridge-protocol handoff advisory, not a terminal `VERIFIED` verdict. Because this Codex Loyal Opposition session authored the repair, Prime Builder or an independent reviewer should inspect the diff and decide the terminal disposition before WI-4481 is closed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Authority

Loyal Opposition normally reviews rather than implements. This repair is scoped to bridge correctness and bridge-use reliability, where GT-KB operating rules grant standing owner authority for Loyal Opposition to diagnose and repair bridge function and downstream bridge-dependent artifacts needed to sustain correct bridge use.

That authority permits the local repair and this advisory handoff. It does not permit the same authoring session to self-declare bridge-terminal `VERIFIED`.

## Files Changed

- `scripts/gtkb_bridge_writer.py`
- `.claude/skills/bridge-propose/helpers/write_bridge.py`
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`
- `platform_tests/scripts/test_gtkb_bridge_writer.py`
- `groundtruth-kb/tests/test_bridge_propose_helper.py`
- `platform_tests/skills/test_bridge_revise_helper.py`
- `platform_tests/skills/test_bridge_impl_report_helper.py`

## Implementation Summary

- `scripts.gtkb_bridge_writer.insert_index_status()` now calls `scripts.bridge_index_writer.atomic_index_update()` with state under `.gtkb-state/bridge-index-writer`.
- Same-document stale snapshot checks now compare only the target document's latest status/version and fail closed when that target changed.
- Unrelated concurrent document changes are merged inside the lock-held read-modify-write instead of causing broad stale-snapshot rejection.
- Duplicate version path insertion is rejected before mutating `bridge/INDEX.md`.
- The active and scaffolded bridge-propose helper paths now use the shared bridge-index writer lock for new document insertion.
- The Codex non-bypass propose path reads the target document snapshot before writing and rejects a same-document drift while merging unrelated current INDEX changes.

## Spec-To-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `platform_tests/scripts/test_bridge_index_writer.py`, `platform_tests/scripts/test_gtkb_bridge_writer.py`, bridge-propose helper tests, revise helper tests, implementation-report helper tests | yes | PASS, 146 tests |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Regression coverage for different-document concurrent updates preserving both document blocks/status lines | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Regression coverage for same-document stale latest-status/version attempts failing closed | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are inside `E:\GT-KB`; no out-of-root live dependency was added | yes | PASS |
| `GOV-STANDING-BACKLOG-001` | Repair is tied to `WI-4481` and preserves the precedence relationship called out in `-001` before broader dispatch expansion | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The advisory carries forward the bridge-governance and backlog/dependency specifications from `-001` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The local implementation evidence maps each required behavior to executed tests and code-quality gates | yes | PASS for local evidence; independent terminal verification still required |

## Commands Executed

```text
python -m pytest platform_tests/scripts/test_bridge_index_writer.py groundtruth-kb/tests/test_cli_bridge_index.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_bridge_propose_helper.py platform_tests/skills/test_bridge_propose_helper_work_intent.py platform_tests/skills/test_bridge_propose_helper.py -q --tb=short
# observed: 146 passed

python -m ruff check scripts/gtkb_bridge_writer.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py
# observed: All checks passed

python -m ruff format --check scripts/gtkb_bridge_writer.py .claude/skills/bridge-propose/helpers/write_bridge.py groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py platform_tests/scripts/test_gtkb_bridge_writer.py groundtruth-kb/tests/test_bridge_propose_helper.py platform_tests/skills/test_bridge_revise_helper.py platform_tests/skills/test_bridge_impl_report_helper.py
# observed: 7 files already formatted
```

## Required Prime Or Independent Follow-Up

1. Inspect the current diff for the seven files listed above.
2. Decide whether to accept the bridge-function fast-lane repair as implemented or request a normal Prime-authored conversion/implementation report.
3. If accepted, run an independent verification pass and file the terminal bridge disposition through the normal protocol.
4. Do not treat this advisory itself as `VERIFIED`; it is the handoff artifact for the implemented local repair.

## Owner Action Required

None.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
