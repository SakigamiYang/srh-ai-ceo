import json
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

MODEL = "gemma-4-12b-it-qat"

client = OpenAI(
    base_url="http://localhost:20000/v1",
    api_key="dummy"
)


def ceo_decision(intelligence: dict) -> dict:
    """
    Input:
        intelligence = {
            "opportunities": [],
            "risks": [],
            "trends": []
        }

    Output:
        {
            "priorities": [],
            "actions": [],
            "justification": ""
        }
    """

    prompt = f"""
You are the CEO of a company.

You are given structured business intelligence:

Opportunities:
{intelligence.get("opportunities")}

Risks:
{intelligence.get("risks")}

Trends:
{intelligence.get("trends")}

Your task:

1. Prioritize the most important strategic directions
2. Propose concrete business actions
3. Justify your decisions clearly

Return STRICT JSON:
{{
  "priorities": [],
  "actions": [],
  "justification": ""
}}
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            ChatCompletionSystemMessageParam(content="You are a strategic CEO.", role="system"),
            ChatCompletionUserMessageParam(content=prompt, role="user"),
        ],
    )

    content = resp.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except Exception:
        return {
            "priorities": [],
            "actions": [],
            "justification": content
        }