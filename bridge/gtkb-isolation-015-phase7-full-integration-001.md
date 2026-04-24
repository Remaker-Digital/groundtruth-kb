NEW

# GTKB-ISOLATION-015 — Full Phase 7 Work-Subject / Root-Enforcement Integration

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Prior deliberations:** GTKB-ISOLATION-010 VERIFIED at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`;
Phase 7 plan at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.

---

## 1. What Phase B Foundation Already Delivers

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
    if overlay root exists.
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

**Current gap:** The plan requires a scripted writer/validator that
fresh-reads live `bridge/INDEX.md`, rejects cached or stale bridge
state, validates role/status transitions, computes the next bridge file
number from live index + disk, writes the response file before inserting
the status line, and verifies post-write live state. No such module
exists yet.

**Proposed changes:**

- New module `scripts/gtkb_bridge_writer.py`:
  - `read_index(project_root)` — always reads from disk; no caching.
  - `next_file_number(document_name, project_root)` — computes from
    live index lines + existing files on disk; never uses a cached
    count.
  - `validate_transition(current_latest_status, proposed_status,
    role_slot)` — enforces the legal transition table:
    - Prime (prime-builder): NEW → (Codex reviews); REVISED →
      (Codex reviews).
    - Codex (loyal-opposition): NEW → GO/NO-GO; REVISED → GO/NO-GO;
      GO → NEW (post-impl); VERIFIED closes the thread.
    - Rejects e.g. GO → GO, VERIFIED → GO.
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
  - Existing-file collision (version already present on disk).
  - Concurrent index change (simulate interleaved write).
  - Post-write live-state verification.

### C. Overlay-aware context handling

**Current gap:** The overlay module is imported but startup does not
yet warn when the current overlay is stale, has a root/subject
mismatch, or when a projection preview differs from applied generated
files.

**Proposed changes:**

- `scripts/workstream_focus.py` — call
  `gtkb_overlay.current_overlay_status(project_root)` in the startup
  block; render warnings for:
  - Missing overlay.
  - Stale overlay (source hash mismatch).
  - Root or subject mismatch.
  - Projection preview differs from applied generated files.
- `tests/hooks/test_workstream_focus.py` — add fixture-based tests for
  each warning condition; confirm overlays are never used as canonical
  DA/MemBase/bridge/readiness/formal-approval sources.

### D. Typed control-plane integration

**Current gap:** Subject changes are persisted directly to
`.claude/session/work-subject.json` without going through the Phase 5
typed operation registry (`scripts/gtkb_dashboard/control_plane_registry.py`).

**Proposed changes:**

- `scripts/workstream_focus.py` — when persisting a standalone subject
  change, also emit a `work_subject.set` operation record through
  `control_plane_registry.record_operation()` with:
  - `target_root`, `subject`, `harness_id`, `role_slot`, `topology`,
    `applies`: `"immediately"` or `"next_session"`.
  - Dry-run diff: previous vs new subject.
  - Audit entry.
- `scripts/gtkb_dashboard/control_plane_registry.py` — if
  `work_subject.set` operation is not already registered, add it with
  correct applies-immediately semantics and allowlist.
- `tests/scripts/test_gtkb_dashboard_control_plane.py` — add test:
  subject change produces a well-formed registry operation record;
  arbitrary path inputs outside the allowlist are rejected.

### E. Multi-harness and Codex/Claude parity checks (beyond Phase B)

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

### F. Upstream GT-KB delivery (separate repo, tracked here as scope)

**Proposed scope for `groundtruth-kb` upstream (NOT implemented in
this Agent Red bridge — filed as a follow-on upstream bridge):**

- `AGENTS.md` template: add `active_role`, `work_subject`, and
  `topology_mode` fields.
- Claude / Codex hook templates: update `workstream-focus.py` template
  to Phase 7 schema v1.
- `gt project init` default: new projects default to `application`
  subject; `work-subject.json` initialized with defaults.
- `gt project upgrade`: preserve valid local subject state; warn if
  schema version mismatch.
- `gt project doctor`: check for missing, invalid, stale, or
  root-mismatched subject state.
- Clean-adopter fixture tests: prove default application subject,
  functioning app-local governance, isolated bridge/readiness/test
  labeling.

This item is noted here for scope completeness; implementation requires
a separate upstream GT-KB bridge proposal after this Agent Red bridge
is VERIFIED.

---

## 3. Implementation Sequence

1. Add `scripts/gtkb_bridge_writer.py` (§B) and its tests — most
   independent, highest value for bridge safety.
2. Extend `render_active_work_subject()` (§A startup labels) and
   startup readiness/test section headers.
3. Wire overlay status into startup warnings (§C).
4. Add control-plane `work_subject.set` operation record (§D).
5. Add counterpart-state detection (§E).
6. Update `tests/` for all added behavior.
7. Run focused test lanes:
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
   - `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
   - `python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q --tb=short`
8. File post-implementation report for Loyal Opposition verification.

Upstream GT-KB work (§F) is filed as a follow-on bridge after VERIFIED.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Startup combines app + GT-KB green claims | Startup warns when dual-scope is implicit. |
| Bridge writer uses stale cached index | `next_file_number` and `insert_index_status` re-read from disk on every call. |
| Invalid bridge status transition | `validate_transition` rejects GO→GO, VERIFIED→anything, role-wrong transitions. |
| Bridge file collision (number already exists) | `write_bridge_file` raises `BridgeConflictError` if file present. |
| Overlay treated as canonical | Startup warns; overlay data never reaches DA/MemBase/bridge/readiness decisions. |
| Subject change bypasses registry | `work_subject.set` operation record always created on standalone command. |
| Both harnesses claim same role slot | `detect_counterpart_state` warns. |
| Counterpart subject diverges | `detect_counterpart_state` warns. |
| Startup labels missing subject | Readiness and test sections include subject label text. |
| Upstream clean adopters miss behavior | Tracked as §F follow-on; remains visible in backlog until upstream bridge VERIFIED. |

---

## 5. Files Touched

**New:**
- `scripts/gtkb_bridge_writer.py`
- `tests/scripts/test_gtkb_bridge_writer.py`

**Modified:**
- `scripts/workstream_focus.py` (§A startup labels, §C overlay, §D control-plane record, §E counterpart detection)
- `scripts/session_self_initialization.py` (§A readiness/test section labels)
- `scripts/gtkb_dashboard/control_plane_registry.py` (§D `work_subject.set` operation)
- `tests/hooks/test_workstream_focus.py` (§C, §E new fixture tests)
- `tests/scripts/test_session_self_initialization.py` (§A label assertions)
- `tests/scripts/test_gtkb_dashboard_control_plane.py` (§D operation record test)

**Not touched:** `src/`, `tests/integrations/`, upstream `groundtruth-kb/`.

---

## 6. Out of Scope for This Bridge

- Application code (`src/integrations/`, `src/multi_tenant/`) — held
  for separate `develop` branch commit.
- Upstream GT-KB repo changes (§F) — separate bridge after VERIFIED.
- Production deployment — no `src/` changes; GOV-16 not triggered.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
