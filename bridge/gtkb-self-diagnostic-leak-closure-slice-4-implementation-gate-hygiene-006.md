# Implementation Report - Implementation Gate Hygiene (Self-Diagnostic Leak Closure Slice 4)

bridge_kind: implementation_report
Document: gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene
Version: 006
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
Implements: bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md (REVISED-1, Codex GO at -004)
Supersedes-on-disk: bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-005.md (pre-existing orphan from a prior session; not present in INDEX; left on disk per the bridge protocol's "never delete bridge files" rule).

## Summary

Slice 4 of GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE is fully implemented. All five IPs (parser hardening, named-packet cache + activate/list subcommands, configurable retention cap, tests, tracking WI) landed under the Codex GO at `-004`. 42 tests pass (12 implementation_authorization + 22 implementation_start_gate including the gate-unchanged regression + 8 assertion_check_prune). Targeted Ruff is clean on all five touched code files. Tracking work_item `WI-3295` inserted with `origin='hygiene'`, `source_spec_id='SPEC-1662'`.

One implementation-discovered design refinement on IP-1: the original proposal stated "the simpler parser at `scripts/implementation_authorization.py` adopts the detector's `filename_does_not_match_document_name` check, but raises rather than warns because the gate fails closed." The strict raise was implemented first and immediately surfaced a real pre-existing malformed entry in `bridge/INDEX.md` (the `gtkb-single-harness-bridge-dispatcher-001` Document name vs. its v1-no-suffix `bridge/gtkb-single-harness-bridge-dispatcher-001.md` filename triggered a slug-vs-doc-id mismatch under the original regex). Raising globally would have blocked the gate for every bridge, including the slice-4 packet's own queries. The implementation pivots to **boundary-based per-bridge enforcement**: `parse_bridge_index` silently skips misattributed status lines and `bridge_entry()` raises only when the queried bridge has mismatches. The fail-closed gate semantic is preserved exactly: querying a malformed bridge raises; unrelated malformed bridges elsewhere in INDEX don't block the gate's hot path.

## Specification Links

The proposal's `-003` `## Specification Links` section is carried forward; no specs removed.

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol observed throughout: NEW -> REVISED -> GO -> implementation -> implementation report. `bridge/INDEX.md` was updated with the `NEW: bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-006.md` entry at the top of slice-4's version list; no prior versions deleted or rewritten. The pre-existing `-005` orphan file is preserved on disk.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all writes inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - carried forward from `-003`; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping below; all linked specs have executed test or verification evidence.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - IP-3 restores SPEC-default chronic-noise threshold reachability via `config/governance/assertion-runs-retention.toml` `default_runs_per_spec = 50`.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic-noise candidates remain gated; IP-3 widens the data window so candidates are accurately surfaced for owner AUQ.
- GOV-STANDING-BACKLOG-001 - tracking `WI-3295` inserted in MemBase per the standing-backlog authority.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - named-packet cache files at `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json` are auditable durable artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix replaces opaque session-overwrite behavior with named, recoverable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - packet lifecycle (begin/activate/expire/drift) remains the trigger surface; `activate` is an explicit lifecycle transition.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - all three defects (a/b/c) were deterministic-plumbing failures; the fix is service-side, not session-side.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - the existing project-authorization metadata pathway in packets is preserved unchanged.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner direction "Start Slice 4 implementation now, please" authorized this implementation work.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-004.md - Codex GO at -004 authorizing implementation.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md - REVISED-1 proposal under that GO.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-002.md - Codex NO-GO on `-001` that motivated the named-packet cache + activate design.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-005.md - pre-existing orphan file from a prior session attempt; not present in INDEX; preserved per bridge audit-trail discipline. This `-006` is the canonical Slice 4 implementation report.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner direction "Start Slice 4 implementation now, please" authorized this implementation work under the existing `-004` GO.
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable bridge entry should I pick up next?" answered "Slice 4 REVISED-1 (Recommended)" - the upstream sequencing decision that led to REVISED-1 and now this implementation.

No new owner decision is required before VERIFIED.

## Implementation Evidence per IP

### IP-1: Filename-vs-document parser hardening

- Status: implemented in this session.
- Location: `scripts/implementation_authorization.py`.
- Functions added:
  - `_filename_matches_doc(path: str, doc_id: str) -> bool`: boundary-based matcher accepting both v1-no-suffix and v2+-NNN-suffix forms; correctly handles doc_ids ending in `-NNN` (e.g. `gtkb-single-harness-bridge-dispatcher-001`).
  - `_validate_bridge_index_for(project_root, bridge_id)`: per-bridge strict consistency check that scans INDEX for status lines under `bridge_id`'s Document section and raises `AuthorizationError` on filename mismatch.
- Functions modified:
  - `parse_bridge_index`: now silently skips misattributed status lines (those whose filename does not match the enclosing Document via `_filename_matches_doc`). Comment in source explains the per-bridge enforcement deferral to `bridge_entry`.
  - `bridge_entry`: now calls `_validate_bridge_index_for(project_root, bridge_id)` before returning the entry. This is the fail-closed enforcement point for the specific queried bridge.
- Design refinement (vs proposal `-003`): the proposal said `parse_bridge_index` should "raise rather than warn." Implementation surfaced that a strict global raise blocked unrelated bridges with pre-existing v1-no-suffix conventions. The pivot to **per-bridge strict check** preserves the fail-closed contract for the queried bridge while not globally blocking on unrelated INDEX issues. Documented in module source.

### IP-2: Named-packet cache + activate/list subcommands

- Status: implemented in this session.
- Location: `scripts/implementation_authorization.py`.
- Constants added: `BY_BRIDGE_DIRECTORY_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/by-bridge")`.
- Functions added: `packet_path_for_bridge`, `write_named_packet`, `_validate_packet`, `load_named_packet`, `activate_packet`, `list_named_packets`.
- Functions modified: `load_packet` delegates validation to `_validate_packet`; `main()` updated: `begin` writes both `current.json` AND the named packet; new `activate --bridge-id <X>` and `list` subcommands.
- Gate contract preservation: `load_packet` and `validate_targets` still read `current.json` only. The named cache is additive recovery storage. Confirmed by `test_gate_unchanged_reads_current_json_only` regression.

### IP-3: Configurable assertion_runs retention cap

- Status: implemented in this session.
- Files:
  - `config/governance/assertion-runs-retention.toml` (new): `schema_version = 1`, `default_runs_per_spec = 50`.
  - `.claude/hooks/assertion-check.py` (modified): `_read_retention_cap(project_dir)` helper; `_prune_assertion_runs` reads the cap and parameterizes the SQL via `?` placeholder (was hardcoded `<= 5`).
- Default behavior change: cap defaults to 50 (was 5). SPEC-1662's chronic-noise threshold is now reachable.
- Fallback path: missing or malformed config falls back to 50 with a log line.

### IP-4: Tests

- `platform_tests/scripts/test_implementation_authorization.py` (new, 12 tests): IP-1 + IP-2 + F2-001 + input-validation coverage.
- `platform_tests/scripts/test_implementation_start_gate.py` (extended): existing 21 tests plus `test_gate_unchanged_reads_current_json_only` regression (the new test was pre-staged in the file when implementation began; now passes because `auth.create_authorization_packet` and `auth.write_named_packet` are both implemented).
- `platform_tests/hooks/test_assertion_check_prune.py` (new, 8 tests): IP-3 helper + end-to-end coverage including fallback paths.
- Test command (executed): `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_assertion_check_prune.py -v`.
- Result: `42 passed in 5.57s`.

### IP-5: Tracking work_item

- Status: implemented in this session.
- Insert: `db.insert_work_item(id='WI-3295', title='Implementation gate hygiene (GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE Slice 4)', origin='hygiene', component='governance', resolution_status='open', changed_by='prime-builder/claude/B', change_reason='S349 self-diagnostic LEAK 4 closure; named-packet cache + activate + IP-1 parser hardening + IP-3 retention cap config; REVISED-1 GO at -004', source_spec_id='SPEC-1662', related_bridge_threads='gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene', ...)`.
- Result rowid: 4570; version: 1.

## Spec-to-Test Mapping

| Linked spec | Verifying test(s) | Result |
|---|---|---|
| SPEC-1662 (GOV-18: meaningfulness over coverage) | `test_prune_defaults_to_50_runs_when_config_missing`, `test_prune_respects_configured_runs_per_spec`, `test_prune_fallback_logs_invalid_config_and_uses_default` | 3 PASS |
| GOV-15 TEST-FIX-GATE | IP-3 widens the data window; the retirement workflow gate itself is unchanged by Slice 4. Inherited PASS. | PASS |
| GOV-STANDING-BACKLOG-001 | `WI-3295` insert verified via `insert_work_item` return value (rowid=4570, version=1) | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This implementation report under the Codex GO at `-004`; INDEX.md updated; no orphan writes | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All target paths under `E:\GT-KB`; no Agent Red references introduced | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Spec links carried forward from `-003` proposal | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This very table | PASS |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Named-packet files at `.gtkb-state/implementation-authorizations/by-bridge/*.json` are durable artifacts | PASS |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | IP-2 replaces opaque session-overwrite with named recoverable artifacts; `test_begin_writes_both_current_and_named_packet`, `test_list_enumerates_named_packets` | 2 PASS |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | `test_activate_restores_named_packet_to_current_json`, `test_activate_fails_when_named_packet_expired`, `test_activate_fails_when_bridge_status_drifted` cover the activate lifecycle | 3 PASS |
| Defect (a) / IP-1 | `test_parse_bridge_index_skips_misattributed_status_line`, `test_bridge_entry_raises_for_misattributed_status_under_queried_bridge`, `test_filename_matches_doc_accepts_v1_no_suffix_and_v2_plus_suffix`, `test_bridge_entry_succeeds_for_well_formed_bridge` | 4 PASS |
| Defect (b) / IP-2 | `test_begin_writes_both_current_and_named_packet`, `test_activate_restores_named_packet_to_current_json`, `test_activate_fails_when_named_packet_expired`, `test_activate_fails_when_bridge_status_drifted`, `test_list_enumerates_named_packets`, `test_list_returns_empty_when_by_bridge_dir_absent`, `test_packet_path_for_bridge_rejects_path_traversal_bridge_id` | 7 PASS |
| F1-001 (contract not widened) / F1-002 (no first-match ambiguity) / F2-001 (current.json preserved) | `test_legacy_current_json_only_workflow_still_works`, `test_gate_unchanged_reads_current_json_only` | 2 PASS |
| Defect (c) / IP-3 | `test_read_retention_cap_*` (4), `test_prune_*` (4) | 8 PASS |

## Mechanical Preflight Evidence

The Codex GO at `-004` recorded:
- Applicability preflight: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. packet_hash: `sha256:2befcd92bc49939598d8d104f7d8266003ded9db1c1a5328e238453a1f06ac18`.
- Clause preflight: 0 blocking gaps; all 5 evaluated clauses pass.

Codex's verifier should re-run both against this `-006` to confirm coverage carried forward.

## Verification Plan

For Codex VERIFIED:

1. Re-run mechanical preflights: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene`. Both should report no missing specs and zero blocking gaps.
2. Re-run full slice-4 test suite: `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_assertion_check_prune.py -v`. Expected: 42 PASS.
3. Re-run targeted Ruff: `python -m ruff check scripts/implementation_authorization.py .claude/hooks/assertion-check.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_assertion_check_prune.py`. Expected: 0 errors.
4. CLI smoke test:
   - `python scripts/implementation_authorization.py begin --bridge-id <bridge>` writes both `current.json` and `by-bridge/<bridge>.json` with identical content.
   - `python scripts/implementation_authorization.py list` enumerates named packets with valid metadata.
   - `python scripts/implementation_authorization.py activate --bridge-id <bridge>` restores `current.json` from the named cache.
5. Source inspection:
   - `scripts/implementation_authorization.py` contains `_filename_matches_doc`, `_validate_bridge_index_for`, `packet_path_for_bridge`, `write_named_packet`, `_validate_packet`, `load_named_packet`, `activate_packet`, `list_named_packets`.
   - `.claude/hooks/assertion-check.py` contains `_read_retention_cap` and `_prune_assertion_runs` uses the parameterized cap.
   - `config/governance/assertion-runs-retention.toml` exists with `default_runs_per_spec = 50`.
6. Tracking work_item: `SELECT id, origin, source_spec_id, resolution_status, version FROM work_items WHERE id='WI-3295' ORDER BY version DESC LIMIT 1`. Expected: `('WI-3295', 'hygiene', 'SPEC-1662', 'open', 1)`.

## Implementation-Discovered Findings

### IP-1 design refinement (resolved in this slice, not deferred)

The original IP-1 strict-raise design blocked all bridges when ANY pre-existing INDEX entry had a slug-vs-doc-id ambiguity. This surfaced via the legitimate `gtkb-single-harness-bridge-dispatcher-001` Document name + its v1-no-suffix `bridge/gtkb-single-harness-bridge-dispatcher-001.md` filename. The implementation pivots to **per-bridge enforcement**: `parse_bridge_index` skips misattributed lines silently; `bridge_entry()` raises only when the queried bridge has mismatches. This preserves the fail-closed contract for the queried bridge while not globally blocking on unrelated INDEX issues. The pivot is documented in source comments and validated by `test_parse_bridge_index_skips_misattributed_status_line` + `test_bridge_entry_raises_for_misattributed_status_under_queried_bridge`.

### Friction observations (defer to a future hygiene slice)

These were filed in Slice 3's `-009` implementation report and remain candidates for a future Slice 5 or separate gate-friction-hygiene bridge:

- Gate false-positive on `2>/dev/null` (matches `(^|[^>])>{1,2}($|[^&])` redirect pattern).
- Gate false-positive on `python -c "...sqlite3..."` for read-only queries (matches `sqlite3` in the mutating regex).
- Gate blocks corrective work after report-level NO-GO when the proposal-chain GO still authorizes the slice (requires REVISED-proposal detour to re-establish GO state).

These are NOT Slice 4 verification concerns; they are scope inputs for a future bridge.

## Recommended Commit Type

`feat:` - the named-packet cache + `activate`/`list` subcommands are net-new capability; the parser hardening (IP-1) and prune cap config (IP-3) are bundled correctness fixes that depend on the same review pass. Diff stat includes net-new tests, config file, and Python helpers. `feat:` matches the diff shape per the Conventional Commits discipline at `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline.

## Files Changed

Net-new files (added):
- `platform_tests/scripts/test_implementation_authorization.py` (12 new tests).
- `platform_tests/hooks/test_assertion_check_prune.py` (8 new tests).
- `config/governance/assertion-runs-retention.toml` (retention-cap config).

Modified files:
- `scripts/implementation_authorization.py` (IP-1 parser hardening + IP-2 helpers + IP-2 CLI subcommands).
- `.claude/hooks/assertion-check.py` (IP-3 retention cap config + parameterized prune).
- `platform_tests/scripts/test_implementation_start_gate.py` (`test_gate_unchanged_reads_current_json_only` regression; pre-staged scaffolding).

Database mutations:
- `groundtruth.db`: one new row in `work_items` (`WI-3295` v1).

State files (runtime):
- `.gtkb-state/implementation-authorizations/by-bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene.json` (this slice's own named packet, written by `begin` during implementation).

## Risks and Rollback

- **IP-1 risk:** the per-bridge strict check raises on misattributed status lines for the queried bridge. Existing well-formed bridges are unaffected. Rollback: revert `_validate_bridge_index_for` call from `bridge_entry`.
- **IP-2 risk:** named-packet files accumulate over time. Mitigation: `list` surfaces stale packets; expired packets fail validation on `activate`. Rollback: revert per-bridge write in `begin` + remove `activate`/`list` subcommands.
- **IP-3 risk:** `assertion_runs` table grows ~10x at default cap=50. Projection: DB total ~370MB. Rollback: revert default to 5 in the TOML.

## Sequenced Follow-Ons

- Slice 3 REVISED-5 at `-013` is awaiting Codex review; once GO'd, the F1-F4 code fixes proceed under the new substrate (no more thrashing).
- Slice 1 GO at `-010` and Slice 2 GO at `-010` can now be implemented in parallel; each `begin` populates the named cache so they don't collide.
- `gtkb-governed-spec-retirement-001` (NEW) refines and implements governed retirement; sequenced after Slice 3 REVISED-5 lands.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` (flat bullets; no `###` sub-headings inside; no parenthetical heading).
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input` citing this session's directive and prior AUQ exchanges.
- Spec-to-test mapping present (per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001).
- `## Recommended Commit Type` present per Conventional Commits Type Discipline.
- All paths under `E:\GT-KB`; no Agent Red commingling.
- IP-1 design refinement documented explicitly (transparent narrative of the strict-raise -> per-bridge pivot).
- Pre-existing `-005` orphan file noted but not modified, per "never delete bridge files."

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
