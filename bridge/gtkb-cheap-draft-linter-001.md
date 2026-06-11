NEW

bridge_kind: prime_proposal
Document: gtkb-cheap-draft-linter
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4437
Project Authorization: PAUTH-DRAFTLINTER-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["scripts/draft_lint.py", "platform_tests/scripts/test_draft_lint.py"]

---

# Cheap-model proposal draft-linter — deterministic QA gate for Qwen-drafted bodies

WI-4437 of PROJECT-FABLE-INVESTIGATION (campaign-support tooling).

## Summary

The validated cheap-drafting workflow has a local model (Qwen) draft a proposal
body, which Opus then finalizes + files. To keep that path from degrading quality,
this proposal adds a **read-only deterministic linter** run on every cheap-drafted
body **before Opus finalization**. It catches the *mechanical* cheap-model failure
modes (hallucinated paths/spec-ids, missing structure, placeholder text, rubber-stamp
verification) at ~0 tokens, so neither Opus review nor a Codex review cycle is spent
on them. This is the GT-KB-correct way to make cheap-model output safe: **mechanical
verification, not AI-trusting-AI** (`DELIB-S312` deterministic-services), and it
augments — never replaces — Opus finalization and Codex Loyal Opposition review.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from specs.
- `GOV-STANDING-BACKLOG-001` — WI-4437 is the governed backlog authority.
- `SPEC-1662` (GOV-18 assertion quality) — the linter enforces that a draft's
  verification section carries at least one concrete (non-rubber-stamp) assertion.

Governing principle (non-spec): `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` —
repetitive mechanical checking belongs in a deterministic service, not a session.

## Prior Deliberations

- `DELIB-DRAFTLINTER-20260610` — owner agreement to build the linter + the layered
  QA strategy and no-rubber-stamp / escalation rules.
- `bridge/gtkb-fable-investigation-advisory-001.md` — campaign charter (the cheap
  drafting workflow this gate protects).
- The validated cheap-drafting workflow + recipe is recorded in
  `memory/fable-investigation-campaign.md` (2026-06-10 FAB-08/HYG-053 validation).
- _No prior bridge thread exists for a proposal-draft linter._

## Owner Decisions / Input

The owner asked (2026-06-10) how to ensure no quality degradation when drafting with
Qwen. After Prime presented the layered QA strategy, the owner **agreed** to build the
deterministic draft-linter first as the top measure (recorded in
`DELIB-DRAFTLINTER-20260610`). The linter does NOT change the requirement that every
proposal still passes the existing preflights and an independent Codex `GO`.

## Requirement Sufficiency

**Existing requirements sufficient.** The linter operationalizes `SPEC-1662` (GOV-18
assertion quality) and `DELIB-S312` (deterministic services) for the cheap-drafting
workflow; it introduces no new requirement. It reuses existing phantom-spec logic for
the spec-id check.

## Scope and Boundaries

In scope: a standalone `scripts/draft_lint.py` + its test. The linter is **advisory
to the author** (it gates Opus's *finalization*, not the bridge): it never writes,
never mutates MemBase, and is invoked manually in the drafting workflow.

Out of scope: it does NOT replace or weaken any existing gate, preflight, or Codex
review; it is NOT wired as a blocking bridge hook in this slice (it is an author-side
pre-finalize check). Wiring it into a hook is a possible follow-on once calibrated.

## Proposed Implementation

`scripts/draft_lint.py` — takes a draft body (file or stdin) + the cluster's frozen
HYG ids, and runs these deterministic checks, emitting PASS/FAIL JSON with per-check
findings (no secret content printed):

1. **Cited-path resolution** — every repo-style path token in the draft resolves
   under `E:\GT-KB` (`Test-Path`/`os.path.exists`); unresolved paths → FAIL.
2. **HYG-id match** — every `HYG-NNN` cited is in the cluster's frozen set; stray
   ids → FAIL (guards against the cheap model importing the wrong finding).
3. **Phantom-spec** — every `SPEC-/GOV-/ADR-/DCL-/PB-/REQ-` id cited exists in the
   live `specifications` table (reuse the existing phantom-spec query) → FAIL on miss.
4. **Required-section presence** — Summary, Scope, Proposed Implementation,
   verification, Acceptance, Risk all present → FAIL on missing.
5. **Placeholder detection** — `tbd|todo|n/a|none|tk|<fill>|xxx` etc. → FAIL.
6. **Assertion floor (GOV-18)** — the verification section contains at least one
   concrete assertion (a check that asserts a measurable PASS/FAIL, not generic
   prose) → WARN/FAIL on rubber-stamp.

`platform_tests/scripts/test_draft_lint.py` — fixtures exercising each check's PASS
and FAIL branch (a clean draft passes; a draft with a hallucinated path, a stray HYG
id, a phantom spec, a missing section, a placeholder, and a rubber-stamp verification
each FAIL the corresponding check).

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `SPEC-1662` (GOV-18 assertion quality) | a rubber-stamp verification section FAILs check 6; a concrete one passes |
| `DELIB-S312` (deterministic, read-only) | AST/behavioral test asserts the linter performs no writes/MemBase mutation (read-only) |
| phantom-spec correctness | a draft citing a non-existent spec id FAILs check 3; a real id passes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_draft_lint.py` + `ruff check`/`format --check` |

## Acceptance Criteria

1. `scripts/draft_lint.py` runs the 6 checks and emits PASS/FAIL JSON; read-only.
2. The test exercises PASS + FAIL for each check; all pass; ruff-clean.
3. Running it on the validated FAB-08 Qwen draft produces a clear, actionable report.

## Risk and Rollback

- **Risk:** false positives (a legitimate path/id flagged) → checks are conservative
  and report *which* token failed so the author adjudicates; the linter is advisory
  to Opus finalization, not a hard bridge block in this slice.
- **Rollback:** delete the script + test; the workflow reverts to manual Opus QA.

## Recommended Implementation Routing

**NOT a cheap-model candidate** — this is the verifier of cheap-model output; building
it with the cheap model would be circular. Reserve for Claude/Codex-supervised
implementation. (Self-referential note: per the protocol, this QA tool still goes
through Codex `GO` like everything else.)

## Recommended Commit Type

`feat:` — net-new deterministic QA service + test.
