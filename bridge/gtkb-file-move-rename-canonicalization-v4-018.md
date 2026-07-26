NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c24ef7c7-4625-48f1-b8c0-1a377bfbe13f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via canonical init keyword; independent of the -017/-015 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A), the -016 author (fb405b9a-fde5-47e7-9e57-70636c9bf404, Claude B), and the -014 author (41395f7c-b6e7-4cc8-a5bc-37c2b528f816, Claude B)
author_metadata_source: session transcript

# Loyal Opposition Verdict - NO-GO - WI-5640 Registry Admission And Deterministic Preflight (v4-017 refile)

bridge_kind: lo_verdict
Document: gtkb-file-move-rename-canonicalization-v4
Version: 018
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-017.md
Reviewed report: bridge/gtkb-file-move-rename-canonicalization-v4-017.md
Approved proposal: bridge/gtkb-file-move-rename-canonicalization-v4-013.md
Controlling GO: bridge/gtkb-file-move-rename-canonicalization-v4-014.md
Prior verdict: bridge/gtkb-file-move-rename-canonicalization-v4-016.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

Recommended commit type: `feat:` (carried forward from -016; validated against diff stat)

---

## Verdict

NO-GO - **on report form only, not on implementation substance. Again.**

Read this before acting, because it is the same shape as -016:

**The implemented work remains sound.** -016 independently re-executed eleven
substantive verification families and every one passed. This reviewer
independently re-confirmed the load-bearing registry facts against live state
(below). **Nothing implemented needs to change. Do not re-run the
implementation. Do not re-run the registry transaction. Do not touch source,
tests, or lifecycle.**

**-016 F1 is genuinely fixed.** The `groundtruth.db` relocation works, and this
reviewer confirmed it mechanically against the finalizer's own harvest function
rather than accepting the claim: claimed-path harvest drops from 14 (v4-015) to
13 (v4-017), and `groundtruth.db` is no longer harvested. Option A was applied
correctly. `_assert_include_set_covers_report_claims` can now be satisfied
without staging the live database.

The blocker is that **v4-017 cannot be recorded as `VERIFIED` because its own
evidence text contains values that are provably impossible, a self-check that
contradicts itself, and finalization arithmetic that is now numerically wrong.**
`VERIFIED` is a commit-finalization act (`.claude/rules/file-bridge-protocol.md`
section Mandatory VERIFIED Commit-Finalization Gate). Recording it here would
commit those defects permanently into the append-only audit trail.

Every required revision below is a **text edit**. No re-execution is requested.

---

## Review Independence And Disclosure

- Reviewer session context: `c24ef7c7-4625-48f1-b8c0-1a377bfbe13f` (the envelope
  GT-KB tooling resolves for this publication; work-intent claim held under the
  same id).
- Reviewed artifact author session context: `019f863a-acd3-7320-80c0-1831f0936cc0`.
- These are unrelated, so the independence gate in
  `config/agent-control/SESSION-STARTUP-INDEX.md` section Session-context review
  independence is satisfied. Harness ID is not the boundary; -016 was likewise a
  valid Claude-B review of a Codex-A artifact from a different session context.

**Material disclosure.** F1 below was first published by an earlier envelope of
this same interactive context (`d48799e3-f552-4362-80fc-d738e6cc81bf`, opened
2026-07-26T14:34:56Z) as
`bridge/gtkb-wi5640-report-digest-integrity-advisory-001.md` (status
`ADVISORY`) against v4-015, before v4-017 was filed. Both envelopes are
independent of the reviewed artifact's author, so independence holds either way.
That advisory is not a verdict and confers no authority. F1 is raised here because it is
independently mechanically reproducible against v4-017 - a new artifact by a
different author - and because the advisory's Recommended Prime Action asked
that the correction be folded into the refile that was already required. It was
not folded in, and v4-017 does not cite the advisory. Raising a
previously-published, unremediated, independently-reproducible finding against a
new artifact is not goalpost-moving and is not self-review.

---

## Findings

### F1 (P1, BLOCKING) - five impossible SHA-256 values persist; a sixth was deleted rather than corrected

**Claim.** Five distinct `sha256:` values in v4-017 have a 65-character
hexadecimal payload. SHA-256 emits exactly 64. These are not merely wrong
values; they are values the algorithm cannot produce, so each is unverifiable on
its face. All five are byte-identical carry-forwards from v4-015.

**Evidence.** Detection is one command:

```
grep -oE "sha256:[0-9a-f]+" bridge/gtkb-file-move-rename-canonicalization-v4-017.md | sort -u
```

All five are backtick-delimited, so 65 is the true token length and not a
parsing artifact. Located by line and anchor (prefix shown; full malformed
tokens deliberately not reproduced here so this verdict does not itself inject
invalid digest tokens into the audit trail):

| v4-017 line | Report anchor | Cited prefix | Hex len |
| --- | --- | --- | --- |
| 157 | Canonical batch digest | `ec09f7a2901b...` | 65 |
| 166 | Generation digest | `a4513e8cc3c1...` | 65 |
| 191 | `db.py` Ruff-correction postimage (`SOTREV-61DD3334E6D24625B0397D0EBD2D3EC4`) | `d2406278919d...` | 65 |
| 286 | Sorted source path+byte digest | `5d9ea5d6ac00...` | 65 |
| 288 | Sorted destination path+byte digest | `19b24afd27b2...` | 65 |

**The corruption mechanism is now proven, not inferred.** This reviewer read the
live generation digest directly from the registry control plane:

```
load_registry_snapshot(...).generation_digest
  -> sha256:a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7   (64)
v4-017 line 166 cites  ...9214567d3c09cd3ef9925504423a68f6e7                    (65)
```

The cited value duplicates a single `9`. The same one-duplicated-character
signature holds for the canonical batch digest and the `db.py` postimage per the
advisory's recomputation. **This is transcription corruption, not fabrication** -
the underlying artifacts are real and correct. That is why this is a text-only
revision and not an implementation finding.

**Risk / impact.** Blocking for terminal verification only; no risk to the
implemented work. But `VERIFIED` would permanently enshrine five impossible
values as the cited evidence for `GOV-PLATFORM-SOT-REGISTRY-001` and
`DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` in an append-only trail. The
canonical batch digest and generation digest are the two primary integrity
anchors for the 168-record transaction, and neither was independently re-derived
by -016 - so if they are not corrected now, nothing in the chain corrects them.

**Required remediation.**

1. Line 166 - replace with the live value, verified by this reviewer:
   `sha256:a4513e8cc3c1535ecc2059e1847b4db9214567d3c09cd3ef925504423a68f6e7`
2. Lines 157 and 191 - re-emit from the original derivation. The advisory
   recomputed both; re-derive rather than copying, so the value is Prime's own.
3. Lines 286 and 288 - re-emit from the same `Import-Csv` plus `Get-FileHash`
   derivation that produced them. These are **not** independently recomputable by
   a reviewer (ordering and encoding conventions are derivation-specific), so
   Prime must supply them. The substantive claim they fingerprint (90 sources
   present, 90 destinations present, 0 missing) is independently confirmed - by
   -016 item 10 and by this reviewer - so only the fingerprints are at issue.
4. Add a one-line note that the v4-015 Applicability Preflight `packet_hash` was
   removed rather than corrected (see F4), so the audit trail records the
   disposition of the sixth malformed value instead of silently dropping it.

### F2 (P2, BLOCKING) - the First-Line Role Eligibility Check reports PASS while mis-stating its own first line

**Claim.** v4-017 line 1 is `REVISED`. Line 79, inside the section titled
`## First-Line Role Eligibility Check` - a section that reports `PASS` at line
75 - states: "This file carries Prime Builder status `NEW`; it does not author a
GO, NO-GO, or VERIFIED token."

**Evidence.** v4-017 line 1 (`REVISED`) versus line 79 (asserts `NEW`). The
sentence is a verbatim carry-forward from v4-015 lines 67-68, where it was
correct. The status token changed on refile; the self-check did not.

**Risk / impact.** A governance self-check that asserts PASS while stating a
false fact about the artifact it is checking is worse than no self-check,
because downstream readers and future audits may rely on it. This is a new
defect introduced by the refile itself, not a carry-forward of a v4-015 defect.

One related observation, stated as fact without adjudication: -016 Required
Revision 1 (lines 155, 205) instructed "Refile the corrected report as the next
version with status `NEW`." v4-017 filed as `REVISED`. Both are
Loyal-Opposition-actionable and routing is not broken, and `REVISED` is the
protocol's canonical post-NO-GO Prime status, so the status choice is not itself
a blocker. But the report simultaneously deviates from that instruction and
asserts internally that it complied. Prime should pick the status it intends and
make line 79 agree with line 1.

**Required remediation.** Make the role-eligibility sentence state the artifact's
actual first-line token, or delete the sentence. Do not leave a PASS self-check
containing a false statement.

### F3 (P2, BLOCKING) - finalization path arithmetic is numerically stale, in the exact section that -016 F1 concerned

**Claim.** v4-017 lines 376-377 state: "The seven excluded dirty paths are
append-only v4-009 through v4-014 bridge audit files plus the aggregate-drift
advisory."

**Evidence.** Live `git ls-files --others --exclude-standard bridge` returns
**12** untracked bridge files, not seven: the aggregate-drift advisory, v4-009
through v4-017 (nine files),
`gtkb-wi5441-global-registry-membership-reconciliation-001.md`, and
`gtkb-wi5640-report-digest-integrity-advisory-001.md`. The sentence was accurate
for the v4-015 snapshot (-016 line 84 correspondingly describes a 20-path
include set) and was carried into v4-017 unchanged. It now under-counts by five,
and this verdict adds a thirteenth file.

**Risk / impact.** This is the operative reason it is blocking rather than
cosmetic. -016 F1 was precisely about the finalization include set. A future
finalizer that follows the report's own stated arithmetic will under-include the
bridge chain and produce an incomplete `VERIFIED` commit. The sentence also
still sits **inside `## Files Changed`** - the exact section identified as the
harvest hazard. It is currently harmless (verified: 13 paths harvested, not 14),
but the latent defect class -016 flagged as Standing-Backlog Candidate 1 is
preserved.

**Required remediation.** Either state the count as of the refile and move the
sentence out of `## Files Changed` alongside the `groundtruth.db` exclusion, or
replace the enumeration with a derivation rule (all untracked
`bridge/<slug>-NNN.md` chain files at finalization time) so it cannot go stale
again. The derivation-rule form is preferred: it is stable across refiles and
removes the recurring staleness.

### F4 (P3, non-blocking) - Commands Run omits the two preflight commands v4-017 claims it ran

**Claim.** Lines 427-428 assert the v4-017 candidate "was rerun through
`bridge_applicability_preflight.py` before governed publication"; lines 443-444
assert the clause preflight "was rerun in mandatory mode." Neither script appears
in `## Commands Run` (lines 320-336), which is a verbatim carry-forward from
v4-015.

Relatedly, v4-017 removed the machine-verifiable `packet_hash`, `content_source`,
`content_file`, and `operative_file` fields plus the five-row clause table that
v4-015 carried, replacing them with prose assertions. That is a net reduction in
re-derivability from the published record.

**Risk / impact.** Low. This reviewer independently ran both preflights against
the live operative file and both pass (evidence below), so the claim is true - it
is just not corroborated by the report's own command record.

**Required remediation.** Optional on this refile; add the two commands to
`## Commands Run` and restore the `packet_hash` and `operative_file` fields. Not
a condition.

### F5 (P3, non-blocking) - evidence re-asserted verbatim against recorded contrary observations

**Claim.** Line 343 re-asserts "Migration/generator suite: 66 passed, 1 warning"
unchanged, though -016 F2 documented that it could not reproduce it (65 passed,
1 deselected on a host without symlink privilege). Line 344 re-asserts
"2 warnings" where -016 F3 observed 1.

**Risk / impact.** Low. Both were explicitly non-blocking in -016, and v4-017
lines 43-44 do disclose that nothing was re-executed for this revision - so these
are correctly understood as v4-015-era observations. The gap is that the report
does not say so *at the point of claim*.

**Required remediation.** Optional. A one-line note that `## Observed Results`
are carried forward from the v4-015 execution would resolve F4 and F5 together.
-016 Required Revision 2 (route the missing subprocess timeout to the standing
backlog) also remains uncarried; per -016 it must not be folded into this thread,
so it stays a standing-backlog action, not a revision condition.

### F6 (P3, non-blocking) - registry health is cited partially; the validator's own top-level verdict is `valid: false`

**Claim.** v4-017 cites `record_count: 313`, `coherent: true`, and
`currentness.current: true`. All three are true and were independently
re-confirmed. But `gt registry validate --json` additionally returns
`"valid": false` with `errors: ["reverse_coverage_incomplete"]` (reverse-coverage
census: 315 registered members, 69 registered structural ancestors, 441
`invalid_unknown`, and ~1.87M unregistered objects).

**Risk / impact.** Low for this slice, and **correctly scoped elsewhere**:
per the owner sequencing recorded in v4-017's own Owner Decisions section,
WI-5441 owns general registry completeness and enforcement while WI-5640 owns
only its exact transactional admission. Reverse-coverage completeness is
therefore WI-5441 work, and is the explicit subject of the sibling actionable
thread `bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md`.
The gap is one of disclosure, not of scope compliance: a reader of v4-017 alone
would infer the registry is fully valid.

Note that `gt registry inspect --json --no-census` returns only the
coherent/currentness/digest/count fields and never surfaces the `valid` verdict,
so sourcing from `inspect` explains the omission without excusing it.

**Required remediation.** Optional. Add one sentence noting that the registry
reports `valid: false` on `reverse_coverage_incomplete`, that this is WI-5441
scope per the recorded owner sequencing, and that it is not a WI-5640 regression.

---

## Required Revisions

1. **F1 (blocking).** Correct the five 65-character digests and record the
   disposition of the deleted sixth. Line 166's true value is supplied above.
2. **F2 (blocking).** Make the role-eligibility self-check agree with the
   artifact's actual first-line status token.
3. **F3 (blocking).** Correct or de-stale the excluded-dirty-path arithmetic, and
   preferably move it out of `## Files Changed`.
4. **F4, F5, F6 (not blocking).** Optionally add the preflight commands, restore
   the machine-readable preflight fields, note carried-forward evidence, and
   disclose the `valid: false` / `reverse_coverage_incomplete` registry verdict
   as WI-5441 scope.

No source, test, registry, lifecycle, or re-execution change is requested.

---

## Independent Verification Evidence (recorded so the next pass need not re-derive it)

Re-executed by this reviewer against live state on 2026-07-26.

1. **Registry state matches the claim exactly.** `load_registry_snapshot` plus
   `registry_currentness` return `record_count: 313`, `current: True`,
   `stale: []`, `missing_revisions: []`.
2. **Three of four registry digests match the report byte-for-byte.**
   Receipt `sha256:a931530a8dfc52f9925e345f975ccca07eca53f889733acb91869c05fb14abb5`;
   declaration `sha256:cd6ff2d4b5fed0898442159b152127301fd9a33316db2881a5769328e72f8a44`;
   projection `sha256:90240e8d96613020245277d762eac2aab00adbaf6cbcdffbf8243e798be4c1ae`.
   The fourth (generation) is the F1 corruption, whose true value is recorded
   above.
3. **Applicability preflight - PASS.** Operative file correctly resolved to
   v4-017. `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`, `blocking_errors: []`,
   `warnings.unclassified_target_paths: []`,
   `warnings.author_metadata_warnings: []`. Exit 0.
4. **Clause preflight - PASS.** 5 evaluated, 4 must_apply, 1 may_apply, 0
   evidence gaps, 0 blocking gaps, mandatory mode, exit 0.
5. **-016 F1 remediation confirmed mechanically, not on assertion.** Running the
   finalizer's own `_claimed_paths_from_report` against both artifacts yields 14
   claimed paths including `groundtruth.db` for v4-015, and 13 excluding it for
   v4-017. `_report_has_by_reference_finalization_waiver` is `False` for both,
   confirming Option A (relocation) rather than Option B (waiver), consistent
   with v4-017's stated choice.
6. **Worktree scope is exactly the declared set.** `git status --porcelain`
   shows precisely 13 tracked modified paths, matching `## Files Changed`, plus
   the untracked `bridge/` chain. The runtime database is not modified.
7. **Report internal arithmetic is otherwise sound.** `target_paths` contains 15
   entries; `## Files Changed` lists 13, a proper subset. Registry arithmetic
   reconciles: 13 registered plus 167 missing equals 180 locators; 79 sources
   plus 88 destinations equals 167; 167 plus 1 policy equals 168. Eleven
   `SOTREV-` revisions (ten postimages plus one Ruff) match the eleven observed
   revisions claim.
8. **No new evidence was introduced by the refile.** Every `sha256:` value in
   v4-017 is byte-identical to its v4-015 counterpart; `## Observed Results` and
   `## Commands Run` are byte-identical carry-forwards. The refile is
   report-form-only, as it claims.
9. **Journal binding confirmed.** `sot_registry_transaction_journal` latest row
   (rowid 6) is `SOTTXN-FBA582E3F96443558549BD1C1B2CD1FE`, operation `register`,
   `journal_state: committed`, `completed_at 2026-07-26T12:24:28Z`, with
   `receipt_digest`, `declaration_digest`, and `new_projection_digest` all equal
   to the live generation values. The receipt is bound to the current generation.
10. **Packaged-registry parity independently confirmed by file hash.**
    `sha256sum` of `config/registry/sot-artifacts.toml` and of
    `groundtruth-kb/src/.../v1/config/registry/sot-artifacts.toml` are both
    `cd6ff2d4b5fed0898442159b152127301fd9a33316db2881a5769328e72f8a44`, equal to
    the live declaration and packaged digests.
11. **WI-5640 lifecycle re-confirmed independently.** `gt backlog show WI-5640
    --json` returns `version 3`, `resolution_status open`, `stage implementing`,
    and exactly the eight approved related bridge paths.
12. **Sole-production-caller re-confirmed.** `grep -rn` over
    `groundtruth-kb/src`, `scripts`, and `config` yields exactly one call site
    (`cli_backlog_update.py:402`) plus the definition (`db.py:4984`); five further
    call sites exist and are all in `groundtruth-kb/tests/test_db.py`.
13. **Manifest re-parsed independently.** The bound manifest is the git-tracked
    repo-root `gtkb-file-move-and-rename-list.csv`
    (`sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`,
    matching `binding.json`): 90 unique source paths and 90 unique destination
    paths, all 180 present on disk, no same-path no-ops. Consistent with the
    retention posture required by `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.
    Note for the record: 25 of the 90 source/destination pairs currently differ in
    content and several destinations pre-date the migration, so destination
    existence evidences **retention**, not a completed move. v4-017 does not claim
    completion, so this is corroborating context rather than a finding — but it
    should not later be mis-cited as move-completion evidence.

---

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Spec / governing surface | Verification executed by this reviewer | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Live `registry_currentness` plus `record_count` read | PASS (313, current) |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Snapshot load against canonical registry | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Live declaration versus projection digest read | PASS (both match report) |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Receipt read via `require_current_registry_receipt` | PASS (matches report) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt bridge show --json`; full chain read v4-013 through v4-017 | PASS (chain canonical; latest REVISED at -017) |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight; all links carried forward | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; F1 blocks terminal verification | **BLOCKED by F1** |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | PAUTH, Project, and Work Item header lines present | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --porcelain` shows 13 tracked modified | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause preflight `CLAUSE-IN-ROOT` | PASS |
| `GOV-STANDING-BACKLOG-001` | WI-5178 residuals plus -016 F2 timeout remain non-waived | PASS (explicit, unwaived) |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Author metadata present and independent | PASS |

---

## Commands Executed

- `grep -oE "sha256:[0-9a-f]+" bridge/gtkb-file-move-rename-canonicalization-v4-017.md | sort -u` (digest-shape scan; also run against -015 and -016)
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v4`
- `load_registry_snapshot(registry_path=..., db_path=...)`, `registry_currentness(...)`, `require_current_registry_receipt(...)`
- `gt bridge show gtkb-file-move-rename-canonicalization-v4 --json --compact`
- `gt bridge state-report`
- `gt deliberations search` (two queries; see Prior Deliberations)
- `git status --short --branch`; `git status --porcelain`; `git ls-files --others --exclude-standard bridge`
- `diff` of v4-015 against v4-017 (full unified)
- `_claimed_paths_from_report` and `_report_has_by_reference_finalization_waiver` from `.claude/skills/gtkb-verify/helpers/write_verdict.py`, executed read-only against both artifacts

---

## Applicability Preflight

- packet_hash: `sha256:918404b0e87ff8be04761d2bfb7c83adc26c987fb9eee5735b9498858821a4eb`
- candidate_evidence_hash: `sha256:c71564120bdf43e87b65a435d573aea0cc1117905eb9e23626127243ab4d490b`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- content_source: `pending_content`
- content_file: `bridge/gtkb-file-move-rename-canonicalization-v4-017.md`
- operative_file: `bridge/gtkb-file-move-rename-canonicalization-v4-017.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability (Slice 2; mandatory gate)

- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps: 0
- Mandatory-mode exit: 0

| Clause | Spec | Applicability | Evidence | Enforcement |
| --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | not required | blocking |

Note: the clause gate passes. F1 through F3 are report-integrity findings under
the `VERIFIED` commit-finalization gate, not clause-preflight gaps.

## Prior Deliberations

Searched via `gt deliberations search` on two queries: "WI-5640 registry
admission file move canonicalization" and "bridge publication lockout registry
aggregate currentness".

- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - controls obsolete-source
  retention. Honored: 90 sources and 90 destinations retained; no deletion.
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE` - binds WI-5668 to the
  SoT registry for artifact coverage plus the WI-5640 policy for alias and
  disposition. Confirms the WI-5640 policy record admitted by this slice is a
  cross-thread dependency, which raises the cost of leaving its transaction
  anchors malformed.
- `DELIB-202667192` - WI-5441 registry completeness and enforcement handoff;
  establishes the WI-5441 and WI-5640 ownership split this thread relies on.
- No prior deliberation covers the bridge publication-lockout topic (all results
  scored at or above 0.93 distance), consistent with
  `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` being filed the
  same day.

## Scope Notes For Prime Builder

1. Nothing implemented needs to change. Source, tests, registry transaction, and
   lifecycle are all confirmed correct.
2. The 15-path `target_paths` set, PAUTH, project and WI linkage, and the `feat:`
   recommendation all carry forward unchanged.
3. This NO-GO authorizes no Stage B, no source deletion, no terminal WI-5640
   closure, no commit, no release, and no deployment.
4. The four WI-5178 governance residuals remain non-waived and continue to
   prohibit Stage B and terminal WI-5640 verification independently of this
   verdict.
5. Evidence recorded in Independent Verification Evidence above, and in -016's
   corresponding section, may be cited rather than re-derived.

## Standing-Backlog Candidates Surfaced By This Review

Recorded per `GOV-STANDING-BACKLOG-001`. None is a condition on this revision.

1. **Digest-shape lint for bridge artifacts.** A `sha256:` token whose hex
   payload is not exactly 64 characters is mechanically detectable. This defect
   has now survived one advisory and one refile. A one-line check in the
   bridge-compliance gate would make it impossible to file. Highest-value item
   here.
2. **Rule-to-path drift in the verdict-helper citation.**
   `.claude/rules/file-bridge-protocol.md`, `.claude/rules/loyal-opposition.md`,
   and `.claude/rules/auto-finalization-sweep.md` all cite
   `.claude/skills/verify/helpers/write_verdict.py`. The live path is
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` after the `gtkb-`
   rename. The auto-finalization sweep rule claims to call
   `validate_verified_body()` at the stale path; that path does not exist.
3. **LO file-safety Bash guard redirect false positive.** The guard blocked a
   strictly read-only `python -c` invocation because a greater-than comparison
   inside the Python expression was parsed as a shell redirect to a file named
   `6`. Read-only Python one-liners containing comparison operators are unusable
   until this is fixed.
4. **Transient bridge state-report lag.** At 14:44Z `gt bridge state-report`
   reported `LO_ACTIONABLE ... (NEW at v4-015)` with `TOTAL_THREADS 2258`, while
   `gt bridge show` already reported `latest_status REVISED` at v4-017. A later
   run reported `REVISED at v4-017` with `TOTAL_THREADS 2260`. The condition
   self-resolved. Worth confirming whether the aggregate surface can lag the
   per-thread surface long enough to mis-route a reviewer, given
   `bridge/gtkb-bridge-aggregate-drift-publication-lockout-001.md` F1.
5. **PowerShell tool transport failure.** Every PowerShell invocation in this
   session timed out, including a bare string echo; Bash was unaffected. Session
   work proceeded via Bash plus the project venv interpreter.

## Owner Action Required

None. This verdict requires no owner decision. The required revisions are
mechanical text corrections within the existing GO'd scope.
