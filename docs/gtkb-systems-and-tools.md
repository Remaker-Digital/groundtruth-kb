# GT-KB systems and tools

This index points to the current CLI, authoritative domain records and authored
configuration sources. Read current state through the selected authority before
acting. The index is a navigation aid and carries no independent authority.

## Authority and work

PostgreSQL behind the native CLI and versioned service APIs holds current domain
state. Ordinary commands use the configured authority endpoint and fail visibly
when it is unavailable. A local database file, generated report or remembered
observation cannot supply fallback authority.

A program expresses a plan and sequence. A project groups work that completes
and commits together. Each work item belongs to one project. Project
reconciliation, current authorization, dependencies, evidence, review and commit
state are separate facts; inspect the current record and readiness results for
the operation at hand. A queue observation does not assign work to an agent.

Every execution project selects one repository explicitly: `platform` or
`application:<catalog-name>`. Application references resolve through the host's
application catalog to an independent Git repository. Programs sequence projects
and have no repository association. Use `gt projects show` to inspect the
reference and `gt projects list --repository-ref application:<catalog-name>` to
find projects for that repository. Work and results still use the one authority.
Project and context worktrees live in the host workspace; finalization changes
only the selected repository and requires its installed reference-transaction hook.

Use `gt application register <name> --host-root <platform-checkout> --json`
to add an application to that host's catalog and create its matching
`application.toml` marker. Multiple applications are supported. Registration
preserves existing application files, comments and catalog metadata; a repeated
registration reports `already_registered` with no changed paths. A malformed
catalog, conflicting marker or differently cased registered name is refused
with the reason shown. Reconcile those existing inputs before retrying.

Registration supplies the `application:<name>` reference used for project
routing and specification/TEST scope. Initialize the application's independent
Git repository and install its reference-transaction hook before finalization.
Canonical specifications, tests and work continue to use the shared authority.

| Subject | Current interface or source | Boundary |
| --- | --- | --- |
| Programs and projects | `gt projects list`, `gt projects show` | Read kind, relationships and current project state from the domain service. |
| Work items | `gt backlog list`, `gt backlog show` | Canonical work records and their project relationships. |
| Task context | `gt context work-item` | Current declared work, project, program, formal, test, phase and predecessor links; complete semantic context and actual-host startup disclosure still require qualification. |
| Formal requirements | `gt spec list`, `gt spec show` | Current status and version determine applicability; retain formal history. |
| Specification coherence | `gt validate spec-coherence --output <directory>` | One native read-only snapshot of active specifications; emits surface, parent-hierarchy and timestamp review candidates, never a verdict or complete applicability result. |
| Terminology | `gt terms list`, `gt terms show`, `gt authority` | Resolve current canonical terms through the service. |
| Tests and plans | `gt tests`, `gt test-plans`, `gt test-phases` | Keep executable bindings, planned coverage and observed execution results distinct. |
| Session attribution | `gt session bind`, `gt session show` | Exact native-context identity resolves one immutable binding, subject and role. No installation-based role assignment or current-context fallback. |
| Startup context | `gt context session --native-context-id <actual-id>` | Read-only binding, three current startup formal sources and two authored baseline rules from the service-selected root. Missing inputs fail visibly; receiving-host activity, tools, hook execution and tokens remain unavailable to this service. Bounded source loading does not qualify actual-host startup or complete semantic closure. |
| Bridge | `gt bridge state-report`, `gt bridge queue`, `gt bridge show` | Canonical coordination with disposable authored messages; claims apply to the exact next artifact, not a whole work item. |
| Installation metadata | `gt harness list`, `gt harness show`, `gt harness record` | Explicit version-checked registration and updates; new installations start registered. Identity and declared invocation/capability metadata do not establish a session role or runtime qualification. |
| Harness diagnostics | `gt harness diagnostic` | Native metadata and an explicitly selected context; measured runtime parity remains unqualified until separately demonstrated. |
| Baseline configuration | `.harness-baseline-configuration/` | Harness-neutral authored input. Derive complete output with `gt harness project`; do not edit generated harness directories. |
| Domain service | `gt service` | Inspect readiness through the CLI; operational changes are separate from read-only diagnostics. |
| Dashboard | `gt dashboard` | Derived observations from the selected sources. Unavailable or unmeasured values do not establish health. |
| Local repository inspection | `gt hygiene`, `gt commit` | Local Git observations; these do not confer project authorization or independent verification. |

`gt test-phases record` applies a version-checked native amendment. A semantic
change to its `test_ids` set clears the phase's stored result and execution date
in the same transaction as the membership change. Omitted or set-identical
membership preserves existing evidence. The request rejects caller-supplied
execution fields; editing a phase cannot assert that its tests ran. Current-row
and history changes roll back together on failure, while earlier history stays
unchanged. This write-side rule does not reconcile pre-existing stale results
or provide an execution-result recorder.
| Runtime tools | The active session's tool and skill inventory | Availability is observed in that context. It does not assign its role or authorize project work. |

Use each command's `--help` for its current arguments. Domain changes go through
version-checked writers; read back the resulting canonical state. A successful
read, diagnostic, assertion lookup or focused test does not establish complete
realignment or actual-host acceptance.

### Existing PostgreSQL schema transition

Ordinary `gt db postgres init` initializes an empty selected schema and refuses
drift in an existing one. During the planned installation, after backing up the
authority and stopping its writers, select the operator configuration and use
`gt --config <operator-config> db postgres init --upgrade-from <schema-sha256>`
for the supported predecessor reported by `gt service status --json`.
The supported predecessor is
`2f25071544591b01b44e0da491a19bd9adee509627114a4dad528205a8f6e2ca`.
The command does not stop services, choose a database, or grant permission for
installation; the selected configuration and the existing installation gate apply.

The explicit transition adds the nullable project repository reference and
generalizes the specification/TEST application-scope constraints. It preserves
current rows, versions and history. Existing project references remain null for
explicit reconciliation; it never infers platform or application membership.
Current retired scope markers cause a refusal identifying the affected records,
which must be reconciled through their existing writers before transition.

The table locks, DDL and existing schema-metadata update run in one transaction
under the configured time limits. Failure preserves the predecessor; a repeated
successful invocation reports `already_current`. Unknown or drifted catalogs
are refused. Verify readiness and the reported unresolved project count before
restarting the service on the matching installed package. Fresh-database and
existing-database behavior are covered by the complete schema-transition tests;
the production restore rehearsal and installation require their own evidence.

The coherence command keeps its rule-ID filter (`--rule-set`), JSON/Markdown/both
formats and optional exit 5 on findings (`--fail-on-findings`). Select an explicit
output directory. Its existing rules come from the selected project's
`config/governance/spec-coherence-rules.toml`; malformed rules or unavailable
authority fail before reports are written. It reads the full active corpus from
`/v1/specifications/snapshot` in one database transaction, including exact current
versions. Reports are observations of that snapshot, not live authority. No local
database override, implicit state directory, record mutation or status promotion
exists. A dependency in `affected_by` is not a parent; surface candidates require
the same configured surface on both records. A clean candidate report does not
establish semantic consistency, formal coverage or independent review.

## Bounded launch probes

`scripts/verify_claude_dispatch.py`, `scripts/verify_codex_dispatch.py` and
`scripts/verify_cursor_dispatch.py` read
one exact native installation record from the explicitly selected project
configuration. They preserve launch checks and optional `--live` prompt probes.
Cursor also checks authentication; its credential helper reads that selected
root without copying parsed credentials into the caller's environment.
Missing authority or malformed input
fails before launch; the retired registry projection supplies no fallback.

Their `probe_passed` field describes only the requested checks. Reports name the
probe scope and leave `harness_qualification` as `unqualified`; they carry no
role or dispatchability claim. Prompt contents, arbitrary auth responses and
command argument lists are omitted from reports. Complete host qualification
still includes the required fresh/successor context, tool, hook, bridge and
review-independence scenarios.

The Codex probe performs ACL inspection in Check mode only. Repairs remain
explicit operator operations through `scripts/repair_codex_dotdir_acl.ps1`.
It does not read old cached qualification files, and a passing prompt result
does not establish model/profile conformance, permissions or window behavior.
Those require actual behavioral qualification against the active baseline,
model profile and adapter. The probe is not another source of model settings.

`scripts/verify_ollama_dispatch.py` reads the selected native installation and
provider-specific routing. Its optional advertised-model HTTP check establishes
neither model execution nor account eligibility. It compares the requested tag
exactly, using `latest` when the tag is omitted, as defined by the
[Ollama model-name contract](https://github.com/ollama/ollama/blob/main/docs/api.md#model-names).
The diagnostic has no mocked live mode, bridge-filing fixture or role-promotion
caller. Provider runtime and native CLI tests cover those behavioral obligations;
actual-host qualification remains required.

The older startup generator and remaining file-role helpers still require
reconciliation. The advisory counter contract and specification-event hook are
retired. The ordinary startup route is the native session/context interface;
fresh native reporting and useful unavailable-state diagnostics remain required.
Dispatcher Next activation and ordinary resumption remain separate milestones.

The package initializer and shared environment loader preserve the caller's
environment and Git configuration on import. Environment loading is an explicit
operation, with setdefault, override and check-only modes. Fresh-process tests
cover the public package, loader and four diagnostic entry points under absent
and preselected settings; real Git reads check system and XDG configuration
selection. These tests do not establish actual-host or provider qualification.

The retired projection-to-SQLite harness seeder is removed. Register an explicitly
selected installation through `gt harness record` using the current expected
version and read back the canonical row. Registry-file contents never supply
roles or activation state. A repeated stale create is refused; it cannot silently
replace an existing record. The broader role-free registry specification and its
unreconciled TEST carriers, actual-host qualification and SDK activation remain
open. No file-backed seeding or projection regeneration is a startup requirement.

The registered-path read guard uses the selected project's current registry and
each harness's own projected hook. It resolves relative reads from the event cwd
and handles nested provider hook directories without choosing a neighbouring
harness. The existing projection conformance diagnostic covers generated files,
registrations and adapters; the redundant vendor-pair read-hook diagnostic is
removed. Explicit test registries exercise restrictions even when the live
registry has none. The guard does not prove canonical currentness, arbitrary
shell coverage, native host invocation or complete TEST-12284 equivalence.

The legacy bridge-content harvester, its private warning baseline, bridge
backfill inventory and archive-population health command are removed. Their
baseline health skill is removed at the source; the native projector owns
removal of managed generated copies. A bridge payload is ephemeral coordination,
not content to copy into a knowledge archive. On explicit close/wrap, harvest
adequately defined facts through their existing canonical domain writers and
read back each operation. Report a failure or incomplete sequence visibly;
neither a historical warning baseline nor a prior result makes it successful.
No replacement archival command or harvest service is introduced.

This removal does not purge historical rows or retire independent knowledge
redaction, search, design-inspection or application obligations. Legacy data
helpers and historical one-off scripts are not current native authority. Full
scoped harvest, scratch lifecycle, fresh/successor actual-host behavior and
independent realignment acceptance remain required.

Scaffold golden fixtures are test inputs generated by
`groundtruth-kb/scripts/_capture_scaffold_golden.py` using the selected package
runtime. Run it with that runtime's source or installed package environment.
It generates in a fresh disposable directory under the fixture root, preserves
existing host applications, and replaces a selected fixture only after complete
generation and copying. A failed publication restores the previous fixture.
The local-only and dual-agent comparisons use independent temporary directories;
their stable project names describe fixture content rather than shared workspaces.
Only the documented creation timestamp is normalized for byte comparison, and
the generated SQLite database remains excluded from the text fixtures.

These checks cover the existing scaffold library's current output. They do not
restore the missing ordinary adopter initialization CLI, reconcile its host-root
selection, waive its placement and overwrite checks, or qualify an actual host.
Live harness projections still come only from the canonical baseline/projector.

Use `gt --config <selected-project>/groundtruth.toml harness project <harness>`
to refresh a supported profile, with `--dry-run` to inspect its paths and
`--check` to verify its generated output. Retirement uses the previous generated
manifest or the profile's explicit leftover list. Claude's retired archive-health
skill and advisory hook are removed even where its old manifest is absent. Codex's
empty old command registry and obsolete plugin hook registration are also removed;
the latter pointed into another harness's tree. Neighboring files and Codex's
local runtime configuration remain intact. Unmanaged configuration is reported by
the conformance diagnostic and still requires reconciliation; a clean managed-file
check does not waive it. Refreshing a provider's configuration does not retire the former
generic `.api-harness` tree. That tree has no current profile and requires a
separately supported cleanup route. Projection conformance does not establish
actual-host behavior or activate a harness installation.

The retired specification-event hook is absent from the baseline, package
templates and supported projections. Upgrade removes its exact former managed
registration while preserving custom commands and mixed hook-group metadata.
No replacement event ledger or renamed counter contract is introduced. Native
advice, queue, claim and project observations retain their separate contracts.

### Native runtime configuration projection

The selected adaptation profile may declare `config_toml` in
`scripts/harness_projection/profiles.toml`. The sole projector validates that
TOML, substitutes declared neutral tokens, adds its derivation notice and writes
`<selected config_dir>/config.toml` through `gt harness project <name>`. The file
participates in the existing managed-output manifest and exact conformance
checks. Wrong input types, invalid TOML and unresolved tokens refuse application
before any output changes. Existing generated configuration supplies no desired
values; edit the canonical profile and regenerate.

The Codex profile carries the existing project settings: `on-request`,
`danger-full-access`, hooks enabled, shell snapshots disabled and
`sandbox_workspace_write.network_access=false`. The network setting applies to
workspace-write mode, so it does not prove networking is disabled in the selected
full-access mode. Host policy and explicit runtime overrides still apply. See
the [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
Projection conformance does not establish native host loading or actual-host
workflow qualification.

### Selected specification test execution

Run `python scripts/run_spec_derived_tests.py --config <project>/groundtruth.toml
--work-item WI-NNNN --json`, or use repeatable `--spec` arguments to select current
requirements. The existing authority client reads current work context, formal
records and every page of linked TEST definitions. No bridge history, local
SQLite file, stored test result or waiver supplies a passing result.

Discovery combines registered file/class/function selectors with module-level
specification citations in `tests/`, `groundtruth-kb/tests/` and `platform_tests/`.
Missing bindings, invalid or outside-root paths, unreadable or malformed sources,
missing tests and failed authority reads are reported. Tests execute with the
selected project's pytest root. The process exit code and JUnit testcase outcomes
must agree; skips, collection errors, empty runs and timeouts cannot pass.
Selected canonical records and discovery inputs are reread after execution.
Changed inputs invalidate the report. No canonical execution history or lifecycle
state is written by this runner; selected test code still performs its own effects.

`execution_result=PASS` describes only the selected tests. The report remains
`PARTIAL`, with `verification_result=UNASSESSED` and exit 1 until complete independent
applicability and semantic review are provided by the required verification route.
Observed failures return exit 2. `--dry-run` reports discovery with no execution
claim. The old bridge, advisory and strict options are removed; a local waiver or
passing selected subset cannot establish VERIFIED. This runner does not complete
the independent duties in DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 or qualify
actual-host/fresh-context operation. Historical Agent Red TEST evidence remains
historical and is not rebound to platform tests.
