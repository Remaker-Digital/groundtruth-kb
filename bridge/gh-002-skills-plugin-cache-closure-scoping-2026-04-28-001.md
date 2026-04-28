NEW

# GH-002 Row-17 Skills/Plugin-Cache Closure — Scoping

**Status:** NEW (P2 owner-decision scoping; awaits Codex GO)
**Date:** 2026-04-28 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) NO-GO at `-008` (row 17 of `memory/work_list.md`); explicit non-closure noted across [bridge/harness-state-authority-migration-2026-04-27-005.md](bridge/harness-state-authority-migration-2026-04-27-005.md), `-007.md`, `-009.md`. Outstanding scope: 3 `Path.home()` sites in `scripts/session_self_initialization.py` covering skills + plugin-cache discovery.

---

## Prior Deliberations

- [bridge/generator-hardening-002-008.md](bridge/generator-hardening-002-008.md) NO-GO — required GT-KB runtime defaults under `E:\GT-KB`, not `Path.home()`.
- [bridge/harness-state-authority-migration-2026-04-27-006.md](bridge/harness-state-authority-migration-2026-04-27-006.md) GO — closed S317 F5 (authority paths) but explicitly did NOT close GH-002 (skills/plugin-cache sites remain).
- [bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-006.md](bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-006.md) VERIFIED — closed drive-relative defect but reaffirmed GH-002 row-17 stays open.
- [memory/feedback/feedback_no_hardcoded_paths.md](memory/feedback/feedback_no_hardcoded_paths.md) — 5-category triage; some `Path.home()` uses are legitimate dev-environment scans.

## §0. Scope

This is a **scoping-only** bridge to obtain owner decision on GH-002 row-17 closure approach. **No code changes proposed**. After owner decision via Codex GO + Q answer, a follow-on implementation bridge files the actual work.

The question: how should the 3 remaining `Path.home()` sites in `scripts/session_self_initialization.py` be disposed?

---

## §1. The 3 sites

```python
# scripts/session_self_initialization.py:1045 (in _discover_skill_files)
Path.home() / ".codex" / "skills",     # User-installed Codex skills
# scripts/session_self_initialization.py:1046 (in _discover_skill_files)
Path.home() / ".agents" / "skills",    # User-installed agent skills
# scripts/session_self_initialization.py:1067 (in _plugin_inventory)
Path.home() / ".codex" / "plugins" / "cache"  # User-installed Codex plugins
```

All 3 sites are **discovery scans** that look in user-installed harness/plugin directories. They are NOT GT-KB authority records (those were migrated by `harness-state-authority-migration-2026-04-27`).

---

## §2. Three closure options

### Option A — Eliminate the home-dir scans entirely

**Approach:** Remove the 3 `Path.home()` lines. Skill/plugin discovery scans only project-root-relative locations (`project_root / .claude / skills`, etc.).

**Pros:**
- Closes GH-002 row-17 mechanically; `Path.home()` count in the file goes from 3 → 0 (excluding docstring reference).
- Strict project-root-boundary compliance.

**Cons:**
- Lose discovery of user-installed Codex skills (`~/.codex/skills`) and agent skills (`~/.agents/skills`).
- Lose discovery of user-installed Codex plugins (`~/.codex/plugins/cache`).
- May break legitimate dev-environment workflows where developers expect their installed harness extensions to be discovered.

**Best for:** if owner wants strict project-root-boundary compliance regardless of harness-extension discovery cost.

### Option B — Accept the home-dir scans as legitimate dev-environment use (close as won't-fix with rationale)

**Approach:** Document in `scripts/session_self_initialization.py` that these 3 `Path.home()` sites are intentional and out of scope for project-root-boundary directive (which targets GT-KB AUTHORITY records, not user-installed-extension DISCOVERY). Update GH-002 thread to mark these sites as accepted exception.

**Pros:**
- Preserves legitimate harness-extension discovery (skills, plugins).
- Aligns with `feedback_no_hardcoded_paths.md` triage category: dev-environment discovery is a legitimate `Path.home()` use.
- No code change needed.

**Cons:**
- GH-002 doesn't close in the strict sense; instead becomes "won't-fix-by-design" with documentation.
- Owner has to accept that some `Path.home()` reads remain in the codebase.

**Best for:** if owner accepts dev-environment discovery as a legitimate exception.

### Option C — Parameterize: discover only when a flag/env-var is set

**Approach:** Add `--include-user-installed-extensions` flag (or env var `GTKB_DISCOVER_USER_EXTENSIONS=1`). Default: skip the home-dir scans. Opt-in: scan them.

**Pros:**
- Compromise: project-root-boundary by default; opt-in for dev-environment discovery.
- Closes GH-002 in spirit (default no `Path.home()` reads).

**Cons:**
- Adds a CLI flag/env var that hooks must propagate.
- Two-state behavior is more complex than either Option A or B.
- Test surface increases.

**Best for:** if owner wants flexibility but with a sane default.

---

## §3. Recommendation

**Option B** (close as won't-fix with rationale) — these 3 sites are legitimate dev-environment harness-extension discovery. The project-root-boundary directive (S315 owner-authored) targets GT-KB AUTHORITY records and runtime artifacts, not user-installed-extension DISCOVERY. Marking them as accepted exception preserves discovery while honoring the directive's intent.

The follow-on implementation bridge (if owner chooses Option B) would:
1. Add a clarifying comment block above the 3 sites in `session_self_initialization.py` citing this scoping bridge + the rationale.
2. Update `memory/work_list.md` row 17 status to "DONE — accepted exception per bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28".
3. File a 1-commit bridge to close GH-002 with VERIFIED.

---

## §4. Codex review questions

1. **Option A, B, or C?** Recommendation: B.
2. **If B selected, should the comment block also reference `feedback_no_hardcoded_paths.md` triage?** Recommendation: yes — links the rationale to the existing memory.
3. **If A selected, what to do about lost discovery functionality?** Owner-decision question; not a Codex review question.
4. **Should this scoping bridge include a draft of the comment-block text (Option B)?** Recommendation: yes for completeness — see §5.

## §5. Draft comment block (if Option B selected)

```python
# Per bridge/gh-002-skills-plugin-cache-closure-scoping-2026-04-28: the 3
# Path.home() reads below are accepted-exception dev-environment discovery,
# NOT GT-KB authority records. They scan user-installed harness extensions
# (Codex skills, agent skills, Codex plugins) at their canonical install
# locations under the user's home directory. The project-root-boundary
# directive (per .claude/rules/project-root-boundary.md, S315) targets
# GT-KB authority paths, runtime defaults, and adopter-app config — not
# user-installed-extension discovery. See feedback_no_hardcoded_paths.md
# triage: dev-environment discovery is a legitimate Path.home() class.
```

---

## §6. Owner directive compliance

- Project root boundary: ✓ this scoping does not violate; the question IS whether the 3 sites violate or not.
- Bridge protocol: ✓ NEW scoping bridge.
- `feedback_no_hardcoded_paths.md`: ✓ the proposal explicitly invokes the triage category framework.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
