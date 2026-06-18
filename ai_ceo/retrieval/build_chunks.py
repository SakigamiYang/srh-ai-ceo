import hashlib
import re

from loguru import logger
from sqlalchemy import create_engine, text


DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"

engine = create_engine(DATABASE_URL)


CHUNK_SIZE = 300
OVERLAP = 100


INSERT_CHUNK = text("""
INSERT INTO document_chunks (
    document_id,
    chunk_index,
    content,
    content_hash
)
VALUES (
    :doc_id,
    :idx,
    :content,
    :hash
)
ON CONFLICT (document_id, chunk_index)
DO UPDATE SET
    content = EXCLUDED.content
""")


def clean(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        chunks.append(chunk)

        start += CHUNK_SIZE - OVERLAP

    return chunks


def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def main():

    with engine.begin() as conn:

        conn.execute(text("""
            DELETE FROM document_chunks
        """))

        rows = conn.execute(text("""
            SELECT id, title, body FROM documents
        """)).mappings()

        for r in rows:

            full_text = clean(f"{r['title']}\n\n{r['body']}")

            chunks = split_text(full_text)

            for i, chunk in enumerate(chunks):

                conn.execute(
                    INSERT_CHUNK,
                    {
                        "doc_id": r["id"],
                        "idx": i,
                        "content": chunk,
                        "hash": hash_text(chunk),
                    },
                )

        logger.info("chunks done")


if __name__ == "__main__":
    main()