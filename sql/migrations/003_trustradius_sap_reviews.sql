CREATE TABLE trustradius_sap_reviews (
    id BIGSERIAL PRIMARY KEY,

    review_url TEXT NOT NULL UNIQUE,

    title TEXT NOT NULL,
    reviewer_name TEXT,
    published_at TIMESTAMP,

    pros TEXT,
    cons TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trustradius_sap_reviews_published_at
    ON trustradius_sap_reviews (published_at);