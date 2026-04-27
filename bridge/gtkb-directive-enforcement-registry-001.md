NEW

# GTKB-DIRECTIVE-ENFORCEMENT-REGISTRY — Scoping Proposal

**Status:** NEW (CRITICAL framework scoping; awaits Codex GO)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** Owner observation 2026-04-27: *"This kind of problem will reoccur when others are using GT-KB. Users will assume that directives and ADRs are applied universally, no matter what user prompt is entered or whether a user approves a proposal which inadvertently violates one of these directives or ADRs. This expectation will cause catastrophic failures unless it is addressed reliably."*
**Class:** GT-KB framework feature (universal across all adopter projects)
**Relationship:** Generalization of existing `formal-artifact-approval-gate.py` PreToolUse pattern

---

## Prior Deliberations

- `bridge/critical-remediation-root-isolation-*.md` thread (S315) — the failure that surfaced this need.
- `.claude/rules/project-root-boundary.md` (owner-authored, S315) — the exemplar directive.
- `.claude/hooks/formal-artifact-approval-gate.py` (existing) — proof-of-pattern for tool-level mechanical enforcement.
- `GTKB-GOV-011 - DONE` per work_list (formal-artifact-approval gate) — establishes that mechanical enforcement at PreToolUse is an accepted pattern.
- ADR/DCL/IPR/CVR framework per CLAUDE.md GOV-20 — establishes how architectural decisions become machine-checkable.

## §0. The structural problem

**Owner-stated:** Standing directives, rule files, and ADRs decay in weight as a session progresses. Users (Prime Builder, Loyal Opposition, owner-driven prompts, future adopters' AIs) may inadvertently approve or execute work that violates them. Catastrophic failure mode: silent drift past hard constraints, discovered only by Codex post-violation review, requiring critical remediation campaigns.

**Class of failures this prevents:**

- File creation outside `E:\GT-KB\` (just demonstrated, S315 critical remediation)
- KB writes without approval packets (already prevented by `formal-artifact-approval-gate.py`)
- Bridge protocol bypass (e.g., implementation without GO)
- Hardcoded paths to legacy locations
- Editable installs pointing outside root
- `Path.home()` reads of GT-KB-class artifacts
- ADR-violating architectural choices (e.g., introducing a write-capable path that contradicts a DCL)
- Future ADRs/directives owners author after this proposal lands

## §1. Solution concept: Directive Enforcement Registry

A machine-readable registry of every active GT-KB directive, paired with hooks that mechanically enforce each directive at the tool-call boundary. The registry is owner-authored; the hooks are framework-provided; enforcement is per-action and bypass-resistant.

### §1.1 Three-layer enforcement architecture

```
Layer 1: Tool-call enforcement (PreToolUse hook)
  → reads directive registry
  → for every Write/Edit/Bash/MultiEdit/etc., applies relevant directive's check
  → BLOCKS the tool call if violation detected
  → returns structured error citing the violated directive ID

Layer 2: Proposal-time enforcement (bridge proposal template + Codex review)
  → every bridge proposal MUST include per-directive compliance attestation
  → Codex review checklist explicitly verifies each attestation against registry
  → proposal cannot get GO without compliance attestation passing

Layer 3: Audit-time enforcement (session-start scan + CI gate)
  → at session start, re-validate current repo state against registry
  → CI gate re-validates pre-merge (similar to assertion-ratchet pattern)
  → any violation that slipped through prior layers surfaces as bridge thread NEW entry
```

The three layers are independently sufficient: even if Layer 2 (Codex) misses a violation, Layer 1 (tool hook) blocks it. Even if Layer 1 has a bypass, Layer 3 (audit) catches it.

### §1.2 Directive registry schema

Stored at `E:\GT-KB\.claude\directive-registry.json` (in-root, per the very directive it encodes):

```json
{
  "schema_version": 1,
  "directives": [
    {
      "id": "DIR-ROOT-BOUNDARY-001",
      "title": "Project Root Boundary",
      "rule_file": ".claude/rules/project-root-boundary.md",
      "established_at": "2026-04-27",
      "established_by": "owner",
      "non_negotiable": true,
      "applies_to": "all-gt-kb-work",
      "machine_check": {
        "type": "path-constraint",
        "tool_uses": ["Write", "Edit", "MultiEdit", "Bash"],
        "rules": [
          {
            "kind": "block-if-path-matches",
            "patterns": [
              "^E:\\\\Claude-Playground",
              "^C:\\\\Users\\\\[^\\\\]+\\\\\\.codex\\\\agent-red-hooks",
              "^C:\\\\Users\\\\[^\\\\]+\\\\\\.claude\\\\projects\\\\E--GT-KB"
            ],
            "violation_message": "DIR-ROOT-BOUNDARY-001 violation: path outside E:\\GT-KB. See .claude/rules/project-root-boundary.md."
          },
          {
            "kind": "require-path-prefix",
            "prefix": "E:\\GT-KB\\",
            "exempt_tools": ["Read", "Grep", "Glob"],
            "violation_message": "DIR-ROOT-BOUNDARY-001 violation: file write/edit destination must be under E:\\GT-KB. Either correct the path or surface explicit override request."
          }
        ]
      }
    },
    {
      "id": "DIR-FORMAL-ARTIFACT-APPROVAL-001",
      "title": "Formal Artifact Approval Required for KB Mutations",
      "rule_file": "(implemented via .claude/hooks/formal-artifact-approval-gate.py)",
      "established_at": "S293",
      "non_negotiable": true,
      "machine_check": {
        "type": "delegated-hook",
        "hook_path": ".claude/hooks/formal-artifact-approval-gate.py"
      }
    }
  ]
}
```

Schema characteristics:

- **`id`:** stable identifier (DIR-* namespace) for cross-references in violation messages, bridge proposals, Codex reviews.
- **`rule_file`:** human-readable rule explanation lives separately; registry encodes the machine check.
- **`non_negotiable`:** owner-authored hard constraint that AI cannot override even with apparent owner approval (because owner approval may be inadvertent).
- **`machine_check`:** the actual enforcement logic, expressed in a small DSL (path-constraint, content-match, command-block, delegated-hook).

Schema versioning + migration path included so the registry evolves cleanly.

### §1.3 Tool-call enforcement hook (Layer 1)

`.claude/hooks/directive-enforcement-gate.py`:

- Triggered by `PreToolUse` for `Write`, `Edit`, `MultiEdit`, `Bash`, `NotebookEdit`.
- Reads `.claude/directive-registry.json`.
- For each directive whose `machine_check.tool_uses` includes the current tool, applies the rules.
- On violation: returns `exit(2)` with the violation message; tool call is BLOCKED.
- On no-violation: `exit(0)`; tool call proceeds.
- Failure-mode: if registry is missing or unparseable, hook FAILS-CLOSED (blocks all writes) — better to halt than to silently allow violations.

### §1.4 Proposal template extension (Layer 2)

Bridge proposal template gains a required section:

```markdown
## Directive Compliance Attestation

For each non-negotiable directive in `.claude/directive-registry.json`, attest compliance:

| Directive ID | Compliance | Evidence |
|---|---|---|
| DIR-ROOT-BOUNDARY-001 | YES | All proposed paths verified under `E:\GT-KB\` |
| DIR-FORMAL-ARTIFACT-APPROVAL-001 | N/A | No KB mutations in this proposal |
| ... | ... | ... |
```

Codex review checklist explicitly verifies the attestation. Missing or incorrect attestation = NO-GO. The Codex review template gains a corresponding directive-check section.

### §1.5 Session-start audit (Layer 3)

`scripts/audit_directive_compliance.py` (called by SessionStart hook):

- Reads registry.
- For each directive's `machine_check`, scans current repo state.
- Outputs violation report to `bridge/audit-evidence/directive-compliance-<timestamp>.json`.
- Any violation triggers a `bridge/INDEX.md` entry as `NEW` for Prime to address.

### §1.6 CI gate (Layer 3)

A new `tests/scripts/test_directive_registry_compliance.py` joins the release-candidate gate. Pre-merge, a workflow runs the audit; any violation fails the merge.

## §2. Relationship to existing ADR/DCL framework

Per CLAUDE.md GOV-20:

- **ADR** = architecture decision record (decision + context + alternatives + consequences)
- **DCL** = design constraint (machine-checkable assertion derived from an ADR)

This proposal:

- **ADR-DIRECTIVE-ENFORCEMENT-REGISTRY-001** would be the new ADR establishing the registry-and-hook pattern as architectural commitment.
- **DCL-DIRECTIVE-REGISTRY-COMPLETENESS-001** would be the assertion that every owner-authored non-negotiable directive has a registry entry.
- Each registered directive's `machine_check` IS a DCL-equivalent — it's the machine assertion form of the rule.
- Existing ADRs/DCLs that are owner non-negotiables become eligible for registry inclusion.

The registry generalizes the ADR/DCL framework to ALL owner-authored constraints, not just architectural decisions.

## §3. Multi-phase implementation plan

| Phase | Scope | Bridge | Estimated effort |
|---|---|---|---|
| **P1** | Registry schema + initial directive-registry.json with DIR-ROOT-BOUNDARY-001 + DIR-FORMAL-ARTIFACT-APPROVAL-001 | `gtkb-directive-enforcement-p1-registry-schema-001.md` | ~2-3 hours |
| **P2** | `directive-enforcement-gate.py` PreToolUse hook + tests | `gtkb-directive-enforcement-p2-tool-hook-001.md` | ~3-4 hours |
| **P3** | Bridge proposal template + Codex review template extensions | `gtkb-directive-enforcement-p3-templates-001.md` | ~1-2 hours |
| **P4** | Session-start audit script + report shape | `gtkb-directive-enforcement-p4-session-audit-001.md` | ~2-3 hours |
| **P5** | CI gate integration + release-candidate test | `gtkb-directive-enforcement-p5-ci-gate-001.md` | ~1-2 hours |
| **P6** | ADR-DIRECTIVE-ENFORCEMENT-REGISTRY-001 + DCL-DIRECTIVE-REGISTRY-COMPLETENESS-001 + KB records | `gtkb-directive-enforcement-p6-adr-dcl-001.md` | ~1 hour |
| **P7** | Adopter consumption pattern (how a new adopter project bootstraps the registry) | `gtkb-directive-enforcement-p7-adopter-consumption-001.md` | ~2 hours |

Total estimated effort: ~12-17 hours across multiple sessions. Each phase is independently reviewable + GO'd.

## §4. Why this is GT-KB framework, not Agent Red local

The owner's framing — *"this will reoccur when others are using GT-KB"* — makes this a framework concern. Every adopter project needs:

- A registry with adopter's owner-specific directives
- The framework's `directive-enforcement-gate.py` hook (consumed via `gt project upgrade`)
- The framework's session-start audit (consumed via `gt project upgrade`)
- The framework's CI gate template (consumed via `gt project upgrade`)
- The framework's bridge proposal template extension (consumed via `gt project upgrade`)

The framework provides the mechanism; each adopter authors their own directives. Agent Red's `DIR-ROOT-BOUNDARY-001` is one example; another adopter might have different non-negotiables.

This means implementation lives in `E:\GT-KB\` (per the very directive it enforces). Per work_list row 19 (forthcoming) and Codex's F3-mandated Agent Red consolidation, the framework code's exact path within `E:\GT-KB\` will be decided in the broader application-boundary migration.

## §5. Risk + decision notes

- **Failure-closed registry hook is HIGH-IMPACT.** If the registry file is missing or malformed, ALL Write/Edit/Bash calls are blocked. Mitigation: hook treats specific errors (missing file, JSON parse failure) as "registry unavailable → fail-CLOSED with clear error message." Tests cover the failure modes.

- **Owner-authored override mechanism.** Sometimes an owner explicitly wants to temporarily override a directive (e.g., for emergency response). Proposed: an explicit `--override-directive=DIR-ID` flag that requires accompanying `--override-justification="..."` and writes the override to the audit log. Owner can use this; AI cannot self-grant overrides.

- **Adopter heterogeneity.** Different adopters have different rule files. The registry pattern is agnostic — each adopter's registry contains their own directives. Framework provides the mechanism, not the policy.

- **Performance.** Per-tool-call hook overhead. The hook reads the registry (small JSON) + applies path regex (microseconds). Negligible.

- **Existing rule files become candidates for registry promotion.** Files like `bridge-essential.md`, `codex-review-gate.md`, `acting-prime-builder.md` contain owner-stated non-negotiables. Each can be analyzed for promotion to a DIR-* registry entry. P1 includes the initial 2 entries; future bridges add more as needed.

## §6. Codex Review Asks

1. Confirm the three-layer architecture (tool hook + proposal-time + audit) provides sufficient defense-in-depth against the failure class.
2. Confirm the registry schema (§1.2) covers the path-constraint case from `DIR-ROOT-BOUNDARY-001` and is extensible to other directive classes (content-match, command-block, delegated-hook).
3. Confirm fail-CLOSED on missing/malformed registry is the right safety posture.
4. Confirm the proposal template extension (§1.4) doesn't impose excessive overhead on small bridges.
5. Confirm phasing (§3) is sound; particularly that P1+P2 (registry + tool hook) ship together as a minimum viable mechanism before P3-P7 layer on enhancements.
6. Confirm relationship to ADR/DCL framework (§2) is correctly framed — registry as a generalization of the DCL pattern to all owner-authored constraints.
7. **GO / NO-GO** as scope-of-program. Implementation is multi-bridge per §3.

## §7. Decisions Needed From Owner

After Codex GO:

1. **Confirm program prioritization.** This is the next program after critical-remediation Phases A-F land + the dirty-worktree disposition. Owner can sequence higher or lower.
2. **Confirm initial registry contents (P1).** Two directives proposed: DIR-ROOT-BOUNDARY-001 + DIR-FORMAL-ARTIFACT-APPROVAL-001. Owner can add more.
3. **Confirm override mechanism (§5).** `--override-directive` + `--override-justification` flags acceptable, OR stricter (no override mechanism at all)?

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
