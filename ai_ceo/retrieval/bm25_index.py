import pickle

from loguru import logger
from rank_bm25 import BM25Okapi
from sqlalchemy import create_engine, text

from ai_ceo.constants import PROJECT_ROOT


DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
engine = create_engine(DATABASE_URL)

BM25_PATH = PROJECT_ROOT / "data" / "db" / "bm25.pkl"


def main():

    docs = []
    doc_ids = []

    with engine.begin() as conn:

        rows = conn.execute(text("""
            SELECT id, content FROM document_chunks
        """)).mappings()

        for r in rows:

            tokens = r["content"].split()

            docs.append(tokens)
            doc_ids.append(r["id"])

    bm25 = BM25Okapi(docs)

    with open(BM25_PATH, "wb") as f:
        pickle.dump({
            "bm25": bm25,
            "doc_ids": doc_ids
        }, f)

    logger.info("BM25 saved: {}", BM25_PATH)


if __name__ == '__main__':
    main()