REVISED

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: claude-code-2026-05-27-impl-report-bridge-structural-validation-mtime-revised-1
author_model: Claude
author_model_version: Claude Opus 4.7
author_model_configuration: 1M-context; mode=Prime Builder; explanatory output style
author_metadata_source: Claude Code session environment

bridge_kind: implementation_proposal
Document: gtkb-impl-report-bridge-structural-validation-mtime
Version: 003
Revision: 1 (responds to NO-GO at -002)
Date: 2026-05-27
Author: prime-builder/claude-B
target_paths: [".claude/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "platform_tests/skills/test_bridge_impl_report_helper.py"]
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3388
Recommended commit type: fix:
Responds to NO-GO: bridge/gtkb-impl-report-bridge-structural-validation-mtime-002.md

## Revision Summary

This REVISED-1 addresses all three Codex NO-GO findings from `-002`:

- **F1 fix**: adds the mandatory `## Requirement Sufficiency` subsection per `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata.
- **F2 fix**: converts `target_paths` to the same-line JSON-list form parseable by `scripts/implementation_authorization.py`'s `TARGET_PATHS_RE` regex.
- **F3 fix**: redesigns the validation to anchor at the helper operation (`file_report()`) instead of at the content-supplied `bridge_kind` marker. `file_report()` validates ALL content it files. Non-report and missing `bridge_kind` values are explicit reject conditions, not bypasses. The test plan adds coverage for missing/alternate/non-report kinds. The new design also requires updating the existing test fixture `_completed_report()` to include `bridge_kind: implementation_report` (currently absent at `platform_tests/skills/test_bridge_impl_report_helper.py:72-103`).

The proposal also adds the template counterpart `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` to `target_paths` so scaffolded adopter projects receive the same fix.

## Implementation Claim

Add three defenses in `.claude/skills/bridge/helpers/impl_report_bridge.py` `file_report()` (lines 405-460), with parallel changes in the template counterpart at `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`:

1. **Bridge-kind gate** (new in REVISED-1): early-check that content declares `bridge_kind: implementation_report`. Missing `bridge_kind` raises `BridgeImplReportError("Implementation report content missing bridge_kind: implementation_report header")`. Wrong value raises `BridgeImplReportError(f"file_report() received bridge_kind={value}, expected implementation_report")`. This anchors validation at the operation boundary per Codex F3 critique.

2. **Structural validation** (after bridge-kind gate): validate presence of required header fields (`target_paths`, `Project Authorization`, `Project`, `Work Item`, `Recommended commit type`) and the `## Prior Deliberations` section (with explicit `_No prior deliberations: <reason>._` opt-out). Raises `BridgeImplReportError` naming missing fields. Mirrors the existing failure-closed pattern at lines 422-423 (`startswith("NEW")` check).

3. **mtime preservation** on draft promotion: after `live_path.write_text` (line 435), call `os.utime(live_path, (src_stat.st_atime, src_stat.st_mtime))` when `content_path` is supplied so promoted reports carry draft authorship time rather than promotion-batch time. Best-effort; swallows `OSError` so mtime preservation never fails the write.

## Requirement Sufficiency

**Existing requirements sufficient.**

Governing requirements for the proposed work are already specified in current canonical artifacts:

- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata: requires `target_paths`, `Project Authorization`, `Project`, `Work Item`.
- `.claude/rules/codex-review-gate.md` § Prior Deliberations Section Requirement: requires `## Prior Deliberations` section OR explicit `_No prior deliberations: <reason>._` opt-out line.
- `bridge/gtkb-governance-hygiene-bundle-001.md` Change B (S333 audit FINDING-P0-001): requires `Recommended commit type:` header field on implementation reports.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: spec-linkage requirement.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: verification gate requirement.
- GOV-RELIABILITY-FAST-LANE-001: standing-authorization eligibility for small defect fixes.

No new requirements or specifications are required to authorize this work. The proposal makes existing requirements mechanically enforceable in `file_report()` rather than relying on the bridge-compliance-gate hook (which `file_report()` bypasses because it writes via `Path.write_text` rather than the Write tool).

## Specification Links

- `.claude/rules/file-bridge-protocol.md` Mandatory Implementation-Start Authorization Metadata.
- `.claude/rules/codex-review-gate.md` Mandatory Owner Decisions / Input Section Gate.
- `.claude/rules/codex-review-gate.md` Prior Deliberations Section Requirement.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (artifact lifecycle integrity; cited per Codex -002 advisory-omission note).
- GOV-RELIABILITY-FAST-LANE-001.
- GOV-FILE-BRIDGE-AUTHORITY-001.

## Prior Deliberations

- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION: standing authorization covers this fix.
- DELIB-0687: credential-scan narrowing — the existing credential gate in `file_report()` (lines 425-427) is the precedent failure-closed pattern this proposal mirrors.
- S363 audit (this session, 2026-05-27): 52/69 audited reports missing `target_paths`; investigation traced the structural bypass to `file_report()` writing via `Path.write_text` outside the PreToolUse hook scope.
- S363 mtime investigation (this session): a parallel Codex session batch-promoted 117 drafts at 2026-05-27T02:08:07 PDT in 54ms; each promotion overwrote draft mtime.
- Codex NO-GO at `-002` (this session): three findings (F1 missing Requirement Sufficiency, F2 target_paths format, F3 validation anchored on wrong boundary). F3 is the critical correction: validation must be anchored on the helper operation, not on author-supplied content marker.

## Owner Decisions / Input

- Owner directive 2026-05-27: "Please proceed with 1-4." Authorizes execution.
- Owner direction (still in force): all new work lands on the develop branch; this REVISED is filed on develop.
- Owner AUQ 2026-05-27 (response to Codex NO-GO): selected "File REVISED-003 now" — addressing F1, F2, F3 fully. This proposal is that REVISED.

## Files Changed

- `.claude/skills/bridge/helpers/impl_report_bridge.py`: ~25 lines added (bridge-kind gate + structural validation + mtime preservation). No deletions.
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py`: parallel changes mirroring the canonical helper. ~25 lines added.
- `platform_tests/skills/test_bridge_impl_report_helper.py`: ~12 new test cases. Existing fixture `_completed_report()` at lines 72-103 updated to include `bridge_kind: implementation_report` + the 5 required header fields + a `## Prior Deliberations` section (since the new validation will reject the current fixture content).

## Implementation Plan

In `.claude/skills/bridge/helpers/impl_report_bridge.py`:

(1) Between the existing `helper.handle_hits_abort_or_redact(content, hits, mode="abort")` call at line 427 and the `ensure_author_metadata(...)` call at line 428, insert bridge-kind gate:

- Pseudocode:
  - Extract bridge_kind via regex on content (`^bridge_kind:\s*(\S+)$`, multiline).
  - If no match: raise `BridgeImplReportError("file_report content missing bridge_kind header")`.
  - If match and value != "implementation_report": raise `BridgeImplReportError(f"file_report() received bridge_kind={value!r}, expected implementation_report")`.

(2) Between the existing `ensure_author_metadata(...)` call at line 428 and the `live_path.write_text(...)` call at line 435, insert structural validation:

- Pseudocode:
  - For each of (`target_paths`, `Project Authorization`, `Project`, `Work Item`, `Recommended commit type`):
    - Check `re.search(rf"^{re.escape(field)}:\s*\S", content, re.MULTILINE)`.
    - Collect missing fields.
  - If any missing: raise `BridgeImplReportError("implementation_report missing required headers: " + ", ".join(missing))`.
  - If `## Prior Deliberations` not in content AND `_No prior deliberations:` not in content: raise `BridgeImplReportError("implementation_report missing ## Prior Deliberations section (use '_No prior deliberations: <reason>._' opt-out for novel topics)")`.

(3) After the `live_path.write_text(content, encoding="utf-8", newline="\n")` call at line 435 and before the INDEX-update block at lines 436-447, insert mtime preservation:

- Pseudocode:
  - If `content_path is not None`:
    - try: `src_stat = content_path.stat(); os.utime(live_path, (src_stat.st_atime, src_stat.st_mtime))`.
    - except `OSError`: pass (best-effort).

(4) Apply the same three changes to the template counterpart at `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` so scaffolded adopter projects receive identical behavior.

(5) Update existing test fixture in `platform_tests/skills/test_bridge_impl_report_helper.py`:

- `_completed_report()` (lines 72-103): inject `bridge_kind: implementation_report` line + the 5 required headers (`target_paths`, `Project Authorization`, `Project`, `Work Item`, `Recommended commit type`) + a `## Prior Deliberations` section. The fixture remains a valid test input for the existing `test_write_mode_creates_report_and_inserts_new_line` test.

## Spec-to-Test Mapping

Tests (12 cases total):

| Test | Spec / Rule | Behavior verified |
|---|---|---|
| `test_file_report_rejects_missing_bridge_kind` | F3 (anchor at operation) | Content with no `bridge_kind:` line raises BridgeImplReportError |
| `test_file_report_rejects_non_report_bridge_kind` | F3 | Content with `bridge_kind: implementation_proposal` (or other non-report value) raises BridgeImplReportError |
| `test_file_report_accepts_implementation_report_bridge_kind` | F3 | Content with `bridge_kind: implementation_report` plus all required fields passes |
| `test_file_report_validates_target_paths_present` | file-bridge-protocol Mandatory Impl-Start Metadata | Missing target_paths raises |
| `test_file_report_validates_project_authorization_present` | same | Missing Project Authorization raises |
| `test_file_report_validates_project_present` | same | Missing Project raises |
| `test_file_report_validates_work_item_present` | same | Missing Work Item raises |
| `test_file_report_validates_recommended_commit_type_present` | hygiene-bundle Change B | Missing Recommended commit type raises |
| `test_file_report_validates_prior_deliberations_section_present` | codex-review-gate Prior Deliberations | Section present + 5 fields present passes |
| `test_file_report_validates_prior_deliberations_opt_out_present` | same | Section absent but `_No prior deliberations: <reason>._` line present passes |
| `test_file_report_validates_prior_deliberations_missing_no_opt_out` | same | Section absent AND opt-out absent raises |
| `test_file_report_preserves_draft_mtime_when_content_path_supplied` | S363 mtime artifact | file_report(content_path=src) produces live file with mtime equal to src.stat().st_mtime |
| `test_file_report_does_not_alter_mtime_when_content_supplied_directly` | S363 | file_report(content=str) produces live file with natural write-time mtime |

(Note: the 13-row table above includes 12 distinct test cases — the first three are F3 anchor coverage; the next 6 are structural-field coverage; the next 3 are Prior Deliberations coverage; the last 2 are mtime coverage.)

## Acceptance Criteria

- All 12 new tests pass.
- All existing tests in `platform_tests/skills/test_bridge_impl_report_helper.py` continue to pass (with the existing fixture updated to include the now-required fields).
- `file_report()` rejects missing-bridge_kind content with an explicit error.
- `file_report()` rejects non-`implementation_report` bridge_kind values with an explicit error.
- `file_report()` rejects implementation_report content that omits any of 5 required headers OR `## Prior Deliberations` section (without opt-out).
- `file_report()` preserves source draft mtime on the live file when `content_path` is supplied.
- The template counterpart at `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` has the same changes.
- Lint, type, and format checks pass on the touched files.

## Risk and Rollback

Risk surface: any active in-flight implementation report being authored by a parallel session against the relaxed contract would fail to file after this lands. Per Codex F3 critique, this is the desired outcome — failing closed against exactly the same structural defects Codex catches in review. Mitigation: validation messages name the specific missing fields so authors immediately know how to correct.

Risk to the existing test suite: the current fixture lacks `bridge_kind: implementation_report`. Without updating the fixture as part of this change, all 9 existing tests would fail. The fix is part of this proposal (item 5 in the Implementation Plan); test changes are atomic with the helper changes in a single PR.

Rollback: a single-revert commit on the three target files restores prior behavior. The new tests fail open in that case; they would be revised or deleted as part of the revert.

Compatibility: no public API changes; `file_report()` signature unchanged. The validation runs for ALL content (not gated on author-supplied marker per F3 fix); non-implementation_report kinds are explicitly rejected rather than silently bypassing validation.

## Loyal Opposition Asks

1. Confirm the bridge-kind gate's two reject paths (missing bridge_kind / wrong bridge_kind value) match the helper's intended semantic. Should missing `bridge_kind:` be normalized to `implementation_report` rather than rejected, given `file_report()` IS the report writer? Either choice is defensible; the reject design is more explicit but the normalize design is more author-friendly.
2. Confirm the existing fixture update approach (modify `_completed_report()` in place rather than add a new fixture) is the right test-suite strategy. Alternative: keep the existing fixture as a "malformed report" negative-case and add a new `_completed_compliant_report()` for positive-case coverage.
3. Confirm the inclusion of the template counterpart `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` in target_paths is the right scope. Or should template changes be a separate slice?
4. Confirm the `os.utime` placement (between live_path.write_text and the INDEX-update block at lines 436-447) does not interfere with the existing best-effort archival-trim call at lines 449-459.
5. Verify the bridge-kind detection regex tolerates both `bridge_kind: implementation_report` (no leading whitespace) and indented forms — if any caller indents bridge_kind, the simple multiline regex would miss it.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
