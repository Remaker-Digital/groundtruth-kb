# NO-GO - GT-KB Artifact Ownership Matrix Review

**Status:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-artifact-ownership-matrix-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target GT-KB HEAD inspected:** `cf29738`

## Claim

The proposal is directionally aligned with the parent structural GO, but it is
not implementation-ready. The revision must resolve the ownership policy
contradictions and make the resolver/loader contract match the live
`managed-artifacts.toml` schema before GT-KB source, template, script, or doc
changes begin.

## Verdict Rationale

Parent `bridge/gtkb-project-boundary-and-upgrade-hardening-implementation-004.md`
requires this sub-bridge to extend the existing `[[artifacts]]` records, avoid a
parallel root, state whether ownership metadata flows through the existing
managed registry dataclasses, and add tests proving registry-loader/resolver
agreement on record IDs and target paths (`:109-126`). It also requires one
sub-bridge to own the Agent Red classification report while preserving the
read-only Agent Red boundary (`:128-143`, `:152-153`).

This proposal accepts those obligations, but the proposed schema cannot be
implemented as written without guessing intent in several places. That is too
risky for the central registry/upgrade/doctor surface.

## Findings

### F1 - Blocking: `silent` policy is internally contradictory

**Evidence**

- The proposal defines `adopter_divergence_policy = "silent"` as "ONLY for
  `transient` upgrade_policy" at
  `bridge/gtkb-artifact-ownership-matrix-001.md:104`.
- Two lines later it states an impossible invariant:
  `upgrade_policy = "silent"` is only valid with `ownership = "gt-kb-managed"`
  (`bridge/gtkb-artifact-ownership-matrix-001.md:107-108`). `silent` is not one
  of the proposed `upgrade_policy` enum values.
- The proposal's own sibling-map examples then set
  `adopter_divergence_policy = "silent"` on `bridge/**/*.md`, `memory/**/*.md`,
  and `webapp/**`, all with `upgrade_policy = "preserve"`, not `transient`
  (`bridge/gtkb-artifact-ownership-matrix-001.md:146-164`).
- The test catalog repeats the field mismatch by asserting rows with
  `upgrade_policy='silent'` must have `ownership='gt-kb-managed'`
  (`bridge/gtkb-artifact-ownership-matrix-001.md:270`).
- Open Question 4 describes a different invariant again:
  `adopter_divergence_policy='silent'` requires `ownership='gt-kb-managed'`
  (`bridge/gtkb-artifact-ownership-matrix-001.md:386-388`), which would reject
  the proposal's adopter-owned examples.

**Risk / impact**

The loader cannot enforce all of these rules simultaneously. An implementation
could either reject valid adopter-owned preserve rows, silently weaken the
invariant, or ship tests that assert the wrong enum field.

**Required action**

Revise the policy matrix so there is one machine-checkable invariant. At
minimum:

- Remove any reference to `upgrade_policy = "silent"` unless `silent` is added
  as an actual upgrade policy.
- State whether `adopter_divergence_policy = "silent"` is valid for
  `preserve` rows. If yes, the text must stop saying it is only for
  `transient`.
- Update example rows and tests to match the final invariant.

### F2 - Blocking: loader/resolver agreement is specified against non-existent registry fields

**Evidence**

- The live registry uses `template_path` and `target_path` for file artifacts,
  not `src` and `dest`. Examples:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\managed-artifacts.toml:29-30`,
  `:38-39`, `:47-48`.
- `managed_registry.py` defines `FileArtifact.template_path` and
  `FileArtifact.target_path` at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\managed_registry.py:75-76`
  and validates those fields as required keys at `:140-143`.
- A TOML parse of the inspected target repo returned:
  `records 40`, `src_keys 0`, `dest_keys 0`,
  `template_path_keys 28`, `target_path_keys 28`.
- The proposal says existing fields include `src`, `dest`, and `condition`
  (`bridge/gtkb-artifact-ownership-matrix-001.md:66`), says the sibling map
  uses `path_glob` instead of `src`/`dest`/`template` (`:119`), and defines the
  agreement test as `classify_path(dest)` for rows with `src`/`dest` (`:254`).

**Risk / impact**

The F3 parent condition is specifically about agreement on record IDs and target
paths. As written, the proposed agreement tests would either skip the actual
registry fields or require an adapter whose behavior is not specified.

**Required action**

Revise all schema and tests to use the live field names:

- File records: `template_path` and `target_path`.
- Settings-hook-registration records: `target_settings_path` plus
  `event`/`hook_filename`; the live registry has 11 such rows
  (`templates/managed-artifacts.toml:294-395`).
- Gitignore-pattern records: `pattern` and `comment`; the live registry has one
  such row (`templates/managed-artifacts.toml:406-408`).

The revision must define how every existing row gets an ownership target key.
For example, `.claude/settings.json` registrations cannot all collapse into one
path without an explicit rule for duplicate target paths and per-hook record
identity.

### F3 - Blocking: sibling `path_glob` records do not fit the current loader contract

**Evidence**

- The existing loader requires every `[[artifacts]]` row to contain common keys
  `class`, `id`, `initial_profiles`, `managed_profiles`, and
  `doctor_required_profiles`
  (`src/groundtruth_kb/project/managed_registry.py:137-143`).
- The existing parse dispatcher rejects records whose `class` is missing or not
  one of the known artifact classes
  (`src/groundtruth_kb/project/managed_registry.py:312-328`).
- The proposed `templates/scaffold-ownership.toml` examples contain `id`,
  `path_glob`, ownership fields, and notes, but no `class` or lifecycle profile
  axes (`bridge/gtkb-artifact-ownership-matrix-001.md:128-171`).
- The proposal simultaneously requires a "single loader extended; no parallel
  parser" (`bridge/gtkb-artifact-ownership-matrix-001.md:197-207`).

**Risk / impact**

Pointing the current `_parse_record` path at the proposed sibling file would
raise `InvalidArtifactRecord` before the resolver can classify anything. Adding
a second raw-TOML parser would violate the stated F3 design goal. The bridge
needs to specify the extension point, not leave it to implementation drift.

**Required action**

Revise the loader design to define exactly how sibling ownership records are
parsed under the same `[[artifacts]]` root. Acceptable options include:

- Add an explicit new artifact class, such as `ownership-glob`, with required
  fields including `path_glob` and ownership metadata.
- Or add a documented ownership-record parse branch in the existing loader that
  recognizes `path_glob` rows and keeps them out of scaffold/upgrade copy
  helpers unless intentionally included.

In either case, require tests proving existing `artifacts_for_scaffold`,
`artifacts_for_upgrade`, and `artifacts_for_doctor` behavior does not regress
for the current 40 managed records.

### F4 - Medium: Agent Red classification path is not explicit enough for a manifestless target

**Evidence**

- Agent Red currently has no `groundtruth.toml`; `gt project upgrade --dry-run`
  from the inspected GT-KB checkout returns only:
  `[SKIP] groundtruth.toml - No [project] manifest found - run `gt project init`
  first`.
- `gt project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"`
  exits non-zero and reports `[FAIL] groundtruth.toml not found - run
  `gt project init` first`.
- The CLI auto-detects the profile from `groundtruth.toml` and falls back to
  `local-only` when the manifest is absent
  (`src/groundtruth_kb/cli.py:660-675`), while `run_doctor()` still always adds
  `_check_groundtruth_toml(target)` and `_check_db_schema(target)`
  (`src/groundtruth_kb/project/doctor.py:1120-1152`).
- The proposal says the resolver is expected to classify files without requiring
  the manifest (`bridge/gtkb-artifact-ownership-matrix-001.md:42-44`) and also
  proposes a one-shot report script
  (`bridge/gtkb-artifact-ownership-matrix-001.md:328-331`).

**Risk / impact**

Without a clear classification-only command path, implementation may either
weaken `doctor` by making missing manifests non-failing, or generate the report
through a script while leaving the proposed doctor dogfood path unverified.

**Required action**

Specify one of these in the revision:

- A dedicated manifest-optional classification command/script that is the
  canonical Agent Red report generator, while `doctor` continues to fail normal
  readiness on missing `groundtruth.toml`.
- Or a `doctor` mode/section that classifies files without suppressing the
  existing required manifest failure.

The post-implementation report must include a before/after `git status --short`
or equivalent proof that Agent Red files were not modified.

## Open Question Responses

1. `shared-structured` does not need to split at the ownership enum level if
   `upgrade_policy` unambiguously distinguishes `structured-merge` from
   `preserve`. The current policy contradiction must be fixed first.
2. Do not require weekly CI regeneration of the Agent Red report unless CI has a
   pinned, available Agent Red checkout. Prefer manual or release-time
   generation with recorded GT-KB HEAD and Agent Red HEAD until Mike decides
   otherwise.
3. Use an explicit priority field for overlapping `path_glob` records. Longest
   literal prefix is useful as a default tie-breaker, but an explicit priority
   is easier to audit and test.
4. The `silent` invariant needs revision per F1.

## Command Evidence

Commands run from `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb` unless
noted:

```text
git rev-parse --short HEAD
cf29738

git status --short --branch
## feat/da-harvest-coverage
?? .groundtruth-chroma/
?? .implementation-log-harvest-coverage.md
?? groundtruth.db-shm
?? groundtruth.db-wal

python -c "<parse templates/managed-artifacts.toml>"
records 40
ownership_count 0
workflow_targets_count 0
src_keys 0
dest_keys 0
template_path_keys 28
target_path_keys 28
classes ['gitignore-pattern', 'hook', 'rule', 'settings-hook-registration', 'skill']

python -c "<count non-file registry targets>"
target_settings_path_keys 11
pattern_keys 1
target_id_values_without_target_path ['settings.hook.session-start-governance.sessionstart', 'settings.hook.assertion-check.sessionstart', 'settings.hook.delib-search-gate.userpromptsubmit'] ... total 12

python -m groundtruth_kb project upgrade --dry-run --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
[SKIP] groundtruth.toml - No [project] manifest found - run `gt project init` first

python -m groundtruth_kb project doctor --dir "E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement"
Overall: [FAIL] FAIL
Required tools missing:
  - groundtruth.toml: groundtruth.toml not found - run `gt project init` first
```

Commands run from
`E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
git ls-files groundtruth.db requirements-local.txt requirements-test.txt
groundtruth.db
requirements-local.txt
requirements-test.txt

git status --short -- groundtruth.db requirements-local.txt requirements-test.txt
 M groundtruth.db
 M requirements-local.txt
 M requirements-test.txt

rg -n "groundtruth-kb|v0\.2\.1" requirements-local.txt requirements-test.txt
requirements-local.txt:17:groundtruth-kb[web,search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
requirements-test.txt:49:groundtruth-kb[search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.1
```

## Required Action Items For Prime

1. File `bridge/gtkb-artifact-ownership-matrix-003.md` as a revised proposal.
2. Resolve the `silent` policy/invariant contradiction and update the examples
   and tests accordingly.
3. Rewrite the registry agreement contract against the live schema:
   `template_path`/`target_path`, `target_settings_path`, and
   `gitignore-pattern` `pattern`.
4. Define the sibling `path_glob` loader extension in enough detail that it can
   be implemented without a parallel parser and without breaking current
   `artifacts_for_*` behavior.
5. Specify the manifest-optional Agent Red classification route and preserve
   the zero-write Agent Red boundary.

