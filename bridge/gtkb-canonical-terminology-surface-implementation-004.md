NO-GO

# Loyal Opposition Review: Canonical Terminology Surface Implementation REVISED-1

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-003.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The revised bridge materially improves the prior version: it moves direct Agent
Red edits out of scope, confirms the epistemic distinction between MemBase,
Deliberation Archive, and MEMORY.md, adds `templates/project/AGENTS.md` to the
startup-visible propagation plan, drops the false doctor content-hash claim, and
clarifies alias treatment for `Knowledge Database` and `GT-KB`.

I still cannot issue GO because the revised implementation plan does not yet
define a coherent, testable MEMORY.md path migration across GT-KB scaffold,
bootstrap, upgrade, doctor, and docs. The proposal pins `memory/MEMORY.md`, but
the current product still creates and documents root `MEMORY.md` in multiple
entrypoints. The proposed dogfood command also uses the wrong CLI surface.

## Prior Deliberations

I verified the two new deliberation references cited by the revised bridge:

- `DELIB-0715` exists and records the owner settlement that MemBase is
  authoritative curated project truth, the Deliberation Archive is evidentiary,
  and MEMORY.md is an operational notepad.
- `DELIB-0719` exists and records the owner decision for a repo-tracked
  `memory/MEMORY.md`, ERROR/WARN terminology doctor severity, separate DA
  harvest scope, Mermaid-only diagrams, curated MEMORY.md migration, and
  CLAUDE.md explicit pointer auto-load.

No retrieved deliberation supersedes the revised bridge, but `DELIB-0719`
raises the implementation bar: the path change must be handled as a real
product migration, not only as terminology text.

## Findings

### P1 - `memory/MEMORY.md` is pinned, but the implementation plan does not migrate the scaffolded MEMORY.md target

The revised proposal pins the canonical adopter MEMORY.md location to
repo-tracked `memory/MEMORY.md` (`-003.md:23`, `:31`) and makes the doctor
profile require `memory/MEMORY.md` for dual-agent projects (`-003.md:77`-`:93`).
Its dogfood evidence likewise asserts `memory/MEMORY.md` exists and contains the
glossary (`-003.md:166`-`:169`, `:193`-`:201`).

Current GT-KB behavior does not create that file. `scaffold_project()` always
copies base templates for all profiles (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:91`-`:92`),
and `_copy_base_templates()` copies `templates/MEMORY.md` to root `MEMORY.md`
(`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:168`-`:178`). The
desktop bootstrap path does the same (`groundtruth-kb/src/groundtruth_kb/bootstrap.py:134`-`:138`)
and renders placeholders in root `MEMORY.md`
(`groundtruth-kb/src/groundtruth_kb/bootstrap.py:215`-`:224`). Public docs still
tell users that `templates/MEMORY.md` copies to root `MEMORY.md`
(`groundtruth-kb/docs/reference/templates.md:11`-`:15`,
`groundtruth-kb/templates/README.md:24`-`:28`, `:54`-`:57`).

The revised phase plan only says to update `templates/MEMORY.md` text
(`-003.md:139`-`:144`) and to add scaffold/upgrade support for the two
canonical-terminology files (`-003.md:146`-`:148`). It does not say to change
the MEMORY.md copy target, create `memory/`, migrate existing root MEMORY.md,
leave a root stub, update bootstrap-desktop, update summary text, or update the
template-reference docs.

Impact: implementation as proposed can pass text edits while a fresh scaffold
still lacks `memory/MEMORY.md`, causing the proposed doctor/dogfood contract to
fail. Worse, adopters would receive conflicting startup instructions across
`AGENTS.md`, `CODEX-SESSION-BOOTSTRAP.md`, root `MEMORY.md`, and docs.

Required action: explicitly choose and document the file-layout contract. If
the owner-settled target is `memory/MEMORY.md`, the revised plan must include
scaffold, bootstrap-desktop, upgrade migration, docs, summary output, startup
bootstrap, and tests for that target. If a root compatibility stub remains,
specify its content and doctor behavior.

### P1 - The doctor/profile matrix is not defined for GT-KB's actual scaffold profiles

The proposal adds the canonical files in `_copy_base_templates()` (`-003.md:48`),
which would affect every scaffold profile because `_copy_base_templates()` runs
before the dual-agent branch for all profiles
(`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:91`-`:96`). GT-KB has
three actual project profiles: `local-only`, `dual-agent`, and
`dual-agent-webapp` (`groundtruth-kb/src/groundtruth_kb/project/profiles.py:23`-`:60`).
The CLI default for `gt project init` is `local-only`
(`groundtruth-kb/src/groundtruth_kb/cli.py:565`-`:571`).

The revised terminology TOML sketch defines `default`, `dual-agent`, and
`harness-memory` profiles (`-003.md:76`-`:100`) but does not define how
`local-only` and `dual-agent-webapp` map into those terminology profiles.
This matters because local-only projects intentionally do not create
`AGENTS.md` (`groundtruth-kb/tests/test_scaffold_project.py:63`-`:77`), while
existing smoke coverage expects local-only doctor not to fail
(`groundtruth-kb/tests/test_scaffold_smoke.py:82`-`:89`).

Impact: a clean local-only scaffold can receive `.claude/canonical-terminology.toml`
but fail terminology checks because it lacks `AGENTS.md` or the new
`memory/MEMORY.md` path. Conversely, `dual-agent-webapp` could silently miss the
stricter dual-agent requirements if the checker falls back to `default`.

Required action: add a profile matrix before implementation:
`local-only`, `dual-agent`, `dual-agent-webapp`, and `harness-memory` must each
state required files, optional files, missing-file severity, startup term
requirements, and tests. The existing local-only no-AGENTS contract must either
remain passing or be explicitly changed with owner approval and docs.

### P1 - The proposed dogfood command uses the wrong CLI surface

The revised plan says to scaffold via `gt init --profile dual-agent`
(`-003.md:166`-`:168`, `:193`-`:196`). The current top-level `gt init` command
accepts only `project_name` and `--dir`
(`groundtruth-kb/src/groundtruth_kb/cli.py:82`-`:87`). The profile-aware scaffold
command is `gt project init PROJECT_NAME --profile dual-agent`
(`groundtruth-kb/src/groundtruth_kb/cli.py:565`-`:613`).

Impact: the post-implementation dogfood transcript cannot run as written. This
is the exact evidence path the bridge proposes to prove that the new templates,
doctor check, and glossary files work together.

Required action: replace the dogfood command sequence with the actual CLI
surface, including a project name and `--dir` if the temp directory should be
the project root. Add the corrected command to the post-implementation evidence
requirements.

### P2 - Documentation propagation omits navigation and existing template references

The revised plan adds `docs/reference/canonical-terminology.md` and runs
`python -m mkdocs build --strict` (`-003.md:161`-`:163`, `:189`-`:191`), but it
does not list a `mkdocs.yml` navigation update. Current `mkdocs.yml` enumerates
Reference pages explicitly and does not include a canonical terminology page
(`groundtruth-kb/mkdocs.yml:43`-`:48`). Existing template docs also still say
`templates/MEMORY.md` copies to root `MEMORY.md`
(`groundtruth-kb/docs/reference/templates.md:11`-`:15`,
`groundtruth-kb/templates/README.md:24`-`:28`).

Impact: the new reference page may be omitted from the published docs nav, and
the MEMORY.md target change may be contradicted by reference docs even if code
changes are implemented.

Required action: include `mkdocs.yml` nav and existing template-reference docs
in the propagation list, or explicitly state why `mkdocs --strict` plus docs
coverage makes them unnecessary.

## Required Conditions For Revised Proposal

- Add a complete `memory/MEMORY.md` migration plan covering `gt project init`,
  `gt bootstrap-desktop`, `gt project upgrade`, doctor, docs, summary output,
  startup bootstrap files, and compatibility behavior for root `MEMORY.md`.
- Define the terminology doctor profile matrix for `local-only`, `dual-agent`,
  `dual-agent-webapp`, and `harness-memory`, with expected missing-file
  severities and tests.
- Correct the dogfood command sequence to use `gt project init`.
- Add docs/navigation propagation for the new canonical terminology reference
  and for any MEMORY.md path change.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Select-String -Path bridge/INDEX.md -Pattern 'gtkb-canonical-terminology-surface-implementation' -Context 20,80
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-002.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-003.md
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0715
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; $env:PYTHONIOENCODING='utf-8'; python -m groundtruth_kb deliberations get DELIB-0719
rg --files src/groundtruth_kb/project templates tests docs scripts
rg -n "MEMORY\.md|memory/MEMORY\.md|target / \"MEMORY\.md\"" src templates tests docs -S
Line-number reads of groundtruth-kb scaffold.py, bootstrap.py, cli.py, profiles.py, templates/CLAUDE.md, templates/MEMORY.md, templates/project/AGENTS.md, docs/reference/templates.md, templates/README.md, and tests.
```

No product tests were run because this is still a pre-implementation proposal
review.
