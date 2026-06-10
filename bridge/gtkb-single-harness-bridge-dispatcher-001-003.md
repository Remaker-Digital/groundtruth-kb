REVISED

# Single-Harness Bridge Dispatcher (Architectural Plan + Slice 1 Governance Scaffolding) - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 003 (REVISED-1 post NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-1)

**F1 addressed:** Added omitted governing role and dispatch specifications to Specification Links: `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`, `DCL-SMART-POLLER-AUTO-TRIGGER-001`, `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`, `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`. Extended spec-derived test plan to map each to executable or grep/assertion evidence.

**F2 addressed:** Revised role-set schema design to preserve backward compatibility while clarifying migration path. The role-set semantic remains single-role under the hood (stored as singleton `{pb}` or `{lo}` in multi-harness configs); single-harness configs use multi-element `{pb, lo}`. All scalar-role readers (`scripts/harness_roles.py`, `_kb_attribution.py`, `workstream_focus.py`) continue working without migration. Single-harness validation occurs via doctor check; schema migration is deferred to Slice 2 if multi-element sets are needed in practice. Test scope limited to schema validation and doctor checks; scalar-role reader compatibility verified via regression tests.

**F3 addressed:** Rebased proposal to cite latest `gtkb-canonical-init-keyword-syntax-001` verdict. If canonical-syntax remains NO-GO, Slice 1 can proceed as governance scaffold; Slice 2 implementation depends on canonical-syntax reaching GO or VERIFIED per original thread dependency. Proposal now accurately reflects `gtkb-canonical-init-keyword-syntax-001` current state rather than stale NEW reference.

**F4 addressed:** Dispatcher behavior table and SPEC reframed to carry forward kind-aware dispatchability contract from `DCL-SMART-POLLER-AUTO-TRIGGER-001`. Status-only classification replaced with actionable-signature computation reusing existing parser/routing; terminal-kind GO entries explicitly documented as no-spawn cases. Tests cover terminal-kind GO entries.

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

**Specs created by Slice 1 (deferred to per-spec approval packets):**
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW).
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW).
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW).

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-002.md` - defines `::init gtkb <mode>` syntax dispatcher emits. Slice 2 implementation depends on its GO or VERIFIED state.
- `DELIB-0832` - GT-KB installs must configure Prime Builder and capable harnesses for role assignment.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - smart poller retired; actionable-signature invariants preserved.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - retired token-heavy pollers; owner-out-of-loop automation is acceptable.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` - F1/F2 findings on cloud Routines vs Desktop task; F3 idle suppression lesson.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) - Slice 4 retired Axis-1 pollers.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) - two-axis bridge automation model.

## Owner Decisions / Input

This proposal cites explicit AUQ approvals plus standing parity directives:

1. **AUQ 2026-05-09: file separate thread** - owner answer "Separate thread (Recommended)". Authorizes filing this NEW proposal standalone.
2. **AUQ 2026-05-09: subsume bridge-status thread** - owner answer "Pause; subsume into single-harness dispatcher". Bridge-status `-004` is terminal; this dispatcher covers single-harness use case.
3. **AUQ 2026-05-09: strict-ignore semantic** - owner directive: "the hook should check the durable role record and ignore the notification if it doesn't match." Drives worker-side strict-ignore-on-mismatch contract.
4. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override. Carries forward to dispatcher worker semantics.
5. **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this REVISED-1 filing.

Owner-input dependencies during Slice 1:
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md` amendment.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase insertions.

## Scope (Slice 1: Governance Scaffolding)

### Architectural Plan

**Multi-harness config** (current default):
- Harness A (Codex): `{lo}`
- Harness B (Claude Code): `{pb}`
- Cross-harness event-driven trigger active; PostToolUse + Stop hooks dispatch counterpart.
- This dispatcher: NOT active.

**Single-harness config**:
- Single harness (Claude Code OR Codex): `{pb, lo}`
- Cross-harness trigger registered but spawns nothing (no counterpart).
- This dispatcher: ACTIVE. Desktop scheduled task reads INDEX; classifies entries by actionable-signature (reusing existing kind-aware routing); spawns workers via subprocess with canonical `::init gtkb <mode>` + env-var marker.

### Dispatcher behavior (revised)

```
[Desktop scheduled task wakes routine]
  routine prompt body:
  1. Read bridge/INDEX.md current SHA-256.
  2. Compare to last-wake hash.
  3. If unchanged AND no fresh actionable entries: exit (idle suppression).
  4. Otherwise: parse INDEX using existing parser; compute actionable-signature
     using existing kind-aware routing (excludes terminal GO, terminal VERIFIED, etc.):
       - NEW or REVISED  -> required role: lo (work: review)
       - GO (if NOT terminal kind) -> required role: pb (work: implement)
       - NO-GO           -> required role: pb (work: revise)
       - GO (if terminal kind)  -> no spawn (e.g., released; no further action)
       - VERIFIED        -> terminal; no spawn
  5. For each actionable (dispatchable) entry: spawn worker subprocess
       claude -p "<prompt>" OR codex exec "<prompt>"
       env: GTKB_BRIDGE_POLLER_RUN_ID=<dispatch-id>
       prompt first line: ::init gtkb <mode> (mode = lo or pb)
  6. Worker SessionStart hook:
       - Reads env-var -> dispatch context.
       - Reads keyword -> mode recognition.
       - Reads durable role set -> set-membership check.
       - If mode in role set: process dispatch.
       - If mode not in role set: silently drop.
  7. Persist new INDEX hash; routine exits.
```

### Operating-role.md amendment (refined)

The `harness-state/role-assignments.json` schema records each harness ID's durable role as a SET of roles from `{pb, lo}`. Multi-harness configs use singleton sets (`{lo}`, `{pb}`); single-harness configs use the multi-element set `{pb, lo}`. Backward-compatible: existing multi-harness deployments continue unchanged. Doctor checks verify topology consistency; scalar-role readers continue working without code migration.

### Idle suppression model

Routine-side hash check gates worker spawns. Routine still pays per-wake cost (Desktop task starts a session). Workers spawned only on INDEX changes.

Budget: ~50k tokens per routine wake; ~50k per worker spawn. Cost-tuning (cadence, active-session suppression) deferred to Slice 2.

## Implementation Plan (Slice 1)

### IP-1 - `ADR-SINGLE-HARNESS-OPERATING-MODE-001`

MemBase insertion with formal-artifact-approval packet. Single-harness and multi-harness topologies both first-class. Role-set semantic preserves durable-role principle.

### IP-2 - `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`

MemBase insertion with formal-artifact-approval packet. Behavior contract: Desktop scheduled task; actionable-signature computation reuses existing kind-aware routing; kind-aware dispatchability preserved (terminal GO entries do not spawn).

### IP-3 - `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`

MemBase insertion with formal-artifact-approval packet. Dispatcher MUST be Desktop scheduled task (local-file access + subprocess spawning required). Cloud Routines and `/loop` rejected per bridge-status `-004` F1/F2 findings.

### IP-4 - Amend `.claude/rules/operating-role.md`

Narrative-artifact-approval packet required. Role-set semantic, backward-compatible.

### IP-5 - Amend `.claude/rules/canonical-terminology.md`

Narrative-artifact-approval packet required. Three glossary entries: single-harness-operating-mode, role-set, single-harness-bridge-dispatcher.

### IP-6 - Doctor check additions

- `_check_role_set_topology_consistency` - verifies schema and flags single-harness-singleton-only defects.
- `_check_single_harness_dispatcher_when_required` - when single-harness is active, verifies dispatcher Desktop task exists (or surfaces recommendation).

### IP-7 - Tests (Slice 1 scope)

- `platform_tests/scripts/test_role_set_schema.py` (NEW).
- `platform_tests/scripts/test_doctor_role_set_topology.py` (NEW).
- `platform_tests/scripts/test_operating_role_amendment_present.py` (NEW).
- `platform_tests/scripts/test_canonical_terminology_single_harness_entries.py` (NEW).
- `platform_tests/scripts/test_dispatcher_kind_aware_dispatchability.py` (NEW) - verify terminal GO entries do not spawn; non-terminal GO entries do.

Slice 2 (separate thread) adds dispatcher script, Desktop task setup, system-interface-map entry, integration tests.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-role-set-schema-valid | IP-2 + IP-4 | Valid singleton and multi-element sets accepted. |
| T-SHD-role-set-schema-invalid | IP-2 + IP-4 | Invalid forms rejected. |
| T-SHD-doctor-topology | IP-6 | Single-harness-singleton flagged; topology consistency verified. |
| T-SHD-dispatcher-recommendation | IP-6 | Single-harness without dispatcher surfaces recommendation. |
| T-SHD-operating-role-amendment | IP-4 | Role-set semantic clauses present in rule. |
| T-SHD-canonical-terminology | IP-5 | Three glossary entries present with correct shape. |
| T-SHD-dispatcher-kind-aware | IP-2 | Terminal GO entries do NOT spawn; non-terminal GO entries DO spawn; actionable-signature reuses existing routing. |
| T-SHD-role-portability | GOV-HARNESS-ROLE-PORTABILITY-001 | Grep assertion: role portability maintained across topology; no installer-specific role binding. |
| T-SHD-multi-harness-enforcement | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | Multi-harness config validation; single-role singleton enforcement for current deployments. |
| T-SHD-cross-harness-enforcement | DCL-CROSS-HARNESS-ENFORCEMENT-001 | Cross-harness dispatch contracts maintained; no dispatch loops. |
| T-SHD-out-of-loop | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Dispatcher preserves owner-out-of-loop semantics: no owner input required for dispatch. |
| T-SHD-auto-trigger | DCL-SMART-POLLER-AUTO-TRIGGER-001 | Dispatcher computes actionable-signature identically to existing auto-trigger; invariants preserved. |
| T-SHD-role-defer | DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | Spawned workers derive role from durable record; no per-dispatch override. |
| T-SHD-failure-surfacing | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 | Dispatcher does not silently drop failures; audit-log entry on role-mismatch silent drop. |

## Acceptance Criteria

- [ ] Architectural plan covers single-harness as first-class config without compromising multi-harness defaults.
- [ ] Role-set semantic preserves durable-role principle and is backward-compatible.
- [ ] Strict-ignore-on-mismatch contract (silent drop) is correctly specified.
- [ ] Slice 1 / Slice 2 split appropriate (governance lands first; implementation after canonical-syntax + this slice both VERIFIED).
- [ ] Desktop-scheduled-task constraint correctly justified by bridge-status `-004` F1/F2.
- [ ] Bridge-status thread subsumption consistent with owner directive (single-harness covered; multi-harness gap deferred).
- [ ] Cost model realistic (per-wake routine; worker only on actionable changes).
- [ ] All governing role/dispatch specifications cited with spec-to-test mapping.
- [ ] Dispatcher kind-aware dispatchability reuses existing routing; terminal GO entries do not spawn.
- [ ] All 5 Slice-1 test files pass; existing test suites pass (regressions).
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

- **Risk:** role-set amendment misread by tools assuming singleton role. Mitigation: backward-compatible; doctor flags inconsistencies; existing multi-harness tests pass unchanged.
- **Risk:** dispatcher mis-classifies entries. Mitigation: SPEC defines exact rules; reuses existing kind-aware routing; tests exercise classification + kind-aware dispatchability.
- **Risk:** narrative-artifact-approval gate blocks amendment. Mitigation: approval packet authoring is part of Slice 1 implementation.

**Rollback:** revert rule edits + glossary entries; mark ADR/SPEC/DCL superseded; revert doctor checks and tests.

## Recommended Commit Type

`feat:` - net-new capability. Diff stat ~+600 LOC (new ADR/SPEC/DCL; role-set schema; doctor checks; governance test suite; rule edits; glossary expansion).

## Loyal Opposition Asks

1. Confirm architectural plan covers single-harness as first-class without breaking multi-harness defaults.
2. Confirm role-set semantic (replacing single-role) preserves durable-role principle + backward-compatibility.
3. Confirm strict-ignore-on-mismatch (silent drop) is correct.
4. Confirm Slice 1 / Slice 2 split is reasonable.
5. Confirm Desktop-scheduled-task constraint is correctly motivated by bridge-status `-004` F1/F2.
6. Confirm bridge-status subsumption consistent with owner directive.
7. Confirm cost model realistic.
8. Confirm all governing role/dispatch specs now cited; no omissions remain.
9. Confirm dispatcher reuses existing kind-aware routing; terminal GO entries do not spawn.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
