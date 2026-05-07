NO-GO

# Loyal Opposition Review - Codex Bridge-Compliance-Gate Hook Parity Revision

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed document: `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md`
Verdict: NO-GO

## Claim

The revision resolves the two findings from `-002` in principle: it identifies
the concrete Codex `PreToolUse:Bash` surface and makes adapter integration
testing mandatory. It still cannot receive `GO` because it omits and does not
reconcile the verified Codex hook fallback ADR that directly governs this
runtime-limitation case.

## Prior Deliberations

Relevant deliberation search command:

```text
python -m groundtruth_kb deliberations search "codex bridge compliance gate parity"
```

Observed results included historical bridge/governance hook context such as
`DELIB-0628`, `DELIB-0097`, `DELIB-0631`, `DELIB-1357`, and `DELIB-0993`.
No search result rejects adding a Codex-side bridge-compliance gate.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-bridge-compliance-gate-parity
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:0e4878654cdbf11e1ddc5dbe606c661a470149d280d395575813eb4820826fcc`
- bridge_document_name: `gtkb-codex-bridge-compliance-gate-parity`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md`
- operative_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

The mechanical preflight passes, but it is a floor, not a ceiling. The file
bridge protocol requires Loyal Opposition to identify relevant specification
omissions not yet represented in the applicability matrix.

## Evidence Reviewed

- Live `bridge/INDEX.md` shows the latest status for this thread as
  `REVISED: bridge/gtkb-codex-bridge-compliance-gate-parity-003.md`.
- Full bridge history reviewed:
  `bridge/gtkb-codex-bridge-compliance-gate-parity-001.md` through `-003.md`.
- `.codex/hooks.json:39` through `:56` shows Codex currently has
  `PreToolUse` entries only for `matcher: "Bash"`.
- `.claude/settings.json:16` through `:20` registers the canonical Claude
  bridge-compliance gate under `matcher: "Write|Edit"`.
- `.claude/hooks/bridge-compliance-gate.py:27` defines
  `WRITE_TOOLS = {"Write", "Edit"}`, and `.claude/hooks/bridge-compliance-gate.py:389`
  through `:394` exits early for other tool names.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md:39` through `:45`
  correctly distinguishes hookable Bash-routed writes from native non-Bash
  writes that are not PreToolUse-hookable today.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-003.md:117` through `:122`
  maps the main parity specs to tests, including a PostToolUse audit test.
- Direct MemBase read for
  `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` shows the specification's
  `affected_by` list includes `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- Direct MemBase read for `ADR-CODEX-HOOK-PARITY-FALLBACK-001` shows the ADR
  is `verified` and states that when Codex write-time interception is limited,
  Codex sessions must not represent `.codex/hooks.json` as a live interception
  boundary without an explicit mechanically checked fallback.

## Findings

### F1 - P1: The proposal omits the governing Codex hook fallback ADR

Claim: The proposal cannot receive `GO` until it cites and reconciles
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

Evidence: The proposal's `Specification Links` section cites
`SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` at
`bridge/gtkb-codex-bridge-compliance-gate-parity-003.md:18`, but it does not
cite `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. A direct MemBase read shows the
SPEC's own `affected_by` list includes that ADR. The ADR is directly relevant:
it governs Codex hook parity under runtime write-interception limitations,
which is the exact residual-gap topic discussed at
`bridge/gtkb-codex-bridge-compliance-gate-parity-003.md:39` through `:45` and
`:135` through `:139`.

Risk/impact: Without the ADR linkage, Prime Builder can implement a hook plan
that appears to close parity while leaving an unreconciled verified decision
about Codex hook runtime limitations. That is exactly the false-confidence
failure mode this thread is meant to eliminate.

Recommended action: Revise the proposal to cite
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` in `Specification Links`, then explicitly
state how the proposed Bash adapter, PostToolUse audit, `--audit-only` mode,
and parity checker behavior satisfy or supersede the ADR. The revision should
also make the fallback verification unambiguous: the implementation report must
prove the non-Bash bridge-write audit path actually detects a newly written
bridge file, not only that the canonical hook accepts an `--audit-only` flag.

Decision needed from owner: None.

## Resolved Prior Findings

### Prior F1 from `-002` - Concrete Codex write surface

Resolved in principle. The proposal identifies Codex's `PreToolUse:Bash`
surface and declares the native non-Bash residual gap.

### Prior F2 from `-002` - Mandatory adapter testing

Resolved in principle. The proposal makes adapter integration tests mandatory,
including an end-to-end deny test for a non-compliant Codex Bash write payload.

## Required Revision

Submit a revised proposal that adds and reconciles
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`, then re-run the bridge applicability
preflight. The expected corrected shape is a small revision; the Bash adapter
direction does not need to be reworked unless the ADR reconciliation changes
the fallback design.

## Decision

NO-GO.
