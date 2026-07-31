REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; owner-directed newest-first bridge processing
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5765-lo-atomicity-suites-and-carrier-gate
Version: 009
Responds to: bridge/gtkb-wi5765-lo-atomicity-suites-and-carrier-gate-008.md
Date: 2026-07-30 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5765

target_paths: [".claude/hooks/bridge-compliance-gate.py", "config/hooks/gtkb-bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py"]

# WI-5765 REVISED — Split the Bridge-Only Carrier Gate from Blocked Atomicity Work

Scope confirmation: this proposal performs no MemBase mutation and no
`groundtruth.db` write. Its project, work-item, authorization, claim, and
bridge references are read-only authority evidence. TAFE and the dispatcher
remain deliberately disabled and outside scope.

## Revision Claim

This revision accepts v008's NO-GO on executable authority for the combined
v005 cohort. It removes the A1 atomicity-suite work and both A1 test targets
because the live `finalize_verified_commit` path publishes before commit.
Repairing those tests alone would therefore encode expectations that production
does not yet satisfy, while adding finalizer implementation targets would exceed
the reviewed cohort. Finalizer ordering remains routed to WI-5742, with WI-5666
as historical/adjacent lineage in a different project. That project's current
authorization is insufficient and non-controlling for this Advisory Corrections
thread, so WI-5666 cannot independently supply implementation authority here
under the owner-confirmed project-only model.

This v009 proposes only the already owner-adopted A7 bridge-only carrier gate
remedy. It does not reuse GO-006. Implementation requires a fresh independent
GO on this exact four-target revision, a fresh exact claim, a schema-v3
implementation-start packet, and a same-operation PAUTH/target/collision check.

## Project Authority

The controlling authorization remains active whole-project
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` v6, current row 944,
changed `2026-07-30T15:54:06+00:00` under `DELIB-202667710`. It is list-free and allows `source`,
`test`, `test_addition`, `configuration`, `metadata`, `governance_evidence`,
`bridge`, and `documentation`; it forbids dispatcher mutation, external-system mutation,
credential lifecycle, push, history rewrite, deployment, release, and
destructive cleanup. WI-5765 is open/backlogged and an active order-9 member of
active `PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729` v1. Its legacy per-WI
approval field is non-controlling under the owner's project-authority decisions.

## Findings Addressed

### v008 Disposition

Response: accepted in full. A1 is removed rather than executed under GO-006,
and no finalizer target is smuggled into this revision. A7 is split into a new
append-only proposal as v008 expressly permits. This cures the executable-scope
defect without weakening the commit-first decision or inventing authority for
WI-5666.

### A7 — Bridge-Only Carrier VERIFIED Evidence

The compliance gate currently requires a test-runner token for every VERIFIED
body, including bridge-only evidence carriers whose reviewed implementation
report changes only `bridge/**`. That class can truthfully provide exact git
provenance and governed applicability/clause preflights yet may have no
source-derived test to run.

Condition only the command-evidence limb of
`_has_spec_derived_verification` so non-test evidence is sufficient if and only
if all three conditions hold:

1. The thread's reviewed operative implementation report resolves
   deterministically.
2. Its `target_paths` parse cleanly, are non-empty, and every path is under
   `bridge/**`.
3. The VERIFIED body records executed governed applicability/clause preflight
   evidence plus exact git provenance (`git show` / `git diff-tree` class
   commands).

Absent, malformed, ambiguous, empty, or mixed/non-bridge target paths fail
closed and retain the existing test-runner requirement.
`COMMAND_EVIDENCE_RE` remains textually unchanged; preflight and git tokens are
not added globally. No per-thread owner waiver is introduced.

Apply the gate change to the canonical hook, its tracked byte-identical
`config/hooks/` activated copy, and the corresponding template region. Add the
focused regression cases to
`platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`. This
WI does not claim full template byte parity; unrelated template repair remains
in the WI-5764 lane. Codex hook adapters already invoke the canonical hook and
require no edit.

## Scope Changes

Compared with v005, this revision removes:

- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py`
- every A1 implementation step, A1 acceptance criterion, and A1 test command

The exact v009 cohort is the four A7 targets declared in `target_paths`. No
source finalizer, dispatcher, TAFE, MemBase, database, provider-specific
adapter, credential, release, or deployment target is added.

## Exact Target Preconditions And Collision Serialization

A fresh audit before drafting found all four target preimages clean in Git and
`git diff --check` clean. Their SHA-256 preimages were:

| Target | SHA-256 |
| --- | --- |
| `.claude/hooks/bridge-compliance-gate.py` | `7fd9d7f3f0f1cfaa8dbb125bb1d7b5b2020f5083dd8bef003a70548e08bf49b2` |
| `config/hooks/gtkb-bridge-compliance-gate.py` | `7fd9d7f3f0f1cfaa8dbb125bb1d7b5b2020f5083dd8bef003a70548e08bf49b2` |
| `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | `50aeed9c1d3aaf7da866f59f60b2deb265f6e158f95a6328a2cea6b762eb29d3` |
| `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py` | `f46c4b9c90e6a159f99530249de0ba64d7aa58da9530a565cc7d8e18ac16427d` |

The canonical and activated configuration hook preimages are byte-identical.

This proposal is fileable for review but is deliberately not implementation-
ready while the collision lane is unresolved:

- WI-5764's latest authoritative bridge status is GO at
  `bridge/gtkb-wi5764-wi5370-fabricated-closure-correction-006.md`; its v005
  cohort owns both `.claude/hooks/bridge-compliance-gate.py` and
  `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` and itself requires
  WI-5763 serialization before mutation.
- WI-5763's latest authoritative status is NO-GO at
  `bridge/gtkb-wi5763-governed-verdict-filing-path-004.md`; its original
  proposed cohort also named those two paths, but its latest NO-ACTION/NO-GO
  chain supplies no implementation authority.
- Project order is WI-5763 order 7, WI-5764 order 8, WI-5765 order 9.

Therefore WI-5765 implementation must not overtake WI-5764. Before any start,
WI-5764 must have released the two shared targets through completed/terminal or
formally revised scope, WI-5763 must no longer create an active conflicting
cohort, and a fresh claim/status/Git check must show the four-target set clean.
If either shared target's preimage changes, PB must rebase the exact A7 change
and test expectations on the resulting content before start. A collision or a
required fifth target is a stop condition, not permission to force through.

The drafting claim was acquired by session
`019fb1f2-2f91-7b82-ac15-acdd56e13d1e` as draft claim row 35028 at
`2026-07-30T16:08:09Z`; it is drafting evidence only and cannot authorize
protected-target mutation.

## Cross-Harness Disposition

| Harness or surface | Disposition |
| --- | --- |
| Claude / canonical workspace hook | `.claude/hooks/bridge-compliance-gate.py` is the canonical behavioral implementation and an exact target. |
| Codex | Existing `.codex/gtkb-hooks/bridge-compliance-gate*.py\|.cmd` adapters invoke the canonical hook; behavior changes by reference and adapter bytes remain unchanged. |
| Cursor and Antigravity | No separate registered implementation of this predicate is introduced; both consume governed bridge artifacts under the canonical workspace gate. |
| Ollama, OpenRouter, Goose, and Alibaba Cloud Studio | No provider-specific prompt, route, hook copy, dispatcher setting, or TAFE setting changes. |
| Activated configuration copy | `config/hooks/gtkb-bridge-compliance-gate.py` receives the byte-identical canonical change. |
| Scaffold/template | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` receives the corresponding logical change without claiming unrelated full-template parity. |
| Regression suite | The single `platform_tests/**` target exercises the canonical predicate; no harness-specific bypass or waiver is used. |

Discovery of another registered implementation of this predicate is target
scope drift and stops implementation for a fresh append-only revision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge role authority and governed verdict publication.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — truthful spec-derived evidence and fail-closed VERIFIED behavior.
- `GOV-10` — tests exercise the exposed compliance-gate behavior.
- `GOV-12` — WI-5765 drives the focused regression cases.
- `GOV-17` — protected hook changes require governed proposal/review evidence.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — preserve mechanical enforcement rather than relying on prose waiver.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — maintain canonical/config/template surface discipline.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex adapters continue routing to the canonical hook.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — current project authorization is the controlling implementation envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — project authorization does not replace fresh bridge review.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — revalidate PAUTH, claim, targets, and proposal at every operation gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the Project/WI/PAUTH linkage is explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant governing links are carried here.
- `GOV-STANDING-BACKLOG-001` — WI-5765 remains the MemBase work authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — authority, chain, membership, targets, and claim state were freshly checked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets remain inside the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory-to-WI-to-proposal lifecycle and durable carrier evidence.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` — the owner adopted the A7 disposition before implementation routing.

## Prior Deliberations

- `DELIB-202667531` — routes fix-class advisories into the Advisory Corrections project while preserving item bridge gates.
- `DELIB-202667533` — selects AT-01 commit-first ordering and establishes the PROGRAM project authorization.
- `DELIB-202667534` — routes A1 and A7 to WI-5765 and adopts the A7 target-path-conditioned bridge-only evidence remedy.
- `DELIB-202667710` — reissues PROGRAM PAUTH v6 with documentation class for the WI-5763 terminology target while preserving v5 scope, bans, and item gates.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — implementation approval is inherited from the parent project; orphan WIs cannot implement.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — legacy per-WI approval state is non-controlling.
- `bridge/gtkb-lo-verified-finalization-toolchain-drift-advisory-001.md` — source advisory for the A7 finding and finalizer sequencing.
- `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-010.md` — governed bridge-only carrier exemplar and adjacent-suite workaround evidence.

## Owner Decisions / Input

No new owner decision is required to file or review this A7-only revision. The
owner already adopted A7 in `DELIB-202667534`, approved the parent project, and
confirmed project-only inheritance. The revision does not authorize WI-5666,
override project order, waive collision checks, or expand the implementation
envelope.

## Requirement Sufficiency

Existing requirements are sufficient. This revision narrows the cohort to the
already-decided A7 remedy and preserves the existing truthful VERIFIED-evidence,
cross-harness enforcement, bridge review, and project-authorization contracts.
A new formal specification would duplicate those controls.

## Pre-Filing Preflight Subsection

The governed candidate applicability preflight was executed against this draft
with the following result:

- most_recent_pre_evidence-update_packet_hash: `sha256:81d6f9e1d2d1c03d64926382e80f55b3b1b24b4bd2988d8c789602546c01cf56`
- packet_hash_schema_version: `3`
- most_recent_pre_evidence-update_source_content_hash: `sha256:4297f144c9025ab33bba000da634b0fbdb43be685ea98a8bba147f01c2f7bf46`
- rules_content_hash: `sha256:9ac027740dc91449b6a7ca402634d9047f130979f09df597ef1978c9031b5281`
- bridge_document_name: `gtkb-wi5765-lo-atomicity-suites-and-carrier-gate`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5765-lo-atomicity-suites-and-carrier-gate-009.md`
- source_identity: `bridge/gtkb-wi5765-lo-atomicity-suites-and-carrier-gate-008.md` (`NO-GO`, version 8)
- declared_target_paths: the exact four paths in the header
- project_authorization_operation_time: `allowed`; active authorization
  version `6`; requested operations `implementation_packet_create` and
  `implementation_start`; mutation classes `configuration`, `source`, and
  `test`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- author_metadata_warnings: `[]`
- unclassified_target_paths: `[]`

The packet and source hashes above identify the most recent passing candidate
immediately before those values were embedded. Embedding a candidate hash
necessarily changes the candidate bytes; the governed filing helper must rerun
the preflight on the exact filing payload and use that final output rather than
treating this self-referential evidence line as the filing hash.

The mandatory ADR/DCL clause preflight evaluated five clauses: four
`must_apply`, one `may_apply`, zero `not_applicable`; it found zero evidence
gaps in must-apply clauses and zero blocking gaps (exit 0). Evidence was found
for:

- `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`

The may-apply clause was
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`; it produced no blocking
gap.

## Complete Specification-Derived Verification Plan

1. **Bridge-only carrier accepts governed non-test evidence.** Add a fixture
   whose deterministically resolved reviewed implementation report declares
   only `target_paths: ["bridge/<slug>-NNN.md"]`. A VERIFIED body containing
   concrete specification links, executed applicability/clause preflight
   evidence, and `git show` / `git diff-tree` provenance, but no test-runner
   token, must pass the spec-derived-verification predicate.
2. **Source-bearing and mixed carriers remain denied.** A negative twin with
   any non-bridge target must retain the existing test-runner requirement.
3. **Malformed authority fails closed.** Missing, empty, malformed, ambiguous,
   or unresolvable `target_paths` and unresolved/multiple operative reports must
   receive no exemption.
4. **No global regex weakening.** Assert that `COMMAND_EVIDENCE_RE` remains
   textually unchanged and does not gain preflight or git tokens.
5. **Projection discipline.** Assert canonical and `config/hooks/` hook copies
   are byte-identical after the edit and that the corresponding logical region
   exists in the template without claiming unrelated template parity.
6. **Focused execution.** Run
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -q`.
7. **Static and scoped checks.** Run Ruff check and format-check over the exact
   four Python targets, `git diff --check`, and `git status --short -- <four
   targets>`; the implementation report must record exact commands and results.

## Acceptance Criteria

1. Only a deterministically resolved all-bridge carrier receives the governed
   non-test evidence path.
2. Mixed, source-bearing, absent, empty, malformed, ambiguous, or unresolvable
   target metadata fails closed and retains the test-runner requirement.
3. `COMMAND_EVIDENCE_RE` remains globally and textually unchanged.
4. Canonical/config activated gate copies are byte-identical; the corresponding
   template region is updated without unrelated full-template scope expansion.
5. Focused regression and Ruff checks pass, and the implementation report maps
   every acceptance criterion to executed evidence.
6. WI-5764 and its transitive WI-5763 serialization are cleared before start;
   no active foreign claim, dirty target, or stale preimage is overridden.
7. PB requests independent VERIFIED review and does not self-author a terminal
   status.

## Risks, Stop Rules, And Rollback

Risk is low-to-medium: the intended exception is narrow, but overly broad
carrier recognition could let source-bearing work bypass mandatory tests. The
design therefore defaults to denial unless operative-report resolution and
all-bridge `target_paths` are exact and the VERIFIED body carries both governed
preflight and git-provenance evidence.

Stop immediately if PAUTH v6 changes, expires, or is superseded; project
membership changes; WI-5763/WI-5764 collision state remains active; another
claim exists; a target preimage or Git cleanliness changes without rebasing;
the gate would need heuristic report resolution; `COMMAND_EVIDENCE_RE` would
need alteration; or any fifth target becomes necessary. Route expansion through
a fresh append-only revision.

Rollback is a scoped revert of only the four-target implementation cohort after
governed review. Bridge history remains append-only. No dispatcher or TAFE
activation/configuration/mutation, external-system action, credential action,
push, history rewrite, deployment, release, or destructive cleanup is allowed.

Recommended commit type: fix

## Verification Questions for Loyal Opposition

1. Does v009 correctly accept v008 by removing A1 and refusing to reuse GO-006?
2. Are the A7 carrier conditions narrow and fail-closed enough to preserve the
   mandatory test requirement for any non-bridge implementation?
3. Does the explicit WI-5764/WI-5763 serialization prevent the four-target
   cohort from overtaking current project work?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
