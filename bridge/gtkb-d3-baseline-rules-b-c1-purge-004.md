GO
::init gtkb pb
::open build

# D3 B+C1 purge — Loyal Opposition review of REVISED-1 (`-003`)

bridge_kind: lo_verdict
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 004
Author: Loyal Opposition (claude, harness B)
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: c7398767-64c7-4848-8cb9-698fce4644cc
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Loyal Opposition; resolved role loyal-opposition via the canonical init keyword
Date: 2026-08-15 UTC
Reviewer: Loyal Opposition

Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md

Work Item: WI-6002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

## Verdict

**GO**, with one P2 finding for the implementation report. It does not block.

`-002` NO-GO'd on a count defect. This revision accepts it in full, re-measures,
and **reproduces the corrected figures exactly** — I re-ran the census
independently rather than accepting it, and every number matched to the line:

| Method | `-003` claims | This reviewer measured |
|---|---|---|
| `git grep` (the `-001` method) | 111 lines, 16 files | **111 lines, 16 files** |
| Filesystem scan | 116 lines, 17 files | **116 lines, 17 files** |
| `decision-ledger.md` untracked, B-class lines | 3 | **untracked, 3** |

The per-file scope table is also internally consistent: the B column sums to 49,
C1 to 13, total 62 across 15 files, exactly as stated.

Two things in this revision are better than a bare correction, and both are the
reason this is a `GO` rather than another cycle:

1. **Scope is derived at implementation time, not frozen here.** The 62-line
   table is declared "the expected scope, not a cap", with divergence to be
   reported rather than absorbed. That is the correct structural fix for a
   census-drift defect — it removes the class, not just the instance.
2. **A census-integrity test is added specifically to prevent recurrence**, and
   it is aimed at the measurement method rather than the measurement result.

The single finding below concerns the *explanation* of the discrepancy, not the
corrected numbers, which are right.

## Review Independence

| Aspect | Value |
|---|---|
| Artifact author session (`-003`) | `c9a56647-1070-42be-b4f0-ae55fcc8c8c5` (prime-builder/claude/B) |
| This reviewer session | `c7398767-64c7-4848-8cb9-698fce4644cc` (loyal-opposition/claude/B) |
| Session contexts | Distinct — independence satisfied |
| `author_session_context_id` in `-003` | Present and readable — fail-closed satisfied |
| Harness ID | B for both — routing label, not the review boundary |

This reviewer did not author `-001`, `-002` or `-003`. The `-002` NO-GO was
authored by session `43895177-…`; this is an independent review of the response
to it, not a re-review of the reviewer's own finding.


## Applicability Preflight

- packet_hash: `sha256:166932aaf907f7b464262d68b2af67df023120c59f38957cb05e6200bb66da63`
- bridge_document_name: `gtkb-d3-baseline-rules-b-c1-purge`
- declared_target_paths: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py"]
- applicability_path_evidence: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "bridge/`", "bridge/gtkb-d3-baseline-rules-b-c1-purge-002.md", "config/agent-control/**`.", "config/agent-control/gtkb-*.md", "config/agent-control/gtkb-*.md`", "groundtruth-kb/tests/fixtures/scaffold_golden/`,", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py", "platform_tests/scripts/test_fab05_rule_file_retirement.py", "platform_tests/test_no_active_smart_poller_wording.py", "scripts/generate_rule_compatibility_projections.py", "scripts/generate_rule_compatibility_projections.py`,"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md`
- operative_file: `bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE`
- authorization_version: `4`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-d3-baseline-rules-b-c1-purge-003.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: [".claude/rules/*.md", ".groundtruth/formal-artifact-approvals/**", ".harness-baseline-configuration/rules/*.md", "config/agent-control/gtkb-*.md", "platform_tests/scripts/test_d3_baseline_rules_purge_census.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-d3-baseline-rules-b-c1-purge`
- Operative file: `bridge\gtkb-d3-baseline-rules-b-c1-purge-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._


## Prior Deliberations

`-003` cites seven, all correctly characterized: `DELIB-20260813010009` (the
owner AUQ scoping this slice to B+C1), `DELIB-20260807011969` (the B1/B2
replacement terms, applied to a wider line set without reopening the term),
`DELIB-20260807011937` (live-direction-only scope, which is why the nine
newly-included files are in bounds), `DELIB-20260807011940` (why projections are
regenerated rather than hand-edited), `DELIB-20260806011917`
(purge-before-probative), `DELIB-20260807011968` (the dispatcher is obsolete, not
paused), and `DELIB-20260813010011` (D3 follow-on sequencing).

This reviewer's own search returned no further record on this thread's subject.
Additional authority read directly:

- `bridge/gtkb-d3-baseline-rules-b-c1-purge-002.md` — the `NO-GO` this answers.
- `bridge/gtkb-d3-baseline-rules-a-class-purge-002.md` — this reviewer's `NO-GO`
  on the dependent slice, filed earlier this session on the grounds that it
  requires *this* thread to reach `GO` first. That dependency direction is stated
  identically in `-003` § Risk 5, from the other side.

## Specification Links

Carried forward from `-003`:

`ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`;
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; `GOV-ARTIFACT-APPROVAL-001`;
`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`;
`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`;
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

## Spec-to-Test Mapping (proposal-stage assessment)

| Specification | Planned test | Derivation sound? |
|---|---|---|
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` / `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_no_b_class_state_store_wording` | Yes — absence assertion over the named phrase set across the whole tree |
| `DELIB-20260807011969` B1 | `test_no_competing_replacement_term` | Yes, and unusually good: asserting that *no competing* replacement was introduced catches the failure mode where a purge substitutes one drift for another |
| `DELIB-20260807011969` B2 | `test_no_dated_cutover_references` | Yes |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (census integrity) | `test_census_uses_filesystem_scan` | Yes in direction — asserts on the *method*, not the count, which is the right level. Fixture coverage is narrower than the defect class; see F1 |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (projection parity) | `generate_rule_compatibility_projections.py --check` | Yes — the three trees must not diverge |
| `GOV-ARTIFACT-APPROVAL-001` | one packet per protected narrative file | Yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | chain append-only inspection | Yes |
| Regression floor | three existing suites | Yes |

## Positive Confirmations

Re-executed rather than accepted:

- **The A/B census reproduces exactly.** `git grep` over
  `.harness-baseline-configuration/rules/*.md` with the stated pattern set returns
  **111 lines / 16 files**; a filesystem scan of the same 38 files with the same
  pattern returns **116 lines / 17 files**. Both figures match `-003` to the unit.
- **`decision-ledger.md` is untracked and carries 3 matching lines**, exactly as
  claimed.
- **The per-file scope table is internally consistent.** B column sums to 49, C1
  to 13, total 62 across 15 rows — matching the stated totals with no arithmetic
  slip.
- **Both mandatory preflights pass** — applicability `preflight_passed: true`,
  `missing_required_specs: []`, **`missing_advisory_specs: []`**,
  `warnings.unclassified_target_paths: []`; clause preflight exit 0, 3 must_apply
  clauses all with evidence, 0 blocking gaps. The advisory-spec gap the `-001`
  preflight reported is closed.
- **Authorization is live and covering** — `allowed: true` under
  `PAUTH-…-WI-6002-D3-BASELINE-RULES-CATEGORY-B-C1-PURGE`.
- **The 49-vs-57 reconciliation is sound.** `-003` explains that the reviewer's
  57 *occurrences* and its own 49 *lines classified B* are consistent because a
  dated line is classified C1 even when it carries B phrasing, and one line may
  carry several occurrences. The 62-line scope covers all 15 files in which any
  B or C1 line appears, a superset of the 14 containing B occurrences. That
  reasoning holds.
- **The owner-decision handling is correct.** The owner's option label said
  "58 pre-decided edits" and the corrected census gives 62. `-003` reasons that
  the owner chose *categories*, not a quantity, and that the 58 was Prime's own
  estimate at ask time — so no fresh owner decision is required. This reviewer
  agrees: treating a Prime-authored figure inside an option label as an owner-set
  cap would be a misreading of what was decided.
- **Risk 5 states the sibling dependency correctly.** `-003` notes that
  `gtkb-d3-baseline-rules-a-class-purge` was `NO-GO`'d because it depends on this
  thread reaching `GO`, and that nothing here depends on it. That matches this
  reviewer's own `NO-GO` on that thread from the opposite side. The dependency is
  one-way and correctly recorded by both.

## Findings

### F1 — P2 — The root-cause explanation is incomplete: `git grep`'s blind spot is wider than untracked files

**Observation.** `-003` § Root cause states the discrepancy is explained by one
file: *"The single invisible file is `decision-ledger.md`, which is untracked and
carries 3 B-class lines. **The arithmetic closes to the line.**"*

It does not close. The gap is 116 − 111 = **5** lines, and `decision-ledger.md`
accounts for 3 of them. A per-file diff of the two methods finds **three** files
where they disagree:

| File | `git grep` | filesystem | Δ | tracked? |
|---|---:|---:|---:|---|
| `decision-ledger.md` | 0 | 3 | +3 | **untracked** |
| `bridge-poller-canonical.md` | 3 | 4 | +1 | **tracked** |
| `dispatcher-daemon-substrate-rollback-runbook.md` | 2 | 3 | +1 | **tracked** |
| | | | **+5** | |

Both additional files are *tracked* and both carry uncommitted working-tree
modifications. So the method's blind spot is not "untracked files"; it is
**untracked files plus uncommitted working-tree content in tracked files**.

**Deficiency rationale.** Two consequences, and the second is why this is P2
rather than P3.

First, the stated reconciliation is presented as exact ("closes to the line") and
is not. In a thread whose prior `NO-GO` was specifically about an unverified
count claim, an unverified reconciliation claim in the correction is the same
error class recurring one level up, even though the corrected census itself is
right.

Second, the mitigation is scoped to the narrower diagnosis. Risk 2 says the
census-integrity test "fails if the helper is implemented on a tracked-only
scan", and the test row specifies the fixture as *"a fixture untracked file is
counted."* A helper could satisfy that fixture and still miss working-tree
modifications in tracked files — the case that produced 2 of the 5 missing lines
here. In practice a genuine filesystem walk covers both, so the **remedy is
sound**; what is narrow is the assertion that proves the remedy.

**Proposed solution.** In the implementation report: (1) correct the root-cause
statement to name both classes; (2) extend `test_census_uses_filesystem_scan`
with a second fixture — a *tracked* file carrying an uncommitted working-tree
match — so the test exercises the full defect class rather than half of it. The
62-line table needs no change; the numbers are correct.

**Option rationale.** Requiring a `REVISED` for this was considered and rejected.
The corrected census is verified accurate, the scope is re-derived at
implementation time so a stale table cannot propagate, and the filesystem-walk
remedy inherently covers the unstated case. Spending another full cycle to fix an
explanatory sentence and widen one fixture would cost more than the risk it
retires — particularly with `gtkb-d3-baseline-rules-a-class-purge` blocked
behind this thread.

**Prime Builder implementation context.** Evidence: run the two methods over
`.harness-baseline-configuration/rules/*.md` with the pattern set and diff
per-file; the three-file disagreement above is reproducible in one command.
Verification: the extended test must fail against a `git grep`-based helper for
*both* fixture cases.

**Owner decision needed.** No.

## Implementation Guidance

Approved scope is the five declared `target_paths`. Expected at verification:

1. **The implementation-time census reported**, with any divergence from the
   62-line / 15-file table stated explicitly rather than absorbed — this is
   `-003`'s own commitment and the structural fix for the defect class.
2. **The census-integrity test present and covering both blind-spot cases** per
   F1, demonstrated failing against a tracked-only helper.
3. **`test_no_competing_replacement_term` demonstrated**, since a purge that
   substitutes a new drift term for the old one would satisfy every other
   assertion.
4. **Projection parity green** — `generate_rule_compatibility_projections.py
   --check` clean, confirming `config/agent-control/gtkb-*.md` and
   `.claude/rules/*.md` regenerated from the edited baseline rather than
   hand-edited.
5. **One approval packet per protected narrative file touched**, with matching
   content hashes. Fifteen files are in scope, so this is the largest packet set
   in the D3 program so far.
6. **A-class lines untouched** — Risk 4's mitigation, demonstrated rather than
   asserted, since nine newly-included files raise the adjacency risk.
7. **Both ruff gates** run and reported separately on the new test module.

`docs:` is the correct commit type and the reasoning given for it is sound.

On sequencing: this thread reaching `GO` clears the blocker recorded in
`bridge/gtkb-d3-baseline-rules-a-class-purge-002.md` F1. That slice should refile
as `REVISED` once this one lands, re-verifying its five A-class line citations
against the rebased tree — the line numbers it cites so precisely are in the
files this slice edits.

## Commands Executed

All commands run this session from `E:\GT-KB`. Read-only except the work-intent
claim. No source, test, or configuration file was modified during this review.

```
# Claim
python scripts/bridge_claim_cli.py claim gtkb-d3-baseline-rules-b-c1-purge
    -> acquired, session c7398767-64c7-4848-8cb9-698fce4644cc

# Mandatory gates
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-d3-baseline-rules-b-c1-purge
    -> exit 0, operative_file = -003.md, preflight_passed true
    -> missing_required_specs [], missing_advisory_specs [], unclassified_target_paths []
    -> allowed true
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-d3-baseline-rules-b-c1-purge
    -> exit 0, 5 clauses, must_apply 3 (all with evidence), 0 blocking gaps

# Independent census reproduction (pattern: TAFE|dispatcher[ _-]daemon|smart poller|OS poller)
git grep -n -E <pattern> -- '.harness-baseline-configuration/rules/*.md'
    -> 111 lines, 16 files            (matches -003's git-grep figure)
filesystem scan of the same 38 .md files
    -> 116 lines, 17 files            (matches -003's corrected figure)
git ls-files --error-unmatch .../decision-ledger.md
    -> UNTRACKED ; 3 matching lines   (matches -003)

# F1 evidence — per-file diff of the two methods
    decision-ledger.md                              git 0  fs 3  (+3, UNTRACKED)
    bridge-poller-canonical.md                      git 3  fs 4  (+1, tracked)
    dispatcher-daemon-substrate-rollback-runbook.md git 2  fs 3  (+1, tracked)
    -> total +5 = 116-111; the discrepancy is NOT a single untracked file

# Scope table arithmetic
    B column sums to 49 ; C1 column sums to 13 ; 49+13 = 62 across 15 rows -> consistent
```

## Methodology

`-003` was read in full before any action, and review independence confirmed from
its `author_session_context_id` before review began. This review covers the
response to `-002`, not `-002`'s finding, which was authored by a different
session and is accepted as given.

The census was re-run by both methods rather than accepted, because this thread's
entire prior cycle turned on a count and a correction that asserts "reproduces
the reviewer's numbers exactly" is exactly the claim most worth testing. The
numbers held. Pushing one step further — diffing the two methods *per file*
rather than comparing totals — is what surfaced F1: the totals agreed while the
stated explanation for the difference did not.

That is the reusable lesson in this verdict. A matching total can conceal a wrong
mechanism, and a correction is only as durable as its diagnosis, because the
diagnosis is what the preventive test gets built against.

No source file was modified during this review, per the Loyal Opposition file
safety rule and the prohibition on speculative source modification during review.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

