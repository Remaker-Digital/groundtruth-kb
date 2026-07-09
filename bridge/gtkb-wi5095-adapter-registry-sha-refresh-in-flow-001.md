NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3e93c6af-78ba-4c3e-81fd-616af4cc9ea4
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# gtkb-wi5095-adapter-registry-sha-refresh-in-flow — Make registry source_sha256 refresh part of the default adapter-regen flow

bridge_kind: prime_proposal
Document: gtkb-wi5095-adapter-registry-sha-refresh-in-flow
Version: 001
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5095

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/generate_api_skill_adapters.py", "config/agent-control/harness-capability-registry.toml", ".codex/skills/**", ".agent/skills/**", ".api-harness/skills/**", ".goose/skills/**", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_generate_api_skill_adapters.py", "platform_tests/scripts/test_registry_source_sha256_consistency.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The harness-capability registry records a `source_sha256` per adapter capability
(the normalized SHA of the canonical `.claude/skills/<name>/SKILL.md` the adapter
mirrors). All three skill-adapter generators
(`scripts/generate_codex_skill_adapters.py`,
`scripts/generate_antigravity_skill_adapters.py`,
`scripts/generate_api_skill_adapters.py`) refresh that registry SHA only under an
opt-in `--update-registry` flag. Their default `generate()` path (the one run by
`--check` and by the routine "regenerate the adapter" step) rewrites the adapter
body and the per-harness `MANIFEST.json` but leaves the registry `source_sha256`
untouched. Any adapter regenerated without the flag therefore silently drifts its
registry `source_sha256` away from the canonical body it claims to mirror.

WI-3407 (commit `2bf26a40`) is the concrete instance that surfaced this: editing
the canonical `decision-capture/SKILL.md` changed its normalized SHA from
`8544a4d4...` to `e2084661...`. The `.codex` adapter body + `.codex` MANIFEST were
regenerated (committed), and the registry `[capabilities.codex]` block was later
hand-refreshed to `e2084661...` (uncommitted in the worktree), but the
`[capabilities.antigravity]` and `[capabilities.goose]` registry blocks remain at
the stale `8544a4d4...`, and the `.agent/skills/decision-capture/SKILL.md` adapter
body was never regenerated (still records `Canonical source sha256: 8544a4d4...`).
The WI-3407 post-implementation report
(`bridge/gtkb-wi3407-composite-delib-workflow-skill-003.md`) surfaced the registry
lag explicitly as an out-of-scope hygiene finding.

This proposal makes registry `source_sha256` refresh part of the **default**
adapter-regen flow so the registry can never again drift from the adapter bodies,
and reconciles the currently-drifted registry blocks + stale adapter bodies as the
natural output of running the corrected generators. It is scoped as a systemic fix
per owner decision (this-session AUQ: "Systemic: refresh in the flow").

## Proposed Change

1. **Default registry refresh.** In each of the three generators, fold the
   `update_registry(...)` call into the standard `generate()` path so a normal
   (non-`--check`) run refreshes every regenerated capability's registry
   `source_sha256`. Preserve `--check` as non-mutating: in check mode the
   generators must **report** a stale registry `source_sha256` as drift (added to
   the `changed` list) without writing, exactly as they already do for stale
   adapter bodies and MANIFEST entries. Preserve idempotence: a second run after a
   clean generate reports no drift.
2. **Drift-catching test.** Add
   `platform_tests/scripts/test_registry_source_sha256_consistency.py` asserting,
   for every adapter capability in the registry, that its recorded
   `source_sha256` equals the current normalized SHA of its `adapter_source`
   canonical `SKILL.md` (using the same strip-generated-block + rstrip + trailing
   newline normalization the generators use). This is the enforcement surface that
   makes the drift class visible in CI going forward.
3. **Reconcile current drift.** Run the corrected generators to reconcile all
   drifted registry blocks (decision-capture codex/antigravity/goose and any other
   skill whose registry SHA lags) and to regenerate any stale adapter body (e.g.,
   `.agent/skills/decision-capture/SKILL.md`). The reconciliation is the
   deterministic output of the corrected default flow, not hand-editing.

Because the corrected default `generate()` regenerates all adapters, the
`target_paths` authorize the full adapter directories (`.codex/skills`,
`.agent/skills`, `.api-harness/skills`, `.goose/skills`) and the registry;
in practice the diff is limited to surfaces that are actually drifted (regeneration
is idempotent for already-current adapters). The breadth reflects the honest scope
of a systemic registry-refresh-in-flow fix.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-governed implementation; work proceeds only after GO + implementation-start packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH-backed implementation under the standing reliability project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the standing PAUTH does not bypass GO or implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH / Project / Work Item metadata carried above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification below.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the registry `source_sha256` is the parity-integrity record between a canonical skill source and its per-harness adapters; keeping it truthful is a cross-harness-parity requirement, and this change touches all harness adapter surfaces.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the adapter/registry/MANIFEST invariants this generator flow maintains.
- `GOV-STANDING-BACKLOG-001` - WI-5095 is the MemBase backlog authority for this work.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the new consistency test is the mechanical enforcement layer for the registry-SHA invariant.
- `GOV-RELIABILITY-FAST-LANE-001` - small, single-concern reliability defect-class fix under the standing fast-lane authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root platform files; no adopter/application file is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the registry is a governed artifact whose integrity record must stay truthful.

## Prior Deliberations

- WI-3407 thread `bridge/gtkb-wi3407-composite-delib-workflow-skill-003.md` (commit `2bf26a40`) - the post-implementation report that surfaced the registry `source_sha256` lag as an out-of-scope hygiene finding; this proposal is the governed follow-on.
- WI-4840 `bridge/gtkb-wi4840-advisory-disposition-skill-scaffold-*` - sibling skill-scaffold whose target_paths correctly included the registry and MANIFEST, illustrating that adapter-body changes must carry the registry `source_sha256` update; the drift here is the consequence of the update being opt-in rather than default.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the parity contract the registry `source_sha256` record serves.
- No prior deliberation proposes making registry refresh part of the default generate flow; this is novel scope for the generator contract.

## Owner Decisions / Input

- AskUserQuestion (this session, 2026-07-09): the owner selected "Systemic: refresh in the flow" - make registry `source_sha256` refresh part of the default adapter-regen flow across the codex/antigravity/api generators plus a drift-catching test, reconciling decision-capture and any other drifted skills. Implementation to await GO and a calmer worktree.
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5095 by project membership.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and the harness-onboarding adapter invariants require the registry `source_sha256` to truthfully record the canonical adapter source; the owner AUQ selected the systemic default-refresh approach. No new or revised requirement is needed before implementation.

## Cross-Harness Disposition

This change is inherently cross-harness: it corrects the registry-refresh behavior of the Codex (`.codex/`), Antigravity (`.agent/`), and API-harness (`.api-harness/`) generators, and the reconciliation run regenerates any drifted adapter body across those surfaces plus `.goose/`. Parity is the point of the change - the registry `source_sha256` is the parity-integrity record. Behavioral parity across the three generators is required and intended: each generator's default `generate()` must refresh the registry for the capabilities it owns, and `--check` must report registry drift without writing on all three. No owner-approved typed waiver is requested. Harnesses without a generator (Cursor `fallback`) are unaffected; their registry rows carry no generator-maintained `source_sha256` obligation under this change.

## Specification-Derived Verification (Spec-to-Test Mapping)

| Specification | Test / command | Expected result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (registry SHA truthful) | New `platform_tests/scripts/test_registry_source_sha256_consistency.py`: for every adapter capability, registry `source_sha256` == normalized SHA of its `adapter_source`. Run `python -m pytest platform_tests/scripts/test_registry_source_sha256_consistency.py -q`. | pytest PASS (green only after the reconciliation run). |
| Default generate refreshes the registry (codex) | Extend `platform_tests/scripts/test_generate_codex_skill_adapters.py`: assert a non-check `generate()` on a fixture whose registry SHA is stale updates the registry, and that `--check` reports the stale registry SHA as drift without writing. | pytest PASS. |
| Default generate refreshes the registry (antigravity) | Extend `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` with the analogous default-refresh + check-reports-drift assertions. | pytest PASS. |
| Default generate refreshes the registry (api-harness) | Extend `platform_tests/scripts/test_generate_api_skill_adapters.py` with the analogous assertions. | pytest PASS. |
| Idempotence preserved | Re-run each generator in `--check` after a clean generate; assert no registry drift reported. | No drift. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` AND `ruff format --check` on every changed `.py`. | Clean. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection: every changed file in-root; no `applications/` path. | In-root only. |

Command evidence (captured in the implementation report), one command per line:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_registry_source_sha256_consistency.py -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check
    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_antigravity_skill_adapters.py --check
    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_api_skill_adapters.py --check
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check the-changed-python-files
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check the-changed-python-files

## Risk / Rollback

Risk: making registry refresh default means a routine adapter regeneration now also
rewrites the registry `source_sha256`, and the first corrected run will reconcile
ALL currently-drifted registry blocks (not only decision-capture). Mitigation: the
reconciliation is deterministic and idempotent, the diff is limited to genuinely
drifted surfaces, and the new consistency test makes any residual drift visible
rather than silent. Because the live worktree is heavily dirtied by concurrent
`keep-working-pb` activity, the implementer MUST use a scoped/hunk-limited commit
that captures only the generator edits, the new test, the registry
`source_sha256` reconciliation hunks, and the regenerated adapter/MANIFEST hunks -
never a blanket sweep of the 400-plus untracked / 170-plus modified worktree files.
If the implementer cannot cleanly isolate those hunks (e.g., the concurrent fleet
is mutating the same files), implementation should pause until the worktree is
quiescent rather than risk a contaminated commit.

Rollback: single-commit revert of the three generator edits, the new test, the
registry reconciliation, and the regenerated adapter/MANIFEST hunks. No KB or
bridge-state mutation.

## Recommended Commit Type

`fix` - repairs a defect class (silent registry `source_sha256` drift from
opt-in registry refresh) by making refresh part of the default generator flow and
adding mechanical enforcement; reconciles the existing drift as a deterministic
consequence. No new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
