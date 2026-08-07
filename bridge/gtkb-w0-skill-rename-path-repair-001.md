NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e551d95-6728-46fd-b64d-181c9617a827
author_model: claude-fable-5
author_model_version: claude-fable-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; activity build

bridge_kind: prime_proposal
Document: gtkb-w0-skill-rename-path-repair
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640
related_work_items: ["WI-5662", "WI-5663", "WI-5664", "WI-5665", "WI-5666", "WI-5667"]

target_paths: [".claude/rules/file-bridge-protocol.md", ".claude/rules/loyal-opposition.md", ".claude/rules/codex-review-gate.md", ".claude/rules/auto-finalization-sweep.md", "config/agent-control/gtkb-file-bridge-protocol.md", "config/agent-control/gtkb-loyal-opposition.md", "config/agent-control/gtkb-review-gate.md", "config/agent-control/gtkb-auto-finalization-sweep.md", ".claude/skills/gtkb-verify/helpers/write_verdict.py", ".codex/skills/gtkb-verify/helpers/write_verdict.py", ".cursor/skills/gtkb-verify/helpers/write_verdict.py", ".goose/skills/gtkb-verify/helpers/write_verdict.py", ".agent/skills/gtkb-verify/SKILL.md", ".agent/skills/gtkb-proposal-review/SKILL.md", ".agent/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py", "groundtruth-kb/templates/skills/bridge/**/*.md", "groundtruth-kb/templates/skills/bridge/**/*.py", "groundtruth-kb/templates/skills/baseline-audit/**/*.md", "groundtruth-kb/templates/skills/baseline-audit/**/*.py", "groundtruth-kb/templates/skills/gtkb-baseline-audit/**/*.md", "groundtruth-kb/templates/skills/gtkb-baseline-audit/**/*.py", "groundtruth-kb/templates/project/AGENTS.md", "groundtruth-kb/templates/rules/session-start-orientation.md", "groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_self_review_write_time_gate.py", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py", "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py", "groundtruth-kb/tests/framework/test_bash_enforcement_parser.py"]
implementation_scope: skill_rename_stale_path_repair_sweep
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# W0.1 Thread A — Skill-Rename Stale-Path Repair Sweep (WI-5640 completion; supplies WI-5662..WI-5667 content)

## Summary

The WI-5640 canonical skill rename (commit `3e7626a41`, landed `--no-verify` per
owner decision A recorded in that commit subject) renamed
`.claude/skills/verify/` to `.claude/skills/gtkb-verify/` and the sibling
bridge-family skills to their `gtkb-` names, but left the retired path
`.claude/skills/verify/helpers/write_verdict.py` (and sibling
`.claude/skills/bridge*/` forms) cited across live governance surfaces. The
retired path does not exist on disk (`ls .claude/skills/verify` fails; the live
helper is `.claude/skills/gtkb-verify/helpers/write_verdict.py`). Three test
modules are broken TODAY because of the drift (live evidence below; the prior
register said two — a third was found failing during live re-verification).
This proposal is a single bounded repair sweep: replace every live-surface
stale reference with the canonical `gtkb-` path, regenerate the harness
projections, retire the unreferenced old-name template duplicate
`groundtruth-kb/templates/skills/bridge/`, complete the last old-name
managed-template registration (`skills/baseline-audit/`) following the exact
precedent the other renamed skills already use, and repair the broken tests.

Behavior safety: no gate or validator requires the literal old path.
`write_verdict.py` validates only the `Commit Finalization Evidence` section
heading (required-sections list at line 78; section check at line 1004), not
the helper-line literal; `scripts/gtkb_bridge_writer.py`,
`scripts/check_protected_commit_authorization.py`, and the bridge-compliance
gate template contain no match for the literal (verified by grep 2026-08-06).

## Live Anchor Evidence (every anchor re-verified 2026-08-06)

Stale literal `.claude/skills/verify/helpers/write_verdict.py` (or sibling
`.claude/skills/bridge*/` forms) at these live lines:

1. `.claude/rules/file-bridge-protocol.md:178`
2. `.claude/rules/loyal-opposition.md:160`
3. `.claude/rules/codex-review-gate.md:130`
4. `.claude/rules/auto-finalization-sweep.md:62`
5. `config/agent-control/gtkb-file-bridge-protocol.md:178`
6. `config/agent-control/gtkb-loyal-opposition.md:160`
7. `config/agent-control/gtkb-review-gate.md:130`
8. `config/agent-control/gtkb-auto-finalization-sweep.md:62`
9. `.claude/skills/gtkb-verify/helpers/write_verdict.py:1010` — the helper
   self-emits the retired path into every generated `Commit Finalization
   Evidence` block ("Finalization helper:" line).
10. Generated projections of the same emission: `.codex/.../write_verdict.py:1010`,
    `.cursor/.../write_verdict.py:1010`, `.goose/.../write_verdict.py:1014`.
11. `.agent/skills/gtkb-verify/SKILL.md:109,123`;
    `.agent/skills/gtkb-proposal-review/SKILL.md:59`;
    `.agent/skills/gtkb-bridge/SKILL.md:143` (Antigravity projections,
    regenerated by `scripts/generate_antigravity_skill_adapters.py`).
12. `groundtruth-kb/templates/rules/file-bridge-protocol.md:178`.
13. `groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md` — 15 stale-ref lines
    (live enumeration: 70, 78, 83, 105, 143, 150, 155, 163, 168, 179, 184,
    238, 239, 240, 250) citing `.claude/skills/bridge/`,
    `.claude/skills/bridge-propose/`, `.claude/skills/proposal-review/`,
    `.claude/skills/send-review/`.
14. `groundtruth-kb/templates/skills/gtkb-bridge/helpers/scan_bridge.py:34,38`;
    `groundtruth-kb/templates/skills/gtkb-bridge/helpers/show_thread_bridge.py:13`.
15. Stale duplicate directory `groundtruth-kb/templates/skills/bridge/`
    (old-name copy of `gtkb-bridge/`; `managed-artifacts.toml` registers only
    the `skills/gtkb-bridge/` template paths at lines 539-591, so the old dir is
    unreferenced by the registry and carries the same stale refs at SKILL.md
    70-250 and helpers 34/38/13).
16. Baseline-audit trio — the last old-name managed-template registration:
    `groundtruth-kb/templates/managed-artifacts.toml:474-475`
    (`template_path = "skills/baseline-audit/SKILL.md"`,
    `target_path = ".claude/skills/baseline-audit/SKILL.md"`),
    referenced by `groundtruth-kb/templates/project/AGENTS.md:98-99` and
    `groundtruth-kb/templates/rules/session-start-orientation.md:55`. Precedent:
    the decision-capture artifact kept its stable id
    `skill.decision-capture.skill-md` while its paths moved to
    `skills/gtkb-decision-capture/` (managed-artifacts.toml:445-449).
17. `groundtruth-kb/src/groundtruth_kb/modernization/workflow.py:405,413,421`
    — retired-path FALLBACK arguments to `_resolve_platform_helper` (the
    canonical `gtkb-` path is tried first; the fallback args are dead code
    because the old paths exist nowhere). Live drift note: the prior register
    cited only line 421; lines 405 and 413 carry the same retired fallbacks.
18. Broken tests (all three failures reproduced live 2026-08-06):
    - `platform_tests/scripts/test_self_review_write_time_gate.py:43` —
      collection-time FileNotFoundError loading the retired helper path.
    - `platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py:33,49`
      — 2 of 5 tests fail asserting a prompt string
      (`python .claude/skills/verify/helpers/write_verdict.py`) that
      `scripts/ollama_harness.py` no longer emits at all (the live prompt
      routes verdicts through the PublishBridgeVerdict tool).
    - `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`
      (fixture lines 17-21, 43-46, 54-56) — 2 of 4 tests fail because
      `.gitignore` already carries only `gtkb-verify` scratch patterns (lines
      621-623, 675-678) while the fixtures still assert the retired
      `skills/verify/` scratch paths are ignored.
19. Stale-literal consistency updates in green tests (inert fixture content;
    updated so the acceptance grep converges): 
    `platform_tests/scripts/test_gtkb_bridge_writer.py:169`,
    `platform_tests/scripts/test_check_protected_commit_authorization.py:889`,
    `platform_tests/scripts/test_fab14_directive_hook_coverage.py:121,171`,
    `platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py:68`,
    `platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py:63`,
    `groundtruth-kb/tests/framework/test_bash_enforcement_parser.py:59,60,73`.
    Live enumeration command and result (2026-08-06):
    `findstr /S /M /C:"skills/verify/helpers" E:\GT-KB\platform_tests\*.py`
    returns exactly the eight platform_tests files listed in items 18-19. The
    prior register's example filename test_verify_skill_scaffolding.py does
    not exist; the live enumeration above supersedes it.

## Proposed Change

One sweep, one commit class (`fix`), no behavior change beyond the corrected
emission string:

1. Replace the retired literal with
   `.claude/skills/gtkb-verify/helpers/write_verdict.py` at anchors 1-9 and 12.
2. Replace the retired `.claude/skills/bridge*/` family literals with their
   `gtkb-` forms at anchors 13-14.
3. Regenerate harness projections rather than hand-editing them:
   `scripts/generate_codex_skill_adapters.py` (.codex),
   `scripts/generate_cursor_skill_adapters.py` (.cursor),
   `scripts/generate_api_skill_adapters.py` with the .goose output dir (.goose),
   `scripts/generate_antigravity_skill_adapters.py` (.agent). The projection
   paths in target_paths are regeneration OUTPUTS, listed because their bytes
   change.
4. Retire `groundtruth-kb/templates/skills/bridge/` (unreferenced old-name
   duplicate; registry points only at `skills/gtkb-bridge/`). The other three
   old-name duplicates (`bridge-propose/`, `decision-capture/`, `spec-intake/`)
   carry none of the swept literals and stay with WI-5667's scaffold-cluster
   scope; they are reported, not touched.
5. Baseline-audit completion, exactly per the decision-capture precedent:
   rename `templates/skills/baseline-audit/` to
   `templates/skills/gtkb-baseline-audit/`; update
   `managed-artifacts.toml:474-475` template_path/target_path to the `gtkb-`
   forms while keeping the stable id `skill.baseline-audit.skill-md`; update
   the two scaffold references (`templates/project/AGENTS.md:98-99`,
   `templates/rules/session-start-orientation.md:55`) to `/gtkb-baseline-audit`
   and `.claude/skills/gtkb-baseline-audit/SKILL.md`.
6. Remove the dead retired-path fallback arguments at
   `modernization/workflow.py:405,413,421`.
7. Repair the three broken test modules (18) against live behavior; update the
   inert stale literals (19) to the canonical path.

## Relationship to Prior Rename-Sweep Threads (collision ledger)

- WI-5665 (Sweep S4) is DONE: `gtkb-wi5665-cursor-fallback-hardening-test-repair`
  reached VERIFIED at version 019, and the previously frozen shared path
  `platform_tests/skills/test_verified_finalization_validation_hardening.py`
  is clean in the worktree (re-verified 2026-08-06). The WI-5662 backlog
  Status Detail hold ("do not claim/revise/edit until WI-5665 reaches governed
  terminal disposition") is therefore satisfied on both stated conditions;
  the Status Detail predates the WI-5665 VERIFIED and is stale.
- Stalled prior threads, none revised or adopted by this thread:
  `gtkb-wi5662-canonical-doc-reference-recovery` (NO-GO v016, no claim, and
  the chain's own record calls the original thread non-executable),
  `gtkb-wi5662-skill-rename-canonical-doc-refs` (NO-GO v010),
  `gtkb-wi5662-canonical-skill-reference-repair` (WITHDRAWN v003),
  `gtkb-wi5664-rules-config-skill-reference-repair` (NO-GO v014),
  `gtkb-wi5666-gitignore-docs-script-skill-refs` (NO-GO v010),
  `gtkb-wi5667-scaffold-managed-skill-rename` (NO-GO v006) and its recovery
  thread (NO-GO v006). WI-5663 has no thread. This proposal is the
  owner-directed Wave 0 consolidation of that livelocked sweep family into one
  executable thread; the stalled threads' own terminal disposition
  (WITHDRAWN or DEFERRED) is owner business flagged for the wrap report, not
  performed here.
- Foreign dirty byte disclosure: `modernization/workflow.py` currently carries
  one unrelated dirty line (removal of the session_resolver_fallback token at
  line 52, another thread's in-flight work). The edits proposed here (lines
  405/413/421) are hunk-disjoint from it. Implementation re-verifies at
  implementation-start and will not stage, revert, or adopt the foreign hunk.
- Out-of-scope residual carriers of the old literal, deliberately untouched:
  append-only `bridge/**` history; historical one-off session filing scripts
  (`scripts/_dispatch_wi5241_006_verdict.py`, `file_go_verdict_*.py`,
  `file_proposal_wi5540.py`, `write_bridge_*.py`, `writer_script.py`, and
  draft bodies under harness skills helpers); untracked
  `.tmp-lo-verdict-drafts/` scratch. These are audit-trail or session
  artifacts, not live governance surfaces.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - applicable because `.claude/rules/file-bridge-protocol.md` is a modified surface; every change in this sweep stays within the GT-KB root, touches no `applications/` path, and leaves the root/applications boundary untouched.

- `GOV-08` — the Knowledge Database is the single source of truth; live rule
  surfaces must not instruct agents to invoke a nonexistent helper path.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — state claims derive from fresh
  canonical reads; stale path citations in always-loaded rules actively
  misdirect every session.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the swept surfaces include the bridge
  protocol rule and the verdict-finalization helper emission; append-only
  bridge history is explicitly excluded from the sweep.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — governing links
  cited concretely here.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project/work-item
  linkage in the metadata block (WI-5640 under
  PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY, active project-scope
  PAUTH cited).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in
  the verification plan below.
- `GOV-WORK-TREE-HYGIENE-001` — hunk-disjoint handling of the one foreign
  dirty line in workflow.py; no concurrent thread's bytes are staged.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the sweep must not impair the
  stalled sibling threads' audit trails; they are left intact.
- WI-5640 rename thread `bridge/gtkb-skill-rename-rollout-001..005` (GO at
  v004; rollout commit `3e7626a41`) — the change this sweep completes.
- WI-5662..WI-5667 — the rename-sweep work items whose concrete content this
  thread supplies (they are backlogged with empty descriptions).

## Prior Deliberations

Search run 2026-08-06: `gt deliberations search "skill rename write_verdict path" --limit 5`.

- `DELIB-202667701` — owner approved the command-centered split:
  write_verdict.py remains the VERIFIED-only finalization surface. This sweep
  preserves that contract; only the emitted path literal changes.
- `DELIB-20265329` — GO for seeding Prior Deliberations into harness-authored
  verdict files; context for why the write_verdict helper emission surface is
  load-bearing across harnesses.
- `DELIB-202667544` — Loyal Opposition NO-GO titled against WI-5640 (registry
  admission / deterministic preflight); surfaced by the search and cited for
  completeness of the WI-5640 decision trail.
- File refs: `bridge/gtkb-skill-rename-rollout-001..005` (WI-5640 rename
  thread; GO at v004; commit `3e7626a41` with owner decision A recorded in the
  commit subject); the stalled sweep threads enumerated in the collision
  ledger above; `bridge/gtkb-wi5667-scaffold-managed-skill-rename-001..006`
  (owner-directed scaffold-cluster rename whose baseline-audit sub-cluster
  this thread completes under the decision-capture precedent).

## Owner Decisions / Input

- Owner AUQ, 2026-08-05 (four recorded answers): investigation method, plan
  scope, context budget, and review model for the friction-remediation
  program that produced this thread's work packet.
- Owner AUQ, 2026-08-06: "Expand Wave 0 now" — authorizes the Wave 0 scope
  expansion containing this repair sweep.
- Owner AUQ, 2026-08-06: "Yes — file W0.1/W0.3/W0.4 now" — adopts split-phase
  execution and authorizes filing this proposal (W0.1 Thread A) immediately.
- Removal notice per CLAUDE.md Protected Behaviors: this proposal includes two
  removals — the unreferenced duplicate directory
  `groundtruth-kb/templates/skills/bridge/` and the dead fallback arguments in
  workflow.py — presented here for explicit review; they proceed only under
  this thread's GO, which together with the owner AUQ chain above constitutes
  the owner-approval path for the removals.
- Non-canonical context: `scratchpad/gtkb-friction-remediation-plan-2026-08-06.md`
  (owner-review draft; Wave 0 / W0.1 packet definition). Cited as context
  only; authority rests on the AUQ decisions and the governing specs above.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-08` and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` already require live surfaces to cite
real, canonical paths, and the WI-5640 rename thread
(`bridge/gtkb-skill-rename-rollout`, GO at v004) is the approved change whose
completion this sweep performs. No new or revised requirement is required
before implementation.

## Specification-Derived Verification Plan

All commands are cmd.exe-safe and runnable from E:\GT-KB as written.

| Requirement | Test / command | Required observed behavior |
|---|---|---|
| GOV-08 / freshness: no live stale refs | `findstr /S /M /C:"skills/verify/helpers" E:\GT-KB\.claude\rules\*.md E:\GT-KB\config\agent-control\*.md` | No output; exit code 1 (no matches). |
| Same, template tree | `findstr /S /M /C:"skills/verify/helpers" E:\GT-KB\groundtruth-kb\templates\*.md E:\GT-KB\groundtruth-kb\templates\*.py E:\GT-KB\groundtruth-kb\templates\*.toml` | No output; exit code 1. |
| Same, test trees | `findstr /S /M /C:"skills/verify/helpers" E:\GT-KB\platform_tests\*.py E:\GT-KB\groundtruth-kb\tests\*.py` | No output; exit code 1. |
| Broken test 1 repaired | `python -m pytest platform_tests/scripts/test_self_review_write_time_gate.py -q` | Collects and passes (FileNotFoundError today). |
| Broken test 2 repaired | `python -m pytest platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py -q` | 5 of 5 pass (2 fail today). |
| Broken test 3 repaired | `python -m pytest platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py -q` | 4 of 4 pass (2 fail today). |
| Emission fix + fixture consistency | `python -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py -q` | All pass with updated canonical literal. |
| workflow.py fallback removal safe | `python -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py -q` | Passes; helper resolution uses canonical paths only. |
| Projection regeneration idempotent | Run the four generators twice; `git status --porcelain .codex .cursor .goose .agent` between runs | First run changes only the listed projection files; second run produces no further diff. |
| Template dir retirement | `dir E:\GT-KB\groundtruth-kb\templates\skills\bridge 2>nul` and `findstr /C:"skills/bridge/" E:\GT-KB\groundtruth-kb\templates\managed-artifacts.toml` | Directory absent; no registry reference (both commands report nothing found). |
| Baseline-audit completion coherent | `findstr /C:"baseline-audit" E:\GT-KB\groundtruth-kb\templates\managed-artifacts.toml E:\GT-KB\groundtruth-kb\templates\project\AGENTS.md E:\GT-KB\groundtruth-kb\templates\rules\session-start-orientation.md` | Every hit is the `gtkb-baseline-audit` form or the stable artifact id; template dir exists only under the new name. |
| Code quality (both gates) | `ruff check` and `ruff format --check` on every touched .py file | Both pass; they are separate gates per the bridge protocol. |

## Acceptance Criteria

1. Only the declared target_paths change; append-only `bridge/**` history and
   the enumerated historical one-off session artifacts are untouched.
2. The acceptance greps in the verification plan return zero live-surface
   matches for the retired literal.
3. The three broken test modules collect and pass; the previously green
   updated modules stay green.
4. Harness projections are regenerated by their documented generators, not
   hand-edited, and regeneration is idempotent.
5. `templates/skills/bridge/` is retired with no residual registry reference;
   the baseline-audit trio is internally consistent under the `gtkb-` name
   with its artifact id unchanged.
6. The one foreign dirty line in workflow.py is neither staged nor reverted.
7. `ruff check` and `ruff format --check` both pass on every changed .py file.
8. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment,
   or external system is mutated; no commit is created by Prime Builder —
   finalization remains the Loyal Opposition atomic step.

## Risk and Rollback

Risk is low: documentation/test/literal-string surface plus one emission
string and two dead-code removals, with no gate matching the old literal
(verified). Residual risks: (a) projection regeneration could pull unrelated
canonical drift into the diff — mitigated by reviewing the regeneration diff
against the expected file set and reporting any excess before filing the
implementation report; (b) adopter scaffolds created between the WI-5640
rename and this sweep may reference the old baseline-audit template path —
mitigated by the stable artifact id and the registry's overwrite upgrade
policy; (c) the workflow.py foreign dirty line could collide at finalization —
mitigated by hunk-disjoint staging and re-verification at implementation
start. Rollback is a plain revert of the sweep hunks and restoration of the
two retired directories from git history; no data migration, schema change,
or state mutation is involved.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640 rename rollout (commit 3e7626a41, landed --no-verify); WI-5662..WI-5667 stalled sweep threads; friction register 2026-08-06 (F-070, F-104-F2); two collection-broken tests reproduced live plus test_gitignore_tree_stabilization_scratch.py 2/4 failing",
  "canonical_authority": "GOV-08 (KB single source of truth); GOV-SOURCE-OF-TRUTH-FRESHNESS-001; canonical skill home .claude/skills/gtkb-verify/ established by the WI-5640 rename thread",
  "primary_route": "mechanical reference sweep: every live citation of the retired .claude/skills/verify/ path family updated to the canonical gtkb-verify path; projections regenerated from canonical sources; stale template dir retired; three broken/stale test files repaired",
  "before_behavior": "four always-loaded rules + mirrors instruct agents to run a nonexistent helper path; write_verdict.py stamps the wrong path into its own finalization evidence; two tests fail at collection; adopter templates scaffold the dead path outward",
  "after_behavior": "every live surface names the real helper path; helper self-emission correct; the three test files collect and pass; templates scaffold canonical paths to adopters",
  "self_descriptive_naming": "no new names introduced; the sweep converges all references onto the existing canonical gtkb- names",
  "obsolete_guidance_disposition": "stale duplicate dir groundtruth-kb/templates/skills/bridge/ retired in favor of templates/skills/gtkb-bridge/; append-only bridge history left untouched as historical record",
  "history_preservation": "no bridge/ file edited; git history preserves the retired template dir; rule edits are content-corrections to live guidance, not history rewrites",
  "baseline": {
    "stale_live_citations": "4 rules + 4 mirrors + helper:1010 + 3 .agent SKILL.mds + templates cluster (15 lines in gtkb-bridge SKILL.md) + workflow.py 405/413/421 + 8 platform_tests files + 1 framework test",
    "broken_today": ["platform_tests/scripts/test_self_review_write_time_gate.py (collection FileNotFoundError)", "platform_tests/scripts/test_ollama_dispatch_prompt_restructure.py (2/5 stale assertions)", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py (2/4 stale fixtures)"]
  },
  "expected_result": {
    "live_stale_citations": "zero outside append-only bridge/ history (findstr acceptance check in the verification plan)",
    "tests": "all three named test files collect and pass; ruff check + ruff format --check clean on touched .py"
  },
  "rollback": "single revert restores prior text; no data, schema, or protocol change involved",
  "hard_invariants": "no behavior change to any gate or helper beyond the emitted path string; compliance gates validate path-set sections, not the literal helper path (verified), so no gate behavior shifts",
  "fail_closed_conditions": "not applicable to the sweep itself; the helper and gates retain their existing fail-closed semantics unchanged",
  "essential_context_preservation": "each edited citation keeps its surrounding instruction text; only the path token changes; the WI-5640 rename thread is cited so provenance of the canonical home stays discoverable"
}
```

## Cross-Harness Disposition

Per-harness parity declaration (per `ADR-CROSS-HARNESS-PARITY-001` Q8 /
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`):

- **claude (B)**: canonical surfaces edited (`.claude/rules/*`, `.claude/skills/gtkb-verify/helpers/write_verdict.py:1010`).
- **codex (A) / cursor (E) / goose (G)**: write_verdict.py projections regenerated from the canonical
  source via the adapter pipeline (codex/cursor content-identical; the goose projection's known
  ~2,833-line pre-existing drift is NOT reconciled here — only the regenerated emission line changes
  with it, and the drift is disclosed as a follow-on repair).
- **All other harnesses (C, D, F, H)**: no harness-local copies of touched surfaces; shared scripts
  change uniformly.
- Sibling-thread disclosure: `bridge/gtkb-w0-executable-go-pre-verdict-validation-001.md` (filed
  2026-08-06) also lists `write_verdict.py` in its target_paths. Sequencing: this sweep's
  single-line emission fix lands first; the sibling's implementer re-verifies line anchors at
  implementation start. Neither change overlaps the other's hunks.
- No typed waiver requested.

## Recommended Commit Type

`fix` — repairs broken tests and actively misdirecting live references left by
an approved rename; no new capability surface is added.

## DISARM — Implementation

This file requests review only. It grants no protected-edit, claim, start,
finalization, or cleanup authority. Implementation requires the Loyal
Opposition GO on this thread, a fresh work-intent claim, and an
implementation-start authorization packet created from that GO before any
target path is touched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
