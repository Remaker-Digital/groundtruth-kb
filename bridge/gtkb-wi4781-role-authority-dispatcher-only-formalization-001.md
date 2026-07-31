NEW

# WI-4781 Role Authority Dispatcher-Only Formalization

bridge_kind: prime_proposal
Document: gtkb-wi4781-role-authority-dispatcher-only-formalization
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-20260629T1600Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4781

target_paths: ["groundtruth.db", "AGENTS.md", "CLAUDE.md", ".claude/rules/operating-role.md", ".claude/rules/canonical-terminology.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py"]

implementation_scope: governance-record, documentation, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

`WI-4781` is Phase 0 of `PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`, now also included in the release-blocking `PROJECT-HARNESS-PARITY-PHASE-2` authorization. Its purpose is to move the corrected role-authority principle into the formal GOV/DCL records before source gates are changed: the harness registry role is authoritative for dispatcher routing only; non-dispatcher behavior uses transcript/session role authority and must not enforce from registry fallback.

This proposal scopes only the formal record update, citation alignment, and focused tests. It does not modify `lo-file-safety-gate.py` or other enforcement gates; that source work remains `WI-4783`. It does not perform the full durable-role terminology purge; that remains `WI-4784`. It does not add the long-term doctor/lint guard; that remains `WI-4785`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected GOV/DCL and rule-surface mutations require bridge `GO`, implementation-start authorization, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing role-authority and bridge requirements before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the active PAUTH, project, work item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove the amended GOV/DCL records and tests express the dispatcher-only authority split.
- `GOV-STANDING-BACKLOG-001` - `WI-4781` is an active P1 backlog item and is part of Harness Parity Phase 2.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH includes `WI-4781` and allows governance-record, documentation, source-adjacent test, and rule-surface work through normal bridge gates.
- `GOV-SESSION-ROLE-AUTHORITY-001` - this is the primary GOV record to amend so the dispatcher-only registry principle has one canonical home.
- `DCL-SESSION-ROLE-RESOLUTION-001` - this DCL must distinguish harness self-role choice from non-dispatcher enforcement-gate role resolution.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - declared/session role authority constrains how non-dispatcher surfaces handle explicit owner role direction.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - records the owner-declared, not agent-detected, role authority principle.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - interactive transcript-defined role persistence remains valid and must not be weakened.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - machine-checkable constraints for interactive role persistence remain in force.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - init-keyword role tokens remain the explicit owner role-direction surface for interactive sessions.

## Prior Deliberations

- `DELIB-20265878` - owner AUQ creating the dispatcher-only role-authority purge project and selecting "capture principle + file as project."
- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` - owner decision that role authority is declared, not detected, and registry mismatch should warn/audit rather than override explicit role direction.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - active release-blocking Harness Parity Phase 2 authorization that includes `WI-4781`.
- `bridge/gtkb-role-authority-declared-not-detected-004.md` - prior VERIFIED ceremony thread that established declared-not-detected role authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` v2 and `DCL-SESSION-ROLE-RESOLUTION-001` v3 - current formal records to amend, not replace with a parallel authority surface.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The needed owner intent is already captured in `DELIB-20265878`, `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613`, and the active `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4781` states the required formal change: make `GOV-SESSION-ROLE-AUTHORITY-001` the canonical home of the dispatcher-only registry principle and amend `DCL-SESSION-ROLE-RESOLUTION-001` so harness self-role choice may use registry hints while enforcement gates must not. The cited owner decisions and active PAUTH are enough to file this formalization slice; later source enforcement changes remain separate work items.

## Proposed Scope

1. Insert new versions of `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` in `groundtruth.db` through the governed KB/spec CLI path.
2. In the GOV record, state the canonical principle directly: the harness registry role is dispatcher-authoritative only; outside dispatcher routing it is at most a non-authoritative hint when no transcript/session role exists.
3. In the DCL record, split contexts explicitly:
   - harness startup/self-orientation may read registry role as a hint or fallback when the transcript has no explicit role direction;
   - non-dispatcher enforcement gates must not enforce from registry fallback and must require explicit session-role evidence or fail open/route to a later gate-specific rule.
4. Update the narrow role-guidance surfaces in `target_paths` to cite the GOV/DCL instead of restating contradictory authority language.
5. Update focused tests so they assert the new formal wording and preserve headless dispatch strict-drop behavior.

## Non-Scope

- Removing registry fallback from `lo-file-safety-gate.py`, implementation-start gates, AUQ routing, or other source enforcement gates. That is `WI-4783`.
- Exhaustive repository-wide terminology replacement. That is `WI-4784`.
- Doctor/lint enforcement for future regrowth. That is `WI-4785`.
- Changing dispatcher recipient selection or durable registry schema.
- Changing owner-approved headless dispatch strict-drop rules for misdirected canonical dispatch envelopes.

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-SESSION-ROLE-RESOLUTION-001` | `gt spec show GOV-SESSION-ROLE-AUTHORITY-001 --json`; `gt spec show DCL-SESSION-ROLE-RESOLUTION-001 --json` | New versions carry the dispatcher-only registry principle and the self-role-choice vs enforcement-gate split. |
| `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001`; `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` | `python -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short` | Declared role authority tests remain green or are updated to assert registry mismatch is warning/audit, not override. |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`; `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | `python -m pytest platform_tests/hooks/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution.py -q --tb=short` | Interactive transcript/session role persistence remains intact after the formal wording update. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --tb=short` | Headless dispatch still strict-drops misdirected role tokens; dispatcher authority is preserved. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table forward with exact command outputs plus `gt spec show` diffs/summaries. | Loyal Opposition can verify the formal records against executed evidence. |

## Risk / Rollback

Risk: wording could accidentally remove the legitimate dispatcher role authority needed for headless routing. Mitigation: preserve strict-drop and dispatcher-routing tests in this slice and state the dispatcher exception directly in the GOV/DCL records.

Risk: this Phase 0 proposal may be mistaken for permission to modify all gate code immediately. Mitigation: source enforcement changes are explicitly non-scope and remain tracked by `WI-4783`.

Rollback: insert a superseding GOV/DCL version restoring the previous wording and revert any documentation/test commit. Formal record history remains append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4781-role-authority-dispatcher-only-formalization`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

docs:

The expected implementation is primarily formal GOV/DCL record and role-guidance wording plus focused tests; source gate behavior changes are deliberately left to later work.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
