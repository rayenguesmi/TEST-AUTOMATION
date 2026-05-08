import { useState, useEffect } from 'react';
import Topbar from '../components/Topbar';
import NewTestWizard from '../components/NewTestWizard';
import TestReportModal from '../components/TestReportModal';
import { fetchMyTests } from '../api/auth';

const mockProjects = [
  { id: 1, nom: 'SauceDemo',   emoji: '🛒', tests: 12, statut: 'ok'    },
  { id: 2, nom: 'DemoWebShop', emoji: '🏪', tests: 8,  statut: 'issue' },
  { id: 3, nom: 'Demoblaze',   emoji: '📱', tests: 6,  statut: 'ok'    },
];

const STATUS = {
  PASS:    { bg: 'rgba(34,197,94,0.12)',  color: '#22c55e', border: 'rgba(34,197,94,0.3)'  },
  FAIL:    { bg: 'rgba(239,68,68,0.12)',  color: '#ef4444', border: 'rgba(239,68,68,0.3)'  },
  RUNNING: { bg: 'rgba(34,211,238,0.12)', color: '#22d3ee', border: 'rgba(34,211,238,0.3)' },
};

const TABS = ['TOUS', 'PASS', 'FAIL', 'RUNNING'];

const Icon = ({ d, size = 15 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

// ── Map a DB test record to the table + modal shape ──────────────────────────
const mapTest = (t) => {
  const passed = t.report?.passed ?? 0;
  const statut =
    t.status === 'completed' ? (passed > 0 ? 'PASS' : 'FAIL')
    : t.status === 'failed'  ? 'FAIL'
    : 'RUNNING';
  const statusModal =
    t.status === 'completed' ? (passed > 0 ? 'pass' : 'fail')
    : t.status === 'failed'  ? 'fail'
    : t.status === 'running' ? 'running'
    : 'pending';
  return {
    // table fields
    id:     t._id,
    nom:    t.targetUrl,
    url:    t.targetUrl,
    statut,
    date:   new Date(t.createdAt).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }),
    duree:  t.report?.duration_seconds ? `${t.report.duration_seconds.toFixed(1)}s` : '—',
    projet: t.analysisType || '—',
    // modal fields
    name:            t.targetUrl,
    status:          statusModal,
    report:          t.report          || null,
    reportHtmlUrl:   t.reportHtmlUrl   || null,
    generatedScript: t.generatedScript || null,
    logs:            t.logs            || [],
    duration:        t.report?.duration_seconds ? `${t.report.duration_seconds.toFixed(1)}s` : null,
    project:         t.analysisType    || '—',
  };
};

export default function MesTests() {
  const [filter,       setFilter]       = useState('TOUS');
  const [tests,        setTests]        = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [wizardOpen,   setWizardOpen]   = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [assignTarget, setAssignTarget] = useState(null);

  // ── Load real tests from API ─────────────────────────────────────────────
  useEffect(() => {
    fetchMyTests()
      .then(({ data }) => setTests((data.data || []).map(mapTest)))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === 'TOUS' ? tests : tests.filter(t => t.statut === filter);

  const handleDelete = (id) => setTests(prev => prev.filter(t => t.id !== id));

  const handleAssign = (testId, projetNom) => {
    setTests(prev => prev.map(t => t.id === testId ? { ...t, projet: projetNom, project: projetNom } : t));
    setAssignTarget(null);
  };

  const counts = TABS.reduce((acc, tab) => {
    acc[tab] = tab === 'TOUS' ? tests.length : tests.filter(t => t.statut === tab).length;
    return acc;
  }, {});

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Topbar />
      <div className="page-content">

        {/* ── Header ──────────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Mes Tests
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>
              {loading ? '…' : `${tests.length} test${tests.length !== 1 ? 's' : ''} au total`}
            </p>
          </div>
          <button onClick={() => setWizardOpen(true)} className="btn btn-primary">
            + Nouveau Test
          </button>
        </div>

        {/* ── Filter tabs ─────────────────────────────────────────────────── */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {TABS.map(tab => {
            const active = filter === tab;
            return (
              <button key={tab} onClick={() => setFilter(tab)} style={{
                padding: '6px 16px', borderRadius: 99, fontSize: 12, fontWeight: 600,
                cursor: 'pointer', transition: 'all 200ms ease', border: 'none',
                background: active ? 'var(--color-brand)' : 'rgba(255,255,255,0.05)',
                color: active ? '#000' : 'var(--text-muted)',
                outline: active ? 'none' : '1px solid var(--border)',
                boxShadow: active ? '0 0 14px rgba(34,211,238,0.3)' : 'none',
              }}>
                {tab}
                {counts[tab] > 0 && (
                  <span style={{
                    marginLeft: 6, fontSize: 10, padding: '1px 6px', borderRadius: 99,
                    background: active ? 'rgba(0,0,0,0.2)' : 'rgba(255,255,255,0.08)',
                    color: active ? '#000' : 'var(--text-muted)',
                  }}>{counts[tab]}</span>
                )}
              </button>
            );
          })}
        </div>

        {/* ── Loading skeleton ─────────────────────────────────────────────── */}
        {loading ? (
          <div className="glass-card" style={{ padding: 20 }}>
            {[1, 2, 3].map(i => (
              <div key={i} style={{ display: 'flex', gap: 16, padding: '14px 0', borderBottom: '1px solid var(--border-muted)', alignItems: 'center' }}>
                <div style={{ flex: 2, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.06)' }} />
                <div style={{ flex: 2, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.04)' }} />
                <div style={{ flex: 1, height: 20, borderRadius: 99, background: 'rgba(255,255,255,0.06)' }} />
                <div style={{ flex: 1, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.04)' }} />
                <div style={{ flex: 1, height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.04)' }} />
                <div style={{ width: 120, height: 28, borderRadius: 8, background: 'rgba(255,255,255,0.06)' }} />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          /* ── Empty state ────────────────────────────────────────────────── */
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>
              {tests.length === 0 ? "Aucun test pour l’instant" : `Aucun test « ${filter} »`}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 24 }}>
              {tests.length === 0
                ? 'Lancez votre premier test IA pour voir les résultats ici.'
                : `Aucun test ne correspond au filtre « ${filter} ».`}
            </div>
            <button onClick={() => setWizardOpen(true)} className="btn btn-primary">
              + Nouveau Test
            </button>
          </div>
        ) : (
          /* ── Table ──────────────────────────────────────────────────────── */
          <div className="glass-card" style={{ overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  {['Nom du test', 'URL', 'Statut', 'Dernière exécution', 'Durée', 'Actions'].map(h => (
                    <th key={h} style={{
                      padding: '12px 16px', textAlign: 'left',
                      fontSize: 11, fontWeight: 600,
                      color: 'var(--text-muted)', textTransform: 'uppercase',
                      letterSpacing: '0.07em', whiteSpace: 'nowrap',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((test, i) => {
                  const s = STATUS[test.statut] || STATUS.RUNNING;
                  return (
                    <tr key={test.id}
                      style={{ borderBottom: i < filtered.length - 1 ? '1px solid var(--border-muted)' : 'none', transition: 'background 150ms ease' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {test.nom}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{test.projet}</div>
                      </td>
                      <td style={{ padding: '14px 16px', maxWidth: 180 }}>
                        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
                          {test.url}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          display: 'inline-flex', alignItems: 'center', gap: 5,
                          padding: '3px 10px', borderRadius: 99, fontSize: 11, fontWeight: 700,
                          background: s.bg, color: s.color, border: `1px solid ${s.border}`,
                        }}>
                          {test.statut === 'RUNNING' && (
                            <span style={{ width: 6, height: 6, borderRadius: '50%', background: s.color, animation: 'pulse-dot 1s ease-in-out infinite', flexShrink: 0 }} />
                          )}
                          {test.statut}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 12, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {test.date}
                      </td>
                      <td style={{ padding: '14px 16px', fontSize: 12, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', whiteSpace: 'nowrap' }}>
                        {test.duree}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', gap: 8 }}>
                          {/* Voir rapport */}
                          <button
                            onClick={() => setSelectedTest(test)}
                            className="btn btn-ghost"
                            style={{ padding: '5px 12px', fontSize: 12 }}
                          >
                            <Icon d="M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" size={13} />
                            Voir
                          </button>

                          {/* Associer à un projet */}
                          <button
                            onClick={() => setAssignTarget(test)}
                            title="Associer à un projet"
                            style={{
                              padding: '5px 10px', fontSize: 12, cursor: 'pointer',
                              display: 'inline-flex', alignItems: 'center', gap: 5,
                              background: 'rgba(34,211,238,0.08)',
                              border: '1px solid rgba(34,211,238,0.3)',
                              borderRadius: 'var(--radius-md)',
                              color: 'var(--color-brand)',
                              transition: 'all 200ms ease',
                              fontFamily: 'var(--font-sans)', fontWeight: 600,
                            }}
                            onMouseEnter={e => { e.currentTarget.style.background = 'var(--color-brand)'; e.currentTarget.style.color = '#000'; }}
                            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(34,211,238,0.08)'; e.currentTarget.style.color = 'var(--color-brand)'; }}
                          >
                            <Icon d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" size={13} />
                            Projet
                          </button>

                          {/* Supprimer */}
                          <button
                            onClick={() => handleDelete(test.id)}
                            className="btn btn-danger"
                            style={{ padding: '5px 10px', fontSize: 13 }}
                            aria-label="Supprimer"
                          >
                            <Icon d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Assign to project modal ──────────────────────────────────────────── */}
      {assignTarget && (
        <div
          onClick={() => setAssignTarget(null)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border)', borderRadius: 20, padding: 28, maxWidth: 460, width: '90%', boxShadow: 'var(--shadow-modal)' }}
          >
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                Associer à un projet
              </h3>
              <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                Test : <span style={{ color: 'var(--color-brand)', fontWeight: 600 }}>{assignTarget.nom}</span>
                {assignTarget.projet && assignTarget.projet !== '—' && (
                  <span style={{ marginLeft: 8 }}>
                    · Projet actuel : <strong style={{ color: 'var(--text-secondary)' }}>{assignTarget.projet}</strong>
                  </span>
                )}
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
              {mockProjects.map(proj => {
                const isCurrent = assignTarget.projet === proj.nom;
                return (
                  <div
                    key={proj.id}
                    onClick={() => handleAssign(assignTarget.id, proj.nom)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 14,
                      padding: '14px 16px', borderRadius: 12, cursor: 'pointer',
                      border: `1.5px solid ${isCurrent ? 'var(--color-brand)' : 'var(--border)'}`,
                      background: isCurrent ? 'var(--bg-active)' : 'rgba(255,255,255,0.03)',
                      transition: 'all 200ms ease',
                      boxShadow: isCurrent ? 'var(--shadow-glow-brand)' : 'none',
                    }}
                    onMouseEnter={e => { if (!isCurrent) { e.currentTarget.style.borderColor = 'rgba(34,211,238,0.3)'; e.currentTarget.style.background = 'rgba(34,211,238,0.04)'; }}}
                    onMouseLeave={e => { if (!isCurrent) { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'rgba(255,255,255,0.03)'; }}}
                  >
                    <div style={{ width: 38, height: 38, borderRadius: 10, background: 'rgba(34,211,238,0.08)', border: '1px solid rgba(34,211,238,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, flexShrink: 0 }}>
                      {proj.emoji}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 14, fontWeight: 600, color: isCurrent ? 'var(--color-brand)' : 'var(--text-primary)' }}>
                        {proj.nom}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
                        {proj.tests} test{proj.tests > 1 ? 's' : ''}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: proj.statut === 'ok' ? 'var(--color-success)' : 'var(--color-danger)' }} />
                      {isCurrent && (
                        <span style={{ fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 99, background: 'var(--color-brand)', color: '#000' }}>
                          Actuel
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setAssignTarget(null)} className="btn btn-ghost">Annuler</button>
            </div>
          </div>
        </div>
      )}

      {/* ── New Test Wizard ──────────────────────────────────────────────────── */}
      <NewTestWizard
        open={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onTestDone={(newTest) => {
          setTests(prev => [
            mapTest({ ...newTest, createdAt: new Date().toISOString() }),
            ...prev,
          ]);
          setWizardOpen(false);
        }}
      />

      {/* ── Test Report Modal ────────────────────────────────────────────────── */}
      <TestReportModal
        test={selectedTest}
        open={!!selectedTest}
        onClose={() => setSelectedTest(null)}
      />
    </div>
  );
}
