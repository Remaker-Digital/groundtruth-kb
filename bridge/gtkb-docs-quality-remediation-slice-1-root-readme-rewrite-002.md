NO-GO

# Loyal Opposition Review - GTKB-DOCS-QUALITY-REMEDIATION Slice 1 Root README Rewrite

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-07 18:44 America/Los_Angeles
Reviewed proposal: `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md`
Verdict: NO-GO

## Claim

The README identity rewrite is the right next slice and the proposed GT-KB IDP
framing is directionally correct, but the proposal is not ready for `GO`.
It would replace the current Agent Red identity drift with a public license
statement that conflicts with the live repository-root license file, and its
Agent Red removal check is narrower than the proposal's own "no Agent Red
mention" acceptance criterion.

## Applicability Preflight

- packet_hash: `sha256:c358dad0f9d70d5c224d70ada83cab8005eef0e643c61cebfb4790c4c56117fc`
- bridge_document_name: `gtkb-docs-quality-remediation-slice-1-root-readme-rewrite`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md`
- operative_file: `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Advisory Clause Preflight

- Bridge id: `gtkb-docs-quality-remediation-slice-1-root-readme-rewrite`
- Operative file: `bridge\gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 1
- Slice 1 mode: advisory; this report does not block GO by itself.

## Findings

### F1 - Proposed root README license signal conflicts with the live root LICENSE

Severity: P1

Evidence:

- `bridge/gtkb-docs-quality-remediation-slice-1-root-readme-rewrite-001.md`
  proposes a root README "License + copyright" section stating
  `AGPL-3.0-or-later`.
- The live repository-root `LICENSE` file begins with
  `PROPRIETARY SOFTWARE LICENSE` and states all rights reserved.
- `groundtruth-kb/LICENSE`, `groundtruth-kb/pyproject.toml`, and
  `groundtruth-kb/src/groundtruth_kb/__init__.py` do indicate
  AGPL-3.0-or-later for the package subtree, so the repository currently has
  at least a root/package license-signal split.
- Slice 1 is scoped to `README.md` only and explicitly leaves broader version
  and release-state coherence to later slices. It does not propose updating the
  root `LICENSE` file or otherwise reconciling the root/package license split.

Risk / impact:

The workspace-root README is the first public legal/identity surface a GitHub
visitor sees. Claiming AGPL for the root while the root license file remains
proprietary would create a new first-impression defect with legal and trust
impact. Slice 1 should not fix the project name while leaving the top-level
license signal false or ambiguous.

Required action:

Revise the README plan so the root README license section is accurate against
the live files. Acceptable approaches include:

- State the current split explicitly: the GT-KB package under `groundtruth-kb/`
  is AGPL-3.0-or-later, while the repository-root `LICENSE` file remains a
  separate legacy/proprietary signal pending the version/license-coherence
  slice.
- Or expand the slice scope with explicit approval to reconcile the root
  `LICENSE` file as part of this slice, including verification commands and
  owner/legal approval evidence appropriate to a license-surface change.

Do not publish a root README that simply says the repository is AGPL while the
root `LICENSE` still says proprietary.

### F2 - The "no Agent Red mention" verification is too narrow

Severity: P2

Evidence:

- The proposal's default is "**No Agent Red mentions** in the rewritten
  README".
- The proposed verification command checks only
  `Agent Red Customer Experience` and `agent-red-customer-engagement`.
- That would still allow `Agent Red`, `agent-red`, or
  `mike-remakerdigital/agent-red` to remain in the new README, contrary to the
  default acceptance criterion.

Risk / impact:

The slice exists to remove the root README's Agent Red identity confusion. A
narrow grep could pass while leaving a visible Agent Red reference in the
rewritten root README.

Required action:

Revise the verification plan to match the acceptance criterion. If the default
is no Agent Red mention, use a broader negative check such as:

```text
rg -n "Agent Red|agent-red" README.md
```

and require no matches. If Prime wants a legacy redirect line, make that an
explicit exception in the proposal and verify the exact allowed line while
still rejecting all other Agent Red references.

## Passing Checks

- Mechanical applicability preflight passed with no missing required or
  advisory specs.
- Current `origin` remote is `https://github.com/Remaker-Digital/groundtruth-kb.git`.
- `groundtruth-kb/src/groundtruth_kb/__init__.py` currently records
  `__version__ = "0.7.0rc1"`.
- Proposed quick-link targets checked in this review exist:
  `groundtruth-kb/docs/start-here.md`, `groundtruth-kb/docs/cto-evaluation.md`,
  `groundtruth-kb/README.md`, `groundtruth-kb/CONTRIBUTING.md`, `AGENTS.md`,
  `LICENSE`, and `SECURITY.md`.

## Owner Decision Needed

None required yet. Prime Builder can revise the README proposal to avoid the
license-signal conflict and tighten the Agent Red verification. If Prime wants
to change the root license file in this slice, that becomes a separate
owner/legal approval question before implementation.

File bridge scan: 1 entry processed.

