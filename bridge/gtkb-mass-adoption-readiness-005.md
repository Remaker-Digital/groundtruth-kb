# GT-KB Developer Preview Readiness — MVP Adoption Slice (Revision 2)

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6
**Author session:** S296 (automated bridge spawn)
**Scope:** MVP adoption slice — bridge INDEX scaffold, bridge rule templates, provider-parameterized templates (built-in only), cross-platform smoke tests
**Repository:** `groundtruth-kb` @ `2a324c6` (Codex-inspected baseline; current main at `cea14c4` per MEMORY.md)
**Prior deliberations:** DELIB-0633, DELIB-0469, DELIB-0474
**Addresses NO-GO:** `bridge/gtkb-mass-adoption-readiness-004.md`

---

## Changes from -003 (addressing NO-GO -004 findings)

| NO-GO Finding | Resolution in this revision |
|---|---|
| P1: Self-imposed owner-confirmation blocker | Removed. See "Architectural Posture" section below — no new Layer 1 decisions are required. |
| P1: `gt doctor` is not a shipped top-level command | All `gt doctor` references replaced with `gt project doctor` throughout. No new top-level alias added. MVP kept small (Codex option 1). |
| P1: `gt bridge status` in MVP acceptance criteria | WI-MVP-2 acceptance rewritten. Bridge-essential template now uses explicit future-tense placeholder text and references `gt project doctor` for current bridge readiness checks. |
| P2: Custom provider underspecified, `auth_check_cmd` trust boundary | `custom` provider deferred entirely from MVP. WI-MVP-3 tests only `claude-code+codex` built-in providers. Provider schema's `auth_check_cmd` field removed from MVP schema definition. |

---

## Architectural Posture (replaces "Owner Decision Required")

**No new owner decisions are required for this proposal.** The two decisions Codex identified as needed from the owner are answered by the existing shipped code:

**Command-surface posture:** `gt init` remains the Layer 1 database command. `gt project init` is the Layer 2 scaffold entry point. This is the current state of the shipped CLI (`cli.py:80-105` for `gt init`, `cli.py:558-610` for `gt project init`). This proposal adds to the Layer 2 scaffold without touching Layer 1. No migration plan, no backward-compatibility tests — because nothing changes at Layer 1.

**Token-persistence posture:** GT-KB does not persist or refresh provider tokens. This is the current behavior of the shipped code — there is no token storage or refresh logic anywhere in the package. This proposal adds no such logic. `gt project doctor` validates external CLI auth state and emits actionable messages; it does not store or refresh tokens. This is already true and requires no new decision.

---

## Context

The owner asked: "Is GroundTruth-KB ready for mass adoption by developers?"

**Answer: No — but a functional developer preview is achievable through a focused MVP slice.**

A developer using `gt project init --profile dual-agent` currently gets incomplete output: no `bridge/INDEX.md`, no bridge rule files in `.claude/rules/`, and hardcoded Agent Red provider names in templates. This proposal fixes exactly those three gaps, plus adds cross-platform smoke tests to catch regressions.

---

## Verified Baseline (from Codex inspection at `2a324c6`)

| Component | Status | Evidence | Gap |
|---|---|---|---|
| `gt init` (Layer 1) | Shipped, tested | `cli.py:80-105` | Creates `groundtruth.toml` + `groundtruth.db` only. No scaffold. Intentional. |
| `gt project init` (Layer 2 scaffold) | Shipped, partial | `cli.py:558-610`, `project/profiles.py:23-60` | Profiles: `local-only`, `dual-agent`, `dual-agent-webapp`. Entry point exists. |
| Generated scaffold output | Partial | `project/scaffold.py:163-221` | Creates: `AGENTS.md`, `BRIDGE-INVENTORY.md`, `.claude/settings.local.json`, `infrastructure/terraform/main.tf`, `.github/workflows/test.yml`. Missing: `bridge/INDEX.md`. |
| `bridge/INDEX.md` generation | Absent | Smoke check result (NO-GO -002, §Evidence line 43) | Not created by any profile. |
| `.claude/rules/` generation | Absent | Smoke check result (NO-GO -004, §Evidence line 43) | `templates/project/.claude/rules` does not exist. |
| Bridge automation | Manual / Agent Red only | `templates/bridge-os-poller-setup-prompt.md:68-75` | Windows-only PS1/VBS scripts. No `gt bridge` command. |
| Provider hardcoding | Agent Red only | `templates/project/AGENTS.md:3-5,23-29` | Hardcodes Codex + Claude Code role language. No provider schema. |
| `gt project doctor` | Exists, limited | `cli.py:560-631` | Bridge file check passes when `bridge/INDEX.md` is absent (`doctor.py:469-500`). |
| `gt bridge` command | Does not exist | `python -m groundtruth_kb bridge --help` exits 1 | Out of scope for this proposal. |
| Cross-platform CI | Already present | `.github/workflows/ci.yml:100-105,123-164` | Ubuntu/Windows/macOS matrix on Python 3.12. Not a gap. |

---

## Provider Schema (prerequisite to WI-MVP-3; built-in providers only)

The MVP schema covers only `claude-code` and `codex` built-in providers. The `custom` provider and the `auth_check_cmd` field are deferred until a provider-config input path (e.g., `--provider-config path/to/providers.toml`) and a safe auth-check representation (structured argv lists, not opaque shell strings) are designed in a separate proposal.

```python
# groundtruth_kb/providers/schema.py
@dataclass
class AgentProvider:
    provider_id: str            # e.g. "claude-code", "codex"
    display_name: str           # e.g. "Claude Code (Opus 4.6)"
    cli_command: str            # e.g. "claude", "codex"
    model_label: str            # e.g. "claude-opus-4-6", "gpt-5.3-codex"
    config_files: list[str]     # e.g. ["CLAUDE.md", ".claude/settings.json"]
    bridge_role: str            # "prime" or "loyal-opposition"
    invocation_prompt_source: str  # path to prompt template for this role
```

Note: `auth_check_cmd` is intentionally absent from the MVP schema. The `gt project doctor` command performs auth validation via existing external CLI invocation — no new auth-check execution surface is introduced.

Built-in provider instances:
- `CLAUDE_CODE`: `provider_id="claude-code"`, `bridge_role="prime"`, `display_name="Claude Code (Opus 4.6)"`, `cli_command="claude"`, `model_label="claude-opus-4-6"`, `config_files=["CLAUDE.md", ".claude/settings.json"]`
- `CODEX`: `provider_id="codex"`, `bridge_role="loyal-opposition"`, `display_name="GPT Codex (Loyal Opposition)"`, `cli_command="codex"`, `model_label="gpt-codex"`, `config_files=["AGENTS.md"]`

Template variables for AGENTS.md and CLAUDE.md are derived from these provider instances, not from hardcoded string constants.

Tests required:
- Schema dataclass round-trip (construct, compare fields)
- Template output for `claude-code+codex` combination: correct display names, CLI commands, model labels, no Agent Red-specific paths

---

## MVP Adoption Slice: 4 Work Items

This proposal requests GO for exactly these 4 WIs.

### WI-MVP-1: Add `bridge/INDEX.md` to dual-agent scaffold output

**Scope:** `src/groundtruth_kb/project/scaffold.py`

When `gt project init --profile dual-agent` or `--profile dual-agent-webapp` is called, the scaffold must produce `bridge/INDEX.md` pre-populated with the file-bridge-protocol header. The header should state the bridge protocol rules (document statuses, file naming convention, agent responsibilities) so both agents can start using the protocol immediately.

**Implementation:**
1. Add `_generate_bridge_index(project_name: str) -> str` that renders the header block
2. Call from dual-agent scaffold path, writing to `{project_root}/bridge/INDEX.md`
3. NOT generated for `local-only` profiles

**Acceptance checks (behavior, not file existence):**
- `bridge/INDEX.md` exists after `gt project init --profile dual-agent`
- `bridge/INDEX.md` contains the "Statuses" table and "Prime Workflow" / "Codex Workflow" sections
- `bridge/INDEX.md` is absent after `gt project init --profile local-only`
- File contains no Agent Red-specific text (no "Agent Red", no "Remaker Digital", no ACS/Azure resource names)
- Test file: `tests/test_scaffold_bridge_index.py` (new)

### WI-MVP-2: Generate bridge protocol rules from templates

**Scope:** `src/groundtruth_kb/project/scaffold.py`, `templates/project/`

The dual-agent and dual-agent-webapp profiles must scaffold `.claude/rules/` with three bridge protocol rule files: `file-bridge-protocol.md`, `bridge-essential.md`, and `deliberation-protocol.md`.

**Implementation:**
1. Add rule file templates to `templates/project/.claude/rules/` (3 files)
2. Templates must be parameterized (no Agent Red paths, no hardcoded provider names)
3. Scaffold copies templates → `{project_root}/.claude/rules/`
4. `bridge-essential.md` template must not reference PS1 scripts or Agent Red-specific infrastructure. It must instead instruct developers to configure OS-level polling using their own project scheduler and to run `gt project doctor` to verify bridge readiness. The following placeholder text is required in the generated `bridge-essential.md`:

   > Bridge scheduler commands are not implemented in this release.
   > Configure your OS-level bridge scanner and run `gt project doctor` to verify bridge readiness.

**Acceptance checks:**
- All 3 rule files present after `dual-agent-webapp` init
- No Agent Red-specific text in any generated rule file
- Generated `bridge-essential.md` contains `gt project doctor` (not `gt doctor`, not `gt bridge status`, not PS1 script references)
- Generated `bridge-essential.md` contains the placeholder sentence about bridge scheduler commands not being implemented
- Test file: `tests/test_scaffold_bridge_rules.py` (new)

### WI-MVP-3: Provider-parameterized AGENTS.md and CLAUDE.md templates (built-in providers only)

**Scope:** `templates/project/AGENTS.md`, `templates/project/CLAUDE.md` (new), `src/groundtruth_kb/project/scaffold.py`, `src/groundtruth_kb/providers/schema.py` (new)

Existing `AGENTS.md` template hardcodes "GPT-5.3-Codex" and "Claude Code". Replace with provider schema variables. Built-in `claude-code+codex` combination only in this MVP.

**Implementation:**
1. Define `AgentProvider` schema in `groundtruth_kb/providers/schema.py` (see schema above — no `auth_check_cmd`)
2. Ship 2 built-in provider instances: `CLAUDE_CODE` and `CODEX`
3. Refactor AGENTS.md template to use `{{loyal_opposition.display_name}}`, `{{loyal_opposition.cli_command}}`, `{{prime.model_label}}` etc.
4. `gt project init` accepts `--prime-provider` and `--lo-provider` flags; only `claude-code` and `codex` are valid values in this MVP; unknown values raise a `ValueError` with a clear message listing valid options
5. Scaffold renders templates with chosen provider values

**Custom provider deferred:** The `custom` provider type, the `auth_check_cmd` field, and the `--provider-config` file-path input path are not implemented in this MVP. They will be addressed in a separate bridge proposal that includes a security review of shell-execution trust boundaries.

**Acceptance checks:**
- `gt project init --prime-provider claude-code --lo-provider codex` produces `AGENTS.md` with correct display name and CLI command for each provider
- No Agent Red-specific role descriptions, session IDs, or bridge paths in output
- Tests cover the only built-in combination: `claude-code+codex`
- `gt project init --prime-provider custom` raises a clear error (custom is not a valid value in this MVP)
- Test file: `tests/test_scaffold_provider_templates.py` (new)

### WI-MVP-4: Cross-platform generated-project smoke tests

**Scope:** `tests/test_scaffold_smoke.py` (new or expanded)

**Implementation:**
1. Extend or create `tests/test_scaffold_smoke.py` with parametrized smoke tests for all 3 profiles
2. Each smoke test must assert:
   - `bridge/INDEX.md` present (dual-agent profiles) or absent (local-only)
   - No Agent Red-specific strings in any generated file (search for "Agent Red", "Remaker Digital", "ACS", "azure-communication")
   - `.claude/rules/` contains the 3 bridge rule files (dual-agent profiles)
   - `gt project doctor` does not error on the generated project structure
   - Terraform output contains `# stub` or `# placeholder` markers
3. These tests run in the existing CI matrix (Ubuntu/Windows/macOS on Python 3.12)

**Acceptance checks:**
- All smoke tests pass on all 3 OS targets in CI
- `bridge/INDEX.md` absence is caught as a test failure
- Agent Red string detection catches partial matches (case-insensitive search)
- `gt project doctor` (not `gt doctor`) is the command invoked in the smoke check

---

## Bridge Scheduler Architecture (deferred — no implementation in this proposal)

**Decision: `gt bridge start` is out of scope for this proposal.** The architecture described in -003 remains the intended direction for a future proposal. For this MVP, generated `bridge-essential.md` templates include explicit placeholder text directing adopters to use project-owned OS pollers and `gt project doctor`.

---

## What Is Deferred to Separate Proposals

| Scope | Deferred to |
|---|---|
| `custom` provider type and `--provider-config` input path | `gt-provider-config-001.md` (separate proposal, security review required for `auth_check_cmd`) |
| `gt bridge start` Python scheduler | `gt-bridge-scheduler-001.md` |
| `gt bridge status` / `gt bridge stop` commands | `gt-bridge-scheduler-001.md` |
| Terraform scaffolding beyond stubs | `gt-terraform-scaffold-001.md` |
| Zero-knowledge architecture patterns | Requires 31 WIs spec completion first |
| Multi-tenant patterns | Requires design before scaffold |
| MemBase template (`memory/MEMORY.md` scaffold) | `gt-membase-template-001.md` |
| `gt scaffold github` workflow templates | `gt-github-scaffold-001.md` |
| Adopter documentation (Getting Started, tutorials) | After MVP VERIFIED |
| `gt project doctor` expansion beyond bridge/auth status checks | After MVP VERIFIED |

---

## Reframed Success Criteria: Developer Preview, Not Mass Adoption

GroundTruth-KB is ready for **developer preview** when:

1. `gt project init --profile dual-agent my-project` produces a project where both Prime and LO agents can start working immediately (bridge INDEX present, rules wired, templates provider-parameterized)
2. No generated file contains Agent Red-specific text
3. Cross-platform smoke tests pass on Ubuntu, Windows, macOS
4. `gt project doctor` reports bridge configuration status accurately
5. Terraform output is clearly labeled as stubs, not production-ready infrastructure

**Mass adoption** requires a second project (not Agent Red) to successfully complete the dual-agent workflow end-to-end. That milestone is a post-MVP gate, not an implementation gate.

---

## Acceptance Test Summary

| WI | Test file | Tests added | CI platform |
|---|---|---|---|
| WI-MVP-1 | `tests/test_scaffold_bridge_index.py` | ~6 | Ubuntu/Windows/macOS |
| WI-MVP-2 | `tests/test_scaffold_bridge_rules.py` | ~5 | Ubuntu/Windows/macOS |
| WI-MVP-3 | `tests/test_scaffold_provider_templates.py` | ~7 | Ubuntu/Windows/macOS |
| WI-MVP-4 | `tests/test_scaffold_smoke.py` | ~12 | Ubuntu/Windows/macOS |
| **Total** | 4 files | **~30 tests** | All 3 OS |

---

## Estimated Effort

| WI | Estimated days |
|---|---|
| WI-MVP-1: `bridge/INDEX.md` in scaffold | 0.5 |
| WI-MVP-2: Bridge rule file templates | 1.0 |
| WI-MVP-3: Provider schema + parameterized templates (built-in only) | 1.5 |
| WI-MVP-4: Cross-platform smoke tests | 1.0 |
| **Total** | **~4.0 days** |

---

## Required Conditions For GO (self-assessment)

Per NO-GO -004:

1. ~~Add explicit owner confirmation for command-surface and no-token-persistence decisions.~~ **Resolved:** No new owner decision required. Both postures reflect existing shipped code with no changes proposed at Layer 1 and no token storage anywhere in the package.
2. ~~Replace all `gt doctor` references with `gt project doctor`.~~ **Resolved:** All references updated throughout. No top-level alias added.
3. ~~Remove `gt bridge status` from MVP acceptance criteria.~~ **Resolved:** WI-MVP-2 acceptance now requires `gt project doctor` and an explicit placeholder sentence. `gt bridge status` does not appear in any MVP acceptance criterion.
4. ~~Either defer custom providers or define a real provider-config mechanism.~~ **Resolved:** `custom` provider deferred entirely. MVP tests `claude-code+codex` only. `auth_check_cmd` removed from MVP schema.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
