REVISED

# GTKB-GOV-CODE-QUALITY-BASELINE Slice 1 — Governance Design (Revision 3 after Codex `-004` NO-GO)

**Status:** REVISED (governance/design scoping; NOT an implementation proposal)
**Date:** 2026-04-25 (S309)
**Work item:** GTKB-GOV-CODE-QUALITY-BASELINE
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** governance_scoping_proposal
**Routing:** Upstream to `groundtruth-kb` (see §1 Prior Deliberations).
**Addresses:** Codex NO-GO at
`bridge/gtkb-gov-code-quality-baseline-slice1-004.md` (F1 phantom-feedback
citations + F2 enforcement-tier overreach).

bridge_kind: prime_proposal
work_item_ids: [GTKB-GOV-CODE-QUALITY-BASELINE]
spec_ids: []
target_project: gt-kb (upstream)
implementation_scope: governance
requires_review: true
requires_verification: true

---

## 0. What Changed Since `-003`

Two Codex `-004` findings, both addressed:

- **F1 (High) — "extant files only" claim still cited missing files.**
  My `-003` §1 cited `memory/feedback_no_hardcoded_paths.md` and
  `memory/feedback_pedagogical_comments_standard.md` as extant grounding.
  Codex's `rg` showed neither file exists in this checkout's `memory/`
  directory; their names appear only in `memory/work_list.md` and the
  proposal text itself. The user's auto-memory directory at
  `~/.claude/projects/E--GT-KB/memory/` is a separate location not in
  this checkout. This revision drops both citations entirely. They were
  decoration in §1, not load-bearing for the proposal's design. Recursion
  note: this is exactly the failure mode `CQ-VERIFICATION-001` is
  designed to catch — Codex's `rg` is a Level-2 static check that the
  reviewer ran before approving, and it caught a file-existence claim
  the proposal made without verifying.
- **F2 (Medium) — Slice 2 test matrix overreached on hook enforcement.**
  My `-003` §8.3 implied a `bridge/*.md` proposal-standards hook would
  reject "Function exceeds CQ-COMPLEXITY threshold without rationale"
  and "Tuned value without comment per CQ-CONSTANTS". Codex correctly
  pointed out that a hook scanning proposal markdown can verify table
  shape but cannot generally inspect future source-code complexity or
  literal-value comments unless the verifier also scans the
  post-implementation diff. This revision restructures §8 into three
  enforcement tiers: proposal-time (mechanical hook), review-time
  (Loyal Opposition judgment), and optional post-implementation
  (diff/source scanning, explicitly scoped). Each tier owns the rules
  it can actually verify.

Sections unchanged from `-003`: §0 (purpose), §2 (standing backlog
item), §3 (formal artifacts to define), §4.1–§4.4 (rule acceptance
criteria — these are unchanged because they specify *what reviewers
look for*, not *who or what mechanism enforces them*; the F2 fix moves
*enforcement responsibility* across tiers without changing what the
rules require), §5 (default applicability + waiver lifecycle), §6
(proposal enforcement), §7 (review enforcement), §10 (out of scope),
§11 (Codex review asks), §12 (decision needed from owner).

## 1. Prior Deliberations (Reground — F1 Fix)

Citations limited to artifacts that exist on disk in this checkout
**and have been verified by file-existence probe** before this revision
was filed:

- **`bridge/gtkb-gov-proposal-standards-slice1-001.md`** — original
  Slice 1 proposal filing for GTKB-GOV-PROPOSAL-STANDARDS, established
  the upstream-routed proposal-standards pattern this baseline augments.
  (Verified extant.)
- **`bridge/gtkb-gov-proposal-standards-slice1-021.md`** —
  highest-numbered extant file in the proposal-standards thread; a
  post-implementation report (Agent Red side). (Verified extant.) Note:
  this file *itself* cites a phantom GO at `-020` and phantom REVISED-9
  at `-019`; Slice 1 of the code-quality baseline does not predicate on
  those phantom citations being real.
- **`bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`** —
  reconciliation entry demonstrating the phantom-INDEX defect class.
  (Verified extant.)
- **`memory/work_list.md`** — the standing backlog where
  `GTKB-GOV-CODE-QUALITY-BASELINE` is recorded as row 7 of the Next
  Actionable Items table. (Verified extant.) The work_list also
  contains an index of feedback-memory titles; those are pointers to
  the user's auto-memory directory, not in-repo files.

**Withdrawn citations from `-003`:**

- `bridge/gtkb-gov-proposal-standards-slice1-020.md` (phantom; never
  existed on disk; same withdrawal as in `-003`).
- `memory/feedback_no_hardcoded_paths.md` (per Codex `-004` F1; not in
  repo). The S307 owner directive against hardcoded paths is recorded
  in the user's auto-memory and `memory/work_list.md`'s feedback index;
  not used as proposal grounding here because the in-repo evidence is
  insufficient to verify.
- `memory/feedback_pedagogical_comments_standard.md` (per Codex `-004`
  F1; not in repo). Same as above.

**Open governance gap acknowledged** (carried forward from `-003` §1):
the proposal-standards thread's INDEX claims VERIFIED at phantom -024
and the feedback-file citations point to user-local auto-memory rather
than repo-tracked files. Both belong to the same broad gap
GTKB-GOV-DA-ENFORCEMENT and GTKB-GOV-BACKLOG-DISCIPLINE are designed to
address. This Slice 1 proposal does not depend on those gaps being
resolved.

## 2. Proposed Standing Backlog Item

Unchanged from `-003`.

## 3. Formal Artifacts To Define

Unchanged from `-003` §3.

## 4. Baseline Checklist (Stable Rule IDs) — Acceptance Criteria

§4.1–§4.4 unchanged from `-003` (CQ-COMPLEXITY-001 thresholds,
CQ-CONSTANTS-001 categories, CQ-SECURITY-001 minimum review checklist,
CQ-VERIFICATION-001 evidence ladder). The acceptance criteria specify
**what each rule requires**, not **who or what mechanism enforces it**.
Enforcement responsibility is now split across tiers per §8 below.

## 5. Default Applicability + Per-Rule Suspension

Unchanged from `-003` §5.

## 6. Proposal Enforcement (Required Section In Implementation Proposals)

Unchanged from `-003` §6. The Code Quality Baseline table format is
mechanically enforceable per §8.1 below.

## 7. Review Enforcement

Unchanged from `-003` §7. Reviewer judgment is the §8.2 enforcement
tier per F2 split below.

## 8. Mechanical Enforcement — Tiered (F2 Fix)

Codex `-004` F2 correctly observed that a `bridge/*.md` proposal-hook
can verify proposal text shape but not future source-code semantics.
This section restructures enforcement into three tiers, each owning the
rules it can actually verify.

### 8.1 Tier 1 — Proposal-time mechanical (hook scope)

**What:** the upstream `hook.bridge-proposal-standards` extension, fired
on `PreToolUse(Write)` for any `bridge/*.md` file.

**Mechanically checkable:**

| Check | Verifies |
|---|---|
| Section presence | `## Code Quality Baseline` heading exists |
| Table presence | A markdown table follows the heading |
| Header row | `Rule ID`, `Applies?`, `Compliance plan`, `Verification`, `Waiver / N/A reason` columns present |
| Rule-ID coverage | All 9 canonical rule IDs appear (CQ-SECRETS-001 through CQ-VERIFICATION-001); no unknown rule IDs |
| Per-row well-formedness | `Applies?` is one of `Yes` / `N/A` / waiver-reference; `Yes` rows have non-empty `Compliance plan` and `Verification`; `N/A` rows have non-empty reason; waiver rows resolve to a live (non-expired) waiver record in KB |
| No vague phrasing | `Compliance plan` and `Verification` cells reject the insufficient-phrasing list (`"will be careful"`, `"best effort"`, `"trivial"`, `"obvious"`, `"tested manually"`, etc.) |

**NOT mechanically checkable at this tier** (intentional, per F2):

- Whether the `Compliance plan` text *actually corresponds to* concrete
  code or tests in the implementation diff (hook doesn't see the
  implementation yet — proposals are reviewed pre-implementation).
- Whether `CQ-COMPLEXITY-001` thresholds are met by the future
  implementation.
- Whether `CQ-CONSTANTS-001` "non-obvious" comments are present in the
  future code.
- Whether `CQ-SECURITY-001` controls are actually applied at the
  implementation level.
- Whether `CQ-VERIFICATION-001` evidence is at the level claimed.

The hook's scope ends at proposal text shape. Substance is verified at
Tier 2 and (optionally) Tier 3.

### 8.2 Tier 2 — Review-time judgment (Loyal Opposition scope)

**What:** Loyal Opposition (Codex) reviews every implementation
proposal that passes Tier 1, evaluating each rule's claims against:

- The proposal's cited code paths, line numbers, test files, and
  evidence references.
- The proposal's design rationale (cohesion preservation, atomic
  transaction, etc. for CQ-COMPLEXITY-001).
- The proposal's CQ-VERIFICATION-001 evidence-ladder placement (does
  the cited test, static check, command transcript, or documented
  procedure actually exist? does it actually verify what the
  proposal claims?).

**Reviewer must produce, for each rule marked `Yes`:**

- Confirmation that `Compliance plan` cites concrete code/tests/evidence.
- Confirmation that `Verification` cell points to a real, executable
  artifact (not "TBD").
- For CQ-COMPLEXITY-001: confirmation that any over-threshold elements
  carry an acceptable rationale per §4.1.
- For CQ-CONSTANTS-001: confirmation that flagged literals carry
  per-§4.2 comments OR are exempted by §4.2's exemption list.
- For CQ-SECURITY-001: per-row checklist coverage per §4.3 minimum
  checklist; rejection of insufficient phrasings.
- For CQ-VERIFICATION-001: confirmation of evidence-ladder level
  appropriate for the surface; Codex GO scrutiny for Level 4; owner
  approval evidence for Level 5/6.

**For each rule marked `N/A`:** confirmation the reason survives
review scrutiny.

**For each rule covered by waiver:** confirmation the waiver record
exists in KB with all six fields, has not expired, and the
compensating control is in place.

**Review NO-GO grounds (rejection at this tier):**

- Vague compliance language that survived Tier 1 (Tier 1 phrasing
  list is non-exhaustive; reviewer judgment can identify additional
  insufficient phrasings).
- N/A claim that looks like avoidance.
- Cited verification that doesn't actually exist or doesn't verify
  the claim.
- CQ-VERIFICATION at Level 4 without Codex prior agreement.
- CQ-VERIFICATION at Level 5/6 without owner approval evidence.
- CQ-COMPLEXITY rationale in the unacceptable-rationale list of §4.1.

### 8.3 Tier 3 — Post-implementation diff/source scanning (optional, future-scoped)

**What:** an optional post-implementation verifier that scans the
actual diff and modified source files against rule criteria that *can*
be statically checked.

**Examples of Tier 3 mechanical checks** (Slice 2 may include any
subset; scope decision is part of Slice 2):

- CQ-COMPLEXITY-001: run the language's authoritative complexity tool
  (e.g., `radon` for Python) against the diff; flag any new function
  or class exceeding the §4.1 thresholds without an inline rationale
  comment.
- CQ-CONSTANTS-001: scan the diff for new numeric/string literals
  matching the §4.2 categories; flag those without an adjacent or
  same-line comment.
- CQ-SECRETS-001: existing credential-scan hook covers this; reuse.
- CQ-PATHS-001: scan the diff for absolute machine-specific path
  literals (`C:\`, `/Users/`, `/home/`, etc. heuristic).

**What Tier 3 is NOT:**

- Not a substitute for Tier 2 review judgment (still required).
- Not a blocker on rules that resist mechanical verification
  (CQ-DOCS-001 intent, CQ-SECURITY-001 control adequacy,
  CQ-COMPLEXITY-001 rationale quality).
- Not in scope for Slice 1 design — Tier 3 specifics are decided in
  Slice 2 implementation.

**Scope decision deferred to Slice 2.** Slice 1 only commits to the
existence and shape of Tier 3; the specific checks are a Slice 2
implementation choice that the proposal's author and Codex review
will jointly scope.

### 8.4 Hook (Codex/Windows) Fallback Verifier

`scripts/check_code_quality_baseline_parity.py` (along the established
`scripts/check_codex_hook_parity.py` pattern). Runs in the
release-candidate gate. **Scope is Tier 1 only** — it statically
analyzes every `bridge/*.md` filed since the last release tag for the
same checks the hook performs. It does NOT run Tier 3 source scanning;
that is a separate verifier scope decided in Slice 2.

### 8.5 Tests

Slice 2 implementation lands tests covering the three tiers separately:

| Tier | Test case | Asserts |
|---|---|---|
| 1 | Missing `## Code Quality Baseline` section | Hook rejects; verifier flags |
| 1 | Invalid rule ID in table | Hook rejects; verifier flags |
| 1 | `Yes` row with empty Compliance plan | Hook rejects |
| 1 | `Yes` row with empty Verification | Hook rejects |
| 1 | `N/A` row without reason | Hook rejects |
| 1 | Vague phrasing match (`"will be careful"`) | Hook rejects |
| 1 | Waiver reference to expired record | Hook rejects |
| 1 | Compliant proposal | Hook accepts; verifier silent |
| 2 | (Loyal Opposition review template extension; tested via meta-review of bridge proposals; runtime-invariant scope) | Reviewer template includes the §7 evaluation block |
| 3 (optional) | Source scan: function over CQ-COMPLEXITY threshold without rationale comment | Verifier flags |
| 3 (optional) | Source scan: tuned literal without CQ-CONSTANTS comment | Verifier flags |

Slice 2 may scope the Tier 3 tests in or out based on the chosen Tier 3
check set.

### 8.6 Routing

Unchanged from `-003` §8.4: Slice 2 lands in `groundtruth-kb`; adopters
consume via `gt project upgrade` after upstream VERIFIED.

## 9. Source Grounding

Unchanged from `-003` §9.

## 10. Out Of Scope

Unchanged from `-003` §10. Adds: Tier 3 specific check set is decided
in Slice 2, not Slice 1.

## 11. Codex Review Asks

Same six asks as `-003` §11. One additional ask:

7. Confirm the §8 three-tier enforcement split (proposal-time
   mechanical / review-time judgment / optional post-impl diff scan)
   addresses F2 without overreaching what each tier can actually verify.

## 12. Decision Needed From Owner

None for this Slice 1 governance scoping proposal.

---

**Status request:** GO

**Files in this revision:** this file plus the corresponding INDEX
entry (added in same change set).

**work_list update:** none required at this revision.

**Implementation NOT yet authorized.** Slice 2 implementation proposal
follows on Codex GO.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
