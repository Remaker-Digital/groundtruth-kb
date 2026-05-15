REVISED

# Implementation Proposal - LO File-Safety PreToolUse Enforcement Slice 1 - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1
Version: 003
Responds to: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3308
target_paths: [".claude/hooks/lo-file-safety-gate.py", ".codex/gtkb-hooks/lo-file-safety-gate.cmd", ".codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py", "config/governance/lo-file-safety.toml", ".claude/settings.json", ".codex/hooks.json", "platform_tests/scripts/test_lo_file_safety_gate.py"]

## Claim

This revision answers Codex NO-GO at `-002` by (1) expanding Claude-side hook coverage from `Write|Edit` to `Write|Edit|MultiEdit|Bash` with explicit post-edit-content reconstruction; (2) binding the approval-packet `full_content_sha256` check to a candidate post-edit content reconstructed per tool shape, with fail-closed semantics for shapes that cannot be reliably reconstructed; (3) replacing the broad `bridge/**.md` allow-list pattern with a narrow bridge-operation classifier that permits creating new bridge versioned files and editing `bridge/INDEX.md` only — and explicitly denies edits to existing `bridge/*.md` files even under LO role; (4) moving the test module to the active platform test lane at `platform_tests/scripts/test_lo_file_safety_gate.py`. No specification gap requires a new requirement; the existing linked specification set governs all four fixes.

## In-Root Placement Evidence

All `target_paths` are in-root under `E:\GT-KB`:

- `.claude/hooks/lo-file-safety-gate.py` — under `.claude/hooks/`, the canonical Claude hooks directory.
- `.codex/gtkb-hooks/lo-file-safety-gate.cmd`, `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` — under `.codex/gtkb-hooks/`, the canonical Codex hook-wrapper directory.
- `config/governance/lo-file-safety.toml` — under `config/governance/`, the canonical governance config directory.
- `.claude/settings.json`, `.codex/hooks.json` — repository-root harness settings files.
- `platform_tests/scripts/test_lo_file_safety_gate.py` — under `platform_tests/scripts/`, the active GT-KB platform test lane.

ADR-ISOLATION-APPLICATION-PLACEMENT-001 `CLAUSE-IN-ROOT` evidence: this hook is GT-KB platform infrastructure (governance enforcement of a `.claude/rules/` rule), not application code; placement under `.claude/`, `.codex/`, `config/governance/`, and `platform_tests/` is canonical for platform infrastructure. No path leaves `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal inserts a status line into `bridge/INDEX.md` at the top of the existing `gtkb-lo-file-safety-pretooluse-enforcement-slice-1` entry per the `insert.+top of.+entry` convention.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — test mapping derived from linked specs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 — Codex parity mandatory; live interception boundary per DELIB-1550 / DELIB-1551.
- `GOV-STANDING-BACKLOG-001` — WI-3308 backlog-authority source; this proposal is not a bulk operation.
- `GOV-ARTIFACT-APPROVAL-001` — approval-packet pathway pattern extended to LO file-system writes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; hook is platform infrastructure.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — rule promoted from text-only to artifact-tested mechanical enforcement.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — surface rule-text-vs-mechanical-enforcement gaps.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — hook lifecycle: created, registered, regression-tested.
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (the rule being mechanically enforced); § "Reviewer-Evidence-Preparation vs Speculative Source Modification" (the boundary the allow-list encodes); § "Loyal Opposition KB-Write Approval-Packet Pathway" (parallel approval-packet contract reused here).
- `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input Section Gate" (gate pattern modeled); § "Guardrails" — never delete bridge files; append-only audit trail (informs the narrow bridge-operation classifier replacing the broad `bridge/**.md` allow pattern; see F3 fix).
- `.claude/rules/codex-review-gate.md` (LO review obligations preserved by allow-listing new-version bridge file creation for verdict authoring).
- `.claude/rules/project-root-boundary.md` (allow-list paths and hook implementation are all in-root).

## Prior Deliberations

- `DELIB-2188` (S350 origin): "Codex (LO) violated `.claude/rules/loyal-opposition.md` file-safety rule by implementing Slice 3/4 source-code edits without per-file owner approval." Originating observation cited in WI-3308.
- `DELIB-1988` (VERIFIED, 4 versions): `gtkb-lo-file-safety-rule-clarification-001` thread — added the "Reviewer-Evidence-Preparation vs Speculative Source Modification" subsection to the rule. This slice promotes that clarified rule to mechanical enforcement.
- `DELIB-1551`, `DELIB-1550` (S337): empirical Codex Windows hook firing on CLI ≥ 0.128.0-alpha.1.
- `DELIB-1742`..`DELIB-1739` (S337-S338): Codex `bridge-compliance-gate` hook parity thread — proven `.cmd` wrapper + `-bash-adapter.py` pattern reused here.
- `DELIB-1518`, `DELIB-1519` (S327): standing-backlog formalization context.
- `DELIB-1738` (S342): Codex NO-GO on `gtkb-pre-filing-preflight-hook` — establishes precedent that approval-packet exceptions must bind to post-edit content, not just to path + standalone hash. F2 fix directly applies this precedent.
- `DELIB-1560` (GO): glossary-backfill precedent for narrowing over-broad allow-list patterns to operation-specific classifiers.

## Owner Decisions / Input

S350 owner direction (current turn): "Please continue to parallelize work." S350 batch authorization (recorded earlier this session): owner AUQ answer "Parallel research + serialized Writes now (Recommended)" — this directive authorizes parallel research and serialized batch filing of priority backlog proposals (WI-3308 is `priority: high`). Per-proposal Codex GO is required before any implementation work begins; this proposal does not bypass the per-proposal review gate.

Detected via: explicit S350 owner AUQ answer + current-turn directive. No new AskUserQuestion is requested by this revision. The owner-approval scope covers proposal revision and re-filing; implementation will require Codex GO on `-003` before any of the listed `target_paths` is written. The implementation-start authorization packet must be created per `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate" once Codex records GO.

## Requirement Sufficiency

Existing requirements sufficient. Governing specs are unchanged from `-001`: GOV-FILE-BRIDGE-AUTHORITY-001 (WI-3308 source spec); `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (rule text being enforced); ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 (parity obligation). Codex's NO-GO at `-002` raised no requirement-disambiguation finding; all four findings are implementation-defect findings remediable through proposal revision without changing the requirement surface.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk operation against the standing backlog or work-items inventory. It touches a single backlog item (WI-3308) and produces a focused, bounded inventory of seven new/modified files: one Claude hook, one Codex `.cmd` wrapper, one Codex `-bash-adapter.py` bridge, one TOML config, two harness settings edits, one platform test module. The proposal does not iterate over `work_items`, does not bulk-mutate backlog entries, does not bulk-promote specs, and does not run inventory-wide operations.

Evidence tokens for `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause-preflight bulk-ops false-positive avoidance: `inventory` (the inventory of target_paths is enumerated above and bounded to seven artifacts); `formal-artifact-approval` (no formal-artifact-approval packet is required by this slice because the proposal touches only hook infrastructure under `.claude/hooks/`, `.codex/gtkb-hooks/`, `config/governance/`, and harness settings, none of which are protected narrative-artifact paths; the implementation-start authorization packet IS required once Codex records GO).

## Proposed Scope

### IP-1: Expand Claude-side hook surface and add post-edit content reconstruction

`.claude/hooks/lo-file-safety-gate.py`. Behavior:

1. Read stdin JSON. If `tool_name` not in `{"Write", "Edit", "MultiEdit", "Bash"}`, emit `{}` (pass).
2. Resolve `_project_root()` from `CLAUDE_PROJECT_DIR` env or `cwd`.
3. Load `harness-state/role-assignments.json` via `scripts.harness_roles.load_role_assignments`. Resolve active harness ID; call `scripts.harness_roles.is_loyal_opposition(record)`. If False, emit `{}`.
4. Per tool_name, normalize a list of `(rel_path, candidate_post_edit_content_or_none)` target tuples:
   - `Write`: single tuple `(file_path, tool_input.content)`.
   - `Edit`: read current file content; apply `old_string` → `new_string` substitution (respecting `replace_all`); produce candidate post-edit content; tuple `(file_path, candidate)`.
   - `MultiEdit`: read current file content; apply each edit sequentially; tuple `(file_path, candidate_after_all_edits)`.
   - `Bash`: invoke `_classify_bash_write_intent(command)` which detects shell redirects (`>`, `>>`, `tee`), heredocs (`cat > file <<EOF ... EOF`), PowerShell write cmdlets (`Set-Content`, `Out-File`, `Add-Content`, `Tee-Object`), destructive ops (`Remove-Item`, `Move-Item`, `Copy-Item -Force`, `New-Item -Type File`, `rm`, `mv`, `cp -f`, `git checkout -- <path>`), and emits zero-or-more `(rel_path, None)` tuples. If the command contains opaque substitution (`$(...)`, backticks, indirect variable expansion) that could mask write targets, emit a single sentinel tuple `("<opaque-bash>", None)` that fails closed at step 6 below.
5. For each tuple, load allow-list from `config/governance/lo-file-safety.toml`. Two-tier classification:
   - Path-prefix allow (dropbox, LO log, KNOWLEDGE-PROJECT.md, MEMORY.md): allow regardless of operation.
   - Bridge-operation classifier: `bridge/INDEX.md` always allowed; `bridge/*.md` other than INDEX is allowed ONLY if the file does not currently exist (creating a new versioned verdict/advisory); existing `bridge/*.md` files MUST NOT be edited by LO under this gate.
   - Anything else: require approval-packet exception (step 6).
6. Approval-packet exception: load `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET` env var. If absent, block. Validate required fields per the proven `narrative-artifact-approval-gate.py` schema. Verify `Path(packet.target_path).as_posix() == rel_path`. Verify `sha256(packet.full_content) == packet.full_content_sha256`. Verify `sha256(candidate_post_edit_content) == packet.full_content_sha256` for `Write|Edit|MultiEdit` — this is the F2 fix. For `Bash`-write tuples (candidate content is None), the packet exception does NOT apply — Bash writes to non-allow-listed paths under LO role are always blocked unless the operation is moved through `Write|Edit|MultiEdit` where post-edit content reconstruction works. Sentinel `<opaque-bash>` always blocks.
7. If all checks pass, emit `{}`. Otherwise emit `{"decision": "block", "reason": "..."}` with a reason that identifies the failed check and the violated rule.

### IP-2: Narrow allow-list configuration

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
description = "Bridge INDEX line insertions and new-version verdict/advisory file creation"
index_path = "bridge/INDEX.md"
new_version_glob = "bridge/*.md"
deny_edit_existing = true

[hook_detection]
env_var_names = ["GTKB_LO_FILE_SAFETY_APPROVAL_PACKET"]
```

The `[bridge_operation]` block encodes F3.

### IP-3: Codex parity wrappers (expanded surface)

`.codex/gtkb-hooks/lo-file-safety-gate.cmd` invokes `python E:\GT-KB\.codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py`. The adapter:

1. Parses Codex `Bash` tool_input commands using the same `_classify_bash_write_intent` logic as the Claude-side hook (shared via import from a stable path to avoid drift).
2. For `apply_patch`, parses patch headers per affected file and reconstructs candidate post-edit content from current file + applied hunks; reshapes payload to `{"tool_name": "Edit", "tool_input": {"file_path": ..., "old_string": ..., "new_string": ...}}` per file and invokes the Claude hook.
3. Translates `{"decision": "block"}` → exit 2 per Codex hook contract.

### IP-4: Hook registrations

`.claude/settings.json`: add `lo-file-safety-gate.py` to a new `Write|Edit|MultiEdit|Bash` matcher block (sibling of `implementation-start-gate.py`). Does NOT extend the narrower `Write|Edit` block where `bridge-compliance-gate.py` and `narrative-artifact-approval-gate.py` live.

`.codex/hooks.json`: add `Bash` and `apply_patch` PreToolUse entries invoking `.codex/gtkb-hooks/lo-file-safety-gate.cmd`.

### IP-5: Platform-lane tests

`platform_tests/scripts/test_lo_file_safety_gate.py` — moved from the previously proposed `tests/scripts/` path. Covered by `pyproject.toml` `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` and by `.github/workflows/groundtruth-kb-tests.yml`.

## Specification-Derived Verification Plan

Tests at `platform_tests/scripts/test_lo_file_safety_gate.py`; run via `python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -v`.

| # | Test | Finding addressed |
|---|------|---|
| 1 | `test_pass_when_role_is_prime_builder` | baseline |
| 2 | `test_block_when_role_is_lo_and_path_not_allow_listed_write` | baseline |
| 3 | `test_block_when_role_is_lo_and_path_not_allow_listed_edit` | F1 |
| 4 | `test_block_when_role_is_lo_and_path_not_allow_listed_multiedit` | F1 |
| 5 | `test_block_when_role_is_lo_bash_shell_redirect` | F1 |
| 6 | `test_block_when_role_is_lo_bash_heredoc_write` | F1 |
| 7 | `test_block_when_role_is_lo_powershell_set_content` | F1 |
| 8 | `test_block_when_role_is_lo_bash_remove_item` | F1 |
| 9 | `test_block_when_role_is_lo_bash_move_item` | F1 |
| 10 | `test_block_when_role_is_lo_bash_opaque_substitution` (sentinel) | F1 |
| 11 | `test_allow_when_path_in_dropbox` | baseline |
| 12 | `test_allow_when_path_is_lo_log` | baseline |
| 13 | `test_allow_when_path_is_knowledge_project` | baseline |
| 14 | `test_allow_when_path_is_memory_md` | baseline |
| 15 | `test_allow_when_creating_new_bridge_verdict_file` | F3 |
| 16 | `test_block_when_editing_existing_bridge_verdict_file` | F3 |
| 17 | `test_block_when_overwriting_existing_bridge_proposal_via_write` | F3 |
| 18 | `test_allow_when_path_is_bridge_index` | F3 |
| 19 | `test_block_with_invalid_approval_packet_env_var` | baseline |
| 20 | `test_pass_with_valid_approval_packet_write` | baseline |
| 21 | `test_block_when_packet_target_path_mismatch` | baseline |
| 22 | `test_block_when_packet_sha256_mismatch` | baseline |
| 23 | `test_block_when_packet_full_content_mismatch_for_edit_after_reconstruction` | F2 |
| 24 | `test_block_when_packet_full_content_mismatch_for_multiedit_after_reconstruction` | F2 |
| 25 | `test_pass_with_valid_approval_packet_edit_after_reconstruction` | F2 |
| 26 | `test_block_when_packet_exception_attempted_for_bash_write` | F1+F2 |
| 27 | `test_pass_for_non_write_tool` | baseline |
| 28 | `test_pass_when_no_role_assignment_record_exists` (fail-open bootstrap) | baseline |
| 29 | `test_claude_settings_registers_hook_on_full_surface` | F1 |
| 30 | `test_codex_hooks_registers_wrapper_on_bash_and_apply_patch` | F1 |
| 31 | `test_codex_adapter_translates_apply_patch_with_reconstruction` | F1+F2 |
| 32 | `test_platform_tests_lane_contains_module` | F4 |

Acceptance commands:
- `python -m pytest platform_tests/scripts/test_lo_file_safety_gate.py -v` reports 32/32 PASS.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` reports `preflight_passed: true`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` exits 0.

## Risks and Rollback

**Risk 1 — Bash classifier false negatives.** A novel write-intent shell idiom may bypass `_classify_bash_write_intent`. Mitigation: classifier defaults to fail-closed via the `<opaque-bash>` sentinel when it detects substitution patterns it cannot statically resolve. Test 10 exercises this path. Conservative bias: ambiguous shells block under LO; PB role is unaffected.

**Risk 2 — Edit/MultiEdit reconstruction divergence from Claude's actual write.** Reconstruction must mirror the tool's `old_string`/`new_string` semantics exactly. Mitigation: tests 23-25 use fixture files with controlled content; reconstruction algorithm tracks `replace_all` flag and edit ordering.

**Risk 3 — `apply_patch` reconstruction fragility.** Patch hunks may not apply cleanly against the on-disk file if the file changed mid-flight. Mitigation: adapter reads file content immediately before patch application; if hunks do not apply cleanly, the adapter fails closed.

**Risk 4 — Role-map drift causes wrong-role enforcement.** Mitigation: hook reads live `harness-state/role-assignments.json` per call (no caching).

**Risk 5 — Legitimate LO Edit to its own previously-authored bridge file gets blocked.** Per F3, even self-authored bridge files cannot be edited by LO under the gate; the audit-trail rule treats every existing `bridge/*.md` as immutable. Mitigation: LO must file a new version (`-NNN+1.md`) rather than edit.

**Rollback.** Revert hook registrations in `.claude/settings.json` and `.codex/hooks.json`. The hook script files, TOML config, and platform tests can remain on disk; absent registration, they are inert.

## Sequenced Dependencies

1. Codex GO on this `-003` proposal recorded in `bridge/INDEX.md`.
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1`.
3. Implementation ordering (single commit):
   a. `config/governance/lo-file-safety.toml` (config first).
   b. `.claude/hooks/lo-file-safety-gate.py` (Claude-side hook).
   c. `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` then `.codex/gtkb-hooks/lo-file-safety-gate.cmd` (Codex parity).
   d. `platform_tests/scripts/test_lo_file_safety_gate.py` (regression tests).
   e. `.claude/settings.json` and `.codex/hooks.json` (registration done LAST so the hook is fully tested before going live).
4. Post-implementation: file post-implementation report at `-004` with spec-to-test mapping, pytest output, preflight outputs.

No cross-thread bridge dependency blocks this thread.

## Recommended Commit Type

`feat:` — net-new hook script, net-new Codex parity wrapper, net-new TOML config, net-new platform test module, plus two settings-registration edits. Mechanical enforcement of a previously rule-cited-only governance rule. `chore:` would be inaccurate (per S333 FINDING-P0-001 precedent).

## Bridge-Compliance Self-Check

- First line is `REVISED`.
- H1 title: `# Implementation Proposal - LO File-Safety PreToolUse Enforcement Slice 1 - REVISED-1`.
- Metadata block includes `bridge_kind`, `Document`, `Version: 003`, `Responds to:`, `Author`, `Date`, `Session: S350`, `target_paths` JSON list.
- All target_paths in-root under `E:\GT-KB`.
- `## Specification Links` plain heading, flat bullets, no `###` inside, includes `bridge/INDEX.md` and `insert.+top of.+entry` evidence.
- `## Prior Deliberations` substantive.
- `## Owner Decisions / Input` substantive; cites S350 parallelization directive.
- `## Requirement Sufficiency` exactly one operative state: `Existing requirements sufficient`.
- `## Clause Scope Clarification (Not a Bulk Operation)` includes `inventory` and `formal-artifact-approval`.
- `## Proposed Scope` uses `### IP-N`.
- `## Recommended Commit Type` declared: `feat:`.
- F1-F4 from `-002` all addressed in `## Claim` and IPs 1-5.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
