author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T09-38-24Z-loyal-opposition-B-dbcd52
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition (::init gtkb lo); dispatch id 2026-07-06T09-38-24Z-loyal-opposition-B-dbcd52

# Loyal Opposition Advisory — WI-4842 formal-artifact-packet-helper: record-and-stop (no verdict)

WIs: WI-4842, WI-5042, WI-5041, WI-5040, WI-4929
Specs: DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001
Bridge thread: bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-006.md (latest = REVISED, v6)
Date: 2026-07-06 UTC

## Disposition

**Record-and-stop. No bridge verdict filed for version 006.** This is the correct
churn-minimizing headless-LO action for a REVISED report that merely re-transports
an already-adjudicated, owner-gated environment blocker with zero new reviewable
implementation content. Filing a 7th verdict would be loop-fuel (see Reasoning).

## Claim under review

Bridge version 006 (REVISED, harness A / prime-builder/codex) is a "blocked retry"
implementation report for WI-4842. It claims **zero completed deliverables** and
attributes the block to a Windows Deny-ACE on `.codex/**` for the Codex sandbox SID,
which prevents creation of the required Codex adapter surface.

## Evidence inspected (methodology trail)

- Full thread read (all 6 versions): 001 NEW proposal (A) → 002 GO (F, openrouter/LO)
  → 003 NEW blocked report (A) → 004 defective NO-GO (superseded) → 005 NO-GO
  (D, ollama/LO — honest first adjudication of the blocked 003 report) → 006 REVISED
  blocked retry (A).
- Live bridge state (`gt bridge show ... --json`): latest_status=REVISED,
  latest_path=...-006.md, version_count=6. No peer has raced a 007; 006 is current.
- **Filesystem confirms zero deliverables** (the reviewable fact, independent of the
  report's own assertions):
  - `.claude/skills/formal-artifact-packet-helper/**` — absent (Glob: no files).
  - `.codex/skills/formal-artifact-packet-helper/**` — absent (Glob: no files).
  - `platform_tests/skills/test_formal_artifact_packet_helper_skill.py` — absent (Glob: no files).
- Blocker is credible and re-confirmed across attempts: 003 cited sandbox SID
  `S-1-5-21-2908765920-875073000-2352713335-4168283502`; 006 cited a **different**
  SID `desktop-g6q5ani\codexsandboxoffline S-1-5-21-955887351-2727327028-1487890216-1004`.
  Both hit `PermissionError: [WinError 5] Access is denied` on
  `.codex\skills\formal-artifact-packet-helper`. The block is not a stale-evidence
  artifact — 006 re-verified it under a fresh process identity.
- Owner-waiver search (`gt deliberations search`): **no** WI-4842 / `.codex`-ACL
  finalization waiver exists (nearest hits are WI-4680 and WI-4990 by-reference
  finalization waivers — different work items, non-applicable). The blocker remains
  genuinely owner-gated.
- Prime Builder protocol conduct on 006 was correct: live-GO/NO-GO re-check,
  work-intent claim, implementation-start packet, attempt, fail-closed cleanup of
  partial `.claude`/registry/test edits, honest blocked report. The bridge audit
  trail is intact.

## Reasoning — why no verdict

1. **GO** is impossible — there is nothing implemented to approve.
2. **VERIFIED** is impossible — DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
   requires spec-derived verification evidence; with zero deliverables there is
   nothing to test. (This is NOT a capability-limited false-negative — the artifacts
   are genuinely absent on disk, so "finalize VERIFIED to break the loop" does not
   apply here.)
3. **NO-GO** is loop-fuel — the blocked 003 report already received its honest first
   NO-GO at 005. 006 re-transports the identical blocker with no new reviewable
   content. A 007 NO-GO is Prime-actionable → re-wakes headless Codex-A → same `.codex`
   Deny-ACL wall → another REVISED → LO → … . This exact treadmill reached **17
   versions** on the sibling thread WI-4978.
4. **DEFERRED** is owner/Prime-only — LO cannot file it.
5. Leaving 006 at REVISED (LO-actionable, Prime-non-actionable) and adding no new
   file holds the actionable signature stable; the dispatcher fires on signature
   CHANGE, so no status change = no Prime re-wake for this entry. This is the quietest
   rest state a headless LO can produce.

## Root cause — thread↔WI linkage (the concrete break)

The immediate WI-4842 block is one instance of a broader, mostly-tracked class. Do
NOT re-file these; prioritize / DEFER against them:

- **WI-5042 (filed this session, P2, dispatcher)** — the missing prevention:
  capability/writability-aware **IMPLEMENTATION** routing. WI-4842's `.codex/skills/**`
  deliverables are a **generated projection** (canonical skill at `.claude/skills/...`;
  adapters emitted by `scripts/generate_codex_skill_adapters.py`) whose intended
  producer is a non-Codex Prime context. The dispatcher routed implementation to the
  Codex sandbox — the one harness structurally Deny-ACL'd from writing `.codex/**` —
  guaranteeing a blocked report. Recurring class: **WI-4929** was the same
  Codex-sandbox Deny-ACL root on `.codex/gtkb-hooks/run_py_no_window.py`.
- **WI-5041 (open, P2, dispatcher)** — the churn symptom: no per-thread re-offer
  backoff for owner-gated verification-blocker treadmills; a record-and-stop LO is
  periodically re-woken on the unchanged REVISED. Its own acceptance summary endorses
  the record-and-stop posture.
- **WI-5040 (open, dispatcher)** — sibling axis: capability-aware **FINALIZATION**
  routing (commit-helper capability). Distinct from WI-5042 (implementation-phase
  `.codex` writability), but the same "capability-aware routing" fix family.

## Owner-gated resolution paths (the break is owner-directed)

A headless worker cannot resolve any of these; surfacing them is the contribution.

1. **Route WI-4842 implementation to a Prime harness that can write `.codex/**`** —
   e.g., an interactive Claude Prime Builder session (`::init gtkb pb`), which can
   author `.claude/skills/formal-artifact-packet-helper/SKILL.md` and run
   `scripts/generate_codex_skill_adapters.py` to emit the Codex adapter. This is the
   fastest concrete unblock and matches the designed adapter-generation flow.
2. **Repair the `.codex/**` Deny-ACL** for the Codex sandbox SID(s), if the Codex
   harness is intended to self-generate its adapters (e.g.
   `icacls E:\GT-KB\.codex /remove:d "<CodexSandboxUser>" /T`). Weigh against the
   likely-intentional guard against a sandboxed Codex self-modifying its surface.
3. **Owner-directed DEFERRED** to park the thread with a clear/resume condition
   (e.g. "WI-4842 re-routed to a `.codex`-writable Prime harness, or `.codex` ACL
   repaired"), stopping the treadmill while the routing fix (WI-5042) is prioritized.

## Churn cap

Further identical dispatcher re-offers onto the **unchanged version 006** should be
handled by silent record-and-stop with **no new advisory** — this advisory is the
canonical record. Write a short addendum (not a fresh advisory) only if thread state
**materially changes**: a new version, a different blocker, an owner waiver/decision,
or artifacts actually landing on disk. Do NOT re-run the expensive premise checks
(`icacls .codex`, adapter-generator drift) on each re-offer while the blocker is
demonstrably stable and nothing has changed on disk.

## Recommended action

Owner (or an interactive Prime Builder session) selects one of the resolution paths
above. Highest-leverage: path 1 (re-route WI-4842 to a Claude Prime session), plus
prioritize **WI-5042** so the class stops recurring. No further LO verdict is owed on
this thread until its state materially changes.
