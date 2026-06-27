NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3972336c-f3d6-47b7-bc56-051c146e2f7c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4762 wrap-scan W2 grandfather exemption for bridge_numbered_file_missing_status

Document: gtkb-wi4762-wrap-scan-numbered-file-status-grandfather
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4762
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4762-WRAP-SCAN-GRANDFATHER

target_paths: ["scripts/wrap_scan_consistency.py", "platform_tests/scripts/test_wrap_scan_consistency.py"]

## Summary

The wrap-scan W2 consistency scanner's `check_bridge_numbered_files_have_status`
(`scripts/wrap_scan_consistency.py`, currently lines 58-79) iterates EVERY
numbered bridge file in `bridge/` and emits a `bridge_numbered_file_missing_status`
finding at `SEVERITY_ERROR` (exit 2) for any file whose
`status_from_bridge_file(...)` is None. It has no grandfather exemption.

This over-reports against the body-status-token rule's grandfather clause. The
Body Status-Token Rule (under GOV-FILE-BRIDGE-AUTHORITY-001, in
`.claude/rules/file-bridge-protocol.md`) requires a canonical first-line status
token but explicitly states: "Files that already exist on disk with a
non-canonical first line are grandfathered, so the rule never retroactively
breaks historical bridge files on overwrite. The rule fires only on the Write
tool ... Edit operations are not subject to it." So historical bridge files that
predate the rule (and Edit-created files) are intentionally exempt. The W2
scanner, scanning the whole corpus, flags those historical files as ERROR —
retroactively breaking exactly what the clause grandfathers, and failing the
wrap-scan on legitimate historical content.

The fix adds a grandfather exemption: the check flags only numbered bridge files
that are NOT already part of the committed history (i.e., new this session),
faithfully implementing "files that already exist on disk are grandfathered."

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — the Body Status-Token Rule and its grandfather
  clause are bridge authority; this scanner enforces that rule and must honor its
  grandfather exemption. This proposal is also a bridge artifact under the
  canonical append-only numbered-file chain.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification and derives its tests from them.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4762 is the canonical backlog record for this
  work. Its CLAUSE-VISIBILITY-BULK-OPS does not apply: this is a single scanner
  false-positive fix, not a bulk backlog operation, so it produces no inventory
  artifact or review-packet and needs no bulk-action formal-artifact-approval
  packet.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the grandfather predicate derives from a
  fresh canonical read of the committed state (`git ls-tree HEAD`) at scan time,
  not a cached snapshot.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the exemption is
  enforced by spec-derived tests over an injectable grandfather resolver.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4762 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop (PB picks); basis
  for the covering PAUTH.
- bridge/gtkb-gov-proposal-standards-slice1-025.md — the GO that landed the Body
  Status-Token Rule (including its grandfather clause); this fix makes the W2
  scanner honor that clause.
- WI-4862 (committed 2026-06-27, "scope inventory-drift gate to staged set") — a
  sibling precedent: a corpus-wide governance gate was scoped to avoid
  over-reporting historical content. This proposal applies the same "don't
  retroactively flag historical files" principle to the W2 missing-status check.
- A live DA search ("wrap-scan bridge numbered file missing status grandfather
  clause") returned no prior deliberation on this scanner's grandfather behavior.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001 already defines
the Body Status-Token Rule and its grandfather clause; this WI makes the W2
scanner conform to the existing clause. No new or revised requirement is needed;
no formal spec/governance mutation is in scope.

## Design

Confined to the two authorized files.

1. `scripts/wrap_scan_consistency.py`:
   - Add `_git_head_bridge_files(project_root) -> set[str] | None`: returns the
     set of bridge-file paths present at `HEAD` via
     `git ls-tree -r --name-only HEAD -- bridge` (paths like `bridge/<name>.md`).
     Returns None when git is unavailable or the command fails (not a repo, no
     commits, etc.).
   - `check_bridge_numbered_files_have_status(project_root, *, head_resolver=_git_head_bridge_files)`:
     resolve the at-HEAD set once. A numbered bridge file is **grandfathered**
     (not flagged) when its `bridge/<name>` path is present in the at-HEAD set —
     it "already exists on disk" in committed history, exactly the clause's
     exemption. Only numbered bridge files NOT at HEAD (newly added this session)
     that are missing a status token are flagged. `head_resolver` is injected so
     the predicate is unit-testable without a real git tree.
   - Fallback safety: when the resolver returns None (git unavailable), the check
     fails toward NOT over-reporting — it treats all files as grandfathered and
     emits a single `bridge_status_grandfather_unavailable` INFO finding rather
     than ERROR-flagging the whole corpus. The Write-time bridge-compliance gate
     remains the primary enforcement for new files; the W2 check is a backstop.

2. `platform_tests/scripts/test_wrap_scan_consistency.py`: spec-derived tests
   using an injected `head_resolver` (no real git repo required) plus tmp
   `bridge/` files.

Rejected alternatives (noted for the reviewer):
- Static allowlist of historical missing-status files: goes stale, must be
  hand-maintained, and does not auto-grandfather files discovered later.
- Pure staged-set scoping (WI-4862 style): correct for a commit-time gate, but
  the W2 scanner runs at session wrap where the relevant unit is "new since
  HEAD," which the at-HEAD predicate captures directly (a staged-only scope would
  miss a new-but-unstaged file).

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 (grandfather: a historical at-HEAD numbered bridge file without a status token is NOT flagged) | test_missing_status_historical_at_head_not_flagged | platform_tests/scripts/test_wrap_scan_consistency.py |
| GOV-FILE-BRIDGE-AUTHORITY-001 (a NEW numbered bridge file — not at HEAD — without a status token IS flagged ERROR) | test_missing_status_new_file_flagged | platform_tests/scripts/test_wrap_scan_consistency.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (a NEW numbered bridge file WITH a valid status token is not flagged) | test_valid_status_new_file_not_flagged | platform_tests/scripts/test_wrap_scan_consistency.py |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (resolver unavailable: fail toward not over-reporting, INFO not ERROR) | test_head_resolver_unavailable_grandfathers_all | platform_tests/scripts/test_wrap_scan_consistency.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_wrap_scan_consistency.py -q --tb=short
python -m ruff check scripts/wrap_scan_consistency.py platform_tests/scripts/test_wrap_scan_consistency.py
python -m ruff format --check scripts/wrap_scan_consistency.py platform_tests/scripts/test_wrap_scan_consistency.py
```

## Risk / Rollback

- Risk: the at-HEAD predicate could under-report a same-session create-then-overwrite
  of a bridge file (flagged as new). Mitigation: this is the safe direction (a
  final-state numbered bridge file generally should carry a status token), and
  the case is an edge; the Write-time gate already covers new Writes.
- Risk: git invocation overhead / failure. Mitigation: a single `git ls-tree`
  call per scan, resolved once; failure falls back to grandfather-all (no
  over-report) with an INFO finding, never an ERROR.
- Risk: behavioral change to an existing check. Mitigation: the existing
  `test_wrap_scan_consistency.py` suite must continue to pass, and the new tests
  pin both the grandfathered and the newly-flagged paths.
- Rollback: changes are an added resolver + a guarded predicate in one check
  plus new tests; reverting the two files restores prior behavior. No schema,
  governed-record, or narrative change is involved.

## Bridge Filing Discipline

This proposal is filed as the next numbered bridge file
(`bridge/gtkb-wi4762-wrap-scan-numbered-file-status-grandfather-001.md`) under the
canonical append-only numbered-file chain; revisions and verdicts are added as new
numbered files so the chain remains the canonical audit trail per
GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the whole-backlog
  NEW-implementation-proposal generation loop (PB picks), under which WI-4762 was
  re-homed to the active PROJECT-BACKLOG-TRIAGE-AND-HYGIENE and its covering PAUTH
  (PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4762-WRAP-SCAN-GRANDFATHER; allowed
  mutation classes source + test_addition; linked spec GOV-FILE-BRIDGE-AUTHORITY-001)
  was minted. No further owner decision is required to review this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
