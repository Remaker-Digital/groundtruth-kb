NEW

# gtkb-verified-finalization-validation-hardening — Fail-closed VERIFIED finalization validation (placeholders, failed-preflight evidence, predecessor chain)

bridge_kind: prime_proposal
Document: gtkb-verified-finalization-validation-hardening
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 6e9eb87a-50f6-492f-b3fe-b230cb088350
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; Prime Builder role (::init gtkb pb); MAY29-HYGIENE retirement drive

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4773

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The VERIFIED finalization helper (`finalize_verified_commit` + `validate_verified_body`
in `.claude/skills/verify/helpers/write_verdict.py`, mirrored byte-for-behavior in the
`.codex` and `.cursor` copies) commits a terminal `VERIFIED` verdict + the verified
path set as one transaction. Its current evidence floor (`validate_verified_body`)
checks only: first-token == `VERIFIED`, a Recommended-commit-type line, a
`## Spec-to-Test Mapping` section with at least one `Executed=yes` row, and a
`## Commands Executed` section. It does **not** fail closed on three observed defect
modes that let an *invalid* VERIFIED verdict become terminal:

1. **Unresolved helper placeholders** — a verdict body containing a literal
   placeholder token (e.g. `PLACEHOLDER_DELIBERATIONS`) the author never replaced
   passes validation today (observed in commit `e68da4d8e`, bridge
   `gtkb-ruff-format-check-pre-commit-drift-clear-008`).
2. **Failed embedded preflight evidence** — a verdict body that embeds candidate
   Applicability/Clause preflight evidence with `preflight_passed: false` (or a
   non-empty `missing_required_specs`) is committed as if verification passed.
3. **Out-of-root scratch paths in evidence** — embedded preflight evidence blocks
   carrying a harness-local user-profile scratch path (an `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
   / `CLAUSE-IN-ROOT` violation) ride along into the terminal verdict.

Separately, `finalize_verified_commit` stages only `include_paths` + the new verdict
and never verifies that the thread's **predecessor bridge chain**
(`<slug>-001.md` through `<slug>-NNN-1.md`) is git-tracked and committed. A terminal
`VERIFIED` can therefore land while predecessors are untracked/staged-outside the
commit (observed: `gtkb-ruff-format-check-pre-commit-drift-clear-008` VERIFIED while
`-005`/`-006` untracked/staged; `gtkb-wi4767-dispatch-config-file-edit-guard-004`
VERIFIED while `-001`/`-002`/`-003` untracked).

This proposal extends the evidence floor and the finalization transaction to fail
closed on all four conditions, applied identically across the three tracked helper
copies for harness parity (the WI-4750 parity lesson — Codex/Cursor finalization
must not diverge from Claude). It is the unified fix for the same-defect-class
cluster **WI-4773** (primary, P1 — prevent invalid VERIFIED finalization),
**WI-4772** (P2 — omit predecessor files / failed preflight evidence), and
**WI-4775** (P2 — leave prior chain files untracked); all three are covered by the
same `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24`. WI-4772 and
WI-4775 are resolved against this thread's VERIFIED outcome (their acceptance
criteria are a strict subset of WI-4773's).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — owns the *Mandatory VERIFIED Commit-Finalization
  Gate*; this proposal strengthens that gate's evidence floor and same-transaction
  staging invariant, so the governing spec is directly implicated.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the fix adds spec-derived
  regression coverage that asserts each defect mode now fails closed; the new test
  is the spec-to-test mapping for this clause.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — defect mode (3) (out-of-root scratch
  paths in embedded evidence) is a `CLAUSE-IN-ROOT` violation; the validator change
  enforces in-root evidence while preserving the known disclosure-span prose
  exemption (no false-positive on prose mentions).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all
  relevant governing specs; satisfied by the applicability preflight.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/work-item
  linkage metadata is present in the header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation is authorized by
  the cited PAUTH covering the cluster work items.
- `GOV-STANDING-BACKLOG-001` — the cluster work items are active MAY29-HYGIENE
  backlog members; their terminal resolution follows this thread's VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the work preserves durable
  bridge audit artifacts (full chain committed) as the artifact-oriented stance
  requires.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — finalization integrity keeps
  the bridge thread a trustworthy durable artifact network.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — VERIFIED is the lifecycle
  transition this gate protects; the fix keeps the transition evidence-backed.

## Prior Deliberations

- `DELIB-WI4723-OWNER-PROCEED-20260621` — owner directive to proceed with WI-4723,
  the VERIFIED finalization-gate **retry** hardening (index.lock retry) on the same
  `finalize_verified_commit` function. This proposal is adjacent but distinct: it
  adds **validation** hardening (evidence floor + predecessor-chain inclusion) to
  the same function, not retry behavior.
- Deliberation search query `"VERIFIED finalization predecessor bridge chain
  untracked placeholder failed preflight evidence verdict"` (2026-06-24) returned
  no prior decision specific to this finalization-**validation** defect class (top
  matches were unrelated LO reviews at semantic score < 0.66). No previously
  rejected approach is being revisited.
- Originating evidence: the LO FLOATER findings of 2026-06-23 that opened the
  cluster work items. Sibling systemic finding captured as WI-4802 (reconciler
  over-blocks on WITHDRAWN/ADVISORY) — out of scope here.

## Owner Decisions / Input

Authorized by owner AskUserQuestion on 2026-06-24 (option "Authorize all 6"),
captured as `DELIB-20265880`, which created
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-OUT-OF-SNAPSHOT-6-2026-06-24` covering the six
out-of-snapshot member work items (including this cluster) for bounded
implementation (allowed mutation classes: source, test_addition, hook_upgrade,
cli_extension, scaffold_update). No further owner decision is required to proceed
through the bridge protocol; this section records the standing authorization
evidence.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is fully specified by
`GOV-FILE-BRIDGE-AUTHORITY-001` (the VERIFIED Commit-Finalization Gate: a terminal
VERIFIED must not commit invalid/incomplete evidence and must carry its bridge
chain), `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`/`CLAUSE-IN-ROOT`, and the acceptance
criteria of the cluster work items. No new or revised requirement is needed.

## Spec-Derived Verification Plan

New regression test `platform_tests/skills/test_verified_finalization_validation_hardening.py`
exercises the exposed `validate_verified_body` / `finalize_verified_commit`
interface for each defect mode; parity tests assert identical behavior across the
three helper copies.

| Specification | Test / Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (placeholder) | `test_validate_rejects_unresolved_placeholder` | `VerifiedFinalizationError` raised |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (failed preflight) | `test_validate_rejects_embedded_failed_preflight` | raised on `preflight_passed: false` / non-empty `missing_required_specs` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (predecessor chain) | `test_finalize_fails_closed_on_untracked_predecessor_chain` | raised; verdict file cleaned up, nothing committed |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`/`CLAUSE-IN-ROOT` | `test_validate_rejects_out_of_root_scratch_in_evidence` + `test_validate_allows_prose_disclosure_span` | reject embedded evidence path; ALLOW prose disclosure span (no false-positive) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | full test module run | all assertions pass |
| parity (`.claude`/`.codex`/`.cursor`) | `test_three_helper_copies_share_validation_behavior` | identical fail-closed behavior |

Execution command (repo venv for reproducibility):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_verified_finalization_validation_hardening.py -q --no-header
```

Pre-file code-quality gates on changed Python (both, separate):

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <changed.py>
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <changed.py>
```

## Risk / Rollback

- **Risk: over-tightening breaks legitimate VERIFIED finalization.** The most
  likely false-positive is the out-of-root-scratch check mis-firing on legitimate
  prose disclosure spans (the known `CLAUSE-IN-ROOT` report-prose lesson). Mitigated
  by scoping the check to embedded preflight/evidence/code-fence blocks only, with
  an explicit allow-prose regression test. The placeholder and failed-preflight
  checks key on machine tokens (`PLACEHOLDER_*`, `preflight_passed: false`) that
  never legitimately appear in a finalized verdict.
- **Risk: predecessor-chain check blocks a valid finalize where predecessors were
  legitimately committed earlier.** Mitigated by accepting either already-committed
  (git-tracked, not dirty) OR same-transaction-included predecessors — only
  untracked/uncommitted-and-not-included predecessors fail closed.
- **Risk: three-copy drift.** Mitigated by the parity regression test asserting all
  three copies share behavior.
- **Rollback:** single-commit revert of the four target paths restores prior
  behavior; the change is additive validation with no data migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-verified-finalization-validation-hardening`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs broken fail-closed behavior in the VERIFIED finalization gate with
no new capability surface (adds validation + a regression test to existing helpers).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
