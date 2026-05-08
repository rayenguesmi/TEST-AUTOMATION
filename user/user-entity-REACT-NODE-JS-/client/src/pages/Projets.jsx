import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';

const mockProjects = [
  {
    id: 1, nom: 'SauceDemo', emoji: '🛒',
    desc: 'Tests e-commerce SauceDemo',
    tests: 12, dernierRun: '2026-04-30',
    statut: 'ok', tauxSucces: 91,
  },
  {
    id: 2, nom: 'DemoWebShop', emoji: '🏪',
    desc: 'Boutique Tricentis — Electronics & Computers',
    tests: 8, dernierRun: '2026-04-30',
    statut: 'issue', tauxSucces: 62,
  },
  {
    id: 3, nom: 'Demoblaze', emoji: '📱',
    desc: 'Marketplace Demoblaze — Phones & Laptops',
    tests: 6, dernierRun: '2026-04-29',
    statut: 'ok', tauxSucces: 83,
  },
];

export default function Projets() {
  const navigate = useNavigate();
  const [showNewModal, setShowNewModal] = useState(false);
  const [projects, setProjects] = useState(mockProjects);
  const [newNom, setNewNom] = useState('');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newNom.trim()) return;
    setProjects(prev => [...prev, {
      id: Date.now(), nom: newNom, emoji: '🧪',
      desc: 'Nouveau projet', tests: 0,
      dernierRun: '—', statut: 'ok', tauxSucces: 100,
    }]);
    setNewNom('');
    setShowNewModal(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Topbar />
      <div className="page-content">

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Projets
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>
              {projects.length} projet{projects.length > 1 ? 's' : ''} actif{projects.length > 1 ? 's' : ''}
            </p>
          </div>
          <button onClick={() => setShowNewModal(true)} className="btn btn-primary">
            + Nouveau Projet
          </button>
        </div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 }}>

          {/* Add card */}
          <div
            onClick={() => setShowNewModal(true)}
            style={{
              background: 'transparent',
              border: '1.5px dashed rgba(34,211,238,0.3)',
              borderRadius: 16, padding: 28, cursor: 'pointer',
              display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              gap: 10, minHeight: 180, transition: 'all 200ms ease',
              color: 'var(--color-brand)',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--color-brand)';
              e.currentTarget.style.background = 'rgba(34,211,238,0.04)';
              e.currentTarget.style.boxShadow = '0 0 20px rgba(34,211,238,0.1)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'rgba(34,211,238,0.3)';
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span style={{ fontSize: 32, opacity: 0.7 }}>+</span>
            <span style={{ fontSize: 13, fontWeight: 600 }}>Nouveau Projet</span>
          </div>

          {/* Project cards */}
          {projects.map(proj => (
            <div
              key={proj.id}
              onClick={() => navigate('/urls')}
              className="glass-card card-hover"
              style={{ padding: 24, cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: 0 }}
            >
              {/* Top row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: 'rgba(34,211,238,0.08)',
                  border: '1px solid rgba(34,211,238,0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20,
                }}>
                  {proj.emoji}
                </div>
                <span style={{
                  width: 10, height: 10, borderRadius: '50%', marginTop: 4, flexShrink: 0,
                  background: proj.statut === 'ok' ? 'var(--color-success)' : 'var(--color-danger)',
                  boxShadow: `0 0 8px ${proj.statut === 'ok' ? 'var(--color-success)' : 'var(--color-danger)'}`,
                  animation: 'pulse-dot 2s ease-in-out infinite',
                }} />
              </div>

              {/* Name + desc */}
              <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                {proj.nom}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 18, lineHeight: 1.5 }}>
                {proj.desc}
              </div>

              {/* Progress bar */}
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Taux de succès</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color: proj.tauxSucces >= 80 ? 'var(--color-success)' : 'var(--color-warning)', fontFamily: 'var(--font-mono)' }}>
                    {proj.tauxSucces}%
                  </span>
                </div>
                <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 99, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', borderRadius: 99,
                    width: `${proj.tauxSucces}%`,
                    background: proj.tauxSucces >= 80 ? 'var(--color-success)' : 'var(--color-warning)',
                    boxShadow: `0 0 8px ${proj.tauxSucces >= 80 ? 'var(--color-success)' : 'var(--color-warning)'}`,
                    animation: 'bar-grow 0.6s ease forwards',
                  }} />
                </div>
              </div>

              {/* Footer */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                  fontSize: 11, padding: '3px 10px', borderRadius: 99,
                  background: 'rgba(34,211,238,0.08)', color: 'var(--color-brand)',
                  border: '1px solid rgba(34,211,238,0.2)', fontWeight: 600,
                }}>
                  {proj.tests} test{proj.tests !== 1 ? 's' : ''}
                </span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {proj.dernierRun !== '—' ? `Dernier : ${proj.dernierRun}` : 'Jamais exécuté'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* New project modal */}
      {showNewModal && (
        <div
          onClick={() => setShowNewModal(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, animation: 'modal-backdrop 0.2s ease' }}
        >
          <div onClick={e => e.stopPropagation()} style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border)', borderRadius: 20, padding: 32, maxWidth: 400, width: '90%', animation: 'modal-content 0.25s ease', boxShadow: 'var(--shadow-modal)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>Nouveau Projet</h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 24 }}>Donnez un nom à votre projet de tests.</p>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>
                  Nom du projet
                </label>
                <input
                  autoFocus className="input-base" type="text"
                  placeholder="Ex : Mon Projet E-commerce"
                  value={newNom} onChange={e => setNewNom(e.target.value)} required
                />
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <button type="button" onClick={() => setShowNewModal(false)} className="btn btn-ghost" style={{ flex: 1 }}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Créer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
