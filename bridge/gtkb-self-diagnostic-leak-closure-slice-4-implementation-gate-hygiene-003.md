# Implementation Proposal REVISED-1 - Implementation Gate Hygiene (Self-Diagnostic Leak Closure Slice 4)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
Addresses: NO-GO at `bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-002.md` (F1-001 contract widening, F1-002 overlapping target paths, F2-001 current.json compatibility)
target_paths: ["scripts/implementation_authorization.py", ".claude/hooks/assertion-check.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/hooks/test_assertion_check_prune.py", "config/governance/assertion-runs-retention.toml", ".gtkb-state/implementation-authorizations/**", "groundtruth.db"]

## Claim

REVISED-1 of Slice 4 redesigns IP-2 to preserve the one-active-packet invariant the original `-001` proposal accidentally widened. The new design solves the auth-packet-thrashing problem without changing the gate's contract:

- **`current.json` remains the single deterministic gate input.** The gate code is unchanged; `load_packet()` and `validate_targets()` continue to read `current.json` exactly as before.
- **A named-packet cache at `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json` is additive.** Each `begin --bridge-id X` writes both the named packet AND `current.json` (identical content). When `current.json` is overwritten by another `begin --bridge-id Y`, the named packet for `X` survives at `by-bridge/X.json`.
- **A new `activate --bridge-id X` subcommand restores `current.json` from the named cache.** It validates the cached packet against live INDEX + expiry before activating. This is the explicit, deterministic recovery path that resolves Codex's F1-002 concern about overlapping target paths: only the activated bridge's packet authorizes writes; there is no first-match ambiguity.
- **No rule-file changes.** Because the contract (`one current authorization packet, scoped to one GO'd bridge proposal`) is preserved, the rule files at `.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md` remain accurate. F1-001 is resolved by removing the rule-conflicting widening.
- **F2-001 resolved explicitly.** `current.json` is kept as the active pointer, in its current location, with its current schema. All known consumers (`scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, `config/agent-control/system-interface-map.toml`, existing implementation-start-gate tests) work without modification.

IP-1 (filename-vs-document consistency check) and IP-3 (configurable `assertion_runs` retention cap) remain as in `-001` — Codex called them "directionally sound" and they were not blocked. IP-4 (tests) is updated to cover the new named-cache + activate semantics. IP-5 (tracking WI) is unchanged.

## Why Now

S349's parallel-slice work proved defect (b) (auth-packet thrashing) is a real blocker, not a theoretical concern. During this session alone, the cross-harness event-driven trigger spawned a Codex session that issued its own `begin --bridge-id gtkb-backlog-hygiene-bundle-s349` *twice* while Prime was implementing Slice 3 IPs, overwriting Prime's slice-3 packet and forcing two re-issues. Without the named-packet cache + activate path, every parallel slice implementation in S349 (and future multi-slice work) hits the same thrashing.

The REVISED-1 redesign preserves all the safety invariants Codex's NO-GO at `-002` defended. It does not widen the gate's contract; it only adds recovery storage. That's the smallest behavior change that closes the friction.

## Specification Links

The proposal's `-001` `## Specification Links` section is carried forward; no specs removed. Spec links reordered for readability; no semantic change.

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this slice files a REVISED proposal under the umbrella. `bridge/INDEX.md` updated with the `REVISED: bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-003.md` entry at the top of slice-4's version list; no prior versions deleted or rewritten.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan maps each defect and each Codex finding to a concrete spec-derived test.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - defect (c) affects reachability of the SPEC-default chronic-noise threshold; IP-3 fix restores SPEC-default behavior.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic_noise candidates require owner AUQ; defect (c) fix widens the data window so retirement candidates are accurately surfaced.
- GOV-STANDING-BACKLOG-001 - Slice 4 creates one tracking WI for its own implementation.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - named-packet cache files are auditable durable artifacts under `.gtkb-state/implementation-authorizations/by-bridge/`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix replaces opaque session-overwrite behavior with named, recoverable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - packet lifecycle (begin/activate/expire/drift) is the trigger surface; the new `activate` subcommand is an explicit lifecycle transition.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - all three defects (a/b/c) are deterministic-plumbing failures whose fix belongs in the service.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - Slice 4 preserves the existing project-authorization metadata pathway in packets unchanged.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-010.md - parallel Slice 1 currently in flight; defect (b) prevents simultaneous implementation.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-010.md - parallel Slice 2 currently in flight; same constraint.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Slice 3 GO that authorized the IPs implemented in this session; defect (b) manifested twice during that implementation.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-010.md - Codex NO-GO on Slice 3 implementation report; documents that auth-packet thrashing made implementation harder.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-002.md - Codex NO-GO on Slice 4 `-001`; this REVISED-1 addresses F1-001, F1-002, F2-001.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate - the rule defines the gate this slice repairs; the REVISED-1 design preserves the rule's wording (`current local authorization packet` scoped to `one GO'd bridge proposal`).
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata - the contract REVISED-1 preserves unchanged. No rule-file edits required.
- `.claude/rules/operating-model.md` §1 - "strongly biased toward durable artifacts, traceability, modular implementation" - named-packet cache honors this bias.
- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` - reference parser implementation containing the `filename_does_not_match_document_name` warning the gate parser lacks; IP-1 ports the check.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` - originating Loyal Opposition advisory.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable bridge entry should I pick up next?" answered "Slice 4 REVISED-1 (Recommended)" - authorizes this REVISED-1 filing.
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - GT-KB Self-Measurement and Self-Improvement Advisory.
- DELIB-1354 - Loyal Opposition Review - GTKB-BRIDGE-POLLER-001 Smart Bridge Trigger REVISED-3 (cited by Codex `-002`).
- DELIB-0873 - Loyal Opposition Review - Bridge Dispatcher Deferral Enforcement Scope (cited by Codex `-002`).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-001.md - the original proposal under review.
- bridge/gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene-002.md - Codex NO-GO addressed here.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner AskUserQuestion "Which actionable bridge entry should I pick up next?" — answer: "Slice 4 REVISED-1 (Recommended)". Authorizes filing REVISED-1 with the new IP-2 design.
- 2026-05-13 UTC, S349: owner AUQ "File both, sequenced" + "parallelize this work to the maximum extent possible" (carried forward as the original motivation for parallel-slice work).

No additional owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The three defects remain repairs to existing specifications, not new requirements:

- Defect (a) IP-1 fix aligns the gate parser's robustness with `GOV-FILE-BRIDGE-AUTHORITY-001` ("INDEX is canonical workflow state") and the existing detector implementation. No new behavior specified.
- Defect (b) IP-2 fix preserves the contract codified in `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata. The contract — one current authorization packet, scoped to one GO'd bridge proposal — is unchanged. The fix is purely additive storage (named cache) plus an explicit recovery subcommand (`activate`).
- Defect (c) IP-3 fix restores `SPEC-1662 (GOV-18)` default chronic-noise threshold reachability; it does not modify the SPEC.

No new requirement candidate is proposed.

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-1 is not a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662') at IP-5, identical in shape to the tracking WIs created by Slices 1, 2, and 3 of the same umbrella. No formal-artifact-approval packet is required because no protected narrative artifact is edited.

## Changes from -001

### IP-2 redesign (closes F1-001, F1-002, F2-001)

**Removed from -001:**

- `load_packet_for_path(project_root, target_path)` — first-matching-packet search across all current packets. Removed entirely.
- `validate_targets(project_root, targets)` first-match batch acceptance. Removed; `validate_targets` continues to read only `current.json` exactly as today.
- `packet_path_for_bridge(project_root, bridge_id)` as the primary packet path. Demoted to a helper for the named cache; `current.json` remains the primary.
- The "ambiguous overlapping target paths" concern (F1-002): structurally cannot occur in the new design because only one packet is active at a time.
- The contract-widening claim (F1-001): the contract is not widened; rule-file changes therefore not required.

**Added in REVISED-1:**

- Named-packet cache at `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json`. Each `begin --bridge-id X` writes both this named file AND `current.json` (identical content). The named cache survives overwrite by a subsequent `begin --bridge-id Y`.
- New CLI subcommand `activate --bridge-id X`: reads `by-bridge/<X>.json`, validates schema, validates expiry, validates `bridge_entry(X).latest_status == "GO"`, validates `bridge_entry(X).latest_path == packet.go_file` (drift check), and writes the validated packet to `current.json`. This is the explicit, deterministic recovery path when a session's packet was overwritten.
- New CLI subcommand `list`: enumerates current named packets at `by-bridge/` with `(bridge_id, expires_at, target_path_globs, valid_against_index)` for owner visibility.
- `current.json` schema unchanged. `current.json` location unchanged. Known consumers (`config/agent-control/system-interface-map.toml`, `scripts/implementation_authorization.py`, `scripts/implementation_start_gate.py`, existing implementation-start-gate tests) keep working without modification — this resolves F2-001 explicitly.

**Preserved from -001:**

- IP-1 filename-vs-document consistency check in `parse_bridge_index` (the simpler parser at `scripts/implementation_authorization.py` adopts the detector's `filename_does_not_match_document_name` check, but raises rather than warns because the gate fails closed).
- IP-3 configurable `assertion_runs` retention cap at `config/governance/assertion-runs-retention.toml`; default 50 (SPEC-1662 reachable).
- IP-4 tests (updated to reflect the REVISED-1 IP-2 design; see below).
- IP-5 tracking work_item insert (one row, `WI-NNNN`, origin='hygiene', source_spec_id='SPEC-1662'). Tracking-WI insertion remains the only authoritative MemBase mutation in scope.

### IP-1 unchanged from -001

(Filename-vs-document consistency check; see `-001` for detail.)

### IP-3 unchanged from -001

(Configurable retention cap with default 50; see `-001` for detail. Storage impact projection unchanged.)

### IP-4 tests (updated for new IP-2 design)

- `platform_tests/scripts/test_implementation_authorization.py`:
  - `test_parse_bridge_index_rejects_misattributed_status_line` — IP-1 coverage (unchanged from `-001`).
  - `test_begin_writes_both_current_and_named_packet` — REVISED IP-2: assert `begin --bridge-id X` writes `current.json` AND `by-bridge/X.json` with identical content.
  - `test_activate_restores_named_packet_to_current_json` — assert `activate --bridge-id X` overwrites `current.json` with the named cache content when the named cache is valid.
  - `test_activate_fails_when_named_packet_expired` — assert expired named packet raises and does not modify `current.json`.
  - `test_activate_fails_when_bridge_status_drifted` — assert that if bridge X's latest status is no longer GO, activate fails and `current.json` is unchanged.
  - `test_list_enumerates_named_packets` — assert `list` returns one entry per named packet with valid metadata.
  - `test_legacy_current_json_only_workflow_still_works` — F2-001 regression: a session that calls only `begin` (no `activate`) gets the same behavior as today.
- `platform_tests/scripts/test_implementation_start_gate.py`:
  - `test_gate_unchanged_reads_current_json_only` — REVISED-1 explicit: the gate reads `current.json`, never `by-bridge/`.
- `platform_tests/hooks/test_assertion_check_prune.py`:
  - Unchanged from `-001` (IP-3 coverage).

### IP-5 unchanged from -001

(One tracking work_item inserted; see `-001` for detail.)

## Proposed Scope

### IP-1: Filename-vs-document consistency check (unchanged from -001)

Modify `scripts/implementation_authorization.py::parse_bridge_index` to validate each status line's referenced filename against the currently-open `Document:` name. On mismatch, raise `AuthorizationError("Bridge INDEX status line filename does not match enclosing Document: <name>; refusing to authorize")`.

### IP-2: Named-packet cache + activate subcommand (REVISED design)

1. Introduce `packet_path_for_bridge(project_root, bridge_id) -> Path` returning `.gtkb-state/implementation-authorizations/by-bridge/<bridge-id>.json`. Helper only; not the primary packet path.
2. `create_authorization_packet` returns the packet dict (unchanged).
3. `begin --bridge-id X` workflow:
   - Compute the packet via `create_authorization_packet` (no change).
   - Write to `by-bridge/X.json` (new).
   - Write to `current.json` (preserved; identical content).
   - Print the packet (unchanged output).
4. New subcommand `activate --bridge-id X`:
   - Read `by-bridge/X.json`.
   - Validate schema, hash, expiry exactly as `load_packet` does today.
   - Validate `bridge_entry(X).latest_status == "GO"` and `bridge_entry(X).latest_path == packet.go_file` (drift check).
   - On success: write the packet to `current.json`; print the activated packet.
   - On failure: raise `AuthorizationError` with the specific reason; do NOT modify `current.json`.
5. New subcommand `list`:
   - Enumerate `by-bridge/*.json` files.
   - For each: read, validate schema, report `(bridge_id, expires_at, target_path_globs, named_packet_valid, would_activate_succeed)`.
   - Output as JSON for owner visibility.
6. The gate code at `scripts/implementation_start_gate.py` is UNCHANGED. `validate_targets` continues to read `current.json` only.
7. `load_packet` is UNCHANGED. The drift detection on `current.json` works exactly as today.

Rationale: this is the minimum behavior change that unblocks parallel slices. The gate's contract is preserved. Overlapping target paths (F1-002) are no longer ambiguous because only one packet is active at a time — the choice of "which slice authorizes this write" is made explicitly by `activate`, not implicitly by the gate.

### IP-3: Configurable assertion_runs retention cap (unchanged from -001)

Modify `.claude/hooks/assertion-check.py::_prune_assertion_runs` to read from `config/governance/assertion-runs-retention.toml`. Default `default_runs_per_spec=50` (SPEC-1662 reachable). Fallback to default 50 on missing or malformed config with a log line.

### IP-4: Tests (updated for REVISED IP-2 design)

As enumerated in § Changes from -001 IP-4 above. Each test maps to an observable behavior of the named-packet cache + activate subcommand or the unchanged gate contract.

### IP-5: Tracking work_item

Insert one `work_items` row via `db.insert_work_item()`:

- `id`: `WI-NNNN` (assigned at insert time)
- `origin='hygiene'`
- `source_spec_id='SPEC-1662'`
- `title='Implementation gate hygiene fixes (GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE Slice 4)'`
- `related_bridge_threads='gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene'`
- `changed_by='prime-builder/claude/B'`
- `change_reason='S349 self-diagnostic LEAK 4 closure; defects a/b/c discovered during parallel Slice 1/2/3 implementation; REVISED-1 owner AUQ authorizes named-packet cache + activate design'`

## Tests

Per § IP-4 above. Each defect or finding maps to a named test that asserts the fix as observable behavior:

- Defect (a) → `test_parse_bridge_index_rejects_misattributed_status_line`.
- Defect (b) → `test_begin_writes_both_current_and_named_packet`, `test_activate_restores_named_packet_to_current_json`, `test_activate_fails_when_named_packet_expired`, `test_activate_fails_when_bridge_status_drifted`, `test_list_enumerates_named_packets`.
- F1-001 (contract not widened) → `test_legacy_current_json_only_workflow_still_works`.
- F1-002 (no first-match ambiguity) → `test_gate_unchanged_reads_current_json_only` plus the absence of any `load_packet_for_path` function (negative regression).
- F2-001 (current.json preserved) → `test_legacy_current_json_only_workflow_still_works` + manual verification that the known consumers list (`system-interface-map.toml`, etc.) is unmodified.
- Defect (c) → `test_prune_defaults_to_50_runs_when_config_missing`, `test_prune_respects_configured_runs_per_spec`, `test_prune_fallback_logs_invalid_config_and_uses_default`.

## Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_assertion_check_prune.py -v` - all new tests PASS.
2. `python scripts/implementation_authorization.py begin --bridge-id <any-bridge>` - verify both `current.json` AND `by-bridge/<bridge-id>.json` written with identical hashes.
3. `python scripts/implementation_authorization.py begin --bridge-id <bridge-A>; python scripts/implementation_authorization.py begin --bridge-id <bridge-B>; python scripts/implementation_authorization.py activate --bridge-id <bridge-A>` - verify `current.json` flips to bridge-A's content after activate, and that `by-bridge/<bridge-B>.json` is unaffected.
4. `python scripts/implementation_authorization.py list` - verify both named packets enumerated.
5. End-to-end parallel-slice simulation: two Prime sessions issuing `begin` for different bridges; one session uses `activate` to restore its packet; the other proceeds independently. Documented in the post-implementation report.
6. Sample `assertion_runs` table inspection: count rows per spec_id after one prune run; assert max(count_per_spec_id) <= configured cap.
7. Tracking work_item exists in MemBase with the documented origin and source_spec_id.
8. Carry forward applicability and clause preflight evidence from this proposal's verdict.

## Risks and Rollback

- **IP-1 risk (parser hardening):** the gate becomes stricter. Existing INDEX files with malformed status lines now fail closed. Mitigation: pre-flight grep current INDEX for misattributed lines before landing. Rollback: revert the consistency check.
- **IP-2 risk (named cache):** the `by-bridge/` directory accumulates files over time. Mitigation: named packets respect existing `expires_at` and are cleaned by the existing expiration check on `activate`; `list` surfaces stale packets for explicit cleanup. Rollback: delete the `by-bridge/` directory and revert `activate`/`list` subcommands; `current.json`-only behavior is preserved as the unchanged default.
- **IP-2 risk (drift between current.json and named cache):** if a session writes only `current.json` (e.g., via direct mutation, not through `begin`), the named cache won't reflect that. Mitigation: `begin` is the only sanctioned write path; ad-hoc current.json edits are out of scope. Rollback: documentation note in the rule files saying `current.json` is owned by `begin`/`activate` only.
- **IP-3 risk:** `assertion_runs` table grows ~10x. Projection still ~370MB DB. Rollback: revert default to 5.
- **General rollback:** all changes isolated to named files in `target_paths`. No schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking WI.

## Recommended Commit Type

`feat:` - the named-packet cache + activate subcommand is the net-new capability; the parser hardening and prune cap config are bundled fixes. Diff stat will be net-new test files + scripts/.claude/hooks edits. `feat:` matches the diff shape.

## Sequenced Follow-Ons

- After VERIFIED, re-issue Slice 1, Slice 2, Slice 3 auth packets via the new `begin` (which writes both current.json + named cache); any work resumed under those GOs operates with the new recovery substrate.
- The implementation-discovered friction this session (gate false-positives on `2>/dev/null` redirect, gate false-positives on `python -c "...sqlite3..."` reads, gate blocks corrective work after report-level NO-GO when proposal-chain GO still authorizes the slice) is documented as scope inputs for a future Slice 5 or for a separate gate-friction-hygiene bridge. NOT in scope for REVISED-1.

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with flat bullets and no `###` sub-headings inside; no parenthetical heading.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the owner AskUserQuestion exchange.
- `target_paths` consistent with all writes; no protected narrative artifacts touched.
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- `## Clause Scope Clarification (Not a Bulk Operation)` section to pre-empt GOV-STANDING-BACKLOG-001 false-positive.
- All paths under `E:\GT-KB`; no Agent Red references.
- explicit `Changes from -001` section.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
