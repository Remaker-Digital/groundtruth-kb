GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-28-claude-md-scope-clarification-review
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default

# Loyal Opposition Review - GT-KB CLAUDE.md Scope Clarification Scoping

Document: gtkb-claude-md-scope-clarification-scoping
Reviewed version: bridge/gtkb-claude-md-scope-clarification-scoping-001.md
Verdict: GO
Date: 2026-05-28 UTC

## Verdict

GO. The proposal is a governance-review scoping artifact, not an implementation authorization. It correctly identifies a real scope ambiguity across `CLAUDE.md`, `AGENTS.md`, `.claude/rules/operating-model.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/project-root-boundary.md`, `CLAUDE-REFERENCE.md`, and `CLAUDE-ARCHITECTURE.md`. It preserves the required gate to Slice 2: owner approach selection plus a later implementation proposal and formal-artifact-approval packets before narrative-artifact writes.

This GO approves the scoping direction and authorizes Prime Builder to proceed to owner approach-selection and a concrete Slice 2 implementation proposal. It does not authorize direct edits to `CLAUDE.md`, `applications/Agent_Red/CLAUDE.md`, `.groundtruth/formal-artifact-approvals/`, or any other narrative/governance artifact.

## Applicability Preflight

- packet_hash: `sha256:0ad3d2461e719d23f4abd0061c9b03a2b2a59b9ebba81653eaa073d4731fd76d`
- bridge_document_name: `gtkb-claude-md-scope-clarification-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-claude-md-scope-clarification-scoping-001.md`
- operative_file: `bridge/gtkb-claude-md-scope-clarification-scoping-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-claude-md-scope-clarification-scoping`
- Operative file: `bridge\gtkb-claude-md-scope-clarification-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

Deliberation search for `CLAUDE.md Agent Red GT-KB scope platform application` returned relevant prior records:

- `DELIB-0706` - Owner decision that spec pipeline features are GT-KB product features, not Agent Red specific.
- `DELIB-0834` - Owner decision that Agent Red is a fully conformant application sustained by GT-KB.
- `DELIB-0023` - Structural separation plan addressing MemBase / Agent Red coupling.
- `DELIB-0876` - Owner directive on durable session work subject.
- `DELIB-0877` - Owner directive update on industry-alignment critique for GT-KB/application separation.

Direct `get_deliberation` checks also confirmed the proposal's cited `DELIB-0785`, `DELIB-0501`, `DELIB-0327`, and `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` records exist.

## Review Evidence

1. `CLAUDE.md:1` and `CLAUDE.md:3` frame the root guidance as Agent Red Customer Experience commercial-project guidance.
2. `CLAUDE.md:42-48` presents Agent Red as the application identity at the GT-KB root.
3. `CLAUDE.md:264-282` contains Agent Red commercial-feature and branch/deployment workflow guidance.
4. `AGENTS.md:11` states that Agent Red is not part of GT-KB and that unqualified work should default to GroundTruth-KB unless Mike explicitly says the session is Agent Red work.
5. `.claude/rules/operating-model.md:15-17` defines GT-KB as the platform and distinguishes application, project, platform, and hosted application.
6. `.claude/rules/canonical-terminology.md:221-263` defines platform, application, hosted application, and Agent Red, including Agent Red as a separate project not part of GT-KB.
7. `.claude/rules/project-root-boundary.md:10-17` requires live GT-KB artifacts to stay within `E:\GT-KB`, demo/application files within `E:\GT-KB\applications\`, and treats `E:\Claude-Playground` as archive-only.
8. `CLAUDE-ARCHITECTURE.md:12` still references `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\`, which conflicts with current root-boundary rules.
9. `CLAUDE-REFERENCE.md:21-34` is strongly Agent Red / AGNTCY scoped while living at the platform root.
10. `(Get-Content 'CLAUDE.md').Count` returned 301 lines, confirming the proposal's GOV-01 line-count observation.

## Findings

No blocking findings.

### Advisory A1 - Carry Advisory Applicability Specs Forward

Observation: The applicability preflight reports missing advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

Deficiency rationale: These are not GO blockers because `missing_required_specs: []`, but Slice 2 will mutate protected narrative artifacts and should be explicit about artifact lifecycle and artifact-oriented governance.

Proposed solution/enhancement: The Slice 2 implementation proposal should cite these advisory specs where applicable, or state why each is not operative for the final selected approach.

Option rationale: Carrying them forward is low-cost and reduces future review churn without blocking a valid scoping artifact.

### Advisory A2 - Preserve Application/Platform Boundary In The New Agent Red CLAUDE Surface

Observation: Approach C proposes `applications/Agent_Red/CLAUDE.md`, while current root-boundary language says Agent Red is separate from GT-KB and must not be treated as a live GT-KB artifact.

Deficiency rationale: This is not a blocker because `applications/` is also the canonical placement for GT-KB-managed application files. The implementation can remain valid if the new file is explicitly framed as application-scoped guidance for the Agent Red application subject, not as GT-KB platform authority.

Proposed solution/enhancement: Slice 2 should label the file's authority clearly, e.g. "Agent Red application-scope guidance consumed only when the active work subject is Agent Red", and should avoid making it a platform-global rule surface.

Option rationale: This preserves the structural split while avoiding a new ambiguity in the opposite direction.

## Conditions For Slice 2

Prime Builder should not edit protected narrative artifacts from this scoping GO alone. Before implementation:

1. Obtain one owner approach selection, preferably via AskUserQuestion.
2. File a concrete Slice 2 implementation proposal with exact `target_paths`.
3. Include formal-artifact-approval packet paths and hash-match procedure for every protected narrative artifact mutation.
4. Include `wc -l` or equivalent verification for `CLAUDE.md` GOV-01 compliance.
5. Include a grep/check step for references to moved or renamed CLAUDE sections.
6. Preserve the project-root boundary and explicitly distinguish platform authority from application-scope guidance.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
