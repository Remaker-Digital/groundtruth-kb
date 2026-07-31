NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-05T22-13-00Z-prime-builder-A-7ad6c6
author_model: GPT-5.5
author_model_version: GPT-5.5
author_model_configuration: Codex dispatcher-spawned headless Prime Builder worker (dispatch 2026-07-05T22-13-00Z-prime-builder-A-7ad6c6); resolved role prime-builder

# WI-5028 Dispatch Run Author Identity Fallback - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi5028-dispatch-run-author-identity-fallback
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-002.md
Approved proposal: bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-001.md
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5028-BATCH-A2-20260705
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5028
Implementation authorization packet: sha256:fd23321ddacd0c017d7b54cc2b35e170554c1e644a4c5ad58302ce728345bf57

## Implementation Claim

Implemented the approved WI-5028 fallback-order repair in `scripts/bridge_author_metadata.py`.

When `GTKB_HARNESS_NAME` is absent, `_resolve_durable_identity_fields()` now parses well-formed dispatcher run ids from `GTKB_BRIDGE_POLLER_RUN_ID` before using the active-Prime fallback. The parser recognizes dispatcher ids in the form `<timestamp>-<canonical-role-token>-<harnessId>-<hex6>`, including role tokens with internal dashes such as `loyal-opposition`, and resolves the parsed harness id through the current registry projection. The dispatch role token is locator evidence only; the stamped role still comes from the durable registry role set. A well-formed dispatch id that points to an unknown harness fails closed instead of falling through to an unrelated Prime stamp.

Added focused regression coverage in `platform_tests/scripts/test_bridge_author_metadata.py` for realistic LO/B and Prime/A dispatch ids, registry-role authority on token disagreement, malformed role-only ids, full `load_author_metadata()` composition, and preservation of the existing non-dispatch/active-Prime fallback behavior.

## Specification Links

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - bridge artifacts must carry accurate durable author identity and harness id.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - status-bearing bridge verdict files are canonical workflow evidence, so their provenance must be trustworthy.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role authority comes from durable registry/dispatch context, not a misleading active-Prime fallback.
- `DCL-SESSION-ROLE-RESOLUTION-001` - dispatcher session context and durable role data must resolve consistently for headless workers.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Batch A2 PAUTH permits this bounded source/test fix but does not replace LO review or implementation-start authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge review or implementation-start gates.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation stayed within the named WI-5028 source/test envelope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation report carries PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing provenance, role, and bridge specs are cited and mapped to verification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification includes focused tests and observed command evidence.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - provenance resolution works for cross-harness headless workers, not only interactive Codex/Claude sessions.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` - WI-5028 closure evidence covers the concrete LO dispatch-stamp defect.
- `GOV-STANDING-BACKLOG-001` - the open WI is advanced through durable bridge/test evidence.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - implementation reads current registry projection and dispatch-id semantics rather than cached summaries.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - provenance defects and repair evidence remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the fix is preserved through bridge, source, and tests rather than session-local memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - verdict/report filing remains the lifecycle trigger where accurate author metadata is required.

## Owner Decisions / Input

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner approved continuing the high-priority queue through governed implementation/disposition work.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5028-BATCH-A2-20260705` - active Batch A2 authorization for WI-5028 source, tests, and governance evidence.

No additional owner decision was required.

## Prior Deliberations

- `bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi5028-dispatch-run-author-identity-fallback-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner authorization for continuing Batch A2 high-priority reliability fixes.

## Specification-Derived Verification Plan

| Governing surface | Executed verification evidence |
| --- | --- |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | `test_dispatch_run_id_resolves_durable_identity_when_harness_name_unset` and `test_load_author_metadata_uses_dispatch_run_id_for_durable_identity` prove a realistic LO/B dispatch run id stamps `author_identity=loyal-opposition/claude` and `author_harness_id=B`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The implementation is filed as the next append-only numbered bridge report after latest `GO`; source/test mutation was preceded by implementation authorization packet `sha256:fd23321ddacd0c017d7b54cc2b35e170554c1e644a4c5ad58302ce728345bf57`. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | `test_dispatch_run_id_token_role_does_not_override_registry_role` proves the dispatch token role does not override the durable registry role. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | `test_load_author_metadata_uses_dispatch_run_id_for_durable_identity` covers dispatcher session-context resolution plus durable registry identity resolution. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5028-dispatch-run-author-identity-fallback` passed before source/test edits and returned active PAUTH metadata. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | The source/test change proceeded only after the latest bridge state was verified as `GO` and implementation-start authorization succeeded. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `git diff -- scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py` shows the claimed implementation is confined to the approved source/test paths. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries `Project Authorization`, `Project`, and `Work Item` metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This section carries forward all linked specs from the approved proposal and maps each family to executed verification. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Targeted pytest, Ruff lint, and Ruff format checks were executed and passed; observed results are listed below. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Parser tests cover LO/B, Prime/A, and acting-prime/E dispatcher role tokens through registry fixtures rather than a Claude-only special case. |
| `DCL-SPEC-RELEVANCE-CLOSURE-001` | Regression tests directly cover the WI-5028 concrete defect: absent `GTKB_HARNESS_NAME` plus LO/B dispatcher id no longer falls back to Prime/Codex A. |
| `GOV-STANDING-BACKLOG-001` | The WI is advanced through bridge report evidence and awaits Loyal Opposition verification rather than untracked session memory. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The implementation resolves identities through projection-backed `load_harness_identities()` / `load_role_assignments()` at call time. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The defect, implementation evidence, commands, and residual risk are captured in this durable bridge artifact. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Code, tests, implementation-start packet, and this report preserve the decision trail in governed artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The bridge report is the lifecycle trigger for LO verification of the implemented provenance repair. |

## GO Carry-Forward Conditions

- F1: Addressed. The parser anchors on canonical role tokens (`acting-prime-builder`, `loyal-opposition`, `prime-builder`) rather than naive dash splitting; `test_dispatch_run_id_parser_handles_realistic_role_tokens` uses realistic dash-containing role tokens.
- F2: Addressed. `test_malformed_dispatch_run_id_does_not_resolve_harness_suffix` proves a role-only/malformed dispatch id does not treat the suffix as a harness id.
- F3: Addressed. `test_dispatch_run_id_token_role_does_not_override_registry_role` documents and verifies registry-preferred role labeling when the dispatch token role disagrees with the durable role set.
- F4: Addressed. Existing non-dispatch and active-Prime fallback tests remained in the same file and passed in the targeted pytest run.

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi5028-dispatch-run-author-identity-fallback
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_author_metadata.py -q --tb=short --basetemp .gtkb-state/pytest-tmp-wi5028
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_author_metadata.py platform_tests/scripts/test_bridge_author_metadata.py
```

## Observed Results

```text
implementation_authorization.py begin: exit 0; latest_status=GO; target_path_globs=["scripts/bridge_author_metadata.py", "platform_tests/scripts/test_bridge_author_metadata.py"]; packet_hash=sha256:fd23321ddacd0c017d7b54cc2b35e170554c1e644a4c5ad58302ce728345bf57
pytest: 21 passed, 2 warnings in 0.25s
ruff check: All checks passed!
ruff format --check: 2 files already formatted
```

The pytest warnings were unrelated to this implementation: `asyncio_mode` is an unknown config option in this environment, and pytest could not update one existing `.pytest_cache` path because it already existed.

## Files Changed

Claimed implementation files:

- `scripts/bridge_author_metadata.py`
- `platform_tests/scripts/test_bridge_author_metadata.py`

The worktree already contained many unrelated modified and untracked files before this dispatch. They are not part of this implementation claim.

## Acceptance Criteria Status

- With `GTKB_HARNESS_NAME` unset and a dispatch-format LO/B run id, durable fields resolve to the B harness's durable LO identity: satisfied by `test_dispatch_run_id_resolves_durable_identity_when_harness_name_unset` and `test_load_author_metadata_uses_dispatch_run_id_for_durable_identity`.
- Explicit `GTKB_HARNESS_NAME` and explicit metadata still take precedence where they already do: existing `test_explicit_overrides_env_and_identity` and embedded metadata short-circuit tests passed unchanged.
- Dispatch token role is not treated as authority when registry role differs: satisfied by `test_dispatch_run_id_token_role_does_not_override_registry_role`.
- Malformed/non-dispatch run ids do not synthesize a wrong identity: satisfied by `test_malformed_dispatch_run_id_does_not_resolve_harness_suffix` and the existing `test_dispatch_run_id_wins_for_runtime_session_context`.
- Existing runtime session/model envelope behavior and stale-current fail-closed tests remain green: targeted pytest passed all existing tests in the file.
- No KB mutation, credential action, deployment, destructive cleanup, broad status mutation, dispatcher routing change, or bridge-history rewrite was performed.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: repairs a concrete bridge-verdict author-provenance defect.

## Risk And Rollback

Residual risk is low. The parser intentionally accepts only the dispatcher id format emitted by `_new_dispatch_id()` and only uses the parsed role token to locate the harness-id segment. The registry remains the role authority, and malformed/non-dispatch ids keep the previous fallback/fail-closed behavior.

Rollback is a revert of the two claimed implementation files plus this append-only bridge report if verification rejects the change. Prior bridge history must remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Confirm F1-F4 from the GO verdict are satisfied.
3. Return `VERIFIED` if the implementation and report satisfy the approved proposal, otherwise return `NO-GO` with findings.
