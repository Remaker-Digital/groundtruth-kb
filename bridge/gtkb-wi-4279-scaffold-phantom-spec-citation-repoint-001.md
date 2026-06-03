NEW

bridge_kind: governance_review
Document: gtkb-wi-4279-scaffold-phantom-spec-citation-repoint
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 2b16ba08-a904-4f3c-976b-889bf9b224c3
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project: PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS
Work Item: WI-4279

target_paths: ["groundtruth-kb/templates/rules/canonical-terminology.md", "groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/canonical-terminology.md", "groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/rules/canonical-terminology.md", "platform_tests/scripts/test_no_phantom_spec_citation.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-4279 — Re-point phantom GOV-CHAT-DERIVED-SPEC-APPROVAL-001 in the scaffold template + golden fixtures

## Source / Owner Directive

This proposal implements WI-4279 (`PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`), the
adopter-facing follow-on explicitly deferred by WI-3506. WI-3506 re-pointed the
phantom spec id `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` → `GOV-SPEC-CAPTURE-TRANSPARENCY-001`
in the three **live** `.claude/rules/*.md` files (GO at
`bridge/gtkb-wi-3506-phantom-spec-citation-repoint-002.md`), but the owner scoped
that change to the live files only. The identical phantom token survives in the
**scaffold copy** that adopter projects inherit via `gt project init`, plus its
two committed golden fixtures.

`rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/` returns
exactly three files (the phantom is absent from MemBase; `current_specifications`
returns NOT FOUND, while the replacement `GOV-SPEC-CAPTURE-TRANSPARENCY-001`
resolves, status `specified`):

1. `groundtruth-kb/templates/rules/canonical-terminology.md:306` (the scaffold source — the `requirement` glossary entry).
2. `groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/.claude/rules/canonical-terminology.md:306` (committed golden fixture).
3. `groundtruth-kb/tests/fixtures/scaffold_golden/local-only/.claude/rules/canonical-terminology.md` (committed golden fixture; same `requirement` entry).

The byte equality between the template and the two goldens is expected: the
scaffold passes `{{PROJECT_NAME}}`/`{{COPYRIGHT}}` through substitution but the
phantom token flows verbatim into scaffolded output, so the golden fixtures
captured it. Adopters who scaffold today inherit a glossary that cites a spec
that exists nowhere — a live instance of the rule-vs-MemBase drift
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` governs, propagated one tier further out.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03)** — adopter-facing template citation
  disposition. Question: given adopter projects won't have GT-KB's spec ids, how
  should the scaffold template cite the phantom's replacement? Owner selected:
  **"Mirror live fix → `GOV-SPEC-CAPTURE-TRANSPARENCY-001`"** over the
  genericize-the-id and placeholder-token alternatives. This is the owner-decision
  authority for this proposal. Rationale captured in the AUQ: it is consistent
  with both the live-file decision and the template's existing convention (its
  `Source:` lines already cite dozens of GT-KB `GOV/ADR/DCL` ids that adopters
  customize), and `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` confirms
  `GOV-SPEC-CAPTURE-TRANSPARENCY-001` is the correct governing surface for the
  cited "owner-visible confirmation on promotion to specification" behavior.

## Proposal Kind

`governance_review` — a citation correction in a scaffold template + its golden
fixtures + a regression-test extension. No source/runtime behavior changes; no
new capability surface.

**Approval-gate note (simplification vs WI-3506):** none of the four target
paths are protected narrative artifacts. `scripts/check_narrative_artifact_evidence.py`
returns `skipped_unprotected` for the template and golden fixtures (the protected
pattern `.claude/rules/*.md` is a single-level glob that matches only repo-root
rule files, not `groundtruth-kb/templates/rules/…` or the nested
`…/scaffold_golden/…/.claude/rules/…`). Unlike WI-3506's live files, **no
per-file formal-artifact-approval packets are required.**

## Exact Change

In each of the three glossary files, replace the citation token
`GOV-CHAT-DERIVED-SPEC-APPROVAL-001` with `GOV-SPEC-CAPTURE-TRANSPARENCY-001` in
the `requirement` entry sentence — "promotion to formal `specification` requires
owner-visible confirmation per `<spec>`." The surrounding sentence is unchanged.
Exactly one occurrence per file (verified by `rg -uu`).

Then extend `platform_tests/scripts/test_no_phantom_spec_citation.py` with a
scaffold-coverage tuple (the template + both goldens) and two assertions
(phantom-absent, replacement-present), parallel to the existing live-rule-file
assertions. This pins the corrected state so the phantom cannot silently
re-enter the scaffold source or its captured goldens.

## Out of Scope (Explicit)

- **Broader golden-fixture byte staleness.** The byte-equality golden tests
  (`test_scaffold_isolation.py::test_tp15_dual_agent_matches_golden_fixture`,
  `test_golden_fixture_diff_per_version.py`) are **already red** on `develop`:
  11 dual-agent files mismatch (bridge hooks, skill helpers, 4 rule files), driven
  by template-vs-golden drift unrelated to this token (e.g., the `bridge` entry's
  `ADVISORY` vs `ADVISORY, DEFERRED, WITHDRAWN` status line). This proposal does
  NOT regenerate the goldens via `scripts/_capture_scaffold_golden.py` — that would
  sweep in 11 files of unrelated drift. The phantom-absence assertions here are
  orthogonal to byte-equality and remain valid whether or not the goldens are
  later regenerated. The broad golden staleness is a separate hygiene WI.
- **Genericizing all GT-KB spec ids in the scaffolded glossary.** The template
  pervasively cites GT-KB-internal ids; whether adopter glossaries should
  genericize them is a broader template-design question, not resolved by this
  one-token fix. Owner chose mirror-live-fix for this token (AUQ above).
- Append-only `bridge/*.md` audit-trail files that mention the phantom historically.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the governing freshness spec (WI-4279's project); this re-point fixes a scaffold-tier rule-vs-MemBase drift instance it governs.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the live replacement spec (owner-visible spec capture/approval); confirmed present in MemBase (status `specified`). The re-point target.
- `GOV-ARTIFACT-APPROVAL-001` — cited for completeness; NOT applicable here because the four target paths are unprotected scaffold/test files (`check_narrative_artifact_evidence` → `skipped_unprotected`), so no approval packets are required.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-approval-gate contract; non-applicable per the same evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal; INDEX-canonical evidence below.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance (concrete links, this section).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item cited above; `governance_review` kind.
- `GOV-STANDING-BACKLOG-001` — WI-4279 captured in the MemBase backlog under the project.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all four target paths are in-root under `E:\GT-KB` (`groundtruth-kb/...`, `platform_tests/...`).

## Prior Deliberations

- WI-3506 + thread `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-001.md` … `-004.md` — the live-file repoint of the identical phantom token; `-001` proposal, `-002` GO (Opportunity Radar explicitly flagged this scaffold follow-on as out of scope and to be tracked by Prime), `-003` report, `-004` NO-GO (a report-side INDEX-canonical clause gap, NOT a substance defect; the live edits were confirmed correct).
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` — originating deliberation for `GOV-SPEC-CAPTURE-TRANSPARENCY-001`; confirms it is the governing surface for "surface every capture event + present full text on approve/reject," i.e. the behavior the phantom citation describes.
- `DELIB-2521` — owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (S376), the governing freshness spec.
- `bridge/gtkb-source-of-truth-freshness-governance-004.md` — Codex NO-GO that first caught the phantom propagating from rule text.
- `gt deliberations search "scaffold template canonical-terminology phantom spec citation adopter"` returned no deliberation specific to the scaffold-template slice beyond the governing decisions cited above.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement is
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (citations must resolve to live MemBase
specs). The owner AUQ (2026-06-03) fixes the replacement choice. No new
specification is required; this corrects a scaffold-tier citation to an existing
live spec.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — phantom absent + replacement present in template + both goldens | extended `test_no_phantom_spec_citation.py` scaffold-coverage assertions | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_no_phantom_spec_citation.py -q --no-header -p no:cacheprovider` | PASS |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` exists (not another phantom) | confirm replacement resolves in MemBase | `gt spec show GOV-SPEC-CAPTURE-TRANSPARENCY-001` (or `current_specifications` read) | present, status `specified` |
| phantom absent everywhere it lived | `rg -uu --hidden` repo sweep | `rg -uu --hidden "GOV-CHAT-DERIVED-SPEC-APPROVAL-001" groundtruth-kb/` | only append-only `bridge/*.md` history (no live/template/golden hits) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the edited test | `python -m ruff check platform_tests/scripts/test_no_phantom_spec_citation.py` ; `python -m ruff format --check …` | clean |

## Risk / Rollback

Low: a one-token citation correction in a scaffold template + two test fixtures
(sentence meaning preserved) + a regression-test extension. No protected-artifact
packets, no runtime/behavior change. Rollback is a single-commit revert. The
edit does not alter scaffold structure, file inventory, or any byte the
already-red golden byte-equality tests additionally depend on (those remain red
on the pre-existing 11-file drift, unchanged by this proposal).

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
a new `gtkb-wi-4279-scaffold-phantom-spec-citation-repoint` document list in
`bridge/INDEX.md`; append-only — no prior version or other document entry is
deleted or rewritten. `bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — governance citation correction in a scaffold template + test fixtures +
a regression test; no code-capability change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
