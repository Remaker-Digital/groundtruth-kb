# GroundTruth-KB

GroundTruth-KB coordinates specification-linked work through a native PostgreSQL
domain service and the `gt` CLI. Programs plan and sequence projects. A work item
has one parent project; project authorization orders dispatch and admission of
NEW implementation proposals. Changing that field does not cancel an initiated
chain. A complete project is committed after its work items have been
independently verified in their final form.

Builder and reviewer roles belong to immutable context bindings. Fresh contexts
exchange ephemeral messages through the native bridge service. A claim reserves
one exact successor artifact, not a work-item thread. Current records and formal
history remain in the authoritative database; bridge payloads are disposable.

## Start with the selected native service

Use the CLI installed for the same GT-KB installation as its native service.
Configure the project root and service URL in the selected `groundtruth.toml`:

```toml
[groundtruth]
project_root = "E:/GT-KB"
authority_url = "http://127.0.0.1:8765"
```

These commands read the selected installation:

```powershell
gt --help
gt --config E:\GT-KB\groundtruth.toml service status --json
gt --config E:\GT-KB\groundtruth.toml projects list --json
gt --config E:\GT-KB\groundtruth.toml backlog list --json
```

The native service must already be installed, initialized and running. Ordinary
knowledge and bridge commands use its HTTP API; they do not initialize a local
SQLite authority or borrow database credentials from the caller. If the service
is unavailable, follow the installation's operator recovery procedure and read
current state again before continuing work.

Record responses have readable labels and details. Non-record responses,
including explicit null or scalar values inside a response wrapper, remain JSON
instead of causing a presentation traceback. `--json` preserves the complete
response, including precise numeric values, for callers that need structured
output. Rendering a response does not verify its underlying work.

## Work and verification

Use `gt context work-item` for an assigned work item and `gt bridge` for current
messages and next-artifact claims. Required role and activity inputs come from
the dispatch or owner; context loading does not invent them. Source changes,
claims and independent review are checked again at their relevant boundaries.

`VERIFIED` records independent review completion for exact Git mode and object
identities. It does not claim a commit. The native project finalization commands
check the complete reviewed project and its actual Git result, preserving foreign
work and requiring fresh review when the reviewed result changes. Publication,
actual-host qualification and operational installation remain separate concerns.

The commands below describe the native platform and explicit local tools.
Application inspection does not establish application lifecycle support, and
generated dashboards do not establish host or release qualification. The former
SQLite bootstrap, durable file-bridge setup and scaffold-profile guides are not
the current native-service setup procedure.


## Current GT-KB task context

For an assigned work item, `gt context work-item WI-NNNN --json` reads the
native authority's current work, project, declared formal requirements and test
instructions. Missing or inactive required sources and unavailable authority
produce a non-success result. The declared relationship closure is a minimum;
it does not replace judgment about additional applicable requirements.

Amend existing open planning records through `gt backlog record --id WI-NNNN
--fields-file change.json --expected-version N --actor CONTEXT --change-reason
REASON --json`. A progress note, priority or predecessor change can preserve an
existing evidence gap while it is reconciled. New implementation work and
changes to specification/test links require complete executable evidence and
an active test-plan phase. Proposal publication separately rechecks that
evidence and the current work-item version. Planning updates retain the work's
current completion state and project membership; read back both after a change.

The descriptor manifest/freshness APIs and standalone modernization workflow
and qualification commands are retired. Their metadata, copied profiles and
frozen receipts cannot establish current requirements or completed work. Fresh
and successor contexts use the ordinary CLI and Bridge interface. Complete
installed startup, activity loading and migration qualification remain required.

## Assertions

`gt --config <path> assert [--spec ID] [--json]` reads the selected native HTTP
authority and evaluates files relative to that configuration's project root,
including when invoked elsewhere. One invocation keeps its initially selected
authority; a changed authority URL or project root invalidates its result. It
re-reads each definition, including explicitly inactive definitions, and refuses
malformed, duplicate or non-advancing inventory pages. It never falls back to a
local database or records assertion history or canonical test/work results.

Only a fully evaluated passing selection exits zero. Empty selections and active
definitions without executable assertions are `UNASSESSED`; mixed evaluated and
unassessed obligations are `PARTIAL`. Explicitly selected retired or superseded
definitions are `NOT_APPLICABLE` only while their canonical identity/version/status
remain unchanged. These are structural observations, not independent behavioral
verification or permission to commit or activate work.

## Registry and configuration selection

Configuration discovery occurs once in `GTConfig.load`. With `discover=False`,
an absent selected file uses explicit overrides, environment settings and defaults;
it never loads a configuration from the caller's directories. An explicitly
selected file is still read and validated, with override/environment precedence.

`gt --config <path> config [--json]` reports the resolved application title,
absolute project root, native authority URL, PostgreSQL service name and client
timeouts. JSON keeps an absent authority URL and unset Chroma path as `null`.
Retained `db_path` and `chroma_path` values appear under `legacy_paths` in JSON
and as legacy helper paths in text. Paths are normalized to absolute paths;
their presence in the report does not assert that they exist or are usable.
The command reads configuration only: it does not open databases, query a service,
read libpq credential files, import Chroma, or establish a runtime search fallback.
Successful display does not establish service readiness or host qualification.

Registry declaration reads use the selected canonical TOML. Declaration mutations
and governed-knowledge inventory additionally require the selected native authority
for their formal/domain inputs. Missing native configuration refuses, preserving
the declaration and any local database. It cannot borrow an unrelated caller's
configuration or authorize current work from a historical SQLite database.

`gt registry inventory [--json]` reports the selected canonical declaration's
actual coverage, missing members and lifecycle/path classes. It is a read-only
inventory; completing the report does not qualify work or clear its findings.
`gt registry scan-strings --match TEXT [--match TEXT ...] [--json]` searches only
declared files. `--match-file` also accepts the existing JSON-list,
JSON-object (`matches` or `strings`) and line-based literal formats. Explicit
`--critical-class` and `--critical-path` options add critical classifications.
Neither command opens a database, queries a service or changes membership.

The scan returns nonzero for critical hits or blocking coverage findings.
Both text and JSON retain those findings. `--report-only` allows a zero exit;
invalid input and unreadable registered files still fail. Missing coverage
metadata is refused before inventory expansion and is never inferred from a
path. Historical projection inspection remains separate from current inventory.
These commands replace the removed inventory CLI entry points through the
current registry surface; they do not restore the retired `admin` command.

## Dynamic operational controls

`config/governance/operational-controls.toml` holds typed live control values,
units, bounds, consumer metadata and coupled invariants. It replaces the empty
dotenv-binding foundation. The runtime control service reads a fresh immutable
snapshot for each operation; an already running operation retains its snapshot.
Missing, invalid or incompatible controls refuse a new operation. Environment
variables and source defaults do not supply a replacement value.

The local CLI selects the same project root as other local operations:

```text
gt --config <path> controls show
gt --config <path> controls validate --input proposed-controls.toml
gt --config <path> controls diff --input proposed-controls.toml
gt --config <path> controls set --input proposed-controls.toml --expected-sha256 <catalog_sha256>
```

Outputs are JSON. `validate` without `--input` checks the current artifact.
`set` validates the complete proposed file, takes a nonblocking writer mutex,
compares the supplied current identity, replaces the file atomically and reads
it back. Coupled values change together. Invalid proposals and stale identities
leave the canonical file unchanged. A busy writer refuses visibly; there is no
hidden retry schedule. Subsequent operations observe an accepted change without
a process restart. Direct owner edits do not take the cooperative mutex; readback
detects observed concurrent changes and does not imply a transaction with an
uncooperative editor.

Registry writer acquisition, backoff, jitter and Git metadata lookup consume one
validated snapshot from that file. Their seven values preserve the prior operating
settings during consolidation; they are not a claim of optimal calibration.
The acquisition budget does not bound the entire registry operation. Successful
registry writes identify the consumed snapshot as `control_catalog_sha256`.
The old registry timeout environment override is no longer a value authority.

Other runtime consumers, their configuration stores and calibration evidence
still require migration. In particular, this first consumer does not externalize
native HTTP, PostgreSQL, bridge-claim, harness or dashboard controls, nor complete
the deterministic control inventory. Parser limits are fixed format bounds,
distinct from tunable runtime values; their classification remains subject to the
complete control-inventory review. No running production service is reconfigured
by developing or validating these sources in an isolated checkout.


## Operations dashboard

```powershell
gt --config E:\GT-KB\groundtruth.toml dashboard init
gt dashboard install
gt dashboard start
# Landing page: http://127.0.0.1:8766/
# Grafana: http://127.0.0.1:3000/d/groundtruth-kb-dashboard/gt-kb-operations-dashboard
gt dashboard refresh --json
gt dashboard stop
```

Use `--config` before `dashboard` to select the project configuration for any command.
`init` and `refresh` generate reporting data and display assets under
`<project_root>/.groundtruth/dashboard` without starting services. Counts come from
the configured native authority; missing observations remain unavailable. The
reporting SQLite database is derived data, never the knowledge authority.

`gt dashboard init --schema-only` initializes or migrates only the derived schema;
it preserves existing reporting rows and performs no refresh or display publication.
`gt dashboard refresh --probe-live` also reads current service/bridge availability
and GitHub workflow observations. Every native read uses the selected configuration.
The default refresh does not run those optional live probes. Completed collection
does not establish release readiness, complete telemetry or actual-host qualification.

`install` places Grafana under `<project_root>/.groundtruth/tools/grafana` by default.
It verifies the pinned archive before extraction, installs the pinned SQLite plugin,
and records the installed binary and plugin identities. `--grafana-home` selects
an existing local installation. `start` binds both services to loopback, confirms
readiness and reuses matching recorded launches. `stop` compares each recorded
process identity before stopping it. Direct refresh-service invocation also accepts
only numeric IPv4 loopback addresses; `--host` defaults to `127.0.0.1` independently
of environment variables. Launched refresh and Grafana children discard inherited
PostgreSQL connection variables and `GT_POSTGRES_*` overrides; the refresh service
continues to read the selected HTTP authority. It exposes its manual control
page at `/control`; applying a refresh requires its configured token.

The dashboard refresh token uses a timing-resistant byte comparison and preserves
non-ASCII tokens. Read-only requests and dry-run previews retain their existing
token rules. This does not make the entire HTTP handler constant-time.

The native project's reference-transaction callback uses a five-second HTTP socket
timeout for its authority check. A stalled check refuses the reference update;
restore authority availability and re-read current state before retrying. This
limits stalled socket I/O, not total commit duration or a slowly streaming reply.
Ordinary authority clients retain their existing timeout.

## Local application inspection

```powershell
gt application inspect --host-root "E:\GT-KB"
gt application inspect --host-root "E:\GT-KB" --json
```

`--host-root` explicitly selects the local host independently of `--config`, the
current directory and database configuration. Inspection reads the host's
`applications/registry.toml`, application identity markers and artifact registry,
and checks the actual top-level entries. It preserves application files and does
not contact the authority service or open a database. Named findings return exit
code 1; no findings return 0. An empty host reports that no application
qualification was performed. `--json` emits the same findings and per-slot facts.
These checks do not establish native application lifecycle or host qualification.

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md) for contributor onboarding.
We value feedback about the engineering method itself as much as bug reports: issues and pull
requests that reveal something about the method carry the `method-feedback` label and are triaged
monthly. Release-health evidence
is published from [docs/wiki/release-health.md](docs/wiki/release-health.md); compare the published
wiki copy with `python scripts/update_wiki_pages.py compare` before a release announcement.
This package is licensed under [AGPL-3.0](LICENSE).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.


### Operational-control inventory

Run `python scripts/timer_inventory.py --project-root <root> --json` to inspect canonical control values, potential literal controls, unresolved numeric uses, consumer-key references and read coverage. Source, test and projector-declared generated observations are separate. Private/runtime directories and foreign worktrees are excluded without reading their contents. Missing, malformed, unreadable or redirected inputs produce visible diagnostics and a nonzero exit; no scan result establishes semantic completeness or calibration.

`--write` derives `.groundtruth/derived/timer-inventory.toml`, a local derived artifact under the gitignored KB working directory: it is never committed, and `config/governance/` carries only the hand-authored control catalog (owner ruling D14, 2026-09-17). `--check` compares those derived bytes with current observations as a local operational diagnostic. A current inventory is not a full-centralization verdict. Numeric names and lexical matches require semantic review, measurement fields remain unavailable until observed, and findings do not assign ownership of work items. The live control values remain in `config/governance/operational-controls.toml`; neither the inventory nor generated harness outputs are value authorities.


The inventory Git revision probe uses `inventory.git_probe_seconds` from that operation's validated control snapshot. The 30-second value was measured on 2026-09-17 (`calibration:2026-09-17:runtime-control-calibration`, cited in the catalog's `evidence_refs`) and kept as the relaxed posture; future operations see validated replacements. An absent local `.git` marker leaves the optional revision unavailable without launching Git. A missing/invalid control, failed or timed-out probe, redirected marker or malformed revision produces explicit partial-coverage diagnostics. The probe has no source-literal or environment fallback.

`scripts/check_runtime_control_centralization.py` is the completeness evaluator DCL-CENTRAL-DYNAMIC-OPERATIONAL-CONTROLS-001 names (assertion `GHRP-DCL-CONTROL-A1`). From local files only, it proves the declared set: every active control names a wired consumer whose module exists and references the key, every key the two consumer contracts read is declared, every invariant holds, every control cites a dated calibration record (`calibration:YYYY-MM-DD[:locator]`), and the governed diff route accepts the current bytes. It then reports the inventory's unclassified or ambiguous production uses without judging them (exit 0 while the declared set is complete; `--fail-on-unresolved` turns that count into a failure; `--skip-inventory` omits the scan; `--json` emits the full evaluation; exit 1 on a finding, 2 when the catalog cannot be evaluated). Migration of the remaining production literals stays with PROJECT-GTKB-TIMER-GOVERNANCE.

The setter refuses removal of required keys for a consumer already present in the current valid catalog, including removal of the entire consumer group. Retiring such a consumer requires a coordinated authored change to the consumer contract. An invalid current artifact also refuses a setter operation without overwriting its bytes.

Dashboard diagnostics use Python logging. Service startup, access and refresh messages go to stderr under the standalone service entry point; library warnings use the existing dashboard logger. Existing logging handlers are preserved. Hook allow, deny and diagnostic JSON remains a single stdout message through the shared governance output module. The development extra includes the pinned PyYAML stubs required by strict checking; runtime PyYAML is unchanged.
