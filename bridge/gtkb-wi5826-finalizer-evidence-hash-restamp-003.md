NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code implementation worker dispatched under the DELIB-202667735 parallel-operation mandate; resolved role prime-builder; implementation-and-report scope only - no commit, no push, no review, no session wrap

bridge_kind: implementation_report
Document: gtkb-wi5826-finalizer-evidence-hash-restamp
Version: 003
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5826-finalizer-evidence-hash-restamp-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5826

target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", ".codex/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py"]
implementation_scope: verified_finalizer_candidate_evidence_hash_restamp
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5826 Implementation Report — Re-Stamp `candidate_evidence_hash` Over The Final Verdict Bytes

## Summary

The GO'd design at `-001` is implemented as approved, with one narrowing recorded under Deviations. `finalize_verified_commit` now pre-applies the writer's own pre-audit normalization and re-stamps the self-referential `candidate_evidence_hash` field as its last act before `write_bridge_file`, so the stamped bytes are the audited bytes. The gate remains the single definition of the hash algorithm; the helper loads it rather than re-implementing it, and fails closed when it cannot.

The defect and its repair were both reproduced directly. With the re-stamp neutralized, a fixture finalization is rejected with the exact production failure text, `Verdict applicability freshness check rejected a stale or missing candidate_evidence_hash`. With the re-stamp active, the same body finalizes and the recomputation over the final on-disk bytes equals the stamped value. That negative control is the evidence that the new regression module is not vacuous.

Three files changed, exactly the declared target paths. No commit was created; this session performs no commit, push, review, or session wrap.

## Changes Implemented

### 1. `.claude/skills/gtkb-verify/helpers/write_verdict.py` (canonical)

- Added `import importlib.util`.
- Added `_load_bridge_compliance_gate(project_root)`. It resolves the gate through the writer's own `_bridge_compliance_gate_path`, so the module loaded is the same file `run_bridge_compliance_audit` executes for that project root, and caches per resolved path. Every failure path raises `VerifiedFinalizationError`, matching the fail-closed posture of the existing review-independence comparator.
- Added `_restamp_candidate_evidence_hash(body, *, verdict_rel_path, project_root)`. Deterministic, with no clock, no network, and no retry. It pre-applies `ensure_author_metadata` then `normalize_bridge_envelope_head`; counts field occurrences with the gate regex; computes the value with the gate function; substitutes it back; then asserts two runtime invariants before returning — that re-applying the writer normalization is a no-op, and that recomputing the hash over the stamped body reproduces the stamped value.
- Wired the call into `finalize_verified_commit` after `_append_commit_finalization_evidence` and after both author-metadata assertions, immediately before `write_bridge_file`. All existing preconditions, staged-set checks, disposable-index mechanics, and rollback behavior are untouched.

### 2. `.codex/skills/gtkb-verify/helpers/write_verdict.py` (projection)

Regenerated with `scripts/generate_codex_skill_adapters.py`, not hand-edited. Byte identity with the canonical helper is confirmed by digest and asserted by test.

### 3. `platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py` (new)

Twelve tests. The fixture repo carries a full Applicability Preflight section with a real rebuilt packet hash, so the green cases exercise the actual production body shape end to end through the real gate subprocess.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — the WI-5826 source specification; terminal-verdict finalization through the governed path is restored and the append-only numbered chain is preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — linkage carried forward from the proposal into this report.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — the mapping below derives every test from a linked requirement and records executed results.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — the header triple and the implementation-start packet evidenced below.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required (blocking) — the re-stamp runs after the review-independence and synthetic-session guards and preserves their fail-closed behavior.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — required (blocking) — the Codex submission path receives the identical fix by regenerated projection.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — required (blocking) — per-harness disposition is declared below; no waiver requested.
- `ADR-CROSS-HARNESS-PARITY-001` — required (blocking) — no harness-conditional branch and no environment gate was introduced.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact was created, updated, or retired.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — all three target paths are in-root; no application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory — the change restores coherence between the write-time gate and the finalization helper rather than weakening either.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — an undocumented manual derivation and a per-harness runtime monkeypatch are replaced by one deterministic helper step.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — the gate is loaded as the single hash definition rather than copied; all evidence below is from fresh reads and live command output this session.
- `SPEC-1662` — advisory — assertions are behavioral, and the negative control demonstrates they fail when the fix is removed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the terminal verdict artifact is reachable through the governed path again.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — verdict, stamped evidence field, and finalization commit remain one linked record.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — advisory — finalization behaves identically on whichever harness holds Loyal Opposition.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5826 is the sole work authority.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin lifecycle transitions.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_final_verdict_bytes_match_stamped_candidate_evidence_hash` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_finalization_succeeds_where_stale_stamp_previously_denied` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_evidence_append_path_is_hash_consistent` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_prior_deliberations_seeding_path_is_hash_consistent` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_writer_normalization_is_idempotent_for_finalizer_bodies` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_restamp_returns_body_whose_recomputation_is_a_fixpoint` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_missing_candidate_evidence_hash_field_fails_closed` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_duplicate_candidate_evidence_hash_field_fails_closed` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_body_without_preflight_section_needs_no_stamp` | yes | PASS |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_gate_module_unavailable_fails_closed` | yes | PASS |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_codex_adapter_projection_matches_canonical_helper` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py::test_restamp_is_wired_into_finalization` | yes | PASS |
| `ADR-CROSS-HARNESS-PARITY-001` | `python scripts/generate_codex_skill_adapters.py --check` | yes | PASS for the helper projection; see Deviations item 3 for the two unrelated files it reports |
| `SPEC-1662` | negative control with the re-stamp neutralized | yes | DENIED as expected with the production stale-hash message |

## Commands Executed

Every command was run from `E:\GT-KB` with the project virtual environment interpreter.

1. `python -m ruff check .claude/skills/gtkb-verify/helpers/write_verdict.py .codex/skills/gtkb-verify/helpers/write_verdict.py platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py`
   Observed: `All checks passed!`, exit 0.

2. `python -m ruff format --check .claude/skills/gtkb-verify/helpers/write_verdict.py .codex/skills/gtkb-verify/helpers/write_verdict.py platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py`
   Observed: `3 files already formatted`, exit 0. This gate initially failed twice on the new test module with `1 file would be reformatted` and was resolved by running `python -m ruff format` on that module; the two gates are reported separately because passing the lint gate does not imply passing the format gate.

3. `python -m pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py -q`
   Observed: `12 passed, 1 warning`, exit 0.

4. `python -m pytest platform_tests/skills/test_verified_finalization_candidate_evidence_hash_restamp.py platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py platform_tests/scripts/test_generate_codex_skill_adapters.py -q`
   Observed: `4 failed, 92 passed, 1 warning, 34 errors`.

5. Pre-change baseline for the same suites excluding the new module and the adapter suite:
   `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_verified_finalization_validation_hardening.py platform_tests/hooks/test_bridge_compliance_gate_lo_verdict_candidate_preflight.py platform_tests/skills/test_verify_prior_deliberations_pre_population.py -q`
   Observed: `4 failed, 47 passed, 1 warning, 34 errors`.

   The failing and erroring sets are identical before and after the change, so there are zero regressions. Both pre-existing causes are outside the declared target paths and are described under Pre-Existing Conditions.

6. `python scripts/generate_codex_skill_adapters.py` then `python scripts/generate_codex_skill_adapters.py --check`
   Observed: the generator updated the helper projection, and `--check` reported `PASS (44 adapters current)` at that moment. See Deviations item 3 for the two additional files the generator touched and why they were reverted.

7. Negative control, executed from a scratch script under `.gtkb-state/wi5826-scratch/` and deleted afterward: the fixture finalization was re-run with `_restamp_candidate_evidence_hash` replaced by identity.
   Observed: `BridgeComplianceError: [Governance] Verdict applicability freshness check rejected a stale or missing candidate_evidence_hash; expected sha256:088e24f5917f856d3ee1fe358b109e58e70933bd01ebf04d67623ce0282b0f70 for the final normalized candidate bytes.` This is the production defect text, reproduced and then eliminated by the change.

8. `git --no-optional-locks status --porcelain` restricted to the declared target paths.
   Observed: the two helpers modified and the test module untracked, and nothing else.

## Implementation Start Evidence

- Work-intent claim acquired before drafting: `python scripts/bridge_claim_cli.py claim gtkb-wi5826-finalizer-evidence-hash-restamp`, `acquired_at` 2026-07-31T15:08:57Z, `claim_kind` `go_implementation`, `acting_role` `prime-builder`, session `bba2e933-5d36-4c5b-ad04-08a653c8700f`, rowid 35358.
- Packet minted before any mutation: `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5826-finalizer-evidence-hash-restamp`.
- Packet path: `E:\GT-KB\.gtkb-state\implementation-authorizations\by-bridge\gtkb-wi5826-finalizer-evidence-hash-restamp.json`; active pointer `E:\GT-KB\.gtkb-state\implementation-authorizations\current.json`.
- `created_at` 2026-07-31T15:10:29Z; `expires_at` 2026-07-31T17:10:29Z; `latest_status` GO; `go_file` `bridge/gtkb-wi5826-finalizer-evidence-hash-restamp-002.md`; `packet_hash` `sha256:f841926b1dacb94c8cd7b33099e52aa9fbe61794537f73863ff804bba528eea7`.
- Project-authorization decision: allowed, reason code `allowed`, authorization `PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730` version 1, work item WI-5826. Target classification: the two helper paths as `configuration` and the test module as `test`.
- No live packet was overwritten and no peer path reservation was encountered.

## Cross-Harness Disposition

The declared target paths touch `.claude/skills/**` and `.codex/skills/**`, so this change is a harness-surface change and behavioral parity is declared per applicable harness. No waiver is requested and none is needed.

- Claude, harness B: parity by construction. The canonical helper carries the change, which runs inside `finalize_verified_commit` on every invocation with no harness-conditional branch and no environment-variable gate.
- Codex, harness A: parity by regenerated projection. The adapter helper was regenerated by the generator rather than hand-edited and is byte-identical to the canonical helper, confirmed by matching digest `fe441376957c64787fe5f1a8787cdbb50f79074bcdd6e8b23f5d182f221e76bd` and asserted by `test_codex_adapter_projection_matches_canonical_helper`.
- Antigravity, harness C, and Cursor: not applicable. Neither surface carries a `gtkb-verify` helpers directory in the tracked tree, so there is no projection to update and no behavioral surface to diverge.
- Goose: known pre-existing divergence, explicitly out of scope as approved at GO. The tracked third copy differs from the canonical helper today and no Goose adapter generator exists. This change neither widens nor repairs that drift. See Follow-On Candidates.
- Ollama and OpenRouter: not applicable. These harnesses consume skills through routing configuration rather than a mirrored helpers directory.

## Deviations From The Approved Design

1. **Zero-occurrence rule narrowed to the gate's own activation condition.** The approved design says a body with zero `candidate_evidence_hash` fields raises. Implemented as: more than one occurrence always raises; zero occurrences raises when the body carries an Applicability Preflight section, and is a no-op otherwise. Rationale: the gate only checks the field when that section is present, so an unconditional raise would newly reject verdict bodies the gate accepts today and would violate the zero-regression acceptance criterion. The narrowing mirrors the gate exactly and preserves the fail-closed intent everywhere the gate can deny. It is covered by `test_missing_candidate_evidence_hash_field_fails_closed` and `test_body_without_preflight_section_needs_no_stamp`. Flagged for reviewer confirmation.

2. **One additional import from the writer.** The design named `ensure_author_metadata` and `normalize_bridge_envelope_head`. The implementation also imports `_bridge_compliance_gate_path` so the helper loads the exact gate module the audit will execute for the same project root. Re-deriving that resolution locally would risk selecting a different gate than the auditor. This remains import-only; `scripts/gtkb_bridge_writer.py` was neither edited nor staged, preserving disjointness from the concurrently GO'd WI-5825 thread.

3. **Generator side effects reverted to hold scope.** Running the adapter generator updated `.codex/skills/MANIFEST.json` and `config/agent-control/gtkb-harness-capability-registry.toml` in addition to the helper. Both edits were a `source_sha256` refresh derived from `.claude/skills/gtkb-verify/SKILL.md`, which is dirty from the separate non-terminal wi5827 thread and is not a target path here. My change to the helper does not affect those digests. Both files were reverted to their prior values so this diff is exactly the three declared target paths. Consequence: `generate_codex_skill_adapters.py --check` now reports those two files as pending, which is pre-existing wi5827-owned drift that wi5827's finalization should regenerate. The helper projection itself is current and is not reported.

4. **Direct `git checkout` is not an authorized boundary.** Reverting item 3 by `git checkout --` was blocked by the GTKB-GIT-LIFECYCLE hook, and `python -m groundtruth_kb.git_lifecycle` exposes `restore-deleted-path` for deletions but no restore for a modified tracked file. The two single-line values were therefore reverted by targeted edit to their exact prior digests. Surfaced as a small gap in the lifecycle surface rather than worked around silently.

## Pre-Existing Conditions Observed (not introduced, not repaired here)

1. **Stale skill directory name in test path constants.** `platform_tests/scripts/test_lo_verified_commit_atomicity.py` and `platform_tests/skills/test_verify_prior_deliberations_pre_population.py` resolve helpers at `.claude/skills/verify/helpers/write_verdict.py` and `.codex/skills/verify/helpers/write_verdict.py`. The skill is `gtkb-verify`, so those modules raise `FileNotFoundError` at setup. This accounts for all 34 errors and 3 of the 4 failures, both before and after this change. The practical effect is that the entire VERIFIED finalization atomicity suite is not executing today. Outside the declared target paths, so not repaired here.

2. **Line-ending drift between the active gate and its template.** `test_active_and_template_hooks_remain_byte_identical` fails because `.claude/hooks/bridge-compliance-gate.py` and `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` differ only by CRLF against LF. This is the fourth pre-existing failure. Outside the declared target paths.

3. **A governance PreToolUse hook emitted an inapplicable NO-GO warning on every edit in this session:** `Bridge proposal for this module has NO-GO status. Review Codex findings at bridge/gtkb-wi5441-registry-control-plane-reverse-coverage before implementing.` That thread is at NO-GO, but its declared target paths cover the registry control plane, the SoT registry, and the implementation-start gate, and contain none of this thread's three target paths. The warning fired on unrelated files including the manifest and the capability registry. It was verified as a misfire before proceeding; the authorization chain here is a live GO plus a validated packet. Recorded because a warning that fires on unrelated edits trains readers to ignore it, which erodes a real signal.

## Acceptance Criteria Check

1. Both ruff gates pass separately on all three changed files — met, commands 1 and 2.
2. The new regression module passes — met, 12 passed.
3. The Codex projection is byte-identical after regeneration — met, matching digests and a passing assertion.
4. TEST-11782 holds end to end: recomputation over the final on-disk verdict bytes equals the stamped value — met in every green finalization test, and shown to fail without the change by the negative control.
5. Every failure mode leaves no terminal verdict artifact and no new commit — met; the fail-closed tests assert artifact absence and unchanged git log.
6. Zero new hard-coded timer, interval, retry, or throttle literals — met; the re-stamp is a pure deterministic transform.
7. No file outside the three declared target paths is modified — met after the item 3 revert, confirmed by scoped status.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring and unblock-implementation mandate for the parallel-operation program authorizes this worker to implement the GO'd WI-5826 thread and file this report. Scope is implementation and reporting only: no commit, no push, no review, and no session wrap were performed.
2. **DELIB-202667731** — the owner's list-free whole-project grant recorded as PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730 covers WI-5826 and supplied the authorization evidence the packet validator consumed. Its recorded scope requires this work item to complete its own governed cycle, so independent Loyal Opposition verification with governed atomic finalization is still required.
3. No new owner decision is required to verify this report. One reviewer confirmation is requested on Deviations item 1.

## Risk And Rollback

- The semantic change is bounded to VERIFIED finalization. Reviewer-authored GO and NO-GO stamping behavior is untouched.
- Normalization drift is guarded twice at runtime: a no-op assertion on re-applied normalization and a hash fixpoint assertion, both raising before any write.
- Gate coupling is deliberate and fail-closed; an unavailable gate denies finalization rather than writing an unverifiable verdict.
- Rollback is source-only: revert the canonical helper, regenerate the Codex projection, delete the new test module. No MemBase record, no dispatcher or TAFE state, and no existing bridge chain file is touched.

## Follow-On Candidates (not implemented here)

1. Repair the stale `skills/verify` path constants so the VERIFIED finalization atomicity suite executes again. This is the highest-value item observed; a suite that cannot import is indistinguishable from a passing suite in aggregate counts.
2. Normalize the line endings between the active compliance-gate hook and its template.
3. Address the Goose helper divergence and the missing Goose adapter generator.
4. Consider moving the re-stamp seam into the writer immediately before the audit once WI-5825 has landed, which would extend the guarantee to GO and NO-GO authoring. This is Loyal Opposition review question 1 from the proposal and is deliberately not done here.
5. Scope the misfiring NO-GO advisory hook in Pre-Existing Conditions item 3 to the thread whose target paths actually match the edited file.

## Note For A Future Finalization

A post-NO-GO REVISED report whose `Responds to` is not the controlling GO must carry a machine-readable `Controlling GO:` line, parsed by `CONTROLLING_GO_RE` in `scripts/check_protected_commit_authorization.py`, where more than one start-of-line match raises. This report is a NEW report responding directly to the GO, so no such line is required or present.

## DISARM — KB Mechanics

This work performs no MemBase mutation. No KB write, no MemBase insert, and no groundtruth.db change of any kind occurred. Only source and test files were created or modified. The `kb_mutation_in_scope: false` flag accurately reflects a pure source-and-test change. Every specification, deliberation, work-item, and test identifier cited here is a read-only reference used as evidence.

## DISARM — Packet Mechanics

The implementation-start packet evidenced above is session-local implementation-scope evidence. It is not a formal artifact and requires no formal-artifact approval packet, because no approval-gated artifact was created, changed, or inserted. The packet derives from dispatcher and TAFE bridge state, the approved proposal file, and the GO verdict file; it expires and fails closed on bridge status drift. It never broadened the declared target paths.

## Recommended Commit Type

Recommended commit type: fix — this repairs a defect that made the sanctioned terminal-verdict finalization path structurally unusable, with regression coverage and a reproduced negative control. It adds no new capability surface; the re-stamp is the missing step in an existing transaction.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
