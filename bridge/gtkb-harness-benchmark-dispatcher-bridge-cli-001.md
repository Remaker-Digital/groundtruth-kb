NEW

# Implementation Proposal - Harness Benchmark Dispatcher/Bridge CLI

bridge_kind: prime_proposal
Document: gtkb-harness-benchmark-dispatcher-bridge-cli
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef2e1-2bb1-7331-8dfd-6201623ff271
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner init keyword `::init gtkb pb`; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4587

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/benchmarks/cli.py", "platform_tests/scripts/test_harness_benchmark_cli.py", "bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-*.md"]

implementation_scope: cli_extension, benchmark_cli_wrapper, focused_tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the first Dispatcher/Bridge CLI surface for harness benchmark execution by adding a `gt bridge benchmark` command group that delegates benchmark run/report/compare behavior to the existing benchmark CLI module and exposes the verified harness-quality manifest validation path as a Bridge CLI use case.

This proposal is intentionally a CLI-extension slice, not a live cross-role benchmark runner. It does not implement fixture generation, synthetic harness dispatch, scoring, telemetry persistence, cadence reporting, benchmark-informed dispatcher enforcement, or the deferred manifest amendment. Those remain governed by their own work items and, for WI-4580/WI-4581/WI-4583/WI-4584, by their existing DEFERRED clear/resume condition.

## Scope And Non-Goals

In scope:

- Add a `gt bridge benchmark` Click group under the existing `gt bridge` surface.
- Delegate existing benchmark run/report/compare operations through the Bridge CLI instead of requiring direct `python -m scripts.benchmarks.cli` invocation.
- Add a harness-quality manifest validation/read command so the Dispatcher/Bridge CLI can act as the first CLI use case for the harness benchmark program before the deferred runner lands.
- Add focused CLI tests proving the bridge command reaches the benchmark module, preserves no-live-mutation boundaries, and fails safely on invalid arguments.

Out of scope:

- No live harness dispatch.
- No durable role assignment mutation.
- No fixture corpus creation.
- No scoring, telemetry write-through, cadence/reporting, dashboard, or dispatcher ranking/eligibility change.
- No change to `scripts/benchmarks/harness_quality_manifest.py`; the unresolved manifest amendment remains outside this WI and outside this PAUTH snapshot.
- No formal GOV/SPEC/ADR/DCL/PB/REQ mutation and no promotion of `INTAKE-f8bc08a3`.

## In-Root Placement Evidence

All implementation target paths are under E:\GT-KB:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\scripts\benchmarks\cli.py`
- `E:\GT-KB\platform_tests\scripts\test_harness_benchmark_cli.py`
- `E:\GT-KB\bridge\gtkb-harness-benchmark-dispatcher-bridge-cli-*.md`

Generated benchmark run outputs remain runtime evidence under `E:\GT-KB\.gtkb-state\benchmarks\` when the CLI is invoked; they are regenerable benchmark outputs, not canonical MemBase state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, implementation report, and eventual verdict must use the TAFE/dispatcher-backed numbered bridge file chain and must not restore retired aggregate queue authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation-targeting proposal carries the required Project Authorization, Project, Work Item, and `target_paths` metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing benchmark, dispatch-envelope, bridge, backlog, and verification specifications before implementation begins.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map each linked specification to executed focused CLI tests plus lint/format evidence before it can receive VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-4587 is the active MemBase work item and project member that authorizes this slice selection.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the owner supplied a bounded project implementation authorization for the seven current open member WIs, including WI-4587.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - benchmark execution belongs under governed dispatch/envelope-oriented CLI surfaces rather than ad hoc direct artifact mutation paths.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - future harness benchmark execution must preserve target, authorization, activity-gate, specialization, and singleton-dispatch semantics; this slice establishes the CLI entrypoint without firing envelopes.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - Bridge CLI benchmark commands must preserve TAFE/dispatcher/versioned bridge state authority and must not write retired queue artifacts.
- `SPEC-1529` - existing benchmark surfaces establish the project convention that benchmark runs produce structured JSON plus markdown runtime outputs under `.gtkb-state/benchmarks/`; this slice reuses that convention for the Bridge CLI wrapper.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - benchmark CLI execution and report outputs are artifact surfaces; failures may later become advisory/backlog artifacts, but this slice does not mutate formal artifacts.

## Pre-Filing Self-Check

Draft preflights were run against `.gtkb-state/propose-drafts/gtkb-harness-benchmark-dispatcher-bridge-cli-001.md` before filing:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-benchmark-dispatcher-bridge-cli --content-file .gtkb-state\propose-drafts\gtkb-harness-benchmark-dispatcher-bridge-cli-001.md --json
```

Observed:

- packet_hash: `sha256:16b62d9b97d96e653a865e29bd5bb0c7907c1ade89b3d4fc41ca3b5c3987741f`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-benchmark-dispatcher-bridge-cli --content-file .gtkb-state\propose-drafts\gtkb-harness-benchmark-dispatcher-bridge-cli-001.md
```

Observed:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

Phantom-spec sweep: every cited SPEC/GOV/ADR/DCL ID in `## Specification Links` exists in the live MemBase `specifications` table.

## Prior Deliberations

- `DELIB-20265586` - owner decision authorizing bounded implementation for the seven currently open member WIs in `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1`; this proposal uses that PAUTH and does not cover future added WIs.
- `DELIB-20263447` - owner decision requiring Harness Testing and Quality Benchmarking 1 benchmark tests to run via Dispatcher/Bridge CLI, with skills over CLI where sensible and direct artifact mutation outside governed skills or CLI access probed and barred.
- `DELIB-20263440` through `DELIB-20263446` - benchmark program decisions: full cross-role matrix, hybrid scoring, no live external mutations, GT-KB-native cases, advisory-first consequences, tiered cadence, and isolated fixtures.
- `DELIB-20265071` - Loyal Opposition GO for the umbrella thread; confirms WI-4587 is visible and matches `DELIB-20263447`.
- `DELIB-20265069` and `DELIB-20265068` - manifest/rubric GO and VERIFIED trail; confirms CLI exposure was deliberately out of WI-4579 and belongs in a later slice.
- `INTAKE-f8bc08a3` - pending intake candidate for Dispatcher/Bridge CLI as the primary mutating UI for GT-KB artifact operations. This proposal does not promote or rely on the candidate as a formal specification; it treats it as context only.
- `bridge/gtkb-harness-benchmark-fixture-corpus-002.md`, `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-002.md`, `bridge/gtkb-harness-benchmark-scoring-pipeline-002.md`, and `bridge/gtkb-harness-benchmark-telemetry-integration-002.md` - deferred sibling slices. This proposal avoids their paused manifest-amendment-dependent scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23` - active owner authorization for bounded implementation of the project's seven current open member WIs, including WI-4587, with allowed mutation classes `source`, `test_addition`, `hook_upgrade`, `cli_extension`, and `scaffold_update`.
- `DELIB-20265586` - owner decision behind that PAUTH. The authorization is snapshot-bound; this proposal does not add WIs and does not attempt to include any future project members.
- `DELIB-20263447` - owner decision that creates the CLI-first benchmark requirement for WI-4587.
- No new owner decision is required for this proposal because it stays inside the active PAUTH, avoids formal-artifact mutation, avoids deployment/credential/destructive operations, and does not widen project scope.

## Requirement Sufficiency

Existing requirements sufficient.

The owner decisions and governing artifacts above are sufficient for this bounded CLI-extension slice: `DELIB-20263447` states the CLI-first benchmark requirement; the verified harness-quality manifest already records Dispatcher/Bridge CLI requirements as manifest data; `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` and `DCL-DISPATCH-ENVELOPE-SCHEMA-001` constrain future dispatch/envelope semantics; and `DELIB-20265586` supplies bounded owner authorization for implementation under WI-4587.

New or revised requirements are not needed before implementing this slice because the implementation does not establish broad governance policy, does not promote `INTAKE-f8bc08a3`, and does not add automatic dispatcher behavior. Any future rule making Dispatcher/Bridge CLI the primary mutating UI for all GT-KB artifact operations remains outside this proposal and requires its own formal approval.

## Proposed Change

Implement a narrow CLI adapter:

1. Register `gt bridge benchmark` under the existing `bridge_group`.
2. Provide `gt bridge benchmark run`, `gt bridge benchmark report`, and `gt bridge benchmark compare` wrappers that reuse or delegate to `scripts.benchmarks.cli` behavior rather than duplicating benchmark execution logic.
3. Provide a read-only `gt bridge benchmark manifest` or equivalent command that validates and prints the existing harness-quality manifest contract, proving the harness benchmark program is reachable through Bridge CLI before the runner lands.
4. Preserve existing `scripts/benchmarks/cli.py` module invocation behavior.
5. Add focused tests using `click.testing.CliRunner` and temporary output roots/mocks where needed so tests do not mutate live `.gtkb-state/benchmarks/`.

## Spec-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` | `gt bridge benchmark --help` and focused CLI tests inspect command availability without bridge state mutation. | Bridge CLI extension is present; no retired queue artifact or versioned bridge state is written by help/manifest commands. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-STANDING-BACKLOG-001` | `python scripts/implementation_authorization.py begin --bridge-id gtkb-harness-benchmark-dispatcher-bridge-cli` after GO. | Implementation packet authorizes only the proposal target paths and WI-4587 under the bounded PAUTH. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001`, `DCL-DISPATCH-ENVELOPE-SCHEMA-001`, `DELIB-20263447` | Focused CLI tests for `gt bridge benchmark` subcommands. | CLI path exposes benchmark execution/manifest validation without live envelope firing, role mutation, or external side effects. |
| `SPEC-1529` and benchmark-output convention | Test or mock verifies the Bridge CLI wrapper delegates to the existing benchmark CLI writer path and preserves run/report/compare argument semantics. | Benchmark outputs remain structured runtime artifacts under the benchmark output path; existing benchmark CLI behavior is not broken. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_harness_benchmark_cli.py -q --tb=short` | Focused CLI tests pass. |
| Python code quality gates | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py scripts/benchmarks/cli.py platform_tests/scripts/test_harness_benchmark_cli.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py scripts/benchmarks/cli.py platform_tests/scripts/test_harness_benchmark_cli.py` | Lint and format checks pass separately. |

## Acceptance Criteria

- `gt bridge benchmark --help` lists the new benchmark command surface.
- Existing benchmark run/report/compare behavior is invokable through the Bridge CLI without removing the existing `scripts.benchmarks.cli` entrypoint.
- A harness-quality manifest validation/read command is available through the Bridge CLI and remains read-only.
- Help/manifest tests prove no live bridge/backlog/spec/MemBase mutation, no durable role mutation, no live dispatch, and no external service side effect.
- Focused tests pass under the repo venv.
- `ruff check` and `ruff format --check` pass on all touched Python files.

## Risk / Rollback

Risk is moderate-low and limited to CLI surface expansion. The main risk is duplicating benchmark CLI logic or creating an entrypoint that implies the deferred cross-role runner is live. Mitigation: implement a thin wrapper over existing benchmark CLI behavior, label live harness dispatch as out of scope, and test that manifest/help paths are read-only.

Rollback is a single-commit revert of the CLI registration/helper changes and the focused test file. No MemBase migration, role-state mutation, dispatcher-ranking change, credential action, deployment, or production application recovery is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-harness-benchmark-dispatcher-bridge-cli`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` - the proposed diff adds a net-new Bridge CLI benchmark command surface and focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
