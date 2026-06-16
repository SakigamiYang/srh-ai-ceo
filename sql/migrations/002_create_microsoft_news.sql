CREATE TABLE microsoft_news (
    id BIGSERIAL PRIMARY KEY,

    -- Unique identifier
    url TEXT NOT NULL UNIQUE,

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

CREATE INDEX idx_microsoft_news_published_at
    ON microsoft_news (published_at);