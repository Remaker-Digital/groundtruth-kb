NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code proposal-author worker dispatched by the Harness Test Corrections program leader; this filing is a Prime Builder proposal-authoring act (envelope pb); the parent interactive session's resolver fallback reports loyal-opposition; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5811-cross-harness-append-only-enforcement
Version: 001
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5811

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/chain_integrity.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/bridge_applicability_preflight.py", ".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "config/hooks/gtkb-bridge-compliance-gate.py", "platform_tests/scripts/test_bridge_chain_integrity.py", "platform_tests/hooks/test_bridge_compliance_gate_source_content_hash.py"]
implementation_scope: detection_module_doctor_check_state_report_surfacing_and_verdict_anchor_hardening
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5811 Implementation Proposal — Cross-Harness Append-Only Enforcement: Bridge Chain-Integrity Verification

## Summary

Deliver write-path-independent protection for the bridge audit trail: deterministically detect in-place modification of existing `bridge/<slug>-NNN.md` chain files and surface the violation on canonical read surfaces (`gt bridge state-report`, `gt project doctor`) before a thread advances, using verdict-recorded content hashes as the integrity anchor. Today, bridge append-only and compliance enforcement exists only as Claude-side `Write`/`Edit` PreToolUse hooks (`.claude/hooks/bridge-compliance-gate.py`); any non-Claude harness that writes through a cmd shell or its own tool surface bypasses every gate. The first live exploit is on record (WI-5811 / WI-5808 evaluation, 2026-07-30): a Goose-harness session rewrote the already-reviewed `bridge/gtkb-wi5808-harness-probe-glm52-r1-001.md` in place after its independent NO-GO verdict, and Goose runs also filed token-less bridge files — all unimpeded.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5811-cross-harness-append-only-enforcement-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical audit trail per GOV-FILE-BRIDGE-AUTHORITY-001. The implementation itself is detection-first and read-only over `bridge/`: it never deletes, rewrites, or repairs any existing chain file, including the tampered evaluation fixture.

## Problem Statement And Live Evidence (fresh reads, 2026-07-30)

All claims below were re-derived this session from the live worktree and code of record; hashes were recomputed with the project interpreter.

1. **Claude-side-only enforcement.** The bridge compliance gate, the append-only protections, and the verdict-freshness check live in `.claude/hooks/bridge-compliance-gate.py` (mirrored at `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` and `config/hooks/gtkb-bridge-compliance-gate.py`) and fire only on Claude `Write`/`Edit` PreToolUse events. DCL-CROSS-HARNESS-ENFORCEMENT-001 already records other write paths as a gap; WI-5811 is the first live violation of exactly that gap.
2. **The tamper.** The Loyal Opposition NO-GO verdict `bridge/gtkb-wi5808-harness-probe-glm52-r1-002.md` reviewed `bridge/gtkb-wi5808-harness-probe-glm52-r1-001.md` (`Responds to:` + preflight `content_file`/`operative_file` all name `-001`). After that verdict, a Goose cmd-shell write rewrote `-001` in place. The current `-001` hashes `sha256:c0313d46536d36bc1c76407462aa6aedb16bee2bd85bcae9fca2e0814dbf3ca4` (recomputed this session over both raw bytes and LF-normalized text; identical because the file has LF endings), with mtime after the verdict. The original content is unrecoverable: the file was untracked and HEAD is frozen.
3. **Precision on the existing anchors** (this grounding shapes the design and corrects a loose phrase in the WI description):
   - `candidate_evidence_hash` is a **self-hash of the verdict file**, not a hash of the reviewed candidate. It is computed by `_candidate_evidence_hash()` in `.claude/hooks/bridge-compliance-gate.py`: root-relative path + `"\n"` + LF-normalized content with the verdict's own `candidate_evidence_hash` line sentinel-substituted (`CANDIDATE_EVIDENCE_HASH_LINE_RE` / `<CANDIDATE_EVIDENCE_HASH>`). Recomputing this algorithm over the current `-002` reproduces the recorded `sha256:dd8ed347feeaaad6830ca1ebfe9d232d509566e01a0418d8769370603cc114ae` exactly — the verdict file itself is intact.
   - The anchor over the **reviewed candidate content** is the verdict-recorded `packet_hash` (`sha256:c9a66345d58a120d13cc0d942073ce3c2375b8cf033faf191fd2803e2081b89f` in `-002`), produced by `build_packet()` in `scripts/bridge_applicability_preflight.py`, whose `_packet_hash_material()` includes `source_content_hash` — `_text_sha256()` over the LF-normalized candidate content (`build_packet` computes it; `format_markdown()` currently does **not** render it as its own line). Post-hoc comparison through `packet_hash` alone is therefore coarse: rules content, MemBase applicability state, and project-authorization operation-time evidence are also part of the hash material and can drift legitimately.
4. **Token-less filings.** Goose runs filed bridge files whose first non-blank line is not a canonical status token. `status_from_bridge_file()` / `_line_status_token()` in `groundtruth_kb/bridge/versioned_files.py` return `None` for such files, so they are invisible to status-driven routing instead of being surfaced as violations.
5. **Detection precedent.** The WI-4871 guard `_check_untracked_terminal_verified_verdicts()` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (defined near line 2454, registered near line 7239) demonstrates the required shape: cheap `git ls-files --others --exclude-standard bridge` enumeration, first-non-blank-line token classification, fail-soft WARN. It covers only untracked terminal VERIFIED verdicts; it does not cover in-place modification of reviewed chain files, untracked reviewed candidates generally, or token-less filings.

## Design (detection-first, write-path-independent)

### D1. Core module: `groundtruth_kb/bridge/chain_integrity.py` (new)

A read-only verification module with no timers, no polling, and no new automation substrate — it is invoked from existing surfaces (doctor, state-report, tests) only.

- **Shared hash primitives** (single implementation, importable by hooks, doctor, and the sibling protected-surfaces carrier):
  - `normalized_content_sha256(text)` — LF-normalized sha256, byte-compatible with `_text_sha256()` in `scripts/bridge_applicability_preflight.py`.
  - `verdict_self_evidence_hash(rel_path, content)` — the exact `_candidate_evidence_hash()` algorithm (sentinel substitution included), so the hook and the detector can never disagree.
- **`parse_verdict_anchors(path)`** — extracts `Responds to:`, preflight `content_file`/`operative_file`, `packet_hash`, `candidate_evidence_hash`, and (when present) `source_content_hash` from a verdict file (GO / NO-GO / VERIFIED first-line token).
- **`verify_chain(slug, project_root) -> ChainIntegrityReport`** — enumerates `bridge/<slug>-NNN.md` for one thread (targeted `<slug>-*.md` glob, never a wholesale `bridge/` scan) and classifies each finding:
  - `tampered_after_verdict` — a verdict's recorded `source_content_hash` does not match the current `normalized_content_sha256` of the responded-to chain file (surgical DETECT; available for all verdicts filed after D2 lands).
  - `coarse_anchor_mismatch` — for historical verdicts without a recorded `source_content_hash`: rebuilding `build_packet()` over the current responded-to content yields a `packet_hash` that mismatches the verdict-recorded one (coarse DETECT; always reported together with git evidence because non-content packet material can drift).
  - `verdict_self_hash_mismatch` — recomputed `verdict_self_evidence_hash` differs from the verdict's recorded `candidate_evidence_hash` (the verdict file itself was modified after write).
  - `git_modified_tracked` — `git --no-optional-locks status --porcelain -- bridge/<slug>-*.md` shows a tracked chain file modified in the worktree (append-only chains must never show worktree modification of committed versions).
  - `untracked_reviewed_candidate` — an untracked chain file that a later verdict responds to (the exact glm52-r1 hole; generalizes the WI-4871 pattern beyond terminal VERIFIED).
  - `token_less` — first non-blank line is not a canonical status token per the `versioned_files` token set (SURFACE class).
  - `clean`.
- **`verify_worktree(project_root)`** — the cheap-gated sweep: enumerate only files reported by `git --no-optional-locks status --porcelain -- bridge` (modified + untracked — a small set), group them by slug, and run `verify_chain` only for affected slugs. This honors the poller-retirement lesson (cheap deterministic gate before the bounded action) and never enumerates the ~14,000-file `bridge/` directory wholesale. No timer or interval values exist anywhere in the module (DELIB-202667722): execution is strictly caller-driven.

### D2. Forward anchor: render `source_content_hash` in the preflight section

`format_markdown()` in `scripts/bridge_applicability_preflight.py` gains one line — `- source_content_hash: ...` — emitting the value `build_packet()` already computes. Every verdict filed after this change carries a surgical, drift-free integrity anchor over the exact reviewed candidate bytes, eliminating the coarse-rebuild caveat for all future chains.

### D3. Gate hardening: validate the embedded anchor (backward compatible)

`_verdict_preflight_freshness_deny_reason()` in `.claude/hooks/bridge-compliance-gate.py` (and byte-mirrors `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `config/hooks/gtkb-bridge-compliance-gate.py`) additionally validates `source_content_hash` when the written verdict embeds the line: it must equal the rebuilt packet's `source_content_hash` for the `Responds to:` artifact. An absent line remains accepted so historical verdicts and in-flight authoring are not broken; the D2 render makes the line present in all tool-generated sections going forward. This is validate-when-present hardening on the Claude write path only; cross-harness protection comes from D1/D4/D5, which are write-path-independent.

### D4. Doctor check: `_check_bridge_chain_integrity`

New check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, defined beside and registered with `_check_untracked_terminal_verified_verdicts()` (WI-4871 precedent). It calls `chain_integrity.verify_worktree()` and reports WARN (fail-soft, never FAIL, matching the WI-4871 severity decision so a transient window cannot block doctor) with per-file classifications. On the current live tree it must flag the glm52-r1 chain.

### D5. State-report surfacing: violations visible before a thread advances

`_bridge_section()` in `groundtruth_kb/bridge/state_report.py` gains a `chain_integrity` block (affected slugs, per-file classifications) computed from `verify_worktree()`, and `render_markdown()` renders integrity-flagged threads prominently. `gt bridge state-report` is the canonical bridge-queue read route, so every session and reviewer sees a DETECT before acting on the thread. Reviewers already run the applicability preflight before verdicts; a flagged thread therefore cannot silently advance through an unaware review.

### Explicitly out of scope

- No dispatcher or TAFE mutation (forbidden operation under the PAUTH); no changes to dispatch eligibility or routing.
- No OS ACL changes and no filesystem write-blocking; prevention lanes are the sibling efforts — WI-5797 governed-writer publication receipts and AT-01 commit-first tracking authority (DELIB-202667533). This WI is the write-path-independent detection net that makes any bypass of those lanes visible.
- No deletion, rewrite, or "repair" of any existing chain file. The tampered glm52-r1 chain is a live evaluation-evidence fixture: regression tests reference its recorded hashes read-only and must not modify it.
- No new poller, daemon, scheduled task, or hard-coded timer values (DELIB-202667722).

### Rejected alternatives

- **Windows read-only attribute (`attrib +R`) on finalized chain files** — cheap but interferes with git tooling and adds a mutation of historical files for marginal value over commit-first tracking; rejected for this slice.
- **Wholesale periodic re-hash of all `bridge/*.md`** — violates the cheap-gate lesson from the poller retirement and the no-timer directive; rejected.
- **Blocking at reconcile by refusing to compute `latest_status` for flagged chains** — risks deadlocking legitimate recovery work on a flagged thread; surfacing-with-evidence chosen instead, leaving disposition to governed roles.

## Detection Matrix (spec-derived acceptance behavior)

| # | Case | Input state | Required outcome |
|---|---|---|---|
| 1 | Tampered after verdict | Chain file content changed after a later verdict recorded its anchors (glm52-r1 pattern) | **DETECT** (`tampered_after_verdict` when a `source_content_hash` anchor exists; `coarse_anchor_mismatch` + git evidence for historical verdicts) |
| 2 | Appended new version | A new next-numbered `bridge/<slug>-NNN.md` file appended; prior versions byte-identical | **PASS** (append-only evolution is the sanctioned path) |
| 3 | Untouched chain | No worktree delta on the chain | **PASS** (and never enumerated by the cheap gate) |
| 4 | Token-less latest | Latest chain file's first non-blank line is not a canonical status token | **SURFACE** (`token_less` WARN classification, never silent invisibility) |

## Specification Links

Required (blocking): DCL-CROSS-HARNESS-ENFORCEMENT-001, GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-ARTIFACT-APPROVAL-001, ADR-ISOLATION-APPLICATION-PLACEMENT-001.
Advisory: GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, SPEC-1662, GOV-STANDING-BACKLOG-001.
Deliberations: DELIB-202667730, DELIB-202667731, DELIB-202667533, DELIB-202667722.

### Required (blocking)

| Spec ID | Relevance |
|---|---|
| DCL-CROSS-HARNESS-ENFORCEMENT-001 | The governing gap record: bridge enforcement covers Claude Write/Edit only; other write paths are tracked as gap or blocked. This proposal closes the detection half of the gap for bridge chains. WI-5811's `source_spec_id` names this DCL. |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Append-only numbered bridge file chain authority; the versioned bridge files under `bridge/` are the canonical audit trail this work protects. Chain files are never deleted or rewritten by this implementation. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal carries concrete specification links and derives its tests from them. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Governs downstream verification: the spec-to-test mapping below is the derivation record the LO verifier will execute against. |
| GOV-ARTIFACT-APPROVAL-001 | Bridge artifacts and any formal-artifact surfaces remain under the approval gate; this work mutates no MemBase formal artifact. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths are in-root under `E:\GT-KB` (`groundtruth-kb/src/`, `scripts/`, `.claude/hooks/`, `config/hooks/`, `platform_tests/`); no out-of-root dependency is created. |

### Advisory

| Spec ID | Relevance |
|---|---|
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Integrity findings become durable, classified evidence on canonical read surfaces rather than transient session observations. |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Traceability: verdict-recorded anchors tie review artifacts to reviewed content across the chain lifecycle. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | DETECT/SURFACE classifications are lifecycle triggers for governed disposition of flagged threads. |
| GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 | Chain verification is a deterministic service (pure functions over file bytes + git porcelain), not per-session AI judgment. |
| SPEC-1662 | Assertion quality: the detection matrix tests assert behavioral outcomes (classifications), not structural presence. |
| GOV-STANDING-BACKLOG-001 | WI-5811 is the MemBase backlog authority for this work; no parallel work authority is created. |

## Prior Deliberations

- **DELIB-202667730** — WI-5808 Harness Test evaluation synthesis: consolidated findings from the 2026-07-30 evaluation runs, including the Goose in-place rewrite and token-less filings that motivate this proposal.
- **DELIB-202667731** — Owner decision (AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT): list-free whole-project implementation authorization for PROJECT-GTKB-HARNESS-TEST-CORRECTIONS, recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730.
- **DELIB-202667533** — AT-01 commit-first authority: bridge artifacts tracked at filing; the complementary prevention lane this detection net backstops (an untracked reviewed candidate is itself a flagged class here).
- **DELIB-202667722** — Timer and throttle governance: no hard-coded timer values; this design contains no timers at all — execution is caller-driven from existing surfaces.

## Owner Decisions / Input

1. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT**: the owner issued the taxonomy-clean, list-free whole-project grant covering PROJECT-GTKB-HARNESS-TEST-CORRECTIONS member work items, including WI-5811. That grant authorizes this proposal-review-implementation cycle; it does not waive independent Loyal Opposition GO, the fresh work-intent claim, the implementation-start packet, exact target-path enforcement, the implementation report, or independent VERIFIED with governed atomic finalization.
2. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5811's description (integrity anchors, write-path independence, detect-before-advance), DCL-CROSS-HARNESS-ENFORCEMENT-001 (the recorded enforcement gap), GOV-FILE-BRIDGE-AUTHORITY-001 (append-only chain authority), DELIB-202667730 (evaluation synthesis), and DELIB-202667722 (timer discipline) fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-to-Test Mapping

All tests land in `platform_tests/scripts/test_bridge_chain_integrity.py` except the hook tests, which land in `platform_tests/hooks/test_bridge_compliance_gate_source_content_hash.py`. Synthetic-fixture tests build temporary chains under `tmp_path`; live-fixture tests read the glm52-r1 chain strictly read-only and assert its bytes are unchanged after the run.

| Requirement source | Test | Detection-matrix case |
|---|---|---|
| WI-5811 / DCL-CROSS-HARNESS-ENFORCEMENT-001 — detect in-place modification | `test_tampered_after_verdict_detected` (synthetic chain: verdict with `source_content_hash` anchor, candidate then mutated → `tampered_after_verdict`) | 1 DETECT |
| WI-5811 — historical chains without surgical anchor | `test_coarse_anchor_mismatch_detected` (synthetic verdict with `packet_hash` only → `coarse_anchor_mismatch` + git evidence) | 1 DETECT |
| WI-5811 — live exploit regression | `test_live_glm52_r1_chain_detects_tamper` (read-only over `bridge/gtkb-wi5808-harness-probe-glm52-r1-001.md`/`-002.md`: recomputed `-002` self-hash equals recorded `sha256:dd8ed347...` — verdict intact; current `-001` no longer matches the verdict-time anchor → DETECT class; fixture bytes asserted unchanged after the run) | 1 DETECT |
| GOV-FILE-BRIDGE-AUTHORITY-001 — append-only evolution sanctioned | `test_appended_new_version_passes` (append `-003` to a synthetic chain; prior files untouched → `clean`) | 2 PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 — no false positives | `test_untouched_chain_passes` (clean synthetic chain → `clean`; also asserts the cheap gate never enumerates unaffected chains) | 3 PASS |
| WI-5811 — token-less filings surfaced | `test_token_less_latest_surfaced` (synthetic latest file with non-canonical first line → `token_less`) | 4 SURFACE |
| WI-5811 — verdict self-integrity | `test_verdict_self_hash_mismatch_detected` (mutate a synthetic verdict after write → `verdict_self_hash_mismatch`) | 1 DETECT (verdict variant) |
| DELIB-202667533 / WI-4871 precedent — untracked reviewed candidate | `test_untracked_reviewed_candidate_flagged` (synthetic untracked candidate with a later verdict responding to it → `untracked_reviewed_candidate`) | 1 DETECT (durability variant) |
| D2 render contract | `test_source_content_hash_rendered` (`format_markdown()` output contains a valid `- source_content_hash:` line equal to `_text_sha256` of the content file) | forward anchor |
| D3 gate contract | `test_gate_rejects_wrong_source_content_hash`, `test_gate_accepts_absent_source_content_hash` (hook-level, patterned on `platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py`) | forward anchor |
| D4 doctor contract / WI-4871 precedent | `test_doctor_chain_integrity_warns_on_violation`, `test_doctor_chain_integrity_passes_clean` (WARN fail-soft severity asserted) | 1-4 surfacing |
| D5 state-report contract | `test_state_report_includes_chain_integrity_block` | 1-4 surfacing |
| DELIB-202667722 — timer discipline | `test_no_timer_values_in_module` (module source contains no sleep/interval/timeout literals; execution strictly caller-driven) | discipline |
| SPEC-1662 — hash primitive parity | `test_hash_primitives_match_hook_and_preflight` (byte-parity of `normalized_content_sha256` with `_text_sha256` and of `verdict_self_evidence_hash` with `_candidate_evidence_hash` on shared vectors, including the live `-002` value `sha256:dd8ed347...`) | anchor correctness |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` pass clean on every changed Python file (both are separate gates).
2. `python -m pytest platform_tests/scripts/test_bridge_chain_integrity.py platform_tests/hooks/test_bridge_compliance_gate_source_content_hash.py -q --tb=short` passes green.
3. On the current live tree, `verify_worktree()` (and therefore the doctor check) flags the `gtkb-wi5808-harness-probe-glm52-r1` chain as a DETECT-class finding, and flags no chain that git porcelain reports as unaffected.
4. `gt bridge state-report` output includes the `chain_integrity` block with the flagged chain visible.
5. The glm52-r1 fixture files are byte-identical before and after every test and verification run.
6. Existing suites that exercise the touched surfaces (doctor, state-report, bridge-compliance-gate hook tests) remain green.
7. No changed file contains a hard-coded timer, interval, or sleep value.

## Risk And Rollback

- **Read-only by construction.** The detector never writes under `bridge/`; the only behavioral writes are one rendered line in future preflight sections (D2) and one additional validate-when-present branch in the gate (D3). The rendered line does not perturb `packet_hash` (hash material is the packet dict, not the rendered markdown), and absent-line acceptance keeps historical verdicts and in-flight authoring valid.
- **Coarse-anchor false positives.** For pre-D2 verdicts, `packet_hash` rebuild mismatches can reflect rules/MemBase/PAUTH-context drift rather than content tampering. Mitigation: the class is explicitly labeled `coarse_anchor_mismatch`, always paired with git worktree evidence, and reported at WARN severity for governed disposition rather than automated action.
- **Concurrent program filings.** Sibling corrections workers are filing bridge threads concurrently; this proposal adds no contention on their write path (detection reads git porcelain snapshots and tolerates transient windows via fail-soft WARN, mirroring the WI-4871 decision).
- **Rollback** is the exact revert of the nine target files. No MemBase mutation, no dispatcher/TAFE state, no chain files, and no fixture bytes are touched, so rollback has no data migration.

## Coordination Note (not scope)

The protected-surfaces-beyond-bridge sibling carrier in PROJECT-GTKB-HARNESS-TEST-CORRECTIONS extends write-path-independent protection to non-bridge governed surfaces. This proposal deliberately scopes to bridge chains; the shared hash primitives in `chain_integrity.py` are designed importable so the sibling can reuse them without re-derivation. WI-5797 (governed-writer publication receipts) and AT-01 commit-first (DELIB-202667533) remain the prevention lanes; this WI is the detection net that makes any bypass of them visible.

## Cross-Harness Disposition

Target paths touch one harness-behavioral surface (`.claude/hooks/bridge-compliance-gate.py`). Per-harness disposition (DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001; ADR-CROSS-HARNESS-PARITY-001 Q8):

- **Claude (harness B):** behavioral parity maintained. The D3 validate-when-present branch is added to the canonical live hook `.claude/hooks/bridge-compliance-gate.py` and propagated byte-for-byte to both mirrors (`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`, `config/hooks/gtkb-bridge-compliance-gate.py`); the implementation report will include mirror-identity evidence (hash comparison across the three copies).
- **Codex (harness A):** behavioral parity by construction. The Codex filing path (`propose_bridge_codex_non_bypass` in `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py`) runs `bridge-compliance-gate.py --audit-only` against the same canonical hook file, so the D3 branch applies identically with no `.codex/hooks.json` registration change.
- **Cursor (E), Goose (G), and other non-hooked write paths:** no hook surface exists on these harnesses — that absence is exactly the WI-5811 gap. Parity for them is delivered by the write-path-independent detection core (D1 module, D4 doctor check, D5 state-report surfacing), which is harness-neutral CLI/library code and requires no per-harness hook. No typed waiver is required because no behavioral hook surface is changed for these harnesses.
- **Doctor and state-report surfaces:** harness-neutral `groundtruth_kb` library code; identical behavior regardless of invoking harness.

## DISARM — KB Mechanics

This proposal creates and modifies source, hook, and test files only. No MemBase records, specifications, ADRs, DCLs, work items, Deliberation Archive entries, or other KB-governed artifacts are created, updated, or retired by this work. The `kb_mutation_in_scope: false` flag accurately reflects a pure source/hook/test change with no KB surface mutation. Citations of DELIB and spec IDs in this proposal are read-only references, not mutations.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5811-cross-harness-append-only-enforcement`, run post-GO by the implementing session) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet. It derives from TAFE/dispatcher bridge state, this proposal, and the GO verdict; it expires and fails closed on bridge status drift. The PAUTH triple cited in this proposal's head is the metadata the packet validator consumes; it never broadens `target_paths` and never replaces the live latest-GO requirement.

## Recommended Commit Type

Recommended commit type: feat — net-new detection module, doctor check, state-report surface, and verdict-anchor hardening.

## Loyal Opposition Review Questions

1. Is the two-tier anchor design (surgical `source_content_hash` going forward; coarse `packet_hash` rebuild + git evidence for historical verdicts) the correct precision/coverage trade-off, given the packet-material drift caveat documented above?
2. Is validate-when-present the right gate posture for D3, or should presence become mandatory for new verdicts in a follow-on slice once D2 has been live long enough?
3. Does the four-case detection matrix plus the live glm52-r1 regression test satisfy the spec-derived testing requirement for every linked specification?
4. Is WARN (fail-soft) the correct doctor severity, mirroring WI-4871, or does the first live exploit justify FAIL for DETECT-class findings?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
