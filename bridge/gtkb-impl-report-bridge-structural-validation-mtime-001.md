NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: claude-code-2026-05-27-impl-report-bridge-structural-validation-mtime
author_model: Claude
author_model_version: Claude Opus 4.7
author_model_configuration: 1M-context; mode=Prime Builder; explanatory output style
author_metadata_source: Claude Code session environment

bridge_kind: implementation_proposal
Document: gtkb-impl-report-bridge-structural-validation-mtime
Version: 001
Date: 2026-05-27
Author: prime-builder/claude-B
target_paths:
  - .claude/skills/bridge/helpers/impl_report_bridge.py
  - platform_tests/skills/test_bridge_impl_report_helper.py
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3388
Recommended commit type: fix:

## Implementation Claim

Add two convergent defenses in `.claude/skills/bridge/helpers/impl_report_bridge.py` `file_report()` (lines 405-460):

1. **Structural validation** before the `live_path.write_text` call: when content declares `bridge_kind: implementation_report`, validate presence of required header fields (`target_paths`, `Project Authorization`, `Project`, `Work Item`, `Recommended commit type`) and the `## Prior Deliberations` section (with explicit `_No prior deliberations: <reason>._` opt-out per `.claude/rules/codex-review-gate.md`). Raises `BridgeImplReportError` on missing fields, matching existing failure-closed pattern at lines 423 and 427.

2. **mtime preservation** on draft promotion: after `live_path.write_text`, call `os.utime(live_path, (src_stat.st_atime, src_stat.st_mtime))` so a promoted report carries its draft authorship time rather than the promotion-batch time.

## Specification Links

- `.claude/rules/file-bridge-protocol.md` Mandatory Implementation-Start Authorization Metadata: `target_paths` is mandatory.
- `.claude/rules/codex-review-gate.md` Mandatory Owner Decisions / Input Section Gate.
- `.claude/rules/codex-review-gate.md` Prior Deliberations Section Requirement.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (canonical spec-linkage rule).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (verification-gate rule).
- GOV-RELIABILITY-FAST-LANE-001 (standing-authorization eligibility for small defect/reliability fixes).
- GOV-FILE-BRIDGE-AUTHORITY-001 (live bridge index canonical workflow state).

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing authorization for small reliability fixes covers this fix by project membership in PROJECT-GTKB-RELIABILITY-FIXES.
- DELIB-0687: credential-scan narrowing post-implementation verification. The existing credential gate in `file_report()` (lines 425-427) is the precedent failure-closed pattern this proposal mirrors for structural fields.
- S363 audit (this session, 2026-05-27): a sub-agent audit of 50 implementation reports in the 2026-05-19..27 window found 52/69 reports authored by the persistent Codex-Desktop session UUID 019e425a-79e8-7351-80bc-38c73b0b9429 missing `target_paths`, 51/69 missing `Project Authorization`/`Project`/`Work Item` tuple, 59/69 missing `Recommended commit type`. A parallel investigation traced the structural bypass to `file_report()` writing directly via `Path.write_text` (line 435), outside the bridge-compliance-gate PreToolUse hook scope.
- S363 mtime investigation (this session): a parallel Codex session executed a batch draft promotion at 2026-05-27T02:08:07 PDT in a 54ms burst, creating 117 files at identical mtime. Drafts staged 2026-05-20 in `.gtkb-state/bridge-impl-reports/drafts/` were promoted to live `bridge/*.md` 7 days later. Each promotion overwrote draft authorship mtime with promotion mtime, breaking any audit recency query that relies on filesystem mtime.

## Owner Decisions / Input

- Owner directive 2026-05-27 in this session: "Please proceed with 1-4." Authorizes execution on the four S363 audit follow-on items, including this structural fix.
- Owner AUQ 2026-05-27 (Bridge INDEX Maintenance governance gap): answer "Relax: remove from required sections." Subsequent investigation found the `## Bridge INDEX Maintenance` section is NOT actually required by any current rule, template, or generator code. The audit had asserted a non-existent requirement; no rule change is needed; the finding is captured as session memory clarification rather than a separate proposal.
- Owner directive 2026-05-27 (branching topology): "All work from all branches should merge to main and all new work should be on the develop branch, starting now." This proposal is filed on develop per directive.

## Files Changed

- `.claude/skills/bridge/helpers/impl_report_bridge.py`: ~15 lines added (structural validation block) + ~5 lines added (mtime preservation block). No deletions; both fixes are additive within the existing `file_report()` function body.
- `platform_tests/skills/test_bridge_impl_report_helper.py`: new test file or extension of existing equivalent, ~9 test cases covering each validation field, the opt-out path, the bridge-kind gate, and mtime preservation positive/negative cases.

## Implementation Plan

In `.claude/skills/bridge/helpers/impl_report_bridge.py`:

(1) Between the existing `ensure_author_metadata(...)` call at line 428 and the `live_path.write_text(...)` call at line 435, insert structural validation. Pseudocode:

- If content contains `bridge_kind: implementation_report`:
  - Collect the missing-required-headers list by scanning each of the 5 fields (`target_paths`, `Project Authorization`, `Project`, `Work Item`, `Recommended commit type`) against a per-line regex.
  - If any are missing, raise `BridgeImplReportError` naming the missing fields.
  - If `## Prior Deliberations` is absent AND `_No prior deliberations:` is also absent, raise `BridgeImplReportError` explaining the opt-out convention.

(2) After `live_path.write_text(content, encoding="utf-8", newline="\n")` at line 435 and before the INDEX-update block at lines 436-447, insert mtime preservation. Pseudocode:

- If `content_path` is not None:
  - Try: read source stat, call `os.utime(live_path, (src_stat.st_atime, src_stat.st_mtime))`.
  - On OSError: swallow (best-effort; the write must not fail on mtime preservation).

Tests in `platform_tests/skills/test_bridge_impl_report_helper.py`:

1. `test_file_report_validates_target_paths_present`: implementation_report content missing the `target_paths:` line raises BridgeImplReportError listing the field.
2. `test_file_report_validates_project_authorization_present`: same shape, Project Authorization field.
3. `test_file_report_validates_project_present`: same shape, Project field.
4. `test_file_report_validates_work_item_present`: same shape, Work Item field.
5. `test_file_report_validates_recommended_commit_type_present`: same shape, Recommended commit type field.
6. `test_file_report_validates_prior_deliberations_section_or_opt_out`: three sub-cases. Section present passes. Section absent without opt-out raises. Opt-out line present without section passes.
7. `test_file_report_only_validates_implementation_report_kind`: content with `bridge_kind: implementation_proposal` lacking structural fields passes (validation gated on implementation_report only).
8. `test_file_report_preserves_draft_mtime_when_content_path_supplied`: file_report called with content_path; resulting live file mtime equals source draft mtime.
9. `test_file_report_does_not_attempt_utime_when_content_supplied_directly`: file_report called with content string (no content_path); no os.utime call; live file mtime is the natural write time.

## Spec-to-Test Mapping

- `.claude/rules/file-bridge-protocol.md` Mandatory Implementation-Start Authorization Metadata maps to tests 1 (target_paths), 2 (Project Authorization), 3 (Project), 4 (Work Item).
- `bridge/gtkb-governance-hygiene-bundle-001.md` Change B (S333 audit FINDING-P0-001) maps to test 5 (Recommended commit type).
- `.claude/rules/codex-review-gate.md` Prior Deliberations Section Requirement maps to test 6 (positive plus negative plus opt-out).
- Validation scope (implementation_report only) maps to test 7.
- S363 mtime artifact finding maps to tests 8 and 9.

## Acceptance Criteria

- All 9 new tests pass.
- All existing tests in the impl_report_bridge test surface continue to pass.
- file_report rejects implementation_report content that omits any of the 5 required headers OR the Prior Deliberations section (without opt-out).
- file_report accepts implementation_proposal, governance_review, and other non-implementation_report bridge kinds without structural validation.
- file_report preserves source draft mtime on the live file when content_path is supplied.
- Lint, type, and format checks pass on the touched file.

## Risk and Rollback

Risk surface: implementation_reports authored against the relaxed contract (52/69 of recent reports per S363 audit) would fail to file after this lands. This is the desired outcome (failing closed against the same structural defects Codex catches in review) but produces transient friction for parallel sessions filing reports concurrently. Mitigation: validation messages name the specific missing fields so authors can immediately correct and retry.

Rollback: a single-revert commit on `.claude/skills/bridge/helpers/impl_report_bridge.py` restores prior behavior. The new tests fail open in that case (no validation present, no exceptions to assert against); they would be revised or deleted as part of the revert.

Compatibility: no public API changes; file_report signature unchanged. The validation block runs only when content already declares `bridge_kind: implementation_report`. Proposals and other bridge kinds bypass it.

## Loyal Opposition Asks

1. Confirm the 5 required-header list captures all S363 audit structural defects, or identify additional fields that should be enforced.
2. Confirm the `## Prior Deliberations` opt-out regex (`_No prior deliberations:`) matches the convention documented in `.claude/rules/codex-review-gate.md` and used by author practice.
3. Confirm the `os.utime` placement (between live_path.write_text and the INDEX-update block at lines 436-447) does not interfere with the existing best-effort archival-trim call at lines 449-459.
4. Confirm test framework choice matches the existing `platform_tests/skills/` conventions (pytest, file-based fixtures).
5. Verify that running this validation does not break the helper invocation from the deterministic `gt bridge propose` CLI scaffold path (where the draft has not yet been promoted to implementation_report kind).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
