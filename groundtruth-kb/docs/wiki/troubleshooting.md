# Troubleshooting

Find your symptom, make the first safe check, and collect a small amount of
evidence before changing the installation. Do not reinstall, widen permissions,
or restart every component just to clear an unexplained indicator.

**Status:** Symptom guide with unresolved recovery gaps noted

**Reviewed:** 2026-09-28

## Find your symptom

| Symptom | Start here |
| --- | --- |
| Command not found or an option is rejected | [`gt` is not found](#gt-is-not-found), [Command mismatch](#a-documented-command-is-missing-or-refuses-valid-work) |
| Home will not open | [Check the selected Home installation](#gtkb-home-does-not-open) |
| Folder selected, but composer still unavailable | [Check workspace acceptance](#a-folder-is-highlighted-but-home-still-needs-a-workspace) |
| Overall UNKNOWN, stale dashboard, or conflicting labels | [Read the status reason](#home-reports-overall-unknown), [Dashboard](#dashboard-says-pass-but-is-not-reachable-or-looks-old), [Task Ready](#home-is-running-but-its-task-says-ready) |
| Model request fails | [Check the actual provider error](#a-provider-has-a-green-dot-but-the-model-request-fails) |
| An operation or tool is refused | [Permissions](#a-permission-label-does-not-explain-a-refusal), [Plugins](#a-plugin-section-is-visible-but-a-tool-is-unavailable-or-refused) |
| A background component fails | [Authority](#the-authority-service-is-unavailable), [PostgreSQL](#postgresql-does-not-start), [Ollama](#ollama-says-stopped-and-task-missing-with-no-start-button) |
| Setup, upgrade, or a setting change fails | [Partial installation](#installation-or-upgrade-stopped-partway-through), [Controls](#a-gtkb-controls-edit-does-not-persist-or-has-an-unclear-effect) |

## Confirm which installation you are checking

Use your installation's configuration path in place of this example:

```powershell
gt --version
gt --config E:\GTKB\groundtruth.toml config --json
gt --config E:\GTKB\groundtruth.toml services status --json
```

**Checkpoint:** The resolved configuration and reported components match the
installation you intended to inspect. If a command or option is unavailable,
stop following that command sequence and use [Command mismatch](#a-documented-command-is-missing-or-refuses-valid-work).
CLI surfaces differ between versions. A page review date is not a compatibility
guarantee.

Inspect this output locally. Do not attach configuration files or unredacted
output to a public issue. See [Information to collect safely](#information-to-collect-safely).

## `gt` is not found

1. Confirm that the selected Python environment contains `groundtruth-kb`.
2. Check that its Scripts directory is on the invoking user's `PATH`.
3. Run `gt --version` again from that environment.

**Checkpoint:** The command resolves to the intended GTKB installation. Installing
the package alone does not provision the whole host. See
[Install on Windows](Install-on-Windows); do not install a similarly named
package as a workaround.

## GTKB Home does not open

```powershell
gt --config E:\GTKB\groundtruth.toml home status
gt --config E:\GTKB\groundtruth.toml services status --json
```

1. Confirm that Home and its pinned Node.js setup belong to the selected
   installation. Inspect that Home log and task registration.
2. If there is a port error, [identify the owning process](#a-port-is-already-in-use).
3. Once the reported problem is resolved through the supported operator route,
   use `gt --config E:\GTKB\groundtruth.toml home open` for a current launch URL.

**Checkpoint:** Home opens for the selected installation. Do not reuse an old
launch URL or publish a credential-bearing one. Browser access alone does not
prove authority-service health. See [Verify installation](Verify-Installation).

## A folder is highlighted but Home still needs a workspace

1. In the [Windows picker](Get-Started#the-windows-directory-picker), check the
   breadcrumb and **Folder** field. Highlighting a folder does not submit it.
2. Use **Select Folder** only for the intended directory, or **Cancel** if it is
   not the directory you want.
3. Check the returned Home view and intended full path before entering a prompt.

**Checkpoint:** Home shows the intended workspace. The
[captured example](Get-Started#home-with-a-selected-workspace) shows only a short
name, not the resolved path. Selection and cancellation still need controlled,
release-specific testing.

If the composer remains unavailable or an error appears, report the installed
version, action, expected result, and redacted error. Do not select a broader
directory, create an unrelated project, or change permissions to bypass the
problem. Directory selection and application registration are separate.

## Home reports Overall UNKNOWN

Open **Settings → GTKB** and read each row's explanation. In the
[captured status example](Status), the session row lacks a native context ID
while the authority row reports ready. Missing session context is not, by
itself, a host outage.

If session diagnostics are needed, use the supported session workflow. Do not
fabricate an identifier or guess a role to clear UNKNOWN. If a component is
unreachable, diagnose that component. The overall aggregation rule still needs
a tested reference, so the headline alone is not a reliable diagnosis.

## Dashboard says PASS but is not reachable or looks old

Check for **not contacted** beside PASS. That combination does not prove
reachability. Verify the intended destination, and compare the status time with
the dashboard's own **Last refreshed** time. Refreshing the status pane does not
establish that the dashboard was regenerated.

The [Services example](Services) shows a Dashboard health URL on port **8766**;
the separate [Status example](Status) shows an uncontacted URL on port **3000**.
Do not assume they are the same probe. The endpoint mapping remains a
documentation gap. Report the route, displayed times, and redacted error.

## Home is running but its task says Ready

Application state and scheduled-task state are separate fields. **task Ready**
is not a Home-readiness result. Use the Home checks above and the
[service-state explanation](Services#application-state-and-task-state-are-different-fields).
Do not create a duplicate task or restart a working instance just to make labels
match.

## A provider has a green dot but the model request fails

1. Confirm the intended provider and session model using the supported
   interface. A provider entry is not the same as the selected model.
2. Read the actual error. Credential, endpoint, model-availability, and
   usage-limit problems need different fixes.
3. Follow the selected release's recovery route or contact [Support](Support).

The green dot's meaning is not established by the screenshot. Do not repeatedly
submit requests or replace configuration just to clear the indicator. Share
only the version, provider display name, model identifier if available, and
redacted error. Never share API keys, authorization headers, private prompts,
or credential-bearing URLs. The complete [provider walkthrough](Models) remains
an open gap.

## A permission label does not explain a refusal

Check the current composer permission, not only the General default for new
sessions. Agent mode, model, and project authorization are separate concerns.
See [Settings](Settings#session-permission-menu-on-home).

Record the intended operation, workspace, displayed permission, whether the
session is new or already running, and the exact redacted refusal. Compare them
with the release-specific permission contract. A correct refusal is not a
defect. Do not switch to Full access, widen the workspace, bypass a prompt, or
retry a destructive operation to investigate a label.

If the contract or safe recovery route is unclear, stop and use
[Support](Support). Permission enforcement and change timing still need
controlled qualification.

## A plugin section is visible but a tool is unavailable or refused

A collapsed configuration card does not prove that a plugin is enabled or a tool
is available in this session. Use the selected release's supported inspection
route and compare the exact tool/error with its documented limits and session
permissions. See [Plugins](Plugins).

A correct refusal is not a reason to relax limits, switch models, or install an
unrelated plugin. Report the version, tool, expected result, and redacted error
if the supported behavior is unclear. Avoid repeated commands, searches, or
subagent calls to investigate an unexplained indicator.

## The authority service is unavailable

These are operator checks:

1. Confirm that configuration selects the intended loopback URL.
2. Inspect the registered native service/task and its current log.
3. Confirm that the expected port belongs to that installation.

After a supported repair, repeat the health check and read current state again.
Do not fall back to SQLite or copied state. See [Services](Services) and
[Verify installation](Verify-Installation).

## PostgreSQL does not start

Have the operator inspect the selected `gtkb-postgresql` Windows service and
its startup/PostgreSQL logs. **Do not reinitialize or delete an existing cluster**
as a repair shortcut. Protect existing data and backups, and keep credentials
out of support evidence.

## Ollama says stopped and task missing, with no Start button

First confirm whether the intended model/provider workflow needs Ollama. The
captured panel does not establish that every installation requires it, or that
it is absent everywhere on the machine. If needed, use the selected release's
setup/registration route. If that route is missing, report the gap; do not
invent a button or assume automatic installation.

## A port is already in use

Identify the owning process **and installation** before taking action. Never
kill a process solely by executable name. If another intended installation owns
the port, use an explicit supported configuration rather than silently reusing
it.

## A scheduled task is missing or disabled

Inspect the existing task and verify that its action points to the selected
installation. Use that release's registration procedure if a repair is needed.
Re-registration changes host state and is an operator action, not a diagnostic
check to run speculatively.

## A GTKB controls edit does not persist or has an unclear effect

Stop changing values. The [Controls reference](Controls) records the visible
fields, but the save trigger, precedence, and runtime reload behavior still need
release-specific verification. A changed field or refreshed display is not proof
that a component used the value.

Record the control name, version, expected result, displayed result, and
redacted error. Use the supported recovery procedure or [Support](Support).
Do not increase timeouts, edit generated files, or restart services to guess
how saving works. Do not attach the whole configuration file.

## A documented command is missing or refuses valid work

Check `gt --version`, the page's review date, and your installed release's help
for that command. Capture the exact command, exit code, and redacted output.
Report the mismatch through [Support](Support). Do not assume current Wiki
examples exist in an older checkout, manually edit generated harness
configuration, or invent a replacement state store.

## Installation or upgrade stopped partway through

Preserve the failure output and ask the operator to inspect partial state before
retrying. Do not recursively delete databases, credentials, or backups. A
unified repair workflow remains a product gap. Use [Support](Support).

## Information to collect safely

Include only what helps reproduce or locate the problem:

- GTKB version and which documented procedure you followed.
- Exact failing action or command, with secrets removed, and its exit code.
- Expected result and actual result.
- Relevant service/task status, timestamps, and a short redacted log excerpt.
- Whether a **previously authorized** controlled restart changed the result,
  if one already occurred. A restart is not required to file a report.

Do not attach `.env` files, credentials, configuration files, database copies,
browser launch URLs, private application content, or unredacted logs. Review
screenshots and session exports before sharing. For a report template and the
appropriate channel, use [Support](Support).
