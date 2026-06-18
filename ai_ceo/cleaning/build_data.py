import hashlib
import json
import re
import unicodedata

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam
from sqlalchemy import create_engine, text


DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
MODEL = "gemma-4-12b-it-qat"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

client = OpenAI(
    base_url="http://localhost:20000/v1",
    api_key="dummy",  # local model, not used
)


# ---------- SQL ----------

INSERT_DOCUMENT = text("""
INSERT INTO documents (
    source, source_id, url, title, body,
    author, published_at, content_hash, metadata
)
VALUES (
    :source, :source_id, :url, :title, :body,
    :author, :published_at, :content_hash, :metadata
)
ON CONFLICT (source, source_id)
DO UPDATE SET
    body = EXCLUDED.body,
    updated_at = NOW()
""")

INSERT_REVIEW = text("""
INSERT INTO reviews (
    source, source_id, url, product_name,
    content, sentiment, tag
)
VALUES (
    :source, :source_id, :url, :product_name,
    :content, :sentiment, :tag
)
ON CONFLICT DO NOTHING
""")

# ---------- prompt ----------

SYSTEM_PROMPT = """
You are a strict classifier.

Classify user feedback into categories.

Allowed categories:
- Usability
- Performance
- Cost
- Integration
- Features
- Stability
- Support
- Implementation

Rules:
- Only use the allowed categories
- Multiple tags allowed
- No explanation
- Return JSON only

Format:
{
  "tags": [
    ...
  ]
}
"""

def classify(text_input: str) -> list[str]:
    """Call local LLM to classify tags."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            ChatCompletionSystemMessageParam(content=SYSTEM_PROMPT, role="system"),
            ChatCompletionUserMessageParam(content=f'Text: "{text_input}"', role="user"),
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content

    if "```json" in content:
        content = content.replace("```json", "")
    if "```" in content:
        content = content.replace("```", "")

    try:
        data = json.loads(content) if content else {}
        return data.get("tags", [])
    except Exception:
        logger.warning("Bad JSON: {}", content)
        return []


# ---------- utils ----------

def clean(text: str | None) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def build_hash(title: str, body: str) -> str:
    raw = (clean(title) + "\n\n" + clean(body)).lower()
    return hashlib.sha256(raw.encode()).hexdigest()


# ---------- documents ----------

def build_documents(conn):

    # --- sap_news_blog ---
    rows = conn.execute(
        text("SELECT * FROM sap_news_blog")
    ).mappings()

    for r in rows:
        body = r["content"]

        if not body:
            continue

        conn.execute(INSERT_DOCUMENT, {
            "source": "sap_news_blog",
            "source_id": str(r["id"]),
            "url": r["url"],
            "title": r["title"],
            "body": body,
            "author": r["author"],
            "published_at": r["published_at"],
            "content_hash": build_hash(r["title"], body),
            "metadata": json.dumps({
                "page": r["page_number"]
            })
        })

    logger.info("sap_news_blog done")


    # --- erp_today_news ---
    rows = conn.execute(
        text("SELECT * FROM erp_today_news")
    ).mappings()

    for r in rows:
        body = "\n\n".join(
            x for x in [r["summary"], r["content"]] if x
        )

        if not body:
            continue

        conn.execute(INSERT_DOCUMENT, {
            "source": "erp_today_news",
            "source_id": str(r["id"]),
            "url": r["url"],
            "title": r["title"],
            "body": body,
            "author": r["author"],
            "published_at": r["published_at"],
            "content_hash": build_hash(r["title"], body),
            "metadata": json.dumps({})
        })

    logger.info("erp_today_news done")


# ---------- reviews ----------

def build_reviews(conn):

    rows = conn.execute(
        text("SELECT * FROM trustradius_sap_reviews")
    ).mappings()

    count = 0

    for r in rows:

        base_id = str(r["id"])

        # --- Pros ---
        if r["pros"]:
            for i, line in enumerate(r["pros"].split("\n")):
                line = clean(line)
                if not line:
                    continue

                tags = classify(line)
                tag = ",".join(tags)
                logger.debug(f"tag: {tag!r}, line: {line!r}")

                conn.execute(INSERT_REVIEW, {
                    "source": "trustradius",
                    "source_id": f"{base_id}_p_{i}",
                    "url": r["review_url"],
                    "product_name": "SAP Analytics Cloud",
                    "content": line,
                    "tag": tag or "",
                    "sentiment": 1,
                })
                count += 1

        # --- Cons ---
        if r["cons"]:
            for i, line in enumerate(r["cons"].split("\n")):
                line = clean(line)
                if not line:
                    continue

                tags = classify(line)
                tag = ",".join(tags)
                logger.debug(f"tag: {tag!r}, line: {line!r}")

                conn.execute(INSERT_REVIEW, {
                    "source": "trustradius",
                    "source_id": f"{base_id}_c_{i}",
                    "url": r["review_url"],
                    "product_name": "SAP Analytics Cloud",
                    "content": line,
                    "tag": tag or "",
                    "sentiment": 0,
                })
                count += 1

    logger.info("reviews inserted: {}", count)


# ---------- main ----------

def main():
    with engine.begin() as conn:
        build_documents(conn)
        build_reviews(conn)

    logger.info("ALL DONE")


if __name__ == "__main__":
    main()