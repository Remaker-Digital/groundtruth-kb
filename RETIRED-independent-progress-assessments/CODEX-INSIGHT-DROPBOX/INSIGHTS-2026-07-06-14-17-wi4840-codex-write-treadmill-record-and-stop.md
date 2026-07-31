author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T14-09-46Z-loyal-opposition-B-1fcc6c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code bridge auto-dispatch; loyal-opposition role; headless worker (no interactive owner channel)

# Loyal Opposition Insight — WI-4840 advisory-disposition skill scaffold: `.codex` write-boundary treadmill (record-and-stop, no verdict)

Prepared: 2026-07-06T14-17Z
Author: loyal-opposition / claude (harness B)
Session: 2026-07-06T14-09-46Z-loyal-opposition-B-1fcc6c (headless bridge auto-dispatch)
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, ADR-CROSS-HARNESS-PARITY-001, ADR-CODEX-HOOK-PARITY-FALLBACK-001, GOV-HARNESS-ONBOARDING-CONTRACT-001
WIs: WI-4840, WI-4842, WI-5040, WI-5041, WI-5042
Bridge: gtkb-wi4840-advisory-disposition-skill-scaffold (versions -001 .. -005)

## Disposition

**RECORD-AND-STOP. No bridge verdict filed.** This is a known, already-diagnosed
`.codex` write-boundary treadmill (class root cause: WI-5042). Filing NO-GO would
re-arm the loop; filing VERIFIED is impossible. The honest Loyal Opposition action
for this class is record-and-stop with no verdict (per WI-5041's own text), plus an
owner-facing mechanical-break recommendation. This mirrors the established sibling
addenda `INSIGHTS-2026-07-06-11-48-wi4842-reoffer-addendum.md` and
`INSIGHTS-2026-07-06-12-05-wi4978-treadmill-mechanical-break.md`.

## Review scope and independence

- Dispatched to review the latest actionable entry: `-005` (status NEW,
  `bridge_kind: implementation_report`, a blocked continuation report).
- Live bridge state confirmed: latest status NEW at
  `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-005.md`; no peer has moved it.
- Review independence holds: report author session
  `2026-07-06T13-53-16Z-prime-builder-A-11729f` (Codex-A) differs from this
  reviewer session.

## The treadmill (full thread chain)

| Ver | Actor | Status | Substance |
| --- | --- | --- | --- |
| -001 | Codex-A (Prime) | NEW | Proposal; 5 target paths, 2 under `.codex/` |
| -002 | Ollama-D (LO) | GO | Approved |
| -003 | Codex-A (Prime) | NEW | Blocked report: `.claude` skill + registry + test done; `.codex/` files denied |
| -004 | Antigravity-C (LO) | NO-GO | "Do the Codex projection remediation" — which Codex structurally cannot do |
| -005 | Codex-A (Prime) | NEW | Still blocked; same ACL Deny; asks not to re-dispatch the unwritable loop |

The `-004` NO-GO demanded remediation the dispatched Codex sandbox is structurally
incapable of performing, guaranteeing `-005` would re-report the identical blocker.
That is the loop.

## Verified findings (canonical state, not the artifact's assertion)

1. **Report premise is accurate.** `.claude/skills/advisory-disposition/SKILL.md`
   exists (7988 bytes). `.codex/skills/advisory-disposition/SKILL.md` is genuinely
   absent. Implementation is incomplete — not merely blocked-on-commit.
2. **Blocker is Codex-sandbox-specific, not universal.** `.codex` is WRITABLE from
   this Claude-B context (`test -w .codex` → writable). The Deny-ACE that blocks
   Codex-A is scoped to the Codex sandbox SID. This directly confirms WI-5042's
   thesis: the `.codex` adapter is a generated projection whose intended producer
   is a non-Codex (Claude) Prime context.
3. **Root cause is already filed as WI-5042** (P2 defect, `dispatch`):
   "Capability/writability-aware IMPLEMENTATION routing: dispatcher routes GO'd
   .codex-writing implementations to the Codex Prime harness that is Deny-ACL'd on
   .codex." Diagnosed 2026-07-06 during headless-LO review of the sibling WI-4842
   thread. Recurring CLASS (WI-4929 same root; WI-4842 same treadmill to -013; now
   WI-4840). Siblings: WI-5041 (per-thread re-offer backoff), WI-5040
   (capability-aware finalization routing).
4. **No mechanical break has landed.** No recent commit finalizes WI-4840 or lands
   WI-5042/5041; no owner-DEFERRED DELIB exists for this treadmill. The loop is live.

## Why no verdict

- **NO-GO is loop-fuel.** It flips the actionable signature NEW→NO-GO, re-dispatching
  Codex-A Prime, which re-hits the same Deny-ACE and re-files a blocked report →
  NEW → LO re-dispatched. The sibling WI-4842 thread reached version -013 this way.
- **VERIFIED is impossible.** The two `.codex/` target files are absent and the
  parity/catalog tests are RED. This is incomplete implementation, not blocked
  finalization — no owner waiver or by-reference finalization waiver can conjure
  missing files.
- **Record-and-stop holds the actionable signature stable** (WI-5041), which is the
  best available outcome short of the mechanical fix.

## Why I did not self-implement (capability ≠ authority)

`.codex` is writable by Claude-B, so this reviewer *could* create the adapter. It
must not: (a) `loyal-opposition.md` prohibits speculative source modification during
review — writing a file the proposal assigns to Prime's implementation phase is
pre-implementation; (b) the "capable-LO-finalizes-VERIFIED" exception applies only
to blocked finalization of complete work, not to incomplete implementation; (c) the
correct actor is a Claude **Prime** session, not a Claude LO dispatch.

## Recommended mechanical break (interactive owner / Prime session)

Preferred, in order:

1. **Owner-DEFERRED on this thread (and the sibling WI-4842 thread).** Clean,
   immediate loop-stop. Suggested clear/resume condition: "when WI-5042
   capability-aware implementation routing lands, OR when a Claude Prime session is
   available to write the `.codex` adapter." DEFERRED is Prime/owner-only; a headless
   LO cannot file it.
2. **Complete it directly via a Claude Prime session.** The operative GO remains
   `-002`. A Claude Prime context can `implementation_authorization.py begin`, write
   `.codex/skills/advisory-disposition/SKILL.md` (source SHA per `-005`:
   `56410b3b28a752001bec269aa03a7360e4ccfd2e5dc0a5a84d6df9c9085614be`) + the
   `.codex/skills/MANIFEST.json` entry, run the tests, and file `-006` as a real
   implementation report for independent LO verification. Caveat: the full adapter
   generator reports ~34-file drift (unrelated stale adapters + WI-5038 scratch
   pollution); the Prime session must scope the write to the WI-4840 targets or
   handle that drift, not blanket-run the generator.
3. **Land WI-5042 (routing) / WI-5041 (backoff)** to fix the class so the dispatcher
   stops routing `.codex`-writing GO'd work to the Deny-ACL'd Codex sandbox.

## What I deliberately did NOT do

- No bridge verdict (avoids re-arming the loop).
- No duplicate WI or advisory — WI-5042/5041/5040 already cover this class; per prior
  guidance, do not re-ask the owner to "authorize a new WI" that already exists.
- No self-implementation of the `.codex` targets (LO role integrity).

## Residual limitation

Record-and-stop from one LO session does not bind the multi-LO pool: another LO
harness (Antigravity-C / Ollama-D / a fresh Claude-B dispatch) may still be re-woken
on the unchanged NEW signature and could file a NO-GO, re-arming the loop (this is
precisely the WI-5041 defect). A durable stop requires the owner-DEFERRED or the
WI-5042/5041 fix above.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
