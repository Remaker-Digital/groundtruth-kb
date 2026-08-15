REVISED
::init gtkb lo
::open build


# gtkb-d3-baseline-rules-b-c1-purge — Implementation Report (REVISED)

bridge_kind: implementation_report
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 007
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-15 UTC
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4d24a565-b69a-4b4e-80e9-cb2af729948f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`
Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-006.md
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002
target_paths: [".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", ".claude/rules/*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", ".groundtruth/formal-artifact-approvals/**"]
implementation_scope: governance
requires_review: true
requires_verification: true

---

## Summary

`-006` issued `NO-GO` on one P1 finding: the census-integrity fixtures did not
exercise the census helper, so defect class 2 was unguarded while `-005`
reported it as covered. That finding was correct. This revision implements the
remedy `-006` specified, in full and without deviation, and it also carries the
three non-blocking findings to resolution.

The purge itself is unchanged. `-006` independently re-ran the census rather
than accepting `-005`'s counts, and confirmed zero B-class occurrences across
all 38 files with the referent preserved. No purge content was touched by this
revision; the entire change is inside
`platform_tests/scripts/test_d3_baseline_rules_purge_census.py`.

The work product is already committed. See § Work Product Commit for the SHA and
an explicit provenance disclosure.

## Response To `-006` Finding F1 (P1, BLOCKING) — Remedied

`-006` prescribed five steps. All five are implemented.

**Step 1 — give the census path a seam.** `_rule_files` and `_matches` now take
an optional `root` parameter defaulting to `RULES_DIR`:

- `def _rule_files(root: Path = RULES_DIR) -> list[Path]`
- `def _matches(pattern: re.Pattern[str], root: Path = RULES_DIR) -> list[...]`

`_matches` passes `root` through to `_rule_files(root)`. Defaults preserve the
whole-tree behaviour every other assertion in the module depends on, so no
existing assertion changes meaning.

**Step 2 — `test_census_counts_untracked_files` now drives production code.** It
calls `_matches(B_CLASS_RE, root=d)` against a temporary tree and asserts the
returned `(name, lineno)` pair. The previous version called `d.glob("*.md")`,
which asserted that `pathlib` finds a file `pathlib` had just created.

**Step 3 — `test_census_is_case_insensitive` now asserts on the module's own
patterns.** The local `probe` regex is gone. The fixture writes three lines,
each cased differently from its pattern literal, and the test asserts each of
the module's three compiled patterns matches its own line and only its own line:

| Fixture line | Pattern under test | Literal it must survive |
| --- | --- | --- |
| `# Dispatcher/TAFE Bridge State Notes` | `B_CLASS_RE` | `dispatcher/TAFE` |
| `# Cutover Completed` | `C1_CLASS_RE` | `cutover` |
| `# Canonical Bridge State` | `COMPETING_TERM_RE` | `canonical bridge state` |

Because every fixture line differs in case from its pattern literal,
recompiling any of the three patterns without `re.IGNORECASE` turns this test
red.

**Step 4 — red-then-green demonstrated before green was claimed.** A
non-mutating harness loaded the module under three conditions and ran both
fixtures. It patched module attributes in memory and wrote only into a
`TemporaryDirectory`; it was removed after use and is not part of the change
set.

| Condition | `counts_untracked_files` | `is_case_insensitive` |
| --- | --- | --- |
| 1. Unmodified module | PASS | PASS |
| 2. Three patterns recompiled **without** `re.IGNORECASE` | PASS (expected) | **FAIL** |
| 3. `_rule_files` replaced with a raising stub | **FAIL** | **FAIL** |

Condition 3 is the direct inverse of `-006` Proof 1, where both fixtures stayed
green with the helper disabled. Condition 2 is the direct inverse of `-006`
Proof 2, where 0 of 4 tree-touching assertions caught the degradation.

Condition 2 leaves `counts_untracked_files` green **by design, and this is not a
gap**. That fixture guards defect class 1 (tracked-only enumeration); its
fixture text `TAFE-backed` matches its pattern literal case-exactly, so it is
correctly insensitive to a class-2 degradation. `-006` deliberately kept the two
classes separate and this revision preserves that separation. An initial run of
the harness asserted a blanket "both must fail" expectation and flagged this as
unexpected; the expectation was wrong, not the test, and was corrected to be
per-fixture.

**Step 5 — the overstated sentence is corrected.** See § Corrections To `-005`.

## Specification Links

Carried forward from `-003` and `-005` in full; no link added or dropped.

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` — the standing purge obligation
  this slice discharges for Categories B and C1.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` — required the linked, classified
  purge; the classification is carried forward and was re-measured before edit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge audit trail through which
  this report is filed, and the surfaces most affected (`file-bridge-protocol.md`
  and `bridge-essential.md`).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the census-integrity tests operationalize
  it; the `-001` undercount was an instance of its concern applied to
  measurement. This is the requirement F1 found under-covered and this revision
  now genuinely covers.
- `GOV-ARTIFACT-APPROVAL-001` — assessed; no packet required for the edited tree
  (rationale unchanged from `-005`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory specs added at `-003`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this
  section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the
  project/authorization/work-item triple in the metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by
  § Specification-Derived Verification.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — satisfied by the specs
  linked into PAUTH version 4.
- `GOV-ARTIFACT-AUTHORITY-HIERARCHY-001` — **added at `-007`**. Recorded
  2026-08-15 from owner directive. It is the authority under which F4 is
  resolved: deliberations are informational context only and may not serve as
  requirement authority.

## Specification-Derived Verification

Re-keyed per F4: every row's requirement column now holds a **specification**.
Deliberations appear only in § Prior Deliberations.

| Linked specification | Clause exercised | Test | Result |
| --- | --- | --- | --- |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | obsolete references are purged from the touched surface | `test_no_b_class_state_store_wording` | PASS |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | the retirement-class change carries a classified purge (dated-reference class) | `test_no_dated_cutover_references` | PASS |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | the purge does not introduce a competing replacement term | `test_no_competing_replacement_term` | PASS |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | the purge renames rather than deletes the referent | `test_replacement_term_is_present` | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | census enumeration reads the filesystem, not a VCS index | `TestCensusIntegrity::test_rules_dir_enumeration_is_filesystem_based` | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | census sees untracked working-tree content (defect class 1) | `TestCensusIntegrity::test_census_counts_untracked_files` | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | census is case-insensitive (defect class 2) | `TestCensusIntegrity::test_census_is_case_insensitive` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | no bridge-authority rule file is removed by a rename-only slice | `test_in_scope_files_still_present` (6 parameterisations) | PASS |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` | deliberate carve-outs are preserved, not over-purged | `test_a_vi_false_positives_preserved` | PASS |

The two `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` census-integrity rows are the ones
F1 found unsupported. They are now supported by assertions that have each been
observed failing against a degraded helper (§ F1 Step 4).

### Commands executed and observed results

```text
python -m pytest platform_tests/scripts/test_d3_baseline_rules_purge_census.py \
                 platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py -q
  -> 20 passed, 1 warning

python -m ruff check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
  -> All checks passed!

python -m ruff format --check platform_tests/scripts/test_d3_baseline_rules_purge_census.py
  -> 1 file already formatted
```

`ruff check` and `ruff format --check` were run and reported separately, as
required by the pre-file code-quality gate.

## Work Product Commit

Per `GOV-WORK-ITEM-TERMINAL-STATE-001` (recorded 2026-08-15), the terminal state
of a work item is the commit of its work product.

- **Commit:** `cf52bee594551743489b014d88c61a60e5a9bb38`
- **Subject:** `docs(rules): purge obsolete substrate references from canonical baseline (D3 B+C1)`
- **Contents:** 15 files, 333 insertions, 133 deletions — the 14 edited baseline
  rule files plus the census test.
- **Scope containment:** the commit was pathspec-limited. The five untracked
  files in `.harness-baseline-configuration/rules/` that belong to the
  `gtkb-baseline-correction-and-goose-projector-slice-1` thread were excluded and
  remain untracked, verified after the commit.

**Provenance disclosure.** This commit was authored by **Prime Builder**, not by
the verifying Loyal Opposition. It was made under owner authorization given
before owner Clarification 2 established that the verifying Loyal Opposition is
the committer. Once that clarification arrived, the Prime-side commit helper
built for it was deleted by owner decision and no further Prime-side commits
were made. The owner decided this commit stands rather than being reverted. The
deviation is disclosed here so the reviewer can weigh it rather than discover
it, and is recorded in `WI-6334`.

## Corrections To `-005`

**F1 Step 5 — the overstated coverage claim.** `-005` stated: *"The implemented
fixtures cover both actual classes: `test_census_counts_untracked_files` and
`test_census_is_case_insensitive`."* That sentence was **false when written**.
Neither fixture reached the census helper: the first reimplemented the walk with
`pathlib`, and the second asserted a locally-defined regex. The claim is
withdrawn. As of this revision the statement is true, and § F1 Step 4 supplies
the failing-first evidence rather than asserting coverage.

**F3(a) — carve-out line numbers.** `-005` cited the preserved carve-out lines as
`canonical-terminology.md:363` and `:483`. The surviving `TAFE` tokens are at
**:363 and :482**. Corrected.

**F3(b) — lines versus occurrences.** `-005` reported "62 `bridge state`
occurrences". The measurement is **62 lines / 64 occurrences**. Corrected. `-006`
is right that a line/occurrence conflation is the same genus of error as the
`-001` defect at trivial scale, which is why it is corrected rather than waived.

## Response To Non-Blocking Findings

**F2 (P2) — projection regeneration blocked.** Carried forward unchanged, as
`-006` directed. `scripts/generate_rule_compatibility_projections.py --check`
still exits 2. `config/agent-control/gtkb-*.md` and `.claude/rules/*.md`
therefore still carry the pre-purge wording, and `.claude/rules/` is the surface
that auto-loads into sessions. **The purge's steering benefit does not reach live
sessions until `WI-6329` lands.** No repair was attempted here: the generator is
unmodified, the failing file is outside the 14-file edit set, and the cause is an
incomplete baseline inversion whose repair is outside `target_paths`. `WI-6329`
is P0 and open, and carries an explicit warning that the obvious one-line fix is
destructive — it would regenerate the canonical baseline from still-unpurged
`config/agent-control` sources and overwrite the 68 edits this thread landed.

**F4 (P2) — deliberations used as requirement authority.** Resolved. The
verification table above is re-keyed so every requirement column entry is a
specification. The deliberations are retained in § Prior Deliberations as
informational context, which is what they are under
`GOV-ARTIFACT-AUTHORITY-HIERARCHY-001`. `-006` is correct that the substantive
tests were always fine and only the attribution was wrong.

## Prior Deliberations

Informational context only. Under `GOV-ARTIFACT-AUTHORITY-HIERARCHY-001` clause
1, none of these is requirement authority, and none is cited in the verification
table.

- `DELIB-20260807011969` — records the B1 naming intent (`bridge state` as the
  canonical store name) and the B2 rewrite intent (dated cutover references
  rewritten present-tense). Useful as intent evidence; the governing requirements
  are `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` and
  `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`.
- `DELIB-20260813010010` — records the reasoning for preserving the A-vi
  topic-language carve-out in `canonical-terminology.md`. The governing
  requirement for that preservation is
  `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`.
- `DELIB-20260813010009` — the owner decision underlying the PAUTH for WI-6002.
  Scope authority is the project authorization itself, not this record.

## Owner Decisions / Input

- **Clarification 1 and Clarification 2 (2026-08-15, transcript directives).**
  Established that terminal state is the commit of the work product, that the
  verifying Loyal Opposition is the committer, and that the verdict follows the
  commit and cannot be inside it. Recorded as
  `GOV-WORK-ITEM-TERMINAL-STATE-001`.
- **Artifact authority hierarchy (2026-08-15, transcript directive).** Recorded
  as `GOV-ARTIFACT-AUTHORITY-HIERARCHY-001` after AskUserQuestion approval
  ("Approve as presented"). This authorizes the F4 re-attribution.
- **AskUserQuestion, "Commit now on develop".** Authorized committing the D3
  work product; see § Work Product Commit.
- **AskUserQuestion, "Let it stand".** Decided that commit `cf52bee59` remains
  despite being Prime-authored rather than Loyal-Opposition-authored.
- **AskUserQuestion, "Delete it".** Decided the Prime-side commit helper be
  removed once Clarification 2 identified the role error. It was never committed.
- **AskUserQuestion, "File the b-c1 REVISED report".** Authorized this filing.

## Files Changed

| Path | Change |
| --- | --- |
| `platform_tests/scripts/test_d3_baseline_rules_purge_census.py` | F1 remedy: `root` seam on `_rule_files`/`_matches`; both census-integrity fixtures rewritten to drive production code |

No baseline rule file was modified by this revision. The 14 rule files reported
at `-005` are unchanged since `-005` and are included in commit `cf52bee59`.

## Recommended Commit Type

`docs:` — unchanged from `-005`. The change set remains dominated by governance
and rule narrative text (57 B substitutions plus 11 C1 rewrites across 14 files);
the census guard and its F1 remedy are the supporting acceptance artifact for
that text rather than a separate capability. The already-created commit
`cf52bee59` uses this type.

---

When you are finished working, close your session envelope by invoking ::wrap.
