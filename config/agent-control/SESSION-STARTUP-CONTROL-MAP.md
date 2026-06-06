<!--
GTKB-STARTUP-REFRACTOR-001 Slice A (WI-4268). Role-neutral single source-of-truth
inventory of session-startup control surfaces. Authority:
GOV-SESSION-SELF-INITIALIZATION-001; DCL-SESSION-STARTUP-TOKEN-BUDGET-001;
bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md (GO).
Covers advisory STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02 findings F2
(single inventory) and F9-classify (every surface classified). This artifact is
classify-only: no surface is deleted, relocated, or retired here (advisory F9
deletion remains a separately owner-gated follow-on).
-->

# Session Startup Control Map

The single role-neutral inventory of the control surfaces that participate in
GroundTruth-KB session startup. It supersedes the scattered, drifted views in
`config/agent-control/CONTROL-MAP.md` and `config/agent-control/REVIEW-MODE-SETUP.md`
as the authoritative startup-surface list (advisory F2). Each surface carries a
lifecycle classification (advisory F9-classify).

Capability detail (skills, agents, commands, plugin/MCP assumptions) lives in the
companion `config/agent-control/ROLE-CAPABILITY-MANIFEST.md` so this map stays
focused on *which surfaces load at startup* rather than *what each capability is*.

## Lifecycle Classifications

Every inventory row below is tagged with exactly one of these lifecycle states:

- **active** — currently load-bearing at session start; trusted and maintained.
- **deprecated** — still present on disk and discoverable, but superseded; must
  not be relied on as the current path. Retained for provenance/compatibility.
- **archive** — moved to an archive location for historical reference only; not a
  live dependency.
- **generated** — produced by a generator from an authoritative source; never
  hand-edited; regenerated rather than maintained.

## Required Startup Files (role-neutral)

The minimum load-bearing set both Prime Builder and Loyal Opposition resolve at
session start.

<!-- inventory -->
| Surface | Path | Classification | Notes |
|---|---|---|---|
| Platform rules & behavior | `CLAUDE.md` | active | Top-level platform guidance; GOV-01 ≤300-line cap. |
| Loyal Opposition / cross-harness rules | `AGENTS.md` | active | Codex-side startup contract; durable-role disclosure. |
| Canonical glossary | `.claude/rules/canonical-terminology.md` | active | Loaded explicitly in both roles (F1, VERIFIED); DA read-surface. |
| Durable operating-role guidance | `.claude/rules/operating-role.md` | active | Human-readable role-resolution guidance; not the role record. |
| File-bridge protocol | `.claude/rules/file-bridge-protocol.md` | active | Bridge statuses, gates, claim/preflight contract. |
| Deliberation protocol | `.claude/rules/deliberation-protocol.md` | active | When to search/archive deliberations. |
| Generated startup service | `scripts/session_self_initialization.py` | active | Emits the startup disclosure payload (its output is generated). |
| Operational notepad | `memory/MEMORY.md` | active | Session state/bootstrap; ADR-0001 notepad tier (not canonical). |
<!-- /inventory -->

## Role-Specific Overlays

Planned (not yet present): `SESSION-STARTUP-INDEX.md` + Prime Builder / Loyal
Opposition overlays are created in Slice C (F4/F7). They are intentionally NOT
inventoried as live rows here because they do not yet exist; this section is the
placeholder the Slice C proposal will populate.

## Generated & Projected Surfaces

<!-- inventory -->
| Surface | Path | Classification | Notes |
|---|---|---|---|
| Harness registry projection | `harness-state/harness-registry.json` | generated | DB-projected hot-path role/identity surface; regenerate via `groundtruth_kb.harness_projection`. |
| Cached startup payload | `.gtkb-state/startup/*` | generated | SessionStart-cached disclosure for lazy init-keyword rendering. |
| Generated dashboard surfaces | `docs/gtkb-dashboard/` | generated | Rendered dashboard artifacts; not authoritative state. |
<!-- /inventory -->

## Settings & Hook Surfaces

<!-- inventory -->
| Surface | Path | Classification | Notes |
|---|---|---|---|
| Tracked Claude settings | `.claude/settings.json` | active | Hook registrations (SessionStart, PreToolUse, Stop, PostToolUse). |
| Machine-local Claude settings | `.claude/settings.local.json` | active | Local-only permissions overlay; hygiene is Slice B (F3). |
| Codex hooks | `.codex/hooks.json` | active | Codex-side hook parity registrations. |
| Claude SessionStart hook | `.claude/hooks/session_start_dispatch.py` | active | Startup dispatch + init-keyword routing (Slice D de-dup target). |
| Codex SessionStart hook | `.codex/gtkb-hooks/session_start_dispatch.py` | active | Codex-side mirror (Slice D de-dup target). |
<!-- /inventory -->

## Capability Surfaces (see role-capability manifest)

<!-- inventory -->
| Surface | Path | Classification | Notes |
|---|---|---|---|
| Skills | `.claude/skills/*/SKILL.md` | active | ~35 repo skills; role grouping in ROLE-CAPABILITY-MANIFEST.md. |
| Agents | `.claude/agents/*.md` | active | `code-reviewer`, `security-analyzer`. |
| Commands | `.claude/commands/*.md` | active | `check-db`, `check-security`, `open-items`, `preflight`, `quick-review`, `refresh-creds`. |
| Control map (legacy) | `config/agent-control/CONTROL-MAP.md` | deprecated | Superseded by this file as the startup-surface inventory (F2). |
| Review-mode setup (legacy) | `config/agent-control/REVIEW-MODE-SETUP.md` | deprecated | Stale Phase-B startup list; superseded by this file (F2). |
<!-- /inventory -->

## Retired / Legacy Surfaces (classify-only)

Discoverable on disk but must not be revived or relied on. Listed for awareness
per advisory F9; deletion is a separately owner-gated follow-on (NOT this slice).

<!-- inventory -->
| Surface | Path | Classification | Notes |
|---|---|---|---|
| Smart-poller bridge-poller template | `.claude/rules/bridge-poller-canonical.md` | deprecated | DEPRECATED stub; smart poller retired 2026-05-09. |
| Legacy OS-poller setup prompt | `templates/bridge-os-poller-setup-prompt.md` | deprecated | Legacy "OS poller" framing; the retired OS poller must not be restored. |
| Smart-poller runtime archive | `archive/smart-poller-2026-05-09/` | archive | Archived VBS daemon / runner / install scripts; historical only. |
<!-- /inventory -->

## Plugin / MCP Assumptions

Codex app plugins and MCP servers available at runtime (Browser, GitHub,
Documents, Presentations, Spreadsheets; various MCP servers) are session-runtime
capabilities, not repo-tracked startup surfaces. They are recorded in
`config/agent-control/ROLE-CAPABILITY-MANIFEST.md` under shared/owner-gated
capabilities so startup can answer "which capabilities are expected to work" per
advisory F8.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
