NEW

# Implementation Proposal — V1 Release Strategy: Docker Isolation-Validator Scoping (WI-3403)

bridge_kind: governance_review
Document: gtkb-v1-docker-isolation-validator-scoping
Version: 001
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 71561f13-3506-44cf-a451-47f87d257a83
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Project: GTKB-V1-RELEASE-STRATEGY-001
Project Authorization: PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING
Work Item: WI-3403
work_item_ids: [WI-3403]
target_paths: []
requires_verification: false
implementation_scope: governance_review_scoping
spec_ids: []

---

## Claim

Scope the future implementation thread for a Docker-based isolation validator per DELIB-2234 §10.4 + §9.3 (Release-Gate) and the promoted Antigravity Finding 1. Deliverable here is the validator's contract, container layout, validation matrix, and acceptance criteria. No Dockerfiles, CI workflows, or scripts are created in this proposal — that begins under the per-slice implementation PAUTHs minted after this scoping reaches GO.

## KB-Mutation Negation (self-demonstration)

target_paths is `[]`; no MemBase spec mutation, no protected narrative artifact edit, no source file change. The artifact produced is this scoping document.

## Why Now

DELIB-2234 §10.4 promotes Antigravity Finding 1 (platform/application isolation drift risk) into Release-Gate scope per §9.3. The validator answers: "Does a fresh, sandboxed adopter built from a published GT-KB wheel actually work without the platform codebase present?" That question can only be answered in a clean environment — by definition, the platform's own development tree contaminates the test.

Without the validator, isolation regressions (the S347 Agent Red severance drift, the kind of phantom-path issue the impl-start gate caught earlier this session) surface only at release time when they're expensive to fix. With the validator running as a release-gate prerequisite, those regressions surface at PR time.

## Why Not (alternatives considered)

1. **Defer to v1.0 cut.** Rejected: the isolation contract is already in force per `ADR-APPLICATION-ISOLATION-CONTRACT-001`; deferring detection past v1.0 means shipping with a broken contract.
2. **Use existing platform_tests/ for isolation validation.** Rejected: those tests run inside the platform tree, so they can't catch dependencies on platform-only paths. The validator's value is the clean environment.
3. **Use a venv instead of Docker for isolation.** Rejected: a venv shares the host filesystem (`.git`, `bridge/`, MemBase) and is still under the platform root. Docker gives a true root-boundary cut.
4. **Adopter-managed validator (each adopter writes their own).** Rejected: that lets isolation drift go undetected upstream. Centralizing the validator in GT-KB means one canonical contract.

## Prior Deliberations

- `DELIB-2234` — V1 release strategy: §10.4 isolation validator, §9.3 Release-Gate dependency, §10.5 rule-corpus cleanse.
- `DELIB-20260674` — owner AUQ approving PAUTH minting for V1 release strategy scopings (S414 wave-7).
- Antigravity Finding 1 — platform/application isolation drift risk; promoted into Release-Gate scope per DELIB-2234 §10.4.
- `memory/v1-release-strategy-deliberation-S347.md` — Hybrid Variant + Release-Gate framing.

_No prior bridge proposal exists for this scoping; this is the first._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — isolation validator produces release-gate evidence per DELIB-2234 §9.3.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — Agent Red is the reference adopter that the validator green-on-clean gates.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` — adopter onboarding flows assume the contract the validator enforces.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` — the contract under test.
- `DCL-APP-ROOT-MINIMIZATION-001` — application paths stay within `applications/<name>/`; the validator's clean-environment baseline.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal carries linked governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification Plan section below.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — scoping → per-slice implementation → per-slice verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the scoping artifact persists as durable bridge evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the validator's clean-environment baseline depends on this placement contract being enforced.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the scoping document itself is an artifact under change control.

## Owner Decisions / Input

- 2026-06-04 UTC, S414: owner AUQ → "Mint V1 release strategy PAUTH; I draft 3 scopings (Recommended)" recorded as `DELIB-20260674`. The PAUTH `PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING` includes WI-3403, allowed_mutation_classes=`["bridge_proposal_authoring"]`.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-2234 §10.4 + §9.3 + Antigravity Finding 1 define the validator's intent; this scoping concretizes the validation matrix and container layout within that intent.

## Proposed Scope of the Future Implementation Thread

### Validator Contract

Given a published GT-KB wheel `groundtruth_kb-X.Y.Z-py3-none-any.whl` and a fresh sandboxed environment, the validator must:

1. Install the wheel into a clean Python env (no platform source on `sys.path`).
2. Run `gt project init` to scaffold a fresh adopter at a sandboxed path.
3. Invoke a representative subset of CLI commands and hooks against the scaffolded adopter.
4. Exit 0 only if every check passes; surface structured per-check evidence on failure.

### Container Layout

```text
docker/isolation-validator/
├── Dockerfile                   # Python:3.12-slim base + minimal apt deps (git, sqlite3)
├── entrypoint.sh                # Orchestrates wheel install + scaffold + checks
├── checks/
│   ├── 01-wheel-installs.sh     # pip install <wheel>; pip show groundtruth-kb
│   ├── 02-gt-cli-present.sh     # gt --help; gt project --help
│   ├── 03-scaffold-fresh.sh     # gt project init <name>; verify tree shape
│   ├── 04-doctor-clean.sh       # gt platform doctor against fresh scaffold
│   ├── 05-bridge-protocol.sh    # bridge proposal + claim + write smoke
│   ├── 06-hook-invocation.sh    # PreToolUse + Stop hook invocations resolve
│   └── 07-app-isolation.sh      # Adopter cannot read platform-only paths
└── README.md                    # How to run + how to extend
```

### Slice Plan

**Slice 0 — Dockerfile skeleton + check harness**
- Authoring the Dockerfile, entrypoint, and skeleton `checks/01-wheel-installs.sh`
- Output: container builds; entrypoint runs check 01 and exits

**Slice 1 — CLI presence + scaffold (checks 02-03)**
- Add `02-gt-cli-present.sh` and `03-scaffold-fresh.sh`
- Tests: scaffolded tree matches `gt project init` golden expectations

**Slice 2 — Doctor + bridge protocol smoke (checks 04-05)**
- Add `04-doctor-clean.sh` and `05-bridge-protocol.sh`
- Tests: doctor PASS on fresh scaffold; bridge proposal authoring smoke clears compliance gate

**Slice 3 — Hook + isolation contract (checks 06-07)**
- Add `06-hook-invocation.sh` and `07-app-isolation.sh`
- Tests: hooks resolve from CLAUDE_PROJECT_DIR with no platform leakage; isolation contract assertions hold

**Slice 4 — CI integration**
- Wire the validator into GitHub Actions as a Release-Gate prerequisite per DELIB-2234 §9.3
- Tests: green-on-clean across the matrix in CI; red on a synthetic isolation regression

**Slice 5 — Release-gate binding**
- Update release scripts/`release_candidate_gate.py` to require validator green
- Tests: rc gate blocks on validator red

### Validation Matrix

| Axis | Values |
|------|--------|
| Python | 3.11, 3.12, 3.13 |
| Platform | linux/amd64, linux/arm64 |
| Wheel source | local build, PyPI (when published), GitHub release artifact |
| Scaffold target | adopter name "demo-app" (deterministic) |

### Acceptance Criteria (umbrella)

- AC1: Container builds reproducibly from `docker/isolation-validator/Dockerfile`.
- AC2: All 7 checks pass against a clean wheel install of the current main-branch GT-KB version.
- AC3: Synthetic isolation regression (e.g., import of a platform-only module from adopter code) fails check 07.
- AC4: Validator runs in <5 minutes for a single matrix entry.
- AC5: Validator is wired as a Release-Gate prerequisite per DELIB-2234 §9.3.

### Out of Scope

- Adopter-specific tests (those run separately under each adopter's CI).
- Performance benchmarks beyond the <5-minute budget.
- Multi-tenant testing (the validator covers single-adopter isolation).

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to bridge/INDEX.md:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-docker-isolation-validator-scoping
```

Expected: `preflight_passed: true`, `missing_required_specs: []`.

## Specification-Derived Verification Plan

| Spec | Verification (for this scoping proposal) |
|------|------------------------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains the document with NEW status. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Slice 5 wires the validator as a Release-Gate prerequisite. |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | Slice 1+ scaffolds an adopter and exercises GT-KB CLI surfaces — the conformance contract under test. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | The validator's green-on-clean gate IS the enforcement mechanism. |
| `ADR-APPLICATION-ISOLATION-CONTRACT-001` | Check 07 tests the contract directly. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Validator's clean baseline assumes the placement contract holds; failures surface as check failures. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites every relevant spec in Specification Links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every cited spec to verification evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Scoping → per-slice implementation → verification chain. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | The validator's baseline assumes this placement; failures surface as check failures. |

Verification commands (for the scoping artifact itself):

```text
test -f bridge/gtkb-v1-docker-isolation-validator-scoping-001.md
grep -q "^Document: gtkb-v1-docker-isolation-validator-scoping" bridge/INDEX.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-docker-isolation-validator-scoping
```

## Risk and Rollback

- **Risk:** Slice 0 Dockerfile choices (base image, layer ordering) get re-litigated in later slices. Mitigation: per-slice review preserves the option to revise the Dockerfile; the contract above is the stable interface.
- **Risk:** Validator runtime exceeds the <5-minute budget on slower CI runners. Mitigation: parallelize independent checks across slices 1-3; cache the wheel install layer.
- **Risk:** Synthetic-regression test (AC3) requires a deliberate isolation break to test the validator. Mitigation: maintain the synthetic break under `tests/synthetic-regressions/` so it's never accidentally committed to mainline adopter scaffolds.
- **Rollback:** The artifact is the scoping document itself. No source mutation in this proposal.

## Bridge Filing (INDEX-Canonical)

After this file is written, an entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-v1-docker-isolation-validator-scoping
NEW: bridge/gtkb-v1-docker-isolation-validator-scoping-001.md
```

## Recommended Commit Type

`docs(bridge):` — scoping proposal only.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
