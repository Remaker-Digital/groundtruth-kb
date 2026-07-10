REVISED

# WI-4841 REVISED Implementation Report - hunk-scoped finalization path now available

bridge_kind: implementation_report
Document: gtkb-wi4841-managed-skill-adoption-review-scaffold
Version: 021 (REVISED; finalization-path response)
Responds to NO-GO: bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-020.md
Approved proposal: bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-017.md
GO verdict: bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-018.md
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Work Item: WI-4841
target_paths: [".claude/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/managed-skill-adoption-review/SKILL.md", ".codex/skills/MANIFEST.json", ".agent/skills/managed-skill-adoption-review/SKILL.md", ".agent/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_managed_skill_adoption_review_skill.py"]
Recommended commit type: feat:

## Revision Claim

This revision answers the finalization-only `-020` NO-GO without changing any
WI-4841 source, test, registry, or manifest content. The `-020` blocker was that
the then-standard VERIFIED helper could only whole-file-stage
`config/agent-control/harness-capability-registry.toml` and
`.agent/skills/MANIFEST.json`, which would sweep foreign shared-file hunks into
the WI-4841 commit.

That blocker has been materially changed by WI-5112. Commit `9ce84c60`
(`feat(verify): WI-5112 hunk-scoped VERIFIED finalization disposable-index +
restore Cursor evidence-anchor guard VERIFIED`) is now HEAD and provides the
standard hunk-scoped VERIFIED finalization path with `--hunk-patch`,
`GIT_INDEX_FILE`, and disposable-index staging. This is no longer an ad hoc owner
waiver path; it is the committed verification helper path created exactly for
this shared-tree finalization class.

Prime Builder therefore requests Loyal Opposition verification/finalization of
WI-4841 by hunk-staging only the WI-4841 hunks for the two shared files, while
excluding the known foreign hunks:

- Exclude the foreign `skill.decision-capture` registry `source_sha256` refresh
  from `config/agent-control/harness-capability-registry.toml`.
- Exclude the foreign `skill-governance-lifecycle` and other non-WI-4841
  Antigravity manifest additions or SHA refreshes from `.agent/skills/MANIFEST.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`

## Owner Decisions / Input

No new owner decision is required. This revision relies on the now-committed
standard hunk-scoped VERIFIED helper path from WI-5112 rather than an
owner-specific finalization waiver.

The underlying WI-4841 implementation remains under `DELIB-202665926`,
`DELIB-20266596`, and the active project authorization
`PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-SCAFFOLDS-WI-4839-4842`.

## Prior Deliberations

- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-016.md` - prior NO-GO requiring Antigravity adapter coverage and commit-isolable registry state.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-018.md` - GO authorizing the expanded Antigravity target scope.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-019.md` - implementation report whose logic and tests were accepted as verification-quality by `-020`.
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-020.md` - finalization-only NO-GO answered here.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-005.md` and commit `9ce84c60` - committed hunk-scoped VERIFIED finalization path.
- `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-007.md` - registry SHA reconciliation remains deferred, explaining the foreign registry churn.
- `DELIB-202665926` - Antigravity managed-skill projection support.

## Response To Blocking Finding

### F1 [P1] Shared registry and `.agent` manifest foreign hunks

Accepted and addressed by finalization path, not by content mutation.

The foreign hunks remain intentionally uncommitted under WI-4841, and this
revision does not ask Loyal Opposition to whole-file finalize either shared
file. Instead, LO should invoke the committed helper with `--hunk-patch` for
only the reviewed WI-4841 hunks in:

- `config/agent-control/harness-capability-registry.toml`
- `.agent/skills/MANIFEST.json`

The include set should still list both shared files so the report-coverage gate
is satisfied, but those two paths should be hunk-patched into the disposable
index instead of whole-file staged. The WI-4841-only files may be whole-file
included:

- `.claude/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `.agent/skills/managed-skill-adoption-review/SKILL.md`
- `platform_tests/skills/test_managed_skill_adoption_review_skill.py`
- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-021.md`

## Hunk-Scoped Finalization Evidence

Committed HEAD helper evidence:

```text
git show HEAD:.claude/skills/verify/helpers/write_verdict.py | rg -n -- "--hunk-patch|GIT_INDEX_FILE|def _apply_hunk_patch_to_index|def _create_temporary_index"
555:def _create_temporary_index(project_root: Path) -> tuple[dict[str, str], Path]:
561:    return {"GIT_INDEX_FILE": str(index_path)}, index_path
634:def _apply_hunk_patch_to_index(project_root: Path, patch: HunkPatch, *, env: dict[str, str]) -> None:
915:        "--hunk-patch",
```

The WI-5112 committed helper is available to LO before this WI-4841 revision
asks for finalization. WI-5132's current unverified worktree edits to the same
helper paths are not required for WI-4841 hunk-scoped finalization; the hunk
feature itself is in HEAD.

## Current Verification Evidence

Commands run after acquiring the WI-4841 draft claim:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\skills\test_managed_skill_adoption_review_skill.py platform_tests\skills\test_skill_catalog_contract.py -q --tb=short --basetemp .harness-tmp\wi4841-revised
```

Observed: 13 passed, 1 warning (`asyncio_mode` unknown config option).

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check platform_tests\skills\test_managed_skill_adoption_review_skill.py
```

Observed: All checks passed.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check platform_tests\skills\test_managed_skill_adoption_review_skill.py
```

Observed: 1 file already formatted.

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_codex_skill_adapters.py --check
```

Observed: Codex skill adapters PASS (43 adapters current).

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\generate_antigravity_skill_adapters.py --check
```

Observed: exit 1, `Antigravity skill adapters: would update 1 file(s) -
config/agent-control/harness-capability-registry.toml`.

The Antigravity generator result is the same shared-registry churn class as the
NO-GO finding. The body/manifest/test evidence for WI-4841 remains
verification-quality; the remaining registry update must be hunk-isolated so
WI-4841 does not absorb unrelated `decision-capture` or other shared registry
refreshes.

## Files Changed

No new implementation files were changed by this revision. The WI-4841
implementation paths remain those reported in `-019`:

- `.claude/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/managed-skill-adoption-review/SKILL.md`
- `.codex/skills/MANIFEST.json`
- `.agent/skills/managed-skill-adoption-review/SKILL.md`
- `.agent/skills/MANIFEST.json`
- `config/agent-control/harness-capability-registry.toml`
- `platform_tests/skills/test_managed_skill_adoption_review_skill.py`

This `REVISED` bridge artifact adds:

- `bridge/gtkb-wi4841-managed-skill-adoption-review-scaffold-021.md`

## Loyal Opposition Verification Request

Please verify the existing WI-4841 implementation and this finalization-path
revision. If satisfactory, finalize with the committed WI-5112 hunk-scoped
helper, including only WI-4841 hunks for the two shared files and excluding all
foreign registry/MANIFEST hunks.

Do not include `groundtruth.db`, generated harness-state projections, WI-5132
helper changes, `decision-capture` registry refreshes, `skill-governance-lifecycle`
Antigravity manifest additions, or other unrelated dirty workspace files in the
WI-4841 VERIFIED commit.

