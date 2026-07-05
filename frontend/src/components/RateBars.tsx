import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SegmentRow } from '../types';

function RateTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="card p-3 text-xs shadow-lg" style={{ color: 'var(--text-primary)' }}>
      <div className="font-semibold mb-1">{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-sm" style={{ background: p.fill }} />
          <span style={{ color: 'var(--text-secondary)' }}>
            {p.dataKey === 'share_rate' ? 'Would share' : 'Would skip'}
          </span>
          <span className="ml-auto font-medium">{(p.value * 100).toFixed(1)}%</span>
        </div>
      ))}
    </div>
  );
}

/** Share vs skip rate per segment — grouped vertical bars, one shared axis. */
export default function RateBars({ rows, title }: { rows: SegmentRow[]; title: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-baseline justify-between mb-2">
        <h3 className="text-sm font-semibold">{title}</h3>
        <div className="flex gap-4 text-xs" style={{ color: 'var(--text-secondary)' }}>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ background: 'var(--rate-share)' }} />
            Would share
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block w-2.5 h-2.5 rounded-sm" style={{ background: 'var(--rate-skip)' }} />
            Would skip
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={rows} margin={{ top: 4, right: 8, bottom: 0, left: -16 }}>
          <CartesianGrid vertical={false} stroke="var(--grid)" />
          <XAxis
            dataKey="segment"
            tickLine={false}
            axisLine={{ stroke: 'var(--baseline)' }}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            interval={0}
          />
          <YAxis
            tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
            tickLine={false}
            axisLine={false}
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
          />
          <Tooltip content={<RateTooltip />} cursor={{ fill: 'var(--grid)', opacity: 0.4 }} />
          <Bar dataKey="share_rate" fill="var(--rate-share)" radius={[4, 4, 0, 0]} barSize={18} isAnimationActive={false} />
          <Bar dataKey="skip_rate" fill="var(--rate-skip)" radius={[4, 4, 0, 0]} barSize={18} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
