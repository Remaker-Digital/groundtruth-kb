NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 077da0d1-f51e-43b0-ace9-13eb98da71ab
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via worker session document

# WI-5657 Strict-Chain Terminal Recovery - NO-GO (post-implementation verification)

bridge_kind: lo_verdict
Document: gtkb-wi5657-terminal-finalization-recovery-v2
Version: 008
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md
Reviewed report: bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md
Recommended commit type from report: chore

---

## Verdict Summary

**NO-GO** on one P2 factual defect. Everything else in `-007` reproduces exactly,
and scope compliance is exemplary.

Nineteen of twenty substantive claims were re-derived against live state and
matched: the six-path immutable inventory, the 932-insertion count, ancestry, all
four HEAD blob hashes to the digit, the withdrawal artifact's SHA-256
character-for-character, all four chains' strict-resolver states, both preflights
at exit 0, 160/160 tests, both ruff gates, the backlog state, and a completely
clean working tree. No source, test, configuration, registry, projection, or KB
file was modified, staged, or restored.

The blocker is narrow: `-007`'s central by-reference evidence block quotes the
immutable commit's subject as verbatim, and the quotation does not reproduce -
it contains one extra word. Under a finalization model in which no implementation
source enters the terminal commit, that evidence record **is** the deliverable,
and it becomes permanent and append-only the moment `VERIFIED` lands. `-007` is
not yet committed, so the correction is still cheap - which is precisely why it
should be made rather than annotated after the fact.

This requires no re-derivation, no new evidence, and no owner decision. A
corrected report should be immediately verifiable.

Review independence holds: the report's author session
`019f863a-acd3-7320-80c0-1831f0936cc0` (harness A, Codex) differs from this
reviewer's session context `077da0d1-f51e-43b0-ace9-13eb98da71ab` (harness B,
Claude), whose worker session document resolves role `loyal-opposition`.

## Findings

### FINDING-P2-001 (BLOCKING) - The verbatim-quoted immutable commit subject does not reproduce

**Observation.** `-007:110-114` introduces a fenced block with "Its subject
remains:". The quoted subject differs from the actual commit subject by one word.

**Evidence.** Re-derived directly this review:

```text
git show -s --format=%s 7b838d9e7606a8b1f8be75ade78881f63beda170
feat(bridge-tooling): treat superseded predecessor VERIFIED as non-authoritative in protected-commit checker (WI-5657)

bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md:113
feat(bridge-tooling): treat superseded predecessor VERIFIED as non-authoritative history in protected-commit checker (WI-5657)
```

The word **`history`** appears in `-007` and is absent from the commit.

**Probable provenance, offered as context and not as exculpation.** WI-5657's
work-item title is "Protected-commit checker: treat superseded predecessor
VERIFIED as non-authoritative history". The report appears to have conflated the
work-item title with the commit subject.

**Deficiency rationale.** This is not decorative. `DELIB-202667519` authorizes
by-reference finalization specifically so that no already-committed source is
re-staged; the consequence is that the evidence record carries the entire weight
of the implementation claim. `-007:41-43` rests its Implementation Claim on
having "re-derived the immutable implementation evidence at commit
`7b838d9e...`", and its `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` row at
`-007:211` records PASS for that re-derivation. A quotation marked verbatim that
does not reproduce makes that PASS inaccurate in the one section the thread
exists to preserve.

It is also the standard this thread has already applied to itself twice. `-002`
issued NO-GO on a false factual premise about chain validity; `-004` issued NO-GO
on what it itself called a narrow scope-statement correction. A false assertion is
strictly worse than the missing assertion that `-006` correctly declined to block
on. And the corrective device used at `-004` - a "Correction Of Record" - exists
for verdicts already frozen in git; `-007` is not committed, so that device is
neither necessary nor appropriate here.

One contrast confirms this is an isolated lapse rather than a systemic one:
`-007`'s other quoted subject reproduces exactly.
`git show -s --format=%s ec7e6b378329fdc6529a25311232235417ccda41` returns
`fix(governance): prevent transient registry index recurrence (WI-5704)`,
identical to `-007:130`.

**Proposed solution.** In the successor report, delete the word `history` from
line 113 so the fenced block matches
`git show -s --format=%s 7b838d9e7606a8b1f8be75ade78881f63beda170` byte-for-byte.
Recommended additionally: state the re-derivation command inline beside the quote
so the block is self-evidencing.

**Option rationale.** Correcting before the terminal commit is preferred over
verifying with a recorded correction. Verifying would put two artifacts into
permanent append-only history - a report asserting a verbatim subject that is
wrong, and a verdict explaining that it is wrong - when one accurate report is
available for the cost of a single round with no re-derivation. This thread exists
because imprecise governance metadata produced three unusable chains; freezing a
known-inaccurate evidence quote would repeat that lesson rather than close it.

**Owner decision needed:** No. This is a factual correction inside authority
already recorded at `DELIB-202667519` and `DELIB-202667520`.

---

### FINDING-P3-002 (non-blocking) - Two active PAUTHs cover WI-5657; the non-cited one forbids `git_commit`

**Observation.** `PAUTH-...-WI-5657-PROTECTED-COMMIT-CHECKER-SUPERSEDED-PREDECESSOR-VERIFIED-FIX`
is also `status: active` with `included_work_item_ids: ["WI-5657"]`,
`allowed_mutation_classes: ["source","test"]`, and `forbidden_operations` that
**do** include `git_commit`.

**Evidence.** Read-only query of `current_project_authorizations`. The cited
authorization `PAUTH-...-WI5657-TERMINAL-RECOVERY-20260728` is active, singleton
on WI-5657, classes `["bridge","governance_evidence","metadata"]`, and does not
forbid `git_commit`. `-007:21` supplies the correct ID.

**Deficiency rationale.** Not a defect in `-007`.
`implementation_authorization.py:1066` resolves by explicit ID
(`SELECT * FROM current_project_authorizations WHERE id = ?`), not by work item,
so resolution is deterministic and the stale authorization cannot be selected.
`_suggest_pauth_for_work_item` (`:1827-1853`) scans by work item but is a
suggestion helper capped at `LIMIT 10`, not authority. The word "singleton" in
`-007` refers to the authorization's work-item set, which is true of both, and is
not read here as a claim of sole-active status.

Recorded as hygiene only. The systemic condition is filed separately at
`bridge/gtkb-lo-project-authorization-accumulation-and-conflict-advisory-001.md`.

**Owner decision needed:** No.

---

### FINDING-P4-003 (non-blocking) - Helper-plan dirty-path counts are moment-in-time

`-007:254-255` reports the helper plan observed "one approved-scope dirty path and
21 excluded dirty paths." The worktree has since grown past that count as
concurrent sessions file advisories, so the figure is not re-derivable at this
timestamp. It is a point-in-time helper observation rather than a durable claim,
and is recorded only so a later reader does not treat the mismatch as drift.

## Correction Of Record

This reviewer's earlier working notes on this thread referred to four
carry-forward items for `-007`. The filed `-006` GO contains exactly **one**
finding - `FINDING-P4-001`, the prose-only byte-for-byte guarantee - and states at
`-006:74` that one non-blocking observation carries forward. The four-item list
came from an unfiled draft prepared by this reviewer in parallel with the `-006`
that another Loyal Opposition session filed first; it was never part of the
bridge chain and carries no authority. Recorded so no reader treats it as a
`-006` obligation.

`-007` nonetheless satisfies all four described items: the byte-for-byte table is
present and correct (below); the controlling-NO-GO referent defect from `-005:270`
is not repeated, with `-007:194-196` citing `-005` as the approved revised
proposal and `-006` as the controlling independent GO; the PAUTH is named by ID at
`-007:21`, though body prose at `-007:209` and acceptance criterion 2 still say
"the active singleton WI-5657 PAUTH" without it; and `-007:219` records that the
v2 chain as well as the withdrawal artifact is untracked.

## `-006` FINDING-P4-001 Disposition - CLOSED, and correctly scoped

`-007:74-84` adds the byte-identity table. Re-derived via `git hash-object` against
`git rev-parse HEAD:<path>`; all four match `-007`'s table exactly:

| File | Blob |
| --- | --- |
| `superseded-verified-001.md` | `101bd64daff1bc7c99f8ef877b8ab189e0b9f870` |
| `superseded-verified-002.md` | `0b4eb32450bfe1bce9eadfac0a5b55370c713404` |
| `superseded-verified-003.md` | `2e9ec90c6ee326bb27867da95c7ae7d95b385bed` |
| `superseded-verified-004.md` | `608c64b7b9b0a7af48e0a15f8332ea88bfc72dbb` |

Scoped exactly to the four committed files, as `-006` recommended. The withdrawal
artifact's SHA-256 also re-derives character-for-character against `-007:156`.

## Positive Confirmations

Each independently reproduced this review.

1. **Five GO-mandated commands re-run.** `git show --stat --oneline --no-renames`
   returns `6 files changed, 932 insertions(+)`; `git diff-tree` returns the
   byte-identical six paths in the same order; `git merge-base --is-ancestor`
   exits 0 against HEAD `4efcb0ee2`; pytest returns `160 passed, 1 warning` with
   the sole warning being the unknown config option `asyncio_mode`; `ruff check`
   returns `All checks passed!` and `ruff format --check` returns
   `2 files already formatted`. Supplementary `git diff --check` on both paths
   exits 0 with no output.
2. **All twelve linked specifications have executed coverage.** `-007:162-173` is
   set-equal to `-006`'s carried-forward list - no drop, no addition - and every
   entry maps to a row at `-007:206-219` with named executed evidence.
3. **All four chains resolve as claimed.** The two historical chains fail closed
   with `WRONG_STATUS_AUTHOR_ROLE` at `-001` (bare `author_identity: codex`);
   `superseded-verified` resolves v5 `WITHDRAWN`, strict, zero diagnostics; the v2
   chain resolves `001 NEW / 002 NO-GO / 003 REVISED / 004 NO-GO / 005 REVISED /
   006 GO / 007 NEW`, all strict, zero blocking diagnostics.
4. **Scope compliance is clean.** `git status --porcelain=v1` shows untracked
   entries only - zero modified, zero staged, zero deleted. `git diff --stat HEAD`,
   `git diff --cached --stat`, and `git diff --stat` are all empty. `-007`'s
   `## Files Changed: None` holds.
5. **Both preflights pass on `-007` as operative file.** Applicability:
   `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`, `blocking_errors: []`,
   `warnings.unclassified_target_paths: []`, exit 0. Clause preflight in mandatory
   mode: 5 clauses, 4 `must_apply` all with evidence, 0 blocking gaps, exit 0.
   Both match `-007:256-260`.
6. **Report shape complete.** First non-blank line is `NEW`; carried-forward
   `Specification Links`; spec-to-test mapping; exact commands; observed results;
   all ten `-005` acceptance criteria numbered and dispositioned; a
   `Recommended Commit Type` of `chore`; a substantive `Owner Decisions / Input`
   section.
7. **Backlog state as claimed.** WI-5657 remains `stage: backlogged`,
   `resolution_status: open`, unreconciled pending terminal verification.

## Finalization Readiness For The Successor

Recorded so the eventual terminal transaction is unambiguous. Per the approved
invariant, the terminal commit must contain exactly every versioned file of this
v2 chain present at finalization, plus the single named retirement artifact
`bridge/gtkb-wi5657-protected-commit-superseded-verified-005.md`, plus the
terminal verdict itself - and no other path.

Two operational cautions for whoever finalizes:

- `write_verdict.py`'s predecessor-chain assertion auto-requires **same-slug**
  predecessors only. The retirement artifact is on a foreign slug and must be
  passed explicitly as an additional `--include`, or the durability defect that
  `-004` FINDING-P1-001 exists to close will recur.
- The worktree currently holds numerous untracked bridge artifacts outside the
  approved include set - advisories filed by concurrent sessions, and the
  `gtkb-wi5679-session-role-keying-continuity` chain. None may be captured.
  `-007:158`'s framing that no fixed v2 version count is authoritative is correct
  and necessary, since this NO-GO and the corrected report both extend the chain.

## Specifications Carried Forward

Mirrors `-007:162-173`:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Spec-to-Test Mapping

| Specification | Verification executed by this reviewer | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `resolve_bridge_lifecycle` over all four WI-5657 chains | yes | PASS - v2 strict through `-007`; historical dispositions exact |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Read-only MemBase query of `current_project_authorizations`; resolution path read at `implementation_authorization.py:1066` | yes | PASS - cited PAUTH active, correct classes, `git_commit` permitted; concurrent stale PAUTH recorded at FINDING-P3-002 |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `git hash-object` against `git rev-parse HEAD:<path>` for the four committed historical files; withdrawal SHA-256 re-derivation | yes | PASS - all four blobs and the withdrawal digest match `-007` exactly |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Re-ran all five GO-mandated commands plus `git diff --check`; compared every reported result | yes | **FAIL** - inventory, counts, ancestry, tests, and ruff all reproduce; the verbatim commit subject does not (FINDING-P2-001) |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-5657` | yes | PASS - `stage: backlogged`, `resolution_status: open`, unreconciled |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header triple inspection against the live PAUTH, project, and work item | yes | PASS - resolves exactly; PAUTH named by ID at `-007:21` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5657-terminal-finalization-recovery-v2` | yes | PASS - exit 0, `missing_required_specs: []`, operative file `-007` |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | First non-blank line check on `-007` | yes | PASS - `NEW`, never `NO-ACTION` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Terminality check on the `WITHDRAWN` artifact; v2 chain append-only inspection | yes | PASS - old chain terminal; no prior version rewritten |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5657-terminal-finalization-recovery-v2` | yes | PASS - 0 blocking gaps, exit 0 |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause preflight `must_apply` evaluation plus path inspection | yes | PASS - all paths root-contained under `E:/GT-KB` |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --porcelain=v1`; `git diff --stat HEAD`; `git diff --cached --stat` | yes | PASS - untracked entries only; nothing staged; this review staged nothing |

## Prior Deliberations

- `DELIB-202667519` - the exact-recovery authorization establishing by-reference
  finalization, and therefore the reason the evidence record carries the full
  weight of the implementation claim. Basis for FINDING-P2-001's severity.
- `DELIB-202667520` - owner disposition continuing the v2 chain and retiring the
  old one; the authority under which the correction may be made without a new
  owner decision.
- `DELIB-202667182` - owner authorization for the original checker fix; provenance
  for immutable commit `7b838d9e...` and for the stale concurrent PAUTH at
  FINDING-P3-002.
- `DELIB-202666412` - Loyal Opposition GO on
  `gtkb-wi5230-terminal-commit-coverage-guard`; the closest prior treatment of
  terminal-commit include-set discipline, applied in Finalization Readiness above.
- `DELIB-202666507` - corrected GO verdict on the WI-5318 failed-`VERIFIED`
  finalization repair; precedent that finalization defects are repaired forward
  rather than by rewriting history.
- `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-006.md` - the controlling
  GO whose single finding `-007` closes.
- `bridge/gtkb-lo-project-authorization-accumulation-and-conflict-advisory-001.md` -
  the systemic authorization-accumulation condition underlying FINDING-P3-002.

## Applicability Preflight

- packet_hash: `sha256:a6dd5bcc3fe0da2d6440d13b1e2245dfee79cb09a2f91d52ab225208540ed719`
- candidate_evidence_hash: `sha256:b350118d5638d7b0919233cc82ff39fa6c9feec051c5d8d95cba884c880d5770`
- bridge_document_name: `gtkb-wi5657-terminal-finalization-recovery-v2`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

Exit 0. All cited required specs matched; `missing_required_specs: []`.

## Clause Applicability

- Bridge id: `gtkb-wi5657-terminal-finalization-recovery-v2`
- Operative file: `bridge/gtkb-wi5657-terminal-finalization-recovery-v2-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Blocking Gaps: none. Exit 0.

Note carried forward: the clause preflight tests evidence *presence*, not factual
correctness. FINDING-P2-001 is a quotation that does not reproduce, which no
currently-registered clause detects.

## Required Revisions

Before resubmitting the report:

1. **FINDING-P2-001 (blocking).** Delete the word `history` from the verbatim
   commit-subject block so it matches
   `git show -s --format=%s 7b838d9e7606a8b1f8be75ade78881f63beda170`
   byte-for-byte. Recommended: state the re-derivation command inline beside the
   quote.

No other revision is required. No re-derivation of any other evidence is
necessary; all of it reproduced this review.

## Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | File a corrected implementation report at the next version with status `NEW`. |
| Preconditions | This `-008` NO-GO is latest. Acquire a work-intent claim before drafting. No new owner decision is required. |
| Evidence paths | `-007:110-114` (the quoted subject); `-007:130` (the correctly-quoted WI-5704 subject, as the pattern to match). |
| File touchpoints | The next versioned bridge file only. No source, test, configuration, or KB mutation. |
| Implementation sequence | (1) Copy `-007` forward. (2) Correct line 113. (3) Optionally add the re-derivation command beside the quote. (4) Leave every other section unchanged - it all verified. |
| Verification steps | Re-run `git show -s --format=%s 7b838d9e...` and diff its output against the fenced block. Re-run both preflights; confirm exit 0. |
| Rollback notes | None required - the corrected report is additive to an append-only chain. Do not modify `-001` through `-008` or commit `7b838d9e`. |
| Open decisions | None. |

## Commands Executed

```powershell
gt bridge state-report
git status --porcelain=v1
git diff --stat HEAD
git show -s --format=%s 7b838d9e7606a8b1f8be75ade78881f63beda170
git show -s --format=%s ec7e6b378329fdc6529a25311232235417ccda41
git show --stat --oneline --no-renames 7b838d9e7606a8b1f8be75ade78881f63beda170
git diff-tree --no-commit-id --name-only -r 7b838d9e7606a8b1f8be75ade78881f63beda170
git merge-base --is-ancestor 7b838d9e7606a8b1f8be75ade78881f63beda170 HEAD
git hash-object bridge/gtkb-wi5657-protected-commit-superseded-verified-00{1,2,3,4}.md
git rev-parse HEAD:bridge/gtkb-wi5657-protected-commit-superseded-verified-00{1,2,3,4}.md
git diff --check -- scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py -q --no-header
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5657-terminal-finalization-recovery-v2
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5657-terminal-finalization-recovery-v2
gt backlog show WI-5657
python scripts/bridge_claim_cli.py claim gtkb-wi5657-terminal-finalization-recovery-v2
```

Read-only resolver invocation: imported `resolve_bridge_lifecycle` from
`scripts/bridge_lifecycle_resolver.py` and resolved all four WI-5657 chains.
Read-only MemBase access via `sqlite3` (`current_project_authorizations`,
`current_work_items`). Read-only source inspection of
`scripts/implementation_authorization.py` (lines 1066, 1827-1853) and
`.claude/skills/gtkb-verify/helpers/write_verdict.py` predecessor-chain handling.

No repository file was modified, staged, or committed by this review other than
the creation of this verdict artifact through the governed bridge writer.

## Owner Action Required

None.

## Skills applied

- gtkb-bridge
- gtkb-verify

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
