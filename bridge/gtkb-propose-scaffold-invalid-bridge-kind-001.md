NEW

# gtkb-propose-scaffold-invalid-bridge-kind — Fix propose scaffold invalid bridge_kind default

bridge_kind: prime_proposal
Document: gtkb-propose-scaffold-invalid-bridge-kind
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-19 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: antigravity-session-76223e81
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4544

target_paths: ["scripts/gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves a defect in `scripts/gtkb_propose_scaffold.py` (WI-4544) where the scaffold script sets the default `bridge_kind` to `"implementation_proposal"`. However, the bridge compliance gate (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`) only permits `prime_proposal` for implementation proposals. Consequently, any proposal created using the scaffold script is immediately blocked from being written to the bridge.

The fix changes the default `bridge_kind` in `scripts/gtkb_propose_scaffold.py` and its tests from `"implementation_proposal"` to `"prime_proposal"`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The proposal scaffolding tool helps authors compose new bridge proposals. Correcting the default value ensures that proposals pass compliance gates and maintain the integrity of the bridge state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Compliant specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Bounded to project `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification plan executed below.
- `GOV-STANDING-BACKLOG-001` — Bounded to single work item `WI-4544`.

## Prior Deliberations

None.

## Owner Decisions / Input

No owner decisions are required. The standing reliability fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this work stream.

## Requirement Sufficiency

Existing requirements sufficient.

## Spec-Derived Verification Plan

### Automated Tests
- Run the scaffold test suite:
  `python -m pytest platform_tests/scripts/test_gtkb_propose_scaffold.py -q`

### Manual Verification
- Generate a new scaffold with default `bridge_kind` and verify it generates `bridge_kind: prime_proposal`.

## Risk / Rollback

No risk. Reverting the default `bridge_kind` change in `gtkb_propose_scaffold.py` and the tests restores the previous behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-propose-scaffold-invalid-bridge-kind`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
