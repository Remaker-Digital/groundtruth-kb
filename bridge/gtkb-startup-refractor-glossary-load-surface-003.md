REVISED

# Implementation Proposal - Startup Refractor First Finding: Glossary-Load Surface (GTKB-STARTUP-REFRACTOR-001)

bridge_kind: prime_proposal
Document: gtkb-startup-refractor-glossary-load-surface
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-REFRACTOR-001

target_paths: ["scripts/session_self_initialization.py", "scripts/startup_glossary_load.py", "platform_tests/scripts/test_startup_glossary_load.py", "platform_tests/scripts/test_session_self_initialization.py"]

This REVISED proposal addresses the first key finding from `STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md`: "Generated startup service still does not surface the new glossary-load requirement." Other findings are deferred to follow-on slices.

## Revision Notes

This `-003` revision addresses every finding in the `-002` NO-GO:

- **F1 (P1) — stale `tests/scripts/**` test path.** The loader and verification plan are moved off the stale root `tests/scripts/**` tree. The authorized test files are now `platform_tests/scripts/test_startup_glossary_load.py` (new, loader + payload-degradation tests) and the existing `platform_tests/scripts/test_session_self_initialization.py` (extended with the rendered-payload Glossary-section integration test). `target_paths` and the Specification-Derived Verification Plan now reference only `platform_tests/**` surfaces, which `pyproject.toml` `testpaths` and the CI workflows discover. No package-root `groundtruth-kb/tests/` test is needed because F2's resolution places the loader in a root `scripts/` module (see F2).
- **F2 (P1) — package loader not importable from the direct SessionStart hook path.** Resolved by placing the loader in a root-importable `scripts/` module — `scripts/startup_glossary_load.py` — instead of `groundtruth-kb/src/groundtruth_kb/startup/glossary_load.py`. The SessionStart hooks and `scripts/session_self_initialization.py` already insert the project root on `sys.path` (`scripts/session_self_initialization.py:45-47`; `.claude/hooks/session_start_dispatch.py:76`; `.codex/gtkb-hooks/session_start_dispatch.py:70`), so a `scripts.startup_glossary_load` import resolves on the real hook execution path with no global install. The integration is additionally written fail-soft: if the loader import or the glossary file read fails, the startup service still renders a payload (the Glossary section degrades to a bounded one-line note) rather than aborting startup.
- **F3 (P2) — verification plan does not prove the emitted SessionStart payload.** A new integration test (T6) runs the startup service through the same `--emit-startup-service-payload --fast-hook` entry shape the hook uses, asserts the emitted `hookSpecificOutput.additionalContext` payload contains a bounded `Glossary` section, and asserts graceful degradation when `.claude/rules/canonical-terminology.md` is absent from a test project root.
- **Non-blocking note — advisory spec omissions.** The three advisory specs flagged by the `-002` preflight (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in `## Specification Links`.

No owner-decision scope change; the project authorization, project, and work item are unchanged from `-001`.

## Claim

Add an explicit glossary-load step to the startup service that loads `.claude/rules/canonical-terminology.md` content into the rendered startup payload, so role-assigned harnesses receive the canonical vocabulary in their session initialization without separately reading the file. The loader is a root-importable `scripts/` module so the direct SessionStart hook execution path can import it without a global package install.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. `scripts/startup_glossary_load.py` and `scripts/session_self_initialization.py` are in-root platform scripts; `platform_tests/scripts/**` is the in-root platform test surface.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - fresh-session self-initialization disclosure requirement; the glossary load is part of that disclosure.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` - glossary as DA read surface; this proposal surfaces the glossary in startup context, which is the agent-side primary read path.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` - glossary citation contract; the loader preserves the glossary's source and implementation-pointer fields.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal as a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface adjacent to the startup hook surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-tracked work; GTKB-STARTUP-REFRACTOR-001 is the governed work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the advisory triggered a work item which triggers this implementation proposal and its tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed artifacts (WI + bridge thread + spec-derived tests).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the project authorization.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization including PROJECT-GTKB-SESSION-LIFECYCLE-UX and work item GTKB-STARTUP-REFRACTOR-001.
- `DELIB-1896` - prior canonical-terminology / DA read-surface history (cited by the `-002` review as relevant prior context).
- `DELIB-1465` - prior canonical-terminology / DA read-surface history.
- `DELIB-1595` - prior canonical-terminology / DA read-surface history.
- `DELIB-1180` - prior bounded-context / canonical-terminology history.
- `DELIB-0722` - prior bounded-context / canonical-terminology history.

No prior deliberation rejected surfacing the glossary in the startup payload; this proposal builds on the DA read-surface placement direction rather than revisiting a rejected approach.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the PROJECT-GTKB-SESSION-LIFECYCLE-UX authorization batch (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), including this work item GTKB-STARTUP-REFRACTOR-001. The authorization `PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH` is active and covers this WI through project membership; the `-002` review independently confirmed this.
- 2026-05-02 S328: original advisory from Codex (STARTUP-PROCEDURE-REFRACTOR-ADVISORY) identified finding #1.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` and `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` already require the startup disclosure to surface the canonical glossary as the agent-side read path. Advisory finding #1 explicitly specifies the gap (the generated startup service does not surface the glossary-load requirement). No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. It implements a single work item (GTKB-STARTUP-REFRACTOR-001), first-of-8 advisory findings only. References to "work item", "backlog", and "standing backlog" describe that single governed work item and its membership in PROJECT-GTKB-SESSION-LIFECYCLE-UX per the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. The review-packet inventory is a single thread: IP-1 (loader module) + IP-2 (startup-payload integration) + IP-3 (tests). The inventory of touched files is the four `target_paths` entries above; no formal artifact is created.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-003` REVISED line is appended under the existing `Document: gtkb-startup-refractor-glossary-load-surface` block above the prior `NO-GO` and `NEW` lines; the prior versions are preserved unchanged (append-only audit trail).

## Proposed Scope

### IP-1: Glossary loader module (root-importable)

`scripts/startup_glossary_load.py` (new, root `scripts/` module so the direct SessionStart hook path can import it without a global package install):

- Function `load_glossary_for_startup(project_root: Path) -> dict[str, Any]` reads `.claude/rules/canonical-terminology.md` and returns a structured representation: term name -> `{definition, source, implementation_pointer}`.
- Returns a well-defined empty/degraded structure (not an exception) when the glossary file is absent or unreadable, so the caller can degrade gracefully.
- Caches the result for in-session reuse.

### IP-2: Startup-payload integration (fail-soft)

In `scripts/session_self_initialization.py`, add a bounded `Glossary` section to the rendered startup payload:

- The section lists canonical term names + 1-line definitions and stays bounded (a conservative line/byte cap so the payload does not balloon).
- Full content remains available via lookup in the structured representation returned by the loader.
- The integration is fail-soft: the loader is imported as `scripts.startup_glossary_load` inside a `try`/`except` consistent with the existing optional-import pattern at `scripts/session_self_initialization.py:6539`. If the import fails or the glossary file is missing, the `Glossary` section degrades to a bounded one-line note and the startup service still emits a complete payload.

### IP-3: Tests

- Loader output schema and missing-file degradation: `platform_tests/scripts/test_startup_glossary_load.py`.
- Rendered-payload Glossary-section integration through the real startup-service entry shape: `platform_tests/scripts/test_session_self_initialization.py`.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. Tests are added/updated only within the `target_paths` test files.

| Behavior / Spec clause | Test | Covers |
|---|---|---|
| Loader extracts canonical terms with definition/source/implementation_pointer | `test_loader_extracts_terms` (`platform_tests/scripts/test_startup_glossary_load.py`) | GOV-GLOSSARY-AS-DA-READ-SURFACE-001, DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001 |
| Loader returns a degraded structure (no exception) when glossary file absent | `test_loader_handles_missing_file` (`platform_tests/scripts/test_startup_glossary_load.py`) | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (fail-soft) |
| Loader caches within session, avoiding re-reads | `test_loader_caches_within_session` (`platform_tests/scripts/test_startup_glossary_load.py`) | GOV-SESSION-SELF-INITIALIZATION-001 (startup latency budget) |
| Loader module is importable as `scripts.startup_glossary_load` from project root only (no package install) | `test_loader_importable_from_project_root` (`platform_tests/scripts/test_startup_glossary_load.py`) | F2 resolution; ADR-ISOLATION-APPLICATION-PLACEMENT-001 |
| Rendered startup payload includes a bounded `Glossary` section (T6 integration through `--emit-startup-service-payload --fast-hook`) | `test_startup_payload_has_glossary_section` (`platform_tests/scripts/test_session_self_initialization.py`) | GOV-SESSION-SELF-INITIALIZATION-001, GOV-GLOSSARY-AS-DA-READ-SURFACE-001 |
| Startup payload degrades gracefully (still emitted; bounded note) when `.claude/rules/canonical-terminology.md` absent from a test project root | `test_startup_payload_glossary_degrades_when_absent` (`platform_tests/scripts/test_session_self_initialization.py`) | F3 resolution; DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |

T6 detail: the integration test invokes the startup service with `--emit-startup-service-payload --fast-hook` (the same entry shape the SessionStart hook uses), parses the emitted payload, and asserts the `hookSpecificOutput.additionalContext` content contains the bounded `Glossary` section.

Verification commands:

```
python -m pytest platform_tests/scripts/test_startup_glossary_load.py platform_tests/scripts/test_session_self_initialization.py -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

- IP-1, IP-2, IP-3 landed; all listed tests PASS.
- The loader is importable as `scripts.startup_glossary_load` from the project root with no global `groundtruth_kb` install (F2 resolved).
- The rendered startup payload, emitted through `--emit-startup-service-payload --fast-hook`, contains a bounded `Glossary` section, and degrades gracefully when the glossary file is absent (F3 resolved).
- All authorized test paths are under `platform_tests/**` (F1 resolved); `ruff check` and `ruff format --check` are clean.
- Both preflights PASS.
- Subsequent advisory findings (2-8) remain tracked for follow-on slices.

## Risks / Rollback

- Risk: glossary load adds startup latency. Mitigation: `.claude/rules/canonical-terminology.md` is a small file; a single read plus in-session caching is sub-millisecond; `--fast-hook` budget is preserved.
- Risk: an oversized glossary balloons the payload. Mitigation: the `Glossary` section is bounded by a conservative line/byte cap.
- Rollback: revert the IP-2 integration in `scripts/session_self_initialization.py`; `scripts/startup_glossary_load.py` remains a standalone module with no caller, causing no behavior change.

## Files Expected To Change

- `scripts/startup_glossary_load.py` — new root-importable glossary loader module (IP-1).
- `scripts/session_self_initialization.py` — fail-soft `Glossary` section integration into the rendered startup payload (IP-2).
- `platform_tests/scripts/test_startup_glossary_load.py` — new loader schema, missing-file degradation, caching, and root-import tests (IP-3).
- `platform_tests/scripts/test_session_self_initialization.py` — extended with the rendered-payload Glossary-section integration test and the graceful-degradation test (IP-3, T6).

## Recommended Commit Type

`feat` - net-new startup-surface capability (glossary loader module + rendered-payload section). ~80 LOC of source + tests.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

- packet_hash: `sha256:a835d623732e1ca7c89e5779a97048a5576e922654b76fe24e1052f82fddd81b`
- bridge_document_name: `gtkb-startup-refractor-glossary-load-surface`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-refractor-glossary-load-surface-003.md`
- operative_file: `bridge/gtkb-startup-refractor-glossary-load-surface-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-refractor-glossary-load-surface`
- Operative file: `bridge\gtkb-startup-refractor-glossary-load-surface-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Result: exit 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
