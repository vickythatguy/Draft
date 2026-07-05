import type { RunResult } from '../types';

function pct(v: number) {
  return `${(v * 100).toFixed(1)}%`;
}

export default function StatTiles({ result }: { result: RunResult }) {
  const positive = result.sentiment.love + result.sentiment.like;
  const tiles = [
    { label: 'Predicted share rate', value: pct(result.rates.share), sub: 'agents who would repost / send it' },
    { label: 'Predicted skip rate', value: pct(result.rates.skip), sub: 'scrolled past without watching' },
    { label: 'Positive sentiment', value: pct(positive), sub: 'love + like' },
    {
      label: 'Net score',
      value: (result.avg_score >= 0 ? '+' : '') + result.avg_score.toFixed(2),
      sub: '−2 all cringe · +2 all love',
    },
  ];
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {tiles.map((t) => (
        <div key={t.label} className="card p-4">
          <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {t.label}
          </div>
          <div className="text-3xl font-semibold mt-1">{t.value}</div>
          <div className="text-xs mt-1" style={{ color: 'var(--text-secondary)' }}>
            {t.sub}
          </div>
        </div>
      ))}
    </div>
  );
}
