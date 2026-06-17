REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ed5c7-138e-7321-bbd3-dd119cec6b9c
author_model: gpt-5-codex
author_model_version: 2026-06-17 runtime
author_model_configuration: Codex desktop automation session; Prime Builder bridge metadata repair

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4611-AND-WI-4612-DEFECT-FIXES
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4612
target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]

# Revised Implementation Proposal - Skill Generator Registry Formatting

bridge_kind: prime_proposal
Document: gtkb-skill-generator-registry-formatting
Version: 003
Responds-To: bridge/gtkb-skill-generator-registry-formatting-002.md
Revises: bridge/gtkb-skill-generator-registry-formatting-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-17 UTC
Recommended commit type: fix

## Revision Claim

The GO verdict at `bridge/gtkb-skill-generator-registry-formatting-002.md` approved the intended WI-4612 implementation, but the approved proposal at `bridge/gtkb-skill-generator-registry-formatting-001.md` is not activatable by `scripts/implementation_authorization.py begin` because it uses a fenced multi-line `Target Paths` JSON block and omits the required `## Requirement Sufficiency` section.

This REVISED proposal repairs only that bridge metadata defect. It preserves the same implementation intent, project authorization, work item, target files, acceptance criteria, verification plan, and risk profile from the approved proposal while adding parser-recognized implementation-start metadata.

## Requirement Sufficiency

Existing requirements sufficient. The work is bounded by `WI-4612`, project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4611-AND-WI-4612-DEFECT-FIXES`, and the governing bridge, verification, and root-boundary specifications cited below. No new or revised requirement is needed before implementation.

## Files Expected To Change

- `scripts/generate_codex_skill_adapters.py` - converge registry TOML formatting behavior.
- `scripts/generate_antigravity_skill_adapters.py` - use the same registry TOML formatting behavior.
- `platform_tests/scripts/test_generate_codex_skill_adapters.py` - cover Codex generator convergence behavior.
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` - cover Antigravity generator convergence behavior.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`. The change remains confined to source and tests under the GT-KB project root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - Proposal and verification flow through the file bridge.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This section cites the governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification is mapped from cited requirements to executable tests below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project authorization, project, and work-item metadata are included at the top of the file.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation target paths remain within `E:\GT-KB`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - The active project authorization supplies owner approval evidence for the bounded work item, without bypassing bridge GO or implementation-start packet requirements.
- `GOV-RELIABILITY-FAST-LANE-001` - The authorized defect fix is a bounded reliability/hygiene repair in May29 Hygiene.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The non-activatable bridge GO is preserved as explicit lifecycle evidence and repaired through a revised bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Advisory; bridge metadata repair preserves durable artifact lifecycle state instead of silently implementing around it.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Advisory; the non-activatable GO is treated as unresolved bridge lifecycle state requiring explicit revision.

## Prior Deliberations

- `DELIB-20260616-MAY29-HYGIENE-AUTHORIZATION` - Owner decision authorizing the WI-4611/WI-4612 defect-fix project authorization.
- `DELIB-20260671` - LO-cited related decision concerning TOML and source-of-truth consolidation context.
- `DELIB-20260868` - LO-cited related disposition context for prior work-item handling.
- `bridge/gtkb-skill-generator-registry-formatting-001.md` - Original WI-4612 proposal.
- `bridge/gtkb-skill-generator-registry-formatting-002.md` - LO GO verdict approving the implementation intent while leaving parser-incompatible metadata in the proposal.

## Owner Decisions / Input

- `DELIB-20260616-MAY29-HYGIENE-AUTHORIZATION` authorizes bounded implementation of `WI-4612` through project authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-WI-4611-AND-WI-4612-DEFECT-FIXES`.
- No new owner decision is required. This revision does not expand target paths, mutation class, project scope, or acceptance criteria.

## Defect Evidence

Attempting to mint an implementation-start packet for the approved GO failed closed:

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-skill-generator-registry-formatting --no-write

authorized: false
error: Approved proposal is missing concrete target_paths or Files Expected To Change; Approved proposal is missing ## Requirement Sufficiency
```

## Proposed Scope

1. Converge TOML formatting behavior between the Codex and Antigravity skill adapter generators so sequential generator runs do not toggle `config/agent-control/harness-capability-registry.toml`.
2. Add or adjust focused platform tests proving both generators converge on the same registry formatting.
3. Preserve the current registry schema and avoid broad capability or role-surface changes.

## Pre-Filing Preflight Subsection

Applicability preflight was run against this candidate content before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-skill-generator-registry-formatting --content-file .gtkb-state\bridge-revisions\drafts\gtkb-skill-generator-registry-formatting-003.md --json
```

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

Clause preflight was run against the same candidate content before live filing:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-skill-generator-registry-formatting --content-file .gtkb-state\bridge-revisions\drafts\gtkb-skill-generator-registry-formatting-003.md
```

- clauses evaluated: `5`
- must_apply: `3`
- may_apply: `2`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit status: `0`

## Specification-Derived Verification Plan

| Specification | Target Test / Manual Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | File this corrected proposal as `REVISED`, wait for LO `GO`, implement, then file a post-implementation report for verification. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-skill-generator-registry-formatting --content-file <candidate>` and require `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused generator tests and sequential generator checks demonstrating no registry diff after Codex then Antigravity updates. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project authorization, project, and work item metadata are present and accepted by bridge compliance. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm changed files and bridge evidence remain under `E:\GT-KB`. |

## Acceptance Criteria

1. `scripts/implementation_authorization.py begin --bridge-id gtkb-skill-generator-registry-formatting --no-write` can mint an authorization packet after LO re-approves this revised proposal.
2. Running `scripts/generate_codex_skill_adapters.py --check --update-registry` followed by `scripts/generate_antigravity_skill_adapters.py --check --update-registry` does not produce formatting-only churn in `config/agent-control/harness-capability-registry.toml`.
3. The focused pytest suites for both generator scripts pass.
4. The registry remains valid TOML.

## Risks And Rollback

- Risk: low. The revision only repairs proposal metadata and re-queues LO review; it does not mutate implementation target files.
- Rollback: if LO identifies a missing constraint, file a further `REVISED` version rather than editing existing bridge history.
