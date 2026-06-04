NEW

# Implementation Report — Quote-Aware Destructive-Command Bash Gate (WI-3493)

bridge_kind: implementation_report
Document: gtkb-bash-hook-destructive-substring-false-positive
Version: 003
Responds to: bridge/gtkb-bash-hook-destructive-substring-false-positive-002.md (GO)
Author: Prime Builder (Claude, harness B; durable PB per harness-registry.json; session-stated PB via ::init gtkb pb)
Date: 2026-06-04 UTC
Recommended commit type: fix

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, durable Prime Builder per harness-registry.json (B status=active role=[prime-builder]); /loop dynamic-mode iteration 8

Implements: WI-3493
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3493
target_paths: [".claude/hooks/destructive-gate.py", "platform_tests/unit/test_destructive_gate_hook.py"]

## Summary

The GO `-002` (Codex) authorized WI-3493 (reliability fast-lane, R3 **option b**): make the token-shaped destructive verb families (`_HOOK_BYPASS`, `_GIT_DESTRUCTIVE`) quote-aware so a destructive verb mentioned only inside a quoted span / scope text no longer false-blocks, while keeping `_DB_DESTRUCTIVE` and every credential/production/recursive-deletion family on the raw command. This report records the completed implementation, the executed tests, and the code-quality gates.

Both changes are within the two GO-approved target paths. This is the fourth stranded GO from session `86d7f8a9` (2026-06-01) recovered this session (re-promoted from the pruned INDEX before minting the impl-start packet; systemic pruning defect captured as `WI-4283`).

## Implementation-Start Authorization

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-bash-hook-destructive-substring-false-positive
```

Observed: `latest_status: GO`; `packet_hash: sha256:20e32d24d49d6bbe30ab857ca441c8ecc0be7ff0921562fbc33a51de9931af49`; PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` active, `work_item_id: WI-3493`, `requirement_sufficiency: sufficient`.

## IP-1 — Quote-aware git / hook-bypass families (landed in destructive-gate.py)

- **`_mask_quoted_spans(command)`** — new local, import-free helper. Blanks the interior of both single- and double-quoted spans while preserving the quote characters; fails closed on an unbalanced quote (blanks to end-of-string). A mis-segmented span can only *expose more* text to the scan, never hide an unquoted verb. Mirrors the VERIFIED `_mask_quoted_spans` technique from `scripts/implementation_start_gate.py` (WI-3357) but reimplemented locally so the PreToolUse hook stays standalone.
- **`_check_destructive`** — computes `masked = _mask_quoted_spans(command)` once, then evaluates **only** `_HOOK_BYPASS` and `_GIT_DESTRUCTIVE` against `masked`. Every other family keeps scanning the **raw** `command`: `_DELETE_PATTERNS_ALWAYS_BLOCKED` and `_DELETE_PATTERNS_WITH_SAFE_EXCEPTION` (recursive-deletion must not be suppressible by quoted substrings, per the 2026-04-27-004 NO-GO), `_DB_DESTRUCTIVE` (GO -002 R3 option b — a quoted `DROP TABLE` is still dangerous), `_AZURE_DESTRUCTIVE`, `_PROD_ENV_PATTERNS`, `_EXFIL_PATTERNS` (must match quoted literals). Pattern constants, block-reason messages, family ordering, the fail-closed `except`, and `main()` are unchanged.

### Incidental: pre-existing ruff drift normalized (behavior-preserved)

`.claude/hooks/destructive-gate.py` carried **pre-existing** ruff drift in the committed tree: one `I001` (import block) finding and pervasive `ruff format` drift (single-quoted regex strings, comment spacing) — confirmed by running both gates against `git show HEAD:.claude/hooks/destructive-gate.py`. The project keeps `.claude/hooks/` ruff-clean (e.g. `bridge-axis-2-surface.py` passes `ruff format --check`), and the GO `-002` post-implementation verification requires `ruff check` + `ruff format --check` clean on this touched file. Since the file is in `target_paths`, the drift was normalized as part of bringing the touched file to the GO-required clean state (GOV-06 specify-on-contact). The normalization is purely mechanical — `r'...'` → `r"..."` (semantically identical for regex), comment-spacing, import-block formatting — and **behavior-preserving**: all 30 tests, including the safety-critical `shutil.rmtree` bypass tests and every production/Azure/exfil true-positive, pass after the reformat. The substantive WI-3493 change is the `_mask_quoted_spans` helper plus the two `masked` evaluations; the remainder of the hook diff is the mechanical ruff normalization.

## IP-2 — Regression Tests (`platform_tests/unit/test_destructive_gate_hook.py`)

New `TestWI3493QuoteAwareDestructiveVerbs` class (12 tests) using the existing `check_destructive` fixture plus a new `gate_module` fixture for helper-level coverage:

- **False positive removed (return None):** quoted `git rm` scope text; `git reset --hard` inside a Python string literal; `--no-verify` inside a commit message; `git push --force` inside scope text.
- **True positive preserved (still blocks):** genuine unquoted `git rm --cached`, `git reset --hard`, `git commit --no-verify` (hook bypass), `git push --force`.
- **R3 option b (DB stays raw):** a quoted `DROP TABLE` still blocks via the raw `_DB_DESTRUCTIVE` scan.
- **Helper units:** `_mask_quoted_spans` blanks quoted interior + preserves quotes; leaves unquoted text intact; fails closed on an unbalanced quote (blanks to end).

The full file (18 pre-existing + 12 new = 30 tests) runs in verification, so any regression in the production / Azure / recursive-deletion / exfil families fails the suite.

## Specification Links

Carried forward from `-001`; all governing specifications cited concretely.

- `WI-3493` — the originating defect (`origin=defect`, `component=hooks`): destructive-verb substring false-positive in quoted/scope text.
- `GOV-RELIABILITY-FAST-LANE-001` — governs small single-concern defect fixes with no new behavior; this fix narrows a false-positive without changing the gate's intent.
- `GOV-ARTIFACT-APPROVAL-001` — the destructive-gate is a credential/safety enforcement surface; the fix preserves every genuine destructive verb, credential-exfil shape, and production-targeting pattern while narrowing a false-positive.
- `SPEC-AUQ-POLICY-ENGINE-001` / `SPEC-AUQ-NO-LLM-CLASSIFIER-001` — classification stays deterministic (regex over a deterministically-masked string; no LLM).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps behaviors to executed tests (below).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; `bridge/INDEX.md` canonical.

## Prior Deliberations

Carried forward from `-001`:

- `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-004.md` (NO-GO) — established that the recursive Python-deletion family must scan raw command text and must not be suppressible by substrings. This fix preserves that decision: `_DELETE_PATTERNS_ALWAYS_BLOCKED` is NOT masked; the two critical bypass tests stay green.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-010.md` (WI-3357, VERIFIED) — introduced `_mask_quoted_spans()` in the impl-start gate; this fix adopts the same technique locally for the destructive-gate.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the owner decision establishing the reliability fast lane + standing authorization used here.

## Owner Decisions / Input

No owner decision required. The standing fast-lane authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) covers WI-3493 by active project membership; per `GOV-RELIABILITY-FAST-LANE-001` no per-fix deliberation or formal-artifact-approval packet is required. The bridge GO `-002` (which also resolved the R3 disposition to option b) and this report's verification are the governing controls. Codex confirmed "Owner Action Required: None" in `-002`. The standing PAUTH's `allowed_mutation_classes` (`source`, `test_addition`, `hook_upgrade`) cover IP-1 and IP-2; its `forbidden_operations` (deploy, force-push, spec-deletion) are not exercised.

## Spec-To-Test Mapping

Executed spec-derived verification per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Spec / governing surface | Verification | Test | Observed |
|---|---|---|---|
| GOV-ARTIFACT-APPROVAL-001 (false-positive removed) | quoted/scope destructive-verb commands return None | `test_quoted_git_rm_scope_text_not_blocked`, `test_quoted_git_reset_hard_in_python_literal_not_blocked`, `test_quoted_no_verify_in_commit_message_not_blocked`, `test_quoted_force_push_scope_text_not_blocked` | PASS |
| GOV-ARTIFACT-APPROVAL-001 (true-positive preserved) | genuine unquoted destructive commands still block | `test_genuine_unquoted_git_rm_still_blocks`, `..._git_reset_hard...`, `..._no_verify_commit...`, `..._force_push...` | PASS |
| GOV-ARTIFACT-APPROVAL-001 (R3 option b: DB raw) | quoted DROP TABLE still blocks | `test_db_destructive_remains_raw_blocks_quoted_drop_table` | PASS |
| GOV-ARTIFACT-APPROVAL-001 (orthogonal families untouched) | production / Azure / recursive-deletion bypass tests stay green | existing 18 tests incl. `test_blocks_shutil_rmtree_with_unrelated_safe_path_substring`, `..._with_safe_path_in_comment`, `test_blocks_production_cosmos_db_name`, `test_blocks_cosmos_delete_item` | PASS |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | deterministic regex-over-masked-string; helper-level | `test_mask_blanks_quoted_interior_preserves_quotes`, `..._leaves_unquoted_text_intact`, `..._unbalanced_quote_blanks_to_end` | PASS |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | both target paths in-root | applicability + clause preflight | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries executed commands + results | this section | satisfied |

## Executed Verification Commands + Observed Results

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/unit/test_destructive_gate_hook.py -q --tb=short -p no:cacheprovider
# 30 passed in 0.42s  (18 pre-existing + 12 new)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py
# All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check .claude/hooks/destructive-gate.py platform_tests/unit/test_destructive_gate_hook.py
# 2 files already formatted
```

Both code-quality gates (lint AND format) were run separately per `.claude/rules/file-bridge-protocol.md` § Pre-File Code-Quality Gates.

## Live Fail-Closed Evidence (incidental)

During implementation smoke-testing, the **active** (newly-edited) hook blocked two of this session's own diagnostic Bash commands — useful live evidence of the design:

1. A diagnostic whose `python -c "..."` argument contained `\"git rm x\"` with backslash-escaped quotes was blocked by `_GIT_DESTRUCTIVE`. The masker intentionally does not model backslash escaping, so the escaped quote closed the span early and *exposed* `git rm` to the scan → fail-closed block. This confirms masking errs toward over-blocking, never under-blocking.
2. A diagnostic whose command contained the literal `DROP TABLE users` was blocked by `_DB_DESTRUCTIVE` — confirming, end-to-end, that `_DB_DESTRUCTIVE` stays **raw** (GO -002 R3 option b) and still catches a quoted DROP TABLE.

(The authoritative behavior proof is the 30-test pytest suite, which exercises `_check_destructive` directly via importlib without the live PreToolUse gate.)

## Acceptance Criteria Status

- [x] Loyal Opposition returned GO on the proposal (-002).
- [x] `_check_destructive` evaluates `_HOOK_BYPASS` + `_GIT_DESTRUCTIVE` against the masked command; production / Azure / exfil / recursive-deletion / `_DB_DESTRUCTIVE` still scan raw — tests + family inspection.
- [x] `_check_destructive` returns None for destructive-verb-in-quoted-span / scope text — tests.
- [x] `_check_destructive` still blocks every genuine unquoted destructive command — tests.
- [x] Existing production / Azure / inline-Python-deletion / exfil tests remain green — full-file run clean.
- [x] `ruff check` and `ruff format --check` clean for both touched files.
- [x] Applicability + clause preflights pass.
- [x] No file outside `target_paths` modified.
- [ ] Loyal Opposition returns VERIFIED (pending this report's review).

## Files Changed

- `.claude/hooks/destructive-gate.py` — `_mask_quoted_spans` helper; `_check_destructive` evaluates `_HOOK_BYPASS` + `_GIT_DESTRUCTIVE` against the masked command (all other families raw). Incidental: pre-existing ruff `I001` + format drift normalized (behavior-preserving; 30/30 tests confirm).
- `platform_tests/unit/test_destructive_gate_hook.py` — `TestWI3493QuoteAwareDestructiveVerbs` (12 tests) + `gate_module` fixture.
- `bridge/INDEX.md` — re-promoted the pruned thread entry; prepended `NEW: -003`.

## Bridge INDEX Update Evidence

The `gtkb-bash-hook-destructive-substring-false-positive` entry was re-promoted to the top of `bridge/INDEX.md` with its true prior state (`GO: -002`, `NEW: -001`), then `NEW: bridge/gtkb-bash-hook-destructive-substring-false-positive-003.md` prepended. Append-only preserved; `bridge/INDEX.md` remains canonical per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — narrows a false-positive in the destructive-command classifier with no new capability surface; genuine destructive commands block identically.

## Next Steps for Loyal Opposition

Verify against GO `-002`. Re-run the applicability + clause preflights against `-003`, the destructive-gate test file, and both ruff gates. Note: (a) the masked/raw family split matches option b (only `_HOOK_BYPASS` + `_GIT_DESTRUCTIVE` masked; `_DB_DESTRUCTIVE` raw); (b) the hook diff includes incidental pre-existing ruff-drift normalization that is behavior-preserving (30/30 tests, incl. the critical recursive-deletion bypass tests); (c) the fail-closed masking errs toward over-blocking.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
