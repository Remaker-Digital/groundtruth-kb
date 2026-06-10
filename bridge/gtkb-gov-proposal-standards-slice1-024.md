REVISED

# GTKB-GOV Proposal Standards — Slice 1 In-Root Reimplementation (REVISED-1: full blast radius)

bridge_kind: prime_proposal
Document: gtkb-gov-proposal-standards-slice1
Version: 024
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-01T14-20-00Z-prime-builder-s382
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto

Project Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4
Project: PROJECT-GTKB-GOV-PROPOSAL-STANDARDS
Work Item: GTKB-GOV-PROPOSAL-STANDARDS

target_paths: ["groundtruth-kb/templates/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py", "platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py", ".claude/rules/file-bridge-protocol.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Revises: `bridge/gtkb-gov-proposal-standards-slice1-022.md` (GO at `-023`).
Reason for revision: implementing the GO'd `-022` design revealed two
blast-radius items the `-022` target_paths did not cover. This REVISED-1
expands target_paths to the full, verified set and documents the complete
change. The body-status-token design itself is unchanged from `-022`.

---

## Why This Revision (Blast Radius Discovered During Implementation)

The `-022` design (add a body-status-token first-line BLOCK to the bridge
compliance gate) was GO'd at `-023` with a 3-file target_paths. Applying it
surfaced two facts that require a wider, owner-visible scope:

1. **The active hook is template-locked byte-for-byte.**
   `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence`
   asserts `.claude/hooks/bridge-compliance-gate.py` is byte-identical to
   `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (per
   gov-process-spec-precondition §2.3 Option A: the GT-KB workspace activates
   the framework template byte-for-byte). Editing only the active hook breaks
   this invariant. The rule must land in the **template** and be re-activated
   byte-for-byte to the active hook. This is also the architecturally correct
   home: the body-status-token rule is a bridge-protocol integrity property
   that every GT-KB adopter should inherit, not a workspace-local policy.

2. **Six existing tests use heading-first proposal fixtures the new rule
   correctly blocks.** In
   `test_bridge_compliance_gate_hard_block_workspace.py`
   (`test_proposal_lacking_spec_links_blocked_with_deny`,
   `test_compliant_proposal_passes`) and
   `test_bridge_compliance_gate_w4_calibration.py`
   (`test_compliance_gate_heading_ambiguity_asks`,
   `test_compliance_gate_absent_section_still_denies`,
   `test_compliance_gate_concrete_links_with_placeholder_word_passes`), the
   fixtures construct versioned-bridge proposal content that begins with a
   markdown heading (`# Implementation Proposal`) rather than a status token.
   These fixtures predate the status-first convention; the new rule blocks
   them before the clause they intend to exercise. The fix is mechanical:
   prepend a canonical status token (`NEW`/`REVISED`) to each affected fixture
   so it reaches the clause under test. (`test_hook_matches_template_or_documented_divergence`
   is resolved by item 1: once the template carries the rule and the active
   hook re-activates it byte-for-byte, the hashes match again.)

Neither file was in the `-022` target_paths, so the implementation-start gate
correctly blocked editing them. This REVISED-1 brings them into scope.

## Design (unchanged from `-022`)

The body-status-token rule, helper predicates, grandfather semantics, and deny
message are exactly as approved in `-022` §"Design — Body-Status-Token Rule".
Summary: versioned bridge files (`bridge/<slug>-NNN.md`) must begin with a
canonical status token on the first non-blank line
(`NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`WITHDRAWN`). New files
(and overwrites of files that currently have a canonical first line) must
comply; files already on disk with a non-canonical first line are
grandfathered. The rule fires only on the `Write` tool (the gate populates
`content` only for `Write`; `Edit` supplies empty content and is skipped).

Three additions to the gate (in the template, mirrored byte-for-byte to the
active hook):

- `_first_line_is_recognized_status(first_line)` — mirrors the gate's existing
  recognition union (`ADVISORY`, `WITHDRAWN`, `PENDING_PREFLIGHT_STATUSES`,
  and `.startswith(("GO","NO-GO","VERIFIED"))`), erring toward acceptance so
  the rule never false-blocks.
- `_ondisk_first_nonblank_line(file_path)` — reads the current on-disk first
  non-blank line for grandfathering; fail-soft on OSError.
- `_body_status_token_violation(file_path, content)` — returns True only for a
  versioned bridge file whose new first line is non-canonical and which is not
  grandfathered.
- One early deny branch at the top of the bridge-markdown block in
  `_deny_reason_for_content`.

Per the Codex `-023` non-blocking note, the implementation makes `WITHDRAWN`
acceptance explicit in both the gate predicate and the rule documentation.

## Files Changed (6)

| File | Change | In `-022`? |
|---|---|---|
| `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` | Add the 3 helpers + deny branch (canonical source) | NEW in `-024` |
| `.claude/hooks/bridge-compliance-gate.py` | Re-activate template byte-for-byte (same edit) | yes |
| `platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py` | New 12-test regression suite | yes |
| `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` | Prepend status tokens to 2 heading-first fixtures | NEW in `-024` |
| `platform_tests/hooks/test_bridge_compliance_gate_w4_calibration.py` | Prepend status tokens to 3 heading-first fixtures | NEW in `-024` |
| `.claude/rules/file-bridge-protocol.md` | New "## Body Status-Token Rule" subsection (narrative-artifact packet) | yes |

## Specification Links

Unchanged from `-022`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified).
- `GOV-STANDING-BACKLOG-001` v5 (verified).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (in-root clause; all 6 paths in-root).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory; carried forward per the
  `-023` non-blocking note).

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` (v1) — owner S382 decision
  authorizing the body-status-token implementation.
- `bridge/gtkb-gov-proposal-standards-slice1-023.md` — Codex GO on `-022`,
  including the non-blocking note that `WITHDRAWN` acceptance be made explicit
  (incorporated here).
- `DELIB-1132` / `DELIB-2024` — archived `gtkb-gov-proposal-standards-slice1`
  thread harvest stubs.
- S317 reconciliation commit `9b5c535b` — phantom-VERIFIED `-024` INDEX
  annotation (the prior phantom history this thread reconciles).

## Owner Decisions / Input

Authorized by the S382 AUQ decision captured in
`DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` ("Implement the one real
gap"), under `PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4` (active;
allowed mutation classes `hook_upgrade`, `test_addition`,
`governance_doc_update`). The blast-radius expansion (template sync + fixture
updates) is mechanical implementation of the same owner-approved rule, not a
new owner decision: the rule's scope is unchanged; only the set of files that
must change to land it cleanly grew. No new owner AUQ is required.

The `.claude/rules/file-bridge-protocol.md` edit requires a per-artifact
narrative-artifact-approval packet at implementation time (per the `-023` GO
condition 2); this proposal's review does not waive it.

## Requirement Sufficiency

**Existing requirements sufficient.** Same as `-022`: the body-status-token
rule is a concrete enforcement of `GOV-FILE-BRIDGE-AUTHORITY-001` and the
proposal-standards DCL family; no new or revised specification is required.

## Spec-Derived Verification Plan

`## Spec-Derived Verification Plan` — the 12-test regression suite
`platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py`
(already authored; passes 12/12 under uv) covers: heading-first new file
blocked; each canonical token accepted; verdict tokens with trailing content
accepted; existing non-canonical file grandfathered; canonical→non-canonical
overwrite blocked; non-versioned bridge markdown skipped; INDEX.md skipped;
WITHDRAWN accepted; integrated deny path; Edit empty-content skipped.

Post-implementation evidence will include:

- The full `bridge_compliance` test family GREEN (the 6 currently-failing
  tests pass after their fixtures are status-token-prepended), run with
  `uv run --with pytest --with pytest-timeout python -m pytest platform_tests/hooks/ -k "bridge_compliance or bridge_author" -q`.
- `test_hook_matches_template_or_documented_divergence` GREEN (active hook
  byte-matches the updated template).
- The new suite GREEN.
- `ruff check` and `ruff format --check` on all changed Python files (bare
  `uv run --with ruff ...`, no `$env:` prefix).

## Bridge Filing (INDEX-Canonical)

This REVISED-1 is filed under `bridge/` with a `REVISED` entry inserted at the
top of the `gtkb-gov-proposal-standards-slice1` version list in
`bridge/INDEX.md`; no prior version (`-022`, `-023`) is deleted or rewritten
(append-only audit trail). `bridge/INDEX.md` remains the canonical workflow
state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Implementation Sequence (post-GO)

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-gov-proposal-standards-slice1` (fresh packet from the `-024` GO; covers all 6 target paths).
2. Add the 3 helpers + deny branch to
   `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`.
3. Copy the template to `.claude/hooks/bridge-compliance-gate.py` byte-for-byte
   (re-activation); confirm sha256 equality.
4. Prepend canonical status tokens to the 5 heading-first fixtures in the 2
   existing test files.
5. Generate the narrative-artifact packet and add the "## Body Status-Token
   Rule" subsection to `.claude/rules/file-bridge-protocol.md`.
6. Run the full `bridge_compliance`/`bridge_author` family + the new suite +
   ruff; confirm green and byte-match.
7. File the post-implementation report.

## Recommended Commit Type

`feat:` — new bridge compliance-gate enforcement capability (body-status-token
BLOCK) with template sync, regression tests, fixture updates, and rule
documentation.

## Risk / Rollback

The gate change is additive (helpers + one early deny branch); the fixture
edits are mechanical status-token prepends; the rule-doc edit is a new
subsection. Single-commit revert restores prior behavior across all 6 files.
The grandfather branch + Write-only firing + append-only bridge discipline mean
the 1038 historical non-canonical bridge files (22% of 4725) are never
re-Written and so never blocked.

## Decision Needed From Owner

None beyond the captured S382 AUQ. The narrative packet is collected
mechanically at implementation time.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
