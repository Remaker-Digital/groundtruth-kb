NEW

# GT-KB Tier A Adoption — Apply Phase Post-Implementation Report

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (capped-spawn execution)
**Implements:** `bridge/gtkb-skills-tier-a-adoption-apply-009.md` (REVISED-4)
**Approved by:** `bridge/gtkb-skills-tier-a-adoption-apply-010.md` (GO, Codex)
**Target:** worktree `../agent-red-e1-apply` on branch `e1-apply` (NOT merged to `develop`)

## Verdict Requested

VERIFIED.

## Summary

All 11 phases (§A.1 → §A.0 → §A.0.1 → §A.2 → §A.2.1 → §A.3 → §B → §C → §D → §E → §F) executed per the approved REVISED-4 plan. Hard gates passed. Ignore-surface expansion installed; 6 adopt-overwrite A2 files committed; GT-KB upgrade applied with `mode='tracked'` receipt; rollback validated; governance artifacts import cleanly; main workspace byte-identical pre/post.

**One non-blocking caveat:** `gt project upgrade --apply` wrote all file actions, the payload commit, the merge commit, and the tracked receipt commit successfully, then crashed in `click.echo` while flushing summary lines containing the Unicode arrow character `→` against Windows `cp1252` stdout. The crash is cosmetic — all on-disk state and git history completed before the exception. Recommend filing a follow-up GT-KB bridge for the Windows `PYTHONIOENCODING` fix; not blocking for E1 Apply.

## Topology on `e1-apply`

| Position | SHA | Commit |
|----------|-----|--------|
| HEAD     | `a5536c7a` | `gt: upgrade receipt for ca6570213a` |
| HEAD~1   | `ca657021` | `gt: merge upgrade payload to 0.6.1` (merge, 2 parents: HEAD~2 + payload) |
| HEAD~1^2 | `a673fa60` | `gt: upgrade payload to 0.6.1` (payload, 21 files) |
| HEAD~2   | `34e9ee85` | `e1-apply: adopt-overwrite 6 A2 files from GT-KB v0.6.1 templates` |
| HEAD~3   | `5c674476` | `e1-apply: expand .gitignore !-negation for Tier A governance artifacts + tracked receipts` |
| HEAD~4   | `34905dc3` | `memory: S301 wrap-up — E1 Apply in-flight status` (worktree base = develop HEAD) |

`git rev-list --parents -n 1 HEAD~1` returns **3 tokens** (merge commit + 2 parents), as required.

## Receipt JSON

`.claude/upgrade-receipts/active/775f9869376b4614.json`:

```json
{
  "schema_version": "v1",
  "receipt_id": "775f9869376b4614",
  "merge_commit": "ca6570213a6587fdeac10b9db5a806c9498f68c2",
  "target_branch": "e1-apply",
  "from_version": "0.6.1",
  "to_version": "0.6.1",
  "mode": "tracked",
  "created_at": "2026-04-18T15:55:17.553178Z",
  "artifact_classes_touched": [
    "gitignore-pattern",
    "hook",
    "rule",
    "settings-hook-registration",
    "skill"
  ]
}
```

`merge_commit` = `ca6570213a6587fdeac10b9db5a806c9498f68c2` matches HEAD~1 SHA; `mode = "tracked"` as required.

## Payload-Commit File List (21 paths)

From `git show --name-only HEAD~1^2`:

```
.claude/hooks/_delib_common.py
.claude/hooks/delib-preflight-gate.py
.claude/hooks/gov09-capture.py
.claude/hooks/intake-classifier.py
.claude/hooks/owner-decision-capture.py
.claude/hooks/scanner-safe-writer.py
.claude/hooks/turn-marker.py
.claude/rules/bridge-poller-canonical.md
.claude/rules/canonical-terminology.md
.claude/rules/canonical-terminology.toml
.claude/rules/prime-bridge-collaboration-protocol.md
.claude/rules/prime-builder.md
.claude/rules/report-depth.md
.claude/settings.json
.claude/skills/bridge-propose/SKILL.md
.claude/skills/bridge-propose/helpers/write_bridge.py
.claude/skills/decision-capture/SKILL.md
.claude/skills/decision-capture/helpers/record_decision.py
.claude/skills/spec-intake/SKILL.md
.claude/skills/spec-intake/helpers/spec_intake.py
.gitignore
```

19 A1 + `.claude/settings.json` + `.gitignore` = 21 paths. Matches the gate.

## Adoption Summary

| Category | Count | Git-tracked on e1-apply | Commit position |
|----------|-------|-------------------------|-----------------|
| A1 `add` (payload)                     | 19 | yes | HEAD~1 (payload merged) |
| A1 `merge-event-hooks` (settings.json) | 3  | yes | HEAD~1 (payload merged) |
| A1 `append-gitignore`                  | 1  | yes | HEAD~1 (payload merged) |
| A2 `adopt-overwrite` (pre-apply commit) | 6  | yes | HEAD~2 |
| A2 `reject-keep-local` (runtime-only)  | 3  | **no** — ignored on disk | n/a |
| `.gitignore` policy expansion          | 1  | yes | HEAD~3 |
| Receipt commit (tracked mode)          | 1  | yes | HEAD |

## Verification Gates (all PASS)

- [x] §A.1 `git worktree list` shows `../agent-red-e1-apply` on `e1-apply` (`a5536c7a`).
- [x] §A.1 pre-A.0 `git status --porcelain` empty (0 lines).
- [x] §A.0 commit `5c674476` touches exactly `.gitignore` (+32 lines, including 26 patterns + 6 section/comment lines). Pre-SHA `d1e63c35ea8f…`; post-SHA `8ee1f87624500d4…`.
- [x] §A.0.1 A1 `FAIL count: 0` (all 19 NOT-IGNORED).
- [x] §A.0.1 AO `FAIL count: 0` (all 6 NOT-IGNORED).
- [x] §A.0.1 RKL `FAIL count: 0` (all 3 IGNORED, disposition unchanged).
- [x] §A.0.1 Receipt-probe NOT-IGNORED.
- [x] §A.0.1 `resolve_receipt_mode()` → `mode='tracked'` (note: `receipt path not ignored → tracked mode`).
- [x] §A.0.1 **zero** `FAIL CHECK-IGNORE-ERROR` lines in evidence — 3-way gate never tripped on any path.
- [x] §A.2 evidence: 6 `MATCH-TEMPLATE` + 3 `MATCH-AR-MAIN`; 0 `MISMATCH-*`.
- [x] §A.2.1 pre-commit `git status --porcelain` = exactly 6 lines (` M` × 2, `??` × 4); 0 RKL paths.
- [x] §A.2.1 commit `34e9ee85` touches exactly 6 files (`6 files changed, 453 insertions(+), 394 deletions(-)`).
- [x] §A.3 planner summary: `counts {'informational': 24, 'add': 19, 'merge-event-hooks': 3, 'append-gitignore': 1}`; `A2 mutating violations 0`.
- [x] §B apply wrote receipt at `.claude/upgrade-receipts/active/775f9869376b4614.json`; receipt commit `a5536c7a`; `mode='tracked'`.
- [x] `git rev-list --parents -n 1 HEAD~1` returns 3 tokens.
- [x] Payload commit `HEAD~1^2` tree = exactly 21 paths (19 A1 + settings.json + .gitignore).
- [x] Exactly 1 receipt file at `.claude/upgrade-receipts/active/*.json`; `merge_commit = HEAD~1 SHA`; `mode = "tracked"`.
- [x] §C revert-status: 19 `D` + 2 `M`; 0 entries for 9 A2 paths or receipt.
- [x] §C `.gitignore` revert diff: `grep -cE '^[+-][^+-]' = 2` (touches only the `.claude/hooks/*.log` append — blank-line/comment/pattern 3-line deletion, 2 counted by the regex because the bare-`-` blank line doesn't match `[^+-]`). §A.0 !-negation block in HEAD~3 untouched.
- [x] §C revert-status-with-ignored: exactly 3 RKL `!!` rows (`assertion-check.py`, `destructive-gate.py`, `scheduler.py`).
- [x] §C `git revert --abort` → empty `git status --porcelain`.
- [x] §D.1 all 7 hook imports `OK`; 0 `FAIL`. (`intake-classifier` emits informational `CANONICAL_CATALOG_USED` line on import — not a failure.)
- [x] §D.2 all 3 `SKILL.md` + 3 helper-module imports `OK`; 0 `FAIL`.
- [x] §D.3 `.claude/settings.json` event counts: PreToolUse=6, UserPromptSubmit=6, PostToolUse=2, SessionStart=0.
- [x] §D.4 all 6 rule files present: `prime-builder.md`, `bridge-poller-canonical.md`, `prime-bridge-collaboration-protocol.md`, `report-depth.md`, `canonical-terminology.md`, `canonical-terminology.toml`.
- [x] §E main-workspace SHAs unchanged: `.gitignore` `d1e63c35…` = pre-Apply; 3 RKL SHAs byte-identical to pre-Apply captures (`40b7fda4…`, `f5dc05b1…`, `97d6b7ad…`).
- [x] §E main-workspace `git rev-parse HEAD = 34905dc3…` (unchanged); `git status` shows 0 `.claude/` changes and 0 `.gitignore` changes (new changes present in main workspace pre-dated Apply; they match the in-flight tree captured at session start).

## Evidence Files

All under `/tmp/` on the Prime Builder runtime host:

- `/tmp/e1-apply-evidence.txt` — consolidated 83-line evidence log (A.0.1 ignore-state proof, resolve_receipt_mode output, A.2 SHA hashes, A.2 post-copy MATCH verification, §B apply notes, §C rollback counts, §E main-workspace SHAs)
- `/tmp/e1-apply-cleantree-status-pre-a0.txt` — empty (clean tree pre-§A.0)
- `/tmp/e1-apply-gitignore-{before,after}.{txt,sha}` — pre/post §A.0 `.gitignore` SHA-256 and contents
- `/tmp/e1-apply-gitignore-diff.txt` — §A.0 diff (+32 lines)
- `/tmp/e1-apply-git-status-after-a2.txt` — 6 lines
- `/tmp/e1-apply-dryrun.txt` — full §A.3 `project upgrade --dry-run` output
- `/tmp/e1-apply-dryrun-summary.txt` — planner Python summary (`counts {...}`, `A2 mutating violations 0`)
- `/tmp/e1-apply-stdout.txt` — §B apply stdout (includes the post-completion `UnicodeEncodeError` traceback)
- `/tmp/e1-apply-{head,merge,adopt-overwrite,gitignore-policy}.txt` — topology SHAs
- `/tmp/e1-apply-merge-parents.txt` — 3 tokens
- `/tmp/e1-apply-receipt-files.txt` — single receipt path
- `/tmp/e1-apply-payload-files.txt` — 21 paths
- `/tmp/e1-apply-commit-log.txt` — 5-line `git log --oneline`
- `/tmp/e1-apply-revert-status.txt` + `/tmp/e1-apply-revert-status-with-ignored.txt` + `/tmp/e1-apply-revert-gitignore-diff.txt` + `/tmp/e1-apply-revert-ignored-proof.txt` — §C rollback evidence
- `/tmp/e1-apply-worktree-list.txt` — `git worktree list` output

## Known Non-Blocker — GT-KB Windows cp1252 Stdout Crash

`python -m groundtruth_kb project upgrade --apply` completed all file actions (19 UPDATED, 3 MERGED, 1 APPENDED) and wrote the tracked receipt commit `a5536c7a` successfully, then crashed in `click.echo` while flushing summary lines like `MERGED .claude/settings.json → PreToolUse rebuilt (6 managed, 0 preserved)`. The Unicode arrow `→` (U+2192) cannot be encoded by Windows default cp1252 stdout. The crash occurred **after** all state transitions completed — verified by:

1. Tree state post-crash: clean (`git status --porcelain` empty).
2. Commit log: 5 expected commits present on `e1-apply`, including the receipt commit at HEAD.
3. Receipt JSON on disk, well-formed, `mode='tracked'`, `merge_commit` matches HEAD~1.
4. Rollback, governance, and non-mutation verification gates (§C/D/E) all pass against the completed state.

Recommend separate follow-up bridge: `gtkb-cli-stdout-utf8-windows` to add `PYTHONIOENCODING` handling or `click.echo(..., file=sys.stdout.buffer, nl=True)` with explicit UTF-8. Non-scope for E1 Apply.

## Cross-GO-Conditions Checklist (from `-010` §GO Conditions)

| # | Condition | Evidence |
|---|-----------|----------|
| 1 | Execute only in `../agent-red-e1-apply` on `e1-apply`; no mutation of main | §E main-workspace HEAD unchanged, 0 `.claude/`/`.gitignore` diffs |
| 2 | §A.0 before §A.2 materialization and before apply | Commit log: `5c674476` → `34e9ee85` → payload/merge/receipt |
| 3 | §A.0.1 hard gate; any A1/AO/RKL/receipt ignore-state failure or CHECK-IGNORE-ERROR ⇒ STOP | 0 FAILs, 0 CHECK-IGNORE-ERRORs |
| 4 | `resolve_receipt_mode() != tracked` ⇒ STOP | Mode = tracked (assertion passed) |
| 5 | Re-planner: `A2 mutating violations 0`; counts `add=19, merge-event-hooks=3, append-gitignore=1` | Exact match |
| 6 | Apply stdout: `RECEIPT tracked @` (not filesystem); STOP if filesystem | Receipt JSON `mode='tracked'`; receipt commit on HEAD (tracked-mode topology) |
| 7 | Payload commit lists 19 A1 + `.claude/settings.json` + `.gitignore` | 21 paths verified |
| 8 | Rollback dry-run: 19 `D` + 2 `M`; no A2/receipt in plain status; exactly 3 RKL `!!` rows in `--ignored` | Exact match |
| 9 | Post-impl report contains ignore-state proof, receipt JSON, payload file list, rollback dry-run outputs, main-workspace non-mutation | All present above |

## Observed Limitations (carried from `-009` §Post-Impl Report Contents)

- **RKL runtime files re-materialize on worktree re-create:** `assertion-check.py`, `destructive-gate.py`, `scheduler.py` are not in git history; recreating the worktree requires re-sourcing them from main Agent Red workspace before Apply can replay.
- **Future `scaffold_version` bumps** re-run forward-materialization for all 3 RKL files until a per-file-skip mechanism or upstream migration lands.
- **Future Tier A expansions** beyond Phase A require a new `.gitignore` policy bridge for each `!`-negation. No auto-expansion is pre-authorized.
- **GT-KB CLI Windows stdout encoding bug** (documented above) — cosmetic; filed separately.

## Non-Scope Confirmed Upheld

- No integration into `develop` (branch remains `e1-apply`-only).
- No hook runtime testing against live Claude Code.
- No metrics collection.
- No migration of AR customizations upstream.
- No `--skip-file` feature request.
- No B1 main-workspace cleanup (separate `agent-red-cto-cleanup` bridge).

## Next Step After Codex VERIFIED

- Leave worktree `../agent-red-e1-apply` and branch `e1-apply` intact until owner decides integration path.
- Do not merge `e1-apply` → `develop` without a fresh bridge. Any merge is a new proposal because `.gitignore` policy + 6 AO commits would join the public branch.
- Follow-up workstream (separate bridge) to address GT-KB CLI cp1252 encoding crash.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
