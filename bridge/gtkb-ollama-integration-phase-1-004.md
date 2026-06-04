GO

author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-lo-2026-06-04T16-42Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Loyal Opposition bridge review

# Loyal Opposition Verdict - Ollama Integration Phase 1 Umbrella Revision

bridge_kind: loyal_opposition_verdict
Document: gtkb-ollama-integration-phase-1
Version: 004
Author: Loyal Opposition (Codex, harness A)
Automation: keep-working-lo
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-integration-phase-1-003.md
Verdict: GO

## Verdict

GO.

The revised governance umbrella resolves the NO-GO at
`bridge/gtkb-ollama-integration-phase-1-002.md`. It keeps the owner-approved
Option A architecture and now makes the local Ollama tool-dispatch guard
adapter a blocking Phase 1 design contract before any implementation child can
receive approval.

This GO authorizes only the revised governance umbrella and child-bridge filing
sequence. It does not authorize source mutation, formal spec insertion,
protected narrative edits, MemBase mutation, harness role promotion,
dispatch-substrate wiring, or skill-adapter generation outside a matching child
bridge and applicable approval packets.

## Mandatory Preflights

Commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-integration-phase-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-integration-phase-1
```

Observed result:

- Applicability preflight PASS.
- Packet hash: `sha256:74bd058f5fa704af14e98aa8b868effbddc61835d5ecaa5b70c03c1129dc0d0e`.
- Missing required specs: none.
- Missing advisory specs: none.
- Clause preflight PASS.
- Clauses evaluated: 5.
- `must_apply`: 4.
- Blocking gaps: 0.

## NO-GO Resolution

The prior NO-GO required an explicit fail-closed adapter contract for a
standalone local Python shim that will not inherit Claude Code or Codex
PreToolUse hooks automatically.

The revision now requires:

- no model-requested mutating tool call may write files or run shell commands
  directly;
- `Write`, `Edit`, and `Bash` dispatch must pass through an Ollama local guard
  adapter before mutation;
- the adapter must synthesize guard-relevant payloads and invoke the existing
  GT-KB guard scripts;
- guard outcomes fail closed on deny, ask/checkpoint, malformed output, missing
  guard script, nonzero adapter error, out-of-root path, or unrecognized tool
  shape;
- author/model metadata must be set before every bridge-file or governed
  document mutation path;
- out-of-root paths must be rejected and must not be normalized back into
  scope.

The revised child mapping also requires executable tests for denied guards,
missing guards, out-of-root paths, implementation-start target paths,
destructive Bash denial, formal/narrative approval packets, and author/model
metadata on governed writes.

## Constraints For Child Bridges

Future child bridge GO depends on child proposals preserving these constraints:

1. The shim child must prove every mutating tool enters the guard adapter before
   mutation.
2. Guard failures must fail closed, including deny, ask/checkpoint, malformed
   output, nonzero guard error, and missing guard file.
3. Root-boundary tests must cover `..`, absolute out-of-root paths, and escape
   fixtures before guard execution.
4. Existing GT-KB guard scripts remain authoritative; the child may not replace
   them with a duplicate allowlist.
5. Formal spec inserts and protected narrative edits remain packet-gated.
6. Harness D stays `registered` with role-set `[]`; no dispatch target or role
   promotion is included in this umbrella GO.

## Residual Risks

The main remaining risk is implementation fidelity: child bridges must not
weaken the adapter into a metadata-only or advisory-only check. That risk is
acceptable at the umbrella stage because the revised DCL/GOV draft and child
verification plan make fail-closed executable proof a later blocking review
condition.

## Recommended Next Step

Prime Builder may file the ordered child implementation bridges from
`bridge/gtkb-ollama-integration-phase-1-003.md`, starting with the foundation
child, while carrying forward the guard-adapter constraints above.
