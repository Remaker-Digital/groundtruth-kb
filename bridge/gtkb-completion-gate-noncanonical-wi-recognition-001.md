NEW

# project-VERIFIED-completion gate cannot recognize membership work items whose VERIFIED thread lacks a regex-parseable `Work Item:` line (WI-4737)

bridge_kind: prime_proposal
Document: gtkb-completion-gate-noncanonical-wi-recognition
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-22 UTC

author_identity: Prime Builder (Claude)
author_harness_id: B
author_session_context_id: 47e792ef-a7b6-4cd7-a41b-2496a7670e7a
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: interactive Prime Builder session (gtkb_infrastructure work subject)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4737

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_verified_completion_scanner.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The project-VERIFIED-completion detection subsystem recognizes a membership work
item as "verified for project P" only when a bridge thread implements-linked to P
carries a `Work Item:` metadata line that `_WORK_ITEM_LINE_RE` parses. That regex
deliberately matches only the canonical id forms the platform generates
(`WI-\d+`, `WI-AUTO-[A-Z0-9-]+`, `GTKB-[A-Z0-9-]+`, `WORKLIST-[A-Z0-9-]+`), per the
sibling fix WI-3335. Two real conditions defeat that single recognition path even
for genuinely-VERIFIED work:

1. **Non-canonical work-item ids.** Thirteen current work items carry ids the
   regex cannot match (e.g. `WI-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001`,
   `WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1`). The platform itself reports these as
   "Malformed work item id," so widening the regex to accept them is the wrong fix —
   it would undermine the deliberate narrow-canonical design WI-3335 established.
2. **Threads authored before their work item existed.** A thread whose `-001`
   predates the creation of its work item may never carry a canonical
   `Work Item: <id>` line. `gtkb-project-scoped-implementation-authorization` is
   exactly this case: its only `Work Item:` line is prose
   ("…new MemBase work item to be created…") and no later version backfilled the id.

Consequently `ProjectLifecycleService.complete_project_authorization()` and the
read-only completion scanner both fail-closed ("not completion-ready") for an
authorization whose only outstanding membership work item is one of these — even
when that work item's bridge thread is VERIFIED and implements-linked to the
project. This blocks the governed automatic VERIFIED-completion/retirement path
(`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`) and forces the owner-directed
`retire` override (observed 2026-06-22 retiring
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001-PROJECT-LIFECYCLE`).

This proposal adds a **second, additive, id-agnostic recognition path** that
preserves the narrow regex: a membership work item counts as verified-for-project
P when **(a)** P holds an active `relationship='implements'` link to a thread that
is **(b)** VERIFIED-topped, and **(c)** that thread slug appears in the work item's
own `related_bridge_threads` field. This is a two-sided safeguard — both the
project (implements-link) and the work item (`related_bridge_threads`) must
reference the same VERIFIED thread — mirroring the existing design's two-sided
requirement (project implements-link + thread `Work Item:` line) without the
id-format dependency. The existing regex path is unchanged and remains the primary
recognizer; the new path only adds recognitions, never removes them.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — the governing specification the
  completion subsystem implements. It requires completion detection to recognize
  work items whose bridge threads reached VERIFIED. The current implementation does
  not fully satisfy that requirement for work items lacking a regex-parseable
  `Work Item:` line; this fix corrects the implementation to match the existing
  requirement. No requirement text changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file-bridge authority model; this proposal
  follows the bridge protocol and dispatcher/TAFE state plus the numbered file
  chain remain the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the cross-cutting
  constraint that a proposal cite every relevant governing specification; this
  section is the compliance with it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the project-linkage
  metadata block (Project Authorization / Project / Work Item) above satisfies this.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Spec-Derived Verification
  Plan below maps the governing specification to named regression tests.
- `GOV-RELIABILITY-FAST-LANE-001` — WI-4737 is a defect-origin fix touching two
  source files and two test files, creating no specification; it meets the
  reliability fast-lane criteria and is filed through the standing reliability
  authorization.
- `GOV-STANDING-BACKLOG-001` — WI-4737 is tracked in the MemBase standing backlog as
  an active member of PROJECT-GTKB-RELIABILITY-FIXES (and of the umbrella
  GTKB-DETERMINISTIC-SERVICES-001 where it surfaced).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four target paths are in-root
  under `E:\GT-KB`; none is an application file under `applications/`.

## Prior Deliberations

- Bridge thread `gtkb-project-completion-scanner-wi-auto-regex-fix` (WI-3335,
  VERIFIED at -008; `DELIB-20260611`, GO `DELIB-20264651`) — the sibling fix that
  added `WI-AUTO-*` to `_WORK_ITEM_LINE_RE`. It established two facts this proposal
  builds on: (1) the regex deliberately matches **only** the canonical id forms the
  platform generates, so accepting arbitrary `WI-*` ids would reverse that decision;
  and (2) the completion regex is mirrored byte-identically across
  `lifecycle.py` and `scripts/project_verified_completion_scanner.py`. This proposal
  does **not** touch the regex; it adds an orthogonal `related_bridge_threads`
  recognition path, so the narrow-canonical design is preserved.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5 (owner approval
  `DELIB-20265228`, 2026-06-18) — the v5 keep-open caller election decoupled
  authorization completion from forced retirement but preserved automatic
  completion-when-VERIFIED as the default. This proposal restores that default's
  reach to work items the regex path cannot see; it changes no v5 semantics.
- A Deliberation Archive search for the project-completion `related_bridge_threads`
  recognition path found no prior deliberation proposing it; WI-4737 is its first
  record. (The `gtkb-project-verified-completion-auq-trigger` AUQ-trigger variant
  was NO-GO'd / not adopted and is unrelated to this recognition-path fix.)

## Owner Decisions / Input

No fresh owner approval is required for this specific fix. WI-4737 is a
defect-origin reliability fix filed through the reliability fast-lane: it is an
active member of PROJECT-GTKB-RELIABILITY-FIXES, covered by the standing
authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status active, no
expiry; allowed mutation classes `source`, `test_addition`, `hook_upgrade`; empty
`included_work_item_ids`, so coverage is by project membership). It creates no
specification and no formal artifact, so no formal-artifact-approval packet and no
per-fix deliberation are required.

Motivating owner directive (context, not an approval gate): on 2026-06-22 the owner
directed driving `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` to VERIFIED/retired. This
defect surfaced and was captured (WI-4737) while retiring the
`…-PROJECT-LIFECYCLE` sub-project, whose member
`WI-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION-001` the completion gate could not
recognize.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
is unchanged — this proposal corrects the implementation's recognition mechanism so
it satisfies the existing requirement (recognize work items whose bridge threads
reached VERIFIED) for the cases the regex-only path misses. No new or revised
requirement is created. The `related_bridge_threads` field is an existing MemBase
work-item field already populated by the platform; this fix reads it, it does not
introduce a new contract.

## Spec-Derived Verification Plan

| Linked spec | Verification step | Expected result |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | IP-3 test in `test_project_artifacts.py`; IP-4 test in `test_project_verified_completion_scanner.py` | a membership WI with a non-canonical id whose VERIFIED thread carries no parseable `Work Item:` line, but whose `related_bridge_threads` cites an implements-linked VERIFIED thread, is recognized as completion-ready by both the package service and the scanner; the two-sided guard holds (a WI citing a non-implements-linked or non-VERIFIED thread is NOT recognized) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this table is the spec-to-test mapping; each behavior change maps to a named regression test | every behavior change is covered |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | inspect all four target paths | all in-root; no application file |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this NEW entry published to dispatcher/TAFE state + numbered file chain | confirmed at filing time |

Commands at implementation time (executed after Codex GO):

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --no-header` — all new and existing tests pass.
2. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py` and `ruff format --check` on the same set — zero errors.
3. Mirror check: confirm the two completion surfaces apply the same `related_bridge_threads` recognition logic (the deliberate mirror is preserved).

## Risk / Rollback

- Risk: the new path falsely recognizes a WI as verified. Mitigation: the
  two-sided guard requires the project to hold an active `implements` link to the
  thread AND the thread to be VERIFIED-topped AND the WI's own
  `related_bridge_threads` to cite that exact slug. A WI cannot self-certify (the
  project's implements-link is project-author-controlled); a project cannot certify
  an unrelated WI (the WI must cite the slug). This is the same two-sided shape as
  the existing implements-link + `Work Item:`-line guard.
- Risk: the two completion surfaces drift. Mitigation: IP-1 and IP-2 apply the same
  logic and the IP-3/IP-4 tests assert identical behavior on both surfaces.
- Risk: a malformed/empty `related_bridge_threads` value. Mitigation: parse
  defensively (treat unparseable/empty as "no extra recognitions"); the existing
  regex path is unaffected.
- Rollback: the change is purely additive (a new recognition branch + two tests).
  Reverting the branch and removing the tests restores prior behavior exactly in a
  single commit.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge
file for `gtkb-completion-gate-noncanonical-wi-recognition`; no prior version is
deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — corrects a defect in existing platform code (completion-gate recognition
narrower than the VERIFIED work it must detect). Two source files augmented with an
additive recognition branch plus two regression tests; no new capability surface,
no spec promotion.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
