GO

# Loyal Opposition Review - GTKB-GOV-TERM-DISAMBIGUATION-MECHANICAL REVISED-2

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md`
Verdict: GO

## Claim

The REVISED-2 proposal is approved for implementation. It resolves the prior
blocking enforcement-event defect by moving deny-capable checks to PreToolUse
and limiting PostToolUse to audit-only behavior.

## Evidence

- The prior NO-GO at `-004.md` rejected assigning hard-blocking behavior to a
  PostToolUse lint hook because PostToolUse observes completed writes.
- The revised proposal now defines a shared pure library
  `groundtruth-kb/src/groundtruth_kb/term_disambiguation.py`, a PreToolUse
  `term-disambiguation-precheck.py` for all `error` severity deny paths, a
  PostToolUse `term-disambiguation-audit.py` for warn-only audit records, and an
  extension to `bridge-compliance-gate.py` that calls the same shared library.
- Live source inspection confirms `bridge-compliance-gate.py` is currently a
  PreToolUse Write/Edit hook and reads `tool_input.content` before writes; this
  is the correct deny-capable pattern for the proposed term-disambiguation
  errors.
- Live registry inspection confirms the managed-artifacts model already
  distinguishes PreToolUse blocking gates from PostToolUse observability hooks.
  The revised proposal follows that split.
- The revised tests T2, T4, T8, T9, T12, and T17 now separately assert
  PreToolUse deny behavior, PostToolUse audit behavior, bridge-specific Tier B
  escalation, universal forbidden-use blocking, non-retroactive enforcement, and
  independence from the unresolved primer state.
- The proposal preserves the prior corrections: sibling
  `canonical-terminology-policy.toml` instead of mutating the existing
  profile-aware `canonical-terminology.toml`, prior canonical-terminology
  deliberations, pinned defaults, and a self-contained 22-term policy set.

## Risk / Impact

The largest implementation risk is duplicate evaluation if both the new
PreToolUse hook and the extended bridge-compliance gate run on the same bridge
write. The proposal explicitly calls out shared-library reuse and includes T8
to prove the shared library is called once, not through parallel logic paths.
That is the right mitigation for scoping approval.

## Recommended Action

Proceed with the proposed slices. During implementation, keep the error/warn
boundary strict:

- all `severity="error"` conditions must be evaluated before content lands;
- PostToolUse may only audit warnings or already-landed observability data;
- `bridge-compliance-gate.py` should remain a thin caller of the shared library,
  not a second policy implementation.

## Decision Needed From Owner

None.

## Verification

Commands and checks performed:

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-001.md
Get-Content -Raw bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-002.md
Get-Content -Raw bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-003.md
Get-Content -Raw bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-004.md
Get-Content -Raw bridge/gtkb-gov-term-disambiguation-mechanical-2026-05-02-005.md
Get-Content -Raw groundtruth-kb/templates/hooks/bridge-compliance-gate.py
Select-String -Path groundtruth-kb/templates/managed-artifacts.toml -Pattern 'bridge-compliance-gate|PostToolUse|PreToolUse|rule.canonical-terminology' -Context 0,5
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-012.md
```

No pytest or ruff run was needed because this is a pre-implementation scoping
review with no product-code diff.

