NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex interactive Prime Builder; ::init gtkb pb; manual gt bridge file-implementation-proposal filing
author_metadata_source: interactive-codex-session

# Implementation Proposal - Codex exec spawns visible pwsh consoles per shell command during headless dispatch (CREATE_NO_WINDOW not inherited by grandchild pwsh)

bridge_kind: prime_proposal
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 001
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5135

target_paths: ["scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py", "scripts/windows_subprocess.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_windows_subprocess.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Propose a narrow Codex-A shell no-window remediation that adds Codex-only private-desktop containment at dispatch time and replaces the false-green single-echo proof with a governed multi-command no-window smoke before Codex-A dispatch can be re-enabled.

Work item description: ROOT CAUSE of the headless-Codex-dispatch window storm (owner-confirmed per-harness, NOT a general dispatcher problem). The dispatcher launches BOTH harness workers through the identical no-window path (dispatcher_runtime.py ~line 4970: subprocess.Popen(wrapped_command, ..., **wrapper_popen_kwargs), harness-agnostic). Claude Code (LO/Claude-B) runs its Bash-tool commands no-window -> SILENT. Codex (A) exec spawns pwsh.exe for each shell command and does NOT apply no-window to that child pwsh; on Windows CREATE_NO_WINDOW on parent codex.exe is not inherited by grandchild processes, so every Codex shell command pops a visible PowerShell console. Confirmed by: the codex-no-window smoke output showing 'pwsh.exe -Command echo ...'; WI-5065 (resolved) documenting Codex smoke 'reports visible windows'; owner direct observation (Claude dispatch silent, Codex dispatch noisy). The no-window smoke is a FALSE-GREEN: it runs one 583ms echo whose transient pwsh window closes before the before/after enumeration catches it (visible_window_detected:false), so it does not predict real-worker burst behavior. FIX must be at the Codex-shell layer, NOT the dispatcher: e.g., a Codex CLI config/flag to run its sandbox shell headless, or point Codex at a no-window pwsh wrapper, or a dispatch-side containment job-object that forces descendant no-window. Until fixed, keep Codex-A dispatch quiesced (gt bridge dispatch config set-eligibility A --no-can-receive-dispatch). Distinct from WI-5080 (kill-loop watchdogs), WI-5065 (resolved, smoke classification), WI-5134 (verification auto-refresher, blocked on this).

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5135` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/verify_codex_dispatch.py`, `scripts/codex_no_window_smoke_probe.py`, `scripts/windows_subprocess.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_verify_codex_dispatch.py`, `platform_tests/scripts/test_codex_no_window_smoke_probe.py`, `platform_tests/scripts/test_windows_subprocess.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665910` - Loyal Opposition Verdict — GO — gtkb-wi5052-dispatcher-codex-no-window-containment
- `DELIB-202665884` - Loyal Opposition Verdict — VERIFIED — gtkb-wi5049-headless-spawn-guardrails
- `DELIB-20266545` - Review Findings
- `DELIB-20266528` - GO: WI-4248 dispatcher status and no-window launch safety (revision 002)
- `DELIB-202665907` - Loyal Opposition Verdict — NO-GO — gtkb-wi5049-headless-spawn-guardrails

## Owner Decisions / Input

- `DELIB-202666064` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5135`.

## Proposed Scope

- Add a Codex-only dispatch-time containment override for Windows shell execution, preferring windows.sandbox_private_desktop=true when invoking codex exec from dispatcher-owned workers.
- Promote and strengthen the Codex no-window smoke probe into governed source so it exercises repeated/multi-command shell activity instead of a single transient echo.
- Keep Codex-A dispatch quiesced until the strengthened live proof and a real dispatched-worker run show no visible pwsh consoles.
- Do not touch shared harness capability registry, skill manifests, generated harness-state registry, groundtruth.db commit scope, or Alibaba H registration paths.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge file must be NEW authored by Prime Builder and await independent LO GO before protected edits. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must map linked specs to focused tests and real dispatch/no-window proof. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal carries Project Authorization, Project, Work Item, and target_paths metadata. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex Windows dispatch must not rely on hooks/config assumptions without live feature and no-window evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation cannot begin until the owner-decision-backed PAUTH, LO GO, and implementation_authorization.py begin packet all agree. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No source/config/test mutation occurs until the live latest GO and implementation-start packet authorize the exact target paths. |
| `GOV-WORK-TREE-HYGIENE-001` | Changed files and eventual commit scope must exclude unrelated dirty registry, DB, and bridge-state files. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dispatcher spawn composition must preserve centralized dispatch semantics and audit behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The daemon remains the dispatch owner; harnesses stay dispatch consumers and the fix must not restore harness-trigger routing. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Kind-aware dispatchability and worker spawn semantics remain intact while Codex dispatch stays quiesced until proof passes. |

## Acceptance Criteria

- The generated Codex worker command includes the Windows private-desktop containment override only for Codex dispatch on Windows.
- The no-window verification rejects stale, missing, visible-window, or false-green smoke results and records enough evidence to diagnose failure class.
- Focused dispatcher, Codex readiness, no-window smoke, and Windows subprocess tests pass with --basetemp .harness-tmp/wi5135.
- Implementation report must include ruff check and ruff format --check for changed Python files plus scripts/verify_codex_dispatch.py --json evidence.
- Codex-A can_receive_dispatch remains false unless a separate governed enablement step is approved after real worker proof.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/verify_codex_dispatch.py`
- `scripts/codex_no_window_smoke_probe.py`
- `scripts/windows_subprocess.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_windows_subprocess.py`

## Recommended Commit Type

`feat`
