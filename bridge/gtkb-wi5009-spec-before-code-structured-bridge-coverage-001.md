NEW

# WI-5009 Spec-Before-Code Structured Bridge Coverage

bridge_kind: prime_proposal
Document: gtkb-wi5009-spec-before-code-structured-bridge-coverage
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-05 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5009-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5009

target_paths: ["groundtruth-kb/templates/hooks/spec-before-code.py", "groundtruth-kb/tests/test_governance_hooks.py"]

implementation_scope: hook_template/test/governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5009 is a follow-up hardening item for the managed `spec-before-code` hook template. The current template lets platform test paths suppress the no-spec advisory when any status-bearing bridge markdown file contains an exact path token. That is too permissive: stale earlier versions, rejected terminal histories, and prose-only mentions can all look like coverage even when the latest governed bridge evidence does not actually map the `platform_tests/` file.

This proposal narrows platform-test bridge evidence to current, structured evidence. A `platform_tests/` path should suppress the advisory only when the latest bridge state for that thread is acceptable and the path appears in a structured bridge surface such as inline `target_paths` or a Spec-to-Test Mapping section/table. Stale earlier versions, latest `NO-GO`/`DEFERRED`/`WITHDRAWN`, unrelated paths, and prose-only mentions must continue to warn.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the latest numbered bridge state, not any historical file mention, determines live bridge evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A2 PAUTH permits this bounded hook-template/test fix but does not replace LO review or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass the live bridge `GO` and implementation-start packet.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay within the named WI-5009 template/test envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing bridge and backlog specifications are cited and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must include focused tests and observed command evidence.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - WI-5009 can close only if tests cover mapped, unmapped, stale/rejected, and prose-only bridge-evidence cases.
- `GOV-STANDING-BACKLOG-001` - the open WI must reach terminal state only with durable bridge/test evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation must inspect current template behavior and live bridge-state semantics rather than historical summaries.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, proposal, implementation evidence, and verification are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the hardening is expressed through source, tests, and bridge records rather than informal session notes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - latest bridge lifecycle state is the trigger that determines whether bridge-derived coverage is live.

## Prior Deliberations

- `WI-5009` backlog text - captures the residual WI-4455 hardening opportunity: stale/rejected bridge histories and prose-only path mentions should not satisfy platform-tests coverage.
- `bridge/gtkb-wi4455-platform-tests-spec-before-code-policy-review-002.md` - earlier policy-review context for platform-tests spec-before-code behavior.
- `bridge/gtkb-wi4455-platform-tests-bridge-derived-spec-before-code-004.md` - LO VERIFIED evidence for the initial Option A implementation; WI-5009 hardens the residual edge cases.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorized continuing Batch A2 reliability fixes through governed bridge work.
- `.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json` - approval packet for that owner decision; scoped here by PAUTH and LO review.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved continuing the high-priority queue through governed implementation/disposition work.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5009-BATCH-A2-20260705` - active Batch A2 authorization for WI-5009 hook-template source, tests, and governance evidence.

No additional owner decision is required. This proposal still requires Loyal Opposition `GO` and an implementation-start packet before protected mutation.

## Requirement Sufficiency

Existing requirements sufficient.

WI-5009 states the required hardening and acceptance surface: platform-tests coverage recognition must ignore stale/rejected bridge histories and prose-only mentions while preserving mapped bridge-derived coverage. Existing bridge authority rules define latest-state semantics; no new requirement is needed.

## Proposed Implementation

1. Update `groundtruth-kb/templates/hooks/spec-before-code.py` so `_bridge_evidence_covers_platform_test()` groups versioned bridge files by thread slug and evaluates only the latest version per thread.
2. Treat only latest acceptable statuses as coverage evidence, expected to include live/accepted implementation evidence such as `NEW`, `REVISED`, `GO`, and `VERIFIED`; latest `NO-GO`, `DEFERRED`, `WITHDRAWN`, and unrelated/unknown statuses must not suppress the advisory.
3. Replace whole-file prose scanning with structured extraction:
   - inline `target_paths: [...]` JSON or equivalent canonical target-path metadata;
   - path mentions inside a Spec-to-Test Mapping section/table.
   Random prose outside those structured surfaces must not count.
4. Preserve existing source-path behavior for non-`platform_tests/` files and existing platform-tests positive behavior when bridge evidence is current and structured.
5. Add focused tests in `groundtruth-kb/tests/test_governance_hooks.py` for mapped, unmapped, stale/latest rejected, and prose-only cases.

## Spec-Derived Verification Plan

| Governing surface | Required behavior | Verification |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Latest bridge state controls whether bridge evidence is live. | Tests create multi-version bridge threads where an earlier mapped version is followed by latest `NO-GO`/`WITHDRAWN` and assert the hook warns. |
| `DCL-SPEC-RELEVANCE-CLOSURE-001` | WI-5009 edge cases are fully covered. | Tests cover mapped target_paths pass, mapped Spec-to-Test Mapping pass, unrelated path warns, stale/rejected latest warns, and prose-only mention warns. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The hook reads current bridge files under the discovered project root and ignores stale summaries. | Tests exercise a temporary bridge directory with versioned files, not mocked cached state. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Verification evidence is command-based and repeatable. | Implementation report includes pytest and ruff command output. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Implementation stays within the two named template/test paths. | `git diff --name-only` in the implementation report lists only authorized paths plus bridge report artifacts. |

Minimum verification commands after GO:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_governance_hooks.py -q --tb=short --basetemp .gtkb-state/pytest-tmp-wi5009
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/templates/hooks/spec-before-code.py groundtruth-kb/tests/test_governance_hooks.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/templates/hooks/spec-before-code.py groundtruth-kb/tests/test_governance_hooks.py
```

## Acceptance Criteria

- A current structured `target_paths` bridge mapping for a `platform_tests/` file still suppresses the advisory.
- A current structured Spec-to-Test Mapping bridge mapping for a `platform_tests/` file suppresses the advisory.
- A path mentioned only in prose outside structured evidence no longer suppresses the advisory.
- An earlier mapped bridge version no longer suppresses the advisory when the latest version is rejected, withdrawn, deferred, or otherwise non-acceptable.
- Existing source_paths behavior for non-platform-test source files is unchanged.
- No live `.claude/hooks/spec-before-code.py` recovery-stub change, KB mutation, credential action, deployment, destructive cleanup, or broad status mutation is in scope.

## Risk / Rollback

Risk is low to moderate: the hook is advisory, but over-tightening could add advisory noise for legitimate platform tests. The mitigation is preserving both structured `target_paths` and Spec-to-Test Mapping paths and adding negative controls for stale/prose-only cases. Rollback is a single revert of the template/test diff; no schema or durable bridge-history mutation is proposed.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5009-spec-before-code-structured-bridge-coverage`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` because the eventual diff repairs a concrete false-positive coverage recognition defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
