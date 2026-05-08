import { useState, useEffect, useRef, useCallback, memo, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import Topbar from '../components/Topbar';
import { KPICardSkeleton, HealthCardSkeleton } from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import { SlideOver, ConfirmModal } from '../components/Modal';
import { useToast } from '../components/Toast';
import {
  getAllUsers, updateUserRole, deleteUser,
  getGlobalStats, getAllTestsAdmin,
  getAdminHealth, getAdminActivityStats, getAdminLLMComparison,
  getAdminUsers, disableAdminUser,
  getAdminAlerts, getAdminFeatureFailures,
  getAdminPrompts, updateAdminPrompts,
} from '../api/auth';

// ─── Icon helper ──────────────────────────────────────────────────────────────
const Icon = ({ d, size = 16, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

// ─── Badge ────────────────────────────────────────────────────────────────────
const BADGE_COLORS = {
  healthy:  { bg: 'rgba(34,197,94,0.12)',  text: '#22c55e', border: 'rgba(34,197,94,0.25)' },
  degraded: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)' },
  down:     { bg: 'rgba(239,68,68,0.12)',  text: '#ef4444', border: 'rgba(239,68,68,0.25)' },
  admin:    { bg: 'rgba(168,85,247,0.12)', text: '#a855f7', border: 'rgba(168,85,247,0.25)' },
  user:     { bg: 'rgba(99,102,241,0.12)', text: '#6366f1', border: 'rgba(99,102,241,0.25)' },
};

const Badge = ({ status, label }) => {
  const s = BADGE_COLORS[status] || BADGE_COLORS.down;
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, letterSpacing: '0.05em', padding: '2px 8px',
      borderRadius: 99, textTransform: 'uppercase', whiteSpace: 'nowrap',
      background: s.bg, color: s.text, border: `1px solid ${s.border}`,
    }}>
      {label || status}
    </span>
  );
};

// ─── Animated count-up ────────────────────────────────────────────────────────
const CountUp = ({ value, duration = 800 }) => {
  const [displayed, setDisplayed] = useState(0);
  const [visible,   setVisible]   = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, { threshold: 0.3 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return;
    const target = typeof value === 'number' ? value : parseFloat(value) || 0;
    let cur = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      cur += step;
      if (cur >= target) { setDisplayed(target); clearInterval(timer); }
      else setDisplayed(Math.floor(cur));
    }, 16);
    return () => clearInterval(timer);
  }, [visible, value, duration]);

  return <span ref={ref}>{typeof value === 'number' ? displayed.toLocaleString() : value}</span>;
};

// ─── Sparkline (pure SVG) ─────────────────────────────────────────────────────
const Sparkline = memo(({ data, color = '#6366f1', height = 36 }) => {
  const max = Math.max(...data, 1);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 120; const h = height;
  const step = data.length > 1 ? w / (data.length - 1) : w;
  const pts = data.map((v, i) => `${i * step},${h - ((v - min) / range) * h}`).join(' ');
  const area = `0,${h} ${pts} ${(data.length - 1) * step},${h}`;
  return (
    <svg width={w} height={h} style={{ overflow: 'visible' }}>
      <defs>
        <linearGradient id={`sg-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={area} fill={`url(#sg-${color.replace('#', '')})`} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
});

// ─── KPI Card ─────────────────────────────────────────────────────────────────
const KPICard = memo(({ title, value, unit = '', delta, sparkData, color = '#6366f1', icon }) => {
  const isPositive = delta >= 0;
  return (
    <div className="glass-card card-hover" style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
        <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-secondary)' }}>{title}</span>
        <div style={{ width: 32, height: 32, borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', background: `${color}18`, border: `1px solid ${color}25` }}>
          <Icon d={icon} size={15} color={color} />
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 6 }}>
        <span style={{ fontSize: 28, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
          <CountUp value={typeof value === 'number' ? value : parseFloat(value) || 0} />
        </span>
        {unit && <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500 }}>{unit}</span>}
      </div>
      {delta !== undefined && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 12 }}>
          <span style={{ fontSize: 11, color: isPositive ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
            {isPositive ? '↑' : '↓'} {Math.abs(delta)}%
          </span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>vs semaine précédente</span>
        </div>
      )}
      {sparkData && <Sparkline data={sparkData} color={color} />}
    </div>
  );
});

// ─── System Health Panel (pings every 30s) ────────────────────────────────────
const HealthPanel = () => {
  const [services, setServices] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [lastPing, setLastPing] = useState(null);

  const ping = useCallback(async () => {
    try {
      const { data } = await getAdminHealth();
      if (data.success) setServices(data.services || []);
      setLastPing(new Date());
    } catch (_) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { ping(); }, [ping]);
  useEffect(() => { const id = setInterval(ping, 30000); return () => clearInterval(id); }, [ping]);

  const statusColors = { healthy: '#22c55e', degraded: '#f59e0b', down: '#ef4444' };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)' }}>Santé des Services</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {lastPing && <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Ping il y a {Math.round((Date.now() - lastPing.getTime()) / 1000)}s</span>}
          <button onClick={ping} className="btn btn-ghost" style={{ fontSize: 11, padding: '3px 8px' }}>↺</button>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {loading ? [1, 2, 3, 4].map((i) => <HealthCardSkeleton key={i} />) :
          services.length > 0 ? services.map((s) => {
            const color = statusColors[s.status] || '#64748b';
            return (
              <div key={s.service} className="glass-card" style={{ padding: 18 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>{s.service}</span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: color, animation: s.status === 'healthy' ? 'pulse-dot 1.5s ease-in-out infinite' : 'none' }} />
                    <Badge status={s.status} />
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10 }}>
                  {[
                    { label: 'Latence', val: `${s.latency}ms`,    good: s.latency < 200 },
                    { label: 'Uptime',  val: `${s.uptime}%`,       good: s.uptime > 99 },
                    { label: 'Mémoire', val: s.memory || '—',      good: true },
                  ].map((m) => (
                    <div key={m.label}>
                      <div style={{ fontSize: 9, color: 'var(--text-muted)', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{m.label}</div>
                      <div style={{ fontSize: 13, fontWeight: 700, fontFamily: 'var(--font-mono)', color: m.good ? 'var(--text-primary)' : '#f59e0b' }}>{m.val}</div>
                    </div>
                  ))}
                </div>
              </div>
            );
          }) : <p style={{ fontSize: 12, color: 'var(--text-muted)', gridColumn: '1 / -1' }}>Impossible de contacter le serveur.</p>
        }
      </div>
    </div>
  );
};

// ─── Activity Heatmap (GitHub-style) ──────────────────────────────────────────
const ActivityHeatmap = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminActivityStats()
      .then(({ data: d }) => { if (d.success) setData(d.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const heatmap = useMemo(() => {
    const map = {};
    data.forEach((d) => { map[d.date] = (map[d.date] || 0) + d.count; });

    const days = [];
    for (let i = 89; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toISOString().slice(0, 10);
      days.push({ date: key, count: map[key] || 0 });
    }
    return days;
  }, [data]);

  const maxCount = Math.max(...heatmap.map((d) => d.count), 1);

  const getColor = (count) => {
    if (count === 0) return 'rgba(255,255,255,0.05)';
    const intensity = count / maxCount;
    if (intensity < 0.25) return 'rgba(34,211,238,0.25)';
    if (intensity < 0.5)  return 'rgba(34,211,238,0.45)';
    if (intensity < 0.75) return 'rgba(34,211,238,0.65)';
    return '#22d3ee';
  };

  const weeks = [];
  for (let i = 0; i < heatmap.length; i += 7) weeks.push(heatmap.slice(i, i + 7));

  return (
    <div className="glass-card" style={{ padding: 20 }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Activité des Tests</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 16 }}>90 derniers jours</div>

      {loading ? (
        <div style={{ height: 80, background: 'rgba(255,255,255,0.03)', borderRadius: 8, animation: 'shimmer 1.8s infinite linear', backgroundSize: '1000px 100%' }} />
      ) : (
        <>
          {/* Day-of-week labels */}
          <div style={{ display: 'flex', gap: 3, marginBottom: 4 }}>
            <div style={{ width: 20 }} />
            {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((d, i) => (
              <div key={i} style={{ width: 12, fontSize: 8, color: 'var(--text-muted)', textAlign: 'center' }}>{d}</div>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 3, overflowX: 'auto', paddingBottom: 8 }}>
            {weeks.map((week, wi) => (
              <div key={wi} style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {week.map((day, di) => (
                  <div key={di} title={`${day.date}: ${day.count} test(s)`} style={{
                    width: 12, height: 12, borderRadius: 2,
                    background: getColor(day.count),
                    cursor: 'default', transition: 'transform 100ms ease',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.3)'}
                  onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                  />
                ))}
              </div>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8, fontSize: 10, color: 'var(--text-muted)' }}>
            <span>Moins</span>
            {[0, 0.25, 0.5, 0.75, 1].map((v, i) => (
              <div key={i} style={{ width: 12, height: 12, borderRadius: 2, background: getColor(v * maxCount) }} />
            ))}
            <span>Plus</span>
            <span style={{ marginLeft: 'auto', fontSize: 11 }}>
              Total: {heatmap.reduce((a, b) => a + b.count, 0)} test(s)
            </span>
          </div>
        </>
      )}
    </div>
  );
};

// ─── LLM Benchmark Table ──────────────────────────────────────────────────────
const LLMBenchmark = () => {
  const [data,    setData]    = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminLLMComparison()
      .then(({ data: d }) => { if (d.success) setData(d.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const cols = ['Moteur', 'Runs', 'Succès', 'Échecs', 'Taux', 'Durée moy.', 'Erreurs'];

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', fontSize: 13, fontWeight: 600 }}>
        Benchmark LLM
      </div>
      {loading ? (
        <div style={{ padding: 24, color: 'var(--text-muted)', fontSize: 12 }}>Chargement…</div>
      ) : data.length === 0 ? (
        <EmptyState type="generic" title="Aucune donnée" message="Les données apparaîtront après les premiers tests." />
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)' }}>
              {cols.map((c) => (
                <th key={c} style={{ padding: '10px 16px', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.engine} style={{ borderBottom: '1px solid var(--border)', transition: 'background 120ms ease' }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: row.engine === 'groq' ? '#22d3ee' : '#a855f7' }}>
                    {row.engine === 'groq' ? '☁️ Groq' : row.engine === 'ollama' ? '🖥️ Ollama' : row.engine}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 13 }}>{row.totalRuns}</td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 13, color: '#22c55e' }}>{row.completed}</td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 13, color: '#ef4444' }}>{row.failed}</td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ width: 60, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${row.successRate}%`, background: row.successRate >= 70 ? '#22c55e' : row.successRate >= 40 ? '#f59e0b' : '#ef4444', borderRadius: 2 }} />
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700, color: row.successRate >= 70 ? '#22c55e' : row.successRate >= 40 ? '#f59e0b' : '#ef4444' }}>{row.successRate}%</span>
                  </div>
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>
                  {row.avgDuration !== null ? `${row.avgDuration}s` : '—'}
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 12, color: row.syntaxErrors > 0 ? '#ef4444' : 'var(--text-muted)' }}>
                  {row.syntaxErrors}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

// ─── Enhanced Users Table (with per-user stats) ───────────────────────────────
const EnhancedUsersTable = ({ onUserCountChange }) => {
  const toast = useToast();
  const [users,      setUsers]      = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [search,     setSearch]     = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [editUser,   setEditUser]   = useState(null);
  const [banUser,    setBanUser]    = useState(null);
  const [page,       setPage]       = useState(1);
  const perPage = 5;

  const fetchUsers = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      // Try enhanced endpoint first, fall back to basic
      let data;
      try {
        const r = await getAdminUsers();
        data = r.data.data;
      } catch (_) {
        const r = await getAllUsers();
        data = r.data.data;
      }
      setUsers(data);
      onUserCountChange?.(data.length);
    } catch (err) {
      setError(err.response?.data?.message || 'Impossible de charger les utilisateurs.');
    } finally {
      setLoading(false);
    }
  }, [onUserCountChange]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    return ((u.name || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q)) &&
           (roleFilter === 'all' || u.role === roleFilter);
  });
  const paginated  = filtered.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.ceil(filtered.length / perPage);

  const handleBan = useCallback((user) => {
    setUsers((prev) => prev.filter((u) => u._id !== user._id));
    let cancelled = false;
    toast.success('Utilisateur banni', `${user.name} retiré`, { label: 'Annuler', onClick: () => { cancelled = true; fetchUsers(); } });
    setTimeout(async () => {
      if (cancelled) return;
      try { await deleteUser(user._id); }
      catch { toast.error('Erreur', 'Impossible de supprimer.'); fetchUsers(); }
    }, 3500);
  }, [toast, fetchUsers]);

  const handleRoleChange = useCallback(async (userId, newRole) => {
    setUsers((prev) => prev.map((u) => u._id === userId ? { ...u, role: newRole } : u));
    try { await updateUserRole(userId, newRole); toast.success('Rôle modifié', newRole); }
    catch { toast.error('Erreur', 'Impossible de modifier.'); fetchUsers(); }
  }, [toast, fetchUsers]);

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      {/* Toolbar */}
      <div style={{ padding: '14px 18px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
          <Icon d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" size={13} color="var(--text-muted)" />
          <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }}><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0" /></svg>
          <input className="input-base" style={{ paddingLeft: 32 }} placeholder="Rechercher…" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
        </div>
        <select value={roleFilter} onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }} className="input-base" style={{ width: 140 }}>
          <option value="all">Tous les rôles</option>
          <option value="admin">Admin</option>
          <option value="user">Utilisateur</option>
        </select>
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto' }}>
        {loading ? (
          <div style={{ padding: 20 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ display: 'flex', gap: 16, padding: '12px 0', borderBottom: '1px solid var(--border)', alignItems: 'center' }}>
                <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', animation: 'shimmer 1.8s infinite linear' }} />
                <div style={{ flex: 1 }}>
                  <div style={{ width: '40%', height: 10, marginBottom: 6, borderRadius: 6, background: 'rgba(255,255,255,0.06)', animation: 'shimmer 1.8s infinite linear' }} />
                  <div style={{ width: '60%', height: 8, borderRadius: 6, background: 'rgba(255,255,255,0.04)', animation: 'shimmer 1.8s infinite linear' }} />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div style={{ padding: 24, textAlign: 'center' }}>
            <p style={{ color: 'var(--color-danger)', fontSize: 13, marginBottom: 12 }}>{error}</p>
            <button onClick={fetchUsers} className="btn btn-ghost" style={{ fontSize: 12 }}>↺ Réessayer</button>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['Utilisateur', 'Rôle', 'Tests', 'Succès', 'LLM Préféré', 'Dernière Activité', 'Actions'].map((h) => (
                  <th key={h} style={{ padding: '10px 16px', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.06em', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginated.length === 0 ? (
                <tr><td colSpan={7}><EmptyState type="users" title="Aucun utilisateur" message="Aucun résultat" /></td></tr>
              ) : paginated.map((u) => (
                <tr key={u._id} style={{ borderBottom: '1px solid var(--border)', transition: 'background 120ms ease' }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 34, height: 34, borderRadius: '50%', flexShrink: 0, background: u.role === 'admin' ? 'linear-gradient(135deg,#a855f7,#6366f1)' : 'linear-gradient(135deg,#6366f1,#3b82f6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 13, fontWeight: 700, color: '#fff' }}>
                        {(u.name || u.email || '?')[0].toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 600 }}>{u.name}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{u.email}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <select value={u.role} onChange={(e) => handleRoleChange(u._id, e.target.value)}
                      style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: u.role === 'admin' ? '#a855f7' : '#6366f1', fontWeight: 600, fontSize: 12, outline: 'none' }}>
                      <option value="admin">Admin</option>
                      <option value="user">User</option>
                    </select>
                  </td>
                  <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
                    <span style={{ fontWeight: 700 }}>{u.totalTests ?? '—'}</span>
                    {u.failedTests > 0 && <span style={{ fontSize: 10, color: '#ef4444', marginLeft: 6 }}>({u.failedTests} ✗)</span>}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {u.successRate !== null && u.successRate !== undefined ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 40, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${u.successRate}%`, background: u.successRate >= 70 ? '#22c55e' : '#f59e0b', borderRadius: 2 }} />
                        </div>
                        <span style={{ fontSize: 11, fontWeight: 700, color: u.successRate >= 70 ? '#22c55e' : '#f59e0b' }}>{u.successRate}%</span>
                      </div>
                    ) : <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>—</span>}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ fontSize: 10, fontWeight: 600, padding: '2px 7px', borderRadius: 4, background: 'var(--bg-overlay)', border: '1px solid var(--border)', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                      {u.preferredLLM || '—'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {u.lastActivity ? new Date(u.lastActivity).toLocaleDateString('fr-FR') : u.createdAt ? new Date(u.createdAt).toLocaleDateString('fr-FR') : '—'}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <button onClick={() => setEditUser(u)} className="btn btn-ghost" style={{ fontSize: 11, padding: '3px 8px' }}>Éditer</button>
                      <button onClick={() => setBanUser(u)} className="btn btn-danger" style={{ fontSize: 11, padding: '3px 8px' }}>Bannir</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {totalPages > 1 && (
        <div style={{ padding: '10px 18px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{filtered.length} utilisateur(s)</span>
          <div style={{ display: 'flex', gap: 4 }}>
            {Array.from({ length: totalPages }).map((_, i) => (
              <button key={i} onClick={() => setPage(i + 1)} style={{ width: 28, height: 28, borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer', background: page === i + 1 ? 'var(--color-brand)' : 'transparent', border: `1px solid ${page === i + 1 ? 'var(--color-brand)' : 'var(--border)'}`, color: page === i + 1 ? '#fff' : 'var(--text-muted)' }}>{i + 1}</button>
            ))}
          </div>
        </div>
      )}

      <SlideOver isOpen={!!editUser} onClose={() => setEditUser(null)} title={`Éditer — ${editUser?.name}`}>
        {editUser && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div><label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Nom</label><input className="input-base" defaultValue={editUser.name} /></div>
            <div><label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Email</label><input className="input-base" defaultValue={editUser.email} /></div>
            <div><label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Rôle</label>
              <select className="input-base" defaultValue={editUser.role}><option value="user">Utilisateur</option><option value="admin">Admin</option></select>
            </div>
            <button onClick={() => { setEditUser(null); toast.success('Profil mis à jour', editUser.name); }} className="btn btn-primary" style={{ marginTop: 8 }}>Sauvegarder</button>
          </div>
        )}
      </SlideOver>

      <ConfirmModal isOpen={!!banUser} onClose={() => setBanUser(null)}
        onConfirm={() => { handleBan(banUser); setBanUser(null); }}
        title="Confirmer le bannissement"
        message={`Bannir ${banUser?.name} ? Annulable dans 3s.`}
        confirmLabel="Bannir" danger />
    </div>
  );
};

// ─── Anomaly Alerts Feed ──────────────────────────────────────────────────────
const AlertsFeed = () => {
  const [alerts,  setAlerts]  = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminAlerts()
      .then(({ data: d }) => { if (d.success) setAlerts(d.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const SEVERITY = {
    high:   { color: '#ef4444', bg: 'rgba(239,68,68,0.08)',  icon: '🔴' },
    medium: { color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', icon: '🟡' },
    low:    { color: '#3b82f6', bg: 'rgba(59,130,246,0.08)', icon: '🔵' },
  };

  const TYPE_LABEL = {
    consecutive_failures: 'Échecs consécutifs',
    pipeline_timeout:     'Timeout pipeline',
    high_failure_rate:    "Taux d'échec élevé",
  };

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontSize: 13, fontWeight: 600 }}>Alertes Anomalies</span>
        {alerts.length > 0 && (
          <span style={{ fontSize: 10, fontWeight: 700, padding: '1px 7px', borderRadius: 99, background: 'rgba(239,68,68,0.15)', color: '#ef4444', border: '1px solid rgba(239,68,68,0.25)' }}>
            {alerts.length}
          </span>
        )}
      </div>
      <div style={{ maxHeight: 280, overflowY: 'auto' }}>
        {loading ? (
          <div style={{ padding: 20, color: 'var(--text-muted)', fontSize: 12 }}>Chargement…</div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: 24, textAlign: 'center' }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>✅</div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Tout est normal</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Aucune anomalie détectée</div>
          </div>
        ) : alerts.map((alert, i) => {
          const sev = SEVERITY[alert.severity] || SEVERITY.low;
          return (
            <div key={i} style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', background: sev.bg }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                <span style={{ fontSize: 14, flexShrink: 0 }}>{sev.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: sev.color }}>
                      {TYPE_LABEL[alert.type] || alert.type}
                    </span>
                    {alert.timestamp && (
                      <span style={{ fontSize: 9, color: 'var(--text-muted)' }}>
                        {new Date(alert.timestamp).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{alert.message}</div>
                  {alert.userName && <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 3 }}>Utilisateur : {alert.userName}</div>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ─── Feature Failure Analytics (Recharts BarChart) ───────────────────────────
const FeatureFailureChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminFeatureFailures()
      .then(({ data: d }) => { if (d.success) setData(d.data); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="glass-card" style={{ padding: 20 }}>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Taux de Pass par Fonctionnalité</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 16 }}>Top 15 des fonctionnalités avec le meilleur taux de réussite</div>

      {loading ? (
        <div style={{ height: 180, background: 'rgba(255,255,255,0.03)', borderRadius: 8, animation: 'shimmer 1.8s infinite linear' }} />
      ) : data.length === 0 ? (
        <EmptyState type="generic" title="Aucune donnée" message="Les statistiques apparaîtront après des tests complétés." />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 8 }}>
            <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" width={140} tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false}
              tickFormatter={(v) => v.length > 20 ? v.slice(0, 20) + '…' : v} />
            <Tooltip
              formatter={(v) => [`${v}%`, 'Taux de Pass']}
              contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 11 }}
              cursor={{ fill: 'rgba(255,255,255,0.04)' }}
            />
            <Bar dataKey="passRate" radius={[0, 4, 4, 0]}>
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.passRate >= 70 ? '#22c55e' : entry.passRate >= 40 ? '#f59e0b' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

// ─── Area Chart (load analysis) ───────────────────────────────────────────────
const AreaChart = ({ allTests }) => {
  const [period, setPeriod] = useState('today');
  const svgW = 600; const svgH = 120;

  const data = useMemo(() => {
    const now = new Date();
    if (period === 'today') {
      return Array.from({ length: 24 }, (_, h) =>
        allTests.filter((t) => {
          const d = new Date(t.createdAt);
          return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate() && d.getHours() === h;
        }).length
      );
    }
    const days = period === '7d' ? 7 : 30;
    return Array.from({ length: days }, (_, i) => {
      const ref = new Date(now);
      ref.setDate(ref.getDate() - (days - 1 - i));
      return allTests.filter((t) => {
        const d = new Date(t.createdAt);
        return d.getFullYear() === ref.getFullYear() && d.getMonth() === ref.getMonth() && d.getDate() === ref.getDate();
      }).length;
    });
  }, [allTests, period]);

  const max   = Math.max(...data, 1);
  const step  = data.length > 1 ? svgW / (data.length - 1) : svgW;
  const yS    = (v) => svgH - (v / max) * (svgH - 10);
  const pts   = data.map((v, i) => `${i * step},${yS(v)}`).join(' ');
  const area  = `0,${svgH} ${pts} ${(data.length - 1) * step},${svgH}`;
  const avg   = Math.round(data.reduce((a, b) => a + b, 0) / data.length);

  return (
    <div className="glass-card" style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600 }}>Analyse de Charge</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Exécutions par période</div>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {['today', '7d', '30d'].map((p) => (
            <button key={p} onClick={() => setPeriod(p)} style={{
              fontSize: 11, fontWeight: 600, padding: '4px 10px', borderRadius: 'var(--radius-sm)',
              border: `1px solid ${period === p ? 'var(--color-brand)' : 'var(--border)'}`,
              background: period === p ? 'var(--color-brand-muted)' : 'transparent',
              color: period === p ? 'var(--color-brand)' : 'var(--text-muted)', cursor: 'pointer',
            }}>{p === 'today' ? "Aujourd'hui" : p}</button>
          ))}
        </div>
      </div>
      <svg viewBox={`0 0 ${svgW} ${svgH}`} preserveAspectRatio="none" style={{ width: '100%', height: 120 }}>
        <defs>
          <linearGradient id="aG" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={area} fill="url(#aG)" />
        <polyline points={pts} fill="none" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <line x1={0} y1={yS(avg)} x2={svgW} y2={yS(avg)} stroke="#94a3b8" strokeWidth="1" strokeDasharray="4 4" />
      </svg>
    </div>
  );
};

// ─── Live Log Stream ──────────────────────────────────────────────────────────
const LogStream = ({ allTests }) => {
  const [filter,  setFilter]  = useState('ALL');
  const [paused,  setPaused]  = useState(false);
  const bottomRef = useRef(null);
  const LOG_COLORS = { INFO: '#3b82f6', SUCCESS: '#22c55e', WARN: '#f59e0b', ERROR: '#ef4444' };

  const logs = useMemo(() => {
    const entries = [];
    allTests.forEach((t) => {
      let agent = 'system';
      try { agent = new URL(t.targetUrl).hostname.replace('www.', '').split('.')[0]; } catch (_) {}
      entries.push({ id: `${t._id}-s`, ts: new Date(t.createdAt).toLocaleTimeString('fr-FR'), level: 'INFO', agent, msg: `Test démarré — ${t.targetUrl}`, _ts: new Date(t.createdAt).getTime() });
      (t.logs || []).forEach((l, i) => entries.push({ id: `${t._id}-l${i}`, ts: new Date(l.timestamp || t.createdAt).toLocaleTimeString('fr-FR'), level: l.level === 'error' ? 'ERROR' : l.level === 'warning' ? 'WARN' : 'INFO', agent, msg: l.message, _ts: new Date(l.timestamp || t.createdAt).getTime() + i }));
      if (t.status === 'completed') {
        const p = t.report?.passed ?? '?', f = (t.report?.failed ?? 0) + (t.report?.errors ?? 0);
        entries.push({ id: `${t._id}-d`, ts: new Date(t.updatedAt).toLocaleTimeString('fr-FR'), level: 'SUCCESS', agent, msg: `Terminé — ${p} passés / ${f} échoués`, _ts: new Date(t.updatedAt).getTime() + 1 });
      } else if (t.status === 'failed') {
        entries.push({ id: `${t._id}-f`, ts: new Date(t.updatedAt).toLocaleTimeString('fr-FR'), level: 'ERROR', agent, msg: `Échec — ${t.targetUrl}`, _ts: new Date(t.updatedAt).getTime() + 1 });
      }
    });
    return entries.sort((a, b) => a._ts - b._ts).slice(-200);
  }, [allTests]);

  useEffect(() => { if (!paused && bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' }); }, [logs, paused]);
  const filtered = filter === 'ALL' ? logs : logs.filter((l) => l.level === filter);

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 13, fontWeight: 600 }}>Logs Live</span>
          {allTests.some((t) => t.status === 'running') && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', animation: 'pulse-dot 1.5s ease-in-out infinite' }} />}
          <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{logs.length} entrée(s)</span>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {['ALL', 'INFO', 'SUCCESS', 'WARN', 'ERROR'].map((f) => (
            <button key={f} onClick={() => setFilter(f)} style={{
              fontSize: 10, fontWeight: 600, padding: '2px 8px', borderRadius: 99, cursor: 'pointer',
              border: `1px solid ${filter === f ? (LOG_COLORS[f] || 'var(--color-brand)') + '60' : 'var(--border)'}`,
              background: filter === f ? `${LOG_COLORS[f] || 'var(--color-brand)'}15` : 'transparent',
              color: filter === f ? (LOG_COLORS[f] || 'var(--color-brand)') : 'var(--text-muted)',
            }}>{f}</button>
          ))}
          <button onClick={() => setPaused((p) => !p)} className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}>{paused ? '▶' : '⏸'}</button>
        </div>
      </div>
      <div style={{ height: 240, overflowY: 'auto', fontFamily: 'var(--font-mono)', fontSize: 11, background: 'rgba(0,0,0,0.3)' }}>
        {filtered.length === 0 ? <EmptyState type="logs" title="Aucun log" message="Les logs apparaissent dès qu'un test est lancé" /> :
          filtered.map((log) => (
            <div key={log.id} style={{ display: 'flex', gap: 10, padding: '4px 16px', borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
              <span style={{ color: 'var(--text-muted)', flexShrink: 0, fontSize: 9, paddingTop: 1 }}>{log.ts}</span>
              <span style={{ color: LOG_COLORS[log.level], fontWeight: 700, width: 52, flexShrink: 0, fontSize: 9 }}>{log.level}</span>
              <span style={{ color: 'var(--color-ai)', flexShrink: 0, fontSize: 9 }}>[{log.agent}]</span>
              <span style={{ color: 'var(--text-secondary)', flex: 1 }}>{log.msg}</span>
            </div>
          ))
        }
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

// ─── Prompt Manager ───────────────────────────────────────────────────────────
const PromptManager = () => {
  const toast = useToast();
  const [prompts,  setPrompts]  = useState({ spec_parsing: '', test_generation: '', selenium_generation: '' });
  const [loading,  setLoading]  = useState(true);
  const [saving,   setSaving]   = useState(false);
  const [activeKey, setActiveKey] = useState('spec_parsing');
  const [edited,   setEdited]   = useState({});
  const [testing,  setTesting]  = useState(false);

  useEffect(() => {
    getAdminPrompts()
      .then(({ data: d }) => { if (d.success) setPrompts(d.data); })
      .catch(() => toast.error('Erreur', 'Impossible de charger les prompts.'))
      .finally(() => setLoading(false));
  }, [toast]);

  const handleSave = async () => {
    if (!Object.keys(edited).length) { toast.info('Aucun changement', ''); return; }
    setSaving(true);
    try {
      await updateAdminPrompts(edited);
      setPrompts((p) => ({ ...p, ...edited }));
      setEdited({});
      toast.success('Prompts sauvegardés', 'config.yaml mis à jour');
    } catch (err) {
      toast.error('Erreur', err.response?.data?.message || 'Échec de la sauvegarde.');
    } finally {
      setSaving(false);
    }
  };

  const TABS = [
    { key: 'spec_parsing',        label: 'Analyse specs' },
    { key: 'test_generation',     label: 'Génération tests' },
    { key: 'selenium_generation', label: 'Scripts Selenium' },
  ];

  const currentText = edited[activeKey] ?? prompts[activeKey] ?? '';
  const isDirty     = !!edited[activeKey];

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 13, fontWeight: 600 }}>Gestionnaire de Prompts</span>
        <div style={{ display: 'flex', gap: 8 }}>
          {Object.keys(edited).length > 0 && <span style={{ fontSize: 10, color: '#f59e0b', alignSelf: 'center' }}>● Non sauvegardé</span>}
          <button onClick={handleSave} disabled={saving} className="btn btn-primary" style={{ fontSize: 12, padding: '5px 14px', opacity: saving ? 0.6 : 1 }}>
            {saving ? '…' : '💾 Sauvegarder'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)' }}>
        {TABS.map((t) => (
          <button key={t.key} onClick={() => setActiveKey(t.key)} style={{
            padding: '10px 16px', fontSize: 12, fontWeight: 500, cursor: 'pointer',
            background: 'transparent', border: 'none', outline: 'none',
            color: activeKey === t.key ? 'var(--color-brand)' : 'var(--text-muted)',
            borderBottom: `2px solid ${activeKey === t.key ? 'var(--color-brand)' : 'transparent'}`,
            marginBottom: -1, transition: 'all 120ms ease',
            position: 'relative',
          }}>
            {t.label}
            {edited[t.key] && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#f59e0b', position: 'absolute', top: 6, right: 6 }} />}
          </button>
        ))}
      </div>

      <div style={{ padding: '16px' }}>
        {loading ? (
          <div style={{ height: 200, background: 'rgba(255,255,255,0.03)', borderRadius: 8, animation: 'shimmer 1.8s infinite linear' }} />
        ) : (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {isDirty ? <span style={{ color: '#f59e0b' }}>● Modifié</span> : 'Inchangé'} · {currentText.length} caractères
              </span>
              <div style={{ display: 'flex', gap: 6 }}>
                {isDirty && (
                  <button onClick={() => setEdited((e) => { const n = {...e}; delete n[activeKey]; return n; })}
                    className="btn btn-ghost" style={{ fontSize: 11, padding: '3px 8px', color: '#f59e0b' }}>
                    ↺ Annuler les changements
                  </button>
                )}
                <button onClick={() => { setTesting(true); setTimeout(() => { setTesting(false); toast.success('Prompt testé', 'Simulation OK (pas de connexion au moteur IA en mode test)'); }, 1200); }}
                  disabled={testing} className="btn btn-ghost" style={{ fontSize: 11, padding: '3px 8px' }}>
                  {testing ? '…' : '▶ Tester'}
                </button>
              </div>
            </div>
            <textarea
              value={currentText}
              onChange={(e) => setEdited((prev) => ({ ...prev, [activeKey]: e.target.value }))}
              style={{
                width: '100%', minHeight: 220, resize: 'vertical',
                background: '#0d1117', border: '1px solid var(--border)', borderRadius: 8,
                padding: '12px 14px', fontFamily: 'var(--font-mono)', fontSize: 12, lineHeight: 1.7,
                color: '#e6edf3', outline: 'none', boxSizing: 'border-box',
              }}
            />
            <div style={{ marginTop: 8, padding: '10px 12px', background: 'rgba(34,211,238,0.05)', border: '1px solid rgba(34,211,238,0.15)', borderRadius: 8, fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.6 }}>
              💡 Variables disponibles : <code style={{ color: '#22d3ee', background: 'var(--bg-overlay)', padding: '1px 4px', borderRadius: 3 }}>{'{'+'url_cible'+'}'}</code> · Modifiez avec précaution — ces prompts pilotent directement la génération IA.
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// ─── Section meta ─────────────────────────────────────────────────────────────
const SECTION_META = {
  dashboard: { title: 'Tableau de bord',         sub: "Vue d'ensemble de la plateforme AutoTest" },
  users:     { title: 'Gestion des Utilisateurs', sub: 'Gérez les comptes, rôles et statistiques par utilisateur' },
  health:    { title: 'Santé des Services',       sub: 'Statut en temps réel des services et moteurs LLM' },
  logs:      { title: 'Logs & Alertes',           sub: 'Flux de logs en direct et détection des anomalies' },
  tests:     { title: 'Analyse des Tests',        sub: 'Charge, tendances et taux de succès par fonctionnalité' },
  settings:  { title: 'Configuration des Prompts', sub: 'Éditez les prompts IA directement depuis le dashboard' },
};

// ─── ADMIN DASHBOARD ──────────────────────────────────────────────────────────
export default function AdminDashboard() {
  const { pathname } = useLocation();
  // Extract section from path: /admin/users → 'users', /admin/dashboard → 'dashboard'
  const section = pathname.split('/').filter(Boolean).pop() || 'dashboard';
  const meta = SECTION_META[section] || SECTION_META.dashboard;

  const [loading,       setLoading]       = useState(true);
  const [stats,         setStats]         = useState({ totalTests: 0, completedTests: 0, failedTests: 0, activeUsersCount: 0 });
  const [allTests,      setAllTests]      = useState([]);
  const [realUserCount, setRealUserCount] = useState(null);
  const [lastRefresh,   setLastRefresh]   = useState(null);

  const loadDashboard = useCallback(async () => {
    try {
      const [statsRes, testsRes, usersRes] = await Promise.allSettled([
        getGlobalStats(),
        getAllTestsAdmin(),
        getAdminUsers(),
      ]);
      if (statsRes.status === 'fulfilled' && statsRes.value.data.success) setStats(statsRes.value.data.data);
      if (testsRes.status === 'fulfilled' && testsRes.value.data.success)  setAllTests(testsRes.value.data.data);
      if (usersRes.status === 'fulfilled' && usersRes.value.data.success)  setRealUserCount(usersRes.value.data.data.length);
      setLastRefresh(new Date());
    } catch (_) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);
  useEffect(() => { const id = setInterval(loadDashboard, 30000); return () => clearInterval(id); }, [loadDashboard]);

  const successRate = stats.totalTests > 0
    ? (stats.completedTests / stats.totalTests * 100).toFixed(1)
    : '0.0';

  const last7 = useMemo(() => Array.from({ length: 7 }, (_, i) => {
    const ref = new Date(); ref.setDate(ref.getDate() - (6 - i));
    return allTests.filter((t) => { const d = new Date(t.createdAt); return d.getDate() === ref.getDate() && d.getMonth() === ref.getMonth(); }).length;
  }), [allTests]);

  const last7Failed = useMemo(() => Array.from({ length: 7 }, (_, i) => {
    const ref = new Date(); ref.setDate(ref.getDate() - (6 - i));
    return allTests.filter((t) => { const d = new Date(t.createdAt); return d.getDate() === ref.getDate() && d.getMonth() === ref.getMonth() && t.status === 'failed'; }).length;
  }), [allTests]);

  const kpiData = [
    { title: 'Utilisateurs',  value: realUserCount ?? 0,        sparkData: [0,0,0,0,0,0, realUserCount ?? 0], color: '#6366f1', icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" },
    { title: 'Tests Exécutés', value: stats.totalTests,          sparkData: last7,       color: '#22c55e', icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" },
    { title: 'Taux de Succès', value: parseFloat(successRate),  unit: '%', sparkData: [0,0,0,0,0,0, parseFloat(successRate)||0], color: '#a855f7', icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707" },
    { title: 'Tests Échoués',  value: stats.failedTests,         sparkData: last7Failed, color: '#ef4444', icon: "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0" },
  ];

  const timeSinceRefresh = lastRefresh ? Math.round((Date.now() - lastRefresh.getTime()) / 1000) : null;

  // ─── Section content ────────────────────────────────────────────────────────
  const renderSection = () => {
    switch (section) {

      // ── /admin/users ──────────────────────────────────────────────────────
      case 'users':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
              {loading ? [1, 2].map((i) => <KPICardSkeleton key={i} />) : [
                kpiData[0], // Utilisateurs
                kpiData[1], // Tests Exécutés
              ].map((kpi) => <KPICard key={kpi.title} {...kpi} />)}
            </div>
            <EnhancedUsersTable onUserCountChange={setRealUserCount} />
          </div>
        );

      // ── /admin/health ─────────────────────────────────────────────────────
      case 'health':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <HealthPanel />
            <LLMBenchmark />
          </div>
        );

      // ── /admin/logs ───────────────────────────────────────────────────────
      case 'logs':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <AlertsFeed />
            <LogStream allTests={allTests} />
          </div>
        );

      // ── /admin/tests ──────────────────────────────────────────────────────
      case 'tests':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
              {loading ? [1, 2, 3, 4].map((i) => <KPICardSkeleton key={i} />) :
                kpiData.map((kpi) => <KPICard key={kpi.title} {...kpi} />)}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <FeatureFailureChart />
              <AreaChart allTests={allTests} />
            </div>
            <ActivityHeatmap />
          </div>
        );

      // ── /admin/settings ───────────────────────────────────────────────────
      case 'settings':
        return <PromptManager />;

      // ── /admin/dashboard (default) ────────────────────────────────────────
      default:
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
              {loading ? [1, 2, 3, 4].map((i) => <KPICardSkeleton key={i} />) :
                kpiData.map((kpi) => <KPICard key={kpi.title} {...kpi} />)}
            </div>
            <HealthPanel />
            <ActivityHeatmap />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <AlertsFeed />
              <LLMBenchmark />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <FeatureFailureChart />
              <AreaChart allTests={allTests} />
            </div>
            <LogStream allTests={allTests} />
          </div>
        );
    }
  };

  return (
    <div className="layout-main">
      <Topbar
        agentActive={allTests.some((t) => t.status === 'running')}
        agentMessage={allTests.some((t) => t.status === 'running') ? `${allTests.filter((t) => t.status === 'running').length} test(s) en cours…` : undefined}
      />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 28 }}>

        {/* Page Header — updates with the active section */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', animation: 'fade-in-up 0.3s ease' }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 4 }}>
              {meta.title}
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              {meta.sub}
              {section === 'dashboard' && timeSinceRefresh !== null && (
                <span style={{ color: 'var(--text-muted)' }}> · Actualisé il y a {timeSinceRefresh}s</span>
              )}
            </p>
          </div>
          <button onClick={loadDashboard} className="btn btn-ghost" style={{ fontSize: 12 }}>↺ Actualiser</button>
        </div>

        {/* Route-based section content */}
        {renderSection()}

      </div>
    </div>
  );
}
