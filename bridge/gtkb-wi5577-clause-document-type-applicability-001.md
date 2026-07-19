NEW
::init gtkb lo
::open build

# WI-5577: Scope spec-to-test clause applicability to verification artifacts

bridge_kind: prime_proposal
Document: gtkb-wi5577-clause-document-type-applicability
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-18 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5577-CLAUSE-DOCUMENT-TYPE-APPLICABILITY-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5577

target_paths: ["config/governance/adr-dcl-clauses.toml", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]
activity_envelope_requirements: {"config/governance/adr-dcl-clauses.toml":"ops","platform_tests/scripts/test_adr_dcl_clause_preflight.py":"build"}

implementation_scope: configuration,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The mandatory spec-to-test clause currently becomes `must_apply` when any
bridge artifact contains ordinary `VERIFIED`, `implementation report`, or
`post-implementation` prose. That makes pre-implementation GO, NO-GO, and
NO-ACTION artifacts subject to a verification-only evidence requirement, while
the current broad evidence pattern can be satisfied by an isolated heading or
command token.

This proposal changes only the registered content trigger for
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.
The replacement trigger is anchored to either a first-line `VERIFIED` status or
a `bridge_kind: implementation_report` metadata line. The existing evaluator,
all evidence semantics, every other clause, and all dispatcher/TAFE/harness
surfaces remain unchanged. Focused tests prove both the corrected negative
cases and the mandatory positive cases.

## Exact Design

1. In `config/governance/adr-dcl-clauses.toml`, replace only the
   `CLAUSE-SPEC-TO-TEST-MAPPING` content regex with the TOML-escaped equivalent
   of `(?ims)(?:\A\s*VERIFIED\b|^bridge_kind:\s*implementation_report\b)`.
2. Do not change `scripts/adr_dcl_clause_preflight.py`. Its existing
   path-plus-content axis semantics already produce the required result:
   verification artifacts are `must_apply`; other bridge artifacts with only a
   path hit are at most `may_apply`.
3. Add focused regression cases to
   `platform_tests/scripts/test_adr_dcl_clause_preflight.py`:
   - GO, NO-GO, and NO-ACTION candidates containing incidental `VERIFIED`
     prose or the governing spec ID are not `must_apply`;
   - a NEW `bridge_kind: implementation_report` candidate is `must_apply`;
   - a first-line VERIFIED candidate is `must_apply`;
   - both verification artifact kinds fail closed without substantive mapped
     command/result evidence and pass when that evidence is present;
   - the other four registered clauses retain their current applicability and
     enforcement behavior.

## Activity-Envelope Segmentation

- The registry mutation is black-box configuration work. It may be performed
  only by a worker initialized with an `ops` activity envelope after independent
  GO, an exact thread claim, schema-v3 implementation-start authorization,
  clean-preimage validation, and per-target operation-time authorization.
- The test mutation is internal build work. It may be performed only by a
  worker initialized with a `build` activity envelope after the same gates are
  independently satisfied for that session and target.
- The two activity steps are sequential. Each worker releases its exact claim
  before the next worker begins. The post-implementation report is filed only
  after both target blobs and the complete focused suite have been verified
  together.
- An ordinary worker is not authorized to perform either mutation. No one
  activity envelope is treated as authority for both target classes.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5577; TEST-11624; bridge/gtkb-wi5483-existing-work-item-test-linkage-004.md; bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md",
  "canonical_authority": "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and the five-clause registry at config/governance/adr-dcl-clauses.toml",
  "primary_route": "Bounded bridge proposal, independent GO, separate ops/configuration and build/test implementation steps, implementation report, and independent VERIFIED finalization",
  "before_behavior": "Any bridge artifact containing incidental VERIFIED or implementation-report prose can make the verification-only spec-to-test clause must_apply.",
  "after_behavior": "Only first-line VERIFIED artifacts and bridge_kind implementation_report artifacts make the spec-to-test clause must_apply; all other clause behavior is preserved.",
  "self_descriptive_naming": "WI-5577, TEST-11624, the bridge slug, V2 PAUTH, and both target paths explicitly name clause document-type applicability.",
  "obsolete_guidance_disposition": "The broad content trigger is replaced in place as configuration history; prior numbered bridge evidence remains append-only and no historical artifact is rewritten.",
  "history_preservation": "The registry and test changes enter history only through independent VERIFIED focused finalization with the complete numbered bridge chain.",
  "baseline": {
    "focused_tests": "25 passed",
    "registry_sha256": "4FD47BFBCB336B0342EBB1E4EC302A0AEFAFBE15274DB44BB4627F240155BDC5",
    "test_sha256": "9AB4BF7AD4F26147E8B9198A3CBD8A274C9B5C80965F69EFA66E6222C562514B",
    "excluded_script_sha256": "685428FB0034E5713E091FBB54322CBCD000793AC7B3759C70EA80E684B5C10C"
  },
  "expected_result": {
    "negative_cases": "GO, NO-GO, and NO-ACTION incidental prose is not must_apply.",
    "positive_cases": "First-line VERIFIED and bridge_kind implementation_report remain must_apply and fail closed without mapped evidence.",
    "unrelated_clauses": "All four other registered clauses retain current behavior."
  },
  "rollback": {
    "instructions": "Use a separately governed bridge cycle to restore the prior trigger and remove only the WI-5577 test additions.",
    "verification": "Rerun the complete focused module, both preflights, Ruff check, Ruff format, and exact target diff inspection."
  },
  "hard_invariants": [
    "No script/source implementation change",
    "No ordinary-worker mutation authority",
    "Configuration mutation requires ops and test mutation requires build",
    "No dispatcher-control configuration, TAFE, runtime, routing, or harness-state mutation",
    "No unrelated worktree or Git history mutation by Prime Builder"
  ],
  "fail_closed_conditions": [
    "Either target preimage drifts before its activity step",
    "The V2 PAUTH, latest GO, exact claim, schema-v3 start, or operation-time authorization is absent or stale",
    "Any verification artifact loses mandatory evidence enforcement",
    "Any unrelated clause changes behavior"
  ],
  "essential_context_preservation": [
    "The mandatory Slice 2 exit-5 contract remains intact.",
    "The owner dispatcher-control troubleshooting hold remains intact.",
    "WI-5577 and TEST-11624 remain the canonical defect and regression-test linkage."
  ]
}
```

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the corrected clause must
  remain mandatory for implementation reports and VERIFIED verdicts and must
  require executed spec-derived evidence.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the registry change must
  remain deterministic, machine-parseable, and reviewable from its exact bytes.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - ordinary workers
  receive no authority to mutate the bridge-governance registry or internals.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - configuration and internal
  test mutations are separated into ops and build activity envelopes.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - the specified
  foundation remains the prerequisite authority for this derived correction.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the change must preserve every
  existing fail-closed clause behavior outside the exact false-activation case.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and
  `ADR-CROSS-HARNESS-PARITY-001` - all harnesses consume the same deterministic
  clause registry and preflight behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal and all later verdict/report
  artifacts remain status-bearing numbered bridge files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  complete specification and project/work-item linkage.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - PAUTH, exact
  claims, schema-v3 starts, activity envelopes, and operation-time checks bound
  both sequential implementation steps.
- `GOV-WORK-TREE-HYGIENE-001` - both targets must be clean and byte-identical to
  reviewed preimages before either implementation step.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all proposal, configuration, test,
  and verification artifacts remain inside `E:/GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the independently reported defect is
  preserved as WI-5577/TEST-11624 and follows the full proposal-to-VERIFIED
  lifecycle.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded
  carriers and proposals for newly reproduced in-scope black-box defects while
  preserving all implementation and independent-review gates.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` is the independent
  VERIFIED/focused-finalized foundation evidence for the ordinary-worker,
  activity-envelope, and foundation-first constraints used here.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
  is the canonical VERIFIED origin of the mandatory fail-closed clause gate.
  This proposal narrows one over-broad trigger without weakening that gate.
- `bridge/gtkb-wi5483-existing-work-item-test-linkage-004.md` is the canonical
  independent GO that reported the false activation and shallow-evidence
  behavior as a non-blocking tooling defect.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` remains binding.
  This proposal excludes `config/dispatcher/**`, runtime state, dispatcher
  control, routing, and every independently troubleshot surface.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner
  decision supporting the bounded V2 PAUTH and this proposal.
- The independently VERIFIED foundation at
  `bridge/gtkb-dispatcher-black-box-spec-foundation-034.md` records the owner's
  ordinary/ops/build activity-envelope boundary in canonical form.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` prohibits
  interference with the independent troubleshooter. The two declared targets
  are outside that held dispatcher-control surface.

No additional owner decision is required to submit this bounded proposal for
independent review. GO would authorize only the later gated implementation
sequence, not immediate mutation.

## Requirement Sufficiency

Existing requirements sufficient. The required behavior is already established
by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; the authority boundary is
already established by
`DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001`,
`DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001`, and
`DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001`. WI-5577 narrows a
detector defect and does not create or revise a formal requirement.

## Spec-Derived Verification Plan

| Specification or acceptance | Test or verification command | Expected result |
| --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` false-activation correction | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | GO, NO-GO, and NO-ACTION incidental prose is not `must_apply`; implementation reports and VERIFIED artifacts are `must_apply`; evidence-missing verification artifacts exit 5; mapped command/result evidence exits 0. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and clause-registry preservation | Same focused module plus assertions over all five registered clause IDs | Existing schema, waiver, fail-closed, content-file, and other-clause behavior remains green. |
| Activity-envelope and authorization specs | `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5577-CLAUSE-DOCUMENT-TYPE-APPLICABILITY-V2-20260718 --json`; per-session claim/start/operation-time validation | Active V2 carrier names only two targets, separates ops/configuration from build/test, and no ordinary worker or cross-class activity is accepted. |
| Cross-harness parity specs | Direct hash/read of the single shared registry and preflight test surface; no harness-local copy is changed | Every harness continues to consume one shared deterministic registry behavior. |
| Bridge/project/spec linkage specs | Candidate and live `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` runs | No missing required/advisory specs and zero blocking clause gaps. |
| `GOV-WORK-TREE-HYGIENE-001` and in-root placement | `git status --short -- <two targets>`; `git diff --check -- <two targets>` | Both preimages are clean before each step; only the exact two in-root paths differ afterward. |
| Python quality for the focused test target | `groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_adr_dcl_clause_preflight.py`; `groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Both commands exit 0. |

TEST-11624 is the canonical linked test artifact for WI-5577. Its expected
outcome is implemented by the focused positive/negative matrix above.

## Baseline Evidence

- `config/governance/adr-dcl-clauses.toml` is clean at SHA-256
  `4FD47BFBCB336B0342EBB1E4EC302A0AEFAFBE15274DB44BB4627F240155BDC5`.
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py` is clean at SHA-256
  `9AB4BF7AD4F26147E8B9198A3CBD8A274C9B5C80965F69EFA66E6222C562514B`.
- Excluded `scripts/adr_dcl_clause_preflight.py` is clean at SHA-256
  `685428FB0034E5713E091FBB54322CBCD000793AC7B3759C70EA80E684B5C10C`.
- The current focused module passes 25/25 tests with one pre-existing unknown
  `asyncio_mode` pytest-configuration warning.
- Ruff check passes and Ruff format reports the test module already formatted.

## Acceptance Criteria

1. Only the exact two declared targets change; the preflight script remains
   byte-identical.
2. Incidental `VERIFIED` prose or the governing spec ID in GO, NO-GO, or
   NO-ACTION artifacts cannot make the spec-to-test clause `must_apply`.
3. First-line VERIFIED and `bridge_kind: implementation_report` artifacts
   remain `must_apply`.
4. Verification artifacts still fail closed without substantive mapped
   command/result evidence.
5. All existing focused tests and the new TEST-11624 matrix pass.
6. Ops/configuration and build/test work occur in separate authorized activity
   envelopes; no ordinary worker or cross-class mutation is accepted.
7. No dispatcher-control configuration, TAFE, runtime, routing, harness state,
   unrelated worktree bytes, Git history, deployment, release, credential, or
   external-system state changes.

## Risk / Rollback

The principal risk is a false negative if the anchored trigger misses a valid
verification artifact. The positive matrix covers both canonical verification
shapes, while the unchanged path axis and mandatory gate preserve conservative
reporting. A second risk is accidental weakening of unrelated clauses; the full
focused module and all-five-clause assertions bound it.

Rollback is the exact inverse of the one registry-line change plus the focused
test additions, performed through a separately governed bridge cycle if the
implementation has already been finalized. No existing bridge version is
rewritten or deleted.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
file for `gtkb-wi5577-clause-document-type-applicability`; no prior version is
deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain remain
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the bounded change corrects false applicability while preserving
the existing clause-preflight capability and public interface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
