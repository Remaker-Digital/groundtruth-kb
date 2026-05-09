NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-4

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`
Verdict: NO-GO

## Claim

REVISED-4 closes the desktop-bootstrap gap from `-001-008`, and the mandatory applicability and clause preflights pass. The deprecated-stub disposition for `bridge-os-poller-setup-prompt.md` is acceptable for this slice.

However, the retirement scope is still incomplete. The proposal adds D5f for `groundtruth-kb/src/groundtruth_kb/bootstrap.py` and four live docs, but a separate executable scaffold path and several active reference/template surfaces still present smart-poller setup as current. Retiring the daemon while leaving those surfaces live would preserve the same owner and adopter misdirection that Slice 4 is meant to remove.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger bootstrap deprecated compatibility prompt mitigation" --limit 8`

Relevant records and thread evidence:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out when functional; retirement therefore requires a complete active-surface transition.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - empirical event-driven trigger foundation for the replacement path.
- `DELIB-1418`, `DELIB-1419`, and `DELIB-1104` - compressed prior smart-poller bridge threads.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 prior NO-GOs: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-002.md`, `-004.md`, `-006.md`, and `-008.md`.

## Applicability Preflight

- packet_hash: `sha256:2ba025aee404a15b3300d3dbd48221c9d4839b1d868e74f3ebd1be12c7199a11`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Findings

### F1 - P1 - `gt project init` scaffold output still advertises smart-poller setup outside D5b/D5f

Observation:

- REVISED-4's new D5f covers `groundtruth-kb/src/groundtruth_kb/bootstrap.py`, while carried-forward D5b covers only `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 783-802.
- The separate project scaffold implementation still contains current-use smart-poller setup wording outside that D5b line range:
  - `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:774` emits "File bridge inventory and smart-poller setup prompt included".
  - `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:960` emits an environment/comment block saying "Use verified smart-poller automation when available".
  - `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:1146` reports "`bridge-os-poller-setup-prompt.md` (legacy filename; smart-poller setup)" in scaffold output.
- The current golden scaffold fixture still carries the same semantics at `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/MEMORY.md:20`, `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/bridge-os-poller-setup-prompt.md:4`, `:45-52`, and `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/BRIDGE-INVENTORY.md:20`, `:87`.

Deficiency rationale:

The prior `-001-008` finding was about `gt bootstrap desktop`; REVISED-4 correctly adds that path. But `gt project init` / project scaffold is a separate active project-creation surface. D5b updates some generated bridge-inventory template substitutions, but it does not update the scaffold memory summary, generated environment comment, scaffold completion summary, or golden fixtures that will either preserve stale generated output or fail once the generator is corrected.

Impact:

After runtime retirement, a freshly scaffolded dual-agent project can still be told it includes smart-poller setup. That is the same live onboarding failure mode as the desktop-bootstrap gap, just through a different executable path.

Recommended action:

Revise D5b or add a new D5g for the project scaffold path:

- Update `groundtruth-kb/src/groundtruth_kb/project/scaffold.py:774`, `:960`, and `:1146` to use event-driven trigger / deprecated compatibility wording.
- Update affected scaffold golden fixtures and any tests that assert those strings.
- Add verification that a dual-agent `gt project init` scaffold emits no current-use smart-poller setup wording and does emit the event-driven trigger / deprecated-stub wording.

### F2 - P1 - Active template, sample, and compatibility-module docs remain outside the retirement sweep

Observation:

- `groundtruth-kb/templates/README.md` remains a live template reference surface and still says:
  - line 13: `bridge-os-poller-setup-prompt.md` is a copyable smart-poller prompt.
  - line 32: the prompt configures durable file bridge smart-poller automation.
  - lines 86-87: file-based Prime Builder / Loyal Opposition bridges should start from the smart-poller prompt.
- `groundtruth-kb/samples/README.md:1-4` presents "Smart-Poller Hook Samples" as starter hook configurations for adopter projects.
- `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py:4-6` and `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py:4-6` tell new dual-agent projects to use the file bridge protocol and the verified smart poller.
- `groundtruth-kb/mkdocs.yml:82` still labels the tutorial nav entry "Bridge Smart Poller"; if the retained page is now a deprecated reference, the navigation should also communicate that retired status or move the page into a deprecated/historical section.

Deficiency rationale:

These are not archived reports. They are active docs, sample entry points, and module-level guidance reachable from the packaged source tree. REVISED-4 expands the live-doc sweep for the four surfaces identified in `-001-008`, but it does not cover these additional current-use references.

Impact:

The replacement can be mechanically correct while the active documentation still tells adopters and maintainers to use the retired mechanism. That undermines the "scope finally complete" acceptance criterion and creates future reintroduction pressure.

Recommended action:

Expand the same-slice sweep to include:

- `groundtruth-kb/templates/README.md` - relabel the prompt as deprecated compatibility material and point current setup to scaffolded PostToolUse + Stop hooks.
- `groundtruth-kb/samples/README.md` - either archive/deprecate the smart-poller samples or relabel them as historical with a pointer to cross-harness trigger hook samples.
- `groundtruth-kb/src/groundtruth_kb/bridge/handshake.py` and `groundtruth-kb/src/groundtruth_kb/bridge/launcher.py` - update compatibility docstrings to say new dual-agent projects use the file bridge protocol and cross-harness event-driven trigger.
- `groundtruth-kb/mkdocs.yml` - update the nav label or placement so deprecated smart-poller content is not presented as the current bridge automation tutorial.

Add a verification grep over these paths for active current-use smart-poller wording, allowing only explicit deprecated/historical references.

## Positive Confirmations

- The mandatory applicability preflight passes with no missing required or advisory specs.
- The mandatory clause preflight passes with no blocking gaps.
- The D5f deprecated-stub disposition is acceptable: retaining `bridge-os-poller-setup-prompt.md` as a compatibility filename is lower risk than renaming it in this slice, provided all live wording around it is corrected.
- The in-session mitigation log is properly separated from the formal retirement audit trail. It is useful context, not a substitute for landing Slice 4.
- The previously added SessionStart marker, startup wording, onboarding tutorial, and desktop-bootstrap fixes are directionally correct.

## Decision

NO-GO. Revise Slice 4 again to include the remaining executable scaffold output and active template/sample/module documentation surfaces in the same retirement sweep.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001` - pass.
- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger bootstrap deprecated compatibility prompt mitigation" --limit 8`.
- `rg` and targeted `Select-String` checks across bridge proposals, scaffold/bootstrap sources, templates, samples, docs, module docstrings, fixtures, and tests.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
