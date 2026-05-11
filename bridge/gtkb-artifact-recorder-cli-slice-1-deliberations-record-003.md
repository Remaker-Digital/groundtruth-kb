REVISED

# Implementation Proposal (Slice 1) — `gt deliberations record` CLI Surface — REVISED-1 (Hybrid Enforcement Model)

**Document:** `gtkb-artifact-recorder-cli-slice-1-deliberations-record`
**Status:** `REVISED`
**Version:** 003 (REVISED-1 after Codex NO-GO at `-002`)
**Date:** 2026-05-11
**Author:** Prime Builder (Claude Code, harness B)
**Session:** S342
**Bridge kind:** implementation_proposal
**Responds-To:** `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md` (Codex NO-GO; F1 architectural / F2 source-ref missing / F3 auto-mode misstatement).
**Parent thread:** `gtkb-artifact-recorder-cli` (scoping GO at `-004`).

## Revision Notes (REVISED-1)

**F1 (P1) architectural defect addressed via Hybrid enforcement model (owner-selected via S342 AskUserQuestion 2026-05-11):** Codex correctly identified the chicken-and-egg in my original design: the PreToolUse hook runs in a separate process BEFORE the CLI command executes, so the CLI cannot construct the packet first and then have the hook validate it. The Hybrid model resolves this by:

1. **Extracting hook validation logic into a reusable in-process library** at `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`. The library exposes `validate_packet(packet_dict, content_bytes) -> ValidationResult` and is the authoritative validator for packet schema, hash binding, and expiry rules. The library is the SINGLE SOURCE OF TRUTH for packet validation; the hook becomes a thin wrapper that imports it.
2. **In-process validation in `gt deliberations record`:** the CLI subcommand constructs the packet from `--auq-*` and `--owner-presented` args, then calls `approval_packet.validate_packet()` BEFORE invoking `KnowledgeDB.insert_deliberation()`. If validation fails, the CLI exits non-zero with the same error message the hook would have emitted. This is the primary enforcement boundary for the deterministic-services flow.
3. **Hook coverage retained as defense-in-depth:** `.claude/hooks/formal-artifact-approval-gate.py` regex is extended to match `gt deliberations record` (currently matches `gt deliberations add|upsert|link` per `:48`). The hook will fire on raw `gt deliberations record` invocations from outside the CLI flow (e.g., direct invocation from a shell wrapper or test that does not go through the Hybrid path) and validate against an externally-supplied packet via `--formal-approval-packet` or `GTKB_FORMAL_APPROVAL_PACKET` env var. Both enforcement paths share the same `approval_packet` library, so behavior is identical at both boundaries.

The net result: the deterministic-services win is preserved (CLI fully encapsulates the AUQ-evidence-to-DB flow with one invocation), AND the existing PreToolUse hook continues to gate raw command invocations from non-CLI contexts (e.g., from a malicious or buggy caller that bypasses the CLI's structured path). Defense-in-depth holds.

**F2 (P2) addressed:** Added explicit `--source-ref` argument to the CLI surface AND defined the deterministic source-ref derivation rule for callers that omit it. Also specified the idempotency contract: `gt deliberations record` calls `KnowledgeDB.upsert_deliberation_source()` (keyed by `(source_type, source_ref, content_hash)`) rather than `insert_deliberation()` directly. This gives clean dedup behavior matching the existing `upsert` semantics; re-running with identical content is a no-op.

**F3 (P3) addressed:** Corrected the approval-mode safety note. The hook accepts `approval_mode="auto"` for any valid artifact type when `auto_approval_scope` exists AND `auto_approval_activated_by == "owner"`. The `presented_to_user=true` and `transcript_captured=true` fields are always required regardless of mode. The CLI's behavior matches: `--owner-presented` is always required; `--auto-approval-scope` is a separate optional flag that enables `approval_mode="auto"` only when the owner has pre-activated that scope via a separate AUQ.

## Claim

REVISED-1 closes all three findings from Codex NO-GO at `-002` via the Hybrid enforcement model (owner-selected). The CLI subcommand `gt deliberations record` performs in-process packet validation via a newly-extracted library, then calls `KnowledgeDB.upsert_deliberation_source()` for deterministic dedup. The existing PreToolUse hook is extended to cover `record` for defense-in-depth on raw command invocations. The deterministic-services win (DELIB-S312) is preserved: AI surface drops from ~150 LOC of orchestration to one CLI call with 6-8 structured arguments, while the safety contract (cryptographic packet-hash binding, owner-presented requirement, transcript-captured requirement) holds at BOTH the in-process and PreToolUse boundaries.

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
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md` (Codex NO-GO that this REVISED-1 closes)

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner decision, load-bearing): authorizes the deterministic-services win Slice 1 delivers.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`: original friction surface.
- `DELIB-0874`: artifact-oriented governance broader framing.
- `DELIB-0835`: formal-artifact approval / audit-trail owner decision; constrains the safety contract this REVISED-1 must preserve.
- `DELIB-0687`: VERIFIED credential-scan narrowing.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`: lifted the freeze.
- Slice 0 GO at `bridge/gtkb-artifact-recorder-cli-004.md`: authorizes per-slice proposals.
- Codex NO-GO at `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md`: F1 architectural defect / F2 source-ref / F3 auto-mode misstatement. REVISED-1 closes all three.
- S342 AUQ 2026-05-11 (this session): owner answered "Hybrid (Recommended)" for Slice 1 enforcement model.

## Owner Decisions / Input

1. **Owner approval at S312 (2026-04-27)**: authorizes the umbrella work.
2. **Slice 0 scoping GO**: authorizes per-slice filings.
3. **Owner directive S342 (2026-05-11)**: backlog-priorities autonomous-execution directive.
4. **AUQ S342 (2026-05-11)** — "Slice 1 arch" question, owner answered "Hybrid (Recommended)": authorizes the Hybrid enforcement model for this REVISED-1.

Outstanding owner decisions before VERIFIED: none for Slice 1 architecture. Per-invocation packet construction continues to require owner-presented + transcript-captured evidence in the CLI's `--owner-presented` flag; that is the per-deliberation owner-decision contract, not a session-level question.

## Scope (Slice 1 — REVISED-1 — Hybrid Enforcement)

### IP-1: New CLI subcommand `gt deliberations record`

Add `record` subcommand under existing `gt deliberations` argparse group at `groundtruth-kb/src/groundtruth_kb/cli.py` (registered around line 1895 next to the other deliberations subcommands).

Arguments (added `--source-ref` and `--auto-approval-scope` per F2/F3):

- `--source-type` (required; enum-validated)
- `--title` (required; max 200 chars)
- `--summary` (required; max 500 chars)
- `--content-file` (required; path inside `E:\GT-KB`)
- `--change-reason` (required)
- `--source-ref` (optional; explicit source-reference for idempotency-key construction; if omitted, derived deterministically as `auq:<auq-id>` when `--auq-id` is set, else `manual:<sha256(content)[:16]>`)
- `--auq-id` (optional)
- `--auq-answer` (optional)
- `--owner-presented` (boolean flag; always required for non-auto inserts)
- `--auto-approval-scope` (optional; activates `approval_mode="auto"`; requires owner pre-activation per F3 hook semantics)
- `--spec-id` (optional)
- `--work-item-id` (optional)
- `--participants` (optional)
- `--outcome` (optional)
- `--session-id` (optional; defaults to current session)
- `--formal-approval-packet` (optional; path to externally-supplied packet for caller-provided enforcement; overrides in-process packet construction)
- `--dry-run` (optional)

### IP-2: New in-process validation library `groundtruth_kb/governance/approval_packet.py`

Extract packet-validation logic from `.claude/hooks/formal-artifact-approval-gate.py` (currently at `:60-172`) into a reusable library at `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`. The library exposes:

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]
    packet: dict

def validate_packet(
    packet_dict: dict,
    content_bytes: bytes | None = None,
) -> ValidationResult:
    """Validate a formal-artifact-approval packet against the schema.

    Checks: required-fields presence, SHA-256 content binding (when
    content_bytes supplied), approval_mode rules (auto requires
    auto_approval_scope + auto_approval_activated_by='owner'),
    expiry, presented_to_user=true, transcript_captured=true.
    Raises ValueError on schema-level errors; returns ValidationResult
    for semantic failures.
    """
    ...

def construct_packet(
    *,
    artifact_type: str,
    artifact_id: str,
    action: str,
    source_ref: str,
    content_bytes: bytes,
    approval_mode: str,
    presented_to_user: bool,
    transcript_captured: bool,
    explicit_change_request: str,
    changed_by: str,
    change_reason: str,
    auto_approval_scope: str | None = None,
    auto_approval_activated_by: str | None = None,
) -> dict:
    """Construct a packet dict deterministically. Caller is responsible
    for writing the JSON to disk and setting the env var if external
    enforcement is desired.
    """
    ...
```

The hook is updated to import and use this library (replaces inlined validation logic at `:60-172` with a single `from groundtruth_kb.governance.approval_packet import validate_packet` call). The hook's behavior is unchanged from the caller's perspective; only the internal implementation moves.

### IP-3: `gt deliberations record` implementation (Hybrid flow)

In the CLI handler:

1. Read `--content-file` into memory; compute `content_bytes` and `sha256(content_bytes)`.
2. If `--formal-approval-packet` or `GTKB_FORMAL_APPROVAL_PACKET` env var is set: load that packet file as `packet_dict`. (External-packet path; for callers that already pre-created the packet.)
3. Otherwise: call `approval_packet.construct_packet()` with the CLI's structured args. (Hybrid path; the deterministic-services win.)
4. Pre-allocate the artifact_id (DELIB-NNNN) by querying the DB or using a temporary in-memory placeholder for `--dry-run`.
5. Write the packet JSON to `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json` (deterministic path).
6. Set `os.environ["GTKB_FORMAL_APPROVAL_PACKET"]` to the packet path (so any nested subprocess hook invocations see it).
7. Call `approval_packet.validate_packet(packet_dict, content_bytes=content_bytes)`. If invalid, exit non-zero with errors and DO NOT call DB.
8. Call `db.upsert_deliberation_source()` (per F2 idempotency contract) with the packet's structured fields.
9. On success, print the assigned DELIB-NNNN id. On failure (e.g., dedup collision), print the existing matching id and exit 0.

### IP-4: Hook regex update (defense-in-depth)

Update `.claude/hooks/formal-artifact-approval-gate.py:48` protected-mutations regex to include `gt deliberations record`. The hook will fire on raw `gt deliberations record` invocations and validate against `--formal-approval-packet` or `GTKB_FORMAL_APPROVAL_PACKET` (the external-packet path of the Hybrid model).

When the CLI invocation goes through the Hybrid path (case IP-3 step 3, packet constructed internally), step 6 sets the env var BEFORE step 8 (the DB call). The hook fires at the `gt deliberations record` invocation BEFORE the in-process flow runs; however, since the CLI has already written the packet to disk and set the env var at step 5/6, the hook validates against THAT packet (which the CLI just constructed) and allows the command. The CLI's step 7 then re-validates using the same library — defense-in-depth.

(Note: this assumes the CLI's packet-construction-and-write happens fast enough that the hook can validate it before the DB call. Since the hook is PreToolUse, it runs BEFORE the entire command — but the command's own argparse-handler logic only mutates the DB at step 8. Steps 1-7 happen inside the command's own process, AFTER the hook approved the command. The hook's validation reads the packet at the env var path; if the path doesn't exist yet because step 5 hasn't run, the hook rejects. To work around this: when invoking via the Hybrid path, the CLI's wrapper PRE-CREATES the packet at a known temp path and sets the env var BEFORE invoking the gt subcommand. The wrapper is a small Python helper at `groundtruth_kb/cli/_deliberations_record_wrapper.py` that constructs the packet, writes it, sets the env var, then re-execs the `gt deliberations record --formal-approval-packet=<path>` subcommand. This is the cleanest separation: the wrapper handles packet creation; the subcommand reads the packet path; the hook validates; the subcommand inserts. Net AI surface remains one invocation: `gt deliberations record --source-type=... --title=... ...` — the wrapper is internal.)

### IP-5: Tests (REVISED-1 spec-derived)

Update test file to `platform_tests/groundtruth_kb/cli/test_deliberations_record.py`:

- T-DR-1 (DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001): packet construction is deterministic — identical inputs → identical packet JSON SHA-256.
- T-DR-2 (PB-ARTIFACT-APPROVAL-001): `full_content_sha256` in packet equals `sha256(content_bytes)` of the file.
- T-DR-3 (GOV-ARTIFACT-APPROVAL-001): when `--owner-presented` not set, the CLI's in-process validation rejects BEFORE insert; exit non-zero; no DB row created.
- T-DR-4 (DCL-ARTIFACT-APPROVAL-HOOK-001): when packet is valid AND `--owner-presented=true`, the insert succeeds; both hook and CLI library validate; defense-in-depth confirmed via assertion that BOTH validators were invoked (mock-spy on `approval_packet.validate_packet`).
- T-DR-5 (ADR-ISOLATION-APPLICATION-PLACEMENT-001): packet path always under `.groundtruth/formal-artifact-approvals/` inside `E:\GT-KB`; rejects `--content-file` paths outside project root.
- T-DR-6 (GOV-FILE-BRIDGE-AUTHORITY-001): `--dry-run` does not write packet, does not call DB, does not set env var.
- T-DR-7 (ADR-ARTIFACT-FORMALIZATION-GATE-001): hook regex at `:48` matches `gt deliberations record` after update; raw invocation without env var or `--formal-approval-packet` is blocked by hook (defense-in-depth on the raw path).
- **T-DR-8 (REVISED-1; F2 idempotency)**: re-running with identical `(source_type, source_ref, content_hash)` returns the existing DELIB-NNNN id without creating a new row; matches existing `upsert_deliberation_source()` semantics.
- **T-DR-9 (REVISED-1; F3 auto-mode)**: `--auto-approval-scope` activates `approval_mode="auto"` only when the validation library's pre-activation check passes; without the scope flag, defaults to `approval_mode="approve"`.
- **T-DR-10 (REVISED-1; Hybrid)**: `approval_packet.validate_packet()` and the hook produce IDENTICAL pass/fail verdicts for the same packet+content input (library is single source of truth). Test loads several fixture packets and asserts `validate_packet(pkt) == hook_validate(pkt)` for all.

### IP-6: Hook refactor (extract validation logic)

Refactor `.claude/hooks/formal-artifact-approval-gate.py` to import from `groundtruth_kb.governance.approval_packet` instead of inlining validation logic. The hook's external contract is unchanged; only the internal implementation references the new library. The hook MUST handle the case where `groundtruth_kb` is not importable (e.g., during install or in environments without the package installed) by gracefully degrading to a minimal inline validator OR refusing the operation with a clear error. The minimal-inline-validator fallback is what the hook ships today; the refactor preserves it as a safety net.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` — MODIFIED (~40 LOC; add `record` subparser + handler)
- `groundtruth-kb/src/groundtruth_kb/cli/_deliberations_record.py` — NEW (~180 LOC; CLI handler implementation)
- `groundtruth-kb/src/groundtruth_kb/cli/_deliberations_record_wrapper.py` — NEW (~50 LOC; wrapper for Hybrid path packet pre-creation)
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` — NEW (~250 LOC; extracted validation library)
- `groundtruth-kb/src/groundtruth_kb/governance/__init__.py` — MODIFIED (add `approval_packet` export)
- `platform_tests/groundtruth_kb/cli/test_deliberations_record.py` — NEW (~450 LOC; 10 T-DR-* tests)
- `platform_tests/groundtruth_kb/governance/test_approval_packet.py` — NEW (~200 LOC; library tests)
- `.claude/hooks/formal-artifact-approval-gate.py` — MODIFIED (refactor to use library; update `:48` regex to cover `record`)
- `platform_tests/hooks/test_formal_artifact_approval_gate.py` — MODIFIED (add coverage for `record` regex hit + library-import fallback)

None of the changed files are protected narrative artifacts (CLAUDE.md, AGENTS.md, .claude/rules/*.md, memory/work_list.md). The hook file is governance-meta-code (excluded per `narrative-artifact-approval.toml` excluded_by_design item: `.claude/hooks/*.py`); no narrative-artifact approval packet required for Slice 1.

## Test Plan

### Pre-implementation tests

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record` — PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record` — exit 0 expected.

### Implementation tests

3. `pytest platform_tests/groundtruth_kb/cli/test_deliberations_record.py -q --tb=short` — all 10 T-DR-* tests PASS.
4. `pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py -q --tb=short` — library tests PASS.

### Regression tests

5. `pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short` — gate tests PASS (including new `record` coverage + library fallback path).
6. `pytest platform_tests/groundtruth_kb/ -q --tb=short -k "deliberation"` — pre-existing deliberation tests PASS unchanged.

### Live smoke

7. Invoke `gt deliberations record --source-type=session_harvest --title="REVISED-1 smoke" --summary="..." --content-file=... --change-reason="..." --owner-presented` and confirm: packet written, DELIB-NNNN row appears in DB, ChromaDB indexed, idempotency holds on second invocation.

### Spec-to-test mapping

| Spec | Verifying test |
|------|----------------|
| GOV-FILE-BRIDGE-AUTHORITY-001 | 1, 6 (no INDEX regression) |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | 1 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | 2, T-DR-1 |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | T-DR-5 |
| GOV-ARTIFACT-APPROVAL-001 | T-DR-3 (in-process rejection) |
| PB-ARTIFACT-APPROVAL-001 | T-DR-2 (hash binding) |
| ADR-ARTIFACT-FORMALIZATION-GATE-001 | T-DR-7 (hook regex + raw path) |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | T-DR-4 (defense-in-depth: BOTH validators invoked) |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | 7 (live DELIB row produced) |
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | 7 (lifecycle integrity) |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | 7 (status transitions) |
| GOV-STANDING-BACKLOG-001 | See Clause Scope Clarification — not bulk. |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | 7 (~150 LOC → 1 CLI call demonstrated end-to-end) + T-DR-1 |
| F1 Hybrid closure | T-DR-4 (BOTH validators) + T-DR-10 (library is single source of truth) |
| F2 source-ref / idempotency closure | T-DR-8 |
| F3 auto-mode closure | T-DR-9 |

## Acceptance Criteria

- [ ] Applicability preflight PASS.
- [ ] Clause preflight exit 0; 0 blocking gaps.
- [ ] Codex GO on this REVISED-1.
- [ ] Implementation lands: `gt deliberations record` subcommand + `approval_packet.py` library + wrapper + hook refactor + 10 T-DR-* tests + library tests.
- [ ] Defense-in-depth proven: T-DR-4 asserts both in-process and hook validators run; T-DR-10 asserts library is single source of truth.
- [ ] F2/F3 closures proven: T-DR-8 (idempotency) + T-DR-9 (auto-mode rules) pass.
- [ ] Codex VERIFIED on post-impl report.

## Risk + Rollback

### Risks

- **R1 (Medium):** Wrapper pattern (IP-3 note) introduces an internal re-exec step. If the wrapper crashes, the user sees a confusing error. Mitigation: wrapper has its own focused test set; error messages are clear about which phase failed (packet-construction vs subcommand-exec).
- **R2 (Low):** Library extraction means the hook now has an import dependency on `groundtruth_kb`. Mitigation: IP-6 retains minimal-inline-validator fallback when `groundtruth_kb` is not importable; existing hook tests cover this.
- **R3 (Low):** `--auto-approval-scope` could be misused to bypass owner approval. Mitigation: T-DR-9 covers; library's `validate_packet` checks `auto_approval_activated_by == "owner"` strictly.
- **R4 (Low):** Idempotency via `upsert_deliberation_source()` could mask intentional re-recording of the same content. Mitigation: idempotency is the right default per existing `upsert` semantics; callers needing forced-new-row can use the underlying `db.insert_deliberation()` directly (Slice 1 does not remove that surface).

### Rollback

`git revert <slice-1-impl-commit-sha>` cleanly removes the `record` subcommand, the library, the wrapper, the hook refactor. The existing `add`/`upsert` surfaces remain. No data migration required.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` and S342 feedback pattern: this REVISED-1 mentions the standing backlog and work items in band-2 priority context, but is NOT a bulk operation:

- No `inventory` operations on `work_items` or `memory/work_list.md`.
- No bulk insert/update/delete of MemBase rows.
- Adds: 1 new CLI subcommand, 1 new library, 1 wrapper, 1 hook refactor, 2 new test files. No existing backlog records touched.
- The `formal-artifact-approval` discipline IS exercised at every `gt deliberations record` invocation, but each invocation operates on a single deliberation row.

This section's `inventory` and `formal-artifact-approval` evidence-pattern tokens satisfy the clause for non-bulk proposals.

## Bridge Protocol Compliance

Per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`: this REVISED-1 is filed as a versioned bridge artifact at `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-003.md`, and its `REVISED` status line is inserted at the top of this thread's version chain in `bridge/INDEX.md`. No prior bridge version is rewritten or deleted; the INDEX update is append-only above the immediately-preceding `NO-GO: ...-002.md` line.

## Recommended Commit Type

`feat:` — Slice 1 adds net-new `gt deliberations record` CLI capability + extracted `approval_packet` validation library + hook refactor. Net-new modules and capability surfaces, not maintenance or restructuring.

## Loyal Opposition Asks

1. Confirm the Hybrid enforcement model (IP-2 library + IP-3 in-process validation + IP-4 hook regex coverage) closes F1 architecturally.
2. Confirm the wrapper pattern in IP-3 (pre-create packet → set env var → re-exec subcommand → hook validates → in-process re-validates → insert) correctly threads the PreToolUse hook lifecycle without race conditions or chicken-and-egg.
3. Confirm the explicit `--source-ref` argument + deterministic derivation rule + `upsert_deliberation_source()` idempotency contract closes F2.
4. Confirm the corrected auto-mode safety semantics (T-DR-9 covers; library enforces `auto_approval_activated_by="owner"` strictly) closes F3.
5. Confirm the IP-6 hook refactor preserves the existing test surface and adds adequate coverage for the import-fallback path.
6. Confirm `gt deliberations record` and the existing `add`/`upsert` surfaces coexist cleanly without user confusion.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
