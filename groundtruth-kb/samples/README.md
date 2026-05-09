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

## Convention

Subdirectory names use `dot-claude` / `dot-codex` placeholders instead of
`.claude` / `.codex`. The latter are gitignored at the GT-KB repo root and
cannot be tracked here. Adopters rename `dot-claude` → `.claude` (etc.) at
copy time.

## Usage

Copy the appropriate sample to your project root, renaming the directory:

```bash
# Claude Code
cp groundtruth-kb/samples/claude/dot-claude/settings-bridge-poller.json .claude/settings.json

# Codex
cp groundtruth-kb/samples/codex/dot-codex/hooks-bridge-poller.json .codex/hooks.json
```

If your project already has a `settings.json` / `hooks.json`, merge the
`hooks` block manually rather than overwriting.

## Codex verification warning

The Codex sample carries a top-level `_verification_warning` referencing
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Per that ADR, Codex hooks are
forward-compatible intent on Windows but not currently active there.
Mechanical adapter parity is verified by `scripts/check_codex_hook_parity.py`
until Windows hooks are live. The warning is metadata only; consumer hook
loaders ignore unknown `_`-prefixed fields.

## What the hook does

The shipped command invokes the GT-KB bridge poller registry CLI:

```text
python -m groundtruth_kb.bridge.registry register --harness-kind <kind>
```

This writes a static registration record at
`<project_root>/.gtkb-state/bridge-poller/registry/<harness_id>.json`
capturing the harness kind, workspace root, active role, recording PIDs
(diagnostic-only — NOT the harness PID), and the default invoke-command
template. Records are NOT live/stale-classified; consumers must NOT treat
them as authoritative for liveness.

See `bridge/gtkb-bridge-poller-p2-registry-005.md` (REVISED-2 GO at -006)
for the full design contract.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
