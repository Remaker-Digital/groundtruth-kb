NEW

# Requirement-Sufficiency operative-precedence fix (impl-authorization gate false-positive)

bridge_kind: prime_proposal
Document: gtkb-impl-auth-requirement-sufficiency-operative-precedence-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-18 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-prime-interactive-bridge-dispatcher-triage-20260618
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (harness B); explanatory output style; bridge-dispatcher triage

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4671

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_fab14_requirement_sufficiency.py"]

implementation_scope: source
kb_mutation_in_scope: false

---

## Summary

`requirement_sufficiency_state()` in `scripts/implementation_authorization.py`
classifies a proposal's `## Requirement Sufficiency` section as a requirement
*gap* whenever `REQUIREMENT_GAP_RE` matches anywhere in the section, and the gap
check runs *before* the sufficiency check. This produces a false positive when a
proposal correctly declares "Existing requirements are sufficient" as its
operative state but also includes a forward-looking explanatory sentence such as
"New or revised requirements would be needed only for a later destructive cleanup
implementation." The trailing conditional mention matches `REQUIREMENT_GAP_RE`,
so the section is classified `gap` and the implementation-authorization packet
mint fails with `AuthorizationError: "Approved proposal says new or revised
requirements are required before implementation"`.

This defect took a correct, GO'd proposal
(`gtkb-stale-git-worktree-autogc-diagnosis`) and made it permanently
un-authorizable: the cross-harness dispatcher re-selected that oldest GO thread on
every trigger fire, failed the packet mint identically, logged it, and repeated,
starving 24+ pending Prime threads behind it. That thread is currently parked
`DEFERRED` (`bridge/gtkb-stale-git-worktree-autogc-diagnosis-003.md`) pending this
fix.

The fix makes the classifier honor the file-bridge-protocol "exactly one operative
state" contract by **operative precedence**: when both a gap phrase and a
sufficiency phrase are present in the section, the one that appears *first* (the
leading operative declaration) determines the state; a trailing mention of the
other state is treated as explanatory context, not the operative classification.

### Before / after

Current (`scripts/implementation_authorization.py:870-877`):

```python
    body = section_body(markdown, "Requirement Sufficiency")
    if not body:
        return "missing"
    if REQUIREMENT_GAP_RE.search(body):
        return "gap"
    if REQUIREMENT_SUFFICIENCY_RE.search(body):
        return "sufficient"
    return "unrecognized"
```

Proposed:

```python
    body = section_body(markdown, "Requirement Sufficiency")
    if not body:
        return "missing"
    gap_match = REQUIREMENT_GAP_RE.search(body)
    sufficiency_match = REQUIREMENT_SUFFICIENCY_RE.search(body)
    if gap_match and sufficiency_match:
        # Both bounded phrases present: the operative state is the LEADING
        # declaration; a trailing mention of the other state (e.g. "new or
        # revised requirements would be needed only for a later <scope>") is
        # explanatory context, not the operative classification. (WI-4671)
        return "gap" if gap_match.start() < sufficiency_match.start() else "sufficient"
    if gap_match:
        return "gap"
    if sufficiency_match:
        return "sufficient"
    return "unrecognized"
```

The regexes (`REQUIREMENT_GAP_RE`, `REQUIREMENT_SUFFICIENCY_RE`) are unchanged;
only the classification logic gains position precedence. This is the
minimal-risk change that resolves the reported false positive without weakening
genuine gap detection: a proposal that leads with "New or revised requirement
required before implementation" still classifies as `gap`.

### Out of scope (documented residual)

A section that contains ONLY a conditional/future-scoped gap mention and no
operative sufficiency phrase still classifies as `gap`. That section violates the
"exactly one operative state" rule (it never states its operative sufficiency),
so prompting the author to add the operative phrase is acceptable. Tightening
`REQUIREMENT_GAP_RE` to exclude modal-conditional framing ("would/could/might be
needed") is a candidate follow-on, intentionally not bundled here to keep this
change minimal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the implementation-start authorization gate is
  part of the governed bridge protocol; this fix repairs that gate's
  Requirement-Sufficiency classifier.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites the
  governing specifications for the change.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan derives
  tests from the operative-state contract being repaired.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries
  Project Authorization, Project, and Work Item metadata.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is bounded by
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`
  (allows `source` + `test_addition`), covering WI-4671 via active project
  membership.
- `GOV-STANDING-BACKLOG-001` — WI-4671 is the standing-backlog defect record for
  this work.
- `GOV-RELIABILITY-FAST-LANE-001` — a small, bounded reliability defect fix.
- `.claude/rules/file-bridge-protocol.md` § "Mandatory Implementation-Start
  Authorization Metadata" — the "exactly one operative state" contract this fix
  makes the classifier honor.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the defect is preserved as a durable
  artifact (WI-4671) and remediated through the governed bridge protocol.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — favors a reviewable artifact (this
  proposal + WI-4671 + DELIB-20265284) over ad-hoc in-session repair.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the dispatch hot-loop observation crossed
  the threshold from session observation into a tracked defect artifact.

## Prior Deliberations

- `DELIB-20265284` — owner AUQ decision ("Park now + fix parser", 2026-06-18) that
  authorized parking the poison-pill thread and filing this fix proposal. Linked
  to WI-4671.
- FAB-14 / HYG-046 — introduced the two bounded regexes (`REQUIREMENT_GAP_RE`,
  `REQUIREMENT_SUFFICIENCY_RE`) replacing the former per-incident literal phrase
  list. This proposal does not alter those regexes; it adds operative precedence
  in the classifier that consumes them.
- `bridge/gtkb-stale-git-worktree-autogc-diagnosis-003.md` — the DEFERRED park
  whose recorded resume condition is exactly this fix landing VERIFIED.

## Owner Decisions / Input

This work is authorized by the owner AUQ answer "Authorize + file fix now" in the
interactive Prime Builder session on 2026-06-18, recorded as `DELIB-20265284`
(outcome=owner_decision, approval packet `approved_by=owner`). That decision
authorized adding WI-4671 to the bridge-protocol-reliability project/PAUTH scope
and filing this NEW parser-fix proposal for Loyal Opposition review. No further
owner decision is required to review or implement within the bounded
`source` + `test_addition` authorization.

## Requirement Sufficiency

Existing requirements are sufficient. The governing specifications listed above —
the file-bridge-protocol operative-state contract, the bridge-authority and
project-authorization governance, and the FAB-14/HYG-046 regex contract — fully
constrain this minimal classifier fix. No new or revised requirement is needed.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | No credential material; logic-only change. | Credential scan on the bridge write + diff review. | |
| CQ-PATHS-001 | Yes | Edits limited to the two declared `target_paths`. | `git diff --name-only` matches `target_paths`. | |
| CQ-COMPLEXITY-001 | Yes | The change reduces ambiguity; no new branches beyond the two-match precedence check. | Diff review. | |
| CQ-CONSTANTS-001 | N/A | No constants changed. | Diff review. | Logic-only. |
| CQ-SECURITY-001 | Yes | No weakening of an authorization control; the fix makes the gate stop FALSE-rejecting a correctly-GO'd proposal and preserves genuine gap detection. | New regression tests for gap-leads and present-tense gap cases. | |
| CQ-DOCS-001 | Yes | Inline comment documents the operative-precedence rationale and cites WI-4671. | Diff review. | |
| CQ-TESTS-001 | Yes | New precedence tests added to the dedicated FAB-14 test module. | `python -m pytest platform_tests/scripts/test_fab14_requirement_sufficiency.py -q`. | |
| CQ-LOGGING-001 | N/A | No logging change. | Diff review. | Logic-only. |
| CQ-VERIFICATION-001 | Yes | Exact commands + observed results captured in the post-implementation report. | LO reproduces the pytest + ruff runs. | |

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` / file-bridge-protocol operative-state contract:
  add regression tests to `platform_tests/scripts/test_fab14_requirement_sufficiency.py`
  asserting `requirement_sufficiency_state()` returns:
  1. `"sufficient"` for the exact `gtkb-stale-git-worktree-autogc-diagnosis-001`
     Requirement-Sufficiency body (sufficiency leads, conditional gap trails) —
     the reported regression;
  2. `"gap"` when a present-tense gap declaration leads and a sufficiency phrase
     trails;
  3. `"sufficient"` for a sufficiency-only section;
  4. `"gap"` for a present-tense gap-only section;
  5. `"missing"` for an absent section and `"unrecognized"` for a non-matching
     section (existing behavior preserved).
  Expected result: all pass.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run
  `python -m pytest platform_tests/scripts/test_fab14_requirement_sufficiency.py
  platform_tests/scripts/test_implementation_authorization.py -q` and confirm no
  regression in the existing suite. Expected: all pass.
- Code-quality gates: `ruff check scripts/implementation_authorization.py
  platform_tests/scripts/test_fab14_requirement_sufficiency.py` and
  `ruff format --check` on the same paths. Expected: clean.
- End-to-end confirmation: re-run `requirement_sufficiency_state()` against the
  parked `-001` body and confirm `"sufficient"`; this is the resume-condition
  evidence for `gtkb-stale-git-worktree-autogc-diagnosis`.

## Risk / Rollback

Risk is low and bounded. The change is a logic-only refinement to one classifier
function on a defined input section; it does not alter the regexes, the
authorization packet schema, or any other gate. The principal risk is
mis-ordering precedence such that a genuine gap-leads proposal is mis-read as
sufficient — covered directly by verification case (2). Rollback is a
single-commit revert of the two-file change; no state migration is involved.

## Recommended Commit Type

`fix:` — repairs broken classifier behavior (a false-positive authorization
rejection) with no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
