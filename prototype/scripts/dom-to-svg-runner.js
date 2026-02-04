/**
 * Browser-side runner for dom-to-svg. Injected into the page; exposes window.capturePageToVectorSvg().
 * Captures the app shell root (#app-shell-capture-root) when present so header/navbar are included.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { documentToSVG, elementToSVG, inlineResources } from 'dom-to-svg';

window.capturePageToVectorSvg = async function () {
  const appShell = document.getElementById('app-shell-capture-root');
  const target = appShell || document.documentElement;
  const captureArea = target.getBoundingClientRect();
  const svgDoc = appShell
    ? elementToSVG(appShell, { captureArea: new DOMRect(0, 0, window.innerWidth, window.innerHeight) })
    : documentToSVG(document, { captureArea: new DOMRect(0, 0, document.documentElement.scrollWidth, document.documentElement.scrollHeight) });

  const root = svgDoc.documentElement;
  document.body.prepend(root);
  try {
    await inlineResources(root);
  } finally {
    root.remove();
  }
  return new XMLSerializer().serializeToString(root);
};
