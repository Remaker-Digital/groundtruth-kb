# Owner Decision: Replace Scope-Defective Canonical-Authority Carrier Work

## Decision Source

Owner Action Required fallback, 2026-07-09. Native AskUserQuestion was not
available in this Codex session. The owner selected option `1` (`replace`).

## Decision

Retire WI-5120 and WI-5121 because their latest GO proposals cannot legally
create the GOV/DCL carriers required by their work-item descriptions: each
omits `groundtruth.db` from `target_paths` and declares
`kb_mutation_in_scope: false`.

Create successor work items under
`PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION`, with fresh project
authorization and NEW bridge proposals. Each successor proposal must include
every actual mutation surface, including `groundtruth.db`, its narrative or
template targets, required formal-artifact approval packets, and
specification-derived verification.

## Rationale

The live bridge gate states that project authorization does not broaden a GO'd
proposal's `target_paths`; implementation-start validation denies KB mutation
outside that scope. Proceeding under the existing GO files would therefore
misrepresent authorization and could not satisfy the project's definition of
done.

## Limits

This decision authorizes the governed recovery path only. It does not authorize
protected-file implementation, bridge verdicts, or verification without the
required successor authorization, independent Loyal Opposition review, formal
approval packets, and live GO verdicts.
