NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-97ef-74b1-9310-09761b16938a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; TAFE deliberately disabled
author_metadata_source: current session metadata

bridge_kind: prime_proposal
Document: gtkb-envelope-protocol-slice-d-dispatch-suppression-recovery
Version: 001
Date: 2026-08-01 UTC

# Recovery Defect-Fix Proposal — Envelope Protocol Slice D application-subject dispatch suppression

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5376
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

KB Mutation: This proposal performs no MemBase or `groundtruth.db` mutation.
The database is not an implementation target.

## Recovery Claim

This is a fresh, narrowly bounded recovery carrier for the outstanding
post-implementation Slice D verification defect. It does not amend, validate,
or erase the historical `gtkb-envelope-protocol-slice-d-worker-hook-injection`
v001-v024 chain. The controlling v024 NO-GO accurately preserves that
application-subject dispatch suppression was evaluated only after Prime
work-intent and target-path filtering, making the mandatory regression
contention-sensitive and preventing terminal verification.

Owner approval is recorded in
`DELIB-20260801-WI5376-GOVERNED-RECOVERY-PROPOSAL-APPROVAL`. That approval
authorizes this proposal and independent review only; it does not authorize
source mutation, a claim-bootstrap bypass, a schema-v3 implementation-start
packet, Git staging/commit, deployment, or TAFE activation.

## Defect / Current Reproduction

In `scripts/dispatcher_runtime.py`, the Prime branch calls
`_filter_prime_selected_by_work_intent(...)` and
`_filter_prime_selected_by_target_paths(...)` before it evaluates
`_application_subject_dispatch_suppression(project_root)`. An explicit
application work subject must suppress Prime dispatch before either filter can
acquire or inspect work intent, enumerate dirty worktree paths, create an
implementation authorization packet, or spawn a worker.

The historic v022 failure timed out in
`test_application_subject_suppresses_prime_dispatch_before_acquire_or_spawn`
while the target-path filter entered implementation authorization. The current
focused command passed in 0.48 seconds on 2026-08-01, which is not proof of
the required ordering: the source still reaches both filters before the
suppression check. The recovery therefore strengthens the regression with
negative assertions that both filter helpers are unreachable for an
application subject; it does not increase the test timeout or rely on a
contention-dependent pass.

## Preconditions — No Implementation Start

No protected source or test mutation may begin unless all conditions below are
true at operation time:

1. This proposal receives a fresh independent Loyal Opposition `GO`.
2. WI-5629 has become genuinely terminal through WI-5786's strict recovery;
   the current WI-5786 NO-GO does not satisfy this condition.
3. The verified projection lane remains independently `VERIFIED` at
   `bridge/gtkb-retire-ipa-refs-skill-projections-006.md` and
   `config/agent-control/harness-capability-registry.toml` is clean at HEAD.
4. The active project PAUTH remains valid for WI-5376 and both exact targets
   are clean, unreserved, and free of shared dirty-target conflict.
5. The implementing Prime Builder holds an exact current-session
   `go_implementation` claim and a fresh schema-v3 implementation-start
   packet that authorizes only the two declared targets.

The forbidden configuration targets remain explicitly outside scope:
`.api-harness/routing.toml`, `.claude/settings.json`, and
`config/dispatcher/rules.toml`. TAFE remains deliberately disabled.

## Proposed Scope

1. Move the application-subject suppression decision into the Prime dispatch
   branch before work-intent and target-path filtering, preserving the existing
   suppression receipt fields, signature semantics, and normal GT-KB subject
   behavior.
2. Add focused tests that monkeypatch both Prime filter helpers to fail if
   called under an `application` subject, then assert the existing suppression
   receipt and no-spawn properties.
3. Preserve the normal non-application negative control: GT-KB infrastructure
   subjects continue through ordinary dispatch selection and are not
   suppressed.
4. Do not alter dispatch selection/ranking policy, model choice, routing,
   TAFE state, hook injection behavior, credentials, releases, or historical
   bridge files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — status-bearing bridge state, role
  authority, independent review, and exact work-intent gates are mandatory.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the active
  PAUTH, target set, claim, and schema-v3 start must be revalidated at the
  point of mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` and
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — this fresh recovery does
  not borrow the expired historical packet or bootstrap implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — each governing
  constraint is linked to the scoped change and evidence below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — terminal verification
  must execute the specified focused and regression coverage, not rely on the
  historical timeout result.
- `DCL-SESSION-ENVELOPE-DURABILITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — application-subject suppression
  must prevent unintended Prime dispatch without degrading the worker envelope
  or weak-hook parity posture.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — preserve dispatcher policy,
  forbidden configurations, and unrelated harness behavior.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — WI-5629/WI-5786 and the verified
  projection lane remain hard Slice D start prerequisites.

## Requirement Sufficiency

Existing requirements sufficient. The governing authorization, bridge,
dependency-ordering, session-envelope, parity, non-impairment, and
spec-derived-verification requirements already define this repair's outcome
and gates. The work is a narrow correction to the established Slice D
application-subject suppression invariant; it neither changes owner intent
nor introduces a new dispatch policy. If current implementation evidence
shows that this invariant cannot be satisfied without changing those
requirements, implementation must stop for a new owner decision and revised
proposal.

## Prior Deliberations and Bridge Evidence

- `DELIB-20260801-WI5376-GOVERNED-RECOVERY-PROPOSAL-APPROVAL` — owner approval
  for this recovery proposal only.
- `DELIB-20260716-ENVELOPE-GRILL-B5-PACKET-HOOK-INJECTION` — packet hook
  injection posture preserved by this dispatcher suppression repair.
- `DELIB-20260717-ENVELOPE-WEAK-HOOK-FALLBACK-POLICY` — weak-hook fallback
  remains disclosed rather than silently promoted to parity.
- `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-022.md` —
  historic timeout finding.
- `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-023.md` —
  direct ordering diagnosis without source mutation.
- `bridge/gtkb-envelope-protocol-slice-d-worker-hook-injection-024.md` —
  independent NO-GO that preserved the authorization gate.
- `bridge/gtkb-wi5786-wi5629-false-terminal-recovery-010.md` — current
  unresolved prerequisite; it is not a clean dependency.

## Specification-Derived Verification Plan

| Governing requirement | Test or check | Required result |
| --- | --- | --- |
| Application work subjects suppress Prime dispatch before filtering or spawn | `platform_tests/scripts/test_dispatcher_runtime.py::test_application_subject_suppresses_prime_dispatch_before_acquire_or_spawn`, strengthened to fail if either Prime filter helper runs | Pass; suppression receipt exists; no work-intent, target-path, or spawn path runs |
| Non-application behavior remains available | `platform_tests/scripts/test_dispatcher_runtime.py::test_gtkb_subject_allows_cross_harness_dispatch_negative_control` | Pass; GT-KB infrastructure subject remains unsuppressed |
| Focused Slice D dispatcher behavior remains coherent | `E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short` | Pass, with any pre-existing unrelated failure separately identified and not claimed as success |
| No syntax/lint/format regression in the two targets | `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`; `E:\GT-KB\groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py` | Both pass |
| Protected target, scope, and finalization discipline | Fresh bridge applicability and ADR/DCL clause preflights; exact claim; schema-v3 start; post-implementation report; independent LO verification | All pass before any `VERIFIED` claim or atomic finalization |

## Acceptance Criteria

- An explicit `application` subject short-circuits Prime dispatch before either
  Prime filter helper or worker spawn.
- Existing suppression telemetry remains complete and deterministic.
- A passing test cannot mask a changed ordering merely because the shared
  database is briefly uncongested.
- No forbidden routing/configuration file is modified and TAFE remains
  disabled.
- No Slice D source/test mutation begins before every listed prerequisite is
  independently true.

## Risks / Rollback

The primary risk is moving suppression too early and obscuring required
dispatcher bookkeeping. The tests retain receipt assertions and a
non-application negative control. The change is limited to two paths and can
be reverted as one scoped commit after independent verification. If any
precondition is false or the source has moved, implementation stops and a new
reviewed revision is required.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5376; DELIB-20260801-WI5376-GOVERNED-RECOVERY-PROPOSAL-APPROVAL; Slice D v022-v024; WI-5786 v010; projection lane v006",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, and DCL-PROJECT-DEPENDENCY-ORDERING-001",
  "primary_route": "Independent LO GO, then only after all hard prerequisites a fresh schema-v3 start, two-path correction, spec-derived tests, report, and independent VERIFIED.",
  "before_behavior": "Application subjects are suppressed only after Prime filters may touch work-intent and target-path authorization state; the historic timeout was contention-sensitive.",
  "after_behavior": "Application subjects suppress Prime dispatch before either Prime filter or spawn path while GT-KB subjects retain normal dispatch behavior.",
  "self_descriptive_naming": "Suppression receipts remain application-subject specific and test failures identify any forbidden filter invocation.",
  "obsolete_guidance_disposition": "The v001-v024 Slice D chain remains historical evidence; this carrier neither reopens its prior GO nor treats a historical packet as current authority.",
  "history_preservation": "All historical Slice D reports, NO-GOs, owner decisions, and the unresolved WI-5629 recovery remain append-only and cited.",
  "baseline": {
    "head": "75decbfa704fe50288aecbc5669def329a0825df",
    "target_paths": [
      "scripts/dispatcher_runtime.py",
      "platform_tests/scripts/test_dispatcher_runtime.py"
    ],
    "focused_reproduction": "1 passed, 1 warning in 0.48s on 2026-08-01; static ordering still evaluates suppression after both Prime filters",
    "program_prerequisite": "WI-5786 latest NO-GO; WI-5629 is not genuinely terminal"
  },
  "expected_result": {
    "summary": "Application subjects short-circuit before Prime work-intent and target-path filters while normal GT-KB dispatch behavior is unchanged.",
    "scope": ["Prime dispatch ordering", "application-subject suppression", "focused dispatcher regression"]
  },
  "rollback": {
    "instructions": "Use a separate governed forward proposal restricted to the same two targets; do not restore historical bridge authority.",
    "verification": "Rerun the strengthened suppression regression, negative control, focused dispatcher tests, Ruff, format, preflights, and independent verification."
  },
  "hard_invariants": [
    "TAFE remains deliberately disabled",
    "Forbidden routing/configuration files remain untouched",
    "WI-5629 must be genuinely terminal through WI-5786 before any Slice D implementation start",
    "No source/test mutation before fresh GO, exact claim, and schema-v3 start packet",
    "No application subject may reach Prime filter or spawn paths"
  ],
  "fail_closed_conditions": [
    "Latest recovery bridge status is not independent GO",
    "WI-5786 remains nonterminal or any Slice D dependency is unresolved",
    "PAUTH, claim, packet, target cleanliness, registry, or overlap revalidation fails",
    "Strengthened regression observes a Prime filter or spawn under application subject",
    "Any forbidden configuration path is proposed or modified"
  ],
  "essential_context_preservation": "The active PAUTH, owner approval boundary, two exact targets, original v024 NO-GO, verified projection lane, unresolved WI-5629/WI-5786 prerequisite, and no-TAFE rule remain explicit."
}
```

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
