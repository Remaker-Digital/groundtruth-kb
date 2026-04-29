# Bridge OS Scheduler (Retired)

The former OS-scheduler bridge poller is retired.

Use [Bridge Smart Poller](bridge-smart-poller.md) for current bridge automation
guidance. The old OS scheduled-task / cron / launchd model caused excessive
background AI-harness invocations in prior GT-KB sessions and should not be
restored as the active automation path.

Historical projects may still contain files or task names that reference
`bridge-os-poller`. Treat those as compatibility names unless the project owner
explicitly directs restoration of the retired implementation.
