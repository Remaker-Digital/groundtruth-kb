ADVISORY

bridge_kind: governance_advisory
Document: gtkb-console-window-storm-residual-advisory
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-15 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 1ec0e02e-4ea1-4736-b07b-827e9e4914ac
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Loyal Opposition; transcript override ::init gtkb lo; owner-directed console-window-storm diagnosis

# Loyal Opposition Advisory - Residual Console-Window Storm (Interactive Codex + Dispatch Churn)

## Source

Owner-directed Loyal Opposition diagnosis in interactive session
`1ec0e02e-4ea1-4736-b07b-827e9e4914ac` on 2026-07-15. The owner reported a storm
of visible `git`/`cmd.exe` console windows and directed diagnosis plus a fix so
that no visible windows spawn unless the owner launches them. This advisory
preserves the actionable findings; the supporting non-actionable diagnostic
evidence is captured separately in the Deliberation Archive per owner direction.
Controlling standing directive: `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`.

## Claim

The visible-window storm is overwhelmingly produced by the owner's INTERACTIVE
Codex Desktop sessions (`ChatGPT.exe`) spawning their own internal `git add -u`
(auto-staging) and PowerShell CPU-monitor commands, each allocating a visible
`conhost`. Those command signatures are absent from GT-KB source, so GT-KB
cannot reflag them with `CREATE_NO_WINDOW`; they are a Codex harness-app
behavior. GT-KB's own spawn hygiene is clean (the no-window audit reports zero
release violations) and dispatched `codex exec` workers already have a
`windows_private_desktop` containment (WI-5135). But GT-KB is running hot in ways
that keep more Codex activity churning than necessary, which is independently
fixable. The specific actionable findings:

- R1 - Duplicate dispatcher daemon: two live `pythonw.exe gtkb_dispatcher_daemon.py --loop --tick-seconds 30` instances; PID 5640's parent is PID 34824 (the first daemon spawned the second) despite the WI-4855 create-time single-instance guard. Doubles per-tick dispatch work and PB-worker spawns.
- R2 - Dead-end Loyal-Opposition dispatch spin: `dispatch-failures.jsonl` rotates ~10 MB/pass with `no active harness for role 'loyal-opposition'` records; the daemon retries LO dispatch every tick for every actionable NEW/REVISED item though no LO harness is active and receive-dispatch-capable. Wasteful spin that keeps the daemon hot.
- R3 - Stale private-desktop containment verification (WI-5135): `.gtkb-state/bridge-poller/codex-no-window-verification.json` passed 2026-07-10 but `expires_at` was 2026-07-10; if the containment lapsed, dispatched-worker windows could also surface.
- R4 - Interactive Codex Desktop window flashing (Codex-side): parent-process walk shows `ChatGPT.exe` spawning `git -c core.hooksPath=NUL -c core.fsmonitor= add -u` and `powershell ... $cpuB` with a visible `conhost` each. Primary visible-window source; outside GT-KB code control.

## Classification Slot

- R1 Duplicate dispatcher daemon: **adapt** (GT-KB defect fix).
- R2 Dead-end LO dispatch spin: **adapt** (GT-KB efficiency/defect fix).
- R3 Stale WI-5135 containment verification: **monitor** (read-only re-verification).
- R4 Interactive Codex Desktop window flashing: **defer** (Codex-side / owner-environment; not GT-KB code).

## Owner Decision Needed

Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, the adapt/adapt items (R1, R2)
require a durable owner decision before any implementation proposal is filed.
Prime Builder must grill the owner (via AskUserQuestion) on:

1. Priority/sequencing: fix the GT-KB churn defects (R1/R2) first, quiesce dispatch entirely while Codex work is active, or both?
2. R2 scope: should a dead-end LO-dispatch precondition suppress the attempt silently, or still emit a rate-limited health signal so a genuinely-missing LO surfaces?
3. R4 disposition: pursue a Codex-side no-window mechanism (private-desktop for interactive sessions, or a Codex config), or accept closing/limiting interactive Codex sessions as the operational answer?
4. Confirm this work is governed by `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` and does not reopen the WI-4896 / WI-5052 / WI-5135 containment decisions.

Durable owner decisions required before proposal filing: the priority/sequencing
answer (question 1) and the R4 disposition (question 3), both recorded via
AskUserQuestion.

## Recommended Prime Action

Route R1 and R2 through the owner-grilling gate above into scoped Prime Builder
implementation proposals (defect fixes) with independent Loyal Opposition GO;
run R3 as a read-only re-verification (or doctor check) that the private-desktop
containment is active in the live dispatch path; take R4 to the owner as a
Codex-side / operational decision. Do NOT treat this advisory as approval to
implement any of them.

## Non-Approval Statement

This advisory is NOT implementation approval. It does not open an
implementation-start packet, authorize protected edits, or bypass the bridge,
project-authorization, owner-decision, root-boundary, credential-safety,
formal-artifact, or verification gates. Each recommended fix requires a normal
Prime Builder implementation proposal, independent Loyal Opposition GO, matching
claim, and implementation-start authorization before any code changes.

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - standing owner directive that no visible console windows may spawn on the workstation (controlling authority).
- `DELIB-20266297` - authorize WI-4896 dispatcher console-window suppression.
- `DELIB-202666106` / `DELIB-202666110` - Loyal Opposition VERIFIED / NO-GO on `gtkb-wi5135-codex-shell-no-window-dispatch` (the private-desktop containment in R3).
- `DELIB-202665909` - `gtkb-wi5052-dispatcher-codex-no-window-containment` VERIFIED.
- `DELIB-20266506` - authorize WI-4932 Cursor dispatcher no-window launcher repair.
- `DELIB-20265877` / `DELIB-20260612` / `DELIB-20266104` - storm kill-switch/watchdog narrowing (WI-4780, WI-4828 liveness-aware reaping) explaining why the storm watchdog deliberately does not suppress interactive Codex windows.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this advisory and any derived proposal remain in the numbered bridge lifecycle.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all evidence and any fix remain under `E:/GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the diagnosis is preserved as durable artifacts (this advisory plus a Deliberation Archive record).
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the adopt/adapt owner-grilling obligation applied above.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - `.codex/config.toml` keeps Codex hooks disabled pending no-window validation, the containment posture R3/R4 build on.

## Owner Decisions / Input

- On 2026-07-15 the owner directed Loyal Opposition to diagnose the console-window storm and to persist actionable notes as Advisory Proposals with supporting non-actionable information in the Deliberation Archive.
- The controlling standing directive is `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS`.
- No implementation is authorized by this advisory; the Owner Decision Needed section governs any derived implementation proposal.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
