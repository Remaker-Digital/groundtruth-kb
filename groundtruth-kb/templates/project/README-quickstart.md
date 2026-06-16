# {{PROJECT_NAME}} — Quickstart

This adopter application was scaffolded by `gt project init` per
ADR-ISOLATION-APPLICATION-PLACEMENT-001. Adopter applications live at
`<gt-kb-root>/applications/<name>/` and consume GT-KB through a service
endpoint rather than mounting the product database directly.

## Phase 4 service endpoint

`groundtruth.toml` carries a `[service]` block with an `endpoint` placeholder:

```toml
[service]
endpoint = "configure-me://placeholder/v1"
```

Override `endpoint` per environment to point at a real GT-KB service. For
local development you can keep the placeholder while using the bundled
adopter-scope `groundtruth.db`. Run `gt project doctor --profile dual-agent`
to confirm the service-endpoint contract is satisfied (the
`isolation:service-endpoint` doctor check fails on absent or raw-DB endpoints
per ADR).

## Bridge essentials

TAFE-backed bridge state is the canonical workflow state for proposals reviewed
through the bridge. Retired bridge-index artifacts are not live bridge state.
The bridge protocol is described in `.claude/rules/bridge-essential.md`; never
delete bridge files (they form the audit trail).

## Adopter-owned vs product-managed

- Adopter-owned: `memory/`, `bridge/`, `.groundtruth/formal-artifact-approvals/`,
  this README, your work-list, your release-readiness file.
- Product-managed: hook scripts under `.claude/hooks/`, rule files under
  `.claude/rules/`, the managed-artifact registry, and any file marked
  `gt-kb-managed` in `groundtruth-kb/templates/managed-artifacts.toml`.

`gt project upgrade` will refresh product-managed files and request
confirmation before touching adopter-owned ones.

## Next steps

1. Adjust `groundtruth.toml` `app_title`, `brand_mark`, and `[service].endpoint`.
2. Run `gt project doctor --profile <your-profile>` to verify the workspace.
3. Run `gt backlog list` to plan your first work items.

---

© {{COPYRIGHT_NOTICE}}
