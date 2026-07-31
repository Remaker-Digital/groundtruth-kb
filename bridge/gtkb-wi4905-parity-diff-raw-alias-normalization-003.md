NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop Prime Builder interactive session; hooks restored with no-window containment; approval_policy=never; cwd=E:\GT-KB

# GT-KB Bridge Implementation Report - gtkb-wi4905-parity-diff-raw-alias-normalization - 003

bridge_kind: implementation_report
Document: gtkb-wi4905-parity-diff-raw-alias-normalization
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-002.md
Approved proposal: bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-001.md
Recommended commit type: feat:

## Implementation Claim

Fixed a parity discovery false positive introduced by restoring Codex hook parity. Registered fallback hook surfaces now satisfy their same-stem raw aliases when another harness exposes the same stem as registered, while genuinely unregistered raw asymmetries remain visible.

The scanner now tracks raw stem presence separately from capability-upgraded presence. It only reintroduces raw `hook:<stem>` keys when at least one in-population harness exposes that stem as unregistered. This preserves the unregistered-surface safety net without reporting false missing-Codex findings for registered fallback equivalents such as `credential-scan`, `session_start_dispatch`, and `spec-classifier`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented change control.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal-to-spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item/target metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner authorization policy.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/adopter boundary.
- `GOV-STANDING-BACKLOG-001` - standing backlog governance.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity fallback.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle triggers.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - cross-harness parity enforcement.
- `ADR-CROSS-HARNESS-PARITY-001` - harness parity architecture.

## Owner Decisions / Input

No new owner decision is required by this implementation report. This work is under `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` and the GO verdict at `bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-002.md`.

## Prior Deliberations

- `bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4905-parity-diff-raw-alias-normalization-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `SPEC-AUQ-POLICY-ENGINE-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4905-parity-diff-raw-alias-normalization` succeeded before protected edits; report filed as next numbered bridge document. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`; `ADR-CROSS-HARNESS-PARITY-001` | Added `test_registered_same_stem_fallback_satisfies_unregistered_raw_alias`; `python scripts\parity_discovery_diff.py --json` returned PASS / no findings against live config. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Focused pytest, ruff check, ruff format-check, live parity-diff, and doctor checks were run. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-STANDING-BACKLOG-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Changes are limited to the platform parity scanner and its focused test file under `E:\GT-KB`. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_hook_registration_parity.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_fab09_safety_gate_registration.py platform_tests\hooks\test_auto_finalize_verified_verdicts.py -q --tb=short`
- `python -m ruff check scripts\parity_discovery_diff.py platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_hook_registration_parity.py`
- `python -m ruff format --check scripts\parity_discovery_diff.py platform_tests\scripts\test_parity_discovery_diff.py platform_tests\scripts\test_codex_hook_runtime_containment.py platform_tests\scripts\test_codex_hook_parity.py platform_tests\scripts\test_cross_harness_protocol_parity.py platform_tests\scripts\test_hook_registration_parity.py`
- `python scripts\parity_discovery_diff.py --json`
- `gt project doctor --json`

## Observed Results

- Focused pytest bundle: `72 passed`.
- Ruff check: `All checks passed`.
- Ruff format-check: `6 files already formatted`.
- `python scripts\parity_discovery_diff.py --json`: PASS with empty findings.
- `gt project doctor --json`: exit code 0, overall `warning`; the cross-harness parity discovery-diff check passes.

## Files Changed

- `scripts/parity_discovery_diff.py`
- `platform_tests/scripts/test_parity_discovery_diff.py`

## Acceptance Criteria Status

- PASS: Registered same-stem fallback hooks no longer produce raw alias false positives.
- PASS: Unregistered raw asymmetry detection is preserved for stems that at least one population member exposes as unregistered.
- PASS: Live parity discovery reports no findings after the Codex hook registry restoration.
- PASS: Focused parity-diff tests pass.

## Residual Release Blocker Outside This Slice

This scanner correction proves static parity shape, not live dispatch execution. Separate runtime dispatch defects remain from verification: Ollama/D hung with empty logs, OpenRouter/F timed out before a Bash tool call, and Cursor/E timed out waiting for Cursor Agent. Those require dispatcher runtime hardening and are not solved by scanner alias normalization.

## Risk And Rollback

Risk is low to moderate. The new logic intentionally keeps raw stem accounting, but narrows raw parity keys to stems with at least one unregistered occurrence so registered fallback equivalents do not create false drift.

Rollback is to restore the previous `compute_diff` key-building logic and remove the focused regression test. Bridge files are append-only and should not be deleted.

## Loyal Opposition Asks

1. Verify the alias-normalization behavior against the focused regression and live parity-diff output.
2. Return VERIFIED if the implementation satisfies the approved proposal; otherwise return NO-GO with concrete findings.
