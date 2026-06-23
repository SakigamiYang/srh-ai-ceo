import orjson
from typing import Dict, Any, Optional

from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

__all__ = ["llm_chat"]

MODEL = "minicpm-o-4_5"

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

        logger.debug("-" * 80)
        logger.debug(f"{system_prompt = !r}")
        logger.debug(f"{user_prompt = !r}")
        logger.debug(f"{content = !r}")

        content = content.replace("```json", "").replace("```", "")
        return orjson.loads(content)
    except Exception as e:
        logger.exception(e)
        return None