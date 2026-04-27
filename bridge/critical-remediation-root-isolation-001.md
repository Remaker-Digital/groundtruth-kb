NEW

# CRITICAL REMEDIATION — Root Isolation Mandate Compliance

**Status:** NEW (CRITICAL scoping; supersedes all other open work; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Owner directive:** [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md) — All active GT-KB files MUST be within `E:\GT-KB`. All GT-KB application files MUST be within `E:\GT-KB\applications\`. **No exceptions.**
**Trigger:** S315 owner directives (2026-04-27): "All active files for the GT-KB project MUST be within the E:\GT-KB directory" + "E:\Claude-Playground is now an archive, not a live directory. It will be deleted as soon as all live GT-KB and Agent Red artifacts have been re-located to their correct homes."

---

## Prior Deliberations

- `.claude/rules/project-root-boundary.md` (owner-authored S315) — the binding directive.
- `bridge/generator-hardening-cross-repo-003.md` (Codex NO-GO) — first cascade of the directive into bridge protocol.
- `bridge/generator-hardening-002-008.md` (Codex NO-GO) — second cascade; Codex now enforcing across all GT-KB-touching proposals.
- `bridge/generator-hardening-cross-repo-005.md` (Codex GO) — degrade-only revision approved as the first compliant pattern.
- All 5 in-flight bridge-poller threads (P1, P2, P2.5, umbrella, GH-002 §B) require revision under the new directive.

## §0. Scope

This plan covers EVERY known violation of the project-root-boundary directive
discovered by the S315 scan, plus the architectural changes needed to honor
the directive going forward. **It supersedes all other open Prime Builder
work.** Pending bridges remain valid as scope (they describe correct
intent) but their implementation paths must be revised under this plan.

## §1. Comprehensive violation inventory

### §1.1 Pip editable install (Category A — HIGHEST IMPACT)

| Path | Disposition |
|---|---|
| `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\` (entire framework codebase) | **DELETE** post-migration per owner. Framework code must originate inside `E:\GT-KB`. |
| `pip show groundtruth-kb` → "Editable project location: E:\Claude-Playground\..." | **UNINSTALL** the editable install. Re-install (if needed) from in-root source. |

### §1.2 Git worktrees outside E:\GT-KB (Category B)

`git worktree list` reports the following outside-root worktrees:

| Worktree path | Branch | Disposition |
|---|---|---|
| `C:/Users/micha/.codex/worktrees/0f27/Agent Red Customer Engagement` | (detached `9ad23cbc`) | **REMOVE** via `git worktree remove --force` |
| `C:/Users/micha/.codex/worktrees/1822/...` through `ffea/...` (12 more Codex worktrees) | (detached HEAD on `9ad23cbc` mostly; one on `b1990241`) | **REMOVE** all |
| `C:/Users/micha/.codex/worktrees/claude-design-backlog` | `codex/claude-design-backlog` | **REMOVE** if not in active use; relocate inside `E:\GT-KB\.claude\worktrees\` if still needed |
| `C:/Users/micha/.cursor/worktrees/...` (4 Cursor worktrees) | (detached `06dcf486`) | **REMOVE** all |
| `C:/Users/micha/AppData/Local/Temp/gh-dep2` | `gh-pages` | **REMOVE**; gh-pages publishing is outside-root by design (publication target, not source) |
| `E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply` | `e1-apply` | **REMOVE** (archive directory) |
| `E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-gtkb-current-main-integration` | `codex/gtkb-current-main-integration` | **REMOVE** (archive directory) |

In-root worktrees at `E:\GT-KB\.claude\worktrees\` (`elegant-brattain`, `nifty-dewdney-16b037`, `vigorous-maxwell-d8aa93`) — KEEP if active; otherwise audit + remove.

### §1.3 Harness-local agent-red-hooks state (Category C)

| Path | Files | Status |
|---|---|---|
| `~/.codex/agent-red-hooks/` | `operating-role.md`, `session-lifecycle-guard.json`, `formal-artifact-approval.cmd`, log files (`last-session-start.err`, etc.) | **Owner migration in flight** — new `.codex/agent-red-hooks/` directory at project root visible in current `git status` |
| `~/.claude/agent-red-hooks/` | `session-lifecycle-guard.json` (and presumably more) | **Owner migration in flight** — new `applications/Agent_Red/harness-state/` directory visible in current `git status` |

**Plan (under owner direction):** complete the migration; update all consumers (scripts/tests) to read from in-root paths; delete home-dir originals.

### §1.4 Active Python `Path.home()` reads of GT-KB state (Category D — 8 sites across 7 files)

```text
scripts/check_codex_hook_parity.py:22                ← Path.home() / ".codex" / "agent-red-hooks"
scripts/extract_owner_messages.py:26                 ← Path.home() / ".claude" / "projects" (auto-memory)
scripts/session_self_initialization.py:94,107-108,111-112,1037-1038,1059  ← 8 Type F sites (GH-002 §B)
scripts/workstream_focus.py:52,55,56,59,60           ← operating-role + lifecycle-guard reads
scripts/wrap_scan_consistency.py:213                 ← Path.home() / ".claude" / "projects" (auto-memory)
tests/scripts/test_codex_hook_parity.py:124,160,186  ← mirrors check_codex_hook_parity.py
tests/scripts/test_memory_md_ceiling.py:57           ← auto-memory MEMORY.md path
```

**Status:** 3 of 7 files (`check_codex_hook_parity.py`, `workstream_focus.py`, `test_codex_hook_parity.py`) currently `M` in `git status` — owner refactoring in flight.

**Plan:** Complete the refactor across remaining 4 files. Each `Path.home()` call must be replaced by a path that resolves under `E:\GT-KB` (typically `applications/Agent_Red/harness-state/...` for adopter-specific state, or framework-equivalent in-root location for framework state).

### §1.5 Active scripts referencing `E:\Claude-Playground\` paths (Category E)

```text
scripts/migrate_root_to_gtkb.py    ← migration tooling (likely complete; review for archival)
scripts/wrap_scan_hygiene.py        ← active scan helper with hardcoded old paths
```

(Plus 13 archived files in `scripts/archive/` — already correctly archived.)

**Plan:** Audit each. `migrate_root_to_gtkb.py` likely served its purpose during the original migration → archive. `wrap_scan_hygiene.py` needs in-root path replacements OR archival if its function is now obsolete.

### §1.6 Auto-memory location (Category F — STRUCTURALLY CONSTRAINED)

| Path | Files | Constraint |
|---|---|---|
| `C:\Users\micha\.claude\projects\E--GT-KB\memory\` | `MEMORY.md`, ~50 `feedback_*.md`, ~50 `project_*.md` and topic files (~104 total) | **Structurally enforced by Claude Code harness software** — the path `~/.claude/projects/<encoded-project-path>/memory/` is hardcoded in Claude Code's auto-memory implementation, not configurable per-project. |

**Per `.claude/rules/project-root-boundary.md` "Apply ... to all GT-KB work":** this directive is binding. So the auto-memory location is a violation requiring resolution. **See §3 for handling.**

### §1.7 Project-root state directory `~/.gtkb-state/bridge-poller/` (NOT YET CREATED)

If P1/P2/P2.5 implementations had proceeded as originally scoped, they would have created `~/.gtkb-state/bridge-poller/` for harness registration + checkpoint state. **This was caught before any files were written.** Under this plan, the bridge-poller state moves to `E:\GT-KB\.gtkb-state\bridge-poller\` or equivalent in-root location.

### §1.8 Files I created during S315 in violation (Category H — ALREADY CORRECTED)

| Path | Status |
|---|---|
| `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\bridge\registry.py` | **DELETED** (S315 commit `01200db7` recorded the deletion narrative) |
| `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\tests\test_bridge_registry.py` | **DELETED** |
| `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\samples/{claude,codex}/` empty dirs | **DELETED** |

### §1.9 General-purpose harness infrastructure (NOT GT-KB artifacts per rule scope)

```text
~/.codex/skills/                  ← user-installed Codex skills (general)
~/.codex/plugins/cache/           ← Codex plugin cache (general)
C:/Python314/...                  ← Python interpreter
~/.local/bin/claude               ← Claude Code CLI binary
```

**No action.** These are general-purpose infrastructure, not GT-KB artifacts.

## §2. Remediation plan per category

### Phase 1 — Foundation (this session OR next, depending on owner pacing)

**Owner-driven (in flight):**
- ✅ `.claude/rules/project-root-boundary.md` rule file (DONE — owner created)
- ✅ `CLAUDE.md` "Mandatory Project Root Boundary" section (DONE — owner added)
- 🔄 In-root harness state directories `.codex/agent-red-hooks/` and `applications/Agent_Red/harness-state/` (DONE — owner created; population in progress)
- 🔄 Refactor of 3 scripts (`check_codex_hook_parity.py`, `workstream_focus.py`, `test_codex_hook_parity.py`) to use in-root paths (IN PROGRESS — visible as `M` in git status)

**Prime-driven (gated on owner finishing Phase 1 above):**
- File this remediation plan (THIS BRIDGE — under Codex review)
- Once owner migration of harness state complete: refactor remaining 4 files (`extract_owner_messages.py`, `session_self_initialization.py` Type F sites, `wrap_scan_consistency.py`, `test_memory_md_ceiling.py`)

### Phase 2 — Pip editable install removal

1. `pip uninstall groundtruth-kb -y` (removes the outside-root editable install reference).
2. If GT-KB framework code is still needed for runtime imports inside this workspace: establish in-root framework package OR re-install groundtruth-kb from PyPI (an installed package, not editable, lives at site-packages — see §3 for why this is acceptable).
3. Audit imports of `groundtruth_kb` across the codebase to confirm no broken references after uninstall.

### Phase 3 — Worktree cleanup

```bash
# Stale Codex worktrees (13 of them):
git worktree remove --force "C:/Users/micha/.codex/worktrees/0f27/Agent Red Customer Engagement"
# ... repeat for all 13 ...

# Stale Cursor worktrees (4):
git worktree remove --force "C:/Users/micha/.cursor/worktrees/Agent_Red_Customer_Engagement/ako"
# ... etc ...

# gh-pages temp:
git worktree remove --force "C:/Users/micha/AppData/Local/Temp/gh-dep2"

# Archive worktrees in E:\Claude-Playground:
git worktree remove --force "E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply"
git worktree remove --force "E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-gtkb-current-main-integration"

# Audit in-root worktrees at E:/GT-KB/.claude/worktrees/ (3) — keep if active
```

### Phase 4 — In-flight bridge revisions

Each open bridge that scoped outside-root paths must be revised:

| Bridge | Revision needed |
|---|---|
| `generator-hardening-001` post-impl | After GH-CROSS-REPO `-005` GO is implemented + Slice 11 reaches 0 violations: file post-impl REVISED-2 at `-009` citing the implemented follow-on. |
| `generator-hardening-002` REVISED-3 NO-GO at `-008` | File REVISED-4 with `--harness-config-root` default = in-root path (e.g., `E:\GT-KB\applications\Agent_Red\harness-state\` for adopter-specific or framework-equivalent for framework). |
| `generator-hardening-cross-repo` REVISED-1 GO at `-005` | **Implementation unblocked** — single-line `_git_checkout_info` change + 1 test + Slice 11 verify. |
| `gtkb-bridge-poller-p1-detector` REVISED-1 GO at `-004` | File REVISED-2 with in-root path (was `src/groundtruth_kb/bridge/detector.py`; new path TBD per §5 architectural decision). |
| `gtkb-bridge-poller-p2-registry` REVISED-2 GO at `-006` | File REVISED-3 with in-root path (same structural concern as P1). |
| `gtkb-bridge-poller-p2-5-verification-spike` REVISED-1 GO at `-004` | Already in-root (`scripts/bridge_poller_verification_spike.py`); no path revision needed. |

### Phase 5 — Active script cleanup

- Audit `scripts/migrate_root_to_gtkb.py` — likely complete; archive after confirmation.
- Audit `scripts/wrap_scan_hygiene.py` — replace hardcoded Claude-Playground references with in-root equivalents OR archive if obsolete.

### Phase 6 — Auto-memory handling (see §3 for detail)

Establish authoritative in-root MEMORY.md + memos at `E:\GT-KB\memory\`. Configure session-start sync from in-root → auto-memory; session-end sync from auto-memory → in-root (if changes). See §3.

### Phase 7 — Verification

- Slice 11 audit-hook lane: 0 violations on full run.
- Re-scan with `find` / `grep` for any remaining `Path.home()` reads of GT-KB state.
- Re-scan with `git worktree list` for any outside-root worktrees.
- Re-scan with `pip show groundtruth-kb` for editable install pointing outside.
- Audit log entry confirming archive directory `E:\Claude-Playground` can be deleted.

## §3. Components that CANNOT reside in `E:\GT-KB` (with handling explanation)

Per the directive's "no exceptions" wording, every GT-KB artifact must live in `E:\GT-KB`. The following components are STRUCTURALLY constrained to outside-root paths by external systems (Python pip, Claude Code harness) and require explicit handling.

### §3.1 The pip-installed `groundtruth-kb` package in adopter site-packages

**Constraint:** When adopters install GT-KB via `pip install groundtruth-kb`, pip places the package files in the adopter's Python `site-packages` directory (typically `~/.local/lib/python3.X/site-packages/groundtruth_kb/` on POSIX or `%APPDATA%\Python\Python3X\site-packages\groundtruth_kb\` on Windows). **This is outside any project root by Python's design.**

**Handling:**

- **GT-KB development workspace (E:\GT-KB):** all SOURCE for `groundtruth-kb` lives in `E:\GT-KB\`. The pip editable install at the outside-root archive path is removed (Phase 2). If during development an installed groundtruth-kb is needed (e.g., to test that scripts can import it), it should be re-installed from PyPI as a NORMAL (non-editable) install. The site-packages copy is then a DEPENDENCY, not a GT-KB SOURCE artifact. Per `.claude/rules/project-root-boundary.md` "does NOT apply to ... non-GT-KB user-installed tools" — **the pip-installed copy in site-packages is treated as a dependency, not a live GT-KB artifact**.

- **Adopter projects (e.g., a hypothetical Customer X consuming GT-KB):** their `site-packages/groundtruth_kb/` is a third-party dependency, not a Customer X artifact. Customer X's project-root-boundary equivalent only governs Customer X's OWN files, not their installed dependencies. So the pip-install pattern works without violating any analogous adopter-side rule.

- **Build/publication artifacts:** when GT-KB publishes a new release, `python -m build` produces wheel + sdist files. The build output by default is `E:\GT-KB\dist/` (in-root). PyPI publication then copies them to PyPI's CDN (outside any local root). **The local build output stays in-root; the published artifact is a publication target, not a live local GT-KB artifact.**

### §3.2 Claude Code's auto-memory location

**Constraint:** Claude Code's auto-memory feature reads/writes at `~/.claude/projects/<encoded-project-path>/memory/MEMORY.md`. The path is hardcoded in Claude Code's session-start hook implementation; it is not configurable per-project via `.claude/settings.json`. **This is a vendor-software constraint, not a project decision.**

**Handling (recommended pattern, requires owner approval):**

1. **Authoritative source:** `E:\GT-KB\memory\MEMORY.md` is the canonical, in-root, git-tracked source of truth.
2. **Auto-memory is a cache:** the path at `~/.claude/projects/E--GT-KB/memory/MEMORY.md` is treated as a Claude Code-controlled cache of the canonical, NOT as the canonical itself.
3. **SessionStart sync (in-root → cache):** before Claude Code reads the cache at session start, a hook copies `E:\GT-KB\memory\MEMORY.md` → `~/.claude/projects/E--GT-KB/memory/MEMORY.md`. The harness then reads the freshly-synced cache. This sync hook becomes part of the SessionStart pipeline.
4. **Session-end sync (cache → in-root, if dirty):** if Claude Code modifies MEMORY.md during the session, a Stop hook copies the cache back to in-root + commits. (Currently MEMORY.md is rarely modified mid-session; the trim S309 was the largest known modification, and it was driven by Prime, not by the harness.)
5. **Per-feedback-memory files** (`feedback_*.md`, ~50 files): same pattern. Authoritative in-root at `E:\GT-KB\memory\feedback/` (or similar); cache at auto-memory location.

**Alternative handling if owner prefers strict reading:**

- **Stop using auto-memory entirely.** Configure Claude Code to NOT read auto-memory at session start. Project knowledge lives only at `E:\GT-KB\memory\`. Each session's CLAUDE.md explicitly references `memory/MEMORY.md` for the bootstrap; no auto-memory feature involved. **This requires verifying Claude Code supports disabling auto-memory** (it likely does via the `--no-auto-memory` flag or equivalent).

**Owner decision needed:** Sync-from-canonical pattern (§3.2 #1-5) OR disable auto-memory entirely (alternative). The sync pattern is less disruptive; the disable pattern is stricter.

### §3.3 Codex MCP server runtime cache

**Constraint:** When Codex spawns an MCP server (e.g., Notion, Slack), the server process state may live at `~/.codex/mcp/...` or similar. This is Codex CLI infrastructure, not a GT-KB artifact.

**Handling:** No action — per rule scope, "general-purpose harness infrastructure" is exempt. Codex MCP cache is not a GT-KB artifact.

### §3.4 OS package manager artifacts (pip wheel cache, npm cache, etc.)

**Constraint:** pip caches downloaded wheels at `~/.cache/pip/` (POSIX) or `%LOCALAPPDATA%\pip\Cache\` (Windows). Same for npm.

**Handling:** No action — these are dependency caches, not GT-KB artifacts.

### §3.5 Git binary internals

**Constraint:** Git stores per-user config at `~/.gitconfig` etc.

**Handling:** No action — general-purpose infrastructure.

## §4. Sequencing + dependencies

```
Phase 1 (Foundation)
  ├─ Owner migration of harness state (IN FLIGHT)
  └─ This remediation plan filed (THIS BRIDGE)
       ↓
Codex review of this plan
       ↓
[GO]
       ↓
Phase 2 (pip uninstall) — independent, can run in parallel with Phase 3
Phase 3 (worktree cleanup) — independent
Phase 4 (bridge revisions)
  ├─ Phase 4a: GH-CROSS-REPO impl (degrade-only; smallest, ships fastest)
  ├─ Phase 4b: GH-002 REVISED-4 with in-root harness-config default
  ├─ Phase 4c: P1/P2 REVISED with in-root paths (gated on §5 architectural decision)
  └─ Phase 4d: GH-001 post-impl REVISED-2 (gated on Phase 4a verified)
       ↓
Phase 5 (active script cleanup)
       ↓
Phase 6 (auto-memory handling per §3.2)
       ↓
Phase 7 (verification + scan re-run)
       ↓
Owner deletes E:\Claude-Playground archive
```

## §5. Open architectural decisions requiring owner direction

1. **Where does GT-KB framework Python code live in-root?** Currently no `groundtruth_kb/` package exists at any path within `E:\GT-KB\`. Bridge-poller program (P1, P2, P2.5) and any future framework work need a home. Options:
   - `E:\GT-KB\src\groundtruth_kb\` (alongside existing `src/` Agent Red app code)
   - `E:\GT-KB\groundtruth_kb\` (top-level package)
   - `E:\GT-KB\framework\groundtruth_kb\` (new top-level `framework/` namespace)
   - "No framework package; everything is scripts under `E:\GT-KB\scripts\`"

2. **Auto-memory pattern:** sync-from-canonical (§3.2 #1-5) OR disable auto-memory entirely (§3.2 alternative)?

3. **Should `wrap_scan_hygiene.py` and `migrate_root_to_gtkb.py` be archived or refactored?** (Owner can audit.)

4. **In-root worktrees** at `E:\GT-KB\.claude\worktrees\` (`elegant-brattain`, `nifty-dewdney-16b037`, `vigorous-maxwell-d8aa93`) — KEEP, AUDIT, or REMOVE?

## §6. Risk + decision notes

- **Plan is multi-session.** Some phases (worktree cleanup, pip uninstall) are quick; others (bridge revisions) require Codex round-trips.
- **Owner is doing migration in parallel.** Prime work on Phase 1 items must not conflict; Prime defers to owner's edits to harness-config consumer scripts.
- **No data loss risk** if executed correctly — all migrations are FILE COPY + verify, then delete originals. Exception: pip uninstall may leave broken imports if scripts depend on installed package; verify in Phase 7.
- **Verification gate is empirical:** Slice 11 audit-hook lane reaching 0 violations + clean re-scans + owner ability to delete `E:\Claude-Playground` without breaking GT-KB.

## §7. Codex Review Asks

1. Confirm the inventory in §1 is comprehensive (or identify additional violation classes).
2. Confirm the §3 "cannot reside in E:\GT-KB" components + handling patterns are acceptable under the directive's "no exceptions" framing — particularly §3.1 (pip-installed package as DEPENDENCY not GT-KB artifact) and §3.2 (auto-memory as Claude Code cache, not canonical).
3. Confirm the phasing (§4) is correct ordering, particularly the gating of Phase 4c (bridge-poller P1/P2 REVISED) on §5 architectural decision 1 (where framework code lives in-root).
4. Confirm the §5 owner-decision questions are correctly framed and complete.
5. **GO / NO-GO** on this critical remediation plan as scope-of-program. Implementation of each phase will file separate sub-bridges as needed.

## §8. Decisions Needed From Owner

1. **§5 question 1** — framework code in-root location.
2. **§5 question 2** — auto-memory pattern.
3. **§5 question 3** — `wrap_scan_hygiene.py` + `migrate_root_to_gtkb.py` disposition.
4. **§5 question 4** — in-root worktrees disposition.
5. **Plan-level approval:** does this plan address the directive comprehensively, or are there additional concerns to fold in before Codex review?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
