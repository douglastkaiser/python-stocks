import { useEffect, useRef, useState } from 'react';
import { money, percent, type Result } from './engine';
export function Chart({
  result,
  risk,
  onTrade,
}: {
  result: Result;
  risk: boolean;
  onTrade: (date: string) => void;
}) {
  const [hover, setHover] = useState<number | null>(null);
  const { points, trades } = result;
  const container = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(1000);
  useEffect(() => {
    const observer = new ResizeObserver((entries) =>
      setWidth(Math.max(320, entries[0].contentRect.width)),
    );
    if (container.current) observer.observe(container.current);
    return () => observer.disconnect();
  }, []);
  const W = width,
    H = width < 500 ? 250 : 330,
    left = 54,
    right = 26,
    top = 24,
    bottom = 42;
  const values = points.flatMap((p) =>
    risk ? [p.drawdown * 100, p.benchmarkDrawdown * 100] : [p.equity, p.benchmark],
  );
  const lo = Math.min(...values),
    hi = Math.max(...values),
    pad = (hi - lo || 1) * 0.15;
  const min = risk ? lo - pad : lo - pad,
    max = risk ? 0 : hi + pad;
  const x = (i: number) => left + (i / (points.length - 1)) * (W - left - right);
  const y = (v: number) => top + (1 - (v - min) / (max - min || 1)) * (H - top - bottom);
  const path = (benchmark: boolean) =>
    points
      .map(
        (p, i) =>
          `${i ? 'L' : 'M'}${x(i).toFixed(2)},${y(risk ? (benchmark ? p.benchmarkDrawdown : p.drawdown) * 100 : benchmark ? p.benchmark : p.equity).toFixed(2)}`,
      )
      .join(' ');
  const focus = hover === null ? null : points[hover];
  return (
    <div className="chart-wrap" ref={container}>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        role="group"
        aria-label={
          risk
            ? 'Strategy and buy-and-hold drawdown over time'
            : 'Strategy and buy-and-hold portfolio value over time'
        }
        onMouseLeave={() => setHover(null)}
        onMouseMove={(event) => {
          const rect = event.currentTarget.getBoundingClientRect();
          setHover(
            Math.max(
              0,
              Math.min(
                points.length - 1,
                Math.round(
                  ((((event.clientX - rect.left) / rect.width) * W - left) / (W - left - right)) *
                    (points.length - 1),
                ),
              ),
            ),
          );
        }}
      >
        <defs>
          <pattern id="chart-fill" width="6" height="6" patternUnits="userSpaceOnUse">
            <path d="M0 6L6 0" stroke="var(--plot-strategy)" strokeWidth="0.6" opacity=".14" />
          </pattern>
        </defs>
        {Array.from({ length: 5 }, (_, i) => {
          const v = min + ((max - min) * i) / 4;
          return (
            <g key={i}>
              <line x1={left} x2={W - right} y1={y(v)} y2={y(v)} stroke="var(--plot-grid)" />
              <text x={left - 13} y={y(v) + 4} textAnchor="end" className="axis-label">
                {risk ? `${v.toFixed(0)}%` : `${(v / 1000).toFixed(1)}k`}
              </text>
            </g>
          );
        })}
        <path
          d={`${path(false)} L${x(points.length - 1)},${H - bottom} L${left},${H - bottom} Z`}
          fill="url(#chart-fill)"
        />
        <path
          d={path(true)}
          fill="none"
          stroke="var(--plot-benchmark)"
          strokeWidth="2"
          strokeDasharray="6 5"
        />
        <path
          d={path(false)}
          fill="none"
          stroke="var(--plot-strategy)"
          strokeWidth="2.2"
          strokeLinejoin="miter"
        />
        {Array.from({ length: 5 }, (_, i) => {
          const idx = Math.round((i * (points.length - 1)) / 4);
          return (
            <text key={i} x={x(idx)} y={H - 10} textAnchor="middle" className="axis-label">
              {new Date(points[idx].date + 'T12:00:00Z').toLocaleDateString('en-US', {
                month: 'short',
                year: 'numeric',
                timeZone: 'UTC',
              })}
            </text>
          );
        })}
        {!risk &&
          trades.map((t) => {
            const i = points.findIndex((p) => p.date === t.date);
            return (
              <g
                key={t.date}
                className="trade-marker"
                role="button"
                tabIndex={0}
                aria-label={`${t.side} on ${t.date}, view trade`}
                onClick={() => onTrade(t.date)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onTrade(t.date);
                  }
                }}
              >
                <title>
                  {t.side} · {t.date} · {money(t.equity)}
                </title>
                <circle cx={x(i)} cy={y(points[i].equity)} r="9" fill="transparent" />
                <circle
                  cx={x(i)}
                  cy={y(points[i].equity)}
                  r="4"
                  fill={t.side === 'Buy' ? 'var(--plot-strategy)' : 'var(--paper)'}
                  stroke="var(--plot-strategy)"
                  strokeWidth="2"
                />
              </g>
            );
          })}
        {focus && hover !== null && (
          <g pointerEvents="none">
            <line
              x1={x(hover)}
              x2={x(hover)}
              y1={top}
              y2={H - bottom}
              stroke="var(--ink)"
              strokeDasharray="3 4"
            />
            <circle
              cx={x(hover)}
              cy={y(risk ? focus.drawdown * 100 : focus.equity)}
              r="5"
              fill="var(--plot-strategy)"
              stroke="#fff"
              strokeWidth="2"
            />
          </g>
        )}
      </svg>
      <div className="chart-readout" aria-live="off">
        {focus ? (
          <>
            <strong>{focus.date}</strong>
            <span>Strategy {risk ? percent(focus.drawdown) : money(focus.equity)}</span>
            <span>
              Buy & hold {risk ? percent(focus.benchmarkDrawdown) : money(focus.benchmark)}
            </span>
          </>
        ) : (
          <span>
            Hover to explore ·{' '}
            {risk
              ? 'Drawdown measures decline from a previous peak'
              : 'Select a trade marker to inspect its execution'}
          </span>
        )}
      </div>
    </div>
  );
}
