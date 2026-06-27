NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4864 deterministic `gt bridge wait` completion-notification CLI

Document: gtkb-wi4864-bridge-wait-completion-notification-cli
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4864
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4864-BRIDGE-WAIT-CLI

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_wait.py"]

## Summary

The dispatcher-daemon Claude+Cursor headless-collaboration goal needs the
interactive session that files a NEW implementation proposal to be able to wait
for its thread to reach completion (VERIFIED, which by protocol implies the
finalize-commit landed) and report — "no further interaction until complete and
committed". Verified live this session: there is NO such surface. `gt bridge`
exposes `show`, `threads`, and the dispatch subcommands, but no `wait`/`watch`.
An interactive session can only poll `gt bridge show <slug>` by hand and re-derive
the terminal/commit check each time.

This proposal adds a deterministic, read-only `gt bridge wait <slug>` CLI: it
polls the canonical bridge thread state until the thread reaches terminal VERIFIED
(success) or a non-success terminal (WITHDRAWN / DEFERRED), or until a timeout,
and — for the VERIFIED case — confirms the latest verdict file is committed in
git, emitting machine-readable JSON. The interactive harness drives it on a
ScheduleWakeup/loop cadence and reports when it returns terminal. This aligns with
the Deterministic Services Principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`):
the repetitive poll + terminal/commit check becomes a service, not per-session
plumbing.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — the bridge thread state and the VERIFIED
  commit-finalization gate are bridge authority; this read-only surface consumes
  the canonical numbered-file thread state and the finalize-commit semantics. This
  proposal is also a bridge artifact under the canonical append-only numbered-file
  chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4864 is the canonical backlog record for this
  work. Its CLAUSE-VISIBILITY-BULK-OPS does not apply: this is a single new
  read-only CLI surface, not a bulk backlog operation, so it produces no inventory
  artifact or review-packet and needs no bulk-action formal-artifact-approval
  packet.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the wait/terminal/
  commit semantics are enforced by spec-derived unit tests over the pure
  evaluate/wait functions plus a CLI test.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the CLI derives terminal state from a fresh
  canonical read each poll (`show_thread`), not a cached snapshot.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4864 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626 (owner_conversation /
  owner_decision) — the parent goal decision; the completion-notification surface
  is the goal's "no further interaction until complete and committed" UX.
- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop (PB picks); basis
  for the covering PAUTH.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive plumbing belongs in a
  deterministic service; the per-session poll + terminal/commit check is exactly
  that.
- No prior deliberation rejects a bridge wait/notification surface; a live DA
  search ("interactive session wait bridge thread verified completion
  notification") returned only unrelated historical bridge reports.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already establishes
the bridge thread state and the VERIFIED finalize-commit semantics; this WI adds a
read-only wait surface over them. No new or revised requirement is needed; no
formal spec/governance mutation is in scope.

## Design

A new pure-core module plus a thin CLI, confined to the three authorized files.

1. `groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py` (new):
   - `TERMINAL_SUCCESS = frozenset({"VERIFIED"})`; `TERMINAL_STOP =
     frozenset({"WITHDRAWN", "DEFERRED"})` (a thread parked/withdrawn will not
     auto-complete, so the wait stops and reports rather than hanging).
   - `evaluate_thread_state(payload, *, success=..., stop=...) -> dict` (pure):
     given a `read_commands.show_thread` payload (or None), classify outcome as
     `verified` / `stopped` / `pending` / `absent` with `latest_status`,
     `latest_version`, `latest_path`, and a `terminal` flag.
   - `verdict_committed(project_root, latest_path, *, git_runner=...) -> bool`:
     confirm the latest VERIFIED verdict file is tracked AND committed in git
     (`git ls-files --error-unmatch` + `git log -1`); `git_runner` is injectable.
   - `wait_for_thread(project_root, slug, *, until="verified", timeout_seconds,
     poll_interval_seconds, require_commit=True, reader=show_thread,
     now=time.monotonic, sleep=time.sleep, commit_checker=verdict_committed)
     -> dict`: poll loop returning a structured result
     (`outcome`, `latest_status`, `latest_version`, `committed`, `elapsed_seconds`,
     `polls`). `now`/`sleep`/`reader`/`commit_checker` are injected so the loop is
     fully unit-testable without real sleeping, live dispatch, or a real git tree.

2. `groundtruth-kb/src/groundtruth_kb/cli.py`: a `@bridge.command("wait")` thin
   wrapper — `gt bridge wait <slug> [--until verified] [--timeout 3600]
   [--poll 30] [--require-commit/--no-require-commit] [--json]` — calls
   `wait_for_thread` and maps the outcome to an exit code (0 on success terminal;
   non-zero on stopped/timeout) so the interactive harness can branch.

3. `platform_tests/scripts/test_bridge_wait.py` (new): spec-derived unit + CLI
   tests (no live dispatch; injected clock/sleep/reader/commit-checker; CLI test
   writes a real VERIFIED bridge file into a tmp project and invokes the command
   so it returns on the first poll).

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (already-VERIFIED + committed thread returns reached on the first poll, no sleep) | test_wait_returns_reached_when_already_verified_and_committed | platform_tests/scripts/test_bridge_wait.py |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (polls a fresh read until VERIFIED across multiple reads) | test_wait_polls_until_verified | platform_tests/scripts/test_bridge_wait.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (require-commit holds until the verdict is committed in git) | test_wait_require_commit_holds_until_committed | platform_tests/scripts/test_bridge_wait.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (timeout returns a non-success outcome and non-zero exit when never terminal) | test_wait_times_out_when_never_terminal | platform_tests/scripts/test_bridge_wait.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (a WITHDRAWN/DEFERRED thread stops and reports rather than hanging) | test_wait_stops_on_withdrawn_or_deferred | platform_tests/scripts/test_bridge_wait.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (CLI: gt bridge wait on an already-VERIFIED thread emits JSON + exit 0) | test_bridge_wait_cli_already_verified_json | platform_tests/scripts/test_bridge_wait.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_bridge_wait.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_wait.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/wait_commands.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_wait.py
```

## Risk / Rollback

- Risk: a poll loop could hang if no terminal/timeout is reached. Mitigation: the
  timeout is mandatory (default 3600s) and a dedicated test pins the timeout path;
  WITHDRAWN/DEFERRED are stop terminals so a parked thread does not hang.
- Risk: the commit confirmation could false-negative on an in-flight finalize.
  Mitigation: `--require-commit` is the precise "committed" signal; it is
  injectable and tested both ways, and `--no-require-commit` degrades to the
  status-only signal (VERIFIED) when the caller prefers it.
- Risk: real sleeping makes tests slow/flaky. Mitigation: `now`/`sleep`/`reader`/
  `commit_checker` are injected; tests use fakes and never sleep.
- Rollback: changes are a new module, a new CLI subcommand, and a new test file;
  reverting them removes the surface with no effect on existing behavior. No
  schema, governed-record, or narrative change is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4864-bridge-wait-completion-notification-cli-001.md`) under the
canonical append-only numbered-file chain; revisions and verdicts are added as new
numbered files so the chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626 — owner AUQ (2026-06-26)
  established the dispatcher-daemon Claude+Cursor headless-collaboration goal and
  its "no further interaction until complete and committed" UX.
- Owner AUQ (2026-06-26, this session) selected "Non-daemon routing readiness" as
  the focus and "Deterministic `gt bridge wait` CLI" as the completion-notification
  mechanism, after confirming live that Cursor LO routing is already correct and
  the wait surface is missing.
- DELIB-20266194 — owner AUQ (2026-06-26) authorized the whole-backlog
  NEW-implementation-proposal generation loop (PB picks), which minted the covering
  PAUTH PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4864-BRIDGE-WAIT-CLI
  (allowed mutation classes source + test_addition; linked spec
  GOV-FILE-BRIDGE-AUTHORITY-001). No further owner decision is required to review
  this proposal; re-enabling dispatch for a live end-to-end test remains a separate
  go-live decision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
