REVISED

# Implementation Proposal - Proposal-Standards Work-Item-ID Collision Gate (Slice 3) - REVISED-3

bridge_kind: implementation_proposal
Document: gtkb-proposal-standards-wi-id-collision-gate
Version: 007
Responds to: bridge/gtkb-proposal-standards-wi-id-collision-gate-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S354+

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-PROPOSAL-STANDARDS-SLICES-2-3
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS-SLICE3

target_paths: ["scripts/bridge_proposal_wi_id_collision_check.py", ".claude/hooks/bridge-proposal-wi-id-collision-gate.py", ".claude/settings.json", ".codex/hooks.json", ".codex/gtkb-hooks/wi-id-collision-gate.cmd", ".codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py", "platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py"]

This REVISED-3 (`-007`) lands GTKB-GOV-PROPOSAL-STANDARDS Slice 3: a pre-review hook that cross-references any `GTKB-ISOLATION-NNN` / `GTKB-DASHBOARD-NNN` / `GTKB-GOV-NNN` or `WI-NNNN` IDs cited in a bridge proposal against the standing backlog, flagging ID collisions before review. The hook fires on Claude `Write`/`Edit` proposal writes and on Codex `Bash` proposal writes.

## Revision Notes

This `-007` REVISED-3 addresses the single finding in the `-006` NO-GO (round-3 review), and carries forward all `-005` (round-2) and `-003` (round-1) fixes without regression.

### Round-3 NO-GO (`-006`) — finding-to-fix mapping

- **FINDING-P1-001 (P1) — claimed Codex `apply_patch` coverage is not designed, registered, or tested.** Resolved via the NO-GO's second acceptable shape (narrow the claim). The `-005` proposal claimed the hook covers Codex `Bash` *and* `apply_patch` proposal writes, but the proposed Codex implementation and tests cover only the `Bash` matcher; live `.codex/hooks.json` registers a separate `apply_patch` PreToolUse matcher, so an `apply_patch`-authored bridge write would bypass the gate while the proposal still claimed cross-surface coverage. This revision narrows the claim to match the actual implemented and tested scope: every statement of Codex `apply_patch` coverage is removed and narrowed to Codex `Bash` only. The narrowed surfaces are the opening paragraph, `## Claim`, IP-2b, the `ADR-CODEX-HOOK-PARITY-FALLBACK-001` line in `## Specification Links`, the verification plan, and the acceptance criteria. The residual Codex `apply_patch` coverage is recorded as an explicit deferred follow-on in `## Deferred Follow-On - Codex apply_patch Coverage`. **The implementation is unchanged from `-005`** — `-005` already implements and tests only the `Bash` adapter — so `-007` is a pure claim-narrowing revision that makes the proposal's stated scope equal its actual implemented/tested scope. No `apply_patch` implementation is added.

### Round-2 NO-GO (`-004`) fixes carried forward unchanged

- **Round-2 FINDING-P1-001 (P1) — Codex parity was claimed without a Codex payload path.** Resolved via the `-004` NO-GO's first acceptable shape: a Codex-side adapter is in scope. The Codex PreToolUse surface is not Claude `Write|Edit` — `.codex/hooks.json` registers PreToolUse matchers including `Bash`, and the existing bridge-compliance hook reaches Codex through `.codex/gtkb-hooks/bridge-compliance-gate.cmd` (a `cmd` wrapper) plus `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py` (a Python adapter that extracts pending bridge-write content from Codex `Bash` commands and synthesizes a Claude-shaped `Write` payload for the canonical hook). This revision mirrors that precedent for the Codex `Bash` surface:
  - `target_paths` adds `.codex/gtkb-hooks/wi-id-collision-gate.cmd` (the Codex `cmd` wrapper) and `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py` (the Codex Bash adapter).
  - IP-2b describes the adapter: it loads the Codex `PreToolUse` Bash payload, reuses the same bridge-write extraction approach as `bridge-compliance-gate-bash-adapter.py` (heredoc / `cat`/`printf`/`echo` redirect / `tee` / `Path(...).write_text(...)` shapes targeting `bridge/<slug>-NNN.md`), and either invokes the shared collision engine in-process or synthesizes a Claude-shaped `Write` payload for `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`.
  - `.codex/hooks.json` registration points at the runnable `wi-id-collision-gate.cmd` wrapper under a `Bash` matcher (the Codex idiom), not at the Claude `Write|Edit` hook directly.
  - IP-3 adds tests that feed representative Codex `Bash` hook payloads (a heredoc bridge-proposal write) through the adapter and prove collision detection plus the no-op pass-through for non-bridge Codex commands.
- **Round-2 FINDING-P1-002 (P1) — the claimed `Write|Edit` hook path was only tested for `Write`.** Resolved by specifying and testing Edit handling. IP-2a now states the Claude hook's Edit-payload behavior explicitly: for an `Edit` tool call the hook reads `new_string` (the post-edit content fragment), consistent with the `credential-scan.py` precedent that scans `content` for `Write` and `new_string` for `Edit`. Because an Edit payload is a fragment, the hook runs the collision scan over the `new_string` text — a WI ID introduced or altered by the edit is therefore in-scope. IP-3 adds Edit-payload regression tests: collision on Edit, no-collision on Edit, and fail-open on Edit when MemBase is unreachable. The verification plan and acceptance criteria name the Edit tests, so the stated `Write|Edit` contract is provable at post-implementation verification.

### Round-1 NO-GO (`-002`) fixes carried forward unchanged

- **Round-1 FINDING-P1-001 (P1) — the required pre-review hook was not in implementation scope.** Resolved via that NO-GO's Option 1: the pre-review hook integration is implemented in this slice. `target_paths` includes `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` (the hook), `.claude/settings.json` (Claude-side `PreToolUse(Write|Edit)` registration), and `.codex/hooks.json` (Codex-side parity registration). The standalone CLI from `-001` is retained as IP-1 — it is the reusable engine the hook calls — but Slice 3 is claimed complete only when the hook path lands.
- **Round-1 FINDING-P1-002 (P1) — the verification command targeted a nonexistent root `tests/` tree.** Resolved. `target_paths` lists no `tests/scripts/...`; the live checkout has no root `tests/` directory. The authorized test file is `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`, and the run command executes exactly that path.
- **Round-1 advisory preflight omissions** (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`). Resolved. All three remain cited in `## Specification Links`.

The collision-detection logic itself (the `(?:GTKB-[A-Z]+-\d+|WI-\d+)` pattern, MemBase lookup, code-fence exclusion) is unchanged from `-001`.

## Claim

A new `PreToolUse(Write|Edit)` hook, `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`, fires when the tool target is a `bridge/<slug>-NNN.md` proposal file. It invokes the collision engine in `scripts/bridge_proposal_wi_id_collision_check.py`, which scans the proposed content for any `(?:GTKB-[A-Z]+-\d+|WI-\d+)` ID, looks each up in MemBase `current_work_items`, and reports any ID that exists but does NOT match the proposal's `Work Item:` metadata declaration. For a `Write` tool call the hook scans `content`; for an `Edit` tool call it scans `new_string` (the post-edit fragment), per the `credential-scan.py` Edit-payload precedent. Codex-authored proposal writes that arrive as Codex `Bash` tool calls (not Claude `Write|Edit`) are covered by a Codex Bash adapter `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py` wired through `.codex/gtkb-hooks/wi-id-collision-gate.cmd`, mirroring the existing `bridge-compliance-gate` Codex Bash adapter. Codex `apply_patch`-authored proposal writes are NOT covered by this slice; that residual cross-harness parity gap is recorded as an explicit deferred follow-on (see `## Deferred Follow-On - Codex apply_patch Coverage`). The hook is **advisory by default** — it surfaces collisions in its hook output without blocking the Write/Edit — consistent with the Slice-1/Slice-2 proposal-standards posture; `--strict` on the CLI returns a non-zero exit for explicit/CI use.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the pre-review hook protects the integrity of the bridge review packet by catching WI-ID collisions before review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposals must cite specs; this gate enforces internal consistency on the WI IDs a proposal cites.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives every test from a linked spec.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `GOV-STANDING-BACKLOG-001` - the gate cross-references cited IDs against the standing backlog (`current_work_items`); `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` is itself a tracked WI.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the hook is registered in both `.claude/settings.json` and `.codex/hooks.json`; the Codex-side surface uses a Bash adapter because the live Codex PreToolUse `Bash` matcher is the Codex idiom, not Claude `Write|Edit`. This slice covers the Codex `Bash` surface only; the residual Codex `apply_patch` surface is a deferred follow-on (see `## Deferred Follow-On - Codex apply_patch Coverage`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the hook is a governed enforcement artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, hook, adapter, and CLI form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the hook fires on the bridge-proposal write/edit lifecycle event.

## Prior Deliberations

- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - batch-2 owner authorization for `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` and its Slice 2/3 work items.
- `DELIB-0990` - prior Loyal Opposition review for `gtkb-gov-proposal-standards-slice1`; parent-thread context for keeping proposal-standards behavior concrete and mechanically enforceable.
- `DELIB-0991` - prior Loyal Opposition review for the proposal-standards family; reinforces that proposal-standards checks must execute mechanically on the claimed path, not as optional diagnostics — applied here by making the Codex `Bash` path real rather than only claimed, and by narrowing the claim so it no longer asserts an untested `apply_patch` path.
- `DELIB-0993` - prior Loyal Opposition review for `gtkb-gov-proposal-standards-slice1`; establishes the proposal-standards enforcement-family intent that this slice's hook satisfies.
- `DELIB-1738` - prior pre-filing hook NO-GO holding that a hook proposal must validate the pending hook content and must specify how Edit payloads are handled; this revision's IP-2a Edit-payload specification and IP-3 Edit regression tests directly answer that precedent.
- `bridge/gtkb-proposal-standards-test-claim-rerun-verifier-002.md` - sibling Slice-2 review identifying the same scope-alignment and test-surface class of defects; this revision applies the same corrections, including narrowing the claim to the surface that is actually implemented and tested.

No retrieved deliberation waives the bridge requirement that an implementation proposal map the operative work item to concrete, executable verification, nor the proposal-standards family's intent that checks fire mechanically before review, nor cross-harness parity, nor the `DELIB-1738` requirement that Edit handling be specified and tested. The `-006` NO-GO confirmed that no searched deliberation waives the need to cover the actual Codex matcher the proposal claims; this revision honors that by claiming only the Codex `Bash` surface it implements and tests.

## Owner Decisions / Input

This proposal is filed under an active project authorization and is authorized by:

- 2026-05-14 UTC, S350+: owner AUQ "Authorize all 3 groups (7 WIs added)" — authorized `PROJECT-GTKB-GOV-PROPOSAL-STANDARDS` including `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3`. Recorded as `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`.

No new owner decision is required for this revision. `-007` is a pure claim-narrowing revision: it removes the untested Codex `apply_patch` coverage claim, narrows every affected surface to the Codex `Bash` coverage that is actually implemented and tested, and records the residual `apply_patch` gap as a named deferred follow-on. The implementation, tests, and `target_paths` are unchanged from `-005`; the round-2 and round-1 fixes are carried forward unchanged.

## Requirement Sufficiency

Existing requirements sufficient. The `GTKB-GOV-PROPOSAL-STANDARDS-SLICE3` work-item description — "a pre-review hook that cross-references `GTKB-ISOLATION-NNN`, `GTKB-DASHBOARD-NNN`, `GTKB-GOV-NNN` mentions against the standing backlog and flags ID collisions before review" — is the operative requirement. This revision implements that requirement as written, including Claude `Write|Edit` coverage and Codex `Bash` coverage so the hook fires on Claude-authored proposal writes and on Codex `Bash`-authored ones. Codex `apply_patch` coverage is a residual cross-harness parity gap deferred to a separate NEW bridge proposal (see `## Deferred Follow-On - Codex apply_patch Coverage`). No new or revised requirement or specification is created.

## Deferred Follow-On - Codex apply_patch Coverage

Codex's PreToolUse surface includes a separate `apply_patch` matcher in addition to the `Bash` matcher (live `.codex/hooks.json`). A Codex-authored bridge proposal filed through the `apply_patch` tool is therefore NOT inspected by the Codex `Bash` adapter this slice delivers. This is a known residual cross-harness parity gap.

This slice deliberately scopes Codex coverage to the `Bash` surface only, because:

- The `Bash` surface is the surface for which a proven precedent adapter exists (`.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`), so the `Bash` adapter is designable, registrable, and testable within this slice without new payload-extraction research.
- An `apply_patch` payload-extraction path is a distinct design problem (the `apply_patch` payload shape differs from a Bash command string) and would expand this thread's scope after multiple revisions — the scope expansion that prior rounds flagged.

Codex `apply_patch` proposal-write coverage is deferred to a separate NEW bridge implementation proposal. Suggested slug: `gtkb-wi-id-collision-gate-apply-patch-coverage`. That follow-on proposal will design the `apply_patch` payload-extraction path, register the collision gate for the `apply_patch` matcher, add any adapter/wrapper `target_paths`, and add tests feeding a representative `apply_patch` bridge-proposal payload through the gate. It is a separate proposal so that this slice's claim equals its implemented and tested scope.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (`GTKB-GOV-PROPOSAL-STANDARDS-SLICE3`). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "standing backlog", and "backlog" describe the single Slice-3 work item and the collision engine's read-only lookup against `current_work_items`. The review-packet inventory is one bridge thread: IP-1 (collision-check engine) + IP-2a (Claude pre-review hook + registration) + IP-2b (Codex Bash adapter + registration) + IP-3 (tests). The Slice-3 project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch2-three-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-007` REVISED line is inserted under the existing `Document: gtkb-proposal-standards-wi-id-collision-gate` entry above the prior `-006` NO-GO, `-005` REVISED, `-004` NO-GO, `-003` REVISED, `-002` NO-GO, and `-001` NEW lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Collision-detection engine CLI

`scripts/bridge_proposal_wi_id_collision_check.py`:

1. Read bridge proposal content (from `bridge/<bridge-id>-NNN.md`, or from stdin / a passed-content path when invoked by the hook or adapter on a not-yet-written file).
2. Parse the `Work Item:` metadata line for the declared WI.
3. Extract all `(?:GTKB-[A-Z]+-\d+|WI-\d+)` ID patterns from the document, **excluding** IDs inside fenced code blocks.
4. For each unique ID, query `current_work_items` for the row.
5. If a cited ID exists in MemBase as a WI different from the declared `Work Item:`, flag it as a collision in the output JSON.
6. Emit a `Collision Check` markdown section: a table of `cited_id`, `exists_in_membase`, `matches_declared`.
7. Exit 0 by default; exit non-zero only when `--strict` is passed AND collisions are present.
8. Expose a `check_content(text, declared_wi) -> CollisionResult` function so the hook and the Codex adapter can call the engine in-process without re-reading a file.

### IP-2a: Claude pre-review hook + Claude registration (round-1 + round-2 FINDING-P1-002 closure)

`.claude/hooks/bridge-proposal-wi-id-collision-gate.py` — a `PreToolUse(Write|Edit)` hook:

- **Trigger point:** the hook reads the tool input; it acts only when the write target path matches `bridge/<slug>-NNN.md` (a bridge proposal/report file). For any other path it is a no-op pass-through.
- **Payload extraction (Write and Edit):** for a `Write` tool call the hook scans `tool_input["content"]`; for an `Edit` tool call it scans `tool_input["new_string"]` — the post-edit content fragment — mirroring `.claude/hooks/credential-scan.py`, which scans `content` for Write and `new_string` for Edit. An Edit payload is a fragment, so the collision scan runs over the `new_string` text; a WI ID introduced or altered by the edit is therefore in-scope of the check. The declared `Work Item:` is read from the same payload text when present; if the Edit fragment does not contain the `Work Item:` line, the hook treats the declared WI as unknown and reports cited IDs without a false collision.
- **Behavior:** it calls `bridge_proposal_wi_id_collision_check.check_content(...)`, and:
  - When no collision is found: emits a normal pass (no `decision` field; the Write/Edit proceeds).
  - When a collision is found: emits an **advisory** hook result that surfaces the collision table in the hook output WITHOUT a `block` decision, so the Write/Edit still proceeds. This matches the Slice-1/Slice-2 proposal-standards posture (mechanically fires on every proposal write/edit, surfaces the defect, does not hard-block). Advisory-not-blocking is the deliberate bypass behavior: a legitimate cross-reference to another WI is common, so the hook informs the reviewer rather than refusing the write.
- **Failure mode:** if MemBase is unreachable, the hook emits a non-blocking diagnostic and passes (fail-open) — it must never block a proposal write/edit because of an infrastructure error.
- **Registration:** add the hook to the existing `PreToolUse(Write|Edit)` matcher block in `.claude/settings.json` (alongside `bridge-compliance-gate.py`).

### IP-2b: Codex Bash adapter + Codex registration (round-2 FINDING-P1-001 closure)

The Codex PreToolUse `Bash` matcher is the Codex idiom for intercepting shell-authored bridge writes; Codex-authored bridge writes performed through the `Bash` tool arrive as shell commands. To give Codex parity on the `Bash` surface, this slice adds a Codex adapter mirroring the existing `.codex/gtkb-hooks/bridge-compliance-gate*` pattern:

- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py` — a Python adapter that:
  - Loads the Codex `PreToolUse` payload from stdin and reads the Bash `command` string.
  - Extracts the pending bridge-write target path and candidate content using the same bridge-write-extraction approach as `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py` (heredoc `cat > bridge/<slug>-NNN.md << TAG`, `cat`/`printf`/`echo` redirect, `tee`, and `Path(...).write_text(...)` shapes). For any command that is not a bridge-proposal write it prints `{}` and exits 0 (no-op pass-through).
  - Invokes the shared collision engine — either `bridge_proposal_wi_id_collision_check.check_content(...)` directly, or by synthesizing a Claude-shaped `Write` payload (`{"tool_name": "Write", "tool_input": {"file_path": ..., "content": ...}}`) and running `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` as a subprocess, exactly as `bridge-compliance-gate-bash-adapter.py` does for the canonical compliance hook.
  - Surfaces the advisory collision result; never blocks (same advisory-by-default and fail-open posture as the Claude hook).
- `.codex/gtkb-hooks/wi-id-collision-gate.cmd` — a one-line `cmd` wrapper that invokes the Python adapter, mirroring `.codex/gtkb-hooks/bridge-compliance-gate.cmd`.
- **Registration:** add a `Bash`-matcher `PreToolUse` entry to `.codex/hooks.json` whose command runs `cmd /d /s /c E:\GT-KB\.codex\gtkb-hooks\wi-id-collision-gate.cmd`, alongside the existing `bridge-compliance-gate.cmd` entry. The `.codex/hooks.json` registration therefore points at a runnable adapter, not at the Claude `Write|Edit` hook.

This slice covers the Codex `Bash` surface only. The separate Codex `apply_patch` PreToolUse matcher is not registered or adapted here; that residual surface is the deferred follow-on documented in `## Deferred Follow-On - Codex apply_patch Coverage`.

### IP-3: Tests

`platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` covers the engine, the Claude hook (Write and Edit), and the Codex Bash adapter:

- Engine: collision detection, no-collision, multiple-collision, strict-mode exit code, default exit code, output JSON schema, code-fence exclusion.
- Claude hook — Write: fires on a `bridge/<slug>-NNN.md` Write, no-op on a non-bridge path, advisory (does not block) on collision, fail-open on MemBase error.
- Claude hook — Edit: fires on a `bridge/<slug>-NNN.md` Edit reading `new_string` and reports a collision; no-collision on an Edit payload; fail-open on an Edit payload when MemBase is unreachable.
- Codex Bash adapter: a representative Codex `Bash` heredoc bridge-proposal write is fed through `wi-id-collision-gate-bash-adapter.py` and a collision is detected; a non-bridge Codex `Bash` command is a no-op pass-through.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-STANDING-BACKLOG-001` | a cited alien WI (exists in `current_work_items`, not the declared WI) is flagged as a collision | `test_collision_detected_on_alien_wi` |
| `GOV-STANDING-BACKLOG-001` | no collision when only the declared WI is cited | `test_no_collision_when_only_declared_wi` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | multiple distinct collisions are each enumerated | `test_multiple_collisions_listed` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the pre-review hook fires on a `bridge/<slug>-NNN.md` Write and reports the collision | `test_hook_fires_on_bridge_proposal_write` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the hook is a no-op pass-through on a non-bridge path | `test_hook_noop_on_non_bridge_path` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the hook fires on a `bridge/<slug>-NNN.md` Edit, scans `new_string`, and reports a collision introduced by the edit | `test_hook_fires_on_bridge_proposal_edit` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the hook reports no collision on an Edit payload that introduces only the declared WI | `test_hook_no_collision_on_edit` |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | the hook is advisory: on a collision it surfaces the table but does NOT emit a `block` decision (Write) | `test_hook_advisory_does_not_block_on_collision` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | the Claude hook fails open (non-blocking diagnostic) when MemBase is unreachable, on both Write and Edit payloads | `test_hook_fail_open_on_membase_error`, `test_hook_fail_open_on_membase_error_edit` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | a representative Codex `Bash` heredoc bridge-proposal write fed through `wi-id-collision-gate-bash-adapter.py` detects a collision | `test_codex_adapter_detects_collision_on_bash_write` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | the Codex Bash adapter is a no-op pass-through on a non-bridge Codex `Bash` command | `test_codex_adapter_noop_on_non_bridge_command` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (proposal-standards posture) | `--strict` returns a non-zero exit on collision; default returns exit 0 | `test_strict_mode_exits_nonzero_on_collision`, `test_default_exit_zero_on_collision` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | the output JSON conforms to the documented schema | `test_output_json_schema` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | IDs inside fenced code blocks are ignored (avoids false positives from example code) | `test_ignore_ids_in_fenced_code_blocks` |

Run: `python -m pytest platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py -v --tb=short`.

Lint: `python -m ruff check scripts/bridge_proposal_wi_id_collision_check.py .claude/hooks/bridge-proposal-wi-id-collision-gate.py .codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`.

JSON validity check after editing `.claude/settings.json` and `.codex/hooks.json`: `python -c "import json,pathlib; [json.loads(pathlib.Path(p).read_text()) for p in ('.claude/settings.json','.codex/hooks.json')]"`.

## Acceptance Criteria

- IP-1 (engine), IP-2a (Claude hook + registration), IP-2b (Codex Bash adapter + wrapper + registration), IP-3 (tests) landed; all tests in `test_bridge_proposal_wi_id_collision_check.py` PASS.
- The Claude hook is registered in `.claude/settings.json` `PreToolUse(Write|Edit)`; the Codex `Bash`-matcher entry in `.codex/hooks.json` runs `.codex/gtkb-hooks/wi-id-collision-gate.cmd`; both files remain valid JSON.
- The Claude hook fires on a `bridge/<slug>-NNN.md` Write and on an Edit (scanning `new_string`), is a no-op on non-bridge paths, is advisory (does not block) on a collision, and fails open on a MemBase error — all proven by tests, including the Edit-payload tests (round-2 FINDING-P1-002 resolved).
- The Codex Bash adapter `wi-id-collision-gate-bash-adapter.py` detects a collision on a representative Codex `Bash` heredoc bridge write and is a no-op on non-bridge Codex `Bash` commands — proven by tests (round-2 FINDING-P1-001 resolved).
- The proposal claims Codex coverage for the `Bash` surface only; Codex `apply_patch` coverage is explicitly out of scope and deferred to a named follow-on proposal (round-3 FINDING-P1-001 resolved by claim narrowing).
- The verification command runs `platform_tests/scripts/test_bridge_proposal_wi_id_collision_check.py` and collects all tests successfully (no nonexistent root `tests/` path; round-1 FINDING-P1-002 resolved).
- Both bridge preflights PASS for this proposal (`-007`).
- `ruff check` is clean on the touched script, hook, and Codex adapter.
- Slice 3 is claimed complete only because the pre-review hook path (Claude `Write|Edit` + Codex `Bash`) lands in this slice.

## Risks / Rollback

- Risk: legitimate cross-references to other WIs (e.g., dependency listings) get flagged. Mitigation: the hook and the Codex adapter are advisory by default — they surface the collision for reviewer judgment and never block the Write/Edit; `--strict` non-zero is reserved for explicit CLI/CI use.
- Risk: the hook adds latency to every Write/Edit. Mitigation: the hook is a no-op pass-through for any non-`bridge/` path; the MemBase lookup runs only for bridge-proposal writes/edits, and a 5s hook timeout (matching the sibling hooks) bounds it.
- Risk: a Codex-authored proposal write through the `apply_patch` tool is not inspected. Mitigation: this is the known residual gap recorded as the deferred follow-on (`## Deferred Follow-On - Codex apply_patch Coverage`); it does not regress any current behavior — today no WI-ID collision gate exists on any Codex surface — and the `Bash` surface (the surface with a proven precedent adapter) is covered.
- Risk: the Codex Bash adapter fails to extract content from an uncommon write shape. Mitigation: the adapter reuses the proven extraction approach from `bridge-compliance-gate-bash-adapter.py`; an extraction miss results in a non-blocking skip diagnostic (fail-open), never a blocked write.
- Risk: a MemBase error blocks proposal writes. Mitigation: the Claude hook and the Codex adapter both fail open with a non-blocking diagnostic (tested on Write and Edit).
- Rollback: remove `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`, `.codex/gtkb-hooks/wi-id-collision-gate.cmd`, and `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`; revert the registration lines in `.claude/settings.json` and `.codex/hooks.json`; and remove `scripts/bridge_proposal_wi_id_collision_check.py`. No existing surface is otherwise modified.

## Recommended Commit Type

`feat` - a new pre-review hook, a Codex Bash adapter for cross-harness parity, the collision-detection engine, and tests; a new mechanical-enforcement capability. The `.claude/settings.json` / `.codex/hooks.json` edits are registration of the new hook/adapter, part of the same feature.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-007` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`

- packet_hash: `sha256:e037db7721ca9fa7caf220539ccdba9f0478446765d4df07eb430daa5ada09bf`
- bridge_document_name: `gtkb-proposal-standards-wi-id-collision-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md`
- operative_file: `bridge/gtkb-proposal-standards-wi-id-collision-gate-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-proposal-standards-wi-id-collision-gate`

- Bridge id: `gtkb-proposal-standards-wi-id-collision-gate`
- Operative file: `bridge\gtkb-proposal-standards-wi-id-collision-gate-007.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
