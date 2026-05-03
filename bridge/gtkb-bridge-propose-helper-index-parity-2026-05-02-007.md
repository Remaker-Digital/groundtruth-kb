NEW

# Closure Proposal — index-parity thread superseded by gtkb_bridge_writer.py

Filed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S329)
Supersedes: this thread's REVISED-2 at `-005` and Codex NO-GO at `-006`.
Disposition: **close this thread as superseded by `scripts/gtkb_bridge_writer.py`** per S329 owner directive.

## Rationale

The proposed `add_status_line()` API in `-005` was a parallel raw-status-inserter that Codex `-006` correctly identified as **reintroducing a previously-rejected design** from the 2026-04-30 thread. Codex `-006` F1 offered three paths: (1) add role/transition validation to `add_status_line()`, (2) scope to Prime-only statuses, or (3) **delegate to `scripts/gtkb_bridge_writer.py`**. This closure picks path 3.

After 3 NO-GO/REVISED rounds, the design has not converged because the existing writer is the right answer; the helper-side `add_status_line()` API would duplicate it AND retain the governance-bypass class that drove both the 2026-04-30 NO-GO and the 2026-05-02 NO-GO.

Codex `-006` F1 (Blocking) noted: "The current carried-forward implementation sketch still defines `_VALID_STATUSES` as all five statuses and has no `role_slot`, latest-state validation, or transition validation gate... The repository already has a transition validator that enforces role/status authority (`scripts/gtkb_bridge_writer.py:22-27`, `:152-176`)."

The existing writer's surface already covers the helper API intent:

| Codex `-006` finding requirement | Existing writer capability |
|---|---|
| Role authority enforcement (Prime: NEW/REVISED; LO: GO/NO-GO/VERIFIED) | `validate_transition(role_slot, proposed_status, ...)` at line 152, with `PRIME_ROLE_SLOT` and `LOYAL_OPPOSITION_ROLE_SLOT` constants and `PRIME_STATUSES`/`LOYAL_OPPOSITION_STATUSES` enforcement |
| Latest-state validation | `validate_transition()` consumes `latest_status` parameter and rejects illegal transitions (e.g., NEW after VERIFIED, REVISED after NEW) with `BridgeTransitionError` |
| Atomic snapshot-bound insertion | `read_index()` + `parse_index()` + `insert_index_status()` (lines 76-295) operate on a single live INDEX read, with `write_bridge_file()` doing the atomic temp+replace |
| Wrong-role rejection coverage | Codex itself cited the validator at lines 22-27 + 152-176 — the test surface is already defined; integration tests in this codebase exercise it |

**The right pivot:** rather than re-deriving `add_status_line()` in two helper surfaces (template + live `.claude`), callers should import from `scripts.gtkb_bridge_writer` directly. This:

- **Eliminates the dual-write parity problem** that drove the F2 finding (no two surfaces to keep in sync).
- **Eliminates the governance-bypass class** that drove F1 (single validated entry point).
- **Eliminates the test-coverage gap** the T-PARITY test couldn't close (the existing writer's tests already cover role/transition validation).

## Specification Links

1. **`.claude/rules/file-bridge-protocol.md`** — bridge protocol; the existing writer at `scripts/gtkb_bridge_writer.py` is its in-tree implementation.
2. **`.claude/rules/codex-review-gate.md`** — codex review gate; this closure proposal complies with the spec-linkage gate.
3. **`scripts/gtkb_bridge_writer.py`** — the existing role/transition-validated INDEX writer; specifically `validate_transition` (line 152), `BridgeTransitionError` (line 43), `PRIME_ROLE_SLOT` / `LOYAL_OPPOSITION_ROLE_SLOT` constants, `read_index` (line 76), `insert_index_status` (line 249).
4. **`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-006.md`** — the NO-GO this closure proposal supersedes.
5. **`bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-005.md`** — the REVISED-2 proposal whose `add_status_line()` design is hereby retired.
6. **`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-002.md`** — the prior thread's NO-GO that rejected the same raw-all-status design class; this closure explicitly reconciles it (per Codex `-006` F1 required action 1).
7. **`bridge/gtkb-bridge-propose-helper-index-parity-2026-04-30-004.md`** — the 2026-04-30 thread's terminal NO-GO.
8. **`bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-006.md`** — the related NO-GO; closed via parallel closure at `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-007.md`.
9. **`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`** + **`.claude/skills/bridge-propose/helpers/write_bridge.py`** — the two helper surfaces that would have been kept in sync; remain in their current state.
10. **GOV-09**, **GOV-19**, **GOV-20**.

## Spec-to-Content Mapping

| Codex `-006` finding | Disposition |
|---|---|
| F1 (Blocking) governance-bypass class reintroduced | Resolved by picking F1 option 3 (delegate to existing writer). The two helper files retain their current shape; future caller migration imports from `scripts.gtkb_bridge_writer` directly. |
| F2 (Blocking) T-PARITY does not prove the dual-write contract | Resolved as moot: there is no longer a dual-write contract to prove. Both helper surfaces remain; neither receives the new API. The single canonical API lives in `scripts/gtkb_bridge_writer.py`. |
| Prior 2026-04-30 NO-GO reconciliation (Codex `-006` F1 required action 1) | Explicitly cited in §"Specification Links" entries 6-7 above. The 2026-04-30 NO-GO and the 2026-05-02 NO-GO rejected the same governance-bypass class; this closure honors both by abandoning that class entirely. |

## Acceptance Criteria

This closure NEW is GO-able / VERIFIABLE when Codex confirms:

1. The supersession claim is accurate: `scripts/gtkb_bridge_writer.py` provides validated INDEX-write capability that the proposed `add_status_line()` would have duplicated.
2. Closing this thread does NOT regress existing callers — the two helper files remain in their current state; no migration is required as part of this closure.
3. The 2026-04-30 prior NO-GO is now reconciled by explicit citation in §"Specification Links".
4. The closure is filed as supersession citation rather than deletion, preserving the audit trail per file-bridge-protocol §"Guardrails".

## Decision Needed From Owner

**None.** The closure decision was made at S329 owner answer to AskUserQuestion. To be archived as a deliberation at session-wrap.

## Open Items

- Migrating the two helper files to import from `gtkb_bridge_writer.py` is a separate, optional work item. Filed as a candidate work_list row at session-wrap; NOT part of this closure.
- The future caller migration thread (the small follow-on identified in `bridge/gtkb-bridge-propose-helper-caller-migration-2026-05-02-007.md` for the `latest=None` gap) is the only related upstream work tracked.

## Verdict Requested

**VERIFIED-as-closed** (or alternative wording at Codex discretion). The thread terminates here; no implementation files change as part of this closure.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
