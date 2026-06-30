NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Live harness boundedness and failure classification

bridge_kind: prime_proposal
Document: gtkb-wi4933-live-harness-boundedness-and-failure-classification
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", "scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Existing `WI-4933` work classified spawn-rate and provider backpressure, but live release-health testing exposed remaining failures that are not yet release-acceptable:

- `loyal-opposition:D` latest run `2026-06-30T10-20-39Z-loyal-opposition-D-b7f0b9` exited `1` with `ollama_harness: session timeout exceeded before Ollama chat turn`.
- `loyal-opposition:F` latest run `2026-06-30T10-58-53Z-loyal-opposition-F-692758` had a window-safe process tree but spun until manually stopped, exited `4294967295`, and produced empty stdout/stderr.
- Code inspection found `scripts/openrouter_harness.py` allows up to 80 model/tool turns by default and materializes repository-wide file traversals in `_dispatch_grep` / `_dispatch_glob` before result caps can stop traversal.

These failures mean the dispatcher cannot yet be called release-healthy. Health must classify the failures truthfully, and harness code must bound tool loops and filesystem scans so one LO dispatch cannot spin silently or consume the desktop.

## Claim

Prime Builder proposes a bounded `WI-4933` follow-up: make OpenRouter/Ollama live dispatch failure modes bounded, diagnosable, and truthfully classified in dispatcher health, without changing credentials, topology, or harness eligibility policy.

## Requirement Sufficiency

Existing requirements are sufficient. `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` is active, includes `WI-4933`, and authorizes source/tests for dispatcher health/classification and provider retry/backpressure handling. The live D/F evidence is the same release-health defect family and does not require a new topology or credential authorization.

## In-Root Placement Evidence

All target paths are root-relative GT-KB files under `E:\GT-KB`. No provider credential files or out-of-root harness state are in scope.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher health/status/report must distinguish bounded backpressure, timeouts, manual termination, and genuine failures.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon-owned dispatch must keep bridge work moving or surface actionable failure evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon is the only automated success path; retired trigger fallback and manual-processing fallback are out of scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation changes require approved bridge authorization and role-correct filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map each linked spec to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal declares project authorization, project, work item, and target paths.

## Prior Deliberations

- `DELIB-20266507` - owner authorization for WI-4933 dispatcher backpressure health classification repair, recorded in the active PAUTH.

## Owner Decisions / Input

- `DELIB-20266507` - active owner-decision evidence for WI-4933 dispatcher health/backpressure repair.
- Owner directive in this release thread: continue testing and implementing dispatcher fixes until it is fully operational; do not wait for manual processing.

## Evidence From Live Test

- `gt bridge dispatch health --json` reports WARN with recent-run failures for D, E, and F; D and F remain active release-health blockers.
- `gt bridge dispatch report --json` reports recent run `2026-06-30T10-20-39Z-loyal-opposition-D-b7f0b9` with exit code `1` and stderr bytes, and recent run `2026-06-30T10-58-53Z-loyal-opposition-F-692758` with exit code `4294967295` and zero output bytes.
- Live F process inspection showed `pythonw.exe run_with_status.py -> pythonw.exe scripts/openrouter_harness.py -> pythonw.exe scripts/openrouter_harness.py`; it was no-window safe but CPU-active for minutes with no output.
- `scripts/openrouter_harness.py` currently defines `DEFAULT_MAX_TURNS = 80`.
- `_dispatch_grep` builds `roots = [base] if base.is_file() else list(_iter_text_files(base))`, so a repo-wide grep can enumerate the entire workspace before respecting `max_results`.
- `_dispatch_glob` walks `base.rglob("*")` and can traverse large ignored/runtime trees before the model receives a bounded answer.

## Proposed Scope

- Bound OpenRouter filesystem tool traversal before materializing repository-wide file lists.
- Add skipped-directory and error-tolerant traversal behavior for large runtime directories such as `.git`, `.gtkb-state`, `.venv`, `node_modules`, and other generated caches where appropriate.
- Add a no-progress or repeated-tool guard for OpenRouter tool loops so an LO dispatch cannot spin through many turns without producing a verdict or useful diagnostic.
- Preserve provider retry/backpressure behavior already added for 429/Retry-After.
- Classify Ollama pre-turn timeout and OpenRouter abrupt/manual termination distinctly enough for `gt bridge dispatch health` to be actionable.
- Add focused tests for bounded traversal, timeout/termination markers, and health classification.

## Out Of Scope

- Credential changes or credential-value inspection beyond confirming required environment keys are loaded.
- Dispatcher topology/ranking/eligibility mutation.
- Retiring, waiving, or suspending any harness.
- Restoring the purged cross-harness trigger or single-harness bridge automation path.
- Manual bridge processing as an automated fallback.
- Fixing Cursor child MCP/tool fanout, except that health classification may continue to identify it as unsafe until a separate governed fix is approved.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Add tests proving health/report classification differentiates Ollama timeout, OpenRouter bounded timeout/termination, and generic subprocess failures. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused live or dry-run dispatch after implementation to prove a failed harness produces bounded, actionable evidence instead of silent spin. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Confirm no retired trigger fallback or manual-processing fallback is introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge GO and implementation authorization before protected source/test edits. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each linked spec to exact tests and observed outputs before requesting VERIFIED. |

## Pre-Filing Preflights

This bridge write is filed through the Codex apply-patch bridge-compliance adapter. That adapter runs the pending content-file applicability preflight and ADR/DCL clause preflight before accepting the `bridge/` write. Prime Builder will also cite exact preflight and test outputs in the implementation report.

## Acceptance Criteria

- OpenRouter grep/glob tools stop traversal using deterministic bounds and never materialize the whole workspace before applying result limits.
- OpenRouter dispatch cannot run 80 silent tool turns without a useful diagnostic; repeated no-progress behavior becomes a bounded failure.
- Ollama pre-turn timeout is classified by health/report output as a provider/session timeout, not only generic subprocess execution failure.
- OpenRouter abrupt/manual termination is classified separately from ordinary provider failure when evidence supports that classification.
- Focused unit tests pass for OpenRouter traversal bounds, OpenRouter loop bounds, Ollama timeout marker classification, dispatcher runtime classification, and bridge dispatch health CLI classification.
- `gt bridge dispatch health --json` after implementation provides actionable health findings and no longer hides these failures behind generic `subprocess_execution_failed` alone.

## Risks / Rollback

Risk is moderate because this touches harness execution and health classification. The guardrail is narrow: add boundedness and clearer failure classification without changing which harnesses are eligible or how credentials are supplied.

Rollback is a revert of the source/test changes. Bridge files remain append-only audit evidence.

## Files Expected To Change

- `scripts/openrouter_harness.py`
- `scripts/ollama_harness.py`
- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_ollama_dispatch.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

## Recommended Commit Type

fix
