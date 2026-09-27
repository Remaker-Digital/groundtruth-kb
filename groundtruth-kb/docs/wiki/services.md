# Services

**Status:** Illustrated service reference; start/stop and recovery checks pending

**Reviewed:** 2026-09-26

GroundTruth KB has independently inspectable components. In [GTKB Home](GTKB-Home),
open **Settings → GTKB services** to find the illustrated service-management
panel. This is separate from the **GTKB** status pane and **GTKB controls** tab.

| Component | Normal Windows behavior |
| --- | --- |
| PostgreSQL | Windows service, local canonical database substrate |
| Native GTKB domain service | Registered background task/service route for the selected installation |
| GTKB Home | Owner-logon scheduled task, loopback web interface |
| Dashboard and optional model services | Installation-dependent; inspect explicitly |

## Read the service-management panel

![GTKB services in Settings: Authority, Home, and PostgreSQL show running; Dashboard and Ollama show stopped. Authority and PostgreSQL have Stop buttons, Dashboard has Start, Home says this page, and Ollama says task missing without an action button.](https://raw.githubusercontent.com/wiki/Remaker-Digital/groundtruth-kb/assets/gtkb-services.png)

Owner-supplied screenshot received 2026-09-26, reproduced unchanged. Its exact
build/version and last-checked time are not visible. The states, registrations,
and addresses below are examples from this capture, not current measurements or
required values for every installation. No displayed endpoint was contacted and
no service control was exercised in this documentation pass.

| Component | State shown | Detail shown | Control shown |
| --- | --- | --- | --- |
| **Authority** | **running** | `http://127.0.0.1:8765; task Running` | **Stop** |
| **Home** | **running** | `127.0.0.1:3080; task Ready` | **this page**, with no Start/Stop button |
| **Dashboard** | **stopped** | `http://127.0.0.1:8766/health` | **Start** |
| **Ollama** | **stopped** | `127.0.0.1:11434; task missing` | No action button visible |
| **PostgreSQL** | **running** | `Windows service gtkb-postgresql: Running` | **Stop** |

The panel includes **Refresh**. Its refresh behavior, probe definitions, failure
messages, and the time represented by each result still need interaction tests.
Read the words and details, not only the green/red indicators.

### Application state and task state are different fields

The Home row combines **running** with **task Ready**. Windows defines a ready
scheduled task as eligible to execute without a queued or running task instance;
running means it has an executing instance. These are scheduler states, not
application-readiness tests. See [Microsoft's task-state reference](https://learn.microsoft.com/en-us/windows/win32/taskschd/registeredtask-state).

The screenshot does not establish how GroundTruth KB derives its application
state or why the two fields differ here. Do not diagnose a failure or create a
duplicate task from that difference alone. Check the selected installation's
service result, registered task, and supported readiness check separately.

### A missing optional integration is not automatically an installation failure

The Ollama row reports **stopped** and **task missing**, with no action button.
That does not establish whether an Ollama executable is installed elsewhere or
whether the selected workflow requires Ollama. Confirm the chosen model/provider
requirements first. Do not install or register a local model service merely to
make this example row green. The supported setup and recovery route for this
state remains a documentation gap.

## Compare services with the status pane

Open **Settings → GTKB** for the illustrated [status pane](Status). This provides
displayed diagnostics, but a row must be read with its explanatory text: the
documented dashboard row says **PASS** and **not contacted**, so it does not
prove that the dashboard is reachable.

The status capture names a dashboard URL on port **3000**, while this service
capture names **Dashboard**, shows **stopped**, and displays a health URL on port
**8766**. These are different endpoints in separate captures. The images do not
prove that they represent the same component, were checked together, or form a
contradictory live result. Documentation must map each label to its component,
endpoint, check, and timestamp before users can reconcile the two views.

The contents of **GTKB controls** have not yet been supplied or tested. Its tab
name is not evidence of additional service behavior.

## Inspect and operate services

Use the installed configuration when inspecting services:

```powershell
gt --config E:\GTKB\groundtruth.toml services status --json
```

Start and stop components only through supported operator controls. A process ID,
task registration, service registration, or old log entry does not prove current
readiness. Never stop a process by executable name alone; identify the exact
owned process or registered component first.

The screenshot establishes that Start/Stop controls exist, not their safety or
recovery behavior. In particular, **Authority** and **PostgreSQL** have **Stop**
buttons. Before using them, establish the effect on active work and dependent
components and the supported restart route. This review has not tested
confirmation dialogs, in-progress feedback, denied operations, or recovery.
Do not stop a required component merely to inspect its button.

Home shows **this page** rather than a lifecycle button. If Home becomes
unavailable, this panel cannot be the only recovery route. Use the separately
documented Home inspection and launch commands in [GTKB Home](GTKB-Home) and
[Troubleshooting](Troubleshooting); do not invent a Start/Stop command.

After a workstation restart, verify the real listeners and readiness responses.
The visible Windows task/service integrations do not prove that a fresh install
registers them correctly or that boot, logon, restart, and intentional stop all
behave as intended. See [Verify installation](Verify-Installation).

The [service controls review checklist](Known-Issues#service-controls-review)
tracks these documentation, usability, and qualification gaps. A separate tray
controller is not needed merely to duplicate the existing panel; prioritize a
discoverable launch route and tested lifecycle behavior first.
