NEW

# gtkb-implementation-report-go-verdict-suppression - Suppress GO Dispatch on Implementation Reports

bridge_kind: prime_proposal
Document: gtkb-implementation-report-go-verdict-suppression
Version: 001
Author: Prime Builder (Codex automation)
Date: 2026-06-18T01:18:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-20260618T0118Z
author_model: GPT-5 Codex
author_model_version: 2026-06-18
author_model_configuration: autonomous Hygiene PB automation

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4641

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Live bridge state on 2026-06-18 exposed a protocol-lifecycle hole: two May29 Hygiene implementation-report threads have latest `GO` verdict files (`gtkb-suppress-non-activatable-go-from-pb-scan-004.md` and `gtkb-target-paths-coverage-preflight-004.md`) responding to implementation reports, not implementation proposals. Prime Builder implementation-start then treats the previous `NEW` implementation report as the approved proposal and fails closed because the report lacks proposal-only authorization metadata such as `target_paths` and `Requirement Sufficiency`.

This proposal narrows the bridge dispatch/queue classifier so a `GO` verdict is Prime-dispatchable only when the operative Prime-authored document is an implementation proposal. When the operative Prime-authored document is an implementation report or post-implementation report, `GO` is treated as a non-dispatchable lifecycle anomaly; the normal post-implementation outcomes are `VERIFIED` or `NO-GO`. `NO-GO` remains Prime-actionable so implementation report revisions can still be requested and processed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge status-token semantics, implementation proposal/report distinction, and the requirement that post-implementation verification results in `VERIFIED` or `NO-GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this implementation proposal to cite the governing specification surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project authorization, project, and work-item metadata carried in this file.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the eventual implementation report to prove behavior through spec-derived tests.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs use of the active May29 Hygiene project authorization for this unimplemented work item.
- `GOV-STANDING-BACKLOG-001` - governs backlog/work-item traceability for `WI-4641`.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorization backing `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` for proposing implementation of all unimplemented May29 Hygiene work items.
- `INTAKE-a815f782` - intake record for per-document bridge dispatch suppression; this proposal applies the same per-document principle to malformed `GO` verdicts over implementation reports.
- `INTAKE-5a61f299` - intake record for claim-gated implementation-start; this proposal prevents queue selection from repeatedly presenting work that cannot mint the required implementation-start packet.
- `WI-4641` - captured live defect from the 2026-06-18 Hygiene PB automation run; two May29 Hygiene threads demonstrate the repeated non-activatable `GO` shape.

## Owner Decisions / Input

No new owner decision is required for this proposal. The work is linked to `WI-4641`, a member of `PROJECT-GTKB-MAY29-HYGIENE`, and is covered by active authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, which authorizes implementation proposals for all unimplemented May29 Hygiene work items.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the canonical file-bridge protocol already define the lifecycle distinction: implementation proposals receive `GO`/`NO-GO`, while implementation reports receive `VERIFIED`/`NO-GO`. The implementation only needs to make the dispatch surface honor that existing lifecycle boundary.

## Spec-Derived Verification Plan

Implementation verification must include:

- `GOV-FILE-BRIDGE-AUTHORITY-001`: add a regression test proving a bridge chain whose operative Prime document is `bridge_kind: implementation_report` and whose latest status is `GO` is not Prime-dispatchable, while the same chain with latest `NO-GO` remains Prime-actionable for revision.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run the focused bridge notify tests and report exact results in the implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and `GOV-STANDING-BACKLOG-001`: run the bridge applicability preflight and implementation-start packet check before source edits.

Expected focused command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py -q --no-header
```

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic bridge file content and avoid credential-shaped flags or fixtures. | Bridge helper credential scan plus focused changed-file review. | |
| CQ-PATHS-001 | Yes | Keep implementation within the two declared target paths under the project root. | Implementation-start target-path packet and `git diff --name-only` against the target paths. | |
| CQ-COMPLEXITY-001 | Yes | Add a narrow status/kind dispatchability guard instead of redesigning bridge routing. | Focused pytest coverage for `GO`, `NO-GO`, implementation proposal, and implementation report chains. | |
| CQ-TESTS-001 | Yes | Add regression coverage before reporting implementation complete. | Focused bridge notify pytest command. | |
| CQ-LINT-001 | Yes | Keep Python code lint- and format-clean. | `ruff check` and `ruff format --check` on the changed source/test files. | |

## Risk / Rollback

Risk is concentrated in Prime bridge dispatch/queue visibility. The change must not suppress ordinary `GO` verdicts over implementation proposals and must not suppress `NO-GO` over implementation reports, because Prime still needs to revise reports after a failed verification. Rollback is a single commit revert of `notify.py` and its focused tests.

## Bridge Filing

This proposal is filed under the bridge directory as the next status-bearing numbered bridge file for `gtkb-implementation-report-go-verdict-suppression`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: corrects bridge dispatch lifecycle behavior that currently presents post-implementation `GO` verdicts as Prime implementation work.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
