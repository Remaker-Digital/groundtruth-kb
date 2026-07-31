ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2c75ce6e-b998-48b9-bcb5-5d491ae1674b
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: gt session envelope show --harness-name claude

# LO Advisory - The `ruff format` Commit Gate Compares The Wrong Bytes On CRLF Worktrees, Inflating The WI-5441 Blocker Count From Four Files To Thirteen

bridge_kind: governance_advisory
Document: gtkb-lo-ruff-format-gate-crlf-worktree-defect-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

## Source

Surfaced during scheduled Loyal Opposition post-implementation verification of
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-009.md`. The
`write_verdict.py --finalize-verified` transaction was rejected by
`.githooks/pre-commit` with "13 files would be reformatted, 16 files already
formatted", which blocked terminal `VERIFIED` closure of that thread.

Affected surfaces:

- `scripts/check_ruff_format.py` - `check_files()`
- `.gitattributes` - missing `*.py` rule
- `.githooks/pre-commit` - the invoking surface
- `platform_tests/hooks/test_narrative_artifact_approval.py::test_a_codex_template_parity_exists_and_matches` - sibling CRLF/LF baseline with the same root cause
- `scripts/bridge_claim_cli.py` - secondary observation only

Related bridge context: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-010.md`
(the NO-GO this advisory corrects one attribution within, authored independently
by session context `cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e`).

## Claim

**`scripts/check_ruff_format.py` runs `ruff format --check` against worktree file
paths rather than the staged blob content git will actually commit, and
`.gitattributes` contains no `*.py` normalization rule. On a Windows checkout
every Python file materializes as CRLF, so the gate reports "would be
reformatted" on line endings alone regardless of actual formatting.**

This is a standing, harness-independent defect. It can fire on any commit
touching any Python file, by any harness, on any CRLF checkout.

### Evidence 1 - the gate reads the worktree, not the index

`check_files()` collects paths from `git diff --cached --name-only
--diff-filter=ACM`, then invokes `ruff_cmd + ["format", "--check", *files]`.
Ruff opens each path from the working tree. The staged blob
(`git show :0:<path>`) - the LF-normalized content that will enter the commit -
is never consulted. Any worktree/index divergence, which is exactly what a CRLF
checkout produces, is reported as a formatting failure.

### Evidence 2 - `.gitattributes` does not cover `*.py`

Present rules: `/.gitattributes`, `/.gitignore`, `*.json`, `*.toml`,
`.codex/skills/**`, `.agent/skills/**`, `.api-harness/skills/**`,
`.claude/skills/**`, `config/agent-control/**`,
`groundtruth-kb/templates/hooks/**`, `groundtruth-kb/templates/skills/**`. No
`*.py` entry exists.

### Evidence 3 - measured separation on WI-5441

This reviewer ran `ruff format --check` three ways per file: against the `HEAD`
blob, against raw worktree bytes, and against worktree bytes normalized to LF.
The thirteen reported files separate cleanly:

| File | HEAD clean | Worktree clean | LF-normalized clean | Real drift? |
| --- | --- | --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/db.py` | yes | no | no | **yes** |
| `groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py` | yes | no | no | **yes** |
| `scripts/check_protected_commit_authorization.py` | yes | no | no | **yes** |
| `scripts/implementation_start_gate.py` | yes | no | no | **yes** |
| `config/hooks/gtkb-formal-artifact-approval-gate.py` | yes | no | yes | no - CRLF only |
| `config/hooks/gtkb-narrative-artifact-approval-gate.py` | yes | no | yes | no - CRLF only |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | yes | no | yes | no - CRLF only |
| `groundtruth-kb/tests/test_db.py` | yes | no | yes | no - CRLF only |
| `platform_tests/scripts/test_check_harness_parity.py` | yes | no | yes | no - CRLF only |
| `platform_tests/scripts/test_check_sot_registry_completeness.py` | yes | no | yes | no - CRLF only |
| `platform_tests/scripts/test_implementation_start_gate.py` | yes | no | yes | no - CRLF only |
| `scripts/check_harness_parity.py` | yes | no | yes | no - CRLF only |
| `scripts/gtkb_file_reference_migration.py` | yes | no | yes | no - CRLF only |

**Four** files carry genuine `ruff format` drift introduced by WI-5441 - clean at
`HEAD`, still failing after LF normalization. The other **nine** fail on carriage
returns alone.

### Evidence 4 - the same root cause is already disclosed elsewhere in the thread

`-009` discloses a pre-existing baseline: the narrative-hook template parity
assertion failing at byte index 22, carriage return versus line feed, which that
report attributes to `.gitattributes` coverage. The defect is therefore already
observable in two independent places within the same work item.

### Correction to `-010` Finding F1

`-010` reached the correct verdict and this advisory does not dispute it. Its F1
states *"Thirteen changed Python files fail `ruff format --check` ... Every
corresponding HEAD version is format-clean, so all thirteen are [introduced]"*,
and its Required Revision 1 directs Prime Builder to *"Apply `ruff format` to the
thirteen files."*

The HEAD-clean observation is correct; the inference that all thirteen are
introduced is not, because it does not control for line endings. A HEAD blob is
LF and a Windows worktree file is CRLF, so that comparison is confounded for
every Python file in the repository.

**Risk of acting on the uncorrected instruction.** Running `ruff format` over all
thirteen rewrites the nine CRLF-only files to LF in the worktree. With no `*.py`
attribute governing normalization, that can register as a whole-file change in
nine files this work item never intended to touch - inflating the WI-5441 diff,
defeating the `-008` GO's declared 41-path discipline, and making the next
report's `## Files Changed` accounting harder to reconcile rather than easier.

### Secondary observation - draft claim TTL is shorter than a real verification

Two Loyal Opposition session contexts (`cc0eaa61-c6a0-41be-9db7-74f8c9f2e20e` and
`2c75ce6e-b998-48b9-bcb5-5d491ae1674b`) independently performed full
post-implementation verification of the same `-009` report and reached the same
NO-GO. Both re-ran the registry postimage, both journals, and six test suites.

`scripts/bridge_claim_cli.py claim` issues a `draft` claim with a 10-minute TTL.
A substantive post-implementation verification of a report this size runs well
past that - the registry postimage regeneration alone is ~36 seconds, and the six
test suites plus evidence reconciliation took considerably longer. The claim
expired mid-verification and did not prevent duplicated effort, which is the
outcome the claim mechanism exists to avoid. Offered for backlog capture, not
immediate implementation.

## Recommended Prime Action

File a normal implementation proposal for the gate fix. Three options:

### Option A - fix the gate to compare index content (preferred)

Change `check_files()` in `scripts/check_ruff_format.py` to feed the staged blob
to ruff instead of the worktree path, conceptually
`git show :0:<path>` piped to `ruff format --check --stdin-filename <path> -`.
This asserts exactly the bytes git will commit, which is what the gate is
semantically trying to check.

- Strengths: precise; no history churn; fixes every harness at once; matches what CI sees for committed content.
- Weaknesses: slightly more complex invocation; ruff driven per file rather than one batch call.
- Reversibility: high - contained to one function.

### Option B - add `*.py text eol=lf` to `.gitattributes`

- Strengths: one line; also likely clears the sibling narrative-hook byte-parity baseline.
- Weaknesses: triggers a one-time renormalization touching most Python files in the repository - a large, noisy commit that must itself clear the credential scan, inventory-drift, and narrative-evidence gates; does not fix the underlying "gate reads the wrong bytes" design.
- Reversibility: moderate - the renormalization commit is disruptive to revert.

### Option C - both, sequenced

Land Option A first so the Option B renormalization commit can actually pass the
gate.

**Recommendation: Option A now; Option B as a separately scheduled hygiene item.**
Option A is small, reversible, and unblocks the immediate failure class. Option B
is worth doing but should not be folded into an unrelated work item, and needs
its own owner-visible scheduling because of the diff size.

**For the WI-5441 revise cycle specifically:** apply `ruff format` to exactly the
four files with real drift -
`groundtruth-kb/src/groundtruth_kb/db.py`,
`groundtruth-kb/src/groundtruth_kb/hygiene/sweep.py`,
`scripts/check_protected_commit_authorization.py`,
`scripts/implementation_start_gate.py` - then re-run `ruff check` and
`ruff format --check` across the full changed set and report both. The nine
CRLF-only files need no content change; they need the gate fixed, which is this
advisory's subject and is not WI-5441's to carry.

## Owner Decision Needed

Yes. Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and
`.claude/rules/peer-solution-advisory-loop.md`, this advisory is classified
`adapt`, so Prime Builder must conduct an owner-grilling pass and capture durable
`AskUserQuestion` evidence before filing any derived implementation proposal.

**Implementation implied:** yes. Option A modifies `scripts/check_ruff_format.py`.
Option B modifies `.gitattributes` and triggers repository-wide renormalization.
Both are source mutations requiring a bridge proposal under an appropriate
project authorization. The correction to `-010` above is *not* implementation -
it is review information to apply within WI-5441's existing GO.

**Grill-the-owner questions:**

1. **Scope.** Fix the gate only (Option A), normalize `*.py` only (Option B), or both in sequence (Option C)?
2. **Renormalization scheduling.** If Option B is in scope, when should the repository-wide `*.py` renormalization land, given it produces a very large diff that must itself clear every commit gate? Should it be its own work item with its own authorization?
3. **Blast radius.** Option A changes a gate that currently blocks commits. Does the owner want a transitional period where the gate reports both old and new results before the old check is removed?
4. **Claim TTL.** Should the secondary observation become its own backlog item, or fold into whichever thread implements the gate fix?

**Required durable owner decisions before a derived proposal may be filed:**

- The Option A / B / C selection.
- Whether the `*.py` renormalization is in scope for the same work item or separately scheduled.
- Whether the claim-TTL observation is captured as a backlog item now.

## Classification Slot

**Classification: `adapt`.**

The core recommendation - stop comparing the wrong bytes - is adopted as stated.
The line-ending normalization half is adapted rather than adopted wholesale:
`.gitattributes` coverage is the obvious complete fix, but its renormalization
blast radius makes it a separately scheduled item rather than part of the gate
correction. Prime Builder should convert this into a scoped implementation
proposal after the owner-grilling gate above is satisfied.

This advisory carries no implementation authority. It does not authorize any
change to `scripts/check_ruff_format.py`, `.gitattributes`, `.githooks/pre-commit`,
or `scripts/bridge_claim_cli.py`. It does not dispute the `-010` NO-GO verdict; it
corrects one attribution inside it. It does not ask Prime Builder to absorb the
gate fix into WI-5441, whose revise cycle needs only the four-file reformat plus
the disclosures `-010` already lists.

## Prior Deliberations

Searched via `gt deliberations search`. No prior deliberation addresses the
`ruff format` gate's worktree-versus-index comparison or `*.py` line-ending
normalization; this appears to be a first surfacing. Adjacent context:

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - governing owner decision for the WI-5441 work in which the defect surfaced.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-009.md` - discloses the sibling CRLF/LF narrative-hook baseline and attributes it to `.gitattributes` coverage.
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-010.md` - the NO-GO whose F1 attribution this advisory corrects.

## Commands Executed

- `python .claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified ...` (the transaction whose pre-commit rejection surfaced the defect)
- `ruff format --check` and `ruff format --diff` against HEAD blobs, raw worktree bytes, and LF-normalized worktree bytes for all thirteen gate-reported files
- Inspection of `scripts/check_ruff_format.py`, `.gitattributes`, and `.githooks/pre-commit`
- `python scripts/bridge_claim_cli.py status gtkb-wi5441-global-registry-membership-reconciliation`
- `gt bridge state-report`
