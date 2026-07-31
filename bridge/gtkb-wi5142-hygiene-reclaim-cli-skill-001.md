NEW

# GT-KB WI-5142 Deterministic Hygiene Reclaim CLI And Managed Skill

bridge_kind: prime_proposal
Document: gtkb-wi5142-hygiene-reclaim-cli-skill
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

target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_hygiene_reclaim_cli.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_work_tree_stray_detector.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "config/registry/sot-artifacts.toml", "groundtruth.db", ".claude/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/gtkb-hygiene-reclaim/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py", "platform_tests/skills/test_skill_catalog_contract.py"]

implementation_scope: source | test | configuration | managed-skill | registry-projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement the first bounded WI-5142 hygiene-reclaim slice by extending the existing read-only hygiene stack instead of creating a competing classifier or artifact registry. Add `gt hygiene reclaim` with deterministic `plan`, `history`, `trash`, and `restore` subcommands, compact machine-readable summaries, immutable plan hashes, append-only event history, and fail-closed revalidation. Add the dedicated managed skill `gtkb-hygiene-reclaim` to orchestrate registry validation, compact planning, exact-batch owner approval, execution, restore verification, and reporting without loading full inventory payloads into model context.

The implementation must distinguish three quantities: bytes in the active tree, bytes moved into reversible in-root trash, and bytes actually reclaimed from the physical volume. Moving content into `.gtkb-state/hygiene-reclaim/trash/{run_id}/` is reversible and can remove high-cost objects from active Git scans, but it does not claim physical-disk reclamation. Permanent purge, Recycle Bin emptying, Git garbage collection, reflog expiration, stash dropping, branch deletion, worktree pruning, commit, push, release, deployment, credential handling, and live cleanup execution are outside this implementation GO.

The live investigation motivating this slice found:

- `gt registry validate --json`: 47 TOML rows and 47 MemBase projection rows in sync, but parity alone does not prove completeness or correct expansion semantics.
- `gt admin inventory refresh --json`: approximately 908,920 expanded files because generated `.gtkb-state/` is recursively scanned; external scheduled-task URIs and an archived missing bridge index are also conflated with ordinary missing files.
- One active registry path is wrong: `project-resource-alias-registry` points to an obsolete `.claude/rules/` location, while the current artifact is `config/agent-control/project-resource-aliases.toml`.
- `gt hygiene strays`: 1,255 dirty paths, 1,185 routed to manual review, and roughly 450,000 tokens of raw JSON, which is unsuitable for a recurring deterministic operation.
- `.git` is approximately 250 GB; `.git/objects` accounts for nearly all of it. `git count-objects -v` reports about 216 GiB of loose objects plus 36 `tmp_obj_*` garbage files totaling about 3.0 GiB. There are 1,693 loose objects larger than 50 MiB totaling about 231.9 GB; a sampled unreachable object is a SQLite blob. Reachable objects from current refs consume about 5.0 GB. These are investigation facts, not deletion authority.
- `git worktree prune --dry-run --verbose --expire now` reports 36 stale/prunable worktree metadata entries. This proposal does not authorize pruning them.

## Existing Capability Reuse

- Reuse `groundtruth_kb.hygiene.auto_resolve` and `gt hygiene strays` classifications as inputs; do not duplicate their dirty-path taxonomy.
- Reuse `config/registry/sot-artifacts.toml` through the typed `groundtruth_kb.project.sot_registry` loader. Registry matches are preservation vetoes, never deletion authorization.
- Keep `config/registry/sot-artifacts.toml` as the only platform SoT registry and `groundtruth.db` as its projection. No second artifact registry or aggregate run index is introduced.
- Enumerate per-run manifests for `history`; do not create an aggregate queue or summary authority.
- Reuse the canonical managed-skill pipeline: `.claude` source, generated Codex adapter, capability registry, Codex manifest, and focused catalog tests.

## Proposed Implementation and CLI Contract

### `gt hygiene reclaim plan`

- Read fresh registry TOML/projection parity, registry-to-disk reality, Git status, refs, worktree HEADs, stash refs, reflog object IDs, index object IDs, loose-object metadata, and disk-free state.
- Use typed registry lifecycle semantics. `membase:` and external URI records are validated by class, archive records are not active-missing failures, generated directory records are checked for existence without recursive content enumeration, and active file/glob/directory records retain deterministic expansion.
- Preserve every registered artifact match. Absence from the registry is not sufficient cleanup authority.
- Protect all Git objects reachable from refs, worktree HEADs, stashes, valid reflog entries, and every index stage before classifying a loose object as a candidate.
- Classify malformed Git temporary objects separately from valid-but-unreferenced loose objects. Apply an explicit age threshold and capture the evidence source for every classification.
- Write `.gtkb-state/hygiene-reclaim/runs/{run_id}/manifest.json`, `summary.json`, and `events.jsonl`. The manifest records schema version, root identity, HEAD, registry hash, plan hash, actor/session, source commands, candidate IDs, path/object identity, size, timestamps, and preservation reasons.
- Emit a compact stdout summary by default. Full item payloads remain on disk and are available only through exact `history --run-id` or `--item-id` reads.

### `gt hygiene reclaim history`

- Enumerate per-run manifests directly and provide compact list/show output.
- Validate manifest and event hash chains and report corrupt, partial, unsupported, or stale runs fail closed.
- Report planned, trashed, restored, refused, and purged states. This slice never emits a purged event.

### `gt hygiene reclaim trash`

- Require one prior plan, exact candidate IDs, the immutable plan hash, non-empty batch-specific owner/apply evidence references, and operation-time revalidation.
- Refuse tracked files, registered artifacts, protected paths, bridge history, active-session paths, current refs/worktree/stash/reflog/index objects, changed files, hash mismatches, path escapes, destination collisions, cross-device moves, missing quiescence evidence, or any unsupported candidate class.
- Move only selected candidates atomically to `.gtkb-state/hygiene-reclaim/trash/{run_id}/payload/{original_relative_path}`, preserving the original path in the manifest. Do not delete.
- Append one event per attempted item and a batch receipt. Partial failure stops further moves and leaves completed items restorable.
- Report logical bytes removed from active scan paths separately from physical bytes reclaimed, which remain zero for same-volume trash.

### `gt hygiene reclaim restore`

- Require the run ID and exact item IDs.
- Verify payload identity and event history; refuse overwrite, path escape, changed payload, missing payload, or active destination.
- Restore atomically to the original path and append restore receipts.

## Registry Correction Scope

1. Correct the `project-resource-alias-registry` storage path to `config/agent-control/project-resource-aliases.toml`.
2. Make inventory refresh use the typed registry loader and lifecycle/path-class semantics rather than the permissive second TOML parser.
3. Stop recursive file expansion for generated registry trees during refresh. Preserve generated-tree path authority and existence checks.
4. Treat `membase:`, external service/task URI, archive, generated, glob, directory, and concrete file records distinctly in the refresh report.
5. Preserve existing inventory string-scan behavior except where lifecycle/path-class consistency is required and covered by explicit regression tests.
6. Sync only the corrected SoT registry projection through `gt registry sync`; no raw SQL and no unrelated MemBase mutation.

## Managed Skill Structural Review

Registry Authority Assessment: PASS. `config/agent-control/harness-capability-registry.toml` remains the durable skill parity declaration; `.claude/skills/gtkb-hygiene-reclaim/SKILL.md` is canonical; `.codex/skills/gtkb-hygiene-reclaim/SKILL.md` and `.codex/skills/MANIFEST.json` are generated projections.

Target-Path Completeness Assessment: PASS with all canonical source, Codex adapter, capability registry, manifest, CLI/source, registry projection, and focused test paths listed in `target_paths`.

Stale-Assumption Warnings: the existing `gtkb-hygiene-sweep` skill is retained for configured content-drift patterns and child-bridge routing. The new skill does not replace it, use a retired Tier A registry, create other harness adapters by implication, or rely on retired bridge indexes/queues.

Specification Linkage Assessment: PASS subject to independent review of the links and spec-to-test mapping below.

Lifecycle Compliance: PASS for a first `NEW` proposal. No managed skill bytes are authored before GO.

Overall structural recommendation: GO.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - requires deterministic report-first hygiene, fresh Git/session evidence, non-mutating defaults, and batch-specific owner-approved apply evidence before cleanup.
- `SPEC-INTAKE-97538b` - makes the tracked SoT artifact registry canonical for cleanup essentiality and prohibits Git state from acting as essentiality authority.
- `SPEC-INTAKE-99a602` - requires high-risk cleanup to be registry-driven with explicit preservation rules while reliable backup coverage is absent.
- `GOV-PLATFORM-SOT-REGISTRY-001` - makes `config/registry/sot-artifacts.toml` plus its MemBase projection the single platform SoT inventory.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` - places repeatable enumeration, hashing, durable transitions, recovery, and event history in deterministic services rather than model context.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - requires STRIP/KEEP/QUARANTINE classification, bounded cleanup, and preservation of audit history.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires fail-closed deterministic evaluation, current evidence, lifecycle-aware history, and non-passing partial/unsupported states.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the modernization slice to preserve current GT-KB behavior and evidence surfaces.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the cleanup plan, risks, owner decision, and accepted future execution batch to remain durable governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the CLI, skill, tests, manifests, receipts, and bridge evidence to form one traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit candidate, preserved, quarantined, restored, refused, and unsupported lifecycle states without silent transitions.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO, matching work-intent claim, and implementation-start authorization before protected mutations.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH, project, and WI metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report and independent verification to execute the mapped tests.
- `GOV-STANDING-BACKLOG-001` - this work extends existing WI-5142 and does not create a competing backlog item or bulk lifecycle mutation.

## Prior Deliberations

_Helper pre-population is disabled at filing because this candidate list was already populated, reviewed, and pruned during the governed proposal-drafting phase._

- `DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER` - owner-approved project charter requires bounded cleanup, explicit lifecycle classification, history preservation, deterministic guards, and no unbounded purge.
- `DELIB-202666274` - active project-scope PAUTH authorizes source, test, configuration, documentation, metadata, governance-evidence, bridge, and runtime-state implementation while keeping destructive cleanup, Git mutation, release, and deployment forbidden.
- `DELIB-20260701-GTKB-ARTIFACT-ESSENTIALITY-EMERGENCY` - owner directed registry-first preservation after loss of an essential local artifact.
- `INTAKE-eb0bbcad` / `SPEC-INTAKE-97538b` - tracked registry authority for cleanup essentiality.
- `INTAKE-b44907bd` / `SPEC-INTAKE-99a602` - backup-risk and preservation requirement.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - separates deterministic enumeration/state transitions from operator judgment.
- `bridge/gtkb-work-tree-hygiene-slice-b-strays-cli-004.md` - VERIFIED read-only stray CLI retained as an input surface.
- `bridge/gtkb-artifact-essentiality-emergency-guardrails-reproposal-008.md` - VERIFIED registry-aware preservation behavior retained unchanged.
- `bridge/gtkb-wi99a602-backup-safety-before-cleanup-006.md` - VERIFIED registry-first preservation in the auto-resolve planner.
- `bridge/gtkb-workspace-orphan-cleanup-2026-06-05-003.md` - prior cleanup proposal was withdrawn after scope/evidence became stale; this proposal uses fresh evidence and no live cleanup authority.

## Owner Decisions / Input

The owner directed this interactive session on 2026-07-16 to prioritize investigation, planning, implementation, testing, and execution of a repeatable ops hygiene capability with deterministic CLI support, a dedicated skill, reversible trash, and tracked history. That direction selects the work and desired delivery surface.

No additional owner decision is required to implement or test this non-live slice because the active project PAUTH covers the listed source, test, configuration, metadata, registry-projection, managed-skill, and runtime-state implementation classes. The active PAUTH explicitly forbids destructive cleanup and Git mutation. Accordingly, this proposal does not authorize a live `trash`, `restore`, worktree-prune, object-prune, or purge run. After implementation, `plan` must produce the exact candidate manifest; live execution requires a separate batch-specific owner-approved apply record and a bridge/authorization scope that permits the exact operation.

## Requirement Sufficiency

Existing requirements are sufficient for this implementation slice. `GOV-WORK-TREE-HYGIENE-001`, `SPEC-INTAKE-97538b`, `SPEC-INTAKE-99a602`, `GOV-PLATFORM-SOT-REGISTRY-001`, `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`, `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, and `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` collectively specify report-first behavior, registry authority, preservation, deterministic services, lifecycle classification, history, recovery, and fail-closed evidence. WI-5142 already records the remaining bounded-cleanup-ledger gap. The current owner direction adds urgency and packaging but does not require a new or revised formal requirement before source implementation.

## Spec-Derived Verification Plan

| Governing surface | Required verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Temp-repository tests prove report-first default, exact-batch evidence requirement, fresh revalidation, no live-root mutation during tests, and refusal of unsupported/destructive operations. Existing strays/auto-resolve tests remain green. |
| `SPEC-INTAKE-97538b`, `SPEC-INTAKE-99a602` | Tests prove registry matches veto trash before Git/age heuristics, unregistered status alone never authorizes trash, changed candidates fail closed, and restore never overwrites. |
| `GOV-PLATFORM-SOT-REGISTRY-001` | `gt registry validate --json` reports 47/47 parity after projection sync; refresh classifies external/archive/generated/active records correctly; corrected resource-alias path resolves; no generated-tree recursion occurs. |
| `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` | Tests prove stable plan/item hashes, bounded compact output, append-only ordered events, interrupted/partial batch receipts, and deterministic history reconstruction without an aggregate index. |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | Tests prove explicit KEEP/QUARANTINE candidate classification and immutable audit/history preservation; no permanent purge exists. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Tests cover corrupt, unsupported, stale, partial, changed, and contradictory manifests as non-passing/refused outcomes. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Existing inventory-string, hygiene-strays, auto-resolve, skill-catalog, registry, and CLI tests remain green. |
| Managed-skill lifecycle | Focused test proves canonical source, registry entry, generated Codex adapter, manifest SHA agreement, role scope, and no orphaned skill. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_hygiene_reclaim.py platform_tests/scripts/test_hygiene_reclaim_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_hygiene_strays_cli.py platform_tests/scripts/test_work_tree_stray_detector.py platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_hygiene_reclaim.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_reclaim_cli.py platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_hygiene_reclaim.py groundtruth-kb/tests/test_inventory_string_scan.py platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py platform_tests/scripts/test_hygiene_reclaim_cli.py platform_tests/skills/test_gtkb_hygiene_reclaim_skill.py
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli registry validate --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli admin inventory refresh --json
```

After generating the one declared Codex adapter through the canonical managed-skill lifecycle, run `scripts/generate_codex_skill_adapters.py --check` as a read-only drift check. The generator must leave every adapter outside `.codex/skills/gtkb-hygiene-reclaim/SKILL.md` byte-identical.

Expected result: focused and regression tests pass; lint/format pass; adapter/manifest/registry SHA agreement passes; registry parity is exact; refresh is lifecycle-aware and bounded; all trash/restore tests operate only in disposable temp repositories; no live cleanup operation occurs under this GO.

## Acceptance Criteria

1. `gt hygiene reclaim plan` creates a compact, deterministic, hash-addressed run without mutating candidates and refuses incomplete registry or Git preservation evidence.
2. `history` reconstructs run/item state from per-run manifests and append-only receipts, detects tampering or partial state, and introduces no aggregate authority.
3. `trash` and `restore` operate only on exact selected item IDs in disposable test roots, enforce fresh registry/Git/path/hash checks, never overwrite, and report zero physical bytes reclaimed for same-volume moves.
4. Inventory refresh reports active, archive, generated, external, glob, directory, and concrete file records by lifecycle/path class; it does not recursively enumerate generated runtime trees; registry TOML and MemBase projection remain exact.
5. The canonical managed skill, Codex adapter, manifest, capability registry, CLI wiring, source, and spec-derived tests agree, while all pre-existing adapters remain byte-identical.
6. Focused tests, named regressions, lint, format, proposal applicability, clause, target coverage, and registry validation all pass. No live cleanup, Git mutation, permanent purge, commit, push, or deployment occurs under this GO.

## Cross-Harness Disposition

- **Claude Code:** `.claude/skills/gtkb-hygiene-reclaim/SKILL.md` is the canonical managed-skill source and supplies the native skill contract.
- **Codex:** `.codex/skills/gtkb-hygiene-reclaim/SKILL.md` is generated from the canonical source; its manifest and capability-registry hashes must agree.
- **Antigravity, Cursor, Ollama, OpenRouter, Goose, Alibaba Cloud Studio, and future harnesses:** no native adapter is implied by this proposal. They may invoke the deterministic `gt hygiene reclaim` CLI, but must not claim managed-skill parity until an explicit registry declaration and governed adapter path exist.
- **Parity proof:** focused catalog tests must fail if the canonical source, Codex adapter, manifest, registry declaration, role scope, or unsupported-harness disposition drifts.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5142; DELIB-20260710-GTKB-MODERNIZATION-ARTIFACT-DECONTAMINATION-CHARTER; DELIB-202666274; owner direction in Prime Builder session 2026-07-16",
  "canonical_authority": "GOV-PLATFORM-SOT-REGISTRY-001; SPEC-INTAKE-97538b; SPEC-INTAKE-99a602; GOV-WORK-TREE-HYGIENE-001; GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001",
  "primary_route": "Operators use one gt hygiene reclaim command family and the gtkb-hygiene-reclaim managed skill; the SoT registry remains the preservation authority and per-run manifests remain execution history.",
  "before_behavior": "Registry parity can pass while refresh recursively expands generated runtime trees, stray scans emit hundreds of thousands of tokens, and Git object bloat has no bounded reversible planner or durable batch history.",
  "after_behavior": "One compact deterministic service validates registry semantics, plans exact candidates, records immutable receipts, and supports exact reversible trash and restore while refusing unsupported or stale evidence.",
  "self_descriptive_naming": "The plan, history, trash, and restore subcommands map directly to non-mutating assessment, durable inspection, reversible quarantine, and recovery.",
  "obsolete_guidance_disposition": "Git ignored, untracked, unreachable, stale-worktree, and temporary-object labels remain evidence inputs rather than cleanup authority; prior read-only hygiene commands remain supported inputs instead of competing implementations.",
  "history_preservation": "The SoT registry, MemBase projection, numbered bridge chain, Git refs/reflogs/indexes, existing hygiene runs, and every preserved or refused candidate remain available; no permanent purge exists in this slice.",
  "baseline": {
    "registry_toml_rows": 47,
    "registry_projection_rows": 47,
    "inventory_expanded_files_approx": 908920,
    "stray_scan_paths": 1255,
    "stray_scan_manual_review": 1185,
    "git_directory_gib_approx": 250,
    "git_loose_object_gib_approx": 216,
    "git_temp_object_garbage_count": 36
  },
  "expected_result": {
    "registry_projection_parity": "exact",
    "generated_runtime_tree_recursive_expansion": 0,
    "default_cli_output": "compact summary",
    "trash_mode": "same-volume reversible move",
    "physical_bytes_reclaimed_by_trash": 0,
    "live_cleanup_under_this_go": 0
  },
  "rollback": {
    "instructions": "Revert only this thread's exact source, test, registry-row, projection, capability-registry, manifest, and generated-adapter hunks; preserve all pre-existing dirty bytes. Runtime test runs are disposable.",
    "test": "Re-run the focused regressions, adapter drift check, registry validation, and byte comparisons for unrelated adapters and pre-existing dirty targets."
  },
  "hard_invariants": [
    "No protected mutation before independent GO, matching work-intent claim, and implementation-start evidence.",
    "Registry matches are preservation vetoes and absence from the registry is never deletion authority.",
    "All refs, worktree HEADs, stash roots, valid reflog object IDs, and every index stage are protected before Git-object candidacy.",
    "No live cleanup, worktree prune, Git garbage collection, reflog expiration, branch deletion, stash drop, commit, push, release, or deployment under this GO.",
    "Same-volume trash is reported as zero physical bytes reclaimed.",
    "Pre-existing dirty and staged bytes are preserved."
  ],
  "fail_closed_conditions": [
    "Independent GO, active PAUTH, matching claim, or implementation-start packet is absent.",
    "A planned mutation is outside the declared target paths.",
    "Registry parity, registry path-class semantics, root identity, candidate hash, or Git preservation evidence is missing, stale, corrupt, or contradictory.",
    "A candidate is tracked, registered, protected, active, changed, out of root, cross-device, or collides with its destination.",
    "Owner/apply evidence is empty, non-specific, or does not identify the exact plan hash and candidate IDs."
  ],
  "essential_context_preservation": "The canonical registry, MemBase projection, current hygiene classifiers, bridge history, project/WI authorization, and Git recovery roots remain the authoritative context; compact summaries point to exact in-root manifests instead of replacing them."
}
```

## Risk / Rollback

Primary risk is false classification of recoverable work or a Git object as disposable. The implementation must therefore protect every registry match and every fresh Git root source (refs, worktree HEADs, stashes, reflogs, indexes), require age plus exact identity, revalidate at operation time, move rather than delete, and refuse on missing/ambiguous evidence. A second risk is semantic regression in the inventory scanner; lifecycle/path-class fixtures and existing string-scan tests must cover it. A third risk is shared dirty-target entanglement: `groundtruth-kb/src/groundtruth_kb/cli.py` and `config/agent-control/harness-capability-registry.toml` already contain staged unrelated changes, while `config/registry/sot-artifacts.toml` and `groundtruth.db` contain unrelated working-tree state. Implementation must preserve those bytes and report only this thread's exact hunks/registry row/projection change.

Rollback source/config/test/skill changes by reverting only this thread's exact hunks and generated adapter/manifest records, then resync the previous registry TOML projection through the canonical CLI. Runtime test runs are disposable. A live trash run is not part of this GO; later trash rollback uses the implemented exact-item `restore` command. Permanent deletion has no implementation or rollback path in this slice.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5142-hygiene-reclaim-cli-skill`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat(hygiene)`: new deterministic reclaim CLI and managed skill, plus a bounded registry path/refresh correctness fix and specification-derived tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
