// @ts-nocheck
/**
 * Mock handlers — Knowledge Base endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerKnowledgeHandlers(): void {
  const s = () => getStore().knowledge;

  GET('/api/admin/knowledge', (_req: MockRequest): MockResponse => {
    const articles = s().articles;
    return { status: 200, body: { articles, total: articles.length } };
  });

  GET('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const article = s().articles.find((a: Record<string, unknown>) => a.id === req.params.id);
    if (!article) return { status: 404, body: { detail: 'Article not found' } };
    return { status: 200, body: article };
  });

  POST('/api/admin/knowledge', (req: MockRequest): MockResponse => {
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

  PUT('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.knowledge.articles.findIndex((a: Record<string, unknown>) => a.id === req.params.id);
    if (idx === -1) return { status: 404, body: { detail: 'Article not found' } };
    store.knowledge.articles[idx] = { ...store.knowledge.articles[idx], ...req.body, updatedAt: new Date().toISOString() };
    return { status: 200, body: store.knowledge.articles[idx] };
  });

  DELETE('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.knowledge.articles = store.knowledge.articles.filter((a: Record<string, unknown>) => a.id !== req.params.id);
    return { status: 200, body: { success: true } };
  });

  // Upload (simplified — returns success with mock entry IDs)
  POST('/api/admin/knowledge/upload', (_req: MockRequest): MockResponse => {
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
  POST('/api/admin/knowledge/import-url', (req: MockRequest): MockResponse => {
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

  // Export
  GET('/api/admin/knowledge/export', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { csv: "id,title,category,status", filename: "knowledge-export.csv" } };
  });

  // Staleness
  GET('/api/admin/knowledge/staleness', (_req: MockRequest): MockResponse => {
    return { status: 200, body: s().staleness };
  });

  GET('/api/admin/knowledge/stale', (_req: MockRequest): MockResponse => {
    const stale = s().articles.filter((a: Record<string, unknown>) => a.stalenessCategory === 'aging' || a.stalenessCategory === 'stale');
    return { status: 200, body: { entries: stale, total: stale.length } };
  });

  POST('/api/admin/knowledge/:id/verify', (req: MockRequest): MockResponse => {
    const store = getStore();
    const article = store.knowledge.articles.find((a: Record<string, unknown>) => a.id === req.params.id);
    if (article) {
      (article as Record<string, unknown>).lastVerifiedAt = new Date().toISOString();
      (article as Record<string, unknown>).stalenessCategory = 'fresh';
      (article as Record<string, unknown>).stalenessScore = 0;
    }
    return { status: 200, body: { success: true } };
  });

  // Conflict scan
  POST('/api/admin/knowledge/scan', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { conflicts: [], total: 0 } };
  });
}
