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
Version: 011
Date: 2026-08-10 UTC
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-010.md
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

This report performs no MemBase, dispatcher, TAFE, external-system, credential,
shared-index, or Git-history mutation.
This report performs no MemBase mutation.

# Prime Builder REVISED Implementation Report — WI-6067 shared-envelope pointer purge

## Result

The accepted shared-pointer purge remains present. The `-010` verifier failures
were caused by tests inheriting an unrelated ambient `GTKB_SESSION_ID`, not by
the removal of `current_envelope_path` or `projection_path`. Seven tests now
bind their follow-on operations to the exact session that each test opened.

With `GTKB_SESSION_ID=foreign-reviewer-session` deliberately set, the four
verifier-named regressions pass 4/4. The full runtime and provenance pair reports
73 passed and the same two proposal-disclosed activity-profile expectation
drifts. The corrected 14-module matrix reports 349 passed and exactly four
independently owned ambient failures. Every session-envelope, provenance,
role-resolution, equivalence, provider-probe, and telemetry assertion passes.

No production identifier, shared pointer, projection, migration reader, or
creating wrap fallback was restored. The absence of `current_envelope_path` and
`projection_path` from `session/envelope.py` is the approved end state, not a
missing payload.

## Findings Addressed

### F1 (P1) — The four named regression tests fail 4/4 in the live worktree

Corrected. The tests opened a generated per-session document and then allowed
later topic, wrap, or attestation calls to re-resolve the current context from
an ambient marker. In the reviewer's shell that marker named a different
session, so the follow-on operation correctly failed closed or reached no
matching document. The test setup was nondeterministic.

The correction sets `GTKB_SESSION_ID` through `monkeypatch` to the exact opened
session id before the follow-on operation in:

- `test_topic_open_close_is_strict_and_single_active`;
- `test_bare_close_closes_current_topic`;
- `test_run_wrap_archives_envelope_with_mandatory_step_results`;
- `test_cli_attests_exact_open_codex_session_metadata`;
- `test_cli_attests_exact_open_cursor_session_metadata`;
- `test_cli_attestation_rejects_noncurrent_session_without_replacing_projection`;
- `test_cli_attestation_promotes_existing_exact_open_codex_thread`.

This makes the tests exercise the exact-context contract under any caller
environment. It does not weaken the fail-closed runtime or recreate a
harness-wide current pointer.

### F2 (P1) — Requirement Sufficiency Gate D fails

Corrected by the bounded statement below.

## Requirement Sufficiency

Existing requirements are sufficient.

The correction is test hermeticity within the already approved WI-6067 design.
It introduces no new runtime capability, requirement, target, mutation class,
or owner decision.

## Implementation Authorization

- claim session: `019fe0e5-4e93-7280-9778-8d6738c9626d`
- controlling GO: `bridge/gtkb-wi6067-shared-envelope-pointer-purge-006.md`
- resumption state: `resumable_report_no_go`
- implementation packet hash:
  `sha256:bdf7cc0d602b009ae84225c28b66622f63e3147ee966ef635faea012c99a7cd4`
- pre-start packet hash:
  `sha256:2829539e078a9f78b1203e58830a08a0969d20b2adcda1346b7535a7e02674fe`

## Scope And Authorship

The corrective cycle changes only the two already approved test paths:

- `platform_tests/scripts/test_session_envelope_runtime.py`
- `platform_tests/scripts/test_session_envelope_cli_provenance.py`

The complete WI-6067 implementation remains the 20 modified source/test paths
reported by `-009`, with `cli_session_handoff.py` isolated by the existing
reviewed hunk patch. `test_gtkb_session_id.py` and the three tracked underscore
probe tests remain declared verification paths but have no worktree diff.

The untracked GLM 5.2 R3 probe files are excluded. They are owned by the separate
WI-6079 carrier and were not edited, staged, claimed, or used as WI-6067
finalization evidence.

## Hunk And Finalization Evidence

`bridge/cleanup-evidence/gtkb-wi6067-cli-session-handoff.patch` remains the sole
WI-6067 carrier for the mixed `cli_session_handoff.py` path.

- SHA-256:
  `d3a30da865cdb683836c1250ab3252e20e28f7934c0a1cd15ed73c8466177518`
- reverse worktree containment: pass
- the shared real index was not reset, rewritten, or used for validation

The 19 full-file candidates remain:

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

Finalization must include the complete predecessor chain through this report,
the reviewed hunk patch, the 19 full-file paths, and the independent terminal
verdict in one scoped transaction. It must not whole-stage the mixed CLI path or
capture any unrelated staged/worktree bytes.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v4 — exact session-context
  identity, context-keyed state, and fail-closed close/wrap behavior.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — no shared projection is current-state
  authority.
- `ADR-CROSS-HARNESS-PARITY-001` — marker and role behavior remains uniform.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the mapped matrix and
  named regressions are reported below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing
  requirements remain linked.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the correction remains
  inside the approved thread and PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the reviewer-observed environment
  defect is preserved and corrected in the existing carrier.

## Prior Deliberations

- `DELIB-20260808-WI6067-WRAP-FABRICATES-ENVELOPE`
- `DELIB-20260808-WI6067-GUARD-CONTRACT-READING`
- `DELIB-20260808-CURRENT-ENVELOPE-OBSOLETE-DESIGN`
- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE`
- `DELIB-20260808-ENVELOPE-ABANDONMENT-NORMAL`
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION`
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION`

## Specification-Derived Verification

| Requirement | Verification | Result |
|---|---|---|
| Exact-context topic and close behavior | Three named runtime regressions with a foreign ambient marker | 3 passed |
| Exact-context attestation | Named Codex regression plus the complete provenance module with a foreign ambient marker | named test passed; module 33 passed |
| No shared pointer/projection | Tracked `git grep` plus negative artifact assertions | zero operative shared reader/writer |
| Fail-closed wrap | Missing/foreign/exact-session runtime cases in the runtime module | all relevant assertions passed |
| Cross-harness parity | Corrected 14-module matrix | all relevant assertions passed |
| Mandatory spec-derived testing | Named regressions, matrix, Ruff, format, diff, and hunk checks | complete; ambient failures disclosed |

## Commands And Observed Results

1. With `GTKB_SESSION_ID=foreign-reviewer-session`, the four verifier-named
   regressions: **4 passed** in `0.89s`.
2. With the same foreign marker, runtime plus CLI provenance: **73 passed / 2
   failed** in `4.00s`. The failures are the already disclosed activity-profile
   string expectations.
3. With the same foreign marker, corrected 14-module matrix: **353 collected;
   349 passed / 4 failed** in `261.56s`.
4. The other two matrix failures remain outside this change:
   `test_startup_model_contains_role_governance_and_kpi_inventory` expects
   `partial` while live inventory says `not_wired`, and
   `test_cursor_harness_emit_resolves_default_lifecycle_guard` encounters the
   pre-existing Windows CP1252 subprocess decoding fault.
5. `ruff check` over all 24 declared Python targets: **All checks passed**.
6. `ruff format --check` over all 24 declared Python targets: **24 files already
   formatted**.
7. `git diff --check` over all 24 declared targets: exit 0.
8. Tracked reader scan: no `.claude/session/envelope.json`,
   `current_envelope_path`, or session-envelope `projection_path` reader/writer;
   remaining `projection_path` matches are harness-registry projection APIs.
9. Hunk patch reverse worktree containment: pass.

## Acceptance Criteria Status

- [x] Wrap does not open or fabricate an envelope.
- [x] Missing and foreign contexts fail without changing another context.
- [x] Explicit and ambient positive wrap close only the exact open document.
- [x] A second close fails without a second archive.
- [x] No tracked live source/script reads or writes the shared pointer or
  projection.
- [x] Dedicated role, equivalence, provenance, marker, SessionStart, probe, and
  telemetry assertions pass.
- [x] Legacy migration reader, `current_envelope_path`, and session-envelope
  `projection_path` remain absent.
- [x] The verifier-named environment is reproduced and the four named tests pass.
- [x] The bounded Requirement Sufficiency statement is present.
- [x] Ambient failures are named and not normalized into passing results.

## Owner Decisions / Input

No new owner decision is required. This revision implements the existing purge
and fail-closed-wrap rulings. The legacy TAFE dispatcher remains disabled and
was neither started nor reconfigured.

## Risk And Rollback

The remaining risk is shared-worktree finalization capture. Finalization must
use the reviewed CLI hunk patch, the 19 exact full-file paths, the complete
bridge chain, and the terminal verdict while preserving unrelated index and
worktree bytes. Rollback is the inverse of that same scoped cohort. No database
row, runtime envelope population, credential, dispatcher, TAFE state, external
system, or Git history was mutated by this corrective cycle.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
