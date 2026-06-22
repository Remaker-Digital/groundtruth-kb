NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eed3f-0ee1-7dc1-aa36-4241c0a96b37
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex autonomous Prime Builder; approval_policy=never; workspace=E:/GT-KB

# GT-KB Bridge Implementation Report - gtkb-gt-backlog-add-changed-by-active-harness - 005

bridge_kind: implementation_report
Document: gtkb-gt-backlog-add-changed-by-active-harness
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-gt-backlog-add-changed-by-active-harness-004.md
Approved proposal: bridge/gtkb-gt-backlog-add-changed-by-active-harness-003.md
Recommended commit type: fix

## Implementation Claim

Implemented the approved combined `changed_by` harness-name precedence contract for WI-4632 and the paired WI-4367 thread in commit `f9846726f` (`fix(attribution): resolve active harness changed_by sources`).

The resolver order is now:

1. explicit `harness_name`;
2. `GTKB_HARNESS_NAME`;
3. one unambiguous open `harness-state/*/session-envelope.json`, skipped under `GTKB_BRIDGE_POLLER_RUN_ID`;
4. deterministic Claude/Codex vendor runtime environment signals;
5. the existing single active Prime Builder fallback.

Envelope and vendor runtime signals are only candidate harness-name selectors. `resolve_changed_by()` still validates the selected name through the harness identity and role source-of-truth path before returning attribution, preserving fail-closed behavior for unknown or roleless candidates.

The same code diff satisfies the paired `gtkb-gt-backlog-add-attribution-resolution` GO. Duplicate backlog item `WI-4625` is covered by the same defect-class fix, but no MemBase backlog mutation was performed in this implementation; any work-item disposition remains a separate governed backlog update.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this defect fix through `PROJECT-GTKB-RELIABILITY-FIXES`.
- `DELIB-20265457` authorized the reliability-fixes proposal batch that included WI-4632 and WI-4367.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` provides the durable fast-lane rationale.

No new owner decision was required. This implementation adds no public CLI surface, no destructive action, no deployment, and no formal artifact mutation.

## Prior Deliberations

- `DELIB-20265457` - owner AUQ authorizing the reliability-fixes proposal batch.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane direction.
- `DELIB-S333-CODEX-PRIME-PERIOD-KB-ATTRIBUTION-DEFECT` - prior cross-harness MemBase attribution defect.
- `DELIB-20263700` - backlog add attribution belongs in the resolver path.
- `DELIB-20263483` - related author identity environment alias defect.
- `bridge/gtkb-gt-backlog-add-changed-by-active-harness-003.md` - approved revised implementation proposal.
- `bridge/gtkb-gt-backlog-add-changed-by-active-harness-004.md` - Loyal Opposition GO verdict.
- `bridge/gtkb-gt-backlog-add-attribution-resolution-003.md` and `-004.md` - paired approved vendor-runtime limb.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | `test_attribution_uses_open_envelope_harness_over_durable_prime`, `test_attribution_open_envelope_precedes_vendor_signal`, `test_runtime_env_detects_codex_over_prime_fallback`, `test_runtime_env_detects_claude`, and existing explicit/env/fallback tests prove attribution follows the acting harness source before durable fallback. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | `test_runtime_env_unknown_harness_still_fails_closed` proves vendor candidates still validate through harness identity; envelope tests keep candidates local to harness-state session envelopes. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation is preserved in commit `f9846726f`, this report, the paired report, and focused regression tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Vendor-runtime detection covers Codex subprocesses where hook-set `GTKB_HARNESS_NAME` is absent; explicit env still has precedence when present. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files are all in-root GT-KB platform source/test paths; no adopter/application files changed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest and both ruff gates were executed and passed; command evidence is listed below. |
| `GOV-STANDING-BACKLOG-001` | Report discloses duplicate backlog item `WI-4625` as covered debt without mutating backlog state outside the approved source/test scope. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py -q --tb=short`
- `python -m ruff check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`
- `python -m ruff format --check scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`
- `git commit -m "fix(attribution): resolve active harness changed_by sources" --only -- scripts/_kb_attribution.py platform_tests/scripts/test_kb_attribution.py platform_tests/scripts/test_kb_attribution_session_role.py`

## Observed Results

- Pytest: `43 passed in 9.47s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `3 files already formatted`.
- Commit: `f9846726f` created with only:
  - `scripts/_kb_attribution.py`
  - `platform_tests/scripts/test_kb_attribution.py`
  - `platform_tests/scripts/test_kb_attribution_session_role.py`

## Files Changed

- `scripts/_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution.py`
- `platform_tests/scripts/test_kb_attribution_session_role.py`

Ambient unrelated worktree/index drift existed before this implementation and remains outside this report's scope. The implementation commit was split so it contains only the three approved paths.

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: this removes a mis-attribution defect in `changed_by` provenance and adds regression tests; it introduces no new public capability or CLI surface.

## Acceptance Criteria Status

- [x] Final resolver order is exactly explicit argument, `GTKB_HARNESS_NAME`, single open envelope, vendor-runtime detection, durable single-Prime fallback.
- [x] WI-4367 Codex runtime reproduction resolves to Codex before the durable Prime fallback.
- [x] WI-4632 single open Claude envelope reproduction resolves to Claude before the durable Prime fallback.
- [x] Candidate names from envelope/vendor detection still validate through harness-state and fail closed when unknown.
- [x] Headless dispatch skips the envelope source.
- [x] Focused pytest and ruff commands pass.

## Risk And Rollback

Residual risk is limited to stale environment variables or stale open session envelopes. The implemented precedence mitigates that by preferring explicit/env sources, requiring exactly one open envelope, skipping envelopes under headless dispatch, and preserving final identity/role validation. Rollback is to revert commit `f9846726f`; no schema, database, or formal artifact migration was performed.

## Loyal Opposition Asks

1. Verify the implementation against both paired GO threads and the executed command evidence.
2. Confirm `WI-4625` is adequately disclosed as duplicate/covered debt without requiring this source/test implementation to mutate backlog state.
3. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
