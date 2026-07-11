NEW

# Defect-Fix Proposal - Startup-input gate re-arms after mid-turn AskUserQuestion, wedging Prime write tools

bridge_kind: prime_proposal
Document: gtkb-wi5118-startup-gate-fresh-start-only
Version: 001
Date: 2026-07-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex system runtime context plus explicit session document


Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-20260710
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5118

target_paths: ["scripts/workstream_focus.py", "scripts/session_self_initialization.py", ".codex/gtkb-hooks/session_start_dispatch.py", ".claude/hooks/session_start_dispatch.py", "platform_tests/hooks/test_workstream_focus.py", "platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Repair the startup-input gate so it arms only for a genuinely fresh interactive
session and, once owner input has satisfied it, cannot re-arm during that
session. Treat AskUserQuestion completion as owner input without retaining any
owner prompt or answer content in lifecycle state.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-STARTUP-GATE-FRESH-START-ONLY-001`
defines the fresh-session, AUQ, continuation, parity, and privacy behavior in
enough detail to implement and verify this repair. No new specification or
owner decision is needed beyond the active PAUTH.

## Defect / Reproduction

1. In the WI-5118 Prime Builder reproduction, a mid-session AskUserQuestion
   round trip left `startup_response_pending` true because clearing occurs only
   on the UserPromptSubmit path. Subsequent protected tool use was blocked by
   `GTKB-STARTUP-INPUT-GATE` until an unrelated plain owner message arrived.
2. A second 2026-07-10 Loyal Opposition occurrence blocked `gt backlog add` in
   a contiguous session after AUQ round trips, demonstrating that the defect is
   not Prime-only.
3. Current state records `startup_prompt_preview` in the lifecycle guard. That
   violates the approved DCL's privacy boundary even where the visible gate
   behavior is otherwise correct.

The repair must retain the fresh-session disclosure gate and must fail safely
for stale or mismatched continuation state without relying on a timeout as the
normal recovery path.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/workstream_focus.py`, `scripts/session_self_initialization.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `.claude/hooks/session_start_dispatch.py`, `platform_tests/hooks/test_workstream_focus.py`, `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`.

## Specification Links

- `DCL-STARTUP-GATE-FRESH-START-ONLY-001` - fixes fresh-session-only arming,
  monotonic satisfaction, AUQ behavior, cross-harness parity, and the privacy
  boundary for gate state.
- `GOV-SESSION-SELF-INITIALIZATION-001`,
  `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`, and
  `SPEC-CODEX-STARTUP-INPUT-GATE-TRIGGER-001` - retain required disclosure and
  the legitimate fresh-start gate.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` - keep mid-session init and role paths from
  creating a new startup gate.
- `ADR-CROSS-HARNESS-PARITY-001` - requires equivalent PB and LO behavior over
  supported interactive harness paths or an explicit waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires this proposal to state
  the applicable harness disposition rather than leaving hook-surface parity
  implicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - preserve PAUTH,
  bridge, and claim gates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires regression
  evidence for every specified state transition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve formal owner-requirement
  lineage through the approved DCL, WI, PAUTH, bridge, tests, and verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `GOV-STANDING-BACKLOG-001` - keep the repair within GT-KB and extend the
  existing defect rather than create duplicate standing work.

## Prior Deliberations

- `DELIB-202666076` - owner approval for the bounded WI-5118 implementation
  authorization.
- `DELIB-202666019` - WI-5083 verification, which fixed continuation re-arming
  but leaves the AUQ path as the subsequent defect.
- `DELIB-202665704` - mid-session role-switch review evidence relevant to the
  no-rearm invariant.
- `DELIB-1531` - Loyal Opposition startup symmetry evidence.

## Owner Decisions / Input

- `DELIB-202666076` - owner approved implementation within the stated gate and
  privacy boundaries.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5118-STARTUP-GATE-20260710` - active
  PAUTH; protected changes still require independent LO GO, claim, and
  implementation-start evidence.

## Proposed Scope

1. Model gate state explicitly as fresh-session pending or satisfied for its
   session context; never re-arm a satisfied context on AUQ completion,
   repeated AUQ, resume, compaction, mid-session init, or mid-session role
   change.
2. Route AUQ completion through the same bounded clear/acknowledge behavior as
   an owner follow-up, without retaining the prompt or answer body.
3. Preserve the genuine fresh-session path: it emits disclosure, blocks
   non-exempt use until owner input, and re-arms only for a distinct context.
4. Remove `startup_prompt_preview` and any equivalent prompt or AUQ-content
   persistence from lifecycle state. Retain only non-content lifecycle events
   and clear reasons needed for audit.
5. Keep applicable Codex and Claude hook paths behaviorally aligned and add
   focused parity coverage; do not edit dispatcher configuration or bypass
   bridge governance.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Genuine fresh session | Assert initial fresh context arms and blocks non-exempt use until an owner input event. |
| Ordinary follow-up | Assert a normal owner follow-up clears the gate. |
| AUQ completion | Assert an AUQ answer clears a pending gate without a second plain prompt. |
| Repeated AUQ | Assert successive AUQ round trips do not re-arm a satisfied state. |
| Continuations | Assert resume and compaction preserve satisfied state. |
| Mid-session init/role | Assert those paths do not create a new fresh-start await. |
| Fresh reset | Assert a distinct session context re-arms the required gate. |
| PB/LO parity | Exercise applicable Codex and Claude hook/state paths or emit the typed parity-waiver evidence required by the ADR. |
| Privacy | Assert lifecycle state omits prompt previews and AUQ-answer content while retaining allowed clear reasons. |

## Cross-Harness Disposition

No owner waiver is requested.

| Harness / path | Disposition | Evidence |
| --- | --- | --- |
| Codex A | Behavioral parity required. The `.codex/gtkb-hooks/session_start_dispatch.py` path and shared lifecycle reader must honor the same fresh-only, AUQ-clearing, and no-content-retention contract. | Focused Codex hook/state fixtures plus the shared regression suite. |
| Claude B | Behavioral parity required. The `.claude/hooks/session_start_dispatch.py` path and shared lifecycle reader must honor the identical contract for Prime Builder and Loyal Opposition sessions. | Focused Claude hook/state fixtures plus the shared regression suite. |
| Shared interactive core | Behavioral parity required. `scripts/workstream_focus.py` and `scripts/session_self_initialization.py` provide the common transition semantics consumed by supported surfaces. | `test_cross_harness_protocol_parity.py` and direct state-transition coverage. |
| Other supported harnesses | No native hook registration is changed in this slice. Their common-core behavior remains covered by the shared transition contract; any native-path discrepancy discovered during verification is a NO-GO unless an owner-approved typed waiver is obtained. | Existing parity assertions plus the shared regression outcome. |

## Acceptance Criteria

- The specified AUQ, repeated-AUQ, continuation, role/init, and fresh-session
  behaviors all pass in focused regression coverage.
- Non-exempt tool use cannot be wedged mid-session by a satisfied gate.
- A truly fresh session remains protected until owner input arrives.
- Gate state contains no owner prompt, prompt preview, or AUQ-answer content.
- Supported PB and LO paths exhibit equivalent behavior or a documented,
  approved parity waiver.

## Risks / Rollback

- Risk: clearing too broadly could weaken fresh-session protection. Mitigation:
  key satisfaction to a validated session context and test a distinct fresh
  context separately.
- Risk: duplicate hook logic diverges across harnesses. Mitigation: keep the
  same small state-transition contract and lock it with parity tests.
- Risk: retaining legacy previews after behavior changes leaks owner content.
  Mitigation: remove all preview writes and assert state serialization has no
  content-bearing fields.
- Rollback: restore only the prior state-transition implementation if a
  regression appears, never restore content retention; the change requires no
  schema migration or dispatcher-state change.
- Filing uses the next numbered bridge file under `bridge/` and remains
  append-only; no prior bridge file is rewritten or deleted.

## Files Expected To Change

- `scripts/workstream_focus.py`
- `scripts/session_self_initialization.py`
- `.codex/gtkb-hooks/session_start_dispatch.py`
- `.claude/hooks/session_start_dispatch.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`

## Recommended Commit Type

`fix`
