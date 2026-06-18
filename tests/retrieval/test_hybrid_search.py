import chromadb

from ai_ceo.retrieval.bm25_search import bm25_search
from ai_ceo.retrieval.hybrid_search import hybrid_search
from ai_ceo.retrieval.utils import encode_query

client = chromadb.HttpClient(host="localhost", port=8000)
document_collection = client.get_collection("documents_chunks")
review_collection = client.get_collection("reviews")

def run_query(query: str):

    # 3️⃣ 生成 query embedding（关键）
    query_embedding = encode_query([query])

    # 4️⃣ hybrid search
    results = hybrid_search(
        query=query,
        query_embedding=query_embedding,
        bm25_search=bm25_search,
        document_collection=document_collection,
        review_collection=review_collection,
        top_k=5
    )

    return results


if __name__ == "__main__":
    from pprint import pp

    res = run_query("SAP AI strategy")
    pp(res)
