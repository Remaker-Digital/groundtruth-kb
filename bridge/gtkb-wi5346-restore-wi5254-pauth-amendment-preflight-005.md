REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6c77-9837-7831-be7f-aede63f3d210
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; WI-5346 proposal-revision-only worker; high reasoning

# Revised Proposal - WI-5346 Restore Structured PAUTH Amendment Preflight

bridge_kind: prime_proposal
Document: gtkb-wi5346-restore-wi5254-pauth-amendment-preflight
Version: 005
Responds to: bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-004.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5346

target_paths: ["scripts/implementation_authorization.py", "scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder accepts the version-004 NO-GO and selects its Option A. The
specification-supported least-broad correction is to retain the authenticated
`scripts/implementation_authorization.py` repair and expand the exact target
scope only far enough to restore structured PAUTH amendment enforcement in the
proposal applicability preflight and its focused tests.

This revision does not authorize implementation. A later independent GO, fresh
matching `go_implementation` claim, and successful implementation-start packet
covering all three target paths are required before any protected edit. No
database, hook, template, dispatcher, TAFE, harness, credential, Git,
deployment, release, or external-system mutation is in scope.

## Why Applicability Enforcement Remains Required

Narrowing away the companion applicability criterion is not supported by the
governed WI-5254 contract. Its approved proposal specifies proposal
applicability enforcement as IP-2 and requires a structured PAUTH amendment
with invalid owner evidence to fail before proposal filing as well as before
implementation start. `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`
requires amendment writes to fail closed without covering owner evidence, while
the existing artifact lifecycle and non-bypass specifications require that a
deterministically detectable prerequisite not be silently deferred past an
earlier governed gate.

The least-broad compliant option is therefore to invoke the already-restored
shared validator from `scripts/bridge_applicability_preflight.py`, expose its
diagnostic through the existing `blocking_errors` and `preflight_passed`
packet contract, and cover that behavior in
`platform_tests/scripts/test_bridge_applicability_preflight.py`. The live and
template hook surfaces from the original WI-5254 proposal are not reopened by
this recovery revision because they already consume the preflight packet's
semantic denial contract and no current evidence identifies a hook defect.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - requires active-project PAUTH specification-set amendments to fail closed without exact owner-approved packet evidence.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - defines the structured included/excluded specification sets and authorization/project identity used to compute the delta.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires the implementation-start packet to bind the complete corrected target scope and operative project authority.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - early validation may deny an incomplete proposal but cannot create approval or bypass GO, claim, start, or operation-time authority.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO, exact claim/start authority, implementation report, and independent VERIFIED before protected mutation can complete.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this revised proposal to carry the complete governing specification set.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5346 to the active Authority Foundations project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed, specification-mapped evidence for both authorization and applicability enforcement.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - requires non-commingling and sequencing around nonterminal WI-5178 and WI-5330 shared-target work.
- `GOV-WORK-TREE-HYGIENE-001` - prohibits treating foreign dirty hunks as WI-5346 implementation or cleanup authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids restoring this gate by weakening operation-time authority, proposal parsing, or unrelated accepted flows.
- `GOV-STANDING-BACKLOG-001` - keeps WI-5346 open until the recovered behavior is independently verified.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - requires every target and verification dependency to remain under `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the regression, partial repair, revised scope, tests, and verdict as linked durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - distinguishes this recovery lifecycle from WI-5254's historical verified stand-down.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the detected scope defect and its correction to remain traceable through the governed bridge.

## Prior Deliberations

- `DELIB-202666274` authorizes required Authority Foundations modernization repairs at project scope while retaining independent GO, claim/start, verification, and mechanical-operation gates.
- `DELIB-202666173` authorized correction of proof-blocking defects during the governed fleet stabilization that produced WI-5254.
- `DELIB-202666140` records the exact owner-evidence precedent for project-authorization amendments.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-001.md` defines proposal applicability enforcement as IP-2 and the fail-before-filing acceptance criterion.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-007.md` and `-008.md` withdraw and verify the historical exact candidate as a stand-down; they do not adopt its source or test hunks.
- `bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-003.md` authenticates the partial one-file repair and records the failing applicability evidence.
- `bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-004.md` requires this scope/verification correction.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` and the active project
authorization cover the required Authority Foundations repair, but they do not
waive independent GO, exact claim/start, verification, Git, release, or
deployment gates. This revision creates no owner evidence and infers no owner
approval for any future PAUTH amendment.

## Findings Addressed

### F1 - GO verification condition required an out-of-scope target

Resolved by expanding `target_paths` from one path to exactly three:

1. `scripts/implementation_authorization.py` for the authenticated validator
   and implementation-start backstop;
2. `scripts/bridge_applicability_preflight.py` for the missing invocation and
   semantic blocking result; and
3. `platform_tests/scripts/test_bridge_applicability_preflight.py` for the
   focused missing/invalid/exact-evidence applicability cases.

No hook, template, database, or unrelated test path is added. Final
verification commands now map only behavior that can be satisfied within this
exact scope.

### F2 - The authorized source hunk is valid partial evidence

Preserved. Version 003 authenticated the one-file implementation-start repair:

- implementation-start packet hash:
  `sha256:26aa7a0e6b6616fe28c964c973f4195fd3bdf8d7f2564fe81c1b3f9fbc9c5a72`;
- pre-start packet hash:
  `sha256:7c5988077788f63fc87a236fd06a4743e215656f2348af29c8156cb98a53f844`;
- pre-start SHA-256 of `scripts/implementation_authorization.py`:
  `00C98C006874A5AAE6395C561E51BE09BF25E22939D2BC1DD191563BDA43190E`;
- focused result: `9 passed, 146 deselected`;
- Ruff lint and format checks: PASS.

Those results remain partial evidence only. They are not a complete
implementation report, do not authorize further edits, and must be re-executed
after a new GO/start against the final exact three-path candidate.

## Scope And Current Ownership Boundary

The three targets are currently dirty. At revision time their observed SHA-256
values are:

- `scripts/implementation_authorization.py`:
  `C129C76D44419E81CAC42DAD9AAEBC272E03737C09CC2966148C237708066C7C`;
- `scripts/bridge_applicability_preflight.py`:
  `118F52791BC965FCFCCB769DB67B4156CEECE2B3738C9680AF9EAB7F6B784ABA`;
- `platform_tests/scripts/test_bridge_applicability_preflight.py`:
  `259DEB6B80F9C1B2CA9E00F95A23763AED559EC4DAC7BE1039CF1EBD7609F066`.

Ownership and attribution are constrained as follows:

- WI-5346 owns only the authenticated structured-amendment validator/import/
  call-site hunk in `scripts/implementation_authorization.py` plus the future
  exact applicability invocation and focused PAUTH test adoption authorized by
  a new GO.
- WI-5178 is a nonterminal `GO` thread for adjacent operation-time authority
  hunks in `scripts/implementation_authorization.py`. Those bytes are foreign
  to WI-5346 and must remain unchanged. A live WI-5178 implementation claim on
  the shared path blocks WI-5346 start; absent a live claim, exact-hunk
  isolation and fresh hashes are still mandatory.
- WI-5330 owns the completed regex and regression-test hunks in
  `scripts/bridge_applicability_preflight.py` and its test file. Its latest
  status is finalization-scoped `NO-GO`; the engineering is explicitly sound.
  WI-5346 must preserve those hunks byte-for-byte and may not use them as its
  own completion evidence.
- WI-5254's verified stand-down withdrew ownership of its historical
  structured-PAUTH preflight candidate. WI-5346 may adopt only the exact
  structured-amendment applicability tests needed by this revised scope after
  new GO/start authority; unrelated historical candidate bytes remain foreign.

Whole-file replacement, broad staging, foreign-hunk cleanup, or attribution of
another thread's bytes to WI-5346 is prohibited. Before implementation, the
Prime Builder must record fresh hashes, inspect current claims and latest
thread statuses, and either sequence behind an active shared-path owner or
produce an exact hunk candidate that demonstrably preserves every foreign
hunk.

## Requirement Sufficiency

Existing requirements are sufficient. The amendment-approval DCL, structured
authorization envelope DCL, original WI-5254 approved enforcement timing, and
existing executable tests define the behavior without a new owner decision or
new specification. This revision changes target scope to match that existing
contract; it does not expand approval policy.

## Specification-Derived Verification Plan

| Governing specification | Executed evidence required after a new GO/start | Expected result |
|---|---|---|
| `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py -k "structured_pauth_amendment or backstops_structured_pauth_amendment" -q --tb=short --timeout=300` | All 9 focused authorization/backstop cases pass, including no-delta, malformed/ambiguous envelope, identity, evidence readability/schema/provenance, exact coverage, and creation-time rejection. |
| Same two specifications; original WI-5254 IP-2 applicability contract | `python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -k "structured_pauth_amendment or pauth_approval" -q --tb=short --timeout=300` | All focused applicability cases pass: missing evidence and invalid/out-of-root/malformed/non-owner/non-covering evidence fail closed; exact evidence passes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | `python -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short --timeout=300` | Both complete target suites pass on the final exact candidate; unrelated proposal parsing and authorization flows do not regress. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short --timeout=300` | The corrected preflight does not weaken claim/start or operation-time enforcement. Any companion-thread dependency failure is reported rather than absorbed. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-WORK-TREE-HYGIENE-001` | Fresh pre-start hashes, `git diff --check --` on all three targets, hunk-level diff attribution against the start snapshot, and current claim/status evidence for WI-5178/WI-5330 | Only WI-5346-attributable hunks differ from the start snapshot; WI-5178 and WI-5330 bytes remain unchanged. |
| Python quality gate | `python -m ruff check scripts/implementation_authorization.py scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py` and `python -m ruff format --check` on the same paths | Both commands pass. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; proposal/spec-linkage DCLs | Mandatory applicability and clause preflights for this revision and the later implementation report | No missing required specifications, no semantic blocking errors, and no blocking clause gaps. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; artifact lifecycle specifications | Final path inventory, WI-5346 backlog record, and numbered bridge chain | Every dependency is in-root and the distinct recovery lifecycle remains append-only and traceable. |

## Pre-Filing Preflight Subsection

Applicability preflight:

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5346-restore-wi5254-pauth-amendment-preflight --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-005.md --json`;
- result: exit 0, `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- semantic blocking errors: none;
- packet hash:
  `sha256:cb213072c283194e286e1c2d5c11f8d60eccb4b7e4c7f5a370fc1b65df133a4c`.

Clause applicability preflight:

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5346-restore-wi5254-pauth-amendment-preflight --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-005.md`;
- result: exit 0;
- clauses evaluated: 5 (`must_apply: 4`, `may_apply: 1`);
- evidence gaps in must-apply clauses: 0;
- blocking gaps: 0.

The governed revision helper reruns both candidate gates before the live bridge
write; the live artifact is filed only if both remain passing.

## Risk And Rollback

The main risk is commingling three already-dirty shared surfaces. The controls
are fresh hashes, claim/status inspection, sequencing behind any live owner,
exact-hunk implementation, full target-suite verification, and an
implementation report that separates WI-5346 evidence from WI-5178/WI-5330
bytes. The secondary risk is divergent validation semantics; the applicability
surface must call the shared validator rather than reimplement its parsing,
owner-packet schema, or exact-coverage logic.

Rollback is limited to the exact WI-5346 applicability invocation and any
newly adopted focused PAUTH test hunk. The already-authenticated
`implementation_authorization.py` repair may be rolled back only through a
later governed verdict that specifically rejects it. No whole-file rollback or
foreign-hunk alteration is permitted.

## Recommended Commit Type

`fix` - restore the already-specified fail-closed proposal and implementation
preflight behavior.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
