NO-GO
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 2026-07-15T21-38-08Z-loyal-opposition-B-d92527
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code bridge auto-dispatch; resolved role loyal-opposition (harness B)

# Loyal Opposition Verdict - WI-5252 Session Envelope CLI Provenance (NO-GO)

bridge_kind: lo_verdict
Document: gtkb-wi5252-session-envelope-cli-provenance
Version: 002
Date: 2026-07-15 UTC
Responds to: bridge/gtkb-wi5252-session-envelope-cli-provenance-001.md

## Verdict

NO-GO. The defect premise is correct and precisely characterized, spec linkage is
comprehensive, both mandatory preflights pass cleanly, and the governance sections
(Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency, in-root
placement, target_paths) are complete. The single blocking gap is a
scope/feasibility contradiction in Proposed Scope item 1: it directs the
implementer to reuse a canonical init-keyword parser and to not add a second
regex, but no importable canonical parser exists inside the `groundtruth_kb`
package, and the declared `target_paths` exclude every module that actually holds
the canonical vocabulary. As written, the three constraints cannot all be
satisfied. One targeted revision clears it.

## What Is Correct (confirmed against live code, this session)

- Defect confirmed. `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:69`
  calls `open_session(...)` and passes `harness_name`, `harness_id`,
  `init_keyword`, `subject`, `role`, `active_work_item_id` but never
  `worker_role_source`. `groundtruth-kb/src/groundtruth_kb/session/envelope.py:529`
  only builds `worker_role_provenance` when `worker_role_source is not None`, so a
  CLI-opened envelope carries no provenance and the governed writer rejects it.
  This matches Defect / Reproduction steps 2-3.
- Asymmetry confirmed. The dispatcher path
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py:571`
  (`ensure_worker_session`) already passes `worker_role_source=role_source`, so
  dispatched workers get provenance today; the gap is the interactive CLI path
  only, exactly as the proposal frames it.
- Downstream fail-closed is already partly enforced.
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py:33` defines
  `WORKER_ROLES` and the role guard at
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py:308` rejects any role
  outside the closed vocabulary. The proposal's net-new obligation is therefore
  the keyword-to-role agreement gate, not role validation itself.
- Preflights clean (I ran both). Applicability preflight preflight_passed true,
  missing_required_specs empty. ADR/DCL clause preflight 0 blocking gaps, exit 0.

## Blocking Finding - P1: Proposed Scope item 1 is unsatisfiable as written

Observation. Proposed Scope item 1 tells the implementer to reuse the canonical
closed-vocabulary init-keyword parser and to not add a second regex. The declared
`target_paths` are limited to `cli_session_handoff.py`, `session/envelope.py`, and
three test files.

Evidence. There is no init-keyword parser inside the installable `groundtruth_kb`
package. The only `::init gtkb` occurrences in the package are at
`groundtruth-kb/src/groundtruth_kb/session/handoff.py:423` and
`groundtruth-kb/src/groundtruth_kb/session/handoff.py:424`, and both are return
values that emit the string for handoff-prompt generation; neither parses it. The
canonical parser and vocabulary live only under `scripts/`, and are already
duplicated across at least five call sites:

- `scripts/session_self_initialization.py:7622` - the regex parse
  (`re.match` on the canonical `::init gtkb (pb|lo)` grammar).
- `scripts/cloud_harness_base.py:148` and `scripts/cloud_harness_base.py:149` -
  a full-string to role map.
- `scripts/ollama_harness.py:69` and `scripts/ollama_harness.py:70` - the same
  map, duplicated.
- `scripts/session_start_dispatch_core.py:77` and
  `scripts/workstream_focus.py:1192` - `pb` to `prime-builder` token maps.

Deficiency rationale. The installable package must not import from `scripts/`
(that inverts the dependency direction and `scripts` is not in the package
namespace). Within the declared `target_paths`, the implementer faces mutually
exclusive constraints:

1. Import the scripts-side parser - architecture violation; not importable from
   the package.
2. Add a package-local parser in `session/envelope.py` - this is literally adding
   a further copy of the grammar/vocabulary, which Scope item 1 forbids and which
   increases the very drift the closed-vocabulary rule exists to prevent.
3. Extract-and-share the canonical parser into the package and repoint the
   scripts consumers - this edits `scripts/session_self_initialization.py`,
   `scripts/session_start_dispatch_core.py`, `scripts/cloud_harness_base.py`,
   `scripts/ollama_harness.py`, and `scripts/workstream_focus.py`, none of which
   are in `target_paths`, so the target_paths-scoped implementation-start gate
   blocks it.

The proposal also names no import path for the canonical parser, so an
implementer cannot locate the thing they are told to reuse.

Proposed solution (either option resolves the NO-GO):

- Option 1 (recommended - single package source of truth). Revise Scope item 1 to
  authorize creating ONE canonical closed-vocabulary parser inside the package
  (either in `session/envelope.py`, already in `target_paths`, or a small new
  `session/init_keyword.py` added to `target_paths`), using the exact canonical
  grammar and the pb-to-prime-builder / lo-to-loyal-opposition map. Reword
  "do not add a second regex" to "introduce the single package-canonical parser;
  do not duplicate the grammar." File a follow-up work item to migrate the
  existing `scripts/*` duplicates to import that package parser, so the net
  direction is toward one source of truth rather than a sixth copy.
- Option 2 (extract-and-share now). Expand `target_paths` to include the
  `scripts/*` modules that hold the canonical vocabulary, move the parser into the
  package, and repoint all current consumers in this work item.

Option rationale. Option 1 is least-regret: it lands the CLI fix within the
current small `target_paths`, creates a genuine canonical home in the package
(where a reusable parser belongs), and defers the multi-file scripts migration to
a scoped follow-up instead of inflating a focused defect fix. Option 2 is also
correct but couples a focused CLI repair to a five-file cross-cutting migration,
raising review and rollback cost against the proposal's own focused-revert
rollback plan.

## Secondary Finding - P3 (non-blocking; handle during implementation)

`groundtruth-kb/src/groundtruth_kb/session/envelope.py:254` sets the
`role_resolution.interactive_role_source` field to the transcript-init-keyword
value based on `role` alone, independent of `init_keyword`. After the fix, a CLI
open with a `--role` but no matching `--init-keyword` would still stamp that
role-resolution source while (correctly) withholding `worker_role_provenance`,
leaving two fields disagreeing about whether a transcript keyword was actually
validated. Decide deliberately whether to also gate that assignment on
keyword-to-role agreement for internal consistency, and add a test either way.
Not a blocker; flagged so it is handled intentionally rather than silently.

## Prime Builder Implementation Context

- Objective: make `gt session envelope open` create writer-usable
  `worker_role_provenance` when a canonical init keyword and a matching `--role`
  are supplied, and fail closed otherwise.
- Preconditions: choose Option 1 or Option 2 above; if Option 2, expand
  `target_paths` and re-file as REVISED.
- Evidence paths: `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py:69`
  (call site missing `worker_role_source`);
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py:529` (the provenance
  gate); `groundtruth-kb/src/groundtruth_kb/session/envelope.py:571` (reference
  implementation that already passes the source);
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py:254` (secondary finding).
- Verification: keep the proposal's spec-derived plan and ADD a regression
  asserting the CLI does not duplicate the init-keyword grammar (Option 1: assert
  the CLI validation routes through the single package parser; no new
  `::init gtkb` regex literal appears outside the one canonical home).
- Rollback: unchanged - focused revert of the CLI integration and focused tests.
- Open decisions: Option 1 vs Option 2 is a Prime/owner scope call; record it in
  the REVISED proposal.

## Preflight Evidence

- Applicability preflight packet_hash
  sha256:8116a5453ae21ac5b58511cf1cb2824cf7486bdce068378b14ae9b7d5fa8c2a9:
  preflight_passed true; missing_required_specs empty; missing_advisory_specs
  empty; blocking_errors empty.
- ADR/DCL clause preflight: 5 clauses evaluated; must_apply 4; blocking gaps 0;
  exit 0.

Both preflights are clean, so this NO-GO is a substantive design finding, not a
mechanical-gate failure.

## Review Independence

Proposal author session context `A-2026-07-15T21-31-23Z` (harness A, codex).
Reviewer session context `2026-07-15T21-38-08Z-loyal-opposition-B-d92527`
(harness B, claude). Distinct session contexts; review independence satisfied.
