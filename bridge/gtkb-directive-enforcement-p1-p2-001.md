# Bridge Proposal — Directive Enforcement Registry P1+P2: Registry Schema + Tool-Call Adapters

**Status:** NEW (implementation proposal derived from program GO)  
**Author:** Prime Builder (Goose / interactive override)  
**Date:** 2026-06-08  
**Document name:** `gtkb-directive-enforcement-p1-p2`  
**Supersedes:** None (first implementation slice from program GO)  
**Derives from:** `bridge/gtkb-directive-enforcement-registry-004.md` (GO), `-003` (contract)

---

## 0. Scope

This proposal covers **P1 + P2 (non-separable)** from the directive enforcement registry program per -003 §3:

- **P1:** Registry schema + initial directives + validate script + owner recovery procedure
- **P2:** Tool-call adapters (Claude PreToolUse hook + Codex hook adapter) + Bash enforcement model + read modes + tests

**Out of scope:**
- P3: Bridge proposal template + Codex review template + per-directive attestation generator
- P4: Session-start audit script + report shape
- P5: CI gate integration
- P6: ADR + DCL records
- P7: Adopter consumption pattern

**P1+P2 non-separability rationale (per -003 §3 and -004 execution conditions):** "The registry without the hooks doesn't enforce; the hooks without the registry don't have rules. They MUST land together to be useful."

---

## 1. Specification Links

| Specification | Status | Relevance |
|---|---|---|
| `SPEC-DIRECTIVE-ENFORCEMENT-REGISTRY-001` | active | Defines registry schema, directive structure, non-negotiable flag |
| `SPEC-DIRECTIVE-ENFORCEMENT-ADAPTERS-001` | active | Defines per-harness adapter contract, tool-call enforcement |
| `SPEC-DIRECTIVE-ENFORCEMENT-BASH-MODEL-001` | active | Defines parse-explicit-target strategy, dangerous patterns, manifest-gated cleanup |
| `SPEC-DIRECTIVE-ENFORCEMENT-READ-MODES-001` | active | Defines 3-mode read framework (audit/migration, live-dependency, general) |
| `REQ-DIRECTIVE-ENFORCEMENT-REGISTRY-001` | active | FR1-FR5 (registry schema, validation, recovery) |
| `REQ-DIRECTIVE-ENFORCEMENT-ADAPTERS-001` | active | FR1-FR8 (Claude/Codex hooks, Bash enforcement, read modes) |
| `DIR-ROOT-BOUNDARY-001` | active | First non-negotiable directive (must be in initial registry) |

**Requirement sufficiency:** Existing specifications are sufficient for P1+P2. No new specifications required. The -003 contract provides complete implementation detail for registry schema, adapter contract, Bash model, and read modes.

---

## 2. Prior Deliberations

- `DELIB-ROOT-BOUNDARY-ENFORCEMENT-001`: Owner directive on root boundary as non-negotiable
- `DELIB-FORMAL-ARTIFACT-APPROVAL-001`: Owner directive on formal artifact approval gate
- `DELIB-CODEX-HOOK-PARITY-FALLBACK-001`: Codex hooks not active on Windows, ADR fallback documented
- `DELIB-S324-OM-DELTA-0001-CHOICE`: Owner decision on operating model delta

**No prior deliberation contradicts the directive enforcement contract.**

---

## 3. Implementation Plan

### 3.1 P1: Registry Schema

**File:** `.gtkb/directive-registry.json`

```json
{
  "schema_version": "1.0",
  "directives": {
    "DIR-ROOT-BOUNDARY-001": {
      "title": "Root Boundary Enforcement",
      "non_negotiable": true,
      "description": "All GT-KB work must occur within E:\\GT-KB. No live dependencies on outside-root paths.",
      "rule_file": ".claude/rules/project-root-boundary.md",
      "enforcement_scopes": ["PreToolUse", "Bash", "Read"],
      "created_at": "2026-06-08T00:00:00Z",
      "created_by": "gt directive enforce init"
    },
    "DIR-FORMAL-ARTIFACT-APPROVAL-001": {
      "title": "Formal Artifact Approval Gate",
      "non_negotiable": true,
      "description": "Formal artifacts (GOV, ADR, DCL, SPEC) require explicit owner approval before mutation.",
      "rule_file": ".claude/rules/formal-artifact-approval.md",
      "enforcement_scopes": ["PreToolUse", "Bash"],
      "created_at": "2026-06-08T00:00:00Z",
      "created_by": "gt directive enforce init"
    }
  }
}
```

**Schema validation per -003 §1.2:**
- `schema_version` must be "1.0"
- Each directive must have: `title`, `non_negotiable` (bool), `description`, `rule_file`, `enforcement_scopes` (list), `created_at`, `created_by`
- `enforcement_scopes` values must be in: `["PreToolUse", "Bash", "Read", "Task"]`

**File:** `scripts/validate_directive_registry.py`

```python
def validate_registry() -> ValidationResult:
    """Validate .gtkb/directive-registry.json per -003 §1.2 schema."""
    # Check file exists, parseable JSON, schema_version matches, all required fields present
    # Return ValidationResult(valid: bool, errors: list[str])
```

**Owner recovery procedure (per -003 §1.7):**

1. If registry missing/malformed → all Write/Edit/Bash blocked
2. Owner runs: `git checkout HEAD -- .gtkb/directive-registry.json`
3. Owner runs: `python scripts/validate_directive_registry.py`
4. Re-trigger session-start audit

### 3.2 P2: Tool-Call Adapters

#### 3.2.1 Claude PreToolUse Hook

**File:** `.claude/hooks/directive-enforcement-claude-adapter.py`

```python
def check_directive_compliance(tool_input: dict, directive_id: str) -> HookDecision:
    """
    Check if tool call violates directive per registry.
    
    Returns:
        HookDecision(
            decision: "allow" | "block",
            reason: str | None,
            additionalContext: str | None
        )
    """
    # 1. Load registry from .gtkb/directive-registry.json
    # 2. Check if tool_input violates directive enforcement_scopes
    # 3. Apply Bash enforcement model if tool == "Bash"
    # 4. Apply read modes if tool == "Read" | "Grep" | "Glob"
    # 5. Return allow/block decision
```

**Registration:** Add to `.claude/settings.json` under `hooks.PreToolUse`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/directive-enforcement-claude-adapter.py"
          }
        ]
      }
    ]
  }
}
```

#### 3.2.2 Codex Hook Adapter

**File:** `.codex/agent-red-hooks/directive-enforcement-codex-adapter.py`

Same logic as Claude adapter, but reads from Codex hook context. Per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, Codex hooks are not active on Windows. Adapter ships forward-compatible (active when Codex hooks come online; CI gate covers gap until then).

**Registration:** Add to `.codex/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "python .codex/agent-red-hooks/directive-enforcement-codex-adapter.py"
          }
        ]
      }
    ]
  }
}
```

#### 3.2.3 Bash Enforcement Model (per -003 §1.4)

**File:** `scripts/directive_enforcement/bash_model.py`

```python
def enforce_bash_command(command: str, registry: DirectiveRegistry) -> BashVerdict:
    """
    Apply 5-step Bash enforcement model per -003 §1.4.
    
    Steps:
    1. Parse explicit write/delete/move/copy targets
    2. Block known dangerous outside-root patterns
    3. Check manifest-gated cleanup commands
    4. Fail-closed on unparseable write-like commands
    5. Allow read-only audit commands
    
    Returns:
        BashVerdict(
            allowed: bool,
            reason: str | None,
            parsed_targets: list[str]
        )
    """
```

**Dangerous patterns (per -003 §1.4 Step 2):**

```python
DANGEROUS_PATTERNS = [
    r"E:\\Claude-Playground\\",
    r"C:\\Users\\[^\\]+\\\.codex\\agent-red-hooks\\",
    r"C:\\Users\\[^\\]+\\\.claude\\projects\\E--GT-KB",
    r"C:\\Users\\[^\\]+\\\.claude\\agent-red-hooks\\",
]
```

**Manifest-gated cleanup (per -003 §1.4 Step 3):**

Commands that delete archive/home/worktree state must include `.gtkb-cleanup-manifest:` annotation:

```bash
git worktree remove "$wt" # .gtkb-cleanup-manifest:bridge/critical-remediation-root-isolation-006.md
```

#### 3.2.4 Read Modes (per -003 §1.5)

**File:** `scripts/directive_enforcement/read_modes.py`

```python
def determine_read_mode(tool_input: dict, session_context: SessionContext) -> ReadMode:
    """
    Determine read mode per -003 §1.5.
    
    Modes:
    - AUDIT_MIGRATION: Active cleanup work (Phases A-F; cleanup-manifest bridge)
    - LIVE_DEPENDENCY: Normal operation reading outside-root paths (BLOCKED)
    - GENERAL: Reads of OS/general infra (Python, pip cache, OS libraries)
    
    Returns:
        ReadMode.AUDIT_MIGRATION | ReadMode.LIVE_DEPENDENCY | ReadMode.GENERAL
    """
```

**Mode determination logic:**
1. If session_context cites cleanup-manifest reference → `AUDIT_MIGRATION` (allowed)
2. If path matches `live-dependency-block` pattern (e.g., `Path.home()`) → `LIVE_DEPENDENCY` (blocked)
3. Default → `GENERAL` (allowed)

**Conservative default:** When ambiguous, reads are allowed (less destructive than writes), but live-dependency patterns are still blocked.

### 3.3 Test Contract

**File:** `tests/framework/test_directive_registry_schema.py`

- `test_registry_schema_valid`: Valid registry parses successfully
- `test_registry_schema_version_mismatch`: Wrong schema_version fails validation
- `test_registry_missing_required_fields`: Missing fields fail validation
- `test_registry_malformed_json`: Invalid JSON fails validation
- `test_registry_missing_file`: Missing registry file fails validation (fail-closed)

**File:** `tests/framework/test_directive_enforcement_adapters.py`

- `test_claude_adapter_allows_compliant_write`: Write within root allowed
- `test_claude_adapter_blocks_outside_root_write`: Write to `E:\Claude-Playground` blocked
- `test_claude_adapter_allows_compliant_bash`: Bash command within root allowed
- `test_claude_adapter_blocks_dangerous_bash_pattern`: Bash command matching dangerous pattern blocked
- `test_claude_adapter_blocks_unparseable_write_like`: Unparseable write-like command blocked (fail-closed)
- `test_claude_adapter_allows_read_only_audit`: Read-only audit command allowed
- `test_claude_adapter_blocks_live_dependency_read`: Read of `Path.home()` blocked
- `test_claude_adapter_allows_general_read`: Read of Python interpreter files allowed
- `test_codex_adapter_parity`: Codex adapter produces same decisions as Claude adapter for same inputs
- `test_non_negotiable_no_runtime_override`: `--override-directive` flag rejected for `non_negotiable: true`
- `test_overrideable_ack_directive`: `--ack-directive` flag accepted for `non_negotiable: false`

**File:** `tests/framework/test_bash_enforcement_model.py`

- `test_parse_explicit_targets`: `cp src dst` parsed correctly
- `test_parse_powershell_targets`: `Copy-Item -Destination dst` parsed correctly
- `test_block_dangerous_patterns`: Commands matching `DANGEROUS_PATTERNS` blocked
- `test_manifest_gated_cleanup_allowed`: Cleanup command with `.gtkb-cleanup-manifest:` annotation allowed
- `test_manifest_gated_cleanup_blocked`: Cleanup command without annotation blocked (fail-closed)
- `test_fail_closed_unparseable`: Unparseable write-like command blocked
- `test_allow_read_only_audit`: `ls`, `find`, `grep` commands allowed

**File:** `tests/framework/test_read_modes.py`

- `test_audit_migration_mode_allowed`: Cleanup-manifest context allows outside-root read
- `test_live_dependency_mode_blocked`: Normal operation reading `Path.home()` blocked
- `test_general_mode_allowed`: OS/Python infra reads allowed
- `test_conservative_default`: Ambiguous context defaults to allowed (but live-dependency still blocked)

**Test mapping:** Each test derives from REQ-DIRECTIVE-ENFORCEMENT-REGISTRY-001 FR1-FR5 (registry schema, validation, recovery) and REQ-DIRECTIVE-ENFORCEMENT-ADAPTERS-001 FR1-FR8 (Claude/Codex hooks, Bash enforcement, read modes).

---

## 4. Acceptance Criteria

1. `.gtkb/directive-registry.json` exists with schema_version "1.0"
2. Registry contains `DIR-ROOT-BOUNDARY-001` and `DIR-FORMAL-ARTIFACT-APPROVAL-001` (per -004 execution conditions)
3. `scripts/validate_directive_registry.py` validates registry successfully
4. Claude PreToolUse hook registered and blocks outside-root writes
5. Codex hook adapter registered (forward-compatible; CI gate covers Windows gap)
6. Bash enforcement model blocks dangerous patterns, requires manifest-gated cleanup, fails-closed on unparseable
7. Read modes correctly classify audit/migration (allowed), live-dependency (blocked), general (allowed)
8. No runtime override for `non_negotiable: true` directives
9. All schema validation tests pass (5 tests)
10. All adapter tests pass (11 tests)
11. All Bash enforcement tests pass (7 tests)
12. All read mode tests pass (4 tests)
13. Owner recovery procedure documented and tested

---

## 5. Risk Assessment

**Medium risk:** This introduces a new enforcement layer that affects all tool calls. Fail-closed semantics ensure conservative behavior, but false positives may block legitimate work.

**Mitigation:**
- Comprehensive test coverage (27 tests) validates all enforcement paths
- Owner recovery procedure documented for registry corruption
- Bash false-positive trade-off accepted per -003 §5 ("occasional false positives over silent violations")
- Codex hook parity gap accepted per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (CI gate covers Windows gap)

---

## 6. Implementation Constraints

- **P1+P2 non-separable:** Registry and adapters must ship together
- **Initial directives must include DIR-ROOT-BOUNDARY-001:** Per -004 execution conditions
- **No runtime override for non-negotiable:** Per -003 §1.6
- **Fail-closed defaults:** Unparseable/malformed inputs block tool calls
- **Codex adapter forward-compatible:** Active when Codex hooks come online; CI gate covers gap
- **Bash false-positives expected:** Operators may need to split complex one-liners

---

## 7. Verification Plan

1. Run `pytest tests/framework/test_directive_registry_schema.py -v`
2. Run `pytest tests/framework/test_directive_enforcement_adapters.py -v`
3. Run `pytest tests/framework/test_bash_enforcement_model.py -v`
4. Run `pytest tests/framework/test_read_modes.py -v`
5. Run `python scripts/validate_directive_registry.py` on live registry
6. Manual test: Attempt write to `E:\Claude-Playground` → should be blocked
7. Manual test: Attempt Bash command with dangerous pattern → should be blocked
8. Manual test: Attempt read of `Path.home()` in normal operation → should be blocked
9. Manual test: Attempt read of `Path.home()` with cleanup-manifest context → should be allowed

---

## 8. Owner Decisions / Input

**None required for this slice.** Owner decisions captured in program GO `-004` and -003 §7 (confirm program prioritization, confirm initial registry contents).

---

## 9. Reversibility

This slice is additive (new registry, new hooks, new scripts). No existing code modified except `.claude/settings.json` and `.codex/hooks.json` (hook registration). Hooks can be disabled by removing registration entries.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
