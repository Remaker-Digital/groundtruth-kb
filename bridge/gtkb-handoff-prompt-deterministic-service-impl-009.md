NO-GO

# Loyal Opposition Verification - Deterministic Handoff-Prompt Service Impl (NO-GO)

bridge_kind: verification_verdict
Document: gtkb-handoff-prompt-deterministic-service-impl
Version: 009
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-05 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: 2026-06-05T01-46-12Z-loyal-opposition-cb5924

## Verdict

NO-GO.

The revised report closes the mechanical bridge-preflight defect from `-007` and
the targeted tests plus ruff gates pass. Verification still cannot record
`VERIFIED` because the implemented service does not honor the
`session_id`-driven archive selection contract in the governing spec. A caller
can request `session_id="S-OLD"` and receive a prompt assembled from the newest
archive envelope for the harness instead of the envelope for `S-OLD`.

This is a behavioral mismatch against `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`
and a missing spec-derived test case.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
```

Observed exit code: 0.

```text
## Applicability Preflight

- packet_hash: `sha256:346a59b84b96bd695f939d020fe9d23ad4844f50fe7405ef4e73537003261e9c`
- bridge_document_name: `gtkb-handoff-prompt-deterministic-service-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md`
- operative_file: `bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
```

Observed exit code: 0.

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-handoff-prompt-deterministic-service-impl`
- Operative file: `bridge\gtkb-handoff-prompt-deterministic-service-impl-008.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Prior Deliberations

- `DELIB-20260872` - owner-approved envelope PAUTH v2 adding `source` and `test_addition` for WI-4299.
- `DELIB-20260636` - envelope-program grilling and WI-4299 service-surface requirements.
- `DELIB-20260638` - standing major-release goal that includes the envelope program.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - deterministic-service principle for repetitive AI-mediated work.
- `DELIB-2500` - terminology authority for "handoff prompt".
- `DELIB-2238` - session envelope foundation.
- `bridge/gtkb-handoff-prompt-deterministic-service-001.md` and GO verdict `bridge/gtkb-handoff-prompt-deterministic-service-002.md` - design authority for the inserted service spec body.
- This thread's proposal-phase NO-GO verdicts at `-002` and `-003`, GO at `-005`, implementation report at `-006`, verification NO-GO at `-007`, and revised report at `-008`.

Deliberation search command:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-4299 handoff prompt deterministic service session_id archive envelope" --limit 8
```

Relevant results included `DELIB-20260872`, `DELIB-20260638`,
`DELIB-20260658`, `DELIB-20260635`, `DELIB-20260750`,
`DELIB-20260636`, `DELIB-2808`, and `DELIB-2673`.

## Specifications Carried Forward

- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`
- `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` (acknowledged active duplicate; retirement deferred)
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py -q --no-header` | yes | pass: `18 passed, 2 warnings in 4.24s` |
| `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` session-id archive selection | focused temp-root reproduction invoking `generate(session_id='S-OLD')` with `S-OLD` and `S-NEW` envelopes | yes | fail: returned `session_id` `S-OLD` while reading `2026-06-05T02-00-00Z-session-envelope.json` |
| `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` | same focused reproduction; duplicate spec describes the same service surface | yes | fail for same reason |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | bridge applicability preflight above | yes | pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | bridge applicability preflight above | yes | pass |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | report header inspection in `-008` | yes | pass |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | this table plus executed commands | yes | fail: a linked primary service behavior lacks passing coverage |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target path inspection in `-008` plus source review | yes | pass |
| `GOV-ARTIFACT-APPROVAL-001` | report states `kb_mutation_in_scope: false`; no formal-artifact mutation verified in this thread | yes | pass |
| `GOV-STANDING-BACKLOG-001` | WI-4299 linkage in report header | yes | pass |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | bridge audit trail preserved through this verdict | yes | pass |

## Positive Confirmations

- Live `bridge/INDEX.md` latest status was `REVISED: bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md`; the thread was actionable for Loyal Opposition.
- Codex harness A resolves to durable role `loyal-opposition` in `harness-state/harness-registry.json`.
- The mechanical applicability and clause preflights both pass on the live operative report `-008`.
- The targeted handoff-service pytest suite passes: 18 tests passed.
- `ruff check` and `ruff format --check` pass on all six target files.
- The prior `-007` heading/preflight defect is addressed by the `## Specification Links` section in `-008`.
- The prior `-007` antigravity fallback defect is improved by the archive-directory resolver and covered by new regression tests.

## Findings

### FINDING-P1-001 - `session_id` is not used to select the archived envelope

**Observation:** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` states that the service reads "the latest archived session-envelope file for `session_id`" and that `<harness_name>` plus `<closed_at-ISO>` are resolved "from the session_id + directory contents" (`bridge/gtkb-handoff-prompt-deterministic-service-001.md:278`). The implemented `generate()` instead resolves only a harness archive directory, calls `_latest_archived_envelope(archive_dir)`, and then sets `resolved_session_id = session_id or _derive_session_id(envelope, envelope_path)` after the envelope is already chosen (`groundtruth-kb/src/groundtruth_kb/session/handoff.py:82`, `groundtruth-kb/src/groundtruth_kb/session/handoff.py:101`, `groundtruth-kb/src/groundtruth_kb/session/handoff.py:104`).

**Deficiency rationale:** This makes the public `session_id` argument an output-label/idempotency key input, not the archive-selection input required by the spec. With two archived envelopes, the service can return a prompt labeled for one session while embedding state copied from a different, newer session. That breaks the handoff prompt's core purpose: the next session inherits the closing session's open state. It also weakens idempotency because the key includes the requested `session_id` but the envelope bytes can belong to another session.

**Reproduction evidence:** A temp-root reproduction with two `claude` archive files produced:

```text
S-OLD
- envelope_file: 2026-06-05T02-00-00Z-session-envelope.json
- closed_at: 2026-06-05T02-00-00Z
```

The command invoked `generate(session_id='S-OLD')` while the selected envelope was the later `S-NEW` envelope. This is not a harmless display issue; the prompt body is assembled from the wrong envelope.

**Test coverage gap:** The current regression tests prove one-archive and harness-disambiguation behavior, but no test stages two archives and asserts that an explicit `session_id` selects the matching envelope. `platform_tests/scripts/test_session_handoff_service.py:213` tests determinism with one envelope per root, and `platform_tests/scripts/test_session_handoff_service.py:347` tests real identity schema with one archive.

**Proposed solution:** Change archive resolution so an explicit `session_id` selects an envelope matching that session, then falls back to latest-active-harness only when `session_id` is omitted. If WI-4293 envelope schema exposes `session_id`, parse candidate envelope JSON and require exactly one matching `session_id`. If the schema encodes session identity only through filename or another field, implement that deterministic mapping and document it in the helper name and tests. On zero matches or multiple matches, raise `HandoffError` with a clear message.

**Option rationale:** Matching the envelope before prompt assembly is the smallest behavioral correction and preserves the existing CLI/API surface. Treating `session_id` as an output-only label would require changing the governing spec and would keep the misleading "for session_id" contract in place.

**Prime Builder implementation context:** Expected touchpoints are `groundtruth-kb/src/groundtruth_kb/session/handoff.py` and `platform_tests/scripts/test_session_handoff_service.py`. Add a failing-then-passing test that creates at least two envelopes in one archive directory, invokes `generate(session_id=<older session>)`, and asserts the prompt cites the older envelope filename/closed_at. Also add a negative test for a non-existent explicit session ID.

## Required Revisions

1. Update the service so explicit `session_id` participates in archive-envelope selection before `_latest_archived_envelope` is used.
2. Add spec-derived tests for multiple archived envelopes:
   - explicit `session_id` selects the matching envelope instead of the lexicographically latest envelope;
   - explicit unknown `session_id` raises `HandoffError`;
   - omitted `session_id` still uses the most-recently-archived envelope for the active harness.
3. Re-run the existing handoff-service pytest suite, ruff check, ruff format check, and the live CLI smoke.
4. Re-file a REVISED post-implementation report carrying forward the same specification links and the new test evidence.

## Opportunity Radar

No separate advisory is needed from this pass. The deterministic-service opportunity is already the subject of WI-4299, and the only material token/test-savings cue is the required regression test above.

## Commands Executed

```text
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .codex/skills/bridge/SKILL.md
Get-Content -Raw .codex/skills/verify/SKILL.md
Get-Content -Raw .codex/skills/lo-opportunity-radar/SKILL.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/codex-review-gate.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw .claude/rules/loyal-opposition.md
Get-Content -Raw .claude/rules/report-depth-prime-builder-context.md
Get-Content -Raw harness-state/harness-identities.json
Get-Content -Raw harness-state/harness-registry.json
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-handoff-prompt-deterministic-service-impl --format json --preview-lines 80
Get-Content -Raw bridge/gtkb-handoff-prompt-deterministic-service-impl-008.md
Get-Content -Raw bridge/gtkb-handoff-prompt-deterministic-service-impl-005.md
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/session/handoff.py
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/session/__init__.py
Get-Content -Raw platform_tests/scripts/test_session_handoff_service.py
rg -n "session_prompts|get_session_prompt_by_idempotency_key|get_session_prompt\(|insert_session_prompt\(" groundtruth-kb/src/groundtruth_kb/db.py
rg -n "session_group|cli_session_handoff|add_command" groundtruth-kb/src/groundtruth_kb/cli.py
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "WI-4299 handoff prompt deterministic service session_id archive envelope" --limit 8
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_session_handoff_service.py -q --no-header
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_session_handoff_service.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/session/__init__.py groundtruth-kb/src/groundtruth_kb/session/handoff.py groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py platform_tests/scripts/test_session_handoff_service.py
groundtruth-kb\.venv\Scripts\python.exe - <<focused temp-root reproduction for explicit session_id archive selection>>
```

## Owner Action Required

None. This auto-dispatched worker cannot ask the owner interactively, and no owner decision is required to correct the implementation. The required revision is within the latest GO'd `target_paths`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
