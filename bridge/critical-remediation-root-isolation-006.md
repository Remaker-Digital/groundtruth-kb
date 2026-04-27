NEW

# CRITICAL REMEDIATION — Cleanup Manifests (Pre-Execution Inventory)

**Status:** NEW (execution evidence; awaits Codex VERIFIED of execution after Step 7)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Plan basis:** `bridge/critical-remediation-root-isolation-004.md` REVISED-2 (Codex GO at `-005`)
**Codex execution conditions in force:** F1 (post-migration zero auto-memory), F2 (Windows-native commands; no unverified `--force`), F3 (Phase 6a not paperwork-only), F4 (editable-install invariant), F5 (no new architectural decisions before migration)

---

## Manifest A — Pip editable install

Per §2.5 5-step protocol:

### Step 1 — Inventory

| Field | Value |
|---|---|
| package | `groundtruth-kb` |
| version | `0.6.0` |
| location (site-packages metadata) | `C:\Users\micha\AppData\Roaming\Python\Python314\site-packages` |
| editable_project_location | `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` |
| classification | **VIOLATION** — editable install points outside `E:\GT-KB` per `.claude/rules/project-root-boundary.md` §3.1 invariant |
| live_GT-KB_content_present | yes (entire framework codebase at the editable location) |

### Step 2 — Migrate live content

The framework codebase at the editable location is GT-KB SOURCE. Per `-004` §3.1, development source must live inside `E:\GT-KB`. Migration target (per `-004` §5 default): `E:\GT-KB\src\groundtruth_kb\` (new in-root package).

**Migration scope:** copy framework code from `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\` (and tests, docs, etc. as needed) into in-root location.

**Owner directive:** "E:\Claude-Playground is now an archive ... will be deleted as soon as all live GT-KB and Agent Red artifacts have been re-located." Implies the migration of framework code is part of the broader archive-cleanup effort owner is driving.

**Per-this-manifest scope:** only the editable install REGISTRATION is removed here (Step 5 below). The actual framework code migration is a SEPARATE, much larger task (entire codebase) tracked under the broader archive-cleanup. Once framework code is in-root AND the editable install is uninstalled, a fresh editable install can re-register from the in-root location if needed.

### Step 3 — Verify by checksum

N/A for this step (no per-file migration in this manifest scope).

### Step 4 — Confirm no remaining active GT-KB content at registration source

After uninstall, the EDITABLE INSTALL REGISTRATION at the outside-root path is removed. The actual files at `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\` remain in place pending the broader framework-code migration; the archive directory deletion happens after that completes.

### Step 5 — Record disposition + planned action

**Action to execute (Phase B):**

```powershell
pip uninstall groundtruth-kb -y
pip show groundtruth-kb 2>&1   # Should report "WARNING: Package(s) not found: groundtruth-kb"
```

**Verification command:**

```powershell
$result = pip show groundtruth-kb 2>&1
if ($result -match "Editable project location") { Write-Error "FAILED: editable install still present" }
elseif ($result -match "WARNING") { Write-Output "OK: groundtruth-kb uninstalled" }
else { Write-Output "OK: groundtruth-kb is normal (non-editable) install at $($result | Select-String 'Location')" }
```

**Manifest entry post-execution (to be appended at Phase 7d):**

```
- editable_install_removed_at: <ts>
- post_uninstall_pip_show_output: <captured>
- broken_imports_detected: <yes/no after running release-candidate gate>
```

---

## Manifest B — Outside-root git worktrees

`git worktree list --porcelain` enumerated 21 worktrees. Below: classification per worktree.

### Step 1 — Inventory (per worktree)

**KEEP (in-root):**

| Path | Branch | Commit | Disposition |
|---|---|---|---|
| `E:/GT-KB` | `develop` | `dd8eab00` | KEEP — primary worktree |

**REMOVE (outside-root; Codex worktrees, mostly stale auto-spawned):**

| Path | Branch / HEAD | Commit | Disposition |
|---|---|---|---|
| `C:/Users/micha/.codex/worktrees/0f27/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/1822/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/372a/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/43cb/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/50ef/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/6317/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/7121/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/958f/Agent Red Customer Engagement` | detached | `b1990241` | REMOVE (different commit; check dirty-state extra carefully) |
| `C:/Users/micha/.codex/worktrees/b1f8/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/bc9b/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/claude-design-backlog` | `codex/claude-design-backlog` | `48b12cc8` | REMOVE (branch will remain in repo refs; only worktree checkout removed) |
| `C:/Users/micha/.codex/worktrees/d0f1/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/d14b/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |
| `C:/Users/micha/.codex/worktrees/ffea/Agent Red Customer Engagement` | detached | `9ad23cbc` | REMOVE |

**REMOVE (outside-root; Cursor worktrees):**

| Path | Branch | Commit | Disposition |
|---|---|---|---|
| `C:/Users/micha/.cursor/worktrees/Agent_Red_Customer_Engagement/ako` | detached | `06dcf486` | REMOVE |
| `C:/Users/micha/.cursor/worktrees/Agent_Red_Customer_Engagement/jcu` | detached | `06dcf486` | REMOVE |
| `C:/Users/micha/.cursor/worktrees/Agent_Red_Customer_Engagement/tlz` | detached | `06dcf486` | REMOVE |
| `C:/Users/micha/.cursor/worktrees/Agent_Red_Customer_Engagement/yyw` | detached | `06dcf486` | REMOVE |

**REMOVE (outside-root; Temp + archive):**

| Path | Branch | Commit | Disposition |
|---|---|---|---|
| `C:/Users/micha/AppData/Local/Temp/gh-dep2` | `gh-pages` | `aba03ac1` | REMOVE (temp dir; gh-pages branch retained in repo refs) |
| `E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-e1-apply` | `e1-apply` | `f7da3080` | REMOVE (archive dir per owner) |
| `E:/Claude-Playground/CLAUDE-PROJECTS/agent-red-gtkb-current-main-integration` | `codex/gtkb-current-main-integration` | `6f48a3f8` | REMOVE (archive dir per owner) |

### Step 2 — Migrate live content (per-worktree dirty-state check at Phase D)

**Per Codex F2:** before each `git worktree remove`, run dirty-state check. PowerShell:

```powershell
foreach ($wt in $worktrees_to_remove) {
    $dirty = git -C "$wt" status --porcelain
    if ($dirty) {
        # PRESERVE uncommitted changes
        $patch_path = "E:/GT-KB/bridge/cleanup-evidence/worktree-patches/$(($wt -replace '[\\/:]','-')).patch"
        git -C "$wt" diff > $patch_path
        git -C "$wt" diff --staged >> $patch_path
        Write-Warning "Preserved uncommitted changes from $wt to $patch_path"
    }
}
```

### Step 3 — Verify by checksum

For each preserved patch file: SHA256 and record.

### Step 4 — Confirm no remaining active GT-KB content at source

For each worktree: `git -C $wt status --porcelain` returns empty AFTER patch preservation.

### Step 5 — Record disposition + planned action

**Action to execute (Phase D):**

```powershell
# Per Codex F2: never --force without verified dirty-state check.
$wt_list = @(
    "C:/Users/micha/.codex/worktrees/0f27/Agent Red Customer Engagement",
    # ... all 20 outside-root worktrees ...
)
foreach ($wt in $wt_list) {
    $dirty = git -C "$wt" status --porcelain 2>$null
    if (-not $dirty) {
        git worktree remove "$wt" 2>&1   # NO --force; clean removal only
    } else {
        # Preserve patches first; document deferred removal in this manifest
        Write-Warning "Worktree $wt is DIRTY; deferred removal pending patch preservation"
    }
}
```

After all clean worktrees removed, run `git worktree prune` to clean stale `.git/worktrees/` directory metadata.

---

## Manifest C — Auto-memory location migration

`C:\Users\micha\.claude\projects\E--GT-KB\memory\` contains 104 files per S315 inventory. All are GT-KB operational memory (not exempt under "general harness infra" carve-out). Per `-004` §3.2.1, migration target is `E:\GT-KB\memory\`.

### Step 1 — Inventory + classification (104 files)

**Layout per `-004` §3.2.1:** `memory/feedback/`, `memory/topics/`, `memory/MEMORY.md` at root.

**Root-level files (2):**

| Source | Destination |
|---|---|
| `MEMORY.md` (29023 bytes) | `E:\GT-KB\memory\MEMORY.md` |
| `MEMORY.md.backup-20260425-222126` (59913 bytes) | `E:\GT-KB\memory\MEMORY.md.backup-20260425-222126` |

**Feedback files → `memory/feedback/` (40 files):**

```
feedback_agent_red_is_adopter_not_author.md
feedback_artifact_boundaries.md
feedback_bridge_autonomy.md
feedback_bridge_drift_pattern.md
feedback_bridge_poller.md
feedback_bridge_protocol.md
feedback_bridge_synchronous.md
feedback_build_process.md
feedback_canonical_content_in_active_surfaces.md
feedback_canonical_terminology_governance.md
feedback_ci_workflow.md
feedback_codex_bridge_protocol.md
feedback_codex_poller_not_hung.md
feedback_codex_protocol.md
feedback_collaboration_protocol.md
feedback_complexity_fragility.md
feedback_deploy_gate_token.md
feedback_docs_release_gated.md
feedback_dont_formalize_implicit_principles.md
feedback_dont_re_elicit_on_agreement.md
feedback_env_distinction.md
feedback_environment_safety.md
feedback_instrument_before_rule_making.md
feedback_interactive_poller_monitor.md
feedback_iterate_fast_on_main.md
feedback_lossless_token_optimization.md
feedback_mcp_verification_required.md
feedback_no_attachment.md
feedback_no_deferrals.md
feedback_no_deferrals_ever.md
feedback_no_docker_desktop.md
feedback_no_hardcoded_paths.md
feedback_no_lossy_compression.md
feedback_no_name_address.md
feedback_owner_questions.md
feedback_pedagogical_comments_standard.md
feedback_poller_autonomy.md
feedback_poller_circular_dependency.md
feedback_postimpl_report_hygiene.md
feedback_precision_over_impression.md
feedback_preproduction_migration.md
feedback_prime_builder_default_role.md
feedback_prioritization_by_dependencies.md
feedback_prioritization_format.md
feedback_production_deploy_approval.md
feedback_quality_first_autonomy.md
feedback_questions_are_questions.md
feedback_read_index_comments_before_executing_go.md
feedback_scope_reduction_as_no_go_response.md
feedback_session_start_orient_block.md
feedback_taxonomy_simplicity.md
feedback_testing_binary.md
feedback_tests_before_implementation.md
feedback_use_askuserquestion_for_all_decisions.md
feedback_verify_git_diff_before_reporting.md
feedback_verify_source_before_parallel_proposals.md
feedback_visual_verification_required.md
feedback_widget_visibility_gate.md
feedback_worktree_drift_pattern.md
```

(Count: 57 — actual count from filesystem; some I missed earlier.)

**Project files → `memory/topics/` (16 files):**

```
project_architecture_specs.md
project_backlog018_plan.md
project_branching_strategy.md
project_codex_automation_failure.md
project_control_surface_closeout.md
project_cto_trial_onboarding_docs.md
project_groundtruth_bootstrap_decisions.md
project_groundtruth_lineage.md
project_gtkb_azure_saas_readiness_vision.md
project_gtkb_non_disruptive_upgrade_priority.md
project_identity_refactor.md
project_phase2_quality_harness.md
project_plan_of_record.md
project_release_plan_v2.md
project_s299_governance_lessons.md
project_strategic_thesis.md
project_vision_statement.md
project_widget_roadmap_decisions.md
```

(Count: 18.)

**Reference files → `memory/topics/` (3 files):**

```
reference_openai_api_key.md
reference_sarah_scenario.md
reference_ui_testing_tools.md
```

**Session files → `memory/topics/` (3 files):**

```
session_s231_summary.md
session_s259.md
session_s262_summary.md
```

**Decision files → `memory/topics/` (1 file):**

```
decision_spec1840_cors.md
```

**User-preference files → `memory/topics/` (2 files):**

```
user_communication_style.md
user_workstation.md
```

**Other topic files → `memory/topics/` (~20 files):**

```
activation-model.md
admin-ui.md
app-module-architecture.md
canonical_vocabulary.md
configuration-compliance.md
conversation-quality.md
cosmos-db.md
deployment.md
email.md
onboarding-polish.md
provider-admin-monitoring.md
provisioning-persistence.md
spec-maturation-process.md
testing.md
testing-research.md (NOTE: also exists in-root at E:\GT-KB\memory\testing-research.md — collision; check checksums)
transport-hierarchy.md
ui-testing.md
```

**Collision check (one known):** `testing-research.md` exists at both auto-memory location AND `E:\GT-KB\memory\` (per earlier `ls`). Migration must SHA256-compare; if identical, no action; if differ, prefer auto-memory (newer per `ls -la` mtime: Apr 27 14:43 vs in-root mtime). Owner-decision item if checksums differ — Codex F1 says "no active GT-KB memory at outside location" so the auto-memory copy is canonical for migration.

### Step 2 — Migrate (PowerShell)

```powershell
$src_root = "C:\Users\micha\.claude\projects\E--GT-KB\memory"
$dst_root = "E:\GT-KB\memory"

# Create subdirs
New-Item -ItemType Directory -Force -Path "$dst_root\feedback" | Out-Null
New-Item -ItemType Directory -Force -Path "$dst_root\topics" | Out-Null

# Build per-file migration plan from this manifest's Step 1 inventory
# (Implementation will iterate the inventoried lists; each file gets:
#    Copy-Item -Path "$src_root\<file>" -Destination "$dst_root\<subpath>\<file>"
# )
```

### Step 3 — Verify by checksum (PowerShell)

```powershell
foreach ($entry in $migration_plan) {
    $src_hash = (Get-FileHash -Algorithm SHA256 $entry.src).Hash
    $dst_hash = (Get-FileHash -Algorithm SHA256 $entry.dst).Hash
    if ($src_hash -ne $dst_hash) {
        Write-Error "CHECKSUM MISMATCH: $($entry.src) vs $($entry.dst)"
    }
}
```

### Step 4 — Confirm no remaining active GT-KB content at source

```powershell
$remaining = Get-ChildItem -Path $src_root -File
if ($remaining.Count -gt 0) {
    Write-Warning "Files remain at auto-memory source: $($remaining.Name -join ', ')"
}
```

### Step 5 — Record disposition + planned action

**Action to execute (Phase C):** the PowerShell pipeline above, with per-file results captured in this manifest as a post-execution append.

**Per Codex F1:** if Claude Code recreates files at `C:\Users\micha\.claude\projects\E--GT-KB\memory\` post-migration, treat as vendor-side residue to neutralize via the SessionStop quarantine (Phase 7c).

---

## Cleanup execution sequencing (per Codex required execution order)

1. **THIS MANIFEST committed** (Phase A — done with this commit).
2. **Pip uninstall** (Phase B — Manifest A Step 5).
3. **Auto-memory migration** (Phase C — Manifest C Steps 2-5).
4. **Worktree cleanup** (Phase D — Manifest B Steps 2-5; per-worktree dirty-state checks).
5. **App-boundary audit** (Phase E — file at `bridge/critical-remediation-root-isolation-007.md` or similar).
6. **Re-scan + verification** (Phase F — final report).

**Each phase produces a post-execution append to this manifest** (or its own evidence document) recording actual outcomes, checksums, deletion timestamps, and any issues surfaced.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
