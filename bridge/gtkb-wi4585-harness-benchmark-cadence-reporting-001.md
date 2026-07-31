NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1868-a18f-7c21-a6a0-3346bcfdf7bd
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop automation Auto-builder; role=prime-builder; approval_policy=never; filesystem=unrestricted
author_metadata_source: auto-builder explicit metadata; CODEX_THREAD_ID fallback

# Implementation Proposal - WI-4585 Harness Benchmark Cadence Reporting

bridge_kind: prime_proposal
Document: gtkb-wi4585-harness-benchmark-cadence-reporting
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4585

target_paths: ["scripts/benchmarks/harness_quality_reporting.py", "scripts/benchmarks/cli.py", "platform_tests/scripts/test_harness_quality_reporting.py", "platform_tests/scripts/test_harness_benchmark_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the next Harness Testing and Quality Benchmarking slice for `WI-4585`: a read-only cadence/reporting layer that consumes existing benchmark run, scoring, telemetry, manifest, and CLI surfaces to produce advisory benchmark reports. The slice should make smoke, full-quality, and adjudicated-calibration tiers visible in generated payloads and markdown summaries, include trend/comparison inputs where available, and emit remediation/backlog suggestions without mutating MemBase, bridge state, dispatcher rules, ranking, or harness eligibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4585`. The work adds advisory reporting primitives and CLI access for benchmark cadence outputs. It does not schedule autonomous benchmark runs, activate benchmark-informed dispatch enforcement, or write backlog/project records from benchmark findings.

## Requirement Sufficiency

Existing requirements are sufficient. The verified Harness Testing and Quality Benchmarking umbrella defines Slice 7 / `WI-4585` as tiered cadence, benchmark run reports, dashboard summaries, trend views, and advisory remediation/backlog suggestions. The predecessor slices for manifest/rubric, fixture corpus, runner, smoke probes, scoring, telemetry, and Dispatcher/Bridge CLI exposure are already VERIFIED or resolved in MemBase, so this proposal can build on their output contracts without adding new owner decisions.

## In-Root Placement Evidence

All target paths are root-relative GT-KB platform files. No `applications/Agent_Red/` adopter code, credentials, cloud resources, production deployment, or out-of-root workstation state is in scope.

## Specification Links

- `SPEC-1529` - benchmark/performance-baseline anchor; this slice extends benchmark reporting conventions to harness-quality cadence outputs.
- `GOV-STANDING-BACKLOG-001` - `WI-4585` is the active MemBase-backed backlog item being processed.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation must remain inside the active snapshot-bound project authorization for `WI-4585`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test edits require this bridge proposal, GO, work-intent, and implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms this platform benchmark-reporting work stays outside adopter application scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal declares project authorization, project, work item, and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposal cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map linked specs to executed tests before VERIFIED.

## Prior Deliberations

- `bridge/harness-testing-quality-benchmarking-umbrella-002.md` - approved/revised umbrella sequencing identifies `WI-4585` as the cadence/reporting/remediation slice.
- `bridge/harness-testing-quality-benchmarking-umbrella-005.md` - umbrella implementation report confirms the first slice was filed separately and project sequencing was preserved.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` - VERIFIED manifest/rubric predecessor establishes tiers, evidence schema, challenge families, and CLI contract expectations.
- `bridge/gtkb-harness-benchmark-fixture-corpus-005.md` - VERIFIED fixture-corpus predecessor establishes isolated benchmark challenge material.
- `bridge/gtkb-harness-benchmark-cross-role-dispatch-runner-006.md` - VERIFIED runner predecessor establishes synthetic benchmark evidence records.
- `bridge/gtkb-harness-benchmark-dispatcher-bridge-cli-004.md` - VERIFIED CLI predecessor establishes Dispatcher/Bridge CLI benchmark access.
- `DELIB-20263447` - owner decision requiring benchmark execution through Dispatcher/Bridge CLI surfaces where sensible.
- `DELIB-20265586` - owner-approved bounded project authorization snapshot for current open project members.

## Owner Decisions / Input

- `DELIB-20263447` - benchmark operations should be reachable through Dispatcher/Bridge CLI surfaces, with governed skills delegating to CLI where sensible.
- `DELIB-20265586` - active snapshot-bound project authorization covering `WI-4585` under the Harness Testing and Quality Benchmarking project.

## Proposed Scope

- Add `scripts/benchmarks/harness_quality_reporting.py` with read-only report builders that consume benchmark run payloads, scored evidence, telemetry-shaped records, and manifest tier definitions.
- Extend `scripts/benchmarks/cli.py` with a cadence/reporting command that writes deterministic JSON and markdown advisory outputs under `.gtkb-state/benchmarks/<run_id>/` or prints them when requested.
- Surface smoke, full-quality, and adjudicated-calibration tier summaries separately so cheap probes, full suites, and calibration runs can be reviewed without conflating their cadence or confidence levels.
- Include trend-ready comparison fields when previous run payloads are supplied, but keep trend computation deterministic and local to supplied runtime artifacts.
- Emit remediation suggestions as advisory records only. Suggestions may name candidate work-item titles or bridge topics, but must not create, update, resolve, or reprioritize MemBase records.
- Add focused tests for tier separation, advisory-only remediation output, CLI behavior, deterministic rendering, and no dispatcher-routing mutation.

## Out Of Scope

- Autonomous scheduling, Windows task registration, service daemons, or always-on benchmark monitors.
- Dispatcher ranking, eligibility, routing, or policy enforcement changes. Those remain disabled unless a later owner-approved proposal activates them.
- Backlog/project/MemBase mutation from benchmark findings.
- Live provider calls, credential reads, cloud-service operations, or production deployment.
- Agent Red application changes.
- Redesigning the already VERIFIED manifest, fixture corpus, runner, scoring, telemetry, or CLI foundations except for narrow integration points required by the report command.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-1529` | Run focused benchmark reporting tests proving deterministic JSON/markdown outputs preserve benchmark run conventions and include tiered cadence summaries. |
| `GOV-STANDING-BACKLOG-001` | Confirm `gt backlog show WI-4585 --json` still identifies this active work item and that the implementation report cites it. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4585-harness-benchmark-cadence-reporting` after GO and confirm the packet authorizes only declared target paths and `WI-4585`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use GO, work-intent, implementation-start packet, and append-only bridge report before protected source/test edits. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assert target paths stay under platform `scripts/` and `platform_tests/`, not `applications/Agent_Red/` or other adopter scopes. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance preflight must pass with project authorization, project, work item, and target paths present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge compliance preflight must recognize concrete Specification Links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map every linked spec to exact command evidence and observed results. |

## Acceptance Criteria

- A read-only reporting module can build deterministic cadence summaries for smoke, full-quality, and adjudicated-calibration benchmark tiers from existing benchmark payload shapes.
- The CLI exposes the cadence/reporting surface without bypassing existing benchmark CLI conventions.
- Generated advisory remediation suggestions are explicitly non-mutating and do not alter dispatcher routing, harness eligibility, bridge files, MemBase, project records, or backlog items.
- Focused tests cover tier separation, deterministic output, advisory-only remediation records, CLI command behavior, and the absence of dispatcher-routing mutations.
- Implementation report includes exact focused pytest and ruff evidence.

## Risks / Rollback

Risk is moderate because benchmark outputs may influence human decisions. The control is to keep this slice read-only and advisory-only: it can report and suggest, but cannot enforce, schedule, or mutate authority surfaces.

Rollback is a revert of the reporting module, CLI extension, and focused tests. Bridge files remain append-only audit evidence.

## Files Expected To Change

- `scripts/benchmarks/harness_quality_reporting.py`
- `scripts/benchmarks/cli.py`
- `platform_tests/scripts/test_harness_quality_reporting.py`
- `platform_tests/scripts/test_harness_benchmark_cli.py`

## Recommended Commit Type

feat
