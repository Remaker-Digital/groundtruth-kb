NEW

# gtkb-codex-mcp-stale-worker-guard - Codex MCP Stale Worker Guard

bridge_kind: prime_proposal
Document: gtkb-codex-mcp-stale-worker-guard
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-23T19:06:36Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef4cc-c15c-7382-bd4f-c4b653e26ef0
author_model: Codex GPT-5
author_model_version: not exposed by current harness
author_model_configuration: Codex desktop, approval_policy=never, GT-KB Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE-001
Project: PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE
Work Item: WI-4776

target_paths: ["scripts/codex_mcp_worker_guard.py", ".codex/gtkb-hooks/codex-mcp-worker-guard.cmd", ".codex/hooks.json", "platform_tests/scripts/test_codex_mcp_worker_guard.py", "platform_tests/scripts/test_check_codex_hook_parity.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement a deterministic Codex development-environment guard for stale MCP sidecar workers. The 2026-06-23 Codex stability diagnosis found 54 stale MCP-related `node.exe` workers, mostly Playwright/browser MCP and Context7-style workers, consuming about 4.8 GB after repeated Codex crashes or aborted tool sessions. A post-restart check showed zero matching stale workers, so this proposal targets prevention and controlled cleanup rather than one-off manual process killing.

The guard must inspect live process state, classify only known Codex MCP worker command-line patterns, report abnormal accumulation during Codex startup or diagnostics, and expose an explicitly invoked cleanup mode that targets only workers classified as stale/detached. Startup integration may warn/report but must not kill processes automatically.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This NEW proposal is filed through the status-bearing bridge file workflow for Loyal Opposition review before implementation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - The proposal cites governing specifications, includes project/work-item/authorization metadata, and maps verification to those requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header includes `Project Authorization`, `Project`, and `Work Item` machine-readable metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must provide spec-derived test evidence, not just narrative confirmation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The implementation must stay in GT-KB/Codex development-environment infrastructure and must not modify adopter application runtime MCP surfaces under `applications/`.
- `GOV-STANDING-BACKLOG-001` - `WI-4776` and `TEST-11236` are the durable MemBase work/test records for this hygiene item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The crash diagnosis crossed the threshold from transient observation to durable project artifact: owner decision, hygiene project, work item, test, and proposal.

## Prior Deliberations

- `DELIB-20265796` - Owner authorized a new hygiene project, work item, and implementation proposal for stale Codex MCP worker prevention after the 54-worker crash diagnosis.

No earlier deliberation found in live context was more specific to Codex desktop MCP sidecar worker lifecycle cleanup. Existing MCP deliberations concern Agent Red/product MCP architecture, not Codex harness-side tool-worker teardown.

## Owner Decisions / Input

- `DELIB-20265796` records the owner decision to create this new hygiene project, work item, linked test, and implementation proposal.
- Project authorization `PAUTH-PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE-001` bounds implementation to `WI-4776` and forbids arbitrary process killing, live MCP worker teardown, unrelated process cleanup, credential changes, production deployment, application runtime MCP gateway work, and broad dispatcher/harness rewrites.

## Requirement Sufficiency

Existing requirements are sufficient for this development-environment hygiene slice. The owner decision and project authorization define the concrete safety boundary; `GOV-STANDING-BACKLOG-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` govern durable capture; the bridge/proposal DCLs govern review and verification. This proposal does not add product behavior or application MCP architecture, so a new formal product SPEC is not required before implementation.

## Spec-Derived Verification Plan

| Specification / governing record | Verification command or evidence | Expected result |
| --- | --- | --- |
| `GOV-STANDING-BACKLOG-001` / `WI-4776` / `TEST-11236` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_mcp_worker_guard.py -q --no-header` | Tests prove stale-worker classification detects known detached Playwright/Context7 MCP workers, excludes live MCP workers, excludes unrelated `node.exe`, and requires explicit cleanup invocation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4776 --json` and `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-CODEX-MCP-WORKER-LIFECYCLE-HYGIENE --json` | The work item remains durably attached to the new hygiene project and cites the owner directive. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-mcp-stale-worker-guard` | Preflight passes with no missing required project/work-item/authorization metadata. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only <implementation-commit>^ <implementation-commit>` inspected against `target_paths` and `applications/` boundary. | No application/adopter files are modified; changes are limited to GT-KB/Codex development-environment guard surfaces listed in `target_paths`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include the targeted pytest result above plus a live read-only diagnostic sample from `scripts/codex_mcp_worker_guard.py --report --json`. | Report provides both deterministic fixture evidence and a live read-only observation; cleanup evidence, if included, must use a dry-run or controlled fake process fixture unless owner explicitly approves a live cleanup run. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge lifecycle: NEW -> GO/NO-GO -> implementation report -> VERIFIED/NO-GO using status-bearing files only. | No implementation starts until a Loyal Opposition GO and matching implementation-start authorization packet exist. |

## Risk / Rollback

Primary risk is over-broad process targeting. Mitigation: make process selection a pure, unit-tested classifier; require exact known MCP command-line families plus detached/stale evidence; default runtime mode is report-only; cleanup mode is explicit and produces a dry-run plan before termination. The implementation must never target arbitrary `node.exe` or live MCP workers for the active Codex session.

Rollback is a single commit revert of the guard script, hook wrapper/registration, and tests. Because startup behavior is report-only, rollback should not require process recovery or data migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-codex-mcp-stale-worker-guard`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - the implementation mitigates a Codex stability failure mode caused by stale local MCP worker accumulation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
