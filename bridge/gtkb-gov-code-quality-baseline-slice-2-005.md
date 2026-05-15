REVISED

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 (hook + Tier-1 verifier + Tier-3 source scan + tests + formal artifacts) - REVISED-2

bridge_kind: implementation_proposal
Document: gtkb-gov-code-quality-baseline-slice-2
Version: 005
Responds to: bridge/gtkb-gov-code-quality-baseline-slice-2-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py", "groundtruth-kb/templates/hooks/code-quality-baseline-proposal-check.py", ".claude/hooks/code-quality-baseline-proposal-check.py", ".codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/templates/managed-artifacts.toml", "scripts/check_code_quality_baseline_parity.py", "scripts/check_code_quality_baseline_source_scan.py", "platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py", "platform_tests/scripts/test_check_code_quality_baseline_parity.py", "platform_tests/scripts/test_check_code_quality_baseline_source_scan.py", ".groundtruth/formal-artifact-approvals/2026-05-14-gov-code-quality-baseline-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-adr-code-quality-baseline-as-default-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-spec-code-quality-checklist-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-dcl-code-quality-waiver-lifecycle-001.json", "groundtruth.db"]

## Claim

This REVISED-2 closes both Codex `-004` findings while preserving every fix from REVISED-1.

- F1 (-004) closed — Codex/Windows fallback verifier restored to Tier 1. `scripts/check_code_quality_baseline_parity.py` is reverted to its parent Slice 1 §8.4 contract: a Tier 1 bridge-proposal table-contract scanner that statically reads `bridge/*.md` and applies the same 8 mechanical checks the hook performs. The previously-conflated Tier 3 source/diff scanner is split out into a separate script at `scripts/check_code_quality_baseline_source_scan.py`. Two distinct CLIs, two distinct test suites.
- F2 (-004) closed — Hook now has a full distribution and registration path. The proposal-time gate is delivered as (a) a Python logic module at `groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py`, (b) a managed template at `groundtruth-kb/templates/hooks/code-quality-baseline-proposal-check.py`, (c) an active Claude hook at `.claude/hooks/code-quality-baseline-proposal-check.py`, (d) a Codex `.cmd` shim at `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`, (e) PreToolUse `Write|Edit` registrations in `.claude/settings.json` and `.codex/hooks.json`, and (f) a `[[artifacts]]` entry in `groundtruth-kb/templates/managed-artifacts.toml`. This matches `bridge-compliance-gate` distribution precedent exactly.
- F1-F4 from `-002` preserved. Formal artifacts (IP-5), full Tier 1 §8.1 contract (IP-1), full §8.5 test matrix (IP-4), and all-9 canonical rule-ID Tier 3 classification (IP-3) are unchanged from REVISED-1.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. No `applications/` paths. No Agent Red paths.

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\hooks\code_quality_baseline_proposal_check.py`
- `E:\GT-KB\groundtruth-kb\templates\hooks\code-quality-baseline-proposal-check.py`
- `E:\GT-KB\.claude\hooks\code-quality-baseline-proposal-check.py`
- `E:\GT-KB\.codex\gtkb-hooks\code-quality-baseline-proposal-check.cmd`
- `E:\GT-KB\.claude\settings.json`
- `E:\GT-KB\.codex\hooks.json`
- `E:\GT-KB\groundtruth-kb\templates\managed-artifacts.toml`
- `E:\GT-KB\scripts\check_code_quality_baseline_parity.py`
- `E:\GT-KB\scripts\check_code_quality_baseline_source_scan.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_code_quality_baseline_proposal_check.py`
- `E:\GT-KB\platform_tests\scripts\test_check_code_quality_baseline_parity.py`
- `E:\GT-KB\platform_tests\scripts\test_check_code_quality_baseline_source_scan.py`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-gov-code-quality-baseline-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-adr-code-quality-baseline-as-default-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-spec-code-quality-checklist-001.json`
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-dcl-code-quality-waiver-lifecycle-001.json`
- `E:\GT-KB\groundtruth.db`
- Bridge file itself at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-slice-2-005.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this REVISED-2 entry inserts at the top of the `bridge/INDEX.md` version list for this thread; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited in this flat list.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in Specification-Derived Verification Plan.
- `GOV-STANDING-BACKLOG-001` - single tracking work_item; not a bulk operation per Clause Scope Clarification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the four formal artifacts carry the rule set the hook enforces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - hook + two scripts + four MemBase records are durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook gates proposal lifecycle; Tier 1 verifier gates release; Tier 3 source scan gates VERIFIED.
- `GOV-ARTIFACT-APPROVAL-001` - the four formal artifact insertions follow the formal-artifact-approval ceremony.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder approval-packet authoring discipline.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - the approval-gate hook governs the four MemBase inserts.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract for approval-packet validation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex `.cmd` shim plus `scripts/check_codex_hook_parity.py` clearance required for the new hook.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative (§3 verbatim artifact contents; §4 nine-rule table; §8.1 Tier 1 contract; §8.4 fallback verifier Tier-1-only scope; §8.5 test matrix).
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - Codex Slice 1 GO authorizing Slice 2 with formal-artifact-approval ceremony.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` - first Codex NO-GO; F1-F4 closed in REVISED-1 and remain closed here.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-004.md` - second Codex NO-GO; F1/F2 closed in this REVISED-2.
- `memory/work_list.md` row 7 - Slice 2 required outcome statement (insert four formal artifacts; extend hook/verifier/tests).

## Prior Deliberations

- `DELIB-1117` - compressed parent `gtkb-gov-code-quality-baseline-slice1` bridge thread; latest status GO at `-006`; authorizes this Slice 2 follow-on.
- `DELIB-0946` - Slice 1 GO review at `-006`; constrains Slice 2 to keep tier separation intact; requires formal-artifact-approval ceremony for GOV/ADR/SPEC/DCL insertion.
- `DELIB-0948` - earlier Slice 1 NO-GO; documents the Tier 2/Tier 3 overreach hazard this REVISED-2 again respects by separating the Tier 1 verifier from the Tier 3 source scanner.
- `DELIB-1132` - `gtkb-gov-proposal-standards-slice1` VERIFIED precedent for proposal-time hook + verifier + tests pattern this thread mirrors.
- `DELIB-1637` - Codex Bridge-Compliance-Gate Hook Parity REVISED-3 GO; precedent for the hook + `.cmd` shim + `check_codex_hook_parity.py` discipline this REVISED-2 adopts.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - S337 owner decision refreshing the Codex/Windows hook parity fallback stance; informs the dual-registration model.

## Owner Decisions / Input

- 2026-05-14 UTC, S350, owner directive: Mike (michaelpalmeter@outlook.com): "Please parallelize work and dispatch as many priority bridge items as possible." This authorizes the in-flight parallel-bridge batch under which this REVISED-2 is filed.
- 2026-05-14 UTC, S350, owner AskUserQuestion answer: Mike selected "Parallel research + serialized Writes now (Recommended)" for this batch; this REVISED-2 is filed as a serialized Write inside that parallel-research wave.
- 2026-05-14 UTC, S350, prior owner directive: Mike: "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - established the Slice-N proposal batch this thread is part of.
- 2026-05-14 UTC, S350, prior owner directive: Mike: "Proceed with all identified work" authorizes follow-through on each Codex NO-GO in this batch, including this `-004` finding cycle.
- No new owner decision required for the formal-artifact-approval ceremony itself. The formal-artifact-approval-gate hook (`.claude/hooks/formal-artifact-approval-gate.py`) validates each of the four artifact insertions against a per-artifact approval packet at write time per `GOV-ARTIFACT-APPROVAL-001`. The four verbatim artifact bodies are specified in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4 and were owner-approved at Slice 1 GO.
- No new owner decision required for the dual-distribution hook pattern. The Claude template + active hook + Codex `.cmd` shim + `managed-artifacts.toml` entry pattern follows the existing `bridge-compliance-gate` precedent (GO at `DELIB-1637`); no new policy.
- DECISION-0572 is a different thread and does not apply here.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) authorization for "hook/verifier/tests/formal artifacts" scope. The four formal artifact contents are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4. The formal-artifact-approval ceremony is governed by `GOV-ARTIFACT-APPROVAL-001`. The dual-distribution hook pattern is governed by `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

## Clause Scope Clarification (Not a Bulk Operation)

This Slice 2 is not a bulk operation. It inserts one tracking `work_items` row and four formal artifact records, each via singleton MemBase insertion gated by a per-artifact formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json`. The four approval packets form a finite per-artifact inventory; there is no batch loop, no bulk-update path, and no shared transaction across artifacts. Each MemBase insert is independently approval-gated, independently versioned, and independently rollback-able. The formal-artifact-approval-gate hook validates per-insert. The hook/script/test/registration changes are file-level edits, not MemBase mutations; they do not change the bulk-ops surface. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not require bulk-operation evidence beyond the explicit per-insert pattern documented here.

## Proposed Scope

### IP-1: Tier-1 mechanical proposal-time hook (with full distribution)

Logic module at `groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py`:

- Exposes a `main()` entry suitable for both `python -m groundtruth_kb.hooks.code_quality_baseline_proposal_check` invocation and direct script invocation.
- PreToolUse hook entry point for `Write`/`Edit` of `bridge/*.md` whose first 1 KiB contains `bridge_kind: implementation_proposal`. Verdict files (lines starting with `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`) and non-implementation bridge files are skipped.
- Tier 1 mechanical checks per `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §8.1: heading presence, table presence, exact header row columns, all 9 canonical `CQ-*-001` rule IDs with no unknown IDs, Applies? cell value validation, Yes-row completeness, N/A-row completeness, waiver-row resolution via read-only MemBase query, vague-phrase rejection.
- Output: `{"decision": "block", "reason": "<finding>"}` on failure; `{}` on pass. Always exits 0 per hook protocol.

Distribution and registration (closes F2 from `-004`):

- `groundtruth-kb/templates/hooks/code-quality-baseline-proposal-check.py` - canonical managed template.
- `.claude/hooks/code-quality-baseline-proposal-check.py` - active Claude-side hook copied from template by `gt project upgrade` / bootstrap.
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd` - Codex `.cmd` shim matching the `bridge-compliance-gate.cmd` pattern.
- `.claude/settings.json` - append the new hook to the existing PreToolUse `Write|Edit` matcher block.
- `.codex/hooks.json` - append the new hook `.cmd` to the existing PreToolUse `Write|Edit` block.
- `groundtruth-kb/templates/managed-artifacts.toml` - new `[[artifacts]]` block with `class = "hook"`, `id = "hook.code-quality-baseline-proposal-check"`, mapping template -> target, `ownership = "gt-kb-managed"`, `upgrade_policy = "overwrite"`.

### IP-2: Tier-1 fallback verifier (restored to Slice 1 §8.4 scope; closes F1 from -004)

In `scripts/check_code_quality_baseline_parity.py`:

- Scope: Tier 1 only. Statically analyzes `bridge/*.md` files (default: every NEW or REVISED entry in `bridge/INDEX.md`; optional `--since-tag <tag>` filters to bridge files added or modified since that release tag). Applies the same 8 Tier 1 mechanical checks the IP-1 hook performs, against each in-scope bridge proposal.
- Does NOT scan source code, does NOT take `--since <commit-sha>` of source diff. That is IP-3's responsibility.
- Runs in the release-candidate gate per Slice 1 §8.4.
- Output: markdown-table violation report on stdout. Exit 0 = clean; 1 = violations present; 2 = invocation error.

### IP-3: Tier-3 post-implementation source/diff scanner (separate script; closes F1 from -004)

In `scripts/check_code_quality_baseline_source_scan.py` (new, separate from IP-2):

- CLI: `python scripts/check_code_quality_baseline_source_scan.py --since <commit-sha>` runs source/diff scan against the diff between HEAD and the cited baseline commit.
- Classifies the 9 canonical rule IDs: Tier 3 mechanical (CQ-SECRETS-001, CQ-PATHS-001, CQ-CONSTANTS-001, CQ-COMPLEXITY-001) scanned by this script; Tier 2 judgment-only (CQ-DOCS-001, CQ-TESTS-001, CQ-LOGGING-001, CQ-SECURITY-001, CQ-VERIFICATION-001) not scanned.
- Output: markdown-table violation report. Exit 0 = clean; 1 = violations; 2 = invocation error.

### IP-4: Regression tests

Test files:
- `platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py` - 9 Tier 1 hook tests covering each §8.5 row.
- `platform_tests/scripts/test_check_code_quality_baseline_parity.py` - 9 Tier 1 fallback-verifier tests applied to bridge-file fixtures.
- `platform_tests/scripts/test_check_code_quality_baseline_source_scan.py` - 5 Tier 3 source-scan tests covering each Tier 3 mechanical rule + one clean-diff baseline.

### IP-5: Formal-artifact approval packets and MemBase inserts

Unchanged from REVISED-1. Under the `GOV-ARTIFACT-APPROVAL-001` ceremony, write four approval packets at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` and execute four singleton MemBase inserts: `GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`. Each packet is owner-approved at implementation time with verbatim content from `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3.

### IP-6: Tracking work_item

One `work_items` row: `origin='new'`, `component='code-quality'`, `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'` (inserted at IP-5 step 1 before this row), `resolution_status='open'`, `stage='implementing'`, `related_bridge_threads='gtkb-gov-code-quality-baseline-slice-2'`, `changed_by='prime-builder/claude/B'`, `change_reason` citing this bridge document.

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py -v` — all 9 Tier 1 hook tests PASS.
2. `python -m pytest platform_tests/scripts/test_check_code_quality_baseline_parity.py -v` — all 9 Tier 1 fallback-verifier tests PASS.
3. `python -m pytest platform_tests/scripts/test_check_code_quality_baseline_source_scan.py -v` — all 5 Tier 3 source-scan tests PASS.
4. `python -m ruff check groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py scripts/check_code_quality_baseline_parity.py scripts/check_code_quality_baseline_source_scan.py` — zero errors.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` — `preflight_passed: true`; `missing_required_specs: []`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` — exit 0; no blocking gaps.
7. `python scripts/check_codex_hook_parity.py --project-root .` — PASS; Codex-side `.cmd` shim is Windows-shell-portable and matches Claude-side registration.
8. End-to-end Claude smoke: trigger the registered PreToolUse hook against a fixture proposal lacking `## Code Quality Baseline`; observe `block` decision. Then attempt with a compliant fixture; observe allow.
9. End-to-end Codex smoke: invoke `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd` against the same fixtures; identical verdicts.
10. MemBase `python -m groundtruth_kb specs get GOV-CODE-QUALITY-BASELINE-001 --json` returns one row; same for the ADR, SPEC, DCL; tracking `work_items` row present.

## Risks and Rollback

- Risk: Hook over-blocks legitimate proposals on edge-case table renderings. Mitigation: vague-phrase list is exact-substring, not heuristic; reviewers can issue an explicit `Owner waiver` line at Tier 2.
- Risk: MemBase query for waiver resolution adds latency to bridge Writes. Mitigation: keyed on waiver-ID index; per-process cache; fail-closed on unreachable.
- Risk: Tier 3 `radon` invocation fails on environments without `radon` installed. Mitigation: source-scan script feature-detects `radon`; absence yields a graceful skip with warning rather than exit 2.
- Risk: Codex `.cmd` shim drifts from Claude-side hook behavior. Mitigation: `check_codex_hook_parity.py` runs in the release-candidate gate; shim is a thin invoke of the same Python module the Claude hook calls.
- Risk: Multi-file edit could land partial across `.claude/settings.json` + `.codex/hooks.json` + `managed-artifacts.toml`. Mitigation: implementation-start authorization packet covers all paths atomically; smoke steps 8/9 explicitly test end-to-end registration.
- Risk: Formal-artifact approval packet for any of the four artifacts is rejected by the approval-gate hook. Mitigation: each packet independent; rollback per-artifact.
- Rollback: Revert all source files, four approval-packet JSON files, three test files, registration blocks in `.claude/settings.json` / `.codex/hooks.json`, and `managed-artifacts.toml` entry. Soft-delete (new-version with `resolution_status='retracted'`) the four MemBase records and the tracking `work_items` row. Revert the INDEX entry.

## Sequenced Dependencies

1. Insert `GOV-CODE-QUALITY-BASELINE-001` via formal-artifact-approval (IP-5 step 1) before IP-6 so the tracking `work_items` row's `source_spec_id` resolves.
2. Insert `SPEC-CODE-QUALITY-CHECKLIST-001` (IP-5 step 3) at or before IP-1 hook landing.
3. IP-1 logic module + template + active hook + `.cmd` shim + `.claude/settings.json` + `.codex/hooks.json` + `managed-artifacts.toml` land as one atomic implementation packet.
4. IP-2 Tier 1 fallback verifier lands at or before IP-1 so the release-candidate gate has a check the moment the hook is active.
5. IP-3 Tier 3 source scanner lands alongside or after IP-1.
6. IP-4 tests land alongside the artifacts they test.
7. Parent dependency: `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` (Slice 1 GO) authorizes the entire Slice 2 scope.

## Recommended Commit Type

`feat:` — net-new Tier-1 proposal-time hook (logic module + template + active hook + Codex `.cmd` shim + dual registration + `managed-artifacts.toml` entry), net-new Tier-1 fallback verifier script, net-new Tier-3 source-scan script, three net-new test files, and four net-new formal-artifact records in MemBase. Unambiguously a new-capability commit (the Code Quality Baseline governance subsystem with cross-harness enforcement).

## Bridge-Compliance Self-Check

- First line is `REVISED`.
- Title line `# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 (hook + Tier-1 verifier + Tier-3 source scan + tests + formal artifacts) - REVISED-2`.
- Metadata block: `bridge_kind: implementation_proposal`, `Document:`, `Version: 005`, `Responds to: bridge/gtkb-gov-code-quality-baseline-slice-2-004.md`, `Author: Prime Builder (Claude, harness B)`, `Date: 2026-05-14 UTC`, `Session: S350`, `target_paths: [JSON list with 17 entries, all in-root]`.
- `## Specification Links` is a plain heading with flat bullets and no `###` sub-headings; cites `bridge/INDEX.md` insertion-at-top discipline (CLAUSE-INDEX-IS-CANONICAL satisfaction).
- `## Prior Deliberations` cites six DELIB IDs from deliberation search.
- `## Owner Decisions / Input` is non-empty, substantive, cites the operative S350 parallel-dispatch directive and AUQ answer.
- `## Requirement Sufficiency` has exactly one operative state (`Existing requirements sufficient`).
- `## Clause Scope Clarification (Not a Bulk Operation)` is present and includes `formal-artifact-approval`, `inventory`, and `singleton MemBase insertion`.
- `## Recommended Commit Type` is present (`feat:`).
- `## In-Root Placement Evidence` enumerates every target path with backtick confirmation.
- F1 and F2 from `bridge/gtkb-gov-code-quality-baseline-slice-2-004.md` are explicitly closed in `## Claim` and in IP-1/IP-2/IP-3.
- F1-F4 from `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` remain closed (formal artifacts in IP-5; full Tier 1 §8.1 contract in IP-1; full §8.5 test coverage in IP-4; all 9 canonical rule IDs classified in IP-3).

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
