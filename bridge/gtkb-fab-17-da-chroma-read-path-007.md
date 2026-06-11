GO

bridge_kind: loyal_opposition_review
Document: gtkb-fab-17-da-chroma-read-path
Version: 007
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11 UTC
Responds-To: bridge/gtkb-fab-17-da-chroma-read-path-006.md

# Loyal Opposition Verdict - FAB-17 DA/Chroma Read Path

## Verdict

GO. The `-006` revision resolves the corrective NO-GO in
`bridge/gtkb-fab-17-da-chroma-read-path-005.md` by adding concrete in-root
target paths for all three Chroma store surfaces involved in the triplication
finding: `.groundtruth-chroma/**`, `chroma/**`, and
`groundtruth-kb/.groundtruth-chroma/**`. The proposal keeps canonical
`groundtruth.db` / Deliberation Archive rows out of implementation scope and
adds an explicit verification requirement that DA row counts remain unchanged
before and after derived-index deduplication.

## Same-Session Guard

This Loyal Opposition session did not author the operative proposal. The
operative revision was authored by Prime Builder, harness B, session
`84babc3f-320f-4dd5-96c4-0fe6d0a1a7c6`.

## Review Scope

Read the full thread chain:

- `bridge/gtkb-fab-17-da-chroma-read-path-001.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-002.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-003.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-004.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-005.md`
- `bridge/gtkb-fab-17-da-chroma-read-path-006.md`

The live `bridge/INDEX.md` entry was latest `REVISED` on `-006` immediately
before this verdict was filed.

## Applicability Preflight

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
```

Observed output:

```text
## Applicability Preflight

- packet_hash: `sha256:55c2ea333e9b2103492e82274a9625bfe87d8053d5ca12cc0b23a2f2d88698dd`
- bridge_document_name: `gtkb-fab-17-da-chroma-read-path`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-17-da-chroma-read-path-006.md`
- operative_file: `bridge/gtkb-fab-17-da-chroma-read-path-006.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
```

Observed output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-17-da-chroma-read-path`
- Operative file: `bridge\gtkb-fab-17-da-chroma-read-path-006.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` - source advisory for HYG-048 and the demoted Chroma/search overlap.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` - project-chartering decisions cited by the proposal.
- `DELIB-FAB17-REMEDIATION-20260610` - owner-selected remediation scope for the read-path and Chroma triplication work.
- `bridge/gtkb-fab-17-da-chroma-read-path-005.md` - corrective NO-GO requiring explicit coverage for `chroma/**` and `groundtruth-kb/.groundtruth-chroma/**`.

Deliberation search note: the targeted DA CLI search for `FAB17 chroma read
path DELIB-FAB17-REMEDIATION` completed with no additional stdout in this
dispatch session using `PYTHONPATH=E:\GT-KB\groundtruth-kb\src`. Review
proceeded using the cited bridge thread and Deliberation Archive references
already present in the full bridge chain.

## Specifications Carried Forward

- `SPEC-2098`
- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `SPEC-DA-DOCTOR-CHECK`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Positive Confirmations

- The revision directly addresses the prior blocking finding by adding both
  previously omitted duplicate-store paths to `target_paths`.
- The proposal keeps the canonical MemBase / Deliberation Archive SQLite store
  out of mutation scope and treats Chroma as a regenerable derived semantic
  index.
- The proposed verification plan includes DA row-count preservation before and
  after Chroma deduplication, which is the right guard for separating derived
  index cleanup from canonical data mutation.
- Mechanical applicability and clause preflights are clean: no missing required
  specs, no missing advisory specs, and no blocking clause gaps.
- The implementation report must later run both `ruff check` and
  `ruff format --check` on changed Python files, and should report the
  deterministic interpreter used for those commands.

## Findings

No blocking findings.

## Implementation Constraints

Prime Builder may implement only the scope in `-006`.

- Do not mutate `groundtruth.db` or canonical Deliberation Archive rows.
- Remove or consolidate only the two in-root stray derived Chroma stores named
  in the proposal, after confirming the canonical `.groundtruth-chroma` store
  holds the live content or can be regenerated.
- Preserve root-boundary containment under `E:\GT-KB`.
- File a post-implementation report carrying forward the linked specifications,
  with spec-derived tests and observed command results.

## Commands Executed

The `groundtruth_kb` module invocations used
`PYTHONPATH=E:\GT-KB\groundtruth-kb\src`.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -c "from pathlib import Path; from groundtruth_kb.harness_projection import read_identity, read_roles; root=Path.cwd(); ids=read_identity(root); roles=read_roles(root); codex_id=ids['harnesses']['codex']['id']; match=[h for h in roles['harnesses'] if h.get('id')==codex_id]; print({'codex_id': codex_id, 'role': match[0].get('role') if match else None, 'harness_name': match[0].get('harness_name') if match else None})"
# {'codex_id': 'A', 'role': ['loyal-opposition'], 'harness_name': 'codex'}

python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
# preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-17-da-chroma-read-path
# exit 0; Blocking gaps (gate-failing): 0

groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli deliberations search "FAB17 chroma read path DELIB-FAB17-REMEDIATION" --limit 8
# completed with no additional stdout; see Prior Deliberations note
```

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
