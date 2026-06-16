import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import RequestException
from sqlalchemy import create_engine, text

BASE_URL = "https://news.sap.com/blog/page/{page}/"

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
    INSERT INTO sap_news_blog (
        url,
        title,
        author,
        published_at,
        page_number,
        content
    )
    VALUES (
        :url,
        :title,
        :author,
        :published_at,
        :page_number,
        :content
    )
    ON CONFLICT (url)
    DO UPDATE SET
        title = EXCLUDED.title,
        author = EXCLUDED.author,
        published_at = EXCLUDED.published_at,
        page_number = EXCLUDED.page_number,
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


def extract_article_content(
    session: requests.Session,
    article_url: str,
) -> str:
    """Extract the article body."""

    response = get_with_retry(
        session=session,
        url=article_url,
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    entry_content = soup.select_one("div.entry-content")

    if entry_content is None:
        logger.error("div.entry-content not found")
        return ""

    paragraphs = []

    nodes = entry_content.find_all("p", recursive=True)

    for p in nodes:
        text = p.get_text(" ", strip=True)
        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def crawl_sap_news() -> None:
    """Crawl SAP News blog pages."""

    session = requests.Session()
    session.headers.update(HEADERS)

    page = 1
    end_page = 20

    while page <= end_page:
        page_url = BASE_URL.format(page=page)

        logger.info(
            "Crawling page {}: {}",
            page,
            page_url,
        )

        try:
            response = get_with_retry(
                session=session,
                url=page_url,
            )

            if response.status_code == 404:
                logger.info(
                    "Received 404 on page {}. Stop crawling.",
                    page,
                )
                break

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            posts = soup.select(
                "ul.c-posts-grid__inner > li.c-post-teaser"
            )

            if not posts:
                logger.warning(
                    "No posts found on page {}.",
                    page,
                )
                break

            with engine.begin() as conn:
                for post in posts:
                    try:
                        link = post.select_one(
                            "div.entry-header a.c-post-link-wrapper"
                        )

                        if link is None:
                            continue

                        article_url = (
                            link["href"].strip()
                        )

                        title = (
                            post.select_one(
                                "h3.c-heading.entry-header__heading"
                            )
                            .get_text(
                                " ",
                                strip=True,
                            )
                        )

                        author_node = post.select_one(
                            "span.c-entry-author a"
                        )

                        author = (
                            author_node.get_text(
                                strip=True
                            )
                            if author_node
                            else None
                        )

                        published_at = datetime.strptime(
                            post.select_one(
                                "span.c-entry-date"
                            ).get_text(strip=True),
                            "%B %d, %Y",
                        ).date()

                        logger.info(
                            "Fetching article: {}",
                            article_url,
                        )

                        content = extract_article_content(
                            session=session,
                            article_url=article_url,
                        )

                        conn.execute(
                            INSERT_SQL,
                            {
                                "url": article_url,
                                "title": title,
                                "author": author,
                                "published_at": published_at,
                                "page_number": page,
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
                            "Failed to process article on page {}.",
                            page,
                        )

            page += 1
            sleep_random()

        except Exception:
            logger.exception(
                "Failed to process list page {}.",
                page,
            )
            break


if __name__ == "__main__":
    crawl_sap_news()