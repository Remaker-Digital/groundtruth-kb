NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4464-commit-pathspec-safety-detector
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4464
target_paths: ["scripts/check_commit_pathspec_safety.py", "platform_tests/scripts/test_check_commit_pathspec_safety.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4464 Slice A: Commit pathspec-safety detection mechanism (bridge+source staged-index contamination detector)

## Summary

WI-4464 (P1, `git-workflow`, origin=improvement) captures a concurrency git-workflow hazard observed during the 2026-06-11 FAB-20 recovery: background governance hooks auto-stage bridge-queue files (`bridge/INDEX.md`, `bridge/*.md`) into the git index between tool calls, so a plain `git commit` **without an explicit pathspec** commits whatever the index holds rather than the intended files. This produced mislabeled commit `772a186b` — a FAB-20 commit message carrying backlog-triage + prefix-split contents, while the intended FAB-20 files stayed uncommitted. Full forensics: `memory/recovery-2026-06-11-fab20-commit-collision.md`. The proven manual mitigation already in use is "ALWAYS commit with explicit `-- <pathspec>` in this repo."

The WI lists three candidate mitigations to evaluate: (a) a commit wrapper / pre-commit advisory that warns when `git commit` runs without an explicit pathspec while non-target files are staged; (b) tooling that discourages `git reset` on shared branches when a concurrent-session lock / recent foreign commit is detected; (c) scoping the auto-staging hooks so they do not pollute an in-progress Prime commit index.

**This proposal is Slice A of mitigation (a):** it delivers the **tested detection mechanism** — a standalone, stdlib-only `scripts/check_commit_pathspec_safety.py` that classifies the staged index and detects the *contamination signature*: a staged set that mixes bridge-queue files with non-bridge source files (the exact shape of the `772a186b` incident, and an existing GT-KB protocol violation per `.claude/rules/bridge-essential.md` "Scoped commits only").

**Scope boundary (surfaced, not smuggled):** the batch-1 PAUTH authorizes `source` + `test_addition` only. *Wiring* this checker into a commit-time interception point — one line appended to the existing `.githooks/pre-commit` gate chain, or a PreToolUse commit-guard hook — is a hook/config-registration mutation class **outside** this PAUTH. It is therefore deliberately deferred to a follow-on slice (Slice B) under an appropriate authorization. Slice A delivers the hard, reusable, fully unit-testable part now (detection logic + CLI + JSON + strict-mode exit code), so the deferred wiring is a trivial one-line change. Mitigations (b) (reset-guard) and (c) (auto-stager scoping) remain separate future slices. This mirrors GT-KB's established "advisory mechanism first → blocking wiring later" slice pattern (e.g. `adr_dcl_clause_preflight`).

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4464 is the backlog authority for this fix (P1 git-workflow reliability hazard).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implementation proceeds under the active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1`, which includes WI-4464 and allows `source` + `test_addition`. Slice A stays strictly within that scope.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `bridge/INDEX.md` + `bridge/*.md` are canonical bridge workflow state; the auto-stage → wrong-commit hazard threatens that audit trail. The detector surfaces the contamination signature without altering bridge authority or touching any bridge file.
- **`.claude/rules/bridge-essential.md`** (Invariants: "Scoped commits only. Bridge work commits should not bundle unrelated source changes.") — the detector operationalizes this existing protocol invariant: a staged set mixing bridge-queue and non-bridge source files is precisely the violation it flags.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB` (`scripts/`, `platform_tests/scripts/`).
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked detection mechanism with explicit test coverage and explicit lifecycle states (candidate mitigations a/b/c, this slice's deferred-wiring follow-on, verified-by-test acceptance); the scope boundary (deferred wiring) is stated plainly rather than silently overreached.

## Requirement Sufficiency

Existing requirements sufficient. The hazard is documented (WI-4464 + the 2026-06-11 forensic record), the bounded PAUTH authorizes the `source` + `test_addition` work, and the detector enforces an existing protocol invariant (`.claude/rules/bridge-essential.md` "Scoped commits only"). No new or revised formal specification is required for Slice A. The deferred wiring slice will declare its own (hook/config) scope when authorized.

## Prior Deliberations

- **`memory/recovery-2026-06-11-fab20-commit-collision.md`** — authoritative forensic record of the `772a186b` mislabel + `git reset` orphan incident that WI-4464 captures. Primary source for the contamination signature this detector targets ("the index is not stable across tool calls; background hooks auto-stage bridge-queue files; plain `git commit` grabbed the wrong files").
- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ decision (2026-06-13) admitting WI-4464 (and 8 sibling reliability WIs) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`).
- **`bridge/gtkb-bridge-index-atomic-write-guard` (WI-4481, VERIFIED)** — the *other half* of the concurrent-INDEX problem: atomic `bridge/INDEX.md` writes. Now resolved. WI-4464 addresses the **commit-index contamination** side, which is distinct from INDEX-file write atomicity; this slice does NOT touch INDEX write atomicity (already fixed). Cited to disambiguate and avoid re-litigating a settled approach.
- **`.claude/rules/bridge-essential.md`** "Scoped commits only" invariant — the standing protocol rule the detector operationalizes.
- _Live semantic deliberation search was not run during authoring: `gt deliberations search` carries the residual WI-4453 first-embed hang risk (WI-4453 fix is in-flight on the bridge). Prior-decision context was gathered from the forensic record, the batch-admission DELIB, the WI-4481 thread, and the bridge-essential rule instead._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement Slice A.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ approval (2026-06-13) admitting WI-4464 to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`; forbids formal-artifact mutation, deploy, force-push, credential lifecycle, broad bulk status mutation). Slice A stays strictly within that scope: it adds one new `scripts/` source file + one new test file, performs no config/hook/INDEX/KB/formal-artifact mutation, and changes no bridge authority.
- **Scope note (informational, not a decision request):** the commit-time *wiring* of this detector requires a hook/config-registration mutation class outside the batch-1 PAUTH; it is deferred to a follow-on slice. No owner action is required for Slice A to proceed.

## Design (Slice A)

New file `scripts/check_commit_pathspec_safety.py` — **stdlib only**, no third-party imports:

1. **`classify_staged(names: list[str]) -> dict`** — pure function (no git, no I/O). Partitions staged path names into `bridge_queue` (matches `bridge/INDEX.md` or a top-level `bridge/<name>.md`) and `other`. Returns `{"mixed": bool, "bridge_queue": [...], "other": [...]}` where `mixed = bool(bridge_queue) and bool(other)`. The bridge-queue matcher is conservative (canonical queue surface only: `bridge/INDEX.md` + top-level `bridge/*.md`); nested non-`.md` or non-`bridge/` paths are `other`. The match rule is a documented module constant so the deferred wiring + any future tuning are explicit.
2. **`_staged_names() -> list[str]`** — runs `git diff --cached --name-only --diff-filter=ACM` (read-only subprocess) and returns the staged path list; isolated in its own function so tests bypass git entirely. Fail-open: any subprocess error / non-repo → returns `[]`.
3. **`main(argv) -> int`** CLI:
   - **Advisory mode (default)**: read staged names → `classify_staged`. If `mixed`, print a prominent multi-line warning to **stderr** — names the bridge-queue files and the other files, explains the auto-staging hazard, recommends committing with an explicit `-- <pathspec>`, and points to `memory/recovery-2026-06-11-fab20-commit-collision.md`. **Exit 0** (never blocks a commit).
   - **`--strict`**: identical detection, but **exit 3** (distinct non-zero) on `mixed`; exit 0 otherwise. For opt-in enforcement / future promotion / CI use.
   - **`--json`**: print `{"mixed":..., "bridge_queue":[...], "other":[...]}` to stdout; exit 0.
   - No staged files / no git repo → exit 0 silently (fail-open; never breaks a commit).

The script is invocation-ready for the deferred wiring step (`python scripts/check_commit_pathspec_safety.py --staged` appended to the existing `.githooks/pre-commit` gate chain — which already chains `scripts/check_*.py --staged` gates — or a PreToolUse commit-guard). **Slice A performs NO wiring**: it is a self-contained, independently runnable + tested mechanism.

No change to any commit path, hook, config, `bridge/INDEX.md`, schema, or KB.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_check_commit_pathspec_safety.py`) | Method |
|---|---|---|
| Contamination signature detected (WI-4464; bridge-essential "Scoped commits only") | `test_mixed_bridge_and_source_is_flagged` | `classify_staged(["bridge/INDEX.md","scripts/x.py"])` → `mixed=True`, correct partition |
| No false positive on a legit bridge-only commit (GOV-FILE-BRIDGE-AUTHORITY-001) | `test_bridge_only_not_mixed` | `classify_staged(["bridge/INDEX.md","bridge/foo-001.md"])` → `mixed=False` |
| No false positive on a source-only commit | `test_source_only_not_mixed` | `classify_staged(["scripts/x.py","a/b.py"])` → `mixed=False` |
| Empty staged set not flagged | `test_empty_not_mixed` | `classify_staged([])` → `mixed=False` |
| Advisory mode never blocks a commit (fail-open; protects active swarm + sweep-commit) | `test_advisory_exit_zero_on_mixed` | `main(["--staged"])` with monkeypatched `_staged_names` → exit 0, warning on stderr |
| Strict mode blocks on contamination | `test_strict_exit_nonzero_on_mixed` | `main(["--staged","--strict"])` mixed → exit 3 |
| Strict mode passes a clean staged set | `test_strict_exit_zero_on_clean` | `main(["--staged","--strict"])` bridge-only → exit 0 |
| JSON output shape | `test_json_output` | `main(["--staged","--json"])` → parseable JSON with `mixed`/`bridge_queue`/`other` |
| No-git / no-staged fail-open | `test_no_staged_fail_open` | `_staged_names` returns `[]` → exit 0, no warning |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_check_commit_pathspec_safety.py -q --tb=short`.

## Risk / Rollback

- **Risk: very low.** Slice A adds ONE standalone stdlib script + ONE test file. It is **not wired into any commit path**, so it cannot block, slow, or alter any commit — zero behavior change to the active multi-session swarm or to `gtkb-sweep-commit`. It performs no git mutation (read-only `git diff --cached`), no `bridge/INDEX.md` write, no KB mutation, no formal-artifact change.
- **Scope risk surfaced:** the eventual commit-time wiring touches a hook/config mutation class beyond the batch-1 PAUTH; deferring it keeps Slice A unambiguously in-scope. The one judgment call for review is whether the tested detection mechanism (without wiring) is acceptable as a slice; the proposal's position is yes — deliver the reusable, verified mechanism now; wire it under a follow-on authorization.
- **Rollback:** delete the two new files. No migration, no schema, no config, no INDEX, no KB.

## Recommended Commit Type

`feat:` — net-new capability (a new detection script + its test suite), not a repair of existing broken behavior. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`), net-new modules / scripts / capabilities are `feat:`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
