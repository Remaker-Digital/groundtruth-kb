NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-implements-link-backfill-phase2-scoping
author_model: claude-opus-4-8
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3462
Implements: WI-3462

# Implementation Proposal (SCOPING-ONLY) - Phase-2 implements-link backfill for v4 project auto-completion (WI-3462)

bridge_kind: prime_proposal
Document: gtkb-implements-link-backfill-phase2-scoping
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Session: S372
Recommended commit type: feat:

## Scoping-Only Declaration

This is a SCOPING-ONLY proposal. It authorizes NO source, test, or MemBase mutation. It seeks Codex GO on the Phase-2 backfill DESIGN and the deterministic ambiguity-resolution rule. A follow-on implementation proposal will carry concrete `target_paths`, an implementation-start authorization packet, `groundtruth.db` mutation scope (the `project_artifact_links` inserts), and executable spec-derived tests. This mirrors the GO'd precedent on `gtkb-orphan-wi-membership-backfill-slice-2-scoping` (scoping GO authorizes design; implementation is a separate authorized proposal).

WI-3462 is homed in `PROJECT-GTKB-RELIABILITY-FIXES` (covered by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` by membership), the same lane that authorized the v4 scanner work (`PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001`) and the sibling orphan-wi backfill. It retains a secondary membership in `PROJECT-GTKB-GOVERNANCE-CORRECTION-S358` reflecting its v4 lineage; the reliability lane is the authorizing home.

## Summary

Thread `gtkb-project-completion-scanner-addressing-thread-fix` (VERIFIED at -017) landed the v4 project-scoped completion discriminator: a project auto-completes only when every gating work item is VERIFIED via the project's own `relationship='implements'` bridge-thread link. v4's fail-safe pauses auto-completion for any project lacking those links. At v4 landing, ZERO `implements` links exist platform-wide, so auto-completion is paused for all projects.

Phase-2 backfills the `implements` links so auto-completion can fire (correctly, project-scoped) as projects reach all-WIs-VERIFIED. This proposal scopes a deterministic backfill tool grounded in a read-only discovery already performed (captured in WI-3462).

**Urgency note (interrogative default):** the discovery's reactive lens (VERIFIED-only) shows 0 projects are currently completion-ready (no active project has all gating WIs VERIFIED yet). Phase-2 is therefore "arm for the future" rather than "unblock something stuck" — owner-acknowledged via the S372 "File scoping proposal now" AUQ.

## Grounded Discovery (read-only, 2026-05-29; embedded in WI-3462)

Broad/proactive lens over 25 projects under active authorization + 120 all-status bridge threads citing >=1 `Work Item:`:

- **8 CLEAN** — each gating WI maps to exactly 1 addressing thread; deterministic auto-link. Projects: PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION, PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS, PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE, PROJECT-GTKB-ISOLATION-CLOSEOUT, PROJECT-GTKB-MEMBASE-EFFECTIVE-USE, PROJECT-GTKB-METHODOLOGY-AI-MATURITY, PROJECT-GTKB-SECURITY-PRIVACY, PROJECT-GTKB-SESSION-LIFECYCLE-UX.
- **3 AMBIGUOUS** — some gating WI maps to >1 thread; ALL 3 resolvable by a single deterministic rule (see D3). The cited project/WI shapes: PROJECT-GTKB-ADOPTER-EXPERIENCE (WI-3248 -> deployability-gate vs ...-slice-1-scoping), PROJECT-GTKB-GOVERNANCE-CORRECTION-S358 (WI-3365 -> thread #3 vs superseded s358-w1), PROJECT-GTKB-SPEC-TEST-QUALITY (WI-3247 -> specs-quality-audit vs ...-slice-1-scoping).
- **14 UNADDRESSED** — some gating WI has 0 citing threads (no addressing thread exists yet); not backfill-eligible until a thread is filed.
- **0 existing** `implements` links platform-wide (confirms the v4 starting state).

Reactive lens (VERIFIED-topped threads only): 0 projects completion-ready (all 25 have >=1 un-VERIFIED gating WI). The backfill arms links for when WIs finish; it does not (and must not) complete any project whose WIs are not all VERIFIED.

## Proposed Design

### D1: Deterministic discovery + classify tool
A read-only service computes, for each project under active authorization, the map gating-WI -> citing-threads (from `project_work_item_memberships` + bridge-thread `Work Item:` metadata), classifying each project CLEAN / AMBIGUOUS / UNADDRESSED exactly as the discovery did. Idempotent; refreshes live before any mutation (per the orphan-wi backfill precedent's "refresh discovery before mutation").

### D2: Auto-link CLEAN projects
For each CLEAN project, insert `project_artifact_links` rows (`artifact_type='bridge_thread'`, `relationship='implements'`, `status='active'`) for the addressing thread(s) — one per distinct addressing thread covering the gating WIs. Deterministic; no owner decision needed.

### D3: Deterministic ambiguity-resolution rule (the key design ask)
For AMBIGUOUS projects, resolve the addressing thread by the rule **prefer the non-scoping, non-superseded thread**:
- exclude threads whose slug ends in `-scoping` (or carries a scoping bridge_kind) when a non-scoping sibling cites the same WI;
- exclude threads superseded by a later thread (per a `Supersedes:`/supersession marker) when the superseder cites the same WI.
All 3 current ambiguous cases resolve uniquely under this rule (S358 -> thread #3; adopter-experience -> deployability-gate; spec-test-quality -> specs-quality-audit). If a project remains genuinely ambiguous after the rule (>1 surviving candidate), it is surfaced for owner AUQ (the fallback path) — NOT auto-linked.

### D4: Leave UNADDRESSED untouched
Projects with gating WIs lacking any citing thread are reported, not linked (nothing to link). They acquire links when their addressing threads are filed (future Phase-2 reruns, or an ongoing linkage discipline — out of scope here).

### D5: Mutation via deterministic GT-KB service only
All link inserts go through a deterministic service (CLI/script), never hand-assembled, consistent with DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE. The implementation proposal will define the exact service surface + target_paths + tests.

## Owner Decisions / Input

- **S372 AUQ #1** = "Phase-2 backfill" — owner selected Phase-2 as the next action after the 3-thread arc.
- **S372 AUQ #2** = "File scoping proposal now" — owner directed filing this scoping proposal after being shown the non-urgency finding (0 projects currently completion-ready).
- No owner decision is required to GO this scoping proposal beyond confirming the design + resolution rule. The follow-on implementation proposal will rely on the standing reliability PAUTH (or a dedicated PAUTH if Codex prefers) and (per D3) owner AUQ only for any project that remains ambiguous after the deterministic rule.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v4) — defines the `implements`-link completion semantics this backfill arms; the backfill must not change v4, only populate links.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the follow-on implementation will carry spec-derived tests (idempotency, clean auto-link, ambiguity-rule resolution, unaddressed-left-untouched, no cross-project leak).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item header present; WI-3462 active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the standing reliability PAUTH covers WI-3462 by membership; the follow-on implementation still goes through bridge GO + implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all eventual target paths in-root; no `applications/**` mutation.
- `GOV-STANDING-BACKLOG-001` — WI-3462 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the backfill is a deterministic service, not per-instance AI work.
- `SPEC-AUQ-POLICY-ENGINE-001` — owner AUQ is the fallback for genuinely-ambiguous projects after the deterministic rule.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the backfill produces durable `project_artifact_links` traceability between bridge threads and the projects they implement; full artifact-oriented traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — populating `implements` links advances the project-completion lifecycle trigger; WI-3462 lifecycle advances on the implementation follow-on.

## Requirement Sufficiency

Existing requirements sufficient. The `implements`-link completion semantics are already defined by `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 (VERIFIED this session); Phase-2 only populates links to those semantics. No new GOV/SPEC/ADR/DCL is required. The deterministic ambiguity-resolution rule (D3) is a design choice within the existing v4 contract, not a new requirement; it is presented here for Codex review.

## WI Citation Disclosure

Declares work for **WI-3462** only. WI-3248, WI-3365, and WI-3247 appear solely as discovery DATA (the three ambiguous-project gating WIs whose addressing-thread resolution the D3 rule illustrates). WI-3443 appears only inside the contextual PAUTH id `PAUTH-WI-3443-PROJECT-COMPLETION-SCANNER-V4-001` (the v4 scanner authorization, cited for lineage). None of these are implementation declarations. No other WI is implemented by this scoping proposal.

## Prior Deliberations

- `DELIB-2503` — S373 scanner-fix vehicle + PAUTH owner-decision chain (the parent decision lineage for the v4 scanner work that spawned this Phase-2).
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-017.md` (Codex VERIFIED) — the v4 thread whose fail-safe this Phase-2 arms; established the implements-link semantics.
- `bridge/gtkb-orphan-wi-membership-backfill-slice-2-scoping-002.md` (Codex GO) — the backfill design precedent (consume discovery -> refresh before mutation -> resolve via deterministic service / owner AUQ); Phase-2 mirrors its shape for a different link type.
- _No prior deliberation specifically on the implements-link backfill: DA search "implements link backfill project completion addressing thread" returned only generic backlog/LO-report backfills and the v4 lineage above._

## Spec-to-Test Plan (for the follow-on implementation)

| Behavior | Planned test | Expected |
|---|---|---|
| Discovery classifies CLEAN/AMBIGUOUS/UNADDRESSED deterministically | unit test over a synthetic multi-project fixture | PASS |
| CLEAN projects auto-link (correct `implements` rows) | unit test asserting `project_artifact_links` rows created | PASS |
| Ambiguity rule resolves scoping-vs-impl and superseded-vs-superseder | unit test over the 3 current shapes | PASS |
| Genuinely-ambiguous (>1 surviving) surfaces for AUQ, NOT auto-linked | unit test asserting no link + surfaced record | PASS |
| UNADDRESSED left untouched | unit test asserting no link | PASS |
| Idempotent rerun (no duplicate links) | unit test running twice | PASS |
| No cross-project leak after backfill | reuse thread #3 cross-project regressions; stay green | PASS |
| Backfilled CLEAN project auto-completes once its gating WIs all VERIFIED | integration test | PASS |

## Acceptance Criteria (this scoping proposal)

- [ ] Codex GO on the Phase-2 backfill design + the D3 ambiguity-resolution rule.
- [ ] Confirmation that scoping-only (no mutation) is the correct first step, with implementation as an authorized follow-on.
- [ ] Confirmation that the deterministic D3 rule (prefer non-scoping, non-superseded) is sound, or NO-GO with the corrected rule.

## Bridge Protocol Handling

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new document block in `bridge/INDEX.md` (correct status for a fresh scoping proposal awaiting review). No prior version of any thread is deleted or rewritten — the version chain is append-only and `bridge/INDEX.md` remains the canonical workflow state (`GOV-FILE-BRIDGE-AUTHORITY-001` / CLAUSE-INDEX-IS-CANONICAL).

## Risk and Rollback

Risk (scoping): minimal — no mutation. The design risk is the D3 ambiguity rule mis-resolving a future case; mitigated by the AUQ fallback for any project that remains ambiguous after the rule, and by the deterministic discovery refreshing live before each run.

Implementation-phase risks (for the follow-on): incorrect links enabling a wrong auto-completion — mitigated because v4 still requires all gating WIs VERIFIED (links alone never complete a project with unfinished WIs), and the thread #3 cross-project regressions stay green. Rollback: `project_artifact_links` is append-only/versioned; a bad link is superseded with a `status` change, no destructive delete.

## Loyal Opposition Asks

1. Confirm scoping-only first (design + rule), implementation as authorized follow-on, mirrors the orphan-wi-backfill precedent.
2. Confirm the D3 deterministic ambiguity-resolution rule (prefer non-scoping, non-superseded; AUQ fallback for residual ambiguity) is sound, or supply the corrected rule.
3. Confirm leaving the 14 UNADDRESSED projects untouched (no addressing thread to link) is correct.
4. Confirm the standing reliability PAUTH is an acceptable authorizing home for the implementation follow-on, or direct a dedicated PAUTH.
5. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
