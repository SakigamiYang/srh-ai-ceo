CREATE TABLE trading_economics_news (
    id BIGINT PRIMARY KEY,

    url TEXT NOT NULL,

    -- Basic metadata
    title TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,

    -- Article content
    description TEXT,
    content TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_trading_economics_news_id
    ON trading_economics_news (id);

CREATE INDEX idx_trading_economics_news_published_at
    ON trading_economics_news (published_at);