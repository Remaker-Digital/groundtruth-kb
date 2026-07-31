REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5662-canonical-doc-reference-recovery
Version: 013
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-012.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662
target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]
observed_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]
expected_absent_paths: [".cursor/skills/gtkb-verify/helpers/write_verdict.py"]
kb_mutation_in_scope: false

This proposal performs no MemBase mutation.

# WI-5662 canonical documentation and helper-reference recovery

## Revision Claim

This HEAD-based revision replaces version 007's stale 21-hunk patch with the
actual remaining WI-5662 delta. The 21 canonical-document substitutions are
already present in clean current files after owner-authored broad commit
`db07f9dcfe7e7de8addc850729209278472cb0fe`; they are read-only verification
evidence and are not re-proposed or retroactively authorized.

One canonical helper hint remains live and stale at
`.claude/skills/gtkb-verify/helpers/write_verdict.py:1009`. After independent
GO, a fresh implementation claim, and a schema-v3 implementation-start packet,
this proposal changes that one literal and adds one focused regression in the
existing canonical-helper hardening test module. No generated adapter is
edited; WI-5663 remains the sequenced regeneration owner for its four declared surfaces.

Version 012 accepted the two-target engineering design and the honest five-failure
baseline. This revision corrects its evidence defects and resolves the Cursor
disposition from current governed authority: WI-5642 records absent Cursor
fallback surfaces as intentional DEFERRED/WAIVED state and forbids placeholder
generation; WI-5665 owns broken and false-green skill-rename tests, with exact
proposal `gtkb-wi5665-cursor-fallback-hardening-test-repair-001` now covering
the five false-red parametrizations. This slice makes no full-module-pass claim
until that WI-5665 proposal is implemented and independently verified.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5662 covers canonical SKILL
documentation and helper docstrings/hints. `DELIB-202667193` sequences the four
non-Cursor generated-adapter surfaces named by WI-5663 after this canonical
slice, while `DELIB-202667194` requires current-byte isolation from WI-5640.
WI-5642 already governs absent Cursor fallback surfaces as intentional deferral,
and WI-5665 already governs broken and false-green skill-rename tests. The exact
WI-5665 Cursor-hardening proposal makes the disposition executable without a
new MemBase mutation, WI-5663 scope expansion, test weakening, or placeholder
adapter generation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`

## Prior Deliberations

- `DELIB-202667193` - canonical source first, then WI-5663 generated-adapter regeneration, with independent per-slice gates.
- `DELIB-202667194` - govern existing work, isolate exact skill-rename bytes, and exclude WI-5640 changes.
- `DELIB-202667421` and `DELIB-202667422` - do not reuse the earlier incomplete GO/report; use a fresh complete lifecycle.
- `bridge/gtkb-wi5662-canonical-doc-reference-recovery-010.md` - accepts the two-target canonical delta but rejects the false full-module validation claim because the Cursor projection is absent.
- `bridge/gtkb-wi5662-canonical-doc-reference-recovery-012.md` - accepts the engineering design and requires corrected blob evidence, durable Cursor disposition, duplicate-thread disposition evidence, and an absent-path annotation.
- `bridge/gtkb-skill-rename-cursor-goose-parity-002.md` and WI-5642 - govern absent Cursor fallback surfaces as intentional DEFERRED/WAIVED state and forbid placeholder generation.
- `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-001.md` under WI-5665 - exact live proposal for the five false-red Cursor parametrizations.

No prior deliberation authorizes weakening Cursor coverage. The current authority separates intentional Cursor fallback deferral (WI-5642), false-red test repair (WI-5665), and the four non-Cursor generated surfaces in WI-5663.

## Owner Decisions / Input

- `DELIB-202667193` — canonical source first, then WI-5663 generated adapter
  regeneration, with independent per-slice gates.
- `DELIB-202667194` — govern existing work, isolate exact skill-rename bytes,
  and exclude WI-5640 changes.
- `DELIB-202667421` and `DELIB-202667422` — do not reuse the earlier incomplete
  GO/report; use a fresh complete lifecycle.
- No new owner decision is required.

## Governed Thread Consolidation

`gtkb-wi5662-canonical-doc-reference-recovery` is the sole implementation
controller for WI-5662.

- `gtkb-wi5662-canonical-skill-reference-repair` is terminal `WITHDRAWN` at
  version 003. Its incomplete inventory-free proposal is historical evidence.
- `gtkb-wi5662-skill-rename-canonical-doc-refs` is mechanically quarantined,
  not executable: its historical version 005 carries decorated metadata
  `005 (NEW; post-implementation report)`. A v011 `WITHDRAWN` candidate passed
  content preflights but was not filed because the typed publication control
  plane rejected the candidate lifecycle with `WRONG_BRIDGE_VERSION_METADATA`.
  The claim was released and the draft removed; no bypass write occurred. This
  is the explicit reason that malformed sibling cannot receive a terminal file.

Neither sibling may be used for implementation authority.

## Reconciled Canonical-Document Evidence

The three version-007 document preimages are stale because all 21 intended old
fragments are absent and their canonical replacements are present. The current
paths are clean and bound to these HEAD blobs:

| Read-only canonical document | HEAD blob | Current result |
| --- | --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `31add23aa7e31c843165b2421cf0b6f76bec4a67` | All 16 listed bridge/proposal/review/helper references use `gtkb-*`. |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `c65e80dd7bc4527016e60e8325acd69730c8714f` | Verdict helper points to canonical `gtkb-verify`. |
| `.claude/skills/gtkb-verify/SKILL.md` | `3e6b1d19be67a40b178fe667bbb80c0bdc2b6aeb` | Both helper commands and Claude/Codex canonical skill paths use `gtkb-verify`. |

Each full value was copied from `git rev-parse HEAD:<path>`; `git cat-file -t`
returns `blob` for all three objects.

`git show db07f9dc -- <three documents>` proves those replacements and also
shows unrelated WI-5640 path changes in the bridge document. This proposal
neither attributes nor re-commits those unrelated bytes.

## Exact Remaining Source Delta

Both declared mutation targets are currently clean. Required preimages:

| Target | Required HEAD blob | Allowed change |
| --- | --- | --- |
| `.claude/skills/gtkb-verify/helpers/write_verdict.py` | `7366e72be3aa8c802dd98b667f3e83faa80aae68` | At line 1009, replace exactly `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` with `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`. Expected old count: one. |
| `platform_tests/skills/test_verified_finalization_validation_hardening.py` | `5b628709a504c73e546a4753382ef46945d2f990` | Add `test_canonical_claude_helper_finalization_hint_uses_gtkb_verify`, which calls `_append_commit_finalization_evidence` on the canonical Claude helper, requires the `gtkb-verify` path, and rejects the retired bare `verify` path. |

Any preimage mismatch or old-fragment count other than one is a stop condition.
The four non-Cursor generated projections named by WI-5663 remain untouched; the Cursor hardening-test correction is governed separately by WI-5665.

## Cursor And Generated-Adapter Disposition

- Current evidence: `.cursor/skills/gtkb-verify/helpers/write_verdict.py` is
  absent, causing exactly five Cursor parametrizations in
  `test_verified_finalization_validation_hardening.py` to fail with
  `FileNotFoundError`; the remaining 17 tests pass.
- Canonical registry evidence: `config/agent-control/harness-capability-registry.toml`
  declares `skill.verify` on Cursor as `status = "fallback"` at
  `.cursor/skills/gtkb-verify/SKILL.md`; the surface and helper have never been
  tracked. WI-5642 and `gtkb-skill-rename-cursor-goose-parity-002` classify
  that absence as intentional DEFERRED/WAIVED state and forbid placeholders.
- Exact repair owner: open WI-5665 covers broken and false-green skill-rename
  tests. `gtkb-wi5665-cursor-fallback-hardening-test-repair-001` targets the
  hardening module, preserves Cursor path-parsing coverage, and replaces the
  false helper-load assumption with explicit registry-backed fallback coverage.
- WI-5663 remains limited to its recorded `.codex/.goose/.agent/.api-harness`
  regeneration scope; it is not expanded to Cursor.
- This proposal does not run or claim the full module as a WI-5662 acceptance
  gate. The five failures remain visible until the WI-5665 repair is implemented
  and independently verified; no missing projection is accepted as native.

## Implementation Plan

1. After GO, acquire this controller claim and obtain a schema-v3 start packet
   for exactly the two target paths.
2. Recheck both HEAD blobs and the one-count old literal, then apply only the
   declared source substitution and named focused regression.
3. Prove the cached path set is exactly the two targets and that the three
   canonical documents plus all WI-5640 bytes remain unstaged.
4. Run the named focused regression only, Ruff check and format-check on the two
   Python targets, exact residual scans, and `git diff --check`. Separately
   report the known full-module baseline as 5 Cursor failures / 17 passes; do
   not claim it as a passing WI-5662 gate.
5. Commit only the reviewed two-path slice, then file a strict implementation
   report with immutable commit evidence for independent terminal review.

## Cross-Harness Disposition

- Claude canonical source: update the one canonical helper hint and its direct
  canonical-helper regression in this slice.
- Cursor: the projection is an intentional fallback deferral under WI-5642;
  the five false-red parametrizations are exactly governed by WI-5665 proposal
  `gtkb-wi5665-cursor-fallback-hardening-test-repair-001`. No placeholder is
  created and no full-module pass is claimed here.
- Codex, Goose, Antigravity, API harness, Ollama, OpenRouter, and Alibaba Cloud
  Studio: generated projections remain unchanged under the same typed
  `sequenced_adapter_regeneration` disposition; WI-5663 is the named next owner
  and the disposition expires only at WI-5663 terminal verification.
- No runtime-helper behavior changes. The canonical helper remains the source
  for generated adapters.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Expected Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Numbered-chain read plus claim/start/report sequence | planned | Only this controller can reach implementation authority; siblings remain non-executable. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Candidate applicability preflight | executed | PASS - PAUTH, project, WI, inline-JSON target paths, and observed paths are present. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Candidate applicability preflight | executed | PASS - all required/advisory specifications cited; no blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Named focused regression plus this per-specification mapping | planned | The exact canonical hint behavior passes without claiming the currently failing full parity module. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Thread disposition, owner-decision, and target-boundary inspection | executed/planned | Existing bytes and deferred parity are preserved as durable governed evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Named executable regression and residual scan | planned | The canonical reference requirement is enforced by code, not prose alone. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | GO, exact claim, schema-v3 packet, implementation report, independent verdict | planned | Each lifecycle transition occurs only after its trigger. |
| `GOV-WORK-TREE-HYGIENE-001` | Preimage, cached path list, Ruff, format, and diff checks | planned | Exactly two authorized paths; no foreign bytes staged or committed. |
| `ADR-CROSS-HARNESS-PARITY-001` | Current full-module baseline plus WI-5642 and exact WI-5665 follow-on | executed/planned | Five Cursor false-red failures remain explicitly visible until the registry-backed fallback test repair is independently verified. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness disposition audit | executed | Cursor is explicitly DEFERRED/WAIVED under WI-5642, false-red tests are owned by WI-5665, and non-Cursor generated surfaces remain in WI-5663. |

## Acceptance Criteria

- The one live canonical helper hint uses `gtkb-verify` and the named focused
  regression passes.
- The 21 already-landed document replacements remain byte-identical and are
  current evidence, not reimplemented.
- The known full hardening baseline is reported truthfully as 5 Cursor failures
  / 17 passes and is not claimed as a passing WI-5662 gate.
- Cursor fallback absence remains governed by WI-5642 and its false-red
  hardening expectations remain governed by the exact WI-5665 proposal; the
  four WI-5663 generated surfaces remain separately sequenced.
- No generated adapter, WI-5640 byte, bridge-history file, configuration, or
  out-of-scope state file enters the source commit.
- Both sibling threads remain non-executable under governed disposition.
- Independent LO provides terminal verdict and commit-finalization evidence.

## Risk And Rollback

The main risk is either absorbing generated-adapter scope or falsely green-lighting
the absent Cursor projection. Exact two-path binding, the named focused test,
explicit failing baseline, and the WI-5642/WI-5665 disposition prevent both. Rollback is a
separately governed revert of only the eventual two-path source/test commit;
bridge history and observed documents remain append-only/unchanged.

## Recommended Commit Type

`fix:`

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

