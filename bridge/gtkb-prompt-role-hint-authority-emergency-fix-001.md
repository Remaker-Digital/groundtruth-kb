NEW

# Implementation Proposal - Prompt Role Hint Authority Emergency Fix

bridge_kind: prime_proposal
Document: gtkb-prompt-role-hint-authority-emergency-fix
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ec1bf-217a-75e2-aabf-6938507c9ad3
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop; owner-declared emergency Prime Builder prompt; durable registry currently disagreeing with prompt role hint

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3480

target_paths: ["scripts/workstream_focus.py", "scripts/session_start_dispatch_core.py", "scripts/check_codex_hook_parity.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/scripts/test_governing_specs_preserved.py", "platform_tests/scripts/test_canonical_init_keyword_assertions.py", "platform_tests/scripts/test_canonical_init_keyword_syntax.py", "platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This emergency fix corrects an agent-facing role-authority regression: an explicit prompt role hint from the owner, dispatcher, or automation must be honored by the receiving agent even when the durable harness registry currently disagrees. The durable registry remains the routing/fallback source of truth when no prompt/session declaration exists; it is not a veto over explicit prompt content from the receiving agent's perspective.

The immediate failure mode was a Codex automation prompt that explicitly said "You are authorized to operate as an autonomous Prime Builder" but was blocked before implementation because the durable registry assigned Codex harness A to Loyal Opposition. Per the owner directive in this session, that behavior is wrong. The prompt content is authoritative to the agent, and registry disagreement should be audited or warned, not used to reject the work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` remains the canonical bridge queue and this proposal uses the bridge path before protected source edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the role-resolution, session-role, init-keyword, and cross-cutting governance surfaces it changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries project authorization, project, and work-item metadata for protected implementation work.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps changed behavior to targeted tests.
- `GOV-STANDING-BACKLOG-001` - the fix is scoped under existing interactive session role override `WI-3480` regression/integration coverage rather than creating duplicate backlog work.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - R1, R2, R4, and R5 govern prompt/session-declared authority, registry fallback, warn-not-override behavior, and no invalidation on registry mismatch alone.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - the role is owner-declared, not agent-detected; this fix applies that principle to explicit prompt prose, not only `::init` markers.
- `DCL-SESSION-ROLE-RESOLUTION-001` - session role resolution must prefer valid prompt/session declarations over durable fallback.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable registry authority is retained for headless routing and fallback, but interactive/agent-side declared role hints control the current receiving session.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - the existing session-role marker design is extended to non-keyword explicit prompt role hints.
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` - dispatcher keyword handling must be updated so a keyword/registry mismatch audits without rejecting the explicit prompt keyword.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - the canonical keyword grammar remains `::init gtkb pb|lo`; the semantics of registry mismatch change from drop to prompt-authorized audit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all source, test, bridge, and runtime artifacts are in-root under `E:\GT-KB`.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness behavior remains symmetric: both harnesses honor explicit prompt keywords and audit registry disagreement.
- `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` - dispatch failure/audit records remain investigable; this fix preserves audit logging while removing the blocking drop behavior.

## Prior Deliberations

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` - owner decision that role authority is owner-declared, not agent-detected; the agent should proceed from declared role context and surface registry mismatch as warning/audit.
- `bridge/gtkb-role-authority-declared-not-detected-004.md` - VERIFIED ceremony thread that added the ADR and DCL governing declared-not-detected role authority.
- `bridge/gtkb-role-resolution-r1-r5-assertion-enforcement-003.md` / `-004.md` - GO'd regression guard proposal for R1-R5. It explicitly described the strict-drop carve-out as permitted; the current owner emergency directive supersedes that carve-out.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-005.md` - established the session-role marker mechanism that this fix extends from canonical init-keyword prompts to explicit ordinary prompt role hints.
- `bridge/gtkb-canonical-init-keyword-syntax-001-009.md` and related strict-drop threads - historical basis for the old strict-drop behavior. The current owner directive identifies that behavior as erroneous for the receiving agent's prompt authority.
- Owner emergency prompt, 2026-06-13: "We do not want any agent to reject the explicit hint in a request because it doesn't match the harness registry's information. That is an error - the content of the prompt is always authoritative from the perspective of an agent."

## Owner Decisions / Input

Owner emergency direction is explicit in the current session and is the approval evidence for revising the previous strict-drop interpretation: prompt content is authoritative from the receiving agent's perspective, and registry mismatch must not block an explicit role hint. The proposal binds to active, included work item `WI-3480` because the correction updates the cross-harness regression/integration behavior for the interactive-session-role override family.

No additional owner decision is required for this source fix. The change does not mutate formal specs, project records, production deployments, credentials, or external systems.

## Requirement Sufficiency

Existing owner direction and existing requirements are sufficient for this scoped governance correction. The implementation applies `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` and `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` to the failing runtime path that was still enforcing the old registry-veto behavior.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Keep the proposal and implementation free of credentials and environment values. | Bridge helper credential scan and diff review. | |
| CQ-PATHS-001 | Yes | Mutate only listed in-root target paths under `E:\GT-KB`. | Applicability preflight and `git diff --name-only -- <target paths>`. | |
| CQ-COMPLEXITY-001 | Yes | Make the narrow role-authority correction without redesigning dispatch routing. | Focused prompt-hint and dispatcher tests. | |
| CQ-CONSTANTS-001 | Yes | Preserve canonical init keyword grammar and dispatch-failures path constants unless a test requires a renamed audit kind. | Canonical init keyword and parity tests. | |
| CQ-SECURITY-001 | Yes | Preserve audit logging for registry disagreement while removing the registry-veto block. | Dispatcher mismatch tests assert prompt authorization plus audit evidence. | |
| CQ-DOCS-001 | Yes | Update comments/docstrings that still describe silent drop as required behavior. | Source review and strict-drop test updates. | |
| CQ-TESTS-001 | Yes | Update/add tests for explicit prompt prose, keyword mismatch authorization, and no registry-mismatch invalidation. | Targeted pytest commands in the verification plan. | |
| CQ-LOGGING-001 | Yes | Keep dispatch disagreement records in `.gtkb-state/bridge-poller/dispatch-failures.jsonl` or an equivalent existing audit surface. | Dispatcher audit tests. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest plus ruff check and format check before filing the implementation report. | Commands recorded in the post-implementation report. | |

## Proposed Implementation

1. Update `scripts/workstream_focus.py` so ordinary prompts with explicit role declarations write the same ephemeral session-role marker used by canonical init-keyword prompts. Supported explicit hints include the automation phrasing "You are authorized to operate as an autonomous Prime Builder" and equivalent direct Loyal Opposition declarations. Ambiguous prompts that declare both roles fail soft and write no marker.
2. Update `scripts/session_start_dispatch_core.py` so `GTKB_BRIDGE_POLLER_RUN_ID` plus a canonical dispatch keyword no longer returns `StartupDecision.STRICT_DROP` when the keyword mode is outside the receiver's durable role set or the durable role set cannot be read. Instead, it authorizes the prompt keyword and writes an audit record describing the registry disagreement or unreadable durable role state.
3. Preserve the dispatch-failures JSONL audit surface so registry drift remains diagnosable. Rename or reframe the helper/tests as needed, but do not use the audit record as a work-blocking veto.
4. Update `scripts/check_codex_hook_parity.py` so parity checks expect prompt-authorized/audited mismatch semantics instead of requiring `StartupDecision.STRICT_DROP` in the dispatcher decision path.
5. Update all strict-drop regression tests to assert the corrected behavior: explicit prompt keyword/hint wins, durable registry mismatch audits, and no agent-side gate invalidates the work solely because the registry disagrees.

## Spec-Derived Verification Plan

| Specification | Test or Verification Command | Expected Result |
| --- | --- | --- |
| `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`, `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001`, `DCL-SESSION-ROLE-RESOLUTION-001` | `python -m pytest platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short` | PASS; explicit Prime Builder and Loyal Opposition prompt prose writes the session-role marker; ambiguous/non-role prompts do not. |
| `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`, `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `python -m pytest platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_governing_specs_preserved.py platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short` | PASS; canonical keyword syntax remains strict, but keyword/registry disagreement authorizes the prompt and records audit evidence instead of strict-dropping. |
| `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short` | PASS; R5 no longer carries a strict-drop carve-out for registry mismatch invalidation. |
| Cross-harness parity | `python -m pytest platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py -q --tb=short` | PASS; parity checker enforces the corrected prompt-authorized/audited mismatch behavior. |
| Lint/format for touched code | `python -m ruff check scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_governing_specs_preserved.py platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` | PASS. |
| Format check for touched code | `python -m ruff format --check scripts/workstream_focus.py scripts/session_start_dispatch_core.py scripts/check_codex_hook_parity.py platform_tests/hooks/test_workstream_focus_session_role_marker.py platform_tests/scripts/test_claude_session_start_dispatcher.py platform_tests/scripts/test_codex_session_start_dispatcher.py platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_governing_specs_preserved.py platform_tests/scripts/test_canonical_init_keyword_assertions.py platform_tests/scripts/test_canonical_init_keyword_syntax.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` | PASS. |

## Risk / Rollback

Risk is concentrated in the bridge-dispatch receiver path. The old strict-drop behavior protected against misdirected headless dispatch by rejecting a keyword that did not match durable registry assignment. The owner has now clarified that this protection is the bug for agent-facing prompt authority. The mitigation is to preserve structured audit logging and keep durable registry routing/fallback behavior unchanged when no explicit prompt/session hint exists.

Rollback is a single scoped revert of this implementation commit. The rollback would restore strict-drop behavior, but that would also restore the emergency blocker identified by the owner.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-prompt-role-hint-authority-emergency-fix` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

fix: correct prompt role hint authority and remove registry-veto strict-drop behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
