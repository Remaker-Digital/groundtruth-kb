NEW

# Bridge VERIFIED Backlog Retirement - Slice 1 NEW

bridge_kind: prime_proposal
Document: gtkb-bridge-verified-backlog-retirement
Version: 001 (NEW; mechanical retirement of verified bridge-backed backlog items)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-13 UTC
Implements: DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM
target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", ".codex/hooks.json", ".claude/settings.json", "groundtruth.db", ".gtkb-state/bridge-verified-backlog-reconciler/**"]
Recommended commit type: feat:

## Claim

This proposal implements the owner decision that bridge verification should mechanically remove completed parent backlog work from the active MemBase backlog. The current bridge and backlog are separate subsystems: `bridge/INDEX.md` is the live bridge queue, while `groundtruth.db` current work item rows are the backlog authority. The defect is that a bridge thread can reach latest `VERIFIED` while the parent work item remains active.

The slice adds a deterministic reconciler that reads live `bridge/INDEX.md`, scans active MemBase work items with `related_bridge_threads`, and resolves a work item only when every recognized linked bridge thread has latest status `VERIFIED`. That implements the shared-parent rule: if multiple implementation bridge threads share one parent backlog item, the parent remains active until the last linked implementation is verified.

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

Manual Deliberation Archive and MemBase searches were run before filing with queries for `bridge verification retires parent backlog item`, `mechanical backlog retirement verified bridge`, `DELIB-S345`, `standing backlog DB authority`, and `deterministic services principle`.

Relevant results:

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - owner decision that `VERIFIED` bridge completion should mechanically retire the parent backlog item, with shared-parent rows closing only after the last linked implementation is verified.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repetitive deterministic AI plumbing should become deterministic service behavior.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`, and `DELIB-0839` - backlog-as-authority and DB-backed backlog context.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - Codex hook parity context for mirrored hook registrations.

No cited deliberation authorizes bypassing the bridge, implementation-start authorization, project-root boundary, credential-safety, or specification-derived verification gates.

## Owner Decisions / Input

Mike explicitly stated that verification of an implementation should mechanically retire the parent backlog item, and that when multiple implementations share a parent backlog item the `VERIFICATION` of the last implementation should mechanically retire the shared parent backlog item. Prime Builder recorded that owner decision as `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`.

This proposal does not require a new owner decision before GO. The active owner request is to correct the defect as quickly as possible and proceed with implementation through the governed bridge path.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements are already captured in `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`, the bridge authority specs, the standing backlog authority specs, and the hook parity/governance rules linked above. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Standing Backlog Visibility

- **Inventory artifact:** the reconciler dry-run output is the authoritative inventory artifact for the candidate work item IDs before any live `--apply` run. It must include every candidate ID, title, current status/stage, recognized bridge links, latest bridge statuses, and whether the item will be resolved or skipped.
- **Review packet:** this bridge proposal is the review packet for the bulk backlog-state correction, and the later implementation report must include the dry-run inventory plus the applied result list.
- **DECISION DEFERRED:** this slice does not create or revise a formal backlog-governance artifact. Any future policy to infer parent work item links beyond explicit `related_bridge_threads` is deferred to a separate owner decision and bridge thread.

## Scope

### IP-1: Add the bridge-verified backlog reconciler

Create `scripts/bridge_verified_backlog_reconciler.py`.

Required behavior:

1. Read live `bridge/INDEX.md` as the only authoritative bridge status source.
2. Build the latest status for each `Document:` block.
3. Query active nonterminal MemBase `current_work_items` rows.
4. Parse `related_bridge_threads` conservatively from JSON lists, plain slugs, comma/newline separated strings, or `bridge/<slug>-NNN.md` paths.
5. Recognize only links that map to a live bridge document in `bridge/INDEX.md`.
6. Resolve a work item only when it has at least one recognized bridge link and all recognized linked bridge documents have latest status `VERIFIED`.
7. Skip work items with unrecognized-only links, mixed verified/nonverified links, missing bridge documents, or terminal statuses.
8. Update the work item through the repo-native MemBase API with `resolution_status='resolved'`, `stage='resolved'`, completion evidence naming the verified bridge threads, `changed_by='bridge-verified-backlog-reconciler'`, and a change reason citing `DELIB-S345`.
9. Provide `--dry-run`, `--apply`, `--quiet`, `--json`, and path override flags for project root, DB, and bridge index.
10. Be idempotent: after a row is resolved it must not be re-updated by subsequent runs.

### IP-2: Register triggered reconciliation hooks

Update `.claude/settings.json` and `.codex/hooks.json` so the reconciler runs as a lightweight triggered service after bridge writes and at session stop. The script must skip quickly when there is no applicable active work item and must not use time-based reconciliation as the primary mechanism.

### IP-3: Reconcile existing stale verified-linked backlog rows

After GO and implementation, run the reconciler against the live MemBase backlog in `--apply` mode and report the exact work item IDs resolved. This one-time apply is in scope because it corrects already-completed bridge protocol work whose backlog state was left active.

### IP-4: Add regression tests

Add `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` covering:

1. Single linked parent resolves when the linked bridge document latest status is `VERIFIED`.
2. Shared parent remains active when any recognized linked bridge document is not latest `VERIFIED`.
3. Shared parent resolves when all recognized linked bridge documents are latest `VERIFIED`.
4. Work items with only unrecognized bridge references are skipped.
5. Terminal work item statuses are skipped and not versioned again.
6. `bridge/<slug>-NNN.md` and plain slug references normalize to the same bridge document.
7. Dry-run reports candidates without mutating the database.
8. Hook registrations in `.claude/settings.json` and `.codex/hooks.json` contain the reconciler command.

## Out Of Scope

- Changing bridge status semantics.
- Treating bridge summaries, cached reports, startup payloads, or dispatch-state files as bridge authority.
- Closing work items without a recognized live bridge link.
- Resolving a shared parent while any recognized linked implementation bridge thread remains non-`VERIFIED`.
- Creating a new formal GOV/SPEC/PB/ADR/DCL artifact.
- Changing Agent Red live project files or any file outside `E:\GT-KB`.
- Restoring the retired OS poller or retired smart poller.

## Files Expected To Change

- `scripts/bridge_verified_backlog_reconciler.py` - new deterministic reconciler.
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` - new focused regression coverage.
- `.claude/settings.json` - Claude-side triggered hook registration.
- `.codex/hooks.json` - Codex-side triggered hook registration.
- `groundtruth.db` - MemBase work item versions created by the one-time reconciliation apply after GO.
- `.gtkb-state/bridge-verified-backlog-reconciler/**` - optional local checkpoint/status evidence.

No files outside `E:\GT-KB` are in scope.

## Spec-To-Test Mapping

| Spec / governing surface | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` | Proposal, GO, implementation report, and VERIFIED flow use append-only bridge files; reconciler reads only live `bridge/INDEX.md` for bridge status. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight must pass with no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this table and executes the tests listed here. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md` | All target paths are under `E:\GT-KB`; tests use temporary project roots and never touch Agent Red. |
| Standing backlog authority specs | Tests exercise MemBase work item updates through the repo-native API and preserve active/nonterminal semantics. |
| `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` | Single-parent and shared-parent tests verify closure only after every linked implementation bridge document is `VERIFIED`. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Reconciler converts manual backlog reconciliation into deterministic service behavior. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests assert mirrored Claude and Codex hook registrations. |

Implementation verification must run:

- `python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short`
- `python scripts/bridge_verified_backlog_reconciler.py --dry-run --json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement`

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The reconciler exists and implements IP-1.
- [ ] Triggered hook registrations exist in both Claude and Codex hook configs.
- [ ] Regression tests cover single-parent, shared-parent, dry-run, skip, normalization, idempotency, and hook registration behavior.
- [ ] Live reconciliation apply reports the exact resolved work item IDs.
- [ ] Targeted pytest and preflight commands pass.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as completed.

## Pre-Filing Preflight Subsection

Candidate content preflight will be run before filing the live `NEW` entry:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file .gtkb-state/bridge-drafts/gtkb-bridge-verified-backlog-retirement-001.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file .gtkb-state/bridge-drafts/gtkb-bridge-verified-backlog-retirement-001.md
```

Observed draft result:

- Applicability preflight passed with `missing_required_specs: []`, `missing_advisory_specs: []`, and packet hash `sha256:110a09323c8b36243165ce751691005625f877dfcbc1e4c1ea6a73e647f77c62`.
- Clause preflight exited 0 with `Blocking gaps (gate-failing): 0`.

After filing through the helper, Prime Builder will rerun both preflights against the indexed operative bridge file and revise if any missing required or advisory spec appears.

## Risk And Rollback

**Risk R1 (medium):** A parser bug could resolve too many work items. Mitigation: require a recognized live bridge document, require latest `VERIFIED` for all recognized links, default to dry-run unless `--apply` is explicit, and test mixed-link and unknown-link cases.

**Risk R2 (medium):** Hook registration could add overhead to every session. Mitigation: the reconciler reads a small index and active work-item rows, exits quietly when there are no candidates, and is deterministic/idempotent.

**Risk R3 (low):** The owner used the phrase "retire" while existing MemBase completion convention uses `resolution_status='resolved'`. Mitigation: implementation uses `resolved` for the MemBase status value while the change reason and completion evidence describe active-backlog retirement under `DELIB-S345`.

**Risk R4 (low):** Shared-parent interpretation could be overbroad. Mitigation: the reconciler only considers explicit `related_bridge_threads` on the parent work item; it does not infer siblings from text summaries.

Rollback: disable the hook registration and revert the implementation script/test changes in a follow-up bridge thread if verification finds a defect. For any live MemBase work item version created by the apply step, rollback requires a new corrective work-item version explaining the reversal; the append-only database history is not rewritten.

## Loyal Opposition Asks

1. Confirm that the proposal correctly implements `DELIB-S345` as triggered mechanical reconciliation, not as time-based report cleanup.
2. Confirm that using MemBase `resolution_status='resolved'` is the right implementation value for removing verified bridge-backed work from the active backlog.
3. Confirm that the one-time live reconciliation apply is within scope after GO, provided the implementation reports the exact work item IDs changed.
