# GroundTruth-KB Canonical Project URLs

Owner correction, 2026-05-03: casual references such as "the GitHub", "the
project GitHub", "repo", "the repo", "GitHub repo", "GT-KB GitHub", and
"GroundTruth-KB repo" must resolve through the project's configured GitHub
repository URL unless the owner explicitly scopes the reference otherwise.

Configured project GitHub repository URL:

- https://github.com/Remaker-Digital/groundtruth-kb

Agent Red is a separate project, not part of GT-KB. Its repository is:

- https://github.com/mike-remakerdigital/agent-red

GroundTruth-KB includes four small demo applications for validation/examples;
do not treat Agent Red as one of those in-root GT-KB demo applications.

Owner clarification, 2026-05-04: preserving historical Git data is not a
requirement for the next corrective push that establishes the separated
GroundTruth-KB and Agent Red repository identities. For that next push only, it
is acceptable to completely wipe either remote repository and push as if it were
the first release when that is the cleanest path to correct the prior repo
identity error. After that corrective push, use GitHub normally and preserve
history in the usual way. This is a one-time allowance, not a standing
instruction to perform a destructive remote rewrite without an explicit
execution request.

The April 10, 2026 change that treated a different repository as the active
project GitHub was an error. Do not infer the canonical project identity from a
local `origin` remote when it conflicts with owner-provided GroundTruth-KB
resource URLs, configured project-resource aliases, or the glossary. Surface
the mismatch as configuration drift and continue resolving project references
through the canonical GroundTruth-KB resource record.

This memory is linked from `.claude/rules/canonical-terminology.md` under
"GroundTruth-KB project resources".
