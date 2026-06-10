VERIFIED

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T17-26Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition verification

bridge_kind: lo_verdict
Document: gtkb-document-author-provenance-contract
Version: 006
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-document-author-provenance-contract-005.md
Recommended commit type: feat

# Loyal Opposition Verification - Document Artifact Author Provenance Contract

## Verdict

VERIFIED.

The post-implementation report satisfies the GO -004 constraints. The helper,
checker, Claude hook, Codex parity wrapper, configuration, hook registrations,
formal-approval packet, and MemBase GOV readback were inspected or reproduced.
The mandatory bridge preflights passed, and the spec-derived tests and
code-quality checks passed locally.

## Applicability Preflight

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:6ea96cadd1ac920193e8c228894de0e7e859efd7a4c59a973166d2485f81a96b`
- bridge_document_name: `gtkb-document-author-provenance-contract`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-document-author-provenance-contract-005.md`
- operative_file: `bridge/gtkb-document-author-provenance-contract-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-document-author-provenance-contract
```

Output:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-document-author-provenance-contract`
- Operative file: `bridge\gtkb-document-author-provenance-contract-005.md`
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

Deliberation search:

```text
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "document author provenance contract WI-3399 DELIB-20260666" --limit 5 --json
```

Relevant results:

- `DELIB-20260666` - S414 owner AUQ chain authorizing the dedicated
  `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE` project and feature-full PAUTH for
  `WI-3399`.
- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - confirms the owner model
  where a declared session role can take precedence for in-session surfaces;
  relevant because the report attributes earlier committed work to a
  `prime-builder/codex/A` peer session while the current durable registry maps
  Codex A to Loyal Opposition.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - carried forward by the report;
  the helper/checker/hook implementation is a deterministic enforcement
  service.

## Specifications Carried Forward

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---:|---|
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | SQLite readback of `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` row in `groundtruth.db` | yes | v1, type `governance`, status `specified`, title present, description length 1993 |
| `GOV-ARTIFACT-APPROVAL-001` | Read `.groundtruth/formal-artifact-approvals/2026-06-04-GOV-DOCUMENT-AUTHOR-PROVENANCE-001.json` | yes | packet exists; action `create`, approval mode `approve`, changed_by `prime-builder/codex/A`, content hash present |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Inspect GOV readback plus helper/checker/hook artifacts | yes | durable GOV spec plus deterministic helper/checker/hook artifacts are present |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-document-author-provenance-contract --format json` | yes | thread has no drift; latest operative was `NEW -005` before this verdict |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Inspect report target paths and committed/staged scope | yes | implementation target paths remain within the approved bridge target set |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Deliberation search for `DELIB-20260666`; read report PAUTH metadata | yes | owner-authorized PAUTH evidence carried forward |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Bridge chain inspection `-003` through `-005` | yes | PAUTH was used with LO GO -004, not as a bridge bypass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on `-005` | yes | `missing_required_specs: []` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Inspect report machine-readable `Project`, `Project Authorization`, and `Work Item` lines | yes | metadata present |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest` document-author suite plus bridge-author regression suite | yes | 17 passed |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge lifecycle chain inspection | yes | NEW -> NO-GO -> REVISED -> GO -> NEW -> VERIFIED chain now complete |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect helper/checker/hook/test/config/GOV artifacts | yes | durable source, tests, config, governance spec, and bridge audit trail exist |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target path classification helper and path inspection | yes | all target paths are under `E:\GT-KB`; none are under `applications/` |

## Positive Confirmations

- The mandatory applicability preflight passed with no missing required or
  advisory specs.
- The mandatory ADR/DCL clause preflight passed with zero blocking gaps.
- `platform_tests/scripts/test_document_author_metadata.py` reproduced
  `12 passed`.
- `platform_tests/scripts/test_document_author_metadata.py` plus
  `platform_tests/scripts/test_bridge_author_metadata.py` reproduced
  `17 passed`, covering bridge-author backward compatibility.
- `platform_tests/scripts/test_hook_registration_parity.py` reproduced
  `2 passed`.
- Ruff lint and format checks passed across
  `scripts/document_author_metadata.py`,
  `scripts/check_document_author_metadata.py`,
  `platform_tests/scripts/test_document_author_metadata.py`,
  `.claude/hooks/document_author_provenance_gate.py`, and
  `.codex/gtkb-hooks/document_author_provenance_gate.py`.
- `.claude/settings.json` and `.codex/hooks.json` parse as valid JSON.
- The Codex parity hook blocks an apply_patch `Add File` for a new governed
  Markdown file without author provenance and allows a non-document `Read`
  payload.
- The formal artifact approval packet exists at
  `.groundtruth/formal-artifact-approvals/2026-06-04-GOV-DOCUMENT-AUTHOR-PROVENANCE-001.json`.
- The live MemBase row for `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` resolves as
  version 1, type `governance`, status `specified`.

## Residual Notes

- `scripts/check_document_author_metadata.py --changed-only --json` currently
  reports 14 findings in unrelated untracked governed Markdown additions under
  `.claude/rules/` and `memory/`. Those files are outside the approved target
  paths for this bridge thread and were not treated as blockers for this
  implementation, but they will need provenance metadata or an authorized
  waiver before they can be safely committed under the new contract.
- The report attributes part of the implementation to `prime-builder/codex/A`.
  The current live durable registry maps Codex harness A to Loyal Opposition,
  but prior owner decision `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH`
  preserves declared session-role override for in-session work. No functional
  verification defect was found from this attribution, but future reports should
  cite the session-role evidence when a harness acts outside its durable
  default role.

## Commands Executed

```text
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\scan_bridge.py --role prime-builder --format json
groundtruth-kb\.venv\Scripts\gt.exe status --startup --json
groundtruth-kb\.venv\Scripts\python.exe .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-document-author-provenance-contract --format json --preview-lines 1200
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-document-author-provenance-contract
git status --short -- <target paths plus bridge paths>
git diff --cached --name-status -- <target paths plus bridge paths>
git log --oneline --max-count=8 -- scripts/document_author_metadata.py scripts/check_document_author_metadata.py config/governance/document-author-provenance.toml groundtruth.db
git show --stat --oneline --name-status 4e062426
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_document_author_metadata.py -q --tb=short -p no:cacheprovider
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_hook_registration_parity.py -q --tb=short -p no:cacheprovider
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_document_author_metadata.py platform_tests\scripts\test_bridge_author_metadata.py -q --tb=short -p no:cacheprovider
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\document_author_metadata.py scripts\check_document_author_metadata.py platform_tests\scripts\test_document_author_metadata.py .claude\hooks\document_author_provenance_gate.py .codex\gtkb-hooks\document_author_provenance_gate.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\document_author_metadata.py scripts\check_document_author_metadata.py platform_tests\scripts\test_document_author_metadata.py .claude\hooks\document_author_provenance_gate.py .codex\gtkb-hooks\document_author_provenance_gate.py
python -m json.tool .claude\settings.json
python -m json.tool .codex\hooks.json
groundtruth-kb\.venv\Scripts\python.exe .codex\gtkb-hooks\document_author_provenance_gate.py < apply_patch-missing-provenance-payload
groundtruth-kb\.venv\Scripts\python.exe .codex\gtkb-hooks\document_author_provenance_gate.py < read-payload
groundtruth-kb\.venv\Scripts\python.exe scripts\check_document_author_metadata.py --changed-only --json
groundtruth-kb\.venv\Scripts\gt.exe deliberations search "document author provenance contract WI-3399 DELIB-20260666" --limit 5 --json
git diff --cached --check -- bridge\INDEX.md bridge\gtkb-document-author-provenance-contract-005.md .codex\gtkb-hooks\document_author_provenance_gate.py .codex\hooks.json .claude\hooks\document_author_provenance_gate.py platform_tests\scripts\test_document_author_metadata.py
```

## Owner Action Required

None.

File bridge scan contribution: 1 entry processed.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
