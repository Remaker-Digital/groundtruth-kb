/**
 * UploadResultDisplay — success banner shown after a file upload or URL import
 * completes, displaying the number of entries created.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import type { KBUploadResult } from '../types';
import { COLOR_SUCCESS, COLOR_TEXT, COLOR_TEXT_SECONDARY, BORDER_RADIUS, buttonStyle } from './styles';

export interface UploadResultDisplayProps {
  result: KBUploadResult;
  onDone: () => void;
}

export const UploadResultDisplay: React.FC<UploadResultDisplayProps> = ({ result, onDone }) => (
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
