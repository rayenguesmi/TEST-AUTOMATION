import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const Icon = ({ d, size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

// Breadcrumb config
const breadcrumbMap = {
  '/dashboard': ['Dashboard'],
  '/new-test': ['Dashboard', 'Nouveau Test'],
  '/my-tests': ['Dashboard', 'Mes Tests'],
  '/projects': ['Dashboard', 'Projets'],
  '/urls': ['Dashboard', 'URLs Surveillées'],
  '/admin/dashboard': ['Admin', 'Dashboard'],
  '/admin/users': ['Admin', 'Utilisateurs'],
  '/admin/health': ['Admin', 'Santé Système'],
  '/admin/logs': ['Admin', 'Logs Live'],
  '/admin/tests': ['Admin', 'Tests Actifs'],
  '/admin/settings': ['Admin', 'Configuration'],
};

// Mock notifications
const mockNotifs = [
  { id: 1, type: 'success', title: 'Test réussi', msg: 'Login Flow — E2E · SauceDemo', time: 'il y a 2min', read: false },
  { id: 2, type: 'ai', title: 'Agent IA a terminé', msg: '47 assertions générées en 3.2s', time: 'il y a 8min', read: false },
  { id: 3, type: 'error', title: 'Test échoué', msg: 'Checkout Flow — timeout sur le paiement', time: 'il y a 15min', read: true },
  { id: 4, type: 'warning', title: 'URL dégradée', msg: 'api.saucedemo.com — latence 1.2s', time: 'il y a 1h', read: true },
];

const notifColors = {
  success: 'var(--color-success)',
  ai: 'var(--color-ai)',
  error: 'var(--color-danger)',
  warning: 'var(--color-warning)',
};

const notifIcons = {
  success: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0",
  ai: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  error: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0",
  warning: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
};

export default function Topbar({ agentActive = false, agentMessage = '' }) {
  const location = useLocation();
  const [showNotifs, setShowNotifs] = useState(false);
  const [showSpotlight, setShowSpotlight] = useState(false);
  const [notifications, setNotifications] = useState(mockNotifs);
  const [searchVal, setSearchVal] = useState('');
  const notifRef = useRef(null);
  const spotlightRef = useRef(null);

  const crumbs = breadcrumbMap[location.pathname] || ['Dashboard'];
  const unread = notifications.filter(n => !n.read).length;

  // Cmd+K spotlight
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowSpotlight(v => !v);
      }
      if (e.key === 'Escape') {
        setShowSpotlight(false);
        setShowNotifs(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) setShowNotifs(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const markAllRead = () => setNotifications(prev => prev.map(n => ({ ...n, read: true })));

  return (
    <>
      <header style={{
        height: 'var(--topbar-height)',
        background: 'var(--bg-raised)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        gap: 16,
        position: 'sticky',
        top: 0,
        zIndex: 30,
        backdropFilter: 'blur(8px)',
      }}>

        {/* Breadcrumb */}
        <nav aria-label="breadcrumb" style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 6, minWidth: 0 }}>
          {crumbs.map((crumb, i) => (
            <span key={crumb} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              {i > 0 && <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>/</span>}
              <span style={{
                fontSize: 13,
                fontWeight: i === crumbs.length - 1 ? 600 : 400,
                color: i === crumbs.length - 1 ? 'var(--text-primary)' : 'var(--text-muted)',
              }}>{crumb}</span>
            </span>
          ))}
        </nav>

        {/* AI Agent indicator */}
        {agentActive && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '5px 12px', borderRadius: 99,
            background: 'var(--color-ai-muted)', border: '1px solid rgba(168,85,247,0.3)',
            animation: 'ai-pulse 2s ease-in-out infinite',
          }}>
            <svg width={12} height={12} viewBox="0 0 24 24" fill="none" stroke="var(--color-ai)" strokeWidth={2}
              style={{ animation: 'spin-slow 1.5s linear infinite' }}>
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span style={{ fontSize: 11, color: 'var(--color-ai)', fontWeight: 500, whiteSpace: 'nowrap' }}>
              {agentMessage || 'Agent génère un test…'}
            </span>
          </div>
        )}

        {/* Global search (Cmd+K) */}
        <button onClick={() => setShowSpotlight(true)} style={{
          display: 'flex', alignItems: 'center', gap: 8,
          padding: '6px 12px', background: 'var(--bg-overlay)',
          border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
          cursor: 'pointer', color: 'var(--text-muted)', fontSize: 12,
          transition: 'all 150ms ease', width: 200,
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
        aria-label="Recherche globale (Ctrl+K)">
          <Icon d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" size={13} />
          <span style={{ flex: 1, textAlign: 'left' }}>Rechercher…</span>
          <span style={{ fontSize: 10, padding: '1px 5px', borderRadius: 4, background: 'var(--border)', color: 'var(--text-muted)', fontWeight: 600 }}>⌘K</span>
        </button>

        {/* Notifications */}
        <div style={{ position: 'relative' }} ref={notifRef}>
          <button onClick={() => setShowNotifs(v => !v)} style={{
            position: 'relative', background: 'transparent', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-md)', padding: 7, cursor: 'pointer',
            color: 'var(--text-secondary)', display: 'flex', transition: 'all 150ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
          aria-label={`Notifications (${unread} non lues)`}>
            <Icon d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" size={16} />
            {unread > 0 && (
              <span style={{
                position: 'absolute', top: -4, right: -4,
                width: 16, height: 16, borderRadius: '50%',
                background: 'var(--color-danger)', fontSize: 9,
                fontWeight: 700, color: '#fff', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                border: '2px solid var(--bg-raised)',
              }}>{unread}</span>
            )}
          </button>

          {showNotifs && (
            <div style={{
              position: 'absolute', top: 'calc(100% + 10px)', right: 0,
              width: 340, background: 'var(--bg-overlay)',
              border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-modal)', zIndex: 50,
              animation: 'fade-in-up 0.2s ease',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontWeight: 600, fontSize: 13 }}>Notifications</span>
                <button onClick={markAllRead} style={{ fontSize: 11, color: 'var(--color-brand)', background: 'none', border: 'none', cursor: 'pointer' }}>Tout marquer lu</button>
              </div>
              <div style={{ maxHeight: 360, overflowY: 'auto' }}>
                {notifications.map(n => (
                  <div key={n.id} style={{
                    display: 'flex', gap: 12, padding: '12px 16px',
                    borderBottom: '1px solid var(--border-muted)',
                    background: n.read ? 'transparent' : 'rgba(99,102,241,0.04)',
                    cursor: 'pointer', transition: 'background 150ms ease',
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = n.read ? 'transparent' : 'rgba(99,102,241,0.04)'}>
                    <div style={{
                      width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                      background: `${notifColors[n.type]}20`, display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                    }}>
                      <svg width={14} height={14} viewBox="0 0 24 24" fill="none"
                        stroke={notifColors[n.type]} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                        <path d={notifIcons[n.type]} />
                      </svg>
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: n.read ? 'var(--text-secondary)' : 'var(--text-primary)' }}>{n.title}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{n.msg}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{n.time}</div>
                    </div>
                    {!n.read && <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-brand)', flexShrink: 0, marginTop: 6 }} />}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Spotlight Modal (Cmd+K) */}
      {showSpotlight && (
        <div onClick={() => setShowSpotlight(false)} style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)', zIndex: 200, display: 'flex',
          alignItems: 'flex-start', justifyContent: 'center', paddingTop: '15vh',
          animation: 'modal-backdrop 0.15s ease',
        }}>
          <div onClick={e => e.stopPropagation()} ref={spotlightRef} style={{
            width: '100%', maxWidth: 580, background: 'var(--bg-overlay)',
            border: '1px solid var(--border)', borderRadius: 'var(--radius-xl)',
            boxShadow: 'var(--shadow-modal)', overflow: 'hidden',
            animation: 'modal-content 0.2s ease',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '0 20px', borderBottom: '1px solid var(--border)' }}>
              <Icon d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" size={16} />
              <input autoFocus value={searchVal} onChange={e => setSearchVal(e.target.value)}
                placeholder="Rechercher un test, utilisateur, URL…"
                style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-primary)', fontSize: 15, padding: '18px 0', fontFamily: 'var(--font-sans)' }} />
              <kbd style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: 'var(--border)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>Esc</kbd>
            </div>
            <div style={{ padding: '8px 0' }}>
              {['Dashboard', 'Nouveau Test', 'Mes Tests', 'Utilisateurs', 'Santé Système'].filter(item =>
                searchVal === '' || item.toLowerCase().includes(searchVal.toLowerCase())
              ).map(item => (
                <div key={item} style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: '10px 20px',
                  cursor: 'pointer', transition: 'background 120ms ease',
                  color: 'var(--text-secondary)', fontSize: 13,
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-hover)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}>
                  <Icon d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0" size={14} />
                  {item}
                </div>
              ))}
            </div>
            <div style={{ padding: '8px 20px 12px', borderTop: '1px solid var(--border)', display: 'flex', gap: 16 }}>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>↑↓ Naviguer</span>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>↵ Sélectionner</span>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Esc Fermer</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
