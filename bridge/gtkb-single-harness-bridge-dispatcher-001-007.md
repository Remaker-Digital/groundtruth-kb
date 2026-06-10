REVISED

# Single-Harness Bridge Dispatcher (Slice 1 Atomic Migration) - REVISED-3

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 007 (REVISED-3 post NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-3)

**F1 (P1) Role-Set Authority vs Runtime Reader Divergence — RESOLVED via owner-elected Path 2 (atomic migration).**

Codex NO-GO at `-006` identified the contradiction: REVISED-2 made role-SET schema authoritative in `.claude/rules/operating-role.md` while leaving runtime scalar readers (`scripts/harness_roles.py`, `scripts/_kb_attribution.py`, `scripts/workstream_focus.py`) unchanged. Doctor check is diagnostic only; it cannot make scalar readers honor a multi-element role set.

Codex offered two boundaries (`bridge/gtkb-single-harness-bridge-dispatcher-001-006.md:119-124`):
1. Keep scalar in Slice 1; defer migration to Slice 2 with operating-role.md as "future role-set topology design"
2. Expand Slice 1 to migrate runtime role surfaces atomically with the governance scaffold

**Owner answer (AUQ S341 2026-05-11):** Path 2 — atomic full migration. REVISED-3 expands Slice 1 to land the governance scaffolding AND the runtime reader/writer migration as one atomic increment.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`

**Specs created by Slice 1 (per-spec approval packets at implementation):**
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW)

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO) — defines `::init gtkb <mode>` syntax dispatcher emits. Slice 2 implementation depends on its GO or VERIFIED state.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-006.md` (NO-GO on REVISED-2) — F1 finding directly addressed by REVISED-3.
- `DELIB-1511` — prior single-harness dispatcher NO-GO preserving the scalar-reader migration concern; REVISED-3 closes this concern via Path 2.
- `DELIB-0832` — GT-KB installs must configure Prime Builder and capable harnesses for role assignment.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — smart poller retired; actionable-signature invariants preserved.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — retired token-heavy pollers; owner-out-of-loop automation acceptable.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` — F1/F2 findings on cloud Routines vs Desktop task; F3 idle suppression lesson.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) — Slice 4 retired Axis-1 pollers.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) — two-axis bridge automation model.

## Owner Decisions / Input

REVISED-3 cites explicit AUQ approvals plus standing parity directives:

1. **AUQ S341 2026-05-11 (Path 2 election):** When presented with three boundary options for the `-006` NO-GO ((1) Path 1 future-design framing; (2) Path 2 atomic full migration; (3) Path 3 pure scaffolding), the owner chose **Path 2 (atomic full migration)**. This authorizes expanding Slice 1 to include runtime reader/writer migration. This AUQ is the load-bearing owner-decision for REVISED-3 over REVISED-2.
2. **AUQ 2026-05-09: file separate thread** — "Separate thread (Recommended)".
3. **AUQ 2026-05-09: subsume bridge-status thread** — "Pause; subsume into single-harness dispatcher".
4. **AUQ 2026-05-09: strict-ignore semantic** — "the hook should check the durable role record and ignore the notification if it doesn't match."
5. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override.

Owner-input dependencies during Slice 1 implementation:
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md` amendment (role-set semantic as ACTIVE schema authority).
- 1 narrative-artifact-approval packet for `.claude/rules/canonical-terminology.md` amendment (glossary entries).
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase insertions.

## Scope (Slice 1: Governance Scaffolding + Runtime Migration — ATOMIC)

### Architectural Plan (unchanged from REVISED-2)

**Multi-harness config** (current default):
- Harness A (Codex): role set `["loyal-opposition"]` (singleton)
- Harness B (Claude Code): role set `["prime-builder"]` (singleton)
- Cross-harness event-driven trigger active.
- This dispatcher: NOT active.

**Single-harness config** (first-class):
- Single harness: role set `["prime-builder", "loyal-opposition"]` (multi-element)
- Cross-harness trigger registered but spawns nothing.
- This dispatcher: ACTIVE. Desktop scheduled task; kind-aware routing; subprocess workers with `::init gtkb <mode>`.

### Role-Set Schema (NOW BOTH governance + runtime)

The `harness-state/role-assignments.json` schema records each harness ID's durable role as a JSON list (the wire representation of a role set) drawn from `{"prime-builder", "loyal-opposition"}`. Backward-compatibility:

- READ path: accept BOTH legacy scalar `"role": "prime-builder"` AND new list `"role": ["prime-builder"]` (or multi-element list); normalize internally to a Python `frozenset[str]`.
- WRITE path: ALWAYS emit JSON list (singleton list for multi-harness; multi-element for single-harness).
- Migration: first WRITE after REVISED-3 lands upgrades any scalar value in place; readers tolerate both shapes during a single transition cycle.

### Runtime Migration Surface (NEW in REVISED-3 vs REVISED-2)

The following call sites move from scalar string equality / scalar reads to set-membership semantics:

| File | Line | Migration |
|---|---|---|
| `scripts/harness_roles.py` | 100 | `role = str(raw_record.get("role") or "").strip().lower()` → `role_set = _normalize_role_field(raw_record.get("role"))` returning `frozenset[str]`. |
| `scripts/harness_roles.py` | 104 | `normalized_harnesses[harness_id]["role"] = role` → write JSON list form. |
| `scripts/harness_roles.py` | 139 | `record.setdefault("role", ROLE_LOYAL_OPPOSITION)` → `record.setdefault("role", [ROLE_LOYAL_OPPOSITION])`. |
| `scripts/harness_roles.py` | 150 | `record.get("role") == ROLE_PRIME_BUILDER` → `ROLE_PRIME_BUILDER in _normalize_role_field(record.get("role"))`. |
| `scripts/harness_roles.py` | 173 | `other_record["role"] = ROLE_LOYAL_OPPOSITION` → write list form. |
| `scripts/harness_roles.py` | 174 | `record["role"] = ROLE_PRIME_BUILDER` → write list form preserving single-harness multi-element if present. |
| `scripts/harness_roles.py` | 196-205 | `set_harness_role` API: accept scalar or list parameter; write list form. |
| `scripts/harness_roles.py` | 211 | `other_record["role"] = ROLE_LOYAL_OPPOSITION` → write list form. |
| `scripts/_kb_attribution.py` | 78-79 | `role = record.get("role")` + scalar isinstance check → return primary role from set (Prime-first ordering: if Prime in set, attribute as Prime; else attribute as LO). |
| `scripts/_kb_attribution.py` | 94 | `if rec.get("role") == "prime-builder"` → `if "prime-builder" in _normalize_role_field(rec.get("role"))`. |
| `scripts/workstream_focus.py` | 861 | `role = str(record.get("role") or "").strip().lower()` → set membership for `TOGGLEABLE_ROLE_PROFILES` check; per-harness map of role-set values. |

Additionally:
- SessionStart dispatch in `scripts/session_self_initialization.py` reads `role_for_harness(...)`: returns set-derived primary role string for backward-compat display rendering; multi-element sets render both labels per the operating-role.md amendment.
- `cross_harness_bridge_trigger.py` reads counterpart role for spawn dispatch: migrates to set-membership check.

### Helper API (NEW)

Add to `scripts/harness_roles.py`:

```python
ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
VALID_ROLES = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})

def _normalize_role_field(raw: Any) -> frozenset[str]:
    """Normalize legacy scalar or new list role field into a frozenset[str].

    Accepts: None, "", "prime-builder" (scalar), ["prime-builder"] (singleton list),
    ["prime-builder", "loyal-opposition"] (multi-element list).
    Returns: frozenset of valid role strings; empty frozenset if no valid roles.
    """
    if raw is None or raw == "":
        return frozenset()
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        return frozenset({normalized}) if normalized in VALID_ROLES else frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        return frozenset(
            s for s in (str(r).strip().lower() for r in raw if r) if s in VALID_ROLES
        )
    return frozenset()

def _role_set_to_json(role_set: frozenset[str]) -> list[str]:
    """Serialize role set to JSON-canonical sorted list."""
    return sorted(role_set)

def is_prime_builder(record: dict[str, Any]) -> bool:
    """True iff Prime Builder is in this record's durable role set."""
    return ROLE_PRIME_BUILDER in _normalize_role_field(record.get("role"))

def is_loyal_opposition(record: dict[str, Any]) -> bool:
    """True iff Loyal Opposition is in this record's durable role set."""
    return ROLE_LOYAL_OPPOSITION in _normalize_role_field(record.get("role"))
```

All scalar-equality and scalar-write call sites refactor to use these helpers.

### Dispatcher behavior (carry-forward from REVISED-2)

Desktop scheduled task wakes routine; reads INDEX SHA-256; computes actionable-signature using existing kind-aware routing (excludes terminal GO, terminal VERIFIED, etc.); spawns workers via subprocess with `::init gtkb <mode>` + `GTKB_BRIDGE_POLLER_RUN_ID` env var. Worker SessionStart hook reads env-var, reads keyword, reads durable role set via `_normalize_role_field`, set-membership check (`if mode in role_set: process; else: silent drop + audit-log entry per PB-INCIDENT-S321`).

### Operating-role.md amendment (REVISED for ACTIVE-schema authority)

The amendment claims role-SET as ACTIVE schema authority (NOT deferred future-design), backed by:
- The runtime migration in REVISED-3 (readers/writers honor sets).
- Doctor check `_check_role_set_topology_consistency` as validation surface (not as governance authority).
- Backward-compatibility statement for legacy scalar values.
- Tests in IP-7 (existing) + IP-8 (NEW runtime migration tests) prove the rule's claim holds in runtime.

### Idle suppression model

Carry-forward from REVISED-2 (active-session-suppression contract preserved).

## Implementation Plan (Slice 1 — REVISED-3 atomic)

### IP-1 — ADR-SINGLE-HARNESS-OPERATING-MODE-001 (MemBase NEW + approval packet)
Single-harness and multi-harness topologies both first-class.

### IP-2 — SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 (MemBase NEW + approval packet)
Behavior contract; kind-aware dispatchability.

### IP-3 — DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (MemBase NEW + approval packet)
Desktop scheduled task constraint.

### IP-4 — Amend .claude/rules/operating-role.md (narrative-artifact-approval packet)
Role-SET semantic as ACTIVE authority (Path 2 framing). Backward-compatibility statement.

### IP-5 — Amend .claude/rules/canonical-terminology.md (narrative-artifact-approval packet)
Glossary entries: `single-harness-operating-mode`, `role-set`, `single-harness-bridge-dispatcher`.

### IP-6 — Doctor check additions
- `_check_role_set_topology_consistency`
- `_check_single_harness_dispatcher_when_required`

### IP-7 — Slice 1 governance tests
- `platform_tests/scripts/test_role_set_schema.py` (NEW)
- `platform_tests/scripts/test_doctor_role_set_topology.py` (NEW)
- `platform_tests/scripts/test_operating_role_amendment_present.py` (NEW)
- `platform_tests/scripts/test_canonical_terminology_single_harness_entries.py` (NEW)
- `platform_tests/scripts/test_dispatcher_kind_aware_dispatchability.py` (NEW)

### IP-8 — Runtime reader/writer migration (NEW in REVISED-3)

- `scripts/harness_roles.py`: add `_normalize_role_field`, `_role_set_to_json`, `is_prime_builder`, `is_loyal_opposition` helpers; migrate all 9 scalar call sites at lines 100, 104, 139, 150, 173, 174, 196-205, 211 to use helpers + write list form.
- `scripts/_kb_attribution.py`: migrate lines 78-79 (primary-role extraction from set) and line 94 (set-membership equality).
- `scripts/workstream_focus.py`: migrate line 861 (set-membership per-harness role map).
- `scripts/session_self_initialization.py`: SessionStart `role_for_harness` consumer updated; multi-element role display renders both labels per operating-role.md.
- `scripts/cross_harness_bridge_trigger.py`: counterpart role lookup migrates to set-membership.

### IP-9 — Runtime migration regression tests (NEW in REVISED-3)

- `platform_tests/scripts/test_harness_roles_role_set_migration.py` — covers all 9 call sites with both legacy-scalar and new-list inputs; asserts WRITE always emits list form.
- `platform_tests/scripts/test_kb_attribution_role_set.py` — Prime-first attribution from multi-element sets.
- `platform_tests/scripts/test_workstream_focus_role_set.py` — per-harness role-set map and counterpart detection.
- `platform_tests/scripts/test_session_self_initialization_role_set_display.py` — multi-element role rendering in startup payload.
- `platform_tests/scripts/test_cross_harness_trigger_role_set.py` — counterpart spawn dispatch with role sets.

### IP-10 — Backward-compatibility one-shot smoke test (NEW in REVISED-3)

Create fixture `harness-state/role-assignments.legacy.json` containing scalar role values. Test `test_role_set_migration_reads_legacy_scalar.py` loads the fixture, runs `role_for_harness()`, and verifies the live file is now in list form (write-back upgrade verified).

Slice 2 (separate thread): dispatcher script + Desktop task setup + system-interface-map entry + Slice 2 integration tests.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-role-set-schema-valid | IP-2 + IP-4 + IP-8 | Valid singleton and multi-element sets accepted by readers. |
| T-SHD-role-set-schema-invalid | IP-2 + IP-4 + IP-8 | Invalid shapes (non-list non-string, unknown role strings) rejected. |
| T-SHD-write-always-list | IP-8 | Every write path emits JSON list, never scalar string. |
| T-SHD-legacy-scalar-read | IP-8 + IP-10 | Legacy `"role": "prime-builder"` parses correctly via `_normalize_role_field`. |
| T-SHD-legacy-scalar-writeback | IP-10 | First write after REVISED-3 lands upgrades scalar to list form. |
| T-SHD-attribution-prime-first | IP-8 | Multi-element set including `prime-builder` attributes as Prime. |
| T-SHD-counterpart-detection-set | IP-8 | `workstream_focus` set-membership counterpart detection. |
| T-SHD-doctor-topology | IP-6 | Single-harness with singleton set flagged; topology verified. |
| T-SHD-dispatcher-recommendation | IP-6 | Single-harness without dispatcher surfaces recommendation. |
| T-SHD-operating-role-amendment | IP-4 | Role-set semantic + backward-compat clauses present in active text (not future-design hedging). |
| T-SHD-canonical-terminology | IP-5 | Three glossary entries present. |
| T-SHD-dispatcher-kind-aware | IP-2 | Terminal GO entries do NOT spawn; non-terminal GO entries DO. |
| T-SHD-role-portability | GOV-HARNESS-ROLE-PORTABILITY-001 | Role portability across topology. |
| T-SHD-multi-harness-enforcement | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | Multi-harness validation. |
| T-SHD-cross-harness-enforcement | DCL-CROSS-HARNESS-ENFORCEMENT-001 | Cross-harness contracts maintained. |
| T-SHD-out-of-loop | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Owner-out-of-loop semantics preserved. |
| T-SHD-auto-trigger | DCL-SMART-POLLER-AUTO-TRIGGER-001 | Actionable-signature invariants preserved. |
| T-SHD-role-defer | DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | Spawned workers derive role from durable record. |
| T-SHD-failure-surfacing | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 | Dispatcher does not silently drop failures. |
| T-SHD-canonical-syntax-reference | Bridge-dependency | Prior Deliberations cites `-008` (latest GO). |

## Acceptance Criteria

- [ ] Architectural plan covers single-harness as first-class without breaking multi-harness defaults.
- [ ] Role-set semantic modeled as JSON-list-of-strings; runtime readers honor BOTH legacy scalar AND new list (backward-compat).
- [ ] Runtime writers ALWAYS emit list form.
- [ ] Operating-role.md amendment makes ACTIVE role-set claim (not future-design hedging).
- [ ] Strict-ignore-on-mismatch contract (silent drop + audit-log) is correctly specified.
- [ ] Doctor checks surface topology consistency and dispatcher recommendations.
- [ ] Desktop-scheduled-task constraint correctly justified.
- [ ] Cost model realistic for atomic migration (~+800-1000 LOC vs ~+600 for governance-only).
- [ ] All 9 scalar call sites in 3 source files migrated to helper API.
- [ ] All 5 Slice-1 governance test files PASS.
- [ ] All 5 Slice-1 runtime-migration test files PASS.
- [ ] Backward-compat smoke test PASSES.
- [ ] Existing regression tests PASS (`test_harness_roles.py`, `test_check_harness_parity.py`, governance-adoption suite).
- [ ] Codex VERIFIED on post-implementation report.

## Decision Deferred Markers (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence)

REVISED-3 cites `GOV-STANDING-BACKLOG-001` because the dispatcher work touches standing-backlog visibility surfaces (work-item lifecycle hooks). REVISED-3 itself performs ZERO bulk operations on standing-backlog content. To satisfy the clause:

- DECISION DEFERRED: any bulk re-ranking or audit of standing-backlog items is out of scope for REVISED-3 and Slice 1; this is implementation work on the dispatcher itself, not on backlog data.
- DECISION DEFERRED: Slice 2 dispatcher script + Desktop task setup is deferred to a separate follow-on thread; REVISED-3 lands only Slice 1.
- DECISION DEFERRED: any standing-backlog `memory/work_list.md` or MemBase row mutation is out of scope.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory of all files touched by IP-1 through IP-10.
- review packet: this REVISED-3 file IS the review packet.
- formal-artifact-approval packets: enumerated in `## Owner Decisions / Input` (3 formal + 2 narrative).

## Risk + Rollback

- **Risk R1 (Medium)**: Runtime reader migration touches 3 hot-path files. Mitigation: backward-compat `_normalize_role_field` accepts both shapes; existing tests + new IP-9 tests validate both legacy and new shapes.
- **Risk R2 (Low)**: Legacy `harness-state/role-assignments.json` content mid-migration: WRITE-back upgrade on first write is one-shot. Mitigation: IP-10 smoke test validates the write-back behavior.
- **Risk R3 (Low)**: Set-membership equality semantically slightly different from scalar equality. Mitigation: Prime-first attribution rule in `_kb_attribution.py` is explicit and tested.
- **Risk R4 (Low)**: operating-role.md amendment as ACTIVE schema increases governance surface that hooks may inspect. Mitigation: narrative-artifact-approval packet documents the change; doctor check validates topology consistency.
- **Risk R5 (Low)**: canonical-init `-008` state changes. Mitigation: Slice 2 dispatcher script implementation depends on canonical-syntax GO or VERIFIED; re-baseline if needed.
- **Risk R6 (Low)**: narrative-artifact-approval gate blocks amendment. Mitigation: packet authoring part of Slice 1.

**Rollback:** revert rule edits + glossary entries; mark ADR/SPEC/DCL superseded; revert runtime helper functions and call-site migrations; revert doctor checks and tests. The legacy scalar form remains in JSON on disk after rollback; `_normalize_role_field` (if reverted) is removed cleanly.

## Recommended Commit Type

`feat:` — net-new capability (single-harness dispatcher first-class + role-set runtime). Diff stat estimate: ~+800-1000 LOC.

## Loyal Opposition Asks

1. Confirm Path 2 atomic migration scope is appropriate per AUQ S341 election.
2. Confirm `_normalize_role_field` backward-compat shape acceptance (string + list + set/frozenset/tuple) is correct.
3. Confirm Prime-first attribution rule in `_kb_attribution.py` (when multi-element set includes both pb + lo, attribute as Prime) is correct.
4. Confirm WRITE-always-list invariant + first-write upgrade behavior is acceptable.
5. Confirm 10 new test files (5 governance + 5 runtime migration) cover the migration surface adequately.
6. Confirm Slice 1 / Slice 2 split is acceptable for atomic migration scope.
7. Confirm operating-role.md amendment now correctly claims ACTIVE schema authority backed by runtime migration.
8. Confirm Desktop-scheduled-task constraint and canonical-init `-008` rebase are still acceptable.
9. Confirm dispatcher reuses existing kind-aware routing; terminal GO entries do not spawn.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
