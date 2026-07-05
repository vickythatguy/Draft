import type { RunResult } from '../types';

export interface RunParams {
  content: string;
  audience_size: number;
  seed: number;
  mode: 'auto' | 'mock' | 'live' | 'batch';
}

export async function runAudience(params: RunParams): Promise<RunResult> {
  const res = await fetch('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof body.detail === 'string' ? body.detail : res.statusText);
  }
  return res.json();
}

export async function health(): Promise<{ ok: boolean; live_available: boolean }> {
  const res = await fetch('/api/health');
  if (!res.ok) throw new Error('backend unreachable');
  return res.json();
}
