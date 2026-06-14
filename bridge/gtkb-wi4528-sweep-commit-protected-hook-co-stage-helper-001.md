NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4528-sweep-commit-protected-hook-co-stage-helper
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4528
target_paths: ["scripts/sweep_commit_helpers.py", "platform_tests/scripts/test_sweep_commit_helpers.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

# WI-4528: Sweep-commit helper that groups protected hook-config edits with their bridge review evidence

## Summary

WI-4528 (P3, `tooling`, origin=improvement): the inventory-drift gate (`scripts/check_dev_environment_inventory_drift.py`, run by `.githooks/pre-commit --staged --allow-review-evidence`) only passes a protected hook-config change such as `.codex/hooks.json` when a `bridge/*.md` (or `bridge/INDEX.md`) is CO-STAGED in the same commit as `review_evidence_present` (`config/governance/protected-artifact-inventory-drift.toml` declares `accept_with_inventory_baseline_update = false` and lists `required_evidence` = hook-parity test + compatibility tests for the protected-hook entry covering `.claude/hooks/**`, `.codex/hooks.json`, `.githooks/**` — lines 71-74). On 2026-06-13 the sweep-commit committed the WI-3446 grilling-gate bridge artifacts separately/first, leaving the dependent `.codex/hooks.json` Stop-hook registration with no co-stageable bridge evidence; the manual scoped commit of `hooks.json` was blocked and had to be split (Claude settings.json + lint script + tests committed at `41727a5ec`; Codex hooks.json deferred).

**Cycle-13 triage (this session) confirms WI-4528 is genuinely OPEN, AND the owner's cycle-13 AskUserQuestion decision is "Seed both as scripts/ helpers"** — file the deterministic grouping logic as a new `scripts/sweep_commit_helpers.py` module in pure source+test PAUTH scope, then a separate follow-on slice (with the appropriate skill-doc authorization) wires the `gtkb-sweep-commit` skill to call it.

This proposal scopes the source helper only. The helper computes the correct co-staging plan: for each protected hook-config path in the staged set, find the corresponding bridge review evidence (bridge file(s) that cite the hook change OR `bridge/INDEX.md` if it carries the relevant new status line) and group them into a single commit batch so the inventory-drift gate sees `review_evidence_present` on the same commit. The helper is callable from any orchestrator (the skill, an ad-hoc script, future automation) and is fully unit-testable on synthetic staged sets.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4528 is the backlog authority for this fix (P3 sweep-commit tooling-completeness improvement). *Note on `CLAUSE-VISIBILITY-BULK-OPS`:* this proposal is **single-WI scope** (one tracked work item, one new helper module + one test, no source-mutation outside that helper), not a bulk operation. The bulk-ops clause is triggered by the spec citation but is `not_applicable` here: no inventory artifact, no formal-artifact-approval packet, no Phase/Path-deferred decision marker, and no broad review packet are required — the standard implementation-proposal + LO-review path is the appropriate visibility surface.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4528; allows `source` + `test_addition`). The follow-on skill-doc slice will declare its own scope.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger). The helper INSPECTS bridge artifacts to compute the co-staging plan; it does NOT modify `bridge/INDEX.md`, any bridge file, or bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a 2026-06-13 incident regression that reproduces the splitting failure on a synthetic staged set.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked tooling addition that codifies a deterministic procedure currently emergent in the skill text; the helper is the durable artifact.

## Requirement Sufficiency

Existing requirements sufficient. The defect is documented (WI-4528 + the 2026-06-13 incident at `41727a5ec`), cycle-13 triage confirmed it open and verified the protected-hook entry still requires co-staged bridge evidence (`protected-artifact-inventory-drift.toml:71-74`), the bounded PAUTH authorizes the `source` + `test_addition` work, and the owner's cycle-13 AUQ chose the scripts/-helper scope. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4528 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Cycle-13 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Seed both as scripts/ helpers" over "defer both" and "seed only WI-4528", explicitly authorizing this slice (and the WI-4530 install-shim sibling) as a scripts/ helper in pure source+test PAUTH scope; the skill-doc wiring is a deferred follow-on slice.
- **`scripts/check_dev_environment_inventory_drift.py`** — the gate this helper feeds compliant commits to. The helper's success criterion = its grouping plan results in the gate accepting the commit.
- **`config/governance/protected-artifact-inventory-drift.toml`** — the authoritative protected-paths + `required_evidence` source. The helper reads this declaratively rather than hardcoding the path set.
- _Live semantic deliberation search was not run during authoring (the WI-4519 always-on-LIKE-merge fix this session is in-flight; per the standing caution prior-decision context was gathered from the live source + the inventory-drift gate source instead)._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4528 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-13 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Seed both as scripts/ helpers"**, explicitly authorizing this scripts/ slice and the WI-4530 install-shim slice in pure source+test PAUTH scope; skill-doc and install-process follow-on slices will declare their own authorization.

## Design

New module `scripts/sweep_commit_helpers.py` — pure-Python, stdlib + project-local TOML reader (the same `tomllib` already used elsewhere). Public API:

1. **`load_protected_path_globs(project_root) -> list[str]`** — reads `config/governance/protected-artifact-inventory-drift.toml`, returns the union of all `protected_paths` globs from entries with `accept_with_inventory_baseline_update = false` (i.e. the paths that require co-staged bridge evidence). Reads declaratively so the helper inherits future protected-path additions.
2. **`is_protected_path(path, globs)` -> `bool`** — matches a single relative path against the glob set (using `fnmatch` for cross-platform shell-style matching).
3. **`partition_staged(paths, protected_globs)` -> `dict`**: returns `{"protected": [...], "bridge": [...], "other": [...]}`, where `bridge` includes `bridge/INDEX.md` and any `bridge/*.md` (the candidate review-evidence files). Pure, no I/O.
4. **`bridge_files_citing(staged_protected, all_bridge_files, project_root) -> dict[str, list[str]]`** — for each protected path, returns the list of bridge files (within the staged set) whose body cites the protected path (path-token match or filename mention). When `bridge/INDEX.md` is in the staged set, it is included as evidence for every protected path (the universal gate-satisfier).
5. **`plan_commit_batches(staged, project_root) -> list[CommitBatch]`** — the headline function. Returns an ordered list of `CommitBatch` records (dataclass: `paths: list[str]`, `kind: str`, `rationale: str`), guaranteeing that:
   - every protected path is in a batch that ALSO contains at least one bridge-evidence file from `bridge_files_citing(...)` (`kind="protected-with-evidence"`);
   - bridge-only files that aren't tied to a specific protected path get their own `"bridge-only"` batch (preserving the existing sweep-commit pattern for the swarm's bridge filings);
   - other files (source, tests, docs that aren't protected) get their own `"unconstrained"` batch.
   The order is: protected-with-evidence first (so the gate's friendly path is exercised early), then bridge-only, then unconstrained.
6. **Fail-soft on missing TOML or unreadable bridge files**: returns a single `"unconstrained"` batch with all staged paths and a `WARN`-level rationale string, so the helper never blocks a commit if the inventory-drift config is missing.

No write path, no subprocess, no git invocation — pure planning. The orchestrator (the skill, in the follow-on slice) is responsible for executing `git commit -- <paths>` per batch.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `platform_tests/scripts/test_sweep_commit_helpers.py`) | Method |
|---|---|---|
| Protected hook-config + co-staged bridge evidence end up in the SAME commit batch (WI-4528 root) | `test_protected_hook_with_bridge_evidence_grouped` | staged = `[".codex/hooks.json", "bridge/foo-001.md"]` (bridge file body cites `.codex/hooks.json`) → `plan_commit_batches` returns ONE batch containing both, `kind="protected-with-evidence"` |
| 2026-06-13 incident regression: protected hook with NO co-stageable bridge → reports a clear missing-evidence diagnostic | `test_missing_evidence_diagnostic` | staged = `[".codex/hooks.json"]` only → `plan_commit_batches` returns a batch with rationale flagging "no bridge evidence co-staged; commit will be blocked by inventory-drift gate" |
| `bridge/INDEX.md` co-stage is the universal gate-satisfier | `test_index_md_is_universal_evidence` | staged = `[".codex/hooks.json", "bridge/INDEX.md"]` → grouped together as `kind="protected-with-evidence"` even when no bridge file body cites `.codex/hooks.json` |
| Bridge-only files batch separately when not tied to a protected path | `test_unrelated_bridge_files_separate_batch` | staged = `["bridge/foo-001.md", "scripts/x.py"]` (no protected paths) → bridge file in `"bridge-only"` batch, scripts/x.py in `"unconstrained"` batch |
| Multiple protected paths each pair with their evidence | `test_multiple_protected_paths_each_get_evidence` | staged = `[".codex/hooks.json", ".claude/hooks/foo.py", "bridge/a-001.md", "bridge/b-001.md"]` where a cites .codex and b cites .claude → two `"protected-with-evidence"` batches |
| Declarative protected-paths read from the inventory-drift TOML (no hardcoding) | `test_protected_globs_read_from_toml` | fixture TOML with a new protected glob → `load_protected_path_globs` returns the new glob; `is_protected_path` matches a path under it |
| Fail-soft when TOML missing (no commit-blocking exception) | `test_fail_soft_when_toml_missing` | project_root without the TOML → `plan_commit_batches` returns one `"unconstrained"` batch + WARN rationale, does NOT raise |
| Real-world replay of the 2026-06-13 commit `41727a5ec` set produces a single co-stageable plan | `test_real_world_2026_06_13_incident_replay` | staged = the actual file list from the incident → plan groups the hooks file with the relevant bridge evidence |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest platform_tests/scripts/test_sweep_commit_helpers.py -q --tb=short`.

## Risk / Rollback

- **Risk: very low.** Pure-Python planning module + its unit tests. No git invocation, no subprocess, no file mutation, no schema/KB change. The helper is invoked-but-not-yet-wired (the follow-on slice does the skill wiring), so it cannot affect existing sweep-commit behavior until the wiring slice lands.
- **Operational note:** the existing `gtkb-sweep-commit` skill text continues to work as today (no skill-doc change in THIS slice). Once the follow-on slice wires the skill to call `plan_commit_batches`, sweep-commits will automatically group correctly; until then, a human / future skill version can call the helper directly.
- **Rollback:** delete the two new files. No migration, no schema, no skill-doc change, no KB mutation.

## Recommended Commit Type

`feat:` — net-new capability (a new commit-planning helper module + its test suite), not a repair of existing broken behavior (the inventory-drift gate is correct as designed; this helper teaches sweep-commit to satisfy it deterministically). Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
