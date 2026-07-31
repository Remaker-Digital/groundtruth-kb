NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f0c8ce96-8652-4240-994b-42a6d03516e3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# gtkb-wi5095-adapter-registry-sha-refresh-in-flow — Post-Implementation Report (Slice A: generator fix + generator tests; registry reconciliation + consistency guard owner-deferred)

bridge_kind: implementation_report
Document: gtkb-wi5095-adapter-registry-sha-refresh-in-flow
Version: 005
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-07-09 UTC
Responds-To: bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-004.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5095

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This report delivers **Slice A** of the GO'd `-003` proposal: the generator
defect fix plus its unit tests. The **registry `source_sha256` reconciliation of
the drifted blocks** and the **`test_registry_source_sha256_consistency.py`
consistency guard** are **owner-deferred** (AUQ this session — see Owner
Decisions / Input) because the shared worktree is not quiescent: a concurrent
session's uncommitted canonical edits and untracked skill registrations make a
HEAD-green consistency guard unachievable right now. The mechanical bug fix (the
`unsupported`→`adapter` clobber prevention and the never-insert guarantee) is
complete, isolable, and green; the data reconciliation is a follow-on once the
registry quiesces.

The verified path set for finalization is the four files in `target_paths`
above. None of the four is touched by concurrent work; each is HEAD + this
session's edits only.

## Implemented Changes — Generator Fix

Both `scripts/generate_codex_skill_adapters.py` and
`scripts/generate_antigravity_skill_adapters.py`:

- Replaced the prior whole-block registry rewrite (codex `_rewrite_registry_text`
  / antigravity `_apply_antigravity_registry`) with a single shared
  **adapter-only `source_sha256` refresh** `_refresh_registry_source_sha256(text,
  adapters, harness_table)` in the codex module, reused by the antigravity
  module via its `REGISTRY_HARNESS_TABLE`.
- The refresh is **two-pass per sub-table**: it collects each
  `[capabilities.<harness>]` block, then inspects it, so `status` /
  `source_sha256` line order within the block does not matter (the likely
  prior-strand ordering assumption).
- It refreshes **only** the `source_sha256` line of a block that **already**
  declares `status = "adapter"`. It **never** flips a `status = "unsupported"`
  (or any non-`adapter`) block to `adapter`, **never** rewrites any other field,
  and **never** inserts a missing sub-table. This closes the `-001` defect that
  clobbered the intentional `unsupported` parity overrides (advisory-*,
  formal-artifact-packet-helper, skill-governance-lifecycle) and the antigravity
  over-projection that materialized blocks for un-projected skills.
- Folded the refresh into the default `generate()` flow (after the manifest
  write): a normal run refreshes existing `adapter` blocks' `source_sha256`;
  `--check` reports a stale adapter-block `source_sha256` as drift without
  writing.
- `--update-registry` is now a **deprecated no-op** (the flag is retained and
  prints a deprecation notice to stderr; the refresh is part of the default
  flow). The removed dead helpers were `_registry_adapter_block`,
  `_rewrite_registry_text` (codex) and `_antigravity_subsection_lines`,
  `_emit_antigravity_block`, `_apply_antigravity_registry` (antigravity).
- LF-only + no-trailing-whitespace write contracts and CRLF-normalization on
  read (`read_bytes().decode()`) are preserved.

## Implemented Changes — Tests

`platform_tests/scripts/test_generate_codex_skill_adapters.py` and
`platform_tests/scripts/test_generate_antigravity_skill_adapters.py`:

- Rewrote the registry-update tests to the new refresh-only contract. New /
  rewritten cases per generator: **does-not-insert-missing-block**,
  **refreshes-existing-stale-block**, **preserves-`unsupported`-block**,
  **idempotence**, plus (codex) a **`--update-registry` deprecated-no-op** test
  and (antigravity) a **codex+antigravity converge** test proving each generator
  maintains only its own harness table.
- Fixed a latent Windows-only fixture bug: the registry fixtures now write with
  `newline="\n"`. `Path.write_text` defaults to `\r\n` on Windows, and
  `update_registry` reads the registry via `read_bytes().decode()` (not
  universal-newline `read_text`), so a CRLF fixture made LF-normalization look
  like a spurious registry change. Writing LF fixtures makes the exact-`changed`
  assertions platform-independent and matches the real on-disk registry (LF).

## Deferred Scope (owner-authorized; follow-on)

Deferred to a follow-on once the shared worktree quiesces:

1. **Registry `source_sha256` reconciliation** of the drifted adapter blocks.
   The reliable HEAD-vs-HEAD analysis (git `cat-file HEAD` blobs, generator-
   identical normalization) found **13** blocks where
   `registry@HEAD.source_sha256 != SHA(canonical@HEAD)`. **11 are cleanly
   reconcilable** (canonical committed at HEAD): bridge (codex+antigravity),
   lo-opportunity-radar/antigravity, codex-report/antigravity, decision-capture
   (codex+antigravity), projects/antigravity, gtkb-benchmarks/antigravity,
   gtkb-hygiene-sweep (codex+antigravity), loyal-opposition-hygiene-assessment/
   antigravity. **4 are entangled** with concurrent in-flight work and cannot be
   made HEAD-green now: harness-parity-review (codex+antigravity) whose canonical
   is concurrently modified-but-uncommitted (reconciling to the HEAD sha reds the
   worktree; reconciling to the worktree sha reds HEAD), and
   skill-governance-lifecycle + formal-artifact-packet-helper whose registry
   blocks exist at HEAD but whose canonical skills are untracked.
2. **`platform_tests/scripts/test_registry_source_sha256_consistency.py`** — the
   drift-catching guard asserting every `status = "adapter"` block's
   `source_sha256` equals the normalized SHA of its `adapter_source`. It is
   authored and parked (out of `platform_tests/` so it does not red the suite on
   the un-reconciled drift) pending the reconciliation follow-on; it is verified
   to correctly detect the current drift.

Rationale: `-003` § Risk explicitly directs pausing the reconciliation when the
worktree cannot be cleanly isolated. It cannot be: the registry carries a
concurrent session's uncommitted `source_sha256` refresh + an appended
`managed-skill-adoption-review` registration, and 4 of 13 HEAD-drifts are
entangled with concurrent uncommitted canonical/skill work. The generator fix is
independent of all of this.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-governed implementation under the -004 GO + implementation-start packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bounded PAUTH-backed implementation under the standing reliability project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the standing PAUTH does not bypass GO or implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH / Project / Work Item metadata carried above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification below.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — the `unsupported` status is a parity disposition that MUST be preserved; the fix now honors it (never flips to `adapter`).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the adapter/registry/MANIFEST invariants this generator flow maintains.
- `GOV-STANDING-BACKLOG-001` — WI-5095 is the MemBase backlog authority for this work.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the (deferred) consistency test is the mechanical enforcement layer; the generator fix is the write-time layer.
- `GOV-RELIABILITY-FAST-LANE-001` — single-concern reliability defect-class fix under the standing fast-lane authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all four changed files are in-root platform files; no adopter/application file is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the registry is a governed artifact whose integrity record must stay truthful.

## Specification-Derived Verification (Spec-to-Test Mapping)

| Specification | Test / command | Result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (`unsupported` preserved) | `test_registry_refresh_preserves_unsupported_codex_block`, `test_update_registry_preserves_unsupported_antigravity_block` — a `status = "unsupported"` block with a stale `source_sha256` is left untouched (no flip, sha not refreshed). | PASS |
| Never insert a missing block (`-001` over-projection defect) | `test_registry_refresh_does_not_insert_missing_codex_block`, `test_update_registry_does_not_insert_missing_antigravity_block` — no block is created for a capability that lacks one; `changed` is False. | PASS |
| Refresh existing adapter block's stale sha | `test_registry_refresh_rewrites_stale_codex_source_sha256`, `test_update_registry_refreshes_existing_stale_block` — the `source_sha256` line is replaced with the built adapter hash; surface/status/adapter_source unchanged. | PASS |
| Idempotence | `test_registry_refresh_is_idempotent`, `test_update_registry_is_idempotent`, `test_codex_and_antigravity_registry_updates_converge` — second refresh is a no-op; both generators converge. | PASS |
| `--update-registry` deprecated no-op | `test_update_registry_flag_is_deprecated_noop` — flag prints a deprecation and does not double-run; the default flow still refreshed. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` AND `ruff format --check` on all four changed files. | Clean |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection: all four files in-root; no `applications/` path. | In-root only |

## Verification Evidence

Commands run (project venv), one per line:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short --basetemp .harness-tmp/wi5095d
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py

Observed: **43 passed** (pytest); **All checks passed** (ruff check); **4 files
already formatted** (ruff format --check). The deferred consistency guard was
separately confirmed to detect the current drift before being parked.

## Prior Deliberations

- This thread's `-001`/`-002` (GO) and `-003`/`-004` (REVISED GO) — the `-001`
  whole-block-rewrite approach whose `unsupported`-clobber this fix corrects; the
  `-003` adapter-only design is what this report implements.
- `DELIB-20260709-WI5095-SYSTEMIC-REFRESH-IN-FLOW`, `DELIB-20260709-WI5095-REVISED-DESIGN` (owner decisions cited in the -004 GO).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — the parity contract the `source_sha256` and `unsupported` status both serve.

## Owner Decisions / Input

- AskUserQuestion (this session, 2026-07-09) — reconciliation scope: owner selected **"Registry-only reconciliation"** (fix generators + tests + refresh only the registry `source_sha256` lines; defer adapter-body regeneration; zero adapter/attribution commingle).
- AskUserQuestion (this session, 2026-07-09) — WI-5095 landing: owner selected **"Commit fix+tests, defer reconcile"** — file this implementation report for the generator fix + generator tests only, and defer the registry `source_sha256` reconciliation AND the `test_registry_source_sha256_consistency.py` guard to a follow-on once the shared worktree quiesces.
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5095 by project membership.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and
the harness-onboarding invariants require the registry `source_sha256` to be
truthful for projected adapters AND require intentional `unsupported`
dispositions to be honored; the delivered generator fix serves both and the
deferred reconciliation completes the data half. No new or revised requirement is
needed.

## Recommended Commit Type

Recommended commit type: `fix` — repairs a defect class (the
`unsupported`→`adapter` clobber and the antigravity over-projection insert) in
the two generators, plus the derived regression tests. No new user-facing
capability surface; the registry data reconciliation is deferred.

## Files Changed (scoped — verified path set for finalization)

- `scripts/generate_codex_skill_adapters.py`
- `scripts/generate_antigravity_skill_adapters.py`
- `platform_tests/scripts/test_generate_codex_skill_adapters.py`
- `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`

(The concurrent-session dirty tree contains ~170 other changed files; NONE are
part of this report. The finalization commit must be scoped/hunk-limited to the
four files above.)

## Risk / Rollback

Risk: the refresh must never match-and-rewrite an `unsupported` block —
regression-tested (preserve-`unsupported` cases). Because the worktree is dirtied
by concurrent work, the finalization commit MUST stage only the four files above.

Rollback: single-commit revert of the two generator edits + two generator-test
edits. No KB, registry, adapter, or bridge-state mutation is included in this
slice.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
