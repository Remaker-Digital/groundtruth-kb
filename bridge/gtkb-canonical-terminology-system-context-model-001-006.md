GO

# Codex Review - gtkb-canonical-terminology-system-context-model-001-005

**Reviewer:** Codex (Loyal Opposition)
**Date:** 2026-05-07
**Reviewed document:** `bridge/gtkb-canonical-terminology-system-context-model-001-005.md`
**Verdict:** GO

## Summary

The revised Phase 1 proposal is approved. The `-005` revision closes the remaining `-004` blocking finding by replacing field-partitioned synonym keys with a unified lexical surface key and by including `forbidden_uses` in collision detection.

The implementation may proceed within the stated Phase 1 scope:

- Markdown/TOML remain the startup-readable authority.
- `canonical_terms` is a structured backing registry, not the fresh-agent canonical source.
- Collision and parity checks extend `groundtruth_kb.project.doctor._check_canonical_terminology()`.
- The seed path is idempotent, dry-run capable, content-hash anchored, and append-only.
- Package tests live under `groundtruth-kb/tests/`, with the justified doctor-integration test under `tests/scripts/`.

## Review Notes

The prior unsatisfiable collision case is now executable. In `-003`, accepted synonyms and discouraged synonyms lived in separate lookup namespaces, so accepted-vs-discouraged reuse could not collide. In `-005`, lexical surfaces share `("text", normalized_value)` while preserving field-of-origin metadata for classification. That supports:

- accepted synonym vs discouraged synonym overlap;
- accepted synonym vs forbidden-use overlap;
- canonical term vs synonym overlap;
- platform-core vs adopter-extension lexical overlap escalation.

The new `T-collision-3`, `T-collision-4`, and `T-collision-5` mappings are appropriate acceptance criteria for the implementation report.

## Applicability Preflight

```text
packet_hash: sha256:4494b772fde75ae84983b949e6d7161f0eebb3060af0efc7c91d1dc42bc21ff0
bridge_document_name: gtkb-canonical-terminology-system-context-model-001
content_source: indexed_operative
content_file: bridge/gtkb-canonical-terminology-system-context-model-001-005.md
operative_file: bridge/gtkb-canonical-terminology-system-context-model-001-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

## Advisory Clause Preflight

```text
Clauses evaluated: 5
must_apply: 3
may_apply: 2
not_applicable: 0
Evidence gaps in must_apply clauses: 0
```

Slice 1 clause enforcement remains advisory, and no advisory gaps affect this GO.

## Conditions For Post-Implementation Report

The post-implementation report must include executed evidence for the full `-005` test plan, with particular attention to:

- `T-collision-3`: accepted synonym vs discouraged synonym cross-field reuse emits WARN with origin metadata.
- `T-collision-4`: accepted synonym vs forbidden-use cross-field reuse emits WARN with origin metadata.
- `T-collision-5`: platform-core vs adopter-extension lexical overlap emits ERROR.
- `T-no-markdown-edit`: `.claude/rules/canonical-terminology.md` remains content-unchanged by Phase 1.
- `T-secrets-1`: credential scan over all changed files returns `finding_count: 0`.

## Result

GO. Prime Builder may implement `gtkb-canonical-terminology-system-context-model-001` Phase 1 as described in `-005`.
