REVISED

# GTKB-COMMAND-SURFACE — Architectural Plan (REVISED-1)

**Status:** REVISED (architecture/scoping; addresses NO-GO at -002; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-COMMAND-SURFACE
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** architecture_proposal
**Routing:** Upstream candidate (`groundtruth-kb`).

bridge_kind: architecture_proposal
work_item_ids: [GTKB-COMMAND-SURFACE]
spec_ids: []
target_project: groundtruth-kb
implementation_scope: architectural_plan_only
requires_review: true
requires_verification: false

---

## 0. What This Revision Addresses

Codex NO-GO at `bridge/gtkb-command-surface-002.md` raised four
findings against the original `bridge/gtkb-command-surface-001.md`.
This revision addresses each finding directly. The strategic
direction (three surfaces over one state, `::` namespace, detector
suppression as load-bearing contract) is preserved. The implementation
premises that were wrong have been corrected.

**Read order:** the binding architecture is `-001` *as modified by
this `-003`*. Sections of `-001` not modified here remain authoritative
verbatim. Sections modified here supersede `-001`.

## 1. Codex GO Conditions Compliance

| GO Condition (from -002) | Resolution in this revision |
|---|---|
| 1. Move or explicitly track the command registry path, with a test or command proving it is not ignored | §3 below: registry tracked at `.claude/commands/registry.json` via new `.gitignore` negation pattern, mirroring the existing `.claude/skills/` and `.claude/hooks/` pattern. CS-1.5 slice adds a regression test asserting the path is tracked |
| 2. Rewrite CS-2 as an implementable hook-to-model routing contract, or explicitly design a real non-model command runner | §4 below: CS-2 is now an additional-context routing contract. The UserPromptSubmit hook parses `::cmd`, validates against registry, writes per-turn suppression/audit state, and emits a compact additional-context routing directive. The model/harness invokes the named skill via the Skill tool. No direct skill execution from the hook |
| 3. Correct the first command set's skill dispatch names or define a tested alias layer | §5 below: dispatch names corrected to actual tracked directory names (`spec-intake`, `decision-capture`). Frontmatter `name:` field (`gtkb-spec-intake`) is documentation; the Skill tool invocation uses the directory name |
| 4. Clarify whether existing `.claude/commands/` slash commands are local-only harness files or tracked/scaffolded GT-KB product surface | §6 below: explicit "tracked vs local" distinction added. The existing 6 `.claude/commands/` files are *currently* local-only (gitignored); whether they become tracked product surface is a Slice CS-7 decision out of scope for the architecture |

Two additional clarifications adopted from the NO-GO's positive findings:

- CS-1 (`gt` CLI) and CS-2 (dispatcher hook) ordering: parallel preserved; the NO-GO confirmed `gt` is genuinely not on PATH despite the package declaration. (`-001` §5.1, unchanged.)
- Heuristic classifiers as backstops: confirmed direction. (`-001` §4.1, unchanged.)

## 2. Sections of -001 That Remain Authoritative Unchanged

These sections of `-001` are not modified by this revision:

- §0 What This Proposal Is
- §1 Prior Deliberations
- §2 Architectural Vision: Three Surfaces, One State
- §3.1 KB / state stores
- §3.2 Skills (catalogue summary; specific dispatch-name correction is in §5 below)
- §3.3 Hooks
- §3.4 groundtruth-kb package
- §3.5 Dashboard infrastructure
- §3.6 Bridge protocol
- §4.1 Heuristic prose triggers (retire to backstop status)
- §4.2 Multi-phrase prose-trigger lists
- §4.3 Dead Codex hook config
- §4.4 What does *not* retire
- §5.1 The `gt` CLI binary (build before in-session)
- §5.4 Dashboard cross-surface affordance
- §5.5 Macros + workflow scaffolds
- §5.6 Codex parity
- §6.1 ADR: `::` chosen over alternatives
- §7 AI Cognitive Load
- §8 Token Cost / Savings Estimate
- §10 Open Questions for Codex Review
- §11 Decisions Needed From Owner

## 3. CORRECTED §3.7 + §4 Registry Tracking (Finding [P1] #1)

### 3.1 Registry path: `.claude/commands/registry.json` (now tracked via gitignore negation)

The original `-001` §5.2 claimed the registry would be tracked at
`.claude/commands/registry.json`. Verified via `git check-ignore` that
this path is currently gitignored under the `.claude/*` blanket pattern
at `.gitignore:211`. The `.claude/` directory uses an "ignore contents,
negate specific paths" pattern (lines 201-231) for the existing
tracked harness-adjacent directories: `settings.json`, `hooks/`,
`rules/`, `skills/`. The `commands/` directory is not in the negation
list.

**Architecture decision:** add `.claude/commands/` to the negation list.
Rationale:

- **Consistency with existing pattern.** `.claude/hooks/`, `.claude/rules/`,
  and `.claude/skills/` are all negated. The command registry is
  semantically the same kind of artifact: harness-adjacent governance
  infrastructure that must travel with the project.
- **Adopter scaffolding alignment.** The isolation project's adopter
  copy point is `.claude/`. Putting the registry there means adopters
  receive the command surface via the same scaffolding mechanism that
  delivers their hooks, rules, and skills. Putting it elsewhere
  (e.g., `config/agent-control/`) creates a second copy point.
- **Keeps `.claude/` as the canonical harness governance namespace.**
  Splitting harness governance across multiple top-level directories
  fragments the mental model.

**The `.gitignore` patch (Slice CS-1.5; new):**

```
!.claude/commands/
.claude/commands/*
!.claude/commands/registry.json
!.claude/commands/*.md
```

Pattern is identical to `.claude/skills/` (negate directory; ignore
loose contents; negate specific tracked artifacts).

### 3.2 New Slice CS-1.5: Registry tracking + regression test

Inserted between CS-1 (gt CLI) and CS-2 (dispatcher hook) so the
registry path is tracked before any code reads from it.

- Patch `.gitignore` per §3.1 above
- Create `tests/scripts/test_command_registry_tracking.py` that asserts
  `git check-ignore .claude/commands/registry.json` returns no rule
  (i.e., the path is tracked) and the file exists
- Wire the test into `scripts/release_candidate_gate.py`
- Empty registry stub committed to `.claude/commands/registry.json`
  (just `{}`) so the test passes from day one
- The 6 existing local `.claude/commands/*.md` files remain *un*tracked
  (consistent with §6 below); the negation rule's `!.claude/commands/*.md`
  pattern would track them, so the registry-only revision uses a more
  precise pattern (only `registry.json` is tracked initially)

**Revised `.gitignore` patch:**

```
!.claude/commands/
.claude/commands/*
!.claude/commands/registry.json
```

(No `*.md` negation in CS-1.5; that decision is deferred to CS-7
per §6 below.)

## 4. CORRECTED §5.2 The `::` In-Session Command Dispatcher (Finding [P1] #2)

The original `-001` §5.2 described the UserPromptSubmit hook as if it
"loads the named skill body" and "passes the remainder of the prompt
body as arguments." That conflated two distinct execution layers:

- **What UserPromptSubmit hooks actually do** (verified in
  `.claude/hooks/owner-decision-tracker.py:716-782`): they read state,
  emit additional context to stdout, and optionally block prompt
  delivery. They do *not* invoke skills, alter model-side skill
  loading, or pass arguments into the model's tool dispatch.
- **What skills do**: they are invoked by the model via the Skill tool
  (or by user typing `/<skill-name>`). The model decides when to
  invoke based on context — including additional context emitted by
  hooks.

### Corrected CS-2 contract

The CS-2 dispatcher is an **additional-context routing hook**, not a
direct skill executor. Specifically:

1. UserPromptSubmit hook fires with the user's raw prompt body.
2. Hook parses `^::(\w+)\b` at message start (or per-line at
   line start, by configuration). If no command match, hook returns
   silently and the prompt proceeds normally.
3. If matched, hook validates the command against the registry at
   `.claude/commands/registry.json`. Unknown commands emit additional
   context: "Unknown command `::xxx`. Use `::help` to list commands."
   The owner's prompt still proceeds; the model sees both the original
   prompt and the unknown-command notice.
4. If valid, the hook:
   - Writes a per-turn suppression/audit record to
     `.groundtruth/session/command-audit/<session-id>.jsonl`
     (gitignored — see §7) listing detectors-to-suppress for that turn
     and the command body
   - Modifies behavior of *other* `.claude/hooks/` UserPromptSubmit
     hooks (`spec-classifier.py`, `owner-decision-tracker.py`) by
     reading the suppression record at hook entry and short-circuiting
     accordingly
   - Emits compact additional context to stdout, e.g.:
     ```
     Owner invoked GT-KB command `::spec`.
     Skill to invoke: spec-intake
     Arguments: <command body>
     Detector suppressions active for this turn: spec-classifier, owner-decision-tracker:offering_or_choice
     ```
5. The model receives the original prompt + this routing directive in
   its context, and uses the Skill tool to invoke `spec-intake` with
   the named arguments.

### Why this matters for the architecture

The architecture-binding contract is **the additional-context payload
shape**, not the hook implementation. Slice CS-2 ships:

- The hook itself
- The contract spec (additional-context format, registry schema,
  suppression-record format)
- Tests asserting the hook's stdout matches the contract for known
  inputs — explicitly **not** "tests asserting the skill ran" because
  skill execution is the model's responsibility

### Why the suppression mechanism is implementable

`spec-classifier.py` and `owner-decision-tracker.py` are the only two
existing UserPromptSubmit hooks that are FP-prone. CS-2 modifies both
to consult the suppression record at startup:

```python
# Existing UserPromptSubmit hook (e.g., owner-decision-tracker.py)
def main():
    suppression = read_suppression_record_for_this_turn()
    if "owner-decision-tracker" in suppression.get("detectors", []):
        sys.exit(0)  # Short-circuit; command surface owns this turn
    # ... existing detection logic
```

The dispatcher hook runs first (registered earliest in
`settings.json`), writes the record, then the other hooks run with the
record visible. This is a deterministic ordering dependency, declared
in `.claude/settings.json` and verified by a CS-2 test.

### What CS-2 explicitly does NOT do

- Does not "load" or "execute" skill bodies
- Does not pass arguments through model tools directly
- Does not block the prompt unless the owner used `::halt` or similar
  explicit-block command
- Does not modify Claude Code's slash command (`/`) dispatch

### Out of scope (deferred to later slices or backlog)

- A non-model command runner (subprocess execution of skills outside
  the model). Considered and rejected for the first iteration: this
  would create a parallel runtime that must duplicate the model's
  context-aware reasoning. CLI dispatch (`gt <cmd>`) covers the
  non-model path.

## 5. CORRECTED §5.3 First Command Set: Skill Names (Finding [P2] #3)

The original `-001` §5.3 listed dispatch targets `gtkb-spec-intake` and
`gtkb-decision-capture`, which are the values of the `name:` frontmatter
field in the SKILL.md files. The Skill tool's actual invocation token
is the **directory name**, which is `spec-intake` and `decision-capture`
respectively. The frontmatter `name:` is documentation, not the
invocation handle.

### Corrected dispatch table

| Command | Skill dispatch (directory name) | Detectors suppressed | Leverage |
|---|---|---|---|
| `::spec <body>` | `spec-intake` | `spec-classifier`, `owner-decision-tracker:offering_or_choice` | Eliminates GOV-09 heuristic FPs |
| `::decide <body>` | `decision-capture` | `owner-decision-tracker:*` | Eliminates the FP cascade class |
| `::question <body>` | (no skill; pure suppression) | `owner-decision-tracker:*` | Marks owner clarifying questions as non-archival |
| `::init` | (formalize session-start; no new skill) | n/a | Replaces "Continue work on Agent Red…" prose |
| `::wrap` | `kb-session-wrap` | n/a | Replaces 15-phrase trigger list |
| `::bridge [scan\|propose\|review]` | `bridge-propose` / `proposal-review` | n/a | Replaces "Bridge" / "Bridge scan" prose triggers |

Verified directory names:

```
.claude/skills/spec-intake/        ← invoked as `spec-intake`
.claude/skills/decision-capture/   ← invoked as `decision-capture`
.claude/skills/kb-session-wrap/    ← invoked as `kb-session-wrap`
.claude/skills/bridge-propose/     ← invoked as `bridge-propose`
.claude/skills/proposal-review/    ← invoked as `proposal-review`
```

### Registry schema (CS-2 implementation contract)

The registry uses the *directory name* (skill invocation token) as
the canonical reference. Frontmatter names are not consulted by the
dispatcher.

```json
{
  "version": 1,
  "commands": {
    "spec": {
      "skill": "spec-intake",
      "suppress_detectors": [
        "spec-classifier",
        "owner-decision-tracker:offering_or_choice"
      ],
      "argument_handling": "pass_remainder",
      "description": "Owner is stating a specification."
    },
    "decide": {
      "skill": "decision-capture",
      "suppress_detectors": ["owner-decision-tracker"],
      "argument_handling": "pass_remainder",
      "description": "Owner is making a decision."
    },
    "question": {
      "skill": null,
      "suppress_detectors": ["owner-decision-tracker"],
      "argument_handling": "pass_remainder",
      "description": "Owner is asking a clarifying question, not a decision."
    },
    "init": {
      "skill": null,
      "suppress_detectors": [],
      "argument_handling": "ignore",
      "description": "Initialize session start."
    },
    "wrap": {
      "skill": "kb-session-wrap",
      "suppress_detectors": [],
      "argument_handling": "ignore",
      "description": "Run session wrap-up."
    },
    "bridge": {
      "skill": "bridge-propose",
      "suppress_detectors": [],
      "argument_handling": "subcommand_dispatch",
      "subcommands": {
        "scan": "proposal-review",
        "propose": "bridge-propose",
        "review": "proposal-review"
      },
      "description": "Bridge protocol operations."
    }
  }
}
```

CS-2 includes a registry-schema test that validates each `skill` value
points to an existing `.claude/skills/<name>/SKILL.md` file at registry
load time.

### Alias-layer alternative (rejected)

Codex offered an alternative ("define an explicit alias layer in the
registry and test aliases against the filesystem"). Considered and
rejected for the first iteration: aliases add a layer of indirection
without removing the underlying constraint that the dispatcher must
ultimately resolve to a directory name. Direct directory-name reference
is simpler and equally testable.

## 6. NEW §3.7 Tracked vs Local Harness Commands (Finding [P2] #4)

The original `-001` §3.7 listed six existing `.claude/commands/` files
as "valid Claude Code `/` commands" that "stay" — implying they are
part of the GT-KB product surface. Verified that all six files are
currently *local-only* (gitignored under `.claude/*`):

```
.claude/commands/check-db.md          (gitignored)
.claude/commands/check-security.md    (gitignored)
.claude/commands/open-items.md        (gitignored)
.claude/commands/preflight.md         (gitignored)
.claude/commands/quick-review.md      (gitignored)
.claude/commands/refresh-creds.md     (gitignored)
```

These files are local development conveniences. They are not part of
what an adopter receives via `gt project upgrade`; they are not part
of CI; they are not visible to fresh checkouts.

### Architecture distinction

The plan distinguishes two categories of commands:

| Category | Tracked? | Distribution | Examples |
|---|---|---|---|
| **GT-KB product commands** (`::` namespace) | Yes | Adopter scaffolding via `.claude/commands/registry.json` | `::spec`, `::decide`, `::wrap`, `::bridge`, `::init` |
| **Local harness commands** (`/` namespace, optional) | No (currently) | Per-developer; copied via `~/.claude/` if user wants them globally | The 6 existing files; future per-project conveniences |

### Slice CS-7 (new): Local-command audit and disposition

A future slice (out of scope for this architecture) decides per file
whether each of the 6 existing local commands should:

- Become a tracked product command (track via `*.md` negation)
- Become a `::` GT-KB command (move under registry)
- Stay local-only (no change)

Until CS-7 lands, the architecture treats the 6 as *local-only*: they
exist on this developer's machine, they work, but they are not part
of the GT-KB binding surface inventory. The `.gitignore` negation
pattern in §3.2 deliberately tracks only `registry.json`, not loose
`*.md` files in `.claude/commands/`.

This matches the existing treatment of `.claude/settings.local.json`
(also intentionally local; documented in `.gitignore:207-208`).

## 7. Suppression-Record Audit Path

Mentioned in `-001` §6.2 but the path was not fully specified. Codex
correctly flagged this as ambiguous in the original.

**Path:** `.groundtruth/session/command-audit/<session-id>.jsonl`

**Tracking status:** **gitignored.** The session-state directory
already has precedent for ignoring per-session ephemera
(`.groundtruth/session/overlays/` is gitignored at `.gitignore:345`).
The audit record is per-session ephemera with the same lifecycle.

**`.gitignore` patch (CS-2 implementation):**

```
.groundtruth/session/command-audit/
```

Added to existing `.groundtruth/session/` ignore block.

**Format (one JSON object per line):**

```json
{
  "turn_id": "S310-T15",
  "timestamp": "2026-04-26T00:30:00Z",
  "command": "spec",
  "command_body": "<truncated to first 200 chars>",
  "skill_invoked": "spec-intake",
  "detectors_suppressed": ["spec-classifier", "owner-decision-tracker:offering_or_choice"],
  "registry_version": 1
}
```

**Retention:** indefinite within session; cleared at session-end by
`kb-session-wrap` Phase 1. (Not implemented in CS-2; deferred to a
small CS-2.5 wrap-up integration slice.)

**Redaction:** `command_body` truncated to first 200 chars. Full body
content is in the harness transcript; the audit only needs enough to
correlate. CS-2 includes a redaction test asserting truncation.

## 8. Updated Slice Sequencing

Revised order (CS-1.5 inserted; CS-7 added):

1. **CS-1** — `gt` CLI binary on PATH, minimal subcommand set
2. **CS-1.5** — Registry tracking via `.gitignore` negation + regression test (NEW; addresses Finding [P1] #1)
3. **CS-2** — `::` dispatcher hook + registry + suppression contract + audit log (REVISED per Finding [P1] #2)
4. **CS-2.5** — `kb-session-wrap` integration: clear command-audit at session end (small)
5. **CS-3** — First six commands (`::spec`, `::decide`, `::question`, `::init`, `::wrap`, `::bridge`) with corrected skill dispatch names (REVISED per Finding [P2] #3)
6. **CS-4** — Dashboard cross-surface affordance
7. **CS-5+** — Macros and workflow scaffolds, owner-discovered
8. **CS-6** — Codex parity
9. **CS-7** — Local-command audit and disposition (NEW; addresses Finding [P2] #4)

CS-1 and CS-1.5 can run in parallel (independent surfaces); CS-2
depends on CS-1.5; CS-3 depends on CS-2; CS-2.5 depends on CS-2; CS-4
depends on CS-3; CS-5+ are independent; CS-6 depends on CS-3; CS-7 is
independent and can land any time.

## 9. Updated §6.2 ADR: Per-turn detector-suppression contract

Materially unchanged from `-001` §6.2 except for the path correction:
the suppression record's path is now formally
`.groundtruth/session/command-audit/<session-id>.jsonl` (gitignored;
see §7 above). The contract semantics — write before other detectors
run, short-circuit named detectors for that turn only, log for audit —
are unchanged.

The dispatcher hook must be registered earliest in `settings.json`'s
UserPromptSubmit hook list. CS-2 includes a test asserting the
ordering.

## 10. Code Quality Baseline (revised CQ-PATHS-001 + CQ-LOGGING-001 + CQ-SECURITY-001)

| Rule ID | Applies? | Notes |
|---|---:|---|
| CQ-SECRETS-001 | Yes | No credentials in any architectural artifact; suppression-record `command_body` truncated to 200 chars (§7) to limit credential-adjacent leakage. CS-2 redaction test enforces |
| CQ-PATHS-001 | Yes | All proposed paths are project-root-relative or `${CLAUDE_PLUGIN_ROOT}`-relative. Registry path is `.claude/commands/registry.json` (now tracked); audit path is `.groundtruth/session/command-audit/<session-id>.jsonl` (gitignored). No hardcoded `E:\GT-KB\` |
| CQ-CONSTANTS-001 | Yes | Command prefix `::` is a single tracked constant; registry version field tracked separately for future-compat schema migrations |
| CQ-DOCS-001 | Yes | Registry schema documented in §5; suppression-record schema documented in §7; CS-2 ships with both as committed JSON Schema files for validation |
| CQ-COMPLEXITY-001 | n/a (architecture; no code) | n/a |
| CQ-TESTS-001 | n/a (architecture; no code) | Implementation slices land tests; CS-1.5 includes the registry-tracking regression test as the architecture's first verifiable artifact |
| CQ-LOGGING-001 | Yes | §7 specifies the audit-log format, location, redaction, and retention. CS-2 ships with both write-side (hook) and read-side (consumer hooks) test coverage |
| CQ-SECURITY-001 | Yes | Authorization model: §2.2 of -001 unchanged. Audit log is gitignored (no transcript exfiltration via commit); registry is tracked (auditable). Detector suppression is per-turn only (no persistent bypass) |
| CQ-VERIFICATION-001 | Partial | Architecture-level verification = Codex GO; implementation-level verification per slice. CS-1.5 introduces architecture-level verification at the contract layer (gitignore behavior is testable) |

---

**Status request:** GO on this revised architectural plan.

**Files in this proposal:** this file (`-003`) only. The unchanged
authoritative content from `-001` is incorporated by reference per §2.

**Files modified on Codex GO:** none in this bridge. Subsequent slice
proposals will name their modified files individually. CS-1.5 (the
new slice) will modify `.gitignore` and add one test file.

**Implementation NOT yet authorized.** This proposal authorizes
*subsequent slice proposals to be filed under the architectural
direction in this document*. Each slice still requires its own Codex
GO before implementation.

## 11. Acknowledgment of NO-GO Quality

The four findings in `-002` were all materially correct and would have
caused implementation defects had they not been caught. Each is
addressed substantively rather than waved away. The hook-contract
correction in §4 in particular is a structural improvement, not a
patch — the original framing would have produced an unimplementable
slice.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
