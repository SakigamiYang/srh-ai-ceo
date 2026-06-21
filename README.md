# AI CEO: Strategic Intelligence Agent

AI CEO is a Retrieval-Augmented Generation (RAG) and multi-agent system that gathers information from public business and financial sources to support intelligent analysis and decision making. It combines web crawlers, PostgreSQL, vector search, and large language models to build an extensible knowledge base for strategic insights.

---

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

---

## System Architecture

The system follows a layered architecture:

- Presentation Layer: Streamlit dashboard
- Orchestration Layer: LangGraph agent
- Retrieval Layer: Hybrid search (BM25 + vector)
- Data Layer: PostgreSQL and Chroma

![aiceo-system-architecture.png](docs/images/aiceo-system-architecture.png)

---

## Data Flow

![aiceo-data-flow.png](docs/images/aiceo-data-flow.png)

---

## Technology Stack

Frontend:
- Streamlit

Backend:
- Python
- LangGraph (Agent Orchestration)

Retrieval:
- BM25 (Gensim)
- Vector Search (ChromaDB)

Database:
- PostgreSQL

ML / AI:
- SentenceTransformers (Embedding)
- Local LLM (Gemma via OpenAI API)

Infrastructure:
- Docker (PostgreSQL, Chroma)

---

## Design Decisions

1. Hybrid Retrieval (BM25 + Vector)
   - Combines lexical and semantic search
   - Improves recall and precision

2. Separation of Documents and Reviews
   - Documents: factual information
   - Reviews: user sentiment
   - Enables balanced decision-making

3. LangGraph-based Pipeline
   - Provides modular and interpretable reasoning
   - Ensures deterministic execution flow

4. Local LLM Deployment
   - Reduces latency and dependency on external APIs
   - Enables full control over inference

5. Chunking Strategy
   - Improves retrieval granularity
   - Enhances embedding quality

---

## AI Pipeline

![aiceo-ai-pipeline.png](docs/images/aiceo-ai-pipeline.png)