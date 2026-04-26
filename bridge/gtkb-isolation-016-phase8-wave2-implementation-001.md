NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 — Sub-Script Implementation (Scoping Bridge)

**Status:** NEW (scoping bridge awaiting Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-ISOLATION-016
**Bridge kind:** implementation_scoping (Wave 2 lays out 11-sub-script delivery plan)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-014.md` (GO scoping)
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md` (VERIFIED Wave 1)
**Owner pre-approvals (2026-04-26):**
- §3.3: Sandbox dir, never becomes target child root (clean-room)
- §3.5: Clone with history filter (Agent Red commits only)

bridge_kind: implementation_scoping
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: rehearsal-driver + 11-sub-script-bodies + manifest

---

## 1. Owner Decisions Recorded (2026-04-26)

### 1.1 §3.3 — Rehearsal output location → **sandbox**

Owner choice: separate sandbox directory that never becomes the target child root. Clean-room rehearsal: each run produces preview output in a throwaway location. Cutover (`GTKB-ISOLATION-018`) re-runs against the chosen target.

**Concrete sandbox path:** `C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}/` (mirrors the recovery-workspace pattern from S311 KB recovery).

Rationale: outside Drive sync (per S311 incident lessons), outside the GT-KB tree (no contamination), per-run timestamped (multiple rehearsal runs don't collide).

**Manifest update:** `output_dir = "C:/temp/agent-red-rehearsal/"` (run-specific timestamp appended at runtime by driver).

### 1.2 §3.5 — Git strategy → **clone with history filter**

Owner choice: extract Agent Red commits into a fresh repo at the target child root using `git filter-repo` (preferred) or `git subtree split`. Preserves Agent Red authorship/blame; rewrites SHAs (acceptable trade-off).

**Concrete approach:** use `git filter-repo --path applications/Agent_Red --path-rename applications/Agent_Red:` to produce a repo whose root is the Agent_Red sub-tree, with only commits that touched that path. Run this once at the target child root creation point; re-runs during rehearsal use the prior result as cache.

**Manifest update:** `git_strategy = "clone_with_history_filter"` plus a new `git_filter_command` field documenting the exact command.

**Pre-condition:** Agent Red files are not yet under `applications/Agent_Red/` in the legacy root. The current state has Agent Red files mixed at the legacy root. The history-filter approach requires either (a) first moving Agent Red files INTO `applications/Agent_Red/` in the legacy root via a Phase 7-Slice-2 work-subject migration, or (b) using a `--path` list enumerating Agent Red's actual current paths and `--path-rename` to map each to the new namespace. Option (b) is what Wave 2 will implement (Phase 7 Slice 2 is unblocked-but-future per work_list row 2 note).

## 2. Sub-Script Inventory (11 lanes per Phase 8 plan)

| # | Module | Purpose | Depends on |
|---|---|---|---|
| 1 | `_inventory.py` | Walk legacy root; build complete file/dir inventory with sizes, hashes, mtimes | (none — leaf) |
| 2 | `_path_rewrite.py` | Apply path rewriting rules from manifest authority matrix | inventory |
| 3 | `_ci_inventory.py` | Inventory CI workflow files; compute path-rewrite preview | inventory |
| 4 | `_membase_export.py` | Export MemBase / KB content to portable form | inventory |
| 5 | `_chromadb_regen.py` | Regenerate ChromaDB at sandbox location | inventory + membase |
| 6 | `_dashboard_regen.py` | Regenerate dashboard data + reports against sandbox | inventory + chromadb |
| 7 | `_bridge_split.py` | Split bridge files between framework / adopter ownership | inventory |
| 8 | `_backlog_split.py` | Split backlog between framework / adopter ownership | inventory |
| 9 | `_release_readiness_split.py` | Split release-readiness records | inventory |
| 10 | `_production_effects.py` | Document production-runtime effects (config, secrets, env vars) | inventory |
| 11 | `_rollback.py` | Generate rollback evidence for cutover failure scenarios | all-of-above |

## 3. Implementation Sequence (per dependency graph)

**Stage A — Independent / leaf (parallel-safe):** `_inventory.py` only. Produces inventory.json that all others read.

**Stage B — Inventory consumers (parallel-safe after Stage A):**
- `_path_rewrite.py`
- `_ci_inventory.py`
- `_membase_export.py`
- `_bridge_split.py`
- `_backlog_split.py`
- `_release_readiness_split.py`
- `_production_effects.py`

**Stage C — Multi-source consumers (sequential after Stage B):**
- `_chromadb_regen.py` (needs inventory + membase output)
- `_dashboard_regen.py` (needs inventory + chromadb output)

**Stage D — Cross-cutting (last):** `_rollback.py` (needs all-of-above to know what would be undone)

**Implementation bridge schedule:** one bridge per sub-script (or per dependency-cluster if the proposal is short). Wave 2 sub-bridges will use the naming pattern `gtkb-isolation-016-phase8-wave2-{module-name}-implementation-001.md`. Anticipated 4-6 implementation bridges total (some clusters bundled).

## 4. Common Contracts (apply to all sub-scripts)

### 4.1 Sub-script signature

```python
# scripts/rehearse/_inventory.py (and peers)
from rehearse._common import ManifestError, validate_target_root
from pathlib import Path
import json

def run(manifest: dict, output_dir: Path, *, dry_run: bool = False) -> dict:
    """Execute this sub-script's rehearsal lane.

    Returns a result dict with at minimum:
        {
            "status": "ok" | "error" | "skipped",
            "output_files": [list of Path objects written],
            "metrics": {...},
            "warnings": [list of strings],
        }
    Never raises for known failure modes; returns status='error' instead.
    Raises only for programming bugs (assertion violations, etc.).
    """
```

### 4.2 Output directory layout

Each sub-script writes under `{output_dir}/{module_short_name}/`:
- `result.json` — structured result returned by `run()`
- `<module-specific files>` — per the module's purpose (e.g., `inventory.json` for `_inventory`)

### 4.3 Idempotency

Re-running the driver with the same `output_dir` overwrites prior output. No append behavior. `output_dir` is timestamped per-run, so collisions are avoided in practice.

### 4.4 Read-only on legacy root

Sub-scripts MUST NOT write to anywhere under `LEGACY_ROOT` (`E:/GT-KB/`). Enforced via `validate_target_root()` before any write. Violation raises `TargetRootError` and aborts the entire rehearsal.

### 4.5 Driver dispatch wire-up

Wave 1 dispatch table at `scripts/rehearse_isolation.py` line ~37 maps CLI phase names to module paths. Wave 2 implementation populates each module's `run()` function. Driver invocation pattern (Wave 1 currently stubs):

```python
def _dispatch(phase_name: str, manifest: dict, output_dir: Path, dry_run: bool) -> dict:
    for cli_name, module_path, function_name in DISPATCH_TABLE:
        if cli_name == phase_name:
            mod = importlib.import_module(module_path)
            fn = getattr(mod, function_name)
            return fn(manifest, output_dir, dry_run=dry_run)
    raise ValueError(f"unknown phase: {phase_name}")
```

Wave 1 has the table; Wave 2 just lights up the implementations.

## 5. Manifest Update (lands in this scoping bridge's commit)

`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` updated to:

```toml
# Lines after the §3.3 / §3.5 OWNER DECISION REQUIRED comments:

# §3.3 owner decision 2026-04-26: sandbox path (clean-room rehearsal).
# Driver appends ISO timestamp at runtime: C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}/
output_dir = "C:/temp/agent-red-rehearsal"

# §3.5 owner decision 2026-04-26: clone with history filter.
git_strategy = "clone_with_history_filter"
git_filter_command = "git filter-repo --path <agent-red-paths> --path-rename <each-to-new-namespace>"

# §3.6 still pending (surfaces at Wave 3 verification matrix).
db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"
```

Plus the `[surface_treatments]` table populated from the Phase 1 authority matrix at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE-1-AUTHORITY-MATRIX.md`. The 16 surfaces from that matrix get explicit treatment per surface (preserve / rewrite-paths / split / regenerate).

## 6. Test Plan

### 6.1 Per-sub-script tests

Each sub-script implementation bridge creates its own test file at `tests/scripts/rehearse/test__{module}.py` covering:

- Happy-path execution against a fixture inventory
- Missing-input handling (returns status='error' not raise)
- Read-only-on-legacy-root enforcement (attempt to write to E:/GT-KB/ is rejected)
- Idempotency (re-running with same output produces same result.json modulo timestamps)

### 6.2 Driver-level tests

`tests/scripts/test_rehearse_isolation_driver_wave2.py` — covers:

- All 11 dispatch entries resolve to importable modules with `run()` functions
- `--phase all` invokes all 11 in dependency-correct order
- Sandbox `output_dir` is created with timestamp suffix; doesn't collide on repeat runs
- Manifest validation rejects `OWNER_DECISION_REQUIRED` placeholders (forces explicit values)

### 6.3 Integration test

`tests/scripts/test_rehearse_isolation_integration_wave2.py` — covers a full `--phase all` rehearsal against a fixture legacy-root tree (small synthetic). Asserts: all 11 sub-scripts complete; output_dir contains expected file structure; no writes to legacy root; result.json valid for each.

## 7. Files Changed

### 7.1 In this scoping bridge's commit
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-001.md` (this file, NEW)
- `bridge/INDEX.md` (entry insertion)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` (§3.3 / §3.5 values filled; surface_treatments populated)

### 7.2 In subsequent Wave 2 implementation bridges
- `scripts/rehearse/_inventory.py` (Stage A)
- `scripts/rehearse/_path_rewrite.py`, `_ci_inventory.py`, `_membase_export.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`, `_production_effects.py` (Stage B)
- `scripts/rehearse/_chromadb_regen.py`, `_dashboard_regen.py` (Stage C)
- `scripts/rehearse/_rollback.py` (Stage D)
- `scripts/rehearse_isolation.py` driver dispatch wire-up (replaces Wave 1 stub)
- 12 test files per §6

## 8. Out of Scope

- §3.6 (concurrent-session DB reconciliation) — surfaces at Wave 3 boundary, not Wave 2
- Phase 7 Slice 2 typed `work_subject.set` / `rollback` (re-opened at `gtkb-isolation-015-slice2-work-subject-set-002`; does not block Wave 2 per `-016-impl-005` §1.2)
- Actual cutover / migration execution — that's `GTKB-ISOLATION-018`
- Re-enabling Windows scheduled tasks — `S308` poller-halt directive simplified this away (manifest records inventory only)

## 9. Codex Review Asks

1. Confirm sandbox path `C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}/` is acceptable for the §3.3 "sandbox" choice (vs e.g. a path under user profile).
2. Confirm git filter-repo with `--path` enumeration is the right strategy given Agent Red files aren't yet under `applications/Agent_Red/` in the legacy root. Alternative: pre-stage an Agent Red move via Phase 7 Slice 2 first (more setup, simpler filter command).
3. Confirm dependency staging in §3 (Stage A→B→C→D) matches the actual data flow needed by each sub-script.
4. Confirm common contracts in §4 (signature, output layout, idempotency, read-only-on-legacy enforcement, driver dispatch wire-up) are the right shape.
5. Confirm test plan in §6 covers the rehearsal correctness properties.
6. Confirm splitting Wave 2 into 4-6 sub-bridges (per stage) is the right granularity vs one mega-bridge.
7. **GO / NO-GO** on Wave 2 scoping.

After GO, Prime files the first implementation bridge for Stage A (`_inventory.py`) and lights up sub-scripts in dependency order.

## 10. Decision Needed From Owner

None — owner pre-acks captured (§3.3 + §3.5) on 2026-04-26 unblock this scoping. §3.6 still pending but does not block Wave 2.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All
rights reserved.*
