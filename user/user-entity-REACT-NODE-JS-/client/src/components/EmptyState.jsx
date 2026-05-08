/**
 * EmptyState — Shows a contextual empty state with illustration, message, and CTA
 * @param {string} type - 'tests' | 'users' | 'projects' | 'urls' | 'logs' | 'notifications' | 'generic'
 * @param {string} title - Main heading
 * @param {string} message - Descriptive message  
 * @param {React.ReactNode} action - CTA button/element
 */

const emptyIllustrations = {
  tests: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <rect x="15" y="12" width="50" height="56" rx="6" fill="rgba(99,102,241,0.08)" stroke="rgba(99,102,241,0.2)" strokeWidth="1.5"/>
      <rect x="24" y="24" width="32" height="4" rx="2" fill="rgba(99,102,241,0.2)"/>
      <rect x="24" y="34" width="24" height="4" rx="2" fill="rgba(99,102,241,0.12)"/>
      <rect x="24" y="44" width="28" height="4" rx="2" fill="rgba(99,102,241,0.12)"/>
      <circle cx="58" cy="58" r="14" fill="rgba(99,102,241,0.1)" stroke="rgba(99,102,241,0.3)" strokeWidth="1.5"/>
      <path d="M52 58l4 4 8-8" stroke="rgba(99,102,241,0.7)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  users: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <circle cx="40" cy="30" r="14" fill="rgba(168,85,247,0.08)" stroke="rgba(168,85,247,0.2)" strokeWidth="1.5"/>
      <path d="M16 64c0-13.3 10.7-24 24-24s24 10.7 24 24" stroke="rgba(168,85,247,0.25)" strokeWidth="1.5" strokeLinecap="round"/>
      <circle cx="40" cy="30" r="8" fill="rgba(168,85,247,0.15)"/>
    </svg>
  ),
  projects: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <rect x="12" y="22" width="24" height="20" rx="4" fill="rgba(99,102,241,0.08)" stroke="rgba(99,102,241,0.2)" strokeWidth="1.5"/>
      <rect x="44" y="22" width="24" height="20" rx="4" fill="rgba(99,102,241,0.05)" stroke="rgba(99,102,241,0.15)" strokeWidth="1.5" strokeDasharray="3 2"/>
      <rect x="12" y="50" width="24" height="20" rx="4" fill="rgba(99,102,241,0.05)" stroke="rgba(99,102,241,0.15)" strokeWidth="1.5" strokeDasharray="3 2"/>
      <path d="M56 56v-6m0 0v-6m0 6h-6m6 0h6" stroke="rgba(99,102,241,0.5)" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  urls: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <circle cx="40" cy="40" r="26" fill="rgba(59,130,246,0.06)" stroke="rgba(59,130,246,0.2)" strokeWidth="1.5"/>
      <ellipse cx="40" cy="40" rx="12" ry="26" fill="none" stroke="rgba(59,130,246,0.15)" strokeWidth="1.5"/>
      <path d="M14 40h52M16 28h48M16 52h48" stroke="rgba(59,130,246,0.2)" strokeWidth="1.2"/>
    </svg>
  ),
  logs: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <rect x="12" y="16" width="56" height="48" rx="6" fill="rgba(15,15,20,0.5)" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5"/>
      <rect x="20" y="26" width="8" height="4" rx="2" fill="rgba(34,197,94,0.4)"/>
      <rect x="32" y="26" width="24" height="4" rx="2" fill="rgba(255,255,255,0.08)"/>
      <rect x="20" y="34" width="8" height="4" rx="2" fill="rgba(239,68,68,0.4)"/>
      <rect x="32" y="34" width="16" height="4" rx="2" fill="rgba(255,255,255,0.06)"/>
      <rect x="20" y="42" width="8" height="4" rx="2" fill="rgba(245,158,11,0.4)"/>
      <rect x="32" y="42" width="20" height="4" rx="2" fill="rgba(255,255,255,0.06)"/>
    </svg>
  ),
  notifications: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <path d="M40 16c-11 0-20 9-20 20v12l-4 8h48l-4-8V36c0-11-9-20-20-20z" fill="rgba(99,102,241,0.08)" stroke="rgba(99,102,241,0.2)" strokeWidth="1.5"/>
      <path d="M34 60a6 6 0 0012 0" stroke="rgba(99,102,241,0.3)" strokeWidth="1.5" strokeLinecap="round"/>
      <circle cx="40" cy="20" r="4" fill="rgba(99,102,241,0.15)"/>
    </svg>
  ),
  generic: (
    <svg width={80} height={80} viewBox="0 0 80 80" fill="none">
      <rect x="20" y="20" width="40" height="40" rx="8" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5"/>
      <path d="M40 32v8m0 8h.01" stroke="rgba(255,255,255,0.2)" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
};

export default function EmptyState({ type = 'generic', title, message, action }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '60px 24px', textAlign: 'center',
      animation: 'fade-in-up 0.4s ease',
    }}>
      {/* SVG Illustration */}
      <div style={{ marginBottom: 20, opacity: 0.85 }}>
        {emptyIllustrations[type] || emptyIllustrations.generic}
      </div>

      {/* Title */}
      <h3 style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8, maxWidth: 280 }}>
        {title}
      </h3>

      {/* Message */}
      {message && (
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', maxWidth: 320, lineHeight: 1.65, marginBottom: 24 }}>
          {message}
        </p>
      )}

      {/* CTA */}
      {action && (
        <div style={{ marginTop: message ? 0 : 24 }}>
          {action}
        </div>
      )}
    </div>
  );
}
