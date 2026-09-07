---
name: gtkb-harness-parity-review
description: Use when reviewing or correcting parity across GT-KB harnesses (Claude, Codex, Cursor, Antigravity, Ollama, OpenRouter), including skills, hooks, roles, commands, plugins, MCP tools, startup context, permissions, role-specific capabilities, or harness capability drift.
---
<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project antigravity`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Harness Parity Review

## Goal

Ensure each **active** harness assigned a GT-KB operating role has the capabilities
required for that role. Parity means semantic capability equivalence, not
byte-for-byte identical files.

Phase 1 (`scripts/check_harness_parity.py`) is a **static catalog drift** checker:
registry rows, declared surfaces, generated skill adapters, and typed waivers. It does
**not** prove hook registration, invocation, or runtime enforcement. Phase 2
(`scripts/harness_parity_phase2.py`) is closer to **operational readiness** and
complements phase 1; use both when judging role fitness.

## Required Inputs

Read:

- `harness-state/harness-registry.json` — durable harness IDs, status, and role sets
- `config/agent-control/harness-capability-registry.toml` — capability matrix + `[[parity_waivers]]`
- `.harness-baseline-configuration/skills/*/SKILL.md` — canonical project skills
- Harness-specific surfaces as needed:
  - Claude: `settings.json`, `.harness-baseline-configuration/hooks/`
  - Codex: `hooks.json`, `config.toml`, `gtkb-hooks/`
  - Cursor: `.cursor/hooks.json`, `.harness-baseline-configuration/skills/`
  - Antigravity: Antigravity skills directory
  - Ollama / OpenRouter: API harness skills directory, provider wrappers

## Workflow

1. Resolve durable harness IDs and **assigned roles** from `harness-registry.json`.
2. Read the harness capability registry (including waivers and applicability).
3. Inventory declared surfaces per harness; do not assume cross-harness file reuse
   implies invocation (API/provider harnesses must not PASS on Claude/Codex hook paths
   they do not wire).
4. Compare phase-1 catalog parity with applicability-aware populations:
   role-relative capabilities are checked against active harnesses assigned the
   requested role; universal capabilities are checked against the active selected
   population because they are not proof of one role alone.
5. Classify each capability:
   - `PASS`: equivalent capability is available natively or adapter hash matches
   - `DEGRADED`: documented fallback exists but is not native
   - `MISSING`: required capability is absent and not waived
   - `STALE`: adapter or mirror differs from canonical source
   - `EXTRA`: harness has undeclared capability
   - `UNSUPPORTED`: known non-equivalence is explicitly documented or owner-approved waiver
   - `OWNER_ACTION_REQUIRED`: install, auth, external setup, or deliberate-deferral waiver
6. Correct safe drift by updating registry entries, pointers, adapters, or reports.
7. Escalate owner action only for required installs/auth/setup.
8. Verify with both phase-1 catalog parity and phase-2 operational readiness
   before making a role-fitness claim. Discovery-diff applies only where a
   harness declares an actual hook config; API/provider harness readiness must
   come from phase-2 or later coverage-audit evidence, not Claude/Codex hook files.

## Commands

Phase 1 — catalog parity:

```powershell
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
python scripts/check_harness_parity.py --harness cursor --role prime-builder --json
python scripts/check_harness_parity.py --harness ollama --role loyal-opposition --show-pass
python scripts/check_harness_parity.py --validate-schema
python -m pytest platform_tests/scripts/test_check_harness_parity.py -q
```

Fleet role coverage is a computed phase-1 row. It proves that at least one
active harness assigned each operating role has no unwaived required
role-relative blocker; it does not prove hook invocation or end-to-end dispatch.

Phase 2 — operational readiness (complementary):

```powershell
python scripts/harness_parity_phase2.py --project-root . --format markdown
```

Hook discovery diff (Claude/Codex hook configs):

```powershell
python scripts/parity_discovery_diff.py --project-root . --markdown
```

## Rules

- Do not assume baseline skills are directly executable in other harnesses without projection or adaptation.
- Do not assume Codex plugin skills are available to Claude Code.
- Skill adapter manifests do **not** prove hook parity for API/provider harnesses.
- Missing role-critical capability blocks normal role work unless the registry marks an
  accepted fallback, `unsupported`, or an approved typed waiver.
- Historical or harness-specific capabilities must be explicitly labeled.
- Undeclared extras are drift until classified.
- After editing this canonical skill, regenerate adapters:
  `python scripts/generate_codex_skill_adapters.py --update-registry`
  `python scripts/generate_antigravity_skill_adapters.py --update-registry`
  `python scripts/generate_api_skill_adapters.py`

## Report Format

Include:

- overall status
- role/harness checked
- missing role-critical capabilities
- degraded fallbacks
- stale adapters
- waived unsupported surfaces
- undeclared extras
- recommended corrections
- verification command output (phase 1 and, when relevant, phase 2)

## Generator Inventory

| Harness | Generator Script | Adapter Surface |
|---|---|---|
| Claude Code | (canonical source — no generator needed) | `.harness-baseline-configuration/skills/` |
| Codex | `scripts/generate_codex_skill_adapters.py` | `.harness-baseline-configuration/skills/` |
| Antigravity | **No generator** — inline loading | N/A |
| Cursor | `scripts/generate_cursor_skill_adapters.py` | `.cursor/skills/` |
| Goose | **No generator** — inline loading | N/A |
| OpenRouter | **No generator** — inline loading | N/A |

When a harness declares capabilities in `config/agent-control/harness-capability-registry.toml` but has no generator script, flag it as a **generator gap** — adapter regeneration is not possible for that harness, and skill changes must be manually synced.

<!--
GTKB-ANTIGRAVITY-SKILL-ADAPTER-BEGIN
Generated by: scripts/harness_projection/project_harness.py
Generated at: content-addressed 7944f7241aeb
Canonical source: .harness-baseline-configuration/skills/gtkb-harness-parity-review/SKILL.md
Canonical source sha256: 7944f7241aeb1f9444774339ad8ef61feea615da7fbd6f4e40323dba5026d501
GTKB-ANTIGRAVITY-SKILL-ADAPTER-END
-->
