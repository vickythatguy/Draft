export const SENTIMENTS = ['love', 'like', 'meh', 'dislike', 'cringe'] as const;
export type Sentiment = (typeof SENTIMENTS)[number];

export type SentimentShares = Record<Sentiment, number>;

export interface SegmentRow {
  segment: string;
  n: number;
  sentiment: SentimentShares;
  share_rate: number;
  skip_rate: number;
  watch_full_rate: number;
  engage_rate: number;
}

export interface Quote {
  quote: string;
  why: string;
  sentiment: Sentiment;
  action: string;
  persona: {
    age: number;
    gender: string;
    neighbourhood: string;
    occupation: string;
    background: string;
  };
}

export interface RunResult {
  meta: { n: number; mode: string; model: string; content: string };
  sentiment: SentimentShares;
  avg_score: number;
  rates: { share: number; skip: number; watch_full: number; engage: number };
  segments: {
    age: SegmentRow[];
    income: SegmentRow[];
    neighbourhood: SegmentRow[];
  };
  quotes: Quote[];
}

export const SENTIMENT_COLOR: Record<Sentiment, string> = {
  love: 'var(--sent-love)',
  like: 'var(--sent-like)',
  meh: 'var(--sent-meh)',
  dislike: 'var(--sent-dislike)',
  cringe: 'var(--sent-cringe)',
};

export const SENTIMENT_LABEL: Record<Sentiment, string> = {
  love: 'Love it',
  like: 'Like it',
  meh: 'Meh',
  dislike: 'Dislike',
  cringe: 'Cringe',
};
