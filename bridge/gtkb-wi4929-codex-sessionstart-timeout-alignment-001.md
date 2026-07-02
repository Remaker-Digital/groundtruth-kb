NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1778-579b-7f03-a949-9cbae207273a
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access; cwd=E:\GT-KB
author_metadata_source: explicit-runtime-envelope

# Implementation Proposal - Align Codex no-window SessionStart timeout with startup service

bridge_kind: prime_proposal
Document: gtkb-wi4929-codex-sessionstart-timeout-alignment
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4929

target_paths: [".codex/gtkb-hooks/run_py_no_window.py", "platform_tests/scripts/test_codex_no_window_timeout_alignment.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Align the Codex no-window SessionStart child timeout with the startup-service budget so the startup relay is not killed before diagnostics refresh completes.

Work item description: Codex SessionStart is configured with a 180s hook timeout and scripts/session_start_dispatch_core.py allows a 150s startup-service timeout, but the live .codex/hooks.json command invokes .codex/gtkb-hooks/run_py_no_window, whose child process default timeout is 4s unless GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS is set. When startup rendering exceeds 4s, the wrapper can kill session_start_dispatch.py before it writes last-session-start diagnostics or refreshes last-user-visible-startup-*.md, leaving stale relay cache metadata and causing the init-keyword UserPromptSubmit startup relay to fail visibly.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4929` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.codex/gtkb-hooks/run_py_no_window.py`, `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`.

## Specification Links

- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20266349` - Separation Check
- `DELIB-20266233` - Separation Check
- `DELIB-20266351` - GO - gtkb-wi4896-ollama-readiness-console-residual - Headless readiness and worker Python launch
- `DELIB-20266234` - Separation Check
- `DELIB-20266116` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` - active project authorization covering `WI-4929`.

## Proposed Scope

- Teach the Codex no-window Python hook wrapper to give `session_start_dispatch.py` the long startup-service headroom when no explicit `GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS` override is present.
- Keep the short default timeout for ordinary non-SessionStart hook children so the containment behavior does not widen accidentally.
- Add focused regression coverage for SessionStart timeout alignment and ordinary-child default timeout preservation.
- Do not change hook routing policy, provider eligibility, credentials, production deployment, or retired poller behavior.

## Cross-Harness Disposition

- Codex (`.codex/gtkb-hooks/run_py_no_window.py`): in scope. This is the only runtime surface affected by the diagnosed WI-4929 failure because the Codex no-window wrapper owns the child timeout for the `.codex/hooks.json` SessionStart invocation.
- Claude Code: behavioral parity is preserved. Claude does not invoke the Codex no-window wrapper; its shared SessionStart startup-service timeout remains governed by `scripts/session_start_dispatch_core.py` and existing startup-service coverage.
- Cursor / Antigravity / Ollama / OpenRouter / API harness adapters: behavioral parity is preserved by non-applicability. These harnesses do not invoke `.codex/gtkb-hooks/run_py_no_window.py` for SessionStart, and this proposal does not change their hook routing or startup relay behavior.
- Cross-harness invariant: the shared startup-service timeout contract stays in `scripts/session_start_dispatch_core.py`; the implementation is limited to the Codex wrapper layer that currently short-circuits that shared contract.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Run focused tests proving `session_start_dispatch.py` receives enough no-window wrapper headroom to refresh startup relay diagnostics. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run focused Codex hook runtime containment tests proving the Windows no-window wrapper remains the active hook path. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- SessionStart dispatch invoked through the Codex no-window wrapper no longer inherits the 4-second ordinary-child timeout by default.
- Ordinary non-SessionStart children still default to the short wrapper timeout unless `GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS` is set.
- Focused pytest coverage passes for the timeout-selection logic without mutating `.codex/hooks.json`.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.codex/gtkb-hooks/run_py_no_window.py`
- `platform_tests/scripts/test_codex_no_window_timeout_alignment.py`

## Recommended Commit Type

`feat`
