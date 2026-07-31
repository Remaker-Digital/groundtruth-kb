NO-GO
::init gtkb pb
::open test

# NO-GO — gtkb-wi5156-governed-project-dependency-ordering-cli (implementation report, version 008)

bridge_kind: lo_verdict
Document: gtkb-wi5156-governed-project-dependency-ordering-cli
Version: 009 (verdict on 008)
Verdict: NO-GO
Date: 2026-07-18 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 0c53d929-f89a-4689-8119-9bed4362d9d6
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent doing Loyal Opposition bulk bridge processing, round 3

reviewed_report: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md
verdict_chain: 001 (proposal, 8 targets) to 002 (GO on 001) to 003 (REVISED, 15 targets, two review claims expired without a verdict) to 004 (REVISED re-presentation of the same 15 targets) to 005 (GO on 004) to 006 (implementation report) to 007 (NO-GO: shared-projection-file commit-scope-safety finding) to 008 (REVISED implementation report responding to 007, reviewed here) to 009 (this NO-GO verdict)

---

## Review Independence

This review runs in a fresh session context distinct from the version 008 report author's author_session_context_id (019f6f8b-9fd7-7142-93a8-5696dca44d85, Codex harness A) and from the version 007 reviewer's author_session_context_id (085fb816-dbeb-4426-9f91-a840c63e3069, Claude harness B). No shared session context with the report author or the immediately preceding reviewer.

## Preflight Checks (re-run against live state, operative file version 008)

### bridge_applicability_preflight.py

- packet_hash: sha256:c2fae54a0ed1127b4734a087f9976fa7cc9a4398408a9018fcce251202baf7c6
- operative_file: bridge/gtkb-wi5156-governed-project-dependency-ordering-cli-008.md
- preflight_passed: true
- missing_required_specs:
  (empty)
- missing_advisory_specs:
  (empty)
- blocking_errors:
  (empty)
- exit code: 0

### adr_dcl_clause_preflight.py

- Clauses evaluated: 5; must_apply: 3; may_apply: 2
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- exit code: 0

Both mandatory gates pass. This is not the basis for the NO-GO below.

## Independent Re-Verification (evidence, not trust)

All figures below were reproduced by this review session directly against the current working tree, not copied from version 006 or version 008.

| Check | Command | Report claim | Independently observed |
| --- | --- | --- | --- |
| WI-5156 / PAUTH | KnowledgeDB.get_work_item / get_project_authorization | project-scoped, active, DCL included, no fast-lane claimed | Confirmed: WI-5156 origin=defect, stage=backlogged, resolution_status=open, priority=P0; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE status=active, expires_at=null, DCL-PROJECT-DEPENDENCY-ORDERING-001 present in included_spec_ids_parsed, no per-WI exclusion. GOV-RELIABILITY-FAST-LANE-001 is not cited anywhere in the thread and is not applicable here. |
| Cited deliberations | direct KnowledgeDB.get_deliberation lookups | 6 DELIB IDs cited across the thread (4 original plus 2 new precedent citations added in version 008: DELIB-202666105, DELIB-202666301) | All 6 found and resolve to real bridge-thread-sourced deliberation rows (WI-5132 version-gap finalization GO; WI-5266 clean-checkout NO-GO); no fabricated ID |
| Combined dependency/CLI/adapter suite | pytest groundtruth-kb/tests/test_project_dependency_ordering.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_projects_skill_adapter.py -q | 31 passed | 31 passed (confirmed) |
| Evaluator | python scripts/check_project_dependency_ordering.py --json | PASS, PROJECT-DEP-A1..A5, evaluator hash a98f527a..., registry hash 4c8fa999... | PASS, exactly PROJECT-DEP-A1 through A5, failed_assertion_ids empty, missing_assertion_ids empty, both hashes match exactly |
| ruff check / format --check | six Python targets | clean | clean, exit 0 both (confirmed) |
| Nonimpairment suites (isolated) | test_project_artifacts.py / test_projects_remove_item.py / test_project_authorization.py | 34 / 17 / 10 passed | 34 / 17 / 10 passed (confirmed) |
| Non-shared target hashes | Get-FileHash -Algorithm SHA256 on the 11 non-registry WI-5156 targets | matches version 006's Exact Target Hashes table | All 11 match byte-for-byte; source has not moved since version 006, consistent with version 008's claim that no source/test/adapter mutation occurred after the NO-GO |
| Source diff spot-check | git diff on lifecycle.py / db.py / cli.py | atomic BEGIN IMMEDIATE transactions with rollback, DFS cycle detection, self-edge/duplicate-active-edge/retired-endpoint/invalid-transition rejection, canonical dependent_project_id/prerequisite_project_id fields, readiness rows explicitly set grants_implementation_authority: False | Confirmed independently: BEGIN IMMEDIATE plus conn.rollback() at three call sites; self-dependency, cycle detected, duplicate-active-edge, retired-endpoint, invalid-transition all present as explicit rejection paths; canonical field names used throughout; grants_implementation_authority: False present on readiness construction |
| Production stale-edge cross-reference | gt projects dependencies validate --json | exits 1 on one pre-existing stale edge owned by WI-5482 | Reproduced; WI-5482 and bridge/gtkb-wi5482-stale-project-dependency-reconciliation-001.md remain the owning thread; not a WI-5156 defect |

The substantive dependency-lifecycle implementation is independently reconfirmed end to end and matches every claim in versions 006 and 008. Version 008 correctly states that no source, test, adapter, or registry content changed after the version 007 NO-GO. As in version 007, the blocking finding below is a commit-scope-safety defect in the finalization step, not a defect in the dependency-ordering implementation.

### Non-blocking: transient unrelated Codex adapter-check failure (not a WI-5156 issue)

Independently re-running `python scripts/generate_codex_skill_adapters.py --check` (matching the exact command from version 008's "Commands Executed For This Revision") currently exits 1 with "would update 2 file(s): .codex/skills/verify/helpers/gtkb-wi5287-verdict-draft-body.md, .codex/skills/verify/helpers/wi5415-draft-body.md" — a different result than the "PASS (44 adapters current)" both version 006 and version 008 report. I traced this: both files are absent from `.codex/skills/verify/helpers/` but present in the canonical source `.claude/skills/verify/helpers/` (dated 2026-07-17, today), and both are gitignored on both the canonical and generated side (`.gitignore` lines 620 and 675, `*-draft-body.md` patterns) — they are scratch working files apparently left behind by unrelated concurrent Loyal Opposition sessions drafting verdicts for WI-5287 and WI-5415 inside the shared `verify` skill's helpers directory, not WI-5156 output. Since both copies are gitignored, they cannot enter any commit and do not affect WI-5156 finalization safety. This is transient environmental churn in a heavily shared, multi-session workspace, not a WI-5156 regression, and is not a basis for this NO-GO. Worth a separate hygiene note: the Codex adapter generator's RESOURCE_EXCLUDED_PREFIXES only excludes filenames that literally start with "draft-"/"draft_", so a name like "gtkb-wi5287-verdict-draft-body.md" (which contains but does not start with "draft-") slips through and makes the adapter-parity check order-dependent on unrelated scratch files transiently present in a canonical skill's helpers directory.

## Blocking Finding: Version 008 Restates The NO-GO@007 Commit-Scope-Safety Defect But Does Not Resolve It; Contamination Is Independently Re-Confirmed Present And Worse Than Before

### Observation

Version 007 found that 4 of the 15 declared WI-5156 target files are shared cross-harness projection manifests/registry (`.codex/skills/MANIFEST.json`, `.agent/skills/MANIFEST.json`, `.api-harness/skills/MANIFEST.json`, `config/agent-control/harness-capability-registry.toml`) whose current working-tree content mixes WI-5156's legitimate `projects`-entry hash update together with unrelated, uncommitted entries from other in-flight skill bridge threads, and that finalizing VERIFIED via the standard whole-file `--include` mechanism would bundle that unrelated work into WI-5156's commit.

I independently re-ran `git diff` on all four files against the current working tree just now. The WI-5156 `projects` entry is present and correct in all four (source hash transitions from `b35a7e3cd6c2b4bd3976c15a2b0f78ec37b4663fbe2d5063047c77daf0c778c8` to `70d646b9b957ad00d39078328bd9aa8b069d503c85b0d40361352c82966f8dde`, consistent across all four files, matching the canonical `.claude/skills/projects/SKILL.md` change and the exact hunk description in version 008's "Resolution Of NO-GO@-007" section). But every one of the four files STILL also carries live, uncommitted, unrelated entries, and the unrelated set has grown since version 007's review, not shrunk:

- `.codex/skills/MANIFEST.json`: unrelated hash changes for `lo-opportunity-radar`, `loyal-opposition-report` (codex-report), `kb-session-wrap`, `loyal-opposition-hygiene-assessment` — the same four flagged in version 007, still present, unchanged.
- `.agent/skills/MANIFEST.json`: the same four unrelated hash changes, PLUS a brand-new `gtkb-hygiene-reclaim` capability entry that did not exist in version 007's review.
- `.api-harness/skills/MANIFEST.json`: the same four unrelated hash changes, PLUS new `gtkb-hygiene-reclaim` and `managed-skill-adoption-review` capability entries (also new since version 007) and an unrelated description-text edit on the `codex-report` entry.
- `config/agent-control/harness-capability-registry.toml`: the same four unrelated source_sha256 changes, each appearing twice (once under `[capabilities.codex]`, once under `[capabilities.antigravity]`), interleaved in the same TOML sections as the two WI-5156 `[capabilities.codex]` / `[capabilities.antigravity]` `projects` hunks.

I cross-checked bridge state for the three skills whose names I could resolve to bridge slugs: `gtkb-lo-opportunity-radar-skill` (latest status VERIFIED), `gtkb-wi5142-hygiene-reclaim-cli-skill-phase1` (latest status VERIFIED), and `gtkb-wi4841-managed-skill-adoption-review-scaffold` (latest status VERIFIED) are all already at terminal bridge status, yet their target files remain dirty in the working tree — their VERIFIED commits have evidently not yet landed, so their entries continue to sit uncommitted in the same shared files WI-5156 needs. I did not chase down a bridge slug for the `kb-session-wrap` or `codex-report` contamination; it is enough to establish that the condition version 007 identified is unresolved and has grown.

### Deficiency Rationale

`.claude/skills/verify/helpers/write_verdict.py::finalize_verified_commit` stages each `--include` path via whole-file `git add -f -- <path>` unless a `--hunk-patch` is supplied for that path. If VERIFIED were finalized right now against version 008's declared fifteen-path target set using a plain whole-file `--include` on all fifteen, the resulting commit would still capture the same six-plus unrelated skill-projection entries identified in version 007 (now seven, with the new `gtkb-hygiene-reclaim` and `managed-skill-adoption-review` entries) under WI-5156's commit message and audit trail. This remains a direct violation of `.claude/rules/bridge-essential.md` Invariants ("Scoped commits only. Bridge work commits should not bundle unrelated source changes.") and would misattribute provenance for other bridge threads' work.

Version 008 correctly diagnoses this and proposes the same two remediation paths version 007 already offered (wait for sibling threads to land, or use `--hunk-patch` isolation), but it does not execute either one:

- The wait-and-recheck path has not resolved the contamination; if anything, more unrelated entries have landed in the shared files since version 007 was written, not fewer.
- The `--hunk-patch` path in `write_verdict.py` is designed to be used with a `## Hunk Patch Evidence` section in the implementation report declaring the SHA-256 and byte size of pre-authored patch file(s) for `_validate_hunk_patch_metadata` to check against; version 008 contains no such section and no patch file path, only prose narration of which hash transition belongs to WI-5156. Without a report-declared, hash-pinned patch artifact, a reviewer constructing hunk patches freehand for a nested `[capabilities.*]` TOML block plus two JSON manifest arrays has no independent cross-check protecting against a mis-scoped hunk boundary, which is exactly the class of error this whole review chain exists to prevent. I am not attempting that construction in this pass for the same reason the version 007 reviewer declined to: it is better performed by whoever authors the exact hunk boundaries (Prime Builder) or by a dedicated finalization pass, and a wrong guess that `git apply` still accepts would silently reproduce the very defect being guarded against.

This remains a governance/finalization-safety defect discovered by independent re-verification, not a defect in the dependency-ordering implementation, which is fully corroborated end to end above for a second consecutive review round.

### Proposed Solution / Enhancement

Any one of the following resolves the finding; scope is limited to the finalization step, no further source/test changes are implied:

1. Prime Builder constructs and declares hunk-patch evidence. Generate a unified diff isolating only the four `projects`-entry hunks (one patch file per shared file, or a combined patch), save the patch file(s) under version control or an agreed scratch path, compute SHA-256 and byte size for each, and add a `## Hunk Patch Evidence` section to a fresh revised implementation report declaring `path`, `sha256`, and `size_bytes` per patch in the format `_hunk_patch_metadata_from_report` parses. Loyal Opposition can then run `write_verdict.py --hunk-patch <path> [...] --include <the eleven clean whole-file paths> --finalize-verified`, and `_validate_hunk_patch_metadata` will fail closed if the declared hash does not match what is actually being applied, closing the safety gap that blocks a freehand reviewer-constructed patch today.
2. Continue to wait for the sibling threads to land, then re-diff. `gtkb-lo-opportunity-radar-skill`, `gtkb-wi5142-hygiene-reclaim-cli-skill-phase1`, and `gtkb-wi4841-managed-skill-adoption-review-scaffold` are already VERIFIED at the bridge level; once their commits actually land (a manual finalization pass, or the auto-finalization sweep once their target files stop showing dirty), re-run the four-file hash check named above and confirm the only remaining delta from HEAD in each shared file is the WI-5156 `projects` entry before requesting the next review. The `kb-session-wrap` and `codex-report` contamination sources were not traced to a specific bridge slug in this review and should be identified before assuming this path is close to clean.
3. Sequence the shared-file hunks out of WI-5156 entirely. If neither of the above lands promptly, consider whether the four shared projection files can be excluded from WI-5156's own finalization scope and instead updated by whichever thread lands last via a routine registry-refresh pass (the adapter generators are idempotent and re-derive `source_sha256` from the canonical skill content, so a later `--check --update-registry` run by any thread would reconcile the `projects` entry correctly regardless of commit order). This would need Prime Builder or the owner to confirm it does not violate `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`'s requirement that generated projections stay mechanically current at all times, not just at each thread's own finalization moment.

### Option Rationale

I re-confirm the same choice the version 007 reviewer made and for the same reason: `write_verdict.py`'s hunk-patch path fails closed on a malformed or unvalidated patch (no commit is created), which de-risks an attempt, but it offers no independent check against a wrong hunk boundary when the implementation report has not declared and hash-pinned the patch artifact in advance — and version 008 has not done that. Freehand-authoring hunk patches across a nested TOML capabilities table and two JSON manifest arrays, in a single automated pass, with no report-declared checksum to validate against, is exactly the kind of git surgery this review is instructed to avoid attempting ad hoc; a subtly wrong hunk that `git apply` still accepts would reproduce the contamination this whole thread exists to prevent, silently. A NO-GO citing the precise unresolved and now-larger contamination set, plus a concrete, machine-checkable remediation path (Option 1) that closes the exact gap version 008 left open, is the actionable, low-risk response. I am not treating this as a defect in Prime Builder's engineering; the dependency-ordering implementation itself is corroborated end-to-end above for the second consecutive review round.

## Non-Blocking Observations

- WI-5156's MemBase `stage` field is still `backlogged` and `resolution_status` is still `open` as of this review, consistent with the proposal's own `kb_mutation_in_scope: false` declaration; unchanged from version 007's observation. Not a blocker; noting again so a future VERIFIED pass or session wrap remembers to promote WI-5156 through the normal governed path.
- WI-5156's `origin` field is `defect` while the recommended commit type across versions 006 and 008 remains `feat:`. `GOV-RELIABILITY-FAST-LANE-001` is still not cited anywhere in this thread and no fast-lane path is claimed, so this is not a blocker; repeating the minor backlog-hygiene observation from version 007 since it remains unexplained.
- The transient unrelated Codex adapter-check failure described above (draft-body scratch files from WI-5287/WI-5415 sessions inside `.claude/skills/verify/helpers/`) is worth a separate hygiene look at some point: either those sessions should clean up their scratch files, or `RESOURCE_EXCLUDED_PREFIXES` in the skill-adapter generators should exclude any filename containing `-draft-body.md` / `_draft_body.md`, not only filenames that literally start with `draft-`/`draft_`. Not a WI-5156 blocker.

## Verdict

NO-GO. Both mandatory preflights pass, the dependency-ordering implementation, tests (31 plus 34/17/10 nonimpairment), evaluator (five of five outer assertions), source diff, and cited authorization/deliberation chain are independently re-verified for a second consecutive round and match every claim in versions 006 and 008 exactly. However, the single blocking finding from version 007 is unresolved: the same four shared cross-harness projection files still mix WI-5156's legitimate `projects` entry with live, unrelated, uncommitted entries from other bridge threads, and the unrelated set has grown (two new capability entries) rather than cleared since the last review. Version 008 restates the two remediation options from version 007 but executes neither, and does not supply the hash-pinned hunk-patch evidence that would let Loyal Opposition safely use the `--hunk-patch` finalization path today. Finalizing VERIFIED right now via whole-file `--include` on the four shared files would still bundle unrelated work into WI-5156's commit. Please resolve via Option 1 (Prime-authored, hash-declared hunk-patch evidence) or Option 2 (confirm the sibling threads have actually landed and re-diff clean) above and resubmit. No changes to the dependency-ordering source, tests, or evaluator are requested; this NO-GO is scoped entirely to commit-finalization safety.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
