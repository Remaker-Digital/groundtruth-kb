---
name: gtkb-arch-audit
description: Inspect assigned architecture requirements and their actual evidence through native readers without promoting structural checks into conformance claims.
argument-hint: "<assigned formal identifier or bounded scope>"
allowed-tools: Bash, Read
license: "Proprietary - Remaker Digital"
metadata:
  project: groundtruth-kb
  category: governance
  governance: GOV-20
---
# Architecture evidence review

Review only the assigned scope using current canonical ADRs, DCLs, requirements
and their linked executable tests. Read the records with `gt spec show <id>
--json` and their declared tests with `gt tests list --spec-id <id> --json`.
Read all relevant bounded pages; a path declaration is not clause coverage.

Use `gt assert --spec <id> --json` for structural assertion evidence. A broad
`gt assert --json` audit is appropriate only when that broad scope was assigned.
Keep its actual exit code, result and unresolved evidence. A source match,
active record or passing structural check cannot establish that the behavior
is implemented, enforced or independently verified.

For each requirement, identify the intended behavior and examine whether the
current implementation and executed tests cover it. Distinguish observed
behavior from structural evidence, missing tests, failed tests, unexecuted
work, unavailable inputs and independent review that remains open. Do not
invent an ENFORCED classification from a lifecycle label plus grep results.

GOV-20 preserves ADR decision, context, failed approaches, alternatives and
consequences. Report absent information honestly. An untried alternative is
not a measured failed experiment, and a declared assertion is not a runtime
test. The current Bridge workflow supplies implementation proposal, independent
review, report and verification; historical IPR/CVR documents replace none of
those outcomes.

For a declaration-population report, the existing utility
`python groundtruth-kb/scripts/audit_adr_dcl_metadata.py --config <config.toml>
--format markdown` reads current ADR/DCL metadata through native GET requests.
Its counts include inactive current rows and distinguish their statuses. Missing
paths and tag frequencies are observations, not conformance or taxonomy
decisions. A paginated observation is not an atomic corpus snapshot.

Report findings with their current source and bounded evidence. Apply an
assigned correction through its canonical writer and follow the existing
defect-intake process for remaining work. This review does not create a
second audit database, DOC receipt, permission history, lifecycle status or
automatic commit. Any canonical amendment or independent verdict remains a
separate act under its actual role and scope.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
