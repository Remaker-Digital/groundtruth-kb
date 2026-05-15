---
Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: WI-3308
Recommended commit type: feat
target_paths: [".claude/hooks/lo-file-safety-gate.py", ".codex/gtkb-hooks/lo-file-safety-gate.cmd", ".codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py", "config/governance/lo-file-safety.toml", ".claude/settings.json", ".codex/hooks.json", "tests/scripts/test_lo_file_safety_gate.py"]
---

# WI-3308 Slice 1: LO File-Safety PreToolUse Enforcement Hook

## Summary

The §"Loyal Opposition File Safety Rule" in `.claude/rules/loyal-opposition.md` is currently rule-cited soft authority only. It states: "When operating as Loyal Opposition, do not delete or modify files you have not created without explicit approval from the owner (Mike)." The S350 incident (`DELIB-S350-CODEX-LO-FILE-SAFETY-VIOLATION`, rowid 2188) documented Codex (assigned LO per `harness-state/role-assignments.json`) editing `scripts/implementation_authorization.py` and other implementation files for Slice 3/4 of `GTKB-SELF-DIAGNOSTIC-LEAK-CLOSURE` without per-file owner approval. The rule fired no mechanical block.

This slice adds a Claude-Code-side PreToolUse Write/Edit hook (`lo-file-safety-gate.py`) plus a Codex-side parity wrapper that:

1. Resolves the active harness role-set from `harness-state/role-assignments.json` via `scripts/harness_roles.py is_loyal_opposition`.
2. When the role-set contains `loyal-opposition` AND the target path is NOT in the LO-authoring allow-list, returns `{"decision": "block", "reason": "..."}` unless an owner-approval-packet path is supplied via env var (`GTKB_LO_FILE_SAFETY_APPROVAL_PACKET`) and that packet validates against the proposed write.
3. Returns the empty `{}` pass response when role-set is `prime-builder` only (no role-set contention with the Prime authority contract per `.claude/rules/prime-builder-role.md`).

Codex parity follows the proven `bridge-compliance-gate` pattern: a `.cmd` wrapper invoking a `-bash-adapter.py` bridge that re-shapes Codex's `Bash` PreToolUse tool-input shape into the Claude-Code `Write|Edit` shape the gate expects, exiting `2` on block per Codex hook contract.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 (bridge protocol authority; WI source spec)
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (this proposal cites all relevant specs)
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (test mapping derived from linked specs)
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 (Codex parity is mandatory; live interception boundary on CLI >= 0.128.0-alpha.1 per `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` rowid 1550)
- GOV-STANDING-BACKLOG-001 (WI-3308 is a backlog-authority item; this proposal is not a bulk operation, see Clause Scope Clarification below)
- GOV-ARTIFACT-APPROVAL-001 (approval-packet pathway for LO KB-writes; this slice extends the packet-gate pattern to LO file-system writes)
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 (hook placement under `.claude/hooks/` + `.codex/gtkb-hooks/` is GT-KB platform infrastructure, not application code)
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (mechanical enforcement promotes rule from text-only to artifact-tested)
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (active-pursuit mandate: surface rule-text-vs-mechanical-enforcement gaps)
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (hook lifecycle: created, registered, regression-tested)
- `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (the rule being mechanically enforced) and § "Reviewer-Evidence-Preparation vs Speculative Source Modification" (the boundary the allow-list encodes) and § "Loyal Opposition KB-Write Approval-Packet Pathway" (parallel approval-packet contract reused here)
- `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input Section Gate" (gate pattern modeled)
- `.claude/rules/codex-review-gate.md` (LO review obligations preserved by allow-listing `bridge/` for verdict authoring)
- `.claude/rules/project-root-boundary.md` (allow-list paths are all in-root; hook itself is in-root)

## Prior Deliberations

- DELIB-2188 (S350 origin): "Codex (LO) violated `.claude/rules/loyal-opposition.md` file-safety rule by implementing Slice 3/4 source-code edits" — the originating observation cited in WI-3308.
- DELIB-1988 (VERIFIED, 4 versions): `gtkb-lo-file-safety-rule-clarification-001` thread — clarified the rule's scope and added the "Reviewer-Evidence-Preparation vs Speculative Source Modification" subsection. This slice promotes that clarified rule to mechanical enforcement.
- DELIB-1551, DELIB-1550 (S337): empirical Codex Windows hook firing on CLI >= 0.128.0-alpha.1 — establishes that `.codex/hooks.json` IS a live interception boundary, justifying full Codex parity rather than fallback-only.
- DELIB-1518, DELIB-1519 (S327 owner directives): standing backlog formalization and primer-loading — context for the WI-3308 backlog-authority spec citation.
- DELIB-1742..1739: Codex `bridge-compliance-gate` hook parity thread — proven `.cmd` wrapper + `-bash-adapter.py` pattern reused here.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" — this directive authorizes batch filing of priority backlog proposals (WI-3308 is `priority: high`). Per-proposal Codex GO is required before any implementation work begins; this proposal does not bypass the per-proposal review gate.

Detected via: implicit owner direction (parallelization request directly authorizing batch proposal filing). No new owner decision is requested by this proposal; existing approval scope covers proposal authoring. Implementation will require a separate Codex GO before any of the listed `target_paths` is written.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk operation against the standing backlog or work-items inventory. The proposal touches a single backlog item (WI-3308) and produces a focused inventory of new files: one Claude hook, one Codex wrapper, one Codex adapter, one TOML config, two settings edits, one test module. The proposal does not iterate over `work_items`, does not bulk-mutate backlog entries, does not bulk-promote specs, and does not run inventory-wide operations.

Evidence tokens for clause-preflight bulk-ops false-positive avoidance: `inventory` (the inventory of target_paths is enumerated above and bounded to seven artifacts); `formal-artifact-approval` (no formal-artifact-approval packet is required by this slice because the proposal touches only hook infrastructure under `.claude/hooks/`, `.codex/gtkb-hooks/`, and `config/governance/`, none of which are protected narrative-artifact paths per `config/governance/narrative-artifact-approval.toml`; the implementation-start authorization packet is required per `.claude/rules/codex-review-gate.md` § "Mechanical Implementation-Start Gate").

## Requirement Sufficiency

Existing requirements sufficient. Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (source spec on WI-3308); `.claude/rules/loyal-opposition.md` § "Loyal Opposition File Safety Rule" (rule text being enforced); ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 (parity obligation). The rule itself defines scope, exceptions (self-created files, owner approval), and the precedent allow-list (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`, `LOYAL-OPPOSITION-LOG.md`, `KNOWLEDGE-PROJECT.md`). No new requirement is needed for the first slice.

## Implementation Plan

### Hook file: `.claude/hooks/lo-file-safety-gate.py`

Modeled on `.claude/hooks/narrative-artifact-approval-gate.py` shape (stdin JSON, stdout `{"decision": "block", ...}` or `{}`, exit `0` always). Behavior:

1. Read stdin JSON. If `tool_name` not in `{"Write", "Edit"}`, emit `{}`.
2. Resolve `_project_root()` from `CLAUDE_PROJECT_DIR` env var or `cwd`.
3. Load `harness-state/role-assignments.json` via `scripts.harness_roles.load_role_assignments` and check `is_loyal_opposition(record)` for the resolved active harness ID.
4. If active harness role-set does NOT contain `loyal-opposition`, emit `{}` (pass; PB writes are unrestricted by this gate).
5. Normalize `tool_input.file_path` to forward-slash relative under project root.
6. Load allow-list from `config/governance/lo-file-safety.toml` (see Allow-List Contents below). If path matches any allow pattern, emit `{}`.
7. Check approval-packet env var `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET`. If absent, emit block.
8. Load packet JSON, validate required fields (`artifact_type='lo_file_safety_authorization'`, `target_path`, `full_content`, `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `approved_by='owner'`). On any validation failure, emit block.
9. Verify `Path(packet.target_path).as_posix() == rel_path`. Verify `hashlib.sha256(full_content).hexdigest() == full_content_sha256`. For Write, verify packet `full_content == tool_input.content`.
10. On all checks pass, emit `{}`.

### Allow-list (`config/governance/lo-file-safety.toml`)

```toml
[[allow]]
description = "LO insight-report authoring dropbox"
patterns = ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**"]

[[allow]]
description = "LO running context files"
patterns = [
  "independent-progress-assessments/LOYAL-OPPOSITION-LOG.md",
  "independent-progress-assessments/KNOWLEDGE-PROJECT.md",
]

[[allow]]
description = "Bridge verdict authoring (NEW/REVISED/GO/NO-GO/VERIFIED files)"
patterns = ["bridge/**.md"]

[[allow]]
description = "Bridge INDEX edits for verdict insertion"
patterns = ["bridge/INDEX.md"]

[[allow]]
description = "MEMORY.md operational notepad (LO-side handoff state)"
patterns = ["memory/MEMORY.md"]

[hook_detection]
env_var_names = ["GTKB_LO_FILE_SAFETY_APPROVAL_PACKET"]
```

### Codex parity wrappers

- `.codex/gtkb-hooks/lo-file-safety-gate.cmd` — invokes `python E:\GT-KB\.codex\gtkb-hooks\lo-file-safety-gate-bash-adapter.py` (modeled on `bridge-compliance-gate.cmd` + `bridge-compliance-gate-bash-adapter.py` shape).
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` — parses Codex's `Bash` tool_input shape, extracts write-intent commands (`> file`, `>> file`, `tee file`, heredoc), re-shapes payload to `{"tool_name": "Write", "tool_input": {"file_path": ..., "content": ...}}`, invokes `.claude/hooks/lo-file-safety-gate.py` via subprocess, translates `{"decision": "block"}` to exit `2`. For `apply_patch` tool, parses patch headers to extract target paths and synthesizes Write/Edit shape per affected file.

### Hook registrations

- `.claude/settings.json` — add `lo-file-safety-gate.py` to the existing `Write|Edit` PreToolUse matcher block (sibling of `bridge-compliance-gate.py` and `narrative-artifact-approval-gate.py`).
- `.codex/hooks.json` — add `Bash` and `apply_patch` PreToolUse entries invoking the `.cmd` wrapper (sibling of `bridge-compliance-gate.cmd`).

## Test Mapping

Tests at `tests/scripts/test_lo_file_safety_gate.py` (pytest module; runs via `python -m pytest tests/scripts/test_lo_file_safety_gate.py -v`):

| # | Test | Spec coverage |
|---|------|---------------|
| 1 | `test_pass_when_role_is_prime_builder` — fixture sets harness B = `["prime-builder"]`; Write to `scripts/foo.py` returns `{}`. | `.claude/rules/loyal-opposition.md` scope; `.claude/rules/prime-builder-role.md` |
| 2 | `test_block_when_role_is_loyal_opposition_and_path_not_allow_listed` — harness A = `["loyal-opposition"]`; Write to `scripts/implementation_authorization.py` returns `{"decision": "block", ...}`. | GOV-FILE-BRIDGE-AUTHORITY-001; DELIB-2188 regression |
| 3 | `test_allow_when_path_in_dropbox` — LO writing `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-14-foo.md` returns `{}`. | `.claude/rules/loyal-opposition.md` § Storage Convention |
| 4 | `test_allow_when_path_is_lo_log` — LO writing `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md` returns `{}`. | `.claude/rules/loyal-opposition.md` § Storage Convention |
| 5 | `test_allow_when_path_is_bridge_verdict` — LO writing `bridge/foo-002.md` returns `{}`. | `.claude/rules/codex-review-gate.md` (LO verdict authoring) |
| 6 | `test_allow_when_path_is_bridge_index` — LO writing `bridge/INDEX.md` returns `{}`. | `.claude/rules/file-bridge-protocol.md` (LO index updates) |
| 7 | `test_allow_when_path_is_memory_md` — LO writing `memory/MEMORY.md` returns `{}`. | `.claude/rules/loyal-opposition.md` (operational notepad) |
| 8 | `test_block_with_invalid_approval_packet_env_var` — env var set to nonexistent path; returns block. | GOV-ARTIFACT-APPROVAL-001 |
| 9 | `test_pass_with_valid_approval_packet` — env var points to packet matching write target_path, full_content, sha256, with all required fields; returns `{}`. | GOV-ARTIFACT-APPROVAL-001 |
| 10 | `test_block_when_packet_target_path_mismatch` — packet target_path differs from tool_input file_path; returns block. | DCL-ARTIFACT-APPROVAL-HOOK-001 |
| 11 | `test_block_when_packet_sha256_mismatch` — packet full_content_sha256 wrong; returns block. | DCL-ARTIFACT-APPROVAL-HOOK-001 |
| 12 | `test_block_when_packet_full_content_mismatch_for_write` — Write `tool_input.content` != packet full_content; returns block. | DCL-ARTIFACT-APPROVAL-HOOK-001 |
| 13 | `test_pass_for_non_write_tool` — `tool_name="Read"` returns `{}`. | Hook scope discipline |
| 14 | `test_pass_when_no_role_assignment_record_exists` — `harness-state/role-assignments.json` missing; returns `{}` (fail-open per Slice 1 conservative scope). | Hook bootstrap safety |
| 15 | `test_claude_settings_registers_hook` — `.claude/settings.json` has `Write|Edit` matcher entry naming `lo-file-safety-gate.py`. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 |
| 16 | `test_codex_hooks_registers_wrapper` — `.codex/hooks.json` has `Bash` PreToolUse entry naming `lo-file-safety-gate.cmd`. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 |
| 17 | `test_codex_adapter_translates_write_command` — feed adapter a `cat > path/to/file <<EOF\ncontent\nEOF` command; adapter re-shapes and invokes Claude hook; exit `2` when block. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2; DELIB-1742..1739 (proven adapter pattern) |
| 18 | `test_codex_adapter_translates_apply_patch` — feed adapter an `apply_patch` payload; adapter extracts target paths and invokes Claude hook per file. | ADR-CODEX-HOOK-PARITY-FALLBACK-001 v2 |

## Risk and Rollback

**Risk 1: False-positive block on legitimate LO verdict authoring.** Mitigation: explicit `bridge/**.md` allow pattern. Verified by Test 5 + Test 6.

**Risk 2: Claude-side write of new bridge proposal under LO role (e.g., LO advisory)** is allowed by `bridge/**.md` pattern. This is correct per `.claude/rules/file-bridge-protocol.md` § "Advisory Reports" (LO authors ADVISORY entries).

**Risk 3: Codex adapter mis-classifies a data-substitution heredoc as an executing write.** Mitigation per `feedback_security_parser_executing_wrapper_distinction.md`: adapter classifies by execution-context axis — `cat > file <<EOF` IS a write; `echo "$(cat file)"` is data-substitution, NOT a write. Test 17 exercises the heredoc-write path explicitly; adapter rejects opaque-wrapper patterns conservatively (defer to fail-open with audit-log emission, NOT silent pass).

**Risk 4: Role-map drift causes wrong-role enforcement.** Mitigation: hook reads live `harness-state/role-assignments.json` per call (no caching). Test 1 + Test 2 cover both role assignments.

**Rollback:** Revert hook registrations in `.claude/settings.json` and `.codex/hooks.json`. The hook script files and config TOML can remain; absent registration, they are inert. No state migration required.

## Acceptance Criteria

1. `python -m pytest tests/scripts/test_lo_file_safety_gate.py -v` reports 18/18 PASS.
2. `python .claude/hooks/lo-file-safety-gate.py --self-test` exits 0 with stdout `{}` (mirrors narrative-artifact-approval-gate self-test contract).
3. End-to-end manual check: with harness A role-set `["loyal-opposition"]`, attempting `Write` to `scripts/foo.py` in a Codex `codex exec` session is blocked with the LO-file-safety reason; switching role-map to `["prime-builder"]` allows the write.
4. End-to-end manual check: LO writing to `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-14-test.md` is allowed.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` reports `preflight_passed: true`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` exits 0.

## Verification Plan

Post-implementation report will include:

- `python -m pytest tests/scripts/test_lo_file_safety_gate.py -v` output (expect 18 PASS).
- `python .claude/hooks/lo-file-safety-gate.py --self-test` stdout + exit code.
- Manual end-to-end transcript: temporarily set harness B role-set to `["loyal-opposition"]` via `python scripts/harness_roles.py set --harness-id B --role loyal-opposition`, attempt `Write` to a non-allow-listed file via Claude tool, capture the block reason, restore role-set to `["prime-builder"]`.
- `python scripts/bridge_applicability_preflight.py --bridge-id <post-impl-doc-name>` packet hash.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id <post-impl-doc-name>` exit code.
- Diff stat justifying `feat:` commit type (~7 new files; non-trivial new capability surface).

## Applicability Preflight

To be embedded after running `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1` (post-INDEX-entry; current pre-filing state requires manual trigger-pattern check against `config/governance/spec-applicability.toml`). Author has reviewed the TOML trigger patterns (`applies_when_path_matches`, `applies_when_content_matches`) against the proposal text; cited specs above include all triggered cross-cutting governance specs.

Packet hash: TO BE FILLED after preflight invocation post-INDEX-entry.

End of proposal.
