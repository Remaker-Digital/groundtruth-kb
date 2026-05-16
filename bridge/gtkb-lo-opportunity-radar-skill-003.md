NEW

# GT-KB Skill: `lo-opportunity-radar` — Post-Implementation Report (003)

**Status:** NEW (post-implementation report — awaiting VERIFIED)
**Author:** Prime Builder (claude, harness B)
**Date:** 2026-05-15
**Session:** S353
**Thread:** gtkb-lo-opportunity-radar-skill
**Implements:** bridge/gtkb-lo-opportunity-radar-skill-001.md (GO at -002)

Project Authorization: PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE
Project: PROJECT-GTKB-LO-OPPORTUNITY-RADAR
Work Item: WI-3324
target_paths: [".claude/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/lo-opportunity-radar/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "tests/skills/test_lo_opportunity_radar_skill.py"]

**Governing spec:** SPEC-LO-OPPORTUNITY-RADAR-001

## Summary

The GO'd `-001` proposal is implemented. The `lo-opportunity-radar` skill — the
first-slice scope of `SPEC-LO-OPPORTUNITY-RADAR-001` — is created as a canonical
Claude skill with a generated Codex parity adapter, a harness-capability
registry entry, and six spec-derived tests. No scanner, CLI, or hook surface
was added; the scope boundary in the spec is respected.

## Implementation performed

1. Authored `.claude/skills/lo-opportunity-radar/SKILL.md` — frontmatter
   (`name`, `description`, `allowed-tools`) plus a body presenting the
   five-pass review posture (`## The radar passes`: Defect pass, Token-savings
   pass, Deterministic-service pass, Surface-eligibility pass, Routing pass),
   an `## Output discipline` section, and a `## Scope` section recording the
   deferred scanner/CLI/hooks.
2. Added the `[[capabilities]]` entry `skill.lo-opportunity-radar` to
   `config/agent-control/harness-capability-registry.toml`
   (`required_for_roles = ["loyal-opposition"]`, `parity_class = "baseline"`).
3. Ran `python scripts/generate_codex_skill_adapters.py --update-registry`,
   which generated `.codex/skills/lo-opportunity-radar/SKILL.md`, updated
   `.codex/skills/MANIFEST.json`, and filled the registry `source_sha256`.
4. Added `tests/skills/test_lo_opportunity_radar_skill.py` — six spec-derived
   structural and parity tests.

## Files changed

- `.claude/skills/lo-opportunity-radar/SKILL.md` — new canonical skill.
- `.codex/skills/lo-opportunity-radar/SKILL.md` — generated Codex adapter.
- `.codex/skills/MANIFEST.json` — adapter inventory updated by the generator.
- `config/agent-control/harness-capability-registry.toml` — new loyal-opposition skill capability entry.
- `tests/skills/test_lo_opportunity_radar_skill.py` — new spec-derived tests.

All changes are within the GO'd `target_paths`.

## Specification Links

- SPEC-LO-OPPORTUNITY-RADAR-001 — the governing requirement; this report implements its first-slice scope (the skill).
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — work bounded by PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Claude / Codex parity; the generated Codex adapter satisfies it.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — the skill is a GT-KB platform artifact under `.claude/skills/`.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol authority governing this report.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — every relevant governing spec is cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification evidence below maps every behavior clause to an executed test.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — satisfied by the Project Authorization / Project / Work Item header lines.
- DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 — WI-3324 is a member of PROJECT-GTKB-LO-OPPORTUNITY-RADAR under an active authorization.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — work captured as governed artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — the SPEC, project, WI, and bridge thread form the artifact graph.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the LO advisory triggered the WI, the spec, and this implementation.

## Spec-Derived Verification Evidence

Commands executed and observed results:

```
python -m pytest tests/skills/test_lo_opportunity_radar_skill.py -q
  -> 6 passed in 0.18s

python scripts/generate_codex_skill_adapters.py --check
  -> Codex skill adapters: PASS (31 adapters current)

python -m ruff check tests/skills/test_lo_opportunity_radar_skill.py
  -> All checks passed!

python -m ruff format --check tests/skills/test_lo_opportunity_radar_skill.py
  -> 1 file already formatted
```

Spec-to-test mapping (`SPEC-LO-OPPORTUNITY-RADAR-001`):

| Test | Behavior clause covered |
|---|---|
| `test_skill_file_exists_with_valid_frontmatter` | "delivered as a canonical skill" — the skill file exists with valid `name`/`description` frontmatter. |
| `test_skill_body_declares_five_passes` | The five-pass review structure (defect / token-savings / deterministic-service / surface-eligibility / routing). |
| `test_routing_pass_routes_through_advisory_router` | Routing pass — material findings route through the existing advisory-router. |
| `test_codex_adapter_parity` | ADR-CODEX-HOOK-PARITY-FALLBACK-001 — the Codex adapter mirrors the canonical skill (name + five passes). |
| `test_registry_marks_skill_loyal_opposition_relevant` | "biases Loyal Opposition" — the skill is registered `required_for_roles` loyal-opposition. |
| `test_registry_declares_both_harness_surfaces` | Cross-harness delivery — both the Claude native surface and the Codex adapter surface are declared and present. |

Every behavior clause of `SPEC-LO-OPPORTUNITY-RADAR-001`'s first-slice scope is
covered by an executed test; all six tests pass.

## Acceptance Criteria Check

1. `.claude/skills/lo-opportunity-radar/SKILL.md` exists with valid frontmatter and the five-pass body — PASS.
2. The Codex adapter and `MANIFEST.json` are regenerated and consistent; `generate_codex_skill_adapters.py --check` is clean — PASS.
3. The skill is registered loyal-opposition-relevant in the capability registry — PASS.
4. All tests pass; ruff check and ruff format --check are clean — PASS.
5. No scanner, CLI, or hook surface was added — PASS (scope boundary respected).

## Owner Decisions / Input

This work was authorized by the AskUserQuestion decisions captured this session
and archived as `DELIB-S353-LO-OPPORTUNITY-RADAR-DISPOSITION-2026-05-15`:

1. Disposition — owner selected "Pursue skill-only first slice".
2. Specification — owner approved `SPEC-LO-OPPORTUNITY-RADAR-001` as written.
3. Project + authorization — owner approved `PROJECT-GTKB-LO-OPPORTUNITY-RADAR`
   and `PAUTH-PROJECT-GTKB-LO-OPPORTUNITY-RADAR-SKILL-FIRST-SLICE` as written.
4. Owner directed proceeding to implementation ("I approve both, please
   proceed").

## Recommended Commit Type

`feat:` — adds a new skill, a net-new capability surface, not a repair or a
maintenance-only change.

## Risk / rollback

- The skill is guidance content; it adds no executable path. Blast radius is
  limited to Loyal Opposition review behavior.
- Rollback: remove `.claude/skills/lo-opportunity-radar/`,
  `.codex/skills/lo-opportunity-radar/`, the registry capability entry, and the
  test file, then re-run `generate_codex_skill_adapters.py --update-registry`
  to restore `MANIFEST.json`.

## Verification Request

Loyal Opposition: please verify the implementation against
`SPEC-LO-OPPORTUNITY-RADAR-001`, confirm the spec-to-test mapping above, and
re-run the listed commands. Issue VERIFIED if the first-slice scope is
satisfied, or NO-GO with specific findings.
