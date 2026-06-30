NEW

# WI-4783 Session Role Gate Fallback Purge

bridge_kind: prime_proposal
Document: gtkb-wi4783-session-role-gate-fallback-purge
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1679-e87b-7df1-86d8-34bf254c61bf
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4783

target_paths: [".claude/hooks/lo-file-safety-gate.py", ".claude/hooks/workstream-focus.py", "scripts/session_role_resolution.py", "scripts/gtkb_session_id.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/hooks/test_lo_file_safety_gate.py"]

implementation_scope: source, tests, hook behavior
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4783` is the source-gate follow-up to the VERIFIED `WI-4781` formalization. The owner-approved principle is now formalized: the durable harness registry is dispatcher-authoritative only. Non-dispatcher enforcement gates must not enforce Loyal Opposition restrictions from a registry fallback when no explicit transcript/session role is present.

This proposal removes that fallback from `lo-file-safety-gate.py`, preserves explicit session/envelope LO enforcement, and fixes the `::init gtkb pb|lo` marker propagation path so the shared resolver and the writer use the same per-session authority. It is proposal-only; no protected source mutation is performed in this run.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected hook/source/test changes require this NEW proposal, Loyal Opposition GO, implementation-start authorization, a post-implementation report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the role-authority and bridge requirements before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the active PAUTH, project, work item, and inline JSON `target_paths` are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps each governing requirement to concrete tests.
- `GOV-STANDING-BACKLOG-001` - `WI-4783` is an open P1 standing-backlog item.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active Phase 2 PAUTH includes `WI-4783` and allows source, test, hook, config, and documentation work through normal bridge gates.
- `GOV-SESSION-ROLE-AUTHORITY-001` - the durable registry is dispatcher-authoritative only; non-dispatcher enforcement must use transcript/session role authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - the shared resolver must distinguish explicit session authority from fallback state.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - role authority is owner-declared, not inferred from stale or mismatched registry state.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - preserves the declared-not-detected architecture decision.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - explicit interactive role survives compaction/resume within the same context.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - the marker/envelope contract must remain machine-checkable.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - `::init gtkb pb|lo` remains the canonical owner role-direction surface.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface hook changes must declare cross-harness behavior or a typed waiver.
- `ADR-CROSS-HARNESS-PARITY-001` - parity decisions are explicit and auditable across supported harnesses.

## Prior Deliberations

- `DELIB-20265878` - owner AUQ creating the dispatcher-only role-authority purge project and selecting "capture principle + file as project."
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - active release-blocking Phase 2 authorization that includes `WI-4783`.
- `bridge/gtkb-wi4781-role-authority-dispatcher-only-formalization-004.md` - VERIFIED formalization of the dispatcher-only registry principle; explicitly leaves source enforcement-gate changes to `WI-4783`.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-001.md` - prior shared resolver slice that made `scripts/session_role_resolution.py` the deterministic read path for interactive role resolution.
- `bridge/gtkb-wi4540-per-session-role-marker-context-envelope-004.md` - prior GO/implementation lineage for per-session role marker continuity.
- `INTAKE-b4928376` - intake candidate noting bridge review eligibility is harness-agnostic and durable role is a fallback, not a review/verdict gate.

## Owner Decisions / Input

No new owner decision is required before filing this proposal. The needed owner direction is already recorded in `DELIB-20265878`, and bounded implementation is authorized by `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`.

## Requirement Sufficiency

Existing requirements sufficient.

`WI-4783` states the required source behavior directly: remove the registry fallback in `lo-file-safety-gate.py`, enforce only on explicitly resolved session LO role, fail open when no explicit role exists, fix `::init gtkb pb|lo` marker propagation, and audit other non-dispatcher consumers for the same leak. `WI-4781` has already formalized the governing GOV/DCL records.

## Proposed Scope

1. In `.claude/hooks/lo-file-safety-gate.py`, stop treating `durable_*` resolver outcomes as LO enforcement authority. If the shared resolver returns an explicit session/envelope LO role, enforce the LO file-safety gate; if it returns durable fallback, no role state, resolver import failure, or malformed state, fail open for this hook.
2. Preserve dispatcher/headless routing authority elsewhere. This proposal does not weaken canonical dispatch strict-drop behavior or durable role selection for dispatcher targets.
3. In `.claude/hooks/workstream-focus.py`, `scripts/session_role_resolution.py`, and `scripts/gtkb_session_id.py`, repair any drift that prevents `::init gtkb pb|lo` from writing the same per-session marker/envelope that `resolve_interactive_session_role` reads.
4. Add or update focused tests proving:
   - explicit `::init gtkb lo` still makes LO file-safety restrictions apply;
   - absent, invalid, stale, or durable-only role evidence does not make `lo-file-safety-gate.py` block protected writes;
   - explicit `::init gtkb pb` and `::init gtkb lo` write/read the same per-session marker authority;
   - the resolver remains read-only and does not mutate marker or registry state.
5. Audit implementation-start gate, changed_by attribution, AUQ routing, and other non-dispatcher consumers for durable-registry-as-authority leakage. If a material leak is found outside this target set, file a follow-up rather than silently expanding scope.

## Non-Scope

- Mutating `groundtruth.db` GOV/DCL records. That formalization is already handled by VERIFIED `WI-4781`.
- Changing dispatcher recipient selection, durable registry schema, harness identity files, or headless strict-drop semantics.
- Resolving unrelated dirty worktree state. At proposal time, `platform_tests/hooks/test_session_role_resolution.py` is already modified by another workstream; implementation must re-check target dirt before editing.
- Credential lifecycle, provider settings, production deployment, or GitHub settings changes.

## Cross-Harness Disposition

This proposal targets Claude hook files plus shared Python resolver/session-id modules. No owner-approved typed waiver is requested or claimed.

| Harness | Disposition |
| --- | --- |
| Claude Code | Directly applicable. `.claude/hooks/lo-file-safety-gate.py` and `.claude/hooks/workstream-focus.py` are the primary hook surfaces for this fix. |
| Codex | Behaviorally applicable through shared resolver/session-id modules and bridge helper compliance paths. No `.codex/gtkb-hooks/**` target is proposed because this defect is in the Claude hook gate and shared resolver contract, not a Codex-specific hook implementation. |
| Antigravity | Behaviorally applicable only where Antigravity consumes shared resolver/session-id modules. No Antigravity-specific hook file is mutated in this slice. |
| Cursor | Behaviorally applicable only where Cursor consumes shared resolver/session-id modules. No Cursor-specific hook file is mutated in this slice. |
| Ollama / OpenRouter dispatch harnesses | Dispatcher routing remains out of scope. The proposal preserves headless strict-drop behavior and does not change provider dispatch selection. |

## Spec-Derived Verification Plan

| Specification | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-SESSION-ROLE-RESOLUTION-001` | `python -m pytest platform_tests/hooks/test_session_role_resolution.py -q --tb=short` | Resolver preserves explicit marker/envelope precedence and treats durable role as fallback, not non-dispatcher enforcement authority. |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`; `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | `python -m pytest platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short` | `::init gtkb pb|lo` writes the per-session marker/envelope that the resolver reads. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` | `python -m pytest platform_tests/hooks/test_lo_file_safety_gate.py -q --tb=short` | LO file-safety enforcement applies only for explicit LO session authority and fails open for durable-only fallback. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_strict_drop_misdirected_headless_dispatch.py -q --tb=short` plus bridge-compliance audit on the filed proposal | Dispatcher/headless strict-drop behavior is unchanged and the harness-surface disposition gate passes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this table forward with exact command output. | Loyal Opposition can verify source changes against executed evidence. |

## Risk / Rollback

Risk: removing the fallback too broadly could let a genuine interactive Loyal Opposition session edit protected files. Mitigation: keep explicit marker/envelope LO enforcement and add tests that show LO still blocks when the role is explicit.

Risk: marker propagation changes could break headless dispatcher behavior. Mitigation: preserve dispatcher strict-drop tests and keep dispatcher routing out of scope.

Rollback: revert the single implementation commit and restore the previous hook/resolver/test behavior; no MemBase mutation is proposed in this slice.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4783-session-role-gate-fallback-purge`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

This is a defect repair in hook/source role enforcement plus focused regression tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
