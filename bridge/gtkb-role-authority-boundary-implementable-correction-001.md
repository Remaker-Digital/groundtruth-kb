NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f2937-cdfc-77a2-964c-944265a361c3
author_model: GPT-5
author_model_version: GPT-5 Codex runtime 2026-07-03
author_model_configuration: Codex Desktop interactive; resolved role prime-builder via ::init gtkb pb; governed bridge-proposal filing
author_metadata_source: interactive-env

# Implementation Proposal - Phase 4 - Regression guards: doctor check + test that the write-gate honors ::init gtkb pb and never enforces on registry fallback

bridge_kind: prime_proposal
Document: gtkb-role-authority-boundary-implementable-correction
Version: 001
Date: 2026-07-03 UTC

Project Authorization: PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702
Project: PROJECT-GTKB-ROLE-AUTHORITY-DISPATCHER-ONLY-PURGE
Work Item: WI-4785

target_paths: ["CLAUDE.md", "AGENTS.md", ".claude/rules/canonical-terminology.md", ".claude/rules/operating-role.md", ".claude/hooks/lo-file-safety-gate.py", "scripts/session_role_resolution.py", "scripts/bridge_work_intent_registry.py", "scripts/bridge_claim_cli.py", "scripts/_kb_attribution.py", "groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py", "groundtruth-kb/src/groundtruth_kb", "groundtruth-kb/tests", "platform_tests", "config/agent-control"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the role-authority boundary correction after AUQ-backed GOV v4 and DCL v5 updates made existing requirements sufficient for source/test/config work. Supersedes the non-activatable source-implementation phase of gtkb-role-authority-boundary-scoped-correction, whose GO intentionally required new or revised requirements first.

Work item description: Promote the Phase 1 lint into a doctor check that FAILS when a non-dispatcher surface references the registry for authority or durable-role terminology reappears without the dispatcher-only qualifier. Add a regression test asserting lo-file-safety-gate.py honors ::init gtkb pb (the 2026-06-24 scenario) and does not enforce on registry fallback.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4785` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `CLAUDE.md`, `AGENTS.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-role.md`, `.claude/hooks/lo-file-safety-gate.py`, `scripts/session_role_resolution.py`, `scripts/bridge_work_intent_registry.py`, `scripts/bridge_claim_cli.py`, `scripts/_kb_attribution.py`, `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`, `groundtruth-kb/src/groundtruth_kb`, `groundtruth-kb/tests`, `platform_tests`, `config/agent-control`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` - auto-linked governing or work-item specification.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` - auto-linked governing or work-item specification.
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `PAUTH-GTKB-ROLE-AUTHORITY-BOUNDARY-20260702` - active project authorization covering `WI-4785`.

## Proposed Scope

- Audit each harness-registry role read and classify it as dispatcher-owned, resolver-fallback-owned, identity/provenance-only, or violation before editing.
- Fix only confirmed non-dispatcher behavior-authority leaks in hooks, CLIs, bridge claim/work-intent, attribution, startup/focus, MCP role surfaces, shared source, and mirrored templates/tests.
- Preserve dispatcher-owned registry routing and receiver-side dispatch audit behavior.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | python -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/scripts/test_session_role_resolution_table.py platform_tests/scripts/test_dcl_role_resolution_authority_001.py -q --tb=short |
| `DCL-SESSION-ROLE-RESOLUTION-001` | python -m pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_bridge_claim_cli.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` | python -m pytest platform_tests/hooks/test_session_role_resolution.py platform_tests/hooks/test_workstream_focus_session_role_marker.py -q --tb=short |
| `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | python -m pytest groundtruth-kb/tests/test_mcp_surface_foundation.py -q --tb=short |
| `ADR-CROSS-HARNESS-PARITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Cross-Harness Disposition

- Claude Code: behavioral parity is required for Claude hook/rule/startup surfaces touched by this correction; no typed waiver requested.
- Codex: behavioral parity is required for Codex-facing bridge helpers, role-resolution behavior, and startup/focus surfaces touched by this correction; no typed waiver requested.
- Cursor: behavioral parity is required where shared startup or bridge-dispatch surfaces consume role evidence; no typed waiver requested.
- Antigravity: behavioral parity is required for shared role-resolution/startup surfaces; no typed waiver requested.
- Ollama/OpenRouter headless workers: dispatcher-owned registry routing and receiver-side audit behavior must remain dispatcher-owned and non-blocking outside dispatch audit; no typed waiver requested.

## Acceptance Criteria

- No non-dispatcher gate, claim path, attribution path, AUQ/focus path, skill/helper path, or doctor/check path directly treats harness-state/harness-registry.json role as behavior authority.
- Interactive Prime sessions with matching per-session role evidence can acquire GO implementation claims without relying on the shared active-session-role.json marker.
- All touched registry reads are documented in the implementation report with dispatcher-owned, resolver-fallback-owned, identity/provenance-only, or violation classification.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `CLAUDE.md`
- `AGENTS.md`
- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-role.md`
- `.claude/hooks/lo-file-safety-gate.py`
- `scripts/session_role_resolution.py`
- `scripts/bridge_work_intent_registry.py`
- `scripts/bridge_claim_cli.py`
- `scripts/_kb_attribution.py`
- `groundtruth-kb/src/groundtruth_kb/mcp_surface/roles.py`
- `groundtruth-kb/src/groundtruth_kb`
- `groundtruth-kb/tests`
- `platform_tests`
- `config/agent-control`

## Recommended Commit Type

`feat`
