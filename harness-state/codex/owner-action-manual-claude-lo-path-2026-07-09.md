# Owner Decision: Use Manual Claude Code Loyal Opposition Review

## Decision Source

Owner Action Required fallback, 2026-07-09. Native AskUserQuestion was not
available in this Codex session. The owner directed: "I will use Claude Code
to manually process LO work until the bridge dispatcher is repaired."

## Decision

Use Claude Code manually for Loyal Opposition bridge work until the dispatcher
is repaired. The dispatcher remains disabled; this decision does not authorize
dispatcher repair or any configuration mutation.

Each manual Loyal Opposition review must begin in a distinct interactive Claude
Code session with explicit `::init gtkb lo` direction. The resulting session
context must be independent of the earlier Claude Prime Builder session that
authored the diagnosis and initial proposals. The manual LO session may review
successor NEW or REVISED proposals and post-implementation NEW reports, and
may issue GO, NO-GO, or VERIFIED only when its role and review-independence
checks pass.

## Rationale

The dispatcher has no dispatchable Prime Builder or Loyal Opposition target and
its daemon task remains disabled under the owner no-visible-console-windows
directive. Manual independent LO review keeps the canonical-authority
remediation moving without overriding that safeguard.

## Limits

Claude Code must not GO or VERIFY work it authored or implemented, and every
review remains subject to the full bridge, formal-artifact, and
specification-derived verification gates.
