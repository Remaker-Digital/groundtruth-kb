NEW

# CLI Module __main__ Guard: Fix Silent No-Op on `python -m groundtruth_kb.cli`

bridge_kind: prime_proposal
Document: gtkb-cli-module-main-guard
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 1834acbd-e886-434c-9ae5-e467a7f93e2b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4518

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner-reported defect (S437): "The backlog command returned nothing. This is an error." Root cause: `groundtruth-kb/src/groundtruth_kb/cli.py` has no `if __name__ == "__main__":` guard, so invoking the CLI via the module form `python -m groundtruth_kb.cli <command>` imports `cli.py` as `__main__`, defines every command, and exits 0 having dispatched nothing. The result is a silent no-op: `python -m groundtruth_kb.cli backlog list` prints nothing and returns exit 0, which falsely looks like an empty backlog. The 417 work items are fully intact — the canonical package form `python -m groundtruth_kb backlog list` and the `gt` console script both work — but the silent-success failure mode on a natural invocation is a footgun that cost a full diagnosis cycle this session.

Fix (fast-lane defect, GOV-RELIABILITY-FAST-LANE-001): add the standard `if __name__ == "__main__": main()` guard to `cli.py`, calling the existing `main` click group that `__main__.py` already imports. This makes the module form dispatch identically to the package form. Add a regression test asserting `python -m groundtruth_kb.cli` dispatches.

This change introduces NO new command, flag, behavior, or public API surface. The `main` group and all its commands already exist; the guard only repairs the module-as-`__main__` dispatch path that currently fails silently. No requirement or specification is created or revised.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - this is a small, single-concern, defect-origin fix (~1 source guard block + 1 test) that introduces no new public CLI surface and needs no new/revised requirement; it is created under `PROJECT-GTKB-RELIABILITY-FIXES` and covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` through active project membership.
- `GOV-STANDING-BACKLOG-001` - the backlog is surfaced through the `backlog list` CLI; a silent no-op on a natural CLI invocation undermines backlog visibility. The fix restores deterministic CLI dispatch so the backlog surface cannot silently appear empty via the module form.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain is append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - project authorization, project, work item, target paths, and governing specs are linked before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps the regression test to the defect this fix removes.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision establishing the reliability fast-lane path used by this fix.
- No prior deliberations found for the CLI `__main__` / module-invocation entry point: `search_deliberations("cli __main__ module entry point python -m invocation")` returned no matches on 2026-06-13. This is a newly-discovered footgun, not a revisit of a rejected approach.
- Owner directive (S437, 2026-06-13): "The backlog command returned nothing. This is an error." is the originating signal; the diagnosis confirmed the canonical command returns all 417 work items and isolated the silent no-op to the `-m groundtruth_kb.cli` form.

## Owner Decisions / Input

No new owner decision is required. The owner reported the defect and the standing directive authorizes driving and fixing backlog/reliability issues. Authorization is the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via WI-4518 active project membership; no per-fix deliberation, per-fix project authorization, or formal-artifact-approval packet is required under GOV-RELIABILITY-FAST-LANE-001.

## Requirement Sufficiency

Existing requirements sufficient. The fix removes a defect (silent no-op) without adding or revising any requirement. The CLI's `main` click group and its commands already exist and define the intended behavior; `__main__.py` already documents the supported module-invocation contract. This proposal only repairs the `cli`-module dispatch path to match that existing contract. No new or revised requirement is needed.

## Implementation Plan

1. In `groundtruth-kb/src/groundtruth_kb/cli.py`, append a standard module entry guard at end of file:
   ```python
   if __name__ == "__main__":
       main()
   ```
   `main` is the existing `@click.group()` entry (cli.py:172) that `groundtruth_kb/__main__.py` already imports and invokes. No other code changes.
2. In `groundtruth-kb/tests/test_cli.py`, add a regression test that runs the CLI via the module form in a subprocess and asserts it dispatches, comparing it to the package form. Use `--help` (DB-independent, fast, deterministic):
   - `subprocess.run([sys.executable, "-m", "groundtruth_kb.cli", "--help"], ...)` returns exit 0 and non-empty stdout containing `Usage:`.
   - Its stdout matches `subprocess.run([sys.executable, "-m", "groundtruth_kb", "--help"], ...)` stdout (identical help => identical dispatch entry).
   - The test would FAIL before this fix (the `.cli` form returns empty) and PASS after, pinning the regression.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_cli.py -q --tb=short
Expected: pass; the new regression test proves `python -m groundtruth_kb.cli --help` dispatches with non-empty `Usage:` output identical to `python -m groundtruth_kb --help`.

groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb.cli backlog list
Expected: non-empty rows (same as the package form) instead of the prior silent empty output; manual confirmation evidence in the report.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\tests\test_cli.py
Expected: pass.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\tests\test_cli.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_cli.py
Expected: no output, exit 0.
```

Spec mapping:

- `GOV-RELIABILITY-FAST-LANE-001` - the change is defect-origin, single-concern, ~2 files, no new requirement/surface; the report reads back WI-4518 as a member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- `GOV-STANDING-BACKLOG-001` - the manual `backlog list` evidence proves the backlog surface no longer silently appears empty via the module form.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the regression test maps to the removed defect and is executed against the implementation.

## Risk / Rollback

Risk is minimal. Adding the conventional `__main__` guard cannot change behavior of the package form (`__main__.py`) or the `gt` console script (both call `main` independently); it only adds a dispatch path for the module form. The only behavioral change is that the previously-silent `-m groundtruth_kb.cli` form now runs the requested command. No new commands or flags are added.

Rollback is a single-commit source/test revert before VERIFIED. There is no data migration and no KB mutation in scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-cli-module-main-guard` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this fix changes no bridge-authority behavior.

## Recommended Commit Type

fix - this repairs a silent no-op defect in CLI module dispatch and adds a regression test; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
