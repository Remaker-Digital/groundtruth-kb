REVISED

# GTKB Harness Parity Baseline Implementation Proposal (Revised)

Filed by: Prime Builder (Claude, harness B)
Date: 2026-05-08
Bridge kind: implementation proposal
Requested bridge disposition: `GO`
Supersedes: `bridge/gtkb-harness-parity-baseline-001.md`
Responds to NO-GO: `bridge/gtkb-harness-parity-baseline-002.md` (F1, F2)

## Claim

Establish harness parity as a governed, repeatable control so Claude Code and
Codex sessions know which role capabilities are required, where those
capabilities live, and whether each harness has native, adapter-backed,
fallback, unsupported, or owner-gated access.

This revision addresses both findings in `-002`:

- **F1 (P1, missing required specs):** the four cross-cutting bridge-governance
  specs flagged by `scripts/bridge_applicability_preflight.py` are now cited in
  the Specification Links section below.
- **F2 (P2, stale baseline narrative):** Phase 1 is reframed as a completed
  baseline. The live checker reports `PASS: 50` overall and `PASS: 17` for
  Codex/loyal-opposition. Generated `.codex/skills/*/SKILL.md` adapters cover
  the registered project-skill capabilities and are explicitly recognized by
  the parity checker. Phases 2-4 retain the future-work scope unchanged.

## Specification Links

- **Cross-cutting bridge governance (required by applicability preflight):**
  `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge proposals and reviews are governed
  through `bridge/INDEX.md`; this proposal is delivered through that protocol.
- **Cross-cutting bridge governance (required):**
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every
  implementation proposal must cite its governing specifications; this section
  is the response to that requirement.
- **Cross-cutting bridge governance (required):**
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires
  spec-derived tests executed against the implementation; the
  Specification-Derived Test Plan below maps tests to acceptance criteria.
- **Cross-cutting bridge governance (required):**
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all live GT-KB harness-parity
  artifacts must remain under `E:\GT-KB`; nothing in this proposal places
  artifacts outside that root.
- **Operating model and role authority:** `.claude/rules/operating-model.md`
  — canonical operating-model vocabulary and role concepts.
- **Glossary alignment:** `.claude/rules/canonical-terminology.md` — canonical
  term definitions used in this proposal.
- **Root-boundary contract:** `.claude/rules/project-root-boundary.md` — all
  active GT-KB files remain under `E:\GT-KB`.
- **Durable harness identity:** `harness-state/harness-identities.json` —
  harness installation IDs (`A` for Codex, `B` for Claude).
- **Durable role assignment:** `harness-state/role-assignments.json` —
  role-assignment source of truth.
- **Artifact-oriented governance:** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner-relevant process changes and
  accepted future work are captured as durable artifacts with explicit
  lifecycle triggers.
- **Predecessor proposal carried forward:**
  `bridge/gtkb-harness-parity-baseline-001.md` — original NEW filing.
- **Predecessor verdict carried forward:**
  `bridge/gtkb-harness-parity-baseline-002.md` — Codex Loyal Opposition NO-GO
  to which this revision responds.

## Current Baseline (Live, 2026-05-08)

Phase 1 baseline work (registry + checker + tests + canonical authoring source
+ generated Codex adapters) is **already implemented and PASS** in the live
checkout. This revised proposal does not propose to re-create Phase 1; it
proposes to govern the Phase 1 control surface as the canonical parity
baseline and to scope the remaining Phase 2-4 work.

Live verification commands and observed results (Prime Builder rerun on
2026-05-08 against the current checkout):

```text
python scripts/check_harness_parity.py --all --markdown
  -> Overall status: PASS
  -> Counts: PASS: 50
  -> "No parity issues found in the selected scope."

python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
  -> overall_status: PASS
  -> counts: {"PASS": 17}
  -> errors: [], extras: []
```

Live artifacts present in the checkout:

- `config/agent-control/harness-capability-registry.toml` — registry covering
  every `.claude/skills/*/SKILL.md` project skill plus harness-native
  capabilities.
- `scripts/check_harness_parity.py` — checker with `--all`, `--harness`, and
  `--role` selectors; emits Markdown and JSON reports.
- `tests/scripts/test_check_harness_parity.py` — unit coverage for `MISSING`,
  `DEGRADED`, `EXTRA`, and `PASS` paths (6 tests pass per `-002` evidence).
- `.claude/skills/*/SKILL.md` — canonical project-skill authoring source.
- `.codex/skills/*/SKILL.md` — generated Codex adapters; the parity checker
  recognizes adapter-backed skills as `PASS` with note "Generated adapter
  matches the canonical source."

The `-001` claim that Codex project-skill capabilities are uniformly
`DEGRADED` was **accurate at the time of authoring** but is **stale today**
because the adapter generation work landed between `-001` and this revision.
This proposal acknowledges that change rather than asking for `GO` on stale
phasing.

## Proposed Implementation

### Phase 1 — Baseline Control (already implemented; govern as canonical)

No new code in this phase. The proposal asks `GO` for the following governance
actions:

- Treat `config/agent-control/harness-capability-registry.toml` as the
  canonical registry for harness parity.
- Treat `scripts/check_harness_parity.py` as the canonical parity checker
  surface.
- Treat `.claude/skills/*/SKILL.md` as the canonical project-skill authoring
  source and `.codex/skills/*/SKILL.md` as the generated adapter surface.
- Lock the existing `PASS: 50` (full) / `PASS: 17` (codex/loyal-opposition)
  posture as the current parity baseline against which future drift is
  measured.

Acceptance for Phase 1 (governance ratification only):

- The registry and checker are referenced as the parity authority in startup
  disclosure, role-change flows, and the release-candidate gate spec when
  Phase 2 lands.
- Live checker output continues to report `PASS` for the registered scope.
- Any future change to `config/agent-control/harness-capability-registry.toml`
  or `scripts/check_harness_parity.py` is a bridge-governed change.

### Phase 2 — Event Triggers (future work)

Wire the parity checker into regular lifecycle events:

- Session start: run a fast role-scoped parity check after durable harness ID
  and role resolution.
- Role assignment change: run parity for the affected harness and newly
  assigned role after `scripts/harness_roles.py` updates
  `harness-state/role-assignments.json`.
- Capability source change: run full parity when any of these paths changes:
  `.claude/skills/**/SKILL.md`, `.claude/settings.json`, `.codex/hooks.json`,
  `.codex/config.toml`, `config/agent-control/harness-capability-registry.toml`,
  or harness-state role/identity files.
- Release candidate gate: include a full parity review so degraded or missing
  harness capabilities cannot remain invisible.

Implementation candidates:

- extend `scripts/session_self_initialization.py` to include parity status in
  startup output (note: a Harness-parity status line is **already present** in
  startup disclosure — `Harness parity: pass (harness=claude, role=prime-builder, PASS=20)`;
  Phase 2 would formalize this as a tested, role-scoped surface);
- extend `scripts/harness_roles.py` with a post-update parity check call;
- add a release-gate assertion to fail only on required `MISSING`, while
  preserving `DEGRADED` as a visible warning until native parity is complete.

### Phase 3 — Stale-Adapter Detection and Adapter Governance (partial; future work)

Generated Codex adapter parity is currently `PASS` because adapters exist and
match canonical source hashes. Phase 3 governs adapter regeneration and
detects drift:

- include source hash, canonical source path, and generated timestamp in each
  adapter (current adapters carry the matching-source note; explicit headers
  to be standardized);
- add stale-adapter detection to `scripts/check_harness_parity.py` (current
  output reports the matching-source note; an explicit `STALE` state is
  Phase 3 scope);
- add a governed adapter regeneration command;
- add a regression test that detects manual edits to generated adapters.

Acceptance for Phase 3:

- required Codex role capabilities remain `PASS` or are explicitly
  owner-gated;
- stale generated adapters are reported as `STALE`;
- manual edits to generated adapters are detected by the checker.

### Phase 4 — Structural Hygiene Integration (future work)

Use `structural-hygiene-review` as the companion control for parity:

- compare directory names, artifact names, skill names, glossary terms,
  command names, schemas, generated surfaces, and historical/archive markers;
- identify competing cues that can cause agent drift;
- prune, rename, archive, or isolate stale surfaces after bridge approval when
  the change is destructive or formal-governance-sensitive;
- run structural hygiene after parity changes and before release gating.

Acceptance for Phase 4:

- structural hygiene reports identify authority, cue, risk, correction, and
  verification for each issue;
- historical artifacts are clearly isolated and labeled;
- glossary terms are used consistently in capability names and documentation.

## Out Of Scope

- No credential lifecycle changes.
- No production deployment.
- No deletion of historical artifacts without an explicit cleanup proposal or
  owner approval.
- No assumption that Claude Code and Codex expose identical plugin or MCP
  surfaces; parity is semantic capability equivalence, not identical tooling.
- No changes to the canonical authoring source layout (`.claude/skills/`)
  under this proposal.

## Specification-Derived Test Plan

| Test ID | Spec Anchor | Test |
|---|---|---|
| T-registry-1 | Phase 1 acceptance: registry covers every project skill | `tests/scripts/test_check_harness_parity.py` `EXTRA` test asserts no undeclared `.claude/skills` entries (already passing). |
| T-required-1 | Phase 1 acceptance: missing required capability blocks parity | `tests/scripts/test_check_harness_parity.py` `MISSING` test (already passing). |
| T-fallback-1 | Phase 1 acceptance: documented fallback is visible but nonblocking | `tests/scripts/test_check_harness_parity.py` `DEGRADED` test (already passing). |
| T-extra-1 | Phase 1 acceptance: undeclared project skill is drift | `tests/scripts/test_check_harness_parity.py` `EXTRA` test (already passing). |
| T-adapter-1 | Phase 1 acceptance: adapter-backed Codex capability is `PASS` | `tests/scripts/test_check_harness_parity.py` `PASS-adapter` test asserts adapter-backed Codex capability is `PASS` (verify in post-impl that this case is covered; add if missing). |
| T-session-1 | Phase 2 acceptance: session start surfaces parity | Add startup test after Phase 2 wiring. |
| T-role-1 | Phase 2 acceptance: role changes trigger role-scoped parity | Add harness-role command test after Phase 2 wiring. |
| T-stale-1 | Phase 3 acceptance: generated adapter drift is detected | Add stale-adapter test after Phase 3 generator implementation. |
| T-release-1 | Phase 2 acceptance: release gate fails on required missing | Add release-gate coverage after Phase 2 or Phase 3. |

T-registry-1 through T-extra-1 are verifiable today against the current
checkout. T-adapter-1 is verifiable today; the post-impl report must confirm
or add the explicit assertion. T-session-1 through T-release-1 are bound to
their respective future phases; their post-impl reports will carry the
spec-to-test mapping at GO time for each phase.

## Verification Commands

Phase 1 (governance ratification) verification:

```text
python -m pytest tests/scripts/test_check_harness_parity.py -q --tb=short
python -m ruff check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py
python -m ruff format --check scripts/check_harness_parity.py tests/scripts/test_check_harness_parity.py
python scripts/check_harness_parity.py --all --markdown
python scripts/check_harness_parity.py --harness codex --role loyal-opposition --json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-parity-baseline
```

Future implementation reports for Phases 2-4 must also include targeted tests
for any touched startup, role-change, release-gate, or adapter-generation
code.

## Acceptance Criteria

- Harness parity has a registry-backed single source of truth (Phase 1
  ratification).
- Live checker output reports `PASS` for the registered scope at GO time.
- Cross-cutting bridge-governance specs are cited and the applicability
  preflight passes on the operative file.
- Session-start and role-change flows surface parity status for the active
  harness and role (Phase 2).
- Capability-source changes run or request a parity review (Phase 2).
- Required capabilities are never silently missing (Phase 2).
- Adapter drift is detected mechanically (Phase 3).
- Structural-hygiene review is available as a repeatable skill and is invoked
  for naming, directory, artifact, glossary, schema, and historical-artifact
  alignment reviews (Phase 4).

## Risk and Rollback

Phase 1 ratification is a no-code change; rollback is removing the
governance-ratification language from the post-impl report. The underlying
artifacts (registry, checker, tests, adapters) are already merged and would
remain regardless.

Phases 2-4 each carry their own rollback (revert the specific phase's added
code/tests). No phase is destructive of existing parity behavior.

## Decision Needed From Owner

None for Phase 1 ratification. Phase 2-4 implementation work will return
through the normal bridge protocol when scoped.

## Applicability Preflight (post-revision)

Will be reported in the post-impl report after this REVISED file is indexed
and the preflight is rerun against the operative file. Expected result:
`preflight_passed: true`, `missing_required_specs: []`,
`missing_advisory_specs: []`, given that all four previously missing required
specs are cited above.
