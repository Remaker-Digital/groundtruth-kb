NEW

# Stabilize the WI-5142 Artifact Decontamination baseline

bridge_kind: prime_proposal
Document: gtkb-wi5347-wi5142-artifact-decontamination-baseline
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16T19:24:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop, Prime Builder, high reasoning

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5347

target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "scripts/check_artifact_decontamination.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py"]

implementation_scope: source and test baseline stabilization
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Independently review and adopt the exact three-file WI-5142 Artifact
Decontamination implementation baseline that is present in the worktree but
absent from `HEAD`. WI-5142 was mechanically resolved from historical VERIFIED
evidence while these implementation bytes remained untracked, leaving
descendant WI-5335 unable to finalize a one-line timeout hunk without absorbing
the entire foreign baseline.

This is a byte-adoption transaction, not a new feature implementation. The
candidate is exactly:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py` | `A5AC3E15AE09D7485751E8329295717188B26F4026134983D671678BAA788DB3` | 40,452 |
| `scripts/check_artifact_decontamination.py` | `8D2A02E90746E2F2A28BBD64E90EBA367285B66F22F3D0D3A7380492F50E23C9` | 20,694 |
| `platform_tests/scripts/test_modernization_artifact_decontamination.py` | `FC82FF570ECAA73A4FAC2004632CE1BFD945571CB69D62FB1CA56B9F95FE4C45` | 20,915 |

All 24 frozen lifecycle tests passed unchanged in 67.21 seconds with a
diagnostic `--timeout=600`. Independent review must inspect the whole candidate,
confirm the hashes immediately before reporting, and preserve WI-5142
provenance. The WI-5335 `@pytest.mark.timeout(...)` descendant hunk is excluded
and must be implemented only after this baseline is present in `HEAD`.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — governs the Artifact Decontamination scanner, lifecycle classifications, and bounded cleanup evidence.
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` — distinguishes canonical current carriers from generated/historical/non-authoritative surfaces.
- `DCL-SUPERSEDED-SOT-LEAKAGE-001` — requires stale or superseded authority to remain outside effective worker-loading paths.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`; `DCL-INDEX-GENERATED-VIEW-001` — provide the current-vs-generated bridge authority semantics exercised by the decontamination graph and tests.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires baseline adoption to preserve both legitimate results and all hard invariants.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` — requires deterministic, executable evidence for the three adopted artifacts.
- `GOV-WORK-TREE-HYGIENE-001` — requires verified implementation bytes to receive explicit ownership rather than remain unexplained dirt.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs independent review, exact claim/start scope, implementation report, and VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires all relevant governing specifications to be linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — binds WI-5347 to the active Artifact Decontamination project PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the 24-test and hash evidence to be executed and mapped before VERIFIED.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — requires this baseline to finalize before WI-5335 and forbids absorption of that descendant hunk.
- `GOV-STANDING-BACKLOG-001` — keeps the false-closure recovery visible until the exact bytes are independently verified and finalized.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — requires every candidate and evidence path to remain inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve the distinct historical WI-5142 lifecycle and current baseline-recovery lifecycle without rewriting either.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-AUTHORIZATION` — authorized WI-5142's bounded Artifact Decontamination implementation packages.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — explains the historical mechanical WI-5142 closure that preceded source finalization.
- `DELIB-202666274` — authorizes all required modernization blocker and false-closure repairs at project scope while preserving mechanical-operation gates.

## Owner Decisions / Input

`DELIB-202666274` and active
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE`
authorize this independently reviewed baseline recovery. No new owner decision
is required for proposal filing or byte-preserving review. This proposal does
not itself authorize staging, commit, push, release, deployment,
dispatcher/TAFE mutation, harness mutation, credential lifecycle, destructive
cleanup, or external-system mutation. Any later local commit still requires its
own exact mechanical authority.

## Requirement Sufficiency

Existing requirements sufficient. The frozen MOD-AD01 through MOD-AD12 contract,
the three exact candidate files, the 24 executable tests, and current lifecycle
specifications completely define the baseline. No new or revised requirement is
needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "config/governance/modernization-release-candidate.json",
  "primary_route": "independently reviewed exact-byte baseline adoption before descendant hunk repair",
  "before_behavior": "three verified implementation files are untracked, so descendant finalization would absorb foreign bytes",
  "after_behavior": "the exact WI-5142 baseline exists in HEAD and WI-5335 can finalize only its own one-line descendant hunk",
  "self_descriptive_naming": "WI-5347 identifies baseline stabilization and preserves WI-5142 provenance",
  "obsolete_guidance_disposition": "historical WI-5142 verification remains history and is not rewritten as current implementation authority",
  "history_preservation": "the original VERIFIED lifecycle and new baseline-recovery lifecycle remain separate and append-only",
  "baseline": {
    "head_presence": "all three paths absent",
    "worktree_presence": "all three exact candidate paths untracked",
    "diagnostic_tests": "24 passed in 67.21 seconds"
  },
  "expected_result": {
    "head_presence": "all three exact hashes present",
    "descendant_scope": "WI-5335 timeout annotation remains absent from baseline"
  },
  "rollback": {
    "instructions": "revert only the exact three-file baseline transaction under separately authorized Git mechanics",
    "test": "rerun the 24 frozen tests and exact hash inventory"
  },
  "hard_invariants": [
    "no unrelated worktree byte is absorbed",
    "no WI-5335 timeout hunk is included",
    "history remains non-authoritative for active loading",
    "all current lifecycle assertions remain intact"
  ],
  "fail_closed_conditions": [
    "any candidate hash changes",
    "any fourth path enters scope",
    "any test or checker behavior contradicts the frozen contract",
    "exact Git mechanical authority is absent"
  ],
  "essential_context_preservation": "all MOD-AD01 through MOD-AD12 behavior, deterministic reports, and current-vs-historical classifications are preserved"
}
```

## Spec-Derived Verification Plan

| Governing specification | Verification evidence | Expected result |
|---|---|---|
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`; `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`; `DCL-SUPERSEDED-SOT-LEAKAGE-001`; `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001`; `DCL-INDEX-GENERATED-VIEW-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short --timeout=600` | All 24 unchanged tests pass; both full repeatability scans and every MOD-AD assertion execute. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`; `GOV-WORK-TREE-HYGIENE-001` | SHA-256/byte inventory before report and before finalization; exact three-path diff/index inventory | Hashes and sizes match the proposal; exactly three files are adopted; no fourth path is included. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Diagnostic test result plus checker/report byte comparisons exercised by the 24-test suite | Legitimate results and all hard invariants are preserved; no assertion is removed or weakened. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Mandatory preflights, exact matching claim/start, implementation report, and independent whole-file review | No missing required/advisory specs or blocking clause gaps; exact-byte adoption is independently VERIFIED. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Search the test candidate for a test-local timeout marker and compare its hash to the proposal | No WI-5335 `@pytest.mark.timeout(...)` hunk is present in the baseline; WI-5335 remains a later descendant. |
| `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5142/WI-5347 histories and numbered proposal/report/verdict chain | Historical closure and current baseline recovery remain distinct and traceable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Mandatory clause preflight and path inventory | `CLAUSE-IN-ROOT` passes and all dependencies resolve under `E:\GT-KB`. |

## Risk / Rollback

Whole-file adoption is intentional only because all three candidates are absent
from `HEAD` and together form the frozen WI-5142 implementation baseline. The
risk is misattributing later foreign bytes or smuggling WI-5335 into that
baseline. Independent review must inspect all three full files, bind the exact
hashes, rerun tests, and fail closed on drift. No source edit is proposed.
Rollback is the exact three-file baseline transaction under separate Git
authority; no broad reset, cleanup, or unrelated file operation is permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5347-wi5142-artifact-decontamination-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — restores the missing committed carrier for an already implemented and
independently verified modernization baseline.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
