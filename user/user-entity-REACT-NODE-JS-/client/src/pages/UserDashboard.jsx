import { useState, useEffect, useRef, useCallback, memo, useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, LineChart, Line, XAxis, YAxis } from 'recharts';
import Topbar from '../components/Topbar';
import { TestCardSkeleton, ProjectCardSkeleton, KPICardSkeleton } from '../components/Skeleton';
import EmptyState from '../components/EmptyState';
import Modal from '../components/Modal';
import { ConfirmModal } from '../components/Modal';
import { useToast } from '../components/Toast';
import { useAuth } from '../context/AuthContext';
import {
  runTest, fetchMyTests, fetchTestProgress, fetchTestResults,
  fetchFilteredTests, fetchCompareTests,
} from '../api/auth';

// ─── Icon helper ───────────────────────────────────────────────────────────────
const Icon = ({ d, size = 16, color = 'currentColor', stroke = 1.6 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

// ─── Animated count-up ────────────────────────────────────────────────────────
const CountUp = ({ target, duration = 1000, suffix = '' }) => {
  const [val, setVal] = useState(0);
  const ref = useRef(null);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return;
      obs.disconnect();
      let start = 0;
      const step = target / (duration / 16);
      const timer = setInterval(() => {
        start += step;
        if (start >= target) { setVal(target); clearInterval(timer); }
        else setVal(Math.floor(start));
      }, 16);
    }, { threshold: 0.3 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, [target, duration]);
  return <span ref={ref}>{val.toLocaleString()}{suffix}</span>;
};

// ─── Status badge ──────────────────────────────────────────────────────────────
const STATUS = {
  pass:    { bg: 'rgba(34,197,94,0.12)',  text: '#22c55e', border: 'rgba(34,197,94,0.25)',  label: 'PASS' },
  fail:    { bg: 'rgba(239,68,68,0.12)', text: '#ef4444', border: 'rgba(239,68,68,0.25)', label: 'FAIL' },
  partial: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)', label: 'PARTIAL' },
  running: { bg: 'rgba(59,130,246,0.12)', text: '#3b82f6', border: 'rgba(59,130,246,0.25)', label: 'EN COURS' },
  pending: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)', label: 'EN ATTENTE' },
  PASS:    { bg: 'rgba(34,197,94,0.12)',  text: '#22c55e', border: 'rgba(34,197,94,0.25)',  label: 'PASS' },
  FAIL:    { bg: 'rgba(239,68,68,0.12)', text: '#ef4444', border: 'rgba(239,68,68,0.25)', label: 'FAIL' },
  PARTIAL: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', border: 'rgba(245,158,11,0.25)', label: 'PARTIAL' },
};

const StatusBadge = ({ status }) => {
  const s = STATUS[status] || STATUS.pending;
  return (
    <span style={{
      fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 99,
      background: s.bg, color: s.text, border: `1px solid ${s.border}`,
      display: 'inline-flex', alignItems: 'center', gap: 4, whiteSpace: 'nowrap',
    }}>
      {status === 'running' && <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#3b82f6', animation: 'pulse-dot 1s ease-in-out infinite' }} />}
      {s.label}
    </span>
  );
};

// ─── Progress pipeline step map ───────────────────────────────────────────────
const PIPELINE_STEPS = [
  { key: 'analyse',    label: 'Analyse',    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' },
  { key: 'generation', label: 'Génération', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' },
  { key: 'dom',        label: 'DOM Scan',   icon: 'M3 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z' },
  { key: 'scripts',    label: 'Scripts',    icon: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' },
  { key: 'execution',  label: 'Exécution',  icon: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { key: 'rapport',    label: 'Rapport',    icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
];

const PROGRESS_MAP = {
  'Démarrage':                                         { step: 0 },
  'En attente':                                        { step: 0 },
  'Analyse des specs':                                 { step: 0 },
  'Consultation de Groq (génération des cas de test)': { step: 1 },
  'Scan du DOM réel':                                  { step: 2 },
  'Génération du script Selenium':                     { step: 3 },
  'Exécution des tests Selenium':                      { step: 4 },
  'Génération du rapport':                             { step: 5 },
  'Terminé':                                           { step: 6 },
};
const STEP_PCT = [5, 20, 38, 56, 74, 88, 100];

// ─── Animated 6-step Pipeline ─────────────────────────────────────────────────
const LivePipeline = ({ progressLabel, elapsedSec, stepTimings = {} }) => {
  const activeStep = PROGRESS_MAP[progressLabel]?.step ?? 0;
  const pct = STEP_PCT[activeStep] ?? 5;

  return (
    <div style={{ padding: '16px 0' }}>
      {/* Step bubbles */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 0, marginBottom: 20, position: 'relative' }}>
        {PIPELINE_STEPS.map((step, i) => {
          const done    = i < activeStep;
          const active  = i === activeStep;
          const color   = done ? '#22c55e' : active ? '#22d3ee' : 'rgba(255,255,255,0.12)';
          const textCol = done ? '#22c55e' : active ? '#22d3ee' : 'var(--text-muted)';

          return (
            <div key={step.key} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, position: 'relative' }}>
              {/* Connector line */}
              {i > 0 && (
                <div style={{
                  position: 'absolute', left: 0, top: 18, width: '50%', height: 2,
                  background: i <= activeStep ? '#22c55e' : 'rgba(255,255,255,0.08)',
                  transition: 'background 0.4s ease',
                }} />
              )}
              {i < PIPELINE_STEPS.length - 1 && (
                <div style={{
                  position: 'absolute', right: 0, top: 18, width: '50%', height: 2,
                  background: i < activeStep ? '#22c55e' : 'rgba(255,255,255,0.08)',
                  transition: 'background 0.4s ease',
                }} />
              )}

              {/* Circle */}
              <div style={{
                width: 36, height: 36, borderRadius: '50%', zIndex: 1,
                background: done ? 'rgba(34,197,94,0.15)' : active ? 'rgba(34,211,238,0.15)' : 'var(--bg-overlay)',
                border: `2px solid ${color}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.3s ease',
                animation: active ? 'ai-pulse 1.5s ease-in-out infinite' : 'none',
              }}>
                {done ? (
                  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth={2.5}><path d="M5 13l4 4L19 7" /></svg>
                ) : active ? (
                  <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth={1.8} strokeLinecap="round" style={{ animation: 'spin-slow 1.2s linear infinite' }}>
                    <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                ) : (
                  <Icon d={step.icon} size={14} color={color} />
                )}
              </div>

              {/* Label */}
              <div style={{ fontSize: 9, fontWeight: done || active ? 700 : 400, color: textCol, textAlign: 'center', letterSpacing: '0.04em' }}>
                {step.label}
              </div>
              {/* Elapsed time for done steps */}
              {stepTimings[step.key] && (
                <div style={{ fontSize: 8, color: '#22c55e', fontFamily: 'var(--font-mono)' }}>{stepTimings[step.key]}s</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Progress bar */}
      <div style={{ height: 6, borderRadius: 3, background: 'var(--bg-overlay)', overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`,
          background: 'linear-gradient(90deg, #22d3ee, #a855f7)',
          borderRadius: 3, transition: 'width 0.8s ease',
        }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 11 }}>
        <span style={{ color: '#22d3ee' }}>{progressLabel}</span>
        <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {Math.floor(elapsedSec / 60) > 0 && `${Math.floor(elapsedSec / 60)}min `}{elapsedSec % 60}s
        </span>
      </div>
    </div>
  );
};

// ─── New Test Wizard ──────────────────────────────────────────────────────────
const STEPS = ['URL & Specs', 'Options', 'Lancement'];

const NewTestWizard = ({ open, onClose, onTestDone }) => {
  const toast = useToast();
  const [step, setStep] = useState(0);
  const [generating, setGenerating] = useState(false);
  const [progressLabel, setProgressLabel] = useState('Initialisation...');
  const [elapsedSec, setElapsedSec] = useState(0);
  const pollRef  = useRef(null);
  const timerRef = useRef(null);
  const [form, setForm] = useState({ url: '', specs: '', groqApiKey: '', provider: 'groq', headless: true });

  const stopPolling = () => {
    if (pollRef.current)  { clearInterval(pollRef.current);  pollRef.current  = null; }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
  };

  const handleClose = () => {
    stopPolling();
    setGenerating(false);
    setElapsedSec(0);
    setStep(0);
    setForm({ url: '', specs: '', groqApiKey: '', provider: 'groq', headless: true });
    onClose();
  };

  const handleLaunch = async () => {
    setGenerating(true);
    setProgressLabel('Initialisation...');
    setElapsedSec(0);
    timerRef.current = setInterval(() => setElapsedSec((s) => s + 1), 1000);
    try {
      const { data } = await runTest({ targetUrl: form.url, userSpecs: form.specs, groqApiKey: form.groqApiKey, provider: form.provider });
      const testId = data.data._id;
      let ticks = 0;
      pollRef.current = setInterval(async () => {
        if (++ticks > 720) {
          stopPolling(); setGenerating(false);
          toast.error('Timeout', 'La génération a dépassé 60 minutes.');
          return;
        }
        try {
          const { data: pData } = await fetchTestProgress(testId);
          const { status, progress, script, report, reportHtmlUrl } = pData.data;
          setProgressLabel(progress || 'En cours...');
          if (status === 'completed') {
            stopPolling(); setGenerating(false); handleClose();
            onTestDone?.({ _id: testId, targetUrl: form.url, generatedScript: script, report, reportHtmlUrl, status: 'completed' });
            toast.ai('Script généré !', `Script Selenium pour ${form.url} prêt.`);
          } else if (status === 'failed') {
            stopPolling(); setGenerating(false);
            toast.error('Erreur', 'La génération a échoué. Vérifiez que le moteur IA est démarré.');
          }
        } catch (_) { /* keep polling */ }
      }, 2000);
    } catch (err) {
      setGenerating(false);
      toast.error('Erreur', err.response?.data?.message || 'Impossible de joindre le serveur.');
    }
  };

  const step0Valid = form.url.startsWith('http') && form.specs.trim().length > 10;
  const step1Valid = form.provider === 'ollama' || form.groqApiKey.trim().length > 10;

  const stepContent = [
    <div key={0} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>URL Cible *</label>
        <input className="input-base" value={form.url} placeholder="https://votre-site.com"
          onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))} />
        {form.url && !form.url.startsWith('http') && (
          <p style={{ fontSize: 11, color: 'var(--color-warning)', marginTop: 4 }}>⚠ L'URL doit commencer par https://</p>
        )}
      </div>
      <div>
        <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Spécifications (Markdown) *</label>
        <textarea className="input-base" value={form.specs}
          placeholder={`## Fonctionnalités à tester\n\n- Login avec email/mot de passe valide\n- Redirection après connexion`}
          onChange={(e) => setForm((f) => ({ ...f, specs: e.target.value }))}
          style={{ minHeight: 130, resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: 12, lineHeight: 1.6 }} />
      </div>
    </div>,

    <div key={1} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Moteur LLM *</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[{ value: 'groq', label: 'Groq Cloud', icon: '☁️', sub: 'Rapide · Clé API requise' }, { value: 'ollama', label: 'Ollama Local', icon: '🖥️', sub: 'Gratuit · Sans clé' }].map((opt) => (
            <div key={opt.value} onClick={() => setForm((f) => ({ ...f, provider: opt.value }))} style={{
              padding: '12px 14px', borderRadius: 'var(--radius-md)', cursor: 'pointer',
              border: `1.5px solid ${form.provider === opt.value ? 'var(--color-brand)' : 'var(--border)'}`,
              background: form.provider === opt.value ? 'rgba(99,102,241,0.08)' : 'var(--bg-overlay)',
              transition: 'all 150ms ease',
            }}>
              <div style={{ fontSize: 18, marginBottom: 4 }}>{opt.icon}</div>
              <div style={{ fontSize: 13, fontWeight: 600, color: form.provider === opt.value ? 'var(--color-brand)' : 'var(--text-primary)' }}>{opt.label}</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>{opt.sub}</div>
            </div>
          ))}
        </div>
      </div>
      {form.provider === 'groq' && (
        <div>
          <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Clé API Groq *</label>
          <input className="input-base" type="password" value={form.groqApiKey}
            placeholder="gsk_••••••••••••••••••••••••••"
            onChange={(e) => setForm((f) => ({ ...f, groqApiKey: e.target.value }))} />
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: 'var(--bg-overlay)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 500 }}>Mode Headless</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Exécuter sans afficher le navigateur</div>
        </div>
        <div onClick={() => setForm((f) => ({ ...f, headless: !f.headless }))} style={{
          width: 40, height: 22, borderRadius: 11, cursor: 'pointer',
          background: form.headless ? 'var(--color-brand)' : 'var(--border)', position: 'relative', transition: 'background 200ms ease',
        }}>
          <div style={{ position: 'absolute', top: 3, left: form.headless ? 21 : 3, width: 16, height: 16, borderRadius: '50%', background: '#fff', transition: 'left 200ms ease' }} />
        </div>
      </div>
    </div>,

    <div key={2} style={{ textAlign: 'center', padding: '8px 0' }}>
      {generating ? (
        <LivePipeline progressLabel={progressLabel} elapsedSec={elapsedSec} />
      ) : (
        <div>
          <div style={{ fontSize: 36, marginBottom: 16 }}>🚀</div>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Prêt à générer</h3>
          <div className="glass-card" style={{ padding: 16, textAlign: 'left' }}>
            {[['URL', form.url || '—'], ['Specs', `${form.specs.trim().split('\n').length} ligne(s)`], ['Moteur', form.provider.toUpperCase()], ['Headless', form.headless ? 'Oui' : 'Non']].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid var(--border-muted)', fontSize: 12 }}>
                <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                <span style={{ fontWeight: 500, fontFamily: k === 'URL' ? 'var(--font-mono)' : 'inherit', fontSize: k === 'URL' ? 10 : 12 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>,
  ];

  return (
    <Modal isOpen={open} onClose={generating ? undefined : handleClose}
      title={generating ? null : `Nouveau Test — Étape ${step + 1}/${STEPS.length}`} size="md"
      footer={generating ? null : (
        <>
          <button className="btn btn-ghost" onClick={() => step === 0 ? handleClose() : setStep((s) => s - 1)}>
            {step === 0 ? 'Annuler' : '← Retour'}
          </button>
          {step < STEPS.length - 1 ? (
            <button className="btn btn-primary" onClick={() => setStep((s) => s + 1)}
              disabled={(step === 0 && !step0Valid) || (step === 1 && !step1Valid)}
              style={{ opacity: ((step === 0 && !step0Valid) || (step === 1 && !step1Valid)) ? 0.5 : 1 }}>
              Suivant →
            </button>
          ) : (
            <button className="btn btn-ai" onClick={handleLaunch}>🤖 Lancer le test</button>
          )}
        </>
      )}>
      {!generating && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
          {STEPS.map((_, i) => <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= step ? 'var(--color-brand)' : 'var(--border)', transition: 'background 300ms ease' }} />)}
        </div>
      )}
      {stepContent[step]}
    </Modal>
  );
};

// ─── Feature Result Cards ──────────────────────────────────────────────────────
const FeatureCards = ({ testId, reportTests }) => {
  const toast = useToast();
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [scriptModal, setScriptModal] = useState(null);

  useEffect(() => {
    if (!testId) return;
    setLoading(true);
    fetchTestResults(testId)
      .then(({ data }) => setFeatures(data.data || []))
      .catch(() => {
        // Fall back to deriving from report on the client
        const featureMap = {};
        (reportTests || []).forEach((tc) => {
          const match = (tc.name || '').match(/test_CT_\d+_(.+?)(?:___|$)/);
          const rawName = match ? match[1] : tc.name || 'unknown';
          const area = rawName.replace(/_/g, ' ').trim();
          if (!featureMap[area]) featureMap[area] = { name: area, passed: 0, total: 0, testCases: [] };
          featureMap[area].total++;
          if (tc.statut === 'PASS') featureMap[area].passed++;
          featureMap[area].testCases.push(tc);
        });
        setFeatures(Object.entries(featureMap).map(([, d], i) => ({
          featureId: `F-${String(i + 1).padStart(3, '0')}`,
          name: d.name,
          status: d.passed === d.total ? 'PASS' : d.passed === 0 ? 'FAIL' : 'PARTIAL',
          passed: d.passed,
          total: d.total,
          testCases: d.testCases,
        })));
      })
      .finally(() => setLoading(false));
  }, [testId, reportTests]);

  if (!features?.length && !loading) return null;

  return (
    <div>
      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12, color: 'var(--text-secondary)' }}>
        Résultats par Fonctionnalité
      </div>
      {loading ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
          {[1, 2, 3].map((i) => <div key={i} style={{ height: 80, borderRadius: 10, background: 'rgba(255,255,255,0.04)', animation: 'shimmer 1.8s infinite linear', backgroundSize: '1000px 100%' }} />)}
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
          {features.map((f) => {
            const color = f.status === 'PASS' ? '#22c55e' : f.status === 'FAIL' ? '#ef4444' : '#f59e0b';
            const isExpanded = expandedId === f.featureId;
            return (
              <div key={f.featureId} className="glass-card" style={{ overflow: 'hidden', cursor: 'pointer', border: `1px solid ${color}25` }}
                onClick={() => setExpandedId(isExpanded ? null : f.featureId)}>
                <div style={{ padding: '14px 16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{f.featureId}</span>
                    <StatusBadge status={f.status} />
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 8, lineHeight: 1.4 }}>{f.name}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${f.total > 0 ? (f.passed / f.total) * 100 : 0}%`, background: color, borderRadius: 2, transition: 'width 0.5s ease' }} />
                    </div>
                    <span style={{ fontSize: 10, fontWeight: 700, color }}>{f.passed}/{f.total}</span>
                  </div>
                </div>
                {isExpanded && (
                  <div style={{ borderTop: '1px solid var(--border)', maxHeight: 160, overflowY: 'auto' }}>
                    {(f.testCases || []).map((tc, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 11 }}>
                        <span style={{ color: tc.statut === 'PASS' ? '#22c55e' : '#ef4444', fontWeight: 700 }}>{tc.statut === 'PASS' ? '✓' : '✗'}</span>
                        <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>{tc.name?.replace(/test_CT_\d+_/, '').replace(/_/g, ' ')}</span>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{(tc.duration || tc.durée_secondes || 0).toFixed(2)}s</span>
                      </div>
                    ))}
                    <div style={{ padding: '8px 16px' }}>
                      <button onClick={(e) => { e.stopPropagation(); setScriptModal(f); }}
                        className="btn btn-ghost" style={{ fontSize: 10, padding: '3px 8px', width: '100%' }}>
                        Voir les scripts générés →
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {scriptModal && (
        <Modal isOpen title={`Scripts — ${scriptModal.name}`} onClose={() => setScriptModal(null)} size="lg">
          <pre style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid var(--border)', borderRadius: 8, padding: 16, fontFamily: 'var(--font-mono)', fontSize: 11, lineHeight: 1.7, overflow: 'auto', maxHeight: 400, color: '#e2e8f0' }}>
            {scriptModal.testCases?.map((tc) => `# ${tc.name}\n# Status: ${tc.statut}\n`).join('\n') || 'No script data available.'}
          </pre>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button onClick={() => { navigator.clipboard.writeText(scriptModal.testCases?.map((tc) => `# ${tc.name}`).join('\n') || ''); toast.success('Copié !', ''); }} className="btn btn-ghost" style={{ fontSize: 11 }}>📋 Copier</button>
          </div>
        </Modal>
      )}
    </div>
  );
};

// ─── Enhanced Report Modal with Recharts ──────────────────────────────────────
const DonutChart = ({ passed, failed, errors }) => {
  const data = [
    { name: 'Passés',  value: passed,         color: '#22c55e' },
    { name: 'Échoués', value: failed,          color: '#ef4444' },
    { name: 'Erreurs', value: errors || 0,     color: '#f59e0b' },
  ].filter((d) => d.value > 0);

  if (!data.length) return null;
  const total = data.reduce((a, b) => a + b.value, 0);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
      <ResponsiveContainer width={120} height={120}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={32} outerRadius={55} paddingAngle={3} dataKey="value" strokeWidth={0}>
            {data.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
          </Pie>
          <Tooltip formatter={(v, n) => [`${v} (${Math.round(v/total*100)}%)`, n]} contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 11 }} />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {data.map((d) => (
          <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: d.color, flexShrink: 0 }} />
            <span style={{ color: 'var(--text-secondary)' }}>{d.name}</span>
            <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: d.color }}>{d.value}</span>
          </div>
        ))}
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Total: {total}</div>
      </div>
    </div>
  );
};

const TestReportModal = ({ test, open, onClose }) => {
  const [tab, setTab] = useState('summary');
  const [logFilter, setLogFilter] = useState('all');
  const toast = useToast();

  useEffect(() => { setTab('summary'); }, [test]);

  const script = test?.generatedScript || '# Aucun script disponible.';
  const logs   = test?.logs || [];
  const filteredLogs = logFilter === 'all' ? logs : logs.filter((l) => l.level === logFilter);

  const handleDownloadScript = () => {
    const blob = new Blob([script], { type: 'text/x-python' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = `test_${test?._id || 'script'}.py`; a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadReport = () => {
    if (test?.reportHtmlUrl) {
      window.open(test.reportHtmlUrl, '_blank');
    } else {
      toast.info('Rapport', 'Aucun rapport HTML disponible pour ce test.');
    }
  };

  const passed   = test?.report?.passed || 0;
  const failed   = test?.report?.failed || 0;
  const errors   = test?.report?.errors || 0;
  const duration = test?.report?.duration_seconds || 0;
  const total    = test?.report?.total || 0;

  const tabs = [
    { key: 'summary', label: 'Résumé visuel' },
    { key: 'code',    label: 'Scripts' },
    { key: 'logs',    label: 'Logs pytest' },
    { key: 'export',  label: 'Export' },
  ];

  return (
    <Modal isOpen={open} onClose={onClose} title={test?.name || test?.targetUrl} size="lg">
      {/* Header KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 20 }}>
        {[
          { label: 'Statut',  val: <StatusBadge status={test?.status || 'pass'} />, mono: false },
          { label: 'Durée',   val: `${duration.toFixed(1)}s`, mono: true },
          { label: 'Total',   val: total, mono: true },
          { label: 'Succès',  val: total > 0 ? `${Math.round(passed/total*100)}%` : '—', mono: true },
        ].map(({ label, val, mono }) => (
          <div key={label} className="glass-card" style={{ padding: '10px 14px', textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 6 }}>{label}</div>
            <div style={{ fontSize: mono ? 18 : 14, fontWeight: 700, fontFamily: mono ? 'var(--font-mono)' : 'inherit' }}>{val}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
        {tabs.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)} style={{
            padding: '8px 16px', fontSize: 12, fontWeight: 500, cursor: 'pointer',
            background: 'transparent', border: 'none', outline: 'none',
            color: tab === t.key ? 'var(--color-brand)' : 'var(--text-muted)',
            borderBottom: `2px solid ${tab === t.key ? 'var(--color-brand)' : 'transparent'}`,
            marginBottom: -1, transition: 'all 120ms ease',
          }}>{t.label}</button>
        ))}
      </div>

      {/* Tab: Summary */}
      {tab === 'summary' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {test?.report ? (
            <>
              <DonutChart passed={passed} failed={failed} errors={errors} />
              <div className="glass-card" style={{ overflow: 'hidden' }}>
                {(test.report.tests || []).map((tc, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 14px', borderBottom: '1px solid var(--border-muted)', fontSize: 11 }}>
                    <span style={{ fontWeight: 700, color: tc.statut === 'PASS' ? '#22c55e' : '#ef4444' }}>{tc.statut === 'PASS' ? '✓' : '✗'}</span>
                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>{tc.name}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{(tc.durée_secondes || 0).toFixed(2)}s</span>
                    <StatusBadge status={tc.statut === 'PASS' ? 'PASS' : 'FAIL'} />
                  </div>
                ))}
              </div>
            </>
          ) : (
            <EmptyState type="generic" title="Aucun résultat" message="Le rapport sera disponible après la prochaine exécution." />
          )}
        </div>
      )}

      {/* Tab: Code with syntax-style highlighting */}
      {tab === 'code' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginBottom: 8 }}>
            <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}
              onClick={() => { navigator.clipboard.writeText(script); toast.success('Copié !', ''); }}>📋 Copier</button>
            <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }} onClick={handleDownloadScript}>⬇ .py</button>
          </div>
          <pre style={{
            background: '#0d1117', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 8,
            padding: 16, fontFamily: 'var(--font-mono)', fontSize: 11, lineHeight: 1.7,
            overflowX: 'auto', overflowY: 'auto', maxHeight: 340, color: '#e6edf3',
          }}>
            {script.split('\n').map((line, i) => {
              let color = '#e6edf3';
              if (/^(import|from|def |class )/.test(line))     color = '#ff7b72';
              else if (/^#/.test(line.trim()))                   color = '#8b949e';
              else if (/"[^"]*"|'[^']*'/.test(line))            color = '#a5d6ff';
              else if (/\b(assert|return|if|else|for|while|try|except|with)\b/.test(line)) color = '#ff7b72';
              return <div key={i} style={{ color, minHeight: '1.4em' }}><span style={{ color: '#484f58', userSelect: 'none', marginRight: 12, fontSize: 9 }}>{String(i + 1).padStart(3, ' ')}</span>{line}</div>;
            })}
          </pre>
        </div>
      )}

      {/* Tab: Logs */}
      {tab === 'logs' && (
        <div>
          <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
            {['all', 'info', 'error', 'warning'].map((f) => {
              const C = { info: '#3b82f6', error: '#ef4444', warning: '#f59e0b', all: 'var(--color-brand)' };
              return (
                <button key={f} onClick={() => setLogFilter(f)} style={{
                  fontSize: 10, fontWeight: 600, padding: '2px 10px', borderRadius: 99, cursor: 'pointer', textTransform: 'uppercase',
                  border: `1px solid ${logFilter === f ? C[f] : 'var(--border)'}`,
                  background: logFilter === f ? `${C[f]}18` : 'transparent',
                  color: logFilter === f ? C[f] : 'var(--text-muted)',
                }}>{f}</button>
              );
            })}
          </div>
          <div style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid var(--border)', borderRadius: 8, padding: 12, fontFamily: 'var(--font-mono)', fontSize: 11, maxHeight: 300, overflowY: 'auto' }}>
            {filteredLogs.length ? filteredLogs.map((l, i) => {
              const C = { info: '#3b82f6', error: '#ef4444', warning: '#f59e0b' };
              return (
                <div key={i} style={{ display: 'flex', gap: 10, padding: '4px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                  <span style={{ color: C[l.level] || '#3b82f6', fontWeight: 700, width: 60, flexShrink: 0 }}>{(l.level || 'info').toUpperCase()}</span>
                  <span style={{ color: 'var(--text-secondary)', wordBreak: 'break-word' }}>{l.message}</span>
                </div>
              );
            }) : <div style={{ color: 'var(--text-muted)', padding: 8 }}>Aucun log {logFilter !== 'all' ? `de niveau "${logFilter}"` : ''}.</div>}
          </div>
        </div>
      )}

      {/* Tab: Export */}
      {tab === 'export' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {[
            { icon: '📄', label: 'Rapport HTML', sub: 'Ouvrir le rapport interactif dans le navigateur', action: handleDownloadReport },
            { icon: '🐍', label: 'Script Python (.py)', sub: 'Télécharger le script Selenium généré', action: handleDownloadScript },
            { icon: '📋', label: 'Copier le script', sub: 'Copier le code dans le presse-papiers', action: () => { navigator.clipboard.writeText(script); toast.success('Copié !', ''); } },
            { icon: '🔗', label: 'Partager le lien', sub: "Copier l'URL de ce test", action: () => { navigator.clipboard.writeText(`${window.location.origin}/dashboard?test=${test?._id}`); toast.success('Lien copié !', ''); } },
          ].map((item) => (
            <button key={item.label} onClick={item.action} style={{
              display: 'flex', alignItems: 'center', gap: 14, padding: '14px 18px',
              background: 'var(--bg-overlay)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
              cursor: 'pointer', textAlign: 'left', transition: 'all 150ms ease', width: '100%',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-brand)'; e.currentTarget.style.background = 'var(--color-brand-muted)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'var(--bg-overlay)'; }}>
              <span style={{ fontSize: 22 }}>{item.icon}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600 }}>{item.label}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{item.sub}</div>
              </div>
            </button>
          ))}
        </div>
      )}
    </Modal>
  );
};

// ─── Filterable Test History Table with sparkline ─────────────────────────────
const TestHistoryTable = ({ tests, onOpenReport }) => {
  const [statusFilter, setStatusFilter] = useState('all');
  const [llmFilter,    setLlmFilter]    = useState('all');
  const [fromDate,     setFromDate]     = useState('');
  const [toDate,       setToDate]       = useState('');
  const [loading,      setLoading]      = useState(false);
  const [rows,         setRows]         = useState(tests);
  const [page,         setPage]         = useState(1);
  const perPage = 8;

  // Sync with parent tests prop when no filters applied
  useEffect(() => { setRows(tests); }, [tests]);

  const applyFilters = useCallback(async () => {
    const hasFilters = statusFilter !== 'all' || llmFilter !== 'all' || fromDate || toDate;
    if (!hasFilters) { setRows(tests); return; }
    setLoading(true);
    try {
      const { data } = await fetchFilteredTests({
        status: statusFilter !== 'all' ? statusFilter : undefined,
        llm:    llmFilter    !== 'all' ? llmFilter    : undefined,
        from:   fromDate || undefined,
        to:     toDate   || undefined,
      });
      setRows((data.data || []).map(mapDbTest));
    } catch (_) {
      setRows(tests.filter((t) => {
        if (statusFilter !== 'all' && t.status !== statusFilter) return false;
        if (llmFilter    !== 'all' && t.llmEngine !== llmFilter) return false;
        return true;
      }));
    } finally {
      setLoading(false);
    }
  }, [statusFilter, llmFilter, fromDate, toDate, tests]);

  useEffect(() => { applyFilters(); }, [applyFilters]);

  // Sparkline: success rate over last 10 runs
  const sparkData = useMemo(() => {
    const last10 = [...tests].reverse().slice(-10);
    return last10.map((t, i) => ({
      i,
      rate: t.status === 'pass' ? 100 : t.status === 'fail' ? 0 : null,
    })).filter((d) => d.rate !== null);
  }, [tests]);

  const paginated  = rows.slice((page - 1) * perPage, page * perPage);
  const totalPages = Math.ceil(rows.length / perPage);

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      {/* Toolbar */}
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ fontSize: 13, fontWeight: 600, marginRight: 4 }}>Historique</span>

        {/* Status filter */}
        {['all', 'pass', 'fail', 'running', 'pending'].map((f) => (
          <button key={f} onClick={() => { setStatusFilter(f); setPage(1); }} style={{
            fontSize: 10, fontWeight: 600, padding: '2px 10px', borderRadius: 99, cursor: 'pointer', textTransform: 'uppercase',
            border: `1px solid ${statusFilter === f ? 'var(--color-brand)' : 'var(--border)'}`,
            background: statusFilter === f ? 'var(--color-brand-muted)' : 'transparent',
            color: statusFilter === f ? 'var(--color-brand)' : 'var(--text-muted)',
          }}>{f === 'all' ? 'Tous' : f}</button>
        ))}

        {/* LLM filter */}
        <select value={llmFilter} onChange={(e) => { setLlmFilter(e.target.value); setPage(1); }}
          className="input-base" style={{ width: 130, fontSize: 11, padding: '4px 8px' }}>
          <option value="all">Tous les moteurs</option>
          <option value="groq">Groq</option>
          <option value="ollama">Ollama</option>
        </select>

        {/* Date range */}
        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)}
          className="input-base" style={{ width: 140, fontSize: 11, padding: '4px 8px' }} />
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>→</span>
        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)}
          className="input-base" style={{ width: 140, fontSize: 11, padding: '4px 8px' }} />

        {/* Sparkline */}
        {sparkData.length >= 3 && (
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Tendance (10 derniers)</span>
            <ResponsiveContainer width={80} height={24}>
              <LineChart data={sparkData}>
                <Line type="monotone" dataKey="rate" stroke="#22d3ee" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Table */}
      {loading ? (
        <div style={{ padding: 16 }}>{[1,2,3].map((i) => <TestCardSkeleton key={i} />)}</div>
      ) : paginated.length === 0 ? (
        <EmptyState type="tests" title="Aucun test trouvé" message="Ajustez les filtres ou lancez un nouveau test." />
      ) : (
        <>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {['URL', 'Moteur', 'Statut', 'Durée', 'Date', 'Actions'].map((h) => (
                  <th key={h} style={{ padding: '10px 14px', fontSize: 10, fontWeight: 600, color: 'var(--text-muted)', textAlign: 'left', textTransform: 'uppercase', letterSpacing: '0.06em', whiteSpace: 'nowrap' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginated.map((test) => (
                <tr key={test.id} style={{ borderBottom: '1px solid var(--border)', transition: 'background 120ms ease' }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}>
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 7, height: 7, borderRadius: '50%', flexShrink: 0, background: { pass: '#22c55e', fail: '#ef4444', running: '#3b82f6', pending: '#f59e0b' }[test.status] || '#64748b', animation: test.status === 'running' ? 'pulse-dot 1s ease-in-out infinite' : 'none' }} />
                      <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>{test.name}</span>
                    </div>
                  </td>
                  <td style={{ padding: '10px 14px' }}>
                    <span style={{ fontSize: 10, fontWeight: 600, padding: '2px 7px', borderRadius: 4, background: 'var(--bg-overlay)', border: '1px solid var(--border)', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                      {test.llmEngine || '—'}
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px' }}><StatusBadge status={test.status} /></td>
                  <td style={{ padding: '10px 14px', fontSize: 11, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{test.duration || '—'}</td>
                  <td style={{ padding: '10px 14px', fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{test.date}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <button onClick={() => onOpenReport(test)} className="btn btn-ghost" style={{ fontSize: 11, padding: '3px 8px' }}>Rapport</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {totalPages > 1 && (
            <div style={{ padding: '10px 16px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{rows.length} test(s)</span>
              <div style={{ display: 'flex', gap: 4 }}>
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button key={i} onClick={() => setPage(i + 1)} style={{
                    width: 28, height: 28, borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: 'pointer',
                    background: page === i + 1 ? 'var(--color-brand)' : 'transparent',
                    border: `1px solid ${page === i + 1 ? 'var(--color-brand)' : 'var(--border)'}`,
                    color: page === i + 1 ? '#fff' : 'var(--text-muted)',
                  }}>{i + 1}</button>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// ─── Run Comparator ───────────────────────────────────────────────────────────
const RunComparator = ({ tests }) => {
  const [id1, setId1] = useState('');
  const [id2, setId2] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const completedTests = tests.filter((t) => t.status === 'pass' || t.status === 'fail');

  const handleCompare = async () => {
    if (!id1 || !id2 || id1 === id2) {
      toast.error('Sélection invalide', 'Choisissez 2 tests différents.');
      return;
    }
    setLoading(true);
    try {
      const { data } = await fetchCompareTests(id1, id2);
      setResult(data.data);
    } catch (err) {
      toast.error('Erreur', err.response?.data?.message || 'Impossible de comparer.');
    } finally {
      setLoading(false);
    }
  };

  const DIRECTION_STYLE = {
    improved:  { color: '#22c55e', icon: '↑', label: 'Amélioré' },
    regressed: { color: '#ef4444', icon: '↓', label: 'Régressé' },
    unchanged: { color: 'var(--text-muted)', icon: '─', label: 'Inchangé' },
    new:       { color: '#22d3ee', icon: '+', label: 'Nouveau' },
    removed:   { color: '#f59e0b', icon: '−', label: 'Supprimé' },
  };

  return (
    <div className="glass-card" style={{ overflow: 'hidden' }}>
      <div style={{ padding: '14px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span style={{ fontSize: 13, fontWeight: 600 }}>Comparateur de Runs</span>
        <select value={id1} onChange={(e) => setId1(e.target.value)} className="input-base" style={{ flex: 1, minWidth: 180, fontSize: 11, padding: '5px 8px' }}>
          <option value="">— Run A —</option>
          {completedTests.map((t) => <option key={t.id} value={t.id}>{t.date} · {t.name.slice(0, 30)}</option>)}
        </select>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>vs</span>
        <select value={id2} onChange={(e) => setId2(e.target.value)} className="input-base" style={{ flex: 1, minWidth: 180, fontSize: 11, padding: '5px 8px' }}>
          <option value="">— Run B —</option>
          {completedTests.map((t) => <option key={t.id} value={t.id}>{t.date} · {t.name.slice(0, 30)}</option>)}
        </select>
        <button onClick={handleCompare} disabled={!id1 || !id2 || loading} className="btn btn-primary" style={{ fontSize: 12, padding: '6px 14px', opacity: (!id1 || !id2) ? 0.5 : 1 }}>
          {loading ? '…' : 'Comparer →'}
        </button>
      </div>

      {result && (
        <div style={{ maxHeight: 320, overflowY: 'auto' }}>
          {/* Summary row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 10, padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
            {[
              { label: 'Amélioré',  count: result.diff.filter((d) => d.direction === 'improved').length,  color: '#22c55e' },
              { label: 'Régressé', count: result.diff.filter((d) => d.direction === 'regressed').length, color: '#ef4444' },
              { label: 'Inchangé', count: result.diff.filter((d) => d.direction === 'unchanged').length, color: 'var(--text-muted)' },
              { label: 'Nouveau',  count: result.diff.filter((d) => d.direction === 'new').length,       color: '#22d3ee' },
            ].map((s) => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 700, fontFamily: 'var(--font-mono)', color: s.color }}>{s.count}</div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Diff table */}
          {result.diff.map((d, i) => {
            const style = DIRECTION_STYLE[d.direction] || DIRECTION_STYLE.unchanged;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 16px', borderBottom: '1px solid rgba(255,255,255,0.04)', fontSize: 12 }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: style.color, width: 20, textAlign: 'center' }}>{style.icon}</span>
                <span style={{ flex: 1, color: 'var(--text-secondary)' }}>{d.name}</span>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  {d.run1 && <StatusBadge status={d.run1.status} />}
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>→</span>
                  {d.run2 && <StatusBadge status={d.run2.status} />}
                </div>
                <span style={{ fontSize: 10, fontWeight: 600, color: style.color, minWidth: 60, textAlign: 'right' }}>{style.label}</span>
              </div>
            );
          })}
        </div>
      )}

      {!result && (
        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)', fontSize: 12 }}>
          Sélectionnez deux runs pour visualiser les changements feature par feature
        </div>
      )}
    </div>
  );
};

// ─── Time Saved Counter ────────────────────────────────────────────────────────
const TimeSavedCard = ({ completedCount }) => {
  const savedMin = completedCount * 20;
  const savedH   = savedMin >= 60 ? `${(savedMin / 60).toFixed(1).replace('.0', '')}h` : `${savedMin}min`;
  const scriptsEq = completedCount;

  return (
    <div className="glass-card card-hover" style={{ padding: 20, background: 'linear-gradient(135deg, rgba(34,211,238,0.05) 0%, rgba(168,85,247,0.05) 100%)', border: '1px solid rgba(34,211,238,0.15)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(34,211,238,0.12)', border: '1px solid rgba(34,211,238,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0" />
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Temps Économisé</div>
          <div style={{ fontSize: 28, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#22d3ee', marginBottom: 4 }}>
            <CountUp target={savedMin >= 60 ? parseFloat(savedH) : savedMin} suffix={savedMin >= 60 ? 'h' : ' min'} />
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            <CountUp target={scriptsEq} /> script(s) × 20 min · vs rédaction manuelle
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Summary Cards ────────────────────────────────────────────────────────────
const SummaryCard = memo(({ icon, title, value, sub, color = '#6366f1', progress }) => (
  <div className="glass-card card-hover" style={{ padding: 20 }}>
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
      <div style={{ width: 40, height: 40, borderRadius: 10, flexShrink: 0, background: `${color}18`, border: `1px solid ${color}25`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon d={icon} size={18} color={color} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{title}</div>
        <div style={{ fontSize: 24, fontWeight: 700, fontFamily: 'var(--font-mono)', marginBottom: 4 }}>{value}</div>
        <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{sub}</div>
        {progress !== undefined && (
          <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${progress}%`, background: color, borderRadius: 2, animation: 'bar-grow 0.6s ease' }} />
            </div>
            <span style={{ fontSize: 10, fontWeight: 700, color }}>{progress}%</span>
          </div>
        )}
      </div>
    </div>
  </div>
));

// ─── DB test → UI shape ───────────────────────────────────────────────────────
const mapDbTest = (t) => ({
  id:          t._id,
  name:        t.targetUrl,
  project:     t.analysisType,
  llmEngine:   t.llmEngine || null,
  status:      t.status === 'completed'
                 ? ((t.report?.passed ?? 0) > 0 ? 'pass' : 'fail')
                 : t.status === 'failed' ? 'fail'
                 : t.status === 'running' ? 'running'
                 : 'pending',
  duration:    t.report?.duration_seconds ? `${t.report.duration_seconds.toFixed(1)}s` : null,
  date:        new Date(t.createdAt).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }),
  progress:    t.status === 'running' ? 50 : null,
  generatedScript: t.generatedScript || null,
  report:      t.report || null,
  reportHtmlUrl: t.reportHtmlUrl || null,
  logs:        t.logs || [],
  url:         t.targetUrl,
  _id:         t._id,
  createdAt:   t.createdAt,
});

// ─── Projects Grid ────────────────────────────────────────────────────────────
const getProjectEmoji = (hostname) => {
  const h = (hostname || '').toLowerCase();
  if (h.includes('shop') || h.includes('store') || h.includes('commerce') || h.includes('cart')) return '🛒';
  if (h.includes('auth') || h.includes('login') || h.includes('password') || h.includes('account')) return '🔐';
  if (h.includes('demo') || h.includes('test') || h.includes('staging')) return '🧪';
  if (h.includes('api') || h.includes('backend') || h.includes('service')) return '⚡';
  if (h.includes('analytics') || h.includes('dashboard') || h.includes('stats')) return '📊';
  return '🌐';
};
const PROJ_COLORS = ['#6366f1', '#22c55e', '#a855f7', '#f59e0b', '#3b82f6', '#ef4444', '#06b6d4', '#84cc16'];

const ProjectsGrid = ({ projects }) => (
  <div>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
      <h2 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-secondary)' }}>Mes Projets</h2>
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
      {projects.map((p) => (
        <div key={p.id} className="glass-card card-hover" style={{ padding: 18, cursor: 'pointer' }}>
          <div style={{ fontSize: 28, marginBottom: 10 }}>{p.emoji}</div>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{p.name}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12 }}>{p.tests} tests</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${p.success}%`, background: p.color, borderRadius: 2 }} />
            </div>
            <span style={{ fontSize: 10, fontWeight: 700, color: p.color }}>{p.success}%</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// ─── USER DASHBOARD ───────────────────────────────────────────────────────────
export default function UserDashboard() {
  const { user } = useAuth();
  const toast = useToast();
  const [loading,     setLoading]     = useState(true);
  const [wizardOpen,  setWizardOpen]  = useState(false);
  const [tests,       setTests]       = useState([]);
  const [resultTest,  setResultTest]  = useState(null);
  const [reportTest,  setReportTest]  = useState(null);

  const loadTests = useCallback(async () => {
    try {
      const { data } = await fetchMyTests();
      setTests((data.data || []).map(mapDbTest));
    } catch (_) {}
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadTests(); }, [loadTests]);

  const handleTestDone = useCallback((newTest) => {
    const mapped = mapDbTest({ ...newTest, createdAt: new Date().toISOString() });
    setTests((prev) => [mapped, ...prev]);
    setResultTest(mapped);
  }, []);

  // Refresh running tests every 5s
  useEffect(() => {
    if (!tests.some((t) => t.status === 'running')) return;
    const id = setTimeout(loadTests, 5000);
    return () => clearTimeout(id);
  }, [tests, loadTests]);

  // Stats
  const completedTests = tests.filter((t) => t.status === 'pass' || t.status === 'fail');
  const passedTests    = tests.filter((t) => t.status === 'pass');
  const runningTests   = tests.filter((t) => t.status === 'running');
  const successRate    = completedTests.length > 0 ? Math.round(passedTests.length / completedTests.length * 100) : 0;

  const projects = useMemo(() => {
    const domainMap = {};
    tests.forEach((t) => {
      let domain = 'Autre';
      try { domain = new URL(t.url || '').hostname.replace('www.', ''); } catch (_) {}
      if (!domainMap[domain]) domainMap[domain] = { tests: 0, passed: 0 };
      domainMap[domain].tests++;
      if (t.status === 'pass') domainMap[domain].passed++;
    });
    return Object.entries(domainMap).map(([name, d], i) => ({
      id: i + 1, emoji: getProjectEmoji(name), name,
      tests: d.tests, success: d.tests > 0 ? Math.round(d.passed / d.tests * 100) : 0,
      color: PROJ_COLORS[i % PROJ_COLORS.length],
    }));
  }, [tests]);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Bonjour' : hour < 18 ? 'Bon après-midi' : 'Bonsoir';
  const userName = user?.name?.split(' ')[0] || user?.email?.split('@')[0] || 'Dev';

  // Latest completed test for feature cards
  const latestCompleted = tests.find((t) => t.status === 'pass' || t.status === 'fail');

  return (
    <div className="layout-main">
      <Topbar />
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', animation: 'fade-in-up 0.3s ease' }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.03em', marginBottom: 4 }}>
              {greeting}, {userName} 👋
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Tableau de bord AutoTest · {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
            </p>
          </div>
          <button onClick={() => setWizardOpen(true)} className="btn btn-primary"
            style={{ fontSize: 13, padding: '10px 20px', boxShadow: 'var(--shadow-glow-brand)', animation: 'ai-pulse 3s ease-in-out infinite' }}>
            + Nouveau Test
          </button>
        </div>

        {/* Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
          {loading ? [1, 2, 3, 4].map((i) => <KPICardSkeleton key={i} />) : (
            <>
              <SummaryCard
                icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                title="Tests Actifs" value={runningTests.length}
                sub={runningTests.length > 0 ? `${runningTests.length} en cours` : 'Aucun test actif'}
                color="#3b82f6" progress={runningTests.length > 0 ? 50 : undefined} />
              <SummaryCard
                icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                title="Taux de Succès" value={`${successRate}%`}
                sub={completedTests.length > 0 ? `${passedTests.length}/${completedTests.length} terminés` : 'Aucun test terminé'}
                color="#a855f7" progress={successRate || undefined} />
              <SummaryCard
                icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2"
                title="Tests Total" value={tests.length}
                sub={`${completedTests.length} terminé(s) · ${runningTests.length} actif(s)`}
                color="#6366f1" />
              <TimeSavedCard completedCount={completedTests.length} />
            </>
          )}
        </div>

        {/* Feature Result Cards — latest completed test */}
        {!loading && latestCompleted?.report?.tests?.length > 0 && (
          <FeatureCards testId={latestCompleted._id} reportTests={latestCompleted.report?.tests} />
        )}

        {/* History Table with Filters */}
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[1, 2, 3].map((i) => <TestCardSkeleton key={i} />)}
          </div>
        ) : (
          <TestHistoryTable tests={tests} onOpenReport={setReportTest} />
        )}

        {/* Run Comparator */}
        {!loading && completedTests.length >= 2 && (
          <RunComparator tests={tests} />
        )}

        {/* Projects */}
        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
            {[1, 2, 3].map((i) => <ProjectCardSkeleton key={i} />)}
          </div>
        ) : projects.length > 0 && (
          <ProjectsGrid projects={projects} />
        )}

      </div>

      {/* New Test Wizard */}
      <NewTestWizard open={wizardOpen} onClose={() => setWizardOpen(false)} onTestDone={handleTestDone} />

      {/* Report after generation */}
      {resultTest && (
        <TestReportModal test={resultTest} open={!!resultTest} onClose={() => setResultTest(null)} />
      )}

      {/* Report from history table click */}
      {reportTest && (
        <TestReportModal test={reportTest} open={!!reportTest} onClose={() => setReportTest(null)} />
      )}
    </div>
  );
}
