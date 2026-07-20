NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: GPT-5 Codex desktop runtime 2026-07-02
author_model_configuration: Codex desktop; E:/GT-KB; danger-full-access; approval-policy never; interactive role Prime Builder via ::init gtkb pb

# GT-KB Bridge Implementation Report - gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment - 003

bridge_kind: implementation_report
Document: gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-002.md
Approved proposal: bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md
Parent implementation report: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OPS-AUQ-HEADLESS-HOOK-LAUNCH-HYGIENE-IMPLEMENTATION-2026-07-02.md
Project: PROJECT-GTKB-AUQ-HEADLESS-HOOK-HYGIENE
Work item: WI-4959
Recommended commit type: fix

## Implementation Claim

The exact-target amendment is implemented as part of the parent WI-4959 launch-hygiene slice. All 15 approved Codex `.cmd` adapters now launch Python hook targets through:

```text
E:\GT-KB\groundtruth-kb\.venv\Scripts\pythonw.exe E:\GT-KB\.codex\gtkb-hooks\run_py_no_window <hook-target.py> [args]
```

The approved regression target, `platform_tests/scripts/test_codex_hook_runtime_containment.py`, now enumerates the exact amended wrapper set and rejects future bare `python`/`py` command tokens.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required by this amendment implementation report.

## Prior Deliberations

- `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-001.md` - exact-target amendment proposal.
- `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-002.md` - LO `GO` authorizing the target-path amendment.
- `bridge/gtkb-auq-headless-hook-launch-hygiene-002.md` - parent LO `GO`.

## Architecture Alignment Ledger

| Alignment surface | Evidence |
| --- | --- |
| OPS consolidation | Amendment only made the approved launcher mechanics concrete; no new owner workflow or policy branch was added. |
| Dispatcher daemon architecture | No dispatch daemon, worker, bridge-claim, or queue behavior changed. |
| Lifecycle-first / scoring-last precedence | Amendment implementation followed live GO/claim/target gates and introduced no scoring behavior. |
| Portfolio reconciliation findings | The amended targets belong to WI-4959's AUQ/headless hook hygiene child lane; no duplicate project-family cleanup was needed for this slice after WI-4960 reconciliation. |

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| Bridge authority and linkage specs | Live parent and amendment `GO`; valid work-intent claims; valid implementation authorization packets; exact-target preflight `verdict: in_scope`. |
| No-console launch specs | Static scan found no bare console Python tokens in the 15 approved wrappers; focused pytest regression passed. |
| Dispatcher architecture and AUQ policy specs | No dispatcher, AUQ policy, or harness-state source was changed; changed paths are limited to the approved wrapper/test targets. |
| Cross-harness parity specs | Parent report documents focused pass evidence and adjacent pre-existing parity-suite failures. |

## Commands Run

See the parent report for full command detail. Amendment-specific evidence:

- `python scripts\impl_start_target_paths_preflight.py --bridge-id gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment --candidate-paths <15 approved .cmd wrappers> platform_tests/scripts/test_codex_hook_runtime_containment.py --json`
- `rg --pcre2 -n '(?i)(^|[`(\s])(?:python(?:\.exe)?|py(?:\.exe)?)(?=$|[\s\"])' <15 approved .cmd wrappers>`
- `python -m pytest platform_tests\scripts\test_codex_hook_runtime_containment.py -q --tb=short`
- `python -m ruff check platform_tests\scripts\test_codex_hook_runtime_containment.py`
- `python -m ruff format --check platform_tests\scripts\test_codex_hook_runtime_containment.py`

## Observed Results

- Exact-target preflight: all 16 candidates in scope, 0 out of scope.
- Static scan: no matches for bare console Python command tokens in the amended wrappers.
- Focused pytest: `10 passed`.
- Ruff check: all checks passed.
- Ruff format check: 1 file already formatted.

## Files Changed

- `.codex/gtkb-hooks/bridge-compliance-audit.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.cmd`
- `.codex/gtkb-hooks/bridge-compliance-gate.cmd`
- `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd`
- `.codex/gtkb-hooks/codex-mcp-worker-guard.cmd`
- `.codex/gtkb-hooks/credential-scan.cmd`
- `.codex/gtkb-hooks/destructive-gate.cmd`
- `.codex/gtkb-hooks/directive-enforcement.cmd`
- `.codex/gtkb-hooks/formal-artifact-approval.cmd`
- `.codex/gtkb-hooks/implementation-start-gate.cmd`
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`
- `.codex/gtkb-hooks/session-start.cmd`
- `.codex/gtkb-hooks/session-stop.cmd`
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd`
- `.codex/gtkb-hooks/workstream-focus.cmd`
- `platform_tests/scripts/test_codex_hook_runtime_containment.py`

## Recommended Commit Type

- Recommended commit type: `fix`
- Justification: the amendment implements the concrete wrapper target correction for the WI-4959 launch-hygiene bug.

## Acceptance Criteria Status

- [x] Every amended `.cmd` wrapper target was changed.
- [x] Every amended wrapper now routes through no-window launcher mechanics.
- [x] Regression coverage enumerates every amended wrapper.
- [x] No source outside the approved amendment target paths was needed for implementation.

## Risk And Rollback

Risk and rollback are identical to the parent report: revert the amended wrapper launcher lines and the test additions. No AUQ, dispatcher, bridge-runtime, or harness-state rollback is required.

## Loyal Opposition Asks

1. Verify this companion report against the exact-target amendment GO.
2. Use the parent WI-4959 report as the detailed implementation and evidence packet.
