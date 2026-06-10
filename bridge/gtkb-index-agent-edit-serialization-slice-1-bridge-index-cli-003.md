REVISED

bridge_kind: prime_proposal
Document: gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli
Version: 003 (REVISED-1)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
Session: 019e8466-acc1-7923-b828-0ef7ab4a7758
Recommended commit type: feat
Project Authorization: PAUTH-WI-3513-BRIDGE-INDEX-SERIALIZATION-SLICE-1
Project: PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES
Work Item: WI-3513
Responds to scoping GO: bridge/gtkb-index-agent-edit-serialization-scoping-007.md
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py", "groundtruth-kb/tests/test_cli_bridge_index.py", "platform_tests/scripts/test_gt_bridge_index_cli.py"]
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e8466-acc1-7923-b828-0ef7ab4a7758
author_model: GPT-5 Codex
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop app; Prime Builder role; local workspace E:\GT-KB

# Implementation Proposal - Bridge INDEX Serialization Slice 1 CLI/API - REVISED-1

## Revision Claim

This REVISED-1 carries forward the GO'd `-001` scope unchanged and repairs the exact operative wording required by `scripts/implementation_authorization.py begin`. The GO at `-002` approved `-001`, but the implementation-start gate returned `Approved proposal is missing ## Requirement Sufficiency` because `-001` used the prose sentence `Existing requirements are sufficient` instead of the exact accepted state token `Existing requirements sufficient`.

Changes vs `-001` are intentionally non-scope-altering:

1. Changed the first sentence under `## Requirement Sufficiency` to the exact operative state `Existing requirements sufficient`.
2. Added this revision claim explaining the implementation-start packet blocker and re-GO request.

`target_paths`, project authorization, project, work item, implementation scope, acceptance criteria, rollback, and verification plan are otherwise identical to `-001`. Re-GO requested so Prime Builder can mint the implementation authorization packet and execute Slice 1 immediately.

## Claim

Implement Slice 1 from the approved `gtkb-index-agent-edit-serialization-scoping` design: add a deterministic `gt bridge index` CLI/API boundary for live `bridge/INDEX.md` mutation, backed by the existing serialized `scripts.bridge_index_writer.atomic_index_update` critical section.

This slice creates the shared safe path. It does not claim to intercept raw hand-edits from hookless harnesses, and it does not modify hook guards, protected rule files, bridge protocol documentation, or existing bridge helper callers. Those are later slices.

## Requirement Sufficiency

Existing requirements sufficient. `WI-3513` identifies the live `bridge/INDEX.md` lost-update class and the need for a `gt bridge index` serialized safe path. The approved scoping GO at `bridge/gtkb-index-agent-edit-serialization-scoping-007.md` directs Prime Builder to file this implementation proposal for Slice 1: `add-document`, `set-status`, `atomic_index_update`, and concurrent no-hook live working-tree tests.

No new product requirement or specification is created by this slice.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py`
- `groundtruth-kb/tests/test_cli_bridge_index.py`
- `platform_tests/scripts/test_gt_bridge_index_cli.py`

`scripts/bridge_index_writer.py` is an existing in-root dependency and is not expected to change in this slice.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical workflow state; this slice adds the serialized live-write path for that file.
- `GOV-STANDING-BACKLOG-001` - `WI-3513` is the tracked standing-backlog anchor.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - each CLI call reads live INDEX state inside the writer lock before writing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - no-hook and hook-capable harnesses get a common deterministic command path before any hook-guard slice.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the CLI/API preserves the bridge artifact graph and makes future helper migration traceable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner authorization, PAUTH, work item, and bridge proposal are durable governance artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - INDEX status lines represent bridge lifecycle transitions; this slice protects those transitions from lost updates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, and work item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps each linked behavior to executable tests.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization is captured as `DELIB-2777` through the governed owner-decision path.

## Prior Deliberations

- `DELIB-2777` - owner decision authorizing WI-3513 Slice 1 under `PAUTH-WI-3513-BRIDGE-INDEX-SERIALIZATION-SLICE-1`.
- `DELIB-2753` - review record for `bridge/gtkb-index-agent-edit-serialization-scoping-007.md`, the GO that approved this Slice 1 proposal direction.
- `DELIB-2755` - prior NO-GO explaining why a hook-first slice overclaimed no-hook and Codex coverage.
- `DELIB-1841` and `DELIB-1795` - prior helper INDEX parity NO-GO records in the same problem family.
- `DELIB-1967` and `DELIB-2173` - VERIFIED histories for bridge-propose helper INDEX parity work.
- `DELIB-2182` - owner authorization for the scheduler lanes/leases program, including the serialized INDEX writer primitive this slice reuses.

No cited deliberation rejects adding a CLI/API wrapper around the existing serialized writer.

## Owner Decisions / Input

- `DELIB-2777` records the 2026-06-01 owner directive to proceed with first-wave bridge-contention work and the narrow authorization for WI-3513 Slice 1.
- `PAUTH-WI-3513-BRIDGE-INDEX-SERIALIZATION-SLICE-1` is active for `WI-3513`, project `PROJECT-GTKB-BRIDGE-CONTENTION-L1-INDEX-WRITES`, with allowed mutation classes `source`, `cli_extension`, and `test_addition`.

No additional owner decision is required for this implementation proposal.

## Proposed Scope

### IP-1: Add package API for serialized INDEX mutations

Add `groundtruth-kb/src/groundtruth_kb/bridge/index_mutation.py` as the small Python API that future helper callers can use. It should validate bridge document slugs, status tokens, and `bridge/<slug>-NNN.md` path shape; provide pure transforms for adding a new `Document: <slug>` block and prepending a status line to an existing exact document block; provide serialized wrappers that call `scripts.bridge_index_writer.atomic_index_update`; and fail closed without writing on unknown status, path/slug mismatch, duplicate document, missing document for `set-status`, or duplicate status line.

### IP-2: Add `gt bridge index add-document`

Add a CLI group under the existing `gt bridge` command:

```text
gt bridge index add-document <document-slug> --status NEW --path bridge/<document-slug>-001.md
```

The command uses the IP-1 package API, defaults `--status` to `NEW`, inserts a new document block at the standard top-of-index location while preserving leading comments/header lines, rejects duplicate/malformed inputs, and supports `--json` for machine-readable callers.

### IP-3: Add `gt bridge index set-status`

Add:

```text
gt bridge index set-status <document-slug> <status> --path bridge/<document-slug>-NNN.md
```

The command uses the same serialized writer path from IP-1, prepends the status line immediately below the existing exact document line, accepts `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `WITHDRAWN`, and `ADVISORY`, and rejects missing document blocks, duplicate status lines, malformed paths, and unknown statuses without modifying `bridge/INDEX.md`.

### IP-4: Tests for no-hook concurrency and fail-closed behavior

Add unit and subprocess coverage:

- `groundtruth-kb/tests/test_cli_bridge_index.py` for Click command behavior, validation, JSON output, and pure transform edge cases.
- `platform_tests/scripts/test_gt_bridge_index_cli.py` for live no-hook subprocess concurrency against a temporary project root and `bridge/INDEX.md`.

The subprocess tests must clear Claude/Codex hook-related environment variables or otherwise run as plain Python subprocesses, so the passing evidence proves the CLI/API boundary itself provides the lock, not a harness hook.

## Out Of Scope

- No hook guard implementation.
- No `bridge/INDEX.md` raw-edit interception claim.
- No protected `.claude/rules/*.md` or `.codex/skills/*.md` edits.
- No migration of `revise_bridge.py`, `impl_report_bridge.py`, or `write_bridge.py` callers; that is Slice 2.
- No deployment, force-push, spec deletion, or broad backlog reconciliation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | Use synthetic bridge slugs and temp paths only; no credential-shaped fixtures. | Bridge helper credential scan plus source review. | n/a |
| CQ-PATHS-001 | Yes | Use config/project-root paths and pytest `tmp_path`; no hard-coded host-only runtime paths in tests. | Targeted pytest verifies temp project roots; ruff covers changed files. | n/a |
| CQ-COMPLEXITY-001 | Yes | Keep parsing and mutation helpers small and table-driven. | Source review plus `python -m ruff check` on changed files. | n/a |
| CQ-CONSTANTS-001 | Yes | Centralize valid statuses and status-line validation in the new API module. | Unit tests cover accepted and rejected status tokens. | n/a |
| CQ-SECURITY-001 | Yes | No network, credentials, deployment, or privilege changes. | Source review and targeted pytest operate only on temp files. | n/a |
| CQ-DOCS-001 | N/A | n/a | n/a | Documentation/rule updates are explicitly later slices. |
| CQ-TESTS-001 | Yes | Add unit and no-hook subprocess concurrency coverage for the new CLI/API. | `python -m pytest groundtruth-kb/tests/test_cli_bridge_index.py platform_tests/scripts/test_gt_bridge_index_cli.py -q --tb=short`. | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | The CLI emits success/error output but adds no logging surface. |
| CQ-VERIFICATION-001 | Yes | Run targeted pytest, existing writer baseline, ruff check, and ruff format check. | Commands listed in the verification plan and implementation report. | n/a |

## Specification-Derived Verification Plan

- Serialized safe path uses live fresh-read writes: unit test monkeypatching or otherwise proving the CLI/API calls `atomic_index_update`.
- `add-document` preserves both concurrent no-hook writers: `python -m pytest platform_tests/scripts/test_gt_bridge_index_cli.py -q -k concurrent_add_document`.
- `set-status` preserves concurrent changes: `python -m pytest platform_tests/scripts/test_gt_bridge_index_cli.py -q -k concurrent_set_status`.
- malformed status fails closed: `python -m pytest groundtruth-kb/tests/test_cli_bridge_index.py -q -k invalid_status`.
- missing document for `set-status` fails closed: `python -m pytest groundtruth-kb/tests/test_cli_bridge_index.py -q -k missing_document`.
- duplicate document/status fails closed: `python -m pytest groundtruth-kb/tests/test_cli_bridge_index.py -q -k duplicate`.
- existing serialized writer baseline remains healthy: `python -m pytest platform_tests/scripts/test_bridge_index_writer.py -q --tb=short`.
- changed Python files are lint-clean and formatted: `python -m ruff check <changed-files>` and `python -m ruff format --check <changed-files>`.

Implementation report must include the exact commands and observed results.

## Acceptance Criteria

- `gt bridge index add-document` exists and is registered under `gt bridge`.
- `gt bridge index set-status` exists and is registered under `gt bridge`.
- Both commands use `atomic_index_update` for the live INDEX read-modify-write.
- No-hook subprocess concurrency tests prove no lost `Document:` entry and no lost status prepend when callers use the CLI.
- Invalid input and stale assumptions fail closed without modifying INDEX.
- The proposal and implementation do not claim raw hookless hand-edits are mechanically intercepted.

## Pre-Filing Preflight Subsection

Candidate preflights must pass before filing this proposal:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli --content-file .tmp/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-001.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli --content-file .tmp/gtkb-index-agent-edit-serialization-slice-1-bridge-index-cli-001.md
```

## Risk And Rollback

Risk: command semantics may be too narrow for future helper migration. Mitigation: Slice 1 intentionally exposes a small package API in addition to the CLI, and later helper migration can add wrapper convenience without changing the lock primitive.

Risk: operators may keep hand-editing `bridge/INDEX.md`. Mitigation: this proposal does not overclaim closure; later hook and documentation slices remain necessary backstops.

Rollback: remove the new `cli_bridge_index.py` and `bridge/index_mutation.py` modules, remove the `gt bridge index` registration from `cli.py`, and remove the two new test files. The existing `scripts/bridge_index_writer.py` primitive is unchanged.
