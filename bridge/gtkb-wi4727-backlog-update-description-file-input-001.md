NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e150e9ce-4657-4130-9e10-af48d3e79a44
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4727 file-based description input for gt backlog update

Document: gtkb-wi4727-backlog-update-description-file-input
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND
Work Item: WI-4727
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/tests/test_backlog_update_cli.py"]

## Summary

`gt backlog update` accepts the work-item description only through the
`--description TEXT` option (confirmed: `gt backlog update --help` lists
`--description` and no file/stdin alternative). On Windows PowerShell, a
description value containing embedded double-quotes is mangled by PowerShell's
native-executable argument splitting before the `gt` process receives it, so the
stored description is corrupted or the command errors. This was observed
first-hand this session (the same class of arg-split issue that makes JSON-array
flags with embedded quotes unsafe to pass inline on PowerShell).

Because the corruption happens in the shell before the CLI parses argv, the CLI
cannot repair it from the `--description` path. The fix is to add an input
channel that does not route the description through a shell-quoted argument: a
`--description-file PATH` option that reads the description from a file's
contents. A caller writes the description to a file (no shell quoting involved)
and passes the path, eliminating the arg-split corruption.

## Specification Links

- GOV-STANDING-BACKLOG-001 — the `gt backlog` CLI is the surface for the MemBase
  standing backlog; reliable description editing is part of that surface's
  integrity. Its CLAUSE-VISIBILITY-BULK-OPS does not apply here: WI-4727 is a
  single CLI-option addition, not a bulk backlog operation, so it produces no
  inventory artifact or review-packet and needs no bulk-action
  formal-artifact-approval packet.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; bridge
  authority and GO/NO-GO discipline apply.
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
  authorizing the NEW-implementation-proposal generation loop; basis for the
  covering PAUTH.
- WI-3269 (open, same project) — `gt backlog add` subcommand; the add path shares
  the same description-quoting exposure, so the file-input pattern here is a
  candidate to extend there as a follow-on.
- Session evidence 2026-06-26: this PB session avoided the embedded-quote
  arg-split bug by omitting a JSON-array flag, directly confirming the WI-4727
  failure mode on PowerShell.
- No prior deliberation rejects adding a file-based description input.

## Requirement Sufficiency

Existing requirements sufficient. GOV-STANDING-BACKLOG-001 already establishes the
`gt backlog` CLI as the standing-backlog surface; this WI makes one of its edit
paths reliable on PowerShell. No new or revised requirement is needed; no formal
spec/governance mutation is in scope.

## Design

Additive change plus tests, confined to the two authorized files:

1. `gt backlog update` (`groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py`):
   add a `--description-file PATH` option. When provided, the command reads the
   file's contents (UTF-8) and uses them as the new description, applying the same
   downstream validation/disjunctive-update rules as `--description`. `--description`
   and `--description-file` are mutually exclusive: supplying both is a usage
   error with a clear message. A missing/unreadable `--description-file` path
   produces a clear, non-traceback error.

2. Backward compatibility: the existing `--description TEXT` option is unchanged;
   callers not using the new option see identical behavior.

Out of scope (noted for the reviewer): extending the same file-input pattern to
`gt backlog add` (WI-3269 / same project) is a follow-on; this WI fixes the
`update` path named in WI-4727. A `--description-stdin` variant is intentionally
deferred unless the reviewer prefers it over (or in addition to) the file option.

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
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py groundtruth-kb/tests/test_backlog_update_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py groundtruth-kb/tests/test_backlog_update_cli.py
```

## Risk / Rollback

- Risk: the new option interacts with the existing disjunctive-update validation.
  Mitigation: route `--description-file` content through the same validation as
  `--description`; the test plan pins both the inline and file paths.
- Risk: mutual-exclusivity handling. Mitigation: a dedicated test asserts the
  both-supplied usage error.
- Rollback: the change is additive and confined to the update command and its
  test; reverting the two files restores prior behavior. No schema,
  governed-record, or narrative change is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4727-backlog-update-description-file-input-001.md`) under the
canonical append-only numbered-file chain; revisions and verdicts are added as
new numbered files so the numbered file chain remains the canonical audit trail
per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks), under which WI-4727 was
  re-homed to the active PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND and
  its covering PAUTH
  (PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT; allowed
  mutation classes source + test_addition; linked spec GOV-STANDING-BACKLOG-001)
  was minted. No further owner decision is required to review this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
