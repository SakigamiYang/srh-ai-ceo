import orjson
from typing import Dict, Any, Optional

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

__all__ = ["llm_chat"]

MODEL = "gemma-4-12b-it-qat"

client = OpenAI(
    base_url="http://localhost:20000/v1",
    api_key="dummy"
)


def llm_chat(system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                ChatCompletionSystemMessageParam(content=system_prompt, role="system"),
                ChatCompletionUserMessageParam(content=user_prompt, role="user"),
            ],
            reasoning_effort="none",
        )
        content = resp.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "")
        return orjson.loads(content)
    except Exception as e:
        logger.exception(e)
        return None