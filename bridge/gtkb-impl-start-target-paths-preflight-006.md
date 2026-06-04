NEW

# Implementation Report — Implementation-Start Target-Paths Preflight (WI-3380)

bridge_kind: implementation_report
Document: gtkb-impl-start-target-paths-preflight
Version: 006
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-impl-start-target-paths-preflight-005.md (GO)

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: ff01ba72-8bce-49fd-ab2f-9d2cff01ba72
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Session: continuation — Codex Prime (harness A, session 019e933c) authored -001/-003/-004; Codex LO authored -002 NO-GO, -005 GO; this Claude B session implements per the GO at -005.

Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Work Item: WI-3380
work_item_ids: [WI-3380]
target_paths: ["scripts/impl_start_target_paths_preflight.py", "groundtruth-kb/tests/test_impl_start_target_paths_preflight.py", ".claude/hooks/bridge-compliance-gate.py"]
spec_ids: []

Recommended commit type: feat

---

## Status

Implementation complete. All 5 verification gates PASS. PAUTH amended to include WI-3380 at v4 per S-loop AUQ 2026-06-04 (DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ).

## Specification Links

Specifications carried forward from -004 + GO -005:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index is canonical workflow state; preflight reads live `bridge/INDEX.md`.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — preflight reads live GO file each run, never a cached extraction.
- `GOV-STANDING-BACKLOG-001` — WI-3380 active P1 backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserves WI → proposal → script → test → report chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section + Spec-to-Test mapping.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-Test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + PAUTH + WI metadata declared above.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — implementation creates 1 new script + 1 new test artifact (advisory addition to existing hook).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook integration kept advisory-only via dedicated helper function (no `main()` change).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all 3 target files inside `E:\GT-KB`; outside `applications/`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — script converts a recurring artifact-envelope check into a durable tool artifact.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — CLI smoke demonstrates the deterministic service replacing manual target-path comparison.

## Files Changed

3 files changed, ~670 insertions, 0 deletions:

- `scripts/impl_start_target_paths_preflight.py` (NEW, +307 lines): read-only CLI tool. Resolves latest GO via `bridge_entry`/`approved_files_for_go`, parses target_paths via `extract_target_paths`, glob-matches via `path_authorized` (synthetic-packet pattern). Supports `--candidate-paths`, `--git-diff` (subprocess.check_output), and authorization-packet fallback. Exit codes centralized as named constants `EXIT_OK=0` / `EXIT_NO_GO_FILE=3` / `EXIT_MISSING_TARGETS=4` / `EXIT_SCOPE_DRIFT=5`. JSON + human output paths.
- `groundtruth-kb/tests/test_impl_start_target_paths_preflight.py` (NEW, +297 lines): 21 focused tests covering all 10 enumerated cases in the proposal § Proposed Scope, plus exit-codes-stable and verdict-labels-stable smoke. Uses `tmp_path` fixture with synthetic bridge thread fixtures (`_write_bridge_thread` helper). `--git-diff` tests use `unittest.mock.patch` on `subprocess.check_output` per CQ-TESTS-001.
- `.claude/hooks/bridge-compliance-gate.py` (EDIT, +66 lines, purely additive): adds `preflight_advisory_for_write(cwd_path, file_path, *, bridge_id=None)` helper above `_audit_only`. Function is non-blocking: fail-soft import, returns `None` on any error or missing packet. Helper is NOT called from `main()` per the proposal's advisory-only constraint; defines the call path for future revisions to wire in without widening current block/pass authority.

## Spec-to-Test Mapping

| Test | Spec(s) | Result |
|------|---------|--------|
| `test_all_candidates_in_scope_returns_exit_ok` | GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | **PASS** |
| `test_single_out_of_scope_candidate_returns_exit_drift` | codex-review-gate.md (drift reporting before impl proceeds) | **PASS** |
| `test_multiple_out_of_scope_candidates_returns_exit_drift` | codex-review-gate.md | **PASS** |
| `test_mixed_in_and_out_of_scope_returns_exit_drift` | codex-review-gate.md | **PASS** |
| `test_recursive_glob_matches_nested_paths` | GOV-FILE-BRIDGE-AUTHORITY-001 (glob semantics match impl-auth gate) | **PASS** |
| `test_recursive_glob_rejects_out_of_subtree` | GOV-FILE-BRIDGE-AUTHORITY-001 | **PASS** |
| `test_unused_targets_reported_but_do_not_fail` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | **PASS** |
| `test_falls_back_to_named_packet_when_no_explicit_candidates` | GOV-STANDING-BACKLOG-001 (auth-packet fallback per WI-3380) | **PASS** |
| `test_no_candidates_and_no_packet_reports_none_source` | (defensive) | **PASS** |
| `test_no_go_file_returns_exit_3` | GOV-FILE-BRIDGE-AUTHORITY-001 | **PASS** |
| `test_unknown_bridge_id_returns_exit_3` | GOV-FILE-BRIDGE-AUTHORITY-001 | **PASS** |
| `test_missing_target_paths_returns_exit_4` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | **PASS** |
| `test_empty_target_paths_returns_exit_4` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | **PASS** |
| `test_json_output_schema` | DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (deterministic JSON schema) | **PASS** |
| `test_human_output_includes_expected_lines` | (defensive) | **PASS** |
| `test_git_diff_collects_candidates_via_subprocess` | GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | **PASS** |
| `test_git_diff_subprocess_error_yields_empty_candidates` | (defensive) | **PASS** |
| `test_hook_existing_required_fields_constant_unchanged` | ADR-CODEX-HOOK-PARITY-FALLBACK-001 (hook authority unchanged) | **PASS** |
| `test_hook_module_imports_cleanly_after_advisory_change` | ADR-CODEX-HOOK-PARITY-FALLBACK-001 | **PASS** |
| `test_exit_codes_stable` | CQ-CONSTANTS-001 (centralized exit codes) | **PASS** |
| `test_verdict_labels_stable` | CQ-CONSTANTS-001 (centralized verdict strings) | **PASS** |

Total: **21 tests, 21 passed in 0.34s**.

## Verification Evidence

```text
# Pre-edit: claim + impl-start packet
python scripts/bridge_claim_cli.py claim gtkb-impl-start-target-paths-preflight
# acquired_at=2026-06-04T16:10:26Z, session_id=ff01ba72-..., ttl=10min

python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-target-paths-preflight
# Packet written; target_path_globs = [3 files matching proposal -004]

# Post-edit verification gates
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <3 files>
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <3 files>
# 3 files already formatted

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_impl_start_target_paths_preflight.py -v --tb=short
# 21 passed in 0.34s

# CLI smoke against live bridge state (this thread, self-test)
python scripts/impl_start_target_paths_preflight.py --bridge-id gtkb-impl-start-target-paths-preflight --candidate-paths <3 files> --json
# exit=0, verdict=in_scope, 3 candidates / 3 targets all matched, 0 unused, 0 out-of-scope
# GO file resolved to: bridge/gtkb-impl-start-target-paths-preflight-005.md
# Approved proposal resolved to: bridge/gtkb-impl-start-target-paths-preflight-004.md
```

The live CLI smoke executed end-to-end against THIS bridge thread (self-test): the preflight resolved its own GO file at `-005`, parsed `target_paths` from the approved proposal at `-004`, and correctly matched all 3 candidate files in scope. This is the deterministic-service dogfood evidence demanded by `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

## Implementation Constraints Satisfied

Per the GO at -005 § Implementation Constraints:

1. Ran `python scripts/implementation_authorization.py begin --bridge-id gtkb-impl-start-target-paths-preflight` before editing.
2. The new script is read-only: only `subprocess.check_output` is invoked (read-only git command); no file mutations, no MemBase mutations, no INDEX mutations, no packet mutations.
3. `.claude/hooks/bridge-compliance-gate.py` integration is advisory-only: `preflight_advisory_for_write` is added as a standalone helper; `main()` does NOT call it; existing `emit_pass`/`emit_ask`/`emit_deny` flow is byte-identical to the pre-edit state. The hook's regression tests in the new test file lock the `WRITE_TOOLS` constant and the `REQUIRED_AUTHOR_METADATA_FIELDS` tuple to confirm authority unchanged.
4. Post-implementation report includes: targeted pytest (21/21 PASS), ruff check (PASS), ruff format check (PASS), preflight smoke (exit 0), and implementation-authorization packet smoke (packet written).

## PAUTH Amendment Note (Cross-Harness Gate Divergence)

This report was originally blocked by the Claude bridge-compliance PreToolUse gate which strictly enforces `included_work_item_ids` against the cited PAUTH. The PAUTH `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH` at v3 did NOT include WI-3380 in its explicit list; WI-3380's authorization theory was active project membership only (which the impl-auth layer's `validate_project_authorization_row` accepts but the bridge-compliance hook does not).

Owner AUQ at 2026-06-04 16:23 UTC approved adding WI-3380 to the PAUTH's `included_work_item_ids`. The PAUTH was amended to v4 via `gt projects authorize PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY --id PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH --owner-decision DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ --include-work-item WI-3380 [+ 10 prior WIs preserved] --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec ADR-CODEX-HOOK-PARITY-FALLBACK-001 --allowed-mutation cli_extension,hook_upgrade,source,test_addition,rules,governance_evidence`.

`DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ` records the AUQ Q+A in the Deliberation Archive (source_type=owner_conversation, outcome=owner_decision). PAUTH v4 active; 11 WIs included (original 10 + WI-3380); same allowed_mutation_classes; same expires_at (None).

This gate divergence (impl-auth membership-accept vs bridge-compliance strict-list) is logged as a candidate hygiene WI for a future session: align the bridge-compliance gate's WI check with `validate_project_authorization_row`'s project-membership semantics so the two layers agree on what's authorized.

## Owner Decisions / Input

- Existing project membership + active PAUTH (v3 → v4) carried forward from -004; original 10-WI scope preserved.
- **2026-06-04 16:23 UTC, S-loop AUQ**: owner selected "Approve PAUTH update: add WI-3380" — recorded as `DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ` (source_type=owner_conversation, outcome=owner_decision). The Q+A is captured in the Deliberation Archive and in `memory/pending-owner-decisions.md` via the owner-decision-tracker hook.
- `DELIB-20260638` confirms WI-3380 as Phase 0 bridge reliability work in the standing major-release order.

No new owner decisions requested by this report. Loyal Opposition VERIFIED or NO-GO verdict is the next step.

## Prior Deliberations

- `DELIB-20260638` — Phase 0 bridge reliability work order; names WI-3380.
- `DELIB-S367-PAUTH-BRIDGE-PROTOCOL-RELIABILITY-AMENDMENT-WORK-INTENT` — original owner-approved PAUTH amendment underpinning this thread's authorization.
- `DELIB-S-LOOP-2026-06-04-WI3380-PAUTH-INCLUSION-AUQ` — owner approval (2026-06-04) to add WI-3380 to the PAUTH's `included_work_item_ids` after the bridge-compliance gate surfaced the included-list divergence.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — target-path drift preflight is exactly the class of deterministic service this principle endorses.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — negative boundary (carried forward from -003 NO-GO).
- `bridge/gtkb-impl-start-target-paths-preflight-003.md` — initial corrective NO-GO on -001 (PAUTH mismatch).
- `bridge/gtkb-impl-start-target-paths-preflight-004.md` — REVISED proposal with corrected authorization (the approved scope this implementation realizes).
- `bridge/gtkb-impl-start-target-paths-preflight-005.md` — Codex LO GO authorizing implementation.

## Specification-Derived Verification Plan

Carried forward from -004 + GO -005; executed and recorded above (Spec-to-Test Mapping + Verification Evidence). All 21 test rows PASS in live state.

## Risk / Rollback

- **Risk: low.** New read-only script + new test file; hook edit is purely additive (one new helper function above `_audit_only`); zero modifications to `main()`. The hook's gate behavior (which gates ALL Write/Edit operations across the repo) is byte-identical to the pre-edit state.
- **Rollback path:** revert the single fix commit. The new script + test file are isolated and deletable; the hook's added helper function can be removed without affecting any active call path. PAUTH v4 → v3 rollback would require a separate owner-authorized supersede operation.
- **Forward-compatibility:** `preflight_advisory_for_write()` in the hook is the integration point for future slices that may wire the preflight into the gate's `emit_ask`/`emit_deny` decision flow (with appropriate regression coverage).

## Recommended Commit Type

`feat:` — net-new operator-invoked script surface + tests + advisory helper. Diff stat: 3 files changed, ~670 insertions, 0 deletions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
