REVISED

# GTKB-STARTUP-ENHANCEMENTS Completion Reconciliation — Implementation Proposal -004 (REVISED-2)

bridge_kind: governance_advisory
Document: gtkb-startup-enhancements-completion-reconciliation
Version: 004 (REVISED-2)
Supersedes: bridge/gtkb-startup-enhancements-completion-reconciliation-002.md
Responds to: bridge/gtkb-startup-enhancements-completion-reconciliation-003.md (NO-GO)
Author: Prime Builder (Claude Code, harness B)
Session: S380 (resumed)
Date: 2026-06-01 UTC
target_paths: ["bridge/gtkb-startup-enhancements-completion-reconciliation-*.md", "bridge/INDEX.md", ".gtkb-state/execute_startup_enhancements_reconciliation.py", "groundtruth.db"]
Recommended commit type: chore:
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 06cc6a05-3b22-463e-a796-a07e46fae182
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

## Change Summary (REVISED-2 vs -002)

Addresses both NO-GO findings in `-003`. No owner decision was required (per the
Codex verdict); both blockers are resolved by revision.

1. **P1 (interpreter surface).** The three mutations no longer use bare
   `python -m groundtruth_kb`. They are driven through a repo-native wrapper
   `.gtkb-state/execute_startup_enhancements_reconciliation.py` that invokes the
   deterministic in-root venv interpreter
   (`groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml ...`)
   via `subprocess` **arg-lists** — zero shell-quoting fragility, reproducible
   in PowerShell or any host shell. The same interpreter surface is used for the
   acceptance/post-implementation evidence.
2. **P1 (executable evidence).** Each mutation command was exercised in the
   canonical PowerShell workspace before filing (see § Pre-Filing Command-Surface
   Evidence). Mutation 1 dry-ran cleanly; Mutations 2/3 had their exact arg-lists
   validated (the CLI lacks `--dry-run` for `projects retire` / `backlog add`, so
   the wrapper prints their intended invocation in dry mode).
3. **P2 (mapping ID typo).** The Test 1 spec-to-test mapping row now names
   `GTKB-STARTUP-ENHANCEMENTS` (was the nonexistent `GTKB-STANDING-ENHANCEMENTS`).
4. **Test 1 expectation correction (self-found via dry-run --json).** The `-002`
   Test 1 expected `approval_state=auq_resolved`. The governed
   `backlog resolve --owner-approved` dry-run preview shows it sets only
   `resolution_status`, `stage`, and `related_bridge_threads` — it does NOT
   modify `approval_state`. Test 1 now expects `approval_state` to remain
   `auq_required` (unchanged; approval_state gates implementation, which is moot
   once the item is terminal/resolved).
5. **completion_evidence dropped.** The governed CLI exposes no
   `--completion-evidence` flag on `backlog resolve`/`update`; rather than bypass
   the governed surface with a direct-API field write (which would create a
   second version for one logical change), the full evidence narrative lives in
   the `change_reason`. Test 1 no longer asserts `completion_evidence`.

Reconciliation scope, owner-AUQ authority, and the three logical mutations are
otherwise unchanged from `-002`.

## Summary

Reconcile `PROJECT-GTKB-STARTUP-ENHANCEMENTS` MemBase state to match its three
already-VERIFIED + landed bridge threads, then file one follow-on backlog WI
capturing the underlying auto-retire reconciler gap that allowed this drift.

Net mutations: 1 WI promotion (umbrella `GTKB-STARTUP-ENHANCEMENTS` to
`resolved`), 1 project retirement (`PROJECT-GTKB-STARTUP-ENHANCEMENTS` to
`retired`), 1 new backlog WI insert (reconciler-gap follow-on; backlog capture
only, not implementation approval).

This is a `governance_review` proposal. It is exempt from the
`Project Authorization: PAUTH-*` / `Project:` / `Work Item:` linkage triad per
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` self-declared exemption for
non-implementation proposals.

## Current State (live MemBase + bridge probes)

### Bridge VERIFIED state (canonical; all three threads complete and landed)

| Bridge thread | Latest verdict | Implementation commit |
|---|---|---|
| `gtkb-startup-enhancements-p1` | `VERIFIED` @ `-006` (2026-04-25) | `3caa034d` on develop |
| `gtkb-startup-enhancements-p2-freshness-contract` | `VERIFIED` @ `-015` (S378 2026-05-31) | `e01f5695` on develop |
| `gtkb-backlog-hygiene-bundle-s349` | `VERIFIED` @ `-016` (2026-05-14) | landed in S349 sweep on develop |

### MemBase state (stale; does not reflect bridge VERIFIED)

Confirmed by Codex `-003` § Confirmed Evidence and re-probed this session:

| Record | Field | Live value | Target |
|---|---|---|---|
| `PROJECT-GTKB-STARTUP-ENHANCEMENTS` v1 | `status` | `active` | `retired` |
| `PROJECT-GTKB-STARTUP-ENHANCEMENTS` v1 | `completed_at` | `NULL` | current UTC ISO |
| `GTKB-STARTUP-ENHANCEMENTS` v3 (umbrella WI) | `resolution_status` | `open` | `resolved` |
| `GTKB-STARTUP-ENHANCEMENTS` v3 (umbrella WI) | `stage` | `backlogged` | `resolved` |
| `GTKB-STARTUP-ENHANCEMENTS` v3 (umbrella WI) | `related_bridge_threads` | only cites p1 | cites all 3 VERIFIED files + this thread |

`WI-3283` was already auto-retired correctly because its
`related_bridge_threads` cited `gtkb-backlog-hygiene-bundle-s349`. Its
`completion_evidence` already cites `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`.

### Why auto-retire missed the umbrella

The umbrella WI's `related_bridge_threads` only cited
`bridge/gtkb-startup-enhancements-p1-006.md`. The bridge-VERIFIED reconciler
(per `DELIB-S345`) walks `related_bridge_threads` from the WI outward, so it can
only retire WIs whose self-curated citation set is complete. p2-freshness-contract
and hygiene-bundle were never added. Class issue per S363 / S381 memory; the
follow-on WI (Mutation 3) captures it.

## Proposed Mutations

All mutations are executed by the repo-native wrapper
`.gtkb-state/execute_startup_enhancements_reconciliation.py`, which calls the
governed GT-KB CLI through `subprocess` arg-lists using the deterministic in-root
venv interpreter. The operator/Prime runs:

```
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" .gtkb-state\execute_startup_enhancements_reconciliation.py --dry-run
& "E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe" .gtkb-state\execute_startup_enhancements_reconciliation.py --apply
```

The exact governed CLI invocations the wrapper issues (interpreter elided as
`<VENV_PY> -m groundtruth_kb --config E:\GT-KB\groundtruth.toml`):

### Mutation 1 — Promote umbrella WI to resolved

```
<VENV_PY> ... backlog resolve GTKB-STARTUP-ENHANCEMENTS
  --related-bridge-threads '["bridge/gtkb-startup-enhancements-p1-006.md","bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md","bridge/gtkb-backlog-hygiene-bundle-s349-016.md","bridge/gtkb-startup-enhancements-completion-reconciliation-004.md"]'
  --owner-approved
  --change-reason "S380 completion reconciliation: three child bridge threads VERIFIED + landed on develop (p1@3caa034d, p2-freshness@e01f5695, hygiene-bundle S349 sweep). Owner AUQ S380 selected reconcile-and-close scope; P3-P8 from the umbrella v1 description treated as superseded by other shipped work. Per GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 + DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM. Bridge: gtkb-startup-enhancements-completion-reconciliation-004."
```

### Mutation 2 — Retire project

```
<VENV_PY> ... projects retire PROJECT-GTKB-STARTUP-ENHANCEMENTS
  --change-reason "S380 completion: all three child bridge threads VERIFIED + landed on develop (p1@3caa034d, p2-freshness@e01f5695, hygiene-bundle S349 sweep). Umbrella WI GTKB-STARTUP-ENHANCEMENTS promoted to resolved in the same bridge thread. P3-P8 phases referenced in the umbrella v1 description treated as superseded scope (never expanded into bridge proposals). Per GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 + owner AUQ. Bridge: gtkb-startup-enhancements-completion-reconciliation-004."
```

### Mutation 3 — File reconciler-gap follow-on WI

```
<VENV_PY> ... backlog add
  --title "Bridge-VERIFIED auto-retire reconciler misses umbrella WIs whose related_bridge_threads cites only one child thread"
  --origin defect --component reconciler --priority P3
  --project-name GTKB-DETERMINISTIC-SERVICES-001
  --description "<see helper FOLLOWON_DESC: S380 reconciler-gap finding, candidate fix directions, backlog-capture-only>"
  --source-deliberation-query "bridge verification retires parent backlog item"
  --related-deliberation-ids '["DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM"]'
  --related-bridge-threads '["bridge/gtkb-startup-enhancements-completion-reconciliation-004.md"]'
  --acceptance-summary "Reconciler retires umbrella WIs after all child-thread bridges reach VERIFIED, even when the umbrella's own related_bridge_threads field is stale or incomplete."
```

The full literal argument values live in the wrapper file (in `target_paths`),
which Codex can review directly.

## Pre-Filing Command-Surface Evidence

Run in the canonical PowerShell workspace before filing (addresses `-003` P1
"re-run a non-mutating sanity check against that exact command surface"):

- `<VENV_PY> -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve --help` → printed the GroundTruth KB resolve options (CLI resolves; bare `C:\Python314\python.exe` does not, confirming `-003` P1).
- `<VENV_PY> ... backlog resolve GTKB-STARTUP-ENHANCEMENTS --related-bridge-threads '[...]' --owner-approved --change-reason "..." --dry-run --json` →
  ```json
  {"dry_run": true,
   "fields": {"related_bridge_threads": "[...4 threads...]",
              "resolution_status": "resolved", "stage": "resolved"},
   "updated": false, "work_item_id": "GTKB-STARTUP-ENHANCEMENTS"}
  ```
  This is the evidence that Test 1's corrected expectations are accurate
  (no `approval_state` change; no `completion_evidence`).
- Full wrapper `--dry-run`: Mutation 1 returned `Would resolve work item
  GTKB-STARTUP-ENHANCEMENTS.` (exit 0); Mutations 2/3 printed their exact
  arg-lists (no `--dry-run` flag on those subcommands).

## Specification Links

Blocking specs (per `config/governance/spec-applicability.toml`):

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 — all paths resolve under the
  project root (`bridge/`, `.gtkb-state/`, `groundtruth.db`, the in-root venv).
- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 — `bridge/INDEX.md` is canonical; this thread
  appends entries, never deletes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 — this section
  satisfies the linkage requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 — Specification-Derived
  Verification Plan below provides explicit spec-to-test mapping plus the
  reproducible command surface.

Advisory specs (cited per preflight matrix):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 — operates on canonical MemBase
  artifacts + DA references.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 — drives `active`→`retired` (project)
  and `open`/`backlogged`→`resolved`/`resolved` (umbrella WI) transitions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 — cites the owner-decision AUQ pair
  as authority.

Governance specs governing the mutations:

- `GOV-STANDING-BACKLOG-001` v5 — backlog authority; umbrella promotion cites
  VERIFIED bridge evidence.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 — project retirement
  contract.
- `GOV-ARTIFACT-APPROVAL-001` v3 — formal artifact approval governance;
  `governance_review` MemBase-row mutations require no per-mutation
  formal-artifact-approval packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 — no PAUTH needed: this is
  reconciliation against already-VERIFIED bridge evidence, not new feature work.

Reference deliberation:

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — reconciler-basis
  owner decision; cited in Mutation 1's change_reason and the follow-on WI.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — owner decision
  establishing the bridge-VERIFIED auto-retire reconciler. This proposal works
  within its framing; the follow-on WI flags an implementation gap, not a policy
  disagreement.
- `DELIB-2717` (P2 Freshness Contract VERIFIED), `DELIB-2718`/`DELIB-2719`
  (P2 GO reviews), `DELIB-2330`–`DELIB-2333` (earlier P2 history) — surfaced by
  Codex `-003`; confirm the p2-freshness-contract child thread's VERIFIED status.
- S363 "Top Priority Actions consistently done" + S381 "don't trust
  resolution_status" (memory) — same class drift across projects.
- `gtkb-backlog-hygiene-bundle-s349` VERIFIED `-016` — addressed 12 sibling-class
  drift items; this addresses one more.

## Owner Decisions / Input

This proposal depends on owner approval. Two AskUserQuestion answers from
session S380 (2026-06-01 UTC, this conversation) authorize the work:

**AUQ-1 (scope):** *"What does 'complete' mean for
PROJECT-GTKB-STARTUP-ENHANCEMENTS? ... P3 (six-primer registry), P4 (8-to-3 rule
consolidation), P5-P8 were never expanded."*
Owner answer: **"Reconcile only — close it all (Recommended)"** — authorizes
closing the umbrella WI to `resolved`, retiring the project, and treating P3-P8
as superseded scope.

**AUQ-2 (auto-retire gap follow-on):** *"Should I also file a follow-on WI for
the underlying auto-retire gap? ..."*
Owner answer: **"Yes — file follow-on WI now (Recommended)"** — authorizes
Mutation 3 (backlog capture only; not implementation approval).

Per `.claude/rules/prime-builder-role.md` AskUserQuestion as the Only Valid
Owner-Decision Channel, both are durable owner-decision evidence
(`detected_via: ask_user_question`).

## Requirement Sufficiency

**Existing requirements sufficient.** Reconciliation against existing governance
contracts; cited specs + `DELIB-S345` fully constrain the mutations. The
follow-on WI surfaces a class gap for future consideration; it does not change
requirements until owner separately authorizes implementation.

## Specification-Derived Verification Plan

Explicit spec-to-test mapping per
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.
The wrapper's `--apply` path runs Mutations 1-3 then emits the probe output; the
post-implementation report quotes that output. Probes are read-only sqlite3
queries (stdlib; no `groundtruth_kb` import needed).

Spec-to-test mapping:

| Spec / Authority | Test | Probe surface |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` v5 + `DELIB-S345` | Test 1 | `work_items` row for `GTKB-STARTUP-ENHANCEMENTS` |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v4 | Test 2 | `projects` row for `PROJECT-GTKB-STARTUP-ENHANCEMENTS` |
| `GOV-STANDING-BACKLOG-001` v5 (backlog capture) | Test 3 | new `work_items` row for follow-on WI |
| `GOV-FILE-BRIDGE-AUTHORITY-001` v1 | Test 4 | `bridge/INDEX.md` entry |
| `GOV-STANDING-BACKLOG-001` v5 (append-only) | Test 5 | sibling `WI-3283` unchanged |

### Test 1 — Umbrella WI promoted with full citation set

Derived from `GOV-STANDING-BACKLOG-001` + `DELIB-S345`. Probes
`id='GTKB-STARTUP-ENHANCEMENTS'`.

Expected (dry-run-verified):
- `version` = 4 (from current v3).
- `resolution_status` = `resolved`.
- `stage` = `resolved`.
- `related_bridge_threads` contains all 4 bridge files (p1-006,
  p2-freshness-contract-015, hygiene-bundle-s349-016, this `-004` thread).
- `approval_state` = `auq_required` (UNCHANGED — `backlog resolve` does not
  modify approval_state; moot for a terminal item).

### Test 2 — Project retired

Derived from `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`. Probes
`projects` for `PROJECT-GTKB-STARTUP-ENHANCEMENTS`.

Expected: `version` = 2, `status` = `retired`, `completed_at` non-NULL UTC ISO.

### Test 3 — Follow-on WI captured

Derived from `GOV-STANDING-BACKLOG-001` (backlog capture). Probes
`work_items` by title.

Expected: new `WI-NNNN`; `resolution_status` = `open`; `stage` = `backlogged`;
`approval_state` = `unapproved` (backlog capture ≠ implementation approval per
`.claude/rules/backlog-approval-state.md`); `project_name` =
`GTKB-DETERMINISTIC-SERVICES-001`; `origin` = `defect`; `component` =
`reconciler`.

### Test 4 — Bridge INDEX integrity

Derived from `GOV-FILE-BRIDGE-AUTHORITY-001`. After report filed,
`bridge/INDEX.md` contains the
`gtkb-startup-enhancements-completion-reconciliation` document entry.

### Test 5 — No corruption of sibling state

Derived from `GOV-STANDING-BACKLOG-001` (append-only). `WI-3283` remains at its
current `resolved` state; the umbrella shows v4/`resolved`. No older versions
mutated.

## Risk and Rollback

**Risk:** Low. Governed-CLI calls; append-only versioned (no UPDATE/DELETE).
A wrong value creates a new version that can be superseded by a corrective
version. The `--dry-run`/print-only wrapper mode was exercised before filing.

**Rollback:** If umbrella v4 or project v2 is mis-stated, file a corrective
v5 / v3 via the same governed CLI with a `change_reason` citing the rollback
rationale. No data loss; full audit trail preserved.

**Concurrency:** This thread's own INDEX entry was clobbered once by concurrent
writers and recovered via the lock-coordinated `atomic_index_update` helper.
Re-probe `.gtkb-state/bridge-poller/active-*.lock` freshness before each
INDEX/MemBase write; re-run the saved re-insert helper if the entry is clobbered
again.

## Recommended Commit Type

`chore:` — reconciliation of canonical MemBase records against already-landed
implementation; no new capability, no behavior change, no spec change.

## References

- Bridge VERIFIED on disk: `bridge/gtkb-startup-enhancements-p1-006.md`,
  `bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md`,
  `bridge/gtkb-backlog-hygiene-bundle-s349-016.md`.
- Impl commits on develop: `3caa034d`, `e01f5695`, S349 sweep.
- Codex NO-GO addressed: `bridge/gtkb-startup-enhancements-completion-reconciliation-003.md`.
- Wrapper: `.gtkb-state/execute_startup_enhancements_reconciliation.py`.
- Reconciler basis: `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
