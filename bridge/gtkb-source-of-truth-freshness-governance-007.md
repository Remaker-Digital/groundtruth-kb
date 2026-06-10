REVISED

bridge_kind: governance_advisory
Document: gtkb-source-of-truth-freshness-governance
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-31 UTC
Session: S376 (provisional)
Supersedes: -005 (GO at -006; impl-start gate heading-format mismatch); -003 (NO-GO at -004, FINDING-P1-002); -001 (NO-GO at -002, FINDING-P1-001)
Recommended commit type: feat

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-source-of-truth-freshness-governance-007
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style, 1M context

# Implementation Proposal (REVISED-3) — Source-of-Truth-Freshness Governance Formalization (WI-3501)

## Revision History / Findings Resolution

This REVISED-3 (`-007`) supersedes `-005` (which received GO at `-006`) to
resolve a Prime-discovered impl-start gate format mismatch. The proposal's
substantive scope, Specification Links, and acceptance shape are unchanged
from `-005`; the only material change is one section-heading wording.

- **Prime-discovered defect (post-GO; impl-start gate heading mismatch)** —
  RESOLVED. After GO at `-006`, `python scripts/implementation_authorization.py
  begin --bridge-id gtkb-source-of-truth-freshness-governance` returned
  `authorized: false` with `error: Approved proposal is missing a
  spec-derived verification plan`. The impl-start gate's `VERIFICATION_HEADING_TOKENS`
  matcher at `scripts/implementation_authorization.py:40-47` checks heading
  substrings, but the `-005` heading `## Spec-Derived Tests / Verification`
  contains none of the recognized tokens (the `Tests /` insertion breaks both
  `spec-derived verification` and `verification plan`). Codex's GO-time
  clause-preflight detector for
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`
  accepted the `-005` section as evidence; the impl-start gate's stricter
  heading-anchored matcher did not. This `-007` renames the section to `##
  Spec-Derived Verification Plan`, which contains BOTH the `spec-derived
  verification` AND `verification plan` recognized substrings, satisfying the
  impl-start gate while preserving the GO-time clause-preflight acceptance.
  No content change to the test table or any other section.

- **FINDING-P1-002** (`-004`; phantom `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`) —
  REMAINS RESOLVED from `-005`. Live `current_specifications` read confirms
  the phantom is absent; `GOV-SPEC-CAPTURE-TRANSPARENCY-001` is the live
  governing surface and is cited in Specification Links and mapped in T8.

- **FINDING-P1-001** (`-002`; post-impl version collision) — REMAINS RESOLVED
  from `-003`. The Implementation Plan step 5 below requires Prime Builder
  to compute the next monotonic bridge version from live `bridge/INDEX.md`
  at filing time, with no hardcoded version number.

Both non-blocking confirmations from Loyal Opposition (the `bridge_kind:
governance_review` exemption acceptance, and the divergent-counts framing as
motivating evidence not fixed acceptance criteria) remain in force; see
`## Open Questions`.

Related backlog capture (informational; not blocking this thread): the
impl-start gate vs clause-preflight heading-matcher divergence has been
captured as `WI-3507` in `PROJECT-GTKB-RELIABILITY-FIXES` for owner-gated
remediation; it is out of scope here.

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
require their own owner acknowledgement per `GOV-ARTIFACT-APPROVAL-001` and
must surface the FULL proposed artifact text per
`GOV-SPEC-CAPTURE-TRANSPARENCY-001`; those acknowledgements are inside the
implementation phase, not preconditions for this `GO`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` — formal approval gate; every artifact created here goes through its own approval packet.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — mechanical enforcement at insertion time.
- `PB-ARTIFACT-APPROVAL-001` — Prime Builder responsibility for the approval evidence trail.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` — gate scope and applicability.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — live governing spec (verified present in `current_specifications`, `status=specified`) for owner-visible specification capture and approval. Its APPROVE/REJECT-WITH-FULL-TEXT clause requires the owner to see the FULL proposed artifact text (not a summary, paraphrase, link, or hash) in each approval prompt, and the approve/reject decision to be captured in the approval packet's `approved_by` / `transcript_captured` fields. This is the live replacement for the phantom chat-derived citation flagged at `-004`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge index authority; this proposal lives in `bridge/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this very Specification Links section is required, must cite every relevant cross-cutting spec, and the proposed tests must derive from those specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — post-implementation verification must execute spec-derived tests.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness write-path enforcement applies to artifact insertions performed here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal self-declares `bridge_kind: governance_review` per the SKILL-sanctioned exemption set, because PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS has no PAUTH at filing time and this proposal scopes pure governance artifact authoring rather than source mutation. (Loyal Opposition accepted this exemption at `-002`, re-affirmed at `-004` and `-006`.)
- `GOV-08` (KB is truth) — direct precedent at type=governance, status=verified. The new GOV does NOT redefine it; it extends the principle from "all knowledge in KB" to "all reads of source-of-truth state are fresh reads of the canonical source, not of caches/snapshots/summaries."
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — architectural pattern precedent: a canonical read surface formalized as governance. The proposed DCL applies the same pattern to numeric reporting/state surfaces.
- `ADR-0001` (Three-Tier Memory Architecture) — defines MemBase as canonical truth, MEMORY.md as operational notepad (not canonical), Deliberation Archive as design-reasoning record. The fresh-read principle reinforces the tier separation: reading from MEMORY.md to claim canonical truth is exactly the violation pattern the new GOV/DCL formalize.
- `GOV-STANDING-BACKLOG-001` — work items cited here (WI-3500/3501/3502/3503, WI-3481) live in the canonical MemBase `work_items` authority; the proposal reads them through `current_work_items` and `current_project_work_item_memberships` rather than any markdown view.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — concrete owner decisions, requirements, and risks preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across artifacts, tests, and decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle transition vocabulary (candidate, specified, verified, retired) used by the proposed GOV/DCL.
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concepts must reach the glossary when first touched; the proposed GOV/DCL introduce "fresh-read invariant" and "declared-TTL cache" as new load-bearing terms requiring glossary promotion (sequenced as a downstream sibling, not blocking).

Non-governing reference (NOT a live spec; recorded for provenance, does not constrain this proposal):

- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — NOT present in `current_specifications` (fresh MemBase read at `-005` drafting time confirms absent). It is future-work tracked as `gtkb-chat-derived-spec-approval-impl` per `memory/work_list.md` and was previously NO-GO'd as a phantom citation in the AUQ-enforcement-stack slice-e requirements-collector thread (the live replacement identified there was `GOV-SPEC-CAPTURE-TRANSPARENCY-001`). It is listed here ONLY to document why earlier proposal versions referenced it; it is not a governing requirement for this work.

## Prior Deliberations

Relevant deliberations and prior decisions identified by direct DA search
and existing-spec audit (see `## Reproduction Commands` below for the exact
queries executed):

- `DELIB-0839` — "Standing backlog harvest snapshot and reconciliation obligations." Directly relevant: it inventoried bridge / MemBase / release-readiness sources and added standing-backlog reconciliation obligations. The fresh-read principle sharpens the same reconciliation discipline by requiring reads to derive from canonical tables, not cached harvest snapshots.
- `DELIB-1580` — "Loyal Opposition Verification — Backlog Work List Retirement Directive" (VERIFIED). Strongly relevant: it formalized retirement of `memory/work_list.md` so that MemBase `work_items` becomes the sole authority. The fresh-read principle is the steady-state rule that prevents the same regression class once a canonical authority is established.
- `DELIB-1469` — "GT-KB Self-Measurement and Self-Improvement Advisory." Relevant: defines benchmarks and metric snapshots as observation-only outputs that do not become canonical state. The proposed DCL preserves this separation (declared-TTL caches are permitted; un-declared cached state is forbidden).
- `DELIB-0018` — "INSIGHTS-2026-03-25-21-07 Project Progress Dashboard KPI Proposal." Relevant: dashboard KPIs over canonical state. The fresh-read principle constrains dashboard KPI derivation paths to canonical reads.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` — adjacent precedent: lifecycle independence is a runtime invariant, not file-relocation. The fresh-read principle is similarly a runtime invariant on read-path derivation, not a refactor.
- Existing-spec precedents: `GOV-08` (KB is truth; verified), `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (glossary IS canonical DA read surface), `GOV-SPEC-CAPTURE-TRANSPARENCY-001` (owner-visible capture/approval transparency), `GOV-ENV-LOCAL-AUTHORITY-001` (env source-of-truth), `ADR-ENV-SOT-TOPOLOGY-001` (env SoT topology). These together establish the pattern of formalizing read-path discipline as governance; the proposed GOV/DCL extend that pattern to reporting/state numeric surfaces.
- Negative precedent / driving incident: the live demonstration that motivated this proposal — `scripts/session_self_initialization.py`'s startup rollup banners 106 / 20 / 33 / 13 (depending on definition), and the LO handoff itself surfaced still-different counts vs. my fresh re-read (210 / 120 / 133 / 14-or-15). The divergence-of-snapshots-over-time pattern is the failure mode the GOV/DCL forbid. (Loyal Opposition confirmed at `-002`, `-004`, and `-006` that this divergence is correctly framed as motivating evidence, not fixed acceptance criteria.) The phantom-citation finding at `-004` and the impl-start heading-format mismatch discovered post-`-006` are both additional live instances of the same drift class — different surfaces, same failure mode.

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
- The rule-vs-MemBase drift remediation for the phantom
  `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` citation in the three narrative rule
  files (captured as `WI-3506`; out of scope here).
- The impl-start gate vs clause-preflight heading-matcher divergence
  remediation (captured as `WI-3507`; out of scope here).
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
   bridge thread + the owner AUQ evidence, and `approved_by=owner`. Per
   `GOV-SPEC-CAPTURE-TRANSPARENCY-001`, the owner approval prompt for each
   artifact surfaces the FULL proposed artifact text (not a summary, link, or
   hash).

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
   (`## Spec-Derived Verification Plan`), the commands executed, the observed
   results, and the recommended commit type (`feat`).

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

## Spec-Derived Verification Plan

Each test below derives directly from a Specification Link or from the
acceptance criteria of WI-3501. Tests are executed at implementation time
and reported in the post-impl report (filed at the next monotonic version
per Implementation Plan step 5). This section is the spec-to-test mapping
required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

| Test ID | Derives From | Procedure | Pass Criterion |
|---|---|---|---|
| T1 | `WI-3501.acceptance_summary` item 1; `DELIB` proposed-content | `python -m groundtruth_kb deliberations get <DELIB-ID>` after insertion | Row exists with `source_type='owner_conversation'`, `outcome='owner_decision'`, content includes the verbatim owner principle and the three-option AUQ structure. |
| T2 | `WI-3501.acceptance_summary` item 2; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` proposed body | read `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` via the spec read surface | Row exists with `type='governance'`, `status='specified'`, body includes Scope + Reporting Surfaces + Declared-TTL exception + Reconsideration trigger sections. |
| T3 | `WI-3501.acceptance_summary` item 3; `DCL-REPORTING-SURFACE-FRESH-READ-001` proposed body | read `DCL-REPORTING-SURFACE-FRESH-READ-001` via the spec read surface | Row exists with `type='design_constraint'`, `status='specified'`, `source_spec_id='GOV-SOURCE-OF-TRUTH-FRESHNESS-001'`, machine-checkable assertion is present. |
| T4 | `WI-3501.acceptance_summary` item 4; `GOV-STANDING-BACKLOG-001` linkage discipline | `python -m groundtruth_kb backlog show WI-3500 --json` (and `WI-3502`, `WI-3503`) | Each WI row records the new GOV ID in `source_spec_id` or `related_spec_ids_at_creation` and this bridge thread in `related_bridge_threads`. |
| T5 | `GOV-ARTIFACT-APPROVAL-001` packet evidence | Inspect `.groundtruth/formal-artifact-approvals/2026-05-30-*` JSON files | Three packets exist; each carries the required fields (`presented_to_user=true`, `transcript_captured=true`, content SHA-256 matches the inserted artifact, `changed_by` Prime Builder, `approved_by=owner`). |
| T6 | `GOV-08` non-regression | read `GOV-08` via the spec read surface | GOV-08 unchanged (still `verified`); no rewrite or supersede performed. |
| T7 | `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` non-regression | read `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` via the spec read surface | Unchanged; this proposal extends the pattern but does not modify the source. |
| T8 | `GOV-SPEC-CAPTURE-TRANSPARENCY-001` APPROVE/REJECT-WITH-FULL-TEXT clause | For each of the three approval packets, confirm the packet's `full_content` field holds the COMPLETE artifact text (not a summary, link, or hash), and that the owner approve decision is captured in `approved_by` + `transcript_captured`. Cross-check that the surfaced approval prompt content equals `full_content`. | Each packet's `full_content` is present and complete; `approved_by=owner`; `transcript_captured=true`; the surfaced prompt text matches `full_content` (no summary/hash substitution). |

Pre-file code-quality gates: no Python files are added or modified by this
proposal, so `ruff check` / `ruff format --check` do not apply. The
post-impl report will state this explicitly.

## Risks and Rollback

- Risk: DELIB content_hash collision if the helper is re-run. Mitigation: the
  insert path checks content_hash; duplicate inserts are no-ops.
- Risk: Provisional artifact IDs (`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
  `DCL-REPORTING-SURFACE-FRESH-READ-001`) already in use. Mitigation:
  pre-flight collision check at impl time (T6/T7 above + a direct
  `current_specifications` read for the two new IDs); rename if collision is
  found. (Fresh read at `-005` drafting confirmed neither ID is currently
  present; Codex re-confirmed at `-006`.)
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
foundation and the spec-linkage correction:

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

Spec-linkage verification (executed against `groundtruth.db` at `-005`
drafting time to confirm FINDING-P1-002's facts; Codex re-confirmed at `-006`):

```sql
-- phantom: expected NOT FOUND
SELECT id, type, status FROM current_specifications WHERE id='GOV-CHAT-DERIVED-SPEC-APPROVAL-001';
-- live replacement: expected present, governance, specified
SELECT id, type, status, title FROM current_specifications WHERE id='GOV-SPEC-CAPTURE-TRANSPARENCY-001';
-- the two proposed new IDs: expected NOT FOUND (no collision)
SELECT id FROM current_specifications WHERE id IN ('GOV-SOURCE-OF-TRUTH-FRESHNESS-001','DCL-REPORTING-SURFACE-FRESH-READ-001');
```

Fresh-read SQL (executed at proposal-drafting time to verify the divergence
pattern is live):

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
per `GOV-ARTIFACT-APPROVAL-001` + `GOV-SPEC-CAPTURE-TRANSPARENCY-001`; that
ceremony does not block this `GO`.

The two refinement questions raised at `-001` were both resolved by Loyal
Opposition at `-002`/`-004`/`-006` (recorded here for thread continuity):

1. `bridge_kind: governance_review` self-declaration — ACCEPTED and
   re-affirmed by Loyal Opposition across three reviews.

2. Divergent counts framing — CONFIRMED CORRECT by Loyal Opposition.

Related backlog captures (informational; not blocking this thread):

- `WI-3506` — rule-vs-MemBase phantom-spec-citation drift (3 narrative rule
  files cite the non-existent `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`). Owner
  AUQ S376 selected re-point to `GOV-SPEC-CAPTURE-TRANSPARENCY-001`;
  remediation routes through its own future bridge thread + approval packets.
- `WI-3507` — impl-start gate vs clause-preflight heading-matcher token-set
  divergence (the defect that motivated this REVISED-3). Routes through the
  reliability fast-lane in a future thread.

## Copyright

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
