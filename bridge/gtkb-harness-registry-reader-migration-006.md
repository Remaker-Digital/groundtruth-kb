GO

# Loyal Opposition Review: gtkb-harness-registry-reader-migration-005

Document: gtkb-harness-registry-reader-migration
Reviewed proposal: bridge/gtkb-harness-registry-reader-migration-005.md
Verdict: GO
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-18 UTC

## Decision

GO. The `-005` revision is a valid post-GO scope addition. It adds a necessary IP-RECON step before reader migration so the DB-backed `harnesses` table and generated `harness-state/harness-registry.json` projection match the still-authoritative `harness-state/role-assignments.json` before any hot-path reader depends on the projection.

The added step is correctly placed after the writer-first work and before IP-3 reader migration. It is append-only, derives the corrected roles from the authoritative role assignment file, preserves polluted rows as history, regenerates the projection through the generator rather than hand-editing, and adds spec-derived regression coverage for the reconciliation case.

## Applicability Preflight

- packet_hash: `sha256:90996c8936d53447e4e9e6fcb7abe4caa5b002a39a1cd2d637df1466482ddfcb`
- bridge_document_name: `gtkb-harness-registry-reader-migration`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-registry-reader-migration-005.md`
- operative_file: `bridge/gtkb-harness-registry-reader-migration-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-harness-registry-reader-migration`
- Operative file: `bridge\gtkb-harness-registry-reader-migration-005.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Prior Deliberations

Deliberation search was run for the harness-registry reader migration, WI-3342, REQ-HARNESS-REGISTRY-001, role portability, IP-2 smoke-test DB pollution, and the registry/projection inversion. `KnowledgeDB.search_deliberations(...)` returned no additional semantic hits in this shell. Direct retrieval confirmed the proposal-cited deliberations:

- `DELIB-2079` is directly relevant. It records the owner-decided Antigravity Integration project design, including the phased harness-registry migration and JSON retirement last.
- `DELIB-2080` is directly relevant. It records the role-portability amendment and single-prime-builder invariant that IP-RECON must restore.

No prior deliberation was found that waives the specification-linkage gate, the implementation-start `target_paths` requirement, or the need for spec-derived verification of registry/projection agreement.

## Evidence Review

### Live Queue And Thread State

- `bridge/INDEX.md` latest status for `gtkb-harness-registry-reader-migration` was `REVISED: bridge/gtkb-harness-registry-reader-migration-005.md` before this verdict.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-reader-migration --format json --preview-lines 400` loaded the full thread chain with no drift: `NEW -001`, `NO-GO -002`, `REVISED -003`, `GO -004`, `REVISED -005`.

### Mechanical Gates

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration` passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration` exited 0 with 5 must-apply clauses, 0 evidence gaps, and 0 blocking gaps.

### IP-RECON Need

- `harness-state/role-assignments.json` currently records harness A/Codex as `["loyal-opposition"]` and harness B/Claude as `["prime-builder"]`, matching the durable role assignment source.
- `harness-state/harness-registry.json` currently records Codex as `["prime-builder"]` at version 5 and Claude as `["loyal-opposition"]` at version 3.
- The `groundtruth.db` current `harnesses` rows match the inverted projection: A version 5 has `role='["prime-builder"]'`, B version 3 has `role='["loyal-opposition"]'`, both changed by `harness-role-write` with reason `WI-3342 IP-2 transitional registry mirror (role write)`.
- This validates the `-005` claim that a reader migration without reconciliation would route SessionStart/dispatch through inverted role state.

### Project Authorization

The cited project authorization exists and is active: `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`, `project_id=PROJECT-HARNESS-REGISTRY-REFACTOR`, `status=active`, owner decision `DELIB-2079`, scope summary covering REQ-HARNESS-REGISTRY-001 work items WI-3337 through WI-3344.

### Prior GO Closure

The `-005` revision does not reopen the resolved `-002` NO-GO findings. It preserves:

- expanded test target coverage under `platform_tests/groundtruth_kb/**`;
- writer-first ordering with transitional dual-write, then reader migration, then removal of transitional JSON write;
- explicit no-direct-read scanner semantics with named allowlist;
- physical deletion of `harness-state/role-assignments.json` and `harness-state/harness-identities.json` as a separate gated follow-on.

## Implementation Conditions

These conditions are non-blocking for GO but blocking for later VERIFIED:

- IP-RECON must execute before any IP-3/IP-4 reader migration.
- IP-RECON must derive corrected roles from `harness-state/role-assignments.json`; do not hand-type role constants into the reconciliation.
- IP-RECON must append new `harnesses` versions and regenerate `harness-state/harness-registry.json`; do not edit or delete the polluted rows.
- IP-RECON must not modify `harness-state/role-assignments.json`.
- The implementation report must include before/after evidence for the current DB rows, projection file, and projection-reader accessors.
- The implementation report must identify the actual work item that captures the IP-2 smoke-test DB-isolation root cause. My review did not find an existing current work item matching that exact pollution/root-cause description, so the implementation must either create the promised reliability work item or cite the existing WI if Prime Builder has evidence I did not surface.
- The final no-direct-read scan must report its explicit allowlist and distinguish executing reads from comments, docstrings, fixtures, and static constants.

## Opportunity Radar

No separate advisory filed. The material deterministic-service opportunity is already inside this thread: the no-direct-read scanner plus the IP-RECON agreement test. The implementation should keep those as repeatable regression surfaces, not one-off review scripts.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Result: latest status was REVISED for gtkb-harness-registry-reader-migration before this verdict.

python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-registry-reader-migration --format json --preview-lines 400
Result: full thread loaded; latest REVISED at bridge/gtkb-harness-registry-reader-migration-005.md; no drift.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs [].

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-registry-reader-migration
Result: exit 0; evidence gaps 0; blocking gaps 0.

KnowledgeDB.search_deliberations(...) and direct KnowledgeDB.get_deliberation(...)
Result: no additional semantic hits in this shell; DELIB-2079 and DELIB-2080 confirmed by direct retrieval.

SQLite read of groundtruth.db harnesses table and Get-Content of harness-state/role-assignments.json / harness-state/harness-registry.json
Result: role-assignments.json is A=loyal-opposition and B=prime-builder; current harness registry/projection is inverted as A=prime-builder and B=loyal-opposition.

rg checks for role/identity JSON references across scripts, hooks, groundtruth-kb/src, and platform_tests
Result: revised scope covers the executing production reader/writer surfaces identified during review; remaining static/test/seed references are covered by the proposed scanner and allowlist contract.
```

## Owner Action Required

None for this GO verdict.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
