NO-GO

# Loyal Opposition Review - Codex Bridge-Compliance-Gate Hook Parity REVISED-2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-07
Reviewed document: `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md`
Prior NO-GO: `bridge/gtkb-codex-bridge-compliance-gate-parity-004.md`
Verdict: NO-GO

## Claim

The revision resolves the specific `-004` ADR-linkage finding: it cites
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`, reconciles the proposed Bash adapter and
PostToolUse audit with the ADR, and tightens the audit-mode detection test.

It still cannot receive `GO` because the linked Codex parity specification and
ADR make `scripts/check_codex_hook_parity.py` the Windows load-bearing
mechanical fallback, but the proposal only requires that checker to continue
passing. It does not require the checker to fail when the new bridge-compliance
hook intent is missing or drifts.

## Applicability Preflight

Command run:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-bridge-compliance-gate-parity
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:98ed7d043c83dc61e7eef09244b6d7420b1778ddeafa45386c7f4ca28802fb16`
- bridge_document_name: `gtkb-codex-bridge-compliance-gate-parity`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md`
- operative_file: `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
```

The mechanical preflight passes. The finding below is a specification-derived
test-gap finding that the applicability matrix does not yet catch.

## Evidence Reviewed

- Live `bridge/INDEX.md` showed latest status
  `REVISED: bridge/gtkb-codex-bridge-compliance-gate-parity-005.md`.
- Full bridge history reviewed: `-001.md` through `-005.md`.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:18` cites
  `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:19` cites
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:59` maps the ADR's
  Windows mechanical enforcement clause to acceptance criterion 8, but the
  acceptance criterion is only that `python scripts/check_codex_hook_parity.py`
  continues to pass.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:227` maps
  `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` to a new static config test, not
  to the existing parity checker.
- `bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:242` requires
  `python scripts/check_codex_hook_parity.py` to continue reporting `PASS`.
- Direct MemBase read for `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` shows
  assertion `A1`: "Parity checker fails when Claude has
  bridge-compliance-gate.py active and Codex lacks a corresponding active hook
  or declared fallback." The recorded verifying test is
  `tests/scripts/test_codex_hook_parity.py::test_codex_parity_requires_bridge_compliance_gate_when_hooks_enabled`.
- Direct MemBase read for `ADR-CODEX-HOOK-PARITY-FALLBACK-001` shows the ADR
  is `verified` and says Codex-on-Windows mechanical enforcement is provided by
  `scripts/check_codex_hook_parity.py` and release-candidate-gate regression
  tests while Codex hooks are not a live Windows interception boundary.
- `scripts/release_candidate_gate.py:259` runs
  `scripts/check_codex_hook_parity.py`, and `scripts/release_candidate_gate.py:289`
  includes `tests/scripts/test_codex_hook_parity.py` in the release gate test
  lane.
- `rg -n "bridge-compliance-gate|test_codex_parity_requires_bridge_compliance_gate" scripts/check_codex_hook_parity.py tests/scripts/test_codex_hook_parity.py`
  returned no matches, confirming the current load-bearing checker and its test
  file do not yet contain bridge-compliance parity coverage.

## Findings

### F1 - P1: The proposal leaves the load-bearing Codex parity checker blind to this hook

Claim: The proposal cannot receive `GO` until it requires
`scripts/check_codex_hook_parity.py` and `tests/scripts/test_codex_hook_parity.py`
to enforce the new bridge-compliance hook intent.

Evidence: The proposal says the parity checker remains the load-bearing
Windows mechanism at
`bridge/gtkb-codex-bridge-compliance-gate-parity-005.md:59`, and its
acceptance criterion at `:242` only requires the checker to continue reporting
`PASS`. That proves the checker was not broken by the change; it does not prove
the checker learned the new required parity surface. The linked SPEC's A1
assertion requires the parity checker to fail when Claude has
`bridge-compliance-gate.py` active and Codex lacks corresponding active hook
intent or fallback. The current checker/test file contain no
`bridge-compliance-gate` coverage.

Risk/impact: This creates the same false-confidence failure mode the thread is
intended to close. The new adapter and audit tests could pass once, while the
release-candidate fallback checker remains unable to detect later removal or
drift of the Codex bridge-compliance hook intent.

Recommended action: Revise the proposal to include a parity-checker update:

- add constants and checks in `scripts/check_codex_hook_parity.py` for the
  Codex bridge-compliance shim/adapter and the PostToolUse audit intent;
- add the SPEC-named regression test, or an equivalent test with that behavior,
  in `tests/scripts/test_codex_hook_parity.py`;
- include a negative fixture proving the checker fails when the Codex
  bridge-compliance entry is absent while Claude's
  `.claude/hooks/bridge-compliance-gate.py` remains registered;
- update the acceptance criteria so `python scripts/check_codex_hook_parity.py`
  is not merely "still PASS" but demonstrably guards this new hook family.

Decision needed from owner: None.

## Resolved Prior Finding

The prior `-004` finding about missing
`ADR-CODEX-HOOK-PARITY-FALLBACK-001` linkage is resolved in principle. The
remaining blocker is the parity-checker enforcement gap described above.

## Decision

NO-GO.
