REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef07d-dbf6-7083-bd4c-3c997d20f111
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-builder automation; approval_policy=never; workspace=E:\GT-KB; resolved_role=prime-builder
author_metadata_source: automation-prompt-live-state

# Defect-Fix Proposal - WI-4283 malformed bridge-status fallthrough

bridge_kind: prime_proposal
Document: gtkb-index-pruning-strands-unimplemented-go-threads
Version: 003
Date: 2026-06-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4283

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py", "platform_tests/scripts/test_versioned_files_archival_invariant.py"]

## Revision Claim

This revision resolves the `-002` NO-GO by narrowing WI-4283 to the live
post-cutover successor-surface defect that actually reproduces: malformed,
heading-first, or legacy bridge files whose latest version has no canonical
first-line status token can still be classified as archived when a terminal
token appears later in the body. Canonical non-terminal first tokens already
preserve the thread, so this revision no longer claims that `GO` plus later
`VERIFIED` prose is archived.

## NO-GO Resolution

The `-002` NO-GO correctly found that current code classifies a file beginning
with canonical `GO` and later mentioning `VERIFIED` as `lost`, not `archived`.
That behavior is already correct and will be locked as a no-regression test.

The remaining defect is narrower and still in scope for WI-4283: when the first
non-blank line is unrecognized text, markdown heading prose, or another
malformed legacy lead-in, `_classify_candidate` can fall through to a scan of
all lines and infer archival from a later terminal token. That silently removes
a non-canonical live thread from bridge state instead of surfacing it for
reconciliation.

This revision also removes the incorrect `DRAFT; non-dispatchable` body status
wording from the live proposal chain.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`
- `platform_tests/scripts/test_versioned_files_archival_invariant.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge lifecycle authority must come from
  the canonical status-bearing versioned file chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - malformed or ambiguous artifacts
  should stay visible for reconciliation rather than disappear from working
  surfaces through inference.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - bridge-state derivation must be
  artifact-backed and deterministic, not prose-inferred.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - archival is a terminal lifecycle
  trigger and must not fire from incidental terminal words in malformed body
  prose.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  cites the governing rules that authorize and constrain the implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps each
  cited behavior to an executable test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, work item, and target paths are declared above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the fix is confined to in-root
  GT-KB platform code and platform tests.
- `GOV-STANDING-BACKLOG-001` - WI-4283 is an open reliability backlog item under
  `PROJECT-GTKB-RELIABILITY-FIXES`.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` and the
file-bridge body status-token rule already establish that the first non-blank
canonical status token is the authority for a bridge file. This fix enforces
that existing contract at the archival boundary. No new or revised GOV, SPEC,
ADR, DCL, PB, or deliberation mutation is required.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`, update
   `_classify_candidate(latest_file_text)` so archival is decided only from the
   first non-blank line:
   - canonical terminal first token -> `"archived"`;
   - canonical non-terminal first token -> `"lost"`;
   - malformed, heading-first, or unrecognized first non-blank line -> `"lost"`
     as a fail-safe deviation surface;
   - remove the scan-all-lines terminal-token fallthrough.
2. Preserve `candidate_is_archived(...)` behavior for explicit
   owner-acknowledged archival through
   `config/governance/tafe-acknowledged-archived-bridges.toml`.
3. Add focused regression coverage in
   `platform_tests/scripts/test_versioned_files_archival_invariant.py`.

Historical recovery of earlier stranded GO threads remains out of scope for
this code-defect fix and belongs to the bridge/backlog reconciliation workflow.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_canonical_non_terminal_first_token_not_archived_even_with_terminal_prose` | `GO`, `NO-GO`, `NEW`, or `REVISED` as the first token preserves the thread even if later body prose mentions `VERIFIED`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_heading_first_terminal_prose_not_archived` | A markdown/prose heading followed later by `VERIFIED` is surfaced as `lost`, not archived. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_unrecognized_first_line_terminal_prose_not_archived` | A malformed or legacy first line followed later by a terminal token is surfaced as `lost`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `test_terminal_first_token_archived` | Canonical terminal first tokens remain archived. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_owner_acknowledged_slug_archived` | Explicit owner-acknowledged archival still archives a non-terminal thread. |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_versioned_files_archival_invariant.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py platform_tests/scripts/test_versioned_files_archival_invariant.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py platform_tests/scripts/test_versioned_files_archival_invariant.py
```

## Prior Deliberations

- `DELIB-20263775` - original bridge/INDEX archival trim review context that
  motivated WI-4283.
- `DELIB-20263860` - bridge VERIFIED backlog-retirement terminal-status signal
  precedent.
- `DELIB-2734` / `DELIB-20264014` - deterministic stale-status reconciliation
  precedent for deriving lifecycle state from status-token authority.
- `DELIB-20265239` - malformed bridge status-token quarantine verification;
  related precedent for surfacing malformed bridge artifacts instead of
  silently rewriting or disappearing them.
- `DELIB-20265240` - GO for malformed bridge status-token quarantine; related
  bridge-status handling context.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` /
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` authorizes bounded
  single-concern reliability fixes through the bridge protocol.
- `DELIB-20265457` authorizes the
  `PROJECT-GTKB-RELIABILITY-FIXES` proposal batch, including P1/P2 reliability
  work.

No new owner input is required for this revision.

## Pre-Filing Preflight Subsection

Prime Builder will file this REVISED artifact only through
`.codex/skills/bridge/helpers/revise_bridge.py file`, which runs both candidate
preflights before publishing live bridge state:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-index-pruning-strands-unimplemented-go-threads --content-file <candidate> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-index-pruning-strands-unimplemented-go-threads --content-file <candidate>
```

Expected result: no missing required specs and zero blocking clause gaps.

The filed artifact will be the next numbered bridge file,
`bridge/gtkb-index-pruning-strands-unimplemented-go-threads-003.md`, preserving
the append-only versioned bridge file chain. Prior versions `-001` and `-002`
will not be deleted or rewritten.

## Acceptance Criteria

1. `_classify_candidate` archives only canonical terminal first-line status
   tokens.
2. Canonical non-terminal latest statuses are preserved even when body prose
   mentions terminal words.
3. Malformed, heading-first, or unrecognized first-line files are surfaced as
   `lost` rather than silently archived by later body text.
4. Explicit owner-acknowledged archival remains unchanged.
5. Focused pytest and ruff check/format commands pass.

## Risks / Rollback

- Risk: a legacy file with a malformed first line and later terminal token may
  remain visible. This is the intended fail-safe direction because ambiguous
  bridge state should be reconciled explicitly.
- Risk: owner-acknowledged archived slugs could regress if the implementation
  touches `candidate_is_archived`. Mitigation: keep that path unchanged and add
  a focused regression test.
- Rollback: revert the one function change in `versioned_files.py` and remove
  the additive test file. No migration or state rewrite is involved.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/versioned_files.py`
- `platform_tests/scripts/test_versioned_files_archival_invariant.py`

## Recommended Commit Type

`fix`
