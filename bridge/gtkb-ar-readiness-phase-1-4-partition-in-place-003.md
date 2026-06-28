NEW

# gtkb-ar-readiness-phase-1-4-partition-in-place - Implementation Report

bridge_kind: implementation_report
Document: gtkb-ar-readiness-phase-1-4-partition-in-place
Version: 003
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T22:14:00Z

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f103f-3963-70b0-8879-13c9646709dd
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4657
Implementation commit: 0b22d3daa
Implementation-start packet: sha256:ae0471ca8bba5141e363b7db6a0b80c6b76ed28cdc67a0152c58b18e0d759407
Responds to GO: bridge/gtkb-ar-readiness-phase-1-4-partition-in-place-002.md

## Summary

Implemented the Agent Red Readiness Phase 1.4 partition-in-place support under the approved GO scope.

The implementation adds nullable `application_scope` schema support for specs and tests, carries that field through the `KnowledgeDB` insert/update paths and governed `gt spec record` / `gt spec update` CLI services, adds application-scope classification helpers, adds a dry-run-first partition helper, and adds a doctor check for explicit scope/path alignment.

The live migration execute path was run after verification. It applied zero row updates because the live MemBase data has no unambiguous Agent Red application rows under the approved classifier. It reported 26 ambiguous candidates and zero violations, which preserves the proposal's false-positive guard instead of silently rewriting generic top-level Agent Red references.

## Files Changed

- `groundtruth.db`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`
- `groundtruth-kb/src/groundtruth_kb/cli_spec_update.py`
- `groundtruth-kb/src/groundtruth_kb/project/application_scope.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `scripts/agent_red_partition_in_place.py`
- `platform_tests/scripts/test_agent_red_partition_in_place.py`
- `platform_tests/scripts/test_application_scope_doctor.py`
- `groundtruth-kb/tests/test_db.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-APPLICATION-ISOLATION-CONTRACT-001`
- `DCL-APP-ROOT-MINIMIZATION-001`
- `DCL-ADOPTER-SPEC-RECLASSIFICATION-001`

## Spec-To-Test Mapping

| Specification | Verification evidence |
| --- | --- |
| `DCL-ADOPTER-SPEC-RECLASSIFICATION-001` | `platform_tests/scripts/test_agent_red_partition_in_place.py` proves unambiguous legacy Agent Red rows are updated append-only and ambiguous mixed/generic candidates are reported rather than rewritten. Live execute reported 26 ambiguous candidates, zero violations, and zero safe actions. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`, `DCL-APP-ROOT-MINIMIZATION-001` | `groundtruth_kb.project.application_scope` and `platform_tests/scripts/test_application_scope_doctor.py` enforce `applications/Agent_Red/` alignment for explicit app-scoped rows and reject platform rows pointing at application product paths. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The migrator builds each manifest from live `KnowledgeDB.list_specs()` and `KnowledgeDB.list_tests()` reads. The live dry-run and execute commands were run against `groundtruth.db` after the schema migration. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation-start packet `sha256:ae0471ca8bba5141e363b7db6a0b80c6b76ed28cdc67a0152c58b18e0d759407` was created from the latest GO and each target path validated authorized before staging. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, migrator dry-run/execute, doctor, Ruff lint, and Ruff format checks were executed and recorded below. |

## Verification Commands And Results

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-ar-readiness-phase-1-4-partition-in-place --session-id 2026-06-28T21-47-39Z-prime-builder-A-5a1435
PASS - packet_hash sha256:ae0471ca8bba5141e363b7db6a0b80c6b76ed28cdc67a0152c58b18e0d759407

python scripts/implementation_authorization.py validate --target <each approved target path>
PASS - all 11 WI-4657 target paths authorized

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py -q --tb=short
PASS - 113 passed, 1 warning in 33.84s

python scripts/agent_red_partition_in_place.py --json
PASS - dry-run; action_count 0, ambiguous_count 26, violation_count 0

python scripts/agent_red_partition_in_place.py --execute --json
PASS - applied [], action_count 0, ambiguous_count 26, violation_count 0

gt project doctor --dir . --json
PASS/WARNING - Knowledge DB pass; File Bridge State pass; Application scope alignment warning with 26 ambiguous candidates and zero violations; overall warning due existing non-slice warnings

groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py groundtruth-kb/src/groundtruth_kb/cli_spec_update.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/application_scope.py scripts/agent_red_partition_in_place.py platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py
PASS - All checks passed

groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py groundtruth-kb/src/groundtruth_kb/cli_spec_update.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/application_scope.py scripts/agent_red_partition_in_place.py platform_tests/scripts/test_agent_red_partition_in_place.py platform_tests/scripts/test_application_scope_doctor.py groundtruth-kb/tests/test_db.py
PASS - 10 files already formatted

git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol diff --cached --check
PASS

git -c core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol commit -m "feat: add Agent Red application scope partition"
PASS - commit 0b22d3daa
```

## Acceptance Status

- Schema support for `application_scope` on specs/tests: complete.
- Append-only insert/update carry-forward for `application_scope`: complete.
- Governed spec record/update CLI support for `--application-scope`: complete.
- Dry-run-first migration helper with 50-row execute ceiling: complete.
- Live execution against `groundtruth.db`: complete; zero safe row mutations were available, 26 ambiguous candidates remained intentionally unmodified.
- Doctor alignment check: complete; reports violations as failures and ambiguous unscoped candidates as warnings.

## Known Residuals

The live MemBase data still has 26 ambiguous Agent Red-related candidates whose paths are generic top-level or mixed platform/application evidence. The approved proposal explicitly required ambiguous candidates to remain unchanged and be reported for later review, so this report does not claim those rows are reclassified.

## Recommended Commit Type

Recommended commit type: feat

## Risk / Rollback

The implementation mutates schema/API surfaces and `groundtruth.db`, but the data migration itself applied no row updates because there were no unambiguous live candidates. Rollback is a revert of commit `0b22d3daa`; any future row-level reclassification should remain append-only through `KnowledgeDB.update_spec()` / `KnowledgeDB.update_test()`.
