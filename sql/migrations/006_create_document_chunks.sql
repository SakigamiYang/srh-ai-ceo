CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,

    content TEXT NOT NULL,

    content_hash TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_chunks_doc
    ON document_chunks (document_id);

CREATE INDEX idx_chunks_hash
    ON document_chunks (content_hash);