author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T12-05-14Z-loyal-opposition-B-ad9883
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; loyal-opposition; explanatory output style

# Loyal Opposition Insight — WI-4978 Verification Treadmill Needs a Mechanical Break

Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, ADR-CROSS-HARNESS-PARITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001
WIs: WI-4978, WI-5038, WI-5040, WI-5041, WI-5042, WI-5002
Bridge thread: gtkb-wi4978-helper-compliance-audit-chokepoint (at version 024 as of this report)
Date: 2026-07-06 UTC

---

## Why this report exists (and why no bridge verdict was filed)

I was auto-dispatched as Loyal Opposition to review `REVISED`
`bridge/gtkb-wi4978-helper-compliance-audit-chokepoint-023.md`. During the
investigation a different LO harness (Antigravity, harness C) filed
`-024 NO-GO`, so the entry I was dispatched on is now stale for my role
(latest status `NO-GO`, which is Prime-actionable, not LO-actionable).

I deliberately filed **no bridge verdict**. This is a record-and-stop to the
LO dropbox, not a verdict, because every verdict on this thread is now
loop-fuel (see Finding 1). This is the first dropbox synthesis for WI-4978;
the ~10 prior LO responses were all bridge NO-GO verdicts, which is exactly
what kept the loop alive.

## Claim

The `gtkb-wi4978-helper-compliance-audit-chokepoint` bridge thread is a
runaway NO-GO↔REVISED treadmill (24 versions and climbing) driven by a
**pre-existing, WI-4978-external, owner-gated blocker**. It cannot be closed
by any headless bridge role. It needs a mechanical break the owner (or an
interactive session) applies, and the mechanical fixes are **already filed and
open in the backlog**. No further bridge verdicts should be filed on this
thread until that break is applied.

## Evidence

1. **The core WI-4978 fix is already verified-correct.** The canonical
   adjudication is `-004` (Loyal Opposition, Claude harness B, 2026-07-05). It
   verified — by reading live code and running tests, not by trusting the
   report — that the shared bridge-compliance audit at the
   `scripts/gtkb_bridge_writer.write_bridge_file()` chokepoint satisfies both
   GO conditions [P1] and [P2] and passes all 43 focused regression tests. That
   work is sound and must NOT be re-implemented.

2. **The only blocker is a red, pollution-dominated cross-harness parity
   test.** `platform_tests/skills/test_bridge_propose_helper.py::test_codex_skill_adapter_parity_check`
   fails. `-004`'s decomposition of the (then 29, now 34) "would-update" paths:
   the large majority are transient `__pycache__/*.pyc` build files and stale
   Loyal-Opposition verdict scratch drafts belonging to *other* work items, plus
   pre-existing `SKILL.md` drift. Only `.codex/skills/bridge/helpers/impl_report_bridge.py`
   is directly WI-4978-attributable, and WI-4978 could not regenerate that
   `.codex` mirror because `.codex` carries an explicit Windows deny ACE for the
   Codex sandbox identity. **WI-4978 did not create the parity failure.**

3. **`-004` explicitly predicted this loop:** "A blind Prime Builder REVISE
   will re-hit the same `.codex` ACL and loop. Prime Builder should NOT simply
   re-file the same report expecting a different result." Versions `-005`
   through `-024` are that predicted loop.

4. **It is genuinely owner-gated.** Recording `VERIFIED` against a red linked
   parity specification requires a documented owner waiver (Mandatory
   Specification-Derived Verification Gate in `.claude/rules/file-bridge-protocol.md`
   + `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`). The approved proposal
   explicitly declined to request a parity waiver, so no headless role may
   presume one. `DEFERRED`/`WITHDRAWN` (the only loop-terminating states a role
   could set here) are Prime/owner-only.

5. **The multi-harness pool actively re-arms the loop.** Harness A (Codex,
   Prime) files `REVISED` blocker responses; harnesses B (Claude) and C
   (Antigravity) file `NO-GO` verdicts. `-024` landed mid-investigation and
   re-transports the same blocker without citing the root cause. A single LO
   record-and-stop does not hold, because the next pool member re-arms it.

6. **Every mechanical fix is already filed and OPEN in the backlog** (verified
   via `gt backlog list` this session):
   - **WI-5041** — "Dispatcher: no per-thread re-offer backoff for owner-gated
     verification-blocker treadmills (launching workers re-woken on unchanged
     REVISED)." *This is the direct mechanical break for this loop.*
   - **WI-5038** — "Codex adapter parity scan counts transient scratch
     (pycache / draft- / temp-) as adapters, producing false parity failures
     that block unrelated WIs." *This makes the parity test honest again.*
   - **WI-5042** — "Capability/writability-aware IMPLEMENTATION routing:
     dispatcher routes GO'd .codex-writing implementations to the Codex Prime
     harness that is Deny-ACL'd on .codex." *This stops routing the fix to the
     one harness that structurally cannot perform it.*
   - **WI-5040** — "Capability-aware finalization routing" (adjacent).
   - **WI-5002** — the `.codex` ACL correction, currently `WITHDRAWN`.

## Severity

**P1 (governance drift).** A protocol-level dispatch cycle with no cycle-breaker
is consuming harness-investigation tokens across three harnesses on a blocker
that no bridge role can clear. Not P0 (no active misdirection — the individual
verdicts are technically honest); the defect is systemic, not a single wrong
claim.

## Impact

- Unbounded token/dispatch churn: 24 bridge versions, ~10 headless
  investigations, still climbing, with zero marginal information per cycle.
- The honest verification signal (WI-4978's core fix is done and correct) is
  buried under a wall of identical NO-GO/REVISED noise.
- Every new pool member that gets dispatched pays the full ~investigation cost
  to re-derive a conclusion already recorded in `-004`.

## Recommended action (mechanical break — owner / interactive session)

One decision, then two-to-three prioritizations. All are owner-gated; a headless
worker cannot perform them:

1. **Stop the dispatch loop now** by moving the WI-4978 thread out of an
   actionable state — either owner-directed `DEFERRED` (with clear/resume
   condition = "parity generator fixed per WI-5038 and `.codex` writability
   resolved per WI-5042/WI-5002") or owner-directed `WITHDRAWN` of the
   verification retry, with the core-fix verification tracked to a fresh report
   once parity is honest.
2. **Prioritize WI-5041** (dispatcher per-thread backoff) — this is the general
   cure for owner-gated blocker treadmills, not just this one.
3. **Prioritize WI-5038** (exclude `__pycache__`/`draft-`/`temp-` scratch from
   the parity set) so the parity test reflects genuine adapter drift only.
4. **Prioritize WI-5042 / revisit WI-5002** so `.codex`-writing work routes to a
   harness with write access (the `.codex` adapters' intended producer is a
   Claude Prime harness, not the Deny-ACL'd Codex worker).

After WI-5038 lands, the parity test likely drops to only genuine adapter drift;
after WI-5042/WI-5002, a capable harness regenerates the one WI-4978 `.codex`
mirror; then a fresh implementation report can be `VERIFIED` on the core fix
that `-004` already validated.

## Owner decision needed

Yes — the `DEFER`/`WITHDRAW` disposition of the WI-4978 thread and the relative
priority of WI-5041/WI-5038/WI-5042 are owner decisions. This report does not
mutate MemBase, does not file a bridge verdict, and does not re-arm the loop.

## Methodology trail

- Read full dispatched entry `-023` (Prime blocker response) and the canonical
  adjudication `-004` (my prior-session LO NO-GO); read the head of peer `-024`.
- `gt bridge show gtkb-wi4978-helper-compliance-audit-chokepoint --json --compact`
  → latest `-024`, status `NO-GO`, version_count 24 (peer-race confirmed).
- `gt backlog list` filtered → confirmed WI-5038 / WI-5040 / WI-5041 / WI-5042
  open; WI-5002 withdrawn.
- `grep` of CODEX-INSIGHT-DROPBOX for WI-4978 → no prior dropbox record (this is
  the first).
- Parity red-state re-confirmed from `-023` (dated today), which re-ran
  `test_codex_skill_adapter_parity_check`; not re-run here to avoid redundant
  cost — the premise is not in dispute, the disposition is.
- No source, test, config, or KB files were modified. No bridge verdict filed.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
