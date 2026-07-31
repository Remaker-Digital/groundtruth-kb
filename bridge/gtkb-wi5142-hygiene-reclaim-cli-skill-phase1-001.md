NEW

# GT-KB WI-5142 Hygiene Reclaim CLI And Managed Skill - Non-DB Implementation Child

bridge_kind: prime_proposal
Document: gtkb-wi5142-hygiene-reclaim-cli-skill-phase1
Version: 001
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
Parent Bridge: gtkb-wi5142-hygiene-reclaim-cli-skill
Parent GO: version 004

target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_hygiene_reclaim_cli.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "platform_tests/scripts/test_worktree_finalization_triage.py", ".claude/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py", "platform_tests/skills/test_skill_catalog_contract.py"]

implementation_scope: source | test | configuration | managed-skill
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the non-database portion of the independently approved WI-5142 hygiene-reclaim design. The parent implementation-start gate was refused because an unrelated, non-terminal implementation report already claims the dirty shared MemBase binary. That refusal is correct and must not be bypassed. Direct read-only collision evaluation confirms the 16 targets above have no peer-report dirty-path conflict.

This child adds the deterministic `gt hygiene reclaim` command family, lifecycle-aware inventory refresh behavior, focused tests, and the canonical `gtkb-hygiene-reclaim` managed skill. It intentionally makes no canonical registry or MemBase projection mutation. The known resource-alias registry defect remains visible in plan output and blocks live trash at operation time. The parent registry-correction scope remains deferred until the shared-binary peer reaches a terminal state or a separately governed row-scoped finalization mechanism exists.

No live trash, restore, prune, purge, Git garbage collection, reflog expiration, stash drop, branch deletion, worktree mutation, commit, push, release, deployment, credential operation, or external mutation is authorized by this child.

## Existing Capability Reuse

- Reuse the existing hygiene stray and auto-resolve classifiers as inputs; do not create another dirty-path taxonomy.
- Reuse the typed SoT registry loader and parity report as preservation and readiness evidence. Registry matches are preservation vetoes; absence from the registry is never deletion authority.
- Reuse the existing inventory refresh command and change only its loader and lifecycle/path-class expansion semantics.
- Reuse the canonical managed-skill pipeline: `.claude` source, generated Codex adapter, capability registry, manifest, and catalog tests.
- Enumerate per-run manifests for history; do not create a second artifact registry, cleanup queue, or aggregate authority.

## Proposed Implementation And CLI Contract

### `gt hygiene reclaim plan`

- Collect fresh registry loader/parity/reality evidence, root identity, HEAD, Git status, refs, worktree HEADs, stashes, valid reflog object IDs, every index stage, loose-object metadata, and disk-free state.
- Protect every registry match and every Git object rooted by refs, worktrees, stashes, valid reflogs, and indexes.
- Classify malformed Git temporary objects separately from valid unreferenced loose objects; preserve ambiguous artifacts.
- Apply explicit age and candidate-class rules. Untracked, ignored, unreachable, old, or large status alone never authorizes trash.
- Write one immutable run directory containing `manifest.json`, `summary.json`, and append-only `events.jsonl`, with stable plan and item hashes.
- Emit compact output by default while retaining exact item evidence on disk.
- Report registry correctness defects and continue read-only candidate enumeration, but mark the run non-executable and refuse `trash` while any blocking registry, Git-root, hash, or root-identity evidence is incomplete or contradictory.

### `gt hygiene reclaim history`

- Enumerate per-run manifests directly, reconstruct item state from append-only events, and verify manifest/event hashes.
- Report planned, trashed, restored, refused, corrupt, stale, partial, and unsupported states without an aggregate index.

### `gt hygiene reclaim trash`

- Require an exact run ID, immutable plan hash, exact item IDs, non-empty batch-specific owner/apply evidence, quiescence evidence, and operation-time revalidation.
- Refuse tracked, registered, protected, bridge, active-session, changed, out-of-root, cross-device, colliding, ambiguous, or newly reachable candidates.
- Move only selected items atomically into same-volume in-root reversible trash, preserving original paths and appending receipts.
- Report logical bytes removed from active scan paths separately from physical bytes reclaimed, which are zero for same-volume trash.

### `gt hygiene reclaim restore`

- Require exact run and item IDs; validate payload identity and history; refuse overwrite, path escape, changed payload, missing payload, or active destination.
- Restore atomically and append receipts.

All actuator behavior is exercised only in disposable test repositories under this GO. The live workspace receives a read-only plan after independent verification and separate execution authorization.

## Inventory Refresh Scope

- Replace the permissive duplicate registry parser with the typed loader.
- Classify MemBase records, external service/task records, archives, generated records, globs, directories, and concrete files distinctly.
- Do not recursively enumerate generated runtime directories; validate their declared path and generator contract only.
- Keep active file/glob/directory expansion deterministic and bounded.
- Preserve existing string-scan behavior except where lifecycle/path-class consistency requires a tested correction.
- Surface the known resource-alias path defect as a blocking registry-reality finding; do not mutate registry authority in this child.

## Managed Skill Structural Review

Registry Authority Assessment: PASS. The capability registry remains the durable parity declaration; the `.claude` skill is canonical; the `.codex` skill and manifest are generated projections.

Target-Path Completeness Assessment: PASS. All source, CLI, canonical skill, generated adapter, manifest, capability-registry, and focused test paths are declared.

Stale-Assumption Warnings: the existing `gtkb-hygiene-sweep` skill remains active for configured content-drift scans and child routing. This child creates no retired registry, alternate queue, router entry, or implied non-Codex adapter.

Lifecycle Compliance: PASS subject to independent GO and implementation-start authorization for this exact child.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - report-first hygiene, fresh evidence, non-mutating defaults, and exact-batch apply evidence.
- `SPEC-INTAKE-97538b` - registry authority for cleanup essentiality; Git state is not essentiality authority.
- `SPEC-INTAKE-99a602` - preservation-first high-risk cleanup while reliable backup coverage is absent.
- `GOV-PLATFORM-SOT-REGISTRY-001` - single typed platform registry and projection; this child reads but does not mutate them.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - deterministic enumeration, hashing, history, transitions, and recovery.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - explicit KEEP/QUARANTINE classification and audit preservation.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - fail-closed evaluation of incomplete, stale, partial, corrupt, or contradictory evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - preserve current behavior and evidence surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable artifact graph and explicit lifecycle states.
- `SPEC-1853` - stable managed-skill identity and frontmatter.
- `ADR-REGISTRY-DISCOVERY-001` - skill registration, discovery, adapter loadability, manifest agreement, and no orphans.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - supported and unsupported harness dispositions.
- `SPEC-SKILL-USAGE-ROUTER-001` - scenario router remains byte-untouched; the operator-invoked skill is not added to it.
- `GOV-10` - tests and skill use the production `gt` interface rather than a private duplicate script.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - governed approval, linkage, and verification gates.
- `GOV-STANDING-BACKLOG-001` - this child remains under WI-5142 and creates no competing backlog authority.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - bounded cleanup, lifecycle classification, history, deterministic guards, and no unbounded purge.
- `DELIB-202666274` - active project-scope PAUTH for this non-live implementation.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - registry-first preservation after essential local artifact loss.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` and `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - cleanup essentiality and backup-risk requirements.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic service placement.
- Parent bridge versions 001 through 004 - full design, one narrow NO-GO, corrected linkage, and independent GO. This child changes only executable target scope in response to the implementation-start shared-path collision.

## Owner Decisions / Input

The owner directed urgent investigation, implementation, testing, and execution of a repeatable deterministic hygiene capability with reversible trash and tracked history. That direction selects WI-5142 and this delivery surface.

No new owner decision is required for the non-live 16-target implementation. The active PAUTH authorizes source, test, configuration, managed-skill, bridge, and runtime evidence while forbidding destructive cleanup and Git mutation. Live execution still requires the exact generated plan and a separate batch-specific owner-approved apply record.

## Requirement Sufficiency

Existing requirements sufficient. The linked hygiene, preservation, registry-authority, deterministic-service, lifecycle, managed-skill, routing, production-interface, and evaluability contracts fully govern this non-database child. WI-5142 records the bounded cleanup-ledger gap, and the parent bridge independently approved the complete design. No new or revised requirement is required before implementation.

## Spec-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Disposable-repository tests prove report-first default, exact evidence requirements, fresh revalidation, refusal of live-root mutation, and no permanent purge. Existing strays/auto-resolve tests remain green. |
| `SPEC-INTAKE-97538b`, `SPEC-INTAKE-99a602` | Tests prove registered matches veto trash, absence/untracked/ignored/unreachable status never authorizes trash, changed candidates fail closed, and restore never overwrites. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Inventory fixtures prove typed lifecycle/path-class behavior, no generated-tree recursion, and a blocking registry-reality finding without registry mutation. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Tests prove stable hashes, compact output, append-only ordered events, partial receipts, and deterministic history reconstruction without an aggregate index. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Tests prove explicit KEEP/QUARANTINE and non-passing corrupt, unsupported, stale, partial, and contradictory states. |
| `SPEC-1853`, `ADR-REGISTRY-DISCOVERY-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Focused tests prove canonical identity/frontmatter, registry entry, generated Codex adapter, manifest SHA agreement, loadability, role scope, unsupported dispositions, and no orphan. |
| `SPEC-SKILL-USAGE-ROUTER-001`, `GOV-10` | Router/catalog regressions remain green; the scenario table remains untouched; skill tests require production `gt hygiene reclaim` commands and reject a duplicate private CLI. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing inventory, strays, auto-resolve, catalog, adapter, and CLI tests remain green. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_hygiene_reclaim.py platform_tests/scripts/test_hygiene_reclaim_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_hygiene_reclaim.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_reclaim_cli.py platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_hygiene_reclaim.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_reclaim_cli.py platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli admin inventory refresh --json
```

Run the canonical managed-skill adapter generation, then its read-only drift check. The operation must change only the declared new Codex adapter, manifest entry, and capability-registry record; every pre-existing adapter must remain byte-identical.

## Cross-Harness Disposition

- **Claude Code:** canonical native managed-skill source.
- **Codex:** generated adapter with manifest and capability-registry SHA agreement.
- **Antigravity, Cursor, Ollama, OpenRouter, Goose, and Alibaba Cloud Studio:** no native adapter or parity claim; each may use the deterministic production CLI.
- **Future harnesses:** require a separate governed registry declaration and adapter path before claiming native parity.

This is an explicit per-harness disposition, not a waiver.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5142; parent bridge versions 001-004; implementation-start shared-binary collision observed 2026-07-16",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; GOV-PLATFORM-SOT-REGISTRY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Operators use one gtkb-hygiene-reclaim skill and the production gt hygiene reclaim command family.",
  "before_behavior": "Existing scans are read-only but verbose, generated registry trees expand recursively, and no reversible candidate ledger exists.",
  "after_behavior": "A compact deterministic service plans, records, revalidates, and restores exact candidates while refusing execution when registry or Git preservation evidence is non-passing.",
  "self_descriptive_naming": "plan, history, trash, and restore map directly to their operator actions.",
  "obsolete_guidance_disposition": "Existing hygiene-sweep, strays, and auto-resolve behavior remains supported; no alternate registry or queue is introduced.",
  "history_preservation": "Per-run manifests and append-only receipts preserve actions without replacing the canonical registry or numbered bridge chain.",
  "baseline": {"parent_go": 4, "authorized_targets": 16, "shared_binary_targets_deferred": 2},
  "expected_result": {"default_output": "compact", "live_cleanup_under_go": 0, "physical_bytes_reclaimed_by_trash": 0},
  "rollback": {"instructions": "Revert only this child's exact source, test, skill, manifest, and capability-registry hunks.", "test": "Re-run focused regressions, lint, format, adapter drift, and byte comparisons for pre-existing dirty targets."},
  "hard_invariants": ["No database or canonical registry mutation in this child.", "No live trash or Git mutation under this GO.", "Registry matches and all Git recovery roots are preserved.", "Pre-existing dirty bytes remain intact."],
  "fail_closed_conditions": ["GO, claim, or implementation-start evidence is absent.", "Registry or Git-root evidence is incomplete or contradictory.", "A mutation falls outside target_paths.", "An exact batch lacks owner/apply evidence."],
  "essential_context_preservation": "The parent design and GO, SoT registry, MemBase projection, bridge history, WI, PAUTH, existing classifiers, and deferred correction remain visible and authoritative."
}
```

## Acceptance Criteria

1. The four command families are available, compact by default, deterministic, and fully tested in disposable roots.
2. Planning audits all registry and Git preservation evidence, identifies exact candidates, and marks live execution blocked on the known registry defect.
3. Inventory refresh is typed, lifecycle-aware, and bounded; generated runtime trees are not recursively expanded.
4. The canonical skill, generated Codex adapter, manifest, capability registry, CLI, and tests agree; no other adapter changes.
5. Focused regressions, lint, format, adapter drift, applicability, clause, target coverage, and non-impairment gates pass.
6. No live cleanup, registry/database mutation, Git mutation, commit, push, release, or deployment occurs under this GO.

## Risk And Rollback

Primary risk is false classification of recoverable work or Git objects. The implementation protects every registered match and every fresh Git root, requires age plus exact identity, revalidates at operation time, moves rather than deletes, and refuses ambiguous evidence. Inventory semantic regression is bounded by lifecycle/path-class fixtures and existing tests. Shared dirty targets are handled hunk-by-hunk; unrelated staged and unstaged bytes are preserved.

Rollback only this child's exact hunks and generated skill records, then rerun focused tests and drift checks. Runtime test repositories are disposable. Live trash is outside scope, so no live restoration is needed for implementation rollback.

## Recommended Commit Type

`feat(hygiene):`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
