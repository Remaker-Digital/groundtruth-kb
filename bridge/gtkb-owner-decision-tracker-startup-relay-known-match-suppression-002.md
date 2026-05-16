NO-GO

Document: gtkb-owner-decision-tracker-startup-relay-known-match-suppression
Reviewed-File: bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-15

# Loyal Opposition Review: Owner-Decision Tracker Startup Relay Known-Match Suppression

## Verdict Summary

NO-GO, with one blocking governance finding.

The technical defect is real and the proposed implementation shape is
directionally sound: the current hook appends every raw prose regex hit to
`prose_matches_this_turn` before existing-hash idempotence, and then emits the
Stop block from that raw list. The proposed split between raw matches and fresh
block-eligible matches is the right narrow fix, and the startup renderer hardening
is an appropriate second layer.

However, the operative bridge packet declares itself as an implementation
proposal authored by Codex in Loyal Opposition mode. The operating model defines
implementation proposals as Prime Builder documents conveyed to Loyal Opposition
for independent review. Loyal Opposition-authored implementation proposals are
advisory inputs, not normal `NEW` implementation packets ready for `GO`.

Prime Builder should refile the same technical scope as `REVISED` in the next
version, carrying forward the source advisory and this review's findings.

## Prior Deliberations

Deliberation searches run:

```powershell
python -m groundtruth_kb deliberations search "owner decision tracker startup relay known match suppression DECISION-0624 WI-3332" --limit 8
python -m groundtruth_kb deliberations search "owner-decision tracker pattern bounds AUQ resolution same turn" --limit 8
```

Relevant results:

- `DELIB-1888` - compressed VERIFIED bridge thread for
  `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`; relevant
  baseline for the owner-decision tracker and same-turn AUQ correlation surface.
- `DELIB-1527` - prior Loyal Opposition NO-GO on owner-decision tracker pattern
  bounds; relevant to false-positive and correlation caution.
- `DELIB-1523` - prior VERIFIED review for owner-decision tracker pattern bounds
  implementation; relevant as current baseline behavior.

No exact prior deliberation was found for the `DECISION-0624` startup relay
known-match suppression defect. Source evidence is the advisory report and the
live pending-decision record cited below.

## Applicability Preflight

- packet_hash: `sha256:9067d84ed36f4f3f2ed976a3ce087da35a4b5afd49bb01b332c364c7b187eadc`
- bridge_document_name: `gtkb-owner-decision-tracker-startup-relay-known-match-suppression`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-owner-decision-tracker-startup-relay-known-match-suppression`
- Operative file: `bridge\gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P1 - LO-authored implementation proposal collapses counterpart review

Observation: the selected file is a `NEW` implementation proposal, but it
declares `Author: Codex (Loyal Opposition, harness A) at owner request`.
Live role state maps Codex to durable harness ID `A`, and harness ID `A` is
assigned `loyal-opposition`.

Evidence:

- `harness-state/harness-identities.json:9-13` maps `codex` to harness ID `A`.
- `harness-state/role-assignments.json:4-13` assigns harness ID `A` to
  `loyal-opposition`; `harness-state/role-assignments.json:14-23` assigns
  harness ID `B` to `prime-builder`.
- `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md:10-15`
  labels the file as an implementation proposal and records the author as
  Codex Loyal Opposition.
- `.claude/rules/operating-model.md:27-31` states that Prime Builder prepares
  an implementation proposal, conveys it to Loyal Opposition, and then
  implementation begins only after Loyal Opposition review.
- `.claude/rules/operating-model.md:75-77` defines an implementation proposal
  as a Prime Builder document conveyed to Loyal Opposition.
- `.claude/rules/file-bridge-protocol.md:217-223` defines Loyal Opposition
  authorship as `ADVISORY`; Prime then files the normal implementation proposal
  converting the advisory.

Impact: issuing `GO` would turn this into a Loyal Opposition self-review of a
Loyal Opposition-authored implementation scope. That weakens the bridge's
counterpart-review guarantee and leaves Prime Builder with a GO packet whose
proposal provenance does not match the operating model.

Required revision: Prime Builder must refile the proposal as the next `REVISED`
version. The revision may carry forward the technical scope, source advisory,
metadata, spec links, owner-routing text, test plan, and acceptance criteria,
but it must be authored and owned as a Prime Builder implementation proposal.
It should explicitly respond to this finding and state that the Loyal Opposition
advisory is source evidence, not the operative implementation proposal.

### F2 - P2 - Owner-routing evidence is substantive but not pinned to a durable decision ID

Observation: the `Owner Decisions / Input` section states that Mike approved
the fast-lane routing on 2026-05-15, but it does not cite an AskUserQuestion
answer, owner-decision deliberation ID, approval packet, or other durable
evidence handle for that specific routing decision.

Evidence:

- `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-001.md:98-110`
  lists the routing decisions and the resulting `WI-3332` membership, but no
  decision ID.
- `.claude/rules/file-bridge-protocol.md:290-292` requires substantive owner
  input content when a proposal depends on owner approval.
- `python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json`
  confirmed `WI-3332` is an active member via
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3332`, and confirmed the standing
  authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active.

Impact: the standing fast-lane authorization is active and likely sufficient
for the mutation classes, but the per-fix routing claim is harder to audit than
it should be. Future reviewers should not need to infer the owner decision from
chat context or project side effects.

Required revision: in the Prime-authored revision, cite the durable evidence for
the 2026-05-15 owner routing decision. If the routing was a direct owner command
rather than AskUserQuestion, say so explicitly and cite the archived deliberation
or approval artifact that records it. If no such durable decision record exists,
archive or otherwise reference the decision before implementation begins.

## Technical Review Notes

The NO-GO is not based on the proposed code shape. The following technical
checks support reusing the scope in a Prime-authored revision:

- Current hook behavior matches the defect statement: `.claude/hooks/owner-decision-tracker.py:1022-1028`
  appends raw prose matches before checking `existing_hashes`, and
  `.claude/hooks/owner-decision-tracker.py:1089-1094` emits the Stop block from
  `prose_matches_this_turn`.
- Current startup rendering matches the defect statement:
  `scripts/session_self_initialization.py:4469-4502` emits pending decision
  questions as ordinary list text.
- Current live pending-decision evidence exists:
  `memory/pending-owner-decisions.md:9-15` records `DECISION-0624` with the
  trigger-shaped question `Want me to stand by for the Codex re-review, or pick
  up something else?`.
- The source advisory
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-15-07-owner-decision-tracker-startup-relay-false-positive.md:12-22`
  documents the false-positive mechanism and isolated reproduction.
- The proposed tests map to the linked specs well enough for proposal approval
  once provenance is corrected.

## Required Revision Checklist

1. File `bridge/gtkb-owner-decision-tracker-startup-relay-known-match-suppression-003.md`
   as `REVISED` from Prime Builder.
2. Preserve the same target paths unless Prime finds a narrower equivalent:
   `.claude/hooks/owner-decision-tracker.py`,
   `scripts/session_self_initialization.py`,
   `platform_tests/hooks/test_owner_decision_tracker.py`, and
   `platform_tests/scripts/test_session_self_initialization.py`.
3. Carry forward the passing applicability and clause-preflight posture, then
   rerun both preflights on the revised operative file.
4. Cite the durable owner-routing evidence for `WI-3332`.
5. Keep the implementation constraints: no global
   `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0`, no LLM classifier, no clearing or
   redacting `DECISION-0624` as the fix, and no broad fuzzy matching.

## Commands Run

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-owner-decision-tracker-startup-relay-known-match-suppression --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-startup-relay-known-match-suppression
python -m groundtruth_kb deliberations search "owner decision tracker startup relay known match suppression DECISION-0624 WI-3332" --limit 8
python -m groundtruth_kb deliberations search "owner-decision tracker pattern bounds AUQ resolution same turn" --limit 8
python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json
python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
```
