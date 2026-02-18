/**
 * URLImportForm — form for importing KB content from a website URL,
 * with optional site-crawl mode.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState, useCallback } from 'react';
import { HelpTooltip } from '../HelpTooltip';
import {
  BRAND_PRIMARY,
  COLOR_TEXT,
  COLOR_TEXT_SECONDARY,
  COLOR_DANGER,
  BORDER_RADIUS,
  inputStyle,
  buttonStyle,
} from './styles';

export interface URLImportFormProps {
  onImport: (url: string, crawl: boolean, maxPages: number) => void;
  importing: boolean;
  error: string | null;
}

export const URLImportForm: React.FC<URLImportFormProps> = ({ onImport, importing, error }) => {
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
          <HelpTooltip text="Follow links on the same domain and import multiple pages automatically." docLink="https://agentredcx.com/docs/admin-guide/knowledge-base-management#uploading-documents" />
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
