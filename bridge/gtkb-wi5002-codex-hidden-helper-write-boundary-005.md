REVISED

# WI-5002 Codex Hidden Helper Write Boundary - Revised Sandbox Route

bridge_kind: prime_proposal
Document: gtkb-wi5002-codex-hidden-helper-write-boundary
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-07-04 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex interactive Prime Builder; approval_policy=never; dispatcher operator quiesce active for revision window

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5002

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/verify_codex_dispatch.py"]

implementation_scope: harness-config, tests, kb-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Claim

This revision responds to the Loyal Opposition NO-GO at `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-004.md`. The NO-GO confirmed that retrying Codex against `.codex/skills/verify/helpers/write_verdict.py` is ineffective: both `Copy-Item` and `apply_patch` fail inside Codex headless `--sandbox workspace-write`, even with a live implementation-start packet and work-intent claim.

The revised route is to change the Codex headless invocation surface before retrying the helper update. The implementation should add the in-root `.codex` directory as an explicit writable root for headless Codex dispatch:

```text
--add-dir {{PROJECT_ROOT}}/.codex
```

The implementation must keep `--sandbox workspace-write`, `approval_policy="never"`, `--model gpt-5.5`, and `model_reasoning_effort="xhigh"`. It must not use `--dangerously-bypass-approvals-and-sandbox`, must not switch to `danger-full-access`, and must not ask another harness to write `.codex/**` for Codex.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Codex PB dispatch must complete approved work without manual intervention.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - the fix must not use direct harness-to-harness fallback or a different harness as Codex's writer.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex-specific hook/sandbox gaps must be handled mechanically and audibly.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - helper behavior must not diverge across Claude, Codex, and Cursor after the sandbox route is repaired.
- `ADR-CROSS-HARNESS-PARITY-001` - generated/adapted harness surfaces must preserve behavior parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - revision, implementation, and verification must use the numbered bridge chain and dispatcher-backed state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specs and target paths are cited before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target paths are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the changed invocation and the subsequent `.codex` write path.
- `GOV-STANDING-BACKLOG-001` - WI-5002 remains the canonical backlog item for this blocker.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the failed route and revised route are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must preserve evidence for the rejected broader sandbox routes.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - repeated blocked dispatches triggered this revised lifecycle step.

## Cross-Harness Disposition

- Codex / harness A: behavior change is required only for the Codex headless invocation surface. Codex remains the Prime Builder dispatch target and must perform its own `.codex/**` writes after the invocation is repaired.
- Claude Code / harness B, Antigravity / harness C, Ollama / harness D, Cursor / harness E, OpenRouter / harness F: no dispatch invocation or helper-surface change is proposed for this revision.
- Waivers: none requested. Direct harness fallback remains prohibited. Broad sandbox bypass is explicitly rejected for this revision.

## Prior Deliberations

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner directed stable unattended bridge processing, Codex as PB, Claude/Ollama as LO, and no direct harness fallback.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-003.md`, `-005.md`, `-007.md`, and `-009.md` - repeated Codex `.codex/**` write-denial reports.
- `bridge/gtkb-wi4975-claimed-path-subpath-overmatch-010.md` - Loyal Opposition accepted that identical Codex retries should stop until the write boundary changes.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-001.md` - original bounded repair proposal.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-002.md` - GO verdict for the original repair route.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-003.md` - blocked Codex implementation report proving the original route still could not write `.codex/**`.
- `bridge/gtkb-wi5002-codex-hidden-helper-write-boundary-004.md` - NO-GO confirming the sandbox/tool-approval layer is the blocker.

## Owner Decisions / Input

- Owner decision `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` authorizes bounded work items and implementation authorization records needed to restore stable unattended bridge processing.
- Project authorization `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5002-CODEX-HIDDEN-HELPER-WRITES` authorizes harness-config, KB-state, source/test, and bridge changes for WI-5002 while forbidding direct harness-to-harness launch, credential mutation, production deployment, and retired poller restoration.
- No new owner decision is required for this revision because it chooses the narrowest Codex-owned route and explicitly rejects the higher-risk broad sandbox and non-Codex executor options.

## Findings Addressed

### NO-GO blocker: Codex sandbox denies approved `.codex/**` writes

Response: revise the implementation target from writing the helper immediately to first repairing the Codex headless invocation surface. The specific proposed repair is adding `--add-dir {{PROJECT_ROOT}}/.codex` to harness A's headless argv, preserving `workspace-write` and the existing model/reasoning/approval settings.

### NO-GO path-forward options

Response: reject owner-manual-copy because it would not repair unattended dispatch; reject non-Codex executor because it conflicts with the direct harness-to-harness ban; reject broad sandbox bypass because it is too permissive for the first repair attempt. Proceed with bounded Codex invocation reconfiguration.

## Scope Changes

The original route targeted helper parity files directly. This revision narrows the next implementation to harness invocation/configuration and tests:

- update MemBase/projection state for Codex harness A headless argv;
- regenerate or update `harness-state/harness-registry.json` through the canonical harness projection path;
- add or update tests proving the Codex headless argv includes `--add-dir {{PROJECT_ROOT}}/.codex` while preserving `workspace-write`, `gpt-5.5`, and `xhigh`;
- do not modify `.codex/skills/verify/helpers/write_verdict.py` in this revision.

## Pre-Filing Preflight Subsection

Pre-filing checks were run against this completed draft before live filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md
python scripts/bridge_proposal_wi_id_collision_check.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5002-codex-hidden-helper-write-boundary-005.md --strict
```

Observed result before filing: applicability preflight passed with no missing required or advisory specs; clause preflight passed with no blocking gaps; collision check found only declared `WI-5002`.

## Verification Plan

The implementation report must include spec-to-test mapping and exact observed results for:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/pytest-wi5002-sandbox
groundtruth-kb/.venv/Scripts/ruff.exe check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py scripts/verify_codex_dispatch.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check platform_tests/scripts/test_verify_codex_dispatch.py platform_tests/scripts/test_dispatcher_runtime.py scripts/verify_codex_dispatch.py
```

Required assertions:

- harness A headless argv includes `--model gpt-5.5`;
- harness A headless argv includes `-c model_reasoning_effort="xhigh"`;
- harness A headless argv keeps `--sandbox workspace-write`;
- harness A headless argv includes `--add-dir {{PROJECT_ROOT}}/.codex` or an equivalent normalized in-root `.codex` writable root;
- harness A headless argv does not include `--dangerously-bypass-approvals-and-sandbox`;
- harness A headless argv does not include `--sandbox danger-full-access`;
- no direct harness-to-harness fallback is introduced.

Post-implementation acceptance also requires a subsequent dispatcher-launched Codex PB attempt to write an approved `.codex/**` target or to report a new, different blocker. Another identical access-denied result against the same target means this revision failed.

## Risk And Rollback

Risk: `--add-dir {{PROJECT_ROOT}}/.codex` may still be insufficient if Codex treats `.codex` as a protected configuration namespace even when explicitly added. That failure would be a useful, narrower fact and would not broaden sandbox authority.

Risk: changing the canonical harness registry/projection incorrectly could break Codex dispatch. Tests must verify the full argv shape, and rollback is restoring the previous harness A argv from git plus regenerating the projection.

Rejected alternatives:

- `--dangerously-bypass-approvals-and-sandbox` - too broad for this repair.
- `--sandbox danger-full-access` - too broad for this repair.
- asking Claude, Cursor, or another harness to write `.codex/**` - prohibited direct harness fallback.
- owner manual copy - may unblock one file but does not satisfy unattended dispatch stability.

## Recommended Commit Type

fix - this is a bounded repair to Codex headless dispatch configuration for an existing blocker.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
