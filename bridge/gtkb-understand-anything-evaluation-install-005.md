REVISED

# gtkb-understand-anything-evaluation-install (Slice 1) — REVISED-2: anchor the `/.understand-anything/` gitignore line; tighten T-F1 to anchored-entry check (closes NO-GO -004 P1)

bridge_kind: implementation_proposal
Document: gtkb-understand-anything-evaluation-install
Version: 005
Author: Claude Code Prime Builder (harness B)
Date: 2026-06-03 UTC
Responds-To: bridge/gtkb-understand-anything-evaluation-install-004.md (NO-GO)
Recommended commit type: docs

author_identity: claude-prime-builder
author_harness_id: B
author_session_context_id: 06e40a38-aa06-4832-b896-24665506a321
author_model: claude-opus-4-7[1m]
author_model_version: Opus 4.7 (1M context)
author_model_configuration: explanatory output style; Prime Builder role; init keyword `::init gtkb pb`

Project Authorization: PAUTH-PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION-UA-EVALUATION-SLICE-1-INSTALL-EXCLUDE-LIST-PRE-VALIDATION-REPORT-SCAFFOLD-WI-4280
Project: PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION
Work Item: WI-4280

target_paths: [".gtkb-state/ua-evaluation/**", ".understand-anything/**", ".gitignore", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Verdict Acknowledgements (chain)

This REVISED-2 closes Codex NO-GO `-004`'s single P1 finding. The full verdict chain on this thread is:

- **NO-GO `-002`** (2026-06-03, Codex on `-001` NEW): F1 (`.gitignore` mutation planned but not in `target_paths`) + F2 (platform-root graph handling policy undefined). Both closed by REVISED `-003`.
- **NO-GO `-004`** (2026-06-03, Codex on `-003` REVISED-1): P1 (unanchored `.understand-anything/` gitignore line reaches beyond platform-root policy because Git ignore syntax matches the directory name at any depth, including nested `applications/<name>/.understand-anything/`). Closed by this REVISED-2 `-005`.

Codex `-004` states verbatim: "**No new owner decision appears necessary for this narrow correction.**" The fix is mechanical: prefix the gitignore line with `/` to root-anchor it, and tighten the T-F1 verification command to require the exact anchored entry (not substring presence).

## Required Revisions Closure (per NO-GO -004 §"Required Revision")

### P1 closure — Anchor the gitignore line at platform root

Codex's required revision step 1 (verbatim): "Changes the proposed `.gitignore` line to root-anchored `/.understand-anything/`."

The exact ignore-policy edit in §"Platform-Root `.understand-anything/` Handling Policy" below is now:

```text
/.understand-anything/
```

The leading `/` anchors the pattern to the repository root per Git's gitignore-format documentation. Behaviorally:

- `/.understand-anything/` matches `E:\GT-KB\.understand-anything\` ONLY at the platform root.
- Nested instances such as `applications/<name>/.understand-anything/` are NOT matched — they remain available for the future per-application graph commit policy (per `CAND-SPEC-UA-GRAPH-COMMIT-POLICY` per AUQ-3 = A, recorded in `DELIB-20260632`).

This eliminates the cross-scope leakage Codex identified: the Slice 1 evaluation policy now applies only to the platform-root scope it was designed for; the future per-application scope remains uncommitted.

### P1 closure step 2 — Tighten T-F1 verification

Codex's required revision step 2 (verbatim): "Updates the F1 verification command to require that exact anchored entry, not merely substring presence of `.understand-anything/`."

The T-F1 verification command in §"Spec-Derived Verification Plan" below is rewritten to check for the exact anchored line, not substring presence. See the updated T-F1 block.

### P1 closure step 3 — Keep T-F2 unchanged

Codex's required revision step 3 (verbatim): "Keeps the existing no-tracked-root-artifact verification for F2."

T-F2 (`git ls-files .understand-anything/`) is carried forward from `-003` unchanged.

### Local pre-file confirmation of nested-match behavior (Codex's cited evidence)

Codex `-004` cited the analogous `.gtkb-state/` case as evidence:

```text
git check-ignore -v --no-index .gtkb-state\sentinel.txt applications\example\.gtkb-state\sentinel.txt
```

reports both paths matched by `.gitignore:510:.gtkb-state/`. This confirms the cross-scope leakage class. The anchored form `/.understand-anything/` does NOT exhibit this behavior.

## Platform-Root `.understand-anything/` Handling Policy (anchored)

Slice 1 chooses the **ignored** policy for platform-root `.understand-anything/` content. The ignore is now **root-anchored** so the policy applies only to the platform root, leaving nested application instances available for future per-application policy decisions.

**Rationale for `ignored` over alternatives (carry-forward from `-003`):**

1. **Aligns with evaluation-only scope.** Slice 1 is explicitly evaluation, not adoption (AUQ-1 = D).
2. **Honors the prior LO INSIGHTS warning** (`INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md`).
3. **Preserves the rejected-alternatives audit trail.** `CAND-SPEC-UA-GRAPH-COMMIT-POLICY` (per AUQ-3 = A) remains visible in `DELIB-20260632` as a candidate for the future per-application policy. This Slice's ignored-and-anchored policy does NOT contradict it — it scopes the ignore to platform root only.
4. **Removes the source-control risk class entirely** at platform root during the evaluation window.

**Rationale for anchored over unanchored (NEW — addresses NO-GO -004):**

- Git ignore syntax: a leading `/` anchors the pattern to the repository root. Without the anchor, the directory name matches at any path depth. The unanchored form would have made a per-application policy decision implicitly, contradicting the proposal's explicit scope boundary.
- The anchor is the minimum change that achieves the policy intent without over-reaching.

**Rejected alternatives (carry-forward from `-003`):**

- Commit with scan evidence; delete after evaluation; selective ignore (`intermediate/` only).

**Ignore-policy edit (the exact line added to `.gitignore`):**

```text
/.understand-anything/
```

Placement: alongside the existing `.gtkb-state/` entry to keep evaluation-tier ignores grouped. (The pre-existing `.gtkb-state/` entry remains unanchored for back-compat; replacing it is OUT of Slice 1 scope. This proposal adds only the new anchored entry.)

**Note on append-only audit trail:** the proposed `.gitignore` edit is additive (one line added). No existing entry is removed or rewritten.

## Specification Links

(Carry-forward from `-003`; unchanged.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol; NEW/REVISED/GO/implement/post-impl/VERIFIED flow with `bridge/INDEX.md` canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every relevant governing spec cited in this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — `Project Authorization`, `Project`, `Work Item` metadata block at header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan maps the closures of NO-GO -002 (F1+F2) and NO-GO -004 (P1) to concrete tests below.
- `GOV-STANDING-BACKLOG-001` — `WI-4280` is the durable backlog record; `TEST-11138` linked in `PHASE-015`.
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` — the 5 candidate specifications remain surfaced in `DELIB-20260632`; this REVISED-2 does NOT formally promote any.
- `GOV-ARTIFACT-APPROVAL-001` — `DELIB-20260632` approval packet on disk.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-...-WI-4280` is the bounded envelope; status active; covers `WI-4280`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — PAUTH envelope satisfies the constraint.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH does not bypass bridge review; this REVISED-2 is the explicit demonstration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the platform-root install (AUQ-5 = A) is NOT inside `applications/<name>/`. The anchored gitignore line `/.understand-anything/` explicitly preserves this scope boundary by NOT affecting `applications/<name>/.understand-anything/` paths.

**Advisory citations** (carry-forward from `-003`):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Prior Deliberations

(Carry-forward from `-003`; unchanged.)

- `DELIB-20260632` (S386 2026-06-03, owner_conversation, owner_decision) — Owner AUQ Envelope: Understand-Anything Evaluation Initiation (10 Decisions).
- `DELIB-S324-OM-DELTA-0001-CHOICE` — Loyal Opposition authority over cited requirements.
- `DELIB-S324-OM-DELTA-0003-CHOICE` — operating-model terminology baseline.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-28-16-03-UNDERSTAND-ANYTHING-EVALUATION.md` — prior LO evaluation warning (cited as the rationale anchor for the §"Platform-Root ... Handling Policy" choice).

## Owner Decisions / Input

This REVISED-2 depends on owner approval; per `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel, the authorizing AskUserQuestion evidence is the foundational `DELIB-20260632` envelope (carried forward from `-001`/`-003`).

**Foundational owner-decision DELIB (carry-forward):** `DELIB-20260632` (10 AUQ answers from S386 2026-06-03; approval packet sha256 `348f64572e9b2c03cfb62e6581b5052f80b7b0144fd674c20c45a52957a10e28`).

**No new owner AUQ is required by this REVISED-2.** Codex confirmed verbatim in `-004`: "No new owner decision appears necessary for this narrow correction." The fix is mechanical (one character added to one gitignore line, plus a tightened verification check).

**Owner Action Required:** None.

## Requirement Sufficiency

**Existing requirements sufficient.**

Carry-forward: the project scope envelope at `PROJECT-GTKB-UNDERSTAND-ANYTHING-EVALUATION` v1 + the PAUTH envelope are sufficient owner authorization for the bounded Slice 1 work. The `.gitignore` config_change is within PAUTH-allowed mutation classes. No new or revised formal specification is required.

## Spec-Derived Verification Plan (extended; T-F1 tightened)

This section retains the full verification plan from `-003` with one targeted change: T-F1 is rewritten to check for the exact anchored gitignore entry, not substring presence (closes NO-GO `-004` P1). The mapping satisfies `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` for the proposal-time gate. All commands run from the GT-KB workspace root (`E:\GT-KB`) and are Windows/PowerShell-compatible.

**Bridge protocol & mandatory preflights (carry-forward):**

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `preflight_passed: true`, `missing_required_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install
```
Expected: `Blocking gaps: 0`.

**T-F1 (NEW — tightened from `-003` per NO-GO -004 P1) — `.gitignore` contains the exact root-anchored entry `/.understand-anything/`:**

```text
python -c "from pathlib import Path; lines = [l.rstrip() for l in Path('.gitignore').read_text(encoding='utf-8').splitlines()]; print('has-anchored-entry:', '/.understand-anything/' in lines); print('has-unanchored-entry (must be False):', '.understand-anything/' in lines)"
```
Expected: `has-anchored-entry: True`, `has-unanchored-entry (must be False): False`. The second clause guards against accidentally landing the unanchored form Codex NO-GO'd.

**T-F1b (cross-scope behavior check — confirms anchored pattern does NOT match nested):**

```text
git check-ignore -v --no-index .understand-anything/sentinel.txt applications/example/.understand-anything/sentinel.txt
```
Expected: `.gitignore:<line>:/.understand-anything/	.understand-anything/sentinel.txt` is reported as ignored; `applications/example/.understand-anything/sentinel.txt` is NOT reported (exit code 1 from git check-ignore for the unmatched path). This directly tests Codex's cited concern: the anchored entry must match only at platform root.

**T-F2 (carry-forward from `-003`; unchanged) — No `.understand-anything/` path is git-tracked after Slice 1:**

```text
git ls-files .understand-anything/
```
Expected: empty output. Verifies the `ignored` policy held: the `/understand` invocation under test criterion (a) produced no repo-tracked artifact under the platform-root tree.

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

(a) **UA Claude Code plugin responsive to `/understand`.**

(b) **Candidate exclude list file present and matches AUQ-4 verbatim.**

```text
python -c "from pathlib import Path; p = Path('.gtkb-state/ua-evaluation/excludes-candidate.toml'); print('exists:', p.exists()); print(p.read_text(encoding='utf-8')) if p.exists() else None"
```
Expected: file exists; content includes the AUQ-4 list verbatim.

(c) **PB pre-validation results documented.**

(d) **INSIGHTS-2026-06-03-UA-EVALUATION.md scaffolded.**

```text
python -c "from pathlib import Path; p = Path('independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-UA-EVALUATION.md'); print('exists:', p.exists()); t = p.read_text(encoding='utf-8') if p.exists() else ''; print('has owner-tasks heading:', '## Owner Navigation Tasks' in t); print('has verdict heading:', '## Owner Verdict' in t); print('cites DELIB:', 'DELIB-20260632' in t)"
```
Expected: all booleans `True`.

**Phantom-spec sweep (carry-forward; spec set unchanged):**

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
Expected: `missing: []`.

## Risk / Rollback

(Carry-forward from `-003`; one risk note added re: anchored vs unanchored.)

**Risks:**

1. **UA plugin install failure.** Mitigation: observable immediately; no repo corruption.
2. **UA generates large `.understand-anything/intermediate/` files.** Mitigation: platform-root `/.understand-anything/` tree gitignored per §"Platform-Root ... Handling Policy".
3. **LLM-API costs.** Mitigation: pre-validation bounded to one structural + one semantic query.
4. **Candidate exclude list false-positives / false-negatives.** Mitigation: pre-validation measures both.
5. **Owner navigation tasks reveal Slice 1 exclude list is wrong.** Mitigation: candidate specs not formally promoted; revision cheap.
6. **Graph artifact disclosure risk if ignore policy is bypassed.** Mitigation: T-F2 verification command confirms zero tracked paths.
7. **NEW (from NO-GO -004) — Cross-scope leakage if gitignore line is unanchored.** Mitigation: T-F1 and T-F1b verify the exact anchored entry is present AND check that nested application paths are NOT matched.

**Rollback (unchanged):** single-commit revert; `Remove-Item -Recurse -Force .understand-anything\, .gtkb-state\ua-evaluation\` for residual state.

The `kb_mutation_in_scope: false` header above guarantees that this Slice 1 proposal does NOT add new GT-KB-managed specifications, work items, or deliberations beyond the four already created this session.

## Bridge Filing (INDEX-Canonical)

This REVISED-2 is filed under `bridge/` as `bridge/gtkb-understand-anything-evaluation-install-005.md`. A `REVISED: bridge/gtkb-understand-anything-evaluation-install-005.md` line is prepended to the existing `gtkb-understand-anything-evaluation-install` document entry in `bridge/INDEX.md` (append-only; no prior version deleted or rewritten). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

Pre-file claim: `python scripts/bridge_claim_cli.py claim gtkb-understand-anything-evaluation-install` executed 2026-06-03 22:10:38Z; held by current session `06e40a38-aa06-4832-b896-24665506a321`; TTL 22:20:38Z; exit 0.

## Recommended Commit Type

`docs:` — unchanged from `-001`/`-003`. The dominant repo-tracked Slice 1 deliverable is the INSIGHTS evaluation report. The `.gitignore` edit is a one-line config_change supporting the evaluation.

## Self-Check (Pre-Filing)

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, this REVISED-2 is self-checked against the operative-file applicability and clause preflights. Codex MUST rerun both `scripts/bridge_applicability_preflight.py --bridge-id gtkb-understand-anything-evaluation-install` and `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-understand-anything-evaluation-install` against this operative file (`-005`).

Local pre-file confirmation (2026-06-03 ~22:11Z this session): no `.understand-anything/` line yet exists in `.gitignore` (confirmed by `git check-ignore -v --no-index .understand-anything/sentinel.txt applications/example/.understand-anything/sentinel.txt` returning "not yet in .gitignore - expected pre-impl"). The implementation phase will add the anchored line; T-F1 and T-F1b verify the correct form.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
