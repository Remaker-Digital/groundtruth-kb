REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5458 v2 - Validated Proposal PAUTH Selection And Currentness - Second Revision

bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence-v2
Version: 005
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-v2-004.md
Date: 2026-07-29 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This proposal performs no MemBase mutation.
This implementation performs no mutation of the live `groundtruth.db` or live
MemBase. It changes only the three declared source/test files. Membership and
PAUTH transaction behavior is exercised solely against isolated test databases;
the production command may perform those governed transactions only when a
future user invokes it under its own authority.

## Claim

Implement the remaining WI-5458 proposal-filing repair in exactly three files.
The canonical command gains a validated explicit project-authorization selector,
validates currentness before ranking, applies global-denial precedence without
fallback broadening, and emits complete machine-readable decision evidence.

The `--create-missing-state` route remains fail-closed: it may create only a
bridge-and-metadata authorization, never derive source or test authority from
filer-supplied target paths, and therefore denies a source/test proposal until
an owner-scoped authorization already covers those exact classes. The old
structurally invalid bridge chain remains untouched; this strict-valid v2 chain
is the sole executable continuation.

## Requirement Sufficiency

Existing requirements are sufficient. This revision does not invent a new
authorization model. It makes the current operation-time contract executable at
the proposal-filing enforcement point and preserves the two independent
boundaries: reviewed proposal targets cannot broaden authorization classes, and
authorization classes cannot broaden reviewed target paths. WI-5178 retains
cross-gate parity and any future restrictive `included_spec_ids` semantics.

## Current Evidence

- The three declared targets are clean and retain the v001 baseline SHA-256 values.
- The focused baseline command passed `20 passed, 1 warning in 9.26s`; the warning is the pre-existing unknown pytest `asyncio_mode` option.
- The cited exact-singleton PAUTH remains the WI-5458 carrier and prohibits dispatcher/TAFE mutation, Git commit/push, external mutation, deployment, release, credentials, and destructive cleanup.
- The latest chain is `NEW -> NO-GO -> REVISED -> NO-GO`; no protected implementation or implementation-start packet exists for this v2 thread.

## NO-GO v004 Finding Disposition

| Finding | Revision disposition |
|---|---|
| F1, filer-derived auto-PAUTH classes | Removed. Auto-created PAUTHs remain exactly `bridge` and `metadata`. Any source/test active target denies before membership or PAUTH insertion and names the owner-scoped PAUTH recovery route. |
| F2, lost specification-inclusion deferral | Restored explicit exclusion-only semantics for this gate: `included_spec_ids` is recorded but non-restrictive, while `excluded_spec_ids` denies. Added the strict-subset success fixture; WI-5178 retains restrictive-inclusion ownership. |
| N1, expiry grammar | Defined timezone-aware ISO-8601 acceptance for both `Z` and `+00:00`, with fixtures for both and malformed/naive denial. |
| N2, stale pruning broadens rank | Ranking fixes the best specificity cohort before currentness pruning. If that cohort is emptied, the request denies; it never falls to a broader rank. |
| N3, currentness ownership | Named `groundtruth_kb.bridge.proposal_filing` as the filing-local currentness owner for this bounded slice and WI-5178 as the later shared-evaluator owner. |
| N4, lower-rank selector fixture | Restored explicit lower-rank selection rejection to the behavioral test matrix. |
| N7, latest status evidence | Added latest bridge status and reviewed proposal version to required decision evidence and invalidation inputs. |

N5 and N6 were explicitly record-only observations. This revision nevertheless
adds an Owner Decisions section; the accepted specification mapping and its
structural rows carry forward unchanged.

## Proposed Implementation

### 1. Validated explicit selector

Add `--project-authorization <PAUTH-ID>` to
`gt bridge file-implementation-proposal` and carry it through
`FilingRequest`, resolution, generated proposal metadata, `FilingResult`, JSON
output, and text output.

Automatic deterministic ranking remains the default. An explicit selector may
choose only among equally best-ranked current covering candidates. It cannot
select a lower-specificity or broader authorization while a more-specific
candidate exists.

### 2. Currentness grammar and fixed-rank precedence

`groundtruth_kb.bridge.proposal_filing` owns the bounded filing-local
currentness parser and candidate disposition in this WI. `expires_at` must be a
timezone-aware ISO-8601 instant; both `YYYY-MM-DDTHH:MM:SSZ` and an explicit
offset such as `YYYY-MM-DDTHH:MM:SS+00:00` are accepted and normalized to UTC.
A naive timestamp, invalid calendar value, unsupported suffix, or parse failure
is malformed currentness and denies the entire request.

Determine the structurally covering candidates and their specificity ranks
before pruning. Fix the best rank from that set. Within the best-rank cohort,
well-formed expired or superseded rows are disclosed and removed. If at least
one current candidate remains at that same rank, ranking continues only inside
the cohort. If none remains, deny globally with the stale-authorization recovery
route. Never fall through to a lower-specificity candidate.

Apply these outcomes exactly:

| Candidate condition | Automatic mode | Explicit selector |
|---|---|---|
| Well-formed expired/superseded row outside best cohort | Disclose; never eligible to lower the fixed best rank | Deny if selected |
| Well-formed expired/superseded row in best cohort | Prune within cohort; deny if cohort empties | Deny selected stale row |
| Unknown row or cross-project row | Not eligible | Deny |
| Excluded or non-covering work item | Not eligible | Deny |
| Linked specification intersects `excluded_spec_ids` | Deny whole request | Deny |
| `included_spec_ids` is a strict subset of linked specs | Permit; record set for evidence | Permit; record set for evidence |
| Malformed currentness | Deny whole request | Deny |
| Missing or unresolvable owner decision | Deny whole request | Deny |
| Forbidden requested operation | Deny whole request; do not try broader PAUTH | Deny |
| Disallowed canonical active-target class | Deny whole request; do not try broader PAUTH | Deny |
| Missing or inconsistent invalidation input | Deny whole request | Deny |

Exclusions and forbidden operations remain dominant. At this filing gate,
`included_spec_ids` is intentionally non-restrictive and evidence-only; only an
intersection with `excluded_spec_ids` denies. Restrictive specification-
inclusion semantics remain WI-5178 scope so this slice cannot make its own
proposal self-deny on five linked specifications absent from the carrier's
included set.

### 3. Canonical operation and active target evaluation

Reuse
`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`
and its root-bound target classifier. The operation is
`bridge_proposal_filing`. Normalize and classify every active proposal
`target_paths` entry before project-state mutation, content construction,
candidate preflights, writer invocation, or bridge publication. Every active
target class must already be allowed by the selected current authorization.
No second operation or mutation-class taxonomy is introduced.

### 4. Create-Missing-State Disposition

The auto-created envelope remains exactly bridge-and-metadata-only:

1. Resolve the owner-decision deliberation and approved linked specifications in memory.
2. Normalize and canonically classify every active target path in memory.
3. If any active target class is outside `bridge` and `metadata`, deny before membership or PAUTH insertion. The recovery message directs the operator to obtain an owner-scoped bounded PAUTH granting the required exact classes, then rerun the filing command.
4. If every active target is bridge/metadata class, construct an in-memory exact-WI candidate with allowed classes `bridge` and `metadata`, validate the full envelope, and only then create membership and PAUTH in one bounded MemBase transaction.
5. Never treat target paths, project membership, work-item membership, a resolvable deliberation ID, or bridge review as permission to mint source/test/configuration authority.

The prior source-target success fixture becomes a denial fixture asserting zero
membership and zero PAUTH rows. A positive create-missing-state fixture uses an
exact bridge/metadata-class target and proves the stored envelope has no source
or test class. Source/test proposals remain supported through a pre-existing
owner-scoped PAUTH; the command does not create that authority.

This is deliberately stricter than self-service authority derivation and
satisfies the DCL's assertion that a bridge-and-metadata-only authorization
cannot authorize protected implementation. Manual and create-missing paths use
the same evaluator; the create path may deny scopes it has no owner grant to
mint, but never produces a weaker or broader envelope.

### 5. Side-effect boundary

All selector, currentness, owner-authority, operation, target-class,
spec-exclusion, and create-missing validation failures occur before:

- MemBase membership or PAUTH insertion;
- work-intent claim or implementation packet creation;
- proposal content or candidate-preflight invocation;
- bridge writer invocation or bridge-file creation.

Tests use recording preflight/writer probes and before/after MemBase row counts.
A denial leaves every counter and target path unchanged.

### 6. Complete decision evidence

Return and render one stable decision object containing:

- selector mode, requested ID, selected ID, all candidate IDs/ranks, fixed best-rank cohort, and each candidate disposition;
- authorization ID/version/status, normalized expiry, supersession state, owner-decision deliberation ID, normalized envelope hash, and invalidation inputs;
- acting exact session context ID and resolved role;
- project, work item, bridge document, latest bridge status, reviewed proposal version, linked specifications, included/excluded specification sets, and exclusions;
- normalized operation, each normalized active target path/class, allowed classes, forbidden operations, evaluator/taxonomy versions and hashes;
- decision time, allow/deny decision, stable reason code, and governed recovery route.

Generated proposal metadata, JSON output, and text output disclose the same
decision identity. Any change to latest status or reviewed proposal version
invalidates prior decision evidence. No output relies on body-inferred session
identity.

## Cross-Harness Disposition

The implementation is in the shared Python `gt` CLI and proposal-filing service.
No harness-specific hook, prompt, adapter, or dispatcher route changes. The same
JSON decision object is the parity surface for Claude, Codex, Cursor,
Antigravity, Ollama, OpenRouter, Goose, and Alibaba callers of the canonical
CLI. Tests invoke the production CLI and pin identical automatic/explicit
selection semantics in text and JSON modes. Generated adapters are unchanged.

## Currentness Blast Radius And Recovery

The v004 review independently measured 578 active PAUTH rows, 21 carrying an
expiry, and none carrying supersession. Stale enforcement can cause work covered
only by a stale best-rank cohort to fail closed. Diagnostics name the stale
PAUTH and recovery route: obtain owner-approved renewal or create a new bounded
PAUTH through the governed project-authorization service. The filing command
never bypasses or mutates stale authority.

## Cross-Thread Coordination

- `WI-5560` currently has a GO thread whose declared scope overlaps all three
  WI-5458 targets without a machine-readable dependency. WI-5458 must implement
  and finalize first; WI-5560 must then rebase and revalidate before its own
  implementation. This revision creates no authority to absorb WI-5560 changes.
- `WI-5466` is already narratively sequenced after terminal/finalized WI-5458
  and overlaps `cli_bridge_propose.py`.
- `WI-5166` and then `WI-5178` remain downstream of WI-5458 completion; WI-5178
  owns cross-gate inclusion-semantics parity.
- The resolved WI-5441 successor makes its older same-path NO-GO thread
  superseded incident evidence, not a concurrent implementation front.

No overlapping implementation begins under this REVISED filing. Exact claim and
implementation-start checks must re-evaluate the live collision set after GO.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Specification-Derived Verification Plan

| Linked specification IDs | Executable verification |
|---|---|
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Exact-singleton, bounded multi-WI, unrestricted fallback, explicit WI exclusion, cross-project, unknown, equal-rank explicit override, and lower-rank explicit rejection fixtures; assert selected envelope and decision evidence. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Active, `Z` expiry, `+00:00` expiry, malformed/naive expiry, expired, superseded, unresolvable owner decision, forbidden operation, disallowed target class, narrow-deny-plus-broad-fallback, expired-exact-plus-current-membership-fallback, latest-status invalidation, and invalidation-input fixtures; every denial asserts zero side effects. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Candidate/live applicability and clause preflights; generated proposal asserts exact project/PAUTH/WI/target/spec metadata; implementation report maps every linked spec to executed evidence. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Query exact WI-5458 state before report and prove WI-5166 does not proceed until terminal VERIFIED. |
| `ADR-CROSS-HARNESS-PARITY-001`; `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Invoke shared CLI in automatic and explicit modes; compare text/JSON decision identity; confirm no harness-specific source or adapter drift. |
| `GOV-STANDING-BACKLOG-001`; `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Preserve the old invalid chain, this v2 chain, WI history, and every finding disposition; no hidden work or lifecycle mutation outside the report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Preserve project-root normalization and Agent Red out-of-scope rejection fixtures. |
| `GOV-WORK-TREE-HYGIENE-001` | Exact three-file status, diff, and `git diff --check`; no unrelated tracked mutation. |

Additional behavioral fixtures:

- Source/test `--create-missing-state` request denies before membership/PAUTH insertion.
- Bridge/metadata create-missing request succeeds and stores no source/test class.
- Strict-subset `included_spec_ids` plus null exclusions permits filing; an explicit excluded linked spec denies.
- Expired best-rank exact singleton plus current lower-rank membership fallback denies rather than broadens.

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2
```

## Acceptance Criteria

1. This v2 chain remains strict-valid and receives independent GO before source or test mutation.
2. Explicit selection is limited to equally best-ranked current covering candidates; lower-rank selection denies.
3. The best specificity cohort is fixed before stale pruning. If it contains no current candidate, the request denies and never selects a broader rank.
4. `Z` and explicit-offset aware expiries normalize correctly; malformed or naive currentness denies globally.
5. Forbidden operation, disallowed target class, unresolvable owner authority, and invalidation defects deny globally without fallback.
6. `included_spec_ids` is non-restrictive at this gate; only `excluded_spec_ids` intersection denies. WI-5178 retains restrictive-inclusion ownership.
7. Create-missing-state never derives classes from requested paths, creates only bridge/metadata authority for bridge/metadata targets, and denies source/test targets with zero durable rows and a governed owner-PAUTH recovery route.
8. Every authorization denial leaves zero MemBase, claim, packet, preflight, writer, and filesystem side effects.
9. Generated metadata, JSON, and text expose complete decision evidence including exact session/role, fixed cohort, currentness, latest bridge status, reviewed proposal version, and invalidation inputs.
10. Existing deterministic specificity, insertion-order, root-boundary, and bridge/metadata create-missing behavior remains passing under strengthened assertions.
11. All 17 linked specifications map to the verification table; focused pytest, Ruff check, Ruff format check, diff check, and both preflights pass.
12. Only the three declared targets change. No live PAUTH/project/backlog/MemBase, dispatcher/TAFE, harness, credential, external, Git commit/push, deployment, release, or cleanup mutation is in implementation scope.
13. A fresh implementation report receives independent terminal VERIFIED before WI-5458 resolves or WI-5166 proceeds.

## Prior Deliberations

- `DELIB-20266083` - restrictive `included_work_item_ids` semantics; it does not make the sibling `included_spec_ids` restrictive at this filing gate.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes creation of bounded PAUTH carriers and governed proposals but explicitly does not authorize protected source/test edits; this is why create-missing cannot mint those classes.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` - dispatcher mutation remains prohibited.
- `DELIB-20263760` - project-membership validation posture.
- `DELIB-20264663` - project-authorization lifecycle currentness.
- `DELIB-20264465` - validate candidate state before durable write.
- `DELIB-202665533` - single-source authority resolution precedent.
- `DELIB-202667230` - predecessor verification NO-GO identifying selector/currentness defects now carried by the v2 recovery.
- `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-004.md` - controlling NO-GO; only F1/F2 block this revision.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` is the owner decision behind the current bounded WI-5458 repair carrier. It permits governed PAUTH-carrier/proposal creation but expressly reserves protected source/test edits for later exact gates.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps dispatcher/TAFE mutation outside this work.

No new owner decision is required to choose the fail-closed bridge/metadata-only
remedy because it preserves the existing auto-created envelope and removes the
unapproved authority widening introduced only in v003.

## Intuitiveness / Non-Impairment Disposition

The common path remains one command with automatic selection. Ambiguity names
equal-ranked candidates and offers a validated selector. Stale or denying
authority produces a specific recovery message before side effects. Create-
missing-state remains useful for bridge/metadata-only work while source/test
work takes the explicit owner-scoped PAUTH route. Ordinary content and owner hand
edits are unaffected; this slice governs only proposal-filing authorization.

## Pre-Filing Preflight Subsection

The completed candidate passed both mandatory commands before filing, and
the governed revision helper repeats them on its metadata-enriched candidate:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2 --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5458-proposal-pauth-precedence-v2-005.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence-v2 --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5458-proposal-pauth-precedence-v2-005.md
```

Observed results: applicability preflight exit `0`,
`preflight_passed=true`, no missing required or advisory specifications, and no
blocking errors; clause preflight exit `0`, three `must_apply` clauses with
evidence, and zero blocking gaps.

## Risks And Rollback

- Strict create-missing behavior changes the old source-target success fixture to a denial. This is intentional: it preserves independent owner authority rather than minting source privilege from filer input. The diagnostic gives the bounded PAUTH recovery route.
- Fixed-cohort pruning can deny where current code falls back. This is intentional fail-closed behavior that prevents stale narrow authority from silently broadening into membership scope.
- Currentness parsing can reject malformed historical values. Both live timezone-aware spellings are supported; malformed/naive values receive a specific renewal route.
- Filing-local currentness logic could diverge before WI-5178 centralizes cross-gate parity. Tests pin the exact grammar, reason codes, evidence fields, and no-side-effect boundary for this gate.

Rollback is a separately governed reversal of only the three implementation
files after preserving report/verdict evidence and rerunning the focused suite.
The old chain, this v2 chain, PAUTH, project, work item, and deliberations are
append-only audit history and must not be deleted.

## Recommended Commit Type

`fix(bridge)`

## Authority Boundary

This REVISED proposal grants only independent Loyal Opposition review
actionability. It authorizes no source/test mutation, implementation-start
packet, live MemBase mutation, bridge verdict, Git action, dispatcher/TAFE or
harness change, credential operation, cleanup, deployment, release, or peer-
worker launch. Implementation remains paused until independent GO plus a valid
exact-session claim and implementation-start packet.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
