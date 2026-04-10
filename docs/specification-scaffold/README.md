# Specification Scaffold

This directory contains the foundational specification templates and boilerplate specifications used to bootstrap new projects built on the groundtruth-kb knowledge database.

## Contents

| File | Purpose |
|------|---------|
| `SPEC-TEMPLATE.md` | Canonical specification format with all fields documented |
| `initial-specifications.json` | ~25 boilerplate specs to seed a new project's KB |
| `intake-checklist.md` | Step-by-step checklist for specification intake at project start |

## Usage

### Starting a New Project

1. Initialize a groundtruth-kb instance: `gt project init --profile dual-agent`
2. Review `SPEC-TEMPLATE.md` to understand the specification format
3. Import `initial-specifications.json` into the KB:
   ```python
   from groundtruth_kb import KnowledgeDB
   import json

   db = KnowledgeDB("path/to/knowledge.db")
   with open("initial-specifications.json") as f:
       specs = json.load(f)
   for spec in specs:
       db.insert_spec(**spec)
   ```
4. Walk through `intake-checklist.md` with the project owner
5. Begin elaborating functional and non-functional requirements iteratively

### Adapting for Your Project

The boilerplate specs are intentionally generic. After import:
- Review each governance spec and adjust thresholds (e.g., coverage minimums)
- Replace placeholder architecture decisions with project-specific choices
- Add domain-specific foundational requirements
- Update protected behaviors to match your data model

## Specification Lifecycle

```
specified  -->  implemented  -->  verified  -->  (retired)
```

- **specified**: Requirement defined and agreed with owner, not yet built
- **implemented**: Code exists that satisfies the spec
- **verified**: Tests pass and assertions confirm correctness
- **retired**: No longer applicable (preserved for audit trail)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
