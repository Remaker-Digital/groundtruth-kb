REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fe0e5-4e93-7280-9778-8d6738c9626d
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; transcript ::init gtkb pb; harness A; build activity
author_metadata_source: transcript init keyword and Codex runtime system metadata

bridge_kind: implementation_report
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 009
Date: 2026-08-10 UTC
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-008.md
Responds to GO: bridge/gtkb-wi6067-shared-envelope-pointer-purge-006.md
Controlling GO: bridge/gtkb-wi6067-shared-envelope-pointer-purge-006.md
Approved proposal: bridge/gtkb-wi6067-shared-envelope-pointer-purge-005.md
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project Authorization Version: 2
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6067
Recommended commit type: fix:
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py", "groundtruth-kb/src/groundtruth_kb/session/wrap.py", "scripts/harness_envelope_equivalence.py", "scripts/session_role_resolution.py", "scripts/harness_probe_dsv4pro-r1.py", "scripts/harness_probe_dsv4pro_r2.py", "scripts/harness_probe_dsv4pro_r3.py", "scripts/harness_probe_q37flash_r3.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_session_envelope_cli_provenance.py", "platform_tests/scripts/test_harness_envelope_equivalence.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_modernization_harness_parity.py", "platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py", "platform_tests/scripts/test_session_self_initialization.py", "platform_tests/scripts/test_harness_probe_dsv4pro-r1.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r2.py", "platform_tests/scripts/test_harness_probe_dsv4pro_r3.py", "platform_tests/scripts/test_harness_probe_q37flash_r3.py"]

This report performs no MemBase, dispatcher, TAFE, external-system, or credential mutation.

# Prime Builder REVISED Implementation Report — WI-6067 shared-envelope pointer purge

## Result

The approved implementation is present again and its specification-derived behavior is green. The four isolated regressions named by `-008` now pass 4/4. The complete core group reports 93 passed with only the two proposal-disclosed activity-profile drift failures. The corrected 14-module matrix reports 349 passed and exactly four independently owned ambient failures; every session-envelope, role-resolution, equivalence, provenance, provider-probe, and telemetry assertion passes.

The `-008` failures were observed after the implementation payload described by `-007` had disappeared from the shared worktree while the bridge report remained. At corrective start, all 24 declared target paths were clean and `envelope.py` again contained `current_envelope_path`, `projection_path`, the shared pointer/projection writers, and the legacy migration read. That state directly explains why the verifier observed behavior contradicting `-007`.

The corrective implementation restored the prior reviewed source/test payload from Git object evidence left by the interrupted finalization, excluded an unrelated WI-6145 test hunk found in the later shared temporary tree, and reapplied only the existing WI-6067 CLI hunk evidence. Fresh tests below bind the final worktree bytes; the unreachable tree is recovery provenance, not a continuing authority dependency.

## Response To `-008` Findings

### Finding 1 — observed core failures contradicted `-007`

Accepted. The contradiction was real at review time because the implementation bytes were no longer present. After restoring the governed payload:

- `test_topic_open_close_is_strict_and_single_active` passes;
- `test_bare_close_closes_current_topic` passes;
- `test_run_wrap_archives_envelope_with_mandatory_step_results` passes; and
- `test_cli_attests_exact_open_codex_session_metadata` passes.

The four-test command returned **4 passed** in `0.90s`. The complete post-format core group returned **93 passed / 2 failed**; both failures are the already-disclosed stale activity-profile expected string and neither exercises envelope identity, close, wrap, or attestation behavior.

### Finding 2 — ambient-failure disclosure understated the observed set

Accepted and corrected with a fresh full matrix. The final classification is:

1. Two activity-profile expected-string failures in `test_session_envelope_runtime.py`: committed configuration/test drift after additional governed skills were added; no envelope assertion fails.
2. `test_startup_model_contains_role_governance_and_kpi_inventory`: expected Locust `partial`, observed `not_wired`; tracked by WI-5526 and unrelated to session-envelope resolution.
3. `test_cursor_harness_emit_resolves_default_lifecycle_guard`: Windows parent decoding uses cp1252 for UTF-8 subprocess output, leaving `stdout=None`; tracked by WI-6105/WI-5745 and unrelated to session-envelope resolution.

No other failure occurred in the corrected 353-test matrix.

## Corrective Implementation-Start Authorization

- Work-intent claim row: `37810`, session `019fe0e5-4e93-7280-9778-8d6738c9626d`, acquired `2026-08-10T16:34:23Z`.
- Resumption state: `resumable_report_no_go`, binding report `-007`, NO-GO `-008`, and controlling GO `-006`.
- Implementation packet: `sha256:a805e7412a944de6f7398a4b4829066bf395e4ec63a29ccbb16a2d13bba4ec5f`.
- Pre-start packet hash: `sha256:65e3ecfbbd4f4852840e155dc5c76d5f1c20a98396e48ce1d17eb4b8658e747c`.
- Packet created `2026-08-10T16:40:08Z`, expires `2026-08-10T17:25:08Z`; operation-time PAUTH decision: `allowed`.
- Fresh applicability preflight: `preflight_passed: true`, missing required/advisory specs empty, blocking errors empty.
- Clause preflight: exit 0, two `must_apply`, zero evidence gaps, zero blocking gaps.

## Implementation Summary

1. `write_current` writes only the session-id-keyed authoritative document. The shared per-harness pointer and `.claude/session/envelope.json` projection writers and helpers are removed.
2. `load_current`, role provenance, diagnostics, telemetry, equivalence, and role resolution use the exact session-id-keyed document; none select a harness-wide current document.
3. `run_wrap` calls non-creating `close_session`. Missing id, missing document, non-open document, and second close fail without fabricating an envelope or archive.
4. Exact explicit/ambient positive wrap closes only the matching open document, preserves topics, and archives it once.
5. The four provider probes and their regression surfaces resolve the authoritative per-session document.
6. The tracked reader scan has no live shared pointer/projection reader or writer. Remaining matches are dated archive filenames and unrelated harness-registry variables named `projection_path`.

## Hunk Patch Evidence

- Hunk patch: `bridge/cleanup-evidence/gtkb-wi6067-cli-session-handoff.patch`
- Scoped path: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`
- Patch SHA-256: `d3a30da865cdb683836c1250ab3252e20e28f7934c0a1cd15ed73c8466177518`
- Patch size: `2351 bytes`
- Scope: only `_only_open_worker_envelope` and the exact-session fallback in `envelope_attest_author_metadata_cmd`.
- Cached forward check: passed while the real index matched HEAD for the scoped path.
- Reverse worktree containment: passed against the final worktree.
- The formatter changed no hunk content; the evidence patch's two hunks remain exact. Only the informational destination blob id differs from the formatted worktree representation.
- Exclusions: no WI-6055 resolver-unification code, no WI-5812 Goose metadata line, and no `test_gtkb_session_id.py` content.

## Finalization Transaction Scoping

Use the hunk patch above for `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`.

The following 19 paths are full-stage candidates because their current diffs contain the WI-6067 payload only:

- `groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/session/wrap.py`
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `platform_tests/hooks/test_session_role_resolution.py`
- `platform_tests/scripts/test_harness_envelope_equivalence.py`
- `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`
- `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`
- `platform_tests/scripts/test_modernization_harness_parity.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_role_resolution.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `scripts/harness_envelope_equivalence.py`
- `scripts/harness_probe_dsv4pro-r1.py`
- `scripts/harness_probe_dsv4pro_r2.py`
- `scripts/harness_probe_dsv4pro_r3.py`
- `scripts/harness_probe_q37flash_r3.py`
- `scripts/session_role_resolution.py`

Explicit exclusions:

- `platform_tests/scripts/test_gtkb_session_id.py` — unchanged at current HEAD; its former dirty addition belonged to WI-6055.
- `platform_tests/scripts/test_harness_probe_dsv4pro_r2.py`, `platform_tests/scripts/test_harness_probe_dsv4pro_r3.py`, and `platform_tests/scripts/test_harness_probe_q37flash_r3.py` — declared verification surfaces but unchanged.
- The unrelated WI-6145 scratchpad allow-list hunk found in recovery object evidence was deliberately excluded; the current `test_lo_file_safety_gate_role_resolution.py` diff is only the WI-6067 session-id-keyed fixture conversion.
- Every unrelated staged or dirty path outside this report.

Immediately before finalization, recheck all full-file candidates, the mixed path, and the real index. Any new overlap requires fresh hunk evidence rather than broad staging.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v4
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Specification-Derived Verification

| Specification / requirement | Executed verification | Result |
| --- | --- | --- |
| Single-context exact identity and fail-closed wrap | Four verifier-named isolated regressions plus core runtime/CLI group | 4/4 targeted pass; all envelope assertions in the 95-test core group pass |
| No shared pointer/projection | Tracked `git grep` over `groundtruth-kb/src` and `scripts`, plus negative artifact assertions | No live reader/writer; only dated archives and unrelated registry projection variables remain |
| Source-of-truth freshness | Per-session resolution, provider-probe, diagnostic, telemetry, and role tests | All relevant assertions pass |
| Cross-harness parity | Equivalence, marker-scope, role-resolution, SessionStart, provider probes, and telemetry | All relevant assertions pass; two unrelated startup failures classified above |
| Mandatory spec-derived testing | Corrected 14-module matrix, both Ruff gates, diff check, patch checks | 349 passed / four named ambient failures; lint/format/diff/patch gates pass |
| Bridge and project authority | Current controlling GO, exact claim, resumable start packet, preflights | Authorized; preflights pass |

## Commands And Observed Results

1. Verifier-named isolated regressions: **4 passed** in `0.90s`.
2. Final post-format core group (`test_session_envelope_runtime.py`, `test_gtkb_session_id.py`, `test_session_envelope_cli_provenance.py`): **93 passed / 2 failed** in `4.29s`; both failures are the activity-profile string drift above.
3. Corrected 14-module matrix: **353 collected; 349 passed / 4 failed** in `348.16s`. The corrected command uses the tracked underscore filenames `test_harness_probe_dsv4pro_r2.py`, `test_harness_probe_dsv4pro_r3.py`, and `test_harness_probe_q37flash_r3.py`; the `-007` command's hyphen spellings collected zero tests for those paths.
4. `ruff check` over all 24 declared Python targets: **All checks passed**.
5. `ruff format --check` over all 24 declared Python targets: **24 files already formatted**.
6. `git diff --check` over all 24 declared targets: exit 0.
7. Hunk evidence: cached forward-check and reverse worktree containment both pass.
8. Tracked reader scan: zero operative shared pointer/projection readers or writers.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py` — WI-6067 hunks only through declared patch.
- `groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `groundtruth-kb/src/groundtruth_kb/session/wrap.py`
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `platform_tests/hooks/test_session_role_resolution.py`
- `platform_tests/scripts/test_harness_envelope_equivalence.py`
- `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py`
- `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`
- `platform_tests/scripts/test_modernization_harness_parity.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`
- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_role_resolution.py`
- `platform_tests/scripts/test_session_self_initialization.py`
- `scripts/harness_envelope_equivalence.py`
- `scripts/harness_probe_dsv4pro-r1.py`
- `scripts/harness_probe_dsv4pro_r2.py`
- `scripts/harness_probe_dsv4pro_r3.py`
- `scripts/harness_probe_q37flash_r3.py`
- `scripts/session_role_resolution.py`

## Acceptance Criteria Status

- [x] Wrap never opens or fabricates an envelope.
- [x] Missing/foreign contexts fail without a new document or archive.
- [x] Foreign context bytes remain unchanged.
- [x] Exact explicit and ambient positive wraps close/archive once; second wrap fails.
- [x] No tracked source/script reads or writes either shared surface.
- [x] Dedicated role, equivalence, provenance, marker, SessionStart, probe, and telemetry assertions pass.
- [x] Legacy migration reader, `current_envelope_path`, and `projection_path` are absent.
- [x] WI-6055/WI-5812 bytes are excluded from WI-6067 authorship.
- [x] Every observed failure is named and independently classified.

## Prior Deliberations

- `DELIB-20260808-WI6067-WRAP-FABRICATES-ENVELOPE`
- `DELIB-20260808-WI6067-GUARD-CONTRACT-READING`
- `DELIB-20260808-CURRENT-ENVELOPE-OBSOLETE-DESIGN`
- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE`
- `DELIB-20260808-ENVELOPE-ABANDONMENT-NORMAL`
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION`
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION`

## Owner Decisions / Input

No new owner decision is required. This correction implements the existing purge and fail-closed-wrap rulings. The legacy TAFE dispatcher remains disabled and was neither started nor reconfigured.

## Risk And Rollback

The remaining risk is shared-worktree finalization capture. The exact 19-file full-stage list, the single mixed-path hunk patch, explicit exclusions, clean real-index check for the mixed path, and immediate collision recheck make that risk fail-closed. Rollback is the inverse of the same scoped full files plus the WI-6067 hunk patch and must not reverse another thread's bytes. No database row, runtime envelope population, shared artifact, credential, dispatcher, TAFE state, external system, or Git history is mutated by this report.

## Loyal Opposition Asks

1. Re-run the four named regressions and the corrected mapped matrix against the current final bytes.
2. Confirm the implementation payload is present before interpreting report claims.
3. Recheck the zero-reader scan and the WI-6145 exclusion.
4. Validate the existing hunk patch and exact transaction cohort immediately before atomic finalization.
5. Return VERIFIED only through scoped atomic finalization; otherwise return a mechanics-specific NO-GO without discarding the substantive implementation.

---

When you are finished working, close your session envelope by invoking ::wrap.
