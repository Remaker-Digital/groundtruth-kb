NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-gtkb-pb-2026-06-02
author_model: GPT-5 Codex
author_model_version: 2026-06-02
author_model_configuration: reasoning=high

# GT-KB Bridge Implementation Report - Inventory Drift GH Probe Parity

bridge_kind: implementation_report
Document: gtkb-inventory-drift-gh-probe-parity
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-inventory-drift-gh-probe-parity-002.md
Approved proposal: bridge/gtkb-inventory-drift-gh-probe-parity-001.md
Project Authorization: PAUTH-WI-4218-INVENTORY-DRIFT-GH-PROBE-MISMATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4218
Recommended commit type: feat:

## Implementation Claim

WI-4218 is implemented for the inventory writer/checker GH probe parity surface. The collector now records the stable public probe command as evidence for `gh --version` whether the command succeeds, returns nonzero, cannot execute, or is unavailable. Outcome-specific strings such as "not found on PATH" and "could not be executed" no longer enter the protected public inventory, preventing writer/checker evidence mismatches that cannot be reconciled by normal baseline regeneration.

The drift-checker path already consumed collector-generated public inventory through `generate_current_public_inventory(...)`; no checker source change was needed. Regression tests now pin that parity and prove that evidence itself remains a material field when it changes.

## Specification Links

- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-SEC-HOOK-PORTABILITY-001`
- `SPEC-DSI-COMMIT-GATE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Owner Decisions / Input

No new owner decision is required. The implementation follows the approved proposal, PAUTH-WI-4218-INVENTORY-DRIFT-GH-PROBE-MISMATCH, and the owner directive to continue until the listed work items are completed.

## Prior Deliberations

- `bridge/gtkb-inventory-drift-gh-probe-parity-001.md` - approved implementation proposal.
- `bridge/gtkb-inventory-drift-gh-probe-parity-002.md` - Loyal Opposition GO verdict.
- `DELIB-2813` - owner directive and active project authorization context cited by the proposal.

## Implementation-Start Authorization

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-inventory-drift-toolchain-flux-stability` created sibling packet `sha256:82d6f4371e905030c508aab2a0488978a34bd5bafc5b0cdb419a4032a1b55efb` at `2026-06-02T05:57:21Z`; expires `2026-06-02T13:57:21Z`.
- `python scripts\implementation_authorization.py begin --bridge-id gtkb-inventory-drift-gh-probe-parity` created packet `sha256:6e104cd1a5df2225ac6bf2ea3c889f3c8ca5f73c70a1f0cb74dfab52900845b9` at `2026-06-02T06:04:59Z`; expires `2026-06-02T14:04:59Z`.
- Both packets carry the same six authorized target paths for the shared implementation scope.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `.claude/rules/file-bridge-protocol.md` | Implementation report filed after live `GO`; `bridge/INDEX.md` now lists `NEW: bridge/gtkb-inventory-drift-gh-probe-parity-003.md` at the top of this thread's entry, with prior versions preserved below. |
| `.claude/rules/codex-review-gate.md` | Targeted pytest plus Ruff check and Ruff format-check passed on all scoped source/test files. |
| `.claude/rules/project-root-boundary.md` | All changed files are under `E:\GT-KB` and within the approved target paths for this proposal. |
| `.claude/rules/operating-model.md` | Proposal, GO, implementation report, verification, and backlog resolution remain distinct lifecycle steps. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge state for this thread was latest `GO` before filing this report; the `bridge/INDEX.md` entry is canonical and now points to this report as latest `NEW`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex used the bridge implementation-report helper and serialized writer path. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Public inventory was regenerated through the live collector, then checked through the live drift checker. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries Project Authorization, Project, and Work Item metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The approved proposal's linked specifications are carried forward here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps each linked governing surface to executed command evidence. |
| `GOV-STANDING-BACKLOG-001` | `WI-4218` backlog resolution is deferred until Loyal Opposition verifies this report. |
| `SPEC-SEC-HOOK-PORTABILITY-001` | Collector regression tests prove public output avoids absolute-path diagnostic evidence and keeps private diagnostics local. |
| `SPEC-DSI-COMMIT-GATE-001` | Drift regression tests prove GH probe success/failure wording no longer creates non-reconcilable material drift. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The source/test evidence, regenerated public inventory, and bridge report are durable artifacts. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Work remains in GO -> implementation report NEW -> Loyal Opposition verification lifecycle. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Completion evidence is preserved in this report rather than only in chat. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_collect_dev_environment_inventory.py platform_tests\scripts\test_check_dev_environment_inventory_drift.py -q --tb=short`
- `python -m ruff check scripts\collect_dev_environment_inventory.py scripts\check_dev_environment_inventory_drift.py platform_tests\scripts\test_collect_dev_environment_inventory.py platform_tests\scripts\test_check_dev_environment_inventory_drift.py`
- `python -m ruff format --check scripts\collect_dev_environment_inventory.py scripts\check_dev_environment_inventory_drift.py platform_tests\scripts\test_collect_dev_environment_inventory.py platform_tests\scripts\test_check_dev_environment_inventory_drift.py`
- `python scripts\collect_dev_environment_inventory.py`
- `python scripts\check_dev_environment_inventory_drift.py --changed-path .groundtruth/inventory/dev-environment-inventory.json --json`

## Observed Results

- Pytest: first attempt with plugin autoload disabled failed before collection because repo config passes `--timeout=30`; repo-native rerun passed with `23 passed, 1 warning in 0.54s`.
- Ruff check: `All checks passed!`.
- Ruff format check: `4 files already formatted`.
- Collector: wrote public JSON, public Markdown, and local JSON; redaction status `pass`.
- Drift checker JSON: `status: "pass"`, `outcome: "accepted_baseline_update"`, `material_inventory_drift: false`, `diff_keys: []`, `blocking: []`.

## Files Changed

- `scripts/collect_dev_environment_inventory.py`
- `platform_tests/scripts/test_collect_dev_environment_inventory.py`
- `platform_tests/scripts/test_check_dev_environment_inventory_drift.py`
- `.groundtruth/inventory/dev-environment-inventory.json`
- `.groundtruth/inventory/dev-environment-inventory.md`

## Acceptance Criteria Status

- [x] GH public probe evidence is deterministic across success, failure, execution-error, and missing-executable collector paths.
- [x] Writer/checker parity is preserved because the checker uses the same collector-generated public inventory surface.
- [x] Toolchain version/status/classification volatility remains bounded to those fields.
- [x] Public evidence remains material and still gates if the probe identity changes.
- [x] The public inventory baseline was regenerated through the collector and accepted by the drift checker.
- [x] Targeted pytest, Ruff check, and format-check passed.

## Risk And Rollback

Residual risk is low and limited to public inventory display wording for missing or failed tools. Rollback restores the collector evidence strings, the added tests, and the regenerated public inventory files; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that GH writer/checker probe evidence parity is now stable.
2. Verify that evidence remains a material field when the probe identity changes.
3. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.
