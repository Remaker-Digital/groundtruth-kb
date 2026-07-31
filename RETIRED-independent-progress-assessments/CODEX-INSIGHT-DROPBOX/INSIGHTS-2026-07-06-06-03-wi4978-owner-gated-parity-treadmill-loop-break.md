author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T05-56-24Z-loyal-opposition-B-79612c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; loyal-opposition; explanatory output style

# WI-4978 Owner-Gated Cross-Harness Parity Treadmill — LO Concurrence, No New Verdict Filed

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001
WIs: WI-4978, WI-5038
Bridge: gtkb-wi4978-helper-compliance-audit-chokepoint (reviewed version -013 REVISED)
Reviewer: Loyal Opposition (Claude, harness B), auto-dispatched
Date: 2026-07-06 UTC

## Disposition

I was auto-dispatched to review the REVISED entry at
`bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-013.md` (a Prime Builder
blocker record). **I am filing NO new bridge verdict.** This report records my
independent concurrence, the loop analysis, and the one piece of new
information that should break the cycle.

Rationale in one line: the WI-4978 verification is blocked by a genuine,
already-adjudicated, owner-gated blocker whose root-cause fix **is already
tracked as WI-5038**; every available verdict is wrong (VERIFIED impossible,
NO-GO loop-fuel, GO nonsensical), so the correct action is record-and-stop.

## Why every verdict is the wrong move

This bridge entry is a post-implementation report, so the reviewer verdict
space is `VERIFIED` / `NO-GO` (`GO` applies only to proposals).

- **VERIFIED — impossible.** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
  and the Mandatory Specification-Derived Verification Gate forbid `VERIFIED`
  while a linked-specification test is failing without a documented owner
  waiver. The linked cross-harness parity test is genuinely RED (re-verified
  below) and the Deliberation Archive contains no waiver.
- **NO-GO — loop-fuel.** The thread has already produced six consecutive
  NO-GO verdicts (004, 006, 008, 010, 012). Each NO-GO flips the latest status
  to `NO-GO`, which dispatches Prime Builder, which files another REVISED
  blocker record, which dispatches Loyal Opposition, which files another
  NO-GO — the observed treadmill. The `-012` NO-GO (Ollama, harness D) already
  made the definitive factual record and enumerated the three owner resolution
  paths. A seventh NO-GO adds zero new information and only re-arms the loop.
- **GO — nonsensical.** `GO` is not a report verdict.

**Filing nothing is the actual loop-halt.** Leaving the latest status at
`REVISED -013` keeps the Loyal Opposition actionable signature unchanged, so
the dispatcher will not re-fire LO on `-013`. Flipping the status is what
perpetuates the treadmill; declining to flip it stops the LO→PB handoff.

## Independent verification (canonical state, not the asserting artifact)

Per the dispatch contract I re-checked the blocker directly rather than
trusting `-013`'s assertions.

1. **Parity test — still RED.** Re-ran
   `platform_tests/skills/test_bridge_propose_helper.py::test_codex_skill_adapter_parity_check`:
   `1 failed`, generator reports `would update 32 file(s)`.
   Composition of the 32 paths:
   - ~7 are `__pycache__/*.pyc` build artifacts.
   - ~12 are draft/temp LO verdict scratch files belonging to **other** work
     items (e.g. `draft-4676-verdict.md`, `draft_wi4944_v020.md`,
     `tmp/wi4842-verdict-draft.md`,
     `_temp_verdict_gtkb-target-paths-coverage-preflight-006.md`).
   - ~13 are genuine adapter/SKILL.md/MANIFEST.json/registry.toml drift.
   - Only **one** path is plausibly WI-4978-attributable
     (`.codex/skills/bridge/helpers/impl_report_bridge.py`, whose `.claude`
     canonical was touched by WI-4978).
   Conclusion: the RED test is dominated by generator pollution and
   pre-existing cross-harness drift — it is **not** a WI-4978 code defect.

2. **`.codex` ACL — still blocking, and scoped to the sandbox SID.**
   `icacls .codex` shows explicit
   `S-1-5-21-2908765920-875073000-2352713335-4168283502:(DENY)(W,D,Rc,DC)`
   plus its inheritable variant. That explicit DENY overrides the inherited
   `(M,DC)` grant lower in the list (Windows evaluates explicit DENY before
   inherited ALLOW). `DESKTOP-G6Q5ANI\micha`, `CodexSandboxUsers`, and
   `BUILTIN\Administrators` retain Modify/Full. The write block is therefore
   scoped precisely to the Codex sandbox SID, not to the directory in general.

3. **No waiver / no prior generator-hygiene decision.** Four Deliberation
   Archive searches (`WI-4978 cross-harness parity waiver`,
   `codex skill adapter parity generator pycache pollution`,
   `parity generator hygiene draft verdict exclusion`,
   `.codex ACL sandbox SID deny write repair`) returned no matches.

The `-012` NO-GO is accurate and well-founded. I concur with it.

## New information: the root-cause fix is already filed as WI-5038

Both `-012` and `-013` frame resolution path (c) as "authorize a **new** work
item to fix the parity generator's pollution." That framing is stale:

> **WI-5038** (open, P2, component `cross-harness-parity`): "Codex adapter
> parity scan counts transient scratch (pycache / draft- / temp-) as adapters,
> producing false parity failures that block unrelated WIs."

WI-5038's description records the *same* evidence from a prior WI-4978
verification session ("would-update 29 files, of which ~18 are pure pollution
(7 pyc + 11 draft/temp) and only 1 is WI-4978-attributable"). The treadmill
participants simply have not connected this thread to its already-existing
root-cause WI. **The loop is not waiting on a new WI to be authorized; it is
waiting on WI-5038 to be implemented, or on an owner waiver / ACL decision.**

## Why this is not a "capable-LO-breaks-the-deadlock" case

A capable harness should sometimes finalize past a prior harness's *capability*
limit (e.g. a harness that cannot run the verify-finalize helper over
already-done work). This is not that case, and I did not attempt to resolve it:

- The blocker is genuine unfinished work (generator defect + `.codex` mirror
  regeneration) plus an environment ACL, not merely a tool-execution gap over
  work that is otherwise complete and verifiable.
- Regenerating ~32 `.codex` files during a review would be prohibited LO
  speculative source modification (`.claude/rules/loyal-opposition.md`
  § "Prohibited: speculative source modification during review") and a
  self-fulfilling-evidence pattern.
- It is out of WI-4978's approved scope, it would bake in this session's dirty
  working-tree state, and it would not fix the generator root cause (WI-5038) —
  the pollution would recur on the next accumulation of draft scratch.

## Resolution paths (all owner-gated)

- **(a) Scoped waiver** for the parity check under
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, recorded in the
  Deliberation Archive. Fastest path; lets WI-4978 be `VERIFIED` as-is since
  the core fix is already accepted and the RED test is not a WI-4978 defect.
- **(b) Land WI-5038** (exclude `__pycache__`/`draft-`/`temp-`/other non-adapter
  scratch from the generator's parity comparison set). This collapses the
  would-update set to genuine adapter drift; the remaining genuine mirror(s)
  must then be regenerated from a context that has `.codex` write access
  (owner/admin), because the sandbox SID is ACL-denied.
- **(c) ACL decision.** The sandbox-SID DENY appears intentional (it protects
  generated `.codex` mirrors from sandbox hand-edits, since `.claude/skills` is
  canonical). If so, the correct action is "regenerate from an owner/admin
  context," not "repair the ACL." This is an owner call, not a code fix.

## Recommended way to stop the treadmill in bridge state

The clean bridge-state stop is an owner-directed `DEFERRED` entry on this
thread with a clear/resume condition such as *"resume when WI-5038 is VERIFIED
or a scoped parity-check waiver is recorded in the Deliberation Archive."*
`DEFERRED` is owner-only (Loyal Opposition cannot file it), so I flag it as a
recommendation rather than filing it. Until then, this thread should not be
re-dispatched; my declining to file a verdict leaves it parked at `REVISED -013`
without re-arming the loop.

## Findings summary

| # | Finding | Evidence | Severity | Owner action |
|---|---------|----------|----------|--------------|
| 1 | WI-4978 verification is blocked by an owner-gated blocker, not a code defect; 6 prior NO-GO verdicts | Version chain 004–012; test breakdown above | P2 | Choose resolution (a), (b), or (c) |
| 2 | Root-cause generator-pollution fix is already tracked but unlinked from this thread | WI-5038 (open, P2) vs `-012`/`-013` "authorize a new WI" framing | P2 | Prioritize WI-5038 or grant waiver |
| 3 | Further NO-GO/REVISED cycling is loop-fuel; no verdict filed this dispatch | Actionable-signature dispatch mechanics | P2 | Owner-directed DEFERRED to park thread |

## Actions taken this dispatch

- Read the full `-013` REVISED report and the `-012` NO-GO; reviewed the
  version-chain history (001–012).
- Re-ran the parity test; ran `icacls .codex`; ran four Deliberation Archive
  searches; inspected WI-4978 and WI-5038 backlog records.
- Filed **no** bridge verdict (no `-014`), made **no** source/test/adapter/ACL/
  KB mutation. This dropbox advisory is the only artifact written.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
