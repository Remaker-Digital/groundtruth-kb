NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker under manual dispatch from leader session bb6ca43c (DELIB-202667523/531/533 fan-out); resolved role prime-builder for this dispatched drafting task

bridge_kind: prime_proposal
Document: gtkb-wi5768-kb-mutation-declaration-preflight
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5768

target_paths: ["scripts/kb_mutation_declaration_preflight.py", "scripts/gtkb_propose_scaffold.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", ".claude/rules/file-bridge-protocol.md", ".claude/skills/gtkb-verify/SKILL.md", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_kb_mutation_declaration_preflight.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

# WI-5768 — Define `kb_mutation_in_scope` Semantics and Add the Declaration-vs-Writes Semantic Preflight

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write. The proposed preflight and every investigation read behind this filing open the database strictly read-only (`file:...?mode=ro`); the irony of this thread's subject is not lost on its author, so the declaration below the header is made under the exact draft semantics this proposal defines.

This filing performs no approval-evidence work; protected narrative-artifact edits listed for implementation require their own per-artifact approval packets at that time.

The `.groundtruth/formal-artifact-approvals/**` envelope appears in target_paths declaratively because the implementation phase must generate per-artifact approval packets for the two protected-surface edits (Slice C); this filing itself creates or edits nothing under that envelope, and reviewers should treat the entry as scope declaration, not authorization exercised.

New files declared new: `scripts/kb_mutation_declaration_preflight.py` and `platform_tests/scripts/test_kb_mutation_declaration_preflight.py` do not exist at the current commit (path-checked this session); every other target exists.

## Problem

`kb_mutation_in_scope` is a machine-readable header field on bridge proposals that downstream reviewers use to size a proposal's scope. Today it is self-attested, boundary-undefined, and unchecked:

1. **Emitted by two surfaces, parsed by zero.** A repo-wide search this session found exactly two live emitters, both hardcoding `false` unconditionally: the governed auto-draft template in `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:1185` and the propose scaffold in `scripts/gtkb_propose_scaffold.py:190`. No hook, preflight, skill helper, or test reads the field anywhere (`.claude/hooks`, `scripts/`, `groundtruth-kb/src`, `platform_tests/` all negative except those two emitters).

2. **The existing gate layer is text-heuristic, not semantic.** The bridge-compliance gate's KB-mutation checkpoint (`.claude/hooks/bridge-compliance-gate.py` — `KB_MUTATION_DECLARATION_RE` / `KB_MUTATION_NEGATION_RE` at `:425-442`, `_declares_kb_mutation` at `:974-978`, `_kb_mutation_target_paths_ask_reason` at `:981-998`; cited strictly read-only, no gate edit in this proposal) fires at Write time on PROSE: when body text declares mutation work it asks that `groundtruth.db` appear in target_paths. It never parses the `kb_mutation_in_scope` header (the bare header line matches neither regex), and it never reads live MemBase. A proposal can declare `false` while its session writes MemBase and pass every mechanical gate.

3. **The failure is real, directional, and reviewer-invisible.** Source advisory `bridge/gtkb-lo-kb-mutation-declaration-integrity-advisory-001.md` documents two independent threads from one session (2026-07-28): WI-5659 (`...-v2-005.md` declared `false`; live state showed WI v6/v7 writes, v7 postdating a GO that scoped "no KB mutation"; thread reached VERIFIED at `-006` unexamined) and WI-5657 (`...-v2-003.md` declared `false` at :29; live state showed WI v4 whose `change_reason` names the very revision declaring no mutation, plus a same-window deliberations insert). Both preflights passed cleanly on both threads; two independent reviewers missed both instances. Verifying costs one command that nothing in the review path asks for.

4. **The boundary is undefined.** The likely-benign explanation is that work-item `status_detail` refreshes are treated as routine bookkeeping rather than "KB mutation." Two threads and two reviewers have now read the field the other way. Per the advisory, this is a semantics question the owner must settle; until then authors and reviewers cannot apply the same reading.

## Recorded Attribution-Feasibility Findings (read-only schema evidence)

Per the advisory's "make it checkable" recommendation, the mechanical check needs session-attributable version deltas. Live schema inspection this session (`sqlite3`, `mode=ro`) establishes what attribution is actually possible today:

- **`work_items`**: carries `changed_by` (role/harness string, e.g. `prime-builder/codex`), `changed_at`, `change_reason` — **no session column**. Exact session attribution is impossible from the row alone.
- **`specifications`**: same shape — `changed_by`/`changed_at`/`change_reason`, no session column.
- **`deliberations`**: HAS a `session_id` column, but population is sparse: of the most recent 200 rows, 32 carry UUID-shaped session ids, 168 are NULL, and historical values include free-text labels (`S324`, `interactive-...`). Exact attribution is possible only when populated.
- **`work_intent_claims`**: a durable MemBase table (`UNIQUE(thread_slug)`, latest-claim semantics) recording `thread_slug`, `session_id`, `acquired_at`, `acting_role`. This gives every claimed thread a durable window-start anchor and a drafting-session id.
- **Bridge chain**: each version file carries `author_session_context_id` under GOV-DOCUMENT-AUTHOR-PROVENANCE-001 — the thread's session-anchor set is recoverable from the chain itself.

**Conclusion (stated per the advisory's phasing recommendation):** exact per-session attribution today exists for (a) deliberations rows whose `session_id` matches a thread anchor, and (b) work_items/specifications version rows whose `change_reason` textually cites the thread slug or its numbered files — the deterministic linkage both advisory instances exhibited. Everything else is heuristic (changed_by-family + time-window) or unavailable. A blocking check pretending otherwise would be dishonest; the design below therefore tiers its evidence and degrades to warn-with-reason, and full promotion is explicitly gated on the WI-5730-family session-authority metadata binding.

## Recorded Operation-Time Evaluation (this proposal's own cohort)

Direct read-only invocation of the canonical evaluator (`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`; live `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` **v3** row — the SF-1-repaired active reissue of 2026-07-30T03:48:58Z under unchanged owner decision DELIB-202667533 AT-04; envelope hash `B5642FC6DC897BF642E7B530F50A447EF44EFFF8E247A8CB033458507946FD01`; evaluator v1 sha256 `2FEEEAB2...`; taxonomy v1 sha256 `7E7D8594...`; decision time 2026-07-30T05:29Z) over this proposal's declared target_paths plus this bridge file:

- **Classification** (`classify_target`): the three `scripts/`+`groundtruth-kb/src` targets classify `source`; the three `platform_tests/` targets classify `test`; this bridge file classifies `bridge`; **`.claude/rules/file-bridge-protocol.md` and `.claude/skills/gtkb-verify/SKILL.md` classify `configuration`; `.groundtruth/formal-artifact-approvals/**` classifies `metadata`**.
- **Full cohort** (all four operations `implementation_packet_create` / `implementation_start` / `protected_mutation` / `git_commit`): `allowed=false, reason_code=target_mutation_class_not_allowed` — the program PAUTH v3 allows `source`/`test_addition`/`governance_evidence`/`bridge` only, so the two protected surfaces and the packet envelope sit outside its class set. This is the same SF-2 class WI-5760's filing recorded; the remedy is routed to OD-C below, not decided here.
- **Core cohort** (source + test + bridge only): `allowed=true, reason_code=allowed` on all four operations. Slices A, B, and D are green under the program PAUTH as issued.

## Proposed Change

Four slices, independently revertible. Slice C is additionally gated on per-artifact approval packets and OD-C.

### Slice A — Field semantics definition (drafted here, flagged for Loyal Opposition review)

The following normative text is proposed for the protocol and template surfaces. **It adopts the broad reading. LO is explicitly asked to review the boundary before GO (Verification Question 1), and OD-A reserves owner ratification before the protocol text lands.**

> **`kb_mutation_in_scope` (draft normative definition D-1).** The field declares the mutation scope of the BRIDGE THREAD'S WORK PRODUCT — from work-intent claim acquisition through terminal status — not merely of the filing act.
>
> Declare `true` when the thread's authorized work includes (or is expected to include) at least one MemBase write: an insert or new-version row in a governed MemBase table — canonically `work_items`, `specifications` (all subtypes), or `deliberations` — that is attributable to the thread: performed by the thread's authoring/implementing session(s), or performed as the thread's declared work product through a governed CLI. Work-item `status_detail` and progress-metadata refreshes ARE in scope: they create version rows (the WI-5657 v4 and WI-5659 v6/v7 incident writes are exactly this class). Declare `false` only when the thread's work performs no such write.
>
> Out of scope (must not force `true`): governed side-records created by platform plumbing rather than by the thread's work product — `work_intent_claims` rows written by the claim CLI, `assertion_runs` telemetry, `session_prompts` handoff records, runtime state under `.gtkb-state/` (not MemBase), and MemBase writes by unrelated concurrent sessions that are not the thread's work product (e.g., a Loyal Opposition triage refresh of the same work item).
>
> Boundary cases E1/E2, flagged for ratification (OD-A): E1 — owner-decision deliberations captured mid-thread by the thread's own session are drafted IN scope when they record decisions about the thread's work. E2 — backlog stage transitions executed by post-terminal completion automation (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001) are drafted OUT of scope for the declaring thread.

Where the definition lands:

- `.claude/rules/file-bridge-protocol.md` — a new short subsection under the implementation-start metadata section stating D-1 (protected; per-artifact packet + OD-A + OD-C gated).
- `scripts/gtkb_propose_scaffold.py` (`:190` region) — the scaffold stops emitting a bare hardcoded `kb_mutation_in_scope: false` and instead emits the field with an adjacent one-line semantics anchor instructing the author to set it truthfully per D-1 (scaffold bodies are TODO-drafts, so guidance text is native to the surface).
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` (`:1185` region) — the governed auto-draft template's hardcoded `false` gains the same one-line semantics anchor; the auto-draft path composes proposals whose work product is bounded and currently mutation-free, so `false` remains the emitted default, now with its meaning stated instead of implied.

### Slice B — Semantic preflight: `scripts/kb_mutation_declaration_preflight.py` (new)

A deterministic, read-only CLI mirroring the invocation grammar of the two existing preflights:

```
python scripts/kb_mutation_declaration_preflight.py --bridge-id <slug> [--content-file <path>] [--json]
```

Behavior:

- **Inputs.** Resolves the operative file from the numbered bridge chain (same operative-file discipline as `scripts/bridge_applicability_preflight.py`; `--content-file` supports pre-filing self-check). Parses the declared `kb_mutation_in_scope` value (true/false/absent), the `Work Item:` metadata line(s), and the chain's `author_session_context_id` headers. Reads the thread's `work_intent_claims` row (read-only) for `session_id` and `acquired_at`.
- **Window.** `[claim acquired_at — falling back to the earliest version's Date header when no claim row exists — through evaluation time]`. Deltas before the window are concurrent history, not thread work.
- **Read-only MemBase comparison** (`mode=ro` URI open, enforced in code and asserted by test): version rows in `work_items` for the cited WI(s), `deliberations` rows, and `specifications` rows changed within the window.
- **Evidence tiers per delta:**
  - `EXACT` — a deliberations row whose `session_id` matches the thread anchor set, or a work_items/specifications row whose `change_reason` cites the thread slug or a `bridge/<slug>-NNN.md` name.
  - `HEURISTIC` — a delta on a cited WI (or a specifications delta) within the window whose `changed_by` role/harness family matches a thread author identity, without slug citation or session binding.
  - `UNATTRIBUTABLE` — deltas in the window with no session, citation, or actor linkage (e.g., `changed_by = gt-cli`), or required inputs missing (no claim row and no author metadata).
- **Decision contract** (exit codes aligned with the clause-preflight convention):
  - declared `false` + any `EXACT` delta → **exit 5, FAIL** (blocking; the advisory's two instances both carried EXACT-tier evidence).
  - declared `false` + `HEURISTIC`-only deltas → **exit 3, WARN**, flagged with the delta table.
  - declared `false` + `UNATTRIBUTABLE`-only deltas, or attribution inputs unavailable → **exit 3, WARN with explicit reason** (`attribution-unavailable: <why>`); never a silent pass, never a false FAIL.
  - declared `true` → **exit 0** (target_paths/`groundtruth.db` coherence remains the text layer's job).
  - field absent → **exit 3, WARN** with a legacy-thread reason (pre-definition threads are grandfathered, not failed).
  - no in-window deltas → **exit 0**.
  - unreadable inputs / tooling failure → distinct non-zero exit, fail closed, never `allowed`-shaped output on error.
- **Output.** A citable `## KB Mutation Declaration Check` markdown section (and `--json`): declared value, window bounds and anchor set, per-delta rows (table, id, version, `changed_at`, `changed_by`, `change_reason` excerpt, evidence tier), decision, and a fixed schema-capability note recording that work_items/specifications carry no session column today — so verdicts citing the section also record the check's honest limits.

**Composition boundary (explicit).** The bridge-compliance gate checkpoint proven in the WI-5760 filing cycle (`KB_MUTATION_DECLARATION_RE`/`KB_MUTATION_NEGATION_RE` and `_kb_mutation_target_paths_ask_reason`) is the **write-time TEXT-heuristic layer**: prose in, target_paths coherence out; it never reads the header field or the database. This preflight is the **review/verdict-time SEMANTIC layer**: header field in, live MemBase version deltas out. They compose as the two layers GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 requires and share no code path; the gate hook is cited read-only and is not modified by this proposal.

**Phasing (gated, per the advisory's interim recommendation).** Phase A (this thread) ships D-1 semantics, the preflight with FAIL reserved to EXACT evidence, and the reviewer-path step (Slice C). Phase B — after the WI-5730-family binding lands bridge author metadata to exact session authority (and/or MemBase writes gain session attribution) — re-ratifies severity: HEURISTIC promotes toward EXACT and the blocking surface may widen (OD-D). If the WI-5730 family stalls, Phase A remains fully operative: template semantics + verdict-time live read were the advisory's standalone interim recommendation.

### Slice C — Reviewer-path wiring (protected; packet- and OD-C-gated)

- `.claude/rules/file-bridge-protocol.md` — D-1 subsection per Slice A.
- `.claude/skills/gtkb-verify/SKILL.md` — one new mandatory pre-write step in § Mandatory pre-write steps (after the two existing preflight steps): run `python scripts/kb_mutation_declaration_preflight.py --bridge-id <slug>`, include the emitted section in the verdict, and treat exit 5 without a documented owner waiver as NO-GO-not-VERIFIED; plus the matching bullet in § Gate enforcement. Until the tool lands, the step's manual equivalent is the advisory's one-command live read (`gt backlog show <WI> --json`) — the wording covers both so the prompt is useful from day one.
- **Sequencing note.** WI-5760 (GO at `-002`) also adds a mandatory pre-write step to the same SKILL section (PAUTH cohort evaluation). The two steps are independent and compose textually; whichever implementation lands second rebases the section. No shared code.

### Slice D — Tests

New `platform_tests/scripts/test_kb_mutation_declaration_preflight.py`; additive cases in `platform_tests/scripts/test_gtkb_propose_scaffold.py` and `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` for the template-surface text. All fixture-rooted (fixture SQLite DB carrying the four relevant tables, fixture bridge dir); no live MemBase read or write in tests. Plan below.

## Cross-Harness Disposition

**Protected surfaces (per-artifact approval packets required).** `.claude/rules/file-bridge-protocol.md` (protected narrative artifact) and `.claude/skills/gtkb-verify/SKILL.md` (managed canonical skill) each require their own formal-artifact approval packet at implementation time under GOV-ARTIFACT-APPROVAL-001 / DCL-ARTIFACT-APPROVAL-HOOK-001, presented to the owner with full content. target_paths inclusion authorizes mechanical write scope only and does not substitute for those packets. The recorded evaluation above additionally shows both paths (class `configuration`) and the packet envelope (class `metadata`) sit outside the program PAUTH's class set — Slice C implementation start is therefore doubly gated: packets AND the OD-C authorization remedy.

**Cross-harness parity.** The preflight is a harness-agnostic Python CLI per ADR-CROSS-HARNESS-PARITY-001 — every reviewer harness invokes it exactly as it invokes the two existing preflights. The SKILL edit follows the managed-skill lifecycle: edit the canonical file, regenerate the Codex adapter via `python scripts/generate_codex_skill_adapters.py --update-registry`; adapters are not edited directly (DCL-CROSS-HARNESS-ENFORCEMENT-001). No hook is modified.

## Specification Links

- GOV-08 — the Knowledge Database is the single source of truth: `kb_mutation_in_scope` is a state claim about MemBase, and MemBase — not the claim — is the authority it must be checked against (mandatory anchor for this thread).
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — state claims derive from fresh canonical reads; a self-attested declaration trusted without a live read is precisely the defect class, and the preflight is the fresh-read mechanism.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail integrity; declarations that parse but lie degrade what this specification protects (mandatory anchor).
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — two-layer defense in depth; the write-time text layer exists, and this proposal adds the review-time semantic layer.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — the preflight-surface discipline (operative-file resolution, citable emitted section) the new tool adopts.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the terminal verification gate the Slice-C reviewer step extends.
- GOV-DOCUMENT-AUTHOR-PROVENANCE-001 — the author-provenance contract supplying `author_session_context_id`, the anchor set the semantic comparison consumes.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — project-scoped authorization contract cited by this proposal's metadata and recorded evaluation.
- GOV-ARTIFACT-APPROVAL-001 — per-artifact approval packets for the two protected Slice-C edits.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the mechanical gate enforcing those packets at write time.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — machine-readable declarations are durable governance surfaces only when their meaning is defined and checkable; this thread restores that property.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — append-only bridge chain preserved; the preflight reads the numbered chain and rewrites nothing.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory capture preceded this derived proposal; boundary questions route to owner decisions, not ad-hoc reinterpretation.
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 — the declaration check is deterministic service work, moved out of reviewer memory into a command.
- SPEC-1830 — operational procedures must be code, not conversation; "read the live work item before trusting the claim" becomes a tool.
- GOV-STANDING-BACKLOG-001 — WI-5768 is the MemBase backlog authority for this work.
- GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 — the source advisory is adapt-class; open decisions are routed to AUQ below, not silently decided.
- DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 — the mechanical contract for that gate; the OD register implements its evidence-routing clause.
- GOV-10 — tests exercise the exposed production interface (the new CLI and the template emitters), not internals.
- GOV-12 — work item creation triggers test creation (Slice D files).
- SPEC-1662 (GOV-18) — assertions are behavioral (decisions, tiers, exit codes, delta tables), not shape-only.
- GOV-15 — no autonomous test fixes; regression failures route to owner-gated work items.
- GOV-17 — automation-script modification gate: `scripts/` changes ride this reviewed proposal.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — canonical-skill edit with adapter regeneration.
- ADR-CROSS-HARNESS-PARITY-001 — harness-agnostic CLI surface over any harness-local helper.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is an in-root platform surface; the tool writes nothing outside stdout/`--json`.

## Prior Deliberations

Deliberation search performed 2026-07-29 (`gt deliberations search "kb mutation declaration integrity" --limit 5`): DELIB-202667208, DELIB-20261671, DELIB-FAB15-REMEDIATION-20260610, DELIB-202666099, DELIB-202667169 — generic verdict/remediation records adjacent at best; no controlling precedent for a declaration-vs-writes check. Targeted-id reads and authorities:

- DELIB-202667531 — owner triage directive: fix-class advisories become authorized corrective work items; owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729; bridge protocol explicitly NOT waived per item.
- DELIB-202667533 (AT-04) — the program PAUTH this proposal cites; verified active at v3 this session (SF-1 token repair reissued 2026-07-30T03:48:58Z under the unchanged owner decision).
- DELIB-202667534 — advisory corpus disposition table; row 17 routes `gtkb-lo-kb-mutation-declaration-integrity` to WI-5768 (order 210) and fixes the coarse direction this proposal implements (define semantics + deterministic declaration-vs-writes preflight).
- Source advisory: `bridge/gtkb-lo-kb-mutation-declaration-integrity-advisory-001.md` (classification `adapt`; keep the field, define and check it). Per-thread instance record: `bridge/gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory-002.md`.
- Sibling scope boundaries: **WI-5760** (`bridge/gtkb-wi5760-pauth-preflight-visibility-001.md`, GO at `-002`) adds the PAUTH cohort preflight and touches the same gtkb-verify SKILL section — different dimension (authorization visibility vs declaration integrity); steps compose, second-lander rebases; its OD-E and this thread's OD-C describe the same protected-surface remedy class and may be satisfied by one combined owner decision. **WI-5771** owns the per-thread WI-5659 corrections (citation referent + truthful redeclaration on that chain); WI-5768 is the pattern-level mechanism; file sets do not overlap. **WI-5730 family** binds bridge author metadata to exact session authority; WI-5768 CONSUMES that binding as its Phase-B promotion gate and does not implement it. The WI-5657 `-005` truthful-redeclaration item remains inside that thread's own authority per the advisory (rec 4) and is not scoped here.

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001. WI-5768 is one of those corrective items (P2, defect, `maintenance_tool`, order 210).
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH `PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` — verified active this session at v3 (classes source, test_addition, governance_evidence, bridge; SF-1 forbidden-token repair reissued 2026-07-30 under the same decision).
- **DELIB-202667534** (owner decision, 2026-07-29): disposition-table row 17 consolidating the source advisory into WI-5768 and fixing the coarse direction (define the field; make it checkable); this proposal implements that direction and reserves the residual forks below.

Open decisions — REMAIN OPEN, flagged for implementation-time owner grilling via AskUserQuestion per GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001; this proposal does NOT silently decide them. A slice touching an open decision does not implement until its AUQ evidence exists and is recorded in the implementation report's Owner Decisions / Input section:

- **OD-A (field semantics ratification — the advisory's one owner question).** D-1 adopts the broad reading (`status_detail`/progress-metadata writes count) with E1 IN / E2 OUT as drafted boundary cases. LO reviews the draft at GO time; the owner ratifies (or narrows) via AUQ before the protocol-rule text lands. The narrow reading (substantive artifact mutation only) is the recorded alternative; adopting it inverts the two incident instances from violations into compliant declarations, which is why this proposal recommends against it.
- **OD-B (Phase-A enforcement placement and severity).** Recommended default: mandatory at verification review via the Slice-C SKILL step, exit 5 reserved to EXACT evidence, exit 3 flagged tiers advisory. Alternatives: report-only until Phase B, or additional GO-review placement. No filing-time hook enforcement is proposed in any variant.
- **OD-C (protected-surface authorization remedy; shared class with WI-5760 OD-E).** The recorded evaluation shows the two `configuration` targets and the `metadata` envelope outside the program PAUTH's classes. Remedy options: a narrow supplemental WI-5768 PAUTH on the DELIB-202667529 exact-scope pattern, a program-PAUTH amendment, or one combined supplemental PAUTH covering the WI-5760 + WI-5768 protected slices together. MemBase `project_authorizations` mutation requiring owner approval; not performed by this filing.
- **OD-D (Phase-B promotion policy).** Once the WI-5730-family session-authority binding lands, whether HEURISTIC-tier evidence escalates to blocking and whether the check extends beyond the cited-WI/deliberations core (e.g., all specifications deltas). Explicitly deferred; sized by Phase-A WARN telemetry.

## Requirement Sufficiency

Existing requirements sufficient. GOV-08 and GOV-SOURCE-OF-TRUTH-FRESHNESS-001 already make MemBase the authority state claims are checked against; GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 already requires the two-layer mechanical shape; GOV-DOCUMENT-AUTHOR-PROVENANCE-001 already supplies the anchor metadata. D-1 is protocol documentation of an existing field's meaning, ratified through OD-A owner-decision evidence — an output of this work executed through its own approval path, not a new specification precondition. No new or revised requirement is required before implementation.

## Spec-Derived Test Plan

New `platform_tests/scripts/test_kb_mutation_declaration_preflight.py` (fixture SQLite DB with `work_items`, `specifications`, `deliberations`, `work_intent_claims`; fixture bridge dir; no live MemBase access):

1. `test_false_declaration_with_slug_cited_wi_delta_fails` — cited WI gains a version row in-window whose `change_reason` names the thread slug; declaration `false` → exit 5, emitted section names the delta row and tier EXACT. Reproduces the WI-5657 incident shape. Derives from GOV-08, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, SPEC-1662.
2. `test_false_declaration_with_session_bound_deliberation_fails` — deliberations row with `session_id` equal to a chain `author_session_context_id`; declaration `false` → exit 5. Derives from GOV-08, GOV-DOCUMENT-AUTHOR-PROVENANCE-001.
3. `test_true_declaration_passes` — identical fixture writes with declaration `true` → exit 0. Derives from GOV-10 (the task's required true-declaration case).
4. `test_heuristic_only_attribution_warns` — in-window WI delta, `changed_by` matching the author family, no slug citation, no session binding → exit 3, tier HEURISTIC, flagged table. Derives from SPEC-1662.
5. `test_attribution_unavailable_warns_with_reason` — in-window delta with generic `changed_by` (`gt-cli`), no claim row, no session ids → exit 3 with explicit `attribution-unavailable` reason; never exit 0, never exit 5. The task-required degradation case. Derives from GOV-SOURCE-OF-TRUTH-FRESHNESS-001, SPEC-1662.
6. `test_absent_declaration_warns_legacy` — operative file lacks the field → exit 3 with legacy reason (grandfathering, not failure).
7. `test_clean_thread_declaration_false_passes` — no in-window deltas → exit 0.
8. `test_window_excludes_pre_claim_history` — delta timestamped before `work_intent_claims.acquired_at` is excluded from the comparison. Derives from GOV-08 (concurrent history is not thread work).
9. `test_read_only_and_idempotent` — fixture DB bytes identical before/after two runs; second run's decision identical. Derives from GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, SPEC-1830.
10. `test_tooling_failure_fails_closed` — unreadable DB path → distinct non-zero exit, no PASS-shaped output. Derives from GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.

Template-surface additions:

11. Additive case in `platform_tests/scripts/test_gtkb_propose_scaffold.py` — scaffold output carries the semantics-anchored field text (not a bare hardcoded line). Derives from GOV-12, GOV-10.
12. Additive case in `platform_tests/groundtruth_kb/test_cli_bridge_propose.py` — the governed auto-draft template emits the anchored field text. Derives from GOV-12, GOV-10.

Execution: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_kb_mutation_declaration_preflight.py platform_tests/scripts/test_gtkb_propose_scaffold.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py -v`, plus `ruff check` and `ruff format --check` on all changed Python files.

## Acceptance Criteria

1. D-1 semantics are stated normatively on the surfaces authors and reviewers actually read (protocol rule post-packet; both template emitters), with the broad-reading boundary, E1/E2 cases, and out-of-scope classes explicit.
2. One documented command compares a thread's declaration against live MemBase and emits a citable section; the WI-5657/WI-5659 incident class reproduces on fixtures as exit 5 with the delta table named.
3. The exit-code contract holds: 0 pass; 3 flagged/warn always carrying a reason (HEURISTIC or attribution-unavailable or legacy-absent); 5 only on EXACT-tier contradiction; distinct non-zero fail-closed on tooling failure.
4. The emitted section records the schema-capability limits (no session column on work_items/specifications today), and Phase-B promotion is documented as gated on the WI-5730-family binding.
5. The gtkb-verify SKILL carries the verdict-time step (post-packet; Codex adapter regenerated), composed with WI-5760's step without conflict; the bridge-compliance gate hook is untouched.
6. All new and additive tests pass; ruff lint and format gates clean on changed files.

## Risk and Rollback

Risk: LOW-MEDIUM. Slices A/B/D are additive template text, one new read-only CLI, and tests — no existing gate's behavior changes, no hook edits, no dispatcher/TAFE surfaces touched, no MemBase schema or row mutation anywhere in scope. Slice C is a text addition to two protected surfaces behind per-artifact packets and the OD-C remedy; until it lands, Slices A/B already give reviewers the command and the definition. Honest failure modes are recorded openly: attribution is structurally limited today (schema findings above), so the tool tiers evidence and can only WARN where certainty is impossible — the residual risk is WARN fatigue on busy work items, mitigated by reasons on every WARN and sized for OD-D by Phase-A telemetry. Rollback: each slice reverts independently by commit; the new files delete cleanly; template and protected-surface text reverts textually with no runtime coupling.

Recommended commit type: feat

## Verification Questions for Loyal Opposition

1. Is the D-1 boundary correct — specifically the broad reading, E1 IN, E2 OUT — or should any class move before this text is put to the owner under OD-A?
2. Is the three-tier evidence model (EXACT / HEURISTIC / UNATTRIBUTABLE with exit 5 reserved to EXACT) the honest ceiling given the recorded schema findings, or is there a deterministic linkage class this proposal missed?
3. Should OD-C be resolved jointly with WI-5760's OD-E as one combined supplemental PAUTH covering both threads' protected slices, or per-thread?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
