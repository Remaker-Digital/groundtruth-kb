NO-GO

# Loyal Opposition Review - GTKB Harness Parity Baseline

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-06
Reviewed proposal: `bridge/gtkb-harness-parity-baseline-001.md`
Skill used: `harness-parity-review`
Verdict: NO-GO

## Claim

The harness parity control itself is currently healthy, but this bridge packet
cannot receive `GO`. The proposal fails the mandatory applicability preflight
because it omits required cross-cutting bridge-governance specifications, and
its current-baseline narrative is stale against the live checker output.

## Applicability Preflight

- packet_hash: `sha256:b6978c536b10219801ff84a3c5fba94ca3d999ba4991a13aa6c89ab998680b62`
- bridge_document_name: `gtkb-harness-parity-baseline`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-parity-baseline-001.md`
- operative_file: `bridge/gtkb-harness-parity-baseline-001.md`
- preflight_passed: `false`
- missing_required_specs:
  - `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
  - `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
  - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
  - `GOV-FILE-BRIDGE-AUTHORITY-001`
- missing_advisory_specs: []

## Findings

### F1 - Mandatory bridge-governance specs are missing

Severity: P1

Evidence:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-parity-baseline`
  returned `preflight_passed: false`.
- Missing required specs were
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
  `GOV-FILE-BRIDGE-AUTHORITY-001`.
- `.claude/rules/file-bridge-protocol.md` requires Loyal Opposition to issue
  `NO-GO` when a bridge proposal's preflight on its operative file does not
  pass.

Risk / impact: The proposal is a bridge-governed implementation proposal, so it
must cite the cross-cutting bridge authority, mandatory spec-linkage, verified
testing, and root-boundary/isolation authorities before review can approve it.

Required action: Refile a revised proposal with the missing required specs in
`Specification Links`, then rerun the preflight and include the resulting packet
hash and missing-spec lists.

### F2 - Current-baseline narrative is stale

Severity: P2

Evidence:

- `bridge/gtkb-harness-parity-baseline-001.md` says all registered Codex
  project-skill capabilities are `DEGRADED` because Codex can read
  `.claude/skills/*/SKILL.md` but does not receive them as native Codex skills.
- Live `python scripts/check_harness_parity.py --all --markdown` returned
  `Overall status: PASS`, `Counts: PASS: 50`, and "No parity issues found."
- Live `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json`
  returned `overall_status: PASS`, `counts: {"PASS": 17}`, and no errors or
  extras.
- `.codex/skills/*/SKILL.md` adapters exist for the registered project skills,
  and the live checker reports matching generated adapters as `PASS`.

Risk / impact: Approving the packet as written would approve a plan whose
phasing no longer matches the current repository state. Phase 3 native Codex
skill parity appears already implemented at least for generated adapters, so
the revised packet needs to distinguish completed baseline work from future
event-trigger/release-gate work.

Required action: Update the Current Baseline and Proposed Implementation
sections to reflect the live adapter-backed `PASS` state, and clearly separate
already-created artifacts from future work that still needs `GO`.

## Harness Parity Review Summary

- Overall status: PASS.
- Checked role/harness: Codex as `loyal-opposition`.
- Missing role-critical capabilities: none in live checker output.
- Degraded fallbacks: none in live checker output.
- Stale adapters: none in live checker output.
- Undeclared extras: none in live checker output.
- Verification:
  - `python scripts/check_harness_parity.py --all --markdown` -> PASS, `PASS: 50`.
  - `python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json` -> PASS, `PASS: 17`.
  - `python -m pytest tests/scripts/test_check_harness_parity.py -q --tb=short` -> PASS, `6 passed`.
  - `python -m ruff check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py` -> PASS.
  - `python -m ruff format --check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py` -> PASS, `2 files already formatted`.
  - `python -m groundtruth_kb secrets scan --paths bridge/gtkb-harness-parity-baseline-001.md config/agent-control/harness-capability-registry.toml scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py --json --fail-on=` -> PASS, `finding_count: 0`.

## Owner Decision Needed

None. This should return to Prime Builder for a revised bridge packet.

File bridge scan: 1 entry processed.
