VERIFIED
author_identity: loyal-opposition/openrouter
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: OpenRouter harness shim; route deepseek-v4-pro; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

bridge_kind: verification_verdict
Document: gtkb-hygiene-sweep-agent-red-inherited-config-drift
Version: 004
Author: Loyal Opposition (openrouter, harness F)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-003.md
Recommended commit type: fix / test

## Verdict

VERIFIED. The implementation corrects the `[tool.coverage.run]` `source` field from `["applications/Agent_Red/src"]` to `["groundtruth-kb/src", "scripts"]`, updates `omit` entries in lockstep, and adds a regression assertion (`test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant`) that locks the corrected coverage scope. The implementation matches the approved proposal, all spec-linked tests pass, and both preflights are clean.

## Applicability Preflight

- packet_hash: `sha256:a1020c4aa1a32d74e3508c9ffa52d2f3be8564ae731e3491103717027f38ee71`
- bridge_document_name: `gtkb-hygiene-sweep-agent-red-inherited-config-drift`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-003.md`
- operative_file: `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-hygiene-sweep-agent-red-inherited-config-drift`
- Operative file: `bridge\gtkb-hygiene-sweep-agent-red-inherited-config-drift-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20265457` — owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch, including WI-3419.
- `DELIB-20263459` — Hygiene Sweep Scope Regression (2026-06-12): directly relevant prior decision on hygiene-sweep scope; this implementation remediates a config-drift instance inside that sweep's domain.
- bridge 001 — approved implementation proposal (NEW).
- bridge 002 — Loyal Opposition GO verdict (harness A) authorizing implementation.

## Specifications Carried Forward

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (coverage assertions) | yes | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (source/omit root existence) | yes | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (regression lock) | yes | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` (artifact-backed config) | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` | yes | PASS |

## Positive Confirmations

- Verified `pyproject.toml` `[tool.coverage.run]` now has `source = ["groundtruth-kb/src", "scripts"]` with zero `applications/Agent_Red` references in source or omit.
- Verified `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` exists in `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` and passes.
- Verified commits `f8936dc1e` and `7cd8aa86a` contain exactly the declared changes to `pyproject.toml` and the regression test respectively.
- Verified `ruff check` and `ruff format --check` pass on both target files.
- Verified all declared source/omit roots (`groundtruth-kb/src`, `scripts`) exist on disk.
- Two pre-existing FAB-12 test failures (`test_platform_identity_and_memory_authority_are_explicit`, `test_claude_md_narrative_approval_packet_matches_current_file`) are unrelated to WI-3419 and pre-date the implementation; they do not gate this VERIFIED verdict.

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -c "import tomllib; d = tomllib.load(open('pyproject.toml','rb')); cr = d.get('tool',{}).get('coverage',{}).get('run',{}); print('source:', cr.get('source')); print('omit:', cr.get('omit'))"
```
Output:
```
source: ['groundtruth-kb/src', 'scripts']
omit: ['groundtruth-kb/src/**/__init__.py', 'scripts/**/__init__.py']
```

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py::test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant -v --tb=short
```
Output: **1 passed in 0.15s**

```
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-sweep-agent-red-inherited-config-drift
```
Output: `preflight_passed: true`

```
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-sweep-agent-red-inherited-config-drift
```
Output: Exit 0, zero blocking gaps.

## Authorization

Authorized under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` and `DELIB-20265457`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Intended commit subject: `review(loyal-opposition): VERIFIED agent-red-inherited-config-drift coverage scope correction (WI-3419)`
- Same-transaction path set:
- `pyproject.toml`
- `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`
- `bridge/gtkb-hygiene-sweep-agent-red-inherited-config-drift-004.md`
- Final commit SHA is emitted by the helper after commit creation; it is intentionally not self-embedded in this verdict file.
