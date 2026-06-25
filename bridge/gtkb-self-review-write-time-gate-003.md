REVISED
author_identity: claude
author_harness_id: B
author_session_context_id: 2bb5c7b5-3956-4498-94d7-f7b2711e8e02
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal (REVISED) — Write-Time + Impl-Start Self-Review Verdict Gate (WI-4829)

bridge_kind: prime_proposal
Document: gtkb-self-review-write-time-gate
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

## Revision Note

REVISED from `-001` (GO at `-002`) for a **format-only** correction: the original
target-paths block used a multi-line fenced JSON list, which
`scripts/implementation_authorization.py` `extract_target_paths` does not parse
(its regex expects the bracketed list on a single metadata line; its heading-body
fallback then grabbed the section's later "Mutation classes used" bullets, so the
impl-start packet authorized the mutation-class names instead of the file paths).
This REVISED version expresses the path list on a single parseable metadata line.
**No design, scope, spec-linkage, or test-plan change** — the `-002` GO analysis
applies unchanged. The proposal-helper-vs-authorizer format mismatch is captured as a
separate follow-up defect.

## Project Authorization

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-SELF-REVIEW-WRITE-TIME-GATE-2026-06-25
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4829

Owner decision basis: DELIB-20266105 (AUQ 2026-06-25 — defense-in-depth scope) + owner spawned-task directive "Please start Block self-review verdicts at bridge-write time".

## target_paths

target_paths: ["scripts/bridge_review_independence.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/skills/verify/helpers/write_verdict.py", "scripts/implementation_authorization.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_self_review_write_time_gate.py"]

Mutation classes used, all within the PAUTH allowed classes (source, hook_upgrade, test_addition): hook_upgrade for the compliance-gate hook (canonical template plus re-activated copy); source for the shared comparator module, the verify finalization helper, the impl-start authorizer, and the dispatch-trigger delegation refactor; test_addition for the new spec-derived tests. `.claude/hooks/bridge-compliance-gate.py` is the re-activated byte-identical copy of the tracked template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (the committed change is the template; re-activation is a local runtime step). No protected narrative-authority file and no MemBase/spec mutation is in scope.

## Summary

The bridge review-independence guarantee — a `GO`/`NO-GO`/`VERIFIED` verdict must
come from a different session context than the artifact it reviews — is enforced
**only at headless dispatch selection** (`scripts/cross_harness_bridge_trigger.py`
`_self_review_refusal_reason`; `groundtruth_kb/tafe_dispatch_policy.py`
`_review_independence_gate`). An **interactive** Loyal Opposition session writes
its verdict directly, bypassing dispatch entirely, and **nothing validates
self-review at verdict-write time**. `scripts/implementation_authorization.py`
`begin` has no independence check either.

Evidence: on 2026-06-25, verdict `bridge/gtkb-canonical-lifecycle-reference-002.md`
was a `GO` whose `author_session_context_id` equaled the reviewed proposal
`-001`'s `author_session_context_id` (a self-review). It was caught and voided
only because a separate Cursor LO session later re-reviewed it (`-004`). Nothing
mechanical stopped the invalid verdict at creation.

This proposal closes the gap with defense-in-depth, reusing the existing
`author_meets_reviewer_refused` semantics.

## Specification Links

Cross-cutting (mechanically applicable to this bridge proposal):
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority (path `bridge/**`); the review-independence boundary is part of this authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived executed tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable-artifact bias.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development decision.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact lifecycle triggers.

Project-authorization governance:
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — governs the cited PAUTH (in the PAUTH `included_spec_ids`).

Subject-matter authority (the invariant this enforces):
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — Document Artifact Author Provenance Contract; the `author_session_context_id` provenance this gate validates is governed here. Related prior provenance work: WI-4522 (loader READ removal after the S389 incident).

This proposal honors `GOV-FILE-BRIDGE-AUTHORITY-001`: it is filed as an append-only
versioned entry in the canonical numbered bridge-file chain
(`bridge/gtkb-self-review-write-time-gate-NNN.md`); no bridge file is deleted or
rewritten in place, and TAFE/dispatcher state is the authoritative workflow state.

## Requirement Sufficiency

Existing requirements sufficient. The review-independence invariant is already
specified (`GOV-FILE-BRIDGE-AUTHORITY-001` review-independence boundary;
`config/agent-control/SESSION-STARTUP-INDEX.md` § Session-context review
independence (normative); `.claude/rules/file-bridge-protocol.md`;
`.claude/rules/loyal-opposition.md`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`). This
proposal adds **enforcement** of an already-specified invariant at two surfaces
that currently lack it. No new or revised requirement is required before
implementation.

## Prior Deliberations

- `DELIB-20266105` — owner authorization for this defense-in-depth gate (this session).
- Deliberation search (2026-06-25): `gt deliberations search "self-review verdict author session context write-time detection review independence enforcement bridge compliance gate"` returned no on-point prior decision (hits were unrelated GO/NO-GO/VERIFIED verdicts).
- Related work items: WI-4823 (implementation-report false-attribution from cross-harness claim/marker population — sibling, not duplicate; tied to ADR-DISPATCHER-ARCHITECTURE-001), WI-4522 (author-metadata loader READ removal, S389 GOV-DOCUMENT-AUTHOR-PROVENANCE-001 incident).

_No prior deliberation rejects or constrains adding write-time self-review enforcement; the closest authority is DELIB-20266105._

## Owner Decisions / Input

This work depends on owner approval, supplied via AskUserQuestion + spawned-task directive, recorded as `DELIB-20266105`:

- Owner spawned-task directive: "Please start 'Block self-review verdicts at bridge-write time'" (2026-06-25).
- AUQ `AUQ-SELF-REVIEW-WRITE-TIME-GATE-SCOPE-2026-06-25`, Q "Gate scope": owner answer **"Defense-in-depth (write-time + impl-start)"** — block a self-review `GO`/`NO-GO`/`VERIFIED` at verdict-write time (compliance gate + verify helper) AND add a symmetric backstop in the impl-start authorizer.
- No further owner decision is blocking.

## Proposed Change

### 1. Shared comparator — `scripts/bridge_review_independence.py` (NEW)

A small, dependency-free module single-sourcing the refusal semantics already used
at dispatch time:
- `self_review_reason(reviewer_session_context_id, target_author_session_context_id) -> str | None`
  — pure comparator: empty/missing → `"author_session_context_missing"`; equal →
  `"author_meets_reviewer_refused"`; otherwise `None`.
- `parse_author_session_context_id(content) -> str | None`.
- `reviewed_artifact_path(verdict_content, bridge_id, project_root) -> Path | None`
  — resolve the reviewed artifact via the verdict's `Responds to:` /
  `Reviewed report:` / `Approved proposal:` reference, falling back to the latest
  prior versioned file. (Latest-file alone is insufficient for `VERIFIED`, where
  an intermediate `GO` can be newer than the reviewed report — `-005` reviews
  report `-003`, not `GO -004`.)
- `verdict_self_review_reason(verdict_content, bridge_id, project_root) -> str | None`
  — compose the above; fail closed (`author_session_context_unreadable`) on read errors.

### 2. Verdict-write-time enforcement (the gap that produced `-002`)

- **`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`** (+ re-activate to
  `.claude/hooks/`): when the Write target is an LO verdict bridge file
  (`_is_lo_verdict_bridge_file`), call `verdict_self_review_reason` on the pending
  content and **hard-block** the Write on any refusal reason, naming the reviewed
  artifact and the equal session ids. Imported the same way the gate already
  imports `scripts.bridge_author_metadata`.
- **`.claude/skills/verify/helpers/write_verdict.py`**: the verify helper writes
  verdicts via `write_bytes`, bypassing the PreToolUse Write hook. Add the same
  check immediately before the write; raise a clear error so the helper never
  emits a self-review verdict.

### 3. Impl-start backstop — `scripts/implementation_authorization.py`

In `begin`, after resolving the latest `GO`, compare the `GO` verdict author
against the reviewed proposal (`NEW`/`REVISED`) author via `self_review_reason`;
refuse authorization when equal or when author metadata is missing/unreadable.

### 4. Single-source the dispatch trigger — `scripts/cross_harness_bridge_trigger.py`

Refactor `_self_review_refusal_reason` to delegate its author-comparison to the
shared `self_review_reason` comparator (behavior-preserving; the dispatch path
keeps its latest-file target resolution). Guarded by the existing
`test_dispatch_author_meets_reviewer.py`.

## Specification-Derived Verification Plan

New `platform_tests/scripts/test_self_review_write_time_gate.py`:

| Requirement (source) | Verification |
|---|---|
| Comparator: equal sessions refused; distinct pass; missing fails closed (GOV-DOCUMENT-AUTHOR-PROVENANCE-001) | `test_comparator_*` |
| Reviewed-artifact resolution honors `Responds to:` over latest file (VERIFIED-reviews-report case) | `test_reviewed_artifact_uses_responds_to` |
| Compliance gate blocks a self-review verdict Write (GOV-FILE-BRIDGE-AUTHORITY-001) | `test_compliance_gate_blocks_self_review_verdict` |
| Verify helper refuses a self-review verdict (write_bytes path) | `test_write_verdict_refuses_self_review` |
| Impl-start `begin` refuses a self-review GO (backstop) | `test_impl_start_refuses_self_review_go` |
| Dispatch trigger behavior preserved after delegation refactor | existing `test_dispatch_author_meets_reviewer.py` |

Execution commands (run on touched files before the report):
- `python -m pytest platform_tests/scripts/test_self_review_write_time_gate.py platform_tests/scripts/test_dispatch_author_meets_reviewer.py -q --tb=short`
- `python -m ruff check <changed .py files>`
- `python -m ruff format --check <changed .py files>`

## Acceptance Criteria

1. A verdict whose `author_session_context_id` equals the reviewed artifact's
   author session is **blocked** at both write-time surfaces and refused at
   impl-start.
2. A self-review verdict with missing/unreadable reviewed-artifact author fails **closed**.
3. A genuinely independent verdict (distinct sessions) passes unchanged.
4. Dispatch-time `author_meets_reviewer_refused` behavior is unchanged (existing test green).
5. New tests PASS; `ruff check` + `ruff format --check` clean on touched files.

## Risk / Rollback

- Risk: medium. Touches the load-bearing PreToolUse compliance gate and the
  impl-start authorizer. The new check fires only on LO verdict bridge files;
  fail-closed only on genuine self-review or unreadable author metadata, so
  legitimate independent verdicts are unaffected. The dispatch-trigger refactor
  is behavior-preserving and test-guarded.
- Rollback: revert the seven target paths and re-activate the prior gate template; no data/state/migration.

## Recommended Commit Type

`fix:` — closes a review-independence enforcement gap (a defect). Adds enforcement
+ tests, not a new user-facing capability.
