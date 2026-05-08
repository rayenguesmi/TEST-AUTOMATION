import { createContext, useContext, useState, useCallback, useEffect } from 'react';

// ─── Toast Context ──────────────────────────────────────────────────────────
const ToastContext = createContext(null);

const toastConfig = {
  success: { color: 'var(--color-success)', icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0", label: 'Succès' },
  error: { color: 'var(--color-danger)', icon: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0", label: 'Erreur' },
  warning: { color: 'var(--color-warning)', icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z", label: 'Attention' },
  info: { color: 'var(--color-info)', icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0", label: 'Info' },
  ai: { color: 'var(--color-ai)', icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z", label: 'Agent IA' },
};

let toastId = 0;

// ─── Toast Item ───────────────────────────────────────────────────────────────
function ToastItem({ toast, onRemove }) {
  const [exiting, setExiting] = useState(false);
  const config = toastConfig[toast.type] || toastConfig.info;

  const dismiss = useCallback(() => {
    setExiting(true);
    setTimeout(() => onRemove(toast.id), 300);
  }, [toast.id, onRemove]);

  useEffect(() => {
    const duration = toast.type === 'error' ? 8000 : 4000;
    const timer = setTimeout(dismiss, duration);
    return () => clearTimeout(timer);
  }, [dismiss, toast.type]);

  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '12px 14px',
      background: 'var(--bg-overlay)',
      border: `1px solid ${config.color}30`,
      borderLeft: `3px solid ${config.color}`,
      borderRadius: 'var(--radius-lg)',
      boxShadow: 'var(--shadow-modal)',
      maxWidth: 360, width: '100%',
      animation: exiting ? 'toast-out 0.3s ease forwards' : 'toast-in 0.3s ease forwards',
      position: 'relative',
    }}>
      {/* Icon */}
      <div style={{
        width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
        background: `${config.color}18`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        {toast.type === 'ai' ? (
          <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
            stroke={config.color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
            style={{ animation: 'spin-slow 2s linear infinite' }}>
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        ) : (
          <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
            stroke={config.color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
            <path d={config.icon} />
          </svg>
        )}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>
          {toast.title || config.label}
        </div>
        {toast.message && (
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {toast.message}
          </div>
        )}
        {toast.action && (
          <button onClick={() => { toast.action.onClick(); dismiss(); }} style={{
            marginTop: 6, background: 'none', border: 'none', cursor: 'pointer',
            color: config.color, fontSize: 11, fontWeight: 600, padding: 0,
          }}>
            {toast.action.label} →
          </button>
        )}
      </div>

      {/* Close */}
      <button onClick={dismiss} style={{
        background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)',
        padding: 2, borderRadius: 4, display: 'flex', transition: 'color 120ms ease',
      }}
      onMouseEnter={e => e.currentTarget.style.color = 'var(--text-primary)'}
      onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
      aria-label="Fermer la notification">
        <svg width={12} height={12} viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
          <path d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

// ─── Toast Provider ──────────────────────────────────────────────────────────
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback(({ type = 'info', title, message, action }) => {
    const id = ++toastId;
    setToasts(prev => {
      const next = [...prev, { id, type, title, message, action }];
      return next.slice(-3); // Max 3 toasts (FIFO)
    });
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  // Convenience methods
  const toast = {
    success: (title, message, action) => addToast({ type: 'success', title, message, action }),
    error: (title, message, action) => addToast({ type: 'error', title, message, action }),
    warning: (title, message, action) => addToast({ type: 'warning', title, message, action }),
    info: (title, message, action) => addToast({ type: 'info', title, message, action }),
    ai: (title, message, action) => addToast({ type: 'ai', title, message, action }),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {/* Toast container — bottom-right */}
      <div style={{
        position: 'fixed', bottom: 24, right: 24,
        display: 'flex', flexDirection: 'column', gap: 10,
        zIndex: 9999, pointerEvents: 'none',
      }}>
        {toasts.map(t => (
          <div key={t.id} style={{ pointerEvents: 'auto' }}>
            <ToastItem toast={t} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside ToastProvider');
  return ctx;
};
