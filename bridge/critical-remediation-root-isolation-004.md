REVISED

# CRITICAL REMEDIATION — Root Isolation Mandate Compliance (REVISED-2)

**Status:** REVISED-2 (CRITICAL scoping; supersedes all other open work; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/critical-remediation-root-isolation-003.md` (REVISED-1)
**Reason for REVISED-2:** Owner correction of §3.2 framing in `-003`. The auto-memory location is NOT an architectural question — the owner's directive (and CLAUDE.md edit "*active GT-KB memory must resolve inside `E:\GT-KB`, not a home-directory mirror or legacy project path*") already established that migration is the work. Branch A / Branch B in `-003` was a category error.

---

## Prior Deliberations + §0 Scope (unchanged)

## Summary of revision (delta from `-003`)

| Section | Change |
|---|---|
| §3.2 | Reframed: migration of 104 files is the primary action; post-migration steady-state options for Claude Code's reading behavior are technical sub-questions (not an architectural choice). |
| §7 | Reframed: Phase 7a = MIGRATE all auto-memory content into `E:\GT-KB\memory\` per §2.5 manifest protocol. Phase 7b = verify source location is empty. Phase 7c = post-migration Claude Code reading-behavior handling. |
| §8 | NO blocking owner decision. Owner directive already binding; migration target already named. |

All other sections (`-003` §1-§2 inventory + §2.5 manifest protocol + §2.6 application-boundary audit + §3.1 editable-install invariant + §3.3-§3.5 exempt categories + §4-§6) **unchanged from `-003`**.

## §3.2 — Claude Code auto-memory location (REFRAMED)

**No "cache" framing. No Branch A vs Branch B as architectural choice.** Per owner directive: *"active GT-KB memory must resolve inside `E:\GT-KB`, not a home-directory mirror or legacy project path"*. The migration is the work; the post-migration Claude Code reading-behavior is a follow-on technical concern.

### §3.2.1 Migration target (already established)

`E:\GT-KB\memory\` exists and currently contains project data files (dashboard sqlite, hibernation runbook + state, pending-owner-decisions, etc.). The migration adds operational memory files to the same directory:

- `MEMORY.md` (canonical operational memory; currently at auto-memory location)
- ~50 `feedback_*.md` files
- ~50 `project_*.md` and topic files
- Total: 104 files per S315 inventory

Post-migration `E:\GT-KB\memory\` becomes the **single, in-root, git-tracked, canonical** source for all operational memory. The directory layout TBD at impl time; likely `E:\GT-KB\memory\feedback/`, `E:\GT-KB\memory\topics/` subdirs to keep navigation clean.

### §3.2.2 Migration is a §2.5 manifest action

The migration of 104 files is a destructive action (delete originals from auto-memory location after migration), so it follows the §2.5 5-step protocol verbatim:

1. **Inventory:** enumerate every file at `C:/Users/<user>/.claude/projects/E--GT-KB/memory/`; classify each as `MEMORY.md` | `feedback_*` | `project_*` | `topic_other` | `backup`.
2. **Migrate:** copy each file to its corresponding in-root path under `E:\GT-KB\memory\` (preserving subdirectory layout per §3.2.1).
3. **Verify by checksum:** SHA256 source vs destination for every migrated file.
4. **Confirm no remaining active GT-KB content at source:** `find C:/Users/<user>/.claude/projects/E--GT-KB/memory/ -type f` returns empty after migration (or only contains items explicitly excluded from migration).
5. **Record disposition + delete:** manifest entry per file + delete originals; commit manifest as part of phase commit.

### §3.2.3 Post-migration Claude Code reading-behavior

After migration, Claude Code's session-start auto-memory read encounters an empty directory. Three possible runtime behaviors (technical sub-question, not architectural):

- **(i) Claude Code tolerates empty auto-memory** — session starts; no auto-memory loaded; CLAUDE.md still loads from project root with its `> **📁 Session memory** (operational patterns, lessons): memory/MEMORY.md` reference (already updated by owner). MEMORY.md gets loaded explicitly via that reference. **Best case; no further action needed.**
- **(ii) Claude Code complains/errors on missing files** — would surface at session start; impl-time test will confirm. Mitigation: ensure CLAUDE.md's reference to `memory/MEMORY.md` works as the explicit pointer; investigate any `--no-auto-memory` flag if needed.
- **(iii) Claude Code re-creates files at the auto-memory location** — would surface at session end (next-session diff). Mitigation: SessionStop hook detects + deletes any files Claude Code wrote there; the writes are treated as **vendor-defect anomalies to neutralize**, not as accepted state.

Phase 7c handles whichever behavior surfaces. The migration (Phase 7a) is the binding action; post-migration cleanup (Phase 7c) handles vendor side effects.

### §3.2.4 Verification (Phase 7d)

After migration + post-migration handling:

- `find C:/Users/<user>/.claude/projects/E--GT-KB/memory/ -type f` returns empty (or only stale residue Claude Code re-created, which Phase 7c neutralizes).
- `ls E:/GT-KB/memory/` shows all 104 migrated files in their planned subdirectory layout.
- A fresh session start successfully loads `memory/MEMORY.md` via CLAUDE.md's explicit reference; operational memory continuity verified.
- No `Path.home()` reads of memory paths remain in any GT-KB-touching script.

## §7. Sequencing (REVISED)

Phase 7 split into 7a/7b/7c/7d:

```
Phase 7 (auto-memory remediation)
  ├─ Phase 7a: Migrate 104 files to E:\GT-KB\memory\ (per §2.5 manifest)
  │            Subdirectory layout: feedback/ + topics/ + root MEMORY.md
  ├─ Phase 7b: Verify source location empty post-migration
  ├─ Phase 7c: Handle Claude Code post-migration runtime behavior
  │            (whichever of §3.2.3 cases (i)/(ii)/(iii) applies)
  └─ Phase 7d: Re-verify in fresh session: source empty, in-root loads
```

All other phases unchanged from `-003` §2.7.

## §8. Decisions Needed From Owner (REVISED — NONE BLOCKING)

**No blocking owner decision.** The owner directive ("active GT-KB memory must resolve inside E:\GT-KB, not a home-directory mirror") + the named migration target (`E:\GT-KB\memory\`) are both binding inputs already in hand.

**Optional owner direction (does not block plan execution):**

- **Subdirectory layout under `E:\GT-KB\memory\`:** default proposed = `memory/feedback/`, `memory/topics/`, `memory/MEMORY.md` at root. Owner can override layout preference at any time.
- **Migration scheduling:** Phase 7 can run during this remediation execution OR as a separate subprogram. Default: Phase 7 in this remediation (binds to current owner directive momentum).

All other defaults from `-003` §5 unchanged (framework code at `E:\GT-KB\src\groundtruth_kb\`; archived migration scripts; in-root worktrees kept).

## Apology + acknowledgment

The `-003` "Branch A vs Branch B" framing was a category error. The owner had already directed migration via the CLAUDE.md edit `"active GT-KB memory must resolve inside E:\GT-KB, not a home-directory mirror or legacy project path"`. I treated an executed decision as an open question. Codex's `-002` F1 ("calling that path a cache does not remove the violation") was the right correction; my `-003` response addressed half of it (rejected "cache" framing) but left the false-choice framing intact. This REVISED-2 fixes both.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
