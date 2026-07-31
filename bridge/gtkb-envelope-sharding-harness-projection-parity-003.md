NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1bfe-9f4b-7bc2-805e-c051192b5a73
author_model: gpt-5-codex
author_model_version: 2026-07-01
author_model_configuration: Codex Desktop interactive Prime Builder session; implementation report for WI-4950 harness projection parity

# GT-KB Bridge Implementation Report - gtkb-envelope-sharding-harness-projection-parity - 003

bridge_kind: implementation_report
Document: gtkb-envelope-sharding-harness-projection-parity
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-envelope-sharding-harness-projection-parity-002.md
Approved proposal: bridge/gtkb-envelope-sharding-harness-projection-parity-001.md
Recommended commit type: feat

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4950
Project: PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING
Work Item: WI-4950
Implementation Authorization Packet: sha256:59bd9390bc0fccb3400fdc6189624aeb5b0046e5d8f195272d892caa02079085
Work-Intent Claim: gtkb-envelope-sharding-harness-projection-parity / prime-builder / session 019f1bfe-9f4b-7bc2-805e-c051192b5a73
Focused Commit: c2ab2d17f

target_paths: ["config/agent-control/harness-capability-registry.toml", "config/harness-parity/phase2-waivers.toml", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "scripts/check_harness_parity.py", "scripts/generate_api_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/generate_codex_skill_adapters.py", "platform_tests/scripts/test_check_harness_parity.py", "platform_tests/scripts/test_harness_projection_reader.py", "platform_tests/scripts/test_api_skill_adapters.py", "platform_tests/scripts/test_antigravity_startup_overlay_integration.py"]

## Implementation Claim

Implemented WI-4950 as a cross-harness activity/result/session-envelope projection and parity surface. The implementation adds explicit activity-envelope projection mode, compact result-envelope mode, compact session-envelope mode, transcript-archive requirement, manifest source, and limitation metadata to the harness capability registry for Claude, Codex, Antigravity, Cursor, Ollama, and OpenRouter.

`groundtruth_kb.harness_projection` now preserves those envelope metadata fields in harness projections and defaults provider harnesses to `compact-provider` when registry data omits explicit mode values. `scripts/check_harness_parity.py` now emits required activity-envelope parity rows for declared harnesses and fails those rows when a mode is missing/invalid or when a harness requires full transcript archive loading. Provider lanes are represented as compact-provider modes with typed full-transcript archive waivers rather than pretending they own native hook infrastructure.

The focused commit is `c2ab2d17f`. The staged set was limited to eight approved WI-4950 target paths. The checkout had broad pre-existing dirty state, including some target-path edits; I worked with the in-scope target-path state and did not stage unrelated files.

## Specification Links

- `SPEC-INTAKE-46594e`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - owner directive to complete all child work items in this project and retire it after governed verification.
- `PAUTH-PROJECT-GTKB-SESSION-ACTIVITY-ENVELOPE-SHARDING-WI-4950` - bounded implementation authorization for WI-4950 only.

No new owner decision is required by this implementation report.

## Prior Deliberations

- `DELIB-20260701-ENVELOPE-SHARDING-EXECUTE-RETIRE` - current owner execution directive.
- `DELIB-202665110` - umbrella program and PAUTH creation authorization.
- `DELIB-20266631` - Loyal Opposition context for activity-envelope context sharding.
- `DELIB-20265892` - disposition-profile ratification.
- `DELIB-20260630-ACTIVITY-ENVELOPE-SHARDING-AUTHORIZATION` - prior envelope refinement authorization.
- `DELIB-20265287` - single-active activity envelope, named disposition profile, and headless eligibility decisions.
- `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` - context-load profile anatomy and activity vocabulary.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - existing harness parity waiver and provider-lane limitation context.
- `bridge/gtkb-envelope-sharding-harness-projection-parity-001.md` - approved implementation proposal.
- `bridge/gtkb-envelope-sharding-harness-projection-parity-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-INTAKE-46594e` | Harness registry and parity output now distinguish base/activity/result/session envelope behavior per harness; `check_harness_parity.py --all --json` reported 24 activity-envelope parity rows and zero non-PASS activity rows. |
| `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001` | Registry rows point activity-envelope manifest source to `config/agent-control/activity-disposition-profiles.toml`; tests verify Antigravity optimized-startup and provider compact-provider projection modes. |
| `DCL-ACTIVITY-DISPOSITION-PROFILE-001` | Parity checks validate declared envelope projection modes against an explicit mode vocabulary instead of accepting untyped free-form claims. |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` | The new parity rows fail if a declared harness requires full transcript archive loading; provider lanes use compact-provider modes and typed transcript waivers. |
| `ADR-EXPLICIT-HINT-CONTEXT-MANAGEMENT-001` | Full transcript archive loading is represented as a required false condition for this parity surface; explicit detailed history remains outside startup by representation. |
| `ADR-CROSS-HARNESS-PARITY-001` | The shared parity checker covers Claude, Codex, Antigravity, Cursor, Ollama, and OpenRouter envelope modes in one report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation occurred only after latest GO, Prime work-intent claim, and implementation-start packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Capability registry metadata, typed waivers, projection reader code, parity checks, tests, commit, and bridge report are durable artifacts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward every linked specification from the approved proposal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps linked specifications to executed command evidence and observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization, Project, and Work Item metadata are present in proposal, GO verdict, and this report. |
| `GOV-STANDING-BACKLOG-001` | No bulk backlog/project mutation was performed in this slice. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | No hook behavior was changed; parity is represented through shared registry/projection/checker surfaces. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Cross-harness envelope claims now live in config/code/tests rather than transcript-only notes. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No new owner decision or requirement was introduced during implementation; existing governing artifacts were cited and preserved. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-envelope-sharding-harness-projection-parity --session-id 019f1bfe-9f4b-7bc2-805e-c051192b5a73`
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-envelope-sharding-harness-projection-parity --session-id 019f1bfe-9f4b-7bc2-805e-c051192b5a73`
- `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_harness_projection_reader.py platform_tests/scripts/test_antigravity_startup_overlay_integration.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_api_skill_adapters.py::test_ollama_registry_declares_adapter_support platform_tests/scripts/test_api_skill_adapters.py::test_openrouter_registry_declares_compact_provider_envelopes -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/harness_projection.py scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_harness_projection_reader.py platform_tests/scripts/test_api_skill_adapters.py platform_tests/scripts/test_antigravity_startup_overlay_integration.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/harness_projection.py scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_harness_projection_reader.py platform_tests/scripts/test_api_skill_adapters.py platform_tests/scripts/test_antigravity_startup_overlay_integration.py`
- `python -c "import json, subprocess, sys; p=subprocess.run([sys.executable, 'scripts/check_harness_parity.py', '--all', '--json'], text=True, capture_output=True); ..."`
- `python -c "import tomllib; data=tomllib.load(open('config/agent-control/harness-capability-registry.toml','rb')); ..."`
- `git diff --check -- config/agent-control/harness-capability-registry.toml config/harness-parity/phase2-waivers.toml groundtruth-kb/src/groundtruth_kb/harness_projection.py scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_harness_projection_reader.py platform_tests/scripts/test_api_skill_adapters.py platform_tests/scripts/test_antigravity_startup_overlay_integration.py`
- `git commit -m "feat(parity): add activity envelope projection parity (WI-4950)"`

## Observed Results

- Work-intent claim succeeded as `go_implementation` for Prime Builder session `019f1bfe-9f4b-7bc2-805e-c051192b5a73`.
- Implementation-start packet succeeded with packet hash `sha256:59bd9390bc0fccb3400fdc6189624aeb5b0046e5d8f195272d892caa02079085`.
- Focused pytest over parity checker, projection reader, and Antigravity startup overlay integration: 35 tests collected; 35 passed.
- Focused provider API assertions: 2 tests collected; 2 passed.
- Ruff check over changed Python paths: all checks passed.
- Ruff format check over changed Python paths: 6 files already formatted.
- TOML parse: registered harnesses were `antigravity`, `claude`, `codex`, `cursor`, `ollama`, and `openrouter`; OpenRouter mode parsed as `compact-provider`; Antigravity mode parsed as `optimized-startup`.
- `scripts/check_harness_parity.py --all --json`: exit 0, overall status `WARN`, counts `PASS: 234`, `DEGRADED: 52`, `STALE: 9`, `UNSUPPORTED: 97`; activity-envelope rows: 24; activity-envelope non-PASS rows: 0.
- `git diff --check` exited 0. It emitted only line-ending warnings for files already subject to CRLF conversion on next Git touch.
- Commit hook evidence for `c2ab2d17f`: scanned 8 staged files, found 0 potential secrets, inventory drift PASS, narrative-artifact evidence PASS, ruff format PASS for 6 staged Python files, protected-commit authorization PASS for 8 protected paths.

## GO Concerns Addressed

1. Cross-Harness Disposition copy/paste concern: this implementation did not change `.claude`, `.codex`, `.cursor`, or `.agent` hook/skill files. It implemented the actual target-path scope: registry, typed waivers, projection reader, parity checker, and tests.
2. Provider result-envelope parity concern: provider lanes are explicitly represented as `compact-provider` for activity/result/session envelope modes. Full transcript archive limitations are recorded as active typed waivers for Ollama and OpenRouter.
3. WI-4949 dependency concern: WI-4950 proceeds independently as a representation/projection/checker slice. It does not migrate startup shards or claim WI-4949 behavior. WI-4949 remains a separate GO implementation lane and was held by another Prime Builder claim at the time this report was filed.

## Files Changed

- `config/agent-control/harness-capability-registry.toml`
- `config/harness-parity/phase2-waivers.toml`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `scripts/check_harness_parity.py`
- `platform_tests/scripts/test_check_harness_parity.py`
- `platform_tests/scripts/test_harness_projection_reader.py`
- `platform_tests/scripts/test_api_skill_adapters.py`
- `platform_tests/scripts/test_antigravity_startup_overlay_integration.py`

No changes were made to `scripts/generate_api_skill_adapters.py`, `scripts/generate_antigravity_skill_adapters.py`, or `scripts/generate_codex_skill_adapters.py`; the implementation did not need generator behavior changes.

## Known Residuals And Dependency Notes

- Full `platform_tests/scripts/test_api_skill_adapters.py` remains unsuitable as acceptance evidence in the live checkout because generated API adapter drift from WI-4951 currently reports `.api-harness/skills/gtkb-benchmarks/SKILL.md` and `.api-harness/skills/MANIFEST.json` would update. Those paths are outside WI-4950 target paths. The provider-envelope assertions in that file pass and are included above.
- The full parity report remains `WARN` because of existing DEGRADED/STALE/UNSUPPORTED rows outside this slice. The new activity-envelope parity rows are all PASS.
- This slice does not perform the startup shard migration itself. That remains WI-4949.

## Acceptance Criteria Status

- [x] `WI-4950` is implemented only within the target paths listed in the approved proposal.
- [x] `TEST-11255` has concrete PASS evidence: activity-envelope parity rows are emitted for registered harnesses, provider lanes can be assessed without full transcript archives, and provider compact-provider assertions pass.
- [x] Routine focused-agent workflow for this slice avoids loading unrelated activity content into the global session envelope by using compact registry/projection/parity metadata rather than raw transcript or archival payloads.
- [x] Out-of-scope generated adapter drift from WI-4951 is disclosed here rather than hidden or fixed under WI-4950.

## Risk And Rollback

Residual risk: this slice models envelope capability and parity, but it does not by itself enforce runtime startup loading. Runtime movement remains in WI-4949 and measurement remains in WI-4951.

Residual risk: provider result/session envelopes are represented as compact-provider parity rather than native hook parity. This is intentional and backed by typed waivers for full transcript archive limitations.

Rollback for this slice is to revert focused commit `c2ab2d17f`, removing the registry envelope fields, provider transcript waivers, harness projection metadata handling, parity checker rows, and focused tests. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the registry/projection/checker surfaces represent activity, result, and session envelope behavior across Claude, Codex, Antigravity, Cursor, Ollama, and OpenRouter.
2. Verify that provider lanes are correctly handled through compact-provider modes and typed full-transcript archive waivers.
3. Verify that the focused commit and command evidence satisfy the approved WI-4950 proposal without requiring WI-4949 to be complete first.
4. Return `VERIFIED` if the implementation and evidence satisfy the approved proposal; otherwise return `NO-GO` with findings.
