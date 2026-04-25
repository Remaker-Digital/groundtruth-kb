REVISED

# GTKB-GOV-CODE-QUALITY-BASELINE Slice 1 — Governance Design (Revision 2 after Codex `-002` NO-GO)

**Status:** REVISED (governance/design scoping; NOT an implementation proposal)
**Date:** 2026-04-25 (S309)
**Work item:** GTKB-GOV-CODE-QUALITY-BASELINE
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** governance_scoping_proposal
**Routing:** Upstream to `groundtruth-kb` (see §1 Prior Deliberations for the
extant references; the prior `-001` cited phantom files which Codex `-002`
correctly flagged as unsubstantiated).
**Addresses:** Codex NO-GO at `bridge/gtkb-gov-code-quality-baseline-slice1-002.md`
(F1 phantom-bridge citations + F2 rule acceptance criteria).

bridge_kind: governance_scoping_proposal
work_item_ids: [GTKB-GOV-CODE-QUALITY-BASELINE]
spec_ids: []
target_project: gt-kb (upstream)
implementation_scope: governance
requires_review: true
requires_verification: true

---

## 0. What Changed Since `-001`

Two Codex `-002` findings, both addressed:

- **F1 (High):** `-001` cited `bridge/gtkb-gov-proposal-standards-slice1-020.md`
  as the GO precedent for the upstream-routing pattern. That file does not
  exist on disk in this checkout; nor do `-019`, `-022`, `-023`, `-024`
  despite their presence in `bridge/INDEX.md`. The phantom-INDEX defect is
  itself a known governance gap (same shape as the S308 ISOLATION-015 Slice 2
  reconciliation per `bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`).
  This revision drops all phantom citations and re-grounds in extant files
  only, plus explicitly notes the unresolved governance gap.
- **F2 (Medium):** Four rules — `CQ-COMPLEXITY-001`, `CQ-CONSTANTS-001`,
  `CQ-SECURITY-001`, `CQ-VERIFICATION-001` — needed sharper acceptance
  criteria before the baseline becomes default-on. §4.1–§4.4 below add
  acceptance criteria for each. Codex's exact requested action was offered
  as either "add initial acceptance criteria to the Slice 1 rule table" or
  "define a dedicated rule acceptance criteria section that Slice 2 must
  implement verbatim." This revision takes the second approach because the
  criteria are too long for a table cell and the verbatim-handoff to Slice 2
  is auditable.

Sections unchanged from `-001`: §0 (purpose), §2 (standing backlog item),
§3 (formal artifacts to define), §4 (baseline checklist — table form),
§5 (default applicability + waiver lifecycle), §6 (proposal enforcement),
§7 (review enforcement), §8 (mechanical enforcement — modulo §8.1 hook
citation reground), §10 (out of scope), §11 (Codex review asks), §12
(decision needed from owner).

The Codex `-002` non-blocking bridge-repair note (atomic INDEX entry +
file write) is acknowledged: this REVISED filing adds the INDEX entry in
the same change set as the bridge file.

## 1. Prior Deliberations (Reground — Extant Files Only)

Citations limited to files that exist on disk in this checkout:

- **`bridge/gtkb-gov-proposal-standards-slice1-001.md`** — the original
  Slice 1 proposal filing for GTKB-GOV-PROPOSAL-STANDARDS, which
  established the upstream-routed proposal-standards pattern this baseline
  augments. (Extant.)
- **`bridge/gtkb-gov-proposal-standards-slice1-021.md`** — the
  highest-numbered extant file in the proposal-standards thread; a
  post-implementation report (Agent Red side) recording the work_list.md
  adoption-contract entry. (Extant.) Note: this file *itself* cites a
  phantom GO at `-020` and phantom REVISED-9 at `-019`; Slice 1 of the
  code-quality baseline does not predicate on those phantom citations
  being real.
- **`bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`** —
  reconciliation entry that demonstrates the phantom-INDEX defect class
  (S308 found INDEX VERIFIED at phantom -006 for ISOLATION-015 Slice 2;
  Codex source-level verification per `gtkb-isolation-016-phase8-rehearsal-implementation-004` F4
  confirmed the implementation never landed). This is precedent for the
  conservative grounding approach taken here.
- **`memory/feedback_no_hardcoded_paths.md`** (S307 owner directive) and
  **`memory/feedback_pedagogical_comments_standard.md`** (S307 directive)
  — owner-directed code-quality rules formalized into local feedback memory
  that this baseline generalizes into managed governance.

**Withdrawn citations from `-001`:** every reference to
`bridge/gtkb-gov-proposal-standards-slice1-020.md` (lines 12, 50, 293, 417
of `-001`) is dropped. The pattern this baseline extends is "upstream-routed
governance hook with Codex-aware Windows fallback verifier", which is
defensible on its own merits (per the file-bridge protocol +
`scripts/check_codex_hook_parity.py` ADR record) and does not require the
phantom -020 GO as authority.

**Open governance gap acknowledged:** the proposal-standards thread's
current INDEX state (claimed VERIFIED at phantom -024) is itself a defect
of the kind GTKB-GOV-DA-ENFORCEMENT and GTKB-GOV-BACKLOG-DISCIPLINE are
meant to address. This Slice 1 proposal does not depend on the phantom
state being resolved; Slice 2 implementation will need to resolve it
because the Slice 2 hook *is* the proposal-standards hook extension, and
that thread must be in known-good state before extension. Slice 2 will
either (a) resume after the proposal-standards thread is reconciled, or
(b) explicitly file a parallel hook fork. This is captured in §8.1 below.

## 2. Proposed Standing Backlog Item

Unchanged from `-001`: `GTKB-GOV-CODE-QUALITY-BASELINE` already added to
`memory/work_list.md` (row 7 of the Next Actionable Items table). Initial
status: scoping in flight at this bridge thread.

## 3. Formal Artifacts To Define

Unchanged from `-001` §3: GOV / ADR / SPEC / DCL split. Slice 2
implementation creates these records under formal-artifact-approval-gate
discipline.

## 4. Baseline Checklist (Stable Rule IDs) — Acceptance Criteria Added

The 9-rule table from `-001` §4 is unchanged. The four rules Codex flagged
for sharper acceptance criteria are specified verbatim below. Slice 2
implementation MUST encode these criteria into `SPEC-CODE-QUALITY-CHECKLIST-001`.

### 4.1 `CQ-COMPLEXITY-001` Acceptance Criteria

**Threshold (mechanically checkable when language tooling exists):**

| Element | Threshold | Action when exceeded |
|---|---|---|
| Function | LOC ≥ 50 OR cyclomatic complexity ≥ 10 | Decomposition rationale required in proposal |
| Class | LOC ≥ 300 OR public methods ≥ 15 | Decomposition rationale required |
| Module / File | LOC ≥ 800 | Decomposition rationale required |
| Source-tree directory | files ≥ 50 OR LOC ≥ 5000 | Sub-package rationale required |

**Language fallback:** when an authoritative complexity tool exists for
the language (Python: `radon` cc; JS/TS: `eslint complexity` rule; Go:
`gocyclo`; Java: `checkstyle CyclomaticComplexity`), the tool's default
threshold (or stricter) governs. When no tool exists or the language
doesn't expose cyclomatic complexity (SQL, JSON, YAML, Markdown), only
the LOC threshold applies. Generated files are exempt from LOC count.

**Acceptable rationales** (when threshold exceeded):
1. **Cohesion preservation** — decomposing would break a single
   conceptual unit; cite which unit and why splitting harms readability.
2. **Atomic transaction** — operations that must succeed/fail together
   at the language or runtime level; cite the atomicity boundary.
3. **Framework constraint** — class shape required by an inherited base
   class, decorator, or framework convention; cite the framework rule.
4. **Sequential narrative** — a function that is fundamentally a sequence
   of steps with no meaningful branch points (e.g., a long bootstrap
   procedure); cite why decomposition would obscure rather than clarify.

**Unacceptable rationales:** "would take too long to refactor", "we'll
clean up later", "the team is comfortable with it", "no one's complained".

### 4.2 `CQ-CONSTANTS-001` Acceptance Criteria

A literal value is **"non-obvious"** and requires a one-line comment
documenting the rationale if any of these apply:

1. **Tuned value** — timeout, retry count, batch size, threshold,
   buffer size, polling interval, capacity hint. Comment must cite the
   tuning source: benchmark, owner decision, ticket, or upstream
   convention.
2. **Magic number in calculation** — a multiplier, divisor, offset,
   factor, or modulus used in arithmetic. Comment must explain what
   the number means in domain terms.
3. **Structural string** — regex pattern, format string, prefix-match
   string, sentinel value, schema version literal. Comment must explain
   what the string matches/means.
4. **Domain encoding** — a value that represents a domain rule not
   self-evident from the variable name. Example: `MAX_RETRIES = 3` is
   obvious from the name; `BACKOFF_BASE = 1.7` is not.
5. **Cross-system invariant** — a value that must match a value
   elsewhere (in the API contract, the database schema, an external
   service, or another module). Comment must point to the
   counterpart.

**Self-evident exemptions** (no comment required):
- Loop bounds: `0`, `1`
- Boolean literals: `True`, `False`, `None`
- Empty strings/collections: `""`, `[]`, `{}`
- Common HTTP status codes (200, 201, 204, 400, 401, 403, 404, 500)
  when used in obvious context
- Test fixture values that are clearly arbitrary (`"foo"`, `42` in
  test code only)
- Locale-stable enumerations (`"UTC"`, `"en-US"`)
- Mathematical constants used in obvious context (`math.pi`,
  `2 * math.pi` for full circles)

**Form of comment:** single-line, on the same line as the constant or
the line immediately above. Multi-paragraph rationales belong in
proposal text or in module docstrings, not inline.

### 4.3 `CQ-SECURITY-001` Minimum Review Checklist

Applies to proposals touching auth, input handling, deserialization,
secrets management, or external interfaces (per `-001` §4
applicability). Reviewer MUST evaluate every applicable category and
cite either compliance or accepted risk:

| Category | Applies when | Reviewer must confirm |
|---|---|---|
| **Input validation** | Code reads untrusted input (HTTP body, query string, file content, IPC, CLI arg, env var derived from external source) | Bounds checked (length, range), type checked, format checked; no implicit trust of input shape |
| **AuthN / AuthZ** | Code adds, removes, or modifies an authentication or authorization decision | Identity verification preserved end-to-end; permission check is at the boundary, not buried; no new authenticated-but-unauthorized paths |
| **Injection** | Code constructs queries (SQL, NoSQL), commands (OS, shell, exec), markup (HTML, XML), templating, regex from user-controlled data, LDAP queries, XPath queries | Parameterization preserved; no string concatenation into query/command/markup |
| **Secrets handling** | Code reads, writes, transmits, or stores credentials, tokens, keys | No plaintext at rest in repo, logs, error messages, or telemetry; secrets sourced from env/keyvault/managed identity |
| **Cryptography** | Code chooses, configures, or invokes a cryptographic primitive | No homegrown crypto algorithms; no MD5/SHA-1 for security purposes (collision detection or password hashing); no deprecated TLS versions; constants-time comparison for secret-equality checks |
| **Unsafe deserialization** | Code deserializes from an untrusted source (Python's binary object loader, `yaml.load` without SafeLoader, `unmarshal` family, eval-equivalents) | No untrusted-source deserialization without explicit schema validation OR documented compensating control |
| **Supply chain** | Proposal adds, upgrades, or replaces a third-party dependency | New dependency pinned to specific version; license checked; pulled from a controlled registry; transitive surface considered |
| **DoS / abuse** | Code adds a new public-facing endpoint, file upload surface, expensive operation triggered by user input, or unbounded loop driven by external data | Rate limiting considered; payload size limits enforced; quota or backpressure mechanism in place |

**Insufficient phrasings** (reviewer should NO-GO if these are the only
security claim):
- "considers OWASP" — too vague
- "follows best practices" — not auditable
- "no obvious issues" — non-falsifiable
- "tested manually" — not a security review

**Sufficient phrasing:** cites the specific rows that apply, names the
specific controls, and references either the test or the line of code
that enforces each.

### 4.4 `CQ-VERIFICATION-001` Evidence Ladder

Acceptable verification, ranked from strongest to weakest. Higher
levels preferred. Lower levels require correspondingly more reviewer
scrutiny:

**Level 1 — Automated test (preferred):**
- Unit, integration, behavioral, or end-to-end test
- Test fails before the change AND passes after (when applicable)
- Test exercises the production interface, not the implementation
  internals (per GOV-10, GOV-19)
- Test is included in the standard test suite (CI-runnable, not
  one-off scripts)

**Level 2 — Static check:**
- Type-checker (mypy --strict, tsc --strict, Go build, etc.)
- Linter rule (custom or built-in) that fires deterministically on
  the failure case and clears on the success case
- Schema validator (JSON Schema, OpenAPI, SQL DDL diff, protobuf)
- Reproducible static analysis (semgrep, bandit, eslint with custom rule)
- Acceptance: cite the tool + rule ID + the assertion

**Level 3 — Command transcript:**
- Recorded execution against the real surface (real DB, real API,
  real filesystem, real container, real cluster)
- Includes the full command, the relevant output, and a comparison
  to the expected output
- Stored in the proposal text or referenced by file path; ephemeral
  outputs that can't be reproduced are not Level 3

**Level 4 — Manual inspection with documented procedure:**
- A written procedure a reviewer or successor can re-execute
- Procedure cites concrete steps: open URL X, click button Y, observe
  state Z; or open log file at path A, search for pattern B
- Procedure produces a binary outcome (pass/fail), not a subjective
  judgment
- Requires Codex GO scrutiny: reviewer should challenge whether
  Level 1–3 was genuinely infeasible

**Level 5 — Documented infeasibility:**
- Concrete statement of why direct verification is impossible
  (production-only, requires customer data, requires destructive
  operation, behavior emerges from concurrency at scale)
- Compensating control identified: canary deployment, staging proxy,
  dry-run mode, post-deploy monitor with rollback trigger
- Requires owner approval evidence (DELIB-ID or AskUserQuestion answer)

**Level 6 — Owner waiver:**
- Recorded waiver under the §5.1 lifecycle with all six fields
- Waiver references this rule by ID; expiry condition stated;
  compensating control or accepted-risk statement included
- Slice 2 hook validates waiver record exists and is non-expired

**Insufficient phrasings:**
- "tested locally" without command transcript
- "should work" without verification mechanism
- "matches existing pattern" without citing which existing test
  exercises the pattern
- "trivial" or "obvious" — never sufficient for surfaces in scope of
  this rule (config, filesystem, network, auth, persistence, deployment)

## 5. Default Applicability + Per-Rule Suspension

Unchanged from `-001` §5. Waiver lifecycle six-field shape per `-001`
§5.1. Storage in KB under `type='governance_waiver'` (Slice 2).

## 6. Proposal Enforcement

Unchanged from `-001` §6. Table format unchanged.

## 7. Review Enforcement

Unchanged from `-001` §7.

## 8. Mechanical Enforcement

### 8.1 Hook Extension (Citation Reground)

Slice 2 extends the upstream `hook.bridge-proposal-standards` (managed in
`groundtruth-kb`). Per §1 of this revision, the proposal-standards thread
state has phantom-INDEX issues that must be resolved before extension.
Slice 2 will:

1. **Verify proposal-standards thread reconciliation:** confirm the
   extant proposal-standards artifacts are sufficient ground truth for
   the hook's current behavior. If not, file a parallel
   reconciliation bridge in `groundtruth-kb` first.
2. **Extend the hook** to add the code-quality-baseline checks per §6 of
   `-001`.
3. **Land the Slice 2 bridge upstream** in `groundtruth-kb` with the
   proposal-standards extension scoped via a clean dependency link.

Hook behavior, file location (`groundtruth-kb/hooks/`), event model
(`PreToolUse(Write)` + `PostToolUse(Edit)`), and rejection contract
unchanged from `-001` §8.1.

### 8.2 Fallback Verifier (Codex/Windows)

Unchanged from `-001` §8.2. Adds `scripts/check_code_quality_baseline_parity.py`
along the established `scripts/check_codex_hook_parity.py` pattern.

### 8.3 Tests

Unchanged from `-001` §8.3, plus four new test cases corresponding to
the four sharpened rules:

| Test case | Asserts |
|---|---|
| Function exceeds CQ-COMPLEXITY threshold without rationale | Hook rejects; verifier flags |
| Tuned value without comment per CQ-CONSTANTS | Hook rejects; verifier flags |
| Auth-touching proposal without per-row CQ-SECURITY checklist coverage | Hook rejects; verifier flags |
| CQ-VERIFICATION at Level 4 without Codex review acknowledgement | Hook rejects; verifier flags |
| CQ-VERIFICATION at Level 5/6 without owner approval evidence | Hook rejects; verifier flags |

### 8.4 Routing

Unchanged from `-001` §8.4: Slice 2 lands in `groundtruth-kb`; adopters
consume via `gt project upgrade` after upstream VERIFIED.

## 9. Source Grounding

Unchanged from `-001` §9 (ISO/IEC 25010, OWASP Secure Coding Practices,
SEI CERT, Twelve-Factor App, Google Python Style Guide).

## 10. Out Of Scope

Unchanged from `-001` §10. Adds: resolving the proposal-standards
phantom-INDEX state is part of Slice 2 entry-condition scope, not Slice 1.

## 11. Codex Review Asks

Same six asks as `-001` §11. Two adjustments:

- Ask 2 (checklist specificity) is now answerable via §4.1–§4.4
  acceptance criteria. Codex should confirm whether the criteria are
  enforceable in proposal review without devolving into reviewer
  judgment-call disputes; flag any criterion that needs further
  sharpening.
- Ask 5 (upstream routing) should additionally confirm whether the §1 +
  §8.1 reground (citation discipline + Slice-2 thread-reconciliation
  prerequisite) is acceptable, or whether further upstream cleanup is
  required before Slice 1 GO.

## 12. Decision Needed From Owner

None for this Slice 1 governance scoping proposal. Slice 2 will require
owner formal-artifact approvals (per `PB-ARTIFACT-APPROVAL-001`).

---

**Status request:** GO

**Files in this revision:** this file plus the corresponding INDEX
entry (added in same change set per Codex `-002` non-blocking note).

**work_list update:** none required at this revision — `GTKB-GOV-CODE-QUALITY-BASELINE`
row 7 already in place from `-001`.

**Implementation NOT yet authorized.** Slice 2 implementation proposal
follows on Codex GO, with appropriate formal-artifact-approval ceremony
for any KB record insertions.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
