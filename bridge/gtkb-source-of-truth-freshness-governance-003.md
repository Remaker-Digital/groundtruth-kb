REVISED

bridge_kind: governance_advisory
Document: gtkb-source-of-truth-freshness-governance
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-30 UTC
Session: S376 (provisional)
Supersedes: -001 (NO-GO at -002, FINDING-P1-001)
Recommended commit type: feat

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-source-of-truth-freshness-governance-003
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style, 1M context

# Implementation Proposal (REVISED-1) — Source-of-Truth-Freshness Governance Formalization (WI-3501)

## Revision History / Findings Resolution

This REVISED-1 (`-003`) supersedes `-001` to resolve the single blocking
finding in the Loyal Opposition NO-GO at `-002`:

- **FINDING-P1-001 (post-implementation report version collides with the
  verdict version)** — RESOLVED. The `-001` Implementation Plan step 5
  hardcoded the post-implementation report filename as
  `bridge/gtkb-source-of-truth-freshness-governance-002.md`. That version is
  now occupied by the Loyal Opposition verdict. Step 5 below is rewritten to
  compute the next available monotonic bridge version from live
  `bridge/INDEX.md` at filing time, with no hardcoded version number. This
  removes the collision and is robust to any number of intervening REVISED/GO
  round-trips.

No other substantive change from `-001`. The two non-blocking confirmations
Loyal Opposition recorded at `-002` are noted in `## Open Questions` below:
the `bridge_kind: governance_review` exemption is accepted, and the framing
of divergent counts as motivating evidence (not fixed acceptance criteria) is
confirmed correct.

## Purpose

Formalize the owner principle captured this session as durable GroundTruth-KB
governance: a Deliberation Archive record, a `GOV` spec, and a `DCL` with a
machine-checkable assertion. The principle (owner verbatim) is:

> Avoid cached copies or snapshots; prefer that all information about the
> state of a source-of-truth is a fresh read of the source, not of a copy or
> summary. Reconsider only if latency or overload become problems, which they
> are not at this time.

This is a governance-only proposal. It scopes the creation of three formal
artifacts and authorizes the per-artifact formal-artifact-approval packets
required by `GOV-ARTIFACT-APPROVAL-001`. It does NOT modify source code,
tests, hooks, or scripts; downstream consumers (WI-3500 rollup fix,
WI-3503 referential-integrity remediation, WI-3502 cached-surface audit)
will be filed as separate bridge threads citing the GOV/DCL landed here.

## Owner Decisions / Input

Owner AUQ approvals on record this session (Loyal Opposition captured prior
to the Prime Builder handoff that initiated this proposal):

1. Owner approved capturing the reporting-surface finding as a backlog item.
   - Durable evidence: `WI-3500` row in MemBase (rowid 5120), `changed_at =
     2026-05-30T20:56:58+00:00`, `changed_by = loyal-opposition/claude`,
     `change_reason` cites owner explicit approval, `source_owner_directive`
     carries the owner principle verbatim.

2. Owner selected `Formalize + audit WI` (chosen option among three): promote
   the principle to a formal governance spec (DA + GOV/DCL) AND open a
   companion audit work item.
   - Durable evidence: `WI-3501` row in MemBase (rowid 5121), `changed_at =
     2026-05-30T21:00:51+00:00`, `change_reason` cites owner AUQ approval
     this session; companion audit captured as `WI-3502` (rowid 5122).

3. Owner approved capturing the referential-integrity gap as its own WI.
   - Durable evidence: `WI-3503` row in MemBase (rowid 5123), `changed_at =
     2026-05-30T21:07:40+00:00`, `change_reason` cites owner AUQ approval
     this session.

4. Routing handoff: Loyal Opposition handed the work to Prime Builder via the
   chat handoff text that opened this Prime session, naming WI-3500, 3501,
   3502, 3503, the recommended ordering (WI-3501 first), and explicit
   DO-NOT items including "do not skip the bridge because of pre-approval"
   and "re-derive all counts from groundtruth.db".

The AUQ owner-conversation records have NOT YET been archived to the
Deliberation Archive (the most recent `owner_conversation` deliberations are
`DELIB-2511..DELIB-2520`, with `DELIB-2515..2520` known-polluted per the
in-flight retraction thread). Authoring that DA record IS task (a) of this
proposal; the WI rows above are the durable evidence trail that upgrades to
a DELIB-* record once this proposal lands.

The proposal asks owner for NO additional decisions beyond the AUQ scope
already captured. The per-artifact formal-artifact-approval packets
(generated at implementation time via `gt generate-approval-packet`) each
require their own owner acknowledgement per `GOV-ARTIFACT-APPROVAL-001`;
those acknowledgements are inside the implementation phase, not preconditions
for this `GO`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` — formal approval gate; every artifact created here goes through its own approval packet.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — mechanical enforcement at insertion time.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder responsibility for the approval evidence trail.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — gate scope and applicability.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority; this proposal lives in `bridge/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this very Specification Links section is required, must cite every relevant cross-cutting spec, and the proposed tests must derive from those specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — post-implementation verification must execute spec-derived tests.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness write-path enforcement applies to artifact insertions performed here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal self-declares `bridge_kind: governance_review` per the SKILL-sanctioned exemption set, because PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS has no PAUTH at filing time and this proposal scopes pure governance artifact authoring rather than source mutation. (Loyal Opposition accepted this exemption at `-002`.)
- `GOV-08` (KB is truth) — direct precedent at type=governance, status=verified. The new GOV does NOT redefine it; it extends the principle from "all knowledge in KB" to "all reads of source-of-truth state are fresh reads of the canonical source, not of caches/snapshots/summaries."
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — architectural pattern precedent: a canonical read surface formalized as governance. The proposed DCL applies the same pattern to numeric reporting/state surfaces.
- `ADR-0001` (Three-Tier Memory Architecture) — defines MemBase as canonical truth, MEMORY.md as operational notepad (not canonical), Deliberation Archive as design-reasoning record. The fresh-read principle reinforces the tier separation: reading from MEMORY.md to claim canonical truth is exactly the violation pattern the new GOV/DCL formalize.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — chat-derived owner principles must reach a formal spec via owner-visible confirmation. The AUQ evidence in `## Owner Decisions / Input` satisfies the confirmation requirement.
- `GOV-STANDING-BACKLOG-001` — work items cited here (WI-3500/3501/3502/3503, WI-3481) live in the canonical MemBase `work_items` authority; the proposal reads them through `current_work_items` and `current_project_work_item_memberships` rather than any markdown view.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete owner decisions, requirements, and risks preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts, tests, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle transition vocabulary (candidate, specified, verified, retired) used by the proposed GOV/DCL.
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concepts must reach the glossary when first touched; the proposed GOV/DCL introduce "fresh-read invariant" and "declared-TTL cache" as new load-bearing terms requiring glossary promotion (sequenced as a downstream sibling, not blocking).

## Prior Deliberations

Relevant deliberations and prior decisions identified by direct DA search
and existing-spec audit (see `## Reproduction Commands` below for the exact
queries executed):

- `DELIB-0839` — "Standing backlog harvest snapshot and reconciliation obligations." Directly relevant: it inventoried bridge / MemBase / release-readiness sources and added standing-backlog reconciliation obligations. The fresh-read principle sharpens the same reconciliation discipline by requiring reads to derive from canonical tables, not cached harvest snapshots.
- `DELIB-1580` — "Loyal Opposition Verification — Backlog Work List Retirement Directive" (VERIFIED). Strongly relevant: it formalized retirement of `memory/work_list.md` so that MemBase `work_items` becomes the sole authority. The fresh-read principle is the steady-state rule that prevents the same regression class once a canonical authority is established.
- `DELIB-1469` — "GT-KB Self-Measurement and Self-Improvement Advisory." Relevant: defines benchmarks and metric snapshots as observation-only outputs that do not become canonical state. The proposed DCL preserves this separation (declared-TTL caches are permitted; un-declared cached state is forbidden).
- `DELIB-0018` — "INSIGHTS-2026-03-25-21-07 Project Progress Dashboard KPI Proposal." Relevant: dashboard KPIs over canonical state. The fresh-read principle constrains dashboard KPI derivation paths to canonical reads.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — adjacent precedent: lifecycle independence is a runtime invariant, not file-relocation. The fresh-read principle is similarly a runtime invariant on read-path derivation, not a refactor.
- Existing-spec precedents: `GOV-08` (KB is truth; verified), `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (glossary IS canonical DA read surface), `GOV-ENV-LOCAL-AUTHORITY-001` (env source-of-truth), `ADR-ENV-SOT-TOPOLOGY-001` (env SoT topology). These together establish the pattern of formalizing read-path discipline as governance; the proposed GOV/DCL extend that pattern to reporting/state numeric surfaces.
- Negative precedent / driving incident: the live demonstration that motivated this proposal — `scripts/session_self_initialization.py`'s startup rollup banners 106 / 20 / 33 / 13 (depending on definition), and the LO handoff itself surfaced still-different counts vs. my fresh re-read (210 / 120 / 133 / 14-or-15). The divergence-of-snapshots-over-time pattern is the failure mode the GOV/DCL forbid. (Loyal Opposition confirmed at `-002` that this divergence is correctly framed as motivating evidence, not fixed acceptance criteria.)

## Requirement Sufficiency

Existing requirements sufficient. The owner principle is captured verbatim
in `WI-3500/3501/3502/3503.source_owner_directive`; acceptance criteria for
each WI are explicit (see `acceptance_summary` fields); the AUQ approvals in
`## Owner Decisions / Input` authorize the work. No new owner-stated
requirement is added by this proposal; it CAPTURES and FORMALIZES the
already-stated owner principle.

## Proposed Scope

In scope (this thread; via per-artifact formal-artifact-approval packets):

1. Insert a `DELIB-*` record into MemBase with `source_type='owner_conversation'`,
   `outcome='owner_decision'`, `session_id='S376'` (or current session id at
   implementation time), capturing the question, the three options (none /
   capture-only / formalize+audit), the chosen option (formalize+audit), the
   owner principle verbatim, the latency/overload reconsideration trigger,
   the WI rows authored as durable evidence (WI-3500/3501/3502/3503), and
   the implementation routing to Prime Builder.

2. Insert `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` into MemBase
   (`type='governance'`, `status='specified'`). Body asserts the fresh-read
   principle as governance:

   - All information about the state of a source-of-truth MUST be derived from
     a fresh read of the canonical source (canonical table, canonical view,
     authoritative file).
   - Cached copies, snapshots, summaries, and denormalized compatibility
     columns MUST NOT be the basis of state claims about a source-of-truth.
   - Declared-TTL caches are permitted when the TTL is documented at the
     cache's read site and the source-of-truth is reachable for re-read.
   - Reconsideration trigger: revisit only if latency or overload become
     observable problems (owner statement: not at this time).

3. Insert `DCL-REPORTING-SURFACE-FRESH-READ-001` into MemBase
   (`type='design_constraint'`, `status='specified'`, governs
   `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`). Machine-checkable assertion (grep /
   structural surface for the future assertion engine; the assertion below is
   the canonical wording for downstream implementation by WI-3500's rollup
   fix and the WI-3502 audit):

   > For each numeric or state-summarizing surface listed in the GOV-SOURCE-OF-TRUTH-FRESHNESS-001 § Reporting Surfaces section, the implementation MUST read its source data from a canonical table or view (e.g., `current_project_work_item_memberships`, `current_projects.status`, `current_work_items.resolution_status`) rather than from a denormalized compatibility column (e.g., `work_items.project_name`), a cached file (e.g., `.claude/hooks/last-user-visible-startup-*.md`), a frozen snapshot (`backlog_snapshots` consumed as live), or a summary report. Declared-TTL caches are permitted only when the read site declares the TTL inline and falls back to the canonical source when the cache is stale.

4. Link the inserted GOV/DCL as `source_spec_id` (or via
   `related_spec_ids_at_creation`) on WI-3500, WI-3502, WI-3503 so the
   downstream implementation threads carry the governance citation.

Out of scope (separate downstream bridge threads, sequenced after Codex `GO`
and post-impl `VERIFIED` here):

- WI-3500 rollup fix in `scripts/session_self_initialization.py` (canonical
  membership read + active-project join). Coordinated with the reporting-half
  of WI-3503 in a single follow-on proposal per the handoff's explicit
  "do NOT file separate WI-3500 and WI-3503 rollup proposals" directive.
- WI-3503 integrity half: reconcile the 13 dangling memberships, move
  `scripts/discover_orphan_wi_memberships.py` to the STRICT definition, add
  a doctor/integrity check. Coordinated with WI-3481 (premature auto-retire
  scanner) and the GO'd orphan-WI Slice-2 thread.
- WI-3502 classified inventory of cached / snapshot / summary surfaces, with
  child fix WIs per must-fix surface.
- Glossary promotion of "fresh-read invariant" and "declared-TTL cache" per
  `DCL-CONCEPT-ON-CONTACT-001` (downstream sibling; not blocking).
- Future creation of `PAUTH-PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS-*` as a
  project-scoped implementation authorization once a downstream
  implementation thread requires it.

## Proposed Artifacts (Provisional Content)

The exact body text for each artifact is drafted here so the per-artifact
approval packets at implementation time have a stable reference. Minor
copy-edits during packet generation are expected; substantive changes from
the wording here require a separate per-artifact approval cycle.

### DELIB-* (Deliberation Archive record)

- `source_type`: `owner_conversation`
- `outcome`: `owner_decision`
- `session_id`: current session at implementation time (provisional: `S376`)
- `title`: "Source-of-truth freshness principle: avoid cached copies; prefer fresh reads"
- `summary` (one sentence): "Owner directs that all state claims about a source-of-truth must derive from a fresh read of the canonical source; caches/snapshots/summaries are not permitted unless declared-TTL with an inline fallback to canonical."
- `content`: question asked, three options offered, chosen option, rationale, latency/overload reconsideration trigger, the four authored WIs (WI-3500/3501/3502/3503) as durable evidence anchors, the live-divergence demonstration (handoff's 106/20/33/13 vs Prime fresh-read 210/120/133/14-or-15) as motivating example.

### GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (Governance spec)

- `type`: `governance`
- `status`: `specified`
- `title`: "Source-of-truth freshness: state claims derive from fresh canonical reads"
- Body sections:
  - Principle (the owner verbatim text)
  - Scope: applies to reporting surfaces, state rollups, dashboard KPIs, doctor checks, and any read-path that produces a claim about the state of a canonical source-of-truth (MemBase tables/views, canonical configuration files, bridge/INDEX.md, harness-state JSON).
  - Reporting Surfaces (initial list; WI-3502 audit expands this): `scripts/session_self_initialization.py` rollup; the cached startup-disclosure payload at `.claude/hooks/last-user-visible-startup-*.md`; the dev-environment inventory snapshot; consumers of `backlog_snapshots`; dashboard KPIs that group by `work_items.project_name`.
  - Declared-TTL exception (precise wording from the principle).
  - Reconsideration trigger: latency or overload become observable problems.
  - Linkage: extends `GOV-08`; follows the architectural pattern of `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`; constrained by `ADR-0001` tier separation.
  - Initial assertions (informational; the assertion engine will exercise these post-WI-3500 / WI-3502 landing): the startup rollup's `ungrouped non-terminal` count equals the canonical-view query result; the startup `Active project states` list excludes `current_projects.status != 'active'` rows.

### DCL-REPORTING-SURFACE-FRESH-READ-001 (Design constraint)

- `type`: `design_constraint`
- `status`: `specified`
- `source_spec_id`: `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `title`: "Reporting and state surfaces read canonical sources, not denormalized columns or caches"
- Body sections:
  - Constraint (the machine-checkable wording quoted in `Proposed Scope` item 3 above).
  - Surface enumeration (the same list as GOV § Reporting Surfaces; the DCL pins each surface to its required canonical source).
  - Assertions field: grep_absent patterns forbidding `work_items.project_name` group-by in production reporting paths; grep patterns requiring canonical-view join in those same paths. (Provisional; precise grep strings finalized at implementation time so they don't false-positive on this proposal's text.)
  - Declared-TTL escape clause: the read site must declare the TTL inline (e.g., a constant or comment) and must fall back to the canonical source when the TTL is exhausted.

## Implementation Plan

After Codex `GO` on this proposal:

1. Generate the three per-artifact formal-artifact-approval packets via
   `gt generate-approval-packet` (or per the canonical packet schema if the
   CLI surface differs at impl time), one per artifact: DELIB, GOV, DCL.
   Each packet captures the full content, the content SHA-256, the
   `presented_to_user=true` + `transcript_captured=true` audit flags, the
   `changed_by` Prime Builder attribution, the `change_reason` citing this
   bridge thread + the owner AUQ evidence, and `approved_by=owner`.

2. Run `python scripts/implementation_authorization.py begin --bridge-id gtkb-source-of-truth-freshness-governance` to mint the implementation-start packet against this thread's GO.

3. Insert the three artifacts in order: DELIB first (so the GOV/DCL can
   cite it), then GOV, then DCL. Each insertion uses `python -m groundtruth_kb` (CLI) or the matching `groundtruth_kb.db` Python API; insertion is gated by `formal-artifact-approval-gate.py` against the per-artifact packet.

4. Update WI-3500, WI-3502, WI-3503 to record the new GOV/DCL spec IDs in
   `source_spec_id` or `related_spec_ids_at_creation`, plus add this bridge
   thread to `related_bridge_threads`. WI updates are versioned and use the
   standard `gt backlog update` / `db.insert_work_item(new_version=...)`
   surface.

5. File the post-implementation report as the NEXT AVAILABLE MONOTONIC bridge
   version after the Loyal Opposition verdict, computed from live
   `bridge/INDEX.md` at filing time (do NOT hardcode a version number — the
   exact number depends on how many REVISED/GO round-trips precede the report;
   read the thread's latest version from INDEX and increment). The report
   carries forward Specification Links, provides the spec-to-test mapping
   (`## Spec-Derived Tests`), the commands executed, the observed results, and
   the recommended commit type (`feat`).

6. After Codex `VERIFIED`, commit through the standard scoped-commit path
   (`git commit -F <message file>`; explicit-pathspec staging to avoid
   parallel-session contamination per session-memory feedback).

## target_paths

- `groundtruth.db` (DA + GOV + DCL inserts; plus WI versioned updates)
- `.groundtruth/formal-artifact-approvals/2026-05-30-delib-source-of-truth-freshness-principle.json`
- `.groundtruth/formal-artifact-approvals/2026-05-30-gov-source-of-truth-freshness-001.json`
- `.groundtruth/formal-artifact-approvals/2026-05-30-dcl-reporting-surface-fresh-read-001.json`

Notes:

- The DELIB packet filename is a placeholder; the canonical packet naming
  per the formal-artifact-approval-packet glossary entry is
  `<date>-<artifact-id>.json`. The DELIB ID is assigned at insert time, so
  the packet may be renamed to match the assigned ID inside the
  implementation step. The hash-bound content is what the gate matches.
- No source-code, test, hook, script, configuration, or rule-file path is
  in scope. Any drift toward those paths is out of scope for this thread.

## Spec-Derived Tests / Verification

Each test below derives directly from a Specification Link or from the
acceptance criteria of WI-3501. Tests are executed at implementation time
and reported in the post-impl report (filed at the next monotonic version
per Implementation Plan step 5).

| Test ID | Derives From | Procedure | Pass Criterion |
|---|---|---|---|
| T1 | `WI-3501.acceptance_summary` item 1; `DELIB` proposed-content | `python -m groundtruth_kb deliberations get <DELIB-ID>` after insertion | Row exists with `source_type='owner_conversation'`, `outcome='owner_decision'`, content includes the verbatim owner principle and the three-option AUQ structure. |
| T2 | `WI-3501.acceptance_summary` item 2; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` proposed body | `python -m groundtruth_kb spec get GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Row exists with `type='governance'`, `status='specified'`, body includes Scope + Reporting Surfaces + Declared-TTL exception + Reconsideration trigger sections. |
| T3 | `WI-3501.acceptance_summary` item 3; `DCL-REPORTING-SURFACE-FRESH-READ-001` proposed body | `python -m groundtruth_kb spec get DCL-REPORTING-SURFACE-FRESH-READ-001` | Row exists with `type='design_constraint'`, `status='specified'`, `source_spec_id='GOV-SOURCE-OF-TRUTH-FRESHNESS-001'`, machine-checkable assertion is present. |
| T4 | `WI-3501.acceptance_summary` item 4; `GOV-STANDING-BACKLOG-001` linkage discipline | `python -m groundtruth_kb backlog show WI-3500 --json` (and `WI-3502`, `WI-3503`) | Each WI row records the new GOV ID in `source_spec_id` or `related_spec_ids_at_creation` and this bridge thread in `related_bridge_threads`. |
| T5 | `GOV-ARTIFACT-APPROVAL-001` packet evidence | Inspect `.groundtruth/formal-artifact-approvals/2026-05-30-*` JSON files | Three packets exist; each carries the required fields (`presented_to_user=true`, `transcript_captured=true`, content SHA-256 matches the inserted artifact). |
| T6 | `GOV-08` non-regression | `python -m groundtruth_kb spec get GOV-08` | GOV-08 unchanged (still `verified`); no rewrite or supersede performed. |
| T7 | `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` non-regression | `python -m groundtruth_kb spec get GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Unchanged; this proposal extends the pattern but does not modify the source. |

Pre-file code-quality gates: no Python files are added or modified by this
proposal, so `ruff check` / `ruff format --check` do not apply. The
post-impl report will state this explicitly.

## Risks and Rollback

- Risk: DELIB content_hash collision if the helper is re-run. Mitigation: the
  insert path checks content_hash; duplicate inserts are no-ops.
- Risk: Provisional artifact IDs (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
  `DCL-REPORTING-SURFACE-FRESH-READ-001`) already in use. Mitigation:
  pre-flight collision check at impl time (T6/T7 above); rename if collision
  is found.
- Risk: Future reads of cached/snapshot surfaces (audited by WI-3502)
  produce DCL violations. Acceptance: expected; WI-3502 is precisely the
  inventory-and-remediate companion.
- Risk: The proposed DCL assertion is currently a textual constraint, not yet
  exercised by the live assertion engine. Mitigation: WI-3500 / WI-3502
  downstream threads add grep/structural assertions when the rollup is fixed.
- Rollback: append-only versioning means rollback is via supersede, never
  delete. If owner withdraws the principle, file a superseding DELIB, mark
  the GOV/DCL `retired` via the standard spec-promote / spec-retire path,
  and unlink them from the dependent WIs. No destructive removal is required.

## Reproduction Commands

Recorded for transparency and so Codex can re-verify the fresh-read
foundation:

```text
python -m groundtruth_kb backlog show WI-3500 --json
python -m groundtruth_kb backlog show WI-3501 --json
python -m groundtruth_kb backlog show WI-3502 --json
python -m groundtruth_kb backlog show WI-3503 --json
python -m groundtruth_kb backlog show WI-3481 --json
python -m groundtruth_kb projects show PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS --json
python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json
python -m groundtruth_kb projects authorizations PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS --json
python -m groundtruth_kb deliberations search "fresh read source of truth caching snapshot reporting surface" --limit 8
```

Fresh-read SQL (executed against `groundtruth.db` at proposal-drafting time
to verify the divergence pattern is live):

```sql
-- total non-terminal current work items
SELECT COUNT(*) FROM current_work_items
WHERE resolution_status NOT IN ('resolved','retired','deferred','closed','superseded');

-- legacy LEGACY field: no project_name set
SELECT COUNT(*) FROM current_work_items
WHERE resolution_status NOT IN ('resolved','retired','deferred','closed','superseded')
  AND (project_name IS NULL OR project_name='');

-- canonical (loose): no active membership
SELECT COUNT(*) FROM current_work_items wi
WHERE wi.resolution_status NOT IN ('resolved','retired','deferred','closed','superseded')
  AND NOT EXISTS (SELECT 1 FROM current_project_work_item_memberships m
                  WHERE m.work_item_id=wi.id AND m.status='active');

-- canonical (strict): loose + only-retired
SELECT COUNT(*) FROM current_work_items wi
WHERE wi.resolution_status NOT IN ('resolved','retired','deferred','closed','superseded')
  AND NOT EXISTS (SELECT 1 FROM current_project_work_item_memberships m
                  JOIN current_projects p ON p.id=m.project_id
                  WHERE m.work_item_id=wi.id AND m.status='active' AND p.status='active');

-- dangling memberships
SELECT m.project_id, p.status AS proj_status, m.work_item_id, wi.resolution_status, wi.title
FROM current_project_work_item_memberships m
JOIN current_work_items wi ON wi.id=m.work_item_id
LEFT JOIN current_projects p ON p.id=m.project_id
WHERE m.status='active'
  AND wi.resolution_status NOT IN ('resolved','retired','deferred','closed','superseded')
  AND (p.id IS NULL OR p.status!='active')
ORDER BY m.project_id, m.work_item_id;
```

## Open Questions / Owner Action Required

None for this proposal. The AUQ approvals already on record cover the work
authorized here. The downstream per-artifact formal-artifact-approval
packets will collect their own owner acknowledgements at implementation time
per `GOV-ARTIFACT-APPROVAL-001`; that ceremony does not block this `GO`.

The two refinement questions raised at `-001` were both resolved by Loyal
Opposition at `-002` (recorded here for thread continuity):

1. `bridge_kind: governance_review` self-declaration — ACCEPTED by Loyal
   Opposition. The thread scopes formal governance artifact authoring,
   carries `target_paths`, includes `Requirement Sufficiency`, includes
   spec-derived verification, and leaves per-artifact formal approval packets
   as implementation-time gates.

2. Divergent counts framing — CONFIRMED CORRECT by Loyal Opposition. The
   proposal frames divergent counts as motivating evidence, not fixed
   acceptance criteria; downstream WI-3500/WI-3502/WI-3503 implementation
   threads re-read the canonical tables at implementation time instead of
   pinning proposal-time numbers.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
