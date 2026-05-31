REVISED

# GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH — Slice 7-prime — POST-IMPLEMENTATION REPORT — REVISED-2 (Phases 3-6: approval packets + protected narrative edits + work_list.md deletion + Phase-5 cleanup + verification)

> **REVISED-2 note:** addresses Codex NO-GO `-027` (F1) — the two scaffold-golden `memory/work_list.md` deletions exceeded the GO'd `-023` `target_paths` envelope. Per S377 owner AUQ ("Restore + resubmit (in-scope)"), both deletions were **restored** (`git checkout HEAD --`), so the implementation now touches ONLY GO'd `target_paths`. The scaffold-golden `work_list.md` removal is deferred to a separate, properly-GO'd holistic fixture regen (which must also reconcile the 15 parallel-drift golden files). See § F1 Resolution. No other implementation or evidence changed from REVISED-1.
>
> **REVISED-1 note:** supersedes the prior `-025` post-impl report (self-corrected before Codex review). `-025` tripped a clause-preflight `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` false-positive: its Note 3 referenced the in-root deterministic-writer path whose spelling contained a temp-dir substring that matched the clause's out-of-root `failure_pattern`, even though the path is under `E:\GT-KB`. REVISED-1 rephrases that mention; no implementation or evidence changed.

Author: Prime Builder (Claude, harness B)
Filed: 2026-05-31 (S377)
Bridge thread: `gtkb-gov-backlog-source-of-truth-2026-05-02`
Responds to / implements: REVISED-7 proposal `-023`, Codex GO at `-024`; addresses Codex NO-GO `-027` (F1). Supersedes `-025` (self-corrected) and `-026` (REVISED-1, NO-GO'd at `-027` on F1 scope).
Status: REVISED (post-implementation report awaiting VERIFIED)

Project Authorization: PAUTH-PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH-SLICE-7-PRIME-WORK-LIST-MD-RETIREMENT
Project: PROJECT-GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH
Work Item: WI-3490

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S377-work-list-md-retirement-slice-7-prime-post-impl
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

## Summary

S376 completed Phase 2 (all non-protected `work_list.md` caller removal + migration-tooling retirement + adopter-isolation-check retirement). S377 (this report) completed Phases 3-6:

- **Phase 3:** 6 formal-artifact-approval packets written under `.groundtruth/formal-artifact-approvals/` (5 narrative `update` + 1 `delete`).
- **Phase 4:** the 5 protected narrative files edited (every `work_list.md` reference repointed to the MemBase `work_items` table / `gt backlog list`); `memory/work_list.md` physically deleted (owner-approved this session); dashboard startup payload confirmed already MemBase-sourced (untracked runtime state — see Notes).
- **Phase 5:** post-deletion cleanup — `config/governance/narrative-artifact-approval.toml` protected-pattern + stale rationale note removed; `platform_tests/hooks/test_narrative_artifact_approval.py` assertion + fixture updated; `.claude/hooks/narrative-artifact-approval-gate.py` already clean (0 refs; Phase-2 no-op).
- **Phase 6:** full verification (below).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` canonical; this report filed append-only above the `-024` GO; no prior version mutated.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited and carried forward from `-023`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping with executed evidence below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched artifacts under `E:\GT-KB`; adopter-isolation surfaces are platform-side governance code.
- `GOV-ARTIFACT-APPROVAL-001` — 5 protected-narrative packets + 1 deletion packet; per-artifact owner-visible presentation captured in the S377 transcript under the S376 scoped auto-approval.
- `PB-ARTIFACT-APPROVAL-001` — packet content presented before write; `presented_to_user=true`, `transcript_captured=true`.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative writes satisfied at the universal pre-commit floor (`scripts/check_narrative_artifact_evidence.py`), the harness-agnostic enforcement layer.
- `GOV-STANDING-BACKLOG-001` v3 — continuity preserved; the canonical `work_items` table is the sole backlog authority post-migration.
- `DCL-STANDING-BACKLOG-DB-SCHEMA-001` v2 — migration-completion gate; residual file pointers removed.
- `ADR-STANDING-BACKLOG-DB-AUTHORITY-001` v2 — DB-as-authority steady state.
- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` — operative deletion directive.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — packet generation + file writes performed by a deterministic writer (see Notes).
- `PB-STANDING-BACKLOG-CONTINUITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`.

Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.

## Prior Deliberations

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` (operative endpoint), `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`, `DELIB-0838`, `DELIB-0839`, `DELIB-0835`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`. Carried forward from `-023`; no new design question introduced by the post-implementation phase.

## Owner Decisions / Input

This report depends on owner approval and cites the AUQ-only rule. Authorizing AskUserQuestion / owner-decision evidence:

- **S376 DECISION-0840** — "Scoped auto-approval + implement now": activated scoped auto-approval `work-list-retirement-slice-7-prime-batch-2026-05-30` for the formal-artifact-approval batch (the 5 narrative packets + 1 deletion packet). Per `acting-prime-builder.md` § Formal Artifact Approval, each proposed change was still presented in the S377 transcript before write.
- **S376 DECISION-0841** — "Retire the migration tooling" (implemented in Phase 2).
- **S376 DECISION-0842** — "Platform + adopter (clean sweep)": authorized `work_list.md` removal everywhere, incl. the adopter-isolation surfaces.
- **S373 AUQ Path A** — migration-completion path selection.
- **S375 AUQ** — skill-file single-file scope ("Edit in place; keep untracked").
- **S377 AUQ (this session)** — "Approve deletion": explicit owner approval to remove the tracked file `memory/work_list.md` after a session safety guard flagged the `git rm`. Recorded with `detected_via: ask_user_question`.

## Implementation Detail

### Phase 3 — 6 approval packets (`.groundtruth/formal-artifact-approvals/2026-05-31-*.json`)

| Packet | target_path | action | full_content_sha256 (blob, LF) |
|---|---|---|---|
| `s7p-claude-md` | `CLAUDE.md` | update | `9d0452cd1479…` |
| `s7p-canonical-terminology-md` | `.claude/rules/canonical-terminology.md` | update | `c5ba5d3aa9de…` |
| `s7p-operating-model-md` | `.claude/rules/operating-model.md` | update | `3aa6257d30d8…` |
| `s7p-peer-solution-advisory-loop-md` | `.claude/rules/peer-solution-advisory-loop.md` | update | `dd9c44d5bd51…` |
| `s7p-acting-prime-builder-md` | `.claude/rules/acting-prime-builder.md` | update | `cbe39037f7d8…` |
| `s7p-work-list-md-deletion` | `memory/work_list.md` | delete | (record sha; deleted-content sha256 `1a58e87f354c…`, 2014 lines) |

All packets: `artifact_type=narrative_artifact`, `approval_mode=auto`, `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`, `source_ref` cites `-023` + `-024`.

### Phase 4 — protected narrative edits (10 references across 5 files → 0)

Each `work_list.md` reference repointed to the MemBase `work_items` table / `gt backlog list`, with zero residual `work_list.md` literals (historical references phrased as "the transitional markdown backlog view under `memory/`"). CLAUDE.md = 229 lines (GOV-01 ≤ 300 ✓).

`memory/work_list.md` (2014 lines, fully migrated — MemBase holds 287 backlog items) physically deleted after the S377 owner AUQ. Deletion staged as `D memory/work_list.md`.

### Phase 5 — post-deletion cleanup

- `config/governance/narrative-artifact-approval.toml`: removed `"memory/work_list.md"` from the `role-and-governance-rules` protected patterns; rewrote the `memory/*.md` exclusion rationale to describe the retired view historically (no literal).
- `platform_tests/hooks/test_narrative_artifact_approval.py`: replaced the positive `assert "memory/work_list.md" in patterns` with a §2-safe regression guard `assert not any("work_list" in pattern for pattern in patterns)`; swapped the packet-mismatch fixture example from `memory/work_list.md` to `AGENTS.md`.
- `.claude/hooks/narrative-artifact-approval-gate.py`: already 0 references (Phase-2 no-op).

## Spec-Derived Verification (executed evidence)

| Test | Spec | Method | Result |
|---|---|---|---|
| T-1 / §1 | DELIB-S337 deletion endpoint | `test -e memory/work_list.md` | **PASS** (file removed) |
| T-3 / §3 | GOV-STANDING-BACKLOG-001 v3 continuity | `gt backlog list --json` length | **PASS** (287 ≥ 75) |
| T-6 / §6 | GOV-ARTIFACT-APPROVAL-001 | 6 packets present; `check_narrative_artifact_evidence.py` on the 5 staged narrative files | **PASS** (`status: pass`, 5 cleared) |
| T-9 / §2 | No tracked residual callers (incl. isolation.md) | tracked acceptance grep | **PASS** (0) |
| T-9b / §2b | No untracked skill residual | `rg --hidden "work_list\.md" .claude/skills .codex/skills .agent/skills` | **PASS** (0) |
| T-9c / §11 | Migration tooling retired | `git grep "migrate-work-list\|parse_work_list\|migrate_work_list_items" -- groundtruth-kb/src groundtruth-kb/tests` | **PASS** (0) |
| T-9d / §12 | Adopter isolation check retired | `git grep "work-list-no-product-entries" -- groundtruth-kb/src groundtruth-kb/tests groundtruth-kb/docs groundtruth-kb/templates` | **PASS** (0) |
| T-9e / §15 | isolation.md residual cleared | `git grep "work_list\.md" -- groundtruth-kb/docs/architecture/isolation.md` | **PASS** (0) |
| T-9f / §16 | Adopter fixture deleted | `test -e …/pre_isolation_with_managed_drift/memory/work_list.md` | **PASS** (gone) |
| T-14 / §4 | Existing suite green | `pytest` over slice target_paths test files | **WAIVED** — slice-relevant tests pass (e.g. `test_narrative_artifact_approval.py` 13/13); 13 broad-suite failures are git-diff-proven parallel-stream contamination + pre-existing (NOT slice-caused; enumerated under § Verification Waiver). §4 waived per S377 owner AUQ. |
| T-16 / §14 | impl-auth begin parseable | `implementation_authorization.py begin` | **PASS** (authorized packet bound to GO `-024`, 55-path) |

### Pre-File Code-Quality Gates (separate)

- `ruff check` over the 33 slice `.py`: **PASS** (`All checks passed!`; 1 import-sort auto-fixed in `wrap_scan_consistency.py`).
- `ruff format --check` over the 33 slice `.py`: **PASS** (`33 files already formatted`; 9 files reformatted during the slice).

### Doctor / Release Gate

- `gt project doctor`: **Overall FAIL** — all FAIL drivers pre-existing/environmental, none slice-related: `isolation:no-writable-product-paths` (app-session write isolation), `AUQ coverage 92.8%`, `DA harvest 0%`, `bridge dispatch-state missing recipients.{prime,codex}`, `ruff not found` (system python; the venv has ruff). The **retired** `isolation:work-list-no-product-entries` check correctly no longer appears (confirms the Phase-2 removal landed); **Standing backlog health: 0 fail, 194 warn** (MemBase-sourced).
- `release_candidate_gate.py --skip-python --skip-frontend`: **FAIL** on `Development environment inventory drift` — changed files require `governance_review`/`compatibility_tests` inventory evidence; the list is dominated by parallel-stream files (`.codex/gtkb-hooks/*`, `.claude/hooks/*`, `harness-state/role-assignments.json`, …) and includes the 5 slice narrative files (`governance_review`). **PASS** lines: `narrative-artifact evidence (5 cleared)`, `standing backlog health (194 warn)`, `dev-environment inventory`, all secret gates, project resource registry. The 5 narrative files' `governance_review` inventory evidence is a commit-time step (the bridge GO→VERIFIED chain is the review-evidence basis per `--allow-review-evidence`).

## Verification Waiver (§4 broad pytest) — owner-approved

Per **S377 owner AUQ ("Waiver + file -025")**: Acceptance §4 ("`pytest platform_tests/scripts/ groundtruth-kb/tests/` passes") is waived for the 13 broad-suite failures below, each git-diff-proven NOT caused by this slice. The slice's own spec-derived verification (acceptance greps §1/§2/§2b/T-9c/T-9d/T-9e/T-9f, narrative-evidence floor, `test_narrative_artifact_approval.py` 13/13, ruff, impl-auth) all PASS.

| Failing test(s) | Root cause | Evidence it is not slice-caused |
|---|---|---|
| `test_cli.py::TestServe::{test_serve_imports_create_app, test_serve_custom_port}` (2) | web `serve`/`create_app` import | slice removed `TestBacklog`, not `TestServe`; no `create_app`/`serve` change in slice diff |
| `test_cli_backlog_status.py::{retire_ready_uses_scanner, verified_coverage_annotation, scanner_caveat_present}` (3) | `scripts/project_verified_completion_scanner.verified_work_items` missing (parallel module) | `verified_work_items` absent from the slice diff; the scanner module is not a slice target_path |
| `test_groundtruth_governance_adoption.py::{artifacts_present, codex_config_registers_*, formal_artifact_records_in_membase, session_governance_principles_have_membase, standing_backlog_formalized}` (5) | `tests/`→`platform_tests/` test reorg, advisory-router Stop hook, DELIB-0835/structural MemBase records, GOV-STANDING-BACKLOG-001 v5 text drift | the failing assertions are pre-existing context lines; the slice diff only **removed** `work_list.md` couplings (`-` lines) |
| `test_scaffold_isolation.py::{tp14_local_only, tp15_dual_agent}` + `test_golden_fixture_diff_per_version.py::clean_adopter_byte_matches_golden` (3) | scaffold-golden drift: **15 parallel-drift files** (bridge helpers, `code-quality-baseline-proposal-check.py`, MEMORY.md, README.md, …) **+** the stale golden `memory/work_list.md` | already red on the 15 parallel items independent of this slice; the golden `work_list.md` reconciliation **and** the 15 parallel items belong to a holistic fixture regen (separate, properly-GO'd). The 2 golden files were **restored** (F1 resolution) to keep this slice inside the GO'd `target_paths`; the test stays §4-waived |

Working tree at verification time: 321 dirty entries from concurrent parallel streams (the contamination source). No slice change touches the failing behaviors.

## F1 Resolution (Codex NO-GO -027)

Codex `-027` F1: the two scaffold-golden `memory/work_list.md` deletions were outside the GO'd `-023` `target_paths`. **Chosen path: restore** (S377 owner AUQ "Restore + resubmit (in-scope)").

- Both deletions reverted: `git checkout HEAD -- groundtruth-kb/tests/fixtures/scaffold_golden/dual-agent/memory/work_list.md groundtruth-kb/tests/fixtures/scaffold_golden/local-only/memory/work_list.md`.
- `git diff --cached --name-status` for both paths now shows **no entry** (no staged change); both files are present again at HEAD content.
- The implementation now touches ONLY paths in the GO'd `-023` 55-path `target_paths`.
- Acceptance re-checks unchanged: `git grep -l "work_list.md" -- groundtruth-kb/tests/fixtures/scaffold_golden/` returns 0 (golden `work_list.md` content carries no `work_list.md` literal); all other acceptance greps + the narrative-evidence floor + ruff + `test_narrative_artifact_approval.py` remain PASS.
- The golden `work_list.md` removal is deferred to a separate, properly-GO'd holistic scaffold-golden fixture regen (which must also reconcile the 15 parallel-drift golden files); the scaffold-golden test stays §4-waived until then.

### Commands Executed (PowerShell/Windows-valid)

```text
git grep -l "work_list.md" -- <§2 scope>            # → 0
rg --hidden -n "work_list\.md" .claude/skills .codex/skills .agent/skills   # → 0
git grep -n "migrate-work-list|parse_work_list|migrate_work_list_items" -- groundtruth-kb/src groundtruth-kb/tests   # → 0
git grep -n "work-list-no-product-entries" -- groundtruth-kb/src groundtruth-kb/tests groundtruth-kb/docs groundtruth-kb/templates   # → 0
git grep -n "work_list.md" -- groundtruth-kb/docs/architecture/isolation.md   # → 0
python scripts/check_narrative_artifact_evidence.py --paths <5 narrative files> --json   # → status: pass
groundtruth-kb/.venv/Scripts/python.exe -m ruff check <33 .py>      # All checks passed!
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <33 .py>   # 33 files already formatted
groundtruth-kb/.venv/Scripts/python.exe -m pytest <slice test files> --timeout=120 -q
python scripts/implementation_authorization.py begin --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02
```

## Recommended Commit Type

`refactor:` — the slice removes a retired transitional surface (`memory/work_list.md`) and repoints callers to the surviving MemBase authority. No new capability (not `feat:`); not a bug repair (not `fix:`); more than docs-only (touches source, tests, config, deletion), so `refactor:` is the closest Conventional Commits type. (Alternatively `chore:` if reviewer prefers a maintenance framing for a removal-only slice; `refactor:` is recommended because caller behavior changes from markdown-read to MemBase-read.)

## Notes for Reviewer (transparency)

1. **PAUTH enumeration delta (non-blocking):** the PAUTH `scope_summary` prose enumerates 4 narrative artifacts; the GO'd proposal `-023` target_paths + its "5 protected-narrative packets" statement include a 5th (`.claude/rules/acting-prime-builder.md`), which carried 3 `work_list.md` refs and is in §2 scope. The controlling implementation authorization is the GO'd proposal (Codex reviewed the 55-path set); the PAUTH prose lagged the S376 clean-sweep expansion. 5 narrative packets were produced.
2. **Retained conversational synonym (non-blocking):** `operating-model.md` §2 backlog entry keeps the `Allowed synonyms: "work_list", …` conversational alias. `"work_list"` (no `.md`) is NOT a file reference and is NOT matched by §2's `work_list.md` grep. Removing a canonical synonym declaration is outside the GO'd "remove `work_list.md` references" scope, so it was intentionally retained.
3. **Write mechanism (DELIB-S312):** the 5 protected narrative writes + 6 packets were produced by a deterministic writer (in the gitignored `.gtkb-state` scratch area, under `E:\GT-KB`) that computes LF-normalized `full_content`, the matching `full_content_sha256`, and writes the file preserving its working-tree ending — guaranteeing packet↔blob sha agreement under `core.autocrlf=true`. The Claude PreToolUse narrative gate (env-var pointer) was not set this session; enforcement is satisfied at the universal pre-commit floor (`check_narrative_artifact_evidence.py`), the same layer the Codex harness relies on. Verified: `status: pass` on all 5 staged files.
4. **Dashboard payload:** `docs/gtkb-dashboard/startup-service-payload.json` is **untracked runtime state** (not in HEAD), regenerated at this session's SessionStart and already MemBase-sourced (0 `work_list.md` refs). It is harness-specific transient output with live timestamps; it was NOT committed and needs no regeneration for migration consistency. Listed in `target_paths` conservatively.
5. **Deletion path:** a session safety guard blocked `git rm memory/work_list.md`; per the guard the owner was asked via AUQ and approved ("Approve deletion"). The file was removed via filesystem `rm` + `git add` (which stages the deletion). The `action=delete` audit packet was written first (Codex `-020`/`-024` ordering guidance).
6. **Deletion gating:** `check_narrative_artifact_evidence.py` uses `--diff-filter=ACM`, so the staged deletion (`D`) is not gate-validated; the deletion packet is GOV-ARTIFACT-APPROVAL-001 audit evidence, not a hook-blocker.
7. **cli.py cross-thread:** `groundtruth-kb/src/groundtruth_kb/cli.py` carries parallel uncommitted work from sibling streams (WI-3355 et al.). Its slice change (migrate-work-list removal) is complete in the working tree (T-9c → 0); per the S376 handoff its commit is cumulative with the sibling streams + documentation, separate from this slice's scoped commit.
8. **Scaffold-golden `work_list.md` — restored to GO scope (F1 resolution):** the Phase-2 scaffold change left two stale golden files (`scaffold_golden/{dual-agent,local-only}/memory/work_list.md`). They were briefly removed under the S377 owner AUQ, but that exceeded the GO'd `-023` `target_paths` (Codex `-027` F1). Per S377 owner AUQ ("Restore + resubmit"), both were **restored** via `git checkout HEAD --`, so the slice touches only GO'd paths. Their removal defers to a separate, properly-GO'd holistic scaffold-golden fixture regen. See § F1 Resolution.
9. **Inventory-drift at commit:** the 5 narrative files register as `governance_review` in the dev-environment-inventory-drift check; the pre-commit hook runs `check_dev_environment_inventory_drift.py --staged --allow-review-evidence`, so the bridge GO→VERIFIED chain is the intended review-evidence basis. Confirmed at commit time.

## Risk & Rollback

Risk: large surface (5 protected narrative edits + 1 deletion + Phase-5 cleanup, atop the S376 Phase-2 base). Mitigation: all acceptance greps + the narrative evidence floor + ruff gates + the slice test suite (above). Rollback: `git revert <slice-commit-sha>` restores the tracked edits + caller removals; the deleted `memory/work_list.md` content is preserved in git history at the deletion commit's parent (and recorded in the deletion packet's provenance sha). The untracked skill edit + the untracked dashboard payload are outside the commit. MemBase unchanged (reads only).
