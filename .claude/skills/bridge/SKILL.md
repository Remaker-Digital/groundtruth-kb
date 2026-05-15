---
name: gtkb-bridge
description: Operate the full bridge protocol — file proposals, scan INDEX for actionable items, write GO/NO-GO/VERIFIED verdicts, file post-implementation reports, navigate lifecycle states. Use when proposing implementation work that needs Loyal Opposition review, when responding to a NEW/REVISED entry as the reviewing harness, or when checking bridge thread state. The companion skills `gtkb-bridge-propose`, `gtkb-proposal-review`, and `gtkb-send-review` cover specific subactions; use this skill when working across the protocol or when an action's fit isn't obvious.
---

# /gtkb-bridge

This skill is the canonical entry point for bridge protocol operations. The bridge is GroundTruth-KB's coordination mechanism between Prime Builder and Loyal Opposition: implementation proposals, reviews, and verifications flow through versioned markdown files under `bridge/` governed by `bridge/INDEX.md` per `.claude/rules/file-bridge-protocol.md`.

This skill body presents **identical content** to both Claude Code and Codex agents via the cross-harness skill-adapter pipeline (per `config/agent-control/harness-capability-registry.toml` + `scripts/generate_codex_skill_adapters.py`). Operations described here behave the same way regardless of which harness invokes the skill.

## Bridge protocol summary

Six operations, six lifecycle states. Operations:

| Operation | Who runs it | What it produces |
|---|---|---|
| **Propose** | Prime Builder | New or revised proposal file `bridge/<topic>-NNN.md` + INDEX entry |
| **Scan** | Both harnesses | List of actionable items needing review or implementation |
| **Revise** | Prime Builder | Non-dispatchable REVISED draft or completed `REVISED:` filing after a NO-GO |
| **Respond** | Loyal Opposition | Review file with verdict GO/NO-GO/VERIFIED + INDEX update |
| **Verify** | Prime Builder | Post-implementation report + INDEX entry (status NEW; the post-impl report itself awaits VERIFIED) |
| **Status** | Both harnesses | Read-only inspection of thread state without mutation |

Lifecycle states (per `.claude/rules/file-bridge-protocol.md`):

| State | Set by | Means |
|---|---|---|
| `NEW` | Prime | Fresh proposal awaiting review |
| `REVISED` | Prime | Updated proposal after a NO-GO |
| `GO` | Loyal Opposition | Proposal approved for implementation |
| `NO-GO` | Loyal Opposition | Proposal requires changes before approval |
| `VERIFIED` | Loyal Opposition | Post-implementation verification passed |
| (terminal) | — | A thread is "terminal" when its latest entry is VERIFIED with no further work pending |

A complete thread cycle: `NEW` → (`NO-GO` → `REVISED`)* → `GO` → (implementation) → `NEW` (post-impl report) → `VERIFIED`.

## Operations

### Propose

**Purpose**: file a NEW or REVISED proposal for review.

**Action**:

1. Draft proposal body containing required sections per `.claude/rules/file-bridge-protocol.md`: `Specification Links`, `Owner Decisions / Input` (when owner-approval-dependent), spec-derived test plan, acceptance criteria, risk/rollback. Per `.claude/rules/codex-review-gate.md`, every proposal must cite all relevant governing specifications; proposals without specification links MUST be NO-GO'd.
   - **Project-linkage metadata (per `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`)**: every implementation-targeting NEW/REVISED proposal MUST include three machine-readable header lines near the top of the file:

     ```text
     Project Authorization: PAUTH-<authorization-id>
     Project: <PROJECT-ID>
     Work Item: <WI-NNNN | GTKB-* | WORKLIST-*>
     ```

     `bridge-compliance-gate.py` hard-blocks the Write when any line is absent. Non-implementation proposals self-declare exemption via a `bridge_kind:` header in `{spec_intake, governance_review, loyal_opposition_advisory}`; verdict files (GO/NO-GO/VERIFIED/WITHDRAWN) are exempt by status.
2. Choose a kebab-case `topic-slug` describing the work (e.g., `gtkb-foo-bar-001`).
3. Choose a version number: `001` for the first NEW; subsequent REVISEDs increment (`002`, `003`, ...). Versions are monotonic per thread.
4. Run pre-filing preflights:
   - `python scripts/bridge_applicability_preflight.py --bridge-id <topic-slug>` — must report `preflight_passed: true`, no missing required/advisory specs.
   - `python scripts/adr_dcl_clause_preflight.py --bridge-id <topic-slug>` — must exit 0, no blocking gaps.
5. Delegate the file write + INDEX update to the helper-mediated path (`gtkb-bridge-propose` skill — see `.claude/skills/bridge-propose/SKILL.md`). The helper performs credential scanning per `CREDENTIAL_PATTERNS + BASH_EXTRAS`, writes `bridge/<topic-slug>-<version>.md`, and inserts `Document: <topic-slug>` + `<status>: bridge/<topic-slug>-<version>.md` at the top of `bridge/INDEX.md`.

**Credential safety**: never bypass the helper for governance-content writes. Use `mode="abort"` on credential hits unless redaction is genuinely safe; `mode="redact"` replaces spans with `[REDACTED:<label>]` markers.

### Scan

**Purpose**: identify actionable bridge items for the current harness's role.

**Helper**: `.claude/skills/bridge/helpers/scan_bridge.py`

**Canonical invocation** (deterministic, replaces manual grep+Read+regex):

```powershell
python .claude/skills/bridge/helpers/scan_bridge.py --role <prime-builder|loyal-opposition> [--format json|markdown]
```

The helper parses `bridge/INDEX.md`, applies the role-filter rules below, and returns a structured `{actionable, terminal_verified, summary, generated_at, role}` dict (or formatted markdown). Public Python API: `from scan_bridge import scan; scan(role="prime-builder")`.

**Action** (manual or via helper):

1. Read `bridge/INDEX.md`. Each `Document:` block lists versions with the **latest at top**. The latest line per document defines the queue state.
2. Filter for actionable status given the current role:
   - **Loyal Opposition** acts on `NEW` and `REVISED` (proposals/reports awaiting verdict).
   - **Prime Builder** acts only on `NO-GO` (revise) and `GO` (implement). `VERIFIED` is terminal closure for both roles, not queue work.
3. For each actionable thread, read **the full version chain** (all prior entries) before responding. The protocol requires reading the whole thread, not just the latest version. The `Show-thread` helper below mechanizes that load.
4. Optional: cross-check with `.gtkb-state/bridge-poller/dispatch-state.json` (or successor under `.gtkb-state/cross-harness-trigger/`) to deduplicate against already-dispatched signatures.

### Revise

**Purpose**: help Prime Builder respond to a latest `NO-GO` without filing incomplete skeletons as actionable bridge state.

**Helper**: `.claude/skills/bridge/helpers/revise_bridge.py`

**Action**:

1. Read the live `bridge/INDEX.md` entry for the exact `Document: <topic-slug>` and the full version chain.
2. Use `plan` or `scaffold` mode to compute the next version and generate a finding-by-finding draft. Scaffold drafts live under `.gtkb-state/bridge-revisions/drafts/` and are non-dispatchable; they must not appear in `bridge/INDEX.md`.
3. Complete the revision content manually: fill every finding response, specification link, prior-deliberation note, owner-decision section when applicable, verification plan, and risk/rollback section.
4. Use `file` mode only for completed content. It refuses draft placeholders, runs the bridge-propose credential scan policy, runs `bridge_applicability_preflight.py --content-file`, runs `adr_dcl_clause_preflight.py --content-file`, refuses existing live target files, and checks for `bridge/INDEX.md` drift before inserting the live `REVISED:` line.
5. After filing, the thread is Loyal Opposition-actionable because the helper inserts `REVISED: bridge/<topic-slug>-<next>.md` at the top of the existing document entry.

The helper creates drafts; it does not author the substantive correction. Prime Builder remains responsible for completing the revision before live filing.

### Respond

**Purpose**: file a GO/NO-GO/VERIFIED verdict on a NEW or REVISED entry.

**Action**:

1. Read the full thread version chain.
2. Run the mandatory applicability preflight: `python scripts/bridge_applicability_preflight.py --bridge-id <topic-slug>`. The output's `Applicability Preflight` section must be included verbatim in the verdict file.
3. Run the mandatory clause preflight: `python scripts/adr_dcl_clause_preflight.py --bridge-id <topic-slug>` (no `--report-only`). Treat exit 5 as a NO-GO blocker unless explicit owner-waiver lines are present per `.claude/rules/file-bridge-protocol.md` "Clause-Test Preflight (Mandatory; Slice 2)".
4. Run a deliberation search: `db.search_deliberations(...)` per `.claude/rules/deliberation-protocol.md`. Add a `Prior Deliberations` section to the verdict citing relevant DELIB-IDs.
5. For implementation reviews: confirm the proposal links all relevant specifications and the proposed tests derive from those specifications. **Issue NO-GO if any relevant specification is missing or test mapping is incomplete**, per `.claude/rules/codex-review-gate.md`.
6. For verification reviews (post-impl reports): confirm the implementation report carries forward the linked specifications, includes spec-to-test mapping, executes the tests, and reports observed results. **Issue NO-GO instead of VERIFIED for any untested linked specification** unless owner waiver is documented.
7. Write the verdict file `bridge/<topic-slug>-<next-version>.md` with the verdict on line 1 (`GO`, `NO-GO`, or `VERIFIED`); include the applicability preflight and clause applicability sections; cite findings with severity (P0-P4), evidence source, impact, and recommended action per `.claude/rules/loyal-opposition.md` and `.claude/rules/report-depth-prime-builder-context.md`.
8. Update `bridge/INDEX.md`: insert the verdict line at the top of the document version list.

**Owner Decisions / Input section enforcement**: bridge proposals/reports that depend on owner approval (cite the AUQ-only rule, reference AskUserQuestion answers, or otherwise indicate owner-decision scope) MUST include a non-empty `## Owner Decisions / Input` section. Loyal Opposition issues NO-GO when this section is missing or contains placeholder content (`tbd`, `n/a`, `none`, etc.).

### Verify

**Purpose**: file a post-implementation report after a GO is implemented.

**Helper**: `.claude/skills/bridge/helpers/impl_report_bridge.py`

**Action**:

1. Implement the work per the GO d proposal scope. Run the spec-derived tests; capture the exact commands and observed results.
2. Use the helper's `plan` mode to read the live `bridge/INDEX.md` entry, require latest `GO`, load the approved proposal and GO verdict, compute the next version, carry forward linked specifications, capture dirty files via `git diff --name-only HEAD --`, and show the proposed `NEW:` INDEX line without mutation:
   ```powershell
   python .claude/skills/bridge/helpers/impl_report_bridge.py plan <topic-slug>
   ```
3. Use `scaffold` mode when you need a non-dispatchable draft under `.gtkb-state/bridge-impl-reports/drafts/`; complete the implementation claim, command evidence, observed results, spec-to-test mapping, acceptance status, and risk/rollback before live filing.
4. Use `file` mode only when the report content is ready for Loyal Opposition verification. The helper refuses non-`GO` latest status, exact-document mismatches, existing target files, credential-shaped content, and `bridge/INDEX.md` drift. It writes `bridge/<topic-slug>-<next-version>.md` and inserts `NEW: bridge/<topic-slug>-<next-version>.md` at the top of the existing document entry:
   ```powershell
   python .claude/skills/bridge/helpers/impl_report_bridge.py file <topic-slug> --content-file <completed-report.md>
   ```
5. The helper does not bypass Loyal Opposition verification. After filing, the thread is Loyal Opposition-actionable; wait for VERIFIED or NO-GO response.

### Status

**Purpose**: read-only inspection without mutation.

**Helper**: `.claude/skills/bridge/helpers/show_thread_bridge.py`

**Canonical invocation** (deterministic, replaces per-version grep+Read):

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py <topic-slug> [--format json|markdown] [--preview-lines N]
```

The helper resolves all `bridge/<slug>-NNN.md` files, sorts by version, and returns `{slug, document_entry, index_status_chain, versions, drift, found, preview_lines_cap}`. Per-version content preview is bounded (default 200 lines) so the output doesn't balloon for long bodies. Cross-references INDEX vs. on-disk files and surfaces drift in the `drift` field. Public Python API: `from show_thread_bridge import show; show("gtkb-foo")`.

**Action** (manual or via helper):

1. `grep -n "Document: <topic-slug>" bridge/INDEX.md` to find the entry.
2. Read the entry full version list (latest on top).
3. The latest line status defines the current queue position:
   - `VERIFIED` (terminal — no further action)
   - `GO` (Prime: implement)
   - `NO-GO` (Prime: revise)
   - `NEW` / `REVISED` (Loyal Opposition: review)

Use this when you need to know "what is the state of thread X?" without touching anything.

## Required reading

Before any operation:

- `.claude/rules/file-bridge-protocol.md` — protocol root contract (status table, file naming, INDEX format, mandatory gates).
- `.claude/rules/codex-review-gate.md` — review-gate constraints (mandatory specification-linkage gate; mandatory pre-filing preflight subsection).
- `.claude/rules/deliberation-protocol.md` — deliberation search obligations before proposing AND before reviewing.
- `.claude/rules/operating-model.md` — canonical vocabulary (specification, implementation proposal, implementation report, verification, etc.).
- For Loyal Opposition: `.claude/rules/loyal-opposition.md` and `.claude/rules/report-depth-prime-builder-context.md`.
- For Prime Builder: `.claude/rules/acting-prime-builder.md` and `.claude/rules/prime-builder-role.md`.

## Mandatory gates

The bridge protocol carries several mandatory gates. Skipping any is a NO-GO trigger:

- **Mandatory project root boundary** (`.claude/rules/project-root-boundary.md`): all live GT-KB files within `E:\GT-KB`. Bridge items depending on paths outside this root are NO-GO.
- **Mandatory specification linkage gate** (`.claude/rules/file-bridge-protocol.md`): every proposal must include `Specification Links` citing every relevant governing specification. Absence = NO-GO.
- **Mandatory pre-filing preflight subsection** (`.claude/rules/file-bridge-protocol.md`): preflights must run before filing; results must be cited; mechanically enforced by `.claude/hooks/bridge-compliance-gate.py`.
- **Mandatory specification-derived verification gate** (`.claude/rules/file-bridge-protocol.md`): VERIFIED requires implementation reports to include spec-to-test mapping + executed evidence.
- **Mandatory applicability preflight gate** (`.claude/rules/file-bridge-protocol.md`): GO and VERIFIED verdicts must include the `Applicability Preflight` section with `missing_required_specs: []`.
- **Mandatory clause-test preflight gate** (Slice 2; `.claude/rules/file-bridge-protocol.md`): exit 5 from `scripts/adr_dcl_clause_preflight.py` is a NO-GO blocker unless explicit owner waiver per blocking gap.
- **Mandatory Owner Decisions / Input section gate** (`.claude/rules/file-bridge-protocol.md`): proposals/reports depending on owner approval must include a non-empty `## Owner Decisions / Input` section enumerating relevant AskUserQuestion evidence. Hook-enforced via `.claude/hooks/bridge-compliance-gate.py`.

## Non-bypassable behaviors

- **Bridge files are append-only.** Never delete or rewrite a prior version. The version chain forms the audit trail.
- **`bridge/INDEX.md` is canonical for queue state.** Both harnesses must trust INDEX over any other signal (commit history, file mtime, smart-poller cache).
- **Versioning is monotonic per thread.** Latest at top within each `Document:` block.
- **Scoped commits only.** Bridge work commits should not bundle unrelated source changes.

## Companion per-action skills

For specific subactions, prefer the more focused skill:

| Action | Specific skill | Path |
|---|---|---|
| File a proposal | `gtkb-bridge-propose` | `.claude/skills/bridge-propose/SKILL.md` |
| Review a proposal | `gtkb-proposal-review` | `.claude/skills/proposal-review/SKILL.md` |
| Submit for review | `gtkb-send-review` | `.claude/skills/send-review/SKILL.md` |

This skill (`gtkb-bridge`) is the cross-cutting reference. Use it when:

- The action fit with a per-action skill is not obvious.
- You need to navigate the protocol across multiple operations in one session.
- You want to understand the full lifecycle and required gates in one place.

## Cross-harness implementation notes

- The skill body is identical across Claude Code and Codex via the `scripts/generate_codex_skill_adapters.py` adapter pipeline. The Codex adapter version at `.codex/skills/bridge/SKILL.md` carries a `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker; do NOT edit the adapter directly. Edit the canonical at `.claude/skills/bridge/SKILL.md` and regenerate.
- Hook-layer behavior (PreToolUse / PostToolUse / Stop) differs between harnesses by necessity (different schemas: `.claude/settings.json` JSON vs `.codex/hooks.json` JSON). Hook handler scripts are shared regardless.
- Underlying scripts and CLIs are harness-agnostic. A future `gt bridge` CLI subcommand (per `gtkb-bridge-skill-unified-001` Slice 3, deferred at Codex GO `-002`) will provide a uniform invocation surface; until that lands, this skill delegates to per-action helpers (`gtkb-bridge-propose`, etc.) and direct script invocations.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
