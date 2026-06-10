NEW

# Implementation Proposal — V1 Release Strategy: §10.1 Mechanical-Enforcement Gate Scoping (WI-3401)

bridge_kind: governance_advisory
Document: gtkb-v1-mechanical-enforcement-gate-scoping
Version: 001
Author: Prime Builder (Claude Opus 4.7, harness B)
Date: 2026-06-04 UTC

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: bfc70de3-76e6-4db9-a78b-ce2758bb8679
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, autonomous /loop dynamic mode

Project: GTKB-V1-RELEASE-STRATEGY-001
Project Authorization: PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING
Work Item: WI-3401
work_item_ids: [WI-3401]
target_paths: []
requires_verification: false
implementation_scope: governance_review_scoping
spec_ids: []

---

## Claim

Scope a future bridge proposal for the V1 Hybrid Variant mechanical-enforcement gate per DELIB-2234 §8.1. This is a *scoping* proposal whose deliverable is the slice plan, requirement enumeration, acceptance criteria, and risk surface for the eventual implementation thread — not the gate's implementation. No source/test/script/hook mutation is in scope here.

## KB-Mutation Negation (self-demonstration)

target_paths is `[]`; no MemBase spec mutation, no protected narrative artifact edit, no source file change. This is governance_review_scoping — the artifact produced is this bridge document.

## Why Now

V1 release strategy depends on a mechanical-enforcement gate as a load-bearing prerequisite for Hybrid Variant per DELIB-2234 §8.1. The gate is the PreToolUse Write/Edit hook that validates spec-governed writes against contract assertions, blocks failing writes, and emits structured remediation messages. Without it, the spec corpus governs by convention rather than by enforcement — exactly the S347 Agent Red severance drift class. Scoping the gate now lets per-slice implementation proceed under proper authorization rather than blanket fast-lane claims that Codex correctly rejects (per the WI-3380 NO-GO lesson this session).

## Why Not (alternatives considered)

1. **Skip scoping and go straight to implementation.** Rejected: the gate's scope is non-trivial (contract assertion validator + Write/Edit hook + remediation surface + opt-in/opt-out boundaries). Going direct without scoping risks fast-lane mismatch + scope creep + multi-revision NO-GO churn.
2. **Defer until V1 release date is set.** Rejected: per DELIB-2234 V1 release strategy uses quality-driven pacing, not date-driven. The gate is on the critical path; deferral pushes the V1 cut.
3. **Roll the gate into an existing thread (e.g., bridge-compliance-gate).** Rejected: bridge-compliance-gate enforces bridge-protocol shape; mechanical-enforcement-gate enforces spec-contract conformance. Conflating them muddies their failure modes and remediation texts.

## Prior Deliberations

- `DELIB-2234` — GT-KB v1.0 release strategy: Hybrid Variant + Release-Gate + 3-tier + In-tree-then-separate spec corpus + Promotion governance + Quality-driven pacing. §8.1 defines the mechanical-enforcement gate.
- `DELIB-20260674` (this session, S414 wave-7) — owner AUQ approving PAUTH minting for V1 release strategy scopings.
- `memory/v1-release-strategy-deliberation-S347.md` — captured Hybrid Variant + 3-tier + spec corpus framing.
- `memory/v1-0-release-plan-scope.md` — V1 release plan scope.

_No prior bridge proposal exists for this scoping; this is the first._

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this scoping proposal lives in `bridge/`.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — production-release work requires governed release-readiness evidence; the gate produces such evidence.
- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` — adoption-enforcement framework that the gate concretizes for spec-contract conformance.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance; the scoping proposal IS an artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal carries linked governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-Derived Verification Plan section below maps each cited spec to verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — lifecycle trigger: scoping → implementation → verification chain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the scoping artifact persists as durable bridge evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the gate stays within `groundtruth-kb/` and `.claude/hooks/`; no `applications/` mutation. The S347 Agent Red severance-drift reference is historical evidence only.

## Owner Decisions / Input

- 2026-06-04 UTC, S414: owner AUQ "How should I handle the final 4 P1 WIs (V1 release strategy trio + D3+D4 fix)?" → "Mint V1 release strategy PAUTH; I draft 3 scopings (Recommended)". Captured as `DELIB-20260674`. The AUQ answer authorized: minting `PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING`, drafting WI-3401/3402/3403 scoping proposals, governance_review only (target_paths:[], no implementation).
- 2026-06-04 UTC: PAUTH minted with `--owner-decision DELIB-20260674`, includes WI-3401/3402/3403, allowed_mutation_classes=`["bridge_proposal_authoring"]`, forbidden_operations=`["spec_deletion","deploy","git_push_force"]`.

## Requirement Sufficiency

Existing requirements sufficient. DELIB-2234 §8.1 defines the gate's intent; this scoping concretizes the slice plan within that intent. New requirements arise only if the slice plan surfaces ambiguity at implementation time (deferred to per-slice proposals).

## Proposed Scope of the Future Implementation Thread

### Concept

The mechanical-enforcement gate is a `PreToolUse` Write/Edit hook whose role is to validate that every protected-path write satisfies the contract assertions declared on the relevant spec(s). Writes that fail assertions are blocked with a structured remediation message identifying which contract clause failed.

### Slice Plan

**Slice 0 — Contract-Assertion Reader**
- New helper `scripts/spec_contract_assertions.py` that reads `assertions` field from MemBase specs (DCL/ADR/PB) for a given target file path.
- Test coverage: assertion-extraction for each spec subtype.

**Slice 1 — Gate Hook (advisory mode)**
- New `.claude/hooks/mechanical-enforcement-gate.py` registered as PreToolUse Write/Edit.
- For each write, identify applicable spec(s) via path mapping → read assertions → evaluate.
- Advisory only: log failures, do not block.
- Test coverage: hook fires on matching paths; assertion failure logged; non-matching paths pass through.

**Slice 2 — Blocking Mode**
- Promote the hook from advisory to blocking when assertion fails.
- Owner-AUQ-confirmed enable per protected-path glob (gradual rollout).
- Test coverage: blocking with structured remediation message; matched-glob enforcement.

**Slice 3 — Remediation Surface**
- Structured remediation messages cite (a) failed assertion, (b) the spec it lives on, (c) the change diff that violated it, (d) recommended fix vocabulary.
- Test coverage: remediation message includes all 4 elements for each assertion subtype.

**Slice 4 — Codex-Side Parity**
- Equivalent gate in `.codex/hooks/` for Codex-as-LO writes.
- Test coverage: parity test asserts both harnesses block identically on the same spec violation.

### Acceptance Criteria (umbrella; per-slice criteria deferred to per-slice proposals)

- AC1: For every protected path with at least one assertion, an applicable assertion-evaluation runs in the gate.
- AC2: Failed assertions produce structured remediation messages, not opaque blocks.
- AC3: The gate's advisory→blocking transition is per-glob and owner-controlled.
- AC4: Cross-harness parity (Claude + Codex) maintained.
- AC5: S347 Agent Red severance class would have been caught (regression check against historical drift).

### Out of Scope

- Spec-corpus distillation surface (WI-3402's deliverable; separate scoping).
- Docker isolation-validator (WI-3403's deliverable; separate scoping).
- Auto-discovery of new spec assertions during a session (deferred).

## Pre-Filing Preflight Subsection

Per `.claude/rules/file-bridge-protocol.md`. Re-run after this NEW entry is added to bridge/INDEX.md:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-mechanical-enforcement-gate-scoping
```

Expected: `preflight_passed: true`, `missing_required_specs: []`.

## Specification-Derived Verification Plan

| Spec | Verification (for this scoping proposal) |
|------|------------------------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `bridge/INDEX.md` contains `Document: gtkb-v1-mechanical-enforcement-gate-scoping` with `NEW: bridge/gtkb-v1-mechanical-enforcement-gate-scoping-001.md`. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Slice plan above includes test coverage per slice; the gate produces release-gate evidence by design. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` | The gate is the adoption-enforcement concretization for V1. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal carries all relevant specs in the Specification Links section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps every cited spec to verification evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Scoping artifact landed → per-slice implementation proposals → per-slice verification = full lifecycle chain. |

Verification commands (for the scoping artifact itself; future per-slice implementations have their own verification):

```text
test -f bridge/gtkb-v1-mechanical-enforcement-gate-scoping-001.md
grep -q "^Document: gtkb-v1-mechanical-enforcement-gate-scoping" bridge/INDEX.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-v1-mechanical-enforcement-gate-scoping
```

## Risk and Rollback

- **Risk:** Codex NO-GO on PAUTH-fit (analogous to WI-3380). Mitigation: this proposal cites `PAUTH-GTKB-V1-RELEASE-STRATEGY-001-V1-RELEASE-STRATEGY-SCOPING` minted with `--allowed-mutation bridge_proposal_authoring` — explicit cover for governance_review scoping.
- **Risk:** Slice plan turns out to be wrong shape after Slice 0 lands (e.g., assertion reader needs different surface than assumed). Mitigation: per-slice proposals can supersede this scoping's slice plan if VERIFIED owner-grilling decisions emerge during implementation.
- **Rollback:** The artifact is the scoping document itself. If owner rejects the slice plan at GO time, file REVISED-N or WITHDRAWN; no source mutation occurred so no rollback work.

## Bridge Filing (INDEX-Canonical)

After this file is written, an entry will be inserted at the top of `bridge/INDEX.md`:

```text
Document: gtkb-v1-mechanical-enforcement-gate-scoping
NEW: bridge/gtkb-v1-mechanical-enforcement-gate-scoping-001.md
```

## Recommended Commit Type

`docs(bridge):` — scoping proposal only, no source mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
