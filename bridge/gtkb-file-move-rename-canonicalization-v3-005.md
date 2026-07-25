NEW
::init gtkb lo
::open build


author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: Codex
author_model_version: GPT-5 Codex
author_model_configuration: Codex Desktop interactive Prime Builder; owner transcript role override; approval_policy=never
author_metadata_source: explicit current-session transcript and matching live GO-implementation claim

# GT-KB Bridge Implementation Report - gtkb-file-move-rename-canonicalization-v3 - 005

bridge_kind: implementation_report
Document: gtkb-file-move-rename-canonicalization-v3
Version: 005 (NEW; Stage A verification request)
Responds to GO: bridge/gtkb-file-move-rename-canonicalization-v3-004.md
Approved proposal: bridge/gtkb-file-move-rename-canonicalization-v3-003.md
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640
Recommended commit type: feat

## Implementation Claim

Stage A implemented a deterministic CSV-driven full-root migration engine, a declarative migration policy, side-effect-free rule and Cursor projection generators, focused fixtures/tests, and runtime preflight/plan evidence. The engine validates the 90-row manifest, inventories the root with explicit audit/runtime/application boundaries, preserves old sources, records exact postimages and preimages, scans text and structured SQLite fields, detects old-path bytes in undecoded containers, and fails closed when any reference or filesystem condition is unresolved.

No migration `apply`, consumer rewrite, destination write, projection write, registry/database mutation, old-source deletion, Git-index mutation, commit, push, release, or deployment occurred. Stage B is paused. The current blocked plan is evidence for correction and review, not an apply candidate and not a child-proposal authorization basis.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` remains controlling: all 90 obsolete paths are retained; no deletion is authorized. No new owner decision is required for this Stage A report. Stage B remains separately gated by an exact child proposal, independent GO, fresh child claim and packet, and matching plan/binding hashes.

## Prior Deliberations

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - retain obsolete paths through repeated verification and require later separate deletion authorization.
- `DELIB-202666274` - project modernization authorization with bridge and independent-review controls.
- `bridge/gtkb-wi5648-file-move-false-verification-incident-001.md` and `-002.md` - incident evidence requiring a fresh valid lifecycle and fail-closed execution.
- `bridge/gtkb-file-move-rename-canonicalization-v3-003.md` - approved Stage A proposal.
- `bridge/gtkb-file-move-rename-canonicalization-v3-004.md` - narrow Stage A GO.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; project authorization DCLs | Live main-v3 claim and implementation packet validated each protected Stage A target before edits. Engine `apply` rejects main-v3 authority and requires the exact child lifecycle. No apply was run. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001` | Preflight/plan are observation modes; Git index hash is `sha256:68b929ed9bf8fb68b268e71b3571ed4865fcb20e58ccba11f5755e6c5aa0c737`; no staging or broad Git operation occurred. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `applications/**` is inventoried as an application boundary and never enters the write set. All Stage A files are within `E:/GT-KB`. |
| Cross-harness parity specifications | The required 209-test suite ran: 203 passed, 6 existing repository-configuration failures remained (one undeclared `gtkb-skill-rollout` skill and five Codex-hook configuration tests). |
| Artifact and lifecycle specifications | The policy, manifest hashes, full observation stream, immutable plan, residual/exception ledger, preimage/postimage payloads, and this numbered implementation report preserve the decisions and blocked states. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Migration-specific suite: 31 passed. Ruff: clean. The combined governance/authorization suite did not complete because an existing implementation-authorization test timed out while waiting on a Git subprocess; the timeout stack is recorded below. |

## Commands Run

```powershell
python scripts/implementation_authorization.py validate --target scripts/gtkb_file_reference_migration.py
python scripts/implementation_authorization.py validate --target config/file-reference-migration/wi5640.toml
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_gtkb_file_reference_migration.py
python scripts/gtkb_file_reference_migration.py preflight
python scripts/gtkb_file_reference_migration.py plan
python -m pytest platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py -q --tb=short
python -m ruff check scripts/gtkb_file_reference_migration.py scripts/generate_rule_compatibility_projections.py scripts/generate_cursor_skill_adapters.py platform_tests/scripts/test_gtkb_file_reference_migration.py platform_tests/scripts/test_generate_rule_compatibility_projections.py platform_tests/scripts/test_generate_cursor_skill_adapters.py
python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py platform_tests/scripts/test_canonical_init_keyword_syntax.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_governance_mutation.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_authorization_gfr_slice_a.py platform_tests/scripts/test_implementation_authorization_harness_selector.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_project_authorization.py groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short
```

## Observed Results

- Manifest: 90 rows; 33 hooks, 38 rules, 19 agent-control; CSV hash `sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`.
- Latest preflight: blocked as designed; 3,824 inventory records, 4,069 reference hits, 1,676 unresolved residuals, 479 proposed writes, and 1,993 blockers.
- Immutable plan: blocked; 3,822 inventory records, 4,069 hits, 1,676 unresolved residuals, 479 proposed writes, and 1,994 blockers.
- Plan hash: `sha256:575053236f13e2a6b456f0b1ec0e7e9d19369138cdb99f52112385976bbb3855`.
- Closure fingerprint: `sha256:f9a5f9301c15e3f8c1e7573a3badff9ce5c1b8b64fdc9279322896a6258582a8`.
- Write-set hash: `sha256:dc2676311f800c1c1a9e5a53fbc2b9266c811628de0fc53619a963c42610348a`.
- Blockers: 1,675 unresolved live references; 277 generated outputs not materialized; 33 undecoded-container byte hits; three generator checks failed; two Goose generator checks blocked on shared manifest ownership; one stale adaptation; one live SQLite domain-API correction; the required unreadable `groundtruth-kb/pytest-kpi-retro-codex/basetemp4`; and one plan-pass closure change.
- Opaque candidates are not silently skipped: 31 hits are in a wheel fixture and two are in `.groundtruth/dashboard/gtkb-dashboard.sqlite`; both require structured disposition.
- Migration-specific tests: 31 passed in 8.28 seconds. Ruff: all checks passed.
- Cross-harness suite: 203 passed, 6 failed. The failures match already-recorded repository gaps: undeclared `gtkb-skill-rollout` and missing Codex hook configuration/wiring.
- Governance/authorization suite: did not complete. Pytest timed out in `platform_tests/scripts/test_implementation_authorization.py::test_create_packet_allows_same_session_overlapping_named_packet` while `implementation_authorization._dirty_worktree_paths` waited on a Git subprocess. No Stage A migration test failed in this run.
- Rule projection check: 38 projections current. Cursor check reports prospective generated drift for the later exact plan. Codex, Antigravity, and API generators report drift; Goose has a shared-manifest ownership conflict.

## Files Changed

- `scripts/gtkb_file_reference_migration.py`
- `scripts/generate_rule_compatibility_projections.py`
- `scripts/generate_cursor_skill_adapters.py`
- `config/file-reference-migration/wi5640.toml`
- `platform_tests/scripts/test_gtkb_file_reference_migration.py`
- `platform_tests/scripts/test_generate_rule_compatibility_projections.py`
- `platform_tests/scripts/test_generate_cursor_skill_adapters.py`
- `platform_tests/fixtures/file_reference_migration/direct-forms.txt`
- `platform_tests/fixtures/file_reference_migration/segmented.py`
- `platform_tests/fixtures/file_reference_migration/segmented.ps1`
- `platform_tests/fixtures/file_reference_migration/structured.toml`

Runtime evidence is under `.gtkb-state/file-reference-migration/wi5640/**`. Unrelated dirty paths were not modified or staged by this Stage A implementation.

## Acceptance Criteria Status

- [x] One Python engine and declarative policy expose `preflight`, `plan`, `apply`, `verify`, and `rollback`; ad hoc recursive replacement is not an execution path.
- [x] The main-v3 GO cannot authorize apply; exact child lifecycle, claim, packet, target set, and content binding are independently checked.
- [x] All 90 obsolete sources remain present; no cleanup or deletion occurred.
- [x] Full-root observation is programmatic, sorted, byte-aware, classification-backed, and fail-closed on unreadable/unclassified/opaque content.
- [x] The mandated access-denied directory was reproduced exactly.
- [ ] The current plan is not closure-ready: unresolved references, generated-owner gaps, opaque containers, generator conflicts/drift, a domain-API database correction, and one mid-pass inventory change remain.
- [ ] Three clean independent verify passes cannot run until plan blockers reach zero.
- [ ] The 209-test cross-harness suite is not clean because six repository-level gaps remain.
- [ ] The combined governance/authorization suite did not complete because an existing implementation-authorization test timed out in a Git subprocess.
- [ ] Apply/rollback safety is not claimed as verified. Advisory review identified Windows reparse races, crash-journal recovery gaps, rollback compare-and-swap gaps, incomplete mutation-universe binding, and missing successful-authorized-apply/fault-injection tests.

## Risk And Rollback

No repository consumer was mutated, so Stage A rollback is limited to removing or reverting the eleven new Stage A implementation/test files under their governed lifecycle; broad Git reset/stash operations are forbidden. Runtime evidence may be regenerated.

Stage B must remain paused. Before a child proposal can be filed, Prime Builder must resolve every plan blocker and the advisory transaction-safety findings, materialize generated outputs through their authoritative generators, add structured handling for the wheel/dashboard database, obtain a domain-API plan for the live database value, and produce repeated stable plan evidence. The current 479-file write set is not authorized for apply.

## Worker-Quality Observations

Three read-only same-session Loyal Opposition advisers were used for blocker triage, code safety, and test-gap review. They did not edit files or file verdicts. Positive signals: they independently found the fixed-root wildcard defect, unknown-extension scan gap, context-free basename risk, generated-owner gaps, and missing authorization/rollback fault tests. The basename finding directly prevented a deterministic but contract-invalid blanket rewrite from remaining in the implementation. Negative/remaining signal: the advisers are not independent formal reviewers and one nested attempt to start further reviewers stalled; formal verdict authority remains with the owner's separate interactive LO session.

## Loyal Opposition Asks

1. Verify that Stage A stayed within its exact target paths and that no migration apply or repository-consumer write occurred.
2. Review the deterministic scan, exclusion ledger, byte-level opaque-container detection, child-only authorization binding, and generator ownership model against the approved proposal.
3. Return `NO-GO` with precise correction conditions if the known transaction-safety and missing-test findings prevent Stage A verification; do not treat this blocked plan as Stage B authorization.
