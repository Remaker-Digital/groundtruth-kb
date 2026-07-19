NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb (transcript_init_keyword override after mid-session role-fallback defect, WI-5568); WI-5509 hook-fix test-file scope split after wi5326 peer-conflict 90-min wait

# Implementation Proposal - WI-5509 hook-fix: scoped test-only completion (3 files)

bridge_kind: prime_proposal
Document: gtkb-wi5509-hookfix-tests-scoped
Version: 001
Date: 2026-07-18 UTC
Responds to GO: bridge/gtkb-narrative-gate-edit-autodiscovery-fix-004.md

Authorization Basis: DELIB-202666772 (original WI-5509 owner authorization,
"Fix the hook itself first"), scoped-split authorized by
DELIB-202666853 (owner AUQ decision, this session, "Split off a scoped
test-only proposal") after a 90-minute background watch confirmed
gtkb-wi5326-atomic-work-item-test-linkage remains stuck at v003/NEW with no
dispatch pickup. The cited Project Authorization below is present to satisfy
the project-linkage metadata gate and reflects WI-5509's genuine active
membership in PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE (independently confirmed
by LO in version 004's GO via `list_project_work_items`); consistent with
version 003/004's own finding, that PAUTH's narrow approval-state-retirement
scope does not itself authorize this hook-governance work, so it is not
relied on as primary authorization -- DELIB-202666772 and DELIB-202666853
are.
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5509

target_paths: ["platform_tests/scripts/test_fab14_narrative_autodiscovery.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

implementation_scope: test-only completion of an already-GO'd design
requires_review: true
requires_verification: true
kb_mutation_in_scope: deliberation_archive_evidence_only
Recommended commit type: test:

## Problem Statement

`bridge/gtkb-narrative-gate-edit-autodiscovery-fix-004.md` (GO) approved an
8-file implementation adding Edit-tool-call support to the narrative-artifact
approval gate's HYG-047/FAB-14 autodiscovery path. 5 of the 8 files are
already implemented, intact, and verified this session:

- `.claude/hooks/narrative-artifact-approval-gate.py` (adds
  `_reconstruct_edit_content`, wires it into `main()` for the Edit branch)
- `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
  (byte-identical Codex template parity copy)
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
  (adds `content_source` param to `build_narrative_packet`)
- `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (wires
  `--content-file` through to `content_source` for `--kind narrative`)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (updated `--content-file` help
  text; confirmed via fresh `git diff` to sit outside the file's three
  pre-existing unrelated hunks)

The remaining 3 files are test-only additions covering the above. Filing
them under the original 8-file `target_paths` set blocks on an unrelated
peer-implementation-report conflict: `gtkb-wi5326-atomic-work-item-test-
linkage` (a different, non-terminal thread, stuck at v003/NEW since
2026-07-18 08:14, never picked up by any Loyal Opposition reviewer in 90+
minutes of polling) also claims `groundtruth-kb/src/groundtruth_kb/cli.py`
as a dirty path, and `implementation_authorization.py begin` has no flag to
scope down to a subset of an already-GO'd proposal's `target_paths`. None of
the 3 remaining files touch `cli.py`. This proposal requests authorization
for exactly those 3 files so implementation can proceed without further
dependency on wi5326's resolution.

No design change is proposed. The technical design was reviewed and GO'd
twice (independently re-verified against live source in version 004); this
proposal is a scope-narrowing procedural split, not a revision.

## Requirement Sufficiency

Existing requirements sufficient. The specifications and design cited in
`bridge/gtkb-narrative-gate-edit-autodiscovery-fix-004.md` (GO) fully cover
this work; no new or revised specification is required.

## Test Plan (the 3 remaining files)

### `platform_tests/scripts/test_fab14_narrative_autodiscovery.py`

Append 8 unit-level tests exercising `_reconstruct_edit_content` directly
(no subprocess) plus one end-to-end autodiscovery test reusing the existing
`_write_packet`/`_autodiscover_packet` helpers already in this file:

- `test_reconstruct_edit_content_single_occurrence` — single unambiguous
  `old_string` match substitutes correctly.
- `test_reconstruct_edit_content_replace_all` — `replace_all=True`
  substitutes every occurrence.
- `test_reconstruct_edit_content_zero_occurrences_fails_closed` —
  `old_string` absent from current file returns `None`.
- `test_reconstruct_edit_content_ambiguous_without_replace_all_fails_closed`
  — `old_string` appears more than once without `replace_all` returns
  `None` (fail-closed; no silent guess).
- `test_reconstruct_edit_content_missing_old_string_fails_closed` —
  missing `old_string` key returns `None`.
- `test_reconstruct_edit_content_non_string_new_string_fails_closed` —
  non-string `new_string` returns `None`.
- `test_reconstruct_edit_content_missing_file_fails_closed` — nonexistent
  `file_path` returns `None` (caught `OSError`).
- `test_edit_autodiscovery_end_to_end` — reconstructed Edit content feeds
  the existing, unmodified `_autodiscover_packet` match, proving the two
  pieces compose correctly.

### `platform_tests/hooks/test_narrative_artifact_approval.py`

Append 2 end-to-end subprocess tests exercising the full hook `main()` for
an `Edit` `tool_name` payload, using a fully sandboxed `tmp_path` project
root (own `config/governance/narrative-artifact-approval.toml` copy, own
target file, own `.groundtruth/formal-artifact-approvals/`) so no real
repository state is touched. `CLAUDE_PROJECT_DIR` is set explicitly in
`env_overrides` (in addition to `cwd`) to guarantee `_project_root()`
resolves to the sandbox regardless of ambient environment:

- `test_a_allow_edit_via_autodiscovery` — Edit payload
  (`old_string`/`new_string`, no full content) reconstructs post-edit
  content matching an autodiscovered on-disk packet; hook returns `{}`
  (allow).
- `test_a_block_edit_when_reconstruction_ambiguous` — Edit payload whose
  `old_string` appears twice without `replace_all`; reconstruction returns
  `None`, autodiscovery cannot run, hook returns `{"decision": "block", ...}`.

### `groundtruth-kb/tests/test_cli_approval_packet.py`

Append 1 CliRunner-based test proving the `--content-file` /
`content_source` decoupling for `--kind narrative`:

- `test_generate_narrative_packet_content_file_overrides_target_content` —
  `--target` points at a real on-disk file with unrelated live content;
  `--content-file` supplies different, intended content. Asserts the
  generated packet's `target_path` matches `--target`'s relative path,
  `full_content` matches the content-file (not the target file's on-disk
  bytes), and `full_content_sha256` matches `sha256(content_file bytes)`.

## Specification-Derived Verification

| Spec | Verification |
| --- | --- |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | All 3 new/extended test files run via `python -m pytest` with exit 0 reported in the post-implementation report. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Specification Links below carry forward all 12 specs cited and verified extant in version 004's GO. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal is filed through the governed no-index bridge writer path under an active work-intent claim for this exact slug. |
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Project and Work Item declared above, matching the parent thread's already-verified project membership (`KnowledgeDB.list_project_work_items('PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE')` includes WI-5509). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All 3 target_paths exist on disk and resolve inside `E:\GT-KB`. |

## Specification Links

Carried forward unchanged from `bridge/gtkb-narrative-gate-edit-autodiscovery-fix-004.md` (GO), all independently re-verified extant by that review:

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-STANDING-BACKLOG-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- DCL-ARTIFACT-APPROVAL-HOOK-001
- GOV-ARTIFACT-APPROVAL-001

## Owner Decisions / Input

- DELIB-202666772 - original WI-5509 owner authorization via AskUserQuestion
  ("Gate blocker", option 1 "Fix the hook itself first"), already
  independently verified real and on-point by LO in version 004's GO.
- DELIB-202666853 - this session's owner AUQ decision ("wi5326 blocker",
  option "Split off a scoped test-only proposal (Recommended)") authorizing
  this narrower proposal after the 90-minute wait produced no resolution.

## Prior Deliberations

- DELIB-202666772
- DELIB-202666853
- DELIB-1575
- DELIB-1577
- DELIB-2408
- DELIB-20261601
- bridge/gtkb-narrative-gate-edit-autodiscovery-fix-001.md
- bridge/gtkb-narrative-gate-edit-autodiscovery-fix-002.md
- bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md
- bridge/gtkb-narrative-gate-edit-autodiscovery-fix-004.md


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Acceptance Criteria

- All 8 new/extended test functions pass under `python -m pytest` with no
  regressions in the existing test suites in the same 3 files.
- `ruff check` and `ruff format --check` pass on all 3 changed files.
- `git diff --stat` for this thread's commit touches only the 3 declared
  `target_paths` (no `cli.py` or other hook-fix source files, since those
  are already committed/pending under the parent thread's own scope).
- Applicability preflight and clause preflight both pass with zero blocking
  gaps, consistent with the parent thread's already-clean results.

## Risk And Rollback

Minimal risk: test-only additions with no production code paths touched.
Rollback is a simple revert of the 3 test files; no other system state
depends on them. The parent hook-fix's already-implemented 5 files are
unaffected by this proposal's scope.
