CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,

    source TEXT NOT NULL,
    source_id TEXT NOT NULL,

    url TEXT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    author TEXT,
    published_at TIMESTAMP,

    content_hash TEXT NOT NULL,

    metadata JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE (source, source_id)
);

CREATE INDEX idx_documents_source
    ON documents (source);

CREATE INDEX idx_documents_published_at
    ON documents (published_at);

CREATE INDEX idx_documents_content_hash
    ON documents (content_hash);