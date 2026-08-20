---
name: gtkb-skill-governance-lifecycle
description: Standardize GT-KB managed-skill creation and projection across canonical .claude skills, generated Codex adapters, registry declarations, manifests, tests, and bridge evidence.
---
# /skill-governance-lifecycle

Use this skill when creating or updating a GT-KB managed skill that must live in
the canonical `.harness-baseline-configuration/skills/` tree and be projected into Codex through the
GT-KB adapter pipeline. This skill is for repo-native managed skills, not
one-off personal skills, external plugin skills, or non-GTKB harness setup.

## Authority and Scope

- A managed GT-KB skill starts with the canonical source file at
  `.harness-baseline-configuration/skills/<skill-slug>/SKILL.md`.
- Codex consumes generated adapters under `.harness-baseline-configuration/skills/<skill-slug>/SKILL.md`.
  Do not hand-maintain adapter bodies when the generator can safely emit them.
- The harness capability registry at
  `config/agent-control/harness-capability-registry.toml` is the durable parity
  declaration for the skill capability.
- `.harness-baseline-configuration/skills/MANIFEST.json` is generated metadata for Codex adapter load and
  drift checks.
- Additional harness projections such as Antigravity, Cursor, API harnesses, or
  provider harnesses require target-path-covered proposal scope or an explicit
  typed parity disposition. Do not create those surfaces from this lifecycle by
  implication.
- Protected source, test, registry, manifest, and bridge-report writes still
  require the live bridge GO, implementation-start packet, and target-path
  coverage for the current thread.

## Required Inputs

Before drafting or editing a managed skill, identify:

- bridge document name, latest GO file, and implementation-start packet hash;
- work item and project authorization, when the change is project-scoped;
- skill slug, frontmatter `name`, and trigger-effective `description`;
- primary role scope in `required_for_roles`;
- canonical source path and projected Codex adapter path;
- tests that prove the skill is registered, loadable, not orphaned, and
  behaviorally described by its body;
- non-target harness disposition for any harness that will not receive a surface
  in the current slice.

## Lifecycle Recipe

1. Confirm the live bridge state is still latest `GO` for the proposal and run
   `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id <document-name>`.
2. Create or update `.harness-baseline-configuration/skills/<skill-slug>/SKILL.md` with valid
   frontmatter, a concise invocation description, non-goals, mandatory steps,
   verification expectations, and cross-harness notes.
3. Add or update the `[[capabilities]]` registry entry:
   `id = "skill.<skill-slug>"`, `kind = "skill"`, `canonical_name`,
   `canonical_purpose`, `canonical_source`, `required_for_roles`, and
   `parity_class`.
4. Declare the native Claude surface and Codex adapter surface in that registry
   entry. Record non-target harnesses as unsupported or deferred only when the
   bridge proposal authorizes that disposition.
5. Run
   `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --update-registry`
   when the generator can write only the authorized target paths. If
   `--check` reports unrelated adapter drift in a dirty worktree, confine the
   implementation to the authorized target paths and record the reason in the
   implementation report.
6. Ensure `.harness-baseline-configuration/skills/MANIFEST.json` includes the new adapter record with the
   canonical source path, adapter path, capability id, canonical name, and
   normalized canonical-source `source_sha256`.
7. Add a focused test under `platform_tests/skills/test_<skill_slug>_skill.py`
   that proves the new skill file, registry entry, adapter, manifest entry, and
   target-path containment.
8. Run the focused test, the catalog-contract test, and the Python lint/format
   gates for changed test files before filing the post-implementation report.

## Canonical Skill Checklist

- Frontmatter opens and closes with `---`.
- Frontmatter includes non-empty `name` and `description` fields.
- The description names the trigger condition, not just the artifact type.
- The body names when to use the skill, when not to use it, required inputs,
  mandatory steps, verification evidence, and cross-harness disposition.
- Helper scripts or templates referenced from the skill are path-stable and
  resolved relative to the skill directory when appropriate.
- The body does not instruct agents to mutate retired queue artifacts or bypass
  bridge, root-boundary, credential-safety, or formal-artifact gates.

## Registry and Adapter Checklist

- The registry skill entry has a stable `skill.<slug>` capability id.
- `canonical_source` points at the `.claude` `SKILL.md`.
- `[capabilities.claude]` uses `status = "native"`.
- `[capabilities.codex]` uses `status = "adapter"`, the projected surface path,
  `adapter_source`, and the canonical normalized-body `source_sha256`.
- `.harness-baseline-configuration/skills/<slug>/SKILL.md` carries the
  `GTKB-CODEX-SKILL-ADAPTER` generated block and records the same source path
  and SHA as the manifest and registry.
- `.harness-baseline-configuration/skills/MANIFEST.json` has exactly one adapter entry for the capability
  id.
- `platform_tests/skills/test_skill_catalog_contract.py` remains green, proving
  no `SKILL.md`-bearing project skill is orphaned from the registry and every
  registered skill has a loadable Codex adapter.

## Verification Checklist

- `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --update-registry --check`
  reports no authorized-target drift after the implementation, or the
  implementation report explains unrelated pre-existing drift.
- `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_<skill_slug>_skill.py platform_tests/skills/test_skill_catalog_contract.py -q --tb=short`
  passes.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/skills/test_<skill_slug>_skill.py`
  passes.
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/skills/test_<skill_slug>_skill.py`
  passes.
- The post-implementation report carries forward specification links and maps
  each tested requirement to the executed command evidence.

## Implementation Report Evidence

The implementation report should include:

- bridge GO file and implementation-start packet hash;
- changed target paths, with any generator-scope exception called out;
- canonical/adapted skill SHA agreement across adapter, manifest, and registry;
- registry declaration and non-target harness disposition;
- focused test and catalog-contract results;
- lint and format results for changed Python tests;
- any advisory-note response from the GO verdict.

## Non-Goals

- Do not create non-Codex harness adapter files unless the active bridge target
  paths authorize them.
- Do not treat generated manifests as authoritative skill source.
- Do not use this skill to file a bridge proposal; use the bridge proposal
  workflow and helpers for proposal authoring.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
