REVISED

# Single-Harness Bridge Dispatcher (Slice 1 Atomic Migration) - REVISED-4

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 009 (REVISED-4 post NO-GO at `-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-4)

**F1 (P1) Role-Set Migration Drops `acting-prime-builder` Legacy-Read Compatibility — RESOLVED.**

Codex NO-GO at `-008` (`bridge/gtkb-single-harness-bridge-dispatcher-001-008.md:125-156`) identified that the REVISED-3 helper `_normalize_role_field` used `VALID_ROLES = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})`, which would drop legacy `acting-prime-builder` scalar values during the migration. The role-session-lifecycle thread VERIFIED at `-010` established the active Compatibility/Provenance Classification contract for `acting-prime-builder`:

- **SET**: REJECT `acting-prime-builder` as a target value (only `prime-builder` and `loyal-opposition` are valid SET targets).
- **READ**: ACCEPT existing `acting-prime-builder` values for backward-compatibility with role-map entries set in prior sessions or by explicit owner-directed legacy-role-switch operations.

REVISED-4 honors this contract by splitting the helper API into two role-set vocabularies:

- `VALID_ROLES_FOR_READ = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION, ROLE_ACTING_PRIME_BUILDER})` — accepted during READ-path normalization.
- `VALID_ROLES_FOR_WRITE = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})` — emitted by WRITE paths.

Write paths NEVER emit `acting-prime-builder` (preserving the SET-reject contract from `acting-prime-builder.md` Compatibility/Provenance Classification section). Read paths accept `acting-prime-builder` and treat it as Prime-equivalent for attribution semantics (since the legacy meaning was "Codex acting as Prime Builder when canonical Prime was unavailable" per `GOV-ACTING-PRIME-BUILDER-001`).

All other REVISED-3 content carries forward unchanged. Specifically: Path 2 atomic migration scope (touching `harness_roles.py`, `_kb_attribution.py`, `workstream_focus.py`, plus SessionStart dispatch and cross-harness trigger consumers); operating-role.md amendment as ACTIVE schema authority; 10 IPs; 10 test files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-ACTING-PRIME-BUILDER-001` (NEW citation in REVISED-4) — defines the Compatibility/Provenance Classification contract that REVISED-4 honors.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/acting-prime-builder.md` (NEW citation in REVISED-4) — Compatibility/Provenance Classification section explicitly states the READ/SET asymmetry.
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `bridge/gtkb-role-session-lifecycle-simplification-010.md` (NEW citation) — VERIFIED report confirming the live Compatibility/Provenance Classification implementation.

**Specs created by Slice 1 (per-spec approval packets at implementation):**
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW)

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-008.md` (NO-GO on REVISED-3) — F1 finding directly addressed by REVISED-4.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md` (REVISED-3 with Path 2 atomic migration scope) — carry-forward.
- `bridge/gtkb-role-session-lifecycle-simplification-010.md` (VERIFIED, 2026-05-11) — confirms the live `acting-prime-builder` Compatibility/Provenance Classification contract that REVISED-4 honors.
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO) — `::init gtkb <mode>` syntax dispatcher emits.
- `DELIB-1511` — prior NO-GO preserving the scalar-reader migration concern.
- `DELIB-0830` — owner decision: Loyal Opposition assumes acting Prime Builder when canonical Prime unavailable. This DELIB motivated `acting-prime-builder` semantics that REVISED-4 must preserve in READ.
- `DELIB-0831` — Prime/LO portable across harnesses.
- `DELIB-0832` — GT-KB installs configure Prime Builder.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` — actionable-signature invariants preserved.

## Owner Decisions / Input

REVISED-4 cites the same explicit AUQ approvals as REVISED-3, plus the catch-up directive that authorizes this filing:

1. **AUQ S341 2026-05-11 catch-up directive (NEW citation):** "Please act on the remaining queue. Continue parallelize work on the backlog and outstanding bridge items. Work independently without owner interaction where possible." Authorizes this REVISED-4 filing under the standing autonomous-execution directive.
2. **AUQ S341 2026-05-11 (Path 2 election):** Owner-elected Path 2 (atomic full migration) — carried forward from REVISED-3.
3. **AUQ 2026-05-09: file separate thread** — "Separate thread (Recommended)".
4. **AUQ 2026-05-09: subsume bridge-status thread** — "Pause; subsume into single-harness dispatcher".
5. **AUQ 2026-05-09: strict-ignore semantic** — "the hook should check the durable role record and ignore the notification if it doesn't match."
6. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override.

Owner-input dependencies during Slice 1 implementation (unchanged from REVISED-3):
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md` amendment.
- 1 narrative-artifact-approval packet for `.claude/rules/canonical-terminology.md` amendment.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase insertions.

No new owner-AUQ rounds needed for the REVISED-4 F1 fix (it is a narrow helper-API correction within the existing slice; the autonomous-execution directive standing authorization covers the revision filing).

## Scope (Slice 1: Governance Scaffolding + Runtime Migration — ATOMIC, Acting-Prime READ-Compatible)

### Architectural Plan (unchanged from REVISED-3)

**Multi-harness config** (current default):
- Harness A (Codex): role set `["loyal-opposition"]` (singleton)
- Harness B (Claude Code): role set `["prime-builder"]` (singleton)
- Cross-harness event-driven trigger active.
- This dispatcher: NOT active.

**Single-harness config** (first-class):
- Single harness: role set `["prime-builder", "loyal-opposition"]` (multi-element)
- Cross-harness trigger registered but spawns nothing.
- This dispatcher: ACTIVE.

### Role-Set Schema (REVISED-4: READ vs WRITE vocabulary split)

The `harness-state/role-assignments.json` schema records each harness ID's durable role as a JSON list of strings.

**READ vocabulary** (accepted during normalization):
- `"prime-builder"`
- `"loyal-opposition"`
- `"acting-prime-builder"` (legacy/compatibility/provenance per `GOV-ACTING-PRIME-BUILDER-001`; preserved per role-session-lifecycle-010 VERIFIED contract)

**WRITE vocabulary** (emitted by writers; SET-rejection enforced):
- `"prime-builder"`
- `"loyal-opposition"`

Backward-compatibility:
- READ path accepts BOTH legacy scalar AND list shapes.
- READ path accepts legacy `acting-prime-builder` values and treats them as Prime-equivalent for attribution semantics.
- WRITE path ALWAYS emits JSON list of WRITE-vocabulary values; NEVER emits `acting-prime-builder`.
- Migration: first WRITE after REVISED-4 lands upgrades any scalar value in place (preserving `acting-prime-builder` as Prime via normalization).

### Runtime Migration Surface (unchanged from REVISED-3, with READ-vocabulary expansion)

Call-site migration table unchanged from REVISED-3 §"Runtime Migration Surface" except that all readers use `VALID_ROLES_FOR_READ` (3 elements) and all writers use `VALID_ROLES_FOR_WRITE` (2 elements). The migration table at REVISED-3 lines 99-113 carries forward.

### Helper API (REVISED-4 update)

Add to `scripts/harness_roles.py`:

```python
ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"

# Per role-session-lifecycle-010 VERIFIED Compatibility/Provenance Classification contract:
# SET rejects acting-prime-builder; READ accepts it (legacy values preserved).
VALID_ROLES_FOR_READ = frozenset({
    ROLE_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
    ROLE_ACTING_PRIME_BUILDER,
})
VALID_ROLES_FOR_WRITE = frozenset({
    ROLE_PRIME_BUILDER,
    ROLE_LOYAL_OPPOSITION,
})


def _normalize_role_field(raw: Any) -> frozenset[str]:
    """Normalize legacy scalar or new list role field into a frozenset[str].

    Accepts (READ vocabulary):
      - None, "" -> frozenset()
      - "prime-builder" (scalar) -> frozenset({"prime-builder"})
      - "loyal-opposition" (scalar) -> frozenset({"loyal-opposition"})
      - "acting-prime-builder" (scalar) -> frozenset({"acting-prime-builder"})
      - ["prime-builder"] (singleton list) -> frozenset({"prime-builder"})
      - ["prime-builder", "loyal-opposition"] (multi-element list) -> the set
      - Mixed legacy/new shapes -> validates each element against READ vocabulary

    Returns: frozenset of READ-vocabulary role strings; empty frozenset if no
    valid roles found.
    """
    if raw is None or raw == "":
        return frozenset()
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        return frozenset({normalized}) if normalized in VALID_ROLES_FOR_READ else frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        return frozenset(
            s for s in (str(r).strip().lower() for r in raw if r) if s in VALID_ROLES_FOR_READ
        )
    return frozenset()


def _role_set_to_json(role_set: frozenset[str]) -> list[str]:
    """Serialize role set to JSON-canonical sorted list.

    Filters out acting-prime-builder per the WRITE vocabulary contract.
    Acting-prime-builder values are READ-accepted but never WRITTEN.
    """
    return sorted(r for r in role_set if r in VALID_ROLES_FOR_WRITE)


def is_prime_builder(record: dict[str, Any]) -> bool:
    """True iff Prime Builder is in this record's durable role set (READ semantics).

    Per GOV-ACTING-PRIME-BUILDER-001, acting-prime-builder values are
    Prime-equivalent for attribution. Returns True for either prime-builder
    OR acting-prime-builder in the record's role set.
    """
    role_set = _normalize_role_field(record.get("role"))
    return ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set


def is_loyal_opposition(record: dict[str, Any]) -> bool:
    """True iff Loyal Opposition is in this record's durable role set."""
    return ROLE_LOYAL_OPPOSITION in _normalize_role_field(record.get("role"))


def _set_role_validate(requested_role: str) -> str:
    """Validate a SET-time role argument against the WRITE vocabulary.

    Per acting-prime-builder.md Compatibility/Provenance Classification:
    SET operations REJECT acting-prime-builder; only prime-builder and
    loyal-opposition are valid SET targets.

    Raises ValueError if the role is not in VALID_ROLES_FOR_WRITE.
    """
    normalized = str(requested_role or "").strip().lower()
    if normalized not in VALID_ROLES_FOR_WRITE:
        raise ValueError(
            f"Unsupported next-session role: {requested_role!r}. "
            f"Valid SET targets: {sorted(VALID_ROLES_FOR_WRITE)}. "
            f"acting-prime-builder is READ-accepted (legacy) but SET-rejected."
        )
    return normalized
```

All scalar-equality and scalar-write call sites refactor to use these helpers. The `set_harness_role` API now validates via `_set_role_validate` (replacing the old inline check).

### Dispatcher behavior (carry-forward from REVISED-3)

Unchanged.

### Operating-role.md amendment (carry-forward from REVISED-3, with READ-compat note)

The amendment claims role-SET as ACTIVE schema authority, backed by:
- The runtime migration in REVISED-4 (readers/writers honor sets via helper API).
- Doctor check `_check_role_set_topology_consistency` as validation surface.
- Backward-compatibility statement: READ accepts legacy scalar `prime-builder`, `loyal-opposition`, AND `acting-prime-builder` values; WRITE emits only the 2-element write vocabulary.
- Tests in IP-7 + IP-8 + IP-9 + new IP-9b cover both READ and WRITE vocabularies.

### Idle suppression model

Carry-forward from REVISED-3.

## Implementation Plan (Slice 1 — REVISED-4 atomic, READ-compatible)

IP-1 through IP-10 carry forward from REVISED-3 unchanged, with these REVISED-4 modifications:

### IP-8 — Runtime reader/writer migration (REVISED-4 updates)

- Helper API uses `VALID_ROLES_FOR_READ` (3 elements) and `VALID_ROLES_FOR_WRITE` (2 elements) per the schema above.
- `set_harness_role` API uses `_set_role_validate` for SET-rejection of `acting-prime-builder`.
- `is_prime_builder` returns True for either `prime-builder` OR `acting-prime-builder` (Prime-equivalent attribution).

### IP-9 — Runtime migration regression tests (REVISED-4 updates)

Carry-forward from REVISED-3 with:
- `test_harness_roles_role_set_migration.py` — adds test cases for `acting-prime-builder` READ acceptance + SET rejection.

### IP-9b — Acting-Prime Legacy-Read Compatibility Tests (NEW per F1 of `-008`)

- `platform_tests/scripts/test_acting_prime_legacy_read_compat.py` (NEW):
  - `test_legacy_acting_prime_scalar_read` — record with `"role": "acting-prime-builder"` parses correctly via `_normalize_role_field`; `is_prime_builder` returns True.
  - `test_legacy_acting_prime_list_read` — record with `"role": ["acting-prime-builder"]` parses correctly.
  - `test_legacy_acting_prime_mixed_set_read` — record with `"role": ["acting-prime-builder", "loyal-opposition"]` parses correctly; `is_prime_builder` AND `is_loyal_opposition` both True.
  - `test_set_role_rejects_acting_prime` — `set_harness_role("acting-prime-builder", ...)` raises `ValueError`.
  - `test_set_role_writeback_excludes_acting_prime` — `_role_set_to_json(frozenset({"acting-prime-builder", "prime-builder"}))` returns `["prime-builder"]` (acting-prime-builder filtered from WRITE).
  - `test_attribution_prime_equivalent` — `_kb_attribution.py` Prime-first attribution returns Prime when set contains `acting-prime-builder` only.

## Spec-Derived Test Plan

Carry-forward from REVISED-3 with:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-acting-prime-legacy-scalar-read | F1 of `-008`; GOV-ACTING-PRIME-BUILDER-001 | Legacy scalar `"acting-prime-builder"` parses correctly via `_normalize_role_field`. |
| T-SHD-acting-prime-legacy-list-read | F1 of `-008`; GOV-ACTING-PRIME-BUILDER-001 | Legacy list `["acting-prime-builder"]` parses correctly. |
| T-SHD-acting-prime-set-rejected | F1 of `-008`; acting-prime-builder.md Compatibility/Provenance | `set_harness_role("acting-prime-builder", ...)` raises `ValueError`. |
| T-SHD-acting-prime-writeback-filtered | F1 of `-008` | `_role_set_to_json` filters acting-prime-builder from output list. |
| T-SHD-acting-prime-prime-equivalent | F1 of `-008`; GOV-ACTING-PRIME-BUILDER-001 | `is_prime_builder` returns True when acting-prime-builder in record's role set. |
| (All REVISED-3 T-SHD rows carry forward) | | |

## Acceptance Criteria

(Carry-forward from REVISED-3 plus:)

- [ ] `VALID_ROLES_FOR_READ` includes `acting-prime-builder`; `VALID_ROLES_FOR_WRITE` does not.
- [ ] `_normalize_role_field` accepts `acting-prime-builder` in scalar AND list forms.
- [ ] `_role_set_to_json` filters `acting-prime-builder` from output (WRITE-vocabulary contract).
- [ ] `set_harness_role` raises `ValueError` for `acting-prime-builder` argument (SET-rejection).
- [ ] `is_prime_builder` returns True for either `prime-builder` OR `acting-prime-builder` in role set (Prime-equivalent attribution).
- [ ] New `test_acting_prime_legacy_read_compat.py` test file PASSES (6 tests).
- [ ] All REVISED-3 acceptance criteria continue to hold.

## Decision Deferred Markers (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence)

(Carry-forward from REVISED-3 unchanged; REVISED-4 adds no new bulk operations.)

- DECISION DEFERRED: any bulk re-ranking or audit of standing-backlog items is out of scope.
- DECISION DEFERRED: Slice 2 dispatcher script + Desktop task setup is deferred to a separate follow-on thread.
- DECISION DEFERRED: any standing-backlog `memory/work_list.md` or MemBase row mutation is out of scope.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory.
- review packet: this REVISED-4 file IS the review packet.
- formal-artifact-approval packets: enumerated in `## Owner Decisions / Input` (3 formal + 2 narrative).

## Risk + Rollback

(Carry-forward from REVISED-3 plus:)

- **Risk R7 (Low)**: `acting-prime-builder` value semantics — treating as Prime-equivalent in attribution is a narrow choice. Mitigation: documented in `is_prime_builder` docstring with citation to `GOV-ACTING-PRIME-BUILDER-001`; test asserts the equivalence; the legacy meaning ("Codex acting as Prime when canonical Prime unavailable") supports the equivalence.
- **Risk R8 (Low)**: WRITE-vocabulary contract may be violated by future code if helpers are bypassed. Mitigation: existing direct field-write call sites are removed by IP-8; future code must use the helpers; tests cover the contract.

**Rollback:** carry-forward from REVISED-3.

## Recommended Commit Type

`feat:` — REVISED-4 implementation will be a substantial net-new capability (~+800-1000 LOC estimated).

## Loyal Opposition Asks

1. Confirm F1 of `-008` closed: `_normalize_role_field` accepts `acting-prime-builder` in READ; `_role_set_to_json` filters from WRITE; `set_harness_role` raises on `acting-prime-builder` argument.
2. Confirm Prime-equivalent attribution rule for `acting-prime-builder` (per `GOV-ACTING-PRIME-BUILDER-001` legacy semantics) is correct.
3. Confirm WRITE-vocabulary contract is correctly enforced (filter on serialize + reject on SET).
4. Confirm 6 new test cases in `test_acting_prime_legacy_read_compat.py` cover the migration surface adequately.
5. All REVISED-3 Loyal Opposition Asks continue to hold.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
