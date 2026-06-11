# Harness Parity Inspection Report (Antigravity Parity Gaps)

**Date**: 2026-06-11  
**Harness**: Antigravity (Identity C)  
**Role**: Prime Builder  
**Author**: Loyal Opposition  

---

## 1. Executive Summary

This report documents a manual inspection of the configuration and capability delivery mechanisms across all GT-KB AI coding harnesses: **Claude Code** (harness B), **Codex** (harness A), **Antigravity** (harness C), **API harnesses** (**Ollama** / **OpenRouter**), and **Goose** (harness E). 

Currently, the Antigravity harness has significant parity gaps, with **55 missing capabilities** and **22 stale capability adapters** flagged by the parity audit tool (`check_harness_parity.py`). The manual inspection has identified two main root causes for these gaps:
1. **Generative Role Filtering**: The Antigravity skill adapter generator hardcodes a role filter for `loyal-opposition`, preventing it from generating skills required by `prime-builder` (which is Antigravity's active role).
2. **Checker Marker Mismatch**: The checker tool does not recognize `GTKB-ANTIGRAVITY-SKILL-ADAPTER` markers in Antigravity's adapters, thus classifying them all as `STALE`.

---

## 2. Manual Inspection Findings

### A. Claude Code Harness (`.claude/`)
- **Primary Config File**: `.claude/settings.json` (tracked) and `settings.local.json` (untracked, workstation-specific).
- **Hooks**: Rich event-driven hook suite defined under `hooks` (`PreToolUse`, `SessionStart`, `PostToolUse`, `Stop`, `UserPromptSubmit`). These invoke custom Python scripts under `.claude/hooks/` (e.g. `bridge-compliance-gate.py`, `lo-file-safety-gate.py`, `session_start_dispatch.py`) with explicit execution timeouts.
- **Skills**: Serves as the canonical source-of-truth. Native skill definitions reside in `.claude/skills/<name>/SKILL.md` without generated headers or wrapper logic.

### B. Codex Harness (`.codex/`)
- **Primary Config File**: `.codex/config.toml` (TOML metadata) and `.codex/hooks.json` (JSON).
- **Hooks**: Supports parity hook events (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`). Reuses many Claude hooks but wraps them in OS-specific shims (e.g. `cmd /d /s /c E:\GT-KB\.codex\gtkb-hooks\workstream-focus.cmd`).
- **Skills**: Delivered via generated adapters under `.codex/skills/` containing `<!-- GTKB-CODEX-SKILL-ADAPTER ... -->` markers. All skills in the registry are generated (no role-based exclusion).

### C. Antigravity Harness (`.antigravity/`)
- **Primary Config File**: `.antigravity/config.toml` (TOML metadata).
- **Hooks**: **No hooks by design**. Research spike (`DOC-ANTIGRAVITY-IDE-RESEARCH-001`) confirmed that the Gemini IDE/CLI environment has no hook event surfaces (`PostToolUse`, etc.). Instead, the harness relies on the fallback interval-driven dispatch substrate (`scripts/cross_harness_bridge_trigger.py` and scheduled tasks).
- **Skills**: Delivered via generated adapters under `.agent/skills/` containing `<!-- GTKB-ANTIGRAVITY-SKILL-ADAPTER ... -->` markers.
- **Gaps**: Only generates skills with `loyal-opposition` in `required_for_roles`.

---

## 3. Analysis of Parity Gaps & Root Causes

### Gap 1: 22 Antigravity Adapters Marked `STALE`
- **Claim**: The checker tool `check_harness_parity.py` falsely identifies existing Antigravity adapters as stale.
- **Evidence**: 
  - `check_harness_parity.py` lines 381-391:
    ```python
    expected_marker = (
        "GTKB-API-SKILL-ADAPTER"
        if manifest_adapters and harness in manifest_adapters
        else "GTKB-CODEX-SKILL-ADAPTER"
    )
    ```
  - For `antigravity`, the checker expects `GTKB-CODEX-SKILL-ADAPTER`.
  - However, `generate_antigravity_skill_adapters.py` line 41 defines `GENERATED_MARKER = "<!-- GTKB-ANTIGRAVITY-SKILL-ADAPTER"`.
  - Because of this marker mismatch, `_strip_generated_block` and `_adapter_metadata` fail to locate the generated block. The checker hash check fails (including the generated block in the hash computation), and the metadata parser returns empty results, causing a `STALE` verdict.
- **Risk/Impact**: Parity checks will always fail with exit code 1, blocking CI and release candidate checks.

### Gap 2: 14 Antigravity `prime-builder` Skills `MISSING`
- **Claim**: Antigravity lacks adapters for skills required by `prime-builder` mode.
- **Evidence**:
  - `generate_antigravity_skill_adapters.py` line 45: `ANTIGRAVITY_ROLE = "loyal-opposition"`.
  - `generate_antigravity_skill_adapters.py` lines 69-87:
    ```python
    required_roles = capability.get("required_for_roles")
    if not isinstance(required_roles, list) or ANTIGRAVITY_ROLE not in required_roles:
        continue
    ```
  - Any skill that is only required for `prime-builder` (such as `assertion-triage`, `gtkb-propose`, `deploy`, `kb-adr`, `kb-spec`, `seed-tenant`, etc.) is skipped by the generator.
  - Since Antigravity is active in the registry as `prime-builder`, it is evaluated against the `prime-builder` capabilities, which are absent.
- **Risk/Impact**: If Antigravity runs a session, it lacks the required skill guidelines for prime building, risking file safety and compliance.

### Gap 3: Goose Harness `MISSING` Entirely
- **Claim**: Goose lacks all configuration and entries in the registry, resulting in 55 missing capability findings.
- **Evidence**:
  - `goose` is in `harness-registry.json` as suspended but is still a known harness in `check_harness_parity.py`.
  - There are no `[capabilities.goose]` blocks in `harness-capability-registry.toml` to specify surfaces or status.
- **Risk/Impact**: Inflates parity gap count and makes general checks fail.

---

## 4. Recommended Action & Proposed Changes

1. **Fix Marker Checking**:
   - Modify `check_harness_parity.py` to resolve `expected_marker` dynamically using the harness name:
     ```python
     if manifest_adapters and harness in manifest_adapters:
         expected_marker = "GTKB-API-SKILL-ADAPTER"
     else:
         expected_marker = f"GTKB-{harness.upper()}-SKILL-ADAPTER"
     ```
     This correctly resolves to `GTKB-ANTIGRAVITY-SKILL-ADAPTER` for `antigravity` and `GTKB-CODEX-SKILL-ADAPTER` for `codex`.

2. **Remove Role Hardcoding in Antigravity Generator**:
   - Update `generate_antigravity_skill_adapters.py` to remove `ANTIGRAVITY_ROLE` filter. Make it build adapters for *all* skills defined in the registry, matching the behavior of the Codex generator. This ensures that Antigravity has the capability set for both `prime-builder` and `loyal-opposition` roles.

3. **Align tests**:
   - Update unit tests in `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` to reflect the removal of the role filter (renaming test cases and updating expected output counts).

4. **Address Suspended Harnesses**:
   - Recommend classifying Goose as suspended/ignored in the checker, or add its capability blocks as `unsupported` in the registry.

---

## 5. Owner Decision Required

We will present the choice on Goose capability declarations and dynamic generation in a separate `OWNER ACTION REQUIRED` block.
