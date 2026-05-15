# Implementation Proposal (NEW): Align implementation-start gate verification-plan heading recognition with the bridge clause-preflight

Status: NEW
Document: gtkb-impl-auth-verification-heading-gate-alignment
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15
Session: S352
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Problem

Two mechanical bridge gates disagree on what constitutes a valid
specification-derived verification plan in an implementation proposal:

1. `scripts/implementation_authorization.py` — `has_spec_derived_verification()`
   (line 429) accepts a proposal only when it contains a `## ` section whose
   heading text equals, case-insensitively and **exactly**, one of four
   whitelisted strings: `Specification-Derived Verification`,
   `Specification-Derived Verification Plan`, `Spec-Derived Test Plan`, or
   `Verification Plan`. The heading comparison runs through `section_body()`
   (line 199), which does exact heading equality. When no exact match is found,
   `implementation_authorization.py begin` returns
   `{"authorized": false, "error": "Approved proposal is missing a spec-derived
   verification plan"}` and refuses to issue the implementation-start packet.

2. `scripts/adr_dcl_clause_preflight.py` — the evidence detector for
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`
   (registered in `config/governance/adr-dcl-clauses.toml`, line 103) accepts a
   much broader `evidence_pattern`:
   `(?i)(?:specification[- ]derived\s+verification|spec[- ]to[- ]test|python -m pytest|pytest|ruff|test_.+\.py)`,
   matched **anywhere** in the document regardless of heading.

Because the two detectors disagree, Loyal Opposition can legitimately issue a
`GO` on a proposal whose verification section is titled, for example,
`## Test Plan (spec-to-test mapping)` — the section satisfies the file-bridge
protocol's verification-plan requirement and the clause-preflight evidence
pattern — and then `implementation_authorization.py begin` rejects that same
GO'd proposal solely because the heading text is not on the four-string
whitelist.

This is not hypothetical. In session S351 on bridge thread
`gtkb-hook-import-latency-chromadb-lazy`, proposal
`bridge/gtkb-hook-import-latency-chromadb-lazy-003.md` titled its verification
section `## Test Plan (spec-to-test mapping)`, received a Codex `GO` at `-004`,
and was then rejected by `begin`. The revision
`bridge/gtkb-hook-import-latency-chromadb-lazy-005.md` (`REVISED`) changed only
that heading to `## Specification-Derived Verification`. The REVISED round-trip
carried no review value — it was pure governance friction caused by the gate
inconsistency.

The file-bridge protocol rule itself
(`.claude/rules/file-bridge-protocol.md`, "Mandatory Implementation-Start
Authorization Metadata") requires "a specification-derived verification plan
mapping the linked requirements to tests or verification commands" — it does
**not** mandate a specific heading string. `has_spec_derived_verification()`
mechanized that rule with an over-narrow exact-heading whitelist; the fix
re-aligns the mechanization with the rule's intent and with the detector that
Loyal Opposition already applies at `GO`.

## Proposed Change

Single-file behavior change in `scripts/implementation_authorization.py`, plus
tests. The fix broadens `has_spec_derived_verification()` from exact-heading
equality to heading-token recognition, while keeping a structural floor so the
predicate stays meaningfully heading-anchored.

Behavior after the change — a `## ` section is recognized as a spec-derived
verification plan when its body is non-empty AND either:

- its heading contains a verification token (`specification-derived
  verification`, `spec-derived verification`, `spec-derived test plan`,
  `spec-to-test`, `specification-to-test`, or `verification plan`); OR
- its heading contains `test plan` AND its body carries spec-to-test command
  evidence (a `pytest` / `python -m pytest` / `ruff` / `npm test` / `pnpm test`
  / `uv run` / `make test` invocation, a `test_*.py` reference, or the literal
  `spec-to-test`).

All four legacy headings remain accepted (each contains a recognized token), so
the change is regression-safe. `## Test Plan (spec-to-test mapping)` is now
accepted. A bare `## Test Plan` with no test-command evidence is still rejected,
preserving a governance floor. The predicate stays heading-anchored, so it
remains structurally stricter than the clause-preflight's document-wide regex
while accepting the same realistic verification surfaces.

Implementation outline:

- `section_body()` is refactored to delegate to a new private generator
  `_iter_sections()` that yields `(heading, body)` for every `## ` section.
  `section_body()` keeps its exact-match, first-match-wins, case-insensitive
  contract unchanged (the refactor is behavior-preserving for that function and
  is covered by a regression test).
- Two module-level constants are added: `VERIFICATION_HEADING_TOKENS` (the
  recognized heading substrings) and `VERIFICATION_TEST_EVIDENCE_RE` (the
  command/`test_*.py` evidence regex, mirroring the token set the bridge
  clause-preflight and `bridge-compliance-gate.py` `COMMAND_EVIDENCE_RE`
  already use).
- `has_spec_derived_verification()` iterates `_iter_sections()` and applies the
  recognition rule above.

No change to `adr_dcl_clause_preflight.py`, `bridge-compliance-gate.py`, the
clause registry, or any rule file. The scope is deliberately the single
predicate that disagrees with the already-correct GO-time detector.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — `bridge/INDEX.md` is the authoritative bridge workflow state; this proposal is filed and reviewed through the file bridge.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites every governing specification it is aware of in this section.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the spec whose clause-preflight evidence detector is the GO-time reference behavior; the verification plan below derives executed tests from this spec and from the defect statement.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 — the proposal header carries the mandatory `Project Authorization`, `Project`, and `Work Item` metadata lines, resolving to live MemBase project membership.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the work is tracked as durable MemBase artifacts: work item `GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` and owner-decision deliberation `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — traceability across the owner decision, work item, proposal, tests, and report is preserved through this bridge thread.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the bridge thread exposes the NEW, GO, and VERIFIED lifecycle states for this change.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is a live GT-KB path inside `E:\GT-KB`; see In-Root Placement Evidence below.
- `.claude/rules/file-bridge-protocol.md` — the Mandatory Specification-Derived Verification Gate and the Mandatory Implementation-Start Authorization Metadata requirements that `has_spec_derived_verification()` mechanizes.
- `.claude/rules/codex-review-gate.md` — the Mechanical Implementation-Start Gate that consumes `has_spec_derived_verification()`.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal references the work item `GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` only as its own provenance metadata. It performs no bulk work-item transition, no standing-backlog cleanup, and no bulk update. It edits a single predicate function and adds tests. The supporting governance artifacts (the owner-decision deliberation, the work-item record, and the project-authorization amendment) were already recorded with their own audit trail and a formal-artifact-approval pathway; the owner decision is enumerated in the Owner Decisions / Input section below. The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause, if triggered by the literal token `work item` in this text, is satisfied by that audit visibility and is not applicable as a bulk operation.

## In-Root Placement Evidence

All target paths are repo-relative paths resolving inside the GT-KB root
`E:\GT-KB`, satisfying `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
`.claude/rules/project-root-boundary.md`:

- `scripts/implementation_authorization.py` -> `E:\GT-KB\scripts\implementation_authorization.py` (existing platform script; edit in place).
- `platform_tests/scripts/test_implementation_authorization.py` -> `E:\GT-KB\platform_tests\scripts\test_implementation_authorization.py` (existing in-root test module; extend with new tests).

No target path is under `applications/`, no path leaves `E:\GT-KB`, and no
GT-KB artifact is created or read from `E:\Claude-Playground` or any
home-directory or temp location.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
and `.claude/rules/file-bridge-protocol.md` already govern the verification-plan
requirement. The defect is that `has_spec_derived_verification()` mechanizes
that requirement more narrowly than the rule states and more narrowly than the
GO-time clause-preflight detector. This is a correctness and reliability fix to
existing behavior; no new or revised specification is needed before
implementation.

## Prior Deliberations

- `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT` — the S352 owner decision (via AskUserQuestion) authorizing this fix as a work item under the existing `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` authorization; rejected alternatives were a standalone new project and recording a triage WI with the proposal deferred.
- `bridge/gtkb-hook-import-latency-chromadb-lazy-003.md` through `-005.md` — the S351 thread that exhibited the defect: a `## Test Plan (spec-to-test mapping)` heading was GO'd at `-004` and then rejected by `begin`, forcing the heading-only REVISED at `-005`.
- `bridge/gtkb-implementation-start-authorization-gate-001.md` through `-010.md` — the originating thread that built `implementation_authorization.py` and `has_spec_derived_verification()`; it established the four-string heading whitelist now being broadened.
- A `search_deliberations` scan for "spec-derived verification heading", "implementation authorization gate inconsistency", and "verification plan heading" returned no prior deliberation addressing this specific gate-alignment defect.

## Specification-Derived Verification

A spec-to-test mapping for the change. New tests are added to the existing
module `platform_tests/scripts/test_implementation_authorization.py`. The plan
prefers deterministic fixture-driven assertions over timing or environment
dependence.

1. `test_has_spec_derived_verification_accepts_legacy_headings` — derives from
   `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and the regression-safety
   requirement. Asserts all four legacy headings
   (`Specification-Derived Verification`, `…Plan`, `Spec-Derived Test Plan`,
   `Verification Plan`) are still recognized.
2. `test_has_spec_derived_verification_accepts_test_plan_spec_to_test_heading`
   — derives from the defect statement. Asserts a `## Test Plan (spec-to-test
   mapping)` section with `pytest` evidence in its body is recognized.
3. `test_has_spec_derived_verification_accepts_spec_to_test_mapping_heading` —
   derives from the clause-preflight evidence pattern. Asserts a
   `## Spec-to-Test Mapping` heading is recognized.
4. `test_has_spec_derived_verification_rejects_bare_test_plan_without_evidence`
   — derives from the governance-floor requirement. Asserts a bare
   `## Test Plan` heading with no test-command evidence is rejected.
5. `test_has_spec_derived_verification_rejects_missing_verification_section` —
   asserts a proposal with no verification section returns `False`.
6. `test_section_body_exact_match_preserved` — regression for the
   `_iter_sections()` refactor; asserts `section_body()` keeps exact,
   first-match, case-insensitive heading semantics.
7. `test_create_authorization_packet_accepts_test_plan_spec_to_test_heading` —
   integration test reproducing the S351 scenario: a GO'd bridge fixture whose
   verification heading is `## Test Plan (spec-to-test mapping)` produces a
   valid authorization packet from `create_authorization_packet()` rather than
   raising `AuthorizationError`.

Verification commands (to be executed and recorded in the implementation
report):

- `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q`
- `ruff check scripts/implementation_authorization.py`

## Acceptance Criteria

- `has_spec_derived_verification()` recognizes all four legacy headings
  (no regression).
- `has_spec_derived_verification()` recognizes `## Test Plan (spec-to-test
  mapping)` when the section body carries test-command evidence.
- `has_spec_derived_verification()` rejects a bare `## Test Plan` with no
  evidence and a proposal with no verification section.
- `section_body()` behavior is unchanged.
- The full `test_implementation_authorization.py` module passes; `ruff` is
  clean on the modified script.
- No change to `adr_dcl_clause_preflight.py`, `bridge-compliance-gate.py`, the
  clause registry, or any rule file.

## Risk and Rollback

Risk is low and contained. The change broadens a single boolean predicate in
one file. The only failure mode is over-acceptance (recognizing a section that
is not a real verification plan); this is bounded by the specific token set and
by the test-evidence requirement on the looser `test plan` heading. The change
cannot make a previously-accepted proposal fail, because every legacy heading
remains in the recognized-token set. Rollback is a single-commit revert of
`scripts/implementation_authorization.py`; the added tests are independent and
harmless if retained.

## Alternatives Considered

- **Unify all three detectors behind one shared predicate.** Rejected for this
  proposal's scope: the clause-preflight evidence pattern lives in a
  TOML-configured registry and `bridge-compliance-gate.py` uses a separate
  heading regex for VERIFIED *reports* (a different artifact than the
  *proposals* `has_spec_derived_verification()` validates). A true shared
  predicate is a larger refactor across a hook, a CLI, and a config file, and
  is out of proportion to this reliability fix. The narrower fix — making
  `begin` at least as permissive as the GO-time detector — fully closes the
  observed inconsistency.
- **Align both gates by tightening the clause-preflight instead.** Rejected:
  the clause-preflight and Loyal Opposition's GO are the *correct* reference
  behavior (they match the rule's intent). The defect is the over-narrow
  `begin` gate. Tightening the GO-time detector would create new false
  rejections rather than removing one.
- **Leave `has_spec_derived_verification()` and require authors to use an exact
  heading.** Rejected: that is the status quo that produced the S351
  pure-friction REVISED; it pushes a mechanical-gate quirk onto every proposal
  author and Loyal Opposition reviewer indefinitely.

Out of scope, noted for a separate review: `bridge-compliance-gate.py`
`_has_spec_derived_verification()` (line 211) uses a heading regex that requires
the heading to *start with* `spec-to-test` / `specification-derived
verification`. It applies to `VERIFIED` reports, not proposals, so it is not
part of the observed inconsistency, but it shares the same narrowness class and
may warrant its own work item.

## Recommended Commit Type

`fix:` — this repairs broken behavior (a mechanical-gate inconsistency causing
false rejection of GO'd proposals). It adds no new capability surface; the two
module-level constants and the `_iter_sections()` helper exist only to
implement the corrected predicate. The accompanying tests are `test:`-class
additions bundled into the same `fix:` commit per the change's single purpose.

## Owner Decisions / Input

- **AskUserQuestion (S352, 2026-05-15)** — Question: "Filing the bridge proposal
  for this gate-alignment fix requires a work item under an owner-authorized
  project (the S350 spec→project→WI→bridge enforcement chain). No existing WI
  covers this defect. How should I authorize the work item?" Owner answer:
  **"Add to reliability project"** — create a new work item for this defect and
  add it to the existing `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
  authorization, then file this bridge proposal. Rejected options: a new
  standalone project + authorization; recording a triage WI and deferring the
  proposal. This decision is archived as
  `DELIB-S352-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT`
  (`source_type=owner_conversation`, `outcome=owner_decision`) and authorizes
  the work item `GTKB-IMPL-AUTH-VERIFICATION-HEADING-GATE-ALIGNMENT`, its
  membership in `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, and the WI-only
  amendment of `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`.
- No further owner decision is required to review or implement this proposal.
  The code change does not deploy, does not mutate specifications, and does not
  cross any release gate.
