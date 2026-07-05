import {
  Bar,
  BarChart,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  SENTIMENTS,
  SENTIMENT_COLOR,
  SENTIMENT_LABEL,
  type Sentiment,
  type SentimentShares,
} from '../types';

export interface StackRow {
  name: string;
  n: number;
  sentiment: SentimentShares;
}

function Legend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
      {SENTIMENTS.map((s) => (
        <span key={s} className="inline-flex items-center gap-1.5">
          <span
            className="inline-block w-2.5 h-2.5 rounded-sm"
            style={{ background: SENTIMENT_COLOR[s] }}
          />
          {SENTIMENT_LABEL[s]}
        </span>
      ))}
    </div>
  );
}

function StackTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="card p-3 text-xs shadow-lg" style={{ color: 'var(--text-primary)' }}>
      <div className="font-semibold mb-1">{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-sm" style={{ background: p.fill }} />
          <span style={{ color: 'var(--text-secondary)' }}>
            {SENTIMENT_LABEL[p.dataKey as Sentiment]}
          </span>
          <span className="ml-auto font-medium">{(p.value * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  );
}

/** Horizontal 100%-stacked sentiment bars (one row per segment). */
export default function SentimentStack({ rows, title }: { rows: StackRow[]; title: string }) {
  const data = rows.map((r) => ({ name: r.name, n: r.n, ...r.sentiment }));
  const height = Math.max(64, rows.length * 44 + 24);
  return (
    <div className="card p-4">
      <div className="flex items-baseline justify-between mb-2">
        <h3 className="text-sm font-semibold">{title}</h3>
        <Legend />
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 8, bottom: 0, left: 8 }}>
          <XAxis type="number" domain={[0, 1]} hide />
          <YAxis
            type="category"
            dataKey="name"
            width={150}
            tickLine={false}
            axisLine={false}
            tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
          />
          <Tooltip content={<StackTooltip />} cursor={{ fill: 'transparent' }} />
          {SENTIMENTS.map((s, i) => (
            <Bar
              key={s}
              dataKey={s}
              stackId="sent"
              fill={SENTIMENT_COLOR[s]}
              stroke="var(--surface-1)"
              strokeWidth={2}
              radius={i === SENTIMENTS.length - 1 ? [0, 4, 4, 0] : 0}
              barSize={22}
              isAnimationActive={false}
            >
              {/* Direct labels only where the segment is wide enough to read. */}
              <LabelList
                dataKey={s}
                position="center"
                formatter={(v: number) => (v >= 0.09 ? `${Math.round(v * 100)}%` : '')}
                style={{
                  fill: s === 'meh' || s === 'like' ? 'var(--text-primary)' : '#ffffff',
                  fontSize: 11,
                }}
              />
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
      <details className="mt-2">
        <summary className="text-xs cursor-pointer" style={{ color: 'var(--text-muted)' }}>
          View as table
        </summary>
        <table className="w-full text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
          <thead>
            <tr className="text-left">
              <th className="py-1 pr-2 font-medium">Segment</th>
              <th className="py-1 pr-2 font-medium">n</th>
              {SENTIMENTS.map((s) => (
                <th key={s} className="py-1 pr-2 font-medium">{SENTIMENT_LABEL[s]}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name} style={{ borderTop: '1px solid var(--grid)' }}>
                <td className="py-1 pr-2">{r.name}</td>
                <td className="py-1 pr-2 tabular-nums">{r.n}</td>
                {SENTIMENTS.map((s) => (
                  <td key={s} className="py-1 pr-2 tabular-nums">
                    {(r.sentiment[s] * 100).toFixed(1)}%
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
