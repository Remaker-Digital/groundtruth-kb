VERIFIED

# Loyal Opposition Verification Review: Canonical Terminology Surface Option B Implementation

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-011.md`
Verdict: VERIFIED
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The REVISED post-implementation report is verified. The submitted implementation
commit `f475c8b029fcaaaad1fce02732b649329079cd0c` is on
`feat/start-here-adopter-rewrite`, contains the registry consolidation commit
`e12aab3`, and implements the GO-008 Option B architecture: canonical
terminology artifacts are managed as registry-backed rule artifacts under
`.claude/rules/`, not as stale hard-coded `.claude/canonical-terminology.*`
files.

No blocking findings remain for this bridge item.

## Governing Review Context

The prior NO-GO at `-010` rejected the obsolete `2b4c1e9` implementation because
it implemented the GO-006 hard-coded path plan rather than the later GO-008
registry-backed Option B contract (`bridge/gtkb-canonical-terminology-surface-implementation-010.md:62`,
`:87`, `:142`-`:158`). The `-011` report explicitly supersedes that stale
implementation, submits `f475c8b`, and requests verification of the GO-008
conditions (`bridge/gtkb-canonical-terminology-surface-implementation-011.md:5`,
`:10`, `:235`-`:244`).

## Evidence

### Branch base and merge posture

- `git rev-parse --abbrev-ref HEAD` returned `feat/start-here-adopter-rewrite`;
  `git rev-parse HEAD` returned `f475c8b029fcaaaad1fce02732b649329079cd0c`.
- `git merge-base --is-ancestor e12aab3 f475c8b` returned success
  (`e12aab3_is_ancestor_of_f475c8b=yes`), discharging the `-010` branch-base
  requirement.
- `git merge-tree main f475c8b` returned only a tree hash, with no conflict
  blocks. That resolves the `-010` concern that the old implementation was not
  cleanly mergeable onto current `main`.

### Registry-backed Option B paths

- The two managed artifacts are registered in `templates/managed-artifacts.toml`
  as `rule.canonical-terminology` and `rule.canonical-terminology-config`, with
  source paths `rules/canonical-terminology.md` / `.toml`, target paths
  `.claude/rules/canonical-terminology.md` / `.toml`, all three scaffold
  profiles, all three managed profiles, and `doctor_required_profiles = []`
  (`groundtruth-kb/templates/managed-artifacts.toml:231`-`:248`).
- The doctor loads `.claude/rules/canonical-terminology.toml`
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:771`-`:784`), checks
  `.claude/rules/canonical-terminology.md`
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:890`-`:899`), and is
  integrated into `run_doctor()` immediately after `_check_rules()`
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1246`-`:1247`).
- Lifecycle-vs-enforcement taxonomy is documented in both code and docs:
  `_check_canonical_terminology()` states that scaffold/upgrade are registry
  lifecycle concerns while validity is owned by the composite doctor check
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:835`-`:847`), and the
  public reference repeats the same contract
  (`groundtruth-kb/docs/reference/canonical-terminology.md:111`-`:118`).

### Stale-path cleanup

- `git grep -n '\.claude/canonical-terminology' -- ':!CHANGELOG.md' ':!docs/archive/**'`
  returned no hits.
- `git grep -n 'memory/MEMORY.md' -- templates/` returned no hits.
- Template pointers use the new `.claude/rules/` paths, including
  `templates/CLAUDE.md:24`, `templates/MEMORY.md:8`,
  `templates/project/AGENTS.md:22`, `templates/project/AGENTS.md:86`, and
  `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md:35`.

### Tests and verification commands

Targeted GO-008 verification set:

```text
python -m pytest tests/test_managed_registry.py tests/test_doctor_registry_parity.py tests/test_no_parallel_manifests.py tests/test_scaffold_project.py tests/test_upgrade.py tests/test_scaffold_smoke.py tests/test_doctor_canonical_terminology.py -q --tb=short
92 passed, 1 warning in 20.33s
```

Full regression:

```text
python -m pytest tests/ -q --tb=short
1266 passed, 1 warning in 321.74s (0:05:21)
```

Documentation gates:

```text
python -m mkdocs build --strict
Documentation built in 1.46 seconds

python scripts/check_docs_cli_coverage.py
All documentation checks passed.
```

The only test warning was the existing ChromaDB dependency warning from
`chromadb.telemetry.opentelemetry`; it is unrelated to this bridge.

### Direct scaffold and doctor smoke check

I scaffolded fresh `dual-agent` and `local-only` projects using
`python -m groundtruth_kb project init ... --dir <empty-target>`.

Observed results:

- Dual-agent scaffold created `CLAUDE.md`, `AGENTS.md`, root `MEMORY.md`,
  `.claude/rules/canonical-terminology.md`, and
  `.claude/rules/canonical-terminology.toml`.
- Generated `AGENTS.md` had zero `memory/MEMORY.md` hits and two `MEMORY.md`
  hits.
- Local-only scaffold correctly did not create `AGENTS.md`, while creating root
  `MEMORY.md` and both canonical terminology rule artifacts.
- `python -m groundtruth_kb project doctor` reported:
  - `[OK] Canonical-terminology surface OK ... (profile: dual-agent)`
  - `[OK] Canonical-terminology surface OK ... (profile: local-only)`
  - Overall WARN only, from non-terminology environment checks.

The committed tests also cover the same contracts:
`tests/test_scaffold_project.py:102`-`:128` asserts generated `AGENTS.md` uses
root `MEMORY.md`, and `tests/test_doctor_canonical_terminology.py:49`-`:219`
covers local-only, dual-agent, dual-agent-webapp, harness-memory, config
loading, and run-doctor integration.

## Residual Notes

The GT-KB working tree is not clean: `git status --short --branch` showed
modified generated evidence/docs files, deleted evidence helper files, and
untracked coverage/site/log artifacts. These dirty files are not part of the
canonical-terminology implementation commit; `git show --name-only f475c8b`
lists the expected 19 implementation files only. The targeted and full test
runs passed in the current worktree, and the line-level implementation evidence
above is from the tracked canonical-terminology files at `f475c8b`.

No owner decision is needed for this bridge item.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-canonical-terminology-surface-implementation' -Context 3,30
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-002.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-003.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-004.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-005.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-006.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-007.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-008.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-009.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-010.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-011.md
git status --short --branch
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git log --oneline --decorate -n 8 --all
git merge-base --is-ancestor e12aab3 f475c8b
git merge-tree main f475c8b
git show --stat --oneline --decorate f475c8b
git branch --contains f475c8b --all
git branch --contains e12aab3 --all
git grep -n '\.claude/canonical-terminology' -- ':!CHANGELOG.md' ':!docs/archive/**'
git grep -n 'memory/MEMORY.md' -- templates/
rg -n "rule\.canonical-terminology|canonical-terminology\.toml|canonical-terminology\.md|doctor_required_profiles" templates/managed-artifacts.toml
rg -n "canonical-terminology|_check_canonical_terminology|run_doctor|\.claude/rules/canonical-terminology|Lifecycle vs enforcement|_check_rules" src/groundtruth_kb/project/doctor.py docs/reference/canonical-terminology.md
rg -n "canonical-terminology|MEMORY\.md|memory/MEMORY\.md|Canonical Terminology|Canonical Term Propagation Gate" templates/CLAUDE.md templates/MEMORY.md templates/project/AGENTS.md templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md templates/rules/deliberation-protocol.md docs/reference/templates.md templates/README.md docs/bootstrap.md mkdocs.yml tests/test_scaffold_project.py
rg -n "42|10|canonical-terminology|canonical-terminology.toml|prime-builder.md|load_managed_artifacts|local-only|dual-agent" tests/test_managed_registry.py tests/test_doctor_canonical_terminology.py tests/test_doctor_registry_parity.py tests/test_no_parallel_manifests.py
python -m pytest tests/test_managed_registry.py tests/test_doctor_registry_parity.py tests/test_no_parallel_manifests.py tests/test_scaffold_project.py tests/test_upgrade.py tests/test_scaffold_smoke.py tests/test_doctor_canonical_terminology.py -q --tb=short
python -m mkdocs build --strict
python scripts/check_docs_cli_coverage.py
python -m pytest tests/ -q --tb=short
python -m groundtruth_kb project init dogfood-dual --profile dual-agent --dir <empty-temp-dir>
python -m groundtruth_kb project init dogfood-local --profile local-only --dir <empty-temp-dir>
python -m groundtruth_kb project doctor
git diff --name-only
git ls-files --others --exclude-standard
git show --name-only --format='' f475c8b
```
