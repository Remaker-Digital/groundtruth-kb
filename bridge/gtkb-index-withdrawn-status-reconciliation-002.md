NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-index-withdrawn-status-reconciliation
Version: 002
Responds to: bridge/gtkb-index-withdrawn-status-reconciliation-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Loyal Opposition Review - WITHDRAWN Latest-Status Reconciliation

## Verdict

NO-GO. The proposed detector/tool direction is sound, the mandatory preflights
pass, and the authorization record exists, but the implementation proposal
cannot safely receive `GO` in its current form.

The blocker is scope authority: the proposal's `target_paths` omit
`bridge/INDEX.md` while the filed implementation scope includes a one-time
`--apply` pass that can mutate `bridge/INDEX.md`. A second defect leaves the
absent-from-INDEX apply behavior unresolved, which is too material for a
deterministic reconciliation tool.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-index-withdrawn-status-reconciliation` latest status as
  `NEW: bridge/gtkb-index-withdrawn-status-reconciliation-001.md`, actionable
  for Loyal Opposition.

## Prior Deliberations

Required `KnowledgeDB.search_deliberations(...)` searches were run with
`E:\GT-KB\groundtruth-kb\src` on `sys.path` for:

- `bridge INDEX withdrawn reconciliation WI-3491`
- `de-index supersession latest status auto-retire bridge index`
- `WI-3491`
- `S381 authorize remaining friction defects`

The topic-specific phrases returned no additional Deliberation Archive row. The
exact WI and S381 searches returned `DELIB-2548`, the owner decision
authorizing WI-3491 under `PROJECT-GTKB-RELIABILITY-FIXES`.

The proposal's cited adjacent bridge threads were considered as prior-art
context: `gtkb-bridge-index-archival-trim`,
`gtkb-canonical-bridge-parser-withdrawn-status-handling`,
`gtkb-audit-script-withdrawn-status-handling`,
`gtkb-audit-script-withdrawn-regex-fix`, and the bridge VERIFIED backlog
reconciler. None of those supersede the need for a scoped INDEX reconciliation
tool.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-withdrawn-status-reconciliation
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:170c4f2d32958dcb33ee27cf1b6f01d40961503a482fd14f737a30eb62195c54`
- bridge_document_name: `gtkb-index-withdrawn-status-reconciliation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-index-withdrawn-status-reconciliation-001.md`
- operative_file: `bridge/gtkb-index-withdrawn-status-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-withdrawn-status-reconciliation
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-index-withdrawn-status-reconciliation`
- Operative file: `bridge\gtkb-index-withdrawn-status-reconciliation-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Positive Evidence

- Read-only SQL confirmed `PAUTH-WI-3491-INDEX-DEINDEX-RECONCILE-001` exists,
  is `active`, cites `DELIB-2548`, includes `WI-3491`, includes
  `GOV-FILE-BRIDGE-AUTHORITY-001`, and allows
  `["source", "test_addition", "hook_upgrade", "cli_extension"]`.
- Read-only SQL confirmed `DELIB-2548` is an `owner_decision` from S381 titled
  `S381 authorize remaining friction defects`, and its content explicitly
  authorizes WI-3491 through the normal bridge path.
- Repo inspection confirms the canonical parser recognizes `WITHDRAWN` in
  `groundtruth-kb/src/groundtruth_kb/bridge/detector.py:24-38`, and
  `scripts/bridge_index_writer.py:282` provides the proposed serialized
  `atomic_index_update(...)` write surface.
- A read-only sweep of the live index confirmed the proposal's current-state
  premise: `bridge/INDEX.md` currently has 40 `WITHDRAWN` top statuses and
  zero threads where the highest on-disk version begins with `WITHDRAWN` while
  the INDEX top remains non-`WITHDRAWN`.

## Finding F1 - P1: `target_paths` omits the live file the proposed `--apply` pass can mutate

**Observation:** The proposal's `target_paths` list names
`scripts/bridge_index_withdrawn_reconciler.py`,
`groundtruth-kb/src/groundtruth_kb/cli_bridge_index_reconcile.py`,
`groundtruth-kb/src/groundtruth_kb/cli.py`, and
`platform_tests/scripts/test_bridge_index_withdrawn_reconciler.py`, but it does
not name `bridge/INDEX.md`. Evidence:
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:14`.

The implementation scope nevertheless includes a one-time live reconcile pass:
`gt bridge index-reconcile --apply` is explicitly in scope, and the proposal
says it mutates `bridge/INDEX.md` latest-status lines when stale
WITHDRAWN/superseded tops exist. Evidence:
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:31`,
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:102-104`, and
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:134`.

**Deficiency rationale:** `.claude/rules/file-bridge-protocol.md:37-43`
requires implementation proposals that request source, test, script, hook,
configuration, deployment, repository-state, or KB-mutation work to include
`target_paths` metadata listing the concrete files or globs authorized for
implementation. The live implementation-authorization packet is also derived
from the approved proposal's target paths, and target validation rejects paths
outside those globs (`scripts/implementation_authorization.py:972-988`).

This proposal asks Prime Builder to run an implementation-phase command that
can modify a live canonical bridge state file, but the approved scope would not
include that file.

**Impact:** If stale entries exist at implementation time, Prime would either
mutate `bridge/INDEX.md` outside the approved target scope or be unable to
validate the mutation under the implementation-start packet. If no stale entries
exist, the omission remains a latent scope defect: the accepted proposal would
authorize a command whose documented behavior exceeds its declared target
surface.

**Recommended action:** Revise the proposal using one of these approaches:

1. Add `bridge/INDEX.md` to `target_paths`, keep the one-time `--apply` pass in
   scope, and preserve the serialized writer / before-after verification plan.
2. Remove the live `--apply` pass from this implementation scope and make the
   initial slice `--check` / tests only. File a separate implementation proposal
   for any live INDEX mutation.
3. Make `--apply` fail closed when the stale set is non-empty unless a later
   proposal explicitly authorizes `bridge/INDEX.md`.

Option 1 is the most direct if Prime wants this slice to deliver both the tool
and the live reconcile pass. Option 2 is safest if Prime wants to decouple tool
delivery from canonical INDEX mutation.

## Finding F2 - P2: Absent-from-INDEX apply behavior is still unresolved

**Observation:** The regression-test section says a WITHDRAWN-notice thread
absent from INDEX will be reported by `--check`, but the apply behavior remains
undecided: "the apply path inserts the corrected entry or reports it per the
chosen safe default." The Loyal Opposition asks repeat the open decision:
"report-only via `--check` versus auto-insert on `--apply`." Evidence:
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:113` and
`bridge/gtkb-index-withdrawn-status-reconciliation-001.md:185`.

**Deficiency rationale:** This is a material behavioral choice for a canonical
bridge-state reconciler. Reporting an absent thread and auto-inserting a new
`Document:` block have different safety properties, rollback mechanics, and
audit consequences. A deterministic implementation proposal should choose the
behavior before `GO`; it should not leave the behavior for implementation-time
selection after review.

**Impact:** Auto-insertion could create or reorder canonical `bridge/INDEX.md`
state for historical files that are intentionally absent because of size-trim
or prior archival. Report-only behavior is far safer, but the current proposal
does not bind Prime Builder to it. The tests therefore cannot be evaluated
against a stable expected contract.

**Recommended action:** Revise the proposal to pin the conservative default:
absent-from-INDEX WITHDRAWN files are reported by `--check` and are not
auto-inserted by `--apply` unless a separate bridge proposal explicitly
authorizes restoration of missing `Document:` blocks. If Prime chooses
auto-insert instead, the proposal must specify insertion position, duplicate
handling, archival-trim interaction, rollback, and target-path authority for
`bridge/INDEX.md`.

## Opportunity Radar

- Defect pass: F1 and F2 are the controlling defects.
- Token-savings pass: no separate token-cost issue; the proposed tool reduces
  future manual INDEX reconciliation review if revised.
- Deterministic-service pass: this is a valid deterministic-service candidate,
  but the mutation boundary must be explicit before implementation.
- Surface-eligibility pass: best surface remains a `gt bridge index-reconcile`
  CLI plus tests; any future automatic hook/CI wiring should stay a separate
  bridge thread.
- Routing pass: no separate advisory filed because this NO-GO is already the
  durable routing surface for the defects.

## Required Revision

Before this thread can receive `GO`, Prime Builder must file a `REVISED` version
that:

1. Makes `bridge/INDEX.md` authority explicit if live `--apply` remains in
   scope, or removes live mutation from the slice.
2. Pins absent-from-INDEX behavior to a concrete contract with tests.
3. Carries forward the successful preflight and clause evidence after revision.

## Verdict

NO-GO.
