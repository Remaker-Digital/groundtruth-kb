REVISED

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 (hook + verifier + tests + formal artifacts) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-gov-code-quality-baseline-slice-2
Version: 003
Responds to: bridge/gtkb-gov-code-quality-baseline-slice-2-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py", "scripts/check_code_quality_baseline_parity.py", "platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py", "platform_tests/scripts/test_check_code_quality_baseline_parity.py", ".groundtruth/formal-artifact-approvals/2026-05-14-gov-code-quality-baseline-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-adr-code-quality-baseline-as-default-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-spec-code-quality-checklist-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-dcl-code-quality-waiver-lifecycle-001.json", "groundtruth.db"]

## Claim

This REVISED-1 restores Slice 2 to the scope approved at the parent `gtkb-gov-code-quality-baseline-slice1-006` GO and the `memory/work_list.md` row 7 outcome statement. Four findings raised by `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` are addressed:

- F1 (formal artifacts in Slice 2 scope): Adds IP-4 and IP-5 to insert all four formal artifact records under the formal-artifact-approval ceremony (`GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`). Each approval-packet target path is enumerated in `target_paths`. No deferral remains.
- F2 (Tier 1 hook scope completeness): IP-1 is rewritten to implement the full Slice 1 §8.1 table contract: heading presence, table presence, exact-header-row column set, all 9 canonical `CQ-*-001` rule IDs with no unknown IDs, per-row well-formedness (`Yes`/`N/A`/waiver-ref), non-empty plan and verification for `Yes`, non-empty reason for `N/A`, live non-expired KB resolution for waiver rows, and vague-phrase rejection.
- F3 (regression test coverage): IP-3 is rewritten to spec-derive tests for all 8 Slice 1 §8.5 Tier-1 cases (missing section, invalid rule ID, empty `Yes` plan, empty `Yes` verification, `N/A` without reason, vague phrasing, expired waiver, compliant proposal) plus the 3 Tier-3 parity-script cases, totaling 11 cases.
- F4 (Tier 3 canonical rule coverage): IP-2 enumerates all 9 canonical rule IDs and classifies each as Tier 3 mechanical (SECRETS, PATHS, CONSTANTS-non-obvious, COMPLEXITY-radon) or Tier 2 judgment-only (DOCS, TESTS, LOGGING, SECURITY, VERIFICATION). Each Tier 3 scan is bound to a named test.

Tier 1 (proposal-time mechanical), Tier 2 (Loyal Opposition judgment, preserved), and Tier 3 (post-impl source/diff scan) are implemented as Slice 1 §8 directs.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. No `applications/` paths. No Agent Red paths.

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\hooks\code_quality_baseline_proposal_check.py`
- `E:\GT-KB\scripts\check_code_quality_baseline_parity.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_code_quality_baseline_proposal_check.py`
- `E:\GT-KB\platform_tests\scripts\test_check_code_quality_baseline_parity.py`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-gov-code-quality-baseline-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-adr-code-quality-baseline-as-default-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-spec-code-quality-checklist-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-dcl-code-quality-waiver-lifecycle-001.json`
- `E:\GT-KB\groundtruth.db`
- Bridge file at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-slice-2-003.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert the REVISED-1 entry at the top of this thread's version list; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited in this flat list.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below in Specification-Derived Verification Plan.
- `GOV-STANDING-BACKLOG-001` - single tracking work_item; not a bulk operation per `## Clause Scope Clarification` below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the four formal artifact records carry the rule set the hook enforces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - hook + parity script + four MemBase records are durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook gates proposal lifecycle; verifier gates VERIFIED.
- `GOV-ARTIFACT-APPROVAL-001` - the four formal artifact insertions follow the formal-artifact-approval ceremony.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder approval-packet authoring discipline.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - the approval-gate hook governs the four MemBase inserts.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract for approval-packet validation.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative proposal (§4 rule set; §8.1 Tier 1 contract; §8.5 test matrix).
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - Codex Slice 1 GO authorizing Slice 2.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` - Codex NO-GO this REVISED-1 responds to.
- `memory/work_list.md` row 7 - Slice 2 required outcome statement.

## Prior Deliberations

- `DELIB-1117` - parent `gtkb-gov-code-quality-baseline-slice1` thread reached GO at -006; this Slice 2 is the authorized follow-on.
- `DELIB-0946` - Slice 1 GO review; authorized "hook/verifier/tests/formal artifacts" scope with formal-artifact-approval ceremony required for GOV/ADR/SPEC/DCL insertion.
- `DELIB-0948` - Slice 1 NO-GO (earlier round) preserved the Tier 2/Tier 3 overreach hazard; the Slice 1 -005/-006 chain resolved it via the three-tier split this Slice 2 implements faithfully.
- `DELIB-0947` - earlier Slice 1 NO-GO context; this REVISED-1 keeps the Tier 1 / Tier 2 separation that resolution required.
- `DELIB-1132` - `gtkb-gov-proposal-standards-slice1` (10 versions, VERIFIED); precedent for the upstream-routed proposal-standards-hook pattern this thread augments.

## Owner Decisions / Input

- 2026-05-14 UTC, S350, AskUserQuestion: owner Mike (michaelpalmeter@outlook.com) selected "Parallel research + serialized Writes now (Recommended)" authorizing this REVISED filing as part of the in-flight bridge batch. This is the operative owner-decision input for filing this REVISED.
- 2026-05-14 UTC, S350: prior owner directive "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" established the Slice-N proposal batch this filing belongs to.
- 2026-05-14 UTC, S350: owner directive "Proceed with all identified work" authorizes follow-through on Codex NO-GO findings.
- No new owner decision is required for the formal-artifact-approval ceremony itself; the formal-artifact-approval-gate hook validates each insertion against a per-artifact approval packet at write time per `GOV-ARTIFACT-APPROVAL-001`. Each of the four packets will be authored at implementation time with owner-confirmed verbatim content.
- DECISION-0572 is a different thread and does not apply here.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) authorization; the four formal artifact contents are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4; the formal-artifact-approval ceremony for inserting them is governed by `GOV-ARTIFACT-APPROVAL-001`.

## Clause Scope Clarification (Not a Bulk Operation)

This Slice 2 is not a bulk operation. It inserts one tracking `work_items` row and four formal artifact records, each via singleton MemBase insertion gated by a per-artifact formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json`. There is no batch loop, no bulk-update path, and no shared transaction across artifacts. Each MemBase insert is independently approval-gated, independently versioned, and independently rollback-able. The formal-artifact-approval hook (`.claude/hooks/formal-artifact-approval-gate.py`) validates per-insert. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not require bulk-operation evidence beyond the explicit per-insert pattern documented here.

## Proposed Scope

### IP-1: Tier-1 mechanical proposal-time hook

In `groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py`:

- PreToolUse hook entry point for `Write`/`Edit` of `bridge/*.md` files whose first 1 KiB contains the `bridge_kind: implementation_proposal` header. Verdict files (lines starting with `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`) and non-implementation bridge files are skipped.
- Tier-1 mechanical checks per `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §8.1:
  - Heading presence: the proposal contains a level-2 `## Code Quality Baseline` heading.
  - Table presence: the first markdown table after the heading is well-formed (header row, separator row, data rows).
  - Exact header row: columns are `Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason` in that order.
  - Canonical rule-ID coverage: all 9 IDs from Slice 1 §4 appear exactly once (`CQ-SECRETS-001`, `CQ-PATHS-001`, `CQ-CONSTANTS-001`, `CQ-DOCS-001`, `CQ-COMPLEXITY-001`, `CQ-TESTS-001`, `CQ-LOGGING-001`, `CQ-SECURITY-001`, `CQ-VERIFICATION-001`); no unknown `CQ-*` IDs; no duplicates.
  - Applies? cell value: value in `{"Yes", "N/A"}` or a waiver-reference of the form `Owner waiver: CQ-<TOPIC>-NNN - <DELIB-ID> - <reason>`.
  - `Yes` row completeness: `Compliance plan` and `Verification` cells are non-empty after whitespace strip.
  - `N/A` row completeness: `Waiver / N/A reason` cell is non-empty after whitespace strip.
  - Waiver-row resolution: for each waiver-reference, a read-only MemBase query confirms the cited waiver record exists, is the latest version, and has `expires_at` either NULL or strictly after `today` (UTC). Hook fails closed if MemBase is unreachable.
  - Vague-phrase rejection: `Compliance plan` and `Verification` cells reject the phrase list `{"will be careful", "best effort", "trivial", "obvious", "tested manually", "TBD", "to be determined", "pending", "???"}` (case-insensitive substring match).
- Hook output: `{"decision": "block", "reason": "<finding>"}` on any failure; `{}` on pass. Always exits 0 per hook protocol.

### IP-2: Tier-3 post-implementation parity verifier

In `scripts/check_code_quality_baseline_parity.py`:

- CLI: `python scripts/check_code_quality_baseline_parity.py --since <commit-sha>` runs source/diff scan against the diff between HEAD and the cited baseline commit.
- The 9 canonical rule IDs are classified for Tier 3 coverage as follows:
  - Tier 3 mechanical (scanned by this script):
    - `CQ-SECRETS-001` - reuses the existing credential-scan hook patterns; flags new secret-shaped tokens.
    - `CQ-PATHS-001` - regex scan for machine-specific absolute path literals (`C:\`, `/Users/`, `/home/`, `\\?\` UNC prefix) in source/config diff.
    - `CQ-CONSTANTS-001` - flags new numeric/string literals in non-test files that match the §4.2 non-obvious categories AND lack an adjacent or same-line comment; exempts the §4.2 self-evident-exemption list.
    - `CQ-COMPLEXITY-001` - runs `radon cc` against Python files in the diff; flags new functions with cyclomatic complexity over the §4.1 threshold (LOC >= 50 OR cc >= 10) that lack a `# CQ-COMPLEXITY-001 rationale:` inline comment.
  - Tier 2 judgment-only (not scanned):
    - `CQ-DOCS-001` (intent vs. mechanical-restatement is reviewer judgment).
    - `CQ-TESTS-001` (risk proportion is reviewer judgment).
    - `CQ-LOGGING-001` (actionability is reviewer judgment).
    - `CQ-SECURITY-001` (control adequacy is reviewer judgment).
    - `CQ-VERIFICATION-001` (evidence-ladder level is reviewer judgment; Codex GO scrutiny per Slice 1 §8.2).
- Output: markdown-table violation report on stdout suitable for inclusion in post-impl reports. Exit code 0 = clean; 1 = violations present; 2 = invocation error.

### IP-3: Regression tests

`platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py` (Tier 1 cases per Slice 1 §8.5):

- `test_hook_allows_compliant_proposal` - asserts pass.
- `test_hook_blocks_missing_code_quality_baseline_section` - asserts block.
- `test_hook_blocks_invalid_rule_id` - asserts block on unknown `CQ-FOO-001`.
- `test_hook_blocks_empty_compliance_plan_for_yes_row` - asserts block.
- `test_hook_blocks_empty_verification_for_yes_row` - asserts block.
- `test_hook_blocks_na_row_without_reason` - asserts block.
- `test_hook_blocks_vague_phrasing` - asserts block on a literal-string-match vague-phrase example.
- `test_hook_blocks_expired_waiver_reference` - asserts block on waiver-ref to a KB record whose `expires_at` is past.
- `test_hook_skips_non_proposal_bridge_files` - asserts pass on verdict/advisory files.

`platform_tests/scripts/test_check_code_quality_baseline_parity.py` (Tier 3 cases):

- `test_parity_returns_zero_on_clean_diff` - exit 0.
- `test_parity_flags_secret_shape_token` - exit 1; CQ-SECRETS-001 violation reported.
- `test_parity_flags_hardcoded_absolute_path` - exit 1; CQ-PATHS-001 violation reported.
- `test_parity_flags_non_obvious_literal_without_comment` - exit 1; CQ-CONSTANTS-001 violation reported.
- `test_parity_flags_over_threshold_function_without_rationale` - exit 1; CQ-COMPLEXITY-001 violation reported (uses a small fixture file).

### IP-4: Formal-artifact approval packets and MemBase inserts

Under the `GOV-ARTIFACT-APPROVAL-001` ceremony, write four approval packets at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` and execute four singleton MemBase inserts (one per artifact). Each packet records `artifact_id`, `artifact_type`, `body_hash`, owner approval evidence, and the `change_reason`. The formal-artifact-approval-gate hook (`.claude/hooks/formal-artifact-approval-gate.py`) validates the packet per insert.

- `GOV-CODE-QUALITY-BASELINE-001` (type `governance`): bound to `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3.1 verbatim text.
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` (type `architecture_decision`): bound to §3.2 verbatim text.
- `SPEC-CODE-QUALITY-CHECKLIST-001` (type `specification`): bound to §3.3 + §4 (the 9-rule table) + §4.1-§4.4 acceptance criteria.
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` (type `design_constraint`): bound to §3.4 + §5 six-field waiver shape.

### IP-5: Tracking work_item

One `work_items` row: `origin='new'`, `component='code-quality'`, `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'` (the insert above lands before this row), `resolution_status='open'`, `stage='implementing'`, `related_bridge_threads='gtkb-gov-code-quality-baseline-slice-2'`, `changed_by='prime-builder/claude/B'`, with explicit `change_reason` citing this bridge document.

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py -v` - all 9 Tier 1 hook cases PASS (derives from `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §8.5 Tier-1 rows and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`).
2. `python -m pytest platform_tests/scripts/test_check_code_quality_baseline_parity.py -v` - all 5 Tier 3 parity cases PASS (derives from §8.5 Tier-3 rows and IP-2's classification table).
3. `python -m ruff check groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py scripts/check_code_quality_baseline_parity.py` - zero errors (derives from `CQ-VERIFICATION-001` Level-2 static check).
4. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` - `preflight_passed: true`; `missing_required_specs: []` (derives from `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and the Mandatory Applicability Preflight Gate in `.claude/rules/file-bridge-protocol.md`).
5. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` - exit 0; no blocking gaps (derives from the same gate).
6. End-to-end smoke: invoke the Tier-1 hook against a well-formed Code Quality Baseline-bearing proposal (fixture file) and assert allow; invoke against a fixture missing the section and assert block (derives from §8.5).
7. End-to-end smoke: invoke `check_code_quality_baseline_parity.py --since <HEAD~1>` against a fixture diff with one of each Tier-3 violation and assert exit 1 (derives from §8.5 Tier-3 rows).
8. MemBase `python -m groundtruth_kb specs get GOV-CODE-QUALITY-BASELINE-001 --json` returns one row; same for the ADR/SPEC/DCL companions; tracking `work_items` row present (derives from IP-4 + IP-5 + `GOV-ARTIFACT-APPROVAL-001`).
9. `python scripts/check_codex_hook_parity.py` - zero parity drift (derives from cross-harness enforcement of `ADR-CODEX-HOOK-PARITY-FALLBACK-001`).

## Risks and Rollback

- Risk: Tier 1 hook over-blocks legitimate proposals on edge-case table renderings (e.g., proposals that genuinely have an `N/A` row whose reason is one short sentence that the vague-phrase list might match). Mitigation: vague-phrase list is exact-substring, not heuristic; the list is owner-approvable via the waiver-lifecycle path; reviewers can issue an explicit `Owner waiver` line at Tier 2.
- Risk: MemBase query for waiver resolution adds latency to every Write of a bridge proposal. Mitigation: query is keyed on a small index (waiver-ID); hook caches per-process; failure-mode is fail-closed (block on MemBase unreachable) so no silent bypass.
- Risk: Tier 3 `radon` invocation fails on non-Python files or environments without `radon` installed. Mitigation: parity script feature-detects `radon`; absence yields a graceful skip with a warning in the violation report rather than exit 2; install line is documented in the script header.
- Risk: Formal-artifact approval packet for any of the four artifacts is rejected by the approval-gate hook. Mitigation: each packet is independent; rollback is per-artifact; failing one does not strand the other three or the hook/verifier work.
- Rollback: Revert all five source files (hook, parity script, two test files, and the four approval-packet JSON files); soft-delete (new-version with `resolution_status='retracted'`) the four MemBase records and the tracking `work_items` row; revert the INDEX entry.

## Sequenced Dependencies

1. Insert `GOV-CODE-QUALITY-BASELINE-001` via formal-artifact-approval (IP-4 step 1) before IP-5 so the tracking `work_items` row's `source_spec_id` resolves.
2. Insert `SPEC-CODE-QUALITY-CHECKLIST-001` (IP-4 step 3) before IP-1 hook implementation if the hook reads the canonical rule-ID list from MemBase at startup; the alternative is to embed the 9 IDs as a constant in the hook code, which is the choice made here (the hook's constant list is verified against `SPEC-CODE-QUALITY-CHECKLIST-001` content as a Tier 3 smoke test in IP-3).
3. IP-1 hook lands before IP-2 parity script so the Tier-1 / Tier-3 separation is enforceable.
4. IP-3 tests land alongside the artifacts they test.
5. Slice 1 GO at `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` is the parent dependency; that GO authorizes the entire Slice 2 scope including the four formal artifacts per the Slice 1 §3 contract.

## Recommended Commit Type

`feat:` - net-new Tier-1 hook module, net-new Tier-3 parity script, net-new test files, and four net-new formal-artifact records in MemBase. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B / S333 audit discipline: this is unambiguously a new-capability commit (the Code Quality Baseline governance subsystem); `chore:` or `refactor:` would be inaccurate.

## Bridge-Compliance Self-Check

- `## Specification Links` is a plain heading with a flat bullet list and no `###` sub-headings.
- `## Prior Deliberations` cites five DELIB IDs returned by deliberation search.
- `## Owner Decisions / Input` is non-empty, substantive, and cites the session-S350 AUQ owner-direction "Parallel research + serialized Writes now (Recommended)"; no placeholder text.
- `target_paths` is a JSON list; all entries in-root under `E:\GT-KB`.
- `## Requirement Sufficiency` has exactly one operative state (`Existing requirements sufficient`).
- `## Clause Scope Clarification (Not a Bulk Operation)` is present and cites `formal-artifact-approval` and `singleton MemBase insertion`.
- `## Recommended Commit Type` is present with a `feat:` choice and diff-stat justification.
- `## In-Root Placement Evidence` enumerates every target path with backtick confirmation.
- F1/F2/F3/F4 from `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` are addressed in the `## Claim` section and IPs.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
