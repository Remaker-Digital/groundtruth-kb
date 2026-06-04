GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T16-46Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition bridge review

# Loyal Opposition Verdict - Document Artifact Author Provenance Contract Revision

bridge_kind: loyal_opposition_verdict
Document: gtkb-document-author-provenance-contract
Version: 004
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-document-author-provenance-contract-003.md
Verdict: GO

## Verdict

GO.

The REVISED proposal resolves the authorization defects from
`bridge/gtkb-document-author-provenance-contract-002.md`. The work is no
longer routed through the reliability fast lane. It now cites a dedicated
feature-scope project authorization for `WI-3399` with mutation classes that
match the proposed source, test, hook, config-governance, governance-spec, and
formal-artifact insertion surfaces.

This GO authorizes implementation under the revised bridge scope. It does not
waive formal-artifact approval for inserting
`GOV-DOCUMENT-AUTHOR-PROVENANCE-001`.

## Mandatory Preflights

Commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-document-author-provenance-contract
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-document-author-provenance-contract
```

Observed result:

- Applicability preflight PASS.
- Packet hash: `sha256:e0a8bc7d3e18ac0e16f17294811290ff06ce2790db12b9dd20e524a4220ba528`.
- Missing required specs: none.
- Missing advisory specs: none.
- Clause preflight PASS.
- Clauses evaluated: 5.
- `must_apply`: 4.
- Blocking gaps: 0.

## Authorization Evidence

Readback confirmed:

- `DELIB-20260666` exists as an owner decision for the S414 AUQ chain.
- Project authorization
  `PAUTH-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE-WI-3399-FEATURE-FULL-AUTHORIZATION`
  exists, is active, version 1, and cites owner decision `DELIB-20260666`.
- The PAUTH includes `WI-3399`.
- `WI-3399` has active membership in
  `PROJECT-GTKB-DOCUMENT-AUTHOR-PROVENANCE`.
- Allowed mutation classes are `source`, `test_addition`, `hook_upgrade`,
  `config_governance`, `governance_spec_insertion`, and
  `formal_artifact_insertion`.
- Forbidden operations are `deploy`, `git_push_force`, and `spec_deletion`.

## Constraints For Implementation

1. Generate and cite the required formal-artifact approval packet before
   inserting `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`.
2. Keep implementation within the target paths named in the REVISED proposal.
3. Preserve the forward-only posture for existing document artifacts.
4. Verify Claude and Codex hook parity for the new provenance gate.
5. Include spec-derived tests for helper behavior, checker behavior, governed
   surface coverage, and hook blocking behavior.

## Residual Risk

The main remaining risk is operator friction when new governed-surface Markdown
files are blocked for missing provenance fields. That is acceptable for GO
because the owner explicitly selected all five surfaces and forward-only
enforcement, and the implementation plan includes a helper plus audit checker.

## Recommended Next Step

Prime Builder may implement the revised proposal, then file a post-
implementation report with targeted tests, ruff checks, formal spec readback,
and hook-registration evidence.
