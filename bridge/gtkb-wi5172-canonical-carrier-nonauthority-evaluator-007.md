REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5172
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder worker; user-directed PB bridge auto-process

# Revised Implementation Proposal - WI-5172 Adopt Evaluator And Declare Generated Skill Manifests

bridge_kind: prime_proposal
Document: gtkb-wi5172-canonical-carrier-nonauthority-evaluator
Version: 007
Responds to: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-006.md
Revises: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-005.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5172
target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "scripts/check_artifact_decontamination.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]

## Revision Claim

Preserve version 005's approved adopt-with-formatting resolution and make its
live-repository acceptance contract satisfiable by declaring the API and Codex
skill MANIFEST files as generated projections in the canonical SoT registry.
Synchronize the packaged registry snapshot byte-for-byte and append the two
MemBase projection rows only through the governed `gt registry sync` service.

This is the NO-GO's preferred sequencing/scope path. The manifest files
themselves do not change, and generated lifecycle classification does not elevate
them to authority. The evaluator remains fail-closed for genuinely undeclared
worker-loading paths.

## Requirement Sufficiency

Existing requirements and active project authorization are sufficient. The
PAUTH covers WI-5172 and permits configuration, metadata, source, test, bridge,
and the bounded database projection required by the registry service. The
additional specifications below already govern canonical SoT records, generated
projection parity, and record schema. No owner decision or new formal
requirement is needed.

## In-Root Placement Evidence

All seven targets are inside `E:\GT-KB`. The two MANIFEST paths are evidence
subjects only, not mutation targets. No adopter/application or external path is
introduced.

## Specification Links

- `DCL-CANONICAL-CARRIER-NONAUTHORITY-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666274` - owner decision backing the active modernization project-scope authorization.
- `DELIB-20260710-GTKB-MODERNIZATION-CARRIER-EVALUABILITY-AUTHORITY-PAIR-RESULT` - evaluator authority pairing.
- `DELIB-20260710-GTKB-MODERNIZATION-CANONICAL-CARRIER-DCL-FORMALIZATION-RESULT` - canonical-carrier formalization.
- Versions 002-005 - original GO, Prime rejection, corrected NO-GO, and adopt-with-formatting revision.
- Version 006 - independent NO-GO proving the current live acceptance failure and requiring this prerequisite repair.
- WI-5300 terminal synchronization evidence does not authorize new declarations and is not reused as implementation authority.

## Owner Decisions / Input

No new owner decision is required. The active project PAUTH has no per-WI target
exclusion for this bounded registry correction. A fresh independent GO, exact
claim, and implementation-start packet remain mandatory before any target
mutation.

## Findings Addressed

### Live repository contract detects two undeclared worker-loading paths

Accepted. Current read-only execution reproduces version 006 exactly:

- focused suite: `1 failed, 23 passed` at
  `test_mod_ad_12_live_repository_contract_passes`;
- live audit: `FAIL` at MOD-AD-07, MOD-AD-11, and MOD-AD-12;
- findings: `.api-harness/skills/MANIFEST.json` and
  `.codex/skills/MANIFEST.json` have no lifecycle declaration.

Both files are generator outputs. `scripts/generate_api_skill_adapters.py` and
`scripts/generate_codex_skill_adapters.py` create the respective MANIFEST files.
A read-only in-memory registry evaluation with the two exact `generated` records
below returns `PASS`, all 12 audit assertions, zero findings, and resolves both
worker references as generated. `active` is deliberately rejected because it
would incorrectly elevate generated projections.

## Exact Registry Records

```toml
[[artifacts]]
id = "api-skill-adapter-manifest"
domain = "control_surface"
lifecycle = "generated"
storage_path = ".api-harness/skills/MANIFEST.json"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "scripts/generate_api_skill_adapters.py"
versioning_policy = "regenerated_from_source"
backup_policy = "regenerable_from_source"
restore_action = "regenerate_from_source"
health_check_function = ""
owner_role = "automated_only"

[[artifacts]]
id = "codex-skill-adapter-manifest"
domain = "control_surface"
lifecycle = "generated"
storage_path = ".codex/skills/MANIFEST.json"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "scripts/generate_codex_skill_adapters.py"
versioning_policy = "regenerated_from_source"
backup_policy = "regenerable_from_source"
restore_action = "regenerate_from_source"
health_check_function = ""
owner_role = "automated_only"
```

## Adopt-With-Formatting Baseline

Version 006 independently established the expected four evaluator candidate
hashes after formatting only the checker and focused test:

| Path | Required post-format SHA-256 |
| --- | --- |
| `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py` | `bbefd5cd37787094dff954b01300447cef171206cf0a776ce8ef72cfbcba2a2d` |
| `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py` | `a5ac3e15ae09d7485751e8329295717188b26f4026134983d671678baa788db3` |
| `scripts/check_artifact_decontamination.py` | `8d2a02e90746e2f2a28bbd64e90eba367285b66f22f3d0d3a7380492f50e23c9` |
| `platform_tests/scripts/test_modernization_artifact_decontamination.py` | `fc82ff570ecaa73a4fac2004632ce1bfd945571cb69d62fb1ca56b9f95fe4c45` |

The implementation must reconfirm these hashes after authorized formatting and
before registry synchronization.

## Scope Changes

1. Retain the original four evaluator/adoption targets and bounded Ruff
   formatting contract.
2. Add the canonical `config/registry/sot-artifacts.toml` authority target.
3. Add its packaged byte-identical registry snapshot target.
4. Add `groundtruth.db` only for the two registry projection rows written by
   `gt registry sync`; raw SQL and byte replacement are prohibited.
5. Do not change either MANIFEST, any generator, any other registry, startup
   control map, context manifest, activity sharding record, or unrelated DB row.

## Implementation Plan After GO

1. Acquire a fresh exact claim and operation-time start packet for all seven
   targets. Fail closed if WI-5329 or another live worker still reserves
   `groundtruth.db`.
2. Reconfirm the four evaluator input hashes and the canonical/packaged registry
   baselines.
3. Ruff-format only the checker and focused test, then require the four reviewed
   post-format hashes.
4. Add the two exact `generated` records to the canonical TOML registry and
   synchronize the packaged snapshot byte-for-byte through the established
   registry projection route.
5. Run the governed `gt registry sync` operation to append only the two matching
   MemBase projection rows. Do not use raw SQL.
6. Execute the full verification matrix and file a report with before/after
   hashes, exact DB row evidence, command output, and foreign dirty-work
   exclusions.

## Pre-Filing Preflight Subsection

- Applicability and clause preflights must pass on the completed revision with
  the added SoT specifications and seven-target envelope.
- The governed revision helper must pass credential, concurrency, project,
  author-provenance, and bridge-compliance gates before filing.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run all 24 focused tests and the live audit; require PASS, zero findings, and both MANIFEST references classified `generated`. |
| `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Run `groundtruth-kb/tests/test_sot_registry.py`; require schema-complete unique records with canonical mutation APIs and generated lifecycle. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Run `groundtruth-kb/tests/test_context_manifest.py` and `groundtruth-kb/tests/test_wi5266_resource_routing.py`; require canonical and packaged TOML byte parity and MemBase projection parity. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Start packet authorizes all seven paths and the governed registry-sync operation before mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Require 24/24 focused tests, live audit PASS, registry suites PASS, Ruff check, Ruff format check, and `git diff --check`. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Record exact four evaluator hashes, canonical/packaged registry hashes, and the two inserted DB projection identities. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use fresh GO, claim, start, report, and independent verdict; no direct or raw bridge write. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Keep registry authority, projections, evaluator candidate, report, and verdict separately attributable. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every mutation and test scratch path stays in-root. |

## Acceptance Criteria

- Exactly the two declared MANIFEST paths resolve as `generated`, never active
  authority.
- Live audit reports PASS for MOD-AD-01 through MOD-AD-12 with zero findings.
- All 24 evaluator tests pass.
- The four evaluator files match the reviewed post-format hashes.
- Canonical and packaged SoT registry files are byte-identical and schema-valid.
- MemBase contains matching projection rows written through `gt registry sync`;
  no unrelated row changes and no raw SQL occur.
- Ruff check, Ruff format check, and whitespace verification pass.
- No MANIFEST, generator, unrelated registry, application, Git, credential,
  dispatcher, release, deployment, or external-system mutation occurs.
- WI-5172 remains open unless later terminal evidence independently supports its
  full lifecycle disposition.

## Risk And Rollback

The main risk is misclassifying generated projections as authority or absorbing
unrelated dirty DB state. Exact-path `generated` records, schema tests, parity
checks, operation-time collision enforcement, and two-row sync evidence contain
that risk. Any active `groundtruth.db` owner blocks implementation start.

Rollback removes only the two registry records and their governed projection
rows through the registry service, and restores only the four adopted evaluator
targets. Append-only bridge, PAUTH, report, and verdict evidence remains.

## Recommended Commit Type

`feat`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
