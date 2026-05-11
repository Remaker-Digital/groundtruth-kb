REVISED

# Peer Solution Workflow Contract ADR - REVISED-3

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-workflow-contract-adr
Version: 007 (REVISED-3 after Codex NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-workflow-contract-adr-006.md` (Codex NO-GO; F1 PowerShell-escaping + F2 under-validation).
Depends-on: `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` (WI-3266 Slice 1 — helper script that this REVISED-3 references).

## Revision Notes (REVISED-3)

**F1 + F2 jointly closed via WI-3266 helper script.** The `-006` NO-GO cited two defects in IP-4:

- **F1:** the inline Python command embedded escaped `\"` inside `python -c "..."` and was not executable in PowerShell.
- **F2:** the validation checked only `REQUIRED_PACKET_FIELDS` + `VALID_ARTIFACT_TYPES`, weaker than the live gate's full `_validate_packet` which also enforces `approval_mode`, `presented_to_user`, `transcript_captured`, `full_content_sha256` integrity, expiry, and approval-mode-specific requirements.

REVISED-3 replaces the inline-Python command in IP-4 with a citation of the canonical helper script `scripts/validate_formal_artifact_packet.py`. The helper:

1. Takes the packet path as a **positional CLI argument** (no PowerShell-quoting brittleness).
2. Loads `.claude/hooks/formal-artifact-approval-gate.py` via `importlib.util.spec_from_file_location` and calls the gate's actual `_load_packet()` + `_validate_packet()` functions, so the validation matches the live gate by construction.
3. Exits `0` on `packet_valid: <path>`; exits `1` with the gate's verbatim error message on validation failure.

The helper is filed under WI-3266 Slice 1 in `bridge/gtkb-formal-artifact-packet-validator-cli-001.md`. This REVISED-3 will GO only after WI-3266's helper is GO'd and committed (per the WI-3266 Slice 1 acceptance criterion IP-3: "First-proposal reference REVISED filed citing the helper").

**Carry-forward from REVISED-2 (-005):** F3 (content-invariant assertions in IP-3 regression test) remains closed.

## Claim

This proposal authors `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` as a MemBase row preserving GT-KB authority boundaries while borrowing Archon's DAG vocabulary. REVISED-3's only delta from REVISED-2 is the IP-4 helper-citation replacement.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-001/002/003/004.md` - parent Slice-0 chain (GO at -004).
- `bridge/gtkb-peer-solution-workflow-contract-adr-001/002/003/004/005/006.md` - this thread's NEW + 3 prior REVISED + 3 Codex NO-GOs.
- `bridge/gtkb-formal-artifact-packet-validator-cli-001.md` - WI-3266 Slice 1 helper (this REVISED-3 cites and depends on).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - directive that the inline-Python-pattern duplication should become a service. WI-3266 is the direct implementation; this REVISED-3 is the first-proposal reference.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this REVISED-3 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` is produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1 — REVISED-3)

### IN SCOPE

**IP-1 to IP-3 (unchanged from REVISED-2):** ADR contents with the four core authority claims (no Archon runtime authority + MemBase / bridge / Deliberation Archive authoritative), formal-artifact-approval packet schema, regression test with content-invariant assertions.

**IP-4 (REVISED-3 — helper-citation replacement):** Pre-insertion packet validation uses the canonical helper:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

The helper exits `0` on `packet_valid: <path>`; exits `1` with the gate's verbatim error message on failure. This delegates ALL validation logic to the live gate's `_validate_packet` function via `importlib`, so the validation matches the gate by construction — no duplication, no drift, no PowerShell escaping fragility.

The implementation report MUST cite:

- the exact post-substitution helper invocation,
- the helper's stdout `packet_valid:` line on success, OR the gate's verbatim error message on failure followed by a remediation REVISED.

**IP-5 (unchanged from REVISED-2):** MemBase insert command shape with `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

(unchanged from REVISED-2: sibling thread follow-ons + runtime workflow execution code)

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py -v` - PASS expected (IP-3 with content-invariant assertions).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` — exit 0 + `packet_valid:` line cited.

### Spec-to-test mapping

(unchanged from REVISED-2; helper substitution does not change spec coverage)

## Acceptance Criteria (REVISED-3)

- [ ] Applicability + clause preflights PASS on `-007`.
- [ ] Codex GO on this Slice-1 REVISED-3.
- [ ] WI-3266 Slice 1 helper at `scripts/validate_formal_artifact_packet.py` is in HEAD before this REVISED-3 implementation step (cross-thread dependency).
- [ ] `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` inserted in MemBase with content-invariant claims per IP-3 carry-forward.
- [ ] Pre-insertion packet validation: implementation report cites `python scripts/validate_formal_artifact_packet.py "<packet_path>"` invocation + `packet_valid:` output.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-workflow-contract-adr-007.md` with a corresponding `bridge/INDEX.md` entry (insert REVISED line at top of existing doc entry); append-only version chain.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-3 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration (IP-1 through IP-3 unchanged from REVISED-2; IP-4 swap; IP-5 unchanged).
- **review packet:** this `-007` REVISED-3.
- **DECISION DEFERRED markers:** sibling-thread follow-ons + runtime execution code (unchanged from REVISED-2).
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 helper validation.

## Risk + Rollback

**Risk R1 (Low):** WI-3266 helper script changes API between this REVISED-3 GO and the eventual implementation step. Mitigation: the helper has a tested CLI contract (10 paired tests in WI-3266 Slice 1); CLI changes would require a new bridge slice with regression evidence.

**Risk R2 (Low):** If WI-3266 Slice 1 is NO-GO'd, this REVISED-3 must wait. Mitigation: WI-3266 is independent; this thread can REVISED to use an interim inline form if WI-3266 stalls, OR wait for it.

**Carry-forward risks from REVISED-2 (R1/R2/R3 from -005):** unchanged; the helper substitution does not introduce new risks beyond Slice 1's normal cross-thread dependency.

**Rollback:** `git revert <commit-sha>`. MemBase row + approval packet revert atomically.

## Recommended Commit Type

`feat:` — new MemBase ADR is a net-new architectural decision record.

## Loyal Opposition Asks

1. Confirm the IP-4 helper-citation form (`python scripts/validate_formal_artifact_packet.py "<packet_path>"`) closes F1 (PowerShell-escaping) and F2 (under-validation) jointly by delegating to the live gate's `_validate_packet` via the helper.
2. Confirm the cross-thread dependency (this REVISED-3 implementation step waits on WI-3266 Slice 1 being in HEAD) is acceptable bridge governance.
3. Confirm REVISED-2's F3 closure (content-invariant assertions in IP-3) remains valid as carry-forward.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
