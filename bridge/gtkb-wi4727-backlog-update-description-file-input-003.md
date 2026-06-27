REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal (REVISED): WI-4727 file-based description input for gt backlog update

Document: gtkb-wi4727-backlog-update-description-file-input
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4727-backlog-update-description-file-input-002.md
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND
Work Item: WI-4727
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_backlog_update_cli.py"]

## Revision Note

REVISED as `-003` correcting a scope defect in `-001` (carried into the `-002`
GO). Both `-001` and the `-002` GO located the `gt backlog update` `--description`
option in `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`. It is not
there: `cli_backlog_update.py` holds only the `BacklogUpdateRequest` dataclass and
the `update_backlog_item` logic. The Click command `backlog update` — including the
`--description` option and the `BacklogUpdateRequest` construction — is registered
in `groundtruth-kb/src/groundtruth_kb/cli.py` (the `backlog_update` command,
currently around lines 3075-3140). A new `--description-file` Click option can only
be declared on that command, and the spec-derived tests invoke the real Click CLI
via `CliRunner` + `groundtruth_kb.cli.main`. The `-001` `target_paths`
(`cli_backlog_update.py` + the test) therefore cannot physically hold the change,
and `implementation_authorization.py begin` scoped to them would block the
required `cli.py` edit.

This `-003` corrects `target_paths` to the file that actually changes
(`cli.py`) plus the test file. The WI premise is unchanged and still valid
(PowerShell native-exe arg-split mangles embedded double-quotes in `--description`).
The design now also mirrors an existing in-tree pattern: `gt spec record` and the
spec-update command already expose a file-based content option via
`click.Path(exists=True, dir_okay=False, path_type=Path)` (cli.py ~5814-5819 and
~5912-5918), so `--description-file` reuses a proven, reviewed shape rather than
introducing a new one. `cli_backlog_update.py` is intentionally NOT in scope: the
file read happens in the command body and the resolved description flows through
the existing `BacklogUpdateRequest.description` field and its existing text-edit
gate unchanged.

## Summary

`gt backlog update` accepts the work-item description only through the
`--description TEXT` option. On Windows PowerShell, a description value containing
embedded double-quotes is mangled by PowerShell's native-executable argument
splitting before the `gt` process receives it, so the stored description is
corrupted or the command errors. Because the corruption happens in the shell
before the CLI parses argv, the CLI cannot repair it from the `--description`
path. The fix adds an input channel that does not route the description through a
shell-quoted argument: a `--description-file PATH` option that reads the
description from a file's contents. A caller writes the description to a file (no
shell quoting involved) and passes the path, eliminating the arg-split corruption.

## Specification Links

- GOV-STANDING-BACKLOG-001 — the `gt backlog` CLI is the surface for the MemBase
  standing backlog; reliable description editing is part of that surface's
  integrity. Its CLAUSE-VISIBILITY-BULK-OPS does not apply here: WI-4727 is a
  single CLI-option addition, not a bulk backlog operation, so it produces no
  inventory artifact or review-packet and needs no bulk-action
  formal-artifact-approval packet.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; bridge
  authority and GO/NO-GO discipline apply, including the canonical append-only
  numbered-file chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  package source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the new input path
  is enforced by spec-derived CLI tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4727 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks); basis for the covering PAUTH.
- bridge/gtkb-wi4727-backlog-update-description-file-input-001.md (NEW) and
  -002.md (the `-002` GO) — the prior versions of this thread; this `-003`
  supersedes the `-001` design's `target_paths` after the cli.py-location finding.
- WI-3269 (open, same project) — `gt backlog add` subcommand; the add path shares
  the same description-quoting exposure, so the file-input pattern here is a
  candidate to extend there as a follow-on.
- No prior deliberation rejects adding a file-based description input.

## Requirement Sufficiency

Existing requirements sufficient. GOV-STANDING-BACKLOG-001 already establishes the
`gt backlog` CLI as the standing-backlog surface; this WI makes one of its edit
paths reliable on PowerShell. No new or revised requirement is needed; no formal
spec/governance mutation is in scope.

## Design

Additive change plus tests, confined to the two authorized files:

1. `gt backlog update` (`groundtruth-kb/src/groundtruth_kb/cli.py`, the
   `backlog_update` command): add a `--description-file` option typed as
   `click.Path(exists=True, dir_okay=False, path_type=Path)`, mirroring the
   existing `gt spec record --content-file` pattern. When provided, the command
   reads the file's contents as UTF-8 and uses them as the new description, which
   then flows through the unchanged `BacklogUpdateRequest.description` field and
   the existing disjunctive text-edit gate. `--description` and
   `--description-file` are mutually exclusive: supplying both raises a
   `click.UsageError` with a clear message (non-zero exit, no traceback). A
   missing/unreadable path is rejected by Click's `exists=True` validation with a
   clear usage error and non-zero exit (no traceback).

2. Backward compatibility: the existing `--description TEXT` option is unchanged;
   callers not using the new option see identical behavior. `cli_backlog_update.py`
   and `BacklogUpdateRequest` are unmodified.

Out of scope (noted for the reviewer): extending the same file-input pattern to
`gt backlog add` (WI-3269 / same project) is a follow-on; this WI fixes the
`update` path named in WI-4727. A `--description-stdin` variant is intentionally
deferred unless the reviewer prefers it.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-STANDING-BACKLOG-001 (--description-file sets a description containing embedded double-quotes correctly) | test_update_description_file_with_embedded_quotes | groundtruth-kb/tests/test_backlog_update_cli.py |
| GOV-STANDING-BACKLOG-001 (existing --description path is unchanged) | test_update_description_inline_still_works | groundtruth-kb/tests/test_backlog_update_cli.py |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (--description and --description-file are mutually exclusive) | test_update_description_and_file_mutually_exclusive | groundtruth-kb/tests/test_backlog_update_cli.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (missing --description-file path errors clearly, no traceback) | test_update_description_file_missing_path_errors | groundtruth-kb/tests/test_backlog_update_cli.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_backlog_update_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_backlog_update_cli.py
```

## Risk / Rollback

- Risk: the new option interacts with the existing disjunctive text-edit gate.
  Mitigation: the file-read resolves to the same `description` value that
  `--description` would set, then flows through the unchanged gate; the test plan
  pins both the inline and file paths.
- Risk: mutual-exclusivity handling. Mitigation: a dedicated test asserts the
  both-supplied usage error.
- Risk: editing the large `cli.py` module. Mitigation: the change is a localized,
  additive option on one command plus a few lines in its body; no other command
  is touched, and `ruff format --check` guards formatting.
- Rollback: the change is additive and confined to the `backlog_update` command
  and its test; reverting the two files restores prior behavior. No schema,
  governed-record, or narrative change is involved.

## Bridge Filing Discipline

This revision is filed as the next numbered bridge file
(`bridge/gtkb-wi4727-backlog-update-description-file-input-003.md`) under the
canonical append-only numbered-file chain. Prior versioned bridge files (`-001`
NEW, `-002` GO) are never rewritten or deleted; this REVISED version is added as a
new numbered file so the numbered file chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), under which WI-4727 was
  re-homed to the active PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND and
  its covering PAUTH
  (PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT; allowed
  mutation classes source + test_addition; linked spec GOV-STANDING-BACKLOG-001)
  was minted. The corrected `target_paths` (cli.py + test) remain within that
  PAUTH's "source and test additions only" scope. No further owner decision is
  required to review this revision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
