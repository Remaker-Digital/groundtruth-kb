# Read current terminology

Canonical definitions are current database records served by the native CLI.
This rule explains retrieval; it does not contain a second glossary.

Use `gt terms list --status active --scope platform` for the current platform
vocabulary, `gt terms show <id>` for a complete record, and
`gt authority resolve "<term>" --scope <scope>` for an ID, canonical name or
accepted spelling. Read the returned definition, formal source and service
pointers. Use the work item's current task context for applicable formal intent.

An ambiguous name requires a scope or exact record ID. A malformed entry or
inactive formal source requires correction for that subject. Other valid
subjects remain available. `gt authority status --json` identifies current
ambiguities and source defects. An unavailable authority does not permit
reusing definitions from a generated file, earlier session or local cache.

Owner terminology changes are applied to the affected current formal and term
records. Session logs retain the conversation when later harvest is useful.
Reasoning notes do not supply decisions, permission or lifecycle authority.

Formal retrieval anchors: GOV-ARTIFACT-AUTHORITY-HIERARCHY-001,
GOV-GLOSSARY-AS-DA-READ-SURFACE-001, DCL-CONCEPT-ON-CONTACT-001,
DCL-CANONICAL-CARRIER-NONAUTHORITY-001.
