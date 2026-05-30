REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-30-ruff-format-pre-file-gate-revised-2
author_model: claude-opus-4-8
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3473
Implements: WI-3473

# Implementation Proposal - Catch `ruff format --check` pre-file: active-hook guardrail + bridge-skill checklist (WI-3473) (REVISED-2)

bridge_kind: implementation_proposal
Document: gtkb-ruff-format-pre-file-gate
Version: 003 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-30 UTC
Session: S372
Responds to NO-GO: bridge/gtkb-ruff-format-pre-file-gate-002.md
Recommended commit type: feat:

target_paths: ["scripts/check_ruff_format.py", ".githooks/pre-commit", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", "platform_tests/scripts/test_check_ruff_format.py"]

## REVISED-2 Changes (closes NO-GO -002 F1 + F2 + F3)

NO-GO -002 raised two P1 correctness defects (both Prime-acknowledged as correct) and one P3 advisory-citation gap:

- **F1 (P1) — wrong hook surface.** -001 targeted `scripts/guardrails/pre-commit` + a reinstall to `.git/hooks/pre-commit`, but `git config core.hooksPath` is **`.githooks`**. The active hook is `.githooks/pre-commit` (confirmed: it runs the staged secret scan, inventory-drift check, narrative-artifact-evidence check, and PS1 syntax parse — the exact output seen on this session's commits). `scripts/guardrails/pre-commit` is an INACTIVE chain; editing it would have left the live commit path unchanged. Prior precedent `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` NO-GO'd the identical `.git/hooks` mistake.
- **F2 (P1) — fail-open interpreter resolution.** -001 used `python -m ruff` + WARN-pass-when-absent. In this checkout default `python` lacks ruff while the project venv has `ruff 0.15.12`, so the guardrail would silently WARN-pass in the exact (dev) environment it must catch.
- **F3 (P3) — uncited advisory specs.** The applicability preflight reported three missing advisory artifact-governance specs.

REVISED-2 closes all three:

1. **F1:** the guardrail is now a stdlib-only helper `scripts/check_ruff_format.py` invoked by the ACTIVE `.githooks/pre-commit` (added as a new staged check alongside the existing ones). `target_paths` lists `.githooks/pre-commit` (the active surface) and drops the `scripts/guardrails/pre-commit` + `.git/hooks` reinstall claim entirely.
2. **F2:** `scripts/check_ruff_format.py` resolves a ruff-capable interpreter **deterministically, venv-first**: (1) project venv (`groundtruth-kb/.venv/Scripts/python.exe` on Windows, `groundtruth-kb/.venv/bin/python` on POSIX); (2) the launching `sys.executable` if it can run ruff; (3) `ruff` on PATH. It only WARN-passes when NO project venv exists at all (genuinely non-dev/CI, where CI's own ruff step is the gate); if the venv exists but ruff is unresolvable it FAILs (dev-env misconfig). A dedicated regression test asserts venv-preference so the gate cannot fail open in this checkout.
3. **F3:** the three advisory specs are added to Specification Links.

The owner-approved "Both" design (mechanical guardrail + pre-file bridge-skill checklist) is preserved. The checklist half (bridge skill + regenerated Codex adapter) is unchanged from -001.

## Summary

Closes the recurring formatter-gate defect (WI-3473): GT-KB enforces `ruff format --check` at CI (post-push), session-wrap (post-VERIFIED), and Codex verification (the NO-GO point), but nowhere at Prime's pre-file moment. Files that pass `ruff check` (lint) can still fail `ruff format --check` (a separate gate), producing a Codex NO-GO + REVISED cycle (hit `gtkb-implements-link-backfill-phase2-implementation` -004 this session). Per the owner's "Both" AUQ: a mechanical guardrail wired into the ACTIVE `.githooks/pre-commit` (deterministic venv-resolved ruff) plus a `gtkb-bridge` skill pre-file checklist bullet.

## Owner Decisions / Input

- **S372 AUQ #1** = "Start WI-3473 (formatter gate)" — owner authorized beginning this work item.
- **S372 AUQ #2** = "Both: guardrail + checklist (Rec.)" — owner selected the dual enforcement design. This REVISED-2 preserves exactly that; the F1/F2 fixes change only HOW the mechanical half is wired (active hook + deterministic interpreter), not the design choice.
- No further owner decision required. Codex -002 did not challenge fast-lane eligibility and confirmed the standing PAUTH covers the mutation classes; if LO now judges otherwise, Prime will obtain a dedicated WI-3473 PAUTH via owner AUQ before implementation.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane governance path; WI-3473 created under PROJECT-GTKB-RELIABILITY-FIXES with origin=defect; eligibility self-assessed below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item header present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers WI-3473 by active membership (source/test_addition/hook_upgrade); still goes through GO + impl-start packet + VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths in-root; no `applications/**` mutation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — `.codex/skills/bridge/SKILL.md` is generated from the canonical `.claude/skills/bridge/SKILL.md` via `scripts/generate_codex_skill_adapters.py`; regenerated, never hand-edited.
- `GOV-STANDING-BACKLOG-001` — WI-3473 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the guardrail is a deterministic check (subprocess `ruff format --check`, deterministic interpreter resolution, no LLM).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — (advisory, added per F3) the guardrail + skill change are durable governance artifacts with traceability to WI-3473 + the motivating NO-GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — (advisory, added per F3) owner-decision / work-item / requirement framing of this fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — (advisory, added per F3) WI-3473 lifecycle advances on this implementation; the VERIFIED gate triggers on the post-impl report.

## Requirement Sufficiency

Existing requirements sufficient. The standard being enforced (`ruff format`) already exists and is enforced at CI / wrap / Codex-verify; this change adds the missing pre-file + commit-time enforcement points on the ACTIVE hook surface. No new GOV/SPEC/ADR/DCL is required. The owner-approved "Both" design is captured in Owner Decisions.

## Fast-Lane Eligibility (self-assessment per GOV-RELIABILITY-FAST-LANE-001)

1. **origin defect/regression** — YES (WI-3473 origin=defect).
2. **no new public API/CLI/behavior beyond removing the defect** — the guardrail adds a pre-commit check enforcing an already-adopted standard at a point where enforcement was missing; no new CLI/API/product surface. Argued as defect-removal. Codex -002 did not flag this as a blocker.
3. **no new/revised requirement/spec** — YES.
4. **small, single-concern (~3 source files / ~150 net lines guide)** — Source: `scripts/check_ruff_format.py` (new, ~85 lines incl. resolver) + `.githooks/pre-commit` (~5-line edit) + `.claude/skills/bridge/SKILL.md` (~2-line edit) = 3 source touchpoints; `.codex/.../SKILL.md` is a generated mirror; the test is the separate test_addition class. Net hand-authored source ~90 lines. Single concern (formatter-gate enforcement on the active hook).

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision creating the standing reliability fast-lane (PROJECT-GTKB-RELIABILITY-FIXES + standing PAUTH + GOV-RELIABILITY-FAST-LANE-001).
- `bridge/gtkb-ruff-format-pre-file-gate-002.md` (Codex NO-GO) — the F1/F2/F3 findings this REVISED-2 closes.
- `bridge/gtkb-commit-scope-bundling-detection-001-prop-002.md` — precedent NO-GO establishing that this repo's active hook path is `.githooks`, not `.git/hooks` (the F1 lesson).
- `bridge/gtkb-secrets-purge-and-commit-enforcement-001-001.md` — adjacent precedent: do not rely on `scripts/guardrails/pre-commit` being copied into `.git/hooks`.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md` (historical formatter-gate NO-GO that motivated WI-3473) and `-006.md` (the VERIFIED closure).
- WI-3473 backlog capture (PROJECT-GTKB-RELIABILITY-FIXES) — the durable defect record + the A/B/C design tradeoff the owner resolved.

## Proposed Implementation

### IP-1: `scripts/check_ruff_format.py` (new stdlib-only guardrail with deterministic resolver)

Stdlib-only (subprocess/pathlib/sys/shutil — NO `groundtruth_kb` import), so it runs under whatever interpreter the hook uses. Separable, testable functions:

- `staged_python_files(repo_root) -> list[str]`: `git diff --cached --name-only --diff-filter=ACM` filtered to `*.py`.
- `resolve_ruff(search_root) -> list[str] | None`: deterministic, venv-first resolution. Try, in order, running `<cmd> --version` (rc 0):
  1. `[<search_root>/groundtruth-kb/.venv/Scripts/python.exe, -m, ruff]` (Windows) or `.../bin/python` (POSIX);
  2. `[sys.executable, -m, ruff]`;
  3. `[shutil.which("ruff")]` if found.
  Returns the first working command, else `None`.
- `check_files(ruff_cmd, files) -> (ok: bool, output: str)`: runs `<ruff_cmd> format --check <files>`.
- `main()`: repo_root = `git rev-parse --show-toplevel` (fallback cwd); if no staged `.py` -> PASS (exit 0). Resolve ruff. If `None`: when `<root>/groundtruth-kb/.venv` exists -> FAIL (exit 1, "venv present but ruff unresolvable; install ruff"); else WARN + PASS (exit 0, non-dev/CI where CI enforces). If resolved: run check; PASS (exit 0) when formatted, FAIL (exit 1) naming offending paths + remedy (`ruff format <paths>`).

### IP-2: `.githooks/pre-commit` (active hook — add the guardrail)

Insert one staged-check invocation into the ACTIVE hook, in the existing style, after the narrative-artifact-evidence check and before the PS1 block:

```bash
"$PYTHON_BIN" scripts/check_ruff_format.py --staged || exit $?
```

`PYTHON_BIN` (default `python`) need not have ruff: `check_ruff_format.py` is stdlib-only and resolves ruff itself (venv-first). No `.git/hooks` reinstall — `.githooks` is the configured `core.hooksPath`, so the edit is live immediately.

### IP-3: `.claude/skills/bridge/SKILL.md` (pre-file checklist) + regenerated `.codex` adapter

Unchanged from -001: add a `## Mandatory gates` bullet instructing Prime to run BOTH `ruff check` AND `ruff format --check` on changed Python before filing a post-impl report (separate gates; format enforced at Codex VERIFIED + the new pre-commit guardrail). Regenerate `.codex/skills/bridge/SKILL.md` via `python scripts/generate_codex_skill_adapters.py`.

### IP-4: `platform_tests/scripts/test_check_ruff_format.py` (tests, incl. F2 regression)

- `test_passes_when_formatted` — temp git repo, stage a formatted `.py`; guardrail exit 0.
- `test_fails_when_unformatted` — stage an unformatted `.py`; exit 1, names the path.
- `test_passes_when_no_python_staged` — stage a non-`.py`; exit 0.
- `test_ignores_non_python` — formatted `.py` + `.md` staged; only `.py` checked; exit 0.
- `test_resolver_prefers_venv` (F2 regression) — assert `resolve_ruff(REPO_ROOT)` returns a command whose interpreter path is under `groundtruth-kb/.venv` when that venv exists (proves resolution does NOT depend on `sys.executable` having ruff — closes F2 fail-open).
- `test_resolver_warn_pass_only_without_venv` — `resolve_ruff` on a tmp root with no venv + the script's main WARN-passes (exit 0) only when no venv; FAILs when a venv dir exists but lacks ruff.

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| Guardrail PASS when staged Python formatted | `test_passes_when_formatted` | PASS |
| Guardrail FAIL (exit 1) when staged Python unformatted | `test_fails_when_unformatted` | PASS |
| No-op PASS when no Python staged | `test_passes_when_no_python_staged` | PASS |
| Non-Python staged files ignored | `test_ignores_non_python` | PASS |
| F2: deterministic venv-first resolution (no fail-open) | `test_resolver_prefers_venv` | PASS |
| F2: WARN-pass only when no venv; FAIL when venv lacks ruff | `test_resolver_warn_pass_only_without_venv` | PASS |
| F1: active hook blocks unformatted in THIS checkout | post-impl dry-run of `.githooks/pre-commit` (stage unformatted -> blocked; formatted -> passes) | PASS at post-impl |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` adapter parity | regenerate + assert `.codex/skills/bridge/SKILL.md` carries the new bullet + adapter marker | PASS at post-impl |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` deterministic check | inspection: subprocess + deterministic resolver, no LLM | PASS |

Verification commands:
- `python -m pytest platform_tests/scripts/test_check_ruff_format.py -q --tb=short`
- `<venv-python> -m ruff check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py`
- `<venv-python> -m ruff format --check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py` (dogfood)
- `python scripts/generate_codex_skill_adapters.py` then `git diff --stat .codex/skills/bridge/SKILL.md`
- Active-hook dry-run: stage an unformatted `.py`, run `.githooks/pre-commit`, observe block; format it, observe pass.

## Bridge Protocol Handling

Filed as `REVISED` at `-003`; the `REVISED` line is inserted at the top of this document's block in `bridge/INDEX.md`. Append-only; `-001` and `-002` retained. `bridge/INDEX.md` remains canonical.

## Acceptance Criteria

- [ ] Codex GO on REVISED-2.
- [ ] Implementation-start packet activated from the GO.
- [ ] IP-1..IP-4 landed; all tests + `ruff check` + `ruff format --check` (via venv) clean on the new files (dogfood).
- [ ] Codex adapter regenerated (not hand-edited); parity bullet present.
- [ ] Active-hook dry-run in THIS checkout: `.githooks/pre-commit` blocks an unformatted staged `.py`, passes once formatted (closes F1 + F2 empirically).
- [ ] Post-impl report with test/ruff/regen evidence + the active-hook dry-run demonstration.
- [ ] Codex VERIFIED.

## Risk and Rollback

Risk: low-moderate. The guardrail is additive on the active hook. Determinism: it resolves the venv ruff in the dev env (no fail-open); WARN-passes only in genuinely venv-less environments (CI enforces there). Over-blocking mitigation: only staged `*.py` checked; remedy printed; `--no-verify` remains the owner-approved bypass (consistent with the existing chain).

- **Active-hook edit risk**: a bad edit to `.githooks/pre-commit` could break all commits. Mitigation: minimal additive line in the existing style; the dry-run acceptance criterion validates the whole hook still functions.
- **Adapter drift**: mitigated by the regenerate step + acceptance criterion + target_path.

Rollback: revert the 5 files (the `.githooks/pre-commit` edit reverts cleanly; it's tracked). No data/state to roll back.

## Loyal Opposition Asks

1. Confirm F1 closed: the guardrail now targets the active `.githooks/pre-commit` (per `core.hooksPath=.githooks`), with `scripts/check_ruff_format.py` as the invoked helper; no `.git/hooks` reinstall.
2. Confirm F2 closed: the deterministic venv-first resolver + the `test_resolver_prefers_venv` regression prevent fail-open in this checkout; the post-impl active-hook dry-run will demonstrate empirically.
3. Confirm F3 closed: the three advisory artifact-governance specs are cited.
4. Confirm the WARN-pass-only-when-no-venv stance (FAIL when venv present but ruff missing) is the right determinism boundary.
5. Confirm fast-lane eligibility under the standing PAUTH (unchanged from -001; not challenged in -002), or direct a dedicated PAUTH.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
