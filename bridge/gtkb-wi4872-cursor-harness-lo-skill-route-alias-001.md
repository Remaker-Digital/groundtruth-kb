NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: d5a77c21-caee-404a-8fb3-6629ba276960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-wi4872-cursor-harness-lo-skill-route-alias — Resolve LO bridge skill-route keys to real skill directories so headless Cursor LO dispatch stops failing closed

Document: gtkb-wi4872-cursor-harness-lo-skill-route-alias
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4872
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4872-CURSOR-HARNESS-SKILL-ROUTE
Recommended commit type: fix

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Every headless Cursor Loyal Opposition dispatch dies immediately with `cursor_harness: unknown skill route 'bridge-review'; no SKILL.md found`, tripping the `loyal-opposition:E` dispatch circuit breaker. The autonomous loop's headless LO review/verify path is therefore non-functional; only Cursor's interactive auto-process performs LO work, on a slow cadence. This blocks PHASE Y's zero-touch headless requirement and throttles X4 (WI-4856) verification and X5 (WI-4857) review.

Root cause: `harness-state/harness-registry.json` Cursor (E) invocation surfaces pass `--skill bridge-review`. `scripts/cursor_harness.py` `_skill_system_prompt` resolves the `--skill` value to `.cursor/skills/<skill>/SKILL.md` (then `.codex`, `.claude`) and raises `CursorHarnessError` (exit 1) when none exists. No `bridge-review` (nor `verification`) SKILL.md exists — the real Loyal Opposition skill directories are `proposal-review` (proposal review) and `verify` (verification). The keys `bridge-review`/`verification` are the canonical cross-harness LO route convention (`LOYAL_OPPOSITION_BRIDGE_SKILLS`, also referenced by `openrouter_harness.py` / `ollama_harness.py`), but they have no backing SKILL.md.

### Behavior change (precise)

In `scripts/cursor_harness.py`, add a skill-route alias map and apply it at the top of `_skill_system_prompt`:

```
_SKILL_ROUTE_ALIASES = {"bridge-review": "proposal-review", "verification": "verify"}
```

`_skill_system_prompt(skill)` resolves `skill = _SKILL_ROUTE_ALIASES.get(skill, skill)` before the SKILL.md lookup. `bridge-review` → `.cursor/skills/proposal-review/SKILL.md` (confirmed present, 2230 B); `verification` → `.cursor/skills/verify/SKILL.md` (confirmed present, 11432 B). Non-aliased keys (e.g. `proposal-review`, `verify`, `bridge`) resolve unchanged. Genuinely unknown keys still raise `CursorHarnessError` (fail-closed preserved). No change to the harness registry, the resolution fallback order, dispatch selection, or worker spawning.

### Scope note

Only Cursor (E) is an active LO dispatch target (`dispatchable=True`); `openrouter` (F) and `ollama` (D) are non-dispatchable and carry the same latent missing-SKILL.md issue via their own `LOYAL_OPPOSITION_BRIDGE_SKILLS` checks. Fixing them (or creating canonical `bridge-review`/`verification` SKILL.md files) is a noted follow-on, out of this bounded WI per the owner-approved scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next append-only numbered bridge file.
- `GOV-17` — Automation script modification approval gate; modifies the Cursor harness automation shim; owner-authorized (DELIB-20266209, PAUTH cited).
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher harness-isolation architecture; headless LO dispatch resolving a valid skill contract is part of the dispatch substrate's operability.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites governing specs; tests mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — WI-4872 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — alias behavior maps to derived tests.
- `GOV-STANDING-BACKLOG-001` — WI-4872 is an authorized standing-backlog item under the active project.

## Prior Deliberations

- `DELIB-20266209` — owner AUQ (S20260627): "Fix cursor_harness route now"; authorizes this bounded WI to restore headless LO dispatch; specifies the alias approach in `cursor_harness.py`.
- `DELIB-20266203` — autonomous-loop plan whose stated goal is a functioning headless PB/LO loop; this defect blocks that goal (PHASE Y prerequisite).
- WI-4818 — prior Cursor-harness coverage work (storm-watchdog), a related cursor_harness drift class.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4872-CURSOR-HARNESS-SKILL-ROUTE` (active; includes WI-4872 + GOV-17 + ADR-DISPATCHER-ARCHITECTURE-001; cites `DELIB-20266209`). The owner selected "Fix cursor_harness route now" via AskUserQuestion (S20260627), authorizing this bounded skill-route fix. No additional owner decision is required for this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is that a dispatched Loyal Opposition worker resolve a valid skill contract for its bridge route rather than failing closed. DELIB-20266209 authorizes the fix and the alias approach. No new requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| WI-4872: `bridge-review` resolves to the real LO review contract | `test_skill_route_alias_bridge_review_resolves` (new) | `_skill_system_prompt("bridge-review")` returns non-None content containing the `proposal-review` skill name (no `CursorHarnessError`). |
| WI-4872: `verification` resolves to the real verify contract | `test_skill_route_alias_verification_resolves` (new) | `_skill_system_prompt("verification")` returns non-None content containing the `verify` skill name. |
| Non-aliased keys resolve unchanged | `test_skill_route_non_aliased_resolves` (new) | `_skill_system_prompt("proposal-review")` returns non-None content. |
| Fail-closed preserved for unknown keys | `test_skill_route_unknown_still_raises` (new) | `_skill_system_prompt("definitely-not-a-skill")` raises `CursorHarnessError`. |
| No skill → no system prompt | `test_skill_route_none_returns_none` (new) | `_skill_system_prompt(None)` returns `None`. |

Commands (pre-report): targeted `pytest` over `platform_tests/scripts/test_cursor_harness.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed files. The alias targets are verified against the real `.cursor/skills` directories (the bug was a missing real target, so the test asserts the alias points at an existing contract). Post-fix live confirmation: a fresh headless LO dispatch no longer emits the `unknown skill route` error.

## Risk / Rollback

- **Risk:** aliasing maps the canonical LO keys to the review/verify skills; if those skill directories are renamed, the alias breaks. Mitigated: the regression tests assert the alias resolves to existing contracts, so a rename surfaces as a test failure.
- **Risk:** masking a genuinely-unknown skill. Mitigated: only the two known LO keys are aliased; all other unknown keys still fail closed (`CursorHarnessError`).
- **Rollback:** single-commit revert removes the alias map and the one-line resolution. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs headless LO dispatch failing closed on an unresolvable skill route. No new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
