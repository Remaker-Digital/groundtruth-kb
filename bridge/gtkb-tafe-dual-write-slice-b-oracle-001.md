NEW

bridge_kind: prime_proposal
Document: gtkb-tafe-dual-write-slice-b-oracle
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder; explanatory output style; autonomous TAFE drive

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_completeness.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Implementation Proposal — TAFE Dual-Write Slice B: External Expected-Document Oracle + Lost-Block Detection (read-only) (WI-4508)

## Summary

Slice A (VERIFIED at `bridge/gtkb-tafe-dual-write-index-parity-007.md`) delivered the lossless `bridge/INDEX.md` parser + text-observable integrity diagnostics (`groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py`). Its docstring explicitly defers the one diagnostic it cannot do from text alone: "it cannot detect a document block that is *already absent* from `index_text`. Lost-block (absent-from-text) detection requires an external expected-document oracle and is explicitly deferred to Slice B."

This proposal delivers that deferred piece as a **read-only external expected-document oracle**. It scans the `bridge/` directory — the filesystem source of truth for which bridge documents exist — builds the expected slug inventory, and diffs it against the parsed canonical INDEX:

- **lost blocks** = slugs with `bridge/<slug>-NNN.md` files on disk but NO `Document:` entry in INDEX (the absent-from-text class Slice A deferred);
- **extra blocks** = `Document:` entries in INDEX with no matching `bridge/<slug>-*.md` files (a phantom-reference advisory).

It is exposed as a new read-only CLI `gt flow index-completeness`. **No TAFE writes, no schema change, no canonical-INDEX write surface, zero concurrency risk** — the same read-only contract as Slice A.

## Slice Scoping (transparent re-scope of the -004 Slice B)

The `-004` proposal lumped Slice B as "bridge-document → TAFE-flow ingestion mapping + TAFE persistence (the literal 'second write') + TAFE-vs-canonical parity, plus lost-block detection," and noted it "will require a design constraint/ADR before implementation." This proposal **splits that**:

- **Slice B (this proposal):** the read-only oracle + lost-block/extra-block detection. It makes **no design decisions** — it only scans and diffs — so it needs **no ADR** and carries **no mutation risk**. It is the smaller, safer half, and it completes the integrity-diagnostic suite (Slice A text-observable + Slice B lost-block) that any cutover-parity evidence (WI-4509) must rest on.
- **Slice C (deferred follow-on; NOT in this proposal):** the bridge-document → TAFE `flow_instances`/`flow_artifacts` ingestion (the literal "second write"). This carries the genuine ADR-worthy decisions the `-004` flagged — `flow_definition` selection, `subject_id` derivation, status-token → stage semantics, idempotency under concurrent INDEX writers. It will be captured as a distinct WI with a focused ADR before any TAFE write surface is added.

Splitting along the ADR boundary is faithful to the project's phased-slice philosophy (each slice removes one way the eventual cutover could silently corrupt canonical state). The LO is invited to review this scoping explicitly.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — governing umbrella spec; this slice completes the lossless+complete "parallel view" integrity prerequisite for an authoritative generated INDEX (Slice A = lossless; Slice B = complete/no-lost-blocks).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — canonical `bridge/INDEX.md` remains authoritative; the oracle reads the index + the `bridge/` directory and writes nothing canonical. The CLI refuses any `--out` resolving to `bridge/INDEX.md` (reuses Slice A / WI-4507 guard intent).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, project authorization, and governing specs linked (this section + header).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable `Project Authorization:` / `Project:` / `Work Item:` metadata present.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` — WI-4508 is an active member of PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE under the cited cutover PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan derives a test per behavior (mapping below).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all three `target_paths` are in-root under `E:\GT-KB\groundtruth-kb`; no application/adopter surface is touched.
- `GOV-STANDING-BACKLOG-001` — WI-4508 is the backlog authority for the dual-write work.

## Prior Deliberations

- `DELIB-20263195` — owner AUQ (2026-06-13) authorizing the full TAFE cutover sequence WI-4508 → WI-4509 → WI-4510; basis for `PAUTH-…-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510`.
- `bridge/gtkb-tafe-dual-write-index-parity-004.md` (GO at `-005`) — the Slice A proposal that DEFINED Slice B and deferred the lost-block oracle. This proposal implements the read-only half of that deferral and re-scopes the ingestion half to Slice C.
- `bridge/gtkb-tafe-dual-write-index-parity-006.md` / `-007.md` — the Slice A implementation report + VERIFIED verdict; the deferral comment in `tafe_index_sync.py` is the direct predecessor of this work.
- `bridge/gtkb-tafe-dual-write-index-parity-002.md` / `-003.md` — the Codex NO-GO whose P1 finding ("no in-text oracle for lost blocks") this slice resolves with the external oracle.
- `bridge/gtkb-tafe-bridge-index-preview-001.md` (WI-4507, VERIFIED) — the non-authoritative TAFE preview; this oracle complements it (preview = render; oracle = verify completeness).

## Owner Decisions / Input

Owner directive (S438, AskUserQuestion, this session): "Drive Slice B now" — issued after I presented the accurate multi-slice state (Slice A VERIFIED; Slice B + ingestion + generation + evidence + cutover remaining). That AUQ answer authorizes proceeding with the Slice B implementation. The prior owner AUQ `DELIB-20263195` authorized the WI-4508→4509→4510 cutover sequence and minted the governing PAUTH. No new owner decision is required to implement this read-only slice; the cutover itself (WI-4510) remains owner-AUQ-gated and is untouched here.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` + WI-4508 + the Slice A deferral fully specify the lost-block-oracle need. Because this slice is read-only and makes no flow-mapping decisions, the design constraint/ADR the `-004` flagged is NOT required for it — that ADR governs the deferred Slice C ingestion only. No new or revised requirement is needed.

## Design (Slice B)

**New module `groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py`** (does `bridge/` directory I/O; deliberately NOT placed in the purity-AST-enforced `tafe_index_sync.py`):

- `@dataclass(frozen=True) class ExpectedDocument` — `slug: str`, `files: tuple[str, ...]` (relative posix paths of `bridge/<slug>-NNN.md`), `latest_version: int`.
- `scan_expected_documents(project_root: Path) -> dict[str, ExpectedDocument]` — globs `bridge/*-[0-9]*.md`, groups by slug (filename minus the trailing `-NNN.md`), excludes `INDEX.md` and any non-`-NNN`-versioned file. The `bridge/` directory IS the external expected-document oracle.
- `@dataclass(frozen=True) class IndexCompletenessReport` — `present_slugs: tuple[str, ...]` (INDEX `Document:` names), `expected_slugs: tuple[str, ...]` (bridge/ slugs), `lost_blocks: tuple[str, ...]` (expected − present), `extra_blocks: tuple[str, ...]` (present − expected), and `.ok` (True iff `lost_blocks` empty).
- `index_completeness_report(index_text: str, project_root: Path) -> IndexCompletenessReport` — calls `tafe_index_sync.parse_bridge_index(index_text)` for the present set (reuses the VERIFIED Slice A parser; no re-implementation), `scan_expected_documents(project_root)` for the expected set, and diffs. Pure over its two inputs (the text + the scan result).

**CLI `gt flow index-completeness`** in `cli.py` (read-only): reads canonical `bridge/INDEX.md` (default `<project_root>/bridge/INDEX.md`, overridable via `--index-path`), runs `index_completeness_report`, prints a human summary or `--json`; exits non-zero when `lost_blocks` is non-empty (1 = lost blocks, 2 = refused canonical-write target, 3 = index not found). An optional `--out` writes the JSON report (never the canonical index; refuses any target resolving to `bridge/INDEX.md`, reusing Slice A's `_targets_canonical_bridge_index` guard). This is a NEW command; Slice A's VERIFIED `gt flow index-parity` is untouched.

No canonical write surface is introduced; no TAFE table is created or written; the multi-session INDEX-write contention surface is untouched.

## Spec-Derived Verification Plan

```text
python -m pytest groundtruth-kb/tests/test_tafe_index_completeness.py -q --tb=short
Expected: pass (the new oracle + CLI tests).

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_index_completeness.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_index_completeness.py
python -m ruff format --check (same files)
Expected: pass.
```

## Spec-to-Test Mapping

| Spec / behavior | Test (`tests/test_tafe_index_completeness.py`) | Oracle / Method |
|---|---|---|
| `SPEC-…-UMBRELLA` — expected-document scan completeness | `test_scan_finds_all_bridge_slugs`, `test_scan_excludes_index_and_nonversioned` | tmp `bridge/` fixture; assert slug set + that `INDEX.md`/non-`-NNN` files are excluded |
| Lost-block detection (Slice A's deferred class) | `test_report_detects_lost_block` | fixture: a slug with bridge files but no INDEX `Document:` entry → appears in `lost_blocks` |
| Extra-block (phantom INDEX entry) detection | `test_report_detects_extra_block` | fixture: an INDEX `Document:` with no bridge files → appears in `extra_blocks` |
| Parity → ok | `test_report_ok_when_index_matches_bridge_dir` | fixture where INDEX names == bridge/ slugs → `lost_blocks==()`, `.ok` True |
| `GOV-FILE-BRIDGE-AUTHORITY-001` — read-only contract | `test_cli_index_completeness_json`, `test_cli_refuses_canonical_write_target` | invoke `gt flow index-completeness --json`; assert read-only + `--out` guard refusal |
| Slice A parser reuse (no regression) | `test_uses_slice_a_parser` | assert `index_completeness_report` consumes `parse_bridge_index` output (present set matches Slice A document names) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + executed commands above | — |

## Risk / Rollback

Risk 1 — **parked-draft false positives.** Per `.claude/rules/file-bridge-protocol.md` § Parked-Draft Pattern, a bridge file MAY be committed without an INDEX entry (a deliberate work-in-progress). Such slugs appear in `lost_blocks`. Mitigation: this is documented as a benign subclass in the report + CLI summary; distinguishing parked drafts from genuine lost blocks requires the originating commit-message `parked` tag, which is deferred (a `--exclude-parked` allowlist is a Slice-C/cutover refinement). The diagnostic still correctly surfaces the candidate set for review — strictly more information than Slice A, never a canonical mutation.

Risk 2 — none to canonical state: the slice is read-only (reads INDEX + scans `bridge/`), adds no TAFE write, no schema, no concurrency surface.

Rollback: delete the new module + test and revert the additive `cli.py` command (one new subcommand); no on-disk state, schema, or INDEX change to undo.

## Bridge Filing (INDEX-Canonical)

Filed under `bridge/` as `bridge/gtkb-tafe-dual-write-slice-b-oracle-001.md`, with a `NEW` entry added to `bridge/INDEX.md` via the serialized `gt bridge index add-document` CLI (`scripts/bridge_index_writer.py` holds the lock + atomic temp-then-replace read-modify-merge). This is version 001; no prior version files are deleted or rewritten. `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`; agent-tool Write/Edit of INDEX is additionally blocked by the WI-4481 INDEX-write-guard. The oracle reads INDEX read-only and never mutates it.

## Recommended Commit Type

`feat:` — adds the lost-block/completeness oracle + a new read-only `gt flow index-completeness` CLI surface (net-new capability completing Slice A's deferred diagnostic). Matches the `feat` recommendation Codex applied to the Slice A VERIFIED.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
