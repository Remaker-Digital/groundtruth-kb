NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-15T01-38-26Z-prime-builder-B-b02baf
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code bridge auto-dispatch Prime Builder session; explanatory output style

# WI-4566 — Post-Implementation Report: gt bridge index remove-document (phantom-only INDEX entry removal)

bridge_kind: implementation_report
Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-B-RESIDUAL-CLEANUP-WI-4566
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4566
Responds to: bridge/gtkb-bridge-index-remove-document-002.md (GO, Loyal Opposition / Antigravity harness C)
target_paths: ["scripts/gtkb_bridge_writer.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "groundtruth-kb/tests/test_cli_bridge_index.py"]

## Summary

The GO'd phantom-only `gt bridge index remove-document <slug>` primitive is implemented
across all four `target_paths`. The implementation reuses the existing serialized-writer
lock + `atomic_index_update` read-modify-write path (identical to `insert_index_status` /
`add_document`), enforces the phantom-only guardrail (refuse when any
`bridge/<slug>-NNN.md` backing file exists), raises explicit not-found for an absent slug,
removes the `Document:` block surgically (the `Document:` line plus its contiguous
status/comment lines plus one trailing blank separator), and double-verifies the post-write
state (byte-match of the written content AND live-state confirmation that the block is
gone). The CLI command wires to the writer, catches `writer.BridgeError`, and emits JSON or
human output.

This report performs no MemBase mutation (no KB write to `groundtruth.db`); the WI-4566
backlog disposition is a separate downstream operational step out of this report's scope.
Staged diff is **4 files changed, 306 insertions(+)** — purely additive; no deletions, no
schema change. All net-new capability surface, hence `feat:`.

**Step 4 (operational phantom removal) is NOT performed in this report.** The proposal scopes
it as "post-VERIFY, operational" — applying
`gt bridge index remove-document sp1-dispatch-reliability-prime-handoff` and confirming the
cutover-evidence gate follows the VERIFIED verdict on this report. The governed cutover
itself remains HELD and OUT OF SCOPE (its own separate fresh owner AUQ).

## Specification Links

(Carried forward verbatim from the GO'd proposal `-001`; cited again here so the
verification gate can map each to a test.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical; INDEX mutations only via
  the serialized writer. The new primitive is a sanctioned INDEX-mutation surface; removal is
  restricted to phantom (no-backing-file) entries to preserve the never-delete-real-threads
  audit invariant.
- `DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` — the completeness contract whose
  `CutoverEvidenceReport.ok` (`extra_blocks == []`) this primitive unblocks (operationally,
  post-VERIFY).
- `ADR-TAFE-SLICE-C-INGESTION-001` — the cutover-evidence derivation cleared by removing the
  phantom (post-VERIFY).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below; tests
  executed against the implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` +
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — phantom-INDEX-entry reconciliation is an
  artifact-lifecycle disposition.
- `GOV-STANDING-BACKLOG-001` — WI-4566.

## Implemented Changes

**`scripts/gtkb_bridge_writer.py`** (+92): adds `remove_document(document_name, project_root)`
and the `_phantom_backing_files` helper. The mutate closure runs inside `atomic_index_update`
(serialized lock); it (1) refuses via `BridgeConflictError` when backing files exist; (2)
raises `BridgeConflictError` not-found when the `Document:` block is absent; (3) surgically
drops the block; (4) post-write byte-match + live-state re-read verification. The backing-file
matcher is anchored (`^{slug}-\d{3,}\.md$`) so a prefix-sharing sibling (`foo-bar-001.md`)
does NOT count as backing for phantom `foo`.

**`groundtruth-kb/src/groundtruth_kb/cli_bridge_index.py`** (+54): adds the
`remove-document <document_slug>` command (`--json` flag), loading the standalone scripts
writer, catching `writer.BridgeError` (superclass of `BridgeConflictError`, confirmed), and
emitting `{"document", "removed": true, "index_path"}` JSON or a human line.

**`platform_tests/scripts/test_gtkb_bridge_writer.py`** (+77): 5 writer tests.

**`groundtruth-kb/tests/test_cli_bridge_index.py`** (+83): 3 CLI tests.

## Spec-Derived Verification — Spec-to-Test Mapping

| Linked specification | Verifying test(s) | Asserts |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (phantom-only, never-delete-real-thread, serialized canonical writer) | `test_remove_document_guardrail_refuses_backed_slug`; `test_remove_document_guardrail_ignores_prefix_sharing_sibling`; `test_cli_remove_document_refuses_backed_slug` | Removal raises and leaves INDEX untouched when a backing file exists; an anchored prefix-sibling does not count as backing; CLI refuses a backed slug |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (surgical, audit-preserving mutation via serialized path) | `test_remove_document_removes_phantom_block`; `test_remove_document_is_surgical_and_preserves_order`; `test_cli_remove_document_removes_phantom` | Phantom block removed; sibling blocks + order preserved; CLI happy-path + JSON shape |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (fail-closed on absent target) | `test_remove_document_absent_slug_raises_not_found`; `test_cli_remove_document_absent_slug_fails_closed` | Absent slug raises not-found; INDEX unchanged |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full suite (64 tests) | Every required behavior exercised; no collateral regression |

`DCL-TAFE-COMPLETENESS-TERMINAL-ARCHIVED-001` / `ADR-TAFE-SLICE-C-INGESTION-001` are verified
operationally **post-VERIFY** via `gt flow cutover-evidence --json` (`extra_blocks == []`,
`ok == True`); that step is intentionally deferred per the proposal's Step 4 scoping and is
not claimed in this report.

## Commands Executed and Observed Results

```text
python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py \
  groundtruth-kb/tests/test_cli_bridge_index.py -k "remove_document" -q
  => 8 passed, 56 deselected in 0.92s   (5 writer + 3 CLI)

python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py \
  groundtruth-kb/tests/test_cli_bridge_index.py -q
  => 64 passed in 1.61s   (full files; no collateral regression)

python -m ruff check <4 target_paths>
  => All checks passed!

python -m ruff format --check <4 target_paths>
  => 4 files already formatted

python -c "issubclass(BridgeConflictError, BridgeError)"  => True
  (confirms the CLI `except writer.BridgeError` catches the guardrail/not-found raises)

git diff --cached --stat <4 target_paths>
  => 4 files changed, 306 insertions(+)   (purely additive)
```

## Owner Decisions / Input

- AskUserQuestion (proposal session `c2f8c28a`, carried forward from `-001`): the owner chose
  **"Build remove-document verb"** to close the last cutover-evidence gap. The governed
  cutover itself remains a separate fresh-AUQ decision and is NOT authorized by this proposal
  or report. No new owner decision is required to VERIFY this implementation; the operational
  phantom-removal and the governed cutover are separate downstream gates.

## Recommended Commit Type

`feat:` — adds the net-new phantom-only `remove_document` writer primitive + `remove-document`
CLI command (+306 lines, all additive; no behavior change to existing surfaces). Matches the
proposal's recommendation and the GO verdict's `Recommended commit type: feat:`.

## Risk / Rollback

- Removing a real thread's INDEX entry is impossible by construction (phantom-only guardrail,
  tested two ways including the prefix-sibling edge case).
- INDEX corruption under concurrent writes is prevented by reusing the serialized-writer lock
  + atomic-index-update path; post-write byte-match and live-state re-read add defense in depth.
- Rollback: revert the additive writer + CLI changes; no schema change, no canonical-content
  loss. The phantom line (if ever removed operationally) is a no-backing-file entry recoverable
  from git history.
