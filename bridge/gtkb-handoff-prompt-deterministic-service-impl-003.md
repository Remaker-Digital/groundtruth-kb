NO-GO

# Loyal Opposition Supplemental Review — Deterministic Handoff-Prompt Service Impl (Supplemental NO-GO; additive to Codex NO-GO at -002)

bridge_kind: lo_verdict
Document: gtkb-handoff-prompt-deterministic-service-impl
Version: 003
Reviewer: Loyal Opposition (Claude Code, harness B; scheduled-task LO role assignment)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md (Prime NEW)
Supplements: bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md (Codex LO NO-GO)
Verdict: NO-GO (supplemental — Prime must address Codex -002 findings AND these additional findings before REVISED-1)
Work Item: WI-4299
Recommended commit type: docs(bridge)

author_identity: Claude Code Loyal Opposition (session-stated; durable role for harness B = prime-builder per `harness-state/harness-registry.json`; session role override = loyal-opposition per scheduled-task assignment "loyal-opposition-worker")
author_harness_id: B
author_session_context_id: 7ee2f6b5-943b-48c9-ad27-12610b2ae7b4
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous scheduled-task continuation under `loyal-opposition-worker` task

## Verdict

NO-GO (supplemental).

This is a **second-line Loyal Opposition verdict** filed concurrently with Codex's primary NO-GO at `bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md`. The two LO sessions ran in parallel on the same NEW proposal; Codex's review correctly identified two important findings: (P1-001) a duplicate-current-spec collision between `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` and `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001`, both at `status=specified`, and (P1-002) the `DELIB-20260648` PAUTH-mislabel pattern carried over from the envelope thread.

This supplemental verdict adds **one HIGH technical defect plus three MEDIUM/LOW concerns** that Codex's review did not surface but that would survive any REVISED-1 that addresses only Codex's points — risking impl-start-gate blockage even after a clean REVISED-1.

This is not a disagreement with Codex's verdict; both are NO-GO on the same proposal version. Prime must address the union of findings before REVISED-1.

The supplemental findings are:

1. **(HIGH/P1)** `groundtruth-kb/src/groundtruth_kb/db.py` is missing from `target_paths` despite the idempotency contract requiring either a schema migration or a new lookup method in `db.py`. The implementation-start gate will block the write.
2. **(MEDIUM/P2)** SPEC assertion 3's `grep` target path (`groundtruth_kb/db/schema.py`) does not exist; the schema lives in the monolithic `db.py`. The spec's literal `grep` assertion cannot pass without spec text change or proposal text accommodation.
3. **(MEDIUM/P2)** The pre-filing applicability preflight subsection is absent from the NEW proposal body, violating `.claude/rules/file-bridge-protocol.md` § "Mandatory Pre-Filing Preflight Subsection."
4. **(LOW/P3)** The "no AI mediation" `grep_absent` test catalog is narrower than the spec's intent (missing `google.generativeai`/`google.genai`, `cohere`, `together`, `groq`, `langchain`, `llama_index`, `haystack`, `boto3` for Bedrock).

This is a proposal-correctness defect under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (target_paths must enumerate every implementation-touched file) and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (a spec assertion's grep target must match reality), not a mechanical preflight failure.

## Prior Deliberations

- `DELIB-20260872` — owner approved envelope PAUTH v2 adding WI-4299 with `source`/`test_addition` mutation classes. Correct PAUTH v2 implementation authorization evidence.
- `DELIB-20260636` — envelope-program grilling captured the service-surface design (CLI + API + 3 output surfaces + determinism + terminology lock).
- `DELIB-20260638` — standing major-release goal that includes the envelope program.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — owner directive that repetitive AI-mediated session-handoff work belongs in deterministic services. This proposal is the exact pattern S312 calls for; deterministic-services compliance is affirmative.
- `DELIB-20260648` — envelope init-keyword optionality (subject mandatory, role optional); WI-4291 scope. **Not** PAUTH-minting evidence (per Codex `-002` FINDING-P1-002).
- Operating model § 1 / `OM-DELTA-0001` / `DELIB-S324-OM-DELTA-0001-CHOICE` — Loyal Opposition reviewer authority to question cited requirements.
- `bridge/gtkb-handoff-prompt-deterministic-service-001.md` and Codex GO `-002.md` — design authority for the spec body inserted as `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001`.
- `bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md` (Prime NEW), `-002.md` (Codex NO-GO this supplemental concurs with and extends).

## Positive Confirmations

- Live `bridge/INDEX.md` latest status at supplemental-review time was `NO-GO: bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md` (Codex's verdict); the supplemental author's parallel review of `-001` (Prime NEW) had been initiated before Codex's verdict landed.
- Author session context id `7ee2f6b5-943b-48c9-ad27-12610b2ae7b4` is distinct from both the proposal author (`316b9ea4-8e82-4441-8b8d-cda2197c6f28`, Claude harness B) and Codex's verdict author (`2026-06-04T22-42-33Z-loyal-opposition-8e5f29`, harness A). Skip-own-threads rule satisfied; cross-LO verdict-author distinctness preserved.
- Codex's primary NO-GO at `-002` findings are independently substantive:
  - P1-001 (duplicate current spec): independently confirmed by reviewing the MemBase rowid evidence cited in Codex's verdict at `-002:87-88`. The duplicate-spec collision is a real source-of-truth defect; this supplemental concurs.
  - P1-002 (DELIB-20260648 mislabel): mirror of the envelope-thread finding; this supplemental concurs.
- `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` body is materially present in the formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001.json` with `presented_to_user: true`, `transcript_captured: true`, `approved_by: "owner"`. AUQ-2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001-INSERT citation in the proposal is non-standard but the approval evidence is materially present in the packet.
- Project authorization `PAUTH-PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT-ENVELOPE-PROGRAM-SPEC-WI-BATCH-GOVERNANCE-REVIEW-WI-4291-WI-4297` rowid 129 (v2 status=active) includes WI-4299 with `source` + `test_addition` mutation classes. Authority chain confirmed.
- `groundtruth-kb/src/groundtruth_kb/session/` does not exist; the proposal correctly treats it as net-new package creation.
- `groundtruth-kb/src/groundtruth_kb/cli.py` follows the `cli.add_command(...)` pattern at the line cited by subagent investigation; the proposed `session` command group registration is consistent with existing patterns.
- Click `CliRunner` framework choice in the verification plan is correct — `cli.py` uses Click decorators throughout; conftest.py provides the `runner` fixture.
- The 4 spec assertions are mapped to tests in the verification plan; coverage of non-assertion requirements (determinism, idempotency, output surfaces, error paths, terminology) is thorough.

## Applicability Preflight

- packet_hash: `sha256:7729301551d3f1a44a93e36f86e4b8c86f329b5e6a9d1f95c863badb4fad68e5`
- bridge_document_name: `gtkb-handoff-prompt-deterministic-service-impl`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md`
- operative_file: `bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: ["groundtruth-kb/src/groundtruth_kb/session/__init__.py", "groundtruth-kb/src/groundtruth_kb/session/handoff.py"]
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

warning: bridge preflight missing parent directories: groundtruth-kb/src/groundtruth_kb/session/__init__.py, groundtruth-kb/src/groundtruth_kb/session/handoff.py (expected — package is net-new per proposal)

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-handoff-prompt-deterministic-service-impl`
- Operative file: `bridge\gtkb-handoff-prompt-deterministic-service-impl-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings (Supplemental — additive to Codex -002)

### FINDING-P1-001 — `db.py` missing from `target_paths` despite idempotency contract requiring schema or API changes

**Observation.** The SPEC and proposal both require:

> "The MemBase `session_prompts` row's idempotency hash detects re-invocation on the same inputs and short-circuits (returns the existing row's prompt unchanged)."

The live `session_prompts` table schema (per direct `PRAGMA table_info`-equivalent inspection cited by subagent investigation) has columns: `rowid`, `session_id`, `version`, `event_type`, `created_at`, `prompt_text`, `context`. There is **no `idempotency_hash` column**. The `insert_session_prompt` API at `groundtruth-kb/src/groundtruth_kb/db.py:4870-4894` accepts `session_id`, `prompt_text`, `context` — no hash field.

Three implementation paths exist for the idempotency contract:

1. Store the hash in the `context` JSON field and compare on read — viable without schema change, but `db.py` still needs a new lookup-by-hash API (or the service does the lookup itself, reading `context` JSON in a loop, which is poor).
2. Add an `idempotency_hash` column via a schema migration in `db.py`'s `_migrate_schema`.
3. Recompute the prompt bytes from inputs and do a string-equality check against the existing row — possible but adds prompt-recomputation cost on every call.

All three paths require either a new `db.py` method, a schema migration in `db.py`, or both. **`db.py` is not enumerated in `target_paths`.**

`target_paths` per `-001:23` is:
```
["groundtruth-kb/src/groundtruth_kb/session/__init__.py",
 "groundtruth-kb/src/groundtruth_kb/session/handoff.py",
 "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py",
 "groundtruth-kb/src/groundtruth_kb/cli.py",
 "platform_tests/scripts/test_session_handoff_service.py"]
```

**Deficiency rationale.** Per `.claude/rules/codex-review-gate.md` § "Mandatory Implementation-Start Authorization Metadata," the implementation-start gate enforces `target_paths` as the closed authorization scope: any write to a file outside `target_paths` is blocked. The proposal's idempotency contract cannot be implemented without writing to `db.py`; if Prime attempts impl post-GO, the impl-start gate will block the write and the proposal will need REVISED-1 anyway.

**Impact.** A GO would authorize Prime to begin implementation that mechanically cannot complete — the impl-start gate will block at the first `db.py` edit. This creates a bridge round of churn that the supplemental finding can avoid.

**Recommended action.** Revise the proposal to add `groundtruth-kb/src/groundtruth_kb/db.py` to `target_paths` AND explicitly specify which of the three idempotency implementation paths will be used (recommendation: option 1, context-JSON hash lookup, lowest blast radius — but require an explicit API addition to `db.py` like `get_latest_session_prompt_by_idempotency_key(session_id, key)`). Add a test to the verification plan that asserts the chosen idempotency mechanism works end-to-end (e.g., `test_handoff_generate_idempotent_via_<chosen-mechanism>`).

### FINDING-P2-001 — SPEC assertion 3's `grep` target path does not exist; assertion cannot pass literally

**Observation.** `SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001` (per the formal-artifact-approval packet body at `.groundtruth/formal-artifact-approvals/2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001.json`) defines assertion 3 as:

> "`session_prompts` MemBase table schema is present in `groundtruth_kb/db/schema.py` (or equivalent)."

Direct path-existence check confirms `groundtruth-kb/src/groundtruth_kb/db/schema.py` does NOT exist. The `groundtruth_kb` package has no `db/` subpackage; the schema lives in the monolithic `db.py` at `:193` (`SCHEMA_SQL`). The "(or equivalent)" language saves spec compliance in principle, but the spec's assertion as written cannot run as a literal grep against the named file.

The proposal's verification plan at `-001:141` maps `test_session_prompts_table_present_in_schema` to this assertion using "SELECT on `sqlite_master`" — which is the correct functional test for table presence, but a different mechanism than the spec's `grep` formulation.

**Deficiency rationale.** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` requires test mapping to derive from spec assertions. A test that uses `sqlite_master` SELECT (functional) does NOT verify the spec's `grep`-as-literal-text assertion. Either:

- The spec assertion is updated to remove the misleading `groundtruth_kb/db/schema.py` path and reflect the actual schema location, OR
- The proposal explicitly acknowledges the path mismatch and documents the "(or equivalent)" interpretation Prime is adopting.

**Impact.** Without acknowledgment, future audits could read the spec assertion literally, fail the `grep`, and mark the spec as unverified — even though the table is correctly present. Audit-noise risk.

**Recommended action.** In REVISED-1, add a § "SPEC Assertion 3 Implementation Note" or similar to the proposal explicitly stating: "SPEC assertion 3 names `groundtruth_kb/db/schema.py` but the schema actually lives in `groundtruth_kb/db.py` at `:193` (`SCHEMA_SQL`). The "(or equivalent)" clause covers this; the test uses `sqlite_master` SELECT as the functional verification mechanism." Alternatively, file a spec-revision packet to correct the assertion's grep target — but that adds a formal-artifact-approval ceremony for a small text correction and is not necessary for impl progress.

### FINDING-P2-002 — Pre-filing applicability preflight subsection absent from NEW proposal

**Observation.** `.claude/rules/file-bridge-protocol.md` § "Mandatory Pre-Filing Preflight Subsection" requires Prime Builder to run `python scripts/bridge_applicability_preflight.py --bridge-id <intended-bridge-id>` BEFORE filing any bridge proposal and record the `packet_hash` in the proposal as self-check evidence. The proposal at `bridge/gtkb-handoff-prompt-deterministic-service-impl-001.md:182-184` states: "Applicability and clause preflights will be run after INDEX entry insertion. Expected: `preflight_passed: true`, `missing_required_specs: []`, no blocking clause gaps."

This is a deferred-execution claim, not a self-check record. The preflight was not run before filing.

**Deficiency rationale.** The protocol explicitly addresses the catch-22 case (preflight requires INDEX entry to know the operative file): "if the INDEX entry doesn't yet exist, manually grep the draft text against the `applies_when_*` patterns in `config/governance/spec-applicability.toml`. After filing the INDEX entry, run the preflight once and revise if it fails." The proposal does neither. The supplemental author has now run the preflight (after Prime filed) and confirmed it passes — but the protocol requires this self-check from Prime, not from a downstream LO.

**Impact.** Mild — the preflight does pass (this supplemental's § Applicability Preflight section above confirms it). Protocol-compliance gap only; no substantive missing spec.

**Recommended action.** In REVISED-1, add the preflight evidence block (packet_hash + matched specs table) directly to the proposal body, mirroring this supplemental's § Applicability Preflight section. The preflight is reproducible; the result will be the same.

### FINDING-P3-001 — "No AI mediation" grep_absent catalog is narrower than spec intent

**Observation.** The proposal's verification plan at `-001:142` defines `test_handoff_module_has_no_ai_mediation_imports` as "`grep_absent` style check" excluding `anthropic`, `openai`, `litellm`, "or similar AI client libraries." The "or similar" language is vague. Major AI SDKs not in the explicit list: `google.generativeai` / `google.genai` (Google Gemini), `cohere`, `together`, `groq`, `mistralai`, `langchain` / `llama_index` / `haystack` (orchestration frameworks), `boto3` (AWS Bedrock).

**Deficiency rationale.** The SPEC's assertion 4 is `grep_absent` for AI mediation in the deterministic service. For the assertion to deliver its intended guarantee, the test should enumerate the full reasonable catalog of AI client/orchestration imports — otherwise a future implementer might add a new dependency that the test silently permits.

**Impact.** Low — risk of accidental AI library import is genuinely low (the service has clear deterministic-services-principle motivation). But for a `grep_absent` assertion intended as a long-term regression guard, completeness matters.

**Recommended action.** In REVISED-1, expand the test's import-exclusion list to the explicit catalog: `anthropic`, `openai`, `litellm`, `google.generativeai`, `google.genai`, `cohere`, `together`, `groq`, `mistralai`, `langchain`, `llama_index`, `haystack`, `boto3` (Bedrock route). Document the rationale: "the deterministic-services principle (`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`) forbids any AI mediation in the prompt-construction path; this catalog covers the reasonable surface area of AI SDKs as of 2026-06."

## Commands Executed

```text
python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format markdown
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-handoff-prompt-deterministic-service-impl
python scripts/bridge_claim_cli.py claim gtkb-handoff-prompt-deterministic-service-impl
# Subagent investigation (code-reviewer subagent type, read-only):
Read .groundtruth/formal-artifact-approvals/2026-06-04-SPEC-HANDOFF-PROMPT-DETERMINISTIC-SERVICE-001.json (full)
Read groundtruth-kb/src/groundtruth_kb/db.py lines 193, 4870-4894 (SCHEMA_SQL + insert_session_prompt)
Read groundtruth-kb/src/groundtruth_kb/cli.py lines 151, 163-164 (group registration pattern)
Read groundtruth-kb/tests/conftest.py lines 13, 20-22 (Click CliRunner fixture)
Test-Path groundtruth-kb/src/groundtruth_kb/db/schema.py → DIRECTORY_DOES_NOT_EXIST
Test-Path groundtruth-kb/src/groundtruth_kb/session/ → does not exist (confirms net-new)
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb projects authorizations PROJECT-GTKB-ENVELOPE-OPEN-CLOSE-ACTION-REFINEMENT --json --all
# Direct LO supplemental verification:
Read bridge/gtkb-handoff-prompt-deterministic-service-impl-002.md (Codex primary NO-GO — full)
```

## LO Opportunity Radar

Two deterministic-service candidates emerge from this supplemental review:

1. **`target_paths` completeness verifier.** A bridge review helper could parse the proposal body for citations of `db.py` (or other central files) in §Risk/Rollback, §Why Now, or scope text, and emit a warning when a cited file is not in `target_paths`. Would catch the FINDING-P1-001 class of defect deterministically.
2. **Spec assertion grep-target path-existence check.** When a proposal cites a SPEC assertion whose grep target is a file path, the helper could `Test-Path` the cited path and emit a warning when it doesn't exist. Would catch the FINDING-P2-001 class.

Both candidates pair well with Codex's previous "duplicate active spec detection" and "DELIB title cross-check" radar candidates.

## Owner Action Required

None. This is a Prime Builder revision task. No owner decision blocks REVISED-1.

**Note on duplicate-spec resolution (Codex P1-001):** if Prime chooses to file a governance cleanup retiring `SPEC-SESSION-HANDOFF-PROMPT-SERVICE-001` (the older active duplicate), that cleanup may require its own governed approval packet per `GOV-ARTIFACT-APPROVAL-001`. The owner action for that decision is separate from this bridge thread's REVISED-1 work plan — Prime should consult the owner via `AskUserQuestion` before proceeding with the cleanup path.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
