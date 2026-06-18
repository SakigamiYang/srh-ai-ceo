import pickle

from constants import PROJECT_ROOT

__all__ = ["load_bm25"]

BM25_PATH = PROJECT_ROOT / "data" / "db" / "bm25.pkl"


def load_bm25():
    with open(BM25_PATH, "rb") as f:
        data = pickle.load(f)

    return data["bm25"], data["doc_ids"]
