REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# WI-5269 Activity-Envelope Authority Validators - Foundation-Aware Revision

bridge_kind: prime_proposal
Document: gtkb-wi5269-activity-envelope-authority-validators
Version: 005
Responds to: bridge/gtkb-wi5269-activity-envelope-authority-validators-004.md
Revises: bridge/gtkb-wi5269-activity-envelope-authority-validators-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5269-ACTIVITY-ENVELOPE-AUTHORITY-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5269
Related Work Items: WI-5268, WI-5263, WI-5279, WI-5501
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "scripts/dispatch_blackbox_gate.py", "scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_dispatch_blackbox_gate.py", "platform_tests/scripts/test_implementation_authorization.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

## Revision Claim

Every version-004 blocking condition is accepted and re-evaluated against
current canonical state.

The foundation is no longer draft authority:

- `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` is independent
  `VERIFIED` and is atomically committed at
  `6262862c8852d4d94530a4074a3047f921e7164e`;
- all five approved foundation artifacts exist in MemBase at version 2,
  `status=specified`, each with one executable assertion;
- WI-5268 no longer falsely claims resolved completion. Its current
  `open/resolved` row accurately records terminal bridge v034 and preserves
  the explicit WI-5501 closure hold;
- the WI-5269 PAUTH is active, scoped only to WI-5269, permits
  bridge/metadata/source/test, cites the now-real foundation specifications,
  and forbids dispatcher mutation, destructive cleanup, Git push/history
  rewrite, release, deployment, credentials, and external systems.

This revision does not treat those facts as immediate source-mutation
authority. WI-5268 remains under a canonical `open/resolved` closure hold
until WI-5501 is terminal/finalized or the owner directs a truly exclusive
window. In addition, two WI-5269 targets are currently dirty from separately
owned work:

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`;
- `platform_tests/scripts/test_implementation_authorization.py`.

Implementation must stop until predecessor readiness is mechanically accepted
and every target is clean, unclaimed, and tied to a fresh reviewed baseline.
This revision requests review of the corrected plan only.

## Findings Addressed

### F1 - Foundation specifications were absent

Resolved. Fresh governed reads return version 2, `specified`, one assertion
each for:

- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`;
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`;
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`;
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`;
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`.

### F2 - WI-5268 was not terminal VERIFIED

Resolved at the bridge and commit layers by independent v034 and commit
`6262862c8852d4d94530a4074a3047f921e7164e`. The MemBase work-item row remains
deliberately nonterminal and accurate while WI-5501 governs final closure.
Implementation therefore remains fail-closed until that hold is cleared or
the operation-time dependency gate explicitly recognizes the committed
VERIFIED predecessor without contradicting the owner-selected ordering.

### F3 - Mechanical gates admitted missing foundation authority

The missing-authority state no longer exists. The future start transaction
must nevertheless re-read all five specs, foundation v034/commit identity,
WI-5268 state, active PAUTH, work-intent claim, exact targets, and project
dependency readiness at operation time. Any drift blocks mutation.

### F4 - WI-5268 falsely claimed resolution

Resolved. Current WI-5268 version 13 is `resolution_status=open`,
`stage=resolved`, links v029-v034, names v034 VERIFIED and its commit, and
states the WI-5501 closure condition without claiming completed work-item
resolution.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved v2 foundation now supplies canonical ordinary-worker,
worker-safe-packet, activity-envelope authority, worker-context facade, and
foundation-first requirements. This proposal implements validators derived
from those records; it creates no new authority and requests no exception.

## Proposed Scope

1. Model an ordinary worker mechanically as a session envelope with no
   initialized activity envelope.
2. Permit ordinary workers only mediated worker-safe packet access to
   black-box work context; deny direct internals and configuration mutation.
3. Permit an `ops` activity envelope to request black-box configuration
   mutation only through governed ops surfaces; do not grant direct internals
   mutation.
4. Permit a `build` activity envelope to request direct internals mutation
   only for an exact case carrying active bridge GO, matching PAUTH,
   same-session work-intent claim, schema-v3 implementation-start evidence,
   operation-time target authorization, and case-approved target paths.
5. Deny cross-authority substitution: ops cannot satisfy build internals
   authority, and build cannot silently satisfy ops configuration authority.
6. Wire the shared validator into the existing black-box and
   implementation-start paths without inspecting or mutating dispatcher
   configuration/runtime, TAFE state, harness role/identity state, or
   credentials.

## Hard Implementation-Start Gates

1. Foundation v034 remains `VERIFIED` and commit
   `6262862c8852d4d94530a4074a3047f921e7164e` remains its durable carrier.
2. All five foundation records remain v2 with their approved content and
   passing assertions.
3. WI-5268 predecessor readiness is accepted by the governed dependency/start
   surface without contradicting its current WI-5501 closure hold. A narrative
   assumption is insufficient.
4. The active WI-5269 PAUTH remains current and unchanged in scope.
5. All eight targets are clean and unclaimed, or every differing byte has a
   separately terminal, focused-finalized owner whose exact resulting hash is
   adopted by fresh independent review. Whole-file overwrite is prohibited.
6. One exact `go_implementation` claim and schema-v3 start packet cover all
   eight targets, with operation-time authorization repeated before each
   mutation.
7. Any dispatcher/configuration/runtime, TAFE, harness-state, credential,
   release, deployment, Git-push/history, destructive-cleanup, or unrelated
   worktree request fails closed.

## Cross-Harness Disposition

The authority decision is envelope- and case-derived, never vendor- or
harness-derived. Claude, Codex, Antigravity, and Cursor ordinary workers
receive the same worker-safe behavior; provider review lanes do not acquire
mutation authority from their provider identity. Ops/build distinctions and
case authorization apply identically across every supported harness.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5269; WI-5268; bridge/gtkb-wi5269-activity-envelope-authority-validators-004.md; bridge/gtkb-dispatcher-black-box-spec-foundation-034.md",
  "canonical_authority": "DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001; DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001; DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001; DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001; ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001",
  "primary_route": "shared envelope authority validator plus exact bridge/PAUTH/claim/schema-v3 operation-time checks",
  "before_behavior": "The proposal named intended foundation records before they existed and a weak GO could bypass the owner-selected foundation-first order.",
  "after_behavior": "Validators derive authority from canonical v2 foundation records and fail closed on ordinary/ops/build confusion, missing case authorization, predecessor hold, dirty targets, or operation-time drift.",
  "self_descriptive_naming": "ordinary, ops, build, configuration mutation, internals mutation, and case authorization remain explicit values rather than inferred aliases.",
  "obsolete_guidance_disposition": "The superseded pre-foundation GO is void; no absent specification or false backlog closure is treated as authority.",
  "history_preservation": "The NO-ACTION/corrected-NO-GO chain, foundation chain, MemBase rows, exact target baselines, and test evidence remain append-only.",
  "expected_result": {
    "ordinary": "worker-safe packet access only",
    "ops": "governed black-box configuration mutation only",
    "build_without_case": "direct internals mutation denied",
    "build_with_case": "only exact authorized targets permitted",
    "cross_authority_substitution": "denied"
  },
  "rollback": {
    "instructions": "Before finalization, restore only WI-5269-owned hunks to the freshly recorded clean baselines.",
    "verification": "Re-run focused tests, target hashes, dependency/start checks, and confirm unrelated Git state is unchanged."
  },
  "hard_invariants": [
    "ordinary is defined by absence of an initialized activity envelope",
    "ops controls configuration only",
    "build internals authority is case-specific",
    "no provider or role label grants black-box mutation",
    "no mutation begins during predecessor or target-ownership uncertainty"
  ],
  "fail_closed_conditions": [
    "foundation or PAUTH drift",
    "WI-5268 readiness is not mechanically accepted",
    "any target is dirty or claimed without terminal owner adoption",
    "claim/start/operation-time authorization mismatch",
    "authority classes are interchangeable",
    "dispatcher configuration/runtime or unrelated mutation enters scope"
  ],
  "essential_context_preservation": "Preserve foundation hashes/status, predecessor state, PAUTH scope, exact target ownership, envelope state, case authorization, denial reason, tests, and rollback evidence."
}
```

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001`
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`
- `DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ACTIVITY-ENVELOPE-AUTHORITY`
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION`
- `DELIB-20260715-DISPATCHER-BLACKBOX-SAFE-PACKET-CONTENT`
- `DELIB-202666277`
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD`
- `bridge/gtkb-wi5269-activity-envelope-authority-validators-003.md`
- `bridge/gtkb-wi5269-activity-envelope-authority-validators-004.md`
- `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md`

## Owner Decisions / Input

No new owner decision is required. The owner-defined ordinary/ops/build
boundary and foundation-first order are now canonical v2 requirements. The
dispatcher-configuration troubleshooter hold remains binding, and this proposal
does not request configuration or runtime mutation.

## Specification-Derived Verification

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| Ordinary-worker definition and worker-safe packet contract | Session-envelope and black-box-gate tests for absent activity envelope | Ordinary gets mediated packet access; protected config/internals mutation denied. |
| Activity-envelope authority split | Parametrized ordinary/ops/build and cross-substitution tests | Ops configuration-only; build internals only with case; substitutions denied. |
| Case-specific build authority | Implementation-authorization/start tests varying GO, PAUTH, claim, packet, target, expiry, and session | Only the exact live case and targets authorize mutation. |
| Foundation-first ordering | Fresh foundation thread/commit, five spec/assertion reads, WI-5268 status, and dependency/start check | Committed VERIFIED foundation; all specs pass; hold honored mechanically. |
| Project/operation-time authorization | PAUTH read, schema-v3 start, per-target operation-time checks | Active exact WI/project/spec/target/session evidence; zero drift. |
| Cross-harness parity | Run supported harness projections against the shared authority matrix | No harness/provider-specific authority bypass. |
| Worktree hygiene | Exact target status/hashes before and after plus target-only diff/whitespace checks | No foreign-byte overwrite or unrelated path change. |
| Mandatory bridge gates | Candidate/live applicability and clause preflights | No missing specs, errors, or blocking gaps. |

Required focused commands include:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_envelope_runtime.py platform_tests/scripts/test_dispatch_blackbox_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check <all changed Python targets>
groundtruth-kb/.venv/Scripts/ruff.exe format --check <all changed Python targets>
groundtruth-kb/.venv/Scripts/python.exe -m py_compile <all changed Python targets>
git diff --check -- <all eight exact targets>
```

## Acceptance Criteria

1. Ordinary sessions are identified only from envelope state and receive no
   direct protected mutation authority.
2. Ops and build authorities are mechanically distinct and non-substitutable.
3. Build direct-internals access requires a live exact case at every authority
   layer and is limited to approved target paths.
4. Foundation, predecessor, target ownership, and operation-time drift fail
   closed before mutation.
5. Focused ordinary/ops/build/cross-authority/expiry/target tests pass across
   supported harness projections.
6. No dispatcher configuration/runtime, TAFE, harness registry/identity,
   credential, deployment, release, Git push/history, destructive cleanup, or
   unrelated worktree mutation occurs.

## Scope Changes

- Replaces draft foundation citations with live v2 MemBase authority.
- Adds committed foundation and accurate WI-5268 readiness evidence.
- Adds explicit predecessor-hold and dirty-target implementation barriers.
- Preserves the original eight source/test targets and behavior goal.

## Pre-Filing Preflight Subsection

Candidate applicability and mandatory clause preflights must pass with no
missing required/advisory specifications, no blocking errors, and zero
blocking clause gaps before filing.

## Risk And Rollback

The main risks are authority-class confusion and overwriting concurrently owned
shared files. Shared validation, exhaustive negative tests, exact operation-time
authorization, predecessor readiness, and clean-target adoption gates address
those risks.

Rollback is a focused revert of WI-5269-owned hunks only. No whole-file restore,
database replacement, bridge-history rewrite, dispatcher/configuration rollback,
or unrelated cleanup is authorized.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/activity/profiles.py`
- `scripts/dispatch_blackbox_gate.py`
- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_dispatch_blackbox_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
