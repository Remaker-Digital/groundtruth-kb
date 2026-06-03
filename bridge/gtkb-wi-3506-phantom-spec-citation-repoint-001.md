NEW

bridge_kind: governance_review
Document: gtkb-wi-3506-phantom-spec-citation-repoint
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-wi-3506-phantom-repoint
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project: PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS
Work Item: WI-3506

target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/prime-builder-role.md", ".claude/rules/operating-model.md", "platform_tests/scripts/test_no_phantom_spec_citation.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-3506 — Re-point phantom GOV-CHAT-DERIVED-SPEC-APPROVAL-001 citation

## Source / Owner Directive

This proposal implements WI-3506 (`PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`). The
glossary term-by-term review (owner directive 2026-06-03) triaged all 73
canonical-terminology terms and surfaced exactly one substance defect: the
`requirement` entry cites `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, which does NOT
exist in MemBase (`current_specifications` returns NOT FOUND). The same phantom
is cited in two sibling rule files. The owner directed (AskUserQuestion
2026-06-03) "Fold into WI-3506 (all 3 files)" — re-point the phantom to the live
governing surface `GOV-SPEC-CAPTURE-TRANSPARENCY-001` across all three rule
files.

**Premature-resolution note:** WI-3506 is currently `Stage: resolved`, but the
phantom citations were never actually re-pointed (all three remain live). This
proposal lands the never-implemented fix WI-3506 documents as decision path (b);
it is itself a live instance of the rule-vs-MemBase drift that
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` governs.

## Proposal Kind

`governance_review` — a protected-narrative citation correction. It re-points
one phantom spec id to its live equivalent in three `.claude/rules/*.md` files
and adds a regression test. No source/runtime behavior changes. Each protected
file edit lands through its own formal narrative-artifact-approval packet
(`GOV-ARTIFACT-APPROVAL-001`).

## Exact Change

In each of the three files, replace the citation token
`GOV-CHAT-DERIVED-SPEC-APPROVAL-001` with `GOV-SPEC-CAPTURE-TRANSPARENCY-001`
(the surrounding sentence is unchanged):

- `.claude/rules/canonical-terminology.md:444` (the `requirement` glossary entry).
- `.claude/rules/prime-builder-role.md:50`.
- `.claude/rules/operating-model.md:25`.

Out of scope (noted for a follow-on): `groundtruth-kb/templates/rules/canonical-terminology.md`
(scaffold copy) carries the same phantom; the owner scoped this change to the
three live rule files. Bridge audit-trail files that mention the phantom
historically are append-only and are not touched.

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the governing freshness spec (WI-3506's project); this re-point fixes a live rule-vs-MemBase drift instance it governs.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the live replacement spec (owner-visible spec capture/approval); confirmed present in MemBase. The re-point target.
- `GOV-ARTIFACT-APPROVAL-001` — governs the three protected-narrative edits via per-file narrative-approval packets.
- `PB-ARTIFACT-APPROVAL-001` — narrative-approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-approval-gate + evidence-checker contract the packets satisfy.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec-linkage compliance.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item cited above; governance_review kind.
- `GOV-STANDING-BACKLOG-001` — WI-3506 linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking; all four target paths in-root.

## Prior Deliberations

- WI-3506 (`PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`) — the originating defect record naming the 3 files + the replacement spec + the owner-gated decision.
- `bridge/gtkb-source-of-truth-freshness-governance-004.md` — Codex NO-GO (FINDING-P1-002) that first caught the phantom propagating from `operating-model.md` rule text into a bridge proposal.
- `bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-*.md` — prior NO-GO of the same phantom citation.
- `DELIB-2521` — owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (S376), the governing freshness spec.

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03)** — glossary-review disposition for the `requirement` term: "Fold into WI-3506 (all 3 files)" — re-point the phantom to `GOV-SPEC-CAPTURE-TRANSPARENCY-001` across all three citing rule files via the bridge protocol + narrative packets. This is the owner-decision authority for the protected-narrative edits (no PAUTH; per-file narrative-approval packets carry the per-artifact approval).

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirements are
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (rule citations must resolve to live MemBase
specs) and WI-3506's documented decision path (b). No new specification is
required; this corrects a citation to an existing live spec.

## Spec-Derived Verification Plan

| Specification / Finding | Spec-to-test mapping | Command | Expected |
|---|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | new `test_no_phantom_spec_citation.py` asserts `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` is absent from the 3 rule files and `GOV-SPEC-CAPTURE-TRANSPARENCY-001` is present | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_no_phantom_spec_citation.py -q --no-header -p no:cacheprovider` | PASS |
| `GOV-SPEC-CAPTURE-TRANSPARENCY-001` exists (not another phantom) | confirm the replacement resolves in MemBase | `gt spec list` filtered for the id (or `current_specifications` read) | present |
| `GOV-ARTIFACT-APPROVAL-001` | narrative-approval evidence for the 3 edited rule files | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/prime-builder-role.md .claude/rules/operating-model.md --json` | `status: pass` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | lint + format on the new test | `python -m ruff check` / `ruff format --check` | clean |

## Risk / Rollback

Low: a one-token citation correction in three protected rule files (sentence
meaning preserved) + a regression test. Each protected edit is packet-gated and
independently auditable. Rollback is a single-commit revert. No runtime/behavior
change.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-wi-3506-phantom-spec-citation-repoint` document list in `bridge/INDEX.md`;
append-only — no prior version is deleted or rewritten. `bridge/INDEX.md` remains
the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs` — governance citation correction in rule files + a regression test;
no code-capability change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
