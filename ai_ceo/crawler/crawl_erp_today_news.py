import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import RequestException
from sqlalchemy import create_engine, text

BASE_URL = "https://erp.today/category/erp-news/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
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
    INSERT INTO erp_today_news (
        url,
        title,
        author,
        published_at,
        summary,
        content
    )
    VALUES (
        :url,
        :title,
        :author,
        :published_at,
        :summary,
        :content
    )
    ON CONFLICT (url)
    DO UPDATE SET
        title = EXCLUDED.title,
        author = EXCLUDED.author,
        published_at = EXCLUDED.published_at,
        summary = EXCLUDED.summary,
        content = EXCLUDED.content,
        updated_at = NOW()
    """
)


def sleep_random() -> None:
    """Sleep for a short random interval."""

    time.sleep(random.uniform(0.8, 2.0))


def get_with_retry(
    session: requests.Session,
    url: str,
    retries: int = 3,
) -> requests.Response:
    """Send an HTTP GET request with retry support."""

    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            response = session.get(
                url,
                timeout=30,
            )

            if response.status_code == 404:
                return response

            response.raise_for_status()
            return response

        except RequestException as exc:
            last_exception = exc

            logger.warning(
                "Request failed (attempt {}/{}): {}",
                attempt,
                retries,
                url,
            )

            if attempt < retries:
                time.sleep(2**attempt)

    raise last_exception


def extract_article(
    session: requests.Session,
    article_url: str,
) -> tuple[str | None, datetime | None, str]:
    response = get_with_retry(session=session, url=article_url)

    soup = BeautifulSoup(response.text, "html.parser")

    author = None
    author_meta = soup.select_one('meta[name="author"]')
    if author_meta:
        author = author_meta.get("content")

    published_at = None
    published_meta = soup.select_one(
        'meta[property="article:published_time"]'
    )
    if published_meta:
        published_at = datetime.fromisoformat(
            published_meta["content"].replace("Z", "+00:00")
        )

    container = soup.select_one("div.entry-content")
    if container is None:
        container = soup.select_one("article")

    paragraphs = []

    if container is not None:
        for p in container.find_all("p"):
            text = p.get_text(" ", strip=True)
            if text:
                paragraphs.append(text)

    content = "\n\n".join(paragraphs)

    return author, published_at, content


def crawl_erp_today_news() -> None:
    """Crawl SAP News blog pages."""

    session = requests.Session()
    session.headers.update(HEADERS)

    page_url = BASE_URL

    logger.info(
        "Crawling page {}",
        page_url,
    )

    try:
        response = get_with_retry(
            session=session,
            url=page_url,
        )

        if response.status_code == 404:
            logger.info(
                "Received 404. Stop crawling.",
            )
            return

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        posts = soup.select("div.article-box")

        if not posts:
            logger.warning(
                "No posts found.",
            )
            return

        with engine.begin() as conn:
            for post in posts:
                try:
                    link = post.select_one("a.article-title")

                    if link is None:
                        continue

                    article_url = link["href"].strip()
                    title = link.get_text(" ", strip=True)

                    summary_node = post.select_one("div.article-excerpt")
                    summary = (
                        summary_node.get_text(" ", strip=True)
                        if summary_node
                        else None
                    )

                    author, published_at, content = extract_article(
                        session=session,
                        article_url=article_url,
                    )

                    logger.info(
                        "Fetching article: {}",
                        article_url,
                    )

                    conn.execute(
                        INSERT_SQL,
                        {
                            "url": article_url,
                            "title": title,
                            "author": author,
                            "published_at": published_at,
                            "summary": summary,
                            "content": content,
                        },
                    )

                    logger.info(
                        "Saved article: {}",
                        title,
                    )

                    sleep_random()

                except Exception:
                    logger.exception(
                        "Failed to process article.",
                    )


    except Exception:
        logger.exception(
            "Failed to process list.",
        )


if __name__ == "__main__":
    crawl_erp_today_news()