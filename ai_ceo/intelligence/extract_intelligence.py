import json
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

MODEL = "gemma-4-12b-it-qat"

client = OpenAI(
    base_url="http://localhost:20000/v1",
    api_key="dummy"
)


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

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            ChatCompletionSystemMessageParam(content="You are a business analyst.", role="system"),
            ChatCompletionUserMessageParam(content=prompt, role="user"),
        ],
    )

    content = resp.choices[0].message.content.strip()

    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except:
        return {
            "opportunities": [],
            "risks": [],
            "trends": []
        }