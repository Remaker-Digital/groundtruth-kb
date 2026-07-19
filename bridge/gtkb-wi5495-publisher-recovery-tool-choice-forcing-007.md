NO-GO
::init gtkb pb
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 20dd407b-d159-4c05-9700-63511dadff11
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code subagent; independent Loyal Opposition bridge review

# LO Review NO-GO (backlog conflict with live WI-5542) - gtkb-wi5495-publisher-recovery-tool-choice-forcing

bridge_kind: lo_verdict
Document: gtkb-wi5495-publisher-recovery-tool-choice-forcing
Version: 007
Reviewed: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-006.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5495

## Verdict

NO-GO. Version 006's underlying technical mechanism is sound and independently
re-verified (see below), but the D/Ollama half of its bundled scope directly
and materially conflicts with a live, more substantive, already-designed
competing proposal for the identical two target files (WI-5542,
`bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md`, status `NEW`,
unreviewed) whose own author has explicitly flagged the overlap and is waiting
on this exact disposition. This is a Backlog Conflict & Future Work Review
finding, not a rejection of version 006's code-level reasoning.

## Independent Technical Verification (the parts that ARE sound)

- `git diff -- scripts/cloud_harness_base.py` (current working tree, unstaged)
  confirms the F/OpenRouter `DIALECT_OPENAI_CHAT` `tool_choice` forcing branch
  is present exactly as described, mirroring the shipped
  `DIALECT_ANTHROPIC_MESSAGES` pattern in the same `if` block (around line
  2389). `git diff -- platform_tests/scripts/test_cloud_harness_base.py`
  confirms matching negative-control test assertions. This is the same
  quarantined F diff independently verified correct by version 004; it is
  unchanged and remains correct.
- Direct read of `scripts/cloud_harness_base.py` confirms all four claimed
  "recovery-exhaustion checkpoints... currently raising a bare
  `CloudHarnessError`": line 2440 (`bridge verdict publication did not advance
  before final assistant text`), line 2481 (`...after blank response`), line
  2514 (`publisher recovery exhausted`, non-publisher tool call branch), and
  line 2627 (`publisher recovery exhausted`, invalid-verdict-path branch). All
  four currently propagate uncaught to the top-level `except CloudHarnessError
  ... raise` at line 2671/2683, matching the reproduction evidence quoted since
  version 001.
- The proposed `BridgeVerdictRecoveryExhausted` mechanism (catch before the
  generic `CloudHarnessError` handler, mirroring the existing
  `BridgeVerdictClaimStandDown` clause at lines 1977/2668-2670) is
  architecturally correct: Python requires the more specific exception
  subclass to be caught first, and `BridgeVerdictClaimStandDown` already
  establishes exactly this pattern at the exact code position described.
- Direct read of `scripts/ollama_harness.py` confirms: (a) only one error
  class, `OllamaHarnessError` (line 103) -- no `BridgeVerdictClaimStandDown`
  equivalent exists; (b) `_dispatch_publish_bridge_verdict` (line 909) calls
  `publish_lo_verdict` directly with no preceding work-intent claim
  acquisition, unlike `cloud_harness_base.py`'s `_dispatch_publish_bridge_verdict`
  (line 1932), which calls `_ensure_provider_verdict_claim` (line 1955) before
  publishing. This asymmetry is real and independently confirmed.
- `dispatch-runs/*loyal-opposition-D*.exit_code` inspection (read-only, all 10
  files present today, 2026-07-18) shows exit code `1` in 10/10 samples --
  even stronger than the proposal's own cited "7/7 crashed, zero successes."
  D's historical failure rate claim is corroborated, not merely asserted.
- **Dispatcher-side completion semantics independently traced** (this was not
  argued in the proposal, but is the determining fact for whether the
  "graceful exit" mechanism is safe): `scripts/dispatcher_runtime.py` around
  line 6050 classifies dispatch outcomes by whether the *selected bridge
  document* actually received a verdict (`incomplete_documents`), not merely
  by exit code. When `incomplete_documents` is non-empty, the stand-down
  marker is absent, and `exit_code == 0`, the dispatcher sets
  `failure_reason = "no_verdict_produced"` (line 6061-6064), which forces
  `dispatch_succeeded = False` regardless of exit code. This means the
  proposed clean `status: recovery_exhausted` JSON return would still be
  correctly classified as a dispatch **failure** by the dispatcher -- it does
  NOT create a false-success blind spot, and it does NOT violate WI-5224's
  "governed verdict required before completion" principle (WI-5224 is
  `resolved`; its principle is preserved). The proposal's "observable" framing
  is accurate for this specific mechanical concern, once traced through to the
  dispatcher's own document-state-based completion check.

## Backlog Conflict Finding (the blocking issue)

A live, unreviewed, `NEW`-status bridge proposal, `WI-5542`
(`bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md`), targets the
identical two files version 006 also targets for D:
`scripts/ollama_harness.py` and `platform_tests/scripts/test_ollama_harness.py`.
This was independently confirmed by direct read of that bridge file (not
merely the WI-5542 MemBase record's self-description):

- WI-5542's own "Proposed Scope" states: *"Sequence implementation after
  WI-5495, WI-5471, WI-5545, and every exact-target owner are terminal, then
  require a fresh matching claim and implementation-start authorization."*
  WI-5542 is deliberately waiting on WI-5495 (this thread) to reach a
  terminal state before it can proceed on the same files.
- WI-5542's MemBase record (`status_detail`, `changed_by: prime-builder/codex`,
  `changed_at: 2026-07-18T07:25:11Z` -- after version 006 was filed) states
  explicitly: *"WI-5495 v006 currently overlaps and its proposed clean
  no-verdict exit does not satisfy WI-5224 or the 60-clean goal, so await
  independent LO disposition rather than absorbing it."*
- WI-5542's design is substantively different from, and more likely to
  actually raise D's success rate than, version 006's D-side mechanism:
  version 006 keeps the existing tool-call-based recovery loop and only makes
  its *failure mode* cleaner (accepting, in its own words, that it is "rather
  than relying solely on forcing to prevent exhaustion from being reached at
  all"). WI-5542 instead proposes bypassing tool-calling reliability
  entirely for the recovery turn -- requesting one structured JSON verdict
  envelope in a no-tools turn and validating it locally before invoking the
  canonical publisher -- which sidesteps the exact tool-choice-non-compliance
  problem that both `DELIB-202666850` (this thread's own cited empirical
  finding) and version 006 document.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718`
  is an active, bounded project authorization specific to WI-5542, confirming
  it is a live, owner-authorized-scope thread, not a stray backlog note.

Per `.claude/rules/loyal-opposition.md` "Backlog Conflict & Future Work Review"
and `.claude/rules/codex-review-checklists.md` ("Has the standing backlog...
been checked for upcoming related work to prevent duplicating effort or
interfering with future project plans... with conflicts resolved by bringing
work forward or adding to the scope of an existing future project?"), this is
exactly the class of conflict that must be resolved before GO, not discovered
after two threads independently mutate the same recovery flow in
`scripts/ollama_harness.py`.

Implementing version 006's D-side scope now would:

1. Not appreciably advance the owner's stated goal ("60 clean sequential
   dispatches... as proof") for D, since the mechanism does not increase the
   probability that a given D recovery turn actually produces a valid verdict
   -- confirmed by version 006's own framing and independently corroborated by
   this review's dispatcher-completion trace above (still `dispatch_succeeded
   = False` either way).
2. Create rework/merge risk: WI-5542's envelope-based redesign will very
   likely need to substantially rewrite the same recovery-turn code region
   version 006 proposes to touch (the tool-call-based exhaustion-catching
   logic), since WI-5542 replaces the *mechanism* by which D exits recovery,
   not just its failure-reporting shape.
3. Delay WI-5542 for no compensating benefit, since WI-5542 is explicitly
   blocked on this thread reaching "terminal," and version 006's D-side change
   does not solve the problem WI-5542 exists to solve.

This is a scope/sequencing finding, not a verdict on WI-5542's eventual
merits (that proposal is itself unreviewed and must clear its own GO/NO-GO on
its own record); nor is it a rejection of version 006's underlying technical
correctness for the parts that do not conflict.

## Non-Blocking Secondary Findings

- Version 006 dropped `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` from `Specification Links`, both of
  which earlier versions of this same thread (001, 003, 005) carried. The
  applicability preflight reports both as `missing_advisory_specs` (non-
  blocking; does not gate this verdict). Restore them for consistency when
  refiling.
- The current unstaged working-tree diff for `scripts/cloud_harness_base.py`
  contains, in addition to the quarantined WI-5495 F-side hunk, a second,
  unrelated hunk wrapping `_tool_call_parts` in a
  `try/except CloudHarnessError` (matches `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-002.md`,
  a different live thread). The two hunks do not functionally conflict (they
  touch different code regions -- the publisher-only-recovery `tool_choice`
  block near line 2389 vs. the per-tool-call parse-error handling near line
  2570), but whichever session next implements either WI-5495 or WI-5471 must
  select hunks carefully so neither thread's change is accidentally staged
  under the other's commit.

## Specification-Derived Verification

| Requirement | Verification | Observed Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability preflight against operative file `-006` | PASS; `preflight_passed=true`; `missing_required_specs` empty. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight | PASS; matched via `doc:*`, `Specification Links` content. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight + direct source re-verification | Clause preflight PASS (zero blocking gaps). Substantively, the F-side test plan is sound (re-verified above); the D-side test plan cannot be evaluated for actual defect resolution because the underlying D-side mechanism is contested by a live competing proposal for the same code region. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Direct re-read of `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `scripts/dispatcher_runtime.py` (current HEAD), plus read-only inspection of `.gtkb-state/bridge-poller/dispatch-runs/*loyal-opposition-D*.exit_code` and the live WI-5542 bridge file and MemBase record | PASS for all of version 006's verifiable code-structure and dispatch-history claims (see Independent Technical Verification above); the backlog-conflict finding itself is grounded in a fresh direct read of `bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md`, not a relayed summary. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Target inventory | `scripts/cloud_harness_base.py`, `scripts/ollama_harness.py`, `platform_tests/scripts/test_cloud_harness_base.py`, `platform_tests/scripts/test_ollama_harness.py` -- all resolve inside `E:\GT-KB`. |
| `GOV-RELIABILITY-FAST-LANE-001` | `KnowledgeDB.get_work_item("WI-5495")` re-check | `origin=defect`, `priority=P0`, `resolution_status=open`, `project_name=PROJECT-GTKB-RELIABILITY-FIXES`; eligibility criteria still hold in principle. The blocking issue here is a backlog conflict, not fast-lane ineligibility. |
| `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` | `KnowledgeDB.get_project_authorization(...)` re-check | `status=active`, `expires_at=None`, covers `PROJECT-GTKB-RELIABILITY-FIXES`, `allowed_mutation_classes` includes `source`/`test_addition`; no forbidden operation implicated. |

## Applicability Preflight

- packet_hash: `sha256:0f20ac5b35203c72eaab513b40f94f36cd6fd95c961812c95550ed95f021ed59`
- bridge_document_name: `gtkb-wi5495-publisher-recovery-tool-choice-forcing`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-006.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`
- blocking_errors: `[]`

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5495-publisher-recovery-tool-choice-forcing`
- Operative file: `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-006.md`
- Clauses evaluated: 5; must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code observed: 0 (pass)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail and numbered-file discipline for this correction.
- `GOV-STANDING-BACKLOG-001` - the substantive basis for this NO-GO: standing-backlog conflict check against WI-5542.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - carried forward from the proposal under review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - carried forward.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - this verdict's claims (both the technical-verification and the backlog-conflict finding) are grounded in fresh direct reads, not relayed summaries.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - target-path and project-linkage evidence carried forward.
- `GOV-RELIABILITY-FAST-LANE-001` - re-checked; eligibility criteria hold in principle, unaffected by this verdict's rationale.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain in-root; carried forward.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing specification, carried forward.

## Required Revision

A `REVISED` proposal must, at minimum:

1. Split the F/OpenRouter `DIALECT_OPENAI_CHAT` forced-function `tool_choice`
   fix in `scripts/cloud_harness_base.py` (plus its test coverage in
   `platform_tests/scripts/test_cloud_harness_base.py`) into its own
   narrowly-scoped filing -- independently re-verified correct, complete, and
   non-conflicting with any other live thread in this review. This mirrors
   version 005's already-attempted split (which was superseded before
   receiving a verdict); re-file that scope on its own so it is not held
   hostage by the D-side conflict.
2. For D/Ollama: either (a) drop the "graceful exhaustion exit" mechanism
   from this thread's scope entirely, since it does not solve the reliability
   problem WI-5542 is already designed to solve and creates rework risk once
   WI-5542 proceeds; or (b) explicitly coordinate scope with WI-5542 (e.g., by
   having the WI-5542 proposal absorb whichever elements of version 006 remain
   useful once WI-5542's envelope-based recovery lands, rather than
   implementing them twice). Prime Builder and/or the owner should make this
   sequencing call with visibility into both threads; this verdict does not
   mandate one specific choice.
3. The work-intent claim-acquisition parity fix for
   `scripts/ollama_harness.py`'s `_dispatch_publish_bridge_verdict`
   (independently confirmed as a real, valuable, low-risk gap -- see
   Independent Technical Verification above) is orthogonal to the recovery-
   mechanism conflict and can proceed on its own merits. Prime should decide
   whether it ships as a narrow WI-5495 D-slice ahead of WI-5542, or is folded
   into WI-5542's proposal (which will already be touching the same function),
   to avoid a second touch to the same code region.
4. Restore `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and
   `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to `Specification Links` for
   consistency with earlier versions of this thread.
5. File the revision through a fresh `bridge_claim_cli.py claim`, `REVISED`
   status, and (after a fresh independent `GO`) a fresh implementation-start
   authorization packet before any further mutation of any target.

## Owner Decisions / Input

Not required for this verdict file (verdict files are excluded from the
Mandatory Owner Decisions / Input Section Gate). No new owner decision is
needed for this technical/backlog-sequencing correction; WI-5495 remains
within the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
authorization once refiled with a resolved scope.

## Prior Deliberations

- `DELIB-202666257`, `DELIB-202666266`, `DELIB-202666227`, `DELIB-202666174`,
  `DELIB-202666256` - independently re-confirmed present in the Deliberation
  Archive; carried forward from versions 001-006.
- `DELIB-202666850` ("Ollama D publisher-recovery fix needs graceful-
  exhaustion redesign, not a transport switch") - directly read in full for
  this review. This is the design-rationale deliberation behind version 006's
  own D-side mechanism; it predates and does not reference WI-5542, which is
  itself the more substantive successor to the direction this deliberation
  sketches.
- No prior Deliberation Archive record addresses the specific WI-5495-vs-
  WI-5542 backlog conflict identified in this verdict; semantic search for
  "publisher envelope recovery Ollama D JSON verdict no-tools" and "WI-5542
  WI-5495 conflict overlap" returned no on-point results. This verdict is the
  first durable record of that specific conflict-resolution finding.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
