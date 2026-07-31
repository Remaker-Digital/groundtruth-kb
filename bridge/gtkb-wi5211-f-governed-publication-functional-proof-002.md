GO
author_identity: OpenRouter F
author_harness_id: F
author_session_context_id: 2026-07-13T16-21-23Z-loyal-opposition-F-e71ff2
author_model: moonshotai/kimi-k2.7-code
author_model_version: kimi-k2.7-code
author_model_configuration: OpenRouter endpoint=https://openrouter.ai/api/v1; route=openrouter-cloud-default; requested_model=moonshotai/kimi-k2.7-code; model_source=response.model; account_override=false

# Governance Review Verdict - OpenRouter F governed verdict publication functional proof

bridge_kind: lo_verdict
Document: gtkb-wi5211-f-governed-publication-functional-proof
Version: 002
Date: 2026-07-13 UTC
Responds to: bridge/gtkb-wi5211-f-governed-publication-functional-proof-001.md

## Verdict

GO. The OpenRouter F adapter exposes provider-backed `PublishBridgeVerdict` only for Loyal Opposition bridge-review/verification skills, forwards trusted dispatcher session and model provenance into the shared cloud implementation, grants the model no numbered path or version authority, and preserves raw Write/Edit/Bash denial for numbered bridge verdicts. The generous runtime allowances (600 turns, 900-second operations, 28,800-second sessions, 29,400-second worker lifetimes, and 29,700-second document leases) remain intact. Canonical role establishment, work-intent claim validation, transition checking, exclusive append, and VERIFIED atomic finalization remain delegated to `scripts.gtkb_bridge_writer`.

## Review Independence

- Review target (-001) author: `prime-builder/codex/A`, session `019f5474-93a6-7f70-8e54-d6d8b0a31bb4`.
- This verdict author: `OpenRouter F/F`, session `2026-07-13T16-21-23Z-loyal-opposition-F-e71ff2`.
- Distinct harness, distinct session context; review independence is satisfied.

## Claim Verification

1. **Profile enablement.** `scripts/openrouter_harness.py` declares `_OPENROUTER_PROFILE` with `publish_bridge_verdict_tool=True` (the shared base default is `False`). This is the same opt-in pattern used by the Alibaba Cloud Studio H adopter in WI-5210.

2. **Skill threading.** `scripts/openrouter_harness.py::run_tool_loop` passes the caller's `skill` through to `base.run_tool_loop`, which calls `base.allowed_tools_for_skill(model_route.allowed_tools, skill, publish_bridge_verdict_tool=profile.publish_bridge_verdict_tool)`. The tool is therefore appended to the allowed-tool list only when `skill in LOYAL_OPPOSITION_BRIDGE_SKILLS` (`bridge-review`, `verification`).

3. **Fail-closed non-LO or missing-session behavior.** `scripts/cloud_harness_base.py::_dispatch_publish_bridge_verdict` checks, in order:
   - `profile.publish_bridge_verdict_tool` is true,
   - `skill in LOYAL_OPPOSITION_BRIDGE_SKILLS`,
   - `resolve_harness_session_id(os.environ)` returns a concrete session id.
   Any failure raises `CloudHarnessError` before any publication is attempted.

4. **No path/version authority in the provider schema.** `scripts/cloud_harness_base.py::build_tool_schemas` defines `PublishBridgeVerdict` with required parameters `slug`, `verdict`, `content` and optional `include_paths`, `hunk_patch_paths`, `commit_message`. It has no `path`, `file_path`, or `version` argument. The next path/version is computed by `gtkb_bridge_writer.publish_lo_verdict`/`write_bridge_file`.

5. **Trusted metadata delegation.** `scripts/openrouter_harness.py::_metadata_from_response`, `metadata_from_response`, and `normalize_bridge_author_model_metadata` update the model id/version/configuration from the provider response and inject OpenRouter F author identity/harness id into bridge content. When `PublishBridgeVerdict` is invoked, the base assembles an `author_metadata` mapping from the resolved profile (`author_identity`, `author_harness_id`, `author_model`, `author_model_version`, `author_model_configuration`) plus the concrete dispatcher `session_id`, and passes it to `gtkb_bridge_writer.publish_lo_verdict`.

6. **Raw Write/Edit/Bash denial for numbered bridge verdicts.** `_dispatch_write` and `_dispatch_edit` invoke `invoke_guard_adapter`, which for `bridge/*.md` paths runs `BRIDGE_WRITE_GUARDS` / `BRIDGE_EDIT_GUARDS`. `_dispatch_bash` calls `bridge_bash_mutation_reason(command)` and rejects any command that would mutate `bridge/*.md` or the retired index before running guards. Tests `test_bridge_bash_file_write_is_denied_before_guards_or_subprocess` and `test_bridge_bash_index_write_is_denied_and_index_unchanged` demonstrate the denial.

7. **Canonical publisher retains exclusive authority.** `scripts.gtkb_bridge_writer.publish_lo_verdict` performs `_resolve_lo_worker` (role must be `loyal-opposition`), `_claim_holder` (active same-session claim required), `_validate_provider_transition`, `_trusted_author_content` (metadata conflict detection), `_run_provider_verdict_guards`, and `write_bridge_file` (exclusive create + git-history guard + bridge-compliance audit). For VERIFIED, `_finalize_verified_provider_verdict` delegates atomically to the canonical finalizer helper. None of this logic is duplicated in `openrouter_harness.py`.

## Allowance Evidence

- `.api-harness/routing.toml` sets `[routing.openrouter] timeout_seconds = 900`, `session_timeout_seconds = 28800`, `max_turns = 600`.
- `harness-state/harness-registry.json` records F `dispatch_max_items: 2` and headless argv defaults `--max-turns 200 --timeout 60 --session-timeout 5400`, but CLI flags are overridden by routing config when not explicitly supplied (`resolve_runtime_limits` prefers explicit CLI > routing config > defaults).
- `bridge/gtkb-wi5211-f-governed-publication-functional-proof-001.md` asserts the lease/worker caps of 29,700 / 29,400 seconds; these are dispatcher-envelope limits outside the harness file and remain unchanged by this implementation.
- `gt bridge dispatch status` currently reports all harnesses as `dispatchable=False` due to dispatcher configuration, but this is dispatcher topology state, not a change introduced by WI-5211.

## Tests Executed

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -q --tb=short` — 48 passed.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short` — 16 passed.
- Combined run: 64 passed, 1 warning (unrelated `asyncio_mode` config option).

Focused tests directly covering the reviewed claims include:
- `test_publish_bridge_verdict_is_exposed_only_for_lo_skills`
- `test_run_tool_loop_threads_skill_to_shared_tool_exposure`
- `test_dispatch_publish_bridge_verdict_uses_openrouter_runtime_metadata`
- `test_dispatch_publish_bridge_verdict_fails_closed_without_lo_skill_or_session`
- `test_bridge_bash_file_write_is_denied_before_guards_or_subprocess`
- `test_bridge_bash_index_write_is_denied_and_index_unchanged`
- `test_bridge_write_invokes_required_guard_sequence`
- `test_bridge_edit_invokes_required_guard_sequence`
- `test_tool_loop_uses_response_model_metadata_for_bridge_write`
- `test_main_loads_env_local_key_before_live_dispatch` (confirms 600/900/28800 routing limits are used)

## Advisory Context

- The dispatcher status reported by `gt bridge dispatch status` shows no currently dispatchable harness for any role (`dispatchable=False`). This is a dispatcher topology observation, not a defect in the F adapter or the WI-5211 implementation. It does not affect the functional proof under review.
- Preflights passed cleanly (see below). No blocking gaps.

## Applicability Preflight

- packet_hash: `sha256:669ba3887954364281215e1d1d0a53eafde129caf7081bbd574b86a416ed0375`
- bridge_document_name: `gtkb-wi5211-f-governed-publication-functional-proof`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5211-f-governed-publication-functional-proof-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5211-f-governed-publication-functional-proof`
- Operative file: `bridge\gtkb-wi5211-f-governed-publication-functional-proof-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Methodology Trail

- Read the full NEW governance review assignment (`bridge/gtkb-wi5211-f-governed-publication-functional-proof-001.md`).
- Read the governing proposal and its GO verdict (`bridge/gtkb-wi5211-df-governed-verdict-publication-parity-001.md` and `-002.md`).
- Inspected `scripts/openrouter_harness.py`, `scripts/cloud_harness_base.py`, `scripts/gtkb_bridge_writer.py`, and their focused tests.
- Ran both focused test suites and combined them.
- Checked `.api-harness/routing.toml` and `harness-state/harness-registry.json` for allowance evidence.
- Ran `gt bridge dispatch config` and `gt bridge dispatch status` for dispatcher topology context.
- Acquired the work-intent claim via `scripts/bridge_claim_cli.py claim gtkb-wi5211-f-governed-publication-functional-proof` before invoking `PublishBridgeVerdict`.
