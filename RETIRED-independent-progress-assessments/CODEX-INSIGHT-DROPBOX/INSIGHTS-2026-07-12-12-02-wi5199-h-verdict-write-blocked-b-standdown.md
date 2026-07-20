# INSIGHTS 2026-07-12 12:02 UTC — WI-5199 H-functional-proof: dispatched B stand-down (12th) — NEW ROOT CAUSE: H's verdict Write is gate-blocked

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-12T11-54-17Z-loyal-opposition-B-82d1db
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless Loyal Opposition; bridge auto-dispatch; full GT-KB governance; resolved_role=loyal-opposition

Specs: GOV-HARNESS-ONBOARDING-CONTRACT-001, GOV-FILE-BRIDGE-AUTHORITY-001, ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001, ADR-CROSS-HARNESS-PARITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001
WIs: WI-5199, WI-5204

## TL;DR

Dispatch `2026-07-12T11-54-17Z-loyal-opposition-B-82d1db` (SOLO WI-5199) routed me the
still-`NEW` report `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-003.md`. This is a
**harness-functional-proof whose verdict is reserved for harness H** (Alibaba Cloud Studio).
I am harness **B**. I **STOOD DOWN with zero bridge mutation** — no GO/NO-GO/VERIFIED. This
is the **12th** stand-down on this thread (6 dropboxes: `-20-38/-20-55/-22-14/-23-08/03-47/08-08`;
stand-downs 7–11 were memory-only under the churn-cap because nothing had changed).

**Churn-cap broken deliberately: the gating blocker MATERIALLY CHANGED and the concrete root
cause is now KNOWN.** H no longer subprocess-crashes. H ran a full, genuine 74-turn review of
`-003` (11:03→11:54 UTC), reached a verdict, and was then **hard-blocked from WRITING the
verdict file** by the native implementation-start gate. This is the most actionable this proof
has ever been — Prime now has a precise, fixable target.

## Why stand-down (not a verdict) — reservation re-confirmed against canonical state

Triple-encoded in the thread (unchanged from prior stand-downs):
- Report `-003` GO-Advisory A (lines 113–114): "Any B worker that nevertheless sees this
  report should stand down because the bridge chain explicitly reserves this proof verdict
  for H." Acceptance criterion (line 209/212) + LO Ask #5 (line 231) require `author_harness_id: H`.
- GO `-002` FINDING A (author = me, harness B, 2026-07-11): "any future auto-dispatched B
  session handed this report should stand down in favor of H."

Authoring ANY verdict as B — even a NO-GO — defeats the proof by falsely satisfying / corrupting
the "target H publishes a committed verdict" acceptance criterion. This is the harness-proof
thread itself, so the rule is STAND DOWN (zero mutation).

## MATERIAL CHANGE since the 6th (08:08Z) and memory-only 7th–11th (02:10Z-era facts)

Prior records described H's last run at `2026-07-12T02:10:42Z` with
`failure_class: subprocess_execution_failed` (blank-final-message shim crash), on
wi5200-5202 / wi5203 — **not** WI-5199. That is now stale. Fresh canonical reads this session:

**1. H ran AGAIN — recently, on WI-5199 specifically, and to a CLEAN exit.**
`.gtkb-state/bridge-poller/dispatch-state.json` `loyal-opposition:H.last_launch` +
`.gtkb-state/bridge-poller/dispatch-runs/2026-07-12T11-03-20Z-loyal-opposition-H-92f409.*`:
- dispatch `2026-07-12T11-03-20Z-loyal-opposition-H-92f409`, worker
  `scripts/alibaba_cloud_studio_harness.py` (genuine H), launched 11:03:20Z,
  completed 11:54:16Z, **elapsed 3056 s (~51 min)**.
- `selected_top_files: ["bridge/gtkb-wi5199-fd-evidence-h-functional-proof-003.md"]` — H ran
  on THIS exact report.
- telemetry.json: `turn_budget 600, turns_used 74` (**not** turn exhaustion);
  `tool_calls.total 139` (Bash 105, Read 16, Grep 11, Glob 6, **Write 1**);
  `outcome: {exit_status: "failed", stop_reason: "process_error", bridge_status: null, exit_code: 0}`.
  The single `Write` is at turn 42; turns 43–74 are Bash (finalization attempts). This is a
  substantive, genuine tool-using review — NOT a canned smoke.

**2. The failure mode EVOLVED: subprocess-crash → verdict-publication block.**
The narrow WI-5200-5202 blank-final-message repair (VERIFIED `45d1c7f2`) WORKED — H no longer
`subprocess_execution_failed`. The new terminal state is `no_verdict_produced` /
`process_error` with `bridge_status: null`: H reaches a verdict but cannot publish it.

**3. ROOT CAUSE (from H's own stdout — the smoking gun).**
`...-92f409.stdout.log` (H's final message, verbatim): *"the **Write tool is blocked** by the
native hook `GTKB-IMPLEMENTATION-START-GATE` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`,
which prevents me from writing the verdict artifact to
`bridge/gtkb-wi5199-fd-evidence-h-functional-proof-004.md`."* H's review body reports both
mandatory preflights clean and F/D evidence independently verified. (Secondary note: H labeled
its verdict "GO" for an implementation *report* — the correct terminal verdict is VERIFIED/NO-GO;
minor role/verdict-semantics confusion, not the blocker.)

**4. FINDING-A re-fan confirmed to the second.** H completed 11:54:16Z; my B dispatch was
created 11:54:17Z — one second later. Report still `NEW`, H's lease released with no verdict,
B restored eligible → re-fan to B. (`harness-registry.json` H `can_receive_dispatch=false`,
B `=true`.)

**5. Thread state:** `bridge/gtkb-wi5199-fd-evidence-h-functional-proof-{001,002,003}.md` only,
all **untracked** (`git status --porcelain` = `??` for all three); **no `-004`** → H has
committed no reserved verdict.

## Likely mechanism (for Prime to confirm) — a cross-harness PARITY gap, not a gate bug

Post-WI-4967, a **raw `Write` to `bridge/*-NNN.md` is hard-blocked for ALL roles**; verdicts
MUST route through the governed verdict-writer helper (`.claude/skills/verify/helpers/write_verdict.py`
for VERIFIED, or `write_bridge_file` for GO/NO-GO), which sets the markers the
implementation-start gate recognizes as a governed LO-verdict write. B and Codex publish
verdicts headlessly this way successfully. `scripts/implementation_start_gate.py` itself directs
callers to "the governed bridge … helper path" (lines 296, 1274) — i.e., it is designed to block
raw mutations.

H's stdout shows it reached for the **raw `Write` tool** and was correctly blocked. The most
probable root cause is therefore: **H's LO verdict-authoring path is not wired to the governed
verdict-writer helper** (a harness-parity gap under `ADR-CROSS-HARNESS-PARITY-001` /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`), so its verdict Write hits the gate. Prime should
confirm whether the fix is (a) wiring H's verdict authoring to the governed writer, or (b) an
explicit LO-verdict-write exemption in the gate for parity harnesses. Sibling
`gtkb-wi5204-h-stop-hook-completion-preservation` (H Stop-hook completion) may be adjacent.

## Ordered resolution actions (Prime/owner-only — a headless LO can do NONE)

1. **NEW — wire H's verdict path to the governed writer (this supersedes the old "diagnose H's
   subprocess crash" action, which is RESOLVED).** H now completes a full clean review; the sole
   remaining blocker is that its verdict-file Write is denied by
   `GTKB-IMPLEMENTATION-START-GATE` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. Ensure H's
   LO verdict authoring routes through `write_verdict.py` / `write_bridge_file` as B/Codex do
   (or add the gate exemption per the mechanism note above). Confirm against H's skill/adapter
   wiring — I cannot invoke H (DIRECT-HARNESS-INVOKE-BAN; different harness).
2. **Only after H can demonstrably COMMIT a verdict:** re-attempt the governed
   `gt bridge dispatch config set-eligibility` H-proof flip, **holding B ineligible until H
   COMMITS** (not merely until in-flight — the FINDING-A defect), then restore B=true/H=false.
3. **Interim mechanical loop-break note:** WI-5203's targeted-reoffer fix is VERIFIED
   (`dc03ada4`) and the broad WI-5200-5202 chain is closed (`12a8508c`), but the `-003` report
   STILL re-fans solo to B (they are different threads) — so the loop persists until action 1+2
   land or WI-5199 is re-scoped.
4. **Owner fallback if H's verdict path is unfixable:** re-scope WI-5199 acceptance to accept
   H-unproven (F proven; D proven-but-DEGRADED). The `-003` F/D evidence is independent of H.

## Cost escalation

Each re-fan spawns a full headless Claude LO investigation (~tens of k tokens) that can only
stand down — the "expensive spawn without commensurate value" anti-pattern `bridge-essential.md`
warns against. 12 stand-downs now. THIS spawn produced a concrete new root cause (real value);
further re-fans before action 1+2 or 4 land will be pure churn. The loop needs a **governed
break now** (action 1+2), or the WI-5199 re-scope (action 4).

## Bridge mutation performed

**None.** Zero GO/NO-GO/VERIFIED/NEW/REVISED written. This dropbox record is the only artifact
produced. Review independence and the harness-proof reservation are both preserved.

## Related prior records / rules

- Prior stand-downs: `INSIGHTS-2026-07-11-20-38/-20-55/-22-14/-23-08.md`,
  `INSIGHTS-2026-07-12-03-47-wi5199-b-standdown.md`, `INSIGHTS-2026-07-12-08-08-wi5199-b-standdown.md`.
- Rules: `.claude/rules/loyal-opposition.md` (Bridge Review Independence; File Safety),
  `.claude/rules/file-bridge-protocol.md` (Review Independence Boundary),
  `.claude/rules/bridge-essential.md` (expensive-spawn anti-pattern).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
