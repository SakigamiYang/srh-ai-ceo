import json
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import RequestException
from sqlalchemy import create_engine, text


SEARCH_URL = (
    "https://nlweb-source-aefyhee7bqhbd5ht.b01.azurefd.net/ask"
)

HEADERS = {
    "Accept": "text/event-stream",
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    ),
}

DATABASE_URL = (
    "postgresql+psycopg://postgres:postgres@localhost:5432/ai_ceo"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

INSERT_SQL = text(
    """
    INSERT INTO microsoft_news (
        url,
        title,
        author,
        published_at,
        description,
        content
    )
    VALUES (
        :url,
        :title,
        :author,
        :published_at,
        :description,
        :content
    )
    ON CONFLICT (url)
    DO UPDATE SET
        title = EXCLUDED.title,
        author = EXCLUDED.author,
        published_at = EXCLUDED.published_at,
        description = EXCLUDED.description,
        content = EXCLUDED.content,
        updated_at = NOW()
    """
)


def random_sleep() -> None:
    """Sleep for a short random interval."""

    time.sleep(random.uniform(0.5, 1.5))


def parse_datetime(value: str | None):
    """Parse an ISO 8601 datetime string."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except Exception:
        logger.warning(
            "Failed to parse datetime: {}",
            value,
        )
        return None


def extract_article_content(
    session: requests.Session,
    article_url: str,
    retries: int = 3,
) -> str:
    """Extract article content from Microsoft News."""

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                article_url,
                timeout=30,
            )
            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            container = soup.select_one(
                "div.wp-block-columns"
            )

            if container is None:
                logger.warning(
                    "Content container not found: {}",
                    article_url,
                )
                return ""

            paragraphs = []

            for p in container.find_all("p"):
                text = p.get_text(
                    separator=" ",
                    strip=True,
                )

                if text:
                    paragraphs.append(text)

            return "\n\n".join(paragraphs)

        except Exception:
            logger.exception(
                "Failed to fetch article: {} (attempt {}/{})",
                article_url,
                attempt,
                retries,
            )

            if attempt < retries:
                time.sleep(random.uniform(1.0, 3.0))

    return ""


def get_event_stream(
    session: requests.Session,
    query: str,
    retries: int = 3,
) -> requests.Response:
    """Fetch the event stream with retry support."""

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                SEARCH_URL,
                params={
                    "query": query,
                    "generate_mode": "summarize",
                    "display_mode": "full",
                    "site": "all",
                },
                stream=True,
                timeout=60,
            )

            response.raise_for_status()
            return response

        except RequestException:
            logger.exception(
                "Request failed (attempt {}/{}).",
                attempt,
                retries,
            )

            if attempt < retries:
                time.sleep(2**attempt)

    raise RuntimeError("Failed to fetch event stream.")


def crawl(query: str = "sap") -> None:
    """Crawl Microsoft News and store the results."""

    session = requests.Session()
    session.headers.update(HEADERS)

    response = get_event_stream(
        session=session,
        query=query,
    )

    with engine.begin() as conn:
        for line in response.iter_lines(
            decode_unicode=True,
        ):
            try:
                if not line:
                    continue

                if not line.startswith("data:"):
                    continue

                payload = line[5:].strip()

                if not payload:
                    continue

                if payload == "[DONE]":
                    logger.info("Received DONE event.")
                    break

                data = json.loads(payload)

                if not data.get("message_type") == "result_batch":
                    continue

                for item in data.get("results", []):
                    url = item.get("url")
                    title = item.get("name")
                    description = item.get("description")

                    schema = item.get("schema_object", {})

                    author = schema.get("author")
                    published_at = parse_datetime(
                        schema.get("datePublished")
                    )
                    content = extract_article_content(
                        session=session,
                        article_url=url,
                    )

                    conn.execute(
                        INSERT_SQL,
                        {
                            "url": url,
                            "title": title,
                            "author": author,
                            "published_at": published_at,
                            "description": description,
                            "content": content,
                        },
                    )

                    logger.info(
                        "Saved article: {}",
                        title,
                    )

                random_sleep()

            except Exception:
                logger.exception(
                    "Failed to process an event."
                )


if __name__ == "__main__":
    crawl("sap")