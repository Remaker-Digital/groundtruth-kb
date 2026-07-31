NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: a9503a56-1058-42c3-8da1-4f404c64d488
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent performing Loyal Opposition bulk bridge processing round 3

# Loyal Opposition Review - WI-5492 generated skill projections for retired IPA reference cleanup

bridge_kind: lo_verdict
Document: gtkb-retire-ipa-refs-skill-projections
Version: 002
Responds to: bridge/gtkb-retire-ipa-refs-skill-projections-001.md

## Verdict

NO-GO. The proposal correctly identifies a real scope gap left by the already-GO'd
gtkb-retire-ipa-refs-rules-skills slice, but its four shared/multi-tenant target
files are, right now, in the live working tree, already commingled with dirty
hunks belonging to at least one other active, non-terminal bridge thread plus
untracked additions for two unrelated skills. The proposal's own safety language
("use scoped patch isolation for the approved entries or file a revised
proposal") defers the isolation method to implementation time with no named
mechanism, no owner waiver, and no binding post-implementation verification
conditions of the kind a directly on-point prior verdict required for this exact
failure class. Approving whole-file target_paths authority over these four
files as currently specified creates a real risk of an unauthorized,
cross-thread commit.

Review independence: proposal author session context
019f6f8b-9fd7-7142-93a8-5696dca44d85 (prime-builder/codex, harness A) differs
from this reviewer's session context a9503a56-1058-42c3-8da1-4f404c64d488
(loyal-opposition/claude, harness B, fresh sub-agent invocation). Independent
review boundary satisfied.

## Applicability Preflight

- packet_hash: sha256:f86db5a19bcd119b4556b8e2b031fa21ef82a6251d81d36efad7f2286209cf3e
- bridge_document_name: gtkb-retire-ipa-refs-skill-projections
- preflight_passed: true
- missing_required_specs: (none)
- missing_advisory_specs: (none)
- blocking_errors: (none)

All 24 declared target paths were confirmed on disk. Mechanical spec-linkage
preflight passes; this NO-GO is not a linkage/format defect, it is a
governance-substance finding the automated preflight cannot detect (it checks
proposal text for cited specs, not live working-tree state).

## Clause Applicability (adr_dcl_clause_preflight.py)

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit: 0 (pass)

Clause preflight also passes mechanically. Same caveat as above: clause
evidence-presence in proposal text is not a substitute for verifying the live
working-tree state the proposal's target_paths actually point at.

## Prior Deliberations

- DELIB-202665986 (WI-4841 Hunk-Scoped Finalization Under Owner Waiver) -
  directly on-point precedent, read in full. A prior thread hit the identical
  failure class: a shared, generator-produced .agent/skills/MANIFEST.json /
  .codex/skills/MANIFEST.json could not be cleanly regenerated without
  absorbing unrelated foreign skill objects. The precedent record states this
  plainly: "a hand-synthesized sub-hunk to isolate the WI-4841 manifest object
  was owner-waiver-class and could not be self-authorized headless." Resolution
  required (1) an explicit owner decision
  (DELIB-20260710-WI4841-HUNK-SCOPED-FINALIZATION-WAIVER) naming the exact
  hand-authored-patch method and its denylist, and (2) seven binding
  "Verification Conditions" that the eventual post-implementation report had to
  satisfy with primary evidence (staged-diff name-only equality to declared
  target_paths; the staged manifest diff contains only the one approved skill
  object; no unrelated source-hash refresh; etc.), reviewable by an independent
  verifier rather than trusted from prose.
- gtkb-wi4841-managed-skill-adoption-review-scaffold-024/-025/-026 - the
  finalization-only NO-GO / Prime NO-ACTION chain that preceded the WI-4841
  owner-waiver route. This is the historical evidence that "approve the
  proposal now, catch commingling at report/verification time" was tried first
  for this failure class and cost multiple review round-trips before the
  owner-waiver method resolved it. That history counsels catching the
  commingling risk at proposal time when it is already visible, rather than
  repeating the same costly cycle here.
- WI-5105 (resolved) - names this exact pattern as a recurring systemic class
  ("multiple reliability threads targeting the same hot files ... commingle
  when implemented in parallel, so neither can be atomically VERIFIED-finalized")
  and records the mitigation this review is applying: full sequencing of one
  thread's implement+report+VERIFY+commit before the next begins, absent a
  coordination-guard tool (none exists yet; confirmed by source search across
  scripts/ and .claude/rules/).
- bridge/gtkb-retire-ipa-refs-rules-skills-001.md / -002.md / -003.md - read in
  full. Confirms the sibling slice's target_paths cover only source files (8
  rules + 4 canonical .claude/skills/** + CLAUDE.md + AGENTS.md), and its -003
  implementation report (status NEW, not yet VERIFIED) already ran
  generate_codex_skill_adapters.py --check --update-registry,
  generate_antigravity_skill_adapters.py --check --update-registry, and
  generate_api_skill_adapters.py --check as its own verification evidence -
  which is what left the projection surfaces dirty in the tree today. Its own
  Risk/Rollback section correctly defers the projection cleanup to "a separate
  bridge thread" (this one), confirming the scope split is intentional and
  sound; the finding below is about how this thread's target files are
  currently, independently, also dirtied by unrelated work.

## Findings

### [P1] Declared target_paths for four shared/generated files are currently commingled with unrelated, non-terminal work

- Claim: .codex/skills/MANIFEST.json, .agent/skills/MANIFEST.json,
  .api-harness/skills/MANIFEST.json, and
  config/agent-control/harness-capability-registry.toml - four of this
  proposal's 24 declared target_paths - are, in the live working tree right
  now, dirty with content this proposal explicitly disclaims plus content it
  never mentions.
- Evidence:
  - git diff -- .codex/skills/MANIFEST.json shows five changed hunks, not
    four: lo-opportunity-radar, loyal-opposition-report/codex-report,
    kb-session-wrap, loyal-opposition-hygiene-assessment (all WI-5492, in
    scope) PLUS a projects source_sha256 hunk (out of scope; the proposal's
    own "Cross-Harness Disposition" table names WI-5156 projects projections
    as excluded).
  - git diff -- .agent/skills/MANIFEST.json shows the same projects hunk PLUS
    a brand-new inserted object for .agent/skills/gtkb-hygiene-reclaim/SKILL.md
    - a skill the proposal's own text names as excluded ("This proposal does
    not claim ... gtkb-hygiene-reclaim ...").
  - git diff -- .api-harness/skills/MANIFEST.json shows the projects hunk PLUS
    new inserted objects for gtkb-hygiene-reclaim AND
    managed-skill-adoption-review - both also named as excluded in the
    proposal's own text.
  - git diff -- config/agent-control/harness-capability-registry.toml shows
    the four approved WI-5492 hunks PLUS a projects Codex/Antigravity
    source_sha256 hunk pair - out of scope per the proposal's own text
    ("Update ... only for those four skills' ... entries").
  - git status --short -- .agent/skills/ .api-harness/skills/ .codex/skills/
    additionally shows .codex/skills/verify/helpers/write_bridge_5171.py and
    .claude/skills/projects/SKILL.md dirty, and three untracked (??) new
    directories: .agent/skills/gtkb-hygiene-reclaim/,
    .api-harness/skills/gtkb-hygiene-reclaim/,
    .api-harness/skills/managed-skill-adoption-review/.
  - gt bridge show gtkb-wi5156-governed-project-dependency-ordering-cli --json
    --compact confirms that thread's latest status is REVISED - active and
    non-terminal, not yet GO'd, not yet committed. Its projects changes are
    therefore live, in-flight, unreviewed content sitting inside the exact
    files this proposal wants whole-file target_paths authority over.
  - The two other skills (gtkb-hygiene-reclaim, managed-skill-adoption-review)
    have their own terminal VERIFIED bridge history
    (gtkb-wi5142-hygiene-reclaim-cli-skill-phase1-004.md,
    gtkb-wi4841-managed-skill-adoption-review-scaffold-030.md) but their
    Antigravity/API-harness cross-harness parity was apparently never
    finalized - a separate, pre-existing hygiene gap unrelated to WI-5492,
    also sitting in these same shared files.
- Risk/impact: the proposal's stated finalization posture ("Preserve sibling
  dirty work in shared projection files ... No whole-file finalization of
  shared manifests or the registry is allowed unless a reviewer re-confirms
  that the whole-file diff is limited to this proposal's four skill families")
  is the right instinct, but I have now re-confirmed the opposite: the
  whole-file diff on all four shared targets is NOT limited to the four
  WI-5492 skill families. If implementation proceeds as scoped (whole-file
  target_paths, generator re-run, then the standard whole-file --include
  VERIFIED finalization helper), the resulting commit would very likely bundle
  WI-5156's still-under-review projects change and the two untracked
  Antigravity/API-harness skill additions into this thread's commit without
  their own GO - a cross-thread authority violation, not merely a cosmetic
  scope overrun. The generator scripts invoked by the sibling -rules-skills-003
  report (--check --update-registry / --check) demonstrably operate over the
  entire skill tree rather than a scoped subset, so simply "re-running the
  generator for the four skills" will reproduce this same commingling on every
  invocation, not just accidentally once.
- Recommended action (either path resolves the finding):
  1. Sequence, don't parallelize - park this proposal until
     gtkb-wi5156-governed-project-dependency-ordering-cli reaches VERIFIED and
     its projects hunks are committed and clean in these four shared files
     (per the WI-5105 mitigation pattern, "fully sequence
     implement+report+VERIFY+commit of one before beginning the other"). Once
     projects is clean, re-run the applicable preflights and re-confirm the
     remaining diff is WI-5492-only before refiling.
  2. Or, name a concrete isolation mechanism now, not at implementation time -
     revise the proposal to specify exactly how the four-skill-only hunks will
     be isolated (e.g., a hand-authored patch limited to the named manifest
     objects, per the WI-4841 method), and, per the WI-4841 precedent, obtain
     an explicit owner decision authorizing that method for this thread if
     headless self-authorization is not available. Include the same class of
     binding, primary-evidence verification conditions the WI-4841 GO recorded
     (staged-diff object-level inspection, not prose) in this proposal's
     Specification-Derived Verification Plan before it can be re-reviewed.
  3. Either way, the untracked gtkb-hygiene-reclaim / managed-skill-adoption-review
     Antigravity/API-harness parity gap is a separate, already-VERIFIED-skill
     hygiene item; it should get its own work item / bridge thread rather than
     being silently absorbed (or silently left stranded) by whichever thread
     next touches these shared files.
- Decision needed from owner: none required to act on this NO-GO; Prime
  Builder can choose remediation path 1 or 2 without new owner input. Path 2's
  owner-waiver sub-step, if chosen, does need an AskUserQuestion-recorded
  decision per the WI-4841 precedent.

### [P3] Fast-lane / approval-state paths not invoked - CONFIRMATION, no defect

- Claim: the proposal does not attempt to invoke GOV-RELIABILITY-FAST-LANE-001
  or rely on work-item approval_state as authorization.
- Evidence: WI-5492 origin is hygiene (not defect/regression), so fast-lane
  eligibility would not apply in any case; the proposal correctly cites the
  active project authorization
  (PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30,
  confirmed status: active, no expiration, allowed_mutation_classes includes
  skill_docs and config) as its authorization basis instead.
- Impact: none; this is a positive confirmation, not a finding requiring
  action.

## Backlog Conflict Check

Checked the standing backlog and live bridge state for conflicting or
duplicate work on the same files before this review, per the reviewer
checklist:

- gtkb-wi5156-governed-project-dependency-ordering-cli - REVISED, live,
  targets the projects skill in the same shared manifest/registry files. This
  is the conflict documented in Finding P1 above; the recommended remediation
  is sequencing, which brings the conflicting work into explicit order rather
  than leaving it implicit.
- No other open thread was found touching the same four shared files for a
  different skill family at review time.

## Gate Summary

- Root boundary: all 24 target_paths inside E:\GT-KB. PASS.
- Specification linkage: present and relevant, 13 specs cited. PASS.
- Applicability preflight: passed, no missing required specs. PASS (mechanical
  gate only; does not reach this review's substantive finding).
- Clause preflight: exit 0, zero blocking gaps. PASS (mechanical gate only).
- Project authorization:
  PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
  independently verified active, scope covers skill_docs/config. PASS.
- Cross-Harness Disposition section: present and detailed. PASS.
- Review independence: distinct session contexts (harness A author vs. harness
  B reviewer, unrelated session IDs). PASS.
- Live working-tree scope isolation for shared target files: FAIL (see Finding
  P1). This is the sole basis for NO-GO.

## Recommended Commit Type

Not applicable - no commit is authorized by this verdict.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
