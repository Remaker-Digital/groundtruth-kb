# 8. Architecture Decisions

An Architecture Decision Record (ADR) explains a significant technical choice.
A Design Constraint (DCL) states the resulting required behavior and the evidence
needed to check it. In GT-KB both are current canonical specifications, read and
amended through the configured native CLI and domain service. GOV-20 describes
the information contract; this guide explains how to use it.

## Architecture Decision Records

An ADR has type `architecture_decision`. Preserve five information topics:

- **Context:** the problem, constraints and applicable requirements.
- **Decision:** the chosen behavior and its scope.
- **Failed approaches:** what was actually tried and what was observed.
- **Alternatives considered:** rejected options and the reasons for rejection.
- **Consequences:** benefits, costs, risks, limitations and affected work.

Organize the information clearly. A reasoned rejection is different from an
observed failed experiment. When available evidence establishes no attempted
approach, say so and retain rejection reasons under alternatives. Do not invent
experiments or historical reasoning to populate a heading. Merely finding five
headings does not establish that their content is adequate.

Use an ADR for a choice whose cross-component effects, difficult reversal or
non-obvious trade-offs need explanation. For example, selecting a canonical
database affects consistency, recovery and deployment. A routine choice of a
local lookup structure usually does not need a new architecture record.

## Design Constraints

A DCL has type `design_constraint`. It identifies required behavior, the source
boundary it affects, applicable formal dependencies, and how to check it.
Assertions can help locate implementation evidence. A grep or a declared source
path is structural evidence; a successful match does not prove runtime behavior.

For example, a requirement to preserve formal history needs an amendment test
that observes the new current version and the preserved earlier version. A ban
on every SQL UPDATE or DELETE would not prove that property and would prohibit
legitimate changes to other data. Select checks for the actual requirement.

## Read, author and amend

Read the selected record and its applicable formal dependencies:

```text
gt spec show <id> --json
gt spec list --search <topic> --limit <count> --json
gt tests list --spec-id <id> --json
```

Follow bounded list results with `--after <last-id>` when needed. An ADR is a
specification with type `architecture_decision`; prepare complete authored field
changes as UTF-8 JSON, then use the current version and context attribution:

```text
gt spec record --id <id> --fields-file <fields.json> --expected-version <version> --actor <current-context> --change-reason "<concrete correction>" --json
gt spec show <id> --json
```

Version zero asserts a new record. For an amendment, use the freshly read
version. On conflict, read again and reconcile the change. Compare the result
and separate readback with the intended postimage. The native writer appends
formal history; do not edit a prior version or use a legacy database connection
as a substitute. A formal amendment does not itself implement the changed rule.

## Implementation and evidence

Derived implementation uses the current project/work-item and Bridge lifecycle:
specification-linked NEW proposal, independent GO, implementation, READY report,
independent VERIFIED for the exact work product, and the complete project commit
when every member is verified. Project authorization, next-artifact claims,
review, tests and commitment are distinct controls.

Historical IPR and CVR documents are not additional current proposal, review or
completion gates. Their presence cannot establish implementation compliance or
replace current independent verification. Retained bridge content is ephemeral
coordination and supplies no durable formal authority.

For assigned structural checks, use `gt assert --spec <id> --json` and report the
actual outcome. Assess behavior with relevant executed tests and independent
review. State failed, missing, unexecuted and structural-only evidence explicitly.
An active specification or passing assertion is not a conformance verdict.

When the decision changes, amend the ADR and affected DCLs through their writers,
reconcile the implementation and tests, and verify the resulting behavior.
Formal history preserves the prior decision and its change reason.
