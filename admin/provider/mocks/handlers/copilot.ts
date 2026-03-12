// @ts-nocheck
/**
 * Mock handlers — Provider Co-Pilot knowledge management.
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerCopilotHandlers(): void {
  // Documents CRUD
  GET('/api/superadmin/copilot/documents', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { documents: getStore().copilot.documents } };
  });

  POST('/api/superadmin/copilot/documents', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    const doc = {
      id: `doc-${String(store.copilot.nextDocId).padStart(3, '0')}`,
      title: body.title, source: body.source || 'manual', url: body.url || null,
      status: 'pending', chunkCount: 0, lastEmbeddedAt: null, createdAt: new Date().toISOString(),
    };
    store.copilot.documents.push(doc);
    store.copilot.nextDocId += 1;
    return { status: 201, body: doc };
  });

  PUT('/api/superadmin/copilot/documents/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.copilot.documents.findIndex(d => d.id === req.params.id);
    if (idx === -1) return { status: 404, body: { detail: 'Document not found' } };
    store.copilot.documents[idx] = { ...store.copilot.documents[idx], ...req.body };
    return { status: 200, body: store.copilot.documents[idx] };
  });

  DELETE('/api/superadmin/copilot/documents/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.copilot.documents = store.copilot.documents.filter(d => d.id !== req.params.id);
    return { status: 200, body: {} };
  });

  // Ingestion
  POST('/api/superadmin/copilot/ingest/docs-site', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { docsIngested: 12 } };
  });

  POST('/api/superadmin/copilot/ingest/url', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { urlIngested: true } };
  });

  POST('/api/superadmin/copilot/re-embed', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { reEmbedded: 1 } };
  });

  // Stats
  GET('/api/superadmin/copilot/stats', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().copilot.stats };
  });

  // Test query
  POST('/api/superadmin/copilot/test-query', (req: MockRequest): MockResponse => {
    const body = req.body as Record<string, unknown>;
    return {
      status: 200,
      body: {
        results: [
          { title: "Getting Started Guide", chunk: "To get started with Agent Red...", score: 0.92 },
          { title: "API Reference", chunk: "The /api/config endpoint allows...", score: 0.85 },
        ],
        query: body.query,
      },
    };
  });

  // Config — schedule
  GET('/api/superadmin/copilot/config/schedule', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().copilot.config.schedule };
  });

  PUT('/api/superadmin/copilot/config/schedule', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    store.copilot.config.schedule = { ...store.copilot.config.schedule, ...body };
    return { status: 200, body: store.copilot.config.schedule };
  });

  // Config — retrieval
  GET('/api/superadmin/copilot/config/retrieval', (_req: MockRequest): MockResponse => {
    return { status: 200, body: getStore().copilot.config.retrieval };
  });

  PUT('/api/superadmin/copilot/config/retrieval', (req: MockRequest): MockResponse => {
    const store = getStore();
    const body = req.body as Record<string, unknown>;
    store.copilot.config.retrieval = { ...store.copilot.config.retrieval, ...body };
    return { status: 200, body: store.copilot.config.retrieval };
  });
}
