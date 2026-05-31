NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-s374-polluted-delib-2514-2520-governed-retraction
Version: 002
Reviewed: 2026-05-30
Reviewer: Codex / Loyal Opposition / harness A
Reviewed file: bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md

# Loyal Opposition Review - S374 Governed Retraction of Polluted DELIB-2514..2520

## Verdict

NO-GO. The contamination evidence and seven-row scope are coherent enough to keep this remediation moving, but the current proposal cannot receive GO because Prime Builder would not be able to create a valid implementation-start authorization packet from it. Revise and resubmit.

## Applicability Preflight

- packet_hash: `sha256:c968144d63c4baf288ab088708a57a516c4724b76b5d7e3a8c76af49fc5ce1f7`
- bridge_document_name: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md`
- operative_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- Operative file: `bridge\gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate when evidence is absent and no owner-waiver line is cited. No such blocking gap was found here.

## Prior Deliberations And Evidence

- `memory/pending-owner-decisions.md` records `DECISION-0834` authorizing "Governed retraction: new DELIB versions + per-record approval packets" for the originally observed DELIB-2511..2520 contamination scope.
- `memory/pending-owner-decisions.md` records `DECISION-0842` selecting the S374 retraction follow-on workflow.
- `memory/pending-owner-decisions.md` records `DECISION-0843` narrowing the work to DELIB-2514..2520 and preserving DELIB-2511..2513.
- Live MemBase query evidence confirms DELIB-2511..2513 have distinct descriptive `source_ref` values and substantive summaries, while DELIB-2514..2520 are v1 rows with `source_ref = DECISION-0001` and fixture-shaped content.
- `platform_tests/owner_decision/test_auto_archive.py` defines `_in_scope_decision()` with `decision_id="DECISION-0001"` and the same Track B fixture body used by DELIB-2514.
- `bridge/gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-014.md` lines 185-187 accepted exactly seven `source_ref=DECISION-0001` rows as deferred future remediation, not authorization inside the Slice 4 implementation thread.

## Findings

### F1 - P1 - Proposal Target Paths Do Not Parse For The Implementation-Start Gate

Observation: The proposal lists paths under `## Target Paths`, with prose annotations. The implementation-start gate does not parse that heading. Current `scripts/implementation_authorization.py` accepts `target_paths: [...]`, `## Files Expected To Change`, or `## target_paths`, and raises `Approved proposal is missing concrete target_paths or Files Expected To Change` otherwise. A direct parser check against the reviewed file returned that exact error.

Evidence:
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md` lines 114-126 use `## Target Paths`.
- `scripts/implementation_authorization.py` lines 455-497 define the accepted target path forms and the failure condition.
- Direct parser check: `extract_target_paths: AuthorizationError: Approved proposal is missing concrete target_paths or Files Expected To Change`.

Impact: If Loyal Opposition issued GO, Prime Builder would fail at `implementation_authorization.py begin` before any protected mutation. That turns GO into a non-executable approval and recreates the same target-path syntax class already caught in the parent Slice 4 thread.

Recommended action: Revise the proposal to include a machine-readable path declaration, preferably near the top:

```text
target_paths: [".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2515-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2516-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2517-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2518-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2519-v2.json", ".groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2520-v2.json", "groundtruth.db", "memory/MEMORY.md", "bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-*.md", "bridge/INDEX.md"]
```

Keep the explanatory `## Target Paths` section if useful, but the machine-readable declaration must exist.

### F2 - P1 - Proposed Implementation-Start Command Uses The Verdict File Name Instead Of The Bridge Document Name

Observation: Step 1 instructs Prime Builder to run `python scripts/implementation_authorization.py begin --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction-002`. The implementation authorization script looks up a `Document:` entry in `bridge/INDEX.md` by bridge id. The document id is `gtkb-s374-polluted-delib-2514-2520-governed-retraction`, not the expected GO file suffix.

Evidence:
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md` line 70 gives the versioned `-002` command.
- `scripts/implementation_authorization.py` lines 721-722 call `bridge_entry(project_root, bridge_id)` and then resolve approved proposal/GO files from that document entry.
- Direct command check: `python scripts/implementation_authorization.py begin --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction-002` returned `Bridge document not found in INDEX: gtkb-s374-polluted-delib-2514-2520-governed-retraction-002`.

Impact: The first implementation step is guaranteed to fail as written. Worse, a future implementer might try to work around the failure manually instead of using the live latest-GO authorization packet.

Recommended action: Revise Step 1 to:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction
```

The approval packet `source_ref` fields may still cite the actual GO verdict file path once it exists.

### F3 - P1 - Implementation Proposal Is Missing Project-Linkage Metadata

Observation: The filed document declares bridge kind value `implementation_proposal` but has no `Project Authorization:`, `Project:`, or `Work Item:` metadata lines. The bridge-compliance gate's project-linkage gate treats non-exempt NEW/REVISED implementation proposals as requiring all three lines; only `spec_intake`, `governance_review`, and `loyal_opposition_advisory` are exempt bridge kinds.

Evidence:
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md` line 3 declares bridge kind value `implementation_proposal`.
- Direct metadata check returned `metadata_exempt: False` and missing `Project Authorization:`, `Project:`, and `Work Item:`.
- `.claude/hooks/bridge-compliance-gate.py` lines 128-143 define the project-linkage metadata gate and exempt set.
- `.claude/hooks/bridge-compliance-gate.py` lines 868-878 hard-block missing project-linkage metadata for implementation bridge proposals.

Impact: The proposal has no machine-readable backlink to the project/work authorization envelope that should scope the MemBase mutation. That weakens implementation provenance and bypasses the live work-item/project membership check that exists to prevent unhomed implementation work.

Recommended action: Add the three metadata lines near the top of the revised proposal and ensure they resolve to live MemBase project membership and an active, unexpired authorization. If this is intentionally not project-scoped implementation work, reclassify the thread as an exempt `bridge_kind: governance_review` and remove implementation-start semantics; otherwise keep it as implementation proposal and provide the metadata.

### F4 - P2 - Scope-Narrowing Owner Decision Should Be Cited By Exact ID

Observation: The proposal describes the scope-narrowing authority as "S374 scope-narrowing AUQ" and says the sequential `DECISION-NNNN` id is next-allocated after `DECISION-0842`. The live record is already present as `DECISION-0843`.

Evidence:
- `memory/pending-owner-decisions.md` lines 9125-9137 record `DECISION-0842`.
- `memory/pending-owner-decisions.md` lines 9139-9151 record `DECISION-0843`, the exact narrowed-scope approval.
- `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-001.md` lines 58-64 use the placeholder-style "S374 scope-narrowing AUQ" reference instead of the exact id.

Impact: Formal-artifact approval packets and future audit readers should not have to infer which owner decision narrowed the retraction. Exact decision IDs are cheap provenance and matter for this thread because it is explicitly retracting polluted owner-decision records.

Recommended action: Replace the placeholder reference with `DECISION-0843` throughout the revised proposal and packet instructions.

## Positive Confirmations

- The live `bridge/INDEX.md` had the selected document latest as `NEW` before review, so it was actionable for Loyal Opposition.
- The mechanical applicability preflight passed with no missing required or advisory specs.
- The mandatory clause preflight exited with zero blocking gaps.
- The proposal correctly excludes DELIB-2511..2513 from the remediation boundary based on live MemBase evidence.
- The append-only v2 supersession direction is the right remediation shape for the seven polluted rows.

## Opportunity Radar

No separate advisory filed. The main repeat pattern is target-path syntax drift before bridge GO; the deterministic replacement already exists in `scripts/implementation_authorization.py`. The corrective action is to run that parser as a pre-filing or pre-GO dry run and revise the proposal before dispatch.

## Required Revision Checklist

1. Add parseable `target_paths` metadata or a lowercase `## target_paths` section recognized by `scripts/implementation_authorization.py`.
2. Correct the implementation-start command to use the bridge document id, not the expected GO file id.
3. Add valid `Project Authorization:`, `Project:`, and `Work Item:` metadata lines, or explicitly reclassify the proposal as a non-implementation exempt bridge kind and remove implementation-start semantics.
4. Replace the "S374 scope-narrowing AUQ" placeholder with exact owner decision id `DECISION-0843`.
5. Re-run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction` before filing the revision.

