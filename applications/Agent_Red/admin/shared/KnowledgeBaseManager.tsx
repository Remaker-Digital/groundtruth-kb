// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * KnowledgeBaseManager - CRUD manager for knowledge base articles.
 *
 * List view: all KB articles with title, category, status badge, last updated.
 * Editor view: title, content textarea, category dropdown, status select.
 * Filtering: category dropdown, status filter, search by title.
 * Actions: create, edit, save, delete.
 *
 * Framework-agnostic React component — no Polaris, no Tailwind, pure inline styles.
 * Receives auth, API fetch, and notification callbacks from the shell.
 *
 * Sub-components and utilities are extracted into ./kb/ for maintainability.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useMemo } from 'react';
import type { BaseComponentProps, KBArticle, KBArticleStatus, KBUploadResult } from './types';
import { useKnowledgeBase, useKBArticle, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useVerifyEntry, useConflictScan } from './hooks';
import type { ConflictPair, ScanResult } from './hooks';
import { HelpTooltip } from './HelpTooltip';

// Sub-components extracted into ./kb/
import {
  // Style constants & helpers
  BRAND_PRIMARY,
  COLOR_SUCCESS,
  COLOR_DANGER,
  COLOR_GRAY,
  COLOR_LIGHT_GRAY,
  COLOR_BORDER,
  COLOR_WHITE,
  COLOR_TEXT,
  COLOR_TEXT_SECONDARY,
  COLOR_WARNING,
  FONT_FAMILY,
  BORDER_RADIUS,
  inputStyle,
  buttonStyle,
  // Utilities
  extractCategories,
  // Components
  KBStatusBadge,
  KBStalenessBadge,
  FileUploadZone,
  URLImportForm,
  UploadResultDisplay,
  ArticleEditor,
  ArticleRow,
  LoadingSpinner,
  EmptyState,
  ErrorBanner,
  WebsiteSourcesPanel,
} from './kb';

// ---------------------------------------------------------------------------
// Filter option constants
// ---------------------------------------------------------------------------

const ALL_STATUSES: Array<{ value: '' | KBArticleStatus; label: string }> = [
  { value: '', label: 'All statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'published', label: 'Published' },
  { value: 'archived', label: 'Archived' },
];

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const KnowledgeBaseManager: React.FC<BaseComponentProps> = ({
  tenantContext,
  apiFetch,
  onNotify,
}) => {
  // View state: 'list', 'editor', or 'import'
  const [view, setView] = useState<'list' | 'editor' | 'import'>('list');
  const [kbTab, setKbTab] = useState<'articles' | 'sources'>('articles');
  const [editingArticle, setEditingArticle] = useState<Partial<KBArticle> | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [uploadResult, setUploadResult] = useState<KBUploadResult | null>(null);
  const [importTab, setImportTab] = useState<'file' | 'url'>('file');

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<'' | KBArticleStatus>('');

  // Data hooks
  const {
    data: kbData,
    loading: kbLoading,
    error: kbError,
    refetch: refetchKB,
  } = useKnowledgeBase(apiFetch);
  const articles = kbData?.articles ?? [];

  // Save hook
  const { save, loading: saving, error: saveError } = useSaveKBArticle(apiFetch);

  // Upload/import/export hooks
  const { upload: uploadFile, loading: uploading, error: uploadError, progress: uploadProgress, reset: resetUpload } = useUploadFile(apiFetch);
  const { importUrl, loading: importing, error: importError } = useImportUrl(apiFetch);
  const { exportCSV, loading: exporting, error: exportError } = useExportCSV(apiFetch);

  // Staleness hooks
  const { data: stalenessData, refetch: refetchStaleness } = useStalenessSummary(apiFetch);
  const { verify, loading: verifying } = useVerifyEntry(apiFetch);

  // Conflict scanner hooks
  const { scan: runConflictScan, result: scanResult, loading: scanning, error: scanError } = useConflictScan(apiFetch);
  const [showScanResults, setShowScanResults] = useState(false);
  const [dismissedPairs, setDismissedPairs] = useState<Set<string>>(new Set());

  // Extract categories from articles for the filter dropdown and editor
  const categories = useMemo(() => extractCategories(articles), [articles]);

  // Filter articles
  const filteredArticles = useMemo(() => {
    let result = articles;

    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      result = result.filter((a) => a.title.toLowerCase().includes(q));
    }

    if (categoryFilter) {
      result = result.filter((a) => a.category === categoryFilter);
    }

    if (statusFilter) {
      result = result.filter((a) => a.status === statusFilter);
    }

    return result;
  }, [articles, searchQuery, categoryFilter, statusFilter]);

  // Handlers
  const handleOpenNew = useCallback(() => {
    setEditingArticle({ title: '', content: '', category: '', status: 'draft' });
    setView('editor');
  }, []);

  const handleOpenImport = useCallback(() => {
    setUploadResult(null);
    resetUpload();
    setImportTab('file');
    setView('import');
  }, [resetUpload]);

  const handleFileUpload = useCallback(
    async (file: File) => {
      const result = await uploadFile(file);
      if (result) {
        setUploadResult(result);
        onNotify(`Imported ${result.entries_created} entries from ${file.name}`, 'success');
      } else {
        onNotify('File upload failed', 'error');
      }
    },
    [uploadFile, onNotify],
  );

  const handleUrlImport = useCallback(
    async (url: string, crawl: boolean, maxPages: number) => {
      const result = await importUrl(url, undefined, crawl, maxPages);
      if (result) {
        setUploadResult(result);
        const label = crawl ? `Crawled and imported ${result.entries_created} entries` : `Imported ${result.entries_created} entries from URL`;
        onNotify(label, 'success');
      } else {
        onNotify('URL import failed', 'error');
      }
    },
    [importUrl, onNotify],
  );

  const handleImportDone = useCallback(() => {
    setUploadResult(null);
    setView('list');
    refetchKB();
  }, [refetchKB]);

  const handleExport = useCallback(async () => {
    const ok = await exportCSV();
    if (ok) {
      onNotify('Knowledge base exported as CSV', 'success');
    } else {
      onNotify(exportError || 'Export failed', 'error');
    }
  }, [exportCSV, exportError, onNotify]);

  const handleVerify = useCallback(
    async (entryId: string) => {
      const result = await verify(entryId);
      if (result) {
        onNotify('Article verified as current', 'success');
        refetchKB();
        refetchStaleness();
      } else {
        onNotify('Failed to verify article', 'error');
      }
    },
    [verify, onNotify, refetchKB, refetchStaleness],
  );

  const handleOpenEdit = useCallback(
    (article: KBArticle) => {
      setEditingArticle(article);
      setView('editor');
    },
    [],
  );

  const handleCancel = useCallback(() => {
    setEditingArticle(null);
    setView('list');
  }, []);

  const handleSave = useCallback(
    async (article: Partial<KBArticle>) => {
      const result = await save(article);
      if (result) {
        onNotify(
          article.id ? 'Article updated successfully' : 'Article created successfully',
          'success',
        );
        refetchKB();
        setEditingArticle(null);
        setView('list');
      } else {
        onNotify('Failed to save article', 'error');
      }
    },
    [save, onNotify, refetchKB],
  );

  const handleDelete = useCallback(
    async (articleId: string) => {
      setDeleting(true);
      try {
        const resp = await apiFetch(`/api/admin/knowledge/${articleId}`, { method: 'DELETE' });
        if (!resp.ok) throw new Error(`${resp.status}`);
        onNotify('Article deleted', 'success');
        refetchKB();
        setEditingArticle(null);
        setView('list');
      } catch {
        onNotify('Failed to delete article', 'error');
      } finally {
        setDeleting(false);
      }
    },
    [apiFetch, onNotify, refetchKB],
  );

  // Editor view
  if (view === 'editor' && editingArticle !== null) {
    return (
      <div
        style={{
          fontFamily: FONT_FAMILY,
          border: `1px solid ${COLOR_BORDER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: COLOR_WHITE,
          minHeight: '500px',
        }}
      >
        <ArticleEditor
          article={editingArticle}
          categories={categories}
          saving={saving}
          saveError={saveError}
          onSave={handleSave}
          onDelete={handleDelete}
          onCancel={handleCancel}
          deleting={deleting}
        />
      </div>
    );
  }

  // Import view
  if (view === 'import') {
    return (
      <div
        style={{
          fontFamily: FONT_FAMILY,
          border: `1px solid ${COLOR_BORDER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: COLOR_WHITE,
          minHeight: '500px',
        }}
      >
        <div style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }}>
              Import Content
              <HelpTooltip text="Upload PDF, DOCX, CSV, or TXT files to automatically create knowledge base entries." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#uploading-documents" />
            </h2>
            <button onClick={() => { setView('list'); refetchKB(); }} style={buttonStyle('secondary')}>
              Back to list
            </button>
          </div>

          {uploadResult ? (
            <UploadResultDisplay result={uploadResult} onDone={handleImportDone} />
          ) : (
            <>
              {/* Tab selector */}
              <div style={{ display: 'flex', gap: '0', marginBottom: '24px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
                {(['file', 'url'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setImportTab(tab)}
                    style={{
                      padding: '10px 20px',
                      border: 'none',
                      borderBottom: importTab === tab ? `2px solid ${BRAND_PRIMARY}` : '2px solid transparent',
                      backgroundColor: 'transparent',
                      color: importTab === tab ? BRAND_PRIMARY : COLOR_TEXT_SECONDARY,
                      fontWeight: importTab === tab ? 600 : 400,
                      fontSize: '14px',
                      fontFamily: FONT_FAMILY,
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {tab === 'file' ? 'Upload file' : 'Import URL'}
                  </button>
                ))}
              </div>

              {importTab === 'file' ? (
                <FileUploadZone
                  onFileSelected={handleFileUpload}
                  uploading={uploading}
                  progress={uploadProgress}
                  error={uploadError}
                />
              ) : (
                <URLImportForm
                  onImport={handleUrlImport}
                  importing={importing}
                  error={importError}
                />
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  // List view
  return (
    <div
      style={{
        fontFamily: FONT_FAMILY,
        border: `1px solid ${COLOR_BORDER}`,
        borderRadius: BORDER_RADIUS,
        backgroundColor: COLOR_WHITE,
        minHeight: '500px',
      }}
    >
      {/* KB section tabs */}
      <div style={{ display: 'flex', gap: '0', borderBottom: `1px solid ${COLOR_BORDER}` }}>
        {([
          { key: 'articles' as const, label: 'Articles' },
          { key: 'sources' as const, label: 'Website Sources' },
        ]).map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setKbTab(key)}
            style={{
              padding: '12px 24px',
              border: 'none',
              borderBottom: kbTab === key ? `2px solid ${BRAND_PRIMARY}` : '2px solid transparent',
              backgroundColor: 'transparent',
              color: kbTab === key ? BRAND_PRIMARY : COLOR_TEXT_SECONDARY,
              fontWeight: kbTab === key ? 600 : 400,
              fontSize: '14px',
              fontFamily: FONT_FAMILY,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Website Sources tab */}
      {kbTab === 'sources' && (
        <WebsiteSourcesPanel apiFetch={apiFetch} onNotify={onNotify} />
      )}

      {/* Articles tab */}
      {kbTab === 'articles' && <>
      {/* Header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: `1px solid ${COLOR_BORDER}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }}>
            Knowledge Base
            <HelpTooltip text="Articles, FAQs, and policies that the AI searches to answer customer questions. Keep it accurate and up to date." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management" />
          </h2>
          <span style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
            {articles.length} article{articles.length !== 1 ? 's' : ''}
            {filteredArticles.length !== articles.length && ` (${filteredArticles.length} shown)`}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }}>
            <button
              onClick={async () => {
                const res = await runConflictScan(true);
                if (res) setShowScanResults(true);
              }}
              disabled={scanning || articles.length < 2}
              style={buttonStyle('secondary', scanning || articles.length < 2)}
            >
              {scanning ? 'Scanning...' : 'Scan for conflicts'}
            </button>
            <HelpTooltip text="Detect duplicate, overlapping, or contradictory knowledge base entries that may cause inconsistent AI responses." docLink="https://agentredcx.com/docs/admin-guide/conflict-scanner" />
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }}>
            <button
              onClick={handleExport}
              disabled={exporting || articles.length === 0}
              style={buttonStyle('secondary', exporting || articles.length === 0)}
            >
              {exporting ? 'Exporting...' : 'Export CSV'}
            </button>
            <HelpTooltip text="Download all knowledge base entries as a CSV file for backup or editing." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base" />
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 2 }}>
            <button onClick={handleOpenImport} style={buttonStyle('secondary')}>
              Import
            </button>
            <HelpTooltip text="Upload PDF, DOCX, CSV, or TXT files, or import from a URL to bulk-create knowledge base entries." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base" />
          </span>
          <button onClick={handleOpenNew} style={buttonStyle('primary')}>
            + New Article
          </button>
        </div>
      </div>

      {/* Staleness summary banner */}
      {stalenessData && (stalenessData.staleCount > 0 || stalenessData.veryStaleCount > 0) && (
        <div
          style={{
            padding: '10px 20px',
            borderBottom: `1px solid ${COLOR_BORDER}`,
            backgroundColor: '#ffeef0',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            fontSize: '13px',
          }}
        >
          <span style={{ color: COLOR_DANGER, fontWeight: 600 }}>
            {stalenessData.staleCount + stalenessData.veryStaleCount} article{(stalenessData.staleCount + stalenessData.veryStaleCount) !== 1 ? 's' : ''} need attention
          </span>
          <span style={{ color: COLOR_TEXT_SECONDARY }}>
            {stalenessData.freshCount} fresh, {stalenessData.agingCount} aging, {stalenessData.staleCount} stale
            {stalenessData.veryStaleCount > 0 && `, ${stalenessData.veryStaleCount} very stale`}
          </span>
        </div>
      )}

      {/* Conflict scan results panel */}
      {showScanResults && scanResult && (
        <div style={{
          padding: '16px 20px',
          borderBottom: `1px solid ${COLOR_BORDER}`,
          backgroundColor: COLOR_LIGHT_GRAY,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontWeight: 600, fontSize: '14px', color: COLOR_TEXT }}>
                Conflict scan results
              </span>
              {scanResult.highCount > 0 && (
                <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: '#ffeef0', color: COLOR_DANGER }}>
                  {scanResult.highCount} high
                </span>
              )}
              {scanResult.mediumCount > 0 && (
                <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: '#fff8c5', color: COLOR_WARNING }}>
                  {scanResult.mediumCount} medium
                </span>
              )}
              {scanResult.lowCount > 0 && (
                <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, backgroundColor: COLOR_LIGHT_GRAY, color: COLOR_GRAY }}>
                  {scanResult.lowCount} low
                </span>
              )}
              {scanResult.conflicts.length === 0 && (
                <span style={{ fontSize: '13px', color: COLOR_SUCCESS, fontWeight: 600 }}>
                  No conflicts found
                </span>
              )}
              <span style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY }}>
                {scanResult.totalEntriesScanned} entries scanned in {scanResult.scanDurationMs}ms
                {scanResult.entriesWithoutEmbeddings > 0 && ` (${scanResult.entriesWithoutEmbeddings} not yet embedded)`}
              </span>
            </div>
            <button
              onClick={() => setShowScanResults(false)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: COLOR_GRAY, fontSize: '16px', padding: '4px' }}
            >
              {String.fromCodePoint(0x2715)}
            </button>
          </div>

          {scanResult.conflicts.filter(c => !dismissedPairs.has(`${c.entryAId}-${c.entryBId}`)).map((conflict, idx) => {
            const pairKey = `${conflict.entryAId}-${conflict.entryBId}`;
            const severityColors: Record<string, { bg: string; color: string }> = {
              high: { bg: '#ffeef0', color: COLOR_DANGER },
              medium: { bg: '#fff8c5', color: COLOR_WARNING },
              low: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY },
            };
            const sev = severityColors[conflict.severity] || severityColors.low;
            const typeLabels: Record<string, string> = {
              near_duplicate: 'Near-duplicate',
              conflicting: 'Conflicting info',
              topical_overlap: 'Topical overlap',
              similar_titles: 'Similar titles',
            };
            return (
              <div
                key={pairKey}
                style={{
                  padding: '12px 16px',
                  marginBottom: '8px',
                  borderRadius: BORDER_RADIUS,
                  border: `1px solid ${COLOR_BORDER}`,
                  backgroundColor: COLOR_WHITE,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, backgroundColor: sev.bg, color: sev.color }}>
                        {conflict.severity.toUpperCase()}
                      </span>
                      <span style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, fontWeight: 500 }}>
                        {typeLabels[conflict.conflictType] || conflict.conflictType}
                      </span>
                      <span style={{ fontSize: '11px', color: COLOR_TEXT_SECONDARY }}>
                        Similarity: {Math.round(conflict.embeddingSimilarity * 100)}% | Overlap: {Math.round(conflict.contentOverlap * 100)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: COLOR_TEXT, marginBottom: '4px' }}>
                      <strong>{conflict.entryATitle}</strong>
                      <span style={{ color: COLOR_TEXT_SECONDARY, margin: '0 6px' }}>vs</span>
                      <strong>{conflict.entryBTitle}</strong>
                    </div>
                    {conflict.conflictingFacts.length > 0 && (
                      <div style={{ fontSize: '12px', color: COLOR_DANGER, marginBottom: '4px' }}>
                        {conflict.conflictingFacts.map((fact, fi) => (
                          <div key={fi}>{String.fromCodePoint(0x26A0)} {fact}</div>
                        ))}
                      </div>
                    )}
                    <div style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, lineHeight: '1.5' }}>
                      {conflict.resolution}
                    </div>
                  </div>
                  <button
                    onClick={() => setDismissedPairs(prev => new Set([...prev, pairKey]))}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: COLOR_GRAY, fontSize: '12px', padding: '4px 8px', marginLeft: '12px', whiteSpace: 'nowrap' }}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            );
          })}

          {scanError && (
            <div style={{ fontSize: '13px', color: COLOR_DANGER, marginTop: '8px' }}>
              Scan error: {scanError}
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div
        style={{
          padding: '12px 20px',
          borderBottom: `1px solid ${COLOR_BORDER}`,
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
          flexWrap: 'wrap',
          backgroundColor: COLOR_LIGHT_GRAY,
        }}
      >
        {/* Search */}
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search articles..."
          aria-label="Search articles by title"
          style={inputStyle({ width: '240px', flex: 'none' })}
        />

        {/* Category filter */}
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' }}
            title="Filter articles by category"
          >
            Category
          </span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={inputStyle({ width: '160px', flex: 'none' })}
            aria-label="Filter by category"
            title="Filter articles by category"
          >
            <option value="">All</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </label>

        {/* Status filter */}
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' }}
            title="Filter articles by publication status"
          >
            Status
          </span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as '' | KBArticleStatus)}
            style={inputStyle({ width: '140px', flex: 'none' })}
            aria-label="Filter by status"
            title="Filter articles by publication status"
          >
            {ALL_STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>

        {/* Clear filters */}
        {(searchQuery || categoryFilter || statusFilter) && (
          <button
            onClick={() => {
              setSearchQuery('');
              setCategoryFilter('');
              setStatusFilter('');
            }}
            style={{
              padding: '6px 12px',
              border: 'none',
              borderRadius: BORDER_RADIUS,
              backgroundColor: 'transparent',
              color: BRAND_PRIMARY,
              fontSize: '12px',
              fontFamily: FONT_FAMILY,
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Content area */}
      {kbLoading && articles.length === 0 && (
        <LoadingSpinner text="Loading articles..." />
      )}

      {kbError && articles.length === 0 && (
        <ErrorBanner message={kbError} onRetry={refetchKB} />
      )}

      {!kbLoading && !kbError && articles.length === 0 && (
        <EmptyState
          icon={String.fromCodePoint(0x1F4DA)}
          title="No articles yet"
          subtitle="Create your first knowledge base article to help your AI agent answer customer questions."
        />
      )}

      {!kbLoading && !kbError && articles.length > 0 && filteredArticles.length === 0 && (
        <EmptyState
          icon={String.fromCodePoint(0x1F50D)}
          title="No matching articles"
          subtitle="Try adjusting your search query or filters."
        />
      )}

      {filteredArticles.length > 0 && (
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '14px',
            }}
          >
            <thead>
              <tr style={{ backgroundColor: COLOR_LIGHT_GRAY }}>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                >
                  Title
                </th>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    width: '160px',
                  }}
                >
                  Category
                  <HelpTooltip text="Organize articles by topic for easier management. The AI uses categories to narrow searches." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#organizing-with-categories" />
                </th>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    width: '110px',
                  }}
                >
                  Status
                  <HelpTooltip text="Draft articles are not used by the AI. Publish when ready." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#article-status-lifecycle" />
                </th>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    width: '100px',
                  }}
                >
                  Freshness
                  <HelpTooltip text="How recently the article content has been verified. Stale articles may contain outdated information." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#staleness-and-freshness" />
                </th>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    width: '140px',
                  }}
                >
                  Last Updated
                </th>
                <th
                  style={{
                    padding: '10px 16px',
                    textAlign: 'left',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: COLOR_TEXT_SECONDARY,
                    borderBottom: `1px solid ${COLOR_BORDER}`,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    width: '90px',
                  }}
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredArticles.map((article) => (
                <ArticleRow
                  key={article.id}
                  article={article}
                  onClick={() => handleOpenEdit(article)}
                  onVerify={handleVerify}
                  verifying={verifying}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
      </>}
    </div>
  );
};

export default KnowledgeBaseManager;
