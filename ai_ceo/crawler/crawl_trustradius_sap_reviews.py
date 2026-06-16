import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests import RequestException
from sqlalchemy import create_engine, text

BASE_URL = "http://www.trustradius.com/products/sap-analytics-cloud/reviews/all?page={page}"

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
    INSERT INTO trustradius_sap_reviews (
        review_url,
        title,
        reviewer_name,
        published_at,
        rating,
        pros,
        cons
    )
    VALUES (
        :review_url,
        :title,
        :reviewer_name,
        :published_at,
        :rating,
        :pros,
        :cons
    )
    ON CONFLICT (review_url)
    DO UPDATE SET
        title = EXCLUDED.title,
        reviewer_name = EXCLUDED.reviewer_name,
        published_at = EXCLUDED.published_at,
        rating = EXCLUDED.rating,
        pros = EXCLUDED.pros,
        cons = EXCLUDED.cons,
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


def crawl_sap_news() -> None:
    """Crawl SAP News blog pages."""

    session = requests.Session()
    session.headers.update(HEADERS)

    page = 1
    end_page = 5

    while page <= end_page:
        page_url = BASE_URL.format(page=page)

        logger.info(
            "Crawling page {}: {}",
            page_url,
            page,
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

            posts = soup.select("article.Review_review__5RC6b")

            if not posts:
                logger.warning(
                    "No reviews found on page {}.",
                    page,
                )
                break

            with engine.begin() as conn:
                for post in posts:
                    try:
                        link = post.select_one("h2 a[href]")
                        if link is None:
                            continue

                        href = link["href"].strip()
                        review_url = (
                            href
                            if href.startswith("http")
                            else f"https://www.trustradius.com{href}"
                        )

                        title = link.get_text(" ", strip=True)

                        time_node = post.select_one("time[datetime]")
                        published_at = (
                            datetime.fromisoformat(
                                time_node["datetime"].replace("Z", "+00:00")
                            )
                            if time_node
                            else None
                        )

                        rating_node = post.select_one("div[data-rating]")
                        rating = (
                            int(rating_node["data-rating"])
                            if rating_node and rating_node.get("data-rating")
                            else None
                        )

                        reviewer_node = post.select_one("div._name_1hm54_58")
                        reviewer_name = (
                            reviewer_node.get_text(" ", strip=True)
                            if reviewer_node
                            else None
                        )

                        pros_items = []
                        pros_header = post.find("h3", string="Pros")
                        if pros_header:
                            pros_ul = pros_header.find_next("ul")
                            if pros_ul:
                                pros_items = [
                                    span.get_text(" ", strip=True)
                                    for span in pros_ul.select("li span")
                                    if span.get_text(" ", strip=True)
                                ]

                        cons_items = []
                        cons_header = post.find("h3", string="Cons")
                        if cons_header:
                            cons_ul = cons_header.find_next("ul")
                            if cons_ul:
                                cons_items = [
                                    span.get_text(" ", strip=True)
                                    for span in cons_ul.select("li span")
                                    if span.get_text(" ", strip=True)
                                ]

                        pros = "\n".join(pros_items)
                        cons = "\n".join(cons_items)

                        conn.execute(
                            INSERT_SQL,
                            {
                                "review_url": review_url,
                                "title": title,
                                "reviewer_name": reviewer_name,
                                "published_at": published_at,
                                "rating": rating,
                                "pros": pros,
                                "cons": cons,
                            },
                        )

                        logger.info(
                            "Saved review: {}",
                            title,
                        )

                        sleep_random()

                    except Exception:
                        logger.exception(
                            "Failed to process review on page {}.",
                            page,
                        )

            page += 1

        except Exception:
            logger.exception(
                "Failed to process list page {}.",
                page,
            )


if __name__ == "__main__":
    crawl_sap_news()