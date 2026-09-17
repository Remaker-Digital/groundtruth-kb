# CLI Reference

Complete reference for all `gt` commands. For a guided introduction, see
[Start Here](../start-here.md). For conceptual context, see
[Tooling](../method/10-tooling.md).

## Global Options

Every command inherits these options from the `gt` root group:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--version` | flag | | Show version and exit |
| `--config <path>` | path | auto-discovered | Path to `groundtruth.toml` |
| `--help` | flag | | Show help and exit |

**Config auto-discovery:** When `--config` is omitted, GroundTruth searches
upward from the current directory for `groundtruth.toml`. Relative paths
inside the config file resolve against the **config file's directory**, not
the caller's working directory.

---

## Core Commands

### Desktop bootstrap

The separate `gt bootstrap-desktop` initializer is retired. `gt project init`
is the single application initializer: it refuses a non-empty target, creates
the profile's files for an explicitly selected execution project and never
creates a local database. See [`gt project init`](#gt-project-init).

---

### gt status

Compact read-only operating status from fresh native reads. Every
component is read at the moment of the call; nothing is inferred from a
cached startup report, a local database or an inherited session, and the
report certifies no context (`certifies_context` is always `false`).

```
gt status [--json] [--startup] [--native-context-id <id>] [--component <name> ...]
```

| Component | Source | PASS / FAIL / UNKNOWN |
|-----------|--------|------------------------|
| `authority` | `GET /v1/status` | ready and reachable / not ready / unavailable (cause recorded) |
| `project` | configuration and `applications/registry.toml` | host present with its registered applications |
| `bridge` | `GET /v1/bridge/state-report` | current counts of the native bridge state |
| `registry` | `config/registry/sot-artifacts.toml` | declarations and active count / no declared registry |
| `formal` | `GET /v1/authority/status` | no ambiguities or source defects / findings present |
| `session` | `GET /v1/sessions/binding` | the named context's immutable binding; UNKNOWN unless `--native-context-id` names one |
| `dashboard` | configuration and the derived view under `.groundtruth/dashboard` (never contacted) | the project dashboard link with the derived view's presence and last published refresh timestamp / UNKNOWN when the project root has no `groundtruth.toml`; never FAIL |

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Canonical JSON envelope (`schema_version` 1) |
| `--startup` | flag | off | Compact startup text from the same collector |
| `--native-context-id` | string | | Report this native context's binding; never inferred from the environment |
| `--component <name>` | choice | all | Limit output; repeat for several; an unknown name is a usage error |

An unavailable authority yields `UNKNOWN` components with the client's
recorded cause and exit 0; it is never replaced by a local quick-check.

The `dashboard` component states the link `gt dashboard start` derives
(`http://127.0.0.1:3000/d/groundtruth-kb-dashboard/groundtruth-kb-dashboard`
with the launch's default ports) and marks it `(not contacted)`: neither
Grafana, the refresh service nor the authority is requested for it, so
reading it creates no session binding, infers no role and selects no work
(SPEC-PROJECT-DASHBOARD-KPI-LINK-001). Its evidence records the runtime
root, whether the landing page and Grafana dashboard JSON exist there, and
the `generated_at` the last refresh published to `dashboard-data.json` when
that file is well formed.

---

### Record version history (`show --history`)

Every id-domain `show` command accepts `--history`: the current record
followed by its recorded version chain, read from the authority's record
history (the kernel records every current-row change with its prior and new
version, actor, time, reason and the resulting state). History is read-only;
a missing record is `not_found`, never an empty chain.

```
gt <spec|tests|test-plans|test-phases|projects|backlog|terms|harness> show <ID> --history [--json]
```

Text output appends a `Version History:` block with one line per version
(`v<n> <changed_at> <actor>: <reason>`). With `--json` the envelope is
`{"current": <record>, "history": [...]}`, each entry carrying `version`,
`prior_version`, `actor`, `changed_at`, `reason` and the recorded `state`.

---

### gt assert

Observe current definitions from one selected authority without canonical
writes: the current specifications are read from the configured
`authority_url` and their assertions are evaluated against the project
root. No execution history is written.

```
gt assert [--spec <id>] [--triggered-by <label>] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--spec` | string | all current specs | Evaluate one current specification |
| `--triggered-by` | string | `cli` | Label this observation; no execution history is written |
| `--json` | flag | off | Emit the summary as canonical JSON |

A change of the selected authority or project root during evaluation is
refused (`assertion_configuration_changed`).

**Exit codes:**

| Code | Meaning |
|------|---------|
| `0` | `aggregate_result` is `PASS` |
| `1` | Any other aggregate result |

**Examples:**

```bash
# Run all assertions
gt assert

# Run for a single specification
gt assert --spec GOV-01

# Run with a custom trigger label (for CI pipelines)
gt assert --triggered-by github-actions
```

For the assertion language syntax, see
[Assertion Language Reference](assertion-language.md).

---

### gt config

Show resolved settings without probing services or optional dependencies.

```
gt config [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the resolved settings as JSON |

Output (text labels; JSON keys in parentheses):

- Application title (`app_title`)
- Project root (`project_root`), resolved
- Authority URL (`authority_url`); the text form reports it missing when no
  `authority_url` is configured
- PostgreSQL service, connect timeout (seconds), lock timeout (ms) and
  statement timeout (ms) (`postgresql.service`,
  `postgresql.connect_timeout_seconds`, `postgresql.lock_timeout_ms`,
  `postgresql.statement_timeout_ms`)
- Legacy helper `db_path` and `chroma_path` (`legacy_paths.db_path`,
  `legacy_paths.chroma_path`), resolved paths used only by local helpers

See [Configuration Reference](configuration.md) for the full list of
settings and resolution order.

---

### gt db postgres

PostgreSQL kernel administration and the one-way migration from a retained
SQLite snapshot: `status`, `init`, `export-current --sqlite-snapshot <FILE>`,
`import-current` and `readback-current`. The live `gt db snapshot` command,
its scheduled task and the doctor's snapshot freshness/allowlist checks are
retired (O-7 R22): a SQLite snapshot is neither a health criterion nor a
production fallback. The PostgreSQL authority is recovered from physical
backups and WAL archives.

---

## Core Specification Intake

GT-KB prompts new projects for a baseline set of core application specifications
(product identity, application type, tenancy, users/roles, data classification,
compliance, security posture, reliability posture, external integrations, AI usage,
operational/release path, and first-release non-goals); each fresh context reads the
next missing question with `gt core-specs next-question` until the baseline is captured.
Completion is derived from the current canonical specifications read through the
authority; nothing is stored between reads. A slot counts as captured only when the
owner states it or explicitly marks it not applicable (`gt core-specs answer`); an
AI-inferred candidate does not complete a slot.

New projects are enrolled by default. To opt out, pass `--opt-out-core-spec-intake`
to `gt project init`, set `GTKB_CORE_SPEC_INTAKE_OPT_OUT=1`, or add a
`[core_spec_intake]` table with `enabled = false` to `groundtruth.toml`. Non-interactive
and JSON-safe paths never emit interactive prompts.

### gt core-specs status

Report the baseline core-spec intake completion state for a project.

```
gt core-specs status (--project-id <id> | --project-name <name>) [--json] [--no-fail] [--opt-out-core-spec-intake]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--project-id` | string | — | Project id to inspect (mutually exclusive with `--project-name`) |
| `--project-name` | string | — | Exact project name; it must resolve to one execution project |
| `--json` | flag | off | Emit machine-readable JSON |
| `--no-fail` | flag | off | Report an incomplete baseline without a failing exit code |
| `--opt-out-core-spec-intake` | flag | off | Report `{"status": "disabled"}` without reading the authority |

The command exits non-zero when intake is incomplete unless `--no-fail` is given, so
it can gate CI without blocking automation when paired with `--no-fail`.

### gt core-specs next-question

Print the single next unanswered core-spec question for a project, or report that the
baseline is complete.

```
gt core-specs next-question (--project-id <id> | --project-name <name>) [--json] [--opt-out-core-spec-intake]
```

With `--json` the result carries `project`, `complete`, `slot`, `question`,
`spec_id` and `expected_version` (the last four `null` when the baseline is
complete); `--opt-out-core-spec-intake` reports `{"status": "disabled"}`.

**Examples:**

```bash
# Human-readable status
gt core-specs status --project-name "My App"

# Automation-safe JSON; never blocks
gt core-specs status --project-id PROJECT-MY-APP --json --no-fail

# The single next question to answer
gt core-specs next-question --project-name "My App"
```

### gt core-specs answer

Apply one explicit owner answer to a core-spec intake slot. The answer is
written through the specification CAS writer of the native authority; an
inference or a request needing clarification does not complete a slot.

```
gt core-specs answer --project-id <id> --slot <name> --expected-version <n> --actor <name> --reason <text> [--value <text>] [--source owner_stated|not_applicable] [--spec-id <id>] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--project-id` | string | *required* | Execution project whose intake slot is answered |
| `--slot` | string | *required* | Slot name as returned by `gt core-specs next-question` (`slot`) |
| `--value` | string | empty | The owner's stated answer; must be non-empty for `owner_stated` |
| `--source` | choice | `owner_stated` | `owner_stated` or `not_applicable`; use `not_applicable` only for an explicit not-applicable answer |
| `--spec-id` | string | derived | Slot specification ID; a different ID for a slot already bound to one is refused (`ambiguous_core_spec`) |
| `--expected-version` | integer >= 0 | *required* | Current version of the slot specification (`expected_version` from `next-question`); `0` creates it |
| `--actor` | string | *required* | Attribution recorded with the version |
| `--reason` | string | *required* | Change reason recorded with the version |
| `--json` | flag | off | Emit the canonical readback as JSON |

**Behaviour:** the current intake state is read first, then the slot
specification (handle `core-spec-intake:<project>:<slot>`, `type =
"requirement"`, `authority = "stated"`, tags `core-spec-intake`,
`project:<id>`, `slot:<name>`, `source:<source>`) is written with
`PUT /v1/specifications/<id>` carrying the expected version, actor and
reason, and the record is read back. A stale expected version is a
`cas_conflict`: re-read with `next-question` and apply the answer again
explicitly. A specification that belongs to another project or slot is
refused (`core_spec_identity_conflict`); a readback that differs from the
write result is reported as `readback_changed`. No prompt block, local
database or session progress flag is written; the next `next-question` read
derives progress from the current canonical specifications.

---

## Dashboard Commands

Generate and run the local Grafana operations dashboard. These commands are
available from the base pip package; Grafana itself remains an external local
runtime.

### gt dashboard init

Create the derived reporting data and Grafana assets (datasource and
dashboard provisioning, dashboard JSON) without starting services.

```
gt dashboard init [--schema-only] [--db-path <path>] [--runtime-root <path>] [--json]
```

`--schema-only` initializes the derived schema without collecting or
publishing data. Defaults:

- Project root: resolved from `groundtruth.toml`
- Dashboard DB: `.groundtruth/dashboard/gtkb-dashboard.sqlite`
- Grafana assets: `.groundtruth/dashboard/grafana/`
- Grafana home: `.groundtruth/tools/grafana`

### gt dashboard refresh

Refresh native observations from the selected authority and rewrite the
derived display assets; the refresh selects no work.

```
gt dashboard refresh [--probe-live] [--db-path <path>] [--runtime-root <path>] [--json]
```

`--probe-live` also reads live service, bridge and GitHub workflow
observations. Use this before showing the dashboard to an evaluator.

### gt dashboard install

Install local Grafana OSS and the `frser-sqlite-datasource` plugin.

```
gt dashboard install [--grafana-home <path>] [--skip-download] [--skip-plugin] [--json]
```

`--skip-download` requires an existing Grafana installation at `--grafana-home`.
`--skip-plugin` is for locked-down environments where the SQLite datasource
plugin is installed through enterprise tooling.

### gt dashboard start

Start the dashboard refresh service and Grafana, returning only after the
readiness checks pass.

```
gt dashboard start [--db-path <path>] [--runtime-root <path>] [--grafana-home <path>] [--grafana-port 3000] [--refresh-port 8766] [--interval-minutes 60] [--json]
```

Default dashboard URL:

```
http://127.0.0.1:3000/d/groundtruth-kb-dashboard/groundtruth-kb-dashboard
```

### gt dashboard stop

Stop the launches recorded for this runtime by `gt dashboard start`, after
checking process identity.

```
gt dashboard stop [--runtime-root <path>] [--json]
```

### gt dashboard serve

Run the dashboard refresh service in the foreground: serve the installed
display on IPv4 loopback and refresh observations from the selected native
authority on an interval. `gt dashboard start` launches the same service
(`groundtruth_kb.dashboard_service`) in the background together with Grafana;
`gt dashboard serve` runs it in the current terminal until interrupted.

```
gt dashboard serve [--db-path <path>] [--runtime-root <path>] [--port <n>] [--grafana-port <n>] [--interval-minutes <n>]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db-path` | path | resolved from config | Derived dashboard database |
| `--runtime-root` | path | resolved from config | Runtime directory holding the installed display |
| `--port` | integer (1-65535) | `8766` | Loopback port of the refresh service |
| `--grafana-port` | integer (1-65535) | `3000` | Grafana port the display links to |
| `--interval-minutes` | integer >= 1 | `60` | Minutes between scheduled refreshes |

The service binds `127.0.0.1` only and has no `--json` option because it does
not return. A setup failure (unreadable configuration, invalid paths, a port
that cannot be bound) is reported as an error and exits non-zero.

---

## Application Commands

Local inspection of a host's `applications/` catalog and slots. These
commands read the explicit host directory; they need no authority and do not
qualify application lifecycle. Registration (`gt application register`) is
listed in the [Complete Command Reference](#complete-command-reference).

### gt application inspect

Read the local application catalog, slot markers and artifact-boundary facts
of an explicit host. The explicit host selects this local inspection
independently of database configuration; native application lifecycle
qualification remains separate.

```
gt application inspect --host-root <host> [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host-root` | path | *required* | Existing host directory whose `applications/` catalog and slots are inspected |
| `--json` | flag | off | Structured diagnostics: `verdicts`, `slots_status` (per slot: `name`, `occupied`, `trigger`, `details`, `marker_check`, `dir_exists`, `registry_exists`) and `occupied_slots` |

**Behaviour:** every catalog entry and every `applications/<name>/`
directory is checked. Each finding is printed as `<severity> <verdict>:
<details>` followed by its remediation line; the verdicts are `Application
catalog invalid`, `Application slot invalid`, `Mismatched markers`, `Malformed
markers`, `Partial slot registration` and `Application registry boundary`
(severity `P1`), and `Registry drift`, `Unregistered application content` and
`Empty unregistered slot` (severity `P2`). Without findings the text output
reports how many applications passed, or that no application slots are
configured. Exit `1` when any finding is present, otherwise `0`. A host that
cannot be resolved or read is refused before inspection.

---

## Project Commands

Native application initialization, diagnostics, upgrade and derived cache
commands. Every command reads the selected authority (`authority_url` in the
selected `groundtruth.toml`); none creates a local database, a commit or a
canonical record unless the option says so.

### gt project init

Create the files of an explicitly selected application project under a GT-KB
host. The application must be registered (`gt application register`) and the
execution project must carry `repository_ref = application:<name>`.

```
gt --config <host>/groundtruth.toml project init <APPLICATION> --project-id <PROJECT> --host-root <host> --owner <owner> [options]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `APPLICATION` | argument | *required* | Registered application slot name |
| `--project-id` | string | *required* | Execution project with the application repository reference |
| `--host-root` | path | *required* | GT-KB host that registers the application |
| `--profile` | choice | `local-only` | `local-only`, `dual-agent` or `dual-agent-webapp` |
| `--owner` | string | *required* | Organization or owner name |
| `--copyright` | string | | Copyright notice written into created files |
| `--cloud-provider` | choice | `none` | `azure`, `aws` or `gcp` infrastructure stubs (webapp profile only) |
| `--harness` | string (repeatable) | | Configuration profiles projected from the host baseline; a harness selects no agent role |
| `--include-ci / --no-include-ci` | flag | `--include-ci` | Profile-tiered CI workflows (minimal / standard / full) |
| `--seed-example / --no-seed-example` | flag | `--no-seed-example` | Example `src/tasks.py` and its tests |
| `--integrations / --no-integrations` | flag | `--no-integrations` | Dependabot and CodeRabbit files |
| `--python-version` | string | `3.11` | Python version used in generated CI workflows |
| `--spec-scaffold` | choice | | Write `minimal` (4) or `full` (6) inferred starter specifications for the project |
| `--opt-out-core-spec-intake` | flag | off | Disable core specification intake for this application |
| `--dry-run` | flag | off | Preview the file set and starter specifications without effects |
| `--json` | flag | off | Machine-readable result |

The result reports the created paths, the projected paths, the starter
specifications written (`canonical_writes`), and the current intake question
read **after** creation (`initial_question`, `intake`). When that later read
fails, the created files are still reported truthfully with `intake.status =
"unavailable"` and a warning; run `gt core-specs next-question` afterwards.
No commit is created (`commits = 0`). Generated CI workflows run linting and
tests on hosted runners; specification assertions (`gt assert`) run where the
authority is reachable.

**Examples:**

```bash
# Preview a local-only application
gt --config E:/GT-KB/groundtruth.toml project init Alpha --project-id PROJECT-Alpha --host-root E:/GT-KB --owner "Acme" --dry-run --json

# Create a webapp application with Claude and Codex configuration and starter specifications
gt --config E:/GT-KB/groundtruth.toml project init Alpha --project-id PROJECT-Alpha --host-root E:/GT-KB \
  --owner "Acme" --profile dual-agent-webapp --harness claude --harness codex --spec-scaffold minimal
```

---

### gt project doctor

Inspect an initialized application against the authority: configuration,
installed native commit hook, core specification intake, platform leakage and
the derived search cache.

```
gt project doctor --project-id <PROJECT> --host-root <host> [--json]
```

| Exit code | Meaning |
|-----------|---------|
| `0` | No failing check (warnings, such as open intake, are reported) |
| `1` | A check failed or the application could not be inspected |

---

### gt project upgrade

Bring managed application files forward from the host baseline: the native
reference-transaction hook and the projections of the harnesses already
present (or selected with `--harness`). Application-owned files are never
touched.

```
gt project upgrade <APPLICATION> --project-id <PROJECT> --host-root <host> [--harness <name>]... [--apply | --recover] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--apply` | flag | off | Replace managed files by staged replacement (default: preview only) |
| `--recover` | flag | off | Restore committed managed files from the application's `HEAD` |
| `--harness` | string (repeatable) | previously projected | Configuration profiles to refresh |

**Default behavior is preview.** Hook registration files are merged: entries
the application added itself are preserved in place, managed entries are
replaced, and retired outputs listed by a previous projection are removed and
never resurrected. Malformed inputs are refused before any effect (exit `4`).
A managed path holding uncommitted local work is refused (exit `2`) because
recovery uses the application's own Git history; there are no receipts and no
implicit commit.

---

### gt project chroma regenerate

Rebuild the application's optional ChromaDB search cache from the authority's
current records for the application scope.

```
gt project chroma regenerate [--dir <application>] [--scope <application:name>] [--dry-run] [--json]
```

`--dry-run` reads the records and reports what would be replaced without
writing. Without the optional `chromadb` dependency (installed with
`pip install "groundtruth-kb[search]"`) the command reports `skipped`
(exit `2`) and preserves existing cache bytes. The cache is a derivation and
is never read as authority.

---

### gt project classify-tree

Classify every path of a tree against the target's current declarations:
the platform registry (`config/registry/sot-artifacts.toml`, read through
the registry resolver — exact, recursive, glob and opaque-container
coverage, archived declarations excluded) or the application's
`.gtkb-app-isolation.json` top-level entries (read and validated by the
application-boundary validator: schema version, application identity,
entry names, types, classifications, purposes, duplicate entries and
duplicate JSON keys), whichever the selected target carries. The
declarations are the sole coverage: a path they do not cover is an
`undeclared` finding even when the packaged template ownership map
(managed artifacts and ownership globs) knows its name — the template
match is reported as a hint, never as coverage
(GOV-PLATFORM-SOT-REGISTRY-001). The template map classifies only a
target that carries neither declaration file. Read-only; needs no
`groundtruth.toml` in the target and no authority.

```
gt project classify-tree --dir <path> [--output <report>] [--format markdown|json] [--max-depth N] [--ignore-glob G ...]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--dir` | path | **required** | Tree root to classify |
| `--output` | path | stdout | Report file; the command prints a one-line summary when writing a file |
| `--format` | choice | `markdown` | `markdown` or `json` |
| `--max-depth` | integer | `10` | Maximum walk depth |
| `--ignore-glob` | repeatable glob | built-in ignores | Additional ignore glob |

**Output:** a deterministic header (GT-KB version, target tree, the
declaration source consulted — `platform-registry`, `application-registry`,
`none` when the target carries neither file, or `unavailable` with the
cause when the file cannot be read or validated — total paths, findings)
and rows ordered by ownership then path: path, ownership, upgrade policy,
divergence policy, the declaration or registry record that classified the
path, and a finding when nothing covers it (`undeclared`) or the walk could
not read it (`unreadable`). An `unavailable` source covers nothing: every
path is then an `undeclared` finding and the validator's findings are
listed (JSON `declaration_source.findings` with `code`, `message`,
`severity` and `path`; Markdown "Declaration findings" section after the
table). An undeclared path the packaged template map knows carries the
template record as a hint (JSON row `template_hint`; Markdown "Template
hints" section after the table). A finding is a diagnostic and a hint is
not coverage; neither grants ownership or authorization, and the report
carries no owner-decision counts.

---

### gt design inspect

Inspect a local Claude Design handoff (`.zip` archive or directory):
file list with sizes, the archive `sha256` for zips, the
`SPEC-CD-HANDOFF-FORMAT-001` D1 format warnings and a deterministic,
redacted inspection record with its content hash. Read-only; needs no
authority and publishes nothing. Raw design bytes are never read into
the record. See [Claude Design Handoff Inspection](../claude-design-intake.md).

```
gt design inspect <HANDOFF> [--date <iso>] [--session-id <id>] [--owner-decision <text>] [--notes <text>] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `HANDOFF` | path | **required** | Local `.zip` file or directory; a missing path is a usage error, any other kind of path is refused |
| `--date` | string | today | Handoff date recorded in the report |
| `--session-id` | string | none | Session that inspected the handoff; omitted from the record when absent |
| `--owner-decision` | string | none | Triage outcome text recorded as a section |
| `--notes` | string | none | Inspection notes recorded as a section |
| `--json` | flag | off | Complete report as canonical JSON |

**Output:** the Markdown record (header, file list, format conformance,
optional owner decision and notes) followed by a `Redacted:` line when
the catalog matched anything; with `--json`, the report fields
(`source_path`, `source_kind`, `sha256`, `total_bytes`, `file_count`,
`entries`, `warnings`, `content`, `content_hash`, `redaction_notes`).
Format warnings are reported, never fatal.

---

## Deliberations (historical records)

Deliberation records are historical reasoning data read through the native
authority. They carry no authorization, currentness, GO, claim or completion
result (SPEC-2098). Enduring facts and decisions are applied to their canonical
records instead; the former `add`, `upsert`, `link`, `search --semantic-only`
and `rebuild-index` archive workflow is retired (O-7 R20), and the service
offers no write route for this domain.

### gt deliberations list

List historical deliberation records in deterministic ID order.

```
gt deliberations list [--search <TEXT>] [--source-type <TYPE>] [--spec-id <ID>] [--work-item-id <ID>] [--after <ID>] [--limit <N>] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--search` | text | none | Case-insensitive title substring |
| `--source-type` | text | none | Exact source type recorded with the deliberation |
| `--spec-id` / `--work-item-id` | text | none | Records linked to one specification or work item |
| `--after` | ID | none | Continue after this record ID |
| `--limit` | integer | `200` | Maximum records returned |
| `--json` | flag | off | Emit the records as JSON |

### gt deliberations show

Read one historical record by ID, including its redaction state.

```
gt deliberations show <DELIB_ID> [--history] [--json]
```

---

## Requirement intake

The persisted intake queue (`gt intake classify/capture/confirm/reject/list`)
is retired (O-7 R24). Requirement intake is direct: the `/gtkb-spec-intake`
skill (`groundtruth_kb.spec_intake`) classifies the owner's text into a
temporary candidate, then either confirms it into exactly one canonical
specification through the native authority (`gt spec show <ID>` reads it
back) or discards it with a reason. Confirmation creates no implementation
work; record work with `gt backlog record` once the specification has an
executable test in an active plan phase.

---

## Health Commands

The per-session health snapshot commands (`gt health`, `gt health snapshot`,
`gt health trends`) are retired (O-7 R23): a session snapshot is not a status
or continuation dependency. Bounded operational measurements are read from the
native dashboard KPI refresh (`gt dashboard refresh`) instead.

---

## Knowledge base maintenance (F8)

### gt kb reconcile

Run the five provenance and consistency detectors over the current
specifications of the configured native authority (`authority_url`). The
command reads `GET /v1/specifications` only and writes nothing; each detector
produces a report with zero or more findings, the command prints each report
and a total. Exit code is 0 whether or not findings exist — this is a
reporting command, not a gate. An unconfigured or unavailable authority is an
error (exit 1); there is no local database fallback.

```
gt kb reconcile [--orphans] [--stale] [--authority] [--duplicates]
                [--provisionals] [--all] [--stale-days <N>] [--activity-days <N>]
                [--project-root <path>] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--orphans` | flag | off | Run the orphaned-assertion detector. Finds machine assertions of active specs whose file targets (literal or glob) do not exist under the project root. |
| `--stale` | flag | off | Run the stale-spec detector. An active spec is stale when its `changed_at` is older than `--stale-days` and another active spec in the same `section` changed within `--activity-days`. |
| `--authority` | flag | off | Run the authority-conflict detector. Finds active stated-vs-inferred spec pairs in the same `(section, scope)` with overlapping machine assertion targets. |
| `--duplicates` | flag | off | Run the duplicate-spec detector. Reports active spec pairs whose titles overlap by >=90% of tokens. |
| `--provisionals` | flag | off | Run the expired-provisional detector. Reports active provisional specs (`authority='provisional'` with a `provisional_until` reference) whose replacement record carries `implementation_verified_at`. |
| `--all` | flag | off | Run every detector in the canonical order orphans, stale, authority, duplicates, provisionals. |
| `--stale-days <N>` | integer | 90 | Staleness threshold in days for `--stale`. |
| `--activity-days <N>` | integer | 30 | Same-section activity window in days for `--stale`. |
| `--project-root <path>` | path | configured `project_root` | Root used to resolve orphaned-assertion file targets. |
| `--json` | flag | off | Emit `{"project_root", "reports": [{"category", "finding_count", "findings"}], "total_findings"}` instead of text. |

**Behavior notes:**

- **No flags is equivalent to `--all`.** Calling `gt kb reconcile` with no
  detector flag runs every detector — useful for full-project sweeps.
- **Only the active corpus is inspected.** Detectors list specifications with
  `status=active`; retired and superseded records produce no findings. The
  replacement of a provisional spec is looked up in the complete listing.
- **Text output** prints one `[category] N finding(s)` block per detector
  with up to 50 canonical-JSON finding lines (the remainder is counted), then
  `Total findings across N detector(s): M`.
- **Non-dict assertions are silently skipped** by the orphan detector (the
  F8 "plain-text safety" guarantee), so reconciliation can traverse specs
  that mix machine and human-readable assertion lists without aborting.
- **Duplicate pairs are canonicalized** (`spec_a < spec_b`) so output is
  deterministic across runs.
- **Stale detection uses `changed_at` only.** The former N-session snapshot
  window has no native record source (session snapshots are retired), so
  every stale finding carries `reason: changed_at` with the thresholds used.
- **Provisional expiration is the replacement's verification.** The native
  lifecycle `status` is `active`, `superseded` or `retired`; the marker that a
  replacement has shipped is its `implementation_verified_at` timestamp. A
  replacement without it, or a dangling `provisional_until` reference, does
  NOT expire the provisional — it is still load-bearing.

**Examples:**

```
# Full sweep — run every detector against the configured authority
gt kb reconcile

# Orphan detection only, with explicit project root
gt kb reconcile --orphans --project-root /path/to/project

# Stale spec detection with tighter windows
gt kb reconcile --stale --stale-days 60 --activity-days 14

# Authority conflicts + duplicates combined, as JSON
gt kb reconcile --authority --duplicates --json

# Check for expired provisionals (cleanup pass)
gt kb reconcile --provisionals
```

---

## Scaffold commands (F6)

### gt scaffold specs

Generate a starter set of inferred specifications for one execution project
through the native authority.

```
gt scaffold specs --project-id <PROJECT> [--profile <minimal|full>] [--apply | --dry-run] [--actor <name>] [--json]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--project-id` | string | *required* | Execution project that owns the starter specifications |
| `--profile` | choice | `minimal` | `minimal` (governance + infra, 4 specs) or `full` (adds AI components + compliance, 6 specs) |
| `--apply` / `--dry-run` | flag | `--dry-run` | Dry-run reports the set without writing; `--apply` writes records with `authority = "inferred"` |
| `--actor` | string | `scaffold-generator` | Attribution recorded with the written records |
| `--json` | flag | off | Emit the report as JSON |

**Behavior:**

- Identities are project-qualified (`GOV-SCAFFOLD-01:<PROJECT>`) and handles
  are `scaffold:<PROJECT>:<template handle>`; an existing active handle in the
  project is skipped, never overwritten.
- Quality scoring runs in both modes and reports bronze / needs-work tiers.
- Inferred records never complete a core specification intake slot; owners
  promote them explicitly through the specification writer.
- `gt project init --spec-scaffold <profile>` applies the same set during
  initialization.

---

### gt scaffold iac

Generate Azure enterprise Terraform skeleton files.

```
gt scaffold iac [--profile azure-enterprise] [--apply | --dry-run] [--target-dir <path>]
```

Default dry-run output lists the files that would be written under
`iac/azure/`. Existing files are skipped; the scaffold never overwrites
adopter-owned IaC.

### gt scaffold cicd

Generate Azure enterprise GitHub Actions and supporting CI/CD docs.

```
gt scaffold cicd [--profile azure-enterprise] [--apply | --dry-run] [--target-dir <path>]
```

Default dry-run output lists workflow and documentation files that would be
written under `.github/` and `docs/azure/`. Existing files are skipped.

---

## Session and Context Commands

The commands in this section and in the Canonical Record, Project Lifecycle,
Bridge, Harness and Service sections below read and write the native
authority selected by `authority_url` in the selected `groundtruth.toml`.
Without an `authority_url` a command refuses with `No authority_url is
configured` and exits `1`; there is no local fallback. An unreachable service
is reported as `authority_unavailable` with the cause, elapsed time and
request path, without retry. A service refusal is printed as `Error: <code>:
<message>` followed by its canonical JSON details and exits `1`. `--json`
prints the service result as canonical JSON; text output prints each record
as `<id> v<version>: <title>` followed by its description and, where the
command shows a complete record, one `key: value` line per remaining field.

### gt session bind

Return the initialization outcome and the immutable binding for the received
init marker. The binding attributes one native context to one subject and
role; a harness, model, environment value or previous context cannot supply
or change it.

```
gt session bind --native-context-id <id> --init-keyword "<received text>" [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--native-context-id` | string | *required* | The actual native context identifier supplied by the harness |
| `--init-keyword` | string | *required* | The complete received text; its lines are scanned for the exact marker `::init gtkb pb`, `::init gtkb lo`, `::init application pb` or `::init application lo` |
| `--json` | flag | off | Emit the result as JSON |

**Behaviour:** `POST /v1/sessions/bind`. The result is `{"status": ...,
"binding": {...}}`. `status` is `init_requested` when this call created the
binding and `already_initialized_idempotent` when an identical binding
already existed (including one created concurrently); it describes this call
only and is never stored. The binding carries `native_context_id`,
`session_context_id` (`SENV-<hex>`), `subject`, `role` (`prime-builder` or
`loyal-opposition`), `created_at` and `minimum_idempotency_identity`.

Refusals: `session_init_conflict` (two distinct markers in the text, or an
existing binding with another subject or role), `invalid_init_marker` (lines
that start with `::init` but no exact marker) and `no_init_marker` (no marker
at all; ordinary owner input is not a bind request). The error details carry
`observed_markers`, `invalid_marker_line_numbers` and a `recovery_route`;
surrounding input and unknown tokens are never echoed.

---

### gt session show

Resolve the immutable binding of exactly the supplied native context, with no
fallback to another session.

```
gt session show --native-context-id <id> [--json]
```

`GET /v1/sessions/binding`. Returns the binding fields listed under `gt
session bind`. A context without a binding is refused with
`no_session_binding`. Read-only.

---

### gt context session

Read an existing binding together with the current startup requirements and
the authored baseline, as one bounded startup read.

```
gt context session --native-context-id <id> [--json]
```

`GET /v1/sessions/context`. The result carries `binding`, `specifications`
(the current records `GOV-SESSION-SELF-INITIALIZATION-001`,
`DCL-SESSION-ROLE-RESOLUTION-001` and `GOV-HARNESS-ISOLATION-001`, all
required to be `active`), `baseline` (path and content of
`.harness-baseline-configuration/rules/session-bootstrap.md` and
`.harness-baseline-configuration/rules/operating-model.md` read from the
service's selected project root, each at most 65536 bytes), `scope`,
`host_observations` (`activity`, `tools_skills_plugins_hooks` and
`startup_tokens`, each `unavailable` with its reason: the service cannot
observe the receiving host) and `retrieval_routes`. Text output prints the
binding, the scope statement, each record, each baseline file and the
observations and routes.

Refusals: `no_session_binding`; `invalid_context_id` for a blank identifier;
`startup_source_unavailable` when a required specification is missing or not
active, or a baseline file is missing, redirected, unreadable or larger than
65536 bytes (details name the source and a recovery route). The read creates
no session state and establishes no activity, work assignment or
qualification.

---

### gt context work-item

Read current work together with its linked formal requirements, test
instructions and prerequisites.

```
gt context work-item <WORK_ITEM_ID> [--json]
```

`GET /v1/work-items/<id>/context`. The result carries `work_item`,
`membership`, `project`, `program` (or `null`), `specifications` (the current
formal sources of the work and its project), `test`, `test_phases`,
`test_plans`, `predecessors` (the work items in `depends_on_work_items`),
`readiness` (the project's readiness gate) and `work_item_readiness`. Text
output prints, in order and only when present, `program`, `project`,
`work_item`, `specifications`, `test`, `test_phases`, `test_plans`,
`predecessors`, `readiness` and `work_item_readiness`.

Refusals: `not_found` for an unknown work item; `inactive_context_source` when
a linked formal source is not active (details list the IDs);
`test_phase_required` when the linked test belongs to no active test-plan
phase. Read-only.

---

## Canonical Record Commands

`gt spec`, `gt tests`, `gt test-plans`, `gt test-phases`, `gt projects`,
`gt backlog`, `gt terms` and `gt harness` share three record verbs generated
from one definition (`show`, `list` and `record`); `gt projects` also carries
the `dependencies` and `formal-links` sub-groups with the same verbs. This
section documents the shared verbs once and then the domains and sub-groups
not covered elsewhere in this reference. `gt spec list|show|record`,
`gt tests list|show`, `gt projects list|show`, `gt backlog list|show|record`
and `gt harness list|show` are listed in the
[Complete Command Reference](#complete-command-reference); `gt backlog record`
is also described under [Requirement intake](#requirement-intake).

### Shared record verbs

```
gt <domain> show <RECORD_ID> [--history] [--json]
gt <domain> list [--limit <n>] [--after <id>] [--search <text>] [<domain filters>] [--json]
gt <domain> record --id <RECORD_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

**`show`** reads `GET /v1/<domain>/<id>` and prints the complete current
record; `--history` reads `/v1/<domain>/<id>/history` instead (see
[Record version history](#record-version-history-show-history)). An
unknown ID is `not_found`.

**`list`** reads `GET /v1/<domain>` in pages of at most 1000 records in
deterministic ID order (`COLLATE "C"`) until `--limit` records (default
`200`) are collected or the service returns no `next_after`; `--after` continues
after a record ID. `--search` is a case-insensitive substring match over the
domain's `title`, `name`, `description`, `purpose`, `canonical_term` and
`definition` columns where they exist; a domain with none of them refuses
search with `invalid_query`. The generated option set shows `--status`,
`--kind`, `--priority`, `--spec-id` and `--plan-id` for every domain, but the
service accepts only the filters listed for each domain below; any other
filter is refused with `invalid_query`.

**`record`** writes `PUT /v1/<domain>/<id>` through the CAS writer:
`--expected-version` must equal the record's current version (`0` asserts a
new record), `--actor` and `--change-reason` are recorded with the new
version, and `--fields-file` names a UTF-8 JSON object whose keys are the
typed fields of the domain (listed below); they are merged into the current
record. The command prints the canonical readback. A stale version is refused
with `cas_conflict` (details carry `expected`, `actual` and `id`); an unknown
or mistyped field is refused with `invalid_request` (details name the field,
never the submitted body). The generated option set also shows
`--project-id` (used only when creating a work item with `gt backlog record`)
and `--kind` (used only by `gt projects record`); the other domains refuse
them as `invalid_request`.

---

### gt terms

Current canonical terminology records (`/v1/terms`).

```
gt terms list [--status <lifecycle>] [--scope <scope>] [--authority-level <level>] [--search <text>] [--limit <n>] [--after <id>] [--json]
gt terms show <TERM_ID> [--history] [--json]
gt terms record --id <TERM_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

| `list` filter | Matches |
|---------------|---------|
| `--status` | `lifecycle_status` (`candidate`, `active`, `deprecated`, `retired`) |
| `--scope` | exact term scope |
| `--authority-level` | `platform_core`, `adopter_extension` or `project_local` |

`record` fields: `canonical_term`, `definition`, `authority_level`, `scope`,
`accepted_synonyms`, `discouraged_synonyms`, `linked_artifacts`,
`linked_services`, `usage_examples`, `forbidden_uses`, `lifecycle_status`,
`source_authority`. A new term defaults to `lifecycle_status = "candidate"`.
Term names are validated after the write (`invalid_terminology`, with the
issues), and an `active` term requires a current formal source
(`invalid_term_source`).

---

### gt tests record

Create or amend one test artifact (`PUT /v1/tests/<id>`); `gt tests list` and
`gt tests show` are indexed below.

```
gt tests record --id <TEST_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

Fields: `title`, `description`, `test_type`, `spec_id`, `test_file`,
`test_class`, `test_function`, `expected_outcome`, `application_scope`
(`gtkb_platform` or `application:<catalog name>`). The application scope is
validated against the platform host's application catalog
(`invalid_application_scope`).

---

### gt test-plans

Current test plans (`/v1/test-plans`).

```
gt test-plans list [--status <status>] [--search <text>] [--limit <n>] [--after <id>] [--json]
gt test-plans show <PLAN_ID> [--history] [--json]
gt test-plans record --id <PLAN_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

`list` accepts the `--status` filter. `record` fields: `title`,
`description`, `status`; a new plan defaults to `status = "active"`.

---

### gt test-phases

Current test-plan phases (`/v1/test-phases`).

```
gt test-phases list [--plan-id <PLAN_ID>] [--search <text>] [--limit <n>] [--after <id>] [--json]
gt test-phases show <PHASE_ID> [--history] [--json]
gt test-phases record --id <PHASE_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

`list` accepts the `--plan-id` filter. `record` fields: `plan_id`,
`phase_order`, `title`, `description`, `gate_criteria`, `test_ids`. Every
`test_ids` entry must name an existing test (`not_found` otherwise). Changing
the set of `test_ids` of an existing phase clears the stored execution
evidence (`last_result`, `last_executed_at`, `last_executed_on`): a native
amendment cannot supply a replacement execution result.

---

### gt harness record

Create or amend one harness installation record (`PUT /v1/harnesses/<id>`).
Roles never live here; they bind to native contexts (`gt session bind`).

```
gt harness record --id <HARNESS_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

Fields: `harness_name`, `harness_type`, `status` (`registered`, `active`,
`suspended`, `retired`), `invocation_surfaces`, `capabilities_ref`. A new
record requires `harness_name` and `harness_type` (`harness_fields_required`)
and starts as `registered` (`invalid_harness_transition` otherwise). A status
change must be a valid lifecycle transition (`invalid_harness_transition`),
and the last `active` harness cannot be suspended or retired
(`last_active_harness`).

---

### gt projects record

Create or amend one program or execution project (`PUT /v1/projects/<id>`).

```
gt projects record --id <PROJECT_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--kind program|project] [--json]
```

Fields: `name`, `repository_ref` (`platform` or `application:<name>`),
`parent_project_id`, `rank`, `purpose`, `target_outcome`, `scope_note`,
`start_date`, `target_date`, `notes`. `--kind` selects `program` or
`project` for a new record (default `project`); it cannot change an existing
record's kind, and a closed project cannot be amended
(`project_structure_frozen`). An execution project requires an explicit
`repository_ref` that resolves on the platform host
(`project_repository_required`, `invalid_repository_ref`), and may name one
active program as `parent_project_id` (`invalid_program_parent`); a program
has no `repository_ref` (`program_has_no_repository`). Reassigning the
repository of a project with active bridge attempts or committed work is
refused (`project_repository_frozen`). A new execution project defaults to
`status = "active"` and `authorization = "authorized"`; programs have no
authorization value; `PROJECT-GTKB-NEW-WORK-INTAKE` is created
`not authorized`.

---

### gt projects dependencies

Project-to-project prerequisites (`/v1/project-dependencies`): a dependent
execution project requires a prerequisite project to reach a state before one
of its gates.

```
gt projects dependencies list [--status active|retired] [--dependent-project <id>] [--prerequisite-project <id>] [--affected-gate readiness|closure] [--limit <n>] [--after <id>] [--json]
gt projects dependencies show <DEPENDENCY_ID> [--history] [--json]
gt projects dependencies record --id <DEPENDENCY_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

`list` accepts `--status`, `--dependent-project`, `--prerequisite-project`
and `--affected-gate`; this domain has no searchable text columns, so
`--search` is refused (`invalid_query`). Text rows read `<dependent> requires
<prerequisite> = <state> at <gate> [<status>]`.

`record` fields: `dependent_project_id`, `prerequisite_project_id`,
`dependency_kind` (`requires_project_state`), `required_prerequisite_state`
(`active`, `verified`, `retired`, `cancelled`), `affected_gate` (`readiness`,
`closure`), `rationale`, `provenance`, `related_work_item_id`, `status`
(`active`, `retired`). Both endpoints must be existing execution projects
(`dependency_endpoint_required`, `invalid_dependency_endpoint`); a new
dependency starts `active` (`invalid_dependency_transition`); a closed
dependent project cannot acquire or change an active dependency
(`closed_dependent_project`); a prerequisite already closed in another state
is refused (`unreachable_dependency`); the resulting active graph is validated
as a whole. New records default `provenance` to the actor and
`blocking_status` to `open`.

---

### gt projects formal-links

Formal relationships between an execution project and its specifications
(`/v1/project-formal-links`, `relationship = "governed_by"`). Amending or
retiring a link preserves the project's authorization.

```
gt projects formal-links list [--status active|retired] [--project-id <id>] [--limit <n>] [--after <id>] [--json]
gt projects formal-links show <LINK_ID> [--history] [--json]
gt projects formal-links record --id <LINK_ID> --fields-file <json> --expected-version <n> --actor <name> --change-reason <text> [--json]
```

`list` accepts `--status` and `--project-id` and returns only specification
links; `--search` is refused (`invalid_query`). Text rows read `<project> ->
<spec> [<status>]`. `show` also resolves obsolete `bridge_thread` and
`completion_guard` relationships; any other link kind is `not_found`.

`record` fields: `project_id`, `artifact_ref` (specification ID), `status`
(`active`, `retired`), `notes`. A link names an execution project and a
formal record (`formal_link_endpoint_required`); its endpoints are frozen once
created (`formal_link_identity_frozen`: retire the old relationship and create
the intended one); a new link starts `active`
(`invalid_formal_link_transition`); an active link requires an active
specification (`inactive_formal_source`) and one active link per project and
source (`duplicate_formal_link`). An obsolete `bridge_thread` or
`completion_guard` relationship accepts only `{"status": "retired"}`
(`invalid_formal_link`).

---

## Project Lifecycle Commands

Owner ordering, readiness reads, membership moves and the complete-project
Git commit, all through the native authority. Finalization is performed by
the independent Loyal Opposition context after every project member is
VERIFIED; Prime Builder contexts are refused (`independent_verifier_required`).

### gt projects set-authorization

Apply the owner's explicit ordering choice to an execution project. Existing
bridge chains continue; membership does not change.

```
gt projects set-authorization <PROJECT_ID> --authorization "authorized"|"not authorized" --expected-version <n> --actor <name> --change-reason <text> [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--authorization` | choice | *required* | `authorized` or `not authorized` |
| `--expected-version` | integer >= 1 | *required* | Current project version |
| `--actor` | string | *required* | Attribution recorded with the version |
| `--change-reason` | string | *required* | Change reason recorded with the version |
| `--json` | flag | off | Emit the complete project record as JSON |

`PUT /v1/projects/<id>/authorization`. Prints the complete current project.
An unchanged value returns the current record without a new version.
Refusals: `cas_conflict`, `program_not_authorizable` (programs have no
authorization), `project_closed` (only an active project changes ordering)
and `intake_not_authorizable` (`PROJECT-GTKB-NEW-WORK-INTAKE` stays
`not authorized`).

---

### gt projects readiness

Explain whether the project's exact prerequisite outcomes are available at a
gate.

```
gt projects readiness <PROJECT_ID> [--gate readiness|closure] [--json]
```

`GET /v1/projects/<id>/readiness?gate=<gate>` (default `readiness`). The
result carries `project_id`, `gate`, `ready` and `dependencies`, one entry per
active dependency affecting that gate with its `satisfied` flag and reason.
Read-only.

---

### gt backlog readiness

Explain whether a work item's reviewed or committed predecessors are
available.

```
gt backlog readiness <WORK_ITEM_ID> [--json]
```

`GET /v1/work-items/<id>/readiness`. The result carries `work_item_id`,
`project_id`, `ready`, `predecessors` (one entry per predecessor with
`required_result`, `current_status`, `satisfied`, `reason` and
`changed_paths`) and `accepted_change_paths`. The bridge evaluates the same
readiness before a NEW, REVISED, GO, READY or VERIFIED artifact and refuses
those effects with `work_item_dependencies_unsatisfied`. Read-only.

---

### gt projects move-item

Move one open work item atomically from one execution project to another,
preserving both projects' authorization.

```
gt projects move-item --work-item-id <id> --from-project <id> --to-project <id> --expected-version <n> --actor <name> --change-reason <text> [--membership-order <n>] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--work-item-id` | string | *required* | Open work item to move |
| `--from-project` | string | *required* | Current parent project |
| `--to-project` | string | *required* | Destination execution project (must differ) |
| `--expected-version` | integer >= 1 | *required* | Current membership version |
| `--membership-order` | integer | none | Position in the destination project |
| `--actor` / `--change-reason` | string | *required* | Attribution and reason |
| `--json` | flag | off | Emit the result as JSON |

`POST /v1/work-items/<id>/move`. Refusals: `cas_conflict` (stale membership
version), `invalid_membership` (same source and destination),
`work_item_frozen` (reviewed or closed membership requires reconciliation).

---

### gt projects commit

Commit the complete reviewed project through the native service and normal
Git hooks, in one operation.

```
gt projects commit <PROJECT_ID> --native-context-id <id> --expected-version <n> --message-file <path> [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--native-context-id` | string | *required* | The verifying Loyal Opposition context |
| `--expected-version` | integer >= 1 | *required* | Current project version |
| `--message-file` | path | *required* | Readable UTF-8 file with the authored commit message |
| `--json` | flag | off | Emit the result as JSON |

**Behaviour:** `POST /v1/projects/<id>/commit` (180-second client timeout).
The service prepares the cohort exactly as `prepare-commit` does, requires
the message to cite every retiring work item as `(WI-NNNN)`
(`incomplete_commit_citations`), creates one normal Git commit of the
reviewed artifacts in the context's registered checkout with hooks running,
then confirms it exactly as `confirm-commit` does. The command exits `0`
only for `status` `confirmed` or `already_confirmed`; every other result
(`fresh_verification_required`, `ready_to_confirm` recovery, a
`commit_not_confirmed` failure record) exits `1`. When Git committed but a
later step failed, the existing reviewed commit is confirmed and the result
carries a `checkout_notice`.

---

### gt projects prepare-commit

Prepare the complete project Git commit: lock the cohort, verify the reviewed
bytes are unchanged and materialize the verifying context's checkout.

```
gt projects prepare-commit <PROJECT_ID> --native-context-id <id> --expected-version <n> [--json]
```

`POST /v1/projects/<id>/prepare-commit`. Results by `status`:
`ready_to_commit` (with `expected_parent`, `checkout`, `hooks_path`,
`reviewed_artifacts`, `work_item_ids`, `required_citations` and an
`instruction`), `ready_to_confirm` (an existing reviewed commit candidate was
found: `commit_id`, `expected_parent`), `already_confirmed` (the project is
already `verified`; `commit_id`) or `fresh_verification_required`
(`work_item_ids`; reviewed bytes changed or a finalization failure is
recorded) which exits `1`. Refusals: `independent_verifier_required`,
`program_has_no_commit`, `cas_conflict`, `project_not_active`,
`terminal_commit_missing`, `ambiguous_project_commit`,
`existing_commit_needs_reconciliation`.

---

### gt projects check-commit

Check a candidate commit against the prepared cohort before the reference is
updated; the installed `.githooks/reference-transaction` hook calls this
route while `gt projects commit` runs.

```
gt projects check-commit <PROJECT_ID> --native-context-id <id> --expected-version <n> --commit-id <sha> --expected-parent <sha> --index-tree <sha> [--json]
```

`POST /v1/projects/<id>/check-commit`. `--commit-id`, `--expected-parent` and
`--index-tree` are Git object IDs (40 or 64 hex digits). Returns
`ready_to_update_reference` with the `commit_id`, or a
`fresh_verification_required` result (exit `1`) when reviewed bytes changed.
Refusals include `fresh_verification_required` while a failure record is
open, `commit_checkout_changed` (the context files changed after
preparation), `commit_not_in_progress` and `commit_context_mismatch` (a check
issued outside, or by another context than, the commit in progress).

---

### gt projects confirm-commit

Confirm the identity of the complete reviewed Git commit and record project
completion.

```
gt projects confirm-commit <PROJECT_ID> --native-context-id <id> --expected-version <n> --commit-id <sha> --expected-parent <sha> [--json]
```

`POST /v1/projects/<id>/confirm-commit`. On success the repository is
fast-forwarded to `--commit-id` when it is not already `HEAD`, the project
becomes `verified` with its activation link (`project_artifact_links`,
`artifact_type = "git_commit"`), every member work item records
`completion_evidence = "git:<commit>"`, the bridge attempts become
`committed` and their disposable payloads are purged; the result is
`confirmed` with `work_item_ids`. A re-confirmation of the recorded commit is
`already_confirmed`; another commit for a terminal project is
`terminal_commit_mismatch`. A candidate that does not verify (a changed
integration base, a parent other than the prepared one, a commit not
reachable from a branch, missing `(WI-...)` citations, paths outside the
reviewed cohort, bytes differing from the reviewed artifacts, or an empty
commit) records a `commit_not_confirmed` failure and returns
`fresh_verification_required` (exit `1`); so does a fast-forward that does
not advance to the candidate (`commit_not_current`). Other refusals:
`fresh_verification_required` while a failure record is open,
`conflicting_commit_fact`.

---

### gt projects commit-failed

Record that the complete project commit did not complete, so the dispatcher
requests fresh verification without authoring a verdict.

```
gt projects commit-failed <PROJECT_ID> --native-context-id <id> --expected-version <n> --reason commit_not_confirmed --evidence <text> [--json]
```

`POST /v1/projects/<id>/commit-failed`. `--reason` accepts only
`commit_not_confirmed`; `--evidence` is the observed failure text, recorded
with the current repository `HEAD`. The result is the
`fresh_verification_required` record (`reason`, `work_item_ids`); unlike the
other finalization commands this one exits `0`, because the failure record is
its intended result.

---

## Bridge Commands

Bridge messages are disposable payloads delivered through fenced native
domain operations; canonical attempt, claim, review and terminal state live in
the authority. Every command here uses the native authority (see the note at
the top of [Session and Context Commands](#session-and-context-commands)).
`gt bridge show` is documented in the Complete Command Reference; the
commands below complete the group.

Common vocabulary: an **attempt** is one bridge document (`DOCUMENT`) with a
`head_version`, `head_status` and `disposition` (`active`, `committed`,
`abandoned`); a **claim** reserves exactly one successor artifact
(`next_version = head_version + 1`, an `intended_status`) for the claimant's
`session_context_id`, expires 600 seconds after acquisition without renewal,
carries a monotonically increasing integer **fence**, and is consumed by
delivery. `--native-context-id` always names the actual bound context; an
unbound context is refused with `no_session_binding`.

### gt bridge queue

Report eligible next actions for one role, for owner or dispatcher selection.

```
gt bridge queue --role pb|lo [--json]
```

`GET /v1/bridge/queue?role=<role>`. The result carries `role`, `eligible`
(active, unclaimed attempts whose head status the role answers, ordered by
work-item priority, head time and ID, with project and work-item readiness
satisfied) and `blocked` (the same attempts with an unsatisfied `readiness`
or `work_item_readiness`, or `reason = "queue_action_time_unavailable"`).
For `lo`, a VERIFIED head with a recorded finalization failure is queued for
fresh verification. Reporting selects nothing and changes no state.

---

### gt bridge state-report

Report canonical attempts, exact claims and both role queues from one
database snapshot, without harness configuration.

```
gt bridge state-report [--json | --markdown]
```

`GET /v1/bridge/state-report`. The default and `--markdown` output is the
rendered Markdown report; `--json` emits `observed_at` (the transaction time
used for claim expiry), `attempts` (per attempt: identity, versions, status,
disposition, `created_at`, `closed_at`, `terminal_commit`, `head_created_at`
and `next_artifact_claim` with `next_version`, `intended_status`,
`expires_at`, or `null`), `attempt_counts` by disposition,
`unfiled_attempt_count`, `active_status_mix`, `active_claim_count` and
`queues` (`pb` and `lo`, as `gt bridge queue`). Giving both `--json` and
`--markdown` is refused. Read-only; counts include unfiled, advisory and
closed attempts, and a purged head has no `head_created_at`.

---

### gt bridge check-delivery

Verify this context's exact assigned delivery, including a purged terminal
head, without claims, payloads or writes.

```
gt bridge check-delivery <DOCUMENT> --version <n> --native-context-id <id> [--json]
```

`GET /v1/bridge/<document>/delivery`. Returns `status = "delivered"` with
`document`, `version`, `bridge_status`, `native_context_id` and
`author_session_context_id` when the numbered delivery (or the retained
terminal head at that version) was authored by the bound context. Otherwise
`bridge_delivery_incomplete` is refused with `observed_head_version`: final
prose is not proof of delivery.

---

### gt bridge claim

Reserve one exact successor slot of an attempt for 600 seconds, without
renewal.

```
gt bridge claim <DOCUMENT> --native-context-id <id> --expected-version <n> --status <STATUS> --request-id <id> [--work-item-id <WI>] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--native-context-id` | string | *required* | The bound context that will author the artifact |
| `--expected-version` | integer >= 0 | *required* | The observed current head version (`0` for a fresh attempt) |
| `--status` | string | *required* | Intended status of the next artifact (NEW, REVISED, GO, NO-GO, READY, NOT-READY, VERIFIED, VERDICT-REJECTED, SUPERSEDED, WITHDRAWN, BLOCKED, ADVISORY) |
| `--request-id` | string | *required* | Unique per claim request; reuse only when retrying this exact request |
| `--work-item-id` | string | none | Required for implementation lifecycle artifacts; omitted for ADVISORY |
| `--json` | flag | off | Emit the claim as JSON |

**Behaviour:** `POST /v1/bridge/<document>/claim`. A fresh attempt (no
canonical row) starts only with NEW, BLOCKED or ADVISORY and, for work,
requires open work in an active execution project; the row is created by the
claim. The result is the claim row (`attempt_id`, `next_version`,
`intended_status`, `predecessor_sha256`, `claimant_session_context_id`,
`request_id`, `fence`, `acquired_at`, `expires_at`) plus `predecessor` (the
current head message, or `null`). Retrying with the same request ID, context,
status and observed head returns the same live claim.

Refusals: `wrong_author_role` (the context's role cannot author that
status), `advisory_is_not_work` / `work_item_required` (work-item presence
must match the status), `invalid_transition` (the status cannot follow the
current head), `work_not_open` (a fresh attempt needs open work in an active
execution project), `stale_bridge_head` (the observed version, work item or
disposition is not current), `scope_changed`, `project_not_authorized` (a NEW
proposal on a project that is not `authorized`),
`project_dependencies_unsatisfied` / `work_item_dependencies_unsatisfied`,
`verification_not_requested` (VERIFIED after VERIFIED without a finalization
failure), `artifact_already_claimed` (another live claim holds the slot) and
`artifact_effect_conflict` (a READY claim whose targets overlap another live
READY claim in the same repository).

---

### gt bridge check

Check that the exact current artifact claim is still live and current before
a protected effect.

```
gt bridge check <DOCUMENT> --native-context-id <id> --fence <n> [--json]
```

`POST /v1/bridge/<document>/check`. Returns `status = "current"` with the
`claim` row and, for a READY claim, the `target_paths` (proposal paths and
test targets) the implementation may touch. Refusals: `stale_artifact_fence`
(the claim is missing, expired, replaced or held by another context),
`stale_bridge_head` (the claimed predecessor is no longer the current
delivery), `scope_changed` and the readiness refusals listed under
`gt bridge claim`. A passing check is not a transferable permission;
publication and delivery recheck the fence at their own boundary.

---

### gt bridge release

Release the exact current artifact claim without delivering.

```
gt bridge release <DOCUMENT> --native-context-id <id> --fence <n> [--json]
```

`POST /v1/bridge/<document>/release`. Returns `status = "released"` with
`document` and `fence`. Refuses `stale_artifact_fence` and `stale_bridge_head`
as `gt bridge check` does. An expired claim needs no release.

---

### gt bridge worktree

Materialize the current project work into this context's own registered
checkout for the claimed artifact.

```
gt bridge worktree <DOCUMENT> --native-context-id <id> --fence <n> [--json]
```

`POST /v1/bridge/<document>/worktree`. Requires a live claim (as `gt bridge
check`) on a work attempt; an advisory selects no worktree
(`advisory_is_not_work`). The checkout under `.worktrees/<session context
id>` receives the current bytes of every path in scope of the project's
active attempts, at the project work root's `HEAD`. The result carries
`path`, `branch`, `head`, `artifact_preimages` (this attempt's own paths
mapped to `{"mode", "object_id"}` or `null` for an absent path; pass this
object to `gt bridge publish-work --preimages-file`) and `loaded_paths`. For
NEW, REVISED, GO, READY and VERIFIED claims, unsatisfied work-item
dependencies are refused. Filesystem refusals (a redirected or unregistered
checkout, changed canonical work during preparation, a readback mismatch)
surface with their own codes, for example `artifact_preimage_changed` and
`checkout_readback_failed`.

---

### gt bridge check-effects

Check concrete tool targets against the bound context's scratch and
implementation scope, without granting or recording permission. This is the
pre-tool check the harness effect gates call.

```
gt bridge check-effects --native-context-id <id> --cwd <absolute dir> --path <target> [--path <target> ...] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--native-context-id` | string | *required* | The bound context performing the effect |
| `--cwd` | string | *required* | The tool's actual absolute working directory (must exist) |
| `--path` | string (repeatable) | *required* | Each concrete tool target; relative targets resolve against `--cwd` |
| `--json` | flag | off | Emit the result as JSON |

`POST /v1/bridge/check-effects`. Targets entirely inside the context's own
scratch directory (`<project root>/scratchpad/<session context id>`) return
`{"status": "current", "scope": "scratch"}`. Any other target requires a live
READY claim held by this context (`implementation_claim_required`), a
registered checkout (`checkout_not_registered`), every target inside that
checkout (`effect_outside_checkout`) as a concrete file, and all targets
belonging to exactly one current claim's proposal paths and test targets
(`effect_outside_claim`); the result then carries `scope =
"implementation"`, the `document` and its `fence`. Targets containing `..`
or `.git` components, drive-relative paths, control characters or directories
are `invalid_effect_path`; a symlink or junction on the path is
`effect_path_redirected`. Nothing is retained: publication rechecks the fence
and scope at its own boundary.

---

### gt bridge publish-work

Publish only the claimed implementation artifacts from this context's
registered checkout into the project work root, before authoring the READY
report.

```
gt bridge publish-work <DOCUMENT> --native-context-id <id> --fence <n> --preimages-file <json> [--json]
```

`--preimages-file` is the UTF-8 JSON object returned as `artifact_preimages`
by `gt bridge worktree`: the exact bytes the context started from, per path.
`POST /v1/bridge/<document>/publish-work` requires the live READY claim
(`implementation_claim_required` otherwise), the stored proposal scope
(`scope_changed`) and satisfied project and work-item dependencies. The
preimages must cover exactly the claimed paths
(`incomplete_artifact_preimage`), and a destination path that changed since
the context loaded it is refused (`artifact_preimage_changed`); then the
claimed paths are copied and read back (`artifact_readback_failed` on a
mismatch) and the result is `status = "published"` with the resulting
`artifacts` map (`path` to `{"mode", "object_id"}` or `null`). The fence is
rechecked immediately before the copy. Unrelated bytes and other contexts'
checkouts are never touched.

---

### gt bridge deliver

Publish the author's complete UTF-8 message bytes as the claimed successor
and consume the claim.

```
gt bridge deliver <DOCUMENT> --native-context-id <id> --fence <n> --content-file <path> [--headless] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--native-context-id` | string | *required* | The authoring bound context |
| `--fence` | integer >= 1 | *required* | Fence of the live claim for this artifact |
| `--content-file` | path | *required* | Readable UTF-8 file holding the complete authored message |
| `--headless` | flag | off | Deliver BLOCKED as the headless response to an unauthorized NEW proposal; interactive contexts ask the owner instead |
| `--json` | flag | off | Emit the result as JSON |

**Behaviour:** `POST /v1/bridge/<document>/deliver` with `mode` `interactive`
or `headless`. The service parses the authored header (status, `Document`,
`Version`, `bridge_kind`, provenance, `recipient_role` and envelope lines) and
stores the bytes unchanged; it never fills provenance, rewrites headers or
allocates another version. Success returns `status = "delivered"` with
`document`, `version`, `bridge_status`, `project_id` and
`project_ready_for_commit` (`false` for ADVISORY). Re-sending the identical
bytes with the same fence for an already stored version returns
`already_delivered`.

Refusals: `bridge_credential_detected` (credential patterns in the message;
details name the patterns), `invalid_bridge_header` (document, project or
work item differ from the attempt), `author_context_mismatch`
(`author_session_context_id` is not the bound context), `wrong_author_role`,
`attempt_closed`, `project_subject_mismatch`, `bridge_version_collision` (a
stored version with different bytes or fence), `stale_artifact_fence`,
`claim_does_not_match_artifact` (version or status differ from the claim),
`not_found` for an unknown `author_harness_id`, `scope_changed`,
`project_not_authorized` (NEW on a project not `authorized`),
`interactive_owner_decision_required` (BLOCKED without `--headless`) and
`invalid_blocked_observation` (BLOCKED must report the current
`not authorized` project and its `authorization_read_at`).

---

### gt bridge artifacts

Identify the current Git-normalized bytes of an attempt's reviewed paths.
This is an identity map, not a verdict.

```
gt bridge artifacts <DOCUMENT> [--json]
```

`GET /v1/bridge/<document>/artifacts`. Returns the map of the attempt's
proposal paths and test targets to `{"mode", "object_id"}` in the project
work root, or `null` for an absent path (an empty object when the attempt has
no scope yet). An attempt that is not active is `not_found`. Read-only; a
verifier inspects and tests the identified bytes before authoring VERIFIED.

---

### gt bridge abandon

Abandon a broken or invalidated attempt from canonical evidence, when no live
claim remains and no verdict can lawfully continue the chain.

```
gt bridge abandon <DOCUMENT> --native-context-id <id> --expected-version <n> --reason <text> [--json]
```

`POST /v1/bridge/<document>/abandon`. The attempt must be active at exactly
`--expected-version` (`attempt_not_abandonable`), hold no live claim
(`live_artifact_claim`) and be demonstrably invalid: a broken chain, changed
scope, missing record or invalid membership (`attempt_still_valid` otherwise:
continue the lawful chain). Committed or verified work is terminal
(`attempt_not_abandonable`). For a VERIFIED head, an existing reviewed Git
commit or changed reviewed paths require Git reconciliation first
(`git_reconciliation_required`); otherwise the work item is reopened. The
attempt's disposition becomes `abandoned`, its payloads are purged, and the
result is `{"document", "disposition": "abandoned", "work_item_id"}`. An
abandoned attempt supplies no reusable GO, claim or effect authority.

---

## Harness Commands

`gt harness list`, `gt harness show` and `gt harness record` read and amend
the harness installation records (see [Canonical Record
Commands](#canonical-record-commands)). The two commands below read
diagnostics and derive configuration.

### gt harness diagnostic

Read local diagnostics for one registered harness and, optionally, one
explicitly selected context binding. Metadata does not qualify actual host
behavior.

```
gt harness diagnostic --harness-id <id> [--native-context-id <id>] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--harness-id` | string | *required* | Harness record to read (`GET /v1/harnesses/<id>`) |
| `--native-context-id` | string | none | Read only this exact context's immutable binding; nothing is inferred |
| `--json` | flag | off | Emit the report as JSON |

**Behaviour:** the report (`schema_id = "gtkb.harness_diagnostic.v1"`) has
`status = "partial"`: identity and a configuration fingerprint come from the
canonical harness record; `role` and `correlation` are observed only when a
binding is supplied and resolves (`unavailable` with
`native_context_not_selected`, `no_session_binding`,
`session_authority_unavailable` or `invalid_session_response` otherwise);
capabilities, provider and model identity, guard, hooks, tool surface,
adapter readiness, telemetry and provider health are `unavailable` with their
reasons, and `parity` is `unqualified`. `errors` lists `harness_not_active`
for a record not in `active` status. An unknown harness
(`harness_not_registered`), an unavailable authority
(`harness_authority_unavailable`) or an invalid record
(`invalid_harness_response`) yields `status = "error"` and exit `1`. No
provider request is made.

---

### gt harness project

Derive one harness configuration from the selected project's canonical
baseline by running that project's projector
(`scripts/harness_projection/project_harness.py --harness <HARNESS>`).

```
gt harness project <HARNESS> [--validate | --check | --dry-run]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `HARNESS` | argument | *required* | Harness profile name known to the projector |
| `--validate` | flag | off | Validate the derivation without refreshing installed output |
| `--check` | flag | off | Report drift without refreshing installed output |
| `--dry-run` | flag | off | Show the proposed output paths without writing |

At most one mode may be given (usage error otherwise); without a mode the
projector refreshes the installed output. The projector must be a regular
file at that path inside the selected project (a missing or redirected script
is refused). Its stdout and stderr are passed through and its exit code is
returned. Generated harness directories are never edited by hand; change the
baseline and re-project.

---

## Service Commands

Operate or inspect the workstation's native domain service, the process that
serves the authority behind every native command.

### gt service serve

Serve an initialized PostgreSQL domain on IPv4 loopback only.

```
gt service serve [--port <n>]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--port` | integer (1-65535) | `8765` | Loopback port to listen on |

The command opens the configured PostgreSQL kernel (`[postgresql]` in
`groundtruth.toml`), verifies it with one read-only transaction, then runs
the authority application on `127.0.0.1:<port>` until interrupted; the
service's project root is the selected configuration's project root. It
never initializes or repairs the schema (`gt db postgres init` does that) and
has no `--json` option because it does not return.

---

### gt service status

Read status from the configured service; never open a client database.

```
gt service status [--json]
```

`GET /v1/status` on the configured `authority_url`; the result is the kernel
status the service reports. An unreachable service is `authority_unavailable`
with its cause; nothing is inferred locally.

---

## Local Governance and Repository Commands

Local operations on the selected project checkout. None of these commands
needs the authority or writes canonical records; the ones that change files
(`gt env migrate --apply`, `gt controls set`, `gt registry register|amend|transition`)
say so below.

### gt commit preflight

Run the staged commit governance checks with structured evidence, mirroring
the Python checks of `.githooks/pre-commit`.

```
gt commit preflight [--json] [--evidence-out <path>] [--python-bin <exe>] [--powershell-bin <exe>]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the evidence packet as JSON instead of the text summary |
| `--evidence-out` / `--evidence-file` | path | none | Also write the evidence packet JSON to this path (directories are created) |
| `--python-bin` | string | current interpreter | Python executable used for the script checks |
| `--powershell-bin` | string | auto-detected | PowerShell executable used to parse staged `.ps1` files |

Checks, in hook order: `secret-scan` (`scripts/scan_secrets.py --staged`),
`ruff-format` (`scripts/check_ruff_format.py --staged`),
`commit-pathspec-safety` (`scripts/check_commit_pathspec_safety.py
--staged`), `projection-drift` (`scripts/check_projection_drift.py
--staged`) and `powershell-syntax`, a parse of the staged `.ps1` files that
passes as skipped when no PowerShell executable is found. Exit `1` when any
hard check failed or was inconclusive, otherwise `0`.

---

### gt push preflight

Run the pre-push redacted secret range scans over the ref updates Git
supplies on stdin.

```
gt push preflight [--json] [--evidence-out <path>] [--python-bin <exe>]   # reads the pre-push ref updates from stdin
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the evidence packet as JSON |
| `--evidence-out` / `--evidence-file` | path | none | Also write the evidence packet JSON to this path |
| `--python-bin` | string | current interpreter | Python executable used for the secret range scans |

The command reads the Git pre-push `local_ref local_sha remote_ref
remote_sha` lines from standard input and records one check per ref update
(`pre-push-ref-<n>`) with redacted evidence; matched values are never
printed. Exit `1` on a hard failure or inconclusive check, otherwise `0`.

---

### gt push readiness

Run a read-only, non-interactive push readiness diagnostic.

```
gt push readiness [--json] [--evidence-out <path>] [--remote <name>] [--hostname <host>] [--timeout-seconds <n>]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the evidence packet as JSON |
| `--evidence-out` / `--evidence-file` | path | none | Also write the evidence packet JSON to this path |
| `--remote` | string | `origin` | Git remote to check |
| `--hostname` | string | `github.com` | GitHub hostname for `gh auth status` |
| `--timeout-seconds` | integer | `15` | Per-command timeout |

Checks: the configured Git `credential.helper`, `gh auth status` for the
hostname, reachability of the remote, and the interactive-prompt risk of a
push. No push is performed and no prompt is answered. Exit `1` on a hard
failure or inconclusive check, otherwise `0`.

---

### gt hygiene worktrees

Report Git checkout observations for the repository without inferring
context liveness or disposal eligibility.

```
gt hygiene worktrees [--root <path>] [--integration-ref <ref>] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--root` | path | `.` | Repository root to inspect; the literal default `.` means the configured project root, any other value is used as given |
| `--integration-ref` | string | `develop` | Integration ref used to decide whether a checkout's `HEAD` is already integrated |
| `--json` | flag | off | Emit one object per checkout |

**Output:** one line per checkout other than the root (`classification`,
`candidate_action`, `dirty`, `untracked`, path) followed by a reminder that
Git observations do not establish liveness or disposal eligibility and the
per-classification counts. Classifications: `holds_work` (tracked changes,
untracked files, or a `HEAD` not reachable from the integration ref),
`no_reported_work`, `unknown` (an observation could not be made) and
`orphaned_checkout` (a directory under `.worktrees/` that Git does not list;
its content is not inspected). `candidate_action` is always `report_only`.
The `--root` must be the exact checkout root (`not_checkout_root`); a
redirected `.worktrees` directory is refused (`worktree_root_redirected`);
Git unavailable or slower than the 15-second read timeout is
`git_observation_unavailable`. Ignored files and current artifact claims are
outside this report: a clean status does not make a checkout disposable.

---

### gt env plan

Plan the local environment source-of-truth migration for an application
without printing any values.

```
gt env plan [--app agent-red] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--app` | string | `agent-red` | Application env layout to inspect; `agent-red` is the only supported value |
| `--json` | flag | off | Emit the plan as JSON |

The plan classifies the keys of the project root `.env.local` (application
keys by prefix, such as `AGENT_RED_`, `SHOPIFY_`, `NEXT_PUBLIC_`, `VITE_`,
`ADMIN_`, `STANDALONE_`, `PROVIDER_`) against the application's own
`applications/Agent_Red/.env.local` and its three generated admin views
(`admin/shopify`, `admin/standalone`, `admin/provider`), and reports the
planned moves, duplicate keys and diagnostics. Values are parsed only to be
preserved opaquely; the CLI never renders them. Read-only.

---

### gt env check

Check whether the local env files are safe to migrate.

```
gt env check [--app agent-red] [--json]
```

Same plan as `gt env plan`, exiting `1` when the plan is not
`ok_for_apply` (for example duplicate keys across sources or a malformed
file) and `0` when `gt env migrate --apply` would proceed. Read-only.

---

### gt env migrate

Move the application's env keys from the project root `.env.local` to the
application source of truth and regenerate the admin views.

```
gt env migrate [--app agent-red] [--dry-run | --apply] [--json]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--app` | string | `agent-red` | Application env layout to migrate |
| `--dry-run` | flag | off | Report the moves without changing files (also the behaviour without `--apply`) |
| `--apply` | flag | off | Apply the migration when the checks pass |
| `--json` | flag | off | Emit the result as JSON |

`--dry-run` and `--apply` are mutually exclusive. Without `--apply` the
result reports `applied = false` with the counts. With `--apply`, a plan that
is not safe (`gt env check`) or an application key already present in the
application source of truth is refused before any write; otherwise the moved
keys are removed from the root file and appended to
`applications/Agent_Red/.env.local`, the three admin views are regenerated
with the marker `# Generated by gt env migrate.`, and the result lists the
`touched_paths` (project-relative) and counts.

---

### gt controls show

Show the live operational-control artifact
(`config/governance/operational-controls.toml`): exact values, units,
metadata, invariants and source identity, as JSON.

```
gt controls show
```

Output: `schema_version`, `catalog_sha256` (the value `gt controls set`
requires as `--expected-sha256`), `source_reference`, `controls` (sorted by
key; decimal values are exact strings) and `invariants`. The artifact is read
afresh; there is no environment, package or cached fallback. Read-only.

---

### gt controls validate

Validate the canonical control artifact, or an explicit proposed TOML file,
without writing.

```
gt controls validate [--input <toml>]
```

Without `--input` the live artifact is validated; with it, the proposed file
(at most 256 KiB) is validated against the same bounded format. Output:
`{"valid": true, "catalog_sha256": ..., "control_count": ...}`; an invalid
artifact is reported as an error and exits `1`.

---

### gt controls diff

Compare the current and a proposed control artifact without writing.

```
gt controls diff --input <toml>
```

Both documents are validated and compared as `gt controls show` renders
them. The JSON result carries `before_sha256`, `after_sha256`, `controls`
(only the keys whose definition differs, each as `{"before", "after"}`) and
`invariants` (`before` and `after` lists). Read-only.

---

### gt controls set

Validate a proposed control artifact and atomically replace the live one for
subsequent operations.

```
gt controls set --input <toml> --expected-sha256 <sha256>
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--input` | path | *required* | Proposed complete replacement artifact (TOML, at most 256 KiB) |
| `--expected-sha256` | string | *required* | The `catalog_sha256` observed with `gt controls show`; stale input is refused |

The replacement is validated as a whole, the current bytes are compared with
the expected digest (`generation_conflict` when the artifact changed since
the read), a replacement that removes a control required by a configured
consumer is refused (`consumer_contract`), and the file is replaced once with
a fsynced temporary file and read back (`readback_conflict` on drift).
Output: `changed`, `before_sha256`, `catalog_sha256`, `reload_behavior =
"next_operation"`, `control_count`. Operations read the artifact afresh at
their own boundary; no running process is signalled.

---

### gt registry inspect

Inspect the canonical SoT declaration (`config/registry/sot-artifacts.toml`),
the actual identity of the declared objects and current path coverage.

```
gt registry inspect [--json] [--no-census]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the complete inspection as JSON |
| `--no-census` | flag | off | Skip the deterministic whole-root census |

Text output prints `Registry coherent: true|false`, the record count and, if
the declaration could not be read or validated, the error. Read-only; the
exit code is `0` regardless of coherence (`gt registry validate` is the
gate).

---

### gt registry inventory

Inspect declared artifact coverage without changing files or domain state.

```
gt registry inventory [--json]
```

Text output: the artifact and scanned file counts, the number of blocking
findings, the path-class counts and one line per registry finding
(`<artifact id>: <code> (<storage path>)`). `--json` emits the complete
report (`summary`, `registry_findings` and the expanded inventory).
Read-only; exit `0`.

---

### gt registry scan-strings

Scan the contents of the declared files for literal strings; no database,
membership or work-state mutation.

```
gt registry scan-strings [--match <literal> ...] [--match-file <path> ...] [--critical-class <class> ...] [--critical-path <glob> ...] [--json] [--report-only]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--match` | string (repeatable) | none | Literal to find in the declared files |
| `--match-file` | path (repeatable) | none | File of literals: one per line (`#` comments ignored), a JSON array, or a JSON object with `matches` or `strings` |
| `--critical-class` | string (repeatable) | none | Artifact ID, domain or lifecycle whose hits are `critical` |
| `--critical-path` | glob (repeatable) | none | Project-relative path pattern whose hits are `critical` |
| `--json` | flag | off | Emit the complete scan report |
| `--report-only` | flag | off | Report findings without a finding-driven non-zero exit |

Hits are `critical` when they match a critical class or path and `warn`
otherwise. The default output is a Markdown ledger; `--json` emits the report
with `summary` (`critical`, `warn`), the hits and `missing_artifacts`
(declared paths that do not exist). Exit `1` when any critical hit or missing
artifact is reported, unless `--report-only`.

---

### gt registry reconcile

Reconcile registry membership through the five typed observers
(`capability_inventory`, `governed_knowledge`, `package_and_entrypoint`,
`registered_dependency_closure`, `physical_census`). Observers establish that
a present path is load-bearing; they never grant membership, and the
declaration is not changed.

```
gt registry reconcile [--json] [--deep] [--batch-output <file>]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--json` | flag | off | Emit the complete machine-readable report |
| `--deep` | flag | off | Inspect disposable descendants instead of emitting pruned envelopes |
| `--batch-output` | path | none | Write the explicit additive declarations (`batch_records`) to a new JSON file inside the project root, for `gt registry register --batch-file` |

Text output: `membership_complete`, the counts of unregistered load-bearing
paths and invalid/unknown paths, the number of admission candidates and the
number of pruned envelopes, plus the batch path when written. `--batch-output`
refuses an existing file or a path outside the project root.

---

### gt registry register

Register current artifact membership in the canonical declaration.

```
gt registry register (--record-json <json> | --batch-file <path>) [--expected-declaration-digest <sha256>] [--dry-run]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--record-json` | string | none | One explicit declaration as a JSON object |
| `--batch-file` | path | none | JSON array of explicit declarations (relative paths resolve against the project root) |
| `--expected-declaration-digest` | string | none | Refuse when the canonical declaration's SHA-256 changed since this read |
| `--dry-run` | flag | off | Validate the current source and the intended result without writing |

Exactly one of `--record-json` and `--batch-file` is required. Each
declaration is validated as a record, then against the actual artifact and
the resolver (identity, coverage, dependencies); an archived record may be
re-registered with a live lifecycle. The declaration file is replaced once,
under a cooperative writer lock, and read back. Output (also for `--dry-run`):
`changed`, `dry_run`, `control_catalog_sha256`, `before_digest`,
`declaration_digest`, `record_count`, `changed_ids`. A declaration that
changed during validation is refused; read current state and retry.

---

### gt registry amend

Amend a declaration's metadata without concealing a locator or lifecycle
change.

```
gt registry amend <ENTRY_ID> --changes-json <json> [--expected-declaration-digest <sha256>] [--dry-run]
```

`--changes-json` is a JSON object of non-identity fields only: `domain`,
`authority_spec_id`, `mutation_api`, `versioning_policy`, `backup_policy`,
`restore_action`, `health_check_function`, `owner_role`, `depends_on`,
`forbidden_substitutes`, `notes`. A change to `storage_path`,
`coverage_mode` or `lifecycle` is refused here and belongs to `gt registry
transition`. Output and write mechanics are those of `gt registry register`.

---

### gt registry transition

Reconcile a declaration to the actual artifact result: a moved or re-scoped
locator, a lifecycle change, or a membership removal. This command does not
move or delete files.

```
gt registry transition <ENTRY_ID> (--changes-json <json> | --remove) [--removal <id> ...] [--removals-file <path>] [--expected-declaration-digest <sha256>] [--dry-run]
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--changes-json` | string | none | Postimage fields: `storage_path`, `coverage_mode`, `lifecycle` and the metadata fields of `gt registry amend` |
| `--remove` | flag | off | Remove the membership, only when the existing content retains coverage or is absent |
| `--removal` | string (repeatable) | none | Related declaration ID removed in the same atomic change |
| `--removals-file` | path | none | UTF-8 JSON array of related IDs removed in the same atomic change |
| `--expected-declaration-digest` | string | none | Refuse when the declaration changed since this read |
| `--dry-run` | flag | off | Validate without writing |

Exactly one of `--changes-json` and `--remove` is required. The intended
postimage is validated against the actual artifact and the affected coverage
before the declaration is replaced once and read back; output is that of
`gt registry register`.

---

---

## Command Tree

```
gt [--config <path>] [--version]
├── application
│   ├── inspect --host-root [--json]
│   └── register <NAME> --host-root [--json]
├── assert [--spec] [--triggered-by] [--json]
├── authority
│   ├── resolve <SUBJECT> [--scope] [--json]
│   └── status [--scope] [--json]
├── backlog
│   ├── list [--status] [--priority] [--search] [--limit] [--after] [--json]
│   ├── readiness <WORK_ITEM_ID> [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--project-id] [--json]
│   └── show <WORK_ITEM_ID> [--history] [--json]
├── bridge
│   ├── abandon <DOCUMENT> --native-context-id --expected-version --reason [--json]
│   ├── artifacts <DOCUMENT> [--json]
│   ├── check <DOCUMENT> --native-context-id --fence [--json]
│   ├── check-delivery <DOCUMENT> --version --native-context-id [--json]
│   ├── check-effects --native-context-id --cwd --path ... [--json]
│   ├── claim <DOCUMENT> --native-context-id --expected-version --status --request-id [--work-item-id] [--json]
│   ├── deliver <DOCUMENT> --native-context-id --fence --content-file [--headless] [--json]
│   ├── publish-work <DOCUMENT> --native-context-id --fence --preimages-file [--json]
│   ├── queue --role [--json]
│   ├── release <DOCUMENT> --native-context-id --fence [--json]
│   ├── show <DOCUMENT> [--content] [--json]
│   ├── state-report [--json | --markdown]
│   └── worktree <DOCUMENT> --native-context-id --fence [--json]
├── commit
│   └── preflight [--json] [--evidence-out] [--python-bin] [--powershell-bin]
├── config [--json]
├── context
│   ├── session --native-context-id [--json]
│   └── work-item <WORK_ITEM_ID> [--json]
├── controls
│   ├── diff --input
│   ├── set --input --expected-sha256
│   ├── show
│   └── validate [--input]
├── core-specs
│   ├── answer --project-id --slot --expected-version --actor --reason [--value] [--source] [--spec-id] [--json]
│   ├── next-question (--project-id | --project-name) [--json] [--opt-out-core-spec-intake]
│   └── status (--project-id | --project-name) [--json] [--no-fail] [--opt-out-core-spec-intake]
├── dashboard
│   ├── init [--schema-only] [--db-path] [--runtime-root] [--json]
│   ├── install [--grafana-home] [--skip-download] [--skip-plugin] [--json]
│   ├── refresh [--probe-live] [--db-path] [--runtime-root] [--json]
│   ├── serve [--db-path] [--runtime-root] [--port] [--grafana-port] [--interval-minutes]
│   ├── start [--db-path] [--runtime-root] [--grafana-home] [--grafana-port] [--refresh-port] [--interval-minutes] [--json]
│   └── stop [--runtime-root] [--json]
├── db
│   └── postgres
│       ├── export-current [--sqlite-snapshot] [--transform-plan] [--output] [--preflight-only]
│       ├── import-current --input --actor --reason
│       ├── init [--upgrade-from]
│       ├── readback-current --output
│       └── status
├── deliberations
│   ├── list [--search] [--source-type] [--spec-id] [--work-item-id] [--after] [--limit] [--json]
│   └── show <DELIB_ID> [--history] [--json]
├── design
│   └── inspect <HANDOFF> [--date] [--session-id] [--owner-decision] [--notes] [--json]
├── env
│   ├── check [--app] [--json]
│   ├── migrate [--app] [--dry-run | --apply] [--json]
│   └── plan [--app] [--json]
├── harness
│   ├── diagnostic --harness-id [--native-context-id] [--json]
│   ├── list [--status] [--search] [--limit] [--after] [--json]
│   ├── project <HARNESS> [--validate | --check | --dry-run]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <HARNESS_ID> [--history] [--json]
├── hygiene
│   └── worktrees [--root] [--integration-ref] [--json]
├── kb
│   └── reconcile [--orphans] [--stale] [--authority] [--duplicates] [--provisionals]
│       [--all] [--stale-days <N>] [--activity-days <N>] [--project-root <path>] [--json]
├── project
│   ├── chroma
│   │   └── regenerate [--dir] [--scope] [--dry-run] [--json]
│   ├── classify-tree --dir [--output] [--format] [--max-depth] [--ignore-glob ...]
│   ├── doctor --project-id --host-root [--json]
│   ├── init <APPLICATION> --project-id --host-root --owner [--profile] [--copyright]
│   │   [--cloud-provider] [--harness ...] [--include-ci/--no-include-ci]
│   │   [--seed-example/--no-seed-example] [--integrations/--no-integrations]
│   │   [--python-version] [--spec-scaffold] [--opt-out-core-spec-intake] [--dry-run] [--json]
│   └── upgrade <APPLICATION> --project-id --host-root [--harness ...] [--apply | --recover] [--json]
├── projects
│   ├── check-commit <PROJECT_ID> --native-context-id --expected-version --commit-id --expected-parent --index-tree [--json]
│   ├── commit <PROJECT_ID> --native-context-id --expected-version --message-file [--json]
│   ├── commit-failed <PROJECT_ID> --native-context-id --expected-version --reason --evidence [--json]
│   ├── confirm-commit <PROJECT_ID> --native-context-id --expected-version --commit-id --expected-parent [--json]
│   ├── dependencies
│   │   ├── list [--status] [--dependent-project] [--prerequisite-project] [--affected-gate] [--limit] [--after] [--json]
│   │   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   │   └── show <DEPENDENCY_ID> [--history] [--json]
│   ├── formal-links
│   │   ├── list [--status] [--project-id] [--limit] [--after] [--json]
│   │   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   │   └── show <LINK_ID> [--history] [--json]
│   ├── list [--status] [--kind] [--repository-ref] [--search] [--limit] [--after] [--json]
│   ├── move-item --work-item-id --from-project --to-project --expected-version [--membership-order]
│   │   --actor --change-reason [--json]
│   ├── prepare-commit <PROJECT_ID> --native-context-id --expected-version [--json]
│   ├── readiness <PROJECT_ID> [--gate] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--kind] [--json]
│   ├── set-authorization <PROJECT_ID> --authorization --expected-version --actor --change-reason [--json]
│   └── show <PROJECT_ID> [--history] [--json]
├── push
│   ├── preflight [--json] [--evidence-out] [--python-bin]
│   └── readiness [--json] [--evidence-out] [--remote] [--hostname] [--timeout-seconds]
├── registry
│   ├── amend <ENTRY_ID> --changes-json [--expected-declaration-digest] [--dry-run]
│   ├── inspect [--json] [--no-census]
│   ├── inventory [--json]
│   ├── list [--domain] [--lifecycle] [--json]
│   ├── reconcile [--json] [--deep] [--batch-output]
│   ├── register (--record-json | --batch-file) [--expected-declaration-digest] [--dry-run]
│   ├── scan-strings [--match ...] [--match-file ...] [--critical-class ...] [--critical-path ...] [--json] [--report-only]
│   ├── show <ENTRY_ID> [--json]
│   ├── transition <ENTRY_ID> (--changes-json | --remove) [--removal ...] [--removals-file]
│   │   [--expected-declaration-digest] [--dry-run]
│   └── validate [--json]
├── scaffold
│   ├── cicd [--profile azure-enterprise] [--apply | --dry-run] [--target-dir]
│   ├── iac [--profile azure-enterprise] [--apply | --dry-run] [--target-dir]
│   └── specs --project-id [--profile <minimal|full>] [--apply | --dry-run] [--actor] [--json]
├── secrets
│   └── scan [PATH_ARGS ...] [--staged] [--range] [--paths] [--tracked] [--all-refs] [--redacted] [--json]
│       [--report-json] [--fail-on]
├── service
│   ├── serve [--port]
│   └── status [--json]
├── session
│   ├── bind --native-context-id --init-keyword [--json]
│   └── show --native-context-id [--json]
├── spec
│   ├── list [--status] [--priority] [--application-scope] [--scope] [--search] [--limit] [--after] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <SPEC_ID> [--history] [--json]
├── status [--json] [--startup] [--native-context-id] [--component ...]
├── terms
│   ├── list [--status] [--scope] [--authority-level] [--search] [--limit] [--after] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <TERM_ID> [--history] [--json]
├── test-phases
│   ├── list [--plan-id] [--search] [--limit] [--after] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <PHASE_ID> [--history] [--json]
├── test-plans
│   ├── list [--status] [--search] [--limit] [--after] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <PLAN_ID> [--history] [--json]
├── tests
│   ├── list [--spec-id] [--application-scope] [--search] [--limit] [--after] [--json]
│   ├── record --id --fields-file --expected-version --actor --change-reason [--json]
│   └── show <TEST_ID> [--history] [--json]
└── validate
    └── spec-coherence --output [--rule-set] [--format] [--fail-on-findings]
```

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

## Complete Command Reference

_Index of every `gt` leaf command in the live Click command tree (`groundtruth_kb.cli.main`), one table per
top-level group. It is maintained by hand from `gt <group> <command> --help` and verified by
`scripts/check_docs_cli_coverage.py`, which fails when a live command is missing from this document. The sections
above give detailed usage for every command; this index is the complete inventory. The package `gt` CLI is the
primary interface._

### gt application

| Command | Description |
| --- | --- |
| `gt application inspect` | Read local application catalog, marker and artifact-boundary facts. |
| `gt application register` | Register a catalog entry and matching marker while preserving existing files. |

### gt assert

| Command | Description |
| --- | --- |
| `gt assert` | Observe current definitions from one selected authority without canonical writes. |

### gt authority

| Command | Description |
| --- | --- |
| `gt authority resolve` | Resolve an exact current name, ID or accepted synonym without a static map. |
| `gt authority status` | Check current terminology interpretation and formal-source references. |

### gt backlog

| Command | Description |
| --- | --- |
| `gt backlog list` | List current work-item records in deterministic ID order. |
| `gt backlog readiness` | Explain whether this item's reviewed or committed predecessors are available. |
| `gt backlog record` | Apply a version-checked work-item amendment (`--project-id` for new work) and return canonical readback. |
| `gt backlog show` | Read one current work-item record, including its project membership. |

### gt bridge

| Command | Description |
| --- | --- |
| `gt bridge abandon` | Abandon a broken or invalidated attempt when no live claim remains. |
| `gt bridge artifacts` | Identify current Git-normalized artifact bytes; this is not a verdict. |
| `gt bridge check` | Check that the exact current artifact claim is still live and current. |
| `gt bridge check-delivery` | Verify this context's exact assigned delivery, including the purged terminal head. |
| `gt bridge check-effects` | Check current scratch/implementation scope without granting or recording permission. |
| `gt bridge claim` | Reserve one exact successor slot for 600 seconds, without renewal. |
| `gt bridge deliver` | Publish the author's complete UTF-8 bytes and consume the exact claim. |
| `gt bridge publish-work` | Publish only the claimed artifacts from this context's registered checkout. |
| `gt bridge queue` | Report eligible next actions for owner or dispatcher selection. |
| `gt bridge release` | Release the exact current artifact claim without delivering. |
| `gt bridge show` | Read canonical attempt state and optionally its available bridge messages. |
| `gt bridge state-report` | Report canonical attempts, exact claims and role queues without harness configuration. |
| `gt bridge worktree` | Materialize current project work into only the receiving context's checkout. |

### gt commit

| Command | Description |
| --- | --- |
| `gt commit preflight` | Run staged commit governance checks with structured evidence. |

### gt config

| Command | Description |
| --- | --- |
| `gt config` | Show resolved settings without probing services or optional dependencies. |

### gt context

| Command | Description |
| --- | --- |
| `gt context session` | Read an existing binding, current startup requirements and authored baseline. |
| `gt context work-item` | Read current work, linked formal requirements, test instructions and prerequisites together. |

### gt controls

| Command | Description |
| --- | --- |
| `gt controls diff` | Compare current and proposed control definitions and invariants without writing. |
| `gt controls set` | Validate and atomically replace the selected artifact for subsequent operations. |
| `gt controls show` | Show exact live values, units, metadata, invariants and source identity as JSON. |
| `gt controls validate` | Validate the canonical artifact or an explicit proposed TOML file without writing. |

### gt core-specs

| Command | Description |
| --- | --- |
| `gt core-specs answer` | Apply one explicit owner answer to a core-spec intake slot through the specification writer. |
| `gt core-specs next-question` | Report the next missing core-spec intake question. |
| `gt core-specs status` | Report baseline core-spec intake completion state. |

### gt dashboard

| Command | Description |
| --- | --- |
| `gt dashboard init` | Create derived reporting data and Grafana assets without starting services. |
| `gt dashboard install` | Install Grafana OSS and its SQLite plugin into the selected local installation. |
| `gt dashboard refresh` | Refresh native observations and derived display assets without selecting work. |
| `gt dashboard serve` | Serve the installed display on loopback, refreshing the selected native authority. |
| `gt dashboard start` | Start the local display and Grafana, returning only after readiness checks. |
| `gt dashboard stop` | Stop the launches recorded for this runtime after checking process identity. |

### gt db

| Command | Description |
| --- | --- |
| `gt db postgres export-current` | Export reviewed current state from one immutable SQLite snapshot. |
| `gt db postgres import-current` | Import one complete canonical current-state manifest. |
| `gt db postgres init` | Initialize an empty schema or explicitly transition a known predecessor. |
| `gt db postgres readback-current` | Publish a canonical current-state readback manifest. |
| `gt db postgres status` | Read PostgreSQL kernel status without creating or repairing objects. |

### gt deliberations

| Command | Description |
| --- | --- |
| `gt deliberations list` | List historical deliberation records in deterministic ID order. |
| `gt deliberations show` | Read one historical deliberation record by ID. |

### gt design

| Command | Description |
| --- | --- |
| `gt design inspect` | Inspect a local Claude Design handoff (file list, sizes, format warnings); publishes nothing. |

### gt env

| Command | Description |
| --- | --- |
| `gt env check` | Check whether local env files are safe for app SoT migration. |
| `gt env migrate` | Move app env keys to the Agent Red SoT and generate admin views. |
| `gt env plan` | Plan Agent Red local env SoT migration without printing values. |

### gt harness

| Command | Description |
| --- | --- |
| `gt harness diagnostic` | Read local diagnostics; metadata does not qualify actual host behavior. |
| `gt harness list` | List current harness installation records in deterministic ID order. |
| `gt harness project` | Derive one harness configuration from the selected project's canonical baseline. |
| `gt harness record` | Apply a version-checked harness record amendment and return canonical readback. |
| `gt harness show` | Read one current harness installation record. |

### gt hygiene

| Command | Description |
| --- | --- |
| `gt hygiene worktrees` | Report checkout observations without inferring liveness or disposal eligibility. |

### gt kb

| Command | Description |
| --- | --- |
| `gt kb reconcile` | Run the read-only provenance and consistency detectors over the active specifications of the configured authority; writes nothing. |

### gt project

| Command | Description |
| --- | --- |
| `gt project chroma regenerate` | Rebuild the application's disposable ChromaDB cache from the authority's current records. |
| `gt project classify-tree` | Classify every path of a tree against the target's current declarations; read-only, no authority needed. |
| `gt project doctor` | Inspect an initialized application against the authority. |
| `gt project init` | Create application files for an explicitly selected project; no commit, no local database. |
| `gt project upgrade` | Preview, apply or recover managed application files from the host baseline. |

### gt projects

| Command | Description |
| --- | --- |
| `gt projects check-commit` | Check a candidate commit against the prepared cohort before the reference update. |
| `gt projects commit` | Commit the complete reviewed project through the native service and normal hooks. |
| `gt projects commit-failed` | Record that the complete project commit did not complete; fresh verification is requested. |
| `gt projects confirm-commit` | Confirm the identity of the complete reviewed Git commit and record project completion. |
| `gt projects dependencies list` | List current project dependency records in deterministic ID order. |
| `gt projects dependencies record` | Apply a version-checked project dependency amendment and return canonical readback. |
| `gt projects dependencies show` | Read one current project dependency record. |
| `gt projects formal-links list` | List current project formal-link records in deterministic ID order. |
| `gt projects formal-links record` | Apply a version-checked project formal-link amendment and return canonical readback. |
| `gt projects formal-links show` | Read one current project formal-link record. |
| `gt projects list` | List current program and project records in deterministic ID order. |
| `gt projects move-item` | Move one open work item atomically, preserving both projects' authorization. |
| `gt projects prepare-commit` | Prepare the complete project Git commit and materialize the verifying checkout. |
| `gt projects readiness` | Explain whether the project's exact prerequisite outcomes are available. |
| `gt projects record` | Apply a version-checked program or project amendment and return canonical readback. |
| `gt projects set-authorization` | Apply the owner's explicit ordering choice; existing bridge chains continue. |
| `gt projects show` | Read one current program or project record, including its planning relationships. |

### gt push

| Command | Description |
| --- | --- |
| `gt push preflight` | Run pre-push redacted secret range scans from Git pre-push stdin. |
| `gt push readiness` | Run a read-only non-interactive push readiness diagnostic. |

### gt registry

| Command | Description |
| --- | --- |
| `gt registry amend` | Amend metadata without concealing a locator or lifecycle change. |
| `gt registry inspect` | Inspect the canonical declaration, actual identity and current coverage. |
| `gt registry inventory` | Inspect declared artifact coverage without changing files or domain state. |
| `gt registry list` | List artifact records from the current canonical declaration. |
| `gt registry reconcile` | Reconcile registry membership through all five typed observers. |
| `gt registry register` | Register current artifact membership in the canonical declaration. |
| `gt registry scan-strings` | Scan declared file contents; no database, membership or work-state mutation. |
| `gt registry show` | Show details of a single SoT artifact record by id. |
| `gt registry transition` | Reconcile the declaration to the actual artifact result; this does not move or delete files. |
| `gt registry validate` | Validate declaration schema, actual identity and current path coverage. |

### gt scaffold

| Command | Description |
| --- | --- |
| `gt scaffold cicd` | Generate GitHub Actions CI/CD skeleton files for the given profile (D4). |
| `gt scaffold iac` | Generate Terraform skeleton files for the given profile (D3). |
| `gt scaffold specs` | Generate a starter set of inferred specifications for one execution project. |

### gt secrets

| Command | Description |
| --- | --- |
| `gt secrets scan` | Run the shared scanner without exposing raw matched values. |

### gt service

| Command | Description |
| --- | --- |
| `gt service serve` | Serve an initialized PostgreSQL domain on IPv4 loopback only. |
| `gt service status` | Read status from the configured service; never open a client database. |

### gt session

| Command | Description |
| --- | --- |
| `gt session bind` | Return the initialization outcome and immutable binding for the received marker. |
| `gt session show` | Resolve the supplied native context, with no fallback to another session. |

### gt spec

| Command | Description |
| --- | --- |
| `gt spec list` | List current specification records in deterministic ID order. |
| `gt spec record` | Apply a version-checked specification amendment and return canonical readback. |
| `gt spec show` | Read one current specification record. |

### gt status

| Command | Description |
| --- | --- |
| `gt status` | Compact read-only operating status from fresh native reads; unavailable facts are reported, never inferred. |

### gt terms

| Command | Description |
| --- | --- |
| `gt terms list` | List current canonical term records in deterministic ID order. |
| `gt terms record` | Apply a version-checked canonical term amendment and return canonical readback. |
| `gt terms show` | Read one current canonical term record. |

### gt test-phases

| Command | Description |
| --- | --- |
| `gt test-phases list` | List current test-plan phase records in deterministic ID order. |
| `gt test-phases record` | Apply a version-checked test-plan phase amendment and return canonical readback. |
| `gt test-phases show` | Read one current test-plan phase record. |

### gt test-plans

| Command | Description |
| --- | --- |
| `gt test-plans list` | List current test plan records in deterministic ID order. |
| `gt test-plans record` | Apply a version-checked test plan amendment and return canonical readback. |
| `gt test-plans show` | Read one current test plan record. |

### gt tests

| Command | Description |
| --- | --- |
| `gt tests list` | List current test artifact records in deterministic ID order. |
| `gt tests record` | Apply a version-checked test artifact amendment and return canonical readback. |
| `gt tests show` | Read one current test artifact record. |

### gt validate

| Command | Description |
| --- | --- |
| `gt validate spec-coherence` | Scan active specifications; candidates are not verdicts or verification. |
