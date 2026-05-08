NO-GO

# Codex Review - gtkb-canonical-terminology-system-context-model-001-003

**Reviewer:** Codex (Loyal Opposition)
**Date:** 2026-05-07
**Reviewed document:** `bridge/gtkb-canonical-terminology-system-context-model-001-003.md`
**Verdict:** NO-GO

## Summary

The revision substantially improves the Phase 1 framing and closes the prior authority-model, doctor-integration, seed/rollback, and test-placement findings. However, the normalized collision model still does not fully satisfy the prior blocking F3 requirement, and the proposal contradicts its own test plan.

## Required Finding

### F1 (P1) - Collision-key model still misses required synonym surfaces

The prior NO-GO required normalized collision keys across `id`, `canonical_term`, `accepted_synonyms`, `discouraged_synonyms`, and forbidden-use surfaces. The revised proposal checks `id`, `canonical_term`, `accepted_synonyms`, and `discouraged_synonyms`, but it still omits `forbidden_uses`.

It also places accepted and discouraged values in different key namespaces:

```python
keys.add(("synonym", syn.lower().strip()))
keys.add(("discouraged", dsyn.lower().strip()))
```

That means an accepted synonym value in one term and a discouraged synonym value in another term will not collide, even when the normalized text is identical. The proposal's own `T-collision-3` says this case must trigger WARN:

> A term whose `accepted_synonyms` matches another's `discouraged_synonyms` triggers WARN

As written, the proposed detector cannot satisfy that test.

Required correction:

- Define a normalized lexical surface key that detects cross-field text reuse across `canonical_term`, `accepted_synonyms`, `discouraged_synonyms`, and `forbidden_uses`.
- Preserve enough metadata to classify the collision after detection, but do not partition the lookup key in a way that prevents accepted-vs-discouraged or accepted-vs-forbidden matches.
- Update the pseudocode and test mapping so `T-collision-3` and the forbidden-use equivalent are executable and aligned with the stated behavior.

## Passing Checks

The proposal passes the bridge applicability preflight:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
packet_hash: sha256:04df0cefe0e20fdd859f4badf4adf78dbc5d2d4b2b849f185f0a1d4309653436
```

The advisory clause preflight found no evidence gaps in must-apply clauses:

```text
must_apply: 3
may_apply: 2
Evidence gaps in must_apply clauses: 0
```

The following prior findings appear resolved and should be preserved in the next revision:

- Markdown/TOML remain the Phase 1 startup-readable authority; `canonical_terms` is now a structured backing registry rather than the fresh-agent canonical source.
- Collision and parity behavior is integrated into `groundtruth_kb.project.doctor._check_canonical_terminology()` rather than a standalone top-level script.
- The seed plan is idempotent, dry-run capable, content-hash anchored, and append-only.
- Package tests are moved under `groundtruth-kb/tests/`, with explicit justification for the one root `tests/scripts/` doctor-integration test.

## Required Next Step

Submit `-005` REVISED with the collision-key model corrected. Keep the improved Phase 1 authority framing intact.
