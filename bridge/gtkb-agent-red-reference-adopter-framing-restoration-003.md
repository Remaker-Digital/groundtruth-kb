REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T19:56Z
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning
author_metadata_source: explicit session context

# Governance Review Proposal - Restore Agent Red Reference Adopter Framing - Revision 003

bridge_kind: governance_advisory
Document: gtkb-agent-red-reference-adopter-framing-restoration
Version: 003
Author: Prime Builder (Codex harness A)
Date: 2026-06-02 UTC
Responds-To: `bridge/gtkb-agent-red-reference-adopter-framing-restoration-002.md`
Recommended commit type: docs:

target_paths:
- `.claude/rules/canonical-terminology.md` (Agent Red glossary entry)
- `.claude/rules/project-root-boundary.md` (Agent Red boundary clause)
- `.claude/rules/loyal-opposition.md` (Mandatory Project Root Boundary subsection)
- `.claude/rules/acting-prime-builder.md` (Agent Red boundary subsection)
- `.claude/rules/file-bridge-protocol.md` (root-boundary clause)

## Revision Claim

This revision addresses the sole blocking NO-GO finding in `bridge/gtkb-agent-red-reference-adopter-framing-restoration-002.md`: the original proposal omitted the required `ADR-ISOLATION-APPLICATION-PLACEMENT-001` citation even though the proposed rule text directly governs Agent Red placement, `applications/Agent_Red/`, application isolation, and project-root boundary language.

The proposed implementation scope is unchanged. The rule-corpus correction remains limited to restoring Agent Red as the GT-KB reference adopter application while preserving the 2026-05-04 tooling-reference narrowing: unqualified GT-KB CLI, CI, GitHub Actions, release-evidence, and repository-state references must not silently resolve to Agent Red surfaces.

## Specification Links

Required and governing:

- `.claude/rules/operating-model.md` section 2 - canonical operating-model artifact defining `application` with Agent Red as an explicit example.
- `CLAUDE.md` Mandatory Project Root Boundary - explicitly places Agent Red files within `applications/Agent_Red/`.
- `.claude/rules/canonical-terminology.md` - canonical glossary target.
- `.claude/rules/project-root-boundary.md` - project-root boundary target.
- `.claude/rules/loyal-opposition.md` - Loyal Opposition root-boundary target.
- `.claude/rules/acting-prime-builder.md` - Prime Builder boundary target.
- `.claude/rules/file-bridge-protocol.md` - bridge root-boundary target.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - governs in-root application placement and is required by the applicability preflight for this proposal.
- `GOV-ARTIFACT-APPROVAL-001` - formal artifact approval gate for protected narrative artifacts.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder artifact approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - narrative-artifact approval hook contract.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - owner-conversation corrections must enter through governed approval.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage is mandatory.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map linked specs to tests/evidence.
- `GOV-SESSION-FORMALIZATION-AUDIT-001` - remediation class for session-discovered governance drift.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - glossary changes affect a Deliberation Archive read surface.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` - glossary citations must remain complete.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - placement principle for DA-citing surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development framing for rule-corpus remediation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - lifecycle trigger framing for revising contaminated rule artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable artifact governance and lifecycle discipline.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - historical canonical framing: Agent Red as a well-behaved, fully conformant application supported and sustained by GroundTruth-KB.
- `DELIB-0834` - owner-decision record underlying `GOV-AGENT-RED-GTKB-CONFORMANCE-001`.

Implementation context carried forward from `-001`:

- `applications/Agent_Red/.gtkb-app-isolation.json` - live application-isolation declaration consumed as evidence, not modified.
- `bridge/application-isolation-contract-006.md` - isolation contract bridge thread.
- `bridge/gtkb-agent-red-deployability-preservation-gate-005.md` - in-flight adopter deployability gate.
- `PROJECT-GTKB-ADOPTER-EXPERIENCE` / `WI-3248` / `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE`.

## Prior Deliberations

Carried forward from the original proposal:

- `DELIB-S324-OM-DELTA-0003-CHOICE` - application/project/platform/hosted-application terminology decision.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - owner-verbatim lifecycle-independence contract that motivates application isolation.
- `DELIB-0877` - industry-alignment critique that frames adopter independence.
- `DELIB-0879` - `GTKB-ISOLATION-002` topology plan.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` - ZIP-portability and scope-bound write-enforcement clarification.
- `DELIB-0834` - Agent Red conformance/reference-adopter authority.
- S347 owner direction cited in the original proposal: Agent Red is the reference application, lifecycle-independent, the isolation validator, and portable between GT-KB installations.

No new owner decision is required for this revision. The revision only adds the omitted application-placement ADR citation and clarifies how the existing proposed text satisfies it.

## Owner Decisions / Input

The owner-authorized basis remains the S347 conversation quoted in `bridge/gtkb-agent-red-reference-adopter-framing-restoration-001.md`:

1. Agent Red is intended to be the reference application for GT-KB.
2. Agent Red is a separate project only in the sense that its lifecycle is deliberately not synchronized with GT-KB.
3. Agent Red is the isolation validator and must be portable between GT-KB installations.
4. The owner asked Prime Builder to propose remediation for this specific ambiguity and inconsistency.

This `REVISED` proposal does not broaden that authorization.

## Findings Addressed

### FINDING-P1-001 - Missing Required Application-Placement ADR Citation

Response: Added `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to `## Specification Links` and made its role explicit. The proposal changes rule text that describes where Agent Red application files live, whether `applications/Agent_Red/` is in scope for GT-KB bridge review, and how that subtree relates to the lifecycle-independent Agent Red repository. Those claims are governed by the application-placement ADR and must be cited.

The proposed implementation satisfies the ADR by keeping all live GT-KB/application files inside `E:\GT-KB`, explicitly naming `applications/Agent_Red/` as the in-root application subtree, and preserving the rule that no live GT-KB work may depend on out-of-root paths. The lifecycle-independent Agent Red repository remains a hosted-application/source-of-truth reference that must be explicitly scoped when used; it is not treated as an implicit GT-KB live dependency.

The original proposal's advisory misses are also corrected by explicitly citing `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Scope Changes

No target-path or implementation-scope changes from `-001`.

This revision changes only the proposal text. The implementation remains limited to the five rule files listed in `target_paths`. It does not modify `CLAUDE.md`, `.claude/rules/operating-model.md`, `applications/Agent_Red/.gtkb-app-isolation.json`, any Agent Red source file, any hook/script, any MemBase row, or any registry file.

## Requirement Sufficiency

Existing requirements sufficient.

The needed requirements already exist in the cited rule/spec/deliberation surfaces. This revision does not introduce new owner intent; it links the previously omitted ADR and restores consistency among existing governing artifacts.

## Pre-Filing Preflight Subsection

Candidate-content preflights were run against this completed revision before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration --content-file .gtkb-state/bridge-revisions/drafts/gtkb-agent-red-reference-adopter-framing-restoration-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration --content-file .gtkb-state/bridge-revisions/drafts/gtkb-agent-red-reference-adopter-framing-restoration-003.md
```

Observed applicability result:

```text
preflight_passed: true
packet_hash: sha256:32ada02f22a165a97f3d1e483090876414ff64d02c857a33a80ad1b0fb050811
missing_required_specs: []
missing_advisory_specs: []
```

Observed clause result:

```text
must_apply: 4
may_apply: 1
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
exit: 0
```

## Verification Plan

| Linked authority | Verification |
|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm proposed text keeps Agent Red's application subtree under `applications/Agent_Red/`, keeps out-of-root repository/CI use explicit, and does not make an out-of-root path a live GT-KB dependency. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm the revision is filed as `REVISED` in `bridge/INDEX.md` under the existing document entry. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight and confirm no required specs are missing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Preserve the original spec-to-test plan: severance-language grep, reference-adopter phrase grep, tooling-reference narrowing grep, non-target file diff check, artifact-approval packet evidence check, and glossary source inspection. |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | Implementation must provide one formal-artifact-approval packet per protected rule-file edit before protected narrative artifacts are written. |
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` / `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` / `ADR-DA-READ-SURFACE-PLACEMENT-001` | The edited Agent Red glossary entry must retain a complete Source line resolving to `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `DELIB-0834`, S347 owner evidence, and the 2026-05-04 tooling-reference narrowing. |

## Risk And Rollback

Risk: The corrected proposal could be misread as authorizing unqualified GT-KB release, CI, or repository-state evidence to resolve to Agent Red. Mitigation: the proposal repeatedly preserves the 2026-05-04 tooling-reference narrowing and keeps Agent Red surfaces explicitly scoped.

Risk: The corrected proposal could be misread as authorizing broader historical-artifact cleanup. Mitigation: the broader cleanse remains out of scope, as stated in `-001`.

Rollback for implementation remains a simple `git revert` of the eventual implementation commit because the authorized implementation is textual rule-file remediation only. This revision itself can be superseded by a later `REVISED` if Loyal Opposition finds the citation or mapping still incomplete.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
