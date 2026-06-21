import orjson
from ai_ceo.intelligence.extract_intelligence import extract_intelligence


if __name__ == "__main__":

    documents = [
        {
            "title": "AI Adoption in Manufacturing",
            "content": "Manufacturing companies are increasing investment in generative AI to automate quality inspection and predictive maintenance."
        },
        {
            "title": "Expansion into Southeast Asia",
            "content": "Several software vendors are entering Southeast Asian markets where cloud adoption is accelerating."
        },
        {
            "title": "New Privacy Regulation",
            "content": "Governments are discussing stricter AI governance and data privacy regulations that may increase compliance costs."
        },
        {
            "title": "Partnership with Cloud Provider",
            "content": "A leading cloud company announced strategic partnerships with ERP vendors to integrate AI assistants."
        },
        {
            "title": "Customer Demand for Automation",
            "content": "Enterprise customers increasingly request workflow automation and intelligent document processing."
        },
        {
            "title": "Open Source LLM Growth",
            "content": "Open-source large language models continue to improve rapidly, reducing deployment costs."
        },
        {
            "title": "Supply Chain Disruption",
            "content": "Chip shortages and geopolitical tensions could delay hardware procurement."
        },
        {
            "title": "Competitor Launches AI Agent",
            "content": "A major competitor released an AI agent platform targeting enterprise decision support."
        },
        {
            "title": "Healthcare AI Opportunity",
            "content": "Hospitals are evaluating AI solutions for administrative tasks and patient communication."
        },
        {
            "title": "Subscription Revenue Trend",
            "content": "More software companies are shifting from perpetual licenses to subscription-based business models."
        },
    ]

    reviews = [
        {
            "sentiment": 1,
            "content": "The AI assistant saves our team several hours every week."
        },
        {
            "sentiment": 1,
            "content": "Easy integration with existing ERP systems."
        },
        {
            "sentiment": 1,
            "content": "Very responsive customer support."
        },
        {
            "sentiment": 1,
            "content": "Automation features significantly improved productivity."
        },
        {
            "sentiment": 1,
            "content": "The dashboard is intuitive and easy to use."
        },
        {
            "sentiment": 0,
            "content": "The pricing is too expensive for small businesses."
        },
        {
            "sentiment": 0,
            "content": "Occasional hallucinations reduce trust in generated reports."
        },
        {
            "sentiment": 0,
            "content": "Initial deployment was more complicated than expected."
        },
        {
            "sentiment": 0,
            "content": "Response latency becomes noticeable during peak hours."
        },
        {
            "sentiment": 0,
            "content": "Documentation lacks examples for advanced features."
        },
    ]

    intelligence = extract_intelligence(documents, reviews)

    print(orjson.dumps(intelligence, option=orjson.OPT_INDENT_2).decode("utf_8", errors="ignore"))