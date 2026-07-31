# GOV-FILE-BRIDGE-AUTHORITY-001 — File Bridge Authority Spec

**Spec ID:** GOV-FILE-BRIDGE-AUTHORITY-001  
**Spec Kind:** GOV (Cross-cutting Governance Specification)  
**Severity:** blocking  
**Status:** active  
**Created:** 2026-06-08  
**Author:** Prime Builder (goose/pb), session S509  
**Formalization of:** `.claude/rules/file-bridge-protocol.md` (normative body)  
**Registered by:** `config/governance/spec-applicability.toml` (blocking severity rule)

---

## Authority Chain

The file bridge between Prime Builder (PB) and Loyal Opposition (LO) is governed
by `E:\\GT-KB\\.claude\\rules\\file-bridge-protocol.md` (hereafter "the protocol").
This specification extracts, structures, and cites the governing clauses of the
protocol for mechanical enforcement and downstream proposal linkability.

The protocol itself is the authoritative source; this spec is a **citation surface**
that downstream proposals MAY reference in their Specification Links section
instead of re-extracting clauses from the protocol.

## Clauses

### C-001 Root Boundary

All bridge proposals, reviews, implementation reports, and verifications must
comply with `.claude/rules/project-root-boundary.md`: all active GT-KB files
and artifacts must remain within `E:\\GT-KB`; all GT-KB application files
must remain within `E:\\GT-KB\\applications\`. No exceptions. A bridge item that
depends on a live path outside those roots is NO-GO. Source: protocol §1
"Directory" and §2 "Mandatory Root Boundary Gate".

### C-002 Mandatory Specification Linkage Gate

Every implementation proposal must include a `Specification Links` section
citing every relevant governing specification. A proposal with no linked
specification surface is NO-GO. Source: protocol §3 "Mandatory Specification
Linkage Gate" + `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.

### C-003 Mandatory Implementation-Start Authorization Metadata

Implementation proposals that request source, test, script, hook,
configuration, deployment, repository-state, or KB-mutation work must include:
(a) `target_paths` metadata, (b) a `Requirement Sufficiency` subsection with
exactly one operative state, (c) a specification-derived verification plan.
Source: protocol §4 "Mandatory Implementation-Start Authorization Metadata".

### C-004 Mandatory Pre-Filing Preflight

Prime Builder MUST run `python scripts/bridge_applicability_preflight.py` on the
operative file (or manual grep against `config/governance/spec-applicability.toml`
if INDEX entry is absent) and record any `missing_*_specs` as self-detected
defects before INDEX update. Source: protocol §5 "Mandatory Pre-Filing
Preflight Subsection".

### C-005 Mandatory Pre-Drafting Claim Step

Prime MUST acquire a work-intent claim via `scripts/bridge_claim_cli.py claim <slug>`
before substantive drafting. Exit code 0 authorizes drafting; exit code 2
requires holder-resolution or owner escalation. The bridge-compliance-gate
hook enforces this at Write time. Source: protocol §6 "Mandatory Pre-Drafting
Claim Step" + `.claude/hooks/bridge-compliance-gate.py`.

### C-006 Mandatory Specification-Derived Verification Gate

An implementation cannot receive VERIFIED unless tests derived from the linked
specifications are executed against the implementation. Source: protocol §7
"Mandatory Specification-Derived Verification Gate" +
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

### C-007 Pre-File Code-Quality Gates (Lint AND Format - Separate)

Post-implementation reports with Python files MUST run both `ruff check` and
`ruff format --check` on changed files and report results. These are separate
gates. Source: protocol §7.1 "Pre-File Code-Quality Gates".

### C-008 Mandatory Applicability Preflight Gate (LO Side)

Before LO issues GO or VERIFIED, LO must run the mechanical preflight and
include the `Applicability Preflight` section in the verdict file. Missing
required specs = NO-GO unless proposal revised. Source: protocol §8
"Mandatory Applicability Preflight Gate".

### C-009 Clause-Test Preflight (Advisory; Slice 1)

The companion `scripts/adr_dcl_clause_preflight.py` is advisory only in
Slice 1 — exits 0 even when blocking clauses lack evidence. Slice 2 of
`gtkb-adr-dcl-clause-test-enforcement` will promote selected clauses to a
hard gate. Source: protocol §9 "Clause-Test Preflight".

### C-010 Status Tokens and Body Status-Token Rule

Bridge files MUST begin with a canonical status token on the first non-blank
line. `WITHDRAWN` remains accepted. The body-status-token rule is mechanically
enforced by `.claude/hooks/bridge-compliance-gate.py`. Source: protocol §10
"Statuses" + §10a "Body Status-Token Rule".

### C-011 ADVISORY Semantics

ADVISORY is first-class workflow state — not a transport workaround via
`NO-GO@001`. Entries are Axis-2 (non-dispatchable). LO authors; Prime
acknowledges and dispositions (converts, defers, or rejects). Source: protocol
§11 "Advisory Reports".

### C-012 DEFERRED Semantics

DEFERRED is owner-only bridge parking state. Indexed via both INDEX line and
versioned file. Requires owner decision evidence, deferral reason, and
clear/resume condition. Non-actionable until cleared by owner. Source: protocol
§12 "DEFERRED Status".

### C-013 Never-Delete Rule

Bridge files are the audit trail and must NEVER be deleted. Source: protocol
§13 "Guardrails".

### C-014 Owner Decisions / Input Section Gate

Impl proposals depending on owner approval MUST include non-empty `Owner
Decisions / Input` section with AskUserQuestion evidence. Hook-enforced at
Write time. Source: protocol §14 "Mandatory Owner Decisions / Input Section
Gate".

### C-015 Conventional Commits Type Discipline

Implementation reports MUST include recommended Conventional Commits type in a
`Recommended Commit Type` section, justified against the diff stat. Source:
protocol §15 "Conventional Commits Type Discipline".

### C-016 Parked-Draft Pattern

Bridge files MAY commit without INDEX entry when tagged as parked drafts.
Applicability preflight returns `ERR_NO_INDEX_ENTRY` for these (expected,
not defect). Promotion requires explicit INDEX entry and tagged commit.
Source: protocol §16 "Parked-Draft Pattern".

---

## Applicability

Registered as blocking severity in `config/governance/spec-applicability.toml`:

- `applies_when_doc_matches = ["*"]` (applies to ALL bridge documents by default)
- `applies_when_paths_match = ["bridge/**", ".claude/rules/file-bridge-protocol.md", ".claude/rules/codex-review-gate.md"]`

---

## Enforcement Surfaces

| Mechanism | What it enforces |
|-----------|------------------|
| `.claude/hooks/bridge-compliance-gate.py` | Body status-token rule, owner-decisions gate |
| `scripts/bridge_applicability_preflight.py` | Spec linkage completeness |
| `scripts/bridge_claim_cli.py` | Single-drafter claim enforcement |
| `scripts/adr_dcl_clause_preflight.py` | Clause-applicability (advisory only in S1) |
| `.githooks/pre-commit` (ruff-format guardrail) | Commit-time format gate |
| Loyal Opposition verdict | NO-GO when preflight fails |

---

## Prior Deliberations

- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — GOV proposal standards slice 1
- `DELIB-S333` (audit finding P0-001, commit `cd8f27ce`) — governance hygiene bundle rationale
- `DELIB-S324-OM-DELTA-0001-CHOICE` (per OS contract) — owner's authority over cited requirements; LO may question them
- Bridge thread `bridge/gtkb-gov-proposal-standards-slice1-025.md` (GO) — body-status-token rule source

---

## Relationship to Umbrella Remediation

This spec was formalized during Option W umbrella remediation
(`bridge/gtkb-v1-s509-proposal-remediation-001.md`) to close the
`GOV-FILE-BRIDGE-AUTHORITY-001` citation gap that blocked B1–B5 NO-GO
preflight passes. Downstream proposals in the bundle (B1 observability hygiene,
B3 workstream marker race, B4 MCP stable surface) MUST cite this spec in their
Specification Links section per the umbrella template.

---

## Amendment Procedure

Amendments to this spec require:
1. A REVISED bridge entry (`bridge/gtkb-gov-file-bridge-authority-001-NNN.md`)
2. LO review with GO verdict
3. Corresponding update to `config/governance/spec-applicability.toml` rule
4. Corresponding propagation to `.claude/rules/file-bridge-protocol.md` if the
   underlying clauses change materially
