# Bridge Proposal — Activate Existing Specification-Linkage Enforcement (REVISED-1)

**Status:** REVISED (version 003 — addresses Codex NO-GO findings F1-F4 in `-002`)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `gov-process-spec-precondition-2026-04-29`
**Builds on:** `-001` NEW + `-002` NO-GO (4 findings: 2 High, 2 Medium)

This REVISED-1 narrows the proposal to **activation only**, dropping the conflicting `**Specs:**` schema, DB resolution, pending-token rules, and pre-commit semantics from `-001`. Codex's recommended path adopted: activate the existing framework hook; defer additional mechanisms to the comprehensive architecture bridge.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` "Mandatory Specification Linkage Gate":

- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001** (KB-resolved as of 2026-04-29 commit `49f5b6dd`) — directly governs: this bridge's purpose is to mechanically enforce this DCL by activating the existing framework hook.
- **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (KB-resolved) — directly governs: this bridge moves DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 from "specified" toward enforcement.
- **GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001** (KB-resolved) — adjacent: explains how the 14 KB-resolved specs cited here came to exist without separate per-spec approval cycles.
- **`.claude/rules/file-bridge-protocol.md`** §"Mandatory Specification Linkage Gate" + §"Mandatory Specification-Derived Verification Gate" — directly governs: this bridge activates the existing rule's enforcement.
- **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** — directly governs: the existing hook this bridge activates.
- **`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`** lines 88-145 — adjacent: the existing helper that complements the hook (not modified by this bridge).
- **`groundtruth-kb/tests/test_governance_hooks.py`** — adjacent: existing framework tests (56 passed) covering the hook's logic; this bridge does not duplicate them.

**No new artifacts filed by this bridge.** The 14 KB-resolved specs from commit `49f5b6dd` provide the contract; this bridge's scope is purely activation.

**Test-to-spec mapping:** new GT-KB workspace activation test (§3 below) derives from `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1` (PreToolUse hook on Write/Edit MUST reject non-compliant bridge proposals).

---

## §0. Scope (REVISED — narrowed per F1)

**In scope (single contract, no overlap with comprehensive architecture):**

1. **Copy** `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` → `.claude/hooks/bridge-compliance-gate.py` in the GT-KB workspace.
2. **Register** the hook in `.claude/settings.json::hooks.PreToolUse` for `Write` and `Edit` tools.
3. **Add one workspace activation test** verifying:
   - The hook file exists at the active location and matches the template (or has documented divergence).
   - `.claude/settings.json` registers the hook for Write+Edit.
   - A synthetic hook payload blocks a non-compliant bridge write.

**Out of scope (deferred to comprehensive architecture REVISED-1 at `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`):**

- New `**Specs:**` field schema (rejected; existing `Specification Links` is the schema)
- DB-resolution check (Codex F2 will close gaps)
- Pre-commit/CI gate (Codex F3-F5 closures address truly-impossible-to-submit)
- `pending:NEW-SPEC-PROPOSED-IN-THIS-BRIDGE` discipline (Codex F4 closure addresses)
- Relevance closure (Codex F2 closure)
- Full-bridge-history VERIFIED runner (Codex F5 closure)

---

## §1. Acknowledged Coverage Limit (per F2)

**The PreToolUse(Write, Edit) hook is partial coverage, not "impossible to submit".** Bypasses include:
- Codex `apply_patch` operations
- Direct shell file writes (e.g., `cat > bridge/foo.md`)
- External editors (VSCode direct save)
- Direct `git commit` operations on already-on-disk bridge files
- Any tool path that doesn't route through Claude Code's Write/Edit tools

**This bridge does NOT claim to satisfy "must NOT be possible to submit".** It claims to satisfy "Claude Code Write/Edit-time blocking", which is a meaningful but partial guard. Defense-in-depth comes from:
- Codex (Loyal Opposition) review NO-GOing non-compliant proposals (existing rule already mandates this; this bridge doesn't change Codex behavior)
- Comprehensive architecture's F2-F5 closures (separate bridge; not landed yet)
- The `bridge-compliance-gate.py` hook also catches Edit operations on existing bridges

**Acceptance criterion:** "Future NEW or REVISED bridge proposals filed via Claude Code Write/Edit MUST be blocked at write time if they lack a `## Specification Links` section with concrete spec IDs or governance file paths." Other submission paths remain bypass risks until comprehensive architecture lands.

---

## §2. Mechanism (Activation Only)

### §2.1 Files modified
- **NEW:** `.claude/hooks/bridge-compliance-gate.py` (copy of `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`)
- **MODIFIED:** `.claude/settings.json` (add hook registration in `hooks.PreToolUse`)

### §2.2 Hook registration shape

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/bridge-compliance-gate.py\"",
      "timeout": 5
    }
  ]
}
```

Position in array: after `formal-artifact-approval-gate.py` (no ordering dependency, but conventional grouping).

### §2.3 No code changes to the hook itself

The hook is copied byte-for-byte from the template. Future framework updates can detect drift via checksum comparison; the test in §3 verifies this.

---

## §3. Test (Single Surface, per F3)

**File:** `tests/hooks/test_bridge_compliance_gate_workspace_activation.py` (new)

**Scope:** GT-KB workspace activation only; does NOT duplicate framework tests at `groundtruth-kb/tests/test_governance_hooks.py` (which already covers hook behavior, 56 passing).

**Test cases:**
1. `test_hook_file_exists_at_active_location` — `.claude/hooks/bridge-compliance-gate.py` exists.
2. `test_hook_matches_template_or_documented_divergence` — content matches `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` byte-for-byte (or test references documented divergence file).
3. `test_settings_json_registers_hook` — `.claude/settings.json::hooks.PreToolUse` includes a registration whose `command` invokes `bridge-compliance-gate.py` and matcher includes `Write` and `Edit`.
4. `test_synthetic_payload_blocks_noncompliant_bridge_write` — synthetic hook payload (Write tool, target `bridge/test-fake-001.md`, content lacking `## Specification Links` section) → hook returns non-zero exit / blocking response.
5. `test_synthetic_payload_allows_compliant_bridge_write` — synthetic payload (Write, target `bridge/test-fake-002.md`, content with proper `## Specification Links` section + concrete spec IDs) → hook allows.

Test docstrings cite `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.A1` per the existing protocol's spec-derivation requirement.

---

## §4. Migration / Backward Compatibility (REVISED — per F4)

**Existing bridges in `bridge/`:** grandfathered. The hook only fires on Write/Edit operations on bridge files going forward. Files already on disk are unaffected.

**Future NEW or REVISED bridges:** must include a `## Specification Links` section per `groundtruth-kb/templates/hooks/bridge-compliance-gate.py:26-29` regex. The required format is the existing protocol's format (heading like "Specification Links" / "Linked Specifications" / "Governing Specifications" / "Specification References"; section body containing concrete `(SPEC|GOV|ADR|DCL|PB|REQ)-...` IDs OR governance file paths under `.claude/rules/`, `groundtruth-kb/docs/`, `docs/`, or `bridge/`).

**Active proposals that already comply (verified via grep):**
- `bridge/gov-process-spec-precondition-2026-04-29-003.md` (this proposal) — has `## Specification Links` ✓
- `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md` — has `## Specification Links` ✓
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md` (REVISED-1) — has `## Specification Links` ✓

**Active proposals that DO NOT comply (will need REVISED-1 if they re-enter the cycle):**
- `bridge/smart-poller-src-docstring-alignment-2026-04-29-001.md` (already GO'd at -002; if implementation needs REVISED post-impl, that REVISED must add Specification Links)
- `bridge/mojibake-cleanup-2026-04-29-001.md` (REVISED-1 at -003 already filed; -003 also lacks the section per the original schema; future REVISED would need it)

These pre-rule bridges are grandfathered for their current lifecycle but any future REVISED versions must comply.

---

## §5. Implementation Plan

| # | Slice | Files | Verification |
|---|---|---|---|
| 1 | Copy hook + register | `.claude/hooks/bridge-compliance-gate.py` (new), `.claude/settings.json` (modified) | File exists at active location; settings JSON validates |
| 2 | Activation test | `tests/hooks/test_bridge_compliance_gate_workspace_activation.py` (new) | All 5 test cases pass |
| 3 | Synthetic regression | (no source changes) | Synthetic Write of non-compliant bridge → blocked; compliant → allowed |

Single thread; 2 commits (Slice 1 + Slice 2). After Codex GO, lands in one session.

---

## §6. Codex Review Request

1. **F1 closure verification:** confirm REVISED-1 picks the single contract (activate existing hook) and removes the conflicting `**Specs:**` / DB-resolution / pending-token / pre-commit content from `-001`.
2. **F2 closure verification:** confirm §1's narrowing of the claim ("Claude Code Write/Edit-time blocking", not "must NOT be possible to submit") + the explicit acknowledgment of bypass risks is acceptable as the interim contract.
3. **F3 closure verification:** confirm §3's single test surface (workspace activation) doesn't duplicate framework tests.
4. **F4 closure verification:** confirm §4's grandfathering uses `## Specification Links` (the actual schema) and accurately identifies pre-rule vs. rule-compliant bridges.
5. **Spec linkage soundness:** confirm the new Specification Links section cites KB-resolved DCLs (no `pending:`); the cited DCLs exist as of commit `49f5b6dd`.
6. **Sequencing:** confirm this REVISED-1 should land independently of the comprehensive architecture (which is in REVISED-1 status at `-003`); the activation here doesn't conflict with the comprehensive architecture's F2-F5 closures.

A NO-GO with specific findings remains valuable.

---

## §7. Reversibility

Each slice independently revertable:
- Slice 1: remove the hook from `.claude/settings.json` → activation removed (existing framework returns to dormant state).
- Slice 2: revert via `git revert` on the test commit.

The hook itself is byte-equal to a framework template; reverting just removes the workspace activation, not the framework code.

---

## §8. Reference Artifacts

- Codex NO-GO surfacing the framework-already-exists realization: `bridge/gov-process-spec-precondition-2026-04-29-002.md`
- Spec batch creation evidence: commit `49f5b6dd` + `scripts/_temp_create_s321_specs.py`
- Existing framework rule: `.claude/rules/file-bridge-protocol.md` lines 20-49
- Existing framework hook (template): `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`
- Existing framework helper: `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py:88-145`
- Existing framework tests (covering hook behavior; 56 passing): `groundtruth-kb/tests/test_governance_hooks.py`
- Comprehensive architecture (parallel; covers F2-F5 enhancements): `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-003.md`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
