NEW

bridge_kind: implementation_report
Document: gtkb-fab-05-rule-file-retirement
Version: 005
Responds-To: bridge/gtkb-fab-05-rule-file-retirement-004.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4417
Project Authorization: PAUTH-FAB05-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 39746c1a-10a0-4914-a27c-dc4251c74b08
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: [".claude/rules/bridge-permanent-operations-runbook.md", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-knowledge-base-index.md", ".claude/rules/codex-review-operating-contract.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/prime-builder.md", ".claude/rules/report-depth-prime-builder-context.md", ".claude/rules/codex-standing-priorities.md", "archive/os-poller-2026-04-25/**", "independent-progress-assessments/archive/cursor-legacy/**", "groundtruth-kb/docs/announcements/v0.7.0-rc1.md", "platform_tests/scripts/test_fab05_rule_file_retirement.py", ".groundtruth/formal-artifact-approvals/fab-05-*.json", "groundtruth.db"]

# FAB-05 — Retire era-stranded + contradictory auto-loaded rule files — Post-Implementation Report

WI-4417 (FAB-05) of PROJECT-FABLE-INVESTIGATION. Implements the GO at
`bridge/gtkb-fab-05-rule-file-retirement-004.md` (proposal `-003`). The
implementation is committed at **`4d31fcf6b`** (`docs:`); this report carries the
four dispositions forward to verification.

## Implementation Summary

All four owner-approved dispositions (DELIB-FAB05-REMEDIATION-20260610) implemented:

- **HYG-018 (poller retirement):** 22 tracked OS-poller scripts archived
  `independent-progress-assessments/bridge-automation/` →
  `archive/os-poller-2026-04-25/` (git rename); `bridge-permanent-operations-runbook.md`
  rewritten as a DEPRECATED stub citing `bridge-essential.md` + WI-4404 (no PT3M
  mandate / repair commands remain); the two stale "(scheduled/automated every 3
  minutes)" cadence echoes removed from `file-bridge-protocol.md`.
- **HYG-026 (Cursor-era retirement):** 4 Cursor/Agent-Red-era rule files archived
  `.claude/rules/` → `independent-progress-assessments/archive/cursor-legacy/`
  (so they no longer auto-load; `.claude/rules/*.md` 38 → 34); the 4 cursor-legacy
  archive paths in `codex-knowledge-base-index.md` corrected to the real
  `independent-progress-assessments/archive/cursor-legacy/` prefix.
- **HYG-027 (dedup):** the verbatim-duplicated `Severity Model` + `Implementation
  Boundary` block in `codex-review-operating-contract.md` removed and the surviving
  mislabeled heading renamed `Review Coordination`; the duplicated AUQ-contract
  block in `acting-prime-builder.md` replaced with a pointer to the canonical home
  in `prime-builder-role.md`; `prime-builder.md` scope note added distinguishing it
  from `prime-builder-role.md`; `report-depth-prime-builder-context.md` replaced
  with a pointer stub to canonical `report-depth.md`.
- **HYG-038 (backlog authority):** `codex-standing-priorities.md` Priority 1
  repointed from the deleted `memory/work_list.md` to the MemBase backlog
  (`gt backlog list` / GOV-STANDING-BACKLOG-001); `v0.7.0-rc1.md` dead work_list.md
  reference fixed; WI-3278 + WI-3465 retired (both resolved; GOV-15, owner-approved).

Each protected `.claude/rules/*.md` edit carries a narrative-approval packet under
`.groundtruth/formal-artifact-approvals/fab-05-*.json` (8 packets);
`check_narrative_artifact_evidence.py --staged` reported PASS (8 cleared) before
commit.

## Implementation Decisions (deviations surfaced + owner-approved)

1. **HYG-018 scope correction (owner AUQ 2026-06-11):** the proposal assumed ~25
   files in `bridge-automation/`; reality is **22 tracked poller scripts + 10,002
   gitignored runtime logs** (`logs/` is `.gitignore`'d). Owner chose "archive the
   22 tracked, leave the logs for FAB-13" (runtime-store retention is FAB-13 scope).
   The 22 tracked scripts are archived; the gitignored logs are untouched.
2. **HYG-027 report-depth = pointer, not delete:** `report-depth-prime-builder-context.md`
   is a required file in `test_groundtruth_governance_adoption.py` (presence list)
   and is referenced by skill frontmatter (`governance: report-depth-prime-builder-context`).
   Hard-deleting it would break those. The proposal's "delete/**pointer**" disposition
   covers this; the **pointer** branch was taken (file retained as a stub → `report-depth.md`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX is canonical; append-only bridge lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + execution below.
- `GOV-STANDING-BACKLOG-001` — HYG-038 restores the MemBase backlog as the sole idle-work authority.
- `GOV-ARTIFACT-APPROVAL-001` — each protected `.claude/rules/*.md` edit carries a per-file narrative-approval packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all edits/moves in-root; no `applications/` subtree touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the rule retirement is captured as
  durable bridge artifacts (proposal `-003`, GO `-004`, this report `-005`) with lifecycle
  state tracked via bridge versioning.

Governing rules (non-spec): `bridge-essential.md` (the do-not-re-enable authority
the runbook contradicted); `project-root-boundary.md` (the dead Playground link);
`DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-018/026/027/038).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering.
- `DELIB-FAB05-REMEDIATION-20260610` — the 4 owner dispositions.
- `bridge/gtkb-fab-05-rule-file-retirement-003.md` (REVISED) / `-004.md` (GO) — the implemented proposal.

## Owner Decisions / Input

Authorized by the bridge `GO` at `-004` plus owner `AskUserQuestion` evidence:
- 2026-06-10 dispositions (`DELIB-FAB05-REMEDIATION-20260610`).
- 2026-06-11 HYG-018 logs scope ("Archive 22 tracked, leave logs").
- 2026-06-11 concrete-content approval ("Approve all — packets, WIs, commit"), which
  approved all 8 protected-narrative edits (incl. the report-depth pointer branch),
  the archive moves, the doc fix, and the WI-3278/3465 retires.

## Spec-to-Test Mapping

| Specification / requirement | Test or verification | Executed | Result |
|---|---|---|---|
| HYG-018 poller retirement (`bridge-essential.md`) | `test_poller_stack_archived_no_tracked_source_files`, `test_runbook_is_deprecated_stub_no_poller_mandate`, `test_file_bridge_protocol_no_poller_cadence` | yes | PASS |
| HYG-026 Cursor-era retirement + index fix (`project-root-boundary.md`) | `test_cursor_era_rule_files_archived`, `test_index_cursor_legacy_path_corrected`, `test_no_playground_link_in_active_rules` | yes | PASS |
| HYG-027 dedup (`report-depth.md` canonical) | `test_severity_model_block_deduped_and_renamed`, `test_auq_block_pointer_not_duplicate`, `test_report_depth_context_is_pointer_stub`, `test_prime_builder_scope_note_present` | yes | PASS |
| HYG-038 backlog repoint (`GOV-STANDING-BACKLOG-001`) | `test_standing_priorities_repointed_to_membase_backlog`, `test_rc1_announcement_no_work_list_ref` | yes | PASS |
| `GOV-ARTIFACT-APPROVAL-001` (narrative packets) | `check_narrative_artifact_evidence.py --staged` → PASS (8 cleared) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (full mapping + execution) | this table + the pytest run below | yes | PASS |

## Verification Commands and Results

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_fab05_rule_file_retirement.py -q --tb=line
# 12 passed in 0.14s

groundtruth-kb\.venv\Scripts\python.exe scripts\check_narrative_artifact_evidence.py --staged
# PASS narrative-artifact evidence (8 cleared)   [pre-commit]

git show --stat 4d31fcf6b
# 8 protected rule edits + 8 fab-05 packets + 22 poller renames + 4 cursor renames + inventory regen + INDEX
```

WI-3278 / WI-3465: both `Resolution Status: resolved` (verified via `gt backlog show`).

## Recommended Commit Type

`docs:` — governance/rule-file retirement + dedup + repoint (with `chore:`-class
archive moves). Committed as `docs:` at `4d31fcf6b`. The grep-absence test
(`platform_tests/scripts/test_fab05_rule_file_retirement.py`) is committed alongside
this report.

## Isolation Placement Compliance

All edits/moves are in-root under `E:\GT-KB`: rule edits under `.claude/rules/`,
archives under `archive/os-poller-2026-04-25/` and
`independent-progress-assessments/archive/cursor-legacy/`, the test under
`platform_tests/scripts/`, packets under `.groundtruth/formal-artifact-approvals/`,
the doc fix under `groundtruth-kb/docs/`. No `applications/` subtree touched; no
out-of-root artifact.

## Acceptance Criteria

1. OS-poller stack archived; runbook is a DEPRECATED stub; no PT3M mandate loads — DONE.
2. 4 Cursor-era rule files archived; index path corrected; no live Playground link in active rules — DONE.
3. Duplicated normative blocks deduped to one canonical home + pointers; Severity Model heading fixed — DONE.
4. `codex-standing-priorities.md` repointed to `gt backlog list`; WI-3278/3465 retired; `v0.7.0-rc1.md` fixed — DONE.
5. Each rule edit has its narrative-approval packet; grep-absence test passes (12/12); ruff-clean — DONE.

## Commit / Bridge State Note

Implementation committed at `4d31fcf6b`. This `-005` report + the grep-absence test
are committed for durability; its `NEW@-005` INDEX entry is added to the live
working-tree `bridge/INDEX.md` for Loyal Opposition to scan. Cross-harness
auto-dispatch is currently disabled (emergency kill-switch `GTKB_NO_CROSS_HARNESS_TRIGGER=1`
after the 2026-06-11 dispatch-storm incident); verification will be picked up via a
manual Codex/LO bridge scan.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
