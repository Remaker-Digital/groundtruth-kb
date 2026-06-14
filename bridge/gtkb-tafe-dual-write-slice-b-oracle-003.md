NEW

bridge_kind: implementation_report
Document: gtkb-tafe-dual-write-slice-b-oracle
Version: 003
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-13T23-22-09Z-prime-builder-B-dd38e2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code auto-dispatched bridge worker; Prime Builder; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_completeness.py"]

implementation_scope: source, test
requires_review: false
requires_verification: true

---

# Implementation Report — TAFE Dual-Write Slice B: External Expected-Document Oracle + Lost-Block Detection (read-only) (WI-4508)

## Summary

Implemented the GO'd Slice B read-only oracle (`bridge/gtkb-tafe-dual-write-slice-b-oracle-002.md`) exactly within the three authorized `target_paths`. The work completes the absent-from-text lost-block diagnostic that Slice A (`tafe_index_sync.py`) explicitly deferred, by scanning the `bridge/` directory as the external expected-document oracle and diffing it against the parsed canonical INDEX.

No TAFE write, no schema change, no canonical-INDEX write surface, no concurrency surface was added. The implementation honors the GO's three review notes:

- **RN1** — the filesystem scan is a diagnostic oracle only; `bridge/INDEX.md` remains the sole authoritative queue state. Unindexed bridge files are reported as *candidate* lost blocks, never treated as workflow-authoritative entries.
- **RN2** — parked-draft handling is report-only; the module mutates no INDEX/MemBase/bridge state based on findings (documented in the module docstring + surfaced in the CLI summary as review candidates).
- **RN3** — no `tafe_index_ingest.py`, `gt flow ingest-parity`, TAFE shadow write, generated canonical INDEX output, dispatch-substrate change, or WI-4510 cutover surface was introduced.

## Files Changed (this work only)

- `groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py` — **new** read-only oracle module: `ExpectedDocument`, `IndexCompletenessReport` (with `.ok`/`.as_dict()`), `scan_expected_documents(project_root)`, `index_completeness_report(index_text, project_root)`. Reuses the VERIFIED Slice A `parse_bridge_index` for the present set; does no canonical write, no `open()`, no subprocess, no MemBase mutation.
- `groundtruth-kb/src/groundtruth_kb/cli.py` — **additive** new `gt flow index-completeness` subcommand (read-only; `--index-path`, `--out`, `--json`). Reuses the existing `_targets_canonical_bridge_index` refusal guard; exit codes 1 = lost blocks, 2 = refused canonical-write target, 3 = index not found. Slice A's `gt flow index-parity` is untouched.
- `groundtruth-kb/tests/test_tafe_index_completeness.py` — **new** 15-test suite (scan, diff, parser-reuse, CLI clean/lost/missing/refusal/out, AST read-only + canonical-token guards).

(The broader working tree contains unrelated uncommitted bridge files from concurrent sessions; those are NOT part of this work and were not authored here. This implementation is confined to the three `target_paths` above.)

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — governing umbrella spec; Slice B completes the complete/no-lost-blocks half of the lossless+complete parallel-view integrity prerequisite.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — canonical `bridge/INDEX.md` remains authoritative; the oracle reads the index + scans `bridge/` and writes nothing canonical; CLI `--out` refuses any target resolving to `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs carried forward (header + this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4508 is an active member of PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE under the cited cutover PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each behavior has a derived, executed test (mapping below).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all three `target_paths` are in-root under `E:\GT-KB\groundtruth-kb`; no application/adopter surface touched.
- `GOV-STANDING-BACKLOG-001` — WI-4508 is the backlog authority for the dual-write work.

## Prior Deliberations

- `DELIB-20263195` — owner AUQ (2026-06-13) authorizing the WI-4508 → WI-4509 → WI-4510 cutover sequence; basis for the governing PAUTH.
- `bridge/gtkb-tafe-dual-write-index-parity-004.md` (GO at `-005`) — Slice A proposal that defined Slice B and deferred the lost-block oracle implemented here.
- `bridge/gtkb-tafe-dual-write-index-parity-006.md` / `-007.md` — Slice A implementation report + VERIFIED; the `tafe_index_sync.py` deferral comment is the direct predecessor of this work.
- `bridge/gtkb-tafe-dual-write-index-parity-002.md` / `-003.md` — the Codex NO-GO whose P1 ("no in-text oracle for lost blocks") this slice resolves with the external oracle.

## Owner Decisions / Input

Owner directive `DELIB-20263195` (AskUserQuestion) authorized the WI-4508→4509→4510 cutover sequence and minted the governing PAUTH, preserving per-WI/slice bridge review. No new owner decision is required for this read-only slice; the irreversible cutover (WI-4510) remains owner-AUQ-gated and is untouched. The proposal's Owner Decisions / Input section (carried into the GO) recorded the S438 "Drive Slice B now" AUQ answer that authorized proceeding with this slice's implementation.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` + WI-4508 + the Slice A deferral fully specify the lost-block-oracle need. Because the slice is read-only and makes no flow-mapping decisions, no ADR/DCL or new requirement was needed (that ADR governs the deferred Slice C ingestion only).

## Spec-to-Test Mapping

| Spec / behavior | Test (`tests/test_tafe_index_completeness.py`) | Executed | Result |
|---|---|---|---|
| `SPEC-…-UMBRELLA` — expected-document scan completeness | `test_scan_finds_all_bridge_slugs`, `test_scan_excludes_index_and_nonversioned`, `test_scan_empty_when_no_bridge_dir` | yes | PASS |
| Lost-block detection (Slice A's deferred class) | `test_report_detects_lost_block` | yes | PASS |
| Extra-block (phantom INDEX entry) detection | `test_report_detects_extra_block` | yes | PASS |
| Parity → ok | `test_report_ok_when_index_matches_bridge_dir` | yes | PASS |
| Slice A parser reuse (no re-implementation) | `test_uses_slice_a_parser` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — read-only contract + `--out` refusal | `test_cli_index_completeness_json`, `test_cli_exits_nonzero_on_lost_block`, `test_cli_index_not_found`, `test_cli_refuses_canonical_write_target`, `test_cli_out_writes_report_to_non_canonical_path` | yes | PASS |
| Read-only module guarantee (no write surface) | `test_module_is_read_only`, `test_module_no_subprocess_no_mutation` | yes | PASS |
| CLI canonical refusal-guard retained (AST) | `test_cli_command_retains_canonical_refusal_token` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed commands below | yes | PASS |

## Verification Evidence (commands + results)

```text
python -m pytest groundtruth-kb/tests/test_tafe_index_completeness.py -q --tb=short
  → 15 passed in ~1.0–1.6s

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_index_completeness.py
  → All checks passed!

python -m ruff format --check (same three files)
  → 3 files already formatted

python -m groundtruth_kb flow index-completeness --json   (live snapshot smoke run)
  → status: lost_blocks_found; mutated: False; present_count: 312; expected_count: 946;
    lost_blocks: 635 (historical bridge files trimmed from INDEX per the documented
    Index-Maintenance routine — benign review candidates, NOT corruption);
    extra_blocks: 1 (sp1-dispatch-reliability-prime-handoff phantom INDEX entry).
    CLI exited 1 (lost blocks present), confirming the non-zero-exit contract.
```

The live smoke run demonstrates the oracle's read-only diagnostic value end-to-end and confirms `mutated: False`: no canonical bridge state, no TAFE table, and no MemBase state was written. The `--out bridge/INDEX.md` refusal is proven by `test_cli_refuses_canonical_write_target` (exit 2 for `bridge/INDEX.md`, `./bridge/INDEX.md`, and `BRIDGE/index.md`).

## Read-Only / No-Mutation Evidence

- Module AST guards (`test_module_is_read_only`, `test_module_no_subprocess_no_mutation`): no file-write attr (`write_text`/`write_bytes`/`writelines`/`write`), no `open()`, no `subprocess`, no MemBase mutator (`insert_`/`update_`/`delete_`/`resolve_`/`promote_`/`retire_`), and no bare `bridge/INDEX.md` literal in the module.
- CLI write path is limited to the optional `--out` JSON report, which refuses any canonical-index target via the shared `_targets_canonical_bridge_index` guard.
- Live smoke confirmed `mutated: False`.

## Recommended Commit Type

Recommended commit type: `feat:` — adds the lost-block/completeness oracle module + a new read-only `gt flow index-completeness` CLI surface (net-new capability completing Slice A's deferred diagnostic). Matches the `feat` recommendation Codex applied to the Slice A VERIFIED.

## Risk / Rollback

Read-only; no canonical state, schema, or concurrency surface introduced. Rollback = delete the new module + test and revert the single additive `cli.py` subcommand; nothing on-disk to undo. Known benign behavior: parked drafts and INDEX-maintenance-trimmed historical files appear in `lost_blocks` as review candidates (documented in the module docstring and CLI summary); a `--exclude-parked` allowlist is a deferred Slice-C/cutover refinement.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
