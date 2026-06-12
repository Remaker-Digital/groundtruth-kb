REVISED

bridge_kind: implementation_report
Document: gtkb-fab-09-safety-gate-registration
Version: 009
Responds-To: bridge/gtkb-fab-09-safety-gate-registration-008.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4421
Project Authorization: PAUTH-FAB09-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: [".claude/settings.json", ".codex/hooks.json", ".claude/hooks/owner-decision-capture.py", ".claude/hooks/gov09-capture.py", ".claude/hooks/_delib_common.py", ".claude/hooks/scheduler.py", ".claude/SCHEDULE.md", ".claude/hooks/turn-marker.py", ".claude/hooks/delib-preflight-gate.py", "CLAUDE.md", ".claude/rules/canonical-terminology.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/templates/hooks/_delib_common.py", "groundtruth-kb/templates/hooks/owner-decision-capture.py", "groundtruth-kb/templates/hooks/gov09-capture.py", "groundtruth-kb/templates/hooks/turn-marker.py", "groundtruth-kb/templates/hooks/delib-preflight-gate.py", ".groundtruth/formal-artifact-approvals/2026-06-12-fab09-canonical-terminology.json", "platform_tests/scripts/test_fab09_safety_gate_registration.py"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

---

# FAB-09 — Safety-Gate Registration Normalization — REVISED Post-Implementation Report (v009)

Implements the GO'd proposal `bridge/gtkb-fab-09-safety-gate-registration-003.md` (GO at `-004`). This REVISED report addresses the single finding in the NO-GO at `-008`.

## Revision Scope

Addresses FINDING P1-001 from `bridge/gtkb-fab-09-safety-gate-registration-008.md` (NO-GO):

**FINDING P1-001 (canonical terminology approval packet is invalid — missing `source_ref` field):** The approval packet at `.groundtruth/formal-artifact-approvals/2026-06-12-fab09-canonical-terminology.json` lacked the required `source_ref` field, causing both `check_narrative_artifact_evidence.py` and `validate_formal_artifact_packet.py` to reject it. Resolved by regenerating the packet with `source_ref: gtkb-fab-09-safety-gate-registration` and recomputing `full_content_sha256` against the current live file content. The narrative evidence checker now passes.

No source code, test, or configuration changes were required. This revision is packet-fix-only.

## Bridge Protocol Compliance

This report is filed at `bridge/gtkb-fab-09-safety-gate-registration-009.md` with a matching `REVISED:` line inserted at the top of the `gtkb-fab-09-safety-gate-registration` document entry in `bridge/INDEX.md`. All prior versions (`-001` through `-008`) remain on disk per bridge append-only protocol. No prior bridge files were deleted or rewritten.

## Summary of Changes

All changes are carried forward from -007 (the prior REVISED report). The implementation scope is unchanged:

1. **Hook registration normalization:** `destructive-gate.py`, `credential-scan.py`, `owner-decision-capture.py`, `gov09-capture.py`, `_delib_common.py`, `scheduler.py`, `turn-marker.py`, and `delib-preflight-gate.py` registered in both `.claude/settings.json` and `.codex/hooks.json` at the correct event positions.

2. **Template parity:** `_delib_common.py`, `owner-decision-capture.py`, `gov09-capture.py`, `turn-marker.py`, and `delib-preflight-gate.py` have matching templates under `groundtruth-kb/templates/hooks/`.

3. **Scanner-safe-writer glossary entry:** `.claude/rules/canonical-terminology.md` updated with explicit credential-scan/scanner-safe-writer naming. Protected narrative approval packet created and force-added.

4. **Doctor checks:** Two new checks in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`:
   - `_check_safety_gate_registration`: WARNING when safety hooks missing from PreToolUse.
   - `_check_capture_hook_stub_status`: WARNING when capture hooks appear stubbed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed at `bridge/gtkb-fab-09-safety-gate-registration-009.md` with a matching entry in `bridge/INDEX.md`; all prior bridge versions remain append-only on disk.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4421 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — canonical-terminology.md edit carries approval packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all edits are in-root; nothing relocated.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — safety-gate registration is a mechanical enforcement surface.

## Spec-to-Test Mapping

| Spec / requirement | Derived test | Result |
|---|---|---|
| Hook registration normalization | `test_destructive_gate_registered`, `test_credential_scan_registered`, `test_capture_hooks_registered`, `test_codex_hooks_registered` (4 tests) | PASS |
| Template parity | `test_template_parity_delib_common`, `test_template_parity_owner_decision_capture`, `test_template_parity_gov09_capture`, `test_template_parity_turn_marker`, `test_template_parity_delib_preflight_gate` (5 tests) | PASS |
| Scanner-safe-writer glossary | `test_canonical_terminology_scanner_safe_writer`, `test_canonical_terminology_credential_scan_entry` (2 tests) | PASS |
| Doctor checks | `test_doctor_safety_gate_check_exists`, `test_doctor_safety_gate_check_detects_missing`, `test_doctor_capture_hook_stub_check_exists`, `test_doctor_capture_stub_detects_stub`, `test_doctor_capture_stub_passes_real` (5 tests) | PASS |
| Hook event positions | `test_scheduler_in_userpromptsubmit`, `test_turn_marker_in_stop`, `test_delib_preflight_in_pretooluse` (3 tests) | PASS |
| Functional surface | `test_destructive_gate_importable`, `test_credential_scan_importable`, `test_schedule_md_exists`, `test_settings_json_parseable`, `test_codex_hooks_json_parseable`, `test_delib_preflight_gate_importable` (6 tests) | PASS |

## Verification Commands and Observed Results

```
python -m pytest platform_tests/scripts/test_fab09_safety_gate_registration.py -q --tb=short
  -> 25 passed in 0.49s

python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_fab09_safety_gate_registration.py
  -> All checks passed!

python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_fab09_safety_gate_registration.py
  -> 2 files already formatted

python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md --json
  -> {"status": "pass", "findings": [], "cleared": [".claude/rules/canonical-terminology.md"]}
```

## Acceptance Criteria Check

1. All 8 hooks registered in both `.claude/settings.json` and `.codex/hooks.json`. PASS
2. 5 template twins verified byte-for-byte. PASS
3. Scanner-safe-writer glossary entry with explicit hook naming. PASS
4. Two doctor checks (`_check_safety_gate_registration`, `_check_capture_hook_stub_status`) added. PASS
5. 25 regression tests passing. PASS
6. Ruff lint and format clean. PASS
7. Narrative approval packet for canonical-terminology.md valid and force-added. PASS
8. (v009) Approval packet includes `source_ref` field; narrative evidence checker passes. PASS

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory.
- `DELIB-FAB09-REMEDIATION-20260610` — owner dispositions.
- `bridge/gtkb-fab-09-safety-gate-registration-003.md` / `-004.md` — proposal and GO.
- `bridge/gtkb-fab-09-safety-gate-registration-006.md` — first NO-GO (2 findings, both addressed in -007).
- `bridge/gtkb-fab-09-safety-gate-registration-008.md` — second NO-GO (1 finding: missing `source_ref` in approval packet).

## Owner Decisions / Input

Fix-scope owner decisions were collected via `AskUserQuestion` on 2026-06-10 and persisted to `DELIB-FAB09-REMEDIATION-20260610`. The owner's 2026-06-12 standing auto-approve-inline authorization governs the canonical-terminology narrative-approval packet. No new owner decision was required for this revision.

## Files Changed

| File | Change |
|------|--------|
| `.claude/settings.json` | Hook registration normalization |
| `.codex/hooks.json` | Hook registration normalization |
| `.claude/hooks/owner-decision-capture.py` | Scaffold stub (registered) |
| `.claude/hooks/gov09-capture.py` | Scaffold stub (registered) |
| `.claude/hooks/_delib_common.py` | Shared helper module |
| `.claude/hooks/scheduler.py` | Registered in UserPromptSubmit |
| `.claude/SCHEDULE.md` | Pre-planned prompt schedule |
| `.claude/hooks/turn-marker.py` | Registered in Stop |
| `.claude/hooks/delib-preflight-gate.py` | Registered in PreToolUse |
| `CLAUDE.md` | No FAB-09 change (already correct) |
| `.claude/rules/canonical-terminology.md` | Scanner-safe-writer glossary entry (approval packet) |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | Two new doctor checks |
| `groundtruth-kb/templates/hooks/_delib_common.py` | Template twin |
| `groundtruth-kb/templates/hooks/owner-decision-capture.py` | Template twin |
| `groundtruth-kb/templates/hooks/gov09-capture.py` | Template twin |
| `groundtruth-kb/templates/hooks/turn-marker.py` | Template twin |
| `groundtruth-kb/templates/hooks/delib-preflight-gate.py` | Template twin |
| `.groundtruth/formal-artifact-approvals/2026-06-12-fab09-canonical-terminology.json` | Regenerated with `source_ref` field + correct content hash |
| `platform_tests/scripts/test_fab09_safety_gate_registration.py` | 25 regression tests |

## Recommended Commit Type

`feat:` — net-new doctor checks, hook registrations, template twins, and glossary entry constitute new safety-gate infrastructure.

## Requirement Sufficiency

Existing requirements sufficient. All acceptance criteria from the GO at `-004` are covered by the 25 tests and the narrative-approval packet. The revision addresses only the packet-evidence finding from the NO-GO at `-008`; no new requirements were needed.
