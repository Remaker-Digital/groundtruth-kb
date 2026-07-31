REVISED
::init gtkb lo
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 8e0b4e69-e221-4d23-9bfd-e5d9591e66f2
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# REVISED Implementation Proposal - Extend narrative-artifact-approval-gate autodiscovery to Edit tool calls

bridge_kind: prime_proposal
Document: gtkb-narrative-gate-edit-autodiscovery-fix
Version: 003 (REVISED after NO-GO 002)
Responds to: bridge/gtkb-narrative-gate-edit-autodiscovery-fix-002.md

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5509

target_paths: [".claude/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_fab14_narrative_autodiscovery.py", "platform_tests/hooks/test_narrative_artifact_approval.py", "groundtruth-kb/tests/test_cli_approval_packet.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

The NO-GO at version 002 is accepted in full. The blocking defect was
procedural, not technical: version 002 explicitly confirmed the design is
"sound, fail-closed, no new trust boundary" and both preflights passed clean.
The sole defect was that `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30`'s
own scope (approval-state retirement) does not cover this hook-governance
work, and the actual owner authorization (an AskUserQuestion answer given
during this same session) was described in prose without a durable, citable
record.

This revision does not change the technical design at all (unchanged from
version 001). It corrects the authorization defect per the NO-GO's option (b):
the owner's AskUserQuestion selection is now captured as a dated Deliberation
Archive record (`DELIB-202666772`, `source_type=owner_conversation`,
`outcome=owner_decision`) and cited below as the operative authorization,
alongside the pre-existing project membership.

## Requirement Sufficiency

Existing requirements are sufficient given `DELIB-202666772`. No new or
revised requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-APPROVAL-001`

## Prior Deliberations

- `DELIB-202666772` - **the operative owner authorization for this exact work
  item**, captured post-NO-GO per the reviewer's option (b): owner AUQ
  "Fix the hook itself first" (2026-07-18, during WI-5492 implementation).
- `DELIB-1575` (VERIFIED) - the narrative-artifact-approval-extension
  Cumulative Round 2 verification; this is the foundation subsystem this
  proposal extends. Confirms the base hook this revision modifies is itself a
  settled, verified surface.
- `DELIB-1577` (NO-GO) - an earlier cumulative-verification round of the same
  extension, prior to `DELIB-1575`'s eventual VERIFIED. Historical iteration
  of the same subsystem, not a standing objection to Edit-autodiscovery
  specifically.
- `DELIB-2408` / `DELIB-20261601` (both NO-GO, same bridge thread
  `bridge/gtkb-generate-approval-packet-cli-008.md`, REVISED-3) - earlier
  construction iterations of the `generate-approval-packet` CLI itself
  (WI-3279), before it reached its current working state (confirmed
  functional and in active use this session for multiple successful DCL/
  deliberation packet insertions). MemBase summary fields for all four are
  terse (`NO-GO`/`VERIFIED` only); the underlying bridge threads were not
  independently re-read in full for this revision, so no specific carried-
  forward objection is claimed beyond what the terse outcome records show.
- No prior deliberation was found (via `search_deliberations` for
  "narrative-artifact-approval-gate Edit", "WI-5509", "Edit autodiscovery
  narrative") that directly authorizes or rejects the specific
  Edit-autodiscovery-reconstruction design in this proposal.

## Owner Decisions / Input

- `DELIB-202666772` - owner AUQ decision, captured 2026-07-18, dated and
  citable: "Fix the hook itself first" selected over an owner-directed
  one-time exception or deferring the blocked files. Explicitly authorizes
  the bounded scope in this proposal (hook Edit-reconstruction +
  `--content-file` for `--kind narrative`) and explicitly excludes the
  broader WI-5441 registry-unification initiative.
- `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30` -
  active project authorization; WI-5509 is a member of
  `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE` (linked via `gt projects add-item`
  after version 001 was filed). Per the NO-GO's own analysis, this PAUTH's
  scope_summary is narrower than WI-5509's subject matter; **this proposal
  does not rely on this PAUTH alone** for authorization - `DELIB-202666772`
  is the operative, on-point authorization. The PAUTH/membership is retained
  only as supplementary project-tracking context.

## Proposed Scope

Unchanged from version 001:

1. Hook fix (byte-identical in both `.claude/hooks/` and the Codex template
   per `test_a_codex_template_parity_exists_and_matches`): add
   `_reconstruct_edit_content(file_path, tool_input)` that reads current
   on-disk content and applies the same `old_string`->`new_string`
   substitution Edit itself performs (single occurrence, or all occurrences
   when `replace_all`); returns `None` (fail-closed, current behavior
   preserved) on missing/non-string `old_string`/`new_string`, zero
   occurrences, or ambiguous multi-occurrence without `replace_all`.
   `main()` calls it for `tool_name==Edit` in place of the current hardcoded
   `None`; Write's path is completely unchanged.
2. CLI fix: `build_narrative_packet()` gains an optional
   `content_source: Path | None` param; when given, `full_content` is read
   from `content_source` instead of `target_path`, while `target_path` (the
   packet field the hook matches against `rel_path`) still derives from the
   `target_path` argument. `_build_narrative_packet()` in
   `cli_approval_packet.py` threads `request.content_file` into this new
   param when present (validated in-root + exists, mirroring the existing
   formal-kind check); when absent, behavior is 100% unchanged.
   `--content-file`'s `cli.py` help text updated to reflect the new optional
   narrative use.
3. New tests: unit tests for `_reconstruct_edit_content` in
   `test_fab14_narrative_autodiscovery.py`; end-to-end Edit-tool_name payload
   tests in `test_narrative_artifact_approval.py`; a `--content-file`
   override test in `test_cli_approval_packet.py`.

## Scope-Isolation Disclosure (new in this revision, per NO-GO Secondary Finding)

`groundtruth-kb/src/groundtruth_kb/cli.py` carries pre-existing, unrelated
uncommitted changes (a `gt projects dependencies add/show/list` CLI group;
`git diff --stat` shows 267 insertions across hunks at lines ~90, ~5437-5438,
and ~5763-6032). This proposal's only change to `cli.py` is the
`--content-file` help-text string at line 3901 (the `generate-approval-packet`
command registration) - confirmed via `git diff` to be topologically distant
from all three pre-existing hunks, with no line-range overlap. The
implementation report will demonstrate this isolation via a scoped diff of
just the touched line; the pre-existing dependency-CLI hunk is left untouched
and must not be swept into this thread's eventual finalization commit.

## Cross-Harness Disposition

- **codex**: parity - byte-identical template update at
  `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py` per
  `test_a_codex_template_parity_exists_and_matches`; forward-compatible only,
  not a live Windows interception boundary per
  `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, unchanged by this fix.

## Out Of Scope

- Full removal of `advisory_backlog_router.py`'s dropbox-scanning code
  (unchanged from version 001 - unrelated to this hook fix).
- The broader `WI-5441` protected-artifact registry unification (explicitly
  excluded by `DELIB-202666772`).
- Any resolution of the pre-existing `cli.py` dependency-CLI hunk (a separate,
  unrelated, already in-progress change this proposal does not touch).

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `python -m pytest platform_tests/hooks/test_narrative_artifact_approval.py platform_tests/scripts/test_fab14_narrative_autodiscovery.py -q` |
| `GOV-ARTIFACT-APPROVAL-001` | `python -m pytest groundtruth-kb/tests/test_cli_approval_packet.py -q` |
| Scope isolation (`cli.py`) | `git diff -- groundtruth-kb/src/groundtruth_kb/cli.py` scoped to only the `--content-file` help-text line; no other hunk touched |

## Acceptance Criteria

- Existing `test_autodiscover_none_for_contentless_edit` and all other current
  tests in both files pass unchanged.
- A new Edit-tool_name payload with a matching on-disk packet (content
  computed via `--content-file`-override packet generation) allows; a
  mismatched or ambiguous Edit still blocks with the existing error message.
- Codex template remains byte-identical to the Claude hook.
- `generate-approval-packet --kind narrative` with no `--content-file` behaves
  exactly as before (regression-covered by the existing CRLF test).
- The `cli.py` diff is scoped to only the `--content-file` help-text change;
  the pre-existing dependency-CLI hunk is untouched.

## Risk And Rollback

Unchanged from version 001: low risk, pure additive/backward-compatible
extension; both changes are narrowing-safe (Write behavior untouched; narrative
`--content-file` is optional and defaults to current behavior when absent).
Rollback is `git revert` of the single implementation commit.

## Recommended Commit Type

`fix` (closes a real session-native authoring gap; not a new capability
surface for end users, but a defect in the approval-packet mechanism itself).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
