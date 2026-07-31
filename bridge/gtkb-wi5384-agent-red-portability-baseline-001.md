NEW

# WI-5384 - Stabilize the frozen Agent Red portability acceptance baseline

bridge_kind: prime_proposal
Document: gtkb-wi5384-agent-red-portability-baseline
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5384

target_paths: ["platform_tests/scripts/test_modernization_agent_red_portability.py"]

implementation_scope: test baseline stabilization only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Independently review and stabilize the exact current bytes of the frozen Agent
Red portability acceptance module before any semantic repair touches it. The
file is staged as a whole-file addition but is absent from `HEAD`, so a later
hunk-only WI cannot be mechanically finalized until this foreign baseline has a
committed parent.

This proposal authorizes no semantic modification. The candidate is exactly
36,844 bytes, SHA-256
`7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB`, Git
blob `4ef44fd6c3c007a9c37ed214bf5daa2c81ecfcc4`. Its current diagnostic result is
also part of the evidence: four tests collected, three passed, and one failed in
49.44 seconds. The failure is not waived or relabeled green. WI-5381 owns the
separately reviewed semantic repair and is hard-sequenced after this baseline is
VERIFIED and mechanically finalized.

## Specification Links

- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - requires portable Agent Red
  verification to prove the application lifecycle boundary rather than merely
  its directory placement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - establishes the in-root
  application placement whose portability evidence this module exercises.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - requires explicit Agent Red scope and
  regression-tested supported-application behavior without treating the app as
  GT-KB platform source.
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` - keeps this platform acceptance proof
  independent from the adopter application's own suite.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids disguising a failing
  baseline as successful modernization evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires the exact test
  artifact that underpins frozen acceptance evidence to be independently
  evaluable and owned.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the test candidate,
  work item, proposal, report, verdict, and later finalization to remain a
  traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps the current candidate state,
  later VERIFIED state, and separately repaired successor state explicit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the observed ownership
  defect and known test failure to be preserved as durable project artifacts.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active project PAUTH
  authorizes test and governance-evidence work but does not waive GO, claim,
  start, verification, or Git-operation gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires the live
  project authorization to be rechecked before any protected effect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO before protected
  work and an independent VERIFIED verdict before finalization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete
  governing specification links in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the explicit
  PAUTH, project, and WI linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the independent
  reviewer to verify the mapped exact-byte and execution evidence.
- `GOV-STANDING-BACKLOG-001` - governs preservation of this discovered baseline
  ownership defect as WI-5384 rather than leaving it implicit in worktree dirt.

## Prior Deliberations

- `DELIB-20265219` - ratified the Agent Red Readiness Program after the owner
  found prior isolation completion incomplete; this exact baseline closes one
  further evidence-ownership gap without overclaiming success.
- `DELIB-20265220` - approved readiness Phase 1 scoping, including independently
  testable application-boundary evidence.
- `DELIB-20265227` - selected the application-isolation ADR and paired
  minimization DCL that the portability activity is intended to prove.
- `DELIB-1336` - required verifiable, generated inventory and pre-move impact
  evidence for active Agent Red build roots; the present exact-byte baseline is
  consistent with that evidence-first constraint.
- `DELIB-202666274` - supplies the active project-scoped modernization Assurance
  implementation authority while retaining independent GO and VERIFIED gates.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` authorizes the Assurance
project and the owner has standingly directed that discovered modernization
defects be captured as hygiene work. This proposal performs no Git staging,
commit, push, deployment, release, cleanup, credential, dispatcher, TAFE, or
harness operation. Any later Git finalization remains a separate mechanical
authorization.

## Requirement Sufficiency

Existing requirements are sufficient. The baseline transaction changes no
behavior and introduces no new requirement; it makes the already-frozen
acceptance artifact independently reviewable before a successor changes it.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
|---|---|---|
| `ADR-APPLICATION-ISOLATION-CONTRACT-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | Independently inspect the candidate and run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_agent_red_portability.py -q --tb=short --timeout=600`. | Four tests collect. The observed current result is reported exactly as three passed and one failed; no green claim is accepted. |
| `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` | Confirm the sole target remains in the platform-owned test tree and its checks invoke production application/platform interfaces rather than relying on the adopter suite as the only proof. | Platform-owned acceptance evidence remains independent and explicit. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Compare `Get-Item`, `Get-FileHash -Algorithm SHA256`, `git hash-object`, and `git diff --no-index` or equivalent against the candidate identified above. | Size is 36,844 bytes, SHA-256 is `7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB`, and Git blob is `4ef44fd6c3c007a9c37ed214bf5daa2c81ecfcc4`; no semantic delta is present. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify WI-5384, this proposal, the exact-byte implementation report, and the independent verdict retain explicit candidate/VERIFIED state and link WI-5381 only as a successor. | No artifact claims the known failing baseline is repaired or complete. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | Before any protected effect, acquire the matching bridge claim and implementation-start packet through governed CLI and verify the active project PAUTH at operation time. | The packet covers exactly the sole target and forbids unauthorized Git or external operations. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the applicability and clause preflights and independently review this mapping plus the recorded command output. | No missing required specification or blocking clause gap; VERIFIED is impossible if bytes or results are misstated. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5384; DELIB-202666274; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE",
  "canonical_authority": "ADR-APPLICATION-ISOLATION-CONTRACT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001",
  "primary_route": "Governed exact-byte proposal, independent review, matching claim and implementation-start packet, exact-byte implementation report, independent VERIFIED, then separately authorized mechanical finalization.",
  "before_behavior": "The 36,844-byte frozen portability test is staged but absent from HEAD, has no independent baseline owner, and currently reports three passes plus one source-read-guard failure.",
  "after_behavior": "The identical bytes and observed three-pass/one-fail result are independently owned and reviewable, allowing WI-5381 to propose only a later semantic hunk against a committed parent.",
  "self_descriptive_naming": "WI-5384 and gtkb-wi5384-agent-red-portability-baseline explicitly identify this as baseline stabilization rather than portability repair.",
  "obsolete_guidance_disposition": "No guidance is changed; no failing evidence is hidden, retired, or relabeled.",
  "history_preservation": "The exact size, SHA-256, Git blob, observed execution result, proposal, report, and append-only verdict chain remain queryable.",
  "baseline": {
    "bytes": 36844,
    "sha256": "7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB",
    "git_blob": "4ef44fd6c3c007a9c37ed214bf5daa2c81ecfcc4",
    "pytest": "3 passed, 1 failed in 49.44 seconds"
  },
  "expected_result": {
    "semantic_delta": "byte-for-byte unchanged from the identified candidate",
    "bytes": 36844,
    "sha256": "7C3B5478DB3A02BC55B902FB583F23212BA6AA238833F550478134E16674D3EB",
    "pytest_claim": "The known three-pass/one-fail result remains explicit and is not represented as green."
  },
  "rollback": {
    "instructions": "No implementation byte changes occur in this baseline transaction; any later finalization is separately authorized and can be reversed only through governed Git mechanics.",
    "test": "Recompute size, SHA-256, and Git blob and confirm the exact values in baseline."
  },
  "hard_invariants": [
    "No semantic byte change",
    "No green claim for the failing relocation proof",
    "No WI-5381 repair hunk absorbed into the baseline",
    "No Git staging, commit, push, deployment, release, dispatcher, TAFE, harness, cleanup, or credential operation"
  ],
  "fail_closed_conditions": [
    "candidate size or hash changes",
    "the observed failure is omitted or relabeled",
    "a semantic repair appears in the candidate",
    "matching GO, claim, start packet, or independent review is absent"
  ],
  "essential_context_preservation": "The full relocation test, its source-read guard, exact hashes, known failing diagnostic, application-isolation authority, and WI-5381 successor boundary remain present."
}
```

## Risk / Rollback

The principal risk is false confidence: committing a test baseline can be
misread as proving that the test passes. The implementation report and verdict
must therefore preserve the exact one-failure result and name WI-5381 as the
semantic successor. Because this proposal changes no bytes, implementation
rollback is a no-op; any later local commit of the exact baseline requires
separate authority and remains reversible through ordinary governed Git
mechanics.

## Bridge Filing

This proposal is filed as the first status-bearing numbered file for
`gtkb-wi5384-agent-red-portability-baseline`; no aggregate queue or manual
routing artifact is created. TAFE/dispatcher behavior remains outside this
transaction. The numbered bridge file chain is append-only; no prior version
may be deleted or rewritten.

## Recommended Commit Type

`test`: a later separately authorized finalizer would establish the exact
platform acceptance-test baseline without claiming semantic repair.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
