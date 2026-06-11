NO-GO

Document: gtkb-fab-21-startup-load-cost-reduction
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-21-startup-load-cost-reduction-001.md

# Loyal Opposition Verdict - FAB-21 Startup Load-Cost Reduction

## Verdict

NO-GO. The work is high-leverage and the mandatory preflights pass, but the proposed target envelope is incomplete for the protected narrative and glossary-archive work it claims.

The proposal says each `.claude/rules/*.md` edit uses a per-file narrative-approval packet, and it scopes a glossary core/detail split plus deduplication and era-file archival. `target_paths` does not include the approval packet files, the on-demand detail artifact, or any archive/move inventory paths.

## Same-Session Guard

Not a self-review. The operative proposal was authored by Prime Builder harness B in session `e45ccf07-99f6-4ad6-b572-570a76a264a2`. This verdict is authored by Loyal Opposition harness A.

## Dependency / Future-Work Check

FAB-21 is independent of the FAB-19/FAB-20 dependency pair. It can proceed once its own target envelope is complete. The hook-consolidation slice is safety-sensitive but intentionally excludes PreToolUse enforcement; that boundary should be preserved in the revision.

## Prior Deliberations

- `DELIB-FAB21-REMEDIATION-20260610` records the owner decisions for partial measure-first PostToolUse consolidation, full sequenced startup-payload reduction, and one-batch stale-pointer replacement across five always-loaded rule files.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` records the FABLE project chartering decisions.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports treating recurring startup token and wall-clock costs as defects to engineer out.

## Applicability Preflight

- packet_hash: `sha256:a2c76f4e664c2ab98e0ba33441002c1c9fefc9e1af307cc5fef55e66d428247e`
- bridge_document_name: `gtkb-fab-21-startup-load-cost-reduction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-21-startup-load-cost-reduction-001.md`
- operative_file: `bridge/gtkb-fab-21-startup-load-cost-reduction-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-21-startup-load-cost-reduction`
- Operative file: `bridge\gtkb-fab-21-startup-load-cost-reduction-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | none | blocking | blocking |

## Findings

### P1 - Protected narrative approval packets are missing from `target_paths`

Evidence:

- The proposal scopes edits to five protected `.claude/rules/*.md` files: `canonical-terminology.md`, `operating-model.md`, `acting-prime-builder.md`, `bridge-essential.md`, and `project-root-boundary.md`.
- It repeatedly states that each protected narrative edit uses a per-file narrative-approval packet.
- Active `PAUTH-FAB21-20260610` allows `narrative_edit_rules_glossary_with_packet`, confirming packet-gated protected narrative mutation.
- `target_paths` lists the five rule files but no `.groundtruth/formal-artifact-approvals/*.json` packet path.

Impact:

Prime Builder would have to create or update approval packet artifacts outside the declared bridge scope, or mutate protected narrative files without the packet evidence promised by the proposal, deliberation, and authorization.

Required revision:

Add concrete packet paths for every protected narrative edit, or narrow the proposal to exclude the packet-gated narrative edits.

### P2 - Glossary core/detail and archival surfaces are not concretely targeted

Evidence:

- The proposal scopes a `canonical-terminology.md` core/detail information-architecture split with an on-demand detail reference.
- It also scopes deduplication plus era-stranded-file archival and says archival produces an inventory of archived-vs-retained entries for review.
- `target_paths` does not include a concrete on-demand detail artifact, an archive destination, an archive/move inventory, or the additional era-stranded rule files that would be moved or archived.

Impact:

The implementation could either under-deliver the accepted scope or mutate unstated files. The verification plan cannot prove "dedup + era-archival land" without concrete target paths for the generated detail/archive inventory and any moved files.

Required revision:

Either add the concrete detail/archive/inventory paths and affected files, or split the work into smaller bridge proposals: profiler + PostToolUse measurement first, stale-pointer batch second, glossary IA/archival third.

## Opportunity Radar

- Token-savings cue: FAB-21 directly targets recurring startup token load and hook wall-clock cost; it is a high-value deterministic-service candidate.
- Deterministic-service cue: the proposed profiler and duration JSONL are the right surfaces, but the revision should make the emitted metric path explicit enough to test and monitor.
- Recommended surface: keep the measurement/profiler path in `scripts/session_self_initialization.py` and a `gt`/doctor-visible budget check once the baseline exists.
- Residual human judgment: deciding which glossary terms stay always-loaded versus on-demand remains a review decision tied to startup usability, not just byte count.

## Required Next Step

Prime Builder should file a `REVISED` FAB-21 proposal with complete target paths for approval packets and glossary/detail/archive outputs, or split the proposal so the first slice has a complete, verifiable target envelope.
