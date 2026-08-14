REVISED
::init gtkb lo
::open build

# WI-6216 Slice 1 — REVISED: the parity break has two causes, not one

bridge_kind: prime_proposal
Document: gtkb-wi6216-tool-and-gate-defect-corpus-slice-1
Version: 009
Author: Prime Builder (harness B, claude)
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 109a3bcf-5456-4b6d-99f5-ad7508304bf7
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword
Date: 2026-08-14 UTC

Work Item: WI-6216
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814B

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", ".harness-baseline-configuration/hooks/bridge-compliance-gate.py", ".goose/hooks/bridge-compliance-gate.py", ".goose/.projection-manifest.json", "platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py", "platform_tests/scripts/test_report_no_go_resume_tolerance.py", ".gitattributes", "platform_tests/scripts/test_gitattributes_lf_policy.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

This proposal performs no MemBase mutation.

Delegability: **author-retained**. Per the WI-6284 criteria this touches the
bridge/gate machinery a delegated worker's own filing depends on
(`.claude/hooks/bridge-compliance-gate.py` validates every bridge Write). That
is the bootstrap-hazard trigger, so it is not delegated regardless of how
mechanical the edit looks.

Responds to: bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-008.md

---

## Why This Revision Exists

`-008` granted GO on the strength of a single-cause mechanism: the template
lacks the D1 content, therefore parity breaks. **That mechanism is incomplete,
and acting on it alone would not make the assertion pass.**

`-008` was explicit that the supporting measurement was not re-executed
(§ Not verified: "the 19 / 21 failure counts were not re-executed"). On
re-measuring, the delta claim does not reproduce. This revision corrects the
mechanism and widens `target_paths` by the two files the real repair needs.

No approved substance is withdrawn. D1 and D3 are unchanged from `-005`.

## Finding 1 — Parity has two independent causes

The assertion is `LIVE_HOOK.read_bytes() == TEMPLATE_HOOK.read_bytes()`
(`test_bridge_compliance_gate_disposition.py:226`, and again at
`test_bridge_compliance_requirement_sufficiency.py:305`). It compares
**working-tree bytes**. Measured now:

| | active | template |
|---|---:|---:|
| working-tree bytes | 121904 | 115200 |
| line endings | CRLF x2771, bare-LF 0 | CRLF 0, LF x2664 |

The pytest failure is at **byte index 22** — `b'\r' != b'\n'` — the first line
ending, before any content difference is reached.

Decomposed by normalising both copies to LF:

- **Cause A — line endings.** Normalising active to LF drops it 121904 -> 119133.
- **Cause B — missing D1+D3 content.** After both are LF, a 3933-byte residual
  remains: 4 hunks, +123 / -16 lines. That is the D1+D3 work `-008` identified.

`-008` addressed Cause B only. Applying D1 to the template is **necessary but
not sufficient**; with Cause A unfixed the assertion still fails at byte 22.

## Finding 2 — Cause A is a `.gitattributes` gap, and it is pre-existing

```
git check-attr text eol -- <both copies>
  .claude/hooks/bridge-compliance-gate.py:                  text: unspecified   eol: unspecified
  groundtruth-kb/templates/hooks/bridge-compliance-gate.py: text: set           eol: lf
```

`.gitattributes` pins `groundtruth-kb/templates/hooks/** text eol=lf` but
carries **no entry for `.claude/hooks/**`**, so that path falls through to
`core.autocrlf=true` and is materialised CRLF on checkout.

`git ls-files --eol` confirms the asymmetry is the norm, not an accident of this
edit:

```
i/lf  w/crlf  attr/                 .claude/hooks/bridge-compliance-gate.py
i/lf  w/lf    attr/text eol=lf      groundtruth-kb/templates/hooks/bridge-compliance-gate.py
```

and across `.claude/hooks/` the census is **32 `w/crlf` to 1 `w/lf`**.

**Consequence for V2.** `-008` V2 requires the affected-module failure count to
"return to the `HEAD` baseline of 19". That baseline is not reproducible from a
real checkout: both blobs are LF-identical at HEAD (`0f7a5614…`, 115200 bytes),
but a checkout materialises the active copy CRLF and the template LF, so the two
parity tests fail at HEAD as well. A restore performed by writing HEAD **blob
bytes** yields LF and makes them pass; a restore performed by `git checkout`
yields CRLF and does not. The 19 figure is an artefact of the first method.
**This revision therefore replaces V2 with a measurement that is reproducible.**

**Blast radius.** CI is unaffected: `platform_tests` runs on `ubuntu-latest`
(`.github/workflows/python-tests.yml`, `groundtruth-kb-tests.yml`) where both
copies are LF. The single `windows-latest` job in `release-candidate-gate.yml` is
the frontend/Node gate and runs no `platform_tests`. The defect is therefore
invisible to CI and lands entirely on Windows sessions — which is why it
presented as "D1 broke parity" rather than as a standing condition.

## Change 1 — Add `.gitattributes` to `target_paths`

Add an LF pin for the active hook directory so the two copies can be
byte-identical in a Windows working tree:

```
.claude/hooks/** text eol=lf
```

This is the mechanism the repository already uses for the template side, applied
to the side that lacks it. It changes checkout materialisation only; the index
blobs are already LF, so no re-normalisation churn is introduced.

## Change 2 — Add `platform_tests/scripts/test_gitattributes_lf_policy.py`

That module already exists and already encodes this exact policy:
`LF_POLICY_PATHS` (lines 8-20) asserts `text: set` and `eol: lf` via
`git check-attr` for eleven paths — **including
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py` and excluding the
active copy**. Adding `.claude/hooks/bridge-compliance-gate.py` to that tuple
makes the fix self-guarding and prevents silent recurrence.

Without this the repair is unguarded: nothing fails if the pin is later removed.

## Change 3 — Normalise the active copy to LF

`.claude/hooks/bridge-compliance-gate.py` is already in `target_paths`. Writing
it with LF is what actually satisfies the assertion today; the `.gitattributes`
pin is what keeps it satisfied across future checkouts. Both are required.

## Scope (revised)

1. **D1 repair** — unchanged from `-005`, implemented.
2. ~~D2~~ — withdrawn at `-007`, accepted at `-008`. `WI-6216` stays open for it.
3. **D3 repair (PARTIAL, by design)** — unchanged from `-005`; `WI-6237` retains
   the residual barriers.
4. **Projection parity** — repaired hook in active, activation template, neutral
   baseline, and the `.goose` projection.
5. **EOL durability (new)** — Changes 1-3.
6. **Two regression modules**, unchanged.

## Specification-Derived Verification

| Requirement | Test | Command |
|---|---|---|
| Cause B repaired: template carries D1+D3 | `test_template_and_active_hook_byte_identical` (disposition) | `python -m pytest platform_tests/scripts/test_bridge_compliance_gate_disposition.py -q` |
| Cause B repaired: second asserting module | `test_template_and_active_hook_byte_identical` (requirement sufficiency) | `python -m pytest platform_tests/scripts/test_bridge_compliance_requirement_sufficiency.py -q` |
| Cause A repaired: active hook pinned LF | `test_generated_and_scaffold_artifacts_resolve_to_lf` | `python -m pytest platform_tests/scripts/test_gitattributes_lf_policy.py -q` |
| D1 sub-repairs | 11 rows in `test_bridge_compliance_gate_pending_banner.py` | `python -m pytest platform_tests/scripts/test_bridge_compliance_gate_pending_banner.py -q` |
| D3 tolerance + fail-closed + residual gap | 7 rows in `test_report_no_go_resume_tolerance.py` | `python -m pytest platform_tests/scripts/test_report_no_go_resume_tolerance.py -q` |
| Projection drift | `--check` 0 drifted | `python scripts/harness_projection/project_harness.py --harness goose --check` |
| Lint gate | ruff check | `python -m ruff check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py platform_tests/scripts/test_gitattributes_lf_policy.py` |
| Format gate (separate) | ruff format | `python -m ruff format --check .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py platform_tests/scripts/test_gitattributes_lf_policy.py` |

**Replacement for `-008` V2.** Rather than a `HEAD`-baseline failure count that
depends on restore method, the reproducible assertion is: after the repair,
`git ls-files --eol` reports `w/lf` for **both** gate copies, and both
`test_template_and_active_hook_byte_identical` rows pass. The report will state
the affected-module count before and after, and will name the restore method
used so the number is interpretable.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v4 — D1/D3 repair the bridge protocol's own
  guidance and recovery surfaces.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — D3's stranded path is the lawful
  post-NO-GO revision route.
- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2; Changes 1-3 extend the
  same activation-parity obligation to the checkout layer that carries it.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every measurement in Findings 1 and 2
  is a fresh read (`git check-attr`, `git ls-files --eol`, live pytest); the
  superseded 19/21 figure is explicitly retired as non-reproducible.
- `SPEC-1662` (GOV-18) — behavioral assertions; Change 2 converts an
  unguarded repair into an asserted one.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1.

## Requirement Sufficiency

Existing requirements sufficient. Changes 1-3 correct the slice's own mechanism
against verified evidence and use a policy surface the repository already
defines; no new requirement surface is created.

## Owner Decisions / Input

- **AskUserQuestion, 2026-08-14 (this session).** Presented with the two-cause
  finding and the fact that the durable repair needs `.gitattributes` plus the
  LF-policy test — neither in the approved `target_paths` — the owner selected
  **"File REVISED, widen scope"** over completing inside the current GO scope or
  splitting into a parallel thread. This revision implements that selection.
- **AskUserQuestion, 2026-08-14 (this session).** On a concurrent-session
  startup-gate block, the owner selected **"Wait out expiry, keep Phase 2
  scope"**, declining to expand this slice to cover the lifecycle-guard
  collision defect. That defect is captured as backlog, not folded in here.
- **Owner directive, 2026-08-14 (this session, verbatim in transcript):** the
  verifying Loyal Opposition is the party that commits; bridge artifacts are
  ephemeral messages, the git log is the durable evidence, and the VERIFIED
  verdict is the post-commit signal. This directly answers `-008` F3, which
  recorded that the reviewer had no record of this directive and could not
  verify it. Per that finding's own remedy it should be recorded in
  `.claude/rules/file-bridge-protocol.md` rather than carried in report prose;
  that rule edit is **out of scope here** and is not proposed by this document.
- **Owner standing directive (2026-08-13/14):** capture and fix tool defects;
  `WI-6216` is the owner-created carrier for this corpus.
- Consistent with the directive above, the implementation is **deliberately not
  committed**; the changes sit in the worktree for the verifying LO to commit.

## Prior Deliberations

- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-008.md` — the GO this
  revises, including its own "Not verified" disclosure on the 19/21 counts that
  Finding 2 acts on.
- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-007.md` — Change 1
  (template parity) and the D2 withdrawal this revision preserves unchanged.
- `bridge/gtkb-wi6216-tool-and-gate-defect-corpus-slice-1-002.md` F1 — "a repair
  derived from a summary rather than the artifact". Finding 1 is the third
  instance of that class on this thread, this time in an accepted GO's own
  mechanism.
- `bridge/gtkb-operation-taxonomy-baseline-path-rules-006.md` F2 — the
  three-barrier analysis D3 cites.
- `DELIB-20260813-TOOL-AND-GATE-FLAWS` — the 13-item corpus.
- `WI-6237` / `TEST-11901` — D3's work item, deliberately left open.

## Cross-Harness Disposition

- **Claude Code** (`.claude/hooks/`): repaired in place, normalised to LF, and
  pinned by `.gitattributes`.
- **Goose** (`.goose/hooks/`): mechanical re-projection from the repaired
  baseline; `--check` 0-drift required.
- **Neutral baseline** (`.harness-baseline-configuration/hooks/`): carries the
  spliced logical change; not byte-identical to the active copy by design, and
  no parity assertion binds it.
- **Codex, Cursor, Antigravity, API harnesses**: carry no copy of the affected
  gate. Typed disposition: `deferred-to-projector-cutover`.

## Risk / Rollback

Change 1 alters checkout materialisation for `.claude/hooks/**`. Index blobs are
already LF, so no content changes and no re-normalisation commit is implied;
the observable effect is that a subsequent checkout writes LF where it
previously wrote CRLF. Python is line-ending agnostic on Windows, and
`.claude/hooks/bridge-axis-2-surface.py` already sits at LF in this worktree, so
LF in that directory is precedented rather than novel.

The residual risk is scoped to one directory and is asserted by Change 2: if the
pin is removed, `test_gitattributes_lf_policy.py` fails.

D1/D3 risk is unchanged from `-007` and bounded by the same guard tests.

Rollback: revert the `.gitattributes` line, the `LF_POLICY_PATHS` entry, two
source files, the template, the baseline copy, and re-project.

## Recommended Commit Type

Recommended commit type: `fix` — gate repairs plus a checkout-durability
correction and regression tests; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
