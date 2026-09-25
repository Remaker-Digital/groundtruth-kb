# PostgreSQL installation and operator tools

The authoritative placement and service boundary are defined by the current
ADR-POSTGRESQL-AUTHORITY-SUBSTRATE-001, its companion DCL, and
GOV-POSTGRESQL-LAN-AUTHORITY-SERVICE-001 in MemBase. This directory contains
installation source and operator instructions. Installing a server does not
change the selected GT-KB database.

The native Windows x64 distribution is pinned in release.json, including its
download checksum. The package comes from the EDB binary distribution linked
by the [PostgreSQL Windows download page](https://www.postgresql.org/download/windows/).
The installer extracts the server, command-line tools, extension libraries and
licenses. It does not install pgAdmin or StackBuilder.

| Location under infrastructure/postgresql | Purpose |
|---|---|
| install.py, archive_wal.py, register-service.ps1, release.json | Tracked installation source |
| runtime/<build>/ | Installed PostgreSQL binaries and archiver |
| data/ | PostgreSQL cluster |
| credentials/ | Protected administrator and service libpq configuration |
| logs/ | Seven rotating daily server logs and startup output |
| wal/ | Complete archived WAL segments |
| backups/ | Local backup staging; not protection against loss of this disk |

Runtime and state directories are ignored by Git. The installer protects
data, credentials, logs, WAL and backup staging using NTFS permissions before
writing them. The GT-KB service login is neither a superuser nor a role/database
administrator. PostgreSQL listens on 127.0.0.1 only.

From a checked-out GT-KB source tree, install into an explicit permanent root:

    & E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe infrastructure/postgresql/install.py --root E:\GT-KB

An existing cluster, credentials directory or runtime destination causes a
refusal; the installer never reinitializes or overwrites them. A failed partial
installation requires inspection, not an automatic recursive removal. An
already downloaded archive can be supplied with --archive; its pinned checksum
is still verified. This installer bootstraps a new cluster, not a version upgrade.

The initial start runs under the installing account. To register the installed
server for automatic startup, run this command in an administrator PowerShell:

    .\infrastructure\postgresql\register-service.ps1 -Root E:\GT-KB

The service is named gtkb-postgresql and runs as Windows LocalService. The
registration script grants that account access to the runtime, cluster, logs
and WAL, but not client credential files. It refuses a same-named service
pointing at another installation. After registration, verify service startup
and a new successful WAL archive under that service account.

Before service registration, the native operator commands are:

    $pg = 'E:\GT-KB\infrastructure\postgresql\runtime\18.6-3\bin'
    $data = 'E:\GT-KB\infrastructure\postgresql\data'
    & "$pg\pg_ctl.exe" status -D $data
    & "$pg\pg_ctl.exe" start -D $data -l 'E:\GT-KB\infrastructure\postgresql\logs\startup.log' -w
    & "$pg\pg_ctl.exe" stop -D $data -m fast -w

The service process uses credentials/pg_service.conf, service gtkb_authority.
Operators use gtkb_admin; no password belongs in shell arguments or agent
configuration. The administrator service intentionally has no fixed database
name so an explicitly selected isolated recovery/test database can be used.
Normal agents use the GT-KB CLI, not these database tools.

Physical backups use pg_basebackup with streamed WAL and are checked using
pg_verifybackup. The continuous archive stores complete WAL files without
overwriting different bytes; an identical retry is safe. Keep a verified base
backup and its complete required WAL sequence together. Do not prune WAL by age
alone. Copy recovery material to an out-of-band location appropriate to the
failure scenario before claiming protection against primary-storage loss.
See the [PostgreSQL recovery contract](https://www.postgresql.org/docs/18/continuous-archiving.html).

Unattended base backups and retention use the operator tool in this directory:

    & E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe infrastructure/postgresql/base_backup.py --root E:\GT-KB --keep 7

It takes one plain-format base backup with streamed WAL and a SHA-256 manifest
into backups/base-<UTC stamp>/, verifies it with pg_verifybackup, writes a JSON
record beside it, keeps the newest seven verified base backups, and prunes only
those archived WAL segments and backup-history files older than the oldest
retained backup's start segment. `--dry-run` prints the plan and changes nothing.
The tool reads the server through the protected admin service file and never
handles a password. Run it unattended from a scheduled task under the owner's
account before the nightly off-volume copy, so that the copy always carries a
verified base backup and the WAL needed after it. Every schema object travels
with the backup; the restore drill of the installed server on another volume is
recorded in the realignment evidence.

Recovery after loss of this volume uses only the off-volume copy written by the
nightly SyncBackSE job (`D:\GT-KB-LocalBackup`), through the operator tool in
this directory as it exists inside that copy:

    & D:\GT-KB-LocalBackup\groundtruth-kb\.venv\Scripts\python.exe D:\GT-KB-LocalBackup\infrastructure\postgresql\restore_from_copy.py --copy D:\GT-KB-LocalBackup --data E:\GT-KB\infrastructure\postgresql\data --port 5432

Any Python 3.11+ interpreter runs it; it needs nothing from the lost volume.
It verifies the newest base backup with the copy's own pg_verifybackup, restores
it into the empty target data directory, replays every complete archived WAL
segment that follows it from the copy's archive, promotes the server and writes
restore-report.json beside the data directory. Recovery runs through the entire
complete archived WAL: no recovery target is set (a target at the first record
of the last segment would discard later committed records in that segment);
PostgreSQL replays every archived segment until the archive ends and promotes,
and the tool then proves that every complete archived segment after the base
was restored from the archive and that replay reached the last archived
segment, so a restore that only replayed the base backup cannot pass as a full
recovery. The report lists the segments restored from the archive, the final
redo and replay positions, the effective restore_command, the schema-comment
digests and every table's row count. For every port, the original one
included, the tool derives the libpq service file and password file inside the
report directory from the copy's own admin credential file (the copied
pg_service.conf names the original volume and is never used); `--stop` removes
them after a rehearsal beside a running installation on another port.
After a real recovery, register the service and re-create the daily base-backup
task as described above, then take a fresh base backup before the next copy.

The opt-in recovery test creates a physical backup, verifies its manifest,
commits another row, archives WAL, restores to a separate directory and port,
and replays to a named restore point. It verifies both rows and stops the
restored instance. Its configured source must be a disposable native installation
outside the repository and all linked worktrees:

    $env:GTKB_NATIVE_POSTGRES_HOME = 'E:\GTKB-realignment-validation\native-install-qualification\infrastructure\postgresql'
    & E:\GT-KB\groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/groundtruth_kb/test_postgres_native_recovery.py --basetemp E:\GTKB-realignment-validation\new-recovery-run -q

Passing this drill demonstrates its isolated recovery scenario. Ordinary CLI
cutover, the authority service, unattended backup/retention, service startup
and a storage-loss recovery copy require their own operational validation.

### Measured recovery and transition figures (2026-09-17, M12)

Three recovery drills ran `restore_from_copy.py` into a disposable cluster on
127.0.0.1:55436; each ended with `archive_recovery_complete`, timeline 2 and
replay confirmed to the end of the last archived segment
(`replay_reached_last_archived_segment`):

| Drill (local time) | Base backup + archive | Wall time (UTC) | Readback |
|---|---|---|---|
| 13:05 rehearsal, before the transition | `base-20260917T091501Z` + segments B4, B5 | 16 s (20:05:16.9 - 20:05:33.2) | redo done 0/B5000130; 101,670 rows; predecessor schema 2f250715... |
| 15:06 post-transition base | `base-20260917T220547Z` (self-contained, segment BA) | 9 s (22:06:01.7 - 22:06:10.3) | redo done 0/BA000120; 101,938 rows; schema 4b5f8275... |
| 15:21 WAL tail from the pre-transition base | `base-20260917T215831Z` + segments B7 - BB | 17 s (22:20:54.4 - 22:21:11.3) | B8, B9, BA, BB restored from the archive; redo done 0/BB000130; 101,938 rows; schema 4b5f8275...; the schema transition and the 268 `repository_ref = platform` writes (record version 2, written 15:03:24 - 15:05:46 local) came back from WAL after the base |

Row arithmetic: 101,938 = 101,670 + 268 (the history rows of the D11 write
set). Records: `E:\GTKB-realignment-validation\m12-4-recovery-drill\`,
`E:\GTKB-realignment-validation\m12-4-recovery-drill-post-transition\` and
`E:\GTKB-realignment-validation\m12-4-wal-tail-drill\drill\` (a
`restore-report.json` in each).

Production transition (M12.3; record
`E:\GTKB-realignment-validation\m123-production\record.json`): the domain
service was down from 14:58:31 to 15:03:23 local (4 min 52 s), covering the
pre-transition base backup with its restore point, the detached checkout of
commit 313c5b597, eight projection regenerations (652/652 generated files
byte-equal to the accepted snapshot) and the schema transition itself (under
1 s: `upgraded`, 25 tables; a repeat reported `already_current`). `/v1/status`
answered ready on schema 4b5f8275... within 3 s of the scheduled task's
restart. The 16:32 restart check measured the listener closed 2.8 s after a
stop request and ready 2.4 s after a start request. The transition reported
`unresolved_project_repositories = 627`; the D11 write set then bound the 268
active execution projects to `repository_ref = platform` through the native
writer with exact readbacks and no refusal, leaving 359.

`unresolved_project_repositories = 359` is the ruled end state for this
cluster (owner ruling D11, 2026-09-17), not a residual to work off: the 359
closed projects (348 retired, 11 cancelled) keep `repository_ref` NULL
permanently, the writer's closed-project rule (`project_structure_frozen`)
stands, and no reconciliation work item follows. The counter is an
upgrade-time diagnostic; it fired once on this cluster and does not recur.

## Native domain service qualification

The package's `authority` dependency extra installs FastAPI and Uvicorn. The
service runs from the installed GT-KB package through `gt service serve`;
its source is `groundtruth_kb/native_authority.py` and `authority_api.py`.
It opens PostgreSQL using the server process's libpq configuration. A client
receives no database credentials, connection string, or raw-table interface.

This interface is currently for migration qualification. It provides typed
specification, test, test-plan/phase, program/project, work-intake, membership,
and current task-context operations. Native session binding and bridge claims,
publication and independent review have behavioral qualification. Isolated
project work, session checkout publication and project finalization are covered
by the additional suites described below. Complete domain coverage, production
migration and authority cutover remain required before ordinary agents are resumed. Attribution on
knowledge correction operations is not a session binding or a review assertion.

For an explicitly initialized disposable database, an operator config selects
the PostgreSQL service under `[postgresql]`. Start its HTTP service with:

    gt --config <operator-config.toml> service serve --port 8765

The listener binds only `127.0.0.1`. It refuses browser-origin requests, emits
no access log by default, and uses the workstation's host/filesystem boundary.
It does not implement or enable a LAN endpoint. The service process alone needs
`PGSERVICEFILE`; do not place credential paths in harness configuration.

A separate client config selects that service:

```toml
[groundtruth]
project_root = "E:/GT-KB"
authority_url = "http://127.0.0.1:8765"
```

Configuring `authority_url` changes ordinary CLI routing. Unavailable services
and unsupported native commands fail without opening SQLite. Do not set this
value in the live GT-KB config as a partial migration.

The importer refuses existing bridge coordination state and divergent immutable
bindings, even when the knowledge rows otherwise match. Its bounded target-table
locks wait for in-flight writers and inspect their committed state before
importing. It never clears another context's binding, attempt or delivery.
An exact import retry compares knowledge, bindings and initial knowledge history.

The current manifest contains 20 versioned knowledge/planning tables and the
six-field `session_init_bindings` table. Knowledge starts PostgreSQL lineage at
version 1. Binding identities, subject, role, creation time and original
idempotency identity are preserved without invented versions or history rows.
Initialization compares the actual stored subject and role; its digest is not
a substitute role predicate or a legacy-format translation requirement.

All 67 tables present in the reviewed SQLite source are accounted for: 21
migrate, 4 contain omitted runtime/derived data, and 42 are
retired storage. The latter includes obsolete dispatcher metrics and lane
projections, mutable session envelopes/role attestations, bootstrap permission
bundles, publication capabilities and mutation receipts. Required current work,
formal, project and test facts migrate from their existing domain rows, not
from those historical bundles. The original source and out-of-band backups
preserve history through the migration cleanup boundary.

Current row payloads are selected inside SQLite; export does not load obsolete
historical bodies merely to choose the newest version. Invalid source versions
and duplicate identity/version pairs still refuse. Work items do not retain a
`related_bridge_threads` column in PostgreSQL: disposable bridge addresses are
not durable knowledge links or recovery inputs. The migration intentionally
excludes that legacy source field; operative bridge state uses the native bridge
service and is purged at terminal completion.

Membership migration retains active parent relationships only, including the
parents of completed work. Known inactive associations (`removed`, `retired`,
`moved`, `superseded`, `completed`, `excluded`, `rehomed`) stay in the source and
backup as history; they are not additional current parents in PostgreSQL. Unknown
membership statuses refuse with the record identity, rather than being silently
omitted. Missing or competing current parents still refuse import.

Known retired/runtime source tables may already be absent. Every migratable
table must be present, and any unknown table refuses export with its name so
new state cannot be silently dropped. The snapshot's actual schema inventory
and contents are still checked against the specific transform input. Accounting
for the table set does not prove every field, citation or work relationship is
valid; those reconciliations and the permanent cutover remain required.
Every open work item must resolve to exactly one active parent-project
relationship; a missing or competing parent refuses the manifest. Closed work
(any resolution status other than open) migrates with its recorded membership
rows exactly as history: zero or several active memberships are accepted for a
closed item and are neither repaired nor fabricated by the migration (owner
decision, 2026-09-10). Intake and every native membership write keep the
exactly-one-parent rule. A read of a closed item (`gt ... show`, `GET
/v1/work-items/<id>`) returns its recorded membership rows and `membership:
null` when no single active parent exists, inventing nothing; task context,
mutations, the membership move and execution readiness still report
`invalid_membership` for an irregular history.

The supported client commands include:

    gt --config <client-config.toml> service status --json
    gt --config <client-config.toml> projects list --kind program --json
    gt --config <client-config.toml> projects show <project-id> --json
    gt --config <client-config.toml> backlog show <work-item-id> --json
    gt --config <client-config.toml> context work-item <work-item-id> --json
    gt --config <client-config.toml> spec record --id <spec-id> --fields-file <fields.json> --expected-version <version> --actor <attribution> --change-reason <reason> --json

`record` takes a JSON object of the domain fields to change. The service retains
omitted fields, validates references and types, compares the expected version,
and returns committed current state. Version 0 asserts that the record is new.
It creates no permission packet or authorization history. Work intake requires
one execution project, a current specification, an executable test, and an
active test-plan phase. A membership move updates both relationships in one
transaction and preserves each project's authorization. Programs never receive
work-item membership or an authorization value.

`context work-item` reads one current database snapshot containing the work item,
its actual project and program, linked formal requirements, executable test,
active test-plan phases and plans, and prerequisite state. Formal requirements
include the project's active specification links, the work item's source and
related specifications, the test's specification, and their transitive `parent`,
`affected_by` and `provisional_until` references. Cyclic references are included
once. Missing or inactive required sources return a diagnostic and recovery
route instead of a partial successful context. This declared relationship set
is a starting point for applicability investigation, not proof that every
semantically relevant requirement has been discovered.

NEW and REVISED proposals must author `work_item_version` with the work-item
version actually read, and `spec_versions` as a JSON object mapping
each applicable formal ID to the positive integer version the author actually
read, for example `{"SPEC-1": 2, "GOV-1": 1}`. An ID-only `spec_ids` field is
not accepted. Include the declared closure and any additional applicable sources,
including the references of those additional sources. The service compares
every authored version with current canonical state; it never supplies or
upgrades the author's source versions at filing time. A delayed proposal must
be reconsidered against the changed requirement and reauthored before acceptance. Bridge
claim, checkout and effect checks re-read it against the proposal's source
versions; changed requirements cannot silently inherit an old review. A fresh
context loads the current task through the same CLI, without a previous agent's
report or direct harness contact. Local `gt status --startup` supplies compact
diagnostics only; a historical startup report does not certify current context.
Both text and JSON task-context output include complete source records and test
instructions; the text view does not reduce gate criteria to record titles.

The behavioral qualification is
`platform_tests/groundtruth_kb/test_native_authority_service.py`. It uses unique
schemas on an explicitly selected disposable PostgreSQL service, including
rollback after a partial transaction, competing writers, dependency write skew,
exact JSON-number transport, and separate CLI processes with no PostgreSQL
environment settings. The client test points SQLite at a deliberately invalid
file and verifies its bytes are unchanged after success and service outage.

## Native session and bridge qualification

The native bridge uses an immutable binding of the actual harness context to
one GT-KB subject and role. The owner or received dispatch supplies the exact
init marker. Environment variables and harness names do not supply the role.
Repeated identical initialization returns the same binding; a conflicting
marker is rejected. A context's end does not require its successor to reuse
that identity or inspect another harness.

    gt session bind --native-context-id <actual-context-id> --init-keyword '::init gtkb pb' --json
    gt bridge claim <document-id> --work-item-id <work-item-id> --native-context-id <actual-context-id> --expected-version <current-version> --status <intended-successor> --request-id <unique-request-id> --json
    gt bridge check <document-id> --native-context-id <actual-context-id> --fence <returned-fence> --json
    gt bridge deliver <document-id> --native-context-id <actual-context-id> --fence <returned-fence> --content-file <authored-message.txt> --json

Use these commands with the explicit disposable client config during
qualification. A claim atomically returns the complete predecessor and reserves
one successor artifact for 600 seconds. It has no renewal. An identical claim
retry preserves the original expiry; a competing request is rejected even from
the same context. Publication validates the complete authored header and
consumes the claim in the same transaction. No writer fills or repairs a header. An
implementation effect covers the union of proposal `target_paths` and
`test_artifact_targets`. Both sets participate in overlap arbitration, and
`gt bridge check` returns that complete mutable artifact set. A shared test is
protected even when the builders modify different implementation files. Release
or expiry frees the next-artifact reservation; it creates no thread ownership.
Call `bridge check` immediately before a protected implementation effect.

`bridge show --content` retrieves the active message chain. `bridge artifacts`
returns actual Git-normalized file identities for independent review, not a
verdict. VERIFIED requires the agent-authored reviewed map to match those bytes.
The response reports whether all current project members are verified; that
boolean does not claim a commit or project terminality. Complete project
finalization uses the separate ordinary project commands below.

`bridge release` ends the named claim by current fence. A worker context ends
without a mutable session lifecycle or deletion of its immutable role binding.
Later contexts use their own bindings and fresh claims. `bridge abandon` closes
an unusable attempt from canonical evidence without inventing a withdrawal or
inheriting its GO. Withdrawn, superseded and abandoned attempts purge their
payloads. `bridge queue --role <pb|lo>` reports eligible work without selecting it.
An ADVISORY claim omits `--work-item-id` and reserves no implementation attempt.

`platform_tests/groundtruth_kb/test_native_bridge.py` exercises fresh-context
continuation, role and header errors, competing requests and effect paths,
expiry/replacement, exact retries, current evidence changes, all phase-specific
statuses, headless BLOCKED, advisory isolation, independent verification of
actual Git bytes and payload purge. The separate CLI-process test in
`test_native_authority_service.py` also completes NEW/GO/READY/VERIFIED using four
fresh contexts with no PostgreSQL client environment settings. These tests use
an explicit disposable PostgreSQL service and isolated Git roots.

## Isolated work and project completion

Uncommitted project work resides in a service-managed checkout under
`.worktrees/projects/`, derived from the project identifier. The integration
checkout retains the committed platform and unrelated existing user work.
Each worker uses its own `.worktrees/<session-context-id>` checkout. The CLI
loads project artifacts into that checkout without reading a predecessor's
checkout or another harness's files:

    gt bridge worktree <document-id> --native-context-id <actual-context-id> --fence <returned-fence> --json

The response supplies the caller's path and the exact `artifact_preimages`
map for its proposal and test paths. Preserve that map in the caller's ephemeral
context/scratch while editing those files in the returned checkout. Publication
accepts only the claimed implementation-report scope:

    gt bridge publish-work <document-id> --native-context-id <actual-context-id> --fence <returned-fence> --preimages-file <preimages.json> --json

Publication compares current project artifacts with the retrieved preimages,
rechecks the current claim before effects, and transfers only that scope.
An exact retry is harmless; it needs no durable permission or publication receipt.
Unpublished local work is preserved. The agent then authors and delivers READY.
A successor reviewer loads the resulting project artifacts into its own checkout
and independently tests them before authoring VERIFIED.

When all members are verified, the reviewing context commits the complete
project through the ordinary CLI:

    gt projects commit <project-id> --native-context-id <actual-context-id> --expected-version <project-version> --message-file <authored-message.txt> --json

The command prepares the verified cohort in that context's own checkout,
refuses unrelated staged paths, stages the exact project scope, and runs normal
Git commit hooks. The authored message must cite every member as `(WI-NNNN)`.
The service checks the candidate's actual parent, complete reviewed file map,
changed paths and citations before fast-forwarding the integration branch.
No additional merge commit is created. Normal Git fast-forward checks preserve
unrelated work and refuse conflicting local edits; see the
[Git merge contract](https://git-scm.com/docs/git-merge).
The short filesystem operation is serialized in PostgreSQL; it does not
reserve a project or work-item thread for an agent's lifetime.

For explicit preparation, an agent-performed normal Git commit, or recovery:

    gt projects prepare-commit <project-id> --native-context-id <actual-context-id> --expected-version <project-version> --json
    gt projects confirm-commit <project-id> --native-context-id <actual-context-id> --expected-version <project-version> --commit-id <actual-sha> --expected-parent <prepared-sha> --json
    gt projects commit-failed <project-id> --native-context-id <actual-context-id> --expected-version <project-version> --reason commit_not_confirmed --evidence <observed-failure> --json

An uncertain confirmation is retried with the same actual commit, including
from a fresh reviewing context if integration already occurred. A changed
reviewed artifact or failed commit records a request for fresh verification;
Dispatcher authors no verdict. Terminal project state records the actual Git
commit, work items receive its identity, and disposable bridge payloads are
purged. The commit's timestamp supplies project completion time.

`platform_tests/groundtruth_kb/test_native_project_finalization.py` exercises
multi-member completion, private candidate commits, preservation of unrelated
staged/unstaged work, hook refusal and hook-altered bytes, partial or foreign
commits, overlapping integration edits, fresh verification and confirmation
after an uncertain acknowledgement. The ordinary CLI-process suite includes
publication, successor review and project commit. These are disposable native
qualification scenarios, not proof of the still-pending production cutover.


### Project prerequisites through the ordinary CLI

Project dependencies describe exact prerequisite outcomes. They never set or
recheck project authorization. With the native authority configured:

    gt projects dependencies list --dependent-project <project-id> --json
    gt projects dependencies show <dependency-id> --json
    gt projects readiness <project-id> --gate readiness --json
    gt projects readiness <project-id> --gate closure --json

Readiness reports each dependency's required state, current state and reason.
Task context includes the same readiness report. This evaluates project
prerequisites; it is not a claim that all work-item readiness conditions pass.
The bridge queue separates blocked advancement from eligible work and retains
the prerequisite explanation. Corrective rejection, withdrawal and supersession
remain available through their lawful transitions.

Create or amend a dependency with an authored JSON fields file:

```json
{
  "dependent_project_id": "PROJECT-SUCCESSOR",
  "prerequisite_project_id": "PROJECT-PREDECESSOR",
  "required_prerequisite_state": "verified",
  "affected_gate": "readiness",
  "rationale": "The successor needs the predecessor's complete committed result."
}
```

    gt projects dependencies record --id <dependency-id> --fields-file <fields.json> --expected-version 0 --actor <actor> --change-reason <reason> --json

Use the current returned version for amendments. `{"status":"retired"}` removes
an edge from current gating; `{"status":"active"}` recovers it only if its
endpoints and the resulting graph are valid. Both preserve prior versions and
project authorization. Cycles, duplicate edges, invalid endpoints and stale
versions refuse without partial mutation. Current-state migration validates the
same graph contract; it never aliases `completed` to `verified`.

Supported required states are exactly `active`, `verified`, `retired` and
`cancelled`. A required `verified` outcome is satisfied only by verified project
state with its canonical activation Git link. Retirement is a separate outcome.
The `readiness` gate applies to forward bridge claims/delivery, implementation
fence checks and publication. `closure` additionally gates complete-project
preparation and confirmation. Publication and integration hold the relevant
project rows while checking prerequisites and performing the short effect, so a
concurrent dependency edit cannot pass between that check and the effect.

`platform_tests/groundtruth_kb/test_native_project_dependencies.py` exercises
blocked new claims, changes after retrieval, independent corrective rejection,
concurrent cycle creation, publication/edit arbitration, and a real predecessor
commit unblocking its successor. The ordinary CLI-process qualification covers
dependency creation/readback, useful readiness output and retirement without
client database credentials. Migration tests reject invalid native dependency
contracts before import. The remaining legacy dependency consumers still need
reconciliation with this native contract.

Work-item `depends_on_work_items` is a list of distinct current work-item
identifiers. An absent list means no predecessors. Predicate objects, non-work
references, missing endpoints, duplicate entries and cycles must be reconciled
in the source; import does not translate or discard them. Closed source labels
do not exempt a current record from this contract. Migration and ordinary
work-item amendments use the same graph validator. Refusals identify the affected
item and missing endpoints or the actual cycle, without a partial mutation.

The kernel and native authority suites exercise accepted same- and cross-project
references, malformed source arrays, missing endpoints, closed/open cycles, deep
shared predecessors, atomic amendments, and concurrent opposing dependency
writes. Graph validity does not assert that predecessor work has been performed.

### Work-item predecessor results

    gt backlog readiness <work-item-id> --json
    gt context work-item <work-item-id> --json

The former `gt session envelope packet` command and descriptor packet producer
are removed. Startup forwards the service response without a role/activity
packet receipt; failure directs the receiving context to the canonical task
reader. The activity renderer points to that same route for the explicitly
assigned work item and does not choose a task or claim that a pointer is loaded
knowledge. Bootstrap directions live in the canonical baseline and must be
mechanically projected. This retirement does not qualify the remaining legacy
manifest/freshness machinery, all startup consumers or installed projections.

The work-item readiness report identifies the required result, current status and
specific reason for each unavailable predecessor. Task context reads the same
report together with project readiness. A closed predecessor whose recorded
membership history is irregular (no single current project) is reported as
`predecessor_membership_irregular`; it never satisfies a dependency until its
history is reconciled or the dependency is re-authored, and the dependent's
read is not refused. These prerequisite checks do not replace
the separate role, proposal, claim, review or NEW-authorization checks.

Within one project, an independently VERIFIED predecessor can support dependent
work before the shared project commit. Its current attempt, work/formal scope
and exact reviewed artifacts must exist; known fresh-verification state blocks
advancement. Before GO, the predecessor bytes must still match that review. After
GO, paths covered by the dependent item's current accepted proposal may change
as that work proceeds. The report names these `accepted_change_paths`; predecessor
artifacts outside that scope must still match their review. Final project
preparation/confirmation checks every member's complete final artifact map and
requests fresh verification of stale members before committing once.

Across projects, the predecessor must have verified project state, the sole
canonical activation commit and matching work-item terminal commit evidence.
A status label, retirement, missing review or uncommitted project is insufficient.
An item dependency neither creates a project-dependency edge nor blocks unrelated
sibling work.

Forward claims/delivery, implementation fence checks and publication use current
predecessor facts. Short effects lock those facts through the publication boundary.
Corrective negative verdicts remain available without fabricating a new lifecycle
status. Queue diagnostics identify blocked work and its missing predecessor result.
The unresolved recovery contract for materially changed formal intent still needs
closure; detection alone does not supply a lawful new implementation transition.

Context loading incorporates committed integration results into the service's
project checkout with an ordinary fast-forward before creating the receiving
context's checkout. Unrelated unfinished project work is preserved; conflicting
work returns `project_base_reconciliation_required`. Existing context work is not
reset to a new base: the receiving context must be fresh when its previous base
differs. Read-only readiness neither creates nor refreshes a project checkout.

`platform_tests/groundtruth_kb/test_native_work_item_dependencies.py` exercises
same-project dependencies, shared-artifact final review/commit, cross-project
commit/loading, changed prerequisites, effect arbitration, missing checkouts and
preservation of conflicting local work. The native CLI-process suite exercises
ordinary readiness/context reads without client database credentials.


Successive work items in one project may change the same artifact. Finalization
compares every member's own reviewed map with the final project bytes before
using the combined artifact set for a commit. Only stale members return for
fresh independent verification; a later member whose review already matches
those bytes stays verified. Differing snapshots are neither silently collapsed
nor a permanent refusal with no recovery. Both commit preparation and
confirmation enforce this comparison, and the project still commits once after
all members have verified their committed form.

## Unattended domain-service startup

Ordinary knowledge and bridge commands route through the native domain service on `authority_url`; a PostgreSQL
service alone leaves the CLI refusing. Three files start the service unattended:

- `domain_service_launcher.py` runs the installed package's `service serve` on `127.0.0.1` with the credential
  environment confined to that process: `PGSERVICEFILE` = `credentials/pg_service.conf`, after every inherited `PG*`
  value, every inherited `GT_POSTGRES_*` override (the configuration loader maps those onto the `[postgresql]` section
  and would redirect the service selection) and any inherited `GT_AUTHORITY_URL` are dropped. On Windows the service
  runs inside a named kill-on-close job object for the installation root
  (`Local\gtkb-domain-service-<first 24 hex digits of the sha256 of the normalized root>`; the mechanics are
  `groundtruth_kb.job_containment`, shared with `gt dashboard` under owner ruling D27); the launcher's handle is the
  job's only handle, so the job ends every process in it when the launcher ends and stopping the launcher never
  leaves a listener behind. Containment precedes execution: without a job nothing is started, and a second launcher
  for a root whose job is already held exits 3 (`held by another launcher for this root`) before anything starts;
  the service is created
  suspended, placed in the job and only then resumed, so no descendant can exist outside the job; an assignment
  refused with ERROR_ACCESS_DENIED right after the job terminated its members is retried for up to two seconds
  while the service stays suspended; a service that
  cannot be placed in the job or resumed is ended while still suspended and the launcher exits 3. Output is appended to `logs/domain-service.log`. It refuses to start when
  the credential file or the operator config is missing. `--print-command` shows the command and the names of the
  environment keys it sets, never their values.
- `domain-service-readiness.ps1` defines `Wait-GtkbDomainServiceReady`, the bounded readiness probe: it runs the
  ordinary `service status --json` bound to `127.0.0.1:<port>` through `GT_AUTHORITY_URL`, treats a failed probe as
  an expected condition while the service starts (native stderr and non-zero exit codes are captured and never
  terminate the loop, in Windows PowerShell 5.1 as in PowerShell 7), and reports readiness, the number of probes and
  the last output.
- `register-domain-service.ps1 -Root E:\GT-KB [-Port 8765] [-ReadinessSeconds 60]` registers the scheduled task
  `GTKB-DomainService` under the current account: at every logon of that account, on demand, and by a repetition
  trigger configured to attempt a start every five minutes (`IgnoreNew` leaves a running instance alone). The
  restart-on-failure settings remain configured. On this workstation on 2026-09-12, each exit-1 probe logged one launch
  and no relaunch during its observation window: 230 seconds after the on-demand start; 310 seconds from registration
  for the one-time-trigger case (about 240 seconds after launch). Repetition recovery was demonstrated separately:
  kill test 2 restored the listener after 37 seconds. These observations do not establish Task Scheduler's general
  restart-on-failure semantics. There is no execution time limit; battery state neither prevents a start nor stops the
  service. It refuses to change a task that points at another installation, starts the
  task, then waits for readiness with the probe above and fails, naming the number of probes and the task state, when
  the service does not answer within the window. Registration is an owner action of the same kind as
  `register-service.ps1` for PostgreSQL.
- GT-KB Home, GT-KB's primary interface, starts at logon through its own task `GTKB-Home`, the same trigger as
  `GTKB-DomainService`. It is installed and
  registered in the same owner step with `infrastructure\deepseek-web\install.py` and
  `infrastructure\deepseek-web\register-home-task.ps1`; see `infrastructure\deepseek-web\README.md`.

Copy `operator-config.example.toml` to `operator-config.toml` and set `[postgresql] service` to the credential entry the
service process uses (`gtkb_authority`). Verify after registration (PowerShell):

    $env:GT_AUTHORITY_URL = 'http://127.0.0.1:8765'
    gt --config E:\GT-KB\infrastructure\postgresql\operator-config.toml service status --json
    schtasks /Query /TN GTKB-DomainService /V /FO LIST

The tests cover the launcher's composition and refusal paths, the regression that inherited `GT_POSTGRES_*` overrides
cannot redirect the operator config's service, the readiness probe's timeout without aborting under Windows PowerShell
5.1 and PowerShell 7, and (opt-in, `GTKB_RUN_POSTGRES_INTEGRATION=1`) a launch to readiness against the disposable
installation with a deliberately polluted parent environment, the probe waiting through the service's delayed
readiness, the complete process tree ending with the launcher so that the listener disappears, refusal before anything
is started when no job exists, refusal of a second launcher while the root's named job is held, an uncontainable
service ended before it runs (no child, no descendant), a real
descendant born inside the job and ended when the job closes, and the cleanup safety net leaving a foreign
listener alone. Scheduled startup
itself is established at registration on the owner's workstation: task state Running after a logon, the status
readback above, and the current state read back through the ordinary CLI. Resumption of ordinary sessions waits for
that evidence, and the client `authority_url` is set only after it.

## Dashboard control plane

`gt dashboard start` and `gt dashboard stop` follow the domain-service pattern above (owner ruling D20, 2026-09-17):

- On Windows, `start` creates one named kill-on-close job object for the runtime root
  (`Local\gtkb-dashboard-<first 24 hex digits of the sha256 of the runtime root>`), creates the refresh service (a
  venv redirector and its child) and Grafana (`grafana.exe` and its plugin children) suspended, places each in the
  job and only then resumes it, so no descendant ever exists outside the job. The children inherit the job handle,
  which keeps the job alive exactly as long as one of them lives; when the last member ends, the job and any
  straggler end with it. `start` writes `<runtime root>/dashboard-launch.json` naming the job, the launched
  processes, the ports, the interval and the selected configuration; nothing in that record decides what `stop`
  signals. The former `pids/*.pid` records no longer exist and a leftover one means nothing to the package. The job
  primitives (`groundtruth_kb.job_containment`) are the ones the domain-service launcher uses; the two prefixes keep
  a dashboard job and a service job for one root distinct, and an extra handle opened to a job delays kill-on-close
  until it is closed.
- `stop` opens the job by name, holds a handle to every member, terminates the job and waits until every handle is
  signalled and the job counts no active process. It reports each member with its executable and outcome:
  `terminated`, or `exited` for a member that ended on its own before the request. Nothing outside the job is
  touched. Refusals are distinguishable by class: `DashboardTerminationRefused` (the job, or `taskkill` for a
  single process, refused the request while the process still runs), `DashboardTerminationUnconfirmed` (the
  request was accepted but a held handle stayed unsignalled: 15 s for a job member, 5 s for `taskkill`) and
  `DashboardIdentityError` (a recorded process is not the launched one; nothing was signalled). The launch record
  is kept for inspection after a refusal.
- A derived dashboard database whose schema is not this package's is moved aside as
  `<runtime root>/gtkb-dashboard.sqlite.legacy-<UTC stamp>` and rebuilt from `templates/dashboard/schema.sql`;
  the refresh result (`legacy_database_moved_to`) and the refresh-service log name the reason and the new path.
  Disqualifying shapes: a table the schema does not define, a table missing an expected column (the July-9
  `kpi_snapshots(id, metric, value, unit, captured_at, source)` file that refused the 2026-09-17 production start),
  a NOT NULL column without a default that the refresh never writes, or a file SQLite cannot read. Additive
  migration columns (nullable or defaulted) are accepted. A legacy or foreign derived schema is no history.
- Grafana's launch environment pins every server-initiated network path off: analytics reporting, version and
  plugin-update checks, the preinstall/background plugin installer and its auto-update
  (`GF_PLUGINS_PREINSTALL_DISABLED=true`, `GF_PLUGINS_PREINSTALL_AUTO_UPDATE=false`), plugin administration from
  the UI (`GF_PLUGINS_PLUGIN_ADMIN_ENABLED=false`) and signing-key retrieval (the embedded key verifies the pinned
  SQLite plugin). `GF_LOG_MODE=console` makes the launcher's redirect the single writer of `logs/grafana.log`.
  On 2026-09-17 the production start let Grafana's background installer fetch plugin updates from grafana.com into
  the qualification Grafana home; that path is closed by these pins.
- `gt dashboard install` remains the route that places Grafana under `<project>/.groundtruth/tools/grafana`
  (pinned 13.2.1 archive and checksum, pinned SQLite datasource plugin, signature verified by the pinned runtime).
- Launch the dashboard from an ordinary shell or scheduled task: a launcher that itself runs inside a kill-on-close
  job passes that containment on, and the dashboard ends with that job.
