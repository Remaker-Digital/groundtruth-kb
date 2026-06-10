# Implementation Proposal — Codex Skill-Loading Failure Cleanup (Slice 1)

bridge_kind: prime_proposal

## Summary

Inventory and repair (or remove) `.codex/skills/*/SKILL.md` files with malformed or missing YAML frontmatter that cause Codex worker startup errors. Extend `gt platform doctor` harness-parity check so "skill exists but cannot load" is a FAIL condition rather than silently passing.

## Background

Owner directive in S350 (2026-05-14) under the 6-point throughput improvement plan, point 5:

> "Clean up Codex skill-loading failures. The worker logs still show Codex startup errors for malformed or missing YAML frontmatter in several .codex/skills/*/SKILL.md files. Dispatch still works, but this slows worker startup and hides real failures in noise. Fix: repair or remove invalid Codex skill adapters, then extend harness parity checks so 'skill exists but cannot load' is a failure. Current parity says PASS: 60, but runtime logs show additional load-time drift."

Live signal: `harness-parity: pass (harness=claude, role=prime-builder, PASS=25)` per the S350 startup payload, plus the owner-reported Codex-side `PASS=60`. The PASS count does not include skill-load attempts; load failures at worker spawn time are non-blocking, surfacing only in logs.

## In-Root Placement Evidence

All target paths and runtime artifacts in-root under `E:\GT-KB`:

- `E:\GT-KB\.codex\skills\*\SKILL.md` — Codex skill files (inventory + repair targets).
- `E:\GT-KB\scripts\check_codex_hook_parity.py` (or successor) — parity check extended.
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\doctor.py` — doctor check extended.
- `E:\GT-KB\platform_tests\` — regression tests for the parity check upgrade.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths and runtime artifacts are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; worker startup health affects bridge throughput.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — Codex hook parity authority; this proposal extends the parity surface to skill-load health.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — skills are durable governance artifacts (advisory).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability across skill files + parity check (advisory).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — skill lifecycle: present → loadable → callable (advisory).
- `.claude/rules/bridge-essential.md` — bridge dispatch enablement; worker startup health is part of dispatch readiness.
- `.claude/rules/file-bridge-protocol.md` — bridge protocol invariants.

## Prior Deliberations

- `bridge/gtkb-codex-hook-parity-fallback-*` thread family — establishes the Codex parity surface this proposal extends.
- No prior deliberation specifically on Codex skill-load failure handling.

## Owner Decisions / Input

Owner directive in S350 (2026-05-14): "I would improve throughput in this order... 5. Clean up Codex skill-loading failures."

Owner directive in S350 (2026-05-14): "Please continue to parallelize work."

## Requirement Sufficiency

Existing requirements sufficient. The harness-parity contract at `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 is unchanged; this proposal extends the parity check's failure detection surface.

## target_paths

- `.codex/skills/*/SKILL.md` — files with malformed YAML repaired or removed (inventory determines per-file action).
- `scripts/check_codex_hook_parity.py` (or successor) — parity check extended to invoke a "skill load smoke" pass.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_codex_hook_parity` (or analogous) extended.
- `platform_tests/scripts/test_codex_skill_load_smoke.py` (new file) — regression tests.

## Implementation Plan

1. **Inventory phase**: enumerate all `.codex/skills/*/SKILL.md` files; attempt YAML frontmatter parse on each; record `(file_path, parse_status, error_message_if_any)` to a temporary inventory file.
2. **Triage phase**: for each parse-failed file, decide:
   - Repair: fix YAML if the skill is intended and the malformation is mechanical (missing `---`, indentation drift, unescaped colon).
   - Remove: delete if the skill is stale or duplicates a Claude-side skill with no Codex-specific behavior.
   - File a separate bridge thread: if the skill genuinely needs redesign (out of scope for this cleanup).
3. **Parity-check extension**: add a `_check_codex_skill_load_health` doctor check that:
   - Lists each `.codex/skills/*/SKILL.md`.
   - Validates YAML frontmatter parses cleanly.
   - Returns FAIL severity for any parse error (was previously silent).
4. **Regression tests**:
   - `test_skill_load_smoke_detects_missing_frontmatter`: fixture skill with no `---` block; assert doctor check FAILs.
   - `test_skill_load_smoke_detects_malformed_yaml`: fixture skill with invalid YAML; assert doctor check FAILs.
   - `test_skill_load_smoke_passes_on_valid_skill`: well-formed fixture; assert doctor check PASSes.

## Spec-to-Test Mapping

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 → all 3 regression tests (parity check now detects skill-load drift).
- `GOV-FILE-BRIDGE-AUTHORITY-001` → indirectly via worker startup health affecting bridge dispatch readiness.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → one test per assertion class.

## Risks

- **Inventory might find more failures than scope-budget allows**: large repair count could blow up the slice. *Mitigation:* triage phase explicitly classifies "repair vs remove vs separate thread"; this slice handles small mechanical repairs only; substantive redesigns spawn sibling threads.
- **Doctor FAIL could break CI**: existing CI pipelines may not handle a new FAIL condition gracefully. *Mitigation:* phase the change — add the check as WARN first, observe one cycle, then promote to FAIL. (Decision to be confirmed in Codex review; if WARN-first is preferred over immediate-FAIL, REVISED.)
- **Repaired skills might still have semantic issues beyond YAML**: this slice only addresses load-time YAML parse. *Mitigation:* semantic skill issues are scope-separate.

## Rollback

Revert inventory-driven file changes (git revert). Remove the new doctor check. Remove regression tests.

## Verification Procedure

1. Run `python -m pytest platform_tests/scripts/test_codex_skill_load_smoke.py -q --tb=short` — all 3 new tests pass.
2. Run `gt platform doctor` (or equivalent) — `_check_codex_skill_load_health` reports PASS after repairs.
3. Manual smoke: spawn a Codex worker subprocess; observe no skill-load errors in stderr.
4. Run preflights — both must pass.

## Acceptance Criteria

- All `.codex/skills/*/SKILL.md` files parse cleanly (YAML frontmatter loadable).
- `_check_codex_skill_load_health` exists and reports correctly.
- 3 regression tests pass.
- All preflights pass.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
