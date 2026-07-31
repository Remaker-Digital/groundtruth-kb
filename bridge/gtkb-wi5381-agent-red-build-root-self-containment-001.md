NEW

# WI-5381 - Make Agent Red build and test-host surfaces self-contained

bridge_kind: prime_proposal
Document: gtkb-wi5381-agent-red-build-root-self-containment
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5381

target_paths: [".dockerignore", "Dockerfile", "Dockerfile.test", "Dockerfile.ui", "docker-compose.yml", ".github/workflows/build-test-host.yml", "applications/Agent_Red/.dockerignore", "applications/Agent_Red/.gtkb-app-isolation.json", "applications/Agent_Red/Dockerfile", "applications/Agent_Red/Dockerfile.test", "applications/Agent_Red/Dockerfile.ui", "applications/Agent_Red/docker-compose.yml", "applications/Agent_Red/pyproject.toml", "applications/Agent_Red/requirements.txt", "applications/Agent_Red/requirements-test.txt", "applications/Agent_Red/requirements-local.txt", "applications/Agent_Red/.github/workflows/build-test-host.yml", "applications/Agent_Red/test_host/__init__.py", "applications/Agent_Red/test_host/cosmos_writer.py", "applications/Agent_Red/test_host/main.py", "applications/Agent_Red/test_host/runner.py", "applications/Agent_Red/test_host/suites.py", "applications/Agent_Red/tests/test_host/test_build_contract.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_modernization_agent_red_portability.py"]

implementation_scope: Agent Red build-root migration, required test-host restoration, release-gate correction, and frozen portability evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Complete the unfinished Agent Red infrastructure migration so every production
build, dependency, test-host, and build-workflow surface belongs to the Agent
Red application lifecycle. The current platform root still contains explicitly
Agent Red Docker and workflow files, while the application root contains only a
placeholder Docker ignore file and lacks Python dependency, project, container,
and test-host surfaces. The surviving test-host container and contract test are
therefore not buildable from the application root.

The missing test-host package must not be dismissed as obsolete. `SPEC-1825`
requires the self-service Provider Console deployment pipeline to execute its
verification stage against test-host infrastructure. The five-file service was
removed in an April cleanup as stale, but the implemented specification, manual
build workflow, test-host Dockerfile, and build-contract test all continued to
depend on it. Restore the last tracked implementation into the application root,
then update it only as needed to pass current application-local tests and
security checks.

The frozen portability suite also has one live failure: its source-host audit
guard treats the relocated test host as forbidden whenever both are inside the
governed root. Correct the guard to deny original-source reads while explicitly
allowing the relocated host, and extend the proof to cover application-local
build/dependency/test-host surfaces. This proposal is hard-sequenced after
WI-5392 is independently VERIFIED and mechanically finalized because that item
owns an earlier hunk in the same portability test file.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the hosted application remains
  inside the canonical applications namespace; the later isolation contract
  refines its earlier directory-only portability assumptions.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - application-specific build,
  runtime, release, and verification artifacts belong to the application root
  and must remain portable with the application subtree.
- `DCL-APP-ROOT-MINIMIZATION-001` - every new top-level application artifact
  requires an exact registry entry and application-owned purpose.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - Agent Red remains a separate adopter
  lifecycle; platform release evidence may validate it without treating its
  files as platform-owned.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - Agent Red files remain within
  the canonical hosted application root.
- `SPEC-1825` - the self-service deployment pipeline requires a functional
  test-host verification stage.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires
  executable gate and regression evidence, not surviving file names.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the migration must preserve
  platform tests, application behavior, and unrelated harness operation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization does
  not waive GO, claim, start, verification, destructive, or Git-operation
  gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live project
  authority must be rechecked before protected mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - all relevant
  application-isolation and release requirements are linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, work
  item, and exact target set are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each linked requirement
  has executable verification below.
- `GOV-STANDING-BACKLOG-001` - WI-5381 durably owns this release blocker.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - historical deletion evidence,
  implementation, test results, review, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the stale cleanup classification and
  continued live dependencies require an explicit corrective lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the discovered contradiction is
  corrected through governed work rather than hidden by a fixture waiver.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` - establishes the hosted
  but lifecycle-independent Agent Red root.
- `DELIB-20265219`, `DELIB-20265220`, and `DELIB-20265227` - establish the Agent
  Red readiness program, application isolation contract, and minimization
  vocabulary.
- Owner modernization directive, 2026-07-15 through 2026-07-16 - deliver the
  frozen release candidate, record defects as hygiene work, and continue
  implementation without weakening bridge or mechanical controls.
- Historical cleanup commit `6e25fbe16a9a54e34ce464d77e509242e70270a8`
  - preserves the prior five-file test-host deletion and its stale-artifact
  rationale; this proposal corrects that classification because `SPEC-1825`
  and surviving executable surfaces still require the service.
- WI-5384 - supplies the committed frozen portability baseline.
- WI-5392 - owns the earlier portability-fixture correction and must be
  finalized before WI-5381 begins.

## Owner Decisions / Input

No new product-policy decision is required. The owner authorized the full
modernization program and explicitly requires production-ready acceptance
evidence. Exact removal of the six remaining legacy root build/workflow files
is a destructive mechanical operation and must still receive path-specific
authority after independent GO; this proposal does not itself execute or waive
that gate. Git staging, commit, push, deployment, release, credentials, TAFE,
dispatcher, routing, harness role, and eligibility changes remain excluded.

## Requirement Sufficiency

Existing requirements are sufficient. The operative application-isolation,
self-service verification, app-root registry, and governed release-evidence
requirements already determine the required outcome.

## Proposed Scope

1. Fail closed unless WI-5392 is independently VERIFIED and mechanically
   finalized in the committed parent.
2. Reconstruct the three application dependency manifests from their last
   tracked versions, reconcile them against current imports, and add a minimal
   application-local Python project configuration for tests and security tools.
3. Move the production, test-host, UI-overlay, compose, Docker-ignore, and
   manual test-host workflow contracts into the application root; rewrite every
   build-context path to be application-relative.
4. Restore the five previously tracked test-host modules into the application
   root, then repair only incompatibilities demonstrated by current tests,
   imports, or security checks.
5. Update the application isolation registry for every new top-level artifact
   and preserve its exact minimization semantics.
6. Make the non-deploying platform release gate audit the application-local
   dependency and Python configuration surfaces while keeping platform checks
   platform-scoped.
7. Correct the portability source-read guard so original-source reads remain
   denied but an in-root relocated host is allowed; prove the relocated
   application contains and can load the build/test-host contract.
8. Remove the six legacy root build/workflow files only under explicit
   path-specific destructive authority. Do not stage, commit, push, deploy, or
   alter credentials as part of implementation.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `ADR-APPLICATION-ISOLATION-CONTRACT-001`; `GOV-AGENT-RED-GTKB-CONFORMANCE-001`; `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | Run the exact frozen Agent Red portability acceptance modules. | The relocated application executes clean install, upgrade, migration, rollback, operational tests, and source-read denial without depending on the original host. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Run application-root minimization and isolation regression coverage against the relocated and live application roots. | Every top-level artifact is registered with bucket A purpose or justified bucket B metadata; no legacy platform-root dependency is accepted. |
| `SPEC-1825` | Collect and run the application build-contract test, import every test-host module, and exercise the test-host health/configuration path without external credentials. | The self-service verification service is importable, its suite registry is coherent, and the Docker/workflow contract references only application-local files. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Run the focused release-gate test module and then the non-deploying modernization release-candidate gate. | Dependency audit, static analysis, container-contract, portability, and modernization checks consume the correct lifecycle surfaces and pass without deployment. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run exact platform scope, Agent Red portability, app-root minimization, and release-gate regressions; inspect the exact target diff. | Platform configuration and tests remain platform-owned, Agent Red remains portable, and no harness/dispatcher/TAFE behavior changes. |
| Bridge and authorization requirements | Run applicability and clause preflights before GO and VERIFIED; require live claim/start evidence and independent implementation review. | Proposal, implementation report, verdict, and mechanical finalization form one traceable authorized chain. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5381; frozen AT-AGENT-RED-PORTABILITY failure on 2026-07-17; historical test-host deletion commit 6e25fbe16a9a54e34ce464d77e509242e70270a8; SPEC-1825","canonical_authority":"ADR-APPLICATION-ISOLATION-CONTRACT-001; SPEC-1825; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"application-root-owned build, dependency, workflow, and test-host surfaces with platform release-gate validation","before_behavior":"Agent Red build files remain at the platform root, application-local dependency and test-host surfaces are absent, the test-host contract cannot collect, and the portability guard rejects its own relocated host.","after_behavior":"Agent Red carries a self-contained production/test build and verification contract, platform gates validate it through explicit adopter scope, and the relocated application runs without original-host reads.","self_descriptive_naming":"Agent_Red application-relative paths and test_host module names describe the owning lifecycle directly.","obsolete_guidance_disposition":"Legacy platform-root build/workflow files are removed only under exact destructive authority; placeholder migration guidance is replaced by the implemented application-local contract.","history_preservation":"The April cleanup commit, surviving dependent surfaces, WI-5381 finding, WI-5392 predecessor, implementation evidence, and independent verdict remain separately traceable.","baseline":{"portability":"1 failed, 71 passed","test_host":"five modules absent after stale cleanup while SPEC-1825 remains implemented","build_root":"six Agent Red build/workflow files remain at the platform root"},"expected_result":{"portability":"72 passed","test_host":"application-local modules import and contract tests pass","release_gate":"application and platform lifecycle checks resolve to their own roots"},"rollback":{"instructions":"Use a governed successor to restore the exact pre-implementation target bytes; do not recreate the split platform-root application dependency as the steady state.","verification":"rerun portability, app-root minimization, test-host contract, and release-gate regressions"},"hard_invariants":["WI-5392 committed predecessor","Agent Red remains under applications/Agent_Red","no original-source dependency in relocated proof","no deployment or credential access","no dispatcher, TAFE, routing, role, eligibility, or harness mutation","all concurrent worktree bytes outside exact authorized hunks are preserved"],"fail_closed_conditions":["WI-5392 not mechanically finalized","missing GO, claim, start, or independent verification","path-specific destructive authority absent for legacy removals","test-host requires external credentials during verification","platform gate silently treats application files as platform-owned","any harness or dispatch state changes"],"essential_context_preservation":"Retain application-isolation authority, SPEC-1825 verification requirement, historical deletion rationale, root-to-application path mapping, portability source-read denial, and exact frozen acceptance results."}
```

## Acceptance Criteria

1. WI-5392 is the committed predecessor for the shared portability test.
2. Every Agent Red production/test build, dependency, workflow, and test-host
   surface resolves from the application root.
3. The application isolation registry exactly covers all new top-level entries.
4. The test-host modules import and the application build-contract tests pass
   without external credentials or deployment.
5. The exact frozen Agent Red portability command reports 72 passed.
6. The non-deploying modernization release gate audits application-local
   dependency and Python configuration surfaces.
7. No Agent Red build or test-host surface remains authoritative at the
   platform root after path-specific destructive authority is exercised.
8. No harness, dispatcher, TAFE, routing, role, eligibility, credential,
   deployment, staging, commit, push, or unrelated worktree state is changed.
9. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The main risk is reviving a stale test-host implementation without reconciling
it to current application code. The implementation therefore restores the last
tracked modules only as a reviewable baseline and requires current import,
contract, security, and credential-free health evidence. Build-context rewrites
can also omit required artifacts; contract tests must enumerate every source.
Rollback is an exact governed restoration of target bytes followed by the same
focused tests. A rollback may restore availability during repair, but the split
platform-root application lifecycle is not an acceptable release-candidate end
state.

## Bridge Filing

File through the governed Codex non-bypass helper. The numbered bridge file
chain is append-only. Deterministic TAFE routing remains external; this filing
does not inspect queue state, contact a harness, or configure routing.

## Recommended Commit Type

`fix` - restore the required self-service verification service and complete the
Agent Red build-root isolation migration.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
