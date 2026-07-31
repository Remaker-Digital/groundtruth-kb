NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex desktop interactive Prime Builder A

# WI-5437: Reject unsupported LO removal claims absent from the reviewed report

bridge_kind: prime_proposal
Document: gtkb-wi5437-verdict-removal-claim-evidence
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5437

target_paths: ["scripts/verdict_evidence_anchor_preflight.py", "platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]
implementation_scope: source and test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Extend the shared verdict-evidence anchor validator with one conservative semantic check for the observed false template claim: a gated verdict that says the operative implementation report "claims removal of" an exact in-root path must find an unambiguous positive removal claim for that same path in the report. The WI-5370 report described adding validation and explicitly said Prime Builder did not remove bridge files, yet Cursor E rejected it by claiming the report promised removal of `scripts/per_thread_finalization_repair.py`.

This slice does not generalize into open-ended semantic review. It recognizes the narrow removal-claim form, preserves legitimate report-removal plus path-reappearance findings, and reuses the validator already consumed by the writer, compliance hook, provider publisher, and verification helpers. Implementation is sequenced after WI-5438 because both touch the focused test module.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governed verdict publication must fail closed on unsupported review claims.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - the check evaluates the exact operative report named by the verdict.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - WI-5437 and TEST-11547 preserve the defect and regression evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation, test, bridge, and verification evidence remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - invalid verdict evidence remains nonterminal and correctable through the bridge lifecycle.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, WI, and targets.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing requirement is cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification executes the focused suite and exact regression.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the extension is conservative and must not block legitimate verdicts.

## Prior Deliberations

_No prior deliberations: the requirement is a direct defect-derived extension of the already governed WI-4520 evidence-anchor validator; no owner tradeoff or requirement change is involved._

## Owner Decisions / Input

The owner authorized the modernization assurance project and directed every discovered bridge, TAFE, or harness defect to become an origin=hygiene work item with a linked test. Active PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` covers source, test, bridge, and governance evidence while preserving GO, exact claim, implementation-start, independent verification, and focused-commit gates. No additional owner decision is required.

## Requirement Sufficiency

Existing requirements are sufficient. The operative-document evidence rule, fail-closed bridge authority, provenance, and modernization non-impairment contract define the exact behavior. No specification or role change is proposed.

## Proposed Scope

1. Recognize gated-verdict prose asserting that the operative report "claims removal of" an exact backtick-delimited in-root path.
2. Search the operative report for an unambiguous positive removal statement for the same path, such as a Files Changed bullet stating `Removed <path>`.
3. Emit a named anchor violation when the report contains no such claim, covering `bridge/gtkb-wi5370-finalizer-body-validation-classification-004.md` against version 003.
4. Preserve a legitimate verdict when the report really claims removal and the reviewer observes that the path has reappeared.
5. Keep ambiguous prose, absence findings, other semantic assertions, non-gated statuses, and non-operative documents outside this narrow check.
6. Reuse the current shared validator so all existing governed publication surfaces receive the same behavior without adapter-specific logic.

## Acceptance Criteria

- The observed WI-5437 false removal verdict is rejected as an unsupported operative-report claim.
- A report that explicitly claims removal of the exact path permits a current-path-reappearance NO-GO.
- Existing evidence-anchor tests remain passing after WI-5438 terminalizes; new positive and negative regressions pass.
- No role, dispatcher, TAFE, harness, eligibility, routing, runtime, or direct-contact behavior changes.
- Exact implementation diff is limited to the declared source and test paths.

## Cross-Harness Disposition

The validator is the canonical shared evidence surface used by governed writer, hook, provider, and verification paths. The same narrow rule applies to every harness; there is no vendor exception, and A remains PB-only. The implementation must not add direct harness contact or adapter-specific branches.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | focused unit and writer/hook integration tests | unsupported exact removal claim fails; legitimate claim passes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | inspect WI, linked TEST-11547, proposal, implementation report | traceable artifact chain |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | independent focused-suite rerun | exact observed results carried into VERIFIED |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | existing corpus/regressions, Ruff, format, diff-check | no new false positive and clean exact scope |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff --check -- scripts/verdict_evidence_anchor_preflight.py platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5437, TEST-11547, and the WI-5370 version 003/004 evidence pair",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-DOCUMENT-AUTHOR-PROVENANCE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "scripts.verdict_evidence_anchor_preflight.validate_verdict_evidence_anchors",
  "before_behavior": "an LO verdict can falsely assert that its operative report claims removal of an exact path and still pass evidence validation",
  "after_behavior": "that narrow assertion must be grounded in an unambiguous same-path removal statement in the operative report",
  "self_descriptive_naming": "unsupported_removal_claim identifies the exact evidence failure without implying general semantic inference",
  "obsolete_guidance_disposition": "no guidance is removed; the validator documentation adds the narrow claim-evidence contract",
  "history_preservation": "existing bridge files remain append-only and unchanged; invalid verdicts are corrected only through later numbered files",
  "baseline": {"source_sha256": "A47FD9E95038E8271424DCEB3AFF7307B2B8BD22005394072CC42EEC9DF2099A", "test_sha256": "D8462FE9E0A9C3B364F8396325FFBFACD72DF82CC4D0743D04A069C3EA0E548D"},
  "expected_result": {"wi5437_false_claim": "blocked", "legitimate_removal_reappearance": "allowed", "adapter_specific_changes": 0},
  "rollback": {"instructions": "under separate authority, revert only the focused source/test commit without amending history", "test": "rerun the complete focused evidence-anchor suite"},
  "hard_invariants": ["no open-ended semantic classifier", "only the operative report and exact claimed path are evaluated", "all harnesses use the shared validator", "bridge history is not rewritten"],
  "fail_closed_conditions": ["operative report is unreadable", "exact removal claim is absent", "focused regression fails", "GO, claim, or implementation-start authority is absent"],
  "essential_context_preservation": "existing WI-4520 anchor behavior, absence opt-outs, legitimate report-removal findings, review independence, and unrelated worktree bytes remain intact"
}
```

## Risk / Rollback

The main risk is false-positive blocking from overbroad language detection. Keep recognition limited to the explicit "report claims removal of `<path>`" form and require exact same-path evidence. Ambiguous statements continue to pass. Rollback is a separately governed revert of the focused source/test commit.

## Bridge Filing

This NEW proposal is filed as the next numbered bridge file `bridge/gtkb-wi5437-verdict-removal-claim-evidence-001.md`; the versioned bridge chain is append-only and no prior file is deleted or rewritten.

## Recommended Commit Type

`fix` - reject one mechanically provable unsupported verdict-evidence claim.
