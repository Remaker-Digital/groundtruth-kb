REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex interactive Prime Builder; ::init gtkb pb; revise_bridge.py file mode
author_metadata_source: interactive-codex-session-env-override

# Implementation Proposal - Codex headless shell containment with efficacy-gated acceptance

bridge_kind: prime_proposal
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 003
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md (NO-GO)
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5135

target_paths: ["scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py", "scripts/windows_subprocess.py", "scripts/codex_shell_no_window_wrapper.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_windows_subprocess.py", "platform_tests/scripts/test_codex_shell_no_window_wrapper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED answers the `-002` LO NO-GO by making WI-5135 acceptance efficacy-gated. The implementation is no longer defined as "append `windows.sandbox_private_desktop=true` to the Codex argv"; that setting is only one candidate hypothesis. The slice is acceptable only if the selected mechanism proves that repeated Codex shell activity produces no visible `pwsh` console windows under the dispatcher-owned launch path.

## Requirement Sufficiency

Existing requirements are sufficient for implementation review. No new or revised requirement is required before implementation.

## Findings Addressed

### Finding 1 - [P1, blocking] Acceptance does not test efficacy; the committed mechanism is unevidenced

Response: accepted. The proposal now treats `windows.sandbox_private_desktop=true` as an unproven candidate, not as a committed mechanism. The implementation must first either cite or probe the live Codex CLI behavior enough to prove that the selected option is accepted, then prove efficacy with runtime observations. Mere command-line presence of any flag, config key, wrapper path, or desktop name is not an acceptance signal.

The candidate decision rule for implementation is:

1. Prefer a Codex-supported headless/private-desktop shell option only if local evidence shows the current Codex CLI accepts it and the strengthened no-window probe passes.
2. If the Codex config-key hypothesis is unsupported or ineffective, attempt GT-KB-side Windows desktop isolation through `scripts/windows_subprocess.py` so the dispatcher launches the Codex worker tree on a non-visible desktop under our control.
3. If desktop isolation is not viable, attempt a no-window PowerShell wrapper path that can be selected by Codex and verified under the same probe.
4. Select the first candidate that passes both proof gates below. If no candidate passes, do not claim implementation acceptance; file a new Prime report/revision with the observed failure class and keep Codex-A persistent dispatch disabled.

The proof gates are now inside this slice:

- Strengthened smoke proof: `scripts/codex_no_window_smoke_probe.py` must exercise at least two Codex runs, each with at least three shell-command steps linked by marker files/nonces, while continuously polling for visible `pwsh`/PowerShell windows. Legacy single-echo results are invalid.
- Readiness proof: `scripts/verify_codex_dispatch.py --json` and the dispatcher readiness gate must reject legacy schema, insufficient run count, insufficient command count, missing marker-chain proof, stale results, and any visible-window observation.
- Dispatcher-path proof: before requesting VERIFIED, the implementation report must include one bounded live proof that uses the same dispatcher wrapped-command path for Codex shell execution and observes zero visible `pwsh` windows during multi-command activity. This proof is not persistent Codex-A enablement; `can_receive_dispatch` for Codex-A remains false unless a later governed enablement step approves steady-state dispatch.

### Finding 2 - [P2, clarification] Cited project authorization is filing-scoped, not implementation-scoped

Response: accepted. The cited PAUTH is only the authority for filing this proposal/revision. It is not the authority for source mutation.

If LO issues GO on this REVISED, Prime Builder still must obtain or confirm an implementation-scoped authorization for WI-5135 and must run:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch
```

Protected source/test/script mutation is blocked unless that begin packet succeeds and agrees with the live latest GO and target path scope. If the implementation-scoped authorization cannot be produced, Prime Builder will not mutate the target paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable artifact capture for implementation proposals and review findings.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - governs owner-decision evidence used to sequence this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform dispatcher repair out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - governs backlog/work-item continuation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex Windows behavior to be proven without assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires implementation/review artifacts to carry durable decisions and evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs bridge lifecycle transitions and follow-up capture.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires implementation authorization before protected mutation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - prohibits source mutation without a live GO and implementation-start packet.
- `GOV-WORK-TREE-HYGIENE-001` - requires scoped source/test changes and excludes unrelated dirty state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - keeps dispatch ownership centralized in the dispatcher service.
- `ADR-DISPATCHER-ARCHITECTURE-001` - preserves daemon-owned dispatch and harness-consumer semantics.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - preserves single-harness bridge dispatcher behavior while Codex-A remains quiesced.

## Prior Deliberations

- `DELIB-202666064` - owner decision: fix WI-5135 for headless Prime rather than switching to a non-GUI Prime harness; sequence after WI-5105/WI-5112/WI-5132.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - owner directive: no visible console windows may spawn; dispatcher can remain quiesced until proof is available.
- `DELIB-202665909` - prior VERIFIED for parent-level dispatcher no-window containment; WI-5135 is the grandchild-shell follow-on after parent containment proved insufficient.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md` - LO NO-GO requiring efficacy-gated acceptance or mechanism evidence.

## Owner Decisions / Input

- `DELIB-202666064` supplies the owner decision to pursue WI-5135 as the Prime harness path.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING` is carried forward only as proposal/revision filing authority.
- No new owner input is requested by this REVISED. Source mutation remains gated on a later implementation-scoped authorization packet after LO GO.

## Proposed Scope

- Replace the false-green no-window verification with a governed schema-v2 repeated, multi-command Codex smoke probe that records marker-chain evidence and live window observations.
- Update Codex dispatcher command composition to support an efficacy-proven containment mechanism selected by the decision rule above, rather than accepting a fixed argv token as success.
- Update readiness and dispatcher gating so legacy/single-echo smoke output, missing marker proof, insufficient run/command counts, stale proof, or any visible-window observation fail closed.
- Keep Codex-A persistent dispatch eligibility disabled until a later governed enablement step approves steady-state use.
- Exclude shared harness capability registry, skill manifests, generated `harness-state/harness-registry.json`, `groundtruth.db` commit scope, and Alibaba H registration paths.

## Acceptance Criteria

- The implementation report identifies the selected containment mechanism and includes evidence that the current runtime accepts or controls that mechanism.
- Acceptance is tied to zero visible `pwsh`/PowerShell windows during repeated multi-command Codex shell activity, not to command-line flag presence.
- `scripts/codex_no_window_smoke_probe.py` writes schema-v2 evidence with at least two runs, at least three linked command steps per run, nonce/marker-chain proof, return codes, stdout/stderr previews, and window-observation samples.
- `scripts/verify_codex_dispatch.py --json` and dispatcher readiness checks reject legacy schema, insufficient proof, stale proof, and visible-window evidence.
- A bounded dispatcher-path proof exercises the same wrapped command path used by real Codex dispatch and observes zero visible `pwsh`/PowerShell windows during multi-command shell activity.
- Focused tests pass with `--basetemp .harness-tmp/wi5135`.
- Ruff check and ruff format check pass for changed Python paths.
- Codex-A persistent `can_receive_dispatch` remains false unless a separate governed enablement step approves steady-state dispatch after proof.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This file is PB-authored `REVISED` after latest LO `NO-GO`; LO must independently review before any protected source mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header carries Project Authorization, Project, Work Item, and machine-readable `target_paths`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | After GO, run `implementation_authorization.py begin` and require an implementation-scoped authorization before mutation. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No source/test/script mutation occurs until latest GO and begin packet authorize the exact target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every linked spec to executed focused tests and runtime proof. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Live evidence must prove Codex behavior rather than assuming hooks, parent no-window flags, or unsupported CLI settings. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests must show dispatcher command composition remains centralized and audited. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests must show the daemon remains the dispatch owner and no retired poller/harness-trigger path is restored. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Dispatcher readiness remains fail-closed while Codex-A is quiesced and until proof is current. |
| `GOV-WORK-TREE-HYGIENE-001` | Final commit/report scope must exclude unrelated dirty DB, registry, and shared bridge-state files. |

## Pre-Filing Preflight Subsection

Prime Builder ran the mandatory candidate preflights against this completed content before live filing:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --content-file .tmp\wi5135-revised-003.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --content-file .tmp\wi5135-revised-003.md
```

Observed results: applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`; clause preflight exited 0 with 0 blocking gaps across 5 evaluated clauses. The revision helper also reruns both gates during live filing and refuses to write `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md` if either gate fails.

## Risk And Rollback

Risk is moderate because this changes dispatcher readiness and Codex worker launch behavior after GO. The revised acceptance reduces the main risk by forbidding VERIFIED on structural flag presence alone.

Rollback is a scoped revert of changed source/test paths. Bridge files and implementation-start packets remain append-only audit artifacts. Codex-A persistent dispatch stays disabled until a separate governed enablement step approves it.

## Recommended Commit Type

`fix`
