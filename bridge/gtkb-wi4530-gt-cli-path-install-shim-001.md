NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4530-gt-cli-path-install-shim
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4530
target_paths: ["scripts/install_gt_path_shim.py", "platform_tests/scripts/test_install_gt_path_shim.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4530: In-root `gt` PATH-shim generator (deterministic launcher emission for fresh installs)

## Summary

WI-4530 (P3, `developer-environment`, origin=improvement): a fresh GT-KB checkout exposes the `gt` CLI only as the venv console-script at `groundtruth-kb/.venv/Scripts/gt.exe`. That venv has no pip and pipx is not installed, so `gt` is not on PATH and bare `gt …` invocations (assumed throughout rules / skills / docs) fail. The 2026-06-13 manual workaround placed a `gt.cmd` launcher shim under a user-PATH directory forwarding to the venv exe — but that out-of-root placement is manual; a fresh install on another machine has no such file.

**Cycle-13 triage (this session) confirms WI-4530 is genuinely OPEN. The owner's cycle-13 AskUserQuestion decision is "Seed both as scripts/ helpers"** — file the deterministic shim-content generator as a new `scripts/install_gt_path_shim.py` module in pure `source` + `test_addition` PAUTH scope. A separate follow-on slice (with the appropriate install-process / PATH-setup authorization) wires the generator into the install/bootstrap path and decides the deployment target (per-OS user-PATH directory, PATH advice in install docs, etc.).

This proposal scopes the source helper only. The helper has two responsibilities:

1. **Emit the launcher script's TEXT CONTENT** (Windows `.cmd`, POSIX shell `gt`) given the venv exe path. Pure-string, fully unit-testable, no I/O.
2. **Resolve the venv exe path** from a `project_root` argument (`groundtruth-kb/.venv/Scripts/gt.exe` on Windows, `groundtruth-kb/.venv/bin/gt` on POSIX). Pure-path, fully unit-testable.

Crucially the helper does NOT write any file or modify any PATH variable in this slice — those are install-process concerns deferred to the follow-on. The helper is a pure content/path generator the follow-on install slice (and the existing in-root `scripts/`-callable tooling) can call to produce a correct shim deterministically. This stays cleanly in-root and defers the out-of-root user-PATH placement decision to the follow-on install slice.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4530 is the backlog authority for this fix (P3 developer-environment improvement). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one new generator module + one test, no install-process mutation), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4530; allows `source` + `test_addition`). The follow-on install-process slice will declare its own scope.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** + **`.claude/rules/project-root-boundary.md`** — both `target_paths` are in-root under `E:\GT-KB` (`scripts/install_gt_path_shim.py` and `platform_tests/scripts/test_install_gt_path_shim.py`); the helper is **path-pure** and does NOT place any artifact out-of-root in this slice. **In-root invariant for this slice:** this proposal makes NO new out-of-root placement — it stops at pure content/path generation, performs no `Path.write_text` / `open(..).write` / `os.environ` mutation in any public function, and asserts that in `test_helper_does_no_io`. The historical 2026-06-13 manual workaround that placed a launcher at a user-PATH directory is cited in this proposal only as evidentiary background; the workaround placement is **not** done by this slice and is **not** proposed for adoption here. The follow-on install slice will discuss the user-PATH deployment target explicitly under its own authorization, where the project-root-boundary review can be applied to that specific decision.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger). It is a developer-environment generator that does NOT modify `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a Windows-cmd and POSIX-shell rendering test plus a venv-path resolution test.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked tooling helper that codifies a manual workaround as a deterministic generator; the helper is the durable artifact.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4530 + the 2026-06-13 manual workaround), cycle-13 triage confirmed it open, the bounded PAUTH authorizes the `source` + `test_addition` work, the owner's cycle-13 AUQ chose the scripts/-helper scope, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / the project-root-boundary rule defines the in-root constraint this slice respects (the helper does not place anything out-of-root). No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4530 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Cycle-13 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Seed both as scripts/ helpers" over "defer both" and "seed only WI-4528", explicitly authorizing this slice and the WI-4528 sweep-commit-helper sibling as scripts/ helpers in pure source+test PAUTH scope; the install/bootstrap PATH-setup follow-on slice will declare its own authorization.
- **Distinct from WI-4395** (uv cache ACLs) — WI-4530 is the launcher-on-PATH gap; WI-4395 is the venv installer permissions class. Cited to disambiguate against any cross-talk.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the existing in-root launcher shape + the 2026-06-13 workaround record instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4530 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-13 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Seed both as scripts/ helpers"**, explicitly authorizing this scripts/ slice. The install-process / PATH-setup follow-on slice will declare its own authorization, including where the rendered shim is placed and how PATH is communicated to the user.

## Design

New module `scripts/install_gt_path_shim.py` — pure-Python, stdlib only. Public API:

1. **`resolve_venv_gt_exe(project_root, platform)` -> `pathlib.Path`**: returns the venv-internal `gt` executable path. On `platform == "win32"` returns `project_root / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"`. On POSIX (`linux`, `darwin`) returns `project_root / "groundtruth-kb" / ".venv" / "bin" / "gt"`. Pure path; no filesystem touch. Raises `ValueError` for an unsupported platform string.
2. **`render_windows_cmd_shim(venv_exe_path)` -> `str`**: returns the launcher's `.cmd` text content forwarding all args to the venv exe. Form: an `@echo off` line, a doc-comment header naming WI-4530 and the helper module, and `"<venv_exe>" %*` as the body. Pure-string; the venv-exe path is properly quoted to tolerate spaces.
3. **`render_posix_shell_shim(venv_exe_path)` -> `str`**: returns the launcher's `gt` (no extension) shell script content. Form: a `#!/usr/bin/env bash` shebang, a doc-comment header naming WI-4530 and the helper module, and `exec "<venv_exe>" "$@"` as the body. Pure-string; venv-exe path properly quoted.
4. **`render_for_platform(project_root, platform)` -> `dict[str, str]`**: convenience wrapper. Returns `{"filename": "gt.cmd"|"gt", "content": str, "venv_exe": str}`. Combines (1) + (2)/(3) so a caller gets everything needed for one call.

The module's `if __name__ == "__main__"` block emits the rendered content to stdout for manual use (e.g. `python scripts/install_gt_path_shim.py > gt.cmd`), with `--platform` (default to current `sys.platform`) and `--project-root` (default to `Path(__file__).resolve().parents[1]`) arguments. No file write, no PATH modification, no out-of-root placement — those are explicitly the follow-on install slice's responsibility.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_install_gt_path_shim.py`) | Method |
|---|---|---|
| Windows venv-exe path resolution (WI-4530 root) | `test_resolve_venv_gt_exe_windows` | `resolve_venv_gt_exe(root, "win32")` → returns `root/groundtruth-kb/.venv/Scripts/gt.exe` (path-string compare, no fs touch) |
| POSIX venv-exe path resolution | `test_resolve_venv_gt_exe_posix` | `resolve_venv_gt_exe(root, "linux")` → `root/groundtruth-kb/.venv/bin/gt`; same for "darwin" |
| Unsupported platform raises | `test_resolve_venv_gt_exe_unsupported_platform` | `resolve_venv_gt_exe(root, "freebsd")` → raises ValueError with a clear message |
| Windows .cmd content forwards all args to the venv exe | `test_windows_cmd_shim_forwards_args` | rendered content contains `@echo off`, contains the venv-exe path quoted, contains `%*` |
| POSIX shell shim is exec-able and forwards "$@" | `test_posix_shell_shim_uses_exec_and_quoted_args` | rendered content has the `#!/usr/bin/env bash` shebang, uses `exec`, contains the venv-exe path quoted, contains `"$@"` |
| Path with spaces is properly quoted on both platforms | `test_shim_quotes_path_with_spaces` | `render_*` invoked with a fixture project_root containing a space → quoted in output; smoke-parse the rendered text and assert the quoted span is intact |
| Convenience wrapper returns filename + content + venv_exe | `test_render_for_platform_shape` | `render_for_platform(root, "win32")["filename"]=="gt.cmd"`, `["content"]` matches `render_windows_cmd_shim(...)`, `["venv_exe"]==str(resolve_venv_gt_exe(root, "win32"))` |
| Helper does NOT write any file or modify PATH (in-root constraint preserved) | `test_helper_does_no_io` | inspect the module: assert no `Path.write_text`, no `open(...).write`, no `os.environ` mutation, no subprocess.run at import or in any public function |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_install_gt_path_shim.py -q --tb=short`.

## Risk / Rollback

- **Risk: very low.** Pure-Python content/path generator + its unit tests. No file write, no PATH mutation, no subprocess, no install-process change in this slice. The helper exists but no caller wires it yet, so it cannot affect any existing developer-environment behavior until the follow-on install slice lands.
- **Boundary discipline:** the WI's 2026-06-13 manual workaround placed `gt.cmd` at an out-of-root user-PATH directory. This slice explicitly does NOT do that — it stops at pure content generation, so any out-of-root placement decision is held over for the follow-on install slice where it can be discussed with the appropriate authorization and project-root-boundary review.
- **Rollback:** delete the two new files. No migration, no schema, no install-process change, no PATH change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (a deterministic launcher-shim content/path generator + its test suite), not a repair of existing broken behavior. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
