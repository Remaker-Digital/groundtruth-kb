NEW

bridge_kind: prime_proposal
Document: gtkb-bridge-index-atomic-write-guard
Version: 001
Author: Prime Builder (Claude, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 604f696d-dc7e-4abe-af6c-dd797bbf543b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

Work Item: WI-4481

target_paths: [".claude/hooks/bridge-index-write-serializer.py", ".claude/settings.json", ".codex/hooks.json", "platform_tests/hooks/test_bridge_index_write_serializer.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true

---

# Bridge INDEX Atomic-Write Guard — Close the Agent-Tool-Write Clobber Gap (WI-4481)

## Summary

WI-4481 (P1, `bridge-integrity`, defect): `bridge/INDEX.md` document blocks are lost or duplicated under concurrent writes, forcing recurring manual owner repair (counter to the owner-burden-reduction vision).

Root cause (confirmed by a read-only code map this session): the serialized INDEX writer `scripts/bridge_index_writer.py` ALREADY provides a Windows-safe file lock + atomic temp-then-`os.replace` + read-modify-**merge** (`atomic_index_update`), with a 20-thread "no lost update" regression test. EVERY Python writer (`gtkb_bridge_writer.insert_index_status`, `bridge/index_mutation.add_document`/`set_status`, `lo_bridge_process_helper`) routes through it safely; the cross-harness trigger is read-only for INDEX. The ONE remaining clobber path is **agent `Write`/`Edit` tool operations directly on `bridge/INDEX.md`**, which bypass the lock entirely — there is no PreToolUse hook forcing tool-writes through the serialized writer, and `lo-file-safety-gate` even permits a raw single-status-line Edit. So an interactive session (or a dispatched worker) editing INDEX races the locked writers with no merge, producing the lost/duplicated blocks WI-4481 cites (observed repeatedly this session; three dropped terminal entries were manually re-added via the serialized CLI).

This proposal closes that gap with a PreToolUse guard hook that blocks raw `Write`/`Edit` of `bridge/INDEX.md` and directs all mutations through the serialized `gt bridge index` CLI (`add-document` / `set-status`), which holds the lock. It does NOT modify the already-correct serialized writer, the INDEX format, the bridge protocol semantics, or dispatch behavior. It is bounded to the agent-tool-write surface.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` is canonical, append-only bridge workflow state (CLAUSE-INDEX-IS-CANONICAL); this fix protects its integrity against concurrent-write corruption.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — work item, target paths, and governing specs are linked before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the guard behavior to a regression test exercising the blocked-write and pass-through paths.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — the guard is registered with `.claude` + `.codex` parity per the harness hook-parity contract.
- `GOV-STANDING-BACKLOG-001` — WI-4481 is the backlog authority for this bridge-integrity defect.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — owner directive → work item → proposal → implementation report → verification preserve the artifact lifecycle; WI-4481 closes only after VERIFIED.

## Prior Deliberations

- `bridge/gtkb-cross-harness-trigger-index-edit-race-quiesce-008.md` (VERIFIED) — fixed the cross-harness trigger's *scheduling* race with a quiesce window, but explicitly did NOT close the general multi-writer atomicity gap. WI-4481 is that general fix; this proposal cites it to avoid re-treading the narrower trigger-race scope.
- `WI-4481` — the P1 `bridge-integrity` defect this implements (evidence per its MemBase record: a 2026-06-12 concurrent-bridge session in which a Document block was duplicated then lost and manually repaired by the owner).
- `scripts/bridge_index_writer.py` + `platform_tests/scripts/test_bridge_index_writer.py` (T4: 20-thread no-lost-update under the lock) — the already-VERIFIED serialized writer this guard routes all agent writes through; no change to it is proposed.
- `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-010.md` (VERIFIED) — the existing `lo-file-safety-gate` INDEX-Edit permit that this guard supersedes for raw writes.

## Owner Decisions / Input

Owner directive (S437, this session, via AskUserQuestion): the owner made both Codex (A) and Claude (B) active Prime Builders, redeployed harness B off TAFE (Codex saturates TAFE PB) to "another high-value project... where a 2nd PB genuinely adds capacity," and on the follow-up answered "Proceed" with this WI-4481 INDEX atomic-write fix, under the standing autonomous-loop directive ("the most difficult PB-actionable work item from the most valuable project... loop until all backlog items are implemented and VERIFIED"). That is the owner-decision evidence authorizing this implementation scope. Bridge integrity is additionally owner-pre-authorized as the top-priority invariant per `.claude/rules/bridge-essential.md`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (INDEX canonical + append-only), the `bridge-essential.md` integrity invariant, and WI-4481's defect definition fully specify the need: no agent may corrupt canonical INDEX via a non-serialized write. No new or revised requirement is needed; this is a defect fix making the code enforce the existing canonical-INDEX invariant against the previously-unguarded agent-tool-write path.

## Implementation Plan

1. **New PreToolUse guard hook** `.claude/hooks/bridge-index-write-serializer.py`: fires on `Write` and `Edit`. If the resolved target path is `bridge/INDEX.md`, BLOCK with a clear message directing the agent to the serialized CLI (`gt bridge index add-document --status <S> --path bridge/<slug>-NNN.md` for a new Document block; `gt bridge index set-status <slug> --status <S> --path bridge/<slug>-NNN.md` for a verdict/status line). All non-INDEX Write/Edit pass through unchanged; the block is INDEX-target-only and fail-closed.
2. **Register** the hook in `.claude/settings.json` PreToolUse (`Write|Edit` matcher), ordered ahead of the existing bridge gates so the redirect message is authoritative.
3. **Codex parity:** register the equivalent guard in `.codex/hooks.json` per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Codex PreToolUse fires on `Bash`/`apply_patch`; the adapter blocks INDEX mutations through those surfaces and directs to the CLI.
4. **Regression test** `platform_tests/hooks/test_bridge_index_write_serializer.py`: assert (a) `Write` to `bridge/INDEX.md` is blocked with the CLI-redirect message; (b) `Edit` to `bridge/INDEX.md` is blocked; (c) Write/Edit to a non-INDEX path passes; (d) the serialized `gt bridge index` route remains the sanctioned mutation path. Mirror the existing hook-test fixtures.

Residual (out of this slice, noted not silently dropped): (i) a Bash `>`/`open("w")` raw write of INDEX bypasses the Write/Edit-tool guard — the Write/Edit-tool path is the primary gap WI-4481 cites; a Bash-surface guard is a lower-frequency follow-on. (ii) Once this guard blocks INDEX Write/Edit first, the `lo-file-safety-gate` INDEX-Edit permit is dead for INDEX; removing it is a non-blocking cleanup follow-on (any blocking hook already blocks the write).

## Spec-Derived Verification Plan

```text
python -m pytest platform_tests/hooks/test_bridge_index_write_serializer.py -q --tb=short
Expected: pass; INDEX Write/Edit blocked + CLI-redirect message + non-INDEX pass-through.

python -m pytest platform_tests/scripts/test_bridge_index_writer.py -q --tb=short
Expected: pass; the serialized writer (sanctioned route) is unaffected, incl. T4 20-thread no-lost-update.

python -m ruff check .claude/hooks/bridge-index-write-serializer.py platform_tests/hooks/test_bridge_index_write_serializer.py
python -m ruff format --check .claude/hooks/bridge-index-write-serializer.py platform_tests/hooks/test_bridge_index_write_serializer.py
Expected: pass.
```

Spec mapping:
- `GOV-FILE-BRIDGE-AUTHORITY-001` → guard test proves raw tool-writes of canonical INDEX are blocked (integrity preserved).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` → parity registration verified via the harness hook-parity check.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` → the implementation report maps each linked spec to executed test evidence.

## Risk / Rollback

Risk: blocking INDEX Write/Edit could disrupt any workflow that currently raw-edits INDEX, notably LO verdict status-line Edits permitted by `lo-file-safety-gate`. Mitigation: the serialized CLI (`gt bridge index set-status`) is the sanctioned, already-working replacement, and the block message names it; the implementation report must demonstrate an LO verdict landing via `set-status`. Rollback: remove the hook registration from `.claude/settings.json` + `.codex/hooks.json` (single-line revert per file); the hook script + test are additive.

## Recommended Commit Type

`fix:` — closes the WI-4481 INDEX-clobber defect (recurring lost/duplicated-block corruption); no new feature surface beyond the integrity guard.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
