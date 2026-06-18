# AI CEO: Strategic Intelligence Agent

AI CEO is a Retrieval-Augmented Generation (RAG) and multi-agent system that gathers information from public business and financial sources to support intelligent analysis and decision making. It combines web crawlers, PostgreSQL, vector search, and large language models to build an extensible knowledge base for strategic insights.

## Crawlers

The project currently includes three data crawlers for collecting public business and financial information.

- TOTAL: 141

| Source         | Type             | URL                                             | Description                                                                                                       |           Records |
|----------------|------------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------:|
| SAP News Blog  | official news    | https://news.microsoft.com/source/              | Crawls SAP official blog posts, including title, author, publication date, and full article content.              |            **60** |
| ERP Today News | industry news    | https://erp.today/category/erp-news/            | Crawls ERP Today News articles news, including title, author, publication date, and full article content.         |            **31** |
| Trust Radius   | customer reviews | https://www.trustradius.com/products/sap-analytics-cloud/reviews/all | Crawls TrustRadius reviews for SAP Analytics Cloud, including review title, reviewer name, publication date, rating, pros, and cons. |            **50** |

### Notes

* All crawlers store the collected data in PostgreSQL.
* Duplicate records are handled using database upsert logic.
* Network requests include retry handling and delays between requests to improve robustness.
* Article content is extracted from the corresponding web pages whenever applicable.
* The crawler framework is designed to be easily extended with additional news and blog sources.

## Data Processing Pipeline

Transforms raw data (`sap_news_blog`, `erp_today_news`, `trustradius_sap_reviews`) into two layers:

- **documents**: normalized news/blog content for retrieval (title + body, deduplicated via hash)
- **reviews**: atomic user feedback (split pros/cons → one row per sentence, with sentiment)

Each review item is further classified by a local LLM (`gemma-4-12b-it-qat`) into predefined tags (e.g., Cost, Performance), converting unstructured feedback into structured signals for downstream analysis and decision-making.

