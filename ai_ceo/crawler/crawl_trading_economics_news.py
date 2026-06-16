import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import RequestException
from sqlalchemy import create_engine, text

URL = (
    "https://tradingeconomics.com/ws/stream.ashx"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://tradingeconomics.com/united-states/stock-market",
    "Origin": "https://tradingeconomics.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
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
    INSERT INTO trading_economics_news (
        id,
        url,
        title,
        description,
        content,
        author,
        published_at
    )
    VALUES (
        :id,
        :url,
        :title,
        :description,
        :content,
        :author,
        :published_at
    )
    ON CONFLICT (id)
    DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        content = EXCLUDED.content,
        author = EXCLUDED.author,
        published_at = EXCLUDED.published_at,
        updated_at = NOW()
    """
)


def random_sleep() -> None:
    """Sleep for a short random interval."""

    time.sleep(random.uniform(0.5, 1.5))


def parse_datetime(value: str | None):
    """Parse datetime string."""

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        logger.exception(
            "Failed to parse datetime: {}",
            value,
        )
        return None


def html_to_text(html: str | None) -> str | None:
    """Convert HTML to plain text."""

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    return soup.get_text(
        separator="\n\n",
        strip=True,
    )


def fetch_news(
    session: requests.Session,
    start: int,
    size: int,
    retries: int = 3,
):
    """Fetch one page of news."""

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                URL,
                params={
                    "start": start,
                    "size": size,
                    "c": "united states",
                },
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except RequestException:
            logger.exception(
                "Request failed (attempt {}/{})",
                attempt,
                retries,
            )

            if attempt < retries:
                time.sleep(2**attempt)

    return []


def crawl() -> None:
    """Crawl Trading Economics news."""

    session = requests.Session()
    session.headers.update(HEADERS)

    session.get(
        "https://tradingeconomics.com/",
        timeout=30,
    )

    time.sleep(1)

    start = 0
    size = 50

    logger.info(
        "Fetching start={} size={}",
        start,
        size,
    )

    items = fetch_news(
        session=session,
        start=start,
        size=size,
    )

    if not items:
        logger.info(
            "No more records."
        )
        return

    with engine.begin() as conn:
        for item in items:
            try:
                content = html_to_text(
                    item.get("html")
                )

                if not content:
                    content = item.get(
                        "description"
                    )

                conn.execute(
                    INSERT_SQL,
                    {
                        "id": item.get("ID"),
                        "url": item.get("url"),
                        "title": item.get("title"),
                        "description": item.get(
                            "description"
                        ),
                        "content": content,
                        "author": item.get(
                            "author"
                        ),
                        "published_at": parse_datetime(
                            item.get("date")
                        ),
                    },
                )

                logger.info(
                    "Saved: {}",
                    item.get("title"),
                )

            except Exception:
                logger.exception(
                    "Failed to process record {}",
                    item.get("ID"),
                )

            random_sleep()


if __name__ == "__main__":
    crawl()