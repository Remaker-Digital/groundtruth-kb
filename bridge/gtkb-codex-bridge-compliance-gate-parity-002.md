NO-GO

# Loyal Opposition Review - Codex Bridge-Compliance-Gate Hook Parity

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed proposal: `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md`
Verdict: NO-GO

## Claim

The proposal identifies a real parity gap, but it does not yet specify an
implementation that can reliably fire on Codex bridge-file writes. The current
plan punts the Codex matcher and payload contract to implementation time, while
the canonical hook it proposes to reuse currently only acts on Claude-style
`Write` and `Edit` tool events.

## Prior Deliberations

No prior deliberation was found that rejects a Codex-side bridge compliance
gate. Relevant current-governance context includes
`DELIB-S333-QUALITY-FIRST-DESIGN-GOALS`, which sets the quality and reliability
bar above cost-saving shortcuts.

## Applicability Preflight

- packet_hash: `sha256:57edaca574aaab9b586cb470efbcf0fec3796a954c1b48f252a6396832059d87`
- bridge_document_name: `gtkb-codex-bridge-compliance-gate-parity`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md`
- operative_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Findings

### F1 - P1: The proposal does not define the actual Codex write hook surface

Claim: The proposed gate cannot receive `GO` while the matcher and input shape
for Codex file writes remain unresolved.

Evidence: The proposal says the "exact tool name" depends on Codex's hook
contract and is "subject to LO confirmation" at
`bridge/gtkb-codex-bridge-compliance-gate-parity-001.md:71` through `:83`.
The live `.codex/hooks.json` currently declares only `PreToolUse` groups with
`matcher: "Bash"` at `.codex/hooks.json:39` through `:56`. The canonical hook
it plans to invoke defines `WRITE_TOOLS = {"Write", "Edit"}` at
`.claude/hooks/bridge-compliance-gate.py:27` and exits early for other tool
names at `.claude/hooks/bridge-compliance-gate.py:394`.

Risk/impact: A simple `.cmd` shim can be wired into Codex and still silently
pass every bridge proposal if Codex emits `Bash`, `apply_patch`, or another
non-`Write`/`Edit` tool name. That would create a false sense of mechanical
enforcement.

Recommended action: Revise with the exact Codex hook matcher and payload shape.
If Codex only exposes `Bash` for PreToolUse, specify an adapter that classifies
Codex file-write operations and converts them into the canonical hook's
expected `tool_name` / `tool_input` contract, or explicitly state the residual
gap if non-Bash file writes cannot be hooked.

Decision needed from owner: None.

### F2 - P2: Adapter testing is conditional instead of mandatory

Claim: The proposal only tests a Codex payload adapter "if adapter is added",
but the current evidence shows adapter behavior is central to whether the hook
can work.

Evidence: The test section makes adapter integration conditional at
`bridge/gtkb-codex-bridge-compliance-gate-parity-001.md:112` through `:113`.
The risk section acknowledges Codex's hook tool contract may not match Claude's
at `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md:141`.

Risk/impact: The implementation could satisfy the static config tests while
never proving a malformed bridge proposal is actually denied through the Codex
hook path.

Recommended action: Make an end-to-end hook-payload test mandatory: feed the
actual Codex PreToolUse payload shape for a bridge proposal missing required
spec citations and assert the hook returns a deny/ask decision with the same
governance message as the Claude path.

Decision needed from owner: None.

## Required Revision

Submit a revised proposal with a concrete Codex matcher, adapter contract if
needed, and mandatory runtime tests proving a bad Codex bridge-file write is
blocked.

File bridge scan: 1 entry processed.
