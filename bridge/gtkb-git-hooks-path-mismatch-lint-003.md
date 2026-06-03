NEW

# Implementation Report — git-hooks-path-mismatch Bridge Lint (WI-3482)

bridge_kind: implementation_report
Document: gtkb-git-hooks-path-mismatch-lint
Version: 003
Responds to: bridge/gtkb-git-hooks-path-mismatch-lint-002.md (GO)
Author: Prime Builder (Claude, harness B; durable PB per harness-registry.json; session-stated PB via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: feat

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder]); /loop dynamic-mode iteration 7

Implements: WI-3482
Project Authorization: PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3482
target_paths: ["scripts/bridge_proposal_pattern_lint.py", "platform_tests/scripts/test_bridge_proposal_pattern_lint.py"]

## Summary

The GO `-002` (Codex, 2026-06-01) authorized WI-3482: extend `scripts/bridge_proposal_pattern_lint.py` with a `git-hooks-path-mismatch` detector that flags a bridge proposal targeting an inactive Git-hook surface (`.git/hooks` or the legacy `scripts/guardrails/pre-commit` staging path) while `core.hooksPath` differs. This report records the completed implementation, the executed tests, and the code-quality gates.

Both changes are within the two GO-approved target paths. The lint's diagnostic-by-default contract is preserved: no new CLI flag, no bridge-compliance hard gate, non-zero exit only through the existing `--strict`. The new detector adds one `Finding` `pattern_id`.

**Bridge-INDEX recovery note:** this is the third stranded GO from session `86d7f8a9` (2026-06-01) recovered this session — it had been pruned from the ~1471-line `bridge/INDEX.md` before implementation. This session re-promoted the entry (`GO: -002`, `NEW: -001`) before minting the implementation-start packet, then prepended this report's `NEW: -003` line. Append-only preserved. (The systemic pruning defect is captured as `WI-4283`.)

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-git-hooks-path-mismatch-lint
```

Observed: `latest_status: GO`; `packet_hash: sha256:1eb446cf33e774c869686b0f9cd2a9d9332eccc99cc652eb278411cf7d7c72bf`; PAUTH `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` active, `work_item_id: WI-3482`, `requirement_sufficiency: sufficient`.

## IP-1 — `git-hooks-path-mismatch` detector (landed in bridge_proposal_pattern_lint.py)

- **`_resolve_active_hooks_path(project_root)`** — reads `git config --get core.hooksPath` (`cwd=project_root`, captured, no shell), normalizes (strip + forward-slash). A missing/empty/failed read degrades to `""` (the Git default `.git/hooks`), guarded by `try/except`, so a default-configured clone never trips the detector and `git` absence is a no-op, not a crash.
- **`_normalize_path_separators(value)`** — folds Windows backslashes to forward-slash so `.git\hooks\pre-commit` matches (GO -002 separator-normalization condition).
- **`_line_targets_inactive_hook_surface(line)`** — true when a line references an inactive token (`.git/hooks/` or `scripts/guardrails/pre-commit`, after separator folding) AND is not a hazard-description line (see the self-documentation guard below).
- **`lint_text(text, *, active_hooks_path=_RESOLVE_HOOKS_PATH)`** — gains a keyword-only `active_hooks_path`. The `_RESOLVE_HOOKS_PATH` sentinel triggers a live `git config` read; tests inject an explicit string (including `""` for the Git default) to stay hermetic. The detector fires per line only when the active hook path is non-default AND the line targets an inactive surface, emitting `Finding(pattern_id="git-hooks-path-mismatch", ...)` whose message and hint name the live `core.hooksPath` value and direct the author to the active surface. Existing detectors (`bare-pytest`, `codex-verified-pending`, `powershell-inline-python-escaping`, `owner-action-required`) and the existing `--strict`/`main()` exit semantics are unchanged.

### Self-documentation guard (verification-hardened)

The proposal's IP-1 step 4 required the detector to not self-trigger on a proposal *describing* the hazard. Rather than extend the shared `RULE_DOCUMENTATION_RE` (which other detectors depend on), the implementation adds a dedicated `HOOKS_HAZARD_DOCUMENTATION_RE`. A high-value regression test (`test_self_documentation_holds_on_real_wi3482_proposal`) runs the detector against the **actual** `-001` proposal — the densest real instance of hazard-describing prose — and asserts zero `git-hooks-path-mismatch` findings. That test drove three guard iterations to convergence: the live `-001` text exercised description phrasings the synthetic negative test alone did not (`active path`, `produces a finding`, `the detector fires/misses`, `token scan`). Final state: the `-001` proposal yields **0** `git-hooks-path-mismatch` findings while genuine target declarations still fire. A real target_paths line never contains those meta-description markers, so the guard does not suppress true positives (verified by the four positive tests).

## IP-2 — Regression Tests (`platform_tests/scripts/test_bridge_proposal_pattern_lint.py`, new)

12 tests (imports the module via the `platform_tests/scripts/conftest.py` REPO_ROOT-on-`sys.path` convention; hermetic — `active_hooks_path` injected, or the resolver monkeypatched for the `main()`/`--strict` path):

- **Positive:** target_paths `.git/hooks/pre-commit` (reproduces `gtkb-ruff-format-pre-file-gate-002` F1); register-at `.git/hooks/pre-commit` (reproduces `gtkb-commit-scope-bundling-detection-001-prop-002` F1); legacy `scripts/guardrails/pre-commit` token; **backslash path** `.git\hooks\pre-commit` (separator normalization).
- **Negative:** default hook path (`""` and explicit `.git/hooks`) → no finding; correct `.githooks/pre-commit` surface → no finding; synthetic self-documentation prose → no finding; **the real `-001` proposal** → no finding.
- **Contract:** `--strict` exit-code (positive case → `main()` returns 1; without `--strict` → 0).
- **Helper units:** `_normalize_path_separators` folds backslashes; `_line_targets_inactive_hook_surface` fires on a target line and excludes a hazard-doc line.

## Specification Links

Carried forward from `-001`; all governing specifications cited concretely.

- `WI-3482` — the originating defect (`origin=defect`, `component=governance`): recurring Prime hazard of targeting `.git/hooks` while `core.hooksPath=.githooks`, cost ≥2 prior Codex NO-GO rounds.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-quality infrastructure; `bridge/INDEX.md` canonical workflow state, unchanged.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — governs the `target_paths` metadata surface the detector inspects.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths are in-root under `E:\GT-KB`; the lint writes no out-of-root path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification is cited in this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications and executed (spec-to-test mapping below); the regression reproduces both prior NO-GO cases.
- `GOV-RELIABILITY-FAST-LANE-001` — cited for the honest non-eligibility assessment; this work is NOT fast-lane (it adds a new detector = new behavior), so it used the dedicated `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` rather than the standing fast-lane PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable preservation of the proposal/report chain.

## Prior Deliberations

Carried forward from `-001`:

- `DELIB-2548` (S381 owner decision) — authorizes WI-3482 through normal bridge review; operationalized as `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001`.
- `bridge/gtkb-ruff-format-pre-file-gate-002.md` (Codex NO-GO F1) — first recorded NO-GO on the inactive `.git/hooks/pre-commit` surface; regression case 1.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` (Codex NO-GO F1) — second NO-GO on the same hazard; regression case 2.

## Owner Decisions / Input

No owner decision required before VERIFIED. The dedicated `PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001` (owner decision `DELIB-2548`, S381) authorizes the bounded scope with allowed mutation classes `["source", "test_addition", "cli_extension"]`; this implementation exercises `source` (the detector) and `test_addition` (the regression file) — `cli_extension` is reserved but **not** exercised (no new CLI flag). Per the GO `-002` condition, `forbidden_operations` on the live PAUTH row is `NULL`; deploy, force-push, and spec-deletion remain outside this proposal by scope and by normal governance gates, not by a populated PAUTH field. No formal-artifact-approval packet is required (no GOV/SPEC/PB/ADR/DCL artifact created, no protected narrative file touched).

## Spec-To-Test Mapping

Executed spec-derived verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec / governing surface | Verification | Test | Observed |
|---|---|---|---|
| DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | target_paths listing `.git/hooks/pre-commit` while `core.hooksPath=.githooks` fires (both prior NO-GO cases) | `test_positive_target_paths_...`, `test_positive_register_at_...` | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 | fires on legacy `scripts/guardrails/pre-commit`; no false positive on default path or correct `.githooks/pre-commit` | `test_positive_legacy_...`, `test_negative_default_hook_path_*`, `test_negative_correct_active_surface_...` | PASS |
| GOV-FILE-BRIDGE-AUTHORITY-001 (separator normalization, GO -002 cond.) | backslash path `.git\hooks\pre-commit` matches | `test_positive_backslash_path_separator_is_normalized`, `test_normalize_path_separators_folds_backslashes` | PASS |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (self-documentation) | hazard-describing prose, incl. the real `-001` proposal, does not self-trigger | `test_negative_self_documentation_...`, `test_self_documentation_holds_on_real_wi3482_proposal`, `test_line_targets_inactive_surface_excludes_hazard_docs` | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (diagnostic-by-default) | findings exit 0 unless `--strict`; non-zero only via `--strict` | `test_strict_exit_code_contract` | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | both target paths in-root; lint writes no out-of-root path | applicability + clause preflight | PASS |

## Executed Verification Commands + Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_proposal_pattern_lint.py -q --tb=short -p no:cacheprovider
# 12 passed in 0.14s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_proposal_pattern_lint.py platform_tests/scripts/test_bridge_proposal_pattern_lint.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_proposal_pattern_lint.py platform_tests/scripts/test_bridge_proposal_pattern_lint.py
# 2 files already formatted

# Live CLI smoke (resolves core.hooksPath=.githooks live; diagnostic-by-default):
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_proposal_pattern_lint.py --file bridge/gtkb-git-hooks-path-mismatch-lint-001.md
#   Findings: 0   (exit 0 — self-documentation holds on the real proposal)

# Regression sanity: existing bare-pytest detector still fires (no regression).
```

Both code-quality gates (lint AND format) were run separately per `.claude/rules/file-bridge-protocol.md` § Pre-File Code-Quality Gates.

## Diagnostic-by-Default Contract (GO -002 condition)

Preserved. No new CLI flag is added (`build_arg_parser` unchanged); `main()` returns `1 if args.strict and findings else 0` (unchanged). The new detector only appends to the findings list. The `--strict` contract is asserted by `test_strict_exit_code_contract` and confirmed by the live CLI smoke (Findings: 0, exit 0 without `--strict`).

## Acceptance Criteria Status

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] Detector fires on `.git/hooks/`/`scripts/guardrails/pre-commit` references when live `core.hooksPath` differs — tests reproduce both prior NO-GO cases.
- [x] No false positive on default hook path, correct `.githooks` surface, or rule-documentation lines — negative tests incl. the real `-001` proposal.
- [x] Diagnostic-by-default preserved: findings exit 0 unless `--strict` — test covered.
- [x] Tests hermetic — `core.hooksPath` injected/overridden; no real git config mutation.
- [x] `ruff check` and `ruff format --check` pass on both files.
- [x] Separator-normalization shown via a positive backslash-path case.
- [x] This report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED (pending this report's review).

## Files Changed

- `scripts/bridge_proposal_pattern_lint.py` — `+subprocess` import; `_GIT_DEFAULT_HOOKS_PATH`/`INACTIVE_HOOK_TOKENS`/`_RESOLVE_HOOKS_PATH`/`HOOKS_HAZARD_DOCUMENTATION_RE` constants; `_normalize_path_separators`, `_resolve_active_hooks_path`, `_line_targets_inactive_hook_surface` helpers; `lint_text` gains keyword-only `active_hooks_path` and the new detector.
- `platform_tests/scripts/test_bridge_proposal_pattern_lint.py` (new) — 12 regression tests.
- `bridge/INDEX.md` — re-promoted the pruned thread entry; prepended `NEW: -003`.

## Bridge INDEX Update Evidence

The `gtkb-git-hooks-path-mismatch-lint` entry was re-promoted to the top of `bridge/INDEX.md` with its true prior state (`GO: -002`, `NEW: -001`), then `NEW: bridge/gtkb-git-hooks-path-mismatch-lint-003.md` prepended. Append-only preserved; `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`feat:` — adds a new detector (new `pattern_id`, new `core.hooksPath` read, new behavior) to the bridge-proposal lint, plus its regression tests. Per the proposal's own `Recommended commit type: feat:`.

## Next Steps for Loyal Opposition

Verify this report against GO `-002`. Re-run the applicability + clause preflights against `-003`, the lint test file, and both ruff gates. Note the separator-normalization backslash case (GO condition met), the diagnostic-by-default preservation, that `forbidden_operations` is NOT claimed as a populated PAUTH field, and the verification-hardened self-documentation guard validated against the real `-001` proposal.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
