// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * AnswerBlocks — renders structured answer blocks within agent messages (SPEC-1867).
 *
 * Block types (v1):
 *   - steps: Numbered procedure list
 *   - faq: Collapsible Q&A accordion
 *   - action: CTA button with link
 *
 * Product cards deferred to v2 (requires upstream structured-data plumbing).
 *
 * Blocks are supplementary — text content is always rendered above.
 * If block rendering fails, the text fallback is sufficient.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { FunctionComponent } from 'preact';
import { useState } from 'preact/hooks';
import type { DesignTokens } from '@/theme/tokens';
import type { AnswerBlock } from '@/state/store';

// ---------------------------------------------------------------------------
// Step List
// ---------------------------------------------------------------------------

const StepList: FunctionComponent<{
  block: Extract<AnswerBlock, { type: 'steps' }>;
  tokens: DesignTokens;
}> = ({ block, tokens }) => (
  <div style={{ marginTop: tokens.space2 }}>
    {block.title && (
      <div style={{
        fontSize: tokens.fontSizeSm,
        fontWeight: tokens.fontWeightMedium,
        fontFamily: tokens.fontFamily,
        color: tokens.colorText,
        marginBottom: tokens.space1,
      }}>
        {block.title}
      </div>
    )}
    <ol style={{
      margin: 0,
      paddingLeft: '1.5em',
      fontFamily: tokens.fontFamily,
      fontSize: tokens.fontSizeSm,
      color: tokens.colorText,
      lineHeight: '1.6',
    }}>
      {block.items.map((item, i) => (
        <li key={i} style={{ marginBottom: tokens.space1 }}>{item}</li>
      ))}
    </ol>
  </div>
);

// ---------------------------------------------------------------------------
// FAQ Accordion
// ---------------------------------------------------------------------------

const FaqItem: FunctionComponent<{
  question: string;
  answer: string;
  tokens: DesignTokens;
}> = ({ question, answer, tokens }) => {
  const [open, setOpen] = useState(false);

  return (
    <div style={{
      borderBottom: `1px solid ${tokens.colorBorder}`,
    }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          display: 'flex',
          width: '100%',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: `${tokens.space2} 0`,
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontFamily: tokens.fontFamily,
          fontSize: tokens.fontSizeSm,
          fontWeight: tokens.fontWeightMedium,
          color: tokens.colorText,
          textAlign: 'left',
        }}
      >
        <span>{question}</span>
        <span style={{
          fontSize: tokens.fontSizeXs,
          color: tokens.colorTextMuted,
          marginLeft: tokens.space2,
          transition: 'transform 0.2s',
          transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
        }}>
          ▾
        </span>
      </button>
      {open && (
        <div style={{
          padding: `0 0 ${tokens.space2} 0`,
          fontSize: tokens.fontSizeSm,
          fontFamily: tokens.fontFamily,
          color: tokens.colorTextMuted,
          lineHeight: '1.5',
        }}>
          {answer}
        </div>
      )}
    </div>
  );
};

const FaqAccordion: FunctionComponent<{
  block: Extract<AnswerBlock, { type: 'faq' }>;
  tokens: DesignTokens;
}> = ({ block, tokens }) => (
  <div style={{ marginTop: tokens.space2 }}>
    {block.items.map((item, i) => (
      <FaqItem
        key={i}
        question={item.question}
        answer={item.answer}
        tokens={tokens}
      />
    ))}
  </div>
);

// ---------------------------------------------------------------------------
// Action Button
// ---------------------------------------------------------------------------

const ActionButton: FunctionComponent<{
  block: Extract<AnswerBlock, { type: 'action' }>;
  tokens: DesignTokens;
}> = ({ block, tokens }) => (
  <a
    href={block.url}
    target="_top"
    rel="noopener noreferrer"
    style={{
      display: 'inline-block',
      marginTop: tokens.space2,
      padding: `${tokens.space2} ${tokens.space3}`,
      backgroundColor: block.style === 'primary' ? tokens.colorPrimary : 'transparent',
      color: block.style === 'primary' ? '#fff' : tokens.colorPrimary,
      border: block.style === 'primary' ? 'none' : `1px solid ${tokens.colorPrimary}`,
      borderRadius: tokens.borderRadius,
      fontFamily: tokens.fontFamily,
      fontSize: tokens.fontSizeSm,
      fontWeight: tokens.fontWeightMedium,
      textDecoration: 'none',
      cursor: 'pointer',
      textAlign: 'center',
    }}
  >
    {block.label}
  </a>
);

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const AnswerBlocks: FunctionComponent<{
  blocks: AnswerBlock[];
  tokens: DesignTokens;
}> = ({ blocks, tokens }) => {
  if (!blocks || blocks.length === 0) return null;

  return (
    <div style={{ marginTop: tokens.space2 }}>
      {blocks.map((block, i) => {
        switch (block.type) {
          case 'steps':
            return <StepList key={i} block={block} tokens={tokens} />;
          case 'faq':
            return <FaqAccordion key={i} block={block} tokens={tokens} />;
          case 'action':
            return <ActionButton key={i} block={block} tokens={tokens} />;
          default:
            return null;
        }
      })}
    </div>
  );
};
