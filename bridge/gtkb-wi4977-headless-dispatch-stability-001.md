NEW
author_identity: codex
author_harness_id: A
author_session_context_id: codex-interactive-2026-07-03-wi4977
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Prime Builder interactive/headless dispatch target; model GPT-5.5; reasoning effort Extra High

# Implementation Proposal - Stabilize headless bridge dispatch across LO recipients

bridge_kind: prime_proposal
Document: gtkb-wi4977-headless-dispatch-stability
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4977

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/ollama_harness.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_ollama_dispatch.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Stabilize headless bridge dispatch so active LO recipients B and D and PB recipient A can process without worker storms or duplicate LO retries.

Work item description: Observed 2026-07-03 while enabling B/D LO and A PB headless dispatch: dispatcher daemon launched real Claude and Ollama workers, but re-offered LO documents to other recipients while prior workers were still in flight; terminal-status reconciliation can match sibling bridge slugs by prefix; Ollama can write a valid verdict file and then exit nonzero after session timeout, causing provider-failure backoff and duplicate retry behavior. Scope this WI to global LO in-flight suppression/lease handling, exact bridge-slug latest-status lookup, and success-after-verdict handling for Ollama bridge verdict output.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4977` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `scripts/ollama_harness.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_ollama_dispatch.py`.

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

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY` - active project authorization covering `WI-4977`.

## Proposed Scope

- Fix duplicate LO in-flight dispatch across active Loyal Opposition recipients by claiming or otherwise suppressing a bridge document globally while a headless LO worker is active.
- Fix exact bridge-thread latest-status reconciliation so sibling slugs with shared prefixes cannot be treated as the selected document's terminal status.
- Treat Ollama bridge verdict completion as successful when the selected bridge thread advances to a valid LO status before the harness session deadline.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Targeted dispatcher runtime and daemon tests exercise bridge-authorized LO dispatch and prevent cross-recipient duplicate in-flight work. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted Ollama and bridge-status tests prove the implementation satisfies the proposal's acceptance criteria before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- With B and D both eligible, a live daemon tick must not dispatch the same LO bridge thread to multiple LO recipients while one worker remains active.
- Latest-status reconciliation must only consider files named exactly <bridge-id>-NNN.md for the selected slug.
- Ollama headless bridge review using deepseek-v4-pro:cloud must not return a provider failure after it has written a valid verdict for the selected bridge thread.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/ollama_harness.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_ollama_dispatch.py`

## Recommended Commit Type

`feat`
