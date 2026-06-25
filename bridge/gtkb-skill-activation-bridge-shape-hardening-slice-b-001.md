NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 19fc5123-fb79-4bd5-8f5c-fdcfd6ecb153
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; skill-activation slice B

bridge_kind: prime_proposal
Document: gtkb-skill-activation-bridge-shape-hardening-slice-b
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-ACTIVATION-SLICE-B-BOUNDED-IMPLEMENTATION-2026-06-25
Work Item: WI-4809
Owner Decision: DELIB-20265889
Umbrella: bridge/gtkb-skill-activation-enforcement-umbrella-002 (GO; DELIB-20265883)
target_paths: ["scripts/proposal_target_paths_coverage_preflight.py", "scripts/bridge_proposal_duplicate_thread_guard.py", "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py", "platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Implementation Proposal - Skill-Activation Slice B: Bridge-Shape Hardening (B#2 delta + B#3)

## Summary

First implemented slice of `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT` (owner-fixed
first slice = bridge-shape hardening, B). It makes the most expensive recurring
bridge-proposal-shape failure classes mechanically detectable, advisory-first, via
two deterministic preflights/guards:

- **Deliverable 1 - B#2 delta (WI-4809):** extend the existing
  `scripts/proposal_target_paths_coverage_preflight.py` to also surface
  **prose-file-claim** and **integration-surface** paths that are not covered by a
  proposal's declared `target_paths`. The preflight already compares declared
  `target_paths` against pytest-command paths and generator-map outputs; this adds
  the two coverage dimensions the umbrella's B#2 named that the current preflight
  does not yet check.
- **Deliverable 2 - B#3 net-new (WI-4573):** add
  `scripts/bridge_proposal_duplicate_thread_guard.py`, a pre-filing guard that warns
  when the declared `Work Item:` already has a non-terminal bridge thread under a
  **different slug** (the duplicate-live-thread failure class that produced two
  prior owner-AUQ reconciliations per WI-4573).

Both are advisory-first (exit-0 advisory by default; an opt-in `--strict` non-zero
exit mirrors the existing coverage preflight's `EXIT_STRICT_GAPS = 5`). No hard
gate is introduced; per the umbrella and `DELIB-20265883`, any hard-gate conversion
is a separate future owner AUQ.

## Reconciliation With Canonical State (why this slice is small)

Due-diligence against live source corrected the umbrella's framing (it was authored
~24h earlier against a staler view):

- **B#1 is already shipped** - `gt bridge propose` deterministic CLI is implemented
  in `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` (WI-3318 resolved;
  source bridge `gtkb-gt-bridge-propose-deterministic-cli` VERIFIED). Not in scope.
- **B#2 is ~70% built** - `scripts/proposal_target_paths_coverage_preflight.py`
  already does the target_paths-vs-command/generator comparison. This proposal adds
  only the missing prose-claim + integration-surface dimensions (an extension, not a
  rebuild).
- **B#3 is genuinely net-new** - distinct from the existing
  `scripts/bridge_proposal_wi_id_collision_check.py`, which flags
  cited-ID-vs-declared-WI collisions *inside one proposal*; B#3 instead detects the
  same WI carrying a live thread under a *different slug across the bridge*.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised formal requirement is needed
before implementation. The work is advisory-first deterministic tooling that
mechanically enforces existing bridge-proposal-shape requirements; it creates no new
governance and mutates no formal artifact. Governing requirements are linked below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol authority; this proposal follows
  the numbered bridge lifecycle).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (this proposal cites all
  relevant governing specs).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (the verification plan below maps
  spec-derived tests to each deliverable).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (slice authorized by the bounded
  PAUTH cited in the header; this spec is included in that PAUTH).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (project carries linked specs).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (Project / Work Item / Project
  Authorization triple present in the header).
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (two-layer write-time +
  review-time defense; both deliverables are review-time mechanical enforcement of
  bridge-proposal-shape requirements).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (repetitive AI plumbing is a defect;
  both guards are deterministic services that move recurring manual scope/duplication
  checks off the session).
- `DELIB-20265883` (umbrella program-scoping owner decision) and `DELIB-20265889`
  (this slice's owner authorization).
- `.claude/rules/file-bridge-protocol.md` section "Mandatory Implementation-Start
  Authorization Metadata" (target_paths semantics this slice audits).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; this slice preserves the umbrella,
  owner decision, project record, work items, and this proposal as durable linked
  artifacts and triggers no untracked-artifact lifecycle transition).

## Owner Decisions / Input

- `DELIB-20265889` (owner_conversation, outcome=owner_decision): the AskUserQuestion
  chain this session authorizing slice B.
  - Populate the project with reconciled net-new slices (AUQ answer).
  - Draft the first slice (B) implementation proposal (AUQ answer).
  - Scope = B#2 delta + B#3, one proposal (AUQ answer).
  - Approve the bounded per-slice PAUTH (WI-4809 + WI-4573; classes source +
    test_addition; advisory-first) (AUQ answer: "Approve PAUTH - proceed").
- `DELIB-20265883` (owner_conversation): the umbrella-scoping AUQ (full enforcement
  program; B first; advisory-first posture).

No further owner decision blocks implementation. Any future conversion of either
guard to a hard gate is a separate owner AUQ per the umbrella.

## Prior Deliberations

- `DELIB-20265883` - umbrella program-scoping owner decision (this slice's parent).
- `DELIB-20265889` - this slice's owner authorization.
- `bridge/gtkb-skill-activation-enforcement-umbrella-001.md` / `-002.md` (GO) - the
  scoping umbrella naming B#2/B#3 as first-slice components.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  - source advisory (opportunities #6 target-paths auditor, #10 stale/duplicate-thread
  check).
- `DELIB-0048` (Bridge Mechanism Hardening, 2026-03) - nearest prior art on bridge
  guard hardening; predates the target_paths/duplicate-thread surfaces and does not
  cover them.
- _No prior deliberations: the prose-file-claim coverage dimension and the
  cross-thread duplicate-live-thread guard contract have no specific DA precedent;
  this proposal is the first to scope them._

## Deliverable 1 - B#2 delta (WI-4809)

Extend `scripts/proposal_target_paths_coverage_preflight.py`:

1. Add `extract_prose_file_claims(markdown)` - collect repository-relative file paths
   named in proposal **prose** (outside fenced/command blocks) that look like source,
   test, config, or doc paths (e.g. `scripts/...py`, `platform_tests/...py`,
   `config/...toml`, `*.md`), reusing the module's existing path-normalization
   (`normalize_relative_path`) and out-of-root handling.
2. Add an integration-surface dimension: when a prose-claimed or command-implied path
   is a known integration surface (hook registration files, `.claude/settings.json`,
   `.codex/hooks.json`, registry TOMLs) it is reported under a distinct
   `implied_integration_paths` result key.
3. Extend `run_preflight(...)` result with `implied_prose_paths`,
   `uncovered_prose_paths`, `implied_integration_paths`, `uncovered_integration_paths`,
   folded into the existing `verdict`/`message` so uncovered prose/integration paths
   surface alongside the current verification/generator gaps. Default advisory
   (exit 0); `--strict` returns `EXIT_STRICT_GAPS` when any uncovered set is non-empty,
   matching current behavior.

Backward compatibility: existing result keys and the `--strict` semantics are
preserved; the new keys are additive.

## Deliverable 2 - B#3 net-new (WI-4573)

Add `scripts/bridge_proposal_duplicate_thread_guard.py` (advisory):

1. Parse the declared `Work Item:` from a proposal body (reuse the
   `Work Item:` regex contract from `scripts/bridge_proposal_wi_id_collision_check.py`
   for consistency).
2. Query live bridge state for **non-terminal** threads citing the same Work Item via
   `groundtruth_kb.bridge.read_commands` (the API backing `gt bridge threads --wi`),
   filtering to threads whose latest status is in the actionable/non-terminal set
   (NEW / REVISED / GO / NO-GO) and whose slug differs from the proposal's own slug.
   It MUST read TAFE/dispatcher bridge state, not `bridge/INDEX.md` (the 2026-06-15
   cutover retired aggregate-queue authority; WI-4573's original "scan INDEX.md"
   description predates that cutover and is corrected here).
3. Emit an advisory result (JSON + markdown) listing any duplicate live threads;
   default exit 0; `--strict` returns a non-zero exit when a duplicate is found.

## Multi-Work-Item Note (intentional)

This single slice-B proposal implements two work items, both covered by the cited
PAUTH: WI-4809 (Deliverable 1) and WI-4573 (Deliverable 2). The header declares
`Work Item: WI-4809` (primary). The existing single-WI
`scripts/bridge_proposal_wi_id_collision_check.py` uses an exact
`cited_id == declared` comparison, so it would advisory-flag the WI-4573 citation as
a "collision." That is a **false positive of the single-WI assumption**, not an error
in this proposal - and is itself a data point for a future B-family refinement
(multi-WI proposal modeling). It is disclosed here so review does not misread it.

## Spec-Derived Verification Plan

| Spec / requirement | Deliverable | Test (spec-derived) |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, B#2 coverage | D1 | extend `platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py`: prose-claimed uncovered path is reported; prose-claimed covered path is not; integration surface is classified; additive keys present; `--strict` exits 5 on uncovered prose/integration gap; backward-compat keys unchanged |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` review-time enforcement, B#3 | D2 | new `platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py`: duplicate live thread under a different slug is detected; terminal (VERIFIED/WITHDRAWN/DEFERRED) threads are NOT flagged; same-slug self is excluded; no-duplicate case is clean; `--strict` non-zero on duplicate; reads TAFE state (fixture), not INDEX.md |

Execution commands:

```
.venv/Scripts/python -m pytest platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py -q --tb=short
.venv/Scripts/python -m ruff check scripts/proposal_target_paths_coverage_preflight.py scripts/bridge_proposal_duplicate_thread_guard.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py
.venv/Scripts/python -m ruff format --check scripts/proposal_target_paths_coverage_preflight.py scripts/bridge_proposal_duplicate_thread_guard.py platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py
```

## Target Path Rationale

- `scripts/proposal_target_paths_coverage_preflight.py` - B#2 delta (extend existing).
- `scripts/bridge_proposal_duplicate_thread_guard.py` - B#3 net-new module.
- `platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py` - B#2 tests
  (extend existing).
- `platform_tests/scripts/test_bridge_proposal_duplicate_thread_guard.py` - B#3 tests
  (new).

No `.claude/` helper-wiring is in scope: both guards ship as standalone preflight
scripts matching the existing `proposal_target_paths_coverage_preflight.py` pattern
(Prime/Codex/LO invoke them; auto-wiring into the propose helper is a separate
follow-on). All paths are tracked, in-root, and within the PAUTH's
`source` + `test_addition` classes.

## Risk / Rollback

- **Risk:** B#2 prose-path extraction over-reports (false positives on incidental path
  mentions). Mitigation: restrict prose extraction to path-shaped tokens with known
  repo-relative prefixes/extensions; advisory-only (no hard gate); tests assert
  non-path prose does not trigger.
- **Risk:** B#3 reads stale bridge state. Mitigation: read TAFE/dispatcher state
  through the canonical `read_commands` API (same source as `gt bridge threads`); no
  aggregate-queue dependency.
- **Rollback:** both deliverables are additive standalone/extension code with no
  hard-gate wiring; reverting the four files fully removes the slice with no residual
  behavior change.

## Requested Loyal Opposition Review

Please review whether (1) the B#2 delta is correctly scoped as an additive extension
of the existing coverage preflight without breaking its current keys/`--strict`
semantics; (2) the B#3 guard correctly reads TAFE/dispatcher state (not INDEX.md) and
correctly excludes terminal threads and the same-slug self; (3) the spec-derived test
plan covers each deliverable's acceptance behavior; and (4) the multi-WI disclosure is
an acceptable handling of the single-WI collision-checker false positive. A `GO`
authorizes implementation within the four declared `target_paths`. A `NO-GO` should
identify a scope, spec-linkage, or test-coverage gap.
