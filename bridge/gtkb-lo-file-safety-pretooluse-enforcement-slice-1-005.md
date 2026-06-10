REVISED

# Implementation Proposal - LO File-Safety PreToolUse Enforcement Slice 1 - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1
Version: 005
Responds to: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+
Source: WI-3308

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: WI-3308

target_paths: [".claude/hooks/lo-file-safety-gate.py", ".codex/gtkb-hooks/lo-file-safety-gate.cmd", ".codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py", "config/governance/lo-file-safety.toml", ".claude/settings.json", ".codex/hooks.json", "platform_tests/scripts/test_lo_file_safety_gate.py"]

## Revision Notes (-005 vs -003, addressing the -004 NO-GO)

The `-004` NO-GO on REVISED-1 raised exactly two findings. Each is addressed below; this revision also adds the project-linkage metadata lines that the `-001`/`-003` proposals predated.

- **F1 (P1) — Bridge INDEX exception remains broader than the audit-trail operation.** `-003` IP-1 step 5 and IP-2's `[bridge_operation]` block declared `bridge/INDEX.md` "always allowed", which the `-004` NO-GO correctly identifies as permitting LO to delete lines, reorder entries, edit unrelated threads, or change prior statuses. `-005` replaces the "always allowed" rule with an **append-only LO-status-line-insertion classifier**: an LO `Edit` to `bridge/INDEX.md` is allowed ONLY when the candidate diff is the insertion of exactly one valid LO status line (`GO`, `NO-GO`, `VERIFIED`, or `ADVISORY`) at the top of one matching live `Document:` entry's version list, with zero deletions, zero reorders, and zero changes to any other line. Any INDEX `Write` (full-file overwrite), any deletion, any reorder, any multi-line-status insertion, or any edit touching an unrelated entry is blocked. See § IP-1 step 5 and § IP-2 below. The existing "new bridge version file must not already exist" rule for `bridge/*.md` is kept unchanged.
- **F2 (P1) — Bash classifier still misses basic copy-based file mutation.** `-003`'s `_classify_bash_write_intent` listed `Copy-Item -Force`, `cp -f`, and `git checkout -- <path>` but missed plain `Copy-Item` (no `-Force`), the PowerShell aliases `cp` / `copy`, plain `cp`, and `git restore <path>`. `-005` treats `Copy-Item`, its aliases `cp` and `copy`, plain POSIX `cp`, all copy/overwrite forms, and `git restore` as write-intent signals **independent of any `-Force` flag** — consistent with the existing GT-KB precedent `scripts/implementation_start_gate.py:62-69` `MUTATING_COMMAND_RE`, which lists `copy-item` and `move-item` as mutating commands with no force-flag requirement. `-005` adds explicit regression tests for `Copy-Item source target`, `cp source target`, and `git restore -- <path>` against non-allow-listed paths under LO assignment. See § IP-1 step 4 and the test mapping.

No requirement-disambiguation finding was raised by the `-004` NO-GO; both findings are implementation-defect findings remediable through proposal revision without changing the requirement surface. There is no technical-scope expansion beyond the two findings; the seven `target_paths` are unchanged from `-003`.

## Summary

The §"Loyal Opposition File Safety Rule" in `.claude/rules/loyal-opposition.md` is currently rule-cited soft authority only. It states: "When operating as Loyal Opposition, do not delete or modify files you have not created without explicit approval from the owner (Mike)." The S350 incident (`DELIB-S350-CODEX-LO-FILE-SAFETY-VIOLATION`, rowid 2188) documented Codex (assigned LO per `harness-state/role-assignments.json`) editing `scripts/implementation_authorization.py` and other implementation files for Slice 3/4 of `GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE` without per-file owner approval. The rule fired no mechanical block.

This slice adds a Claude-Code-side PreToolUse `Write|Edit|MultiEdit|Bash` hook (`lo-file-safety-gate.py`) plus a Codex-side parity wrapper that:

1. Resolves the active harness role-set from `harness-state/role-assignments.json` via `scripts/harness_roles.py is_loyal_opposition`.
2. When the role-set contains `loyal-opposition` AND the target path is NOT in the LO-authoring allow-list (nor a permitted bridge operation), returns `{"decision": "block", "reason": "..."}` unless an owner-approval-packet path is supplied via env var (`GTKB_LO_FILE_SAFETY_APPROVAL_PACKET`) and that packet validates against the reconstructed post-edit content.
3. Returns the empty `{}` pass response when the role-set does not contain `loyal-opposition` (no contention with the Prime authority contract per `.claude/rules/prime-builder-role.md`).

## In-Root Placement Evidence

All `target_paths` are in-root under `E:\GT-KB`:

- `.claude/hooks/lo-file-safety-gate.py` — under `.claude/hooks/`, the canonical Claude hooks directory.
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`, `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` — under `.codex/gtkb-hooks/`, the canonical Codex hook-wrapper directory.
- `config/governance/lo-file-safety.toml` — under `config/governance/`, the canonical governance config directory.
- `.claude/settings.json`, `.codex/hooks.json` — repository-root harness settings files.
- `platform_tests/scripts/test_lo_file_safety_gate.py` — under `platform_tests/scripts/`, the active GT-KB platform test lane.

ADR-ISOLATION-APPLICATION-PLACEMENT-001 `CLAUSE-IN-ROOT` evidence: this hook is GT-KB platform infrastructure (governance enforcement of a `.claude/rules/` rule), not application code; placement under `.claude/`, `.codex/`, `config/governance/`, and `platform_tests/` is canonical for platform infrastructure. No path leaves `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; WI-3308 source spec. This proposal inserts a status line into `bridge/INDEX.md` at the top of the existing `gtkb-lo-file-safety-pretooluse-enforcement-slice-1` entry, and the F1 fix narrows the LO INDEX exception to exactly that append-only insertion operation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test mapping derived from linked specs; the Specification-Derived Verification Plan maps each finding and spec to tests.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex parity mandatory; live interception boundary per DELIB-1550 / DELIB-1551.
- `GOV-STANDING-BACKLOG-001` — WI-3308 backlog-authority source; this proposal is not a bulk operation (see Clause Scope Clarification).
- `GOV-ARTIFACT-APPROVAL-001` — approval-packet pathway pattern extended to LO file-system writes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; hook is platform infrastructure.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — rule promoted from text-only to artifact-tested mechanical enforcement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — surface rule-text-vs-mechanical-enforcement gaps.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — hook lifecycle: created, registered, regression-tested.
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (the rule being mechanically enforced); § "Reviewer-Evidence-Preparation vs Speculative Source Modification" (the boundary the allow-list encodes); § "Loyal Opposition KB-Write Approval-Packet Pathway" (parallel approval-packet contract reused here).
- `.claude/rules/file-bridge-protocol.md` § "Loyal Opposition Workflow" (LO inserts a verdict line at the top of the target entry — the exact operation the F1-narrowed classifier permits); § "Guardrails" (never delete bridge files; append-only audit trail; index is the source of truth for workflow state).
- `.claude/rules/codex-review-gate.md` (LO review obligations preserved by allow-listing new-version bridge file creation and append-only INDEX status-line insertion for verdict authoring).
- `.claude/rules/project-root-boundary.md` (allow-list paths and hook implementation are all in-root).

## Prior Deliberations

- `DELIB-2188` (S350 origin): "Codex (LO) violated `.claude/rules/loyal-opposition.md` file-safety rule by implementing Slice 3/4 source-code edits without per-file owner approval." Originating observation cited in WI-3308.
- `DELIB-1886` (VERIFIED): `gtkb-lo-file-safety-rule-clarification-001` bridge thread — clarified the rule's scope and added the "Reviewer-Evidence-Preparation vs Speculative Source Modification" subsection. This slice promotes that clarified rule to mechanical enforcement.
- `DELIB-1738` (S342): Codex NO-GO on `gtkb-pre-filing-preflight-hook` — establishes precedent that approval-packet exceptions must bind to post-edit content, not just to path + standalone hash. The `-003` F2 fix applied this precedent and is preserved here.
- `DELIB-1518` (S327): Loyal Opposition verification for the file-safety rule clarification — context for the rule-text surface this slice mechanically enforces.
- `DELIB-1551`, `DELIB-1550` (S337): empirical Codex Windows hook firing on CLI >= 0.128.0-alpha.1 — establishes that `.codex/hooks.json` IS a live interception boundary, justifying full Codex parity.
- `DELIB-1742`..`DELIB-1739` (S337-S338): Codex `bridge-compliance-gate` hook parity thread — proven `.cmd` wrapper + `-bash-adapter.py` pattern reused here.

No retrieved deliberation waives bridge audit-trail protection or basic shell write detection for a hook whose purpose is to mechanically enforce the Loyal Opposition file-safety rule; the `-005` revision tightens both per the `-004` NO-GO.

## Owner Decisions / Input

S350 owner direction: owner AUQ answer "Parallel research + serialized Writes now (Recommended)" authorized parallel research and serialized batch filing of priority backlog proposals (WI-3308 is `priority: high`). The work item WI-3308 is an active member of `PROJECT-GTKB-GOVERNANCE-HARDENING`, which is covered by the active project-scoped authorization `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` (owner decision `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`); that authorization's `included_work_item_ids` explicitly lists `WI-3308`. That project-scoped authorization is the owner-approval evidence for ordinary scoped source/test work on this WI.

Detected via: explicit S350 owner AUQ answer + the project authorization record. No new AskUserQuestion is requested by this revision; the `-004` NO-GO itself records "Decision needed from owner: None." Per-proposal Codex GO is still required before any implementation work begins; this proposal does not bypass the per-proposal review gate. The implementation-start authorization packet must be created per `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate" once Codex records GO on `-005`.

## Requirement Sufficiency

Existing requirements sufficient. Governing specs are unchanged from `-001`/`-003`: `GOV-FILE-BRIDGE-AUTHORITY-001` (WI-3308 source spec); `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (rule text being enforced); `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (parity obligation). The `-004` NO-GO raised no requirement-disambiguation finding; both findings are implementation-defect findings remediable through proposal revision without changing the requirement surface. No new or revised requirement or specification is created by this proposal.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk operation against the standing backlog or work-items inventory. It touches a single backlog item (WI-3308) and produces a focused, bounded inventory of seven new/modified files: one Claude hook, one Codex `.cmd` wrapper, one Codex `-bash-adapter.py` bridge, one TOML config, two harness settings edits, one platform test module. The proposal does not iterate over `work_items`, does not bulk-mutate backlog entries, does not bulk-promote specs, and does not run inventory-wide operations.

Evidence tokens for `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause-preflight bulk-ops false-positive avoidance: `inventory` (the inventory of target_paths is enumerated above and bounded to seven artifacts); `formal-artifact-approval` (no formal-artifact-approval packet is required by this slice because the proposal touches only hook infrastructure under `.claude/hooks/`, `.codex/gtkb-hooks/`, `config/governance/`, and harness settings, none of which are protected narrative-artifact paths per `config/governance/narrative-artifact-approval.toml`; the implementation-start authorization packet IS required once Codex records GO).

## Proposed Scope

### IP-1: Claude-side hook with full mutation surface, post-edit reconstruction, and narrowed bridge classifier

`.claude/hooks/lo-file-safety-gate.py`. Behavior:

1. Read stdin JSON. If `tool_name` not in `{"Write", "Edit", "MultiEdit", "Bash"}`, emit `{}` (pass).
2. Resolve `_project_root()` from `CLAUDE_PROJECT_DIR` env or `cwd`.
3. Load `harness-state/role-assignments.json` via `scripts.harness_roles.load_role_assignments`. Resolve active harness ID; call `scripts.harness_roles.is_loyal_opposition(record)`. If False, emit `{}`.
4. Per `tool_name`, normalize a list of `(rel_path, candidate_post_edit_content_or_none)` target tuples:
   - `Write`: single tuple `(file_path, tool_input.content)`.
   - `Edit`: read current file content; apply `old_string` -> `new_string` substitution (respecting `replace_all`); produce candidate post-edit content; tuple `(file_path, candidate)`.
   - `MultiEdit`: read current file content; apply each edit sequentially; tuple `(file_path, candidate_after_all_edits)`.
   - `Bash`: invoke `_classify_bash_write_intent(command)` (see § Bash Write-Intent Classifier below) which emits zero-or-more `(rel_path, None)` tuples, or the single sentinel tuple `("<opaque-bash>", None)` when the command contains opaque substitution that could mask write targets.
5. For each tuple, load the allow-list from `config/governance/lo-file-safety.toml`. Classification (the F1 fix is the bridge-operation sub-step):
   - **Path-prefix allow** (dropbox, LO log, `KNOWLEDGE-PROJECT.md`, `MEMORY.md`): allow regardless of operation.
   - **Bridge-operation classifier (F1-narrowed):**
     - `bridge/INDEX.md` is NOT blanket-allowed. An LO mutation of `bridge/INDEX.md` is allowed ONLY when ALL of these hold:
       1. The tool is `Edit` or `MultiEdit` (a `Write` full-file overwrite of `bridge/INDEX.md` is always blocked — a full overwrite cannot be proven append-only).
       2. The candidate post-edit content is computed by reconstruction (step 4) and diffed line-by-line against the current `bridge/INDEX.md`.
       3. The diff is purely additive: exactly one line is inserted, zero lines are deleted, and zero existing lines are modified or reordered.
       4. The single inserted line is a valid LO status line — it matches `^(GO|NO-GO|VERIFIED|ADVISORY): bridge/[A-Za-z0-9._-]+-\d+\.md\s*$`.
       5. The inserted line sits at the top of exactly one `Document:` entry's version list (immediately after that entry's `Document:` header line), and that entry exists in the current INDEX. No other `Document:` entry's lines are touched.
       Any deletion, any reorder, any change to an unrelated entry, any multi-line insertion, an inserted line whose status is not an LO status (`NEW`/`REVISED` are Prime-set and are NOT permitted via this LO classifier), or an inserted line that is not at the top of its entry's version list -> blocked.
     - `bridge/*.md` other than `bridge/INDEX.md`: allowed ONLY if the file does not currently exist (creating a new versioned verdict/advisory file). Editing or overwriting an existing `bridge/*.md` file is always blocked under LO role (preserves the append-only audit trail per `.claude/rules/file-bridge-protocol.md` § Guardrails).
   - **Anything else:** require the approval-packet exception (step 6).
6. **Approval-packet exception:** load `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET` env var. If absent, block. Validate required fields per the proven `narrative-artifact-approval-gate.py` schema (`artifact_type='lo_file_safety_authorization'`, `target_path`, `full_content`, `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `approved_by='owner'`). Verify `Path(packet.target_path).as_posix() == rel_path`. Verify `sha256(packet.full_content) == packet.full_content_sha256`. Verify `sha256(candidate_post_edit_content) == packet.full_content_sha256` for `Write|Edit|MultiEdit` (the `-003` F2 fix, preserved). For `Bash`-write tuples (candidate content is `None`) the packet exception does NOT apply — Bash writes to non-allow-listed paths under LO role are always blocked unless the operation is moved through `Write|Edit|MultiEdit` where post-edit reconstruction works. The `<opaque-bash>` sentinel always blocks.
7. If all checks pass, emit `{}`. Otherwise emit `{"decision": "block", "reason": "..."}` with a reason identifying the failed check and the violated rule.

#### Bash Write-Intent Classifier (F2 fix)

`_classify_bash_write_intent(command)` detects write intent and emits `(rel_path, None)` tuples. Detected signals — each is a write-intent signal **independent of any `-Force` / `-f` flag**, consistent with the `MUTATING_COMMAND_RE` precedent at `scripts/implementation_start_gate.py:62-69`:

- Shell output redirects: `> file`, `>> file` (excluding null-sink redirects to `/dev/null`, `$null`, `NUL`).
- `tee file`, PowerShell `Tee-Object`.
- Heredoc writes: `cat > file <<EOF ... EOF`.
- PowerShell write cmdlets: `Set-Content`, `Out-File`, `Add-Content`.
- File-create: `New-Item` (file type), POSIX `touch`.
- Destructive / move: `Remove-Item`, `rm`, `Move-Item`, `mv`.
- **Copy forms (the F2 addition) — independent of any force flag:** `Copy-Item` (with or without `-Force`), the PowerShell aliases `cp` and `copy` for `Copy-Item`, plain POSIX `cp` (with or without `-f`).
- **Git working-tree restore (the F2 addition):** `git checkout -- <path>` AND `git restore <path>` / `git restore -- <path>` / `git restore --source ... <path>` — all treated as write-intent independent of flags.
- Opaque substitution: if the command contains `$(...)`, backticks, or indirect variable expansion that could mask write targets, the classifier emits the single `("<opaque-bash>", None)` sentinel which fails closed at step 6 (conservative bias: ambiguous shells block under LO; the Prime role is unaffected).

The classifier extracts the destination path token for copy/move/restore forms (the path that is being written/overwritten — for `Copy-Item src dst` and `cp src dst` that is `dst`; for `git restore <path>` that is `<path>`) and emits a `(dst_rel_path, None)` tuple per destination.

### IP-2: Narrowed allow-list configuration (F1 fix)

`config/governance/lo-file-safety.toml`:

```toml
[[allow]]
description = "LO insight-report authoring dropbox"
patterns = ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**"]

[[allow]]
description = "LO running context files"
patterns = ["independent-progress-assessments/LOYAL-OPPOSITION-LOG.md", "independent-progress-assessments/KNOWLEDGE-PROJECT.md"]

[[allow]]
description = "MEMORY.md operational notepad"
patterns = ["memory/MEMORY.md"]

[bridge_operation]
description = "Append-only LO status-line insertion into bridge/INDEX.md, and new-version verdict/advisory file creation"
index_path = "bridge/INDEX.md"
# bridge/INDEX.md edits are NOT blanket-allowed. They are permitted only when the
# candidate diff is a single append-only insertion of one valid LO status line at
# the top of one matching Document: entry. Enforced by the hook's diff classifier.
index_lo_status_line_re = '^(GO|NO-GO|VERIFIED|ADVISORY): bridge/[A-Za-z0-9._-]+-\d+\.md\s*$'
index_require_append_only_single_line = true
index_deny_full_write = true
# Other bridge/*.md files: a new versioned verdict/advisory file may be created
# (must not already exist); editing/overwriting an existing bridge/*.md is denied.
new_version_glob = "bridge/*.md"
deny_edit_existing = true

[hook_detection]
env_var_names = ["GTKB_LO_FILE_SAFETY_APPROVAL_PACKET"]
```

The `[bridge_operation]` block encodes the F1 fix: `index_require_append_only_single_line` and `index_lo_status_line_re` together replace the prior "always allowed" semantics; `index_deny_full_write` blocks the `Write` overwrite path; `deny_edit_existing` keeps the existing-file protection.

### IP-3: Codex parity wrappers (expanded surface)

`.codex/gtkb-hooks/lo-file-safety-gate.cmd` invokes `python E:\GT-KB\.codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py`. The adapter:

1. Parses Codex `Bash` tool_input commands using the same `_classify_bash_write_intent` logic as the Claude-side hook (shared via import from a stable in-root path to avoid drift), so the F2 copy/restore detection holds symmetrically on the Codex side.
2. For `apply_patch`, parses patch headers per affected file and reconstructs candidate post-edit content from current file + applied hunks; reshapes payload to `{"tool_name": "Edit", "tool_input": {"file_path": ..., "old_string": ..., "new_string": ...}}` per file and invokes the Claude hook. The reconstructed-content path also feeds the F1 INDEX diff classifier when an `apply_patch` targets `bridge/INDEX.md`.
3. Translates `{"decision": "block"}` -> exit 2 per Codex hook contract.

### IP-4: Hook registrations

`.claude/settings.json`: add `lo-file-safety-gate.py` to a `Write|Edit|MultiEdit|Bash` PreToolUse matcher block (sibling of `implementation-start-gate.py`). Does NOT extend the narrower `Write|Edit` block where `bridge-compliance-gate.py` and `narrative-artifact-approval-gate.py` live.

`.codex/hooks.json`: add `Bash` and `apply_patch` PreToolUse entries invoking `.codex/gtkb-hooks/lo-file-safety-gate.cmd`.

### IP-5: Platform-lane tests

`platform_tests/scripts/test_lo_file_safety_gate.py` — in the active GT-KB platform test lane, covered by `pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` and by `.github/workflows/groundtruth-kb-tests.yml`.

## Specification-Derived Verification Plan

Tests at `platform_tests/scripts/test_lo_file_safety_gate.py`; run via `python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -v`. Each test maps to a linked specification and, where applicable, to the `-002` or `-004` finding it closes.

| # | Test | Finding / spec coverage |
|---|------|---|
| 1 | `test_pass_when_role_is_prime_builder` | baseline; `.claude/rules/prime-builder-role.md` |
| 2 | `test_block_when_role_is_lo_and_path_not_allow_listed_write` | `-002` F1 baseline; GOV-FILE-BRIDGE-AUTHORITY-001; DELIB-2188 regression |
| 3 | `test_block_when_role_is_lo_and_path_not_allow_listed_edit` | `-002` F1 |
| 4 | `test_block_when_role_is_lo_and_path_not_allow_listed_multiedit` | `-002` F1 |
| 5 | `test_block_when_role_is_lo_bash_shell_redirect` | `-002` F1 |
| 6 | `test_block_when_role_is_lo_bash_heredoc_write` | `-002` F1 |
| 7 | `test_block_when_role_is_lo_powershell_set_content` | `-002` F1 |
| 8 | `test_block_when_role_is_lo_bash_remove_item` | `-002` F1 |
| 9 | `test_block_when_role_is_lo_bash_move_item` | `-002` F1 |
| 10 | `test_block_when_role_is_lo_bash_opaque_substitution` (sentinel) | `-002` F1 |
| 11 | `test_block_when_role_is_lo_bash_copy_item_no_force` — `Copy-Item source target` against a non-allow-listed path under LO role is blocked even without `-Force`. | `-004` F2 |
| 12 | `test_block_when_role_is_lo_bash_cp_alias` — PowerShell `cp src dst` (Copy-Item alias) against a non-allow-listed path under LO role is blocked. | `-004` F2 |
| 13 | `test_block_when_role_is_lo_bash_copy_alias` — PowerShell `copy src dst` (Copy-Item alias) against a non-allow-listed path under LO role is blocked. | `-004` F2 |
| 14 | `test_block_when_role_is_lo_bash_posix_cp_no_force` — POSIX `cp src dst` (no `-f`) against a non-allow-listed path under LO role is blocked. | `-004` F2 |
| 15 | `test_block_when_role_is_lo_bash_git_restore` — `git restore -- <path>` against a non-allow-listed path under LO role is blocked. | `-004` F2 |
| 16 | `test_block_when_role_is_lo_bash_git_checkout_dashdash` — `git checkout -- <path>` remains blocked (regression guard for the `-003` coverage). | `-004` F2 |
| 17 | `test_allow_when_path_in_dropbox` | baseline; `.claude/rules/loyal-opposition.md` § Storage Convention |
| 18 | `test_allow_when_path_is_lo_log` | baseline; `.claude/rules/loyal-opposition.md` § Storage Convention |
| 19 | `test_allow_when_path_is_knowledge_project` | baseline |
| 20 | `test_allow_when_path_is_memory_md` | baseline |
| 21 | `test_allow_when_lo_inserts_status_line_at_top_of_entry` — an `Edit` to `bridge/INDEX.md` whose candidate diff inserts exactly one `NO-GO:`/`GO:`/`VERIFIED:`/`ADVISORY:` line at the top of a matching `Document:` entry's version list is allowed. | `-004` F1; `.claude/rules/file-bridge-protocol.md` § Loyal Opposition Workflow |
| 22 | `test_block_when_lo_index_edit_deletes_a_line` — an `Edit` to `bridge/INDEX.md` whose candidate diff removes any line is blocked. | `-004` F1 |
| 23 | `test_block_when_lo_index_edit_reorders_entries` — an `Edit` to `bridge/INDEX.md` whose candidate diff reorders existing lines is blocked. | `-004` F1 |
| 24 | `test_block_when_lo_index_edit_touches_unrelated_entry` — an `Edit` to `bridge/INDEX.md` that inserts a line into a different `Document:` entry than the matching one (or modifies an unrelated entry) is blocked. | `-004` F1 |
| 25 | `test_block_when_lo_index_full_write_overwrite` — a `Write` (full-file overwrite) of `bridge/INDEX.md` under LO role is blocked. | `-004` F1 |
| 26 | `test_block_when_lo_index_edit_inserts_prime_status_line` — an `Edit` inserting a `NEW:` or `REVISED:` line (Prime-set statuses) into `bridge/INDEX.md` under LO role is blocked. | `-004` F1 |
| 27 | `test_block_when_lo_index_edit_inserts_two_lines` — an `Edit` whose candidate diff inserts more than one line is blocked. | `-004` F1 |
| 28 | `test_allow_when_creating_new_bridge_verdict_file` — LO `Write` creating a not-yet-existing `bridge/foo-002.md` is allowed. | `-002` F3; `.claude/rules/codex-review-gate.md` |
| 29 | `test_block_when_editing_existing_bridge_verdict_file` — LO `Edit` to an existing `bridge/foo-002.md` is blocked. | `-002` F3 |
| 30 | `test_block_when_overwriting_existing_bridge_proposal_via_write` — LO `Write` overwriting an existing `bridge/foo-001.md` is blocked. | `-002` F3 |
| 31 | `test_block_with_invalid_approval_packet_env_var` | baseline; GOV-ARTIFACT-APPROVAL-001 |
| 32 | `test_pass_with_valid_approval_packet_write` | baseline; GOV-ARTIFACT-APPROVAL-001 |
| 33 | `test_block_when_packet_target_path_mismatch` | baseline; DCL-ARTIFACT-APPROVAL-HOOK-001 |
| 34 | `test_block_when_packet_sha256_mismatch` | baseline; DCL-ARTIFACT-APPROVAL-HOOK-001 |
| 35 | `test_block_when_packet_full_content_mismatch_for_edit_after_reconstruction` | `-002` F2 |
| 36 | `test_block_when_packet_full_content_mismatch_for_multiedit_after_reconstruction` | `-002` F2 |
| 37 | `test_pass_with_valid_approval_packet_edit_after_reconstruction` | `-002` F2 |
| 38 | `test_block_when_packet_exception_attempted_for_bash_write` | `-002` F1+F2 |
| 39 | `test_pass_for_non_write_tool` — `tool_name="Read"` returns `{}`. | hook scope discipline |
| 40 | `test_pass_when_no_role_assignment_record_exists` (fail-open bootstrap) | hook bootstrap safety |
| 41 | `test_claude_settings_registers_hook_on_full_surface` — `.claude/settings.json` has a `Write|Edit|MultiEdit|Bash` matcher naming `lo-file-safety-gate.py`. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 |
| 42 | `test_codex_hooks_registers_wrapper_on_bash_and_apply_patch` — `.codex/hooks.json` has `Bash` and `apply_patch` PreToolUse entries naming `lo-file-safety-gate.cmd`. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 |
| 43 | `test_codex_adapter_translates_apply_patch_with_reconstruction` — adapter reshapes `apply_patch` and invokes the Claude hook per affected file; exit 2 on block. | ADR-CODEX-HOOK-PARITY-FALLBACK-001; DELIB-1742..1739 |
| 44 | `test_platform_tests_lane_contains_module` — the test module is under `platform_tests/scripts/`. | `-002` F4 |

Acceptance commands:

- `python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -v` reports 44/44 PASS.
- `python .claude/hooks/lo-file-safety-gate.py --self-test` exits 0 with stdout `{}` (mirrors `narrative-artifact-approval-gate.py` self-test contract).
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` reports `preflight_passed: true`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` exits 0.

## Risks and Rollback

**Risk 1 — Bash classifier false negatives.** A novel write-intent shell idiom may bypass `_classify_bash_write_intent`. Mitigation: the classifier defaults to fail-closed via the `<opaque-bash>` sentinel when it detects substitution patterns it cannot statically resolve; the F2 copy/restore additions close the specific gap the `-004` NO-GO identified. Tests 10-16 exercise these paths.

**Risk 2 — Edit/MultiEdit reconstruction divergence from Claude's actual write.** Reconstruction must mirror the tool's `old_string`/`new_string` semantics exactly. Mitigation: tests 35-37 use fixture files with controlled content; the reconstruction algorithm tracks the `replace_all` flag and edit ordering.

**Risk 3 — INDEX diff classifier false positives on legitimate verdict insertion.** A legitimate LO verdict insertion that happens to also normalize whitespace elsewhere in `bridge/INDEX.md` would be blocked by the strict single-line-additive check. Mitigation: this is the intended conservative behavior — LO should insert exactly one status line and change nothing else; tests 21-27 pin the boundary. If a legitimate operation is blocked, LO files the insertion as a clean single-line `Edit`.

**Risk 4 — `apply_patch` reconstruction fragility.** Patch hunks may not apply cleanly against the on-disk file if the file changed mid-flight. Mitigation: the adapter reads file content immediately before patch application; if hunks do not apply cleanly, the adapter fails closed.

**Risk 5 — Role-map drift causes wrong-role enforcement.** Mitigation: the hook reads live `harness-state/role-assignments.json` per call (no caching). Tests 1-2 cover both role assignments.

**Risk 6 — Legitimate LO Edit to its own previously-authored bridge file gets blocked.** Per the F3 fix carried forward, even self-authored existing `bridge/*.md` files cannot be edited by LO under the gate; the audit-trail rule treats every existing `bridge/*.md` as immutable. Mitigation: LO files a new version (`-NNN+1.md`) rather than editing.

**Rollback.** Revert the hook registrations in `.claude/settings.json` and `.codex/hooks.json`. The hook script files, TOML config, and platform tests can remain on disk; absent registration, they are inert. No state migration required.

## Sequenced Dependencies

1. Codex GO on this `-005` proposal recorded in `bridge/INDEX.md`.
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1`.
3. Implementation ordering (single commit):
   a. `config/governance/lo-file-safety.toml` (config first).
   b. `.claude/hooks/lo-file-safety-gate.py` (Claude-side hook).
   c. `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` then `.codex/gtkb-hooks/lo-file-safety-gate.cmd` (Codex parity).
   d. `platform_tests/scripts/test_lo_file_safety_gate.py` (regression tests).
   e. `.claude/settings.json` and `.codex/hooks.json` (registration done LAST so the hook is fully tested before going live).
4. Post-implementation: file a post-implementation report at `-006` with the spec-to-test mapping, pytest output, and preflight outputs.

No cross-thread bridge dependency blocks this thread.

## Recommended Commit Type

`feat:` — net-new hook script, net-new Codex parity wrapper, net-new Codex adapter, net-new TOML config, net-new platform test module, plus two settings-registration edits. Mechanical enforcement of a previously rule-cited-only governance rule; net-new capability surface. `chore:` would be inaccurate per the S333 FINDING-P0-001 precedent.

## Bridge INDEX Maintenance

This REVISED-2 proposal is filed as version `-005` of the existing `Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1` entry in `bridge/INDEX.md`. The `REVISED: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md` line is inserted at the top of that entry's version list, above the existing `NO-GO: ...-004.md`, `REVISED: ...-003.md`, `NO-GO: ...-002.md`, and `NEW: ...-001.md` lines, per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior version line is deleted or reordered; the append-only audit trail is preserved.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:a809b791e428fb936454b63e46fb12addf72de7cf0b306d4c6d68f179da97324`
- bridge_document_name: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md`
- operative_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- Operative file: `bridge\gtkb-lo-file-safety-pretooluse-enforcement-slice-1-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```
