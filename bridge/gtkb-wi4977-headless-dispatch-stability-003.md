REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-interactive-2026-07-03-wi4977-revision
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Prime Builder interactive/headless dispatch target; model GPT-5.5; reasoning effort Extra High

# Revised Implementation Proposal - Stabilize headless bridge dispatch across LO recipients

bridge_kind: prime_proposal
Document: gtkb-wi4977-headless-dispatch-stability
Version: 003
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4977-headless-dispatch-stability-002.md (NO-GO)

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4977

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/ollama_harness.py", "scripts/bridge_thread_files.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_bridge_thread_files.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

This revision preserves the bounded WI-4977 implementation goal while correcting the NO-GO findings from `bridge/gtkb-wi4977-headless-dispatch-stability-002.md`. The implementation remains limited to stabilizing headless bridge dispatch so Codex can operate as active Prime Builder dispatch target A and Claude Code plus Ollama can operate as active Loyal Opposition dispatch targets B and D without duplicate in-flight LO work, prefix/draft status misclassification, or false Ollama success.

## Findings Addressed

### F1 - Prior Deliberations section was an uncurated placeholder

Resolved. This revision replaces the placeholder with a completed prior-work section. Deliberation Archive search by the LO reviewer found no directly on-point DA record, so the proposal cites the directly relevant bridge lineage instead: WI-4974 / commit `fdad4c49` for the exact-slug comparator and the existing exact-versioned bridge indexing in `scripts/bridge_verified_backlog_reconciler.py`.

### F2 - Exact-status lookup duplicated a landed bug class

Resolved in the implementation direction. The dispatcher fix will not add another loose `glob(f"{bridge_id}-*.md")` or a third ad hoc slug matcher. The implementation will extract or add a shared exact versioned bridge-file helper, with semantics matching the WI-4974 comparator in `scripts/bridge_review_independence.py` and the exact `<slug>-NNN.md` indexer in `scripts/bridge_verified_backlog_reconciler.py`, then wire dispatcher runtime and dispatch-config reconciliation through that exact helper.

The shared helper must ignore both prefix-sibling files such as `<slug>-child-001.md` and draft/noncanonical files such as `<slug>-004-draft.md` or `<slug>-004-draft-body.md`.

### F3 - Verification plan used generic filler

Resolved. The revised verification plan maps concrete tests to the governing specs and acceptance criteria, including targeted dispatcher runtime tests, daemon live-spawn tests, exact bridge-file helper tests, and Ollama harness loop tests.

### F4 - Some spec links appeared spurious or auto-attached

Resolved by curation rather than silent deletion. Each retained specification link now carries a concrete relevance statement. `SPEC-AUQ-POLICY-ENGINE-001` is retained only because WI-4977 depends on owner authorization evidence captured from the owner directive; the implementation itself will not change AUQ behavior.

### F5 - Ollama success-after-verdict premise contradicted observed behavior

Resolved. This revision changes Fix-3 from "success after any verdict-shaped write" to "success only after canonical thread advancement." Ollama must not be treated as successful merely for creating `bridge/*-draft*.md` files or any status-token-bearing noncanonical draft. Success requires the selected thread to advance to a canonical exact versioned bridge file visible through the same exact `<slug>-NNN.md` lookup used by `gt bridge show`. For VERIFIED finalization, success also requires the atomic finalization/commit helper path to complete; otherwise the Ollama worker remains failed/retryable and must not silently clear the dispatch.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs role-correct bridge status authorship and protects implementation from starting before LO GO plus implementation authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite and test against the relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the later implementation report to map these fixes to executed tests before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - governs the PAUTH/project/WI/target-path metadata retained above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governs preserving the owner-discovered bridge stability defect as WI-4977 and routing the fix through bridge review.
- `SPEC-AUQ-POLICY-ENGINE-001` - relevant only to the captured owner authorization evidence used to create and authorize WI-4977; no AUQ engine behavior is in implementation scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps dispatcher and harness infrastructure changes in GT-KB platform paths rather than adopter application paths.
- `GOV-STANDING-BACKLOG-001` - governs retaining the defect as standing operational backlog work until verified stable.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because the fix must preserve cross-harness dispatch parity and Codex PB dispatch fallback behavior while B/D LO dispatch is restored.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governs preserving bridge, PAUTH, test, and implementation-report artifacts for this operational defect.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs treating the observed dispatch storm and model-routing evidence as formal artifact triggers, not scratchpad-only notes.

## Prior Deliberations

- _No prior deliberations: Loyal Opposition semantic search found no directly on-point Deliberation Archive record; directly relevant bridge lineage is cited here instead._
- `WI-4974` / commit `fdad4c49` - exact-slug comparator fix for the same prefix-superset bug class in `scripts/bridge_review_independence.py`; the WI-4977 dispatcher fix must reuse this lineage instead of inventing an incompatible matcher.
- `scripts/bridge_verified_backlog_reconciler.py` - existing exact-versioned bridge-file indexer groups only files named exactly `<slug>-NNN.md` and explicitly excludes child/prefix sibling files. WI-4977 should share that semantic rule for dispatcher latest-status reconciliation.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4974-4976-FINALIZATION-TOOLING-20260702` - adjacent finalization-tooling authorization whose reviewer noted B should remain ineligible until the hung-worker root cause is fixed. WI-4977 is the bounded root-cause repair needed before B/D are safely re-enabled.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4977-STABILITY` - active project authorization covering `WI-4977`.
- `.gtkb-state/owner-evidence/wi-4977-bridge-stability-auq.md` - owner directive evidence: enable the bridge and keep testing/fixing until stable with Claude Code and Ollama as active LO targets and Codex as active PB; Ollama must use `deepseek-v4-pro:cloud`.

## Revised Proposed Scope

- Add global LO in-flight suppression for live dispatcher/daemon dispatch so one bridge document cannot be concurrently assigned to multiple active LO recipients. Use a lease or equivalent global document claim that is acquired at live spawn time and released/reconciled when the worker exits or the canonical thread advances.
- Replace prefix-loose latest-status reconciliation in dispatcher runtime and dispatcher-config health with exact versioned bridge-file lookup semantics shared with the WI-4974 / exact-index lineage. Only files named exactly `<slug>-NNN.md` may define the selected thread's latest status.
- Update Ollama harness completion handling so a nonzero or timeout-late turn is reconciled as successful only when the selected bridge thread has advanced to a canonical exact versioned LO status. Draft files, noncanonical files, and status-token-bearing `bridge/*-draft*.md` artifacts must not count as success and should be prevented or staged outside `bridge/`.
- Preserve the existing model-pinning direction: Claude Code B headless sessions use `claude-opus-4-8` with `--effort max`; Ollama D uses the `deepseek-v4-pro-cloud` route resolving to `deepseek-v4-pro:cloud`; Codex A uses `gpt-5.5` with extra-high/xhigh reasoning.

## Out Of Scope

- No credential changes.
- No production deployment.
- No retired OS poller or retired smart-poller restoration.
- No durable role reassignment beyond the existing A Prime Builder and B/D Loyal Opposition topology.
- No "success" classification for Ollama draft-only output or failed VERIFIED finalization commits.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `platform_tests/scripts/test_dispatcher_runtime.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` assert LO dispatch uses role-correct queue entries, suppresses duplicate in-flight LO documents, and does not let Prime Builder author LO verdicts. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate and live bridge applicability preflights must pass for this REVISED proposal, proving required proposal metadata/spec linkage remains present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The later implementation report must cite the targeted dispatcher, daemon, exact-helper, and Ollama tests with observed pass results before asking for VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate and live preflights verify `Project Authorization`, `Project`, `Work Item`, and `target_paths` metadata in this proposal. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `WI-4977`, this REVISED proposal, and the implementation report preserve the owner-discovered dispatch defect and remediation evidence as governed artifacts. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Verify the implementation report cites the owner evidence file and does not introduce AUQ behavior changes; no AUQ runtime test is required because AUQ engine behavior is out of implementation scope. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --name-only` and test target paths must show changes only in GT-KB platform paths, not adopter application paths. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4977 --json` remains the authoritative work item until bridge VERIFIED finalization closes it through governed flow. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Dispatcher status/health evidence after implementation must show Codex A remains the PB dispatch target while B/D LO dispatch can be restored without breaking cross-harness routing. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report must attach command evidence, bridge state evidence, and rollback notes as durable artifacts rather than relying on chat-only claims. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Regression tests must cover the incident-triggered artifacts: duplicate LO in-flight work, exact thread lookup, and Ollama draft-only failure handling. |

## Acceptance Criteria

- With B and D both eligible, a live daemon tick must not dispatch the same LO bridge thread to multiple LO recipients while one worker remains active.
- Latest-status reconciliation must only consider files named exactly `<bridge-id>-NNN.md` for the selected slug; prefix siblings and `-draft` files must not affect terminal-state reconciliation.
- Ollama headless bridge review using `deepseek-v4-pro:cloud` must not return provider failure after the selected bridge thread advances to a canonical exact versioned LO status, but it must remain failed/retryable when it only leaves draft/noncanonical output.
- VERIFIED finalization through Ollama is successful only when the atomic finalization helper commits the canonical VERIFIED file and verified path set; otherwise dispatch health reports the failure visibly.
- After the fix and governed re-enable, dispatcher status/health must show Codex A selected for PB and Claude B plus Ollama D selected for LO, with daemon/supervisor active and no worker storm during a bounded soak.

## Expected Tests

- `platform_tests/scripts/test_bridge_thread_files.py::test_exact_thread_files_ignore_prefix_siblings_and_drafts`
- `platform_tests/scripts/test_dispatcher_runtime.py::test_latest_bridge_status_ignores_draft_and_prefix_sibling_files`
- `platform_tests/scripts/test_dispatcher_runtime.py::test_lo_live_spawn_acquires_document_lease_or_suppresses_duplicate`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets`
- `platform_tests/scripts/test_ollama_harness.py::test_tool_loop_reconciles_success_only_after_canonical_bridge_advancement`
- Existing baseline checks around lease diagnostics, daemon decision splitting, and Ollama session timeout behavior must continue to pass.

## Pre-Filing Preflight Subsection

This completed revision will be filed only after candidate-content applicability and ADR/DCL clause preflights pass through `.codex/skills/bridge/helpers/revise_bridge.py file`. Manual candidate preflight evidence is captured in the filing transcript before live write.

## Risks / Rollback

Risk is moderate because the implementation touches dispatcher runtime, daemon live-spawn behavior, and harness completion classification. The highest risk is masking stuck LO work as success; this revision explicitly prevents that by requiring canonical exact thread advancement.

Rollback is a revert of source/test changes and a governed dispatcher config transaction that disables B/D if soak testing shows renewed instability. Bridge files and PAUTH records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/ollama_harness.py`
- `scripts/bridge_thread_files.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_bridge_thread_files.py`

## Recommended Commit Type

`fix`
