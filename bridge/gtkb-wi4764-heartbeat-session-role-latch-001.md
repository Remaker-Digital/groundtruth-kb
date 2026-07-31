NEW

# WI-4764 - Heartbeat Session-Role Latch

bridge_kind: prime_proposal
Document: gtkb-wi4764-heartbeat-session-role-latch
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:26:13Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5.5 Codex
author_model_version: gpt-5.5
author_model_configuration: interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4764-BATCH-B-20260705
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4764

target_paths: [".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", ".codex/gtkb-hooks/session_start_dispatch.py", "scripts/session_role_resolution.py", "scripts/session_start_dispatch_core.py", "config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_start_dispatch_role_cache.py", "platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4764 captures a Codex-side heartbeat/interactive automation role-confusion class: an in-session surface can fresh-read durable role assignment after a mid-session registry change and silently begin behaving as the new durable role, even though the transcript-established interactive session role should remain authoritative for non-dispatcher surfaces. Newer session-role work introduced the shared session-role resolver and tightened the formal role-authority split, so this proposal does not assume the original 2026-06-23 implementation premise is still exact.

This proposal authorizes a bounded current-state correction: audit the Codex heartbeat and UserPromptSubmit/startup surfaces listed in `target_paths`, classify any durable-registry reads as dispatcher-owned, resolver-fallback-owned, identity/provenance-only, or violation, then make the Codex heartbeat path consume session-role evidence or the shared resolver instead of silently re-resolving durable role mid-session. If the current code already satisfies WI-4764, the implementation report may resolve the work item with evidence rather than adding code.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation work requires this proposal, Loyal Opposition review, latest `GO`, implementation-start authorization, implementation report, and verification before WI-4764 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the owner-approved WI-4764 Batch B scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization satisfies owner approval only; it does not bypass bridge `GO`, target paths, report, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing role-authority and bridge-control specifications before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this proposal to the active project authorization, project, and work item.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map each role-authority requirement to concrete tests or evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4764 remains the MemBase backlog authority and must be resolved only with evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposal treats possible stale/partly superseded backlog work as an evidence-backed artifact lifecycle decision instead of silently ignoring it.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, PAUTH, proposal, implementation report, tests, and final backlog disposition must remain traceable as one artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - if implementation finds WI-4764 already covered or superseded, the report must make that terminal/supersession transition explicit with evidence.
- `GOV-SESSION-ROLE-AUTHORITY-001` - non-dispatcher behavior surfaces must not treat the durable harness registry role as behavior authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role-resolution changes must follow the deterministic table and classify registry reads.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - interactive transcript role authority is distinct from durable harness role assignment.
- `ADR-CROSS-HARNESS-PARITY-001` - harness-observable behavior must be equivalent for applicable harnesses or explicitly waived.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - because this proposal targets `.codex/gtkb-hooks/**`, it must declare cross-harness disposition before filing.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved Batch B continuation and the active PAUTH covering WI-4764.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` - owner approved the scoped role-authority boundary correction program.
- `DELIB-20265878` - owner correction that the registry role is dispatcher-authoritative only.
- `DELIB-20265226` - owner directive that transcript-defined interactive role persists across compaction, resume, and contiguous SessionStart-like boundaries.
- `INTAKE-e71dd673` and `INTAKE-d9d4764d` - prior intake records for default interactive session-envelope role continuity; relevant because the implementation must preserve the newer resolver/envelope authority rather than reviving direct registry behavior.

## Owner Decisions / Input

Owner approval is already recorded by `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` and active authorization `PAUTH-PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE-WI4764-BATCH-B-20260705`. No fresh owner decision is required for this proposal. The prior owner-action prompt in this interactive session is superseded by the live PAUTH evidence.

## Cross-Harness Disposition

This proposal touches Codex harness-surface files and therefore requires an explicit parity disposition.

- **Codex:** in scope. The implementation must inspect and, if needed, correct Codex heartbeat/UserPromptSubmit/startup behavior so it consumes session-role evidence or the shared resolver for non-dispatcher behavior authority. Direct durable-registry role reads are allowed only when classified as dispatcher-owned, resolver-fallback-owned, or identity/provenance-only.
- **Claude Code:** parity expected from the existing AXIS 2 UserPromptSubmit path, which already resolves the session-stated role through the shared resolver. Implementation must preserve that behavior and may add/update tests if Codex changes expose a parity drift.
- **Cursor, Antigravity, Ollama, OpenRouter:** no equivalent Codex app-thread heartbeat surface is targeted by WI-4764. Their headless dispatch behavior remains registry-authoritative by design and is not changed by this proposal. If implementation discovers an active non-dispatcher heartbeat/UserPromptSubmit equivalent on any of these harnesses, the implementation report must either include a parity-preserving change inside an approved target path or file a follow-up backlog/bridge item; no owner waiver is requested here.

## Requirement Sufficiency

Existing requirements are sufficient. The operative requirements are `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, and the WI-4764 backlog row. They require the implementation to prevent non-dispatcher heartbeat/interactive surfaces from silently substituting the durable registry role for session-role evidence, while preserving registry authority for dispatcher-owned routing.

## Spec-Derived Verification Plan

| Requirement | Verification |
|---|---|
| `GOV-SESSION-ROLE-AUTHORITY-001` non-dispatcher registry boundary | Add or update tests proving Codex heartbeat/UserPromptSubmit behavior consumes explicit session-role evidence or resolver output, not a fresh durable-registry role read, when a registry role changes mid-session. |
| `DCL-SESSION-ROLE-RESOLUTION-001` assertion 9 registry-read classification | Include implementation-report evidence classifying each touched registry read as dispatcher-owned, resolver-fallback-owned, identity/provenance-only, or violation; violations must be removed or routed through the resolver. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` transcript-role continuity | Run existing and new session-role tests showing transcript/session-envelope role continuity is preserved across SessionStart-like boundaries. |
| `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Verify the implementation either preserves equivalent behavior on applicable harnesses or records a follow-up where an equivalent active surface is discovered outside the approved target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` bridge lifecycle | Implementation must run only after latest `GO` and `implementation_authorization.py begin --bridge-id gtkb-wi4764-heartbeat-session-role-latch`; report must cite target-path authorization evidence. |

Minimum expected verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_start_dispatch_role_cache.py platform_tests/scripts/test_codex_hook_parity_resolution_table_drift.py -q --tb=short
python -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4764-heartbeat-session-role-latch --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4764-heartbeat-session-role-latch
```

## Risk / Rollback

Risk is concentrated in Codex interactive hook routing and startup/heartbeat prompt handling. A mistaken fix could suppress useful interactive notifications or blur headless dispatch routing with interactive role evidence. Keep changes narrow to the listed target paths, preserve dispatcher-owned registry reads, and roll back as one commit if startup/role-resolution regressions appear.

## Bridge Filing

This proposal is filed as the next status-bearing numbered bridge file for `gtkb-wi4764-heartbeat-session-role-latch`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix - the expected implementation corrects a role-confusion defect in heartbeat/interactive role handling.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
