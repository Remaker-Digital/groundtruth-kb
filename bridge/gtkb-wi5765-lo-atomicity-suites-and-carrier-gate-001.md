NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 08ab8a9d-bc19-4278-b81f-a8b3a488700c
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code headless proposal worker under manual dispatch from leader session bb6ca43c (DELIB-202667523/531/533 fan-out); resolved role prime-builder for this dispatched drafting task

bridge_kind: prime_proposal
Document: gtkb-wi5765-lo-atomicity-suites-and-carrier-gate
Version: 001
Date: 2026-07-29 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5765

target_paths: ["platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py", ".claude/hooks/bridge-compliance-gate.py", "config/hooks/gtkb-bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py"]

# WI-5765 — Repair the Red LO Commit-Atomicity Suites and the Bridge-Only-Carrier VERIFIED Evidence Gate

Scope confirmation: this proposal performs no MemBase mutation and no
groundtruth.db write.

This filing performs no approval-evidence work; no protected
narrative-artifact edit is in scope for this work item.

## Problem

Source advisory:
`bridge/gtkb-lo-verified-finalization-toolchain-drift-advisory-001.md`
(ADVISORY, 2026-07-29), routed to WI-5765 by DELIB-202667534 row 14 with the
advisory's own sequencing preserved: A1 and A7 first, both P1. Every fact
below was re-verified fresh this session (2026-07-30 UTC) per
GOV-SOURCE-OF-TRUTH-FRESHNESS-001, including a read-only re-execution of the
red suites.

### A1 — The LO commit-atomicity suites are entirely red and asserting nothing

Two regression modules guard the atomicity of the VERIFIED commit
transaction — the mechanism that makes a terminal verdict durable rather than
file-only. Both still hard-code the pre-rename `skills/verify/` helper paths
and abort before asserting anything:

- `platform_tests/scripts/test_lo_verified_commit_atomicity.py:17-19` —
  `VERIFY_HELPER_PATH`, `CODEX_VERIFY_HELPER_PATH`, and
  `CURSOR_VERIFY_HELPER_PATH` all resolve to
  `.{claude,codex,cursor}/skills/verify/helpers/write_verdict.py`; the module
  fixture loads the helper from the dead claude path (`:24`), and the
  byte-parity check reads the dead codex/cursor paths (`:1130-1131`).
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py:16-20` —
  the `HELPER_COPIES` dict points all three harness entries at the same
  retired `skills/verify/` locations.

Red baseline captured this session (read-only runs, live worktree):

- Combined:
  `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q`
  → **8 failed, 1 passed, 29 errors** (1 warning) in 32.74s.
- Parity module alone → **7 failed** (all 7 tests) in 4.76s.
- Atomicity module alone (derived) → **1 failed, 1 passed, 29 errors**
  (31 tests; the 29 errors are fixture-level `FileNotFoundError` aborts).

This matches the advisory's A1 observation exactly. The live helper topology
is: `.claude/skills/gtkb-verify/helpers/write_verdict.py` (exists),
`.codex/skills/gtkb-verify/helpers/write_verdict.py` (exists),
`.cursor/skills/gtkb-verify/helpers/write_verdict.py` (does NOT exist — Cursor
has no helper copy; its live surface is the SKILL.md fallback shape), and a
divergent `.goose` copy that is A4's concern, not this WI's. The already-green
sibling suite `platform_tests/skills/test_verified_finalization_validation_hardening.py:16-20`
demonstrates the correct repaired shape: `HELPER_COPIES` limited to
claude + codex at `gtkb-verify` paths, with the Cursor surface asserted as
`.cursor/skills/gtkb-verify/SKILL.md` (`:278`), not as a phantom helper copy.

While these suites are red, the atomicity contract is unenforced in CI — a
silent false-green class, and the worst possible time for it: known finalizer
defects are open in exactly this path (`.claude/rules/auto-finalization-sweep.md`,
the interrupted-transaction-recovery advisory family).

### A7 — The VERIFIED evidence gate is unsatisfiable for bridge-only carriers

`.claude/hooks/bridge-compliance-gate.py:2131` hard-blocks any `VERIFIED`
verdict for which `_has_spec_derived_verification` (`:1047-1052`) is false.
That predicate requires concrete Specification Links AND a spec-to-test
heading AND a `COMMAND_EVIDENCE_RE` match (`:174-177`), whose token set is
exclusively test-runner commands:
`python -m pytest | pytest | ruff | npm test | pnpm test | uv run | make test`.

Some threads are legitimate **bridge-only evidence carriers**: their declared
`target_paths` contain only `bridge/**`, they mutate no source, test, or
configuration byte, and their honest verification evidence is git provenance
plus the two governed preflights — there is nothing testable to run. For that
class the gate is unsatisfiable by honest means. The advisory documents three
finalization attempts on the WI-5661 carrier failing on this predicate with a
fully compliant body (seven concrete spec links, seven-row mapping with
`Executed: yes`, a `## Commands Executed` section recording the real git and
preflight invocations).

The exemplar terminal thread
`bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-010.md` (VERIFIED)
shows the workaround shape that eventually cleared the gate: its mapping rows
carry git/preflight evidence (`-010.md:263-271`), and the reviewer executed
two *adjacent* regression suites (81 passed) purely so an honest pytest token
would exist in `## Commands Executed` (`-010.md:295`). That is honest but
structurally forced: it couples carrier verdicts to the state of unrelated
suites and leaves the gate producing verification deadlock and pressure toward
fabricated test evidence for every future carrier. Note the finalization
helper itself is NOT the blocker: `validate_verified_body`
(`.claude/skills/gtkb-verify/helpers/write_verdict.py:293-314`) requires an
executed mapping row and a `## Commands Executed` section but no test-runner
token — the unsatisfiable limb lives solely in the compliance gate.

### Boundary — remaining advisory defects

A2 (preflight-hash/append collision in the finalization helper), A3 (retired
helper-path literal emitted into every verdict's Commit Finalization
Evidence), A4 (stale divergent `.goose` helper copy), A5 (no LO verdict-drafts
allow-list surface), and A6 (LO file-safety Bash heuristic over-match) are out
of scope for this proposal and fold into the WI-5763 governed verdict-filing
consolidation lane per DELIB-202667534 (rows consolidating the verdict-filing
cluster into WI-5763 at program order 160, ahead of this WI at 180).

## Proposed Change

### Slice 1 — A1: re-point and re-green the commit-atomicity suites under commit-first semantics

Repair both modules' helper-path literals to the live `gtkb-verify` topology,
following the shape already proven green in
`test_verified_finalization_validation_hardening.py`:

- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`: re-point the
  claude/codex constants (`:17-18`) to
  `.{claude,codex}/skills/gtkb-verify/helpers/write_verdict.py`; reshape the
  byte-parity check (`:1130-1131`) to the live copy topology
  (claude + codex byte-identical; the absent `.cursor` helper copy is removed
  from the parity set rather than re-pointed at a phantom; the divergent
  `.goose` copy stays excluded pending its A4 disposition in the WI-5763
  lane).
- `platform_tests/skills/test_auto_retire_actuation_helper_parity.py`:
  re-point `HELPER_COPIES` (`:16-20`) to the claude + codex `gtkb-verify`
  copies and drop the phantom cursor entry, mirroring the hardening suite's
  `HELPER_COPIES` (`:16-20`) exactly.

**AT-01 design constraint (DELIB-202667533).** Commit-first ordering governs
every suite expectation this repair touches: repaired expectations must assert
that terminal publication happens only after the backing local commit exists
(commit-before-publish), and must not encode the legacy publish-first shape.
Expectations are written against outcome invariants — on commit failure no
terminal published state and no verdict file survive; on success the commit
contains exactly the reviewed path set — rather than pinning the current
pending-then-promote intermediate mechanics (`write_verdict.py:1184-1230`),
which AT-01 rejected as a durable lifecycle state and whose redesign belongs
to the WI-5742/WI-5666 finalizer lane, not here. If re-greening exposes a
genuine helper-ordering defect (as opposed to a stale expectation), it is
reported to that lane, not silently patched here (GOV-15: this proposal plus
its GO is the approval evidence for repairing these failing tests; no
autonomous fix beyond the approved scope).

### Slice 2 — A7: bridge-only-carrier conditioning of the command-evidence limb

Extend `_has_spec_derived_verification` in
`.claude/hooks/bridge-compliance-gate.py` (`:1047-1052`) so that a `VERIFIED`
verdict satisfies the command-evidence limb without a test-runner token IF AND
ONLY IF:

1. the reviewed operative implementation report resolves from the thread
   chain, AND
2. that report's declared `target_paths` parse cleanly, are non-empty, and
   every entry matches `bridge/**`, AND
3. the verdict body carries governed non-test evidence: the applicability
   and/or ADR/DCL clause preflight invocations plus git provenance commands
   (`git show` / `git diff-tree` class) in its executed evidence.

All other paths are unchanged and fail closed: any non-bridge entry, any
unparseable or absent `target_paths`, or any failure to resolve the reviewed
report leaves the existing test-runner requirement in force.
`COMMAND_EVIDENCE_RE` (`:174-177`) itself is NOT extended — adding preflight
tokens globally would let source-changing threads satisfy the test-evidence
limb with a preflight run, materially weakening the gate exactly where it
earns its keep (the advisory's option rationale, adopted). Per-thread owner
waivers are likewise rejected: a recurring structural mismatch must not become
recurring owner toil (Deterministic Services Principle).

The edit lands identically in the tracked byte-identical activated copy
`config/hooks/gtkb-bridge-compliance-gate.py` (sha-verified identical to the
canonical hook this session) and in the corresponding region of
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. The template
currently diverges from the activated pair in HEAD (pre-existing drift, not
expanded by this change); full template byte-parity restoration is owned by
the WI-5764 parity work already ahead of this WI in program order.

### Slice 3 — regression coverage

Extend `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`
(the module that already exercises the predicate at `:112-138`) with the
carrier-conditioning cases enumerated in the test plan below.

## Cross-Harness Disposition

The compliance-gate edit applies to the canonical hook and its tracked
byte-identical `config/hooks/` copy; the Codex-side adapters
(`.codex/gtkb-hooks/bridge-compliance-gate*.py|.cmd`) invoke the canonical
hook and need no edit (per the adapter header: canonical hook is
`.claude/hooks/bridge-compliance-gate.py`). The suite repairs are
harness-agnostic pytest modules. No managed-skill (SKILL.md) edit and no
dispatcher/TAFE configuration change is in scope.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge audit-trail authority and home of the Mandatory VERIFIED Commit-Finalization Gate; A1 restores its regression enforcement, A7 makes its terminal path honestly satisfiable for carriers (mandatory anchor).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the specification the gate cites as its authority; the conditioned limb preserves its mandate for every source-bearing thread while ending the fabrication pressure the advisory documents for bridge-only carriers.
- SPEC-1662 — assertion quality (GOV-18): a fully-red suite asserts nothing; the repair converts zero-signal modules back into meaningful behavioral assertions.
- GOV-15 — test fix approval gate: the red suites are repaired only under this reviewed proposal's GO; no autonomous test fixing.
- GOV-10 — tests exercise exposed production interfaces (`finalize_verified_commit`, the gate predicate), not internals-only shims.
- GOV-12 — work item drives test creation (Slice 3 gate cases).
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the gate edit keeps write-time enforcement mechanical; the suites restore the review-time layer.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — activated-copy parity discipline for the hook edit.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Codex hook-surface parity foundation (adapters route to the canonical hook).
- GOV-17 — automation-script modification gate: hook and test changes ride this reviewed proposal.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — durable-artifact discipline; carriers reach terminal state through governed evidence instead of accumulating non-terminal.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — endorses by-reference bridge-only carriers; A7 makes that endorsed pattern terminally reachable.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory capture preceded this derived proposal; lifecycle discipline for the carrier class.
- GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 — the source advisory is adapt-class; its gate questions for this scope are resolved by the triage decisions recorded below.
- DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001 — mechanical contract for that gate; evidence routing satisfied in Owner Decisions / Input.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — program PAUTH chain cited in the header; this proposal still awaits its own independent GO.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 — project authorization does not bypass the bridge; this filing is the bridge step.
- GOV-STANDING-BACKLOG-001 — WI-5765 is the MemBase backlog authority for this work.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — the red baseline and every line anchor above derive from fresh reads and a fresh read-only test execution this session.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is an in-root platform surface.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this section satisfies the concrete-links clause.

## Prior Deliberations

Deliberation search performed this session:
`gt deliberations search "LO commit atomicity suites red" --limit 5` returned
five semantic matches (DELIB-0920, DELIB-1314, DELIB-20265126, DELIB-20265693,
DELIB-1660) — adjacent review/verification records, none governing the red
suites or the carrier gate. Governing and adjacent authorities consulted by
id and file:

- DELIB-202667531 — owner advisory-triage directive: fix-class advisories become authorized corrective work items; owner-decision evidence for PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729 and its program PAUTH; bridge protocol explicitly NOT waived per item.
- DELIB-202667533 — AT-01 commit-first finalization ordering (the design authority governing every suite expectation repaired here) and AT-04 program PAUTH with completion discipline.
- DELIB-202667534 — advisory corpus disposition table: row 14 routes the source advisory to WI-5765 ("A1+A7 first"); the verdict-filing cluster rows route A2-A6's remedy surface to WI-5763.
- DELIB-202667104 — LO review of Cursor fallback and Goose manifest parity gaps: establishes the live Cursor surface shape (SKILL.md fallback, no helper copy) that Slice 1 aligns the parity fixtures to, and the Goose-copy disposition context left to the A4/WI-5763 lane.
- DELIB-20265963 — WI-4750 auto-retire verify-helper parity regression: the origin of the parity suite being repaired.
- DELIB-202666065 — WI-5112 hunk-scoped VERIFIED finalization GO: prior governance of the hunk-patch finalization paths the atomicity suite covers.
- `bridge/gtkb-lo-verified-finalization-toolchain-drift-advisory-001.md` — the source advisory (findings A1 `:79-120`, A7 `:262-319`, sequencing `:61-67`).
- `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-010.md` — the A7 exemplar VERIFIED: governed non-test evidence rows (`:263-271`) plus the adjacent-suite pytest workaround (`:295`) that this change makes unnecessary.

## Owner Decisions / Input

Recorded authority for this filing:

- **DELIB-202667531** (owner decision, 2026-07-29): fix-class advisory triage authorized; corrective work items created and authorized ahead of other advisory-derived work; supplies the owner-decision evidence for the corrections project and program PAUTH per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001.
- **DELIB-202667533 AT-01** (owner AUQ, 2026-07-29): commit-first, publish-after finalization ordering ratified; adopted here as the binding design constraint on repaired suite expectations (assert commit-before-terminal-publication; never re-encode publish-first; do not pin the rejected pending-then-promote intermediate).
- **DELIB-202667533 AT-04** (owner AUQ, 2026-07-29): program PAUTH PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM covering source, test_addition, governance_evidence, and bridge mutation classes for this project, with completion discipline.
- **DELIB-202667534** (owner decision, 2026-07-29): row 14 gives A1 a dedicated work item (WI-5765) rather than folding it into the skill-rename umbrella — resolving the source advisory's grilling-gate question 1 — and adopts the advisory's recommended A7 remedy shape (target_paths-conditioned acceptance of governed non-test evidence) as this fix WI's scope, resolving grilling-gate question 5; the WITHDRAWN-route alternative is thereby not selected. Grilling-gate questions 2-4 concern A2/A4/A5 and travel with the WI-5763 lane.

No open owner decision blocks this scope. Implementation proceeds only after
independent Loyal Opposition GO on this proposal, per the unwaived bridge
protocol.

## Requirement Sufficiency

Existing requirements sufficient. GOV-FILE-BRIDGE-AUTHORITY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, SPEC-1662, GOV-15, and the
AT-01 owner decision (DELIB-202667533) already require an enforced atomicity
contract, truthful spec-derived verification evidence, meaningful assertions,
approved test repair, and commit-first ordering; this change makes the
platform enforce what they already require and removes the one case where the
gate demanded evidence that cannot honestly exist. No new or revised
requirement is required before implementation.

## Spec-Derived Test Plan

Red baseline (captured this session, read-only, before any change): combined
run of the two suites → 8 failed, 1 passed, 29 errors; parity module alone →
7 failed; atomicity module alone → 1 failed, 1 passed, 29 errors. The plan's
governing outcomes: red baseline → suites green under commit-first semantics;
a bridge-only carrier passes the evidence gate with governed non-test
evidence; a source-bearing carrier still requires full test-runner evidence.

1. **Atomicity suite green under commit-first semantics** — after Slice 1,
   `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q`
   collects all 31 tests and reports 0 failed / 0 errors; no
   `skills/verify/` literal remains in the module; ordering-sensitive
   expectations assert terminal publication only after the backing commit
   exists (AT-01), including the fail-closed cases (commit failure leaves no
   verdict file and no published terminal state). Derives from
   GOV-FILE-BRIDGE-AUTHORITY-001, DELIB-202667533 AT-01, SPEC-1662, GOV-15.
2. **Parity suite green against the live copy topology** —
   `python -m pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q`
   reports 7/7 passed with `HELPER_COPIES` = claude + codex `gtkb-verify`
   copies (hardening-suite shape); no phantom cursor path. Derives from
   SPEC-1662, GOV-10, DELIB-20265963 lineage.
3. **Bridge-only carrier satisfies the gate** — new
   `test_bridge_only_carrier_verdict_accepts_governed_non_test_evidence` in
   `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py`:
   fixture thread whose reviewed report declares
   `target_paths: ["bridge/<slug>-NNN.md"]`; a VERIFIED body with concrete
   spec links, spec-to-test heading, preflight + `git show`/`git diff-tree`
   evidence, and NO test-runner token is not denied by
   `_has_spec_derived_verification`/`:2131`. Derives from
   GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001,
   ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001.
4. **Source-bearing carrier still requires full evidence** — negative twin:
   identical verdict body, but the reviewed report's `target_paths` include
   one non-bridge path (e.g., `scripts/x.py`) → the write is denied exactly as
   today; and an unparseable/absent `target_paths` report likewise receives no
   exemption (fail-closed). Existing predicate tests (`:112-138`) stay green
   unchanged. Derives from DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001,
   GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001.
5. **COMMAND_EVIDENCE_RE unchanged globally** — assertion that the token set
   at `:174-177` gains no preflight/git tokens (the exemption is
   carrier-conditioned, not global). Derives from the advisory's adopted
   option rationale under DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
6. **Activated-pair parity** — `.claude/hooks/bridge-compliance-gate.py` and
   `config/hooks/gtkb-bridge-compliance-gate.py` remain byte-identical after
   the edit; the template receives the same-region edit. Derives from
   DCL-CROSS-HARNESS-ENFORCEMENT-001.

Execution:
`groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -q`,
plus `ruff check` and `ruff format --check` on all changed Python files.

## Acceptance Criteria

1. Both A1 suites collect and pass fully green (0 failed, 0 errors) against
   the live `gtkb-verify` topology; zero retired `skills/verify/` literals
   remain in either module.
2. Repaired expectations comply with AT-01: commit-before-terminal-publication
   asserted; publish-first never asserted; the rejected pending-then-promote
   intermediate is not pinned as required behavior.
3. A VERIFIED verdict whose reviewed report is bridge-only passes the gate
   with governed non-test evidence; the same body is denied when the report
   is source-bearing, and absent/malformed target_paths receive no exemption.
4. `COMMAND_EVIDENCE_RE` is textually unchanged; no global weakening.
5. Activated gate pair byte-identical; ruff lint and format gates clean; all
   new and existing gate-predicate tests green.
6. The WI-5661 carrier class is honestly finalizable going forward: a
   carrier-shaped verdict body passes the predicate in fixture without
   adjacent-suite padding.

## Risk and Rollback

Risk: LOW-MEDIUM. Slice 1 is test-only repair of modules that currently
assert nothing — the floor is zero signal, so the change is strictly
signal-restoring; the AT-01 constraint prevents re-encoding the rejected
ordering. Slice 2 is a narrowly conditioned gate extension that defaults
closed on every resolution failure; false negatives (carrier wrongly denied)
regress only to today's behavior, and false positives are structurally
excluded by the bridge-only target_paths condition. Sequencing risk with
WI-5763/WI-5764 (shared gate/finalizer surfaces, both ahead in program order)
is bounded: this WI touches the gate predicate region and test modules only,
and the template receives a corresponding-region edit rather than a forced
byte-sync while the WI-5764 parity restoration is in flight. Rollback: each
slice reverts independently by commit; no dispatcher/TAFE configuration
change, no bridge-file deletion, no append-only history rewrite anywhere.

Recommended commit type: fix

## Verification Questions for Loyal Opposition

1. Does the AT-01 constraint as stated (assert commit-before-publish outcome
   invariants; do not pin pending-then-promote mechanics) correctly separate
   this WI's suite-expectation scope from the WI-5742/WI-5666 finalizer
   redesign lane?
2. Is the three-condition carrier exemption (resolved reviewed report +
   all-bridge target_paths + governed non-test evidence present) tight enough
   that no source-bearing thread can reach it, and fail-closed on every
   resolution failure?
3. Is dropping the phantom `.cursor` helper entry from both parity fixtures
   (mirroring the green hardening suite and DELIB-202667104) the correct
   Cursor disposition for this lane, with the `.goose` divergence left to the
   A4/WI-5763 lane?
