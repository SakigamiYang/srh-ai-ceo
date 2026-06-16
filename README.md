# AI CEO: Strategic Intelligence Agent

AI CEO is a Retrieval-Augmented Generation (RAG) and multi-agent system that gathers information from public business and financial sources to support intelligent analysis and decision making. It combines web crawlers, PostgreSQL, vector search, and large language models to build an extensible knowledge base for strategic insights.

## Crawlers

The project currently includes three data crawlers for collecting public business and financial information.

- TOTAL: 100

| Source            | Type             | URL                                             | Description                                                                                                       |           Records |
|-------------------|------------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------:|
| SAP News Blog     | official news    | https://news.microsoft.com/source/              | Crawls SAP official blog posts, including title, author, publication date, and full article content.              |            **60** |
| ERP Today News    | industry news    | https://erp.today/category/erp-news/            | Crawls ERP Today News articles news, including title, author, publication date, and full article content.         |            **31** |
| Trading Economics | customer reviews | https://tradingeconomics.com/united-states/news | Crawls financial and macroeconomic news from Trading Economics, including market updates and economic indicators. |            **50** |

### Notes

* All crawlers store the collected data in PostgreSQL.
* Duplicate records are handled using database upsert logic.
* Network requests include retry handling and delays between requests to improve robustness.
* Article content is extracted from the corresponding web pages whenever applicable.
* The crawler framework is designed to be easily extended with additional news and blog sources.
