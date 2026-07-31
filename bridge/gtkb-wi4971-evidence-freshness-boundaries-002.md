NO-GO

# Loyal Opposition Verdict — NO-GO — WI-4971 Evidence Freshness and Archival Boundaries

bridge_kind: lo_verdict
Document: gtkb-wi4971-evidence-freshness-boundaries
Version: 002
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-06 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4971-evidence-freshness-boundaries-001.md (NEW; prime_proposal; prime-builder/codex; harness A; author session 019f3170-d706-77d3-b3e1-be39d47f3eda)

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-06T01-17-11Z-loyal-opposition-B-4e5b0a
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition

## Verdict Summary

NO-GO on a single, cheap-to-fix specification-linkage gap. The proposal is
well-formed, bounded, correctly authorized, and passes both mechanical
preflights — it is roughly one revision away from GO. The blocker is
substantive, not structural: a proposal whose entire subject is *evidence
freshness* does not cite the canonical GT-KB freshness governance
(`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`) and does not reconcile its new
read-governance config against the platform's existing SoT read-discipline
registry (`config/registry/sot-artifacts.toml` / `DCL-SOT-READ-HOOK-CONTRACT-001`).
Per the file-bridge protocol's Mandatory Specification Linkage Gate, a missing
*relevant governing* specification is NO-GO, and the reconciliation it forces is
a design question best settled before the config is authored, not after.

## Positive Confirmations (what passes)

- Structural gates all present: status token; Specification Links (12 specs);
  Prior Deliberations; Owner Decisions / Input; `target_paths`; Requirement
  Sufficiency; project linkage (PAUTH + Project + Work Item); In-Root Placement
  Evidence; Specification-Derived Verification Plan; Recommended Commit Type.
- Root boundary: all four target paths in-root; the report path is under the
  allow-listed `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. PASS.
- Authorization: WI-4971 is a real open P2 item in
  PROJECT-HARNESS-EQUIVALENCE-PHASE-3 (subproject gap-09); PAUTH-PROJECT-HARNESS-
  EQUIVALENCE-PHASE-3-WI4971-BATCH-C-20260705 is cited; owner continuation
  DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE is cited. Valid.
- Review independence: author is harness A / prime-builder / session
  019f3170-d706-77d3-b3e1-be39d47f3eda; this reviewer is harness B /
  loyal-opposition / unrelated dispatch session
  2026-07-06T01-17-11Z-loyal-opposition-B-4e5b0a. Satisfied.
- Scope discipline: the proposal explicitly disclaims startup-contract mutation,
  dispatcher routing, and bulk archive migration. Good — this keeps the slice
  bounded.
- Mechanical preflights BOTH pass (reproduced under "Mechanical Preflight
  Evidence"): applicability `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`; clause preflight
  exit 0, 0 blocking gaps, 4/4 must_apply clauses have evidence.

## Finding 1 [P1 — NO-GO blocker] — Canonical freshness governance absent from Specification Links

**Observation.** The Specification Links section cites 12 governing specs
(project-authorization, bridge-authority, spec-linkage, verified/testing,
token-budget, session self-initialization, artifact-oriented governance,
lifecycle-triggers). It does NOT cite `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the
platform's canonical governance for freshness — nor the existing SoT
read-discipline surface (`DCL-SOT-READ-HOOK-CONTRACT-001`,
`GOV-PLATFORM-SOT-REGISTRY-001`, `config/registry/sot-artifacts.toml`,
`.claude/rules/sot-read-discipline.md`).

**Deficiency rationale.** This is not a tangential spec. The proposed classifier
(Proposed Scope) labels evidence references as "current, stale,
archival-citation-only, full-read-justified, or missing". "Current" and "stale"
are freshness classifications, and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (v3) is
precisely the governance that defines them. Its Scope covers "State queries: any
code that asks 'what is the current state of X?'" and any read-path producing a
state claim; its Forbidden read patterns prohibit "Trusting summaries or
paraphrases of canonical state." A classifier that authorizes compact/current
reads by default therefore operates *inside* that governance's jurisdiction and
must not license a compact summary in place of a fresh canonical read when the
consumer is making a state claim. Conversely, GOV-SOURCE-OF-TRUTH-FRESHNESS-001's
explicit carve-out — "Historical / audit-trail reads: append-only history is
itself canonical and is not affected" — is exactly the space the
"archival-citation-only" class occupies; the proposal should anchor to that
carve-out, not silently reinvent it.

Separately, `config/registry/sot-artifacts.toml` is a live ~15 KB registry
(modified 2026-07-05) that already operationalizes read discipline via a
`forbidden_substitutes` column and a PreToolUse blocking hook
(`DCL-SOT-READ-HOOK-CONTRACT-001`). WI-4971 introduces a *second*
read-governance config, `config/governance/evidence-freshness-boundaries.toml`,
with no stated relationship to the first. Two overlapping read-governance
registries in one platform, absent an explicit relationship statement, is a
structural-drift hazard (two sources of truth for one domain). Proposal review —
before any config is authored — is the cheapest possible place to reconcile them.

**Proposed solution (minimal; ~1 revision).**
1. Add to Specification Links: `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and at least
   one SoT read-discipline anchor (`DCL-SOT-READ-HOOK-CONTRACT-001` and/or
   `GOV-PLATFORM-SOT-REGISTRY-001`).
2. Add a short "Relationship to existing SoT freshness / read-discipline"
   subsection stating: (a) `evidence-freshness-boundaries.toml` complements — does
   not duplicate or supersede — `config/registry/sot-artifacts.toml`; (b) the
   "current/stale" classification defers to `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
   for what counts as a state-truth read; (c) "archival-citation-only" aligns with
   that governance's historical/audit-trail carve-out.
3. Add one Verification-Plan row binding `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` —
   e.g., a test asserting the classifier never labels a state-claim evidence
   reference as satisfiable by a compact summary alone (state claims still require
   a fresh canonical read).

**Option rationale.** I considered GO-with-advisory (add the linkage at the
implementation-report stage). Rejected on two grounds: the file-bridge protocol
makes a missing *relevant governing* spec a NO-GO at the proposal gate; and the
registry reconciliation is a *design* decision (does the new config overlap the
existing one?) that must be settled before the config exists, not audited after.
Catching it now costs one quick REVISED; catching it post-implementation risks a
rewrite of `evidence-freshness-boundaries.toml`.

## Finding 2 [P3 — advisory, non-blocking] — Cross-link the nearest sibling gap (WI-4966)

**Observation.** WI-4966 ("Phase 3 gap 04: CLI compactness and source-of-truth
size controls"; proposal already filed at
`bridge/gtkb-wi4966-cli-compactness-sot-size-controls-001.md`) extends compact
query defaults to MemBase, the Deliberation Archive, dispatcher state, and
transcript inventories. WI-4971 governs *when* compact vs archival/full reads are
justified. These are adjacent compact-read concerns in the same project.

**Deficiency rationale.** Not a duplication blocker — they are deliberately
separate subprojects (gap-04 vs gap-09) — but WI-4971 does not cite WI-4966, so a
future reader cannot see that "compact read defaults" (WI-4966) and
"compact-vs-archival justification rules" (WI-4971) were designed to interlock
rather than overlap.

**Proposed solution.** Add a one-line cross-reference to WI-4966 (in Prior
Deliberations or Proposed Scope) naming the boundary: WI-4966 owns query-output
compactness; WI-4971 owns evidence-reference freshness/archival classification.
Cheap; prevents future overlap drift. Optional for this REVISED but recommended.

## Prime Builder Implementation Context (for the REVISED)

- Objective: clear Finding 1; optionally address Finding 2. The REVISED is filed
  as the next version, `bridge/gtkb-wi4971-evidence-freshness-boundaries-003.md`,
  status REVISED, through the governed bridge writer.
- Preconditions: none beyond the existing PAUTH (still active). No owner decision
  is required — the fix is purely additive spec-linkage plus a relationship
  subsection.
- Evidence paths to inspect: `gt spec show GOV-SOURCE-OF-TRUTH-FRESHNESS-001`;
  `config/registry/sot-artifacts.toml`; `.claude/rules/sot-read-discipline.md`;
  `gt spec show DCL-SOT-READ-HOOK-CONTRACT-001`.
- Sequence: (1) add the two spec links; (2) add the relationship subsection;
  (3) add the verification-plan row; (4) optionally cross-link WI-4966;
  (5) re-run `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py`
  on the REVISED; (6) file REVISED via the governed writer.
- Verification: both preflights still pass on the REVISED operative file.
- Rollback: none (proposal-only revision; no source/config authored yet).
- Open decisions: none require the owner.

## Mechanical Preflight Evidence (structural gates pass; NO-GO is on Finding 1)

### Applicability Preflight

- packet_hash: sha256:e4909e389a3285937387cea0ff9a86c65f9e83471d594b05ff182426e45828a2
- bridge_document_name: gtkb-wi4971-evidence-freshness-boundaries
- operative_file: bridge/gtkb-wi4971-evidence-freshness-boundaries-001.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []

### Clause Applicability

- Clauses evaluated: 5 (must_apply: 4, may_apply: 1, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)

Note: both preflights are mechanical floors that check only *registered*
cross-cutting triggers. Finding 1 concerns a relevant-but-unregistered governing
spec, which is the reviewer's independent responsibility per the file-bridge
protocol ("Loyal Opposition remains responsible for identifying relevant
specifications that are not yet represented in spec-applicability.toml").

## Prior Deliberations

- No prior deliberations matched "evidence freshness archival boundaries harness
  equivalence" (searched via `gt deliberations search`; no match). The proposal's
  own cited authorizations — DELIB-202665197 (Phase 3 child authorization) and
  DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE (Batch C continuation) — are
  accepted as the governing owner authorizations for this work.
