NEW
::init gtkb lo
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - Dispatcher Next Foundation Spike

bridge_kind: implementation_report
Document: gtkb-dispatcher-next-foundation-spike
Version: 005
Responds to: bridge/gtkb-dispatcher-next-foundation-spike-004.md
Approved proposal: bridge/gtkb-dispatcher-next-foundation-spike-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617
Recommended commit type: feat(dispatcher-next):

target_paths: ["groundtruth-kb/requirements-dispatcher-next-spike.txt", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py", "platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py"]

implementation_scope: source | test | dependency_manifest | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Implementation Claim

Implemented the isolated WI-5617 foundation spike on DBOS 2.27.0 and the
official A2A SDK 1.1.1 under Python 3.14. The package is not registered with
the production CLI, daemon, TAFE, bridge router, harness registry, or any real
worker adapter.

The spike provides:

- real DBOS workflows and steps around opaque local Python subprocesses;
- a post-domain-commit/pre-DBOS-result failpoint, durable executor
  crash/restart recovery with multiple pending workflows, deterministic
  workflow IDs, exactly-once semantic operation recording, and a purpose-built
  transient retry policy capped at three total attempts;
- a strict A2A protobuf task facade covering submitted, working, completed,
  failed, and canceled lifecycles, structured artifacts, deterministic wire
  round trips, fail-closed invalid transitions, and rejection of integers
  outside protobuf `Value`'s exact IEEE-754 safe range;
- a SQLite capacity ledger that atomically acquires global, role, provider,
  model, and harness capacity in one `BEGIN IMMEDIATE` transaction, preserves
  an immutable canonical policy in database metadata, preserves permanent
  lease-ID history, emits append-only audits, and reaps expired crash leases;
- lazy package exports so `python -m
  groundtruth_kb.dispatcher_next.foundation` does not double-register DBOS
  decorators; and
- a pytest-session-finish verifier whose records use the actual invocation and
  final session exit status, and whose only outcomes are
  `adopt_dbos_a2a` and `reject_and_evaluate_hatchet`.

The final full-suite evidence selects `adopt_dbos_a2a`. A focused
manifest-only run exits nonzero with all missing predicates enumerated. Failed,
missing, duplicate, cleanup-incomplete, or caller-invented records cannot
produce adoption, and inconsistent direct `AdoptionManifest` construction
raises.

Two defects surfaced during integration and were corrected before this report:
eager package exports caused duplicate DBOS registration under `python -m`,
and concurrent domain connections each attempted to negotiate WAL mode,
creating a SQLite lock race. Exports are now lazy, and WAL/schema
initialization occurs once before workers start. The affected 16-workflow test
then passed repeatedly as part of the full suite.

An independent pre-report review found six additional acceptance-evidence
gaps. All were corrected before filing: synthetic adoption evidence, incomplete
live-state/process evidence, process-local capacity policy, a pre-commit crash
failpoint, protobuf integer precision loss, and unmeasured concurrency/cap
width. No finding remains open.

The first exact final-command attempts also caught concurrent legacy-daemon
TAFE/WAL and dispatch-state activity during every long snapshot interval.
Whole-file dynamic byte equality is therefore not a causal non-impairment
oracle while the owner-required parallel legacy dispatcher remains active. The
final test preserves both before/after dynamic snapshots and reports changed
paths without attribution. Every in-process test call is guarded by a Python
audit hook that rejects write-capable live-state opens, SQLite connections,
deletes, renames, and directory mutations. Repeated child-process sampling
rejects any observed live file handle or real harness command; source/path
constraints prohibit live integration; and rules, registry, and bridge routing
remain byte-identical. This is stronger causal evidence than silently treating
background writes as spike mutations or retrying them away.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`

## Owner Decisions / Input

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` accepted DBOS plus
  the official A2A SDK for this bounded spike, retained Hatchet as the explicit
  fallback, and required isolated parallel implementation with independent
  review and no activation from this slice.
- `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` v4 is active and includes WI-5617.
- No new owner decision is required. This report does not authorize or request
  production activation.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - accepted
  architecture and bounded foundation-spike decision.
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` - approved operative
  implementation proposal.
- `bridge/gtkb-dispatcher-next-foundation-spike-003.md` - Prime Builder
  `NO-ACTION` correction of malformed verdict metadata.
- `bridge/gtkb-dispatcher-next-foundation-spike-004.md` - independent corrected
  Loyal Opposition GO.

## Specification-Derived Verification

| Spec / governing surface | Executed evidence and observed result |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Full focused pytest measured peak overlap of 16 real DBOS subprocess workflows. A four-workflow executor crash occurred after one domain commit but before its DBOS step result, and restart recovered the three pending workflows with exactly four semantic operations total. Purpose-built transient failures succeeded on attempt three below the ceiling and exhausted at exactly three attempts at the ceiling. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Barrier-driven waves measured global 16, PB 8, LO 8, provider 5, model 3, and harness A 2 simultaneously; each next acquisition was denied atomically. A mixed 100-job run produced real retries at saturation. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Post-commit DBOS recovery, deterministic IDs, opaque subprocesses, explicit three-attempt DBOS retry policy, bounded 100-job capacity retry, append-only audits, immutable persisted capacity policy, TTL recovery, and lazy package facade all passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Exact proposal v001, corrected GO v004, live WI-5617 claim, and finalized implementation packet `sha256:9190209cf00c7dca692846ff0c46a824a96f704e574eab2f7864bbea5daf24fd` covered exactly the six changed targets. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Owner decision, PAUTH, proposal chain, linked TEST-11662, binary adoption record, and this report preserve the result durably. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passed with `missing_required_specs: []`, `missing_advisory_specs: []`, and `blocking_errors: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The exact focused file executed 11 specification-derived tests. Session-finish records carry the actual invocation and session exit. A manifest-only selection exited nonzero because all six execution-derived predicates were absent. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Proposal and report carry the exact PAUTH, project, and WI-5617 linkage. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Missing, failed, duplicate, cleanup-incomplete, or unsubstantiated all-true evidence fails closed to `reject_and_evaluate_hatchet`; direct inconsistent manifest construction raises; no owner answer is inferred. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All six targets are under `E:/GT-KB`; no Agent Red or outside-root path is imported, read, or changed. |
| `GOV-STANDING-BACKLOG-001` | All integration and independent-review findings were resolved inside the approved slice before report filing; no unresolved derived defect or fallback trigger remains to file. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The PB session self-enforced exact GO, claim, packet, and target checks without relying on native hook availability. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The test emits a complete adoption manifest, and this report records the single resulting lifecycle outcome. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | The isolated 16-worker/replay/retry probe preserved before/after dynamic snapshots and observed only concurrent WAL/SHM disappearance. Rules, registry, and bridge routing remained byte-identical; Python audit coverage completed all 11 test calls with zero live-write violations; repeated child-process sampling observed no live-state handle, real harness command, or surviving descendant. |

## Commands Run

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q -s --tb=short --timeout=240

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q --tb=short

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q --tb=short --timeout=240

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q -s --tb=short -k adoption --timeout=120

$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.dispatcher_next.foundation versions

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py

groundtruth-kb\.venv\Scripts\python.exe -m compileall -q groundtruth-kb/src/groundtruth_kb/dispatcher_next platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py

groundtruth-kb\.venv\Scripts\python.exe -m pip check

git diff --check -- groundtruth-kb/requirements-dispatcher-next-spike.txt groundtruth-kb/src/groundtruth_kb/dispatcher_next platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py

python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-dispatcher-next-foundation-spike-001.md --json

python scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-dispatcher-next-foundation-spike-001.md
```

## Observed Results

- Final exact focused suite: `11 passed, 1 warning in 30.94s`;
  emitted `outcome: adopt_dbos_a2a` with all six predicates true and complete,
  execution-derived evidence records carrying the actual command and session
  exit code 0.
- Manifest-only run: process exit 1 after `1 passed, 10 deselected`;
  emitted `reject_and_evaluate_hatchet` and enumerated all six missing
  predicates. It cannot emit adoption without the actual verification runs.
- Installed versions: `{"a2a-sdk": "1.1.1", "dbos": "2.27.0"}` under Python
  3.14.0.
- DBOS concurrency: measured peak execution overlap was exactly 16, not merely
  16 started handles or distinct PIDs.
- DBOS crash recovery: exit 91 occurred after one domain commit; restart
  recovered three pending workflows and produced exactly four semantic
  operations; repeated recovery was identical.
- DBOS bounded retry: two purpose-built transient failures succeeded on
  attempt 3; three transient failures exhausted with CLI exit 2 after exactly
  3 attempts. Only `TransientProbeError` is retryable.
- Capacity contention: synchronized waves observed global 16, PB 8, LO 8,
  provider 5, model 3, and harness A 2; all 100 mixed deterministic jobs
  acquired and released with retries observed;
  audit contained exactly 100 `lease_acquired` and 100 `lease_released`
  events, with capacity denials observed during bounded retries.
- Capacity restart: the ledger reaped the expired crash lease, permanently
  rejected reuse of its lease ID, and rejected a second instance presenting a
  policy different from the canonical persisted policy.
- A2A: completed structured artifact, failed diagnostic, and canceled
  diagnostic all survived deterministic protobuf round trips; invalid and
  repeated terminal transitions failed closed; integers at
  `9007199254740991` round-tripped and both signs beyond that boundary were
  rejected before protobuf conversion.
- Ruff lint: `All checks passed!`.
- Ruff format: `5 files already formatted`.
- Compileall: exit 0 with no output.
- Pip dependency check: `No broken requirements found.`
- Git diff whitespace check: exit 0 with no output.
- Applicability: passed with no missing required/advisory specs or blockers.
- Clause gate: four `must_apply`, zero evidence gaps, zero blocking gaps.
- Live non-impairment snapshots preserved the identical database hash
  `66cd667ce66286dae9754ea0cb162da888c2748c3869b1d0af12a791d9a9abdb`
  and dispatcher-state hash
  `167f0bb2c5b5df32912db7724118b2fb4b2cf07753a1bf74b70471892d08b060`.
  The concurrent legacy system removed its WAL/SHM files during the interval;
  those two paths are reported in the manifest rather than misattributed.
- Static non-impairment hashes:
  `config/dispatcher/rules.toml=26e7e8236220c11d73e23919f6f64d4a877df66139909a6acf312b6b38a40b76`,
  `harness-state/harness-registry.json=91947ec9be18867309122fed4abd27c646e894407f012622932408f064d0a2a9`,
  `.api-harness/routing.toml=610837493c98cac41de72a3248a773c8cf1d7926153ddcf84ebaf70866b8f047`.
- The in-process audit covered all 11 test calls with zero live-write
  violations. Child-process sampling observed 12 distinct process records and
  7 open files with inventory hash
  `b35378732672f110ca999ffe69d5b86a5aee77bb46162ab710e2cb16ee6f2508`;
  zero sampled handles targeted live state, zero commands matched a real
  harness, and no real harness descendant survived.
- The only warning was the repository's existing pytest
  `Unknown config option: asyncio_mode`; it did not affect collection,
  execution, or the WI-5617 targets.

## Files Changed

- `groundtruth-kb/requirements-dispatcher-next-spike.txt`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py`
- `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py`

All six were absent at implementation start and remain the only WI-5617
changes. The final helper plan excluded 1,105 unrelated dirty paths from
attribution.

## Acceptance Criteria Status

- PASS - both pinned dependencies import and execute under Python 3.14.
- PASS - measured peak overlap is 16 DBOS subprocess workflows; a
  post-domain-commit executor crash with three additional pending workflows
  recovers with exactly one semantic result per workflow ID; transient retry
  succeeds below and exhausts at the explicit three-attempt ceiling.
- PASS - A2A completion, structured artifact, failure, cancellation, and
  deterministic round trips are covered, with exact protobuf integer bounds.
- PASS - 100 jobs complete under atomic global/role/provider/model/harness
  caps, each exact cap is concurrently saturated, and canonical policy
  mismatch fails closed across ledger instances.
- PASS - repeated workflow/operation IDs return the original result without an
  additional domain mutation.
- PASS - the focused test emits command, exit code, predicate, observed value,
  satisfaction, and cleanup evidence for every actually executed mandatory
  predicate; focused omission exits nonzero.
- PASS - dynamic production state is observed before/after without causal
  overclaim; byte-identical static authorities, all-test in-process write
  auditing, child handle sampling, source constraints, and temp-path arguments
  show no live integration; no real harness process is launched.
- PASS - exactly one supported outcome is recorded:
  `adopt_dbos_a2a`.
- PASS - full focused pytest, Ruff lint, Ruff format, compileall, applicability,
  and clause gates pass.

## Risk And Rollback

This is an isolated spike, not an activated dispatcher. The main residual risk
is that later production integration may expose DBOS or A2A behavior not
present in deterministic local stubs. WI-5618 and later slices must retain
their own GO, claim, implementation-start, shadow, rollback, and independent
verification gates.

The dependency pins are isolated in the spike requirements file. The package
uses only caller-supplied SQLite paths; tests use pytest-owned temporary
databases. No production database, TAFE state, dispatcher state, lease, route,
registry, daemon, or external provider was mutated.

Under separate rollback authority, remove only the six listed WI-5617 targets.
Do not delete or rewrite the owner decision, PAUTH, project, work item,
proposal/verdict chain, test linkage, or this implementation report.

## Loyal Opposition Asks

1. Verify all six exact targets against operative proposal v001 and corrected
   GO v004.
2. Re-run the 11-test focused suite and inspect the emitted adoption manifest.
3. Confirm measured DBOS overlap, post-domain-commit multi-workflow recovery,
   persisted capacity policy, synchronized per-dimension saturation, and exact
   A2A integer bounds.
4. Confirm the lazy package facade prevents DBOS duplicate registration, the
   one-time domain initialization prevents concurrent WAL negotiation, and a
   manifest-only selection exits nonzero.
5. Return `VERIFIED` only if the binary outcome, isolation, atomic caps,
   recovery, A2A semantics, and non-impairment evidence all hold.
