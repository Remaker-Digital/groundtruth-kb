NEW

# Post-Implementation Report - W4 Enforcement Calibration: Five Mechanical Bridge-Gate Fixes (GTKB-GOVERNANCE-CORRECTION-S358-W4)

bridge_kind: implementation_report
Document: gtkb-s358-w4-enforcement-calibration
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3368

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "config/governance/adr-dcl-clauses.toml", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/**", "platform_tests/hooks/**"]

## Summary

This post-implementation report covers the implementation of the operative proposal `bridge/gtkb-s358-w4-enforcement-calibration-005.md` (Codex GO at `-006`): five mechanical bridge-gate false-positive calibrations (IP-1 through IP-5) plus the IP-6 regression and preservation test cluster.

Implementation-start authorization: a packet was generated from the live `-006` GO via `python scripts/implementation_authorization.py begin --bridge-id gtkb-s358-w4-enforcement-calibration` (packet_hash `sha256:558fe1b49f4a0ce0581b5bbcc5eb2e5558bb8d5ccd9821feeb28094e7619d2ec`, derived from `go_file: bridge/gtkb-s358-w4-enforcement-calibration-006.md`).

All five fixes are in the working tree, all IP-6 tests pass, the live bridge-compliance-gate hook and its scaffold template remain byte-identical, and `ruff` is clean over every changed file. One pre-existing unrelated test failure inside the proposal's verification command is disclosed below and is owner-waived for this verdict per `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER`.

## Implementation Status By IP

IP-1 and IP-2 were found already present as uncommitted working-tree changes at the start of this session, byte-exact to the `-005` proposal's IP-1/IP-2 scope (made by a prior/parallel session). They were verified by inspection against the proposal text and `git diff`; this session applied no further change to `scripts/bridge_applicability_preflight.py`, `scripts/adr_dcl_clause_preflight.py`, or `config/governance/adr-dcl-clauses.toml`. IP-3, IP-4, IP-5, and IP-6 were implemented by this session.

- IP-1 (verified pre-existing): `PATH_TOKEN_RE` in `scripts/bridge_applicability_preflight.py` is the anchored enumerated-repo-directory pattern, byte-equal to the pattern in `scripts/implementation_start_gate.py`. Prose `word/word` tokens no longer harvest as repository paths; declared `target_paths` and repo-rooted path mentions still harvest.
- IP-2 (verified pre-existing): `config/governance/adr-dcl-clauses.toml` CLAUSE-VISIBILITY-BULK-OPS `applies_when_content` no longer contains the bare `work[- ]item` alternative; `scripts/adr_dcl_clause_preflight.py` `evaluate_applicability` promotes to `must_apply` only on `triggers_hit == triggers_total` (the `content_hit and triggers_hit >= 1` single-content-hit branch was removed, demoting that case to `may_apply`).
- IP-3 (this session): `.claude/hooks/bridge-compliance-gate.py` and the byte-identical scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` gained `SPEC_LINK_HEADING_NEAR_MISS_RE`, `_specification_links_heading_misdetected()`, and `_ask_reason_for_content()`. The `_deny_reason_for_content` Specification-Links branch is now guarded by `not _specification_links_heading_misdetected(content)`; `main()` routes a heading-format misdetection to `emit_ask` rather than `emit_deny`. A genuinely absent section, and a placeholder-content section, still `deny`.
- IP-4 (this session): `scripts/implementation_start_gate.py` `MUTATING_COMMAND_RE` no longer carries the regex redirect alternative `(?<![:>-])>{1,2}(?![>&=])`. Redirect detection is now `_shell_redirect_present()`, a punctuation-aware `shlex` token scan that recognizes a redirect operator only as a standalone token; `_has_mutating_signal()` combines the named-command regex with the token scan; `_is_mutating_command()` and `_all_mutating_signal_is_null_sink_redirect()` consume `_has_mutating_signal()`. A `>` inside a quoted argument or embedded Python expression is no longer misread as a redirect; a parse failure falls back conservatively to non-redirect.
- IP-5 (this session): `.claude/hooks/bridge-compliance-gate.py` and its byte-identical template `_has_concrete_spec_links()` now evaluates the placeholder check per line - a line carrying a genuine `SPEC_LINK_TOKEN_RE` citation token is exempt, so a placeholder-vocabulary word in citation-rationale prose no longer rejects the section. The whole-section `SPEC_PLACEHOLDER_RE` was replaced with the per-line-anchored `SPEC_PLACEHOLDER_LINE_RE`. The requirement that the section carry at least one `SPEC_LINK_TOKEN_RE` match is retained; a placeholder-only section is still rejected.
- IP-6 (this session): regression and preservation tests were added - `platform_tests/scripts/test_bridge_applicability_preflight.py` (+2 fix-1 tests), `platform_tests/scripts/test_adr_dcl_clause_preflight.py` (+2 fix-2 tests), `platform_tests/scripts/test_implementation_start_gate.py` (+2 fix-4 tests), and a new module `platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py` (4 fix-3 and fix-5 tests). One cluster per fix, each covering both the false-positive-removed path and the genuine-positive-preserved path.

The live `.claude/hooks/bridge-compliance-gate.py` and the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` remain byte-identical after the IP-3 and IP-5 edits - confirmed PASS by `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence`.

## In-Root Placement Evidence

All changed files are in-root under `E:\GT-KB`: `scripts/`, `config/governance/`, `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, `platform_tests/scripts/`, and `platform_tests/hooks/`. No `applications/` path is touched. This bridge file resides under `E:\GT-KB\bridge\`. No target path or output path is outside the GT-KB project root.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and bridge verdict files are canonical workflow state; preflight and gate surfaces that false-positive obstruct that canonical workflow. Direct governing authority for keeping the bridge mechanical gates correct.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - the applicability preflight calibrated by W4 fix 1 is the mechanical enforcer of this DCL; calibrating it keeps the enforcer aligned with the requirement it serves. W4 fix 5 additionally calibrates `_has_concrete_spec_links` in the bridge-compliance gate - the write-time enforcer of this DCL - so it accepts a relevance-complete Specification Links section instead of rejecting one whose rationale prose contains a placeholder-vocabulary word. This report also carries concrete specification links per the DCL.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the clause preflight calibrated by W4 fix 2 is the mechanical enforcer of this DCL; this report carries the spec-to-test mapping and executed-test evidence below.
- DCL-SPEC-RELEVANCE-CLOSURE-001 - bridge proposal spec linkage must be relevance-complete, not just non-empty. W4 fix 1 modifies `scripts/bridge_applicability_preflight.py`, the mechanical surface that enforces this DCL, and W4's target paths include `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. IP-1's anchoring removes phantom-path-driven spurious required-spec demands without weakening genuine relevance closure: declared target paths and repo-rooted path mentions still harvest, so every genuine path-keyed spec still triggers; the preflight stays a mechanical floor and reviewer relevance judgment stays the ceiling.
- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 - all directives must be mechanically enforced, not documentation-only. W4 changes mechanical enforcement classifications (IP-2 demotes single-content-hit promotion to `may_apply`; IP-3 downgrades heading-misdetection from `deny` to `ask`; IP-5 narrows a placeholder-content check). W4 preserves hard mechanical enforcement for genuine violations: IP-2 keeps full-trigger satisfaction at `must_apply`, IP-3 keeps genuinely-absent and placeholder sections at `deny`, IP-5 keeps a placeholder-only Specification Links section rejected, and the IP-6 preservation tests assert each genuine-positive path still blocks.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance-gate (fixes 3 and 5) and the implementation-start gate (fix 4) participate in the deterministic AUQ policy engine; the calibration keeps these surfaces deterministic and correctly scoped.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - all five fixes are deterministic (anchored regex, narrowed TOML trigger, deny-to-ask disposition change, shlex token parse, per-line placeholder evaluation); no fix introduces an LLM classifier.
- GOV-STANDING-BACKLOG-001 - W4 fix 2 calibrates the GOV-STANDING-BACKLOG-001 / CLAUSE-VISIBILITY-BULK-OPS clause so it fires on genuine bulk standing-backlog operations rather than on the bare phrase "work item".
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root under `E:\GT-KB`; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the defects and fixes are preserved as durable artifacts (WI-3368, the proposal chain, the regression tests, this post-implementation report).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3368 moves through open, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search for bridge-gate calibration and the W4 verification was performed. Relevant records:

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing the combined S358 governance-correction project, with W4 enforcement calibration sequenced first.
- DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER - the owner-decision deliberation (this session, 2026-05-18) recording the owner waiver of the pre-existing `test_non_go_bridge_entry_cannot_create_authorization` failure for this W4 VERIFIED verdict. See the Owner Decisions / Input section.
- DELIB-1851 - a prior Loyal Opposition NO-GO for ADR-evaluation enforcement scoping, cited in the `-002` review; it first flagged missing spec-coverage governance including DCL-SPEC-RELEVANCE-CLOSURE-001 for proposal-time applicability work.

No prior deliberation rejected or already addressed these five calibrations.

## Specification-Derived Verification

Commands executed (from `E:\GT-KB`, `python` = Python 3.14 with `groundtruth_kb` importable and `pytest` 9.0.2):

1. `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -v` - observed: 151 passed, 1 failed. The single failure is the pre-existing, unrelated `test_non_go_bridge_entry_cannot_create_authorization` (see Pre-Existing Failure Disclosure + Owner Decisions / Input). Every W4 IP-6 test and every W4 regression test passed.
2. `python -m pytest groundtruth-kb/tests/test_governance_hooks.py -q` - observed: 56 passed. The IP-3/IP-5 scaffold-template edits did not break the framework hook suite.
3. `python -m ruff check scripts/implementation_start_gate.py .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py` - observed: All checks passed.

Spec-to-test mapping (every row observed PASS):

| Specification | Behavior verified | Test | Observed |
|---|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Prose word/word tokens do not harvest as applicability paths | test_preflight_prose_slash_not_harvested | PASS |
| DCL-SPEC-RELEVANCE-CLOSURE-001 | Declared target_paths + repo-rooted path mentions still harvest (relevance closure preserved) | test_preflight_declared_and_rooted_paths_still_harvested | PASS |
| GOV-STANDING-BACKLOG-001 | A proposal mentioning only "work item" yields may_apply, not must_apply | test_clause_work_item_phrase_is_advisory | PASS |
| GOV-STANDING-BACKLOG-001 | A genuine bulk-transition standing-backlog proposal still yields must_apply | test_clause_genuine_bulk_op_still_must_apply | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | A heading-format ambiguity yields ask, not deny | test_compliance_gate_heading_ambiguity_asks | PASS |
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | A genuinely absent Specification Links section still yields deny | test_compliance_gate_absent_section_still_denies | PASS |
| SPEC-AUQ-POLICY-ENGINE-001 | A command containing a Python > operator is not flagged mutating | test_impl_start_gate_python_operator_not_mutating | PASS |
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | A genuine shell redirect and named-command mutations are still flagged mutating | test_impl_start_gate_genuine_redirect_still_mutating | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | A Specification Links section with genuine citations passes despite a placeholder word in rationale prose | test_compliance_gate_concrete_links_with_placeholder_word_passes | PASS |
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | A placeholder-only Specification Links section with no genuine citation is still rejected | test_compliance_gate_placeholder_only_section_still_rejected | PASS |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | All five calibrations are deterministic; no LLM classifier is introduced | full IP-6 cluster (10 tests, deterministic fixtures) | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Each fix carries a false-positive-removed AND a genuine-positive-preserved test | full IP-6 cluster (10 tests) | PASS |

Regression preservation (no W4 change broke an existing test): the existing redirect/operator regression tests for `implementation_start_gate.py` (the WI-3317, WI-3356, WI-3357 clusters) all pass under IP-4's shlex-token redirect detection; the existing `bridge-compliance-gate` regression files `test_bridge_compliance_gate_hard_block_workspace.py` and `test_bridge_compliance_gate_spec_test_heading.py` (live + template parametrized) all pass under IP-3/IP-5; and the framework suite `groundtruth-kb/tests/test_governance_hooks.py` passes 56/56.

## Pre-Existing Failure Disclosure

A broader run, `python -m pytest platform_tests/scripts/ platform_tests/hooks/ -q`, reported 11 failures, 401 passed. All 11 are in code W4 does not touch:

- `test_non_go_bridge_entry_cannot_create_authorization` (in `platform_tests/scripts/test_implementation_start_gate.py`) - the only failure inside the proposal's `-k "preflight or clause or compliance_gate or implementation_start_gate"` verification command. Proven pre-existing: at HEAD the test (`:177`) expects `pytest.raises(match="latest GO")`, while HEAD `scripts/implementation_authorization.py:339` raises `"Implementation authorization requires a GO in the bridge chain; found latest status <status>"` - a literal-string mismatch (test/code drift). `scripts/implementation_authorization.py` is NOT in W4's target_paths and W4 does not modify it. Owner-waived for this verdict (see Owner Decisions / Input).
- 10 failures outside the `-k` verification command: `test_glossary_expansion.py` (5), `test_narrative_artifact_approval.py` (4), `test_credential_scan.py::test_docstring_inventory_covers_repo` (1, references a missing `src/multi_tenant/auth.py`). These exercise the glossary-expansion hook, the narrative-artifact-approval gate, and the credential-scan inventory respectively - none modified by W4. They are pre-existing failures / parallel-session working-tree contamination (the working tree carries many uncommitted changes from other in-flight sessions).

These failures should be captured as separate `PROJECT-GTKB-RELIABILITY-FIXES` work items; they are out of scope for W4 (GOV-07 record-defects-as-WIs; scoped-commit discipline).

## Owner Decisions / Input

- 2026-05-18, S358: the owner directed implementing W4 now, selected via AskUserQuestion. The combined-project authorization and the W4-first sequencing are recorded in `DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` and `PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION` (active, includes WI-3368).
- 2026-05-18, S358: after W4 verification, Prime Builder surfaced via AskUserQuestion that one pre-existing test failure, `test_non_go_bridge_entry_cannot_create_authorization`, falls inside the proposal's `-k` verification command. The owner was offered three options - (1) disclose and let Codex rule, (2) owner waiver now, (3) fix it inside W4 - and chose option 2, "Owner waiver now". The decision is archived as `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER` (`source_type=owner_conversation`, `outcome=owner_decision`).

Owner waiver: `test_non_go_bridge_entry_cannot_create_authorization` is owner-waived for this W4 VERIFIED verdict per `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER`. The waiver is scoped to this verdict only; it does not waive any commit-gate check. The test remains red and is to be repaired under a separate `PROJECT-GTKB-RELIABILITY-FIXES` work item. The failure is provably pre-existing and unrelated to W4 (evidence in Pre-Existing Failure Disclosure).

No further owner decision is pending.

## Clause Scope Clarification (Not a Bulk Operation)

This report is not a bulk standing-backlog operation. It is the post-implementation report for a five-fix mechanical calibration tracked by exactly one work item, WI-3368, an active member of PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 under the cited project authorization. No work-item state inventory, bulk transition, or backlog cleanup is performed. The report references the phrase "work item" and "standing backlog" only to describe W4 fix 2, which recalibrates the CLAUSE-VISIBILITY-BULK-OPS clause itself. The owner waiver above is captured through the formal-artifact-approval-class deliberation `DELIB-S358-W4-PREEXISTING-TEST-FAILURE-WAIVER`.

## Acceptance Criteria

- IP-1 through IP-6 landed - MET (IP-1/IP-2 verified pre-existing; IP-3/IP-4/IP-5/IP-6 implemented this session).
- The applicability preflight no longer harvests prose `word/word` tokens as paths; declared and repo-rooted paths still harvest - MET (test_preflight_prose_slash_not_harvested, test_preflight_declared_and_rooted_paths_still_harvested).
- CLAUSE-VISIBILITY-BULK-OPS no longer fires `must_apply` on the bare phrase "work item"; genuine bulk operations still trigger it - MET (test_clause_work_item_phrase_is_advisory, test_clause_genuine_bulk_op_still_must_apply).
- A heading-format ambiguity yields `ask`; genuinely missing or placeholder sections still yield `deny` - MET (test_compliance_gate_heading_ambiguity_asks, test_compliance_gate_absent_section_still_denies, test_compliance_gate_placeholder_only_section_still_rejected).
- `MUTATING_COMMAND_RE` no longer false-positives on Python `>` operators; genuine redirects and named-command mutations still flag - MET (test_impl_start_gate_python_operator_not_mutating, test_impl_start_gate_genuine_redirect_still_mutating, plus the preserved WI-3317/3356/3357 clusters).
- `_has_concrete_spec_links` accepts a Specification Links section carrying genuine citation tokens even when a rationale contains a placeholder-vocabulary word; a placeholder-only section still fails - MET (test_compliance_gate_concrete_links_with_placeholder_word_passes, test_compliance_gate_placeholder_only_section_still_rejected).
- The live `bridge-compliance-gate.py` and its scaffold-template copy remain byte-identical - MET (test_hook_matches_template_or_documented_divergence PASS).
- The IP-6 test clusters pass; existing preflight/gate regression tests still pass; `ruff` is clean over the changed files - MET, with one disclosed, owner-waived exception: the pre-existing unrelated `test_non_go_bridge_entry_cannot_create_authorization` (see Pre-Existing Failure Disclosure + Owner Decisions / Input).
- Both bridge preflights pass on this post-implementation report - to be confirmed by the filing helper and the Codex verdict.

## Files Changed

- `scripts/bridge_applicability_preflight.py` - IP-1 (verified pre-existing; uncommitted at session start).
- `config/governance/adr-dcl-clauses.toml` - IP-2 (verified pre-existing; uncommitted at session start).
- `scripts/adr_dcl_clause_preflight.py` - IP-2 (verified pre-existing; uncommitted at session start).
- `.claude/hooks/bridge-compliance-gate.py` - IP-3 + IP-5 (this session).
- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - IP-3 + IP-5 (this session; byte-identical to the live hook).
- `scripts/implementation_start_gate.py` - IP-4 (this session).
- `platform_tests/scripts/test_bridge_applicability_preflight.py` - IP-6 fix-1 tests (this session).
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` - IP-6 fix-2 tests (this session).
- `platform_tests/scripts/test_implementation_start_gate.py` - IP-6 fix-4 tests (this session).
- `platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py` - new module, IP-6 fix-3 and fix-5 tests (this session).

## Risks / Rollback

- Risk: the shlex-based redirect detection (IP-4) mishandles an exotic command. Mitigation: `shlex` is the standard tokenizer; a parse failure falls back conservatively to non-redirect; the named-command alternatives are unchanged; all WI-3317/3356/3357 redirect/operator regression tests pass.
- Risk: the IP-3 deny-to-ask change lets a malformed proposal through on an owner confirmation. Mitigation: only the heading-format-misdetection class moves to `ask`; genuinely absent and placeholder sections still `deny` (test_compliance_gate_absent_section_still_denies, test_compliance_gate_placeholder_only_section_still_rejected).
- Risk: the IP-5 per-line placeholder change lets a placeholder-stubbed section through. Mitigation: a line is exempt only when it carries a genuine `SPEC_LINK_TOKEN_RE` token; the whole-section `SPEC_LINK_TOKEN_RE` requirement is retained; a placeholder-only section still fails.
- Rollback: each fix is self-contained text/regex change with no schema, configuration-data, or migration dependency. The four files changed by this session (`implementation_start_gate.py`, both `bridge-compliance-gate.py` copies, and the three/four test files) are independently revertible; reverting them restores the pre-W4 gate behavior.

## Recommended Commit Type

`fix` - all five changes repair false-positive behavior in mechanical bridge gates with no new capability surface. IP-3's deny-to-ask disposition, IP-4's shlex parser, and IP-5's per-line evaluation are internal corrections of existing predicates, not new public interfaces. The IP-6 additions are test coverage for those fixes.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
