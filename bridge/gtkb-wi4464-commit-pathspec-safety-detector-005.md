REVISED

bridge_kind: implementation_report
Document: gtkb-wi4464-commit-pathspec-safety-detector
Version: 005
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 94dd17d8-0952-4acf-bef7-6330d72b2779
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code dispatched bridge worker; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC
Review-Target: bridge/gtkb-wi4464-commit-pathspec-safety-detector-002.md
Responds to: bridge/gtkb-wi4464-commit-pathspec-safety-detector-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4464
target_paths: ["scripts/check_commit_pathspec_safety.py", "platform_tests/scripts/test_check_commit_pathspec_safety.py"]
implementation_scope: source, test
Recommended commit type: feat:

# WI-4464 Slice A — Implementation Report (REVISED): Commit pathspec-safety detector

## Revision Scope (response to NO-GO -004)

This is a **report-only revision** of `-003`. The NO-GO at `-004` did not request
any source/test change — its single P1 finding was that the mandatory bridge
applicability preflight reported `preflight_passed: false` on the report file
itself, with `missing_required_specs` containing
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`GOV-FILE-BRIDGE-AUTHORITY-001`.

Root cause: `-003`'s spec-link heading was `## Specification Links (carried
forward from -001)`. The preflight's `SPEC_LINK_HEADING_RE`
(`scripts/bridge_applicability_preflight.py`) anchors `$` immediately after the
optional `links?` token, so the trailing ` (carried forward from -001)` suffix
prevented the heading from matching. `extract_spec_links()` therefore found no
spec-link section, harvested zero spec IDs, and reported every triggered
cross-cutting spec as missing — even though all three required specs were cited
inline in that section.

Fix (this version):

1. The section heading is restored to the canonical `## Specification Links`
   (no parenthetical suffix); the "carried forward from -001" provenance moves
   into the section body, where it does not affect the parse.
2. The three advisory specs the preflight also flagged
   (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
   `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`)
   are now cited so `missing_advisory_specs` is also empty.

No change was made to `scripts/check_commit_pathspec_safety.py` or
`platform_tests/scripts/test_check_commit_pathspec_safety.py`; the behavioral
evidence from `-003` (16 tests, both ruff gates) is carried forward unchanged
and re-confirmed below.

## Summary

Implemented the GO'd Slice A (`bridge/gtkb-wi4464-commit-pathspec-safety-detector-002.md`):
a standalone, stdlib-only detector for the bridge+source staged-index
contamination signature that caused the 2026-06-11 `772a186b` mislabel
incident, plus its full unit-test suite. Both files are net-new and within the
two GO-approved `target_paths`. No hook/config wiring, no commit interception,
no bridge authority mutation, no KB/formal-artifact mutation was bundled — the
commit-time wiring remains deliberately deferred to a follow-on slice under its
own (hook/config) authorization, exactly as the proposal scoped it.

Implementation-start authorization packet (derived from the live GO):
`sha256:fb5165d951b8bae544c2a1e691696b72ded1557446bf189c6a391184892b864e`.

## Files Changed

- `scripts/check_commit_pathspec_safety.py` (NEW, ~170 lines, stdlib only) —
  `classify_staged()` pure partition function, `_staged_names()` read-only git
  shim (`git diff --cached --name-only --diff-filter=ACM`, fail-open to `[]`),
  `main()` CLI with `--staged` / `--strict` / `--json`. Bridge-queue match rule
  is a documented module constant `BRIDGE_QUEUE_PATTERN = ^bridge/[^/]+\.md$`
  (canonical queue surface only: `bridge/INDEX.md` + top-level `bridge/*.md`;
  nested or non-`.md` paths are `other`). Advisory mode (default) exits 0
  always; `--strict` exits `STRICT_CONTAMINATION_EXIT` (3) on contamination.
- `platform_tests/scripts/test_check_commit_pathspec_safety.py` (NEW, 16 tests)
  — covers every acceptance criterion plus matcher edge cases (nested path,
  non-`.md`, backslash normalization) and `_staged_names` fail-open paths
  (OSError + CalledProcessError). Loads the script via
  `importlib.util.spec_from_file_location` and monkeypatches `_staged_names`
  to bypass git entirely.

## Specification Links

These governing surfaces are carried forward from the GO'd proposal `-001` and
the report `-003` (the "carried forward from -001" provenance previously in the
heading is recorded here in the body so the canonical heading parses cleanly):

- **GOV-STANDING-BACKLOG-001** — WI-4464 backlog authority (P1 git-workflow).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implemented under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (`source` + `test_addition`); stayed strictly in scope.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — detector surfaces the contamination signature without altering bridge authority or touching any bridge file.
- **`.claude/rules/bridge-essential.md`** ("Scoped commits only") — the standing protocol invariant the detector operationalizes.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH/project/WI/target-path metadata concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (table below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both target paths in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001**, **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001**, **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** — this report is the durable artifact preserving the WI-4464 implementation decision, its verification evidence, and the lifecycle transition (advisory cross-cutting surfaces the preflight associates with bridge reports).

## Spec-to-Test Mapping (executed)

| Acceptance criterion | Test | Result |
|---|---|---|
| Contamination signature detected (WI-4464; "Scoped commits only") | `test_mixed_bridge_and_source_is_flagged` | PASS |
| No false positive on bridge-only commit (GOV-FILE-BRIDGE-AUTHORITY-001) | `test_bridge_only_not_mixed` | PASS |
| No false positive on source-only commit | `test_source_only_not_mixed` | PASS |
| Empty staged set not flagged | `test_empty_not_mixed` | PASS |
| Conservative matcher — nested `bridge/` path is `other` | `test_nested_bridge_path_is_other` | PASS |
| Conservative matcher — non-`.md` `bridge/` path is `other` | `test_non_md_bridge_path_is_other` | PASS |
| Backslash path normalization | `test_backslash_paths_normalized` | PASS |
| Advisory mode never blocks a commit (fail-open) | `test_advisory_exit_zero_on_mixed` | PASS |
| Strict mode blocks on contamination (exit 3) | `test_strict_exit_nonzero_on_mixed` | PASS |
| Strict mode passes a clean staged set | `test_strict_exit_zero_on_clean` | PASS |
| JSON output shape | `test_json_output` | PASS |
| JSON always exits 0 even when mixed | `test_json_exit_zero_even_when_mixed` | PASS |
| No-git / no-staged fail-open | `test_no_staged_fail_open` | PASS |
| Default (no `--staged`) clean exit | `test_default_no_staged_flag_is_clean` | PASS |
| `_staged_names` fail-open on OSError | `test_staged_names_fail_open_on_oserror` | PASS |
| `_staged_names` fail-open on CalledProcessError | `test_staged_names_fail_open_on_called_process_error` | PASS |

## Verification Evidence (exact commands + observed results)

```powershell
python -m pytest platform_tests/scripts/test_check_commit_pathspec_safety.py -q --tb=short
# -> 16 passed in 0.31s

python -m ruff check scripts/check_commit_pathspec_safety.py platform_tests/scripts/test_check_commit_pathspec_safety.py
# -> All checks passed!

python -m ruff format --check scripts/check_commit_pathspec_safety.py platform_tests/scripts/test_check_commit_pathspec_safety.py
# -> 2 files already formatted
```

Both ruff gates were run as SEPARATE checks per the file-bridge protocol's
Pre-File Code-Quality Gates: one `ruff format` quote-normalization was applied
to the script during implementation, after which both gates are green. This
revision touches no source/test file, so these results are unchanged from `-003`
and re-confirmed in the Commands Executed section below.

### Live read-only demonstration (no staging performed)

Run against the actual current staged index (read-only `git diff --cached`):

```powershell
python scripts/check_commit_pathspec_safety.py --staged --json
# -> mixed: True; bridge_queue: staged bridge files; other: non-bridge file(s)
```

The detector correctly flags the live index — which genuinely mixes staged
bridge-queue files with one or more non-bridge `other` files — as the exact
contamination signature WI-4464 targets. A plain `git commit` against this
index would mislabel, reproducing the `772a186b` failure mode. The run is
read-only and staged nothing.

## Scope Boundary Confirmation (no out-of-scope changes bundled)

- No hook registration changed (`.githooks/pre-commit`, `.claude/settings.json`, `.codex/hooks.json` untouched).
- No commit interception / pre-commit wiring / PreToolUse guard added.
- No `bridge/INDEX.md` content authority change, no bridge file content mutation (only the protocol-required `-005` report + its `REVISED:` index row).
- No KB / formal-artifact / config / schema / deployment / credential work.
- Only the two GO-approved `target_paths` were created (in `-003`); this revision adds no new files.

## Prior Deliberations

- **`memory/recovery-2026-06-11-fab20-commit-collision.md`** — forensic record of the `772a186b` mislabel + reset-orphan incident; primary source for the contamination signature.
- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ admitting WI-4464 under the batch-1 PAUTH (`source` + `test_addition`).
- **`bridge/gtkb-wi4464-commit-pathspec-safety-detector-002.md`** — the GO verdict implemented here.
- **`bridge/gtkb-wi4464-commit-pathspec-safety-detector-004.md`** — the verification NO-GO this revision addresses (preflight heading-recognition defect).

## Owner Decisions / Input

Implemented under durable owner-decision evidence; no new owner AskUserQuestion
was required.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ approval (2026-06-13) admitting WI-4464 to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`). Slice A stayed strictly within that scope. This report-only revision introduces no new owner-decision scope.

## Recommended Commit Type

`feat:` — net-new capability (a new detection script + its test suite), not a
repair of existing broken behavior. Per the Conventional Commits discipline
(`.claude/rules/file-bridge-protocol.md`), net-new modules/scripts/capabilities
are `feat:`. The report-only heading fix in this revision does not change the
recommended type.

## Risk / Rollback

Very low. The detector is NOT wired into any commit path, so it cannot block,
slow, or alter any commit — zero behavior change to the active swarm or to
`gtkb-sweep-commit`. Read-only git access only. Rollback: delete the two new
files.

## Commands Executed (this revision)

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4464-commit-pathspec-safety-detector
# -> preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4464-commit-pathspec-safety-detector
# -> exit 0; blocking gaps: 0

python -m pytest platform_tests/scripts/test_check_commit_pathspec_safety.py -q --tb=short
# -> 16 passed

python -m ruff check scripts/check_commit_pathspec_safety.py platform_tests/scripts/test_check_commit_pathspec_safety.py
# -> All checks passed!

python -m ruff format --check scripts/check_commit_pathspec_safety.py platform_tests/scripts/test_check_commit_pathspec_safety.py
# -> 2 files already formatted
```

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
