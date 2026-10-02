# GT-KB Home

GT-KB Home is GT-KB's primary interface (owner rulings D58 and D59). It is the DeepSeek Harness Web UI, pinned and
installed with GT-KB, started at logon by the same kind of task as GT-KB's authority and kept running, branded GT-KB by
Remaker Digital, and extended with GT-KB's own pages. It listens on `127.0.0.1:3080` only.

GT-KB has no single whole-product start or stop. The Home's triggers are:

- logon of the owner account (task `GTKB-Home`);
- a restart within five minutes if it stops without a requested stop;
- `gt services start home` or `gt home start` on demand;
- `gt services stop home`, which pauses the task first, so the stop holds.

`gt services status` reports it with every other service.

## What is here

| File | Role |
| --- | --- |
| `package.json`, `package-lock.json` | The pinned npm tree: `@deepseek-ai/dsh` 0.1.2-rc.1 and its 584 dependencies, each with its integrity hash. |
| `release.json` | The pin: package, version, the lockfile's SHA-256, the Node.js floor (20; qualified on 24.11.1), and the profile manifest (the web bundles with `patchReload: "startup"`, the 0.1.2-rc.1 workaround for live patch reload). |
| `install.py` | Installs the pinned tree with `npm ci` from the lockfile. |
| `home.py` | Starts, stops, inspects and opens the Home server (`gt home …` and `gt services …` call it). |
| `register-home-task.ps1` | Registers the logon task `GTKB-Home`: start at logon, restart within five minutes. |
| `gtkb-home.patch.yml` | GT-KB's one configuration layer over the pinned bundles: the model route, the effect guard, the Home plugin, and the upstream brand turned off. |
| `gtkb_home_guard.mjs` | The effect guard every Home session runs under. |
| `plugins/gtkb-home/` | The Home plugin: branding, attribution, title and the GT-KB pages (host `lib/index.js`, browser `lib/client.js`, marks in `assets/`). |
| `THIRD-PARTY-NOTICES.md` | Upstream licenses. |

## Install and start (operator)

Node.js 20 or newer is a prerequisite.

```powershell
python infrastructure\deepseek-web\install.py --root E:\GT-KB
powershell -NoProfile -File infrastructure\deepseek-web\register-home-task.ps1 -Root E:\GT-KB
```

Registration starts the Home and opens it in the default browser (`-NoOpen` skips that). Later, `gt home open` opens it.

`install.py`:

- verifies the lockfile against `release.json`;
- refuses an existing `node_modules`;
- runs `npm ci --ignore-scripts`. Package install scripts run only with `--allow-scripts`. `--cache <folder>` installs
  offline from a prepared npm cache.
- confirms the installed version;
- records the result in `installed.json`, including the installed tree's identity: one SHA-256 over every file's
  relative path and content digest.

It handles no credential and starts nothing.

| Command | Effect |
| --- | --- |
| `install.py --root E:\GT-KB --verify` | Recomputes the tree identity and refuses a changed or damaged tree. |
| `install.py --root E:\GT-KB --uninstall` | Removes the tree and its record, and refuses a linked tree. Stop the Home first. |

Recovery is uninstall, then install again from the same pins: from the registry, or offline with `--cache` pointing at
an npm cache that holds them. A reinstall from the same pins has the same tree identity.

The `GTKB-Home` task runs `home.py start` at logon and every five minutes. `start` is idempotent. It:

1. verifies the installation;
2. writes the pinned profile manifest;
3. in a fresh state folder, acknowledges upstream's Internal Testing Notice (see State and privacy);
4. proves that the composed configuration contains every GT-KB row, with the upstream brand disabled;
5. starts the server detached with a minimal environment;
6. returns once the guard, the plugin and the server have all reported ready.

Otherwise it stops what it started and fails.

| Command | Effect |
| --- | --- |
| `gt home start` / `gt home stop` / `gt home status` | Operate the server directly. |
| `gt home open` | Opens the Home in the default browser. The sign-in URL carries the running server's launch token, which exchanges for a 30-day browser cookie; it goes only to the browser. |
| `gt services stop home` | Pauses the task, then stops the Home, so the stop holds. |
| `gt services start home` | Resumes the task and starts the Home. |

## Model route and credential

Sessions use OpenRouter's GT-KB preset (`@preset/gtkb-openrouter-deepseek-v4-flash`) through the provider-neutral pi-ai
route. The credential is referenced only by its name, `GTKB_OPENROUTER_API_KEY`. The DeepSeek-specific provider is
turned off: OpenRouter refuses its request shape, it would ask for a second key typed into the UI, and it is the only
route that sends the harness's anonymous id.

- `home.py` takes `GTKB_OPENROUTER_API_KEY` from its environment, or from GT-KB's `.env.local` through GT-KB's own
  loader.
- It places the credential only in the server's environment.
- The value is never logged, written to a patch, or shown.

## GT-KB pages

The pages appear in Settings, after General:

| Page | Contents |
| --- | --- |
| GT-KB | `gt status` and the dashboard's links. |
| GT-KB services | Start and stop for the authority, the dashboard, Ollama and PostgreSQL, with a confirmation before any stop. A task or service that another installation registered is shown as status only. The Home's own row is shown but has no action. |
| GT-KB controls | The live operational controls. A change is previewed as a complete proposed file with its diff, then applied with `gt controls set` only if the live file still has the digest that was previewed. |

Every control is one fixed `gt` command. It runs through the plugin's authenticated `/gtkb` channel, with an environment
that carries no credential. The controls are the signed-in owner's browser actions, never model tools.

## Governed sessions

Every Home session runs under `gtkb_home_guard.mjs`:

- One Home, one project. The effect gate judges only the project of the installation the Home belongs to, so a session
  whose workspace is outside that installation's root is refused at every gated call, reads included, before any gate
  call. The workspace is resolved through junctions and links first, and one that cannot be resolved is refused. The
  refusal (`workspace_outside_project_root`) names the workspace, where it resolves when that is somewhere else (or why
  it cannot be resolved), and the root. Start a new session in a workspace inside the root.
- The same rule covers the `workdir` a one-shot shell call names (the `pwsh` of the standard, ptc and cordis agent
  presets), absolute or relative to the workspace: one outside the root, or one that cannot be resolved, is refused, and
  otherwise the gate judges the command from the resolved workdir, where it runs. A call without a workdir is judged
  from the session's workspace, and so is every call to the persistent shell, which ignores a workdir.
- Each effect-bearing tool call (write, edit, the editor's create, replace and insert, shell) passes GT-KB's effect gate
  (`scripts/implementation_start_gate.py`). It runs under that session's own identity and workspace, and the approval
  is bound to the exact arguments.
- File reads and searches (read, read_image, glob, grep, the editor's view) reach the same gate as reads: it refuses
  credential material and allows the rest.
- A call to a shell whose directory persists across calls (the `pwsh` of the shipped `minimal` agent preset) is marked
  `persistent_shell` for the gate, which refuses a top-level directory change there.
- Network tools are denied.
- Unrecognized tools are denied.
- A gate failure of any kind denies.

The start screen's workspace menu offers the Home's root: at each start the plugin registers it as a workspace, named
after its folder, so a removed entry returns at the next start. The Windows folder dialog stays; a session in a folder
it picks outside the root is refused as above.

## State and privacy

Home state lives outside the repository, in `%LOCALAPPDATA%\GT-KB\home` (or `GTKB_HOME_STATE`). It holds:

- sessions;
- the browser-cookie secret;
- run records;
- logs, including the guard log;
- configuration proposals;
- `settings.yaml`, the server's user settings (the Models page writes there).

Telemetry is disabled (`DSH_TELEMETRY_DISABLED=1`). The sign-in URL is written only to `run\home-url.txt`.

`home.py start` writes `settings.yaml` only into a state folder that has none, production's included, with one
setting: the acknowledgement of upstream's Internal Testing Notice (`ui-onboarding.welcomeNoticeVersion`), so the
notice does not show in a fresh state. An existing `settings.yaml` is never changed. If an upstream release changes the
notice's version, the notice shows again until it is acknowledged; a pin test names the upstream package to verify
first.

The guard log, `logs\guard-decisions.jsonl`, has one JSON line per guard decision: each of the guard's own denials
and each effect-gate verdict. A line holds the time, the tool, the session id, a folder (the session's workspace, or
for a gate verdict the folder the gate judged the call from, which is a one-shot shell's resolved workdir when the call
names one), the gate's exit status (null for the guard's own denials), whether the call was allowed, and the refusal
text. Apart from that folder, the guard writes no call arguments and no environment values; a refusal text can quote
the part of the call it refused, and a workdir refusal names the workdir. A failed write is ignored, so the log is
evidence, not a control.

Every installation uses the same default state folder. A run record names the installation whose Home it describes,
and `home.py start` and `stop` refuse a record of another installation's live Home and leave it and the sign-in URL in
place. Give a second installation its own folder with `--state` or `GTKB_HOME_STATE`.

## Changing the pin

1. Update `package.json`.
2. Regenerate `package-lock.json` with npm.
3. Record the lockfile's SHA-256 and the version in `release.json`.
4. Qualify the change like any other GT-KB change.
