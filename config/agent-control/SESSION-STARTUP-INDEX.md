<!--
GTKB-STARTUP-REFRACTOR-001 Slice C (WI-4271). Role-neutral startup index.
Authority: GOV-SESSION-SELF-INITIALIZATION-001; DCL-SESSION-STARTUP-TOKEN-BUDGET-001;
bridge/gtkb-startup-refractor-slice-c-startup-index-overlays-002.md (GO).
Covers advisory STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02 findings F4
(duplicated startup content) and F7 (no compact role-neutral startup load list).
Companion surfaces: config/agent-control/SESSION-STARTUP-CONTROL-MAP.md (Slice A,
surface inventory), PRIME-BUILDER-STARTUP-OVERLAY.md, LOYAL-OPPOSITION-STARTUP-OVERLAY.md.
-->

# Session Startup Index

The short, role-neutral canonical statement of *what loads at session start and
in what order*. It is the single entry point both Prime Builder and Loyal
Opposition resolve at startup; the long-form procedure restated across `CLAUDE.md`,
`AGENTS.md`, and the Codex bootstrap files should defer to this index rather than
re-stating it (advisory F4). The surface *inventory* (which files, with lifecycle
classification) lives in `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
(Slice A); this index is the *load order* over those surfaces.

## Canonical Startup Load Order (both roles)

1. **Role record** — resolve the durable operating role from the canonical
   MemBase harness registry projection `harness-state/harness-registry.json`
   (per `REQ-HARNESS-REGISTRY-001`); the legacy
   `harness-state/role-assignments.json` mirror is an orphan compatibility
   surface, **not** the source. Honor any interactive session-stated override
   (`::init gtkb pb|lo`) per `DCL-SESSION-ROLE-RESOLUTION-001`.
2. **Role overlay** — load the role-specific overlay:
   `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` or
   `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`.
3. **Canonical terminology** — load `.claude/rules/canonical-terminology.md`
   before interpreting owner terms or proposing specifications.
4. **File bridge** — read live `bridge/INDEX.md` directly; it is the sole
   authoritative bridge-queue state (no cached/derived counts).
5. **Dashboard / backlog summary** — the generated startup service
   (`scripts/session_self_initialization.py`) emits the current-state summary;
   it is not authoritative after generation.
6. **Selected task** — map the owner's first non-init message to session work
   (Prime Builder: confirm session focus; Loyal Opposition: process the
   actionable bridge queue by default per the LO overlay).

## Role Overlays

- **Prime Builder** → `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`.
- **Loyal Opposition** → `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`.

## Surface Inventory

For the full classified inventory of startup control surfaces (required files,
settings, hooks, skills/commands/agents, generated/projected surfaces, retired
surfaces), see `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` (Slice A).

## Authority Note

This index is a consolidation/navigation surface; it does not supersede the
governing records. The init-keyword startup-disclosure relay contract
(`DELIB-2078`, `GOV-SESSION-SELF-INITIALIZATION-001`) and GOV-01 (CLAUDE.md
≤300 lines) remain in force.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
