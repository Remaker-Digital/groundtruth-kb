NEW

bridge_kind: implementation_proposal
Document: gtkb-tafe-dual-write-index-parity
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dfc088ac-2d2c-4b3e-8117-6e5ed57469e8
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4508
target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_index_sync.py"]

# Implementation Proposal — TAFE Dual-Write Foundation: Lossless INDEX Parser + Round-Trip Integrity Check (WI-4508, Slice A)

## Summary

WI-4508 ("Dual-write mode: TAFE authoritative + generated INDEX.md; validate
parity") is the Phase-6 step toward the owner-authorized TAFE bridge-INDEX
cutover (DELIB-20263195). Investigation of the existing surface (WI-4507
`tafe_index_preview.py`, the `typed_artifact_flow.py` runtime service, and the
canonical `bridge/INDEX.md` format) surfaced two load-bearing facts that shape
the design:

1. **No bridge → TAFE ingestion path exists.** WI-4507 only *renders* from TAFE
   state; nothing *populates* TAFE flow/stage records from canonical bridge
   state. True "dual-write" therefore requires a new ingestion + persistence
   layer.
2. **A format-fidelity gap.** WI-4507's renderer emits stage lines as
   `<status>: <stage_id> (role=…, claim=…)`; canonical `bridge/INDEX.md` emits
   `<STATUS>: bridge/<slug>-NNN.md`. The preview is a visual approximation, not
   a byte-faithful reproduction. For TAFE to *generate* the canonical INDEX at
   cutover, a **lossless** parse↔serialize round-trip is a prerequisite.

To make progress safely on the canonical bridge surface (which multiple
sessions write concurrently), this proposal **phases** WI-4508:

- **Slice A (this proposal):** a pure, read-only canonical-INDEX structured
  parser + lossless serializer + round-trip integrity check, exposed as a
  read-only `gt flow index-parity` CLI. Writes nothing canonical, persists
  nothing to TAFE, adds zero concurrency risk. It establishes the lossless
  round-trip that any TAFE-authoritative INDEX generation depends on, and
  doubles as a structural INDEX-corruption detector for the lost/duplicated
  document-block class (WI-4481).
- **Slice B (deferred follow-on; not in this proposal):** the bridge-document →
  TAFE-flow ingestion mapping + TAFE persistence (the literal "second write")
  + TAFE-vs-canonical parity. This carries genuine design decisions
  (flow_definition selection, subject_id derivation, status→stage semantics)
  that merit a focused ADR + their own review.
- **Cutover (WI-4510; PAUTH-forbidden until owner AUQ):** making TAFE
  authoritative and INDEX a generated artifact.

## Specification Links

- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — governing umbrella spec for
  TAFE; this slice implements the "renderable/round-trippable parallel view"
  prerequisite for the authoritative generated view.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — canonical `bridge/INDEX.md` remains the
  authoritative workflow state. Slice A reads the canonical index and writes
  nothing to it; the module exposes no canonical-INDEX write surface
  (mirrors the WI-4507 guard posture).
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing spec it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — verification plan below
  derives tests from each linked spec/acceptance criterion.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`; no application/adopter surface is touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — the work is delivered
  as durable, tracked, phased artifacts (Slice A / Slice B / cutover) rather
  than a single opaque change.
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — deferred (Slice B) and
  superseded (WI-4495/4496) lifecycle states are handled explicitly, not
  silently dropped.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision, PAUTH,
  spec, and work-item artifacts are linked and traceable.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA and
WI-4508 govern this work; no new or revised requirement is needed for Slice A.
The Slice-B ingestion mapping will require a design constraint/ADR before
implementation, but that is out of scope for this proposal and does not block
Slice A.

## Prior Deliberations

- **DELIB-20263195** — owner AUQ (2026-06-13) authorizing the full TAFE cutover
  sequence WI-4508 → WI-4509 → WI-4510; basis for
  PAUTH-…-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510.
- **DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612**,
  **DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612** — TAFE project formation
  (Step 5); origin of WI-4508/4509/4510.
- **DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612** — WI-4495/4496
  supersession (the superseded rows that WI-4509 still references; rewiring is
  tracked in DELIB-20263195's scope, handled when WI-4509 starts).
- **bridge/gtkb-tafe-bridge-index-preview-002 (GO)** — WI-4507 compatibility
  view; the renderer this slice complements. Slice A deliberately operates on
  the *canonical* INDEX text (lossless), distinct from WI-4507's lossy preview
  shape.

_No prior deliberation proposes a lossless INDEX parser; this is novel building
work for the cutover._

## Design (Slice A)

New module `groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py`:

- `parse_bridge_index(index_text: str) -> ParsedBridgeIndex` — pure parser.
  Tokenizes canonical `bridge/INDEX.md` into an ordered list of document blocks,
  each `Document: <name>` followed by its ordered `<STATUS>: <path>` version
  lines (latest-first), preserving header comments and the exact inter-block
  layout needed for lossless re-emission. Recognizes the canonical status
  vocabulary (NEW, REVISED, GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN,
  plus historically-present tokens like ACCEPTED/BLOCKED, preserved verbatim).
- `serialize_bridge_index(parsed: ParsedBridgeIndex) -> str` — inverse of the
  parser; re-emits byte-identical INDEX text for any well-formed input.
- `roundtrip_report(index_text: str) -> RoundTripReport` — parses then
  serializes and reports byte-equality plus, on mismatch, the first differing
  region and per-document structural deltas (lost block, duplicated block,
  reordered versions) — the corruption class from WI-4481.
- Purity: no file I/O, no subprocess, no MemBase mutation, no reference to the
  canonical index path. AST-enforced purity test (same pattern as WI-4507).

CLI `gt flow index-parity` (read-only) in `cli.py`:

- Reads the canonical `bridge/INDEX.md` (read-only), runs `roundtrip_report`,
  prints a human summary or `--json`. Exits non-zero on round-trip mismatch
  (structural-integrity signal). No write surface; refuses any output target
  resolving to the canonical index (reuses WI-4507's guard intent).

## Verification Plan (Specification-Derived)

| Spec / Acceptance criterion | Test (in `tests/test_tafe_index_sync.py`) | Method |
|---|---|---|
| SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA — lossless round-trip foundation | `test_roundtrip_byte_identical_on_live_index`, `test_roundtrip_multiversion_blocks`, `test_status_vocabulary_preserved` | parse→serialize == input for representative + live-INDEX fixtures |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no canonical write surface | `test_module_has_no_write_surface`, `test_ast_purity_no_io_no_subprocess_no_mutation` | AST scan asserts no `open`/`write`/`subprocess`/MemBase-mutation; no canonical-index path constant |
| WI-4481 corruption-class detection | `test_roundtrip_detects_lost_block`, `test_detects_duplicated_block` | corrupted fixtures → `roundtrip_report` flags the delta |
| CLI read-only contract | `test_cli_index_parity_json`, `test_cli_refuses_canonical_write_target` | invoke `gt flow index-parity --json`; assert read-only + guard |

Pre-file gates (run before report): `ruff check` + `ruff format --check` on
changed files; `python -m pytest groundtruth-kb/tests/test_tafe_index_sync.py -q`.

## Risk / Rollback

- **Risk:** low. Slice A is additive and read-only; it cannot alter canonical
  bridge state. Worst case is a false integrity signal, surfaced only via an
  opt-in CLI.
- **Concurrency:** none introduced — no writer-path change; the multi-session
  INDEX-write contention surface is untouched.
- **Rollback:** delete the new module + CLI command + test file; no migration,
  no state, no canonical artifact changed.

## Owner Decisions / Input

- **DELIB-20263195** (owner AUQ, 2026-06-13): owner selected "Authorize full
  cutover 4508→4510", authorizing this WI-4508 work and the bounded PAUTH
  `PAUTH-…-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510` (active; allows
  `dual_write`/`authoritative_generated_view`/`source`/`test_addition`/`config`;
  forbids the irreversible `cutover` op, preserving WI-4510's closing owner-AUQ
  gate).
- AUQ id `AUQ-2026-06-13-TAFE-CUTOVER-FULL`, answer "Authorize full cutover
  4508 to 4510".
- No further owner decision is required for Slice A. The Slice-B ingestion
  mapping will return for design review (ADR) before implementation.

## Recommended Commit Type

`feat:` — net-new module (`tafe_index_sync.py`) + new CLI command + tests
(parser/serializer capability surface).
