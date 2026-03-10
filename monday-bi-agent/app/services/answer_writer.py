from __future__ import annotations

import json
from openai import OpenAI

from app.config import settings
from app.prompts import ANSWER_SYSTEM_PROMPT


client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


def write_answer(question: str, metrics_package: dict) -> str:
    payload = {
        "question": question,
        "metrics_package": metrics_package,
    }

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, default=str)},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content