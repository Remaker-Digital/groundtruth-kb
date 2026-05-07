/**
 * "Was this helpful?" feedback widget for documentation pages.
 *
 * Stub implementation — logs feedback to console. Before launch, connect
 * this to Google Analytics (GA4 custom event) or a lightweight backend.
 *
 * Usage: Add <DocFeedback /> at the bottom of any doc page, or integrate
 * into the DocItem footer via Docusaurus theme swizzling.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useState } from 'react';

const styles = {
  container: {
    marginTop: '2rem',
    paddingTop: '1.5rem',
    borderTop: '1px solid var(--ifm-toc-border-color)',
    textAlign: 'center',
  },
  question: {
    fontSize: '0.95rem',
    color: 'var(--ifm-color-content-secondary)',
    marginBottom: '0.75rem',
  },
  buttonGroup: {
    display: 'flex',
    gap: '0.75rem',
    justifyContent: 'center',
  },
  button: {
    padding: '0.4rem 1.2rem',
    border: '1px solid var(--ifm-color-emphasis-300)',
    borderRadius: '4px',
    backgroundColor: 'transparent',
    color: 'var(--ifm-color-content)',
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'border-color 0.2s, background-color 0.2s',
  },
  thanks: {
    fontSize: '0.9rem',
    color: 'var(--ifm-color-content-secondary)',
    marginTop: '0.5rem',
  },
};

export default function DocFeedback() {
  const [submitted, setSubmitted] = useState(false);

  function handleFeedback(helpful) {
    setSubmitted(true);

    // TODO: Replace with GA4 event or API call before launch
    // Example GA4 integration:
    //   window.gtag?.('event', 'doc_feedback', {
    //     page_path: window.location.pathname,
    //     helpful: helpful,
    //   });
    if (typeof window !== 'undefined') {
      console.log('[DocFeedback]', {
        page: window.location.pathname,
        helpful,
        timestamp: new Date().toISOString(),
      });
    }
  }

  if (submitted) {
    return (
      <div style={styles.container}>
        <p style={styles.thanks}>Thank you for your feedback.</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <p style={styles.question}>Was this page helpful?</p>
      <div style={styles.buttonGroup}>
        <button
          style={styles.button}
          onClick={() => handleFeedback(true)}
          aria-label="Yes, this page was helpful"
        >
          Yes
        </button>
        <button
          style={styles.button}
          onClick={() => handleFeedback(false)}
          aria-label="No, this page was not helpful"
        >
          No
        </button>
      </div>
    </div>
  );
}
