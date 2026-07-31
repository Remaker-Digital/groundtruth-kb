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
Version: 011
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-010.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662
target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]
observed_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md", ".cursor/skills/gtkb-verify/helpers/write_verdict.py"]
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
edited; WI-5663 remains the sequenced regeneration owner.

Version 010 confirmed the two-target boundary and identified a pre-existing
five-failure Cursor projection dependency in the full hardening module. This
revision takes its route 2: it defines a genuinely scoped canonical-helper
regression, records the missing Cursor projection as live WI-5663 work, and
makes no full-module-pass claim until adapter parity is restored.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5662 covers canonical SKILL
documentation and helper docstrings/hints. `DELIB-202667193` sequences generated
adapter regeneration as WI-5663 after this canonical slice, while
`DELIB-202667194` requires current-byte isolation from WI-5640. The Cursor
projection absence does not require weakening coverage or expanding WI-5662;
it requires truthful scoping and an explicit sequenced disposition.

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

No prior deliberation authorizes weakening Cursor coverage or bypassing WI-5663.

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
  `005 (NEW; post-implementation report)`. Typed publication rejects any append
  with `WRONG_BRIDGE_VERSION_METADATA`.

Neither sibling may be used for implementation authority.

## Reconciled Canonical-Document Evidence

The three version-007 document preimages are stale because all 21 intended old
fragments are absent and their canonical replacements are present. The current
paths are clean and bound to these HEAD blobs:

| Read-only canonical document | HEAD blob | Current result |
| --- | --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `31add23a87c490ebff4270e71289786460d9f414` | All 16 listed bridge/proposal/review/helper references use `gtkb-*`. |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `c65e80dd7a1c35866fca16b14736574c3ab882ed` | Verdict helper points to canonical `gtkb-verify`. |
| `.claude/skills/gtkb-verify/SKILL.md` | `3e6b1d19ba94dc6c2b74c3a86dcd8cbc650e0c79` | Both helper commands and Claude/Codex canonical skill paths use `gtkb-verify`. |

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
The generated projections remain untouched until WI-5663.

## Cursor And Generated-Adapter Disposition

- Current evidence: `.cursor/skills/gtkb-verify/helpers/write_verdict.py` is
  absent, causing exactly five Cursor parametrizations in
  `test_verified_finalization_validation_hardening.py` to fail with
  `FileNotFoundError`; the remaining 17 tests pass.
- Governing owner decision: `DELIB-202667193` assigns all generated adapter
  regeneration, including Cursor, to open work item WI-5663 after WI-5662's
  canonical slice.
- Required follow-on: WI-5663 must regenerate the Cursor projection and restore
  full hardening-module parity before WI-5663 can be terminally verified.
- This proposal does not run or claim the full module as a WI-5662 acceptance
  gate, does not silently exclude a passing projection, and does not weaken or
  alter any Cursor test. The failure remains visible and blocking for WI-5663.

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
- Cursor: current projection absence and five failing parametrizations are
  explicitly assigned to open WI-5663 under `DELIB-202667193`; no test is
  weakened and no pass is claimed here.
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
| `ADR-CROSS-HARNESS-PARITY-001` | Current full-module baseline plus WI-5663 follow-on | executed/planned | Five Cursor failures remain explicitly visible until adapter regeneration restores parity. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Cross-harness disposition audit | executed | Every generated surface has a named sequenced disposition; no missing projection is accepted as healthy. |

## Acceptance Criteria

- The one live canonical helper hint uses `gtkb-verify` and the named focused
  regression passes.
- The 21 already-landed document replacements remain byte-identical and are
  current evidence, not reimplemented.
- The known full hardening baseline is reported truthfully as 5 Cursor failures
  / 17 passes and is not claimed as a passing WI-5662 gate.
- Cursor and every generated adapter remain assigned to WI-5663 without test
  weakening or silent parity acceptance.
- No generated adapter, WI-5640 byte, bridge-history file, configuration, or
  out-of-scope state file enters the source commit.
- Both sibling threads remain non-executable under governed disposition.
- Independent LO provides terminal verdict and commit-finalization evidence.

## Risk And Rollback

The main risk is either absorbing generated-adapter scope or falsely green-lighting
the absent Cursor projection. Exact two-path binding, the named focused test,
explicit failing baseline, and WI-5663 disposition prevent both. Rollback is a
separately governed revert of only the eventual two-path source/test commit;
bridge history and observed documents remain append-only/unchanged.

## Recommended Commit Type

`fix:`

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
