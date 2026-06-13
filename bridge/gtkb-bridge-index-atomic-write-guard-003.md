NEW

bridge_kind: implementation_report
Document: gtkb-bridge-index-atomic-write-guard
Version: 003
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: default
Responds-To: bridge/gtkb-bridge-index-atomic-write-guard-002.md

Project Authorization: PAUTH-WI4481-INDEX-CLOBBER-GUARD-20260613
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4481

target_paths: [".claude/hooks/bridge-index-write-serializer.py", ".claude/settings.json", ".codex/hooks.json", "platform_tests/hooks/test_bridge_index_write_serializer.py"]

---

# Implementation Report — Bridge INDEX Atomic-Write Guard (WI-4481)

## Summary

Implemented WI-4481 per GO@-002 (Antigravity/Gemini-LO, harness C), under the impl-start packet granted earlier this session (`sha256:6806241b0893e7a2aa9f040bc71548c2d76d215afa81b964efca89c8ed8fab94`) and now bound to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY via PAUTH-WI4481-INDEX-CLOBBER-GUARD-20260613.

A new role-agnostic PreToolUse hook (`.claude/hooks/bridge-index-write-serializer.py`) blocks raw agent `Write`/`Edit`/`MultiEdit`/`Bash`(redirect or write-cmdlet)/`apply_patch` mutations of `bridge/INDEX.md` and directs them to the serialized `gt bridge index` CLI, which holds the file lock and performs the atomic read-modify-merge in `scripts/bridge_index_writer.py`. The serialized CLI, INDEX reads, and non-INDEX writes pass unchanged. This closes the only remaining concurrent-write clobber path: all Python writers already route through the lock, and the prior race-quiesce thread fixed only the trigger's scheduling race — the unguarded agent-tool-write path (which caused the recurring lost/duplicated Document blocks and manual owner repair WI-4481 cites) is now closed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` (CLAUSE-INDEX-IS-CANONICAL) — INDEX integrity protected against concurrent-write corruption.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — hook registered with `.claude` + `.codex` parity.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping + executed evidence below.
- `GOV-STANDING-BACKLOG-001` — WI-4481 is the backlog authority for this bridge-integrity defect.

## Owner Decisions / Input

Owner directive (S437, multiple AskUserQuestion answers this session): (1) "Bind to BRIDGE-PROTOCOL-RELIABILITY" approved the PAUTH project home; (2) "implement a GO verdict, ignore claimed ownership" (current turn) authorized harness-B to drive WI-4481 to VERIFIED including releasing a stale claim from a prior harness-B session (6441d1) and acquiring mine to file this report. Captured as DELIB-20263143 (autonomous-backlog-loop directive applied narrowly to WI-4481 via PAUTH-WI4481-INDEX-CLOBBER-GUARD-20260613).

## Files Changed

1. `.claude/hooks/bridge-index-write-serializer.py` (NEW) — the guard hook. `gate_decision(payload)` returns a block for Write/Edit/MultiEdit whose `file_path` resolves to `bridge/INDEX.md`, for Bash commands with a redirect/write-cmdlet targeting `bridge/INDEX.md`, and for apply_patch hunks targeting `bridge/INDEX.md`; everything else (incl. the serialized CLI and reads) returns `{}`. Role-agnostic (PB + LO).
2. `.claude/settings.json` — registered the hook first in the existing `Write|Edit|MultiEdit|Bash` PreToolUse block.
3. `.codex/hooks.json` — parity: added `Bash` + `apply_patch` matcher blocks invoking the hook via direct python (matching the existing `document_author_provenance_gate.py` / `sot-read-discipline-bash-adapter.py` Codex pattern).
4. `platform_tests/hooks/test_bridge_index_write_serializer.py` (NEW, 16 tests) — guard regression tests across all surfaces + non-regression of the sanctioned route.

## Verification Evidence (commands + observed results)

```text
python -m pytest platform_tests/hooks/test_bridge_index_write_serializer.py platform_tests/scripts/test_bridge_index_writer.py -q --tb=short
-> 28 passed in 3.42s (16 guard tests + 12 serialized-writer tests, incl. T4 20-thread no-lost-update).
   (Re-confirmed this session: 28/28 still pass.)

python -m ruff check .claude/hooks/bridge-index-write-serializer.py platform_tests/hooks/test_bridge_index_write_serializer.py
-> All checks passed!

python -m ruff format --check .claude/hooks/bridge-index-write-serializer.py platform_tests/hooks/test_bridge_index_write_serializer.py
-> 2 files already formatted.
```

## Spec-to-Test Mapping

| Spec | Test evidence | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_write_to_index_is_blocked`, `test_edit_to_index_is_blocked`, `test_multiedit_to_index_is_blocked`, `test_absolute_index_path_is_blocked`, `test_bash_redirect_to_index_is_blocked`, `test_bash_append_to_index_is_blocked`, `test_powershell_set_content_index_is_blocked`, `test_apply_patch_targeting_index_is_blocked` — raw INDEX mutations blocked across all surfaces | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Bash + apply_patch surfaces covered by tests; hook registered in both `.claude/settings.json` and `.codex/hooks.json` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this mapping + the executed commands above | PASS |
| Sanctioned-route non-regression | `test_serialized_cli_add_document_passes`, `test_serialized_cli_set_status_passes`, `test_reading_index_passes`, `test_grep_literal_redirect_char_does_not_false_positive`, `test_write_to_non_*_passes`, `test_read_tool_passes`, + `test_bridge_index_writer.py` (12) | PASS |

## Scope Adherence

Implemented exactly the GO'd target_paths (4 files); no other files touched. The guard covers all agent write surfaces (Write/Edit/MultiEdit + Bash redirect/write-cmdlet + apply_patch), addressing the proposal's Bash-surface "follow-on" and the `.codex` apply_patch parity within the approved target_paths. Non-blocking follow-on (unchanged): removing the now-redundant `lo-file-safety-gate` INDEX-Edit permit (the new guard blocks first regardless) — file separately, out of this slice's PAUTH scope.

## Recommended Commit Type

`fix:` — closes the WI-4481 INDEX-clobber defect (recurring lost/duplicated-block corruption); no new feature surface beyond the integrity guard.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
