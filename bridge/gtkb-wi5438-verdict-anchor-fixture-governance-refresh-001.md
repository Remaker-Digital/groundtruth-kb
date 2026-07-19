NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex desktop interactive Prime Builder A

# WI-5438: Refresh verdict-evidence anchor integration fixtures

bridge_kind: prime_proposal
Document: gtkb-wi5438-verdict-anchor-fixture-governance-refresh
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5438

target_paths: ["platform_tests/scripts/test_verdict_evidence_anchor_preflight.py"]
implementation_scope: test fixture content only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Refresh three stale integration fixtures so the verdict-evidence anchor suite reaches each named assertion under the current review-independence, author-provenance, and proposal-specification gates. Production validators and governance gates remain unchanged. Clean baseline: 26 collected, 23 passed, three failed before their intended anchor assertions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge writes and verdicts remain governed and independently reviewed.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - fixture authors carry explicit provenance.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and WI linkage.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification executes the focused suite.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - fixture changes preserve current governance and production behavior.

## Prior Deliberations

_No prior deliberations: this is a narrow hygiene correction to stale test fixtures discovered from a clean focused-suite baseline; no owner tradeoff or requirement change is involved._

## Owner Decisions / Input

The owner authorized the modernization program at project scope and directed every discovered bridge, TAFE, or harness defect to become an origin=hygiene work item with a linked test. Active PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` covers test and governance-evidence work while preserving GO, claim, implementation-start, independent verification, and focused-commit gates. No additional owner decision is needed.

## Requirement Sufficiency

Existing requirements are sufficient. Current review-independence, provenance, proposal-linkage, verification, and non-impairment requirements define the fixture shape and expected behavior. No requirement or production rule changes.

## Proposed Scope

1. Give the valid NO-GO fixture distinct valid proposal and verdict session provenance.
2. Give the non-verdict NEW fixture concrete Specification Links and other mandatory positive-proposal metadata.
3. Give the hook-level fabricated-NO-GO fixture valid independent provenance.
4. Change only `platform_tests/scripts/test_verdict_evidence_anchor_preflight.py`; do not change production source, hooks, dispatcher, TAFE, harness, eligibility, or runtime state.

## Acceptance Criteria

- All 26 focused tests pass and the three stale fixtures reach their named anchor assertions.
- Negative governance coverage remains fail-closed for same-session review, missing provenance, and missing Specification Links.
- Exact diff contains one test path and no production/runtime behavior changes.

## Cross-Harness Disposition

The shared test module covers the common bridge writer and compliance hook. No harness-specific exemption or divergent behavior is introduced; A remains PB-only and LO review remains session-context independent.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | focused 26-test module | writer and hook cases reach intended anchor outcomes; all pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | inspect positive NEW fixture and owning negative suites | positive fixture has concrete links; negative gate remains active |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | independent rerun before VERIFIED | exact results recorded by unrelated LO session |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Ruff, format, diff-check, one-path diff | clean and exactly scoped |

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff --check -- platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
git diff -- platform_tests/scripts/test_verdict_evidence_anchor_preflight.py
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5438 and TEST-11548 clean baseline evidence",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-DOCUMENT-AUTHOR-PROVENANCE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verdict_evidence_anchor_preflight.py -q --tb=short",
  "before_behavior": "three positive integration fixtures fail at newer prerequisite governance gates before their named anchor assertions",
  "after_behavior": "fixtures satisfy prerequisite provenance and specification gates, then exercise unchanged evidence-anchor behavior",
  "self_descriptive_naming": "existing names identify valid NO-GO, non-verdict, and fabricated-NO-GO outcomes",
  "obsolete_guidance_disposition": "replace stale fixture content only; no active governance guidance is removed or weakened",
  "history_preservation": "bridge history and production behavior remain unchanged while the numbered audit chain preserves this correction",
  "baseline": {"collected": 26, "passed": 23, "failed_before_anchor": 3},
  "expected_result": {"collected": 26, "passed": 26, "production_files_changed": 0},
  "rollback": {"instructions": "under separate authority, revert only the focused fixture commit without amending history", "test": "rerun the focused module and owning negative governance suites"},
  "hard_invariants": ["no production or runtime path changes", "review independence and provenance stay fail-closed", "proposal Specification Links remain mandatory"],
  "fail_closed_conditions": ["any focused test misses its named assertion", "any production path changes", "any negative gate is weakened", "GO, claim, or implementation-start authority is absent"],
  "essential_context_preservation": "WI-4520 anchor protections, governance prerequisites, shared harness behavior, and unrelated worktree bytes remain intact"
}
```

## Risk / Rollback

Risk is limited to unrealistic fixtures or accidental bypass of prerequisite gates. Use realistic distinct sessions and concrete links, preserve negative coverage, and touch one test file. Rollback is a separately governed revert of the focused fixture commit.

## Bridge Filing

This NEW proposal is filed as the next numbered bridge file `bridge/gtkb-wi5438-verdict-anchor-fixture-governance-refresh-001.md`; the versioned bridge chain is append-only and no prior file is deleted or rewritten.

## Recommended Commit Type

`test` - refresh stale integration fixtures without production behavior change.
