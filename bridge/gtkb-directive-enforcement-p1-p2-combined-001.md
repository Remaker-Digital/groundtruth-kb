NEW

# Implementation Proposal — GT-KB Directive Enforcement Registry P1+P2 Combined

**Status:** NEW
**Author:** Prime Builder (goose/pb)
**Session:** S509 (2026-06-07)
**Document name:** `gtkb-directive-enforcement-p1-p2-combined`
**Builds on:** `bridge/gtkb-directive-enforcement-registry-001` through `-004` (GO)

## 1. Scope

This proposal implements the registry and tool-call adapters for Directive Enforcement (P1+P2), providing Layer 1 enforcement for Claude Code and a catch-all audit for all harnesses.

## 2. Deliverables

### 2.1 Canonical Registry (`.gtkb/directive-registry.json`)

Primary store for enforcement rules.

```json
{
  "schema_version": "1.0",
  "directives": [
    {
      "id": "DIR-ROOT-BOUNDARY-001",
      "name": "Project Root Boundary",
      "description": "All active files must be within E:\\GT-KB.",
      "non_negotiable": true,
      "enforcement_modes": ["tool-call", "bash", "audit"],
      "patterns": {
        "allowed_root": "E:\\GT-KB",
        "blocked_absolute": [
          "E:\\Claude-Playground\\",
          "C:\\Users\\",
          "/etc/",
          "/home/"
        ]
      }
    },
    {
      "id": "DIR-FORMAL-ARTIFACT-APPROVAL-001",
      "name": "Formal Artifact Approval",
      "description": "Mutations to ADR, DCL, and SPEC require explicit bridge-verdict evidence.",
      "non_negotiable": true,
      "enforcement_modes": ["tool-call", "audit"],
      "patterns": {
        "governed_paths": [
          ".claude/rules/",
          "docs/adr/",
          "docs/dcl/",
          "docs/specs/"
        ]
      }
    }
  ]
}
```

### 2.2 Claude Adapter (`.claude/hooks/directive-enforcement-claude-adapter.py`)

Registered as a `PreToolUse` hook.

- Intercepts `Write`, `Edit`, `Bash`, `Delete`, `Move`, `Copy`.
- Validates path arguments against `DIR-ROOT-BOUNDARY-001`.
- Blocks unparseable bash commands containing file redirection or path delimiters that reference blocked locations.
- Returns non-zero and descriptive error message on violation.

### 2.3 Validation Script (`scripts/validate_directive_registry.py`)

Used by owner and CI to ensure registry integrity.

- Schema validation (pydantic-based).
- Path sanity checks (ensures allowed_root exists and is absolute).
- Dependency verification (ensures adapters are registered).

### 2.4 Test Suite

- `tests/framework/test_directive_registry_schema.py`
- `tests/framework/test_claude_directive_adapter.py` (mocking tool calls)
- `tests/framework/test_bash_enforcement_parser.py`

## 3. Execution Plan

1. Create `.gtkb/` directory at root.
2. Write `.gtkb/directive-registry.json` with initial directives.
3. Implement `scripts/validate_directive_registry.py`.
4. Implement tool-call parsing and path validation logic in a shared module `groundtruth_kb.enforcement`.
5. Implement the Claude adapter hook.
6. Register the hook in `.claude/settings.json`.
7. Verify enforcement with test suite.

## 4. Reversibility

- Hook can be deregistered in `.claude/settings.json`.
- Registry and scripts can be removed.
- All changes are additive.

## 5. Decision Needed

No owner decision needed beyond approval of this implementation proposal. 
Proceeding with combine P1+P2 as requested in LO findings closure F6.
