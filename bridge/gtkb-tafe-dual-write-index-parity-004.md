REVISED

bridge_kind: implementation_proposal
Document: gtkb-tafe-dual-write-index-parity
Version: 004
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

# Implementation Proposal (REVISED) — TAFE Dual-Write Foundation: Lossless INDEX Parser + Text-Observable Integrity Diagnostics (WI-4508, Slice A)

## Revision Scope

This `-004` REVISED supersedes `-001` in response to the Loyal Opposition NO-GO
at `bridge/gtkb-tafe-dual-write-index-parity-002.md` / `-003.md` (single P1
finding). The NO-GO is **accepted as correct**: a pure `roundtrip_report(index_text)`
that receives only the current INDEX text cannot detect a document block that is
*already absent* from that text — lost-block detection requires an external
oracle (expected-document set, prior snapshot, or bridge-directory inventory),
which a no-I/O module has no way to obtain.

This revision adopts the reviewer's **Option A** (the smaller, lower-risk path):

1. **Narrowed the integrity claim** to only what a pure, single-input parser can
   actually prove from `index_text` alone: parse/serialize **byte-fidelity**,
   **malformed-line** syntax errors, **duplicate-document** names, and
   **version-order anomalies** within a document block.
2. **Removed the lost-block (absent-from-text) detection claim** from Slice A
   and explicitly **deferred it to Slice B**, where an external expected-document
   oracle is available.
3. **Fixed the verification plan** so every named test has a real oracle:
   removed `test_roundtrip_detects_lost_block`; kept `test_detects_duplicated_block`;
   added `test_detects_version_order_anomaly`.

No other scope changed. The canonical INDEX read-only boundary, `target_paths`,
PAUTH, and the phased Slice-A/Slice-B/cutover structure are unchanged.

## Summary

WI-4508 ("Dual-write mode: TAFE authoritative + generated INDEX.md; validate
parity") is the Phase-6 step toward the owner-authorized TAFE bridge-INDEX
cutover (DELIB-20263195). Two facts from the existing surface (WI-4507
`tafe_index_preview.py` renderer; `typed_artifact_flow.py` runtime service; the
canonical `bridge/INDEX.md` format) shape the design: (a) **no bridge → TAFE
ingestion path exists**, so true dual-write requires a new ingestion/persistence
layer; (b) WI-4507's preview shape (`<status>: <stage_id> (role=…, claim=…)`) is
**not byte-faithful** to canonical INDEX lines (`<STATUS>: bridge/<slug>-NNN.md`),
so a **lossless** parse↔serialize round-trip is a prerequisite for any
TAFE-generated authoritative INDEX.

This proposal phases WI-4508 to make progress safely on the canonical bridge
surface (which multiple sessions write concurrently):

- **Slice A (this proposal):** a pure, read-only canonical-INDEX structured
  parser + lossless serializer + **text-observable** integrity diagnostics,
  exposed as a read-only `gt flow index-parity` CLI. Writes nothing canonical,
  persists nothing to TAFE, adds zero concurrency risk. It establishes the
  lossless round-trip any TAFE-authoritative INDEX generation depends on, and
  surfaces the *text-observable* half of the WI-4481 corruption classes
  (duplicate document blocks, malformed lines, version-order anomalies, and
  parser round-trip loss).
- **Slice B (deferred follow-on; NOT in this proposal):** the bridge-document →
  TAFE-flow ingestion mapping + TAFE persistence (the literal "second write")
  + TAFE-vs-canonical parity, **plus lost-block (absent-from-text) detection**
  using an external expected-document oracle (expected-document set, prior
  snapshot, or bridge-directory inventory). This carries genuine design
  decisions (flow_definition selection, subject_id derivation, status→stage
  semantics, oracle source) that merit a focused ADR + their own review.
- **Cutover (WI-4510; PAUTH-forbidden until owner AUQ):** making TAFE
  authoritative and INDEX a generated artifact.

## Specification Links

- **SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA** — governing umbrella spec for
  TAFE; this slice implements the lossless "round-trippable parallel view"
  prerequisite for the authoritative generated view.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — canonical `bridge/INDEX.md` remains the
  authoritative workflow state. Slice A reads the canonical index and writes
  nothing to it; the module exposes no canonical-INDEX write surface.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** — this proposal
  cites every governing spec it touches.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — verification plan below
  derives tests from each linked spec/acceptance criterion, and (per the NO-GO)
  every named test now has a real oracle.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — all `target_paths` are in-root
  under `E:\GT-KB`; no application/adopter surface is touched.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory) — the work is delivered
  as durable, tracked, phased artifacts (Slice A / Slice B / cutover).
- **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — deferred (Slice B) and
  superseded (WI-4495/4496) lifecycle states are handled explicitly.
- **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory) — owner decision, PAUTH,
  spec, and work-item artifacts are linked and traceable.

## Requirement Sufficiency

Existing requirements sufficient. SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA and
WI-4508 govern this work; no new or revised requirement is needed for Slice A.
The Slice-B ingestion mapping + lost-block oracle will require a design
constraint/ADR before implementation, but that is out of scope here and does
not block Slice A.

## Prior Deliberations

- **DELIB-20263195** — owner AUQ (2026-06-13) authorizing the full TAFE cutover
  sequence WI-4508 → WI-4509 → WI-4510; basis for
  PAUTH-…-TAFE-PHASE-6-7-CUTOVER-WI-4508-4509-4510.
- **bridge/gtkb-tafe-dual-write-index-parity-002.md / -003.md** — Loyal
  Opposition NO-GO (Codex, harness A) whose P1 finding this revision adopts
  (Option A).
- **DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612**,
  **DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612** — TAFE project formation.
- **DELIB-TAFE-BACKLOG-RECONCILIATION-PAUTH-20260612** — WI-4495/4496
  supersession context.
- **bridge/gtkb-tafe-bridge-index-preview-002.md** — GO verdict for the WI-4507
  compatibility view this slice complements.

_Codex's deliberation searches for "WI-4508 TAFE dual write index parity" and
"lost/duplicated document block bridge INDEX WI-4481" returned no additional
exact matches (carried forward from `-002`/`-003`); no prior deliberation
proposes a lossless INDEX parser._

## Design (Slice A)

New module `groundtruth-kb/src/groundtruth_kb/tafe_index_sync.py`:

- `parse_bridge_index(index_text: str) -> ParsedBridgeIndex` — pure parser.
  Tokenizes canonical `bridge/INDEX.md` into an ordered list of document blocks
  (each `Document: <name>` plus its ordered `<STATUS>: <path>` version lines,
  latest-first), preserving leading/header content and exact inter-block layout
  for lossless re-emission. Recognizes the canonical status vocabulary (NEW,
  REVISED, GO, NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN, plus
  historically-present tokens such as ACCEPTED/BLOCKED, preserved verbatim).
- `serialize_bridge_index(parsed: ParsedBridgeIndex) -> str` — inverse of the
  parser; re-emits byte-identical INDEX text for any well-formed input.
- `roundtrip_report(index_text: str) -> RoundTripReport` — parses then
  serializes and reports: (1) **byte-equality** of round-trip;
  (2) **malformed lines** (lines inside a document block that match neither a
  `Document:` nor a `<STATUS>: <path>` shape); (3) **duplicate-document** names
  (the same `Document: <name>` block appearing more than once — observable
  directly in the text); (4) **version-order anomalies** (a document block whose
  `<STATUS>: <path>` version lines are not in monotonic latest-first `-NNN`
  order). It does **not** claim to detect blocks absent from the text (deferred
  to Slice B with an oracle).
- Purity: no file I/O, no subprocess, no MemBase mutation, no reference to the
  canonical index path. AST-enforced purity test (same pattern as WI-4507).

CLI `gt flow index-parity` (read-only) in `cli.py`:

- Reads the canonical `bridge/INDEX.md` (read-only), runs `roundtrip_report`,
  prints a human summary or `--json`. Exits non-zero on any reported anomaly
  (round-trip mismatch / malformed line / duplicate document / version-order
  anomaly) as a structural-integrity signal. No write surface; refuses any
  output target resolving to the canonical index (reuses WI-4507's guard intent).

## Verification Plan (Specification-Derived)

| Spec / Acceptance criterion | Test (in `tests/test_tafe_index_sync.py`) | Oracle / Method |
|---|---|---|
| SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA — lossless round-trip | `test_roundtrip_byte_identical_on_live_index`, `test_roundtrip_multiversion_blocks`, `test_status_vocabulary_preserved` | Oracle = the input text itself: `serialize(parse(t)) == t` for representative + live-INDEX fixtures |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no canonical write surface | `test_module_has_no_write_surface`, `test_ast_purity_no_io_no_subprocess_no_mutation` | AST scan asserts no `open`/`write`/`subprocess`/MemBase-mutation; no canonical-index path constant |
| WI-4481 text-observable corruption: duplicate block | `test_detects_duplicated_block` | Oracle = a fixture with the same `Document:` block twice; `roundtrip_report` flags it |
| WI-4481 text-observable corruption: version-order anomaly | `test_detects_version_order_anomaly` | Oracle = a fixture whose version lines are out of `-NNN` order; report flags it |
| Malformed-line detection | `test_detects_malformed_line` | Oracle = a fixture with a non-conforming line inside a block |
| CLI read-only contract | `test_cli_index_parity_json`, `test_cli_refuses_canonical_write_target` | invoke `gt flow index-parity --json`; assert read-only + guard |

Explicitly **out of scope for Slice A** (no test asserts it): detection of a
document block *absent* from the current text (no in-text oracle exists) —
deferred to Slice B.

Pre-file gates (run before the implementation report): `ruff check` +
`ruff format --check` on changed files; `python -m pytest
groundtruth-kb/tests/test_tafe_index_sync.py -q`.

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
  mapping + lost-block oracle will return for design review (ADR) before
  implementation.

## Recommended Commit Type

`feat:` — net-new module (`tafe_index_sync.py`) + new CLI command + tests
(parser/serializer + text-observable integrity diagnostics).
