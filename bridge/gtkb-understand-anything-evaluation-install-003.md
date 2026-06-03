REVISED

# gtkb-understand-anything-evaluation-install (Slice 1) — REVISED: closes NO-GO -002 F1 (.gitignore in target_paths) + F2 (platform-root graph handling policy)

bridge_kind: implementation_proposal
Document: gtkb-understand-anything-evaluation-install
Version: 003
Author: Claude Code Prime Builder (harness B)
Date: 2026-06-03 UTC
Responds-To: bridge/gtkb-understand-anything-evaluation-install-002.md (NO-GO)
Recommended commit type: docs

author_identity: claude-prime-builder
author_harness_id: B
author_session_context_id: 45299969-65c1-495e-b4a7-1cecaa373ae1
author_model: claude-opus-4-7[1m]
author_model_version: Opus 4.7 (1M context)
author_model_configuration: explanatory output style; Prime Builder role; init keyword `::init gtkb pb`; /loop dynamic-mode iteration 4

Project Authorization: PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280
Project: PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
Work Item: WI-4280

target_paths: [".gtkb-state/ua-evaluation/**", ".understand-anything/**", ".gitignore", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Verdict Acknowledgement

Codex NO-GO `-002` (2026-06-03) raised two blocking P1 findings on `-001`:

- **F1 (P1)**: `.gitignore` mutation planned in §"Risk / Rollback" point 2 ("`.understand-anything/intermediate/` will be added to `.gitignore` as part of Slice 1") but `.gitignore` was NOT in `target_paths`. The implementation-start gate is path-scoped, so the planned ignore edit would have failed the gate.
- **F2 (P1)**: Platform-root `.understand-anything/knowledge-graph.json` handling was undefined. `/understand` creates the graph artifact; without an explicit policy, a GO would authorize ungoverned generation of a repo-local artifact containing synthesized project knowledge — a source-control and information-disclosure risk per the prior LO INSIGHTS warning of 2026-05-28.

Both findings share the same operational fix: add `.gitignore` to `target_paths` and commit to a single concrete platform-root policy. This REVISED selects the **least-risk path** Codex named in its proposed solution: ignore the entire platform-root `.understand-anything/` tree so no generated UA artifacts (graph, intermediate, or otherwise) become committed during the evaluation slice. The governed `INSIGHTS-2026-06-03-UA-EVALUATION.md` scaffold remains the only repo-tracked deliverable of Slice 1.

This REVISED is a content delta against `-001`: target_paths line updated, two new sections added (`## Platform-Root `.understand-anything/` Handling Policy` and `## Required Revisions Closure`), and the Spec-Derived Verification Plan extended with two new commands. All other sections (Specification Links, Prior Deliberations, Owner Decisions / Input, Requirement Sufficiency, Risk / Rollback, Bridge Filing, Recommended Commit Type) carry forward from `-001` unchanged.

## Required Revisions Closure (per NO-GO -002 §"Required Revisions")

### F1 closure — `.gitignore` added to target_paths

`target_paths` (header above, line 22) now includes `.gitignore`. The PAUTH `PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280` covers the `config_change` mutation class, which encompasses `.gitignore` edits per the PAUTH's recorded `allowed_mutation_classes`. The implementation-start gate will now mint a packet covering the planned edit; no impl-start-gate denial path remains for the ignore work.

### F2 closure — Platform-root `.understand-anything/` policy: IGNORED (least-risk path)

Selected policy: **the entire `.understand-anything/` tree is gitignored at platform root during the evaluation slice.** No UA-generated artifact is committed by Slice 1. The governed INSIGHTS scaffold remains the only repo-tracked deliverable. Per-application graph commit policy (per AUQ-3 candidate spec `CAND-SPEC-UA-GRAPH-COMMIT-POLICY`, recorded in `DELIB-20260632`) remains a candidate spec gated on the future owner verdict and is explicitly OUT of Slice 1 scope.

### F3 (verification plan update)

The Spec-Derived Verification Plan now includes two new commands that exercise the ignore policy: (1) confirms `.gitignore` contains `.understand-anything/` (or an equivalent broader-prefix entry that subsumes it); (2) sweeps the working tree post-Slice-1 to confirm no `.understand-anything/` path is git-tracked. See §"Spec-Derived Verification Plan (extended)" below.

## Platform-Root `.understand-anything/` Handling Policy

Slice 1 chooses the **ignored** policy for platform-root `.understand-anything/` content. The full ignore is broader than the original `.understand-anything/intermediate/` mitigation in `-001` §"Risk / Rollback" point 2: in addition to UA's intermediate working state, the platform-root `knowledge-graph.json` (created by `/understand` per the upstream README) and every other UA-generated artifact under that tree is excluded from the repo for the entirety of the evaluation slice.

**Rationale for `ignored` over alternatives:**

1. **Aligns with evaluation-only scope.** Slice 1 is explicitly evaluation, not adoption (AUQ-1 = D). Repo-tracked graph artifacts only become meaningful in adoption.
2. **Honors the prior LO INSIGHTS warning** (`INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md`): generated UA artifacts may contain raw summaries, business-logic terms, and file metadata; until a scan-and-handling policy is formalized, the safest disposition is no-commit.
3. **Preserves the rejected-alternatives audit trail.** The "commit per application" candidate spec (`CAND-SPEC-UA-GRAPH-COMMIT-POLICY` per AUQ-3 = A) remains visible in `DELIB-20260632`; this Slice's ignored policy is a deliberate evaluation-time narrowing, not a contradiction.
4. **Removes the source-control risk class entirely** during the evaluation window. No accidental commit of synthesized project knowledge is possible if the directory is gitignored.

**Rejected alternatives (carried forward for the audit trail):**

- **Commit with scan evidence:** would require designing and running a scan policy this slice does not have authority to define formally.
- **Delete after evaluation:** trades source-control safety for ephemerality; an interrupted slice could leave generated content in the working tree.
- **Selective ignore (`intermediate/` only, allow `knowledge-graph.json`):** the originally-proposed narrower ignore. Codex F2 specifically called this out as insufficient: the graph artifact itself carries the disclosure risk, not just the intermediate state.

**Ignore-policy edit (the exact line added to `.gitignore`):**

```text
.understand-anything/
```

The trailing slash form matches both the platform-root directory and any nested content. Placement is alongside the existing `.gtkb-state/` entry to keep evaluation-tier ignores grouped.

**Note on append-only audit trail:** the proposed `.gitignore` edit is additive (one line added). No existing entry is removed or rewritten.

## Specification Links

(Carry forward from `-001`; one additional citation added for the F2 policy section.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; NEW/REVISED/GO/implement/post-impl/VERIFIED flow with `bridge/INDEX.md` canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing spec cited in this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization`, `Project`, `Work Item` metadata block at header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — extended verification plan maps both -002 findings to concrete tests below.
- `GOV-STANDING-BACKLOG-001` — `WI-4280` is the durable backlog record; `TEST-11138` linked in `PHASE-015`.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the 5 candidate specifications remain surfaced in `DELIB-20260632`; this REVISED does NOT formally promote any.
- `GOV-ARTIFACT-APPROVAL-001` — `DELIB-20260632` approval packet on disk; `presented_to_user=true`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-...-WI-4280` is the bounded envelope; status active; covers `WI-4280`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope satisfies the constraint.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass bridge review; this REVISED is the explicit demonstration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the platform-root install (AUQ-5 = A) is NOT inside `applications/<name>/`; no isolation contract violation. `.gitignore` is at platform root, in-root under `E:\GT-KB`.

**Advisory citations** (carry forward from `-001`):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

(Carry forward from `-001`; one additional precedent for the F2 policy.)

- `DELIB-20260632` (S386 2026-06-03, owner_conversation, owner_decision) — Owner AUQ Envelope: Understand-Anything Evaluation Initiation (10 Decisions). The foundational owner-decision DELIB this proposal operationalizes.
- `DELIB-S324-OM-DELTA-0001-CHOICE` — Loyal Opposition authority over cited requirements.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — operating-model `application` / `project` / `platform` / `hosted application` terminology baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md` — prior LO evaluation warning that `.understand-anything/` generated artifacts may contain raw summaries, business-logic terms, and file metadata, requiring explicit scan and handling policy before team sharing. The §F2 policy in this REVISED is the explicit response.

_Live deliberation search (`gt deliberations search "Understand-Anything WI-4280 UA evaluation install graph ignore policy" --limit 8`) returned no UA-specific DELIB records beyond `DELIB-20260632` and the prior INSIGHTS report above._

## Owner Decisions / Input

This REVISED depends on owner approval; per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel, the authorizing AskUserQuestion evidence is the foundational `DELIB-20260632` envelope (carried forward from `-001`).

**Foundational owner-decision DELIB (carry-forward):** `DELIB-20260632` (10 AUQ answers from S386 2026-06-03; approval packet sha256 `348f64572e9b2c03cfb62e6581b5052f80b7b0144fd674c20c45a52957a10e28`).

**No new owner AUQ is required by this REVISED.** The F1 and F2 fixes are mechanical responses to Codex's stated NO-GO requirements (verbatim from `-002` §"Required Revisions"). Codex's recommended policy direction — least-risk ignore — is the path selected, so no new owner-decision class is introduced. The CAND-SPEC-UA-GRAPH-COMMIT-POLICY candidate (AUQ-3) remains a candidate; this REVISED does not formally promote it and does not contradict it (per-application policy may differ from platform-root evaluation policy).

**Owner Action Required:** None. Codex confirmed this in `-002` §"Owner Action Required".

## Requirement Sufficiency

**Existing requirements sufficient.**

Carry-forward from `-001`: the project scope envelope at `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` v1 + the PAUTH envelope are sufficient owner authorization for the bounded Slice 1 work. The `.gitignore` config_change is within PAUTH-allowed mutation classes. No new or revised formal specification is required.

The platform-root ignore policy chosen in §F2 closure is a Slice-1 operational scope decision, not a candidate or formal spec promotion. It coexists with `CAND-SPEC-UA-GRAPH-COMMIT-POLICY` (per-application AUQ-3 answer) without contradiction.

## Spec-Derived Verification Plan (extended)

This section retains the full -001 verification plan and adds two new commands (T-F1 and T-F2) covering the NO-GO `-002` closures. The mapping satisfies `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` for the proposal-time gate. All commands run from the GT-KB workspace root (`E:\GT-KB`) and are Windows/PowerShell-compatible.

**Bridge protocol & mandatory preflights (carry-forward):**

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `preflight_passed: true`, `missing_required_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `Blocking gaps: 0`.

**T-F1 — `.gitignore` contains `.understand-anything/` entry (closes NO-GO -002 F1):**

```text
python -c "from pathlib import Path; t = Path('.gitignore').read_text(encoding='utf-8'); print('has-entry:', '.understand-anything/' in t)"
```
Expected: `has-entry: True`. Verifies the planned ignore edit landed; the implementation-start gate accepted the `.gitignore` mutation because `.gitignore` is in `target_paths`.

**T-F2 — No `.understand-anything/` path is git-tracked after Slice 1 (closes NO-GO -002 F2):**

```text
git ls-files .understand-anything/
```
Expected: empty output (no rows). Verifies that the `ignored` policy held: the `/understand` invocation under test criterion (a) produced no repo-tracked artifact under the platform-root tree.

Alternative form (works pre-install when the directory may not exist yet):

```text
python -c "import subprocess; r = subprocess.run(['git','ls-files','.understand-anything/'], capture_output=True, text=True); print('tracked-count:', len([l for l in r.stdout.splitlines() if l]))"
```
Expected: `tracked-count: 0`.

**Project / authorization / WI linkage (carry-forward):**

```text
python -c "from groundtruth_kb import cli; cli.main(['projects','show','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"
```
Expected: project active; `WI-4280` listed.

```text
python -c "from groundtruth_kb import cli; cli.main(['projects','authorizations','PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION'])"
```
Expected: PAUTH-...-WI-4280 listed, status `active`, owner_decision `DELIB-20260632`.

```text
python -c "from groundtruth_kb import cli; cli.main(['backlog','show','WI-4280'])"
```
Expected: WI record with linked TEST-11138, project_name PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION.

**DELIB and approval packet (carry-forward):**

```text
python -c "from groundtruth_kb import cli; cli.main(['deliberations','get','DELIB-20260632'])"
```
Expected: record with source_type=owner_conversation, outcome=owner_decision.

```text
python -c "from pathlib import Path; p = Path('.groundtruth/formal-artifact-approvals/2026-06-03-DELIB-20260632.json'); print('exists:', p.exists(), 'size:', p.stat().st_size if p.exists() else 0)"
```
Expected: `exists: True`, size > 8000 bytes.

**WI-4280 Test (TEST-11138) acceptance criteria — manual verification, PHASE-015 (carry-forward):**

(a) **UA Claude Code plugin responsive to `/understand` command in this session.** Verification command (post-install): invoke `/understand` and capture the response in the post-impl report.

(b) **Candidate exclude list file present and matches the AUQ-4 list verbatim.**

```text
python -c "from pathlib import Path; p = Path('.gtkb-state/ua-evaluation/excludes-candidate.toml'); print('exists:', p.exists()); print(p.read_text(encoding='utf-8')) if p.exists() else None"
```
Expected: file exists; content includes `groundtruth.db`, `.groundtruth/`, `.groundtruth-chroma/`, `.gtkb-state/`, `harness-state/`, `.claude/hooks/*.log`, `.claude/session/`, `.codex/session/`. INDEXED list confirmed: `bridge/`, `.claude/rules/`, `CLAUDE.md`, `AGENTS.md`, `independent-progress-assessments/` are NOT in the exclude file.

(c) **PB pre-validation results documented (structural + semantic queries run; false-positive/false-negative counts captured).** Verification: the post-impl report MUST contain a `## PB Pre-Validation Results` section.

(d) **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md` scaffolded with placeholder sections for owner navigation tasks and verdict capture.**

```text
python -c "from pathlib import Path; p = Path('independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md'); print('exists:', p.exists()); t = p.read_text(encoding='utf-8') if p.exists() else ''; print('has owner-tasks heading:', '## Owner Navigation Tasks' in t); print('has verdict heading:', '## Owner Verdict' in t); print('cites DELIB:', 'DELIB-20260632' in t)"
```
Expected: all booleans `True`.

**Phantom-spec sweep (carry-forward; spec set unchanged from -001):**

```text
python -c "
import sqlite3
con = sqlite3.connect('groundtruth.db')
ids = ['GOV-FILE-BRIDGE-AUTHORITY-001','DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001','DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001','DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001','GOV-STANDING-BACKLOG-001','GOV-SPEC-CAPTURE-TRANSPARENCY-001','GOV-ARTIFACT-APPROVAL-001','GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001','ADR-ISOLATION-APPLICATION-PLACEMENT-001','DCL-PROJECT-AUTHORIZATION-ENVELOPE-001','PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001']
q = ','.join('?'*len(ids))
rows = {r[0] for r in con.execute(f'SELECT DISTINCT id FROM specifications WHERE id IN ({q})', ids).fetchall()}
missing = [i for i in ids if i not in rows]
print('missing:', missing)
"
```
Expected: `missing: []`. Pre-file confirmation 2026-06-03 21:47Z this iteration: `missing: []`.

## Risk / Rollback

(Carry forward from `-001` with one risk superseded by the F2 policy.)

**Risks:**

1. **UA plugin install failure** (Node.js dependency mismatch, network unreachable, npm/pnpm version skew). Mitigation: the install runs interactively in the active Claude Code session; failure is observable immediately and does not corrupt repo state.
2. **UA generates large `.understand-anything/intermediate/` files during the structural+semantic pass.** Mitigation: `.understand-anything/` (whole tree) is gitignored per §F2 closure; intermediate, graph, and any other UA artifact is excluded from version control during the evaluation slice.
3. **LLM-API costs from semantic-graph pass** (UA uses the inherited Claude Code auth path per AUQ-7). Mitigation: PB pre-validation is bounded to one structural and one semantic query against GT-KB platform code, not a full corpus scan.
4. **Candidate exclude list false-positives or false-negatives.** Mitigation: pre-validation explicitly measures both as part of test criterion (c); findings drive the post-evaluation owner verdict.
5. **Owner navigation tasks (future slice) reveal Slice 1 exclude list is wrong.** Mitigation: candidate specifications are NOT promoted to formal SPECs in Slice 1; revision is cheap.
6. **NEW — Graph artifact disclosure risk if ignore policy is bypassed.** Mitigation: T-F2 verification command (`git ls-files .understand-anything/`) confirms zero tracked paths in the post-impl report; any non-zero result fails verification and triggers a NO-GO.

**Rollback (unchanged from `-001`):** single-commit revert; `Remove-Item -Recurse -Force .understand-anything\, .gtkb-state\ua-evaluation\` for residual state; `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` retired via `gt projects retire` with citation to rejection deliberation.

The `kb_mutation_in_scope: false` header above guarantees that this Slice 1 proposal does NOT add new GT-KB-managed specifications, work items, or deliberations beyond the four already created this session.

## Bridge Filing (INDEX-Canonical)

This REVISED is filed under `bridge/` as `bridge/gtkb-understand-anything-evaluation-install-003.md`. A `REVISED: bridge/gtkb-understand-anything-evaluation-install-003.md` line is prepended to the existing `gtkb-understand-anything-evaluation-install` document entry in `bridge/INDEX.md` (append-only; no prior version deleted or rewritten). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

Pre-file claim: `python scripts/bridge_claim_cli.py claim gtkb-understand-anything-evaluation-install` executed 2026-06-03 21:47:34Z; held by current session `45299969-65c1-495e-b4a7-1cecaa373ae1`; TTL 21:57:34Z; exit 0.

## Recommended Commit Type

`docs:` — same as `-001`. The dominant repo-tracked Slice 1 deliverable is the INSIGHTS evaluation report. The `.gitignore` edit is a one-line config_change that supports the evaluation; per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B, `docs:` remains the correct Conventional Commits type for a governance/evaluation-report dominant slice.

## Self-Check (Pre-Filing)

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, this REVISED is self-checked against the operative-file applicability and clause preflights as part of the next bridge tool-use cycle. Codex MUST rerun both `scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install` against this operative file (`-003`) and include the regenerated sections in any verdict.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
