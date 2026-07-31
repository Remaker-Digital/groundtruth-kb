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
Document: gtkb-wi5760-pauth-preflight-visibility
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5760

target_paths: ["scripts/pauth_cohort_preflight.py", "scripts/pauth_finalization_exposure_sweep.py", "scripts/bridge_applicability_preflight.py", "scripts/implementation_authorization.py", ".claude/skills/gtkb-verify/SKILL.md", ".claude/rules/codex-review-gate.md", ".groundtruth/formal-artifact-approvals/**", "platform_tests/scripts/test_pauth_cohort_preflight.py", "platform_tests/scripts/test_pauth_finalization_exposure_sweep.py", "platform_tests/scripts/test_implementation_authorization.py"]

# WI-5760 — Surface PAUTH Operation-Time Mutation-Class Evaluation in Preflights and the Pre-VERIFIED Gate

Scope confirmation: this proposal performs no MemBase mutation and no groundtruth.db write.

This filing performs no approval-evidence work; protected narrative-artifact edits listed for implementation require their own per-artifact approval packets at that time.

The `.groundtruth/formal-artifact-approvals/**` envelope appears in
target_paths declaratively because the implementation phase must generate
per-artifact approval packets for the two protected-surface edits (Slice B);
this filing itself creates or edits nothing under that envelope, and reviewers
should treat the entry as scope declaration, not authorization exercised.

## Problem

No step in the documented review or verification workflow evaluates whether
the work a reviewer is approving is PAUTH-authorized at operation time. The
canonical evaluator exists and is deterministic
(`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`,
with `classify_target` and the permanent taxonomy at
`config/governance/project-authorization-operation-taxonomy.toml`), but the
platform runs it only inside
`scripts/implementation_authorization.py` (`_evaluate_project_authorization_operations`,
`scripts/implementation_authorization.py:996`, raising at `:1015`) — i.e.
AFTER `GO`, at implementation start, and again inside the terminal
finalization path. Neither mandatory preflight
(`scripts/bridge_applicability_preflight.py`,
`scripts/adr_dcl_clause_preflight.py`) consults `project_authorizations` at
all.

Two source advisories establish the defect class with direct evidence:

1. **Review-time gap on proposals**
   (`bridge/gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory-001.md`,
   D1/D2/D3/D4): four of five threads in one Loyal Opposition queue pass
   returned `allowed=False, reason_code=target_mutation_class_not_allowed`
   from direct evaluator invocation while both mandatory preflights returned
   clean; two `GO`s were issued on proposals that could never reach
   implementation start.
2. **Verification-time gap on the terminal transaction**
   (`...-advisory-002.md`, D6/D7/D8): `VERIFIED` is not a file-only status —
   per `.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED
   Commit-Finalization Gate it atomically commits the verified implementation
   paths PLUS the thread's bridge chain
   (`.claude/skills/gtkb-verify/helpers/write_verdict.py:446
   _assert_predecessor_chain_committed`, enforced at `:1145`). That commit's
   target set includes `bridge/<slug>-NNN.md` files (mutation class
   `bridge`). The eight-step verification checklist in
   `.claude/rules/codex-review-gate.md:117` ("If Loyal Opposition is verifying
   an implementation") and the eleven mandatory pre-write steps in
   `.claude/skills/gtkb-verify/SKILL.md` (§ Mandatory pre-write steps) never
   ask whether that projected finalization commit cohort is authorized. A
   reviewer executing every documented gate correctly still drafted a full,
   evidence-rich, WRONG `VERIFIED` on WI-5665 — the blocker sat in a dimension
   the workflow never surfaces.

**Live reproduction — the WI-5741 chain.** The exact blocking class this
proposal targets played out end-to-end on
`gtkb-wi5741-spec-packet-postimage-completeness`:

- The v005 implementation report was technically green (62 passed, ruff
  clean, both preflights clean, all acceptance criteria met).
- Codex A's terminal review at
  `bridge/gtkb-wi5741-spec-packet-postimage-completeness-006.md` (`NO-GO`,
  2026-07-29) ran the canonical operation-time evaluation directly and found
  the standing fast-lane PAUTH
  (`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, classes
  `source`/`test_addition`/`hook_upgrade`, no `bridge`) denies the atomic
  terminal transaction: `git_commit` over the seven implementation targets
  plus bridge versions 001-006 returned `allowed=false,
  reason_code=target_mutation_class_not_allowed` naming all six numbered
  bridge paths.
- The remedy required a fresh owner decision (`DELIB-202667529`) minting the
  narrow exact-scope
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5741-TERMINAL-RECOVERY-20260729`
  (active; classes `source`/`test_addition`/`bridge`/`governance_evidence`;
  `included_work_item_ids=["WI-5741"]`) before the thread could legally
  finalize.

That -006 review caught the collision only because the reviewer ran the
evaluator by hand, outside any documented step. WI-5760 makes that evaluation
a mandatory, mechanical, citable review surface so the WI-5741 `-006`
blocking class (`target_mutation_class_not_allowed`) surfaces at review time
— before `GO`, and before a reviewer drafts a terminal verdict — instead of
at finalization time.

## Recorded Operation-Time Evaluation (this proposal's own cohort)

Per advisory-001 D4 (proposals must RECORD the evaluation, not predict it),
this filing eats its own dogfood. Direct invocation of
`evaluate_envelope` (read-only; evaluator loaded from
`groundtruth_kb.governance.project_authorization_operation_time`; envelope
decoded from the live
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` v1 row;
2026-07-30T03:2xZ) over this proposal's declared target_paths plus this
bridge file produced three discriminating results:

**Classification** (`classify_target`): the four `scripts/*.py` targets
classify `source`; the three `platform_tests/scripts/*.py` targets classify
`test`; `bridge/gtkb-wi5760-pauth-preflight-visibility-001.md` classifies
`bridge`; **`.claude/skills/gtkb-verify/SKILL.md` and
`.claude/rules/codex-review-gate.md` classify `configuration`**, and
**`.groundtruth/formal-artifact-approvals/**` classifies `metadata`**.

**S1 — envelope exactly as recorded:** every operation
(`implementation_packet_create`, `implementation_start`,
`protected_mutation`, `git_commit`) returns `allowed=False,
reason_code=unknown_forbidden_operation: dispatcher_activation`. **Side
finding SF-1 (P1):** the program PAUTH's `forbidden_operations` list contains
the token `dispatcher_activation`, which is not a registered operation or
alias in the permanent taxonomy (the registered entry is
`dispatcher_mutation` with aliases including
`dispatcher_topology_activation`). The evaluator fails closed, so AS RECORDED
the program PAUTH cannot authorize ANY operation for ANY of WI-5757..WI-5773
until the token is repaired through a governed PAUTH amendment (or the
taxonomy gains the alias). This filing performs no such mutation; disposition
is routed to OD-E below.

**S2 — token-repaired simulation, full cohort:** `allowed=False,
reason_code=target_mutation_class_not_allowed:
.claude/skills/gtkb-verify/SKILL.md (configuration),
.claude/rules/codex-review-gate.md (configuration),
.groundtruth/formal-artifact-approvals/** (metadata)`. **Side finding SF-2
(P1):** the program PAUTH allows
`source`/`test_addition`/`governance_evidence`/`bridge` only; the two
protected Slice-B surfaces and the approval-packet envelope are outside its
mutation-class set. Implementation start for Slice B therefore requires an
implementation-time owner decision on the WI-5741 remedy pattern
(`DELIB-202667529` precedent): a narrow supplemental WI-5760 PAUTH covering
exactly these `configuration`/`metadata` targets, or a program-PAUTH
amendment. Routed to OD-E; NOT decided or performed in this filing.

**S3 — token-repaired simulation, source/test/bridge-only cohort:**
`allowed=True` on all four operations — confirming the evaluation is
meaningful and discriminating, not uniformly failing.

This section is itself the demonstration of WI-5760's value: three
governance-relevant facts (SF-1, SF-2, and the green core cohort) that no
mandatory gate currently surfaces became visible by running the recorded
evaluation at proposal time.

## Proposed Change

Four slices. Slices are independently revertible; Slice B is additionally
gated on per-artifact approval packets and the open decisions below.

### Slice A — Focused cohort preflight: `scripts/pauth_cohort_preflight.py`

New read-only CLI (default recommendation under OD-A) mirroring the
invocation grammar of the two existing preflights:

```
python scripts/pauth_cohort_preflight.py --bridge-id <slug> [--envelope proposal|finalization|both] [--content-file <path>] [--json]
```

Behavior:

- **Two evaluation envelopes** (per advisory-002 question 6; coarse direction
  fixed by the owner-ratified WI-5760 consolidation): `proposal` evaluates the
  operative proposal's declared `target_paths` for
  `implementation_packet_create`/`implementation_start`; `finalization`
  projects the terminal commit cohort — implementation/report `target_paths`
  UNION the thread's full `bridge/<slug>-NNN.md` chain including the next
  verdict version — and evaluates `git_commit`/`protected_mutation`,
  mirroring the finalizer's own staging contract
  (`write_verdict.py:446` predecessor-chain assertion and `--include` set
  semantics) so the reviewer sees the authorization decision for the exact
  path set the finalizer will stage, before drafting the verdict.
- Resolves the cited PAUTH from the proposal's `Project Authorization:` line;
  decodes the envelope through the same row-decode used by
  `scripts/implementation_authorization.py`; delegates every decision to the
  canonical `evaluate_envelope` (no reimplementation, no second authority).
- Emits a citable `## PAUTH Operation-Time Evaluation` markdown section (and
  `--json`) recording `allowed`, `reason_code`, per-target classifications,
  evaluator/taxonomy versions and hashes, and the evaluated operation set —
  converting the advisory-001 D4 "predicted result" anti-pattern into a
  recorded evaluation.
- Exit codes: `0` allowed; `5` when any evaluated envelope is denied
  (blocking semantics aligned with `adr_dcl_clause_preflight.py`), with the
  documented owner-waiver line as the only bypass; distinct non-zero exit for
  evaluator/taxonomy load failure (fail closed, never fail silent).
  Enforcement placement is OD-B.
- Thread-state inputs come from the status-bearing numbered bridge files
  (and, where needed, the canonical state-report CLI); the tool reads no
  dispatcher/TAFE configuration surfaces.

`scripts/bridge_applicability_preflight.py` and
`scripts/implementation_authorization.py` are in target_paths for the OD-A
fold-in alternative and for bounded reuse respectively: if OD-A selects
fold-in, the cohort check lands inside the applicability preflight instead of
a third command; independent of OD-A, shared envelope-decode helpers may be
imported from (or minimally extracted out of)
`implementation_authorization.py` so proposal-time and packet-time
evaluations cannot drift. No behavioral change to the post-GO `begin` gate is
proposed.

### Slice B — Wire the check into the surfaces reviewers actually read (protected)

- `.claude/rules/codex-review-gate.md` — checklist addition: one new step in
  the "If Loyal Opposition is reviewing an implementation proposal" list
  (run the cohort preflight, `proposal` envelope) and one new step in the
  eight-step "If Loyal Opposition is verifying an implementation" list at
  `:117` (run the cohort preflight, `finalization` envelope; include the
  emitted section in the verdict; a denied envelope without a documented
  owner waiver is `NO-GO`, not `VERIFIED`).
- `.claude/skills/gtkb-verify/SKILL.md` — workflow step: a new mandatory
  pre-write step in § Mandatory pre-write steps (after the two existing
  preflight steps) running the `finalization` envelope evaluation and
  capturing output, plus a `## PAUTH Operation-Time Evaluation` entry in the
  verdict template and a matching bullet in § Gate enforcement.

This is the placement argument from `.claude/rules/canonical-terminology.md`
§ placement, applied per advisory-002 D7: the check must sit on the path the
reviewer already walks. Both files are protected surfaces — see Cross-Harness
Disposition.

### Slice C — Exposure sweep: `scripts/pauth_finalization_exposure_sweep.py`

New read-only sweep sizing the D8 exposure: for every non-terminal bridge
thread (latest status not `VERIFIED`/`WITHDRAWN`/`DEFERRED`, derived from the
status-bearing numbered bridge files), project the finalization commit cohort
(declared `target_paths` of the latest proposal/report version UNION the
thread's numbered chain), resolve the cited PAUTH, evaluate, and emit a
report table (markdown + JSON under `.gtkb-state/pauth-exposure/`) listing
each exposed thread with `reason_code` and the denied paths/classes. Threads
citing no PAUTH, or citing a PAUTH that fails to load/evaluate (the SF-1
class), are reported in distinct columns rather than skipped. Output is
regenerable runtime evidence, not canonical state; the sweep mutates nothing.
Known expected members per advisory-002 D8: the WI-5662..WI-5668 band under
the bridge-excluding sweep PAUTH; the recorded S1 finding predicts the
WI-5757..WI-5773 band will also surface until SF-1 is repaired.

### Slice D — Tests

New `platform_tests/scripts/test_pauth_cohort_preflight.py` and
`platform_tests/scripts/test_pauth_finalization_exposure_sweep.py`, plus
additive cases in the existing
`platform_tests/scripts/test_implementation_authorization.py` covering any
shared-helper extraction. Fixture-rooted; no live MemBase or live bridge
mutation. Plan below.

## Cross-Harness Disposition

**Protected surfaces (per-artifact approval packets required).** Two
target_paths entries are protected artifacts whose edits require their own
formal-artifact approval packets at implementation time under
GOV-ARTIFACT-APPROVAL-001 / DCL-ARTIFACT-APPROVAL-HOOK-001:

- `.claude/rules/codex-review-gate.md` (Slice B checklist additions — a
  protected narrative artifact under the formal-artifact approval gate).
- `.claude/skills/gtkb-verify/SKILL.md` (Slice B workflow step — a managed
  canonical skill surface; its edit is routed through the same per-artifact
  packet discipline for this change).

Each requires its own packet, presented to the owner with full content per
GOV-ARTIFACT-APPROVAL-001, at implementation time. **target_paths
authorization does not substitute for those per-artifact approval packets**;
inclusion above authorizes the mechanical write scope only. The
`.groundtruth/formal-artifact-approvals/**` envelope is declared in
target_paths for exactly those implementation-time packets. The recorded S2
evaluation above additionally shows both protected paths (class
`configuration`) and the packet envelope (class `metadata`) sit OUTSIDE the
program PAUTH's mutation-class set — so Slice B implementation start is
doubly gated: per-artifact packets AND the OD-E authorization remedy.

**Cross-harness parity.** The cohort preflight and sweep are harness-agnostic
Python CLIs per ADR-CROSS-HARNESS-PARITY-001 — Codex, Cursor, Ollama, and
Claude reviewer sessions invoke them identically, exactly as they invoke the
two existing preflights today. The `.claude/skills/gtkb-verify/SKILL.md` edit
follows the managed-skill lifecycle: edit the canonical file, regenerate the
Codex adapter via `python scripts/generate_codex_skill_adapters.py
--update-registry`; adapters are not edited directly
(DCL-CROSS-HARNESS-ENFORCEMENT-001). No hook is modified by this proposal.

## Specification Links

- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — the project-scoped authorization contract whose operation-time evaluation this proposal makes visible at review time (mandatory anchor).
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 — the machine-checkable operation-time enforcement constraint; the cohort preflight surfaces the same canonical decision the enforcement layer applies.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge protocol and GO/VERIFIED authority; non-executable GOs and unauthorized terminal transactions degrade exactly what this specification protects (mandatory anchor).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — defines the terminal verification gate the finalization-envelope check extends; the evaluated cohort mirrors the atomic commit this DCL's gate requires.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — the preflight surface being extended; the cohort preflight adopts the same operative-file resolution and citable-section discipline.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — two-layer defense in depth; today PAUTH evaluation exists only at the post-GO layer, and this proposal adds the review-time layer.
- GOV-ARTIFACT-APPROVAL-001 — per-artifact approval packets for the two protected Slice-B edits (see Cross-Harness Disposition).
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the mechanical gate enforcing those packets at write time.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — a GO or VERIFIED that certifies unexecutable work degrades the audit trail's meaning; recorded evaluations restore artifact truthfulness.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — append-only bridge chain preserved; the cohort projection reads the numbered chain and rewrites nothing.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory capture preceded this derived proposal; sweep findings route to lifecycle-correct dispositions (work items / owner decisions), not ad-hoc fixes.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the evaluation section is a fresh canonical read (live PAUTH row + permanent taxonomy), replacing the predicted-result anti-pattern of advisory-001 D4.
- GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001 — the evaluation is deterministic service work (evaluator already exists); the preflight and sweep move it out of ad-hoc session judgment.
- SPEC-1830 — operational procedures must be code, not conversation; the reviewer's authorization question becomes a command.
- GOV-STANDING-BACKLOG-001 — WI-5760 is the MemBase backlog authority for this work.
- GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 — both source advisories are adapt-class; open decisions are routed to AUQ below, not silently decided.
- DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 — the mechanical contract for that gate; the OD register implements its evidence-routing clause.
- GOV-10 — tests exercise the exposed production interfaces (the two new CLIs), not internals.
- GOV-12 — work item creation triggers test creation (Slice D files).
- SPEC-1662 (GOV-18) — assertions are behavioral (allowed/denied decisions, reason codes, exit codes, cohort membership), not shape-only.
- GOV-15 — no autonomous test fixes; regression failures route to owner-gated work items.
- GOV-17 — automation-script modification gate: `scripts/` changes ride this reviewed proposal.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — canonical-skill edit with adapter regeneration; enforcement surfaces stay in agreement.
- ADR-CROSS-HARNESS-PARITY-001 — harness-agnostic CLI surface chosen over any harness-local helper extension.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is an in-root platform surface; sweep output stays under `.gtkb-state/`.

## Prior Deliberations

Deliberation search performed 2026-07-29 (`gt deliberations search "PAUTH
operation-time preflight visibility" --limit 5`): top semantic hits were
DELIB-202667587 (WI-5458 PAUTH-precedence NO-GO — adjacent PAUTH-enforcement
surface, consistent, non-controlling), DELIB-20266176, DELIB-202667251,
DELIB-20261427, and DELIB-2579 (generic verdict records; no controlling
precedent for a review-time authorization gate). Targeted-id reads and
authorities:

- DELIB-202667531 — owner triage directive: fix-class advisories become authorized corrective work items; owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729; bridge protocol explicitly NOT waived per item.
- DELIB-202667533 — AT-01..AT-04 synthesis decisions; AT-04 establishes the program PAUTH this proposal cites, paired with the completion discipline WI-5760 protects (threads must actually be able to reach terminal VERIFIED for completion automation to mean anything).
- DELIB-202667534 — advisory corpus disposition table consolidating advisory-001/-002 of the PAUTH operation-time gate cluster into WI-5760 and fixing the coarse remediation direction (pre-VERIFIED cohort evaluation, checklist + skill placement, exposure sweep).
- DELIB-202667529 — the WI-5741 exact-scope terminal-recovery PAUTH owner decision; the proven narrow-remedy pattern OD-E reuses for the SF-2 class gap.
- Source advisories: `bridge/gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory-001.md` (D1-D5) and `-002.md` (D6-D8).
- Live reproduction chain: `bridge/gtkb-wi5741-spec-packet-postimage-completeness-006.md` (NO-GO on the unauthorized terminal transaction).
- Sibling scope boundary: `bridge/gtkb-wi5763-governed-verdict-filing-path-001.md` owns the finalizer/commit-first restructuring and the governed verdict-filing CLI. WI-5760 deliberately does NOT touch `write_verdict.py` or the filing path; it makes the authorization decision visible BEFORE those surfaces run. The two work items compose without overlap (WI-5763 changes HOW verdicts are filed/finalized; WI-5760 changes WHAT the reviewer knows before drafting one).

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001. WI-5760 is one of those corrective items (P1, defect, `maintenance_tool`).
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM (verified active this session, v1, scope WI-5757..WI-5773 including WI-5760; classes source, test_addition, governance_evidence, bridge; owner decision DELIB-202667533) paired with completion discipline. **Completion-discipline linkage:** AT-04's auto-completion on terminal VERIFIED presupposes threads CAN legally reach terminal VERIFIED; the WI-5741/WI-5665 blocking class silently breaks that presupposition, and WI-5760's finalization-envelope visibility is what keeps the AT-04 discipline sound. The recorded S1 finding (SF-1) is material to AT-04 and is surfaced to the owner via OD-E.
- **DELIB-202667534** (owner decision, 2026-07-29): disposition-table consolidation fixing WI-5760's coarse direction; this proposal implements that direction and reserves residual forks to the OD register below.

Open decisions — REMAIN OPEN, flagged for implementation-time owner grilling
via AskUserQuestion per GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001; this
proposal does NOT silently decide them. Design sections present recommended
defaults for ratification; a slice touching an open decision does not
implement until its AUQ evidence exists and is recorded in the implementation
report's Owner Decisions / Input section:

- **OD-A (gate shape; advisory-001 Q1).** Standalone third preflight `scripts/pauth_cohort_preflight.py` (default) versus folding the cohort check into `bridge_applicability_preflight.py`. Both surfaces are in target_paths so either resolution is in scope.
- **OD-B (enforcement placement; advisory-001 Q2).** Review-time mandatory command with blocking exit 5 (default) versus additional filing-time PreToolUse blocking versus both. Filing-time blocking would reject legitimate proposals authored before their enabling PAUTH exists; the default defers it, and no hook edit is in this proposal's scope.
- **OD-C (envelope operations; advisory-002 Q6 residual).** The two-envelope direction (proposal target_paths at GO review; projected finalization cohort at VERIFIED review) is fixed by the WI-5760 consolidation; the residual AUQ is the exact operation set evaluated per envelope (defaults: `implementation_packet_create`+`implementation_start` for proposal; `git_commit`+`protected_mutation` for finalization).
- **OD-D (bridge-class authorization shape; advisory-001 Q3 / advisory-002 Q7).** Whether `bridge` is added to every PAUTH governing bridge-protocol work as a matter of course, or governed-writer append-only `bridge/<slug>-NNN.md` writes are exempted from the packet requirement. Highest-leverage question of the set; the Slice C sweep exists to size it with evidence before the owner answers. Explicitly NOT decided here.
- **OD-E (side-finding remediation routing; SF-1 + SF-2).** SF-1: repair of the unregistered `dispatcher_activation` forbidden-operation token on the program PAUTH (governed PAUTH amendment to the registered `dispatcher_topology_activation`/`dispatcher_mutation` vocabulary, versus taxonomy alias registration). SF-2: authorization remedy for Slice B's `configuration`/`metadata` targets (narrow supplemental WI-5760 PAUTH on the DELIB-202667529 WI-5741 remedy pattern, versus program-PAUTH amendment). Both are MemBase `project_authorizations` mutations requiring owner approval per GOV-ARTIFACT-APPROVAL-001; neither is performed by this filing, and SF-1 blocks implementation start for the whole WI-5757..WI-5773 band until resolved.

## Requirement Sufficiency

Existing requirements sufficient. GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
and DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 already define
the authorization contract and its canonical evaluator;
GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 already requires
two-layer mechanical enforcement; GOV-FILE-BRIDGE-AUTHORITY-001 already makes
GO/VERIFIED integrity load-bearing. This change makes the platform comply by
surfacing the existing contract at review time. No new or revised requirement
is required before implementation. (Any OD-D/OD-E authorization-model change
is corrective formal-artifact work executed through its own
GOV-ARTIFACT-APPROVAL-001 evidence at that time; an output of the work, not a
precondition for it.)

## Spec-Derived Test Plan

New test files: `platform_tests/scripts/test_pauth_cohort_preflight.py`,
`platform_tests/scripts/test_pauth_finalization_exposure_sweep.py`; additive
cases in `platform_tests/scripts/test_implementation_authorization.py`. All
run against fixture project roots, fixture bridge threads, and fixture
`project_authorizations` rows; no live MemBase or live bridge mutation.

1. **Bridge-excluding PAUTH is flagged at review time** —
   `test_finalization_cohort_denied_for_bridge_excluding_pauth`: fixture
   thread with a green implementation target set and a cited PAUTH lacking
   the `bridge` class; the `finalization` envelope returns `allowed=False,
   reason_code=target_mutation_class_not_allowed` naming the numbered bridge
   chain paths, and the CLI exits 5 — the WI-5741 `-006` blocking class
   reproduced as a review-time signal. Derives from
   GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001,
   DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001,
   GOV-FILE-BRIDGE-AUTHORITY-001, GOV-10.
2. **Two envelopes can diverge** —
   `test_proposal_envelope_allowed_while_finalization_denied`: same fixture;
   the `proposal` envelope (implementation targets only) returns
   `allowed=True` while `finalization` is denied — the exact WI-5665/WI-5741
   divergence from advisory-002 D6. Derives from
   DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and advisory-002's D6
   two-envelope requirement, SPEC-1662.
3. **Authorized cohort passes** — `test_authorized_cohort_allowed`: fixture
   PAUTH carrying `source`/`test`/`bridge`/`governance_evidence`; both
   envelopes return `allowed=True, reason_code=allowed`, exit 0, and the
   emitted section records evaluator/taxonomy identity and per-target
   classifications. Derives from GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-10.
4. **Evaluator fails closed and reports distinctly** —
   `test_unregistered_forbidden_operation_fails_closed`: fixture PAUTH with
   an unregistered forbidden-operation token (the recorded SF-1 class)
   produces `reason_code=unknown_forbidden_operation`, a non-zero exit, and a
   report row distinct from mutation-class denial; no allowed=True is ever
   emitted on evaluator failure. Derives from
   DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, SPEC-1662.
5. **Sweep enumerates exposed threads** —
   `test_sweep_enumerates_exposed_threads`: fixture bridge dir with one
   authorized thread, one bridge-excluded thread, one thread citing no PAUTH,
   and one terminal (`VERIFIED`) thread; the sweep lists exactly the exposed
   non-terminal threads with reason codes, reports the no-PAUTH and
   evaluator-failure classes in distinct columns, skips terminal threads, and
   writes only under the fixture's `.gtkb-state/pauth-exposure/`. A rerun is
   idempotent. Derives from advisory-002 D8 sizing requirement,
   GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001, SPEC-1830, GOV-10.
6. **No drift against the post-GO gate** —
   `test_cohort_preflight_matches_implementation_authorization_decision`:
   for identical fixture envelope+targets+operation, the cohort preflight's
   decision equals `_evaluate_project_authorization_operations`' outcome
   (allowed and denied cases) — one canonical authority, two surfaces.
   Derives from GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.

Execution: `groundtruth-kb/.venv/Scripts/python.exe -m pytest
platform_tests/scripts/test_pauth_cohort_preflight.py
platform_tests/scripts/test_pauth_finalization_exposure_sweep.py
platform_tests/scripts/test_implementation_authorization.py -v`, plus
`ruff check` and `ruff format --check` on all changed Python files.

## Acceptance Criteria

1. A reviewer can run one documented command per envelope and see the
   canonical `allowed`/`reason_code` decision for a proposal's target_paths
   and for a thread's projected finalization commit cohort BEFORE issuing
   `GO` or drafting a terminal verdict.
2. The WI-5741 `-006` blocking class (`target_mutation_class_not_allowed` on
   the bridge chain) is reproducible as a review-time exit-5 signal on
   fixtures, and the recorded evaluation section is citable in verdicts.
3. The verification checklist in `.claude/rules/codex-review-gate.md` and the
   mandatory pre-write steps in `.claude/skills/gtkb-verify/SKILL.md` each
   carry the cohort-evaluation step (post per-artifact packets; Codex adapter
   regenerated).
4. The exposure sweep enumerates every exposed non-terminal thread with
   reason codes and distinct no-PAUTH/evaluator-failure classes, writing only
   regenerable output under `.gtkb-state/pauth-exposure/`.
5. Cohort-preflight decisions provably match the post-GO gate's canonical
   evaluator outcomes on identical inputs.
6. All new tests pass; ruff lint and format gates clean.

## Risk and Rollback

Risk: LOW-MEDIUM. Slices A/C/D are additive read-only tooling plus tests —
no existing gate's behavior changes, no hook edits, no dispatcher/TAFE
surfaces touched, no MemBase schema or row mutation. Slice B is a text
addition to two protected surfaces behind per-artifact approval packets and
the OD-E authorization remedy; until Slice B lands, Slices A/C already give
reviewers the command. The main delivery risk is recorded openly above:
SF-1 blocks implementation start for the whole program PAUTH band until the
owner resolves OD-E, and SF-2 gates Slice B specifically — both surfaced now,
at review time, which is precisely the behavior this work item institutes.
Rollback: each slice reverts independently by commit; new files delete
cleanly; the two protected-surface edits revert as text with no runtime
coupling.

Recommended commit type: feat

## Verification Questions for Loyal Opposition

1. Does the two-envelope design (proposal vs projected finalization cohort,
   with the cohort mirroring the finalizer's staging contract) correctly
   close the D6 gap without duplicating the post-GO gate's authority?
2. Is the OD register the correct governance shape — coarse direction fixed
   by DELIB-202667534, residual forks reserved to implementation-time AUQ —
   or should OD-A/OD-B be resolved before GO?
3. Are the recorded SF-1/SF-2 side findings correctly scoped as
   owner-decision material (OD-E) rather than silent scope creep, given they
   were discovered by the exact evaluation this proposal mandates?

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
