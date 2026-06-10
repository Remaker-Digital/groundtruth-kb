WITHDRAWN

# Supersession Notice - Directive Enforcement Registry Scoping Program

bridge_kind: lo_verdict
Document: gtkb-directive-enforcement-registry
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-directive-enforcement-registry-004.md`
Recommended commit type: `docs:`

## Disposition

Prime Builder withdraws this old scope-of-program GO as a current
implementation target.

The owner concern is not withdrawn: durable directives, ADRs, DCLs, and
bridge-governance requirements must not silently decay during a session. The
specific 2026-04-27 program shape is now stale, though. It predates the current
bridge applicability registry, mandatory proposal preflight, ADR/DCL clause
preflight, bridge-compliance gate, Codex hook parity work, AUQ policy-gate
work, and the active single-harness dispatch topology.

The approved `-003` scope also left owner choices unresolved after GO:
program prioritization and initial registry contents. It is not valid for
Prime Builder to implement those old choices by inference during an automated
bridge dispatch. Re-running this thread as written would either overclaim that
the modern governance lattice is implemented by this proposal, or it would file
a new directive-registry implementation without current owner-visible scope
confirmation.

`WITHDRAWN` closes only this obsolete queue entry. It preserves the prior
NO-GO, revision, and GO as historical evidence. Future directive-enforcement
work should be proposed from the current rule set and current backlog, with
fresh specification links and current preflight evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/prime-builder-role.md`

## Superseding Evidence

- `.claude/rules/file-bridge-protocol.md` now requires mandatory
  specification linkage and pre-filing preflight for implementation proposals.
- `.claude/rules/codex-review-gate.md` now requires bridge applicability and
  ADR/DCL clause preflights before `GO` or `VERIFIED`.
- `config/governance/spec-applicability.toml` is the current mechanical
  cross-cutting-spec applicability registry for bridge packets.
- `config/governance/adr-dcl-clauses.toml` and
  `scripts/adr_dcl_clause_preflight.py` are the current clause-level
  applicability and blocking-gap surface.
- `.claude/hooks/bridge-compliance-gate.py` and the mirrored Codex hook
  configuration are the current bridge-packet compliance enforcement surfaces.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-007.md`
  is the current live revision for hardening ADR/DCL clause-test enforcement.
- The single-harness dispatcher now supplies Prime Builder queue handling for
  GO and NO-GO entries, replacing the older poller-era assumptions under which
  this scoping thread was filed.

## Specification-Derived Verification

No source, configuration, hook, KB, or formal artifact implementation is
performed by this notice. Verification is limited to proving that the current
queue-state closure is append-only, root-contained, and explicitly scoped.

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This notice is filed as `bridge/gtkb-directive-enforcement-registry-005.md`; `bridge/INDEX.md` is updated append-only above the prior `GO`. | Prior versions remain preserved; live latest state becomes terminal. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The disposition cites current governance surfaces and states that future directive-enforcement work needs a fresh proposal. | Lifecycle state is explicit instead of leaving a stale `GO`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This notice carries concrete governing spec links and does not present itself as a new implementation proposal. | The stale proposal's old preflight gap is not hidden. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No implementation is claimed; the verification surface is limited to append-only bridge closure evidence. | No implementation test is applicable to this closure notice. |
| `.claude/rules/project-root-boundary.md` | This notice creates only an in-root bridge file and updates in-root `bridge/INDEX.md`. | Root boundary remains preserved. |

## Owner Decisions / Input

No new owner decision is required. This notice does not approve or implement a
new directive-registry design; it only closes a stale GO whose own follow-on
owner choices were never resolved in current form.

## Commands Executed

```text
Get-Content bridge/INDEX.md
Get-Content bridge/gtkb-directive-enforcement-registry-001.md
Get-Content bridge/gtkb-directive-enforcement-registry-002.md
Get-Content bridge/gtkb-directive-enforcement-registry-003.md
Get-Content bridge/gtkb-directive-enforcement-registry-004.md
rg -n "directive-enforcement|directive registry|DIR-ROOT|DIRECTIVE" memory groundtruth.db .groundtruth config bridge/INDEX.md independent-progress-assessments
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-directive-enforcement-registry
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-directive-enforcement-registry --content-file bridge/gtkb-directive-enforcement-registry-005.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-directive-enforcement-registry
```

Observed result: the live INDEX showed this document latest at `GO`; the
thread chain showed a scope-of-program GO with unresolved owner choices; the
current indexed operative file failed the modern applicability preflight
because it predates current required specification links; the ADR/DCL clause
preflight reported zero blocking gaps. The content-file applicability preflight
for this withdrawal notice passed with `missing_required_specs: []` and
`missing_advisory_specs: []`; after the INDEX update, the clause preflight used
this notice as operative and again reported `Blocking gaps (gate-failing): 0`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
