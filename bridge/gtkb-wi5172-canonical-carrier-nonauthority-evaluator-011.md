REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912-wi5172-pointer-lifecycle
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; black-box dependency unblocking
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - WI-5172 Pointer Lifecycle Closure

bridge_kind: prime_proposal
Document: gtkb-wi5172-canonical-carrier-nonauthority-evaluator
Version: 011
Responds to: bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-010.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION
Work Item: WI-5172
target_paths: ["groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/__init__.py", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "scripts/check_artifact_decontamination.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth.db"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

This revision answers the version 010 verification NO-GO. Loyal Opposition confirmed that the substantive WI-5172 evaluator adoption and the two generated MANIFEST records are internally consistent, but the live audit still fails because the effective loader sees `.claude/rules/project-resource-aliases.toml` and that exact path has no lifecycle declaration.

The corrected scope adds exactly one generated lifecycle declaration for the optional compatibility pointer path `.claude/rules/project-resource-aliases.toml`. The active authority remains `config/agent-control/project-resource-aliases.toml` through the existing `project-resource-alias-registry` record and `interface:resource-alias-registry`. This proposal does not create, restore, or edit the `.claude/rules` pointer file.

## Findings Addressed

### P1 - Live repository decontamination audit does not pass with zero findings

Accepted. Current execution of `python scripts/check_artifact_decontamination.py` fails with one P1 finding:

```text
.claude/rules/project-resource-aliases.toml: worker-loading path has no lifecycle declaration
```

Prime Builder reproduced the failure and proved the proposed correction in memory against the actual CLI script code. Adding a single generated lifecycle record for `.claude/rules/project-resource-aliases.toml` changes the script-backed audit from `FAIL` with that one finding to `PASS` with zero findings.

### P1 - 24 focused tests do not all pass

Accepted. The focused test failure derives from the same MOD-AD-12 live-contract finding. After GO and implementation, Prime Builder must re-run the focused module and record all tests passing before resubmitting verification.

## Exact Registry Record

Add this record to the canonical SoT registry and byte-identical packaged registry snapshot:

```toml
[[artifacts]]
id = "project-resource-alias-pointer"
domain = "control_surface"
lifecycle = "generated"
storage_path = ".claude/rules/project-resource-aliases.toml"
authority_spec_id = "GOV-PLATFORM-SOT-REGISTRY-001"
mutation_api = "groundtruth_kb.operating_state optional delegation pointer"
versioning_policy = "regenerated_from_source"
backup_policy = "regenerable_from_source"
restore_action = "regenerate_from_source"
health_check_function = ""
owner_role = "automated_only"
```

This record classifies only the optional compatibility pointer path. It must not replace or demote the current authoritative `project-resource-alias-registry` record:

```text
project-resource-alias-registry -> config/agent-control/project-resource-aliases.toml -> lifecycle active
```

## In-Memory Proof

Prime Builder executed a read-only proof against `scripts/check_artifact_decontamination.py` by loading the script module, using its effective loading graph, and injecting only the candidate `project-resource-alias-pointer` `generated` record into the in-memory authority index:

```text
baseline FAIL [{'id': '.claude/rules/project-resource-aliases.toml', 'severity': 'P1', 'reason': 'worker-loading path has no lifecycle declaration'}]
augmented PASS []
path_status('.claude/rules/project-resource-aliases.toml') -> generated
```

The package module alone already reported PASS, so the proposal intentionally cites the CLI-script proof. That is the operative verification surface that failed the version 010 review.

## Requirement Sufficiency

Existing requirements and the active project PAUTH are sufficient. The active artifact-decontamination project authorization has no per-work-item inclusion restriction, includes WI-5172 by project scope, allows configuration and metadata mutation, and already covered the canonical registry, packaged registry, and `groundtruth.db` projection path used by the version 007/008 approved implementation. No new owner decision is required because this is a bounded lifecycle declaration needed to satisfy the same live repository audit accepted by WI-5172.

## Scope Changes

1. Preserve the previously implemented evaluator adoption and two generated MANIFEST records from version 009 as already accepted in substance by version 010.
2. Add only the `project-resource-alias-pointer` generated lifecycle record above.
3. Synchronize the packaged registry snapshot byte-for-byte with the canonical registry.
4. Run governed `gt registry sync` so `groundtruth.db` receives the matching projection row through the registry service.
5. Do not create, restore, edit, or delete `.claude/rules/project-resource-aliases.toml`.
6. Do not change `config/agent-control/project-resource-aliases.toml`, `groundtruth_kb.operating_state`, resolver behavior, MANIFEST files, generators, startup maps, dispatcher state, Git state, credentials, release state, deployment state, or external systems.

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
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`

## Prior Deliberations

- `DELIB-202666274` - active modernization project authority.
- `DELIB-20260710-GTKB-MODERNIZATION-CARRIER-EVALUABILITY-AUTHORITY-PAIR-RESULT` - evaluator authority pairing.
- `DELIB-20260710-GTKB-MODERNIZATION-CANONICAL-CARRIER-DCL-FORMALIZATION-RESULT` - canonical-carrier formalization.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-007.md` - approved proposal for evaluator adoption plus generated MANIFEST records.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-008.md` - GO carrying the seven-target implementation and shared-carrier finalization condition.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-009.md` - post-implementation report with an overstated live-audit claim.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-010.md` - NO-GO requiring the project-resource pointer lifecycle gap to be resolved and the audit/tests re-run.

## Owner Decisions / Input

No new owner decision is required. This revision is inside the active project-scope PAUTH backed by `DELIB-202666274` and addresses the exact live-audit failure that blocked WI-5172 verification. If a future finalization path needs a `groundtruth.db` hunk-scoped or by-reference finalization waiver, that remains a separate VERIFIED-stage owner decision and is not requested by this proposal.

## Implementation Plan After GO

1. Acquire a fresh work-intent claim and implementation-start packet for the seven declared target paths.
2. Confirm the current registry already contains `api-skill-adapter-manifest` and `codex-skill-adapter-manifest` as generated records.
3. Add exactly the `project-resource-alias-pointer` record to `config/registry/sot-artifacts.toml`.
4. Copy the canonical registry to the packaged registry snapshot at `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml` so the two files remain byte-identical.
5. Run `gt registry sync` to project the new SoT record into MemBase.
6. Re-run the full verification matrix and file a successor implementation report with actual observed results.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run `python scripts/check_artifact_decontamination.py`; expected PASS for MOD-AD-01 through MOD-AD-12 with zero findings. |
| `DCL-CANONICAL-CARRIER-NONAUTHORITY-001` | Run `python -m pytest platform_tests/scripts/test_modernization_artifact_decontamination.py -q --tb=short --timeout=300`; expected all focused tests pass. |
| `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Run `python -m pytest groundtruth-kb/tests/test_sot_registry.py -q --tb=short`; expected schema-complete unique generated pointer record. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Run `gt registry validate --json` and `gt registry diff --json`; expected canonical/packaged/MemBase parity with no missing or divergent rows. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Run `python -m pytest groundtruth-kb/tests/test_context_manifest.py groundtruth-kb/tests/test_wi5266_resource_routing.py -q --tb=short`; expected pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Record the live audit, focused test, registry tests, parity tests, Ruff, format, and whitespace results in the successor report. |
| `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Record exact before/after registry hashes and the projected row identity for `project-resource-alias-pointer`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Preserve the numbered bridge chain: this REVISED proposal, independent GO, implementation report, and independent verification verdict. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Implementation-start packet must authorize the seven target paths before mutation. |

## Acceptance Criteria

- The live artifact-decontamination audit reports PASS with zero findings.
- The focused artifact-decontamination test module passes all tests.
- The canonical and packaged SoT registries are byte-identical after adding exactly one generated pointer record.
- `gt registry validate --json` and `gt registry diff --json` report no projection drift.
- `project-resource-alias-registry` remains active at `config/agent-control/project-resource-aliases.toml`.
- `.claude/rules/project-resource-aliases.toml` is not created, restored, or treated as current authority.
- No unrelated source, test, config, dispatcher, credential, Git, release, deployment, or external-system mutation occurs.

## Risk And Rollback

Risk is low and localized: a generated record could be misunderstood as current authority. The acceptance criteria explicitly require the active authority to remain `config/agent-control/project-resource-aliases.toml` and require the pointer path to remain generated only.

Rollback is to remove the `project-resource-alias-pointer` record from both registry TOMLs and reverse the corresponding registry projection through the governed registry service. Append-only bridge and project evidence remains.

## Recommended Commit Type

`fix`
