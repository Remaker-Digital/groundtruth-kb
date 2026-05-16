NO-GO

# Loyal Opposition Review - In-Source Provenance Anchors and Orphan-Citation Doctor

Reviewed proposal: `bridge/gtkb-in-source-provenance-anchors-001-prop.md`
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-16 UTC
Verdict: NO-GO

## Verdict

NO-GO. The proposal objective is sound, and the mandatory blocking preflights pass, but the live bridge thread is filed in a non-versioned shape that the canonical thread loader cannot read as a version chain, and the proposed verification path uses the stale root `tests/scripts/**` surface instead of a live GT-KB test surface.

## Prior Deliberations

Deliberation Archive searches were run before review for:

- `GTKB-IN-SOURCE-PROVENANCE-ANCHORS-001 S332 anchor-only source comments Deliberation Archive`
- `in-source provenance anchors orphan citation doctor MemBase bridge DELIB`

Relevant records surfaced:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - project authorization context for the batch containing this work item.
- `DELIB-1629` and `DELIB-1917` - ISOLATION-017 citation audit / citation-backfill verification context.
- `DELIB-1554` - DA read-surface/template pre-population verification context showing citation/read-surface support needs.
- `DELIB-0974`, `DELIB-0975`, and `DELIB-1300` - bridge INDEX/file-reference hygiene precedent.

No searched deliberation rejects the anchor-only citation convention. The blockers are proposal-shape and verification-surface defects, not objections to the product goal.

## Applicability Preflight

- packet_hash: `sha256:97b9b6b96ef976ddd48406f75fdfca02d4f7b1a6b7f9d04b6c38cb443f62dd23`
- bridge_document_name: `gtkb-in-source-provenance-anchors-001-prop`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-in-source-provenance-anchors-001-prop.md`
- operative_file: `bridge/gtkb-in-source-provenance-anchors-001-prop.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability

- Bridge id: `gtkb-in-source-provenance-anchors-001-prop`
- Operative file: `bridge\gtkb-in-source-provenance-anchors-001-prop.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - P1 - The indexed proposal file is not protocol-versioned, so the canonical full-chain helper cannot load it

Evidence:

- `bridge/INDEX.md` lists `Document: gtkb-in-source-provenance-anchors-001-prop` and `NEW: bridge/gtkb-in-source-provenance-anchors-001-prop.md`.
- `bridge/gtkb-in-source-provenance-anchors-001-prop.md` declares `Document: gtkb-in-source-provenance-anchors-001-prop` and `Version: 001`, but the filename is not `bridge/gtkb-in-source-provenance-anchors-001-prop-001.md`.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-in-source-provenance-anchors-001-prop --format markdown --preview-lines 1200` returned `_No version files found on disk for slug 'gtkb-in-source-provenance-anchors-001-prop'._`
- `.claude/skills/bridge/helpers/show_thread_bridge.py` looks for `bridge/<slug>-NNN.md`.
- `.claude/rules/file-bridge-protocol.md` requires `{descriptive-name}-{NNN}.md` and INDEX lines shaped as `STATUS: bridge/{descriptive-name}-{NNN}.md`.

Impact: A GO would normalize a malformed bridge thread whose operative proposal is invisible to the canonical full-chain loader.

Required action: Refile the proposal using a protocol-conformant numbered filename and INDEX line. Preserve the existing malformed file as historical evidence if needed, but the live actionable proposal should be a numbered bridge file the helper can load.

### F2 - P1 - Verification uses the stale root `tests/scripts/**` surface

Evidence:

- `bridge/gtkb-in-source-provenance-anchors-001-prop.md:16` declares `tests/scripts/test_orphan_citation_audit.py` in `target_paths`.
- `bridge/gtkb-in-source-provenance-anchors-001-prop.md:106` runs `python -m pytest tests/scripts/test_orphan_citation_audit.py -v`.
- `pyproject.toml:9` sets pytest discovery to `["platform_tests", "applications/Agent_Red/tests"]`.
- `.github/workflows/groundtruth-kb-tests.yml:42` runs `python -m pytest platform_tests/ -q --tb=short`.
- `Test-Path tests/scripts/test_orphan_citation_audit.py` returned false.
- The root `tests/` directory currently contains only `tests/skills`, while an adjacent citation test exists under `platform_tests/scripts/test_isolation_017_citation_backfill_audit.py`.

Impact: The proposed tests would not be part of the live root pytest discovery/CI surface.

Required action: revise `target_paths` and the verification plan to use a live test surface, for example `platform_tests/scripts/test_orphan_citation_audit.py` and `python -m pytest platform_tests/scripts/test_orphan_citation_audit.py -q --tb=short`.

## Non-Blocking Notes For Revision

- The revised proposal should cite the three advisory specs reported missing by the applicability preflight.
- The project authorization is active for `PROJECT-GTKB-MEMBASE-EFFECTIVE-USE`.
- If Prime will create `.claude/rules/in-source-citation-conventions.md`, the approval-packet path must either be included in implementation scope or handled through the governed approval path before the protected rule write.

File bridge scan: 1 entry processed.
