-- Enable pg_stat_statements for query analysis
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Users (authentication)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sectors
CREATE TABLE IF NOT EXISTS sectors (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Companies (S&P 500 universe)
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    sector_id INTEGER REFERENCES sectors(id) ON DELETE SET NULL,
    added_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_companies_ticker ON companies(ticker);

-- News headlines (for sentiment inputs)
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    source TEXT,
    headline TEXT,
    url TEXT,
    published_at TIMESTAMPTZ,
    ts tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(headline,''))) STORED
);
CREATE INDEX IF NOT EXISTS idx_news_company_time ON news(company_id, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_fts ON news USING GIN (ts);

-- Sentiment scores (aggregated or per-headline)
CREATE TABLE IF NOT EXISTS sentiments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    headline_id INTEGER REFERENCES news(id) ON DELETE SET NULL,
    source TEXT,
    score NUMERIC,          -- VADER compound or other normalized score
    magnitude NUMERIC,      -- optional
    computed_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sentiments_company_time ON sentiments(company_id, computed_at DESC);

-- Helpful materialized view for latest company-level sentiment
DROP MATERIALIZED VIEW IF EXISTS company_latest_sentiment;
CREATE MATERIALIZED VIEW company_latest_sentiment AS
SELECT s.company_id,
       c.ticker,
       c.name,
       MAX(s.computed_at) AS latest_at,
       AVG(s.score) FILTER (WHERE s.computed_at > NOW() - INTERVAL '7 days') AS avg7d,
       AVG(s.score) AS avg_all
FROM sentiments s
JOIN companies c ON c.id = s.company_id
GROUP BY s.company_id, c.ticker, c.name;

CREATE INDEX IF NOT EXISTS idx_cls_company ON company_latest_sentiment(company_id);

-- Example role for app (optional; can be configured at container init)
-- CREATE USER appuser WITH PASSWORD 'apppass';
-- GRANT ALL PRIVILEGES ON DATABASE marketview TO appuser;
