NEW

bridge_kind: implementation_report
Document: gtkb-wi4509-cutover-evidence
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ce76da9c-67eb-4f67-b540-521aeec05550
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4509

# Implementation Report (NEW -003) — WI-4509: TAFE Cutover Evidence Gathering

## Summary

WI-4509 is implemented and verified per the GO'd proposal (`-002` GO over `-001`).
A new **read-only** module `groundtruth-kb/src/groundtruth_kb/tafe_cutover_evidence.py`
gathers cutover evidence by comparing the Slice C ingest dry-run plan
(`tafe_bridge_ingestion.ingest_bridge_index(..., apply=False)`) against the canonical
`bridge/INDEX.md` and the Slice B completeness oracle
(`tafe_index_completeness.index_completeness_report`): parity, completeness,
contention-zero (idempotence), flow-completion-rate distribution, and
compatibility-view fidelity. A new `gt flow cutover-evidence` CLI (`--write-evidence`,
`--json`) drives it; evidence output lands under `.gtkb-state/cutover-evidence/`
(regenerable, non-canonical). The module writes nothing canonical or shadow and holds
no canonical-index path literal (`GOV-FILE-BRIDGE-AUTHORITY-001`).

**Stall-recovery provenance (transparency):** a dispatched peer
(`2026-06-14T02-55-28Z-prime-builder-B-55ecef`) authored the module + CLI + tests but
its `go_implementation` claim lapsed before it filed this report, leaving the work at
10/11 tests passing (1 Windows CRLF/LF test-fixture failure) and unreported, with no
swarm re-dispatch (the dispatcher fires on signature-change, not claim-lapse). The
interactive Prime completed the recovery under **explicit owner authorization
(AskUserQuestion this session)**: fixed the one failing test and two ruff issues,
re-verified all green, and filed this report. The owner authorization also covered
setting the `.claude/session/active-session-role.json` marker so the interactive Prime
became `go_implementation`-eligible (the WI-4540 init-keyword marker gap).

## Specification Links

- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — tracked evidence-gathering artifact gating the Phase-7 governed cutover (WI-4510).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — superseded WI-4496 dependency + deferred cutover handled by name.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decisions, ADR, WI-4509, tests linked.
- **ADR-TAFE-SLICE-C-INGESTION-001** — the canonical Slice C design whose shadow (D1/D2/D3 derivation) this evidence assesses.
- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — umbrella spec.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` stays authoritative; the tool is read-only.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — all governing specs cited.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each test derives from an evidence-category requirement (mapping below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all changed files in-root; evidence output under `.gtkb-state/` (non-canonical).

## Spec-to-Test Mapping

`groundtruth-kb/tests/test_tafe_cutover_evidence.py` — 11 tests, all passing:

| ADR / evidence requirement | Test(s) |
|---|---|
| Parity (ADR D1/D2/D3 derivation: one instance per thread, one artifact per version) | `test_parity_one_instance_per_thread_one_artifact_per_version`; `test_parity_mismatch_detected` |
| Completeness (Slice B lost/extra-block integration) | `test_completeness_surfaces_lost_and_extra_blocks` |
| Contention-zero / idempotence (ADR D4) | `test_contention_zero_repeat_plan_writes_nothing`; `test_contention_nonzero_when_shadow_unpopulated` |
| Flow-completion-rate distribution | `test_flow_completion_rate_distribution` |
| Compatibility-view fidelity (shadow round-trips INDEX latest-status) | `test_compatibility_view_round_trips_index_latest_status`; `test_fidelity_mismatch_detected` |
| CLI read-only + report shape; evidence under `.gtkb-state` | `test_cli_cutover_evidence_readonly_json`; `test_cli_cutover_evidence_write_evidence_under_gtkb_state` |
| Read-only contract (no canonical-index path literal — AST check) | `test_cutover_evidence_module_holds_no_canonical_index_path_literal` |

## Verification Performed

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_tafe_cutover_evidence.py -q --tb=short
```
Result: **11 passed** (4.05s pre-fix had 1 failure; post-fix 11/11 in ~2.88s).

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\tafe_cutover_evidence.py groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\tests\test_tafe_cutover_evidence.py
```
Result: **All checks passed!**

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check <same 3 files>
```
Result: **3 files already formatted.**

## Implementation Notes (recovery edits)

1. **`test_tafe_cutover_evidence.py`** — fixed `test_cli_cutover_evidence_write_evidence_under_gtkb_state`: the fixture wrote the INDEX with `Path.write_text` (which translates `\n`→`\r\n` on Windows) but the read-only-contract assertion at line 281 compared `read_bytes()` against the LF-`encode("utf-8")` expected, producing a spurious CRLF/LF mismatch. Changed the fixture to `write_bytes(...encode("utf-8"))` so the on-disk bytes are byte-identical LF. This was a **test-fixture bug, not a CLI bug** — the CLI is genuinely read-only (the evidence correctly lands under `.gtkb-state`; the canonical INDEX is unchanged).
2. **`cli.py`** — two ruff fixes in the `flow cutover-evidence` command: shortened the `--evidence-dir` help string (E501, was 123>120) and joined a split string literal (ruff format). No behavior change.
3. **WI-4509 dependency rewiring deferred:** the proposal called for dropping the superseded WI-4496 from WI-4509's `depends_on_work_items`. `gt backlog update` does not expose a `depends_on` field, so the governed-CLI rewiring is not possible here; WI-4496 is superseded so the dependency is moot (WI-4508/Slice C is VERIFIED and supplies the shadow). Flagging as a follow-on (CLI gap) rather than performing a raw `work_items` mutation.

## Owner Decisions / Input

- **Owner AskUserQuestion (this session)** — authorized the interactive Prime to set the `active-session-role` marker (correcting the WI-4540 init-keyword gap) and complete the stalled WI-4509 recovery (fix the failing test + file this report). This is the owner-approval evidence for the recovery edits.
- **DELIB-20263195** — owner AUQ authorizing the WI-4508→WI-4509→WI-4510 cutover sequence + the PAUTH covering WI-4509's `source`/`test_addition` scope.

## Recommended Commit Type

Recommended commit type: `feat:` — net-new read-only evidence module (`tafe_cutover_evidence.py`) + net-new `gt flow cutover-evidence` CLI subcommand + tests.
