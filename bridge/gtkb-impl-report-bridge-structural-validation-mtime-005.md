REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e8991-a63a-7181-8f15-9e412e44f46d
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Revised Proposal - Impl Report Bridge Structural Validation and Mtime

bridge_kind: prime_proposal
Document: gtkb-impl-report-bridge-structural-validation-mtime
Version: 005 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-02 UTC
Responds-To: `bridge/gtkb-impl-report-bridge-structural-validation-mtime-004.md`
Supersedes: `bridge/gtkb-impl-report-bridge-structural-validation-mtime-003.md`
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3388
Recommended commit type: fix:
target_paths: [".claude/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]

## Revision Claim

This revision accepts the `-004` NO-GO and narrows the implementation to requirements already specified for implementation reports.

The revised implementation no longer enforces `target_paths`, `Project Authorization`, `Project`, `Work Item`, or `## Prior Deliberations` on implementation reports. Those fields remain implementation-proposal requirements unless and until the rule corpus is formally changed.

## NO-GO Resolution

### FINDING-P1-001 - Claimed implementation-report metadata requirement is not actually specified

Accepted. The revised proposal enforces only the currently specified implementation-report structure:

- `bridge_kind: implementation_report`, because the helper scaffold emits it and the helper is specifically the implementation-report filing path.
- `Recommended commit type:`, because `.claude/rules/file-bridge-protocol.md` requires implementation reports to include the recommended Conventional Commits type.

This revision does not enforce proposal-only implementation-start metadata on implementation reports.

### FINDING-P2-001 - Proposed validation is stricter than the helper scaffold

Accepted. The revised validation matches the helper scaffold. Current `build_report_skeleton()` already emits `bridge_kind: implementation_report` and `Recommended commit type:`. The revised tests assert the scaffold remains compatible with the filing validator.

## Summary

Add two narrow defenses to `.claude/skills/bridge/helpers/impl_report_bridge.py`:

1. Validate that filed content is an implementation report and includes the currently required `Recommended commit type:` field.
2. Preserve draft mtime when promoting a report from a content file, so filesystem recency evidence reflects draft authorship time rather than batch promotion time.

## Requirement Sufficiency

Existing requirements sufficient.

The current rule corpus already specifies the fields this revision enforces for implementation reports. No new rule or governance change is required for this narrowed validator. A later proposal may separately formalize additional implementation-report metadata if the owner wants that broader governance floor.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not include credentials in fixtures or helper errors. | Secret scan and fixture review. | |
| CQ-PATHS-001 | Yes | Touch only the helper and focused helper tests listed in `target_paths`. | Implementation authorization validation and git diff review. | |
| CQ-COMPLEXITY-001 | Yes | Keep validation as small helper-local checks. | Focused helper tests and source review. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing bridge kind and commit-type labels. | Tests assert expected labels. | |
| CQ-SECURITY-001 | Yes | Validate metadata without executing report content. | Unit tests use static content strings. | |
| CQ-DOCS-001 | Yes | Implementation report explains the narrowed governance scope. | Loyal Opposition bridge verification. | |
| CQ-TESTS-001 | Yes | Add tests for bridge kind, commit type, scaffold compatibility, and mtime behavior. | Focused pytest command. | |
| CQ-LOGGING-001 | N/A | | | Proposal does not change runtime logging. |
| CQ-VERIFICATION-001 | Yes | Run focused tests plus ruff check and ruff format check on changed Python files. | Commands and observed results in implementation report. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing authorization for small reliability fixes.
- `DELIB-0687` - credential-scan narrowing; precedent for helper-level fail-closed validation.
- S363 implementation-report audit - found repeated post-implementation report structural drift and traced helper writes through `Path.write_text`.
- S363 mtime investigation - found batch draft promotion overwrote useful draft mtimes.
- `bridge/gtkb-impl-report-bridge-structural-validation-mtime-004.md` - current NO-GO requiring this narrowed scope.

## Owner Decisions / Input

- Owner directive 2026-05-27: "Please proceed with 1-4."
- Owner directive that new work lands on `develop`; this revision is filed from `develop`.

No new owner decision is required.

## Implementation Plan

In `.claude/skills/bridge/helpers/impl_report_bridge.py`:

1. Add a helper-local validation function used by `file_report()` before writing the live file.
2. Reject content that omits `bridge_kind:` or supplies a value other than `implementation_report`.
3. Reject content that omits `Recommended commit type:`.
4. Do not validate `target_paths`, `Project Authorization`, `Project`, `Work Item`, or `## Prior Deliberations`.
5. After `live_path.write_text(...)`, when `content_path` is supplied, copy the source draft atime/mtime to the live file with `os.utime` when the filesystem allows it.

In `platform_tests/skills/test_bridge_impl_report_helper.py`:

1. Add tests for missing/wrong `bridge_kind`.
2. Add tests for missing `Recommended commit type:`.
3. Add a scaffold compatibility test proving generated skeleton content satisfies the validator once filled with normal required report sections.
4. Add mtime preservation tests for content-file promotion and direct string content.

## Spec-to-Test Mapping

- Helper files only implementation reports: tests reject missing and wrong `bridge_kind` values.
- Implementation reports include commit-type recommendation: test rejects missing `Recommended commit type:`.
- Validator does not enforce proposal-only metadata: test verifies reports without `target_paths` and project tuple can file when current report requirements are present.
- Scaffold remains compatible: test fills scaffold output and files it through the helper validator.
- Draft mtime is preserved on promotion: test asserts content-path filing sets live mtime to source mtime.
- Direct content retains natural write time: test asserts no source mtime copy is attempted when filing from direct content.

## Acceptance Criteria

- Focused helper tests pass.
- Ruff check and ruff format check pass for changed Python files.
- The implementation report carries the linked specifications, exact commands, observed results, and the mtime behavior evidence.
- The change does not create new implementation-report metadata requirements beyond the current rule corpus.

## Risk and Rollback

Risk is limited to the implementation-report helper filing path. The validator is narrow and aligned to current scaffold output. Rollback is a single revert of the helper/test changes.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
