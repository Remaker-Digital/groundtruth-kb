# Bridge Proposal — GT-KB Platform Spec-Coverage Architecture

**Status:** NEW (version 001 — scoping; awaits Codex GO)
**Author:** Prime Builder (Claude Code / Opus 4.7 1M)
**Session:** S321 (2026-04-29)
**Document name:** `gtkb-platform-spec-coverage-architecture-2026-04-29`

**Specs:** GOV-01, GOV-03, GOV-08, GOV-09, GOV-20 (existing; this proposal does not modify them)
**Specs proposed by this bridge** (will be filed in Slice 1 before any implementation): `GOV-SPEC-PRECONDITION-001`, `GOV-SPEC-COVERAGE-001`, `DCL-BRIDGE-PROPOSAL-SPEC-LINKAGE-001`, `DCL-TEST-IN-GATE-001`, `DCL-DCL-DRIVEN-DOCTOR-001`, `DCL-VERIFIED-SPEC-DERIVATION-001`, `DCL-TEST-SPEC-DERIVATION-001`, `PB-OWNER-DIRECTION-SPEC-CAPTURE-001`, `ADR-SPEC-COVERAGE-ARCHITECTURE-001`

**Trigger:** Owner directive 2026-04-29 (S321) following diagnosis of the smart-poller auto-trigger requirement failure cascade. Owner statement: "If this happens to a GT-KB user they will consider this a failure of the platform. This is an example of a major problem. We need a deep diagnosis and comprehensive fix proposed for the GT-KB system which will catch and correct all omissions like this in the future." Plus the strengthening: "It must *not* be possible to submit an implementation proposal that is not linked to any and all relevant specifications. This is an *essential* part of any and all implementation proposals."

**Non-negotiable invariants from owner direction:**
- Implementation proposals without spec linkage MUST be mechanically rejected (not just discouraged).
- Specifications MUST be created before bridge proposals reference behavioral/architectural contracts.
- All relevant specifications must be cited (not just a token reference).
- The fix must catch and correct ALL omissions of this class — not just the smart-poller incident.
- **VERIFIED issuance is conditional on test creation + execution derived from each linked spec.** Codex MUST NOT issue VERIFIED unless: (1) every linked spec has at least one derived test, (2) all derived tests are executed during the verification procedure, (3) all executed tests pass. Mechanical enforcement; no human judgment override.
- **Tests claiming to verify a spec MUST cite the spec ID + the specific assertion in their docstring.** Tests without spec-derivation citations cannot count as coverage. This binds tests to the specs they verify; coverage cannot be claimed circumstantially.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- **`bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` VERIFIED** — the incident this proposal responds to. Activation thread shipped observability without dispatch contract; revealed the platform-level governance gap.
- **`bridge/gtkb-bridge-poller-001-smart-poller-007.md` GO** (S315) — umbrella that explicitly deferred dispatch (P3 invoker) to a never-filed bridge. Demonstrates AP-2 (bridge scope amputation).
- **`bridge/critical-remediation-root-isolation-005.md` GO** (S315) — owner-corrective response to a different class of platform drift (root-boundary violations). Same systemic pattern: requirements stated verbally, never reaching mechanical enforcement.
- **`bridge/gtkb-membase-effective-use-recovery` (work_list row 19, not yet filed)** — Codex LO assessment surfaced a similar pattern: phantom-INDEX entries for specs claimed as VERIFIED but never implemented. Same anti-pattern (AP-6 in §2.2 below).
- **DELIB-1314 + DELIB-1315 (S317 working-tree triage VERIFIED)** + **DELIB-1289 + DELIB-1290 (S319 session-hygiene gitignore VERIFIED)** — both bridges that addressed drift after-the-fact rather than preventing it. Demonstrates the platform's reliance on owner-driven cleanup loops instead of structural prevention.

No prior deliberation proposes a comprehensive spec-coverage architecture. This is novel platform work.

---

## §0. Scope

This is a **GT-KB platform-level governance architecture proposal**. It proposes a 7-layer integrity system that makes the smart-poller-class failure mechanically impossible across all GT-KB adopter projects (not just Agent Red).

**In scope:**
1. New rules, specs, and hooks that mechanically enforce spec-coverage at every governance handoff
2. Changes to `groundtruth-kb` framework code (bridge protocol implementation, doctor checks, release-candidate gate, scaffold templates)
3. Migration plan for existing bridges (grandfathering, retroactive linkage)
4. Documentation updates for adopter onboarding
5. Validation: verifying the smart-poller incident is now caught at the L1 commit stage

**Out of scope:**
- The narrow incident remediation (filing the missing smart-poller DCL/ADR + wiring orphan tests) — handled by parallel bridge `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md`
- The interim stop-the-bleeding rule — handled by parallel bridge `bridge/gov-process-spec-precondition-2026-04-29-001.md`
- Phase 2 of standing isolation directive — preconditioned by but separate from this work
- Mojibake cleanup, smart-poller src docstring alignment, and other in-flight bridges — orthogonal

---

## §1. Failure Diagnosis — Why the Platform Allowed This

### §1.1 The lossy chain

Every requirement traverses these waystations, each of which can lose fidelity:

```
[1] Owner verbal statement
[2] Memory note / chat capture
[3] Bridge proposal §0 scope
[4] Bridge GO conditions
[5] Implementation
[6] Tests in some directory
[7] Release-gate execution
[8] Codex VERIFIED
```

The platform has **bilateral review** between adjacent waystations (e.g., Codex reviews [3]→[4], pre-commit hooks gate [5]→[7]) but **no global integrity layer** that ensures the requirement made it from [1] to [8] without dropping.

### §1.2 Five structural weaknesses

| # | Weakness | Mechanism | Consequence |
|---|---|---|---|
| W1 | Spec creation is voluntary | `/kb-spec` exists but bridge protocol doesn't require it | Verbal-only requirements travel forever in conversation/memory and never reach release-gate |
| W2 | Bridge scope can amputate dependencies | Each bridge defines its own scope; deferred work can be left unfiled | Load-bearing pieces become invisible to GO/VERIFIED |
| W3 | Tests can be orphans | Release-gate test list is hand-curated | Tests that exist but don't run still let regressions slip through |
| W4 | Doctor verifies state, not contracts | No mechanism mapping DCL assertions → doctor checks | Behavioral regressions silent unless somebody manually probes |
| W5 | VERIFIED is bounded by proposal scope | Codex verifies what proposal claims; no spec-coverage check | Platform-wide drift accumulates one VERIFIED at a time |

### §1.3 Anti-pattern catalog

| AP | Anti-pattern | Smart-poller evidence | Other documented occurrences |
|---|---|---|---|
| AP-1 | Verbal requirement never specced | Auto-trigger contract: 0 KB matches | DELIB-S312 deterministic-services principle (similar pattern) |
| AP-2 | Bridge scope amputation | Umbrella deferred dispatch to unfiled P3 invoker | GTKB-WRAPUP S1.a (deferred); GTKB-COMMAND-SURFACE CS-2 (deferred) |
| AP-3 | Orphan tests | `test_bridge_poller_runner.py` not in any gate | DORA-001b S319 caught only by Codex luck |
| AP-4 | Observability-only doctor | All current doctor checks are state-only | Universal in current `_check_*` functions |
| AP-5 | VERIFIED without spec coverage | Activation `-012` VERIFIED with no spec referenced | Universal in current bridges |
| AP-6 | Phantom-INDEX entries | Multiple in S315/S319/S320 (annotated but not prevented) | Documented in DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT P1 |
| AP-7 | Bridge cites external GO that doesn't fully cover | Activation cited umbrella; umbrella deferred dispatch | Common pattern in S314-S320 |

---

## §2. Proposed Architecture — 7 Interlocking Layers

Each layer addresses one or more anti-patterns. Layers compose: a requirement that bypasses one layer is caught by the next.

### §2.1 Layer 1: Spec-First Mechanical Enforcement at Bridge-Filing Time

**Catches:** AP-1, AP-7

**Per owner directive (non-negotiable):** it MUST be mechanically impossible to file an implementation proposal without spec linkage.

**Specs filed by Slice 1:**
- `GOV-SPEC-PRECONDITION-001`: every implementation bridge proposal (NEW or REVISED) MUST have a `Specs:` field at the top listing every relevant SPEC/GOV/ADR/DCL/PB ID. Field MUST be non-empty. Cited IDs MUST resolve to existing specs in `groundtruth.db`.
- `DCL-BRIDGE-PROPOSAL-SPEC-LINKAGE-001`: machine-checkable assertion. Verifies via shell command: `python scripts/check_bridge_spec_linkage.py <file>` returns 0 iff the file has a non-empty `Specs:` field with all-resolving IDs.

**Mechanism:**
- New file: `scripts/check_bridge_spec_linkage.py` — parses `bridge/*.md` files, extracts `Specs:` field, validates against `groundtruth.db`
- New file: `.claude/hooks/bridge-proposal-spec-linkage-gate.py` — PreToolUse hook on Bash `git commit` operations affecting `bridge/*-001.md` or any REVISED versions; rejects commit if `check_bridge_spec_linkage.py` fails
- New rule: `.claude/rules/bridge-proposal-spec-linkage.md` — auto-loaded; documents the contract for both Prime Builder and Loyal Opposition
- Codex (Loyal Opposition) review skill (`.claude/skills/proposal-review/SKILL.md` or equivalent) extended: first check is `Specs:` field presence and validity; auto-NO-GO if missing or insufficient
- **Sole exemption:** proposals whose own scope is "file SPEC-X" use `Specs: pending:NEW-SPECS-PROPOSED-IN-THIS-BRIDGE` with the proposed IDs explicitly listed in §0; Codex verifies the proposal actually files those specs as Slice/Step 0

### §2.2 Layer 2: Spec-to-Test Bidirectional Mapping

**Catches:** AP-3 (orphan tests can't claim coverage)

**Specs filed by Slice 1:**
- `GOV-SPEC-COVERAGE-001`: every spec with `status` in (`implemented`, `verified`) MUST have at least one citing test. Every test exercising a behavioral contract MUST cite the spec ID(s) in its docstring.
- `DCL-SPEC-TEST-COVERAGE-001`: machine-checkable. New table `spec_test_coverage` populated by parsing test docstrings; release-gate audit fails if any `verified` spec lacks ≥1 citing test.

**Mechanism:**
- New script: `scripts/audit_spec_test_coverage.py` — parses `tests/**/*.py` and `groundtruth-kb/tests/**/*.py` for spec-ID citations in docstrings; cross-references with `groundtruth.db`; reports gaps
- New table: `spec_test_coverage` (auto-populated by audit script)
- Release-gate addition: run `audit_spec_test_coverage.py`; fail if any `verified` spec lacks tests
- Codex VERIFIED process extended: must run audit on the changed-modules slice and report

### §2.3 Layer 3: Test-in-Gate Auto-Discovery

**Catches:** AP-3 (tests-not-in-any-gate)

**Specs filed by Slice 1:**
- `DCL-TEST-IN-GATE-001`: ALL tests under `tests/` and `groundtruth-kb/tests/` MUST be discoverable and executable by the release-candidate gate. Exclusions require explicit `# spec-test-exclusion: <reason>` markers and audit tracking.

**Mechanism:**
- Replace `_python_gates()` hand-curated list in `scripts/release_candidate_gate.py` with `pytest tests/ groundtruth-kb/tests/`
- `pyproject.toml` add `[tool.pytest.ini_options].testpaths = ["tests", "groundtruth-kb/tests"]`
- New script: `scripts/audit_excluded_tests.py` — finds files marked `spec-test-exclusion`; verifies justifications are current; release-gate fails if exclusions exceed N or lack justifications
- Migration: existing tests not currently in the hand-curated list are vetted (some intentionally excluded for performance; mark them; rest get auto-included)

### §2.4 Layer 4: DCL-Driven Doctor Checks

**Catches:** AP-4 (observability-only doctor)

**Specs filed by Slice 1:**
- `DCL-DCL-DRIVEN-DOCTOR-001`: every `DCL-` artifact with a `behavioral_assertions:` field MUST have those assertions wired into `gt project doctor` output. The doctor MUST execute behavioral assertions, not just state assertions.

**Mechanism:**
- Extend DCL spec format: add optional `behavioral_assertions:` field (list of shell commands or Python expressions)
- Extend `groundtruth_kb/project/doctor.py` to enumerate all DCLs with `behavioral_assertions`; run them; report pass/fail in standard doctor output
- New `gt project doctor --behavioral-only` mode for targeted runs
- Migrate existing DCLs that have informal behavioral expectations into formal `behavioral_assertions` where applicable

### §2.5 Layer 5: VERIFIED Requires Test Creation + Execution Derived from Linked Specs (mechanical, non-negotiable)

**Catches:** AP-5 (VERIFIED without spec coverage), and forecloses circumstantial claims of coverage

**Per owner directive (non-negotiable):** it MUST be mechanically impossible to issue VERIFIED for an implementation without:
1. **Test existence:** every spec linked in the implementation proposal has at least one derived test (a test whose docstring cites the spec ID + the specific assertion being verified)
2. **Test execution:** every derived test is executed during the VERIFIED procedure
3. **Test passing:** every executed test passes
4. **Mechanical:** these conditions are enforced by the verification tooling, not by reviewer judgment

**Specs filed by Slice 1:**
- `DCL-VERIFIED-SPEC-DERIVATION-001`: VERIFIED issuance is conditional on the three conditions above. Failure of any condition is automatic NO-GO. Behavioral assertion: `python scripts/run_spec_derived_tests.py --bridge <bridge-file>` returns 0 iff (a) every linked spec has ≥1 derived test, (b) all derived tests executed, (c) all passed.
- `DCL-TEST-SPEC-DERIVATION-001`: tests claiming to verify a spec MUST cite the spec ID + specific assertion in their docstring. Format: `"""Verifies <SPEC-ID> <assertion-ref>: <one-line description>."""`. Tests without spec-derivation citations cannot count as coverage.

**Mechanism:**
- New file: `scripts/run_spec_derived_tests.py` — given a bridge file: parses `Specs:` field; for each spec, finds all derived tests (by docstring citation); executes them via pytest; returns 0 iff every spec has ≥1 test AND all tests pass; non-zero with structured output otherwise
- New file: `bridge/VERIFIED_TEMPLATE.md` — required "Spec-Derived Test Execution" section listing per-spec test paths + execution outcomes
- Codex (Loyal Opposition) review skill prompt extended: VERIFIED procedure is now:
  1. Parse `Specs:` field from implementation proposal
  2. Run `scripts/run_spec_derived_tests.py --bridge <bridge>`
  3. If exit non-zero: file an implementation-gap NO-GO; surface either "spec X has no derived tests" or "spec X derived test Y failed"
  4. If exit zero: include the per-spec execution report in the VERIFIED response, then issue VERIFIED
- Existing tests retroactively annotated (Slice 9 migration) — tests that exercise an existing spec are updated to cite it explicitly in the docstring; tests that don't cite any spec become candidates for either deletion (if the behavior they exercise has no spec) or spec-creation + citation
- Spec format extension: add `affected_modules:` field (source paths the spec governs) — used by Layer 6 audit to detect specs whose modules changed without VERIFIED reconciliation

**Edge cases handled:**
- Implementation introducing a new spec → derived tests filed in the same implementation slice; the Layer 5 check verifies them before VERIFIED
- Implementation satisfying a pre-existing spec → derived tests must already exist OR be added in the implementation; missing tests block VERIFIED
- Implementation that "implements but doesn't yet verify" a spec → status stays `implemented`, not `verified`. The Layer 5 gate prevents promotion to `verified` without test execution
- Spec linked but irrelevant to implementation (false linkage) → Codex flags during review; proposer must either justify or remove
- Implementation that improves coverage without changing the spec → still requires re-execution of all derived tests; passes trivially

### §2.6 Layer 6: Standing Audit + Report

**Catches:** All anti-patterns by surfacing accumulated drift

**Specs filed by Slice 1:**
- `GOV-PLATFORM-GOVERNANCE-AUDIT-001`: GT-KB platform MUST run a standing governance audit pre-release-gate. Audit MUST report all 7 anti-patterns. P0/P1 gaps fail the release-candidate gate.

**Mechanism:**
- New script: `scripts/gtkb_governance_audit.py` — runs all 7 audits (specs without tests, orphan tests, bridges without spec citations, doctor checks not derived from DCL, implementations claiming verified without DCL assertions running, phantom-INDEX entries, bridge-citing-amputated-scope detection)
- Output: `independent-progress-assessments/GOVERNANCE-AUDIT-{date}.md`
- Pre-release-gate run; fails if any P0/P1 gap
- Weekly scheduled run via cron/scheduled-task as proactive surfacing

### §2.7 Layer 7: Owner-Direction → Spec-Capture Loop

**Catches:** AP-1 at the source (owner statement → memory)

**Specs filed by Slice 1:**
- `PB-OWNER-DIRECTION-SPEC-CAPTURE-001`: Prime Builder protocol MUST detect classified owner input (existing `spec-classifier.py`) and either (a) cite an existing spec covering it OR (b) file a placeholder spec at the next bridge boundary. Pending classifications MUST be tracked in `memory/pending-spec-classifications.md`.

**Mechanism:**
- Extend `.claude/hooks/spec-classifier.py` (existing UserPromptSubmit hook) — when owner input is classified as specification language, append to `memory/pending-spec-classifications.md` with timestamp and classification confidence
- Bridge-filing pre-check: if `pending-spec-classifications.md` has unresolved entries, the new bridge must address them or explicitly defer (with justification) — auto-injected reminder in the proposal template
- Standing audit (§2.6) reports pending classifications older than 1 session as P1 gap

---

## §3. Architectural Decision Record

**Specs filed by Slice 1:**
- `ADR-SPEC-COVERAGE-ARCHITECTURE-001`: documents the 7-layer architecture, the rejected alternatives, and the rationale for layered redundancy.

**Rejected alternatives (cited in the ADR):**
- **A1 — Single mega-rule "all proposals must cite specs"** without mechanical enforcement: rejected because owner directive explicitly says voluntary compliance is insufficient. Mechanical enforcement is mandatory.
- **A2 — Replace bridge protocol with spec-only protocol**: rejected because bridge protocol's bilateral review (Prime ↔ Codex) is high-quality. The fix is integration with specs, not replacement.
- **A3 — Trust Codex review to catch spec gaps**: rejected because Codex can only verify what's in scope. Codex needs a mechanical gate before review (Layer 1) and after (Layer 5).
- **A4 — Comprehensive global registry vs layered redundancy**: rejected because a single registry is a single point of failure. Layered redundancy means a requirement that bypasses one layer is caught by the next.

**Why 7 layers (not fewer):** owner directive ("catch and correct ALL omissions") requires belt-and-suspenders. Each layer addresses a different waystation in §1.1's lossy chain. Fewer layers would leave gaps:
- Layer 1 only → tests can still be orphans (W3)
- Layers 1+3 only → doctor still doesn't verify behavior (W4)
- Layers 1+3+4 only → VERIFIED still doesn't reconcile (W5)
- All 5 mechanical layers + audit (L6) → still missing the upstream capture (L7) for verbal-only requirements
- All 6 + L7 → catches owner-direction at the source

The 7 layers are the minimum sufficient set.

---

## §4. Implementation Plan — Sliced

This is a substantial multi-slice program. **No slice ships behavior that bypasses Layer 1**: every implementation slice must itself comply with the rules it implements (bootstrap-safe).

| Slice | Subject | Files | Specs filed |
|---|---|---|---|
| 1 | **Specs** — file all 8 specs (GOV/DCL/PB/ADR) listed in this proposal's `Specs proposed by this bridge` field. KB inserts only; no source code yet. | `groundtruth.db` insertions via `db.insert_spec()` | All 8 |
| 2 | **Layer 1 implementation** — bridge proposal spec-linkage gate | `scripts/check_bridge_spec_linkage.py`, `.claude/hooks/bridge-proposal-spec-linkage-gate.py`, `.claude/rules/bridge-proposal-spec-linkage.md`, `.claude/settings.json` registration, tests, Codex skill prompt update | (cites Slice 1 specs) |
| 3 | **Layer 3 implementation** — test-in-gate auto-discovery | `scripts/release_candidate_gate.py` rewrite, `pyproject.toml`, `scripts/audit_excluded_tests.py`, migration of existing exclusions, tests | (cites Slice 1 specs) |
| 4 | **Layer 2 implementation** — spec-to-test bidirectional mapping | `scripts/audit_spec_test_coverage.py`, new `spec_test_coverage` table, schema migration, release-gate integration, tests | (cites Slice 1 specs) |
| 5 | **Layer 5 implementation** — VERIFIED spec-derived test creation+execution gate (mechanical) | `scripts/run_spec_derived_tests.py`, spec format extension (`affected_modules:`), `bridge/VERIFIED_TEMPLATE.md`, Codex skill prompt update, derived-test parsing logic in tests-DB integration, tests covering DCL-VERIFIED-SPEC-DERIVATION-001 + DCL-TEST-SPEC-DERIVATION-001 | (cites Slice 1 specs) |
| 6 | **Layer 4 implementation** — DCL-driven doctor checks | `groundtruth_kb/project/doctor.py` extension, DCL spec format extension (`behavioral_assertions:`), migration of existing DCLs, tests | (cites Slice 1 specs) |
| 7 | **Layer 7 implementation** — owner-direction spec-capture loop | `.claude/hooks/spec-classifier.py` extension, `memory/pending-spec-classifications.md` lifecycle, bridge-filing pre-check, tests | (cites Slice 1 specs) |
| 8 | **Layer 6 implementation** — standing governance audit | `scripts/gtkb_governance_audit.py`, audit-output template, scheduled task, release-gate integration, tests | (cites Slice 1 specs) |
| 9 | **Migration** — retroactive spec linkage for active bridges | Audit existing bridges; file specs for un-linked work; mark as compliant | (cites Slice 1 specs) |
| 10 | **Validation** — verify the smart-poller incident is now caught | Synthetic test: create a bridge proposal without spec linkage; confirm L1 hook rejects commit. Run governance audit; confirm it would have flagged the original gap. | (cites Slice 1 specs) |

**Sequencing constraints:**
- Slice 1 (specs) MUST land first (bootstrap)
- Slices 2-8 can largely run in parallel after Slice 1, but L1 (Slice 2) blocks new bridge filings, so it should land second so subsequent slices can validate the gate
- Slice 9 (migration) blocks Slice 10 (validation)

**Estimated scope:** large. Each slice is its own dedicated session. Total: ~10 sessions. No slice should be bundled with another.

---

## §5. Validation — Smart-Poller Incident as Regression Test

After all slices land, the test exercises both the L1 filing gate and the L5 VERIFIED gate:

**L1 filing-gate validation:**
1. Synthetically file `bridge/test-fake-proposal-no-specs-001.md` without a `Specs:` field
2. Attempt `git commit` → **expected: rejected by L1 pre-commit hook**
3. Add empty `Specs:` field; retry commit → **expected: still rejected** (empty is invalid)
4. Add `Specs: SPEC-NONEXISTENT-12345`; retry commit → **expected: still rejected** (ID doesn't resolve)
5. Add `Specs: GOV-01`; retry commit → **expected: accepted** (cited spec exists)
6. File against Codex review (Loyal Opposition skill) → **expected: NO-GO** (spec cited but irrelevant to proposal subject)
7. Re-file with relevant specs → **expected: GO**

**L5 VERIFIED-gate validation (per owner directive, non-negotiable):**
8. Implement an authorized proposal that links `DCL-EXAMPLE-001` (a synthetic test spec)
9. File post-impl WITHOUT writing any test deriving from `DCL-EXAMPLE-001`
10. Attempt VERIFIED via Codex skill → **expected: automatic NO-GO** ("spec DCL-EXAMPLE-001 has no derived tests")
11. Add a test with docstring NOT citing any spec → retry VERIFIED → **expected: still NO-GO** (test doesn't derive from the spec)
12. Add a test with docstring `"""Verifies DCL-EXAMPLE-001 §1: <description>."""` → retry VERIFIED → **expected: passes the existence check**
13. Make the test fail → retry VERIFIED → **expected: NO-GO** ("derived test failed")
14. Fix the test → retry VERIFIED → **expected: GO** with execution evidence in the VERIFIED response

**Smart-poller incident retroactive validation:**
If smart-poller-class regression occurs (someone disables dispatch), the audit script (L6) catches it; the doctor (L4) catches it via DCL behavioral assertion; Codex VERIFIED (L5) catches it because the dispatch spec's derived tests would fail. **Four-layer defense vs. zero-layer current state.** Even if any single layer were to silently fail, three other layers independently catch the same regression.

---

## §6. Migration / Backward Compatibility

**Existing bridges (open and closed):**
- Bridges already in `bridge/` are grandfathered. The L1 hook only fires on new commits to bridge files.
- Slice 9 audits existing bridges, files retroactive specs where missing, marks compliant.
- This work is finite (~30-50 currently-active bridges) and bounded (new bridges must comply).

**Existing specs:**
- Slice 4 audits all specs at `verified` status; files placeholder tests if missing. Spec promotion path adapts: cannot promote to `verified` without ≥1 citing test.

**Adopter projects:**
- This is GT-KB framework work. Adopters consume via `gt project upgrade` after framework slices VERIFIED.
- Adopter migration: the L1 hook ships in the upgraded framework; adopter's existing bridges grandfathered; new adopter bridges must comply.

---

## §7. Risks + Reversibility

### §7.1 Bootstrap risk

This proposal itself must comply with L1. Citation: this bridge cites `GOV-01, GOV-03, GOV-08, GOV-09, GOV-20` (existing) plus the 8 new specs to be filed in Slice 1 (using the `pending:` exemption mechanism, with Slice 1 explicitly the first executable work).

### §7.2 Friction risk

L1 makes filing more expensive (must cite specs). **Mitigation:** the upfront cost is offset by structural prevention of incident-cleanup work like S321's drift triage (which cost ~50 commits + 4 NO-GO/REVISED cycles to recover from drift the system shouldn't have allowed).

### §7.3 Spec creation overhead

Slice 1 files 8 specs. Each requires owner-acknowledgement per `acting-prime-builder.md` "Formal Artifact Approval And Audit Principle". **Mitigation:** Slice 1 batches all 8 into a single owner-decision-acknowledgement packet.

### §7.4 Reversibility

Each slice individually revertable. The architecture is composable: even partial deployment (e.g., just L1 + L2) provides material protection.

### §7.5 Performance

L1 pre-commit hook: cheap (parse 1 markdown file + 1 SQLite query). L6 audit: bounded by spec count (~2,100 specs); estimated <30s.

---

## §8. Codex Review Request

Please verify:

1. **Architecture completeness.** Are all 7 anti-patterns in §1.3 actually addressed by the layered design? Any anti-pattern I missed?
2. **Layer interaction correctness.** §2 claims layered redundancy ensures no single bypass. Walk through each layer's failure mode and verify the next layer catches it.
3. **Bootstrap safety.** This proposal cites pending specs in Slice 1. Is the `pending:` exemption mechanism (described in §2.1) sound? Or does it create a loophole (e.g., proposals citing pending specs that never get filed)?
4. **Slice ordering.** §4 sequences Slice 1 first. Any dependency order issues in Slices 2-8?
5. **Migration / grandfathering.** Are existing bridges and specs handled correctly? Any compatibility breaks for in-flight Agent Red work or upstream `groundtruth-kb` users?
6. **Owner direction fidelity (filing gate).** Owner explicitly stated "must NOT be possible" (mechanical) and "any AND ALL relevant specifications". Does §2.1 satisfy both? Codex's auto-NO-GO check (§2.1) — is it strong enough or does it need additional teeth?
7. **Owner direction fidelity (VERIFIED gate).** Owner explicitly stated VERIFIED MUST NOT be possible without test creation + execution from linked specs, and tests must be derived from specs (citation in docstring). Does §2.5 satisfy both via mechanical enforcement (`scripts/run_spec_derived_tests.py` exit code)? Is the docstring-citation format (`"""Verifies <SPEC-ID> §<assertion>: <description>."""`) sufficiently parseable, or does the format need to be more rigid (e.g., explicit `:spec:` and `:assertion:` Sphinx-style markers)?
8. **Friction acceptability.** Owner implicitly accepted the friction cost ("essential part of any and all implementation proposals"). Does the proposal's friction-mitigation (batched spec creation, exemption mechanism, retroactive annotation in Slice 9) preserve the spec-first invariant without being prohibitive?
9. **Coverage of TODO-VERIFIED gap on existing implementations.** What about the ~30-50 existing bridges that have already issued VERIFIED without spec derivation? Slice 9 migration handles them, but the L5 gate would block re-VERIFIED if any of those threads needs re-review. Is that acceptable, or should there be an explicit grandfathering window?

A NO-GO with specific findings remains valuable. This is platform-level governance work — getting it right matters more than landing it fast.

---

## §9. Reference Artifacts

- Triggering incident: `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (S320 VERIFIED, with hindsight: PREMATURE — see §1)
- Diagnosis report: this proposal's §1
- Owner directives: 2026-04-29 (S321) — non-negotiable mechanical enforcement of spec linkage; comprehensive coverage of all omissions of this class
- Parallel filings (next): `bridge/spec-smart-poller-auto-trigger-2026-04-29-001.md` (incident-narrow remediation), `bridge/gov-process-spec-precondition-2026-04-29-001.md` (interim stop-the-bleeding)
- Authority chain: GOV-01 (spec-first), GOV-03 (specs as negotiation artifact), GOV-08 (KB as truth), GOV-09 (input classification), GOV-20 (architecture decisions ADR/DCL/IPR/CVR)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
