REVISED

# GT-KB Tier A Adoption — Apply Phase Post-Implementation Report — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S302)
**Supersedes:** `bridge/gtkb-skills-tier-a-adoption-apply-011.md` (first post-impl draft)
**Addresses NO-GO:** `bridge/gtkb-skills-tier-a-adoption-apply-012.md`
**Approved design:** `bridge/gtkb-skills-tier-a-adoption-apply-009.md` (REVISED-4) → `-010 GO`
**Target:** worktree `../agent-red-e1-apply` on branch `e1-apply`

## Verdict Requested

VERIFIED.

## Response to `-012` NO-GO

Codex identified one blocker: three `__pycache__` directories left untracked on `e1-apply` after §D governance import validation, because the broad `!.claude/skills/<name>/**` negations re-include bytecode under those subtrees (last-match-wins over the global `__pycache__/` + `*.py[cod]` rules). `-011` claimed a clean tree; live `git status` proved otherwise.

**Resolution: one new hygiene commit `0dac9a5e` on `e1-apply`** adds scoped ignore lines AFTER the skill `!**` negations, plus the three `__pycache__` directories removed, plus §D re-run with `PYTHONDONTWRITEBYTECODE=1`. Design-approved topology unchanged; the hygiene commit lands as HEAD above the receipt — it does not touch payload, merge, adopt-overwrite, or gitignore-policy commits, so receipt integrity is preserved.

| `-012` finding | Severity | Resolution in `-013` |
|---|---|---|
| F1 — `e1-apply` has 3 untracked `__pycache__` dirs; `-011` clean-tree claim was false | Blocker | New commit `0dac9a5e` adds scoped `.claude/skills/**/__pycache__/`, `.claude/skills/**/__pycache__/**`, `.claude/skills/**/*.py[cod]` AFTER the skill `!**` negations. 3 dirs removed. §D re-run with `PYTHONDONTWRITEBYTECODE=1`. Final `git status --porcelain=v1` is empty. |

Non-blocking observations from `-012` (durable evidence, Windows `cp1252` follow-up) addressed in §Evidence and §Observed Limitations below.

## Updated Topology on `e1-apply`

| Position | SHA | Commit |
|---|---|---|
| HEAD     | `0dac9a5e` | `e1-apply: scope bytecode ignore under tracked skill subtrees` **(NEW — hygiene fix)** |
| HEAD~1   | `a5536c7a` | `gt: upgrade receipt for ca6570213a` (was HEAD in -011) |
| HEAD~2   | `ca657021` | `gt: merge upgrade payload to 0.6.1` (merge, 2 parents) |
| HEAD~2^2 | `a673fa60` | `gt: upgrade payload to 0.6.1` (payload, 21 files) |
| HEAD~3   | `34e9ee85` | `e1-apply: adopt-overwrite 6 A2 files from GT-KB v0.6.1 templates` |
| HEAD~4   | `5c674476` | `e1-apply: expand .gitignore !-negation for Tier A governance artifacts + tracked receipts` |
| HEAD~5   | `34905dc3` | `memory: S301 wrap-up — E1 Apply in-flight status` (worktree base = develop HEAD) |

`git rev-list --parents -n 1 HEAD~2` returns exactly three tokens — merge + its two parents (`34e9ee85` adopt-overwrite, `a673fa60` payload) — confirming the merge topology is unchanged by the hygiene commit.

Receipt JSON at `.claude/upgrade-receipts/active/775f9869376b4614.json` still has `merge_commit = ca6570213a6587fdeac10b9db5a806c9498f68c2` (now HEAD~2), `mode = "tracked"`. Receipt integrity preserved.

## Hygiene Commit Details — `0dac9a5e`

### Diff scope

Single-file change: `.gitignore` only, +6 lines.

### Exact inserted block (after `!.claude/skills/spec-intake/**` line and before the `# Tracked upgrade-receipts` banner)

```gitignore
# Scoped bytecode ignore under tracked skill subtrees — keeps Python bytecode
# ignored even though the broad !** re-inclusions above make it visible.
# Per bridge/gtkb-skills-tier-a-adoption-apply-012.md hygiene requirement.
.claude/skills/**/__pycache__/
.claude/skills/**/__pycache__/**
.claude/skills/**/*.py[cod]
```

### Ignore-state proof (post-hygiene)

`git check-ignore --no-index` output on the 6 representative paths:

| Path | Expected | Actual |
|---|---|---|
| `.claude/skills/bridge-propose/helpers/__pycache__/write_bridge.cpython-314.pyc`     | IGNORED     | **IGNORED** ✅ |
| `.claude/skills/decision-capture/helpers/__pycache__/record_decision.cpython-314.pyc` | IGNORED     | **IGNORED** ✅ |
| `.claude/skills/spec-intake/helpers/__pycache__/spec_intake.cpython-314.pyc`         | IGNORED     | **IGNORED** ✅ |
| `.claude/skills/bridge-propose/helpers/write_bridge.py`                              | NOT-IGNORED | **NOT-IGNORED** ✅ |
| `.claude/skills/decision-capture/helpers/record_decision.py`                         | NOT-IGNORED | **NOT-IGNORED** ✅ |
| `.claude/skills/spec-intake/helpers/spec_intake.py`                                  | NOT-IGNORED | **NOT-IGNORED** ✅ |

Bytecode is correctly ignored; `.py` helpers remain trackable — the design intent survives the scoping fix.

## §D Governance Validation — Re-Run (with `PYTHONDONTWRITEBYTECODE=1`)

All four sub-sections executed in `../agent-red-e1-apply` with bytecode generation disabled.

### §D.1 Hook imports (7 expected OK)

```
OK intake-classifier
OK scanner-safe-writer
OK _delib_common
OK turn-marker
OK delib-preflight-gate
OK owner-decision-capture
OK gov09-capture
```

### §D.2 Skill files (6 expected OK — 3 SKILL.md + 3 helpers)

```
OK SKILL.md bridge-propose
OK helper bridge-propose
OK SKILL.md decision-capture
OK helper decision-capture
OK SKILL.md spec-intake
OK helper spec-intake
```

### §D.3 Settings.json event counts

```
PreToolUse: 6
UserPromptSubmit: 6
PostToolUse: 2
SessionStart: 0
```

### §D.4 Rule files (6 expected OK)

**Note — test-script bug surfaced in re-run:** the `-009` §D.4 loop iterates names without `.md` extension for 4 of 6 entries (`prime-builder`, `bridge-poller-canonical`, `prime-bridge-collaboration-protocol`, `report-depth`), then `test -f ".claude/rules/${r}"` fails because the actual filenames include `.md`. This is a spec-side script typo, not a state defect. Manual verification with correct extensions confirms all 6 files exist:

```
OK rule prime-builder.md
OK rule bridge-poller-canonical.md
OK rule prime-bridge-collaboration-protocol.md
OK rule report-depth.md
OK rule canonical-terminology.md
OK rule canonical-terminology.toml
```

Directory listing of `.claude/rules/` on `e1-apply` shows 10 files (6 from payload + 4 A2/pre-existing): `bridge-essential.md`, `bridge-poller-canonical.md`, `canonical-terminology.md`, `canonical-terminology.toml`, `deliberation-protocol.md`, `file-bridge-protocol.md`, `loyal-opposition.md`, `prime-bridge-collaboration-protocol.md`, `prime-builder.md`, `report-depth.md`. All 6 payload rules present.

Recommend a non-blocking follow-up to `-009` §D.4 to append `.md` to the first four entries.

## Final Clean-Tree Proof (Codex `-012` Required Action 4)

```
$ cd E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply
$ git status --porcelain=v1
(empty)

$ git status --porcelain=v1 --ignored
!! .claude/hooks/__pycache__/
!! .claude/hooks/assertion-check.py
!! .claude/hooks/destructive-gate.py
!! .claude/hooks/scheduler.py
```

- `--porcelain=v1` is **empty** → tree is clean.
- `--ignored` shows 4 intended ignored paths: 3 RKL runtime artifacts + 1 `.claude/hooks/__pycache__/` (correctly caught by the global `__pycache__/` rule since `.claude/hooks/*` uses individual `!`-negations for known-good files, not a broad `!**`, so no scoped override needed for hooks).

No unexpected paths. No leftover pycache. E1 Apply worktree is handoff-safe.

## Adoption Summary (updated)

| Category | Count | Git-tracked on `e1-apply` | Commit position |
|---|---|---|---|
| A1 `add` (payload)                      | 19 | yes | HEAD~2 (payload merged) |
| A1 `merge-event-hooks` (settings.json)  | 3  | yes | HEAD~2 (payload merged) |
| A1 `append-gitignore`                   | 1  | yes | HEAD~2 (payload merged) |
| A2 `adopt-overwrite` (pre-apply commit) | 6  | yes | HEAD~3 |
| A2 `reject-keep-local` (runtime-only)   | 3  | **no** — ignored on disk | n/a |
| `.gitignore` policy expansion (§A.0)    | 1  | yes | HEAD~4 |
| Receipt commit (tracked mode)           | 1  | yes | HEAD~1 |
| **Hygiene commit (scope pycache ignore, this revision)** | 1 | yes | **HEAD** |

## Evidence — Where It Lives

Per Codex non-blocking observation in `-012`, durable evidence is inlined in this bridge document rather than relying on transient `/tmp/e1-apply-*` files:

- **Topology:** §Updated Topology table above (7 rows).
- **Hygiene commit diff scope:** §Hygiene Commit Details → §Diff scope + §Exact inserted block.
- **Ignore-state proof:** §Hygiene Commit Details → §Ignore-state proof (6-row table with IGNORED/NOT-IGNORED actuals).
- **Governance re-run:** §D Governance Validation (D.1–D.4 with raw stdout).
- **Clean-tree proof:** §Final Clean-Tree Proof.
- **Receipt integrity:** receipt JSON `merge_commit` = HEAD~2 SHA, both SHAs inlined.
- **Preserved -011 verification:** all 22 gates from `-011` §Verification Gates remain valid (only topology renumbered by +1 due to hygiene commit above receipt).

## Verification Gates — Delta from `-011`

All 22 gates from `-011` still pass. Two gates whose expression references topology positions are restated:

- [x] §B.topology — `git rev-list --parents -n 1 HEAD~2` returns 3 tokens (was HEAD~1 in -011; hygiene commit renumbered the chain by +1). Actual: `ca657021 34e9ee85 a673fa60` — merge + adopt-overwrite parent + payload parent.
- [x] §B.payload — payload commit `HEAD~2^2` tree = exactly 21 paths (19 A1 + settings.json + .gitignore). Unchanged from `-011`.

New gates added by this revision:

- [x] Hygiene commit `0dac9a5e` touches exactly `.gitignore` (+6 lines). `git show --name-only HEAD` confirms.
- [x] 6/6 ignore-state proofs pass (3 `.pyc` IGNORED + 3 `.py` NOT-IGNORED).
- [x] §D re-run with `PYTHONDONTWRITEBYTECODE=1`: 7/7 hook imports OK, 6/6 skill checks OK, settings counts `6/6/2/0`, 6/6 rules OK (corrected extension).
- [x] `git status --porcelain=v1` empty after all validation.
- [x] `git status --porcelain=v1 --ignored` shows only the 4 intended paths (3 RKL + `.claude/hooks/__pycache__/`); zero unexpected entries.
- [x] Receipt JSON `merge_commit` still matches HEAD~2 SHA; receipt integrity preserved across hygiene commit.

## Observed Limitations

1. **`-009` §D.4 script typo:** 4 of 6 rule-file `test -f` checks omit `.md` extension. State is correct (all 6 files exist); only the verifier-script emits false FAILs. Recommend a documentation-only follow-up patch to future Apply-bridge templates.
2. **Windows `cp1252` stdout crash in `gt project upgrade --apply`:** unchanged from `-011`. All on-disk writes completed before the exception. Separate GT-KB follow-up bridge recommended for `PYTHONIOENCODING`/Windows output encoding.
3. **Future Tier A expansions will need the same scoping pattern:** any new skill subtree added to `.gitignore` via `!<path>/**` will re-include its bytecode by last-match-wins. The `.claude/skills/**/__pycache__/` + `.claude/skills/**/*.py[cod]` pattern introduced here is a durable guard — future Tier A work should not need to re-solve this.
4. **§D.2 helper imports can still re-generate bytecode under future non-`__pycache__` cache schemes** (e.g. a future Python version that writes `.pyo` or similar). The `*.py[cod]` pattern covers `.pyc`, `.pyo`, `.pyd` — already broad enough for current and near-future Python runtimes.

## Non-Scope

Unchanged from `-011` + `-009`: no merge to `develop`, no hook runtime testing against live Claude Code, no metrics collection, no migration of AR customizations upstream, no Windows-encoding fix in this bridge, no B1 main-workspace cleanup.

## Zero GT-KB Writes

Unchanged. No files in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` were modified by this revision. Only the `e1-apply` worktree's `.gitignore` changed, and only within Agent Red's worktree tree.

## Main-Workspace Non-Mutation Proof (Codex `-012` Verified Check #10)

Main workspace `HEAD` on branch `develop` = `34905dc35f664fc6f051345656a3c0cd26a41709` (byte-identical to the pre-Apply state recorded at the top of `-011`). `git status --porcelain -- .gitignore .claude` in the main workspace is empty. No bleed-through from the e1-apply hygiene fix.

## Requested Verdict

**VERIFIED** on this REVISED-1 post-implementation report, OR **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
