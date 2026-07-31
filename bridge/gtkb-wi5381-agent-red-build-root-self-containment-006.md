GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 9f8e599a-6ec5-4f01-9d98-cb4999def835
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing; independent fresh review session with no relationship to any prior author or reviewer session on this thread

# LO Review - WI-5381 Agent Red Application-Root Build Self-Containment (Revision 005)

bridge_kind: lo_verdict
Document: gtkb-wi5381-agent-red-build-root-self-containment
Version: 006
Responds to: bridge/gtkb-wi5381-agent-red-build-root-self-containment-005.md
Reviewed_document: bridge/gtkb-wi5381-agent-red-build-root-self-containment-005.md
Date: 2026-07-17 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5381

## Verdict

GO.

## Rationale

Version 005 is a REVISED proposal (bridge_kind: prime_proposal) that supersedes
version 001 and directly answers all three blockers raised in version 003
(Prime NO-ACTION) and version 004 (prior Loyal Opposition NO-GO from
harness E / Cursor):

1. Version 002's operative GO lacked a detector-recognized
   "## Specification-Derived Verification" section. Version 005 line 223
   carries that exact heading with a nine-row requirement-to-command-to-
   expected-result table. Confirmed by direct read of the file.
2. WI-5392 was cited as a hard sequencing predecessor but was not committed
   in the parent tree. Version 005 removes the shared portability test file
   (platform_tests/scripts/test_modernization_agent_red_portability.py) from
   target_paths entirely, so WI-5381 no longer has any implementation
   overlap with WI-5392 or WI-5405 and the hard-sequencing claim is moot.
   Independently confirmed: WI-5392's own thread
   (gtkb-wi5392-rehearse-outside-root-fixture) is latest VERIFIED at version
   004, and WI-5405's thread (gtkb-wi5405-portability-fixture-read-guard) is
   latest REVISED targeting only
   platform_tests/scripts/test_modernization_agent_red_portability.py -- a
   path that does not appear anywhere in version 005's 18-entry target_paths
   list.
3. Version 001/002 reserved destructive deletion of six legacy root build
   files (.dockerignore, Dockerfile, Dockerfile.test, Dockerfile.ui,
   docker-compose.yml, .github/workflows/build-test-host.yml) without
   citing owner per-path destructive authority. Version 005 removes every
   one of those six paths from target_paths and adds an explicit
   "Explicit Exclusions" section naming all six by path. Independently
   confirmed the active project authorization
   (PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE)
   forbids "destructive_cleanup" -- version 005 is now consistent with its
   own cited authorization, where version 001/002 was not.

## Independent Verification Performed

Filesystem (not proposal prose) was inspected directly for all 18 declared
target_paths in version 005:

- Confirmed MISSING (matches the 15-missing-target baseline claim):
  applications/Agent_Red/Dockerfile, Dockerfile.test, Dockerfile.ui,
  docker-compose.yml, pyproject.toml, requirements.txt,
  requirements-test.txt, requirements-local.txt,
  .github/workflows/build-test-host.yml, test_host/__init__.py,
  test_host/cosmos_writer.py, test_host/main.py, test_host/runner.py,
  test_host/suites.py, scripts/sync-admin-env.ps1.
- Confirmed EXISTING (matches the 3-existing-target baseline claim):
  applications/Agent_Red/.dockerignore, .gtkb-app-isolation.json,
  tests/test_host/test_build_contract.py.
- Confirmed the six excluded platform-root legacy files (.dockerignore,
  Dockerfile, Dockerfile.test, Dockerfile.ui, docker-compose.yml,
  .github/workflows/build-test-host.yml) all still exist at the GT-KB root
  and are absent from version 005's target_paths -- the revision is
  genuinely non-destructive as claimed.
- Confirmed applications/Agent_Red/tests/test_host/ already contains a full
  eight-file test suite (test_api.py, test_build_contract.py,
  test_cosmos_writer.py, test_dispatch.py, test_dispatch_integration.py,
  test_runner.py, test_spa_contract.py, test_suites.py) that imports
  "test_host.main", "test_host.runner", "test_host.suites", and
  "test_host.cosmos_writer" -- none of which currently exist. This is
  independent corroboration that the missing test_host package is a live
  collection failure today, not a hypothetical.
- Confirmed test_build_contract.py's PROJECT_ROOT already resolves three
  parents up from tests/test_host/, i.e. to applications/Agent_Red/ itself
  -- the existing test is already application-root-relative and will find
  the newly created Dockerfile/.dockerignore/requirements files once they
  exist, with no path rewrite needed in that test.
- Confirmed historical cleanup commit 6e25fbe16a9a54e34ce464d77e509242e70270a8
  (2026-04-29) deleted exactly five tracked test_host/ files as part of a
  24-category stale-directory sweep, and that the pre-deletion parent commit
  (6e25fbe1^) carries test_host/main.py with a matching header comment --
  the "last tracked implementation" restoration source cited by the
  proposal is real and resolvable.
- Confirmed via SPEC-1825 (status: implemented) that the self-service
  deployment pipeline's VERIFY stage explicitly requires "test suite
  execution on test host (existing infrastructure)" -- the deleted package
  is a live dependency of an implemented spec, not stale debris, which is
  the crux of the proposal's justification for un-deleting it.
- Confirmed applications/Agent_Red/admin/{standalone,provider,shopify}/package.json
  each run "../../scripts/sync-admin-env.ps1", resolving to
  applications/Agent_Red/scripts/sync-admin-env.ps1, which is confirmed
  absent. Confirmed the only existing sync-admin-env.ps1 (at GT-KB root)
  derives its target root from its own script location and would resolve
  to a root-level admin/ directory that does not exist on this host --
  independent confirmation that no functioning application-owned sync
  script currently exists for Agent Red.
- Confirmed the isolation registry (.gtkb-app-isolation.json) already
  registers "scripts" and "tests" as top-level entries (both pre-existing
  directories) but does not yet register "test_host", ".github", or any of
  the eight new top-level files version 005 proposes to add -- Acceptance
  Criterion 3 (exact registry coverage) is a real, currently-unmet gap that
  the revision correctly scopes as in-scope work.
- Confirmed applications/Agent_Red/.gtkb-app-isolation.json's existing
  ".dockerignore" registry entry already anticipates this exact migration
  ("placeholder pending Phase 3 infra cluster move that brings Dockerfile*
  into this directory"), corroborating that this move was expected, not
  novel scope creep.
- Confirmed via git status --short -- applications/Agent_Red/ that the
  application subtree is currently clean (no output), so no other in-flight
  session is concurrently modifying any file in this proposal's target set.

## Mandatory Preflights

## Applicability Preflight

Command: groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5381-agent-red-build-root-self-containment

- packet_hash: `sha256:9bd6e06764fe1cb964b9fe755d09b7c1ee35559169031856a0865719fb771063`
- bridge_document_name: `gtkb-wi5381-agent-red-build-root-self-containment`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5381-agent-red-build-root-self-containment-005.md`
- operative_file: `bridge/gtkb-wi5381-agent-red-build-root-self-containment-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: non-blocking; expected for the six not-yet-created paths under .github/workflows/ and test_host/ (both directories do not exist yet, exactly matching what the proposal says it will create).
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` |

### Clause Applicability

Command: groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5381-agent-red-build-root-self-containment

Result: exit code 0. Clauses evaluated: 5 (4 must_apply, 1 may_apply, 0 not_applicable). Evidence gaps in must_apply clauses: 0. Blocking gaps: 0.

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | may_apply | no (non-gating; may_apply clauses do not gate per tool contract) |

#### Blocking Gaps

None.

## Project Authorization Verification

Independently queried KnowledgeDB.get_project_authorization for
PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
rather than trusting the proposal's citation. Result: status active,
project_id PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE, no per-work-item
inclusion restriction (covers WI-5381 by project membership),
allowed_mutation_classes includes source/test/configuration/metadata
(covers everything version 005 proposes), forbidden_operations includes
destructive_cleanup/dispatcher_mutation/git_commit/git_push/deployment/
release/credential_lifecycle/external_system_mutation -- version 005's
scope (application-local file creation, no deletion, no git operation, no
credential access, no deployment) is fully inside the authorized envelope.

## Backlog and Bridge Conflict Check

Independently queried the WI-5381 MemBase record directly (not the bridge
proposal's paraphrase): resolution_status open, stage backlogged, priority
P0, project PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE. The record's own
status_detail field independently corroborates the WI-5405 sequencing
correction and the admin-package sync-script coupling claim, written before
this review and consistent with everything found by direct filesystem
inspection above.

Searched bridge/ for other threads touching the same paths. Found:
gtkb-wi5435-agent-red-frontend-gate-paths (latest NO-GO, target_paths
limited to scripts/release_candidate_gate.py and its platform test -- no
overlap with version 005's application-local target set),
gtkb-isolation-016-phase8-wave2-slice9 (latest VERIFIED, terminal),
critical-remediation-root-isolation (latest VERIFIED, terminal). No
active, non-terminal bridge thread targets any path in version 005's
target_paths list. No backlog or bridge conflict found.

Deliberation Archive was searched (search_deliberations) for prior related
decisions on Agent Red build-root self-containment, application isolation
contract test-host requirements, and Agent Red destructive cleanup
authority. No prior deliberation was found that rejects or contradicts the
non-destructive application-local build/test-host restoration approach
version 005 now takes; the closest relevant precedent is the thread's own
version 003/004 history, which version 005 already cites and answers
directly.

## Specification Links (carried forward)

All specification IDs cited in version 005's Specification Links section
were spot-checked against the live KB (db.get_spec) rather than trusted at
face value: ADR-ISOLATION-APPLICATION-PLACEMENT-001,
ADR-APPLICATION-ISOLATION-CONTRACT-001, DCL-APP-ROOT-MINIMIZATION-001,
GOV-AGENT-RED-GTKB-CONFORMANCE-001, GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001,
SPEC-1825, GOV-RELEASE-READINESS-GOVERNED-TESTING-001,
GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, SPEC-CODE-QUALITY-CHECKLIST-001,
GOV-WORK-TREE-HYGIENE-001, DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001,
and DCL-PROJECT-DEPENDENCY-ORDERING-001 all resolved to real KB records with
titles consistent with how the proposal characterizes them. None were
fabricated or mischaracterized.

## Conditions

- All mutation remains confined to the 18 declared target_paths, all of
  which resolve under applications/Agent_Red/ inside E:\GT-KB.
- No mutation, deletion, or rewrite of the six platform-root legacy build
  files, root pyproject.toml/requirements, root scripts/sync-admin-env.ps1,
  scripts/release_candidate_gate.py, scripts/session_self_initialization.py,
  or any platform test. Any deviation into those paths is out of scope for
  this GO and would require a fresh proposal.
- The five restored test_host modules must satisfy the pre-existing,
  unmodified tests/test_host/ suite (test_api.py, test_cosmos_writer.py,
  test_dispatch.py, test_dispatch_integration.py, test_runner.py,
  test_spa_contract.py, test_suites.py, test_build_contract.py) since none
  of those seven non-build-contract test files are in target_paths and
  therefore cannot be modified to fit the restored implementation --
  compatibility must run in that direction only.
- The isolation registry update must cover every new top-level artifact
  (test_host, .github, Dockerfile, Dockerfile.test, Dockerfile.ui,
  docker-compose.yml, pyproject.toml, requirements.txt,
  requirements-test.txt, requirements-local.txt) with an exact bucket A or
  bucket B entry per DCL-APP-ROOT-MINIMIZATION-001, matching Acceptance
  Criterion 3.
- No live credentials, cloud writes, deployment, dispatcher, TAFE, routing,
  role, eligibility, or harness mutation, consistent with the proposal's own
  hard invariants and this review's scope boundary.
- Independent VERIFIED and the required commit-finalization helper remain
  mandatory before this work item is treated as complete; this GO does not
  itself authorize commit, push, or deployment.

## Scope Boundary Note

This review did not touch, and found no reason to touch, dispatcher
configuration, harness role registries, or dispatch-eligibility settings.
Version 005 does not request any such mutation and none is implicated by
this GO.

## Minor Observations (non-blocking)

- Version 002 (the original, now-superseded GO from harness E / Cursor)
  used "bridge_kind: loyal_opposition_review", a value not present in the
  currently valid bridge_kind enum (governance_advisory,
  implementation_report, index_reconciliation, lo_verdict,
  operational_state_change, prime_proposal). This verdict uses the correct
  "lo_verdict" value. Flagging only as a hygiene note for the enum's
  historical drift; it does not affect this GO since version 002 is already
  superseded.
- The clause preflight's one may_apply, no-evidence clause
  (GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS) does not gate per
  the tool's own documented contract (only must_apply clauses with absent
  evidence gate). Noted for completeness; not a blocker.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
