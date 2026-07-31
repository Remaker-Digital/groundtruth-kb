NEW

# WI-5204 - Preserve H review outcomes across native Stop-hook failures

bridge_kind: prime_proposal
Document: gtkb-wi5204-h-stop-hook-completion-preservation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-12 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f522a-849d-7d43-8c60-0afc829438a6
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5204

target_paths: [".claude/settings.json", "scripts/cloud_harness_base.py", "scripts/check_codex_hook_parity.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_codex_hook_parity.py"]

implementation_scope: shared native-full cloud lifecycle, hook registration, and focused tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

A genuine dispatcher-produced Alibaba H review (`2026-07-12T00-58-06Z-loyal-opposition-H-33480b`) completed 55 DeepSeek V4 Pro turns and 99 governed tool calls, using only 55 of its 600-turn budget. The provider/tool loop was active and productive. Every observed provider turn contained tool calls; while the loop was unwinding, the native `Stop` hook `session_self_initialization.py --emit-wrapup --fast-hook` exceeded the 15-second registration timeout. Because `run_tool_loop` invokes `Stop` unconditionally inside `finally`, that lifecycle timeout replaced the unknown pre-Stop outcome, exited the harness 1, and erased the evidence needed to diagnose whether the loop had a pending result or a different exception.

The exact hook completes in about 4.7 seconds in an uncontended diagnostic run, so this was realistic transient latency rather than a permanently hung hook. This proposal adds event-specific Stop handling and increases the registered wrap-up allowance from 15 to 60 seconds. A Stop timeout, non-blocking non-2 exit, or malformed informational output preserves a pending result or the original pre-Stop exception; an explicit Stop block (exit 2 or valid block JSON) returns the block reason to the model and continues under a bounded eight-block ceiling. Every `PreToolUse` denial, guard-adapter failure, provider error, session exhaustion, and max-turn exhaustion remains fail-closed. The dispatcher still independently requires a role-correct bridge verdict, so preserved final stdout cannot turn prose-only completion into success.

## Specification Links

- `ADR-CLOUD-HARNESS-TEMPLATE-001` — assigns shared native-hook and tool-loop lifecycle behavior to `cloud_harness_base.py` for every adopter.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` — requires H to operate as a dispatchable native-full hook adopter through the shared base.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — requires truthful operational readiness and genuine governed end-to-end proof rather than registration smoke.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` — keeps the separate mutation guard floor fail-closed; this proposal does not weaken it.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — requires an explicit disposition for every active harness when a native harness surface changes.
- `ADR-CROSS-HARNESS-PARITY-001` — requires semantic capability parity by applicability rather than byte-identical hook registration.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires role-correct append-only proposal, verdict, report, and H reproof artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires concrete governing specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the project, work item, and PAUTH linkage above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires independent execution of the mapped timeout/block/guard checks before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5204 and TEST-11358 preserve the observed failure and acceptance boundary before source mutation.

## Prior Deliberations

- `DELIB-202666173` — directs genuine governed proof for A/B/C/D/F/H and correction of every discovered defect with generous evidence-based allowances.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` — establishes generous initial timing and evidence before failure classification; the 15-second lifecycle hook allowance is too tight under observed contention.
- `DELIB-20260711-WI5200-5202-HARNESS-REPAIR-AUTHORIZATION` — authorized and independently VERIFIED the 600-turn/28,800-second H envelope that exposed this separate Stop-hook boundary after productive work.
- `bridge/gtkb-wi5198-native-hook-empty-allow-001.md` — its VERIFIED fix correctly kept native-hook timeout/nonzero/malformed behavior fail-closed as a generic interim rule; WI-5204 supersedes that statement for the `Stop` lifecycle event only, while preserving its `PreToolUse` and guard protections.
- `INTAKE-6308b73f` — establishes a harness as integration plus model plus configuration and prefers maximal-hook operation; this repair preserves native-full hooks rather than bypassing them.

## Owner Decisions / Input

Mike explicitly set the goal that every named harness be verified through genuine governed dispatcher work and every discovered defect be corrected. The decision is recorded as `DELIB-202666173`. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5204-H-STOP-HOOK-20260711`.

## Requirement Sufficiency

Existing requirements are sufficient. The shared-runtime and H adoption ADRs define lifecycle ownership and native-full operation, the onboarding contract requires genuine readiness evidence, and the guard/bridge/verification controls define the fail-closed boundary. The owner decision resolves the timing policy: begin generously and tighten only from sufficient data.

## Spec-Derived Verification Plan

1. `ADR-CLOUD-HARNESS-TEMPLATE-001`: shared-base regressions prove Stop timeout, non-blocking non-2 exit, and malformed informational output preserve a candidate result or the original exception; explicit exit-2/JSON blocks continue the model loop with the reason and fail closed after eight repeated blocks.
2. `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`: registration/parity tests prove the wrap-up Stop allowance is 60 seconds and H continues to use the native-full hook runner rather than bypassing hooks.
3. `DCL-OLLAMA-TOOL-PARITY-GATE-001`: existing and focused tests prove `PreToolUse` timeout/block/nonzero/malformed behavior and the separate guard-adapter empty/error paths remain fail-closed.
4. `GOV-HARNESS-ONBOARDING-CONTRACT-001`: after independent code verification, a genuine dispatcher-produced H run performs real tool work and writes a role-correct bridge verdict; telemetry reports successful completion with a bridge status.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_codex_hook_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_codex_hook_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py scripts/check_codex_hook_parity.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py platform_tests/scripts/test_codex_hook_parity.py
```

Expected result: all focused tests and quality checks pass; diagnostic execution of the registered fast hook completes within the 60-second allowance; explicit Stop blocks continue and are bounded; PreToolUse/guard failures remain fatal; original exceptions are not masked by Stop failures; and H produces a genuine committed LO verdict after re-enable.

## Cross-Harness Disposition

| Harness | Applicability and disposition |
| --- | --- |
| Codex A | Codex does not consume Claude `Stop` registrations as native hooks. `check_codex_hook_parity.py` remains the typed applicability authority and must continue to report the existing non-native disposition without inventing a Codex Stop command. Shared cloud-base Stop semantics do not execute in A. |
| Claude Code B | B consumes `.claude/settings.json` natively. Its wrap-up Stop registration receives the same 60-second allowance; native Claude remains the semantic reference for exit-2/JSON block versus nonblocking hook errors. |
| Antigravity C | C has no Claude-native Stop-hook registration and does not execute `cloud_harness_base.py`; no mirrored command is applicable. Existing optimized startup/overlay behavior is unchanged. |
| Ollama D | D uses the shared cloud base at the guard-adapter floor, not `native-full`; event-specific Stop code is unreachable and its fail-closed mutation guard remains unchanged. |
| OpenRouter F | F uses the shared cloud base at the guard-adapter floor, not `native-full`; event-specific Stop code is unreachable and its fail-closed mutation guard remains unchanged. |
| Alibaba H | H is the affected native-full shared-base adopter. It receives event-specific Stop semantics plus the 60-second registered allowance and must complete a genuine dispatcher-produced verdict before the repair is accepted. |

No typed waiver is requested. A/B/C/D/F/H retain semantic parity according to their declared hook tier, and the focused Codex parity test prevents `.claude/settings.json` from silently creating a false A-equivalence claim.

## Risk / Rollback

The risk is accidentally applying non-blocking Stop semantics to mutation guards. The implementation uses dedicated Stop evaluation rather than a generic `fail_open` switch, and existing PreToolUse/guard tests are mandatory. Increasing one hook timeout adds at most 45 seconds over the prior bound when the hook is genuinely slow, far below the approved 28,800-second session envelope. Rollback may safely restore only the 15-second timeout after event-specific Stop handling lands; reverting event-specific handling would restore outcome masking and must keep H ineligible. The failed run telemetry remains append-only evidence.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5204-h-stop-hook-completion-preservation`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects a reproduced native-full lifecycle failure without adding a new capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
