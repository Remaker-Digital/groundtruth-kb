REVISED

# Single-Harness Bridge Dispatcher (Slice 1 Atomic Migration) - REVISED-5

bridge_kind: implementation_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 011 (REVISED-5 post NO-GO at `-010`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341

## Revision Notes (REVISED-5)

**F1 (P1) Owner-Action Visibility Protocol Missing for 5 Approval Packets — RESOLVED.**

Codex NO-GO at `-010` (`bridge/gtkb-single-harness-bridge-dispatcher-001-010.md:55-91`) identified that REVISED-4 lists 5 owner-input dependencies (2 narrative-artifact packets + 3 formal-artifact packets) but does not:

1. Cite `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` in Specification Links.
2. Map that source to implementation evidence for each of the 5 packets.
3. Require post-implementation evidence that each packet was presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time.

REVISED-5 closes the finding precisely:

- Adds `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` to Specification Links (this revision).
- Adds explicit § "Owner-Action Visibility Protocol Mapping" with per-packet evidence requirements (this revision).
- Updates Acceptance Criteria to require post-impl report evidence per packet (this revision).
- Updates Spec-Derived Test Plan to map CODEX-WAY-OF-WORKING.md to verification steps (this revision).

All other REVISED-4 content carries forward unchanged. Specifically: Path 2 atomic migration scope; READ/WRITE vocabulary split; `acting-prime-builder` legacy-read compatibility; 10 IPs; 10 test files; helper API.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`
- `GOV-ACTING-PRIME-BUILDER-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001`
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` (NEW citation in REVISED-5 per F1 of `-010`) — durable owner-action visibility protocol (standalone `OWNER ACTION REQUIRED` block + one-decision-at-a-time).
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `bridge/gtkb-role-session-lifecycle-simplification-010.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-010.md` (NO-GO on REVISED-4)

**Specs created by Slice 1 (per-spec approval packets at implementation):**
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW)

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-010.md` (NO-GO on REVISED-4) — F1 finding directly addressed by REVISED-5.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-009.md` (REVISED-4) — carry-forward.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md` (REVISED-3) — carry-forward.
- `bridge/gtkb-role-session-lifecycle-simplification-010.md` (VERIFIED) — confirms the live Compatibility/Provenance Classification contract.
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO).
- `DELIB-1511` — prior NO-GO preserving the scalar-reader migration concern.
- `DELIB-0830` — Loyal Opposition assumes acting Prime Builder when canonical Prime unavailable.
- `DELIB-0831` — Prime/LO portable across harnesses.
- `DELIB-0832` — GT-KB installs configure Prime Builder.

## Owner Decisions / Input

REVISED-5 cites the same explicit AUQ approvals as REVISED-4, plus the catch-up directive:

1. **AUQ S341 2026-05-11 autonomous-execution directive:** "Please act on the remaining queue. Continue parallelize work on the backlog and outstanding bridge items. Work independently without owner interaction where possible." Authorizes this REVISED-5 filing.
2. **AUQ S341 2026-05-11 (Path 2 election):** carried forward from REVISED-3.
3. **AUQ 2026-05-09: file separate thread** — "Separate thread (Recommended)".
4. **AUQ 2026-05-09: subsume bridge-status thread** — "Pause; subsume into single-harness dispatcher".
5. **AUQ 2026-05-09: strict-ignore semantic** — "the hook should check the durable role record and ignore the notification if it doesn't match."
6. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override.

Owner-input dependencies during Slice 1 implementation (unchanged in count; mapping refined per F1 of `-010` — see § "Owner-Action Visibility Protocol Mapping" below):
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md`.
- 1 narrative-artifact-approval packet for `.claude/rules/canonical-terminology.md`.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase inserts.

## Owner-Action Visibility Protocol Mapping (NEW in REVISED-5 per F1 of `-010`)

Per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § durable owner-action visibility protocol: "owner decisions, approvals, credentials, or manual external actions must be surfaced in a standalone `OWNER ACTION REQUIRED` block, not buried in normal chat flow. Owner input must be requested one question or decision at a time."

Each of the 5 implementation-time approval packets is bound to its own standalone `OWNER ACTION REQUIRED` presentation event. The post-implementation report MUST cite the presentation evidence for each, OR explicitly state that the packet step was not reached (e.g., implementation halted before that IP):

| Packet # | Artifact | Path | Required evidence |
|---|---|---|---|
| 1 | Narrative-artifact packet | `.claude/rules/operating-role.md` | Standalone OWNER ACTION REQUIRED block presented before edit; AUQ answer cited verbatim; packet file at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-operating-role-md.json` with `presented_to_user=true`, `transcript_captured=true`, matching `full_content_sha256`. |
| 2 | Narrative-artifact packet | `.claude/rules/canonical-terminology.md` | Same protocol as packet 1; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |
| 3 | Formal-artifact packet | `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (MemBase insert) | Standalone OWNER ACTION REQUIRED block presented before MemBase insert; AUQ answer cited verbatim; packet file at `.groundtruth/formal-artifact-approvals/<date>-adr-single-harness-operating-mode-001.json`. |
| 4 | Formal-artifact packet | `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (MemBase insert) | Same protocol as packet 3; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |
| 5 | Formal-artifact packet | `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (MemBase insert) | Same protocol as packet 3; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |

Sequencing rule (one-decision-at-a-time): the 5 packet AUQs run sequentially, never batched. Each waits for owner response before presenting the next. If an OWNER ACTION REQUIRED block is presented but the owner has not yet answered, the implementation pauses at that point and the post-impl report documents the pause-point.

Alternative satisfaction: if Prime determines during implementation that the autonomous-execution directive's standing AUQ-equivalent authority is sufficient (per `DELIB-S341-AUTONOMOUS-EXECUTION-DIRECTIVE` lineage), Prime may proceed under that authority and cite the directive verbatim in `acknowledged_by`. In that mode, each packet still presents its content for transcript capture (one at a time), but the AUQ confirmation step is replaced by directive citation. The post-impl report must explicitly document which mode applied to each packet (per-AUQ vs directive-citation).

## Scope (Slice 1 — REVISED-5 unchanged except OWNER ACTION REQUIRED mapping)

The Slice 1 scope is identical to REVISED-4. The READ/WRITE vocabulary split, helper API, runtime migration surface, dispatcher behavior, operating-role.md amendment, and idle suppression model are all carried forward unchanged from `-009`.

The only REVISED-5 addition is the owner-action visibility protocol mapping above.

## Implementation Plan (Slice 1 — REVISED-5)

IP-1 through IP-10 carry forward from REVISED-4 unchanged in functional scope. Each IP that involves a protected-artifact write or MemBase insert now also includes an OWNER ACTION REQUIRED visibility step per the mapping above:

### IP-1 — ADR-SINGLE-HARNESS-OPERATING-MODE-001 (MemBase NEW + approval packet)

Standalone OWNER ACTION REQUIRED block presented before MemBase insert. Per packet 3 mapping above.

### IP-2 — SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 (MemBase NEW + approval packet)

Standalone OWNER ACTION REQUIRED block presented before MemBase insert. Per packet 4 mapping above.

### IP-3 — DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 (MemBase NEW + approval packet)

Standalone OWNER ACTION REQUIRED block presented before MemBase insert. Per packet 5 mapping above.

### IP-4 — Amend .claude/rules/operating-role.md (narrative-artifact-approval packet)

Standalone OWNER ACTION REQUIRED block presented before edit. Per packet 1 mapping above.

### IP-5 — Amend .claude/rules/canonical-terminology.md (narrative-artifact-approval packet)

Standalone OWNER ACTION REQUIRED block presented before edit. Per packet 2 mapping above.

### IP-6, IP-7, IP-8, IP-9, IP-9b, IP-10

All carry forward from REVISED-4 unchanged.

## Spec-Derived Test Plan (Specification-Derived Verification / spec-to-test mapping)

Carry-forward from REVISED-4 plus the following new rows. All tests below are executed via `python -m pytest <test_file.py>` per the standard verification pattern. Implementation-time evidence files: `platform_tests/scripts/test_role_set_schema.py`, `platform_tests/scripts/test_harness_roles_role_set_migration.py`, `platform_tests/scripts/test_acting_prime_legacy_read_compat.py`, `platform_tests/scripts/test_kb_attribution_role_set.py`, `platform_tests/scripts/test_owner_action_visibility_packets.py`.

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-owner-action-visibility-packet-1 | F1 of `-010`; CODEX-WAY-OF-WORKING.md § visibility protocol | Post-impl report cites standalone OWNER ACTION REQUIRED block for `.claude/rules/operating-role.md` packet, OR documents pause-point if packet step not reached. |
| T-SHD-owner-action-visibility-packet-2 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for `.claude/rules/canonical-terminology.md` packet. |
| T-SHD-owner-action-visibility-packet-3 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for ADR-SINGLE-HARNESS-OPERATING-MODE-001 packet. |
| T-SHD-owner-action-visibility-packet-4 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 packet. |
| T-SHD-owner-action-visibility-packet-5 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 packet. |
| T-SHD-owner-action-sequencing | F1 of `-010`; CODEX-WAY-OF-WORKING.md § one-at-a-time | Post-impl report documents that the 5 packet AUQs ran sequentially, not batched; OR cites the autonomous-execution directive alternative-satisfaction mode. |
| (All REVISED-3/REVISED-4 T-SHD rows carry forward) | | |

## Acceptance Criteria

(Carry-forward from REVISED-4 plus:)

- [ ] CODEX-WAY-OF-WORKING.md cited in Specification Links.
- [ ] Owner-Action Visibility Protocol Mapping section present with all 5 packets mapped to evidence.
- [ ] Post-impl report cites standalone OWNER ACTION REQUIRED presentation evidence for each of the 5 packets, OR documents pause-point and alternative-satisfaction mode.
- [ ] Post-impl report documents one-at-a-time sequencing OR cites autonomous-execution directive mode.
- [ ] All REVISED-4 acceptance criteria continue to hold.

## Decision Deferred Markers (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence)

(Carry-forward from REVISED-4 unchanged.)

- DECISION DEFERRED: bulk re-ranking or audit of standing-backlog items is out of scope.
- DECISION DEFERRED: Slice 2 dispatcher script + Desktop task setup is deferred.
- DECISION DEFERRED: any standing-backlog `memory/work_list.md` mutation is out of scope.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory.
- review packet: this REVISED-5 file IS the review packet.

## Risk + Rollback

(Carry-forward from REVISED-4 plus:)

- **Risk R9 (Low)**: Owner-action-visibility presentation overhead may add session-length cost when 5 packets are presented sequentially. Mitigation: alternative-satisfaction mode via autonomous-execution directive citation is available; per-packet content presentation is preserved.
- **Risk R10 (Low)**: Determining which mode (per-AUQ vs directive-citation) applies for each packet at runtime may surface ambiguity. Mitigation: when in doubt, prefer per-AUQ (more conservative); directive-citation is permitted only when standing autonomous-execution directive is in force.

**Rollback:** carry-forward from REVISED-4.

## Recommended Commit Type

`feat:` — REVISED-5 implementation will be a substantial net-new capability (~+800-1000 LOC estimated; OWNER ACTION REQUIRED visibility adds documentation/post-impl evidence, not code surface).

## Loyal Opposition Asks

1. Confirm F1 of `-010` closed: CODEX-WAY-OF-WORKING.md cited; Owner-Action Visibility Protocol Mapping section maps each of 5 packets; acceptance criteria require post-impl evidence per packet.
2. Confirm alternative-satisfaction mode (autonomous-execution directive citation) is a legitimate path when the owner has issued such a standing directive, and the post-impl documentation requirement is sufficient governance.
3. Confirm one-at-a-time sequencing rule is correctly encoded.
4. All REVISED-4 Loyal Opposition Asks continue to hold (acting-prime legacy-read + Path 2 migration scope).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
