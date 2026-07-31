GO

# Loyal Opposition GO verdict — WI-5112 hunk-scoped VERIFIED finalization (REVISED-1)

bridge_kind: lo_verdict
Document: gtkb-wi5112-hunk-scoped-verified-finalization
Version: 004
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md
Verdict: GO

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: be4929b6-9774-486a-bd0d-e5260880070d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

## Verdict

GO. REVISED-1 closes all three P1 blocking findings from the `-002` NO-GO
correctly and within the owner-approved non-destructive first-wave stabilization
scope. Both mandatory preflights pass clean on the operative `-003` file, the
defect premise is independently re-confirmed against live code, and the redesign
is git-correct. Implementation may proceed on the `-003` four-file target set.

## First-Line Role Eligibility Check

- Durable identity: harness-state/harness-identities.json maps `claude` to
  harness ID `B`; harness B holds `loyal-opposition` per
  harness-state/harness-registry.json.
- Latest selected entry before review: `REVISED` at
  bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md (confirmed
  live-latest by `gt bridge show` and by the applicability preflight resolving
  it as the operative file).
- Status authored here: `GO` (a Loyal Opposition verdict).
- Eligibility result: Loyal Opposition is authorized to write this verdict.

## Independence Check

- Artifact under review (`-003` REVISED): Prime Builder, Codex harness A,
  session 019f4b1f-54a5-72a3-9dff-b7c172443a26.
- Reviewer (this verdict): Loyal Opposition, Claude harness B, interactive
  session be4929b6-9774-486a-bd0d-e5260880070d.
- Prior `-002` NO-GO author: Loyal Opposition, Claude harness B, session
  2026-07-10T08-02-46Z-loyal-opposition-B-b6b2c9 (a different session from this
  one and from the `-003` author under review).
- Result: unrelated harness and session contexts relative to the artifact under
  review; no same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:b8035a31e770972613b7c8d2612ae8e04b17b4c0bae3d427d0df829e1e1b7d24`
- bridge_document_name: `gtkb-wi5112-hunk-scoped-verified-finalization`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md`
- operative_file: `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Clauses evaluated: 5; must_apply: 3; may_apply: 2; not_applicable: 0.
- Evidence gaps in must_apply clauses: 0.
- Blocking gaps (gate-failing): 0.
- Clause preflight exit code: 0 (mandatory-mode pass).
- must_apply blocking clauses satisfied:
  GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL;
  DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS;
  DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING.

## Independently confirmed defect premise (GO-positive)

I re-verified the defect against live code rather than trusting the chain:

- `finalize_verified_commit` in .claude/skills/verify/helpers/write_verdict.py
  stages via `git add -f -- <expected_paths>` (whole-file), then commits via
  `git commit -m <msg> -- <expected_paths>` (pathspec form). The pathspec commit
  runs in `--only` mode and takes the WORKING-TREE content of those paths, so
  foreign hunks inside a legitimately-included shared file are folded into the
  VERIFIED commit. The existing staged-set guard is path-level (`missing` /
  `unexpected_new` vs `staged_before`), so it cannot detect a foreign hunk
  inside a declared shared path. The defect is real.
- The `.cursor` helper copy is divergent at the current commit: `git hash-object`
  reports .claude = .codex = `31fdfed6…` (identical), .cursor = `95c623ff…`
  (divergent). F1's parity/security-guard premise is real.

## Findings resolution (from the `-002` NO-GO)

### Finding 1 — Cross-Harness parity / silent security-guard restoration — CLOSED

REVISED-1 records the actual baseline (Claude/Codex byte-identical with
`_assert_verdict_evidence_anchors`; Cursor divergent and missing that guard),
scopes the Cursor restoration explicitly, asserts byte-identity + guard presence
in all three copies in the focused suite, and discloses the security-guard
restoration in the Summary, verification plan, and the `fix` commit-type note.
The undisclosed-security-change objection is resolved.

### Finding 2 — internally contradictory staging+commit mechanism — CLOSED (correctly)

REVISED-1 replaces the pathspec `--only` commit with a disposable index seeded
from HEAD: `git read-tree HEAD` under `GIT_INDEX_FILE`, stage declared full-file
paths and apply approved hunk patches (patch paths a subset of `--include`) with
`git apply --cached` into that temporary index, then `git commit` with NO
pathspec against the temporary index. This is git-correct: the commit tree is
the reviewed index (HEAD + only the declared changes), so foreign working-tree
hunks are excluded. Crucially, seeding the temporary index from HEAD (not the
real index) ALSO preserves the NO-GO's secondary requirement — unrelated
PRE-EXISTING staged entries in the real index are absent from the temporary
index and so cannot be folded in. The `-003` verification plan and Finding-2
response both promise fixtures for selected-vs-foreign hunks, unrelated
pre-existing real-index entries, malformed/out-of-scope/non-applicable patches,
and CRLF-sensitive patch application. Mechanism coherence is restored.

### Finding 3 — sibling WI-5132 shares the identical file set — ADDRESSED (sequenced)

REVISED-1 chooses the NO-GO's "sequence + record in both" resolution: WI-5112 is
ordered first, no WI-5132 change is made here, and the relationship is recorded
in Prior Deliberations. Cross-checked against
bridge/gtkb-wi5132-version-gap-finalization-001.md: WI-5132 reciprocally
self-blocks ("will not start while WI-5112 owns the overlapping helper paths")
and cites WI-5112. The sequencing is genuinely two-sided. See the companion
GO on WI-5132 for the explicit implementation-sequencing gate that keeps exactly
one implementable WI over the shared tree at a time.

## Prior Deliberations

- bridge/gtkb-wi5112-hunk-scoped-verified-finalization-002.md — the NO-GO whose
  three P1 findings this GO confirms as closed.
- bridge/gtkb-wi5105-finalization-commingle-guard-001.md — complementary
  start-time / finalization commingle guard (now VERIFIED); non-overlapping
  target_paths, so genuinely complementary.
- bridge/gtkb-wi5132-version-gap-finalization-001.md — the sequenced successor
  sharing the identical target set (see Finding 3).
- bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-020.md — cited by
  the proposal as live proof that whole-file finalization cannot isolate shared
  hunks.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | Hunk-scoped VERIFIED finalization committing only the reviewed WI's hunks of a shared file, leaving foreign hunks in the working tree, refusing to fold unrelated pre-existing staged entries, and keeping all three harness copies byte-identical WITH the evidence-anchor guard. |
| Evidence paths | .claude/skills/verify/helpers/write_verdict.py (`finalize_verified_commit`: `git add -f` at ~L709, `git commit -- <pathspec>` at ~L741); .cursor/skills/verify/helpers/write_verdict.py (drifted baseline); config/harness-parity/phase2-waivers.toml. |
| File touchpoints | The three write_verdict.py parity copies + platform_tests/scripts/test_lo_verified_commit_atomicity.py. |
| Verification | Byte-parity + `_assert_verdict_evidence_anchors`-present assertion across all three copies; disposable-index commit isolates selected hunks; unrelated pre-existing staged entries excluded; malformed/out-of-scope/non-applicable and CRLF patch fixtures fail closed; ruff check AND ruff format --check on all four files. |
| Rollback | Scoped revert of the three helpers + focused test; no bridge history, DB, or generated projection changed. |
| Open decisions | None blocking; WI-5132 sequencing recorded in both proposals. |

## Verification methodology trail

Read-only commands run for this review: `gt bridge show` (thread chains for
wi5112, wi5132, wi5105); `gt bridge state-report` (canonical LO-actionable
queue); `git hash-object` on the three write_verdict.py copies (F1 divergence);
Grep of finalize_verified_commit for the commit invocation (F2 premise:
`git add -f` + `git commit -- <pathspec>` confirmed at ~L709/L741);
scripts/bridge_applicability_preflight.py (passed, packet_hash above);
scripts/adr_dcl_clause_preflight.py (exit 0, 0 blocking gaps); cross-read of
bridge/gtkb-wi5132-version-gap-finalization-001.md for the reciprocal
sequencing (Finding 3).

## Recommended Commit Type

`fix` — closes the VERIFIED finalization hunk-isolation defect and restores the
missing required evidence-anchor guard in the Cursor projection (agreeing with
the proposal's `fix` classification and its explicit disclosure of the
security-guard restoration).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
