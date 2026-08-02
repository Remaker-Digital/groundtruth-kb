REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: OpenAI Codex
author_model_version: GPT-5.6
author_model_configuration: Codex desktop; owner-designated Prime Builder; manual physical-bridge processing with dispatcher disabled
author_metadata_source: explicit current-session metadata

bridge_kind: prime_proposal
Document: gtkb-wi5723-session-resolver-fallback-removal
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5723-session-resolver-fallback-removal-004.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5723
target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_end_to_end_workflow.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# Revised Proposal — WI-5723 Session Resolver Fallback Removal

## Revision Claim

Prime Builder accepts v004's correction of the invalid v003 inactivity closure.
No implementation report exists because the approved change was never started.
This version therefore reoffers the bounded v001 implementation proposal against
the current clean six-path baseline; it does not fabricate implementation
evidence and does not treat the historical GO as a live start authorization.

The defect still reproduces. `session_resolver_fallback` remains in the live
producer, the envelope fallback-source set, the modernization trusted-source
set, and three fixtures. All six declared targets are tracked and clean. A new
independent GO, exact-session claim, and schema-v3 implementation-start packet
are mandatory before any target mutation.

This revision changes only its append-only bridge artifact. It performs no
source, test, configuration, narrative, database, registry, project, PAUTH,
backlog, Git, dispatcher/TAFE, credential, deployment, release, cleanup, or
external-system mutation.

## Findings Addressed

### F1 — `NO-ACTION` was used as closure

Accepted. Version 003 remains non-terminal incident evidence. WI-5723 remains
open/backlogged, and this complete revision restores the normal review lane.

### F2 — Factual implementation evidence is absent

Accepted as a present-state fact, not a reason to invent a report. Current
source inspection confirms the change is absent. The lawful next artifact is
this revised implementation proposal, followed by independent review; a factual
report is due only after a future GO-authorized implementation.

## Current Reproduced Baseline

The literal is present at these live locations:

- `scripts/session_self_initialization.py` — explanatory comment and producer
  branch still emit the fallback source.
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py` —
  `REGISTRY_FALLBACK_ROLE_SOURCES` still contains it.
- `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` — trusted
  worker-role sources still contain it.
- `platform_tests/scripts/test_modernization_end_to_end_workflow.py`,
  `platform_tests/scripts/test_session_self_initialization.py`, and
  `platform_tests/scripts/test_session_envelope_cli_provenance.py` — fixtures
  still exercise the prohibited value.

Current SHA-256 preimages:

| Path | SHA-256 |
| --- | --- |
| `scripts/session_self_initialization.py` | `5ca958fed69a8525b7597392df9aaf4cbf6cd9b3d18bf2a043efb8d7ad979cba` |
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | `c7e52e66b193a91e82cf59f60e66ab2faa1797f7b1e119b154ca3b13ed136130` |
| `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py` | `ebafbe854e5d26cf2afc023aa61a6f7c1eeba6986784b3e139263da580e5ff64` |
| `platform_tests/scripts/test_modernization_end_to_end_workflow.py` | `86d18e9f628c644a80bbd969716e6bef133c4667483adca5b1270cc7970088d5` |
| `platform_tests/scripts/test_session_self_initialization.py` | `26355abbce775b1c2bd21189d85329bb91df4f6f0cce987b8e00934bdc8b1115` |
| `platform_tests/scripts/test_session_envelope_cli_provenance.py` | `b2c2a41bbc55323c0f362267dfe935c572b02af8da54db01229a3a2472a1e230` |

Scoped Git status returned no output for the six targets. These hashes are
admission preimages, not ownership claims over unrelated future changes.

## Proposed Change

### C1 — Remove the producer fallback

In `scripts/session_self_initialization.py`, when neither dispatcher composition
nor an explicit transcript role exists, do not call `ensure_worker_session` with
a synthesized role. Delete the live `session_resolver_fallback` literal and let
unresolved sessions remain without authoritative worker-role provenance.

### C2 — Preserve recorded interactive authority

In `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, prevent an open
session whose recorded role source is `transcript_init_keyword`,
`owner_init_keyword`, or `interactive_transcript_explicit` from being
overwritten by a non-interactive source. Preserve explicit owner
re-declaration and dispatcher-composition behavior.

### C3 — Fail closed on residual envelopes

Remove the prohibited source from trusted modernization workflow provenance so
any residual envelope fails at the trust gate.

### C4 — Update and add focused tests

Update the three affected fixtures and add behavioral coverage proving:

- a SessionStart-like rerun cannot revert a transcript-declared role;
- an unresolved role writes no authoritative envelope and fails closed;
- all three interactive sources resist non-interactive overwrite;
- owner re-declaration and dispatcher composition still update authority; and
- a residual fallback-bearing envelope is rejected before role activation.

## Collision And Sequencing Boundary

These are shared session-authority surfaces. WI-5679 and current WI-5815/WI-5830
chains describe adjacent keying, claim-isolation, and harness-selector behavior.
This revision claims only the six explicit C1–C4 paths and the fallback-removal
hunks. At implementation start, Prime Builder must re-hash each path and scan
the latest physical bridge heads for any active GO on the same targets. Any
changed preimage, foreign dirty hunk, or competing GO fails closed and requires
a new revision or explicit sequencing; it must not be absorbed into WI-5723.

No protected narrative-artifact or formal GOV/DCL/ADR mutation is in this
narrow slice. WI-5723's broader D2/Part B/Part C cleanup remains separate future
work requiring its own exact target scope and approval packets.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202667524` Decision 1 — unresolved identity must fail closed.
- `DELIB-202667530` — explicit session direction is canonical and supersedes
  competing resolution paths.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — investigation provenance for
  the reproduced defect.
- Owner's 2026-07-31 narrow-slice choices recorded in v001: use WI-5723,
  investigate dependents first, accept fail-closed behavior, and keep ad-hoc
  provenance hygiene separate.
- `bridge/gtkb-wi5723-session-resolver-fallback-removal-002.md` — prior
  independent GO, now historical rather than start authority.
- `bridge/gtkb-wi5723-session-resolver-fallback-removal-003.md` and `-004.md` —
  invalid closure and independent correction.

## Owner Decisions / Input

No new owner decision is required. WI-5723 has an active membership in
`PROJECT-GTKB-HOUSEKEEPING-HARDENING` and inherits the active list-free
whole-project PAUTH cited above. Its legacy WI `approval_state` is
noncontrolling. The dispatcher/TAFE prohibition is preserved.

## Requirement Sufficiency

Existing requirements remain sufficient. The owner already selected the narrow
fail-closed slice. This proposal restores that exact scope to review without
expanding into protected narrative or formal-artifact cleanup.

## Specification-Derived Verification Plan

| Requirement / behavior | Verification | Required result |
| --- | --- | --- |
| Producer removal | deterministic search of the six targets | no production occurrence; only explicit rejection fixtures if still necessary |
| Transcript persistence | new SessionStart-after-init regression | recorded role and provenance remain unchanged |
| Unresolved role fail-closed | fresh session with no role keyword | no authoritative envelope; provenance resolver raises missing-current-session error |
| Interactive overwrite guard | tests for all three interactive sources | non-interactive overwrite refused |
| Legitimate role changes | owner re-declaration and dispatcher-composition tests | both remain permitted |
| Residual fallback rejection | modernization actor resolution test | trust gate rejects the value |
| Dispatch non-regression | focused dispatcher runtime suite | composed workers still use `dispatcher_composition` |
| Path containment | scoped Git status and diff | only six declared targets changed |

Exact verification commands to record in the future implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_cli_provenance.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py platform_tests/scripts/test_session_envelope_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/session/envelope.py groundtruth-kb/src/groundtruth_kb/modernization/workflow.py
git --no-optional-locks diff --check -- <six declared targets>
```

## Acceptance Criteria

1. No production code can create `role_resolution_source=session_resolver_fallback`.
2. An unresolved role writes no authoritative envelope and fails closed.
3. A SessionStart-like rerun cannot revert transcript authority.
4. Interactive provenance resists non-interactive overwrite while owner
   re-declaration and dispatcher composition remain valid.
5. Residual fallback-bearing envelopes are untrusted.
6. Focused session, modernization, and dispatcher suites pass.
7. Only the six declared paths change.
8. No dispatcher/TAFE, database, protected narrative, or formal artifact is
   mutated.

## Risk And Rollback

The accepted ergonomic risk is that a session which never declares a role
cannot mint governed claims. That is the intended fail-closed behavior. The
overwrite guard could suppress a legitimate transition; positive tests for
owner re-declaration and dispatcher composition constrain that risk. Rollback
is a separately governed revert of the six-path implementation commit; bridge
history remains append-only.

Recommended commit type: fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
