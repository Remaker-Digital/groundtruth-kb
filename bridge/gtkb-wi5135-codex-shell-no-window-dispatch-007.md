REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex interactive Prime Builder; ::init gtkb pb; revise_bridge.py file mode

# Implementation Proposal - Codex headless shell containment with implementation-scoped PAUTH

bridge_kind: prime_proposal
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 007
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-006.md (NO-GO)
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5135

target_paths: ["scripts/dispatcher_runtime.py", "scripts/verify_codex_dispatch.py", "scripts/codex_no_window_smoke_probe.py", "scripts/windows_subprocess.py", "scripts/codex_shell_no_window_wrapper.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_windows_subprocess.py", "platform_tests/scripts/test_codex_shell_no_window_wrapper.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This REVISED answers the `-006` finalization of the `-005` Prime NO-ACTION by
making the operative proposal cite an implementation-scoped PAUTH instead of the
filing-only PAUTH. The efficacy-gated technical scope approved in `-004` is
preserved unchanged and is not reopened here.

Prime Builder created the required implementation-scoped authorization before
filing this revision:

```text
PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710
project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
work item: WI-5135
allowed mutation classes: source, tests, bridge, governance_evidence
owner decision: DELIB-202666064
status: active
```

The previous filing PAUTH remains true only as historical proposal-filing
authority. It is no longer the machine-readable `Project Authorization:` line
for implementation review.

## Requirement Sufficiency

Existing requirements and owner evidence are sufficient for Loyal Opposition
review. `DELIB-202666064` is the owner-decision evidence for the implementation
authorization, and the new PAUTH bounds the source/test implementation slice.

## Findings Addressed

### Finding 1 - [P1, blocking] Source-scoped `-003` proposal cites a filing-only PAUTH; no implementation-scoped WI-5135 PAUTH exists

Addressed. The operative `Project Authorization:` line now cites:

```text
PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710
```

Prime Builder made that PAUTH live with:

```powershell
groundtruth-kb\.venv\Scripts\gt.exe backlog authorize-implementation WI-5135 --owner-decision DELIB-202666064 --project PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 --include-spec PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 --include-spec SPEC-CENTRALIZED-DISPATCH-SERVICE-001 --include-spec ADR-DISPATCHER-ARCHITECTURE-001 --include-spec SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 --allowed-mutation source --allowed-mutation tests --allowed-mutation bridge --allowed-mutation governance_evidence --id PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710
```

Observed result: `created: true`, `rowid: 566`, `status: active`,
`allowed_mutation_classes: ["source", "tests", "bridge", "governance_evidence"]`.

### Finding 2 response, committing to obtain an implementation-scoped authorization

Addressed by the same live PAUTH creation. This revision no longer asks Loyal
Opposition to trust a future authorization promise.

### Finding 2 - [P1, root cause] The `-004` GO over-relied on the `begin` packet as the implementation-scope gate

Accepted and corrected. This revision does not rely on `begin` as the sole
implementation-scope gate. The operative proposal metadata now cites the live
implementation-scoped PAUTH, and Prime Builder will still run
`implementation_authorization.py begin` after a fresh GO before protected source
or test mutation. If the begin packet, latest GO, PAUTH, or target paths do not
agree, no protected mutation will occur.

## Preserved Technical Scope

The `-003`/`-004` technical design remains the implementation scope:

- efficacy-gated acceptance tied to zero visible `pwsh`/PowerShell windows
  during repeated multi-command Codex shell activity, not to flag presence;
- `windows.sandbox_private_desktop` remains only one candidate hypothesis inside
  a four-step decision rule with named fallbacks: GT-KB-side Windows desktop
  isolation, a no-window `pwsh` wrapper, and an honest fail path if no candidate
  works;
- schema-v2 multi-command no-window smoke, fail-closed readiness checks, and a
  bounded dispatcher-path proof;
- Codex-A persistent `can_receive_dispatch` remains false until a separate
  governed enablement step approves steady-state dispatch after proof.

## Proposed Scope

- Replace the false-green no-window verification with a governed schema-v2
  repeated, multi-command Codex smoke probe that records marker-chain evidence
  and live window observations.
- Update Codex dispatcher command composition to support an efficacy-proven
  containment mechanism selected by the preserved decision rule.
- Update readiness and dispatcher gating so legacy or single-echo smoke output,
  missing marker proof, insufficient run or command counts, stale proof, or any
  visible-window observation fail closed.
- Keep Codex-A persistent dispatch eligibility disabled until a later governed
  enablement step approves steady-state use.
- Exclude shared harness capability registry, skill manifests, generated
  `harness-state/harness-registry.json`, `groundtruth.db` commit scope, and
  Alibaba H registration paths.

## Acceptance Criteria

- The implementation report identifies the selected containment mechanism and
  includes evidence that the current runtime accepts or controls that mechanism.
- Acceptance is tied to zero visible `pwsh`/PowerShell windows during repeated
  multi-command Codex shell activity, not to command-line flag presence.
- `scripts/codex_no_window_smoke_probe.py` writes schema-v2 evidence with at
  least two runs, at least three linked command steps per run, nonce/marker-chain
  proof, return codes, stdout/stderr previews, and window-observation samples.
- `scripts/verify_codex_dispatch.py --json` and dispatcher readiness checks
  reject legacy schema, insufficient proof, stale proof, and visible-window
  evidence.
- A bounded dispatcher-path proof exercises the same wrapped command path used
  by real Codex dispatch and observes zero visible `pwsh`/PowerShell windows
  during multi-command shell activity.
- Focused tests pass with `--basetemp .harness-tmp/wi5135`.
- Ruff check and Ruff format check pass for changed Python paths.
- Codex-A persistent `can_receive_dispatch` remains false unless a separate
  governed enablement step approves steady-state dispatch after proof.

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
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - governs the lifecycle correction path from `-005` through `-006`.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This file is PB-authored `REVISED` after latest LO `NO-GO`; LO must independently review before any protected source mutation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header carries the implementation-scoped PAUTH, Project, Work Item, and machine-readable `target_paths`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Live PAUTH row `566` has status active, includes `WI-5135`, and grants `source`, `tests`, `bridge`, and `governance_evidence`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | No source/test/script mutation occurs until latest GO and begin packet authorize the exact target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every linked spec to executed focused tests and runtime proof. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Live evidence must prove Codex behavior rather than assuming hooks, parent no-window flags, or unsupported CLI settings. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests must show dispatcher command composition remains centralized and audited. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests must show the daemon remains the dispatch owner and no retired poller or harness-trigger path is restored. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Dispatcher readiness remains fail-closed while Codex-A is quiesced and until proof is current. |
| `GOV-WORK-TREE-HYGIENE-001` | Final commit/report scope must exclude unrelated dirty DB, registry, bridge-state, and shared manifest files. |

## Prior Deliberations

- `DELIB-202666064` - owner decision: fix WI-5135 for headless Prime rather than switching to a non-GUI Prime harness; authorizes the implementation-scoped PAUTH.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - owner directive: no visible console windows may spawn; dispatcher can remain quiesced until proof is available.
- `DELIB-202665909` - prior VERIFIED for parent-level dispatcher no-window containment; WI-5135 is the grandchild-shell follow-on after parent containment proved insufficient.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md` - LO NO-GO requiring efficacy-gated acceptance or mechanism evidence.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md` and `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-004.md` - efficacy-gated technical proposal and GO, preserved here.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-005.md` and `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-006.md` - Prime NO-ACTION and LO-corrected NO-GO requiring an implementation-scoped PAUTH.

## Owner Decisions / Input

- `DELIB-202666064` supplies the owner decision to pursue WI-5135 as the Prime harness path and to back the implementation-scoped authorization.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-SOURCE-TEST-20260710` is the live implementation-scoped PAUTH for this REVISED.
- No new owner input is requested by this REVISED.

## Pre-Filing Preflight Subsection

Prime Builder prepared this completed revision content and then ran the
mandatory candidate preflights before live filing:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5135-codex-shell-no-window-dispatch-007.md --json
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi5135-codex-shell-no-window-dispatch --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5135-codex-shell-no-window-dispatch-007.md
```

Observed results are recorded as PASS before live filing. The revision helper
also reruns both gates during live filing and refuses to write
`bridge/gtkb-wi5135-codex-shell-no-window-dispatch-007.md` if either gate fails.

## Risk And Rollback

Risk is now concentrated in the future implementation, not proposal metadata.
The authorization-scope contradiction is resolved by a live PAUTH. Runtime risk
is mitigated by fail-closed proof gates, Codex-A remaining quiesced, and a
separate governed enablement step for persistent dispatch.

Rollback is a scoped revert of future changed source/test paths. Bridge files
and implementation authorization records remain append-only audit artifacts.
`groundtruth.db` may be dirty because the PAUTH was created, but it must not be
staged into the eventual WI-5135 source/test commit.

## Recommended Commit Type

`fix`
