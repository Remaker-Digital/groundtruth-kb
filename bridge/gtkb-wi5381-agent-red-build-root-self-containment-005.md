REVISED
::init gtkb lo
::open build

# WI-5381 - Agent Red Application-Root Build Self-Containment

bridge_kind: prime_proposal
Document: gtkb-wi5381-agent-red-build-root-self-containment
Version: 005
Responds to: bridge/gtkb-wi5381-agent-red-build-root-self-containment-004.md
Supersedes proposal: bridge/gtkb-wi5381-agent-red-build-root-self-containment-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5381

target_paths: ["applications/Agent_Red/.dockerignore", "applications/Agent_Red/.gtkb-app-isolation.json", "applications/Agent_Red/Dockerfile", "applications/Agent_Red/Dockerfile.test", "applications/Agent_Red/Dockerfile.ui", "applications/Agent_Red/docker-compose.yml", "applications/Agent_Red/pyproject.toml", "applications/Agent_Red/requirements.txt", "applications/Agent_Red/requirements-test.txt", "applications/Agent_Red/requirements-local.txt", "applications/Agent_Red/.github/workflows/build-test-host.yml", "applications/Agent_Red/test_host/__init__.py", "applications/Agent_Red/test_host/cosmos_writer.py", "applications/Agent_Red/test_host/main.py", "applications/Agent_Red/test_host/runner.py", "applications/Agent_Red/test_host/suites.py", "applications/Agent_Red/tests/test_host/test_build_contract.py", "applications/Agent_Red/scripts/sync-admin-env.ps1"]

implementation_scope: application-owned build, dependency, test-host, environment-sync, registry, and contract-test surfaces
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete the Agent Red application-root build contract without deleting,
rewriting, or adopting any platform-root or concurrently owned file. Agent Red
currently has application source and tests but no application-owned Python
dependency manifests, Python project configuration, Docker/compose surfaces,
test-host service, build-test-host workflow, or environment-sync script. Its
existing test-host tests and three admin package scripts already resolve these
missing application-local surfaces.

The implementation will create the missing application-owned files, replace the
existing application `.dockerignore` placeholder with the real build-context
contract, register each new top-level artifact, and extend the existing
application-local build-contract test. Historical root or pre-cleanup bytes may
be used as read-only reconstruction evidence, but every resulting path and
runtime assumption must be reconciled to the current Agent Red application root.

This revision is deliberately non-destructive. The six legacy root build files,
root dependency/configuration surfaces, platform release gate, shared
portability tests, dispatcher/TAFE, and Git state are outside the target
inventory and remain byte-for-byte untouched.

## Requirement Sufficiency

Existing requirements sufficient. The application-isolation contract,
application-root minimization constraint, `SPEC-1825` test-host requirement,
governed release-readiness requirement, and modernization non-impairment
contract already determine the required outcome. No new product policy or
formal requirement is needed.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all Agent Red artifacts remain
  below the canonical in-root application namespace.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - build, dependency, runtime,
  release, and verification artifacts belong to the application lifecycle and
  must operate after relocation without GT-KB-root dependencies.
- `DCL-APP-ROOT-MINIMIZATION-001` - every added top-level application artifact
  must have an exact registry entry and application-owned purpose.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red remains a conformant
  reference adopter with lifecycle-independent application surfaces.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - application files remain under
  `applications/Agent_Red`.
- `SPEC-1825` - the self-service deployment pipeline requires a functional
  test-host verification stage.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires
  executable build, dependency, and test-host evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the correction must preserve
  platform behavior, concurrent work, credentials, and unrelated harness
  operation.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - changed Python files require lint,
  formatting, compilation, and focused test evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227` established the
  Agent Red readiness program, Phase 1 scope, application-isolation contract,
  and app-root minimization foundation.
- `DELIB-202666274` records the active project-scoped modernization authority
  and its non-bypass boundaries.
- `DELIB-202666694` records the initial WI-5381 GO and confirms that
  `SPEC-1825` keeps the test-host surface live.
- `bridge/gtkb-wi5381-agent-red-build-root-self-containment-003.md` identified
  the stale operative-verdict evidence, unfinalized predecessor, and missing
  destructive authority.
- `bridge/gtkb-wi5381-agent-red-build-root-self-containment-004.md` required
  either exact destructive authority or a coherent non-destructive revision.
- Historical cleanup commit `6e25fbe16a9a54e34ce464d77e509242e70270a8`
  preserves the deleted test-host implementation and stale-artifact rationale;
  it is reconstruction evidence, not authority to copy stale behavior blindly.
- WI-5392 and WI-5405 own the shared portability-fixture and source-read guard
  corrections. WI-5435 owns platform release-gate command path correction.

## Owner Decisions / Input

The active project authorization is
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`,
owner decision `DELIB-202666274`. It permits bridge, source, test,
configuration, documentation, metadata, runtime-state, and governance-evidence
work for this project while forbidding destructive cleanup, dispatcher
mutation, Git commit/history/push, credential lifecycle, deployment, release,
and external-system mutation.

No new owner decision is required because this revision removes every
destructive operation. It neither requests nor infers authority to delete the
six root legacy files. Exact mechanical finalization remains a separate
post-VERIFIED operation.

## Findings Addressed

### P1 - Operative GO lacked detector-recognized verification evidence

Response: corrected in proposal scope. The specification-derived verification
section below maps every governing requirement to concrete commands and
expected results. Any new GO must carry a detector-recognized
`## Specification-Derived Verification` section with its independently
observed preflight results.

### P1 - WI-5392 was not committed as the shared-test predecessor

Response: the shared portability test is removed from WI-5381 `target_paths`.
WI-5381 therefore has no implementation overlap with WI-5392 or WI-5405 and
may begin after a fresh GO, claim, and implementation-start packet. WI-5392 and
WI-5405 remain dependencies of the final combined frozen portability evidence,
not prerequisites for creating application-owned build surfaces.

### P1 - Six root deletions lacked exact destructive authority

Response: all six root paths and all deletion acceptance criteria are removed.
The implementation may read committed or historical files as reconstruction
evidence but may mutate only the 18 declared application-owned targets. Root
cleanup, compatibility retirement, and authority designation are not claimed
by WI-5381.

## Proposed Scope

1. Capture pre-implementation hashes for the three existing targets
   (`.dockerignore`, `.gtkb-app-isolation.json`, and
   `tests/test_host/test_build_contract.py`) and verify that the other fifteen
   targets are absent before writing.
2. Reconstruct the production, test, and local dependency manifests from
   historical requirements, then reconcile every line against current Agent Red
   imports and test-host needs. Keep production dependencies separate from test
   and local tooling.
3. Add an application-local `pyproject.toml` that builds and tests from
   `applications/Agent_Red`, discovers the current `src` and `test_host`
   packages, and gives Ruff/pytest/security tooling an application-owned
   configuration surface.
4. Create application-relative production, test-host, UI-overlay, and compose
   container contracts. Populate `.dockerignore` so required source,
   configuration, tests, project metadata, and test-host inputs remain in the
   build context while generated, secret, and cache material remain excluded.
5. Restore the five test-host modules from the last tracked implementation,
   then repair only current incompatibilities proven by application-local tests,
   imports, security checks, or container-contract checks. Test execution must
   not require live credentials, cloud writes, deployment, or external systems.
6. Add the application-local manual test-host workflow with
   `applications/Agent_Red` as its build context and no GT-KB-root path
   dependency.
7. Add `scripts/sync-admin-env.ps1` under the application root. It must derive
   its default root from its own location, support a temporary application-root
   override for deterministic testing, consume only the selected
   application-local env file, write only expected application admin env
   targets, avoid printing secret values or prefixes, and fail clearly on
   missing input.
8. Extend the existing build-contract test to prove Docker, requirements,
   project, workflow, test-host, and environment-sync paths are application
   relative. Exercise environment sync against a temporary fake application
   root and synthetic non-secret fixture values.
9. Register every new top-level application artifact exactly once in
   `.gtkb-app-isolation.json`, update the `.dockerignore` registry rationale,
   and preserve all unrelated registry entries.
10. Run focused application tests and static checks. After WI-5392 and WI-5405
    are finalized separately, run the combined frozen portability lane as
    release-candidate integration evidence without changing its files.

## Explicit Exclusions

- No mutation or deletion of `.dockerignore`, `Dockerfile`,
  `Dockerfile.test`, `Dockerfile.ui`, `docker-compose.yml`, or
  `.github/workflows/build-test-host.yml` at the GT-KB root.
- No mutation of root `pyproject.toml`, root requirements, root
  `scripts/sync-admin-env.ps1`, `scripts/release_candidate_gate.py`,
  `scripts/session_self_initialization.py`, or any platform test.
- No mutation of the WI-5392/WI-5405 portability targets, WI-5435 release-gate
  targets, admin package manifests, production credentials, environment files,
  generated admin env files, database, dispatcher, TAFE, routing, roles,
  eligibility, harnesses, Git index/history/remotes, deployment, or release.
- No claim that the six retained root legacy files are deleted, retired, or
  part of WI-5381 finalization.

## Specification-Derived Verification

| Requirement | Verification command / evidence | Expected result |
| --- | --- | --- |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001`; Agent Red placement/conformance specs | `python -m pytest applications/Agent_Red/tests/test_host -q --tb=short --rootdir=applications/Agent_Red` | All test-host API, runner, suite, dispatch, Cosmos mock, SPA, and build-contract tests collect and pass from the application root without a GT-KB-root import. |
| `SPEC-1825` | Import `test_host.main`, `test_host.runner`, `test_host.suites`, and `test_host.cosmos_writer`; execute the existing test-host suite with external clients mocked. | The required self-service verification service is importable, suite routing is coherent, and no live credential or cloud write is required. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Run the app-root minimization validator against the live Agent Red root and a relocated copy. | Every new top-level entry has one exact bucket-A purpose or bucket-B tool justification; no unmatched entry appears. |
| Build/dependency self-containment | Run the build-contract test, `python -m build applications/Agent_Red`, dependency-manifest consistency checks, and `docker compose -f applications/Agent_Red/docker-compose.yml config --quiet` when the installed Docker CLI supports compose config. | Build metadata, requirements, Docker COPY sources, compose contexts, workflow paths, and package discovery resolve only inside the application root. |
| Environment-sync self-containment | Execute the application script from each admin package path and against a temporary synthetic application root via the build-contract test. | All three existing package references resolve to the application-owned script; only temporary application admin env targets are written; output contains no synthetic secret values or prefixes. |
| `SPEC-CODE-QUALITY-CHECKLIST-001`; non-impairment | Run Ruff lint and Ruff format checks on all changed Python files, `py_compile` on all five test-host modules, PowerShell parser validation on the sync script, YAML/JSON/TOML parsers on new configuration, and `git diff --check` on all targets. | Every check passes; exact diff contains only the 18 approved application targets. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | After separate WI-5392/WI-5405 closure, run the exact frozen Agent Red portability command and the non-deploying modernization RC gate. | The relocated application carries and exercises the same application-owned build/test-host contract; no original-host read or deploy occurs. |
| Bridge/project authority specs | Re-run applicability and clause preflights; validate the current GO-derived implementation-start packet and exact target inventory. | No missing required/advisory spec, no blocking clause gap, and no mutation outside the approved targets. |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5381; SPEC-1825; live missing Agent Red build/dependency/test-host/sync surfaces",
  "canonical_authority": "ADR-APPLICATION-ISOLATION-CONTRACT-001; DCL-APP-ROOT-MINIMIZATION-001; SPEC-1825",
  "primary_route": "applications/Agent_Red-owned build, dependency, workflow, test-host, and environment-sync surfaces",
  "before_behavior": "Agent Red tests and admin package scripts reference application-local build and sync surfaces that do not exist, while application execution depends on lifecycle artifacts outside its root.",
  "after_behavior": "Agent Red builds, imports, tests, composes, and synchronizes admin environment configuration from its own root without mutating or reading GT-KB-root application surfaces.",
  "self_descriptive_naming": "Dockerfile.test, build-test-host.yml, test_host, requirements-test.txt, and sync-admin-env.ps1 state their application-owned purpose directly.",
  "obsolete_guidance_disposition": "The application .dockerignore placeholder is replaced by the executable contract; retained root legacy files remain outside this non-destructive slice.",
  "history_preservation": "Historical cleanup, prior GO/NO-ACTION/NO-GO, WI-5392/WI-5405/WI-5435 ownership, implementation evidence, and independent verdict remain separately traceable.",
  "baseline": {
    "missing_targets": 15,
    "existing_targets": 3,
    "test_host_collection": "fails because test_host package is absent",
    "admin_sync": "three package scripts resolve a missing application-owned script"
  },
  "expected_result": {
    "missing_targets": 0,
    "test_host": "application-local suite imports and passes without external credentials",
    "build": "metadata, Docker, compose, workflow, and dependencies resolve from applications/Agent_Red",
    "sync": "credential-safe temporary-root execution passes"
  },
  "rollback": {
    "instructions": "Use a governed successor to restore the three pre-existing target hashes and remove only the fifteen WI-5381-created application paths under exact destructive authority.",
    "verification": "rerun test-host, build-contract, minimization, parser, and relocated portability checks"
  },
  "hard_invariants": [
    "all implementation paths remain under applications/Agent_Red",
    "no root legacy file or platform test changes",
    "no live credentials, cloud writes, deployment, or release",
    "no dispatcher, TAFE, routing, role, eligibility, or harness mutation",
    "no Git staging, commit, push, or history mutation by Prime Builder",
    "concurrent worktree bytes outside exact targets are preserved"
  ],
  "fail_closed_conditions": [
    "missing fresh independent GO, claim, or implementation-start packet",
    "any approved target has unexpected pre-start dirt",
    "application build or test resolves a GT-KB-root dependency",
    "sync script reads root .env.local, writes root admin, or emits secret material",
    "test-host verification requires live credentials or external systems",
    "any excluded path changes"
  ],
  "essential_context_preservation": "Retain application-isolation authority, SPEC-1825 test-host need, exact root-to-application reconstruction provenance, WI ownership boundaries, and frozen portability evidence."
}
```

## Acceptance Criteria

1. All 15 previously absent application targets exist, and the three existing
   targets preserve unrelated bytes while implementing the approved contract.
2. Agent Red dependency, Python project, Docker, compose, workflow, test-host,
   and environment-sync surfaces resolve from `applications/Agent_Red`.
3. The application isolation registry exactly covers every new top-level
   artifact, and the app-root minimization validator passes.
4. All application test-host tests collect and pass without live credentials,
   cloud writes, deployment, or original-root imports.
5. The environment-sync script passes a temporary-root execution test, writes
   only expected temporary admin targets, and reveals no secret values or
   prefixes.
6. Application package build, configuration parsers, PowerShell parser, Ruff
   lint/format, Python compilation, and diff checks pass.
7. No excluded root, platform test, release-gate, session-start, dispatcher,
   TAFE, harness, database, credential, deployment, release, or Git state is
   mutated.
8. After separate WI-5392/WI-5405 closure, the frozen combined portability lane
   proves the relocated application carries the build/test-host contract.
9. Independent VERIFIED and exact mechanical finalization occur before WI-5381
   is treated as complete.

## Pre-Filing Preflight Subsection

Candidate-content preflights executed against this complete revision:

- `scripts/bridge_applicability_preflight.py --bridge-id
  gtkb-wi5381-agent-red-build-root-self-containment --content-file
  <this-revision> --json` returned `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`, and no blocking
  errors.
- The preflight reported expected non-blocking missing-parent warnings for the
  new application workflow and five new `test_host` modules. All declared
  targets remain below `applications/Agent_Red`.
- `scripts/adr_dcl_clause_preflight.py --bridge-id
  gtkb-wi5381-agent-red-build-root-self-containment --content-file
  <this-revision>` returned exit 0 with 5 clauses evaluated, 4 `must_apply`,
  zero mandatory evidence gaps, and zero blocking gaps.
- Current scope inspection found all fifteen create targets absent and all three
  existing targets clean in the worktree before implementation.

## Risk And Rollback

The largest technical risk is restoring a historically coherent but currently
stale test-host or dependency set. Current imports, credential-free unit tests,
package building, parser checks, and container-contract tests therefore govern
the result rather than historical byte identity alone. A second risk is
accidentally retaining a root-relative path inside a copied build surface; the
build-contract and relocated-app checks must search and execute from the
application root.

Rollback requires a governed successor: restore the exact three pre-start
target hashes and remove only the fifteen files created by WI-5381 under exact
destructive authority. No rollback may alter the retained root legacy files,
foreign worktree state, bridge history, dispatcher/TAFE state, credentials, or
Git history.

## Bridge Filing

File through the governed revision helper. Deterministic TAFE routing remains
external; this filing does not contact a harness, inspect or configure routing,
or mutate dispatcher eligibility.

## Recommended Commit Type

`feat:` - this adds the missing application-owned production/test build and
self-service verification capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
