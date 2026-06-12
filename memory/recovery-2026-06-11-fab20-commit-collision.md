---
name: recovery-2026-06-11-fab20-commit-collision
description: HOLD/recovery state. FAB-20 verified source uncommitted; my mislabeled commit 772a186b + git reset orphaned Codex commit 51c9bdeb. Awaiting owner quiesce of concurrent Codex session before recovery. Nothing lost.
metadata:
  type: project
author_identity: prime-builder
author_harness_id: B
author_session_context_id: ad3221a1-e3bc-4d3e-bcec-d3d608598322
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, explanatory
---

# Recovery state — 2026-06-11 FAB-20 commit/reset collision

**Status: RESOLVED 2026-06-11. No work lost; no Codex work orphaned.**

During the owner-directed quiesce, Codex self-corrected both of my errors:
it `--amend`ed the mislabeled `772a186b` into `d16906eb`
("feat: add backlog triage stage 1 detector", correct message) and
re-landed the stage-2 GO verdict as `be95922c` (restoring the content my
reset had orphaned in `51c9bdeb`). On resume I confirmed the current tip
was clean (no restore needed — resetting to `51c9bdeb` would have
re-orphaned `be95922c`/`d16906eb`), re-verified FAB-20 (28 passed; adapter
PASS), refreshed the inventory, and landed two scoped commits with
**explicit pathspec**:

- `b92f6475` fix: land verified FAB-20 hygiene skill correction (6 FAB-20
  files; gate PASS clean; `git show --stat` confirmed exact contents).
- `348bf47f` chore: refresh dev-environment inventory baseline (cleared the
  pre-existing `e90b2f03` `--no-verify` inventory-drift release-blocker).

The concurrency/index-thrash hazard that caused the incident is captured as
**WI-4464** (P1, git-workflow). The historical detail below is preserved as
the forensic record.

---

**Original HOLD record (superseded by the RESOLVED note above):**

## What happened (forensic, from reflog)

```
9be66825  docs(bridge): record bridge verdicts            base (clean)
772a186b  fix: land verified FAB-20 hygiene skill ...      MY mislabeled commit
51c9bdeb  chore(bridge): LO GO verdict for stage 2 ...      CODEX committed on top (concurrent)
772a186b  HEAD@{0} reset: moving to HEAD~1                  MY reset landed HERE
```

1. I committed `772a186b` with a "fix: FAB-20" message but the index had
   been mutated by a background hook, so it actually contains **Codex's**
   work: `bridge/INDEX.md`, `gtkb-backlog-triage-...-stage-1-structural-repair-005.md`,
   `-006.md`, `gtkb-backlog-triage-...-stage-2-router-corpus-disposition-003.md`,
   `scripts/hygiene/prefix_split_detector.py`, and
   `platform_tests/scripts/test_prefix_split_detector.py`. My FAB-20 files
   were NOT committed.
2. Codex concurrently committed `51c9bdeb` on top of `772a186b`.
3. My `git reset HEAD~1` (intending to undo `772a186b`) instead landed on
   `772a186b` because HEAD~1 of `51c9bdeb` is `772a186b` — **orphaning
   Codex's `51c9bdeb`** out of the branch.

Current HEAD = `772a186b` (mislabeled). `51c9bdeb` is reachable only via
reflog (recoverable ~30 days).

## Durable recovery anchors (nothing is lost)

- **Codex orphaned commit:** `51c9bdeb` (reflog `HEAD@{1}` at time of note).
  Verify it is still the Codex tip before restoring — Codex may have
  committed more since.
- **FAB-20 verified source — TWO copies:**
  - Working tree (modified, recovered + verified this session), AND
  - `stash@{2}` = `codex-temp-fab20-verdict-tracked-drift` (durable;
    survives a working-tree sweep). Extract with
    `git checkout "stash@{2}" -- <6 paths>`.
- **FAB-20 file set (6):** `.api-harness/skills/MANIFEST.json`,
  `.claude/skills/gtkb-hygiene-investigation/SKILL.md`,
  `.codex/skills/MANIFEST.json`,
  `.codex/skills/gtkb-hygiene-investigation/SKILL.md`,
  `config/agent-control/harness-capability-registry.toml`,
  `platform_tests/scripts/test_gtkb_hygiene_investigation.py`.
- **Inventory regen:** regenerable via
  `groundtruth-kb\.venv\Scripts\python.exe scripts\collect_dev_environment_inventory.py`.
  Needed to clear a PRE-EXISTING inventory-drift release-blocker: `e90b2f03`
  restored 6 governance hooks via `--no-verify` and never refreshed
  `.groundtruth/inventory/dev-environment-inventory.json`; material drift is
  the 6 hooks under `repo_configured_surfaces` (tool-version churn is
  normalized out per `config/governance/protected-artifact-inventory-drift.toml`).

## FAB-20 verification (reproduced this session, pre-collision)

`pytest test_gtkb_hygiene_investigation.py` -> 28 passed;
`generate_codex_skill_adapters.py --check` -> PASS (37 adapters);
ruff check/format clean; `hygiene_report.py --baseline --count-only` -> 3.
Bridge `gtkb-fab-20-hygiene-investigation-skill` is VERIFIED@-008 (verdict
already committed at `8929cbaf`).

## Recovery sequence (execute ONLY after owner confirms Codex quiesced)

1. `git reflog -15` + `git log --oneline -6`. Confirm current HEAD and find
   Codex's true latest commit (`51c9bdeb` or newer). If Codex committed more
   after my reset, the restore target is that newer tip, not `51c9bdeb`.
2. Restore Codex's tip: `git reset --mixed <codex-tip-sha>` (keeps
   working-tree FAB-20 + inventory; unstages all).
3. If the working-tree FAB-20 edits were swept during quiesce: re-extract
   `git checkout "stash@{2}" -- <6 paths>` and re-verify (pytest 28 passed;
   adapter --check PASS).
4. Re-run the inventory collector if its regen was swept.
5. Commit FAB-20 with **EXPLICIT pathspec** (NOT plain `git commit`):
   `git commit -- <6 paths> -m "fix: land verified FAB-20 ..."` via
   PowerShell.
6. Commit inventory: `git commit -- .groundtruth/inventory/dev-environment-inventory.json .groundtruth/inventory/dev-environment-inventory.md -m "chore: refresh dev-environment inventory baseline (WI-4449 restored-hooks follow-on)"`.
7. Verify each commit: gate PASS + `git show --stat` shows exactly the
   intended files (the lesson that bit me: confirm contents, not just exit
   code).
8. Flag `772a186b` mislabel: it carries my FAB-20 message but Codex's
   backlog-triage + prefix-split contents. Owner decision whether to rewrite
   (rebase — risky) or accept + document. Capture as a WI.

## Lessons (reusable)

- **ALWAYS commit with explicit `-- <pathspec>` in this repo.** The index is
  not stable across tool calls; background hooks auto-stage bridge-queue
  files. Plain `git commit` grabbed the wrong (hook-staged) files.
- **NEVER `git reset` on the shared branch while a concurrent session
  commits.** `HEAD~1` is not what you think if the other session committed on
  top — my reset orphaned Codex's `51c9bdeb`.
- **Re-read `git reflog`/`rev-parse HEAD` immediately before any history
  operation** when concurrency is possible.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
