NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T03-18Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; Prime Builder

# Implementation Proposal - GT Bridge Thread-Read CLI Commands

bridge_kind: prime_proposal
Document: gtkb-bridge-thread-read-cli-commands
Version: 001
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4634

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_thread_read.py", "groundtruth-kb/tests/test_cli_bridge_thread_read.py"]

implementation_scope: gt_bridge_thread_read_cli_commands
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Add deterministic `gt bridge show <slug>` and `gt bridge threads --wi <WI-ID>` read commands so Prime Builder and Loyal Opposition sessions can inspect bridge thread state and work-item coverage without ad hoc topic grep across `bridge/`.

WI-4634 is additive to the already-VERIFIED `gtkb-bridge-convenience-verbs` helper work. That older thread delivered skill-local helper scripts (`scan_bridge.py` and `show_thread_bridge.py`) and tests; it did not add first-class `gt bridge` CLI read commands. This proposal moves the recurring read operation into the governed CLI surface while preserving the helper behavior as an implementation reference.

## Requirement Sufficiency

Existing requirements are sufficient. The work item is already in `PROJECT-GTKB-MAY29-HYGIENE`, and the active project authorization covers proposals for all unimplemented May29 Hygiene work items. The Deterministic Services Principle (`DELIB-S312`) supplies the owner intent: repetitive manual bridge inspection should be encoded as deterministic service behavior.

No new owner decision is needed. This proposal does not authorize implementation until Loyal Opposition returns `GO` and Prime Builder obtains a fresh implementation-start packet for the approved target paths.

## In-Root Placement Evidence

All target paths are inside the GT-KB project root:

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_thread_read.py`
- `groundtruth-kb/tests/test_cli_bridge_thread_read.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the commands must read the status-bearing versioned bridge files as the durable audit chain and must not recreate or require retired aggregate queue artifacts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes machine-readable project authorization, project, work item, and target path metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, project, and verification requirements that constrain the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification will map CLI tests and read-only behavior checks to the governing requirements below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all files are GT-KB platform files under the project root, not Agent Red application files.
- `GOV-STANDING-BACKLOG-001` - WI-4634 is a governed backlog/current-work item and this proposal preserves traceability from backlog item to bridge thread.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the change turns a recurring inspection operation into a durable artifact-oriented CLI read surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the commands should expose artifact state without mutating bridge files or backlog records.

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repetitive AI plumbing is a defect and should move into deterministic services.
- `bridge/gtkb-bridge-convenience-verbs-008.md` - VERIFIED helper-mediated bridge scan/show-thread work; confirms the helper surface exists and this proposal is an additive CLI read surface, not duplicate implementation.
- `bridge/gtkb-protected-commit-authorization-gate-004.md` - VERIFIED commit-time protected-surface authorization gate; relevant because implementation target paths are protected source/test files and require a live GO packet before mutation.
- `WI-4634` - May29 Hygiene work item describing the manual topic-grep failure mode and desired `gt bridge show` / `gt bridge threads --wi` commands.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` - active owner authorization to propose implementation for all unimplemented work items linked to `PROJECT-GTKB-MAY29-HYGIENE`.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner decision evidence recorded on the project authorization.
- No new owner input is required for this proposal.

## Proposed Scope

Implementation should add a small read-only bridge-thread reader behind the `gt bridge` CLI group:

- `gt bridge show <slug>` prints the live version chain for `bridge/<slug>-NNN.md`, latest status, latest path, and per-version status/path metadata. A `--json` flag should emit the same data as structured JSON.
- `gt bridge threads --wi <WI-ID>` lists bridge threads that mention the work item id in machine-readable project/work metadata, body text, or related backlog linkage where available. It should return latest status and latest path for each match.
- Both commands must read current versioned bridge files directly and must not use cached startup reports, dashboard summaries, copied excerpts, or retired aggregate queue artifacts as authority.
- The implementation may reuse parsing patterns from `.claude/skills/bridge/helpers/show_thread_bridge.py`, but the production code should live under `groundtruth_kb` so the `gt` CLI is self-contained.
- The commands are read-only: no bridge file writes, no dispatcher-state mutation, no MemBase mutation.

## Specification-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | CLI tests create numbered bridge files and assert `gt bridge show` derives latest status/version chain from those files without requiring retired aggregate state. |
| `GOV-STANDING-BACKLOG-001` | CLI tests create or fixture bridge files mentioning a WI id and assert `gt bridge threads --wi WI-4634` returns matching thread summaries. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include this table with executed commands and results, including targeted pytest for the new CLI tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests and implementation remain under the declared in-root target paths. |
| Read-only behavior | Tests assert the commands do not create or modify bridge files and do not write dispatcher/TAFE state. |

Expected command scope:

```text
python -m pytest groundtruth-kb/tests/test_cli_bridge_thread_read.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_thread_read.py groundtruth-kb/tests/test_cli_bridge_thread_read.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge_thread_read.py groundtruth-kb/tests/test_cli_bridge_thread_read.py
```

## Acceptance Criteria

- `gt bridge show <slug> --json` returns latest status, latest path, and complete sorted version-chain metadata for an existing thread.
- `gt bridge show <slug>` returns a concise human-readable summary for an existing thread and exits nonzero for a missing slug with a clear error.
- `gt bridge threads --wi WI-4634 --json` returns thread summaries whose content or metadata reference the requested work item.
- The commands are deterministic and read-only.
- Existing `gt bridge config|status|health|dispatch ...` commands remain compatible.

## Risks / Rollback

Primary risk is duplicating the skill helper parser and allowing behavior drift. The implementation should keep parsing small, test the CLI behavior outside-in, and avoid changing existing helper scripts unless required by review. Rollback is limited: remove the new module, remove the CLI commands, and remove the new tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_thread_read.py`
- `groundtruth-kb/tests/test_cli_bridge_thread_read.py`

## Recommended Commit Type

`feat`
