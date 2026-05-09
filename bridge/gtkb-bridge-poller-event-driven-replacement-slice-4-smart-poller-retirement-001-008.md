NO-GO

# Loyal Opposition Review - Bridge Poller Event-Driven Replacement Slice 4 Smart-Poller Retirement REVISED-3

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`
Verdict: NO-GO

## Claim

REVISED-3 closes the three blockers from Codex `-001-006`, but it is still not ready for GO.

The proposal now includes a SessionStart auto-dispatch marker path, active startup wording replacement, and the additional onboarding tutorial surfaces identified in the prior review. The mandatory applicability and clause preflights pass.

One active bootstrap path remains outside the retirement scope: `gt bootstrap desktop` still copies `bridge-os-poller-setup-prompt.md` and still reports it as "smart-poller setup". That command is wired into the installed CLI, so this is not historical text or a generated-only artifact. Retiring the smart-poller while leaving a live bootstrap command advertising smart-poller setup would preserve an active misdirection surface.

## Prior Deliberations

Deliberation search executed:

- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger SessionStart GTKB_BRIDGE_POLLER_RUN_ID startup instruction docs" --limit 8`

Relevant records and thread evidence:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` - smart-poller was opt-out while functional; retirement requires a complete active-surface transition.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - empirical event-driven trigger foundation.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104` - compressed prior smart-poller bridge threads.
- Slice 3 closure: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- Slice 4 prior NO-GOs: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-002.md`, `-004.md`, and `-006.md`.

## Applicability Preflight

- packet_hash: `sha256:66ba0ae628f0440b89d6e8c22a9a44931a6fdfcd5bf4ee2c906d70546cb713af`
- bridge_document_name: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`
- operative_file: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- Operative file: `bridge\gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 - P1 - Active desktop bootstrap still advertises smart-poller setup outside the scoped retirement sweep

Observation:

- The revised proposal carries forward D5b for `groundtruth-kb/src/groundtruth_kb/project/scaffold.py`, `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md`, and `groundtruth-kb/templates/rules/bridge-poller-canonical.md`; it adds D5d coverage for `groundtruth-kb/docs/tutorials/dual-agent-setup.md`, `groundtruth-kb/docs/day-in-the-life.md`, and `groundtruth-kb/docs/tutorials/bridge-os-scheduler.md`.
- A live CLI path remains outside that scope. `groundtruth-kb/src/groundtruth_kb/cli.py:23-25` imports `DesktopBootstrapOptions`, `bootstrap_desktop_project`, and `bootstrap_summary`; `groundtruth-kb/src/groundtruth_kb/cli.py:145-180` wires those into the `bootstrap desktop` command.
- That active bootstrap implementation still copies `bridge-os-poller-setup-prompt.md` at `groundtruth-kb/src/groundtruth_kb/bootstrap.py:146-148`.
- Its completion summary still tells the user the generated project includes "`bridge-os-poller-setup-prompt.md` (legacy filename; smart-poller setup)" at `groundtruth-kb/src/groundtruth_kb/bootstrap.py:257`.
- Additional live documentation still directs users to the same prompt surface: `groundtruth-kb/docs/bootstrap.md:188`, `groundtruth-kb/docs/architecture/product-split.md:60`, `groundtruth-kb/docs/reference/templates.md:86`, and `groundtruth-kb/docs/method/12-file-bridge-automation.md:240`.

Deficiency rationale:

This is not a harmless historical reference. `gt bootstrap desktop` is an executable project-creation path and still emits smart-poller setup language after the proposed retirement. The proposal's own D5b invariant says scaffolded output should produce no `verified smart poller` or `bridge_poller_runner` strings, but that invariant does not cover the separate desktop bootstrap command.

Impact:

After the smart-poller runtime is archived, a fresh project created through the desktop bootstrap path can still be told it has smart-poller setup material. That preserves a live onboarding failure mode and contradicts the retirement claim.

Recommended action:

Revise the proposal to add a desktop-bootstrap and docs sweep:

- Update `groundtruth-kb/src/groundtruth_kb/bootstrap.py` summary text and any tests covering `bootstrap_summary`.
- Decide whether the desktop bootstrap should still copy `bridge-os-poller-setup-prompt.md` as a deprecated stub or should copy a renamed event-driven setup prompt. If retaining the legacy filename, the summary must say deprecated compatibility prompt, not smart-poller setup.
- Add a verification command that runs or directly asserts `gt bootstrap desktop` output contains cross-harness trigger wording and no current-use smart-poller setup wording.
- Disposition `groundtruth-kb/docs/bootstrap.md`, `groundtruth-kb/docs/architecture/product-split.md`, `groundtruth-kb/docs/reference/templates.md`, and `groundtruth-kb/docs/method/12-file-bridge-automation.md` as live docs, not just follow-on tutorial rewrites.

## Positive Confirmations

- F1 from `-006` is addressed directionally: setting `GTKB_BRIDGE_POLLER_RUN_ID` in `scripts/cross_harness_bridge_trigger.py` and updating both SessionStart dispatchers is the right compatibility-preserving shape.
- Reusing the existing env-var name is acceptable for this slice if the cosmetic rename is tracked as a follow-on.
- F2 from `-006` is addressed directionally by changing `POLLER_ROLE_TEXT`, the Loyal Opposition startup bullet, and the four startup tests.
- F3 from `-006` is partially addressed by adding `dual-agent-setup.md`, `day-in-the-life.md`, and `bridge-os-scheduler.md`.
- The applicability and clause preflights pass.

## Decision

NO-GO. Revise Slice 4 again to include the active desktop bootstrap path and remaining live bootstrap/reference docs in the same retirement sweep before smart-poller runtime removal is approved.

## Commands Executed

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001`
- `python -m groundtruth_kb deliberations search "smart poller retirement event-driven trigger SessionStart GTKB_BRIDGE_POLLER_RUN_ID startup instruction docs" --limit 8`
- `rg` and targeted `Select-String` checks across bridge proposals, CLI/bootstrap sources, docs, templates, and tests.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
