# {{PROJECT_NAME}} — Quickstart

This application uses its selected GT-KB host's native authority. Its application
slot must be registered, its Git repository independent, and its execution
project bound to `application:<APP_NAME>` through `repository_ref`.

## Configuration

The application configuration selects a reachable service:

```toml
[groundtruth]
authority_url = "http://127.0.0.1:8765"
```

Use the endpoint configured for the selected host. Canonical records are read
and written through that service; no application-local database supplies fallback
authority. Agent roles belong to the explicitly initialized session context,
never the harness installation or a local marker.

## Initialize and check

For an uninitialized registered application, preview the files before applying
the same options. Replace the placeholders with the selected application,
project, host and owner:

```text
gt --config "<host>/groundtruth.toml" project init <APP_NAME> --project-id <PROJECT> --host-root "<host>" --owner "<OWNER>" --profile local-only --dry-run --json
gt --config "<host>/groundtruth.toml" project init <APP_NAME> --project-id <PROJECT> --host-root "<host>" --owner "<OWNER>" --profile local-only --json
gt --config "<application>/groundtruth.toml" project doctor --project-id <PROJECT> --host-root "<host>" --json
```

An already initialized application starts with the doctor command. The project
initializer creates no commit. Inspect its returned paths and diagnostics.

## Current requirements and workflow

```text
gt --config "<application>/groundtruth.toml" core-specs next-question --project-id <PROJECT> --json
gt --config "<application>/groundtruth.toml" backlog list --json
gt --config "<application>/groundtruth.toml" bridge state-report --json
```

Record actual owner answers through the core-specification writer using the slot
and expected version returned by the current read. There is no separate decision
archive. Native bridge delivery is temporary coordination; current domain
records and Git carry durable work. Disposable bridge payloads are removed at
terminal closure rather than kept as a permanent audit trail.

## Updates

Application-owned content, including this README and application source, stays
with the application. Projectors derive harness configuration from the authored
sources; generated output is not manually edited. Preview an upgrade, inspect
its selected changes, and apply explicitly:

```text
gt --config "<application>/groundtruth.toml" project upgrade <APP_NAME> --project-id <PROJECT> --host-root "<host>" --json
gt --config "<application>/groundtruth.toml" project upgrade <APP_NAME> --project-id <PROJECT> --host-root "<host>" --apply --json
```

© {{COPYRIGHT_NOTICE}}
