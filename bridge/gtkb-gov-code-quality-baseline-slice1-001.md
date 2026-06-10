NEW

# GTKB-GOV-CODE-QUALITY-BASELINE Slice 1 — Governance Design

**Status:** NEW (governance/design scoping; NOT an implementation proposal)
**Date:** 2026-04-25
**Work item:** GTKB-GOV-CODE-QUALITY-BASELINE (proposed; new standing backlog
entry filed in same change set as this proposal)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** governance_scoping_proposal
**Routing:** Upstream to `groundtruth-kb` per the GTKB-GOV-PROPOSAL-STANDARDS
pattern (see `bridge/gtkb-gov-proposal-standards-slice1-020.md` GO at S306).
Agent Red adopts via `gt project upgrade` after upstream VERIFIED.

bridge_kind: prime_proposal
work_item_ids: [GTKB-GOV-CODE-QUALITY-BASELINE]
spec_ids: []
target_project: gt-kb (upstream)
implementation_scope: governance
requires_review: true
requires_verification: true

---

## 0. What This Proposal Is And Is Not

This proposal scopes a new GT-KB governance subsystem: a default
**Code Quality Baseline** that applies to every implementation
proposal in every GT-KB adopter project. The baseline is enforced
both at proposal time (Prime must include a Code Quality Baseline
table) and at review time (Loyal Opposition must evaluate it).

This proposal is **governance-design only**. It does NOT:

- Implement the proposal-standards hook extension that would
  mechanically enforce the table.
- Mutate any formal artifact (no GOV/ADR/SPEC/DCL records are
  inserted by this proposal — the proposal *defines* what those
  records will be when implementation lands).
- Modify any source code, test, schema, or workflow.
- Bind any specific adopter project to immediate compliance.

A separate implementation bridge (Slice 2, scoped after this Slice 1
GO) lands the hook, the verifier, the tests, and the formal artifact
records.

## 1. Prior Deliberations

- **GTKB-GOV-PROPOSAL-STANDARDS Slice 1** GO at
  `bridge/gtkb-gov-proposal-standards-slice1-020.md` established the
  upstream-routed proposal-standards pattern this proposal extends.
- **`hook.bridge-proposal-standards`** (in upstream `groundtruth-kb`)
  is the canonical enforcement hook this proposal augments.
- **`scripts/check_codex_hook_parity.py`** is the established Windows
  fallback verifier this proposal extends for Codex parity.
- **GTKB-GOV-DA-ENFORCEMENT** (`bridge/gtkb-gov-da-enforcement-slice1-010.md`
  VERIFIED) established the upstream-routing convention for governance
  hooks that span Prime+LO interaction.
- No prior bridge thread exists for code-quality baseline as a
  cross-cutting governance artifact; this is the first.
- The S307 owner directive `feedback_no_hardcoded_paths.md` and the
  S307 `feedback_pedagogical_comments_standard.md` are precedent
  for owner-directed code-quality rules being formalized into
  governance — this proposal generalizes that pattern.

## 2. Proposed Standing Backlog Item

**`GTKB-GOV-CODE-QUALITY-BASELINE`** added to `memory/work_list.md`
in the same change set as this proposal. Initial status: scoping in
flight at this bridge thread; awaits Codex GO before any
implementation work begins.

Stake: GT-KB-side (upstream); Agent Red is an early-adopter
beneficiary, not the owner of the baseline definition.

## 3. Formal Artifacts To Define

The implementation bridge (Slice 2, post-GO) will create these
records under the established formal-artifact-approval-gate
discipline:

### 3.1 `GOV-CODE-QUALITY-BASELINE-001`

**Type:** governance (KB `type='governance'`).

**Core rule:** Every implementation proposal in every GT-KB adopter
project carries an explicit Code Quality Baseline table. Each rule in
the baseline applies by default unless explicitly marked N/A with a
concrete reason or explicitly suspended by the owner under the waiver
lifecycle.

**Scope:** Cross-cutting; binds Prime Builder proposal authoring,
Loyal Opposition review, and the bridge-proposal-standards
enforcement hook.

### 3.2 `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`

**Type:** spec with `type='architecture_decision'`.

**Decision:** Code-quality rules are universal-default rather than
opt-in per-proposal. Rationale: opt-in produces inconsistent coverage
across adopter projects and across proposal authors; default-on with
explicit suspension produces auditable per-rule waivers and a
durable record of accepted technical debt.

**Failed approaches:** opt-in checklists (rejected — per-proposal
inconsistency); compile-time enforcement only (rejected — many
quality rules are reviewer-judgment, not mechanically checkable);
post-implementation audit (rejected — late detection costs
proportional to time-to-discover).

**Rejected alternatives:** language-specific style enforcement only
(rejected — quality is cross-cutting and includes architectural,
security, and operational surfaces beyond style); third-party SaaS
linter (rejected — adds dependency, doesn't cover the
governance-aligned categories); CI-only enforcement (rejected — too
late in the loop, doesn't shape proposal authoring).

**Consequences:** every proposal grows by the size of one
small-to-medium table; reviewer cycle includes table evaluation;
new authors learn the baseline through proposal-template exposure.

### 3.3 `SPEC-CODE-QUALITY-CHECKLIST-001`

**Type:** spec with `type='specification'`.

**Required behavior:** the baseline checklist exists as a versioned
list of rule IDs with descriptions, severity, and applicability
guidance. Adopter projects MUST consume the canonical version from
GT-KB; they MAY NOT redefine rule IDs locally. Adopters MAY add
project-specific rules (different ID prefix) but those are out of
scope for this baseline spec.

**Initial rule set:** §4 below.

### 3.4 `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`

**Type:** spec with `type='design_constraint'`.

**Constraint:** Each per-rule suspension carries the six fields per
§5 below (rule ID, scope, reason, owner-approval evidence,
expiry/review condition, compensating control or accepted risk).
Suspensions without all six fields are mechanically rejected by the
hook and are NO-GO for Loyal Opposition review.

**Assertions field** (machine-checkable): waiver records can be
audited against the six-field shape; expired waivers can be queried
and reported.

## 4. Baseline Checklist (Stable Rule IDs)

| Rule ID | Title | Default applicability |
|---|---|---|
| `CQ-SECRETS-001` | No hardcoded secrets, tenant IDs, deploy-specific values, or environment-specific config | All proposals |
| `CQ-PATHS-001` | No machine-specific absolute paths in source/config (use env vars, relative paths, or discovered roots) | All proposals touching files/scripts |
| `CQ-CONSTANTS-001` | Domain-stable named constants are acceptable; document the why for non-obvious values | All proposals introducing literal values |
| `CQ-DOCS-001` | Comments/docstrings explain intent, invariants, public API behavior, or non-obvious logic; avoid noisy "what the code does" comments | All proposals adding/modifying code |
| `CQ-COMPLEXITY-001` | No god classes/modules/functions; large objects require explicit decomposition rationale | All proposals adding/modifying classes, modules, or functions over a complexity threshold |
| `CQ-TESTS-001` | New behavior requires behavioral tests proportional to risk (risk = blast radius × reversibility × affected users) | All proposals adding new behavior |
| `CQ-LOGGING-001` | Errors and logging must be actionable; must not leak secrets, tokens, or PII; must include enough context for diagnosis | All proposals adding/modifying error/logging surfaces |
| `CQ-SECURITY-001` | Security-relevant changes consider OWASP/CERT-style controls explicitly (input validation, authn/authz, injection, supply chain) | All proposals touching auth, input handling, deserialization, secrets management, or external interfaces |
| `CQ-VERIFICATION-001` | Config, filesystem, network, auth, persistence, and deployment surfaces require explicit verification (test or evidence) — not just "should work" claims | All proposals touching those surfaces |

**Naming convention:** `CQ-<TOPIC>-NNN`. Topic prefixes are
controlled by the canonical SPEC; adopters cannot mint new prefixes.
Numbers are monotonic per topic; existing IDs are append-only (per
KB versioning convention).

**Applicability guidance:** "All proposals" means every
implementation proposal must have a Code Quality Baseline table
including this rule, even if marked N/A. The N/A reason makes the
non-applicability auditable.

**Severity:** all rules are advisory-with-NO-GO for Slice 1. A future
slice may introduce hard-blocking rules with mechanical compile/test
gates; that's out of scope here.

## 5. Default Applicability + Per-Rule Suspension

**Default rule:** every checklist item from §4 applies to every
implementation proposal unless one of:

1. **Item is N/A:** Prime marks the rule as N/A with a concrete reason
   in the proposal table (e.g., "CQ-SECURITY-001 N/A: documentation-
   only change, no auth/input/deserialization surfaces touched").
   Codex review may challenge the N/A claim and demand re-marking.

2. **Owner suspension:** the owner has explicitly suspended that
   specific rule for that specific scope via the waiver lifecycle
   below.

**Default applicability is per-rule, not per-proposal.** Marking one
rule N/A does not affect the others.

### 5.1 Waiver/Suspension Lifecycle

Every per-rule suspension MUST include all six fields:

| Field | Purpose |
|---|---|
| `rule_id` | Which rule is suspended (e.g., `CQ-PATHS-001`) |
| `scope` | What the suspension covers (project, module, proposal-thread, single-PR) |
| `reason` | Why the suspension is necessary (concrete, not "developer convenience") |
| `owner_approval_evidence` | Reference to the owner-decision record (DELIB-ID, AskUserQuestion answer, or signed approval packet) |
| `expiry_or_review_condition` | When the suspension is revisited (calendar date OR triggering event OR "permanent with annual review") |
| `compensating_control_or_accepted_risk` | What replaces the rule's protection (alternative test, manual audit, accepted risk statement) |

**Storage:** waiver records live in the KB under
`type='governance_waiver'` (new sub-type to add in Slice 2). Each
waiver insert is gated by the formal-artifact-approval-gate hook.

**Expiry handling:** when a waiver's `expiry_or_review_condition`
fires (date passes, event occurs), the hook flags any new proposal
relying on that waiver and demands either renewal or compliance.

**Audit:** `db.list_specs(type='governance_waiver', active=True)`
produces the live suspension inventory; reportable for governance
review.

## 6. Proposal Enforcement (Required Section In Implementation Proposals)

Every implementation proposal in any GT-KB adopter project MUST
include this section:

```markdown
## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---:|---|---|---|
| CQ-SECRETS-001 | Yes | (how the proposal complies) | (test or evidence reference) | n/a |
| CQ-PATHS-001 | Yes | ... | ... | n/a |
| CQ-CONSTANTS-001 | Yes | ... | ... | n/a |
| CQ-DOCS-001 | Yes | ... | ... | n/a |
| CQ-COMPLEXITY-001 | Yes | ... | ... | n/a |
| CQ-TESTS-001 | Yes | ... | ... | n/a |
| CQ-LOGGING-001 | N/A | n/a | n/a | No error/logging surfaces touched |
| CQ-SECURITY-001 | Yes | ... | ... | n/a |
| CQ-VERIFICATION-001 | Yes | ... | ... | n/a |
```

**Enforcement criteria** (Loyal Opposition NO-GO if any of these
fail):

- Table missing entirely.
- Any row uses a `Rule ID` that doesn't exist in the canonical SPEC
  (per §3.3).
- Any row marked N/A without a concrete reason that survives review
  scrutiny.
- Any row marked Yes without a `Compliance plan` or `Verification`
  cell.
- Any row referencing a waiver that has expired or doesn't match the
  six-field shape (§5.1).
- Vague compliance language ("we will be careful", "best effort")
  that doesn't reference concrete code, tests, or evidence.

## 7. Review Enforcement

Loyal Opposition reviews MUST evaluate the Code Quality Baseline
table for every implementation proposal. The review template gains a
new section:

```markdown
## Code Quality Baseline Review

For each rule marked Yes:
- Confirm Compliance plan is concrete (cites code/tests/evidence).
- Confirm Verification is real (not "TBD").

For each rule marked N/A:
- Confirm reason is concrete and review-survivable.
- Challenge any N/A that looks like avoidance.

For each waivered rule:
- Confirm waiver record exists in KB with all six fields.
- Confirm expiry/review condition is not stale.
- Confirm compensating control is in place.

Cite any baseline violation as:
- GO condition (small fix; allow GO with the condition tracked)
- NO-GO finding (substantial defect; require revision)
- Explicit accepted waiver (referenced waiver record in KB)
```

Reviews that omit this section are themselves NO-GO targets in a
future audit pass. (Self-enforcement: applies to LO reviews of LO
review templates as well.)

## 8. Mechanical Enforcement

### 8.1 Hook extension

Extend the upstream `hook.bridge-proposal-standards` (currently in
`groundtruth-kb` per `bridge/gtkb-gov-proposal-standards-slice1-020.md`)
to additionally check for:

- Presence of the `## Code Quality Baseline` section.
- Presence of the table with all 9 canonical rule IDs (or future
  additions).
- Per-row well-formedness (Applies?, Compliance plan, Verification,
  Waiver/N/A cells).
- Rule IDs match canonical SPEC.
- N/A rows have a non-empty reason.
- Yes rows have non-empty Compliance plan + Verification.
- Any Waiver reference resolves to a live (non-expired) waiver
  record in KB.

Hook fires on `PreToolUse` for any Write to `bridge/*.md`. Failures
produce a `systemMessage` rejecting the write until the table
complies.

### 8.2 Fallback verifier (Codex/Windows)

Codex hooks remain disabled on Windows per
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Add a Windows-aware verifier
along the established `scripts/check_codex_hook_parity.py` pattern:

`scripts/check_code_quality_baseline_parity.py` — runs in the
release-candidate gate; statically analyzes every `bridge/*.md` file
filed since the last release tag; reports any proposal missing the
table or carrying a malformed entry.

This ensures parity even when the hook isn't live on Windows.

### 8.3 Tests

The Slice 2 implementation bridge will land tests covering:

| Test case | Asserts |
|---|---|
| Missing table | Hook rejects; verifier flags |
| Invalid rule ID | Hook rejects; verifier flags |
| N/A without reason | Hook rejects; verifier flags |
| Yes without Compliance plan or Verification | Hook rejects; verifier flags |
| Waiver expired | Hook rejects; verifier flags |
| Compliant proposal | Hook accepts; verifier silent |

### 8.4 Routing (per Codex pattern)

This is upstream-routed work:

- Slice 1 (this proposal): governance design only; lands in
  `groundtruth-kb/bridge/` as a design record. Agent Red side is
  this Slice 1 bridge file (which is a design record, not the
  upstream artifact itself).
- Slice 2 (future implementation): hook + verifier + tests + KB
  records, all in `groundtruth-kb`. Agent Red adopts via
  `gt project upgrade` after upstream VERIFIED.
- Adopter projects (Agent Red etc.) adopt the baseline as part of
  their next `gt project upgrade` cycle.

## 9. Source Grounding (Informing References)

These external standards inform the baseline but do NOT directly
define it. The canonical SPEC owns the rule definitions; external
references are advisory:

- **ISO/IEC 25010** — quality model categories (functional
  suitability, performance efficiency, compatibility, usability,
  reliability, security, maintainability, portability) inform the
  topic split in §4.
- **OWASP Secure Coding Practices** — informs `CQ-SECURITY-001`
  category list (input validation, output encoding, authentication,
  session management, access control, cryptography, error handling,
  data protection, communication, system configuration, database
  security, file management, memory management, general practices).
- **SEI CERT Coding Standards** — informs language-specific secure
  coding rules where applicable (C, C++, Java, Perl); not a primary
  driver because most GT-KB adopter code is Python and JS/TS.
- **Twelve-Factor App** — informs `CQ-PATHS-001`,
  `CQ-CONSTANTS-001`, `CQ-SECRETS-001` (config separation; environment
  parity).
- **Google Python Style Guide** — informs `CQ-DOCS-001` and
  `CQ-COMPLEXITY-001` for Python-specific style and complexity
  thresholds.

When external standards conflict, the canonical SPEC wins. When
external standards are silent, the canonical SPEC is the only
authority.

## 10. Out Of Scope For This Slice 1

- Implementing the hook extension (Slice 2).
- Implementing the fallback verifier (Slice 2).
- Writing the tests (Slice 2).
- Inserting the GOV/ADR/SPEC/DCL records into KB (Slice 2; gated by
  formal-artifact-approval-gate).
- Defining hard-blocking rules with compile-time enforcement (future
  slice).
- Adopter-side waiver UI / dashboard (future slice).
- Backfilling the Code Quality Baseline table into existing in-flight
  bridge proposals (out of scope; only applies prospectively).
- Publishing the canonical SPEC content to public-facing
  documentation (separate doc-publishing track).

## 11. Codex Review Asks

Per the user's required asks:

1. **Artifact split:** Confirm the GOV/ADR/SPEC/DCL split in §3 is
   correct (governance authority + architecture decision + behavior
   spec + machine-checkable design constraint), or recommend a
   different breakdown.
2. **Checklist specificity:** Confirm the 9 rules in §4 are specific
   enough to be enforceable in proposal review without devolving into
   reviewer judgment-call disputes. Identify any rule that needs
   sharper criteria.
3. **Default applicability + per-rule suspension:** Confirm that
   "default-on with explicit suspension" is the right model, or
   recommend an alternative (e.g., per-project profiles, severity
   tiers).
4. **Proposal/review enforcement:** Confirm the §6 table format and
   §7 review template extension are sufficient to make the baseline
   actually felt at proposal authoring + review time, not just
   nominally referenced.
5. **Upstream managed-artifact routing:** Confirm Slice 2 routing to
   `groundtruth-kb` (hook + verifier + tests + KB records) matches
   the GTKB-GOV-PROPOSAL-STANDARDS / hook.bridge-proposal-standards
   convention.
6. **GO / NO-GO** on this Slice 1 governance design proposal. On GO,
   Prime files Slice 2 implementation bridge upstream in
   `groundtruth-kb` (with the appropriate AskUserQuestion for any
   owner approvals the formal-artifact insertion requires).

## 12. Decision Needed From Owner

None for this Slice 1 governance scoping proposal. Slice 2
implementation will require owner formal-artifact approvals (per the
`PB-ARTIFACT-APPROVAL-001` strict default) when the GOV/ADR/SPEC/DCL
records are inserted.

---

**Status request:** GO

**Files in this proposal:** this file only.

**work_list update in same change set:** new standing backlog entry
for `GTKB-GOV-CODE-QUALITY-BASELINE` added.

**Implementation NOT yet authorized.** Slice 2 implementation
proposal will follow on Codex GO, with appropriate
formal-artifact-approval ceremony for any KB record insertions.
