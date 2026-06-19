NEW

# WI-4676 Harness Registry Read Side-Effect Guard

bridge_kind: prime_proposal
Document: gtkb-wi4676-harness-registry-read-side-effect
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-19T08:12:05Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019edee6-dc09-7903-8274-267d09d3bfd1
author_model: Codex
author_model_version: GPT-5
author_model_configuration: desktop automation session

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4676

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_harness_registry_reader_migration.py", "platform_tests/scripts/test_harness_roles.py", "platform_tests/groundtruth_kb/cli/test_harness_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

During verification of `bridge/gtkb-harness-b-headless-dispatch-enable-005.md`,
Loyal Opposition observed that read/status command evidence left
`harness-state/harness-registry.json` dirty with a regenerated projection. That
creates two risks: routine inspection can alter tracked state, and an
implementation report can accidentally omit an out-of-scope generated-file
mutation.

This proposal authorizes a narrow investigation and fix for WI-4676: make
`gt harness roles`, bridge dispatch status/config reads, and their shared reader
paths provably non-mutating with respect to the tracked harness registry
projection. If a projection refresh is genuinely required, it must remain behind
an explicit writer/regeneration path and be named in the implementation report,
not happen as a side effect of status inspection.

All implementation targets are in-root under `E:\GT-KB`; the live proposal file
will be filed under `E:\GT-KB\bridge\`, and any generated test fixtures must
stay inside pytest-managed temporary roots.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — implementation must proceed only after
  bridge review, preserve the numbered bridge audit chain, and file a
  post-implementation report for verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  links the governing specifications before requesting implementation approval.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries
  `Project Authorization`, `Project`, and `Work Item` metadata for the active
  May29 Hygiene authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must include
  tests derived from the read-side-effect and harness-registry requirements.
- `GOV-STANDING-BACKLOG-001` — WI-4676 is the MemBase work item selected from
  the governed May29 Hygiene backlog.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active project authorization
  permits autonomous proposal and implementation flow for unimplemented May29
  Hygiene work items, without bypassing bridge `GO`.
- `REQ-HARNESS-REGISTRY-001` — the harness registry projection is the hot-path
  role/identity dispatch surface; reader commands must not silently mutate it.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — committed readers must use the
  canonical harness-state reader entrypoints and preserve read-only behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — generated projections must be explicit
  refreshes from their source of truth, not hidden write side effects of reads.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the discovered defect is preserved
  as a governed work item and routed through bridge review instead of remaining
  chat-only operational knowledge.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the proposal preserves the plan,
  tests, and verification evidence as durable artifacts before implementation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the verification report will be a
  lifecycle trigger for resolving WI-4676 only after Loyal Opposition verifies
  the implementation.

## Prior Deliberations

- `INTAKE-97211546` — harness registrar role assignment and independent review
  requirements are relevant because this work preserves registry role data as
  the authoritative read surface.
- `INTAKE-5a61f299` — claim-gated implementation-start remains applicable: no
  source or test target may be edited until this proposal receives `GO` and a
  current implementation-start packet is created.
- `INTAKE-2ce995f2` — bounded parallel cross-harness auto-dispatch depends on
  trustworthy read-only status surfaces; this proposal removes a mutation side
  effect that can obscure parallel-run evidence.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — OpenRouter registry integration uses
  the same harness registry projection discipline and reinforces that dispatch
  targets should be read from durable registry surfaces without incidental
  rewrites.

## Owner Decisions / Input

Owner approval for autonomous May29 Hygiene implementation flow is already
recorded in active project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, citing
`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`. No additional owner
decision is required because this proposal stays within WI-4676, does not
authorize formal GOV/SPEC/ADR/DCL mutation, and will still require Loyal
Opposition `GO` before implementation.

## Requirement Sufficiency

Existing requirements sufficient — WI-4676, `REQ-HARNESS-REGISTRY-001`,
`DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
and the bridge/project-authorization specifications above provide enough
requirement detail for a narrow defect fix. No new or revised requirement is
needed before implementation.

## Spec-Derived Verification Plan

The implementation report must map the final diff to these checks:

- `REQ-HARNESS-REGISTRY-001`,
  `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001`, and
  `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`: add or update focused tests that create a
  temporary project root with a tracked harness registry projection, execute the
  relevant read/status code path, and assert the projection file bytes are
  unchanged after the read. If the fix is a write-if-changed guard, include a
  regression proving no rewrite occurs when the generated document is identical
  apart from `generated_at`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `GOV-STANDING-BACKLOG-001`, and
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: run the bridge applicability
  and ADR/DCL clause preflights on the implementation report and include the
  clean outputs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: verify that WI-4676 remains linked to
  the bridge thread and is resolved only after the implementation receives
  `VERIFIED`.

Expected focused commands:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/harness_projection.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_harness_registry_reader_migration.py platform_tests/scripts/test_harness_roles.py platform_tests/groundtruth_kb/cli/test_harness_cli.py
```

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Use only synthetic harness records, project roots, and JSON fixtures; do not add credential-shaped examples. | Bridge helper credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep all implementation mutations inside declared in-root target paths under E:/GT-KB; do not authorize `harness-state/harness-registry.json` itself as a target. | Implementation-start packet target-path validation and `git diff --name-only` scoped to target paths. | |
| CQ-COMPLEXITY-001 | Yes | Prefer a small read/write separation or no-op write guard over broad CLI redesign. | Focused regression tests proving read/status commands leave projection bytes unchanged. | |
| CQ-CONSTANTS-001 | Yes | Preserve existing harness ID, status, and dispatch field names; introduce only narrow helper names if needed. | Source review plus existing harness registry reader tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed behavior for malformed harness-state files and do not relax bridge dispatch eligibility checks. | Negative-path harness reader tests and bridge dispatch config tests. | |
| CQ-DOCS-001 | Yes | Update only docstrings or inline comments needed to clarify read vs explicit regeneration behavior. | Changed-file review and focused tests. | |
| CQ-TESTS-001 | Yes | Add or update focused tests for read/status commands and shared reader paths preserving projection bytes. | Pytest commands listed in the verification plan. | |
| CQ-LOGGING-001 | N/A | No logging or telemetry behavior change is planned. | Diff review. | Read-side-effect repair only. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, Ruff check, Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before report. | Commands recorded in the implementation report. | |

## Risk / Rollback

Primary risk is confusing an intentional projection refresh with an unintended
read-side mutation. The implementation should preserve explicit regeneration
commands while preventing status/read paths from writing, or make no-op
generation compare content before replacing the tracked file. Rollback is a
single commit reverting the source/test changes and leaves the bridge audit
chain intact.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4676-harness-registry-read-side-effect`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the expected implementation repairs a read/status side effect that can
dirty tracked harness registry state without introducing a new user-facing
capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
