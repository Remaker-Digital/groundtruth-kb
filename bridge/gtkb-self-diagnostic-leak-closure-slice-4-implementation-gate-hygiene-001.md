# Implementation Proposal - Implementation Gate Hygiene (Self-Diagnostic Leak Closure Slice 4)

bridge_kind: implementation_proposal
Document: gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S349 (continuation)
target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", ".claude/hooks/assertion-check.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/hooks/test_assertion_check_prune.py", "config/governance/assertion-runs-retention.toml", ".gtkb-state/implementation-authorizations/**", "groundtruth.db"]

## Claim

Slice 4 of the GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE umbrella closes three implementation-discovered defects surfaced during S349 parallel-slice implementation of Slices 1, 2, 3. The defects are:

- **(a) Implementation-start-gate INDEX-parser silently absorbs misattributed status lines.** The simpler parser in `scripts/implementation_authorization.py` accepts any `(NEW|REVISED|GO|NO-GO|VERIFIED): bridge/<file>.md` line under the currently-open `Document:` block without checking that `<file>` corresponds to the document name. The more rigorous `groundtruth_kb.bridge.detector.parse_index` parser emits a `filename_does_not_match_document_name` warning for the same input. The asymmetry makes the gate's `entry.latest_status` lookup vulnerable to a misplaced status line being misattributed to the active bridge.
- **(b) Auth-packet thrashing under parallel slices.** `scripts/implementation_authorization.py` uses a single fixed packet path `.gtkb-state/implementation-authorizations/current.json`. Each `begin --bridge-id <X>` overwrites the prior packet. Two slices implemented in parallel cannot both hold authorization; the last `begin` wins and the other slice's writes get blocked by the gate. Empirical evidence: at the start of this session, `current.json` referenced `gtkb-backlog-hygiene-bundle-s349`, not the in-flight `gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage` packet, even though Slice 3 work was unfinished.
- **(c) `assertion_runs` history cap of 5 makes SPEC-1662 chronic-noise threshold unreachable.** `.claude/hooks/assertion-check.py` lines 477-509 prune `assertion_runs` to the latest 5 rows per `spec_id` per session. The Slice 3 SPEC defines `chronic_noise` as "50+ consecutive FAIL runs" (configurable). With a hard 5-row ceiling, the SPEC's default chronic-noise classification is unreachable; Slice 3 IP-1 worked around this by defaulting `--chronic-threshold=5`, but the underlying retention policy still prevents the SPEC's stated default from operating as documented.

Defects (a) and (b) directly block parallel Slice 1/2/3 implementation. Defect (c) does not block implementation but narrows the SPEC-1662 chronic-noise signal to a 5-run window rather than the SPEC-default 50-run window.

The slice creates one MemBase `work_item` to track its own implementation (`origin='hygiene'`, `source_spec_id='SPEC-1662'`); `groundtruth.db` is included in `target_paths` to authorize that single mutation. All other writes are to source code, tests, hook code, configuration, and `.gtkb-state/` runtime data.

## Why Now

S349's parallel-slice implementation directive (owner: "parallelize this work to the maximum extent possible") exposed defects (a) and (b) as direct blockers within hours. The current session opened with a misattributed auth packet, confirming the issue is not theoretical. Defect (c) is the smallest of the three but is bundled because it shares the same Slice 3 spec lineage and benefits from a single review pass.

DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE is the relevant governance lens: each of these defects is deterministic plumbing whose failure surfaces as repeated owner-visible friction. The fixes belong in the services that emit the failures, not in per-session workarounds.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; this slice files a proposal under the umbrella before any implementation.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths inside `E:\GT-KB`; no Agent Red commingling.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section cites every governing specification; no placeholder text.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan maps each defect (a/b/c) to a concrete spec-derived test.
- SPEC-1662 (GOV-18: Assertion Quality Standard - meaningfulness over coverage) - defect (c) directly affects whether the SPEC's chronic-noise threshold is reachable; the fix restores SPEC-default behavior.
- GOV-15 TEST-FIX-GATE - retirement decisions for chronic_noise candidates require owner AUQ; defect (c) fix preserves the gate by widening the data window so retirement candidates are accurately surfaced.
- GOV-STANDING-BACKLOG-001 - Slice 4 creates one tracking WI for its own implementation; standing-backlog authority observed.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - per-bridge packets (defect b fix) preserve the same auditable artifact shape; only the file naming changes.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix replaces an opaque single-packet state with named-per-bridge artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - packet lifecycle (begin/expire/drift) remains the trigger surface; defect (b) widens it from one-active to one-per-bridge-active.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - all three defects are deterministic-plumbing failures whose fix belongs in the service, not the session.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION - Slice 4 does not propose new project authorizations; it preserves the existing project-authorization metadata pathway in packets.
- bridge/gtkb-self-diagnostic-leak-closure-slice-1-advisory-router-010.md - parallel Slice 1 currently in flight; defect (b) prevents simultaneous implementation with Slice 3.
- bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-010.md - parallel Slice 2 currently in flight; same constraint.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Slice 3 (active GO); defect (c) is documented in `scripts/assertion_categorize.py` lines 23-29 of that slice's implementation, and IP-1 already defaulted around the 5-run cap.

Advisory / cross-cutting:

- `.claude/rules/codex-review-gate.md` § Mechanical Implementation-Start Gate - the rule defines the gate that this slice repairs.
- `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata - the contract defect (b) widens.
- `.claude/rules/operating-model.md` §1 - "GT-KB is strongly biased toward durable artifacts, traceability, modular implementation" - per-bridge packets honor this bias more directly than a single shared current.json.
- `groundtruth-kb/src/groundtruth_kb/bridge/detector.py` - reference parser implementation containing the `filename_does_not_match_document_name` warning the gate parser lacks.
- `INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM.md` - originating Loyal Opposition advisory.

## Prior Deliberations

- S349 self-diagnostic investigation (this conversation, 2026-05-14 UTC).
- INSIGHTS-2026-05-10-13-26-GTKB-SELF-MEASUREMENT-SYSTEM (Codex LO advisory, 2026-05-10).
- DELIB-1469 - GT-KB Self-Measurement Advisory.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE.
- DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-008.md - Slice 3 GO; defect (c) documented in IP-1 commentary.
- bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md - the proposal under that GO.

## Owner Decisions / Input

- 2026-05-14 UTC, S349 continuation: owner direction in chat - "If those blockers can't be resolved quickly, file a small hygiene bridge for them as Slice 4 of the umbrella, then continue implementation under the existing Slice 3 GO." This proposal is the direct fulfillment of that direction. No new AskUserQuestion is required to file the proposal; subsequent owner approval gates (per-artifact narrative-artifact-approval packets, etc.) are not triggered because the slice does not edit protected narrative artifacts.

## Requirement Sufficiency

Existing requirements sufficient.

The three defects are repairs to existing specifications, not new requirements:

- Defect (a) is a fix to align the gate parser's robustness with `GOV-FILE-BRIDGE-AUTHORITY-001` ("INDEX is canonical workflow state") and the existing detector implementation; no new behavior is specified.
- Defect (b) widens the same auth-packet contract codified in `.claude/rules/file-bridge-protocol.md` § Mandatory Implementation-Start Authorization Metadata from one-active-packet to one-active-packet-per-bridge. The fields, hash discipline, and validation invariants remain unchanged.
- Defect (c) restores `SPEC-1662 (GOV-18)` default chronic-noise threshold reachability; it does not modify the SPEC.

No new requirement candidate is proposed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk operation against the standing backlog. It creates exactly one tracking `work_item` (origin='hygiene', source_spec_id='SPEC-1662') at IP-7, identical in shape to the tracking WIs created by Slices 1, 2, and 3 of the same umbrella. The inventory of fixes is itemized (a/b/c) for review clarity, not for bulk standing-backlog manipulation. No formal-artifact-approval packet is required because no protected narrative artifact is edited.

## Current Implementation Baseline

- `scripts/implementation_authorization.py`:
  - `DEFAULT_PACKET_RELATIVE_PATH = Path(".gtkb-state/implementation-authorizations/current.json")` (line 22).
  - `packet_path(project_root)` returns the single fixed path.
  - `parse_bridge_index` accepts any `^(NEW|REVISED|GO|NO-GO|VERIFIED): bridge/.+\.md$` line under the currently-open `Document:` block; no filename-vs-document-name check.
- `scripts/implementation_start_gate.py` delegates `load_packet` and `validate_targets` to `implementation_authorization`; the gate inherits both defects.
- `.claude/hooks/assertion-check.py` `_prune_assertion_runs` (lines 477-509) hard-codes `rn <= 5` partition cap; no env-var or config-file override.
- `groundtruth_kb.bridge.detector.parse_index` (groundtruth-kb/src/groundtruth_kb/bridge/detector.py:105+) is a known-good reference implementation that already emits `filename_does_not_match_document_name` warnings; its state-machine layout differs and includes blank-line/comment-block flushing.

## Proposed Scope

### IP-1: Filename-vs-document consistency check in the gate INDEX parser

Modify `scripts/implementation_authorization.py::parse_bridge_index` to validate each status line's referenced filename against the currently-open `Document:` name. The check matches the reference detector's existing logic:

1. Extract the kebab-case slug from `bridge/<slug>-<version>.md` in the status line.
2. Compare the slug to `current_id`.
3. On mismatch, raise `AuthorizationError("Bridge INDEX status line filename does not match enclosing Document: <name>; refusing to authorize")` rather than silently appending the version to the wrong document's list.

Rationale: the gate's authority depends on `entry.latest_status` being correct. A misplaced status line silently absorbed into the wrong document corrupts that authority. Failing closed is correct gate behavior.

Edge case: the detector emits a `ParseWarning` rather than a hard error. The gate is stricter because its consumers are write-protected paths; a warning that gets ignored is the existing failure mode.

### IP-2: Per-bridge auth packets

Modify `scripts/implementation_authorization.py` to support per-bridge packet files:

1. Introduce `packet_path_for_bridge(project_root, bridge_id) -> Path` returning `.gtkb-state/implementation-authorizations/<bridge-id>.json`. The bridge-id is path-safe by construction (kebab-case slugs are filesystem-safe across Windows/POSIX).
2. `create_authorization_packet` (no behavioral change to the packet content) writes to the per-bridge path via `write_packet(project_root, packet, bridge_id)`.
3. Preserve `current.json` as a convenience symlink/copy pointing at the most recently created packet for backward compatibility with any tools that read it directly (verify by grep first; if no consumer remains, drop the symlink).
4. Add `load_packet_for_path(project_root, target_path) -> dict` that:
   - Lists all `.gtkb-state/implementation-authorizations/*.json` files.
   - For each, validates schema and hash; skip corrupt or expired.
   - Returns the first packet whose `target_path_globs` cover the requested target.
   - Raises `AuthorizationError` if no packet authorizes the target.
5. `validate_targets(project_root, targets)` uses `load_packet_for_path` for each target individually, so multi-file batch writes are accepted as long as every file is authorized by some current packet.
6. `begin --bridge-id <X>` writes the per-bridge packet and prints its path; the existing `--no-write` flag still works.
7. Add `python scripts/implementation_authorization.py list` subcommand to enumerate active packets and their `(bridge_id, expires_at, target_path_globs)` for owner visibility.

Rationale: this is the minimum behavior change that unblocks parallel slices while preserving the gate's hash, expiry, drift, and project-authorization invariants. Each packet is still bound to one bridge document; the gate still fails closed on drift; only the index lookup widens.

### IP-3: Configurable `assertion_runs` retention cap

Modify `.claude/hooks/assertion-check.py::_prune_assertion_runs` to read a configurable cap:

1. Introduce `config/governance/assertion-runs-retention.toml` with two fields:
   - `default_runs_per_spec` (int, default 50; matches SPEC-1662 chronic-noise threshold).
   - `override_runs_per_spec_by_category` (dict, optional; reserved for future per-category overrides; empty in this slice).
2. `_prune_assertion_runs` reads the config file at hook-execution time; falls back to the new default of 50 if the file is missing or malformed; emits a hook-log line noting the effective cap.
3. The SQL preserves the same `ROW_NUMBER() OVER (PARTITION BY spec_id ORDER BY run_at DESC)` shape; only the `rn <= <cap>` literal is parameterized.
4. Update the docstring at line 478-484 to cite the new config path and the SPEC-1662 chronic-noise threshold rationale.

Storage impact note: at the prior 5-run cap, the table is ~30MB. At 50 runs, projected size is ~10x = ~300MB. This is acceptable within the 92MB-base DB context: total DB size with 50-run cap is projected at ~370MB, still well under any local-disk constraint. The verification plan asserts the 10x growth ceiling explicitly.

### IP-4: Tests

Add three test files:

- `platform_tests/scripts/test_implementation_authorization.py` (extend if exists):
  - `test_parse_bridge_index_rejects_misattributed_status_line` - constructs an INDEX text fixture with a `Document: foo` block containing a `GO: bridge/bar-001.md` line; asserts `AuthorizationError` is raised. Covers IP-1.
  - `test_per_bridge_packet_path_returns_named_file` - asserts `packet_path_for_bridge(root, "test-bridge")` returns `.../<root>/.gtkb-state/implementation-authorizations/test-bridge.json`. Covers IP-2.
  - `test_load_packet_for_path_returns_first_authorizing_packet` - writes two packets with disjoint `target_path_globs`; asserts each target finds its packet. Covers IP-2.
  - `test_validate_targets_accepts_multiple_packets_in_batch` - mixed batch of authorized targets across two packets; asserts all accepted. Covers IP-2.
  - `test_packet_drift_detection_per_bridge` - writes packet for bridge A, simulates A's INDEX drift to NO-GO, asserts `load_packet_for_path` raises. Covers IP-2 invariant preservation.

- `platform_tests/scripts/test_implementation_start_gate.py` (extend if exists):
  - `test_gate_authorizes_target_via_per_bridge_packet` - simulates a Write to a slice-3 target with a slice-3 per-bridge packet present and a slice-1 per-bridge packet also present; asserts the write is permitted. Covers IP-2 end-to-end.

- `platform_tests/hooks/test_assertion_check_prune.py` (new):
  - `test_prune_defaults_to_50_runs_when_config_missing` - removes config file, runs prune against a 100-row fixture for one spec_id; asserts 50 rows retained. Covers IP-3.
  - `test_prune_respects_configured_runs_per_spec` - writes config with `default_runs_per_spec=10`; asserts 10 rows retained. Covers IP-3.
  - `test_prune_fallback_logs_invalid_config_and_uses_default` - writes malformed TOML; asserts prune still runs with default 50 and emits a fallback log line. Covers IP-3 robustness.

### IP-5: Tracking work_item

Insert one `work_items` row via `db.insert_work_item()`:

- `origin='hygiene'`
- `source_spec_id='SPEC-1662'`
- `title='Implementation gate hygiene fixes (GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE Slice 4)'`
- `related_bridge_threads='gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene'`
- `changed_by='prime-builder/claude/B'`
- `change_reason='S349 self-diagnostic LEAK 4 closure; defects a/b/c discovered during parallel Slice 1/2/3 implementation; owner-authorized hygiene slice'`

This WI documents the slice's implementation lineage in the canonical backlog for cross-session traceability and is the only authoritative MemBase mutation in scope.

## Tests

Per § Proposed Scope IP-4. Each defect maps to a named test that asserts the fix as observable behavior:

- Defect (a) → `test_parse_bridge_index_rejects_misattributed_status_line`.
- Defect (b) → `test_per_bridge_packet_path_returns_named_file`, `test_load_packet_for_path_returns_first_authorizing_packet`, `test_validate_targets_accepts_multiple_packets_in_batch`, `test_packet_drift_detection_per_bridge`, `test_gate_authorizes_target_via_per_bridge_packet`.
- Defect (c) → `test_prune_defaults_to_50_runs_when_config_missing`, `test_prune_respects_configured_runs_per_spec`, `test_prune_fallback_logs_invalid_config_and_uses_default`.

## Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/hooks/test_assertion_check_prune.py -v` - all eight new tests PASS.
2. `python scripts/implementation_authorization.py list` - lists the active per-bridge packets with `(bridge_id, expires_at, target_path_globs)`.
3. `python scripts/implementation_authorization.py begin --bridge-id gtkb-self-diagnostic-leak-closure-slice-4-implementation-gate-hygiene --no-write` - prints a valid packet for this slice; hash verifies.
4. Functional regression: end-to-end simulation of two concurrent slices holding packets simultaneously, with file writes to each slice's `target_paths`, both succeed. Documented in the post-implementation report.
5. Sample `assertion_runs` table inspection: count rows per spec_id after one prune run; assert max(count_per_spec_id) <= configured cap.
6. Tracking work_item exists in MemBase with the documented origin and source_spec_id.
7. Carry forward applicability and clause preflight evidence from this proposal's verdict.

## Risks and Rollback

- **Defect (a) fix risk:** the gate parser becomes stricter. Existing INDEX files with malformed status lines (filename does not match enclosing Document:) will newly raise `AuthorizationError` during gate evaluation. Mitigation: pre-flight grep the current INDEX for misattributed lines before landing; the bridge-compliance-gate hook can be extended in a follow-on to refuse Writes that would create misattributed lines. Rollback: revert the consistency check.
- **Defect (b) fix risk:** per-bridge packet files accumulate over time. Mitigation: packets respect existing `expires_at` and are cleaned by the existing expiration check on read; `list` subcommand surfaces stale packets for explicit cleanup. Rollback: revert per-bridge writes and restore `current.json`-only behavior; existing tests continue to pass under either model.
- **Defect (c) fix risk:** `assertion_runs` table grows to ~10x current size (5 → 50 rows per spec). Verified-safe magnitude (projection 300MB total). Rollback: revert default to 5; the config-file override remains useful for future tuning.
- **General rollback:** all three changes are isolated to the named files in `target_paths`. No schema migrations, no protected-narrative-artifact edits, no MemBase mutations beyond the one tracking WI.

## Recommended Commit Type

`feat:` - per-bridge auth packets (IP-2) is the net-new capability; the parser hardening (IP-1) and prune cap config (IP-3) are bundled fixes that depend on the same review pass. Diff stat will be net-new test files plus targeted scripts/hooks edits; `feat:` matches the diff shape per the Conventional-Commits discipline.

## Sequenced Follow-Ons

- After VERIFIED, re-issue Slice 1, Slice 2, Slice 3 auth packets via the new per-bridge mechanism so any work resumed under those GOs operates with the corrected gate.
- Consider an optional bridge-compliance-gate Write-time check that refuses to land a `bridge/INDEX.md` edit introducing a misattributed status line (separate proposal; not in scope for Slice 4).

## Bridge-Compliance Self-Check

- non-empty `## Specification Links` with flat bullets and no `###` sub-headings inside.
- non-empty `## Prior Deliberations`.
- non-empty `## Owner Decisions / Input` citing the owner direction in this session.
- `target_paths` consistent with all writes (including `groundtruth.db` for the IP-5 tracking WI and `.gtkb-state/implementation-authorizations/**` for the per-bridge packet directory).
- `## Requirement Sufficiency` with exactly one operative state.
- `## Recommended Commit Type`.
- `## Clause Scope Clarification (Not a Bulk Operation)` section to prevent GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS false-positive.
- All paths under `E:\GT-KB`; no Agent Red or out-of-root references.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
