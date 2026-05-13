WITHDRAWN

# Supersession Notice - ADR Isolation Application Placement

bridge_kind: prime_supersession_notice
Document: gtkb-adr-isolation-application-placement
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Responds-To: `bridge/gtkb-adr-isolation-application-placement-004.md`
Dispatch: `2026-05-12T21-58-57Z-prime-builder-72f0a8` / single-harness mode `pb`

## Disposition

Prime Builder withdraws this GO'd governance transport thread as a current
implementation target. This notice does not withdraw
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`; the ADR decision remains active.

The `-003` revision and `-004` GO were written during the pre-current
mixed-repo topology and required live upstream evidence at
`E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`. The current mandatory
project-root boundary makes that location archive-only and forbids treating it
as a live GT-KB dependency. Re-executing this thread as written would therefore
reintroduce the outside-root dependency the current rules prohibit.

The durable outcome is already represented by in-root evidence and downstream
verified work:

- `.groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json`
  is tracked and records the owner-approved ADR packet.
- `groundtruth.db` contains `ADR-ISOLATION-APPLICATION-PLACEMENT-001` as
  `type='architecture_decision'`, `status='specified'`.
- The Phase 9 plan carries the supersession notice for the older sibling-root
  paragraph and cites the ADR ID plus historical upstream commit reference.
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md` consumed
  this ADR outcome, and the downstream Wave 1 implementation reached VERIFIED
  at `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md`.
- Current governance registries cite the ADR as the active root-boundary
  constraint: `config/governance/spec-applicability.toml` and
  `config/governance/adr-dcl-clauses.toml`.

Leaving this thread at latest `GO` causes the single-harness dispatcher to keep
selecting an obsolete transport entry. `WITHDRAWN` is the narrow audit-trail
closure: it makes the live INDEX state terminal while preserving all prior
versions.

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

## Prior Deliberations

- `DELIB-0919` - Codex GO for the revised governance proposal.
- `DELIB-0920` - Codex NO-GO for the original cross-repo single-commit plan.
- `DELIB-0954` - Codex GO for the downstream
  `gtkb-isolation-016-phase8-rehearsal-implementation-013.md` proposal that
  consumed this ADR outcome.
- `DELIB-1109` - harvested bridge-thread summary recording this thread as
  latest `GO` before this withdrawal.

## Specification-Derived Verification

No new ADR implementation is performed by this notice. Verification is limited
to proving that the current in-root system already carries the ADR outcome and
that this bridge closure is append-only.

| Specification / rule | Verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Append-only file `bridge/gtkb-adr-isolation-application-placement-005.md`; `bridge/INDEX.md` updated by inserting `WITHDRAWN` above the prior `GO`. | Prior bridge versions remain preserved; live latest state becomes terminal. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -c` SQLite query against `groundtruth.db` for the ADR row; `Select-String` on the Phase 9 plan supersession notice; `git ls-files --stage` for the formal approval packet and downstream `-013` bridge file. | ADR mirror row exists with `type='architecture_decision'`, `status='specified'`; Phase 9 supersession notice is present; tracked packet and downstream bridge file exist. |
| `.claude/rules/project-root-boundary.md` | This notice performs no live read or write outside `E:\GT-KB`; historical outside-root paths are cited only as evidence of why the old GO is obsolete. | Current root-boundary contract is preserved. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_rehearse_common_validation.py platform_tests/scripts/test_rehearse_isolation.py -q --tb=short`. | 82 passed in 0.64s; the ADR-backed rehearsal/root-boundary test surface remains green. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and artifact-lifecycle specs | This notice carries explicit specification links and records the superseded lifecycle disposition instead of leaving an obsolete `GO`. | The bridge audit trail now states the lifecycle transition and governing specs. |

## Command Evidence

### Applicability and Clause Preflights

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-adr-isolation-application-placement --content-file bridge/gtkb-adr-isolation-application-placement-005.md
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-isolation-application-placement
```

Observed result:

```text
Blocking gaps (gate-failing): 0
Evidence gaps in must_apply clauses: 0
```

Note: the applicability preflight is run with `--content-file` because this
notice is a terminal Prime-side withdrawal, not a NEW/REVISED operative
proposal. The indexed operative proposal remains the historical `-003`; this
notice is the current queue-state closure.

### Runtime Evidence

```text
git ls-files --stage -- .groundtruth/formal-artifact-approvals/2026-04-26-adr-isolation-application-placement.json bridge/gtkb-isolation-016-phase8-rehearsal-implementation-013.md independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml
```

Observed result: tracked entries were returned for all three paths.

```text
python -c "import sqlite3; con=sqlite3.connect('groundtruth.db'); print(con.execute(\"select id, type, status, changed_at from specifications where id='ADR-ISOLATION-APPLICATION-PLACEMENT-001' order by version desc limit 1\").fetchone())"
```

Observed result:

```text
('ADR-ISOLATION-APPLICATION-PLACEMENT-001', 'architecture_decision', 'specified', '2026-04-26T06:56:44+00:00')
```

```text
python -m pytest platform_tests/scripts/test_rehearse_common_validation.py platform_tests/scripts/test_rehearse_isolation.py -q --tb=short
```

Observed result: `82 passed in 0.64s`.

Owner action required: none.

## Recommended Commit Type

`docs:` - bridge audit-trail closure only; no source implementation.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
