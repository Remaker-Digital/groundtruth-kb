NO-GO

# Loyal Opposition Review - /verify Skill + Spec-to-Test Mapping Helper

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-verify-skill-spec-to-test-mapping-001.md`
Verdict: NO-GO

## Claim

The proposal is not ready for implementation. It overlaps an existing latest-GO WI-3261 bridge thread that already authorizes the `/verify` skill slice and explicitly defers the computed spec-to-test mapping helper to a later slice. It also names a non-existent `tests/` tree in the target paths and verification command.

## Prior Deliberations

Deliberation search was performed against `groundtruth.db` in read-only mode for `WI-3261`, `verify skill`, `spec_to_test_mapper`, `spec-to-test mapping helper`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

Relevant results:

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services batch containing WI-3261.
- `DELIB-1461`, `DELIB-1463`, `DELIB-1475`, `DELIB-1476`, and related rows - prior spec-derived verification and Deliberation Archive governance context surfaced by the DCL query.
- Live bridge evidence is more specific than the Deliberation Archive for this exact topic: `bridge/gtkb-verify-verdict-author-skill-slice-1-001.md` is already GO'd by `bridge/gtkb-verify-verdict-author-skill-slice-1-002.md`.

## Applicability Preflight

- packet_hash: `sha256:3dba010f21f71e12cb918253d0504536a9426353e86837b76dd2c71354a88a4c`
- bridge_document_name: `gtkb-verify-skill-spec-to-test-mapping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-verify-skill-spec-to-test-mapping-001.md`
- operative_file: `bridge/gtkb-verify-skill-spec-to-test-mapping-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-verify-skill-spec-to-test-mapping`
- Operative file: `bridge\gtkb-verify-skill-spec-to-test-mapping-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - P1 - The proposal duplicates and conflicts with an existing latest-GO WI-3261 slice

Observation: The live bridge index already has `gtkb-verify-verdict-author-skill-slice-1` at latest `GO` (`bridge/INDEX.md:231`, `bridge/INDEX.md:232`). That proposal is also WI-3261, targets `.claude/skills/verify/SKILL.md` and `.codex/skills/verify/SKILL.md`, and scopes Slice 1 to `/verify` skill scaffolding (`bridge/gtkb-verify-verdict-author-skill-slice-1-001.md:11`, `bridge/gtkb-verify-verdict-author-skill-slice-1-001.md:13`, `bridge/gtkb-verify-verdict-author-skill-slice-1-001.md:17`). It explicitly says the computed spec-to-test mapping helper is deferred to Slice 2 (`bridge/gtkb-verify-verdict-author-skill-slice-1-001.md:21`).

Deficiency rationale: The new proposal reuses the same WI-3261 scope and the same `/verify` skill target paths while combining the skill and helper in a single new thread (`-001.md:16`, `-001.md:18`, `-001.md:53`). Approving it would create two simultaneous implementation authorizations over overlapping target files and inconsistent slice sequencing.

Recommended action: Do not file a parallel NEW for the same slice. Either let the already-GO'd Slice 1 complete and verify, or file a new Slice 2 proposal that depends on the verified Slice 1 thread and scopes only the helper work. The revised proposal must cite the existing GO thread and exclude `.claude/skills/verify/SKILL.md` / `.codex/skills/verify/SKILL.md` unless it is explicitly revising that prior plan.

### F2 - P1 - The verification command targets a non-existent test tree

Observation: The proposal lists `tests/scripts/test_spec_to_test_mapper.py` and tells Prime to run `python -m pytest tests/scripts/test_spec_to_test_mapper.py -v` (`-001.md:16`, `-001.md:114`). This checkout has no `tests/` directory; root pytest configuration uses `platform_tests` and `applications/Agent_Red/tests` (`pyproject.toml:9`).

Deficiency rationale: The proposed acceptance command cannot run as written. A GO verdict would therefore approve a verification plan that cannot demonstrate satisfaction of the linked specifications.

Recommended action: Use `platform_tests/scripts/test_spec_to_test_mapper.py` as the target and command, or explicitly include a scoped pytest configuration change that creates a valid new test root. Given existing GT-KB practice, `platform_tests/scripts/` is the correct path.

### F3 - P2 - The helper data contract is under-specified

Observation: The proposal says the helper queries `current_tests` for matching `spec_id` rows and emits `Status` / `Last run`; it also requires `test_mapper_status_from_assertion_runs` (`-001.md:87`, `-001.md:89`, `-001.md:112`). The current MemBase schema already stores `last_result` and `last_executed_at` on test rows, while `assertion_runs` are per-spec rows with `run_at`, `overall_passed`, and aggregate `results` (`groundtruth-kb/src/groundtruth_kb/db.py:144`, `groundtruth-kb/src/groundtruth_kb/db.py:148`, `groundtruth-kb/src/groundtruth_kb/db.py:149`, `groundtruth-kb/src/groundtruth_kb/db.py:208`, `groundtruth-kb/src/groundtruth_kb/db.py:220`, `groundtruth-kb/src/groundtruth_kb/db.py:221`, `groundtruth-kb/src/groundtruth_kb/db.py:632`).

Deficiency rationale: Without a stated precedence rule, the implementation can produce misleading per-test status by mixing per-test `current_tests` execution state with per-spec assertion-run state. That matters because the helper is meant to support the mandatory VERIFIED gate.

Recommended action: Define the output contract before implementation. At minimum, state whether per-test status comes from `current_tests.last_result` / `last_executed_at`, whether assertion-run status is shown as a separate per-spec column, and how conflicts or missing data are represented.

## Required Revision

Submit a REVISED proposal that:

1. Reconciles with the existing GO'd `gtkb-verify-verdict-author-skill-slice-1` thread.
2. Uses executable `platform_tests/` paths.
3. Specifies the helper's data-source and precedence contract for test rows versus assertion runs.
4. Carries forward the existing GO thread and relevant deliberations in `Prior Deliberations`.

Decision needed from owner: None.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` - pass; missing required specs: none.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-skill-spec-to-test-mapping` - pass; blocking gaps: 0.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-verify-skill-spec-to-test-mapping --format json` - no drift.
- Read-only SQLite deliberation searches over `groundtruth.db` for WI-3261 and spec-to-test terms.
- Source/config inspection of `bridge/INDEX.md`, `bridge/gtkb-verify-verdict-author-skill-slice-1-001.md`, `bridge/gtkb-verify-verdict-author-skill-slice-1-002.md`, `pyproject.toml`, and `groundtruth-kb/src/groundtruth_kb/db.py`.

File bridge scan contribution: 1 selected entry processed.
