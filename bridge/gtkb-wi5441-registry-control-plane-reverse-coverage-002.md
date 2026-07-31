NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f96e2-e204-72e1-993c-702062f7077e
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: lo_verdict
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 002
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-001.md
Reviewed proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-001.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: ["config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "scripts/controlled_artifact_paths.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py", "scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "scripts/registry_observation_hook.py", "platform_tests/scripts/test_registry_observation_hook.py", ".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py"]

## Verdict

NO-GO. The active PAUTH, owner decision, independent author session, in-root scope, applicability preflight, and mandatory ADR/DCL clause preflight are valid. The implementation cannot begin because the proposal does not yet provide a complete enforcement scope or an observationally atomic registry transaction.

## First-Line Role Eligibility And Review Independence

- Current session envelope `019f96e2-e204-72e1-993c-702062f7077e` resolves the interactive Codex A role as `loyal-opposition`; this context is authorized to file `NO-GO`.
- Proposal author session: `019f863a-acd3-7320-80c0-1831f0936cc0`.
- Reviewer session: `019f96e2-e204-72e1-993c-702062f7077e`.
- The readable session contexts differ. Review independence passes.

## Findings

### F1 — P0 — Required enforcement consumers are outside the declared 19-path scope

`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` requires the shared resolver/authorization service at the relevant hook, commit, release, and migration boundaries. The proposal claims stale or incomplete registry state blocks migration and release, but `scripts/gtkb_file_reference_migration.py:1744-1757` still obtains registered paths through `groundtruth_kb.inventory.string_scan._artifact_inventory`; neither that migration service nor `groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py` is a target. `scripts/release_candidate_gate.py` likewise has no platform-SoT validation path and is excluded.

Impact: the proposed implementation could add a correct new CLI while the intended WI-5640 consumer and release path still bypass it. That contradicts the proposal's own fail-closed claim.

Required revision: either add the exact migration, inventory, release-gate, and focused-test paths required to make those boundaries resolve through the canonical control plane, or explicitly defer those claims and amend the governing scope so no false enforcement claim remains.

### F2 — P1 — The proposed write order is recoverable at best, not atomic to readers

The design writes an intent, atomically replaces TOML, and then updates the SQLite projection/revision tables. A crash between the replace and DB commit yields new TOML with old projection. Existing independent readers expose `load_toml` (`groundtruth-kb/src/groundtruth_kb/project/sot_registry.py:308`) and `load_projection` (`:443`); `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py:346-349` reads the TOML directly. The proposal blocks some later operations for incomplete journals but does not define a universal reader/journal linearization rule.

Impact: a consumer can observe split membership before recovery, violating the exact-projection invariant and the claim that injected failures never publish mixed membership.

Required revision: define a reader-visible transaction state and require every authoritative resolver, inventory, doctor, commit, release, and migration consumer to fail closed on an incomplete journal. Add phase-by-phase fault-injection tests proving that no consumer can observe mixed membership, plus an idempotent receipt-bound legacy-to-v3 bootstrap for the 50 existing records with no `coverage_mode` field.

### F3 — P1 — The exact target set cannot preserve packaged-registry parity

Acceptance criterion 3 changes `config/registry/sot-artifacts.toml` to add reviewed `coverage_mode` fields. `groundtruth-kb/tests/test_context_manifest.py:107-123` requires that source registry to be byte-identical to `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`. The packaged mirror and its test are absent from the nineteen permitted paths, while criterion 9 forbids required spillover.

Impact: the declared target set forces either a parity regression or an out-of-scope mutation.

Required revision: include the exact packaged mirror and parity-test paths, with their registry admission and source-of-truth projection relationship explicitly defined, or change the implementation plan so TOML content does not diverge.

### F4 — P1 — Coverage and observation boundaries remain underspecified

The controlling decision requires a whole-root inventory excluding only immediate `applications/<child>/` repositories. The proposal instead permits broad "service/runtime exclusions" without an exhaustive classification contract. It also calls `gt registry observe` automated-only but provides no caller-authentication, authorization, or negative test proving a direct worker cannot manufacture freshness evidence after an unauthorized mutation.

Impact: exclusions can conceal unregistered load-bearing artifacts, and an unrestricted observer can turn an unauthorized mutation into apparently current evidence.

Required revision: enumerate every exception as a deterministic classified category, and define/test an authenticated observer caller boundary that rejects direct user/worker invocation while retaining the stale-state commit/doctor backstop.

### F5 — P1 — WI-5441 is still falsely resolved and the proposal does not repair its lifecycle

The active PAUTH correctly includes WI-5441, but the backlog still records it as `resolved` even though its live thread set includes GO, VERIFIED-with-missing-commit-coverage, this NEW proposal, and `gtkb-wi5441-registry-db-schema-009.md` at NO-GO. The proposed scope includes `groundtruth.db` but does not make re-opening/reconciling the work item's terminal state an acceptance criterion.

Impact: implementation would proceed under an incorrect work-item lifecycle and could repeat the historical false closure.

Required revision: bind governed WI-5441 re-open/reconciliation and canonical thread linkage to the implementation/report acceptance evidence; preserve the historical chain rather than rewriting it.

### F6 — P2 — The relevant implementation-start test module is already red

`python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short -x` fails before registry assertions: its fixture `bridge/sample-implementation-001.md` lacks required `Version` metadata, and the resolver raises before the test's intended PAUTH assertion. The proposal lists the test module and gate but neither discloses this baseline nor specifies a bounded fixture/lifecycle repair.

Required revision: state the baseline, isolate a legitimate test-only fixture correction or a separate governed repair, and identify the registry-specific selectors that must pass without masking the unrelated lifecycle failure.

## Positive Confirmations

- `PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724` is active, names WI-5441, permits source/test/configuration/metadata work, and forbids destructive cleanup, dispatcher/external mutation, history rewrite, push, release, deployment, and credential lifecycle.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` authorizes the policy but retains independent GO, PAUTH, and operation-time enforcement for protected implementation.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` preserves the incident history, forbids treating it as migration authorization, and requires a fresh reviewed repair-forward transaction.
- Current `gt registry validate --json` and `gt registry diff --json` report 50 TOML declarations and 50 projection rows in sync. This is legacy parity only, not evidence of the proposed control plane.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — exclusive membership authority, CLI shielding, atomic registered identity handling, and whole-root inventory policy.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` — preserve `db07f9dc` as incident evidence; WI-5640 remains paused pending independent GO, matching implementation authority, and terminal verification.

## Applicability Preflight

- packet_hash: `sha256:b82b78f4337955696fb7aa6bc4cfaefed07cadb24c4a01f8c355c4910ae2f13b`
- candidate_evidence_hash: `sha256:128a222031958bb1b8373b7423c8a75eea1e0d7412c793d08aefe211ce2b1981`
- bridge_document_name: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- declared_target_paths: [".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py", "config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth.db", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_registry_observation_hook.py", "scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "scripts/registry_observation_hook.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-001.md`
- operative_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- Operative file: `bridge\\gtkb-wi5441-registry-control-plane-reverse-coverage-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Owner Action Required

None. The Prime Builder can file a bounded REVISED proposal that addresses these findings. No implementation is authorized by this verdict.
