---
name: gtkb-assert
description: "Evaluate current specification assertions through the ordinary CLI without recording results or changing work state."
argument-hint: "[--spec <id>] [--scope <scope>] [--json]"
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: governance
---
# Specification assertion observations

Use the ordinary CLI for the current assigned scope:

```text
gt assert --spec <specification-id> --json
```

Without `--spec`, the command evaluates the current active specifications of one application scope: `--scope gtkb_platform` or `--scope application:<name>`, defaulting to `application:<name>` when the project root carries an `application.toml` marker and to `gtkb_platform` otherwise. Records carrying no scope are evaluated with the selection and counted in the summary (`unscoped_specs`); records of another scope are excluded and counted (`excluded_specs`). Use that broader census only when it is within the assigned investigation. Both roles may perform this read-only observation. The command reads the configured authority; native service failure does not fall back to SQLite.

`--json` returns structured results. Omit it for the human-readable summary. `--triggered-by <label>` labels the current observation; it creates no persistent execution record. Evaluation has no `--record` mode and needs no `--dry-run` flag.

The command does not create or migrate a SQLite database, write assertion-run history, change test or work-item results, produce a verdict, or commit a project. Do not replace it with direct database access or private module imports.

## Interpret the result

- PASS means the selected executable structural checks passed against the observed source version. It does not establish the complete behavioral or independent-review obligation.
- FAIL means an evaluated check found a violation.
- UNASSESSED means required evidence was not evaluated, an assertion is unsupported, or the canonical definition changed during evaluation. Re-read current scope and perform the missing qualification.
- PARTIAL means the result combines evaluated checks with unassessed obligations.
- NOT_APPLICABLE means there was no applicable assertion to evaluate, including an explicitly selected retired or superseded record. It is not a completion result.

Only an aggregate PASS exits successfully. Required behavioral validation remains UNASSESSED when no behavioral evidence was evaluated, or PARTIAL alongside passing structural checks. File presence, matching strings and counts cannot prove that a referenced evaluator or test actually ran.

Before a bridge verdict or protected effect, use the current canonical scope and perform the complete applicable executable testing and independent review. The returned observation includes its specification version; a result for a changed definition must not be reused. Capture the command process exit code directly, without substituting a later formatting pipeline's status.

If a required evaluator, command or binding is missing or contradicts current formal guidance, carry the concrete defect into the existing corrective work. Do not repair the reported score by adding marker text, ignoring requirements or inventing an approval/evidence ledger.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
