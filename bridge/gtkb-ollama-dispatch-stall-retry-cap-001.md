NEW
bridge_kind: prime_proposal
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-monitor-ollama-hotfix-20260607T0627Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; monitor-ollama hotfix path
author_metadata_source: explicit automation run metadata

# GT-KB Bridge Implementation Proposal - gtkb-ollama-dispatch-stall-retry-cap - 001

Document: gtkb-ollama-dispatch-stall-retry-cap
Version: 001 (NEW implementation proposal)
Author: Prime Builder (Codex, harness A)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4388
Recommended commit type: fix:
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Implementation Proposal

Harden the Ollama Loyal Opposition dispatch path against the live stall observed on 2026-06-07. The trigger currently records a selected-batch signature as dispatched at spawn time, but if the worker later fails, subsequent trigger runs see the same signature and classify the queue as healthy `unchanged`. With nonzero pending work, this permanently stalls the selected batch and prevents later LO-actionable bridge entries from being selected.

The same run also proved that a one-item manual dispatch can launch Ollama D but still fail when the generated verdict omits the mandatory applicability preflight. The dispatch prompt should explicitly require the canonical preflight commands before a GO or VERIFIED write.

## Scope

Implement four narrow changes:

1. Preserve enough `last_launch` metadata in `dispatch-state.json` across unchanged runs to inspect the prior worker stdout/stderr paths.
2. Before returning `unchanged`, detect whether the previous launch for the same signature completed with a fatal worker marker such as max-turn exhaustion or guard denial. If so, record `previous_launch_failed` evidence and allow retry instead of treating the queue as healthy.
3. Cap Ollama Loyal Opposition dispatch to one selected bridge item while keeping the global `DEFAULT_MAX_ITEMS=2` contract unchanged for other harnesses.
4. Update the dispatch prompt so Loyal Opposition workers must run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>` and `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>` before writing GO or VERIFIED verdicts, and must include the clean applicability section in the verdict.

Out of scope:

- No retired OS poller or retired smart poller restoration.
- No alternate bridge queue or duplicate automation.
- No model routing change.
- No production deployment, credential lifecycle action, or formal GOV/ADR/DCL mutation.
- No changes outside the two target paths listed above.

## Requirement Sufficiency

Existing requirements are sufficient for this reliability hotfix. The work is covered by the file bridge authority, the standing reliability fast-lane PAUTH, active Ollama dispatch work item `WI-4388`, and the owner directive in this thread: `AUTHORIZE HOTFIX PATH`.

## Current Evidence

- Live LO scan on 2026-06-07T06:21Z found 8 actionable NEW/REVISED items.
- `scripts/verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB` reported `ready: true`, recipient `D`, route `qwen3-coder-next-cloud`, model `qwen3-coder-next:cloud`, and no missing required tools.
- `scripts/cross_harness_bridge_trigger.py --diagnose --include-rotated-failures` reported LO `last_result=unchanged`, `pending=8`, `selected=2`, and matching `signature` / `last_dispatched` even though no new worker was running.
- Latest prior LO worker logs `2026-06-07T02:27Z`, `2026-06-07T03:49Z`, and `2026-06-07T03:56Z` each contain `ollama_harness: max-turn exhaustion before final assistant text` with empty stdout.
- Manual one-item dispatch at `2026-06-07T06:26:32Z` launched Ollama D but failed with `guard denied Write` because the verdict lacked the mandatory clean Applicability Preflight section.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge INDEX remains the authoritative work handoff surface and dispatch must preserve its lifecycle state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, owner authorization, implementation evidence, and residual risk are preserved through bridge artifacts.
- `GOV-RELIABILITY-FAST-LANE-001` - this is a small reliability correction under the standing fast-lane envelope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries concrete governing specification links and project/work-item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must map every linked requirement to focused tests or command evidence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness dispatch must degrade honestly and surface fallback/failure evidence rather than hiding failed workers as healthy no-ops.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target files and verification artifacts stay inside `E:\GT-KB`.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - Ollama dispatch must keep the full bridge-review tool set available while preserving guard behavior.

## Owner Decisions / Input

- Owner reply in this thread on 2026-06-07: `AUTHORIZE HOTFIX PATH`.
- Carried-forward authorization: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` under `PROJECT-GTKB-RELIABILITY-FIXES` for small reliability fixes.
- Active work item: `WI-4388` tracks Ollama headless Loyal Opposition dispatch reliability.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization.
- `WI-4388` - Ollama headless LO dispatch loses bridge work-intent session id / dispatch reliability follow-up.
- `bridge/gtkb-ollama-dispatch-failure-hardening-001.md` through `-004.md` - earlier VERIFIED hardening baseline; now insufficient because later worker failures are hidden behind selected-batch dedupe.
- `bridge/gtkb-ollama-lo-dispatch-session-propagation-008.md` - prior VERIFIED Ollama dispatch baseline.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | No credential-shaped fixtures or secret values. | Bridge helper credential scan and focused tests. | |
| CQ-PATHS-001 | Yes | Keep edits to the declared target paths. | Implementation authorization packet and scoped diff review. | |
| CQ-COMPLEXITY-001 | Yes | Add small helper functions and branch logic; avoid broad dispatcher refactor. | Focused pytest and source review. | |
| CQ-CONSTANTS-001 | Yes | Add explicit result strings/constants only where needed for diagnostics. | Focused tests assert strings. | |
| CQ-SECURITY-001 | Yes | Preserve guard denials; classify them honestly instead of bypassing them. | Manual dispatch failure evidence and tests. | |
| CQ-DOCS-001 | N/A | Internal dispatcher behavior only. | Bridge proposal/report document the change. | No user-facing docs needed. |
| CQ-TESTS-001 | Yes | Add regression tests for failed prior launch retry, Ollama one-item cap, and preflight prompt instruction. | Targeted pytest. | |
| CQ-LOGGING-001 | Yes | Record prior worker failure in `dispatch-failures.jsonl` without suppressing evidence. | Focused test and live diagnose. | |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, ruff check/format, readiness, diagnose, and a live one-item dispatch check. | Commands captured in the post-implementation report. | |

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`: use this bridge thread for GO, implementation report, and final verification; confirm `bridge/INDEX.md` latest state is updated.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: implementation report records claim, exact files changed, commands, observed results, risk, and rollback.
- `GOV-RELIABILITY-FAST-LANE-001`: keep scope to the two target paths and active reliability work item `WI-4388`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this proposal includes concrete spec links and project authorization metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: add focused tests for each code behavior change and include observed command output in the report.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`: live diagnose must no longer describe known failed worker output as healthy dispatch liveness.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`: `git diff --name-only -- scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` must show only in-root target paths.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001`: live readiness must continue to pass for Ollama D with full bridge-review tools.

Planned commands:

```powershell
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
python -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_cross_harness_bridge_trigger.py
python scripts\verify_ollama_dispatch.py --readiness-only --json --project-root E:\GT-KB
python scripts\cross_harness_bridge_trigger.py --project-root E:\GT-KB --state-dir E:\GT-KB\.gtkb-state\bridge-poller --diagnose --include-rotated-failures
```

## Acceptance Criteria

- An unchanged selected signature with prior fatal worker stderr is no longer reported as healthy `unchanged` liveness.
- The dispatcher records durable failure evidence for prior fatal worker output.
- Ollama Loyal Opposition receives one selected bridge item per dispatch by default through the trigger path.
- The dispatch prompt explicitly names the mandatory applicability and clause preflights before GO/VERIFIED verdict writes.
- Existing non-Ollama dispatch cap and selected-batch signature behavior remain unchanged.

## Risk And Rollback

Risk is moderate but localized to the cross-harness trigger. Retrying after known worker failure can produce duplicate attempts, but only after evidence that the prior worker did not complete successfully. The one-item Ollama cap may slow queue drain but should improve successful completion and prevent later entries from being starved by an oversized selected batch. Rollback is a normal revert of the two target files plus this bridge thread's post-implementation report; append-only bridge audit files remain.
