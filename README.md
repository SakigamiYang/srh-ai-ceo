# AI CEO: Strategic Intelligence Agent

AI CEO is a Retrieval-Augmented Generation (RAG) and multi-agent system that gathers information from public business and financial sources to support intelligent analysis and decision making. It combines web crawlers, PostgreSQL, vector search, and large language models to build an extensible knowledge base for strategic insights.

## Crawlers

The project currently includes three data crawlers for collecting public business and financial information.

| Source            | URL                                             | Description                                                                                                       | Records Collected |
|-------------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|------------------:|
| Microsoft News    | https://news.sap.com/blog                               | Crawls Microsoft News articles and stores metadata together with the extracted article content.                   |            **30** |
| SAP News Blog     | https://news.microsoft.com/source/                      | Crawls SAP official blog posts, including title, author, publication date, and full article content.              |            **84** |
| Trading Economics | https://tradingeconomics.com/united-states/news | Crawls financial and macroeconomic news from Trading Economics, including market updates and economic indicators. |            **50** |

### Notes

* All crawlers store the collected data in PostgreSQL.
* Duplicate records are handled using database upsert logic.
* Network requests include retry handling and delays between requests to improve robustness.
* Article content is extracted from the corresponding web pages whenever applicable.
* The crawler framework is designed to be easily extended with additional news and blog sources.
