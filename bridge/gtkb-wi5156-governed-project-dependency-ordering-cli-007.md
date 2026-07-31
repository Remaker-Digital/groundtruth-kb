NO-GO
::init gtkb pb
::open test

# NO-GO — gtkb-wi5156-governed-project-dependency-ordering-cli (implementation report, version 006)

bridge_kind: lo_verdict
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 007 (verdict on 006)
Verdict: NO-GO
Date: 2026-07-17 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 085fb816-dbeb-4426-9f91-a840c63e3069
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent doing Loyal Opposition bulk bridge processing, round 2

reviewed_report: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-006.md
verdict_chain: 001 (proposal, 8 targets) to 002 (GO on 001) to 003 (REVISED, 15 targets, two review claims expired without a verdict) to 004 (REVISED, delta re-presentation of the same 15 targets) to 005 (GO on 004) to 006 (implementation report, reviewed here) to 007 (this NO-GO verdict)

---

## Review Independence

This review runs in a fresh session context distinct from the report author's `author_session_context_id` (`019f6668-9974-7d72-a456-826f9a67e627`, Codex harness A). No shared session context with the proposal or report author.

## Preflight Checks (re-run against live state, operative file version 006)

### bridge_applicability_preflight.py

- packet_hash: `sha256:1cc871d7cc9894923c0ea4b64d8f6c71bcaa108269928cf969bc0a8a218c94b0`
- operative_file: `bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-006.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- exit code: `0`

### adr_dcl_clause_preflight.py

- Clauses evaluated: 5; must_apply: 4; may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- exit code: `0`

Both mandatory gates pass. This is not the basis for the NO-GO below.

## Independent Re-Verification (evidence, not trust)

All figures below were reproduced by this review session directly, not copied from the report.

| Check | Command | Report claim | Independently observed |
| --- | --- | --- | --- |
| Dependency suite | `pytest groundtruth-kb/tests/test_project_dependency_ordering.py -q` | 11 passed | 11 passed (confirmed) |
| Projects CLI suite | `pytest platform_tests/scripts/test_projects_cli.py -q` | 16 passed | 16 passed (confirmed) |
| Skill adapter suite | `pytest platform_tests/scripts/test_projects_skill_adapter.py -q` | 4 passed | 4 passed (confirmed) |
| Project artifacts suite | `pytest groundtruth-kb/tests/test_project_artifacts.py -q` (isolated) | 34 passed | 34 passed (confirmed) |
| Remove-item suite | `pytest groundtruth-kb/tests/test_projects_remove_item.py -q` (isolated) | 17 passed | 17 passed (confirmed) |
| Project authorization suite | `pytest platform_tests/scripts/test_project_authorization.py -q` (isolated) | 10 passed | 10 passed (confirmed) |
| Evaluator | `python scripts/check_project_dependency_ordering.py --json` | PASS, PROJECT-DEP-A1..A5, evaluator hash `a98f527a...`, registry hash `4c8fa999...` | PASS, exactly PROJECT-DEP-A1 through A5, both hashes match exactly |
| Codex/Antigravity/API adapters | three `--check` invocations | PASS, 44 adapters current, each surface | PASS, 44 adapters current, each surface (confirmed) |
| ruff check / format --check | six Python targets | clean | clean (confirmed) |
| Production stale-edge cross-reference | `gt projects dependencies validate --json` (read-only, live `groundtruth.db`) | exactly one pre-existing stale edge, `PDEP-PROJECT-GTKB-ROLE-ENHANCEMENT-...`, owned by WI-5482 | Reproduced verbatim; `WI-5482` exists in MemBase ("Retire stale role-enhancement dependency that invalidates the governed project graph"); `bridge/gtkb-wi5482-stale-project-dependency-reconciliation-001.md` exists on disk |
| WI-5156 / PAUTH | `KnowledgeDB.get_work_item` / `get_project_authorization` | project-scoped, active, DCL included | Confirmed: PAUTH status=active, `expires_at=null`, `DCL-PROJECT-DEPENDENCY-ORDERING-001` is in `included_spec_ids_parsed`, no per-WI exclusion |
| Cited deliberations | `search_deliberations` / direct lookup | 4 DELIB IDs cited as authorization/approval basis | All 4 found: `DELIB-202666274`, `DELIB-20260710-GTKB-MODERNIZATION-PROJECT-DEPENDENCY-ORDERING-DCL-APPROVAL`, `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-FORMAL-LANGUAGE-DRAFT`, `DELIB-20260715-DISPATCHER-BLACKBOX-SPEC-FOUNDATION-FIRST`; no conflicting prior deliberation found on the same topic |
| Source diff spot-check | `git diff` on `lifecycle.py` | atomic transaction, cycle detection, canonical field names, readiness never grants authority | Confirmed: `BEGIN IMMEDIATE`/commit/rollback with in-transaction graph revalidation, DFS-based cycle detection over active edges, `dependent_project_id`/`prerequisite_project_id` canonical fields throughout, `"grants_implementation_authority": False` explicit on every readiness row |

The one apparent discrepancy (`test_projects_remove_item.py::test_cli_remove_item_invokes_service` failing when run in the same process as `test_project_artifacts.py` and `test_project_authorization.py`, per this review's own reproduction) is a pre-existing cross-file test-order/state-leakage issue, not a WI-5156 regression: the same failure and workaround are already documented in version 003's "Current Candidate Evidence," and the file passes cleanly (17/17) in isolation, matching the report's own isolated-process methodology and claimed count. Not a blocker.

The substantive dependency-lifecycle implementation is well-executed and everything above independently reproduces the report's claims. The blocking finding below is a commit-scope-safety defect discovered by independent hash re-verification, not a defect in the dependency-ordering logic itself.

## Blocking Finding: Exact Target Hashes Are Stale for 4 of 15 Files Due to Concurrent Cross-Thread Contamination of Shared Projection Files

### Observation

I recomputed SHA-256 for all fifteen files in the report's "Exact Target Hashes" section directly from the current working tree (`Get-FileHash -Algorithm SHA256`), rather than trusting the table. Eleven match exactly. Four do not:

| File | Report claimed (v006) | Currently on disk |
| --- | --- | --- |
| `.codex/skills/MANIFEST.json` | `eed3618e4fdf3f0aa9cad24cf0198c67b311e6c5724244a8d61ddf4974860491` | `15ea6b030eb4387ceecc818dc7773d7f4d7132ae698721ac20d833ef5f91a26a` |
| `.agent/skills/MANIFEST.json` | `d3932d5bc882c939fc1e540763ab5d27810ca82403051a103f8f20d591d05feb` | `6675555e21b5ba7d5e54a68026fb61ea365166dc68d4a6033d61ea3f6ea572de` |
| `.api-harness/skills/MANIFEST.json` | `fb25c0212ccc9d25e21fffd32be0e0edd7b80daf8fb17959811bff7207d12a26` | `ccc30cfa5d2af979a64a842fa71e4f5d8b39e0dc2e9255d493086e8f05b986c1` |
| `config/agent-control/harness-capability-registry.toml` | `ec4193603e28cdbfd201e2a6c1b0be2d72d1060a0baf5d05d0cec1b16ae0263d` | `1d538bc131902f45c4fa3363905a9fd04d5589c04abc4d0b35f3451b6bb9ca31` |

`git diff -- <each file>` shows why: each is a shared cross-harness projection manifest/registry containing one entry per skill. The current working tree has the WI-5156 `projects` entry correctly updated (source hash `b35a7e3c...` to `70d646b9...`, consistent across all four files and matching the canonical `.claude/skills/projects/SKILL.md` change), but the SAME files also carry live, uncommitted, unrelated entry changes from other active bridge threads:

- `lo-opportunity-radar` (`f6541de2...` to `d5f68022...`)
- `codex-report` / `loyal-opposition-report` (`3c46cefd...` to `527ddc84...`, plus a description-text change)
- `kb-session-wrap` (`eb2b6752...` to `78880c71...`)
- `loyal-opposition-hygiene-assessment` (`a77cd8c1...` to `a8386eb6...`)
- a brand-new entry for `gtkb-hygiene-reclaim` (present in `.agent/skills/MANIFEST.json` and `.api-harness/skills/MANIFEST.json` only)
- a brand-new entry for `managed-skill-adoption-review` (present in `.api-harness/skills/MANIFEST.json`)

None of these six are named in WI-5156's target_paths, Specification Links, or Files Changed. `git status --short` on the fifteen declared targets alone does not reveal this — every file legitimately shows as dirty because WI-5156 did change it. The contamination is only visible by reading the diff content, which is what the report's flat "Exact Target Hashes" and "No other dirty path is claimed by this implementation" language does not surface.

I also confirmed the three adapter `--check` invocations (`generate_codex_skill_adapters.py`, `generate_antigravity_skill_adapters.py`, `generate_api_skill_adapters.py`) all report `PASS (44 adapters current)` against this mixed state — the other threads' entries are internally self-consistent (their generated adapters already match their own canonical sources too), so this is not corruption or garbage data. It is fully-formed, legitimate, but unrelated concurrent work sharing the same four files.

### Deficiency Rationale

`.claude/skills/verify/helpers/write_verdict.py::finalize_verified_commit` stages each `--include` path via a disposable index built from HEAD, using whole-file `git add -f -- <path>` for any path not covered by an explicit `--hunk-patch` (see `full_stage_paths = [path for path in expected_paths if path not in hunk_patch_touched_paths]` at line ~1194). If VERIFIED is finalized right now against the report's declared fifteen-path `--include` set using the documented mechanical flow (whole-file include, no hunk patches), the resulting commit would stage the CURRENT on-disk content of all four shared files — capturing the six unrelated skill-entry changes above under WI-5156's commit message, `Files Changed` claim, and audit trail.

This is a concrete violation of `.claude/rules/bridge-essential.md` Invariants ("Scoped commits only. Bridge work commits should not bundle unrelated source changes.") and would misattribute provenance for six other bridge threads' work, independent of whether those threads have their own review in flight elsewhere. It would also leave those other threads unable to cleanly commit their own changes afterward without re-diffing against a HEAD that already contains their content under someone else's commit.

This is a governance/finalization-safety defect discovered by the mandatory independent hash re-verification, not a defect in the dependency-ordering implementation, which is otherwise fully corroborated above.

### Proposed Solution / Enhancement

Any one of the following resolves the finding; scope is limited to the finalization step, no source/test changes are implied:

1. **Re-verify immediately before finalization.** Re-capture "Exact Target Hashes" for the four shared files at the moment `--finalize-verified` is about to run, and only proceed if the reviewer re-diffs and confirms the ONLY delta versus HEAD in each of those four files is the `projects` entry (i.e., the sibling threads have landed their own commits in the interim and the shared files are clean again).
2. **Hunk-patch isolation (already supported by the helper).** Construct a unified diff containing only the `projects`-entry hunk for each of the four shared files (the exact hunks are visible in this review's `git diff` output above) and pass them via repeated `--hunk-patch` flags. `_apply_hunk_patch_to_index` fails closed (raises `VerifiedFinalizationError`, creates no commit) if a patch does not cleanly apply, so a malformed patch cannot silently corrupt a sibling thread's uncommitted work.
3. **Sequence after sibling threads.** Defer WI-5156 finalization until `lo-opportunity-radar`, `codex-report`/`loyal-opposition-report`, `kb-session-wrap`, `loyal-opposition-hygiene-assessment`, `gtkb-hygiene-reclaim`, and `managed-skill-adoption-review` (whichever are in-flight bridge threads) land their own commits, then re-run the eleven-file plus four-file hash check named above before requesting a fresh VERIFIED review.

### Option Rationale

I did not attempt hunk-patch construction myself in this review pass. The tooling fails closed on a bad patch, which de-risks the attempt, but correctly isolating a `projects`-only hunk inside a nested `[capabilities.*]` TOML block and two JSON manifests, across four files, in a single automated pass, is exactly the kind of git surgery this review is instructed to avoid attempting ad hoc. It is better performed by Prime Builder (who authored the exact hunk boundaries) or by a dedicated finalization pass, either of which can also simply wait a cycle for the shared files to settle. A NO-GO with the precise mismatched hashes and contaminating entries named above is the actionable, low-risk path; a guessed hunk-patch that misfires would either fail closed (wasted cycle) or, if I got the file/line accounting wrong in a way `git apply` still accepted, could bundle the wrong hunk anyway. I am not treating this as a defect in Prime Builder's engineering — the dependency-ordering implementation itself is corroborated end-to-end above — only as a finalization-timing hazard that must be closed before a scoped commit is safe.

## Non-Blocking Observations

- Version 004 (the proposal that received the GO at version 005) does not contain an `## Owner Decisions / Input` section, unlike versions 001 and 003. Per `.claude/rules/file-bridge-protocol.md` "Mandatory Owner Decisions / Input Section Gate," this section is required only when a proposal "depends on owner approval" / cites the AUQ-only rule; version 004 explicitly states "No new owner decision is required," so this is plausibly a legitimate exemption rather than a gap, and it is already GO'd, terminal history I am not reopening. Flagging only for completeness since the pattern (present in v001/v003, absent in v004) is otherwise unexplained in the thread.
- WI-5156's MemBase `stage` field is still `backlogged` and `resolution_status` is still `open` as of this review, despite an approved GO and a filed implementation report. This is consistent with the proposal's own `kb_mutation_in_scope: false` declaration (no live MemBase mutation in this slice) and is not something this NO-GO is conditioned on; noting it so a future VERIFIED pass or session wrap remembers to promote WI-5156 through the normal governed path.
- WI-5156's `origin` field is `defect`, while the report's own "Recommended Commit Type" is `feat:` (net-new CLI capability). `GOV-RELIABILITY-FAST-LANE-001` is not cited anywhere in this thread and no fast-lane path is claimed, so the stricter fast-lane origin/scope criteria do not apply here and this is not a blocker; noting the origin/commit-type tension only as a minor backlog-hygiene observation for whoever triages WI-5156's classification.

## Verdict

**NO-GO.** Both mandatory preflights pass, the dependency-ordering implementation, tests, evaluator, and cross-harness adapter generation are independently re-verified and match the report's claims, and the cited authorization/deliberation chain is real and active. However, 4 of the 15 "Exact Target Hashes" claimed in the implementation report no longer match the current working tree because the underlying files are shared cross-harness projection manifests/registry currently carrying live, unrelated, uncommitted changes from at least six other skills/bridge threads. Finalizing VERIFIED right now via the standard whole-file `--include` mechanism would bundle that unrelated work into WI-5156's commit, violating the bridge protocol's scoped-commit invariant. Please re-verify the four shared-file hashes immediately before requesting the next review (after the sibling threads land, or via `--hunk-patch` isolation), and resubmit. No changes to the dependency-ordering source, tests, or evaluator are requested.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
