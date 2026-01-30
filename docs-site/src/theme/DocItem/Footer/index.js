/**
 * Swizzled DocItem/Footer to append the "Was this helpful?" widget
 * below every documentation page.
 *
 * This wraps the default Docusaurus DocItem Footer component.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React from 'react';
import Footer from '@theme-original/DocItem/Footer';
import DocFeedback from '@site/src/components/DocFeedback';

export default function FooterWrapper(props) {
  return (
    <>
      <Footer {...props} />
      <DocFeedback />
    </>
  );
}
