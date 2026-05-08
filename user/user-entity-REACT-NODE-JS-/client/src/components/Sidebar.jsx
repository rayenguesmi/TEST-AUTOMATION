import { useState, useEffect } from 'react';
import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

// ─── Icons ─────────────────────────────────────────────────────────────────
const Icon = ({ d, size = 18, stroke = 1.5 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

const icons = {
  dashboard: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  tests: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
  newTest: "M12 4v16m8-8H4",
  history: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0",
  users: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z",
  health: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  logs: "M4 6h16M4 10h16M4 14h10",
  settings: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
  logout: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1",
  chevronLeft: "M15 19l-7-7 7-7",
  chevronRight: "M9 5l7 7-7 7",
  project: "M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z",
  url: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1",
  ai: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
};

// ─── Navigation config ─────────────────────────────────────────────────────
const navUser = [
  { label: 'Dashboard', icon: 'dashboard', to: '/dashboard', badge: null },
  { label: 'Mes Tests', icon: 'tests', to: '/my-tests', badge: 'active' },
  { label: 'Projets', icon: 'project', to: '/projects', badge: null },
  { label: 'URLs Surveillées', icon: 'url', to: '/urls', badge: null },
];

const navAdmin = [
  { label: 'Dashboard', icon: 'dashboard', to: '/admin/dashboard', badge: null },
  { label: 'Utilisateurs', icon: 'users', to: '/admin/users', badge: null },
  { label: 'Santé Système', icon: 'health', to: '/admin/health', badge: null },
  { label: 'Logs Live', icon: 'logs', to: '/admin/logs', badge: 'alerts' },
  { label: 'Tests Actifs', icon: 'tests', to: '/admin/tests', badge: 'active' },
];

// ─── Mock real-time counts ─────────────────────────────────────────────────
const useLiveCounts = () => {
  const [counts, setCounts] = useState({ active: 3, alerts: 1 });
  useEffect(() => {
    // TODO: Replace with WebSocket subscription
    const interval = setInterval(() => {
      setCounts({ active: Math.floor(Math.random() * 8) + 1, alerts: Math.floor(Math.random() * 3) });
    }, 8000);
    return () => clearInterval(interval);
  }, []);
  return counts;
};

export default function Sidebar() {
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [wsConnected, setWsConnected] = useState(true);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const counts = useLiveCounts();

  const isAdmin = user?.role === 'admin';
  const navItems = isAdmin ? navAdmin : navUser;

  // TODO: Replace with actual WS connection state
  useEffect(() => {
    const interval = setInterval(() => setWsConnected(prev => prev), 5000);
    return () => clearInterval(interval);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getBadgeCount = (badge) => {
    if (!badge) return null;
    if (badge === 'active') return counts.active;
    if (badge === 'alerts') return counts.alerts;
    return null;
  };

  return (
    <>
      {/* Sidebar */}
      <aside style={{
        width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
        minHeight: '100vh',
        background: 'var(--bg-raised)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 300ms ease',
        position: 'sticky',
        top: 0,
        overflow: 'hidden',
        flexShrink: 0,
        zIndex: 40,
      }}>

        {/* Logo + Toggle */}
        <div style={{
          height: 'var(--topbar-height)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'space-between',
          padding: collapsed ? '0' : '0 16px',
          borderBottom: '1px solid var(--border)',
          flexShrink: 0,
        }}>
          {!collapsed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <img src="/logo.png" alt="AutoTest" style={{
                width: 32, height: 32,
                objectFit: 'contain',
                filter: 'drop-shadow(0 0 6px rgba(34,211,238,0.4))',
                flexShrink: 0,
              }} />
              <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                AutoTest
              </span>
            </div>
          )}
          <button onClick={() => setCollapsed(!collapsed)} style={{
            background: 'transparent', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)', padding: 5, cursor: 'pointer',
            color: 'var(--text-muted)', display: 'flex', transition: 'all 150ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'; }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
          aria-label={collapsed ? 'Expandre la sidebar' : 'Réduire la sidebar'}>
            <Icon d={collapsed ? icons.chevronRight : icons.chevronLeft} size={14} />
          </button>
        </div>

        {/* Role badge */}
        {!collapsed && (
          <div style={{ padding: '12px 16px 4px' }}>
            <span style={{
              fontSize: 10, fontWeight: 600, letterSpacing: '0.08em',
              color: isAdmin ? 'var(--color-ai)' : 'var(--color-brand)',
              textTransform: 'uppercase',
            }}>
              {isAdmin ? '⚡ Admin Panel' : '👤 Espace Utilisateur'}
            </span>
          </div>
        )}

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '8px 8px', overflowY: 'auto' }}>
          {navItems.map(item => {
            const isActive = location.pathname === item.to || location.pathname.startsWith(item.to + '/');
            const badgeCount = getBadgeCount(item.badge);

            return (
              <NavLink key={item.to} to={item.to} style={{ textDecoration: 'none' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: collapsed ? 'center' : 'space-between',
                  gap: 10,
                  padding: collapsed ? '10px 0' : '9px 12px',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: 2,
                  background: isActive ? 'var(--bg-active)' : 'transparent',
                  color: isActive ? 'var(--color-brand)' : 'var(--text-secondary)',
                  border: `1px solid ${isActive ? 'var(--border-brand)' : 'transparent'}`,
                  cursor: 'pointer',
                  transition: 'all 120ms ease',
                  position: 'relative',
                }}
                onMouseEnter={e => { if (!isActive) { e.currentTarget.style.background = 'var(--bg-hover)'; e.currentTarget.style.color = 'var(--text-primary)'; }}}
                onMouseLeave={e => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                    <Icon d={icons[item.icon]} size={16} />
                    {!collapsed && (
                      <span style={{ fontSize: 13, fontWeight: isActive ? 600 : 400, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {item.label}
                      </span>
                    )}
                  </div>
                  {!collapsed && badgeCount > 0 && (
                    <span style={{
                      fontSize: 10, fontWeight: 700,
                      padding: '1px 6px',
                      borderRadius: 99,
                      background: item.badge === 'alerts' ? 'var(--color-danger-muted)' : 'var(--color-brand-muted)',
                      color: item.badge === 'alerts' ? 'var(--color-danger)' : 'var(--color-brand)',
                      border: `1px solid ${item.badge === 'alerts' ? 'rgba(239,68,68,0.3)' : 'rgba(99,102,241,0.3)'}`,
                    }}>{badgeCount}</span>
                  )}
                  {collapsed && badgeCount > 0 && (
                    <span style={{
                      position: 'absolute', top: 4, right: 4,
                      width: 8, height: 8, borderRadius: '50%',
                      background: item.badge === 'alerts' ? 'var(--color-danger)' : 'var(--color-brand)',
                    }} />
                  )}
                </div>
              </NavLink>
            );
          })}

          {/* Admin System section */}
          {isAdmin && !collapsed && (
            <div style={{ marginTop: 16 }}>
              <div style={{ height: 1, background: 'var(--border)', margin: '0 4px 12px' }} />
              <span style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', color: 'var(--text-muted)', textTransform: 'uppercase', padding: '0 12px' }}>
                Système
              </span>
              <NavLink to="/admin/settings" style={{ textDecoration: 'none' }}>
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 12px', borderRadius: 'var(--radius-md)', marginTop: 4,
                  color: 'var(--text-secondary)', cursor: 'pointer', transition: 'all 120ms ease',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-hover)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-secondary)'; }}>
                  <Icon d={icons.settings} size={16} />
                  <span style={{ fontSize: 13 }}>Configuration</span>
                </div>
              </NavLink>
            </div>
          )}
        </nav>

        {/* Footer: WS indicator + User + Logout */}
        <div style={{ borderTop: '1px solid var(--border)', padding: '12px 8px', flexShrink: 0 }}>
          {/* WebSocket indicator */}
          {!collapsed && (
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '6px 12px', marginBottom: 8,
            }}>
              <span className="pulse-dot" style={{
                background: wsConnected ? 'var(--color-success)' : 'var(--color-danger)',
                animation: wsConnected ? 'pulse-dot 1.5s ease-in-out infinite' : 'none',
                flexShrink: 0,
              }} />
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {wsConnected ? 'WebSocket connecté' : 'Déconnecté'}
              </span>
            </div>
          )}

          {/* User info */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: collapsed ? '8px 0' : '8px 12px',
            justifyContent: collapsed ? 'center' : 'flex-start',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-overlay)',
            border: '1px solid var(--border)',
            marginBottom: 8,
          }}>
            <div style={{
              width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
              background: `linear-gradient(135deg, ${isAdmin ? '#a855f7, #6366f1' : '#6366f1, #3b82f6'})`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 12, fontWeight: 700, color: '#fff',
            }}>
              {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || '?'}
            </div>
            {!collapsed && (
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user?.name || user?.email?.split('@')[0] || 'Utilisateur'}
                </div>
                <div style={{ fontSize: 10, color: isAdmin ? 'var(--color-ai)' : 'var(--color-brand)', textTransform: 'capitalize', fontWeight: 500 }}>
                  {user?.role || 'user'}
                </div>
              </div>
            )}
          </div>

          {/* Logout button */}
          <button onClick={() => setShowLogoutConfirm(true)} style={{
            width: '100%', display: 'flex', alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-start',
            gap: 8, padding: collapsed ? '8px 0' : '8px 12px',
            background: 'transparent', border: 'none', cursor: 'pointer',
            borderRadius: 'var(--radius-md)', color: 'var(--text-muted)',
            fontSize: 13, transition: 'all 120ms ease',
          }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--color-danger-muted)'; e.currentTarget.style.color = 'var(--color-danger)'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--text-muted)'; }}
          aria-label="Se déconnecter">
            <Icon d={icons.logout} size={15} />
            {!collapsed && <span>Déconnexion</span>}
          </button>
        </div>
      </aside>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div onClick={() => setShowLogoutConfirm(false)} style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', zIndex: 100, animation: 'modal-backdrop 0.2s ease',
        }}>
          <div onClick={e => e.stopPropagation()} style={{
            background: 'var(--bg-overlay)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-xl)', padding: 28, maxWidth: 360, width: '90%',
            boxShadow: 'var(--shadow-modal)', animation: 'modal-content 0.25s ease',
          }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>👋</div>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>Confirmer la déconnexion</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 24, lineHeight: 1.6 }}>
              Vous allez être déconnecté de la plateforme AutoTest. Vos sessions actives seront conservées.
            </p>
            <div style={{ display: 'flex', gap: 10 }}>
              <button onClick={() => setShowLogoutConfirm(false)} className="btn btn-ghost" style={{ flex: 1 }}>Annuler</button>
              <button onClick={handleLogout} className="btn btn-danger" style={{ flex: 1 }}>Se déconnecter</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
