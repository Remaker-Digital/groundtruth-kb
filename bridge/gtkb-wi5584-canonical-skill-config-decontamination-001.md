NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; filing an ops-only implementation proposal without configuration mutation
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Canonicalize proposal-review configuration across harnesses

bridge_kind: prime_proposal
Document: gtkb-wi5584-canonical-skill-config-decontamination
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5584-CANONICAL-CONFIG-DECONTAMINATION-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5584-CANONICAL-CONFIG-DECONTAMINATION-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5584

target_paths: [".claude/skills/proposal-review/SKILL.md", ".api-harness/skills/proposal-review/SKILL.md", ".agent/skills/proposal-review/SKILL.md", ".codex/skills/proposal-review/SKILL.md", ".goose/skills/proposal-review/SKILL.md", ".cursor/skills/proposal-review/SKILL.md", ".api-harness/skills/MANIFEST.json", ".agent/skills/MANIFEST.json", ".codex/skills/MANIFEST.json", ".goose/skills/MANIFEST.json", ".cursor/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "config/governance/evidence-freshness-boundaries.toml", "config/governance/hygiene-baseline-registry.toml"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Replace noncanonical proposal-review and evidence-registry references with stable canonical identities across every managed harness projection.

Work item description: Ops-only configuration slice that canonicalizes proposal-review evidence identities across one source skill, five managed projections, five manifests, and three registries.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5584` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/skills/proposal-review/SKILL.md`, `.api-harness/skills/proposal-review/SKILL.md`, `.agent/skills/proposal-review/SKILL.md`, `.codex/skills/proposal-review/SKILL.md`, `.goose/skills/proposal-review/SKILL.md`, `.cursor/skills/proposal-review/SKILL.md`, `.api-harness/skills/MANIFEST.json`, `.agent/skills/MANIFEST.json`, `.codex/skills/MANIFEST.json`, `.goose/skills/MANIFEST.json`, `.cursor/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`, `config/governance/evidence-freshness-boundaries.toml`, `config/governance/hygiene-baseline-registry.toml`.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
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
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - auto-linked governing or work-item specification.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - auto-linked governing or work-item specification.
- `DCL-SUPERSEDED-SOT-LEAKAGE-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - owner direction that canonical artifacts depend only on canonical evidence carriers and governed identities.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - preserves the independent dispatcher-configuration hold; this proposal excludes dispatcher configuration and runtime surfaces.
- _No additional directly applicable prior deliberation was found beyond the canonical owner boundary and the active exact-singleton ops authorization._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5584-CANONICAL-CONFIG-DECONTAMINATION-2026-07-18` - active project authorization covering `WI-5584`.

## Proposed Scope

- Replace live proposal-review skill lookups, evidence fields, and worker instructions that identify a noncanonical auxiliary source with stable Deliberation Archive, MemBase, numbered bridge, or content-hash identities.
- Regenerate or hunk-refresh only the five proposal-review projections, their five manifest entries, the proposal-review harness registry entry, and the affected rows in the two evidence registries.
- Preserve append-only historical artifacts and every unrelated foreign byte in the two dirty manifests; no whole-file manifest rewrite is authorized.
- Limit implementation to the fourteen declared configuration targets; source scripts, tests, dispatcher configuration, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded.

## Activity-Envelope Segmentation

This interactive session is a build envelope and files only the numbered bridge proposal plus governed project metadata. It grants and exercises no configuration authority. Any implementation of these fourteen targets requires a separate ops activity envelope, independent GO, exact claim, schema-v3 implementation start, and operation-time authorization.

## Existing Worktree Ownership

At proposal filing, `.agent/skills/MANIFEST.json` and `.api-harness/skills/MANIFEST.json` contain unrelated foreign additions not authored by this session. Implementation may change only the `proposal-review` manifest entries and must preserve every foreign byte exactly through hunk isolation.

## Cross-Harness Disposition

- **Claude Code**: Canonical proposal-review source; configuration behavior is updated directly.
- **Codex**: Generated proposal-review projection and manifest entry must match the canonical source hash.
- **Cursor**: Generated proposal-review projection and manifest entry must match the canonical source hash.
- **Antigravity**: Generated .agent proposal-review projection and manifest entry must match the canonical source hash.
- **API harness**: Generated proposal-review projection and manifest entry must match the canonical source hash.
- **Goose**: Generated proposal-review projection and manifest entry must match the canonical source hash.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5584; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5584-CANONICAL-CONFIG-DECONTAMINATION-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Ops activity-envelope child of WI-5582. Mutate only the canonical proposal-review skill, its five managed projections, five associated manifests, the harness capability registry, and the two governance evidence registries. Replace every live lookup, evidence field, or worker instruction that identifies the retired external advisory carrier with stable Deliberation Archive, MemBase, or numbered bridge identities and hashes, or with an explicit non-resolving historical label. Regenerate or hunk-refresh only proposal-review projection metadata. Preserve append-only historical artifacts and all unrelated foreign manifest hunks. Dispatcher configuration, TAFE state, runtime state, source scripts, and tests are excluded.",
  "after_behavior": "Replace noncanonical proposal-review and evidence-registry references with stable canonical identities across every managed harness projection.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5584",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      ".claude/skills/proposal-review/SKILL.md",
      ".api-harness/skills/proposal-review/SKILL.md",
      ".agent/skills/proposal-review/SKILL.md",
      ".codex/skills/proposal-review/SKILL.md",
      ".goose/skills/proposal-review/SKILL.md",
      ".cursor/skills/proposal-review/SKILL.md",
      ".api-harness/skills/MANIFEST.json",
      ".agent/skills/MANIFEST.json",
      ".codex/skills/MANIFEST.json",
      ".goose/skills/MANIFEST.json",
      ".cursor/skills/MANIFEST.json",
      "config/agent-control/harness-capability-registry.toml",
      "config/governance/evidence-freshness-boundaries.toml",
      "config/governance/hygiene-baseline-registry.toml"
    ],
    "linked_specifications": [
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001",
      "DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001",
      "DCL-SUPERSEDED-SOT-LEAKAGE-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "ADR-CROSS-HARNESS-PARITY-001",
      "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001",
      "DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
      "DCL-ACTIVITY-DISPOSITION-PROFILE-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Replace noncanonical proposal-review and evidence-registry references with stable canonical identities across every managed harness projection.",
    "scope": [
      "Replace live proposal-review skill lookups, evidence fields, and worker instructions that identify a noncanonical auxiliary source with stable Deliberation Archive, MemBase, numbered bridge, or content-hash identities.",
      "Regenerate or hunk-refresh only the five proposal-review projections, their five manifest entries, the proposal-review harness registry entry, and the affected rows in the two evidence registries.",
      "Preserve append-only historical artifacts and every unrelated foreign byte in the two dirty manifests; no whole-file manifest rewrite is authorized.",
      "Limit implementation to the fourteen declared configuration targets; source scripts, tests, dispatcher configuration, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path are excluded."
    ],
    "acceptance_criteria": [
      "The canonical proposal-review skill and every managed projection use only stable canonical evidence identities or explicit non-resolving historical labels.",
      "All five projection manifests and the harness capability registry carry correct proposal-review source hashes and preserve unrelated entries byte-for-byte.",
      "The two evidence registries contain no live lookup to a noncanonical auxiliary source and pass their existing validation and freshness tests.",
      "Implementation occurs only in an ops envelope after independent GO, and the final fourteen-target diff leaves dispatcher configuration and all disclosed foreign hunks untouched."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved configuration hunks under separate ops authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Inspect the canonical skill and registries proving no noncanonical location is identified as review evidence or worker authority. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run both proposal preflights and require the implementation report to use the governed numbered bridge writer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify proposals, decisions, evidence identities, projection receipts, and review outcomes remain durable governed artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights against the exact filed proposal with no missing specifications or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run existing proposal-review routing, adapter-generation, manifest, registry, evidence-freshness, and hygiene-baseline tests and report exact results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate the exact ops PAUTH, project, work item, inline target_paths, and project bridge-thread link. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify the proposal-review skill preserves one-at-a-time owner decision routing and does not treat evidence discovery as approval. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify every configuration target and generated projection remains inside E:/GT-KB and introduces no external live dependency. |
| `GOV-STANDING-BACKLOG-001` | Verify WI-5584 remains linked in MemBase through proposal, implementation, report, and terminal verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run direct skill and registry tests proving correctness across harnesses without relying on one hook implementation. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect traceability from each changed instruction or evidence field to its canonical identity, projection hash, test evidence, report, and verdict. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify active, historical, superseded, and unavailable evidence states remain explicit and do not silently resolve to auxiliary files. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Run a bounded scan of the fourteen targets proving live configuration uses only canonical evidence identities and explicit non-resolving historical labels. |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | Verify every removed live lookup or instruction is paired with a stable MemBase, Deliberation Archive, numbered bridge, or content-hash replacement and focused parity evidence. |
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run negative scans and projection checks proving no live lookup, path, or worker instruction can resolve a retired auxiliary source. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Validate evidence-freshness records use stable canonical identities, hashes, and fresh-read boundaries. |
| `ADR-CROSS-HARNESS-PARITY-001` | Regenerate or check all five managed projections and prove the canonical proposal-review behavior is equivalent across supported harnesses. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run adapter and manifest parity checks for all five projections with canonical source hashes and no unmanaged divergence. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Verify the harness capability registry advertises the same proposal-review contract and canonical source to every managed harness. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm configuration mutation occurs only in a separate ops activity envelope; this build session is limited to bridge and metadata filing. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Inspect the final configuration diff to prove no worker instruction grants direct dispatcher, TAFE, or harness-complex internal access. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Record and validate the ops configuration disposition at implementation start and operation time. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active exact-singleton WI-5584 ops authorization before any configuration edit and bind it into the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, exact claim, ops envelope, schema-v3 start, and operation-time authorization before mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the selected PAUTH covers WI-5584, configuration class, and exactly the fourteen declared targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Revalidate authorization for every configuration edit, projection generation, and governed evidence-producing side effect. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes and preserve all unrelated foreign additions in the two dirty manifests while changing only proposal-review entries. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run proposal-review, adapter, manifest, registry, freshness, and hygiene checks proving no review capability or harness support regresses. |

## Acceptance Criteria

- The canonical proposal-review skill and every managed projection use only stable canonical evidence identities or explicit non-resolving historical labels.
- All five projection manifests and the harness capability registry carry correct proposal-review source hashes and preserve unrelated entries byte-for-byte.
- The two evidence registries contain no live lookup to a noncanonical auxiliary source and pass their existing validation and freshness tests.
- Implementation occurs only in an ops envelope after independent GO, and the final fourteen-target diff leaves dispatcher configuration and all disclosed foreign hunks untouched.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a hunk-scoped revert of the approved configuration changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/skills/proposal-review/SKILL.md`
- `.api-harness/skills/proposal-review/SKILL.md`
- `.agent/skills/proposal-review/SKILL.md`
- `.codex/skills/proposal-review/SKILL.md`
- `.goose/skills/proposal-review/SKILL.md`
- `.cursor/skills/proposal-review/SKILL.md`
- `.api-harness/skills/MANIFEST.json`
- `.agent/skills/MANIFEST.json`
- `.codex/skills/MANIFEST.json`
- `.goose/skills/MANIFEST.json`
- `.cursor/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `config/governance/evidence-freshness-boundaries.toml`
- `config/governance/hygiene-baseline-registry.toml`

## Recommended Commit Type

`feat`
