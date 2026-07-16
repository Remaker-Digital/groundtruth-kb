NEW

# Baseline Proposal - Stabilize the frozen scope-semantics acceptance artifacts

bridge_kind: prime_proposal
Document: gtkb-wi5357-scope-semantics-acceptance-baseline
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
Work Item: WI-5357

target_paths: ["scripts/check_modernization_scope_semantics.py", "platform_tests/scripts/test_modernization_scope_semantics.py", "platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py", "platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Preserve four existing untracked modernization acceptance artifacts as an exact,
independently reviewed baseline. The files are absent from HEAD and predate the
WI-5260 exact-proof additions, so the hunk-only WI-5260 finalizer cannot safely
commit its additions until these foreign bytes have a committed owner.

This proposal does not alter any source or test semantics. It authorizes only
verification of the four current byte images and, after independent review and
the separate exact Git authority required for finalization, their byte-for-byte
addition to HEAD. It excludes every WI-5260 exact-proof addition, timeout repair,
receipt, manifest change, and unrelated worktree path.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/check_modernization_scope_semantics.py` | 53,258 | `49FB96512D4CB5778C96B585E248D1D942E7FC703E88FED356715A1554812247` |
| `platform_tests/scripts/test_modernization_scope_semantics.py` | 13,425 | `683FCF9A3B1770FD6DF55FD9880AB8A70C91438CA782BA35E456F7363349AEF6` |
| `platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py` | 27,231 | `05B4E04197E085248C17846EB766F714CC1ADFD90F37AF21D55D2864F0333914` |
| `platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py` | 28,089 | `2354C9099775CF448D0633648637C99E0D319BC9BE8D8659538851C5F83FDC81` |

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - Foreign concurrent bytes require deterministic ownership and exact, independently reviewed preservation rather than accidental absorption.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - The frozen modernization objectives require executable, fail-closed acceptance evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Baseline stabilization must preserve the frozen manifest, existing checker behavior, and every observed failure without substituting synthetic evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected test additions require independent GO, a matching claim, implementation-start authority, and independent VERIFIED evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal links the exact file images and verification commands to their governing requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, PAUTH, work item, and parseable target paths are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Independent review must rerun the binding, focused regression, and clause-exact collection checks before VERIFIED.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - Exact file hashes and deterministic test collection make the baseline machine-evaluable.
- `GOV-STANDING-BACKLOG-001` - WI-5357 is the durable backlog owner for this baseline.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All artifacts and diagnostic outputs remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-202666274` - The owner authorized the complete modernization program while retaining bridge review, independent verification, and exact mechanical Git gates.

## Owner Decisions / Input

No new owner decision is required to file or independently review this
proposal. `DELIB-202666274` and the active Assurance project authorization cover
the baseline work. Any later Git staging or commit remains a separate mechanical
operation and is not authorized by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The linked work-tree hygiene, mechanical
enforcement, non-impairment, evaluability, and independent-verification
requirements already require exact preservation of this acceptance baseline.
No new normative behavior is introduced.

## Proposed Scope

1. Verify that each target remains untracked and absent from HEAD before implementation.
2. Verify each exact byte length and SHA-256 value in the table above.
3. Verify the checker validates all 94 frozen scope bindings without changing the frozen manifest.
4. Verify the two clause-exact files collect 56 concrete cases with `--runxfail` available for honest failure execution.
5. Preserve the exact four byte images as the baseline only after independent GO, matching claim/start authority, implementation reporting, independent VERIFIED, and separate exact Git authority.
6. Fail closed if any target hash, length, path, manifest digest, or collection count changes before finalization.
7. Do not edit a target, manufacture a receipt, change a timeout, stage another path, or absorb any WI-5260 addition.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_modernization_scope_semantics.py validate",
  "before_behavior": "The acceptance files exist only as untracked foreign bytes, so a later hunk-only WI-5260 finalizer cannot preserve them without absorbing unrelated content.",
  "after_behavior": "The same byte images have an independently reviewed committed baseline and WI-5260 can remain limited to its reviewed additions.",
  "self_descriptive_naming": "The WI-5357 baseline title and four-path hash table identify the artifact ownership boundary directly.",
  "obsolete_guidance_disposition": "No guidance is added, retired, or replaced; this transaction preserves existing acceptance artifacts only.",
  "history_preservation": "All current bytes, current passing checks, current failing checks, and the frozen manifest remain unchanged.",
  "baseline": {
    "target_count": 4,
    "binding_count": 94,
    "focused_tests_passed": 11,
    "clause_exact_cases": 56,
    "clause_exact_passed": 25,
    "clause_exact_failed": 31
  },
  "expected_result": {
    "target_count": 4,
    "byte_changes": 0,
    "binding_count": 94,
    "clause_exact_cases": 56,
    "git_scope_path_count": 4
  },
  "rollback": "Remove only the exact baseline commit through a separately governed Git operation; do not rewrite or restore any concurrent path.",
  "hard_invariants": [
    "the four target hashes and lengths remain exact",
    "the frozen manifest remains unchanged",
    "no receipt is created or rewritten",
    "no WI-5260 addition is included",
    "no fifth Git path is staged or committed"
  ],
  "fail_closed_conditions": [
    "target hash or length changes",
    "target becomes tracked before the baseline transaction",
    "94-handle validation fails",
    "clause-exact collection is not 56 cases",
    "frozen manifest changes",
    "Git scope includes any fifth path"
  ],
  "essential_context_preservation": "All 94 frozen handles, existing broad proofs, 56 clause-exact cases, observed failures, and root-containment rules remain present and queryable."
}
```

## Spec-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact-byte evaluability and work-tree hygiene | `Get-FileHash -Algorithm SHA256` plus file lengths for all four targets; `git ls-files --error-unmatch` for each | The table hashes/lengths match and every target is absent from HEAD. |
| Frozen binding enforcement | `python scripts/check_modernization_scope_semantics.py validate` | `MODERNIZATION SCOPE SEMANTICS: PASS` for 94 bindings. |
| Baseline focused regressions | `python -m pytest platform_tests/scripts/test_modernization_scope_semantics.py -q --tb=short --timeout=180` | 11 passed; no target byte changes. |
| Clause-exact evaluability | `python -m pytest platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py --collect-only -q` | 56 tests collected. |
| Honest current failures | `python -m pytest platform_tests/scripts/test_modernization_harness_assurance_clause_exactness.py platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py -q --tb=short --runxfail --timeout=600` | Completes without infrastructure timeout and preserves real pass/fail outcomes; current observation is 31 failed and 25 passed in 240.18 seconds. A changed semantic count requires explanation, not baseline editing. |
| Non-impairment | Rehash all targets and the frozen manifest after every verification command | All four target hashes remain exact and the frozen manifest is unchanged. |

## Risk / Rollback

The main risk is legitimizing implementation bytes accidentally. The exact hash
allowlist, four-path boundary, and pre-finalization recheck prevent scope drift.
The current clause-exact run exceeds the repository-wide 30-second test bound in
the real `MOD-GL02` Git-lifecycle proof; this proposal records that behavior but
does not repair or conceal it. A separate descendant work item owns the bounded
runtime correction.

Rollback is a separately governed single-commit reversal limited to these exact
four paths. No broad reset, checkout, cleanup, or concurrent-path restoration is
permitted.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5357-scope-semantics-acceptance-baseline`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test` - the eventual exact baseline transaction adds only acceptance checker
and test artifacts; it changes no production behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
