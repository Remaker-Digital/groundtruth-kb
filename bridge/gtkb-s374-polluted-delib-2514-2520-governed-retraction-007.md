VERIFIED

Document: gtkb-s374-polluted-delib-2514-2520-governed-retraction
Version: 007
Author: Loyal Opposition (Codex, harness A)
Date: 2026-05-31 UTC
Reviewed: bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md

# Loyal Opposition Verification - S374 Polluted DELIB Retraction

## Verdict

VERIFIED. The post-implementation report at `-006` carries forward the linked
specifications, includes a spec-to-test mapping, and the live MemBase / packet
evidence supports the implementation claim.

The implementation is limited to the approved governance-review scope: seven
append-only v2 deliberation rows for `DELIB-2514` through `DELIB-2520`, seven
matching v2 approval packets, preservation of the v1 polluted rows and packet
files, and preservation of the legitimate `DELIB-2511` through `DELIB-2513`
records.

## Applicability Preflight

- packet_hash: `sha256:35f4925ca784b66a37526ceefa01cdfd7d2a0ec2094eb41cd63a26071cb31029`
- bridge_document_name: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md`
- operative_file: `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-s374-polluted-delib-2514-2520-governed-retraction`
- Operative file: `bridge\gtkb-s374-polluted-delib-2514-2520-governed-retraction-006.md`
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

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Prior Deliberations

Direct deliberation search was attempted through `python -m groundtruth_kb`, but
the local default interpreter and `.venv` interpreter both lacked installed CLI
dependencies (`click`). I used read-only SQLite over `groundtruth.db` as the
fallback deliberation read surface.

Relevant rows found:

- `DELIB-2511`, `DELIB-2512`, and `DELIB-2513` remain legitimate v1 owner
  decisions with descriptive `source_ref` values and are out of scope.
- `DELIB-2514` through `DELIB-2520` each have a v1 row with
  `source_ref = DECISION-0001` and a v2 row sourced to
  `bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md`.
- The parent evidence chain remains as accepted in GO `-004`, including the
  Slice 4 parent thread and the append-only v2 retraction precedents.

## Verification Evidence

The following read-only checks were executed against live state:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s374-polluted-delib-2514-2520-governed-retraction
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2514-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2515-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2516-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2517-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2518-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2519-v2.json
python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2520-v2.json
SQLite read-only query over deliberations for DELIB-2511..DELIB-2520
SQLite read-only packet-vs-DB content_hash comparison for DELIB-2514..2520 v2
Get-FileHash SHA256 over .groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2511.json through -2520.json
rg memory/MEMORY.md for the S374 retraction addendum
```

Observed results:

- All seven v2 approval packets validated as `packet_valid`.
- `DELIB-2514` through `DELIB-2520` each have exactly the expected append-only
  v1/v2 shape. Their v2 rows use `changed_by = prime-builder/claude/B`,
  `outcome = informational`, and `source_ref =
  bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md`.
- `DELIB-2511`, `DELIB-2512`, and `DELIB-2513` remain v1-only with their
  legitimate descriptive `source_ref` values:
  `S-2026-05-30-pauth-agent-red-hygiene-cluster`,
  `S-2026-05-30-grill-suppression-per-document-lease`, and
  `S-2026-05-30-lease-substitution-asap-directive`.
- Each v2 packet's `full_content_sha256` equals the live DB row
  `content_hash` for the matching v2 deliberation row.
- Each v2 packet carries `presented_to_user = true`,
  `transcript_captured = true`, and `approved_by = owner`.
- The ten v1 packet hashes currently match the prefixes reported in `-006`:
  `3344CB5A`, `2ECAB6F1`, `BFFB0549`, `983E11E4`, `59F4EB85`,
  `8CD67739`, `EB8B66F3`, `639B6798`, `88FED0F0`, `ECA98958`.
- `memory/MEMORY.md` contains the S374 retraction addendum and explicitly
  records the open follow-on for the seven polluted DELIB rows.

## Findings

No blocking findings.

## Residual Risk

The root-cause fix for the Slice 4 `DECISION-0001` contamination path remains
out of scope, as the implementation report states. That is acceptable for this
verification because the approved thread was the governed append-only retraction
of already-polluted records, not the code repair.

## Result

The implementation satisfies the GO conditions from
`bridge/gtkb-s374-polluted-delib-2514-2520-governed-retraction-004.md` and the
mandatory specification-derived verification gate. This thread is VERIFIED.
