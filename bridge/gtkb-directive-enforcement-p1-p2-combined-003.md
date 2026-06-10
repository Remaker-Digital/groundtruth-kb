REVISED

# Implementation Proposal — GT-KB Directive Enforcement Registry P1+P2 Combined

**Status:** REVISED
**Document name:** `gtkb-directive-enforcement-p1-p2-combined`
**Version:** 003
**Author:** Prime Builder (antigravity, harness C)
**Session:** S509 (2026-06-09)
**Builds on:** `bridge/gtkb-directive-enforcement-registry-004.md` (GO)

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — File bridge protocol governance (config/governance/gov-file-bridge-authority-001.md)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified proposals must have spec-to-test mapping
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Placement contract for application isolation
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — Harness onboarding requirements and registry governance
- `REQ-DIRECTIVE-ENFORCEMENT-P1` — Registry and tool-call adapter enforcement for Layer 1.
- `REQ-DIRECTIVE-ENFORCEMENT-P2` — Catch-all audit adapter hook for all harnesses.
- `DELIB-S509-B1-B5-TRIAGE` — S509 triage deliberation.

## 2. Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-CORE`
- **Work Item:** `WI-4327` (or corresponding directive registry WI)
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `groundtruth-kb/pyproject.toml`
  - `groundtruth-kb/src/groundtruth_kb/enforcement/`
  - `.gtkb/directive-registry.json`
  - `.claude/hooks/directive-enforcement-claude-adapter.py`
  - `scripts/validate_directive_registry.py`
  - `.claude/settings.json`
  - `tests/framework/test_directive_registry_schema.py`
  - `tests/framework/test_claude_directive_adapter.py`
  - `tests/framework/test_bash_enforcement_parser.py`

All target paths reside under the project root (`E:\\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## 3. Requirement Sufficiency

| Requirement | Source | Satisfied By | Test Coverage |
|-------------|--------|--------------|---------------|
| REQ-DIRECTIVE-ENFORCEMENT-P1 | `bridge/gtkb-directive-enforcement-registry-004.md` | `.gtkb/directive-registry.json` + `PreToolUse` hook | `tests/framework/test_directive_registry_schema.py` |
| REQ-DIRECTIVE-ENFORCEMENT-P2 | `bridge/gtkb-directive-enforcement-registry-004.md` | `.claude/hooks/directive-enforcement-claude-adapter.py` | `tests/framework/test_claude_directive_adapter.py` + `tests/framework/test_bash_enforcement_parser.py` |

## 4. Deliverables

### 4.1 Canonical Registry (`.gtkb/directive-registry.json`)
Primary store for enforcement rules containing non-negotiable patterns (such as root boundary validation).

### 4.2 Claude Adapter (`.claude/hooks/directive-enforcement-claude-adapter.py`)
Registered as a `PreToolUse` hook to intercept file mutations and bash commands, validating them against the registry and raising non-zero exit codes/errors on violation.

### 4.3 Validation Script (`scripts/validate_directive_registry.py`)
Schema validation using Pydantic, enforcing structural compliance and path sanity checks.

### 4.4 Hook Registration in `.claude/settings.json`
Hook registration is strictly **additive**. It appends the adapter to the existing array of `PreToolUse` hooks in `.claude/settings.json`, ensuring that existing hooks remain unperturbed and active.

### 4.5 Dependency Management
We will declare `pydantic>=2.0` as a dependency in `groundtruth-kb/pyproject.toml` to support the validation script, ensuring standard toolchain support.

## 5. Specification-Derived Verification Plan

### Automated Tests
Execute the pytest suite covering the schema validation, hook behavior, and parser behavior:
```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_directive_registry_schema.py -v
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_claude_directive_adapter.py -v
groundtruth-kb\.venv\Scripts\python.exe -m pytest tests/framework/test_bash_enforcement_parser.py -v
```

### Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| REQ-DIRECTIVE-ENFORCEMENT-P1 | `tests/framework/test_directive_registry_schema.py` | `test_schema_load`, `test_schema_invalid_pattern` |
| REQ-DIRECTIVE-ENFORCEMENT-P2 | `tests/framework/test_claude_directive_adapter.py` | `test_pre_tool_use_allow`, `test_pre_tool_use_block_violation` |
| REQ-DIRECTIVE-ENFORCEMENT-P2 | `tests/framework/test_bash_enforcement_parser.py` | `test_bash_parser_allowed_cmd`, `test_bash_parser_blocked_path` |

## target_paths

- `groundtruth-kb/pyproject.toml`
- `groundtruth-kb/src/groundtruth_kb/enforcement/__init__.py`
- `.gtkb/directive-registry.json`
- `.claude/hooks/directive-enforcement-claude-adapter.py`
- `scripts/validate_directive_registry.py`
- `.claude/settings.json`
- `tests/framework/test_directive_registry_schema.py`
- `tests/framework/test_claude_directive_adapter.py`
- `tests/framework/test_bash_enforcement_parser.py`

## Requirement Sufficiency

Existing requirements sufficient
