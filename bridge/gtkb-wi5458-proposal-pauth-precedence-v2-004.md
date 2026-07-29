NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: af8deadc-ebed-461b-994a-6f40241e0f39
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5458 Proposal PAUTH Precedence v2 - NO-GO (second revised proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 004
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-003.md
Reviewed proposal: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-003.md

---

## Verdict Summary

**NO-GO** on one blocking finding that is new in version 003 and demonstrable
against live code, plus one blocking regression against version 001.

**Four of the five version 002 findings are genuinely closed**, including both
P1s, and the closures are real design changes rather than rewording. The
specification-to-verification re-keying is complete and mechanically checkable.
The side-effect-ordering fix addresses a confirmed live defect. The
prune-versus-deny disposition table implements version 002's own recommended
remedy verbatim. Both mandatory preflights pass. Every claim version 003 makes
about live code that this review checked is accurate, and version 003 corrects a
module-path error that version 002 itself made.

What blocks GO is that the new section 4 resolves version 002's F2 contradiction
by **widening** the auto-created authorization, and the widening opens a
privilege-escalation path into the implementation-start gate. That is a defect
demonstrable against live code and against a cited specification clause, so it
falls squarely inside the exception version 002's Scope Commitment reserved.

---

## Blocking Findings

### F1 (P1) - Deriving auto-PAUTH mutation classes from filer-supplied targets creates a privilege-escalation path

**Claim.** Section 4 at
`bridge/gtkb-wi5458-proposal-pauth-precedence-v2-003.md:120-124` specifies that
the `--create-missing-state` auto-created authorization receives allowed classes
of `bridge`, `metadata`, "plus only the canonical classes required by the exact
targets", and states explicitly that "For the existing source-target fixture
that means `source` is present." The exact targets are the filer's own
`--target-path` arguments. The authorization's privilege boundary is therefore
defined by the same actor it is meant to bound.

**Evidence - the current backstop being removed.**
`groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:291` hardcodes
`allowed_mutation_classes=["bridge", "metadata"]` on the auto-created
authorization. That constant is today's fail-closed guarantee that a
self-service filing cannot mint source or test authority. Version 003 replaces
the constant with a derived set.

**Evidence - the downstream gate that consumes it.** The auto-created
authorization is persisted at `proposal_filing.py:282-292` and thereafter is a
covering authorization for that work item.
`scripts/implementation_authorization.py` gates the implementation-start packet
on exactly these classes, and
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
denies via its target-mutation-class path when a classified target falls outside
`allowed_mutation_classes`. Widening the minted set therefore widens what the
implementation-start gate will later admit.

**Evidence - the owner-decision check is not a compensating control.**
`groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py:207-211` is the
whole of `_require_owner_decision`: it requires the argument to be present and
requires `db.get_deliberation(delib_id)` to resolve. It validates **existence,
not scope**. No check ties the deliberation's content to the classes being
granted. Under version 003, any resolvable deliberation identifier plus a
self-chosen target set mints an `active` authorization carrying `source` and
`test`.

**Evidence - the cited specification clause.**
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` requires that every
required mutation class is authorization-allowed and every target is
proposal-approved, with **neither boundary permitted to broaden the other**, and
its deterministic precedence holds that authorization scope never broadens the
reviewed proposal's exact target paths. Deriving the authorization's classes
*from* the proposal's targets is that prohibited coupling, running in the
reverse direction. The same DCL requires manual authorization creation and
`--create-missing-state` to produce equivalent envelopes; a manual envelope's
classes come from the owner, whereas a derived envelope's come from the filer's
CLI arguments, which is not equivalent.

**Risk / impact.** This converts a two-gate fail-closed path - bridge `GO` **and**
authorization class coverage - into a one-gate path, in precisely the defect
class WI-5458 exists to close. The over-broad authorization also persists as a
ranking candidate for every later filing on that work item, so the widening is
durable rather than per-invocation.

**Recommended action.** Do not derive allowed classes from filer-supplied
targets. Either:

1. Keep the auto-created envelope bridge-and-metadata-only, and state plainly
   that a source or test proposal filed through `--create-missing-state` must
   obtain an owner-scoped authorization before `implementation_authorization.py
   begin`. This is the current fail-closed behavior, made explicit and given a
   named recovery route; or
2. Require the owner-decision deliberation itself to carry the class grant, and
   validate the derived set against it - with a negative fixture proving that a
   deliberation granting no `source` cannot produce a `source`-class
   authorization.

Either way, reconcile the section explicitly against the neither-boundary-broadens
assertion and the precedence rule above, not only against the least-privilege
assertion version 003 currently cites.

**Scope-Commitment note.** Version 002 barred further scope-completeness `NO-GO`
absent new evidence - a defect demonstrable against live code or a cited
specification clause. This finding is both, and it arises from section 4, which
did not exist in version 001. It is not a restatement of preference, and it is
the only finding in this verdict that reaches the new-evidence bar on its own.

### F2 (P2) - The revision deleted a safety deferral that version 002 positively credited

**Claim.** Version 001 stated explicitly that this work item does not invent a
restrictive `included_spec_ids` interpretation, deferring inclusion semantics to
WI-5178. Version 002 credited that reasoning as a positive confirmation and named
the trap it avoided. That paragraph is absent from version 003; the only
remaining treatment is an ambiguous disposition-table row reading "WI/spec
exclusion or non-covering row - Not eligible - Deny".

**Evidence.** The cited authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718` carries
twelve `included_spec_ids` and a null `excluded_spec_ids`, while the proposal
links seventeen specifications. Five linked specifications are not in the
included set, and one of those five is
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the central
specification of this work item. Current live semantics are exclusion-only, so
the gap is presently harmless; but version 003 no longer says so, and
`DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` establishes a restrictive
precedent for the sibling field.

**Risk / impact.** An implementer reading the ambiguous row as restrictive
inclusion would build a gate that denies this very proposal's filing on its own
governing DCL. Silent removal of previously-credited safety text is a regression
against version 001, and it is the kind of removal a revision diff makes easy to
miss.

**Recommended action.** Restore an explicit sentence: `included_spec_ids` is not
restrictive at this gate, only `excluded_spec_ids` denies, and restrictive
inclusion semantics remain owned by WI-5178. Add a fixture pinning that an
authorization whose included set is a strict subset of the proposal's linked
specifications still permits filing.

---

## Non-Blocking Findings

**N1 (P2) - Malformed-currentness denial has no defined expiry grammar.** The
disposition table makes malformed currentness a global no-fallback denial, but
version 003 never states the accepted `expires_at` grammar. A live survey of
active authorization rows finds two ISO-8601 spellings in use - a `Z` suffix and
a `+00:00` offset - and the current envelope evaluator does not parse
`expires_at` at all, so the parser is entirely new code with no precedent to
inherit. A `Z`-only parser would turn a future-dated, currently-valid
authorization into a hard denial on formatting variance rather than on an
authority defect. State the grammar - accepting both spellings - and add fixtures
for each plus one genuinely malformed value.

**N2 (P2) - Prune-then-rerank can still promote broader authority.** Pruning a
well-formed expired top-rank candidate promotes a lower-specificity fallback to
selected, so bounded authority can silently expire into blanket authority. The
relevant precedence rule holds that project membership never substitutes for
explicit current authorization coverage. **This does not on its own force
`NO-GO`**: version 003 implemented version 002's recommended remedy verbatim, and
re-opening it as a fresh blocker would be exactly the ratchet the Scope
Commitment forbids. Fold in as a one-line rule during the F1 revision - pruning
may not lower the selected candidate's specificity rank, and if the best-rank
cohort is emptied by pruning, deny globally with the stale-authorization recovery
message - plus a fixture pairing an expired exact-singleton with a current
membership fallback.

**N3 (P3) - Four of nine deny conditions are unlocalized.** Section 3 names the
envelope evaluator as the evaluation mechanism. Verified live, that evaluator
implements the forbidden-operation, unknown-operation, missing-classes, and
target-class denials, but implements none of currentness and expiry,
supersession, owner-decision resolution, cross-project match, work-item coverage,
or invalidation inputs. Name the module that will own currentness so the verifier
can map the remaining conditions to code.

**N4 (P3) - A fixture named in version 001 was lost in the re-key.** Version 001
named lower-rank rejection tests; the version 003 verification table enumerates
exact-singleton, bounded multi-work-item, unrestricted fallback, explicit
exclusion, cross-project, unknown, and equal-rank fixtures, with no
lower-rank-rejection fixture, although the acceptance criterion still asserts the
behavior. Restore it to the table.

**N5 (P3) - No `## Owner Decisions / Input` section.** Confirmed absent. Version
003 does not cite the AskUserQuestion-only rule, and its owner-decision references
describe runtime feature behavior rather than this proposal's own approval
dependency, so the conditional gate does not fire. Version 002 did not raise this
against version 001. **Explicitly non-blocking** and recorded for the record only;
raising it as a gate now would be the ratchet the Scope Commitment forbids.

**N6 (P3) - Half the verification rows are structural.** Four of eight rows assert
bridge and backlog state queries, chain preservation, existing-fixture
preservation, and worktree cleanliness; none would fail if the precedence rule
regressed. The other four are genuinely behavioral, and one in particular - the
row enumerating active, expired, superseded, malformed-currentness,
unresolvable-owner-decision, forbidden-operation, disallowed-target-class,
narrow-deny-plus-broad-fallback, and invalidation-input fixtures, each asserting
zero side effects - is a real regression net. Grouping was explicitly permitted by
version 002. Non-blocking.

**N7 (P3) - One required input still missing from the decision-evidence set.** The
DCL names bridge document, **latest status**, and reviewed proposal version;
version 003 supplies a bridge slug and version candidate without latest status.
Fold in.

---

## Version 002 Closure Audit

| From 002 | Finding | Closed | Evidence |
|---|---|---|---|
| F1 (P1) | Verification plan mapped zero of 17 linked specs | **YES** | Every row re-keyed to specification identifiers. The links block contains 17 identifiers and each appears in exactly one of the 8 rows, verified by count rather than impression. A cross-harness disposition section was added, satisfying the parity-specification alternative. All 17 resolve live. |
| F2 (P1) | Section 5 preservation contradicted section 3 exact-target evaluation | **NO - relocated, not resolved** | Resolved by widening the auto-created authorization. See F1 above. |
| F2 secondary (P1) | Membership and authorization writes execute before authorization resolution | **YES** | Live defect confirmed at `proposal_filing.py:254` and `:282`, both preceding resolution at `:263`. Version 003 moves both behind complete in-memory validation, extends the no-side-effect invariant to name membership and authorization insertion explicitly, and backs it with acceptance criteria and negative fixtures. A real design change. |
| F3 (P2) | Prune-versus-deny precedence unspecified in the broadening direction | **YES** | A nine-row disposition table, with forbidden operation and disallowed target class both denying the whole request rather than falling back to a broader authorization, plus an explicit dominance sentence and a named fixture. This is version 002's own recommended remedy. Residual noted at N2, not treated as re-opening. |
| F4 (P2, non-blocking) | Decision-evidence field set narrower than the DCL | **PARTIAL** | Acting session and role, bridge/work-item/specification identity, authorization status, expiry and supersession, owner-decision identifier, and invalidation inputs are now carried. One required input remains absent; see N7. |
| F5 (P3, non-blocking) | Blast radius unquantified | **YES** | The measurement is recorded with a governed renewal recovery route and no stale-row bypass. Independently re-measured live: 578 active authorizations, 21 carrying an expiry, 0 superseded. The single-row drift from version 002's figure is the newly-created WI-5714 authorization, not an error. |

---

## Positive Confirmations

Verified against live state; do not re-derive in revision.

1. **Both mandatory preflights pass** on the version 003 operative file. The
   applicability preflight reports `preflight_passed: true` with empty
   missing-required, missing-advisory, and blocking-error lists, and the clause
   preflight exits 0 with zero blocking gaps.
2. **Version 003 corrects a module-path error made in the version 002 verdict.**
   Version 002 cited the operation-time module under a `project/` directory; the
   module actually lives under `governance/`. Version 002's line numbers were
   correct against the real file - only the directory was wrong. Credit to
   version 003; the correction is recorded here against version 002.
3. **All seventeen linked specifications resolve live**, and all seven cited
   deliberations resolve.
4. **Every claim about live code that this review checked is accurate.** The
   hardcoded bridge-and-metadata grant exists where stated; the membership and
   authorization writes do precede resolution; the create-missing-state fixture
   does pass a source-class target and assert success; and the filing module does
   not currently call the envelope evaluator anywhere. **No false live-state
   assertion was found.** F1 is not a factual dispute - it is a disagreement about
   what the correctly-described change should be.
5. **The baseline is still valid.** Repository `HEAD` matches the declared
   baseline commit, and all three declared targets are clean in `git status`.
6. **The cited authorization envelope matches MemBase exactly**, including its
   exact-singleton work-item scope, absent expiry and supersession, allowed
   classes, and forbidden operations. Its `excluded_spec_ids` is null, so the
   proposal does not self-deny under current exclusion-dominant semantics.
7. **Required sections are otherwise complete**: specification links, a non-empty
   prior-deliberations section with eight entries, requirement sufficiency with
   exactly one operative state, a recommended commit type, inline-JSON target
   paths, a spec-derived verification plan, and the full project-linkage triple.

---

## Cross-Thread Coordination

Declared `target_paths` were intersected against both other currently-live
threads. **Both intersections are empty.**

- Against `gtkb-wi5714-registry-write-linearizability`: empty.
- Against `gtkb-wi5679-session-role-keying-continuity` version 011, which
  received `GO` at version 012 earlier in this run: empty. Note in particular
  that the WI-5679 test targets sit under `platform_tests/hooks/` and
  `platform_tests/scripts/`, whereas this proposal's test target sits under
  `platform_tests/groundtruth_kb/`.

No implementation-start packet collision and no shared-module merge hazard. One
non-blocking substrate note: WI-5714 hardens the registry control plane against
concurrent read-modify-write, whereas this proposal's writes go to MemBase, so
the linearizability defect that thread addresses does not apply to this
transaction.

---

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - the owner decision
  behind the cited authorization. Confirmed present.
- `DELIB-20266083`, `DELIB-20263760`, `DELIB-20264663`, `DELIB-20264465`,
  `DELIB-202665533`, and
  `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - the remaining
  cited deliberations, all confirmed present.

No prior deliberation adjudicates the derived-class question raised in F1, and no
previously-rejected approach is being silently revisited. F2 concerns text
removed from this thread's own version 001 rather than a prior deliberation.

---

## Review Independence

Reviewer session context `af8deadc-ebed-461b-994a-6f40241e0f39` is distinct from
the reviewed artifact's author session context
`019f863a-acd3-7320-80c0-1831f0936cc0`. Author metadata is present and readable;
the independence gate is satisfied on evidence rather than by assumption.

---

## Methodology Trail

Bridge files read: versions 001, 002, and 003 of the v2 chain in full - version
001 specifically to establish what the revision removed, which is the source of
F2 and N4 - plus enumeration of the earlier non-v2 chain.

Source modules inspected:
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
in full, confirming the evaluator's actual decision surface and the absence of any
currentness evaluation;
`groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py` across its
candidate-ranking, owner-decision, and create-missing-state regions;
`scripts/implementation_authorization.py` across its packet-gating region,
establishing the downstream half of F1; and
`platform_tests/groundtruth_kb/test_cli_bridge_propose.py` for the
create-missing-state fixture's target class and exit assertion.

Repository-wide searches for envelope-evaluator consumers and for
`included_spec_ids` and `excluded_spec_ids` enforcement.

Read-only MemBase queries for the full text of
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` including its required
inputs, deterministic precedence, mandatory enforcement points, and executable
assertions; existence and status of all seventeen linked specifications;
existence of all seven cited deliberations; the cited authorization's full
envelope; and an all-projects survey of active authorizations for the
blast-radius re-measurement and the expiry-format census.

Both mandatory preflights run directly by this reviewer against the operative
file. Baseline commit and per-target `git status` verified. Target-path
intersections computed against both concurrent threads.

Not run: the focused pytest suite, because version 003 is a pre-implementation
proposal with no implementation to exercise and version 002 already established
the fixture baseline; and the implementation-start packet command, which would
create an authorization packet and is a mutation.

No file was created, modified, or deleted in the reviewed scope.

---

## Applicability Preflight

- packet_hash: `sha256:3c7910b5c3555eae39c97034c2e865bbe683bfc49d1fcd42b42fadc131542e7b`
- candidate_evidence_hash: `sha256:ee58be3aaf7880a826b3326740c2d969ea402f77465109ebbde551f76ac99a96`
- bridge_document_name: `gtkb-wi5458-proposal-pauth-precedence-v2`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-003.md`
- operative_file: `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5458-proposal-pauth-precedence-v2`
- Operative file: `bridge\gtkb-wi5458-proposal-pauth-precedence-v2-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

Both mandatory preflights pass. This `NO-GO` rests on a live-code and
specification-clause finding, not on a mechanical preflight gap.

---

## What Revision Requires

Only F1 and F2:

1. Stop deriving auto-created authorization classes from filer-supplied targets.
   Choose one of the two remedies in F1, and reconcile the section against the
   neither-boundary-broadens assertion and the precedence rule, not only against
   least privilege (F1).
2. Restore the non-restrictive `included_spec_ids` sentence and add the
   strict-subset fixture (F2).

Fold in N1's expiry grammar, N2's specificity-rank rule, N3's currentness module
name, N4's restored fixture, and N7's latest-status input while revising. N5 and
N6 are recorded for the record and are not gates.

Everything else in version 003 is accepted and carries forward unchanged: the
specification-to-verification re-key, the side-effect-ordering fix, the
prune-versus-deny disposition table, the decision-evidence expansion, the
blast-radius measurement, and the module-path correction.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
