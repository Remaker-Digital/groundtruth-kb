# 13. Deliberations (historical reasoning)

Deliberations are historical reasoning data. They can explain an earlier
discussion or rejected alternative, but they do not record current owner
decisions, authorization, review approval, claims or completion. Apply an
owner's answer directly to the applicable canonical specification, project or
work item, then read that record back.

The native authority provides read-only access to the existing deliberation
corpus. The archive has no current creation, amendment, relation-writing or
semantic-index workflow. Its historical content and outcome labels remain
historical observations; they do not revive the workflow that produced them.

## Retrieve historical context

```bash
# Find records by a case-insensitive title substring.
gt deliberations list --search "rate limiting" --limit 20 --json

# Read records whose primary context is this specification or work item.
gt deliberations list --spec-id SPEC-1234 --json
gt deliberations list --work-item-id WI-5678 --json

# Filter the historical source type.
gt deliberations list --source-type lo_review --limit 10 --json

# Read a record or its recorded version history.
gt deliberations show DELIB-0123 --json
gt deliberations show DELIB-0123 --history --json
```

Replace example identifiers with identifiers obtained from the live list.
`--after <ID>` continues the list after a returned record ID. Search matches
titles; it does not search or embed the full content.

The `--spec-id` and `--work-item-id` filters match a deliberation's primary
`spec_id` and `work_item_id` fields. `show` returns those primary references.
Historical relation rows have no native reader or writer and do not establish
a reverse relationship on a current specification or work item.

## Use the result

Read the current canonical record before acting on any fact mentioned in a
deliberation. A historical `go`, `no_go` or `owner_decision` label is not a
current verdict or an owner instruction. A reference to a bridge exchange is
historical text and cannot be required for canonical recovery.

The native record may contain historical redaction metadata. That metadata
does not establish that arbitrary historical content is free of credentials;
retrieve only the context needed and never reproduce secrets. No current
archive writer or index rebuild is implied by the presence of historical
hashes, redaction fields or version history.

See [Deliberations](../reference/cli.md#deliberations-historical-records) for
the supported command options. Current terminology is retrieved through
`gt terms` and `gt authority`, rather than inferred from archive wording.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
