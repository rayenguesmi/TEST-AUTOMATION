import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [status, setStatus] = useState({ loading: false, error: '' });
  const [showPass, setShowPass] = useState(false);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, error: '' });
    try {
      const data = await login(form);
      if (data.success) {
        navigate(data.data.role === 'admin' ? '/admin/dashboard' : '/dashboard');
      }
    } catch (err) {
      setStatus({
        loading: false,
        error: err.response?.data?.message || 'Email ou mot de passe invalide.',
      });
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg-base)', padding: 24, position: 'relative', overflow: 'hidden',
    }}>
      {/* Background glow */}
      <div style={{
        position: 'absolute', top: '20%', left: '50%', transform: 'translateX(-50%)',
        width: 600, height: 400, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(99,102,241,0.08) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: '10%', right: '10%',
        width: 300, height: 300, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(168,85,247,0.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div style={{ width: '100%', maxWidth: 420, animation: 'fade-in-up 0.4s ease' }}>
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 36 }}>
          <img src="/logo.png" alt="AutoTest" style={{
            width: 72, height: 72,
            objectFit: 'contain',
            margin: '0 auto 16px',
            display: 'block',
            filter: 'drop-shadow(0 0 20px rgba(34,211,238,0.35))',
          }} />
          <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: '-0.04em', marginBottom: 6 }}>
            Bienvenue sur AutoTest
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Plateforme de tests automatisés par IA
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'var(--bg-raised)', border: '1px solid var(--border)',
          borderRadius: 'var(--radius-xl)', padding: 32,
          boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
        }}>
          {/* Error */}
          {status.error && (
            <div style={{
              background: 'rgba(239,68,68,0.10)', border: '1px solid rgba(239,68,68,0.25)',
              borderRadius: 'var(--radius-md)', padding: '12px 14px',
              color: '#ef4444', fontSize: 13, fontWeight: 500, marginBottom: 20,
              display: 'flex', gap: 8, alignItems: 'center',
            }}>
              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0" /></svg>
              {status.error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
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

            {/* Password */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                  Mot de passe
                </label>
                <Link to="/forgot-password" style={{ fontSize: 11, color: 'var(--color-brand)', fontWeight: 500, textDecoration: 'none' }}
                  onMouseEnter={e => e.currentTarget.style.color = 'var(--color-brand-hover)'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--color-brand)'}>
                  Mot de passe oublié ?
                </Link>
              </div>
              <div style={{ position: 'relative' }}>
                <input
                  name="password" type={showPass ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={form.password} onChange={handleChange} required
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
            </div>

            {/* Submit */}
            <button type="submit" disabled={status.loading} style={{
              width: '100%', padding: '12px 0', borderRadius: 'var(--radius-md)',
              background: status.loading ? 'rgba(99,102,241,0.6)' : 'var(--color-brand)',
              border: 'none', cursor: status.loading ? 'not-allowed' : 'pointer',
              color: '#fff', fontSize: 14, fontWeight: 700, letterSpacing: '-0.01em',
              transition: 'all 120ms ease', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
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
                  Connexion en cours…
                </>
              ) : 'Se connecter →'}
            </button>
          </form>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '20px 0' }}>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>ou</span>
            <div style={{ flex: 1, height: 1, background: 'var(--border)' }} />
          </div>

          <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)' }}>
            Pas encore de compte ?{' '}
            <Link to="/register" style={{ color: 'var(--color-brand)', fontWeight: 600, textDecoration: 'none' }}
              onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
              onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}>
              S'inscrire gratuitement
            </Link>
          </p>
        </div>

        {/* Footer */}
        <p style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-muted)', marginTop: 24 }}>
          Protected by AutoTest · End-to-end encrypted
        </p>
      </div>
    </div>
  );
}
