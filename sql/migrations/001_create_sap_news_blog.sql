CREATE TABLE sap_news_blog (
    id              BIGSERIAL PRIMARY KEY,

    -- Article URL
    url             TEXT NOT NULL UNIQUE,

    -- Article metadata
    title           TEXT NOT NULL,
    author          TEXT,
    published_at    DATE,

    -- Crawling information
    page_number     INTEGER NOT NULL,

    -- Filled when the detail page is crawled
    content         TEXT,

    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sap_news_blog_published_at
ON sap_news_blog (published_at);