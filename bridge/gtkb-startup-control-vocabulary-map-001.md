NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-20260606T1019Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Keep Working PB automation; high autonomy
author_metadata_source: Codex automation context

# Implementation Proposal - Startup-Control Vocabulary Map

bridge_kind: implementation_report
Document: gtkb-startup-control-vocabulary-map
Version: 001
Date: 2026-06-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001-WI-4362
Project: PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001
Work Item: WI-4362

target_paths: ["config/agent-control/system-interface-map.toml", "docs/gtkb-systems-and-tools.md", "platform_tests/scripts/test_system_interface_map.py"]

implementation_scope: config, docs, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4362 by extending the VERIFIED GT-KB system/interface terminology
map so startup-control operator vocabulary resolves deterministically to
authoritative files or command surfaces.

Prime Builder bridge scan has no actionable latest GO/NO-GO entries. The
project `PROJECT-GTKB-SYSTEMS-TERMINOLOGY-MAP-001` remains active because
`WI-4362` is open. Its parent terminology-map work was VERIFIED at
`bridge/gtkb-systems-terminology-map-001-004.md`, so this proposal is a
follow-on extension to that VERIFIED resolver rather than a competing
terminology surface.

The implementation-start gate blocked direct mutation of
`config/agent-control/system-interface-map.toml`; that is correct because the
target is protected config. This proposal requests Loyal Opposition review
before any protected config edit.

## Specification Links

- `WI-4362` - add startup-control vocabulary locators for startup index, startup control map, role overlay, hot-path projection, and repo-local adapter.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this NEW proposal uses the file bridge as the review authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal carries concrete governing specification links.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map requirements to executed verification.
- `GOV-STANDING-BACKLOG-001` - the work item remains the backlog authority for this follow-on.
- `GOV-SESSION-SELF-INITIALIZATION-001` - startup surfaces must support correct fresh-session initialization.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` - startup-control surfaces should remain compact and navigable.
- `GOV-SESSION-ROLE-AUTHORITY-001` - role-overlay terminology must not override durable role authority.
- `DCL-SESSION-ROLE-RESOLUTION-001` - startup role terms must preserve the deterministic role-resolution order.
- `REQ-HARNESS-REGISTRY-001` - the harness registry hot-path projection is the generated startup-safe role/identity read surface.

## Prior Deliberations

- `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL` - owner approved conversion of the glossary/CLI scan delta that created `WI-4362`.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - informs the decision not to retire this project while `WI-4362` remains open.
- `bridge/gtkb-systems-terminology-map-001-004.md` - prior Loyal Opposition VERIFIED verdict for the system/interface map and resolver pattern this follow-on extends.

## Owner Decisions / Input

No new owner decision is needed. `DELIB-20260605-GLOSSARY-CLI-SCAN-DELTA-APPROVAL`
approved conversion of the glossary/CLI scan delta that created `WI-4362`;
this proposal asks only for Loyal Opposition review of the implementation plan
under that approved work item.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4362` names the five required
startup-control terms and requires each term to link to an authoritative file
or command surface. The governing startup, role-authority, and harness-registry
records listed above provide enough constraints to implement the locator rows
without creating a new specification.

## Target Paths

- `config/agent-control/system-interface-map.toml`
- `docs/gtkb-systems-and-tools.md`
- `platform_tests/scripts/test_system_interface_map.py`

## Implementation Plan

1. Add system-map rows for `startup-index`, `startup-control-map`,
   `startup-role-overlay`, `harness-registry-hot-path-projection`, and
   `repo-local-adapter`.
2. Point each row to its authoritative source or command surface:
   - startup index -> `config/agent-control/SESSION-STARTUP-INDEX.md`
   - startup control map -> `config/agent-control/SESSION-STARTUP-CONTROL-MAP.md`
   - role overlay -> `config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md` and `config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md`
   - hot-path projection -> `harness-state/harness-registry.json`, read through `groundtruth_kb.harness_projection.read_roles` / `gt harness roles`
   - repo-local adapter -> `config/agent-control/harness-capability-registry.toml` and the specific adapter path named by that registry row
3. Update the human companion compact map so operators can scan the same five
   terms without opening TOML.
4. Add a focused regression proving all five owner-facing terms resolve with
   concrete `authoritative_source` values.
5. If the rows expose stale legacy wording already adjacent to the touched
   rows, correct only the stale wording necessary to avoid contradictory
   resolver output.

## Spec-Derived Verification Plan

| Requirement | Planned verification |
| --- | --- |
| `WI-4362` startup-control locator coverage | `python -m pytest platform_tests/scripts/test_system_interface_map.py -q --tb=short` plus five CLI resolver probes |
| Alias uniqueness and map schema | Existing `validate_map()` regression in `platform_tests/scripts/test_system_interface_map.py` |
| Startup authority distinctions | Assertions over `authoritative_source` for startup index, startup control map, role overlay, hot-path projection, and repo-local adapter |

Planned CLI probes:

- `python scripts/resolve_system_interface.py "startup index" --json`
- `python scripts/resolve_system_interface.py "startup control map" --json`
- `python scripts/resolve_system_interface.py "role overlay" --json`
- `python scripts/resolve_system_interface.py "hot-path projection" --json`
- `python scripts/resolve_system_interface.py "repo-local adapter" --json`

## Risk / Rollback

- Risk: adding aliases that collide with existing rows. Control: resolver tests and existing alias-uniqueness validation.
- Risk: treating generated startup or dashboard text as authority. Control: rows distinguish authoritative source, generated projection, and summary surfaces.
- Risk: confusing role overlay with durable role assignment. Control: row text explicitly separates overlays from `harness-state/harness-registry.json` role authority.
- Risk: protected config mutation without authorization. Control: this proposal waits for LO GO before implementation; the project authorization is scoped to `WI-4362` only.

Rollback is to remove the added map rows, remove the companion-doc rows, and
remove the focused resolver test before filing the implementation report.

## Bridge Filing (INDEX-Canonical)

File this proposal as `NEW: bridge/gtkb-startup-control-vocabulary-map-001.md`
under `Document: gtkb-startup-control-vocabulary-map` in `bridge/INDEX.md`.

## Recommended Commit Type

`docs/tests`: startup-control terminology map proposal.
