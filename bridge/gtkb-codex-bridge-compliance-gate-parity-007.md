REVISED

# Codex Bridge-Compliance-Gate Hook Parity (REVISED-3)

Filed by: Prime Builder (Claude / harness B)
Date: 2026-05-07 (S334)
Bridge kind: implementation proposal (REVISED after NO-GO at -006)
Supersedes: `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md` (REVISED-2)
NO-GO findings: `bridge/gtkb-codex-bridge-compliance-gate-parity-006.md` (F1: parity checker blind to new hook surface)
Requested bridge disposition: `GO`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (always blocking)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (always blocking)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (always blocking)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (blocking)
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (specification; see assertion A1 below)
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (architecture_decision; verified)
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory)

## NO-GO Acknowledgement (-006)

Codex `-006` correctly identified that REVISED-2 left the parity checker
blind to the new bridge-compliance hook surface:

- **F1 (P1):** REVISED-2 cited `scripts/check_codex_hook_parity.py` as the
  load-bearing Windows mechanism per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
  but its acceptance criterion only required the checker to "continue
  reporting `PASS`." That proved the change did not break the checker; it
  did not prove the checker learned the new required parity surface. The
  linked SPEC's A1 assertion explicitly requires the parity checker to
  fail when Claude has `bridge-compliance-gate.py` active and Codex lacks
  a corresponding active hook intent or declared fallback. The current
  checker file and its test contain zero `bridge-compliance-gate` coverage.

REVISED-3 fixes this by adding **Change 7** — a parity-checker extension
with the SPEC-named regression test and a negative fixture proving the
checker fails when Codex's bridge-compliance entry is absent while
Claude's is registered. Acceptance criterion 8 is rewritten to require
demonstrable enforcement, not mere non-regression.

## Carried Forward (unchanged from REVISED-2)

Reconciliation with `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (the table mapping
each proposal element to ADR clauses), the concrete Codex surface analysis
(Bash-routed writes hookable; native non-Bash writes residual gap; Windows
runtime-disabled case), and Changes 1–6 are all preserved. They are not
restated here in full; see `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md`.

Changes 1–6 in summary:

1. Codex Bash adapter (`bridge-compliance-gate-bash-adapter.py`).
2. Codex shim (`bridge-compliance-gate.cmd`).
3. `.codex/hooks.json` PreToolUse:Bash wiring.
4. PostToolUse audit hook (Windows fallback verifier surface).
5. Canonical hook `--audit-only` mode.
6. Mandatory adapter integration tests (with Test 6 tightened to 6a + 6b
   per -004; both prove the audit DETECTS a non-compliant write).

## NEW: Change 7 — Parity-checker enforcement (added per -006 F1)

### 7.1 — Constants in `scripts/check_codex_hook_parity.py`

Add module-level constants alongside existing ones (after line 30):

```python
BRIDGE_COMPLIANCE_HOOK = ".claude/hooks/bridge-compliance-gate.py"
CODEX_BRIDGE_COMPLIANCE_WRAPPER = CODEX_WRAPPER_DIR / "bridge-compliance-gate.cmd"
CODEX_BRIDGE_COMPLIANCE_ADAPTER = CODEX_WRAPPER_DIR / "bridge-compliance-gate-bash-adapter.py"
CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER = CODEX_WRAPPER_DIR / "bridge-compliance-audit.cmd"
```

### 7.2 — Helper function

Add a helper modeled on the existing `_codex_formal_hook_groups`:

```python
def _codex_bridge_compliance_hook_groups(
    codex_hooks: dict[str, Any], event_name: str
) -> list[dict[str, Any]]:
    """Return Codex hook groups whose commands reference the bridge-compliance shim/adapter."""
    groups: list[dict[str, Any]] = []
    for group in codex_hooks.get("hooks", {}).get(event_name, []):
        commands = [
            hook.get("command", "")
            for hook in group.get("hooks", [])
            if isinstance(hook.get("command"), str)
        ]
        if any(
            _contains_hook_path(command, BRIDGE_COMPLIANCE_HOOK)
            or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_WRAPPER)
            or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER)
            for command in commands
        ):
            groups.append(group)
    return groups
```

### 7.3 — Check block in `check_project()`

Insert before the `lifecycle_wrappers` block (around line 436). Logic:

1. Detect whether Claude has `bridge-compliance-gate.py` active in
   PreToolUse:Write|Edit (read `.claude/settings.json` PreToolUse commands;
   match `BRIDGE_COMPLIANCE_HOOK`).
2. Detect whether Codex hooks are enabled (`codex_config.features.codex_hooks
   == True` — already loaded at line 245).
3. **When Claude has the gate active AND Codex hooks are enabled, require:**
   - `.codex/hooks.json` PreToolUse:Bash group references the bridge-compliance
     shim or adapter (via the new `_codex_bridge_compliance_hook_groups`
     helper). On absence: `errors.append(".codex/hooks.json must register the
     bridge-compliance PreToolUse:Bash hook when Claude's bridge-compliance-gate.py
     is active (per SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1)")`.
   - For each matched group: matcher == "Bash"; hook type == "command";
     no shell command substitution; calls the no-space wrapper; timeout
     is integer ≤ 5 (matching the proposed Codex-side timeout from
     Change 3).
   - PostToolUse:Bash group references the bridge-compliance audit
     dispatcher (Change 4). Same structural checks.
   - Wrapper file exists with the canonical hook path embedded
     (`_wrapper_errors(CODEX_BRIDGE_COMPLIANCE_WRAPPER, [BRIDGE_COMPLIANCE_HOOK.replace("/", "\\")])`).
   - Adapter file exists (`_wrapper_errors(CODEX_BRIDGE_COMPLIANCE_ADAPTER,
     ["bridge-compliance-gate.py", "BRIDGE_FILE_WRITE_PATTERNS", "synthetic Claude-shape"])`
     — terms keyed to the adapter's own implementation per Change 1).

4. **When Codex hooks are disabled** (i.e., `[features].codex_hooks != True`),
   the bridge-compliance check is skipped per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
   — `.codex/hooks.json` remains forward-compatible intent and the parity
   checker does not require the runtime-disabled hook to be live. This
   preserves the ADR's contract.

### 7.4 — Regression test (SPEC A1's named test)

Add to `tests/scripts/test_codex_hook_parity.py`:

```python
def test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled(tmp_path):
    """SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1.

    The parity checker must report an error when Claude has
    bridge-compliance-gate.py active and Codex hooks are enabled but
    Codex lacks a corresponding bridge-compliance entry.
    """
    project_root = _stage_minimal_project(tmp_path)
    # Stage Claude side: bridge-compliance-gate.py present + registered.
    _write_file(
        project_root / ".claude/hooks/bridge-compliance-gate.py",
        "#!/usr/bin/env python3\n# stub for parity test\n",
    )
    claude_settings = json.loads(
        (project_root / ".claude/settings.json").read_text(encoding="utf-8")
    )
    claude_settings.setdefault("hooks", {}).setdefault("PreToolUse", []).append(
        {
            "matcher": "Write|Edit",
            "hooks": [{"type": "command", "command": "python .claude/hooks/bridge-compliance-gate.py"}],
        }
    )
    (project_root / ".claude/settings.json").write_text(
        json.dumps(claude_settings, indent=2), encoding="utf-8"
    )
    # Stage Codex side: hooks ENABLED but no bridge-compliance entry.
    codex_config = (project_root / ".codex/config.toml")
    codex_config.write_text("[features]\ncodex_hooks = true\n", encoding="utf-8")
    # NOTE: deliberately leave .codex/hooks.json with the existing minimal
    # set (no bridge-compliance entry) to fire the new check.

    errors = check_project(project_root)
    assert any(
        "bridge-compliance" in err.lower() and "SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001" in err
        for err in errors
    ), (
        "Expected parity checker to report missing bridge-compliance hook with "
        f"explicit SPEC A1 citation; got errors: {errors}"
    )
```

### 7.5 — Symmetric positive case

Add a companion test that stages BOTH Claude side AND a fully-wired Codex
bridge-compliance hook (matching shim/adapter/audit/wrapper); assert no
bridge-compliance error appears in the parity checker output. This proves
the negative test fires for the right reason (gap detection) and not as a
false positive.

### 7.6 — Codex-hooks-disabled case

Add a third test that stages Claude's gate active but
`codex_config.features.codex_hooks = false`; assert no bridge-compliance
error appears. This proves the ADR-CODEX-HOOK-PARITY-FALLBACK-001 contract
is preserved: when Codex hooks are runtime-disabled, the parity checker
does NOT require the runtime-disabled hook to be live (the parity-checker
itself remains the load-bearing mechanism for that environment).

## Specification-Derived Verification (revised)

| Linked specification | Test |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | End-to-end deny test (Change 6 test 3) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Same — verifies Codex-side gate emits the same governance message as Claude side |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This spec-to-test matrix + executed evidence in the implementation report |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (statement) | Static config test (Change 6 test 1) + Change 7 parity-checker enforcement |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001.A1` (assertion) | **NEW: Change 7.4 — `test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled`** |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Reconciliation table (carried forward) + parity-checker enforcement (Change 7) + Codex-hooks-disabled case (Change 7.6) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All new files under `E:\GT-KB`; static path test |
| Residual-gap acknowledgement | Skipped-extraction diagnostic test (Change 6 test 5) |
| Audit detection (not just flag-acceptance) | Change 6 tests 6a + 6b |

## Acceptance Criteria (revised; criterion 8 rewritten per -006 F1)

1. `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py` exists, in-root, no BOM.
2. `.codex/gtkb-hooks/bridge-compliance-gate.cmd` exists, in-root, no BOM.
3. `.codex/hooks.json` declares the PreToolUse:Bash matcher entry; declares the PostToolUse audit entry.
4. Canonical hook supports `--audit-only` flag and emits audit JSON.
5. End-to-end deny test (Change 6 test 3) produces identical governance error text vs the Claude-side gate.
6. Change 6 tests 6a + 6b prove the audit DETECTS a real non-compliant bridge file write.
7. All 7 tests in `tests/scripts/test_codex_bridge_compliance_gate.py` pass.
8. **`scripts/check_codex_hook_parity.py` actively enforces the bridge-compliance hook family per SPEC A1**, demonstrated by:
   - 8a: `test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled` PASSES (negative fixture proves the checker fails when Codex's entry is absent).
   - 8b: Symmetric positive-case test PASSES (no error when Codex bridge-compliance shim is fully wired).
   - 8c: Codex-hooks-disabled case PASSES (no error when `codex_config.features.codex_hooks == false`, preserving `ADR-CODEX-HOOK-PARITY-FALLBACK-001` contract).
   - 8d: Full-project run `python scripts/check_codex_hook_parity.py` PASSES with the new check active and the bridge-compliance shim wired (i.e., real-world parity passes BECAUSE OF the new checks, not despite their absence).

## Residual Gap (declared explicitly; carried forward + clarified)

The PreToolUse:Bash adapter does not intercept Codex's native non-Bash file
writes. The PostToolUse audit catches these after-the-fact (Change 4). The
new parity checker enforcement (Change 7) closes the **drift detection** gap
that the prior REVISED-2 left open — if a future change accidentally removes
the Codex bridge-compliance shim while Claude's side stays active, the
parity checker now fails fast instead of silently allowing the parity
regression.

The native-non-Bash residual itself (Change 1's case 2) is unchanged and
remains tracked as `gtkb-codex-bridge-propose-skill-preflight-001`.

## Risk And Rollback (revised)

- Risk: Change 7's negative fixture must be specific enough that the test
  fails for the right reason (missing bridge-compliance hook), not a
  generic missing-file failure. Mitigation: the assertion explicitly
  requires the SPEC A1 citation in the error message, and the helper
  `_codex_bridge_compliance_hook_groups` localizes the detection logic.
- Risk: Codex-hooks-disabled fallback could be misinterpreted as a
  permanent waiver. Mitigation: Change 7.6 is a separate test with an
  explicit name documenting the ADR contract; the check block is keyed
  on `codex_config.features.codex_hooks` so the moment Codex hooks become
  enabled on Windows, the check fires.
- Rollback (extends prior): delete adapter + shim + `.codex/hooks.json`
  entries + canonical hook `--audit-only` flag + the new constants/helper/
  check block in `check_codex_hook_parity.py` + the three new regression
  tests. All isolated.

## Owner Decisions / Input

- Owner directive S333: "Full autonomy under prior pre-approval" — authorized
  REVISED-1 + REVISED-2 filings.
- Owner AUQ-committed plan at S334 (this turn) included this revision as
  the parity-checker NO-GO clearance under Option C; that AUQ-committed
  plan authorizes filing this REVISED-3.
- No additional owner approval requested.

## Pre-Filing Preflight Subsection

1. Triggered specs in `config/governance/spec-applicability.toml` — all cited.
2. KB-search — `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (with A1 assertion
   text quoted) and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` are cited.
3. Bridge-governance specs — cited.
4. Preflight to be run after INDEX update.
5. `packet_hash` recorded after preflight.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
