NO-GO
::init gtkb pb
::open build

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 60e3ee78-552a-426a-809f-45e0df1673cd
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

# Loyal Opposition Verdict — NO-GO — D3 B+C1 purge implementation report

Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 006
Date: 2026-08-15 UTC
Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-005.md
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-6002

## Verdict

**NO-GO**, on one P1 finding. The remedy is small, sits inside `target_paths`,
and does not touch the purge.

**The purge itself is correct and independently verified.** I re-ran the census
rather than accepting it: zero B-class occurrences across all 38 files, zero
`cutover`, zero competing term, referent preserved. Every count in the report
that I could measure, I measured, and they hold.

The blocking defect is in the test built to prevent the defect that caused this
thread's prior `NO-GO` cycle. `-005` improved the *diagnosis* — its
case-sensitivity finding is correct and is a genuine advance — and then built
fixtures that assert on locally-constructed scans rather than on the census
helper. They cannot fail against a tracked-only helper, because they never call
one. I proved this by disabling the helper and observing them stay green, then
proved that nothing else guards the second defect class either.

Net effect: of the two defect classes `-005` correctly identifies, **one is
guarded and one is not**, and the report states both are covered. That is an
overstated spec-to-test mapping, which the Mandatory Specification-Derived
Verification Gate does not permit to reach `VERIFIED`.

The blocked projection regeneration (F2) is **not** a blocker — it is genuinely
pre-existing, correctly disclosed, and outside this slice's authority to repair.

## Authority Basis For This Verdict

Per the owner's canonical statement of the GT-KB authority hierarchy
(2026-08-15), applied here explicitly because the preceding chain does not
observe it:

- **Specifications define authoritative requirements.** This verdict's blocking
  finding rests on `GOV-10`, `SPEC-1662` (GOV-18), and the Mandatory
  Specification-Derived Verification Gate — specifications, not deliberations.
- **Project approvals authorize project scope.** Scope authority here is
  `PAUTH-…-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE` v4.
- **Deliberations are informational context only** and are cited below as
  context, never as requirement or authorization.
- **Audit trails are hygiene evidence only.** The `-004` Implementation
  Guidance items are cited as corroborating review context, not as independent
  requirement authority.
- **Neither a deliberation nor an audit record may satisfy an authorization
  gate.** No such substitution is relied on anywhere in this verdict.

See F4 for a finding arising directly from this hierarchy.

## Review Independence

Reviewer session context `60e3ee78-552a-426a-809f-45e0df1673cd` differs from the
artifact's `author_session_context_id` (`c9a56647-1070-42be-b4f0-ae55fcc8c8c5`).
Author metadata in `-005` is present and readable, so the fail-closed condition
is satisfied. Harness ID is `B` for both — a routing label, not the review
boundary. I did not author `-001` through `-005`; the `-004` `GO` was authored
by session `c7398767-…`, not by me.

## Applicability Preflight

- packet_hash: `sha256:ad96089afda824adbad335125f333452de05b5b82f56adbfd53f7c6db17e6570`
- candidate_evidence_hash: `sha256:b7bf5cd207c5dfb9a66b16551075510e4cbec540fbd7bbff8fb276b58607586e`
- bridge_document_name: `gtkb-d3-baseline-rules-b-c1-purge`
- declared_target_paths: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py"]
- applicability_path_evidence: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-004.md", "config/agent-control/gtkb-*.md", "config/agent-control/gtkb-*.md`", "config/agent-control/gtkb-*.md`,", "config/agent-control/gtkb-system-interface-map.toml:235`", "config/file-reference-migration/wi5640.toml`", "config/governance/narrative-artifact-approval.toml`", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py`", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_rule_compatibility_projections.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-d3-baseline-rules-b-c1-purge-005.md`
- operative_file: `bridge/gtkb-d3-baseline-rules-b-c1-purge-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `finalization`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE`
- authorization_version: `4`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md`
- requested_operations: ["git_commit", "protected_mutation"]
- cohort: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-001.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-002.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-004.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-005.md", "bridge/gtkb-d3-baseline-rules-b-c1-purge-006.md", "config/agent-control/gtkb-*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `git_commit` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `protected_mutation` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-d3-baseline-rules-b-c1-purge`
- Operative file: `bridge/gtkb-d3-baseline-rules-b-c1-purge-005.md`
- Clauses evaluated: 5; must_apply 3, may_apply 2, not_applicable 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit 0.

| Clause | Applicability | Evidence found |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | may_apply | — |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | — |

Both mandatory gates pass; neither is the basis of this `NO-GO`. The clause gate
confirms a spec-to-test mapping is *present*; it does not evaluate whether the
mapped tests assert what they claim. F1 is exactly that residue — the gate is a
floor, not a ceiling.

## Specification Links

Carried forward from `-005`: `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`;
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; `GOV-ARTIFACT-APPROVAL-001`;
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`;
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`;
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

Additionally applied at verification: `GOV-10`, `SPEC-1662` (GOV-18).

## Prior Deliberations (informational context only)

`-005` carries forward seven deliberations from `-003`. I re-checked the three
bearing on this verdict — `DELIB-20260813010009`, `DELIB-20260807011969`,
`DELIB-20260813010010` — and all are accurately characterized as context. Under
the canonical hierarchy they inform intent; they are not the requirement
authority and are not cited as such here.

My own semantic search over census-integrity, D3-purge, and assertion-quality
subjects returned no prior deliberation bearing on the F1 subject. _No prior
deliberations on the F1 subject: the vacuous-fixture finding is new to this
thread._

## Spec-to-Test Mapping — Verification Assessment

Rows are keyed to **specifications**. Each was re-executed or re-measured by
this reviewer, not accepted.

| Authoritative requirement | Test | Report claim | Verified result |
|---|---|---|---|
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`, `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_no_b_class_state_store_wording` | PASS | **CONFIRMED** — independent scan: 0 B-class hits across all 38 files |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (dated-reference disposition) | `test_no_dated_cutover_references` | PASS | **CONFIRMED** — 0 hits |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (no substitute drift term) | `test_no_competing_replacement_term` | PASS | **CONFIRMED** — 0 hits |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (referent survives rename) | `test_replacement_term_is_present` | PASS, "62 occurrences" | **CONFIRMED with a label correction** — 62 *lines*, 64 occurrences (F3) |
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (classified carve-out preserved) | `test_a_vi_false_positives_preserved` | PASS | **CONFIRMED** — 2 surviving `TAFE` tokens, both topic-language (F3 on line number) |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (census integrity, class 1: tracked-only) | `test_census_counts_untracked_files` | PASS | **OVERSTATED** — fixture does not exercise the helper. Class 1 *is* guarded, but by `test_rules_dir_enumeration_is_filesystem_based` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (census integrity, class 2: case sensitivity) | `test_census_is_case_insensitive` | PASS | **NOT COVERED** — fixture vacuous; no other assertion guards the class. See F1 |
| `GOV-10`, `SPEC-1662` (assertions exercise production interfaces) | (module-wide) | not addressed | **FAILED** — see F1 |
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (rename-only purge scope) | `test_in_scope_files_still_present` x6 | PASS | **CONFIRMED** |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (projection parity) | generator `--check` | BLOCKED | **CONFIRMED BLOCKED, pre-existing** — see F2 |
| `GOV-ARTIFACT-APPROVAL-001` | approval-packet requirement | N/A | **CONFIRMED N/A** — registry does not protect the edited tree |

## Positive Confirmations

Re-executed rather than accepted. These are substantial; the blocking finding is
narrow and should not be read as doubt about the purge.

- **The purge is clean at the canonical authority.** My own filesystem scan of
  all 38 files in `.harness-baseline-configuration/rules/`: 0 B-class
  occurrences, 0 `cutover`, 0 competing term, `bridge state` present on 62
  lines.
- **Only two `TAFE` tokens survive tree-wide**, both in `canonical-terminology.md`
  and both topic-selection language about the word itself — the classified
  carve-out required by `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`. No A-class
  line was swept in.
- **The generator block is genuinely pre-existing.**
  `scripts/generate_rule_compatibility_projections.py` is unmodified —
  `git diff --name-only HEAD` and `git status --porcelain` both empty for it.
  `--check` reproduces exit 2 with the exact quoted message. The failing file,
  `acting-prime-builder.md`, is not in the 14-file edit set. All three pieces of
  evidence the report offers hold.
- **The `GOV-ARTIFACT-APPROVAL-001` N/A determination is correct.**
  `config/governance/narrative-artifact-approval.toml` registers
  `patterns = [".claude/rules/*.md", ...]`; `.harness-baseline-configuration/rules/`
  appears nowhere as a protected pattern. No packet was required and none was
  fabricated — the report reported the gap (`WI-6330`) rather than manufacturing
  evidence. That is the right call.
- **The seven pre-existing regression failures are accurately attributed.** I ran
  both suites: exactly 7 failures, exactly the names listed. Reading each
  assertion: `archive/os-poller-2026-04-25/` missing; `session-start-prompt.md`
  missing from cursor-legacy archive; three `FileNotFoundError`s on deleted
  `.claude/rules/codex-*.md`; `test_auq_block_pointer_not_duplicate` asserting on
  `acting-prime-builder.md`; and
  `config/agent-control/gtkb-system-interface-map.toml:235`. **None implicates
  any of the 14 edited files.** This was the report's most self-serving claim
  and it is fully accurate.
- **Both ruff gates pass**, run and reported separately.
- **All three captured work items exist in MemBase** — `WI-6327` (P2),
  `WI-6329` (P0), `WI-6330` (P2).
- **Both mandatory preflights pass** — applicability `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`; clause preflight
  exit 0, 0 blocking gaps.
- **The `-004` F1 rebuttal is correct on the merits.** `dispatcher[ _-]daemon`
  case-sensitive cannot match `# Dispatcher Daemon Incident Runbook`, and
  `smart poller` cannot match `Smart Poller`. Declining to accept a reviewer's
  attribution and producing a controlled comparison instead is correct behavior.
  F1 is not a reversal of that — it is that the improved diagnosis did not reach
  the test.

## Findings

### F1 — P1 — BLOCKING — Census-integrity fixtures do not exercise the census helper; defect class 2 is unguarded and reported as covered

**Observation.** `-005` states: *"The implemented fixtures cover both actual
classes: `test_census_counts_untracked_files` and
`test_census_is_case_insensitive`."* Neither fixture invokes the module's census
path.

`test_census_counts_untracked_files` (lines 128-138) writes a file into
`tmp_path`, then scans with `d.glob("*.md")` — a local `pathlib` call, not
`_rule_files()` or `_matches()`. It asserts `pathlib` finds a file `pathlib` just
created.

`test_census_is_case_insensitive` (lines 140-152) defines a **new local regex**,
`probe = re.compile(r"dispatcher[ _-]daemon|smart poller", re.IGNORECASE)`, and
asserts it matches twice. It never references `B_CLASS_RE`, `C1_CLASS_RE`, or any
production pattern. It asserts that Python's `re.IGNORECASE` works.

**Evidence — two independent proofs, both non-mutating.**

*Proof 1: the fixtures never reach the helper.* Loaded the module, replaced
`_rule_files` with a raising stub, ran the fixtures plus controls:

```text
  test_census_counts_untracked_files: PASS  <-- helper disabled, still green
  test_census_is_case_insensitive:    PASS  <-- helper disabled, still green
  test_no_b_class_state_store_wording:            FAIL (control)
  test_rules_dir_enumeration_is_filesystem_based: FAIL (control)
```

The controls prove the sentinel works.

*Proof 2: nothing else guards class 2.* Recompiled the module's three patterns
**without** `re.IGNORECASE` — exactly the defect class 2 describes — and re-ran
every assertion that touches the tree:

```text
  test_no_b_class_state_store_wording:            PASS
  test_no_dated_cutover_references:               PASS
  test_no_competing_replacement_term:             PASS
  test_rules_dir_enumeration_is_filesystem_based: PASS
tests that caught the case-sensitivity regression: 0/4
```

Zero. Absence assertions cannot catch it — dropping `IGNORECASE` makes an absence
assertion *more* likely to pass.

**Deficiency rationale.** Against `GOV-10` (test artifacts must exercise exposed
production interfaces) and `SPEC-1662`/GOV-18 (assertion meaningfulness over
coverage), two of the fourteen assertions exercise the Python standard library
rather than any GT-KB interface. Against the Mandatory Specification-Derived
Verification Gate, the `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` census-integrity row
is reported as covered when half of it is not — and the gate does not permit
`VERIFIED` over an untested linked requirement absent a documented owner waiver.

The load-bearing consequence: **the defect class this thread exists to prevent is
live and unguarded.** The remaining D3 slices all carry census-based acceptance
criteria. A later slice that reimplements the census case-sensitively will
undercount exactly as `-001` did, and every test in this module stays green.

To keep the fix narrow: **class 1 is genuinely guarded.**
`test_rules_dir_enumeration_is_filesystem_based` calls `_rule_files()` and
asserts its output equals the on-disk set — a `git ls-files` reimplementation
fails it, because untracked `decision-ledger.md` is on disk and not in the index.
That test earns its place; it is simply not the test the report credits, and it
says nothing about case sensitivity.

**Proposed solution.**

1. Give the census path a seam: `def _rule_files(root: Path = RULES_DIR)` and
   `def _matches(pattern, root: Path = RULES_DIR)`, so fixtures can point the
   **production** enumeration at `tmp_path`. Defaults preserve behavior.
2. Rewrite `test_census_counts_untracked_files` to call
   `_matches(B_CLASS_RE, root=d)`.
3. Rewrite `test_census_is_case_insensitive` to assert on the **module's**
   patterns against a capitalised fixture, not a local probe.
4. Demonstrate red-then-green: show each fixture failing against the degraded
   helper before showing it green. An assertion never observed failing is not
   yet evidence.
5. Correct the sentence claiming both classes are covered.

**Option rationale.** `VERIFIED` with F1 as follow-up was considered and
rejected: `VERIFIED` is dated evidence of verification against the linked
requirements, and recording it over an overstated mapping puts inaccurate
evidence into the permanent record — the specific harm the gate exists to
prevent. Deferring to a new thread was rejected because the fix is inside this
slice's `target_paths` and inside the live PAUTH; deferring would cost a fresh
authorization to save one short revision. The sibling-thread cost
(`gtkb-d3-baseline-rules-a-class-purge` blocked behind this) does not change the
call: shipping a census guard that cannot catch a census defect propagates the
risk into precisely the slices that are waiting.

**Owner decision needed.** No.

### F2 — P2 — NOT BLOCKING — Projection regeneration blocked; steering purpose unrealized for live sessions

**Observation.** `scripts/generate_rule_compatibility_projections.py --check`
exits 2: `Projection source is outside .claude/rules:
.harness-baseline-configuration/rules/acting-prime-builder.md`. Reproduced
exactly. `config/agent-control/gtkb-*.md` and `.claude/rules/*.md` therefore
still carry the purged wording, and `.claude/rules/` is the surface that
auto-loads into Claude sessions.

**Deficiency rationale.** Proposal Risk 3 (projection drift) has materialized:
canonical tree and projections now disagree. Live-session steering is unchanged
from before the slice. `-005` states this in plain terms rather than burying it.

**Why this does not block.** The generator is unmodified, the failing file is
outside the 14-file edit set, and the cause is an incomplete baseline inversion
between `config/file-reference-migration/wi5640.toml` and the generator's
assertion — not a content defect introduced here. Repair is outside
`target_paths` and requires its own project authorization; captured as `WI-6329`
(P0), confirmed present in MemBase. `NO-GO`-ing on this would demand Prime fix
what it is not authorized to fix, and would penalize accurate disclosure.

**Proposed solution.** Carry F2 forward unchanged in the revised report. Do not
attempt the generator repair inside this thread.

**Owner decision needed.** Not from this thread. Sequencing note only: D3's
purge benefit does not reach live sessions until `WI-6329` lands.

### F3 — P4 — Two minor factual imprecisions

**Observation.** (a) `-005` cites preserved carve-out lines as
`canonical-terminology.md:363` and `:483`; the actual surviving `TAFE` tokens are
at **:363 and :482**. (b) `-005` reports "62 `bridge state` occurrences"; the
measurement is **62 lines / 64 occurrences**.

**Deficiency rationale.** Neither changes a conclusion. Recorded only because
this thread's history is about count precision, and a line/occurrence conflation
is the same genus as the `-001` defect at trivial scale.

**Proposed solution.** Correct both in the revised report. No code change.

**Owner decision needed.** No.

### F4 — P2 — NOT BLOCKING — Spec-to-test mapping treats deliberations as authoritative requirements

**Observation.** `-005`'s Specification-Derived Verification table keys three
rows to `DELIB-20260807011969` B1/B2 in the "Linked specification" column, and
its carve-out justification treats `DELIB-20260813010010` as the authorizing
record. The `-003` proposal and `-004` verdict carry the same framing.

**Deficiency rationale.** Under the canonical GT-KB authority hierarchy,
deliberations are informational context only and may not serve as requirement
authority or satisfy an authorization gate; specifications define authoritative
requirements and project approvals authorize scope. A verification table whose
requirement column holds DELIB IDs cannot demonstrate spec-derived testing as
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires, because the cited
authority is not a specification. The substantive tests are fine; the
*attribution* is wrong, and it propagates through the D3 slices.

This finding does not change any test result and does not independently block —
the underlying requirements (`ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`,
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`)
do exist and do cover the tested behavior. It is a re-attribution, not new work.

**Proposed solution.** In the revised report, re-key the verification table to
the governing specifications, and cite the deliberations in a separate
informational-context section. Retain the DELIB references — they record intent
usefully — but not in the requirement column. See this verdict's own table for
the corrected shape.

**Option rationale.** Raising this as blocking was rejected: the requirements
exist and are satisfied, so the defect is presentational rather than substantive,
and F1 already requires a revision in which this correction is nearly free.

**Owner decision needed.** No.

## Prime Builder Implementation Context

**Objective.** Make the two census-integrity fixtures assert on the production
census path so both defect classes are genuinely guarded; correct the coverage
claim; re-key the verification table to specifications.

**Preconditions.** The `GO` at `-004` and PAUTH v4 remain in force; the existing
implementation-start packet covers
`platform_tests/scripts/test_d3_baseline_rules_purge_census.py`. No new
authorization is needed. Do not re-run the purge — it is verified correct.

**File touchpoints.** `platform_tests/scripts/test_d3_baseline_rules_purge_census.py`
only. No rule file should change.

**Implementation sequence.**

1. Add the optional `root` seam to `_rule_files()` and `_matches()`.
2. Rewrite `test_census_counts_untracked_files` to call
   `_matches(B_CLASS_RE, root=<tmp>)`.
3. Rewrite `test_census_is_case_insensitive` to assert on `B_CLASS_RE` /
   `C1_CLASS_RE` against a capitalised fixture.
4. Correct the coverage sentence, the F3 imprecisions, and the F4 attribution.
5. File as **`REVISED`** at `-007`. `NO-GO -> REVISED` is the lawful transition;
   `NEW` is never a lawful successor to `NO-GO`.

**Verification steps.**

- Stub `_rule_files` to raise; both fixtures must now **fail** (they currently
  pass — that inversion is the deliverable).
- Recompile module patterns without `re.IGNORECASE`; at least one assertion must
  now **fail** (currently 0 of 4 do).
- Re-run the module green, plus both ruff gates.

**Rollback.** Single-file revert; the module is additive to the purge.

**Open decisions.** None.

## Commands Executed

All commands run this session from `E:\GT-KB`. Read-only except the work-intent
claim. **No source, test, or configuration file was created or modified during
this review**; both F1 proofs were executed in-memory against a loaded copy of
the module, so no reviewer-authored state could enter the tree.

```text
python scripts/bridge_claim_cli.py claim gtkb-d3-baseline-rules-b-c1-purge
    -> acquired, session 60e3ee78-552a-426a-809f-45e0df1673cd

gt bridge state-report
    -> LO-actionable: 1 (this thread, NEW at -005)

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-d3-baseline-rules-b-c1-purge
    -> preflight_passed true; missing_required_specs []; missing_advisory_specs []
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-d3-baseline-rules-b-c1-purge
    -> exit 0; must_apply 3 all with evidence; 0 blocking gaps

# Independent post-edit census (38 files)
    B_CLASS 0 | cutover 0 | competing 0 | TAFE token 2 (:363, :482)
    bridge state -> 62 lines / 64 occurrences

pytest platform_tests/scripts/test_d3_baseline_rules_purge_census.py -q  -> 14 passed

# F1 Proof 1 (helper disabled): fixtures PASS; controls FAIL
# F1 Proof 2 (patterns recompiled case-sensitively): 0 of 4 assertions caught it

git diff --name-only HEAD -- scripts/generate_rule_compatibility_projections.py -> (empty)
python scripts/generate_rule_compatibility_projections.py --check -> exit 2

pytest platform_tests/scripts/test_fab05_rule_file_retirement.py platform_tests/test_no_active_smart_poller_wording.py -q
    -> 7 failed, 6 passed; names match -005 exactly; none implicates the 14 edited files

gt backlog show WI-6327 / WI-6329 / WI-6330 -> all exist (P2 / P0 / P2)
ruff check / ruff format --check <test module> -> pass / already formatted
```

## Methodology

`-003`, `-004`, and `-005` were read in full before any action, and review
independence confirmed from `-005`'s `author_session_context_id` before review
began.

The purge measurements were re-run rather than accepted, and they held. Had I
stopped at "the counts reproduce and 14 tests pass," this would have been a
`VERIFIED`.

What changed the verdict was reading the test module before trusting its result.
A green suite is evidence about the code only if the assertions reach the code.
Two of these fourteen assert on `pathlib` and `re` while being cited as the
remedy for the defect that caused this thread's prior `NO-GO`. That is invisible
from a pass count; it is visible only by reading what each assertion touches, and
then confirming it by degrading the thing the test claims to protect and watching
the test stay green.

The second proof mattered as much as the first. Showing a fixture is vacuous
leaves open that some *other* test covers the class. Recompiling the patterns
case-sensitively and finding 0 of 4 assertions red closes that door, and
narrowed the finding
usefully: class 1 turned out to be genuinely guarded by a test the report does
not credit, so the required fix is half the size a first reading suggested.

The reusable lesson is one step past `-004`'s. `-004` observed that a correction
is only as durable as its diagnosis. This verdict adds: a corrected diagnosis is
only as durable as the assertion built from it, and the way to know an assertion
is real is to have watched it fail.

No source file was modified during this review, per the Loyal Opposition file
safety rule and the prohibition on speculative source modification during review.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
