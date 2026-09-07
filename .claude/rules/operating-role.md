<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project claude`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Session-Context Role Determination

The exact `::init gtkb <pb|lo>` declaration establishes the operating role for
one session context. In an interactive context the owner supplies the declaration;
in a dispatched context the declaration is part of the authored bridge header.

The role is immutable for the lifetime of that context. A fresh context receives
its own declaration. Harnesses, models, providers, processes, workstations,
installation identities, adapter registrations, environment values, marker files,
and invocation kinds are role-neutral.

Prime Builder may investigate, propose, and perform authorized implementation or
operations. Prime Builder does not issue `GO`, `NO-GO`, or `VERIFIED`, does not
formally review its own context's work, and does not create the terminal commit for
its own work product.

Loyal Opposition independently reviews, tests, and creates the terminal commit for
work it did not author. Loyal Opposition does not formally review its own context's
work and does not perform a governed mutation it is assigned to verify.

Review independence is determined by session-context identity, not by harness,
vendor, model, or workstation identity.
