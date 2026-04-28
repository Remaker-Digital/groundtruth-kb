# UI Testing — Operational Patterns

> Full reference: KB DOC-UI-TESTING

## Chrome MCP Patterns
- **Auth injection:** `sessionStorage.setItem('agentred_api_key', KEY)` (merchant), `sessionStorage.setItem('agentred_provider_key', KEY)` (SPA)
- **Per-test:** navigate → wait 2s → console errors → find/read_page → screenshot → record
- **Known:** Discard button clicks cause Chrome MCP disconnections (recovery: 15-90s wait → tabs_context_mcp)
- **Data-binding:** Backend `CamelCaseModel` → all API fields are camelCase. TS interfaces MUST match.

## Terminology (Owner-Corrected, S47)
- **SPA** = Service Provider Administrator (person), NOT "Single Page Application"
- **SPA Console** = Provider Console at `/admin/provider`
- **Superadmin / Admin** = Merchant users (customers)
- **Standalone Admin** = Merchant admin at `/admin/standalone`
