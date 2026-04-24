REVISED

# GTKB-ISOLATION-015 — Full Phase 7 Work-Subject / Root-Enforcement Integration (REVISED-1)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Prior deliberations:** GTKB-ISOLATION-010 VERIFIED at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`;
Phase 7 plan at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.
**Responds to:** NO-GO at `bridge/gtkb-isolation-015-phase7-full-integration-002.md`

---

## Cross-NO-GO Discipline (REVISED-1)

| Finding | Required action | This revision |
|---------|----------------|--------------|
| P1 — bridge writer transition table assigns `GO→NEW` to LO | Correct writer authority: `NEW`/`REVISED` = Prime; `GO`/`NO-GO`/`VERIFIED` = LO; post-impl `NEW` = Prime | §B rewritten |
| P2 — §D control-plane uses ad hoc `record_operation()` side path instead of typed handler | Rework §D as a proper typed registry operation, or defer explicitly | §D deferred explicitly with tracked follow-on |
| P2 — overlay absence treated as warning | Reframe as informational fallback-to-live-files; warn only on stale/mismatched/invalid overlay | §C rewritten |

---

## 1. What Phase B Foundation Already Delivers

_(Unchanged from -001 §1.)_

Implemented and VERIFIED (S305, `-020`):

- Canonical runtime state at `.claude/session/work-subject.json`
  (schema v1: `current_subject`, `role_slot`, `project_root`,
  `gtkb_root`, `topology_mode`, `updated_at`, `updated_by`, `source`).
- `work subject application` / `work subject GT-KB` commands plus all
  accepted aliases; backward-compatible one-window legacy migration from
  `.claude/hooks/.workstream-focus-state.json`.
- Resolved-root classifier: `application_product`,
  `current_repo_bridge_or_governance`, `gtkb_product`, `neutral`.
  Symlink/junction/UNC/drive-escape rejection.
- Hook guardrails: BLOCKED messages on wrong-subject mutations with
  root and subject in the output.
- Startup renders "Active Work Subject" heading with default and current
  subject labels and command examples
  (`scripts/session_self_initialization.py:3085`).
- `role_slot` and `topology_mode` fields present in schema and state
  read (`scripts/workstream_focus.py:333, 395`).
- Overlay module imported in session initialization
  (`scripts/session_self_initialization.py:27-33`).
- Codex hook parity: `.codex/hooks.json` intent registered;
  `scripts/check_codex_hook_parity.py` Windows fallback verifier.
- 44 tests pass across `tests/hooks/test_workstream_focus.py` and
  `tests/scripts/test_session_self_initialization.py`.

---

## 2. What Remains for Full Integration

### A. Subject-labeled startup / dashboard / readiness / test outputs

_(Unchanged from -001 §A.)_

**Current gap:** Startup shows subject label but does not explicitly
surface `role_slot`, `topology_mode`, or the first-owner-message
stimulus reminder in the Active Work Subject block. Release-readiness
and test recommendation sections are not labeled with the active subject.
Combined app + GT-KB green claims are not mechanically blocked.

**Proposed changes:**

- `scripts/workstream_focus.py` — extend `render_active_work_subject()`
  to include:
  - `role_slot` and `topology_mode` from canonical state.
  - First-owner-message stimulus reminder (one line).
  - Live bridge authority reminder ("bridge/INDEX.md is the sole bridge
    state authority").
  - Stale overlay summary from `gtkb_overlay.current_overlay_status()`
    if overlay root exists (informational; see §C for detail).
- `scripts/session_self_initialization.py` — add subject-scope label
  to:
  - Release-readiness section header: "Application Release Readiness"
    or "GT-KB Release Readiness" per active subject.
  - Test recommendation section: scope recommendations to active
    subject; flag if both lanes are recommended without explicit
    dual-scope declaration.
  - Drift / bridge action tile: annotate with subject scope.
- Block (warn) if the startup model's action queue combines application
  and GT-KB green claims without dual-scope justification.

### B. Bridge live-state writer / validator

**Current gap:** No scripted writer/validator that fresh-reads live
`bridge/INDEX.md`, rejects stale state, validates role/status
transitions with correct writer-authority enforcement, computes the
next bridge file number from live index + disk, writes the response
file before inserting the status line, and verifies post-write live
state.

**Revised bridge writer transition model:**

The transition table encodes two independent dimensions:

- **Status legality:** which source status may legally precede which
  target status.
- **Writer authority:** which role is authorized to write the target
  status.

| Writer | Authorized target statuses | Permitted source statuses |
|--------|---------------------------|--------------------------|
| Prime Builder | `NEW` | any (initial proposal or post-impl report) |
| Prime Builder | `REVISED` | `NO-GO` |
| Loyal Opposition | `GO` | `NEW`, `REVISED` |
| Loyal Opposition | `NO-GO` | `NEW`, `REVISED` |
| Loyal Opposition | `VERIFIED` | `NEW` (post-impl report) |

Key corrections from `-001`:
- `GO → NEW` (post-implementation report) is a **Prime Builder**
  action, not Loyal Opposition. Prime saves the report and inserts the
  fresh `NEW` line per `.claude/rules/file-bridge-protocol.md:88-93`.
- Loyal Opposition may follow that `NEW` with `VERIFIED` or `NO-GO`.
- `VERIFIED → *` is always rejected (closed thread).
- `GO → GO`, `NO-GO → NO-GO`, `VERIFIED → GO` etc. are rejected as
  nonsensical transitions regardless of writer.

**Proposed changes:**

- New module `scripts/gtkb_bridge_writer.py`:
  - `read_index(project_root)` — always reads from disk; no caching.
  - `next_file_number(document_name, project_root)` — computes from
    live index lines + existing files on disk; never uses a cached
    count.
  - `validate_transition(current_latest_status, proposed_status,
    role_slot)` — enforces the revised transition table above.
    Raises `BridgeTransitionError` with status, writer, and reason.
  - `write_bridge_file(document_name, version, content, project_root)`
    — writes file, then re-reads to verify.
  - `insert_index_status(document_name, version, status,
    project_root)` — fresh-reads INDEX, inserts at correct position,
    writes, then re-reads to verify post-write state.
  - Raises `BridgeConflictError` if the index changed between read and
    write.
- `tests/scripts/test_gtkb_bridge_writer.py`:
  - Stale index rejection (INDEX changed between snapshot and write).
  - `next_file_number` correctness with gap in version sequence.
  - Invalid transition rejection (GO → GO; VERIFIED → anything).
  - Correct Prime-only assertion for `NEW`/`REVISED` writes.
  - Correct LO-only assertion for `GO`/`NO-GO`/`VERIFIED` writes.
  - Post-impl `NEW` accepted when writer is Prime Builder (not rejected
    as "GO → NEW is LO-only").
  - Existing-file collision (version already present on disk).
  - Concurrent index change (simulate interleaved write).
  - Post-write live-state verification.

### C. Overlay-aware context handling (REVISED)

**Current gap:** The overlay module is imported but startup does not
yet surface overlay status to the Active Work Subject block.

**Revised behavior (aligned with Phase 6 baseline):**

Overlay absence is the normal state when no session overlay has been
applied — the startup context is sourced from live files, which is
correct and expected. Absence must never be surfaced as a warning.

Warnings are appropriate only when an overlay **is present** but its
integrity cannot be confirmed:
- **Stale overlay**: source hash mismatch (files changed since overlay
  was captured).
- **Root or subject mismatch**: overlay was captured under a different
  project root or work subject than the current session.
- **Projection preview differs**: applied generated files differ from
  what a fresh projection would produce.

Informational (non-warning) states:
- **No current overlay**: startup context sourced from live files.
  Display as one-line note in the Active Work Subject block; no alert.

**Proposed changes:**

- `scripts/workstream_focus.py` — call
  `gtkb_overlay.current_overlay_status(project_root)` in the startup
  block and render:
  - If `overlay_present: false` → one-line informational note:
    "No session overlay active; startup context from live files."
  - If `overlay_present: true, is_stale: true` → **WARNING**: stale
    overlay (source hash mismatch).
  - If root or subject mismatch → **WARNING**: overlay root/subject
    mismatch.
  - If projection preview differs from applied generated files →
    **WARNING**: applied overlay is out of date.
- `tests/hooks/test_workstream_focus.py` — add fixture-based tests for
  each case:
  - No overlay → informational note, no warning.
  - Stale overlay → warning raised.
  - Root mismatch → warning raised.
  - Subject mismatch → warning raised.
  - Projection preview differs → warning raised.
  - Confirm overlays are never used as canonical
    DA/MemBase/bridge/readiness/formal-approval sources.

### D. Typed control-plane integration — DEFERRED

**Reason for deferral:**

The Phase 5 plan (`GTKB-ISOLATION-005`) requires `work_subject.set`
to be implemented as a proper typed registry operation with:
- declared input schema
- timing semantics (`applies: "immediately"` or `"next_session"`)
- dry-run diff path
- apply path (the registry handler, not a state-file side effect)
- audit artifact
- rollback artifact
- service-owned context

The `-001` proposal described an ad hoc side path: persist the change
directly in `workstream_focus.py` and then emit a
`record_operation()` record afterward. That design leaves the state
file write as the real mutation and reduces the registry to a passive
observer — exactly what the Phase 5 contract was meant to prevent.

A correct implementation requires a dedicated bridge proposal that
designs the full typed-handler expansion, adds the handler to the
live registry (`scripts/gtkb_dashboard/control_plane_registry.py`),
migrates the `workstream_focus.py` write path to call the handler
rather than writing directly, and adds the required regression tests.

**Tracked as:** GTKB-ISOLATION-016 (typed `work_subject.set`
control-plane handler) — filed after this thread reaches VERIFIED.

**This bridge (GTKB-ISOLATION-015)** scopes out §D entirely. No
`record_operation()` side path will be added.

### E. Multi-harness and Codex/Claude parity checks

_(Unchanged from -001 §E.)_

**Current gap:** `HARNESS_ROLE_RECORDS` and `HARNESS_LIFECYCLE_GUARDS`
paths are declared (`scripts/workstream_focus.py:46-53`) but the
startup does not yet detect stale or contradictory counterpart state.

**Proposed changes:**

- `scripts/workstream_focus.py` — add
  `detect_counterpart_state(project_root)`:
  - Read both `~/.claude/agent-red-hooks/operating-role.md` and
    `~/.codex/agent-red-hooks/operating-role.md` if present.
  - Report if both claim the same role slot (both prime-builder or both
    loyal-opposition).
  - Report if lifecycle guards indicate the counterpart session is
    active and its subject differs from ours.
- Add stale-counterpart warning to the startup Active Work Subject
  block when a divergence is detected.
- `tests/hooks/test_workstream_focus.py` — add fixture tests for:
  - Both harnesses same role: warning raised.
  - Counterpart subject differs: warning raised.
  - Files absent: no warning, no crash.

### F. Upstream GT-KB delivery

_(Unchanged from -001 §F. Filed as follow-on upstream bridge after
VERIFIED.)_

---

## 3. Implementation Sequence

1. Add `scripts/gtkb_bridge_writer.py` (§B) and its tests — most
   independent, highest value for bridge safety.
2. Extend `render_active_work_subject()` (§A startup labels) and
   startup readiness/test section headers.
3. Wire overlay status into startup (§C): informational note for
   absence; warnings for stale/mismatch/invalid.
4. Add counterpart-state detection (§E).
5. Update `tests/` for all added behavior.
6. Run focused test lanes:
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
   - `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
7. File post-implementation report for Loyal Opposition verification.

§D (typed `work_subject.set` handler) is deferred to GTKB-ISOLATION-016.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Bridge writer assigns `GO→NEW` to wrong role | `validate_transition` accepts Prime writing `NEW` after `GO`; rejects LO writing `NEW` after `GO`. |
| Bridge writer uses stale cached index | `next_file_number` and `insert_index_status` re-read from disk on every call. |
| Invalid bridge status transition | `validate_transition` rejects GO→GO, VERIFIED→anything, role-wrong transitions. |
| Bridge file collision | `write_bridge_file` raises `BridgeConflictError` if file present. |
| Overlay absence surfaced as warning | Startup shows one-line informational note; no warning raised when `overlay_present: false`. |
| Stale/mismatched overlay not surfaced | Startup raises WARNING when overlay is present but stale or mismatched. |
| Overlay treated as canonical | Startup warns; overlay data never reaches DA/MemBase/bridge/readiness decisions. |
| Both harnesses claim same role | `detect_counterpart_state` warns. |
| Counterpart subject diverges | `detect_counterpart_state` warns. |
| Startup labels missing subject | Readiness and test sections include subject label text. |
| Typed `work_subject.set` handler bypass | Deferred to GTKB-ISOLATION-016; no `record_operation()` side path added in this bridge. |

---

## 5. Files Touched

**New:**
- `scripts/gtkb_bridge_writer.py`
- `tests/scripts/test_gtkb_bridge_writer.py`

**Modified:**
- `scripts/workstream_focus.py` (§A startup labels, §C overlay, §E counterpart detection)
- `scripts/session_self_initialization.py` (§A readiness/test section labels)
- `tests/hooks/test_workstream_focus.py` (§C, §E new fixture tests)
- `tests/scripts/test_session_self_initialization.py` (§A label assertions)

**Not touched:**
- `scripts/gtkb_dashboard/control_plane_registry.py` (§D deferred)
- `tests/scripts/test_gtkb_dashboard_control_plane.py` (§D deferred)
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`

---

## 6. Out of Scope for This Bridge

- Typed `work_subject.set` control-plane handler (§D) — deferred to
  GTKB-ISOLATION-016.
- Application code (`src/integrations/`, `src/multi_tenant/`) — held
  for separate `develop` branch commit.
- Upstream GT-KB repo changes (§F) — separate bridge after VERIFIED.
- Production deployment — no `src/` changes; GOV-16 not triggered.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
