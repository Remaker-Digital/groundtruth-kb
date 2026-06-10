REVISED

# Implementation Proposal - Project Authorization Spec-Amendment Approval Gate - REVISED-2 (WI-3313)

bridge_kind: prime_proposal
Document: gtkb-project-auth-spec-amendment-gate
Version: 005
Responds to: bridge/gtkb-project-auth-spec-amendment-gate-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3313

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/tests/test_db.py", "groundtruth.db"]

This REVISED-2 addresses the NO-GO at `bridge/gtkb-project-auth-spec-amendment-gate-004.md`:

- **F1 (P1/blocking)** - the REVISED-1 required verification command named `groundtruth-kb/tests/test_governance_approval_packet.py`, a file that does not exist in the live checkout and is not in `target_paths`; the run command was therefore non-executable -> **closed** by adopting NO-GO option 2: ALL tests (including the IP-2 helper coverage) live in the already-authorized `groundtruth-kb/tests/test_db.py`, and the verification command names only authorized files. The phantom test file is removed from both the verification command and the scope.

IP-1 (real packet-evidence validation), IP-2 (helper extraction), and IP-4 (no spec promotion) carry forward from REVISED-1 unchanged. IP-3 (tests) is revised below to keep every test in `test_db.py`.

## Why Option 2 (not a new test file)

The NO-GO offered two paths: (1) add `test_governance_approval_packet.py` to `target_paths`, or (2) keep all tests in `test_db.py` and drop the missing file from the run command. REVISED-2 takes option 2:

- IP-2's helpers (`parse_packet_path_from_change_reason`, `packet_covers_amendment`) are exercised both directly and through the DB-layer validator. The IP-3 test table already routes every test through `groundtruth-kb/tests/test_db.py`; the helper-isolation assertions are added as additional test functions in that same file (importing the helpers from `groundtruth_kb.governance.approval_packet`).
- Option 2 adds no new file, keeps the scope minimal, and makes the verification command executable from the existing authorized `target_paths`.

## Claim

`KnowledgeDB.insert_project_authorization()` must reject any version that mutates `included_spec_ids` or `excluded_spec_ids` (relative to the prior version) unless `change_reason` carries a path to a real, owner-approved formal-artifact-approval packet that covers the mutation. Substring text alone is insufficient.

## In-Root Placement Evidence

All 4 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - source spec; v1 specified 2026-05-14.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - sibling spec (WI-3312); covers initial authorization linkage.
- `GOV-ARTIFACT-APPROVAL-001` - approval-packet workflow that this gate enforces.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract this aligns with.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3313 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-project-auth-spec-amendment-gate-002.md` - first NO-GO (closed by REVISED-1).
- `bridge/gtkb-project-auth-spec-amendment-gate-004.md` - second NO-GO (closed by this REVISED-2).

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; this REVISED-2 is a mechanical scope correction.

## Requirement Sufficiency

Existing requirements sufficient. The F1 fix uses the existing `validate_packet()` shared validator already trusted by `formal-artifact-approval-gate.py` - no new validation invented.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3313); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (real packet validation) + IP-2 (helper extraction) + IP-3 (tests) + IP-4 (no promotion) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-project-auth-spec-amendment-gate-005.md`; `REVISED:` line prepended. Prior lines (`-004` NO-GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved.

## Proposed Scope

### IP-1: Real packet-evidence validation in insert_project_authorization()

Unchanged from REVISED-1. In `groundtruth-kb/src/groundtruth_kb/db.py`, `insert_project_authorization()` (or its validation helper) detects a `linked_specs` mutation relative to the prior version and requires `change_reason` to cite a real packet path that: (1) is extracted by regex, (2) resolves inside `.groundtruth/formal-artifact-approvals/` under the project root, (3) exists as a file, (4) parses as JSON and passes `validate_packet()`, (5) has `approved_by == "owner"`, and (6) covers the amendment (mentions the project/authorization id and every added/removed spec id). Any failure raises `ValueError` citing `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001/CLAUSE-AMENDMENT-APPROVAL-REQUIRED`.

### IP-2: Helper extraction (refactor for testability)

Unchanged from REVISED-1. In `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`, expose `parse_packet_path_from_change_reason(change_reason) -> Path | None` and `packet_covers_amendment(packet, project_id, authorization_id, added_specs, removed_specs) -> tuple[bool, str]`. The DB-layer validator calls these helpers; tests exercise them in isolation within `test_db.py`.

### IP-3: Tests - all in test_db.py

ALL tests live in `groundtruth-kb/tests/test_db.py` (already in `target_paths`). DB-layer scenario tests plus helper-isolation tests that import `parse_packet_path_from_change_reason` and `packet_covers_amendment` directly from `groundtruth_kb.governance.approval_packet`. No new test file is created.

### IP-4: No spec promotion at proposal-filing time

`DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` stays at `specified`. Promotion only on VERIFIED.

## Specification-Derived Verification Plan

Tests in `groundtruth-kb/tests/test_db.py`:

| Clause / scenario | Test |
|---|---|
| spec mutation + no packet path -> blocked | `test_amend_specs_without_packet_path_raises` |
| spec mutation + fake/non-existent path -> blocked | `test_amend_specs_with_fake_path_raises` |
| spec mutation + outside-root path -> blocked | `test_amend_specs_with_outside_root_path_raises` |
| spec mutation + malformed JSON -> blocked | `test_amend_specs_with_malformed_json_raises` |
| spec mutation + schema-invalid packet -> blocked | `test_amend_specs_with_schema_invalid_packet_raises` |
| spec mutation + non-owner-approved packet -> blocked | `test_amend_specs_with_non_owner_approved_packet_raises` |
| spec mutation + packet not mentioning project -> blocked | `test_amend_specs_packet_does_not_cover_project_raises` |
| spec mutation + packet not mentioning added spec -> blocked | `test_amend_specs_packet_does_not_cover_added_spec_raises` |
| spec mutation + valid covering packet -> passes | `test_amend_specs_with_covering_packet_succeeds` |
| batch packet covering multiple amendments -> passes per-call | `test_amend_specs_batch_packet_multiple_projects` |
| initial version (no prior) -> no packet required | `test_authorize_initial_version_no_packet_required` |
| status-only change (no spec mutation) -> no packet required | `test_authorize_status_change_no_packet_required` |
| excluded_spec_ids mutation also gated | `test_amend_excluded_specs_also_gated` |
| helper: path parse from change_reason | `test_parse_packet_path_from_change_reason_helper` |
| helper: packet coverage predicate | `test_packet_covers_amendment_helper` |

Clause mapping: `CLAUSE-AMENDMENT-APPROVAL-REQUIRED` positive (`test_amend_specs_with_covering_packet_succeeds`); negative F1 cluster (the 8 blocked-case tests); `CLAUSE-BATCH-APPROVAL-PERMITTED` (`test_amend_specs_batch_packet_multiple_projects`); grandfathering (`test_authorize_initial_version_no_packet_required`); status-only exemption (`test_authorize_status_change_no_packet_required`); both linkage sets gated (`test_amend_excluded_specs_also_gated`).

Required verification command (F1 - executable from authorized files only):

```text
python -m pytest groundtruth-kb/tests/test_db.py -v
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; 15 tests PASS (8 negative cases + positive + batch + 2 grandfathering/exemption + excluded-set + 2 helper-isolation).
- The verification command runs entirely from `target_paths`-authorized files; no missing-file collection error.
- IP-4: `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` stays at `specified` at proposal time.
- No regression in the existing `test_db.py` suite or the formal-artifact-approval gate tests.
- Both preflights PASS.

## Risks / Rollback

- Risk: legacy amendment commits with substring-only packet citations will fail under the new gate. Mitigation: only NEW insertions are gated; existing data unchanged on read.
- Risk: coverage check may false-negative when a packet legitimately covers an amendment with different ID phrasing. Mitigation: per-spec-ID + project-or-auth-ID substring search; tests document expected phrasing.
- Risk: regex anchoring on packet path may fail on unusual separators. Mitigation: regex accepts `/` and `\`.
- Rollback: revert `_validate_spec_amendment_approval_packet` (single-function scope) + helper additions in `approval_packet.py`.

## Recommended Commit Type

`feat` - real packet-evidence gate replacing the substring check; ~80 LOC DB + ~30 LOC helpers + ~210 LOC tests + fixtures.
