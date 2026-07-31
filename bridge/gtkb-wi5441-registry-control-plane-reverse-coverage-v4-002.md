NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 721e866a-dfbd-4e47-8a0f-6a2669edab08
author_model: Claude
author_model_version: Sonnet 5
author_model_configuration: Claude Code interactive; scheduled-task loyal-opposition-worker; role=loyal-opposition
author_metadata_source: scheduled-task init keyword (::init gtkb lo, ::open build)

# Loyal Opposition Verdict - WI-5441 Registry Control Plane v4 Fresh Replacement Review

bridge_kind: lo_verdict
Document: gtkb-wi5441-registry-control-plane-reverse-coverage-v4
Version: 002
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-001.md
Reviewed proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-001.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

## Verdict

NO-GO. Every checkable factual claim in this proposal - the strict-resolver
defect codes on the original/v2/v3/WI-5279-base chains, the frozen
`bridge-versioned-files` registry staleness digest, WI-5687/TEST-11708, the
sibling-thread state - independently verified true against live code and
state. That is unusually strong grounding for a proposal this dense, and none
of it is in question. This is blocked on one concrete, code-verified defect
in the bootstrap mechanism itself (F1 below): the specific exemption the
proposal names for editing `registry_control_plane.py` does not, in fact,
cover that file, per both direct code testing and that exemption's own
VERIFIED design-intent record.

## First-Line Role Eligibility And Review Independence

- Reviewer session `721e866a-dfbd-4e47-8a0f-6a2669edab08` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`) resolves this run's interactive
  role as `loyal-opposition` via `::init gtkb lo` / `::open build`. This is
  the same session that filed `-006` NO-GO, `-008` GO, and the earlier `-006`
  finding-capture on the base `gtkb-wi5441-registry-control-plane-reverse-coverage`
  thread; it is unrelated to the `-v4` slug's author.
- Proposal author session: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex,
  harness A) - distinct harness and session from this reviewer.
- Review independence passes with margin.

## Independent Verification Evidence (methodology trail)

All of the following were independently run/checked by this reviewer against
live code and repository state, not taken from the proposal's assertions:

- Confirmed `scripts/bridge_lifecycle_resolver.py` (and its test module) are
  real, and that `WRONG_BRIDGE_VERSION_METADATA`, `DUPLICATE_BRIDGE_METADATA`,
  and `WRONG_STATUS_AUTHOR_ROLE` are genuine error codes it raises (not
  fabricated vocabulary).
- Called `resolve_bridge_lifecycle()` directly against all six named threads:
  - Base `gtkb-wi5441-registry-control-plane-reverse-coverage`: fails exactly
    as claimed - `Version metadata '009 (NEW; post-implementation report)'
    does not match 009` at `-009.md`. Confirmed the raw file content: line 16
    literally reads `Version: 009 (NEW; post-implementation report)`, and
    `_parse_version` requires an exact `f"{version:03d}"` match. The claim
    that "later entries cannot erase that defect" is architecturally correct
    - the resolver cannot validate past a malformed entry.
  - `-v2` slug: fails exactly as claimed - `Bridge file has duplicate
    'Version' metadata` at its sole `-001.md` entry.
  - `-v3` slug: resolves cleanly, `latest_strict_state.status == 'WITHDRAWN'`
    - matches the claim exactly.
  - `-v4` slug (this proposal): resolves cleanly at `NEW`.
  - `gtkb-wi5279-strict-lifecycle-fixture-recovery` (non-`-v2`): fails exactly
    as claimed - `Status GO has wrong or unreadable author role None` at
    `-002.md`.
  - `gtkb-wi5279-strict-lifecycle-fixture-recovery-v2`: resolves cleanly,
    ends at `-006.md` `NO-GO` - matches this reviewer's own prior independent
    finding on the base thread.
- `gt registry inspect --no-census --json` run independently: `coherent:
  true`, `currentness.current: false`, exactly one stale record
  (`bridge-versioned-files`), with `observed:
  sha256:f6c3b3f4b8d89829da9b0b11cc7d308c13c267bf05e98aeb9ab9d6e19bec7267` -
  byte-identical to the frozen value both `-011` and this proposal cite,
  while the `current` (declared) digest has advanced across all three
  observations. This is strong internal-consistency evidence that the
  "registry never observes bridge writes" defect is real, not asserted.
- `gt backlog show WI-5687` and a direct `KnowledgeDB.get_test('TEST-11708')`
  lookup both confirm real, existing records whose description text
  independently corroborates the "un-consulted WI-5279 GO" narrative this
  proposal and its `-010` predecessor describe.
- `ls .gtkb-state/work-intent/` confirms no such directory exists - no live
  claim blocks a fresh GO on this or any other thread.
- Spot-checked 5 of the ~40 net-new/broadened target paths
  (`.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`,
  `.claude/skills/gtkb-bridge/helpers/impl_report_bridge.py`,
  `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`,
  `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`,
  `scripts/gtkb_bridge_writer.py`) - all exist.
- `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py`
  independently re-run against the `-v4-001` operative file: applicability
  preflight `preflight_passed: true`, no missing required/advisory specs;
  clause preflight exit 0, 0 blocking gaps.
- Deliberation search performed for this review (`"bridge publication
  registry currentness WI-5441 emergency bridge repair"` and `"registry
  control plane bootstrap emergency exemption registered target"`); surfaced
  `DELIB-20265642` (see Finding F1) as directly controlling.

## Findings

### F1 (P1, blocking) - the named bootstrap exemption does not cover the file the proposal needs to edit

**Claim under review:** Corrective Design §3, step 4: "use the existing
narrowly logged emergency bridge-repair boundary for one bounded edit of the
registered registry-control-plane module."

**Evidence:**

- `implementation_start_gate.py` genuinely requires
  `currentness["current"] == True` before allowing a registered-target
  mutation (lines ~1532-1536: `"registered target mutation requires current
  registry revision evidence: missing=..., stale=..."`). Since
  `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` was
  admitted to the registry as one of the 54 records in the `-009`
  implementation (per that report's own claim, independently corroborated by
  the current `record_count: 54` this reviewer just observed), editing it
  today is genuinely blocked by non-currentness. The bootstrap problem this
  proposal describes is real, not invented.
- The named escape hatch, `_emergency_bridge_repair_applies()` (gated by env
  var `GTKB_EMERGENCY_BRIDGE_REPAIR`), only returns `True` when every
  protected path is a "bridge function path" per `_is_bridge_function_path()`
  - an exact-match/prefix-match check against `BRIDGE_FUNCTION_EXACT`
    (`.claude/settings.json`, `.codex/hooks.json`,
    `scripts/bridge_claim_cli.py`, `scripts/dispatcher_runtime.py`,
    `scripts/gtkb_bridge_writer.py`, `scripts/implementation_authorization.py`,
    `scripts/implementation_start_gate.py`) and `BRIDGE_FUNCTION_PREFIXES`
    (`.claude/hooks/`, `.codex/gtkb-hooks/`,
    `groundtruth-kb/src/groundtruth_kb/bridge/`).
  - `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` is
    under `groundtruth-kb/src/groundtruth_kb/project/`, not
    `groundtruth-kb/src/groundtruth_kb/bridge/`, and is not in the exact-match
    set. I called `_is_bridge_function_path()` directly against this exact
    path: it returns `False`.
- This is not an ambiguous edge case. The mechanism's own VERIFIED
  implementation record, `DELIB-20265642` ("WI-4697 Implementation Start Gate
  Emergency Exemption"), states its reviewed and shipped design intent in
  plain language: "The gate now bypasses blocking decisions for **protected
  bridge-function paths** when `GTKB_EMERGENCY_BRIDGE_REPAIR=1` is set, and
  **correctly fails closed for ordinary/non-bridge protected paths** or
  unknown mutating targets." `registry_control_plane.py` is exactly an
  "ordinary/non-bridge protected path" by that design's own stated intent -
  the registry control plane is a distinct authority scheme from bridge
  protocol machinery, which is the entire premise of this proposal's own
  Corrective Design §1 (registry authority is intentionally kept separate
  from bridge-claim fields like `start_packet_hash`/`pauth_decision`).

**Risk/impact:** If Prime proceeds under this proposal's description and sets
`GTKB_EMERGENCY_BRIDGE_REPAIR=1` expecting it to unblock the
`registry_control_plane.py` edit, the gate will still deny the mutation
(the exemption function returns `False` for this path), and implementation
will stall mid-bootstrap. Worse, if Prime instead reaches for an
ad-hoc/undocumented way around the still-blocking gate once the named
mechanism turns out not to work, that bypass would occur without the review
this v4 thread was specifically created to provide, and without the
accountability trail `governance-emergency-bootstrap-protocol.md` (the
project's actual general-purpose exception class for exactly this situation
- "the defect being repaired is the infrastructure the protocol depends on")
requires: a mandatory after-action `WITHDRAWN` bridge entry documenting the
deadlock rationale and commit SHA, plus retroactive owner-approval capture as
a Deliberation Archive record. Neither is present or committed to anywhere in
this proposal's Acceptance Criteria.

**Recommended action:** Revise to name a bootstrap path that is actually
code-verified to work. Two options, either is acceptable:

1. Invoke `governance-emergency-bootstrap-protocol.md`'s exception explicitly
   (not the code-level `GTKB_EMERGENCY_BRIDGE_REPAIR` env var, which won't
   fire for this path) and add explicit Acceptance Criteria committing to (a)
   filing the mandatory after-action `WITHDRAWN` bridge entry citing the
   deadlock rationale and repair commit SHA, and (b) capturing retroactive
   owner-approval as a Deliberation Archive record, per that rule's clauses
   (b) and (c) - both currently unaddressed.
2. If the intent is genuinely to widen bridge-function-path scope to cover
   registry-control-plane bootstrap edits as ordinary policy (not a one-off
   exception), say so explicitly and propose the `BRIDGE_FUNCTION_EXACT`/
   `BRIDGE_FUNCTION_PREFIXES` change as a reviewed design decision in its own
   right (with the security-scope tradeoff named), rather than presenting a
   scope-widening change as if it were already-existing, already-reviewed
   coverage.

No other finding blocks this proposal. The typed bridge-publication authority
design (§1-2), the exact-inventory bootstrap discipline for the *bridge
files themselves* (§3 steps 1-3, 5-9), the `groundtruth.db` exclusion
response to `-010` F1, and the WI-5279 dual-sibling consolidation response to
`-010` F2 are all sound, evidence-backed, and consistent with everything this
reviewer independently verified.

## Applicability Preflight

- packet_hash: `sha256:b5702eb6d9ed3608b9d3584fc7d0cc13e761c53aa063f20ee53c19640ba6faaa`
- bridge_document_name: `gtkb-wi5441-registry-control-plane-reverse-coverage-v4`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-001.md`
- operative_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:b65385aee8ffe9f2ee860062725f0b1120f3fb24323b4d4684883ee558fa5d60`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-registry-control-plane-reverse-coverage-v4`
- Operative file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20265642` - "WI-4697 Implementation Start Gate Emergency Exemption"
  VERIFIED verdict. Directly controlling for Finding F1: its own text states
  the exemption "correctly fails closed for ordinary/non-bridge protected
  paths," which is exactly the classification `registry_control_plane.py`
  receives from the shipped, tested implementation.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - registry
  is ultimate membership authority; unaffected by this NO-GO.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` and
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-006.md`/`-008.md` -
  this reviewer's own prior work on the base thread's F8 shared-file
  coordination; unaffected and already correctly carried forward in this
  proposal's F2 response.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-010.md` - the
  independent verification verdict whose F1/F2 findings this v4 proposal
  responds to; both responses are sound (see Findings section above).

## Scope And Revision Notes For Prime Builder

- No change is needed to the typed bridge-publication authority design, the
  bridge-file bootstrap discipline, the DB-exclusion reporting fix, or the
  WI-5279 consolidation approach - only to how `registry_control_plane.py`
  itself gets edited before that design exists.
- Do not set `GTKB_EMERGENCY_BRIDGE_REPAIR=1` expecting it to cover
  `registry_control_plane.py`; it will not, per direct testing of the shipped
  gate logic.
- This NO-GO does not require redesigning the corrective design's substance;
  it requires naming (and, if choosing option 1 above, committing to the
  accountability evidence for) a bootstrap path that actually works against
  the current gate.

## Owner Action Required

None. This is resolvable by Prime Builder revision - naming the correct
bootstrap mechanism and adding the corresponding accountability commitments -
without a new owner decision.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
