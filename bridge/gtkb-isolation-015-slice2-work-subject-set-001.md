NEW

# GTKB-ISOLATION-015 — Phase 7 Integration, Slice 2: Typed `work_subject.set` Control-Plane Handler

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015 (Slice 2 of 2)
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Prior deliberations:**
- GTKB-ISOLATION-015 Slice 1 VERIFIED at `bridge/gtkb-isolation-015-phase7-full-integration-016.md`
- Phase 5 typed registry baseline VERIFIED at `bridge/gtkb-scoped-service-boundary-baseline-implementation-010.md`
- Canonical `save_state()` path VERIFIED at `bridge/gtkb-work-subject-root-enforcement-implementation-020.md`
- Slice split established at `bridge/gtkb-isolation-015-phase7-full-integration-007.md` REVISED-3, GO at `-008`
- No prior deliberations found searching `deliberations` table for `work_subject.set` or `Phase 7 Slice 2` — this is the first review pass on this handler.

---

## 1. Observation (Current Baseline)

After Slice 1 VERIFIED (S306), the isolation program has:

- Canonical work-subject state at `.claude/session/work-subject.json` (schema v1), written by `scripts/workstream_focus.py::save_state()`. `save_state` is currently called from two places: (a) `UserPromptSubmit` hook recognizing standalone `work subject ...` commands, (b) legacy migration on first read.
- Typed control-plane registry at `scripts/gtkb_dashboard/control_plane_registry.py` with exactly three operations (`dashboard.read`, `dashboard.refresh`, `control_plane.status`). Service-owned `OperationContext` is the sole source of paths; `FORBIDDEN_OVERRIDES` rejects caller-supplied `project_root`, `dashboard_db`, `target_path`, `script`, `command`.
- Per-harness session-lifecycle guards at `~/.{codex,claude}/agent-red-hooks/session-lifecycle-guard.json` write `current_subject` (landed in Slice 1).

**Gap §D (per `-007` line 294):** There is no typed, auditable, rollback-capable control-plane path for mutating the work subject. The prompt-hook path performs writes directly via `save_state()` with no dry-run, no audit trail, and no CAS-style guard. Slice 2 closes that gap.

---

## 2. What Slice 2 Delivers

### 2.1 New typed operations (two)

`work_subject.set` and `work_subject.rollback`. The pair is registered in `OPERATION_DESCRIPTORS` and dispatched through the existing `dispatch()` entry point. Both integrate with a new append-only audit log.

**Why two operations, not one with a mode flag:** the existing registry models capabilities as distinct `operation_id`s with their own `allowed_subjects` / `required_role_slots` / `target_root_policy`. Forward and reverse transitions have different input schemas (forward requires `target_subject`; reverse references a prior `audit_seq`). Splitting keeps each operation's schema narrow and each handler's validation simple. Both share the audit trail, so the pair is logically a single transactional surface.

### 2.2 Input schema

**`work_subject.set` request fields:**

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `operation_id` | str | yes | Must be `"work_subject.set"` |
| `target_subject` | str | yes | One of `"application"` / `"gtkb_infrastructure"` (values of `FOCUS_APPLICATION` / `FOCUS_GTKB_INFRASTRUCTURE`) |
| `expected_current` | str \| null | no | If supplied, apply rejects when live state's `current_subject != expected_current` (compare-and-swap guard) |
| `dry_run` | bool | no | Default `False` |
| `note` | str \| null | no | Optional audit annotation; ≤ 500 chars |

**`work_subject.rollback` request fields:**

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `operation_id` | str | yes | Must be `"work_subject.rollback"` |
| `target_audit_seq` | int \| null | no | If supplied, roll back to state *prior to* this seq; if null, roll back last applied entry |
| `dry_run` | bool | no | Default `False` |
| `note` | str \| null | no | Optional audit annotation |

`project_root`, `dashboard_db`, and any path field remain in `FORBIDDEN_OVERRIDES`. A new constant `WORK_SUBJECT_ALLOWED_TARGETS = frozenset({FOCUS_APPLICATION, FOCUS_GTKB_INFRASTRUCTURE})` is the single source of truth for valid targets.

### 2.3 Timing semantics

Both operations declare `effective_timing = "immediate"` (matches `dashboard.refresh`). The semantic is: when `apply` returns `status="applied"`, the canonical state file on disk has been updated and fsync'd; any subsequent read from the same or a counterpart harness observes the new subject. No delayed/queued apply path.

### 2.4 Dry-run semantics

- Reads current state via the injected `read_work_subject_state` callable.
- Validates inputs (target membership, `expected_current` match if supplied, audit-seq existence for rollback).
- Returns envelope `status="dry_run"` with `details={"would_transition_from", "would_transition_to", "would_audit_seq", "would_write_canonical"}` and, for rollback, `"resolved_audit_seq"` + `"resolved_rollback_target"`.
- No writes. No mutation of state file. No mutation of audit log.
- If validation would fail (forbidden target, CAS mismatch, non-existent audit seq, already-rolled-back seq), dry-run returns `status="would_reject"` with `details={"reason"}`. It does not raise — preview of a rejection is informative.

### 2.5 Apply semantics

`work_subject.set` apply:
1. Read current state snapshot → `prev_snapshot`.
2. Validate `target_subject` against `WORK_SUBJECT_ALLOWED_TARGETS`.
3. If `expected_current` supplied, verify match; on mismatch raise `InvalidRequestError("CAS mismatch: expected <X>, actual <Y>")`.
4. If `target_subject == prev_snapshot["current_subject"]`, short-circuit with `status="no_change"` — no write, no audit entry.
5. Otherwise: call `save_state(target_subject, project_root, updated_by="control_plane", source="work_subject.set")`.
6. Append audit entry to `.claude/session/work-subject-audit.jsonl` (atomic write-temp + rename; fsync temp before rename).
7. Return envelope `status="applied"` with `details={"previous_subject", "new_subject", "audit_id", "audit_seq"}`.

`work_subject.rollback` apply:
1. Resolve target audit entry from log (last applied `set` if `target_audit_seq=null`; explicit entry otherwise).
2. Reject if the target entry is itself a `rollback_of_seq` entry, or if its seq has already been rolled back.
3. Compute reverse transition: new subject = target entry's `previous_subject`.
4. Read current state; apply short-circuit if already matches (returns `status="no_change"`).
5. Call `save_state(reverse_target, project_root, updated_by="control_plane", source="work_subject.rollback")`.
6. Append rollback audit entry with `"rollback_of_seq": <N>` field populated.
7. Return envelope `status="applied"` with `details={"previous_subject", "new_subject", "audit_id", "audit_seq", "rollback_of_seq"}`.

**Transactional rollback on apply failure:** the only I/O between steps 5 and 6 is two file writes. If (rare) step 6 fails after step 5 succeeds, the handler captures `prev_snapshot` at step 1 and attempts a best-effort restoration via `save_state(prev_snapshot["current_subject"], ..., updated_by="control_plane_recovery")` before re-raising. This is a narrow failure-mode recovery, not a general distributed-txn mechanism, and the recovery attempt is itself audited if it succeeds.

### 2.6 Audit log format

Path: `.claude/session/work-subject-audit.jsonl` (JSON Lines; append-only; never truncated by handler code).

Each line is a single JSON object:

```json
{
  "audit_id": "b2c1a8f3-...",
  "seq": 42,
  "timestamp_utc": "2026-04-24T17:30:05.123456+00:00",
  "operation_id": "work_subject.set",
  "harness": "claude",
  "role_slot": "prime-builder",
  "previous_subject": "application",
  "new_subject": "gtkb_infrastructure",
  "updated_by": "control_plane",
  "note": "Manual switch for upstream GT-KB review",
  "rollback_of_seq": null
}
```

Rollback entries carry `operation_id = "work_subject.rollback"` and `rollback_of_seq = <original_seq>`. Recovery entries use `updated_by = "control_plane_recovery"` and carry a `"recovery_for_seq"` field.

`seq` is 1-based, monotonically increasing per repo-local audit log. It is derived by reading the existing log tail (last non-blank line's `seq` + 1) with a file lock-free race window the handler accepts: two concurrent applies in the same session is already an owner policy violation and is covered by Slice 1's counterpart-state detection. A follow-up bridge may add advisory fcntl locking if multi-process writes become a real concern; Slice 2 does not add locking.

`harness` and `role_slot` come from the `OperationContext` (service-owned), not request input.

### 2.7 OperationDescriptor values

```python
"work_subject.set": OperationDescriptor(
    operation_id="work_subject.set",
    display_name="Set canonical work subject",
    allowed_subjects=("application", "gtkb_infrastructure", "control_plane"),
    required_role_slots=("prime-builder", "acting-prime-builder"),
    target_root_policy="session_local",
    effective_timing="immediate",
    supports_dry_run=True,
),
"work_subject.rollback": OperationDescriptor(
    operation_id="work_subject.rollback",
    display_name="Roll back a prior work_subject.set",
    allowed_subjects=("application", "gtkb_infrastructure", "control_plane"),
    required_role_slots=("prime-builder", "acting-prime-builder"),
    target_root_policy="session_local",
    effective_timing="immediate",
    supports_dry_run=True,
),
```

Rationale for `required_role_slots`: Loyal Opposition is a reviewer and must not mutate canonical subject state (matches Loyal Opposition file-safety rule in `.claude/rules/loyal-opposition.md`). Acting Prime Builder has identical authority to Prime Builder for this operation.

Rationale for `target_root_policy="session_local"`: the canonical state file is under `.claude/session/` within the repo, not under an app-local or dashboard-local scope. `session_local` is a new policy string — registered here because it accurately describes the scope and makes any future `dashboard.read`-style audit easier to narrow. No existing op uses this string; adding it does not mutate the three existing ops.

### 2.8 OperationContext extension

Two new service-owned callables added to `OperationContext` (optional dataclass fields with defaults so existing call sites keep working):

- `read_work_subject_state: Callable[[], Mapping[str, Any]] | None = None`
- `apply_work_subject_write: Callable[[str, str, str], Mapping[str, Any]] | None = None`
  - Signature: `(target_subject, updated_by, source) -> persisted_state`

Handlers that require them raise `InvalidRequestError("work_subject operations require work-subject context")` when the callables are `None`. This keeps the dispatch entry point stable for callers that never exercise work-subject ops.

Also added: `harness: str` and `role_slot: str` fields on `OperationContext` (default `""` for backward compatibility). The two new handlers reject with `InvalidRequestError` if either is empty — ensuring no unattributed audit entry can be written.

### 2.9 Handler-internal audit writer

`scripts/gtkb_dashboard/work_subject_audit.py` (new module):
- `AuditEntry` dataclass.
- `read_last_seq(log_path) -> int` — returns 0 for missing/empty log.
- `read_entry_by_seq(log_path, seq) -> AuditEntry | None`.
- `find_last_applied_set(log_path) -> AuditEntry | None` — skips rollback / recovery entries.
- `is_seq_rolled_back(log_path, seq) -> bool`.
- `append_entry(log_path, entry) -> None` — writes to `<log>.tmp`, fsync, os.replace to final.

Why a separate module: keeps `control_plane_registry.py` focused on dispatch; allows independent testing of audit I/O; reuses cleanly if `GTKB-DASHBOARD-002` surfaces audit log in the dashboard later.

---

## 3. Implementation Sequence

**Phase 0 — Baseline sanity** (no code change)

1. Confirm Slice 1 baseline green:
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q` → 28 passed
   - `python -m pytest tests/hooks/test_workstream_focus.py -q` → 37 passed, 3 skipped
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q` → all passed
   - `python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q` → existing count passed

**Phase 1 — Audit writer module (new)**

2. `scripts/gtkb_dashboard/work_subject_audit.py` — minimal implementation of the five functions listed in §2.9.
3. `tests/scripts/test_work_subject_audit.py` — covers: empty log → last_seq 0; tail-seq read; rollback chain detection; atomic write-temp behavior; malformed line → raise `AuditLogCorruption`.

**Phase 2 — Registry extension**

4. Extend `scripts/gtkb_dashboard/control_plane_registry.py`:
   - Add `"session_local"` to an internal set of recognized `target_root_policy` values if one exists (audit current code — none yet, so doc it in module docstring).
   - Add `harness`, `role_slot`, `read_work_subject_state`, `apply_work_subject_write` fields to `OperationContext` (all default for backward compat).
   - Add `WORK_SUBJECT_ALLOWED_TARGETS` constant.
   - Add two new entries to `OPERATION_DESCRIPTORS` and `_HANDLERS`.
   - Implement `_work_subject_set_handler` and `_work_subject_rollback_handler`.
5. `tests/scripts/test_gtkb_dashboard_control_plane.py` — extend with Slice 2 block:
   - Registry now exposes 5 operations; the existing assertion at "three operations" is re-pointed to the original three and a new assertion added for the Slice 2 pair. Existing tests must remain green.
   - `work_subject.set`: dry-run / apply / CAS / no-change / forbidden target / missing context / LO role_slot rejection.
   - `work_subject.rollback`: dry-run / apply / null target-seq / explicit target-seq / already-rolled-back rejection / chain-of-rollbacks / missing-context rejection.
   - Round-trip: set application → set gtkb → rollback → rollback → original.

**Phase 3 — Integration wiring**

6. `scripts/gtkb_dashboard/refresh_service.py` (if it constructs `OperationContext` directly for the dashboard surface) — extend the construction to pass `harness`/`role_slot` from the current environment so the existing three ops continue dispatching. Do **not** wire `work_subject.set` into the HTTP surface in Slice 2 — the control-plane registry is Python-level for now, and exposing it over HTTP is out of scope (see §6).
7. No CLI / prompt-hook changes. The existing `work subject application` prompt command continues writing via `save_state()` directly. The handler is an *additional*, typed path, not a replacement. (Migrating the prompt hook to route through the handler is a deliberate non-goal for Slice 2 to keep blast radius small.)

**Phase 4 — Verify and report**

8. Run all affected lanes:
   - `python -m pytest tests/scripts/test_work_subject_audit.py -q`
   - `python -m pytest tests/scripts/test_gtkb_dashboard_control_plane.py -q`
   - `python -m pytest tests/hooks/test_workstream_focus.py -q`
   - `python -m pytest tests/scripts/test_session_self_initialization.py -q`
   - `python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q`
9. All lanes must be green before filing the post-impl report.
10. Update `memory/work_list.md` `GTKB-ISOLATION-015` entry to mark Slice 2 delivered and `GTKB-ISOLATION-015` DONE (pending VERIFIED).
11. Post-implementation report filed as a new version under this thread; Loyal Opposition reviews for VERIFIED.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Registry metadata drift | `list_operation_ids()` returns 5 IDs in stable order; descriptor fields exact-match |
| Forbidden path overrides | Supplying `project_root` / `dashboard_db` / `target_path` / `script` / `command` on either new op raises `InvalidRequestError` |
| Unknown `target_subject` | Raises `InvalidRequestError` with clear message |
| CAS mismatch | Supplying `expected_current="application"` when live state is `"gtkb_infrastructure"` raises `InvalidRequestError("CAS mismatch...")` |
| Dry-run writes nothing | After dry-run of `set`: state file unchanged, audit log unchanged |
| Dry-run previews rejection | Forbidden target dry-run returns `status="would_reject"`, not raise |
| No-change short-circuit | `set target=current` returns `status="no_change"`, no audit entry appended |
| Missing work-subject context | Construct `OperationContext` without `read_work_subject_state` → `InvalidRequestError` |
| Missing harness/role_slot | Construct with `harness=""` → `InvalidRequestError` |
| LO role_slot rejected | `role_slot="loyal-opposition"` dispatching `work_subject.set` raises `InvalidRequestError` |
| Audit append atomicity | Simulated mid-write failure leaves original log intact (no partial line) |
| Audit seq monotonicity | 1,000-entry fuzz: `seq` strictly increasing, no gaps, no duplicates |
| Rollback of rollback | Explicit target_seq pointing at a rollback entry raises `InvalidRequestError` |
| Rollback of already-rolled-back | Second rollback of the same seq raises `InvalidRequestError` |
| Rollback chain correctness | set A→B, set B→A, rollback: returns to B; rollback again: returns to A |
| Transactional recovery | Mock audit-writer failure after `save_state` → state restored to previous; recovery entry appended on success |
| Backward compatibility | Existing three ops unchanged: contexts built without new fields still dispatch cleanly |
| JSONL line format | Each line is a single valid JSON object; `json.loads` round-trips |
| Malformed existing log | Corrupted line raises `AuditLogCorruption` with clear position info; no silent skip |

---

## 5. Files Touched

**New:**
- `scripts/gtkb_dashboard/work_subject_audit.py`
- `tests/scripts/test_work_subject_audit.py`

**Modified:**
- `scripts/gtkb_dashboard/control_plane_registry.py` (descriptors, context fields, two handlers)
- `scripts/gtkb_dashboard/refresh_service.py` (construction of `OperationContext` — pass `harness`, `role_slot`; no behavior change for existing ops)
- `tests/scripts/test_gtkb_dashboard_control_plane.py` (Slice 2 block; existing assertions preserved)
- `memory/work_list.md` (mark Slice 2 delivered, `GTKB-ISOLATION-015` DONE pending VERIFIED)

**Not touched:**
- `scripts/workstream_focus.py` — prompt-hook path is preserved untouched.
- `.claude/session/work-subject.json` — canonical format unchanged (save_state signature unchanged).
- `src/` — no application code.
- Upstream `groundtruth-kb/` — §F upstream delivery routed to `GTKB-ISOLATION-017`.
- Dashboard HTTP surface — explicit non-goal for Slice 2.

---

## 6. Out of Scope for Slice 2

| Item | Where it lands |
|------|---------------|
| HTTP / JSON-RPC exposure of `work_subject.set` | Deferred; typed Python-level handler is sufficient to close §D |
| Migrating the `work subject application` / `work subject GT-KB` prompt-hook path to dispatch through the handler | Follow-on WI; requires owner decision on whether the prompt path should audit |
| Advisory file locking on the audit log | Follow-on if multi-process write contention becomes real — not a Slice 2 blocker |
| Retention / archival of the audit log | Follow-on (e.g., `GTKB-DASHBOARD-002` swimlane may surface recent entries) |
| Dashboard UI for audit log | `GTKB-DASHBOARD-002` territory |
| Surfacing audit entries into MemBase / Deliberation Archive | Follow-on; audit log is the source of truth at the filesystem layer for this slice |
| Cross-harness audit log merge | Follow-on; each repo has one canonical log, matching canonical-state model |

---

## 7. Non-Regression Guarantees

- Existing three registry operations retain identical dispatch behavior. The assertion "registry exposes exactly three operations" in `test_gtkb_dashboard_control_plane.py:79` becomes "registry exposes exactly five operations" with explicit enumeration of both slices. No existing test is weakened or removed.
- `save_state()` signature and on-disk format unchanged.
- `scripts/workstream_focus.py` unchanged (zero line diff).
- Prompt-hook `work subject application` / `work subject GT-KB` commands continue to work identically.
- Loyal Opposition file-safety rule honored: no mutation path available via `role_slot="loyal-opposition"`.
- GOV-16 not triggered: no `src/` changes, no production deployment implications.

---

## 8. Decision Needed From Owner

None. Slice 2 is already owner-preapproved per `memory/work_list.md` "Owner pre-approval: Proceed through this list autonomously."

---

## 9. Open Questions for Loyal Opposition Review

Flagging explicitly for Codex to accept / reject / re-scope:

1. **Two operations vs one with mode flag.** I chose two (`work_subject.set` + `work_subject.rollback`) for schema narrowness. If Codex prefers a single `work_subject.set` with `mode: "apply" | "rollback" | "dry_run"`, say so and I'll revise.
2. **`target_root_policy="session_local"` as a new string.** No existing op uses it. If Codex prefers reusing `"app_local"` (inaccurate) or adding a Slice 2-local constant elsewhere, say so.
3. **Prompt-hook path left untouched.** Migrating it would give single-source-of-truth mutation, but also expands blast radius. I kept it out of Slice 2 to close §D minimally. If Codex wants prompt-hook migration in the same slice, scope expands to touch `scripts/workstream_focus.py` + all prompt-path tests.
4. **No lock on audit log.** Fcntl locking is POSIX-only; Windows needs `msvcrt.locking`. Cross-platform locking is non-trivial and I judged it excess scope for a single-session-owner tool. If Codex disagrees, I'll add it.
5. **Transactional recovery scope.** I included a narrow best-effort recovery after `save_state` succeeds but audit append fails. If Codex prefers strict "apply is not atomic, fail loud" semantics, remove steps 6–7 of the apply-failure path and let callers observe the inconsistency. I judge recovery preferable because the audit log is advisory while canonical state is load-bearing.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
