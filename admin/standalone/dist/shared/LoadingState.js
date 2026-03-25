import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { tokens } from './theme/styles';
// ---------------------------------------------------------------------------
// Keyframes (injected once)
// ---------------------------------------------------------------------------
const KEYFRAMES_ID = 'agent-red-loading-keyframes';
function ensureKeyframes() {
    if (typeof document === 'undefined')
        return;
    if (document.getElementById(KEYFRAMES_ID))
        return;
    const style = document.createElement('style');
    style.id = KEYFRAMES_ID;
    style.textContent = `
    @keyframes ar-spin { to { transform: rotate(360deg); } }
    @keyframes ar-pulse { 0%,100% { opacity: 0.4; } 50% { opacity: 0.15; } }
  `;
    document.head.appendChild(style);
}
const Spinner = ({ text = 'Loading\u2026', size = 32 }) => {
    ensureKeyframes();
    return (_jsxs("div", { style: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '48px 16px',
            color: tokens.textMuted,
        }, role: "status", "aria-label": text, children: [_jsx("div", { style: {
                    width: size,
                    height: size,
                    border: `3px solid ${tokens.border}`,
                    borderTopColor: tokens.brand,
                    borderRadius: '50%',
                    animation: 'ar-spin 0.8s linear infinite',
                    marginBottom: '12px',
                } }), _jsx("span", { style: { fontSize: '14px' }, children: text })] }));
};
const Skeleton = ({ lines = 3, showHeader = true }) => {
    ensureKeyframes();
    const lineWidths = ['100%', '92%', '85%', '78%', '95%', '88%'];
    return (_jsxs("div", { style: { padding: '24px 0' }, role: "status", "aria-label": "Loading content", children: [showHeader && (_jsx("div", { style: {
                    height: '20px',
                    width: '40%',
                    background: tokens.border,
                    borderRadius: '4px',
                    marginBottom: '20px',
                    animation: 'ar-pulse 1.5s ease-in-out infinite',
                } })), Array.from({ length: lines }, (_, i) => (_jsx("div", { style: {
                    height: '14px',
                    width: lineWidths[i % lineWidths.length],
                    background: tokens.border,
                    borderRadius: '4px',
                    marginBottom: '12px',
                    animation: 'ar-pulse 1.5s ease-in-out infinite',
                    animationDelay: `${i * 0.1}s`,
                } }, i)))] }));
};
export const LoadingState = (props) => {
    if (props.variant === 'skeleton') {
        return _jsx(Skeleton, { ...props });
    }
    return _jsx(Spinner, { ...props });
};
export default LoadingState;
//# sourceMappingURL=LoadingState.js.map