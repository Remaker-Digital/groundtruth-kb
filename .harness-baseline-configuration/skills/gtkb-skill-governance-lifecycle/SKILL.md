---
name: gtkb-skill-governance-lifecycle
description: Develop managed skills from neutral source through the current CLI and Bridge lifecycle.
---

# Managed skill lifecycle

The one authored source is `.harness-baseline-configuration/skills/<name>/SKILL.md`; its helpers and
references belong beside it. Hosts that discover it read it in place; the others
get a pointer stub that carries only its frontmatter. Frontmatter edits need
`gt harness project`; body edits do not. Retiring a skill means deleting its
directory, and re-projection removes its stubs. A harness never reads or
coordinates through a peer.

Read the dispatched work item, its single parent project, current formal intent,
test requirements, dependencies and exact Bridge attempt through the CLI.
The role comes from the literal init line bound to the current context.
This skill supplies neither a role nor permission to select unrelated work.

Scope the complete behavior: source, callers, tests, templates, projector support
and obsolete guidance. The proposal declares authored artifact/test paths and
applicable formal sources. Obtain independent GO and hold the exact next-artifact
claim before implementation. Native effect checks revalidate binding, checkout
and current scope.

Author valid YAML frontmatter with an exact directory-matching name and useful
description. Give concrete triggers, inputs, commands, expected results,
refusals and recovery steps. Verify commands against current CLI help.
Keep provider-specific translation in the existing projector profile/renderer.
Correct obsolete source instead of adding compatibility aliases.

Qualification includes all-target derivability, exact projection parity,
meaningful positive/refusal tests and actual affected-host loading:

    gt harness project <harness> --validate
    python scripts/check_harness_parity.py --all --validate

Report exact commands, results and gaps. The agent authors its complete READY
report and delivers through the CLI under its artifact claim; the harness only
verifies delivery. Independent review verifies specification intent and exact
Git mode/object identities. The project commits its complete verified authored
work product once all members are ready. Generated output is refreshed
operationally and excluded from the work-product commit.

After material formal-intent change following VERIFIED while still uncommitted,
start a fresh attempt on the same work item. Preserve membership and bytes;
inherit no GO, claim or effect authority from the old attempt.
