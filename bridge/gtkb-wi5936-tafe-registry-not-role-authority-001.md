NEW
::init gtkb pb
::open build
author_identity: Goose Prime Builder
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: goose-deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: manual interactive desktop session

bridge_kind: prime_proposal
Document: gtkb-wi5936-tafe-registry-not-role-authority
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WI-5935-SESSION-ENVELOPE-SINGLE-CONTEXT-IMPLEMENTATION
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-5936

# WI-5936 Slice 1 - Enumerate TAFE/dispatcher role/active-status misuse surfaces + authority-correction design

## Summary

WI-5936 (owner-identified defect): the TAFE/dispatcher harness-registry projection (`groundtruth_kb.harness_projection.read_roles` active/role flags) is NOT valid authority for harness/session role or for harness active-status; any reference to it as such is an error. This slice produces the enumerated inventory of every surface that consumes the projection for role/active-status, and the authority-correction design that re-points them to the authoritative sources (static identity file `harness-state/harness-identities.json` for active-status; transcript-declared init keyword / durable owner assignment for role). It is the investigation + design gate for the dependent correction slices. This proposal is filed as the next numbered file `bridge/gtkb-wi5936-tafe-registry-not-role-authority-001.md` under `bridge/` (append-only; no deletion or rewrite of prior versions).

## Requirement Sufficiency

New or revised requirement required before implementation: this slice's design output (the authority-correction contract) is the requirement that the correction slices implement. The owner directive (DELIB-20260804-TAFE-DISPATCHER-NOT-ROLE-AUTHORITY) is the governing decision.

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/harness_projection_reader.py", "scripts/session_role_resolution.py", "groundtruth.db"]

## Investigation scope (surfaces to enumerate)

Preliminary scan identified projection consumers to classify (role/active-status misuse vs. legitimate dispatch routing): `groundtruth_kb/session/envelope.py`, `session/handoff.py`, `project/doctor.py`, `mode_switch/*`, `bridge/state_report.py`, `harness_ops.py`, `harness_diagnostic.py`, `mcp_surface/roles.py`, plus scripts `harness_projection_reader.py`, `session_role_resolution.py`, `session_self_initialization.py`, `session_start_dispatch_core.py`, `check_harness_parity.py`, `protected_mutation_guard.py`, and the dispatcher/verify harness scripts. This slice classifies each as (a) role/active-status misuse to correct, (b) legitimate dispatch-routing use to retain, or (c) ambiguous (owner call).

## Authority-correction design (to be ratified)

1. Active-status authority = `harness-state/harness-identities.json` (static identity file).
2. Role authority = transcript-declared init keyword / durable owner assignment (never the dispatcher registry projection).
3. The dispatcher/TAFE registry projection remains valid ONLY for dispatch routing (who CAN be dispatched), never as a statement of which harness is active or what role a session holds.
4. A conformance guard (doctor/parity check) fails when any surface reads the projection for role/active-status.

## Specification Links

- `DELIB-20260804-TAFE-DISPATCHER-NOT-ROLE-AUTHORITY` - the governing owner decision.
- `GOV-SESSION-ROLE-AUTHORITY-001`; `DCL-SESSION-ROLE-RESOLUTION-001` - role authority model.
- `ADR-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-001` - role is owner-declared, not agent-detected.
- `REQ-HARNESS-REGISTRY-001` - the registry projection's intended scope (dispatch routing).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Specification-Derived Verification

- The slice's inventory enumerates every `read_roles`/projection consumer with a misuse/retain/ambiguous classification (evidence: the inventory artifact).
- The conformance guard (Slice 2) is verified by `python -m pytest` cases asserting no surface reads the projection for role/active-status.
- Self-check: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5936-tafe-registry-not-role-authority-001` preflight_passed.

## Prior Deliberations

- `DELIB-20260804-TAFE-DISPATCHER-NOT-ROLE-AUTHORITY` - owner decision.
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS` - NO-ACTION semantics (Slice C/F rejections).


### Helper-suggested candidates

_Deliberation semantic search degraded (SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 25900 and this is thread id 34264.); do not treat this section as an authoritative empty search result._
_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- 2026-08-04 (this session): Owner - 'The TAFE/dispatcher registry projection must not be used as harness/session role or active-status authority. Please create a work item and drive this through to a GO verdict.'

## Cross-Harness Disposition

Authority model is harness-neutral (applies uniformly); no per-harness variant and no waiver requested (per `ADR-CROSS-HARNESS-PARITY-001` Q8).

## Recommended Commit Type

docs: (investigation inventory + design contract; correction code lands in Slice 2).
