NEW

# gtkb-understand-anything-evaluation-install (Slice 1) — Install UA at platform root, author candidate exclude list, PB pre-validate, scaffold INSIGHTS evaluation report

bridge_kind: prime_proposal
Document: gtkb-understand-anything-evaluation-install
Version: 001
Author: Claude Code Prime Builder (harness B)
Date: 2026-06-03 UTC

author_identity: claude-prime-builder
author_harness_id: B
author_session_context_id: 06e40a38-aa06-4832-b896-24665506a321
author_model: claude-opus-4-7[1m]
author_model_version: Opus 4.7 (1M context)
author_model_configuration: explanatory output style; Prime Builder role; init keyword `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280
Project: PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
Work Item: WI-4280

target_paths: [".gtkb-state/ua-evaluation/**", ".understand-anything/**", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal authorizes Slice 1 of `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` (`WI-4280`): install Understand-Anything (https://github.com/Lum1104/Understand-Anything) via the native Claude Code plugin path at GT-KB platform root `E:\GT-KB`; author a candidate exclude-list file under `.gtkb-state/ua-evaluation/` matching the AUQ-4 binaries-and-runtime-state list; run a PB pre-validation pass exercising UA across structural and semantic queries against GT-KB platform code; and scaffold `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md` as the evaluation report skeleton ready for the owner-driven navigation tasks that will follow this slice. The work is evaluation-only: nothing is added to `groundtruth-kb/templates/managed-artifacts.toml`; no per-application UA scaffold is built; no candidate specification is promoted to a formal SPEC. Conversion to default-install is explicitly gated on a future owner GO/NO-GO verdict via AskUserQuestion (per AUQ-1 + AUQ-8 in `DELIB-20260632`).

The proposal operationalizes the 10 owner AUQ decisions captured in this session as `DELIB-20260632` (Owner AUQ Envelope: Understand-Anything Evaluation Initiation). The `PAUTH-...-WI-4280` envelope authorizes the bounded mutation classes (`documentation`, `config_change`, `source`), explicitly forbids managed-artifacts-toml additions and default-install scaffold promotion, and includes only `WI-4280` so the Write-time allowlist remains tight.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol governs how this proposal is filed, reviewed, and verified through `bridge/INDEX.md`. The proposal is filed `NEW` with this content and follows the standard NEW → GO → implement → post-impl → VERIFIED flow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing specification is cited in this section per the proposal-spec-linkage gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — proposal cites `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` and `WI-4280` in the metadata block above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan below maps each linked specification to a concrete check command.
- `GOV-STANDING-BACKLOG-001` — `WI-4280` is the durable backlog record for Slice 1 work; created with linked `TEST-11138` (GOV-12) assigned to `PHASE-015` Manual Verification (GOV-13).
- `GOV-09` — owner stated 10 specification-language requirements via AskUserQuestion this session; the 10 candidate specifications and their answers are recorded verbatim in `DELIB-20260632` rather than silently promoted.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the 5 candidate specifications (CAND-SPEC-UA-STRICT-ISOLATION, -GRAPH-COMMIT-POLICY, -DEFAULT-EXCLUDES, -INSTALL-METHOD, -LLM-AUTH) are surfaced explicitly in `DELIB-20260632` as candidates pending formal promotion gated on evaluation verdict; they are NOT inserted into the `specifications` table by this proposal.
- `GOV-ARTIFACT-APPROVAL-001` — `DELIB-20260632` approval packet on disk at `.groundtruth/formal-artifact-approvals/2026-06-03-DELIB-20260632.json` with `presented_to_user=true`, `transcript_captured=true`, `approved_by=owner`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-...-WI-4280` is the bounded project authorization envelope; status active; covers `WI-4280`; cites `DELIB-20260632` as the owner-decision deliberation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope satisfies the constraint: records owner-decision id, scope summary, allowed mutation classes, forbidden operations, included work-item id, included spec id, audit metadata.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — this proposal demonstrates that PAUTH does not bypass bridge review: the PAUTH exists, but Loyal Opposition review of this proposal is still required.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the platform-root install (AUQ-5 = A) is NOT inside `applications/<name>/`; no isolation contract violation. The strict-isolation candidate spec (CAND-SPEC-UA-STRICT-ISOLATION per AUQ-2) is a future-runtime configuration concern, NOT a Slice 1 install-location concern.
- `GOV-06` — touching `.understand-anything/`, `.gtkb-state/ua-evaluation/`, and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md` for the first time brings those paths under control through the PAUTH + bridge-GO chain.

**Advisory citations** (preflight-reported advisory triggers; cited for completeness):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the work creates MemBase artifacts (project, WI, DELIB, PAUTH) and references the Deliberation Archive; the artifact-oriented development pattern governs how those artifacts compose.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the proposal uses candidate / verified / retired lifecycle vocabulary (candidate specifications, evaluation verdict, future retire-on-rejection path).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — owner decisions, requirements, specifications, ADR/DCL citations, work items, and backlog all surface through governed artifacts per the artifact-oriented governance pattern.

## Prior Deliberations

- `DELIB-20260632` (S386 2026-06-03, owner_conversation, owner_decision) — Owner AUQ Envelope: Understand-Anything Evaluation Initiation (10 Decisions). The foundational owner-decision DELIB this proposal operationalizes; it records the 10 AUQ answers, the 5 candidate specifications, the rejected alternatives, and the IN/OUT scope envelope. This proposal is the direct implementation artifact of that envelope's "IN" scope.
- `DELIB-S324-OM-DELTA-0001-CHOICE` — Loyal Opposition authority over cited requirements; relevant because review of this proposal may include requirement-disambiguation findings on the 10 AUQ answers and the 5 candidate specifications.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — operating-model `application` / `project` / `platform` / `hosted application` terminology baseline; the proposal uses these terms per `.claude/rules/operating-model.md` §2.

_No prior deliberations on Understand-Anything specifically exist (fresh peer-system integration evaluation; no precedent in the Deliberation Archive)._

## Owner Decisions / Input

This proposal depends on owner approval; per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel, the authorizing AskUserQuestion evidence is enumerated below.

**Foundational owner-decision DELIB:** `DELIB-20260632` (10 AUQ answers from this session, S386 2026-06-03; `--owner-presented` flag set; approval packet sha256 `348f64572e9b2c03cfb62e6581b5052f80b7b0144fd674c20c45a52957a10e28`).

**The 10 AskUserQuestion answers that authorize this work:**

1. Install scope: **D — Install for evaluation only — defer default-install decision** (this proposal's scope follows directly)
2. Index scope when working on an application: **A — applications/<name>/ only — strict isolation** (candidate spec; runtime concern, not Slice 1)
3. Knowledge-graph commit policy: **A — Commit knowledge-graph.json per application; gitignore intermediate/** (candidate spec; Slice 1 doesn't commit a graph)
4. Default GT-KB-internal excludes: **A — Binaries & runtime state only** (concrete list authored by Slice 1; candidate spec status)
5. Evaluation install host: **A — Platform root E:\GT-KB — dogfood on GT-KB itself** (this proposal's install location)
6. Windows install path: **A — Native Claude Code plugin install** (this proposal's install method; POSIX shell installer ruled out)
7. LLM auth: **A — Reuse Claude Code plugin path — inherit harness auth** (no separate Anthropic API key needed for evaluation)
8. Evaluation exit gate: **A — Hands-on demo + owner verdict** (future-slice scope; not part of Slice 1)
9. Evaluator: **C — Both — PB scaffolds/pre-validates; owner does final navigation tasks** (Slice 1 = PB pre-validation; future slice = owner navigation tasks)
10. Evidence preservation: **B — DELIB + dedicated report under independent-progress-assessments/** (Slice 1 scaffolds the report skeleton)

**Project + authorization context:**

- Project: `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` (rowid 230, v1, active, start 2026-06-03)
- PAUTH: `PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280` (rowid 107, v1, active; cites DELIB-20260632)
- Work item: `WI-4280` (created via `gt backlog add-work-item`; linked `TEST-11138` in `PHASE-015` Manual Verification)

**Owner directive (verbatim):** "I would like to add Understand-Anything (https://github.com/Lum1104/Understand-Anything) to GT-KB as a default installed option. I would like to determine the correct configuration for a GT-KB user who is working on an application within GT-KB, so that default file exclusions and preferences are appropriate. Please investigate and evaluate this proposal, then grill me for more detail and initiate a project called 'Understand-Anything'." (S386 2026-06-03)

**Continuation directive:** "Please continue," (S386 2026-06-03; authorizing the bridge-proposal filing step explicitly via AUQ "Path A — full compliance (DELIB → WI → PAUTH → scaffold)" and "Yes — record now as DELIB-S386-UA-EVAL-AUQ-ENVELOPE; cite from wherever".)

## Requirement Sufficiency

**Existing requirements sufficient.**

Cited governing requirements:
- `GOV-09` classifies the owner's 10 AUQ statements as specification-language input; recording them as `DELIB-20260632` rather than silently promoting them is the GOV-09-compliant path.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` requires owner-visible surfacing of candidate specifications; the 5 candidate specs are surfaced in `DELIB-20260632` and re-surfaced in this proposal's `Owner Decisions / Input` section.
- The project scope envelope at `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` v1 + the PAUTH envelope are sufficient owner authorization for the bounded Slice 1 work.

No new or revised formal specification is required before Slice 1 implementation. Formal promotion of the 5 candidate specifications (CAND-SPEC-UA-STRICT-ISOLATION, -GRAPH-COMMIT-POLICY, -DEFAULT-EXCLUDES, -INSTALL-METHOD, -LLM-AUTH) is OUT of scope for this proposal and gated on the owner GO/NO-GO verdict from the future evaluation slice.

## Spec-Derived Verification Plan

This section is the specification-derived verification plan: a spec-to-test mapping that ties each linked specification to a concrete command and expected result. The mapping satisfies `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` for the proposal-time gate. All commands run from the GT-KB workspace root (`E:\GT-KB`) and are Windows/PowerShell-compatible (Python one-liners or repo-native tools per the workstation's shell context).

**Bridge protocol & mandatory preflights:**

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `preflight_passed: true`, `missing_required_specs: []`. Verifies `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `Blocking gaps: 0`. Verifies clause-level satisfaction of `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and any blocking ADR/DCL clauses applicable to this proposal type.

**Project / authorization / WI linkage:**

```text
python -c "from groundtruth_kb import cli; cli.main(['projects','show','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"
```
Expected: project record displayed with `WI-4280` listed under its work-item memberships. Verifies `GOV-STANDING-BACKLOG-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`.

```text
python -c "from groundtruth_kb import cli; cli.main(['projects','authorizations','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"
```
Expected: PAUTH-...-WI-4280 listed, status `active`, owner_decision `DELIB-20260632`. Verifies `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`.

```text
python -c "from groundtruth_kb import cli; cli.main(['backlog','show','WI-4280'])"
```
Expected: WI record with linked TEST-11138, source_spec_id GOV-09, project_name PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION. Verifies `GOV-STANDING-BACKLOG-001`, `GOV-09`.

**DELIB and approval packet:**

```text
python -c "from groundtruth_kb import cli; cli.main(['deliberations','get','DELIB-20260632'])"
```
Expected: record with source_type=owner_conversation, outcome=owner_decision, session_id matches, content begins with "Owner AUQ Envelope: Understand-Anything Evaluation Initiation". Verifies `GOV-09`, `GOV-SPEC-CAPTURE-TRANSPARENCY-001`.

```text
python -c "from pathlib import Path; p = Path('.groundtruth/formal-artifact-approvals/2026-06-03-DELIB-20260632.json'); print('exists:', p.exists(), 'size:', p.stat().st_size if p.exists() else 0)"
```
Expected: `exists: True`, size > 8000 bytes. Verifies `GOV-ARTIFACT-APPROVAL-001`.

**WI-4280 Test (TEST-11138) acceptance criteria — manual verification, PHASE-015:**

Each test criterion below MUST be observable for the post-implementation report to claim PASS:

(a) **UA Claude Code plugin responsive to `/understand` command in this session.**

Verification command (post-install): invoke `/understand` slash command in the active Claude Code session and capture the response in the post-impl report.

(b) **Candidate exclude list file present and matches the AUQ-4 list verbatim.**

```text
python -c "from pathlib import Path; p = Path('.gtkb-state/ua-evaluation/excludes-candidate.toml'); print('exists:', p.exists()); print(p.read_text(encoding='utf-8')) if p.exists() else None"
```
Expected: file exists; content includes exactly: `groundtruth.db`, `.groundtruth/`, `.groundtruth-chroma/`, `.gtkb-state/`, `harness-state/`, `.claude/hooks/*.log`, `.claude/session/`, `.codex/session/`. INDEXED list confirmed: `bridge/`, `.claude/rules/`, `CLAUDE.md`, `AGENTS.md`, `independent-progress-assessments/` are NOT in the exclude file.

(c) **PB pre-validation results documented (structural + semantic queries run; false-positive/false-negative counts captured).**

Verification: the post-impl report MUST contain a `## PB Pre-Validation Results` section enumerating: at least one structural query (e.g., "show file/class graph for `groundtruth-kb/src/groundtruth_kb/cli.py`") and at least one semantic query (e.g., "where is bridge dispatch implemented?") with raw UA responses, plus a table of detected false-positives (paths excluded that shouldn't be) and false-negatives (paths NOT excluded that should be) against the AUQ-4 list.

(d) **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md` scaffolded with placeholder sections for owner navigation tasks and verdict capture.**

```text
python -c "from pathlib import Path; p = Path('independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md'); print('exists:', p.exists()); t = p.read_text(encoding='utf-8') if p.exists() else ''; print('has owner-tasks heading:', '## Owner Navigation Tasks' in t); print('has verdict heading:', '## Owner Verdict' in t); print('cites DELIB:', 'DELIB-20260632' in t)"
```
Expected: `exists: True`, all three booleans `True`.

**Phantom-spec sweep:**

```text
python -c "
import sqlite3
con = sqlite3.connect('groundtruth.db')
ids = ['GOV-FILE-BRIDGE-AUTHORITY-001','DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001','DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001','DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001','GOV-STANDING-BACKLOG-001','GOV-09','GOV-SPEC-CAPTURE-TRANSPARENCY-001','GOV-ARTIFACT-APPROVAL-001','GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001','ADR-ISOLATION-APPLICATION-PLACEMENT-001','DCL-PROJECT-AUTHORIZATION-ENVELOPE-001','PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001','GOV-06']
q = ','.join('?'*len(ids))
rows = {r[0] for r in con.execute(f'SELECT DISTINCT id FROM specifications WHERE id IN ({q})', ids).fetchall()}
missing = [i for i in ids if i not in rows]
print('missing:', missing)
"
```
Expected: `missing: []`. All cited specifications exist in the live `specifications` table.

## Risk / Rollback

**Risks:**

1. **UA plugin install failure** (Node.js dependency mismatch, network unreachable, npm/pnpm version skew). Mitigation: the install runs interactively in the active Claude Code session; failure is observable immediately and does not corrupt repo state.
2. **UA generates large `.understand-anything/intermediate/` files during the structural+semantic pass.** Mitigation: `.understand-anything/intermediate/` will be added to `.gitignore` as part of Slice 1 (AUQ-3 candidate spec); evaluation pass is scoped to a single platform-root run, not a full sweep.
3. **LLM-API costs from semantic-graph pass** (UA uses the inherited Claude Code auth path per AUQ-7). Mitigation: PB pre-validation is bounded to one structural and one semantic query against GT-KB platform code, not a full corpus scan.
4. **Candidate exclude list false-positives** (paths excluded that shouldn't be) **or false-negatives** (paths NOT excluded that should be). Mitigation: pre-validation explicitly measures both as part of test criterion (c); findings drive the post-evaluation owner verdict.
5. **Owner navigation tasks (future slice) reveal Slice 1 exclude list is wrong.** Mitigation: candidate specifications are NOT promoted to formal SPECs in Slice 1; revision is cheap (edit the candidate exclude file).

**Rollback:**

Single-commit rollback path. If the bundled commit lands and the owner subsequently rejects the evaluation:
1. `git revert <commit-sha>` reverts the INSIGHTS report scaffold + any operational files added to the working tree.
2. `python scripts/uninstall_ua_claude_code_plugin.sh` (or equivalent — the actual install path is determined during Slice 1 execution) removes the UA plugin.
3. `Remove-Item -Recurse -Force .understand-anything\, .gtkb-state\ua-evaluation\` cleans residual operational state.
4. MemBase records (PROJECT, WI-4280, DELIB-20260632, PAUTH) remain as append-only history; they are not deleted but `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` can be retired via `gt projects retire` with a citation to the rejection deliberation.

The `kb_mutation_in_scope: false` header above guarantees that this Slice 1 proposal does NOT add new GT-KB-managed specifications, work items, or deliberations beyond the four already created this session (`PROJECT-...`, `WI-4280` + `TEST-11138`, `DELIB-20260632`, `PAUTH-...`). The verdict DELIB and any candidate-spec formal promotions are explicitly OUT of scope until the future evaluation-slice bridge proposal.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-understand-anything-evaluation-install` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`docs:` — the dominant repo-tracked change is the INSIGHTS-2026-06-03-UA-EVALUATION.md evaluation report. The candidate exclude list lives under `.gtkb-state/` (gitignored operational tier). The UA plugin install does not produce repo-tracked changes. The bridge proposal + INDEX entry are themselves audit-trail evidence; per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B, `docs:` is the correct Conventional Commits type for governance/runbook/evaluation-report dominant changes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
