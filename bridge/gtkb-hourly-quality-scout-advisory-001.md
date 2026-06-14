ADVISORY

bridge_kind: loyal_opposition_advisory
Document: gtkb-hourly-quality-scout-advisory
Version: 001
Author: Loyal Opposition Advisor (Antigravity, harness C)
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: a7257629-1f8f-4e1d-a5b4-42bbe2794c45
author_model: gemini-2.5-pro
Date: 2026-06-14 UTC

# GroundTruth-KB Hourly Quality Scout Advisory Report - 2026-06-14

This advisory report presents the findings from the read-only spot check conducted on 2026-06-14.

## Inspected Surfaces

- `bridge/INDEX.md`
- Workstation doctor configuration (`groundtruth-kb/templates/managed-artifacts.toml`)
- Active developed applications registry (`applications/` and `applications/registry.toml`)
- Legacy-root reference checks in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- Legacy-root patterns configuration (`config/governance/hygiene-sweep-patterns.toml`)

## Summary of Findings

1. **Finding 1 (P0/P1 - Multi-slot Occupancy / Partial Slot Registration):** Unregistered leftover test slot directories under `applications/` trigger doctor failures.
2. **Finding 2 (P1 - Config/Template hook drift):** Missing template hook scripts still declared as active in `managed-artifacts.toml`.
3. **Finding 3 (P1/P2 - Legacy-Root false positive):** `hygiene-sweep-patterns.toml` matches legacy-root path patterns because it is not whitelisted in `doctor.py`.

---

## Detailed Findings

### Finding 1: Leftover Test Slot Directories
- **Severity:** P0/P1
- **Claim:** Leftover test slot directories `_test_7450a0ff` and `_test_dca06e76` in `applications/` trigger P0 multi-slot occupancy checks and P1 partial registration failures.
- **Evidence:** `applications/_test_7450a0ff` and `applications/_test_dca06e76` directories contain untracked residue files (e.g. `groundtruth.db`, `MEMORY.md`), violating the platform's single active developed application design constraint.
- **Risk/Impact:** Prevents the workstation doctor check from succeeding cleanly, creating noisy diagnostic results.
- **Recommended Action:** Execute `gt application unregister _test_7450a0ff` and `gt application unregister _test_dca06e76` (or delete the directories manually and remove entries from registry if needed).
- **Owner Decision Needed:** No.

### Finding 2: Config/Template Drift for Hooks
- **Severity:** P1
- **Claim:** Hook scripts `turn-marker.py` and `delib-preflight-gate.py` were deleted from templates, but remain defined as active in `managed-artifacts.toml`.
- **Evidence:** `doctor` fails reporting missing hook files in `.claude/hooks/`. Running `gt project upgrade --apply` cannot restore them since their template source files do not exist under `groundtruth-kb/templates/hooks/`.
- **Risk/Impact:** Permanent workstation doctor failure. Operators are instructed to run upgrade commands that cannot succeed.
- **Recommended Action:** Remove `hook.turn-marker`, `hook.delib-preflight-gate`, and their settings registration definitions from `groundtruth-kb/templates/managed-artifacts.toml`.
- **Owner Decision Needed:** No.

### Finding 3: Legacy-Root Reference False Positive
- **Severity:** P1/P2
- **Claim:** The legacy-root path reference check fails on `config/governance/hygiene-sweep-patterns.toml` because it defines patterns containing `E:\Claude-Playground` paths for sweep checks.
- **Evidence:** `doctor` fails with:
  - `[FAIL] Active control surface references retired E:\Claude-Playground archive root: config/governance/hygiene-sweep-patterns.toml:200, config/governance/hygiene-sweep-patterns.toml:213, config/governance/hygiene-sweep-patterns.toml:214`
- **Risk/Impact:** Creates false-positive doctor failures for configuration files that naturally define the legacy paths for matching patterns, obscuring real issues in active scripts.
- **Recommended Action:** Add `"hygiene-sweep-patterns.toml"` to the `_LEGACY_ROOT_PATTERN_SCRIPT_NAMES` (or rename to file names) whitelist in `doctor.py`.
- **Owner Decision Needed:** No.

---

## Recommended Prime Builder Disposition

Convert all three findings to implementation proposals for Prime Builder action in upcoming sessions.
