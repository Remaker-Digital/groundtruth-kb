NO-GO

Document: gtkb-role-status-orthogonality-dispatch-scoping
Version: 002
Responds to: bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-31 UTC
Verdict: NO-GO

# Loyal Opposition Verdict - Role/Status Orthogonality Dispatch Model Scoping

## Claim

The current content of `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md` is close to approvable as a governance-review scoping proposal, but the filed `-001` artifact changed in place during this dispatched review. That violates the bridge audit-trail expectation for versioned proposal files. Prime Builder should file the now-corrected content as a new `REVISED` version so the correction is explicit in the bridge chain.

## Applicability Preflight

- packet_hash: `sha256:fd1640afff3a7d14f000eeb94f87beb19e8ebcc9be6e928828ed9444df77dbdc`
- bridge_document_name: `gtkb-role-status-orthogonality-dispatch-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md`
- operative_file: `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-role-status-orthogonality-dispatch-scoping`
- Operative file: `bridge\gtkb-role-status-orthogonality-dispatch-scoping-001.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Review-Session Drift Evidence

During this same dispatched Loyal Opposition review, the first run of the mandatory preflights against the live indexed operative file produced a different packet hash and failed:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-status-orthogonality-dispatch-scoping

packet_hash: sha256:1acf585821c87af6a2e3f68b3de8557d556a2a20e8705fe4d7c6080bf68c5711
preflight_passed: false
missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The first clause preflight in the same review also failed the mandatory gate:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-status-orthogonality-dispatch-scoping

Evidence gaps in must_apply clauses: 1
Blocking gaps (gate-failing): 1

Blocking gap:
ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT
Gap: Evidence missing: Implementation must declare in-root output paths for all generated artifacts; bridge file must reside under E:\GT-KB\bridge\.
```

A later read of the same `bridge/gtkb-role-status-orthogonality-dispatch-scoping-001.md` file showed added `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` linkage text at lines 133-157. The rerun then passed with packet hash `sha256:fd1640afff3a7d14f000eeb94f87beb19e8ebcc9be6e928828ed9444df77dbdc`.

## Prior Deliberations

Searches run:

- `gt deliberations search "Antigravity" --limit 8`
- `gt deliberations search "single-prime-builder" --limit 8`
- `gt deliberations search "role portability" --limit 8`
- targeted `gt deliberations get` checks for `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`, `DELIB-2079`, `DELIB-2080`, and `DELIB-2081`

Relevant records:

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - owner decision adopting role/status orthogonality with single-ACTIVE-per-role dispatch and authorizing this umbrella scoping proposal.
- `DELIB-2079` - Antigravity Integration 3-harness design, including the earlier harness registry and lifecycle-FSM framing.
- `DELIB-2080` - role-portability amendment with the now-superseded single-prime-builder invariant.
- `DELIB-2081` - Antigravity-project authorization context for bridge notifier auto-drain; relevant to the surrounding multi-harness dispatch history.
- `DELIB-2094` - verified bridge thread for `gtkb-harness-role-portability-fr9`; relevant prior implementation history for the single-prime-builder invariant.
- `DELIB-2342` / `DELIB-2344` - prior bridge role-intent sentinel reviews; useful context for avoiding role/dispatch conflation.

## Findings

### F1 - P1 - Filed bridge artifact changed in place during review

Evidence: The same indexed operative file produced two different mandatory preflight packet hashes during this review: initial `sha256:1acf585821c87af6a2e3f68b3de8557d556a2a20e8705fe4d7c6080bf68c5711` with missing required/advisory specs, then current `sha256:fd1640afff3a7d14f000eeb94f87beb19e8ebcc9be6e928828ed9444df77dbdc` with no missing specs. The current file now contains added spec-linkage and in-root evidence at lines 133-157.

Impact: The bridge protocol relies on versioned files as the audit trail. In-place correction of a dispatched `NEW` proposal erases the exact proposal version Loyal Opposition first reviewed and makes the `-001` state non-reproducible from disk. This is especially risky here because the original failure was a mandatory gate failure.

Recommended action: Prime Builder should file the current corrected scoping text as a new `REVISED` bridge version and leave this `NO-GO` as the audit record of the in-place mutation. Future bridge filings should complete preflight corrections before inserting the `NEW` row into `bridge/INDEX.md`, or else file a `REVISED` version after a verdict rather than rewriting a live version.

### F2 - P2 - Slice order is still easy to misread

Evidence: The owner-input section says Slice 1 is the resolver change and subsequent slices handle ADR/GOV/SPEC/DCL updates (lines 60-64). The Requirement Sufficiency and Slice 1 sections correctly state that Slice 2 ADR + DCL must exist before Slice 1 lands (lines 202-212 and 302-304).

Impact: The proposal is substantively recoverable, but the numbering and prose can still push implementers toward starting with resolver code before the requirement artifacts exist. That would contradict the proposal's own requirement-sufficiency declaration.

Recommended action: In the revised version, make the execution order explicit: governance prerequisite first, resolver implementation second. Either renumber the slices or add a compact dependency table that says Slice 2 must be completed before Slice 1 implementation begins.

## Opportunity Radar

Observed pattern: a scoping proposal that lists future implementation paths can trigger mandatory applicability and clause preflights even when the current proposal authorizes only bridge-file scope.

Candidate deterministic replacement: the bridge proposal helper or preflight report could emit a "future path mention" warning distinct from current `target_paths`, while still requiring explicit governing-spec citations when the text names future in-root files.

Recommended surface: `scripts/bridge_applicability_preflight.py` plus the bridge proposal helper template. Residual human judgement: whether a future path mention is merely context or a binding slice plan. No separate advisory file was created in this auto-dispatch turn to keep the work scoped to the selected bridge entry.

## Decision Needed From Owner

None. This is a protocol NO-GO that Prime Builder can correct by refiling the current proposal as a `REVISED` version with the already-added specification linkage and a clearer execution-order statement.
