NEW
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-20260605T200100Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, Prime Builder keep-working loop
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Implementation Proposal - Work-Tree Hygiene Slice A Detector

bridge_kind: implementation_proposal
Document: gtkb-work-tree-hygiene-slice-a-detector
Version: 001
Author: Codex Prime Builder, harness A
Date: 2026-06-05 UTC
Recipient: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356
work_item_ids: [WI-4356]
target_paths: ["scripts/hygiene/stray_detector.py", "platform_tests/scripts/test_work_tree_stray_detector.py"]
requires_verification: true
implementation_scope: implementation_slice_a_read_only_detector

Recommended commit type: feat(hygiene)

---

## Claim

Implement Slice A of the owner-directed recurring work-tree hygiene mechanism: a read-only detector module that computes stale workspace and stash candidates without taking cleanup action. This child proposal follows the GO'd scoping thread `gtkb-work-tree-hygiene-mechanism-scoping` and intentionally leaves CLI commands, doctor wiring, governance-spec insertion, hooks, scheduled enforcement, and any apply behavior out of scope.

## Dependency And Precedence Check

Live Prime bridge scan before this proposal showed three actionable bridge items. The Ollama governance child is GO but requires formal and protected narrative approval packets before mutation. The harness-state rule-files NO-GO requires protected narrative approval packets before correction. The Ollama parent NO-GO depends on the governance child. WI-4356 Slice A is therefore the highest-priority unblocked reliability item found in the current backlog and bridge context.

## Owner Decisions / Input

Owner directive recorded on WI-4356: agents cannot be expected to return after twelve hours, stale work older than twelve hours must be triaged by a different agent, and GT-KB needs recurring work-tree hygiene plus a regular method for cleaning strays.

`DELIB-20260867` authorizes WI-4356 implementation work under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` for source, test addition, hook upgrade, and CLI extension mutation classes. This slice uses only source and test-addition classes.

## Requirement Sufficiency

Existing requirements are sufficient for this read-only detector slice. The detector must identify candidate stale work, preserve evidence, and return structured decisions for later CLI or doctor surfaces. It must not perform repository mutation or cleanup.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving recurring hygiene work into deterministic services.
- `DELIB-20260809` records the Loyal Opposition GO for the WI-4356 scoping proposal.
- `DELIB-20260867` records owner authorization for WI-4356 implementation work.
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-002.md` approved child proposals with concrete target paths and dry-run-first behavior.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - filed through the bridge index as a versioned proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work item metadata are declared above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section maps applicable specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps specs to concrete checks.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - detector inputs must be supplied from live state by callers rather than cached startup summaries.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale workspace findings are lifecycle-trigger candidates for owner-gated follow-up.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - target paths remain under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - findings are structured artifacts for future triage and work-item capture.

## Proposed Scope

Implement `scripts/hygiene/stray_detector.py` as a pure Python module with dataclasses and functions that classify provided workspace entries and stash entries. The module should accept injected clock/input data for deterministic tests, support a default stale threshold of twelve hours, distinguish active-session recent work from stale candidates, and emit JSON-serializable result dictionaries.

Add `platform_tests/scripts/test_work_tree_stray_detector.py` covering stale tracked edits, stale untracked files, recent work, active-session exclusions, stash age boundaries, unique-content flags, and JSON-serializable output.

Out of scope for this slice: command-line interfaces, doctor integration, hooks, scheduled execution, governance-spec insertion, deletion, stash mutation, branch changes, automated commits, pushing, and cross-repository scanning.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Detector processes path and timestamp metadata only; tests use synthetic names. | Secret scan remains covered by normal hooks and focused tests avoid credential-shaped fixtures. | |
| CQ-PATHS-001 | Yes | Normalize path-like inputs through pathlib/PurePath style handling and keep all repo assumptions under injected roots. | Focused tests cover root-relative and nested path examples. | |
| CQ-COMPLEXITY-001 | Yes | Keep classifier functions small and split workspace and stash classification paths. | Ruff plus focused pytest exercise branch behavior. | |
| CQ-CONSTANTS-001 | Yes | Name the twelve-hour threshold constant and avoid magic values in classifiers. | Tests assert threshold boundary behavior. | |
| CQ-SECURITY-001 | Yes | Read-only module with no subprocess execution and no repository mutation API. | Tests assert output only; code review confirms no mutating calls. | |
| CQ-DOCS-001 | Yes | Public dataclasses and classifier functions receive concise docstrings where behavior is not self-evident. | Ruff/docstring review during implementation. | |
| CQ-TESTS-001 | Yes | Add targeted unit tests for stale, recent, active-session, stash, and serialization cases. | `python -m pytest platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short`. | |
| CQ-LOGGING-001 | N/A |  |  | Library detector should return structured data and leave logging to caller surfaces. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff check, scoped Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before report. | Commands recorded in the post-implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: run bridge applicability preflight for this bridge id.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: confirm Project Authorization, Project, and Work Item header lines remain present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: focused pytest must cover every behavior in Proposed Scope.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: tests inject fresh input snapshots and assert no cached global state is used.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: tests verify stale findings carry explicit triage reasons and candidate action labels.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all changed files stay under the GT-KB root.

## Acceptance Criteria

1. `scripts/hygiene/stray_detector.py` exists and exposes read-only classifier functions.
2. `platform_tests/scripts/test_work_tree_stray_detector.py` covers stale workspace and stash candidate behavior.
3. No code path performs repository mutation, cleanup, deletion, external process execution, or scheduled enforcement.
4. Focused pytest passes.
5. Scoped Ruff check and format-check pass.
6. Bridge applicability and ADR/DCL clause preflights pass before the implementation report.

## Implementation Plan

1. Add the detector module with dataclasses for workspace and stash inputs plus JSON-serializable finding output.
2. Add focused unit tests with injected timestamps and roots.
3. Run focused pytest and scoped Ruff checks.
4. File a post-implementation report only after the source and tests pass.