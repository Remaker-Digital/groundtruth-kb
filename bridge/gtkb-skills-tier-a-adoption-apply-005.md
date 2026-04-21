REVISED

# GT-KB Tier A Adoption — Apply Phase Implementation Bridge (E1 δ+ε) — REVISED-2

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GO:** `bridge/gtkb-skills-tier-a-adoption-apply-004.md`
**Prior versions:** `bridge/gtkb-skills-tier-a-adoption-apply-003.md` (REVISED-1), `-002` (NO-GO), `-001` (NEW)

## Response to NO-GO -004

Blocker finding addressed:

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1 — Worktree rooted at `develop` HEAD does not contain 7 of 9 A2 files (they are `.gitignore`'d in the main workspace). Copy-aside/no-preservation design assumed local files would inherit into the worktree, which they do not. Reject-keep-local is violated because GT-KB's unconditional `add` for missing managed files would overwrite the 3 `reject-keep-local` paths with template bytes. | Blocker | **§A.2 (new) materializes all 9 A2 files into the worktree BEFORE apply runs**, sourced appropriately per disposition: 6 from GT-KB v0.6.1 templates (adopt-overwrite), 3 from main workspace local bytes (reject-keep-local). After materialization, the planner sees 9 files present on disk → no `add` actions emitted for them → reject-keep-local files are preserved. Only 2 of the 9 files are tracked via `.gitignore` `!`-negation (`credential-scan.py`, `bridge-essential.md`) and are committed on `e1-apply`; the other 7 remain as runtime-only artifacts on the worktree disk, matching AR's existing `.gitignore` policy. |

## Cross-NO-GO Discipline

| NO-GO | Required action | Status in -005 |
|-------|-----------------|----------------|
| -002 F1 | Provide executable A2 adopt-overwrite mechanism | §A.2 manual copy from templates for all 6 adopt-overwrite paths |
| -002 F1 | Reassess whether copy-aside/restore is needed | Replaced with forward-materialization from main workspace for 3 reject-keep-local paths |
| -002 F1 | Prove mutating surface includes every adopt-overwrite file | §A.3 re-planner run proves A2 files do not appear in planner output (present on disk) |
| -002 F2 | Provide clean-tree evidence | §A.1 worktree + §A.2 materialization results in clean tree because ignored files do not appear in `git status --porcelain` |
| -002 keep Apply isolated from develop integration | Preserved: Apply runs in worktree + e1-apply branch; develop untouched |
| -004 F1 | State whether A2 source of truth is committed develop HEAD or current ignored local files | §Owner Decisions now explicit: 6 adopt-overwrite from GT-KB v0.6.1 templates; 3 reject-keep-local from main workspace local bytes |
| -004 F1 | Explicitly copy/materialize reject-keep-local files into worktree with owner-approved source paths and hash evidence | §A.2 sources `.claude/hooks/{assertion-check,destructive-gate,scheduler}.py` from `../Agent Red Customer Engagement/` (the main workspace); pre-copy SHA-256 of main-workspace file recorded as the authoritative reference |
| -004 F1 | Decide tracked/ignored disposition for the 3 reject-keep-local files | Ignored runtime files only — NOT force-added. `.gitignore` policy preserved. 7 of 9 A2 files remain runtime-only on worktree disk |
| -004 F1 | Recompute mutating surface against actual execution target after A2 setup | §A.3 runs `gt project upgrade --dry-run --dir .` inside worktree AFTER §A.2 materialization, documents the actions, confirms 23 mutating actions match -007's A1 surface |
| -004 F1 | Update adoption summary and rollback proof for missing-file adds, manual additions, preserved ignored files | §D adoption summary reclassified; §C rollback proof updated for new file topology |

## Owner Decisions Carried Forward (pinned)

From Prepare -007 §Reconciliation Table (owner-ratified):

- **Clean-tree strategy:** δ3 — side-branch `e1-apply` on a separate worktree.
- **Per-file-skip mechanism:** (a) — pre-apply forward-materialization. The 3 `reject-keep-local` files are sourced from the current AR main workspace into the worktree before apply; the 6 `adopt-overwrite` files are sourced from GT-KB v0.6.1 templates.
- **A2 dispositions (9 paths):**
  - `adopt-overwrite` (6): `credential-scan.py`, `spec-classifier.py`, `bridge-essential.md`, `deliberation-protocol.md`, `file-bridge-protocol.md`, `loyal-opposition.md`
  - `reject-keep-local` (3): `assertion-check.py`, `destructive-gate.py`, `scheduler.py`

**A2 source-of-truth declaration (explicit per -004 F1 required action #1):**
- For 6 `adopt-overwrite` files → GT-KB v0.6.1 template bytes at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/{hooks,rules}/*`.
- For 3 `reject-keep-local` files → current AR main workspace local-file bytes at `E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/.claude/hooks/*`. Those local files are the owner-ratified "keep" content per Prepare -007. The main workspace is READ-ONLY throughout Apply execution.

## Insight — How the .gitignore Re-Inclusion Pattern Shapes Apply

`.gitignore:187-195` blanket-ignores `.claude/hooks/*` and `.claude/rules/*`, then re-includes specific filenames via `!`-negation:

- Tracked (via `!`-negation): `.claude/hooks/poller-freshness.py`, `.claude/hooks/credential-scan.py`, `.claude/rules/bridge-essential.md`.
- Ignored (runtime-only): all other files under `.claude/hooks/` and `.claude/rules/`.

Of the 9 A2 files, exactly **2 are tracked** (`credential-scan.py`, `bridge-essential.md`) and **7 are ignored runtime artifacts**. This is not a bug — it is the project's established policy that keeps governance hook and rule content out of the committed tree by default.

Applied to Apply semantics:
- A git worktree rooted at `develop` HEAD inherits only the 2 tracked files.
- The other 7 files must be MATERIALIZED into the worktree from their owner-ratified sources before apply.
- After materialization, the planner sees all 9 on disk → emits no `add` actions for them → avoids the reject-keep-local violation.
- `git status --porcelain` in the worktree only reports modifications to the 2 tracked files (since the other 7 are ignored by `.gitignore`, which the worktree inherits).
- Commits on `e1-apply` therefore capture only the 2 tracked adopt-overwrite changes + the 23-action payload merge + the tracked-mode receipt. The other 7 A2 files are runtime artifacts of the worktree only and not in git history. This keeps the project's `.gitignore` policy intact on `e1-apply`.

**Decision (per -004 F1 required action #3):** Do NOT `git add -f` any of the 7 ignored A2 files. They remain ignored runtime files. This preserves the existing policy and minimizes the surface of Apply's committed diff.

## Phase Plan

### A.1 — Clean-tree worktree + side-branch creation

```bash
cd "/e/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"

DEVELOP_HEAD=$(git rev-parse develop)
echo "Worktree root: $DEVELOP_HEAD" > /tmp/e1-apply-evidence.txt

git worktree add ../agent-red-e1-apply -b e1-apply develop
cd ../agent-red-e1-apply

git status --porcelain > /tmp/e1-apply-cleantree-status-pre-a2.txt
test -z "$(cat /tmp/e1-apply-cleantree-status-pre-a2.txt)" && echo "OK clean tree (pre-A2)" || echo "FAIL clean tree"
```

**Expected:** `OK clean tree (pre-A2)`. `git status --porcelain` empty.

**If not clean:** STOP and file a REVISED Apply bridge. All subsequent commands in §A.2 through §D run in `../agent-red-e1-apply`; main workspace is READ-ONLY.

### A.2 — Materialize all 9 A2 files in worktree

For each A2 file, copy the appropriate source into the worktree path, with pre/post SHA-256 evidence. Main workspace is never written to; only `cat`/`cp` reads from it.

```bash
# Absolute paths
AR_MAIN="/e/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
WORKTREE="/e/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply"
GTKB_TEMPLATES=$(python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())")

cd "$WORKTREE"

echo "AR_MAIN: $AR_MAIN"                   >> /tmp/e1-apply-evidence.txt
echo "WORKTREE: $WORKTREE"                 >> /tmp/e1-apply-evidence.txt
echo "GTKB_TEMPLATES: $GTKB_TEMPLATES"     >> /tmp/e1-apply-evidence.txt

# Ensure directories exist (worktree only)
mkdir -p .claude/hooks .claude/rules

# --- Pre-copy SHA-256 of SOURCE files (truth-of-record for each A2 path) ---
echo "--- A2 source hashes ---" >> /tmp/e1-apply-evidence.txt

# 6 adopt-overwrite sources (GT-KB templates)
for rel in hooks/credential-scan.py hooks/spec-classifier.py \
           rules/bridge-essential.md rules/deliberation-protocol.md \
           rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    src="$GTKB_TEMPLATES/$rel"
    sha=$(sha256sum "$src" | cut -d' ' -f1)
    echo "SRC-TEMPLATE  $sha  $src" >> /tmp/e1-apply-evidence.txt
done

# 3 reject-keep-local sources (AR main workspace)
for rel in hooks/assertion-check.py hooks/destructive-gate.py hooks/scheduler.py; do
    src="$AR_MAIN/.claude/$rel"
    sha=$(sha256sum "$src" | cut -d' ' -f1)
    echo "SRC-AR-MAIN   $sha  $src" >> /tmp/e1-apply-evidence.txt
done

# --- Copy phase ---

# 6 adopt-overwrite copies (templates → worktree)
cp "$GTKB_TEMPLATES/hooks/credential-scan.py"       .claude/hooks/credential-scan.py
cp "$GTKB_TEMPLATES/hooks/spec-classifier.py"       .claude/hooks/spec-classifier.py
cp "$GTKB_TEMPLATES/rules/bridge-essential.md"      .claude/rules/bridge-essential.md
cp "$GTKB_TEMPLATES/rules/deliberation-protocol.md" .claude/rules/deliberation-protocol.md
cp "$GTKB_TEMPLATES/rules/file-bridge-protocol.md"  .claude/rules/file-bridge-protocol.md
cp "$GTKB_TEMPLATES/rules/loyal-opposition.md"      .claude/rules/loyal-opposition.md

# 3 reject-keep-local copies (main workspace → worktree)
cp "$AR_MAIN/.claude/hooks/assertion-check.py"  .claude/hooks/assertion-check.py
cp "$AR_MAIN/.claude/hooks/destructive-gate.py" .claude/hooks/destructive-gate.py
cp "$AR_MAIN/.claude/hooks/scheduler.py"        .claude/hooks/scheduler.py

# --- Post-copy SHA-256 of worktree targets; match verification ---
echo "--- A2 post-copy verification ---" >> /tmp/e1-apply-evidence.txt

# Adopt-overwrite: worktree file must MATCH GT-KB template
for rel in hooks/credential-scan.py hooks/spec-classifier.py \
           rules/bridge-essential.md rules/deliberation-protocol.md \
           rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    tgt=".claude/$rel"
    tpl="$GTKB_TEMPLATES/$rel"
    t_sha=$(sha256sum "$tgt" | cut -d' ' -f1)
    s_sha=$(sha256sum "$tpl" | cut -d' ' -f1)
    m=$([ "$t_sha" = "$s_sha" ] && echo "MATCH-TEMPLATE" || echo "MISMATCH-TEMPLATE")
    echo "$m  $t_sha  $tgt" >> /tmp/e1-apply-evidence.txt
done

# Reject-keep-local: worktree file must MATCH AR main-workspace file
for rel in hooks/assertion-check.py hooks/destructive-gate.py hooks/scheduler.py; do
    tgt=".claude/$rel"
    src="$AR_MAIN/.claude/$rel"
    t_sha=$(sha256sum "$tgt" | cut -d' ' -f1)
    s_sha=$(sha256sum "$src" | cut -d' ' -f1)
    m=$([ "$t_sha" = "$s_sha" ] && echo "MATCH-AR-MAIN" || echo "MISMATCH-AR-MAIN")
    echo "$m  $t_sha  $tgt" >> /tmp/e1-apply-evidence.txt
done
```

**Verification:** 9 MATCH-* lines, 0 MISMATCH-*.

### A.2.1 — Commit the 2 tracked adopt-overwrite files

Only `credential-scan.py` and `bridge-essential.md` are tracked via `.gitignore` `!`-negation. The other 4 adopt-overwrite files and all 3 reject-keep-local files are ignored by `.gitignore` and will not appear in `git status`; they persist only as worktree runtime artifacts.

```bash
git status --porcelain > /tmp/e1-apply-git-status-after-a2.txt

# Expected output (exactly 2 lines):
#  M .claude/hooks/credential-scan.py
#  M .claude/rules/bridge-essential.md

git add .claude/hooks/credential-scan.py .claude/rules/bridge-essential.md
git commit -m "e1-apply: adopt-overwrite 2 tracked A2 files from GT-KB v0.6.1 templates

Per owner-ratified A2 dispositions in Prepare -007 §Reconciliation Table:
- .claude/hooks/credential-scan.py   (tracked via .gitignore !-negation)
- .claude/rules/bridge-essential.md  (tracked via .gitignore !-negation)

These 2 files are git-tracked because .gitignore re-includes them. The other
4 adopt-overwrite files (spec-classifier.py, deliberation-protocol.md,
file-bridge-protocol.md, loyal-opposition.md) and 3 reject-keep-local files
(assertion-check.py, destructive-gate.py, scheduler.py) are materialized on
the worktree disk but remain gitignored runtime artifacts and are not
committed here; .gitignore policy preserved on e1-apply.

Pre/post SHA-256 evidence in /tmp/e1-apply-evidence.txt."
```

**Verification:** `git status --porcelain` empty post-commit. HEAD commit touches exactly 2 files.

### A.3 — Re-planner run inside worktree

Confirm the planner output inside the worktree (post-A2) matches the Prepare -007 mutating surface for A1 rows and emits zero actions for A2 paths.

```bash
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges 2>&1 \
    | tee /tmp/e1-apply-dryrun.txt

# Action counts
python -c "
import json, subprocess
from groundtruth_kb.project import upgrade
from pathlib import Path
plan = upgrade.plan_upgrade(Path('.'), ignore_inflight_bridges=True)
from collections import Counter
c = Counter(a.action for a in plan.actions)
print('total', len(plan.actions))
print('counts', dict(c))
# Assert 0 mutating actions on any A2 path
A2 = {
  '.claude/hooks/assertion-check.py', '.claude/hooks/credential-scan.py',
  '.claude/hooks/destructive-gate.py', '.claude/hooks/scheduler.py',
  '.claude/hooks/spec-classifier.py', '.claude/rules/bridge-essential.md',
  '.claude/rules/deliberation-protocol.md',
  '.claude/rules/file-bridge-protocol.md', '.claude/rules/loyal-opposition.md'
}
mutating = {'add', 'merge-event-hooks', 'append-gitignore'}
violations = [a for a in plan.actions if a.action in mutating and str(a.target).replace('\\\\','/') in A2]
print('A2 mutating violations', len(violations))
for a in violations:
    print('  VIOLATION', a.action, a.target)
" | tee /tmp/e1-apply-dryrun-summary.txt
```

**Expected:**
- `counts` contains 19 `add`, 3 `merge-event-hooks`, 1 `append-gitignore` = 23 mutating actions total.
- `A2 mutating violations 0`.

If any A2 mutating violation is reported, STOP — materialization failed.

### B — Run apply

```bash
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges 2>&1 \
    | tee /tmp/e1-apply-stdout.txt
```

**Expected mutating actions:**
- 19 `[ADD]` complete (A1 missing files).
- 3 `[MERGE-EVENT-HOOKS]` complete (`.claude/settings.json` registry merge).
- 1 `[APPEND-GITIGNORE]` complete (`.gitignore` one-pattern append).
- `MERGED payload into e1-apply @ <sha>` line.
- `RECEIPT tracked @ <sha> (<id>.json)` line.

**Expected post-apply topology on e1-apply branch:**
- `HEAD`   = receipt commit (tracked mode per rollback-receipts).
- `HEAD~1` = merge commit (two parents).
- `HEAD~2` = adopt-overwrite commit from §A.2.1.

**Capture:**
```bash
git rev-parse HEAD    > /tmp/e1-apply-head.txt
git rev-parse HEAD~1  > /tmp/e1-apply-merge.txt
git rev-parse HEAD~2  > /tmp/e1-apply-adopt-overwrite.txt
git rev-list --parents -n 1 HEAD~1 > /tmp/e1-apply-merge-parents.txt
ls .claude/upgrade-receipts/active/*.json > /tmp/e1-apply-receipt-files.txt
```

### C — Rollback validation

Dry-run `git revert -m 1 <merge_commit>` and inspect what would change.

```bash
MERGE_COMMIT=$(cat /tmp/e1-apply-merge.txt)

git revert -m 1 --no-commit "$MERGE_COMMIT"
git status --porcelain > /tmp/e1-apply-revert-status.txt

# Expected lines:
#   D  .claude/hooks/_delib_common.py            (19 ADD files reappear as deletions)
#   D  .claude/hooks/delib-preflight-gate.py
#   ... (all 19 A1 files listed as D)
#   M  .claude/settings.json                     (3 MERGE-EVENT-HOOKS reverted)
#   M  .gitignore                                (1 APPEND-GITIGNORE reverted)
#
# Expected NOT in revert-status.txt:
#   .claude/hooks/assertion-check.py    (reject-keep-local runtime file; not in git history, not reverted)
#   .claude/hooks/credential-scan.py    (adopt-overwrite committed pre-merge in HEAD~2, not reverted)
#   .claude/hooks/destructive-gate.py   (reject-keep-local runtime file; not in git history, not reverted)
#   .claude/hooks/scheduler.py          (reject-keep-local runtime file; not in git history, not reverted)
#   .claude/hooks/spec-classifier.py    (adopt-overwrite runtime file; not in git history, not reverted)
#   .claude/rules/bridge-essential.md   (adopt-overwrite committed pre-merge in HEAD~2, not reverted)
#   .claude/rules/deliberation-protocol.md (adopt-overwrite runtime file; not in git history, not reverted)
#   .claude/rules/file-bridge-protocol.md  (adopt-overwrite runtime file; not in git history, not reverted)
#   .claude/rules/loyal-opposition.md      (adopt-overwrite runtime file; not in git history, not reverted)
#   .claude/upgrade-receipts/active/*.json (receipt commit is post-merge, not reverted)

git revert --abort
git status --porcelain  # expected empty
```

**Why this is correct:** `git revert -m 1 <merge>` undoes exactly the merge's net diff against the first-parent mainline. The first-parent is the commit chain before the payload was merged (so it is `HEAD~2` = the adopt-overwrite commit). The revert therefore only undoes what the payload branch added/changed: the 19 A1 files + settings.json merge + .gitignore append. The 2 tracked adopt-overwrite files are already in `HEAD~2`'s tree, which is the mainline; revert does not re-remove them. The 7 runtime-only A2 files never entered git history, so revert cannot touch them either.

### D — Governance runtime validation (Phase ε)

Same 4 validation suites as -001/-003.

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

Expected: registry-merged counts.

#### D.4 Rule files

```bash
for rule in prime-builder bridge-poller-canonical prime-bridge-collaboration-protocol report-depth canonical-terminology.md canonical-terminology.toml; do
    test -f ".claude/rules/${rule}" && echo "OK rule ${rule}" || echo "FAIL rule ${rule}"
done
```

Expected: 6 `OK`, 0 `FAIL`.

### E — Main-workspace non-mutation proof

Prove the main workspace was not modified during Apply. Capture a before/after snapshot of the 9 A2 file SHAs in the main workspace:

```bash
cd "$AR_MAIN"
echo "--- Main workspace A2 SHAs after Apply ---" >> /tmp/e1-apply-evidence.txt
for rel in hooks/assertion-check.py hooks/credential-scan.py hooks/destructive-gate.py \
           hooks/scheduler.py hooks/spec-classifier.py rules/bridge-essential.md \
           rules/deliberation-protocol.md rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    sha=$(sha256sum ".claude/$rel" | cut -d' ' -f1)
    echo "MAIN-POST-APPLY  $sha  .claude/$rel" >> /tmp/e1-apply-evidence.txt
done
```

**Pre-Apply main-workspace SHAs are already captured in this proposal at lines referencing `LOCAL_EXISTS` in the evidence. Post-apply SHAs must be byte-identical.**

### F — Post-impl cleanup

Worktree and `e1-apply` branch remain until Codex VERIFIED. On VERIFIED, owner decides integration strategy; worktree cleanup is the last step.

```bash
cd "$AR_MAIN"
git worktree list > /tmp/e1-apply-worktree-list.txt
```

## Commit Plan

Two Prime-authored commits + two upgrade-flow-authored commits on `e1-apply`:

1. **Adopt-overwrite commit** (§A.2.1) — 2 tracked files (credential-scan.py, bridge-essential.md) from GT-KB v0.6.1 templates. The other 4 adopt-overwrite files are materialized to the worktree disk but remain gitignored runtime artifacts (not in this commit).
2. **Payload commit** (auto by `gt project upgrade --apply`, on a temporary `gt-upgrade-payload-<id>` branch) — 19 A1 ADDs + .claude/settings.json merge + .gitignore append.
3. **Merge commit** (auto by apply) — merges payload into `e1-apply`. Two parents: HEAD~2 (§A.2.1 adopt-overwrite) + payload commit.
4. **Receipt commit** (auto by tracked-mode `write_receipt`) — separate post-merge commit containing the receipt JSON.

Total: 2 Prime commits + 2 flow commits = 4 commits in `e1-apply` history (`gt-upgrade-payload-<id>` branch cleaned up by upgrade flow).

`e1-apply` is NOT merged to `develop` by this bridge.

## Post-Impl Report Contents

- **§Evidence:** worktree creation output, `/tmp/e1-apply-evidence.txt` hash proofs, §A.3 dry-run output, apply stdout, topology SHAs, revert-status output, main-workspace non-mutation proof, D.1–D.4 validation output.
- **§Topology:** HEAD/HEAD~1/HEAD~2 SHAs + merge-two-parents confirmation + receipt file contents.
- **§Adoption Summary:**

  | Category | Count | Git-tracked | Notes |
  |----------|-------|-------------|-------|
  | A1 missing-file `add` | 19 | yes (payload) | From planner |
  | A1 `merge-event-hooks` | 3 | yes (payload) | On `.claude/settings.json` |
  | A1 `append-gitignore` | 1 | yes (payload) | One pattern to `.gitignore` |
  | A2 `adopt-overwrite` — tracked | 2 | yes (HEAD~2) | credential-scan.py, bridge-essential.md |
  | A2 `adopt-overwrite` — runtime | 4 | no | spec-classifier.py, deliberation-protocol.md, file-bridge-protocol.md, loyal-opposition.md |
  | A2 `reject-keep-local` — runtime | 3 | no | assertion-check.py, destructive-gate.py, scheduler.py |
  | **Effective worktree changes** | **32** | — | (matches Prepare -007 reconciliation row count) |
  | **Git-committed changes** | **25** | — | 23 payload + 2 tracked adopt-overwrite |

- **§Rollback Proof:** revert-status listing that includes only the 23 payload-managed rows and excludes all 9 A2 files + receipt.
- **§Main-Workspace Non-Mutation Proof:** pre/post SHA-256 parity for all 9 A2 paths at `../Agent Red Customer Engagement/.claude/…`.
- **§Observed Limitations:**
  - The 4 ignored adopt-overwrite files and 3 reject-keep-local files are runtime-only artifacts of the `e1-apply` worktree; if the worktree is deleted, they must be re-materialized to re-run Apply.
  - A future `gt project upgrade` at a bumped scaffold_version may re-surface drift actions on any of the 9 A2 files. The copy-aside-for-reject and force-overwrite-for-adopt patterns must be re-applied on each future drift-gated upgrade until either (1) their registry `upgrade_policy` changes, (2) GT-KB gains a first-class per-file-skip flag, or (3) AR's customizations migrate upstream into GT-KB templates.

## Non-Scope for Apply

Unchanged from -001/-003:
- No integration into `develop`.
- No hook runtime testing against live Claude Code invocations.
- No metrics collection.
- No migration of AR customizations to GT-KB templates.
- No `--skip-file` feature request.

**Also out-of-scope:** B1 cleanup of the main AR workspace's 129 dirty items. Separate bridge (`agent-red-cto-cleanup`).

## Verification Gates

- [ ] `git worktree list` shows `../agent-red-e1-apply` on branch `e1-apply`.
- [ ] `git status --porcelain` in worktree is empty after each of the 2 Prime commits + 2 upgrade-flow commits land.
- [ ] 6 adopt-overwrite files in the worktree SHA-256-match their GT-KB v0.6.1 templates (§A.2 evidence: 6 `MATCH-TEMPLATE` lines).
- [ ] 3 reject-keep-local files in the worktree SHA-256-match the current main-workspace local files (§A.2 evidence: 3 `MATCH-AR-MAIN` lines).
- [ ] §A.2.1 `git status --porcelain` post-A2 shows exactly 2 modified paths (`credential-scan.py`, `bridge-essential.md`); the other 7 A2 paths do NOT appear (ignored by `.gitignore`).
- [ ] §A.3 planner summary shows `A2 mutating violations 0`.
- [ ] §A.3 counts: `add=19, merge-event-hooks=3, append-gitignore=1`.
- [ ] `git rev-list --parents -n 1 HEAD~1` shows 3 tokens (real merge commit).
- [ ] Exactly one receipt file at `.claude/upgrade-receipts/active/*.json`.
- [ ] Receipt JSON `merge_commit` matches HEAD~1 SHA.
- [ ] Revert-dry-run status excludes all 9 A2 files and the receipt; includes 19 A1 deletions + 2 `M` paths on settings.json + .gitignore.
- [ ] D.1–D.4 validation commands all report `OK`, zero `FAIL`.
- [ ] Main workspace post-Apply SHAs for 9 A2 paths byte-identical to pre-Apply (§E).

## Zero GT-KB Writes

Unchanged. Apply writes zero GT-KB source; reads only templates.

## Requested Verdict

**GO on REVISED-2 Apply implementation**, OR **NO-GO with specific findings** I can address in REVISED-3.

## Next Step After Codex GO

Execute §A.1 → §A.2 → §A.2.1 → §A.3 → §B → §C → §D → §E, capturing evidence. File post-impl report as next available version after this GO. On Codex VERIFIED, E1 thread closes. Owner decides integration strategy.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
