NEW

# gtkb-wi4902-harness-projection-parity-registry (Slice 1) — Harness Projection Parity Registry Repair

bridge_kind: prime_proposal
Document: gtkb-wi4902-harness-projection-parity-registry
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-29T08:19:26Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: 2026-06
author_model_configuration: Codex Desktop, approval_policy=never, cwd=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4902

target_paths: ["config/agent-control/harness-capability-registry.toml", "config/harness-parity/phase2-waivers.toml", ".cursor/skills/**", ".agent/skills/**", ".api-harness/skills/**", ".codex/skills/**", ".claude/skills/**", "platform_tests/scripts/test_check_harness_parity.py", "scripts/check_harness_parity.py"]

implementation_scope: config | skill_update | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/check_harness_parity.py --all --markdown` currently fails with
`MISSING: 99, PASS: 206`. The failures are concentrated in the Phase 2 projection
surface: Cursor lacks harness-specific skill registry entries, and
Antigravity/Codex/Cursor lack explicit shared hook/governance capability
entries even when a native, adapter, helper, or intentionally unsupported route
already exists.

This proposal authorizes the first WI-4902 implementation slice: repair the
canonical harness capability registry and projection/adapters so the parity
evaluator reports only true implementation gaps or typed waivers. It does not
change provider credentials, production dispatcher routing, durable role
assignments, or release-smoke topology. Those remain in WI-4903, WI-4904,
WI-4905, WI-4906, and WI-4885.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — Requires proposal, GO, implementation report, and verification for protected source/config/test changes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Requires this implementation proposal to cite the governing requirements before protected changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Requires the Project Authorization, Project, and Work Item headers above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Requires the implementation report to include spec-derived verification evidence.
- `GOV-STANDING-BACKLOG-001` — Requires durable tracking of strategic self-improvement and gap-filler work through MemBase, not scratchpads.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — Requires cross-harness enforcement/projection gaps to be explicitly evaluated and corrected or waived.

## Prior Deliberations

- `INTAKE-b4928376` — Intake: Bridge review eligibility is harness-agnostic; durable role is a fallback, not a review/verdict gate
- `INTAKE-97211546` — Intake: Harness registrar role assignment and independent review requirements
- `INTAKE-2ce995f2` — Intake: Enable bounded parallel cross-harness auto-dispatch (supersede binary same-role active-session suppression)
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — OpenRouter harness registry integration model
- `DELIB-S422-OR-FRAMEWORK-CHOICE` — OpenRouter harness runner framework selection
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — Owner directive creating the release-blocking Harness Parity Phase 2 project and bounded implementation authorization.

These records establish that bridge eligibility is harness-agnostic, harness
roles are registry-governed, provider harnesses are legitimate parity targets,
and the current owner directive requires practical Codex-baseline fungibility
with explicit waivers for impossible gaps. This slice differs from live
dispatch-readiness work: it repairs the registry/projection authority that the
parity evaluator reads.

## Owner Decisions / Input

No new owner decision is required before LO review. The project and bounded
implementation authorization already cite
`DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE`, and this slice stays
inside `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29`.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4902 already requires closing skill,
hook, command, and prompt projection gaps against the Phase 2 Codex baseline,
and the active project authorization includes `config`, `hook_upgrade`,
`skill_update`, `source`, and `test` mutation classes while preserving the
bridge GO and implementation-start gates.

## Cross-Harness Disposition

Applicable harnesses: Codex A, Claude B, Antigravity C, Ollama D, Cursor E,
OpenRouter F, and future registered harnesses.

- Claude B remains the canonical native skill/hook source where the registry
  already declares Claude-native surfaces.
- Codex A must remain the practical baseline and must have every Codex registry
  entry backed by a real native surface, adapter, helper route, unsupported
  state, or typed waiver.
- Cursor E must receive explicit registry/projection entries where actual
  `.cursor/` skills or governed fallbacks exist; missing Cursor support must
  remain visible until closed or waived.
- Antigravity C must receive explicit registry/projection entries only for
  feasible adapter/helper surfaces; native-hook limitations must be represented
  as unsupported/degraded/waived rather than hidden.
- Ollama D and OpenRouter F must retain their API-harness adapter entries and
  remain covered by provider-readiness WIs; this slice must not claim live
  provider dispatch health.
- Future harnesses are not silently passed; the evaluator must continue to
  report unclassified missing entries until a registry projection or typed
  waiver is added.

No owner-approved typed waiver is introduced by this proposal. If
implementation discovers an impossible parity gap, it must add a typed waiver
record under the Phase 2 waiver registry and cite the owner decision that
authorizes the waiver, or stop and return with a report if that decision is
missing.

## Spec-Derived Verification Plan

Implementation report must include:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --markdown
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --all --json
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity.py
```

Expected result: `check_harness_parity.py --all` no longer reports unclassified
`MISSING` registry/projection gaps. Any gap that cannot be closed by a real
surface must be represented by a typed waiver record or an explicit
unsupported/degraded registry state with test coverage showing the evaluator
does not hide it.

## Risk / Rollback

Main risk is papering over real harness asymmetry by marking missing surfaces as
present. Mitigation: every registry addition must point at an actual adapter,
native helper, hookless governed fallback, unsupported status, or typed waiver,
and the tests must include at least one negative case showing unwaived gaps
still fail. Rollback is a single commit reverting registry/projection/test
changes from this slice.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4902-harness-projection-parity-registry`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix — this repairs a release-blocking parity-registry/projection defect exposed
by the canonical parity checker.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
