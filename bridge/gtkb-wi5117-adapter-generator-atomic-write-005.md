NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4a33-6a08-79a3-96e5-1594436d319c
author_model: gpt-5-codex
author_model_version: 2026-07-10 runtime
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb; approval_policy=never

# GT-KB Bridge Implementation Report - gtkb-wi5117-adapter-generator-atomic-write - 005

bridge_kind: implementation_report
Document: gtkb-wi5117-adapter-generator-atomic-write
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5117-adapter-generator-atomic-write-004.md
Approved proposal: bridge/gtkb-wi5117-adapter-generator-atomic-write-003.md
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5117
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-TREE-STABILIZATION-WI-5117-ATOMIC-WRITE-AUTHORIZATION
Recommended commit type: fix:

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/generate_api_skill_adapters.py", "scripts/_wrap_io.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]

## Implementation Claim

WI-5117 is implemented within the approved GO scope. The adapter-generator write sites now use a shared atomic byte helper for final disk commits, preserving the existing change-detection and `--check` behavior while replacing direct write calls with same-directory temp write plus `os.replace`.

Completed changes:

- `scripts/_wrap_io.py` adds `_atomic_write_bytes(path, content)` beside the existing text helper, using `path.with_suffix(path.suffix + ".tmp")`, `write_bytes`, `os.replace`, and cleanup of the sibling temp file on exceptions.
- `scripts/generate_codex_skill_adapters.py` imports `_atomic_write_bytes` through a script-dir-safe import path and routes `_write_if_changed`, `_write_bytes_if_changed`, and registry updates through it.
- `scripts/generate_antigravity_skill_adapters.py` routes registry updates through `codex_gen._atomic_write_bytes`; adapter-body writes continue to reuse the codex generator helpers and are therefore covered by the same atomic byte route.
- `scripts/generate_api_skill_adapters.py` imports `_atomic_write_bytes` through a script-dir-safe import path and routes `_write_if_changed` through it.
- `platform_tests/scripts/test_generate_codex_skill_adapters.py` adds focused tests proving a simulated replace failure leaves the existing target intact and proving codex generation routes adapter writes through `_atomic_write_bytes`.
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` adds a focused test proving Antigravity generation routes adapter writes through the shared atomic byte helper.

No adapter content, registry schema, resource exclusion rule, `--check` semantics, deprecated `--update-registry` behavior, credential handling, deployment setting, or KB schema is intentionally changed.

## Design Note

The implementation deliberately uses `_atomic_write_bytes`, not `_atomic_write_text`, at the generator text-write sites. `_atomic_write_text` currently uses `Path.write_text` without `newline="\n"`, which can convert LF text to CRLF on Windows. The generator text sites already construct LF-only strings, so they encode those strings to UTF-8 bytes and pass the bytes to `_atomic_write_bytes`. This preserves the WI-4701 LF contract while gaining the WI-5117 atomic replace behavior.

## Implementation Authorization

- Work-intent claim acquired for `gtkb-wi5117-adapter-generator-atomic-write` as Prime Builder, claim kind `go_implementation`, rowid `31054`, session `019f4a33-6a08-79a3-96e5-1594436d319c`.
- Implementation-start packet created from the latest GO before source mutation:
  - `bridge_id`: `gtkb-wi5117-adapter-generator-atomic-write`
  - `go_file`: `bridge/gtkb-wi5117-adapter-generator-atomic-write-004.md`
  - `proposal_file`: `bridge/gtkb-wi5117-adapter-generator-atomic-write-003.md`
  - `packet_hash`: `sha256:621366cf883cda5232ce550b8972bd983fe465d707ca19775c28f163a69b2d95`
  - `Project Authorization`: `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-TREE-STABILIZATION-WI-5117-ATOMIC-WRITE-AUTHORIZATION`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-governed source/test change, approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authorization now established via the cited PAUTH.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH does not bypass the GO or the implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project / Work Item / Project Authorization metadata above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps focused tests to the linked specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are GT-KB platform files inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-5117 is the active backlog record for this defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - defect, proposal, verification, and report stay linked through governed artifacts.

## Owner Decisions / Input

- AskUserQuestion 2026-07-09 "File proposal now, authorize at GO" authorized filing the original proposal before the project authorization was established.
- AskUserQuestion 2026-07-10 selected "Scoped to WI-5117"; this owner decision is captured as `DELIB-202665932` and materialized as `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-TREE-STABILIZATION-WI-5117-ATOMIC-WRITE-AUTHORIZATION`.
- AskUserQuestion 2026-07-10 selected "Start WI-5117 now", authorizing implementation after WI-5095 was VERIFIED and committed (`fd36d92c`) and after LO returned GO on the revised proposal.
- No new owner decision is required by this implementation report. No credential change, deployment, force-push, external mutation, KB schema mutation, or sandbox weakening was requested or performed.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - tree-stabilization diagnosis that surfaced the adapter/scratch churn class this WI belongs to.
- `DELIB-202665932` - owner decision authorizing the WI-5117-scoped PROJECT-GTKB-TREE-STABILIZATION PAUTH.
- `bridge/gtkb-wi5117-adapter-generator-atomic-write-003.md` - revised approved implementation proposal with concrete PAUTH, target paths, and spec links.
- `bridge/gtkb-wi5117-adapter-generator-atomic-write-004.md` - Loyal Opposition GO authorizing implementation after WI-5095 completion.
- WI-5095 thread - VERIFIED and committed at `fd36d92c`, providing the committed base for the shared adapter-generator files.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| WI-5117 acceptance: adapter-generator writes use atomic final commits | `test_atomic_write_bytes_midwrite_failure_leaves_target_intact` patches `os.replace` behind `_atomic_write_bytes`, asserts `OSError` is raised, the pre-existing target remains `b"original\n"`, and no sibling `*.tmp` remains. |
| WI-5117 acceptance: codex generator write routing | `test_generate_routes_writes_through_atomic_bytes` in the codex generator suite spies on `module._atomic_write_bytes`, runs `module.generate(tmp_path)`, asserts `.codex/skills/review/SKILL.md` was written through the helper, and asserts the adapter bytes contain no CR bytes. |
| WI-5117 acceptance: Antigravity generator write routing | `test_generate_routes_writes_through_atomic_bytes` in the Antigravity generator suite spies on `module.codex_gen._atomic_write_bytes`, runs `module.generate(tmp_path)`, asserts `.agent/skills/review/SKILL.md` was written through the helper, and asserts the adapter bytes contain no CR bytes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Ran the full codex, Antigravity, and API adapter-generator platform test suites with writable `--basetemp .harness-tmp/wi5117`; ran `ruff check`; ran `ruff format --check`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Claimed the GO work intent and created the implementation-start packet from `-004` before editing protected source/test files. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed implementation/test files are inside the GT-KB root and match the approved `target_paths` list. |
| WI-4701 LF preservation regression | Existing LF-only generator tests still pass; direct byte scan of all six changed files showed `CR=0`. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_api_skill_adapters.py -q --tb=short --basetemp .harness-tmp/wi5117`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py`
- PowerShell LF byte scan over the six changed files using `[System.IO.File]::ReadAllBytes(...)` and counting CR/LF bytes.
- `git diff --check -- scripts/_wrap_io.py scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py`

## Observed Results

- Pytest collected 50 items and passed: `50 passed, 1 warning in 2.40s`. The warning was the pre-existing pytest config warning: `Unknown config option: asyncio_mode`.
- Ruff check passed: `All checks passed!`
- Ruff format check passed: `6 files already formatted`.
- LF byte scan results:
  - `scripts/_wrap_io.py`: `CR=0`, `LF=56`
  - `scripts/generate_codex_skill_adapters.py`: `CR=0`, `LF=501`
  - `scripts/generate_antigravity_skill_adapters.py`: `CR=0`, `LF=260`
  - `scripts/generate_api_skill_adapters.py`: `CR=0`, `LF=297`
  - `platform_tests/scripts/test_generate_codex_skill_adapters.py`: `CR=0`, `LF=687`
  - `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`: `CR=0`, `LF=450`
- `git diff --check` returned exit code 0 with no whitespace errors. Git emitted local autocrlf warnings that LF would be replaced by CRLF the next time Git touches the files; this is a Git working-tree policy warning, not a current-file byte finding. The direct byte scan above is the current-file evidence.

## Files Changed

- `scripts/_wrap_io.py`
- `scripts/generate_codex_skill_adapters.py`
- `scripts/generate_antigravity_skill_adapters.py`
- `scripts/generate_api_skill_adapters.py`
- `platform_tests/scripts/test_generate_codex_skill_adapters.py`
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`

The bridge filing itself will add `bridge/gtkb-wi5117-adapter-generator-atomic-write-005.md`. No other file is claimed under this implementation report.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: this repairs a reliability defect in existing adapter-generator writes by making final disk commits atomic while preserving the generated outputs and command behavior.

## Acceptance Criteria Status

- [x] Shared atomic byte helper added in `_wrap_io`.
- [x] Codex adapter file, resource byte, and registry write sites route through `_atomic_write_bytes`.
- [x] Antigravity registry writes route through `_atomic_write_bytes`; adapter-body writes remain covered through the codex generator helper reuse.
- [x] API adapter writes route through `_atomic_write_bytes`.
- [x] Simulated replace failure test proves existing target contents remain intact and temp files are cleaned up on exception.
- [x] Codex and Antigravity routing tests prove generated adapter writes pass through the atomic byte helper.
- [x] Existing generator regression suites pass, including LF-only and registry/source-hash stability tests.
- [x] Changed files are LF-only in the working tree.

## Pre-Filing Preflight Subsection

The bridge applicability and ADR/DCL clause preflights are run against this exact content file before filing:

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5117-adapter-generator-atomic-write-005.md`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-wi5117-adapter-generator-atomic-write-005.md`

Expected passing result: no missing required specs and `Blocking gaps: 0`.

## Risk And Rollback

Residual risks:

- A process kill between temp write and replace can leave a sibling `.tmp` file. The helper cleans temp files on exceptions; process-kill cleanup remains best-effort and does not endanger the existing target because the target is only replaced by `os.replace`.
- Git on this Windows checkout still warns that LF files may be converted to CRLF the next time Git touches them. Current working-tree bytes are LF-only; this implementation avoids `Path.write_text` for generator outputs to preserve LF bytes at generation time.

Rollback:

- Revert the six changed implementation/test files plus the bridge report file. No deployment, credential, external-service state, KB schema, or data migration rollback is in scope.

## Loyal Opposition Asks

1. Verify that the implementation remains within `bridge/gtkb-wi5117-adapter-generator-atomic-write-003.md` target paths and `-004.md` GO conditions.
2. Verify that `_atomic_write_bytes` is the correct LF-preserving route for text outputs on Windows.
3. Verify the executed tests and gates satisfy `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.
4. Return `VERIFIED` if the report and implementation satisfy the approved proposal; otherwise return `NO-GO` with findings.
