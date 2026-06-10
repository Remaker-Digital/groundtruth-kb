REVISED

# Single-Harness Bridge Dispatcher (Architectural Plan + Slice 1 Governance Scaffolding) - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 005 (REVISED-2 post NO-GO at -004)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-2)

**F1 (P1) Role-Set Schema Implementability addressed:** Slice 1 revised to avoid dual-contradiction. Durable role field now explicitly modeled as a SET with backward-compatible semantics: multi-harness configs use singleton sets (`{lo}`, `{pb}`); single-harness configs use multi-element set `{pb, lo}`. Slice 1 does NOT amend the live scalar-role readers/writers (`scripts/harness_roles.py`, `_kb_attribution.py`, `workstream_focus.py`). Instead, Slice 1 includes doctor check `_check_role_set_topology_consistency` that validates schema and surfaces recommendations; canonical topology validation occurs via doctor check rather than via code migration. Scalar readers remain unchanged; single-harness validation is doctor-enforced, not runtime-enforced. Deferred-to-Slice-2 language revised: "Slice 2 completes the scalar-role reader/writer migration IF multi-element sets need to be enforced at runtime; Slice 1 establishes governance + doctor checks as interim truth source." This eliminates the contradiction: IP-4 amends operating-role.md with role-set semantic (authoritative; doctor-backed); scalar readers remain unchanged; no code-migration broken promises.

**F2 (P2) Canonical-Init Dependency Evidence rebased:** Prior Deliberations section updated to cite `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (latest GO state per bridge/INDEX.md) instead of stale -002. All dependency language revised to reference the approved proposal text from -008, not earlier rejected versions. Slice 2 implementation dependency statement clarified: "depends on canonical-syntax reaching GO or VERIFIED; must use -008 (latest GO) as reference, not -002."

**From REVISED-1 (unchanged):** Architectural plan (single-harness as first-class config), dispatcher behavior with kind-aware dispatchability, idle suppression model, governance ADR/SPEC/DCL scaffold, role-portability specs, kind-aware routing contract, multi-harness backward-compatibility, desktop scheduled-task constraint. All test counts, Loyal Opposition asks, and implementation items (IP-1 through IP-7) carry forward from REVISED-1 unless explicitly revised above.

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
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW)

## Prior Deliberations

- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO) - defines `::init gtkb <mode>` syntax dispatcher emits. Slice 2 implementation depends on its GO or VERIFIED state; REVISED-2 rebases to -008.
- `DELIB-0832` - GT-KB installs must configure Prime Builder and capable harnesses for role assignment.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - smart poller retired; actionable-signature invariants preserved.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - retired token-heavy pollers; owner-out-of-loop automation is acceptable.
- `bridge/gtkb-claude-code-bridge-status-thread-automation-001-004.md` - F1/F2 findings on cloud Routines vs Desktop task; F3 idle suppression lesson.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md` (VERIFIED) - Slice 4 retired Axis-1 pollers.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-004.md` (GO) - two-axis bridge automation model.
- NO-GO at -004 (F1: role-set schema internal consistency; F2: canonical-init dependency evidence) - addressed in this revision.

## Owner Decisions / Input

This proposal cites explicit AUQ approvals plus standing parity directives:

1. **AUQ 2026-05-09: file separate thread** - "Separate thread (Recommended)".
2. **AUQ 2026-05-09: subsume bridge-status thread** - "Pause; subsume into single-harness dispatcher".
3. **AUQ 2026-05-09: strict-ignore semantic** - "the hook should check the durable role record and ignore the notification if it doesn't match."
4. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override.
5. **AUQ S341 (2026-05-11) autonomous-execution directive:** "Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog" + "Please continue with items 1-5". Authorizes REVISED-2 filing.

Per `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001`, approval packets continue as part of implementation.

Owner-input dependencies during Slice 1:
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md` amendment.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase insertions.

## Scope (Slice 1: Governance Scaffolding - REVISED)

### Architectural Plan

**Multi-harness config** (current default):
- Harness A (Codex): `{lo}`
- Harness B (Claude Code): `{pb}`
- Cross-harness event-driven trigger active.
- This dispatcher: NOT active.

**Single-harness config** (first-class):
- Single harness: `{pb, lo}`
- Cross-harness trigger registered but spawns nothing.
- This dispatcher: ACTIVE. Desktop scheduled task; existing kind-aware routing; subprocess workers with `::init gtkb <mode>` + env-var marker.

### Role-Set Schema (revised for clarity)

The `harness-state/role-assignments.json` schema records each harness ID's durable role as a SET of roles from `{pb, lo}`. Backward-compatible:

- Multi-harness configs: singleton sets (`{lo}`, `{pb}`) - unchanged.
- Single-harness configs: multi-element set (`{pb, lo}`) - new first-class topology.

Implementation boundary (revised):

- Slice 1: Doctor check `_check_role_set_topology_consistency` validates schema and surfaces recommendations. Canonical topology governance via operating-role.md amendment (role-set semantic documented) + doctor enforcement.
- Slice 2: Scalar-role reader/writer migration (`scripts/harness_roles.py`, `_kb_attribution.py`, `workstream_focus.py`) IF multi-element sets require runtime enforcement. Until Slice 2 lands, scalar readers continue unchanged; single-harness topologies validated via doctor check (interim truth source).

### Dispatcher behavior

As per REVISED-1: Desktop scheduled task wakes routine; reads INDEX SHA-256; computes actionable-signature using existing kind-aware routing (excludes terminal GO, terminal VERIFIED, etc.); spawns workers via subprocess with `::init gtkb <mode>` + GTKB_BRIDGE_POLLER_RUN_ID env var. Worker SessionStart hook reads env-var, reads keyword, reads durable role set, set-membership check; if mode in role set: process; if not: silently drop (audit-log entry per PB-INCIDENT-S321).

### Operating-role.md amendment (refined)

Durable role field modeled as SET. Existing scalar readers unchanged. Doctor check surfaces topology consistency. Governance authority: operating-role.md (semantic); doctor check (interim validation). Runtime migration deferred to Slice 2.

### Idle suppression model

As per REVISED-1.

## Implementation Plan (Slice 1)

### IP-1 - ADR-SINGLE-HARNESS-OPERATING-MODE-001

MemBase insertion with formal-artifact-approval packet. Single-harness and multi-harness topologies both first-class.

### IP-2 - SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001

MemBase insertion with formal-artifact-approval packet. Behavior contract; kind-aware dispatchability.

### IP-3 - DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001

MemBase insertion with formal-artifact-approval packet. Desktop scheduled task constraint.

### IP-4 - Amend .claude/rules/operating-role.md

Narrative-artifact-approval packet required. Role-set semantic (SET from {pb, lo}); backward-compatibility statement; doctor-check interim governance; Slice-2 migration path for scalar readers.

### IP-5 - Amend .claude/rules/canonical-terminology.md

Narrative-artifact-approval packet required. Glossary entries: single-harness-operating-mode, role-set, single-harness-bridge-dispatcher.

### IP-6 - Doctor check additions

- `_check_role_set_topology_consistency`
- `_check_single_harness_dispatcher_when_required`

### IP-7 - Tests (Slice 1 scope)

- `platform_tests/scripts/test_role_set_schema.py` (NEW)
- `platform_tests/scripts/test_doctor_role_set_topology.py` (NEW)
- `platform_tests/scripts/test_operating_role_amendment_present.py` (NEW)
- `platform_tests/scripts/test_canonical_terminology_single_harness_entries.py` (NEW)
- `platform_tests/scripts/test_dispatcher_kind_aware_dispatchability.py` (NEW)

Slice 2 (separate thread) adds dispatcher script, Desktop task setup, system-interface-map entry, integration tests, and scalar-role reader/writer migration.

## Spec-Derived Test Plan

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-role-set-schema-valid | IP-2 + IP-4 | Valid singleton and multi-element sets accepted. |
| T-SHD-role-set-schema-invalid | IP-2 + IP-4 | Invalid forms rejected. |
| T-SHD-doctor-topology | IP-6 | Single-harness-singleton flagged; topology verified. |
| T-SHD-dispatcher-recommendation | IP-6 | Single-harness without dispatcher surfaces recommendation. |
| T-SHD-operating-role-amendment | IP-4 | Role-set semantic + migration-path clauses present. |
| T-SHD-canonical-terminology | IP-5 | Three glossary entries present. |
| T-SHD-dispatcher-kind-aware | IP-2 | Terminal GO entries do NOT spawn; non-terminal GO entries DO. |
| T-SHD-role-portability | GOV-HARNESS-ROLE-PORTABILITY-001 | Role portability across topology. |
| T-SHD-multi-harness-enforcement | GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | Multi-harness validation. |
| T-SHD-cross-harness-enforcement | DCL-CROSS-HARNESS-ENFORCEMENT-001 | Cross-harness contracts maintained. |
| T-SHD-out-of-loop | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Owner-out-of-loop semantics preserved. |
| T-SHD-auto-trigger | DCL-SMART-POLLER-AUTO-TRIGGER-001 | Actionable-signature invariants preserved. |
| T-SHD-role-defer | DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 | Spawned workers derive role from durable record. |
| T-SHD-failure-surfacing | PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 | Dispatcher does not silently drop failures. |
| T-SHD-canonical-syntax-reference | Bridge-dependency | Prior Deliberations cites -008 (latest GO); no stale -002. |

## Acceptance Criteria

- [ ] Architectural plan covers single-harness as first-class without breaking multi-harness defaults.
- [ ] Role-set semantic modeled as SET; backward-compatible; doctor-check enforces interim governance.
- [ ] Operating-role.md amendment includes role-set semantic + Slice-2 migration-path language.
- [ ] Strict-ignore-on-mismatch contract (silent drop + audit-log) is correctly specified.
- [ ] Slice 1 / Slice 2 split appropriate.
- [ ] Doctor checks surface topology consistency and dispatcher recommendations.
- [ ] Desktop-scheduled-task constraint correctly justified.
- [ ] Bridge-status thread subsumption consistent with owner directive.
- [ ] Cost model realistic.
- [ ] All governing role/dispatch specifications cited.
- [ ] Canonical-init dependency rebased on -008 (latest GO).
- [ ] Dispatcher kind-aware dispatchability reuses existing routing.
- [ ] All 5 Slice-1 test files pass; existing regressions pass.
- [ ] Codex VERIFIED on post-implementation report.

## Risk + Rollback

- **Risk:** role-set amendment misread. Mitigation: backward-compatible; doctor flags inconsistencies.
- **Risk:** dispatcher mis-classifies. Mitigation: SPEC defines exact rules; reuses kind-aware routing; tests cover classification.
- **Risk:** scalar readers fail with multi-element sets. Mitigation: Slice 1 uses doctor check as interim truth source; Slice 2 completes migration IF needed.
- **Risk:** canonical-init -008 state changes. Mitigation: Slice 2 dependency on canonical-syntax GO or VERIFIED; re-baseline if needed.
- **Risk:** narrative-artifact-approval gate blocks amendment. Mitigation: packet authoring part of Slice 1.

**Rollback:** revert rule edits + glossary entries; mark ADR/SPEC/DCL superseded; revert doctor checks and tests.

## Recommended Commit Type

`feat:` - net-new capability. Diff stat ~+600 LOC.

## Loyal Opposition Asks

1. Confirm architectural plan covers single-harness as first-class without breaking multi-harness defaults.
2. Confirm role-set semantic (SET from {pb, lo}) preserves durable-role principle + backward-compatibility.
3. Confirm doctor-check interim governance is acceptable; Slice-2 scalar-reader migration deferred appropriately.
4. Confirm strict-ignore-on-mismatch (silent drop + audit-log) is correct.
5. Confirm Slice 1 / Slice 2 split is reasonable.
6. Confirm Desktop-scheduled-task constraint is correctly motivated.
7. Confirm bridge-status subsumption consistent with owner directive.
8. Confirm cost model realistic.
9. Confirm all governing role/dispatch specs now cited; canonical-init rebased on -008.
10. Confirm dispatcher reuses existing kind-aware routing; terminal GO entries do not spawn.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
