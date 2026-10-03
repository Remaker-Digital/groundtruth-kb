---
name: gtkb-promote
description: "Correct a specification's canonical lifecycle state through the ordinary CLI without conflating it with implementation completion."
argument-hint: "<specification-id> <intended-state>"
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: knowledge-management
  references:
    - references/validation-rules.md
---
# Correct specification lifecycle state

Read the current specification and the owner's intended correction:

```text
gt spec show <specification-id> --json
```

A formal record's active, superseded or retired state concerns its current authority. Implementation progress, independent verification and project commit belong to work items and projects. A passing assertion must not promote a specification through the obsolete specified/implemented/verified sequence or complete its implementation work.

Follow [validation-rules.md](references/validation-rules.md) for the correction. Use the configured ordinary CLI's supported amendment command and options, discovered through `gt spec --help` and that command's `--help`. Preserve formal history, state the reason and resulting current requirement, and use the source-version check exposed by the writer. Do not import private database modules or write assertion-run history.

After the mutation, read the exact record back through `gt spec show <specification-id> --json`. Reconcile affected current citations and work scope. An owner-directed formal correction does not substitute for independent review of implementation, and a retirement does not assert that old implementation was tested or correct.

When structural observations would help, use `gt assert --spec <specification-id> --json`. Its PASS, FAIL, PARTIAL, UNASSESSED and NOT_APPLICABLE results have the limited meaning explained by the assertion skill. Perform the full required executable testing independently of those structural observations.

Never infer a target state, batch-retire failing requirements, preserve an obsolete permission predicate, or create an approval ledger. Ask for a material unresolved change of intent; an already supplied owner direction requires no duplicate approval record.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
