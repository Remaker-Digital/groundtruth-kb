NEW

# WI-4700 Narrative Approval Packet Scope Fix Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4700-narrative-approval-packet-scope-fix
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-20 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee6b1-1e3b-7cf1-bd9c-a6770173767a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

Project Authorization: PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4700

target_paths: [".groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-canonical-terminology-md-wi4700.json", ".groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-operating-model-md-wi4700.json", "bridge/gtkb-wi4700-narrative-approval-packet-scope-fix-*.md"]

implementation_scope: narrative_approval_packet_scope_fix
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
protected_source_mutation_in_scope: false
protected_narrative_mutation_in_scope: false
supporting_approval_packet_mutation_in_scope: true

---

## Summary

`bridge/gtkb-wi4700-harness-metadata-freshness-guard-004.md` gives GO for
WI-4700 and explicitly conditions implementation on creating and citing any
required protected narrative-artifact approval evidence before editing protected
narrative files. During implementation, the implementation-start gate correctly
refused creation of the two required `.groundtruth/formal-artifact-approvals/`
packet files because the revised WI-4700 `target_paths` authorize the protected
narrative targets but omit their matching approval-packet artifacts.

This proposal is a narrow scope correction. It authorizes only the two
narrative-artifact approval packet JSON files needed for the already-GO'd
WI-4700 protected edits:

- `.claude/rules/canonical-terminology.md`
- `.claude/rules/operating-model.md`

It does not authorize editing those protected files by itself; the original
WI-4700 implementation-start packet already covers those targets. It also does
not authorize any change to `.api-harness/routing.toml`, source code, tests,
config, MemBase, deployment, or credentials.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The missing target authorization was found
  by the implementation-start gate; packet creation must proceed through bridge
  GO rather than an out-of-scope side write.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal
  carries concrete project/work metadata, target paths, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - The header links this
  scope correction to `PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD`,
  `PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH`, and `WI-4700`.
- `GOV-ARTIFACT-APPROVAL-001` - Protected narrative-artifact mutations require
  per-target approval packets with full-content hash evidence.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - The narrative-artifact hook and universal
  pre-commit floor validate approval packets against staged protected content.
- `config/governance/narrative-artifact-approval.toml` - Defines the protected
  `.claude/rules/*.md` narrative-artifact family and the required packet fields.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - The WI-4700 project
  authorization does not bypass bridge GO or implementation-start target scope.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` and `REQ-HARNESS-REGISTRY-001` - The
  parent WI-4700 work corrects stale routing/registry/narrative metadata; this
  child proposal supplies only the missing approval-packet authorization needed
  to complete that correction.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The post-implementation
  report must map packet creation and narrative evidence validation to executed
  checks before Loyal Opposition can verify.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The packet artifacts are durable
  governance evidence for a protected narrative mutation in the WI-4700
  lifecycle, not transient session scratch.

## Prior Deliberations

- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - Owner selected the
  systemic WI-4700 freshness guard: correct stale Ollama/local/free claims and
  add a deterministic doctor check.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-003.md` - Revised
  WI-4700 proposal: implementation step 4 requires narrative-artifact approval
  packets before protected narrative edits.
- `bridge/gtkb-wi4700-harness-metadata-freshness-guard-004.md` - LO GO: GO
  condition 4 says to create and cite required approval evidence before editing
  protected narrative artifacts.
- `bridge/gtkb-work-intent-registry-prime-write-integration-008.md` and
  `bridge/gtkb-work-intent-registry-prime-write-integration-009.md` - Prior
  bridge precedent for NO-GO when a proposal requires a narrative approval
  packet but omits the concrete approval-packet file from `target_paths`.

## Owner Decisions / Input

No new owner decision is required for this scope correction. The owner selected
WI-4700's systemic freshness guard in
`DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION`, and
`PAUTH-WI-4700-HARNESS-METADATA-FRESHNESS-GUARD` covers governance evidence and
protected narrative work for `WI-4700`. This proposal does not ask Loyal
Opposition to approve the protected narrative content; it asks only to authorize
creation of the matching approval-packet files that the protected-write workflow
already requires.

## Requirement Sufficiency

Existing requirements are sufficient. The missing scope is a bridge target-path
omission, not a new platform requirement. `GOV-ARTIFACT-APPROVAL-001`,
`DCL-ARTIFACT-APPROVAL-HOOK-001`, and the already-GO'd WI-4700 proposal fully
constrain the work.

## Implementation Plan

1. After Loyal Opposition GO, acquire an implementation-start packet for this
   scope-fix bridge id.
2. Generate exactly two narrative-artifact approval packets under
   `.groundtruth/formal-artifact-approvals/`:
   - `2026-06-20-claude-rules-canonical-terminology-md-wi4700.json`
   - `2026-06-20-claude-rules-operating-model-md-wi4700.json`
3. Each packet must set `artifact_type = "narrative_artifact"`, target the
   protected file it covers, include the full proposed post-edit content, and
   carry a `full_content_sha256` matching that content.
4. Resume the parent WI-4700 implementation using the original WI-4700 packet
   for the protected file edits and these child-scope packets as the
   narrative-artifact evidence consumed by the protected-write helper.
5. File a post-implementation report for this scope-fix and cite it from the
   parent WI-4700 report. No terminal claim should be made until Loyal
   Opposition verifies both reports.

## Spec-to-Test Mapping

| Specification | Verification command | Expected observed result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4700-narrative-approval-packet-scope-fix` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4700-narrative-approval-packet-scope-fix` | no missing required specs; no blocking clause gaps |
| `GOV-ARTIFACT-APPROVAL-001`; `DCL-ARTIFACT-APPROVAL-HOOK-001` | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/operating-model.md` | `PASS narrative-artifact evidence (2 cleared)` after the packets and protected files are staged |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python scripts/implementation_authorization.py validate --target .groundtruth/formal-artifact-approvals/2026-06-20-claude-rules-canonical-terminology-md-wi4700.json` and the equivalent operating-model packet target | `authorized: true` after this scope-fix receives GO and `begin` is run |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | focused pytest lane in the parent WI-4700 report, including doctor tests that exercise stale narrative/registry metadata | observed `pytest` result is included in the implementation report |

## Risk / Rollback

Risk is low and bounded: this proposal authorizes evidence packet files only.
A bad packet cannot by itself mutate a protected narrative artifact because the
protected-write helper and pre-commit evidence checker require the packet hash
to match the staged protected file content. Rollback is deleting the generated
packet files before verification if Loyal Opposition issues NO-GO or if the
parent WI-4700 implementation changes the proposed narrative content and must
regenerate packet hashes.

## Recommended Commit Type

`fix:` - this corrects an implementation-scope defect that blocks WI-4700's
approved freshness guard from completing.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
