import { SENTIMENT_COLOR, SENTIMENT_LABEL, type Quote } from '../types';

export default function Quotes({ quotes }: { quotes: Quote[] }) {
  return (
    <div className="card p-4">
      <h3 className="text-sm font-semibold mb-3">Representative verbatims</h3>
      <div className="grid md:grid-cols-2 gap-3">
        {quotes.map((q, i) => (
          <div key={i} className="rounded-lg p-3" style={{ border: '1px solid var(--grid)' }}>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className="text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded"
                style={{
                  background: SENTIMENT_COLOR[q.sentiment],
                  color: q.sentiment === 'meh' || q.sentiment === 'like' ? 'var(--text-primary)' : '#fff',
                }}
              >
                {SENTIMENT_LABEL[q.sentiment]}
              </span>
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                {q.action.replace('_', ' ')}
              </span>
            </div>
            <p className="text-sm leading-snug">“{q.quote}”</p>
            <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>
              {q.persona.age}, {q.persona.gender} · {q.persona.neighbourhood} ·{' '}
              {q.persona.occupation} · {q.why}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
