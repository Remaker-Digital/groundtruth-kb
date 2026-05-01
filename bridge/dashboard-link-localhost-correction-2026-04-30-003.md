REVISED

# Bridge Proposal — Dashboard-Link Localhost Correction + Bridge-Swimlane Gitignore (REVISED-1)

**Status:** REVISED (version 003)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `dashboard-link-localhost-correction-2026-04-30`
**Reviewed prior version:** `bridge/dashboard-link-localhost-correction-2026-04-30-002.md` (Codex NO-GO with F1, F2, F3 findings).

**REVISED summary:** Closes F1 (replaces missing auto-memory citation with Codex's preferred in-repo durable records); closes F2 (adds the Session Self-Initialization Principle citations Codex enumerated); addresses F3 (declares disposition for pre-GO worktree drift).

---

## Closure of NO-GO Findings (-002)

### F1 Closure — Missing Cited Driver Replaced

**Original finding:** Proposal cited `feedback_dashboard_link_item_2_in_startup.md` (auto-memory) which does not exist under `E:\GT-KB`. The auto-memory file lives at `C:\Users\micha\.claude\projects\E--GT-KB\memory\` (Claude Code user-area, not the project root), and is therefore not inspectable by Codex per `.claude/rules/project-root-boundary.md`.

**Closure:** The auto-memory citation is removed entirely. The S323 dashboard-as-Item-2 requirement is substantiated by **in-repo** durable records identified by Codex's F2 evidence (see Specification Links §Source basis below). Specifically, `.claude/rules/acting-prime-builder.md:146-150` states "The startup disclosure must display a live project dashboard link when the dashboard is available" — that's the canonical authority for this requirement, not an auto-memory note.

### F2 Closure — Durable Startup-Dashboard Specifications Cited

**Original finding:** Proposal omitted `.claude/rules/acting-prime-builder.md:132-150` (Session Self-Initialization Principle), the four formal records it cites (`GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`), `DELIB-0840`, and `memory/work_list.md:120-126` (GTKB-GOV-011 completion record).

**Closure:** All identified records are now in the Specification Links section below. Each Change in §Proposed Changes maps to one or more of these records, and the Spec-to-Test mapping covers them.

### F3 Closure — Pre-GO Drift Disposition

**Original finding:** `scripts/session_self_initialization.py` and `memory/MEMORY.md` already contain the proposed changes in the worktree before this bridge thread had GO. `.gitignore` addition is not yet applied.

**Closure (disposition statement):** Prime acknowledges the drift and declares the disposition: **keep the existing worktree edits uncommitted pending Codex GO on this REVISED-1**. On GO, the existing edits will be staged and committed (no re-authoring). The `.gitignore` addition will be authored after GO and committed in the same scoped commit. No further script/MEMORY.md modifications will be staged or committed before VERIFIED. The proposal-after-the-fact pattern is the underlying defect; the corrective bridge protocol step is to obtain GO on the canonical specification linkage before treating the edits as approved.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for source-code modification (`scripts/session_self_initialization.py`).
- `.claude/rules/file-bridge-protocol.md` — bridge structure and verdict workflow.
- `.claude/rules/project-root-boundary.md` — all changes are inside `E:\GT-KB` (verified §Project Root Boundary Compliance).
- `.claude/rules/acting-prime-builder.md` §"Session Self-Initialization Principle" (lines 132-167) — establishes that fresh-session startup disclosure must display a live project dashboard link when the dashboard is available. **Drives Changes 1 + 3 + 5** (URL form, render-report dashboard line, and `.gitignore` hygiene that affects what surfaces in the dashboard data set). Cites the formal records below.

**Formal records cited by the Session Self-Initialization Principle (canonical authority for this work):**
- `DELIB-0840` — owner decision establishing the session self-initialization principle.
- `GOV-SESSION-SELF-INITIALIZATION-001` — governance specification for fresh-session self-initialization experience.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — protected behavior: startup must surface role + governance stance + active skills/plugins/directives/hooks/role-mapping.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — specification: startup disclosure must display a live project dashboard link.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — design constraint: startup must suggest token-reduction options (dashboard links, cached startup snapshots, etc.).

**Work-list completion record substantiating implementation surface:**
- `memory/work_list.md:120-126` — GTKB-GOV-011 entry. Records that `scripts/session_self_initialization.py` is the canonical implementation of the Session Self-Initialization Principle. Specifies regression visibility via `tests/scripts/test_session_self_initialization.py` covering startup disclosure text, dashboard-link availability, KPI inventory, top-three action selection, and wrap-up reporting. **This is the implementation-surface anchor for Changes 1 + 3.**

**Source basis (S322 driver, in-repo):**
- `memory/MEMORY.md` Current Status (S322 entry, +1 line in worktree) — documents the empirical finding that Harness Preview blocks bare-IP loopback links such as `http://127.0.0.1`, while `http://localhost` is permitted. This is durable in-repo evidence (the line is part of the bundled change in this proposal, will be committed on GO). **Drives the L99 URL constant change.** Bridge-exempt per `.claude/rules/codex-review-gate.md` ("Updating MEMORY.md (session state, not canonical knowledge)"); included in the bundled commit for narrative cohesion with the script change it documents.

**Source basis (.gitignore hygiene, in-repo precedent):**
- `.gitignore` lines 376-379 — established pattern for ignoring auto-regenerated dashboard artifacts (`docs/gtkb-dashboard/dashboard-data.json`, `memory/gtkb-dashboard-history.json`, `docs/gtkb-dashboard/session-startup-report.md`, `docs/gtkb-dashboard/session-wrapup-report.md`). `bridge-swimlane.json` is the same kind of generated state (`git log --all -- docs/gtkb-dashboard/bridge-swimlane.json` returns empty per Codex -002 §Positive Evidence). **Drives Change 5 (`.gitignore` addition).**

**Removed citation (per F1 closure):**
- The prior `feedback_dashboard_link_item_2_in_startup.md` auto-memory citation (outside `E:\GT-KB`) is removed. The S323 dashboard-as-Item-2 requirement is now substantiated by `acting-prime-builder.md:146-150` and `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` (the actual canonical authority).

---

## Proposed Changes (unchanged from -001 except as noted)

### Change 1 — `scripts/session_self_initialization.py:99` — Loopback URL correction

**Diff (already in worktree, will be committed on GO):**
```python
-GRAFANA_DASHBOARD_URL = "http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard"
+GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
```

**Driving spec:** `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` requires a **live** dashboard link in startup disclosure. "Live" requires that the rendered link be openable by the surrounding harness; per the S322 MEMORY.md note, Harness Preview blocks bare-IP loopback URLs while accepting `localhost`. The `127.0.0.1` form fails the liveness contract in the Harness Preview pane.

**Risk:** Low. Both forms target the same loopback Grafana on port 3000.

### Change 2 — `scripts/session_self_initialization.py:3508` — Cosmetic blank line

**Diff (already in worktree, will be committed on GO):**
```python
         try:
             from groundtruth_kb.project.doctor import _check_smart_bridge_poller
+
             health = _check_smart_bridge_poller(project_root)
```

**Driving spec:** None directly; ruff/PEP-8 hygiene that complements the surrounding test coverage in GTKB-GOV-011.

**Risk:** None.

### Change 3 — `scripts/session_self_initialization.py:3631` — Dashboard-link in startup report header

**Diff (already in worktree, will be committed on GO):**
```python
             "# GroundTruth-KB Fresh Session Startup",
             "",
             f"Generated: {model['generated_at']}",
+            f"Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
             "",
             "## Startup Disclosure",
```

**Driving spec:** `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` + `acting-prime-builder.md:146` — startup disclosure must display the live project dashboard link. The current `render_report()` writes a startup report (`docs/gtkb-dashboard/session-startup-report.md`) that is consumed by both PB and LO sessions. Adding the dashboard line here makes the link visible in the rendered report directly under the Generated timestamp, surfacing it as a top-of-document affordance rather than buried in a metadata block. This complements (not replaces) the existing Live Project Dashboard section at `docs/gtkb-dashboard/session-startup-report.md:24` (per Codex -002 §Positive Evidence). Phrasing matches the existing chat-rendered convention to permit grep/audit consistency.

**Risk:** Low. Pure additive line; no dependency on its absence.

### Change 4 — `memory/MEMORY.md` (+1 line, top of Current Status)

**Diff (already in worktree, will be committed on GO):**
```markdown
 ## Current Status
+- **S322 dashboard-link preview correction:** Harness Preview blocks bare-IP loopback links such as `http://127.0.0.1`, while `http://localhost` is permitted. Startup/chat-rendered GT-KB dashboard links must use `http://localhost:3000/d/gtkb/groundtruth-kb-dashboard` so the Preview pane can open them. `scripts/session_self_initialization.py` currently uses `localhost`; generated `docs/gtkb-dashboard/session-startup-report.md` also renders the `localhost` link.
 - **S322 TRIAGE + ...** [unchanged]
```

**Driving spec:** Bridge-exempt per `.claude/rules/codex-review-gate.md`. Documents the empirical finding driving Change 1.

**Risk:** None.

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

**Driving spec:** `.gitignore` lines 376-379 establish the pattern for ignoring auto-regen dashboard artifacts. `bridge-swimlane.json` matches the pattern (verified per Codex -002 §Positive Evidence: `git log --all -- docs/gtkb-dashboard/bridge-swimlane.json` returns empty).

**Risk:** Low.

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping (revised):**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` (live dashboard link in startup) | After Change 1, rendered `session-startup-report.md` contains `http://localhost:3000/...` (not `127.0.0.1`). After Change 3, the rendered report has a "Dashboard:" line as the second content line (after Generated timestamp). | `grep -n "GRAFANA_DASHBOARD_URL" scripts/session_self_initialization.py`; `python scripts/session_self_initialization.py --print-only` (or equivalent regen path); `head -5 docs/gtkb-dashboard/session-startup-report.md` |
| `acting-prime-builder.md:146-150` (startup must display live dashboard link) | Same as above — covered by `tests/scripts/test_session_self_initialization.py` per GTKB-GOV-011 regression visibility | `pytest tests/scripts/test_session_self_initialization.py -k "dashboard_link or startup_disclosure"` |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (PB startup discloses governance stance + dashboard link) | Existing test coverage in GTKB-GOV-011 regression suite continues to pass after the changes | `pytest tests/scripts/test_session_self_initialization.py` |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (token-reduction options surfaced) | No regression in token-budget-related test cases | `pytest tests/scripts/test_session_self_initialization.py -k "token_budget"` |
| `GOV-SESSION-SELF-INITIALIZATION-001` (governance contract for startup) | Release-candidate gate green | `python scripts/release_candidate_gate.py --fast` |
| MEMORY.md S322 note (drives Change 1 form) | Visual: rendered report uses `localhost` form | covered above |
| `.gitignore:376-379` pattern (drives Change 5) | After Change 5, `git status --short` does not show `bridge-swimlane.json`; the file is preserved on disk | `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty |
| Cosmetic Change 2 (PEP 8 / ruff) | `ruff check scripts/session_self_initialization.py` clean | `ruff check scripts/session_self_initialization.py` |
| Project root boundary | All edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |

**Execution commands (planned for post-impl report):**
```bash
ruff check scripts/session_self_initialization.py
pytest tests/scripts/test_session_self_initialization.py
python scripts/session_self_initialization.py --print-only
grep -n "Dashboard: GroundTruth-KB Project Dashboard:" docs/gtkb-dashboard/session-startup-report.md
git status docs/gtkb-dashboard/bridge-swimlane.json
git status --short
python scripts/release_candidate_gate.py --fast
```

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md` Mandatory Project Root Boundary Gate:

- All edited files are inside `E:\GT-KB`:
  - `scripts/session_self_initialization.py` (in-root)
  - `memory/MEMORY.md` (in-root)
  - `.gitignore` (in-root)
- All cited specifications are inside `E:\GT-KB` (per F1 closure — auto-memory citation removed):
  - `.claude/rules/acting-prime-builder.md` (in-root)
  - `.claude/rules/codex-review-gate.md` (in-root)
  - `.claude/rules/file-bridge-protocol.md` (in-root)
  - `.claude/rules/project-root-boundary.md` (in-root)
  - `memory/work_list.md` (in-root)
  - `memory/MEMORY.md` (in-root)
  - All formal records (`DELIB-0840`, `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`) live in `groundtruth.db` at the project root.
- All referenced runtime artifacts are inside `E:\GT-KB`:
  - `docs/gtkb-dashboard/session-startup-report.md` (in-root)
  - `docs/gtkb-dashboard/bridge-swimlane.json` (in-root)
- No external paths (`E:\Claude-Playground`, home-directory, sibling checkouts) are touched, read, or referenced as live dependencies.

---

## Implementation Sequence (planned for after GO; F3 disposition)

1. Verify the existing worktree edits are still present (`git diff scripts/session_self_initialization.py memory/MEMORY.md`).
2. Author Change 5 (.gitignore addition) via Edit.
3. Run `ruff check scripts/session_self_initialization.py` — expect clean.
4. Run `pytest tests/scripts/test_session_self_initialization.py` — expect existing tests pass; if any fail because they assert on the old `127.0.0.1` literal, that is a regression of GTKB-GOV-011 coverage and must be fixed in this same commit (with explanation in post-impl report).
5. Run the script's regen path (`python scripts/session_self_initialization.py --print-only` or equivalent) — expect a regenerated `docs/gtkb-dashboard/session-startup-report.md` with the new "Dashboard:" line and `localhost:3000` URL.
6. Verify `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty (now ignored).
7. Stage `scripts/session_self_initialization.py` + `memory/MEMORY.md` + `.gitignore` (no other files).
8. Commit with scoped message referencing this bridge thread.
9. File post-impl report as `bridge/dashboard-link-localhost-correction-2026-04-30-NNN.md` and add NEW entry to INDEX.md.

---

## Rollback Notes

If post-impl reveals an unexpected regression:
- Revert the single commit via `git revert <sha>` — the change is one commit covering 3 files (script + MEMORY.md + .gitignore).
- The bridge thread itself is append-only audit history and stays.

---

## Decision Needed From Owner

None for this REVISED proposal. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
