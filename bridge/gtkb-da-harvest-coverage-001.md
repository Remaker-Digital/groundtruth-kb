# Scope Proposal: DA Harvest Coverage Remediation

**Status:** NEW
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Origin:** Owner directive 2026-04-17 ~1:00 PM: "We are being too sparse about our addition of materials to the DA. We should try to include every document, even if we do not want to add the full transcript of every session."
**Scope decision:** Owner chose separate bridge (answered via AskUserQuestion on 2026-04-17 ~1:15 PM) rather than folding into `gtkb-canonical-terminology-surface` Phase 7.

## Problem Statement

**Measured coverage gap (2026-04-17):**
- 785 bridge files on disk in `bridge/`
- 60 DA entries (~7.6%) have `source_ref` containing `bridge/`
- 649 of 720 DA entries (~90%) are `source_type='lo_review'` — overwhelming bias toward Codex insight reports
- 12 DA entries total are `source_type='owner_conversation'` across the project history
- S280+ session window: 12 DA entries, zero touch branding/terminology/membase/rename despite 100+ mentions in raw transcripts across 2026-04-13, 2026-04-16, 2026-04-17 sessions

**Downstream effects observed in S299:**
1. Prime Builder listed "MemBase" as an open clarification question in `bridge/gtkb-start-here-adopter-rewrite-001.md` despite the term being extensively documented in prior DA entries, standalone repo-root docs, and GT-KB published docs. Root cause: the prior knowledge was not discoverable through the default retrieval flow.
2. Owner directive: "if we start a fresh session, all of our agreements and shared understanding is not durable. This is exactly what the DA was intended to resolve."

## Owner Specification Language (GOV-09 trigger)

Verbatim directive 2026-04-17:

> "We should try to include every document, even if we do not want to add the full transcript of every session."
>
> "If that information is not in the DA, it should be added and we should determine why not. If it was there, we should determine why you did not find it, and why you did not search the DA automatically."

Derived requirements:

1. Every significant document (bridge thread, LO report, governance diagnosis, owner decision, ADR/DCL/IPR/CVR, post-implementation report) MUST reach DA.
2. Raw session transcripts MUST NOT reach DA (too noisy, corrupts retrieval).
3. Harvest MUST be mechanically enforced, not procedurally suggested.
4. Failure to find an existing DA entry that should be there is either (a) a harvest gap to close, or (b) a retrieval failure to diagnose.

## Scope (in)

**Deliverable A — Harvest policy specification:**
1. Explicit inclusion criteria: every bridge thread (one DELIB per thread, summarizing NEW + GO + REVISED + VERIFIED versions, not one per file); every LO report in `CODEX-INSIGHT-DROPBOX/`; every owner-decision conversation with substance; every ADR/DCL/IPR/CVR at creation; every post-implementation report at VERIFIED.
2. Explicit exclusion criteria: raw transcripts, bridge scan status files, routine poller ticks, code artifacts (those live elsewhere).
3. DELIB compression rule: one entry per thread, not per file, with version trail embedded.

**Deliverable B — Retroactive sweep:**
1. One-time back-harvest of un-harvested bridge threads (~130 distinct threads; ~725 files not yet in DA).
2. Target: bridge-thread coverage from ~7.6% (file level) to ≥95% (thread level).
3. Script: `scripts/retroactive_harvest_bridge_threads.py` that groups bridge files by thread (name-prefix match), generates a summary per thread, inserts one DELIB per thread with `source_type='bridge_thread'`.
4. Run once, idempotent (content_hash dedupe prevents re-insertion).

**Deliverable C — Mechanical enforcement:**
1. Session-wrap hook runs expanded `scripts/harvest_session_deliberations.py` with new selectors covering owner_conversation, bridge_thread, methodology_review, report types.
2. Wrap failure is LOUD, not silent: if harvest script exits non-zero or emits warnings, wrap reports ALARM rather than "clear".
3. `UserPromptSubmit` hook extension: if Prime Write-calls a `bridge/*-001.md` new proposal, hook emits reminder to run DA search first. Not blocking (would be too aggressive), but visible in system message.

**Deliverable D — Doctor check:**
1. Extension to `gt project doctor`: verify that every VERIFIED bridge thread has at least one DELIB with matching `source_ref`. Flag gaps as WARN (not ERROR, because legacy backlog exists).
2. Count-based check: if DA bridge-source-ref count drops below a threshold fraction of total VERIFIED bridges, flag ALARM.

**Deliverable E — Ongoing coverage metric:**
1. Dashboard metric: DA bridge coverage % (DELIB count with bridge source_ref / VERIFIED bridge thread count).
2. Target: ≥95% steady-state.
3. Trend monitoring catches drift (e.g., a run of new bridges where harvest regressed).

## Scope (out)

- No transcript harvesting. Transcripts are operational artifacts, not governance artifacts.
- No retroactive harvest of LO reports (already at ~649 DA entries — bulk of those are LO reports; coverage there is good).
- No changes to DA schema.
- No changes to ChromaDB embedding index (existing search infra is adequate; the gap is input, not retrieval).
- No rewrite of `scripts/harvest_session_deliberations.py` wholesale — extending is cheaper than replacing.

## Proposed Spec Inventory

After Codex GO, record in MemBase (`type=requirement`, `tags=['da-coverage','governance','harvest']`):

| # | Draft ID | Requirement |
|---|----------|-------------|
| 1 | SPEC-DA-HARVEST-INCLUSION | DA harvest MUST include every bridge thread, LO report, ADR/DCL/IPR/CVR, owner-decision conversation, and post-implementation report. |
| 2 | SPEC-DA-HARVEST-EXCLUSION | DA harvest MUST NOT include raw session transcripts, bridge scan status files, or routine poller activity. |
| 3 | SPEC-DA-THREAD-COMPRESSION | DA MUST store one DELIB per bridge thread (not per file), with the version trail embedded in the summary. |
| 4 | SPEC-DA-MECHANICAL-ENFORCE | Session-wrap MUST fail LOUD if harvest script exits non-zero. No silent-failure mode permitted. |
| 5 | SPEC-DA-COVERAGE-METRIC | Dashboard MUST show DA bridge-thread coverage percent with ≥95% target. |
| 6 | SPEC-DA-RETROACTIVE-SWEEP | Retroactive back-harvest script MUST be idempotent via content_hash dedupe and run once to close the pre-2026-04-17 coverage backlog. |
| 7 | SPEC-DA-DOCTOR-CHECK | `gt project doctor` MUST flag missing bridge-thread coverage as WARN. |

## Prior Deliberations (cited per deliberation-protocol.md)

- `DELIB-0715` (2026-04-17) — MemBase Canonical Definition; the owner settlement that exposed this gap.
- `DELIB-0716`, `DELIB-0717`, `DELIB-0718` (2026-04-17) — first examples of bridge_thread harvest compression.
- `DELIB-0105` (2026-04-12) — GroundTruth rename transition; in DA but had no `session_id`, reducing discoverability.
- `bridge/gtkb-canonical-terminology-surface-002.md` (Codex GO 2026-04-17) — the paired remediation workstream for the complementary governance gap.

## Relationship to `gtkb-canonical-terminology-surface`

- Same root cause (Prime Builder governance surface not enforcing discoverability) but distinct scope.
- Canonical-terminology-surface focuses on **what vocabulary exists and is loaded**. Harvest-coverage focuses on **what deliberations reach DA so retrieval works**.
- Both land before S300 bootstrap ideally. If scheduling forces sequencing, canonical-terminology-surface has priority because its failure is more visible to CTO trial.
- Doctor checks can share infrastructure: one doctor command, two rule groups.

## Implementation Approach

- **Phase 1:** spec recording (7 specs into MemBase) + WI creation. Gated by Codex GO on this bridge.
- **Phase 2:** harvest policy document + selector extensions to existing harvest script. Small surface; fast.
- **Phase 3:** retroactive sweep script + dry-run against real data + owner/Codex sanity-check on sample output before committing inserts.
- **Phase 4:** wrap-hook LOUD-failure mode + bridge-scan reminder hook.
- **Phase 5:** doctor extension + coverage metric on dashboard.
- **Phase 6:** VERIFIED + post-implementation report (which itself will be harvested per the new policy as the first real test of the mechanical enforcement).

## Verification Approach

- **Coverage measurement:** post-Phase 3, bridge-thread coverage metric ≥95%.
- **Dedupe assertion:** running the retroactive script twice produces zero duplicate inserts (content_hash gate).
- **Enforcement assertion:** simulating a harvest failure in session-wrap produces ALARM output, not silent pass.
- **Retrieval self-test:** run `search_deliberations("MemBase")` at post-implementation session start; expect ≥3 relevant DELIBs surface in the first page of results.

## Timeline

- **2026-04-17:** scope bridge posted NEW (this file). Codex review overnight.
- **2026-04-18:** on GO, Phase 1–3. Retroactive sweep dry-run for owner/Codex review.
- **2026-04-19:** Phase 4–5. Doctor check + dashboard metric.
- **2026-04-20:** VERIFIED + post-implementation report + S300 readiness check.

## Open Questions for Codex

1. Is `scripts/harvest_session_deliberations.py` the right script to extend, or is there a better entry point?
2. Does the retroactive sweep need a separate script, or should it be a flag on the existing harvest script (`--retroactive --since <date>`)?
3. For doctor coverage check: is a separate check rule preferred, or extension to an existing one?
4. Should the wrap-hook LOUD-failure be an opt-in flag initially, to avoid breaking past wrap flows that may depend on silent pass?
5. Any existing assertion infrastructure that can back the coverage metric without new plumbing?

## Rollback / Containment

- Retroactive script is idempotent (content_hash); can be re-run or partially re-run safely.
- Selector extensions to harvest script are additive; no existing harvesting behavior changes.
- Wrap LOUD-mode can be flag-gated initially so it doesn't break current wrap semantics unexpectedly.
- Doctor check is WARN-level by default per paired canonical-terminology-surface pattern (error for missing required terms, warn for drift).

## Next Steps After Codex GO

1. File implementation bridge `gtkb-da-harvest-coverage-implementation-001.md`.
2. Execute Phases 1–5.
3. Post-implementation report + Codex VERIFIED.
4. Measure: how does this change session-boundary durability in the next live CTO-facing session?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
