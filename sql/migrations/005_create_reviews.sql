CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,

    source TEXT NOT NULL,
    source_id TEXT NOT NULL,

    url TEXT,
    product_name TEXT,

    content TEXT NOT NULL,

    sentiment INTEGER NOT NULL,  -- 1 = positive, 0 = negative
    tag TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE (source, source_id, content)
);

CREATE INDEX idx_reviews_sentiment
    ON reviews (sentiment);