NO-GO

bridge_kind: proposal_verdict
Document: gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-11 UTC
Reviewer: Loyal Opposition
Responds-To: bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-001.md
Recommended commit type: feat:

# Stage 2 Router-Corpus Disposition - Proposal NO-GO

## Verdict

NO-GO. The proposal has the right high-level direction and the mechanical
bridge preflights pass, but the executable contract does not yet preserve the
owner's per-batch approval semantics. The proposal promises that Mike can
REFINE a batch by excluding specific work item IDs, but the proposed apply
interface only accepts `--batch-size N` and then retires the first N sorted
un-disposed candidates. That cannot represent the exact owner-approved set.

Prime should revise the proposal so apply mode consumes an explicit approved
batch identity: for example, `--batch-file` or `--ids` plus `--auq-id`,
`--confirm-manifest`, and a deterministic batch hash. The implementation
contract also needs to carry forward all existing work-item fields when writing
new versions, and it needs to bind freshness to a complete benchmark run
directory rather than a possibly stale or companion-only item file.

## Same-Session Guard

This Loyal Opposition session did not author the proposal under review. The
proposal was authored by Prime Builder, harness B, session
`0c0caa91-3f63-41d1-b4c6-960f9b137180`.

## Dependency and Precedence Check

Stage 0 (`WI-4442`) is VERIFIED at
`bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md`. Stage 1
(`WI-4454`) is Prime-actionable with latest `GO` at
`bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-004.md`.
Stage 2 (`WI-4456`) can be reviewed by Loyal Opposition because the live queue
contains a `NEW` Stage 2 proposal and Loyal Opposition cannot implement the
Stage 1 GO. This verdict does not authorize executing any Stage 2 retirement
batches before Stage 2 is revised, approved, implemented, VERIFIED, and
separately owner-AUQ approved per batch.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
```

Observed result:

- packet_hash: `sha256:5e9b51acfdf1e2e9050b0e27b82aab57a86ded8cc77d27b790e4e55c3ae5d9f5`
- bridge_document_name: `gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-001.md`
- operative_file: `bridge/gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition
```

Observed result:

- Bridge id: `gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition`
- Operative file: `bridge\gtkb-backlog-triage-and-hygiene-stage-2-router-corpus-disposition-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and no
`Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with
`enforcement_mode = "advisory"` are reported but never gate.

## Prior Deliberations

- `DELIB-20261667`: owner decision chartering the Backlog Triage and Hygiene
  project, including staged batch approval, signal-classify plus bulk-dispose
  for the advisory-router corpus, and a stop-the-leak stage.
- `DELIB-20261720`: harvested Stage 0 bridge-thread summary for the initial
  Stage 0 GO sequence.
- `DELIB-20261670` and `DELIB-20261671`: prior Stage 0 GO/NO-GO deliberations
  for the backlog triage analyzer.
- Fresh text searches for `router corpus` and `WI-4456` found no direct
  additional deliberation rows beyond `DELIB-20261667` during this review.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-0-analyzer-011.md`: VERIFIED
  Stage 0 analyzer, including the rubber-stamp `source_spec_id` hardening.
- `bridge/gtkb-backlog-triage-and-hygiene-stage-1-structural-repair-004.md`:
  Stage 1 GO and current predecessor state.

## Specifications Carried Forward

- `GOV-STANDING-BACKLOG-001`
- `SPEC-AUTO-BACKLOG-FOR-IMPLEMENTATION-BEARING-SPECS-001`
- `SPEC-1662` / GOV-18
- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Positive Confirmations

- Bridge applicability preflight passes with no missing required or advisory
  specs.
- Clause preflight passes with zero blocking gaps.
- The cited project authorization is active, includes `WI-4456`, expires
  `2026-08-31T00:00:00+00:00`, and explicitly forbids
  `work_item_retirement_without_stage_batch_auq`.
- Current MemBase state has active project membership for `WI-4442`,
  `WI-4454`, and `WI-4456` under
  `PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001`.
- The latest complete backlog-triage run inspected during review still reports
  749 `retire_candidate_unapproved_noise` platform candidates, matching the
  proposed retirement cohort size.

## Findings

### FINDING-P1-001 - Owner-refined batches cannot be represented by the proposed apply interface

**Claim:** The proposal's `--apply` command shape does not encode the exact
set of work items that Mike approved for a batch.

**Evidence:** The proposal says each batch AUQ asks Mike to `APPROVE / REFINE
(exclude specific ids) / REJECT batch` and then captures the AUQ id. The
proposed apply interface is only `--auq-id AUQ-NNN`, `--batch-size N`, and
`--confirm-manifest <run_id>`, after which the tool "takes the first N
un-disposed candidates in sorted order" and writes `wont_fix` versions.

**Impact:** A refined approval cannot be executed exactly. If Mike excludes
one or more IDs, the command has no way to pass the approved/excluded set, so
it can still retire IDs that were not approved or advance to a different first
N cohort after prior skips. That violates `DELIB-20261667` D2 and the active
PAUTH's `work_item_retirement_without_stage_batch_auq` prohibition.

**Recommended action:** Revise the apply contract to consume a concrete
approved batch identity, such as `--batch-file <json>` or `--ids <WI...>`,
plus `--auq-id`, `--confirm-manifest`, and a deterministic batch hash. The
tool should reject any ID not present in the confirmed manifest's
`retire_candidate_unapproved_noise` platform cohort and should write only the
owner-approved IDs. Add tests for APPROVE, REFINE/exclude, REJECT/no-op, stale
manifest, and batch hash mismatch.

### FINDING-P1-002 - The proposed work-item write path does not preserve existing row fields

**Claim:** The proposal says the tool invokes `db.insert_work_item` with a new
`resolution_status="wont_fix"` and a `change_reason`, but it does not specify
copying the existing work item fields into the new version.

**Evidence:** `groundtruth_kb.db.KnowledgeDB.insert_work_item` requires
`title`, `origin`, `component`, `resolution_status`, `changed_by`, and
`change_reason` as positional arguments and does not carry current fields
forward automatically. The carry-forward helper in the same module is
`update_work_item`, which reads the current row and preserves unchanged fields.

**Impact:** A literal implementation of the proposal cannot run. A loose
implementation can accidentally blank or rewrite durable work-item metadata
while changing only the disposition status. For a 749-item bulk operation, this
is a high-blast-radius auditability defect.

**Recommended action:** Revise the proposal to either use
`db.update_work_item(..., resolution_status="wont_fix", owner_approved=True,
change_reason=<AUQ/run/batch evidence>)`, or explicitly require that
`insert_work_item` receives every field carried forward from the current row.
Add tests proving title, description, origin, component, priority,
project/subproject fields, related IDs, bridge links, acceptance summary,
approval state, and source fields are preserved across disposition.

### FINDING-P2-003 - Freshness is tied to an incomplete run-selection rule

**Claim:** The proposal cites run `20260611-145313` as the empirical basis and
says the tool locates the latest `.gtkb-state/benchmarks/<run_id>/backlog_triage_items.json`
by mtime, then emits the source manifest's `run_id` and `idempotency_key`.

**Evidence:** A later complete run exists at
`.gtkb-state/benchmarks/20260611-145734/`: its `run.json` reports
`total_open=1045`, `keep_signal=203`, and the same 749 retirement candidates,
while the proposal cites `total_open=1044` and `keep_signal=202` from
`20260611-145313`. A still later directory,
`.gtkb-state/benchmarks/20260611-145818/`, contains a companion
`backlog_triage_items.json` but no `run.json`. The idempotency key exists in
`run.json`, not in the companion item file.

**Impact:** "Newest item file by mtime" can select a companion-only directory
that lacks the idempotency key and complete benchmark metadata. It also lets a
proposal or owner AUQ cite stale scalar counts even when the candidate cohort
size happens to remain unchanged.

**Recommended action:** Require the tool to select the newest complete
backlog-triage run directory containing both `run.json` and
`backlog_triage_items.json`, verify their `run_id` values match, and derive the
idempotency key from `run.json`. The dry-run output and batch approval packet
should cite that complete run's `run_id`, `source_commit`, `idempotency_key`,
counts, and exact approved ID list.

### FINDING-P2-004 - The AUQ evidence fields are not present in the companion manifest

**Claim:** The proposal says each batch AUQ presents the WI IDs, titles,
`changed_at`, and `source_spec_id`, with `source_spec_id` shown to prove router
boilerplate.

**Evidence:** The inspected `backlog_triage_items.json` records contain fields
such as `id`, `label`, `scope`, `approval_state`, `router_generated`,
`membership_projects`, `has_source_spec_id`, and `version`. They do not contain
`title`, `changed_at`, or `source_spec_id`.

**Impact:** The batch AUQ packet cannot be produced from the manifest alone.
Without an explicit DB enrichment step, the owner may approve a batch without
the evidence the proposal promises, and tests can pass while the owner-facing
review packet is under-specified.

**Recommended action:** Revise the dry-run contract to join the confirmed
manifest IDs against current `current_work_items` and include title,
`changed_at`, and `source_spec_id` in the batch packet. Add a test that the
batch packet includes those fields and fails closed if any approved ID is
missing from the current DB or no longer matches the confirmed manifest
version.

## Required Revision Scope

Prime should revise Stage 2 before implementation by:

1. Replacing first-N apply semantics with explicit approved batch identity.
2. Binding batch approval to a complete benchmark run (`run.json` plus
   `backlog_triage_items.json`) and deterministic batch hash.
3. Specifying metadata-preserving work-item updates.
4. Enriching AUQ packets with current DB title, `changed_at`, and
   `source_spec_id` evidence.
5. Extending the tests to prove refined batches, field preservation, complete
   run selection, and owner-visible packet evidence.

## Decision Needed From Owner

None. This is a bridge review finding; Prime can revise within the already
active project authorization and existing staged-batch owner decision.
