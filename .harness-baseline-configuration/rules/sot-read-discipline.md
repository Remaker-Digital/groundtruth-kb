# SoT read discipline

Read current requirements, work, dependencies, session attribution and bridge
state through their canonical CLI/domain services at the decision boundary.
This generated guidance and other projections carry no independent authority.
An allowed file read does not establish that its contents are current.

The governing sources are `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
`DCL-SOT-READ-HOOK-CONTRACT-001`, `GOV-PLATFORM-SOT-REGISTRY-001`,
`DCL-SOT-REGISTRY-RECORD-SCHEMA-001` and the current harness-baseline projection
contract. Query their current records; historical version labels in a copied
rule are not proof of current authority.

The authored hook is
`.harness-baseline-configuration/hooks/sot-read-discipline.py`. The configuration
projector derives an independent copy at
`{{HARNESS_HOOKS_DIR}}/sot-read-discipline.py` and its registration from the
baseline manifest and declared profile. A harness does not import another
harness's configuration or role state. Edit the baseline and use the projector;
never repair a generated configuration by hand.

For a covered read event, the hook reads the selected project's current registry
through `load_registry_snapshot(project_root=...)`. There is no projection or
mtime-cache fallback. A non-archived declaration's `forbidden_substitutes` names
paths that must not replace its canonical source. The substitute is not required
to be a second registered source, and a virtual canonical locator need not be a
local file. A missing or malformed registry produces an explicit block for the
covered read. An empty list declares no path restrictions; it proves neither
host coverage nor currentness.

The hook derives the project root from its exact authored or projected location,
including nested provider directories. Relative targets resolve against the
event's working directory, or the process working directory when it is omitted.
An unrelated project with the same relative filename is outside that root.

The normalized native surface accepts direct `Read` targets and `Grep`/`Glob`
search paths and patterns. Shared native adapters supply this representation
where the declared profile requires one. The shell surface handles explicit
simple-command paths for `Get-Content`/`gc`/`cat`, `Select-String`/`sls`,
`Get-ChildItem`/`gci`, `rg` and `grep`, including named path arguments and the
declared search flags. It does not execute or interpret the proposed command.
Arbitrary shell expressions, variables, substitutions and compound commands are
outside its demonstrated parser coverage. Unknown or targetless forms return no
hook decision; this is not approval, proof of current facts, or a substitute for
the applicable effect gates.

The existing projection conformance diagnostic compares declared output with the
current baseline/projector, including hook paths, registrations and shared
adapters. It supplies configuration evidence. Native event delivery, adapter
translation and observable denial on actual hosts require separate behavioral
qualification. A command string or a matching filename cannot prove invocation.

For owner-directed historical inspection or hook diagnosis, the existing
`GTKB_SOT_READ_DISCIPLINE_BYPASS=1` exception applies only to the specified command.
Use authorization already supplied for that work; do not request it again or
manufacture a packet, decision file, role assertion or permission ledger. Keep
the explanation in the conversation/session log. The exception never turns a
historical substitute into current authoritative state.
