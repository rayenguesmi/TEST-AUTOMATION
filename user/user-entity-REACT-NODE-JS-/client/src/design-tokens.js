// AUTOTEST Design Tokens
// Centralized design system tokens for the AUTOTEST platform

export const colors = {
  // Semantic colors
  success: '#22c55e',
  successMuted: '#16a34a20',
  danger: '#ef4444',
  dangerMuted: '#ef444420',
  warning: '#f59e0b',
  warningMuted: '#f59e0b20',
  info: '#3b82f6',
  infoMuted: '#3b82f620',
  ai: '#a855f7',          // Violet for AI-generated content
  aiMuted: '#a855f720',

  // Surface levels (dark-first)
  bgBase: '#0a0b0f',      // Deepest background
  bgRaised: '#111318',    // Cards, sidebars
  bgOverlay: '#1a1d27',   // Modals, dropdowns, elevated panels

  // Border
  border: '#ffffff12',
  borderMuted: '#ffffff08',

  // Text
  textPrimary: '#f1f5f9',
  textSecondary: '#94a3b8',
  textMuted: '#475569',
  textInverse: '#0a0b0f',

  // Brand / Primary (Electric blue)
  brand: '#6366f1',
  brandHover: '#818cf8',
  brandMuted: '#6366f120',
};

export const fonts = {
  sans: "'Geist', 'Inter', system-ui, sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
};

export const spacing = {
  sidebar: '220px',
  sidebarCollapsed: '56px',
  topbar: '60px',
};

export const radius = {
  sm: '6px',
  md: '10px',
  lg: '14px',
  xl: '20px',
  full: '9999px',
};

export const shadows = {
  card: '0 1px 3px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05)',
  modal: '0 25px 50px rgba(0,0,0,0.7)',
  glow: {
    brand: '0 0 20px rgba(99,102,241,0.3)',
    success: '0 0 20px rgba(34,197,94,0.3)',
    danger: '0 0 20px rgba(239,68,68,0.3)',
    ai: '0 0 20px rgba(168,85,247,0.3)',
  }
};

export const transitions = {
  fast: '120ms ease',
  normal: '150ms ease',
  slow: '300ms ease',
};

// Status badge color map
export const statusColors = {
  pass: { bg: '#22c55e20', text: '#22c55e', border: '#22c55e40' },
  fail: { bg: '#ef444420', text: '#ef4444', border: '#ef444440' },
  running: { bg: '#3b82f620', text: '#3b82f6', border: '#3b82f640' },
  pending: { bg: '#f59e0b20', text: '#f59e0b', border: '#f59e0b40' },
  healthy: { bg: '#22c55e20', text: '#22c55e', border: '#22c55e40' },
  degraded: { bg: '#f59e0b20', text: '#f59e0b', border: '#f59e0b40' },
  down: { bg: '#ef444420', text: '#ef4444', border: '#ef444440' },
  online: { bg: '#22c55e20', text: '#22c55e', border: '#22c55e40' },
  idle: { bg: '#f59e0b20', text: '#f59e0b', border: '#f59e0b40' },
  offline: { bg: '#64748b20', text: '#64748b', border: '#64748b40' },
  admin: { bg: '#a855f720', text: '#a855f7', border: '#a855f740' },
  user: { bg: '#6366f120', text: '#6366f1', border: '#6366f140' },
};
