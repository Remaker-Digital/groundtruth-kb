REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-11-regression-signal-revival
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-11-regression-signal-revival-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4423
Project Authorization: PAUTH-FAB11-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/*.json", "scripts/fab11_assertion_corpus_remediation.py", "scripts/fab11_pytest_evidence_contract.py", "scripts/fab11_pipeline_events_retention.py", "config/governance/pipeline-events-retention.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "config/agent-control/**", ".claude/settings.json", "CLAUDE.md", "groundtruth.db.corrupt-S311-*", "groundtruth.db.pre-backfill-*", "platform_tests/scripts/**"]

KB mutation: YES. This cluster mutates `groundtruth.db` via the governed Python API — append-only re-versioning/retirement of stale-path assertion specs (HYG-029), the GOV-12/GOV-13 amendment to the pytest-as-evidence contract + scoping the `tests` table to Agent Red history + fixing the `kpi_spec_test_mapping` view (HYG-030), and owner-classified prunable-telemetry deletion of `assertion_run` `pipeline_events` rows (HYG-014). `groundtruth.db` is in `target_paths`. No SQLite file is hand-edited; all writes flow through `KnowledgeDB`. The GOV-12/GOV-13 amendments and the CLAUDE.md edit are formal/protected artifacts with approval packets under `.groundtruth/formal-artifact-approvals/`.

---

# FAB-11 — Regression-Signal Revival (Sequenced) — re-aligned to DELIB-...B

WI-4423 (FAB-11) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-029, HYG-044, HYG-030, HYG-014.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

This cluster is **internally SEQUENCED**: corpus repair → sweep revival → pytest-as-evidence contract →
telemetry prune + VACUUM. The order is load-bearing — reviving the SessionStart sweep (HYG-044) before
repairing the assertion corpus (HYG-029) would immediately re-flood `pipeline_events` with ~1,374 false
failures, the exact firehose that bloated the database (HYG-014).

## Revision Scope

REVISED-003 responds to the three NO-GO findings in
`bridge/gtkb-fab-11-regression-signal-revival-002.md`. This is a **substantive redraft**, not a path fix:

- **F1 (superseded owner authority):** the `-001` proposal cited and implemented
  `DELIB-FAB11-REMEDIATION-20260610` (v1). The active `PAUTH-FAB11-20260610` is **v2**, re-keyed to the
  superseding `DELIB-FAB11-REMEDIATION-20260610B`. This redraft cites DELIB-...B as the operative owner
  decision and treats the v1 record as superseded audit history. Per the supersession note, **two**
  decisions changed (HYG-030, HYG-014); **HYG-029 (hybrid) and HYG-044 (re-register after corpus) are
  UNCHANGED** from v1.
- **HYG-030 changed (Decision 2):** from "partial deterministic recorder" to **amend GOV-12/GOV-13 to the
  pytest-as-evidence contract**. Pytest files are formally declared the platform test-evidence surface; the
  MemBase `tests` table is scoped to Agent Red history; the `kpi_spec_test_mapping` view + dependent KPI
  surfaces are fixed so they no longer overstate health from 8,006 stale `pass` rows. The
  `fab11_spec_derived_test_recorder.py` script from `-001` is REMOVED. GOV-12 and GOV-13 are amended via
  formal-artifact-approval packets.
- **HYG-014 changed (Decision 4):** from "archive-then-prune + VACUUM" to **prune + retention.toml +
  VACUUM, NO archive** (the cost/waste framing: do not archive 3.3M near-zero-value dead telemetry rows).
  The archive-first behavior is REMOVED. A **cheap file-level `groundtruth.db` snapshot is taken
  immediately before VACUUM** (insurance, per the active PAUTH), not an off-root archive.
- **F2 (formal-artifact packet paths):** added `.groundtruth/formal-artifact-approvals/*.json` for the
  GOV-12/GOV-13 amendment packets and the CLAUDE.md narrative packet.
- **F3 (off-root archive conflicts with PAUTH v2):** PAUTH v2 forbids `off_root_telemetry_archive`; all
  archive/off-root language is removed. HYG-014 is now prune + retention + VACUUM + cheap pre-VACUUM
  file-level snapshot only.

The valid sequencing constraint (assertion-corpus repair MUST precede sweep revival) is preserved.

## Summary

GT-KB's flagship regression-detection promise (GOV-08 / GOV-18 = SPEC-1662) is currently **inoperative**.
Four causally-linked findings:

- **HYG-029 (root cause):** 1,468 of 2,052 specs-with-runs fail their latest assertion, and ~1,374 of
  those fail solely on `File not found` for root-relative paths (`src/` 746, `admin/` 438, `widget/` 131,
  `tests/` 20, `docs-site/` 19, `docs/` 12, `branding/` 6) relocated under `applications/Agent_Red/` during
  the isolation cutover. This includes **233 status='verified' specs** failing now — among them **8 verified
  protected behaviors** (PB-001, PB-010, PB-011, PB-020, PB-021, PB-022, PB-023, PB-030) and governance
  SPEC-1534 — and the categorizer reports `genuine_drift=0` because real drift is invisible under the noise
  floor.
- **HYG-044 (downstream):** the SessionStart assertion sweep (`.claude/hooks/assertion-check.py`) last fired
  2026-05-13; the hook file exists but is **unregistered** in `settings.json` SessionStart, while CLAUDE.md
  still claims it "runs assertions automatically." No Deliberation Archive record authorized the removal — it
  was lost, not retired.
- **HYG-030 (parallel leg):** the MemBase `tests` table disconnected from live execution on 2026-04-29:
  `max(last_executed_at)`=Apr 29, 8,006 `pass` rows ≥6 weeks stale, 35 verified specs with zero linked tests.
  Platform pytest runs daily but never records back to MemBase, so the governed `tests` artifact and its KPI
  view overstate health.
- **HYG-014 (consequence):** `pipeline_events` holds 3,325,082 rows, 99.93% of them `assertion_run`
  telemetry from the now-dead sweep — ~90% of the 1.32 GB `groundtruth.db` (vs ~47 MB for all other tables
  combined). `assertion_runs` has a retention policy; `pipeline_events` has none.

## Specification Links

- `SPEC-1662` (GOV-18: Assertion Quality Standard) — the assertion-corpus and sweep findings (HYG-029,
  HYG-044) govern the assertion-quality contract this restores.
- `GOV-08` (Knowledge Database is the single source of truth) — governs the telemetry classification
  (prunable vs canonical) and the tests-table/KPI accuracy obligation.
- `GOV-12` (Work item creation triggers test creation) and `GOV-13` (Test artifacts assigned to a plan
  phase) — **amended** to the pytest-as-evidence contract (HYG-030), via formal-artifact-approval packets.
- `GOV-15` (Test fix gate) — the bulk stale-path assertion disposition runs as kb-batch waves under GOV-15
  owner AUQ gating (50-item max per batch).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the hybrid rewrite points assertions at
  `applications/Agent_Red/*` (the contract-correct relocation target); see Isolation Placement Compliance
  below. The proposal relocates no platform files and writes no out-of-root artifact.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the prune/VACUUM step and the contract migration are
  deterministic services, not per-session AI plumbing.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.
- `GOV-STANDING-BACKLOG-001` — WI-4423 is the governed backlog authority; the bulk GOV-15 assertion
  disposition stays backlog-visible (dry-run + per-wave owner AUQ; no silent bulk mutation).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-lifecycle work (append-only spec re-versioning, spec
  retirement, GOV amendment, telemetry reclassification).

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-029/044/030/014).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB11-REMEDIATION-20260610B` — the **authoritative, operative** owner decision set (re-keys
  PAUTH-FAB11 to v2). Supersedes the v1 on HYG-030 (→ pytest-as-evidence) and HYG-014 (→ prune+VACUUM, no
  archive); HYG-029 + HYG-044 unchanged.
- `DELIB-FAB11-REMEDIATION-20260610` — **superseded** v1 (audit history only; do not implement).
- `DELIB-COST-WASTE-FRAMING-20260610` — the value-density lens driving the no-archive (HYG-014) and the
  retire-low-value-artifact (HYG-030) choices.
- HYG-029's DA search found **no prior decision** on mass assertion-path migration; this is the first
  governed disposition of the stale-path corpus.

## Owner Decisions / Input

Operative set: `DELIB-FAB11-REMEDIATION-20260610B` (AskUserQuestion, 2026-06-10; re-run after the cost/waste
framing). Supersedes the v1 on Decisions 3 and 4:

1. **HYG-029 = Hybrid (UNCHANGED).** Script append-only new spec versions rewriting assertion paths to
   `applications/Agent_Red/*` ONLY for the 233 verified specs + 8 protected behaviors + governance SPEC-1534
   (the must-always-pass signal); retire the remaining ~1,124 Agent-Red-era requirement assertions as
   app-scoped history. kb-batch waves (GOV-15, ≤50/batch). Re-run the categorizer to expose the residual ~93
   real failures.
2. **HYG-030 = Amend GOV-12/13 to pytest-as-evidence (CHANGED from v1).** Formally declare pytest files the
   platform test-evidence surface; scope the MemBase `tests` table to Agent Red history; update the
   `kpi_spec_test_mapping` view + dependent KPI surfaces so they no longer overstate health from 8,006 stale
   `pass` rows. GOV-12 + GOV-13 amended via formal-artifact-approval packets. (Rejected: a deterministic
   pytest→tests recorder + backfill; the partial bridge-cited recorder.)
3. **HYG-044 = Re-register AFTER corpus repair (UNCHANGED).** Sequence the `assertion-check.py`
   re-registration in `.claude/settings.json` (+ `.codex` parity) behind the HYG-029 fix; amend CLAUDE.md's
   "Knowledge Database Access" claim to match the actual state until re-registration lands; optionally scope
   the revived sweep to protected_behavior + verified specs for latency.
4. **HYG-014 = Prune + retention.toml + VACUUM, NO archive (CHANGED from v1).** Classify
   `event_type='assertion_run'` `pipeline_events` rows as PRUNABLE TELEMETRY (overriding the default GOV-08
   append-only prohibition for this telemetry class); add `config/governance/pipeline-events-retention.toml`
   mirroring `assertion-runs-retention.toml`; ship a prune+VACUUM script with before/after row/byte evidence;
   take a **cheap file-level `groundtruth.db` snapshot immediately before VACUUM** (insurance, no archive);
   dispose of the 2 dead root DB snapshots (`groundtruth.db.corrupt-S311-*` ~1,190 MB,
   `groundtruth.db.pre-backfill-*` ~76 MB). Targets ~150 MB DB. (Rejected: archive-then-prune — wastes effort
   exporting near-zero-value rows.)

## Requirement Sufficiency

**Existing requirements sufficient (with governed amendment).** The dispositions are fixed by
`DELIB-FAB11-REMEDIATION-20260610B`; the governing specifications (`SPEC-1662`, `GOV-08`, `GOV-12`, `GOV-13`,
`GOV-15`) already constrain the assertion-quality, source-of-truth, test-governance, and test-fix-gate
surfaces. HYG-030 **amends** GOV-12 and GOV-13 (the pytest-as-evidence contract) through the
formal-artifact-approval path — an owner-decided amendment of existing governance specs, not a new
requirement. The exact `N`-day retention horizon for `pipeline-events-retention.toml` is fixed at
implementation with before/after evidence within the owner-approved prune+VACUUM policy.

## Scope and Boundaries

In scope: the four sequenced slices below. Out of scope and explicitly excluded: the full Agent-Red spec
corpus migration to an application-scoped MemBase (isolation workstream); a full pytest→tests recorder (the
owner chose the pytest-as-evidence contract instead); any off-root telemetry archive (PAUTH v2 forbids it);
and deploy/push. This proposal **absorbs and supersedes** the existing-WI overlap the advisory lists for
FAB-11: the stale-assertions architecture-improvement item (HYG-029 supplies the aggregate root cause and
~1,374-spec quantification) and the per-spec test-coverage cluster in the 3178–3224 range (HYG-030 shows the
recording pipeline died upstream). Those overlaps are folded into WI-4423 and described here, not re-filed.

## Cross-Cluster Coordination (FAB-04 overlap on the 2 dead root DB snapshots)

`DELIB-FAB11-REMEDIATION-20260610B` Decision 4 places disposal of the 2 dead root DB snapshots
(`groundtruth.db.corrupt-S311-*`, `groundtruth.db.pre-backfill-*`) inside HYG-014 — a change from the `-001`
framing, which deferred them to FAB-04. FAB-04 (`gtkb-fab-04-storage-reclamation`, GO@-004) covers the
broader ~10.8 GB reclamation (HYG-013/057/058) and its `-001` scope listed those same 2 snapshots. To avoid
double-deletion: the disposal is **idempotent file deletion** (deleting an already-absent file is a no-op),
so whichever cluster implements first disposes them; FAB-11 includes the paths in `target_paths` per the
authoritative DELIB-...B, and FAB-04 should drop them from its scope (or treat the deletion as already done).
This coordination is surfaced explicitly for Loyal Opposition adjudication; no double-deletion risk exists.

## Proposed Implementation

**Slice 1 — HYG-029 assertion-corpus hybrid repair (FIRST).**
`scripts/fab11_assertion_corpus_remediation.py`: a deterministic, dry-run-first script keyed on the
`File not found: <path>` classification (the failure detail names the missing path; the prefix-map
`src|admin|widget|tests|docs-site|docs|branding` → `applications/Agent_Red/...` is mechanical and validated
against live file existence). For each affected spec: if `type='protected_behavior'` OR `status='verified'`
OR id is SPEC-1534, emit a new spec version rewriting the assertion path to the `applications/Agent_Red/*`
location (preserving coverage); otherwise emit a new version marking the assertion retired / app-scoped. Runs
as kb-batch waves under GOV-15 owner AUQ (≤50/batch). Re-run `scripts/assertion_categorize.py` afterward to
expose the residual ~93 genuine failures.

**Slice 2 — HYG-044 sweep re-registration (AFTER Slice 1).**
Re-register `.claude/hooks/assertion-check.py` on SessionStart in `.claude/settings.json` and the tracked
template under `config/agent-control/**` (the in-root SoT for the settings template, since `.claude/` is
gitignored), plus `.codex` parity, optionally scoped to `protected_behavior + verified` specs for startup
latency. Reconcile the CLAUDE.md "Knowledge Database Access" sentence to match actual behavior
(narrative-artifact approval packet under `.groundtruth/formal-artifact-approvals/`). Gated strictly behind
Slice 1 verification so the revived sweep runs against a clean corpus.

**Slice 3 — HYG-030 pytest-as-evidence contract.**
`scripts/fab11_pytest_evidence_contract.py` (deterministic migration): amend GOV-12 and GOV-13 in MemBase
(append-only new spec versions) to declare pytest files the platform test-evidence surface — each amendment
carrying a formal-artifact-approval packet under `.groundtruth/formal-artifact-approvals/`; scope the MemBase
`tests` table to Agent Red history (annotate/version the platform-era `tests` rows as historical); and update
the `kpi_spec_test_mapping` view + dependent KPI surfaces (in `groundtruth-kb/src/groundtruth_kb/db.py`) so
they no longer count the 8,006 stale `pass` rows as live coverage. No new recorder script; pytest IS the
evidence.

**Slice 4 — HYG-014 telemetry prune + retention + VACUUM (LAST; NO archive).**
`config/governance/pipeline-events-retention.toml` mirroring the `assertion-runs-retention.toml` pattern;
`scripts/fab11_pipeline_events_retention.py`: take a **cheap file-level `groundtruth.db` snapshot immediately
before VACUUM** (insurance, in-root, NO off-root archive — PAUTH v2 forbids `off_root_telemetry_archive`),
DELETE `event_type='assertion_run'` `pipeline_events` rows older than the configured horizon through the
governed path (owner-classified prunable telemetry), then VACUUM. Emits before/after row + byte evidence.
Dispose of the 2 dead root DB snapshots (idempotent; see Cross-Cluster Coordination). Add a doctor
freshness/size check so the table cannot silently re-bloat if the sweep is revived.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: FAB-11 is isolation-**positive**. The Slice-1 hybrid rewrite
repoints protected_behavior + verified Agent-Red assertions at `applications/Agent_Red/*` — exactly where
Agent Red files correctly live — and retires/app-scopes the remaining Agent-Red-era requirement assertions
out of the platform regression corpus. It relocates no platform file, creates no out-of-root artifact (this
bridge file is under `E:\GT-KB\bridge\`; the pre-VACUUM snapshot is an in-root file-level copy, NOT an
off-root archive), and reduces Agent-Red residue in the platform DB.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-1662` + `GOV-08` (HYG-029 corpus) | test: after Slice 1, every protected_behavior + verified Agent-Red spec's assertion resolves against an existing `applications/Agent_Red/*` path (no `File not found`); retired specs carry a new retired/app-scoped version (append-only, no row DELETE); the 8 named protected behaviors + SPEC-1534 PASS; categorizer re-run reports a sharply reduced failure count exposing the residual genuine failures |
| `SPEC-1662` (HYG-044 sweep) | test: `assertion-check.py` is registered in the SessionStart array of `.claude/settings.json` + the tracked `config/agent-control/**` template (+ `.codex` parity); a simulated SessionStart fires it; the registration is absent until Slice 1 verification (sequencing assertion) |
| `GOV-12` + `GOV-13` (HYG-030 pytest-as-evidence) | test: GOV-12 + GOV-13 carry amended versions declaring pytest-as-evidence (each with a packet under `.groundtruth/formal-artifact-approvals/`); the `tests` table is scoped to Agent Red history; the `kpi_spec_test_mapping` view no longer counts the 8,006 stale `pass` rows as live coverage |
| `GOV-08` (HYG-014 telemetry) | test: the prune DELETEs `assertion_run` rows older than the horizon (governed path); non-`assertion_run` `pipeline_events` are preserved; a cheap file-level DB snapshot is taken before VACUUM; VACUUM reduces DB file size; before/after row+byte evidence emitted; the doctor size/freshness check FAILs on simulated re-bloat; NO off-root archive is produced |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` for the two new scripts + the db.py view change + `ruff check` AND `ruff format --check` on all changed Python |

## Acceptance Criteria

1. **Slice 1:** stale-path assertions dispositioned per the hybrid policy via GOV-15 kb-batch waves; the 8
   protected behaviors + 233 verified specs + SPEC-1534 no longer fail on `File not found`; categorizer
   exposes the residual genuine-failure set; all dispositions are append-only spec versions (zero hard
   DELETEs of spec rows).
2. **Slice 2:** the SessionStart assertion sweep is re-registered (settings + tracked template + `.codex`
   parity), fires at SessionStart, sequenced strictly after Slice-1 verification; CLAUDE.md accurately
   describes the behavior (with narrative packet).
3. **Slice 3:** GOV-12 + GOV-13 are amended to the pytest-as-evidence contract (with packets); the `tests`
   table is scoped to Agent Red history; the `kpi_spec_test_mapping` view + KPI surfaces no longer overstate
   health from stale `pass` rows.
4. **Slice 4:** `pipeline-events-retention.toml` exists; the prune+VACUUM (NO archive) reclaims the bulk of
   the DB (target on the order of ~150 MB) with before/after evidence and a cheap pre-VACUUM file snapshot;
   the 2 dead root DB snapshots are disposed (idempotent); a doctor check guards against silent re-bloat.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-11-regression-signal-revival-003.md` with a matching `REVISED` line inserted at the
top of `bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten.
`GOV-FILE-BRIDGE-AUTHORITY-001` is honored — `bridge/INDEX.md` remains canonical workflow state and nothing
implements until Loyal Opposition records `GO` on this thread.

## Backlog Visibility

FAB-11 is WI-4423 under `GOV-STANDING-BACKLOG-001`. The Slice-1 bulk assertion disposition is a GOV-15-gated,
dry-run-first, per-wave-owner-AUQ operation over the inventory of ~1,374 stale-path assertion specs (≤50 per
wave) — not a silent bulk mutation; each disposition is an append-only spec version. The GOV-12/GOV-13
amendments and the CLAUDE.md edit carry formal-artifact-approval packets.

## Risk and Rollback

- **Risk — mis-rewrite of an assertion path:** keyed on the `File not found: <path>` classification and
  validated against live file existence before emitting a version; dry-run-first + GOV-15 owner AUQ waves
  (≤50/batch). **Rollback:** spec re-versioning is append-only — re-version back to the prior assertion.
- **Risk — telemetry prune collides with append-only (GOV-08):** the owner classified `assertion_run`
  `pipeline_events` as prunable telemetry in `DELIB-FAB11-REMEDIATION-20260610B`, explicitly overriding the
  default for this class; the cheap pre-VACUUM file snapshot guards the only irreversible step.
  **Rollback:** restore from the pre-VACUUM file snapshot.
- **Risk — amending GOV-12/GOV-13 weakens test governance:** the amendment is the owner-decided
  pytest-as-evidence contract (formal packets); it retires a managed artifact type for platform-era work
  deliberately, keeping pytest as the live evidence surface. **Rollback:** re-version GOV-12/GOV-13.
- **Risk — reviving the sweep re-floods telemetry:** mitigated by the hard sequencing (Slice 2 behind Slice
  1) and the new retention policy (Slice 4).

## Recommended Implementation Routing

**Opus/Codex-supervised, sequenced.** Slices 1, 3, and 4 are KB-mutating and governance-heavy (GOV-15 waves,
GOV-12/13 amendment with packets, owner-classified telemetry prune, irreversible VACUUM) — not cheap-model
candidates. Slice 2 touches a protected narrative (CLAUDE.md) requiring an approval packet. Implement strictly
in slice order; HYG-029 corpus repair MUST precede HYG-044 sweep revival.

## Recommended Commit Type

`fix:` — repairs the dead regression signal (stale corpus, unregistered sweep, disconnected tests/KPI surface,
unbounded telemetry), with `feat:`-class additions (the `pipeline-events-retention.toml` contract and the
doctor re-bloat guard) and `docs:`-class governance amendments (GOV-12/GOV-13 → pytest-as-evidence).
