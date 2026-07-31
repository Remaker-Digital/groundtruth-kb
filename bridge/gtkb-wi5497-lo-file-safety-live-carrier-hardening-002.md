GO
::init gtkb pb
::open test

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f7815-a565-78d3-a599-dec8388086ff
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Loyal Opposition; reasoning_effort=xhigh; sandbox=none; thread_source=user
author_metadata_source: x-codex-turn-metadata plus current owner transcript role assignment

# Loyal Opposition Proposal Review - GO - WI-5497 LO File-Safety Live Carrier Hardening

bridge_kind: lo_verdict
Document: gtkb-wi5497-lo-file-safety-live-carrier-hardening
Version: 002
Responds to: bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5497-LO-FILE-SAFETY-SEVEN-FILE-BUILD-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5497
Recommended commit type: fix(governance)

## Verdict

GO. Version 001 identifies a real Loyal Opposition live-carrier safety gap and proposes the right bounded repair: one shared, side-effect-free mutation payload normalizer; thin Claude/Codex/Cursor/Antigravity adapters; and focused tests proving equivalent whole-carrier mutation intent is denied before execution while additive bridge verdict and valid approval-packet paths keep working.

The GO is limited to the owner-approved seven-file build scope. It does not authorize hook registration, harness settings, dispatcher configuration/runtime, TAFE state, runtime JSON, routing, eligibility, caps, leases, provider contact, credentials, deployment, release, Git push/history rewrite, destructive cleanup, `groundtruth.db` mutation, MemBase row mutation, Deliberation Archive mutation, or unrelated worktree paths.

## First-Line Role Eligibility And Review Independence

PASS. This interactive session is operating as Loyal Opposition by direct owner instruction in the current chat. `GO` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`, and v001 is latest `NEW`, which is Loyal-Opposition-actionable.

PASS. Version 001 was authored by Prime Builder session `019f6668-9974-7d72-a456-826f9a67e627`. This verdict is authored by Loyal Opposition session `019f7815-a565-78d3-a599-dec8388086ff`. The session contexts differ, so this is not same-session self-review.

## Applicability Preflight

- packet_hash: `sha256:1721eaa18217e0f06881e348057fd69516ce38060ecfe5ed960ac44a7d3c91f4`
- bridge_document_name: `gtkb-wi5497-lo-file-safety-live-carrier-hardening`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md`
- operative_file: `bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- declared_target_paths: [`.claude/hooks/lo-file-safety-gate.py`, `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`, `scripts/cursor_hook_adapter.py`, `scripts/lo_file_safety_payloads.py`, `scripts/antigravity_hook_adapter.py`, `platform_tests/scripts/test_lo_file_safety_payloads.py`, `platform_tests/scripts/test_antigravity_hook_adapter.py`]
- candidate_evidence_hash: `sha256:8fb8ba793aaa2b19273b9f04332c783c8f81aa8b09943bdc20f55b4d6ca983b3`

## Clause Applicability

- Bridge id: `gtkb-wi5497-lo-file-safety-live-carrier-hardening`
- Operative file: `bridge\gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must-apply clauses: 0
- Blocking gaps: 0
- Mode: mandatory Slice 2 gate

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Evidence Reviewed

- `gt projects show-authorization PAUTH-DISPATCHER-BLACK-BOX-WI5497-LO-FILE-SAFETY-SEVEN-FILE-BUILD-20260718 --json` - active singleton PAUTH includes only `WI-5497`; permits bridge, metadata, governance evidence, source, configuration, and test only for the approved hook/source/test boundary; forbids credentials, deployment, dispatcher mutation, TAFE mutation, runtime-state mutation, external systems, destructive cleanup, Git history rewrite, and push.
- `gt deliberations show DELIB-20260718-WI5497-SEVEN-FILE-BUILD-SCOPE --json` - owner approved the exact seven-file scope and explicitly excluded hook registration, harness configuration, dispatcher/TAFE configuration or runtime mutation, credentials, deployment, and unrelated files.
- `gt backlog show WI-5497 --json` - records the reproduced P0 live-carrier defect, the seven exact paths, the active PAUTH, and clean/absent preimage state.
- `gt tests show TEST-11581 --json` - governed acceptance carrier requires Claude, Codex, Cursor, and Antigravity mutation payloads to deny whole-carrier replacement of `groundtruth.db`, preserve concurrent sentinel rows, preserve allowed LO verdict writes, and fail closed on opaque mutation syntax.
- `git status --short -- <seven targets>` - no output; the three existing targets are clean and the four new targets are absent.
- `Get-FileHash -Algorithm SHA256` for existing targets:
  - `.claude/hooks/lo-file-safety-gate.py`: `CEB1892BE8258DFC51C89BE6E368C6E6EB22C98D34EF29BFF19183285289C4D1`
  - `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py`: `4A6F1D1BFFC9471B200CA912DA7BE466675543D0273ED231C1983E0787A12ED2`
  - `scripts/cursor_hook_adapter.py`: `555697E41F0837E5962B8978393B32EBBA512B99406FB5FD843C246B6697C73F`
- `.claude/hooks/lo-file-safety-gate.py` - current `WRITEISH_COMMAND_RE` includes `git restore` and `git checkout`, but not `git reset`; `_changed_paths()` recognizes only Claude `Write`/`Edit`/`MultiEdit`, `Bash`, and apply-patch payloads, and returns an empty change set for unrecognized mutation tool names.
- `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` - currently forwards the raw Codex payload to the canonical hook with Codex harness defaults, with no shared mutation schema.
- `scripts/cursor_hook_adapter.py` - currently maps Cursor command payloads into Claude-style `Bash`/tool payloads locally, with no shared mutation schema.
- `rg ... scripts/antigravity_hook_adapter.py platform_tests/scripts/test_lo_file_safety_payloads.py platform_tests/scripts/test_antigravity_hook_adapter.py` - all three are absent, matching the proposal's net-new target plan.
- `python -m pytest platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q --tb=short` - 12 passed, 1 pre-existing pytest config warning for unknown `asyncio_mode`.
- `ruff check .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py` - all checks passed.
- `ruff format --check .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py` - 3 files already formatted.
- `python -m py_compile .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py` - exit 0.
- `git diff --check -- .claude/hooks/lo-file-safety-gate.py .codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py scripts/cursor_hook_adapter.py` - exit 0.
- `python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md --json` - PASS, packet hash above.
- `python scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5497-lo-file-safety-live-carrier-hardening-001.md` - PASS, must-apply gaps 0.

## Findings

### F1 - The live-carrier false-negative class is real

The current canonical hook has a path-aware deny path for selected write and restore forms, but it does not classify `git reset`, Python whole-file copy/replace forms, or unsupported Antigravity write payloads. Returning an empty change set for an unrecognized mutation-capable payload is unsafe for `groundtruth.db`.

### F2 - The seven-file owner boundary resolves the adapter ownership problem

The owner decision explicitly includes the Codex and Cursor adapters as editable implementation targets, and the PAUTH matches that scope. That removes the earlier ambiguity where adapter behavior was part of the defect but outside the build slice.

### F3 - The proposal preserves the right separation between build and ops

WI-5497 changes hook/source/test bytes only. Registration and harness configuration remain owned by later ops work. This is the correct sequencing for a black-box bridge/TAFE/harness complex: first prove equivalent local behavior, then wire it into harness configurations under separate authority.

## Required Implementation Constraints

1. Acquire exact same-session `go_implementation` claim and schema-v3 implementation-start authority before editing any target.
2. Revalidate the three existing target hashes and the absence of the four new targets immediately before implementation start; drift must fail closed or be adopted by fresh review.
3. Keep all implementation changes to the seven declared paths.
4. Do not mutate hook registration, harness settings, dispatcher configuration/runtime, TAFE state, runtime JSON, routing, eligibility, caps, leases, provider contact, credentials, deployment, release, Git push/history rewrite, destructive cleanup, `groundtruth.db`, MemBase rows, Deliberation Archive rows, or unrelated paths.
5. The shared normalizer must be side-effect-free and must fail closed on opaque mutation-capable syntax involving the live carrier.
6. Equivalent mutation intent across Claude, Codex, Cursor, and Antigravity payload shapes must produce equivalent allow/deny decisions with harness-native response translation.
7. Additive new LO verdict publication and valid content-exact approval-packet behavior must remain allowed; overwrite/delete and invalid/mismatched packets must remain denied.
8. Tests must use disposable carriers only and prove concurrent sentinel-row survival.

## Scope Of This Verdict

Verdict-file only. I did not mutate source, tests, dispatcher configuration, TAFE state, runtime JSON, leases, harness registry, hook registration, harness settings, `.codex`, `groundtruth.db`, MemBase rows, credentials, deployment state, release state, Git state, or external systems.
