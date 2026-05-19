# `.antigravity/` - GT-KB Integration Directory for the Antigravity Harness

This directory is GT-KB's in-root harness-integration directory for the
**Antigravity** AI coding harness (harness identity **C**, `loyal-opposition`
role). It is the harness-C analogue of `.codex/` and `.claude/`.

Created by WI-3346 (bridge thread `gtkb-antigravity-integration-directory`)
under `PROJECT-ANTIGRAVITY-INTEGRATION` / `PROJECT-ANTIGRAVITY-ONBOARDING`
(owner decisions DELIB-2079, DELIB-2080, DELIB-2081).

## No hooks - by design

There is intentionally **no `hooks.json`** in this directory. The WI-3345
research spike (`DOC-ANTIGRAVITY-IDE-RESEARCH-001`, determined-with-evidence)
found that the Antigravity IDE exposes **no hook event surface at all** - no
`SessionStart`, `PostToolUse`, or `Stop` event, and no hook-registration
configuration file. This is the categorical current state of the harness, not
a version-gated condition.

Consequently, harness C **cannot** host the cross-harness event-driven trigger
(`scripts/cross_harness_bridge_trigger.py`), which depends on `PostToolUse` and
`Stop` hooks. Per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3, harness C's standing
bridge-dispatch substrate is the **interval-driven single-harness bridge
dispatcher / host-scheduled-task model** (`ADR-SINGLE-HARNESS-OPERATING-MODE-001`,
`SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`), invoking the Antigravity headless
surface `gemini -p "<prompt>" --approval-mode=yolo`. For harness C this fallback
is the permanent, correct dispatch model - not a degraded mode.

## In-root vs harness-installation config

This `.antigravity/` directory, under the GT-KB project root, is the **GT-KB
integration directory** - a GT-KB artifact under
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`. The Antigravity harness *installation*
maintains its own separate user-profile configuration directory outside the
project root; that directory belongs to the harness installation and is **not**
a GT-KB artifact.

## Files

- `config.toml` - the GT-KB integration config: harness identity, intended
  role, invocation surfaces (interactive IDE and headless Gemini CLI), and the
  dispatch model.

Antigravity's native agent-automation surfaces (`.agent/rules/` auto-loaded
context, `.agent/skills/<name>/SKILL.md` capability adapters) are populated by
later onboarding slices, not by WI-3346.

## Onboarding status

WI-3346 creates this integration directory and the
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 record. The remaining onboarding:

- **WI-3347** - LO-role-scoped capability adapters in `.agent/skills/`.
- **WI-3348** - register the Antigravity harness (identity C) in the MemBase
  harness registry via `gt harness register`.
- **WI-3349** - end-to-end verification of headless Gemini CLI loyal-opposition
  review dispatch.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
