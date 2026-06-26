import chromadb
from loguru import logger
from sqlalchemy import create_engine, text

from ai_ceo.retrieval.utils import encode_document

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
engine = create_engine(DATABASE_URL)

client = chromadb.HttpClient(host="localhost", port=8000)
client.delete_collection("documents_chunks")
collection = client.get_or_create_collection("documents_chunks")


def main():

    with engine.begin() as conn:

        rows = conn.execute(text("""
            SELECT id, content FROM document_chunks
        """)).mappings()

        for r in rows:

            logger.info(f"embedding document id={r['id']}")

            collection.upsert(
                ids=[f"d_{r['id']}"],
                documents=[r["content"]],
                embeddings=encode_document(r["content"]),
                metadatas=[{
                    "chunk_id": r["id"]
                }]
            )

    logger.info(f"collection count: {collection.count()}")


if __name__ == "__main__":
    main()