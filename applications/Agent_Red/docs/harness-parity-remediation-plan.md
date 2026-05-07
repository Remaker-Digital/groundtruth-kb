# Harness Parity Remediation Plan

Date: 2026-05-06

## Purpose

Claude Code and Codex should behave identically wherever GT-KB relies on
shared governance, role duties, project vocabulary, bridge use, backlog access,
review methods, safety gates, and skill workflows.

Parity does not mean disabling harness-specific strengths. A harness may keep
additional tools, plugins, MCP integrations, or model-specific capabilities as
long as those enhancements are declared and do not change required governance
semantics.

## Parity Classes

- `required`: role-critical capabilities that must be present for the assigned
  role.
- `baseline`: expected project capabilities that should be available to both
  harnesses but are not always role-blocking.
- `owner-gated`: capabilities whose instructions can be available while actual
  execution remains owner-gated, such as deployment.
- `enhancement`: harness-specific strengths that are allowed and encouraged,
  but must not override shared behavior.
- `unsupported`: known non-equivalence that is explicitly accepted.

## Target State

- Required capabilities are `PASS` for both harnesses wherever technically
  possible.
- Fallbacks are temporary, visible, and tied to a remediation item.
- Extras are declared as enhancements or removed.
- Unsupported items are rare, documented, and reviewed.
- Session startup surfaces parity status for the active harness and role.
- Role changes and capability-source changes trigger parity review.

## Execution Plan

1. Keep `config/agent-control/harness-capability-registry.toml` as the
   canonical semantic capability registry.
2. Generate Codex skill adapters from the current canonical project skills in
   `.claude/skills/*/SKILL.md`.
3. Embed canonical source paths and source hashes in generated adapters.
4. Update registry Codex skill entries from `fallback` to generated adapter
   surfaces when the adapter exists and matches the canonical source.
5. Extend `scripts/check_harness_parity.py` to report generated adapters as:
   - `PASS` when the adapter exists and source hash matches;
   - `STALE` when the source hash differs;
   - `MISSING` when source or adapter is absent.
6. Add tests for generated-adapter pass/stale/missing behavior.
7. Re-run parity until required skill parity is clean.
8. In a later slice, wire parity checks into session-start, role-change,
   capability-change, and release-gate events.
9. In a later structural hygiene slice, decide whether to keep `.claude/skills`
   as the long-term canonical authoring location or move to a neutral project
   path and generate both Claude and Codex adapters from that source.

## Non-Inhibition Rule

Harness-specific capabilities are not removed solely for parity. They are
classified and constrained:

- They may improve execution quality or efficiency.
- They may not redefine role authority.
- They may not bypass bridge, backlog, glossary, credential, release, or owner
  approval rules.
- They must be documented as enhancements when they matter to agent behavior.

## Verification

The required baseline commands are:

```powershell
python scripts/generate_codex_skill_adapters.py --check
python scripts/check_harness_parity.py --all --markdown
python -m pytest tests/scripts/test_check_harness_parity.py tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short
python -m ruff check scripts/check_harness_parity.py scripts/generate_codex_skill_adapters.py tests/scripts/test_check_harness_parity.py tests/scripts/test_generate_codex_skill_adapters.py
python -m ruff format --check scripts/check_harness_parity.py scripts/generate_codex_skill_adapters.py tests/scripts/test_check_harness_parity.py tests/scripts/test_generate_codex_skill_adapters.py
```

## Open Follow-Ups

- Add broader change-event parity checks for skill, hook, registry, and
  harness-state files outside the release-candidate gate.
- Extend the registry beyond skills to include hooks, startup context, bridge
  handling, backlog access, release gates, MCP/plugin surfaces, and declared
  harness enhancements.

## Execution Record

Initial execution completed on 2026-05-06:

- generated 25 Codex skill adapters under `.codex/skills/`;
- updated Codex skill capability entries in
  `config/agent-control/harness-capability-registry.toml` from fallback surfaces
  to generated adapter surfaces;
- added adapter source-hash validation and stale detection to
  `scripts/check_harness_parity.py`;
- added `scripts/generate_codex_skill_adapters.py --update-registry --check` as
  the repeatable drift check;
- surfaced harness parity status in session startup;
- surfaced role-scoped parity status after next-session role changes;
- added adapter and parity checks to the release-candidate Python gate.

Current executed result:

```powershell
python scripts/check_harness_parity.py --all --markdown
```

Result: `PASS`, with `PASS: 50` and no parity findings in the registered skill
surface.
