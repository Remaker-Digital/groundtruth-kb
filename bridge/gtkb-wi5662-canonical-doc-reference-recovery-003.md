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


# Canonical Skill Documentation Recovery — WI-5662

bridge_kind: prime_proposal
Document: gtkb-wi5662-canonical-doc-reference-recovery
Version: 003
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-002.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5662

target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]

## Claim

This fresh recovery preserves only a mechanically specified canonical
documentation slice. It corrects the historical chain's invalid provenance
without attributing any pre-existing hunk. After independent GO, claim, and a
successful implementation-start packet, it may stage exactly the 21
substitutions below. No generated adapter, template, migration policy, test,
or foreign WI-5640 line is in scope.

## Requirement Sufficiency

Existing requirements sufficient. WI-5662 and DELIB-202667193 authorize the
canonical documentation slice; DELIB-202667194 requires exact isolation from
commingled WI-5640 migration work. No new owner decision is requested.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations

- DELIB-202667193 — S1 canonical docs precede WI-5663 generated-adapter work.
- DELIB-202667194 — all commingled work requires exact index isolation and WI-5640 exclusion.

## Owner Decisions / Input

No new owner decision is required. This is an append-only recovery of the
already approved canonical documentation outcome.

## Exact Index Preconditions

The implementation must begin from these complete index preimages. A changed
blob is a stop condition requiring a new review.

| Target | Required index blob | Allowed-hunk manifest SHA-256 |
| --- | --- | --- |
| .claude/skills/gtkb-bridge/SKILL.md | 60a86337c93f394a9905a6e890d126d5f2ff74ef | 03c45f33783cddde51a2470701ab441680977464a0fd1086ccf8bb808f1627f9 |
| .claude/skills/gtkb-proposal-review/SKILL.md | 0666108438fdc7b303b891204248847aa0ace745 | 4bf69b8a0e3f7dfac56c589ff89fc588c4204f9b393179bc7c7212e1443981fc |
| .claude/skills/gtkb-verify/SKILL.md | 58206159065e174124d941965a367939aaf0f864 | d1a1842e5a02942d6b2b073b74906b1012f0e3ccc794e42ca0cd6dd43fa46f4a |

Each manifest is SHA-256 over the ordered newline-separated records
line-number NUL old-fragment NUL new-fragment specified below. Each individual
row fingerprint is SHA-256 over path NUL line-number NUL old-fragment NUL
new-fragment. The old fragment must appear in the index once and the new
fragment must appear only in the candidate worktree hunk once.

## Allowed Zero-Context Hunk Inventory

All 21 rows are mandatory and have expected count one. No other line may be
placed in the cached patch.

| ID | Context | Exact old fragment -> exact new fragment | Fingerprint |
| --- | --- | --- | --- |
| H01 | gktb-bridge line 70 | .claude/skills/bridge-propose/SKILL.md -> .claude/skills/gtkb-bridge-propose/SKILL.md | 19304df5e8b94e21f9460d3cc6b7d3887cf81dd480a8fe87994c6db30cfb7c91 |
| H02 | gktb-bridge line 78 | .claude/skills/bridge/helpers/scan_bridge.py -> .claude/skills/gtkb-bridge/helpers/scan_bridge.py | 70877df1600460da1b9bc5835d4a5465dab53893528d3a03044862d0c2788658 |
| H03 | gktb-bridge line 83 | python .claude/skills/bridge/helpers/scan_bridge.py --role <prime-builder|loyal-opposition> --compact [--format json|markdown] -> python .claude/skills/gtkb-bridge/helpers/scan_bridge.py --role <prime-builder|loyal-opposition> --compact [--format json|markdown] | 8807607ae43a8bde17dd00804b934673d5a239a6a527a503d2823614808f7f66 |
| H04 | gktb-bridge line 108 | .claude/skills/bridge/helpers/revise_bridge.py -> .claude/skills/gtkb-bridge/helpers/revise_bridge.py | 735c223f3a375beb82762690b18cb98a34b31178fd9cafae5b54c2db77320c16 |
| H05 | gktb-bridge line 134 | python .claude/skills/verify/helpers/write_verdict.py --slug <topic-slug> --body-file <draft-body-file> -> python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug <topic-slug> --body-file <draft-body-file> | b6b32ee6fbb2db0911f4098ab90cc50ac60936ddcbf607aee3790c2b80e23960 |
| H06 | gktb-bridge line 147 | .claude/skills/bridge/helpers/impl_report_bridge.py -> .claude/skills/gtkb-bridge/helpers/impl_report_bridge.py | 681a267e071a79d140f1f5e0e2b24226b4401dc1766ab34a6c32f3c005e80b1a |
| H07 | gktb-bridge line 154 | python .claude/skills/bridge/helpers/impl_report_bridge.py plan <topic-slug> --compact -> python .claude/skills/gtkb-bridge/helpers/impl_report_bridge.py plan <topic-slug> --compact | b0b0d118d1258e015a27fa85075c8aa60ed39a05b9a4382e6d1a14c2116327e1 |
| H08 | gktb-bridge line 162 | python .claude/skills/bridge/helpers/impl_report_bridge.py file <topic-slug> --content-file <completed-report.md> -> python .claude/skills/gtkb-bridge/helpers/impl_report_bridge.py file <topic-slug> --content-file <completed-report.md> | 2e4268fff2c5e9102c61130cdc4f0248c33d629334047e2c99003bb12651f9a5 |
| H09 | gktb-bridge line 170 | .claude/skills/bridge/helpers/protected_write.py -> .claude/skills/gtkb-bridge/helpers/protected_write.py | 88445b8ecf9be39a6989b9689007bc26a4ecbd135662f48d975d1d0d472ca177 |
| H10 | gktb-bridge line 175 | python .claude/skills/bridge/helpers/protected_write.py --target <path> --content-file <path> --packet <packet-path> -> python .claude/skills/gtkb-bridge/helpers/protected_write.py --target <path> --content-file <path> --packet <packet-path> | a184455bf57e3f20f305434bfd6a8db6df81fe27d519179837f8ebe440b31d41 |
| H11 | gktb-bridge line 186 | .claude/skills/bridge/helpers/show_thread_bridge.py -> .claude/skills/gtkb-bridge/helpers/show_thread_bridge.py | 7b123b73a3236aae410bd042f76910b8ce437838565f207a292903b008c9391b |
| H12 | gktb-bridge line 191 | python .claude/skills/bridge/helpers/show_thread_bridge.py <topic-slug> [--format json|markdown] [--preview-lines N] -> python .claude/skills/gtkb-bridge/helpers/show_thread_bridge.py <topic-slug> [--format json|markdown] [--preview-lines N] | b542286cdaff4a25dc2fa100632e53c8badaefa4b54f85b8b05b566749034582 |
| H13 | gktb-bridge line 248 | .claude/skills/bridge-propose/SKILL.md -> .claude/skills/gtkb-bridge-propose/SKILL.md | 43bd6e13bc03b1d8754f8b24e4c9e346007173c5a795ce8ef1b542e0fd93c574 |
| H14 | gktb-bridge line 248 | .claude/skills/proposal-review/SKILL.md -> .claude/skills/gtkb-proposal-review/SKILL.md | c17b318f116cf31f17880fa64564e4097a2c9450913dbd26f6ee1617236bd5fc |
| H15 | gktb-bridge line 248 | .claude/skills/send-review/SKILL.md -> .claude/skills/gtkb-send-review/SKILL.md | 2d9cadb95f8146bb4bc8c708a784b10d90bf6aa3d1897cebbb5c66e4e6a52382 |
| H16 | gktb-bridge line 260 | .codex/skills/bridge/SKILL.md -> .codex/skills/gtkb-bridge/SKILL.md | 8c5889a5d0f002da070bff1ebcf84474c31b360aad714418f050bd44045f3ff6 |
| H17 | gktb-proposal-review line 51 | .claude/skills/verify/helpers/write_verdict.py --slug <slug> --body-file <draft-body-file> -> .claude/skills/gtkb-verify/helpers/write_verdict.py --slug <slug> --body-file <draft-body-file> | 274246983bf85a71500f07a72fb22db315aa81901fd2d7afa60121f26c3f1178 |
| H18 | gktb-verify line 101 | python .claude/skills/verify/helpers/write_verdict.py --slug <slug> --body-file <draft-body-file> -> python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug <slug> --body-file <draft-body-file> | 82d83824f3321863e723fdef347a273877c44519092308ad1310cb3a3f9c66ca |
| H19 | gktb-verify line 115 | python .claude/skills/verify/helpers/write_verdict.py --slug <slug> --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message <type(scope): message> --include <verified-path> [--include <verified-path> ...] -> python .claude/skills/gtkb-verify/helpers/write_verdict.py --slug <slug> --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message <type(scope): message> --include <verified-path> [--include <verified-path> ...] | df3a322d09e26bc8540cb248c44a550983f3b63f03b62e5b4bc6e1727b4089db |
| H20 | gktb-verify line 197 | .claude/skills/verify/SKILL.md -> .claude/skills/gtkb-verify/SKILL.md | 9ab106ec7bbac47e652aa985725d2150a5aa474b2c661ce6a1b4e91149bf4ade |
| H21 | gktb-verify line 197 | .codex/skills/verify/SKILL.md -> .codex/skills/gtkb-verify/SKILL.md | c0988bcc4affaa37bd4d3298c7c80260dd0eae5c25a66bb87d3ee24225588834 |

## Prohibited WI-5640 Hunks

The 24 currently added lines in gktb-bridge/SKILL.md whose added text contains
config/agent-control/gtkb- are read-only foreign evidence. They are the zero-
context hunk anchors 18, 33, 55, 128, 134, 138, 214, and 225; where an anchor
contains multiple such lines, every line is prohibited. The staged patch must
contain zero additions or deletions matching config/agent-control/gtkb- and
must not otherwise alter those eight hunks. The allowed H05 at anchor 134 is
the sole independent skill-helper line in that mixed hunk and must be emitted
as its own zero-context patch fragment.

## Cross-Harness Disposition

- Claude: these three canonical documents are the only source correction.
- Codex, Goose, Cursor, Antigravity, API harness, Ollama, and OpenRouter:
  generated projections are intentionally deferred under the typed
  sequenced_adapter_regeneration waiver in DELIB-202667193. The waiver expires
  at independent WI-5662 terminal review and the next action is a fresh
  WI-5663 adapter-regeneration GO. It never waives runtime-helper parity.
- No unmanaged harness surface is created or changed.

## Implementation And Verification Plan

1. After GO, acquire the claim and obtain an implementation-start packet. Stop
   on any packet, blob, manifest, or worktree assertion failure.
2. Materialize only H01 through H21 as a reviewed zero-context cached patch.
   Run git apply --cached --check before application. The cached path set must
   equal the three declared targets.
3. Verify all 21 cached row fingerprints and the three cached manifest hashes.
   The cached bridge diff must contain no config/agent-control/gtkb- text.
   The same 24 foreign additions must remain in the unstaged bridge diff.
4. Run git diff --check --cached, the focused skill catalog test, and exact
   cached residual scans for every old fragment above. Commit only the
   authorized cached slice, then file a strict implementation report with
   commit-finalization evidence for independent LO review.

## Specification-Derived Verification Mapping

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge authority | Fresh GO, PB claim, packet, and cached three-path list | No file is staged before authorization. |
| Canonical completeness | H01-H21 fingerprint and residual checks | Exactly the listed bare references are removed. |
| WI-5640 isolation | Cached and unstaged assertions at eight anchors | All 24 foreign additions remain unstaged and unowned. |
| Skill structure | focused catalog test and cached diff check | No structural or whitespace regression. |

## Acceptance Criteria

- The cached and committed content contains exactly H01-H21 on the named
  preimages.
- All 24 config/agent-control/gtkb- foreign additions remain unstaged.
- Generated adapters, templates, tests, policies, and historical artifacts are
  excluded.
- PB provides commit-finalization evidence; only independent LO may determine
  VERIFIED.

## Risks And Rollback

The principal risk is absorbing a foreign migration hunk from the mixed bridge
document. Blob binding, row fingerprints, prohibited-hunk assertions, and a
zero-context cached patch make that failure visible before commit. A rollback
is a separately governed three-file revert and never rewrites history or
foreign worktree bytes.

## Recommended Commit Type

docs
