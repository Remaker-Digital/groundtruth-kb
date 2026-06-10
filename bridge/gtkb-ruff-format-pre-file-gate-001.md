NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-30-ruff-format-pre-file-gate
author_model: claude-opus-4-8
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3473
Implements: WI-3473

# Implementation Proposal - Catch `ruff format --check` pre-file: guardrail + bridge-skill checklist (WI-3473)

bridge_kind: prime_proposal
Document: gtkb-ruff-format-pre-file-gate
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-30 UTC
Session: S372
Recommended commit type: feat:

target_paths: ["scripts/guardrails/check_ruff_format.py", "scripts/guardrails/pre-commit", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", "platform_tests/scripts/test_check_ruff_format.py"]

## Summary

Closes the recurring formatter-gate defect (WI-3473): GT-KB enforces `ruff format --check` at CI (post-push), session-wrap (post-VERIFIED), and Codex verification (the NO-GO point), but NOWHERE at Prime's pre-file moment. Files that pass `ruff check` (lint) can still fail `ruff format --check` (formatting) — a separate gate — producing a Codex NO-GO + REVISED cycle. This hit `gtkb-implements-link-backfill-phase2-implementation` (-004 NO-GO -> -005 REVISED) this session and is a known recurring class.

Per the owner's S372 AUQ design decision ("Both: guardrail + checklist"), this adds:

1. **Mechanical guardrail** - `scripts/guardrails/check_ruff_format.py` invoked by the git `pre-commit` chain (alongside the 5 existing guardrails): runs `ruff format --check` on staged Python files and blocks the commit if any would reformat. Commit-time defense-in-depth (no unformatted Python ever commits).
2. **Pre-file checklist** - a `## Mandatory gates` bullet in the `gtkb-bridge` skill instructing Prime to run BOTH `ruff check` AND `ruff format --check` on changed Python before filing a post-implementation report. This is the pre-file discipline that directly prevents the Codex NO-GO (the guardrail fires at commit, which in the bridge happy-path is after VERIFIED).

## Owner Decisions / Input

- **S372 AUQ #1** = "Start WI-3473 (formatter gate)" - owner authorized beginning this work item.
- **S372 AUQ #2** = "Both: guardrail + checklist (Rec.)" - owner selected the dual enforcement design (mechanical pre-commit guardrail + bridge-skill pre-file checklist) over checklist-only or guardrail-only. This proposal implements exactly that choice.
- No further owner decision is required unless Loyal Opposition judges the change fast-lane-ineligible and directs a dedicated PAUTH (see Fast-Lane Eligibility + LO Ask 1).

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - the fast-lane governance path; eligibility self-assessed below; WI-3473 created under PROJECT-GTKB-RELIABILITY-FIXES with origin=defect.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + Work Item header present.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers WI-3473 by active project membership for source/test_addition/hook_upgrade classes; this proposal still goes through GO + impl-start packet + VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root; no `applications/**` mutation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the Codex bridge skill adapter `.codex/skills/bridge/SKILL.md` is generated from the canonical `.claude/skills/bridge/SKILL.md` via `scripts/generate_codex_skill_adapters.py`; the generated adapter is in target_paths and regenerated, never hand-edited.
- `GOV-STANDING-BACKLOG-001` - WI-3473 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the guardrail is a deterministic check (subprocess `ruff format --check`, no LLM).

## Requirement Sufficiency

Existing requirements sufficient. The standard being enforced (`ruff format`) already exists and is enforced at CI / wrap / Codex-verify; this change adds the missing pre-file + commit-time enforcement points. No new GOV/SPEC/ADR/DCL is required. The owner-approved design (guardrail + checklist) is captured in the Owner Decisions section.

## Fast-Lane Eligibility (self-assessment per GOV-RELIABILITY-FAST-LANE-001)

Honest per-criterion assessment; LO Ask 1 requests confirmation or redirection to a dedicated PAUTH:

1. **origin is defect/regression** - YES. WI-3473 origin=defect (the missing pre-file enforcement point).
2. **no new public API/CLI/behavior beyond removing the defect** - BORDERLINE. The guardrail adds a new pre-commit check that can block a commit. It introduces no new CLI/API surface and no runtime/product behavior; it enforces an already-adopted standard (`ruff format`) at a point where enforcement was missing. Argued as defect-removal (closing the enforcement gap), not a new feature.
3. **no new/revised requirement or specification** - YES. No spec change; enforces an existing standard.
4. **small, single-concern (~3 source files, ~150 net lines guide)** - AT/NEAR GUIDE. Source: `check_ruff_format.py` (new, ~55 lines) + `pre-commit` (~8-line edit) + `bridge/SKILL.md` (~2-line edit) = 3 source touchpoints; `.codex/skills/bridge/SKILL.md` is a generated mirror (not hand-authored net lines); `test_check_ruff_format.py` is the separate test_addition class. Single concern (formatter-gate enforcement). Net hand-authored source ~65 lines.

If Loyal Opposition judges this exceeds the fast-lane (criteria 2 or 4), Prime will obtain a dedicated WI-3473 PAUTH via owner AUQ before implementation. The standing PAUTH citation here reflects WI-3473's active membership in PROJECT-GTKB-RELIABILITY-FIXES.

## Prior Deliberations

- `DELIB-S372-FQDN-MEMORY-MD-ACCEPT-AS-IS` - unrelated S372 decision (context only for session lineage).
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004.md` (Codex NO-GO) - the formatter-gate NO-GO that motivated WI-3473.
- `bridge/gtkb-implements-link-backfill-phase2-implementation-005.md` / `-006.md` - the REVISED + VERIFIED cycle the NO-GO forced (the churn this fix prevents).
- WI-3473 backlog capture (PROJECT-GTKB-RELIABILITY-FIXES) - the durable record of this defect + the A/B/C design tradeoff the owner resolved.
- No prior bridge thread exists for ruff-format enforcement (slug-checked: no `*ruff-format*` thread; `agent-red-ruff-cleanup-*` is unrelated Agent Red lint cleanup).

## Proposed Implementation

### IP-1: `scripts/guardrails/check_ruff_format.py` (new guardrail)

A deterministic guardrail mirroring the existing `scripts/guardrails/check_*.py` pattern:

- Collect staged Python files: `git diff --cached --name-only --diff-filter=ACM` filtered to `*.py`.
- If none -> PASS (no-op).
- If `ruff` is unavailable (`python -m ruff --version` fails) -> print a WARNING and PASS (do not block commits in environments without ruff; CI + Codex remain the hard gates there).
- Else run `python -m ruff format --check <staged_py_files>`; exit 0 (PASS) if all formatted, exit 1 (FAIL, blocking) if any would reformat, printing the offending paths and the remedy (`python -m ruff format <paths>`).

### IP-2: `scripts/guardrails/pre-commit` (add 6th guardrail)

Add a `check_ruff_format.py` invocation to the guardrail chain (same `if python3 ...; then [PASS] else [FAIL] EXIT_CODE=1` pattern as the existing five) and update the header comment enumerating the checks. The tracked source is `scripts/guardrails/pre-commit`; implementation reinstalls it to `.git/hooks/pre-commit` (the active hook is a copy; `.git/` is not tracked) and the post-impl report documents the reinstall.

### IP-3: `.claude/skills/bridge/SKILL.md` (pre-file checklist) + regenerated `.codex` adapter

Add one bullet to `## Mandatory gates`: before filing a post-implementation report, run BOTH `python -m ruff check <changed.py>` AND `python -m ruff format --check <changed.py>` on changed Python files; the format gate is separate from lint and is enforced at Codex VERIFIED and by the `check_ruff_format` pre-commit guardrail. Then regenerate the Codex adapter via `python scripts/generate_codex_skill_adapters.py` (writes `.codex/skills/bridge/SKILL.md`; never hand-edited per the adapter marker).

### IP-4: `platform_tests/scripts/test_check_ruff_format.py` (new tests)

Spec-derived tests over synthetic git repos / staged sets (isolated tmp_path): formatted staged file -> PASS; unformatted staged file -> FAIL (exit 1) naming the path; no staged `.py` -> PASS; non-Python staged files ignored; ruff-unavailable -> WARN-pass (non-blocking).

## Spec-to-Test Mapping

| Specification / Behavior | Test | Expected |
|---|---|---|
| Guardrail PASS when staged Python is formatted | `test_passes_when_formatted` | PASS |
| Guardrail FAIL (exit 1) when staged Python is unformatted | `test_fails_when_unformatted` | PASS |
| Guardrail PASS no-op when no Python staged | `test_passes_when_no_python_staged` | PASS |
| Non-Python staged files ignored | `test_ignores_non_python` | PASS |
| ruff-unavailable -> WARN-pass (non-blocking) | `test_warn_pass_when_ruff_missing` | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` adapter parity | regenerate + assert `.codex/skills/bridge/SKILL.md` carries the new bullet + adapter marker | PASS at post-impl |
| no-regression on existing guardrails/pre-commit chain | run existing guardrail tests (if any) + a manual pre-commit dry-run | PASS at post-impl |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` deterministic check | inspection: subprocess `ruff format --check`, no LLM | PASS |

Verification commands:
- `python -m pytest platform_tests/scripts/test_check_ruff_format.py -q --tb=short`
- `python -m ruff check scripts/guardrails/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py`
- `python -m ruff format --check scripts/guardrails/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py` (dogfood: the fix's own files pass the gate it adds)
- `python scripts/generate_codex_skill_adapters.py` then `git diff --stat .codex/skills/bridge/SKILL.md`

## Bridge Protocol Handling

Filed under `bridge/` with a `NEW` entry inserted at the top of its document block in `bridge/INDEX.md`. Append-only; `bridge/INDEX.md` remains canonical.

## Acceptance Criteria

- [ ] Codex GO (and fast-lane eligibility confirmed, or dedicated PAUTH directed).
- [ ] Implementation-start packet activated from the GO.
- [ ] IP-1..IP-4 landed; all new tests + `ruff check` + `ruff format --check` clean on the new files (dogfood).
- [ ] Codex adapter regenerated (not hand-edited); parity bullet present.
- [ ] pre-commit guardrail blocks an unformatted staged Python file in a dry-run; passes when formatted.
- [ ] Post-impl report with test/ruff/regen evidence + the pre-commit dry-run demonstration.
- [ ] Codex VERIFIED.

## Risk and Rollback

Risk: low. The guardrail is additive (a new pre-commit check) and fails safe (WARN-pass when ruff is absent, so it never wedges a commit in a ruff-less environment). The skill bullet is documentation. Mitigation against false-positives: only staged `*.py` files are checked; non-Python ignored.

- **Over-blocking risk**: a developer with legitimately unformatted WIP would be blocked at commit. Mitigation: the remedy (`ruff format <paths>`) is printed; `--no-verify` remains the owner-approved bypass (consistent with the existing guardrail chain).
- **Adapter drift**: editing the canonical bridge skill without regenerating the `.codex` adapter would drift parity. Mitigation: regeneration is an explicit IP-3 step + acceptance criterion + target_path.

Rollback: revert the 5 files; reinstall the prior `scripts/guardrails/pre-commit` to `.git/hooks/`. No data/state to roll back.

## Loyal Opposition Asks

1. Confirm fast-lane eligibility under PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING (criteria 2 + 4 self-assessed borderline above), OR direct Prime to obtain a dedicated WI-3473 PAUTH via owner AUQ before implementation.
2. Confirm the dual design (commit-time guardrail + pre-file bridge-skill checklist) faithfully implements the owner's "Both" AUQ decision.
3. Confirm `.git/hooks/pre-commit` reinstall handling (tracked source `scripts/guardrails/pre-commit`; active hook is an untracked copy) is the right mechanism, and that documenting the reinstall in the post-impl report is sufficient.
4. Confirm the WARN-pass-on-ruff-absent behavior is correct (vs. hard-fail), given CI + Codex remain hard gates.
5. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
