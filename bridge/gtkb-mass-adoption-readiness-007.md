# GT-KB Developer Preview Readiness — MVP Adoption Slice (Revision 3)

**Status:** REVISED
**Prime Builder:** Claude Sonnet 4.6
**Author session:** S296 (automated bridge spawn)
**Scope:** MVP adoption slice — bridge INDEX scaffold, bridge rule templates, provider-parameterized templates (built-in only), doctor bridge-readiness fixes, cross-platform smoke tests
**Repository:** `groundtruth-kb` @ `2a324c6` (Codex-inspected baseline; working against current main)
**Prior deliberations:** DELIB-0633, DELIB-0469, DELIB-0474, DELIB-0601
**Addresses NO-GO:** `bridge/gtkb-mass-adoption-readiness-006.md`

---

## Changes from -005 (addressing NO-GO -006 findings)

| NO-GO Finding | Resolution in this revision |
|---|---|
| P1: `gt project doctor` false-positive — passes when `bridge/INDEX.md` absent | Added WI-MVP-5: explicit doctor work item. Doctor must warn/fail for bridge profiles when INDEX or rule files are missing. Negative tests required. |
| P1: WI-MVP-4 smoke test scan broader than implementation scope | Narrowed WI-MVP-4 string scan to product-specific leakage only. `Remaker Digital` in Docker/compose/bootstrap templates deferred to a separate template-neutrality proposal. Policy choice documented explicitly. |
| P2: Provider flags allow role/provider mismatch | WI-MVP-3 updated to require `bridge_role` validation on `--prime-provider` and `--lo-provider`. `--prime-provider codex` and `--lo-provider claude-code` must fail with clear errors. `src/groundtruth_kb/cli.py` added to scope. |
| Non-blocking: repo commit ref stale | Fixed. Proposal now correctly states `2a324c6` as inspected baseline per Codex evidence (previous phrasing was ambiguous). |
| Non-blocking: `.claude/rules/` baseline row inaccurate | Fixed. Scaffold does generate `.claude/rules/` with existing rule files; the gap is the three specific new files. |

---

## Architectural Posture

**No new owner decisions are required for this proposal.** All Layer 1 interfaces remain unchanged. No token storage or refresh logic is introduced.

**Command-surface posture:** `gt init` remains Layer 1. `gt project init` is the Layer 2 scaffold entry point. `gt project doctor` is the readiness verifier. This proposal adds to Layer 2 scaffold and fixes doctor accuracy — no Layer 1 changes.

**Token-persistence posture:** GT-KB does not persist or refresh provider tokens. This proposal adds no such logic. Doctor checks CLI availability only; it makes no claim about auth-state validation beyond what the CLI itself can report.

---

## Context

The owner asked: "Is GroundTruth-KB ready for mass adoption by developers?"

**Answer: No — but a functional developer preview is achievable through a focused MVP slice.**

A developer using `gt project init --profile dual-agent` currently gets incomplete output: no `bridge/INDEX.md`, no bridge rule files in `.claude/rules/`, hardcoded Agent Red provider names in templates, and a doctor that reports bridge readiness as pass even when critical bridge prerequisites are missing. This proposal fixes all four gaps, plus adds cross-platform smoke tests.

---

## Verified Baseline (from Codex inspection at `2a324c6`)

| Component | Status | Evidence | Gap |
|---|---|---|---|
| `gt init` (Layer 1) | Shipped, tested | `cli.py:80-105` | Creates `groundtruth.toml` + `groundtruth.db` only. No scaffold. Intentional. |
| `gt project init` (Layer 2 scaffold) | Shipped, partial | `cli.py:558-610`, `project/profiles.py:23-60` | Profiles: `local-only`, `dual-agent`, `dual-agent-webapp`. Entry point exists. |
| Generated scaffold output | Partial | `project/scaffold.py:163-221` | Creates: `AGENTS.md`, `BRIDGE-INVENTORY.md`, `.claude/settings.local.json`, `infrastructure/terraform/main.tf`, `.github/workflows/test.yml`. Missing: `bridge/INDEX.md`. |
| `bridge/INDEX.md` generation | Absent | Smoke check result (NO-GO -002, §Evidence line 43) | Not created by any profile. |
| `.claude/rules/` generation | Partial | Smoke check result (NO-GO -006, §Evidence lines 44-50) | Scaffold does create `.claude/rules/` with `bridge-poller-canonical.md`. Gap: three specific new rule files absent (`file-bridge-protocol.md`, `bridge-essential.md`, `deliberation-protocol.md`). |
| Bridge automation | Manual / Agent Red only | `templates/bridge-os-poller-setup-prompt.md:68-75` | Windows-only PS1/VBS scripts. No `gt bridge` command. |
| Provider hardcoding | Agent Red only | `templates/project/AGENTS.md:3-5,23-29` | Hardcodes Codex + Claude Code role language. No provider schema. |
| `gt project doctor` bridge check | Exists, false-positive | `doctor.py:469-500` | Returns pass when `bridge/INDEX.md` absent. Does not check the three new rule files. |
| `gt project doctor` CLI check | Exists, limited | `doctor.py:181-188` | Checks Claude Code with `claude --version` only. Does not check Codex availability. |
| `gt bridge` command | Does not exist | `python -m groundtruth_kb bridge --help` exits 1 | Out of scope for this proposal. |
| Cross-platform CI | Already present | `.github/workflows/ci.yml:100-105,123-164` | Ubuntu/Windows/macOS matrix on Python 3.12. Not a gap. |

---

## Provider Schema (prerequisite to WI-MVP-3; built-in providers only)

The MVP schema covers only `claude-code` and `codex` built-in providers. The `custom` provider and the `auth_check_cmd` field are deferred.

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

Built-in provider instances:
- `CLAUDE_CODE`: `provider_id="claude-code"`, `bridge_role="prime"`, `display_name="Claude Code (Opus 4.6)"`, `cli_command="claude"`, `model_label="claude-opus-4-6"`, `config_files=["CLAUDE.md", ".claude/settings.json"]`
- `CODEX`: `provider_id="codex"`, `bridge_role="loyal-opposition"`, `display_name="GPT Codex (Loyal Opposition)"`, `cli_command="codex"`, `model_label="gpt-codex"`, `config_files=["AGENTS.md"]`

**Role validation invariant:** A provider may only be selected for a flag whose expected `bridge_role` matches. `--prime-provider` accepts only providers with `bridge_role == "prime"`. `--lo-provider` accepts only providers with `bridge_role == "loyal-opposition"`. This is validated at CLI parse time, not at scaffold generation time.

Template variables for AGENTS.md and CLAUDE.md are derived from these provider instances, not from hardcoded string constants.

---

## Generated-Output Neutrality Policy

**Policy choice (Option 2 from NO-GO -006):** The WI-MVP-4 string scan is narrowed to product-specific leakage only. Specifically, the smoke test searches for: `"Agent Red"`, `"ACS"`, `"azure-communication"`, and hardcoded Agent Red repository paths.

**`Remaker Digital` handling:** `Remaker Digital` appears in Docker, compose, and Codex bootstrap templates as a copyright/vendor placeholder. These templates are owned by GT-KB and included in generated adopter projects. The correct policy for rendering or replacing vendor copyright text in generated adopter outputs is a separate legal/template ownership question. That question is deferred to `gt-template-neutrality-001.md` (a separate bridge proposal, not this MVP). The smoke test does **not** assert on `"Remaker Digital"`.

**Rationale for Option 2 over Option 1:** Option 1 (add a broad template-neutrality work item to this MVP) would expand scope beyond what is needed for bridge operational correctness. The three gaps this MVP closes (missing INDEX, missing rule files, hardcoded agent role names) are the bridge readiness blockers. Template copyright text is a separate concern with a different risk profile and owner decision surface.

---

## MVP Adoption Slice: 5 Work Items

This proposal requests GO for exactly these 5 WIs.

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
- File contains no Agent Red-specific text (no "Agent Red", no ACS/Azure resource names)
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

### WI-MVP-3: Provider-parameterized AGENTS.md and CLAUDE.md templates with role validation

**Scope:** `templates/project/AGENTS.md`, `templates/project/CLAUDE.md` (new), `src/groundtruth_kb/project/scaffold.py`, `src/groundtruth_kb/providers/schema.py` (new), `src/groundtruth_kb/cli.py`

Existing `AGENTS.md` template hardcodes "GPT-5.3-Codex" and "Claude Code". Replace with provider schema variables. Built-in `claude-code+codex` combination only in this MVP.

**Implementation:**
1. Define `AgentProvider` schema in `groundtruth_kb/providers/schema.py` (see schema above — no `auth_check_cmd`)
2. Ship 2 built-in provider instances: `CLAUDE_CODE` and `CODEX`
3. Refactor AGENTS.md template to use `{{loyal_opposition.display_name}}`, `{{loyal_opposition.cli_command}}`, `{{prime.model_label}}` etc.
4. `gt project init` in `cli.py` accepts `--prime-provider` and `--lo-provider` flags
5. Provider selection validates both id and role:
   - Lookup provider by id; unknown ids raise `click.UsageError` listing valid options
   - `--prime-provider` must resolve to a provider with `bridge_role == "prime"`; any other role raises `click.UsageError` with message: "Provider '{id}' has role '{role}' but --prime-provider requires bridge_role='prime'"
   - `--lo-provider` must resolve to a provider with `bridge_role == "loyal-opposition"`; any other role raises `click.UsageError` with message: "Provider '{id}' has role '{role}' but --lo-provider requires bridge_role='loyal-opposition'"
6. Scaffold renders templates with chosen provider values

**Custom provider deferred:** The `custom` provider type, the `auth_check_cmd` field, and the `--provider-config` file-path input path are not implemented in this MVP.

**Acceptance checks:**
- `gt project init --prime-provider claude-code --lo-provider codex` produces `AGENTS.md` with correct display name and CLI command for each provider
- No Agent Red-specific role descriptions, session IDs, or bridge paths in output
- Tests cover the built-in combination: `claude-code+codex` (happy path)
- `gt project init --prime-provider custom` raises a clear error (unknown id)
- `gt project init --prime-provider codex` raises a `click.UsageError` citing role mismatch (codex has bridge_role='loyal-opposition', not 'prime')
- `gt project init --lo-provider claude-code` raises a `click.UsageError` citing role mismatch (claude-code has bridge_role='prime', not 'loyal-opposition')
- Test file: `tests/test_scaffold_provider_templates.py` (new)

### WI-MVP-4: Cross-platform generated-project smoke tests (narrowed string scan)

**Scope:** `tests/test_scaffold_smoke.py` (new or expanded)

**Implementation:**
1. Extend or create `tests/test_scaffold_smoke.py` with parametrized smoke tests for all 3 profiles
2. Each smoke test must assert:
   - `bridge/INDEX.md` present (dual-agent profiles) or absent (local-only)
   - No product-specific leakage strings in any generated file (search for `"Agent Red"`, `"ACS"`, `"azure-communication"`, and any hardcoded Agent Red repository path)
   - `.claude/rules/` contains the 3 new bridge rule files (dual-agent profiles)
   - `gt project doctor` does not error on the generated project structure (exit code 0)
   - Terraform output contains `# stub` or `# placeholder` markers
3. These tests run in the existing CI matrix (Ubuntu/Windows/macOS on Python 3.12)

**String scan scope clarification:** The scan does NOT assert on `"Remaker Digital"` — that text may appear in Docker/compose/bootstrap templates as vendor copyright and is deferred to the template-neutrality proposal. Scanned strings are limited to product-specific identifiers that would indicate Agent Red application state was leaked into a generic adopter scaffold.

**Acceptance checks:**
- All smoke tests pass on all 3 OS targets in CI
- `bridge/INDEX.md` absence in a dual-agent profile is caught as a test failure
- `"Agent Red"` detection catches partial matches (case-insensitive)
- `gt project doctor` (not `gt doctor`) is the command invoked in the smoke check

### WI-MVP-5: Fix `gt project doctor` bridge-readiness accuracy

**Scope:** `src/groundtruth_kb/project/doctor.py`

The current doctor bridge-file check (`doctor.py:469-500`) passes when `bridge/INDEX.md` is absent and does not check for the three bridge rule files. This makes it unreliable as the bridge-readiness verifier generated `bridge-essential.md` instructs adopters to run.

**Implementation:**
1. In `_check_file_bridge()` (or the equivalent check called from `run_doctor()` for bridge profiles), add:
   - If `bridge/INDEX.md` is absent: emit a WARN result (not pass), with message: "bridge/INDEX.md not found — create it to enable the bridge workflow"
   - If any of the three required rule files are absent from `.claude/rules/` (`file-bridge-protocol.md`, `bridge-essential.md`, `deliberation-protocol.md`): emit a WARN result per missing file
   - Only return pass (OK) when `bridge/INDEX.md` exists AND all three rule files exist
2. CLI availability check (currently `claude --version`): rename or annotate the check as "CLI availability" in output, not "auth validation". Do NOT change the check behavior (running `--version` is correct for availability); only ensure the output label accurately describes what is being checked.
3. Add Codex availability check: run `codex --version` (or equivalent exit-code-0 check) for bridge profiles, with the same WARN-not-error semantics as the Claude check. If `codex` CLI is not found, emit: "codex CLI not found on PATH — Loyal Opposition bridge agent unavailable".

**Negative test cases required:**
- Generate a dual-agent profile, delete `bridge/INDEX.md`, run `gt project doctor` → assert doctor output contains the INDEX WARN (not pass)
- Generate a dual-agent profile, delete one of the three required rule files, run doctor → assert doctor output contains a WARN for that rule file
- Generate a local-only profile → assert doctor does not emit bridge-related WARNs

**Acceptance checks:**
- Doctor no longer false-positives when `bridge/INDEX.md` is absent
- Doctor reports WARN when required rule files are missing
- Doctor output labels CLI checks as availability checks, not auth checks
- Doctor checks Codex CLI availability for bridge profiles
- Negative tests pass
- Test file: `tests/test_doctor_bridge_accuracy.py` (new)

---

## Bridge Scheduler Architecture (deferred — no implementation in this proposal)

**Decision: `gt bridge start` is out of scope for this proposal.** Generated `bridge-essential.md` templates include explicit placeholder text directing adopters to use project-owned OS pollers and `gt project doctor`.

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
| Template neutrality for `Remaker Digital` in Docker/compose/bootstrap | `gt-template-neutrality-001.md` |
| `gt project doctor` expansion beyond bridge/auth status checks | After MVP VERIFIED |

---

## Reframed Success Criteria: Developer Preview, Not Mass Adoption

GroundTruth-KB is ready for **developer preview** when:

1. `gt project init --profile dual-agent my-project` produces a project where both Prime and LO agents can start working immediately (bridge INDEX present, rules wired, templates provider-parameterized)
2. No generated file contains product-specific Agent Red application text
3. Cross-platform smoke tests pass on Ubuntu, Windows, macOS
4. `gt project doctor` accurately reports bridge configuration status (WARN when INDEX or rule files are missing; pass only when both are present)
5. Terraform output is clearly labeled as stubs, not production-ready infrastructure
6. Provider flag role validation prevents role/provider mismatch at CLI parse time

**Mass adoption** requires a second project (not Agent Red) to successfully complete the dual-agent workflow end-to-end. That milestone is a post-MVP gate, not an implementation gate.

---

## Acceptance Test Summary

| WI | Test file | Tests added | CI platform |
|---|---|---|---|
| WI-MVP-1 | `tests/test_scaffold_bridge_index.py` | ~6 | Ubuntu/Windows/macOS |
| WI-MVP-2 | `tests/test_scaffold_bridge_rules.py` | ~5 | Ubuntu/Windows/macOS |
| WI-MVP-3 | `tests/test_scaffold_provider_templates.py` | ~9 (adds 2 role-mismatch negative cases) | Ubuntu/Windows/macOS |
| WI-MVP-4 | `tests/test_scaffold_smoke.py` | ~12 | Ubuntu/Windows/macOS |
| WI-MVP-5 | `tests/test_doctor_bridge_accuracy.py` | ~6 (3 negative cases) | Ubuntu/Windows/macOS |
| **Total** | 5 files | **~38 tests** | All 3 OS |

---

## Estimated Effort

| WI | Estimated days |
|---|---|
| WI-MVP-1: `bridge/INDEX.md` in scaffold | 0.5 |
| WI-MVP-2: Bridge rule file templates | 1.0 |
| WI-MVP-3: Provider schema + parameterized templates + role validation | 1.5 |
| WI-MVP-4: Cross-platform smoke tests (narrowed scan) | 0.75 |
| WI-MVP-5: Doctor bridge-readiness accuracy | 1.0 |
| **Total** | **~4.75 days** |

---

## Required Conditions For GO (self-assessment)

Per NO-GO -006:

1. ~~Add an explicit doctor-readiness work item and negative tests, or remove doctor-readiness claims from the MVP.~~ **Resolved:** Added WI-MVP-5 with explicit doctor behavior changes, Codex CLI availability check, and 3 negative test cases.
2. ~~Resolve the generated-output string-scan policy so implementation scope matches smoke test.~~ **Resolved:** Narrowed WI-MVP-4 scan to product-specific leakage. `Remaker Digital` deferred to `gt-template-neutrality-001.md`. Policy documented explicitly in "Generated-Output Neutrality Policy" section.
3. ~~Add provider role validation and tests for role/provider mismatch; include `src/groundtruth_kb/cli.py` in scope.~~ **Resolved:** WI-MVP-3 updated with explicit `bridge_role` validation, `click.UsageError` with role-mismatch message, two new negative test cases, and `cli.py` added to scope.
4. ~~Correct the minor baseline inaccuracies.~~ **Resolved:** Repository ref now unambiguously states `2a324c6`. `.claude/rules/` baseline row corrected to reflect that scaffold generates some rule files; gap is the three specific new files.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
