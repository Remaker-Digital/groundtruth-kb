NEW

# Defect-Fix Proposal - Normalize two untracked modernization test candidates

bridge_kind: prime_proposal
Document: gtkb-wi5291-modernization-candidate-lint-normalization
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5291

target_paths: ["platform_tests/scripts/test_check_artifact_evaluability.py", "platform_tests/scripts/test_modernization_authority_foundations.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make two frozen-modernization acceptance candidates satisfy the release code
quality floor without changing their behavior. Both files are absent from HEAD
and are pre-existing foreign untracked content. Together they currently pass
all 17 focused tests, but the release Ruff command reports one E402 import
finding in each and `ruff format --check` reports localized expression reflow.

The implementation will add only the established E402 disposition to the two
post-`sys.path` imports and apply Ruff formatting. It must prove normalized AST
identity and focused-test parity. Because no committed baseline exists, this
slice is deliberately uncommitted: it does not stage, finalize, or claim
authorship of either file. WI-5277 and the owning Gate 1.25 slices remain
responsible for provenance quarantine and governed baseline stabilization.

## Baseline And Ownership Boundary

- HEAD at proposal preparation:
  `2974839d62374e8e23cd585d6e3c254716a907ec`.
- Both target files are `??` and have no path history in any current Git ref.
- `platform_tests/scripts/test_check_artifact_evaluability.py`:
  - SHA-256:
    `68291C0186E45093FF164053FD64FC7F3D3452678B180C90B2CF16AD1F68389D`;
  - 7,892 bytes;
  - declared future WI-5153 Gate 1.25 target.
- `platform_tests/scripts/test_modernization_authority_foundations.py`:
  - SHA-256:
    `4E5015C3408CB8EA8DE38976F74679EF6ACCD54CF6DF011522CB7A61FD46BBA8`;
  - 4,192 bytes;
  - consumed by `scripts/check_modernization_scope_semantics.py` but not
    backed by a committed owning baseline.
- Current focused baseline: 17 passed in 4.36 seconds.
- Current lint baseline: exactly two E402 errors; formatter reports both files
  would be reformatted.
- WI-5277 owns detection/quarantine of protected work begun without applicable
  PAUTH. WI-5291 neither resolves that provenance defect nor converts these
  files into committable content.
- Implementation must abort if either SHA-256 differs before mutation.

## Specification Links

- `GOV-CODE-QUALITY-BASELINE-001` - The release Ruff and formatting floors
  apply by default to these Python acceptance candidates.
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` - Code quality is a universal
  baseline rather than an opt-in property of already committed files.
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` - No waiver or suspension is needed;
  both findings have deterministic mechanical fixes.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - The normalization must preserve
  test semantics and the frozen acceptance contract exactly.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Exact before hashes,
  AST equality, lint output, format output, and focused tests make the result
  independently evaluable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Both candidates remain inside
  the GT-KB platform-test root; no application or external path is introduced.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected test mutation requires
  independent GO, matching claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  links the exact mechanical delta and verification to governing contracts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work
  item, and target paths are explicit above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent VERIFIED
  must rerun the focused tests, AST comparison, and release lint commands.
- `GOV-STANDING-BACKLOG-001` - WI-5291 records the lint blocker and WI-5277
  remains the separate provenance owner.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The foreign candidate state,
  baseline hashes, bounded repair, and finalization hold remain durable.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Work item, proposal, exact test
  evidence, and independent verdict form the repair evidence graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Formatting does not advance either
  candidate from untracked/quarantined to committed or verified authority.

## Prior Deliberations

- `DELIB-202666080` - The owner-approved Gate 1.25 readiness design supplied
  the future child scope containing the evaluability test candidate; later
  enforcement review correctly withheld implementation activation.
- `DELIB-202666274` - The owner authorized all required modernization blocker
  repairs while preserving bridge, implementation-start, review, and
  mechanical-operation gates.

## Owner Decisions / Input

No additional product decision is required for AST-identical lint
normalization. The owner authorized the modernization program and the release
quality baseline is already stated. This proposal explicitly does not authorize
staging, commit, push, deployment, release, credentials, dispatcher, TAFE,
harness, routing, role, external-system mutation, or baseline promotion.

## Requirement Sufficiency

Existing requirements sufficient.

Ruff identifies the exact default-baseline violations, its formatter defines
the deterministic layout, and the 17 focused tests define the current
behavioral baseline. The outstanding provenance question is already governed
by WI-5277 and is intentionally not redefined by this formatting slice.

## Proposed Scope

1. After GO/claim/start, verify both target SHA-256 values match this proposal
   and save ignored pre-edit copies for rollback and AST comparison.
2. Add `# noqa: E402` to each
   `from groundtruth_kb.db import KnowledgeDB` import because each import
   intentionally follows local package-path setup.
3. Run Ruff formatter only on the two exact files.
4. Compute normalized `ast.dump(..., include_attributes=False)` hashes before
   and after; both must be identical.
5. Rerun all 17 focused tests, focused Ruff E/F, focused format check, and the
   exact release Ruff command.
6. Leave both files untracked and do not mutate the Git index. Record that
   finalization remains held for WI-5277 and owning-slice baseline
   stabilization.
7. Preserve every non-target byte.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5291, WI-5277, DELIB-202666080, and DELIB-202666274",
  "canonical_authority": "GOV-CODE-QUALITY-BASELINE-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --ignore E501,E741",
  "before_behavior": "Seventeen focused tests pass, but two untracked acceptance candidates fail two E402 checks and both fail format check.",
  "after_behavior": "The same tests and ASTs are unchanged while both files satisfy Ruff check and format floors.",
  "self_descriptive_naming": "The E402 dispositions remain on the intentional post-path-setup imports and no opaque waiver file is introduced.",
  "obsolete_guidance_disposition": "No test, assertion, acceptance clause, or provenance warning is retired; only formatter drift and two explicit import dispositions change.",
  "history_preservation": "Exact pre-edit copies, SHA-256 values, AST hashes, and test output are retained as implementation evidence while Git remains untouched.",
  "baseline": {
    "head": "2974839d62374e8e23cd585d6e3c254716a907ec",
    "evaluability_sha256": "68291C0186E45093FF164053FD64FC7F3D3452678B180C90B2CF16AD1F68389D",
    "authority_sha256": "4E5015C3408CB8EA8DE38976F74679EF6ACCD54CF6DF011522CB7A61FD46BBA8",
    "focused_passed": 17,
    "ruff_e402": 2,
    "format_drift_files": 2
  },
  "expected_result": {
    "focused_passed": 17,
    "ruff_errors": 0,
    "format_drift_files": 0,
    "ast_hash_changes": 0,
    "git_index_operations": 0
  },
  "essential_context_preservation": "All frozen carrier lists, evaluator assertions, expected outcomes, path setup, and imported KnowledgeDB behavior remain AST-identical.",
  "hard_invariants": [
    "no assertion or test-name change",
    "no source or database mutation",
    "no staging, commit, push, deploy, or release",
    "no conversion of untracked content into governed baseline",
    "no target outside the two exact files",
    "frozen modernization acceptance scope unchanged"
  ],
  "fail_closed_conditions": [
    "either pre-edit SHA-256 differs",
    "either normalized AST hash changes",
    "focused test count or result changes",
    "Ruff or format check fails",
    "either target becomes staged or tracked",
    "any non-target path changes"
  ],
  "rollback": "Restore each exact ignored pre-edit copy, verify the two proposal SHA-256 values, and remove only WI-5291 scratch evidence."
}
```

## Spec-Derived Verification Plan

| Specification | Verification and expected result |
|---|---|
| `GOV-CODE-QUALITY-BASELINE-001` | Focused and exact release Ruff commands exit zero; focused format check reports both files unchanged. |
| `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` | No per-file waiver registry or exclusion is added; the files conform directly. |
| `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` | Review proves only inline intentional-import dispositions exist and no temporary waiver lifecycle is opened. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Pre/post normalized AST hashes match and the same 17 tests pass. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Report exact before hashes, after hashes, AST hashes, command outputs, and Git status. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both targets resolve beneath `E:\GT-KB\platform_tests`; no external path is read as authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability and clause preflights pass with zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Independent LO reruns AST, pytest, Ruff, format, and Git-status checks before VERIFIED. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify valid GO, matching claim, and implementation-start packet before either target is edited. |

Exact implementation verification commands:

```text
python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py -q --tb=short
python -m ruff check platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py --select E,F --ignore E501,E741
python -m ruff format --check platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py
python -m ruff check applications/Agent_Red/src/ applications/Agent_Red/tests/ platform_tests/ --select E,F --ignore E501,E741
git status --short -- platform_tests/scripts/test_check_artifact_evaluability.py platform_tests/scripts/test_modernization_authority_foundations.py
```

The implementation report must include before/after normalized AST SHA-256
values and prove both Git status entries remain `??`.

## Acceptance Criteria

1. Both proposal baseline SHA-256 values match immediately before mutation.
2. The two intentional post-path-setup imports carry explicit E402
   dispositions and no other lint suppression is added.
3. Ruff format check passes for both files.
4. Normalized AST hashes are identical before and after for each file.
5. All 17 focused tests pass with the same collection count.
6. Focused Ruff and the exact release Ruff E/F command exit zero.
7. Both targets remain untracked, the Git index is unchanged, and finalization
   remains held for WI-5277 and owning-slice baseline stabilization.
8. Independent LO returns VERIFIED before the uncommitted repair is considered
   complete.

## Risk / Rollback

The main risk is laundering foreign untracked implementation into an unrelated
commit. Exact hash binding, AST equality, untracked-status verification, and an
explicit no-finalization rule contain that risk. Rollback restores the two
pre-edit copies and verifies their proposal hashes.

## Bridge Filing

This proposal is filed as the first append-only numbered bridge file,
`bridge/gtkb-wi5291-modernization-candidate-lint-normalization-001.md`; no
prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered
bridge files remain the governed workflow surfaces.

## Recommended Commit Type

`test` would be appropriate only after the owning Gate 1.25 baselines are
governed and separately authorized for finalization. This WI performs no Git
commit.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
