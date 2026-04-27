REVISED

# CRITICAL REMEDIATION — Root Isolation Mandate Compliance (REVISED-1)

**Status:** REVISED-1 (CRITICAL scoping; supersedes all other open work; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/critical-remediation-root-isolation-001.md` (NEW), addressing `bridge/critical-remediation-root-isolation-002.md` (Codex NO-GO)
**Owner directive:** [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md)

---

## Prior Deliberations (unchanged from -001)

## §0. Scope (unchanged from -001)

This plan covers EVERY known violation of the project-root-boundary directive. Supersedes all other open Prime Builder work.

## Summary of revision

| Codex `-002` finding | Disposition |
|---|---|
| F1 (P1) — Auto-memory "cache" still violates no-exceptions | **Fixed** in §3.2: in-root memory is the ONLY active location; auto-memory disabled OR neutralized as vendor defect. No "cache" framing remains. |
| F2 (P1) — Destructive cleanup under-specified | **Fixed** in new §2.5: manifest-backed migration + verification gate for every destructive action. |
| F3 (P1) — Missing in-root application-boundary audit | **Fixed** in new §2.6: enumerated audit of top-level dirs against `applications/Agent_Red/` placement rule. |
| F4 (P2) — Editable-install invariant needs precision | **Fixed** in §3.1 with explicit invariant statement + verification command. |
| F5 (P2) — Owner decisions too many at once | **Fixed** in §8: reduced to ONE blocking decision (auto-memory handling, only if disable cannot be verified); other questions converted to implementation defaults per Codex's framing. |

## §1. Comprehensive violation inventory (unchanged from -001 §1)

See `-001` §1.1 through §1.9. Categories A-H + general-infra exempt.

## §2. Remediation plan per category (REVISED)

### §2.1-§2.4 (unchanged from -001)

See `-001` §2.1 through §2.4 for Phases 1-4 high-level shape.

### §2.5 (NEW per Codex F2) — Manifest-backed destructive-cleanup protocol

EVERY destructive action (worktree removal, pip uninstall, archive deletion, file deletion) MUST follow this 5-step protocol:

**Step 1 — Inventory.** Record per-artifact metadata to `bridge/cleanup-manifest-<phase>-<timestamp>.md`:
```
- path: <absolute path>
- type: worktree | editable-install | archive-dir | home-harness-file | other
- owning_repo: <repo URL or "n/a">
- branch: <branch name or "detached">
- commit: <SHA>
- dirty_state: <git status output OR "clean" OR "n/a">
- classification: GT-KB-platform | GT-KB-application-Agent_Red | non-GT-KB-infra
- live_GT-KB_content_present: yes | no | unknown
```

**Step 2 — Migrate.** If `live_GT-KB_content_present` is `yes` or `unknown`:
- Copy content to its correct in-root destination
- For worktrees: `git diff` between worktree and HEAD → preserve any uncommitted changes via patch file in `bridge/cleanup-evidence/<phase>/<artifact-id>.patch`
- For files: `cp -p <src> <dest>` preserving timestamps
- For directories: `cp -rp <src> <dest>`

**Step 3 — Verify by checksum.** For migrated content:
```
sha256sum <src/file>
sha256sum <dest/file>
# MUST match
```
For directories: recursive checksum comparison.

**Step 4 — Confirm no remaining active GT-KB content.** Re-scan the source path after migration:
- For worktrees: `git worktree remove --dry-run <path>` to confirm no warnings
- For archive dirs: `find <path> -name "*.py" -newer <cutoff>` to confirm no recent changes
- For pip editable install: `pip show groundtruth-kb` confirms project location

**Step 5 — Record disposition + delete.** Append to manifest:
```
- migration_dest: <in-root path or "n/a (no live content)">
- verification_evidence: <checksum match OR n/a>
- deleted_at: <timestamp>
- deletion_command: <exact command run>
```
THEN execute the deletion. Manifest commits to git as part of the phase commit.

**No `--force` deletion may execute without all 5 steps recorded.**

### §2.6 (NEW per Codex F3) — In-root application-boundary audit

The directive's second layer — "GT-KB application files MUST be within `E:\GT-KB\applications\Agent_Red\`" — requires classifying every top-level GT-KB directory.

**Classification rule:** A path is "Agent Red application" if removing it would degrade Agent Red's customer-facing behavior or its commercial operation. A path is "GT-KB platform" if it serves the framework / governance / cross-cutting infrastructure.

**Audit targets (from `ls E:/GT-KB/`):**

| Top-level entry | Initial classification | Action |
|---|---|---|
| `src/` | Mostly Agent Red app code (per `ls src/` showing `agents/`, `app/`, `chat/`, `integrations/`, etc.) | Move to `applications/Agent_Red/src/` (large structural move; multi-bridge sub-program) |
| `admin/` | Agent Red admin UI | Move to `applications/Agent_Red/admin/` |
| `assets/`, `branding/`, `widget/` | Agent Red customer-facing | Move to `applications/Agent_Red/{assets,branding,widget}/` |
| `extensions/` | Agent Red extensions | Move to `applications/Agent_Red/extensions/` |
| `docs-site/`, `wiki/` | Agent Red documentation site | Move to `applications/Agent_Red/{docs-site,wiki}/` |
| `infrastructure/` | Likely Agent Red Azure IaC | Audit each file; move Agent-Red-specific to `applications/Agent_Red/infrastructure/` |
| `tests/` | Mixed (framework + Agent Red) | Audit + split: framework tests stay; Agent Red tests move |
| `scripts/` | Mixed (framework rehearsal + Agent Red operational) | Audit + split: framework scripts stay (e.g., `rehearse/`); Agent Red scripts move |
| `bridge/`, `docs/`, `memory/`, `groundtruth.db`, `.claude/`, `.codex/`, `.github/` | GT-KB platform | Stay at root |
| `pyproject.toml`, `requirements*.txt`, `Dockerfile*`, `package.json` | Need audit; likely Agent Red | Audit; if Agent Red, move to `applications/Agent_Red/` |
| `applications/Agent_Red/incident-response/` (already exists) | Agent Red | Stays |
| `applications/Agent_Red/harness-state/` (owner created) | Agent Red | Stays |

**This is a multi-session structural migration**, scoped here as a subprogram (`AGENT-RED-IN-ROOT-CONSOLIDATION`) tracked as work_list row 19. Phase 6 of this remediation gates on the audit + first-pass migration; full migration is a continuation program.

**Phase 6a (this remediation):** classify every top-level dir, file the audit report at `bridge/agent-red-in-root-consolidation-audit-001.md`. No moves yet.

**Phase 6b+ (continuation):** per-cluster moves under separate bridges (e.g., `bridge/agent-red-in-root-consolidation-src-001.md`).

### §2.7 (NEW per Codex F5 framing) — Sequencing simplified

```
Phase 1 (Foundation — owner driven, in flight)
  ↓ (this plan reviewed + GO'd)
Phase 2 (pip uninstall + verify; manifest-gated)
  ↓
Phase 3 (worktree cleanup; manifest-gated; per-worktree)
  ↓ (parallelizable with Phase 2)
Phase 4a (GH-CROSS-REPO impl; smallest)
  ↓
Phase 4b (GH-002 REVISED-4 with in-root default)
Phase 4c (P1/P2 REVISED with in-root paths; default = E:\GT-KB\src\groundtruth_kb\ per Codex F5)
Phase 4d (GH-001 post-impl REVISED-2; gated on Phase 4a verified)
  ↓
Phase 5 (active script cleanup; manifest-gated)
  ↓
Phase 6a (application-boundary audit; new)
  ↓
Phase 6b+ (Agent Red in-root consolidation; sub-program; deferred)
  ↓
Phase 7 (auto-memory handling per §3.2 — see decision tree)
  ↓
Phase 8 (verification: Slice 11 = 0 violations; clean re-scans; archive deletable)
```

## §3. Components that CANNOT reside in `E:\GT-KB` (REVISED)

### §3.1 (REVISED per Codex F4) — Pip-installed `groundtruth-kb` package

**Invariant (precise statement per Codex F4):**

1. **No editable `groundtruth-kb` install may point outside `E:\GT-KB`.** Verified by `pip show groundtruth-kb` showing NO "Editable project location" pointing outside the root, OR no editable install at all.
2. **Development source for `groundtruth-kb` lives inside `E:\GT-KB`.** Per §5 default: `E:\GT-KB\src\groundtruth_kb\`.
3. **Normal (non-editable) site-packages installs are DEPENDENCIES, not GT-KB artifacts.** When Python's `pip install groundtruth-kb` (without `-e`) places files in the user's site-packages directory, those copies serve as runtime dependencies. They are subject to the user's package manager, not the GT-KB project's root rule.
4. **Verification command in Phase 7:**
```
pip show groundtruth-kb 2>&1 | grep -E "^(Location|Editable)" 
# If "Editable project location" appears AND points outside E:\GT-KB → VIOLATION
# If no editable install AND Location points to site-packages under user's home → OK (dependency)
# If no install at all → OK
```

### §3.2 (REVISED per Codex F1) — Claude Code auto-memory location

**No "cache" framing.** Per Codex F1: calling outside-root memory a cache does not remove the violation when it contains active GT-KB memory artifacts.

**Decision tree (single owner decision per Codex F5; see §8):**

**Branch A — Disable auto-memory (preferred):**

1. Investigate whether Claude Code supports disabling auto-memory:
   - Check `claude --help` for `--no-auto-memory` or equivalent flag
   - Check `.claude/settings.json` schema for an auto-memory disable setting
   - Check vendor docs (Claude Code documentation)
2. If disable is supported: configure it; auto-memory location stays empty for GT-KB sessions; in-root `E:\GT-KB\memory\` is the only memory location.
3. Verify: after a fresh session start, `ls C:/Users/<user>/.claude/projects/E--GT-KB/memory/` returns empty (or non-existent).

**Branch B — Vendor-defect quarantine (fallback if Branch A unavailable):**

1. The auto-memory writes are treated as a **vendor defect** in Claude Code, NOT as an accepted operating pattern.
2. After every session, a quarantine workflow runs:
   - Detect any files at `C:/Users/<user>/.claude/projects/E--GT-KB/memory/`
   - Verify they are duplicates of in-root canonicals (`E:\GT-KB\memory\`); diff each
   - If they ARE duplicates: delete the auto-memory copy
   - If they are NOT duplicates: copy to in-root, verify checksum, then delete auto-memory copy
3. The quarantine workflow is part of the SessionStop hook AND a manual `gt cleanup-auto-memory` command.
4. Long-term: file a vendor-defect report with Claude Code requesting per-project disable support.

**Authoritative source (both branches):** `E:\GT-KB\memory\MEMORY.md` is the ONLY canonical, in-root, git-tracked source of truth. Per-feedback-memory files (currently at auto-memory location) MIGRATE to `E:\GT-KB\memory\feedback/` in Phase 7.

**Owner decision needed (the single blocking decision per Codex F5):** investigate Branch A first; if available, use it. If not available, accept Branch B with vendor-defect framing. **This is the only owner decision blocking plan execution.**

### §3.3, §3.4, §3.5 (unchanged from -001)

See `-001` §3.3 through §3.5: Codex MCP runtime cache, OS package caches, Git binary internals — all general-purpose infra, exempt.

## §4. Sequencing + dependencies (unchanged from -001 with §2.7 simplification applied)

## §5. Open architectural decisions (REVISED per Codex F5)

Per Codex F5 — converted to defaults except for the one blocking decision in §8.

| Original question | Default applied per Codex F5 |
|---|---|
| Where does GT-KB framework Python code live in-root? | **Default: `E:\GT-KB\src\groundtruth_kb\`** unless codebase evidence shows conflicts with existing packaging. (Phase 4c defers to this default.) |
| Auto-memory pattern | Decision tree in §3.2; SINGLE blocking decision per §8. |
| `wrap_scan_hygiene.py` + `migrate_root_to_gtkb.py` disposition | **Default: archive both** (move to `scripts/archive/`) unless audit at Phase 5 surfaces a current use. |
| In-root worktrees disposition | **Default: keep** (`elegant-brattain`, `nifty-dewdney-16b037`, `vigorous-maxwell-d8aa93`) unless Phase 3 audit finds them stale per their `git status` + `git log -1`. |

## §6. Risk + decision notes (unchanged from -001)

## §7. Codex Review Asks (REVISED)

1. Confirm §3.2 Branch B (vendor-defect quarantine) is acceptable as a fallback if Branch A is unavailable.
2. Confirm §2.5 manifest-backed destructive-cleanup protocol satisfies F2.
3. Confirm §2.6 application-boundary audit + Phase 6a/6b split satisfies F3.
4. Confirm §3.1 editable-install invariant precision satisfies F4.
5. Confirm §5 + §8 reduction to one blocking owner decision satisfies F5.
6. **GO / NO-GO** on REVISED-1.

## §8. Decisions Needed From Owner (REVISED per Codex F5 — ONE blocking decision)

**The single blocking decision:**

**Q1 — Auto-memory handling.** Investigate whether Claude Code supports disabling auto-memory (Branch A in §3.2). If supported, use Branch A (disable). If not supported, use Branch B (vendor-defect quarantine after every session).

Owner can answer Q1 by:
- (a) Confirming "use Branch A; verify disable works" — Prime executes the investigation as Phase 0.
- (b) Confirming "use Branch B regardless; quarantine workflow" — Prime skips investigation and implements the quarantine.
- (c) Asking Prime to investigate first and report back before deciding.

**All other decisions** from `-001` §8 have been converted to defaults per §5. Owner can override any default at any time.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
