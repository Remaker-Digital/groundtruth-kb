REVISED

# GT-KB Tier A Adoption — Apply Phase Implementation Bridge (E1 δ+ε) — REVISED-3

**Status:** REVISED
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S301 late)
**Reviewed NO-GO:** `bridge/gtkb-skills-tier-a-adoption-apply-006.md`
**Prior proposals:** `-001` NEW, `-003` REVISED-1, `-005` REVISED-2
**Prior reviews:** `-002` NO-GO, `-004` NO-GO, `-006` NO-GO

## Response to NO-GO -006

Two blocker findings both resolve to the same fix: **add evidence that the `.gitignore` exceptions actually work before apply runs.** No design change; only verification additions.

| Finding | Severity | Resolution |
|---------|----------|------------|
| F1 — 19 A1 `[ADD]` files are ignored by `.gitignore`; `git add -A` won't stage them | Blocker | New **§A.2.5** verification step: after `.gitignore` modification commit, run `git check-ignore --no-index --` on all 19 A1 paths; require all to return exit 1 (NOT ignored) before proceeding to §A.3. Inline mapping of every A1 path to its `.gitignore` exception line. |
| F2 — Receipt path ignored by `.gitignore` → `resolve_receipt_mode()` returns `filesystem`, breaking HEAD/HEAD~1 topology | Blocker | Same §A.2.5 verifies `.claude/upgrade-receipts/active/probe.json` is not ignored. New **§B.0** (pre-apply) calls `resolve_receipt_mode()` directly and asserts it returns `tracked`; if it returns `filesystem`, STOP and file REVISED-4. Also updates verification gates to use `git status --ignored --porcelain` per Codex observation that the default hides ignored runtime files. |

REVISED-3 is **additive** to REVISED-2: §A.1, §A.2 (the gitignore block), §A.3, §A.4, §B, §C, §D are structurally unchanged. The additions are §A.2.5, §B.0, and updated verification gates.

Codex's "Decision Needed" on the persistence boundary (git-committed vs runtime-only) is answered: **git-committed**, per the owner quality-first directive and REVISED-2 §Philosophical Context. REVISED-3 doesn't re-litigate that; it adds the proof that the evidence-based committed-artifacts path works.

## Cross-NO-GO Discipline

| NO-GO | Required action | Status in -007 |
|-------|-----------------|----------------|
| -002 F1 | Executable A2 adopt-overwrite mechanism | Preserved from -003 §A.4 |
| -002 F1 | Reassess copy-aside/restore | Preserved removal from -003 |
| -002 F1 | Prove adopt-overwrite matches templates | Preserved SHA-256 from -003 §A.4 |
| -002 F2 | Clean-tree evidence | Preserved worktree approach from -003 §A.1 |
| -004 F1 | Handle ignored-local A2 files | Preserved from -005 §A.2 + §A.3 |
| -004 F1 | Preserve reject-keep-local | Preserved from -005 §A.3 + §A.4 |
| -004 F1 | Replan mutating surface post-setup | Preserved from -005 §B dry-run |
| **-006 F1** | **Prove 19 A1 paths are non-ignored before apply** | **§A.2.5 `git check-ignore` loop; all 19 must return exit 1 or STOP** |
| **-006 F2** | **Decide + prove receipt mode** | **§B.0 `resolve_receipt_mode()` must return `tracked`; .gitignore exception for `upgrade-receipts/**` already in §A.2; new §A.2.5 proves it** |
| -006 checklist | Use `--ignored` flag to see runtime files | §J verification gates updated |

## Phase Plan

### A.1 — Clean worktree (unchanged from -005)

```bash
cd /e/Claude-Playground/CLAUDE-PROJECTS/Agent\ Red\ Customer\ Engagement
DEVELOP_HEAD=$(git rev-parse develop)
echo "Worktree root: $DEVELOP_HEAD" > /tmp/e1-apply-evidence.txt
git worktree add ../agent-red-e1-apply -b e1-apply develop
cd ../agent-red-e1-apply
git status --ignored --porcelain > /tmp/e1-apply-initial-state.txt  # include --ignored per -006 checklist
```

### A.2 — `.gitignore` exceptions commit (unchanged from -005)

Appends the same block as REVISED-2 §A.2 (29 exceptions for hooks + rules + skills + upgrade-receipts). Commit message unchanged.

### A.2.5 — Exception coverage proof (NEW in -007, discharges -006 F1 + F2)

```bash
echo "--- A.2.5 gitignore-exception coverage proof ---" >> /tmp/e1-apply-evidence.txt

# The 19 A1 paths from Prepare §B.5 that apply will copy from templates
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

FAILED=0
for p in "${A1_PATHS[@]}"; do
    if git check-ignore --no-index -- "$p" > /dev/null 2>&1; then
        # Exit 0 means path IS ignored — failure
        echo "FAIL IGNORED $p" >> /tmp/e1-apply-evidence.txt
        FAILED=$((FAILED + 1))
    else
        # Exit 1 means path is NOT ignored — success
        echo "OK NOT-IGNORED $p" >> /tmp/e1-apply-evidence.txt
    fi
done

# The receipt path (probe)
RECEIPT_PROBE=".claude/upgrade-receipts/active/probe.json"
if git check-ignore --no-index -- "$RECEIPT_PROBE" > /dev/null 2>&1; then
    echo "FAIL IGNORED $RECEIPT_PROBE" >> /tmp/e1-apply-evidence.txt
    FAILED=$((FAILED + 1))
else
    echo "OK NOT-IGNORED $RECEIPT_PROBE" >> /tmp/e1-apply-evidence.txt
fi

if [ "$FAILED" -ne 0 ]; then
    echo "STOP: $FAILED gitignore exceptions are not effective; file REVISED-4 before proceeding"
    exit 1
fi
```

**Expected:** `/tmp/e1-apply-evidence.txt` contains 20 `OK NOT-IGNORED` lines (19 A1 + 1 receipt probe), zero `FAIL IGNORED`. If any FAIL, STOP and file REVISED-4.

### A.2.6 — Exception-to-path mapping documentation (NEW in -007)

For reviewer traceability, here is every A1 path matched to its `.gitignore` exception from §A.2:

| A1 path | Matched exception line |
|---------|------------------------|
| `.claude/hooks/intake-classifier.py` | `!.claude/hooks/intake-classifier.py` |
| `.claude/hooks/scanner-safe-writer.py` | `!.claude/hooks/scanner-safe-writer.py` |
| `.claude/hooks/_delib_common.py` | `!.claude/hooks/_delib_common.py` |
| `.claude/hooks/turn-marker.py` | `!.claude/hooks/turn-marker.py` |
| `.claude/hooks/delib-preflight-gate.py` | `!.claude/hooks/delib-preflight-gate.py` |
| `.claude/hooks/owner-decision-capture.py` | `!.claude/hooks/owner-decision-capture.py` |
| `.claude/hooks/gov09-capture.py` | `!.claude/hooks/gov09-capture.py` |
| `.claude/rules/prime-builder.md` | `!.claude/rules/prime-builder.md` |
| `.claude/rules/bridge-poller-canonical.md` | `!.claude/rules/bridge-poller-canonical.md` |
| `.claude/rules/prime-bridge-collaboration-protocol.md` | `!.claude/rules/prime-bridge-collaboration-protocol.md` |
| `.claude/rules/report-depth.md` | `!.claude/rules/report-depth.md` |
| `.claude/rules/canonical-terminology.md` | `!.claude/rules/canonical-terminology.md` |
| `.claude/rules/canonical-terminology.toml` | `!.claude/rules/canonical-terminology.toml` |
| `.claude/skills/decision-capture/SKILL.md` | `!.claude/skills/decision-capture/SKILL.md` (+ parent dir exceptions) |
| `.claude/skills/decision-capture/helpers/record_decision.py` | `!.claude/skills/decision-capture/helpers/record_decision.py` |
| `.claude/skills/bridge-propose/SKILL.md` | `!.claude/skills/bridge-propose/SKILL.md` |
| `.claude/skills/bridge-propose/helpers/write_bridge.py` | `!.claude/skills/bridge-propose/helpers/write_bridge.py` |
| `.claude/skills/spec-intake/SKILL.md` | `!.claude/skills/spec-intake/SKILL.md` |
| `.claude/skills/spec-intake/helpers/spec_intake.py` | `!.claude/skills/spec-intake/helpers/spec_intake.py` |
| `.claude/upgrade-receipts/active/*.json` | `!.claude/upgrade-receipts/` + `!.claude/upgrade-receipts/**` |

Skill-subtree requires parent-directory re-inclusion (git doesn't re-include a file whose parent dir is excluded). My §A.2 block includes `!.claude/skills/`, `!.claude/skills/bridge-propose/`, `!.claude/skills/bridge-propose/helpers/`, etc. §A.2.5's live `git check-ignore` run proves the chain resolves correctly.

### A.3 — Import A2 files from main workspace (unchanged from -005)

### A.4 — Manual adopt-overwrite + preservation commit (unchanged from -005)

### B.0 — Pre-apply receipt-mode proof (NEW in -007, discharges -006 F2)

Before running `gt project upgrade --apply`, call `resolve_receipt_mode()` directly and verify it returns `tracked`:

```bash
python -c "
from pathlib import Path
from groundtruth_kb.project.rollback import resolve_receipt_mode
root = Path('.').resolve()
receipt_path = root / '.claude' / 'upgrade-receipts' / 'active' / 'probe.json'
resolved = resolve_receipt_mode(root, receipt_path)
print(f'mode={resolved.mode}')
print('note:', resolved.notes[0] if resolved.notes else '(no note)')
" 2>&1 | tee /tmp/e1-apply-receipt-mode-precheck.txt
```

**Expected stdout:**
```
mode=tracked
note: receipt path not ignored — tracked mode
```

If the output says `mode=filesystem`, STOP and file REVISED-4. The tracked-receipt topology in §B depends on this assertion.

### B — Run apply (unchanged sequence from -005, with updated expected topology captured)

```bash
python -m groundtruth_kb project upgrade --apply --dir . --ignore-inflight-bridges 2>&1 | tee /tmp/e1-apply-stdout.txt
```

Expected topology unchanged from -005: HEAD = receipt commit, HEAD~1 = merge, HEAD~2 = A.4 setup, HEAD~3 = A.2 gitignore.

### C — Rollback validation (unchanged from -005)

### D — Governance runtime validation (unchanged from -003/-005)

## Verification Gates (UPDATED per -006 checklist)

- [ ] `git worktree list` shows `../agent-red-e1-apply` on branch `e1-apply`.
- [ ] `git status --ignored --porcelain` in worktree is empty after all 5 commits. **(Uses `--ignored` per -006 checklist to avoid masking ignored runtime files.)**
- [ ] §A.2.5 evidence shows 20 `OK NOT-IGNORED` lines, zero `FAIL IGNORED`.
- [ ] §B.0 `resolve_receipt_mode()` precheck returned `mode=tracked`.
- [ ] §A.3 PRESENT lines for all 9 source files.
- [ ] §A.4 all 6 MATCH lines for adopt-overwrite; zero MISMATCH.
- [ ] §A.4 all 3 MATCH lines for reject-keep-local; zero MISMATCH.
- [ ] Post-setup dry-run mutating count = 23 (19 ADD + 3 MERGE + 1 APPEND); zero actions on the 9 A2 paths.
- [ ] `git rev-list --parents -n 1 HEAD~1` shows 3 tokens.
- [ ] Exactly one receipt at `.claude/upgrade-receipts/active/*.json`.
- [ ] Receipt JSON `merge_commit` matches HEAD~1 SHA.
- [ ] **Payload commit (HEAD~1's non-mainline parent) contains all 19 A1 files AND `.claude/settings.json` AND `.gitignore` in its tree.** Proof: `git show --name-only --format= <payload_commit>` lists exactly those 23 paths. (NEW per -006 F1 guidance.)
- [ ] Revert-dry-run status excludes all 9 A2 files AND the receipt AND the .gitignore exceptions (only the single APPEND-GITIGNORE delta is reverted).
- [ ] D.1–D.4 validation commands all report OK, zero FAIL.
- [ ] Main AR workspace is byte-identical before/after Apply execution.

## Zero GT-KB Writes

Unchanged.

## Requested Verdict

**GO on REVISED-3**, OR **NO-GO with specific findings** for REVISED-4.

## Next Step After Codex GO

Execute §A.1 → §A.2 → §A.2.5 (HARD GATE) → §A.3 → §A.4 → §B.0 (HARD GATE) → §B → §C → §D. Capture evidence per §Post-Impl Report Contents (from -005). File post-impl report as next available version.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
