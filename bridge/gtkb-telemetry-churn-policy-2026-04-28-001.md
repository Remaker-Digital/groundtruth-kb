NEW

# GTKB Telemetry Churn Policy

**Status:** NEW (P3 policy decision; awaits Codex GO)
**Date:** 2026-04-28 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** Codex Q1 of `bridge/s317-working-tree-triage-002.md` ("Treat large generated dashboard/history churn as a separate policy question if it keeps recurring") + observed recurrence across S317-working-tree-triage `Commit 6` and harness-state-authority-migration close-out.

---

## Prior Deliberations

- [bridge/s317-working-tree-triage-002.md](bridge/s317-working-tree-triage-002.md) Codex Q1 — first surfaced the policy question.
- [bridge/s317-working-tree-triage-005.md](bridge/s317-working-tree-triage-005.md) §1.5 — committed auto-regen telemetry per Q1's "commit for now" guidance; named GTKB-TELEMETRY-CHURN-POLICY as future work_list candidate.
- [bridge/s317-working-tree-triage-007.md](bridge/s317-working-tree-triage-007.md) — observed the recurrence concretely.
- [bridge/harness-state-authority-migration-2026-04-27-007.md](bridge/harness-state-authority-migration-2026-04-27-007.md) — second commit absorbed dashboard regen.

## §0. Scope

Decide whether the 5 auto-regen telemetry files should be:
- **Committed** on each session boundary (current behavior — preserves history; large diff churn each session).
- **Gitignored** entirely (no history; clean working tree always).
- **Hybrid**: gitignore high-churn files (`dashboard-data.json` 4900-line churn, `gtkb-dashboard-history.json` 1080-line churn); commit low-churn files (`session-startup-report.md`, `session-wrapup-report.md` ~10-line churn each; `pending-owner-decisions.md` durable owner-decision state).

**In scope:** A single `.gitignore` policy decision for the 5 files. No code changes.

**Out of scope:** Refactoring the dashboard regeneration logic; changing what's emitted; archive snapshots elsewhere.

---

## §1. Current state

5 files regenerate via `SessionStart` hook (`scripts/session_self_initialization.py`) and the owner-decision-tracker hook:

| File | Per-session diff churn | Content class |
|---|---|---|
| `docs/gtkb-dashboard/dashboard-data.json` | ~4900 lines | Pure machine-generated (timestamps + data snapshot) |
| `memory/gtkb-dashboard-history.json` | ~1080 lines | Append-only KPI history (session points + day points) |
| `docs/gtkb-dashboard/session-startup-report.md` | ~10-30 lines | Markdown render of startup model |
| `docs/gtkb-dashboard/session-wrapup-report.md` | ~1-5 lines | Markdown render of wrap-up model |
| `memory/pending-owner-decisions.md` | varies (0-50 lines) | **DURABLE owner-decision state**; not auto-regen, hook-tracked |

**Cumulative observed churn this session (S317):** ~6 commits absorbed dashboard auto-regen content; ~12,000 lines of dashboard-data.json diff committed across the session. ~5,000 of that is content; the rest is timestamp re-rendering.

---

## §2. Recommendation: Hybrid (Option C)

| File | Recommendation | Reasoning |
|---|---|---|
| `docs/gtkb-dashboard/dashboard-data.json` | **GITIGNORE** | Pure timestamp+snapshot regen; no historical value worth ~4900 lines per session; can be regenerated on demand. |
| `memory/gtkb-dashboard-history.json` | **GITIGNORE** | Append-only history file; the data IS the history, but it grows continuously and rebuilding is cheap. |
| `docs/gtkb-dashboard/session-startup-report.md` | **COMMIT** | Small (~30 lines); the human-readable startup snapshot is referenced in MEMORY.md and useful as a session-time anchor. |
| `docs/gtkb-dashboard/session-wrapup-report.md` | **COMMIT** | Small; same reasoning. |
| `memory/pending-owner-decisions.md` | **COMMIT** | Durable owner-decision state; hook-tracked; not auto-regen in the same sense as dashboard. |

**Net effect:** ~5980 lines of diff churn per session eliminated. Two small markdown reports + the pending-decisions state continue to commit as durable session-time anchors.

---

## §3. Implementation plan (1 commit)

**1 commit:** `gitignore: Move high-churn dashboard auto-regen files out of git tracking`.

Edit `.gitignore` to add:
```gitignore
# =============================================================================
# Dashboard auto-regen telemetry (churn policy per
# bridge/gtkb-telemetry-churn-policy-2026-04-28). The two large telemetry files
# regenerate on every SessionStart hook with timestamp + snapshot content; the
# diff churn (~5980 lines per session) is high and the data is reproducible.
# =============================================================================
docs/gtkb-dashboard/dashboard-data.json
memory/gtkb-dashboard-history.json
```

Then `git rm --cached` the 2 files (since they're currently tracked):
```
git rm --cached docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
```

Single commit captures the .gitignore addition + the index removal.

---

## §4. Verification

### §4.1 Files no longer tracked

```
$ git ls-files docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
# (empty — both untracked post-commit)
```

### §4.2 Files still on disk (not deleted)

```
$ ls -la docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
# Both present; ~50K + ~1MB sizes preserved
```

### §4.3 Subsequent session-start does NOT show them in `git status`

```
$ python scripts/session_self_initialization.py ...  # SessionStart regenerates files
$ git status --short
# Should show 0 modifications for the 2 gitignored files
```

### §4.4 Dashboard view still functional

`docs/gtkb-dashboard/index.html` reads `dashboard-data.json` from the same relative path; gitignoring doesn't break the dashboard view, just removes git tracking.

---

## §5. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Lose historical KPI snapshot data | LOW (P3) | Per-session points are derivable from KB queries + git log + bridge audit trail. The dashboard JSON is a snapshot, not the source of truth. |
| Dashboard view breaks because file is missing on fresh checkout | LOW (P3) | SessionStart hook regenerates the file at session boundary. Fresh checkout running the hook produces the file. |
| Other tooling depends on git-tracked dashboard-data.json | LOW (P3) | Verified via grep: `dashboard-data.json` is referenced by `index.html` (which reads it locally) and by `session_self_initialization.py` (which writes it). No git-tracking dependency. |
| Owner wants to preserve dashboard snapshots in git for forensics | LOW (P3) | If owner objects, REVISED-1 can choose Option A (commit, current behavior) instead. |

---

## §6. Codex review questions

1. **Policy scope:** Hybrid (Option C) acceptable, or prefer all-in (Option A keep committing) or all-out (Option B gitignore everything including reports)? Recommendation: Hybrid. Reports are small and human-readable; the JSONs are bulk telemetry.

2. **`pending-owner-decisions.md` continued tracking:** This file is hook-tracked (not session-regen) so it stays committed. Acceptable, or should it also move to gitignore for symmetry? Recommendation: keep tracked — it's durable owner-decision state with audit value.

3. **Git history of the two files:** Past dashboard-data.json commits remain in git history (no rewrite). Acceptable, or should this proposal also include a git filter-branch to clean history? Recommendation: no rewrite — past commits are immutable record; gitignore only affects future commits.

---

## §7. Owner directive compliance

- Project root boundary: ✓ all in-root.
- Bridge protocol: ✓ NEW awaits GO.
- `feedback_explicit_destructive_action_authorization.md`: ✓ no file deletions; `git rm --cached` removes from index but preserves on disk.
- `feedback_no_lossy_compression.md`: ✓ this isn't lossy compression of agent I/O; it's a tracking decision for derivable telemetry.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
