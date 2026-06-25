NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bf970d5e-9dda-4a61-bd98-41fac87d2f68
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; skill-activation WI-4810 router slice

bridge_kind: prime_proposal
Document: gtkb-skill-usage-router-slice
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-ACTIVATION-WI-4810-ROUTER-SLICE-BOUNDED-IMPLEMENTATION-2026-06-25
Work Item: WI-4810
Owner Decision: DELIB-20265895
Umbrella: bridge/gtkb-skill-activation-enforcement-umbrella-002 (GO; DELIB-20265883)
target_paths: ["scripts/skill_usage_router.py", "config/agent-control/skill-scenarios.toml", "groundtruth-kb/src/groundtruth_kb/cli_skills.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_skill_usage_router.py"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Implementation Proposal — Skill-Usage Router (WI-4810, advisory/report-only first slice)

## Summary

Second implemented slice of `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT` (slice B
bridge-shape hardening is VERIFIED + resolved). This slice builds the advisory's
Opportunity #1 / "Suggested First Slice": a **deterministic, report-only
skill-usage router** that answers "which skills should this scenario use?" from a
static table, replacing per-turn human memory. It is governed by the owner-approved
`SPEC-SKILL-USAGE-ROUTER-001`.

Four deliverables, all advisory/report-only (no hard gate; per the umbrella and
`DELIB-20265883` any hard-gate conversion is a separate future owner AUQ):

- **D1 — Router engine + table:** `scripts/skill_usage_router.py` (deterministic; no
  LLM) reading a tracked TOML table `config/agent-control/skill-scenarios.toml` that
  maps each of 6 scenarios to required skills, recommended skills, and a rationale.
- **D2 — CLI:** `gt skills suggest` (new `cli_skills.py` registered in `cli.py`)
  emitting human-readable + `--json` output. `gt skills check` is OUT OF SCOPE
  (depends on WI-4814 report self-disclosure).
- **D3 — Startup advisory line:** a report-only suggested-skills line in the startup
  payload (`scripts/session_self_initialization.py`) for the resolved role, fail-safe
  (router error → omit line, never break startup), preserving the existing payload
  contract and rendering identically across Claude / Codex / Antigravity.
- **D4 — Spec-derived tests:** `platform_tests/scripts/test_skill_usage_router.py`
  covering the router, the CLI, and the startup integration against the spec's
  acceptance criteria.

## Requirement Sufficiency

**Existing requirements sufficient.** `SPEC-SKILL-USAGE-ROUTER-001` (requirement,
status `specified`, owner-approved this session) governs the router's deterministic,
report-only contract and supplies the AC1–AC7 acceptance criteria the tests derive
from. No new or revised formal requirement is needed before implementation; this
proposal creates no governance and mutates no formal artifact.

## Specification Links

- `SPEC-SKILL-USAGE-ROUTER-001` — **governing implementation spec** (R1–R8 + AC1–AC7);
  the verification plan below maps a test to each acceptance criterion.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal follows
  the numbered, append-only bridge lifecycle.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` — project carries linked specs; this
  slice links its governing spec.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all
  relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps
  spec-derived tests to each acceptance criterion.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` — advisory adopt-conversion; owner grilling
  evidence (`DELIB-20265895`) is recorded in Owner Decisions / Input below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — slice authorized by the bounded
  PAUTH cited in the header (this spec is included in that PAUTH).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item / Project
  Authorization triple present in the header.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — advisory: the router is
  a review/runtime advisory surface; it is report-only this slice (no write-time gate).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the router is a deterministic service
  that moves recurring "which skill?" reasoning off the session.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — this slice preserves the umbrella,
  the owner grilling/spec-approval decisions, `SPEC-SKILL-USAGE-ROUTER-001`, the project
  record, WI-4810, and this proposal as durable linked artifacts, and triggers no
  untracked-artifact lifecycle transition.
- `DELIB-20265883` (umbrella program-scoping owner decision) and `DELIB-20265895` (this
  slice's grilling + design owner decision).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  — source advisory (Opportunity #1 / Suggested First Slice).

## Owner Decisions / Input

This slice converts an LO advisory, so per `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001`
the owner grilling evidence is recorded here.

- `DELIB-20265895` (owner_conversation, outcome=owner_decision; AUQ
  `AUQ-WI4810-GRILLING-2026-06-25`) — the design grilling this session:
  - **Scenario-table home = standalone TOML** (`config/agent-control/skill-scenarios.toml`).
  - **Integration surface = CLI + report-only startup advisory line** (both report-only).
  - **Scenario coverage = 6 high-value scenarios** (the advisory's Suggested First Slice set).
  - Prime-scoped (disclosed): **CLI verb = `suggest` only**; `check` deferred to its
    WI-4814 report-self-disclosure dependency.
- `AUQ-WI4810-SPEC-APPROVAL-2026-06-25` (formal-artifact-approval for
  `SPEC-SKILL-USAGE-ROUTER-001`, captured in
  `.groundtruth/formal-artifact-approvals/2026-06-25-SPEC-SKILL-USAGE-ROUTER-001.json`)
  — owner answer "Approve & record … move to PAUTH (WI-4810, classes source + config +
  test_addition) and file the NEW bridge proposal." This authorizes the PAUTH scope and
  the filing of this proposal.
- `DELIB-20265883` (owner_conversation) — the umbrella-scoping AUQ (full enforcement
  program; advisory-first posture; bridge-shape hardening first slice).

No further owner decision blocks implementation. Any future conversion of the router to
a hard gate is a separate owner AUQ per the umbrella.

## Prior Deliberations

- `DELIB-20265883` — umbrella program-scoping owner decision (this slice's parent).
- `DELIB-20265895` — this slice's grilling + design owner decision.
- `bridge/gtkb-skill-activation-enforcement-umbrella-001.md` / `-002.md` (GO) — the
  scoping umbrella; `-002` carries forward `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` and
  the harness-parity risk note this slice addresses.
- `bridge/gtkb-skill-activation-bridge-shape-hardening-slice-b-004.md` (VERIFIED) —
  sibling first slice (bridge-shape hardening); establishes the project's advisory-first
  deterministic-tooling pattern this slice follows.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  — source advisory; F1 + Opportunity #1 + "Suggested First Slice" name this router and
  its 6-scenario starter table.
- A pre-filing `search_deliberations()` for the router topic returned no prior decision
  that pre-decides or conflicts with this design (closest hits: the umbrella scoping
  `DELIB-20265883` and disposition-profile `DELIB-20265892`, neither of which scopes a
  skill-usage router).

## Deliverable 1 — Router engine + scenario table

Add `config/agent-control/skill-scenarios.toml` (tracked, versioned) with a `[scenarios.<key>]`
table per scenario carrying `title`, `required` (list of skill names), `recommended`
(list), and `rationale` (string). The 6 keys (SPEC R3): `lo_bridge_review`,
`lo_verify_report`, `advisory_report`, `harness_surface_change`, `session_wrap`,
`release_readiness`. Seed content derives from the advisory's F3 consistent-use table.

Add `scripts/skill_usage_router.py` (SPEC R1, R4, R5):
1. `load_table(path)` — parse the TOML (stdlib `tomllib`); validate each scenario has
   `required`/`recommended`/`rationale`; deterministic, no network/LLM.
2. `suggest(*, scenario=None, role=None, changed_paths=None, bridge_status=None,
   bridge_kind=None, target_files=None, report_type=None, table=...)` — an explicit
   `scenario` selects directly; otherwise a deterministic signal-matcher maps available
   inputs to at most one scenario key. Returns a result with `scenario`, `required`,
   `recommended`, `rationale`, `matched_by`.
3. Unknown/unmatched → empty advisory result (no scenario); never raises for "no match".

## Deliverable 2 — `gt skills suggest` CLI

Add `groundtruth-kb/src/groundtruth_kb/cli_skills.py` exposing a `skills` group with a
`suggest` command (SPEC R6); options mirror the router inputs (`--scenario`, `--role`,
`--changed-path` (repeatable), `--bridge-status`, `--bridge-kind`, `--target-file`
(repeatable), `--report-type`, `--json`). Register the group in
`groundtruth-kb/src/groundtruth_kb/cli.py` alongside existing groups. Exit 0 always
(report-only, SPEC R5); human-readable default, `--json` machine output. No `check`
subcommand this slice.

## Deliverable 3 — Report-only startup advisory line

In `scripts/session_self_initialization.py`, add a report-only "Suggested skills"
advisory line derived from the router for the resolved role + work subject (SPEC R7).
Constraints, asserted by tests:
- It MUST NOT alter existing startup routing facts or the payload contract (additive
  line only).
- It MUST fail safe: any router/table error is swallowed and the line is omitted; startup
  still exits 0.
- It is harness-agnostic text in the shared payload, so it renders identically across
  Claude / Codex / Antigravity (addresses the umbrella GO `-002` harness-parity risk).

## Deliverable 4 — Spec-derived tests

Add `platform_tests/scripts/test_skill_usage_router.py` covering the router engine, the
CLI, and the startup integration (see the verification plan). The startup-integration
test invokes `session_self_initialization.main(...)` and asserts the advisory line is
present and that a simulated router failure omits the line while startup still exits 0 —
kept in this new file so the unrelated red migration test currently in
`test_session_self_initialization.py` is not entangled.

## Spec-Derived Verification Plan

| Spec acceptance criterion | Deliverable | Test (spec-derived) |
|---|---|---|
| `SPEC-SKILL-USAGE-ROUTER-001` AC1 | D1/D2 | `gt skills suggest --scenario lo_bridge_review` exits 0; required ⊇ {gtkb-bridge, proposal-review}; recommended ⊇ {check-deliberations, lo-opportunity-radar} |
| AC2 | D1 | each of the 6 scenarios returns its table-defined required/recommended/rationale |
| AC3 | D1/D2 | unrecognized/empty inputs → empty advisory, exit 0 (report-only) |
| AC4 | D1 | router loads the table from `config/agent-control/skill-scenarios.toml`; a temp-table edit changes output with no router code change |
| AC5 | D3 | startup payload includes the advisory line for a resolved role; existing startup routing-fact assertions unchanged; a monkeypatched router failure omits the line and `main(...)` still returns 0 |
| AC6 | D1 | router performs no network/LLM call; identical inputs → identical output (determinism) |
| AC7 | D1/D2 | no file under `.claude/skills/` or `.codex/skills/` is read-mutated by router operation (content-coupling guard) |

Execution commands (run against changed files before the post-implementation report):

```
.venv/Scripts/python -m pytest platform_tests/scripts/test_skill_usage_router.py -q --tb=short
.venv/Scripts/python -m ruff check scripts/skill_usage_router.py groundtruth-kb/src/groundtruth_kb/cli_skills.py platform_tests/scripts/test_skill_usage_router.py
.venv/Scripts/python -m ruff format --check scripts/skill_usage_router.py groundtruth-kb/src/groundtruth_kb/cli_skills.py platform_tests/scripts/test_skill_usage_router.py
```

(The session_self_initialization edit is exercised by the AC5 startup-integration test;
its existing suite is re-run to confirm no regression beyond the pre-existing unrelated
red migration test.)

## Target Path Rationale

- `scripts/skill_usage_router.py` — D1 router engine (new source).
- `config/agent-control/skill-scenarios.toml` — D1 scenario table (new config; the
  owner-chosen tracked-surface home).
- `groundtruth-kb/src/groundtruth_kb/cli_skills.py` — D2 `gt skills` group (new source).
- `groundtruth-kb/src/groundtruth_kb/cli.py` — D2 register the skills group (source edit).
- `scripts/session_self_initialization.py` — D3 report-only startup advisory line
  (source edit).
- `platform_tests/scripts/test_skill_usage_router.py` — D4 spec-derived tests (new test).

All paths are tracked, in-root, and within the PAUTH's `source` + `config` +
`test_addition` classes. No skill CONTENT (`.claude/skills/*/SKILL.md`, `.codex`
adapters) is modified (SPEC R8; preserves the `PROJECT-GTKB-SKILL-MODERNIZATION`
boundary).

## Risk / Rollback

- **Risk:** startup-line edit destabilizes the heavily-tested startup payload (which
  currently carries an unrelated red role-migration test). **Mitigation:** additive
  fail-safe line only (router error → omit); AC5 asserts existing routing-fact
  assertions are unchanged and startup still exits 0; the new assertion lives in a
  separate test file.
- **Risk:** signal-matcher over-matches a scenario from ambiguous inputs.
  **Mitigation:** deterministic, conservative matcher; an explicit `--scenario` always
  wins; no match → empty advisory (report-only, never blocks).
- **Risk:** harness-parity drift in the advisory line. **Mitigation:** the line is
  harness-agnostic text in the shared startup payload; no per-harness branch.
- **Rollback:** all deliverables are additive (one source edit to `cli.py` register-line
  and one additive block in `session_self_initialization.py`); reverting the six paths
  fully removes the slice with no residual behavior change (report-only, no hard gate).

## Recommended Commit Type

`feat:` — net-new capability surface (router module, scenario-table config, `gt skills`
CLI command, report-only startup integration, spec-derived tests).

## Requested Loyal Opposition Review

Please review whether (1) the router is genuinely deterministic and report-only per SPEC
R1/R5 (no LLM, never blocks, unknown→empty/exit 0); (2) the standalone TOML table home +
6-scenario coverage match the owner grilling (`DELIB-20265895`) and the spec; (3) the
startup-line integration is additive + fail-safe and preserves the existing payload
contract and harness parity (SPEC R7); (4) the spec-derived test plan covers AC1–AC7;
and (5) the `target_paths` are complete and correctly scoped to the PAUTH classes. A `GO`
authorizes implementation within the six declared `target_paths`. A `NO-GO` should
identify a scope, spec-linkage, determinism, or test-coverage gap.
