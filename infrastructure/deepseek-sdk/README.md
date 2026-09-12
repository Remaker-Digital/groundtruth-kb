# DeepSeek Harness SDK installation

The official DeepSeek Harness SDK runs as an independent GT-KB harness from this
directory. `release.json` pins the two official wheels, the runtime executable
digest and the dependency versions; `install.py` creates the private
`runtime-env` from verified wheels and refuses an existing one; `installed.json`
records what was installed. Nothing here selects a canonical backend, stores a
credential or registers the harness.

```powershell
uv run --python 3.14 python infrastructure/deepseek-sdk/install.py --root E:\GT-KB --wheel-dir <offline wheels>
```

`harness.py` runs one bridge action: it verifies the installation against
`release.json`, binds the runtime's own session identifier through
`gt session bind`, loads the neutral baseline `AGENTS.md` and the supplied task
as the prompt, starts the pinned runtime with `gtkb_guard.mjs` (a monotonic native
tool guard that routes every editor and PowerShell effect through
`scripts/implementation_start_gate.py`, hence `gt bridge check-effects`), and exits
0 only when `gt bridge check-delivery` confirms this context's exact delivery.
Startup, binding and delivery failures, interruptions and installation drift are
distinct nonzero exit codes; the JSON report contains no message content. The
model's credential is read by the runtime from its environment and never printed.
The runtime home (the SDK's `dsh_home`, the guard patch and the guard decision log)
defaults to the bound context's own scratch directory,
`scratchpad/<session context>/deepseek-sdk/<native context id>`, which the native
effect gate grants to that context and the commit gates never stage; `--home`
overrides it.

```powershell
infrastructure\deepseek-sdk\runtime-env\Scripts\python.exe infrastructure\deepseek-sdk\harness.py `
  --init "::init gtkb lo" --document <attempt> --version <n> --task-file <task.md> --report <report.json>
```

The opt-in qualification (`GTKB_RUN_DEEPSEEK_SDK=1`, `GTKB_DEEPSEEK_SDK_DIR=<this directory with runtime-env>`)
exercises the installed runtime's actual editor and PowerShell tools against the
native CLI, incomplete delivery, interruption and a fresh successor context; the
model-driven positive case runs only when a credential is present and is reported
as not executed otherwise. The harness registry row is recorded with
`gt harnesses record` after the PostgreSQL cutover.
