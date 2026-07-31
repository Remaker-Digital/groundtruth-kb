author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T11-48-34Z-loyal-opposition-B-48de5f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition (::init gtkb lo); dispatch id 2026-07-06T11-48-34Z-loyal-opposition-B-48de5f

# Loyal Opposition Advisory Addendum — WI-4842 record-and-stop still holds at v010; advisory-only posture is empirically insufficient → escalate to a mechanical (owner/Prime) break

WIs: WI-4842, WI-5042, WI-5041, WI-5040, WI-4840, WI-4929
Specs: DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001
Bridge thread: bridge/gtkb-wi4842-formal-artifact-packet-helper-scaffold-010.md (latest = REVISED, v10)
Canonical prior advisory: INSIGHTS-2026-07-06-09-38-wi4842-record-and-stop.md (written at v006)
Date: 2026-07-06 UTC

## Disposition

**Record-and-stop. No bridge verdict filed for version 010.** Reaffirms the canonical
09:38 advisory. This addendum exists only because thread state MATERIALLY CHANGED since
that advisory (v006 → v010) — the prior advisory's own "churn cap" section authorizes a
short addendum on material change and forbids a fresh full advisory or a repeat verdict.

## Material change since the 09:38 canonical advisory

The 09:38 record-and-stop was filed at v006. Since then the treadmill advanced **two full
cycles** — not because Prime produced anything new, but because other dispatched LO
harnesses filed NO-GO verdicts that re-armed Prime:

- v007 NO-GO (Antigravity-C, after the 09:38 advisory) → re-woke Codex-A
- v008 REVISED blocked retry (Codex-A, ~10:21Z) — identical `.codex` Deny-ACL block
- v009 NO-GO (Antigravity-C, 11:07Z) → re-woke Codex-A
- v010 REVISED blocked retry (Codex-A, 11:25Z) — identical block
- 11:48Z → dispatched to this session (Claude-B / loyal-opposition)

**Empirical finding: advisory-only record-and-stop does NOT hold this loop.** A dropbox
advisory is non-mechanical: it cannot stop the dispatcher from re-offering the thread to a
*different* LO harness that then files a NO-GO (as Antigravity-C did twice). The loop is
broken only by a mechanical action, and every such action is outside a headless LO's
authority. This is the WI-5041 churn class made concrete.

## Premises re-verified against canonical state (this session — not trusting the artifact)

- Role: harness B = claude / loyal-opposition, active, dispatchable (`gt harness roles`).
- Live status: `gt bridge show gtkb-wi4842-formal-artifact-packet-helper-scaffold --json`
  → latest_status=REVISED, version_count=10.
- Blocker still real and structural: Codex-A is the **only** dispatchable prime-builder in
  the registry, and it is Deny-ACL'd on `.codex` for its sandbox SID. `.codex/skills/**` is
  writable by non-Codex contexts — proven by the many committed adapters under
  `.codex/skills/*` (git log touching `.codex/skills`: WI-3445, WI-5004, WI-4957 …). The
  intended producer of the adapter projection is Claude, not the Codex sandbox (WI-5042
  thesis, diagnosed from this exact thread).
- Report v010 is accurate: no `formal-artifact-packet-helper` entry retained in
  `config/agent-control/harness-capability-registry.toml` (grep: no match). The registry's
  only uncommitted diff is a **sibling WI-4840** (`skill.advisory-disposition`) entry —
  unrelated to WI-4842. No false "retained entry" claim to flag.
- Sibling WI-4840 is stuck on the SAME wall: its `.codex/skills/advisory-disposition/`
  adapter is also absent on disk. Confirms a recurring CLASS blocker, not a one-off (cf.
  WI-4929, the same Codex-sandbox Deny-ACL root on `.codex/gtkb-hooks/run_py_no_window.py`).
- No owner `.codex`-ACL / finalization waiver exists for WI-4842 (per the 09:38 search;
  nothing has changed the owner-gated status).

## Reasoning — why no verdict (unchanged from 09:38)

1. **GO** impossible — nothing implemented to approve.
2. **VERIFIED** impossible — DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 requires
   spec-derived evidence; zero deliverables exist on disk. This is genuine absence, NOT a
   capability-limited false-negative, so "finalize VERIFIED to break the loop" does not
   apply here.
3. **NO-GO** = loop-fuel — Prime-actionable → re-wakes headless Codex-A → same `.codex`
   Deny-ACL wall → another REVISED. This exact treadmill reached 17 versions on the sibling
   thread WI-4978.
4. **DEFERRED** = owner/Prime-only — LO cannot file it.
5. Leaving v010 at REVISED (LO-actionable, Prime-non-actionable) and adding no new bridge
   file holds the actionable signature stable; the dispatcher fires on signature CHANGE, so
   no status change = no Prime re-wake for this entry.

## Escalation — advisory-only has now failed twice; the break must be mechanical

Because the loop demonstrably survived the 09:38 record-and-stop, the recommendation
sharpens from "surface options" to "this thread needs a mechanical break now." All three
are owner/Prime actions a headless LO cannot execute:

1. **Owner-directed DEFERRED (highest-leverage immediate break).** Park the thread out of
   the actionable pool with a clear/resume condition: "WI-4842 re-routed to a
   `.codex`-writable Prime harness, or `.codex` ACL repaired." This is the ONLY action that
   stops *every* LO harness (not just this session) from re-arming the loop.
2. **Route WI-4842 (and sibling WI-4840) implementation to a Claude Prime session**
   (`::init gtkb pb`) that can author `.claude/skills/.../SKILL.md` and run
   `scripts/generate_codex_skill_adapters.py` to emit the `.codex` adapter. Fastest concrete
   unblock; matches the designed adapter-generation flow.
3. **Prioritize WI-5042** (writability-aware IMPLEMENTATION routing) and **WI-5041**
   (per-thread re-offer backoff). WI-5042 was diagnosed from this exact thread; both are
   already filed P2 dispatcher defects — do NOT re-file them.

## Churn cap

Further re-offers onto unchanged v010 → silent record-and-stop, no new advisory. The 09:38
canonical advisory plus this addendum are the record. Write a new addendum only on material
change (a new version, a different blocker, an owner waiver/decision, or artifacts landing
on disk). Do not re-run the expensive premise checks (`icacls .codex`, adapter-generator
drift) on each re-offer while the blocker is demonstrably stable.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
