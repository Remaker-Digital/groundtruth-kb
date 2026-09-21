# Application/Platform Isolation

GT-KB keeps host infrastructure and application files in separate roots. A
registered application lives at `<host>/applications/<name>/`; its execution
project identifies that repository as `application:<name>`. Canonical project,
specification, test and work-item records are served by the host's native
authority. Application files and derived caches do not replace those records.

## Register and initialize an application

Follow the [bootstrap guide](../bootstrap.md) to register the application and
create its execution project. Registration, project creation and file
initialization are separate operations.

```powershell
gt --config <host>/groundtruth.toml application register <APPLICATION> --host-root <host> --json
gt --config <host>/groundtruth.toml project init <APPLICATION> --project-id <PROJECT> --host-root <host> --owner "<OWNER>" --dry-run --json
gt --config <host>/groundtruth.toml project init <APPLICATION> --project-id <PROJECT> --host-root <host> --owner "<OWNER>" --json
```

The selected project must already carry the application's repository reference.
The preview reports the intended files and any requested starter specifications.
Initialization refuses an existing application and does not create a local
authority database or a Git commit. If the post-creation intake read fails,
created files remain reported and intake is marked unavailable; retry the
question through `gt core-specs next-question`.

The host supplies the shared hook and rule sources, shared skills and projector.
Host registrations and pointers are generated for the selected harnesses.
Application-owned source, tests and custom hook registrations stay with the
application. A harness name selects configuration, not a Prime Builder or Loyal
Opposition role.

## Inspect the selected application

```powershell
gt --config <host>/groundtruth.toml project doctor --project-id <PROJECT> --host-root <host> --json
```

The doctor reads the native project and reports the resolved application root,
profile, individual checks and overall result. It checks:

- the application registry and repository binding;
- matching application configuration and native authority;
- the installed native commit hook and its Git hook configuration;
- leakage of platform state or a local authority store into the application;
- the optional derived search cache and available terminology guidance; and
- the current core-specification intake question.

A required failure fails the report. Warnings remain visible. A matching commit
hook is a byte/configuration observation; actual commit behavior requires its
own qualification. Doctor performs no canonical writes.

If the authority is unavailable, the command cannot obtain the current project
or complete its native inspection. Local bridge documents and caches cannot
supply replacement authority. The configured `authority_url` must identify the
actual service; a placeholder is not a working installation.

## Upgrade managed files

Upgrade previews by default. Choose the application and project explicitly:

```powershell
gt --config <host>/groundtruth.toml project upgrade <APPLICATION> --project-id <PROJECT> --host-root <host> --json
gt --config <host>/groundtruth.toml project upgrade <APPLICATION> --project-id <PROJECT> --host-root <host> --apply --json
gt --config <host>/groundtruth.toml project upgrade <APPLICATION> --project-id <PROJECT> --host-root <host> --recover --json
```

Managed hook registrations are merged with application-owned entries; retired
projected outputs are removed through the projector. Application-owned files
are preserved. Malformed inputs are refused before effects. Managed paths with
uncommitted work must be resolved first because recovery restores committed
managed files from the application's own `HEAD`. Upgrade creates no commit.

## Derived search cache

The optional ChromaDB cache is rebuilt from current application-scoped authority
records:

```powershell
gt --config <application>/groundtruth.toml project chroma regenerate --dir <application> --scope application:<name> --dry-run --json
```

Remove `--dry-run` to rebuild. If the optional search dependency is unavailable,
the command reports a skip and preserves existing cache bytes. Cache inspection
does not establish canonical freshness or authorize work.

## Verification and further reading

The current tests in `groundtruth-kb/tests/adopter/` cover application defaults,
scaffold ownership, overwrite refusal, isolation findings, packaging and derived
cache behavior. Native application initialization, doctor and upgrade modules
exercise the corresponding service-backed commands. Run the current selected
tests against the source or installed package being evaluated.

- [Bootstrap guide](../bootstrap.md)
- [CLI reference](../reference/cli.md)
- [Product architecture](product-split.md)
- [Canonical terminology](../reference/canonical-terminology.md)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
