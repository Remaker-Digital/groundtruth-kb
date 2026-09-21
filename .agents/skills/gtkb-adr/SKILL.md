---
name: gtkb-adr
description: Author or amend a canonical architecture decision, preserving its context, rejected alternatives, observed failures and consequences through the native spec CLI.
argument-hint: "<assigned ADR identifier or topic>"
allowed-tools: Bash, Read, Grep
license: "Proprietary - (c) 2026 Remaker Digital"
metadata:
  project: groundtruth-kb
  category: specifications and governance
---
# Architecture decision authoring

Use this guidance for assigned architecture work in the current spec activity.
Follow the current immutable session binding and assigned scope. GOV-20 and
GOV-ARTIFACT-AUTHORITY-HIERARCHY-001 govern the formal record; this skill is
derived authoring guidance, not a separate authority or permission step.

Read the selected ADR and its current formal dependencies with `gt spec show
<id> --json`. Use `gt spec list --search <topic> --json` to find related current
records, following its bounded pagination as needed. Do not inspect a legacy
database or import a legacy database class, infer an ID from a numeric
maximum, or use a generated harness directory as canonical source.

Preserve these five information topics in the authored description:

1. **Context**: the problem, constraints and relevant current requirements.
2. **Decision**: the chosen behavior and the boundary of the decision.
3. **Failed Approaches**: approaches actually tried and what was observed.
   Distinguish them from reasoned rejections. If available evidence establishes
   no attempted approach, say so; never invent an experiment to fill a heading.
4. **Alternatives Considered**: meaningful rejected alternatives and why.
5. **Consequences**: benefits, costs, risks, limitations and affected work.

Use clear sections or equivalent organized prose. Cite current formal sources
where necessary. Keep the record self-contained: it must not depend on a
retained bridge message, a conversation, an approval ledger or another
harness's notes for its meaning. Preserve formal history when revising.

Prepare a UTF-8 JSON fields file using the supported native specification
schema. An ADR has type `architecture_decision`; its authored fields must agree
with current formal lifecycle and assigned work. Use the selected identifier,
the freshly read version and the current context's attribution:

```text
gt spec record --id <id> --fields-file <fields.json> --expected-version <version> --actor <current-context> --change-reason "<concrete correction>" --json
gt spec show <id> --json
```

Version zero asserts a new record; an amendment uses the observed current
version. A conflict requires a fresh read and reconciliation, not an overwrite.
Compare the returned and reread fields with the intended postimage. Record
owner direction directly in its canonical result; logs retain conversation.
Ask only unresolved material choices, one at a time.

An ADR does not authorize or perform implementation. Derived implementation
uses the current project and Bridge proposal/review/test lifecycle. Structural
authoring checks do not prove runtime conformance or independent verification.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
