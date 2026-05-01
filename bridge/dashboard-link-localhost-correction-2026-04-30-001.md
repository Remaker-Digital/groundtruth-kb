NEW

# Bridge Proposal — Dashboard-Link Localhost Correction + Bridge-Swimlane Gitignore

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `dashboard-link-localhost-correction-2026-04-30`
**Trigger:** S324 worktree triage (post-Slice-1-VERIFIED at `5c54d715`) surfaced four out-of-scope modifications. Three of them (one source-code file + one MEMORY.md note + one untracked generated file) form a coherent dashboard-link cluster with documented S322/S323 drivers but no prior bridge thread. Owner answered S324 AskUserQuestion: "File bundled bridge proposal."

**Owner pre-approval:** Yes — for filing this proposal. Bridge protocol still requires Codex GO before commit per `.claude/rules/codex-review-gate.md`.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for source-code modification (`scripts/session_self_initialization.py`).
- `.claude/rules/file-bridge-protocol.md` — bridge structure and verdict workflow.
- `.claude/rules/project-root-boundary.md` — all changes are inside `E:\GT-KB` (verified §5).

**Source basis (S322/S323 drivers, pre-existing in tracked artifacts):**
- `memory/MEMORY.md` Current Status (S322) — documents that Harness Preview blocks bare-IP loopback links such as `http://127.0.0.1`, while `http://localhost` is permitted. **Drives the L99 URL constant change.** The MEMORY.md note itself was added in the worktree as part of this cluster but is bridge-exempt per the codex-review-gate rule's MEMORY.md exception clause.
- Auto-memory `feedback_dashboard_link_item_2_in_startup.md` (S323) — owner feedback memory: "Dashboard link as Item 2 in startup must be present for both PB and LO; never buried in metadata block." **Drives the L3631 dashboard-link rendering addition** to `render_report()`.
- `.gitignore` lines 376-379 — established pattern for ignoring auto-regenerated dashboard artifacts (`dashboard-data.json`, `session-startup-report.md`, `session-wrapup-report.md`). `bridge-swimlane.json` is the same kind of generated state (verified: `git log --all -- docs/gtkb-dashboard/bridge-swimlane.json` returns empty; never committed historically). **Drives the .gitignore addition.**

**Rule files that constrain this work:**
- `.claude/rules/codex-review-gate.md` (above)
- `.claude/rules/file-bridge-protocol.md` (above)
- `.claude/rules/project-root-boundary.md` (above)

---

## Proposed Changes

### Change 1 — `scripts/session_self_initialization.py:99` — Loopback URL correction

**Diff (already in worktree):**
```python
-GRAFANA_DASHBOARD_URL = "http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard"
+GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
```

**Justification:** Per the S322 MEMORY.md note, Harness Preview blocks bare-IP loopback links. `localhost:3000` resolves to the same Grafana instance but renders as a clickable link in the Preview pane. The S323 dashboard-as-Item-2 feedback only delivers value if the link is actually clickable in the harness — the URL form is the gating constraint.

**Risk:** Low. Both forms target the same loopback Grafana on port 3000; no environment configuration changes. If a downstream caller hard-codes `127.0.0.1` for comparison, that would be a bug regardless.

### Change 2 — `scripts/session_self_initialization.py:3508` — Cosmetic blank line

**Diff (already in worktree):**
```python
         try:
             from groundtruth_kb.project.doctor import _check_smart_bridge_poller
+
             health = _check_smart_bridge_poller(project_root)
```

**Justification:** PEP 8 / ruff E305 compliance — blank line between import-style statement and following logic. Cosmetic only.

**Risk:** None.

### Change 3 — `scripts/session_self_initialization.py:3631` — Dashboard-link in startup report header

**Diff (already in worktree):**
```python
             "# GroundTruth-KB Fresh Session Startup",
             "",
             f"Generated: {model['generated_at']}",
+            f"Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
             "",
             "## Startup Disclosure",
```

**Justification:** S323 owner feedback mandates the dashboard link as Item 2 in startup output. The current `render_report()` writes a startup report consumed by both PB and LO; adding the line here makes the link visible in `docs/gtkb-dashboard/session-startup-report.md` directly under the Generated timestamp. The phrasing "Dashboard: GroundTruth-KB Project Dashboard: {link}" matches the existing chat-rendered phrasing convention (allows future grep/audit consistency).

**Risk:** Low. Pure additive line in a generated report; no dependency on its absence.

### Change 4 — `memory/MEMORY.md` (+1 line, top of Current Status)

**Diff (already in worktree):**
```markdown
 ## Current Status
+- **S322 dashboard-link preview correction:** Harness Preview blocks bare-IP loopback links such as `http://127.0.0.1`, while `http://localhost` is permitted. Startup/chat-rendered GT-KB dashboard links must use `http://localhost:3000/d/gtkb/groundtruth-kb-dashboard` so the Preview pane can open them. `scripts/session_self_initialization.py` currently uses `localhost`; generated `docs/gtkb-dashboard/session-startup-report.md` also renders the `localhost` link.
 - **S322 TRIAGE + MOJIBAKE VERIFIED + SLICE A IMPLEMENTED ...** [unchanged]
```

**Justification:** Bridge-exempt per `.claude/rules/codex-review-gate.md` ("Updating MEMORY.md (session state, not canonical knowledge)"). Included in the bundle because it's the documented driver for Change 1 and ships in the same commit for narrative cohesion.

**Risk:** None. MEMORY.md is operational state; the line documents an established constraint.

### Change 5 — `.gitignore` — Ignore `bridge-swimlane.json`

**Proposed diff (not yet in worktree; will be authored on GO):**
```
 # `write_dashboard_and_report(...)` at session boundary; tracking creates noise.
 docs/gtkb-dashboard/dashboard-data.json
 memory/gtkb-dashboard-history.json
 docs/gtkb-dashboard/session-startup-report.md
 docs/gtkb-dashboard/session-wrapup-report.md
+docs/gtkb-dashboard/bridge-swimlane.json
```

**Justification:** `git log --all -- docs/gtkb-dashboard/bridge-swimlane.json` returns empty — the file has never been committed. Its content (102-thread bridge-state snapshot generated `2026-04-30T23:41:12`) is exactly the same kind of regenerated dashboard data as the three siblings already ignored at `.gitignore:376-379`. Adding it to the ignore list closes a tracked gap.

**Risk:** Low. If a downstream tool expects the file in git history (none observed), the absence becomes visible. The current state — untracked but on disk — is more error-prone (likely to be accidentally `git add .`-ed).

---

## Tests / Verification (specification-derived)

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping:**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| MEMORY.md S322 note (drives Change 1) | Visual: rendered `session-startup-report.md` contains `http://localhost:3000/...` (not `127.0.0.1`) | `grep -n "GRAFANA_DASHBOARD_URL" scripts/session_self_initialization.py` after edit; `grep -n "localhost:3000" docs/gtkb-dashboard/session-startup-report.md` after `python scripts/session_self_initialization.py` regenerates the report |
| `feedback_dashboard_link_item_2_in_startup.md` (drives Change 3) | Visual: rendered report has a "Dashboard:" line as the second content line under the "# GroundTruth-KB Fresh Session Startup" heading (after Generated timestamp) | `head -5 docs/gtkb-dashboard/session-startup-report.md` after regeneration — should include the Dashboard line |
| `.gitignore:376-379` pattern (drives Change 5) | `git status --short` shows `bridge-swimlane.json` no longer untracked after .gitignore edit; the file is preserved on disk | `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty (ignored) |
| `.claude/rules/codex-review-gate.md` (protocol authority) | Release-candidate gate passes with the 5 quality guardrails GREEN | `python scripts/release_candidate_gate.py --fast` (or equivalent) on staged changes |
| Cosmetic Change 2 (PEP 8 / ruff) | `ruff check scripts/session_self_initialization.py` clean | `ruff check scripts/session_self_initialization.py` |

**Execution commands (planned for post-impl report):**
```bash
ruff check scripts/session_self_initialization.py
python scripts/session_self_initialization.py --print-only  # regenerate report
grep -n "Dashboard: GroundTruth-KB Project Dashboard:" docs/gtkb-dashboard/session-startup-report.md
git status docs/gtkb-dashboard/bridge-swimlane.json
git status --short
```

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md` Mandatory Project Root Boundary Gate:

- All edited files are inside `E:\GT-KB`:
  - `scripts/session_self_initialization.py` (in-root)
  - `memory/MEMORY.md` (in-root)
  - `.gitignore` (in-root)
- All referenced runtime artifacts are inside `E:\GT-KB`:
  - `docs/gtkb-dashboard/session-startup-report.md` (in-root)
  - `docs/gtkb-dashboard/bridge-swimlane.json` (in-root)
- No external paths (`E:\Claude-Playground`, home-directory, sibling checkouts) are touched, read, or referenced as live dependencies.

---

## Implementation Sequence (planned for after GO)

1. Verify the three script edits are still in worktree (`git diff scripts/session_self_initialization.py`).
2. Stage `scripts/session_self_initialization.py` + `memory/MEMORY.md`.
3. Author the `.gitignore` addition (one new line under existing dashboard-regen block).
4. Stage `.gitignore`.
5. Run `ruff check scripts/session_self_initialization.py` — expect clean.
6. Run `python scripts/session_self_initialization.py --print-only` (or equivalent regen path) — expect a regenerated `docs/gtkb-dashboard/session-startup-report.md` with the new "Dashboard:" line.
7. Verify `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty (now ignored).
8. Commit with scoped message referencing this bridge thread.
9. File post-impl report as `-NNN.md` and add NEW entry to INDEX.md.

---

## Rollback Notes

If post-impl reveals an unexpected regression:
- Revert the single commit via `git revert <sha>` — the change is one commit covering 3 files (script + MEMORY.md + .gitignore).
- The bridge file itself is append-only audit history and stays.

The risk surface is small (one URL constant + one render-report line + one .gitignore line + one MEMORY.md note); a clean revert restores the prior state with no migration needed.

---

## Decision Needed From Owner

None for this proposal. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
