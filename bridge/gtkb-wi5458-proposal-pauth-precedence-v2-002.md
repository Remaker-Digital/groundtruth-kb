NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: beb9672b-f0a6-4caf-8e51-925fdc3dfb49
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5458 PAUTH Precedence v2 - NO-GO (v2 chain, first proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md
Reviewed proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md

---

## Verdict Summary

**NO-GO** on one rule-mandated gate failure (F1) plus two substantive defects
(F2, F3) that are bounded and addressable in a single REVISED version.

**The v2 chain-reopen rationale is accepted and must not be re-litigated.**
`bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:18` reads
`Version: 007 (NEW; post-implementation report)` rather than the exact
`Version: 007` the strict lifecycle resolver requires. An append cannot repair
a strict prefix, so opening a clean v2 thread and retiring the old chain
append-only is the correct repair-forward move. The v008 findings F1 (no
validated `--project-authorization` selector) and F2 (expired status-active
PAUTHs remain eligible) are correctly carried into v2 sections 1-3 with an
explicit disposition table.

**Factual accuracy is unusually high and is credited.** Every checkable claim
verified: baseline commit `8317c8b17d00...` equals current `HEAD`; all three
declared-target SHA-256 values match byte-for-byte; the focused suite reports
20 collected with the single known `asyncio_mode` config warning; the PAUTH
envelope, scope, allowed classes, and forbidden operations match MemBase
exactly; all 17 linked specs and 4 cited DELIBs resolve. No inaccurate factual
claim was found.

---

## Findings

### FINDING-F1 (P1, BLOCKING) - Verification plan maps zero linked specifications; rule-mandated NO-GO

**Claim.** The Specification-Derived Verification Plan does not map any of the
17 linked specifications to a test.

**Evidence.** `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md:181-201`.
The plan's left column is thematic, not spec-keyed: `PAUTH envelope and
restrictive WI scope`, `Operation-time currentness`, `Explicit selector`,
`Deterministic ranking`, `Bridge and project linkage`, `Independent
verification`. I ran a spec-ID regex
(`\b(SPEC|GOV|DCL|ADR|PB)-[A-Z0-9-]+`) over that region: **0 matches**. By
contrast the predecessor that earned `GO` keyed every row to explicit
specification IDs at
`bridge/gtkb-wi5458-proposal-pauth-precedence-005.md:276-285`.

Specifications with no traceable verification row at all:
`ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
(v005 carried a dedicated parity row; v2 has neither a row nor a
`## Cross-Harness Disposition` section), `DCL-PROJECT-DEPENDENCY-ORDERING-001`,
`GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Impact.** `.claude/rules/file-bridge-protocol.md` Mandatory Specification
Linkage Gate is explicit: when "the proposed tests do not map back to the
linked specifications, the only valid verdict is `NO-GO`." Independently, a
thematic table leaves the verifying reviewer with no deterministic basis for
the report-stage spec-to-test mapping - which is precisely where v008 F2
landed last time. This is a regression against the standard the predecessor
`GO` accepted, not a new requirement.

**Recommended action.** Re-key the table to specification IDs using the v005
format. Grouping several IDs into one row is acceptable; omitting them is not.
Either add a parity row / `## Cross-Harness Disposition` section for the two
parity specs, or remove them from `## Specification Links` with a stated
reason.

---

### FINDING-F2 (P1, BLOCKING) - Section 5 create-missing-state preservation promise contradicts section 3 target-path evaluation

**Claim.** Section 5 promises to "Preserve the existing owner-approved
`--create-missing-state` route" while section 3 requires that "the exact
normalized proposal targets are evaluated." Both cannot hold.

**Evidence.**

- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md:145-150` (section 5
  preservation promise) and `:121-128` (section 3 target-path evaluation).
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:282-292` - the
  auto-created PAUTH is hardcoded
  `allowed_mutation_classes=["bridge", "metadata"]`.
- `groundtruth-kb/src/groundtruth_kb/project/project_authorization_operation_time.py:336-340`
  - `evaluate_envelope` denies with `target_mutation_class_not_allowed` for any
  classified target outside the allowed families.
- Same module `:173-178` and `:215-223` - `platform_tests/**` classifies as
  `test`; `groundtruth-kb/src/**` classifies as `source`. Neither is in
  the bridge/metadata pair.
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py:415-452` - the
  existing create-missing-state test passes target
  `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` (class `source`)
  and asserts `exit_code == 0`.

**Impact.** Under section 3 as written, the create-missing-state route becomes
non-functional for every source/test proposal - the overwhelming majority. The
currently-green test at `:415` must either change (a behavior change the
proposal does not disclose) or the gate must be weakened for that path, which
would violate `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
Required Executable Assertion 9 ("a bridge-and-metadata-only authorization
cannot authorize protected implementation"). The proposal asserts the opposite
at AC6 (`:217-218`) and AC7 (`:219`), and its v008 disposition table does not
mention this at all.

**Secondary defect, same root cause - side-effect ordering.**
`proposal_filing.py:254-261` writes `db.link_project_work_item` and `:282`
writes `db.insert_project_authorization` **before** `:263` resolves the
authorization. A currentness or target-class denial after those writes leaves
persistent MemBase rows behind. The section 4 no-side-effect invariant
(`:139-141`) enumerates only "proposal content, candidate preflights, bridge
writer calls, or bridge-file creation" - it excludes MemBase membership and
PAUTH creation. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
Required Executable Assertion 8 ("A denied request creates no claim, packet,
protected mutation...") is therefore not satisfied.

**Recommended action.** Add an explicit `## Create-Missing-State Disposition`
stating (a) what allowed mutation classes the auto-created PAUTH receives
under section 3 evaluation, or that the route is now denied for
non-bridge/metadata targets with a named recovery path; (b) that
`test_file_implementation_proposal_can_create_missing_state_with_owner_decision`
is expected to change, and how; (c) that membership and PAUTH creation move
after full envelope evaluation, or explicitly scope that out with rationale
against Assertion 8. Correct AC6/AC7 if the existing suite will not pass
unchanged.

---

### FINDING-F3 (P2, BLOCKING) - Candidate-pruning versus global-denial precedence is unspecified in the authority-broadening direction

**Claim.** Section 2 conflates two dispositions and never states which applies
to which failure class.

**Evidence.**
`bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md:96-114` opens by
requiring validation of "every candidate" across nine checks, including that
"every target path receives one canonical mutation class permitted by the
authorization; forbidden-operation precedence remains absolute" (`:108`). The
only explicit disposition rule given is `:110-111`: "**Expired and
already-superseded** status-active rows are removed from automatic candidate
ranking." Nothing states the disposition for a candidate that fails the
forbidden-operation or disallowed-target-class check. Two readings follow:

- *Prune-and-continue*: a PAUTH forbidding `bridge_proposal_filing` is dropped
  and a broader candidate is selected instead - converting an absolute deny
  into "try the next one," contradicting
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` Deterministic
  Precedence rule 1 and the proposal's own `:108`.
- *Deny-globally*: the whole filing fails - safe, but never stated, and
  section 3 (`:121-128`) implies envelope evaluation runs once on the
  *selected* authorization, i.e. after pruning.

**Impact.** Under the permissive reading this is an authority-broadening path -
exactly the defect class WI-5458 exists to close. The Risks section
(`:257-258`) acknowledges the shape ("Filtering stale rows could silently
choose broader authority") but offers disclosure as the mitigation rather than
a precedence rule.

**Recommended action.** State the outcome per failure class explicitly.
Recommended: prune only for expired and superseded; deny globally for
forbidden-operation, disallowed-target-class, unresolvable owner decision, and
malformed currentness. Add a fixture with one exact-singleton PAUTH that
forbids `bridge_proposal_filing` plus one broader eligible PAUTH, asserting
global denial rather than fallback selection.

---

### FINDING-F4 (P2, NON-BLOCKING) - Decision-evidence field set is narrower than the DCL it cites

`bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md:130-137` enumerates the
emitted decision object. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
Decision Evidence And Currentness additionally requires acting session and
role, bridge/work-item/spec identities, and invalidation inputs; its Required
Inputs section also names authorization status, expiration, supersession state,
and the owner-decision deliberation ID as bound inputs. None appear in the
emitted object - only as pass/fail predicates. The scoping caveat at `:56-58`
covers *cross-gate* parity (WI-5178), not *within-gate* evidence completeness
at the one enforcement point this slice owns.

**Recommended action.** Extend the section 4 field list, or explicitly enumerate
which DCL evidence fields are deferred to WI-5178 with a safety rationale.

---

### FINDING-F5 (P3, NON-BLOCKING) - Blast radius of the currentness filter is unquantified

I surveyed MemBase across all projects: **577 active PAUTHs, 21 of which carry
an expiry, with sampled expiry values all in the past** relative to
2026-07-28 (2026-06-12, 2026-06-27, 2026-07-03, 2026-07-05, 2026-07-18). Zero
active rows carry a supersession pointer; zero have missing or unresolvable
owner-decision deliberation IDs, so the owner-decision check at `:103` is
low-regression - itself worth stating. After this lands, proposal filing for
any work item covered only by one of those 21 rows fails closed. The
proposal's Authority Boundary (`:275-281`) forbids PAUTH mutation, so the
operator recovery route is not obvious from the text.

**Recommended action.** Add one line to Risks stating the measured count and
naming the governed recovery route (owner-approved PAUTH renewal or a new
bounded PAUTH), not a bypass.

---

## Positive Confirmations

- Both mandatory preflights pass on the operative file with zero blocking gaps
  and zero missing specifications.
- Existing call ordering already supports the section 4 invariant:
  `proposal_filing.py:710` (`_resolve_project_state`) precedes `:711`
  (`_build_content`), `:715` (candidate preflights), and `:728` (writer). The
  claimed no-side-effect placement is achievable without restructuring, except
  for the MemBase writes in F2.
- The restrictive-versus-inclusive spec-scoping reasoning at `:116-119` is
  correct and correctly deferred to WI-5178. The v2 PAUTH excludes no specs, so
  the proposal's own 17-spec set does not self-deny - a real trap the author
  avoided.
- Constraining the selector to best-rank candidates (`:91-92`, AC2 at
  `:207-209`) closes the obvious authority-bypass vector, with the tradeoff
  disclosed in Risks.
- Old-chain preservation is honest: versions 001-008 are clean in `git status`;
  no historical artifact was rewritten.
- WI-5458 v17 links only the v2 proposal as a related bridge thread, matching
  the stated continuation claim.

---

## Blocking Items For Prime Builder

1. **F1** - Re-key the verification table to specification IDs (v005 format at
   `bridge/gtkb-wi5458-proposal-pauth-precedence-005.md:276-285`). Every linked
   specification must appear in at least one row. Resolve the two parity specs
   by adding a row / `## Cross-Harness Disposition` section, or remove them
   with a stated reason.
2. **F2** - Add an explicit `## Create-Missing-State Disposition`; reconcile
   with Required Executable Assertion 9; correct AC6/AC7 if the existing suite
   will not pass unchanged.
3. **F2 (secondary)** - Move membership and PAUTH creation after full envelope
   evaluation, or state why MemBase writes are excluded from the
   no-side-effect invariant despite Required Executable Assertion 8. Extend the
   invariant sentence at `:139-141` accordingly.
4. **F3** - State per-failure-class disposition in section 2.
   Forbidden-operation and disallowed-target-class must deny globally, not
   prune.
5. **Fixtures implied by 2-4** - bridge+metadata-only PAUTH denies a
   source-target filing; a denied create-missing-state run leaves zero new
   MemBase rows; a forbidden-operation candidate denies globally rather than
   falling through to a broader PAUTH.

Non-blocking, fold into the same revision: F4 and F5.

---

## Scope Commitment

To prevent an open-ended review ratchet on this thread: once items 1-5 above
are addressed and the fixtures land, no further scope-completeness NO-GO will
be raised on this proposal absent **new evidence** - that is, a defect
demonstrable against live code or a cited specification clause, not a
restatement of preference. F4 and F5 are explicitly non-blocking and must not
be escalated in a later round.

---

## Applicability Preflight

- packet_hash: `sha256:a0367a921964ad7c6e7f84cc2c22a0be3e60945beeb5dfce5983a89d796e1c74`
- candidate_evidence_hash: `sha256:e05843c021d81f0f6ddd62227699f0a91725d4ec9f765f3c91509a10eef5a0bc`
- bridge_document_name: `gtkb-wi5458-proposal-pauth-precedence-v2`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md`
- preflight_passed: `true`
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5458-proposal-pauth-precedence-v2`
- Operative file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit code observed: `0`.

### Blocking Gaps

None. The clause preflight does not contribute to this NO-GO; findings F1-F3
are review-layer determinations under the Mandatory Specification Linkage Gate
and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`.

---

## Prior Deliberations

- `DELIB-20263760` - Loyal Opposition Review, Bridge Compliance Gate Work Item
  Project Membership Check. Establishes the project-membership validation
  posture this proposal extends.
- `DELIB-20264663` - Loyal Opposition Review, Project VERIFIED-Completion
  Owner-Confirmed AUQ Trigger. Relevant to project-authorization lifecycle
  currentness.
- `DELIB-20264465` - Loyal Opposition Review, Operating-Mode Transaction
  Component Slice 1 REVISED-1. Precedent for candidate-state validation before
  durable write.
- `DELIB-202665533` - Loyal Opposition Review, WI-5013 SoT Singleton GOV
  Foundation. Precedent for single-source authority resolution.
- Predecessor chain: `bridge/gtkb-wi5458-proposal-pauth-precedence-002.md`
  (deterministic precedence and fail-closed ambiguity), `-006.md` (GO;
  deferred explicit-selector and currentness risk to implementation
  verification), `-008.md` (NO-GO; F1 selector, F2 currentness).

---

## Review Methodology

- Read the full v2 proposal and the complete predecessor chain (001-009).
- Verified the malformed version-metadata line at
  `bridge/gtkb-wi5458-proposal-pauth-precedence-007.md:18` that motivates the
  v2 reopen.
- Verified baseline commit, all three declared-target SHA-256 digests, and
  `git status` cleanliness on the declared targets.
- Read current state of all three declared target paths, focusing on the filing
  request dataclass, the CLI option surface, candidate ranking, and
  create-missing-state ordering.
- Read `project_authorization_operation_time.py` classification and
  `evaluate_envelope` denial paths.
- Queried MemBase for the PAUTH envelope, all 17 linked specifications, the 4
  cited deliberations, and the active-PAUTH expiry survey (577 active, 21 with
  an expiry).
- Ran a spec-ID regex over the verification-plan region (0 matches).
- Ran `scripts/bridge_applicability_preflight.py` and
  `scripts/adr_dcl_clause_preflight.py` on the operative file.
- Ran deliberation search across project-authorization precedence and
  currentness topics.

## Review Independence

Reviewer session context `beb9672b-f0a6-4caf-8e51-925fdc3dfb49` (harness B,
Claude). Proposal author session context
`019f863a-acd3-7320-80c0-1831f0936cc0` (harness A, Codex). Distinct session
contexts; author metadata present and readable. Independence gate satisfied.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*
