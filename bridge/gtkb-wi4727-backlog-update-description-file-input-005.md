NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8f2455b1-c515-479c-b544-720ce8ef2471
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

bridge_kind: implementation_report

# Implementation Report: WI-4727 file-based description input for gt backlog update

Document: gtkb-wi4727-backlog-update-description-file-input
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4727-backlog-update-description-file-input-004.md
Project: PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND
Work Item: WI-4727
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT
Recommended commit type: feat

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_backlog_update_cli.py"]

## Summary

Implemented per the GO'd `-003` proposal (Cursor LO GO at `-004`). Added a
`--description-file PATH` option to the `gt backlog update` command
(`backlog_update`, cli.py ~3088) that reads the new description from an in-root
file's UTF-8 contents, so a description containing embedded double-quotes is not
mangled by PowerShell native-exe arg-split (the WI-4727 defect). `--description`
and `--description-file` are mutually exclusive (`click.UsageError` on both). The
resolved description flows through the unchanged `BacklogUpdateRequest.description`
field and the existing WI-4357 disjunctive text-edit gate. Backward compatible:
`--description TEXT` is unchanged; `cli_backlog_update.py` and
`BacklogUpdateRequest` are untouched. The option type
`click.Path(exists=True, dir_okay=False, path_type=Path)` mirrors the in-tree
`gt spec record --content-file` pattern (cli.py ~5816).

## Specification Links

(carried forward from `-003`)

- GOV-STANDING-BACKLOG-001 — the `gt backlog` CLI is the surface for the MemBase
  standing backlog; reliable description editing is part of that surface's
  integrity. Single CLI-option addition, not a bulk backlog operation; no
  inventory/review-packet or bulk formal-artifact-approval packet required.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; bridge
  authority and GO/NO-GO discipline apply, including the canonical append-only
  numbered-file chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal cited every
  relevant governing specification; this report carries them forward.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — each behavioral clause maps
  to an executed test (see Spec-to-Test Mapping below), all executed and PASS.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  package source/tests in-root under the project root; no out-of-root dependency.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the new input path
  is enforced by spec-derived CLI tests.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4727 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Requirement Sufficiency

Existing requirements sufficient. GOV-STANDING-BACKLOG-001 already establishes the
`gt backlog` CLI as the standing-backlog surface; this WI makes one of its edit
paths reliable on PowerShell. No new or revised requirement is needed; no formal
spec/governance mutation is in scope.

## Recommended Commit Type

`feat:` — adds a new CLI input channel (`--description-file`) plus four
spec-derived tests. Matches the GO'd reviewer's `Recommended commit type: feat`
at `-004` and the diff stat (net-new capability surface).

> SCOPE CAVEAT for the finalizer: `cli.py` also carries ONE pre-existing,
> unrelated working-tree change at line ~7404 — `+"dispatcher_daemon"` added to
> the `gt mode set-bridge-substrate --substrate` Choice (in-flight
> dispatcher-daemon work; NOT part of WI-4727). It was already dirty in the
> working tree before this implementation began. A
> `--finalize-verified --include groundtruth-kb/src/groundtruth_kb/cli.py` will
> stage that line into the WI-4727 commit. Flagging for scoped-commit awareness;
> disposition is the owner's (e.g., accept it riding along, or stage the
> WI-4727 hunks selectively).

## Implemented Changes

1. cli.py `backlog_update` command (~line 3087-3099): new `--description-file`
   option, `type=click.Path(exists=True, dir_okay=False, path_type=Path)`,
   `default=None`.
2. cli.py `backlog_update` signature + body (~line 3116, 3125-3128): added
   `description_file: Path | None` parameter; mutual-exclusivity check
   (`click.UsageError` if both `--description` and `--description-file`); when
   `--description-file` is provided, the command reads the file via
   `read_text(encoding="utf-8")` before the unchanged `BacklogUpdateRequest`
   construction.
3. groundtruth-kb/tests/test_backlog_update_cli.py: 4 new spec-derived tests
   appended (embedded-quotes via file, inline backward-compat, mutual exclusivity,
   missing-path usage error).

## Spec-to-Test Mapping (verification)

| Specification clause | Test | Result |
|---|---|---|
| GOV-STANDING-BACKLOG-001 (`--description-file` sets a description with embedded double-quotes correctly) | test_update_description_file_with_embedded_quotes | PASS |
| GOV-STANDING-BACKLOG-001 (existing inline `--description` path unchanged) | test_update_description_inline_still_works | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (`--description` and `--description-file` mutually exclusive, no traceback) | test_update_description_and_file_mutually_exclusive | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (missing `--description-file` path errors clearly, no traceback) | test_update_description_file_missing_path_errors | PASS |

## Verification Evidence

Commands run against the changed files (project venv interpreter
`groundtruth-kb/.venv/Scripts/python.exe`):

- `python -m pytest groundtruth-kb/tests/test_backlog_update_cli.py -q --tb=short`
  -> `20 passed in 9.87s` (16 pre-existing + 4 new).
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_backlog_update_cli.py`
  -> `2 files already formatted` (PASS — both gates run; format and lint are separate).
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_backlog_update_cli.py`
  -> 2 `E501` (line-too-long) findings at cli.py:6142 and cli.py:6580. Both are
  pre-existing ChromaDB error-message strings, confirmed present verbatim in
  `HEAD` (`git show HEAD:...cli.py` matches), NOT introduced by this change and
  outside the `backlog_update` edit region (~3088-3128). The changed lines are
  lint-clean. Not fixed here (out of WI-4727 scope; avoids unrelated
  whitespace/scope churn).

Line endings: `git diff --check` reports working-tree trailing-whitespace on added
lines; this is `core.autocrlf=true` working-tree-vs-index noise (cli.py is
uniformly CRLF on disk — 7844 CRLF, 0 bare LF; the test file uniformly LF). Both
files are internally consistent (no mixed-ending contamination) and normalize to
LF on commit; the source lines contain no literal trailing whitespace.

Changeset: `cli.py` +15/-1 (the `-1` is the pre-existing dispatcher_daemon line
noted in the scope caveat); `test_backlog_update_cli.py` +134.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks); basis for the covering PAUTH.
- bridge/gtkb-wi4727-backlog-update-description-file-input-001.md (NEW),
  -002.md (GO on prior `target_paths`, superseded), -003.md (REVISED scope
  correction to cli.py), -004.md (Cursor LO GO on `-003`).
- Deliberation search "backlog update description file input quoting" (5 hits;
  none reject file-based description input).
- WI-3269 (open, same project) — `gt backlog add` shares the quoting exposure;
  extending the file-input pattern there is a noted follow-on, out of scope here.

## Risk / Rollback

- Additive change confined to the `backlog_update` command plus its test file.
  Reverting the two files restores prior behavior. No schema, governed-record, or
  narrative change is involved.
- The new option composes with the unchanged WI-4357 text-edit gate; the
  embedded-quotes and inline tests pin both input paths; the mutual-exclusivity
  and missing-path tests pin the error paths.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks). WI-4727 sits in the active
  PROJECT-GTKB-BACKLOG-CAPTURE-001-BACKLOG-ADD-COMMAND under
  PAUTH-PROJECT-GTKB-BACKLOG-CAPTURE-001-WI-4727-DESCRIPTION-FILE-INPUT (allowed
  mutation classes source + test_addition; linked spec GOV-STANDING-BACKLOG-001).
  The implemented target_paths (cli.py + test) are within that PAUTH scope. No
  further owner decision is required to verify this report.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
