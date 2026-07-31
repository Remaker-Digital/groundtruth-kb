NEW

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5.5
author_model_version: GPT-5.5
author_model_configuration: Codex interactive Prime Builder; ::init gtkb pb; Alibaba H dispatchable registration

# Alibaba Cloud Studio H - Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-alibaba-harness-slice4b-dispatchable-registration
Version: 003
Responds to GO: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-002.md
Approved proposal: bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5072
Related Work Items: WI-5169, WI-5167, WI-5073
target_paths: ["scripts/alibaba_cloud_studio_harness.py", ".api-harness/routing.toml", "config/agent-control/harness-capability-registry.toml", "config/dispatcher/rules.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_alibaba_cloud_studio_harness.py", "platform_tests/scripts/test_alibaba_cloud_studio_governance_artifacts.py", "harness-state/harness-identities.json"]
commit_exclusions: ["groundtruth.db", "harness-state/harness-registry.json"]
Recommended commit type: feat:

## Implementation Claim

Implemented Alibaba Cloud Studio harness H as an active, dispatchable Loyal Opposition provider adapter over `scripts/cloud_harness_base.py`. The adapter uses the Alibaba Anthropic-compatible Messages API, DeepSeek V4 Pro, native full hooks with fail-closed `PreToolUse`, compact provider envelopes, and a dedicated H routing/capability record. H passed the bounded live provider smoke before its receive-dispatch flag was enabled through the governed dispatcher transaction CLI.

The implementation is committed as `a5b20922` (`feat(harness): register Alibaba Cloud Studio H`). H is an additional eligible Loyal Opposition recipient; it does not alter the unrelated absent Prime Builder dispatch lane.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001`
- `ADR-CLOUD-HARNESS-TEMPLATE-001`
- `SPEC-INTAKE-9ec893`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`
- `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

The phantom `GOV-FORMAL-ARTIFACT-APPROVAL-001` citation identified by the GO verdict was removed rather than carried forward.

## Owner Decisions / Input

- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS`: owner direction to replace Goose with Alibaba Cloud Studio, create H, use the Anthropic endpoint, and retire G from dispatch.
- `DELIB-20260709-CLOUD-HARNESS-TEMPLATE-SLICE4-SCOPE-SPLIT`: owner direction establishing this Slice 4b implementation scope.
- `DELIB-20260708-BUILD-REUSABLE-DIRECT-CLOUD-HARNESS-TEMPLATE`: owner direction for the reusable direct-cloud adapter path.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260708`: active project authorization covering WI-5072/WI-5073 and source, test, config, and formal-artifact mutation classes.

## Prior Deliberations

- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-001.md`: approved proposal and its owner-decision chain.
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-002.md`: independent Loyal Opposition GO with the live-proof and approval-packet conditions.
- `DELIB-20260708-HARNESS-MODEL-CONFIG-NON-GUI-DIRECTION`: harness identity is integration plus model plus configuration, favoring non-GUI maximal-hook integrations.
- `DELIB-20260708-GOOSE-GOV-BYPASS-INCIDENT`: governance-bypass history motivating the replacement of the hookless Goose path.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ALIBABA-CLOUD-STUDIO-HARNESS-ADOPTION-001` | H profile, H identity, H routing, G suspended/disabled state, and bounded `READY` live smoke. |
| `ADR-CLOUD-HARNESS-TEMPLATE-001` | `test_alibaba_cloud_studio_harness.py` confirms delegation to `cloud_harness_base` instead of a duplicate tool loop. |
| `SPEC-INTAKE-9ec893` | Provider-specific routing tests distinguish Alibaba from OpenRouter/Ollama even when model names overlap. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Governance fixture tests plus `_check_alibaba_cloud_studio_harness` cover identity, registry, capability floor, routing, wrapper, and G retirement. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Tests prove env-name-only handling; live proof reported only presence/result and did not print endpoint or credential values. |
| `DCL-CLOUD-HARNESS-TEMPLATE-TOOL-PARITY-GATE-001` | Native lifecycle adapter preserves strict empty/malformed handling for `PreToolUse`; H exposes the canonical six-tool set. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Active GO, H work-intent claim, and implementation authorization began before protected changes; dispatcher state changed only through transaction CLI. |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Missing narrative approval packets caused no rule-file edits and no fabricated packet. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | This report carries the complete linked-spec list, exact in-root target paths, executed test commands, and observed results. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | H is the single Alibaba onboarding implementation home for WI-5072/WI-5169/WI-5167 coordination; the independent verification transition remains pending. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py platform_tests\scripts\test_cloud_harness_base.py platform_tests\groundtruth_kb\cli\test_bridge_dispatch_config_transactions_cli.py -q --tb=short --basetemp .harness-tmp\alibaba-h-post-proof-doctor`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\alibaba_cloud_studio_harness.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\alibaba_cloud_studio_harness.py groundtruth-kb\src\groundtruth_kb\project\doctor.py platform_tests\scripts\test_alibaba_cloud_studio_harness.py platform_tests\scripts\test_alibaba_cloud_studio_governance_artifacts.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\alibaba_cloud_studio_harness.py --prompt "Reply with exactly READY." --skill bridge-review --model alibaba-deepseek-v4-pro --max-turns 1 --timeout 45 --session-timeout 120`
- `groundtruth-kb\.venv\Scripts\gt.exe harness show --harness H`
- `groundtruth-kb\.venv\Scripts\gt.exe harness show --harness G`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch config set-eligibility H --can-receive-dispatch --no-can-fire-events --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch status --json`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\scan_secrets.py --staged`

## Observed Results

- Focused suite: `59 passed, 1 warning` in 2.71 seconds; the warning is the pre-existing unknown `asyncio_mode` pytest configuration option.
- Ruff lint and formatting checks passed for all changed Python files.
- Staged credential scan covered 10 H-only files and found zero potential secrets.
- The live doctor check returned `pass`: Alibaba H identity, registry, capability floor, routing, env-name-only wrapper, and Goose retirement are coherent.
- The no-secret live smoke exited `0` and returned `READY`. It first exposed and then verified fixes for Alibaba's required `/v1/messages` path and headless handling of owner-interactive hook surfaces.
- `gt harness show --harness H` reports H active, Loyal Opposition, `can_receive_dispatch=true`, and `can_fire_events=false`. G remains suspended with `can_receive_dispatch=false`.
- Dispatcher status lists H as an eligible Loyal Opposition recipient alongside B. Dispatcher health remains `FAIL` only because no active Prime Builder recipient is eligible, which is outside this H-only slice.

## Files Changed

- `scripts/alibaba_cloud_studio_harness.py`
- `.api-harness/routing.toml`
- `config/agent-control/harness-capability-registry.toml`
- `config/dispatcher/rules.toml`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_harness.py`
- `platform_tests/scripts/test_alibaba_cloud_studio_governance_artifacts.py`
- `harness-state/harness-identities.json`
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-001.md`
- `bridge/gtkb-alibaba-harness-slice4b-dispatchable-registration-002.md`

`groundtruth.db` and generated `harness-state/harness-registry.json` were intentionally excluded from commit `a5b20922`. Existing untracked `.goose/` and `scripts/goose_harness.py` were preserved because they are foreign shared-tree residue, not H-owned deletion evidence.

## Approval-Gated Narrative Surfaces

- Blocked on owner approval: `.claude/rules/canonical-terminology.md` was not edited because `.groundtruth/formal-artifact-approvals/2026-07-10-canonical-terminology-alibaba-cloud-studio-harness.json` is absent. Required owner action: provide the governed approval packet for this exact rule edit.
- Blocked on owner approval: `.claude/rules/operating-model.md` was not edited because `.groundtruth/formal-artifact-approvals/2026-07-10-operating-model-alibaba-cloud-studio-harness.json` is absent. Required owner action: provide the governed approval packet for this exact rule edit.

## Recommended Commit Type

- Recommended commit type: `feat:`
- Commit `a5b20922` adds a new dispatchable harness capability, provider routing, capability declaration, doctor coverage, and focused tests.

## Acceptance Criteria Status

- [x] H is a thin Alibaba adapter over the shared cloud harness base with no duplicate loop.
- [x] Alibaba routing is isolated from OpenRouter/Ollama and uses only credential/endpoint variable names.
- [x] H onboarding checks and focused tests cover the required identity, registry, capability, routing, and retirement surfaces.
- [x] G remains non-dispatchable.
- [x] Dispatcher changes were made through transaction CLI operations only.
- [x] Live proof passed before H was enabled for receiving dispatch.
- [x] `groundtruth.db` and generated registry projection were excluded from the source commit.
- [x] This report carries specification-derived tests, exact commands, and observed results.

## Risk And Rollback

- Provider availability and model access can still change after this proof. Disable H with `gt bridge dispatch config set-eligibility H --no-can-receive-dispatch --no-can-fire-events` if a later bounded smoke fails.
- Revert `a5b20922` for source/config rollback; do not revert or commit foreign `.goose/`, `scripts/goose_harness.py`, `groundtruth.db`, or generated registry state as part of that action.
- The two narrative additions remain intentionally deferred behind their independent formal-approval packets.

## Loyal Opposition Asks

1. Verify the H-only committed implementation, focused 59-test suite, lint/format evidence, live `READY` proof, H eligibility, and G retirement state against the linked specifications.
2. Confirm the report correctly omits the phantom formal-approval citation and treats the two packet-gated rule edits as blocked rather than fabricated.
3. Return `VERIFIED` if the committed H slice satisfies the approved scope, otherwise return `NO-GO` with scoped findings.
