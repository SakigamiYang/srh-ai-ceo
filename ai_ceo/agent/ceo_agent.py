from ai_ceo.llm import llm_chat


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
    result = llm_chat(system_prompt="You are a strategic CEO.", user_prompt=prompt)
    if not result:
        result = {
            "priorities": [],
            "actions": [],
            "justification": ""
        }
    return result