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

1. **Role record** — resolve the dispatcher/default role from the canonical
   MemBase harness registry projection `harness-state/harness-registry.json`
   (per `REQ-HARNESS-REGISTRY-001`). Honor any interactive session-stated override
   (`::init gtkb pb|lo`) per `DCL-SESSION-ROLE-RESOLUTION-001`.
2. **Role overlay** — load the role-specific overlay:
   `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` or
   `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`.
3. **Canonical terminology** — load the **core GT-KB primer subset** from
   `.claude/rules/canonical-terminology.md` at base startup (bounded by
   `required_primer_terms` in `canonical-terminology.toml`). Activity-specific
   terminology and skill recommendations load only when an agent opens the
   corresponding activity envelope with `::open <activity>` per
   `SPEC-INTAKE-46594e` and `DCL-ACTIVITY-DISPOSITION-PROFILE-001`.
   The enforceable sharding boundary is declared in
   `config/agent-control/activity-envelope-sharding.toml`: `global_baseline`
   loads at session start, `activity_only` loads on `::open <activity>`,
   `explicit_query` stays behind compact query/read surfaces, and
   `never_startup` is forbidden from routine startup loads.
4. **File bridge** — read current TAFE/dispatcher bridge state and the
   status-bearing versioned files under `bridge/`; generated or cached startup
   counts are not live authority. The retired aggregate queue artifact must
   not be recreated as a startup dependency. Bridge review independence is
   session-context based — see **Session-context review independence (normative)**
   below.
5. **Dashboard / backlog summary** — the generated startup service
   (`scripts/session_self_initialization.py`) emits the current-state summary;
   it is not authoritative after generation.
6. **Selected task** — map the owner's first non-init message to session work
   (Prime Builder: confirm session focus; Loyal Opposition: process the
   actionable bridge queue by default per the LO overlay).

## Session-context review independence (normative)

Formal bridge review (GO / NO-GO / VERIFIED) must come from a **different model
session context** than the one that authored or implemented the artifact under
review. Shared session context means the verifier likely inherits the same
assumptions and errors as the author — same-session formal review is prohibited
and must fail closed.

- **Blocker:** reviewer session context equals artifact `author_session_context_id`
- **Fail closed:** missing or unreadable `author_session_context_id`
- **Not the boundary:** harness ID, vendor, or durable registry role (routing labels only)

Interactive `::init gtkb pb` grants Prime Builder authority in this session
regardless of durable registry role. It does **not** permit this same session
context to later issue GO/VERIFIED on work it authored or implemented here.

## Antigravity (Harness ID C) Overrides

To minimize token cost and resource consumption, the Antigravity harness modifies the canonical startup order:
- **Load Role Overlay**: Antigravity's optimized startup path must load the active role overlay (`config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` or `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`) appropriate to its resolved role to enforce role boundaries.
- **Skip Rules/Logs Reads**: Antigravity is exempt from reading the extensive Phase B rule/log payload. It only loads essential baseline files (`CLAUDE.md`, `AGENTS.md`, `canonical-terminology.md`, `file-bridge-protocol.md`, `memory/MEMORY.md`).
- **Omit Heavy Subprocesses**: Any startup dispatching or background scripts (e.g. `session_self_initialization.py`) must be run with `--fast-hook` and `--skip-bridge-maintenance` to skip reachability probes and PDF exports.

## New-agent orientation

For the canonical end-to-end GT-KB lifecycle (deliberate through commit), read
`groundtruth-kb/docs/method/14-lifecycle.md`. This pointer is the role-neutral
startup surfacing for WI-3352; it does not expand the minimized init-disclosure
payload (`DCL-SESSION-STARTUP-TOKEN-BUDGET-001`).

## Role Overlays

- **Prime Builder** → `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md`.
- **Loyal Opposition** → `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`.

## Surface Inventory

For the full classified inventory of startup control surfaces (required files,
settings, hooks, skills/commands/agents, generated/projected surfaces, retired
surfaces), see `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md` (Slice A).
For the session/activity envelope sharding taxonomy and the four payload classes
that constrain startup versus opened activities, see
`config/agent-control/activity-envelope-sharding.toml`.

## Authority Note

This index is a consolidation/navigation surface; it does not supersede the
governing records. The init-keyword startup-disclosure relay contract
(`DELIB-2078`, `GOV-SESSION-SELF-INITIALIZATION-001`) and GOV-01 (CLAUDE.md
≤300 lines) remain in force.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
