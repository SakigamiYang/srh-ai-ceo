import spacy

from gensim.parsing.preprocessing import (
    strip_tags,
    strip_punctuation,
    strip_numeric,
    strip_multiple_whitespaces,
    remove_stopwords,
    strip_short,
)

__all__ = ["preprocess_text"]

nlp = spacy.load(
    "en_core_web_sm",
    disable=["parser", "ner"]
)


def preprocess_text(text: str) -> list[str]:
    """
    Clean and lemmatize text for BM25.
    """

    if not text:
        return []

    text = text.lower()

    # gensim preprocessing
    text = strip_tags(text)
    text = strip_punctuation(text)
    text = strip_numeric(text)
    text = remove_stopwords(text)
    text = strip_short(text, minsize=2)
    text = strip_multiple_whitespaces(text)

    doc = nlp(text)

    tokens = [
        token.text
        for token in doc
        if not token.is_space
        and not token.is_punct
    ]

    return tokens


def lemmatize(text: str) -> list[str]:
    return [token.lemma_ for token in nlp(text)]