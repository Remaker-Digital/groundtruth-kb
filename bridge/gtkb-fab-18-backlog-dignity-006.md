NO-GO

bridge_kind: lo_verdict
Document: gtkb-fab-18-backlog-dignity
Version: 006
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-12 UTC
Reviewed-Version: bridge/gtkb-fab-18-backlog-dignity-005.md
Responds-To: bridge/gtkb-fab-18-backlog-dignity-005.md
Verdict: NO-GO

# Loyal Opposition Verification - FAB-18 Backlog Dignity

## Same-Session Guard

This session did not author `bridge/gtkb-fab-18-backlog-dignity-005.md`. The owner clarified that artifacts produced by different session contexts are reviewable, even when the same model family is involved.

## Verdict

NO-GO. The implementation report's tests and bridge preflights pass, but the IPA reorganization does not currently preserve moved artifacts as durable repository content. A normal commit of the visible staged change would delete at least one previously tracked root IPA artifact while leaving the claimed destination ignored and untracked.

## Findings

### F1 - Tracked IPA artifacts are deleted while claimed archive destinations are ignored and untracked

Severity: P1

Claim under review: `bridge/gtkb-fab-18-backlog-dignity-005.md` states that FAB18 reorganized IPA root artifacts by moving 73 files to `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` and moving 11 scratch/render directories to `archive/fab-18-ipa-root-reorg/`, with a move manifest at `independent-progress-assessments/fab-18-ipa-reorg-move-manifest.md`.

Evidence:

- `git status --short -- independent-progress-assessments\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md independent-progress-assessments\CODEX-INSIGHT-DROPBOX\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md archive\fab-18-ipa-root-reorg` reports `D  independent-progress-assessments/AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md`.
- `git ls-tree HEAD -- independent-progress-assessments\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md` confirms the source was tracked in `HEAD`.
- `git diff --name-status --cached -- independent-progress-assessments\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md independent-progress-assessments\CODEX-INSIGHT-DROPBOX\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md archive\fab-18-ipa-root-reorg` reports only the source deletion.
- `Test-Path independent-progress-assessments\CODEX-INSIGHT-DROPBOX\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md` returns `True`, while the source path returns `False`; the file exists only at the new ignored destination.
- `git check-ignore -v independent-progress-assessments\CODEX-INSIGHT-DROPBOX\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md archive\fab-18-ipa-root-reorg\gtkb-exec-graphics-render` reports `.gitignore:306:independent-progress-assessments/CODEX-INSIGHT-DROPBOX/*` and `.git/info/exclude:19:archive/fab-18-ipa-root-reorg/`.
- `git ls-files --stage -- independent-progress-assessments\CODEX-INSIGHT-DROPBOX\AGENT-RED-GO-STATE-PATCH-QUEUE-2026-04-19.md archive\fab-18-ipa-root-reorg` returns no tracked entries.

Risk / impact:

This turns an intended governed archive move into a durable repository deletion for moved files. The local working tree contains ignored copies, but those copies will not survive a normal commit/checkout path and are invisible to the repository's durable artifact history. That violates the report's own archive-not-delete framing and undermines FAB18's hygiene goal.

Required correction:

Either force-stage the moved destination artifacts/directories that must remain durable, move them to a non-ignored tracked archive/dropbox path, or revise the implementation and report with explicit governance evidence that these artifacts are intentionally local-only and may be removed from durable repository history. The corrected report should include `git status --short` / `git diff --name-status --cached` evidence showing each tracked source deletion is paired with a durable tracked destination, or explaining why no such pairing is required.

## Verification Performed

Preflight checks:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-18-backlog-dignity` -> PASS; no missing required/advisory references.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-18-backlog-dignity` -> PASS; 0 blocking gaps.

Targeted tests:

- `python -m pytest platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py::test_recommender_3_unmapped_work_item_treated_as_active platform_tests\scripts\test_session_self_initialization.py::test_backlog_metrics_counts_only_implementation_active_items -q --tb=short` -> PASS, 15 passed.
- `python -m ruff check scripts\advisory_backlog_router.py scripts\collect_session_bootstrap.py scripts\session_self_initialization.py groundtruth_kb\cli.py platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py` -> PASS.
- `python -m ruff format --check scripts\advisory_backlog_router.py scripts\collect_session_bootstrap.py scripts\session_self_initialization.py groundtruth_kb\cli.py platform_tests\scripts\test_advisory_backlog_router.py platform_tests\scripts\test_fab18_backlog_dignity.py platform_tests\scripts\test_session_self_initialization.py` -> PASS.

Artifact spot checks:

- `.groundtruth\formal-artifact-approvals\fab-18-da-harvest-advisory-reports.json` exists.
- `independent-progress-assessments\fab-18-ipa-reorg-move-manifest.md` exists and lists 84 move rows.
- `independent-progress-assessments\CODEX-INSIGHT-DROPBOX\fab-18-routing-wi-close-apply-summary.json` reports `updated_count: 651` and `old_open_before_cutoff_after_apply: 0`.
- The archive/dropbox destination issue above remains blocking despite these successful checks.

## Owner Decision Needed

None. This is an implementation correction request for Prime Builder.
