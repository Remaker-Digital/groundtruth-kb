GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-lo-autoproc-2026-06-25
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Loyal Opposition auto-process

bridge_kind: proposal_review
Document: gtkb-index-md-strip-skill-docs
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-25 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-index-md-strip-skill-docs-001.md
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4799
Recommended commit type: fix

## Applicability Preflight

- preflight_passed: `true`
- missing_required_specs: []

## Review Summary

Proposal is **correct, bounded, and well-governed**. S3 skill-doc/template surfaces are already compliant (guard-aware KEEP notes only); the **only load-bearing residue** is two stale `test_cli.py` assertions deferred from WI-4798. Scope correction is accepted.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| Two `test_cli.py` assertions fail | pass | independent pytest `FF` on L411 + L452 |
| Templates stripped of `bridge/INDEX.md` | pass | `groundtruth-kb/templates/` grep → zero matches |
| Skill mirrors guard-aware KEEP only | pass | `.claude`/`.codex` `bridge-reconciliation/SKILL.md` cite INDEX only in "do not treat as live" notes |
| Single-file fix (`not in` flip) | pass | matches adjacent retired-mechanism negatives L453–454 |
| Deferred from S2 tranche | pass | `gtkb-index-md-strip-tests` GO scope note |

## Scope Note Ruling

**Accepted:** residue = two deferred stale tests in `groundtruth-kb/tests/test_cli.py`; flipping `in` → `not in` is preferred over deletion (preserves scaffold contract checks).

## Residual Risks

- Low: single-file, two assertion flips. Deprecated poller scaffold artifact is correctly out of scope.

## Prior Deliberations

- `gtkb-index-md-classified-inventory` GO — S3 classification contract.
- `gtkb-index-md-strip-tests` / WI-4798 — deferred `test_cli.py` assertions.
- `gtkb-index-md-strip-docs` / WI-4797 — S1 peer.

## Verdict Rationale

**GO** — spec-derived verification plan complete; implementation may proceed after claim + `implementation_authorization.py begin`.
