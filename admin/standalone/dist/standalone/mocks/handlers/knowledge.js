// @ts-nocheck
/**
 * Mock handlers — Knowledge Base endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
export function registerKnowledgeHandlers() {
    const s = () => getStore().knowledge;
    GET('/api/admin/knowledge', (_req) => {
        const articles = s().articles;
        return { status: 200, body: { articles, total: articles.length } };
    });
    // Templates (used by OnboardingWizard) — MUST be before /:id to avoid being caught by parameterized route
    GET('/api/admin/knowledge/templates', (_req) => {
        return { status: 200, body: { templates: [] } };
    });
    POST('/api/admin/knowledge/templates/:id/apply', (_req) => {
        return { status: 200, body: { articlesCreated: 0, articlesFailed: 0, totalChars: 0 } };
    });
    // Staleness — MUST be before /:id
    GET('/api/admin/knowledge/staleness', (_req) => {
        return { status: 200, body: s().staleness };
    });
    GET('/api/admin/knowledge/stale', (_req) => {
        const stale = s().articles.filter((a) => a.stalenessCategory === 'aging' || a.stalenessCategory === 'stale');
        return { status: 200, body: { entries: stale, total: stale.length } };
    });
    // Export — MUST be before /:id
    GET('/api/admin/knowledge/export', (_req) => {
        return { status: 200, body: { csv: "id,title,category,status", filename: "knowledge-export.csv" } };
    });
    // Suggestions (used by OnboardingWizard) — MUST be before /:id
    GET('/api/admin/knowledge/suggestions', (_req) => {
        return { status: 200, body: { suggestions: [] } };
    });
    GET('/api/admin/knowledge/:id', (req) => {
        const article = s().articles.find((a) => a.id === req.params.id);
        if (!article)
            return { status: 404, body: { detail: 'Article not found' } };
        return { status: 200, body: article };
    });
    POST('/api/admin/knowledge', (req) => {
        const store = getStore();
        const id = 'kb-' + String(store.knowledge.articles.length + 1).padStart(3, '0');
        const article = {
            id, title: req.body?.title ?? 'New Article', content: req.body?.content ?? '',
            category: req.body?.category ?? 'general', status: 'draft',
            entryType: 'manual', is_active: true,
            createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
        };
        store.knowledge.articles.push(article);
        return { status: 201, body: article };
    });
    PUT('/api/admin/knowledge/:id', (req) => {
        const store = getStore();
        const idx = store.knowledge.articles.findIndex((a) => a.id === req.params.id);
        if (idx === -1)
            return { status: 404, body: { detail: 'Article not found' } };
        store.knowledge.articles[idx] = { ...store.knowledge.articles[idx], ...req.body, updatedAt: new Date().toISOString() };
        return { status: 200, body: store.knowledge.articles[idx] };
    });
    DELETE('/api/admin/knowledge/:id', (req) => {
        const store = getStore();
        store.knowledge.articles = store.knowledge.articles.filter((a) => a.id !== req.params.id);
        return { status: 200, body: { success: true } };
    });
    // Upload (simplified — returns success with mock entry IDs)
    POST('/api/admin/knowledge/upload', (_req) => {
        return {
            status: 200,
            body: {
                source_type: 'file', source_filename: 'uploaded-doc.pdf',
                entries_created: 3, total_chars: 4500,
                entry_ids: ['kb-upload-001', 'kb-upload-002', 'kb-upload-003'],
                parent_entry_id: 'kb-upload-001',
            },
        };
    });
    // Import from URL
    POST('/api/admin/knowledge/import-url', (req) => {
        return {
            status: 200,
            body: {
                source_type: 'url', source_url: req.body?.url ?? 'https://example.com',
                entries_created: 2, total_chars: 3200,
                entry_ids: ['kb-url-001', 'kb-url-002'],
                parent_entry_id: 'kb-url-001',
            },
        };
    });
    POST('/api/admin/knowledge/:id/verify', (req) => {
        const store = getStore();
        const article = store.knowledge.articles.find((a) => a.id === req.params.id);
        if (article) {
            article.lastVerifiedAt = new Date().toISOString();
            article.stalenessCategory = 'fresh';
            article.stalenessScore = 0;
        }
        return { status: 200, body: { success: true } };
    });
    // Conflict scan
    POST('/api/admin/knowledge/scan', (_req) => {
        return { status: 200, body: { conflicts: [], total: 0 } };
    });
    // Ingestion (used by OnboardingWizard)
    POST('/api/admin/knowledge/ingest', (_req) => {
        return { status: 200, body: { job_id: 'mock-job-001', status: 'completed' } };
    });
    GET('/api/admin/knowledge/ingest/status', (_req) => {
        return { status: 200, body: { job_id: 'mock-job-001', status: 'completed', progress: 100 } };
    });
}
//# sourceMappingURL=knowledge.js.map