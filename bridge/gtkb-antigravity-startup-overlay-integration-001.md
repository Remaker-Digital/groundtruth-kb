NEW

# gtkb-antigravity-startup-overlay-integration — Load active role overlays in Antigravity startup sequence

bridge_kind: prime_proposal
Document: gtkb-antigravity-startup-overlay-integration
Version: 001
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-20 UTC

author_identity: prime-builder/antigravity
author_harness_id: C
author_session_context_id: cb447a9a-62e4-4fbe-8f6f-ef77dee8e1d3
author_model: gemini-2.0-pro
author_model_version: 2.0
author_model_configuration: default

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PAUTH-PROJECT-HARNESS-PARITY-ANTIGRAVITY-OVERLAY-BOUNDARY
Project: PROJECT-HARNESS-PARITY
Work Item: WI-4695

target_paths: ["AGENTS.md", "config/agent-control/SESSION-STARTUP-INDEX.md"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal updates the Antigravity harness startup and file safety rules in [AGENTS.md](file:///E:/GT-KB/AGENTS.md) and [SESSION-STARTUP-INDEX.md](file:///E:/GT-KB/config/agent-control/SESSION-STARTUP-INDEX.md) to load the active role overlay file ([PRIME-BUILDER-STARTUP-OVERLAY.md](file:///E:/GT-KB/config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md) or [LOYAL-OPPOSITION-STARTUP-OVERLAY.md](file:///E:/GT-KB/config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md)) at session startup. 

This ensures that Antigravity is always aware of the boundary guidelines for its current active role (resolved from the harness registry or transcript override). Furthermore, this proposal amends [AGENTS.md](file:///E:/GT-KB/AGENTS.md) to add an explicit boundary check requiring the active agent to verify that its current role aligns with the target bridge file status before writing any bridge files, preventing future role-confusion defects. All modified files are located in-root under the project root at `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Enforces that the numbered bridge file chain drives active work and that assistants must remain in their correct role boundaries when writing bridge files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Constrains the proposal to explicitly cite relevant specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires mapping the work item, project, and pauth triple.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification of compliance via git status and local syntax checking.
- `GOV-STANDING-BACKLOG-001` — Backlog capturing of candidate work under `WI-4695`.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — Ensures Antigravity loads role overlays while still respecting the low-overhead token-budget optimizations.

## Prior Deliberations

- `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` — Owner decision directing that Antigravity load active role overlays in its startup sequence and execute first-line verification checks before writing bridge files to avoid role-confusion defects.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — Establishes proposal formatting standards which this document conforms to.

## Owner Decisions / Input

Authorized by the owner decision `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` recorded in this session.

## Requirement Sufficiency

New or revised requirement required before implementation. The requirement is defined by the owner decision `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` to load active role overlays in Antigravity's startup path.

## Specification-Derived Verification Plan

No code test suite is run since this is a documentation/governance change. Verification is performed by checking the correctness of the changes in git:

| Linked spec | Verification | Expected result |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run git status. | Only `AGENTS.md` and `config/agent-control/SESSION-STARTUP-INDEX.md` are modified in the working tree. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Review changes to `AGENTS.md` and `SESSION-STARTUP-INDEX.md`. | Startup sequence loads active overlays, and first-line verification checks are documented. |

## Risk / Rollback

Risk is low. The changes update only rule and startup-index markdown files, which are non-executable documentation. Rollback is a single commit revert of `AGENTS.md` and `config/agent-control/SESSION-STARTUP-INDEX.md`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-antigravity-startup-overlay-integration`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs:` — changes only documentation/rule files.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
