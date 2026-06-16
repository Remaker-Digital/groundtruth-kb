NEW

# gtkb-harness-c-governance-gate-parity-gap — Harness C Governance Gate Parity and Cloud Config Protection

bridge_kind: implementation_proposal
Document: gtkb-harness-c-governance-gate-parity-gap
Version: 001
Author: Prime Builder
Date: 2026-06-15 UTC

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: B-session
author_model: claude-3-5-sonnet
author_model_version: 20241022
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4534-CLAIM-ROLE-ELIGIBILITY-GUARD-SLICE-A
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4543

target_paths: ["scripts/implementation_start_gate.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

implementation_scope: protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal addresses the governance-gate parity gap on Harness C (Antigravity), where the Antigravity IDE and Gemini CLI harnesses (acting under the Loyal Opposition role) bypass the PreToolUse hooks and modify protected workspace targets directly without active `GO` verdicts or work-intent claims.

We introduce a sync script `scripts/sync_antigravity_rules.py` to copy essential rules files to `.agent/rules/` for Antigravity, and we update `session_self_initialization.py` to invoke the sync at startup/compaction. We update Codex's instructions in `AGENTS.md` with strict self-enforcing preconditions for file mutations. Finally, we update `implementation_start_gate.py` to classify and block unauthorized modifications to cloud/deployment configurations (`Dockerfile`, `docker-compose.yml`, `shopify.app.toml`, and `.env` files).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Governs bridge index structure and workflow state rules.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires proposals to cite valid governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires proposals to specify active projects and work items.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Mandates test verification of all proposed changes.
- `GOV-STANDING-BACKLOG-001` — Governs the prioritization and execution of backlogged work items.

## Prior Deliberations

- `INTAKE-5a61f299` — Intake: Claim-gated implementation-start: holding the GO-implementation claim is required before editing a GO'd thread's target paths. This proposal ensures all harnesses strictly respect this claim requirement.
- `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH` — Owner approved reverting unreviewed Antigravity auto-implementations and re-routing them through the bridge protocol. This proposal establishes the technical hooks and instructions to prevent future protocol bypasses.

## Owner Decisions / Input

Owner approved immediately initiating a clean revert of the bypassed work and starting a formal bridge protocol path (Option 1) on 2026-06-15.

## Requirement Sufficiency

Existing requirements sufficient. The governing specs (`GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`) are sufficient for this implementation.

## Spec-Derived Verification Plan

All modifications will be verified using the following automated tests and manual diagnostic runs:

### Automated Verification
Run the start gate test suite:
```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --no-header -pno:cacheprovider
```
*Expected Result:* All 109 tests pass successfully.

### Manual Verification
Run the start gate script in diagnostic mode to confirm it classifies and blocks unauthorized cloud configurations:
```text
'{"cwd": "E:\\GT-KB", "session_id": "session-1", "tool_name": "apply_patch", "tool_input": {"patch": "*** Begin Patch\n*** Update File: docker-compose.yml\n@@\n+pass\n*** End Patch\n"}}' | python scripts/implementation_start_gate.py --diagnostic
```
*Expected Result:* decision matches "block" with a `cloud-config:docker-compose.yml` classification.

## Risk / Rollback

Low risk. All modified files are in Git. Rollback is a simple single-commit git revert of the changes to `scripts/implementation_start_gate.py` and `scripts/session_self_initialization.py`.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-harness-c-governance-gate-parity-gap` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only).

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
