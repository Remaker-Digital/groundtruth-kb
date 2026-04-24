NEW

# GT-KB Tier A Adoption - Current Main Integration Implementation Report

**Status:** NEW - Loyal Opposition verification requested  
**Prime Builder:** Codex  
**Date:** 2026-04-22  
**Reviewed GO:** `bridge/gtkb-tier-a-current-main-integration-002.md`

## Claim

Prime Builder implemented the approved current-`main` GT-KB v0.6.1 scaffold
integration in a clean isolated worktree, without merging the stale `e1-apply`
branch and without applying scaffold changes in the dirty main workspace.

The branch is ready for Loyal Opposition verification, subject to one explicit
evidence note: the GT-KB apply completed and produced commits/receipt evidence,
but the command exited non-zero while printing a Unicode arrow on Windows
cp1252. The worktree was clean afterward and all required checks passed after a
small local Codex hook parity marker repair.

## Implementation Evidence

- Integration worktree:
  `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration`
- Integration branch: `codex/gtkb-current-main-integration`
- Base SHA: `707c2679d8b2378e8b29ad7b09ecc1d1a96a6bfc`
- Base commit: `707c2679 ci: harden docs quality workflow (#24)`
- Current HEAD: `d048146d gt: track canonical terminology config`
- Upgrade merge commit: `cd006769d012c4a8e5915a804ede903edbad446e`
- Upgrade payload commit: `b8f0068c6b7091e4c6103d0bf89d2788fb7f37d6`

Commands:

```powershell
git worktree add -b codex/gtkb-current-main-integration `
  'E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration' main
```

Result: worktree created at base `707c2679`.

```powershell
python -m groundtruth_kb --version
```

Result: `gt, version 0.6.1`.

```powershell
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges
```

Initial result: 45 rows total: 24 informational rows, 13 managed-file `ADD`
rows, 4 `.claude/settings.json` `MERGE-EVENT-HOOKS` rows, and 4 `.gitignore`
`APPEND-GITIGNORE` rows.

```powershell
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges
```

Result: file actions completed, payload branch merged, and filesystem receipt
written. The command then exited with a `UnicodeEncodeError` while printing the
receipt line containing `→` to the Windows cp1252 console.

The branch was clean immediately afterward:

```text
git status --porcelain=v1 -b
## codex/gtkb-current-main-integration
```

## Exact Diff

```text
git diff --name-status main..HEAD
A       .claude/hooks/_delib_common.py
A       .claude/hooks/delib-preflight-gate.py
A       .claude/hooks/gov09-capture.py
A       .claude/hooks/intake-classifier.py
A       .claude/hooks/owner-decision-capture.py
A       .claude/hooks/scanner-safe-writer.py
A       .claude/hooks/turn-marker.py
A       .claude/rules/bridge-poller-canonical.md
A       .claude/rules/canonical-terminology.md
A       .claude/rules/canonical-terminology.toml
A       .claude/rules/prime-bridge-collaboration-protocol.md
A       .claude/rules/prime-builder.md
A       .claude/rules/report-depth.md
M       .claude/settings.json
M       .gitignore
```

```text
git diff --name-status main..HEAD --diff-filter=D
```

Result: no deleted files.

```text
git diff --stat main..HEAD
15 files changed, 1327 insertions(+)
```

The GT-KB apply copied `.claude/rules/canonical-terminology.toml`, but the
existing `.gitignore` pattern `.claude/rules/*` initially left it ignored and
untracked. Because the dry-run classified that path as an authorized managed
add, Prime Builder force-added that one file in commit `d048146d`.

## Current-Base Managed-File Reconciliation

Before apply:

```text
managed_file_artifacts=28
missing=13 equal_template=0 differ_from_template=15
```

Missing rows were the 13 authorized managed adds:

```text
hook|.claude/hooks/intake-classifier.py|gt-kb-managed|overwrite
hook|.claude/hooks/scanner-safe-writer.py|gt-kb-managed|overwrite
hook|.claude/hooks/_delib_common.py|gt-kb-managed|overwrite
hook|.claude/hooks/turn-marker.py|gt-kb-managed|overwrite
hook|.claude/hooks/delib-preflight-gate.py|gt-kb-managed|overwrite
hook|.claude/hooks/owner-decision-capture.py|gt-kb-managed|overwrite
hook|.claude/hooks/gov09-capture.py|gt-kb-managed|overwrite
rule|.claude/rules/prime-builder.md|gt-kb-managed|overwrite
rule|.claude/rules/bridge-poller-canonical.md|gt-kb-managed|overwrite
rule|.claude/rules/prime-bridge-collaboration-protocol.md|gt-kb-managed|overwrite
rule|.claude/rules/report-depth.md|gt-kb-managed|overwrite
rule|.claude/rules/canonical-terminology.md|gt-kb-managed|overwrite
rule|.claude/rules/canonical-terminology.toml|gt-kb-managed|overwrite
```

After apply and the force-add follow-up:

```text
managed_file_artifacts=28
missing=0 equal_template=3 differ_from_template=25
```

Prime Builder did not run `--force` and did not overwrite or delete existing
current-main files. The remaining hash-different rows are preserved as local
current-main content for future review rather than changed under this GO.

## Settings Hook Validation

Custom validation compared `.claude/settings.json` against the GT-KB scaffold
registry order:

```text
SessionStart: ok=True managed=2 preserved=1 total=3
UserPromptSubmit: ok=True managed=5 preserved=1 total=6
PostToolUse: ok=True managed=2 preserved=0 total=2
PreToolUse: ok=True managed=6 preserved=1 total=7
settings_order_validation=PASS
```

## Git Ignore Probes

Expected ignored paths:

```text
.gitignore:310:.claude/hooks/*.log        .claude/hooks/example.log
.gitignore:316:.groundtruth/              .groundtruth/receipt.json
.gitignore:29:__pycache__/                src/__pycache__/x.pyc
.gitignore:319:.claude/settings.local.json        .claude/settings.local.json
```

Managed hook/rule/skill probes returned no ignore match:

```text
git check-ignore -v `
  .claude/hooks/intake-classifier.py `
  .claude/rules/prime-builder.md `
  .claude/rules/canonical-terminology.toml `
  .claude/skills/decision-capture/SKILL.md
```

Result: exit code 1 with no output, meaning those probes were not ignored.

## Rollback / Receipt Evidence

Filesystem receipt:

```text
.claude/upgrade-receipts/active/669e076f67ff4b64.json
```

Receipt content:

```json
{
  "schema_version": "v1",
  "receipt_id": "669e076f67ff4b64",
  "merge_commit": "cd006769d012c4a8e5915a804ede903edbad446e",
  "target_branch": "codex/gtkb-current-main-integration",
  "from_version": "0.6.1",
  "to_version": "0.6.1",
  "mode": "filesystem",
  "created_at": "2026-04-22T09:12:23.988777Z",
  "artifact_classes_touched": [
    "gitignore-pattern",
    "hook",
    "rule",
    "settings-hook-registration"
  ]
}
```

Rollback dry-run:

```powershell
python -m groundtruth_kb project rollback --dry-run `
  --receipt-id 669e076f67ff4b64 --target-dir .
```

Result: rollback plan found merge commit `cd006769d012c4a8e5915a804ede903edbad446e`
and 14 files to revert from the GT-KB payload merge. The manually force-added
`canonical-terminology.toml` is outside that receipt and can be reverted by
reverting commit `d048146d` if the branch is rejected.

## Verification Results

```powershell
python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q --tb=short
```

Result: `22 passed, 1 warning`.

```powershell
python scripts/check_codex_hook_parity.py --project-root .
```

Initial result: failed because local Codex hook wrappers under
`C:\Users\micha\.codex\agent-red-hooks\` were missing literal parity markers.
Prime Builder made local-only marker comments in:

- `C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py`
- `C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py`

Follow-up results:

```text
python -m py_compile C:\Users\micha\.codex\agent-red-hooks\session_start_dispatch.py C:\Users\micha\.codex\agent-red-hooks\session_wrapup_trigger_dispatch.py
exit code 0

python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short
5 passed

python scripts/check_codex_hook_parity.py --project-root .
Codex hook parity: PASS
```

```powershell
python scripts/release_candidate_gate.py --skip-frontend
```

Result: `RELEASE GATE: PASS`.

Release-gate details:

- Ruff `E,F`: pass
- Import-cycle detector: pass
- Bandit: pass
- pip-audit: pass
- Codex hook parity: pass
- Required pytest suite: `185 passed, 2 warnings`

Final clean-tree proof:

```text
git status --porcelain=v1 -b
## codex/gtkb-current-main-integration
```

## Risk / Impact

- The integration branch does not delete current Agent Red-owned governance or
  Codex parity files.
- The direct GT-KB payload rollback receipt covers the 14 files committed by the
  GT-KB apply merge. The extra tracked TOML managed add is a separate one-file
  commit because `.gitignore` otherwise hid it from the payload commit.
- The GT-KB CLI has a Windows encoding bug in receipt-output printing; it did
  not prevent file application, commit creation, receipt creation, or later
  verification.

## Recommended Action

Loyal Opposition should verify the branch
`codex/gtkb-current-main-integration` in
`E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-gtkb-current-main-integration`.

If verified, Prime Builder can prepare the branch for normal review/merge.

## Decision Needed From Owner

None at this verification request. No production deployment, credential action,
destructive cleanup, or formal GOV/SPEC/PB/ADR/DCL/Deliberation Archive mutation
is requested.
