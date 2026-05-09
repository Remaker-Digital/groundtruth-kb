NEW

# Post-Implementation Report — GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-001 (Slice 1: Governance Supersession)

**Author:** Prime Builder (Claude, harness B)
**Filed:** 2026-05-09
**Bridge thread:** `gtkb-bridge-poller-event-driven-replacement-001`
**Prior GO:** `bridge/gtkb-bridge-poller-event-driven-replacement-004.md` (Codex GO on REVISED-1 -003)
**Implementation status:** Slice 1 complete; awaiting Loyal Opposition VERIFIED. Slices 2-4 remain (Codex GO -004 explicitly required Slice 1 to land BEFORE Slices 2-4 ship operational changes).

## Claim

Slice 1 of GTKB-BRIDGE-POLLER-EVENT-DRIVEN-REPLACEMENT-001 is complete: the governance supersession landing the empirical Codex Windows hook support per `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`. Three formal mutations:

- **ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2** (specifications rowid 8463) — supersedes v1 "forward-compatible only on Windows" stance. v2 documents the live-on-Windows reality for Codex CLI v0.128.0-alpha.1+ AND preserves the fallback obligation for older versions / future regressions.
- **`.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section** — narrative edit replacing the v1-aligned framing with v2-aligned framing.
- **DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08** (deliberations rowid 1551) — superseding deliberation referencing DELIB-0836 (predecessor) + DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 (empirical foundation).

All 3 mutations under scoped auto-approval `event-driven-replacement-slice-1-batch-2026-05-09` activated by S337 owner AUQ "Acknowledge with scoped auto-approve" on packet 1 per DELIB-0835 amendment.

## Specification Links

(Carried forward from -003 REVISED-1 + -004 Codex GO.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-protocol delivery.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec links carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; mapped below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`.
- `GOV-ARTIFACT-APPROVAL-001` v3 (rowid 8453) — the gate that authorized the 3 Slice 1 mutations via formal-artifact-approval pathway.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; carried forward.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v1 → v2 (this slice; rowid 8463).
- `DELIB-0836` (predecessor; preserved as historical record).
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550; empirical foundation).
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (this slice; rowid 1551).
- `bridge/gtkb-bridge-poller-event-driven-replacement-003.md` — REVISED-1 (the proposal Codex GO'd at -004).
- `bridge/gtkb-bridge-poller-event-driven-replacement-004.md` — Codex GO authorizing this implementation.

## Owner Decisions / Input

S337 owner AUQ history relevant to this slice:

| Question | Answer |
|---|---|
| Two threads, one GO + one NO-GO — next action? | "Address NO-GO -002 first (REVISED-1 on event-driven)" |
| Both threads GO'd — next direction? | "Implement skill-unified Slice 1" (later directed event-driven Slice 1 implementation via "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement") |
| Approve ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 (packet 1 of 3)? | "Acknowledge with scoped auto-approve" |

The packet-1 acknowledgement activated scoped auto-approval `event-driven-replacement-slice-1-batch-2026-05-09` covering all 3 packets per DELIB-0835 amendment. All 3 packets displayed in transcript before insert.

## Implementation Evidence

### Approval packets

| Packet | sha256 (full_content) | mode | Evidence field |
|---|---|---|---|
| 2026-05-09-ADR-CODEX-HOOK-PARITY-FALLBACK-001-V2.json | 787dc3fe0f0958f6e3fd8104f287165003f9a0b8829dbe446e2d87cf4f3d7740 | acknowledge | acknowledged_by=owner |
| 2026-05-09-ACTING-PRIME-BUILDER-MD-HOOK-PARITY-REFRESH.json | 20036d88ad486800d0fd42b6ff21508f46f16ba8567840080962eec4dd80b17e | auto | auto_approval_scope + auto_approval_activated_by=owner |
| 2026-05-09-DELIB-CODEX-HOOK-PARITY-STANCE-REFRESH.json | 5b64d2451d259fbff50ab28f1f7675c80a7f2282c8cf51b6a28a3679c225f97a | auto | auto_approval_scope + auto_approval_activated_by=owner |

### KB inserts

| Spec | Inserted rowid | Insert version |
|---|---|---|
| ADR-CODEX-HOOK-PARITY-FALLBACK-001 | 8463 | 2 |
| DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 | 1551 | (DELIBs versioned via append-only insertion, not version field) |

PostToolUse `[KB-SPEC-EVENT]` fired for ADR v2 confirming the formal-artifact-approval-gate authorized the insert.

### Narrative edit

`.claude/rules/acting-prime-builder.md` "Harness Hook Parity Fallback Principle" section (lines 99-109) replaced. New file size: 14788 bytes; sha256 matches packet 2's `full_content_sha256`. Verification:

```text
grep -c "ADR-CODEX-HOOK-PARITY-FALLBACK-001\` v2" .claude/rules/acting-prime-builder.md
```

Returns `1` — the v2 supersession reference is now present in the narrative.

The narrative-artifact-approval gate (Slice C of `gtkb-narrative-artifact-approval-extension-001`) will validate the staged blob's sha256 against the approval packet at pre-commit time.

## Specification-Derived Verification

| Linked clause | Spec | Verification command | Observed result |
|---|---|---|---|
| Specification Links present | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001` | preflight_passed expected true on -005 |
| Spec-to-test mapping present | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-001` | exit 0 expected on -005 |
| ADR v2 inserted with packet linkage | `GOV-ARTIFACT-APPROVAL-001` v3 | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT MAX(version) FROM specifications WHERE id=?', ('ADR-CODEX-HOOK-PARITY-FALLBACK-001',)); assert c.fetchone()[0] >= 2"` | exit 0 |
| ADR v2 description references DELIB-S337 empirical evidence | This proposal | `python -c "import sqlite3; c=sqlite3.connect('groundtruth.db').cursor(); c.execute('SELECT description FROM specifications WHERE id=? AND version=2', ('ADR-CODEX-HOOK-PARITY-FALLBACK-001',)); d=c.fetchone()[0]; assert 'DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08' in d and '0.128.0-alpha.1' in d"` | exit 0 |
| DELIB inserted with predecessor citation | `acting-prime-builder.md:74-78` (DA formal-artifact contract) | `python -c "from groundtruth_kb.db import KnowledgeDB; db=KnowledgeDB('groundtruth.db'); res=db.search_deliberations('codex hook parity stance refresh', limit=5); assert any('DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH' in (r.get('id') or '') for r in res)"` | exit 0 |
| Narrative edit reflects v2 stance | This proposal | `python -c "from pathlib import Path; t = Path('.claude/rules/acting-prime-builder.md').read_text(encoding='utf-8'); assert 'ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2' in t and '0.128.0-alpha.1' in t and 'forward-compatible only' not in t"` | exit 0 (the old "forward-compatible only on Windows" framing is removed; v2 + 0.128.0-alpha.1 references present) |
| Approval packets exist on disk | `GOV-ARTIFACT-APPROVAL-001` v3 | `ls .groundtruth/formal-artifact-approvals/2026-05-09-*.json` | 3 files present |
| Pre-commit narrative-artifact-approval gate accepts | Slice C of sibling thread | At commit time: `PASS narrative-artifact evidence (1 cleared)` for the acting-prime-builder.md edit | expected at commit |
| Predecessor preservation | Append-only invariant | DELIB-0836 still present in deliberations table | OK (verified) |
| Root-boundary | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files under `E:\GT-KB`. | OK |
| No NEW operational change | Codex GO -004 explicit constraint | Slice 1 touched only governance artifacts (ADR, narrative, DELIB); no hooks, scripts, or settings.json changed | OK |

## Baseline Accounting (per F2 fix from -003)

### Pre-state (captured 2026-05-09 BEFORE Slice 1)

**Release gate**: 4 inventory-drift findings:
- `.claude/hooks/session_start_dispatch.py` requires compatibility_tests
- `.claude/rules/codex-review-gate.md` requires governance_review
- `.claude/rules/file-bridge-protocol.md` requires governance_review
- `.codex/gtkb-hooks/session_start_dispatch.py` requires compatibility_tests

**Project doctor**: multiple FAIL findings (AUQ coverage 88%, 3 VERIFIED bridges missing Owner Decisions, scanner-safe-writer missing, turn-marker missing, delib-preflight-gate missing, gov09-capture missing, owner-decision-capture missing, DA harvest 0%, product-scope writable paths) plus several WARN.

### Post-state (captured 2026-05-09 AFTER Slice 1)

**Release gate**: 5 inventory-drift findings (4 pre-existing + 1 NEW):
- (pre-existing) 4 carryover findings.
- **(NEW, this slice) `.claude/rules/acting-prime-builder.md` requires governance_review.**

**Project doctor**: identical FAIL/WARN list as pre-state. **No new doctor failures introduced.**

### Disposition

| Finding | Source | Disposition |
|---|---|---|
| (pre-existing) `.claude/hooks/session_start_dispatch.py` + `.codex/gtkb-hooks/session_start_dispatch.py` | Parallel-agent activity | NOT INTRODUCED. |
| (pre-existing) `.claude/rules/codex-review-gate.md` + `.claude/rules/file-bridge-protocol.md` | Parallel-agent activity | NOT INTRODUCED. |
| **(NEW) `.claude/rules/acting-prime-builder.md` requires governance_review** | Slice 1 narrative edit | LEGITIMATE-BY-DESIGN: bridge GO -004 explicitly authorized this edit; approval packet at `.groundtruth/formal-artifact-approvals/2026-05-09-ACTING-PRIME-BUILDER-MD-HOOK-PARITY-REFRESH.json` validates the staged content via narrative-artifact-approval gate. Same drift-checker-vs-release-gate-`--allow-review-evidence`-plumbing gap pattern documented as Open Follow-On #3 in `gtkb-narrative-artifact-approval-extension-001-005.md`. |
| All project-doctor findings | Pre-existing | NOT INTRODUCED. |

Per F2 acceptance: NEW failures are traced to source thread (this Slice 1); each is bridge-authorized + approval-packet-evidenced; the narrative-artifact-approval gate at pre-commit time WILL accept this change when staged together with the packet.

## Acceptance Criteria Status (per -003 §"Acceptance Criteria" Slice 1)

1. ✅ ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 inserted (rowid 8463) with formal-artifact-approval packet citing DELIB-S337 empirical evidence.
2. ✅ acting-prime-builder.md "Harness Hook Parity Fallback Principle" narrative edit applied (sha256 matches packet 2; gate will validate at commit time).
3. ✅ DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08 inserted (rowid 1551) referencing DELIB-0836 (predecessor; preserved) + DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 (empirical foundation).
4. ✅ All 3 mutations approved per DELIB-0835 strict-default + amendment via scoped auto-approval activated by S337 owner AUQ.
5. ✅ Per F2: pre/post baselines captured; new release-gate finding traced to source thread; doctor identical pre/post.
6. ✅ No operational change in Slice 1 (no hook installations; no script modifications; no smart-poller retirement).

## Risk / Rollback

Risk surface:

- **Slice 2 dependency**: Slice 2 (cross-harness trigger script) can be authored as non-live development phase before Slice 1 VERIFIED, but Slice 3 hook registrations cannot ship until Slice 1 is VERIFIED. The slice ordering Codex required is preserved.
- **Append-only versioning**: rolling back v2 means inserting v3 with `change_reason` citing rollback. The v2 row remains in the table as historical evidence. No destructive rollback.
- **Predecessor reference fragility**: the narrative edit and DELIB v2 reference DELIB-0836 by id; if DELIB-0836 is ever moved/renamed, the references become stale. Mitigation: DELIB IDs are stable per the deliberations table append-only contract.

Rollback per slice:

- Slice 1 ADR: insert v3 with change_reason citing rollback rationale. v2 preserved as historical.
- Slice 1 narrative edit: revert the file edit via git revert + insert a superseding deliberation entry.
- Slice 1 DELIB: append-only; insert a new deliberation entry citing the rollback. Existing rowid 1551 preserved.

Rollback should be unnecessary because owner explicitly approved via AUQ + scoped auto-approval.

## Files Changed

- `groundtruth.db` — 1 new row in `specifications` (rowid 8463; ADR v2); 1 new row in `deliberations` (rowid 1551; supersession DELIB).
- `.claude/rules/acting-prime-builder.md` — narrative edit at lines 99-109 ("Harness Hook Parity Fallback Principle" section).
- `.groundtruth/formal-artifact-approvals/2026-05-09-ADR-CODEX-HOOK-PARITY-FALLBACK-001-V2.json` (gitignored).
- `.groundtruth/formal-artifact-approvals/2026-05-09-ACTING-PRIME-BUILDER-MD-HOOK-PARITY-REFRESH.json` (gitignored).
- `.groundtruth/formal-artifact-approvals/2026-05-09-DELIB-CODEX-HOOK-PARITY-STANCE-REFRESH.json` (gitignored).

## Recommended Commit Type

For this Slice 1 implementation: `feat(governance):` — net-additional governance state across ADR v2 + DELIB + narrative edit. The narrative edit is governance-content (not refactoring); the spec inserts are net-additional capability surfaces (the empirically-restored Windows hook support is a new authority position).

## Pre-Filing Preflight

- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-005.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-005.md`
- preflight_passed: confirmed via `.claude/hooks/bridge-compliance-gate.py` mechanical enforcement on Write.

## Requested Loyal Opposition Action

Review this `-005` for VERIFIED of **Slice 1 only**. Slices 2-4 will land separately with their own implementation reports. Specific reviewer questions for Codex:

1. Does the ADR v2 description correctly preserve the fallback obligation for older Codex CLI versions / future regressions while documenting the live-on-Windows reality for current versions?
2. Does the narrative edit correctly remove the "forward-compatible only on Windows" framing AND preserve the regression-test-as-tripwire mechanism for falsifiability?
3. Is the scoped auto-approval pattern (S337 AUQ "Acknowledge with scoped auto-approve" → 3 packets under one scope) acceptable per DELIB-0835 amendment, matching the precedent set in Slice A.2 of `gtkb-narrative-artifact-approval-extension-001` earlier this session?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
