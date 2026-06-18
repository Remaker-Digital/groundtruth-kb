NEW
author_identity: prime-builder/Codex
author_harness_id: A
author_session_context_id: keep-working-20260618T0945Z
author_model: GPT-5
author_model_version: 2026-06-18
author_model_configuration: Codex desktop automation; PowerShell; approval_policy_never

# CLI Artifact Read Verbs Slice 1

bridge_kind: prime_proposal
Document: gtkb-cli-artifact-read-verbs-slice-1
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4635

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_cli_artifact_read_verbs.py", "platform_tests/scripts/test_project_authorization.py", "bridge/gtkb-cli-artifact-read-verbs-slice-1-*.md"]
Recommended commit type: feat:

implementation_scope: cli_artifact_read_verbs_slice_1
requires_review: true
requires_verification: true

## Claim

`WI-4635` identifies an inconsistent MemBase read surface in the `gt` CLI that
forces Prime Builder and Loyal Opposition sessions back to raw SQL or ad hoc
Python for common inspections.

Live command-surface checks confirm the gap:

- `gt spec --help` exposes only `record` and `update`, with no read-only
  `show` or `list` command.
- `gt projects --help` exposes `authorizations PROJECT-ID` to list project
  authorization rows, but no `show-authorization PAUTH-ID` command to inspect
  one authorization directly.
- `gt deliberations --help` exposes `get`, while newer artifact groups such as
  `gt backlog` and `gt projects` use `show`.
- `gt --help` exposes no top-level `tests` group, even though
  `KnowledgeDB.get_test()` and `KnowledgeDB.list_tests()` already exist.

This proposal scopes a first CLI-read consistency slice that adds deterministic
read verbs without changing formal artifact records, authorization semantics,
or existing command behavior.

## Proposed Implementation After GO

1. Create a fresh implementation-start packet for this bridge thread.
2. Add read-only `gt spec show SPEC-ID --json/--history` using
   `KnowledgeDB.get_spec()` and `get_spec_history()`.
3. Add read-only `gt spec list --json` with filters that mirror existing
   `KnowledgeDB.list_specs()` arguments where practical, keeping the first
   slice small enough to verify.
4. Add read-only `gt projects show-authorization PAUTH-ID --json` that returns
   the latest authorization row by ID, including parsed JSON fields already
   shown by `gt projects show` and `gt projects authorizations`.
5. Add `gt deliberations show` as an alias for the existing `get` behavior,
   preserving `get` for compatibility.
6. Add a minimal read-only `gt tests` group with `show TEST-ID --json/--history`
   and `list --json` using `KnowledgeDB.get_test()`, `get_test_history()`, and
   `list_tests()`.
7. Add focused CLI tests that seed a temporary MemBase database and assert the
   new read commands are read-only, JSON-shaped, and compatible with existing
   verbs.
8. Run focused CLI tests plus ruff check/format on touched files, then file a
   post-implementation report with observed output.

## Out Of Scope

- Renaming or removing existing commands.
- Changing `gt deliberations get`; this slice adds `show` as a compatibility
  alias only.
- Adding mutation commands for specs, tests, or project authorizations.
- Changing database schemas or artifact lifecycle semantics.
- Broad UX polish outside the named read verbs.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected source/test
  mutation must wait for Loyal Opposition `GO` and a valid implementation-start
  packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - active May29 Hygiene
  project authorization permits autonomous proposals for unimplemented May29
  work items without bypassing bridge review.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, eventual report, and
  verification use the versioned bridge file chain.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes
  project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must map the linked requirements to executed tests and observed results.
- `GOV-STANDING-BACKLOG-001` - `WI-4635` is the governed backlog authority for
  this deterministic-service improvement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the CLI read surface helps preserve
  and inspect durable artifacts without ad hoc side channels.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact graph inspection should be
  available through deterministic project tools.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - read commands must expose lifecycle
  states without mutating them.
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - artifact lookup and filtering behavior
  must remain deterministic CLI logic, not conversational inference.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy-relevant artifact inspection should be
  machine-readable and repeatable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changed files and tests remain
  in-root under `E:\GT-KB`.

## Requirement Sufficiency

Existing requirements are sufficient for a read-only deterministic-service
slice. The work item asks for a CLI convenience/read surface over existing
MemBase records, and the implementation does not require new formal
GOV/SPEC/PB/ADR/DCL artifacts before source/test work begins.

## Owner Decisions / Input

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes autonomous
  proposal work for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE` through
  `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`.
- No new owner decision is required. This proposal does not request a waiver,
  production deployment, credential action, destructive cleanup, or formal
  artifact mutation.

## Prior Deliberations

- `WI-4635` live work-item record - captures the owner standing directive to
  offload repetitive, error-prone artifact inspection into deterministic CLI
  verbs.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - prior project principle that
  repetitive inspection and routing work should be moved from agent judgment to
  deterministic services.
- `platform_tests/scripts/test_project_authorization.py` - existing project
  authorization CLI coverage that already seeds a temporary project,
  authorization, specification, and work item for readback assertions.
- Focused bridge search for `WI-4635` and the exact title returned no existing
  bridge thread for this work item.

## Specification-Derived Verification Plan

This is the spec-to-test mapping for the proposed change. The
post-implementation report will include executed commands and observed results.

| Requirement / specification | Verification evidence |
|---|---|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Implementation-start packet created before source/test edits. |
| `GOV-STANDING-BACKLOG-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | CLI tests seed MemBase artifact rows and read them back through `gt spec`, `gt projects`, `gt deliberations`, and `gt tests` without raw SQL. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` and `SPEC-AUQ-POLICY-ENGINE-001` | New commands emit deterministic JSON with stable keys from `KnowledgeDB` read methods. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `show` and `list` commands expose status/stage/lifecycle fields without writing new versions. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Bridge applicability preflight passes for this proposal and report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest command covers each new CLI verb and compatibility alias. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-cli-artifact-read-verbs-slice-1` shows no drift after report filing. |

## Acceptance Criteria

- `gt spec show SPEC-ID --json` returns the requested current specification.
- `gt spec list --json` returns current specifications with useful filters.
- `gt projects show-authorization PAUTH-ID --json` returns one current
  authorization row by ID, including parsed JSON fields.
- `gt deliberations show DELIB-ID --json` works as an alias for `get`.
- `gt tests show TEST-ID --json` and `gt tests list --json` expose current test
  rows through existing `KnowledgeDB` read methods.
- Existing `gt spec record/update`, `gt projects authorizations`, and
  `gt deliberations get` behavior remains compatible.
- Focused CLI tests and ruff check/format pass for touched files.

## Risk And Rollback

Risk is moderate because `groundtruth-kb/src/groundtruth_kb/cli.py` is a large
shared command surface. The implementation should avoid broad refactors and
add small read-only commands near related groups. Rollback is a scoped revert
of the CLI/test additions; it would restore the manual-inspection friction but
should not affect stored artifacts.
