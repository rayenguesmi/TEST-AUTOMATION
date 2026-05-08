import { useState } from 'react';
import Topbar from '../components/Topbar';

const mockUrls = [
  { id: 1, nom: 'SauceDemo', url: 'https://www.saucedemo.com', uptime: '99.8%', latence: '245ms', statut: 'UP', checked: 'il y a 2 min' },
  { id: 2, nom: 'DemoWebShop', url: 'https://demowebshop.tricentis.com', uptime: '98.2%', latence: '420ms', statut: 'UP', checked: 'il y a 5 min' },
  { id: 3, nom: 'Demoblaze', url: 'https://www.demoblaze.com', uptime: '95.1%', latence: '812ms', statut: 'DOWN', checked: 'il y a 1 min' },
];

const labelStyle = {
  display: 'block', fontSize: 11, fontWeight: 600,
  color: 'var(--text-muted)', textTransform: 'uppercase',
  letterSpacing: '0.07em', marginBottom: 6,
};

const selectStyle = {
  background: 'rgba(255,255,255,0.04)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-md)',
  color: 'var(--text-primary)',
  padding: '9px 13px',
  fontSize: 13,
  fontFamily: 'var(--font-sans)',
  outline: 'none',
  width: '100%',
  cursor: 'pointer',
  appearance: 'none',
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2322d3ee' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
  backgroundRepeat: 'no-repeat',
  backgroundPosition: 'right 12px center',
  paddingRight: 36,
};

export default function UrlsSurveillees() {
  const [urls, setUrls] = useState(mockUrls);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ nom: '', url: '', frequence: '5min' });

  const handleAdd = (e) => {
    e.preventDefault();
    setUrls(prev => [...prev, {
      id: Date.now(),
      nom: form.nom,
      url: form.url,
      uptime: '—',
      latence: '—',
      statut: 'UP',
      checked: 'à l\'instant',
    }]);
    setForm({ nom: '', url: '', frequence: '5min' });
    setShowModal(false);
  };

  const handleDelete = (id) => setUrls(prev => prev.filter(u => u.id !== id));

  const upCount = urls.filter(u => u.statut === 'UP').length;
  const downCount = urls.filter(u => u.statut === 'DOWN').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Topbar />
      <div className="page-content">

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              URLs Surveillées
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>
              {urls.length} URL{urls.length > 1 ? 's' : ''} en surveillance
            </p>
          </div>
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            + Ajouter
          </button>
        </div>

        {/* KPI row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 24 }}>
          {[
            { label: 'Total', value: urls.length, color: 'var(--color-brand)' },
            { label: 'En ligne', value: upCount, color: 'var(--color-success)' },
            { label: 'Hors ligne', value: downCount, color: downCount > 0 ? 'var(--color-danger)' : 'var(--text-muted)' },
          ].map(kpi => (
            <div key={kpi.label} className="glass-card" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 22, fontWeight: 800, color: kpi.color, fontFamily: 'var(--font-mono)' }}>
                {kpi.value}
              </span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{kpi.label}</span>
            </div>
          ))}
        </div>

        {/* URL list */}
        {urls.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>🌐</div>
            <div style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>Aucune URL surveillée</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 24 }}>Ajoutez une URL pour démarrer la surveillance.</div>
            <button onClick={() => setShowModal(true)} className="btn btn-primary">+ Ajouter une URL</button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {urls.map(u => (
              <div key={u.id} className="glass-card card-hover" style={{ padding: '18px 24px', display: 'flex', alignItems: 'center', gap: 20 }}>

                {/* Status dot */}
                <span style={{
                  width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
                  background: u.statut === 'UP' ? 'var(--color-success)' : 'var(--color-danger)',
                  boxShadow: `0 0 8px ${u.statut === 'UP' ? 'var(--color-success)' : 'var(--color-danger)'}`,
                  animation: 'pulse-dot 2s ease-in-out infinite',
                }} />

                {/* Name + URL */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{u.nom}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {u.url}
                  </div>
                </div>

                {/* Metrics */}
                <div style={{ display: 'flex', gap: 28, flexShrink: 0, alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-success)', fontFamily: 'var(--font-mono)' }}>{u.uptime}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>Uptime</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{u.latence}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>Latence</div>
                  </div>
                  <span style={{
                    fontSize: 11, fontWeight: 700,
                    padding: '3px 12px', borderRadius: 99,
                    background: u.statut === 'UP' ? 'rgba(34,197,94,0.12)' : 'rgba(239,68,68,0.12)',
                    color: u.statut === 'UP' ? 'var(--color-success)' : 'var(--color-danger)',
                    border: `1px solid ${u.statut === 'UP' ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)'}`,
                  }}>
                    {u.statut}
                  </span>
                </div>

                {/* Last check + delete */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{u.checked}</span>
                  <button
                    onClick={() => handleDelete(u.id)}
                    className="btn btn-danger"
                    style={{ padding: '5px 8px', fontSize: 12 }}
                    aria-label="Supprimer"
                  >
                    <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
                      <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add URL Modal */}
      {showModal && (
        <div
          onClick={() => setShowModal(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, animation: 'modal-backdrop 0.2s ease' }}
        >
          <div onClick={e => e.stopPropagation()} style={{ background: 'var(--bg-overlay)', border: '1px solid var(--border)', borderRadius: 20, padding: 32, maxWidth: 440, width: '90%', animation: 'modal-content 0.25s ease', boxShadow: 'var(--shadow-modal)' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>Ajouter une URL</h3>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 24 }}>
              L'URL sera vérifiée à la fréquence choisie.
            </p>
            <form onSubmit={handleAdd} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={labelStyle}>Nom</label>
                <input autoFocus className="input-base" type="text" placeholder="Ex : Mon Site" value={form.nom} onChange={e => setForm(p => ({ ...p, nom: e.target.value }))} required />
              </div>
              <div>
                <label style={labelStyle}>URL</label>
                <input className="input-base" type="url" placeholder="https://..." value={form.url} onChange={e => setForm(p => ({ ...p, url: e.target.value }))} required />
              </div>
              <div>
                <label style={labelStyle}>Fréquence de vérification</label>
                <select style={selectStyle} value={form.frequence} onChange={e => setForm(p => ({ ...p, frequence: e.target.value }))}>
                  <option value="5min">Toutes les 5 min</option>
                  <option value="15min">Toutes les 15 min</option>
                  <option value="1h">Toutes les heures</option>
                  <option value="1j">1 fois par jour</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-ghost" style={{ flex: 1 }}>Annuler</button>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Ajouter</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
