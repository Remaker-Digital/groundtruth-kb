NEW
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-2026-06-04T11-scan-helper
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, Keep Working PB, PowerShell workspace-write

# Implementation Proposal - Manual Bridge Scan Terminal-GO Filter

bridge_kind: prime_proposal
Document: gtkb-manual-bridge-scan-terminal-go-filter
Version: 001
Author: Prime Builder (Codex automation, owner prompt role)
Date: 2026-06-04 UTC
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4278

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

implementation_scope: helper_alignment plus regression_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

The manual bridge scan helper at `.claude/skills/bridge/helpers/scan_bridge.py` still treats every latest `GO` as Prime-actionable. That is stale for terminal-kind bridge proposals. The canonical notifier path already classifies operative Prime proposal `bridge_kind` values and derives `dispatchable=False` for terminal-kind `GO` entries such as `governance_review`, `scoping`, `closure`, `parking`, `index_reconciliation`, `thread_reconciliation`, `operational_state_change`, `candidate_spec_intake`, and `loyal_opposition_advisory`.

The mismatch creates false Prime work in Keep Working PB and manual startup scans. Current live examples include envelope governance-review threads whose GO verdicts explicitly state that `GO is terminal`, `target_paths: []`, and `requires_verification: false`, while the manual helper still reports them as Prime-actionable. The AXIS 2 in-session surface has already been fixed to consume the notifier `dispatchable` flag; this proposal applies the same rule to the manual scan helper.

## Claim

`scan_bridge.py` should preserve the file-bridge role split while using the canonical dispatchability model for latest `GO` entries:

- `NEW` and `REVISED` remain Loyal Opposition-actionable.
- `NO-GO` remains Prime-actionable, even for terminal-kind proposals, because it requires Prime revision.
- `GO` remains Prime-actionable only when the operative proposal is not terminal-kind.
- `VERIFIED`, `ADVISORY`, `DEFERRED`, and `WITHDRAWN` remain non-actionable.

The helper should not invent a new classifier. It should import and reuse the canonical detector/notify path if practical, or mirror the same terminal-token behavior only with explicit parity tests.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` is the queue authority, but consumers must not manufacture actionability beyond the protocol's terminal-kind routing rules.
- `GOV-RELIABILITY-FAST-LANE-001` - small reliability defect in a development helper, scoped to source plus tests, no schema or formal-artifact mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section links the proposal to governing specs and the bridge authority surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - header cites PAUTH, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps the behavior to regression tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` and `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the false-positive queue is a durable workflow artifact problem, not just cosmetic output.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale actionability is a lifecycle-state interpretation defect: terminal-kind `GO` entries should not remain active Prime work.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner authority for the reliability fast-lane standing PAUTH.
- `smart-poller-kind-aware-routing-2026-04-30-009` lineage, cited in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, established terminal-kind routing and the `dispatchable` invariant.
- `bridge/gtkb-axis-2-dispatchable-filter-003.md` and `bridge/gtkb-axis-2-dispatchable-filter-004.md` - same defect class for the AXIS 2 surface; that fix already filters terminal-kind `GO` entries by `dispatchable`.
- `bridge/gtkb-axis-2-dispatchable-filter-006.md` - on-disk VERIFIED verdict for the AXIS 2 surface fix, though the thread is currently not referenced by live `bridge/INDEX.md`; this proposal does not depend on INDEX authority from that unindexed thread.

## Requirement Sufficiency

Existing requirements are sufficient. The central notifier already has the terminal-kind classification and dispatchability behavior. The defect is limited to the manual helper not consuming that existing authority.

No owner decision is required before implementation because the work is a reliability fast-lane helper alignment under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` and does not mutate formal artifacts, schema, deployment, credentials, or application files outside GT-KB.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Proposal and implementation contain no credentials or environment values. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Mutate only the two declared in-root target paths. | Implementation-start packet and `git diff --name-only` review. | |
| CQ-COMPLEXITY-001 | Yes | Reuse the existing notifier dispatchability rule instead of adding a parallel classifier. | Focused pytest for terminal and non-terminal cases. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing status and bridge-kind terms; avoid divergent token lists if import reuse is viable. | Source review and tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed bridge dispatch behavior and do not broaden queue actionability. | Regression tests for terminal-kind `GO` exclusion and `NO-GO` preservation. | |
| CQ-DOCS-001 | Yes | Keep helper docstring/markdown output aligned with changed behavior if needed. | Source review and LO bridge review. | |
| CQ-TESTS-001 | Yes | Add focused regression tests to `platform_tests/scripts/test_scan_bridge.py`. | `python -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A | No runtime logging surface changes. | N/A. | Helper output only; no logs added. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus Ruff check and format-check before filing the implementation report. | Commands listed in the verification plan. | |

## Implementation Plan

1. Update `.claude/skills/bridge/helpers/scan_bridge.py` so Prime `GO` entries are filtered through the same terminal-kind dispatchability rule used by `groundtruth_kb.bridge.notify`.
2. Add focused tests in `platform_tests/scripts/test_scan_bridge.py`:
   - a latest `GO` whose operative `NEW` has `bridge_kind: governance_review` is excluded from Prime actionable output;
   - a latest `GO` whose operative `NEW` has `bridge_kind: implementation_proposal` remains Prime-actionable;
   - a `NO-GO` for a terminal-kind operative proposal remains Prime-actionable;
   - `NEW` / `REVISED` terminal-kind proposals remain Loyal Opposition-actionable.
3. Preserve existing tests for status-only parsing and summary counts.

## Specification-Derived Verification Plan

- `python -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short`
- `python -m ruff check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py`
- `python -m ruff format --check .claude/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py`
- Manual live scan check: `python .claude/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json` should not list terminal-kind governance-review `GO` entries such as `gtkb-session-wrap-procedure-001` or `gtkb-work-envelope-router-slice-1-001` as actionable, while still listing true implementation `GO` and `NO-GO` threads when present.

## Risk And Rollback

Risk is low and localized. The main behavioral risk is filtering a `GO` that actually needs Prime implementation. That is mitigated by using the same canonical terminal-kind classifier already used by cross-harness dispatch and by retaining all non-terminal and `NO-GO` behavior.

Rollback is a normal git revert of the helper/test commit. No database, formal-artifact, credential, deployment, or application runtime state changes are in scope.

## Files Expected To Change

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Recommended Commit Type

`fix` - reliability helper alignment plus regression tests.
