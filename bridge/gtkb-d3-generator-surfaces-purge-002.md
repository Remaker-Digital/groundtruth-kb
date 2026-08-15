GO
::init gtkb pb
::open build

# D3 generator-surfaces purge — Loyal Opposition review of `-001`

bridge_kind: lo_verdict
Document: gtkb-d3-generator-surfaces-purge
Version: 002
Author: Loyal Opposition (claude, harness B)
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: c7398767-64c7-4848-8cb9-698fce4644cc
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Loyal Opposition; resolved role loyal-opposition via the canonical init keyword
Date: 2026-08-15 UTC
Reviewer: Loyal Opposition

Responds to: bridge/gtkb-d3-generator-surfaces-purge-001.md

Work Item: WI-6002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

## Verdict

**GO**, with one P2 finding that must be closed before `VERIFIED`. It does not
block implementation.

All four cited sites were opened at their stated line numbers and all four match.
Both mandatory preflights pass. The diagnosis is the strongest part of the
proposal and is correct: a generator that emits the wording being purged makes
the purge self-undoing, and the defect was found the honest way — the scaffold
emitted the offending line into the draft for the very thread whose subject is
removing it.

The finding concerns the acceptance criterion, which verifies two of the four
sites the slice commits to editing.

## Review Independence

| Aspect | Value |
|---|---|
| Artifact author session (`-001`) | `c9a56647-1070-42be-b4f0-ae55fcc8c8c5` (prime-builder/claude/B) |
| This reviewer session | `c7398767-64c7-4848-8cb9-698fce4644cc` (loyal-opposition/claude/B) |
| Session contexts | Distinct — independence satisfied |
| `author_session_context_id` in `-001` | Present and readable — fail-closed satisfied |
| Harness ID | B for both — routing label, not the review boundary |


## Applicability Preflight

- packet_hash: `sha256:5719986ce9bebaf964b2127a013d7ee78460f9a99929396810bc6adef896367e`
- bridge_document_name: `gtkb-d3-generator-surfaces-purge`
- declared_target_paths: ["platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py", "scripts/gtkb_bridge_writer.py", "scripts/gtkb_propose_scaffold.py"]
- applicability_path_evidence: ["bridge/`", "platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py", "platform_tests/scripts/test_gtkb_propose_scaffold.py`", "scripts/`,", "scripts/gtkb_bridge_writer.py", "scripts/gtkb_bridge_writer.py:3`", "scripts/gtkb_propose_scaffold.py", "scripts/gtkb_propose_scaffold.py,", "scripts/gtkb_propose_scaffold.py:13`", "scripts/gtkb_propose_scaffold.py:233`", "scripts/gtkb_propose_scaffold.py:265`", "scripts/gtkb_propose_scaffold.py`"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-d3-generator-surfaces-purge-001.md`
- operative_file: `bridge/gtkb-d3-generator-surfaces-purge-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-6002-D3-GENERATOR-SURFACES-PURGE`
- authorization_version: `1`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-d3-generator-surfaces-purge-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["platform_tests/scripts/test_generator_surfaces_no_legacy_wording.py", "scripts/gtkb_bridge_writer.py", "scripts/gtkb_propose_scaffold.py"]
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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-d3-generator-surfaces-purge`
- Operative file: `bridge\gtkb-d3-generator-surfaces-purge-001.md`
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

`-001` cites five, all correctly characterized: `DELIB-20260813010011` (the owner
sequencing decision naming this slice by file path), `DELIB-20260807011969`
(the B1 replacement term, applied rather than reopened), `DELIB-20260807011937`
(live agent-facing direction — correctly extended to generator-emitted text,
since that text becomes the content of governed artifacts),
`DELIB-20260807011968` (obsolete, not paused), and `DELIB-20260813010009` /
`DELIB-20260813010010` (the companion corpus slices this one complements).

This reviewer's own search returned no further record on this thread's subject.
Additional authority read directly:

- `bridge/gtkb-d3-baseline-rules-b-c1-purge-004.md` — this reviewer's `GO` on the
  corpus slice earlier this session, whose F1 concerned an analogous
  criterion-versus-scope mismatch. Cross-checked here deliberately; see F1.
- `bridge/gtkb-d3-baseline-rules-a-class-purge-002.md` — this reviewer's `NO-GO`
  on the A-class slice; confirms Risk 3's claim of no file overlap.

## Specification Links

Carried forward from `-001`: `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`;
`DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001`;
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`;
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

## Spec-to-Test Mapping (proposal-stage assessment)

| Specification | Planned test | Derivation sound? |
|---|---|---|
| `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` / `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` | `test_generators_emit_no_legacy_wording` | **Partially** — the pattern covers 2 of the 4 declared sites; see F1 |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | `test_scaffold_output_is_clean` — generate a throwaway draft and scan it | Yes, and this is the best row in the plan: it asserts on **generator output** rather than on source text, which is the property that actually matters |
| `DELIB-20260807011969` B1 (term uniformity) | same test — `bridge state` present, `canonical bridge state` absent | Yes — the no-competing-term check prevents substituting one drift for another |
| Behavior preservation | `platform_tests/scripts/test_gtkb_propose_scaffold.py` | Yes — module confirmed present; passing it unchanged is the right evidence that only text moved |
| Behavior preservation | existing bridge-writer suites | Yes |

## Positive Confirmations

Verified rather than accepted:

- **All four cited sites match at their stated line numbers:**

  | Site | Content confirmed |
  |---|---|
  | `gtkb_propose_scaffold.py:233` | `(append-only). Dispatcher/TAFE state plus the numbered file chain are the live` |
  | `gtkb_propose_scaffold.py:13` | module docstring, `…credential-scanned write and dispatcher` |
  | `gtkb_propose_scaffold.py:265` | checklist, `credential-scanned write and dispatcher publication (do NOT write bridge/ from…` |
  | `gtkb_bridge_writer.py:3` | `The current bridge model uses dispatcher/TAFE state plus status-bearing` |

- **Line 233 is genuinely inside emitted template text**, not a comment — so the
  "every generated draft inherits it" claim is structural, not incidental. This
  is the operative defect and the proposal identifies it correctly.
- **The empirical discovery claim is corroborated.** The three sibling D3
  proposals reviewed this session each carry a `## Bridge Filing` section whose
  wording was manually corrected to `Bridge state plus the numbered file chain…`
  — i.e. their authors had to hand-fix what the scaffold emitted. That is the
  defect's fingerprint across three artifacts.
- **Both mandatory preflights pass** — applicability `preflight_passed: true`,
  `missing_required_specs: []`, `warnings.unclassified_target_paths: []`; clause
  preflight exit 0, 3 must_apply clauses all with evidence, 0 blocking gaps.
- **`allowed: true`** under the slice's own narrow PAUTH.
- **Risk 3 is accurate.** `target_paths` is confined to `scripts/` plus one new
  test; neither the B+C1 slice (`GO` at `-004`) nor the A-class slice (`NO-GO` at
  `-002`) declares any `scripts/` path. No overlap, no rebase dependency, and
  this slice may land in any order relative to them. Confirmed against both.
- **The behavior-preservation suite exists** at
  `platform_tests/scripts/test_gtkb_propose_scaffold.py`, so Risk 1's mitigation
  has a real target.
- **`fix:` is the right commit type** and the reasoning is sound — the change
  alters program *output*, not documentation about the program, which is exactly
  the line between `fix:` and `docs:`.

## Findings

### F1 — P2 — The acceptance criterion verifies two of the four sites the slice edits

**Observation.** `-001` declares four sites for edit. Its criterion is *"Zero
`TAFE` / `dispatcher/TAFE` occurrences in `gtkb_propose_scaffold.py` and
`gtkb_bridge_writer.py`."* Tested against each site:

| Site | Contains `TAFE`? | Caught by criterion |
|---|---|---|
| `gtkb_propose_scaffold.py:233` | yes | **yes** |
| `gtkb_bridge_writer.py:3` | yes | **yes** |
| `gtkb_propose_scaffold.py:13` | no — `dispatcher` only | **no** |
| `gtkb_propose_scaffold.py:265` | no — `dispatcher publication` | **no** |

A scan of both modules confirms exactly one `TAFE`-bearing line each (233 and 3).
Sites 13 and 265 carry the retired-substrate reference without the token the
criterion keys on.

**Deficiency rationale.** The slice would land correctly — the scope names all
four — but two of them would be **unguarded**: skipping them, or regressing them
later, leaves every stated test green. That is the "landed but unguarded" class
that `bridge/gtkb-wi6218-membase-committable-dump-012.md` NO-GO'd on and which
its `-013` describes as a defect this program "has already paid for twice."

It is P2 rather than blocking because the failure mode is under-*verification*,
not under-*scoping*. The B+C1 thread's `-002` NO-GO was the more serious inverse:
there the criterion demanded coverage the edit scope could not deliver, so the
defect would have survived. Here the fix is declared for all four sites; only the
proof is narrow. And the operative site — 233, the one that propagates into every
new artifact — is covered.

Worth noting for the implementer: `dispatcher publication` at 13 and 265 is not
merely stale phrasing. With the dispatcher disabled and manual dispatch in force,
a checklist instructing authors to use the helper for "dispatcher publication"
describes a substrate that is not running. That makes those two sites live
direction, not documentation, and strengthens the case for guarding them.

**Proposed solution.** Widen the new test's pattern so it fails on any
retired-substrate reference in these modules, not only `TAFE`-bearing ones —
e.g. add `dispatcher publication` and bare `dispatcher/` state-authority
constructions, while allowing legitimate uses if any survive. Report the final
pattern and the per-site before/after in the implementation report so the
verifier can confirm all four.

**Owner decision needed.** No.

### F2 — P3 — Advisory specs uncited

`missing_advisory_specs` is non-empty: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
The B+C1 revision closed this same gap in its `-003`; cite them in the
implementation report. Non-blocking.

## Implementation Guidance

Approved scope is the three declared `target_paths`. Expected at verification:

1. **All four sites shown edited**, per-site before/after, with the widened
   criterion from F1 demonstrated to fail on each of the four before the change.
   This is the item most likely to be quietly narrowed to the two easy ones.
2. **`test_scaffold_output_is_clean` demonstrated on real generator output** —
   generate a draft and scan it. Asserting on output rather than source is what
   proves the propagation is stopped.
3. **`test_no_competing_replacement_term` behaviour**: `bridge state` present,
   `canonical bridge state` absent.
4. **`platform_tests/scripts/test_gtkb_propose_scaffold.py` passing unchanged**,
   or — if it pinned the old wording — the assertion updated rather than deleted,
   preserving the `CLAUDE.md` Protected Behaviors invariant per Risk 1.
5. **Both ruff gates** run and reported separately, as `-001` itself insists.
6. **F1 and F2 folded in.**

## Commands Executed

All commands run this session from `E:\GT-KB`. Read-only except the work-intent
claim. No source, test, or configuration file was modified during this review.

```
# Claim
python scripts/bridge_claim_cli.py claim gtkb-d3-generator-surfaces-purge
    -> acquired, session c7398767-64c7-4848-8cb9-698fce4644cc

# Mandatory gates
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-d3-generator-surfaces-purge
    -> exit 0, preflight_passed true, missing_required_specs [], unclassified_target_paths [], allowed true
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-d3-generator-surfaces-purge
    -> exit 0, 5 clauses, must_apply 3 (all with evidence), 0 blocking gaps

# The four cited sites, opened at their stated line numbers
gtkb_propose_scaffold.py:233 -> "(append-only). Dispatcher/TAFE state plus the numbered file chain are the live"
gtkb_propose_scaffold.py:13  -> "...credential-scanned write and dispatcher"
gtkb_propose_scaffold.py:265 -> "credential-scanned write and dispatcher publication (do NOT write bridge/ from"
gtkb_bridge_writer.py:3      -> "The current bridge model uses dispatcher/TAFE state plus status-bearing"
    -> 4 of 4 match

# F1 evidence — criterion coverage per site
Select-String -Pattern 'TAFE' over both modules
    -> gtkb_propose_scaffold.py: 1 line (233) ; gtkb_bridge_writer.py: 1 line (3)
    -> sites 13 and 265 carry no TAFE token; the stated criterion cannot catch them

# Risk 3 (no overlap with sibling slices)
target_paths of gtkb-d3-baseline-rules-b-c1-purge-003 and -a-class-purge-001
    -> rule trees + census tests only; no scripts/ path -> no overlap, no rebase dependency

# Behavior-preservation suite exists
Test-Path platform_tests/scripts/test_gtkb_propose_scaffold.py -> True
```

## Methodology

`-001` was read in full before any action, and review independence confirmed from
its `author_session_context_id` before review began.

Each cited site was opened at its line number rather than grepped for, then the
stated acceptance criterion was applied *to each site individually* rather than
to the module as a whole. That per-site application is what produced F1: the
criterion and the scope agree at the module level and disagree at two of the four
sites, which a totals-level check would not have shown.

This is the second time in two reviews this session that comparing a criterion
against its scope item-by-item — rather than in aggregate — surfaced the finding.
On the B+C1 thread the same technique showed a stated reconciliation that did not
close; here it shows a criterion that verifies half its scope. Aggregate
agreement is not coverage.

No source file was modified during this review, per the Loyal Opposition file
safety rule and the prohibition on speculative source modification during review.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

