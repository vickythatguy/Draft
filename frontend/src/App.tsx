import { useEffect, useState } from 'react';
import { health, runAudience } from './lib/api';
import type { RunResult } from './types';
import StatTiles from './components/StatTiles';
import SentimentStack from './components/SentimentStack';
import RateBars from './components/RateBars';
import Quotes from './components/Quotes';

const PLACEHOLDER =
  "e.g. 30-second TikTok skit: a raccoon 'inspects' a new condo while a deadpan " +
  'realtor lists its features; punchline about Toronto rent prices. Light branding ' +
  'for a rental-listings app in the last 3 seconds.';

export default function App() {
  const [content, setContent] = useState('');
  const [size, setSize] = useState(500);
  const [mode, setMode] = useState<'auto' | 'mock' | 'live'>('auto');
  const [liveAvailable, setLiveAvailable] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RunResult | null>(null);

  useEffect(() => {
    health()
      .then((h) => setLiveAvailable(h.live_available))
      .catch(() => setLiveAvailable(null));
  }, []);

  async function onRun() {
    setLoading(true);
    setError(null);
    try {
      setResult(await runAudience({ content, audience_size: size, seed: 42, mode }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Synthetic Audience · Toronto</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
          Test a Reel, TikTok, Short or ad against a census-grounded synthetic
          Toronto audience before you publish.{' '}
          {liveAvailable === false && (
            <span style={{ color: 'var(--text-muted)' }}>
              (running in offline mock mode — set ANTHROPIC_API_KEY on the backend for live reactions)
            </span>
          )}
        </p>
      </header>

      <div className="card p-4 mb-6">
        <label className="text-sm font-semibold block mb-2" htmlFor="content">
          Describe the content
        </label>
        <textarea
          id="content"
          className="w-full rounded-lg p-3 text-sm min-h-[96px]"
          style={{ background: 'var(--page)', border: '1px solid var(--grid)', color: 'var(--text-primary)' }}
          placeholder={PLACEHOLDER}
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <div className="flex flex-wrap items-center gap-3 mt-3">
          <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
            Audience size
            <select
              className="rounded-md px-2 py-1 text-sm"
              style={{ background: 'var(--page)', border: '1px solid var(--grid)', color: 'var(--text-primary)' }}
              value={size}
              onChange={(e) => setSize(Number(e.target.value))}
            >
              {[100, 250, 500, 1000, 2000].map((n) => (
                <option key={n} value={n}>{n.toLocaleString()} agents</option>
              ))}
            </select>
          </label>
          <label className="text-xs flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
            Engine
            <select
              className="rounded-md px-2 py-1 text-sm"
              style={{ background: 'var(--page)', border: '1px solid var(--grid)', color: 'var(--text-primary)' }}
              value={mode}
              onChange={(e) => setMode(e.target.value as 'auto' | 'mock' | 'live')}
            >
              <option value="auto">auto (live if key set)</option>
              <option value="mock">mock (free, offline)</option>
              <option value="live">live (Claude Haiku)</option>
            </select>
          </label>
          <button
            className="ml-auto px-5 py-2 rounded-lg text-sm font-semibold text-white disabled:opacity-50"
            style={{ background: 'var(--accent)' }}
            disabled={loading || content.trim().length < 10}
            onClick={onRun}
          >
            {loading ? 'Running audience…' : 'Run audience'}
          </button>
        </div>
        {error && (
          <p className="text-sm mt-3" style={{ color: 'var(--sent-cringe)' }}>
            {error}
          </p>
        )}
      </div>

      {result && (
        <div className="space-y-4">
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {result.meta.n.toLocaleString()} agents · engine: {result.meta.mode}
            {result.meta.mode !== 'mock' && ` (${result.meta.model})`}
          </p>
          <StatTiles result={result} />
          <SentimentStack
            title="Overall sentiment"
            rows={[{ name: 'All agents', n: result.meta.n, sentiment: result.sentiment }]}
          />
          <div className="grid lg:grid-cols-2 gap-4">
            <SentimentStack
              title="Sentiment by age"
              rows={result.segments.age.map((r) => ({ name: r.segment, n: r.n, sentiment: r.sentiment }))}
            />
            <RateBars title="Share vs skip by age" rows={result.segments.age} />
            <SentimentStack
              title="Sentiment by household income"
              rows={result.segments.income.map((r) => ({ name: r.segment, n: r.n, sentiment: r.sentiment }))}
            />
            <SentimentStack
              title="Sentiment by neighbourhood area"
              rows={result.segments.neighbourhood.map((r) => ({ name: r.segment, n: r.n, sentiment: r.sentiment }))}
            />
          </div>
          <Quotes quotes={result.quotes} />
          <footer className="text-xs pb-8" style={{ color: 'var(--text-muted)' }}>
            Synthetic pre-filter, not a replacement for real testing — validate winners
            with a small human panel (see backend/validation).
          </footer>
        </div>
      )}
    </div>
  );
}
