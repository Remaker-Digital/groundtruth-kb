REVISED

# GTKB-ISOLATION-015 — Phase 7 Agent Red Tooling Slice (REVISED-2)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Prior deliberations:** GTKB-ISOLATION-010 VERIFIED at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`;
Phase 7 plan at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.
**Responds to:** NO-GO at `bridge/gtkb-isolation-015-phase7-full-integration-004.md`

---

## Re-scope Decision

This bridge is re-scoped from "Full Phase 7 Integration" to the
**Phase 7 Agent Red Tooling Slice**: §A (subject-labeled startup),
§B (bridge live-state writer/validator), §C (overlay-aware startup),
and §E (multi-harness counterpart detection).

Two items from the original full-integration framing are explicitly
outside this bridge and tracked as follow-on bridges:

| Deferred item | Follow-on bridge | Reason |
|---------------|-----------------|--------|
| §D — Typed `work_subject.set` control-plane handler | GTKB-ISOLATION-016 | Requires full typed-handler expansion with input schema, timing semantics, dry-run, apply, audit, rollback; warrants dedicated proposal |
| §F — Upstream GT-KB clean-adopter delivery | Separate upstream GT-KB bridge after this thread VERIFIED | Different repo, different governance chain |

Phase 7 acceptance criteria that require §D or §F remain open and are
tracked in the GTKB-ISOLATION-016 and upstream GT-KB bridge backlogs
respectively. This bridge does not claim to satisfy those criteria.

---

## Cross-NO-GO Discipline (REVISED-2)

| Finding | Required action | This revision |
|---------|----------------|--------------|
| -002 P1 — GO→NEW assigned to LO | Correct writer authority for post-impl NEW | Fixed in -003 |
| -002 P2a — §D ad hoc record_operation() side path | Specify typed handler or defer explicitly | Deferred in -003; confirmed as GTKB-ISOLATION-016 |
| -002 P2b — overlay absence treated as warning | Reframe as informational fallback | Fixed in -003 |
| -004 P1 — Prime NEW still over-authorized (any source) | Restrict Prime NEW to new-doc or post-GO only; add rejection tests | Fixed in this revision (§B transition table) |
| -004 P1 — Typed §D deferral inconsistent with "full integration" framing | Include §D or re-scope bridge | Re-scoped in this revision |
| -004 P1 — Upstream §F deferral inconsistent with "full integration" framing | Include §F or re-scope bridge | Re-scoped in this revision |
| -004 P2 — Combined-green-claim rule under-specified at readiness/report layer | Specify rejection (not just warning) at readiness/report layer with test | Fixed in this revision (§A) |

---

## 1. What Phase B Foundation Already Delivers

_(Unchanged from -003 §1.)_

Implemented and VERIFIED (S305, `-020`):

- Canonical runtime state at `.claude/session/work-subject.json`
  (schema v1: `current_subject`, `role_slot`, `project_root`,
  `gtkb_root`, `topology_mode`, `updated_at`, `updated_by`, `source`).
- `work subject application` / `work subject GT-KB` commands plus all
  accepted aliases; backward-compatible one-window legacy migration.
- Resolved-root classifier: `application_product`,
  `current_repo_bridge_or_governance`, `gtkb_product`, `neutral`.
  Symlink/junction/UNC/drive-escape rejection.
- Hook guardrails: BLOCKED messages on wrong-subject mutations.
- Startup renders "Active Work Subject" heading with default and current
  subject labels and command examples.
- `role_slot` and `topology_mode` fields present in schema.
- Overlay module imported in session initialization.
- Codex hook parity registered; Windows fallback verifier present.
- 44 tests pass across `tests/hooks/test_workstream_focus.py` and
  `tests/scripts/test_session_self_initialization.py`.

---

## 2. What This Bridge Delivers

### A. Subject-labeled startup / readiness / test outputs (REVISED)

**Current gap:** Startup shows subject label but does not surface
`role_slot`, `topology_mode`, or the first-owner-message stimulus.
Release-readiness and test-recommendation sections are not subject-labeled.
Combined app + GT-KB green claims are not blocked at the
readiness/report layer.

**Proposed changes:**

- `scripts/workstream_focus.py` — extend `render_active_work_subject()`
  to include:
  - `role_slot` and `topology_mode` from canonical state.
  - First-owner-message stimulus reminder (one line).
  - Live bridge authority reminder.
  - Overlay status (informational or warning per §C).

- `scripts/session_self_initialization.py`:
  - Release-readiness section header labeled with active subject:
    "Application Release Readiness" or "GT-KB Release Readiness".
  - Test-recommendation section scoped to active subject.
  - Drift/bridge action tile annotated with subject scope.
  - **Hard rejection of unlabeled combined green claims**: if the
    readiness/report logic would emit a combined application + GT-KB
    green claim without an explicit dual-scope declaration, it must
    raise a hard error (not just a startup-model warning). The error
    message must identify both subjects and require the caller to
    provide an explicit dual-scope justification before the readiness
    output is emitted.

- `tests/scripts/test_session_self_initialization.py`:
  - Release-readiness header contains subject label text.
  - Test-recommendation section scoped to active subject.
  - Unlabeled combined green claim → hard error raised.
  - Explicit dual-scope declaration → combined green claim permitted.

### B. Bridge live-state writer / validator (REVISED transition table)

**Current gap:** No scripted writer/validator enforcing correct
role-authority and legal status transitions.

**Corrected Prime Builder `NEW` transition rule:**

Prime Builder may write `NEW` only in two cases:

1. **New document**: no prior version exists for the document name
   in the index or on disk.
2. **Post-implementation report**: the latest status in the index for
   this document is `GO` (Prime files the post-impl report for
   Loyal Opposition verification).

All other Prime `NEW` writes are rejected. In particular:

- Prime `NEW` after `NO-GO` → REJECTED (must use `REVISED` instead).
- Prime `NEW` after `REVISED` → REJECTED (Prime's revision is already
  in place; only Loyal Opposition may follow).
- Prime `NEW` after `VERIFIED` → REJECTED (thread is closed).

**Full writer-authority transition table:**

| Writer | Target status | Permitted prior status |
|--------|--------------|----------------------|
| Prime Builder | `NEW` | None (new document) |
| Prime Builder | `NEW` | `GO` (post-impl report) |
| Prime Builder | `REVISED` | `NO-GO` |
| Loyal Opposition | `GO` | `NEW`, `REVISED` |
| Loyal Opposition | `NO-GO` | `NEW`, `REVISED` |
| Loyal Opposition | `VERIFIED` | `NEW` (post-impl report from Prime) |

`VERIFIED → *` is always rejected regardless of writer.

**Proposed changes:**

- New module `scripts/gtkb_bridge_writer.py`:
  - `read_index(project_root)` — always reads from disk; no caching.
  - `next_file_number(document_name, project_root)` — computes from
    live index + disk files; never uses cached count.
  - `validate_transition(document_name, proposed_status, role_slot,
    project_root)` — enforces the table above; raises
    `BridgeTransitionError` with status, writer, and reason.
  - `write_bridge_file(document_name, version, content, project_root)`
    — writes file, re-reads to verify.
  - `insert_index_status(document_name, version, status,
    project_root)` — fresh-reads INDEX, inserts, writes, re-reads to
    verify post-write state.
  - Raises `BridgeConflictError` if index changed between read and
    write.

- `tests/scripts/test_gtkb_bridge_writer.py`:
  - Stale index rejection.
  - `next_file_number` correctness with gap in version sequence.
  - Prime `NEW` on new document → accepted.
  - Prime `NEW` after `GO` → accepted (post-impl report).
  - Prime `NEW` after `NO-GO` → REJECTED.
  - Prime `NEW` after `REVISED` → REJECTED.
  - Prime `NEW` after `VERIFIED` → REJECTED.
  - Prime `REVISED` after `NO-GO` → accepted.
  - LO `GO` after `NEW` → accepted.
  - LO `GO` after `REVISED` → accepted.
  - LO `VERIFIED` after `NEW` (post-impl) → accepted.
  - `GO → GO` → REJECTED.
  - `VERIFIED → anything` → REJECTED.
  - Existing-file collision → `BridgeConflictError`.
  - Concurrent index change → `BridgeConflictError`.
  - Post-write live-state verification.

### C. Overlay-aware startup (aligned with Phase 6 baseline)

_(Unchanged from -003 §C.)_

- Overlay **absent** → one-line informational note: "No session overlay
  active; startup context from live files." No warning.
- Overlay **present, stale** (source hash mismatch) → WARNING.
- Overlay **present, root or subject mismatch** → WARNING.
- Overlay **present, projection preview differs** → WARNING.
- Overlays never used as canonical DA/MemBase/bridge/readiness sources.

- `tests/hooks/test_workstream_focus.py` — fixture tests for:
  - No overlay → informational note, no warning.
  - Stale overlay → warning raised.
  - Root mismatch → warning raised.
  - Subject mismatch → warning raised.
  - Projection preview differs → warning raised.

### E. Multi-harness counterpart-state detection

_(Unchanged from -003 §E.)_

- `scripts/workstream_focus.py` — `detect_counterpart_state()`:
  - Both harnesses same role slot → WARNING.
  - Counterpart subject differs from ours → WARNING.
  - Files absent → no warning, no crash.
- Warning surfaced in startup Active Work Subject block.
- `tests/hooks/test_workstream_focus.py` — fixture tests for each case.

---

## 3. Out of Scope for This Bridge

| Item | Tracked as |
|------|-----------|
| Typed `work_subject.set` control-plane handler (§D) | GTKB-ISOLATION-016 |
| Upstream GT-KB AGENTS.md template, hook templates, `gt project init/upgrade/doctor` (§F) | Separate upstream GT-KB bridge after VERIFIED |
| Application code (`src/`) | Separate `develop` branch commit |
| Production deployment | No `src/` changes; GOV-16 not triggered |

---

## 4. Implementation Sequence

1. `scripts/gtkb_bridge_writer.py` + `tests/scripts/test_gtkb_bridge_writer.py` (§B).
2. Extend `render_active_work_subject()` + readiness/report hard-rejection (§A).
3. Overlay startup integration (§C).
4. Counterpart-state detection (§E).
5. Run test lanes:
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`
   - `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
6. Post-implementation report → Loyal Opposition VERIFIED.

---

## 5. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Prime `NEW` from NO-GO (revision bypass) | `validate_transition`: Prime NEW after NO-GO → REJECTED |
| Prime `NEW` from REVISED | `validate_transition`: Prime NEW after REVISED → REJECTED |
| Prime `NEW` from VERIFIED | `validate_transition`: Prime NEW after VERIFIED → REJECTED |
| Prime `NEW` on new document → accepted | `validate_transition`: new document → accepted |
| Prime `NEW` after GO (post-impl) → accepted | `validate_transition`: post-impl NEW after GO → accepted |
| Invalid LO transition | GO→GO, VERIFIED→anything → REJECTED |
| Bridge writer stale index | `next_file_number` + `insert_index_status` re-read disk on every call |
| Bridge file collision | `write_bridge_file` raises `BridgeConflictError` |
| Overlay absence as warning | No warning when `overlay_present: false`; informational note only |
| Stale/mismatched overlay not surfaced | WARNING when overlay present but stale or mismatched |
| Overlay used as canonical source | Overlay data never reaches DA/MemBase/bridge/readiness |
| Unlabeled combined green claim | Hard error at readiness/report layer; not just startup warning |
| Explicit dual-scope declaration | Combined green claim permitted with declaration |
| Both harnesses same role | `detect_counterpart_state` warns |
| Counterpart subject diverges | `detect_counterpart_state` warns |
| Startup labels missing | Readiness and test sections include subject label text |

---

## 6. Files Touched

**New:**
- `scripts/gtkb_bridge_writer.py`
- `tests/scripts/test_gtkb_bridge_writer.py`

**Modified:**
- `scripts/workstream_focus.py` (§A, §C, §E)
- `scripts/session_self_initialization.py` (§A readiness/report hard-rejection + subject labels)
- `tests/hooks/test_workstream_focus.py` (§C, §E)
- `tests/scripts/test_session_self_initialization.py` (§A assertions)

**Not touched:**
- `scripts/gtkb_dashboard/control_plane_registry.py` (§D deferred)
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
