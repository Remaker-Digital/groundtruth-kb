---
name: gtkb-spec
description: Author or amend an assigned canonical specification through the native CLI, with current-source readback and bounded assertion evidence.
argument-hint: "[new|update] <assigned identifier or topic>"
allowed-tools: Bash, Read, Grep
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: specifications and governance
  references:
    - references/assertion-format.md
---
# Specification authoring

Use this skill for assigned specification work in the current `spec` activity,
with the existing immutable session binding and actual context attribution.
GOV-ARTIFACT-AUTHORITY-HIERARCHY-001 governs current authority and owner direction.
Read the current applicable formal sources. This derived guide is not a separate
authority, permission step or proof that a service enforces every formal clause.

Drafting text is distinct from canonical persistence. Prepare and compare text
freely; persist it within owner-directed scope after resolving material choices.
Direction already given applies without a second permission ledger. Do not
mistake project authorization, an actor string, a test pass or a draft for the
owner's approval of new formal substance. A conflict between current formal
records and the directed work needs explicit reconciliation, not invented
approval fields or a claim that an absent approval service ran.

## Read and select

Use the configured native authority through the ordinary CLI:

```text
gt spec show <id> --json
gt spec list --search <topic> --limit 200 --json
gt spec list --search <topic> --limit 200 --after <last-returned-id> --json
```

Keep the same filters while paging; a full page may have successors. Read the
exact selected record and its formal dependencies, including status and version.
Distinguish a typed missing-record response from an unavailable authority.
Search results identify candidates for comparison, not automatic duplicates or
an exhaustive semantic search. Amend an existing subject when appropriate.
Use the assigned or explicitly selected identifier. Never calculate a new ID
from the largest numeric ID in a listing; creation is checked atomically with
expected version zero. Do not open SQLite, call KnowledgeDB, or read another
harness's state to recover current authority.

## Prepare the fields

A UTF-8 JSON object contains only authored fields accepted by `gt spec record`.
The identifier, expected version, actor and change reason are separate options.
For example, after the subject and scope have been settled:

```json
{
  "title": "Local service configuration requirement",
  "type": "requirement",
  "status": "active",
  "description": "The service configuration declares port 8765. Structural configuration checks are separate from actual listener and request qualification."
}
```

The native writer accepts only `active`, `superseded` and `retired` as status
values. Legacy progress labels, unknown values and explicit null are refused.
`active` identifies a current formal requirement; it does not claim completed
implementation or independent verification. New native records default to
`active` if status is omitted. An amendment that omits status retains the current
value. Read and reconcile an existing inactive state explicitly; do not promote
it merely because assertions pass. Retire or supersede a formal subject through
an appropriate forward amendment, preserving historical versions. Work-item
verification and Git activation use their own domain lifecycle.

Use the appropriate formal class, such as `requirement`, `governance`,
`design_constraint`, `architecture_decision` or `protected_behavior`, and the
current canonical vocabulary. Keep substance self-contained and preserve
unmodified semantic fields. Optional native fields include `assertions`,
`constraints`, `tags`, `source_paths`, `parent` and `affected_by`. A parent is an
explicit relationship; dependency references do not imply parenthood. Referenced
identifiers must resolve. Do not copy returned version/history fields into the
fields object or manufacture retirement timestamps. Null is an authored value,
not an instruction to preserve a field.

Assertions must state the limited observation they make. Use the supported
formats in [the assertion reference](references/assertion-format.md). Structural
checks complement executable behavioral tests and independent review; they do
not prove that code is invoked, an operation succeeds or a requirement is fully
satisfied.

## Write and read back

```text
gt spec record --id <id> --fields-file <fields.json> --expected-version <version> --actor <current-context> --change-reason "<concrete correction>" --json
gt spec show <id> --json
gt assert --spec <id> --triggered-by <current-context> --json
```

Use zero only for creation; use the freshly read version for an amendment.
After a CAS conflict, re-read and reconcile changed content before retrying.
Do not overwrite the intervening version. Compare both returned and separately
read canonical fields with the intended result, including unchanged fields and
the new version. The writer appends native change history; assertion evaluation
does not amend the specification or record an implementation verdict.

Map each implementation gap to its existing project, work item and executable
test, or use the current work-intake route where new work is required. Preserve
single-project membership and current test-plan relationships. Specification
authoring alone neither creates implementation work nor starts it. Do not
invent a project, force every test into a hard-coded plan, or substitute a
historical assertion result for current qualification.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
