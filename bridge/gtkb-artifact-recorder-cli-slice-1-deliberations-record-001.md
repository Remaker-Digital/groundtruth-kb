NEW

# Implementation Proposal (Slice 1) — `gt deliberations record` CLI Surface

**Document:** `gtkb-artifact-recorder-cli-slice-1-deliberations-record`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Session:** S342
**Bridge kind:** implementation_proposal
**Slice:** 1 (of 6 under the `gtkb-artifact-recorder-cli` umbrella; first concrete implementation slice after Slice 0 scoping VERIFIED at `bridge/gtkb-artifact-recorder-cli-004.md`)
**Parent thread:** `gtkb-artifact-recorder-cli` (scoping GO at `-004`, derived from REVISED-2 at `-003`).

## Claim

This Slice 1 proposal adds `gt deliberations record` as a new subcommand of the existing `gt deliberations` CLI group, implementing the first concrete manifestation of the Deterministic Services Principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`) for Deliberation Archive inserts. The subcommand accepts structured AUQ evidence as inputs, deterministically constructs the formal-artifact-approval packet, sets the `GTKB_FORMAL_APPROVAL_PACKET` env var, and invokes `KnowledgeDB.insert_deliberation()` such that the existing `formal-artifact-approval-gate.py` PreToolUse hook validates the packet at write time (defense-in-depth preserved).

The net AI-surface reduction is the load-bearing win: today, recording a deliberation requires ~150 LOC of orchestration (compute packet dict, write JSON file, compute SHA-256, set env var, invoke `gt deliberations add` with 10+ flags, handle ChromaDB indexing on success). Slice 1 reduces this to a single CLI invocation with 6-8 structured arguments. The cryptographic content-hash binding between packet and stored content remains intact because the CLI computes both deterministically from the same input bytes.

Slice 1 explicitly does NOT replace `gt deliberations add` or `gt deliberations upsert`; those surfaces remain for direct API access. `record` is the new high-level surface intended for owner-approved AUQ-driven deliberation recording.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `DELIB-0874`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/gtkb-artifact-recorder-cli-003.md` (parent Slice 0 proposal)
- `bridge/gtkb-artifact-recorder-cli-004.md` (parent Slice 0 GO)

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner decision, load-bearing): establishes the active-pursuit mandate for plumbing-to-service work and names `GTKB-ARTIFACT-RECORDER-CLI` as the first concrete manifestation. Slice 1 is the first manifestation of THAT manifestation.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE` (2026-04-27 S312): the original ~150 LOC orchestration friction surface that motivated this entire umbrella.
- `DELIB-0874`: artifact-oriented governance broader framing.
- `DELIB-0835`: formal-artifact approval / audit-trail owner decision; directly constrains approval-packet behavior the CLI must preserve.
- `DELIB-0687`: VERIFIED credential-scan narrowing — relevant because the CLI's packet-write surface must not introduce new credential-exposure pathways.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`: lifted the freeze that previously blocked this thread.
- Slice 0 GO at `bridge/gtkb-artifact-recorder-cli-004.md` (Codex VERIFIED): authorizes filing this per-slice proposal.

## Owner Decisions / Input

This Slice 1 proposal depends on the following owner authorizations:

1. **Owner approval at S312 (2026-04-27)** captured at `memory/work_list.md` row 113. Authorizes the GTKB-ARTIFACT-RECORDER-CLI work as the named first manifestation of `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
2. **Slice 0 scoping GO** at `bridge/gtkb-artifact-recorder-cli-004.md` (2026-05-11): authorizes filing per-slice implementation proposals.
3. **Owner directive S342 (2026-05-11)** — "Please proceed with Backlog priorities. Parallelize work and proceed without my intervention when possible." Authorizes this Slice 1 NEW filing as the band-2 (Acceleration / deterministic-services) top priority per the S332 default idle work directive.

Outstanding owner decisions before VERIFIED: none for Slice 1. Per-invocation `gt deliberations record` calls carry their own per-deliberation AUQ evidence as args (which is the entire point of the deterministic surface); no further session-level owner decision is required to land Slice 1's CLI plumbing.

## Scope

### IP-1: New CLI subcommand `gt deliberations record`

Add a new subcommand under the existing `gt deliberations` argparse group at `groundtruth-kb/src/groundtruth_kb/cli.py` (registered around line 1895 next to `add`, `upsert`, `get`, `list`, `search`, `link`, `rebuild-index`).

The subcommand accepts these arguments:

- `--source-type` (required; one of the valid `source_type` enum values: `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`, etc., matching `KnowledgeDB.insert_deliberation()` validation)
- `--title` (required; max 200 chars)
- `--summary` (required; max 500 chars)
- `--content-file` (required; path to file containing the deliberation content; resolved relative to project root; must be inside `E:\GT-KB`)
- `--change-reason` (required; short rationale, typically cites bridge thread or DELIB-ID)
- `--auq-id` (optional; the AskUserQuestion question_hash or DECISION-NNNN id that authorized this insert)
- `--auq-answer` (optional; verbatim owner answer text from the AUQ; used to populate `explicit_change_request`)
- `--owner-presented` (boolean flag; when set, asserts that the owner saw the proposed insert and that the transcript captures it; populates `presented_to_user=true` and `transcript_captured=true` in the packet)
- `--spec-id` (optional; passed through to `insert_deliberation()`)
- `--work-item-id` (optional; passed through)
- `--participants` (optional; comma-separated list)
- `--outcome` (optional)
- `--session-id` (optional; defaults to current session from `harness-state/active-session.json` if available)
- `--dry-run` (optional; prints planned packet + insert without writing or calling DB)

### IP-2: Deterministic packet construction logic

A new internal helper `_record_deliberation_packet()` in `groundtruth-kb/src/groundtruth_kb/cli/_deliberations_record.py` (or equivalent module location consistent with existing CLI structure):

1. Reads `--content-file` into memory.
2. Computes `full_content_sha256 = sha256(content_bytes).hexdigest()`.
3. Constructs a packet dict with all 11+ required fields from `.claude/hooks/formal-artifact-approval-gate.py:60-70`:
   - `artifact_type="deliberation"`
   - `artifact_id=<generated DELIB-NNNN>` (queried from DB or pre-generated)
   - `action="create"`
   - `source_ref=<from --source-ref or constructed from --auq-id>`
   - `full_content=<content>` (verbatim)
   - `full_content_sha256=<computed hash>`
   - `approval_mode="approve"` (when `--owner-presented` set) or `"auto"` (when AUQ-evidence missing — see safety note below)
   - `presented_to_user=<--owner-presented>`
   - `transcript_captured=<--owner-presented>`
   - `explicit_change_request=<--auq-answer or "AUQ evidence not captured at record time">`
   - `changed_by=<harness identity from harness-state/harness-identities.json>`
   - `change_reason=<--change-reason>`
4. Writes packet JSON to `.groundtruth/formal-artifact-approvals/<YYYY-MM-DD>-<artifact-id>.json` (matching `[approval_packet] packet_filename_pattern` in `config/governance/narrative-artifact-approval.toml`).
5. Sets `os.environ["GTKB_FORMAL_APPROVAL_PACKET"]` to the packet path.
6. Calls `db.insert_deliberation()` with the args (the gate hook reads the env var, validates the packet, and allows the insert).
7. On success, prints the assigned DELIB-NNNN id; on failure, propagates the gate error.

**Safety note on `approval_mode="auto"`:** When `--owner-presented` is not set and `--auq-id` is missing, the packet is rejected by the existing gate (because `presented_to_user=true` is required). This is intentional: the CLI does NOT bypass the gate; it merely deterministically constructs valid packets when owner-evidence inputs are supplied. The CLI surfaces the gate error to the caller with a clear message about which fields are missing.

### IP-3: Tests (Slice 1 spec-derived)

Add `platform_tests/groundtruth_kb/cli/test_deliberations_record.py` covering:

- T-DR-1 (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001): packet construction is deterministic — given identical inputs, the packet JSON has identical SHA-256.
- T-DR-2 (PB-ARTIFACT-APPROVAL-001): `full_content_sha256` in packet matches `sha256(content_bytes)` of the file.
- T-DR-3 (GOV-ARTIFACT-APPROVAL-001): when `--owner-presented` not set, the packet has `presented_to_user=false` and the existing gate rejects the insert.
- T-DR-4 (DCL-ARTIFACT-APPROVAL-HOOK-001): when packet is valid (all required fields, hash matches, owner-presented=true), the insert succeeds and the gate allows it.
- T-DR-5 (ADR-ISOLATION-APPLICATION-PLACEMENT-001): packet path is always under `.groundtruth/formal-artifact-approvals/` inside `E:\GT-KB`; rejects `--content-file` paths outside the project root.
- T-DR-6 (GOV-FILE-BRIDGE-AUTHORITY-001): no bridge-protocol regression — `--dry-run` invocation does not mutate INDEX or write packet files.
- T-DR-7 (ADR-ARTIFACT-FORMALIZATION-GATE-001): smoke test confirming the gate's protected-mutations list at `.claude/hooks/formal-artifact-approval-gate.py:48` still matches `gt deliberations record` (so the gate continues to fire on `record` invocations after this slice lands).

### IP-4: CLI help + man-page-equivalent documentation

Update `gt deliberations --help` output to include `record` in the subcommand list. No separate documentation files (e.g., docs/) in scope for Slice 1; that's tracked as a follow-on.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` — MODIFIED (add `record` subparser + handler ~30-40 LOC)
- `groundtruth-kb/src/groundtruth_kb/cli/_deliberations_record.py` — NEW (~150 LOC; deterministic packet construction)
- `platform_tests/groundtruth_kb/cli/test_deliberations_record.py` — NEW (~300 LOC; 7 spec-derived tests)
- `.claude/hooks/formal-artifact-approval-gate.py` — POSSIBLY MODIFIED (add `gt deliberations record` to the protected-mutations list at `:48` if not already implicitly covered by the existing `gt deliberations add|upsert|link` regex)

None of the changed files are protected narrative artifacts (CLAUDE.md, AGENTS.md, .claude/rules/*.md, memory/work_list.md). No narrative-artifact approval packet is required for Slice 1.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record` — PASS expected (`missing_required_specs: []`, `missing_advisory_specs: []`).
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record` — exit 0 expected (0 blocking gaps).

### Implementation tests

3. `pytest platform_tests/groundtruth_kb/cli/test_deliberations_record.py -q --tb=short` — all 7 T-DR-* tests PASS.

### Regression tests

4. `pytest platform_tests/groundtruth_kb/ -q --tb=short -k "deliberation"` — pre-existing deliberation-related tests PASS unchanged.
5. `pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short` — gate tests PASS unchanged.

### Live smoke

6. End-to-end smoke: invoke `gt deliberations record --source-type=session_harvest --title="Slice 1 smoke test" --summary="..." --content-file=...` and confirm:
   - Packet written to `.groundtruth/formal-artifact-approvals/<date>-DELIB-NNNN.json`
   - DELIB-NNNN row appears in `groundtruth.db`
   - ChromaDB index entry is created (existing `insert_deliberation()` already handles this)
   - Re-running with same content produces dedup behavior matching existing `add`/`upsert` semantics

### Spec-to-test mapping

| Spec | Verifying test |
|------|----------------|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1 (preflight) + 6 (no INDEX regression) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2 + this mapping + T-DR-1 |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | 1 (path:.claude/rules/file-bridge-protocol.md match) + T-DR-5 (filesystem assertion) |
| GOV-ARTIFACT-APPROVAL-001 | T-DR-3 (gate rejects missing owner-presented) |
| PB-ARTIFACT-APPROVAL-001 | T-DR-2 (content-hash binding) |
| ADR-ARTIFACT-FORMALIZATION-GATE-001 | T-DR-7 (gate still fires on `record`) |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | T-DR-4 (valid packet allows insert) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | 6 (live smoke produces DELIB-NNNN row) |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | 6 (deliberation lifecycle integrity) |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | 6 (status transitions intact) |
| GOV-STANDING-BACKLOG-001 | See Clause Scope Clarification section below — not a bulk operation. |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | 6 (~150 LOC of orchestration → 1 CLI call demonstrated) + T-DR-1 (deterministic) |

## Acceptance Criteria

- [ ] Applicability preflight PASS (`missing_required_specs: []`, `missing_advisory_specs: []`).
- [ ] Clause preflight exit 0; 0 blocking gaps.
- [ ] Codex GO on this Slice 1 NEW.
- [ ] Implementation lands: `gt deliberations record` subcommand registered, packet-construction module added, 7 T-DR-* tests authored.
- [ ] Tests 3, 4, 5, 6 PASS.
- [ ] Codex VERIFIED on Slice 1 post-implementation report.
- [ ] Slice 1 commit uses recommended type `feat:` (net-new CLI capability).

## Risk + Rollback

### Risks

- **R1 (Low):** Packet schema drift between `gt deliberations record` and the gate. Mitigation: T-DR-7 explicitly tests gate compatibility; gate is the authoritative validator at write time.
- **R2 (Low):** Existing `gt deliberations add|upsert` callers might be confused by the new `record` surface. Mitigation: `add` and `upsert` remain unchanged; help-text distinguishes "advanced/explicit packet" (add/upsert) vs "AUQ-driven structured insert" (record).
- **R3 (Very Low):** CLI argument explosion. Mitigation: Slice 1 keeps args focused (6 required + 6 optional); no nested subcommands.
- **R4 (Low):** `--owner-presented=false` packets (action="auto") could be misused to bypass owner approval. Mitigation: The gate enforces `presented_to_user=true` for non-auto inserts; auto-mode requires explicit `approval_mode="auto"` which the gate currently rejects for `artifact_type="deliberation"` per `.claude/hooks/formal-artifact-approval-gate.py:60-70`. T-DR-3 covers this explicitly.

### Rollback

`git revert <slice-1-impl-commit-sha>` removes the `record` subcommand cleanly. The packets directory and existing `add`/`upsert` surfaces are unaffected. No data migration required.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` and the S342 feedback pattern (auto-memory `feedback_bulk_ops_clause_false_positive_s342.md`): this Slice 1 proposal mentions the standing backlog and work items in the priority-band context (S332 band 2 — Acceleration / deterministic-services), but the proposal itself is NOT a bulk operation on the backlog. Specifically:

- No `inventory` operations on `work_items` or `memory/work_list.md` are in scope.
- No bulk insert, update, or delete of MemBase rows is in scope.
- The implementation creates a single new CLI subcommand and one supporting test file; no existing backlog records are touched.
- The `formal-artifact-approval` discipline IS exercised at every `gt deliberations record` invocation (defense-in-depth), but each invocation operates on a single deliberation row.

Per the clause-preflight feedback, this section's presence (with the `inventory` and `formal-artifact-approval` evidence-pattern tokens above) satisfies the bulk-ops clause for non-bulk proposals.

## Bridge Protocol Compliance

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this Slice 1 proposal is filed as a versioned bridge artifact under `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-001.md`, and its `NEW` status line is inserted at the top of `bridge/INDEX.md` per the file-bridge-protocol convention. No prior bridge version is rewritten or deleted; the INDEX update is append-only above the immediately-preceding `gtkb-canonical-bridge-parser-withdrawn-status-handling` entry. Post-implementation reporting (anticipated under version `-NNN.md` after Codex GO + implementation) will likewise add a new INDEX line at the top of this thread's version chain. The author-side bridge-compliance-gate hook ran against this file before submission; if a NO-GO returns, REVISED versions will be filed at incrementing `-NNN.md` filenames per protocol.

## Recommended Commit Type

`feat:` — Slice 1 adds net-new `gt deliberations record` CLI capability (a new subcommand, supporting module, test file). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B and `.claude/rules/file-bridge-protocol.md` § Conventional Commits Type Discipline, this is `feat` (net-new module + capability surface), not `chore` (maintenance) or `refactor` (restructuring without behavior change).

## Loyal Opposition Asks

1. Confirm Slice 1 scope is correctly narrowed to `gt deliberations record` CLI surface only (no Slice 2-6 work mixed in).
2. Confirm the deterministic packet-construction approach preserves the existing approval-gate's safety contract (packet hash binds to content; gate validates at write time; `--owner-presented=false` correctly rejected by gate).
3. Confirm the test plan's 7 T-DR-* tests provide adequate spec-derived coverage for the linked specifications.
4. Confirm `gt deliberations record` does not duplicate `add` or `upsert` in a confusing way, and that the help-text distinguishes them.
5. Confirm the `## Clause Scope Clarification (Not a Bulk Operation)` section adequately disarms the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` false-positive per the S342 feedback pattern.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
