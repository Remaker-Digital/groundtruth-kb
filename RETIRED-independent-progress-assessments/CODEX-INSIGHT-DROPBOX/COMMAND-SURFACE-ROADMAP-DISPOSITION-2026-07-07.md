# Command-Surface Roadmap Disposition

- Roadmap: `GTKB-COMMAND-SURFACE`
- Source bridge: `bridge/gtkb-command-surface-003.md`
- Verified architecture closure: `bridge/gtkb-command-surface-006.md`
- Project: `PROJECT-HARNESS-PARITY-PHASE-2`
- Work item: `WI-4754`
- Project authorization: `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`

## Slice Disposition Table

| Slice | Title | Disposition | Child slice |
| --- | --- | --- | --- |
| `CS-2` | :: dispatcher hook, registry, suppression contract | `defer` | `GTKB-COMMAND-SURFACE-CS-2-DISPATCHER-HOOK` |
| `CS-2.5` | Session wrap clears command-audit state | `supersede` | `none` |
| `CS-3` | First command set | `needs_owner_decision` | `GTKB-COMMAND-SURFACE-CS-3-FIRST-COMMAND-SET` |
| `CS-4` | Dashboard cross-surface affordance | `defer` | `GTKB-COMMAND-SURFACE-CS-4-DASHBOARD-AFFORDANCE` |
| `CS-5+` | Macros and workflow scaffolds | `defer` | `GTKB-COMMAND-SURFACE-CS-5-WORKFLOW-MACROS` |
| `CS-6` | Codex parity | `supersede` | `none` |
| `CS-7` | Local-command audit and disposition | `retire` | `none` |

## Details

### CS-2 - :: dispatcher hook, registry, suppression contract

- Disposition: `defer`
- Child slice: `GTKB-COMMAND-SURFACE-CS-2-DISPATCHER-HOOK`
- PAUTH needed: `true`
- Bridge proposal needed: `true`
- Rationale: The corrected architecture is implementable, but a broad UserPromptSubmit command dispatcher would now overlap the shipped init-keyword and activity-envelope routing surfaces. Keep it as a future child slice only after a fresh owner decision confirms the generic dispatcher is still desirable.
- Harness parity disposition: Future work must prove Claude hook ordering, Codex fallback semantics, and Cursor/other harness non-hook behavior explicitly instead of assuming a shared native hook model.

Required target paths:

- `.claude/commands/registry.json`
- `.claude/hooks/command-dispatcher.py`
- `.claude/hooks/spec-classifier.py`
- `.claude/hooks/owner-decision-tracker.py`
- `.claude/settings.json`
- `.groundtruth/session/command-audit/`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

Required specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

### CS-2.5 - Session wrap clears command-audit state

- Disposition: `supersede`
- Child slice: `none`
- PAUTH needed: `false`
- Bridge proposal needed: `false`
- Rationale: The original cleanup concern is covered by the later wrap scanner/session artifact work and by treating command-audit as session-local runtime evidence. No standalone CS-2.5 implementation should proceed unless CS-2 itself is re-approved.
- Harness parity disposition: No harness-specific command runtime remains to equalize until CS-2 is revived.

Required target paths:

- none

Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Covered by:

- `bridge/gtkb-wrapup-enhancements-slice1-007.md`

### CS-3 - First command set

- Disposition: `needs_owner_decision`
- Child slice: `GTKB-COMMAND-SURFACE-CS-3-FIRST-COMMAND-SET`
- PAUTH needed: `true`
- Bridge proposal needed: `true`
- Rationale: The first command set mixes commands that are already covered (`::init`, `::wrap`) with optional future intent macros (`::spec`, `::decide`, `::question`, `::bridge`). A future child slice must split covered commands from new macros and get owner confirmation before adding runtime dispatch.
- Harness parity disposition: Any new macro must state whether it is a Claude hook command, a Codex prompt convention, a CLI affordance, or a cross-harness rule-only surface.

Required target paths:

- `.claude/commands/registry.json`
- `.claude/skills/spec-intake/SKILL.md`
- `.claude/skills/decision-capture/SKILL.md`
- `.claude/skills/kb-session-wrap/SKILL.md`
- `.claude/skills/bridge-propose/SKILL.md`
- `.claude/skills/proposal-review/SKILL.md`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

Required specs:

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`

Covered behaviours:

- ::init - covered by the current init-keyword startup contract; do not re-implement through a generic dispatcher.
- ::wrap - covered by kb-session-wrap and wrap-scan surfaces; keep a macro as optional future syntax only.

Owner decision needed:

- Confirm whether ::spec, ::decide, ::question, and ::bridge remain desirable as runtime macros after current skill, AUQ, and bridge helper workflows.

### CS-4 - Dashboard cross-surface affordance

- Disposition: `defer`
- Child slice: `GTKB-COMMAND-SURFACE-CS-4-DASHBOARD-AFFORDANCE`
- PAUTH needed: `true`
- Bridge proposal needed: `true`
- Rationale: Dashboard affordances remain potentially useful, but they should follow a fresh dashboard/product proposal after the command registry and runtime command model are confirmed.
- Harness parity disposition: Dashboard UX is harness-neutral and should not create harness-specific command behavior.

Required target paths:

- `docs/gtkb-dashboard/`
- `config/agent-control/command-surface.toml`
- `platform_tests/scripts/test_command_surface_disposition.py`

Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

### CS-5+ - Macros and workflow scaffolds

- Disposition: `defer`
- Child slice: `GTKB-COMMAND-SURFACE-CS-5-WORKFLOW-MACROS`
- PAUTH needed: `true`
- Bridge proposal needed: `true`
- Rationale: Macro/workflow scaffolds should be driven by observed owner workflows, not by the historical roadmap alone. Keep the category as an owner-discovered future slice.
- Harness parity disposition: Every macro must declare whether it is model-instruction-only, hook-routed, CLI-routed, or dashboard-routed before parity claims are made.

Required target paths:

- `.claude/commands/registry.json`
- `config/agent-control/command-surface.toml`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`

### CS-6 - Codex parity

- Disposition: `supersede`
- Child slice: `none`
- PAUTH needed: `false`
- Bridge proposal needed: `false`
- Rationale: Codex command parity is now governed by the broader Harness Parity Phase 2 surfaces. Do not revive a standalone CS-6 unless a future command dispatcher lands and creates a new Codex-specific gap.
- Harness parity disposition: Covered by Harness Parity Phase 2 typed parity checks and waiver mechanics; no separate command-surface parity slice is currently needed.

Required target paths:

- none

Required specs:

- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`

Covered by:

- `PROJECT-HARNESS-PARITY-PHASE-2`
- `scripts/harness_parity_phase2.py`

### CS-7 - Local-command audit and disposition

- Disposition: `retire`
- Child slice: `none`
- PAUTH needed: `false`
- Bridge proposal needed: `false`
- Rationale: The six local `.claude/commands/*.md` files are developer-local conveniences, not a GT-KB product surface. Retire this roadmap slice as live implementation work unless the owner later chooses to productize a specific local command.
- Harness parity disposition: Local slash commands are intentionally outside the tracked cross-harness product surface; they should not create release parity obligations.

Required target paths:

- none

Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Surviving Child Work

The following entries are not implementation approval. Each requires a fresh bridge proposal, PAUTH coverage, GO, implementation-start packet, report, and verification before mutation.

### GTKB-COMMAND-SURFACE-CS-2-DISPATCHER-HOOK

- Parent slice: `CS-2`
- Current disposition: `defer`
- Required target paths:

- `.claude/commands/registry.json`
- `.claude/hooks/command-dispatcher.py`
- `.claude/hooks/spec-classifier.py`
- `.claude/hooks/owner-decision-tracker.py`
- `.claude/settings.json`
- `.groundtruth/session/command-audit/`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

- Required specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

### GTKB-COMMAND-SURFACE-CS-3-FIRST-COMMAND-SET

- Parent slice: `CS-3`
- Current disposition: `needs_owner_decision`
- Required target paths:

- `.claude/commands/registry.json`
- `.claude/skills/spec-intake/SKILL.md`
- `.claude/skills/decision-capture/SKILL.md`
- `.claude/skills/kb-session-wrap/SKILL.md`
- `.claude/skills/bridge-propose/SKILL.md`
- `.claude/skills/proposal-review/SKILL.md`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

- Required specs:

- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`

### GTKB-COMMAND-SURFACE-CS-4-DASHBOARD-AFFORDANCE

- Parent slice: `CS-4`
- Current disposition: `defer`
- Required target paths:

- `docs/gtkb-dashboard/`
- `config/agent-control/command-surface.toml`
- `platform_tests/scripts/test_command_surface_disposition.py`

- Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

### GTKB-COMMAND-SURFACE-CS-5-WORKFLOW-MACROS

- Parent slice: `CS-5+`
- Current disposition: `defer`
- Required target paths:

- `.claude/commands/registry.json`
- `config/agent-control/command-surface.toml`
- `platform_tests/hooks/test_command_surface_dispatcher.py`

- Required specs:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
