NEW

# gtkb-wi4735-clause-preflight-user-profile-disclosure-guard - reduce CLAUSE-IN-ROOT false positives for harness-local path disclosures

bridge_kind: prime_proposal
Document: gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-23T09:56:30Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, Prime Builder resolved role

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4735

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py", "platform_tests/scripts/test_clause_in_root_disclosure_exempt.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4735 covers a recurring false positive in the mandatory ADR/DCL clause
preflight. `scripts/adr_dcl_clause_preflight.py` currently treats any Windows
user-profile path literal in a bridge report as refuting
`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, even when the path is
only a harness-local disclosure or diagnostic example and every declared
artifact target remains in-root under `E:\GT-KB`.

This proposal adds a narrow source/test guard so CLAUSE-IN-ROOT continues to
block genuine out-of-root artifact/output declarations while allowing
report-safe harness-local disclosures. The intended implementation should
preserve the existing explicit disclosure-block behavior, keep raw
`target_paths` metadata fully enforced, and add regression coverage for the
WI-4735 incident shape.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge status-bearing numbered files remain the authoritative proposal/report/verdict chain; this proposal must preserve mandatory clause-preflight semantics for GO/VERIFIED review.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the detector being changed enforces the in-root placement invariant, so the implementation must not permit declared GT-KB artifacts or outputs outside `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, clause, project-linkage, and verification requirements before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the required `Project Authorization`, `Project`, and `Work Item` metadata lines for WI-4735.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must include focused positive and negative tests derived from the CLAUSE-IN-ROOT invariant and the WI-4735 false-positive requirement.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation relies on the active May29 Hygiene PAUTH and stays inside source/test target paths.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the work preserves traceability among WI-4735, clause-preflight source, regression tests, bridge proposal, implementation report, and LO verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the false positive blocks lifecycle transitions at GO/VERIFIED review time; the repair must keep the artifact lifecycle trigger visible and testable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governance evidence should remain durable and mechanically reviewable instead of forcing authors to avoid truthful diagnostic disclosures.

## Prior Deliberations

- `DELIB-20263398` - GO review for WI-3384, which introduced the existing CLAUSE-IN-ROOT disclosure-block exemption while preserving strict `target_paths` enforcement.
- `DELIB-20263484` - Loyal Opposition advisory verifying the WI-3384 disclosure exemption and its regression-test coverage.
- `DELIB-2026-06-14-BRIDGE-PROTOCOL-COMPLIANCE-DISPATCH-BATCH-ADMISSION` - owner authorization record for the prior WI-3384 disclosure-exemption batch; relevant precedent for source/test-only repair of this detector family.
- `DELIB-20263832` - bridge preflight path-warning GO, relevant because it accepted a narrow cited-path collector instead of broad document-wide path scanning.
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-006.md` - incident evidence where CLAUSE-IN-ROOT failed because report text quoted a harness-local user-profile path while implementation targets remained in-root.

## Owner Decisions / Input

The owner already authorized this bounded implementation through
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`,
owner decision `DELIB-20265586`. No additional owner decision is required
because this proposal does not mutate formal artifacts, does not change the
clause registry TOML, does not add work items, and limits implementation to the
source/test target paths above.

## Requirement Sufficiency

Existing requirements sufficient - WI-4735 states the required behavior
directly: fix the CLAUSE-IN-ROOT user-profile literal false positive or require
report-safe disclosure/escaping so legitimate harness-local examples do not
block unrelated VERIFIED decisions. The linked ADR/DCL/GOV specifications are
sufficient to constrain implementation and verification.

## Spec-Derived Verification Plan

| Linked specification / requirement | Proposed verification |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; WI-4735 false-positive requirement | Add a regression where a bridge report declares only in-root `target_paths` and in-root output evidence, includes a harness-local user-profile path solely as report-safe disclosure/example context, and `evaluate_evidence()` returns `True` for CLAUSE-IN-ROOT. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; strict artifact enforcement | Preserve/add negative regressions proving out-of-root `target_paths`, out-of-root Files Changed/output declarations, and unescaped artifact claims still refute CLAUSE-IN-ROOT evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run mandatory bridge applicability and ADR/DCL clause preflights on this proposal before filing and after implementation report filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused clause-preflight regression modules and include observed results in the post-implementation report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve WI-to-bridge-to-test traceability and verify the lifecycle gate no longer blocks truthful disclosure-only report evidence while retaining in-root artifact enforcement. |

Expected commands after implementation:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/scripts/test_clause_in_root_disclosure_exempt.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/scripts/test_clause_in_root_disclosure_exempt.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py platform_tests/scripts/test_clause_in_root_disclosure_exempt.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4735-clause-preflight-user-profile-disclosure-guard
```

## Risk / Rollback

Primary risk is a false negative: relaxing the scanner too much could permit a
real out-of-root artifact/output declaration to pass as a disclosure. The
implementation must therefore keep `target_paths` fully enforced and carry
paired positive/negative tests. Rollback is a single source/test revert of the
three target paths plus bridge supersession if LO finds the proposed detector
boundary unsound.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4735-clause-preflight-user-profile-disclosure-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - this repairs a false-positive gate condition in an existing mandatory
preflight surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
