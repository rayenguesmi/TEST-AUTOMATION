import { useEffect, useState } from 'react';

/**
 * Skeleton — Exact-dimension shimmer placeholder for each data component
 * Components: KPICard, TableRow, TestCard, ProjectCard, LogLine, HealthCard
 */

const shimmerStyle = {
  background: 'linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.09) 50%, rgba(255,255,255,0.04) 75%)',
  backgroundSize: '1000px 100%',
  animation: 'shimmer 1.8s infinite linear',
  borderRadius: 'var(--radius-md)',
};

// Delay render to avoid flash on fast requests
function DelayedRender({ delay = 200, children }) {
  const [show, setShow] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setShow(true), delay);
    return () => clearTimeout(t);
  }, [delay]);
  return show ? children : null;
}

// ─── KPI Card Skeleton ────────────────────────────────────────────────────────
export function KPICardSkeleton() {
  return (
    <DelayedRender>
      <div style={{ padding: 20, background: 'var(--bg-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ ...shimmerStyle, width: 100, height: 12 }} />
          <div style={{ ...shimmerStyle, width: 32, height: 32, borderRadius: 8 }} />
        </div>
        <div style={{ ...shimmerStyle, width: 80, height: 28, marginBottom: 8 }} />
        <div style={{ ...shimmerStyle, width: 60, height: 10 }} />
        <div style={{ ...shimmerStyle, width: '100%', height: 40, marginTop: 16, borderRadius: 4 }} />
      </div>
    </DelayedRender>
  );
}

// ─── Table Row Skeleton ────────────────────────────────────────────────────────
export function TableRowSkeleton({ cols = 6 }) {
  return (
    <DelayedRender>
      <tr style={{ borderBottom: '1px solid var(--border)' }}>
        {Array.from({ length: cols }).map((_, i) => (
          <td key={i} style={{ padding: '14px 16px' }}>
            <div style={{ ...shimmerStyle, width: i === 0 ? 140 : i === cols - 1 ? 80 : 100, height: 12 }} />
          </td>
        ))}
      </tr>
    </DelayedRender>
  );
}

// ─── Test Card Skeleton ──────────────────────────────────────────────────────
export function TestCardSkeleton() {
  return (
    <DelayedRender>
      <div style={{ padding: '14px 16px', background: 'var(--bg-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ ...shimmerStyle, width: 36, height: 36, borderRadius: 8, flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <div style={{ ...shimmerStyle, width: '60%', height: 12, marginBottom: 8 }} />
          <div style={{ ...shimmerStyle, width: '40%', height: 10 }} />
        </div>
        <div style={{ ...shimmerStyle, width: 60, height: 22, borderRadius: 99 }} />
        <div style={{ ...shimmerStyle, width: 80, height: 10 }} />
      </div>
    </DelayedRender>
  );
}

// ─── Project Card Skeleton ───────────────────────────────────────────────────
export function ProjectCardSkeleton() {
  return (
    <DelayedRender>
      <div style={{ padding: 20, background: 'var(--bg-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <div style={{ ...shimmerStyle, width: 40, height: 40, borderRadius: 10 }} />
          <div style={{ flex: 1 }}>
            <div style={{ ...shimmerStyle, width: '70%', height: 12, marginBottom: 6 }} />
            <div style={{ ...shimmerStyle, width: '40%', height: 10 }} />
          </div>
        </div>
        <div style={{ ...shimmerStyle, width: '100%', height: 6, borderRadius: 3 }} />
      </div>
    </DelayedRender>
  );
}

// ─── Log Line Skeleton ────────────────────────────────────────────────────────
export function LogLineSkeleton({ count = 5 }) {
  return (
    <DelayedRender>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} style={{ display: 'flex', gap: 12, padding: '6px 16px', alignItems: 'center' }}>
          <div style={{ ...shimmerStyle, width: 40, height: 10, borderRadius: 4 }} />
          <div style={{ ...shimmerStyle, width: `${40 + (i % 4) * 10}%`, height: 10 }} />
        </div>
      ))}
    </DelayedRender>
  );
}

// ─── Health Card Skeleton ─────────────────────────────────────────────────────
export function HealthCardSkeleton() {
  return (
    <DelayedRender>
      <div style={{ padding: 20, background: 'var(--bg-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <div style={{ ...shimmerStyle, width: 80, height: 12 }} />
          <div style={{ ...shimmerStyle, width: 60, height: 22, borderRadius: 99 }} />
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <div style={{ ...shimmerStyle, width: '50%', height: 10, marginBottom: 4 }} />
            <div style={{ ...shimmerStyle, width: '70%', height: 18 }} />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ ...shimmerStyle, width: '50%', height: 10, marginBottom: 4 }} />
            <div style={{ ...shimmerStyle, width: '60%', height: 18 }} />
          </div>
        </div>
      </div>
    </DelayedRender>
  );
}

// ─── Generic Skeleton ─────────────────────────────────────────────────────────
export function Skeleton({ width = '100%', height = 16, radius = 'var(--radius-md)', delay = 0, style = {} }) {
  return (
    <DelayedRender delay={delay}>
      <div style={{ ...shimmerStyle, width, height, borderRadius: radius, ...style }} />
    </DelayedRender>
  );
}

export default Skeleton;
