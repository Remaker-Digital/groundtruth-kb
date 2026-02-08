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
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback, useMemo, useRef } from 'react';
import type { BaseComponentProps, KBArticle, KBArticleStatus, KBUploadResult } from './types';
import { useKnowledgeBase, useKBArticle, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useVerifyEntry } from './hooks';
import { HelpTooltip } from './HelpTooltip';

// ---------------------------------------------------------------------------
// Style constants
// ---------------------------------------------------------------------------

const BRAND_PRIMARY = '#ff3621';
const COLOR_SUCCESS = '#22863a';
const COLOR_DANGER = '#d73a49';
const COLOR_GRAY = '#6a737d';
const COLOR_LIGHT_GRAY = '#f6f8fa';
const COLOR_BORDER = '#e1e4e8';
const COLOR_WHITE = '#ffffff';
const COLOR_TEXT = '#24292e';
const COLOR_TEXT_SECONDARY = '#586069';
const COLOR_WARNING = '#e36209';
const FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";
const BORDER_RADIUS = '6px';

const STATUS_BADGE_STYLES: Record<KBArticleStatus, { bg: string; color: string; label: string }> = {
  draft: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Draft' },
  published: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Published' },
  archived: { bg: COLOR_LIGHT_GRAY, color: COLOR_GRAY, label: 'Archived' },
};

const STALENESS_BADGE_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  fresh: { bg: '#dcffe4', color: COLOR_SUCCESS, label: 'Fresh' },
  aging: { bg: '#fff8c5', color: COLOR_WARNING, label: 'Aging' },
  stale: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Stale' },
  very_stale: { bg: '#ffeef0', color: COLOR_DANGER, label: 'Very Stale' },
};

const ALL_STATUSES: Array<{ value: '' | KBArticleStatus; label: string }> = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'published', label: 'Published' },
  { value: 'archived', label: 'Archived' },
];

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}

function extractCategories(articles: KBArticle[]): string[] {
  const set = new Set<string>();
  for (const a of articles) {
    if (a.category) set.add(a.category);
  }
  return Array.from(set).sort();
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const KBStatusBadge: React.FC<{ status: KBArticleStatus; isActive?: boolean }> = ({ status, isActive }) => {
  // Backend may return is_active (boolean) instead of status (string).
  // Derive status from is_active if status is missing.
  const effectiveStatus: KBArticleStatus = status ?? (isActive === false ? 'archived' : 'published');
  const style = STATUS_BADGE_STYLES[effectiveStatus] ?? STATUS_BADGE_STYLES.published;
  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: '11px',
        fontWeight: 600,
        padding: '2px 8px',
        borderRadius: '10px',
        backgroundColor: style.bg,
        color: style.color,
      }}
    >
      {style.label}
    </span>
  );
};

const KBStalenessBadge: React.FC<{ category: string | null | undefined }> = ({ category }) => {
  if (!category) {
    return (
      <span
        style={{
          display: 'inline-block',
          fontSize: '11px',
          fontWeight: 600,
          padding: '2px 8px',
          borderRadius: '10px',
          backgroundColor: COLOR_LIGHT_GRAY,
          color: COLOR_GRAY,
        }}
      >
        --
      </span>
    );
  }
  const style = STALENESS_BADGE_STYLES[category] ?? STALENESS_BADGE_STYLES.fresh;
  return (
    <span
      style={{
        display: 'inline-block',
        fontSize: '11px',
        fontWeight: 600,
        padding: '2px 8px',
        borderRadius: '10px',
        backgroundColor: style.bg,
        color: style.color,
      }}
    >
      {style.label}
    </span>
  );
};

const LoadingSpinner: React.FC<{ text?: string }> = ({ text = 'Loading...' }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 16px',
      color: COLOR_TEXT_SECONDARY,
    }}
  >
    <div
      style={{
        width: '32px',
        height: '32px',
        border: `3px solid ${COLOR_BORDER}`,
        borderTopColor: BRAND_PRIMARY,
        borderRadius: '50%',
        animation: 'kbSpin 0.8s linear infinite',
        marginBottom: '12px',
      }}
    />
    <span style={{ fontSize: '14px' }}>{text}</span>
    <style>{`@keyframes kbSpin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

const EmptyState: React.FC<{ icon: string; title: string; subtitle?: string }> = ({ icon, title, subtitle }) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 16px',
      color: COLOR_TEXT_SECONDARY,
    }}
  >
    <span style={{ fontSize: '40px', marginBottom: '12px' }}>{icon}</span>
    <span style={{ fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }}>{title}</span>
    {subtitle && <span style={{ fontSize: '13px' }}>{subtitle}</span>}
  </div>
);

const ErrorBanner: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div
    style={{
      padding: '12px 16px',
      backgroundColor: '#ffeef0',
      border: `1px solid ${COLOR_DANGER}33`,
      borderRadius: BORDER_RADIUS,
      margin: '16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '12px',
    }}
  >
    <span style={{ fontSize: '13px', color: COLOR_DANGER }}>{message}</span>
    {onRetry && (
      <button
        onClick={onRetry}
        style={{
          padding: '4px 12px',
          border: `1px solid ${COLOR_DANGER}`,
          borderRadius: BORDER_RADIUS,
          backgroundColor: 'transparent',
          color: COLOR_DANGER,
          fontSize: '12px',
          fontFamily: FONT_FAMILY,
          cursor: 'pointer',
          whiteSpace: 'nowrap',
        }}
      >
        Retry
      </button>
    )}
  </div>
);

// Shared input style factory
function inputStyle(extraStyles?: React.CSSProperties): React.CSSProperties {
  return {
    width: '100%',
    padding: '8px 12px',
    border: `1px solid ${COLOR_BORDER}`,
    borderRadius: BORDER_RADIUS,
    fontSize: '14px',
    fontFamily: FONT_FAMILY,
    backgroundColor: COLOR_WHITE,
    color: COLOR_TEXT,
    boxSizing: 'border-box' as const,
    ...extraStyles,
  };
}

function buttonStyle(variant: 'primary' | 'secondary' | 'danger', disabled = false): React.CSSProperties {
  const base: React.CSSProperties = {
    padding: '8px 16px',
    borderRadius: BORDER_RADIUS,
    fontSize: '13px',
    fontFamily: FONT_FAMILY,
    fontWeight: 500,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    transition: 'opacity 0.15s ease',
    border: 'none',
  };

  if (variant === 'primary') {
    return { ...base, backgroundColor: BRAND_PRIMARY, color: COLOR_WHITE };
  }
  if (variant === 'danger') {
    return { ...base, backgroundColor: COLOR_DANGER, color: COLOR_WHITE };
  }
  return {
    ...base,
    backgroundColor: COLOR_WHITE,
    color: COLOR_TEXT,
    border: `1px solid ${COLOR_BORDER}`,
  };
}

// ---------------------------------------------------------------------------
// File upload sub-component
// ---------------------------------------------------------------------------

const ACCEPTED_TYPES = '.pdf,.docx,.csv,.txt';
const ACCEPTED_LABELS = 'PDF, DOCX, CSV, TXT';
const MAX_FILE_SIZE_MB = 50;

interface FileUploadZoneProps {
  onFileSelected: (file: File) => void;
  uploading: boolean;
  progress: 'idle' | 'uploading' | 'processing' | 'done';
  error: string | null;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({ onFileSelected, uploading, progress, error }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (uploading) return;
      const file = e.dataTransfer.files?.[0];
      if (file) onFileSelected(file);
    },
    [onFileSelected, uploading],
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onFileSelected(file);
      if (inputRef.current) inputRef.current.value = '';
    },
    [onFileSelected],
  );

  const progressLabel = progress === 'uploading' ? 'Uploading...' : progress === 'processing' ? 'Processing document...' : '';

  return (
    <div>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && inputRef.current?.click()}
        style={{
          border: `2px dashed ${dragOver ? BRAND_PRIMARY : COLOR_BORDER}`,
          borderRadius: BORDER_RADIUS,
          padding: '40px 24px',
          textAlign: 'center' as const,
          cursor: uploading ? 'default' : 'pointer',
          backgroundColor: dragOver ? `${BRAND_PRIMARY}08` : COLOR_LIGHT_GRAY,
          transition: 'all 0.2s ease',
          opacity: uploading ? 0.7 : 1,
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <div style={{ fontSize: '32px', marginBottom: '8px' }}>
          {uploading ? String.fromCodePoint(0x23F3) : String.fromCodePoint(0x1F4C4)}
        </div>
        {uploading ? (
          <div>
            <span style={{ fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }}>{progressLabel}</span>
            <div style={{ marginTop: '12px' }}>
              <div style={{
                width: '200px', height: '4px', backgroundColor: COLOR_BORDER,
                borderRadius: '2px', margin: '0 auto', overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%', backgroundColor: BRAND_PRIMARY,
                  width: progress === 'uploading' ? '40%' : '80%',
                  transition: 'width 0.5s ease',
                  borderRadius: '2px',
                }} />
              </div>
            </div>
          </div>
        ) : (
          <>
            <span style={{ fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }}>
              Drop a file here or click to browse
            </span>
            <br />
            <span style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '4px', display: 'inline-block' }}>
              Supported: {ACCEPTED_LABELS} (max {MAX_FILE_SIZE_MB}MB)
            </span>
          </>
        )}
      </div>
      {error && (
        <div style={{
          marginTop: '8px', padding: '8px 12px', backgroundColor: '#ffeef0',
          border: `1px solid ${COLOR_DANGER}33`, borderRadius: BORDER_RADIUS,
          fontSize: '13px', color: COLOR_DANGER,
        }}>
          {error}
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// URL import sub-component
// ---------------------------------------------------------------------------

interface URLImportFormProps {
  onImport: (url: string, crawl: boolean, maxPages: number) => void;
  importing: boolean;
  error: string | null;
}

const URLImportForm: React.FC<URLImportFormProps> = ({ onImport, importing, error }) => {
  const [url, setUrl] = useState('');
  const [crawl, setCrawl] = useState(false);
  const [maxPages, setMaxPages] = useState(10);

  const handleSubmit = useCallback(() => {
    const trimmed = url.trim();
    if (!trimmed) return;
    onImport(trimmed, crawl, maxPages);
  }, [url, crawl, maxPages, onImport]);

  return (
    <div>
      <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '6px' }}>
        Website URL
      </label>
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/faq"
          style={inputStyle({ flex: '1' })}
          disabled={importing}
        />
        <button
          onClick={handleSubmit}
          disabled={!url.trim() || importing}
          style={buttonStyle('primary', !url.trim() || importing)}
        >
          {importing ? 'Importing...' : 'Import'}
        </button>
      </div>

      {/* Import mode: single page vs crawl */}
      <div style={{ marginTop: '12px', display: 'flex', gap: '16px', alignItems: 'center' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: COLOR_TEXT, cursor: 'pointer' }}>
          <input
            type="radio"
            name="crawl_mode"
            checked={!crawl}
            onChange={() => setCrawl(false)}
            disabled={importing}
            style={{ accentColor: BRAND_PRIMARY }}
          />
          Single page
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: COLOR_TEXT, cursor: 'pointer' }}>
          <input
            type="radio"
            name="crawl_mode"
            checked={crawl}
            onChange={() => setCrawl(true)}
            disabled={importing}
            style={{ accentColor: BRAND_PRIMARY }}
          />
          Crawl site
          <HelpTooltip text="Follow links on the same domain and import multiple pages automatically." />
        </label>

        {crawl && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label style={{ fontSize: '12px', color: COLOR_TEXT_SECONDARY, whiteSpace: 'nowrap' as const }}>
              Max pages:
            </label>
            <input
              type="number"
              value={maxPages}
              onChange={(e) => {
                const v = parseInt(e.target.value, 10);
                if (!isNaN(v)) setMaxPages(Math.max(1, Math.min(50, v)));
              }}
              min={1}
              max={50}
              disabled={importing}
              style={inputStyle({ width: '70px', padding: '4px 8px', fontSize: '13px' })}
            />
          </div>
        )}
      </div>

      <span style={{ display: 'block', fontSize: '12px', color: COLOR_TEXT_SECONDARY, marginTop: '8px' }}>
        {crawl
          ? `We'll follow same-domain links and import up to ${maxPages} pages.`
          : "We'll extract text content from the page and create knowledge base entries."}
      </span>
      {error && (
        <div style={{
          marginTop: '8px', padding: '8px 12px', backgroundColor: '#ffeef0',
          border: `1px solid ${COLOR_DANGER}33`, borderRadius: BORDER_RADIUS,
          fontSize: '13px', color: COLOR_DANGER,
        }}>
          {error}
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Upload result display sub-component
// ---------------------------------------------------------------------------

interface UploadResultDisplayProps {
  result: KBUploadResult;
  onDone: () => void;
}

const UploadResultDisplay: React.FC<UploadResultDisplayProps> = ({ result, onDone }) => (
  <div style={{
    padding: '24px', backgroundColor: '#dcffe4', border: `1px solid ${COLOR_SUCCESS}33`,
    borderRadius: BORDER_RADIUS, textAlign: 'center' as const,
  }}>
    <div style={{ fontSize: '32px', marginBottom: '8px' }}>{String.fromCodePoint(0x2705)}</div>
    <div style={{ fontSize: '15px', fontWeight: 600, color: COLOR_TEXT, marginBottom: '4px' }}>
      Import Successful
    </div>
    <div style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY, marginBottom: '16px' }}>
      Created {result.entries_created} {result.entries_created === 1 ? 'entry' : 'entries'} from{' '}
      {result.source_filename || result.source_url || 'document'}{' '}
      ({Math.round(result.total_chars / 1000)}K characters)
    </div>
    <button onClick={onDone} style={buttonStyle('primary')}>
      Back to Knowledge Base
    </button>
  </div>
);

// ---------------------------------------------------------------------------
// Editor sub-component
// ---------------------------------------------------------------------------

interface ArticleEditorProps {
  article: Partial<KBArticle>;
  categories: string[];
  saving: boolean;
  saveError: string | null;
  onSave: (article: Partial<KBArticle>) => void;
  onDelete: (id: string) => void;
  onCancel: () => void;
  deleting: boolean;
}

const ArticleEditor: React.FC<ArticleEditorProps> = ({
  article,
  categories,
  saving,
  saveError,
  onSave,
  onDelete,
  onCancel,
  deleting,
}) => {
  const [title, setTitle] = useState(article.title || '');
  const [content, setContent] = useState(article.content || '');
  const [category, setCategory] = useState(article.category || '');
  const [status, setStatus] = useState<KBArticleStatus>(article.status || 'draft');
  const [newCategory, setNewCategory] = useState('');
  const [showNewCategory, setShowNewCategory] = useState(false);

  const isNew = !article.id;
  const canSave = title.trim().length > 0 && content.trim().length > 0 && (category.trim().length > 0 || newCategory.trim().length > 0);

  const handleSubmit = useCallback(() => {
    const resolvedCategory = showNewCategory ? newCategory.trim() : category;
    if (!title.trim() || !content.trim() || !resolvedCategory) return;

    onSave({
      ...(article.id ? { id: article.id } : {}),
      title: title.trim(),
      content: content.trim(),
      category: resolvedCategory,
      status,
      // Backend requires entry_type — default to 'custom' for manual articles
      entry_type: 'custom',
      // Pass category as metadata for backend storage
      metadata: { category: resolvedCategory },
    });
  }, [article.id, title, content, category, newCategory, showNewCategory, status, onSave]);

  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }}>
          {isNew ? 'New Article' : 'Edit Article'}
        </h2>
        <button onClick={onCancel} style={buttonStyle('secondary')}>
          Back to List
        </button>
      </div>

      {saveError && (
        <div
          style={{
            padding: '10px 14px',
            backgroundColor: '#ffeef0',
            border: `1px solid ${COLOR_DANGER}33`,
            borderRadius: BORDER_RADIUS,
            marginBottom: '16px',
            fontSize: '13px',
            color: COLOR_DANGER,
          }}
        >
          {saveError}
        </div>
      )}

      {/* Title */}
      <div style={{ marginBottom: '16px' }}>
        <label
          style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: 600,
            color: COLOR_TEXT,
            marginBottom: '6px',
          }}
        >
          Title <span style={{ color: COLOR_DANGER }}>*</span>
          <HelpTooltip text="A clear, descriptive title helps the AI match articles to customer questions." />
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Article title..."
          style={inputStyle()}
        />
      </div>

      {/* Category */}
      <div style={{ marginBottom: '16px' }}>
        <label
          style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: 600,
            color: COLOR_TEXT,
            marginBottom: '6px',
          }}
        >
          Category <span style={{ color: COLOR_DANGER }}>*</span>
        </label>
        {!showNewCategory ? (
          <div style={{ display: 'flex', gap: '8px' }}>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={inputStyle({ flex: '1' })}
            >
              <option value="">Select category...</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <button
              onClick={() => setShowNewCategory(true)}
              style={buttonStyle('secondary')}
              title="Create new category"
            >
              + New
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="New category name..."
              style={inputStyle({ flex: '1' })}
            />
            <button
              onClick={() => {
                setShowNewCategory(false);
                setNewCategory('');
              }}
              style={buttonStyle('secondary')}
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Status */}
      <div style={{ marginBottom: '16px' }}>
        <label
          style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: 600,
            color: COLOR_TEXT,
            marginBottom: '6px',
          }}
        >
          Status
        </label>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as KBArticleStatus)}
          style={inputStyle({ width: '200px' })}
        >
          <option value="draft">Draft</option>
          <option value="published">Published</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {/* Content */}
      <div style={{ marginBottom: '24px' }}>
        <label
          style={{
            display: 'block',
            fontSize: '13px',
            fontWeight: 600,
            color: COLOR_TEXT,
            marginBottom: '6px',
          }}
        >
          Content <span style={{ color: COLOR_DANGER }}>*</span>
          <HelpTooltip text="The full article text the AI will reference when answering questions." />
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write article content..."
          rows={14}
          style={inputStyle({ resize: 'vertical' as const, lineHeight: '1.6' })}
        />
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          {!isNew && !confirmDelete && (
            <button
              onClick={() => setConfirmDelete(true)}
              style={buttonStyle('danger')}
            >
              Delete
            </button>
          )}
          {!isNew && confirmDelete && (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <span style={{ fontSize: '13px', color: COLOR_DANGER, fontWeight: 500 }}>
                Are you sure?
              </span>
              <button
                disabled={deleting}
                onClick={() => {
                  if (article.id) onDelete(article.id);
                }}
                style={buttonStyle('danger', deleting)}
              >
                {deleting ? 'Deleting...' : 'Confirm Delete'}
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                style={buttonStyle('secondary')}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={onCancel} style={buttonStyle('secondary')}>
            Cancel
          </button>
          <button
            disabled={!canSave || saving}
            onClick={handleSubmit}
            style={buttonStyle('primary', !canSave || saving)}
          >
            {saving ? 'Saving...' : isNew ? 'Create Article' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Article list row
// ---------------------------------------------------------------------------

interface ArticleRowProps {
  article: KBArticle;
  onClick: () => void;
  onVerify?: (id: string) => void;
  verifying?: boolean;
}

const ArticleRow: React.FC<ArticleRowProps> = ({ article, onClick, onVerify, verifying }) => (
  <tr
    onClick={onClick}
    style={{ cursor: 'pointer', transition: 'background-color 0.15s ease' }}
    onMouseEnter={(e) => {
      (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_LIGHT_GRAY;
    }}
    onMouseLeave={(e) => {
      (e.currentTarget as HTMLElement).style.backgroundColor = COLOR_WHITE;
    }}
  >
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <span style={{ fontSize: '14px', fontWeight: 500, color: COLOR_TEXT }}>{article.title}</span>
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <span
        style={{
          fontSize: '12px',
          color: COLOR_TEXT_SECONDARY,
          backgroundColor: COLOR_LIGHT_GRAY,
          padding: '2px 8px',
          borderRadius: '10px',
        }}
      >
        {article.category || 'Uncategorized'}
      </span>
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <KBStatusBadge status={article.status} isActive={article.is_active} />
    </td>
    <td style={{ padding: '12px 16px', borderBottom: `1px solid ${COLOR_BORDER}` }}>
      <KBStalenessBadge category={article.stalenessCategory} />
    </td>
    <td
      style={{
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOR_BORDER}`,
        fontSize: '13px',
        color: COLOR_TEXT_SECONDARY,
      }}
    >
      {formatDate(article.updatedAt)}
    </td>
    <td
      style={{
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOR_BORDER}`,
      }}
    >
      {onVerify && (article.stalenessCategory === 'stale' || article.stalenessCategory === 'aging' || article.stalenessCategory === 'very_stale') && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onVerify(article.id);
          }}
          disabled={verifying}
          style={{
            padding: '4px 10px',
            border: `1px solid ${COLOR_SUCCESS}`,
            borderRadius: BORDER_RADIUS,
            backgroundColor: 'transparent',
            color: COLOR_SUCCESS,
            fontSize: '11px',
            fontFamily: FONT_FAMILY,
            fontWeight: 500,
            cursor: verifying ? 'not-allowed' : 'pointer',
            opacity: verifying ? 0.6 : 1,
            whiteSpace: 'nowrap' as const,
          }}
        >
          {verifying ? 'Verifying...' : 'Verify'}
        </button>
      )}
    </td>
  </tr>
);

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
              <HelpTooltip text="Upload PDF, DOCX, CSV, or TXT files to automatically create knowledge base entries." />
            </h2>
            <button onClick={() => { setView('list'); refetchKB(); }} style={buttonStyle('secondary')}>
              Back to List
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
                    {tab === 'file' ? 'Upload File' : 'Import URL'}
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
            <HelpTooltip text="Articles, FAQs, and policies that the AI searches to answer customer questions. Keep it accurate and up to date." />
          </h2>
          <span style={{ fontSize: '13px', color: COLOR_TEXT_SECONDARY }}>
            {articles.length} article{articles.length !== 1 ? 's' : ''}
            {filteredArticles.length !== articles.length && ` (${filteredArticles.length} shown)`}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleExport}
            disabled={exporting || articles.length === 0}
            style={buttonStyle('secondary', exporting || articles.length === 0)}
          >
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
          <button onClick={handleOpenImport} style={buttonStyle('secondary')}>
            Import
          </button>
          <HelpTooltip text="Import multiple articles at once from a CSV file." />
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
          placeholder="Search by title..."
          style={inputStyle({ width: '240px', flex: 'none' })}
        />

        {/* Category filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          style={inputStyle({ width: '180px', flex: 'none' })}
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>

        {/* Status filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as '' | KBArticleStatus)}
          style={inputStyle({ width: '160px', flex: 'none' })}
        >
          {ALL_STATUSES.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>

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
                  <HelpTooltip text="Organize articles by topic for easier management. The AI uses categories to narrow searches." />
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
                  <HelpTooltip text="Draft articles are not used by the AI. Publish when ready." />
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
                  <HelpTooltip text="How recently the article content has been verified. Stale articles may contain outdated information." />
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
    </div>
  );
};

export default KnowledgeBaseManager;
