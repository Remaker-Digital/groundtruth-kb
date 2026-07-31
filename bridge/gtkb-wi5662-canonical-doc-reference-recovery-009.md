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
Version: 009
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-008.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662
target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]
observed_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]
kb_mutation_in_scope: false

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

## Requirement Sufficiency

Existing requirements sufficient. Existing owner decisions and the active
bounded sweep PAUTH are sufficient.
WI-5662 explicitly covers canonical SKILL documentation and helper
docstrings/hints; `DELIB-202667193` sequences generated adapter regeneration as
WI-5663 after this canonical slice; `DELIB-202667194` requires current-byte
isolation from WI-5640.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-WORK-TREE-HYGIENE-001
- ADR-CROSS-HARNESS-PARITY-001
- DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001

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
  version 003. Its incomplete inventory-free proposal is preserved only as
  historical evidence.
- `gtkb-wi5662-skill-rename-canonical-doc-refs` is mechanically quarantined,
  not executable: its historical version 005 carries decorated metadata
  `005 (NEW; post-implementation report)`. The typed publication authority
  rejects any attempted append with
  `WRONG_BRIDGE_VERSION_METADATA`. A version-011 withdrawal attempt therefore
  created no live file, and its claim was released. That malformed chain is
  preserved read-only and cannot issue a packet or compete with this controller.

This is a governed terminal disposition for the first sibling and a
mechanically enforced quarantine for the second; neither may be claimed,
appended, or used for implementation.

## Reconciled Canonical-Document Evidence

The three version-007 document preimages are stale because all 21 intended
old fragments are absent and their canonical replacements are present. The
current paths are clean and bound to these HEAD blobs:

| Read-only canonical document | HEAD blob | Current result |
| --- | --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `31add23a87c490ebff4270e71289786460d9f414` | All 16 listed bridge/proposal/review/helper references use `gtkb-*`. |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `c65e80dd7a1c35866fca16b14736574c3ab882ed` | Verdict helper points to canonical `gtkb-verify`. |
| `.claude/skills/gtkb-verify/SKILL.md` | `3e6b1d19ba94dc6c2b74c3a86dcd8cbc650e0c79` | Both helper commands and Claude/Codex canonical skill paths use `gtkb-verify`. |

`git show db07f9dc -- <three documents>` proves those exact replacements and
also proves the broad commit included unrelated WI-5640 path changes in the
bridge document. This proposal neither attributes nor re-commits those
unrelated bytes.

## Exact Remaining Source Delta

Both declared mutation targets are currently clean. Required preimages:

| Target | Required HEAD blob | Allowed change |
| --- | --- | --- |
| `.claude/skills/gtkb-verify/helpers/write_verdict.py` | `7366e72be3aa8c802dd98b667f3e83faa80aae68` | At line 1009, replace exactly `.claude/skills/verify/helpers/write_verdict.py --finalize-verified` with `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`. Expected old count: one. |
| `platform_tests/skills/test_verified_finalization_validation_hardening.py` | `5b628709a504c73e546a4753382ef46945d2f990` | Add one direct regression that calls `_append_commit_finalization_evidence` on the canonical Claude helper, requires the `gtkb-verify` path, and rejects the retired bare `verify` path. |

Any preimage mismatch or old-fragment count other than one is a stop condition
requiring fresh review. The generated `.codex` helper remains untouched and is
expected to retain the stale literal until WI-5663 regenerates all adapters
from canonical sources.

## Implementation Plan

1. After GO, acquire this controller claim and obtain a schema-v3 start packet
   for exactly the two target paths.
2. Recheck both HEAD blobs and the one-count old literal, then apply only the
   declared source substitution and focused regression.
3. Prove the cached path set is exactly the two targets and that the three
   canonical documents plus all WI-5640 bytes remain unstaged.
4. Run the focused new regression, the full hardening module, Ruff check and
   format-check on the two Python targets, exact residual scans, and
   `git diff --check`.
5. Commit only the reviewed two-path slice, then file a strict implementation
   report with immutable commit evidence for independent terminal review.

## Cross-Harness Disposition

- Claude canonical source: update the one canonical helper hint and its direct
  canonical-helper regression in this slice.
- Codex, Cursor, Goose, Antigravity, API harness, Ollama, OpenRouter, and
  Alibaba Cloud Studio: generated projections are intentionally unchanged in
  this slice under the typed `sequenced_adapter_regeneration` disposition in
  `DELIB-202667193`; WI-5663 is the named next owner and the disposition expires
  at WI-5663 terminal verification.
- No runtime-helper behavior changes. This is a reference-string correction;
  the canonical helper remains the behavioral source for generated adapters.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Canonical helper hint | New direct `_append_commit_finalization_evidence` regression | Emitted evidence names `.claude/skills/gtkb-verify/...` and contains no retired bare path. |
| Canonical-document completeness | Exact residual scan across three observed documents | Zero old fragments; all 21 current replacements remain present and unchanged. |
| Canonical/generated ownership | Staged path list and `.codex` status | Only canonical helper plus test are staged; generated helper is deferred to WI-5663. |
| Worktree isolation | Preimage blobs and cached diff | No WI-5640 or broad-commit byte is absorbed. |
| Source/test quality | Focused/full pytest, Ruff check/format, diff check | All pass. |
| Unique lifecycle | Direct thread-state reads | One controller; one sibling WITHDRAWN; one malformed sibling quarantined and unclaimable. |

## Acceptance Criteria

- The one live canonical helper hint uses `gtkb-verify` and has a focused
  regression.
- The 21 already-landed document replacements remain byte-identical and are
  verified as current evidence, not reimplemented.
- No generated adapter, WI-5640 byte, bridge-history file, configuration,
  MemBase state, or runtime state enters the source commit.
- Both sibling threads remain non-executable under their governed dispositions.
- Independent LO provides terminal verdict and commit-finalization evidence.

## Risk And Rollback

The main risk is accidentally editing the generated Codex helper or absorbing
unrelated broad-commit history. Exact two-path binding, clean preimages, and
staged-path assertions fail closed. Rollback is a separately governed revert
of only the eventual two-path source/test commit; bridge history and the three
observed documents remain append-only/unchanged.

## Recommended Commit Type

`fix`

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
