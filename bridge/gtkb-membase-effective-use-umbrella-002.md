NO-GO

author_identity: loyal-opposition/codex-special-owner-authorized
author_harness_id: A
author_session_context_id: 019ecc04-9ec8-7e81-a2e7-10000eba4ed9
created_at: 2026-06-16T00:00:00Z
responds_to: bridge/gtkb-membase-effective-use-umbrella-001.md
verdict_type: proposal_review

# Loyal Opposition Review: MemBase Effective Use Umbrella

## Verdict

NO-GO.

The proposal addresses a real product goal, but this April umbrella is no longer
approval-ready. It fails live applicability preflight and references obsolete
path conventions.

## Evidence

Command:

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-membase-effective-use-umbrella --content-file bridge\gtkb-membase-effective-use-umbrella-001.md --json
```

Observed result: exit `5`.

Live path checks:

- `templates/hooks`: absent
- `src/groundtruth_kb/intake.py`: absent
- `groundtruth-kb/templates/hooks`: present
- `groundtruth-kb/src/groundtruth_kb/intake.py`: present

## Findings

### P1 - Target paths point at obsolete roots

The proposal targets `templates/**` and `src/**` at repository root, while the
live GT-KB platform code and templates are under `groundtruth-kb/`.

Required action: refile with current in-root platform paths and a bounded
sub-slice. Do not carry old root-relative paths forward.

### P1 - Live applicability preflight fails

The umbrella does not satisfy the current proposal linkage gate even though it
would create hooks, events, intake behavior, skills, and managed-artifact
registry entries.

Required action: cite the current governing specs and split the umbrella into a
reviewable implementation proposal with explicit test coverage and current
MemBase/backlog linkage.
