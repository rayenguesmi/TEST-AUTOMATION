import { useEffect, useRef } from 'react';

/**
 * Generic Modal component with focus trap and keyboard navigation
 * @param {boolean} isOpen - Whether the modal is open
 * @param {function} onClose - Callback to close the modal
 * @param {string} title - Modal title
 * @param {React.ReactNode} children - Modal content
 * @param {string} size - 'sm' | 'md' | 'lg' | 'xl'
 * @param {React.ReactNode} footer - Optional footer content
 */
export default function Modal({ isOpen, onClose, title, children, size = 'md', footer }) {
  const modalRef = useRef(null);
  const firstFocusRef = useRef(null);

  const sizes = { sm: 420, md: 560, lg: 780, xl: 960 };

  // Focus trap + Escape key
  useEffect(() => {
    if (!isOpen) return;

    const focusableElements = modalRef.current?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusableElements?.[0];
    const last = focusableElements?.[focusableElements.length - 1];

    first?.focus();

    const handler = (e) => {
      if (e.key === 'Escape') { onClose(); return; }
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first?.focus();
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  // Prevent body scroll
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.65)',
        backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', zIndex: 100, padding: 20,
        animation: 'modal-backdrop 0.2s ease',
      }}>
      <div
        ref={modalRef}
        onClick={e => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: sizes[size],
          background: 'var(--bg-overlay)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xl)', boxShadow: 'var(--shadow-modal)',
          display: 'flex', flexDirection: 'column', maxHeight: '90vh',
          animation: 'modal-content 0.25s ease',
        }}>

        {/* Header */}
        {title && (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '18px 24px', borderBottom: '1px solid var(--border)', flexShrink: 0,
          }}>
            <h2 id="modal-title" style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
              {title}
            </h2>
            <button onClick={onClose} ref={firstFocusRef} style={{
              background: 'transparent', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)',
              padding: 5, cursor: 'pointer', color: 'var(--text-muted)', display: 'flex',
              transition: 'all 150ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
            aria-label="Fermer la modal">
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth={2.5} strokeLinecap="round">
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div style={{
            padding: '16px 24px', borderTop: '1px solid var(--border)',
            display: 'flex', gap: 10, justifyContent: 'flex-end', flexShrink: 0,
          }}>
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Confirmation modal with optional danger styling
 */
export function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmLabel = 'Confirmer', danger = false }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm"
      footer={
        <>
          <button className="btn btn-ghost" onClick={onClose}>Annuler</button>
          <button className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`} onClick={() => { onConfirm(); onClose(); }}>
            {confirmLabel}
          </button>
        </>
      }>
      <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{message}</p>
    </Modal>
  );
}

/**
 * Slide-over panel (from right)
 */
export function SlideOver({ isOpen, onClose, title, children, width = 480 }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    if (isOpen) window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div onClick={onClose} style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 100,
      animation: 'modal-backdrop 0.2s ease',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        position: 'fixed', top: 0, right: 0, bottom: 0, width,
        background: 'var(--bg-overlay)', borderLeft: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column',
        animation: 'slide-in-right 0.25s ease',
        boxShadow: '-20px 0 60px rgba(0,0,0,0.4)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '18px 24px', borderBottom: '1px solid var(--border)' }}>
          <h3 style={{ fontSize: 14, fontWeight: 700 }}>{title}</h3>
          <button onClick={onClose} className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 12 }}>✕</button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>{children}</div>
      </div>
    </div>
  );
}
