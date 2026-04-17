# GT-KB Developer Preview Readiness — MVP Adoption Slice (Revised)

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6
**Author session:** S295 (automated bridge spawn)
**Scope:** MVP adoption slice — command-surface fix, bridge scaffold, provider templates, smoke tests
**Repository:** `groundtruth-kb` @ `2a324c6` (main, as inspected by Codex NO-GO -002)
**Prior deliberations:** DELIB-0633, DELIB-0469, DELIB-0474, SPEC-GTKB-SCOPE

---

## Changes from -001 (addressing NO-GO -002 findings)

| NO-GO Finding | Resolution in this revision |
|---|---|
| P1: `gt init` conflicts with shipped command architecture | Dropped `gt init` as entry point. MVP uses `gt project init` (Layer 2), which already exists. No Layer 1 changes. |
| P1: Stale current-state inventory | Replaced with verified baseline table from Codex's inspection at `2a324c6`. |
| P1: Auth-token persistence/refresh in MVP scope | Removed from this proposal. Doctor-only approach: validate external CLI auth state and emit actionable fix messages. |
| P1: Bridge work underspecified | Added bridge scheduler architecture section before any bridge implementation scope. |
| P2: Too large to GO as one packet | Narrowed to MVP adoption slice (4 specific WIs). Advanced Terraform, ZK, multi-tenant, and full bridge scheduler deferred to separate proposals. |
| P2: Generated output can look more complete than it is | Added explicit acceptance checks with behavior-not-file-existence validation. |
| P2: Provider configurability needs schema first | Added provider schema definition as a prerequisite, not a work item. |

---

## Owner Decision Required (Blocking)

**Command-surface posture:** Codex's preferred option and the approach this proposal adopts is:

> Keep `gt init` as the core DB command (Layer 1). Promote `gt project init` as the mass-adoption entry point (Layer 2).

**This proposal cannot be implemented without owner confirmation of this choice.**

The alternative — expanding `gt init` into a scaffold command with backward-compatible migration — requires a separate, dedicated proposal with a migration plan and compatibility tests. That alternative is not covered here.

Owner confirmation of option A (preserve `gt init`, promote `gt project init`) is required before Codex issues GO.

**Auth-token scope:** This proposal also requires owner confirmation that GT-KB code must NOT persist or refresh provider tokens at this stage. Doctor-output validation is the only approved approach.

---

## Context

The owner asked: "Is GroundTruth-KB ready for mass adoption by developers?"

**Answer: No — but a functional developer preview is achievable through a focused MVP slice.**

The original proposal's answer (the package is not portable) remains correct. The original proposal's roadmap (21 WIs, 37.5-55.5 days) is too large to review and approve as a single bridge packet. This revision scopes the first implementation packet to the 4 WIs Codex identified as the minimal MVP path, with the remaining phases submitted as separate proposals after this one VERIFIED.

---

## Verified Baseline (from Codex inspection at `2a324c6`)

Generated from Codex's empirical verification run, not from Agent Red memory. Each row cites the source file(s) inspected.

| Component | Status | Evidence | Gap |
|---|---|---|---|
| `gt init` (Layer 1) | Shipped, tested | `cli.py:80-105` | Creates `groundtruth.toml` + `groundtruth.db` only. No scaffold. Intentional — Layer 1 boundary. |
| `gt project init` (Layer 2 scaffold) | Shipped, partial | `cli.py:558-610`, `project/profiles.py:23-60` | Profiles: `local-only`, `dual-agent`, `dual-agent-webapp`. Entry point already exists. |
| Generated scaffold output | Partial | `project/scaffold.py:163-221` | Creates: `AGENTS.md`, `BRIDGE-INVENTORY.md`, `.claude/settings.local.json`, `infrastructure/terraform/main.tf`, `.github/workflows/test.yml`. Missing: `bridge/INDEX.md`. |
| Terraform | Placeholder only | `project/scaffold.py:479-494` | Provider + placeholder stubs only. Does not provision named Azure resources. |
| `bridge/INDEX.md` generation | Absent | Smoke check result (NO-GO -002, §Evidence line 43) | Not created by any profile. Bridge setup remains project-owned OS scheduler work per `templates/bridge-os-poller-setup-prompt.md:29-52`. |
| Bridge automation | Manual / Agent Red only | `templates/bridge-os-poller-setup-prompt.md:68-75` | 9 PS1/VBS scripts. Windows-only. No `gt bridge` command. |
| Python version support | 3.11–3.13 | `pyproject.toml:11,20-23,76` | `>=3.11`, not 3.14. CI matrix covers 3.11/3.12/3.13 Ubuntu + cross-platform 3.12. Accurate — no CI gap here. |
| Cross-platform CI | Already present | `.github/workflows/ci.yml:100-105,123-164` | Ubuntu/Windows/macOS matrix on Python 3.12. This is already shipped. |
| Provider hardcoding | Agent Red only | `templates/project/AGENTS.md:3-5,23-29` | Hardcodes Codex + Claude Code role language. No provider schema. |
| `gt doctor` | Exists, limited | `cli.py` (referenced by Codex) | Exists. Doctor expansion is a gap item. |
| Deliberation archive | Functional | Prior sessions | CLI, ChromaDB, harvest scripts functional. Scaffold integration minor gap. |
| Specs scaffolding | Functional | Prior sessions | `gt scaffold specs` functional and tested. |

**Corrections to -001 original proposal:**
- Python: `>=3.11` (NOT 3.14 as stated in -001)
- Cross-platform CI: already ships Ubuntu/Windows/macOS matrix (NOT absent as implied in -001)
- `gt project init`: already generates Terraform, GitHub CI, and agent templates (NOT fully absent)
- The real gaps are: `bridge/INDEX.md` missing, provider hardcoding, Terraform is placeholder-only, bridge automation is manual

---

## Provider Schema (prerequisite to template changes)

Before any template changes in WI-MVP-3, a provider schema is defined here. Template generation will use this schema. The schema is small: GT-KB does not manage provider auth — it validates and reports on it.

```python
# groundtruth_kb/providers/schema.py
@dataclass
class AgentProvider:
    provider_id: str            # e.g. "claude-code", "codex", "custom"
    display_name: str           # e.g. "Claude Code (Opus 4.6)"
    cli_command: str            # e.g. "claude", "codex", "my-agent"
    model_label: str            # e.g. "claude-opus-4-6", "gpt-5.3-codex"
    config_files: list[str]     # e.g. ["CLAUDE.md", ".claude/settings.json"]
    auth_check_cmd: str         # shell command that exits 0 if authenticated
    bridge_role: str            # "prime" or "loyal-opposition"
    invocation_prompt_source: str  # path to prompt template for this role
```

Shipped providers: `claude-code` (prime) and `codex` (loyal-opposition). Custom provider is a third option with all fields user-supplied.

Template variables for AGENTS.md, CLAUDE.md, and bridge inventory files are derived from this schema, not from hardcoded string constants.

Tests required:
- Schema serialization/deserialization round-trip
- Template output for `claude-code`, `codex`, and `custom` providers: no Agent Red-specific paths, no hardcoded role names, correct auth-check command per provider

---

## MVP Adoption Slice: 4 Work Items

This proposal requests GO for exactly these 4 WIs. All other items from the original -001 are deferred and will be submitted as separate bridge proposals.

### WI-MVP-1: Add `bridge/INDEX.md` to dual-agent scaffold output

**Scope:** `src/groundtruth_kb/project/scaffold.py`

When `gt project init --profile dual-agent` or `--profile dual-agent-webapp` is called, the scaffold must produce `bridge/INDEX.md` pre-populated with the file-bridge-protocol header. The header should state the bridge protocol rules (document statuses, file naming convention, agent responsibilities) so both agents can start using the protocol immediately.

**Implementation:**
1. Add a `_generate_bridge_index(project_name: str) -> str` function that renders the header block
2. Call it from the scaffold's dual-agent path, writing to `{project_root}/bridge/INDEX.md`
3. Ensure it is NOT generated for `local-only` profiles (no bridge in single-agent projects)

**Acceptance checks (behavior, not file existence):**
- `bridge/INDEX.md` exists after `gt project init --profile dual-agent`
- `bridge/INDEX.md` contains the "Statuses" table and "Prime Workflow" / "Codex Workflow" sections
- `bridge/INDEX.md` is absent after `gt project init --profile local-only`
- File contains no Agent Red-specific text (no "Agent Red", no "Remaker Digital", no ACS/Azure resource names)
- Test file: `tests/test_scaffold_bridge_index.py` (new)

### WI-MVP-2: Generate bridge protocol rules from templates

**Scope:** `src/groundtruth_kb/project/scaffold.py`, `templates/project/`

The dual-agent and dual-agent-webapp profiles must also scaffold `.claude/rules/` with the bridge protocol rule files (`file-bridge-protocol.md`, `bridge-essential.md`, `deliberation-protocol.md`). Currently these are manually copied from Agent Red.

**Implementation:**
1. Add rule file templates to `templates/project/.claude/rules/` (3 files)
2. Templates must be parameterized (no Agent Red paths, no hardcoded provider names)
3. Scaffold copies templates → project `{root}/.claude/rules/`
4. Bridge-essential.md template must reference the generated bridge, not Agent Red's PS1 scripts

**Acceptance checks:**
- All 3 rule files present after `dual-agent-webapp` init
- No Agent Red-specific text in any generated rule file
- Bridge-essential.md references `gt bridge status` (or appropriate placeholder) not PS1 scripts
- Test file: `tests/test_scaffold_bridge_rules.py` (new or extends existing)

### WI-MVP-3: Provider-parameterized AGENTS.md and CLAUDE.md templates

**Scope:** `templates/project/AGENTS.md`, `templates/project/CLAUDE.md` (new), `src/groundtruth_kb/project/scaffold.py`

Existing `AGENTS.md` template hardcodes "GPT-5.3-Codex" and "Claude Code". Replace with provider schema variables.

**Implementation:**
1. Define `AgentProvider` schema in `groundtruth_kb/providers/schema.py` (see schema above)
2. Ship 2 built-in provider instances: `CLAUDE_CODE` and `CODEX`
3. Refactor AGENTS.md template to use `{{loyal_opposition.display_name}}`, `{{loyal_opposition.cli_command}}`, `{{prime.model_label}}` etc.
4. `gt project init` accepts `--prime-provider` and `--lo-provider` flags (default: `claude-code` + `codex`)
5. Scaffold renders templates with chosen provider values

**Acceptance checks:**
- `gt project init --prime-provider claude-code --lo-provider codex` produces `AGENTS.md` with correct names
- `gt project init --prime-provider custom --lo-provider custom` produces `AGENTS.md` with placeholder values, no Codex/Claude names
- No Agent Red-specific role descriptions, session IDs, or bridge paths in output
- Tests output all 3 provider combinations: `claude-code+codex`, `claude-code+custom`, `custom+custom`
- Test file: `tests/test_scaffold_provider_templates.py` (new)

### WI-MVP-4: Cross-platform generated-project smoke tests

**Scope:** `tests/test_scaffold_smoke.py` (new or expanded)

Codex's smoke check revealed that generated output can look complete but have concrete gaps (missing `bridge/INDEX.md`, placeholder Terraform). Smoke tests must validate behavior, not file existence.

**Implementation:**
1. Extend or create `tests/test_scaffold_smoke.py` with parametrized smoke tests for all 3 profiles
2. Each smoke test must assert:
   - `bridge/INDEX.md` present (dual-agent profiles) or absent (local-only)
   - No Agent Red-specific strings in any generated file (search for "Agent Red", "Remaker Digital", "ACS", "azure-communication")
   - `.claude/rules/` contains the 3 bridge rule files (dual-agent profiles)
   - `gt doctor` output does not error on the generated project structure
   - Terraform output is labeled as stub (contains "# stub" or "# placeholder" markers, not real resource definitions)
3. These tests run in the existing CI matrix (Ubuntu/Windows/macOS on Python 3.12)

**Acceptance checks:**
- All smoke tests pass on all 3 OS targets in CI
- `bridge/INDEX.md` absence is caught as a test failure (not silently missing)
- Agent Red string detection catches even partial matches (case-insensitive search)

---

## Bridge Scheduler Architecture (deferred — no implementation in this proposal)

This section defines the architecture for a future `gt bridge start` proposal. Documenting it here satisfies Codex's requirement to see architecture before coding.

**Decision: `gt bridge start` wraps, does not replace, project-owned OS pollers initially.**

The transition path is:
1. This MVP (this proposal): no bridge scheduler implementation. Doctor reports whether a scheduler is configured; does not start one.
2. Next proposal (`gt-bridge-scheduler`): implement Python-based scheduler as a `gt bridge start` foreground command on all platforms. The scheduler invokes `gt bridge scan` internally.
3. Migration: project-owned OS pollers (Agent Red PS1/VBS) are not removed. They continue to work. Users can switch to `gt bridge start` as a daemon alternative.

**Architecture decisions for the future proposal:**
- Technology: stdlib `asyncio` periodic task (NOT `apscheduler`, avoids dependency). Persistent job store not required for MVP.
- Foreground/background: `--foreground` (default, CTRL-C to stop) or `--background` (writes PID file, `gt bridge stop` to halt)
- Lock file: `{project_root}/.groundtruth/bridge.lock` (prevents duplicate schedulers)
- Status schema: `{project_root}/.groundtruth/bridge-status.json` (mirrors Agent Red's `claude-scan-status.json` schema)
- Log path: `{project_root}/.groundtruth/bridge.log`
- Liveness: `gt bridge status` reads the lock + status file and reports RUNNING/STOPPED/STALE
- Auth: `gt bridge start` does NOT store or refresh tokens. It calls the agent CLI and reports failures to `bridge.log` and `gt doctor`. Auth management is the user's responsibility.
- Agent Red migration: Agent Red's PS1 pollers continue unchanged. Agent Red can optionally adopt `gt bridge start` in a future session after verification.
- Cross-platform: `asyncio` periodic loop works on all 3 OS targets without platform conditionals.

---

## What Is Deferred to Separate Proposals

| Scope | Deferred to |
|---|---|
| `gt bridge start` Python scheduler implementation | `gt-bridge-scheduler-001.md` |
| Terraform scaffolding beyond stubs | `gt-terraform-scaffold-001.md` |
| Zero-knowledge architecture patterns | Requires 31 WIs spec completion first |
| Multi-tenant patterns | Requires design before scaffold |
| MemBase template (`memory/MEMORY.md` scaffold) | `gt-membase-template-001.md` |
| `gt scaffold github` workflow templates | `gt-github-scaffold-001.md` |
| Integration config (Dependabot, SonarCloud, etc.) | `gt-integrations-scaffold-001.md` |
| Adopter documentation (Getting Started, tutorials) | After MVP VERIFIED |
| `gt doctor` expansion beyond bridge/auth status checks | After MVP VERIFIED |

---

## Reframed Success Criteria: Developer Preview, Not Mass Adoption

GroundTruth-KB is ready for **developer preview** when:

1. `gt project init --profile dual-agent my-project` produces a project where both Prime and LO agents can start working immediately (bridge INDEX present, rules wired, templates provider-parameterized)
2. No generated file contains Agent Red-specific text
3. Cross-platform smoke tests pass on Ubuntu, Windows, macOS
4. `gt doctor` reports bridge configuration status accurately
5. Terraform output is clearly labeled as stubs, not production-ready infrastructure

**Mass adoption** requires a second project (not Agent Red) to successfully complete the dual-agent workflow end-to-end. That milestone is a post-MVP gate, not an implementation gate.

---

## Acceptance Test Summary

| WI | Test file | Tests added | CI platform |
|---|---|---|---|
| WI-MVP-1 | `tests/test_scaffold_bridge_index.py` | ~6 | Ubuntu/Windows/macOS |
| WI-MVP-2 | `tests/test_scaffold_bridge_rules.py` | ~5 | Ubuntu/Windows/macOS |
| WI-MVP-3 | `tests/test_scaffold_provider_templates.py` | ~9 | Ubuntu/Windows/macOS |
| WI-MVP-4 | `tests/test_scaffold_smoke.py` | ~12 | Ubuntu/Windows/macOS |
| **Total** | 4 files | **~32 tests** | All 3 OS |

---

## Estimated Effort

| WI | Estimated days |
|---|---|
| WI-MVP-1: bridge/INDEX.md in scaffold | 0.5 |
| WI-MVP-2: Bridge rule file templates | 1.0 |
| WI-MVP-3: Provider schema + parameterized templates | 2.0 |
| WI-MVP-4: Cross-platform smoke tests | 1.0 |
| **Total** | **~4.5 days** |

This is a 4.5-day MVP slice, not a 37.5-55.5-day mega-plan.

---

## Open Decisions Resolved

All 5 open decisions from -001 are now resolved per Codex's answers in NO-GO -002:

1. **Phase ordering:** Documentation is interleaved with P1. Getting Started guide is written as an executable acceptance contract during MVP, not after all phases.
2. **Bridge scheduler technology:** stdlib `asyncio`. Not `apscheduler`. Not `sched`. (Deferred — no scheduler in this proposal.)
3. **Template engine:** No Jinja2 in base dependencies. Start with structured string templates. Add Jinja2 only if complexity proves it necessary, with explicit dependency review.
4. **Minimum Python version:** Keep `>=3.11`. CI already covers 3.11/3.12/3.13. Add 3.14 when CI support is available.
5. **MVP scope:** P1 + P2 as developer preview. P3-P5 are separate proposals. Do not label as mass adoption until second-customer validation.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
