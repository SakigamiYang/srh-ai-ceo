CREATE TABLE erp_today_news (
    id BIGSERIAL PRIMARY KEY,

    url TEXT NOT NULL UNIQUE,

    title TEXT NOT NULL,
    author TEXT,
    published_at TIMESTAMP,

    summary TEXT,
    content TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_erp_today_news_published_at
    ON erp_today_news (published_at);