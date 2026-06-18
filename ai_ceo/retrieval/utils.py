from sentence_transformers import SentenceTransformer
from constants import PROJECT_ROOT

__all__ = ["encode_query", "encode_document"]

model = SentenceTransformer(str(PROJECT_ROOT / "models" / "BAAI__bge-small-en-v1.5"))


def encode_query(texts):
    return model.encode_query(texts).tolist()


def encode_document(texts):
    return model.encode_document(texts).tolist()