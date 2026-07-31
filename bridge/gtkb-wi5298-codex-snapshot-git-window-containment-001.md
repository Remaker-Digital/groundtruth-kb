NEW

# WI-5298: Hide Codex Desktop snapshot Git consoles without impairing dispatch

bridge_kind: prime_proposal
Document: gtkb-wi5298-codex-snapshot-git-window-containment
Version: 001
Author: Prime Builder (Codex Desktop, harness A)
Date: 2026-07-15T23:34:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; default reasoning configuration

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5298

target_paths: ["scripts/ops/codex_snapshot_window_hider.py", "scripts/ops/harness_storm_watchdog_launcher.py", "platform_tests/scripts/test_codex_snapshot_window_hider.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source | test | runtime_state
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Codex Desktop 26.707.9981.0 currently creates working-tree safety snapshots by
spawning `ChatGPT.exe -> git.exe -> conhost.exe`; the Git command includes the
exact argument sequence `-c core.hooksPath=NUL -c core.fsmonitor= add -u`.
Process telemetry and the packaged application source both confirm that this is
the interactive app's temporary-index snapshot path, not a TAFE-dispatched
harness worker. The snapshot mechanism must keep running, but its transient
console must not become visible.

Add an in-root, Windows-only, hide-only monitor using `SetWinEventHook` for
window-show events. It will call `ShowWindowAsync(SW_HIDE)` only when the window
process is proven to be the `conhost.exe` child (or console owner) of the exact
snapshot Git command and that Git process is a direct descendant of the signed
Codex Desktop `ChatGPT.exe` installation. A named mutex provides singleton
operation. The already-enabled, root-bound storm-watchdog launcher will ensure
the monitor is running under `pythonw.exe` with canonical no-window flags; it
will not register or edit a scheduled task. The monitor never terminates a
process, alters Git arguments or results, touches the real index, contacts a
harness, or changes dispatcher/TAFE/bridge/harness configuration or eligibility.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — containment must preserve Git
  snapshot completion, every harness's dispatchability, and live bridge
  automation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex-specific capability gaps use a
  governed, root-bound deterministic fallback without weakening shared
  behavior.
- `ADR-CROSS-HARNESS-PARITY-001` — an interactive Codex UI defect cannot be
  projected into role or eligibility restrictions for any harness.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — nonimpairment and equivalent
  dispatchability require focused static and runtime proof.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected source and test edits require
  independent GO, matching claim/start authority, and post-implementation
  independent verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal maps
  each operative specification to verification evidence below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the active Harness
  Parity project, PAUTH, and WI-5298 are declared in the machine-readable header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires the
  focused tests and live nonimpairment evidence defined below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — process provenance, the owner
  correction, implementation, tests, report, and verdict remain traceable as
  one durable artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-5298 remains a candidate until GO,
  implementation-start, report, independent VERIFIED, and exact finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the discovered defect and owner
  correction are preserved in MemBase rather than left as transcript-only
  context.

## Prior Deliberations

- `DELIB-202666274` — authorizes the full modernization project while preserving
  bridge, implementation-start, independent-review, and mechanical-operation
  gates.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — establishes the workstation
  requirement that background automation must not surface visible consoles.
- `DELIB-202666320` — the independent WI-5113 review accepts canonical
  no-window Git subprocess treatment but is limited to finalizer call sites;
  this proposal addresses the separate interactive Codex Desktop snapshot path.
- Owner directive, 2026-07-15 — console visibility never makes a harness
  non-dispatchable; the only acceptable resolution fixes the window while the
  harness remains fully usable. WI-5113 and WI-5298 were corrected through the
  governed backlog CLI to encode that invariant before this filing.

## Owner Decisions / Input

No further owner decision is required for source/test implementation. The owner
explicitly authorized the modernization program and directed this exact
nonimpairing resolution on 2026-07-15. This proposal does not request or perform
any forbidden mechanical operation: no dispatcher/TAFE/harness mutation, task
registration, Git staging/commit/push, deployment, release, credential action,
or destructive cleanup is in scope.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`,
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, and the
owner's 2026-07-15 dispatchability correction jointly define the required
behavior: keep the snapshot and every harness operational, hide only the exact
app-owned console surface, and prove no routing or process-lifecycle impairment.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5298, owner directive 2026-07-15, live Windows process telemetry, and Codex Desktop 26.707.9981.0 packaged-source inspection",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and ADR-CODEX-HOOK-PARITY-FALLBACK-001",
  "primary_route": "scripts/ops/codex_snapshot_window_hider.py ensured by scripts/ops/harness_storm_watchdog_launcher.py",
  "before_behavior": "Codex Desktop safety snapshots run through ChatGPT.exe to git.exe to conhost.exe and can surface a visible console even though the dispatcher remains healthy",
  "after_behavior": "The same snapshot Git command runs to natural completion while only its exactly attributed console surface is hidden; dispatcher and harness behavior are unchanged",
  "self_descriptive_naming": "codex_snapshot_window_hider identifies the exact app-side responsibility and does not claim dispatcher control",
  "obsolete_guidance_disposition": "The WI-5113 instruction to keep harness C dispatch-ineligible was removed through the governed backlog CLI; console containment cannot disable a harness",
  "history_preservation": "MemBase work-item versions and the numbered bridge chain remain append-only; commit 08cbc017 and all prior implementation history remain unchanged",
  "baseline": {
    "dispatch_topology": "Codex A and Antigravity C are active and dispatchable through the governed status CLI",
    "process_chain": "ChatGPT.exe directly parents the exact snapshot git.exe command, which parents conhost.exe",
    "git_state": "The real repository index is unlocked and snapshot staging uses a temporary index"
  },
  "expected_result": {
    "snapshot": "The exact Git helper exits naturally with its original result",
    "window": "The qualifying console is hidden immediately and no qualifying visible window remains",
    "dispatch": "Eligibility, selection, active work, and bridge automation are byte-for-byte or semantically unchanged"
  },
  "rollback": {
    "instructions": "Remove the scoped source and test implementation and let the singleton monitor process exit",
    "test_plan": "Focused launcher tests and the live proof confirm that no dispatcher, task, repository, or harness state requires restoration"
  },
  "hard_invariants": [
    "No process termination or process-priority change",
    "No Git interception, argument change, repository mutation, staging, or commit",
    "No task registration or external-system mutation",
    "No dispatcher, TAFE, bridge-route, harness, role, allowance, or eligibility mutation",
    "No direct harness contact, deployment, release, credential action, or destructive cleanup"
  ],
  "fail_closed_conditions": [
    "Unreadable process ancestry leaves the window and process untouched",
    "Non-exact Git arguments leave the window and process untouched",
    "Missing Codex Desktop ancestor leaves the window and process untouched",
    "Missing Windows APIs or monitor startup preserves the existing watchdog and harness operation"
  ],
  "essential_context_preservation": "Codex temporary-index snapshot safety, Git exit semantics, bridge automation, independent review, active worker allowances, and every harness's dispatchability remain intact"
}
```

## Cross-Harness Disposition

- **Codex A:** only the interactive Desktop app's exact snapshot-console
  presentation changes. Prime Builder role, safety snapshots, CLI workers,
  allowances, private-desktop dispatch, and eligibility remain unchanged.
- **Claude B, Antigravity C, Ollama D, Cursor E, OpenRouter F, and Alibaba H:**
  no source adapter, invocation, role, allowance, routing, or eligibility is
  changed. In particular, C remains active and dispatchable throughout.
- **Fallback:** if the Windows event hook or ancestry proof is unavailable, the
  monitor touches nothing and all harness work continues normally.

## Spec-Derived Verification Plan

1. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` and
   `ADR-CROSS-HARNESS-PARITY-001`:
   `gt bridge dispatch status --json` before and after the live proof must show
   the same eligibility/selection topology, including A and C remaining
   dispatchable. No proposal step may call a dispatcher mutation command.
2. `ADR-CODEX-HOOK-PARITY-FALLBACK-001`:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest
   platform_tests/scripts/test_codex_snapshot_window_hider.py -q --no-header`
   must prove exact positive and negative ancestry/argv matching, named-mutex
   singleton behavior, WinEvent callback filtering, and `ShowWindowAsync` as the
   only target-process action. Generic Git, user terminals, dispatched workers,
   and non-Codex parents must be rejected.
3. `DCL-CROSS-HARNESS-ENFORCEMENT-001`:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest
   platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --no-header`
   must prove the existing launcher starts the root-bound monitor through
   `pythonw.exe` with canonical no-window/detached flags, preserves the watchdog
   invocation, and fails soft if monitor startup is unavailable.
4. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:
   focused Ruff checks on all four targets must pass. A fresh 120-second Windows
   observation must capture at least one qualifying Codex snapshot, record that
   its console was hidden, show the snapshot Git process exited naturally, show
   no real `.git/index.lock` residue or index mutation attributable to the
   monitor, and show no qualifying window remains visible. The evidence record
   belongs under ignored `.gtkb-state/ops/`; no synthetic bridge evidence is
   permitted.

## Risk / Rollback

The primary risk is hiding an unrelated console. The mitigation is conjunctive
provenance: exact Git argv, exact Git/conhost parentage, and a Codex Desktop
`ChatGPT.exe` ancestor. Any unreadable or ambiguous process evidence fails open
for visibility and leaves the process/window untouched. The monitor never calls
`TerminateProcess`, `Stop-Process`, `kill`, or changes process priority, handles,
stdin/stdout, exit status, Git configuration, or repository data.

Rollback is one scoped source/test commit plus natural monitor termination; no
task or dispatcher restoration is required because those surfaces are never
mutated. Commit execution itself remains outside this proposal's current
mechanical authority.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5298-codex-snapshot-git-window-containment`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — this is a bounded Windows reliability correction for a reproducible
Codex Desktop snapshot-console defect, with focused regression coverage.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
