NEW

# gtkb-role-authority-boundary-scoped-correction (Slice 1) — durable registry dispatcher-only boundary correction

bridge_kind: prime_proposal
Document: gtkb-role-authority-boundary-scoped-correction
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-02T19:10:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-02T00-26-35Z
author_model: Codex (model id not exposed by local session envelope)
author_model_version: not-exposed-by-session-envelope
author_model_configuration: desktop Codex session, GT-KB Prime Builder via owner init keyword

Project Authorization: PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4785

target_paths: ["groundtruth.db", "CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-role.md", ".claude/hooks/lo-file-safety-gate.py", "scripts/session_role_resolution.py", "scripts/bridge_work_intent_registry.py", "scripts/_kb_attribution.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb/**", "groundtruth-kb/tests/**", "platform_tests/**", "config/agent-control/**"]

implementation_scope: governance | source | tests | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal files the scoped correction program Mike approved on 2026-07-02:
the durable role in `harness-state/harness-registry.json` is dispatcher
authority only for headless dispatch routing, while non-dispatcher behavior
surfaces must consume the resolved session role. The session-envelope/session
role resolver may consult the durable registry only as a no-explicit-role,
non-binding fallback; hooks, gates, CLIs, skills, doctor checks, tests,
MemBase attribution, focus menus, AUQ routing, and bridge claim metadata must
not fresh-read the durable registry as behavior authority.

The immediate evidence is live and reproducible: this Codex session envelope is
open as Prime Builder (`harness-state/codex/session-envelope.json`), yet the
shared `.claude/session/active-session-role.json` is absent and
`python scripts/bridge_claim_cli.py claim gtkb-role-authority-boundary-scoped-correction --session-id A-2026-07-02T00-26-35Z`
acquired a claim with `acting_role: null`. Earlier handoff evidence reported
the worse form of the same defect, where a Prime Builder interactive session
was stamped or blocked as Loyal Opposition after falling back to durable state.

Slice 1 is deliberately bounded: update the governing GOV/DCL wording if the
July 2 rule is stricter than the current text, audit the named non-dispatcher
surfaces, fix only confirmed leaks, and add regression guards so durable
registry authority cannot regrow outside dispatcher-owned paths.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001` — canonical authority boundary: durable registry authority belongs to headless dispatcher routing; non-dispatcher behavior must be governed by resolved session role.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic resolution table and assertion surface for session role consumers; this proposal sharpens non-dispatcher fallback behavior if current rows are too permissive.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — architectural basis for transcript/session role overriding durable assignment in interactive contexts.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` — persistence rule for owner-declared interactive role across compaction, resume, and contiguous startup-like boundaries.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` — executable constraints for interactive role persistence and the requirement that enforcement changes proceed through separate bridge review.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal and any LO response must use the versioned bridge file chain plus dispatcher/TAFE state as the live workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation proposals must cite applicable governing specs before they are eligible for review and implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this implementation-targeting proposal includes live project, work item, and PAUTH metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must derive tests from the linked role-authority specifications and include per-spec evidence.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — because `.claude/hooks/**` is in target scope, the proposal must declare cross-harness behavioral parity or an owner-approved typed waiver.
- `ADR-CROSS-HARNESS-PARITY-001` — architectural basis for keeping harness-specific hook and skill behavior aligned when one harness surface is changed.

## Prior Deliberations

- `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` — establishes the owner-declared, not agent-detected, role model and separates dispatcher routing authority from interactive session role.
- `DELIB-20265878` — owner chose to capture the dispatcher-only registry principle and file the role-authority purge project; this created the existing Phase 0-4 work items.
- `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A` — owner approved Option A, "Approve as scoped", for the July 2 durable-role authority boundary audit and correction program.

## Owner Decisions / Input

Owner approval is already captured in `DELIB-20260702-ROLE-AUTHORITY-SCOPED-APPROVAL-A`.
That deliberation authorized the scoped boundary program, attaching the live
WI-4868 claim defect to `PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE`,
and creating bounded implementation authorization
`PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702`.

No additional owner decision is required before LO review. Any formal GOV/DCL
mutation performed during implementation must still carry the normal
formal-artifact approval packet evidence before insertion/update.

## Requirement Sufficiency

New or revised requirement required before source implementation.

The current GOV/DCL family already states the dispatcher-only principle, but
the July 2 owner clarification is stricter: no GT-KB part may reference the
durable registry role except the dispatcher for headless routing and the
session-envelope role resolver as a no-explicit-role, non-binding fallback.
Slice 1 must first sharpen `GOV-SESSION-ROLE-AUTHORITY-001` and
`DCL-SESSION-ROLE-RESOLUTION-001` if their current wording leaves room for
behavior gates or attribution paths to re-read durable state as authority.
Only after that formal wording is in place should source/test corrections be
implemented against it.

## Cross-Harness Disposition

No typed waiver is requested.

Applicable harness disposition:
- Claude Code: `.claude/hooks/lo-file-safety-gate.py` is a direct target only
  if the audit confirms it still leaks durable-registry authority or carries
  dead/contradictory role-resolution code. Any Claude hook change must be
  covered by `platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py`.
- Codex: Codex does not receive a separate Claude PreToolUse hook mutation in
  this slice. Behavioral parity is supplied through shared resolver/registry
  code (`scripts/session_role_resolution.py`,
  `scripts/bridge_work_intent_registry.py`, `scripts/_kb_attribution.py`) and
  the Codex bridge-propose helper path. If implementation discovers a Codex
  harness-surface file needs mutation, the target list and parity tests must be
  updated before implementation report.
- Cursor, Antigravity, Ollama, and OpenRouter: no direct harness-surface file is
  targeted in Slice 1. Their parity obligation is that shared role-resolution
  and work-intent behavior not regress; targeted tests must cover shared code
  rather than relying on a Claude-only hook behavior.

Parity acceptance: there must be no role-authority rule that applies only to
Claude when the same behavior-gating decision is reachable by another harness
through shared CLI, dispatcher, attribution, or bridge-claim code. Any found
exception requires either an implementation change in the relevant harness
surface or a new owner-approved typed waiver before VERIFIED.

## Spec-Derived Verification Plan

Run targeted tests that map to the role-authority specs:

```text
python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short
python -m pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short
python -m pytest platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short
```

Expected results:
- `GOV-SESSION-ROLE-AUTHORITY-001`: tests prove non-dispatcher gates, attribution, and claim metadata do not treat durable registry role as behavior authority.
- `DCL-SESSION-ROLE-RESOLUTION-001`: tests prove explicit/per-session/session-envelope role wins; durable fallback is only resolver fallback and is distinguishable from authoritative behavior input.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`, `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`, and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`: tests prove `::init gtkb pb|lo` / session-envelope role survives the relevant interactive handoff path and stale shared-marker cases do not override it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: bridge compliance preflight accepts this proposal's project/PAUTH/WI metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: LO verification can cite the above per-spec test execution evidence before VERIFIED.

Run proposal preflights before filing and again after edits if the body changes:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-role-authority-boundary-scoped-correction
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-role-authority-boundary-scoped-correction
```

## Risk / Rollback

Main risk: over-correcting legitimate dispatcher-owned registry reads or
breaking headless dispatch routing while removing non-dispatcher authority
leaks. Mitigation: classify each registry read as dispatcher-owned,
resolver-fallback-owned, identity/provenance-only, or violation before editing.
Rollback is a single commit revert of source/rule/test changes plus revoking
`PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702` if implementation proves broader
than approved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-role-authority-boundary-scoped-correction`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — the primary outcome is correcting role-authority behavior that can block
or mislabel an owner-declared Prime Builder session.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
