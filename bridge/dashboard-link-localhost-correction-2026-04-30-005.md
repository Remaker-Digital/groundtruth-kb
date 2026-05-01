REVISED

# Bridge Proposal — Dashboard-Link Localhost Correction + Bridge-Swimlane Gitignore (REVISED-2)

**Status:** REVISED (version 005)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `dashboard-link-localhost-correction-2026-04-30`
**Reviewed prior version:** `bridge/dashboard-link-localhost-correction-2026-04-30-004.md` (Codex NO-GO with F1, F2, F3 findings on the verification plan and test scope).

**REVISED-2 summary:** Closes -004 F1 (replaces nonexistent `--print-only` flag with the real `--emit-report` flag); closes -004 F2 (replaces zero-matching pytest selector with full-file run + a verified narrowed selector for assertions); closes -004 F3 (adds `tests/scripts/test_session_self_initialization.py` URL-assertion updates to first-class commit scope at the 9 specific line locations).

---

## Closure of NO-GO Findings (-004)

### F1 Closure — Executable Regeneration Command

**Original finding:** The verification plan and implementation sequence repeatedly cited `python scripts/session_self_initialization.py --print-only`. The script's argparse surface (`scripts/session_self_initialization.py:5436-5527`) does not define `--print-only`; the available flags are `--project-root`, `--dashboard-dir`, `--history-path`, `--emit-report`, `--emit-startup-service-payload`, `--emit-wrapup`, `--force-wrapup`, `--lifecycle-guard-path`, `--role-record-path`, `--user-preferences-path`, `--harness-name`, `--json`, `--role-profile`, `--fast-hook`, `--skip-bridge-maintenance`. Codex confirmed the failure by direct execution: `error: unrecognized arguments: --print-only`.

**Closure:** All references to `--print-only` are removed. The replacement command is `python scripts/session_self_initialization.py --emit-report` (defined at `scripts/session_self_initialization.py:5456`; help text: "Print the startup report after writing it"). This flag both writes the startup report to `docs/gtkb-dashboard/session-startup-report.md` and prints it to stdout, which is what the verification needs.

### F2 Closure — Pytest Selector Replaced with a Verified Run Path

**Original finding:** The mapping cited `pytest tests/scripts/test_session_self_initialization.py -k "dashboard_link or startup_disclosure"`. Codex confirmed by direct execution: 55 collected, all 55 deselected, 0 selected. The `-k` tokens did not match any test name in the file.

**Closure:** The narrowed selector is dropped. The verification path runs the **full** `tests/scripts/test_session_self_initialization.py` file (55 tests, ~few seconds locally per Codex's collection report). For visibility into which tests directly exercise the URL surface, post-impl will additionally report results from a verified narrowed selector based on actual test names: `pytest tests/scripts/test_session_self_initialization.py -k "dashboard_and_report or render_report or direct_script_execution"` (these tokens appear in test names per Codex's `-004` evidence at line 53: `test_dashboard_and_report_are_written_with_time_series_kpi`, `test_direct_script_execution_emits_startup_payload`; the broader `render_report` token matches multiple existing test names per the `module.render_report(...)` call sites at test file lines 232, 505, 547). If the narrowed selector still matches zero tests at execution time, post-impl will fall back to the full-file result and document the selector mismatch as a separate hygiene item.

### F3 Closure — Test Updates Are First-Class Commit Scope

**Original finding:** The proposal acknowledged that tests might need fixing if they assert the old URL literal, but only listed `scripts/session_self_initialization.py`, `memory/MEMORY.md`, and `.gitignore` in the staged-files list. Codex's direct check found 3 assertions in `tests/scripts/test_session_self_initialization.py` at lines 674, 761, 764 that already fail with the current worktree change in place.

**Closure:** `tests/scripts/test_session_self_initialization.py` is added to the proposed Changes (Change 6 below) and to the implementation sequence and stage/commit list. The proposal now specifies all 9 URL hits in the test file by line number, the type of update (assertion vs. fixture), and the expected new value. The spec-to-test mapping treats these tests as primary regression coverage for the URL change, not implicit dependencies.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Governance specs / records that constrain this work:**
- `.claude/rules/codex-review-gate.md` — protocol authority requiring this bridge for source-code modification (`scripts/session_self_initialization.py` + `tests/scripts/test_session_self_initialization.py`).
- `.claude/rules/file-bridge-protocol.md` — bridge structure and verdict workflow.
- `.claude/rules/project-root-boundary.md` — all changes are inside `E:\GT-KB`.
- `.claude/rules/acting-prime-builder.md` §"Session Self-Initialization Principle" (lines 132-167) — establishes that fresh-session startup disclosure must display a live project dashboard link when the dashboard is available. **Drives Changes 1 + 3** (URL form + render-report dashboard line). Cites the formal records below.

**Formal records cited by the Session Self-Initialization Principle (canonical authority):**
- `DELIB-0840` — owner decision establishing the session self-initialization principle.
- `GOV-SESSION-SELF-INITIALIZATION-001` — governance specification for fresh-session self-initialization experience.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — protected behavior: startup must surface role + governance stance + active skills/plugins/directives/hooks/role-mapping.
- `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — specification: startup disclosure must display a live project dashboard link.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — design constraint: startup must suggest token-reduction options.

**Work-list completion record substantiating implementation surface:**
- `memory/work_list.md:120-126` — GTKB-GOV-011 entry. Records `scripts/session_self_initialization.py` as the canonical implementation of the Session Self-Initialization Principle and `tests/scripts/test_session_self_initialization.py` as the regression coverage. **This is the implementation-surface anchor for Changes 1 + 3 + 6.**

**Source basis (S322 driver, in-repo):**
- `memory/MEMORY.md` Current Status (S322 entry, +1 line in worktree) — empirical finding that Harness Preview blocks bare-IP loopback links, while `localhost` is permitted. **Drives Change 1.** Bridge-exempt per `.claude/rules/codex-review-gate.md`.

**Source basis (.gitignore hygiene, in-repo precedent):**
- `.gitignore` lines 376-379 — established pattern for ignoring auto-regen dashboard artifacts. `bridge-swimlane.json` matches the pattern (`git log --all -- docs/gtkb-dashboard/bridge-swimlane.json` returns empty per Codex `-002` §Positive Evidence). **Drives Change 5.**

---

## Proposed Changes

### Change 1 — `scripts/session_self_initialization.py:99` — Loopback URL correction

**Diff (already in worktree, will be committed on GO):**
```python
-GRAFANA_DASHBOARD_URL = "http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard"
+GRAFANA_DASHBOARD_URL = "http://localhost:3000/d/gtkb/groundtruth-kb-dashboard"
```

**Driving spec:** `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` — live dashboard link must be openable by the surrounding harness; per the S322 MEMORY.md finding, `127.0.0.1` form fails the liveness contract in Harness Preview.

**Risk:** Low.

### Change 2 — `scripts/session_self_initialization.py:3508` — Cosmetic blank line

**Diff (already in worktree, will be committed on GO):**
```python
         try:
             from groundtruth_kb.project.doctor import _check_smart_bridge_poller
+
             health = _check_smart_bridge_poller(project_root)
```

**Driving spec:** ruff/PEP-8 hygiene.

**Risk:** None.

### Change 3 — `scripts/session_self_initialization.py:3631` — Dashboard-link in startup-report header

**Diff (already in worktree, will be committed on GO):**
```python
             "# GroundTruth-KB Fresh Session Startup",
             "",
             f"Generated: {model['generated_at']}",
+            f"Dashboard: GroundTruth-KB Project Dashboard: {dashboard_link}",
             "",
             "## Startup Disclosure",
```

**Driving spec:** `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` + `acting-prime-builder.md:146`.

**Risk:** Low.

### Change 4 — `memory/MEMORY.md` (+1 line, top of Current Status)

**Diff (already in worktree, will be committed on GO):**
```markdown
 ## Current Status
+- **S322 dashboard-link preview correction:** ...localhost-only Preview behavior...
 - **S322 TRIAGE + ...** [unchanged]
```

**Driving spec:** Bridge-exempt per `.claude/rules/codex-review-gate.md`.

**Risk:** None.

### Change 5 — `.gitignore` — Ignore `bridge-swimlane.json`

**Proposed diff (not yet in worktree; authored on GO):**
```
 docs/gtkb-dashboard/dashboard-data.json
 memory/gtkb-dashboard-history.json
 docs/gtkb-dashboard/session-startup-report.md
 docs/gtkb-dashboard/session-wrapup-report.md
+docs/gtkb-dashboard/bridge-swimlane.json
```

**Driving spec:** `.gitignore:376-379` precedent.

**Risk:** Low.

### Change 6 — `tests/scripts/test_session_self_initialization.py` — URL fixture and assertion updates (NEW in REVISED-2)

**Driving spec:** GTKB-GOV-011 regression visibility per `memory/work_list.md:120-126`. Test fixtures must match the production `GRAFANA_DASHBOARD_URL` constant after Change 1; assertions on the rendered URL must match the new constant.

**Specific updates (9 hits at known line numbers, all changing `http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard` to `http://localhost:3000/d/gtkb/groundtruth-kb-dashboard`):**

| Line | Type | Code excerpt | Update reason |
|---|---|---|---|
| 60 | Fixture (variable) | `dashboard_url = "http://127.0.0.1:3000/..."` | Test fixture: must match production constant for realistic scenario |
| 232 | Fixture (call arg) | `module.render_report(model, "http://127.0.0.1:3000/...", REPO_ROOT)` | Test passes URL into `render_report`; must match production constant |
| 465 | Fixture (call arg) | `"http://127.0.0.1:3000/..."` | Same pattern as line 232 |
| 480 | Fixture (call arg) | `"http://127.0.0.1:3000/..."` | Same pattern |
| 505 | Fixture (call arg) | `module.render_report(model, "http://127.0.0.1:3000/...", REPO_ROOT)` | Same pattern |
| 547 | Fixture (call arg) | `module.render_report(model, "http://127.0.0.1:3000/...", REPO_ROOT)` | Same pattern |
| 674 | **Assertion (FAILS without fix)** | `assert result["dashboard_url"] == "http://127.0.0.1:3000/..."` | Codex `-004` confirmed direct failure: "implementation now returns `http://localhost:3000/...` while the test still expects `http://127.0.0.1:3000/...`" |
| 761 | **Assertion (FAILS without fix)** | `assert "http://127.0.0.1:3000/..." in report_text` | Will fail because rendered report uses production constant |
| 764 | **Assertion (FAILS without fix)** | `assert "http://127.0.0.1:3000/..." in wrapup_text` | Same as 761 for wrap-up text |

**Update operation:** Single global replace within the file: `http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard` → `http://localhost:3000/d/gtkb/groundtruth-kb-dashboard` (9 occurrences). Implemented via `Edit` tool with `replace_all: true`.

**Verification after update:**
- `grep -c "127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py` returns 0.
- `grep -c "localhost:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py` returns 9.
- `pytest tests/scripts/test_session_self_initialization.py` passes.

**Risk:** Low. Pure literal replacement; no semantic change to the test logic. Preserves the exact 3-tuple of asserted forms (`result["dashboard_url"]`, `report_text` substring, `wrapup_text` substring).

---

## Specification-Derived Verification

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification-Derived Verification Gate:

**Spec-to-test mapping (REVISED-2):**

| Linked spec / driver | Test / verification | Command |
|---|---|---|
| `SPEC-PROJECT-DASHBOARD-KPI-LINK-001` (live dashboard link) | After Changes 1+3+6, full test suite passes; rendered report contains `localhost:3000` (not `127.0.0.1`); rendered report has "Dashboard:" line as second content line under heading | `pytest tests/scripts/test_session_self_initialization.py` (full file); `python scripts/session_self_initialization.py --emit-report`; `head -5 docs/gtkb-dashboard/session-startup-report.md`; `grep -n "localhost:3000" docs/gtkb-dashboard/session-startup-report.md` |
| `acting-prime-builder.md:146-150` (startup discloses live dashboard link) | Covered by full test suite per GTKB-GOV-011 regression visibility | `pytest tests/scripts/test_session_self_initialization.py` |
| `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (governance + dashboard link in startup) | Same — full suite | `pytest tests/scripts/test_session_self_initialization.py` |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (token-reduction options) | Same — full suite | `pytest tests/scripts/test_session_self_initialization.py` |
| `GOV-SESSION-SELF-INITIALIZATION-001` (governance contract) | Release-candidate gate green | `python scripts/release_candidate_gate.py --fast` |
| MEMORY.md S322 note (drives Change 1 form) | Visual: rendered report uses `localhost` form | covered above |
| `.gitignore:376-379` pattern (drives Change 5) | After Change 5, `git status --short` does not show `bridge-swimlane.json`; the file remains on disk | `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty |
| Cosmetic Change 2 (PEP 8 / ruff) | `ruff check scripts/session_self_initialization.py` clean | `ruff check scripts/session_self_initialization.py` |
| Test-fixture/assertion consistency (Change 6) | All 9 URL hits in test file match production constant; full suite passes | `grep -c "127.0.0.1:3000" tests/scripts/test_session_self_initialization.py` returns 0; `grep -c "localhost:3000" tests/scripts/test_session_self_initialization.py` returns 9; `pytest tests/scripts/test_session_self_initialization.py` |
| Project root boundary | All edited paths inside `E:\GT-KB` | manual verification, see §Project Root Boundary Compliance |

**Execution commands (planned for post-impl report):**
```bash
ruff check scripts/session_self_initialization.py
grep -c "127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py
grep -c "localhost:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py
pytest tests/scripts/test_session_self_initialization.py
pytest tests/scripts/test_session_self_initialization.py -k "dashboard_and_report or render_report or direct_script_execution"
python scripts/session_self_initialization.py --emit-report
head -5 docs/gtkb-dashboard/session-startup-report.md
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
  - `tests/scripts/test_session_self_initialization.py` (in-root, new in REVISED-2)
- All cited specifications are inside `E:\GT-KB`:
  - `.claude/rules/acting-prime-builder.md` (in-root)
  - `.claude/rules/codex-review-gate.md` (in-root)
  - `.claude/rules/file-bridge-protocol.md` (in-root)
  - `.claude/rules/project-root-boundary.md` (in-root)
  - `memory/work_list.md` (in-root)
  - `memory/MEMORY.md` (in-root)
  - All formal records (`DELIB-0840`, `GOV-SESSION-SELF-INITIALIZATION-001`, `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, `SPEC-PROJECT-DASHBOARD-KPI-LINK-001`, `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`) live in `groundtruth.db` at the project root.
- No external paths are touched, read, or referenced as live dependencies.

---

## Implementation Sequence (planned for after GO)

1. Verify the existing worktree edits are still present (`git diff scripts/session_self_initialization.py memory/MEMORY.md`).
2. Apply Change 6 to `tests/scripts/test_session_self_initialization.py` via `Edit` with `replace_all: true`, swapping `http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard` for `http://localhost:3000/d/gtkb/groundtruth-kb-dashboard` (9 occurrences).
3. Verify the literal replacement: `grep -c "127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py` returns 0; `grep -c "localhost:3000/d/gtkb/groundtruth-kb-dashboard" tests/scripts/test_session_self_initialization.py` returns 9.
4. Author Change 5 (`.gitignore` addition) via `Edit`.
5. Run `ruff check scripts/session_self_initialization.py` — expect clean.
6. Run `pytest tests/scripts/test_session_self_initialization.py` (full file) — expect all 55 tests pass.
7. Run `python scripts/session_self_initialization.py --emit-report` — expect a regenerated `docs/gtkb-dashboard/session-startup-report.md` with the new "Dashboard:" line and `localhost:3000` URL.
8. Verify `git status docs/gtkb-dashboard/bridge-swimlane.json` returns empty (now ignored).
9. Stage `scripts/session_self_initialization.py` + `memory/MEMORY.md` + `.gitignore` + `tests/scripts/test_session_self_initialization.py` (no other files).
10. Commit with scoped message referencing this bridge thread.
11. File post-impl report and add NEW entry to INDEX.md.

---

## Rollback Notes

If post-impl reveals an unexpected regression:
- Revert the single commit via `git revert <sha>` — covers 4 files (script + MEMORY.md + .gitignore + test file).
- Bridge thread itself is append-only audit history.

---

## Decision Needed From Owner

None for this REVISED-2 proposal. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
