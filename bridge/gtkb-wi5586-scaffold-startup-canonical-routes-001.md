NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Canonicalize project scaffolds and startup context routes

bridge_kind: prime_proposal
Document: gtkb-wi5586-scaffold-startup-canonical-routes
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5586-SCAFFOLD-STARTUP-DECONTAMINATION-V2-2026-07-18
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5586-SCAFFOLD-STARTUP-DECONTAMINATION-V2-2026-07-18","coverage":"exact_singleton","included_work_item_count":1,"specificity_rank":[0,1],"selected":true},{"project_authorization_id":"PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":false}]
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5586

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/scaffold.py", "groundtruth-kb/src/groundtruth_kb/bridge/context.py", "groundtruth-kb/src/groundtruth_kb/activity/ops.py", "scripts/session_self_initialization.py", "groundtruth-kb/templates/rules/deliberation-protocol.md", "groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md", "groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md", "groundtruth-kb/templates/project/AGENTS.md", "groundtruth-kb/templates/BRIDGE-INVENTORY.md", "groundtruth-kb/templates/hooks/kb-not-markdown.py", "docs/gtkb-systems-and-tools.md", "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/AGENTS.md", "platform_tests/scripts/test_ops_activity_context.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Converge project scaffolds, startup initialization, bridge context, activity operations, generated templates, documentation, fixtures, and focused tests on canonical advisory routes.

Work item description: Build-only scaffold and startup work that converges generated and runtime guidance on canonical numbered bridge, Deliberation Archive, MemBase, and Advisory Proposal routes.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5586` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, `groundtruth-kb/src/groundtruth_kb/bridge/context.py`, `groundtruth-kb/src/groundtruth_kb/activity/ops.py`, `scripts/session_self_initialization.py`, `groundtruth-kb/templates/rules/deliberation-protocol.md`, `groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`, `groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md`, `groundtruth-kb/templates/project/AGENTS.md`, `groundtruth-kb/templates/BRIDGE-INVENTORY.md`, `groundtruth-kb/templates/hooks/kb-not-markdown.py`, `docs/gtkb-systems-and-tools.md`, `groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py`, `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md`, `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/AGENTS.md`, `platform_tests/scripts/test_ops_activity_context.py`, `platform_tests/scripts/test_session_self_initialization.py`.

## Specification Links

- `DCL-SUPERSEDED-SOT-LEAKAGE-001` - auto-linked governing or work-item specification.
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
- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001` - auto-linked governing or work-item specification.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.
- `ADR-0001` - auto-linked governing or work-item specification.
- `SPEC-2098` - auto-linked governing or work-item specification.
- `GOV-SESSION-SELF-INITIALIZATION-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - auto-linked governing or work-item specification.
- `SPEC-ENVELOPE-DISCLOSURE-UI-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` - auto-linked governing or work-item specification.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` - auto-linked governing or work-item specification.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY - owner direction that canonical artifacts and generated guidance may depend only on canonical evidence carriers.
- DELIB-20260715-DISPATCHER-BLACKBOX-OPS-BUILD-ENVELOPES - separates build-only internal source mutation from ops-only configuration mutation; WI-5596 owns the two excluded registries.
- DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD - preserves the independent dispatcher-configuration hold; this proposal neither inspects nor mutates that surface.

## Owner Decisions / Input
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5586-SCAFFOLD-STARTUP-DECONTAMINATION-V2-2026-07-18` - active project authorization covering `WI-5586`.

## Proposed Scope

- Update the four internal source surfaces so scaffold and startup behavior expose only canonical numbered bridge, Deliberation Archive, MemBase, and Advisory Proposal routes.
- Update generated templates, hook template, documentation, and golden fixtures to match the canonical authority model while preserving explicit rejection guidance.
- Run and update the registry-presence, ops activity-context, session initialization, and golden scaffold coverage required by the sixteen exact targets.
- Exclude the WI-5585-owned scaffold assertion, both WI-5596 configuration registries, dispatcher configuration/control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5586; PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5586-SCAFFOLD-STARTUP-DECONTAMINATION-V2-2026-07-18; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Scaffold, startup, context, activity, template, documentation, and fixture surfaces still expose advisory routes that are not consistently derived from canonical numbered bridge, Deliberation Archive, or MemBase authority.",
  "after_behavior": "Converge project scaffolds, startup initialization, bridge context, activity operations, generated templates, documentation, fixtures, and focused tests on canonical advisory routes.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5586",
    "project": "PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/project/scaffold.py",
      "groundtruth-kb/src/groundtruth_kb/bridge/context.py",
      "groundtruth-kb/src/groundtruth_kb/activity/ops.py",
      "scripts/session_self_initialization.py",
      "groundtruth-kb/templates/rules/deliberation-protocol.md",
      "groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md",
      "groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md",
      "groundtruth-kb/templates/project/AGENTS.md",
      "groundtruth-kb/templates/BRIDGE-INVENTORY.md",
      "groundtruth-kb/templates/hooks/kb-not-markdown.py",
      "docs/gtkb-systems-and-tools.md",
      "groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py",
      "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md",
      "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/AGENTS.md",
      "platform_tests/scripts/test_ops_activity_context.py",
      "platform_tests/scripts/test_session_self_initialization.py"
    ],
    "linked_specifications": [
      "DCL-SUPERSEDED-SOT-LEAKAGE-001",
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
      "DCL-CANONICAL-CARRIER-NONAUTHORITY-001",
      "GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
      "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
      "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001",
      "DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001",
      "DCL-ACTIVITY-DISPOSITION-PROFILE-001",
      "GOV-WORK-TREE-HYGIENE-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
      "ADR-0001",
      "SPEC-2098",
      "GOV-SESSION-SELF-INITIALIZATION-001",
      "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001",
      "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
      "SPEC-ENVELOPE-DISCLOSURE-UI-001",
      "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001",
      "DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001",
      "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
      "GOV-HARNESS-ONBOARDING-CONTRACT-001",
      "ADR-CROSS-HARNESS-PARITY-001",
      "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001",
      "GOV-SESSION-ROLE-AUTHORITY-001",
      "DCL-SESSION-ROLE-RESOLUTION-001"
    ]
  },
  "expected_result": {
    "summary": "Converge project scaffolds, startup initialization, bridge context, activity operations, generated templates, documentation, fixtures, and focused tests on canonical advisory routes.",
    "scope": [
      "Update the four internal source surfaces so scaffold and startup behavior expose only canonical numbered bridge, Deliberation Archive, MemBase, and Advisory Proposal routes.",
      "Update generated templates, hook template, documentation, and golden fixtures to match the canonical authority model while preserving explicit rejection guidance.",
      "Run and update the registry-presence, ops activity-context, session initialization, and golden scaffold coverage required by the sixteen exact targets.",
      "Exclude the WI-5585-owned scaffold assertion, both WI-5596 configuration registries, dispatcher configuration/control, TAFE/runtime state, credentials, deployment, release, push, history rewrite, destructive cleanup, and every other path."
    ],
    "acceptance_criteria": [
      "Newly scaffolded and initialized sessions neither create, discover, load, advertise, nor emit advisory work through any route other than canonical numbered bridge, Deliberation Archive, MemBase, and Advisory Proposal surfaces.",
      "Generated templates, documentation, and golden fixtures agree byte-for-byte on the canonical route semantics required by their focused tests.",
      "The two configuration registries and the WI-5585-owned scaffold assertion are absent from the implementation diff.",
      "All focused tests and both ruff gates pass, and the final diff contains exactly the sixteen declared paths or a reviewed subset of them."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
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
| `DCL-SUPERSEDED-SOT-LEAKAGE-001` | Run focused negative scans across all sixteen targets proving unsupported operational advisory routes are absent while explicit rejection guidance remains. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate/live proposal preflights and file the later implementation report through the governed numbered bridge writer. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Verify generated guidance promotes decisions, findings, work, and verification into canonical durable artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and ADR/DCL clause preflights against the filed proposal with no missing specs or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute all declared focused tests plus ruff check and ruff format --check on Python targets and carry exact results into the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Validate Project Authorization, Project, Work Item, exact target_paths, and project bridge-thread linkage. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run startup and context tests proving owner decisions remain routed through the governed interactive decision channel. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify all source, template, fixture, documentation, test, report, and generated paths remain within E:/GT-KB. |
| `GOV-STANDING-BACKLOG-001` | Verify WI-5586 remains linked in MemBase throughout proposal, implementation, report, and terminal verification. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run scaffold and hook-template tests proving generated behavior remains valid when harness interception capabilities differ. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Inspect traceability from generated instructions through focused tests, proposal, implementation report, and review outcome. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Verify generated guidance exposes explicit advisory adoption, deferral, rejection, implementation, and verification lifecycle routes. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run scaffold, startup, and activity-context tests proving generated and runtime guidance names only numbered bridge, Deliberation Archive, and MemBase authority routes. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Verify startup and bridge context obtain current advisory state from canonical readers and do not embed a stale copied state surface. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate the active WI-5586 V2 exact-singleton authorization before any protected edit and record it in the schema-v3 start packet. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Require independent GO, matching claim, schema-v3 start, and operation-time authorization before every protected mutation. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify V2 covers WI-5586 source/test/documentation classes, excludes configuration, and binds the exact sixteen targets. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Check the selected V2 authorization before each protected edit and each evidence-producing operation with governed side effects. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Confirm only a build envelope may mutate the internal source/template paths and that configuration targets are absent from this proposal. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Verify generated ordinary-worker context exposes mediated canonical routes and no direct dispatcher, TAFE, or harness-complex internals. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Run ops activity-context and session initialization tests proving activity specialization remains distinct from ordinary-worker behavior. |
| `GOV-WORK-TREE-HYGIENE-001` | Capture pre-edit hashes and final per-target diff, preserving unrelated dirty bytes and rejecting any seventeenth path. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run scaffold golden, startup, registry-presence, and activity-context regressions with no loss of supported initialization behavior. |
| `ADR-0001` | Inspect generated templates and golden fixtures to prove MemBase, operational notepad, and Deliberation Archive tiers remain distinct and correctly named. |
| `SPEC-2098` | Run scaffold and template assertions proving Deliberation Archive search and citation guidance survives without any alternate report store. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Run session self-initialization tests covering Prime, Loyal Opposition, ordinary, and build contexts with canonical advisory routing. |
| `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` | Verify startup retains proactive owner-facing priorities while routing durable findings through canonical artifacts. |
| `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` | Run startup tests proving canonical advisory discovery uses bounded compact readers rather than full-history or duplicate-directory scans. |
| `SPEC-ENVELOPE-DISCLOSURE-UI-001` | Run disclosure tests proving activity and role surfaces remain correctly rendered after canonical route replacement. |
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` | Run scaffold golden and initialization tests proving the generated guidance remains valid for the supported harness role set. |
| `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` | Run init-keyword tests proving canonical startup relay behavior and non-matching prompt behavior remain unchanged. |
| `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` | Execute canonical init-keyword grammar tests across generated and runtime startup context. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run registry-presence and scaffold golden tests proving every generated harness surface retains the onboarding contract. |
| `ADR-CROSS-HARNESS-PARITY-001` | Compare template and golden fixture semantics across the scaffolded role surfaces after route replacement. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run deterministic scaffold registry and golden-file tests proving no supported harness receives a divergent authority route. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Run startup context tests proving role authority remains session-resolved and is not inferred from advisory storage or dispatcher internals. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Execute Prime and Loyal Opposition context tests proving canonical route changes do not alter role resolution precedence. |

## Acceptance Criteria

- Newly scaffolded and initialized sessions neither create, discover, load, advertise, nor emit advisory work through any route other than canonical numbered bridge, Deliberation Archive, MemBase, and Advisory Proposal surfaces.
- Generated templates, documentation, and golden fixtures agree byte-for-byte on the canonical route semantics required by their focused tests.
- The two configuration registries and the WI-5585-owned scaffold assertion are absent from the implementation diff.
- All focused tests and both ruff gates pass, and the final diff contains exactly the sixteen declared paths or a reviewed subset of them.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/context.py`
- `groundtruth-kb/src/groundtruth_kb/activity/ops.py`
- `scripts/session_self_initialization.py`
- `groundtruth-kb/templates/rules/deliberation-protocol.md`
- `groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md`
- `groundtruth-kb/templates/project/codex-bootstrap/codex-review-operating-contract.md`
- `groundtruth-kb/templates/project/AGENTS.md`
- `groundtruth-kb/templates/BRIDGE-INVENTORY.md`
- `groundtruth-kb/templates/hooks/kb-not-markdown.py`
- `docs/gtkb-systems-and-tools.md`
- `groundtruth-kb/tests/adopter/test_registry_entry_present_for_every_scaffolded_file.py`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md`
- `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/AGENTS.md`
- `platform_tests/scripts/test_ops_activity_context.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Recommended Commit Type

`feat`
