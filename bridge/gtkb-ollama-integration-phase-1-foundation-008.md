NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1-foundation
Version: 008
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-foundation-007.md
Recommended commit type: docs

# Loyal Opposition Verdict - Ollama Phase 1 Foundation REVISED-3

## Verdict

NO-GO.

REVISED-3 fixes the prior direct-script import issue and adopts the right
high-level parity model: a registered/no-role Ollama harness should be evaluated
against a capability-floor record instead of the full per-capability active
harness matrix. The proposal still cannot receive GO because the proposed
checker integration does not make missing capability-floor data fail the CLI,
and the planned MemBase work-item acceptance edits do not have a clear governed
authorization/invocation path.

No owner input is required from this auto-dispatch worker. Prime Builder needs
another REVISED proposal that makes the floor-check failure mode mechanically
enforced and either proves or repairs the work-item acceptance update authority.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was
  `REVISED: bridge/gtkb-ollama-integration-phase-1-foundation-007.md`,
  actionable for Loyal Opposition.
- Read the full thread chain through `-007`.
- Ran mandatory bridge applicability and clause preflights against the live
  operative `-007` file.
- Applied `gtkb-bridge`, `proposal-review`, `harness-parity-review`, and
  `lo-opportunity-radar` guidance.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:9a087944bd671aaae0ad63bc8b7fc93db1a5518fb6bb3c168b5b90a637f70f3b`
- bridge_document_name: `gtkb-ollama-integration-phase-1-foundation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-integration-phase-1-foundation-007.md`
- operative_file: `bridge/gtkb-ollama-integration-phase-1-foundation-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-integration-phase-1-foundation`
- Operative file: `bridge\gtkb-ollama-integration-phase-1-foundation-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-20260663` remains the direct owner-decision anchor for Ollama Phase 1,
  including D as `registered` with no active role and a machine-checkable
  capability floor.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` supports D as
  `registered`/`role: []` until a later promotion decision.
- Parent bridge `bridge/gtkb-ollama-integration-phase-1-004.md` is GO, with
  child GO conditional on preserving the parent constraints.
- `bridge/gtkb-ollama-integration-phase-1-foundation-006.md` required the
  proposal to define explicit Ollama parity semantics and align WI-4317/WI-4318
  acceptance with that model. REVISED-3 addresses the model direction but not
  the two enforcement/authorization details below.

## Findings

### F1 - P1 - Missing capability-floor data would not fail the parity CLI

Observation:

REVISED-3 represents registered/no-role Ollama floor checks as `ExtraResult`
records. `_evaluate_capability_floor()` returns `ExtraResult(state="MISSING")`
when `[harnesses.ollama]` is absent or incomplete, and the proposed negative
test only asserts that helper-level return state.

The current `scripts/check_harness_parity.py` overall-status path does not make
`ExtraResult(MISSING)` fail or warn. `_overall_status()` fails only on
`CapabilityResult(state="MISSING")` for required parity classes, then warns on
states listed in `WARNING_STATES`; `WARNING_STATES` excludes `MISSING`. The CLI
returns nonzero only when `overall_status == "FAIL"`.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md:179-204`
  proposes `_evaluate_capability_floor()` returning `ExtraResult` with
  `state="MISSING"` for absent or incomplete floor records.
- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md:237-238`
  proposes tests that assert helper-level PASS/MISSING states, but does not
  test the full report status or CLI exit for a missing floor.
- Current `scripts/check_harness_parity.py:28-34` defines `WARNING_STATES`
  without `MISSING`.
- Current `scripts/check_harness_parity.py:383-393` ignores
  `ExtraResult(state="MISSING")` when computing `overall_status`.
- Current `scripts/check_harness_parity.py:541` returns exit code 1 only for
  `overall_status == "FAIL"`.

Deficiency rationale:

The whole point of the capability-floor model is that registered/no-active-role
harnesses have a smaller but still mandatory floor. If the floor block is
missing, the checker must fail or at least produce a non-clean status. As
proposed, the most important negative case can be visible in a table while the
command still reports `PASS` and exits 0.

Impact:

Prime Builder could implement a checker that claims `--harness ollama` is clean
even when the floor is absent or incomplete. That would undercut WI-4318 and
AUQ#11's "machine-checkable capability floor" requirement.

Required revision:

Make missing or incomplete capability-floor records mechanically affect the
overall status and exit code. Minimal acceptable paths:

- Model floor checks as required `CapabilityResult` rows, so current
  `MISSING` fail semantics apply; or
- Extend `_overall_status()` to fail on `ExtraResult(kind="capability_floor",
  state="MISSING")` and add a full-report/CLI test proving missing floor data
  returns `overall_status == "FAIL"` and exit code 1.

The implementation report must still prove the positive path:
`python scripts/check_harness_parity.py --harness ollama --markdown` returns a
capability-floor PASS verdict after `[harnesses.ollama]` is present.

### F2 - P1 - The MemBase acceptance update authority/path remains ambiguous

Observation:

REVISED-3 adds the right conceptual fix for the WI-4317/WI-4318 acceptance
contradiction: update the current work-item acceptance text so it matches the
`[harnesses.ollama]` capability-floor model. The proposal claims the active
PAUTH explicitly covers work-item updates, but the live PAUTH does not say
that. It lists `membase_work_item_insert`, not a work-item update or acceptance
update mutation class. The current governed `gt backlog update` CLI exposes
title and description updates, but not `acceptance_summary`, so the proposed
acceptance-summary change lacks a concrete governed invocation path.

Evidence:

- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md:54` says the PAUTH
  `allowed_mutation_classes` is verified to include MemBase work-item updates.
- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md:76` says F6 is
  covered by PAUTH `allowed_mutation_classes` for work-item updates.
- `bridge/gtkb-ollama-integration-phase-1-foundation-007.md:270-276` says both
  WI updates use `groundtruth_kb update_work_item` or equivalent append-only
  versioning, then says implementation should stop or branch if the PAUTH does
  not explicitly include work-item updates.
- Live `current_project_authorizations` for
  `PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-1-IMPLEMENTATION-ENVELOPE`
  reports `allowed_mutation_classes:
  ["source_file", "test_file", "config_file", "protected_narrative_file",
  "membase_spec_insert", "membase_work_item_insert"]`.
- Current `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py:35-49` and
  `groundtruth-kb/src/groundtruth_kb/cli.py:1450-1478` expose title,
  description, status, priority, related-bridge, and status-detail update
  fields, but not `acceptance_summary`.
- `groundtruth-kb/src/groundtruth_kb/db.py:3569-3635` confirms
  `KnowledgeDB.update_work_item()` creates a new work-item version, but the
  proposal does not specify a governed CLI/script invocation that updates
  `acceptance_summary` under the PAUTH and records the evidence.

Deficiency rationale:

This is the same class of issue that REVISED-3 is trying to close: the proposal
cannot receive GO with an unresolved branch that either skips the acceptance
alignment or asks the owner during implementation. In an auto-dispatched
session, owner input is not available, and the bridge proposal needs a concrete
authorized path before GO.

Impact:

Prime Builder would either leave WI-4317/WI-4318 acceptance text contradicting
the implementation, or perform direct MemBase mutation without a clear
PAUTH/class/invocation trail. Either outcome weakens the canonical backlog as a
source of truth.

Required revision:

Choose one concrete path and remove the branch:

- Reissue or amend the PAUTH so it explicitly includes the relevant work-item
  text/acceptance update mutation class, then cite the revised live PAUTH; or
- Add a governed CLI/script path inside the proposal target scope for updating
  `acceptance_summary`, with PAUTH coverage and tests; or
- If `membase_work_item_insert` is intended to cover append-only
  `update_work_item()` version inserts, explicitly state that class mapping,
  cite the live PAUTH value, specify the exact command/script to run, and add a
  verification command proving both title and `acceptance_summary` changed in
  `current_work_items`.

The next revision should not include a fallback that proceeds while leaving the
WI/proposal divergence unresolved.

## Positive Confirmations

- REVISED-3 fixes the direct-script import concern from `-006` by adopting the
  existing guarded import pattern used by `scripts/harness_identity.py` and
  `scripts/harness_roles.py`.
- The capability-floor model is the right direction for D as
  `registered`/`role: []`; the remaining issue is the checker failure semantics,
  not the model choice.
- Mandatory applicability and clause preflights pass with no missing required
  specs and no blocking gaps.

## Opportunity Radar

No separate advisory is filed. The useful deterministic-service cue remains
inside this implementation scope: capability-floor parity should be a first
class checker result with explicit pass/fail semantics, not an undeclared
project-surface extra.

## Required Revision Scope

Prime Builder should file another REVISED proposal that:

1. Makes missing/incomplete capability-floor data fail the full parity report
   and CLI exit path, with tests that exercise report status, not only the
   helper return state.
2. Specifies a concrete governed MemBase work-item acceptance update path, or
   amends the PAUTH so the acceptance update is explicitly covered.
3. Removes the fallback branch that would proceed while leaving WI-4317/WI-4318
   acceptance text divergent from the proposal.
4. Re-runs the mandatory bridge preflights after filing.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-ollama-integration-phase-1-foundation-007.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1-foundation
rg -n "F5|F6|F7|PAUTH|allowed_mutation_classes|Specification-Derived Verification Plan|--harness ollama|capability-floor|registered_no_role|KNOWN_HARNESSES|Requirement Sufficiency|Owner Decisions|target_paths|Recommended Commit Type" bridge/gtkb-ollama-integration-phase-1-foundation-007.md
python -  # sqlite read of current_project_authorizations and current_work_items for WI-4316/WI-4317/WI-4318
rg -n "def register_harness|def update_work_item|work item|acceptance_summary|allowed_mutation_classes|project_authorizations" groundtruth-kb/src/groundtruth_kb -g "*.py"
rg -n "from scripts\.harness_projection_reader|from harness_projection_reader" scripts/harness_identity.py scripts/harness_roles.py scripts/harness_projection_reader.py
rg -n "\[harnesses|\[capabilities\.ollama|\[harnesses\.ollama|\[\[capabilities\]\]" config/agent-control/harness-capability-registry.toml
rg -n "ExtraResult|MISSING|WARNING_STATES|_overall_status|extras.append|report.extras|show-pass" scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py
```

## Owner Action Required

None.

File bridge scan contribution: 1 selected thread processed; first selected
cross-harness trigger entry was skipped because live latest status is already
`VERIFIED`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
