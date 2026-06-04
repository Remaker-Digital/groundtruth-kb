REVISED
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: 019e933c-8522-75e1-bf57-0fcb06fd8a89
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; user-assigned Prime Builder; workspace-write
author_metadata_source: keep-working automation environment

# Implementation Proposal REVISED - Implementation-Start Target-Paths Preflight (WI-3380)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-target-paths-preflight
Version: 004
Responds to: bridge/gtkb-impl-start-target-paths-preflight-003.md
Supersedes proposal metadata from: bridge/gtkb-impl-start-target-paths-preflight-001.md
Author: Prime Builder (Codex automation, user-assigned PB)
Date: 2026-06-04 UTC
Session: keep-working-20260604T1532Z

Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Work Item: WI-3380
work_item_ids: [WI-3380]
target_paths: ["scripts/impl_start_target_paths_preflight.py", "groundtruth-kb/tests/test_impl_start_target_paths_preflight.py", ".claude/hooks/bridge-compliance-gate.py"]

Recommended commit type: feat

## Claim

Add a deterministic, read-only preflight that compares candidate implementation file paths against the latest GO-derived `target_paths` glob set for a bridge thread. The preflight gives Prime Builder and verification sessions an explicit scope-drift report before implementation-start, report filing, or hook-time enforcement turns scope mistakes into later NO-GO churn.

This revision keeps the original implementation target paths and functional shape from `bridge/gtkb-impl-start-target-paths-preflight-001.md`, but corrects the authorization envelope. It no longer relies on `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` or `GOV-RELIABILITY-FAST-LANE-001`. Instead it routes the improvement-scope work through the active bridge-protocol reliability project and PAUTH that permit `cli_extension`, `hook_upgrade`, `source`, and `test_addition`.

## Revision Summary

- Authorization corrected: `WI-3380` remains live with `origin=improvement`, so the rejected fast-lane authority is removed.
- Project corrected: `WI-3380` has active membership in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` with membership source `owner-approved-orphan-batch-S378`.
- PAUTH corrected: the active v3 PAUTH for that project allows the new operator-invoked script surface (`cli_extension`) plus the hook and test changes.
- Scope preserved: target paths remain exactly the three paths reviewed in `-001`; no implementation file is added by this proposal.
- Advisory citation corrected: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is now cited and mapped below.

## Prior Deliberations

- `DELIB-20260638` - standing major-release content goal and confirmed work order. Phase 0 explicitly names bridge reliability plus `WI-3380` as build-front stabilization work to pursue before later release waves.
- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` - owner-approved amendment making the bridge-protocol reliability PAUTH v3 active and broadening allowed mutation classes to include source, rules, and governance evidence; the live PAUTH also permits `cli_extension`, `hook_upgrade`, and `test_addition`.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - negative boundary carried forward from the NO-GO: the standing reliability fast lane is for small defect or regression fixes and is not the authority for this improvement-scope tool surface.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive manual governance checks should move into deterministic services. A target-path drift preflight is exactly that class of service.

## Owner Decisions / Input

Existing owner/governance evidence is sufficient for this revision:

- The live project membership row `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-3380` records `WI-3380` as an active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, with source `owner-approved-orphan-batch-S378`.
- The active PAUTH row `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` records owner decision `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT`, status `active`, no expiration, and allowed mutation classes including `cli_extension`, `hook_upgrade`, `source`, and `test_addition`.
- `DELIB-20260638` confirms `WI-3380` as Phase 0 bridge reliability work in the standing major-release order.

No new owner decision is requested by this revision. Loyal Opposition should evaluate whether the existing project membership plus active project PAUTH is sufficient authorization for this improvement-scope script and hook work before GO.

## Requirement Sufficiency

Existing requirements are sufficient. The proposal implements a deterministic helper around the existing file-bridge `target_paths` contract rather than adding a new governance requirement. If Loyal Opposition finds that a narrower WI-specific PAUTH is still required despite the active project membership and active project PAUTH, this thread should receive NO-GO with that specific authorization requirement.

## In-Root Placement Evidence

All declared target paths are inside `E:\GT-KB` and inside GT-KB platform/tooling surfaces:

- `scripts/impl_start_target_paths_preflight.py`
- `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py`
- `.claude/hooks/bridge-compliance-gate.py`

The proposal does not target `applications/`, external repositories, deployment assets, credentials, or Agent Red files.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge index is the authoritative workflow state, and `target_paths` is the implementation envelope this preflight reads.
- `.claude/rules/file-bridge-protocol.md` - defines mandatory implementation-start metadata including `target_paths` and the append-only bridge protocol.
- `.claude/rules/codex-review-gate.md` - implementation work must stay within GO-derived scope; the preflight gives that rule a deterministic path check.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the preflight reads live `bridge/INDEX.md` and the latest operative GO rather than cached summaries.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries concrete governing links and a spec-derived verification map.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps each linked governance claim to tests or smoke checks.
- `GOV-STANDING-BACKLOG-001` - `WI-3380` remains a live P1 backlog item and active project member.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, and work-item metadata are machine-readable in the header.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook integration is limited and parity-aware; this slice enriches the existing hook message path without changing the bridge review authority split.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains in the GT-KB platform root, not in adopter applications.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - this proposal preserves the durable chain from WI to bridge proposal to deterministic script, tests, and report.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the script converts a recurring artifact-envelope check into a durable tool artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation will create a new script and test artifact, so lifecycle evidence is recorded in the bridge thread.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - rationale for moving repetitive manual target-path comparisons into a deterministic service.

## Findings Addressed

### FINDING-P1-001 - Standing fast-lane eligibility fails on live WI origin

Resolved by authorization replacement. This revision no longer cites `PROJECT-GTKB-RELIABILITY-FIXES` or `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`. It cites `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, where live project membership shows `WI-3380` active with `work_item_origin=improvement`. The active project PAUTH is not the reliability fast lane and is the intended authorization envelope for bridge-protocol reliability work.

### FINDING-P1-002 - The proposal introduces a new operator-invoked script surface under a no-new-CLI fast-lane rule

Resolved by authorization replacement. The new script surface remains in scope, but it is now authorized under a PAUTH whose allowed mutation classes include `cli_extension`, plus `source`, `hook_upgrade`, and `test_addition`. This revision does not ask Loyal Opposition to treat a new script as a fast-lane defect fix.

### FINDING-P3-001 - Advisory artifact-oriented development citation is missing

Resolved. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` is cited in Specification Links and mapped in the verification plan.

## Proposed Scope

### New file: `scripts/impl_start_target_paths_preflight.py`

Read-only command surface:

```text
python scripts/impl_start_target_paths_preflight.py --bridge-id BRIDGE_ID [--candidate-paths PATH ...] [--git-diff] [--json]
```

Behavior:

1. Resolve the latest GO file for `--bridge-id` from live `bridge/INDEX.md`.
2. Reuse `extract_target_paths()` from `scripts/implementation_authorization.py` to parse the canonical target glob list.
3. Build a candidate set from explicit `--candidate-paths`, `--git-diff`, or the current implementation-authorization packet.
4. Report `in_scope`, `out_of_scope`, `unused_targets`, and a verdict.
5. Exit 0 for all candidates in scope, 5 for out-of-scope drift, 3 for no GO file, and 4 for missing target paths.

The script is read-only and must not mutate bridge files, MemBase, git state, or authorization packets.

### Hook integration: `.claude/hooks/bridge-compliance-gate.py`

Add a non-blocking advisory call path that can use the preflight for a single `Write` or `Edit` target path to enrich existing bridge-compliance messages. This slice does not promote the preflight to a new blocking gate.

### Tests: `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py`

Focused tests should cover:

- candidate paths that all match target globs
- one and multiple out-of-scope candidates
- glob patterns such as `groundtruth-kb/src/**/*.py`
- informational unused targets
- authorization-packet fallback when candidates are omitted
- no-GO-file exit behavior
- missing-target-paths exit behavior
- JSON output schema
- `--git-diff` path collection through subprocess mocking
- hook-message enrichment remains advisory and does not widen blocking behavior

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic paths and fixture data only; no environment reads or credential material. | Run `gt secrets scan --staged` before commit and inspect diff for fixture-only data. | |
| CQ-PATHS-001 | Yes | Normalize all paths to repository-relative POSIX strings and reject traversal outside `E:\GT-KB`. | Pytest covers path normalization, glob matching, and in-root target evidence. | |
| CQ-COMPLEXITY-001 | Yes | Keep the preflight as small parser, resolver, matcher, and reporter functions. | Ruff plus focused unit tests cover each function path and failure branch. | |
| CQ-CONSTANTS-001 | Yes | Centralize exit codes, verdict labels, and JSON keys in named constants. | Tests assert documented exit codes and verdict strings. | |
| CQ-SECURITY-001 | Yes | Keep the command read-only and fail closed on missing GO or target metadata. | Tests assert no write paths and nonzero exits for missing authority data. | |
| CQ-DOCS-001 | Yes | Document behavior in the bridge proposal and implementation report; avoid broad user docs in this slice. | Implementation report will cite this proposal and command smoke output. | |
| CQ-TESTS-001 | Yes | Add focused pytest coverage for path matching, GO resolution, JSON output, and advisory hook behavior. | Run `python -m pytest groundtruth-kb/tests/test_impl_start_target_paths_preflight.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Emit structured stdout/stderr only and avoid persistent log files. | Tests inspect JSON/stdout and confirm no log path is written. | |
| CQ-VERIFICATION-001 | Yes | Verify with pytest, ruff check, ruff format check, preflight smoke, and implementation-start packet smoke. | Implementation report will include exact command results before VERIFIED review. | |

## Pre-Filing Preflight Subsection

Before filing this revision, the bridge revision helper will run these candidate-file checks:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --content-file candidate-revision-file --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --content-file candidate-revision-file
```

Expected result: blocking requirements pass, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` advisory gap closes, and no mandatory clause evidence gap is reported.

After filing, run the same checks against the indexed operative revision:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight
```

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`: test fixture resolves latest GO from `bridge/INDEX.md` and parses inline `target_paths` through the existing authorization parser.
- `.claude/rules/codex-review-gate.md`: out-of-scope candidate tests prove scope drift is reported before implementation/report work proceeds.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: test proves each run reads the live GO file and does not use a cached extracted target list.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal cites every relevant bridge/governance artifact and maps each to verification evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report must include the concrete test results for the mapped verification rows.
- `GOV-STANDING-BACKLOG-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: implementation-start packet generation must validate project, PAUTH, and `WI-3380` metadata before code edits begin.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: hook regression test verifies the new call path is advisory enrichment only and keeps existing block/pass authority unchanged.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: tests and report evidence show all changed files are inside `E:\GT-KB` and outside `applications/`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: implementation report carries the durable WI/proposal/script/test/report chain and explains artifact lifecycle impact.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: CLI smoke test demonstrates the deterministic service replacing manual target-path comparison.

Verification commands planned for the implementation report:

```text
python -m pytest groundtruth-kb/tests/test_impl_start_target_paths_preflight.py -q --tb=short
python -m ruff check scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py .claude/hooks/bridge-compliance-gate.py
python -m ruff format --check scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py .claude/hooks/bridge-compliance-gate.py
python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --candidate-paths scripts/impl_start_target_paths_preflight.py groundtruth-kb/tests/test_impl_start_target_paths_preflight.py .claude/hooks/bridge-compliance-gate.py --json
python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-target-paths-preflight
```

## Risk And Rollback

- Risk: the project PAUTH is active but `WI-3380` is covered by active project membership rather than an explicit `included_work_item_ids` entry. Mitigation: this revision makes that evidence explicit so Loyal Opposition can GO or reject that exact authorization theory before implementation starts.
- Risk: glob semantics diverge from implementation-start authorization. Mitigation: the preflight imports the existing `extract_target_paths()` parser and tests the matching behavior directly.
- Risk: hook integration changes blocking behavior by accident. Mitigation: implementation keeps hook integration advisory only and adds a regression test proving current block/pass authority is unchanged.
- Rollback: delete the new script and test, and revert the small hook advisory branch. No MemBase, deployment, credential, or external state mutation is part of this proposal.

## Bridge Filing

This file should be inserted at the top of the `gtkb-impl-start-target-paths-preflight` entry in `bridge/INDEX.md` as:

```text
Document: gtkb-impl-start-target-paths-preflight
REVISED: bridge/gtkb-impl-start-target-paths-preflight-004.md
```
