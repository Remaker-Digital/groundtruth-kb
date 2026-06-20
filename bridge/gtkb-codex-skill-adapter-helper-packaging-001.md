NEW

# gtkb-codex-skill-adapter-helper-packaging - Fix Codex skill adapter helper packaging

bridge_kind: prime_proposal
Document: gtkb-codex-skill-adapter-helper-packaging
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-20 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee5e0-d8b0-7461-9250-6a1e3d6971a3
author_model: GPT-5 Codex
author_model_version: gpt-5.3-codex
author_model_configuration: Codex Desktop interactive targeted Prime Builder continuation; approval_policy=never; workspace=E:/GT-KB
author_metadata_source: explicit_owner_directed_project_continuation

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-WI-4486-SKILL-ADAPTER-HELPER-PACKAGING
Project: PROJECT-HARNESS-PARITY
Work Item: WI-4486

target_paths: ["scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_codex_skill_load_smoke.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/skills/test_verify_skill_scaffolding.py", ".codex/skills/**", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml"]

implementation_scope: source-and-generated-adapter-packaging
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4486` reports that a generated Codex skill adapter can name a helper path under `.codex/skills/<skill>/...` that is not actually present in the adapter bundle. At runtime, that pushes the harness into fallback behavior against the canonical `.claude/skills/...` location instead of proving that the Codex-facing adapter is self-contained for its advertised helper paths.

This proposal authorizes a narrow generator and regression-test fix: update Codex skill adapter generation/packaging so adapter-owned helper files are copied or otherwise exposed at the adapter path the generated skill names, regenerate the affected `.codex/skills` adapter output through the existing generator, and add regression coverage that fails when a generated adapter can only succeed by falling back to canonical `.claude/skills` helper locations.

The implementation must not edit generated `.codex/skills` files by hand. It must edit the generator and/or canonical source surfaces, then regenerate with the established adapter pipeline.

## First-Line Role Eligibility Check

Prime Builder is authorized to write `NEW` status for a fresh implementation proposal.

```json
{"session_role":"prime-builder","role_source":"owner-directed PROJECT-HARNESS-PARITY continuation; initial session role intent ::init gtkb pb","target_status":"NEW","authorized":true}
```

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - governs harness capability floors and machine-checkable harness artifacts. Codex skill adapters are part of the Codex harness capability surface and must expose the files they advertise.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires bridge-mediated implementation and verification through the append-only bridge file chain and dispatcher/TAFE bridge state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this implementation proposal to cite relevant governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, and work-item metadata in implementation-targeting bridge proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification evidence derived from every linked specification before `VERIFIED`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires concrete decisions, requirements, risks, work items, reports, and tests to be preserved as durable artifacts.
- `GOV-STANDING-BACKLOG-001` - `WI-4486` is the MemBase standing-backlog authority for this work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - establishes harness-specific fallback obligations and supports the general principle that Codex harness behavior must be explicit and machine-checkable rather than silently relying on a weaker fallback path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires preserving decisions, implementation reports, tests, and generated artifacts as a durable graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner-directed harness-governance changes trigger proposal, review, implementation report, and verification lifecycle records.

## Prior Deliberations

- `DELIB-20265431` - owner decision authorizing bounded implementation-proposal work for `WI-4486` under `PROJECT-HARNESS-PARITY`.
- `WI-4486` source owner directive - "The Codex skill adapter does not include the helper file at its adapter path, so runtime resolves it through the canonical .claude skill location the adapter names."
- `bridge/gtkb-antigravity-startup-overlay-integration-010.md` - immediately preceding `PROJECT-HARNESS-PARITY` verified bridge thread, demonstrating the current project-bridge closure pattern.

## Owner Decisions / Input

No additional owner decision is required before Loyal Opposition reviews this proposal.

Owner authorization is already captured as `DELIB-20265431` and active project authorization `PAUTH-PROJECT-HARNESS-PARITY-WI-4486-SKILL-ADAPTER-HELPER-PACKAGING`.

Boundaries from that authorization:

- Allowed mutation classes: `skill-adapter-generator`, `codex-skill-adapter-generated-files`, `regression-tests`.
- Forbidden operations: `production-deployment`, `credential-or-secret-mutation`.
- The authorization does not bypass bridge review, GO, implementation-start authorization, work-intent claim, implementation report, or Loyal Opposition verification.

## Requirement Sufficiency

Existing requirements are sufficient.

The work item description, source owner directive, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, and `DELIB-20265431` are enough to implement a bounded fix. The acceptance target is not a new feature: generated Codex adapters must include or expose the helper files they name, and tests must fail if adapter-owned helpers only resolve through canonical `.claude/skills` fallback paths.

## Spec-Derived Verification Plan

| Spec / requirement | Verification command or inspection | Expected result |
| --- | --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `WI-4486` | Add or update regression coverage in `platform_tests/scripts/test_generate_codex_skill_adapters.py` proving helper directories/files referenced by generated Codex adapters exist under `.codex/skills/<skill>/...` and do not require `.claude/skills/...` fallback. | Test fails before the fix and passes after adapter helper packaging is corrected. |
| Generated adapter parity | `groundtruth-kb\.venv\Scripts\python.exe scripts/generate_codex_skill_adapters.py --check --update-registry` | Generated `.codex/skills` adapters, `.codex/skills/MANIFEST.json`, and harness capability registry are current. |
| Codex adapter loadability | `groundtruth-kb\.venv\Scripts\pytest.exe platform_tests/scripts/test_codex_skill_load_smoke.py -q --tb=short` | Codex skill adapters load with their packaged helper/reference surfaces. |
| Harness parity surface | `groundtruth-kb\.venv\Scripts\pytest.exe platform_tests/scripts/test_check_harness_parity.py -q --tb=short` | Harness parity remains green for Codex skill surfaces. |
| Existing generator regression suite | `groundtruth-kb\.venv\Scripts\pytest.exe platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short` | Adapter generator tests pass, including the new helper-packaging regression. |
| Optional generated-skill scaffolding guard if affected | `groundtruth-kb\.venv\Scripts\pytest.exe platform_tests/skills/test_verify_skill_scaffolding.py -q --tb=short` | Verify-skill adapter scaffolding remains consistent if helper packaging touches that adapter. |
| Bridge filing gates | `groundtruth-kb\.venv\Scripts\python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-skill-adapter-helper-packaging --json`; `groundtruth-kb\.venv\Scripts\python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-skill-adapter-helper-packaging` | No missing required/advisory specs and no blocking clause gaps. |

## Acceptance Criteria

- Generated Codex skill adapters include or expose helper files at the adapter-relative paths they name.
- Regression coverage detects missing adapter-owned helper files and prevents silent success via canonical `.claude/skills` helper fallback.
- The fix is generated through `scripts/generate_codex_skill_adapters.py`; generated `.codex/skills` output is not hand-edited.
- Existing Codex skill load smoke, harness parity, and relevant skill scaffolding tests remain passing.
- No credential, production deployment, or unrelated project scope is touched.

## In-Root Placement Evidence

All implementation, generated-artifact, regression-test, and bridge outputs stay under `E:/GT-KB`.

- Bridge audit file: `E:/GT-KB/bridge/gtkb-codex-skill-adapter-helper-packaging-001.md`.
- Generator source: `E:/GT-KB/scripts/generate_codex_skill_adapters.py`.
- Generated Codex skill adapters: `E:/GT-KB/.codex/skills/`.
- Regression tests: `E:/GT-KB/platform_tests/`.
- Harness capability registry, if regenerated: `E:/GT-KB/config/agent-control/harness-capability-registry.toml`.

## Risk / Rollback

Risk is mostly generated-artifact churn: changing the generator may update several `.codex/skills` adapter files and the manifest. The implementation should keep the generator change minimal and let tests define the exact generated-output scope.

Rollback is a single local commit revert after verification, restoring the generator, tests, and generated adapter outputs. Because generated adapters are reproducible, a rollback should also rerun `scripts/generate_codex_skill_adapters.py --check --update-registry` to confirm the generated surfaces match the reverted generator behavior.

## Bridge Filing

This proposal is filed under `bridge/` as `bridge/gtkb-codex-skill-adapter-helper-packaging-001.md`; no prior version for this slug exists or is rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix:

The proposed implementation fixes an existing packaging defect in generated Codex skill adapter helper paths and adds regression coverage for that defect.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
