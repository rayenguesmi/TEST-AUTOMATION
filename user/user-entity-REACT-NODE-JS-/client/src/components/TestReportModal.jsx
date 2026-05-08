import { useState, useEffect } from 'react';
import Modal from './Modal';
import EmptyState from './EmptyState';
import { useToast } from './Toast';

const StatusBadge = ({ status }) => {
  const MAP = {
    pass:    { bg: 'rgba(34,197,94,0.12)',  text: '#22c55e', border: 'rgba(34,197,94,0.25)',  label: 'PASS' },
    fail:    { bg: 'rgba(239,68,68,0.12)',  text: '#ef4444', border: 'rgba(239,68,68,0.25)',  label: 'FAIL' },
    running: { bg: 'rgba(59,130,246,0.12)', text: '#3b82f6', border: 'rgba(59,130,246,0.25)', label: 'EN COURS' },
    pending: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)', label: 'EN ATTENTE' },
  };
  const s = MAP[status] || MAP.pending;
  return (
    <span style={{
      fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 99,
      background: s.bg, color: s.text, border: `1px solid ${s.border}`,
      display: 'inline-flex', alignItems: 'center', gap: 4, whiteSpace: 'nowrap',
    }}>
      {status === 'running' && (
        <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#3b82f6', animation: 'pulse-dot 1s ease-in-out infinite' }} />
      )}
      {s.label}
    </span>
  );
};

export default function TestReportModal({ test, open, onClose }) {
  const toast = useToast();
  const [tab, setTab] = useState('summary');

  useEffect(() => {
    if (test) setTab('summary');
  }, [open]);

  if (!test) return null;

  const hasTabs = ['summary', 'code', 'logs'];
  const tabLabels = {
    summary: 'Résumé',
    code: 'Code Généré',
    logs: "Logs d'exécution",
  };
  const code = test.generatedScript || `# Aucun script disponible pour ce test.\n# Lancez un nouveau test via "+ Nouveau Test".`;

  return (
    <Modal
      isOpen={open}
      onClose={onClose}
      title={test.name || test.url}
      size="lg"
      footer={
        <>
          <button className="btn btn-ghost" style={{ fontSize: 12 }}
            onClick={() => toast.info('Export en cours', 'Téléchargement du rapport PDF')}>
            📄 Export PDF
          </button>
          <button className="btn btn-ghost" style={{ fontSize: 12 }}
            onClick={() => { navigator.clipboard.writeText(code); toast.success('Code copié !', ''); }}>
            📋 Copier le code
          </button>
          <button className="btn btn-ghost" style={{ fontSize: 12 }} onClick={onClose}>
            Fermer
          </button>
        </>
      }
    >
      {/* ── Header KPIs ──────────────────────────────────────────────────── */}
      <div style={{
        display: 'flex', gap: 16, marginBottom: 20, padding: 16,
        background: 'var(--bg-raised)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)',
      }}>
        {[
          { label: 'Statut',  node: <StatusBadge status={test.status || 'pass'} /> },
          {
            label: 'Durée',
            node: <span style={{ fontSize: 14, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
              {test.report?.duration_seconds ? `${test.report.duration_seconds.toFixed(1)}s` : test.duration || '—'}
            </span>,
          },
          { label: 'Projet',  node: <span style={{ fontSize: 12, fontWeight: 600 }}>{test.project || '—'}</span> },
          { label: 'Date',    node: <span style={{ fontSize: 11 }}>{test.date || '—'}</span> },
        ].map(({ label, node }) => (
          <div key={label} style={{ flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
              {label}
            </div>
            {node}
          </div>
        ))}
      </div>

      {/* ── Tabs ─────────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
        {hasTabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '8px 16px', fontSize: 12, fontWeight: 500, cursor: 'pointer',
            background: 'transparent', border: 'none',
            color: tab === t ? 'var(--color-brand)' : 'var(--text-muted)',
            borderBottom: `2px solid ${tab === t ? 'var(--color-brand)' : 'transparent'}`,
            marginBottom: -1, transition: 'all 120ms ease',
          }}>{tabLabels[t]}</button>
        ))}
      </div>

      {/* ── Tab: Résumé ─────────────────────────────────────────────────── */}
      {tab === 'summary' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {test.report ? (
            <>
              {/* KPI row */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
                {[
                  { label: 'Total',   value: test.report.total ?? '—',  color: 'var(--text-primary)' },
                  { label: 'Passés',  value: test.report.passed ?? '—', color: 'var(--color-success)' },
                  { label: 'Échoués', value: (test.report.failed ?? 0) + (test.report.errors ?? 0), color: 'var(--color-danger)' },
                  { label: 'Durée',   value: `${(test.report.duration_seconds || 0).toFixed(1)}s`, color: 'var(--text-muted)' },
                ].map(({ label, value, color }) => (
                  <div key={label} className="glass-card" style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'var(--font-mono)', color }}>{value}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
                  </div>
                ))}
              </div>

              {/* Per-test results */}
              {(test.report.tests || []).length > 0 && (
                <div className="glass-card" style={{ overflow: 'hidden' }}>
                  {(test.report.tests || []).map((tc, i) => (
                    <div key={i} style={{
                      display: 'flex', alignItems: 'center', gap: 10,
                      padding: '8px 14px', borderBottom: '1px solid var(--border-muted)', fontSize: 11,
                    }}>
                      <span style={{ fontSize: 13, fontWeight: 700, flexShrink: 0, color: tc.statut === 'PASS' ? 'var(--color-success)' : 'var(--color-danger)' }}>
                        {tc.statut === 'PASS' ? '✓' : '✗'}
                      </span>
                      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
                        {tc.name}
                      </span>
                      <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', flexShrink: 0 }}>
                        {(tc.durée_secondes || 0).toFixed(2)}s
                      </span>
                      <StatusBadge status={tc.statut === 'PASS' ? 'pass' : 'fail'} />
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <EmptyState
              type="generic"
              title="Aucun résultat d'exécution"
              message="Le rapport sera disponible après la prochaine génération complète."
            />
          )}
        </div>
      )}

      {/* ── Tab: Code généré ─────────────────────────────────────────────── */}
      {tab === 'code' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginBottom: 8 }}>
            <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}
              onClick={() => { navigator.clipboard.writeText(code); toast.success('Copié !', ''); }}>
              📋 Copier
            </button>
          </div>
          <pre style={{
            background: 'rgba(0,0,0,0.4)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)', padding: 16,
            fontFamily: 'var(--font-mono)', fontSize: 11, lineHeight: 1.7,
            overflowX: 'auto', color: '#e2e8f0', maxHeight: 380, overflowY: 'auto',
          }}>
            <code>{code}</code>
          </pre>
        </div>
      )}

      {/* ── Tab: Logs ─────────────────────────────────────────────────────── */}
      {tab === 'logs' && (
        <div style={{
          background: 'rgba(0,0,0,0.4)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)', padding: 12,
          fontFamily: 'var(--font-mono)', fontSize: 11, maxHeight: 320, overflowY: 'auto',
        }}>
          {test.logs?.length ? test.logs.map((l, i) => {
            const lvl = (l.level || 'info').toUpperCase();
            const COLOR = { INFO: '#3b82f6', ERROR: '#ef4444', WARNING: '#f59e0b', WARN: '#f59e0b' };
            return (
              <div key={i} style={{ display: 'flex', gap: 12, padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <span style={{ color: COLOR[lvl] || '#3b82f6', fontWeight: 700, width: 56, flexShrink: 0 }}>{lvl}</span>
                <span style={{ color: 'var(--text-secondary)', wordBreak: 'break-word' }}>{l.message}</span>
              </div>
            );
          }) : (
            <div style={{ color: 'var(--text-muted)', padding: 8 }}>Aucun log disponible.</div>
          )}
        </div>
      )}
    </Modal>
  );
}
