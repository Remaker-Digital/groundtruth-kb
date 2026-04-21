REVISED

# GT-KB Tier A Adoption — Apply Phase Implementation Bridge (E1 δ+ε) — REVISED-4

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GOs addressed:** `bridge/gtkb-skills-tier-a-adoption-apply-006.md` (blockers F1+F2) AND `bridge/gtkb-skills-tier-a-adoption-apply-008.md` (findings F1+F2+F3)
**Prior versions:** `-007` REVISED-3 draft (filed unreviewed; superseded), `-005` REVISED-2, `-003` REVISED-1, `-001` NEW
**Prior reviews:** `-008` NO-GO, `-006` NO-GO, `-004` NO-GO, `-002` NO-GO

**Note on index state:** `-007` and `-008` were produced by prior scan spawns but never added to `bridge/INDEX.md`. I am adding both entries to the INDEX as part of filing this `-009`, so the full audit trail (REVISED-3 draft, its NO-GO, and this REVISED-4 response) is visible to Codex.

## Response to NO-GOs -006 and -008

The core design fix is a new **§A.0 `.gitignore` policy commit** that expands the narrow-tracking `!`-negation pattern to cover all 19 A1 paths + 6 adopt-overwrite paths + rollback-receipt subtree. It lands on `e1-apply` before any materialization or `gt project upgrade --apply` invocation. **§A.0.1** proves the expansion works via `git check-ignore --no-index` on every affected path and asserts `resolve_receipt_mode()` returns `tracked`.

| Finding | Severity | Resolution |
|---------|----------|------------|
| -006 F1 — 19 A1 `[ADD]` files are `.gitignore`'d; `git add -A` won't stage them | Blocker | **§A.0 (new)** expands `!`-negation to cover all 19 A1 paths. **§A.0.1** proves all 19 return exit 1. After §A.0, `_commit_payload()`'s `git add -A` stages all 19 into the payload commit. |
| -006 F2 — Receipt path `.gitignore`'d; `resolve_receipt_mode()` returns `filesystem` | Blocker | **§A.0** adds 2-line receipt re-inclusion. **§A.0.1** asserts `resolve_receipt_mode() == 'tracked'`. Tracked-mode post-merge receipt commit at `HEAD` restored. |
| -008 F1 — `.gitignore` exception commit was missing executable content; -007 mis-referenced -005 as the source | Blocker | **§A.0** contains the **exact block content** to insert, **exact `cp`/`diff`/`git add`/`git commit` commands**, SHA-256 evidence capture, and the commit message. -009 does NOT cite -005 for the `.gitignore` step because -005 has none. |
| -008 F2 — -007 mixed "git-committed" and runtime-only A2 models (stage-2 only; claim stage-6) | Blocker | **§A.0** re-includes all 6 adopt-overwrite paths (2 pre-existing + 4 newly tracked). **§A.2.1** stages all 6 in one commit. The 3 reject-keep-local files **remain explicitly runtime-only**; §A.2.1 does NOT stage them; §C revert gate uses `git status --porcelain --ignored` to show them; adoption summary classifies them as non-tracked. One coherent model: committed = 19 A1 + 6 adopt-overwrite + receipt + `.gitignore` policy; runtime = 3 reject-keep-local. |
| -008 F3 — `check-ignore` shell gate accepted any non-zero exit as "NOT-IGNORED", masking fatal errors | Medium | **§A.0.1 (NEW)** uses a 3-way branch: exit 0 → `FAIL IGNORED`; exit 1 → `NOT-IGNORED`; anything else → `FAIL CHECK-IGNORE-ERROR (rc=N)` → STOP. Matches GT-KB's own `resolve_receipt_mode()` convention. |

## Cross-NO-GO Discipline

Every prior finding re-resolved here (pattern from `gtkb-rollback-receipts-013` per S300 lesson).

| Source | Required action | Status in -009 |
|--------|-----------------|----------------|
| -002 F1 | Executable A2 adopt-overwrite mechanism | §A.2 manual copy from templates; §A.2.1 stages all 6 |
| -002 F1 | Reassess copy-aside/restore need | Replaced with forward-materialization from main workspace for 3 RKL paths |
| -002 F1 | Prove mutating surface includes every adopt-overwrite file | §A.3 planner run proves A2 files do not appear (present on disk; post-A.0 they're tracked) |
| -002 F2 | Clean-tree evidence | §A.1 worktree; §A.0 + §A.2.1 commits leave tree clean |
| -002 — isolation from develop | Preserved: Apply runs in worktree + `e1-apply`; `develop` untouched |
| -004 F1 | State A2 source of truth | 6 AO ← GT-KB v0.6.1 templates; 3 RKL ← main workspace local bytes (unchanged from -005) |
| -004 F1 | Materialize RKL with source paths + hash evidence | §A.2 sources from main workspace with SHA-256 pre-copy capture |
| -004 F1 | Decide tracked/ignored disposition for 3 RKL files | **3 RKL files remain ignored runtime artifacts.** §A.0 does NOT re-include them. §A.2.1 does NOT stage them. |
| -004 F1 | Recompute mutating surface post A2 setup | §A.3 runs `plan_upgrade` in worktree after §A.0 + §A.2 + §A.2.1 |
| -004 F1 | Update adoption summary + rollback proof | §Post-Impl Report §Adoption Summary reclassified; §C rollback proof shows 19 A1 D rows |
| -006 F1 | Decide A1 persistence | **COMMITTED.** §Owner-Persistence Decision. |
| -006 F1 | Prove A1 not ignored | **§A.0.1 3-way gate.** All 19 exit 1. |
| -006 F2 | Decide receipt mode | **TRACKED.** §Owner-Persistence Decision. |
| -006 F2 | Prove receipt re-inclusion before `resolve_receipt_mode` | **§A.0.1 `resolve_receipt_mode()` assertion.** |
| -006 observation | Show ignored runtime artifacts explicitly | §C revert gate uses `git status --porcelain --ignored` and extracts RKL `!!` rows explicitly. |
| **-008 F1** | **Full executable `.gitignore` edit + commit step** | **§A.0 contains exact block, `cp`, `diff`, `git add`, `git commit` commands.** |
| **-008 F1** | **Stop referencing -005 for the `.gitignore` step** | **-009 cites -005 only for A2 materialization (§A.2) and disposition pinning (Owner Decisions).** The `.gitignore` step is introduced in §A.0 as new work. |
| **-008 F1** | **Ordering vs. documented receipt re-inclusion block (last-match-wins)** | **§Insight — `.gitignore` semantics** explicitly discusses ordering and chooses the narrower 2-line receipt re-inclusion (NOT the docs' 4-line block) to preserve per-file `!`-negations. |
| **-008 F2** | **One coherent A2 persistence model** | **Committed:** 6 AO files (§A.2.1 stages all 6). **Runtime-only:** 3 RKL files (§A.0 does not touch; §A.2.1 does not stage). Adoption summary + rollback proof aligned. |
| **-008 F2** | **Status gate expectations aligned with ignored runtime files** | **§C uses `git status --porcelain --ignored`** + targeted `!!` grep for RKL files. Plain `git status --porcelain` is used for change detection where empty is expected (post-commit tree). |
| **-008 F3** | **3-way `check-ignore` gate (exit 0 / exit 1 / other)** | **§A.0.1 branch: rc=0 → FAIL IGNORED; rc=1 → NOT-IGNORED; other → FAIL CHECK-IGNORE-ERROR → STOP.** |
| -008 checklist | Keep `resolve_receipt_mode()` precheck before apply | **§A.0.1 calls `resolve_receipt_mode()` directly after the `.gitignore` commit; asserts `mode='tracked'` before §A.2 proceeds.** |

## Owner-Persistence Decision (explicit per -006 "Decision Needed" and -008 Finding 2)

**DECISION:** **Committed adoption** for the 19 A1 governance hooks + rules + skills, the 6 adopt-overwrite A2 files, and the rollback receipt. **Runtime-only** for the 3 reject-keep-local A2 files (`assertion-check.py`, `destructive-gate.py`, `scheduler.py`).

### Rationale

1. **S294 `.claude/rules/bridge-essential.md` precedent:** owner-ratified lesson *"if it is essential, it must be tracked"* — established when `.claude/` blanket-ignore silently hid bridge visibility infrastructure outside git.
2. **19 A1 + 6 AO files match the "essential governance" category** (credential-scan, scanner-safe-writer, deliberation common, turn-marker, pre-flight gate, owner-decision capture, GOV-09 classifier, 3 skills, canonical-terminology surface, rule docs). Leaving them untracked reproduces the S294 failure mode.
3. **3 RKL files stay runtime-only** because the Prepare -007 owner disposition `reject-keep-local` says "keep AR's customized content", and their current state is ignored runtime files. This bridge does NOT re-classify them; a future bridge can.
4. **Chose narrow per-file `!`-negation expansion (Option A2)** over the GT-KB-docs "remove broad `.claude/` ignore entirely" (Option A1) or "leave runtime-only" (Option B). A1 has wider blast radius; B contradicts S294.
5. **The docs' 4-line receipt re-inclusion block is unsuitable here** because its Line 2 `/.claude/*` would shadow per-file `!`-negations on last-match-wins. Use the simpler 2-line variant.
6. **If owner prefers A1 or B** — NO-GO -009 with preference, and I file REVISED-5.

### Owner-visible implications

- `.gitignore` gains ~26 new lines (per-file `!`-negations + section headers).
- `e1-apply` gains 1 additional commit at `HEAD~3` below the adopt-overwrite at `HEAD~2`.
- Future Tier A additions beyond Phase A require a new bridge for each `!`-negation expansion (no auto-expansion pre-authorized).

## Insight — `.gitignore` semantics and last-match-wins ordering

`.gitignore` uses last-match-wins. §A.0's block preserves and extends the existing per-file pattern:

- For `.claude/hooks/foo.py`: order is `.claude/hooks/*` then `!.claude/hooks/foo.py`. My expansion appends the 8 new `!`-negations inside the existing `hooks/` re-inclusion section so last-match still wins.
- For `.claude/skills/<name>/**`: add `!.claude/skills/` + `.claude/skills/*` + per-subdir `!.claude/skills/<name>/` + `!.claude/skills/<name>/**`. Git requires parent-dir re-inclusion before nested files can be re-included.
- For the receipt subtree: `!.claude/upgrade-receipts/` + `!.claude/upgrade-receipts/**` (NOT the docs' 4-line block, which would shadow per-file `!`-negations via its `/.claude/*` Line 2).

Live planner inspection confirms GT-KB's `append-gitignore` will append `.claude/hooks/*.log` — orthogonal to every `!`-negation added.

## Owner Decisions Carried Forward (pinned from Prepare -007 §Reconciliation Table)

- **Clean-tree strategy:** δ3 — side-branch `e1-apply` on separate worktree.
- **Per-file-skip mechanism:** (a) — pre-apply forward-materialization.
- **A2 dispositions (9 paths):** 6 adopt-overwrite, 3 reject-keep-local.
- **A2 source of truth:** AO ← GT-KB v0.6.1 templates; RKL ← main-workspace local bytes. Main workspace is READ-ONLY throughout Apply.

## Phase Plan

### A.1 — Clean-tree worktree + side-branch creation

```bash
cd "/e/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"

DEVELOP_HEAD=$(git rev-parse develop)
echo "Worktree root: $DEVELOP_HEAD" > /tmp/e1-apply-evidence.txt

git worktree add ../agent-red-e1-apply -b e1-apply develop
cd ../agent-red-e1-apply

git status --porcelain > /tmp/e1-apply-cleantree-status-pre-a0.txt
test -z "$(cat /tmp/e1-apply-cleantree-status-pre-a0.txt)" && echo "OK clean tree (pre-A0)" || { echo "FAIL clean tree"; exit 1; }
```

**Expected:** `OK clean tree (pre-A0)`. Main workspace READ-ONLY for §A.0–§F.

### A.0 — `.gitignore` policy commit (NEW — discharges -006 F1/F2 and -008 F1/F2)

Expand the narrow-tracking `!`-negation pattern. First commit on `e1-apply`.

```bash
cp .gitignore /tmp/e1-apply-gitignore-before.txt
sha256sum .gitignore > /tmp/e1-apply-gitignore-before.sha
```

**Patch target** — replace the existing "AI Assistant" block (`.gitignore` lines ≈180–195 on develop HEAD) with the following expanded block. The preceding `.claude/` comment banner and succeeding blank line + `.kiro/` section are unchanged.

**Exact block to install (copy-pasteable into the worktree `.gitignore`):**

```gitignore
# =============================================================================
# AI Assistant
# =============================================================================
# NOTE: we deliberately ignore the CONTENTS of .claude/ (with /*), not the
# directory itself. This is required so that !-negations below can re-include
# specific files. A blanket ".claude/" ignore would shadow all negations.
# Do not collapse these patterns without reading .claude/rules/bridge-essential.md.
.claude/*
!.claude/settings.json
!.claude/hooks/
.claude/hooks/*
!.claude/hooks/poller-freshness.py
!.claude/hooks/credential-scan.py
# Tier A governance hooks (tracked per S294 "essential → tracked"; adopted via
# bridge/gtkb-skills-tier-a-adoption-apply-009.md)
!.claude/hooks/intake-classifier.py
!.claude/hooks/scanner-safe-writer.py
!.claude/hooks/_delib_common.py
!.claude/hooks/turn-marker.py
!.claude/hooks/delib-preflight-gate.py
!.claude/hooks/owner-decision-capture.py
!.claude/hooks/gov09-capture.py
!.claude/hooks/spec-classifier.py
!.claude/rules/
.claude/rules/*
!.claude/rules/bridge-essential.md
# Tier A governance rules (tracked per S294 "essential → tracked")
!.claude/rules/prime-builder.md
!.claude/rules/bridge-poller-canonical.md
!.claude/rules/prime-bridge-collaboration-protocol.md
!.claude/rules/report-depth.md
!.claude/rules/canonical-terminology.md
!.claude/rules/canonical-terminology.toml
!.claude/rules/deliberation-protocol.md
!.claude/rules/file-bridge-protocol.md
!.claude/rules/loyal-opposition.md
# Tier A governance skills (tracked per S294 "essential → tracked")
!.claude/skills/
.claude/skills/*
!.claude/skills/bridge-propose/
!.claude/skills/bridge-propose/**
!.claude/skills/decision-capture/
!.claude/skills/decision-capture/**
!.claude/skills/spec-intake/
!.claude/skills/spec-intake/**
# Tracked upgrade-receipts (opt-in; see docs/reference/upgrade-receipts.md)
!.claude/upgrade-receipts/
!.claude/upgrade-receipts/**
```

Editor: `Write`-tool call on the worktree `.gitignore` path **only** (main workspace is not touched). The block replaces the pre-existing narrow block; all other `.gitignore` content is preserved. If Prime uses a line-based editor (sed/awk/Python), the pre-block and post-block context markers are the comment banner above and the blank line before `.kiro/`.

```bash
cp .gitignore /tmp/e1-apply-gitignore-after.txt
sha256sum .gitignore > /tmp/e1-apply-gitignore-after.sha
diff /tmp/e1-apply-gitignore-before.txt /tmp/e1-apply-gitignore-after.txt \
    > /tmp/e1-apply-gitignore-diff.txt

git add .gitignore
git commit -m "e1-apply: expand .gitignore !-negation for Tier A governance artifacts + tracked receipts

Per Owner-Persistence Decision in bridge/gtkb-skills-tier-a-adoption-apply-009.md:
committed adoption for 19 A1 governance hooks/rules/skills, 6 adopt-overwrite
A2 files, and rollback receipt. 3 reject-keep-local A2 files remain ignored
runtime artifacts.

Rationale: S294 precedent 'if it is essential, it must be tracked' established
when .claude/ blanket-ignore silently hid bridge visibility infrastructure
outside git. Same failure mode applies to Tier A governance artifacts.

Adds narrow per-file !-negation for:
- 8 hooks: intake-classifier, scanner-safe-writer, _delib_common, turn-marker,
  delib-preflight-gate, owner-decision-capture, gov09-capture, spec-classifier
- 9 rules: prime-builder, bridge-poller-canonical,
  prime-bridge-collaboration-protocol, report-depth, canonical-terminology
  (.md + .toml), deliberation-protocol, file-bridge-protocol, loyal-opposition
- 3 skills subtrees: bridge-propose, decision-capture, spec-intake
- 1 receipt subtree: .claude/upgrade-receipts/**

SHA-256 pre/post: see /tmp/e1-apply-gitignore-{before,after}.sha."
```

### A.0.1 — Ignore-surface verification (3-way gate; discharges -008 F3)

Prove every affected path behaves as designed. **Shell gate uses 3-way branch per -008 F3:** exit 0 = `FAIL IGNORED`, exit 1 = `NOT-IGNORED`, other = `FAIL CHECK-IGNORE-ERROR → STOP`.

```bash
check_path() {
    local path="$1"
    local expected="$2"  # "notignored" or "ignored"
    git check-ignore --no-index -- "$path" >/dev/null 2>&1; local rc=$?
    if [ "$rc" -eq 0 ]; then
        state="IGNORED"
    elif [ "$rc" -eq 1 ]; then
        state="NOT-IGNORED"
    else
        echo "FAIL CHECK-IGNORE-ERROR  rc=$rc  $path" >> /tmp/e1-apply-evidence.txt
        echo "STOP: git check-ignore returned unexpected exit $rc on $path" >&2
        exit 1
    fi

    if [ "$expected" = "notignored" ] && [ "$state" = "NOT-IGNORED" ]; then
        echo "OK NOT-IGNORED  $path" >> /tmp/e1-apply-evidence.txt
        return 0
    elif [ "$expected" = "ignored" ] && [ "$state" = "IGNORED" ]; then
        echo "OK IGNORED      $path" >> /tmp/e1-apply-evidence.txt
        return 0
    else
        echo "FAIL $state (expected $expected)  $path" >> /tmp/e1-apply-evidence.txt
        return 1
    fi
}

echo "--- A.0.1 A1 ignore-state proof (19 paths expected NOT-IGNORED) ---" >> /tmp/e1-apply-evidence.txt
A1_PATHS=(
  .claude/hooks/intake-classifier.py
  .claude/hooks/scanner-safe-writer.py
  .claude/hooks/_delib_common.py
  .claude/hooks/turn-marker.py
  .claude/hooks/delib-preflight-gate.py
  .claude/hooks/owner-decision-capture.py
  .claude/hooks/gov09-capture.py
  .claude/rules/prime-builder.md
  .claude/rules/bridge-poller-canonical.md
  .claude/rules/prime-bridge-collaboration-protocol.md
  .claude/rules/report-depth.md
  .claude/rules/canonical-terminology.md
  .claude/rules/canonical-terminology.toml
  .claude/skills/decision-capture/SKILL.md
  .claude/skills/decision-capture/helpers/record_decision.py
  .claude/skills/bridge-propose/SKILL.md
  .claude/skills/bridge-propose/helpers/write_bridge.py
  .claude/skills/spec-intake/SKILL.md
  .claude/skills/spec-intake/helpers/spec_intake.py
)
FAIL=0
for p in "${A1_PATHS[@]}"; do
    check_path "$p" notignored || FAIL=$((FAIL + 1))
done
echo "A1 FAIL count: $FAIL" >> /tmp/e1-apply-evidence.txt
test "$FAIL" -eq 0 || { echo "STOP — A1 ignore-check failures"; exit 1; }

echo "--- A.0.1 Adopt-overwrite ignore-state proof (6 paths expected NOT-IGNORED) ---" >> /tmp/e1-apply-evidence.txt
AO_PATHS=(
  .claude/hooks/credential-scan.py
  .claude/hooks/spec-classifier.py
  .claude/rules/bridge-essential.md
  .claude/rules/deliberation-protocol.md
  .claude/rules/file-bridge-protocol.md
  .claude/rules/loyal-opposition.md
)
FAIL=0
for p in "${AO_PATHS[@]}"; do
    check_path "$p" notignored || FAIL=$((FAIL + 1))
done
echo "AO FAIL count: $FAIL" >> /tmp/e1-apply-evidence.txt
test "$FAIL" -eq 0 || { echo "STOP — AO ignore-check failures"; exit 1; }

echo "--- A.0.1 Reject-keep-local ignore-state proof (3 paths expected IGNORED) ---" >> /tmp/e1-apply-evidence.txt
RKL_PATHS=(
  .claude/hooks/assertion-check.py
  .claude/hooks/destructive-gate.py
  .claude/hooks/scheduler.py
)
FAIL=0
for p in "${RKL_PATHS[@]}"; do
    check_path "$p" ignored || FAIL=$((FAIL + 1))
done
echo "RKL FAIL count: $FAIL" >> /tmp/e1-apply-evidence.txt
test "$FAIL" -eq 0 || { echo "STOP — RKL ignore-check unexpected results"; exit 1; }

echo "--- A.0.1 Receipt path ignore-state proof (expected NOT-IGNORED) ---" >> /tmp/e1-apply-evidence.txt
RECEIPT_PROBE=".claude/upgrade-receipts/active/probe-$(date +%s).json"
check_path "$RECEIPT_PROBE" notignored || { echo "STOP — Receipt path still ignored"; exit 1; }

echo "--- A.0.1 resolve_receipt_mode() assertion ---" >> /tmp/e1-apply-evidence.txt
python -c "
from pathlib import Path
from groundtruth_kb.project.rollback import resolve_receipt_mode
resolved = resolve_receipt_mode(Path('.'), Path('.claude/upgrade-receipts/active/probe.json'))
print('mode:', resolved.mode)
print('notes:', resolved.notes)
assert resolved.mode == 'tracked', f'Expected tracked, got {resolved.mode}'
" 2>&1 | tee -a /tmp/e1-apply-evidence.txt
```

**Verification:** A1 FAIL=0, AO FAIL=0, RKL FAIL=0, Receipt OK, `resolve_receipt_mode` returns `mode='tracked'`. Any `FAIL CHECK-IGNORE-ERROR` stops the flow.

### A.2 — Materialize all 9 A2 files in worktree (unchanged from -005 semantics)

```bash
AR_MAIN="/e/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement"
WORKTREE="/e/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply"
GTKB_TEMPLATES=$(python -c "from groundtruth_kb import get_templates_dir; print(get_templates_dir())")

cd "$WORKTREE"
mkdir -p .claude/hooks .claude/rules

echo "--- A2 source hashes ---" >> /tmp/e1-apply-evidence.txt
for rel in hooks/credential-scan.py hooks/spec-classifier.py \
           rules/bridge-essential.md rules/deliberation-protocol.md \
           rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    src="$GTKB_TEMPLATES/$rel"
    echo "SRC-TEMPLATE  $(sha256sum "$src" | cut -d' ' -f1)  $src" >> /tmp/e1-apply-evidence.txt
done
for rel in hooks/assertion-check.py hooks/destructive-gate.py hooks/scheduler.py; do
    src="$AR_MAIN/.claude/$rel"
    echo "SRC-AR-MAIN   $(sha256sum "$src" | cut -d' ' -f1)  $src" >> /tmp/e1-apply-evidence.txt
done

cp "$GTKB_TEMPLATES/hooks/credential-scan.py"       .claude/hooks/credential-scan.py
cp "$GTKB_TEMPLATES/hooks/spec-classifier.py"       .claude/hooks/spec-classifier.py
cp "$GTKB_TEMPLATES/rules/bridge-essential.md"      .claude/rules/bridge-essential.md
cp "$GTKB_TEMPLATES/rules/deliberation-protocol.md" .claude/rules/deliberation-protocol.md
cp "$GTKB_TEMPLATES/rules/file-bridge-protocol.md"  .claude/rules/file-bridge-protocol.md
cp "$GTKB_TEMPLATES/rules/loyal-opposition.md"      .claude/rules/loyal-opposition.md
cp "$AR_MAIN/.claude/hooks/assertion-check.py"  .claude/hooks/assertion-check.py
cp "$AR_MAIN/.claude/hooks/destructive-gate.py" .claude/hooks/destructive-gate.py
cp "$AR_MAIN/.claude/hooks/scheduler.py"        .claude/hooks/scheduler.py

echo "--- A2 post-copy verification ---" >> /tmp/e1-apply-evidence.txt
for rel in hooks/credential-scan.py hooks/spec-classifier.py \
           rules/bridge-essential.md rules/deliberation-protocol.md \
           rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    t_sha=$(sha256sum ".claude/$rel" | cut -d' ' -f1)
    s_sha=$(sha256sum "$GTKB_TEMPLATES/$rel" | cut -d' ' -f1)
    m=$([ "$t_sha" = "$s_sha" ] && echo "MATCH-TEMPLATE" || echo "MISMATCH-TEMPLATE")
    echo "$m  $t_sha  .claude/$rel" >> /tmp/e1-apply-evidence.txt
done
for rel in hooks/assertion-check.py hooks/destructive-gate.py hooks/scheduler.py; do
    t_sha=$(sha256sum ".claude/$rel" | cut -d' ' -f1)
    s_sha=$(sha256sum "$AR_MAIN/.claude/$rel" | cut -d' ' -f1)
    m=$([ "$t_sha" = "$s_sha" ] && echo "MATCH-AR-MAIN" || echo "MISMATCH-AR-MAIN")
    echo "$m  $t_sha  .claude/$rel" >> /tmp/e1-apply-evidence.txt
done
```

**Verification:** 9 MATCH-* lines, 0 MISMATCH-*.

### A.2.1 — Commit all 6 adopt-overwrite files (tracked after §A.0)

After §A.0, all 6 adopt-overwrite paths are trackable. The 3 RKL files remain ignored and do NOT appear in `git status`.

```bash
git status --porcelain > /tmp/e1-apply-git-status-after-a2.txt
# Expected (exactly 6 lines, no RKL paths):
#  M .claude/hooks/credential-scan.py         (pre-existing tracked)
#  M .claude/rules/bridge-essential.md        (pre-existing tracked)
# ?? .claude/hooks/spec-classifier.py         (newly trackable)
# ?? .claude/rules/deliberation-protocol.md   (newly trackable)
# ?? .claude/rules/file-bridge-protocol.md    (newly trackable)
# ?? .claude/rules/loyal-opposition.md        (newly trackable)

# Also verify RKL paths do NOT appear in status (they should be ignored)
if grep -E '^(\?\?|[ MA]) \.claude/hooks/(assertion-check|destructive-gate|scheduler)\.py' \
    /tmp/e1-apply-git-status-after-a2.txt; then
    echo "STOP — RKL files unexpectedly appear in git status; .gitignore expansion went too far"
    exit 1
fi

git add .claude/hooks/credential-scan.py .claude/hooks/spec-classifier.py \
        .claude/rules/bridge-essential.md .claude/rules/deliberation-protocol.md \
        .claude/rules/file-bridge-protocol.md .claude/rules/loyal-opposition.md
git commit -m "e1-apply: adopt-overwrite 6 A2 files from GT-KB v0.6.1 templates

Per owner-ratified A2 dispositions in Prepare -007 §Reconciliation Table.
All 6 files become git-tracked here following §A.0 .gitignore expansion
(per bridge/gtkb-skills-tier-a-adoption-apply-009.md Owner-Persistence Decision).

- .claude/hooks/credential-scan.py         (re-adopted; previously tracked)
- .claude/hooks/spec-classifier.py         (newly tracked)
- .claude/rules/bridge-essential.md        (re-adopted; previously tracked)
- .claude/rules/deliberation-protocol.md   (newly tracked)
- .claude/rules/file-bridge-protocol.md    (newly tracked)
- .claude/rules/loyal-opposition.md        (newly tracked)

3 reject-keep-local files (assertion-check.py, destructive-gate.py,
scheduler.py) remain ignored runtime artifacts on the worktree disk;
.gitignore continues to ignore them; they are NOT staged here."
```

**Verification:** `git status --porcelain` empty post-commit (ignored RKL files hidden by default per their disposition).

### A.3 — Re-planner run inside worktree

```bash
python -m groundtruth_kb project upgrade --dry-run --dir . --ignore-inflight-bridges 2>&1 \
    | tee /tmp/e1-apply-dryrun.txt

python - <<'PYEOF' | tee /tmp/e1-apply-dryrun-summary.txt
from pathlib import Path
from collections import Counter
from groundtruth_kb.project import upgrade
actions = upgrade.plan_upgrade(Path('.'), ignore_inflight_bridges=True)
c = Counter(a.action for a in actions)
print('total', len(actions))
print('counts', dict(c))
A2 = {
  '.claude/hooks/assertion-check.py', '.claude/hooks/credential-scan.py',
  '.claude/hooks/destructive-gate.py', '.claude/hooks/scheduler.py',
  '.claude/hooks/spec-classifier.py', '.claude/rules/bridge-essential.md',
  '.claude/rules/deliberation-protocol.md',
  '.claude/rules/file-bridge-protocol.md', '.claude/rules/loyal-opposition.md'
}
mutating = {'add', 'merge-event-hooks', 'append-gitignore'}
violations = [a for a in actions if a.action in mutating and str(a.file).replace('\\','/') in A2]
print('A2 mutating violations', len(violations))
for a in violations:
    print('  VIOLATION', a.action, a.file)
PYEOF
```

**Expected:** `counts` has `add=19, merge-event-hooks=3, append-gitignore=1`. `A2 mutating violations 0`.

### B — Run apply

```bash
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges 2>&1 \
    | tee /tmp/e1-apply-stdout.txt
```

**Expected stdout:**
- 19 `[ADD]` complete (all staged because §A.0 removed ignore coverage).
- 3 `[MERGE-EVENT-HOOKS]` complete.
- 1 `[APPEND-GITIGNORE]` complete (appends `.claude/hooks/*.log`; orthogonal to §A.0).
- `MERGED payload into e1-apply @ <sha>`.
- `RECEIPT tracked @ <sha> (<id>.json)`. If `RECEIPT filesystem` appears → STOP.

**Topology on `e1-apply`:**
- `HEAD`   = receipt commit (tracked mode).
- `HEAD~1` = merge commit (two parents: `HEAD~2` + payload branch).
- `HEAD~2` = §A.2.1 adopt-overwrite commit.
- `HEAD~3` = §A.0 `.gitignore` policy commit.

```bash
git rev-parse HEAD   > /tmp/e1-apply-head.txt
git rev-parse HEAD~1 > /tmp/e1-apply-merge.txt
git rev-parse HEAD~2 > /tmp/e1-apply-adopt-overwrite.txt
git rev-parse HEAD~3 > /tmp/e1-apply-gitignore-policy.txt
git rev-list --parents -n 1 HEAD~1 > /tmp/e1-apply-merge-parents.txt
ls .claude/upgrade-receipts/active/*.json > /tmp/e1-apply-receipt-files.txt
git log --oneline -n 5 HEAD > /tmp/e1-apply-commit-log.txt

# Payload-commit staging proof (verification gate per -006 non-blocking guidance)
PAYLOAD_COMMIT=$(git rev-parse "HEAD~1^2")
git show --name-only --format= "$PAYLOAD_COMMIT" > /tmp/e1-apply-payload-files.txt
# Expected: 21 paths — 19 A1 + .claude/settings.json + .gitignore
```

### C — Rollback validation

```bash
MERGE_COMMIT=$(cat /tmp/e1-apply-merge.txt)

git revert -m 1 --no-commit "$MERGE_COMMIT"
git status --porcelain           > /tmp/e1-apply-revert-status.txt
git status --porcelain --ignored > /tmp/e1-apply-revert-status-with-ignored.txt

# Expected in plain status: 19 `D` rows (A1 paths) + 2 `M` rows (settings.json, .gitignore)
DROWS=$(grep -c '^D  ' /tmp/e1-apply-revert-status.txt)
MROWS=$(grep -c '^M  ' /tmp/e1-apply-revert-status.txt)
echo "D rows: $DROWS  (expected 19)" >> /tmp/e1-apply-evidence.txt
echo "M rows: $MROWS  (expected 2)"  >> /tmp/e1-apply-evidence.txt
test "$DROWS" -eq 19 || { echo "STOP — unexpected D-row count"; exit 1; }
test "$MROWS" -eq 2  || { echo "STOP — unexpected M-row count"; exit 1; }

# .gitignore revert must only touch the one-line .claude/hooks/*.log append,
# NOT the §A.0 !-negation expansion in HEAD~3.
git diff --no-color HEAD -- .gitignore > /tmp/e1-apply-revert-gitignore-diff.txt
DIFF_CHANGES=$(grep -cE '^[+-][^+-]' /tmp/e1-apply-revert-gitignore-diff.txt)
echo "Revert .gitignore change-line count: $DIFF_CHANGES (expected 2: one '-' + one '+')" >> /tmp/e1-apply-evidence.txt

# RKL runtime files should still appear in --ignored listing (proves they
# survive revert because they were never in git history)
grep -E '^!! \.claude/hooks/(assertion-check|destructive-gate|scheduler)\.py' \
    /tmp/e1-apply-revert-status-with-ignored.txt \
    > /tmp/e1-apply-revert-ignored-proof.txt
RKL_LINES=$(wc -l < /tmp/e1-apply-revert-ignored-proof.txt)
echo "RKL ignored-line count: $RKL_LINES  (expected 3)" >> /tmp/e1-apply-evidence.txt
test "$RKL_LINES" -eq 3 || { echo "STOP — unexpected RKL ignored-line count"; exit 1; }

git revert --abort
git status --porcelain  # expected empty
```

**Why correct:** `git revert -m 1 <merge>` undoes the payload's diff vs first-parent mainline. First parent = `HEAD~2` (adopt-overwrite). Revert touches only: 19 A1 adds + settings.json merge + one-line `.claude/hooks/*.log` append. §A.0 expansion in `HEAD~3` is mainline ancestor and untouched. 6 AO files in `HEAD~2` untouched. Receipt at `HEAD` is above merge and untouched. 3 RKL runtime files never entered git history.

### D — Governance runtime validation (Phase ε)

```bash
# D.1 hook imports (7 expected OK)
for hook in intake-classifier scanner-safe-writer _delib_common turn-marker delib-preflight-gate owner-decision-capture gov09-capture; do
    python -c "import importlib.util; spec=importlib.util.spec_from_file_location('t', '.claude/hooks/${hook}.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK ${hook}')" || echo "FAIL ${hook}"
done

# D.2 skill files (6 expected OK)
for s in bridge-propose decision-capture spec-intake; do
    test -f ".claude/skills/${s}/SKILL.md" && echo "OK SKILL.md ${s}" || echo "FAIL SKILL.md ${s}"
    h=$(find ".claude/skills/${s}/helpers/" -name "*.py" -type f | head -1)
    test -f "$h" && python -c "import importlib.util; spec=importlib.util.spec_from_file_location('t','$h'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); print('OK helper ${s}')" || echo "FAIL helper ${s}"
done

# D.3 settings.json event counts
python -c "import json; d=json.loads(open('.claude/settings.json').read()); [print(f'{k}: {len(d.get(\"hooks\",{}).get(k,[]))}') for k in ('PreToolUse','UserPromptSubmit','PostToolUse','SessionStart')]"

# D.4 rule files (6 expected OK)
for r in prime-builder bridge-poller-canonical prime-bridge-collaboration-protocol report-depth canonical-terminology.md canonical-terminology.toml; do
    test -f ".claude/rules/${r}" && echo "OK rule ${r}" || echo "FAIL rule ${r}"
done
```

### E — Main-workspace non-mutation proof

```bash
cd "$AR_MAIN"
echo "--- Main workspace A2 SHAs after Apply ---" >> /tmp/e1-apply-evidence.txt
for rel in hooks/assertion-check.py hooks/credential-scan.py hooks/destructive-gate.py \
           hooks/scheduler.py hooks/spec-classifier.py rules/bridge-essential.md \
           rules/deliberation-protocol.md rules/file-bridge-protocol.md rules/loyal-opposition.md; do
    echo "MAIN-POST-APPLY  $(sha256sum ".claude/$rel" | cut -d' ' -f1)  .claude/$rel" >> /tmp/e1-apply-evidence.txt
done
echo "MAIN-POST-APPLY  $(sha256sum .gitignore | cut -d' ' -f1)  .gitignore" >> /tmp/e1-apply-evidence.txt
```

### F — Post-impl cleanup

Worktree + `e1-apply` branch remain until Codex VERIFIED.

```bash
cd "$AR_MAIN"
git worktree list > /tmp/e1-apply-worktree-list.txt
```

## Commit Plan

Four commits on `e1-apply` above the worktree's initial `develop` HEAD:

1. **§A.0 `.gitignore` policy commit** (Prime, manual) — ~26 new lines. Position `HEAD~3`.
2. **§A.2.1 adopt-overwrite commit** (Prime, manual) — 6 A2 files from GT-KB v0.6.1 templates. Position `HEAD~2`.
3. **Payload commit + merge commit** (auto, `gt project upgrade --apply`). Position `HEAD~1` is merge (two parents).
4. **Receipt commit** (auto, tracked-mode `write_receipt`). Position `HEAD`.

`e1-apply` is NOT merged to `develop` by this bridge.

## Post-Impl Report Contents

- **§Evidence:** worktree creation, `/tmp/e1-apply-evidence.txt` (§A.0.1 ignore-state proof for A1/AO/RKL/receipt + `resolve_receipt_mode` + §A.2 hashes), §A.3 dry-run, §B apply stdout, topology SHAs, §C revert status (with/without `--ignored`), `.gitignore` diff assertion, §E main-workspace non-mutation.
- **§Topology:** HEAD/HEAD~1/HEAD~2/HEAD~3 SHAs + merge-parents confirmation + receipt JSON contents + 5-line `git log`.
- **§Adoption Summary:**

  | Category | Count | Git-tracked on e1-apply | Notes |
  |----------|-------|-------------------------|-------|
  | A1 `add` (payload) | 19 | yes (HEAD~1) | All staged because §A.0 removed ignore coverage |
  | A1 `merge-event-hooks` (payload) | 3 | yes (HEAD~1) | On `.claude/settings.json` |
  | A1 `append-gitignore` (payload) | 1 | yes (HEAD~1) | Appends `.claude/hooks/*.log` |
  | A2 `adopt-overwrite` (pre-apply commit) | 6 | yes (HEAD~2) | All 6 tracked after §A.0 |
  | A2 `reject-keep-local` | 3 | **no** | Runtime-only on worktree disk; AR customizations preserved |
  | `.gitignore` policy expansion | 1 | yes (HEAD~3) | ~26 new lines |
  | Receipt commit | 1 | yes (HEAD) | Tracked-mode post-merge JSON |

- **§Rollback Proof:** 19 `D` + 2 `M`; excludes 9 A2 + receipt + §A.0 policy. `git status --ignored` shows 3 RKL `!!` rows.
- **§Main-Workspace Non-Mutation Proof:** SHA parity 9 A2 + `.gitignore`.
- **§Observed Limitations:** RKL runtime files re-materialized on worktree re-create; future `scaffold_version` bumps re-run forward-materialization until per-file-skip or upstream migration; future Tier A expansions need a new `.gitignore` bridge.

## Non-Scope for Apply

- No integration into `develop`.
- No hook runtime testing against live Claude Code.
- No metrics collection.
- No migration of AR customizations upstream.
- No `--skip-file` feature request.
- No B1 main-workspace cleanup (separate bridge `agent-red-cto-cleanup`).

## Verification Gates

- [ ] `git worktree list` shows `../agent-red-e1-apply` on `e1-apply`.
- [ ] §A.1 `git status --porcelain` empty at worktree creation.
- [ ] §A.0 commit touches exactly `.gitignore` (diff ≈26 insertions).
- [ ] §A.0.1 A1 FAIL=0 (all 19 NOT-IGNORED).
- [ ] §A.0.1 AO FAIL=0 (all 6 NOT-IGNORED).
- [ ] §A.0.1 RKL FAIL=0 (all 3 IGNORED — unchanged disposition).
- [ ] §A.0.1 Receipt probe NOT-IGNORED.
- [ ] §A.0.1 `resolve_receipt_mode()` returns `mode='tracked'`.
- [ ] §A.0.1 no `FAIL CHECK-IGNORE-ERROR` lines in evidence file.
- [ ] §A.2 evidence: 6 `MATCH-TEMPLATE` + 3 `MATCH-AR-MAIN`; zero `MISMATCH-*`.
- [ ] §A.2.1 pre-commit `git status --porcelain` shows 6 lines (2 `M` + 4 `??`); zero RKL paths appear.
- [ ] §A.2.1 commit touches exactly 6 files.
- [ ] §A.3 planner summary: `A2 mutating violations 0`; `counts` has `add=19, merge-event-hooks=3, append-gitignore=1`.
- [ ] §B apply stdout: `RECEIPT tracked @` (NOT `RECEIPT filesystem`).
- [ ] `git rev-list --parents -n 1 HEAD~1` returns 3 tokens.
- [ ] Payload commit `HEAD~1^2` tree lists exactly 21 paths (19 A1 + settings.json + .gitignore).
- [ ] Exactly one receipt at `.claude/upgrade-receipts/active/*.json`; `merge_commit` = HEAD~1 SHA; `mode = "tracked"`.
- [ ] §C revert-status: 19 `D` + 2 `M`; zero entries for the 9 A2 paths or the receipt.
- [ ] §C `.gitignore` revert diff: 1 `-` line + 1 `+` line (the `.claude/hooks/*.log` toggle only).
- [ ] §C revert-status-with-ignored: exactly 3 RKL `!!` rows.
- [ ] §C `git revert --abort` leaves empty `git status --porcelain`.
- [ ] D.1–D.4 all `OK`; zero `FAIL`.
- [ ] §E main-workspace SHAs byte-identical pre/post for 9 A2 paths + `.gitignore`.

## Zero GT-KB Writes

Unchanged. Apply reads GT-KB templates; writes zero GT-KB source.

## Requested Verdict

**GO on REVISED-4**, OR **NO-GO with specific findings** for REVISED-5. If owner prefers Option A1 or B persistence model, NO-GO with preference.

## Next Step After Codex GO

Execute §A.1 → §A.0 → §A.0.1 (HARD GATE) → §A.2 → §A.2.1 → §A.3 → §B → §C → §D → §E → §F; capture evidence; file post-impl report as the next version.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
