from ai_ceo.llm import llm_chat


def build_documents_summary(documents):

    texts = []
    for d in documents:
        texts.append(f"{d['title']}: {d['content']}")

    return "\n".join(texts[:10])


def build_reviews_summary(reviews):

    positives = []
    negatives = []

    for r in reviews:
        if r["sentiment"] == 1:
            positives.append(r["content"])
        else:
            negatives.append(r["content"])

    return f"""
Positive:
{chr(10).join(positives[:10])}

Negative:
{chr(10).join(negatives[:10])}
"""


def extract_intelligence(documents, reviews):

    doc_summary = build_documents_summary(documents)
    review_summary = build_reviews_summary(reviews)

    prompt = f"""
You are a business analyst.

Identify:

1. Opportunities
2. Risks
3. Trends

Documents:
{doc_summary}

User Feedback:
{review_summary}

Return JSON:
{{
  "opportunities": [],
  "risks": [],
  "trends": []
}}
"""

    result = llm_chat(system_prompt="You are a business analyst.", user_prompt=prompt)
    if not result:
        result = {
            "opportunities": [],
            "risks": [],
            "trends": []
        }
    return result