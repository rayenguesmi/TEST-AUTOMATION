import { useState } from 'react';
import { Link } from 'react-router-dom';
import { registerUser } from '../api/auth';

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [status, setStatus] = useState({ loading: false, success: '', error: '' });
  const [showPass, setShowPass] = useState(false);
  const [strength, setStrength] = useState(0);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    if (e.target.name === 'password') {
      const p = e.target.value;
      let s = 0;
      if (p.length >= 6) s++;
      if (p.length >= 10) s++;
      if (/[A-Z]/.test(p)) s++;
      if (/[0-9]/.test(p)) s++;
      if (/[^a-zA-Z0-9]/.test(p)) s++;
      setStrength(s);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, success: '', error: '' });
    try {
      const { data } = await registerUser(form);
      setStatus({ loading: false, success: data.message || 'Inscription réussie ! Vérifiez votre email.', error: '' });
      setForm({ name: '', email: '', password: '' });
      setStrength(0);
    } catch (err) {
      setStatus({
        loading: false, success: '',
        error: err.response?.data?.message || 'Échec de l\'inscription. Réessayez.',
      });
    }
  };

  const strengthColors = ['var(--color-danger)', 'var(--color-danger)', 'var(--color-warning)', 'var(--color-warning)', '#22c55e'];
  const strengthLabels = ['', 'Très faible', 'Faible', 'Moyen', 'Fort', 'Très fort'];

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-base)', padding: 24, position: 'relative', overflow: 'hidden',
    }}>
      {/* Background glow */}
      <div style={{
        position: 'absolute', top: '15%', right: '15%',
        width: 500, height: 500, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(168,85,247,0.07) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: '10%', left: '10%',
        width: 350, height: 350, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(99,102,241,0.07) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div style={{ width: '100%', maxWidth: 420, animation: 'fade-in-up 0.4s ease' }}>
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <img src="/logo.png" alt="AutoTest" style={{
            width: 72, height: 72,
            objectFit: 'contain',
            margin: '0 auto 16px',
            display: 'block',
            filter: 'drop-shadow(0 0 20px rgba(34,211,238,0.35))',
          }} />
          <h1 style={{ fontSize: 24, fontWeight: 800, letterSpacing: '-0.04em', marginBottom: 6 }}>
            Créer un compte
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Rejoignez la plateforme AutoTest AI
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'var(--bg-raised)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xl)', padding: 32,
          boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
        }}>
          {/* Success banner */}
          {status.success && (
            <div style={{
              background: 'rgba(34,197,94,0.10)', border: '1px solid rgba(34,197,94,0.25)',
              borderRadius: 'var(--radius-md)', padding: '12px 14px',
              color: '#22c55e', fontSize: 13, fontWeight: 500, marginBottom: 20,
              display: 'flex', gap: 8, alignItems: 'center',
            }}>
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0" />
              </svg>
              {status.success}
            </div>
          )}

          {/* Error banner */}
          {status.error && (
            <div style={{
              background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.25)',
              borderRadius: 'var(--radius-md)', padding: '12px 14px',
              color: '#ef4444', fontSize: 13, fontWeight: 500, marginBottom: 20,
              display: 'flex', gap: 8, alignItems: 'center',
            }}>
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0" />
              </svg>
              {status.error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Name */}
            <div>
              <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>
                Nom complet
              </label>
              <input
                name="name" type="text"
                placeholder="Rayen Guesmi"
                value={form.name} onChange={handleChange} required
                className="input-base"
              />
            </div>

            {/* Email */}
            <div>
              <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>
                Email
              </label>
              <input
                name="email" type="email"
                placeholder="nom@exemple.com"
                value={form.email} onChange={handleChange} required
                className="input-base"
              />
            </div>

            {/* Password + strength */}
            <div>
              <label style={{ display: 'block', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>
                Mot de passe
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  name="password" type={showPass ? 'text' : 'password'}
                  placeholder="8 caractères minimum"
                  value={form.password} onChange={handleChange} required minLength={6}
                  className="input-base"
                  style={{ paddingRight: 42 }}
                />
                <button type="button" onClick={() => setShowPass(v => !v)} style={{
                  position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)',
                  padding: 4, display: 'flex', transition: 'color 120ms ease',
                }}
                onMouseEnter={e => e.currentTarget.style.color = 'var(--text-primary)'}
                onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}>
                  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
                    <path d={showPass ? "M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" : "M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 100 6 3 3 0 000-6z"} />
                  </svg>
                </button>
              </div>
              {/* Strength bar */}
              {form.password.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
                    {[1, 2, 3, 4, 5].map(i => (
                      <div key={i} style={{
                        flex: 1, height: 3, borderRadius: 2,
                        background: i <= strength ? (strengthColors[strength - 1] || '#64748b') : 'rgba(255,255,255,0.08)',
                        transition: 'background 200ms ease',
                      }} />
                    ))}
                  </div>
                  <span style={{ fontSize: 10, color: strength > 0 ? strengthColors[strength - 1] : 'var(--text-muted)', fontWeight: 500 }}>
                    {strengthLabels[strength]}
                  </span>
                </div>
              )}
            </div>

            {/* Submit */}
            <button type="submit" disabled={status.loading} style={{
              width: '100%', padding: '12px 0', borderRadius: 'var(--radius-md)', marginTop: 4,
              background: status.loading ? 'rgba(99,102,241,0.6)' : 'var(--color-brand)',
              border: 'none', cursor: status.loading ? 'not-allowed' : 'pointer',
              color: '#fff', fontSize: 14, fontWeight: 700, letterSpacing: '-0.01em',
              transition: 'all 120ms ease',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              boxShadow: status.loading ? 'none' : 'var(--shadow-glow-brand)',
            }}
            onMouseEnter={e => { if (!status.loading) e.currentTarget.style.background = 'var(--color-brand-hover)'; }}
            onMouseLeave={e => { if (!status.loading) e.currentTarget.style.background = 'var(--color-brand)'; }}>
              {status.loading ? (
                <>
                  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
                    style={{ animation: 'spin-slow 1s linear infinite' }}>
                    <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Inscription en cours…
                </>
              ) : 'Créer mon compte →'}
            </button>
          </form>

          {/* Divider → Login */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '20px 0' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>ou</span>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
          </div>

          <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
            Déjà un compte ?{' '}
            <Link to="/login" style={{ color: 'var(--color-brand)', fontWeight: 600, textDecoration: 'none' }}
              onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
              onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}>
              Se connecter
            </Link>
          </p>
        </div>

        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', marginTop: 24 }}>
          En créant un compte, vous acceptez les{' '}
          <span style={{ color: 'var(--color-brand)', cursor: 'pointer' }}>Conditions d'utilisation</span>
        </p>
      </div>
    </div>
  );
}
