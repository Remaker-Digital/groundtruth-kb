NEW

# Baseline Proposal - Stabilize the artifact-evaluability acceptance artifacts

bridge_kind: prime_proposal
Document: gtkb-wi5359-artifact-evaluability-acceptance-baseline
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5359

target_paths: ["scripts/check_artifact_evaluability.py", "platform_tests/scripts/test_check_artifact_evaluability.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Preserve the current untracked artifact-evaluability checker and focused test as
an exact, independently reviewed baseline before WI-5153 adds fail-closed scoped
evaluation semantics or WI-5291 applies lint-only normalization. Both files are
absent from HEAD, and the focused test hash has already changed since WI-5291's
earlier inventory, so neither descendant may absorb the current bytes silently.

This proposal changes no behavior. It authorizes exact-byte review and, only
after independent VERIFIED plus separate mechanical Git authority, addition of
these two byte images to HEAD:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/check_artifact_evaluability.py` | 14,503 | `AE6B58F5FE5B4BDE9A5501A013D0CEFD5D229BEC6AF41A7750449F9CBC686065` |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | 7,933 | `69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67` |

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - Foreign untracked acceptance bytes require exact ownership before descendant finalization.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - The baseline checker and tests expose the current evaluability contract without claiming future WI-5153 behavior.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - Evaluability evidence must remain executable and fail closed.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Stabilization preserves current behavior, failure boundaries, and descendant ownership.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected additions require independent GO, matching claim/start authority, and independent VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Exact paths, hashes, requirements, and verification are linked here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work item, and target paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent review reruns the focused tests and expected CLI boundary.
- `GOV-STANDING-BACKLOG-001` - WI-5359 is the durable baseline owner.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All files and diagnostic output remain under `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202666274` - The owner authorized the complete modernization program while retaining bridge, independent-verification, and exact Git gates.

## Owner Decisions / Input

No new owner decision is required to file or review this proposal. The active
Assurance project authorization covers baseline stabilization. Git staging or
commit remains a separate mechanical operation outside this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The linked hygiene, evaluability,
mechanical-enforcement, and non-impairment carriers already require exact,
reviewable preservation. No new normative behavior is introduced.

## Proposed Scope

1. Verify both paths are untracked and absent from HEAD.
2. Verify the exact lengths and SHA-256 values above.
3. Rerun the 14 focused tests without editing either target.
4. Confirm the current checker rejects the future `--work-item` and `--gate` arguments; WI-5153 owns that later interface and semantics.
5. Fail closed on any hash, length, path, test-count, or Git-scope drift.
6. Exclude all WI-5153 engine behavior, WI-5291 lint normalization, database changes, receipts, and unrelated worktree content.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180",
  "before_behavior": "The checker and test exist only as changing untracked bytes that descendants cannot finalize safely.",
  "after_behavior": "The same two byte images have an independently reviewed baseline and semantic/lint descendants remain hunk-scoped.",
  "self_descriptive_naming": "WI-5359 and the two-path hash table state the exact ownership boundary.",
  "obsolete_guidance_disposition": "No guidance is added, retired, or replaced.",
  "history_preservation": "The current checker behavior, current CLI limitation, and 14 passing focused tests remain unchanged.",
  "baseline": {
    "target_count": 2,
    "focused_tests": 14,
    "scoped_cli_supported": false
  },
  "expected_result": {
    "target_count": 2,
    "byte_changes": 0,
    "focused_tests": 14,
    "git_scope_path_count": 2
  },
  "rollback": "Remove only the exact baseline commit through a separately governed Git operation.",
  "hard_invariants": [
    "both target hashes and lengths remain exact",
    "no WI-5153 behavior is added",
    "no WI-5291 lint normalization is added",
    "no third Git path is included"
  ],
  "fail_closed_conditions": [
    "target hash or length changes",
    "target becomes tracked before the baseline transaction",
    "focused collection is not 14 tests",
    "current scoped CLI rejection changes",
    "Git scope includes any third path"
  ],
  "essential_context_preservation": "The complete current checker, focused tests, expected CLI boundary, and descendant WI ownership remain queryable."
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact-byte hygiene/evaluability | File lengths, `Get-FileHash -Algorithm SHA256`, and `git ls-files --error-unmatch` for both targets | Both hashes/lengths match and both paths are absent from HEAD. |
| Current executable baseline | `python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180` | 14 passed; both hashes remain unchanged. |
| Descendant boundary | `python scripts/check_artifact_evaluability.py --spec-id DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 --work-item WI-5158 --gate verification --json` | Current baseline rejects the unimplemented `--spec-id`, `--work-item`, and `--gate` arguments; WI-5153 remains open. |
| Non-impairment | Rehash both targets after all commands | Exact hashes remain unchanged and no evidence is manufactured. |

## Risk / Rollback

The main risk is treating current precursor bytes as completed WI-5153 work.
The explicit expected CLI rejection and exact hash boundary prevent that false
claim. Rollback is a separately governed single-commit reversal limited to the
two paths; broad reset, checkout, cleanup, and concurrent-path restoration are
forbidden.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5359-artifact-evaluability-acceptance-baseline`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - the eventual exact transaction adds only the current checker and its
focused acceptance tests without changing behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
