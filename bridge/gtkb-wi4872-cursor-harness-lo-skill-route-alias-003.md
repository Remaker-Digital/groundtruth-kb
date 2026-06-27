NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report

# gtkb-wi4872-cursor-harness-lo-skill-route-alias — Post-implementation report: LO skill-route alias restores headless Cursor LO dispatch

Document: gtkb-wi4872-cursor-harness-lo-skill-route-alias
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4872
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4872-CURSOR-HARNESS-SKILL-ROUTE
Responds to: bridge/gtkb-wi4872-cursor-harness-lo-skill-route-alias-002.md (GO)
Recommended commit type: fix

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd (`-002`) skill-route alias. `scripts/cursor_harness.py` now maps the canonical Loyal Opposition route keys `bridge-review` → `proposal-review` and `verification` → `verify` before the SKILL.md lookup, so a headless Cursor LO worker dispatched with `--skill bridge-review` (per the harness-registry invocation surfaces) loads the real `proposal-review` skill contract instead of raising `CursorHarnessError` and exiting 1. This removes the cause of the `loyal-opposition:E` dispatch circuit-breaker trips.

## Implemented Changes

`scripts/cursor_harness.py`:
- Added module constant `_SKILL_ROUTE_ALIASES = {"bridge-review": "proposal-review", "verification": "verify"}`.
- `_skill_system_prompt(skill)` resolves `skill = _SKILL_ROUTE_ALIASES.get(skill, skill)` before the `.cursor`/`.codex`/`.claude` SKILL.md lookup. Non-aliased keys resolve unchanged; genuinely unknown keys still raise `CursorHarnessError` (fail-closed preserved).

`platform_tests/scripts/test_cursor_harness.py` (new):
- 5 spec-derived tests (alias-resolves-bridge-review / alias-resolves-verification / non-aliased-resolves / unknown-still-raises / none-returns-none).

No change to the harness registry, the resolution fallback order, dispatch selection, or worker spawning. (Scope note from `-001`: `openrouter`/`ollama` harnesses carry the same latent issue but are non-dispatchable; out of this bounded WI.)

## Specification Links

Carried forward from `-001`:
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-17` — Automation script modification approval gate; owner-authorized (DELIB-20266209, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher harness-isolation operability.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — specs cited; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4872 + project + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — behavior maps to derived tests, executed below.
- `GOV-STANDING-BACKLOG-001` — WI-4872 authorized standing-backlog item.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| WI-4872: `bridge-review` resolves to the proposal-review contract | `test_skill_route_alias_bridge_review_resolves` | PASS |
| WI-4872: `verification` resolves to the verify contract | `test_skill_route_alias_verification_resolves` | PASS |
| Non-aliased keys resolve unchanged | `test_skill_route_non_aliased_resolves` | PASS |
| Fail-closed preserved for unknown keys | `test_skill_route_unknown_still_raises` | PASS |
| No skill → no system prompt | `test_skill_route_none_returns_none` | PASS |

## Verification Evidence

Repo venv `groundtruth-kb/.venv/Scripts/python.exe`:
- `python -m pytest platform_tests/scripts/test_cursor_harness.py -q` → `5 passed in 0.19s`.
- `python -m ruff check scripts/cursor_harness.py platform_tests/scripts/test_cursor_harness.py` → `All checks passed!`.
- `python -m ruff format --check` on both files → `2 files already formatted`.
- The alias targets are verified against the real `.cursor/skills` tree (`proposal-review/SKILL.md` 2230 B, `verify/SKILL.md` 11432 B exist), so the tests assert resolution to existing contracts. Live confirmation: resetting the `loyal-opposition:E` circuit breaker and a fresh headless LO dispatch should no longer emit `unknown skill route`.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is that a dispatched Loyal Opposition worker resolve a valid skill contract for its bridge route rather than failing closed. DELIB-20266209 authorizes the fix and the alias approach. No new requirement.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4872-CURSOR-HARNESS-SKILL-ROUTE` (active; includes WI-4872 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266209`). The owner selected "Fix cursor_harness route now" via AskUserQuestion (S20260627). No additional owner decision is required for this report.

## Prior Deliberations

- `DELIB-20266209` — owner AUQ (S20260627): "Fix cursor_harness route now"; specifies the alias approach.
- `DELIB-20266203` — autonomous-loop plan; this fix restores the headless LO path (PHASE Y prerequisite).
- `bridge/gtkb-wi4872-cursor-harness-lo-skill-route-alias-001.md` (NEW proposal), `-002.md` (Cursor LO GO).

## Risk / Rollback

- Risk: aliasing maps the canonical LO keys to the review/verify skills; if those directories are renamed the alias breaks. Mitigated: the regression tests assert resolution to existing contracts, so a rename surfaces as a test failure. Only the two known LO keys are aliased; all other unknown keys still fail closed.
- Rollback: single-commit revert removes the alias map and the one-line resolution. No KB mutation.

## Recommended Commit Type

`fix` — repairs headless LO dispatch failing closed on an unresolvable skill route. No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
