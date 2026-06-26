from ai_ceo.retrieval.load_bm25 import load_bm25
from ai_ceo.retrieval.tokenization import preprocess_text, lemmatize

__all__ = ["bm25_search"]


bm25, doc_ids = load_bm25()


def bm25_search(query, top_k=10):

    tokens = lemmatize(' '.join(preprocess_text(query)))

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        zip(doc_ids, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]