NEW

# WI-5280 - Recover H reviews after a transient native PreToolUse timeout

bridge_kind: prime_proposal
Document: gtkb-wi5280-native-pretool-timeout-recovery
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-15 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; governed fleet stabilization

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5280-NATIVE-HOOK-TIMEOUT-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5280
Test: TEST-11435

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make one transient native-full `PreToolUse` hook timeout deny only the affected
tool invocation instead of terminating the entire Alibaba H review. The tool
must remain fail-closed: it is not executed, the model receives a bounded and
attributable denial, and a later model turn may recover when the hook is
healthy. Existing repeated no-progress detection remains the bounded escape
from a hook that continues timing out.

This is separate from WI-5267. WI-5267 repaired Alibaba thinking-mode
publisher request compatibility and is independently VERIFIED in commit
`2eb034dd`. WI-5280 addresses the later local failure in dispatcher run
`2026-07-15T16-35-03Z-loyal-opposition-H-27c83c`, where H completed 16
substantive review turns and 46 read-only tool calls before one
`formal-artifact-approval-gate.py` invocation exceeded its configured
five-second allowance and the adapter exited 1.

## Defect Evidence And Causal Boundary

- Run telemetry identifies H, Loyal Opposition role, model `deepseek-v4-pro`,
  16 turns, 46 tools, and 705 seconds of substantive work.
- Stderr is exact: `native hook timed out: PreToolUse: ...formal-artifact-approval-gate.py`.
- A read-only local probe of that exact hook completes in approximately 0.17
  seconds, establishing intermittent delay rather than a permanently broken
  hook.
- `invoke_native_hooks` currently raises `CloudHarnessError` for a timed-out
  `PreToolUse` hook. The exception escapes before the model loop can convert a
  hook block into its existing `ERROR: native hook blocked <tool>` result.
- The model loop already prevents execution when a block reason is returned
  and already terminates repeated identical tool-call loops through
  `MAX_REPEATED_TOOL_SIGNATURE_TURNS`. No new unbounded retry mechanism is
  required.
- The failure occurred after WI-5267 and does not implicate provider request
  shape, tool selection, bridge publication, dispatcher selection, or lease
  handling.

## Proposed Implementation

1. In `invoke_native_hooks`, preserve the existing fail-soft treatment for
   `Stop`, `PostToolUse`, and `UserPromptSubmit` timeouts.
2. For a timed-out `PreToolUse` command, return a canonical block decision
   instead of raising. The reason must identify the event, requested tool,
   bounded hook command label, and configured timeout without including tool
   input, provider content, environment values, or credentials.
3. Return immediately after the timeout. Do not execute later hooks or the
   requested tool under a partially evaluated guard chain.
4. Let the existing model-loop block path append the denial as the tool result.
   A later provider turn may choose the same or another tool and re-run the
   full hook chain from the beginning.
5. Preserve existing repeated-tool-signature detection as the hard bound for a
   hook that repeatedly times out. Do not add retries inside a single hook
   invocation and do not extend the configured hook timeout.
6. Preserve fatal fail-closed behavior for malformed hook configuration,
   unsupported hook types, nonzero `PreToolUse` exits, malformed non-empty
   output, non-object output, and explicit block/deny decisions.
7. Add focused shared-base tests proving timeout-to-block conversion, no tool
   execution, one-turn recovery, repeated no-progress termination, bounded
   diagnostics, and unchanged non-timeout failures.
8. Add an Alibaba wrapper regression proving native-full H inherits the shared
   behavior without a provider-specific bypass.

## Explicit Exclusions

- No direct Alibaba, provider, or harness invocation.
- No change to `.claude/settings.json` or any hook implementation.
- No hook timeout increase, hidden retry, or fail-open tool execution.
- No publisher-recovery, tool-choice, provider transport, prompt, token,
  turn-budget, model/session-window, worker-lifetime, or lease change.
- No dispatcher runtime, config, selection, eligibility, role, model, lease,
  lock, or telemetry mutation.
- No bridge writer, verdict attribution, session-envelope lifecycle, PAUTH,
  credential, external-system, deployment, release, push, or unrelated work.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-HARNESS-ONBOARDING-CONTRACT-001`
requires a native-full harness to preserve governance while completing genuine
work; `DCL-OLLAMA-TOOL-PARITY-GATE-001` requires fail-closed tool mediation;
the cloud and Alibaba ADRs establish the shared-base/native-full boundary; and
the bridge, project-authorization, provenance, verification, and artifact
lifecycle specifications define the exact execution gates. No new or revised
requirement is needed before implementation.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - H must complete genuine governed work without bypassing native hooks.
- `ADR-CLOUD-HARNESS-TEMPLATE-001` - the behavior belongs in the reusable shared cloud harness base.
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` - H is the native-full affected adopter and needs focused wrapper proof.
- `DCL-OLLAMA-TOOL-PARITY-GATE-001` - a timed-out guard must deny tool execution and never become fail-open.
- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001` - verification must retain truthful H/session outcome evidence without claiming success absent a target-authored verdict.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation and verification remain in the numbered bridge lifecycle.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - any later H verdict must remain attributable to its exact dispatch session.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the concrete governing requirements before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification requires the mapped focused tests and observed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI, test, and exact targets are explicit.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - claim and implementation start must evaluate the live bounded PAUTH.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not replace independent GO, claim, start, report, or verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the observed failure is preserved as WI-5280 and TEST-11435.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - evidence, implementation, test, report, verdict, and commit remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - candidate, authorized, implemented, and verified states remain distinct.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all code, tests, and evidence remain under `E:/GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces bridge and start gates where native Codex hooks are unavailable.
- `GOV-STANDING-BACKLOG-001` - the failure remains visible until independently verified and committed.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner directs governed repair of Alibaba H and all discovered fleet defects while preserving isolation and non-bypass gates.
- `DELIB-202666160` - independent GO on WI-5204 established the event-specific pattern: lifecycle failures may be recoverable while `PreToolUse` tool execution remains fail-closed.
- `DELIB-202666159` - WI-5204 VERIFIED preserved H outcomes across native Stop-hook failures and explicitly retained fatal `PreToolUse` enforcement in that earlier scope; WI-5280 narrows only timeout handling from fatal session exit to fail-closed tool denial.
- `DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT` - direct evidence that cloud harnesses must never weaken or bypass the native tool-governance chain.
- `bridge/gtkb-wi5267-alibaba-thinking-mode-publisher-recovery-004.md` and commit `2eb034dd` - independently verified provider publisher recovery predecessor; distinct from this local hook timeout.

No prior deliberation rejects fail-closed per-tool timeout denial with bounded
session recovery. This proposal does not rely on `DELIB-202666173`, which is an
LO verdict rather than owner-approval evidence.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` records Mike's
  explicit directives to make Alibaba work and to advance each discovered
  fleet defect through WI, test, PAUTH, bridge, implementation, independent
  verification, and focused commit.
- The active PAUTH cites that canonical owner-conversation record and permits
  only source/test mutation for WI-5280 after all later gates pass.

## Cross-Harness Disposition

| Harness | Disposition |
| --- | --- |
| A Codex | Prime author only; no native-full runtime behavior change and no LO action. |
| B Claude | Native Claude hooks remain authoritative; no settings or Claude runtime change. |
| C Antigravity | No native-full shared-base path; no behavior change. |
| D Ollama | Guard-adapter floor does not enter `invoke_native_hooks`; no behavior change. |
| F OpenRouter | Guard-adapter floor does not enter `invoke_native_hooks`; no behavior change. |
| H Alibaba | Affected native-full adopter; receives focused wrapper regression and later genuine governed proof. |

No parity waiver is requested. The shared implementation is intentionally
reachable only for profiles already classified `native-full`.

## Spec-Derived Verification Plan

| Requirement | Verification and expected result |
| --- | --- |
| Native-full governance and tool parity | Shared-base unit tests simulate one timed-out `PreToolUse` hook; result is a block, requested tool call count remains zero, and no hook/input secret appears in diagnostics. |
| Bounded recovery | Tool-loop test supplies a timeout on one provider turn and a healthy hook on the next; later tool execution and governed completion succeed within existing turn/signature bounds. |
| Repeated failure bound | Repeated identical timed-out tool requests terminate through the existing no-progress ceiling; no unbounded internal retry occurs. |
| Non-timeout fail-closed preservation | Existing and focused tests require nonzero, malformed, non-object, unsupported, and explicit-block paths to retain their current denial/error behavior. |
| Alibaba adoption | H wrapper test proves `native-full` uses the shared timeout-to-block behavior without skipping hooks or changing provider request handling. |
| Provenance and truthful completion | No code change claims a verdict; after independent code verification, a separate owner-routed dispatcher proof must correlate any H verdict to H's exact dispatch/session before fleet eligibility is restored. |
| Project and bridge gates | Applicability and clause preflights pass; implementation begins only after independent GO, exact claim, and implementation-start authorization. |
| Static and diff quality | Ruff check, Ruff format check, focused pytest, and `git diff --check` pass on exactly the three target paths. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
git diff --check -- scripts/cloud_harness_base.py platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_alibaba_cloud_studio_harness.py
```

## Acceptance Criteria

- A timed-out native-full `PreToolUse` hook denies the exact tool and executes
  no requested command, read, write, or publisher action.
- The model receives a bounded reason containing event, tool, hook identity,
  and configured timeout but no payload, environment value, provider content,
  or credential.
- One later healthy turn can execute through the entire hook chain and finish
  normally.
- Repeated identical timeout attempts terminate within the existing
  no-progress cap; the 600-turn and 60-minute allowances are not reduced.
- Nonzero, malformed, non-object, unsupported, and explicit block behavior is
  unchanged and fail-closed.
- H inherits the behavior through the shared native-full path with no
  provider-specific bypass.
- Focused tests, Ruff checks, preflights, implementation report, independent
  verification, and a focused commit all pass before any reproof is counted.

## Risk / Rollback

The principal risk is accidentally turning a governance failure into tool
execution. The design avoids that by returning a block before dispatch and by
ending evaluation of the current hook chain. A secondary risk is an endless
model retry loop; the existing repeated-tool-signature ceiling remains the
hard bound and receives explicit regression coverage.

Rollback is a focused revert of the WI-5280 changes in the three target files.
The append-only WI, test, PAUTH, proposal, report, verdict, and incident evidence
remain as audit history. Rollback does not change H eligibility or runtime
state.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered
file for `gtkb-wi5280-native-pretool-timeout-recovery`. Dispatcher/TAFE state
plus the numbered file chain remain the live workflow authority.

## Recommended Commit Type

`fix` - the change corrects a reproduced native-full worker-termination defect
without adding a new capability or weakening governance.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
