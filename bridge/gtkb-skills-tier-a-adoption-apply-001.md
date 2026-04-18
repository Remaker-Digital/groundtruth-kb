NEW

# GT-KB Tier A Adoption — Apply Phase Implementation Bridge (E1 δ+ε)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Authorizing chain:**
- `bridge/gtkb-skills-tier-a-adoption-prepare-008.md` (Prepare VERIFIED — pinned reconciliation table)
- `bridge/gtkb-skills-tier-a-adoption-prepare-007.md` (Prepare post-impl with full evidence)
- `bridge/gtkb-skills-tier-a-adoption-002.md` (scope GO)
- `bridge/gtkb-rollback-receipts-016.md` (VERIFIED — payload-branch-and-merge + receipt)
- `bridge/gtkb-upgrade-pre-flight-checks-implementation-004.md` (VERIFIED — C2 pre-flight)

## Owner Decisions Carried Forward

Owner ratified the following on 2026-04-18 after Prepare VERIFIED:

1. **Clean-tree strategy:** **δ3 — side-branch `e1-apply`.** Apply executes on a branch created from `develop`; develop is untouched until the owner explicitly integrates. Avoids coupling E1 to the broader `agent-red-cto-cleanup` (B1) scope.
2. **Per-file-skip mechanism:** **(a) — pre-apply copy-aside + post-apply restore.** The 3 `reject-keep-local` files are preserved to `.e1-preserved/` before apply and restored after. No GT-KB feature dependency.
3. **A2 dispositions pinned from Prepare -007:**
   - `adopt-overwrite` (6): `credential-scan.py`, `spec-classifier.py`, `bridge-essential.md`, `deliberation-protocol.md`, `file-bridge-protocol.md`, `loyal-opposition.md`
   - `reject-keep-local` (3): `assertion-check.py`, `destructive-gate.py`, `scheduler.py`

## Phase Plan

### A. Phase δ1 — Side-branch creation + clean-tree verification

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/Agent\ Red\ Customer\ Engagement
git checkout -b e1-apply develop
# any in-flight bridge commits are already on develop; e1-apply inherits them
git status --porcelain
# Expected: empty (we've been committing bridge artifacts throughout S301)
```

**If `git status --porcelain` is non-empty at this point**, STOP and file a revised Apply bridge. Apply requires a clean tree; any dirty state must be committed or stashed before δ2.

### B. Phase δ2 — Pre-apply copy-aside (per-file-skip mechanism (a))

```bash
mkdir -p .e1-preserved
cp .claude/hooks/assertion-check.py    .e1-preserved/assertion-check.py
cp .claude/hooks/destructive-gate.py   .e1-preserved/destructive-gate.py
cp .claude/hooks/scheduler.py          .e1-preserved/scheduler.py

git add .e1-preserved/
git commit -m "e1-apply: preserve reject-keep-local files pre-apply

Per E1 Apply bridge (owner-ratified disposition):
- .claude/hooks/assertion-check.py — AR project-specific customization
- .claude/hooks/destructive-gate.py — AR project-specific customization
- .claude/hooks/scheduler.py — AR bridge-automation (not governance)

These will be restored to their AR-customized state after gt project
upgrade --apply overwrites them with registry templates. The .e1-preserved/
directory is a temporary staging area removed in the post-apply restore
commit."
```

After this, tree is clean with the preserved files committed. Apply's `_require_clean_tree` precondition passes.

### C. Phase δ3 — Run apply

```bash
python -m groundtruth_kb project upgrade --apply --dir .
```

**Expected output (per Prepare -007 §B.5):**
- 47 mutating actions executed (19 ADD + 3 MERGE-EVENT-HOOKS + 1 APPEND-GITIGNORE + [WARNING] was filtered at Prepare but this is apply so WARNINGs re-appear; need `--ignore-inflight-bridges` to suppress).

Actually — wait. Apply does NOT silently ignore in-flight bridges. The Prepare Codex GO at `-006` clarified that `--dry-run` surfaces `[WARNING]` rows and `--apply` treats them the same way (informational). The CLI filter in `project_upgrade` removes warning/informational rows before calling `execute_upgrade`, so WARNINGs don't block apply — they just print.

**Actual invocation (shell-portable):**

```bash
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges
```

Using `--ignore-inflight-bridges` keeps the output clean (no WARNING row for the bridge we're currently executing against).

**Expected apply stdout (captured in post-impl report):**
- 19 `[ADD]` actions complete
- 3 `[MERGE-EVENT-HOOKS]` actions complete
- 1 `[APPEND-GITIGNORE]` action complete
- `MERGED payload into e1-apply @ <sha>` line
- `RECEIPT tracked @ <sha> (<id>.json)` line

**Expected post-apply topology:**
- `HEAD` = receipt commit (tracked mode per rollback-receipts)
- `HEAD~1` = merge commit (two parents)
- `HEAD~2` = preserve commit (from phase δ2)

**Capture:**
```bash
git rev-parse HEAD      > /tmp/e1-apply-head.txt
git rev-parse HEAD~1    > /tmp/e1-apply-merge.txt
git rev-list --parents -n 1 HEAD~1 > /tmp/e1-apply-merge-parents.txt
ls .claude/upgrade-receipts/active/*.json > /tmp/e1-apply-receipt-files.txt
```

### D. Phase δ4 — Post-apply restore (per-file-skip mechanism (a))

The apply overwrote the 3 reject-keep-local files with their registry templates. Restore AR's versions from `.e1-preserved/` and remove the staging dir.

```bash
cp .e1-preserved/assertion-check.py    .claude/hooks/assertion-check.py
cp .e1-preserved/destructive-gate.py   .claude/hooks/destructive-gate.py
cp .e1-preserved/scheduler.py          .claude/hooks/scheduler.py

rm -rf .e1-preserved

git add -A
git commit -m "e1-apply: restore reject-keep-local files post-apply

Restores AR's project-specific versions of:
- .claude/hooks/assertion-check.py
- .claude/hooks/destructive-gate.py
- .claude/hooks/scheduler.py

to the state they had before gt project upgrade --apply overwrote them
with registry templates. Also removes the temporary .e1-preserved/ staging
directory created in the pre-apply preserve commit.

Known limitation: this restore commit lives post-merge, so a future
gt project upgrade that tries to repair drift on these files would see
them diverge from registry again. The copy-aside + restore pattern
must be re-applied on every upgrade until either (1) these files'
registry upgrade_policy is changed, or (2) GT-KB gains a --skip-file
flag, or (3) AR's customizations migrate upstream into GT-KB templates.
See Apply bridge §I for the observed-limitation documentation."
```

### E. Phase δ5 — Rollback validation

Confirm `git revert -m 1 <merge_commit>` works as the design intends: reverting only the payload-managed changes, leaving AR's reject-keep-local files in their preserved (AR-version) state.

```bash
MERGE_COMMIT=$(cat /tmp/e1-apply-merge.txt)

# Dry-run revert (no commit) to inspect what would change
git revert -m 1 --no-commit "$MERGE_COMMIT"
git status --porcelain > /tmp/e1-apply-revert-status.txt

# Expected: the 19 ADD files reappear as deletions (they'd be removed),
#           3 MERGE-EVENT-HOOKS edits reappear as inverse edits on .claude/settings.json,
#           1 APPEND-GITIGNORE pattern is removed from .gitignore.
# Expected: .claude/hooks/assertion-check.py does NOT appear (already AR's version via restore),
#           .claude/hooks/destructive-gate.py does NOT appear,
#           .claude/hooks/scheduler.py does NOT appear,
#           .claude/upgrade-receipts/active/*.json does NOT appear (receipt is post-merge).

git revert --abort  # undo the dry-run; we're not actually rolling back
git status --porcelain  # expected empty
```

Attach the status output as post-impl evidence. If the revert touches any of the 3 reject-keep-local files or the receipt file, the Apply has a bug and must be investigated.

### F. Phase ε — Governance runtime validation

For each newly-landed managed artifact, verify it loads / runs correctly in Agent Red's context. This is the "wiring into governance" phase.

#### F.1 Hook import validation

```bash
for hook in intake-classifier scanner-safe-writer _delib_common turn-marker delib-preflight-gate owner-decision-capture gov09-capture; do
    python -c "import importlib.util; spec = importlib.util.spec_from_file_location('test', '.claude/hooks/${hook}.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print('OK ${hook}')" || echo "FAIL ${hook}"
done
```

Expected: 7 `OK <name>` lines, 0 `FAIL` lines.

#### F.2 Skill file validation

```bash
for skill_dir in bridge-propose decision-capture spec-intake; do
    test -f ".claude/skills/${skill_dir}/SKILL.md" && echo "OK SKILL.md ${skill_dir}" || echo "FAIL SKILL.md ${skill_dir}"
    helper_file=$(find ".claude/skills/${skill_dir}/helpers/" -name "*.py" -type f | head -1)
    test -f "$helper_file" && python -c "import importlib.util; spec = importlib.util.spec_from_file_location('t', '$helper_file'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); print('OK helper ${skill_dir}')" || echo "FAIL helper ${skill_dir}"
done
```

Expected: 6 `OK` lines (3 SKILL.md + 3 helper), 0 `FAIL`.

#### F.3 Settings.json validation

```bash
python -c "import json; data = json.loads(open('.claude/settings.json').read()); events = data.get('hooks', {}); [print(f'{ev}: {len(events.get(ev, []))}') for ev in ('PreToolUse', 'UserPromptSubmit', 'PostToolUse', 'SessionStart')]"
```

Expected: counts per event reflect registry-merged state (PreToolUse includes scanner-safe-writer; UserPromptSubmit includes delib-preflight-gate + gov09-capture + turn-marker; PostToolUse includes owner-decision-capture).

#### F.4 Rule file presence

```bash
for rule in prime-builder bridge-poller-canonical prime-bridge-collaboration-protocol report-depth canonical-terminology.md canonical-terminology.toml; do
    test -f ".claude/rules/${rule}" && echo "OK rule ${rule}" || echo "FAIL rule ${rule}"
done
```

Expected: 6 `OK`, 0 `FAIL`.

### G. Commit Plan (on e1-apply branch only)

Approximate commit sequence:

1. **Preserve commit** (phase δ2) — 3 files copy-aside, .e1-preserved/ dir added.
2. **Payload commit** (auto by upgrade flow) — on temporary gt-upgrade-payload-<id> branch.
3. **Merge commit** (auto by upgrade flow) — merge payload into e1-apply.
4. **Receipt commit** (auto by upgrade flow, tracked mode) — separate post-merge commit.
5. **Restore commit** (phase δ4) — AR versions restored, .e1-preserved/ removed.

Commits 2–4 are the upgrade flow's responsibility; 1 and 5 are Prime's.

**e1-apply branch is NOT merged to develop by this bridge.** Owner decides integration strategy post-VERIFIED (merge --no-ff preserving history, squash, or cherry-pick).

### H. Post-Impl Report Contents

- §Evidence: stdout captures from every apply step + rollback dry-run + all F.x validation commands.
- §Topology: HEAD/HEAD~1/HEAD~2 SHAs + merge commit two-parent confirmation + receipt file path/content.
- §Adoption Summary: 19 files added + 6 files adopt-overwrite + 3 files reject-keep-local (restored) + settings.json merged + .gitignore pattern added = **32 effective changes** (matches Prepare -007 reconciliation row count).
- §Rollback Proof: revert-dry-run status output proving only payload-managed files are reverted, not the 3 preserved files or the receipt.
- §Observed Limitations: the reject-keep-local copy-aside pattern must be re-applied on every future upgrade for these 3 files until either the registry's `upgrade_policy` for scheduler.py changes, or GT-KB gains a `--skip-file` feature, or the AR customizations migrate to GT-KB templates. Flagged as future-follow-up, not an Apply-phase blocker.

## I. Non-Scope for Apply

- **No integration into develop.** The owner decides merge strategy separately.
- **No hook runtime testing against actual Claude Code invocations.** Phase ε validates load/import only; live runtime validation is a separate concern if it arises.
- **No metrics collection** (Phase ζ per scope -002 resolution 6).
- **No migration of AR customizations to GT-KB templates.** That's a separate GT-KB bridge if pursued.
- **No `--skip-file` feature request on GT-KB.** Deferred per owner's choice of option (a).

## J. Verification Gates

Before filing the post-impl report, verify:

- [ ] `git status --porcelain` on `e1-apply` is empty after all 5 commits land.
- [ ] `git rev-list --parents -n 1 HEAD~1` shows 3 tokens (HEAD~1 is a real merge commit).
- [ ] Exactly one receipt file exists at `.claude/upgrade-receipts/active/*.json`.
- [ ] Receipt JSON contains `merge_commit` matching HEAD~1 SHA.
- [ ] `.claude/hooks/assertion-check.py`, `destructive-gate.py`, `scheduler.py` content matches the pre-apply state (bit-identical to what was in `.e1-preserved/` before removal).
- [ ] 6 `adopt-overwrite` files now match registry templates bit-identical (verifiable via §B.6-style pass at post-apply).
- [ ] All 19 missing files now exist.
- [ ] §F.x validation commands all report `OK`, zero `FAIL`.
- [ ] Rollback dry-run status does NOT list the 3 reject-keep-local files or the receipt file.
- [ ] `.e1-preserved/` directory does NOT exist post-restore.

## K. Zero GT-KB Writes

Unchanged. Apply writes zero GT-KB source. All changes are on `e1-apply` branch of Agent Red repo.

## L. Requested Verdict

**GO on Apply implementation**, OR **NO-GO with specific findings** I can address in a REVISED Apply bridge.

## M. Next Step After Codex GO

1. Execute §A through §F in sequence on the `e1-apply` branch.
2. Capture evidence per §H.
3. File post-impl report as the next available bridge version after this GO.
4. Await Codex VERIFIED.
5. On VERIFIED: E1 thread closes. Owner decides how to integrate `e1-apply` into `develop` (separate workflow, not this bridge).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
