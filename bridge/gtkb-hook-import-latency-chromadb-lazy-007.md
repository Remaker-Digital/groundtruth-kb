# Post-Implementation Report: Lazy chromadb import to remove PreToolUse hook latency

Status: NEW
Document: gtkb-hook-import-latency-chromadb-lazy
Version: 007
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15
Session: S351
Responds to: bridge/gtkb-hook-import-latency-chromadb-lazy-006.md (Codex GO)
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3319

## Summary

The lazy-chromadb fix from `bridge/gtkb-hook-import-latency-chromadb-lazy-005.md`
(Codex GO at `-006`) has been implemented. Implementation began with the
implementation-start authorization packet created via
`python scripts/implementation_authorization.py begin --bridge-id gtkb-hook-import-latency-chromadb-lazy`.

`groundtruth_kb/db.py` no longer imports `chromadb` at module load. Importing
`groundtruth_kb` therefore no longer pays chromadb's ~6s opentelemetry/grpc
import chain. Measured: `from groundtruth_kb.governance.output import emit_pass`
went from ~6.4-8.0s to ~0.11s.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py` — three edits:
  1. Added `import importlib.util` to the stdlib import block.
  2. Replaced the module-level eager `try: import chromadb` block with
     `HAS_CHROMADB = importlib.util.find_spec("chromadb") is not None` (cheap,
     no package execution) plus a new `_load_chromadb()` lazy loader that
     imports `chromadb` on first use and, on `ImportError`, returns `None` and
     sets `HAS_CHROMADB = False`.
  3. `_get_chroma_collection()` now resolves the module via `_load_chromadb()`
     and returns `None` if it is unavailable, before constructing
     `chromadb.PersistentClient(...)`.
- `platform_tests/test_groundtruth_kb_import_budget.py` — new regression test
  file, four tests.

Both paths are within the GO-approved `target_paths`. The two
bridge-compliance-gate hook files were not modified; their byte-identical
parity contract is untouched.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — implemented under the file-bridge protocol, GO at `-006`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — specification links carried forward from the GO'd proposal `-005`.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec-to-test mapping and executed-command evidence are in the Specification-Derived Verification section below.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — the report carries the `Project Authorization`, `Project`, and `Work Item` metadata.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both changed paths resolve inside `E:\GT-KB`; no path under `applications/`, none outside the root.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — tracked as WI-3319 with deliberation DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability preserved across proposal, tests, and this report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — this report moves the thread toward the VERIFIED lifecycle state.
- `.claude/rules/file-bridge-protocol.md` — the protocol governing this report.
- `.claude/rules/codex-review-gate.md` — the review gate; this report is filed for VERIFIED review.
- `bridge/gov-process-spec-precondition-2026-04-29-005.md` — the byte-identical hook/template parity contract; satisfied unchanged (no hook file touched).

## Specification-Derived Verification

Spec-to-test mapping and observed results. All commands run from `E:\GT-KB`.

### Acceptance criterion 1 — `import groundtruth_kb` does not import chromadb

Command:
```
python -c "import sys, groundtruth_kb; leaked=[m for m in sys.modules if m=='chromadb' or m.startswith('chromadb.')]; print(leaked or 'NONE')"
```
Observed: `chromadb in sys.modules after import groundtruth_kb: NONE`.
Test: `test_chromadb_not_eagerly_imported` — PASSED.

### Acceptance criterion 2 — import latency reduced to well under 1s

Command: `python -X importtime -c "from groundtruth_kb.governance.output import emit_pass"`
Observed (after fix):
```
import time:       556 |     110418 |     groundtruth_kb
import time:       498 |     110927 | groundtruth_kb.governance.output
```
`groundtruth_kb.governance.output` cumulative import = 110,927 us (~0.11s),
down from the ~6.4-8.0s baseline recorded in the proposal; `chromadb` no
longer appears in the importtime output at all.

### Acceptance criterion 3 — HAS_CHROMADB remains an eager bool

Test: `test_has_chromadb_is_eager_bool` — PASSED.

### Acceptance criterion 4 — lazy-import ImportError degrades gracefully

Test: `test_lazy_chromadb_import_failure_degrades_gracefully` — PASSED
(simulates `find_spec` success with `import chromadb` raising `ImportError`;
asserts `_load_chromadb()` returns `None`, `HAS_CHROMADB` becomes `False`, and
`search_deliberations()` still returns SQLite-LIKE results without raising).

### Acceptance criterion 5 — semantic search unchanged

Command:
```
python -m pytest groundtruth-kb/tests/test_deliberations.py groundtruth-kb/tests/test_cli_deliberations.py groundtruth-kb/tests/adopter/test_overlay_refresh.py groundtruth-kb/tests/adopter/test_overlay_disposability.py groundtruth-kb/tests/test_operating_state.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py
```
Observed: `1 failed, 128 passed, 1 warning in 73.64s`.

The single failure was
`platform_tests/scripts/test_codex_bridge_compliance_gate.py::test_audit_only_accepts_compliant_files_without_blocking`
with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1` reading
the audit file. This test was re-run in isolation three times and PASSED all
three (`1 passed in 0.57s / 0.35s / 0.68s`). It is a pre-existing flaky test:
the bridge-compliance-gate `--audit-only` mode writes a FIXED shared path
(`.codex/gtkb-hooks/last-bridge-audit.json`), and concurrent writers during a
full-suite run race on it. The failure is unrelated to this change — `db.py`'s
lazy-chromadb edit does not touch the audit-file path or audit logic — and is
out of this proposal's `target_paths` scope. It has been flagged for separate
remediation as a test-isolation defect (a reliability-fast-lane candidate).

### Acceptance criterion 6 — hook parity preserved

Neither `.claude/hooks/bridge-compliance-gate.py` nor
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` was modified.
`test_hook_matches_template_or_documented_divergence` (in the executed
`platform_tests/hooks/...` suite) is among the 128 passing tests.

### Acceptance criterion 7 — new import-budget tests pass

Command: `python -m pytest platform_tests/test_groundtruth_kb_import_budget.py -v`
Observed: `4 passed, 1 warning in 1.48s`
(`test_chromadb_not_eagerly_imported`, `test_has_chromadb_is_eager_bool`,
`test_lazy_chromadb_loads_on_demand`, `test_lazy_chromadb_import_failure_degrades_gracefully`).

### Lint

Command: `python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py platform_tests/test_groundtruth_kb_import_budget.py`
Observed: `All checks passed!`

## Recommended Commit Type

`perf:` — the change removes ~7s of dead import latency from the
`import groundtruth_kb` critical path (paid by 7 hooks and the `gt` CLI) with
no behavior change. The semantic-search and `HAS_CHROMADB`-contract behavior
is preserved, verified by the regression suite and the new tests.

## Owner Decisions / Input

- The owner tasked this fix in S351 and approved the project/work-item/
  authorization chain via AskUserQuestion, archived as
  `DELIB-S351-HOOK-IMPORT-LATENCY-AUTHORIZATION`.
- No further owner decision is required for verification. The one regression
  failure is documented above as a pre-existing, out-of-scope flaky test with
  isolation-run evidence; no owner waiver is sought because the failing test
  does not cover any specification linked to this change.
