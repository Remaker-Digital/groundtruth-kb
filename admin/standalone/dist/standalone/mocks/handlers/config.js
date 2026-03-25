// @ts-nocheck
/**
 * Mock handlers — Config endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
export function registerConfigHandlers() {
    const s = () => getStore().config;
    // Draft config
    GET('/api/config', (_req) => {
        return { status: 200, body: { config: s().draft, version: s().draftVersion, tier: 'professional', fromCache: false } };
    });
    PUT('/api/config', (req) => {
        const fields = req.body?.fields ?? {};
        const store = getStore();
        store.config.draft = { ...store.config.draft, ...fields };
        store.config.draftVersion += 1;
        store.config.activationStatus.has_pending_changes = true;
        store.config.activationStatus.draft_version = store.config.draftVersion;
        const changes = Object.keys(fields).map(k => ({ field: k, before: null, after: fields[k] }));
        return { status: 200, body: { success: true, version: store.config.draftVersion, changes, message: 'Config updated' } };
    });
    // Schema
    GET('/api/config/schema', (_req) => {
        return { status: 200, body: { fields: s().schema } };
    });
    GET('/api/config/schema/:step', (_req) => {
        return { status: 200, body: { fields: [] } };
    });
    // Versions
    GET('/api/config/versions', (_req) => {
        return { status: 200, body: { versions: s().versions } };
    });
    // Named configs
    GET('/api/config/named', (_req) => {
        return { status: 200, body: { configs: s().namedConfigs, total: s().namedConfigs.length } };
    });
    POST('/api/config/named', (req) => {
        const name = req.body?.name ?? 'Unnamed';
        const store = getStore();
        const existing = store.config.namedConfigs.find((c) => c.name === name);
        if (existing) {
            existing.version = existing.version + 1;
        }
        else {
            store.config.namedConfigs.push({
                name, version: 1, isActive: false, isDefault: false,
                createdAt: new Date().toISOString(), createdBy: 'mock-user', fieldCount: Object.keys(store.config.draft).length,
            });
        }
        return { status: 200, body: { success: true, version: 1, changes: [], message: 'Named config saved' } };
    });
    POST('/api/config/named/:name/activate', (req) => {
        const name = decodeURIComponent(req.params.name);
        const store = getStore();
        store.config.namedConfigs.forEach((c) => { c.isActive = c.name === name; });
        return { status: 200, body: { success: true, version: 1, changes: [], message: 'Activated ' + name } };
    });
    DELETE('/api/config/named/:name', (req) => {
        const name = decodeURIComponent(req.params.name);
        const store = getStore();
        store.config.namedConfigs = store.config.namedConfigs.filter((c) => c.name !== name);
        return { status: 200, body: { success: true } };
    });
    // Activation status (also registered by tenant handler, this is an alias)
    GET('/api/config/activation-status', (_req) => {
        return { status: 200, body: s().activationStatus };
    });
    // Draft state
    GET('/api/config/draft', (_req) => {
        return {
            status: 200,
            body: {
                has_pending_changes: s().activationStatus.has_pending_changes,
                active_version: s().activationStatus.active_version,
                active_activated_at: s().activationStatus.active_activated_at,
                draft_version: s().draftVersion,
                changed_fields: [],
                draft_config: s().draft,
                active_config: s().draft,
            },
        };
    });
    POST('/api/config/draft/activate', (_req) => {
        const store = getStore();
        store.config.activationStatus.has_pending_changes = false;
        store.config.activationStatus.active_version = store.config.draftVersion;
        store.config.activationStatus.active_activated_at = new Date().toISOString();
        return { status: 200, body: { success: true, message: 'Draft activated' } };
    });
    POST('/api/config/draft/discard', (_req) => {
        const store = getStore();
        store.config.activationStatus.has_pending_changes = false;
        store.config.activationStatus.draft_version = store.config.activationStatus.active_version;
        return { status: 200, body: { success: true, message: 'Draft discarded' } };
    });
    POST('/api/config/restore', (_req) => {
        return { status: 200, body: { success: true, message: 'Previous config restored' } };
    });
    // Widget appearances
    GET('/api/config/widget-appearances', (_req) => {
        return { status: 200, body: { configs: s().widgetAppearances } };
    });
    POST('/api/config/widget-appearances', (req) => {
        const name = req.body?.name ?? 'Unnamed';
        const store = getStore();
        store.config.widgetAppearances.push({
            name, version: 1, isActive: false, isDefault: false,
            createdAt: new Date().toISOString(), createdBy: 'mock-user', fieldCount: 5,
        });
        return { status: 200, body: { success: true } };
    });
    POST('/api/config/widget-appearances/:name/activate', (req) => {
        const name = decodeURIComponent(req.params.name);
        const store = getStore();
        store.config.widgetAppearances.forEach((c) => { c.isActive = c.name === name; });
        return { status: 200, body: { success: true } };
    });
    DELETE('/api/config/widget-appearances/:name', (req) => {
        const name = decodeURIComponent(req.params.name);
        const store = getStore();
        store.config.widgetAppearances = store.config.widgetAppearances.filter((c) => c.name !== name);
        return { status: 200, body: { success: true } };
    });
    // Widget key rotation
    POST('/api/keys/rotate-widget-key', (_req) => {
        const newKey = 'pk_live_mock_' + Math.random().toString(36).slice(2, 18);
        return { status: 200, body: { newWidgetKey: newKey, message: 'Widget key rotated' } };
    });
}
//# sourceMappingURL=config.js.map