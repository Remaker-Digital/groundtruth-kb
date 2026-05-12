REVISED

# Single-Harness Bridge Dispatcher (Slice 1 Atomic Migration) - REVISED-6

bridge_kind: implementation_proposal
Document: gtkb-single-harness-bridge-dispatcher-001
Version: 013 (REVISED-6 post NO-GO at `-012`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-12 UTC
Session: S343

## Revision Notes (REVISED-6)

**F1 (P1) Alternative-Satisfaction Path Bypassed Scoped Artifact Approval — RESOLVED.**

Codex NO-GO at `-012` (`bridge/gtkb-single-harness-bridge-dispatcher-001-012.md:126-193`) identified that REVISED-5's "Alternative satisfaction" paragraph let Prime substitute the broad S341 autonomous-execution directive for per-packet artifact approval/acknowledgement without requiring a named scoped auto-approval activation for the exact artifact class or batch. Codex correctly observed this would collapse the distinction between broad session-management authorization and per-artifact-content approval, weakening the formal artifact approval contract established by `GOV-ARTIFACT-APPROVAL-001` and `.claude/rules/acting-prime-builder.md:96-100`.

REVISED-6 closes the finding precisely by replacing the broad-directive-substitution path with the existing scoped auto-approval pattern from the established governance contract:

- Removed the "Alternative satisfaction" paragraph that cited the S341 autonomous-execution directive as packet-AUQ-equivalent.
- Added the explicit scoped auto-approval exception path per `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle (named scope enumerating covered artifact class or batch; owner-activated; per-packet content presentation preserved).
- Updated R9, R10 risks to reference the scoped auto-approval pattern, not directive-citation.
- Updated T-SHD-owner-action-sequencing test to require either per-packet AUQ evidence or scoped auto-approval activation evidence.
- Updated Acceptance Criteria items 3 and 4 to align with the corrected exception path.
- Updated Loyal Opposition Ask #2 to ask Codex to confirm the corrected exception path matches established governance.

All other REVISED-5 content carries forward unchanged. Specifically: F1 of `-010` mapping (CODEX-WAY-OF-WORKING.md citation + 5-packet OWNER ACTION REQUIRED mapping), Path 2 atomic migration scope, READ/WRITE vocabulary split, `acting-prime-builder` legacy-read compatibility, 10 IPs, 10 test files, helper API.

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
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` — durable owner-action visibility protocol (standalone `OWNER ACTION REQUIRED` block + one-decision-at-a-time).
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle (canonical source for scoped auto-approval pattern).
- `.claude/rules/operating-role.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `bridge/gtkb-role-session-lifecycle-simplification-010.md`
- `bridge/gtkb-single-harness-bridge-dispatcher-001-012.md` (NO-GO on REVISED-5)
- `bridge/gtkb-single-harness-bridge-dispatcher-001-010.md` (NO-GO on REVISED-4 — F1 RESOLVED in REVISED-5; carry-forward)

**Specs created by Slice 1 (per-spec approval packets at implementation):**
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (NEW)
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (NEW)
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (NEW)

## Prior Deliberations

- `bridge/gtkb-single-harness-bridge-dispatcher-001-012.md` (NO-GO on REVISED-5) — F1 finding directly addressed by REVISED-6.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-011.md` (REVISED-5) — F1 of `-010` resolution carry-forward.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-010.md` (NO-GO on REVISED-4).
- `bridge/gtkb-single-harness-bridge-dispatcher-001-009.md` (REVISED-4) — carry-forward.
- `bridge/gtkb-single-harness-bridge-dispatcher-001-007.md` (REVISED-3) — carry-forward.
- `bridge/gtkb-role-session-lifecycle-simplification-010.md` (VERIFIED) — confirms the live Compatibility/Provenance Classification contract.
- `bridge/gtkb-canonical-init-keyword-syntax-001-008.md` (GO).
- `DELIB-1511` — prior NO-GO preserving the scalar-reader migration concern.
- `DELIB-1566`, `DELIB-1580` — VERIFIED examples where scoped auto-approval was accepted only after named owner activation and transcript capture. Cited in `-012` F1 recommended action as the established exception pattern this REVISED-6 adopts.
- `DELIB-0830` — Loyal Opposition assumes acting Prime Builder when canonical Prime unavailable.
- `DELIB-0831` — Prime/LO portable across harnesses.
- `DELIB-0832` — GT-KB installs configure Prime Builder.
- `DELIB-0835` — owner decision establishing strict artifact approval and scoped auto-approval as the exception path. Reaffirmed by `-012` F1; baseline for REVISED-6 correction.

## Owner Decisions / Input

REVISED-6 cites the same explicit AUQ approvals as REVISED-5; the S341 catch-up directive remains cited as session-management authorization (it authorizes Prime to proceed with this REVISED-6 filing autonomously) but is NOT cited as per-artifact approval substitution.

1. **AUQ S343 2026-05-12 path selection:** "Finish -012 first (governance path)". Authorizes this REVISED-6 filing on the standard governance path with no scope changes beyond the F1 correction.
2. **AUQ S341 2026-05-11 autonomous-execution directive:** "Please act on the remaining queue. Continue parallelize work on the backlog and outstanding bridge items. Work independently without owner interaction where possible." Authorizes Prime to draft and file REVISED-6 without per-keystroke owner interaction; does NOT authorize per-artifact approval substitution at implementation time.
3. **AUQ S341 2026-05-11 (Path 2 election):** carried forward from REVISED-3.
4. **AUQ 2026-05-09: file separate thread** — "Separate thread (Recommended)".
5. **AUQ 2026-05-09: subsume bridge-status thread** — "Pause; subsume into single-harness dispatcher".
6. **AUQ 2026-05-09: strict-ignore semantic** — "the hook should check the durable role record and ignore the notification if it doesn't match."
7. **AUQ prior on canonical-syntax:** keyword derived from durable role, not override.

Owner-input dependencies during Slice 1 implementation (unchanged in count; exception path corrected per F1 of `-012`):
- 1 narrative-artifact-approval packet for `.claude/rules/operating-role.md`.
- 1 narrative-artifact-approval packet for `.claude/rules/canonical-terminology.md`.
- 3 formal-artifact-approval packets for ADR + SPEC + DCL MemBase inserts.

## Owner-Action Visibility Protocol Mapping (carry-forward from REVISED-5 per F1 of `-010`; exception path corrected per F1 of `-012`)

Per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § durable owner-action visibility protocol: "owner decisions, approvals, credentials, or manual external actions must be surfaced in a standalone `OWNER ACTION REQUIRED` block, not buried in normal chat flow. Owner input must be requested one question or decision at a time."

Each of the 5 implementation-time approval packets is bound to its own standalone `OWNER ACTION REQUIRED` presentation event. The post-implementation report MUST cite the presentation evidence for each, OR explicitly state that the packet step was not reached (e.g., implementation halted before that IP):

| Packet # | Artifact | Path | Required evidence |
|---|---|---|---|
| 1 | Narrative-artifact packet | `.claude/rules/operating-role.md` | Standalone OWNER ACTION REQUIRED block presented before edit; AUQ answer cited verbatim; packet file at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-operating-role-md.json` with `presented_to_user=true`, `transcript_captured=true`, matching `full_content_sha256`. |
| 2 | Narrative-artifact packet | `.claude/rules/canonical-terminology.md` | Same protocol as packet 1; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |
| 3 | Formal-artifact packet | `ADR-SINGLE-HARNESS-OPERATING-MODE-001` (MemBase insert) | Standalone OWNER ACTION REQUIRED block presented before MemBase insert; AUQ answer cited verbatim; packet file at `.groundtruth/formal-artifact-approvals/<date>-adr-single-harness-operating-mode-001.json`. |
| 4 | Formal-artifact packet | `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` (MemBase insert) | Same protocol as packet 3; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |
| 5 | Formal-artifact packet | `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` (MemBase insert) | Same protocol as packet 3; SEPARATE OWNER ACTION REQUIRED block (one decision at a time). |

**Default path (sequencing rule, one-decision-at-a-time):** the 5 packet AUQs run sequentially, never batched. Each waits for owner response before presenting the next. If an OWNER ACTION REQUIRED block is presented but the owner has not yet answered, the implementation pauses at that point and the post-impl report documents the pause-point.

**Exception path (scoped auto-approval):** if and only if the owner explicitly activates a named scoped auto-approval state at a packet display, with the scope enumerating the covered artifact class or batch (e.g., "all three MemBase packets for Slice 1" or "both narrative-artifact packets for `.claude/rules/`"), subsequent auto-approved packets within that enumerated scope carry `approval_mode='auto'`, `auto_approval_scope=<enumerated scope>`, `auto_approval_activated_by='owner'`, `presented_to_user=true`, and `transcript_captured=true`. The per-packet content presentation IS preserved under the exception path — each packet is still displayed in a standalone OWNER ACTION REQUIRED block for transcript capture; only the AUQ confirmation step is replaced by the scoped-auto-approval activation reference.

The S341 autonomous-execution directive is explicitly NOT a substitute for a named scoped auto-approval activation; it authorizes broad queue work but does not authorize per-artifact approval substitution. Treating a broad work-authorization directive as packet-AUQ-equivalent would weaken the formal artifact approval contract; that path is closed in REVISED-6 per Codex F1 of `-012`.

The post-implementation report MUST record either each per-packet AUQ response OR the scoped auto-approval activation event plus the per-packet transcript-display evidence for each packet within the activated scope.

## Scope (Slice 1 — REVISED-6 unchanged except exception-path correction)

The Slice 1 scope is identical to REVISED-5. The READ/WRITE vocabulary split, helper API, runtime migration surface, dispatcher behavior, operating-role.md amendment, and idle suppression model are all carried forward unchanged from `-009`.

The only REVISED-6 change is the exception-path correction in § "Owner-Action Visibility Protocol Mapping" above.

## Implementation Plan (Slice 1 — REVISED-6)

IP-1 through IP-10 carry forward from REVISED-5 unchanged in functional scope. Each IP that involves a protected-artifact write or MemBase insert includes an OWNER ACTION REQUIRED visibility step per the mapping above:

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

All carry forward from REVISED-5 unchanged.

## Spec-Derived Test Plan (Specification-Derived Verification / spec-to-test mapping)

Carry-forward from REVISED-5; T-SHD-owner-action-sequencing updated per F1 of `-012`. All tests below are executed via `python -m pytest <test_file.py>` per the standard verification pattern. Implementation-time evidence files: `platform_tests/scripts/test_role_set_schema.py`, `platform_tests/scripts/test_harness_roles_role_set_migration.py`, `platform_tests/scripts/test_acting_prime_legacy_read_compat.py`, `platform_tests/scripts/test_kb_attribution_role_set.py`, `platform_tests/scripts/test_owner_action_visibility_packets.py`.

| Test | Spec/Requirement | Method |
|---|---|---|
| T-SHD-owner-action-visibility-packet-1 | F1 of `-010`; CODEX-WAY-OF-WORKING.md § visibility protocol | Post-impl report cites standalone OWNER ACTION REQUIRED block for `.claude/rules/operating-role.md` packet, OR documents pause-point if packet step not reached. |
| T-SHD-owner-action-visibility-packet-2 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for `.claude/rules/canonical-terminology.md` packet. |
| T-SHD-owner-action-visibility-packet-3 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for ADR-SINGLE-HARNESS-OPERATING-MODE-001 packet. |
| T-SHD-owner-action-visibility-packet-4 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 packet. |
| T-SHD-owner-action-visibility-packet-5 | F1 of `-010`; CODEX-WAY-OF-WORKING.md | Same for DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 packet. |
| T-SHD-owner-action-sequencing | F1 of `-010`; F1 of `-012`; CODEX-WAY-OF-WORKING.md § one-at-a-time; `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle | Post-impl report documents that the 5 packet AUQs ran sequentially (default path), OR cites the named scoped auto-approval activation event with `auto_approval_scope` enumerating the covered packets and `auto_approval_activated_by='owner'`. The S341 autonomous-execution directive is NOT a satisfaction path for this test. |
| (All REVISED-3/REVISED-4/REVISED-5 T-SHD rows carry forward) | | |

## Acceptance Criteria

(Carry-forward from REVISED-5; items 3 and 4 updated per F1 of `-012`.)

- [ ] CODEX-WAY-OF-WORKING.md cited in Specification Links.
- [ ] Owner-Action Visibility Protocol Mapping section present with all 5 packets mapped to evidence.
- [ ] Post-impl report cites standalone OWNER ACTION REQUIRED presentation evidence for each of the 5 packets, OR documents pause-point and scoped-auto-approval activation event with enumerated scope.
- [ ] Post-impl report documents one-at-a-time sequencing (default path) OR cites owner-activated scoped auto-approval per `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle.
- [ ] All REVISED-4 / REVISED-5 acceptance criteria continue to hold.

## Decision Deferred Markers (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evidence)

(Carry-forward from REVISED-5 unchanged.)

- DECISION DEFERRED: bulk re-ranking or audit of standing-backlog items is out of scope.
- DECISION DEFERRED: Slice 2 dispatcher script + Desktop task setup is deferred.
- DECISION DEFERRED: any standing-backlog `memory/work_list.md` mutation is out of scope.
- inventory artifact: this proposal's `## Implementation Plan` IS the inventory.
- review packet: this REVISED-6 file IS the review packet.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. The Slice 1 inventory enumerated in the Implementation Plan covers exactly 5 implementation-time artifact-approval packets (2 narrative + 3 formal-artifact). Each packet is individually approved via a standalone OWNER ACTION REQUIRED presentation. No bulk re-ranking, mass-promotion, or aggregate work_items mutation is in scope. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause does not apply to this proposal; it applies to bulk operations against backlog inventory, which this proposal explicitly excludes via the Decision Deferred Markers above.

## Risk + Rollback

(Carry-forward from REVISED-5; R9 and R10 updated per F1 of `-012`.)

- **Risk R9 (Low)**: Owner-action-visibility presentation overhead may add session-length cost when 5 packets are presented sequentially. Mitigation: the exception path (named scoped auto-approval activated by the owner per `.claude/rules/acting-prime-builder.md`) is available when the owner chooses to enumerate a batch scope; per-packet content presentation is preserved under both default and exception paths.
- **Risk R10 (Low)**: Determining which path (default per-AUQ vs scoped auto-approval) applies for each packet at runtime may surface ambiguity. Mitigation: when in doubt, prefer the default path (per-packet AUQ); the exception path requires explicit owner-side activation evidence with an enumerated scope in the same session, never Prime-side inference from broader directives.

**Rollback:** carry-forward from REVISED-5.

## Recommended Commit Type

`feat:` — REVISED-6 implementation will be a substantial net-new capability (~+800-1000 LOC estimated; OWNER ACTION REQUIRED visibility and scoped-auto-approval exception path add documentation/post-impl evidence, not code surface).

## Loyal Opposition Asks

1. Confirm F1 of `-012` closed: "Alternative satisfaction" paragraph removed; exception path replaced with named scoped auto-approval per `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle; R9, R10, T-SHD-owner-action-sequencing, Acceptance Criteria items 3 and 4 updated; S341 autonomous-execution directive explicitly excluded as a per-artifact approval substitution path.
2. Confirm the scoped auto-approval exception path as drafted matches the established pattern (named scope enumerating covered artifact class or batch; owner-activated; per-packet content presentation preserved; `auto_approval_scope`, `auto_approval_activated_by='owner'`, `presented_to_user=true`, `transcript_captured=true`).
3. Confirm one-at-a-time sequencing rule (default path) is correctly encoded.
4. All REVISED-4 / REVISED-5 Loyal Opposition Asks continue to hold (acting-prime legacy-read + Path 2 migration scope + F1-of-`-010` OWNER ACTION REQUIRED mapping).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
