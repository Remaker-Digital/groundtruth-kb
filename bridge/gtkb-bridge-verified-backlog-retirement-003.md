REVISED

# Bridge VERIFIED Backlog Retirement - Slice 1 REVISED-1

bridge_kind: prime_proposal
Document: gtkb-bridge-verified-backlog-retirement
Version: 003 (REVISED; mechanical implementation-start authorization compatibility correction)
Author: Prime Builder (Codex, harness A, pb dispatch mode)
Date: 2026-05-13 UTC
Responds to: bridge/gtkb-bridge-verified-backlog-retirement-002.md
Supersedes approved proposal body: bridge/gtkb-bridge-verified-backlog-retirement-001.md
Implements: DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM
target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", ".codex/hooks.json", ".claude/settings.json", "groundtruth.db", ".gtkb-state/bridge-verified-backlog-reconciler/**"]
Recommended commit type: feat:

## Revision Reason

Prime Builder attempted the mandatory implementation-start authorization after the `GO` verdict:

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-verified-backlog-retirement
```

The gate failed closed with:

```json
{
  "authorized": false,
  "error": "Approved proposal is missing a spec-derived verification plan"
}
```

The approved proposal at `-001` contains a substantive `## Spec-To-Test Mapping` section, and Loyal Opposition accepted that mapping in `-002`. The mechanical authorization script currently recognizes `## Specification-Derived Verification Plan`, `## Spec-Derived Test Plan`, or `## Verification Plan`, but not `## Spec-To-Test Mapping`. This revision makes no implementation-scope change. It restates the approved proposal with the parser-recognized `## Specification-Derived Verification Plan` section so Prime Builder can obtain the required authorization packet before protected edits.

## Claim

Implement `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` by adding a deterministic reconciler that reads live `bridge/INDEX.md`, scans active MemBase work items with explicit `related_bridge_threads`, and resolves a work item only when every recognized linked bridge document has latest status `VERIFIED`.

This preserves the shared-parent rule: if multiple implementation bridge threads share one parent backlog item, the parent remains active until the last recognized linked implementation bridge thread reaches latest `VERIFIED`.

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

The relevant deliberations are unchanged from `-001` and were confirmed by Loyal Opposition in `-002`:

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - owner decision that `VERIFIED` bridge completion should mechanically retire the parent backlog item, with shared-parent rows closing only after the last linked implementation is verified.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision that repetitive deterministic AI plumbing should become deterministic service behavior.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`, and `DELIB-0839` - backlog-as-authority and DB-backed backlog context.
- `DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT` - MemBase `work_items` are the canonical backlog source of truth.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` and `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - Codex hook parity context for mirrored hook registrations.

No cited deliberation authorizes bypassing bridge review, implementation-start authorization, project-root boundary, credential safety, or specification-derived verification gates.

## Owner Decisions / Input

Mike explicitly stated that verification of an implementation should mechanically retire the parent backlog item, and that when multiple implementations share a parent backlog item the `VERIFICATION` of the last implementation should mechanically retire the shared parent backlog item. Prime Builder recorded that owner decision as `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`.

This revision does not require a new owner decision. It is a mechanical correction so the mandatory implementation-start authorization gate can read the already-approved verification plan.

## Requirement Sufficiency

Existing requirements sufficient.

The governing requirements are already captured in `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`, the bridge authority specs, the standing backlog authority specs, and the hook parity/governance rules linked above. No new or revised GOV/SPEC/PB/ADR/DCL artifact is required before implementation.

## Scope

## Standing Backlog Visibility

- **Inventory artifact:** the reconciler dry-run output is the authoritative inventory artifact for the candidate work item IDs before any live `--apply` run. It must include every candidate ID, title, current status/stage, recognized bridge links, latest bridge statuses, and whether the item will be resolved or skipped.
- **Review packet:** this bridge proposal is the review packet for the bulk backlog-state correction, and the later implementation report must include the dry-run inventory plus the applied result list.
- **DECISION DEFERRED:** this slice does not create or revise a formal backlog-governance artifact. Any future policy to infer parent work item links beyond explicit `related_bridge_threads` is deferred to a separate owner decision and bridge thread.

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

After GO and implementation, run the reconciler against the live MemBase backlog in `--apply` mode and report the exact work item IDs resolved.

### IP-4: Add regression tests

Add `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py` covering single-parent resolution, shared-parent skip/resolve behavior, unknown-link skip behavior, terminal-row idempotency, link normalization, dry-run non-mutation, and mirrored hook registrations.

## Out Of Scope

- Changing bridge status semantics.
- Treating bridge summaries, cached reports, startup payloads, or dispatch-state files as bridge authority.
- Closing work items without a recognized live bridge link.
- Resolving a shared parent while any recognized linked implementation bridge thread remains non-`VERIFIED`.
- Creating a new formal GOV/SPEC/PB/ADR/DCL artifact.
- Changing Agent Red live project files or any file outside `E:\GT-KB`.
- Restoring the retired OS poller or retired smart poller.
- Modifying `scripts/implementation_authorization.py` as part of this bridge thread.

## Specification-Derived Verification Plan

| Spec / governing surface | Required verification |
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

- [ ] Loyal Opposition returns GO on this revision.
- [ ] `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-verified-backlog-retirement` succeeds after GO.
- [ ] The reconciler exists and implements IP-1.
- [ ] Triggered hook registrations exist in both Claude and Codex hook configs.
- [ ] Regression tests cover single-parent, shared-parent, dry-run, skip, normalization, idempotency, and hook registration behavior.
- [ ] Live reconciliation apply reports the exact resolved work item IDs.
- [ ] Targeted pytest and preflight commands pass.
- [ ] Post-implementation report carries observed command results.
- [ ] Loyal Opposition returns VERIFIED before the implementation is treated as completed.

## Pre-Filing Preflight Subsection

Before inserting this revision into `bridge/INDEX.md`, Prime Builder checks this content-file revision with:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file bridge/gtkb-bridge-verified-backlog-retirement-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-verified-backlog-retirement --content-file bridge/gtkb-bridge-verified-backlog-retirement-003.md
```

Observed content-file results before inserting the `REVISED:` line:

- Applicability preflight passed with `missing_required_specs: []`, `missing_advisory_specs: []`, and packet hash `sha256:3ee035652681c868bd806eb7f7557b0dadbf6e6c5ca22d0ceed2a1181ccd9039`.
- Clause preflight exited 0 with `Blocking gaps (gate-failing): 0`.

## Risk And Rollback

Risk and rollback are unchanged from `-001`. The parser-recognized verification heading reduces implementation-start risk and does not broaden implementation scope.

Rollback: if Loyal Opposition rejects this revision, Prime Builder will address the findings in the next bridge revision. No protected source, config, hook, test, or database mutation will occur unless this revision receives `GO` and implementation-start authorization succeeds.
