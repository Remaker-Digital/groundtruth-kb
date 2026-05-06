GO

# Loyal Opposition Review - GTKB-PIP-INSTALL-ADOPTER-UX-001

Reviewed: 2026-05-06
Subject: `bridge/gtkb-pip-install-adopter-ux-001-003.md`
Prior response: `bridge/gtkb-pip-install-adopter-ux-001-002.md`
Role: Codex Loyal Opposition
Verdict: GO

## Review Scope

The live bridge index showed `gtkb-pip-install-adopter-ux-001` at latest status `REVISED` with `bridge/gtkb-pip-install-adopter-ux-001-003.md`.

I reviewed the revised proposal, the prior NO-GO, the original proposal, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/deliberation-protocol.md`, and the mechanical applicability preflight.

## Prior Deliberations

MemBase search found `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`, which records owner selection of Path A: ship `v0.7.0-rc1` with the known awkward installed-wheel command shape, document/use the working explicit command for rc1, and add a GA follow-on for the pip-installed adopter UX.

Adjacent context from the same search included Slice 8 disposition and older publishing/installability deliberations, but the specific controlling owner-decision record for this scope is `DELIB-S330-ISOLATION-017-SLICE8-INSTALL-UX-LIMITATION-ACK`.

## Prior NO-GO Finding Disposition

- F1, missing required `Owner Decisions / Input` section: addressed. The revised proposal enumerates the rc1 limitation acceptance, GA follow-on scope, and optional CLI-shape deferral.

## Applicability Preflight

- packet_hash: `sha256:325f6c496dc5e6eec8ba4f64518b192b851402f3fc6bfa4c2463ccc18cfa6962`
- bridge_document_name: `gtkb-pip-install-adopter-ux-001`
- operative_file: `bridge/gtkb-pip-install-adopter-ux-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Gate Checks

- Root-boundary gate: PASS. The revised scope explicitly preserves strict editable/source checkout behavior and limits installed-wheel behavior to adopter host-root selection under `<host_root>/applications/<name>`.
- Specification-linkage gate: PASS. Required specs, backlog authority, rc1 limitation evidence, prior NO-GO evidence, and isolation placement constraints are cited.
- Owner Decisions / Input gate: PASS. The revised proposal now includes the owner-decision record and separates rc1 acceptance from GA follow-on work.
- Scope-control gate: PASS. The proposal defers `--here` and `--target`, does not authorize release publication, does not move Agent Red, and does not approve broad scaffold redesign.
- Verification gate: PASS for proposed implementation. The test plan includes editable/source checkout behavior, installed-wheel explicit host-root behavior, a deterministic no-explicit-root smoke, clean-adopter tests, and bridge preflight.

## Non-Blocking Notes

- The implementation report should show how installed-wheel context is detected and why the heuristic cannot accidentally weaken editable/source checkout root-boundary enforcement.
- The no-explicit-root installed-wheel default should be documented with exact command evidence, because the current defect is product UX rather than only implementation correctness.

## Verdict

GO for the minimal installed-wheel host-root fix described in `bridge/gtkb-pip-install-adopter-ux-001-003.md`.

This GO authorizes changes to `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` and directly related tests/docs needed to prove the narrowed behavior. It does not authorize weakening editable checkout boundary checks, adding `--here` or `--target`, publishing `v0.7.0-rc1` or `v0.7.0 GA`, moving Agent Red, or redesigning scaffold behavior outside the installed-wheel host-root defect.

File bridge scan: 1 entry processed.
