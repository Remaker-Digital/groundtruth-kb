NEW

# gtkb-wi5083-startup-input-gate-rearm-fix — Startup-input gate must not re-arm on a mid-session continuation

bridge_kind: prime_proposal
Document: gtkb-wi5083-startup-input-gate-rearm-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 054bb30f-56ef-436b-a5d6-ad07f7b29dd6
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive session; resolved_role=prime-builder (session-stated ::init gtkb pb)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5083

target_paths: ["scripts/session_start_dispatch_core.py", "scripts/session_self_initialization.py", "scripts/workstream_focus.py", ".codex/gtkb-hooks/session_wrapup_trigger_dispatch.py", "platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py", "platform_tests/scripts/test_session_continuation_sources_parity.py", "platform_tests/scripts/test_session_start_dispatch_core.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The GT-KB startup-input gate (GTKB-STARTUP-INPUT-GATE) exists so the SessionStart
init-keyword disclosure relay owns a genuinely-fresh session's first owner prompt.
It is armed by a SessionStart-side hook (the discard_next_user_prompt /
startup_response_pending flags in session-lifecycle-guard.json) and cleared only
by a subsequent UserPromptSubmit.

WI-5083 is the verified defect that the arm re-fires on every SessionStart —
including mid-session compaction/resume — so the gate is re-armed mid-session.
Because the clear is bound only to UserPromptSubmit, a tool call or an
AskUserQuestion answer (neither is a UserPromptSubmit) cannot clear it, and the
gate readers block authorized shell tools until the owner happens to type or the
30-minute expiry fires. WI-5083 was observed blocking authorized PowerShell/Bash
tool calls three separate times during real owner-requested work, requiring an
extra owner message to clear the gate each time.

Verified root cause (two mechanisms in combination): (1) the shared SessionStart
entrypoint scripts/session_start_dispatch_core.py::main() never reads the
SessionStart hook stdin, so it discards the source field and invokes the arming
startup service on every SessionStart; (2) the arm's idempotency guard is dead
code because it keys on startup_guard_id == guard_id while guard_id defaults to a
fresh timestamp per call. So discard_next_user_prompt is re-armed True even after
the fresh-start gate was already consumed.

The fix has two parts. Fix (a) — root cause: thread the SessionStart source
(startup / resume / compact / clear) from the dispatcher into the startup
service, and arm the gate only on a genuinely-fresh start; a mid-session
continuation (resume / compact) no longer re-arms. This corrects the guard state
every reader consults. Fix (b) — belt-and-suspenders: record armed_source on each
arm, and teach the tracked readers to treat a continuation-armed gate as stale
rather than blocking, preserving the legitimate fresh-start guard. Every change is
additive and fail-soft: an absent/unread source degrades to "startup" (pre-WI-5083
behavior), and the legitimate fresh-start await still blocks.

The exact old-block to new-block replacements and full new test files are recorded
in the verified review-ready implementation package WI-5083-startup-gate-rearm-review-package.md
(sections 3 through 6 for source, section 5 for tests). This proposal authorizes
applying those blocks across the listed target_paths under the reliability
fast-lane.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — reliability fast-lane for small defect fixes; this WI's project home (PROJECT-GTKB-RELIABILITY-FIXES) and the governing authority for a bounded, spec-linked defect fix.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` — the startup relay owns the genuinely-first prompt of a fresh session; the gate must not spuriously own mid-session prompts, which is exactly the behavior this fix restores.
- `GOV-SESSION-SELF-INITIALIZATION-001` — fresh-session self-initialization contract; the arm belongs to a genuinely-fresh SessionStart, not a continuation.
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` — the init-keyword disclosure-relay contract the gate serves; the fix keeps the relay window intact for a fresh start while removing the mid-session re-arm.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — SessionStart hot-path budget; the new source reader is stdlib-light and fail-soft, adding no measurable startup cost.
- `ADR-CROSS-HARNESS-PARITY-001` — cross-harness parity for the Codex-side reader change (session_wrapup_trigger_dispatch.py) and the reconcile-on-merge of the git-untracked Claude reader.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline governing this proposal and its verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal must cite every relevant governing spec (satisfied here).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/PAUTH/WI linkage metadata present (WI-5083 / PROJECT-GTKB-RELIABILITY-FIXES / PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED requires spec-derived tests; the Spec-Derived Verification Plan below maps each linked spec to executed tests.
- `GOV-STANDING-BACKLOG-001` — MemBase work_items is the canonical backlog authority; WI-5083 is tracked there and is now a member of PROJECT-GTKB-RELIABILITY-FIXES.

## Prior Deliberations

Deliberation semantic search was run for this topic on the canonical MemBase
(query: "startup input gate rearm mid-session compaction resume"). It surfaced
adjacent startup-relay work (DELIB-20261085 / DELIB-20261228 startup-payload +
compact SessionStart context; DELIB-1083 startup token / premature wrap-up;
DELIB-20261025 startup disclosure relay truncation; DELIB-20265224 interactive
role persistence across contiguous sessions) but no prior decision on the
mid-session re-arm defect specifically. The closest prior art is the bridge-thread
history of the gate machinery itself:

- `gtkb-codex-wrapup-startup-gate-guard-sot-001` (…004) — origin of the `_startup_input_gate_active` reader and the SoT lifecycle-guard path; records the incident where GTKB-STARTUP-INPUT-GATE "blocked all shell commands as stale." Directly adjacent prior art; WI-5083 corrects when the gate is armed rather than removing it.
- `gtkb-loyal-opposition-startup-symmetry-001` (…010) — the guard blocked-reason wording and the explicit finding that "the guard path itself remains valuable (it prevents tool use during the disclosure-relay-then-await window)." WI-5083 preserves that guard and only corrects when it is armed.
- `gtkb-startup-relay-pretooluse-read-exemption-001` (…005) — the Read/Grep/Glob exemption on the startup gate; explains why reads are exempt while shell tools are blocked (the observed WI-5083 stall class).
- `gtkb-session-start-formalization-001` (…012) — the SessionStart arming machinery (`_arm_startup_interaction_guard`) this fix gates.
- `gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004` — extraction of the shared `session_start_dispatch_core`; the shared-core parity contract this change must respect.

This proposal differs from all of the above by fixing the arm trigger (fresh vs
continuation) at the source, not the reader wording or the read-exemption set.

## Owner Decisions / Input

This proposal depends on owner approval. Authorizing evidence:

- **Owner task directive (this session, 2026-07-09, interactive Prime Builder, harness B):** "complete WI-5083 through the full governed bridge cycle … route the governed cycle through canonical + a Loyal Opposition counterpart." Authorizes filing this NEW proposal and running the propose → GO → implement → report → VERIFIED cycle for WI-5083 on the canonical tree. `detected_via: owner_directive`.
- **AUQ (prior worktree session `quizzical-bun-93f523`, `detected_via: ask_user_question`):** "How should I execute WI-5083's bridge protocol?" → "Implement in-worktree now" (LO GO + MemBase records deferred to merge/dispatch review).
- **AUQ (prior worktree session, `detected_via: ask_user_question`):** "In-worktree governed implementation is mechanically blocked — how should I land WI-5083?" → "Review-ready package."

The two worktree AUQs authorized producing the verified review-ready package (the
source of the exact old→new blocks); the current owner task directive authorizes
running the real governed cycle on the canonical tree. Implementation authority
remains gated by Loyal Opposition GO plus the implementation-start authorization
packet. Project-scope owner-approval evidence is
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (reliability fast-lane standing
authorization, governed by DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION), which
covers WI-5083 by active project membership.

## Requirement Sufficiency

Existing requirements sufficient. This is a defect fix under
`GOV-RELIABILITY-FAST-LANE-001` against the existing startup-relay contract
(`PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001`,
`DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`,
`GOV-SESSION-SELF-INITIALIZATION-001`). No new requirement is needed to authorize
it. Candidate spec for the reviewer's consideration (not required for this fix):
a future `DCL-STARTUP-GATE-FRESH-START-ONLY-001` capturing "the startup-input gate
arms only on a genuinely-fresh SessionStart source" would make the corrected
behavior a first-class, testable constraint; recording it is optional and out of
scope for this reliability-fast-lane fix.

## Spec-Derived Verification Plan

Each linked spec is verified by executed tests. Interpreter: the project venv
(`groundtruth-kb/.venv/Scripts/python.exe`).

Spec-to-test mapping:

- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` + `GOV-RELIABILITY-FAST-LANE-001` (Fix a — arm only on a genuinely-fresh start) → `platform_tests/scripts/test_session_self_initialization_startup_gate_rearm.py` (continuation source does not re-arm an active gate; fresh/absent source arms and records armed_source).
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001` + `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` (Fix b — a continuation-armed gate does not block, but the legitimate fresh-start await still blocks) → the two appended cases in `platform_tests/hooks/test_workstream_focus.py` (`test_continuation_armed_gate_does_not_block_tool_use`, `test_fresh_armed_gate_still_blocks_within_window`).
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` (fail-soft source reader) → the appended cases in `platform_tests/scripts/test_session_start_dispatch_core.py` (`_read_session_start_source` extracts source; returns None on tty/empty/bad-json/absent).
- `ADR-CROSS-HARNESS-PARITY-001` (the continuation-sources constant is duplicated across three hot-path modules) → `platform_tests/scripts/test_session_continuation_sources_parity.py` (asserts the copies stay equal, mirroring the `_SESSION_ROLE_MARKER_NAME` parity contract).

Verification commands (run in a gate-satisfied environment after applying the
package blocks):

- Targeted regression: pytest the four test targets above with `-q --tb=short`.
- Wider guard: pytest `platform_tests/scripts/test_session_self_initialization.py`, `test_claude_session_start_dispatcher.py`, `test_codex_session_start_dispatcher.py`.
- Code quality, BOTH separate gates on the changed .py: `python -m ruff check <changed>` AND `python -m ruff format --check <changed>`.
- Cross-harness parity: `python scripts/check_codex_hook_parity.py`.

Acceptance: all four targeted test files pass; wider suites remain green; ruff
check and ruff format --check both pass on the changed files; the Codex hook
parity check does not drift.

## Cross-Harness Disposition

This proposal touches harness-surface files (`.codex/gtkb-hooks/**` and, at
reconcile, `.claude/hooks/**`), so per `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
(assertion PARITY-DISPOSITION-GATE; `ADR-CROSS-HARNESS-PARITY-001` Q8) the
per-harness disposition is declared here. Disposition: **full behavioral parity
across all affected harnesses; no waiver requested.**

- **Shared core (both harnesses):** Fix (a) lands in
  `scripts/session_start_dispatch_core.py` and
  `scripts/session_self_initialization.py`, the shared SessionStart entrypoint
  that BOTH the Claude wrapper (`.claude/hooks/session_start_dispatch.py`) and the
  Codex wrapper (`.codex/gtkb-hooks/session_start_dispatch.py`) delegate to. Both
  harnesses inherit the fresh-vs-continuation arm gating identically. A harness
  whose SessionStart stdin lacks `source` degrades to "startup" (pre-WI-5083
  behavior) on both sides.
- **Claude harness:** the tracked reader `scripts/workstream_focus.py` gains the
  continuation-armed staleness guard (Fix b). The git-untracked Claude reader
  `.claude/hooks/session-topic-envelope-router.py` receives the same one-line
  guard at reconcile (see Reconcile-Only Untracked Reader below); it is
  defense-in-depth because Fix (a) prevents the continuation arm at the source.
- **Codex harness:** the mirrored reader
  `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` gains the identical
  continuation-armed staleness guard, keeping the `_startup_input_gate_active`
  reader behaviorally equal to its Claude twin.
- **Parity enforcement:** the
  `_SESSION_CONTINUATION_SOURCES = frozenset({"resume", "compact"})` constant is
  intentionally duplicated (not imported) across the three hot-path modules to
  keep each SessionStart path import-light, mirroring the existing
  `_SESSION_ROLE_MARKER_NAME` duplicate-with-parity pattern.
  `platform_tests/scripts/test_session_continuation_sources_parity.py` asserts the
  copies stay equal, and `python scripts/check_codex_hook_parity.py` must not
  drift after the change.

## Reconcile-Only Untracked Reader

`.claude/hooks/session-topic-envelope-router.py` is the Claude twin of the
Codex `_startup_input_gate_active` reader. It is git-untracked in the canonical
tree (not in target_paths, since target_paths lists governed/tracked files). Per
package section 6, the same one-line continuation-armed staleness guard is applied
to it during implementation so both harness readers match and the Codex hook
parity check does not drift. Fix (a) prevents the continuation arm at the source,
so this reader change is defense-in-depth only.

## Risk / Rollback

Blast radius: the SessionStart hot path. All changes are additive and fail-soft —
an unread/absent source degrades to "startup" (pre-WI-5083 behavior), so a stdin
read failure cannot break startup; the arm is only ever skipped (never newly
blocking) for continuations; Fix (b) only ever relaxes a block. The legitimate
fresh-start await is preserved (armed_source=startup still blocks — test 5.2b).
Rollback: revert the eight target_paths files plus the untracked reader; the only
new persisted field is armed_source in session-lifecycle-guard.json, which older
readers ignore. No data migration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5083-startup-input-gate-rearm-fix`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: — repairs broken behavior (mid-session gate re-arm blocking authorized tools)
without adding a new capability surface. The net-new lines are almost entirely
regression tests for the repaired behavior; per the Conventional Commits type
discipline, a test-heavy defect fix remains `fix:` (not `test:`) because its
purpose is the behavior repair.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
