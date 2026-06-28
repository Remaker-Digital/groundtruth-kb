NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: gpt-5-codex
author_model_version: gpt-5-codex-2026-06-28
author_model_configuration: Codex desktop automation; role=Prime Builder; reasoning_effort=default

# GT-KB Bridge Implementation Report - gtkb-work-tree-hygiene-slice-b-strays-cli - 003

bridge_kind: implementation_report
Document: gtkb-work-tree-hygiene-slice-b-strays-cli
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-002.md
Approved proposal: bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-001.md
Recommended commit type: feat

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/hygiene/strays.py", "platform_tests/scripts/test_hygiene_strays_cli.py"]

## Implementation Claim

Implemented the approved WI-4356 Slice B read-only `gt hygiene strays` CLI.

The implementation adds `groundtruth_kb.hygiene.strays`, a package-side adapter that gathers fresh live state from:

- `git status --porcelain=v1 -z --untracked-files=all`
- `git stash list --format=%gd%x09%ct%x09%gs`
- `git worktree list --porcelain`
- immediate orphan candidates under `.claude/worktrees/`

The adapter feeds those inputs into the verified Slice A detector in `scripts.hygiene.stray_detector`, then emits candidate actions only. It does not delete files, drop stashes, create commits, mutate MemBase, mutate bridge state beyond this report, or change GOV/SPEC/ADR/DCL artifacts.

The CLI adds `gt hygiene strays` with:

- `--format human|json|both`
- optional `--output` for `strays.json` and/or `summary.md`
- `--active-workspace-path` and `--active-stash-ref` active-session suppression
- `--report-only/--fail-on-findings` exit-code policy
- a hidden `--now` option for deterministic tests

## First-Line Role Eligibility Check

Prime Builder processed latest `GO` at `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-002.md`.

Implementation-start evidence:

- Work-intent claim row: `24921`
- Work-intent session: `019f1078-0168-7573-8a31-a68af5b9842a`
- Implementation packet: `sha256:f89c7bea9272da5c587fbfaf45dc6293c0847e91fe5d02ebf9094706b35fc4bb`
- Target-path preflight: `verdict=in_scope`; all 3 candidate paths in scope; 0 out of scope

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/hygiene/strays.py`
- `platform_tests/scripts/test_hygiene_strays_cli.py`

No other implementation paths were intentionally modified.

## Commits

- `7f2e564ab` - `proposal: add WI-4356 strays CLI slice`
- `1bc7fdef7` - `feat: add work-tree strays hygiene CLI`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge files and role-specific status tokens remain the canonical handoff chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - cleanup recommendations are surfaced as candidate actions rather than direct governance mutations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's governing spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification evidence below is mapped from the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target path metadata are included.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner approval evidence remains the active PAUTH and owner decision.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation stays under `E:\GT-KB` platform/test paths and does not touch adopter applications.
- `GOV-STANDING-BACKLOG-001` - WI-4356 remains the backlog authority for this slice.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex used explicit bridge/commit/target-path checks in this Windows automation context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - work-tree hygiene behavior is preserved as source, tests, proposal, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale workspace/stash/worktree states are classified into explicit candidate-action lifecycle states.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the command collects live git/stash/worktree state each run and does not read cached startup reports, dashboard summaries, or prior scan artifacts.

## Owner Decisions / Input

- `DELIB-20260867` - owner decision authorizing WI-4356 implementation under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` - active project authorization for WI-4356.

No new owner input was required. The slice is dry-run/report-only and performs no destructive cleanup.

## Prior Deliberations

- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-002.md` - GO for the WI-4356 slice plan.
- `bridge/gtkb-work-tree-hygiene-slice-a-detector-004.md` - VERIFIED detector slice consumed by this CLI adapter.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-001.md` - approved implementation proposal.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification

| Spec / requirement | Verification evidence | Result |
| --- | --- | --- |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_hygiene_strays_reports_stale_tracked_and_untracked_paths` builds a temporary git repo, mutates live files, and asserts the CLI reports those live changes via JSON. | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_hygiene_strays_reports_orphaned_worktree_directory` builds a live `.claude/worktrees/*` orphan and asserts it is collected from the filesystem. | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_hygiene_strays_active_workspace_path_is_not_stale` proves active-session suppression produces `candidate_action=skip` instead of direct cleanup. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest and ruff commands below were executed after implementation and formatting. | PASS |
| Proposal acceptance: clean state | `test_hygiene_strays_clean_repo_has_zero_findings` verifies a clean temporary repo returns zero workspace/stash/worktree findings. | PASS |
| Proposal acceptance: stash parsing | `test_parse_stash_entries_uses_epoch_timestamp` verifies stash timestamp parsing for deterministic detector input. | PASS |

Commands executed:

```text
python -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short
```

Result: 33 passed.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/hygiene/strays.py platform_tests/scripts/test_hygiene_strays_cli.py
```

Result: All checks passed.

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/hygiene/strays.py platform_tests/scripts/test_hygiene_strays_cli.py
```

Result: 3 files already formatted.

## Residual Risk

The CLI is intentionally dry-run-only. It surfaces candidate actions such as stale tracked edit review, stale untracked file review, stale stash review, and orphaned worktree prune/delete recommendation, but it does not execute those actions. Later WI-4356 slices can add doctor integration, governance spec insertion, or apply-mode behavior through separate bridge-scoped proposals.

## Handoff

Loyal Opposition should verify the implementation against the approved scope, especially that `gt hygiene strays` reads fresh live state, preserves active-session exclusions, emits JSON/human dry-run output, and does not perform cleanup mutations.
