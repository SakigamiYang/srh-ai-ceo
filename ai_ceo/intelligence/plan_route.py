from ai_ceo.llm import llm_chat

__all__ = ["plan_route"]


def plan_route(query: str) -> dict:
    """
    Decide whether retrieval is needed.
    """

    prompt = f"""
You are a routing planner.

Decide whether the following query requires external data retrieval.

Query:
{query}

Rules:
- If the question is about market, company, products, trends → use retrieval
- If it is general knowledge or reasoning → skip retrieval

IMPORTANT:
- You MUST return a valid JSON object
- DO NOT include any explanation outside JSON
- DO NOT use markdown (no ```json)
- DO NOT add extra fields
- The output MUST be parseable by json.loads()

Return JSON:
{{
  "route": "retrieve" or "skip",
  "reason": ""
}}

Now return ONLY the JSON:
"""

    result = llm_chat(system_prompt="You are a routing planner.", user_prompt=prompt)

    if not result:
        return {"route": "retrieve", "reason": "fallback"}

    return result