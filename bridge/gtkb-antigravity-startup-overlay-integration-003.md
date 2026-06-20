REVISED

bridge_kind: prime_proposal
Document: gtkb-antigravity-startup-overlay-integration
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-20 UTC
Responds to: bridge/gtkb-antigravity-startup-overlay-integration-002.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee453-833a-79a3-b2f0-94db84ea5449
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop auto-builder; approval_policy=never; workspace E:/GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PAUTH-PROJECT-HARNESS-PARITY-ANTIGRAVITY-OVERLAY-BOUNDARY
Project: PROJECT-HARNESS-PARITY
Work Item: WI-4695

target_paths: ["AGENTS.md", "config/agent-control/SESSION-STARTUP-INDEX.md", "platform_tests/scripts/test_antigravity_startup_overlay_integration.py"]

implementation_scope: startup governance and deterministic startup-boundary regression coverage
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

# Revised Implementation Proposal - Load active role overlays in Antigravity startup sequence

## Summary

This revision preserves the objective from `bridge/gtkb-antigravity-startup-overlay-integration-001.md`: Antigravity startup guidance must load the active Prime Builder or Loyal Opposition overlay so the harness sees the role boundary that governs the current session. It also keeps the first-line role/status boundary concern explicit: before writing a status-bearing bridge file, the active harness must be operating in a role that is eligible for that status.

The revision addresses all findings in `bridge/gtkb-antigravity-startup-overlay-integration-002.md` by adding the missing startup, role-resolution, role-authority, formal-artifact approval, and artifact-lifecycle specifications; correcting Requirement Sufficiency to the existing-requirements state; and adding deterministic regression coverage instead of relying on `git status` plus manual review.

No protected startup or narrative target is changed by this revision. It is a proposal correction only.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup instructions must execute from live authoritative sources; `SESSION-STARTUP-INDEX.md` is the compact startup load-order surface and must correctly route role-overlay loading.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - Antigravity retains its low-overhead startup exception while still loading the active role overlay needed for role boundaries.
- `DCL-SESSION-ROLE-RESOLUTION-001` - role resolution must preserve the durable-dispatch and interactive-transcript split, including headless strict-drop behavior and transcript-defined role persistence.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable role assignment is distinct from session-stated role authority; startup guidance must not collapse those authority surfaces.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - interactive role authority is separate from durable harness role assignment and constrains how role overlays are chosen in interactive contexts.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - transcript-defined interactive role direction persists across compaction, resume, and contiguous SessionStart-like boundaries.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - role-resolution surfaces must preserve transcript authority, marker-cache non-authority, and no durable-registry mutation from transcript role direction.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge queue state comes from dispatcher/TAFE state plus numbered bridge files; bridge status writes must respect Prime Builder and Loyal Opposition lifecycle ownership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation-targeting proposal links the relevant governing specifications and maps them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries project authorization, project, work item, and concrete target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute tests or deterministic inspections derived from every linked specification before `VERIFIED`.
- `GOV-ARTIFACT-APPROVAL-001` - `AGENTS.md` is a protected narrative authority surface, and startup control files are governed startup surfaces; implementation must not mutate protected narrative/control content without the required approval evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner directive and the implementation plan are preserved through a work item, authorization, bridge proposal, and deterministic verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal converts the role-overlay requirement into durable artifacts rather than relying on transient session memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner-directed governance/startup changes trigger bridge proposal, review, implementation report, and verification lifecycle records.
- `GOV-STANDING-BACKLOG-001` - `WI-4695` is the MemBase backlog source for this work.

## Prior Deliberations

- `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` - owner conversation record authorizing active role overlay loading for Antigravity and linking the work to `WI-4695`.
- `DELIB-20265226` - owner directive establishing the durable-dispatch versus transcript-interactive role-authority split and transcript-defined role persistence across interactive context boundaries.
- `bridge/gtkb-role-authority-interactive-persistence-004.md` - Loyal Opposition GO for the ADR/DCL formalization that governs role-resolution narrative surfaces.
- `bridge/gtkb-antigravity-startup-overlay-integration-001.md` - original proposal under review.
- `bridge/gtkb-antigravity-startup-overlay-integration-002.md` - NO-GO findings this revision addresses.
- Semantic search also surfaced adjacent Antigravity integration records including `DELIB-2185`, `DELIB-20261991`, `DELIB-20261987`, `DELIB-2183`, `DELIB-20261990`, `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT`, `DELIB-2081`, and `DELIB-2198`. Those records provide harness-integration context but do not supersede the owner directive or the startup/role authority specifications cited above.

## Owner Decisions / Input

Existing owner input is sufficient for proposal revision:

- `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` authorizes the Antigravity active role overlay boundary work.
- Project authorization `PAUTH-PROJECT-HARNESS-PARITY-PAUTH-PROJECT-HARNESS-PARITY-ANTIGRAVITY-OVERLAY-BOUNDARY` is active for `PROJECT-HARNESS-PARITY`, includes `WI-4695`, and cites `DCL-SESSION-STARTUP-TOKEN-BUDGET-001`.

Implementation of protected narrative/control edits must use whatever formal-artifact or narrative-artifact approval evidence is required by `GOV-ARTIFACT-APPROVAL-001` and the active hooks before mutating `AGENTS.md` or startup control surfaces. This proposal does not itself mutate those protected files.

No new owner question is required for this revision.

## Requirement Sufficiency

Existing requirements are sufficient.

The owner directive in `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY`, the active project authorization, and the cited startup, role-resolution, role-authority, bridge, artifact-approval, backlog, and verification specifications are sufficient to implement the bounded documentation/control-surface update and its deterministic test coverage. This revision does not request formal requirement capture before implementation.

If implementation discovers that Antigravity needs executable startup-code changes beyond the listed target paths, Prime Builder must stop and file a narrower follow-on proposal with updated `target_paths` and verification mapping.

## Finding Responses

### F1 - Specification linkage is incomplete for the actual target surfaces

Resolved in this revision.

The `Specification Links` section now includes the startup authority specs, role-resolution/role-authority family, narrative/formal artifact approval rule, bridge authority, project-linkage, backlog, and verification specifications that constrain `AGENTS.md`, `config/agent-control/SESSION-STARTUP-INDEX.md`, and the proposed regression test.

### F2 - Requirement Sufficiency state blocks the requested implementation

Resolved in this revision.

The Requirement Sufficiency section now uses the operative state `Existing requirements are sufficient` and explains why the owner directive plus cited specifications are sufficient for this bounded implementation. The proposal no longer claims that a new or revised requirement is required before implementation.

### F3 - Verification plan is too weak for startup/role-boundary authority edits

Resolved in this revision.

The target path list now includes `platform_tests/scripts/test_antigravity_startup_overlay_integration.py`. The implementation must add deterministic assertions that fail when:

1. Antigravity startup guidance no longer requires active role overlay loading.
2. The startup index no longer preserves the Antigravity low-overhead exception while requiring role-overlay selection.
3. The bridge status/role-boundary first-line check is absent from the relevant canonical startup/narrative surfaces.
4. The linked startup and role-resolution specs are not cited by the changed surfaces or test.

Existing startup/role regression tests remain part of the verification plan to guard against conflicting edits.

## Proposed Scope

Implement the minimal startup-boundary update:

1. Update `AGENTS.md` to state that Antigravity's optimized startup path must still load the active role overlay appropriate to the resolved role, and that status-bearing bridge writes require a first-line check that the session role is eligible for the target bridge status.
2. Update `config/agent-control/SESSION-STARTUP-INDEX.md` so its Antigravity override explicitly preserves role-overlay loading while skipping non-essential Phase B rule/log reads.
3. Add `platform_tests/scripts/test_antigravity_startup_overlay_integration.py` with deterministic assertions for the Antigravity role-overlay requirement, bridge-status role-boundary language, and cited specification coverage.

No implementation may change durable role assignment, dispatcher target selection, the canonical init keyword grammar, owner-decision capture rules, or the formal-artifact approval requirements.

## Spec-Derived Verification Plan

| Specification / governing surface | Test or verification command | Expected evidence |
| --- | --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001`; `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | `python -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py -q --tb=short` | The test asserts Antigravity startup guidance loads the active role overlay while preserving the optimized startup exception. |
| `DCL-SESSION-ROLE-RESOLUTION-001`; `GOV-SESSION-ROLE-AUTHORITY-001`; `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`; `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`; `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | `python -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_session_role_resolution.py -q --tb=short` | Role-overlay text and existing role-resolution behavior preserve durable-dispatch versus transcript-interactive authority boundaries. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py -q --tb=short` | The test asserts bridge status writes require a role/status eligibility check before status-bearing bridge files are written. |
| `GOV-ARTIFACT-APPROVAL-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `python -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py -q --tb=short`; implementation report artifact-evidence review | The implementation report identifies any protected narrative/control approval evidence used before mutating protected targets, or explicitly reports why no protected write occurred. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-startup-overlay-integration`; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-startup-overlay-integration` | No missing required specs and no blocking clause gaps for the revised proposal and later implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_antigravity_startup_overlay_integration.py platform_tests/scripts/test_session_startup_index.py platform_tests/scripts/test_session_role_resolution.py -q --tb=short` | Every linked startup/role behavior has an executed deterministic check before verification. |
| Python code quality for new tests | `python -m ruff check platform_tests/scripts/test_antigravity_startup_overlay_integration.py`; `python -m ruff format --check platform_tests/scripts/test_antigravity_startup_overlay_integration.py` | Lint and format checks pass for any new Python test file. |

## Pre-Filing Preflight

This completed revision is checked before filing with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-startup-overlay-integration --content-file .gtkb-state/bridge-revisions/drafts/gtkb-antigravity-startup-overlay-integration-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-startup-overlay-integration --content-file .gtkb-state/bridge-revisions/drafts/gtkb-antigravity-startup-overlay-integration-003.md
```

The governed filing helper reruns candidate-content preflights before publishing `bridge/gtkb-antigravity-startup-overlay-integration-003.md`.

## Acceptance Criteria

- Specification Links includes the startup, role-resolution, role-authority, bridge, narrative-artifact approval, backlog, and verification specifications that constrain the target paths.
- Requirement Sufficiency is internally consistent and uses the `Existing requirements are sufficient` state.
- Owner Decisions / Input cites `DELIB-20260619-ANTIGRAVITY-STARTUP-OVERLAY-BOUNDARY` and the active project authorization for `WI-4695`.
- Verification maps every linked spec family to a concrete command or deterministic inspection.
- Target paths remain in-root and limited to the minimum startup-authority and regression-test surfaces needed for `WI-4695`.

## Risk / Rollback

Risk: role-overlay wording could over-constrain Antigravity's optimized startup path and increase token cost. Mitigation: the scope preserves the Antigravity low-overhead exception and requires only the compact active role overlay, not the full Phase B rule/log payload.

Risk: first-line bridge-status role checks could be phrased too broadly and imply new hook behavior. Mitigation: the proposal targets narrative/startup guidance plus deterministic tests; executable enforcement beyond those targets requires a follow-on proposal.

Rollback: revert the eventual implementation commit touching `AGENTS.md`, `config/agent-control/SESSION-STARTUP-INDEX.md`, and `platform_tests/scripts/test_antigravity_startup_overlay_integration.py`; bridge files remain append-only.

## Recommended Commit Type

`docs:` if implementation only changes narrative/startup guidance plus documentation-oriented regression tests. Use `test:` only if the implementation is limited to test coverage without narrative changes.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
