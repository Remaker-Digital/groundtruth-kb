---
name: Production deploy requires explicit approval
description: Never start a production deploy based on ambiguous "continue" — require explicit "yes, deploy to production" from owner
type: feedback
---

Production deployments require explicit owner approval with the word "production" in the confirmation. Do not interpret "please continue" or "yes" to a multi-option question as production deploy authorization.

**Why:** In S267, I started a production deploy based on ambiguous "Please continue" after presenting production deploy as one of several next steps. The owner had to request a rollback. The deploy itself was premature — Phase 2A code hadn't been Codex-reviewed as implementation, ACS SMS wasn't verified in production, and Phase 3 wasn't in the build.

**How to apply:** Before any `deploy.py production` command, explicitly state "I'm about to deploy v{X} to production" and wait for a response that specifically confirms production deployment. If the owner says "continue" in a context with multiple pending tasks, work on the non-production tasks.
