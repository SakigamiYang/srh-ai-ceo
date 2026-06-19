from sqlalchemy import create_engine, text

__all__ = ["hybrid_search"]

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
engine = create_engine(DATABASE_URL)


def fetch_documents_by_chunk_ids(chunk_ids):

    with engine.begin() as conn:

        rows = conn.execute(text("""
            SELECT DISTINCT d.*, c.content
            FROM document_chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.id = ANY(:ids)
        """), {"ids": chunk_ids}).mappings()

        results = []
        for r in rows:
            d = dict(r)
            del d["body"]
            results.append(r)
        return results


def fetch_reviews_by_ids(review_ids):

    with engine.begin() as conn:

        rows = conn.execute(text("""
            SELECT *
            FROM reviews
            WHERE id = ANY(:ids)
        """), {"ids": review_ids}).mappings()

        return [dict(r) for r in rows]


def hybrid_search(
    query,
    query_embedding,
    bm25_search,
    document_collection,
    review_collection,
    top_k=10
):

    # ---------- documents ----------
    bm25_results = bm25_search(query, top_k)

    vector_results = document_collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    doc_scores = {}

    # BM25
    for rank, (chunk_id, _) in enumerate(bm25_results):
        doc_scores[chunk_id] = doc_scores.get(chunk_id, 0) + 1 / (rank + 1)

    # Vector
    for rank, cid in enumerate(vector_results["ids"][0]):
        chunk_id = int(cid.split("_")[1])
        doc_scores[chunk_id] = doc_scores.get(chunk_id, 0) + 1 / (rank + 1)

    # 排序 chunk
    ranked_chunks = sorted(
        doc_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    chunk_ids = [cid for cid, _ in ranked_chunks]

    documents = fetch_documents_by_chunk_ids(chunk_ids)

    # ---------- reviews ----------
    review_results = review_collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    review_ids = [
        int(rid.split("_")[1])
        for rid in review_results["ids"][0]
    ]

    reviews = fetch_reviews_by_ids(review_ids)

    return {
        "documents": documents,
        "reviews": reviews
    }