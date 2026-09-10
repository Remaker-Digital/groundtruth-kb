# Bridge Hook Samples (Smart-Poller Register Stub — RETIRED)

> **RETIRED (2026-05-09):** The smart-poller mechanism that consumed the
> `register` SessionStart hook in these samples was retired in favor of the
> cross-harness event-driven trigger
> (`scripts/cross_harness_bridge_trigger.py`) registered in
> `.claude/settings.json` and `.codex/hooks.json`. The trigger is scaffolded
> automatically by `gt project init --profile dual-agent`. These samples are
> retained for two release cycles for adopter compatibility; do not start a
> new installation from them. See `docs/tutorials/dual-agent-setup.md`.

These are starter hook configurations for adopter projects that previously
ran the smart-poller `register` SessionStart hook in Claude Code or Codex.

## Current configuration

These poller samples are inert historical examples and must not be installed.
Use the canonical harness baseline and projector for new configuration. Inspect
`gt harness project --help` for the supported projection interface, then verify
the selected target through `scripts/check_harness_parity.py --harness <name>`.
That command checks installed derivation; qualify actual native hook execution
separately before relying on an interception boundary.
