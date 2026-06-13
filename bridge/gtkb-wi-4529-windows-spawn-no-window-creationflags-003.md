NEW

# Windows Spawn No-Window Flag for Bridge-Dispatch Subprocesses — Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi-4529-windows-spawn-no-window-creationflags
Version: 003
Responds to: bridge/gtkb-wi-4529-windows-spawn-no-window-creationflags-002.md (GO)
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-13T18-42-48Z-prime-builder-B-23d5f4
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch worker; Prime Builder durable role; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4529-WINDOWS-SUBPROCESS-CREATE-NO-WINDOW
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4529

target_paths: ["scripts/run_with_status.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_run_with_status.py"]

implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd proposal (`-001`, GO at `-002`). Every subprocess in the
bridge-dispatch path now passes the Windows-conditional no-window flag
consistently (trigger → wrapper → harness shim tool calls).

Implementation-start authorization packet:
`sha256:8657e83c5038d280c3802286278bb7bb94f465cf9ff9bf9e6e384c236e3fb8f0`
(derived from the live latest-`GO` entry; covers all four `target_paths`).

### Changes made

1. **Primary fix — `scripts/run_with_status.py`.** Computed
   `creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0`
   and passed it to the `subprocess.Popen(...)` call that runs every dispatched
   harness. A short comment documents the rationale and the
   `cross_harness_bridge_trigger.py` precedent. Additionally, `main()` now
   accepts an optional `argv` parameter (`def main(argv: list[str] | None = None)`)
   defaulting to `sys.argv[1:]`. This testability refactor is exactly what the
   approved proposal's verification plan anticipated
   (`run_with_status.main([status_file, ...])`); production callers
   (`if __name__ == "__main__": main()`) are unaffected.

2. **Defense in depth — `scripts/ollama_harness.py`.** Applied the same
   Windows-conditional `creationflags` to both worker-side `subprocess.run(...)`
   sites: `_default_guard_runner` (runs the guard adapter) and
   `_default_command_runner` (runs LLM-emitted Bash with `shell=True`).

3. **Defense in depth — `scripts/openrouter_harness.py`.** Identical treatment
   at the matching `_default_guard_runner` and `_default_command_runner` sites.

4. **Test — `platform_tests/scripts/test_run_with_status.py` (new).** Three
   tests covering the Windows-positive, non-Windows-negative, and exit-code
   propagation cases via a recording `Popen` stub and `os.name` monkeypatch.

`git diff --stat` (source) + new untracked test:

```text
 scripts/ollama_harness.py     |  4 ++++
 scripts/openrouter_harness.py |  4 ++++
 scripts/run_with_status.py    | 12 ++++++++++--
 3 files changed, 18 insertions(+), 2 deletions(-)
?? platform_tests/scripts/test_run_with_status.py
```

All four paths are under `E:\GT-KB`; none under `applications/`
(`ADR-ISOLATION-APPLICATION-PLACEMENT-001` satisfied).

## Specification Links

Carried forward from the proposal (`-001`):

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge dispatch substrate hardened; INDEX
  remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs
  cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project/WI/PAUTH metadata
  present in header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `REQ-HARNESS-REGISTRY-001` — registry argv vectors unchanged; only the wrapping
  subprocess's Windows creationflags changed.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — Windows-conditional behavior derives from
  a fresh `os.name` check at spawn time (clause c).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact graph preserved
  (WI-4529 → DELIB-20263188 → PAUTH → proposal → tests → this report → VERIFIED).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — bridge thread lifecycle advanced
  (NEW → GO → implementation report).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decision → DELIB → PAUTH →
  bridge governed chain.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths in-root.

## Spec-to-Test Mapping

| Linked spec | Derived test / verification | Result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` (spawn decision from fresh `os.name`; argv carried through) | `test_popen_uses_create_no_window_on_windows_via_monkeypatch` (asserts `creationflags == CREATE_NO_WINDOW` and the `0x08000000` bit is set when `os.name == "nt"`) and `test_popen_uses_no_creationflags_off_windows` (asserts `creationflags == 0` otherwise) | PASS |
| Wrapper exit-code propagation (no behavioral regression) | `test_status_file_records_exit_code` (status file records `0`) | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all changed paths in-root) | `git diff --stat` review | PASS — all paths under `E:\GT-KB` |
| All changed-file Python conformance | `ruff check` + `ruff format --check` on the four target paths | `format --check`: PASS (all 4 formatted). `check`: see Pre-existing lint note below |
| `GOV-FILE-BRIDGE-AUTHORITY-001` + linkage/testing DCLs | applicability preflight + clause preflight (below) | PASS |

## Test Execution Evidence

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe` (project venv). Note: the
venv lacks `pytest-timeout`, so the pyproject `--timeout=30` addopt was cleared
with `-o addopts=""` for the run; this affects only the timeout plugin, not the
assertions.

```text
$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py -o addopts="" -q --no-header
3 passed, 1 warning in 0.19s

$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_ollama_harness.py -o addopts="" -q --no-header
35 passed, 1 warning in 0.84s

$ groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_routing_deepseek.py -o addopts="" -q --no-header
6 passed, 1 warning in 0.25s

$ groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_run_with_status.py
4 files already formatted        # exit 0
```

The ollama (32) and openrouter (6) regression suites confirm the
defense-in-depth `creationflags` additions to the shim subprocess sites did not
break existing harness behavior.

### Pre-existing lint note (out of scope)

`ruff check` on `scripts/run_with_status.py` reports 4 findings — `SIM115`
(context-manager for `open()`) at lines 44/50/56 and `UP015` (unnecessary `"r"`
mode) at line 44. These are on the original `open()` calls that this change does
**not** touch. Verified pre-existing on `HEAD`:

```text
$ git show HEAD:scripts/run_with_status.py > /tmp/rws_head.py
$ ruff check /tmp/rws_head.py
Found 4 errors.   # identical findings, exit 1
```

They are outside the WI-4529 scope (the authorization packet scopes this work to
`creationflags` only) and `SIM115` would require a behavior-affecting refactor of
the file-handle lifecycle. Per GOV-06/scope discipline they are left untouched
and recorded here rather than silently absorbed. `ruff check` on the other three
changed files (`ollama_harness.py`, `openrouter_harness.py`,
`test_run_with_status.py`) is clean.

## Applicability Preflight

- packet_hash: `sha256:a4ccbb8f6685289c14ca834ecde00009d524f32a75c9e192e756b2cf8168b051`
- bridge_document_name: `gtkb-wi-4529-windows-spawn-no-window-creationflags`
- content_source: `indexed_operative`
- operative_file: `bridge/gtkb-wi-4529-windows-spawn-no-window-creationflags-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi-4529-windows-spawn-no-window-creationflags`
- Clauses evaluated: 5 — must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit 0 (pass).

## Prior Deliberations

- `DELIB-20263188` (2026-06-13) — owner_conversation / owner_decision capturing
  the owner's observation of empty `C:\Python314\python.exe` console windows and
  the explicit "Yes" authorization to capture WI-4529. Direct basis for the
  proposal and this implementation.

## Owner Decisions / Input

This work depends on owner approval, captured durably:

- `OWNER-CHAT-2026-06-13-WI4529` / `DELIB-20263188` (source_type
  `owner_conversation`, outcome `owner_decision`, work_item_id `WI-4529`): the
  owner observed the console-window accumulation and answered "Yes" to capturing
  WI-4529. That decision authorized the WI, the bounded PAUTH, the proposal, and
  this implementation. No further owner decision is required; LO verification is
  the next gate.

## Recommended Commit Type

`fix:` — corrects a latent Windows UX defect in the dispatch wrapper (the wrapper
was always missing the `creationflags` argument the outer trigger already had).
Not a new capability surface; not a refactor (the `main(argv=...)` parameter is a
minimal testability seam, behavior-preserving for production callers). The
defense-in-depth shim additions are part of the same fix surface.

## Verification Request

Requesting LO verification (`VERIFIED` or `NO-GO`) against the linked
specifications and the spec-to-test mapping above. The wrapper-side
`creationflags` behavior is covered by the new monkeypatched unit tests; the
shim-side defense-in-depth additions are covered indirectly by the passing
harness regression suites (the `creationflags` argument is accepted by
`subprocess.run` and is a no-op off Windows).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
