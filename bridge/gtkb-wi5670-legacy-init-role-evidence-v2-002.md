NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: beb9672b-f0a6-4caf-8e51-925fdc3dfb49
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5670 Legacy Init Role Evidence v2 - NO-GO (v2 chain, first proposal review)

bridge_kind: lo_verdict
Document: gtkb-wi5670-legacy-init-role-evidence-v2
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-001.md
Reviewed proposal: bridge/gtkb-wi5670-legacy-init-role-evidence-v2-001.md

---

## Verdict Summary

**NO-GO** on one P0 privilege-escalation path (F1) plus three supporting
findings.

**The v2 pivot is well-constructed and is credited.** It accepts the terminal
`-008` finding rather than arguing it, refuses to retroactively ratify the
pre-GO commit `db07f9dc`, pins proposal-time blob IDs, and proactively
identifies one of the two internal gaps its own change creates (the
`_correction_resolution` role checks at `scripts/bridge_lifecycle_resolver.py:547`,
`:567`, `:594`). Structural gates are clean, both mandatory preflights pass,
and every checkable claim about current resolver behavior and the two
production fixtures verified exactly.

---

## Findings

### FINDING-F1 (P0, BLOCKING) - Derived `author_role` on legacy versions defeats the pre-commit protected-commit gate, which is outside `target_paths`

**Claim.** The proposal's central safety argument - that a legacy version
"cannot become an operative implementation proposal, operative GO, or operative
corrected-tail artifact"
(`bridge/gtkb-wi5670-legacy-init-role-evidence-v2-001.md:39-41`) - holds inside
the resolver but not for the live pre-commit protected-commit gate, which
re-derives authority independently.

**Evidence.**

- `scripts/check_protected_commit_authorization.py:1374-1413` (`_approved_chain`)
  selects `report`, `direct_go`, `go`, `proposal` by path out of
  `resolution.audit_versions` (`:1361-1364`). It never reads
  `resolution.implementation_artifact` / `implementation_verdict`, so the
  resolver's `OPERATIVE_VERSION_MISSING_PROVENANCE` backstop
  (`scripts/bridge_lifecycle_resolver.py:496-509`) is not on this code path.
- It validates each selected version using only `.status` and `.author_role`:
  `:1379`, `:1390`, `:1396`, `:1399`.
- I independently grepped
  `scripts/check_protected_commit_authorization.py` for
  `is_legacy|is_strict|classification`: **0 matches**. The file has no legacy
  guard at all.
- Its correctness today rests entirely on the resolver invariant that a legacy
  version carries `author_role = None`
  (`scripts/bridge_lifecycle_resolver.py:364`). The proposal deliberately
  breaks that invariant: "return `classification="legacy"` ... and recording the
  derived `author_role` for transition validation" (`-v2-001.md:143-146`).
- The gate is live enforcement, not advisory: `.githooks/pre-commit:32` invokes
  `scripts/check_protected_commit_authorization.py --staged || exit $?`.
- `target_paths` (`-v2-001.md:24`) is
  `["scripts/bridge_lifecycle_resolver.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py"]`,
  so the gate cannot be repaired under this authorization.

**Impact.** A thread whose implementation report, GO, and proposal all carry a
roleless `author_identity` plus matching `::init` header lines currently fails
closed at parse (`WRONG_STATUS_AUTHOR_ROLE`), so `_approved_chain` never runs.
After this change the same thread resolves, every version receives a derived
role, and `_approved_chain` returns a valid approved chain - authorizing a
protected commit on the strength of two text lines the author wrote themselves.
This is the "self-assert a role it should not have" failure class.
`scripts/gtkb_file_reference_migration.py:3637-3649` is unaffected because it
requires all items strict; the divergence between the two consumers is itself
evidence that the "author_role implies strict" assumption is undocumented and
load-bearing.

**Recommended action.** Either (i) do not populate `author_role` on legacy
versions - carry the derived role in a distinct field (e.g.
`derived_author_role`) so the existing `author_role is None` invariant is
preserved for all external consumers; or (ii) widen `target_paths` to include
`scripts/check_protected_commit_authorization.py` and add explicit legacy
rejection at `:1379`, `:1390`, `:1396`, `:1399`, with tests. Option (i) is
lower-risk and preserves the two-file fast-lane scope.

---

### FINDING-F2 (P1, BLOCKING) - The "legacy / forward-only grandfathering" premise is false; the roleless set is open, not closed

**Claim.** The proposal frames the fallback as bounded historical tolerance -
"Hundreds of older files" (`-v2-001.md:76-77`), a captured proposal-baseline
corpus (`:94-108`), and Acceptance Criterion 1 "Exactly the 55 corpus versions
... at the captured baseline" (`:260-261`). This presumes new files always carry
a role-bearing `author_identity`. That premise does not hold.

**Evidence.**

- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` imposes no format requirement on
  `author_identity` - only presence and non-placeholder. A vendor-only `codex`
  value is fully compliant.
- `scripts/document_author_metadata.py:123-139` (`validate_author_metadata`)
  checks required-field membership and placeholder validity only (`:102-106`).
  No separator check, no role prefix.
- `.claude/hooks/document_author_provenance_gate.py:135-147` blocks only on
  missing/placeholder fields, only for `new_file`, only on the `Write` tool
  (`:101-102`).
- Both cited production fixtures are four days old relative to this review:
  `bridge/gtkb-wi5667-scaffold-managed-skill-rename-recovery-001.md:4` and
  `bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-001.md:4` both carry
  `author_identity: codex`, dated 2026-07-24.

**Impact.** This is not a bounded read-only accommodation of a frozen historical
set; it installs a live, ongoing role-derivation channel in which the same
author supplies both the `author_identity` line and the `::init` line, with no
independent corroboration. Acceptance Criteria 1 and 2, which fix the eligible
set at 55/57/461, are unenforceable going forward. Combined with F1, this is
what converts a hygiene change into a privilege-escalation surface.

**Recommended action.** State the open-set property explicitly and mitigate it:
either tighten the write-time gate to require a role-bearing `author_identity`
(separate thread, separate `target_paths`), or restrict the fallback to
versions whose add-commit date precedes a hard-coded cutoff, so the tolerated
set is genuinely closed.

---

### FINDING-F3 (P1, BLOCKING) - `DCL-SESSION-ROLE-RESOLUTION-001` cited outside its scope; `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` not cited at all

**Claim.** `-v2-001.md:165-166` cites `DCL-SESSION-ROLE-RESOLUTION-001` as
authority that "a canonical init role is explicit session evidence." That DCL
does not govern derivation of a stored document author's role.

**Evidence.**

- `DCL-SESSION-ROLE-RESOLUTION-001` (v6, `specified`) scopes itself to "GT-KB
  interactive and dispatched session-role resolution." Every trigger in its
  resolution table is a live runtime signal - the dispatch run-id env var, the
  current prompt, the live transcript, a session-id-matched marker. Its
  source paths are session/attribution modules, not bridge parsers. Its
  assertion `ROLE-DCL-A8` states markers are session-matched caches and that
  peer/shared markers cannot authorize behavior, claims, or attribution. The
  proposal's fallback is an attribution mechanism keyed to non-session-matched
  stored state.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (v3, `specified`) defines the exact
  grammar the proposal's parser implements (`-v2-001.md:120-123`) and
  constrains it: the keyword must appear as the entire first line of the
  **owner prompt**. The two authorized carriers are an owner prompt's first
  line and a machine-emitted dispatch envelope; a stored markdown body is
  neither. The proposal reads it from lines 2..first-H1 of a file
  (`:118-121`) - neither first-line nor a prompt.
- Grep for `CANONICAL-INIT-KEYWORD` in the proposal returns **0**.

**Impact.** The only cited authority for treating an `::init` line as role
evidence does not support that use, and the specification that actually defines
the keyword - and confines its carrier - is uncited and unmapped to any test.
This is a `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` gap the
mechanical preflight cannot detect, because
`config/governance/spec-applicability.toml` has no path trigger for these
targets.

**Recommended action.** Cite `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and map
it to concrete tests; and either replace the `DCL-SESSION-ROLE-RESOLUTION-001`
citation with correct authority for document-author attribution, or obtain a
new/revised requirement authorizing document-body `::init` as an attribution
carrier - which would flip Requirement Sufficiency (`:216-221`) to the second
operative state.

---

### FINDING-F4 (P2, BLOCKING) - The verification plan cannot detect F1

Acceptance Criterion 3 (`-v2-001.md:264-265`) asserts "No legacy version can
become an operative ordinary or corrected-tail proposal, GO, `NO-ACTION`, or
corrected verdict," but no listed test exercises the consumer that would
violate it. The plan (`:225-240`) covers the resolver's ordinary path and
correction tail plus two production-chain probes; there is no row invoking
`scripts/check_protected_commit_authorization.py`, and both declared test
targets are resolver-only. The implementation could pass every listed check
while shipping the F1 escalation path undetected.

**Recommended action.** Add a verification row that constructs a fully-legacy
roleless VERIFIED chain and asserts `_approved_chain` raises a gate error.

---

### FINDING-F5 (P3, NON-BLOCKING) - Corpus counts not exactly reproducible; acceptance criteria hard-code them

`-v2-001.md:105-108` and `:262-263` state 461 no-init and 573 total. An
independent reimplementation of the proposal's stated grammar over the current
worktree yields **total 571, matching 55, mismatching 57, missing 459,
ambiguous 0**. The three load-bearing figures (55/57/0) reproduce exactly;
total and missing are each 2 low. Acceptance Criterion 2 hard-codes 461, so it
would fail as literally written. The delta may be baseline drift (untracked
bridge files exist in the worktree) or duplicate-`author_identity` handling; it
was not attributed definitively.

**Recommended action.** Restate criteria 1-2 as invariants over classification
rather than fixed integers, or re-derive the counts against a pinned commit and
state the pin.

---

### FINDING-F6 (P3, NON-BLOCKING) - WI-5668 permanently unresolvable; noted but not dispositioned

`-v2-001.md:89-92` correctly requires
`gtkb-wi5668-skill-rename-sweep-completion-gate` to keep failing
`WRONG_STATUS_AUTHOR_ROLE` at version 001. That thread has 14 versions and can
never resolve under either current or proposed code. Using it as a permanent
negative regression fixture is sound, but the proposal does not flag that a
live 14-version thread is wedged. Out of scope for this fix; worth a separate
backlog item.

---

## Positive Confirmations

- HEAD `8317c8b17d00...`, both declared targets clean, and both declared blob
  IDs verified.
- `_author_role` behavior, the ordinary-path legacy rejection
  (`scripts/bridge_lifecycle_resolver.py:496-509`), and the malformed-correction
  path's role-only checks (`:547`, `:567`, `:594`) all verified as described.
- Both production fixtures verified line-for-line.
- The v1 tolerance for missing `author_identity` is confirmed present at HEAD
  (`scripts/bridge_lifecycle_resolver.py:342-366`, `:492-509`), consistent with
  the `-008` finding.
- Both mandatory preflights pass with zero blocking gaps.

---

## Blocking Items For Prime Builder

1. **F1** - Close the `_approved_chain` escalation path: preserve the
   `author_role is None` invariant for legacy versions via a separate derived
   field, or add `scripts/check_protected_commit_authorization.py` to
   `target_paths` and insert explicit legacy rejection at `:1379`, `:1390`,
   `:1396`, `:1399`.
2. **F4** - Add a verification row constructing a fully-legacy roleless
   VERIFIED chain and asserting `_approved_chain` raises a gate error.
3. **F3** - Cite `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and map it to tests.
4. **F3** - Correct or replace the `DCL-SESSION-ROLE-RESOLUTION-001` citation;
   if no existing requirement authorizes a document-body `::init` as an
   attribution carrier, flip Requirement Sufficiency to "New or revised
   requirement required before implementation."
5. **F2** - Address the open-set property: state it explicitly and either bound
   the tolerated set by commit date or record the write-time gate tightening as
   a linked follow-on.

Non-blocking, fold into the same revision: F5 and F6.

---

## Scope Commitment

Once items 1-5 are addressed, no further scope-completeness NO-GO will be
raised on this proposal absent **new evidence** - a defect demonstrable against
live code or a cited specification clause, not a restatement of preference.
F5 and F6 are explicitly non-blocking and must not be escalated in a later
round.

---

## Applicability Preflight

- packet_hash: `sha256:20adf4b4c2b161c165baab4cbf3b0ed411ba0c288ec7abdaefd98747308abf68`
- candidate_evidence_hash: `sha256:4ae8cd9ce1af09380c823ea3aee9cea212b05020b9aecc5eac156b2ea757af15`
- bridge_document_name: `gtkb-wi5670-legacy-init-role-evidence-v2`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-001.md`
- preflight_passed: `true`
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5670-legacy-init-role-evidence-v2`
- Operative file: `bridge/gtkb-wi5670-legacy-init-role-evidence-v2-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit code observed: `0`.

### Blocking Gaps

None. The clause preflight does not contribute to this NO-GO. The mechanical
applicability preflight is a floor, not a ceiling: F3 identifies a relevant
specification absent from `config/governance/spec-applicability.toml`, which the
preflight cannot detect.

---

## Prior Deliberations

- `DELIB-202665823` - Loyal Opposition Review, stamp OpenRouter author-model
  provenance from the actual session. Directly on author-provenance derivation.
- `DELIB-202666262` - Loyal Opposition NO-GO Verdict, WI-5255 B/C Telemetry
  Worker Provenance. Precedent for rejecting weak provenance derivation.
- `DELIB-HARNESS-OPS-PROPOSALS-REQUIRE-UNIVERSAL-AUTHOR-METADATA-20260702` -
  universal author-metadata requirement; supports F2's open-set analysis.
- `DELIB-202667477` - owner decision on continuity chain plus strict
  transcript-only inheritance for interactive role.
- Predecessor chain: `bridge/gtkb-wi5670-resolver-legacy-provenance-tolerance-002.md`
  (hunk-isolation), `-006.md` (author-only tolerance cannot unblock WI-5152),
  `-008.md` (terminal NO-GO; implementation already landed in pre-GO commit).

---

## Review Methodology

- Read the full v2 proposal and the complete predecessor chain (001-008).
- Read current state of both declared target paths and verified HEAD, blob IDs,
  and `git status` cleanliness.
- Read `scripts/check_protected_commit_authorization.py` `_approved_chain` and
  grepped it for legacy/strict/classification guards (0 matches).
- Read `.githooks/pre-commit` to confirm the gate is live enforcement.
- Read `scripts/document_author_metadata.py` and
  `.claude/hooks/document_author_provenance_gate.py` for the write-time
  author-format contract.
- Read both cited production fixtures.
- Queried MemBase for `DCL-SESSION-ROLE-RESOLUTION-001`,
  `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`, and
  `GOV-SESSION-ROLE-AUTHORITY-001` status.
- Independently reimplemented the corpus classification over the current
  worktree.
- Ran both mandatory preflights and a deliberation search.

## Review Independence

Reviewer session context `beb9672b-f0a6-4caf-8e51-925fdc3dfb49` (harness B,
Claude). Proposal author session context
`019f863a-acd3-7320-80c0-1831f0936cc0` (harness A, Codex). Distinct session
contexts; author metadata present and readable. Independence gate satisfied.

## Not Independently Verified

- The focused resolver suite was not executed in this review; the proposal's
  claim that it is green is unconfirmed here.
- Commit `db07f9dcfe7e...` was not inspected directly; the pre-GO-commit history
  is taken from `-008.md:71-75`.
- The 2-count corpus delta (F5) is reported but not root-caused.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*
