REVISED

# Bridge VERIFIED Backlog Retirement - Corrective Revision

bridge_kind: prime_proposal
Document: gtkb-bridge-verified-backlog-retirement
Version: 007 (REVISED after verification NO-GO)
Author: Prime Builder (Codex, harness A, single-harness corrective mode)
Date: 2026-05-13 UTC
Responds to: bridge/gtkb-bridge-verified-backlog-retirement-006.md
Implements: DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM
target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", ".codex/hooks.json", ".claude/settings.json", "groundtruth.db", ".gtkb-state/bridge-verified-backlog-reconciler/**"]
Recommended commit type: fix:

## Claim

Revise the approved implementation so bridge VERIFIED backlog retirement is
strictly tied to explicit parent-implementation evidence, not broad contextual
`related_bridge_threads` references. Then repair any live MemBase work-item
closures created by the overbroad first implementation through append-only
corrective versions.

## NO-GO Response

### Response to F1 - Closure predicate treats contextual bridge links as parent implementation links

Accepted. The revised reconciler will require each recognized latest-VERIFIED
bridge thread to carry explicit work-item evidence for the row being retired.
For this corrective slice, the mechanical evidence rule is: at least one file
in the bridge thread chain must contain the exact work item ID or equivalent
explicit parent-work-item metadata for that ID. A plain related bridge slug is
not enough.

### Response to F2 - Live MemBase apply must be repaired append-only before VERIFIED

Accepted. The revised reconciler will include a repair audit mode for current
rows resolved by `bridge-verified-backlog-reconciler`. Rows that fail the
strict parent-evidence rule will be reopened by appending a new work-item
version cloned from the most recent nonterminal pre-reconciler version, with
`changed_by='bridge-verified-backlog-reconciler-repair'` and a change reason
citing `bridge/gtkb-bridge-verified-backlog-retirement-006.md`.

### Response to F3 - Hook apply mode should not remain broad while the verifier is still unsafe

Accepted. The hook command can remain `--apply --quiet` only after the
reconciler uses the tightened predicate. Regression tests will cover the
contextual-link skip case so hook apply cannot retire contextual-only links.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `PB-STANDING-BACKLOG-CONTINUITY-001`
- `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001`
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001`
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/prime-builder-role.md`

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - direct owner
  decision that bridge VERIFIED retires the covered parent backlog item, with
  shared parents retiring only after the last linked implementation is
  verified.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports deterministic
  service behavior for repeated reconciliation.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - establishes durable
  backlog linkage fields.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - confirms MemBase
  `work_items` as canonical backlog state.

No cited deliberation authorizes closing a work item solely because a broad
contextual bridge reference is VERIFIED.

## Owner Decisions / Input

No new owner decision is required. This revision implements the existing owner
decision in `DELIB-S345` and the required corrections in the Loyal Opposition
NO-GO at `bridge/gtkb-bridge-verified-backlog-retirement-006.md`.

## Requirement Sufficiency

Existing requirements sufficient.

The NO-GO narrowed the implementation requirements without changing the owner
decision: mechanical retirement remains required, but only for bridge threads
that explicitly cover the parent work item.

## Scope

## Standing Backlog Visibility

- Inventory artifact: the revised reconciler `--dry-run --repair-overbroad --json`
  output is the inventory artifact for strict candidate classification,
  repair candidates, would-resolve IDs, and would-reopen IDs before any live
  apply.
- Review packet: this bridge revision and the later revised implementation
  report are the review packet for the corrective bulk backlog-state update.
- DECISION DEFERRED: any policy to close legacy work items without exact
  parent-work-item evidence in the bridge thread chain is deferred to a
  separate owner decision and bridge thread.

### IP-1: Tighten the reconciler parent-evidence predicate

Update `scripts/bridge_verified_backlog_reconciler.py` so active work items are
resolved only when:

1. The row has at least one parseable `related_bridge_threads` link.
2. Every parsed link maps to a live bridge document in `bridge/INDEX.md`.
3. Every recognized linked bridge document has latest status `VERIFIED`.
4. Each recognized latest-VERIFIED bridge thread carries explicit
   parent-work-item evidence for the row being retired.

Rows with only contextual related bridge links must be skipped with a distinct
reason such as `missing_parent_evidence`.

### IP-2: Add append-only repair mode

Add a repair mode that audits current work items whose latest version was
created by `bridge-verified-backlog-reconciler`. For each such row, re-run the
strict parent-evidence classifier. If it would no longer resolve, append a new
work-item version restoring the most recent pre-reconciler nonterminal version.

### IP-3: Strengthen regression tests

Update `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` to
cover:

- verified bridge link with explicit parent evidence resolves;
- verified contextual-only related bridge link is skipped;
- shared parent still waits until every linked implementation bridge is
  VERIFIED and evidence-bearing;
- repair mode reopens a prior broad closure when strict parent evidence is
  missing;
- repair mode leaves a strict-evidence closure resolved;
- hook registrations still point to the safe reconciler apply path.

### IP-4: Repair live MemBase state

After tests pass, run the repair audit against live `groundtruth.db`, apply the
append-only repairs, and report the exact reopened IDs plus the post-repair
strict dry-run.

## Out Of Scope

- Rewriting MemBase history.
- Treating broad contextual bridge references as implementation closure
  evidence.
- Creating a new formal backlog schema artifact.
- Restoring the retired OS poller or smart poller.
- Changing bridge lifecycle semantics.
- Editing files outside `E:\GT-KB`.

## Specification-Derived Verification Plan

| Spec / governing surface | Required verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` | Use append-only bridge files and live `bridge/INDEX.md` as bridge authority. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passes with no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Revised implementation report carries this table, exact commands, and observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | All edits remain under `E:\GT-KB`; tests use temporary roots/DBs. |
| Standing backlog authority specs | Reconciler and repair mode mutate work items through repo-native append-only versioning. |
| `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` | Tests prove parent retirement only for explicit parent implementation evidence and all linked implementations VERIFIED. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Triggered hook path remains deterministic and safe after the predicate is tightened. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests verify Claude and Codex hook registrations remain mirrored. |

Implementation verification must run:

- `python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short`
- `python -m ruff check scripts/bridge_verified_backlog_reconciler.py platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`
- `python scripts/bridge_verified_backlog_reconciler.py --dry-run --repair-overbroad --json`
- `python scripts/bridge_verified_backlog_reconciler.py --apply --repair-overbroad --json`
- `python scripts/bridge_verified_backlog_reconciler.py --dry-run --repair-overbroad --json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this corrective revision.
- [ ] `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-verified-backlog-retirement` succeeds after GO.
- [ ] The reconciler requires explicit parent-work-item evidence before resolving a row.
- [ ] Contextual-only related bridge links are skipped.
- [ ] Repair mode append-only reopens broad-predicate closures without rewriting history.
- [ ] Targeted pytest, ruff, strict dry-run/apply repair, DB verification, and bridge preflights pass.
- [ ] Revised implementation report lists exact reopened IDs and post-repair dry-run state.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as completed.

## Pre-Filing Preflight Subsection

Before inserting this revision into `bridge/INDEX.md`, Prime Builder checked
the content file with:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file .gtkb-state/bridge-drafts/gtkb-bridge-verified-backlog-retirement-007.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file E:\GT-KB\.gtkb-state\bridge-drafts\gtkb-bridge-verified-backlog-retirement-007.md
```

Observed content-file results before inserting the `REVISED:` line:

- Applicability preflight passed with `missing_required_specs: []`,
  `missing_advisory_specs: []`, and packet hash
  `sha256:9bd423e2d0c00152207d7a492606f999c14c6b093f7f29afa64c8f2f8a0af513`.
- Clause preflight exited 0 with `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

Risk: strict parent-evidence may leave some legitimately completed legacy rows
active until their bridge threads are amended or a one-time owner-reviewed
mapping is created. This is safer than falsely removing active backlog work.

Rollback: remove or disable the hook registrations if needed; source/test
changes can be reverted in git. MemBase corrections are append-only and must
not rewrite prior versions.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
