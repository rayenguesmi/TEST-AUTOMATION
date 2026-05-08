import { useState, useRef } from 'react';
import Modal from './Modal';
import { useToast } from './Toast';
import { runTest, fetchTestProgress } from '../api/auth';

const PROGRESS_MAP = {
  'Démarrage':                                          { label: 'Initialisation...',                step: 0 },
  'En attente':                                         { label: 'Initialisation...',                step: 0 },
  'Analyse des specs':                                  { label: 'Analyse des specs...',             step: 1 },
  'Consultation de Groq (génération des cas de test)':  { label: 'Consultation de Groq...',          step: 2 },
  'Scan du DOM réel':                                   { label: 'Scan du DOM réel...',              step: 3 },
  'Génération du script Selenium':                      { label: 'Génération du script Selenium...', step: 4 },
  'Exécution des tests Selenium':                       { label: 'Exécution des tests Selenium...',  step: 5 },
  'Génération du rapport':                              { label: 'Génération du rapport...',          step: 6 },
  'Terminé':                                            { label: 'Terminé !',                        step: 7 },
};
const STEP_PCT  = { 0: 5, 1: 15, 2: 32, 3: 50, 4: 65, 5: 82, 6: 93, 7: 100 };
const toLabel   = (p) => PROGRESS_MAP[p]?.label   || p || 'En cours...';
const toStepPct = (p) => STEP_PCT[PROGRESS_MAP[p]?.step ?? 0] ?? 5;
const STEPS     = ['URL & Specs', 'Options', 'Confirmation'];

export default function NewTestWizard({ open, onClose, onTestDone }) {
  const toast = useToast();
  const [step, setStep]               = useState(0);
  const [generating, setGenerating]   = useState(false);
  const [progressLabel, setProgressLabel] = useState('Initialisation...');
  const [progressPct, setProgressPct] = useState(0);
  const [elapsedSec, setElapsedSec]   = useState(0);
  const pollRef  = useRef(null);
  const timerRef = useRef(null);
  const [form, setForm] = useState({
    url: '', specs: '', groqApiKey: '', provider: 'groq', headless: true,
  });

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
    setProgressPct(5);
    setElapsedSec(0);
    timerRef.current = setInterval(() => setElapsedSec(s => s + 1), 1000);
    try {
      const { data } = await runTest({
        targetUrl: form.url, userSpecs: form.specs,
        groqApiKey: form.groqApiKey, provider: form.provider,
      });
      const testId = data.data._id;
      let pollTicks = 0;
      const MAX_TICKS = 720;

      pollRef.current = setInterval(async () => {
        if (++pollTicks > MAX_TICKS) {
          stopPolling();
          setGenerating(false);
          toast.error('Timeout', 'La génération a dépassé 60 minutes. Vérifiez que le moteur IA est démarré.');
          return;
        }
        try {
          const { data: pData } = await fetchTestProgress(testId);
          const { status, progress, script, report, reportHtmlUrl } = pData.data;
          setProgressLabel(toLabel(progress));
          setProgressPct(toStepPct(progress));
          if (status === 'completed') {
            stopPolling();
            setGenerating(false);
            handleClose();
            onTestDone?.({ _id: testId, targetUrl: form.url, generatedScript: script, report, reportHtmlUrl, status: 'completed' });
            toast.ai('Script généré !', `Le script Selenium pour ${form.url} est prêt.`);
          } else if (status === 'failed') {
            stopPolling();
            setGenerating(false);
            toast.error('Erreur', 'La génération du script a échoué. Vérifiez que le moteur IA est démarré.');
          }
        } catch (_) { /* network hiccup */ }
      }, 2000);

    } catch (err) {
      setGenerating(false);
      toast.error('Erreur', err.response?.data?.message || 'Impossible de joindre le serveur.');
    }
  };

  const step0Valid = form.url.startsWith('http') && form.specs.trim().length > 10;
  const step1Valid = form.provider === 'ollama' || form.groqApiKey.trim().length > 10;

  const stepContent = [
    // ── Step 0 — URL + Specs ──────────────────────────────────────────────────
    <div key={0} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <label style={labelStyle}>URL Cible *</label>
        <input className="input-base" value={form.url} placeholder="https://votre-site.com"
          onChange={e => setForm(f => ({ ...f, url: e.target.value }))} />
        {form.url && !form.url.startsWith('http') && (
          <p style={{ fontSize: 11, color: 'var(--color-warning)', marginTop: 4 }}>
            ⚠ L'URL doit commencer par https://
          </p>
        )}
      </div>
      <div>
        <label style={labelStyle}>Spécifications (Markdown) *</label>
        <textarea
          className="input-base"
          value={form.specs}
          placeholder={`## Fonctionnalités à tester\n\n- Login avec email/mot de passe valide\n- Redirection vers le dashboard après connexion\n- Message d'erreur si credentials invalides`}
          onChange={e => setForm(f => ({ ...f, specs: e.target.value }))}
          style={{ minHeight: 130, resize: 'vertical', fontFamily: 'var(--font-mono)', fontSize: 12, lineHeight: 1.6 }}
        />
        <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
          Décrivez en Markdown ce que doit faire chaque test. L'IA lira ces instructions pour générer les assertions.
        </p>
      </div>
    </div>,

    // ── Step 1 — Provider + Options ───────────────────────────────────────────
    <div key={1} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <label style={labelStyle}>Moteur LLM *</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[
            { value: 'groq',   label: 'Groq Cloud',   icon: '☁️', sub: 'Rapide · Clé API requise' },
            { value: 'ollama', label: 'Ollama Local',  icon: '🖥️', sub: 'Gratuit · Sans clé · Doit être lancé' },
          ].map(opt => (
            <div key={opt.value} onClick={() => setForm(f => ({ ...f, provider: opt.value }))}
              style={{
                padding: '12px 14px', borderRadius: 'var(--radius-md)', cursor: 'pointer',
                border: `1.5px solid ${form.provider === opt.value ? 'var(--color-brand)' : 'var(--border)'}`,
                background: form.provider === opt.value ? 'var(--bg-active)' : 'var(--bg-overlay)',
                transition: 'all 150ms ease',
                boxShadow: form.provider === opt.value ? 'var(--shadow-glow-brand)' : 'none',
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
          <label style={labelStyle}>Clé API Groq *</label>
          <div style={{ position: 'relative' }}>
            <svg width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth={1.8}
              strokeLinecap="round" strokeLinejoin="round"
              style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}>
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
            </svg>
            <input className="input-base" type="password" value={form.groqApiKey}
              placeholder="gsk_••••••••••••••••••••••••••••••••"
              onChange={e => setForm(f => ({ ...f, groqApiKey: e.target.value }))}
              style={{ paddingLeft: 30 }} />
          </div>
          <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
            Obtenez votre clé sur{' '}
            <span style={{ color: 'var(--color-brand)', cursor: 'pointer' }}
              onClick={() => window.open('https://console.groq.com', '_blank')}>
              console.groq.com
            </span>
            {' '}→ API Keys → Create.
          </p>
        </div>
      )}

      {form.provider === 'ollama' && (
        <div style={{ padding: '12px 14px', borderRadius: 'var(--radius-md)', background: 'rgba(34,197,94,0.07)', border: '1px solid rgba(34,197,94,0.2)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#22c55e', marginBottom: 4 }}>Ollama — aucune clé requise</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.6 }}>
            Assurez-vous qu'Ollama est démarré sur{' '}
            <code style={{ background: 'var(--bg-overlay)', padding: '1px 5px', borderRadius: 4 }}>http://localhost:11434</code>
            {' '}avec le modèle <code style={{ background: 'var(--bg-overlay)', padding: '1px 5px', borderRadius: 4 }}>llama3.2</code> :<br />
            <code style={{ background: 'var(--bg-overlay)', padding: '2px 6px', borderRadius: 4, marginTop: 4, display: 'inline-block' }}>ollama run llama3.2</code>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', background: 'var(--bg-overlay)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 500 }}>Mode Headless</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>Exécuter sans afficher le navigateur</div>
        </div>
        <div onClick={() => setForm(f => ({ ...f, headless: !f.headless }))} style={{
          width: 40, height: 22, borderRadius: 11, cursor: 'pointer',
          background: form.headless ? 'var(--color-brand)' : 'var(--border)',
          position: 'relative', transition: 'background 200ms ease',
          boxShadow: form.headless ? 'var(--shadow-glow-brand)' : 'none',
        }}>
          <div style={{
            position: 'absolute', top: 3,
            left: form.headless ? 21 : 3,
            width: 16, height: 16, borderRadius: '50%', background: '#fff',
            transition: 'left 200ms ease',
          }} />
        </div>
      </div>

      <div className="glass-card" style={{ padding: 14, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.7 }}>
        <strong style={{ color: 'var(--text-secondary)' }}>Ce qui se passe :</strong><br />
        1. L'IA analyse votre URL et vos specs<br />
        2. Groq (Llama 3) génère les cas de test<br />
        3. Un script Selenium Python complet est produit<br />
        4. Le résultat apparaît dans votre historique
      </div>
    </div>,

    // ── Step 2 — Confirmation / Progress ─────────────────────────────────────
    <div key={2} style={{ textAlign: 'center', padding: '20px 0' }}>
      {generating ? (
        <div>
          <div style={{
            width: 64, height: 64, borderRadius: '50%',
            background: 'var(--color-ai-muted)', border: '2px solid rgba(168,85,247,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px', animation: 'ai-pulse 1.5s ease-in-out infinite',
          }}>
            <svg width={26} height={26} viewBox="0 0 24 24" fill="none"
              stroke="var(--color-ai)" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"
              style={{ animation: 'spin-slow 1.5s linear infinite' }}>
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 6 }}>L'agent IA travaille…</div>
          <div style={{ fontSize: 12, color: 'var(--color-ai)', marginBottom: 4, minHeight: 18 }}>{progressLabel}</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 16 }}>
            {Math.floor(elapsedSec / 60) > 0 && `${Math.floor(elapsedSec / 60)}min `}
            {elapsedSec % 60}s écoulées
          </div>
          <div style={{ height: 6, borderRadius: 3, background: 'var(--bg-overlay)', overflow: 'hidden', margin: '0 20px' }}>
            <div style={{
              height: '100%', width: `${progressPct}%`,
              background: 'linear-gradient(90deg, var(--color-brand), var(--color-ai))',
              borderRadius: 3, transition: 'width 0.6s ease',
              boxShadow: '0 0 10px rgba(34,211,238,0.4)',
            }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', margin: '8px 20px 0', fontSize: 9, color: 'var(--text-muted)' }}>
            {['Specs', 'Groq', 'DOM Scan', 'Scripts', 'Tests', 'Rapport'].map(l => <span key={l}>{l}</span>)}
          </div>
        </div>
      ) : (
        <div>
          <div style={{ fontSize: 36, marginBottom: 16 }}>🚀</div>
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Prêt à générer</h3>
          <div className="glass-card" style={{ padding: 16, marginBottom: 20, textAlign: 'left' }}>
            {[
              ['URL',     form.url || '—'],
              ['Specs',   `${form.specs.trim().split('\n').length} ligne(s)`],
              ['Provider', form.provider === 'groq' ? 'Groq Cloud' : 'Ollama Local'],
              ['Headless', form.headless ? 'Oui' : 'Non'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-muted)', fontSize: 12 }}>
                <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                <span style={{ fontWeight: 500, fontFamily: k === 'URL' ? 'var(--font-mono)' : 'inherit', fontSize: k === 'URL' ? 11 : 12 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>,
  ];

  return (
    <Modal
      isOpen={open}
      onClose={generating ? undefined : handleClose}
      title={generating ? null : `Nouveau Test — Étape ${step + 1}/${STEPS.length}`}
      size="md"
      footer={generating ? null : (
        <>
          <button className="btn btn-ghost" onClick={() => step === 0 ? handleClose() : setStep(s => s - 1)}>
            {step === 0 ? 'Annuler' : '← Retour'}
          </button>
          {step < STEPS.length - 1 ? (
            <button className="btn btn-primary"
              onClick={() => setStep(s => s + 1)}
              disabled={(step === 0 && !step0Valid) || (step === 1 && !step1Valid)}
              style={{ opacity: ((step === 0 && !step0Valid) || (step === 1 && !step1Valid)) ? 0.5 : 1 }}>
              Suivant →
            </button>
          ) : (
            <button className="btn btn-ai" onClick={handleLaunch}>
              🤖 Lancer le test
            </button>
          )}
        </>
      )}
    >
      {!generating && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
          {STEPS.map((_, i) => (
            <div key={i} style={{
              flex: 1, height: 3, borderRadius: 2,
              background: i <= step ? 'var(--color-brand)' : 'var(--border)',
              transition: 'background 300ms ease',
              boxShadow: i <= step ? '0 0 6px rgba(34,211,238,0.4)' : 'none',
            }} />
          ))}
        </div>
      )}
      {stepContent[step]}
    </Modal>
  );
}

const labelStyle = {
  fontSize: 11, color: 'var(--text-muted)', display: 'block',
  marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em',
};
