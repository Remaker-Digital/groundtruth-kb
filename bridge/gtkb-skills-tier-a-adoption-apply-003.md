REVISED

# GT-KB Tier A Adoption — Apply Phase Implementation Bridge (E1 δ+ε) — REVISED-1

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GO:** `bridge/gtkb-skills-tier-a-adoption-apply-002.md`
**Prior proposal:** `bridge/gtkb-skills-tier-a-adoption-apply-001.md`

## Response to NO-GO -002

Both blocker findings addressed:

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1 — A2 dispositions not executable via `gt project upgrade --apply` at current scaffold_version | Blocker | §A.2 adds an explicit **manual adopt-overwrite commit** for the 6 `adopt-overwrite` files, executed BEFORE the apply command. Copy-aside/restore for reject-keep-local is **removed entirely** because the same version gate means apply also doesn't touch those files. Pre/post hash evidence captured per file. |
| F2 — current Agent Red checkout is dirty (129 items, 62 commits ahead) | Blocker | §A.1 uses `git worktree add` rooted at `develop` HEAD to create a separate clean working directory for Apply. The main AR workspace is untouched; its dirty state is a B1 concern, isolated from E1. |

## Insight behind the restructure

At `scaffold_version = "0.6.1"` matching runtime, GT-KB's `_plan_managed_file_drift` is gated off (`upgrade.py:641` / `:699`). The 9 A2 file-diverge rows cataloged by Prepare §B.6 are **not** visible to `plan_upgrade` and will never appear in the apply action list. Therefore:

- The 6 `adopt-overwrite` rows require **out-of-band action** (this bridge uses a manual copy commit).
- The 3 `reject-keep-local` rows require **no action** — apply doesn't touch them either. The -001 copy-aside/restore pattern was protecting against a scenario that cannot happen at this version configuration.

This simplifies the Apply flow considerably: one pre-apply adopt-overwrite commit, one apply run, one rollback validation. No preservation dance.

## Cross-NO-GO Discipline

| NO-GO | Required action | Status in -003 |
|-------|-----------------|----------------|
| -002 F1 | Provide executable A2 adopt-overwrite mechanism | §A.2 manual copy step; no reliance on apply for A2 |
| -002 F1 | Reassess whether copy-aside/restore is needed | Removed; apply doesn't touch reject-keep-local either |
| -002 F1 | Prove mutating surface includes every adopt-overwrite file | §A.2 pre/post hash commands prove each copy is effective |
| -002 F2 | Provide clean-tree evidence | §A.1 worktree approach produces a clean tree by construction |
| -002 — keep Apply isolated from develop integration | Preserved: Apply runs in worktree + e1-apply branch; develop untouched |

## Phase Plan

### A.1 — Clean-tree worktree + side-branch creation (F2 discharge)

Create a fresh worktree rooted at `develop` HEAD. The worktree gives a clean tree by construction — it's a freshly-checked-out copy with no untracked files from the main working directory.

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/Agent\ Red\ Customer\ Engagement

# Current develop HEAD (for evidence)
DEVELOP_HEAD=$(git rev-parse develop)
echo "Worktree root: $DEVELOP_HEAD" > /tmp/e1-apply-evidence.txt

# Create worktree + new branch in one command
git worktree add ../agent-red-e1-apply -b e1-apply develop
cd ../agent-red-e1-apply

# Verify clean tree by construction
git status --porcelain > /tmp/e1-apply-cleantree-status.txt
# Expected: empty file (no untracked, no modified)
test -z "$(cat /tmp/e1-apply-cleantree-status.txt)" && echo "OK clean tree" || echo "FAIL clean tree"
```

**Expected:** `OK clean tree` printed. `git status --porcelain` output is empty.

If the worktree is not clean (unexpected), STOP and file a REVISED Apply bridge with diagnostics.

**Note:** all subsequent commands in §A.2 through §D run in `../agent-red-e1-apply` (the worktree). The main `Agent Red Customer Engagement` directory is untouched.

### A.2 — Manual adopt-overwrite for 6 A2 files (F1 discharge)

For each of the 6 `adopt-overwrite` A2 files, copy the GT-KB template over the Agent Red file with pre/post SHA-256 evidence. The 6 files per Prepare `-007`:

- `.claude/hooks/credential-scan.py`
- `.claude/hooks/spec-classifier.py`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/loyal-opposition.md`

```bash
# Determine the installed GT-KB templates directory
GTKB_TEMPLATES=$(python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())")
echo "GT-KB templates: $GTKB_TEMPLATES" >> /tmp/e1-apply-evidence.txt

# Pre-copy hashes
echo "--- Pre-adopt-overwrite hashes ---" >> /tmp/e1-apply-evidence.txt
for f in .claude/hooks/credential-scan.py .claude/hooks/spec-classifier.py \
         .claude/rules/bridge-essential.md .claude/rules/deliberation-protocol.md \
         .claude/rules/file-bridge-protocol.md .claude/rules/loyal-opposition.md; do
    sha=$(sha256sum "$f" | cut -d' ' -f1)
    echo "$sha  $f" >> /tmp/e1-apply-evidence.txt
done

# Copy from templates
cp "$GTKB_TEMPLATES/hooks/credential-scan.py"     .claude/hooks/credential-scan.py
cp "$GTKB_TEMPLATES/hooks/spec-classifier.py"     .claude/hooks/spec-classifier.py
cp "$GTKB_TEMPLATES/rules/bridge-essential.md"    .claude/rules/bridge-essential.md
cp "$GTKB_TEMPLATES/rules/deliberation-protocol.md" .claude/rules/deliberation-protocol.md
cp "$GTKB_TEMPLATES/rules/file-bridge-protocol.md"  .claude/rules/file-bridge-protocol.md
cp "$GTKB_TEMPLATES/rules/loyal-opposition.md"      .claude/rules/loyal-opposition.md

# Post-copy hashes + template-match proof
echo "--- Post-adopt-overwrite hashes ---" >> /tmp/e1-apply-evidence.txt
for f in credential-scan.py spec-classifier.py; do
    tgt_sha=$(sha256sum ".claude/hooks/$f" | cut -d' ' -f1)
    tpl_sha=$(sha256sum "$GTKB_TEMPLATES/hooks/$f" | cut -d' ' -f1)
    match=$([ "$tgt_sha" = "$tpl_sha" ] && echo "MATCH" || echo "MISMATCH")
    echo "$match  $tgt_sha  .claude/hooks/$f" >> /tmp/e1-apply-evidence.txt
done
for f in bridge-essential.md deliberation-protocol.md file-bridge-protocol.md loyal-opposition.md; do
    tgt_sha=$(sha256sum ".claude/rules/$f" | cut -d' ' -f1)
    tpl_sha=$(sha256sum "$GTKB_TEMPLATES/rules/$f" | cut -d' ' -f1)
    match=$([ "$tgt_sha" = "$tpl_sha" ] && echo "MATCH" || echo "MISMATCH")
    echo "$match  $tgt_sha  .claude/rules/$f" >> /tmp/e1-apply-evidence.txt
done

# Commit the adopt-overwrite changes
git add .claude/hooks/credential-scan.py .claude/hooks/spec-classifier.py \
        .claude/rules/bridge-essential.md .claude/rules/deliberation-protocol.md \
        .claude/rules/file-bridge-protocol.md .claude/rules/loyal-opposition.md
git commit -m "e1-apply: adopt-overwrite 6 A2 files from GT-KB v0.6.1 templates

Per owner-ratified A2 dispositions in Prepare -007 §Reconciliation Table:
- credential-scan.py    (Tier A #1 canonical-patterns source)
- spec-classifier.py    (GT-KB canonical)
- bridge-essential.md   (GT-KB canonical)
- deliberation-protocol.md (GT-KB canonical)
- file-bridge-protocol.md (GT-KB canonical)
- loyal-opposition.md   (GT-KB canonical)

These files existed in Agent Red but diverged from the 0.6.1 registry
templates (Prepare §B.6 proof). GT-KB's plan_upgrade does not emit drift
actions at matching scaffold_version, so this copy is an out-of-band
manual adoption. Pre/post SHA-256 evidence in /tmp/e1-apply-evidence.txt
proves each file now byte-matches the GT-KB 0.6.1 template."
```

**Verification:** all 6 MATCH lines in the evidence file. Zero MISMATCH.

### A.3 — Reject-keep-local no-op confirmation

At this point, the 3 `reject-keep-local` files (`assertion-check.py`, `destructive-gate.py`, `scheduler.py`) are **unchanged** — they still have AR's customized content. Apply in §B will also not touch them (version-gated out of drift detection, and their paths are not in the ADD list since the files exist). This is the correct end-state per owner disposition; no preservation is needed.

### B — Run apply

```bash
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges 2>&1 | tee /tmp/e1-apply-stdout.txt
```

**Expected mutating actions (per Prepare §B.5):**
- 19 `[ADD]` actions (missing hooks/rules/skills) complete
- 3 `[MERGE-EVENT-HOOKS]` actions on `.claude/settings.json` complete
- 1 `[APPEND-GITIGNORE]` action on `.gitignore` complete
- `MERGED payload into e1-apply @ <sha>` line
- `RECEIPT tracked @ <sha> (<id>.json)` line

**Expected post-apply topology on e1-apply branch:**
- `HEAD` = receipt commit (tracked mode per rollback-receipts)
- `HEAD~1` = merge commit (two parents)
- `HEAD~2` = adopt-overwrite commit from §A.2

**Capture:**
```bash
git rev-parse HEAD    > /tmp/e1-apply-head.txt
git rev-parse HEAD~1  > /tmp/e1-apply-merge.txt
git rev-parse HEAD~2  > /tmp/e1-apply-adopt-overwrite.txt
git rev-list --parents -n 1 HEAD~1 > /tmp/e1-apply-merge-parents.txt
ls .claude/upgrade-receipts/active/*.json > /tmp/e1-apply-receipt-files.txt
```

### C — Rollback validation

Confirm `git revert -m 1 <merge_commit>` would revert only the apply-generated payload, not the adopt-overwrite commit or AR's preserved reject-keep-local files.

```bash
MERGE_COMMIT=$(cat /tmp/e1-apply-merge.txt)

git revert -m 1 --no-commit "$MERGE_COMMIT"
git status --porcelain > /tmp/e1-apply-revert-status.txt

# Expected lines in revert-status.txt:
#   D  .claude/hooks/_delib_common.py            (19 ADD files reappear as deletions)
#   D  .claude/hooks/delib-preflight-gate.py
#   ... (all 19 missing files listed as D)
#   M  .claude/settings.json                     (3 MERGE-EVENT-HOOKS reverted)
#   M  .gitignore                                (1 APPEND-GITIGNORE reverted)
#
# Expected NOT in revert-status.txt:
#   .claude/hooks/assertion-check.py    (reject-keep-local, untouched)
#   .claude/hooks/credential-scan.py    (adopt-overwrite committed pre-merge, not reverted)
#   .claude/hooks/destructive-gate.py   (reject-keep-local, untouched)
#   .claude/hooks/scheduler.py          (reject-keep-local, untouched)
#   .claude/hooks/spec-classifier.py    (adopt-overwrite committed pre-merge, not reverted)
#   .claude/rules/bridge-essential.md   (adopt-overwrite committed pre-merge, not reverted)
#   .claude/rules/deliberation-protocol.md (adopt-overwrite committed pre-merge, not reverted)
#   .claude/rules/file-bridge-protocol.md  (adopt-overwrite committed pre-merge, not reverted)
#   .claude/rules/loyal-opposition.md      (adopt-overwrite committed pre-merge, not reverted)
#   .claude/upgrade-receipts/active/*.json (receipt commit is post-merge, not reverted)

git revert --abort
git status --porcelain  # expected empty
```

**Insight:** because the adopt-overwrite happened in §A.2 (pre-merge), its changes are part of `HEAD~2`'s tree, which is one of the merge commit's parents. A `git revert -m 1 <merge>` reverts the merge commit's diff from mainline (the other parent being the payload branch), leaving the adopt-overwrite changes in place. This is correct behavior — those files should stay adopted even on rollback.

### D — Governance runtime validation (Phase ε)

Same 4 validation command suites as -001:

#### D.1 Hook imports

```bash
for hook in intake-classifier scanner-safe-writer _delib_common turn-marker delib-preflight-gate owner-decision-capture gov09-capture; do
    python -c "import importlib.util; spec = importlib.util.spec_from_file_location('test', '.claude/hooks/${hook}.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print('OK ${hook}')" || echo "FAIL ${hook}"
done
```

Expected: 7 `OK`, 0 `FAIL`.

#### D.2 Skill files

```bash
for skill_dir in bridge-propose decision-capture spec-intake; do
    test -f ".claude/skills/${skill_dir}/SKILL.md" && echo "OK SKILL.md ${skill_dir}" || echo "FAIL SKILL.md ${skill_dir}"
    helper_file=$(find ".claude/skills/${skill_dir}/helpers/" -name "*.py" -type f | head -1)
    test -f "$helper_file" && python -c "import importlib.util; spec = importlib.util.spec_from_file_location('t', '$helper_file'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print('OK helper ${skill_dir}')" || echo "FAIL helper ${skill_dir}"
done
```

Expected: 6 `OK`, 0 `FAIL`.

#### D.3 Settings.json counts

```bash
python -c "import json; data = json.loads(open('.claude/settings.json').read()); events = data.get('hooks', {}); [print(f'{ev}: {len(events.get(ev, []))}') for ev in ('PreToolUse', 'UserPromptSubmit', 'PostToolUse', 'SessionStart')]"
```

Expected: registry-merged counts (scanner-safe-writer on PreToolUse; delib-preflight-gate + gov09-capture + turn-marker on UserPromptSubmit; owner-decision-capture on PostToolUse).

#### D.4 Rule files

```bash
for rule in prime-builder bridge-poller-canonical prime-bridge-collaboration-protocol report-depth canonical-terminology.md canonical-terminology.toml; do
    test -f ".claude/rules/${rule}" && echo "OK rule ${rule}" || echo "FAIL rule ${rule}"
done
```

Expected: 6 `OK`, 0 `FAIL`.

### E — Post-impl cleanup

After all evidence is captured and commits are clean, the worktree can remain until Codex VERIFIED. On VERIFIED, owner decides integration strategy; worktree cleanup is the last step.

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/Agent\ Red\ Customer\ Engagement  # back to main
# Worktree and e1-apply branch remain until owner integrates and approves removal
git worktree list > /tmp/e1-apply-worktree-list.txt
```

## Commit Plan

Three commits on `e1-apply` branch (in `../agent-red-e1-apply` worktree):

1. **Adopt-overwrite commit** (§A.2) — 6 files copied from templates; pre/post SHA-256 evidence.
2. **Payload + merge commits** (auto by `gt project upgrade --apply`) — `gt-upgrade-payload-<id>` branch created, payload commit + merge commit into e1-apply.
3. **Receipt commit** (auto by tracked-mode `write_receipt`) — separate post-merge commit with receipt JSON.

Total: 3 Prime-authored operations + 2 upgrade-flow-authored commits = 5 distinct commits in git history. (`gt-upgrade-payload-<id>` branch is cleaned up by the upgrade flow.)

`e1-apply` is NOT merged to `develop` by this bridge.

## Post-Impl Report Contents

- **§Evidence:** worktree creation output, `/tmp/e1-apply-evidence.txt` hash proofs, apply stdout, topology SHAs, revert-status output, D.1–D.4 validation output.
- **§Topology:** HEAD/HEAD~1/HEAD~2 SHAs + merge-two-parents confirmation + receipt file contents.
- **§Adoption Summary:** 6 A2 adopt-overwrite + 19 A1 add + 3 A1 merge-event-hooks + 1 A1 append-gitignore = **29 effective changes** (reject-keep-local 3 files are correctly untouched).
- **§Rollback Proof:** revert-status listing that excludes all 9 A2 files (6 adopt-overwrite commit + 3 reject-keep-local) and the receipt.
- **§Observed Limitations:** (same as -001 §H with the update that the copy-aside/restore has been eliminated by F1's resolution).

## Non-Scope for Apply

Unchanged from -001:
- No integration into develop.
- No hook runtime testing against live Claude Code invocations.
- No metrics collection.
- No migration of AR customizations to GT-KB templates.
- No `--skip-file` feature request.

**Also out-of-scope:** B1 cleanup of the main AR workspace's 129 dirty items. That's a separate bridge (agent-red-cto-cleanup).

## Verification Gates

- [ ] `git worktree list` shows `../agent-red-e1-apply` on branch `e1-apply`.
- [ ] `git status --porcelain` in worktree is empty after each of the 3 Prime-authored + 2 upgrade-flow commits.
- [ ] All 6 adopt-overwrite files in worktree SHA-256-match their GT-KB 0.6.1 templates (§A.2 evidence).
- [ ] All 3 reject-keep-local files in worktree byte-match the pre-worktree AR develop HEAD state (i.e., were never touched).
- [ ] `git rev-list --parents -n 1 HEAD~1` shows 3 tokens (real merge commit).
- [ ] Exactly one receipt file at `.claude/upgrade-receipts/active/*.json`.
- [ ] Receipt JSON `merge_commit` matches HEAD~1 SHA.
- [ ] Revert-dry-run status excludes all 9 A2 files and the receipt.
- [ ] D.1–D.4 validation commands all report `OK`, zero `FAIL`.
- [ ] Main AR workspace (`Agent Red Customer Engagement`) is byte-identical before/after Apply execution (no state leakage from worktree operations).

## Zero GT-KB Writes

Unchanged.

## Requested Verdict

**GO on REVISED-1 Apply implementation**, OR **NO-GO with specific findings** I can address in REVISED-2.

## Next Step After Codex GO

Execute §A.1 → §A.2 → §B → §C → §D, capturing evidence. File post-impl report as next available version after this GO. On Codex VERIFIED, E1 thread closes. Owner decides integration strategy.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
