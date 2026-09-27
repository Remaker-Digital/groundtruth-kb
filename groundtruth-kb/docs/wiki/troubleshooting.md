# Troubleshooting

**Status:** First-pass symptom index
**Reviewed:** 2026-09-26

Start by confirming the selected installation:

```powershell
gt --version
gt --config E:\GTKB\groundtruth.toml config --json
gt --config E:\GTKB\groundtruth.toml services status --json
```

## `gt` is not found

- Confirm that the selected Python environment contains `groundtruth-kb`.
- Confirm that its Scripts directory is on the invoking user's `PATH`.
- Do not install an unrelated package with a similar name as a workaround.

## The authority service is unavailable

- Confirm that the configuration selects the intended loopback URL.
- Inspect the registered native service/task and its current log.
- Confirm that the expected port belongs to the selected installation.
- Restore service availability, then re-read canonical state; do not fall back to
  a local SQLite database or copied state.

## GTKB Home does not open

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml services status --json
```

- Verify Node.js and the pinned Home installation.
- Inspect the exact Home log and task registration.
- Check whether port 3080 is already owned by another process.
- Use `gt home open` to obtain a current launch URL; do not reuse an old URL.

## Home reports Overall UNKNOWN

Open **Settings → GTKB** and read the explanation for each row, not only the
headline. In the documented [status example](Status), the session row says no
native context id was supplied, while the authority row reports ready. That
missing context is not, by itself, evidence of a broken host.

If session diagnostics are required, check the real context through the
supported session workflow. Do not fabricate an identifier or guess a role to
remove UNKNOWN. If a component itself is unreachable, diagnose that component
through the service checks above. The full overall-status aggregation rule still
needs a tested reference.

## Dashboard says PASS but is not reachable or looks old

Check whether the dashboard row also says **not contacted**. If so, that result
does not prove reachability. Verify the destination for the selected installation
and inspect the intended dashboard through its supported route.

Compare the overall-status time with the dashboard's own **Last refreshed**
time. Do not assume that refreshing the status pane regenerates the dashboard,
or that opening a dashboard makes its data current. Report the exact failing
route, displayed times, and redacted error through [Support](Support).

The [Services example](Services) shows **Dashboard stopped** at a health URL on
port **8766**, while the separate [status example](Status) uses port **3000** for
an uncontacted dashboard URL. Check the component and endpoint each view means;
do not assume these separate captures are conflicting results from the same
probe. This naming and endpoint mapping still needs a tested reference.

## Home is running but its task says Ready

In **Settings → GTKB services**, the application state and task state are
separate fields. **task Ready** is not itself a Home-readiness result. Use the
Home inspection commands above, inspect the selected task and installation, and
read [Services](Services#application-state-and-task-state-are-different-fields)
before treating the different labels as a fault. Do not create a duplicate task
or restart a functioning Home instance merely to align the labels.

## Ollama says stopped and task missing, with no Start button

First confirm whether the selected model/provider workflow needs Ollama. The
captured panel does not establish that it is required for every installation,
or that no Ollama installation exists elsewhere on the machine. If it is needed,
inspect the selected release's supported setup and registration route; do not
substitute an invented button or automatic installation. If the route cannot be
found, report that documentation or platform gap through [Support](Support).

## A provider has a green dot but the model request fails

Open the [Models guide](Models) to distinguish the provider entry from the
selected model and actual request results. The screenshot does not establish
the green dot's meaning. Confirm the intended provider/model using the supported
session interface, and use the actual redacted error to distinguish credential,
endpoint, model-availability, and usage-limit problems.

Do not repeatedly submit requests, expose a key, or replace a working provider
configuration just to make the indicator agree with expectations. Collect the
version, provider display name, model identifier if available, exact redacted
error, and expected result for [Support](Support). Do not attach API keys,
authorization headers, credential-bearing URLs, configuration files, or private
prompts. The exact provider setup and error-recovery walkthrough remains open.

## A plugin section is visible but a tool is unavailable or refused

The [Plugins overview](Plugins) distinguishes configuration sections from a
tested inventory and session tool availability. Record the exact tool, installed
version, expected result, and redacted error. Use the selected release's
supported inspection route to establish whether the relevant plugin is present,
enabled, and available in the intended session; do not infer those states from
a collapsed card.

Compare the refusal with the documented limits and session permissions. A
correct refusal is not a failure to work around by relaxing limits, switching
models, or installing an unrelated plugin. If the supported behavior or recovery
route is unclear, contact [Support](Support). Do not attach keys, private prompts,
configuration files, or unredacted command output, and do not repeatedly execute
commands, searches, or subagents to diagnose an unexplained indicator.

## PostgreSQL does not start

- Inspect the exact `gtkb-postgresql` Windows service configuration.
- Read the startup and PostgreSQL logs from the selected installation.
- Do not reinitialize or delete an existing cluster as a repair shortcut.
- Do not expose credentials in an issue or support bundle.

## A port is already in use

Identify the owning process and installation before taking action. Never kill a
process solely by executable name. If the port belongs to another intended
installation, choose an explicit supported configuration rather than silently
reusing it.

## A scheduled task is missing or disabled

Use the selected release's registration script and verify the task action points
to the selected installation. Re-registration is an operator mutation; inspect
the existing task before replacing it.

## A GTKB controls edit does not persist or has an unclear effect

Do not repeatedly change values, increase timeouts, edit a generated file, or
restart services to guess how saving works. The [GTKB controls reference](Controls)
documents the captured fields, but the exact save trigger, value precedence,
and runtime reload behavior still need release-specific verification.

Record the control name, installed version, expected result, displayed result,
and redacted error. A changed field or refreshed display is not by itself proof
that a running component used the value. Use the supported recovery procedure;
if it is unclear, stop making changes and contact [Support](Support). Do not
attach the whole configuration file.

## A documented command is missing or refuses valid work

Confirm the installed GTKB version and compare the page's review date. Capture
the exact command, exit code, and redacted output. Report the documentation or
platform defect through [Support](Support). Do not create a competing authority
surface or manually edit generated harness configuration.

## Installation or upgrade stopped partway through

Preserve the failure output and inspect the partial state. Do not recursively
delete database, credential, or backup directories. The unified repair workflow
is a known product gap; escalate using [Support](Support).

## Information to collect safely

- GTKB version.
- Redacted resolved configuration.
- Exact failing command and exit code.
- Service/task status.
- Relevant log excerpt with secrets removed.
- Expected result and actual result.
- Whether the failure reproduces after a controlled restart.

Do not attach `.env` files, credentials, database copies, browser launch URLs,
private application content, or unredacted logs.
