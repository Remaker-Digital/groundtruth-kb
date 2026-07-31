# WI-4464 git-workflow hazard gap audit

Date: 2026-06-13
Role: Loyal Opposition
Harness: Codex A
Work item: WI-4464

## Claim

WI-4464 remains a valid high-priority backlog item, but the actionable gap is narrower than the row title now implies. The commit-scope detector exists and passes tests, but the active pre-commit hook does not run it; the reset-orphan hazard is documented and partially guarded only for destructive resets, not for ordinary shared-branch reset patterns.

## Evidence

- The forensic recovery record marks the 2026-06-11 incident resolved and explicitly captures WI-4464 as the follow-up at `memory/recovery-2026-06-11-fab20-commit-collision.md:34`.
- The same record identifies explicit pathspec commits as the operating mitigation at `memory/recovery-2026-06-11-fab20-commit-collision.md:26` and `memory/recovery-2026-06-11-fab20-commit-collision.md:121-123`.
- `scripts/check_commit_scope_bundling.py` exists and is verified by `bridge/gtkb-commit-scope-bundling-detection-slice-1-008.md`.
- The active hook path is `.githooks`: `git config --get core.hooksPath` returned `.githooks`.
- `.githooks/pre-commit` runs the secret scan, inventory drift check, narrative artifact evidence check, and staged-Python ruff-format check at lines 15, 17, 25, and 30. It does not invoke `scripts/check_commit_scope_bundling.py`.
- The existing destructive-git tests cover hard reset only: `platform_tests/unit/test_destructive_gate_hook.py:228` and `platform_tests/unit/test_destructive_gate_hook.py:247`.

## Verification

```powershell
python scripts\check_commit_scope_bundling.py --staged --json
python -m pytest platform_tests\scripts\test_check_commit_scope_bundling.py platform_tests\unit\test_destructive_gate_hook.py -q --tb=short
```

Results:

- `check_commit_scope_bundling.py --staged --json`: `status: pass` for the current unstaged/clean index.
- Focused tests: `45 passed`.

## Risk / impact

The detector is available but passive unless a user or harness runs it manually. A plain `git commit` can still bypass the WI-4464 mitigation when unrelated protected paths are already staged, because the active pre-commit hook does not emit even the Slice 1 warning. The reset-orphan hazard remains procedural: the project warns humans not to reset on a shared branch, but current automated coverage only demonstrates blocking for `git reset --hard`, not the softer reset shape that caused the incident.

## Recommended action

Prime Builder should split WI-4464 into two follow-up scopes before implementation:

1. Hook wiring scope: add `python scripts/check_commit_scope_bundling.py --staged` to `.githooks/pre-commit` in warn-only mode, preserving the verified Slice 1 behavior and adding a hook-registration regression.
2. Reset safety scope: design a separate guard or advisory for ordinary `git reset` on shared branches when concurrent-session evidence or recent foreign commits exist. This should be separate from the commit-scope detector because it is a history-operation hazard, not a staged-scope hazard.

This report does not request owner action. It preserves the current disposition so Prime can avoid duplicating the already-verified detector work while still closing the unprotected hook and reset-safety gaps.
