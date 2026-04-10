// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * ArticleEditor — create / edit form for a single KB article.
 * Handles title, category (existing or new), status, content textarea,
 * save, and delete with confirmation.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import type { KBArticle, KBArticleStatus } from '../types';
import { HelpTooltip } from '../HelpTooltip';
import {
  COLOR_TEXT,
  COLOR_DANGER,
  BORDER_RADIUS,
  inputStyle,
  buttonStyle,
} from './styles';

export interface ArticleEditorProps {
  article: Partial<KBArticle>;
  categories: string[];
  saving: boolean;
  saveError: string | null;
  onSave: (article: Partial<KBArticle>) => void;
  onDelete: (id: string) => void;
  onCancel: () => void;
  deleting: boolean;
}

export const ArticleEditor: React.FC<ArticleEditorProps> = ({
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
      entryType: 'custom',
    });
  }, [article.id, title, content, category, newCategory, showNewCategory, status, onSave]);

  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: COLOR_TEXT }}>
          {isNew ? 'New article' : 'Edit article'}
        </h2>
        <button onClick={onCancel} style={buttonStyle('secondary')}>
          Back to list
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
          <HelpTooltip text="A clear, descriptive title helps the AI match articles to customer questions." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#article-structure" />
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
                {deleting ? 'Deleting...' : 'Confirm delete'}
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
            {saving ? 'Saving...' : isNew ? 'Create article' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  );
};
