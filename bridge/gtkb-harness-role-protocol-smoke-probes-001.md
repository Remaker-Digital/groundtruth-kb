NEW

# Implementation Proposal - Harness Role And Protocol Smoke Probes

bridge_kind: prime_proposal
Document: gtkb-harness-role-protocol-smoke-probes
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-24 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef2e1-2bb1-7331-8dfd-6201623ff271
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner init keyword `::init gtkb pb`; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4582

target_paths: ["scripts/benchmarks/harness_role_protocol_smoke.py", "scripts/benchmarks/cli.py", "platform_tests/scripts/test_harness_role_protocol_smoke.py", "bridge/gtkb-harness-role-protocol-smoke-probes-*.md"]

implementation_scope: benchmark_smoke_probe, benchmark_cli_registration, focused_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4582 as a cheap, deterministic harness role/protocol smoke benchmark. The benchmark will inspect existing in-root GT-KB authority surfaces and report whether the current checkout exposes the expected anchors for role adoption, bridge protocol actionability, implementation-start safety, protected mutation boundaries, role-authority citation, and direct-mutation refusal.

This is intentionally not the deferred cross-role dispatch runner and not the benchmark fixture corpus. It will not launch harnesses, synthesize dispatch envelopes, emit full runner evidence records, adjudicate scoring, map telemetry, alter durable role assignment, write live bridge/backlog/spec challenge state, or affect dispatcher ranking. It is a read-only smoke probe that can run frequently through the existing benchmark CLI while later runner/fixture/scoring/telemetry slices remain parked or separately reviewed.

## Scope And Non-Goals

In scope:

- Add `scripts/benchmarks/harness_role_protocol_smoke.py` with a read-only `run(window_start, window_end, project_root=None)` benchmark module returning a `BenchmarkResult`.
- Register `harness_role_protocol_smoke` in `scripts/benchmarks/cli.py` so the existing `scripts.benchmarks.cli` and verified `gt bridge benchmark run --benchmark ...` path can invoke it.
- Score a small set of deterministic probes over in-root files such as the harness registry projection, file bridge protocol rule, implementation authorization/start-gate script, project-root boundary rule, and harness-quality manifest.
- Add focused tests using temporary project roots that prove PASS and FAIL dimensions, registration, deterministic output shape, and read-only behavior.

Out of scope:

- No live dispatch to Codex, Claude Code, Antigravity, Ollama, OpenRouter, or future harnesses.
- No durable harness role assignment mutation.
- No fixture corpus generation, answer-key schema, seeded-defect files, or live bridge/backlog/spec challenge artifacts.
- No full evidence-schema emission keyed to the pending manifest amendment fields `author_model_configuration` or `FAILURE_CLASSES`.
- No scoring pipeline, adjudication, telemetry mapping, dashboard/cadence reporting, or benchmark-informed dispatcher enforcement.
- No formal GOV/SPEC/ADR/DCL/PB/REQ mutation and no promotion of `INTAKE-f8bc08a3`.

## In-Root Placement Evidence

All proposed target paths are under `E:\GT-KB`:

- `E:\GT-KB\scripts\benchmarks\harness_role_protocol_smoke.py`
- `E:\GT-KB\scripts\benchmarks\cli.py`
- `E:\GT-KB\platform_tests\scripts\test_harness_role_protocol_smoke.py`
- `E:\GT-KB\bridge\gtkb-harness-role-protocol-smoke-probes-*.md`

The benchmark itself must only read in-root project files. Any benchmark run output created by the existing benchmark CLI remains regenerable runtime evidence under `E:\GT-KB\.gtkb-state\benchmarks\`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, implementation report, and eventual verdict must use the dispatcher/TAFE-backed numbered bridge file chain; the benchmark probes must respect role/status actionability and must not restore retired aggregate queue authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation-targeting proposal carries the required Project Authorization, Project, Work Item, and `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing benchmark, dispatch, role, bridge, backlog, root-boundary, and verification specifications before implementation begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must carry forward these links and map each to executed focused tests plus lint and format evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4582 is the active MemBase work item and project member that authorizes this slice selection.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the owner supplied bounded project implementation authorization for the seven snapshot-bound open member WIs, including WI-4582.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - this slice preserves the separation between synthetic benchmark modes and durable dispatch/role state; it does not fire envelopes.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - the smoke probe is a precursor to structured harness benchmark dispatch and must preserve authorization/activity-gate/specialization boundaries rather than bypass them.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - live bridge authority remains TAFE/dispatcher state plus versioned bridge files; probes must not create alternate state.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role checks must distinguish durable harness role assignment from transcript-defined interactive session role authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role-adoption probes should verify that deterministic role-resolution rules are discoverable and cited by the authority surfaces.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - role-adoption probes must not confuse benchmark/interview role behavior with durable registry mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` - implementation, tests, and runtime dependency reads must remain inside `E:\GT-KB`.
- `SPEC-1529` - existing benchmark surfaces establish the convention that benchmark modules return structured `BenchmarkResult` values and benchmark runs emit JSON plus markdown runtime outputs.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - benchmark observations are artifact surfaces that may later inform advisory/backlog artifacts; this slice does not mutate formal artifacts.

## Pre-Filing Self-Check

Draft preflights were run against `.gtkb-state/propose-drafts/gtkb-harness-role-protocol-smoke-probes-001.md` before filing:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-role-protocol-smoke-probes --content-file .gtkb-state\propose-drafts\gtkb-harness-role-protocol-smoke-probes-001.md --json
```

Observed:

- packet_hash: `sha256:f81e2ec9abd2e4cd92188150dc54805a84d14c7c5a79aca7270704a13cbc0432`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-role-protocol-smoke-probes --content-file .gtkb-state\propose-drafts\gtkb-harness-role-protocol-smoke-probes-001.md
```

Observed:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

Phantom-spec sweep: every cited SPEC/GOV/ADR/DCL ID in `## Specification Links` exists in the live MemBase `specifications` table. The inline `target_paths` metadata is valid JSON and `scripts/implementation_authorization.py` extracts the four intended target globs from the inline metadata form.

## Prior Deliberations

- `DELIB-20265586` - owner decision authorizing bounded implementation for the seven current open member WIs in `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1`; this proposal uses that PAUTH and does not cover future added WIs.
- `DELIB-20263440` - full cross-role benchmark matrix; this smoke probe preserves the principle that benchmark role checks do not mutate durable role assignments.
- `DELIB-20263441` - hybrid scoring; this smoke slice covers deterministic evidence only and leaves adjudication to later scoring work.
- `DELIB-20263442` - no live external mutations; this smoke probe reads in-root files only and does not call cloud, deployment, credential, or production services.
- `DELIB-20263443` - GT-KB-native benchmark cases; this probe checks GT-KB role, bridge, implementation-start, and mutation-boundary surfaces rather than generic model tasks.
- `DELIB-20263444` - advisory-first consequences; this slice reports benchmark dimensions only and does not change dispatcher ranking or eligibility.
- `DELIB-20263445` - tiered cadence; WI-4582 implements the frequent cheap role/protocol probe tier.
- `DELIB-20263446` - isolated fixtures; this proposal avoids fixture corpus generation and treats temp test roots as isolated test fixtures only.
- `DELIB-20263447` - Dispatcher/Bridge CLI-first operation and direct-mutation probes; this slice registers the smoke benchmark with the existing benchmark CLI so the verified `gt bridge benchmark` surface can invoke it.
- `DELIB-20265071` - Loyal Opposition GO for the umbrella thread; confirms later slices need their own reviewed proposals and that benchmark probes must remain isolated from live bridge/backlog/spec authority.
- `DELIB-20265069` and `DELIB-20265070` - manifest/rubric GO and umbrella verification trail; confirm WI-4579 produced the benchmark manifest contract and left smoke probes for WI-4582.
- `bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-004.md` - WI-4587 VERIFIED the Bridge CLI benchmark wrapper; this proposal builds on that CLI surface by adding a registered benchmark module.
- `bridge/gtkb-harness-benchmark-fixture-corpus-002.md`, `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md`, `bridge/gtkb-harness-benchmark-scoring-pipeline-002.md`, and `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` - deferred sibling slices pending manifest amendment. This proposal avoids their parked evidence-schema, fixture, runner, scoring, and telemetry scopes.
- `INTAKE-f8bc08a3` - pending intake candidate for Dispatcher/Bridge CLI as the primary mutating UI. This proposal does not promote it or rely on it as a formal specification.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23` - active owner authorization for bounded implementation of the project's seven current open member WIs, including WI-4582, with allowed mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- `DELIB-20265586` - owner decision behind that PAUTH. The authorization is snapshot-bound; this proposal does not add work items and does not attempt to include future project members.
- `DELIB-20263440` through `DELIB-20263447` - owner benchmark-program decisions that define the role/protocol smoke tier, isolation, no-live-mutation boundary, CLI-first path, and advisory-first consequence model.
- No new owner decision is required for this proposal because it stays inside the active PAUTH, avoids formal-artifact mutation, avoids deployment/credential/destructive operations, and does not widen project scope.

## Requirement Sufficiency

Existing requirements sufficient.

The owner benchmark decisions, verified manifest/rubric contract, role-authority specifications, bridge protocol requirements, and bounded PAUTH above are sufficient for this narrow read-only smoke benchmark. The slice implements an executable deterministic probe over already-specified authority surfaces; it does not establish new benchmark governance, durable role semantics, dispatcher enforcement, full runner evidence schema, fixture corpus, telemetry, or adjudicated scoring.

## Proposed Change

Implement a narrow read-only benchmark module:

1. Add a `PROBES` table or equivalent deterministic definitions for role adoption, bridge protocol compliance, implementation-start safety, protected mutation boundary, required role-authority citation, and direct-mutation/CLI-first refusal.
2. Resolve a project root from the explicit `project_root` argument and read only in-root files.
3. For each probe, check for concrete anchors in existing authority surfaces, such as:
   - harness registry role coverage without durable benchmark-mode mutation;
   - file bridge protocol status/actionability boundaries;
   - implementation-start gate and work-intent claim requirements;
   - project-root/protected mutation boundary language;
   - session role authority/resolution citations;
   - harness-quality manifest direct-mutation and CLI-first challenge families.
4. Return `BenchmarkResult(benchmark_id="harness_role_protocol_smoke")` with `value` equal to the rounded fraction of passing probes and dimensions containing per-probe pass/fail details.
5. Register the module in `scripts/benchmarks/cli.py` without changing existing benchmark behavior.
6. Add focused tests that create temporary in-root fixture files, verify full-pass and degraded-fail outcomes, verify CLI module registration, and statically assert the benchmark module does not contain write/database mutation calls.

## Spec-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` | Focused tests exercise file-bridge protocol probe inputs and assert no bridge state files are written. | Smoke benchmark detects the bridge status/actionability anchors read-only. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-STANDING-BACKLOG-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-role-protocol-smoke-probes` after GO. | Implementation packet authorizes only the proposal target paths and WI-4582 under the bounded PAUTH. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`, `DCL-DISPATCH-ENVELOPE-SCHEMA-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `DCL-SESSION-ROLE-RESOLUTION-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Focused temp-root tests for role authority and harness-registry probes. | Role probes distinguish benchmark/read-only checks from durable role assignment mutation and require role-authority citations. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `.claude/rules/project-root-boundary.md`, `DELIB-20263442`, `DELIB-20263446` | Focused temp-root tests and static mutation scan over the new benchmark module. | The benchmark reads only supplied in-root files and contains no write/database mutation calls. |
| `SPEC-1529`, `DELIB-20263445`, `DELIB-20263447` | Focused tests assert `harness_role_protocol_smoke` is registered in `scripts.benchmarks.cli.BENCHMARK_MODULES` and importable with `run()`. | The cheap smoke probe can be invoked by existing benchmark CLI and verified Bridge CLI wrapper. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation report confirms outputs are runtime benchmark artifacts only and no formal artifact mutation occurred. | Artifact-oriented evidence is preserved without mutating formal GOV/SPEC/ADR/DCL/PB/REQ records. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_harness_role_protocol_smoke.py -q --tb=short` | Focused smoke benchmark tests pass. |
| Python code quality gates | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/benchmarks/harness_role_protocol_smoke.py scripts/benchmarks/cli.py platform_tests/scripts/test_harness_role_protocol_smoke.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/benchmarks/harness_role_protocol_smoke.py scripts/benchmarks/cli.py platform_tests/scripts/test_harness_role_protocol_smoke.py` | Lint and format checks pass separately. |

## Acceptance Criteria

- `scripts.benchmarks.harness_role_protocol_smoke.run()` returns a `BenchmarkResult` with `benchmark_id == "harness_role_protocol_smoke"`.
- The result value is the deterministic pass fraction across the defined role/protocol probes.
- Dimensions include per-probe status/details for role adoption, bridge protocol compliance, implementation-start safety, protected mutation boundary, role-authority citation, and direct-mutation/CLI-first refusal.
- Full fixture inputs produce value `1.0`; deliberately missing or damaged authority surfaces reduce the value and identify the failed probe.
- The benchmark is registered in `BENCHMARK_MODULES`, so it is reachable by `scripts.benchmarks.cli run --benchmark harness_role_protocol_smoke` and the verified `gt bridge benchmark run --benchmark harness_role_protocol_smoke` wrapper.
- Focused tests prove the module is read-only and does not dispatch harnesses, mutate durable role state, write live bridge/backlog/spec/MemBase state, call external services, or create benchmark fixtures outside temp test roots.
- The implementation report carries forward the linked specifications and records pytest, Ruff lint, and Ruff format-check evidence.

## Risk / Rollback

Risk is low and bounded to an additive benchmark module plus CLI registration. The main risk is over-claiming live role-dispatch coverage from static smoke probes. Mitigation: the module name, dimensions, proposal, tests, and report will state that this is a deterministic repo-surface smoke benchmark only; live synthetic dispatch remains WI-4581 scope and is currently deferred.

Rollback is a single-commit revert of the new benchmark module, the `BENCHMARK_MODULES` registration line, the focused tests, and this bridge thread's report artifact. No MemBase migration, formal artifact mutation, durable role mutation, external action, deployment, credential operation, or dispatcher-ranking recovery is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-harness-role-protocol-smoke-probes`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the proposed diff adds a net-new benchmark module, registers it in the existing benchmark CLI list, and adds focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
