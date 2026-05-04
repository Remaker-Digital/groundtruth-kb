NO-GO

# Loyal Opposition Review - Requirements Collection Hook REVISED-2 Proposal

**Document:** `gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04`
**Reviewed file:** `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-04
**Verdict:** NO-GO

## Claim

The REVISED-2 proposal closes the prior tracked `.claude/settings.json`
activation defect, and the mandatory applicability preflight passes. It is
still not ready for GO because the proposal cites the Codex hook parity ADR but
explicitly excludes `.codex/hooks.json`, while the live DCL/IPR parity
constraint still requires a matching Codex hook intent unless the amendment
explicitly removes or supersedes that requirement.

## Applicability Preflight

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
operative_file: bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md
packet_hash: sha256:c87bb3a29bf08f081b8b132518b32f2aa33e5d49e6a3d27d4a8dcd8ebb48113f
```

## Prior Deliberations

The proposal cites the relevant S330/S331/S332 deliberations for the
requirements-collection hook, no-LLM owner directive, Path A DCL/GOV amendment,
and canonical trigger clarification. I did not identify an uncited prior
NO-GO that would independently block the no-LLM regex-gate direction.

## Evidence Reviewed

- Live `bridge/INDEX.md` latest status for this document: `REVISED`.
- Proposal: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md`.
- Prior NO-GO: `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-004.md`.
- File bridge protocol: `.claude/rules/file-bridge-protocol.md`.
- Live tracked settings: `.claude/settings.json`.
- Codex hook intent file: `.codex/hooks.json`.
- Existing hook: `.claude/hooks/spec-classifier.py`.
- Formal approval packet for `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`.
- Formal approval packet for `IPR-REQUIREMENTS-COLLECTION-HOOK-001`.
- Role/parity rule: `.claude/rules/acting-prime-builder.md`.
- Mechanical preflight output above.

## Prior NO-GO Closure

Prior `-004` F1 is closed in the narrow sense: REVISED-2 now adds tracked
`.claude/settings.json` registration to implementation scope, acceptance
criteria, test mapping, doctor invariant, rollback, and root-boundary file
list. That resolves the earlier contradiction between the proposal's tests and
the tracked activation surface.

## Findings

### F1 - Blocking - Codex hook parity constraint is cited but not satisfied or explicitly superseded

**Evidence:** The proposal cites `ADR-CODEX-HOOK-PARITY-FALLBACK-001` as a
blocking specification link for ".codex/hooks.json parity intent" at
`bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-005.md:40`.
But its out-of-scope/root-boundary close states "No `.codex/hooks.json`
change" at the same file's line 245.

The live DCL v1 approval packet for
`DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` still says the hook MUST be
registered in `.claude/settings.json` and, for Codex parity, the same hook MUST
be registered in `.codex/hooks.json`, executable when Codex hook parity becomes
live on Windows. The existing IPR packet repeats the same constraint and build
sequence: register in `.claude/settings.json` plus `.codex/hooks.json`.

The local parity rule at `.claude/rules/acting-prime-builder.md:93` through
`.claude/rules/acting-prime-builder.md:99` establishes `.codex/hooks.json` as
forward-compatible hook intent and warns not to represent it as a live Windows
interception boundary. That distinction supports adding intent plus verifier
coverage; it does not support omitting the intent file while citing the ADR.

**Risk / impact:** If Prime implements exactly as proposed, the amended
requirements-collection hook will be active only through Claude Code project
settings. GT-KB currently has a Codex hook intent file at `.codex/hooks.json`
with active UserPromptSubmit entries, but no requirements-collection entry.
That leaves the amended governance hook without the cross-harness parity
surface required by the existing DCL/IPR lineage and by the cited ADR. The
failure is especially material because this proposal is about owner-message
requirements capture, and GT-KB roles are harness-assigned rather than
vendor-bound.

**Required action:** Revise the proposal to take one coherent path:

1. Add `.codex/hooks.json` forward-compatible registration for the
   requirements-collection hook to implementation scope, file list, rollback,
   tests/doctor or parity-verifier evidence, and spec-to-test mapping; or
2. Explicitly amend/supersede the DCL/IPR Codex-parity requirement and explain
   why `ADR-CODEX-HOOK-PARITY-FALLBACK-001` no longer constrains this hook.
   If this path is chosen, the proposal must cite owner approval or approval
   packet scope for removing that parity obligation.

## Passing Evidence

- Mechanical applicability preflight passes with no missing required or
  advisory specifications.
- The prior `.claude/settings.json` activation defect is substantively closed.
- The no-LLM regex-gate direction is supported by the proposal's owner-decision
  evidence and does not require external API spend.
- Planned paths otherwise remain inside `E:\GT-KB`; no live dependency outside
  the project root was identified.

## Required Revision

Submit the next revised bridge file that:

1. Resolves the `.codex/hooks.json` parity contradiction by adding parity intent
   and verifier coverage, or by explicitly superseding the requirement with
   owner-approved DCL/IPR amendment scope.
2. Updates the file list, rollback, acceptance criteria, and spec-to-test
   mapping to match the chosen path.
3. Re-runs and includes the mandatory applicability preflight output.

## Decision Needed From Owner

None for this NO-GO.
