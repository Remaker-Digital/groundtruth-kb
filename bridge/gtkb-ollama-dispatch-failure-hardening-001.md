NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-20260607T0118Z
author_model: GPT-5 Codex
author_model_version: 2026-06-07
author_model_configuration: automation keep-working prime-builder; owner-authorized dispatch hardening
author_metadata_source: explicit Codex automation metadata

# GT-KB Bridge Implementation Proposal - gtkb-ollama-dispatch-failure-hardening - 001

bridge_kind: implementation_proposal
Document: gtkb-ollama-dispatch-failure-hardening
Version: 001 (NEW implementation proposal)
Author: Prime Builder (Codex, harness A)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4388
Recommended commit type: fix:
target_paths: ["scripts/ollama_harness.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py"]

## Implementation Proposal

Harden the Ollama Loyal Opposition dispatch path so bridge verification sessions do not disappear behind harness process failures when the intended LO target exists but a tool command exits nonzero or an optional file read fails.

This proposal addresses the defect observed during recovery of `gtkb-core-spec-intake-current-root-phase3a-cli`: the live registry had Ollama harness D active as Loyal Opposition, but the trigger surfaced `no_active_target_for_role` after recording `ollama_dispatch_not_ready`, and the Ollama harness aborted when normal review commands returned nonzero evidence.

## Scope

Implement three narrow changes:

1. In `scripts/ollama_harness.py`, make ordinary Bash command nonzero exits return a model-visible tool result containing the return code, command, stdout, and stderr. Guard denials and timeouts remain fatal harness errors.
2. In `scripts/ollama_harness.py`, make missing or unreadable `Read` targets return a model-visible read error instead of crashing the worker with an unhandled `FileNotFoundError`.
3. In `scripts/cross_harness_bridge_trigger.py`, separate active event-capable target resolution from runtime readiness. If an active Ollama LO target exists but `/api/tags` is not ready, preserve `ollama_dispatch_not_ready` as the dispatch result instead of reclassifying it as `no_active_target_for_role`.

Out of scope:

- No model routing changes.
- No bridge protocol status vocabulary changes.
- No retired OS poller or retired smart poller restoration.
- No production deployment, push, or credential lifecycle action.
- No modification of the core-spec implementation files already awaiting LO verification.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped reliability fix. The work is covered by the file bridge authority, reliability fast-lane project authorization, existing Ollama LO dispatch work item `WI-4388`, and the owner directive in this session to perform protocol-approved recovery plus dispatcher/LO harness hardening until VERIFIED.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

- Owner directive in this thread: "I authorize you to do anything you need to do for this: a protocol-approved recovery for the malformed pending report, then hardening the dispatcher/LO harness behavior. Please keep working until your fix(es) is/are VERIFIED."
- Existing owner authorization: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` backs `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for small source/test/hook reliability fixes.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization.
- `WI-4388` - open work item for Ollama headless LO dispatch work-intent/session failures.
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-008.md` - prior VERIFIED Ollama LO dispatch reliability work and current baseline.
- `bridge/gtkb-core-spec-intake-current-root-phase3a-cli-004.md` - live corrected report whose verification exposed the current hardening need.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic command output and no credential-shaped fixtures. | Bridge helper scan and focused tests. | |
| CQ-PATHS-001 | Yes | Keep changes under the declared current-root target paths. | Implementation-start packet, scoped diff review, and bridge preflights. | |
| CQ-COMPLEXITY-001 | Yes | Add small error-formatting/readiness-classification branches without broad refactor. | Focused pytest and Ruff. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing result strings such as `ollama_dispatch_not_ready`. | Dispatcher tests assert exact classification. | |
| CQ-SECURITY-001 | Yes | Preserve guard-denial and timeout failure behavior; only ordinary command exit codes become model-visible. | Existing verify_ollama_dispatch guard-denial checks plus focused pytest. | |
| CQ-DOCS-001 | N/A | No user-facing docs change required for internal harness error handling. | Proposal/report record behavior. | Internal dispatch harness behavior only. |
| CQ-TESTS-001 | Yes | Add focused regression coverage for Bash nonzero, missing Read, and readiness classification. | `pytest platform_tests/scripts/test_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short`. | |
| CQ-LOGGING-001 | Yes | Keep dispatcher failure records precise and non-duplicative. | Test failure records do not include false `no_active_target_for_role`. | |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, live Ollama readiness verification, Ruff check, Ruff format-check, bridge applicability, and ADR/DCL clause preflight. | Commands recorded in post-implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: file proposal/report through the bridge and run `show_thread_bridge.py` to confirm no INDEX drift.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: post-implementation report must preserve claim, changed files, commands, observed results, risks, and rollback.
- `GOV-RELIABILITY-FAST-LANE-001`: keep the change small, source/test scoped, and tied to active reliability work item `WI-4388`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal carries concrete spec links and project-linkage metadata before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: add focused tests for each behavior change and carry the mapping into the implementation report.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: verify Codex/Ollama fallback behavior through repo-native tests and the live `scripts/verify_ollama_dispatch.py` suite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: `git diff --name-only` for this thread must stay under `E:\GT-KB` and the declared target paths.

Additional planned commands:

```powershell
python -m pytest platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py -q --tb=short
python scripts\verify_ollama_dispatch.py
python -m ruff check scripts\ollama_harness.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py
python -m ruff format --check scripts\ollama_harness.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_ollama_dispatch.py platform_tests\scripts\test_verify_ollama_dispatch.py
```

## Acceptance Criteria

- Ordinary Bash command exit codes are observable by the Ollama model and no longer terminate the worker process by default.
- Missing in-root Read targets are observable by the Ollama model and no longer terminate the worker process by default.
- Dispatcher target resolution distinguishes "no active target" from "active target not runtime-ready".
- Focused tests cover the three behavior changes.
- The corrected core-spec report can be sent back through Loyal Opposition verification after the hardening lands.

## Risk And Rollback

Risk is low and localized to dispatch harness behavior. Returning nonzero Bash output may let a model continue after a failed command, but that is the desired bridge-verification behavior because mandatory preflight exit codes are review evidence. Guard denials remain fatal to preserve file-safety boundaries. Rollback is a normal revert of the two script changes and focused tests.
