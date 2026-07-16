REVISED

# GT-KB WI-5142 Deterministic Hygiene Reclaim CLI And Managed Skill - Revision

bridge_kind: prime_proposal
Document: gtkb-wi5142-hygiene-reclaim-cli-skill
Version: 003
Responds to: bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-16T01-48-03Z-prime-builder-A-b8e790
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive Prime Builder; reasoning effort xhigh; approval policy never

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5142

target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_hygiene_reclaim_cli.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "config/registry/sot-artifacts.toml", "groundtruth.db", ".claude/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py", "platform_tests/skills/test_skill_catalog_contract.py"]

implementation_scope: source | test | configuration | managed-skill | registry-projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Claim

This revision resolves the sole P1 finding in the version 002 NO-GO. It adds all governing managed-skill contracts to the proposal and maps them to focused catalog, adapter, manifest, capability-registry, router, and production-interface verification. No implementation target, CLI behavior, registry correction, cleanup boundary, owner-approval boundary, or execution authority changes from version 001.

## Specification Links

The following links from version 001 remain governing:

- `GOV-WORK-TREE-HYGIENE-001` - deterministic report-first hygiene, fresh evidence, non-mutating defaults, and exact-batch owner-approved apply evidence.
- `SPEC-INTAKE-97538b` - tracked SoT registry authority for cleanup essentiality; Git state is not essentiality authority.
- `SPEC-INTAKE-99a602` - registry-driven preservation for high-risk cleanup while reliable backup coverage is absent.
- `GOV-PLATFORM-SOT-REGISTRY-001` - the TOML registry and MemBase projection are the single platform SoT inventory.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - deterministic enumeration, hashing, transitions, recovery, and event history belong in services.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - explicit STRIP/KEEP/QUARANTINE classification and audit preservation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - fail-closed evaluation with current, lifecycle-aware evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - preservation of current GT-KB behavior and evidence surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable plan, risk, decision, and execution evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceable source, skill, test, manifest, receipt, and bridge artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - explicit candidate, preserved, quarantined, restored, refused, and unsupported states.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO, matching claim, and implementation-start authorization before protected mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, and WI linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - mapped test execution in the report and independent verification.
- `GOV-STANDING-BACKLOG-001` - this work extends WI-5142 without creating a competing backlog.

The following managed-skill contracts are added by this revision:

- `SPEC-1853` - Stable Skill/Tool Identity Contract; governs valid, stable `gtkb-hygiene-reclaim` skill frontmatter and identity.
- `ADR-REGISTRY-DISCOVERY-001` - governs capability-registry registration, discoverability, Codex adapter loadability, manifest agreement, and no-orphan behavior.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - governs explicit harness registration, supported/unsupported disposition, and capability-floor evidence.
- `SPEC-SKILL-USAGE-ROUTER-001` - governs scenario-to-skill resolution. The existing scenario/router table remains byte-untouched; the new operator-invoked skill is intentionally not added to that table, which is not an implementation target.
- `GOV-10` - governs reuse of the production `gt` CLI interface from the skill instead of introducing a duplicate script or private execution path.

## Prior Deliberations

Version 001's reviewed prior-deliberation set remains authoritative and unchanged. In particular, `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER`, `DELIB-202666274`, `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY`, and `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` continue to govern bounded cleanup, active authorization, registry-first preservation, and deterministic service placement. The version 002 review found no contrary prior deliberation and required only the managed-skill specification linkage corrected here.

## Owner Decisions / Input

The owner direction and approval boundary from version 001 are carried forward unchanged. The owner selected urgent implementation and testing of the deterministic CLI and managed skill. The active PAUTH covers this non-live implementation slice but forbids destructive cleanup and Git mutation. This revision does not authorize a live `trash`, `restore`, prune, purge, garbage-collection, commit, push, release, or deployment operation. An exact generated batch still requires separate batch-specific owner-approved apply evidence and matching authorization.

## Requirement Sufficiency

Existing requirements sufficient. The complete requirement-sufficiency analysis in version 001 remains unchanged: the linked hygiene, registry-authority, preservation, deterministic-service, lifecycle, managed-skill, routing, production-interface, and evaluability contracts fully govern this implementation slice. WI-5142 already records the bounded-cleanup-ledger gap. No new or revised requirement is required before implementation.

## Findings Addressed

### F1 [P1] Managed-skill deliverable lacked governing specification linkage

Response: resolved. `SPEC-1853`, `ADR-REGISTRY-DISCOVERY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `SPEC-SKILL-USAGE-ROUTER-001`, and `GOV-10` are now linked above. The managed-skill verification row below maps each contract to executable checks. The scenario/router table is expressly out of scope and remains untouched; production-interface reuse is verified by requiring the skill to invoke `gt hygiene reclaim` rather than a new helper CLI.

## Scope Changes

None. The target paths, implementation design, registry correction, reversible-trash model, non-live GO boundary, verification commands, acceptance criteria, non-impairment disposition, and rollback from version 001 remain unchanged.

## Pre-Filing Preflight

The completed revision candidate is subject to the governed revision helper's mandatory credential scan, proposal applicability preflight, ADR/DCL clause preflight, exact version-chain transition check, and append-only bridge writer. The file operation is refused unless those checks pass. All newly cited specification IDs are also checked directly in MemBase before filing.

## Spec-Derived Verification Plan

The version 001 mappings for hygiene safety, registry authority, deterministic history, obsolete-reference classification, evaluability, and modernization non-impairment remain unchanged. The corrected managed-skill mapping is:

| Governing surface | Required verification |
| --- | --- |
| `SPEC-1853` | `platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py` and `test_skill_catalog_contract.py` verify stable canonical name, required YAML frontmatter, valid description, and supported role scope. |
| `ADR-REGISTRY-DISCOVERY-001` | Focused tests verify canonical `.claude` source, capability-registry entry, generated Codex adapter, Codex manifest entry, matching SHA values, loadability, and no orphaned skill. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused tests verify the capability registry declares Codex support and gives explicit unsupported dispositions for other harnesses without implying undeclared adapters. |
| `SPEC-SKILL-USAGE-ROUTER-001` | Existing router/catalog tests remain green and byte checks prove the canonical scenario table is untouched; the intentionally operator-invoked skill is not required to be scenario-referenced. |
| `GOV-10` | Skill-content tests require use of the production `gt hygiene reclaim plan/history/trash/restore` interface and reject a duplicate script/private execution path. |

The planned test, lint, format, registry-validation, inventory-refresh, and adapter-drift commands listed in version 001 remain the required verification set.

## Managed Skill Structural Review

Registry authority remains `config/agent-control/harness-capability-registry.toml`; the `.claude` skill is canonical, and the Codex skill plus manifest are generated projections. All canonical, generated, registry, manifest, CLI, and focused test paths remain in `target_paths`. The existing `gtkb-hygiene-sweep` skill remains intact. No retired registry, bridge queue, or undeclared adapter is introduced. The five added managed-skill specifications and the verification table above close the only structural-review gap identified in version 002.

## Cross-Harness Disposition

- **Claude Code:** the `.claude` `gtkb-hygiene-reclaim` skill is the canonical managed source and provides native behavior.
- **Codex:** the `.codex` adapter is generated from the canonical source; its manifest and capability-registry hashes must agree exactly.
- **Antigravity:** no native adapter is introduced or claimed; the deterministic production `gt hygiene reclaim` CLI remains available.
- **Cursor:** no native adapter is introduced or claimed; the deterministic production CLI remains available.
- **Ollama:** no native adapter is introduced or claimed; the deterministic production CLI remains available.
- **OpenRouter:** no native adapter is introduced or claimed; the deterministic production CLI remains available.
- **Goose:** no native adapter is introduced or claimed; the deterministic production CLI remains available.
- **Alibaba Cloud Studio:** no native adapter is introduced or claimed; the deterministic production CLI remains available.
- **Future harnesses:** native parity requires a separate governed registry declaration and adapter path; this proposal creates no implied support.

Focused catalog tests must fail if canonical source, Codex adapter, manifest, capability-registry declaration, role scope, or unsupported-harness disposition drifts. This is an explicit per-harness parity disposition, not a waiver.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5142; bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-001.md; bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-002.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; SPEC-1853; ADR-REGISTRY-DISCOVERY-001; GOV-HARNESS-ONBOARDING-CONTRACT-001; SPEC-SKILL-USAGE-ROUTER-001; GOV-10",
  "primary_route": "Operators use the canonical gtkb-hygiene-reclaim managed skill and production gt hygiene reclaim command family; no duplicate script or router entry is introduced.",
  "before_behavior": "Version 001 completely specified the hygiene implementation but omitted the managed-skill governing specifications from its traceability map.",
  "after_behavior": "The implementation behavior and target set are unchanged; the managed skill is now linked to identity, discovery, onboarding, routing, and production-interface contracts with executable verification.",
  "self_descriptive_naming": "The gtkb-hygiene-reclaim name and plan, history, trash, and restore commands remain unchanged and map directly to their operator actions.",
  "obsolete_guidance_disposition": "No guidance is removed; the existing hygiene-sweep skill and scenario router remain unchanged.",
  "history_preservation": "Versions 001 and 002 remain immutable; this REVISED version records the correction without rewriting prior history.",
  "baseline": {
    "proposal_version": 1,
    "review_version": 2,
    "blocking_findings": 1
  },
  "expected_result": {
    "managed_skill_specs_added": 5,
    "implementation_scope_changes": 0,
    "live_cleanup_authorized": 0
  },
  "rollback": {
    "instructions": "Leave this revision unapproved or revert only later implementation hunks authorized by this bridge; never rewrite the numbered bridge chain.",
    "test": "Re-run applicability, clause, target-coverage, managed-skill catalog, adapter, manifest, and production CLI tests."
  },
  "hard_invariants": [
    "No protected implementation before independent GO, claim, and implementation-start evidence.",
    "The scenario/router table remains byte-untouched.",
    "The skill reuses the production gt CLI.",
    "No live cleanup or Git mutation is authorized by this revision.",
    "Pre-existing dirty bytes are preserved."
  ],
  "fail_closed_conditions": [
    "Managed-skill identity, registry, adapter, manifest, role-scope, router non-impairment, or production-interface checks fail.",
    "Any planned mutation falls outside target_paths or the active PAUTH.",
    "Independent GO, matching claim, or implementation-start evidence is absent."
  ],
  "essential_context_preservation": "The original proposal, NO-GO, SoT registry, MemBase projection, current hygiene classifiers, and exact authorization boundaries remain authoritative and intact."
}
```

## Risk And Rollback

No new implementation risk is introduced by this linkage-only revision. The original primary risks remain false cleanup classification, incomplete Git recovery-root protection, inventory semantic regression, and entanglement with pre-existing dirty bytes. The original fail-closed controls and hunk-scoped rollback remain mandatory. Before implementation, rollback is simply to leave version 003 unapproved; prior bridge versions remain immutable. After implementation, revert only this thread's exact source, test, registry-row, projection, skill, manifest, and capability-registry hunks while preserving all pre-existing dirty content.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
