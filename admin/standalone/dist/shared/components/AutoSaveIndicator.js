import { jsx as _jsx } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import { useEffect, useState } from 'react';
import { Text } from '@mantine/core';
/**
 * Subtle "✓ Saved" indicator that appears after auto-save and fades out.
 *
 * Usage: pass a `saveCount` that increments on every successful save.
 * The indicator appears instantly and fades out after `fadeAfter` ms.
 */
export const AutoSaveIndicator = ({ saveCount, fadeAfter = 1500, }) => {
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        if (saveCount === 0)
            return;
        setVisible(true);
        const timer = setTimeout(() => setVisible(false), fadeAfter);
        return () => clearTimeout(timer);
    }, [saveCount, fadeAfter]);
    return (_jsx(Text, { size: "xs", c: "dimmed", style: {
            opacity: visible ? 1 : 0,
            transition: 'opacity 0.4s ease-out',
            userSelect: 'none',
            minWidth: 50,
        }, "aria-live": "polite", children: "\u2713 Saved" }));
};
//# sourceMappingURL=AutoSaveIndicator.js.map