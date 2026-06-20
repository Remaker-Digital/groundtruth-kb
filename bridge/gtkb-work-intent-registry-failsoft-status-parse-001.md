NEW

# gtkb-work-intent-registry-failsoft-status-parse — Tolerate token-then-prose status lines and fail-soft on unparseable bridge files (WI-4658)

bridge_kind: implementation_proposal
Document: gtkb-work-intent-registry-failsoft-status-parse
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-18 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: claude-interactive-20260618-work-intent-failsoft
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: claude-code-interactive

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4658

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`scripts/bridge_work_intent_registry.py::_bridge_file_status` (line 177) parses a
bridge file's first non-blank line with `BRIDGE_FILE_STATUS_RE.fullmatch(line)`,
where the regex is anchored end-to-end
(`^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED)$`).
A first line such as `GO test` — a canonical token followed by trailing prose,
which the body-status-token rule in `.claude/rules/file-bridge-protocol.md`
explicitly permits ("token first, then prose") — therefore raises
`WorkIntentRegistryError`. Worse, `_thread_version_entries` (line 192) calls
`_bridge_file_status` for **every** version of a thread and re-raises on the
first failure, so one malformed legacy artifact aborts the entire thread's
work-intent acquire.

Observed live on 2026-06-18: `bridge/gtkb-wi4232-bridge-index-drift-pb-classification-002.md`
contains only the line `GO test`. As a result, every `prime-builder:A`
dispatch attempt selecting that GO-actionable thread fails with
`work_intent_acquire_failed` / `WorkIntentRegistryError: Bridge file has
unrecognized status line: ... 'GO test'` on each reconcile cycle (evidence:
`.gtkb-state/bridge-poller/dispatch-failures.jsonl`). This head-of-line-blocks
the Prime dispatch lane and contributed to the stalled Loyal Opposition
verification routing for `gtkb-bridge-dispatcher-canonical-verdict-repair-005`.

The registry parser is the outlier. The canonical reader
`groundtruth_kb.bridge.versioned_files._line_status_token` strips leading
markers (`#`, `>`, `*`, `-`, backticks, whitespace) and uses `.match()`
(leading-token, prose-tolerant), which is why `collect_bridge_status` parses
`# GO: …` and `GO test` correctly while the registry throws.

This proposal implements WI-4658: (1) align `_bridge_file_status` with the
canonical leading-token, marker-tolerant semantics so `GO test` parses as `GO`;
and (2) make `_thread_version_entries` skip a genuinely-unparseable version with
a structured warning rather than raising, so a single malformed artifact can
never head-of-line-block the dispatch lane. The fix is scoped to the registry
module plus its test file; the body-status-token PreToolUse gate already
prevents new malformed files, so this hardening is for grandfathered/legacy
artifacts and robustness.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered `bridge/<slug>-NNN.md` files are the
  authoritative workflow surface and their first-line status tokens drive
  work-intent and dispatch state; the parser that reads those tokens must honor
  the canonical token grammar.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch health and liveness must
  reflect canonical bridge progress; one malformed artifact must not
  head-of-line-block a recipient lane (the WI-4658 quarantine requirement).
- `GOV-RELIABILITY-FAST-LANE-001` — small, reversible defect fix (single source
  module + its test file); qualifies for the reliability fast lane.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  every governing specification it is constrained by.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project / work-item /
  authorization triple is declared in the metadata block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  derives tests from the linked specifications.
- `GOV-STANDING-BACKLOG-001` — implements the already-tracked standing-backlog
  item WI-4658 (no duplicate work item created; backlog checked pre-filing).

Advisory (artifact-oriented governance triad, applicable to bridge proposals):

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — this work is captured as a durable
  bridge artifact implementing a tracked work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — proposal → review → implement →
  verify lifecycle preserved as artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching the registry source brings the
  spec-to-test mapping under change control via the verification plan.

## Prior Deliberations

- `DELIB-20261120` — "Loyal Opposition Report: Bridge Dispatch Deadlock &
  Contention Critique" (2026-06-09). Directly relevant: it critiques bridge
  dispatch deadlock/contention. This proposal removes one concrete deadlock
  source (fatal parse on a malformed status token that loops every cycle),
  consistent with that report's reliability direction.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — S382 owner decision that
  established the body-status-token rule ("token first, then prose") via
  GTKB-GOV-PROPOSAL-STANDARDS Slice 1. This proposal aligns the registry parser
  with that already-decided grammar rather than introducing a new convention.
- No prior deliberation rejected fail-soft parsing for the work-intent registry;
  WI-4658 is a tracked, un-superseded backlog item.

## Owner Decisions / Input

This reliability work was directed by the owner this session via AskUserQuestion
(detected_via `ask_user_question`): the owner selected **"Fix work-intent
registry (fail-soft)"** in response to the bridge-reconciliation finding that a
malformed `GO test` bridge file was poisoning Prime-A dispatch. Implementation
authority for the code change derives from the Loyal Opposition `GO` on this
proposal plus the implementation-start packet, scoped by
`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-001`,
which covers WI-4658. No further owner decision is required to implement after
`GO`.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement already exists: the
body-status-token rule in `.claude/rules/file-bridge-protocol.md`
(source `DELIB-S382` / GTKB-GOV-PROPOSAL-STANDARDS Slice 1) mandates "a canonical
status token on the first non-blank line … Headings and prose follow the token."
`GOV-FILE-BRIDGE-AUTHORITY-001` makes those tokens authoritative. The registry
parser currently contradicts that requirement by demanding an exact full-line
match; this proposal brings the implementation into conformance with the
existing requirement. No new or revised requirement is needed.

## Spec-Derived Verification Plan

New/updated tests in `platform_tests/scripts/test_bridge_work_intent_registry.py`:

| Linked spec | Test | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, body-status-token rule (`DELIB-S382`) | `test_status_parse_token_then_prose` — first lines `GO test`, `# GO: F1 …`, `> NO-GO blah` | parse to `GO`, `GO`, `NO-GO` respectively |
| body-status-token rule (regression) | `test_status_parse_bare_token_regression` — bare `NEW`/`GO`/`VERIFIED` lines | still parse unchanged |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (WI-4658 quarantine) | `test_unparseable_version_skipped_warns` — a thread with one version whose first line has no canonical leading token | that version is skipped with a structured warning; latest status derived from remaining parseable versions; no exception raised |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` (no head-of-line block) | `test_acquire_succeeds_with_token_then_prose_version` — `acquire()` against a thread whose latest version first line is `GO test` | succeeds (no `WorkIntentRegistryError`) |

Verification commands (repo venv interpreter for reproducible evidence):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
```

## Risk / Rollback

Risk is low and bounded. The change only (a) broadens acceptance to the
already-sanctioned token-then-prose form, and (b) converts a fatal raise into a
skip-with-warning. Well-formed bare-token files are unaffected
(regression-tested). The one residual risk — fail-soft skipping could mask a
genuinely corrupt *latest* version — is mitigated by emitting a structured
warning on every skip and by the existing body-status-token PreToolUse gate that
blocks new malformed files at write time. Rollback is a single-commit revert of
`scripts/bridge_work_intent_registry.py` and
`platform_tests/scripts/test_bridge_work_intent_registry.py`.

Out of scope (captured as follow-on, not implemented here): consolidating the
~9 divergent `BRIDGE_FILE_STATUS_RE` copies across the codebase into one
canonical parser. This proposal aligns only the work-intent registry; broader
consolidation is a separate backlog candidate.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-work-intent-registry-failsoft-status-parse`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs broken dispatch behavior (fatal parse on a sanctioned status-line
form; head-of-line block from one malformed artifact). No new capability surface;
adds regression/robustness tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
