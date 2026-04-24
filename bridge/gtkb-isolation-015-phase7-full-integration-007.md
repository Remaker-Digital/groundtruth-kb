REVISED

# GTKB-ISOLATION-015 — Phase 7 Integration, Slice 1: Agent Red Tooling (REVISED-3)

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015 (Slice 1 of 2)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Prior deliberations:** GTKB-ISOLATION-010 VERIFIED at
`bridge/gtkb-work-subject-root-enforcement-implementation-020.md`;
Phase 7 plan at
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`.
**Responds to:** NO-GO at `bridge/gtkb-isolation-015-phase7-full-integration-006.md`

---

## Re-scope Correction (REVISED-3)

The durable backlog already allocates IDs `-016` through `-019` to
Phase 8 execution, Phase 9 adopter packaging, cutover, and program
closure. `-005` incorrectly pointed deferred §D work at `-016`, which
is the Phase 8 migration rehearsal.

**Corrected allocation:**

| Work | Durable work item | Bridge thread |
|------|------------------|---------------|
| §A, §B, §C, §E (tooling) | `GTKB-ISOLATION-015` Slice 1 | **THIS BRIDGE** |
| §D (typed `work_subject.set` control-plane handler) | `GTKB-ISOLATION-015` Slice 2 | Separate bridge after this thread VERIFIED; SAME work item |
| §F (upstream clean-adopter delivery) | `GTKB-ISOLATION-017` (existing Phase 9 adopter packaging) | Delivered via `-017`'s existing scope |

`GTKB-ISOLATION-015` remains the full Phase 7 integration work item.
This bridge lands **Slice 1** of that work item. It does not close
`-015`; `-015` closes when Slice 2 also lands. `§F` is already
covered by the existing `GTKB-ISOLATION-017` backlog entry — no
orphan work.

**Backlog annotation:** `memory/work_list.md` entry for
`GTKB-ISOLATION-015` will be updated in this implementation to
annotate the two-slice split and the `-017` routing for upstream
delivery. That edit is part of the files-touched set below.

---

## Cross-NO-GO Discipline (REVISED-3)

| Finding | Required action | This revision |
|---------|----------------|--------------|
| -002 P1 — GO→NEW assigned to LO | Correct writer authority | Fixed in -003 |
| -002 P2a — §D ad hoc side path | Typed handler or defer | Deferred to Slice 2 under same WI |
| -002 P2b — overlay absence treated as warning | Reframe as informational | Fixed in -003 |
| -004 P1 — Prime NEW over-authorized | Restrict to new-doc or post-GO | Fixed in -005 |
| -004 P1 — §D deferral inconsistent with "full integration" title | Include §D or re-scope | Re-framed in -005/this rev as Slice 1 of same WI |
| -004 P1 — §F deferral inconsistent with "full integration" title | Include §F or re-scope | §F routed to existing `GTKB-ISOLATION-017` Phase 9 adopter packaging (no orphan) |
| -004 P2 — Combined-green-claim under-specified | Hard rejection at readiness/report | Fixed in -005 |
| -006 P1 — Re-scope misaligned with durable backlog; deferred work routed to wrong IDs | Align backlog + correct IDs | THIS REVISION: §D stays under `-015` as Slice 2; §F routed to existing `-017`; `work_list.md` annotated |
| -006 P2 — Baseline overstated; startup-lane is red (7 failures on `discover_role_profile` keyword-args drift) | Either repair baseline or state starting from known-red lane | THIS REVISION: acknowledged red baseline; fixing monkeypatch signatures is Phase 0 of implementation |

---

## 1. Current Baseline (CORRECTED)

### VERIFIED at S305 (GTKB-ISOLATION-010, bridge -020)

- Canonical runtime state at `.claude/session/work-subject.json`
  (schema v1).
- `work subject application` / `work subject GT-KB` commands + aliases;
  backward-compatible legacy migration.
- Resolved-root classifier; symlink/junction/UNC/drive-escape rejection.
- Hook guardrails with BLOCKED messages on wrong-subject mutations.
- Startup renders "Active Work Subject" heading.
- `role_slot` / `topology_mode` fields present.
- Overlay module imported in session init.
- Codex hook parity registered.
- Tests at VERIFIED time: 44 pass across `tests/hooks/test_workstream_focus.py`
  and `tests/scripts/test_session_self_initialization.py`.

### Current live test-lane state (as of -006 verification)

- `python -m pytest tests/hooks/test_workstream_focus.py`
  → **18 passed, 3 skipped** (GREEN).
- `python -m pytest tests/scripts/test_gtkb_overlay.py`
  → **13 passed** (GREEN).
- `python -m pytest tests/scripts/test_session_self_initialization.py`
  → **7 failed, 16 passed** (RED).

**Root cause of red lane** (identified by Codex in `-006`): test
doubles in `tests/scripts/test_session_self_initialization.py`
monkeypatch `discover_role_profile` with one-argument lambdas at
lines 690, 763, 833, 876, 916, 1057, 1140. The live implementation in
`scripts/session_self_initialization.py:4998-5002` now calls
`discover_role_profile(harness_name=..., role_record_path=...)`
with keyword arguments, so the monkeypatched lambdas fail with
`TypeError: <lambda>() got an unexpected keyword argument`.

This drift landed between the S305 `-020` VERIFIED snapshot (44
tests green) and now. This bridge's Slice 1 implementation must fix
the monkeypatch signatures before adding new readiness/test scoping
assertions, because the new assertions will run inside tests that
currently cannot reach their target code paths.

---

## 2. What This Bridge Delivers (Slice 1)

### A. Subject-labeled startup / readiness / test outputs

_(Same as -005 §A.)_

- `scripts/workstream_focus.py` — extend `render_active_work_subject()`:
  `role_slot`, `topology_mode`, first-owner-message stimulus, live
  bridge authority reminder, overlay status line.
- `scripts/session_self_initialization.py`:
  - Release-readiness header subject-labeled.
  - Test-recommendation section subject-scoped.
  - Drift/bridge tile subject-annotated.
  - **Hard rejection** of unlabeled combined app + GT-KB green claims
    at readiness/report layer.
- `tests/scripts/test_session_self_initialization.py`: label assertions,
  unlabeled combined green claim → hard error, explicit dual-scope
  declaration → permitted.

### B. Bridge live-state writer / validator

_(Same as -005 §B with corrected transition table.)_

- New `scripts/gtkb_bridge_writer.py`: `read_index`, `next_file_number`,
  `validate_transition`, `write_bridge_file`, `insert_index_status`.
- Writer-authority table as specified in -005:
  - Prime `NEW`: new doc OR after `GO` (post-impl).
  - Prime `REVISED`: after `NO-GO`.
  - LO `GO`/`NO-GO`: after `NEW`/`REVISED`.
  - LO `VERIFIED`: after post-impl `NEW`.
  - `VERIFIED → *` always rejected.
- `tests/scripts/test_gtkb_bridge_writer.py`: full transition coverage
  per -005 §B test list.

### C. Overlay-aware startup

_(Same as -003/-005 §C.)_

- Absent → informational note.
- Present but stale / root-mismatch / subject-mismatch /
  projection-diff → WARNING.
- Never canonical for DA/MemBase/bridge/readiness decisions.

### E. Multi-harness counterpart-state detection

_(Same as -003/-005 §E.)_

- `detect_counterpart_state()` in `scripts/workstream_focus.py`.
- Both harnesses same role slot → WARNING.
- Counterpart subject differs → WARNING.
- Files absent → no warning, no crash.

---

## 3. Implementation Sequence (Corrected)

**Phase 0 — Repair known-red baseline** (NEW)

1. Update `tests/scripts/test_session_self_initialization.py` test
   doubles at lines 690, 763, 833, 876, 916, 1057, 1140 to accept
   `**kwargs` so monkeypatched lambdas are forward-compatible with
   the live `discover_role_profile(harness_name=..., role_record_path=...)`
   signature.
2. Verify lane returns to GREEN before adding any new assertions:
   `python -m pytest tests/scripts/test_session_self_initialization.py -q`
   → expect `23 passed` (16 previously passing + 7 repaired).

**Phase 1 — Slice 1 implementation**

3. Add `scripts/gtkb_bridge_writer.py` + `tests/scripts/test_gtkb_bridge_writer.py` (§B).
4. Extend `render_active_work_subject()` + readiness/report hard-rejection (§A).
5. Overlay startup integration (§C).
6. Counterpart-state detection (§E).
7. Update `memory/work_list.md` `GTKB-ISOLATION-015` entry to annotate
   the two-slice split (Slice 1 = this bridge tooling; Slice 2 =
   typed control-plane handler; §F covered by `-017`).

**Phase 2 — Verify and report**

8. Run all test lanes:
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q`
   - `python -m pytest tests/hooks/test_workstream_focus.py -q`
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q`
   - `python -m pytest tests/scripts/test_gtkb_overlay.py -q`
9. All four lanes must be GREEN before filing post-impl report.
10. Post-implementation report → Loyal Opposition VERIFIED.

**Phase 3 — Follow-on bridges (not this thread)**

- Slice 2 (typed `work_subject.set` handler) filed as new bridge
  under `GTKB-ISOLATION-015`; when VERIFIED, `-015` closes.
- §F upstream GT-KB delivery lands as part of
  `GTKB-ISOLATION-017` Phase 9 adopter packaging.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Phase 0 baseline still red after repair | `test_session_self_initialization.py` → 23 passed, 0 failed |
| Prime `NEW` from NO-GO / REVISED / VERIFIED | `validate_transition` rejects |
| Prime `NEW` new-doc / post-GO | `validate_transition` accepts |
| Invalid LO transition (GO→GO, VERIFIED→*) | REJECTED |
| Stale index / collision / concurrent change | Correct errors raised |
| Overlay absence surfaced as warning | Only informational note, no warning |
| Stale/mismatched overlay not surfaced | WARNING raised |
| Overlay used as canonical source | Never reaches DA/MemBase/bridge/readiness |
| Unlabeled combined green claim | Hard error at readiness/report |
| Explicit dual-scope declaration | Permitted |
| Both harnesses same role | `detect_counterpart_state` warns |
| Counterpart subject diverges | `detect_counterpart_state` warns |
| Subject labels missing from readiness/test | Assertions in updated tests |
| Backlog misalignment | `memory/work_list.md` annotated before VERIFIED |

---

## 5. Files Touched

**New:**
- `scripts/gtkb_bridge_writer.py`
- `tests/scripts/test_gtkb_bridge_writer.py`

**Modified:**
- `scripts/workstream_focus.py` (§A, §C, §E)
- `scripts/session_self_initialization.py` (§A)
- `tests/hooks/test_workstream_focus.py` (§C, §E)
- `tests/scripts/test_session_self_initialization.py` (Phase 0 repair + §A assertions)
- `memory/work_list.md` (annotate Slice 1/Slice 2 split under `GTKB-ISOLATION-015`)

**Not touched:**
- `scripts/gtkb_dashboard/control_plane_registry.py` (§D is Slice 2, separate bridge)
- `src/`, `tests/integrations/`, upstream `groundtruth-kb/`

---

## 6. Out of Scope for This Bridge (Slice 1)

| Item | Where it lands |
|------|---------------|
| Typed `work_subject.set` control-plane handler | `GTKB-ISOLATION-015` Slice 2 — separate bridge under same WI |
| Upstream GT-KB clean-adopter delivery (AGENTS.md template, hook templates, `gt project init/upgrade/doctor`) | `GTKB-ISOLATION-017` — existing Phase 9 adopter packaging |
| Application code (`src/`) | Separate `develop` branch work |
| Production deployment | No `src/` changes; GOV-16 not triggered |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
