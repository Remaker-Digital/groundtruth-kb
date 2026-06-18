NEW

# gtkb-prefiling-preflight-content-file-bridge-id-optional - Make Content-File Draft Checks Self-Contained

bridge_kind: prime_proposal
Document: gtkb-prefiling-preflight-content-file-bridge-id-optional
Version: 001
Author: Codex Prime Builder automation
Date: 2026-06-18T09:25:00Z

author_identity: codex/A
author_harness_id: A
author_session_context_id: automation:keep-working:2026-06-18
author_model: GPT-5
author_model_version: 2026-06-18 Codex desktop
author_model_configuration: Prime Builder automation, danger-full-access filesystem, approval-policy never

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4636

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4636 captures a recurring pre-filing ergonomics defect: both `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py` require `--bridge-id` even when `--content-file` points to a draft that has no live bridge thread yet. In this run, draft self-review had to pass a placeholder bridge id beside `--content-file` for both mandatory preflight scripts.

This proposal authorizes a narrow CLI fix so content-file mode is self-contained. When `--content-file` is supplied without `--bridge-id`, each tool should derive a stable bridge id from candidate content metadata (`Document:` when present, otherwise the content-file stem with a trailing numeric version removed when applicable) or use an equivalent explicit content-file-mode id. Existing bridge-id behavior for live bridge files must remain unchanged.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep fixtures synthetic and avoid credential-shaped examples. | Bridge helper credential scan and focused review. | |
| CQ-PATHS-001 | Yes | Mutate only the declared in-root source and test target paths. | Applicability preflight, implementation-start target path packet, and `git diff --name-only -- scripts/bridge_applicability_preflight.py scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`. | |
| CQ-COMPLEXITY-001 | Yes | Add a small shared or local derivation helper rather than changing preflight semantics. | Focused unit/CLI tests for content-file-only mode and existing bridge-id mode. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing argument names and derive ids through a clearly named helper. | Ruff and focused tests. | |
| CQ-SECURITY-001 | Yes | Preserve in-root content-file normalization and fail-closed behavior for missing/unreadable files. | Existing path-normalization tests plus new content-file-only tests. | |
| CQ-DOCS-001 | Yes | Update argparse help only if needed to describe optional bridge-id content-file mode. | CLI help assertions or source review. | |
| CQ-TESTS-001 | Yes | Add focused tests for both preflight scripts when `--content-file` is provided without `--bridge-id`. | Targeted pytest commands listed below. | |
| CQ-LOGGING-001 | N/A | These preflight scripts print reports and do not write runtime logs. | Existing report output remains stdout/file-output only. | No logging surface is changed. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, and Ruff format-check before filing the implementation report. | Commands listed in the verification plan. | |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preflight reports are part of bridge proposal/review evidence and must work against live bridge files and pending draft content.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal authors need a reliable draft preflight path before filing a proposal for LO review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project authorization, project, work item, and concrete target paths for the scoped implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must include focused tests proving content-file-only draft checks work for both mandatory preflight scripts.
- `GOV-STANDING-BACKLOG-001` - WI-4636 is a governed MemBase backlog item under `PROJECT-GTKB-MAY29-HYGIENE`; this proposal advances that work item through the bridge.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the repeated draft-check friction is preserved as a work item and implementation proposal instead of remaining an ad hoc workaround.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change improves durable bridge-proposal authoring artifacts and their deterministic prefiling evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the unresolved-new ergonomics defect moves into bridge review without silently changing lifecycle state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root GT-KB platform files.

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - proposal standards work created the current scaffold/self-review workflow that relies on pre-filing draft checks.
- `DELIB-WI4510-CUTOVER-PROPOSAL-RECONCILE-20260614` - bridge state authority moved to dispatcher/TAFE plus numbered bridge files; draft content still needs a prefiling check before it has live state.
- `bridge/gtkb-proposal-target-paths-report-resolution-001.md` - same automation run reproduced the content-file preflight friction while filing WI-4640, confirming WI-4636 remains current.

No prior deliberation found that rejects content-file-only mode for these preflight scripts. This proposal preserves live `--bridge-id` behavior and only removes the extra placeholder requirement for pending draft content.

## Owner Decisions / Input

No new owner decision is required for this proposal. Owner authorization already exists through `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` and active project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, which authorizes proposing implementation for unimplemented May29 Hygiene work items. This proposal does not request formal GOV/SPEC/ADR/DCL mutation, credential action, deployment, destructive cleanup, or production release.

## Requirement Sufficiency

Existing requirements sufficient. WI-4636 states the required behavior: `--bridge-id` should be optional when `--content-file` is supplied to the two pre-filing preflight scripts. The linked bridge-governance and proposal-standard requirements are sufficient to constrain implementation and verification.

## Spec-Derived Verification Plan

Spec-to-test mapping:

```text
GOV-FILE-BRIDGE-AUTHORITY-001
  -> Existing indexed/live bridge-id tests must continue to pass for both scripts.

DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  -> Add content-file-only tests proving draft proposal content can be checked before dispatcher/TAFE publication.

DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
  -> Keep this proposal scoped to the project authorization and target paths declared above; no KB mutation is in scope.

DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  -> Focused tests must execute and pass before the implementation report is filed.

GOV-STANDING-BACKLOG-001 / GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
  -> Preserve the lifecycle trail in this proposal and the implementation report; do not perform untracked formal artifact mutation.
```

Expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short
python -m ruff check scripts/bridge_applicability_preflight.py scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py
python -m ruff format --check scripts/bridge_applicability_preflight.py scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py
```

## Risk / Rollback

Risk is limited to CLI argument handling for two preflight scripts. The main risk is deriving a misleading id for content-file mode; mitigation is to prefer explicit `Document:` metadata when present and keep `--bridge-id` required for live bridge resolution when no content file is supplied. Rollback is a single commit reverting the source/test changes.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-prefiling-preflight-content-file-bridge-id-optional`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the proposed change repairs CLI argument handling in existing preflight tools and adds regression coverage for the defect.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
